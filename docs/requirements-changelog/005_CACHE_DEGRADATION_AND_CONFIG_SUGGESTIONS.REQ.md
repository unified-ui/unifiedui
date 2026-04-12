# 005 — Cache Degradation & Config Suggestions

> **Status:** DRAFT
> **Scope:** unified-ui-agent-service, unified-ui-platform-service, unified-ui-frontend-service
> **Goal:** (A) Services start and operate without Redis cache via NoOp fallback. (B) Endpoint fields in agent/workflow config suggest previously used values. (C) Foundry agent discovery and N8N workflow browser for smarter config.

---

## Working Process

> **This document is the central tracking and requirements document.**
> There is no separate implementation plan file. Everything is managed here.

### Process per Package (0, 1, 2, …)

1. **Implementation Overview**: Copilot reads the relevant code and creates a compact overview: which files are affected, which approach is chosen.
2. **Review**: User reviews the overview, gives OK or corrections.
3. **Implementation**: Copilot implements the **entire package** (all sub-packages together, not individually).
4. **Test Notes**: Copilot shows after implementation what the user should manually test (bullet points).
5. **Test & Feedback**: User tests the implementation and gives adjustment requests.
6. **Completion**: Package is marked as `✅ Done` in the title → continue to next package.

### Status Tracking

Each package gets a status marker in the title:
- *(no marker)* → Not yet started
- `⏳ In Progress` → Currently being worked on
- `✅ Done` → Implemented and accepted

### Rules

- Always work on a **complete package** as a unit (not sub-packages individually).
- This document can be loaded as context in any new session to know the current state and next step.
- Backend changes are handled in the same package if the package contains backend requirements.
- After **every package**: Run `pre-commit run --all-files` and fix all errors.

---

## References

- GitHub Issue #36: [Services fail to start when Redis cache is unavailable](https://github.com/unified-ui/unifiedui/issues/36)
- GitHub Issue #28: [Reusable endpoint suggestions in agent and workflow config](https://github.com/unified-ui/unifiedui/issues/28)

---

## Packages

### Package 0: NoOp Cache — Agent Service (Go)

> Add a NoOp cache implementation to the agent-service that fulfills the `cache.Cache` and `cache.Client` interfaces but does nothing. Update the factory to fall back to NoOp when Redis is unavailable or cache type is `none`/empty.

**Context & Research:**
- Cache interface: `internal/core/cache/cache.go` — `Cache` interface with `Get`, `Set`, `Delete`, `DeletePattern`, `Ping`, `Close`
- Client interface: `internal/core/cache/client.go` — `Client` wrapping `Cache`
- Redis implementation: `internal/infrastructure/cache/redis/cache.go` — pings on init, returns error on failure
- Factory: `cmd/server/main.go` → `createCacheClient()` — currently `log.Fatalf` on unsupported type, returns error on Redis failure → service crashes
- Reference pattern: `internal/pkg/encryption/encryption.go` → `NoOpEncryptor`
- Cache type constants: `internal/core/cache/cache.go` → `TypeRedis`

**Approach:**
1. Create `internal/infrastructure/cache/noop/cache.go` implementing `cache.Cache` — `Get` returns nil/cache-miss, `Set`/`Delete` are no-ops, `Ping` returns nil
2. Create `internal/infrastructure/cache/noop/client.go` implementing `cache.Client` using the NoOp cache
3. Add `TypeNone` constant to `internal/core/cache/cache.go`
4. Update `createCacheClient` in `cmd/server/main.go`:
   - `TypeNone` / empty → return NoOp client
   - `TypeRedis` with connection failure → log warning, return NoOp client (instead of fatal error)
5. Add unit tests for NoOp cache

#### 0.1 NoOp Cache Implementation

