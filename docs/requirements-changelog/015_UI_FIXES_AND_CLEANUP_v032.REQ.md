# 015 — UI Fixes, ReACT Removal & is_active Cleanup v0.3.2

> **Status:** DRAFT
> **Scope:** unified-ui-frontend-service (primary), unified-ui-platform-service (secondary), unified-ui-agent-service (enforcement)
> **Goal:** Fix various UI/UX issues (sidebar, scrolling, menus, embed), remove all ReACT Agent & Tools code, improve External Apps iFrame configuration, and clean up `is_active` usage with backend enforcement at invoke time.

---

## Arbeitsweise & Prozess

> **Dieses Dokument ist das zentrale Tracking- und Anforderungsdokument.**
> Es gibt keine separate Implementierungsplan-Datei. Alles wird hier gesteuert.

### Ablauf pro Paket (0, 1, 2, …)

1. **Implementierungsübersicht**: Copilot liest den relevanten Code ein und erstellt eine kompakte Übersicht: welche Dateien betroffen sind, welcher Ansatz gewählt wird.
2. **Review**: Nutzer prüft die Übersicht, gibt OK oder Korrekturen.
3. **Implementierung**: Copilot implementiert das **gesamte Paket**.
4. **Testhinweise**: Copilot zeigt nach Implementierung kurz auf, was der Nutzer manuell testen soll.
5. **Test & Feedback**: Nutzer testet und gibt Anpassungswünsche.
6. **Abschluss**: Paket wird als `✅ Done` markiert → weiter zum nächsten Paket.

### Status-Tracking

- *(kein Marker)* → Noch nicht begonnen
- `⏳ In Progress` → Gerade in Bearbeitung
- `✅ Done` → Fertig implementiert und abgenommen

---

## Pakete

### Paket 0: ReACT Agents & Tools — Complete Removal

> Remove all ReACT Agent and Tools functionality from platform-service, frontend-service, and documentation. This is foundational because subsequent packages (sidebar, is_active cleanup) depend on the reduced codebase.

#### 0.1 Platform Service — Backend Removal

| ID | Requirement |
|----|-------------|
| 0.1.1 | Remove `tools` API routes (`unifiedui/apis/v1/tools.py`) and unregister from router |
| 0.1.2 | Remove `tools` handler (`unifiedui/handlers/tools.py`) and dependency (`unifiedui/handlers/dependencies/tools.py`) |
| 0.1.3 | Remove tool validator (`unifiedui/handlers/validators/tool_validator.py`) |
| 0.1.4 | Remove tool schemas: `unifiedui/schema/requests/tools.py`, `unifiedui/schema/responses/tools.py` |
| 0.1.5 | Remove tool exceptions (`unifiedui/exc/tools.py`) and ReACT agent exceptions (`unifiedui/exc/re_act_agents.py`) |
| 0.1.6 | Remove `REACT_AGENT` from `ChatAgentTypeEnum` in `core/database/enums.py` |
| 0.1.7 | Remove `REACT_AGENT_ADMIN` and `REACT_AGENT_CREATOR` from `TenantRolesEnum` in `core/database/enums.py` |
| 0.1.8 | Remove `ToolTypeEnum` from `core/database/enums.py` |
| 0.1.9 | Remove ReACT-specific fields from `CreateChatAgentRequest` / `UpdateChatAgentRequest` (system prompt, tool assignments) |
| 0.1.10 | Remove ReACT agent version endpoints from `unifiedui/apis/v1/chat_agents.py` (`/versions` routes) |
| 0.1.11 | Remove ReACT version handling logic from `unifiedui/handlers/chat_agents.py` |
| 0.1.12 | Remove ReACT-specific validation from `chat_agent_config_validator.py` |
| 0.1.13 | Create Alembic migration to drop tables: `tools`, `tool_members`, `tool_tags`, `re_act_agent_versions` |
| 0.1.14 | Remove DB models: `Tool`, `ToolMember`, `ToolTag`, `ReActAgentVersion` from `models.py` |
| 0.1.15 | Remove `tool_tags` relationship from `Tag` model |
| 0.1.16 | Remove `versions` relationship from `ChatAgent` model |
| 0.1.17 | Remove all tool/ReACT-related tests (`test_tools.py`, ReACT test cases in `test_chat_agents.py`, etc.) |
| 0.1.18 | Update instruction files: remove ReACT/Tools mentions from `auth-permissions.instructions.md`, `database.instructions.md`, `project-structure.instructions.md` |

