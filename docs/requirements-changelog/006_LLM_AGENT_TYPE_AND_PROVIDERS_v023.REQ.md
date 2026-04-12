# 006 — LLM Agent Type, Unified Provider System & Auth Methods v0.23.0

> **Status:** DRAFT
> **Scope:** unified-ui-platform-service, unified-ui-agent-service, unified-ui-frontend-service, unifiedui (docker)
> **Ziel:** Neuen Agent-Typ `LLM` einführen, der direkt mit konfigurierten AI-Modellen chattet (mit Streaming, History, System Prompt). Alle 7 Provider vollfunktionsfähig machen. Ollama im lokalen Docker-Setup bereitstellen. Foundry Agents und Azure OpenAI um flexible Auth-Methoden erweitern (API Key, App Registration).

---

## Arbeitsweise & Prozess

> **Dieses Dokument ist das zentrale Tracking- und Anforderungsdokument.**
> Es gibt keine separate Implementierungsplan-Datei. Alles wird hier gesteuert.

### Ablauf pro Paket (0, 1, 2, …)

1. **Implementierungsübersicht**: Copilot liest den relevanten Code ein und erstellt eine kompakte Übersicht: welche Dateien betroffen sind, welcher Ansatz gewählt wird.
2. **Review**: Nutzer prüft die Übersicht, gibt OK oder Korrekturen.
3. **Implementierung**: Copilot implementiert das **gesamte Paket** (alle Teilpakete zusammen, nicht einzeln).
4. **Testhinweise**: Copilot zeigt nach Implementierung kurz auf, was der Nutzer manuell testen soll (Stichpunkte).
5. **Test & Feedback**: Nutzer testet die Implementierung und gibt Anpassungswünsche.
6. **Abschluss**: Paket wird als `✅ Done` im Titel markiert → weiter zum nächsten Paket.

### Status-Tracking

- *(kein Marker)* → Noch nicht begonnen
- `⏳ In Progress` → Gerade in Bearbeitung
- `✅ Done` → Fertig implementiert und abgenommen

### Regeln

- Immer ein **komplettes Paket** als Einheit bearbeiten (nicht Teilpakete einzeln).
- Dieses Dokument kann in jeder neuen Session als Kontext geladen werden, um den aktuellen Stand und nächsten Schritt zu kennen.
- Backend-Änderungen werden im selben Paket miterledigt, wenn das Paket Backend-Anforderungen enthält.
- Nach **jedem Paket**: `pre-commit run --all-files` ausführen und alle Fehler fixen.

---

## Kontext & Architekturentscheidungen

### Flow: LLM Agent

```
User erstellt Agent → Typ "LLM" → wählt TenantAIModel aus Settings
                                  → konfiguriert System Prompt, Temperature, Max Tokens
User chattet → Agent Service empfängt Nachricht
             → lädt AI Model Config + Credentials via Platform Service
             → baut messages[] Array (system prompt + history + user message)
             → ruft LLM API mit Streaming auf
             → forwarded SSE Events (STREAM_START → TEXT_STREAM → STREAM_END → MESSAGE_COMPLETE)
             → speichert assistant message in MongoDB
```

### LLM Agent Config Schema (im `config` JSON der ChatAgent-Tabelle)

```json
{
  "ai_model_id": "uuid-ref-to-tenant-ai-model",
  "system_prompt": "You are a helpful assistant.",
  "temperature": 0.7,
  "max_tokens": 4096
}
```

### Streaming-Architektur

Der aktuelle `LLMClient` im Agent Service unterstützt nur non-streaming (`ChatCompletion`).
Neues Interface `StreamChatCompletion` wird hinzugefügt, das einen Channel zurückgibt.
Alle 7 Provider (Azure OpenAI, OpenAI, Anthropic, Google GenAI, Ollama, Mistral, Groq) unterstützen
native Streaming über ihre APIs — die meisten sind OpenAI-kompatibel.

### Auth-Methoden-Architektur (Foundry + Azure OpenAI)

