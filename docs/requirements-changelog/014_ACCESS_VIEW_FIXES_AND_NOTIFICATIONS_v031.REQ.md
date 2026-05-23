# 014 — Access View Fixes, Role Rename & Notification Center v0.3.1

> **Status:** DRAFT
> **Scope:** unified-ui-frontend-service (primary), unified-ui-platform-service (minor)
> **Goal:** Fix remaining RBAC gaps found during REQ 013 testing, rename deprecated `AUTONOMOUS_AGENTS_*` roles to `WORKFLOWS_*`, improve 403 toast handling for explicit actions, and add a notification center for reviewing past notifications.

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

## Findings from REQ 013 Testing

| # | Finding | Severity |
|---|---------|----------|
| F1 | **ChatAgentDetailsPage**: "Manage Access" + "Edit" buttons visible for READ users | High |
| F2 | **WorkflowDetailsPage**: "Edit" button visible for READ users | High |
| F3 | **WorkflowDetailsPage**: `workflow-runs` endpoint 403 silently swallowed → infinite loader | Medium |
| F4 | **Explicit action 403 (e.g. create conversation) shows no toast** — `PermissionError` globally suppressed, but REQ 013 §0.2.4 required toasts for user-initiated actions | High |
| F5 | **Role enum mismatch**: Backend renamed `AUTONOMOUS_AGENTS_*` → `WORKFLOWS_*`, frontend still uses old names → permission checks broken | Critical |
| F6 | **Conversation search**: User reports seeing other users' conversations in search — backend filters by membership (including group membership). READER user likely sees conversations where their identity group or custom group is a member. **Probably correct behavior** — verify with user | Low |
| F7 | **Notification Center**: User wants a sidebar/panel to review and clear past notifications (toast history) | Feature |

---

## Pakete

### Paket 0: Role Enum Rename — `AUTONOMOUS_AGENTS_*` → `WORKFLOWS_*`

> **Critical foundation** — must be done first. All permission checks for workflows are currently broken because frontend sends `AUTONOMOUS_AGENTS_ADMIN`/`AUTONOMOUS_AGENTS_CREATOR` but backend expects `WORKFLOWS_ADMIN`/`WORKFLOWS_CREATOR`.

#### 0.1 Frontend Enum Rename

| ID | Anforderung |
|----|-------------|
| 0.1.1 | In `src/api/types.ts`: Rename `TenantPermissionEnum.AUTONOMOUS_AGENTS_ADMIN` → `WORKFLOWS_ADMIN` (value: `"WORKFLOWS_ADMIN"`) and `AUTONOMOUS_AGENTS_CREATOR` → `WORKFLOWS_CREATOR` (value: `"WORKFLOWS_CREATOR"`) |
| 0.1.2 | In `src/hooks/usePermissions.ts`: Update `CREATOR_ROLES` and `ADMIN_ROLES` maps to use the new enum values |
| 0.1.3 | Search all usages of `AUTONOMOUS_AGENTS_ADMIN` / `AUTONOMOUS_AGENTS_CREATOR` across the frontend and update to `WORKFLOWS_ADMIN` / `WORKFLOWS_CREATOR` |
| 0.1.4 | Verify `AccessDeniedBanner` `ROLE_DISPLAY_NAMES` map includes the new role names with correct display labels |

#### 0.2 Backend Verification

| ID | Anforderung |
|----|-------------|
| 0.2.1 | Verify backend `TenantRolesEnum` already uses `WORKFLOWS_ADMIN` / `WORKFLOWS_CREATOR` ✓ (confirmed) |
| 0.2.2 | Verify existing database entries: Alembic migration was already done for the rename ✓ (confirmed by user) |

---

### Paket 1: Detail Page Button Gating (ChatAgent + Workflow)

> Fix the missing permission checks on detail page action buttons. READ users should not see Edit or Manage Access buttons.

**Context & Research:**
- `ChatAgentDetailsPage`: Agent is fetched into `agent` state, which includes `my_permission` field from backend
- `WorkflowDetailsPage`: Same — `agent` state includes `my_permission`
- `usePermissions` hook provides `canWrite(permission)` and `canAdmin(permission)` helpers
- Pattern from REQ 013: Use `my_permission` to gate UI — WRITE+ for edit, ADMIN for manage access

#### 1.1 ChatAgentDetailsPage

| ID | Anforderung |
|----|-------------|
| 1.1.1 | **Edit button** (pencil icon): Only show when `agent.my_permission === 'ADMIN' \|\| agent.my_permission === 'WRITE'` (or equivalently `canWrite(agent.my_permission)`) |
| 1.1.2 | **"Manage Access" button**: Only show when `agent.my_permission === 'ADMIN'` (or `canAdmin(agent.my_permission)`) |
| 1.1.3 | **"Chat with Agent" button**: Always visible (READ users can chat) |

#### 1.2 WorkflowDetailsPage

| ID | Anforderung |
|----|-------------|
| 1.2.1 | **Edit button** (pencil icon): Only show when `agent.my_permission === 'ADMIN' \|\| agent.my_permission === 'WRITE'` |
| 1.2.2 | If "Manage Access" button exists (or similar): Only show for ADMIN |
| 1.2.3 | **Workflow Runs tab**: Handle 403 from `listWorkflowRuns` endpoint — catch `PermissionError`, show `AccessDeniedBanner` instead of infinite loader |

---

### Paket 2: Explicit Action 403 Toasts

> REQ 013 §0.2.4 was not implemented: explicit user actions (create, update, delete) that fail with 403 should still show a toast notification. Currently ALL 403s are globally suppressed.

**Problem:** In `IdentityContext.tsx`, `onError` skips all `PermissionError` instances. This means:
- Page-load 403 → correctly suppressed ✓
- User clicks "Create Conversation" → 403 → **silently fails** ✗

