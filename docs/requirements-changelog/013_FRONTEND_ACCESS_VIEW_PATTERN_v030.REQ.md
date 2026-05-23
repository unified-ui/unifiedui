# 013 — Frontend Access View Pattern v0.3.0

> **Status:** ✅ DONE  
> **Scope:** unified-ui-frontend-service (primary), unified-ui-platform-service (minor)  
> **Ziel:** Implement a consistent, user-friendly RBAC-based access pattern across the frontend — hide actions users can't perform, show informative permission banners instead of generic errors, and eliminate noisy 403 toast notifications on passive navigation.

---

## Arbeitsweise & Prozess

> **Dieses Dokument ist das zentrale Tracking- und Anforderungsdokument.**  
> Es gibt keine separate Implementierungsplan-Datei. Alles wird hier gesteuert.

### Ablauf pro Paket (0, 1, 2, …)

1. **Implementierungsübersicht**: Copilot liest den relevanten Code ein und erstellt eine kompakte Übersicht: welche Dateien betroffen sind, welcher Ansatz gewählt wird, bei Design-Paketen konkrete Varianten mit Empfehlung.
2. **Review**: Nutzer prüft die Übersicht, gibt OK oder Korrekturen.
3. **Implementierung**: Copilot implementiert das **gesamte Paket** (alle Teilpakete zusammen, nicht einzeln).
4. **Testhinweise**: Copilot zeigt nach Implementierung kurz auf, was der Nutzer manuell testen soll (Stichpunkte).
5. **Test & Feedback**: Nutzer testet die Implementierung und gibt Anpassungswünsche.
6. **Abschluss**: Paket wird als `✅ Done` im Titel markiert → weiter zum nächsten Paket.

### Status-Tracking

Jedes Paket bekommt einen Status-Marker im Titel:
- *(kein Marker)* → Noch nicht begonnen
- `⏳ In Progress` → Gerade in Bearbeitung
- `✅ Done` → Fertig implementiert und abgenommen

### Regeln

- Immer ein **komplettes Paket** als Einheit bearbeiten (nicht Teilpakete einzeln).
- Bei Design-Entscheidungen werden konkrete Optionen mit CSS-Beispielen gezeigt → Nutzer wählt vor der Implementierung.
- Dieses Dokument kann in jeder neuen Session als Kontext geladen werden, um den aktuellen Stand und nächsten Schritt zu kennen.
- Backend-Änderungen werden im selben Paket miterledigt, wenn das Paket Backend-Anforderungen enthält.
- Nach **jedem Paket**: `pre-commit run --all-files` ausführen und alle Fehler fixen.

---

## Current State Analysis

### What Works

| Area | Status |
|------|--------|
| `usePermissions` hook | Solid — covers all resource types, org bypass, global admin |
| Sidebar filtering | Create buttons hidden via `canCreate()`, admin link hidden for non-admins |
| Settings create buttons | Properly gated per-tab via `canCreate()` / `isGlobalAdmin` |
| IAM tab visibility | Hidden from tab list for non-admins |
| Admin Analytics route | Protected via `AdminProtectedRoute` → redirect to `/unauthorized` |
| Instance-level permissions | `my_permission` field on resources used for edit/delete buttons |
| `PermissionGate` component | Exists with hide/disable modes — but **unused in production** |

### Gaps Found

| # | Gap | Impact |
|---|-----|--------|
| G1 | **No 403 differentiation in API client** — 403s show the same red toast as any error | Users see cryptic "Access denied: User does not have required permissions..." toasts |
| G2 | **403 toasts fire on page load** — when a page tries to fetch data the user can't access, toast appears immediately | Violates Issue #11: no error toasts on passive navigation |
| G3 | **Detail pages don't distinguish 403 from 404** — both show generic "Failed to load" error | User can't tell if resource doesn't exist vs. no permission |
| G4 | **Settings sub-tabs show "Create one to get started"** for users who **can't** create | Misleading — suggests user should create something they're not allowed to |
| G5 | **Admin sidebar shows all settings items** regardless of role | Non-admin user sees IAM/org-iam links; clicking them shows empty or broken state |
| G6 | **No permission banner component** | No reusable way to show "Access denied — requires roles: X, Y" |
| G7 | **`PermissionGate` unused** | Good component exists but nobody uses it |
| G8 | **Agent-service error handler ignores `silent` flag** | Always fires toast even when `silent: true` is passed |
| G9 | **Dashboard quick-create hides items silently** | OK behavior, no issue |