**Aktueller Stand:**
- **Foundry Agents**: Nutzer sendet sein OIDC-Token über den `X-Microsoft-Foundry-API-Key` Header. Nur User-Token-Forward.
- **Azure OpenAI (AI Models)**: Nur API-Key-Authentifizierung via `api-key` Header.

**Neues Modell — 3 Auth-Methoden für Foundry:**

| Auth-Methode | Beschreibung | Credential-Typ |
|---|---|---|
| `USER_TOKEN` (Default) | User-Token-Forward wie bisher | Kein Credential nötig |
| `API_KEY` | Foundry Project API Key | `API_KEY` Credential |
| `APP_REGISTRATION` | Entra ID Service Principal → Token-Akquise via MSAL Client Credentials | `ENTRA_ID_APP_REGISTRATION` Credential |

**Neues Modell — 2 Auth-Methoden für Azure OpenAI (AI Models):**

| Auth-Methode | Beschreibung | Credential-Typ |
|---|---|---|
| `API_KEY` (Default) | API Key wie bisher | `API_KEY` / `AI_MODEL_PROVIDER` Credential |
| `APP_REGISTRATION` | Entra ID Service Principal → Token mit Scope `https://cognitiveservices.azure.com/.default` | `ENTRA_ID_APP_REGISTRATION` Credential |

**Alle anderen LLM-Provider**: Nur API Key (keine Änderung).

**Token-Caching (App Registration):**
- Agent Service cached acquired Tokens in Redis
- Key: `token:{tenant_id}:{credential_id}:{scope_hash}`
- TTL: Token-Expiry minus 30 Sekunden
- Token wird AES-256-GCM-verschlüsselt in Redis gespeichert (bestehendes Pattern aus `internal/pkg/encryption/` + Session Service)

**Foundry Config Schema (erweitert):**
```json
{
  "agent_type": "AGENT",
  "api_version": "2025-11-15-preview",
  "project_endpoint": "https://...",
  "agent_name": "MyAgent",
  "auth_method": "USER_TOKEN | API_KEY | APP_REGISTRATION",
  "credential_id": "uuid-ref (optional, required for API_KEY und APP_REGISTRATION)"
}
```

**Azure OpenAI AI Model Config (erweitert):**
```json
{
  "endpoint": "https://...",
  "api_version": "2024-08-01-preview",
  "deployment_name": "gpt-4o",
  "auth_method": "API_KEY | APP_REGISTRATION"
}
```
Das `credential_id` auf dem `TenantAIModel` verweist auf das passende Credential (API_KEY oder ENTRA_ID_APP_REGISTRATION).

---

## Pakete

### Paket 0: Foundation — Enums, Types, Database Migration

> Grundlagen in allen Services schaffen: neuer Agent-Typ `LLM`, neuer Purpose Group `DIRECT_CHAT`, Alembic-Migration, Config-Validator.

#### 0.1 Platform Service — Enums & Migration

| ID | Anforderung |
|----|-------------|
| 0.1.1 | `ChatAgentTypeEnum` um `LLM = "LLM"` erweitern in `enums.py` |
| 0.1.2 | `AIModelPurposeGroupEnum` um `DIRECT_CHAT = "DIRECT_CHAT"` erweitern in `enums.py` |
| 0.1.3 | Alembic-Migration erstellen, die den neuen Enum-Wert `LLM` für `chat_agents.type` und `DIRECT_CHAT` für Purpose Groups hinzufügt |
| 0.1.4 | `ChatAgentConfigValidatorFactory` um `LLMConfigValidator` erweitern — validiert: `ai_model_id` (required, UUID), `system_prompt` (optional, str, max 10000 chars), `temperature` (optional, float, 0.0–2.0, default 0.7), `max_tokens` (optional, int, 1–100000, default 4096) |

#### 0.2 Agent Service — Type Constants

