# SSE vs WebSockets — Review & Empfehlung

## Datum: Februar 2026

## Kontext

Der Agent-Service nutzt aktuell **SSE (Server-Sent Events)** für `POST /messages`, um AI-Antworten in Echtzeit an das Frontend zu streamen. Dieses Dokument evaluiert, ob SSE die richtige Wahl bleibt oder ob WebSockets (oder andere Alternativen) besser geeignet wären — insbesondere mit Blick auf folgende Szenarien:

1. **Callback von externen Services** — Ein externer Service postet auf eine Callback-URL eine Message, die in Echtzeit an den User gesendet werden soll
2. **Message-Generierung abbrechen** — Stop-Button im Frontend, der die Generierung serverseitig tatsächlich abbricht
3. **Service-Unavailability erkennen** — Echtzeit-Erkennung, wenn das Backend nicht mehr erreichbar ist (wie in Chainlit)
4. **Performance** — Latenz und Overhead für Chat-Streaming

---

## Status Quo — Aktuelle SSE-Implementierung

### Agent-Service (Go/Gin)

- Custom `sse.Writer` mit `http.Flusher`
- `POST /messages` → Response `Content-Type: text/event-stream`
- Event-Typen: `message`, `trace`, `error`, `done`
- Stream-Protokoll: `STREAM_START` → `TEXT_STREAM` (n-mal) → `STREAM_END` → `MESSAGE_COMPLETE` → `TITLE_GENERATION`
- **Kein** expliziter Cancellation-Mechanismus — Server streamt bis zum Ende

### Frontend (React)

- `fetch()` mit `ReadableStream` (nicht `EventSource`, da POST benötigt)
- Manuelles SSE-Line-Parsing mit 7 Callbacks
- `AbortController` existiert, aber:
  - Signal wird **nicht** an `fetch()` übergeben
  - Stop-Button ist im UI vorhanden, aber `onCancel` wird **nicht** an `ChatInput` weitergegeben
  - Cancellation bricht nur die `for await`-Loop — Server und Agent laufen weiter

### Identifizierte Lücken

| Problem | Status |
|---------|--------|
| Stop-Button funktioniert nicht | `onCancel` nicht verdrahtet in `ConversationsPage` |
| `AbortController.signal` nicht an `fetch()` übergeben | HTTP-Verbindung bleibt offen |
| Kein serverseitiger Cancel-Endpunkt | Agent läuft weiter bis zum Ende |
| Kein Callback/Push-Kanal für externe Events | Nicht möglich mit aktuellem SSE-Setup |
| Keine Service-Health-Erkennung in Echtzeit | Keine Heartbeats implementiert |

---

## Technologie-Vergleich

### SSE (Server-Sent Events)

| Aspekt | Bewertung |
|--------|-----------|
| **Richtung** | Unidirektional: Server → Client |
| **Protokoll** | HTTP/1.1 (oder HTTP/2), text-basiert |
| **Verbindung** | Pro Request eine langlebige HTTP-Response |
| **Browser-Support** | Nativ via `EventSource` (nur GET); mit `fetch()` + ReadableStream auch POST |
| **Auto-Reconnect** | `EventSource` hat eingebauten Reconnect; bei `fetch()` manuell |
| **Proxy/CDN/LB** | Gut unterstützt, HTTP-Standard |
| **Max. Connections** | Browser-Limit: 6 pro Domain (HTTP/1.1), kein Limit bei HTTP/2 |
| **Skalierung** | Stateless, horizontal gut skalierbar |
| **Overhead** | Minimal — kein Handshake, kein Frame-Overhead |

**Stärken:**
- Perfekt für unidirektionales Streaming (AI-Antworten)
- Einfacher als WebSockets zu implementieren und zu debuggen
- Standard-HTTP — funktioniert mit allen Proxies, Load Balancern, CDNs
- Kein spezieller Upgrade-Handshake nötig
- Leichtgewichtig und effizient für Chat-Streaming

**Schwächen:**
- Nur Server → Client (keine bidirektionale Kommunikation)
- Kein nativer Mechanismus für Client → Server Signale (z.B. Cancel)
- Externe Push-Events erfordern eine separate persistente Verbindung
- Kein eingebauter Health-Check/Heartbeat (muss selbst implementiert werden)

---

### WebSockets

