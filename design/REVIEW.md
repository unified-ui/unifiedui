# unified-ui — Comprehensive Code Review

**Date:** 2026-02-09
**Scope:** All three services (Platform, Agent, Frontend)
**Test Status:** Platform 1269/1269 ✅ · Agent all ✅ · Frontend 26/26 ✅ · TS 0 errors ✅

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Agent Service (Go)](#2-agent-service-go)
3. [Platform Service (Python)](#3-platform-service-python)
4. [Frontend Service (React/TS)](#4-frontend-service-reactts)
5. [Cross-Service Issues](#5-cross-service-issues)
6. [Priority Action Plan](#6-priority-action-plan)

---

## 1. Executive Summary

| Category | Agent (Go) | Platform (Python) | Frontend (React) | Total |
|----------|:----------:|:------------------:|:-----------------:|:-----:|
| Critical | 13 | 12 | 14 | **39** |
| Medium | 40 | 8 | 23 | **71** |
| Low | 61 | 3 | 18+ | **82+** |

**Top 3 systemic issues across the project:**
1. **Comment violations** — ~200+ inline/section/German comments across all services
2. **File size violations** — 25 Python files, 5 Go files, 2 TS files exceed limits
3. **Code duplication** — Platform tag/permission routers (~3000 lines), Go auth helpers, TS request methods

---

## 2. Agent Service (Go)

### 2.1 File Size Violations (limit: 300 lines)

| # | File | Lines | Severity |
|---|------|------:|----------|
| AG-1 | `internal/api/handlers/traces.go` | 629 | Critical |
| AG-2 | `internal/api/handlers/traces_import.go` | 549 | Critical |
| AG-3 | `internal/infrastructure/docdb/mongodb/traces.go` | 451 | Medium |
| AG-4 | `internal/api/handlers/messages_send.go` | 405 | Medium |
| AG-5 | `internal/domain/models/trace.go` | 351 | Medium |
| AG-6 | `internal/services/agents/factory.go` | 341 | Medium |
| AG-7 | `internal/api/dto/traces.go` | 337 | Medium |
| AG-8 | `cmd/server/main.go` | 334 | Medium |
| AG-9 | `internal/api/handlers/messages.go` | 308 | Low |
| AG-10 | `internal/api/handlers/ai.go` | 301 | Low |

**Fix:**
- `traces.go` (629): Extract `ListAutonomousAgentTraces`+`GetAutonomousAgentTraces`+`RefreshAutonomousAgentTrace` → `traces_autonomous.go`
- `traces_import.go` (549): Extract shared auth resolution block into helper, reduce branching
- `mongodb/traces.go` (451): Split into `traces.go` + `traces_indexes.go`
- `main.go` (334): Extract factory functions → `cmd/server/factories.go`
- `factory.go` (341): Extract n8n/foundry adapters → separate files

### 2.2 Comment Violations (~60+ violations)

| File | Count | Examples |
|------|------:|---------|
| `cmd/server/main.go` | 18 | `// Load configuration`, `// Initialize cache client`, `// Graceful shutdown` |
| `internal/api/middleware/auth.go` | 6 | `// Extract Bearer token`, `// Store token in context` |
| `internal/services/session/service.go` | 11 | `// Decrypt`, `// Marshal to JSON`, `// Save updated session` |
| `internal/services/traceimport/queue.go` | 3 | `// Execute the worker function`, `// Queue is full` |
| `internal/domain/models/trace.go` | 4 | `// Context fields`, `// Audit fields` |
| `internal/infrastructure/docdb/mongodb/*.go` | 2+ | `// Primary ID index`, `// Default to descending` |
| `internal/api/handlers/health.go` | 3 | `// Check cache`, `// Check document database` |

**Fix:** Remove all inline/section comments. Code should be self-documenting per project rules.

### 2.3 Security Issues

| # | File | Line | Severity | Issue | Fix |
|---|------|------|----------|-------|-----|
| AG-S1 | `handlers/traces.go` | L224 | **Critical** | `AddLogs` has NO auth check — anyone with tenant+trace ID can add logs | Add `resolveUserIDForTrace` call matching `AddNodes` |
| AG-S2 | `platform/types.go` | L160 | **Critical** | `GetSecretAsBasicAuth()` uses unsafe `m["username"].(string)` — panics on malformed data | Use comma-ok pattern |
| AG-S3 | `cmd/server/main.go` | L298 | Medium | Swagger UI exposed unconditionally in production | Gate behind `GIN_MODE != "release"` |
| AG-S4 | `middleware/auth.go` | L62 | Medium | `token.(string)` without comma-ok guard | Add type assertion guard |

### 2.4 Error Handling Issues

| # | File | Severity | Issue | Fix |
|---|------|----------|-------|-----|
| AG-E1 | `traceimport/queue.go:59` | **Critical** | Worker errors silently swallowed: `_ = q.workerFunc(...)` | Log error on failure |
| AG-E2 | `traceimport/queue.go:68` | **Critical** | Jobs silently dropped when queue full — data loss | Return error or log |
| AG-E3 | `platform/client.go` (3x) | Medium | `ValidateConversation`/`ValidateAutonomousAgent`/`ValidateAPIKey` return `nil` when `baseURL == ""` | Return error consistently |
| AG-E4 | `handlers/health.go` | Medium | Raw `c.JSON(StatusServiceUnavailable, gin.H{...})` instead of domain errors | Use `middleware.HandleError` |

### 2.5 Code Duplication

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| AG-D1 | `getUserID()` identical on `TracesHandler` and `ReactionsHandler` | Critical | Extract to shared helper |
| AG-D2 | Auth resolution block duplicated in `ImportAutonomousAgentTrace` + `RefreshAutonomousAgentImportTrace` (~40 lines each) | Critical | Extract `resolveAutonomousAgentAuth()` |
| AG-D3 | Error-string-prefix parsing (`strings.HasPrefix(errStr, "unauthorized")`) repeated ~8 times | Medium | Create `mapPlatformError()` helper |
| AG-D4 | `RefreshConversationTrace` / `RefreshAutonomousAgentTrace` structurally identical (~55 lines each) | Medium | Extract shared refresh logic |
| AG-D5 | `"autonomous-agent-"` prefix used 4 times | Low | Define constant |
| AG-D6 | `"X-Microsoft-Foundry-API-Key"` header 3 times | Low | Define constant |
| AG-D7 | Vault client/cache client wrapper delegation identical across 3 implementations | Medium | Merge `Vault`/`Client` interfaces |

### 2.6 Consistency Issues

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| AG-C1 | `ai.go` uses `c.Get("auth_token")` while all others use `middleware.GetToken(c)` | Critical | Use `middleware.GetToken(c)` |
| AG-C2 | `ai.go` imports errors as `domainerrors`, others use `errors` | Medium | Standardize alias |
| AG-C3 | `traces_helpers.go` uses substring check `errStr[:12]`, others use `strings.HasPrefix` | Medium | Use `strings.HasPrefix` |
| AG-C4 | Inline DTOs in handlers vs dto/ package — inconsistent | Medium | DTOs should all be in handlers or all in dto/ |
| AG-C5 | `messages.go` (plural) vs `trace.go`/`session.go`/`reaction.go` (singular) in models | Low | Rename to `message.go` |

### 2.7 Dead Code

| # | File | Issue | Severity |
|---|------|-------|----------|
| AG-DC1 | `domain/models/session.go` | Entire file likely unused — service uses `session.SessionData` | Medium |
| AG-DC2 | `core/vault` interface | `useCache` parameter ignored by all implementations | Medium |
| AG-DC3 | `core/cache/client.go` | `GetCache() Cache` leaks inner interface | Low |
| AG-DC4 | `traces_import.go:157` | `buildN8NConfig` always returns "not yet implemented" error | Low |
| AG-DC5 | `traces.go:37` | `GetImportService()` exposes internal for testing | Low |

### 2.8 Architectural Issues

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| AG-A1 | Handlers contain substantial business logic (CreateTrace ~108 lines, handleStreamingResponse ~60 lines) | Critical | Move orchestration logic to service layer |
| AG-A2 | `ImportService` is concrete struct, not interface — hard to mock in tests | Medium | Extract interface |
| AG-A3 | `platform.Client` has 15 methods — too broad | Medium | Split by concern |
| AG-A4 | `session/service.go` read-modify-write without locking (concurrency risk) | Medium | Use Redis WATCH/MULTI |
| AG-A5 | `queue.Stop()` closes channel while goroutines may still write — potential panic | Medium | Add send-guard |
| AG-A6 | `streamTitleGeneration` uses `context.Background()` — orphaned on shutdown | Medium | Use server context |

### 2.9 Magic Constants

| # | Value | Location | Fix |
|---|-------|----------|-----|
| AG-M1 | `"2025-11-15-preview"` | traces_import.go:151 | `const DefaultFoundryAPIVersion` |
| AG-M2 | `"20"`, `"0"` default query params | traces_helpers.go:24-25 | `const DefaultTraceListLimit/Skip` |
| AG-M3 | `100` max limit | traces_helpers.go:39 | `const MaxTraceListLimit` |
| AG-M4 | `"msg_"`, `"conv_"` prefixes | messages_helpers.go:17,21 | Define constants |
| AG-M5 | `15 * time.Second` title timeout | messages_send.go:393 | `const TitlePersistTimeout` |
| AG-M6 | `100` queue buffer, `3` workers | service.go/main.go | Config values |

---

## 3. Platform Service (Python)

### 3.1 File Size Violations (limit: 400 lines) — 25 files

| # | File | Lines | Over by |
|---|------|------:|--------:|
| PL-1 | `apis/v1/tags.py` | 1492 | 1092 |
| PL-2 | `handlers/autonomous_agents.py` | 1223 | 823 |
| PL-3 | `apis/v1/autonomous_agents.py` | 962 | 562 |
| PL-4 | `handlers/applications.py` | 956 | 556 |
| PL-5 | `core/database/models.py` | 986 | 586 |
| PL-6 | `handlers/custom_groups.py` | 921 | 521 |
| PL-7 | `handlers/resource_permissions.py` | 849 | 449 |
| PL-8 | `handlers/credentials.py` | 835 | 435 |
| PL-9 | `handlers/tags.py` | 765 | 365 |
| PL-10 | `apis/v1/applications.py` | 758 | 358 |
| PL-11 | `handlers/principals.py` | 761 | 361 |
| PL-12 | `apis/v1/credentials.py` | 739 | 339 |
| PL-13 | `handlers/tools.py` | 733 | 333 |
| PL-14 | `core/middleware/apis/v1/auth.py` | 724 | 324 |
| PL-15 | `handlers/chat_widgets.py` | 721 | 321 |
| PL-16 | `handlers/conversations.py` | 712 | 312 |
| PL-17 | `handlers/re_act_agents.py` | 698 | 298 |
| PL-18 | `apis/v1/chat_widgets.py` | 669 | 269 |
| PL-19 | `apis/v1/conversations.py` | 664 | 264 |
| PL-20 | `apis/v1/tools.py` | 580 | 180 |
| PL-21 | `apis/v1/re_act_agents.py` | 532 | 132 |
| PL-22 | `handlers/resource_tags.py` | 531 | 131 |
| PL-23 | `app.py` | 507 | 107 |
| PL-24 | `handlers/tenants.py` | 493 | 93 |
| PL-25 | `handlers/tenant_ai_models.py` | 485 | 85 |

**Root cause:** Massive duplication in tag/permission routes. See PL-D1/PL-D2.

### 3.2 Critical Architecture Issues

| # | Issue | Severity | Impact | Fix |
|---|-------|----------|--------|-----|
| PL-A1 | **Duplicated tag CRUD** — `tags.py` (1492 lines) has 6 identical sets of tag endpoints for each resource type | **Critical** | ~1200 lines of pure duplication | Create `create_resource_tag_router(resource_type, handler_factory)` factory → reduces to ~150 lines |
| PL-A2 | **Duplicated permission CRUD** — 7 resource route files each have ~200-250 lines of identical permission endpoints | **Critical** | ~1400 lines of duplication | Create `create_permission_router(resource_type, handler_factory)` factory |
| PL-A3 | **Verbose try/except in routes** — 116 `except Exception as e:` blocks manually converting exceptions to HTTPException | **Critical** | Massive boilerplate; also leaks internal errors | Replace with global exception handler middleware in `app.py` |
| PL-A4 | **Duplicate exception handling** — `app.py` registers global handlers AND routes catch/re-raise the same exceptions | Medium | Conflicting, redundant | Choose one: global handlers (recommended) or route-level |
| PL-A5 | **Empty `exc/base.py`** — no common exception base class | Medium | Each domain defines its own hierarchy | Define `UnifiedUIError` → `NotFoundError` / `ConflictError` / `ValidationError` base |

### 3.3 Security Issues

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| PL-S1 | `notifications.py:142` — `create_notification_webhook` has **NO auth decorator** | **Critical** | Add `@authenticate_service_key()` or similar |
| PL-S2 | **106 instances** of `detail=str(e)` in HTTPException — leaks internal errors (DB errors, vault errors, stack traces) to API consumers | **Critical** | Log actual error, return generic message |
| PL-S3 | `identity.py:43` — uses `print()` instead of `logger` | Critical | Replace with `logger.error()` |

### 3.4 Code Quality Issues

| # | Issue | Count | Severity | Fix |
|---|-------|------:|----------|-----|
| PL-Q1 | Generic `ValueError`/`RuntimeError` raises instead of custom exceptions | ~55 | Critical | Define custom exceptions in `exc/` |
| PL-Q2 | Section-divider comments (`# ========== ... ==========`) | 44+ | Medium | Remove all; file splitting makes them unnecessary |
| PL-Q3 | Business logic in routes (tag ID parsing, roles parsing) | 6+ | Critical | Move to handlers or utility functions |
| PL-Q4 | Missing `response_model` on list endpoints | 7 | Medium | Add typed response models |
| PL-Q5 | Raw `dict` returns instead of Pydantic models | 2 | Medium | Create proper response schemas |
| PL-Q6 | Magic integer status codes instead of `fastapi.status` constants | 301 | Low | Use `status.HTTP_404_NOT_FOUND` etc. |

### 3.5 Highest-Impact Refactors

These 3 changes would eliminate ~4000+ lines and fix the majority of issues:

1. **Generic tag/permission router factories** → eliminates PL-1, PL-A1, PL-A2 (~3000 lines)
2. **Global exception middleware** → eliminates PL-A3, PL-S2, PL-Q1 (116 try/except blocks + 106 error leaks)
3. **Split `models.py`** into per-domain files → eliminates PL-5

---

## 4. Frontend Service (React/TS)

### 4.1 File Size Violations (limit: 400 lines)

| # | File | Lines | Severity |
|---|------|------:|----------|
| FE-1 | `src/api/client.ts` | 1467 | Critical |
| FE-2 | `src/api/types.ts` | 1372 | Critical |
| FE-3 | `src/pages/TenantSettingsPage/TenantSettingsPage.tsx` | ~1998 | Critical |
| FE-4 | `src/components/layout/Sidebar/Sidebar.tsx` | 544 | Medium |
| FE-5 | `src/components/common/DataTable/DataTable.tsx` | ~500 | Medium |
| FE-6 | `src/components/common/ChatPanel/ChatPanel.tsx` | ~570 | Medium |
| FE-7 | `src/hooks/useEntityList.ts` | 376 | Low |

**Fix:**
- `client.ts` (1467): Split into `client/base.ts`, `client/tenants.ts`, `client/agents.ts`, `client/messages.ts`, etc.
- `types.ts` (1372): Split into `types/tenant.ts`, `types/agent.ts`, `types/trace.ts`, etc.
- `TenantSettingsPage` (~1998): Extract each tab into its own component
- `Sidebar.tsx` (544): Extract conversation sidebar logic to `useConversationsSidebar` hook

### 4.2 Comment Violations (~150+ violations)

| Location | Count | Notable |
|----------|------:|---------|
| `src/api/client.ts` | ~80 | Section headers, JSDoc, inline `// Handle 204` |
| `src/api/types.ts` | ~60 | All section headers, inline type hints |
| `src/theme/mantineTheme.ts` | 15 | **German** comments (`// Primary Color (verwendet für Buttons...)`) |
| `src/theme/colors.ts` | 50+ | **German** + shade labels |
| `src/auth/authConfig.ts` | 3 | **German** (`// MSAL Konfiguration`) |
| `src/authConfig.ts` | 8 | **German** (`// Ersetze mit deiner Azure AD App Client ID`) |
| `src/styles/variables.css` | 10+ | **German** block comment + section headers |
| `src/contexts/ChatSidebarContext.tsx` | 12 | JSDoc + inline |

### 4.3 Security Issues

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| FE-S1 | **Hardcoded Azure AD Client ID** in `src/auth/authConfig.ts` AND duplicate `src/authConfig.ts` | Critical | Move to `import.meta.env.VITE_MSAL_CLIENT_ID` |
| FE-S2 | **Dead duplicate auth config** — `src/authConfig.ts` is never imported but contains credentials | Critical | Delete file |
| FE-S3 | OAuth scopes hardcoded in 3 different places | Medium | Centralize into single constant |

### 4.4 Performance Issues

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| FE-P1 | `AuthProvider.tsx` — `login`, `logout`, `getAccessToken`, `getFoundryToken` NOT wrapped in `useCallback`; `value` object recreated every render | **Critical** | Wrap all in `useCallback`, `value` in `useMemo` |
| FE-P2 | `IdentityContext.tsx` — `useEffect` depends on `getAccessToken` which isn't memoized → API client recreated every render | **Critical** | Memoize `getAccessToken` first |
| FE-P3 | `IdentityContext.tsx` — `refreshIdentity` not wrapped in `useCallback` | Medium | Add `useCallback` |
| FE-P4 | `SidebarDataContext.tsx` — `useCallback` deps include mutable state, defeating memoization | Medium | Restructure dependencies |

### 4.5 Code Duplication

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| FE-D1 | `src/authConfig.ts` exact duplicate of `src/auth/authConfig.ts` | Critical | Delete root-level copy |
| FE-D2 | `request()` and `agentServiceRequest()` in client.ts — near-identical ~50-line fetch methods | Critical | Extract shared `_fetch()` base method |
| FE-D3 | `SidebarDataContext.tsx` — `fetchApplications`/`fetchAutonomousAgents`/`fetchChatWidgets` structurally identical | Medium | Create generic `fetchEntities<T>(fetcher, stateKey)` |
| FE-D4 | Create/Edit dialog pairs share 80%+ code across entity types | Medium | Create generic `EntityFormDialog<T>` |
| FE-D5 | Tag convenience methods in client.ts — 6 identical one-liner patterns | Low | Generate dynamically |

### 4.6 i18n Issues

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| FE-I1 | **40+ hardcoded success messages** in `client.ts` (`'Application created successfully'`, etc.) | Critical | Move to i18n or handle at call sites |
| FE-I2 | **~28 page/component files** have NO i18n for user-visible text | Critical | Add `useTranslation()` + define keys |
| FE-I3 | **`ConfirmDeleteDialog`** — 6 hardcoded English strings, used in 12+ locations | Critical | Add i18n keys |
| FE-I4 | **`settings` namespace (10 keys) entirely unused** — `TenantSettingsPage` doesn't call `useTranslation('settings')` | Medium | Wire up or remove unused keys |
| FE-I5 | **~40 unused i18n keys** defined in JSON but never referenced | Medium | Audit and remove |

### 4.7 Error Handling

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| FE-E1 | `main.tsx` — `msalInstance.initialize().then(...)` has no error handler | Critical | Add `.catch()` with user-visible error |
| FE-E2 | `IdentityContext.tsx` — `refreshIdentity` swallows errors with `console.error` | Medium | Show notification to user |
| FE-E3 | 19 files use `console.error` instead of notification system | Medium | Replace with notification toasts |

### 4.8 Dead Code

| # | File | Issue | Severity |
|---|------|-------|----------|
| FE-DC1 | `src/authConfig.ts` | Entire file never imported | Critical |
| FE-DC2 | `src/theme/mantineTheme.ts` `darkTheme` export | Never imported | Medium |
| FE-DC3 | `src/theme/spacing.ts` | Export unused | Low |
| FE-DC4 | `src/api/types.ts` legacy type aliases | Verify usage | Low |

### 4.9 Test Coverage

| Category | Tested | Total | Coverage |
|----------|-------:|------:|---------:|
| Pages | 1 | ~15 | 7% |
| Common components | 0 | ~12 | 0% |
| Layout components | 1 | 4 | 25% |
| Dialogs | 0 | ~18 | 0% |
| Tracing | 0 | ~9 | 0% |
| Hooks | 0 | 3 | 0% |
| Contexts | 0 | 10 | 0% |
| i18n/setup | 2 | 2 | 100% |
| **Total** | **4** | **~73** | **5%** |

**Priority test targets:** `useEntityList` hook, `DataTable` component, `ChatPanel`, `ConfirmDeleteDialog`, all contexts.

### 4.10 Hook Issues

| # | File | Issue | Severity | Fix |
|---|------|-------|----------|-----|
| FE-H1 | `useEntityList.ts` | Missing `AbortController` — stale data risk on tenant switch | Medium | Add cleanup in useEffect |
| FE-H2 | `useEntityPermissions.ts` | Sequential `await` in loop for batch operations | Medium | Use `Promise.all` |
| FE-H3 | `useEntityList.ts` | `handleDuplicate` is a no-op stub | Low | Remove or implement |

---

## 5. Cross-Service Issues

### 5.1 Systemic Patterns

| # | Issue | Services | Severity |
|---|-------|----------|----------|
| XS-1 | **Comment violations everywhere** — ~200+ inline/section comments across all services despite "no comments" rule | All | Critical |
| XS-2 | **File size limits widely ignored** — 25 Python, 5 Go, ~7 TS files over limit | All | Critical |
| XS-3 | **Hardcoded config** — Client IDs, API versions, worker counts, timeouts | All | Medium |
| XS-4 | **Low test coverage** — Platform 80% (good), Agent handlers tested, Frontend 5% (critical gap) | Frontend | Critical |

### 5.2 Error Handling Philosophy

The three services handle errors inconsistently:
- **Platform:** Manual try/except in every route + redundant global handlers + raw `str(e)` leakage
- **Agent:** Domain error types with middleware.HandleError (good), but some handlers use raw `c.JSON`
- **Frontend:** `console.error` instead of user notifications; MSAL init unguarded

**Recommendation:** Establish error handling guidelines in copilot-instructions:
- Platform: Global exception middleware only, no route-level try/except
- Agent: Always use `middleware.HandleError`, never raw `c.JSON` for errors
- Frontend: Always use notification system, never `console.error` for user-facing errors

---

## 6. Priority Action Plan

### Phase 1: Critical Security & Bugs (do first)

| # | Service | Action | Impact |
|---|---------|--------|--------|
| 1 | Agent | Fix `AddLogs` missing auth check (AG-S1) | Security hole |
| 2 | Agent | Fix `GetSecretAsBasicAuth` panic (AG-S2) | Crash risk |
| 3 | Agent | Log queue worker errors (AG-E1, AG-E2) | Silent data loss |
| 4 | Platform | Add auth to `create_notification_webhook` (PL-S1) | Unprotected endpoint |
| 5 | Platform | Replace `detail=str(e)` with generic messages (PL-S2) | Error leakage (106 instances) |
| 6 | Frontend | Delete duplicate `src/authConfig.ts` (FE-DC1) | Dead credentials in source |
| 7 | Frontend | Move Client ID to env var (FE-S1) | Hardcoded secret |
| 8 | Frontend | Add MSAL init error handling (FE-E1) | Silent failure |

### Phase 2: Performance & Stability

| # | Service | Action | Impact |
|---|---------|--------|--------|
| 9 | Frontend | Memoize AuthProvider functions + value (FE-P1) | Excessive re-renders |
| 10 | Frontend | Memoize IdentityContext deps (FE-P2) | API client recreation |
| 11 | Agent | Fix `ai.go` auth token retrieval (AG-C1) | Potentially broken auth |
| 12 | Agent | Add send-guard to queue.Stop() (AG-A5) | Potential panic |

### Phase 3: Highest-Impact Refactors

| # | Service | Action | Lines saved |
|---|---------|--------|------------:|
| 13 | Platform | Generic tag router factory (PL-A1) | ~1200 |
| 14 | Platform | Generic permission router factory (PL-A2) | ~1400 |
| 15 | Platform | Global exception middleware (PL-A3) | ~1500 (116 try/except + error leaks) |
| 16 | Platform | Custom exception hierarchy in `exc/base.py` (PL-A5) | ~55 generic raises |
| 17 | Frontend | Split `client.ts` into domain modules | 1467 → ~12 × 120 |
| 18 | Frontend | Split `types.ts` into domain modules | 1372 → ~10 × 140 |
| 19 | Frontend | Extract `request()`/`agentServiceRequest()` shared base | ~50 lines DRY |
| 20 | Frontend | Split `TenantSettingsPage` into tab components | ~1998 → ~6 × 300 |

### Phase 4: Comment Cleanup

| # | Service | Action | Count |
|---|---------|--------|------:|
| 21 | Agent | Remove all inline/section comments | ~60 |
| 22 | Platform | Remove all section divider comments | ~44 |
| 23 | Frontend | Remove all comments from client.ts, types.ts | ~140 |
| 24 | Frontend | Remove/translate German comments | ~30 |

### Phase 5: Test Coverage

| # | Service | Action | Priority |
|---|---------|--------|----------|
| 25 | Frontend | Test `useEntityList` hook | High |
| 26 | Frontend | Test `DataTable` component | High |
| 27 | Frontend | Test all contexts (10 untested) | High |
| 28 | Frontend | Test `ConfirmDeleteDialog` | Medium |
| 29 | Frontend | Test `ChatPanel` | Medium |
| 30 | Frontend | Test all page components (~15) | Lower |

### Phase 6: Code Quality Polish

| # | Service | Action |
|---|---------|--------|
| 31 | Agent | Extract constants (AG-M1 through AG-M6) |
| 32 | Agent | Merge Vault/Cache interfaces (AG-DC2, AG-D7) |
| 33 | Agent | Remove dead `models/session.go` (AG-DC1) |
| 34 | Agent | Move handler business logic to services (AG-A1) |
| 35 | Platform | Replace `print()` with `logger` (PL-S3) |
| 36 | Platform | Use `fastapi.status` constants (PL-Q6) |
| 37 | Platform | Split `models.py` into per-domain files |
| 38 | Frontend | i18n for all remaining hardcoded strings (~28 files) |
| 39 | Frontend | Replace `console.error` with notifications (19 files) |
| 40 | Frontend | Delete dead code (FE-DC2, FE-DC3, FE-DC4) |