**Solution approach:** The `PermissionError` class needs a way to distinguish "passive" (page-load) from "active" (user-action) contexts. Options:

#### 2.1 Approach: `silent` flag on PermissionError

| ID | Anforderung |
|----|-------------|
| 2.1.1 | Add a `silent: boolean` field to `PermissionError` class. Default: `true` (suppress toast). When a caller wants the toast to fire, set `silent: false` |
| 2.1.2 | In `IdentityContext.tsx` `onError`: Only suppress if `error instanceof PermissionError && error.silent`. When `!error.silent`, show orange toast with user-friendly message: "No permission for this action. Required roles: {roles}" |
| 2.1.3 | In `client.ts` `request()`: When constructing the `PermissionError`, default `silent = true`. Provide a way for individual API calls to opt into `silent: false` |
| 2.1.4 | All **mutation methods** (create, update, delete) in `client.ts` should pass `silent: false` on the request options so that 403 toasts fire for user-initiated actions |

**Decision: Option A** — Use HTTP method to determine default: GET → `silent: true`, POST/PUT/PATCH/DELETE → `silent: false`. This is systematic and requires no per-call changes.

#### 2.2 Toast Message Quality

| ID | Anforderung |
|----|-------------|
| 2.2.1 | When a 403 toast DOES fire (explicit action), show: Title: "Permission denied" / Message: "You do not have the required permissions." + list required roles if available |
| 2.2.2 | Add i18n keys for `permissionDenied.actionTitle` and `permissionDenied.actionMessage` in both `en-US` and `de-DE` |

---

### Paket 3: WorkflowRunsTable 403 Handling

> When a READ user views a workflow detail page, the `listWorkflowRuns` endpoint returns 403. Currently this is silently caught → shows empty/loading state forever.

| ID | Anforderung |
|----|-------------|
| 3.1.1 | In `WorkflowRunsTable.tsx`: Catch `PermissionError` in the fetch callback and store in state |
| 3.1.2 | When `permissionError` is set, render `AccessDeniedBanner` instead of the runs table/empty state |
| 3.1.3 | Ensure no toast fires for this (passive page-load → already suppressed) |

---

### Paket 4: Conversation Search Verification

> User reported seeing other users' conversations in search. Backend already filters by membership. Need to verify and clarify behavior.

| ID | Anforderung |
|----|-------------|
| 4.1.1 | **Verify**: Backend `list_conversations` handler filters by `ConversationMember` for non-admin users, even when `name_filter` is applied ✓ (confirmed in code) |
| 4.1.2 | **Clarify UX**: If the user is a member of conversations created by others (e.g. shared conversations), those correctly appear in search. This is expected behavior — the user is a member |
| 4.1.3 | **Test**: As a non-admin user, search for a conversation that exists but the user is NOT a member of → should return empty results |
| 4.1.4 | **If bug confirmed**: Investigate whether the frontend's `listConversations` call passes incorrect parameters or the backend membership filter has a gap |

---

### Paket 5: Notification Center (New Feature)

> User wants a sidebar/panel to review and clear past notifications — a notification history. Currently, toasts disappear after a few seconds and are lost.

#### 5.1 Notification Store

| ID | Anforderung |
|----|-------------|
| 5.1.1 | Create a `NotificationContext` / `useNotificationStore` that stores notification history in `localStorage` (persisted across page reloads) |
| 5.1.2 | Each notification entry: `{ id, title, message, color, timestamp, read }` |
| 5.1.3 | Wire the existing `onError` / `onSuccess` callbacks to push entries to the store in addition to showing toasts |
| 5.1.4 | Cap history at 100 entries (FIFO — oldest removed when limit exceeded) |

#### 5.2 Notification Sidebar/Panel

| ID | Anforderung |
|----|-------------|
| 5.2.1 | Add a bell icon (🔔) in the header bar (next to user avatar / settings) |
| 5.2.2 | Badge on bell icon showing count of unread notifications |
| 5.2.3 | Clicking bell opens a slide-in sidebar panel (right side, Mantine `Drawer`, not too wide ~380px, standard slide animation) |
| 5.2.4 | Panel shows list of notifications, newest first, with timestamp, title, message, color indicator |
| 5.2.5 | "Mark all as read" button |
| 5.2.6 | "Clear all" button to empty the history |
| 5.2.7 | Individual notification can be dismissed |

#### 5.3 Design Considerations

| ID | Anforderung |
|----|-------------|
| 5.3.1 | Notifications ARE persisted across page reloads via `localStorage`. Scoped by tenant (key: `unifiedui_notifications_{tenantId}`) |
| 5.3.2 | Style: Use CSS variables, support dark mode |
| 5.3.3 | i18n: Add keys for "Notifications", "Mark all as read", "Clear all", "No notifications" in en-US and de-DE |

---

## Open Questions

- [x] **Paket 0**: DB migration already done ✓
- [x] **Paket 2**: Option A — silent flag based on HTTP method ✓
- [ ] **Paket 4**: User sees foreign conversations as READER — likely via group membership. Backend filters correctly. Verify: are those conversations shared via identity/custom group membership?  
- [x] **Paket 5**: Right-side drawer, ~380px wide, standard slide animation, bell icon in header ✓

---

## Anhang

### Referenzen

- [REQ 013 — Frontend Access View Pattern](013_FRONTEND_ACCESS_VIEW_PATTERN_v030.REQ.md) (predecessor)
- [Issue #46 — Refactor frontend access view](https://github.com/unified-ui/unifiedui/issues/46)
- [Issue #11 — Error notifications only after unauthorized action](https://github.com/unified-ui/unifiedui/issues/11)