| Aspekt | Bewertung |
|--------|-----------|
| **Richtung** | Bidirektional: Client ↔ Server |
| **Protokoll** | WS/WSS, eigenes Frame-Format nach HTTP-Upgrade |
| **Verbindung** | Persistente Verbindung (langlebig) |
| **Browser-Support** | Nativ via `WebSocket` API |
| **Auto-Reconnect** | Kein eingebauter Reconnect — manuell implementieren |
| **Proxy/CDN/LB** | Problematischer — erfordert Sticky Sessions, Proxy-Unterstützung für Upgrade |
| **Max. Connections** | Kein hartes Browser-Limit, aber Server muss Connections verwalten |
| **Skalierung** | Stateful — erfordert Session-Affinity oder Pub/Sub-Layer (Redis) |
| **Overhead** | Initialer Upgrade-Handshake; danach sehr geringer Frame-Overhead |

**Stärken:**
- Bidirektional — Client kann Cancel, Typing-Indicators etc. senden
- Persistente Verbindung — ideal für externe Callbacks und Echtzeit-Push
- Sofortige Erkennung von Verbindungsverlust (onclose, onerror)
- Niedrige Latenz nach Verbindungsaufbau
- Natürlich geeignet für Chat-Anwendungen

**Schwächen:**
- Signifikant komplexere Implementierung (Connection Lifecycle, Reconnect, State-Management)
- Stateful — erschwert horizontale Skalierung erheblich
  - Erfordert Redis Pub/Sub oder ähnliches für Multi-Instance-Setups
  - Sticky Sessions bei Load Balancern nötig
- Nicht alle Proxies/Firewalls unterstützen WebSocket-Upgrade
- Debugging schwieriger (kein Standard-HTTP, spezielle DevTools nötig)
- Mehr Server-Ressourcen pro Verbindung (offene TCP-Connections)
- Authentifizierung komplexer (kein einfacher Authorization-Header bei Handshake)

---

### Hybrid: SSE + REST (Aktueller Ansatz, erweitert)

| Aspekt | Bewertung |
|--------|-----------|
| **Streaming** | SSE für Server → Client |
| **Client-Signale** | Separate REST-Endpunkte (z.B. `POST /cancel`, `POST /callback`) |
| **Externe Events** | Separater SSE-Kanal oder Long-Polling für Push-Events |
| **Verbindungsverlust** | Heartbeat-Events im SSE-Stream |
| **Skalierung** | Stateless möglich mit Redis Pub/Sub für Cross-Instance Events |

---

## Szenario-Analyse

### 1. Callback von externen Services

**Anforderung:** Ein externer Service (z.B. MCP Server, N8N Webhook) sendet eine Message an den Agent-Service, die in Echtzeit an den aktiven User gestreamt werden soll.

| Ansatz | SSE | WebSocket |
|--------|-----|-----------|
| **Implementierung** | Separater SSE-Kanal (`GET /events/{conversationId}`) + Backend empfängt Callback → schreibt in Redis Pub/Sub → SSE-Kanal pusht an Client | Callback → Redis Pub/Sub → WebSocket pusht an Client |
| **Komplexität** | Mittel — zweiter SSE-Kanal + Pub/Sub | Mittel — Pub/Sub + Connection-Registry |
| **Skalierung** | Einfacher — SSE-Kanal ist stateless, Pub/Sub entkoppelt | Schwieriger — braucht Connection-Registry + Sticky Sessions |

**Fazit:** Beide Ansätze brauchen einen Pub/Sub-Layer (Redis). Der SSE-Ansatz ist etwas einfacher zu skalieren. WebSockets bieten keinen signifikanten Vorteil hier.

### 2. Message-Generierung abbrechen

**Anforderung:** User klickt Stop → Agent-Service bricht die laufende AI-Generierung ab.

| Ansatz | SSE | WebSocket |
|--------|-----|-----------|
| **Implementierung** | `POST /messages/{id}/cancel` → Backend setzt Cancel-Flag → Streaming-Loop prüft Flag → bricht ab | Client sendet `{type: "cancel"}` über WebSocket → Server bricht ab |
| **Komplexität** | Niedrig — ein REST-Endpoint + AbortController.signal an fetch() | Niedrig — Message-Type + Handler |
| **Zuverlässigkeit** | Sehr gut — REST-Call ist unabhängig vom Stream | Gut — aber nur wenn WS-Verbindung noch steht |

**Fazit:** SSE + separater REST-Cancel-Endpunkt ist **zuverlässiger** als Cancel über denselben WebSocket-Kanal. Wenn die WS-Verbindung instabil ist, kommt der Cancel ggf. nicht an. Bei SSE + REST sind es zwei unabhängige HTTP-Verbindungen.

### 3. Service-Unavailability erkennen