### Backend 403 Response Analysis

The backend **already includes required roles** in the 403 detail message:
```
"Access denied: User does not have required permissions. Required: ['TENANT_GLOBAL_ADMIN'], Has: ['READER', 'CHAT_AGENTS_CREATOR']"
```

This is useful but unstructured (embedded in a string). For the frontend to show "requires roles: X, Y", we have two options:
1. Parse the string (fragile)
2. Add structured error response with `required_roles` field (clean, Package 0)

---

## Pakete

### ✅ Paket 0: API Client 403 Handling & Permission Banner Component

> Foundation: Structured 403 responses from backend + frontend infrastructure to handle them cleanly. Everything else builds on this.

#### 0.1 Backend: Structured 403 Response (platform-service)

| ID | Anforderung |
|----|-------------|
| 0.1.1 | Add a structured 403 error response format: `{ "detail": "...", "error_code": "PERMISSION_DENIED", "required_roles": ["TENANT_GLOBAL_ADMIN"], "user_roles": ["READER"] }` — returned alongside the existing `detail` string for backward compatibility |
| 0.1.2 | Apply the structured format to the `check_permissions` middleware in `auth.py` |
| 0.1.3 | Apply the structured format to handler-level `PermissionDeniedError` exceptions |

#### 0.2 Frontend: API Client 403 Handling

| ID | Anforderung |
|----|-------------|
| 0.2.1 | Create a typed `PermissionError` class (extends `Error`) that carries `requiredRoles`, `userRoles`, and `statusCode` fields. Parse 403 responses in `client.ts` into `PermissionError` instances instead of generic `Error` |
| 0.2.2 | **Suppress 403 toasts in the global `onError` handler** — when `error instanceof PermissionError`, do NOT show a toast notification. Pages/components handle 403s inline instead |
| 0.2.3 | Fix the agent-service request helper to respect the `silent` flag (same as the main `request()` method) |
| 0.2.4 | For explicit user actions (create, update, delete) that result in 403: continue showing error toast with a user-friendly message like "No permission for this action" (not the raw backend detail) |

#### 0.3 Frontend: Permission Banner Component (`AccessDeniedBanner`)

| ID | Anforderung |
|----|-------------|
| 0.3.1 | Create `src/components/common/AccessDeniedBanner/AccessDeniedBanner.tsx` — a Mantine `Alert` component with `color="orange"`, exclamation icon, displaying: title "Access Denied" and a message like "You do not have the required permissions. Required roles: {roles}" |
| 0.3.2 | Props: `requiredRoles?: string[]`, `message?: string` (custom override), `compact?: boolean` (for inline usage vs. full-width) |
| 0.3.3 | Use i18n keys for all strings (both en-US and de-DE) |
| 0.3.4 | Export from `components/common/index.ts` barrel |

---

### ✅ Paket 1: Settings Page (Admin Portal) — Permission Gating

> The admin portal settings page is where most non-admin users interact with restricted content. Apply the access pattern here.

#### 1.1 Admin Sidebar Filtering

| ID | Anforderung |
|----|-------------|
| 1.1.1 | In `AdminLayout.tsx`: Show all `SETTINGS_ITEMS` in the sidebar for all users (as requested — user sees all items) |
| 1.1.2 | **Exception**: Hide "Organisation IAM" (`org-iam`) for users without `hasOrgBypass` |
| 1.1.3 | **Exception**: Hide "Organisation Settings" (`organization`) for users without `hasOrgBypass` (only meaningful for org users) |

#### 1.2 Settings Tab Content — Permission Banners

