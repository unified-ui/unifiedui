# 008 — Foundry Authentication Modes v0.25.0

> **Status:** DRAFT
> **Scope:** unified-ui-platform-service, unified-ui-agent-service, unified-ui-frontend-service
> **Ziel:** Microsoft Foundry Chat-Agents um drei explizite Authentication-Modi erweitern: **User Token Forward** (bestehend), **Entra App Registration** (Credential) und **Foundry Project API Key** (Credential). Test-Connection für alle drei Modi mit echtem Agent-Ping. Token-Cache via Redis.
> **Issue:** [unified-ui#25](https://github.com/unified-ui/unifiedui/issues/25)

---

## Arbeitsweise & Prozess

> Standard-Ablauf: Übersicht → Review → Implementation → Testhinweise → Review → Done. Nach jedem Paket `pre-commit run --all-files`.

### Status-Tracking

- *(kein Marker)* | `⏳ In Progress` | `✅ Done`

---

## Kontext & Architekturentscheidungen

### Aktueller Stand

| Bereich | Datei | Status |
|---------|-------|--------|
| Foundry-Config-Schema | `unifiedui/handlers/validators/chat_agent_config.py` → `MicrosoftFoundryChatAgentConfig` | nur `agent_type`, `api_version`, `project_endpoint`, `agent_name` — **kein `auth_type`, kein `credential_id`** |
| Foundry-Adapter (Go) | `internal/services/agents/foundry/...` | verwendet ausschließlich User-Token-Forward |
| Frontend-Dialog | `src/components/dialogs/.../FoundryConfigForm` o.ä. | kein Auth-Dropdown im Foundry-Tab |
| Test-Connection | `unifiedui/handlers/credentials.py::test_credential_connection` | nur generischer ENTRA_ID_APP_REGISTRATION-Token-Test, **nicht agent-spezifisch** |
| Token-Caching | bestehend für REST-API: `unifiedui/core/identity/client_credentials.py::ClientCredentialsTokenClient` | wiederverwendbar |

### Ziel-Architektur

```
Foundry Agent Config (JSON):
{
  "agent_type": "AGENT" | "MULTI_AGENT",
  "api_version": "2025-11-15-preview",
  "project_endpoint": "https://{account}.services.ai.azure.com/api/projects/{project}",
  "agent_name": "my-agent",
  "auth_type": "ENTRA_ID_USER_TOKEN" | "ENTRA_ID_APP_REGISTRATION" | "API_KEY",
  "credential_id": "uuid" | null
}
```

| auth_type | credential_id required | credential type | Token-Erwerb |
|-----------|-----------------------|----------------|--------------|
| `ENTRA_ID_USER_TOKEN` | nein | — | User-Token aus Request-Header forwarded (bestehende Logik) |
| `ENTRA_ID_APP_REGISTRATION` | ja | `ENTRA_ID_APP_REGISTRATION` | Client-Credentials-Flow → Redis-Cache (TTL = exp − 30 s, encrypted) |
| `API_KEY` | ja | `API_KEY` | Header `api-key: <secret>` direkt (kein Token-Erwerb, kein Cache) |

### Test-Connection-Strategie

**Pro Create/Edit Agent:** echter Ping gegen den konkreten Agent — nicht nur ein generischer Endpoint-Reachability-Test.

```
GET {project_endpoint}/assistants/{agent_name}?api-version={api_version}
   Headers: <auth-spezifisch>
   → 200 ok → Agent existiert + Auth funktioniert
   → 401/403 → Auth fehlerhaft
   → 404 → Agent_name unbekannt
```

Wird sowohl im Frontend-Dialog (Button „Test Connection") als auch beim Speichern automatisch ausgeführt.

---

## Pakete

### Paket 0: Schema-Erweiterung & Validator (Platform-Service)

> Foundation. Backend-Schema erweitern, dann hängen FE und Agent-Service daran.

#### 0.1 Enum & Validator

| ID | Anforderung |
|----|-------------|
| 0.1.1 | Neuer Enum `MicrosoftFoundryAuthTypeEnum` in `unifiedui/core/database/enums.py` mit Werten `ENTRA_ID_USER_TOKEN`, `ENTRA_ID_APP_REGISTRATION`, `API_KEY` |
| 0.1.2 | `MicrosoftFoundryChatAgentConfig` (`handlers/validators/chat_agent_config.py`) erhält Felder: `auth_type: MicrosoftFoundryAuthTypeEnum = ENTRA_ID_USER_TOKEN` (default für Backward-Compat), `credential_id: str \| None = None` |
| 0.1.3 | `model_validator(mode="after")`: Wenn `auth_type` in `{ENTRA_ID_APP_REGISTRATION, API_KEY}` → `credential_id` muss gesetzt sein, sonst Validation-Error |
| 0.1.4 | Bei `auth_type=API_KEY` zusätzliche Prüfung: Credential-Type muss `API_KEY` sein (Lookup im Handler, nicht im Validator-Schema) |
| 0.1.5 | Bei `auth_type=ENTRA_ID_APP_REGISTRATION`: Credential-Type muss `ENTRA_ID_APP_REGISTRATION` sein |

#### 0.2 Handler-Logik

| ID | Anforderung |
|----|-------------|
| 0.2.1 | `ChatAgentHandler.create_chat_agent` und `update_chat_agent` (für Foundry-Type) → vor Speichern Credential-Existenz + Type-Match prüfen → spezifische Exception (`ChatAgentConfigCredentialMismatchError`) |
| 0.2.2 | `_resolve_chat_agent_credentials` (oder analoge Methode in `unifiedui/handlers/chat_agents.py` ab Zeile ~830) erweitern: für Foundry mit `API_KEY` Credential auflösen, Secret in Response hängen (analog zu REST-API-Logik) |

#### 0.3 Tests

| ID | Anforderung |
|----|-------------|
| 0.3.1 | Validator-Tests: alle 3 Auth-Typen valide, `credential_id` Pflicht-Logik, Default-Verhalten |
| 0.3.2 | Handler-Tests: Create mit gültigem Credential → success, mit falschem Credential-Type → 400, mit nicht-existentem Credential → 404 |

---

### Paket 1: Agent-Service Foundry-Adapter (Go) ⏳ depends on 0

> Foundry-Adapter im Go-Service erhält Auth-Mode-Switch + Token-Cache.

#### 1.1 Auth-Switch

| ID | Anforderung |
|----|-------------|
| 1.1.1 | Neuer Enum `FoundryAuthType` in `internal/services/agents/foundry/types.go` analog zu `restapi/types.go::AuthType` |
| 1.1.2 | Foundry-Client (`internal/services/agents/foundry/client.go`) bekommt `authType`, `credential` (Map mit Secret-Daten), `userToken` (für USER_TOKEN-Mode) als Konstruktor-Parameter |
| 1.1.3 | Switch-Statement vor jedem HTTP-Request: setzt korrekte Auth-Header je nach `authType` |
| 1.1.4 | `ENTRA_ID_USER_TOKEN`: `Authorization: Bearer <userToken>` (bestehend) |
| 1.1.5 | `ENTRA_ID_APP_REGISTRATION`: Token via `internal/services/auth/clientcredentials/token.go` (neu — analog zu Python `ClientCredentialsTokenClient`) erwerben → Cache in Redis lookup zuerst |
| 1.1.6 | `API_KEY`: Header `api-key: <secret>` (Foundry/Azure-OpenAI-Konvention) |

#### 1.2 Token-Cache (Redis)

| ID | Anforderung |
|----|-------------|
| 1.2.1 | Neue Komponente `internal/services/auth/clientcredentials/cache.go` |
| 1.2.2 | Cache-Key: `foundry:token:<sha256(tenant_id + client_id + scope)>` |
| 1.2.3 | Wert encrypted (AES-256-GCM mit Key aus Vault) — Encryption-Helper im selben Package |
| 1.2.4 | TTL = `expires_in − 30s` |
| 1.2.5 | Cache-Hit → direkt zurück; Cache-Miss → Token-Erwerb via Microsoft Identity Endpoint → schreiben → zurück |
| 1.2.6 | Bei 401-Response vom Foundry → Cache invalidieren + 1× Retry |

#### 1.3 Tests

| ID | Anforderung |
|----|-------------|
| 1.3.1 | Unit-Tests pro Auth-Mode mit gemocktem HTTP-Client |
| 1.3.2 | Cache-Tests: Hit/Miss, Encryption Round-Trip, Invalidation bei 401 |

---

### Paket 2: Test-Connection für Foundry (Platform-Service)

> Echter Agent-Ping pro Create/Edit.

#### 2.1 Endpoint

| ID | Anforderung |
|----|-------------|
| 2.1.1 | Neuer Endpoint `POST /api/v1/platform-service/tenants/{tenant_id}/chat-agents/test-connection` |
| 2.1.2 | Request-Body: vollständige Foundry-Config (`agent_type`, `api_version`, `project_endpoint`, `agent_name`, `auth_type`, `credential_id`) — funktioniert auch für Agents, die noch nicht existieren (während Create-Dialog) |
| 2.1.3 | Response: `{ success: bool, latency_ms: int, error_code?: str, error_message?: str, agent_metadata?: {...} }` |
| 2.1.4 | Implementierung: temporären Auth-Token (je nach Mode) erwerben → HTTP-GET auf `{project_endpoint}/assistants/{agent_name}?api-version={api_version}` |
| 2.1.5 | Spezifische Error-Codes: `AUTH_FAILED` (401/403), `AGENT_NOT_FOUND` (404), `INVALID_ENDPOINT` (DNS/Connection), `TIMEOUT`, `CREDENTIAL_INVALID` |
| 2.1.6 | Timeout: 10 s |

#### 2.2 Auto-Test bei Save

| ID | Anforderung |
|----|-------------|
| 2.2.1 | Optional via Query-Param `?test_connection=true` bei `POST /chat-agents` und `PUT /chat-agents/{id}` → führt vor Persistierung Test-Connection durch; bei Fehler → 422 mit Test-Result; bei Success → speichern |
| 2.2.2 | Default ist `false`, damit existierende Frontend-Calls nicht brechen |

#### 2.3 Tests

| ID | Anforderung |
|----|-------------|
| 2.3.1 | Pro Auth-Mode: Mock-HTTP-Server der 200/401/404/Timeout simuliert |
| 2.3.2 | Test-Connection-Endpoint inklusive Permission-Check (nur User mit Schreibrechten auf Chat-Agents) |

---

### Paket 3: Frontend Foundry-Dialog (Auth-Dropdown + Test-Button)

> UI-Erweiterung im Chat-Agent Create/Edit-Dialog.

#### 3.1 Types

| ID | Anforderung |
|----|-------------|
| 3.1.1 | `FoundryAuthTypeEnum` in `src/api/types.ts` mit drei Werten |
| 3.1.2 | `FoundryChatAgentConfig` Interface erweitern um `auth_type: FoundryAuthTypeEnum` und `credential_id?: string` |
| 3.1.3 | Neue Test-Connection-Types: `TestConnectionRequest`, `TestConnectionResponse` |
| 3.1.4 | API-Client (`src/api/client.ts`): neue Methode `testChatAgentConnection(tenantId, config)` |

#### 3.2 Dialog-UI

| ID | Anforderung |
|----|-------------|
| 3.2.1 | Im Foundry-Tab des Chat-Agent-Dialogs: neues Dropdown **„Authentication"** mit den 3 Optionen, Default = `User Token Forward` |
| 3.2.2 | Conditional Rendering: bei `ENTRA_ID_APP_REGISTRATION` → CredentialPicker (gefiltert auf Type `ENTRA_ID_APP_REGISTRATION`); bei `API_KEY` → CredentialPicker (gefiltert auf Type `API_KEY`); bei `USER_TOKEN` → Info-Hinweis „User-Token wird durchgereicht" |
| 3.2.3 | CredentialPicker hat Inline-Link „+ Neuer Credential" → öffnet Credential-Dialog vor (gleicher Mechanismus wie bei REST-API-Config) |
| 3.2.4 | Button **„Test Connection"** unter dem Auth-Block: ruft `/test-connection` auf, zeigt Spinner, danach grünes Häkchen (mit `latency_ms`) oder rote Error-Box (mit `error_code` + Klartext aus i18n) |
| 3.2.5 | Save-Button disabled, solange Test-Connection-State `untested` oder `failed` ist (Soft-Block: kann via Checkbox „Test überspringen" überschrieben werden, dann Server-seitig auch ohne `?test_connection=true`) |

#### 3.3 i18n

| ID | Anforderung |
|----|-------------|
| 3.3.1 | Neue Keys in `src/i18n/locales/en-US/common.json` (oder dedicated namespace) für alle Auth-Labels und Error-Codes |

#### 3.4 Tests

| ID | Anforderung |
|----|-------------|
| 3.4.1 | Vitest + RTL: Dialog rendert alle 3 Modi, conditional Felder erscheinen, Test-Button mit MSW-mock |

---

## Anhang

### Migrations-Hinweise

- **Keine SQL-Migration nötig** — `auth_type` und `credential_id` werden im JSON-Field `config` gespeichert
- Existierende Foundry-Agents bekommen beim ersten Read implicit `auth_type = ENTRA_ID_USER_TOKEN` (Default im Schema) → keine DB-Backfill nötig

### Sicherheit

- Credential-Secrets niemals im API-Response zurückgeben (außer für die Test-Connection-Route, die sie nur transient hält)
- API-Key-Credentials werden im Vault gespeichert (bestehender Mechanismus)
- Token-Cache verwendet AES-256-GCM-Encryption — Vault-Key, Encryption-Helper im selben Repo wie REST-API-Implementation

### Issue-Referenz

- [unified-ui#25](https://github.com/unified-ui/unifiedui/issues/25) — feat(svc): Support Entra ID App Reg for Foundry Agent Invocation