| ID | Anforderung |
|----|-------------|
| 0.2.1 | Neue Konstante `AgentTypeLLM = "LLM"` in Agent-Type-Definitionen hinzufügen |
| 0.2.2 | `SendMessage` Handler: neuen Case `AgentTypeLLM` → `handleLLMStreaming` (Stub, wird in Paket 2 implementiert) |

#### 0.3 Frontend — Type Enum

| ID | Anforderung |
|----|-------------|
| 0.3.1 | `ChatAgentTypeEnum` um `LLM: 'LLM'` erweitern in `types.ts` |
| 0.3.2 | `AIModelPurposeGroupEnum` um `DIRECT_CHAT: 'DIRECT_CHAT'` erweitern in `types.ts` (falls vorhanden, sonst anlegen) |

---

### Paket 1: Platform Service — LLM Agent CRUD & AI Model Endpoint

> Platform Service um LLM-Agent-spezifische Logik erweitern. Neuen Endpoint für das Abrufen eines einzelnen AI Models mit Secret bereitstellen (Agent Service braucht dies für LLM-Agents).

#### 1.1 ChatAgent Handler — LLM-Typ-Logik

| ID | Anforderung |
|----|-------------|
| 1.1.1 | `create_chat_agent`: Wenn Typ `LLM`, validiere dass `ai_model_id` in `config` auf ein existierendes `TenantAIModel` desselben Tenants verweist |
| 1.1.2 | `update_chat_agent`: Gleiche Validierung wie bei Create |
| 1.1.3 | Schema: `LLMAgentConfig` Pydantic-Modell als Referenz-Dokumentation (das eigentliche Schema ist im Validator) |

#### 1.2 AI Model — Get by ID with Secret

| ID | Anforderung |
|----|-------------|
| 1.2.1 | Neuer interner Endpoint (Service-Key-Auth): `GET /api/v1/internal/tenants/{tenant_id}/ai-models/{ai_model_id}/with-secret` — gibt AI Model inkl. entschlüsseltem Credential Secret zurück |
| 1.2.2 | Response-Schema: `AIModelWithSecretResponse` (id, type, provider, config, credential_secret, priority) |
| 1.2.3 | Validierung: AI Model muss existieren, zum Tenant gehören, und `is_active` sein |

---

### Paket 2: Agent Service — LLM Streaming Implementation

> Streaming LLM Client und neuer Handler für den `LLM` Agent-Typ im Agent Service.

#### 2.1 Streaming LLM Client Interface

| ID | Anforderung |
|----|-------------|
| 2.1.1 | Neues Interface `StreamingLLMClient` mit Methode `StreamChatCompletion(ctx, messages []ChatMessage, opts StreamOptions) (<-chan StreamChunk, error)` |
| 2.1.2 | `StreamOptions` Struct: `Temperature *float64`, `MaxTokens *int`, `SystemPrompt *string` |
| 2.1.3 | `StreamChunk` Struct: `Content string`, `Done bool`, `Error error` |
| 2.1.4 | Factory-Methode `NewStreamingLLMClient(provider string, config, credentialSecret map[string]interface{}) (StreamingLLMClient, error)` |

#### 2.2 Provider-Implementierungen (Streaming)

| ID | Anforderung |
|----|-------------|
| 2.2.1 | **Azure OpenAI**: Streaming via Azure OpenAI REST API (`stream: true`), SSE-Parsing |
| 2.2.2 | **OpenAI**: Streaming via OpenAI API (`stream: true`) — OpenAI-kompatibles Format |
| 2.2.3 | **Anthropic**: Streaming via Anthropic Messages API (`stream: true`) — eigenes SSE-Format |
| 2.2.4 | **Google GenAI**: Streaming via Gemini API (`streamGenerateContent`) |
| 2.2.5 | **Ollama**: Streaming via Ollama API (`/api/chat` mit `stream: true`) |
| 2.2.6 | **Mistral**: Streaming via Mistral API (OpenAI-kompatibel, `stream: true`) |
| 2.2.7 | **Groq**: Streaming via Groq API (OpenAI-kompatibel, `stream: true`) |