| ID | Anforderung |
|----|-------------|
| 1.2.1 | **IAM tab**: When a non-admin navigates to `?tab=iam` (e.g., via direct URL or admin sidebar), show `AccessDeniedBanner` with required roles: `TENANT_GLOBAL_ADMIN` instead of empty/broken content. Don't hide the tab from the sidebar — show the banner as content |
| 1.2.2 | **Tenant Settings tab**: Keep current behavior (fields disabled for non-admins), but add a subtle info banner at the top: "Read-only — tenant settings require admin access to modify" |
| 1.2.3 | **Custom Groups / Tools / Credentials / AI Models tabs**: When user has no create permission AND the list is empty, replace "No X yet. Create one to get started." with `AccessDeniedBanner`: "You do not have permission to create {resource}. Required roles: {role}" |
| 1.2.4 | When user has no create permission but list is NOT empty (they can see existing items via membership), keep showing the list normally — just hide the Create button (current behavior, already works) |

#### 1.3 Settings Tab URL Safety

| ID | Anforderung |
|----|-------------|
| 1.3.1 | Ensure `?tab=iam` from URL does not render the IAM panel content for non-admins — render the `AccessDeniedBanner` instead |
| 1.3.2 | Ensure `?tab=org-iam` from URL does not render org IAM panel content for users without `hasOrgBypass` |

---

### ✅ Paket 2: Resource Pages — Create/Action Button Gating

> Ensure all resource pages consistently hide create/action buttons for users without permission.

#### 2.1 Create Button Consistency Audit

| ID | Anforderung |
|----|-------------|
| 2.1.1 | **ChatAgentsPage**: Verify create button is gated by `canCreate('chat-agents')` ✓ (already done) |
| 2.1.2 | **WorkflowsPage**: Verify create button is gated by `canCreate('workflows')` ✓ (already done) |
| 2.1.3 | **ChatWidgetsPage**: Verify create button is gated by `canCreate('chat-widgets')` ✓ (already done) |
| 2.1.4 | **ExternalAppsPage**: Verify add button is gated by `canCreate('external-apps')` ✓ (already done) |
| 2.1.5 | **ConversationsPage / sidebar**: Verify create conversation is gated by `canCreate('conversations')` |
| 2.1.6 | **DashboardPage**: Verify quick-create actions are filtered by `canCreate()` ✓ (already done) |

#### 2.2 Edit/Delete Button Consistency

| ID | Anforderung |
|----|-------------|
| 2.2.1 | Audit all detail pages and list item actions: ensure edit/delete buttons check `my_permission` (instance-level) or `isResourceAdmin` (role-level) |
| 2.2.2 | Standardize the pattern: use `canWrite(item.my_permission)` for edit, `canDelete(item.my_permission)` for delete — replace raw `=== 'ADMIN'` string comparisons |

---

### ✅ Paket 3: Detail Pages — 403 vs 404 Handling

> When a user navigates to a resource detail page they don't have access to, show a clear permission error instead of a generic "Failed to load" message.

#### 3.1 Detail Page Error Differentiation

| ID | Anforderung |
|----|-------------|
| 3.1.1 | **ChatAgentDetailsPage**: When the API call to fetch the agent returns a `PermissionError` (403), render `AccessDeniedBanner` instead of the generic red Alert. For 404 or other errors, keep the current "not found" behavior |
| 3.1.2 | **WorkflowDetailsPage**: Same pattern — distinguish 403 from other errors |
| 3.1.3 | **ConversationPage/ChatView**: If the selected conversation returns 403, show inline `AccessDeniedBanner` in the chat area |
| 3.1.4 | No toast should appear on navigation-triggered 403s (covered by Package 0.2.2) |

---

### ✅ Paket 4: Dashboard & Analytics Access

> Clarify analytics access and ensure dashboard works gracefully for all roles.

#### 4.1 Analytics Access

| ID | Anforderung |
|----|-------------|
| 4.1.1 | Analytics page (`/admin`) is already protected by `AdminProtectedRoute` — verify it redirects non-admins cleanly ✓ |
| 4.1.2 | The "Admin" link in the sidebar is already hidden for non-admins ✓ |
| 4.1.3 | No changes needed for analytics access gating |

