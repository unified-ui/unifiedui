# ADR-002: Frontend-seitiges Token-Smoothing für gleichmäßiges Chat-Streaming

- **Status**: Under Evaluation
- **Date**: 2026-03-19
- **Decision Makers**: Enrico Goerlitz
- **Betrifft**: unified-ui-frontend-service, (unified-ui-agent-service — keine Änderung)

---

## Context

### Problem

Das aktuelle Streaming-Verhalten im Chat fühlt sich "bursty" an: Antworten kommen in unregelmäßig großen Chunks beim User an. Das führt dazu, dass plötzlich ein großer Textblock erscheint und der Scroll ruckartig nach unten springt. Das ist UX-technisch deutlich schlechter als das gleichmäßige, token-weise Streaming wie man es von ChatGPT oder Chainlit kennt.

### Aktueller Flow

```
Backend (N8N/Foundry/REST)
    ↓ Chunks kommen unregelmäßig (Netzwerk-Buffering, Backend-Batching)
    ↓ z.B. "Hello, " ... 200ms ... "how can I help you today? I'd be" (großer Burst)
Agent-Service (Go/Gin)
    ↓ 1:1 Passthrough: chunk.Content → writer.WriteTextStream(chunk.Content)
    ↓ Flush nach jedem Write — keine eigene Buffering-Logik
Frontend (React)
    ↓ accumulatedContent += chunk → setStreamingContent(accumulatedContent)
    ↓ Kein Throttling, kein Smoothing
    ↓ Jeder Chunk = 1 State-Update = 1 Re-Render
Browser
    ↓ Großer Chunk → großes DOM-Update → ruckartiger Scroll
```

### Warum ist das so?

Die Ursache liegt **nicht** im Agent-Service — der flusht nach jedem Write korrekt. Das Problem sind die **ungleichmäßigen Chunk-Größen** der Backend-Quellen:

- **N8N**: Buffered HTTP-Streaming, sendet gelegentlich große Text-Blöcke auf einmal
- **Microsoft Foundry**: OpenAI-kompatibles Streaming, relativ gleichmäßig aber abhängig von Netzwerk-Buffering
- **Custom REST / ReACT**: Backend-abhängig, oft große Chunks durch interne Verarbeitung

### Analyse: Chainlit als Referenz

Chainlit wurde als Referenz analysiert (Python Backend + React Frontend, `@chainlit/react-client`).

**Kernerkenntnisse:**

1. Chainlit hat **kein explizites Smoothing/Buffering** — weder Backend noch Frontend
2. Tokens werden 1:1 weitergeleitet (via WebSocket / Socket.IO)
3. Der angenehme Streaming-Effekt kommt dadurch, dass Chainlit **direkt am LLM sitzt** und die natürlich gleichmäßige Token-Rate des LLMs (~15–30ms pro Token) 1:1 ans Frontend weitergibt
4. Bei uns sitzt ein **zusätzlicher Proxy-Layer** (N8N, Foundry, REST-Backend) dazwischen, der Tokens buffert/batcht bevor sie beim Agent-Service ankommen

| Aspekt | Chainlit | unified-ui |
|--------|----------|------------|
| Transport | WebSocket (Socket.IO) | SSE über HTTP |
| Chunk-Granularität | LLM-native Tokens (einzelne Wörter) | Backend-abhängig (große Bursts möglich) |
| Overhead pro Message | ~20–50 Bytes (WS Frame) | ~100–200 Bytes (SSE Event + JSON) |
| Direkte LLM-Anbindung | Ja | Nein (über N8N/Foundry/REST) |
| Frontend-Smoothing | Keines nötig (Token-Rate ist gleichmäßig) | Keines vorhanden (nötig!) |

**Fazit**: Chainlit hat keinen magischen Algorithmus. Wir brauchen ein Frontend-seitiges Smoothing, um die ungleichmäßige Chunk-Rate unserer Proxy-Architektur auszugleichen.

---

## Evaluated Approaches

### Ansatz A: Frontend-seitiges Token-Smoothing (⭐ GEWÄHLT)