| ID | Requirement |
|----|-------------|
| 0.1.1 | Create `NoOpCache` struct in `internal/infrastructure/cache/noop/cache.go` implementing the `cache.Cache` interface |
| 0.1.2 | `Get()` returns `nil, nil` (cache miss, no error) |
| 0.1.3 | `Set()` returns `nil` (does nothing) |
| 0.1.4 | `Delete()` returns `false, nil` |
| 0.1.5 | `DeletePattern()` returns `0, nil` |
| 0.1.6 | `Ping()` returns `nil` |
| 0.1.7 | `Close()` returns `nil` |

#### 0.2 NoOp Client Implementation

| ID | Requirement |
|----|-------------|
| 0.2.1 | Create `NoOpClient` struct in `internal/infrastructure/cache/noop/client.go` implementing the `cache.Client` interface using `NoOpCache` |
| 0.2.2 | Constructor: `NewClient() cache.Client` |

#### 0.3 Factory Update

| ID | Requirement |
|----|-------------|
| 0.3.1 | Add `TypeNone cache.Type = "none"` constant in `internal/core/cache/cache.go` |
| 0.3.2 | Update `createCacheClient` in `cmd/server/main.go`: when `TypeNone` or empty string → return `noop.NewClient()` |
| 0.3.3 | Update `createCacheClient`: when `TypeRedis` and Redis connection fails → log warning and return `noop.NewClient()` instead of returning error |
| 0.3.4 | Remove `log.Fatalf` for unsupported cache type — return proper error instead |

#### 0.4 Tests

| ID | Requirement |
|----|-------------|
| 0.4.1 | Unit tests for `NoOpCache` — all interface methods return expected zero values |
| 0.4.2 | Unit tests for `NoOpClient` — get/set/delete operations behave as cache miss |

---

### Package 1: NoOp Cache — Platform Service (Python)

> Add a NoOp cache implementation to the platform-service. Refactor the existing `None` cache pattern: handlers currently receive `CacheClient | None` and check `if cache_client:`. Instead, always provide a cache client (NoOp when cache is disabled/unavailable) so handlers don't need None checks.

**Context & Research:**
- Cache interface (ABC): `unifiedui/core/caching/` — `BaseCache` with `get`, `set`, `delete`, `delete_pattern`, `ping`, `close`
- Redis implementation: `unifiedui/caching/redis/cache.py`
- Factory: `unifiedui/caching/client.py` → `CacheClientFactory.create()`
- Dependency: `unifiedui/caching/dependencies.py` → `get_cache_client()` returns `CacheClient | None`
- Enum: `unifiedui/caching/enums.py` → `CacheTypeEnum` (currently only `REDIS`)
- Config: `unifiedui/core/config.py` → `cache_enabled: bool`, `cache_backend: str | None`
- Handlers receive `CacheClient | None` via `Depends(get_cache_client)` and check for `None`

**Approach:**
1. Create `unifiedui/caching/noop/cache.py` implementing `BaseCache`
2. Add `NONE = "NONE"` to `CacheTypeEnum`
3. Update `CacheClientFactory.create()` to support `NONE` type
4. Update `get_cache_client` dependency to return `NoOpCacheClient` (wrapped in `CacheClient`) instead of `None` when cache is disabled
5. When `cache_backend=REDIS` but Redis unavailable → log warning, return NoOp client
6. Refactor handler dependency signatures: `CacheClient | None` → `CacheClient` (remove None checks)
7. Add unit tests

#### 1.1 NoOp Cache Implementation

| ID | Requirement |
|----|-------------|
| 1.1.1 | Create `NoOpCache` class in `unifiedui/caching/noop/cache.py` implementing `BaseCache` |
| 1.1.2 | `get()` returns `None` (cache miss) |
| 1.1.3 | `set()` does nothing |
| 1.1.4 | `delete()` returns `False` |
| 1.1.5 | `delete_pattern()` returns `0` |
| 1.1.6 | `ping()` returns `None` (no error) |
| 1.1.7 | `close()` does nothing |

#### 1.2 Factory & Dependency Update