**Anforderung:** Frontend erkennt in Echtzeit, wenn der Agent-Service nicht mehr erreichbar ist.

| Ansatz | SSE | WebSocket |
|--------|-----|-----------|
| **Implementierung** | Heartbeat-Events alle 15-30s im SSE-Stream; Frontend detektiert fehlende Heartbeats | `onclose`/`onerror` Events auf der WebSocket-Verbindung |
| **Komplexität** | Niedrig — Timer + Heartbeat-Event-Type | Sehr niedrig — nativ eingebaut |
| **Reaktionszeit** | 15-30s (Heartbeat-Intervall) | Sofort bei TCP-Close; sonst Ping/Pong Interval |

**Fazit:** WebSockets haben hier einen nativen Vorteil durch `onclose`/`onerror`. SSE kann das aber mit Heartbeats gut genug lösen. Bei einer persistenten SSE-Connection (`EventSource`) gibt es auch Reconnect-Events. Für einen Chat-Use-Case ist ein 15-30s Heartbeat-Intervall ausreichend.

### 4. Performance

| Aspekt | SSE | WebSocket |
|--------|-----|-----------|
| **Latenz (nach Aufbau)** | ~gleichwertig | ~gleichwertig |
| **Verbindungsaufbau** | Kein Upgrade nötig | HTTP Upgrade Handshake (~1 RTT extra) |
| **Payload-Overhead** | `event: ...\ndata: ...\n\n` (Text) | 2-14 Byte Frame-Header (Binary) |
| **Für AI-Token-Streaming** | Optimal | Leicht over-engineered |

**Fazit:** Für AI-Chat-Streaming ist der Performance-Unterschied **vernachlässigbar**. Die Tokens kommen ohnehin mit ~50-200ms Intervall vom LLM. Der Textoverhead von SSE ist bei JSON-Payloads irrelevant.

---

## Empfehlung

### SSE beibehalten + gezielt erweitern (Hybrid-Ansatz)

**SSE ist die richtige Wahl für unified-ui.** Die Vorteile von WebSockets (bidirektionale Kommunikation, nativer Disconnect-Detection) wiegen die Nachteile (Komplexität, Skalierung, Infrastruktur) für unseren Use-Case nicht auf.

### Empfohlene Architektur

```
┌─────────────┐     POST /messages          ┌───────────────┐
│   Frontend   │ ─────────────────────────── │ Agent-Service  │
│   (React)    │ ◄━━━━━━━━━━━━━━━━━━━━━━━━━ │    (Go/Gin)    │
│              │     SSE: text/event-stream  │                │
│              │                             │                │
│              │     POST /cancel            │                │
│              │ ───────────────────────────►│                │
│              │                             │                │
│              │     GET /events (SSE)       │                │  Callback
│              │ ◄━━━━━━━━━━━━━━━━━━━━━━━━━ │ ◄──────────────── Ext. Service
│              │     (Heartbeats, Callbacks) │   Redis PubSub │
└─────────────┘                             └───────────────┘
```

### Konkrete Erweiterungen

#### 1. Cancel-Mechanismus (Priorität: Hoch)

**Frontend:**
- `AbortController.signal` an `fetch()` übergeben
- `onCancel` in `ConversationsPage` an `ChatInput` verdrahten
- Bei Cancel: `POST /tenants/{tenantId}/conversations/{convId}/messages/{msgId}/cancel`

**Agent-Service:**
- Cancel-Endpoint implementieren
- Cancel-Flag pro Message-Stream (z.B. `sync.Map` oder Redis)
- Streaming-Loop prüft Cancel-Flag und bricht ab
- `context.Context` Cancellation an Agent-Client propagieren

#### 2. Event-Kanal für externe Callbacks (Priorität: Mittel)

**Agent-Service:**
- `GET /tenants/{tenantId}/conversations/{convId}/events` — persistenter SSE-Kanal
- Heartbeat alle 20s: `event: heartbeat\ndata: {}\n\n`
- Callback-Endpoint: `POST /tenants/{tenantId}/conversations/{convId}/callback`
  - Schreibt Event in Redis Pub/Sub
  - SSE-Kanal liest aus Pub/Sub und pusht an Client

**Frontend:**
- Separater `EventSource` oder `fetch(GET)` ReadableStream für den Event-Kanal
- Reconnect-Logik bei Verbindungsverlust

#### 3. Health/Heartbeat (Priorität: Niedrig)

- Heartbeat-Events im Event-Kanal (siehe oben)
- Frontend: Timer prüft letzten Heartbeat, zeigt Banner bei Timeout
- Alternative: Einfacher `GET /health` Polling alle 30s (weniger elegant, aber funktional)