#### 2.3 Platform Client — AI Model by ID

| ID | Anforderung |
|----|-------------|
| 2.3.1 | Neue Methode `GetAIModelByID(ctx, tenantID, aiModelID string) (*AIModelWithSecretResponse, error)` im Platform Client Interface |
| 2.3.2 | Implementierung: ruft den neuen internen Endpoint aus Paket 1.2 auf |

#### 2.4 LLM Streaming Handler

| ID | Anforderung |
|----|-------------|
| 2.4.1 | `handleLLMStreaming` Funktion: Extrahiert `ai_model_id`, `system_prompt`, `temperature`, `max_tokens` aus Agent Config |
| 2.4.2 | Ruft AI Model mit Secret via Platform Client ab (`GetAIModelByID`) |
| 2.4.3 | Erstellt `StreamingLLMClient` via Factory |
| 2.4.4 | Baut messages Array: System Prompt (wenn vorhanden) → Chat History → User Message |
| 2.4.5 | Emittiert SSE Events: `STREAM_START` → `TEXT_STREAM` (pro Chunk) → `STREAM_END` → `MESSAGE_COMPLETE` |
| 2.4.6 | Speichert vollständige Assistant-Nachricht in MongoDB nach Stream-Ende |
| 2.4.7 | Error Handling: `ERROR` SSE Event bei Provider-Fehlern, Timeout, etc. |

---

### Paket 3: Frontend — Create/Edit LLM Agent

> LLM-Typ im CreateChatAgentDialog und EditChatAgentDialog. AI Model Selector, System Prompt Editor, Parameter-Konfiguration.

#### 3.1 Create Chat Agent Dialog

| ID | Anforderung |
|----|-------------|
| 3.1.1 | `CHAT_AGENT_TYPES` um `{ value: 'LLM', label: 'LLM' }` erweitern |
| 3.1.2 | Wenn Typ `LLM` ausgewählt: AI Model Dropdown anzeigen (filtert TenantAIModels mit `type=LLM_MODEL`) |
| 3.1.3 | AI Model Dropdown zeigt: `{name} ({provider})` — z.B. "GPT-4o (OpenAI)" |
| 3.1.4 | System Prompt Textarea (optional, Placeholder: "You are a helpful assistant.") |
| 3.1.5 | Temperature Slider (0.0–2.0, Default 0.7, Step 0.1) |
| 3.1.6 | Max Tokens NumberInput (1–100000, Default 4096) |
| 3.1.7 | Config wird als JSON gebaut: `{ ai_model_id, system_prompt, temperature, max_tokens }` |

#### 3.2 Edit Chat Agent Dialog

| ID | Anforderung |
|----|-------------|
| 3.2.1 | Gleiche Felder wie beim Create, vorausgefüllt mit existierendem Config |
| 3.2.2 | AI Model Dropdown zeigt aktuell gewähltes Model an |
| 3.2.3 | Typ-Feld ist beim Edit disabled (kein Typ-Wechsel) |

#### 3.3 AI Model Fetching

| ID | Anforderung |
|----|-------------|
| 3.3.1 | API Client: Endpoint zum Abrufen aller Tenant AI Models nutzen (existiert bereits) |
| 3.3.2 | Filtern auf `type=LLM_MODEL` und `is_active=true` im Dropdown |

---

### Paket 4: AI Models Settings — Provider Cleanup & Test Connection

> Sicherstellen, dass alle 7 Provider in den AI-Model-Settings korrekt konfiguriert und getestet werden können.

#### 4.1 Backend — Test Connection für alle Provider

| ID | Anforderung |
|----|-------------|
| 4.1.1 | Test-Connection-Endpoint prüfen: Funktioniert er für alle 7 Provider korrekt? |
| 4.1.2 | Falls nicht: Provider-spezifische Test-Logik implementieren (einfacher Health-Check / Model-List-Call) |
| 4.1.3 | Ollama: Test-Connection via `GET {base_url}/api/tags` (listet verfügbare Models) |