#### 4.2 Dashboard Graceful Degradation

| ID | Anforderung |
|----|-------------|
| 4.2.1 | DashboardPage: If `getDashboardStats()` fails with 403, show a subtle `AccessDeniedBanner` instead of silently failing (currently logs to console and shows nothing) |
| 4.2.2 | DashboardPage: If stats load but user has no create permissions, the "Quick Actions" section should gracefully hide or show a reduced set (already works via `canCreate` filtering) |

---

## Access Pattern Summary (Target State)

### Rule 1: Hide What Users Can't Do
- **Create buttons**: Hidden via `canCreate(resourceType)` — already implemented ✓
- **Edit/Delete buttons**: Hidden via `canWrite/canDelete(my_permission)` — standardize
- **Admin-only links**: Hidden via `isGlobalAdmin` — already implemented ✓

### Rule 2: Show, Don't Toast — for Navigation
- **Page loads / data fetching**: NEVER show toast on 403. Show inline `AccessDeniedBanner` instead
- **Settings tabs**: Show the tab in sidebar, show banner in content area when no access

### Rule 3: Toast Only on Explicit Actions
- **Create/Update/Delete actions**: Show toast on 403 (user clicked a button, action was denied)
- **Message**: "No permission for this action" (user-friendly, not raw backend detail)

### Rule 4: Differentiate 403 from 404
- **Detail pages**: 403 → `AccessDeniedBanner` with required roles. 404 → "Not found" alert
- **List pages**: 403 on list fetch → `AccessDeniedBanner`. Empty list → normal empty state

---

## Anhang

### Referenzen

- [Issue #46 — Refactor frontend access view](https://github.com/unified-ui/unifiedui/issues/46)
- [Issue #11 — UX: Error notifications only after unauthorized action](https://github.com/unified-ui/unifiedui/issues/11)
- Frontend: `src/hooks/usePermissions.ts` — central RBAC hook
- Frontend: `src/components/common/PermissionGate/PermissionGate.tsx` — existing but unused
- Frontend: `src/api/client.ts` — API client with `onError` handler
- Backend: `unifiedui/core/middleware/apis/v1/auth.py` — `@check_permissions` decorator
- Backend: `unifiedui/exc/permissions.py` — `PermissionDeniedError`

### Role Reference

| Tenant Role | Can Create | Can Admin |
|-------------|-----------|-----------|
| `TENANT_GLOBAL_ADMIN` | Everything | Everything |
| `CHAT_AGENTS_CREATOR` | Chat Agents | — |
| `CHAT_AGENTS_ADMIN` | Chat Agents | Chat Agents |
| `CREDENTIALS_CREATOR` | Credentials | — |
| `CREDENTIALS_ADMIN` | Credentials | Credentials |
| `AUTONOMOUS_AGENTS_CREATOR` | Workflows | — |
| `AUTONOMOUS_AGENTS_ADMIN` | Workflows | Workflows |
| `CONVERSATIONS_CREATOR` | Conversations | — |
| `CONVERSATIONS_ADMIN` | Conversations | Conversations |
| `CHAT_WIDGETS_CREATOR` | Chat Widgets | — |
| `CHAT_WIDGETS_ADMIN` | Chat Widgets | Chat Widgets |
| `CUSTOM_GROUP_CREATOR` | Custom Groups | — |
| `CUSTOM_GROUPS_ADMIN` | Custom Groups | Custom Groups |
| `REACT_AGENT_CREATOR` | Tools (ReACT) | — |
| `REACT_AGENT_ADMIN` | Tools (ReACT) | Tools (ReACT) |
| `TENANT_AI_MODELS_ADMIN` | AI Models | AI Models |
| `EXTERNAL_APPS_CREATOR` | External Apps | — |
| `EXTERNAL_APPS_ADMIN` | External Apps | External Apps |
| `READER` | Nothing | Nothing |