Empfangene Chunks im Frontend nicht sofort vollständig rendern, sondern über einen `requestAnimationFrame`-basierten Render-Loop gleichmäßig "abspielen". Große Chunks werden zeichenweise mit konstanter Geschwindigkeit gerendert.

**Wichtiges Designprinzip**: Kein abruptes "Alles-Anzeigen" wenn der Stream endet. Stattdessen rendert der Smoother nach Stream-Ende **in derselben Geschwindigkeit weiter** bis der Buffer vollständig dargestellt ist. So bleibt das Erlebnis durchgängig gleichmäßig.

### Ansatz B: Backend-seitiges Chunk-Splitting (Agent-Service, Go)

Große Chunks im Agent-Service in kleinere Teile aufteilen und mit Timer-basiertem Delay senden.

**Verworfen weil:**
- **Erhöhte Latenz**: Jedes Zeichen wird um Timer-Intervall verzögert
- **Künstliche Verlangsamung**: Backend-seitig Tokens bremsen ist kontra-intuitiv
- **Goroutine pro Request**: Timer-basierte Goroutine erhöht Komplexität und Server-Last
- **Mehr SSE Events**: Statt ~50 Events pro Response → 500+ Events (mehr Netzwerk-Overhead)
- **Buffer-Verlust bei Disconnect**: Gepufferter Content geht bei Client-Disconnect verloren

### Ansatz C: Hybrid (BE-Splitting + FE-Smoothing)

Backend splittet nur absurd große Chunks (>500 Zeichen), Frontend macht feines Smoothing.

**Verworfen weil:**
- Zwei Stellen zum Warten = höhere Gesamt-Komplexität
- Marginaler Vorteil gegenüber reinem FE-Ansatz
- FE-Smoothing allein löst das Problem vollständig

---

## Decision

**Ansatz A: Frontend-seitiges Token-Smoothing** via `useStreamSmoother` Hook.

### Begründung

1. **Kein Backend-Änderung nötig** — Agent-Service bleibt unverändert
2. **Sofort wirksam** für alle Agent-Typen (N8N, Foundry, REST, ReACT)
3. **Keine erhöhte Latenz** — erste Zeichen erscheinen sofort
4. **Gleichmäßiger Scroll** — kleine DOM-Updates statt große Bursts
5. **Kein Server-Overhead** — Backend sendet weiterhin wie bisher
6. **`requestAnimationFrame`** — frame-aligned, batterie-freundlich, pausiert wenn Tab inaktiv
7. **Graceful Stream-Ende** — kein abruptes Aufblitzen, Smoother rendert bis zum natürlichen Ende
8. **Geringster Aufwand** — ein Hook + Integration in ChatContent (~1–2 Tage)

---

## Technical Design

### Core Concept

```
Backend-Chunks (unregelmäßig):     "Hello, "  ...200ms...  "how can I help you today?"
                                       ↓                           ↓
rawContent (akkumuliert):          "Hello, "               "Hello, how can I help you today?"
                                       ↓                           ↓
Smoother-Buffer (intern):         Target-String wird gespeichert, Display-Cursor rückt vor
                                       ↓
displayContent (gleichmäßig):     "He" → "Hel" → "Hell" → "Hello" → "Hello," → "Hello, " → ...
                                  ↑ ~3 Zeichen pro Frame (konfigurierbar)
```

### Stream-Ende Verhalten

```
isStreaming = true            isStreaming = false (Stream endet)
    ↓                              ↓
Buffer empfängt Chunks        Buffer empfängt keine neuen Chunks mehr
    ↓                              ↓
Render-Loop: 3 chars/frame    Render-Loop: LÄUFT WEITER in gleicher Geschwindigkeit
    ↓                              ↓
                              Erst wenn displayContent === rawContent → Loop stoppt
```

Kein abruptes "Alles anzeigen". Der letzte Rest wird in derselben gleichmäßigen Geschwindigkeit zu Ende gerendert wie der Rest davor.

### Catch-Up Mechanismus