#### 0.2 Frontend Service — UI Removal

| ID | Requirement |
|----|-------------|
| 0.2.1 | Remove `ReActAgentDeveloperPage` and all sub-components from `src/pages/ReActAgentDeveloperPage/` |
| 0.2.2 | Remove ReACT-related dialogs: `CreateToolDialog/`, `EditToolDialog/` |
| 0.2.3 | Remove ReACT sidebar navigation item (`REACT_AGENT` entry and feature flag `VITE_SHOW_RE_ACT_AGENT_DEVELOPMENT_PAGE`) |
| 0.2.4 | Remove route for `/chat-agents/:agentId/develop` from `src/routes/index.tsx` |
| 0.2.5 | Remove `REACT_AGENT` from `ChatAgentTypeEnum` in `src/api/types.ts` |
| 0.2.6 | Remove `REACT_AGENT_ADMIN` role references from `src/api/types.ts` |
| 0.2.7 | Remove tool-related types (`ToolResponse`, `CreateToolRequest`, `ToolTypeEnum`, etc.) from `src/api/types.ts` |
| 0.2.8 | Remove `UpdateReActAgentVersionRequest`, `ReActAgentVersionResponse` types from `src/api/types.ts` |
| 0.2.9 | Remove tool/ReACT API client methods (`listTools`, `getTool`, `createTool`, `updateTool`, version endpoints) from `src/api/client.ts` |
| 0.2.10 | Remove i18n files: `src/i18n/locales/en-US/reactAgent.json` and `src/i18n/locales/de-DE/reactAgent.json` |
| 0.2.11 | Remove `reactAgent` namespace registration from i18n config |
| 0.2.12 | Remove ReACT-related sidebar label from `sidebar.json` locales |
| 0.2.13 | Clean up any remaining `REACT_AGENT` type checks in `ChatAgentsPage.tsx` (e.g., conditional navigation to develop page) |
| 0.2.14 | Remove "Tools" tab from Admin Settings page (`/admin/settings`) |
| 0.2.15 | Update frontend instruction files: remove ReACT/Tools mentions |

---

### Paket 1: Sidebar Fixes

> Fix data sidebar link targets and remove the redundant "Settings" item from the sidebar.

#### 1.1 Data Sidebar Links

| ID | Requirement |
|----|-------------|
| 1.1.1 | Change chat-agents `getLink` in `Sidebar.tsx` from `/conversations?chat-agent=${id}` to `/chat-agents/${id}` — the hover data sidebar should navigate to the agent detail page, not open a chat |

#### 1.2 Settings Item Removal

| ID | Requirement |
|----|-------------|
| 1.2.1 | Remove "Settings" (`/user/settings`) from the sidebar bottom section — it already exists in the user dropdown (Header.tsx "My Settings") |
| 1.2.2 | "Admin" button becomes the only bottom sidebar item |

**Context:**
- Sidebar items defined in: `src/components/layout/Sidebar/Sidebar.tsx`
- Settings already in user dropdown: `src/components/layout/Header/Header.tsx`

---

### Paket 2: Chat Agents List & Detail Page Fixes

> Add missing menu actions, consolidate embed functionality, fix UI issues on chat agent pages.

#### 2.1 Chat Agents List Page (`/chat-agents/`) — 3-Dots Menu

| ID | Requirement |
|----|-------------|
| 2.1.1 | Add "Open Chat" menu item (positioned below "Open") — navigates to `/conversations?agent={id}&selected={id}` (same target as the "Chat with Agent" button on the detail page) |
| 2.1.2 | "Embed Agent" menu item should navigate to `/chat-agents/{id}?tab=embed` (the embed tab on the detail page, see 2.2.1) |

#### 2.2 Chat Agent Detail Page (`/chat-agents/{id}`) — Embed Tab Consolidation