#### 4.2 Frontend — AI Model Dialog Verbesserungen

| ID | Anforderung |
|----|-------------|
| 4.2.1 | `DIRECT_CHAT` als neue Purpose Group im MultiSelect anzeigen |
| 4.2.2 | Prüfen ob alle Provider-spezifischen Felder im AIModelDialog korrekt angezeigt werden |
| 4.2.3 | Ollama: `Base URL` Default-Wert `http://ollama:11434` (Docker) bzw. `http://localhost:11434` (lokal) |

---

### Paket 5: Docker — Ollama Container

> Ollama in das lokale Docker-Compose-Setup integrieren.

#### 5.1 Docker Compose

| ID | Anforderung |
|----|-------------|
| 5.1.1 | Neue `ollama.yml` Include-Datei erstellen |
| 5.1.2 | Ollama Service: Image `ollama/ollama:latest`, Port `11434:11434`, Volume für Model-Storage |
| 5.1.3 | Modelinitialisierung: Init-Container oder Entrypoint-Script das `llama3.2:3b` beim ersten Start pullt |
| 5.1.4 | In `docker-compose.yml` einbinden (optional include, damit es nicht jeden Dev zwingt) |
| 5.1.5 | Ollama muss im selben Docker-Netzwerk wie Agent Service sein (erreichbar via `http://ollama:11434`) |

---

### Paket 6: Foundry Agent — Flexible Auth Methods (API Key + App Registration)

> Foundry Agents um alternative Auth-Methoden erweitern: API Key und Entra ID App Registration neben dem bestehenden User-Token-Forward.

#### 6.1 Platform Service — Foundry Config erweitern

| ID | Anforderung |
|----|-------------|
| 6.1.1 | Neues Enum `FoundryAuthMethodEnum` in `enums.py`: `USER_TOKEN`, `API_KEY`, `APP_REGISTRATION` |
| 6.1.2 | `MicrosoftFoundryChatAgentConfig` Validator erweitern: + `auth_method` (required, default `USER_TOKEN`), + `credential_id` (optional, required wenn auth_method ≠ USER_TOKEN) |
| 6.1.3 | Validierung: Wenn `auth_method = API_KEY` → `credential_id` muss auf Credential vom Typ `API_KEY` verweisen. Wenn `auth_method = APP_REGISTRATION` → `credential_id` muss auf Credential vom Typ `ENTRA_ID_APP_REGISTRATION` verweisen |
| 6.1.4 | `MicrosoftFoundryConfigSettingsResponse` erweitern: + `auth_method`, + `credential_id`, + `credential_secret` (entschlüsseltes Secret, nur bei API_KEY/APP_REGISTRATION) |
| 6.1.5 | Alembic-Migration für neuen Enum-Wert (falls DB-Enum für auth_method nötig — prüfen ob JSON-Feld reicht) |

#### 6.2 Agent Service — Foundry Auth-Logik

| ID | Anforderung |
|----|-------------|
| 6.2.1 | `SendMessage` Handler: Wenn Foundry Agent mit `auth_method = USER_TOKEN` → bestehende Logik (Token aus Header) |
| 6.2.2 | Wenn `auth_method = API_KEY` → API Key aus `credential_secret` extrahieren, als `apiToken` an WorkflowClient übergeben |
| 6.2.3 | Wenn `auth_method = APP_REGISTRATION` → Token via MSAL Client Credentials Flow akquirieren (tenant_id, client_id, client_secret aus Credential Secret). Default-Scope: `https://management.azure.com/.default` (funktioniert für Foundry Endpoints) |
| 6.2.4 | Token-Caching in Redis: Key `token:{tenant_id}:{credential_id}`, TTL = Expiry - 30s, AES-256-GCM-verschlüsselt (bestehendes Encryptor-Pattern aus Session Service wiederverwenden) |
| 6.2.5 | MSAL-Integration: Go-Library für OAuth2 Client Credentials (z.B. `golang.org/x/oauth2/clientcredentials` oder `github.com/AzureAD/microsoft-authentication-library-for-go`) |
| 6.2.6 | `X-Microsoft-Foundry-API-Key` Header wird weiterhin als Fallback akzeptiert für `USER_TOKEN`; bei API_KEY/APP_REGISTRATION kommt der Token serverseitig |