| ID | Requirement |
|----|-------------|
| 1.2.1 | Add `NONE = "NONE"` to `CacheTypeEnum` in `unifiedui/caching/enums.py` |
| 1.2.2 | Update `CacheClientFactory.create()` to handle `CacheTypeEnum.NONE` → return `CacheClient(NoOpCache())` |
| 1.2.3 | Update `CacheClientFactory.create()`: when `CacheTypeEnum.REDIS` and connection fails → log warning, return `CacheClient(NoOpCache())` |
| 1.2.4 | Update `get_cache_client` dependency: when `cache_enabled=False` → return `CacheClient(NoOpCache())` instead of `None` |
| 1.2.5 | Change return type of `get_cache_client` from `CacheClient | None` to `CacheClient` |

#### 1.3 Handler Refactoring

| ID | Requirement |
|----|-------------|
| 1.3.1 | Update all handler dependency signatures: change `cache_client: CacheClient | None` to `cache_client: CacheClient` |
| 1.3.2 | Remove all `if cache_client:` / `if cache_client is not None:` guards in handlers — call cache methods directly (NoOp handles the no-cache case) |

#### 1.4 Tests

| ID | Requirement |
|----|-------------|
| 1.4.1 | Unit tests for `NoOpCache` — all interface methods return expected values |
| 1.4.2 | Test that `get_cache_client` returns `CacheClient` (not `None`) when cache is disabled |
| 1.4.3 | Test factory fallback when Redis is unavailable |

---

### Package 2: Config Suggestions API — Platform Service

> Add a new API endpoint that returns distinct endpoint/URL values from chat agent and workflow configs within a tenant, filtered by platform type. This enables the frontend to suggest previously used endpoints when configuring agents/workflows.

**Context & Research:**
- Chat agent config fields per type:
  - n8n: `chat_url`, `workflow_endpoint` (in `config` JSON)
  - Foundry: `project_endpoint`
  - REST: `invoke_endpoint`, `create_conversation_endpoint`
- Workflow config fields:
  - n8n: `workflow_endpoint`, `webhook_url`
- Config validators: `unifiedui/handlers/validators/chat_agent_config.py`, `workflow_config.py`
- Models: `ChatAgent` and `Workflow` in `unifiedui/core/database/models.py` — both have `config` (PortableJSON) and `type` fields
- Existing route pattern: `unifiedui/apis/v1/` with tenant-scoped routes

**Approach:**
1. Create new route: `GET /api/v1/tenants/{tenant_id}/config-suggestions?type={platform_type}&q={search_term}`
2. Handler queries `chat_agents` and `workflows` tables for the given tenant and type
3. Extracts distinct endpoint values from the JSON `config` column based on the known field names per platform type
4. Filters results by `q` parameter (case-insensitive substring match) if provided
5. Returns a response with grouped suggestions (field name → list of distinct values)
6. No Redis caching for v1 — simple DB query

#### 2.1 Schema

| ID | Requirement |
|----|-------------|
| 2.1.1 | Create `ConfigSuggestionsResponse` Pydantic model in `unifiedui/schema/responses/config_suggestions.py` with structure: `{ suggestions: dict[str, list[str]] }` where keys are field names (e.g., `project_endpoint`) and values are distinct URL lists |
| 2.1.2 | Create `ConfigSuggestionsQueryParams` with `type: str` (platform type: `n8n`, `foundry`, `rest`, `copilot`, `langgraph`) and `q: str | None` (optional search filter) |

#### 2.2 Handler

| ID | Requirement |
|----|-------------|
| 2.2.1 | Create `ConfigSuggestionsHandler` in `unifiedui/handlers/config_suggestions.py` |
| 2.2.2 | Define a mapping of platform type → list of config field names to extract (e.g., `n8n` → `["chat_url", "workflow_endpoint"]`, `foundry` → `["project_endpoint"]`) |
| 2.2.3 | Query `chat_agents` table for given tenant + type, extract distinct values from config JSON for each mapped field |
| 2.2.4 | Query `workflows` table for given tenant + type (if applicable), extract distinct values from config JSON for each mapped field |
| 2.2.5 | Merge and deduplicate results per field |
| 2.2.6 | If `q` parameter is provided, filter all suggestion values by case-insensitive substring match |
| 2.2.7 | Return `ConfigSuggestionsResponse` |