| ID | Requirement |
|----|-------------|
| 2.2.1 | Move ALL content from `HowEmbedChatPage` (`/chat-agents/{id}/embed-chat`) into the "Embed" tab on the detail page: Base URL config, Tenant ID, Theme selector, Language, Dimensions, Context Parameters (`ctx_` params), Embed Code (iframe snippet), Allowed Origins, Preview button with live preview |
| 2.2.2 | Remove the route for `/chat-agents/:id/embed-chat` from routes |
| 2.2.3 | Remove `HowEmbedChatPage` component and all sub-components |
| 2.2.4 | Update any navigation links that previously pointed to `/chat-agents/{id}/embed-chat` to navigate to `/chat-agents/{id}?tab=embed` instead |

#### 2.3 Chat Agent Detail Page — UI Cleanup

| ID | Requirement |
|----|-------------|
| 2.3.1 | Remove "Manage Access" button (`IconShieldLock`) from the detail page header — access management is done via the list page menu or edit dialog |
| 2.3.2 | Fix missing icon in Overview tab info header — the `EntityAvatar` with `entityType="chat-agent"` shows an empty square with colors instead of an actual icon |

**Context:**
- List page: `src/pages/ChatAgentsPage/ChatAgentsPage.tsx`
- Detail page: `src/pages/ChatAgentDetailsPage/ChatAgentDetailsPage.tsx`
- Embed page to remove: `src/pages/HowEmbedChatPage/HowEmbedChatPage.tsx`

---

### Paket 3: Workflow Detail Page — Dynamic Host URL

> Replace hardcoded `{YOUR-AGENT-SERVICE-HOST}` placeholder with actual agent service host from environment config.

#### 3.1 Endpoint URL Resolution

| ID | Requirement |
|----|-------------|
| 3.1.1 | In `WorkflowDetailsPage.tsx`: Replace `{YOUR-AGENT-SERVICE-HOST}` with the actual agent service host URL from environment variables (e.g., `VITE_AGENT_SERVICE_URL` or equivalent) |
| 3.1.2 | In `IntegrationDialog.tsx`: Same replacement — use the actual agent service host URL |

**Context:**
- `{YOUR-AGENT-SERVICE-HOST}` is currently hardcoded as a string constant in both files
- The host should come from env config (check `src/config/` or `.env` for existing agent service URL variables)

---

### Paket 4: Admin Pages — Scroll Behavior

> Fix scrolling on admin dashboard and admin settings pages so that headers/filters stay fixed and only content areas scroll. **Note:** Read the existing scroll behavior instructions (`ui-patterns.instructions.md`) before implementing.

#### 4.1 Admin Dashboard (`/admin`)

| ID | Requirement |
|----|-------------|
| 4.1.1 | "Analytics" title, agent filter (`MultiSelect`), and date range filter must be sticky at the top of the page content area |
| 4.1.2 | Only the content below (KPI cards, feedback insights, statistics tables) should be scrollable in a dedicated scrollable container |

#### 4.2 Admin Settings (`/admin/settings`)

| ID | Requirement |
|----|-------------|
| 4.2.1 | Tab bar must remain sticky at the top of the content area |
| 4.2.2 | Within each tab, only the table/list content should scroll — the tab header and any section titles above the table should remain fixed |

**Context:**
- Dashboard: `src/pages/AdminAnalyticsPage/AdminAnalyticsPage.tsx`
- Settings: `src/pages/TenantSettingsPage/TenantSettingsPage.tsx`
- Layout: `AdminLayout.tsx` → `MainLayout.module.css` (`.content` with `overflow-y: auto`)
- **Read before implementing:** `ui-patterns.instructions.md` (scroll behavior patterns)

---

### Paket 5: External Apps — iFrame Configuration ✅ Done

> Improve External Apps with a `config` JSON column (replacing the dedicated `url` column), two embedding modes (URL+params vs. raw iFrame HTML), and a backend config validator.

#### 5.1 Backend — Model & Migration