Wenn der Buffer sehr weit hinter dem empfangenen Content zurückfällt (>`catchUpThreshold` Zeichen), wird die Render-Geschwindigkeit automatisch erhöht, damit die Anzeige nicht zu weit hinter der tatsächlichen Antwort zurückbleibt:

```
Normal:     3 Zeichen/Frame (~250 chars/sec bei 83fps)
Catch-Up:  15 Zeichen/Frame (~1250 chars/sec) ab 200 Zeichen Rückstand
```

### Konfigurierbare Parameter

| Parameter | Default | Beschreibung |
|-----------|---------|-------------|
| `charsPerTick` | 3 | Zeichen pro Render-Frame bei normalem Tempo. Bestimmt die "Tipp-Geschwindigkeit" |
| `minIntervalMs` | 12 | Minimales Intervall zwischen Renders (~83fps max) |
| `catchUpThreshold` | 200 | Ab wie vielen gepufferten Zeichen in den Catch-Up-Modus gewechselt wird |
| `catchUpMultiplier` | 5 | Faktor für Catch-Up-Geschwindigkeit (5 × `charsPerTick` = 15 chars/frame) |

**Geschwindigkeits-Referenz** bei `minIntervalMs=12`:

| `charsPerTick` | Zeichen/Sek | Gefühl |
|----------------|-----------:|--------|
| 1 | ~83 | Langsam, bewusstes Tippen |
| 2 | ~167 | Gemächlich |
| **3** | **~250** | **ChatGPT-ähnlich (Default)** |
| 5 | ~417 | Schnell, flüssig |
| 8 | ~667 | Sehr schnell |

### Hook Implementation

```typescript
// src/hooks/chat/useStreamSmoother.ts

import { useEffect, useRef, useState } from 'react';

interface StreamSmootherConfig {
    charsPerTick?: number;
    minIntervalMs?: number;
    catchUpThreshold?: number;
    catchUpMultiplier?: number;
}

const DEFAULT_CONFIG: Required<StreamSmootherConfig> = {
    charsPerTick: 3,
    minIntervalMs: 12,
    catchUpThreshold: 200,
    catchUpMultiplier: 5,
};

export const useStreamSmoother = (
    rawContent: string,
    isStreaming: boolean,
    config?: StreamSmootherConfig,
): string => {
    const cfg = { ...DEFAULT_CONFIG, ...config };
    const [displayContent, setDisplayContent] = useState('');
    const bufferRef = useRef('');
    const rafRef = useRef<number>();
    const lastTimeRef = useRef(0);
    const displayLengthRef = useRef(0);

    useEffect(() => {
        bufferRef.current = rawContent;
    }, [rawContent]);

    useEffect(() => {
        if (!isStreaming && displayLengthRef.current >= bufferRef.current.length) {
            setDisplayContent(bufferRef.current);
            return;
        }

        const tick = (timestamp: number) => {
            const elapsed = timestamp - lastTimeRef.current;
            if (elapsed >= cfg.minIntervalMs) {
                lastTimeRef.current = timestamp;

                const target = bufferRef.current;
                const currentLen = displayLengthRef.current;

                if (currentLen < target.length) {
                    const remaining = target.length - currentLen;
                    const chars = remaining > cfg.catchUpThreshold
                        ? cfg.charsPerTick * cfg.catchUpMultiplier
                        : cfg.charsPerTick;

                    const newLen = Math.min(currentLen + chars, target.length);
                    displayLengthRef.current = newLen;
                    setDisplayContent(target.slice(0, newLen));
                } else if (!isStreaming) {
                    // Buffer fully rendered and stream ended → stop
                    return;
                }
            }

            rafRef.current = requestAnimationFrame(tick);
        };

        rafRef.current = requestAnimationFrame(tick);

        return () => {
            if (rafRef.current) {
                cancelAnimationFrame(rafRef.current);
                rafRef.current = undefined;
            }
        };
    }, [isStreaming, cfg.charsPerTick, cfg.minIntervalMs,
        cfg.catchUpThreshold, cfg.catchUpMultiplier]);

    return displayContent;
};
```