---

## Warum NICHT WebSockets?

| Argument | Bewertung |
|----------|-----------|
| **Skalierungskomplexität** | WebSockets sind stateful — bei mehreren Agent-Service-Instanzen brauchen wir Connection-Registry + Sticky Sessions + Redis Pub/Sub. SSE ist stateless und horizontal trivial skalierbar. |
| **Infrastruktur-Overhead** | Viele Reverse-Proxies, CDNs und Cloud-Load-Balancer (Azure App Gateway, ALB) haben Einschränkungen oder erfordern spezielle Konfiguration für WebSockets. SSE funktioniert mit Standard-HTTP überall. |
| **Debugging & Observability** | SSE-Streams sind in Browser-DevTools als normale HTTP-Responses sichtbar. WebSocket-Frames erfordern spezielle Tools und sind schwerer zu loggen/monitoren. |
| **Authentifizierung** | SSE nutzt Standard-HTTP-Header (Bearer Token). WebSockets können bei dem initialen Handshake keine custom Authorization-Header setzen — erfordert Workarounds (Query-Parameter, Cookie, Subprotocol). Mit MSAL wäre das ein Problem. |
| **Implementierungsaufwand** | Migration zu WebSockets würde die gesamte Streaming-Infrastruktur (Frontend + Backend) neu erfordern. Die SSE-Erweiterungen (Cancel, Event-Kanal) sind inkrementell und mit deutlich weniger Aufwand umsetzbar. |
| **AI-Chat ist primär unidirektional** | 95% des Datenflows ist Server → Client (Token-Streaming). Die wenigen Client → Server Signale (Cancel, Typing) sind besser als separate REST-Calls modelliert. |

---

## Alternativen (kurz bewertet)

### gRPC Streaming
- Pros: Bidirektional, typsicher (Protobuf), effizient
- Cons: Kein nativer Browser-Support (braucht gRPC-Web Proxy), hoher Migrationsaufwand, Overkill für Chat
- **Verdict:** Nicht sinnvoll für Frontend-Chat-Kommunikation

### HTTP/2 Server Push
- Deprecated in den meisten Browsern (Chrome hat es 2022 entfernt)
- **Verdict:** Keine Option

### Long Polling
- Pros: Universell kompatibel
- Cons: Hohe Latenz, viele Requests, ineffizient für Streaming
- **Verdict:** Rückschritt gegenüber SSE

### WebTransport (QUIC-basiert)
- Pros: Bidirektional, multiplexed, QUIC-Performance
- Cons: Sehr neues API, limitierter Browser-Support, keine Go-Standardlibrary
- **Verdict:** Zukunftsoption, aber noch nicht produktionsreif (Stand Feb 2026)

---

## Zusammenfassung

| Kriterium | SSE (erweitert) | WebSockets |
|-----------|-----------------|------------|
| AI-Token-Streaming | ✅ Perfekt | ✅ Funktioniert, aber Overhead |
| Cancellation | ✅ Via separatem REST-Call (zuverlässiger) | ⚠️ Via WS-Message (fragiler) |
| Externe Callbacks | ✅ Via Event-Kanal + Pub/Sub | ✅ Via WS + Pub/Sub |
| Health-Detection | ⚠️ Via Heartbeats (15-30s Delay) | ✅ Nativ (sofort) |
| Skalierung | ✅ Stateless, einfach | ❌ Stateful, komplex |
| Infrastruktur | ✅ Standard-HTTP überall | ⚠️ Spezielle Proxy/LB-Config |
| Auth (MSAL) | ✅ Standard Authorization Header | ⚠️ Workarounds nötig |
| Implementierungsaufwand | ✅ Inkrementelle Erweiterung | ❌ Komplette Neuimplementierung |
| Debugging | ✅ Standard-HTTP-Tools | ⚠️ Spezielle WS-Tools |
| Zukunftssicherheit | ✅ Erweiterbar um Event-Kanal | ✅ Flexibler bei komplexen Szenarien |

**Empfehlung: SSE beibehalten und um Cancel-Endpoint + Event-Kanal + Heartbeats erweitern.**

Die Investition in WebSockets lohnt sich erst, wenn signifikant mehr bidirektionale Echtzeit-Features benötigt werden (z.B. kollaboratives Editing, Multiplayer-Features). Für einen AI-Chat-Client mit gelegentlichen Callbacks ist der erweiterte SSE-Ansatz die pragmatischere und robustere Lösung.