| ID | Requirement |
|----|-------------|
| 5.1.1 | Add `config` column (`PortableJSON`, non-nullable, default `{}`) to `ExternalApp` model — stores all iFrame configuration |
| 5.1.2 | Remove `url` column from `ExternalApp` model — URL moves into `config` |
| 5.1.3 | Create Alembic migration: add `config` column, migrate existing `url` values into `config` JSON (`{"mode": "url", "url": "<old-url>", "params": {}}`), then drop `url` column |
| 5.1.4 | Update request/response schemas: replace `url: str` with `config: dict` in `CreateExternalAppRequest`, `UpdateExternalAppRequest`, `ExternalAppResponse` |

#### 5.2 Backend — Config Validator

| ID | Requirement |
|----|-------------|
| 5.2.1 | Create `ExternalAppConfigValidatorFactory` in `unifiedui/handlers/validators/external_app_config_validator.py` (following the existing `ChatAgentConfigValidatorFactory` pattern) |
| 5.2.2 | **Mode `url`** (URL + params): Validate that `config.url` is a non-empty valid URL (max 2000 chars). `config.params` is an optional dict of string key-value pairs (query parameters). Generated iFrame URL = `url + ?key1=value1&key2=value2` |
| 5.2.3 | **Mode `iframe`** (raw HTML): Validate that `config.iframe_html` is a non-empty string containing a valid `<iframe>` tag. Sanitize to prevent XSS — only allow `<iframe>` elements with safe attributes (`src`, `width`, `height`, `title`, `sandbox`, `allow`, `referrerpolicy`, `loading`, `style`). Reject any `<script>`, event handlers (`onload`, `onerror`, etc.), or `javascript:` URLs |
| 5.2.4 | Validate `config.mode` is either `"url"` or `"iframe"` — reject unknown modes |
| 5.2.5 | Call the validator in the External App handler on create and update |

#### 5.3 Frontend — Create/Edit Dialog

| ID | Requirement |
|----|-------------|
| 5.3.1 | Add mode toggle in create/edit dialog: "URL" mode (default) vs. "Custom iFrame" mode |
| 5.3.2 | **URL mode**: Show URL input (required) + dynamic key-value list for query parameters (add/remove rows). Live iFrame preview below using the assembled URL |
| 5.3.3 | **Custom iFrame mode**: Show a textarea/code input where users paste a complete `<iframe>` HTML tag. Live preview renders the pasted HTML |
| 5.3.4 | Update form submission to send `config` object instead of `url` string |

#### 5.4 Frontend — View Page

| ID | Requirement |
|----|-------------|
| 5.4.1 | Update `ExternalAppPage` to read from `config` instead of `url` |
| 5.4.2 | **URL mode**: Render iFrame with assembled URL (base URL + query params) |
| 5.4.3 | **Custom iFrame mode**: Render the stored iFrame HTML (sanitized on backend, displayed via `dangerouslySetInnerHTML` or safe HTML parser) |

**Context:**
- Create dialog: `src/components/dialogs/CreateExternalAppDialog.tsx`
- Edit dialog: `src/components/dialogs/EditExternalAppDialog/EditExternalAppDialog.tsx`
- View page (iFrame rendering): `src/pages/ExternalAppPage/ExternalAppPage.tsx`
- Backend model: `ExternalApp` in `models.py` — currently has `url` (required), `image_url`, `image_file_id` but no `config` JSON column
- Validator pattern: `unifiedui/handlers/validators/chat_agent_config_validator.py`
- Config schema example: `{"mode": "url", "url": "https://app.example.com", "params": {"theme": "dark", "lang": "en"}}` or `{"mode": "iframe", "iframe_html": "<iframe src=\"...\" ...></iframe>"}`

---

### Paket 6: FilterableSelect (Dropdown with Search) — Alignment Fix ✅ Done

> Fix the search input alignment in the searchable dropdown component.

#### 6.1 Search Box Alignment

| ID | Requirement |
|----|-------------|
| 6.1.1 | Fix the search input position in `FilterableSelect` — the search box is slightly too far left. Adjust padding/margin to align it properly within the dropdown (see attached screenshot) |

**Context:**
- Component: `src/components/common/FilterableSelect/FilterableSelect.tsx`
- Uses Mantine's `Combobox.Search` inside the dropdown