#### 2.3 Route & Dependency

| ID | Requirement |
|----|-------------|
| 2.3.1 | Add route `GET /api/v1/tenants/{tenant_id}/config-suggestions` in `unifiedui/apis/v1/config_suggestions.py` |
| 2.3.2 | Route requires authentication (use `@authenticate` decorator) |
| 2.3.3 | Route requires tenant membership (user must have access to the tenant) |
| 2.3.4 | Create `get_config_suggestions_handler` dependency in `unifiedui/handlers/dependencies/config_suggestions.py` |
| 2.3.5 | Register route in the router setup |

#### 2.4 Tests

| ID | Requirement |
|----|-------------|
| 2.4.1 | Test: returns empty suggestions when no agents/workflows exist |
| 2.4.2 | Test: returns distinct endpoint values for n8n type |
| 2.4.3 | Test: returns distinct endpoint values for foundry type |
| 2.4.4 | Test: returns distinct endpoint values for REST type |
| 2.4.5 | Test: merges suggestions from chat_agents and workflows |
| 2.4.6 | Test: authentication required |
| 2.4.7 | Test: tenant scoping (only returns config from user's tenant) |

---

### Package 3: Endpoint Suggestions UI — Frontend

> Replace text input fields for endpoint/URL config with a creatable combobox that suggests previously used endpoints from the tenant. Users can select an existing endpoint or type a new custom value. Restructure dialogs so credential selection appears before endpoint fields.

**Context & Research:**
- Existing `FilterableSelect` component does NOT support free-text input
- Affected dialogs:
  - `src/components/dialogs/CreateChatAgentDialog/CreateChatAgentDialog.tsx`
  - `src/components/dialogs/EditChatAgentDialog/EditChatAgentDialog.tsx`
  - `src/components/dialogs/CreateWorkflowDialog/CreateWorkflowDialog.tsx`
  - `src/components/dialogs/EditWorkflowDialog/EditWorkflowDialog.tsx`
- Endpoint fields per dialog (suggestions apply to):
  - n8n ChatAgent: `n8n_chat_url`, `n8n_workflow_endpoint` (NOT `webhook_url` — must be copied 1:1)
  - Foundry ChatAgent: `foundry_project_endpoint`
  - REST ChatAgent: `rest_api_invoke_endpoint`, `rest_api_create_conversation_endpoint`
  - n8n Workflow: `n8n_workflow_endpoint` (NOT `webhook_url`)
- Credential form fields: `n8n_api_api_key_credential_id`, `n8n_chat_auth_credential_id`, `rest_api_credential_id`
- API client: `src/api/client.ts`

**Approach:**
1. Add `getConfigSuggestions(tenantId, type, q?)` to API client
2. Create new `EndpointSuggestInput` component (creatable Mantine Combobox with free-text support)
3. Create `useConfigSuggestions(tenantId, type)` hook that fetches suggestions
4. Restructure dialogs: move credential dropdown above endpoint fields (needed for Package 4+5 where credential must be known before querying)
5. Replace `TextInput` with `EndpointSuggestInput` for endpoint/URL fields in all 4 dialogs
6. Fetch suggestions when platform type is selected; don't fetch if no credential is selected (for types that require it)

#### 3.1 API Client

| ID | Requirement |
|----|-------------|
| 3.1.1 | Add `getConfigSuggestions(tenantId: string, type: string, q?: string): Promise<ConfigSuggestionsResponse>` to `src/api/client.ts` |
| 3.1.2 | Add `ConfigSuggestionsResponse` type to `src/api/types.ts`: `{ suggestions: Record<string, string[]> }` |

#### 3.2 Hook

| ID | Requirement |
|----|-------------|
| 3.2.1 | Create `useConfigSuggestions(tenantId: string, type: string)` hook in `src/hooks/useConfigSuggestions.ts` |
| 3.2.2 | Returns `{ suggestions: Record<string, string[]>, isLoading: boolean }` |
| 3.2.3 | Fetches suggestions when `type` changes (re-fetches on type change) |
| 3.2.4 | Returns empty suggestions when type is not set |

#### 3.3 EndpointSuggestInput Component

| ID | Requirement |
|----|-------------|
| 3.3.1 | Create `EndpointSuggestInput` component in `src/components/common/EndpointSuggestInput/` |
| 3.3.2 | Uses Mantine `Combobox` with editable search input (free-text allowed) |
| 3.3.3 | Props: `label`, `placeholder`, `description`, `required`, `suggestions: string[]`, `value`, `onChange`, `error` — compatible with `form.getInputProps()` |
| 3.3.4 | Shows suggestion dropdown when input is focused and suggestions exist |
| 3.3.5 | Filters suggestions as user types (client-side filtering is sufficient; `q` param available for future server-side filtering if lists grow) |
| 3.3.6 | User can select from suggestions OR type a custom value |

#### 3.4 Dialog Restructuring & Integration

| ID | Requirement |
|----|-------------|
| 3.4.1 | In all 4 dialogs: move credential selection dropdown(s) above the endpoint fields so credentials are chosen before endpoints |
| 3.4.2 | `CreateChatAgentDialog`: fetch suggestions when platform type is selected, pass to `EndpointSuggestInput` for each endpoint field |
| 3.4.3 | `EditChatAgentDialog`: same as above, with pre-filled current values |
| 3.4.4 | `CreateWorkflowDialog`: fetch suggestions for workflow endpoint fields |
| 3.4.5 | `EditWorkflowDialog`: same as above, with pre-filled current values |
| 3.4.6 | Map suggestion response fields to the correct form fields (e.g., `project_endpoint` suggestions → `foundry_project_endpoint` input) |
| 3.4.7 | Do NOT add suggestions to `webhook_url` fields (n8n) — these must be copied 1:1 |

#### 3.5 Tests

| ID | Requirement |
|----|-------------|
| 3.5.1 | Unit test for `EndpointSuggestInput`: renders suggestions, allows free-text input |
| 3.5.2 | Unit test for `useConfigSuggestions` hook |

---

### Package 4: Foundry Agent Discovery — Platform Service + Frontend

> When configuring a Foundry chat agent, after entering the `project_endpoint`, the agent name field should show a list of available agents fetched from the Foundry API. This replaces manual typing of agent names with a discoverable dropdown.

**Context & Research:**
- Foundry REST API supports listing agents via the Azure AI Foundry project endpoint
- Auth: User's MSAL token is passed through (bearer token passthrough, same pattern as agent invocation)
- Agent Service (`internal/services/agents/foundry/workflow_client.go`) uses direct HTTP calls to Foundry REST API with bearer token
- Platform Service does NOT currently have Foundry SDK dependency — will need `azure-ai-projects` or direct REST call
- Frontend: `foundry_project_endpoint` TextInput + `foundry_agent_name` TextInput in CreateChatAgentDialog
- Agent Service `platform.Client.GetCredentialSecret()` resolves credentials using user's auth token

**Approach:**
1. Platform Service: Add new endpoint `GET /api/v1/tenants/{tenant_id}/foundry/agents?project_endpoint={url}`
2. Platform Service: Use user's MSAL bearer token (from request header) to call Foundry REST API `{project_endpoint}/openai/agents?api-version=2025-05-01-preview` (or similar)
3. Return list of agent names/IDs
4. Frontend: Replace `foundry_agent_name` TextInput with a FilterableSelect/dropdown
5. Frontend: Fetch agents when `foundry_project_endpoint` changes (debounced)
6. User can still type a custom agent name if the API call fails

#### 4.1 Backend — Agent Discovery Endpoint

| ID | Requirement |
|----|-------------|
| 4.1.1 | Add route `GET /api/v1/tenants/{tenant_id}/foundry/agents` in `unifiedui/apis/v1/foundry.py` |
| 4.1.2 | Query params: `project_endpoint: str` (required) |
| 4.1.3 | Forward the user's MSAL bearer token from the `Authorization` header to the Foundry API call |
| 4.1.4 | Call Foundry REST API to list available agents at the given project endpoint |
| 4.1.5 | Create `FoundryAgentListResponse` schema: `{ agents: list[FoundryAgentInfo] }` with `FoundryAgentInfo` having `id: str`, `name: str` |
| 4.1.6 | Handle errors gracefully: if Foundry API fails, return empty list with warning (not 500) |
| 4.1.7 | Validate `project_endpoint` — must be HTTPS URL, prevent SSRF (no internal IPs, no localhost) |
| 4.1.8 | Route requires authentication (`@authenticate` decorator) |

#### 4.2 Frontend — Agent Name Discovery

| ID | Requirement |
|----|-------------|
| 4.2.1 | Add `getFoundryAgents(tenantId: string, projectEndpoint: string): Promise<FoundryAgentListResponse>` to API client |
| 4.2.2 | Add `FoundryAgentListResponse` and `FoundryAgentInfo` types to `src/api/types.ts` |
| 4.2.3 | Create `useFoundryAgents(tenantId: string, projectEndpoint: string)` hook — debounced fetch when `projectEndpoint` changes |
| 4.2.4 | In `CreateChatAgentDialog` + `EditChatAgentDialog`: Replace `foundry_agent_name` TextInput with a Combobox/FilterableSelect showing discovered agents |
| 4.2.5 | Dropdown shows agent names; selecting one sets the `foundry_agent_name` form value |
| 4.2.6 | Allow free-text fallback: if API fails or user wants a custom name, they can type it manually |
| 4.2.7 | Show loading indicator while fetching agents |
| 4.2.8 | Clear agent list when `project_endpoint` changes |

#### 4.3 Tests

| ID | Requirement |
|----|-------------|
| 4.3.1 | Backend: Test Foundry agent list endpoint returns agents |
| 4.3.2 | Backend: Test SSRF validation on `project_endpoint` |
| 4.3.3 | Backend: Test graceful error handling when Foundry API is unreachable |
| 4.3.4 | Frontend: Test `useFoundryAgents` hook |

---

### Package 5: N8N Workflow Browser — Platform Service + Frontend

> When configuring an n8n agent/workflow, a magnifying glass button next to the workflow endpoint field opens a browser dialog. The dialog shows a host URL input and a paginated list of workflows fetched from the n8n instance. Selecting a workflow populates the endpoint field.

**Context & Research:**
- N8N REST API: `GET {host}/api/v1/workflows` with `X-N8N-API-KEY` header, supports pagination
- Auth: API Key stored in credentials (resolved via `credential_id` from vault)
- Frontend form field: `n8n_api_api_key_credential_id` (for API key credential used for management)
- Credential must be selected before browsing workflows
- Agent Service `n8n/api_client.go` uses `X-N8N-API-KEY` header pattern

**Approach:**
1. Platform Service: Add endpoint `GET /api/v1/tenants/{tenant_id}/n8n/workflows?host={base_url}&credential_id={id}&page={n}&limit={n}`
2. Platform Service: Resolve API key from vault using `credential_id`, call n8n API with `X-N8N-API-KEY`
3. Return paginated list of workflows with name + endpoint URL
4. Frontend: Add magnifying glass icon button next to workflow endpoint field
5. Frontend: New `N8NWorkflowBrowserDialog` — host input (top), paginated workflow list (below)
6. Selecting a workflow closes dialog and sets the endpoint URL in the form

#### 5.1 Backend — N8N Workflow List Endpoint

| ID | Requirement |
|----|-------------|
| 5.1.1 | Add route `GET /api/v1/tenants/{tenant_id}/n8n/workflows` in `unifiedui/apis/v1/n8n.py` |
| 5.1.2 | Query params: `host: str` (required, n8n base URL), `credential_id: str` (required), `page: int = 1`, `limit: int = 20` |
| 5.1.3 | Resolve the API key secret from vault using `credential_id` (via existing credential handler/vault infrastructure) |
| 5.1.4 | Call n8n REST API: `GET {host}/api/v1/workflows` with `X-N8N-API-KEY: {secret}` header |
| 5.1.5 | Create `N8NWorkflowListResponse` schema: `{ workflows: list[N8NWorkflowInfo], total: int, page: int, limit: int }` with `N8NWorkflowInfo` having `id: str`, `name: str`, `active: bool`, `url: str` (constructed endpoint URL) |
| 5.1.6 | Handle errors gracefully: n8n unreachable → return empty list with warning |
| 5.1.7 | Validate `host` — must be HTTPS URL, prevent SSRF (no internal IPs, no localhost) |
| 5.1.8 | Route requires authentication + credential access permission |

#### 5.2 Frontend — Workflow Browser Dialog

| ID | Requirement |
|----|-------------|
| 5.2.1 | Add `getN8NWorkflows(tenantId, host, credentialId, page, limit): Promise<N8NWorkflowListResponse>` to API client |
| 5.2.2 | Add `N8NWorkflowListResponse` and `N8NWorkflowInfo` types to `src/api/types.ts` |
| 5.2.3 | Create `N8NWorkflowBrowserDialog` component in `src/components/dialogs/N8NWorkflowBrowserDialog/` |
| 5.2.4 | Dialog layout: Host URL input (top, with `EndpointSuggestInput` showing n8n host suggestions), paginated workflow list (below) |
| 5.2.5 | Workflow list shows: workflow name, active/inactive badge, workflow ID |
| 5.2.6 | Pagination controls at bottom |
| 5.2.7 | Selecting a workflow calls `onSelect(workflowUrl: string)` callback and closes dialog |
| 5.2.8 | Dialog requires `credentialId` prop — if not provided, show message "Please select a credential first" |

#### 5.3 Frontend — Dialog Integration

| ID | Requirement |
|----|-------------|
| 5.3.1 | Add magnifying glass icon button (🔍) next to `n8n_workflow_endpoint` field in `CreateChatAgentDialog` |
| 5.3.2 | Same for `EditChatAgentDialog`, `CreateWorkflowDialog`, `EditWorkflowDialog` |
| 5.3.3 | Button opens `N8NWorkflowBrowserDialog`; passes current `n8n_api_api_key_credential_id` from form |
| 5.3.4 | If no credential selected → button disabled with tooltip "Select an API Key credential first" |
| 5.3.5 | `onSelect` callback sets the `n8n_workflow_endpoint` form field value |

#### 5.4 Tests

| ID | Requirement |
|----|-------------|
| 5.4.1 | Backend: Test n8n workflow list endpoint returns workflows |
| 5.4.2 | Backend: Test SSRF validation on `host` parameter |
| 5.4.3 | Backend: Test credential resolution and auth header forwarding |
| 5.4.4 | Backend: Test graceful error handling when n8n is unreachable |
| 5.4.5 | Frontend: Test `N8NWorkflowBrowserDialog` renders and handles selection |

---

## Open Questions

- [ ] Foundry REST API: exact endpoint path and api-version for listing agents — needs verification against Azure AI Foundry docs
- [ ] Copilot / LangGraph platform types: do they have discoverable endpoint fields? (Not in scope for this version)

## Appendix

### Platform Type → Config Field Mapping (Suggestions)

```
n8n         → chat_url, workflow_endpoint  (NOT webhook_url — must be copied 1:1)
foundry     → project_endpoint
rest        → invoke_endpoint, create_conversation_endpoint
copilot     → (not in scope)
langgraph   → (not in scope)
```

### Platform Type → Discovery Features

```
foundry     → Agent name discovery via Foundry API (Package 4)
n8n         → Workflow browser via n8n REST API (Package 5)
```