#### 6.3 Frontend — Foundry Auth-UI

| ID | Anforderung |
|----|-------------|
| 6.3.1 | Neues Select-Feld "Authentication Method" im Foundry-Config-Bereich: `User Token` (default), `API Key`, `App Registration` |
| 6.3.2 | Wenn Auth Method ≠ User Token → Credential-Dropdown (FilteredSelect) anzeigen, gefiltert auf passenden Credential-Typ |
| 6.3.3 | Bei `User Token` → kein Credential-Feld, Hinweis dass der User-Token weitergeleitet wird |
| 6.3.4 | Gleiche Änderungen in EditChatAgentDialog |
| 6.3.5 | Frontend sendet `X-Microsoft-Foundry-API-Key` Header NICHT mehr bei `API_KEY` / `APP_REGISTRATION` (Agent Service regelt das serverseitig) |

---

### Paket 7: Azure OpenAI — App Registration Auth für AI Models

> Azure OpenAI AI Models um App-Registration-Authentifizierung erweitern, neben dem bestehenden API Key.

#### 7.1 Platform Service — Azure OpenAI Config erweitern

| ID | Anforderung |
|----|-------------|
| 7.1.1 | `AzureOpenAIConfigValidator` erweitern: + `auth_method` (optional, default `API_KEY`, Werte: `API_KEY`, `APP_REGISTRATION`) |
| 7.1.2 | Validierung: Wenn `auth_method = APP_REGISTRATION` → `credential_id` auf TenantAIModel muss auf `ENTRA_ID_APP_REGISTRATION` Credential verweisen |
| 7.1.3 | Wenn `auth_method = API_KEY` → bestehendes Verhalten (API Key aus Credential) |

#### 7.2 Agent Service — Azure OpenAI Auth-Logik

| ID | Anforderung |
|----|-------------|
| 7.2.1 | LLM Client Factory: Wenn Azure OpenAI mit `auth_method = APP_REGISTRATION` → Token via MSAL akquirieren statt API Key. Scope: `https://cognitiveservices.azure.com/.default` |
| 7.2.2 | Token-Caching in Redis wiederverwenden (gleiche Logik wie Paket 6.2.4) |
| 7.2.3 | Azure OpenAI Client: `Authorization: Bearer <token>` Header statt `api-key` Header bei App-Reg-Auth |
| 7.2.4 | Bestehender (non-streaming) `ChatCompletion` Client: gleiche Auth-Logik integrieren |
| 7.2.5 | Neuer (streaming) Client aus Paket 2: gleiche Auth-Logik integrieren |

#### 7.3 Frontend — AI Model Dialog

| ID | Anforderung |
|----|-------------|
| 7.3.1 | Wenn Provider = Azure OpenAI: neues Select "Authentication Method" (`API Key` default, `App Registration`) |
| 7.3.2 | Bei `App Registration` → Credential-Dropdown auf `ENTRA_ID_APP_REGISTRATION` Credentials filtern |
| 7.3.3 | Bei `API Key` → bestehendes Verhalten (Credential-Dropdown zeigt API Key / AI Model Provider Credentials) |

---

## Dependency Graph

```
Paket 0 (Foundation)
   ├──→ Paket 1 (Platform Service LLM CRUD)
   │       └──→ Paket 2 (Agent Service Streaming)
   │               └──→ Paket 3 (Frontend LLM Agent UI)
   ├──→ Paket 4 (AI Model Provider Cleanup) — unabhängig von 1-3
   ├──→ Paket 5 (Docker Ollama) — unabhängig von 1-4
   ├──→ Paket 6 (Foundry Auth Methods) — unabhängig von 1-5
   └──→ Paket 7 (Azure OpenAI App Reg) — abhängig von Paket 2 (Streaming Client) + Paket 6 (Token-Caching-Infrastruktur)
```