---

### Paket 7: Default `is_active` & Active State Enforcement

> Clean up `is_active` usage: remove it from entities where it's unnecessary, change defaults, and add backend enforcement for agents and credentials at invoke time.

#### 7.1 Remove `is_active` from Non-Essential Entities

Entities that should **keep** `is_active`: `ChatAgent`, `Credential`, `Principal` (users)
Entities that should **lose** `is_active` (field removal + migration): `Workflow`, `ChatWidget`, `Conversation`, `TenantAIModel`
Entities that **already don't have it**: `ExternalApp`
Entities **not touched** (infrastructure): `Organization`
Entities **removed in Paket 0**: `Tool`

| ID | Requirement |
|----|-------------|
| 7.1.1 | Remove `is_active` column from `Workflow` model — all workflows are always active |
| 7.1.2 | Remove `is_active` column from `ChatWidget` model — all chat widgets are always active |
| 7.1.3 | Remove `is_active` column from `Conversation` model — conversations don't need an active toggle |
| 7.1.4 | Remove `is_active` column from `TenantAIModel` model — all AI models are always active |
| 7.1.5 | Create Alembic migration to drop `is_active` from `workflows`, `chat_widgets`, `conversations`, `tenant_ai_models` tables |
| 7.1.6 | Remove `is_active` from request/response schemas for Workflow, ChatWidget, Conversation, TenantAIModel |
| 7.1.7 | Remove `is_active` toggle from frontend list pages and create/edit dialogs for Workflow, ChatWidget, Conversation, TenantAIModel |
| 7.1.8 | Remove any `is_active` filter logic in handlers for these entities |

#### 7.2 Default Active for ChatAgent & Credential

| ID | Requirement |
|----|-------------|
| 7.2.1 | Change `ChatAgent.is_active` default from `False` to `True` in the model |
| 7.2.2 | Change `Credential.is_active` default from `False` to `True` in the model |
| 7.2.3 | Create Alembic migration for default value changes |

#### 7.3 Backend Enforcement — Active State Checks (Agent Service, Go)

| ID | Requirement |
|----|-------------|
| 7.3.1 | When a user invokes an inactive agent (`is_active=False`): return HTTP 422 with clear error message ("Agent is currently inactive and cannot be used for conversations") — check at invoke time in the agent-service (Go) |
| 7.3.2 | When an agent invoke requires a credential that is inactive (`credential.is_active=False`): return HTTP 422 with clear error message ("The credential '{name}' required by this agent is currently inactive") |
| 7.3.3 | When a credential is fetched for operational use (not just for listing/viewing) and it is inactive: return HTTP 422 with clear error message |
| 7.3.4 | These checks happen in the **agent-service** (Go) at invoke time — an agent can be deactivated during an ongoing conversation, and the next invoke must fail |

**Context:**
- Current `is_active` exists on: `Organization`, `Principal`, `ChatAgent`, `Conversation`, `Workflow`, `Credential`, `ChatWidget`, `TenantAIModel`
- `ChatAgent` and `Credential` currently default to `is_active=False`
- No backend enforcement currently exists — `is_active` is only used for UI display
- Enforcement scope: `unified-ui-agent-service` (Go) — the invoke handler must check active state before forwarding to the AI backend

---

### Paket 8: Notification Drawer — Rich Error Details

> Notifications currently show only a generic title `"Error"` and the raw `error.message` (e.g. `"Failed to fetch"`). Users need more context — at minimum the HTTP status, server-provided `detail`, and ideally the full server JSON response (collapsible).

#### 8.1 Analysis (Current State)

**API client** (`src/api/client.ts`):
- Throws `new Error(errorData.detail || \`HTTP ${response.status}: ${response.statusText}\`)` (~5 occurrences)
- Loses everything except `detail` (no status code, no raw body, no validation errors array)
- Network failures throw native `TypeError: Failed to fetch` — no extra context available
- Two response shapes in the wild:
  - Platform-service: `{"detail": "message"}` or `{"detail": [{"loc":..., "msg":..., "type":...}]}` (FastAPI validation)
  - Agent-service: `{"message": "..."}` (Go domain errors)

