# 012 — Foundry Agent behind Custom REST API Proxy v0.3.0

> **Status:** DRAFT
> **Scope:** unifiedui-sample-rest-api-agent, unified-ui-agent-service, unified-ui-platform-service, unified-ui-frontend-service
> **Ziel:** Neuen Foundry-Integrationsmodus `CUSTOM_REST_API` einführen, bei dem ein Custom REST API Proxy vor dem Foundry Agent sitzt. Demo-Implementierung im Sample REST API Agent Service. Kein SDK nötig.
> **Issue:** [unified-ui#37](https://github.com/unified-ui/unifiedui/issues/37)

---

## Arbeitsweise & Prozess

> **Dieses Dokument ist das zentrale Tracking- und Anforderungsdokument.**

### Ablauf pro Paket (0, 1, 2, …)

1. **Implementierungsübersicht**: Copilot liest den relevanten Code ein und erstellt eine kompakte Übersicht: welche Dateien betroffen sind, welcher Ansatz gewählt wird.
2. **Review**: Nutzer prüft die Übersicht, gibt OK oder Korrekturen.
3. **Implementierung**: Copilot implementiert das **gesamte Paket** (alle Teilpakete zusammen, nicht einzeln).
4. **Testhinweise**: Copilot zeigt nach Implementierung kurz auf, was der Nutzer manuell testen soll.
5. **Test & Feedback**: Nutzer testet und gibt Anpassungswünsche.
6. **Abschluss**: Paket wird als `✅ Done` im Titel markiert → weiter zum nächsten Paket.

### Status-Tracking

- *(kein Marker)* → Noch nicht begonnen
- `⏳ In Progress` → Gerade in Bearbeitung
- `✅ Done` → Fertig implementiert und abgenommen

---

## Kontext & Architekturentscheidungen

### Aktueller Stand

| Bereich | Status |
|---------|--------|
| Foundry Auth-Modi (Platform Service) | `ENTRA_ID_USER_TOKEN`, `ENTRA_ID_APP_REGISTRATION`, `API_KEY` — kein Proxy-Modus |
| Foundry Adapter (Agent Service Go) | Direkt-Verbindung zu Foundry via `foundry/workflow_client.go` |
| REST API Adapter (Agent Service Go) | Generischer REST-API-Client (`restapi/client.go`) mit unified-ui SSE-Protokoll |
| Sample REST API Agent | Echo-, LangChain-, LangGraph-Agents mit API Key / Bearer / Basic Auth |
| Frontend | Create-Dialog hat auth_type-Dropdown (3 Optionen), Edit-Dialog hat **kein** auth_type |

### Ziel-Architektur

```
unified-ui Agent Service
        │
        ├─ auth_mode = API_KEY / USER_TOKEN / APP_REG
        │    → Direkt zu Foundry (bestehend)
        │
        └─ auth_mode = CUSTOM_REST_API
             │
             ▼ (POST mit unified-ui-Kontext)
     ┌───────────────────────────────┐
     │  Custom REST API Proxy        │
     │  (z.B. PII Filter, Logging)   │
     │  → Streamt Foundry-Response   │
     │    im unified-ui SSE-Protokoll│
     └───────────────┬───────────────┘
                     │
                     ▼
          Microsoft Foundry Agent
```

### Schlüsselentscheidung: Foundry-Erweiterung vs. REST_API wiederverwenden

**Ansatz:** Den `CUSTOM_REST_API`-Modus als neuen `MicrosoftFoundryAuthTypeEnum`-Wert implementieren. Wenn `auth_mode = CUSTOM_REST_API`, leitet der Agent Service den Request **nicht** an Foundry, sondern an den konfigurierten Proxy-Endpoint — analog zum bestehenden REST_API-Adapter.

**Warum kein eigener AgentType?** Der Chat Agent bleibt `type = MICROSOFT_FOUNDRY`. Es ist ein Auth/Integration-Modus, kein neuer Agent-Typ. Die Proxy-URL ist Teil der Foundry-Config.

### Proxy-Auth vom Agent Service zum Proxy

| Auth-Typ | Header | Beschreibung |
|----------|--------|--------------|
| `API_KEY` | `X-API-Key: {secret}` (oder custom Header) | Statischer API Key aus Credential |
| `BEARER` | `Authorization: Bearer {user_token}` | User-Token forwarden (identisch zu `ENTRA_ID_USER_TOKEN`) |
| `NONE` | — | Kein Auth-Header |

### SSE-Protokoll

Der Proxy MUSS das unified-ui Streaming-Protokoll (22 SSE Event Types) implementieren. Da der Proxy den Foundry-Stream 1:1 weiterleitet, muss er die Foundry-Events in unified-ui-Events konvertieren (oder selbst direkt unified-ui-Events erzeugen).

---

## Pakete

### Paket 0: Sample REST API Agent — Foundry Proxy Demo

> Neuen Foundry-Proxy-Endpoint im Sample REST API Agent implementieren. Dieser empfängt die unified-ui Invoke-Request, leitet sie 1:1 an Foundry weiter und streamt die Foundry-Antwort als unified-ui SSE-Events zurück. Zwei Auth-Modi: API Key und Bearer (User Token Forward).

#### 0.1 Foundry Proxy Agent

| ID | Anforderung |
|----|-------------|
| 0.1.1 | Neues Agent-Modul `app/agents/foundry_proxy_agent.py` erstellen, das per `httpx` (async) an Foundry streamt und Foundry-SSE-Events in unified-ui `StreamMessage`-Events konvertiert. |
| 0.1.2 | Konfiguration: `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_AGENT_NAME`, `FOUNDRY_API_KEY`, `FOUNDRY_API_VERSION` in `app/config.py` als Settings. |
| 0.1.3 | Der Proxy empfängt `RestApiAgentInvokeRequest`, baut daraus den Foundry `/openai/responses` Request (mit `stream: true`), und konvertiert die Foundry-SSE-Events (`response.output_text.delta` → `TEXT_STREAM`, `response.completed` → `STREAM_END`, etc.). |
| 0.1.4 | Message-History aus dem Request in Foundry-`input`-Format konvertieren (letzter User-Message als String oder Message-Array). |

#### 0.2 Proxy-Endpoints mit zwei Auth-Modi

| ID | Anforderung |
|----|-------------|
| 0.2.1 | Endpoint `POST /api/v1/api-key/agent/foundry-proxy/invoke` — geschützt mit `verify_api_key_header`. Nutzt den konfigurierten `FOUNDRY_API_KEY` für die Foundry-Verbindung. |
| 0.2.2 | Endpoint `POST /api/v1/entra-id/agent/foundry-proxy/invoke` — geschützt mit `verify_entra_id_token`. Extrahiert den Bearer Token aus dem Request und leitet ihn als `Authorization: Bearer {token}` an Foundry weiter (User Token Forward). |
| 0.2.3 | Conversation-Endpoints: `POST /api/v1/api-key/conversations` und `POST /api/v1/entra-id/conversations` existieren bereits — können wiederverwendet werden. |

#### 0.3 Dependencies & Config

| ID | Anforderung |
|----|-------------|
| 0.3.1 | `httpx` als Dependency hinzufügen (für async HTTP streaming zu Foundry). |
| 0.3.2 | `.env.example` um Foundry-spezifische Variablen erweitern. |
| 0.3.3 | README kurz aktualisieren mit Foundry-Proxy-Endpoint-Doku. |

---

### Paket 1: Platform Service — Config-Schema erweitern

> Neuen Auth-Modus `CUSTOM_REST_API` in der Foundry-Config validierbar machen. Konfigurationsfelder für Proxy-Endpoint und Proxy-Auth.

#### 1.1 Enum & Config-Validator

| ID | Anforderung |
|----|-------------|
| 1.1.1 | `MicrosoftFoundryAuthTypeEnum` um `CUSTOM_REST_API` erweitern in `core/database/enums.py`. |
| 1.1.2 | `MicrosoftFoundryChatAgentConfig` Validator erweitern: Wenn `auth_type = CUSTOM_REST_API`, sind folgende Felder **required**: `custom_rest_api_endpoint` (str, muss `https://` starten), `custom_rest_api_auth_type` (neuer Enum: `API_KEY` / `BEARER` / `NONE`). |
| 1.1.3 | Wenn `custom_rest_api_auth_type = API_KEY`: `credential_id` wird required; optionaler `custom_rest_api_api_key_header` (str, default `X-API-Key`). |
| 1.1.4 | Wenn `custom_rest_api_auth_type = BEARER`: kein `credential_id` nötig — User-Token wird vom Agent Service automatisch weitergeleitet. |
| 1.1.5 | Wenn `custom_rest_api_auth_type = NONE`: kein `credential_id` nötig. |

#### 1.2 Config-Response für Agent Service

| ID | Anforderung |
|----|-------------|
| 1.2.1 | `MicrosoftFoundryConfigSettingsResponse` um die neuen Felder erweitern (`custom_rest_api_endpoint`, `custom_rest_api_auth_type`, `custom_rest_api_api_key_header`), damit der Agent Service die Proxy-Config bekommt. |

#### 1.3 Alembic Migration

| ID | Anforderung |
|----|-------------|
| 1.3.1 | Keine DB-Migration nötig — die Config liegt im JSON-Feld `config`. Nur Enum-Wert validiert auf App-Ebene. |

---

### Paket 2: Agent Service (Go) — Foundry Adapter erweitern

> Den Foundry-Adapter im Agent Service um den `CUSTOM_REST_API`-Modus erweitern. Wenn dieser Modus aktiv ist, wird statt Foundry direkt der konfigurierte Proxy-Endpoint angesprochen — dabei wird der bestehende REST API Client wiederverwendet.

#### 2.1 Foundry Factory — Proxy-Modus

| ID | Anforderung |
|----|-------------|
| 2.1.1 | In `foundry/factory.go`: Wenn `auth_type = CUSTOM_REST_API`, statt `WorkflowClient` einen REST-API-artigen Client erstellen, der den `custom_rest_api_endpoint` als `invoke_endpoint` nutzt. |
| 2.1.2 | Auth-Handling im Proxy-Modus: `custom_rest_api_auth_type` bestimmt, wie der Proxy-Endpoint authentifiziert wird (API_KEY → Credential-Header, BEARER → User-Token forward, NONE → kein Header). |
| 2.1.3 | Der Proxy streamt im unified-ui SSE-Protokoll zurück — also wird der Stream wie ein REST_API-Agent behandelt (gleicher SSE-Parser, gleiche Event-Mappings). |

#### 2.2 Handler-Dispatch

| ID | Anforderung |
|----|-------------|
| 2.2.1 | In `messages_send.go`: Wenn Foundry + `auth_type = CUSTOM_REST_API`, den Request an den REST-API-Streaming-Pfad leiten (nicht den Foundry-Streaming-Pfad). |
| 2.2.2 | Platform-Models (`models.go`): Die neuen Config-Felder (`CustomRestApiEndpoint`, `CustomRestApiAuthType`, `CustomRestApiApiKeyHeader`) aus der AgentSettings parsen. |

#### 2.3 Tests

| ID | Anforderung |
|----|-------------|
| 2.3.1 | Unit-Tests für die Factory-Logik: Korrekter Client-Typ bei `CUSTOM_REST_API` auth_type. |
| 2.3.2 | Unit-Tests für Auth-Header-Setzung im Proxy-Modus (API_KEY, BEARER, NONE). |

---

### Paket 3: Frontend — Chat Agent Config UI erweitern

> Im Create- und Edit-Dialog für Foundry-Agents den neuen `CUSTOM_REST_API`-Auth-Modus als Option hinzufügen. Bei Auswahl: Proxy-Endpoint-URL und Proxy-Auth-Typ konfigurierbar.

#### 3.1 Types & API

| ID | Anforderung |
|----|-------------|
| 3.1.1 | `FoundryAuthTypeEnum` in `api/types.ts` um `CUSTOM_REST_API` erweitern. |
| 3.1.2 | `FoundryChatAgentConfig` Interface um optionale Felder erweitern: `custom_rest_api_endpoint`, `custom_rest_api_auth_type`, `custom_rest_api_api_key_header`. |
| 3.1.3 | Neuer Enum `FoundryCustomRestApiAuthTypeEnum` mit `API_KEY`, `BEARER`, `NONE`. |

#### 3.2 Create-Dialog

| ID | Anforderung |
|----|-------------|
| 3.2.1 | `FOUNDRY_AUTH_TYPES` Array um `CUSTOM_REST_API`-Option erweitern mit Label "Custom REST API Proxy". |
| 3.2.2 | Wenn `CUSTOM_REST_API` ausgewählt: Zusätzliche Felder anzeigen — TextInput für Proxy-Endpoint-URL (required), Select für Proxy-Auth-Typ (API_KEY/BEARER/NONE). |
| 3.2.3 | Wenn Proxy-Auth = `API_KEY`: Credential-Dropdown anzeigen (wie bei bestehender API_KEY-Auswahl), optionaler TextInput für Custom API Key Header Name (default `X-API-Key`). |
| 3.2.4 | Wenn Proxy-Auth = `BEARER`: Info-Alert anzeigen "The signed-in user's token is forwarded to the proxy." Kein Credential nötig. |
| 3.2.5 | Wenn Proxy-Auth = `NONE`: Info-Alert "No authentication — proxy endpoint must be accessible without credentials." |
| 3.2.6 | Foundry-spezifische Felder (Project Endpoint, Agent Name) ausblenden bei `CUSTOM_REST_API` — der Proxy managed die Foundry-Verbindung selbst. |
| 3.2.7 | Validierung: Proxy-Endpoint-URL muss mit `https://` beginnen (oder `http://localhost` für lokale Entwicklung). |

#### 3.3 Edit-Dialog

| ID | Anforderung |
|----|-------------|
| 3.3.1 | Edit-Dialog um die gleichen `CUSTOM_REST_API`-Felder erweitern (analog zu 3.2). |
| 3.3.2 | Bestehende Foundry-Config-Werte korrekt aus `data.config` laden und in Form-State initialisieren. |

#### 3.4 i18n

| ID | Anforderung |
|----|-------------|
| 3.4.1 | Neue i18n-Keys für alle UI-Strings in `en-US` und `de-DE` anlegen (Labels, Placeholder, Alert-Texte). |

---

## Offene Fragen

- [x] ~~SDK-Helper (`FoundryProxyMiddleware`) nötig?~~ → **Nein**, nicht in diesem Scope.
- [ ] Soll `custom_rest_api_endpoint` auch `http://` erlauben (für lokale Entwicklung)? → **Ja, `http://localhost` erlauben.**
- [ ] Soll Test-Connection für `CUSTOM_REST_API` implementiert werden? → Vorerst nein, kann nachgereicht werden.

---

## Anhang

### Referenzen

- [Issue #37 — Foundry Agent behind Custom REST API Proxy](https://github.com/unified-ui/unifiedui/issues/37)
- [008 — Foundry Auth Modes v0.25.0](./008_FOUNDRY_AUTH_MODES_v025.REQ.md) (Vorarbeit: auth_type-Feld in Foundry-Config)

### Betroffene Dateien (Überblick)

| Service | Dateien |
|---------|---------|
| **sample-rest-api-agent** | `app/agents/foundry_proxy_agent.py` (neu), `app/api/v1/agent.py`, `app/config.py`, `.env.example`, `pyproject.toml` |
| **platform-service** | `core/database/enums.py`, `handlers/validators/chat_agent_config.py`, `schema/responses/chat_agents.py` |
| **agent-service** | `internal/services/agents/foundry/factory.go`, `internal/services/platform/models.go`, `internal/api/handlers/messages_send.go` |
| **frontend-service** | `src/api/types.ts`, `src/components/dialogs/CreateChatAgentDialog/`, `src/components/dialogs/EditChatAgentDialog/`, `src/i18n/locales/` |