Pakete 4, 5, 6 können unabhängig voneinander und parallel zu Paketen 1-3 implementiert werden.
Paket 7 baut auf der Token-Caching-Infrastruktur aus Paket 6 und dem Streaming-Client aus Paket 2 auf.

---

## Offene Fragen

- [ ] Soll der LLM Agent ein eigenes Icon/Badge im Agent-Listing bekommen? (z.B. ein Brain-Icon oder das Provider-Logo)
- [ ] Soll es ein Token-Limit-Warning geben, wenn die Chat-History zu lang wird? (Context Window Management)
- [ ] Soll der System Prompt auch zur Laufzeit im Chat änderbar sein, oder nur in der Agent-Konfiguration?

---

## Anhang

### Referenzen

- [Issue #19: Support for Direct LLM Providers](https://github.com/unified-ui/unifiedui/issues/19)
- [Issue #21: Unified LLM Provider System: Azure, OpenAI, Gemini & Ollama](https://github.com/unified-ui/unifiedui/issues/21)
- [Issue #25: Support Entra ID App Reg for Foundry Agent Invocation](https://github.com/unified-ui/unifiedui/issues/25)

### Betroffene Dateien (Übersicht)

| Service | Datei | Änderung |
|---------|-------|----------|
| **LLM Agent Feature** | | |
| Platform | `core/database/enums.py` | + `LLM`, `DIRECT_CHAT` |
| Platform | `handlers/validators/chat_agent_config.py` | + `LLMConfigValidator` |
| Platform | `handlers/chat_agents.py` | + ai_model_id Validierung |
| Platform | `apis/v1/tenant_ai_models.py` | + internal get-with-secret |
| Platform | `handlers/tenant_ai_models.py` | + get-with-secret handler |
| Platform | Alembic Migration | + enum values |
| Agent | `services/platform/client.go` | + `GetAIModelByID` |
| Agent | `services/ai/streaming.go` (NEU) | StreamingLLMClient |
| Agent | `services/ai/providers/*.go` (NEU) | 7 Streaming-Provider |
| Agent | `api/handlers/messages_send.go` | + LLM case |
| Agent | `api/handlers/messages_send_llm.go` (NEU) | handleLLMStreaming |
| Frontend | `api/types.ts` | + LLM enum, DIRECT_CHAT |
| Frontend | `CreateChatAgentDialog.tsx` | + LLM Formular |
| Frontend | `EditChatAgentDialog.tsx` | + LLM Formular |
| Frontend | `AIModelDialog.tsx` | + DIRECT_CHAT purpose |
| Docker | `docker/local/ollama.yml` (NEU) | Ollama Container |
| Docker | `docker/local/docker-compose.yml` | + ollama include |
| **Auth Methods Feature** | | |
| Platform | `core/database/enums.py` | + `FoundryAuthMethodEnum` |
| Platform | `handlers/validators/chat_agent_config.py` | Foundry Validator erweitern |
| Platform | `handlers/validators/tenant_ai_model_validator.py` | Azure OpenAI Validator erweitern |
| Platform | `schema/responses/chat_agents.py` | + auth_method, credential_secret |
| Agent | `api/handlers/messages_send.go` | Foundry auth routing |
| Agent | `services/auth/token_provider.go` (NEU) | MSAL Client Credentials + AES-256-GCM Redis Cache |
| Agent | `services/agents/foundry/workflow_client.go` | Auth-Methoden-Support |
| Agent | `services/ai/providers.go` | Azure OpenAI Bearer Token Support |
| Frontend | `CreateChatAgentDialog.tsx` | + Foundry auth method + credential |
| Frontend | `EditChatAgentDialog.tsx` | + Foundry auth method + credential |
| Frontend | `AIModelDialog.tsx` | + Azure OpenAI auth method |