**Notification flow** (`src/contexts/IdentityContext.tsx` → `onError` ~L65-75):
- Title is hardcoded `t('error')` → "Error" / "Fehler"
- Message is `error.message` only
- No raw payload is attached → `NotificationEntry` has no `details` / `rawJson` field

**Notification storage** (`src/contexts/NotificationContext.tsx`):
- `NotificationEntry`: `{ id, title, message, color, timestamp, read }` — no detail/raw fields
- Persisted to localStorage

**Notification UI** (`src/components/common/NotificationDrawer/NotificationDrawer.tsx`):
- Renders title + message + relative time
- No expand/collapse, no JSON viewer

#### 8.2 Proposed Solution

**New `ApiError` class** in `src/api/errors.ts` (or extend existing):

```ts
export class ApiError extends Error {
  constructor(
    public readonly status: number,        // 0 for network errors
    public readonly statusText: string,    // e.g. "Bad Request", "Network Error"
    message: string,                       // primary user-facing detail
    public readonly detail?: string,       // server `detail` / `message` (short)
    public readonly raw?: unknown,         // full parsed JSON body (if any)
    public readonly url?: string,          // request URL for context
    public readonly method?: string,       // HTTP method
  ) { super(message); this.name = 'ApiError'; }
}
```

**API client** — wrap all `throw new Error(...)` with `ApiError`:
- Extract `detail` (platform) or `message` (agent)
- Attach full parsed JSON as `raw`
- Wrap `TypeError: Failed to fetch` in `ApiError(0, 'Network Error', ...)`
- Wrap unexpected exceptions in `ApiError(0, 'Unexpected Error', ...)`

**`NotificationEntry`** — extend with optional fields:

```ts
export interface NotificationEntry {
  id: string;
  title: string;
  message: string;
  color: string;
  timestamp: number;
  read: boolean;
  status?: number;        // HTTP status (for API errors)
  url?: string;           // request URL (for API errors)
  method?: string;        // HTTP method
  rawJson?: unknown;      // server response body (for collapsible viewer)
}
```

**`onError` in IdentityContext** — derive better title/message:
- Title: `${error.status} ${error.statusText}` for ApiError with status (e.g. `"404 Not Found"`, `"Network Error"`)
- Message: `error.detail || error.message`
- Pass `status`, `url`, `method`, `rawJson` through to `addNotification`

**NotificationDrawer UI changes:**
- Show new compact secondary line: `${method} ${url}` (dimmed, monospace) when present
- When `rawJson` present, render a Mantine `Spoiler` or `Accordion` with `<pre>{JSON.stringify(rawJson, null, 2)}</pre>`
- Add a copy-to-clipboard button on the raw JSON block
- Keep existing close-button + read state behavior

**Toast (`notifications.show`)** — keep concise (title + message only). Rich JSON only in the drawer.

#### 8.3 Requirements

| ID    | Requirement |
|-------|-------------|
| 8.1.1 | Create `ApiError` class in `src/api/errors.ts` with fields: `status`, `statusText`, `message`, `detail`, `raw`, `url`, `method` |
| 8.1.2 | `client.ts`: replace all `throw new Error(errorData.detail ...)` with `throw new ApiError(...)`, parsing both `detail` (platform) and `message` (agent) shapes |
| 8.1.3 | `client.ts`: wrap network errors (`TypeError: Failed to fetch`) and unexpected exceptions in `ApiError(0, 'Network Error', ...)` / `ApiError(0, 'Unexpected Error', ...)` |
| 8.2.1 | Extend `NotificationEntry` interface with optional `status`, `url`, `method`, `rawJson` |
| 8.2.2 | `IdentityContext.onError`: when `error instanceof ApiError`, set title to `${status} ${statusText}` (or `statusText` when status=0), message to `detail \|\| message`, attach `status` + `url` + `method` + `rawJson` |
| 8.2.3 | `IdentityContext.onError`: keep existing PermissionError branch unchanged |
| 8.3.1 | `NotificationDrawer`: render `${method} ${url}` as dimmed monospace line below message when present |
| 8.3.2 | `NotificationDrawer`: when `rawJson` is present, render a Mantine `Spoiler` (or `Accordion.Item`) labeled `t('notifications.showDetails')` containing `<pre>` with formatted JSON |
| 8.3.3 | `NotificationDrawer`: add copy-to-clipboard button next to the raw JSON block |
| 8.4.1 | i18n keys (en-US + de-DE): `notifications.showDetails`, `notifications.hideDetails`, `notifications.copyDetails`, `notifications.networkError`, `notifications.unexpectedError` |
| 8.5.1 | Existing toast (`notifications.show`) remains short — only title + message, no JSON in toast |
| 8.6.1 | Backwards-compat: `NotificationEntry` records from localStorage without new fields render exactly as before |

