# 010 — Context Compaction & Visual Token Monitoring v0.27.0

> **Status:** DRAFT
> **Scope:** unified-ui-platform-service, unified-ui-agent-service, unified-ui-frontend-service, unifiedui-sdk
> **Ziel:** Lange Conversations effizient verwalten via **Context Compaction** (automatische Zusammenfassung alter Messages) und einen **visuellen Token-Monitor** (Donut-Chart) im Chat-UI, der den aktuellen Context-Window-Verbrauch zeigt. Nutzt die in REQ 009 etablierte Token-Erfassung wieder.
> **Issue:** [unified-ui#20](https://github.com/unified-ui/unifiedui/issues/20)

---

## Arbeitsweise & Prozess

> Standard-Ablauf. Nach jedem Paket `pre-commit run --all-files`.

### Status-Tracking

- *(kein Marker)* | `⏳ In Progress` | `✅ Done`

### Voraussetzungen

- **REQ 009 Paket 0** (Telemetry-Foundation) muss fertig sein — wir nutzen die zentral erfassten Token-Counts (`AssistantMetadata.TokensInput/Output` + `message_metric` Tabelle)
- **REQ 007** (Debug Backdoor) für autonomes Testing empfohlen

---

## Kontext & Architekturentscheidungen

### Warum dieses REQ separat?

User-Feedback: Issue #20 ist eine **Chat-Feature**, kein Admin-Topic. Es nutzt aber die gleichen Token-Daten wie REQ 009. Logische Trennung verhindert Vermischung von User-Facing-Chat und Admin-Observability.

### Wo kommen die Token-Counts her?

In REQ 009 Paket 0 etablierten wir:
- agent-service speichert `TokensInput`, `TokensOutput` in `messages.metadata` (Mongo, Source-of-Truth)
- platform-service hat `message_metric` SQL-Tabelle für Aggregationen

Für REQ 010 brauchen wir:
- **Per-Conversation-Live-Query**: Summe der Tokens der letzten N Messages → bestimmt aktuelle Context-Auslastung
- → Endpoint im agent-service `GET /conversations/{id}/context-stats` (liest aus Mongo, billig wenn Index auf conversationId)
- Optional: Cache in Redis pro Conversation (TTL 30 s)

### Compaction-Strategie

```
Conversation grows → tokens_used / model_context_window > threshold (z.B. 70%)
                  → Compaction-Trigger
                  → "Compaction-LLM" (cheap, z.B. gpt-4o-mini) summarizes
                    older messages (alle bis auf last N=10)
                  → Summary wird als spezielle Message vom Type COMPACTED_SUMMARY
                    gespeichert (oder in Conversation.metadata.compactedSummary)
                  → ältere Messages werden NICHT gelöscht, nur beim Build
                    des LLM-Prompts ersetzt durch die Summary
                  → SSE-Event COMPACTION_START / COMPACTION_END
                    informiert Frontend
```

**Wichtig:** Compaction ist persistent — wird nicht bei jedem Request neu berechnet.

### Token-Monitor UI

- Donut-Chart unten rechts im Chat-Footer
- Zeigt `used_tokens / max_tokens` mit Color-States:
  - 0–60% Grün
  - 60–85% Gelb
  - > 85% Rot
- Tooltip zeigt: aktuell verwendete Tokens, Compaction-Status, Model-Context-Window-Size
- Klick öffnet kleines Settings-Panel: Compaction toggle, Threshold, Compaction-LLM-Auswahl

---

## Pakete

### Paket 0: Token-Tracking-Konsolidierung ⏳

> Sicherstellen, dass alle Agent-Typen Token-Counts korrekt befüllen. REQ 009 Paket 0 hat das nur für die Aggregations-Schiene gemacht; hier verifizieren wir die Datenquelle.

#### 0.1 Audit existing token capture

| ID | Anforderung |
|----|-------------|
| 0.1.1 | Inventur über alle Agent-Adapter (`internal/services/agents/foundry`, `n8n`, `restapi`, `llm`, `react-agent-client`): wo werden Tokens erfasst, wo nicht? |
| 0.1.2 | Erstellung Coverage-Tabelle in dieser Datei nach Implementation |
| 0.1.3 | Lücken füllen: jeder Adapter setzt nach erfolgreicher Response `AssistantMetadata.TokensInput`, `TokensOutput`, `Model` |

#### 0.2 LLM-Adapter (REQ 006)

| ID | Anforderung |
|----|-------------|
| 0.2.1 | LLM-Adapter erfasst Tokens aus Provider-Response (alle 7 Provider: Azure-OpenAI, OpenAI, Anthropic, Gemini, Ollama, Mistral, Groq) |

#### 0.3 ReAct-Adapter

| ID | Anforderung |
|----|-------------|
| 0.3.1 | ReAct-Agent-Service liefert Tokens via SSE-Event `MESSAGE_COMPLETE` payload zurück; agent-service propagiert in `AssistantMetadata` |

#### 0.4 Foundry-Adapter

| ID | Anforderung |
|----|-------------|
| 0.4.1 | Foundry-API liefert `usage`-Block in Response — extraktion sicherstellen |

---

### Paket 1: Context-Stats-Endpoint (Agent-Service) ⏳

> Live-Query der Token-Auslastung einer Conversation für den UI-Donut.

#### 1.1 Endpoint

| ID | Anforderung |
|----|-------------|
| 1.1.1 | `GET /api/v1/agent-service/tenants/{tenant_id}/conversations/{conv_id}/context-stats` |
| 1.1.2 | Response: `{ used_tokens: int, max_tokens: int, usage_percent: float, model: str, compaction_active: bool, compacted_until_message_id?: str, last_compacted_at?: timestamp }` |
| 1.1.3 | Berechnung: lese Conversation-Config (chat_agent → AI-Model → context_window), summiere Tokens aller Messages > `compacted_until_message_id` (oder alle, wenn keine Compaction) |
| 1.1.4 | Cache in Redis 30 s, Invalidierung bei neuer Message |
| 1.1.5 | Permission: User muss Member der Conversation sein |

#### 1.2 SSE-Event-Erweiterung

| ID | Anforderung |
|----|-------------|
| 1.2.1 | Bestehender `MESSAGE_COMPLETE`-Event erhält Field `contextStats` (gleiche Struktur wie 1.1.2) — Frontend kann ohne Extra-Request live updaten |

---

### Paket 2: Compaction-Settings & Schema ⏳

> Konfigurations-Schema für Compaction in den Chat-Agents bzw. Conversations.

#### 2.1 Chat-Agent-Config Erweiterung

| ID | Anforderung |
|----|-------------|
| 2.1.1 | Globaler Settings-Block in jedem `ChatAgentConfig` (egal welcher Type): `compaction: { enabled: bool, threshold_percent: int (default 70), keep_last_n_messages: int (default 10), compaction_ai_model_id?: str }` |
| 2.1.2 | Validation: wenn `enabled=true` → `compaction_ai_model_id` muss existieren und dem Tenant gehören |
| 2.1.3 | Pydantic-Validator + Tests |

#### 2.2 Conversation-Schema (Mongo)

| ID | Anforderung |
|----|-------------|
| 2.2.1 | `Conversation` Model erhält Feld `compactedSummary: { messageIdUntil: str, summary: str, tokensSaved: int, createdAt: timestamp, model: str }` (nullable) |
| 2.2.2 | Wenn Compaction läuft → Summary persisted, ältere Messages bleiben unverändert |

---

### Paket 3: Compaction-Logik (Agent-Service) ⏳ depends on 1, 2

| ID | Anforderung |
|----|-------------|
| 3.1.1 | Neuer Service `internal/services/compaction/compactor.go` |
| 3.1.2 | Hook in `messages_send.go` (vor LLM-Call): wenn `compaction.enabled` und `usage_percent > threshold` → Trigger Compaction (synchron oder async je nach Modus — Default async, dann nachladen beim nächsten Message) |
| 3.1.3 | Compaction-Aufruf: lade alle Messages bis vor `keep_last_n_messages`, baue Summary-Prompt, rufe `compaction_ai_model_id` LLM auf, persist in `Conversation.compactedSummary` |
| 3.1.4 | Beim Build des LLM-Prompts (jede Message): wenn `compactedSummary` existiert → ersetze ältere Messages durch eine system-message mit dem Summary; nur Messages > `messageIdUntil` werden direkt durchgereicht |
| 3.1.5 | SSE-Events `COMPACTION_START` und `COMPACTION_END` (mit `summary_excerpt`, `tokens_saved`) — neue Event-Types in unifiedui-sdk Streaming-Protocol |
| 3.1.6 | Bei Compaction-Failure: Log Error, Compaction übersprungen, normale Flow läuft weiter |
| 3.1.7 | Tests inkl. Edge-Cases: zweite Compaction (aufeinanderfolgend), Manual-Trigger via API |

---

### Paket 4: Manual-Compaction-Endpoint ⏳ depends on 3

| ID | Anforderung |
|----|-------------|
| 4.1.1 | `POST /tenants/{tenant_id}/conversations/{conv_id}/compact` — manueller Trigger |
| 4.1.2 | Body optional: `{ keep_last_n: int }` |
| 4.1.3 | Response: `{ success, summary_excerpt, tokens_saved, latency_ms }` |
| 4.1.4 | Permission: Conversation-Member |

---

### Paket 5: SDK Streaming-Protocol Erweiterung ⏳ depends on 3

| ID | Anforderung |
|----|-------------|
| 5.1.1 | `unifiedui-sdk` Streaming-Module: neue Event-Types `COMPACTION_START`, `COMPACTION_END` zu den existierenden 22 hinzufügen → werden 24 |
| 5.1.2 | Type-Definitions, Doc-Update |
| 5.1.3 | Event-Type Tests |

---

### Paket 6: Frontend Token-Monitor (Donut) ⏳ depends on 1

| ID | Anforderung |
|----|-------------|
| 6.1.1 | Neue Komponente `src/components/chat/ContextMonitor/ContextMonitor.tsx` mit Donut-Chart (Mantine `RingProgress` oder Recharts) |
| 6.1.2 | Position: unten rechts im `ChatInput`-Bereich (kompakt, 32px), bei Hover/Klick Expand mit Tooltip |
| 6.1.3 | Lade Daten: initial via `getConversationContextStats`, danach Updates aus SSE `MESSAGE_COMPLETE.contextStats` |
| 6.1.4 | Color-States via CSS-Variablen: 0–60% `--color-success-500`, 60–85% `--color-warning-500`, > 85% `--color-error-500` |
| 6.1.5 | Tooltip-Content: `Used: 14,200 / 128,000 tokens (11%)`, `Compaction: enabled`, `Last compacted: 2 min ago` |
| 6.1.6 | Klick → öffnet Settings-Popover mit Compaction-Toggle (admin only) + Manual-Compaction-Button + Threshold-Slider |
| 6.1.7 | i18n |
| 6.1.8 | Tests |

---

### Paket 7: Frontend Compaction-Events Display ⏳ depends on 5, 6

| ID | Anforderung |
|----|-------------|
| 7.1.1 | `useChat`-Hook: Handler für `COMPACTION_START` und `COMPACTION_END`-Events |
| 7.1.2 | Während Compaction → Anzeige im Chat-View: kleines transientes Banner oben „Optimizing context …" mit Spinner |
| 7.1.3 | Nach Compaction → kurz Anzeige Toast „Context compacted, saved X tokens" (auto-dismiss 4 s) |
| 7.1.4 | Tests |

---

### Paket 8: Compaction-Settings im Agent-Dialog ⏳ depends on 2

| ID | Anforderung |
|----|-------------|
| 8.1.1 | Im Chat-Agent Create/Edit-Dialog neuer Tab oder Section **„Advanced History Management"** |
| 8.1.2 | Felder: Toggle „Enable Compaction", AI-Model-Picker (gefiltert auf LLM-Type), Threshold-Slider 50–95%, Keep-Last-N-Slider 5–30 |
| 8.1.3 | i18n + Tests |

---

## Anhang

### Issue-Zuordnung

- [#20](https://github.com/unified-ui/unifiedui/issues/20) — feat(chat): Context Compaction & Visual Token Monitoring → Pakete 0–8

### Lieferreihenfolge

1. Paket 0 (Audit + Lücken füllen, parallel zu REQ 009 Paket 0 möglich)
2. Paket 1 + 2 parallel (Endpoint + Schema)
3. Paket 5 (SDK-Erweiterung — kleines Paket, früh erledigen)
4. Paket 3 (Compaction-Logik)
5. Paket 4 (Manual-Trigger)
6. Paket 6 + 8 parallel (Frontend Donut + Settings)
7. Paket 7 (Compaction-Events-Display, baut auf 6)

### Performance-Erwägungen

- Context-Stats-Endpoint Cache-TTL 30 s — sonst pro Tab-Refresh ein Mongo-Query
- Compaction-LLM-Calls können teuer sein → Compaction-LLM-Auswahl ist Pflicht (nicht implizit das Haupt-Modell)
- Compaction läuft async per default — Frontend muss damit umgehen, dass die nächste Message noch ohne kompakten Context geht

### Sicherheit

- Manual-Compaction-Endpoint hat Permission-Check (Conversation-Member)
- LLM-Calls für Compaction nutzen System-Service-Key (nicht User-Tokens, damit cron-artige Nachverarbeitung möglich)
- Summary-Inhalt wird gleichbehandelt wie normale Messages (Tenant-Scope, RBAC)