### Integration in ChatContent

```typescript
// ChatContent.tsx
const { streamingContent, isStreaming } = props;

// Smoother zwischen Raw-Content und Anzeige
const smoothedContent = useStreamSmoother(streamingContent ?? '', isStreaming);

// MessageBubble bekommt smoothedContent statt streamingContent
<MessageBubble content={smoothedContent} ... />

// Scroll reagiert auf smoothedContent
useEffect(() => {
    if (!userScrolledUpRef.current && smoothedContent) {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
}, [smoothedContent]);
```

---

## Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Stream endet | Render-Loop läuft in gleicher Geschwindigkeit weiter bis Buffer leer |
| User scrollt hoch | `userScrolledUpRef` verhindert Auto-Scroll (bestehende Logik) |
| Sehr lange Antwort (>10k Zeichen) | Catch-Up-Mechanismus hält Display-Rückstand unter Kontrolle |
| Schnelle kurze Antwort (<50 Zeichen) | ~1–2 Sekunden Render-Zeit, kaum spürbare Verzögerung |
| Tab wird inaktiv | `requestAnimationFrame` pausiert automatisch |
| Leerer Stream | Kein Rendering, kein Effekt |
| Mehrere Nachrichten (Foundry) | Smoother-Reset bei `STREAM_NEW_MESSAGE` Event |
| Markdown-Rendering | Smoothing auf String-Level, Markdown-Parser sieht aktuellen Display-Stand |
| ReACT-Steps (Reasoning, ToolCall) | Können separat durch gleichen Hook geglättet werden (Follow-Up) |
| Neuer User-Message während Smooth-Ausgang | Reset: `displayLengthRef.current = 0`, neuer Buffer |

---

## Consequences

### Positive

- UX wird signifikant besser — gleichmäßiges, ChatGPT-ähnliches Streaming
- Scroll-Verhalten stabilisiert sich (kleine, konstante DOM-Updates)
- Kein Backend-Impact — Agent-Service bleibt unverändert
- Konfigurierbare Geschwindigkeit für verschiedene Präferenzen
- Geringer Implementierungs-Aufwand (~1–2 Tage)
- Batterie-freundlich durch `requestAnimationFrame`

### Negative

- Minimale künstliche Verzögerung zwischen Empfang und Anzeige (~50–300ms je nach Chunk-Größe)
- Nach Stream-Ende dauert es kurz bis der letzte Rest angezeigt ist (gewollt — smooth statt Burst)
- Nur für das React-Frontend wirksam — zukünftige Clients (Chat-Widget, Mobile) brauchen eigene Lösung oder Backend-Ansatz wird ergänzt

### Neutral

- ReACT-Steps (Reasoning, ToolCall, Plan) profitieren noch nicht — Follow-Up-Task
- Parameter-Tuning nötig nach erster Integration (optimale Werte durch Testen finden)

---

## Implementation Plan

| Phase | Beschreibung | Aufwand |
|-------|-------------|---------|
| 1 | `useStreamSmoother` Hook erstellen | ~0.5 Tage |
| 2 | Integration in `ChatContent.tsx` (smoothedContent statt streamingContent) | ~0.5 Tage |
| 3 | Scroll-Logic auf `smoothedContent` umstellen | ~0.25 Tage |
| 4 | Parameter-Tuning und manuelles Testing | ~0.25 Tage |
| 5 (optional) | ReACT-Steps durch gleichen Smoother leiten | ~0.5 Tage |

---

## References

- Chainlit Source: `chainlit/message.py` (`stream_token`), `chainlit/emitter.py` (`send_token`)
- Chainlit React Client: `@chainlit/react-client` (`updateMessageContentById`)
- Agent-Service SSE: `internal/api/sse/writer.go`, `internal/api/handlers/messages_send.go`
- Frontend Chat Hook: `src/hooks/chat/useChat.ts`
- Frontend Chat Content: `src/components/chat/ChatContent/ChatContent.tsx`