#### 8.4 Scope Clarifications

- **Success / Info notifications stay unchanged** — they already render well (verified visually). Paket 8 enriches **error** notifications only.
- The new collapsible JSON block uses the **same styling** as the existing notification cards (Mantine tokens, dark-mode aware, monospace `<pre>` with `var(--mantine-color-dark-6)` background).
- `rawJson` field is only populated for `ApiError` instances — non-error notifications (success, info) leave it `undefined` and the Spoiler is not rendered.

#### 8.5 Out of Scope

- Standardising the backend error response shape (platform uses `detail`, agent uses `message`) — handled in a separate REQ if desired
- Stack traces in production builds
- Server-side error tracking / Sentry integration

---

## Anhang

### Entities with `is_active` (Current State)

| Entity | Has `is_active` | Default | After Cleanup |
|--------|----------------|---------|---------------|
| Organization | Yes | `True` | Keep (infrastructure) |
| Principal | Yes | `True` | Keep (users need active toggle) |
| ChatAgent | Yes | `False` | **Keep, change default to `True`, add enforcement at invoke** |
| Credential | Yes | `False` | **Keep, change default to `True`, add enforcement at invoke** |
| Workflow | Yes | `False` | **Remove** |
| ChatWidget | Yes | `False` | **Remove** |
| Conversation | Yes | `False` | **Remove** |
| TenantAIModel | Yes | `False` | **Remove** |
| Tool | Yes | `False` | Removed with ReACT (Paket 0) |
| ExternalApp | No | — | No change |

### Affected Files (Key References)

**Frontend:**
- Sidebar: `src/components/layout/Sidebar/Sidebar.tsx`
- Header: `src/components/layout/Header/Header.tsx`
- Chat Agents List: `src/pages/ChatAgentsPage/ChatAgentsPage.tsx`
- Chat Agent Detail: `src/pages/ChatAgentDetailsPage/ChatAgentDetailsPage.tsx`
- Embed Page (to remove): `src/pages/HowEmbedChatPage/HowEmbedChatPage.tsx`
- Workflow Detail: `src/pages/WorkflowDetailsPage/WorkflowDetailsPage.tsx`
- Integration Dialog: `src/components/dialogs/IntegrationDialog/IntegrationDialog.tsx`
- Admin Dashboard: `src/pages/AdminAnalyticsPage/AdminAnalyticsPage.tsx`
- Admin Settings: `src/pages/TenantSettingsPage/TenantSettingsPage.tsx`
- FilterableSelect: `src/components/common/FilterableSelect/FilterableSelect.tsx`
- External App Create Dialog: `src/components/dialogs/CreateExternalAppDialog.tsx`
- External App Edit Dialog: `src/components/dialogs/EditExternalAppDialog/EditExternalAppDialog.tsx`
- External App View: `src/pages/ExternalAppPage/ExternalAppPage.tsx`

**Platform Service:**
- Models: `unifiedui/core/database/models.py`
- Enums: `unifiedui/core/database/enums.py`
- Tools API: `unifiedui/apis/v1/tools.py`
- Chat Agents API: `unifiedui/apis/v1/chat_agents.py`
- Tools Handler: `unifiedui/handlers/tools.py`
- Chat Agents Handler: `unifiedui/handlers/chat_agents.py`

**Agent Service (Go):**
- Invoke handler (active state enforcement): `internal/api/handlers/` (agent invoke logic)
