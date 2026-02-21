# Frontend Code Review

> **Scope**: `src/pages/`, `src/components/`, `src/hooks/`  
> **Date**: 2025-07-14 (original), **2026-02-09 (i18n & Test Coverage addendum)**  
> **Format**: File · Line(s) · Category · Severity · Description + Fix

---

## Table of Contents

1. [File Size Violations (>400 lines)](#1-file-size-violations-400-lines)
2. [i18n Violations — Hardcoded Strings](#2-i18n-violations--hardcoded-strings)
3. [Comment Violations](#3-comment-violations)
4. [Code Duplication](#4-code-duplication)
5. [Dead Code / Unused Variables](#5-dead-code--unused-variables)
6. [console.error / console.log Usage](#6-consoleerror--consolelog-usage)
7. [Inline Styles](#7-inline-styles)
8. [eslint-disable Comments](#8-eslint-disable-comments)
9. [Export Pattern Violations](#9-export-pattern-violations)
10. [CSS Custom Properties Violations](#10-css-custom-properties-violations)
11. [Miscellaneous Issues](#11-miscellaneous-issues)

---

## Summary

| Category | Critical | Medium | Low | Total |
|---|---|---|---|---|
| File Size | 17 | 3 | 0 | 20 |
| i18n | 28 | 8 | 0 | 36 |
| Comments | 0 | 8 | 12 | 20 |
| Code Duplication | 5 | 4 | 0 | 9 |
| Dead Code | 0 | 5 | 3 | 8 |
| console.error | 0 | 19 | 0 | 19 |
| Inline Styles | 0 | 0 | 14 | 14 |
| eslint-disable | 0 | 7 | 0 | 7 |
| Export Pattern | 0 | 0 | 5 | 5 |
| CSS Custom Props | 0 | 0 | 3 | 3 |
| Miscellaneous | 0 | 3 | 2 | 5 |
| **Total** | **50** | **57** | **39** | **146** |

---

## 1. File Size Violations (>400 lines)

All files must be **< 400 lines**. Files exceeding this limit need decomposition.

| File | Lines | Over By | Severity |
|---|---|---|---|
| `pages/TenantSettingsPage/TenantSettingsPage.tsx` | 1998 | 5.0× | **Critical** |
| `components/tracing/TracingCanvasView/TracingCanvasView.tsx` | 975 | 2.4× | **Critical** |
| `components/dialogs/EditChatAgentDialog/EditChatAgentDialog.tsx` | 937 | 2.3× | **Critical** |
| `components/tracing/TracingHierarchyView/TracingHierarchyView.tsx` | 781 | 2.0× | **Critical** |
| `pages/AutonomousAgentDetailsPage/AutonomousAgentDetailsPage.tsx` | 700 | 1.75× | **Critical** |
| `components/common/AddPrincipalDialog/AddPrincipalDialog.tsx` | 641 | 1.6× | **Critical** |
| `components/dialogs/CreateChatAgentDialog/CreateChatAgentDialog.tsx` | 602 | 1.5× | **Critical** |
| `components/dialogs/EditAutonomousAgentDialog/EditAutonomousAgentDialog.tsx` | 591 | 1.48× | **Critical** |
| `pages/ConversationsPage/components/ChatSidebar/ChatSidebar.tsx` | 591 | 1.48× | **Critical** |
| `components/common/ManageTenantAccessTable/ManageTenantAccessTable.tsx` | 576 | 1.44× | **Critical** |
| `components/layout/Sidebar/Sidebar.tsx` | 545 | 1.36× | **Critical** |
| `components/dialogs/AIModelDialog/AIModelDialog.tsx` | 498 | 1.25× | **Critical** |
| `pages/ConversationsPage/hooks/useChat.ts` | 486 | 1.22× | **Critical** |
| `pages/ConversationsPage/components/ChatContent/ChatContent.tsx` | 484 | 1.21× | **Critical** |
| `pages/ReActAgentDeveloperPage/ReActAgentDeveloperPage.tsx` | 481 | 1.20× | **Critical** |
| `components/dialogs/EditCustomGroupDialog/EditCustomGroupDialog.tsx` | 456 | 1.14× | **Critical** |
| `components/dialogs/EditCredentialDialog/EditCredentialDialog.tsx` | 444 | 1.11× | **Critical** |
| `components/common/ManageAccessTable/ManageAccessTable.tsx` | 437 | 1.09× | **Medium** |
| `components/common/DataTable/DataTable.tsx` | 403 | 1.01× | **Medium** |
| `components/dialogs/EditChatWidgetDialog/EditChatWidgetDialog.tsx` | 401 | 1.00× | **Medium** |

### Recommended Decompositions

**TenantSettingsPage (1998 → ~7 files)**
- Extract each tab into its own component: `GroupsTab`, `ToolsTab`, `CredentialsTab`, `AIModelsTab`, `MembersTab`, `DangerZoneTab`, `GeneralSettingsTab`
- Move shared table patterns into a reusable `TenantEntityTable` component
- Extract `useTenantSettings` hook for state management

**TracingCanvasView (975 → ~4 files)**
- Extract `TraceCustomNode`, `InvisibleNode` into `TracingCanvasView/nodes/`
- Extract `CollapsibleEdge`, `IndexedEdge` into `TracingCanvasView/edges/`
- Extract `useTracingLayout` hook for dagre layout logic
- Extract `useTracingCanvas` hook for selection/interaction state

**EditChatAgentDialog (937 → ~4 files)**
- Extract `ChatAgentDetailsForm` component
- Extract `ChatAgentN8NConfig` component
- Extract `ChatAgentFoundryConfig` component
- Extract `ChatAgentIAMTab` component

**TracingHierarchyView (781 → ~4 files)**
- Extract `JsonViewer` into a shared `common/` component (also used by `TracingDataSection`)
- Extract `ResizablePanel` component
- Extract `TreeItem` / `TreeItemWrapper` components
- Extract `DataPanelsContainer` component

**AutonomousAgentDetailsPage (700 → ~4 files)**
- Extract `AgentDetailsTab`, `AgentTracesTab`, `AgentKeysTab`, `AgentN8NConfigTab`
- Extract `useAgentDetails` hook

---

## 2. i18n Violations — Hardcoded Strings

All user-visible strings must use `useTranslation()` with proper i18n keys.

### Critical — Hardcoded German Strings

| File | Line(s) | String | Severity | Fix |
|---|---|---|---|---|
| `pages/NotFoundPage/NotFoundPage.tsx` | ~10-15 | `"Die angeforderte Seite konnte nicht gefunden werden."`, `"Zurück zum Dashboard"` | **Critical** | Replace with `t('notFound:message')`, `t('notFound:backToDashboard')` |
| `pages/LoginTokenPage/LoginTokenPage.tsx` | ~90-100 | `'Kopiert!'`, `'Token kopieren'` | **Critical** | Replace with `t('loginToken:copied')`, `t('loginToken:copyToken')` |
| `pages/TracingDialogDevelopmentPage/TracingDialogDevelopmentPage.tsx` | ~40-60 | `'Fehler beim Laden der Traces'`, `'Verwendung'` | **Critical** | Replace with i18n keys |
| `components/common/TagInput/TagInput.tsx` | ~30 | `'Tag eingeben...'` | **Critical** | Replace with `t('common:enterTag')` |
| `components/tracing/TracingSubHeader/TracingSubHeader.tsx` | ~80 | Hardcoded `'de-DE'` locale in `toLocaleTimeString` | **Critical** | Use `i18n.language` for locale |
| `components/tracing/TracingHierarchyView/TracingHierarchyView.tsx` | ~15 | `"Tracing Hierarchie"` (title), `"Vollbild"` (tooltip) | **Critical** | Replace with `t('tracing:hierarchy')`, `t('tracing:fullscreen')` |
| `components/tracing/TracingCanvasView/TracingCanvasView.tsx` | throughout | German variable names and comments throughout file | **Critical** | Translate all to English |

### Critical — Hardcoded English Strings (Systematic)

These files have **no i18n at all** or import `useTranslation` but don't use `t()` for most strings:

| File | Examples of hardcoded strings | Severity |
|---|---|---|
| `components/dialogs/CreateChatAgentDialog` | `"Create Chat Agent"`, `"Name"`, `"Cancel"`, `"Create"`, validation messages | **Critical** |
| `components/dialogs/CreateAutonomousAgentDialog` | `"Create Autonomous Agent"`, `"Name"`, `"Type"`, all form labels | **Critical** |
| `components/dialogs/CreateChatWidgetDialog` | `"Create Chat Widget"`, `"Name"`, `"Type"`, `"Cancel"`, `"Create"` | **Critical** |
| `components/dialogs/CreateCredentialDialog` | `"Create Credential"`, `"Name"`, `"Type"`, all validation | **Critical** |
| `components/dialogs/CreateCustomGroupDialog` | `"Create Custom Group"`, `"Name"`, `"Cancel"`, `"Create"` | **Critical** |
| `components/dialogs/CreateTenantDialog` | `"Create Tenant"`, `"Name"`, `"Cancel"`, `"Create"` | **Critical** |
| `components/dialogs/CreateToolDialog` | `"Create New Tool"`, `"Name"`, `"Type"`, `"Cancel"`, `"Create"` | **Critical** |
| `components/dialogs/EditChatAgentDialog` | All form labels, tab labels, validation messages, badge text | **Critical** |
| `components/dialogs/EditAutonomousAgentDialog` | `"Active"`, `"Inactive"`, all labels, validation | **Critical** |
| `components/dialogs/EditChatWidgetDialog` | `"Details"`, `"Manage Access"`, `"Name"`, `"Cancel"`, `"Save Changes"`, `"Active"`, `"Inactive"` | **Critical** |
| `components/dialogs/EditToolDialog` | `"Details"`, `"Manage Access"`, `"Name"`, `"Cancel"`, `"Save Changes"`, `"Active"`, `"Inactive"` | **Critical** |
| `components/dialogs/EditCredentialDialog` | All form labels (imports `useTranslation` but barely uses `t()`) | **Critical** |
| `components/dialogs/EditCustomGroupDialog` | `"Member"`, `"Admin"`, form labels, validation | **Critical** |
| `components/dialogs/AIModelDialog` | Provider labels, model config labels, validation messages, `"Test Model"` | **Critical** |
| `components/dialogs/AnalyzeErrorDialog` | `"AI Error Analysis"`, `"Analyzing error..."`, `"Retry"`, `"Re-generate"`, `"Close"` | **Critical** |
| `components/dialogs/IntegrationDialog` | `"Endpoint"`, `"Copied!"`, `"Copy"`, `"Add header"`, `"with value"`, `"Or add header"`, tab labels | **Critical** |
| `components/dialogs/SearchConversationsDialog` | `"Search Conversations"`, `"Start typing..."`, `"No conversations found"`, time format strings | **Critical** |
| `components/common/DataTableToolbar` | `"Tags"`, `"Status"`, `"Select tags"`, `"All"`, `"Active"`, `"Inactive"`, `"Reset"`, `"Apply Filters"` | **Critical** |
| `components/common/DataTableRow` | Menu item labels: `"Edit"`, `"Share"`, `"Pin"`, `"Delete"` etc. | **Critical** |
| `components/common/TracesTable` | All column headers and labels | **Critical** |
| `components/common/SecretField` | `"Hide"`, `"Reveal"`, `"Copied!"`, `"Copy"`, `"Rotate key"` | **Critical** |
| `components/common/DetailPageTabs` | `"Details"`, `"Manage Access"` | **Critical** |
| `components/common/ConfirmDeleteDialog` | `"Delete"`, `"Cancel"`, confirmation messages | **Critical** |
| `components/tracing/TracingVisualDialog` | `"Tracing for {name}"`, `"Summarize with AI"` | **Critical** |
| `components/tracing/TracingDataSection` | `"Logs"`, `"Input / Output"`, `"Metadata"`, `"Input"`, `"Output"`, `"Analyze Error"`, `"Text:"` etc. | **Critical** |
| `components/tracing/TraceAnalysisPanel` | `"AI Trace Summary"`, `"Short"`, `"Medium"`, `"Long"`, `"Summarizing trace..."`, `"Retry"` | **Critical** |
| `components/tracing/TraceChatPanel` | `"Trace Chat"`, `"Clear chat"`, `"Ask questions about this trace"`, `"Thinking..."` | **Critical** |
| `pages/ConversationsPage/components/ChatInput` | `"Type a message..."`, `"Drop files here"`, `"Attach files"`, `"Send message"`, `"Generating..."`, `"Press Enter to send..."` | **Critical** |

### Medium — Partial i18n (Some strings translated, some not)

| File | Issue | Severity |
|---|---|---|
| `pages/ChatAgentsPage` | `"Chat Agents"`, `"Manage your AI chat agents"`, `"Create Chat Agent"`, `"Search chat agents..."` | **Medium** |
| `pages/AutonomousAgentsPage` | Page title, description, button labels | **Medium** |
| `pages/ChatWidgetsPage` | Similar to above | **Medium** |
| `pages/LoginTokenPage` | `"Access Token"`, `"Graph API Token"` hardcoded alongside i18n | **Medium** |
| `pages/AutonomousAgentDetailsPage` | Extensive hardcoded labels across all sections | **Medium** |
| `components/layout/SidebarDataList` | `'Collapse'`, `'Expand'`, `'Close'`, `'Refresh data'`, `'Loading...'`, `'No entries found'`, `addButtonLabel = 'Add'` | **Medium** |
| `components/layout/GlobalChatSidebar` | `'Conversations'`, `'No conversations yet'`, `'View all conversations'`, `'Unknown Chat Agent'` | **Medium** |
| `pages/ConversationsPage/components/ChatContent` | `"Loading messages..."`, `"How can I help you today?"`, `"Retry"` | **Medium** |

### Well-Implemented i18n (Reference)

These files properly use i18n and should serve as templates:
- `components/layout/Header/Header.tsx` — `useTranslation('header')`
- `components/layout/NotificationPanel/NotificationPanel.tsx` — `useTranslation('notifications')`
- `pages/ConversationsPage/components/ChatHeader/ChatHeader.tsx` — `useTranslation()` with `t('conversations:...')`
- `pages/ConversationsPage/components/ChatSidebar/ChatSidebar.tsx` — `useTranslation()` with `t('conversations:...')`
- `components/common/CommandPalette/CommandPalette.tsx` — `useTranslation('header')` + `useTranslation('common')`
- `pages/DashboardPage/DashboardPage.tsx` — proper i18n usage
- `pages/WidgetDesignerPage/WidgetDesignerPage.tsx` — proper i18n usage

---

## 3. Comment Violations

Project rule: **No comments** except absolutely critical ones.

### Medium — JSDoc Blocks

| File | Description | Severity |
|---|---|---|
| `pages/ConversationsPage/ConversationsPage.tsx` | JSDoc block at file top | **Medium** |
| `pages/TracingDialogDevelopmentPage/TracingDialogDevelopmentPage.tsx` | JSDoc + inline comments | **Medium** |
| `pages/ConversationsPage/hooks/useConversationList.ts` | JSDoc: `/** Hook for managing the conversation list... */` | **Medium** |
| `pages/ConversationsPage/hooks/useConversationTracing.ts` | JSDoc: `/** Hook for managing conversation tracing state... */` | **Medium** |
| `pages/ConversationsPage/hooks/useFileUpload.ts` | JSDoc: `/** Hook for managing drag-and-drop file uploads... */` | **Medium** |
| `components/tracing/TracingVisualDialog/TracingVisualDialog.tsx` | JSDoc block | **Medium** |
| `components/tracing/TracingContext/TracingContext.tsx` | JSDoc block | **Medium** |
| `components/tracing/TracingSidebar/TracingSidebar.tsx` | JSDoc in German | **Medium** |

### Low — Section Separator Comments (`// ====`)

| File | Severity |
|---|---|
| `pages/AutonomousAgentDetailsPage/AutonomousAgentDetailsPage.tsx` | **Low** |
| `components/tracing/TracingVisualDialog/TracingVisualDialog.tsx` | **Low** |
| `components/tracing/TracingContext/TracingContext.tsx` | **Low** |
| `components/tracing/TracingCanvasView/TracingCanvasView.tsx` | **Low** |
| `components/tracing/TracingHierarchyView/TracingHierarchyView.tsx` | **Low** |
| `components/tracing/TracingDataSection/TracingDataSection.tsx` | **Low** |
| `components/tracing/TracingSubHeader/TracingSubHeader.tsx` | **Low** |
| `components/tracing/TracingSidebar/TracingSidebar.tsx` | **Low** |

### Low — Inline Comments

| File | Examples | Severity |
|---|---|---|
| `components/layout/SidebarDataList/SidebarDataList.tsx` | 14+ inline comments: `// Delay showing loading indicator`, `// Filter items`, `// Header`, `// Search Bar` | **Low** |
| `components/layout/GlobalChatSidebar/GlobalChatSidebar.tsx` | `// Don't render`, `// Load conversations` | **Low** |
| `components/dialogs/CreateCredentialDialog/CreateCredentialDialog.tsx` | `/* API Key field */` | **Low** |
| `pages/ConversationsPage/components/ChatInput/ChatInput.tsx` | `// Auto-resize textarea`, `// Focus textarea on mount`, `// Send on Enter`, etc. | **Low** |

**Fix**: Remove all comments. Code should be self-documenting through descriptive variable/function names.

---

## 4. Code Duplication

### Critical — Structural Duplication

| Files | Duplication | Lines Affected | Severity | Fix |
|---|---|---|---|---|
| `TenantSettingsPage.tsx` | Groups/Tools/Credentials/AI Models tabs repeat the same table+CRUD pattern (~150 lines each) | ~600 | **Critical** | Extract generic `TenantEntityTab<T>` accepting config for columns, API calls, and form fields |
| `CreateChatAgentDialog` ↔ `EditChatAgentDialog` | Duplicated constants (`CHAT_AGENT_TYPES`, `N8N_API_VERSIONS`, `FOUNDRY_MODELS`), validation logic, form field structure | ~300 | **Critical** | Extract shared `ChatAgentForm` + constants file |
| `CreateAutonomousAgentDialog` ↔ `EditAutonomousAgentDialog` | Same form structure, validation, N8N config sections | ~200 | **Critical** | Extract shared `AutonomousAgentForm` component |
| `TracingHierarchyView` ↔ `TracingDataSection` | `JsonViewer` component duplicated identically in both files | ~60 | **Critical** | Extract `JsonViewer` to `components/common/` |
| `ChatAgentsPage` ↔ `AutonomousAgentsPage` ↔ `ChatWidgetsPage` | Nearly identical entity list page structure | ~120 each | **Critical** | Extract shared `EntityListPageLayout` |

### Medium — Pattern Duplication

| Pattern | Files | Severity | Fix |
|---|---|---|---|
| `getStatusIcon` helper | `TracingSubHeader`, `TracingCanvasView`, `TracingHierarchyView` | **Medium** | Extract to `components/tracing/utils/getStatusIcon.ts` |
| Edit dialog IAM tab (SegmentedControl + ManageAccessTable + AddPrincipalDialog) | All 6 Edit dialogs | **Medium** | Extract `EntityIAMTab` container |
| Wrapper callbacks (`handleRoleChangeWithTypes`, `handleDeletePrincipalWithTypes`, `handleAddPrincipalsWithRole`) | All 6 Edit dialogs | **Medium** | Move into `useEntityPermissions` hook |
| Tab data (Details + Manage Access SegmentedControl config) | All Edit dialogs | **Medium** | Extract `EditDialogTabs` constant |

---

## 5. Dead Code / Unused Variables

| File | Line(s) | Issue | Severity | Fix |
|---|---|---|---|---|
| `pages/AutonomousAgentsPage` | ~50-60 | `handleShare` and `handlePin` defined but unused | **Medium** | Remove or implement |
| `pages/ChatWidgetsPage` | ~50-60 | `handleShare` defined but unused | **Medium** | Remove or implement |
| `pages/TracingDialogDevelopmentPage` | ~30 | `_isLoading`, `_error` prefixed-unused variables | **Medium** | Remove unused destructured values |
| `components/tracing/TracingHierarchyView` | ~100 | `_maxHeight` unused parameter | **Medium** | Remove parameter |
| `pages/ConversationsPage/components/ChatContent` | ~130 | `const userMessages = message.conversationId ? undefined : undefined; void userMessages;` | **Medium** | Remove dead code entirely |
| `components/dialogs/IntegrationDialog` | ~70 | `_agentId` unused parameter in `buildPutSampleJson` | **Low** | Remove parameter |
| `pages/ConversationsPage/hooks/useConversationList.ts` | ~155 | `resetStreamingState` — empty function body | **Low** | Remove or implement |
| `components/common/ChatPanel` | ~30 | Underscore-prefixed unused prop destructuring | **Low** | Remove from interface |

---

## 6. console.error / console.log Usage

Replace with notification system (`notifications.show()`) or centralized error logging.

| File | Context | Severity |
|---|---|---|
| `pages/DashboardPage` | API error handling | **Medium** |
| `pages/LoginPage` | Auth error handling (2 occurrences) | **Medium** |
| `pages/TracingDialogDevelopmentPage` | Trace loading error | **Medium** |
| `components/layout/Sidebar` | `'Failed to load conversations:'` | **Medium** |
| `components/layout/GlobalChatSidebar` | `'Failed to load conversations:'` | **Medium** |
| `components/common/TagInput` | Tag operation error | **Medium** |
| `components/common/CommandPalette` | `'Search failed:'` | **Medium** |
| `components/dialogs/CreateAutonomousAgentDialog` | Create error | **Medium** |
| `components/dialogs/CreateChatWidgetDialog` | Create error | **Medium** |
| `components/dialogs/CreateCredentialDialog` | Create error | **Medium** |
| `components/dialogs/ShareConversationDialog` | Share error | **Medium** |
| `components/dialogs/EditChatAgentDialog` | Multiple catch blocks | **Medium** |
| `components/dialogs/EditAutonomousAgentDialog` | Multiple catch blocks | **Medium** |
| `components/dialogs/EditCredentialDialog` | Fetch/save errors | **Medium** |
| `components/dialogs/EditChatWidgetDialog` | `'Failed to fetch chat widget:'` | **Medium** |
| `components/dialogs/EditToolDialog` | `'Failed to fetch tool:'` | **Medium** |
| `pages/ConversationsPage/hooks/useChat.ts` | SSE streaming errors | **Medium** |
| `pages/ConversationsPage/hooks/useConversationList.ts` | 5 occurrences across catch blocks | **Medium** |
| `pages/ConversationsPage/hooks/useConversationTracing.ts` | `'Failed to refresh traces:'` | **Medium** |

**Fix**: Replace all `console.error(...)` with:
1. User-facing: `notifications.show({ title: t('error:title'), message: t('error:...'), color: 'red' })`
2. Internal: centralized `errorLogger.capture(error, context)` utility

---

## 7. Inline Styles

All styles should be in CSS Module files using CSS Custom Properties.

| File | Inline Style | Severity |
|---|---|---|
| `pages/AutonomousAgentDetailsPage` | `style={{ minHeight: '60vh' }}` | **Low** |
| `pages/ReActAgentDeveloperPage` | Various inline styles on sub-components | **Low** |
| `pages/DashboardPage` | Inline styles on stat cards | **Low** |
| `pages/NotFoundPage` | Inline style for centering | **Low** |
| `pages/ConversationsPage/components/ChatContent` | `style={{ position: 'relative' }}` | **Low** |
| `pages/ConversationsPage/components/ChatInput` | `textarea.style.height = 'auto'` (imperative DOM) | **Low** |
| `components/layout/Header` | `style={{ cursor: 'pointer' }}`, `style={{ wordBreak: 'break-all' }}` | **Low** |
| `components/layout/SidebarDataList` | `style={{ flex: 1 }}` | **Low** |
| `components/common/DataTableRow` | `style={{ cursor: 'pointer' }}` | **Low** |
| `components/common/DataTable` | Inline styles in Skeleton loader | **Low** |
| `components/common/EntityAvatar` | Inline `backgroundColor` and `color` | **Low** |
| `components/common/ConfirmDeleteDialog` | Inline styles | **Low** |
| `components/dialogs/IntegrationDialog` | `style={{ cursor: 'pointer' }}` on copy buttons | **Low** |
| `components/tracing/TracingVisualDialog` | Extensive `styles` prop on Modal | **Low** |

**Fix**: Move each inline style to the corresponding `.module.css` file using CSS Custom Properties.

---

## 8. eslint-disable Comments

eslint-disable comments indicate design issues that should be resolved, not suppressed.

| File | Rule Disabled | Severity | Fix |
|---|---|---|---|
| `pages/AutonomousAgentDetailsPage` | `react-hooks/exhaustive-deps` | **Medium** | Restructure deps |
| `components/dialogs/EditChatAgentDialog` | `react-hooks/exhaustive-deps` | **Medium** | Fix `initializeFromData` pattern |
| `components/dialogs/EditAutonomousAgentDialog` | `react-hooks/exhaustive-deps` | **Medium** | Same pattern |
| `components/dialogs/EditCredentialDialog` | `react-hooks/exhaustive-deps` | **Medium** | Same pattern |
| `components/dialogs/EditCustomGroupDialog` | `react-hooks/exhaustive-deps` | **Medium** | Same pattern |
| `components/dialogs/EditChatWidgetDialog` | `react-hooks/exhaustive-deps` | **Medium** | Same pattern |
| `components/dialogs/EditToolDialog` | `react-hooks/exhaustive-deps` | **Medium** | Same pattern |

**Fix**: The recurring `eslint-disable` on `initializeFromData` across all Edit dialogs is caused by `form.setValues` in the callback. Solution:

```tsx
const formRef = useRef(form);
formRef.current = form;

const initializeFromData = useCallback((data: T) => {
  formRef.current.setValues({ ... });
}, []);
```

---

## 9. Export Pattern Violations

Project rule: Named exports only with `FC<Props>`. No `export default`.

| File | Issue | Severity |
|---|---|---|
| `components/tracing/TracingSidebar` | `export default` alongside named export | **Low** |
| `components/tracing/TracingSubHeader` | `export default` alongside named export | **Low** |
| `components/tracing/TracingDataSection` | `export default` alongside named export | **Low** |
| `components/tracing/TracingContext` | `export default` alongside named export | **Low** |
| `components/tracing/TraceChatPanel` | `export default` alongside named export | **Low** |

**Fix**: Remove all `export default`. Use only named exports re-exported through barrel `index.ts`.

---

## 10. CSS Custom Properties Violations

| File | Issue | Severity |
|---|---|---|
| `components/common/EntityAvatar` | Hardcoded `backgroundColor`/`color` from hash function | **Low** |
| `components/tracing/TracingVisualDialog` | Direct `document.body.style.overflow` manipulation | **Low** |
| `components/dialogs/IntegrationDialog` | Inline `styles` prop with font-size var (should be in CSS Module) | **Low** |

---

## 11. Miscellaneous Issues

### Direct DOM Manipulation

| File | Issue | Severity |
|---|---|---|
| `components/tracing/TracingVisualDialog` | `document.body.style.overflow = 'hidden'/'auto'` | **Medium** |
| `pages/ConversationsPage/components/ChatInput` | Imperative `textarea.style.height` changes | **Medium** |

**Fix**: Use Mantine's `ScrollArea` or CSS `field-sizing: content` for textarea auto-resize.

### Performance Issue

| File | Issue | Severity |
|---|---|---|
| `components/tracing/TracingContext` | `JSON.stringify` comparison for trace updates on every render | **Medium** |

**Fix**: Memoize serialized value or use deep comparison utility.

### Feature Parity Gap

| File | Issue | Severity |
|---|---|---|
| `pages/ChatWidgetsPage` | Missing `useFavorites` integration (present in other entity pages) | **Low** |

### forwardRef Pattern

| File | Issue | Severity |
|---|---|---|
| `pages/ConversationsPage/components/ChatInput` | Uses `forwardRef` instead of `FC<Props>` | **Low** |

**Note**: Acceptable since `forwardRef` is needed to expose `handleFileDrop`. Consider React 19 ref forwarding when upgrading.

---

## Top 10 Priority Actions

1. **Decompose `TenantSettingsPage.tsx`** (1998 lines) — Extract 7 tab components + shared table pattern
2. **Add i18n to ALL dialog components** — ~20 dialog files have zero i18n; create namespaced translation files per dialog
3. **Fix hardcoded German strings** — 7 files contain hardcoded German text (NotFoundPage, LoginTokenPage, TagInput, TracingSubHeader, TracingHierarchyView, TracingCanvasView, TracingDialogDevelopmentPage)
4. **Decompose `TracingCanvasView.tsx`** (975 lines) — Extract nodes, edges, and layout hooks
5. **Decompose `EditChatAgentDialog.tsx`** (937 lines) — Extract form sections, share with CreateChatAgentDialog
6. **Extract shared `JsonViewer`** — Duplicated in TracingHierarchyView and TracingDataSection
7. **Remove all `console.error`** — 19 files; replace with notification system
8. **Remove all comments** — 20+ files contain JSDoc, section separators, or inline comments
9. **Fix all `eslint-disable` hooks deps** — 7 Edit dialogs share same `initializeFromData` pattern issue; use `formRef` pattern
10. **Extract shared entity page patterns** — ChatAgentsPage/AutonomousAgentsPage/ChatWidgetsPage are nearly identical; Create↔Edit dialog pairs duplicate forms

---
---

# Part 2: i18n Setup & Test Coverage Review (2026-02-09)

---

## 12. i18n SETUP ANALYSIS

### 12.1 Namespace Registration & Consistency

| Check | Status | Notes |
|-------|--------|-------|
| All 13 JSON files imported in `index.ts` | ✅ PASS | common, dashboard, login, header, conversations, settings, notifications, tracing, credentials, token, widgetDesigner, reactAgent, sidebar |
| All 13 JSON files imported in `i18nForTests.ts` | ✅ PASS | Same 13 namespaces |
| `ns` array matches imports | ✅ PASS | All 13 listed in prod config |
| `i18nForTests.ts` omits `LanguageDetector` | ✅ CORRECT | Test config uses fixed `lng: 'en-US'` |
| `defaultNS: 'common'` consistent | ✅ PASS | Both files |
| `i18nForTests.ts` missing `ns` array | ⚠️ MINOR | Not required since resources object defines them, but inconsistent with prod config |
| German strings in JSON files | ✅ NONE | All 13 locale files contain only English |

### 12.2 Unused i18n Keys

Keys defined in JSON but never referenced via `t()` in any `.tsx`/`.ts` file:

| # | Namespace | Key | Severity |
|---|-----------|-----|----------|
| 1 | `settings` | **ALL 10 KEYS** (`title`, `general`, `iam`, `groups`, `credentials`, `aiModels`, `tools`, `billing`, `newApiKey`, `keepCurrentValue`) | **HIGH** — entire namespace unused; `TenantSettingsPage` imports no `useTranslation('settings')` |
| 2 | `common` | `deleteConfirmTitle` | **MEDIUM** — should replace hardcoded `"Confirm Delete"` in ConfirmDeleteDialog |
| 3 | `common` | `deleteConfirmMessage` | **MEDIUM** — should replace hardcoded delete messages in ConfirmDeleteDialog |
| 4 | `common` | `confirm` | LOW |
| 5 | `common` | `yes` | LOW |
| 6 | `common` | `no` | LOW |
| 7 | `common` | `noData` | LOW |
| 8 | `common` | `retry` | LOW |
| 9 | `common` | `back` | LOW |
| 10 | `common` | `next` | LOW |
| 11 | `common` | `actions` | LOW |
| 12 | `common` | `name` | LOW |
| 13 | `common` | `description` | LOW |
| 14 | `common` | `status` | LOW |
| 15 | `common` | `active` | LOW |
| 16 | `common` | `inactive` | LOW |
| 17 | `common` | `createdAt` | LOW |
| 18 | `common` | `updatedAt` | LOW |
| 19 | `common` | `tags` | LOW |
| 20 | `common` | `duplicate` | LOW — `handleDuplicate` in `useEntityList` is a no-op stub |
| 21 | `common` | `pin` | LOW |
| 22 | `common` | `unpin` | LOW |
| 23 | `common` | `favorite` | LOW |
| 24 | `common` | `unfavorite` | LOW |
| 25 | `common` | `messageCopied` | LOW |
| 26 | `common` | `deleteFailed` | LOW |
| 27 | `common` | `createFailed` | LOW |
| 28 | `common` | `updateFailed` | LOW |
| 29 | `common` | `loadFailed` | LOW |
| 30 | `common` | `selectAll` | LOW |
| 31 | `common` | `deselectAll` | LOW |
| 32 | `common` | `save` | LOW |
| 33 | `common` | `edit` | LOW |
| 34 | `common` | `create` | LOW |
| 35 | `common` | `close` | LOW |
| 36 | `notifications` | `noNotificationsDescription` | LOW |
| 37 | `notifications` | `markAsRead` | LOW |
| 38 | `notifications` | `minutesAgo` | LOW — only `*Short` variants used |
| 39 | `notifications` | `hoursAgo` | LOW |
| 40 | `notifications` | `daysAgo` | LOW |

**Total: ~40 unused keys.** The `settings` namespace (10 keys) is entirely unused.

### 12.3 Hardcoded Strings in ConfirmDeleteDialog (i18n-Critical)

| File | Line | String | Fix |
|------|------|--------|-----|
| `ConfirmDeleteDialog.tsx` | L23 | `title = 'Confirm Delete'` | Use `t('common:deleteConfirmTitle')` |
| `ConfirmDeleteDialog.tsx` | L28 | `confirmButtonText = 'Delete'` | Use `t('common:delete')` |
| `ConfirmDeleteDialog.tsx` | L37 | `"Are you sure you want to delete"` | Use `t('common:deleteConfirmMessage')` |
| `ConfirmDeleteDialog.tsx` | L77 | `"This action cannot be undone."` | Add new key `common:actionCannotBeUndone` |
| `ConfirmDeleteDialog.tsx` | L93 | `"Cancel"` | Use `t('common:cancel')` |
| `ConfirmDeleteDialog.tsx` | L101 | `"Cancel"` | Use `t('common:cancel')` |

This is **HIGH** severity because ConfirmDeleteDialog is used across 12+ locations in the app.

### 12.4 i18n Architecture Issues

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| 1 | `settings` namespace defined but never consumed | **HIGH** | Either i18n-ify TenantSettingsPage or remove the unused JSON |
| 2 | Mixed flat vs. nested keys | LOW | `reactAgent.json` and `widgetDesigner.json` use nested keys (`sections.aiModels`, `properties.label`); all others use flat keys. Pick one style. |
| 3 | Only `en-US` locale exists | LOW | No structure for additional locales. Document single-locale strategy or prepare for expansion. |
| 4 | ConfirmDeleteDialog uses props for text instead of internal i18n | **MEDIUM** | Component should call `useTranslation('common')` internally rather than relying on caller props |

---

## 13. TEST COVERAGE

### 13.1 Test Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| `setup.ts` | ✅ Good | `matchMedia` mock, `ResizeObserver` mock, MSW server lifecycle |
| `utils.tsx` | ✅ Good | `renderWithProviders` wraps `MantineProvider` + `I18nextProvider` + `MemoryRouter` |
| MSW mock handlers | ✅ Good | Covers `/v1/me`, `/v1/tenants/:id/chat-agents`, `/autonomous-agents`, `/chat-widgets`, `/conversations`, `/ai-capabilities` |
| `i18nForTests.ts` | ✅ Good | Deterministic `lng: 'en-US'`, no LanguageDetector |

### 13.2 Existing Test Quality

| Test File | Tests | Quality | Notes |
|-----------|-------|---------|-------|
| `i18n.test.tsx` | 8 tests | **GOOD** | Tests 7 namespaces, interpolation, missing key fallback. Missing: `conversations`, `widgetDesigner`, `reactAgent`, `sidebar`, `settings` namespaces |
| `dashboard.test.tsx` | 8 tests | **GOOD** | Loading state, welcome message, tenant subtitle, stat cards, favorites/recent sections, German string check |
| `header.test.tsx` | 6 tests | **GOOD** | Tenant name, no-tenant fallback, search readonly, notification badge, German string check, user display name |
| `setup.test.tsx` | 2 tests | **LOW** | Just verifies test framework works, minimal value |

**Strengths**: Tests verify real rendered content (not just "renders without crashing"), check for German text regression, use proper mock patterns.  
**Weaknesses**: Zero interaction tests (no `userEvent.click`, `userEvent.type`), zero API integration tests (MSW handlers exist but untested).

### 13.3 Test Coverage Matrix: Pages (1/14 = 7%)

| Page | Tested? | Complexity | Priority |
|------|---------|------------|----------|
| `DashboardPage` | ✅ | Medium | — |
| `LoginPage` | ❌ | Medium | Medium |
| `LoginTokenPage` | ❌ | Medium | Low |
| `ConversationsPage` | ❌ | **Very High** | **HIGH** |
| `ChatAgentsPage` | ❌ | High | **HIGH** |
| `AutonomousAgentsPage` | ❌ | High | **HIGH** |
| `AutonomousAgentDetailsPage` | ❌ | **Very High** | **HIGH** |
| `ChatWidgetsPage` | ❌ | High | Medium |
| `TenantSettingsPage` | ❌ | **Very High** (1998 lines) | **HIGH** |
| `WidgetDesignerPage` | ❌ | High | Medium |
| `ReActAgentDeveloperPage` | ❌ | High | Medium |
| `EmbedChatPage` | ❌ | Low | Low |
| `TracingDialogDevelopmentPage` | ❌ | Medium | Low |
| `NotFoundPage` | ❌ | Low | Low |

### 13.4 Test Coverage: Layout Components (1/5 = 20%)

| Component | Tested? | Priority |
|-----------|---------|----------|
| `Header` | ✅ | — |
| `Sidebar` | ❌ | **HIGH** |
| `MainLayout` | ❌ | Low |
| `NotificationPanel` | ❌ | Medium |
| `GlobalChatSidebar` | ❌ | Medium |

### 13.5 Test Coverage: Common Components (0/19 = 0%)

| Component | Tested? | Priority |
|-----------|---------|----------|
| `DataTable` | ❌ | **HIGH** — used on every entity list page |
| `CommandPalette` | ❌ | **HIGH** — keyboard navigation, search |
| `ConfirmDeleteDialog` | ❌ | **HIGH** — used across 12+ locations |
| `ManageAccessTable` | ❌ | Medium |
| `ManageTenantAccessTable` | ❌ | Medium |
| `ChatPanel` | ❌ | Medium |
| `AddPrincipalDialog` | ❌ | Medium |
| `EntityDetailsForm` | ❌ | Medium |
| `TracesTable` | ❌ | Medium |
| `TagInput` | ❌ | Medium |
| `SecretField` | ❌ | Low |
| `Breadcrumbs` | ❌ | Low |
| `DelayedTooltip` | ❌ | Low |
| `DetailPageTabs` | ❌ | Low |
| `EditRolesDialog` | ❌ | Low |
| `EntityAvatar` | ❌ | Low |
| `GenerateWithAIButton` | ❌ | Low |
| `MarkdownRenderer` | ❌ | Low |
| `PageHeader` | ❌ | Low |

### 13.6 Test Coverage: Dialog Components (0/18 = 0%)

All 18 dialog components (7 Create + 6 Edit + AIModelDialog + AnalyzeErrorDialog + IntegrationDialog + SearchConversationsDialog + ShareConversationDialog) have **zero tests**.

### 13.7 Test Coverage: Tracing Components (0/9 = 0%)

All 9 tracing components have **zero tests**.

### 13.8 Test Coverage: Hooks (0/3 = 0%)

| Hook | Tested? | Lines | Priority |
|------|---------|-------|----------|
| `useEntityList` | ❌ | 376 | **HIGH** — complex state, pagination, search debounce, sort, filter |
| `useEntityPermissions` | ❌ | 234 | **HIGH** — CRUD operations on permissions |
| `useKeyboardShortcuts` | ❌ | 69 | Medium |

### 13.9 Test Coverage: Contexts (0/10 = 0%)

All 10 context providers have **zero tests**.

---

## 14. HOOK IMPLEMENTATION REVIEW

### 14.1 `useEntityList.ts` (376 lines)

| # | Issue | Severity | Line(s) | Fix |
|---|-------|----------|---------|-----|
| 1 | No `AbortController` for fetch requests | **MEDIUM** | `fetchEntities` callback (~L145) | If tenant changes mid-request, stale data can overwrite fresh. Add `AbortController`, cancel on re-fetch/unmount. |
| 2 | `tagMapRef` never clears on tenant change | LOW | L122 | Tags from previous tenant could leak into new tenant context. Clear map when `selectedTenant` changes. |
| 3 | `handleDuplicate` is a no-op stub | LOW | L310 | `void _id;` — remove from return value or implement |
| 4 | `rawDataRef` never cleaned on unmount | LOW | L127 | Potential memory leak with large datasets |
| 5 | Missing error notification to user | LOW | catch blocks | Only sets `error` state and `console.error`; no toast/notification |

### 14.2 `useEntityPermissions.ts` (234 lines)

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| 1 | `handleAddPrincipals` uses sequential `await` in loop | **MEDIUM** | Use `Promise.all()` or `Promise.allSettled()` for parallel permission grants |
| 2 | Silent error handling in `handleRoleChange` | LOW | Catches error but shows no user notification; only re-fetches |
| 3 | No abort/cancellation on unmount | LOW | State updates after unmount will warn in strict mode |

### 14.3 `useKeyboardShortcuts.ts` (69 lines)

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| 1 | No `event.isComposing` check | LOW | Could fire shortcuts during CJK IME composition. Add `if (event.isComposing) return;` |
| 2 | Callers may pass unstable `handlers` object | LOW | Document that callers should memoize the handlers object or wrap in `useMemo` |

### 14.4 Missing Custom Hooks (Repeated Logic)

| # | Suggested Hook | Where Logic Repeats |
|---|---------------|---------------------|
| 1 | `useAsyncAction` (loading + error + try/catch) | All dialog forms, entity pages, settings tabs |
| 2 | `useClipboardWithNotification` | LoginTokenPage, ChatHeader, IntegrationDialog, SecretField |
| 3 | `usePaginatedList` (extracted from useEntityList) | useEntityList pagination logic could be shared with TracesTable |

---

## 15. OVERALL SCORES (i18n + Tests + Hooks)

| Area | Score | Comment |
|------|-------|---------|
| **i18n key completeness** | 5/10 | ~40 unused keys, `settings` namespace entirely unused, many keys defined speculatively |
| **i18n coverage in code** | 3/10 | ConfirmDeleteDialog + most dialogs + tracing components + TenantSettingsPage have hardcoded strings |
| **No German in JSON** | 10/10 | All locale files are clean English |
| **Test coverage (breadth)** | 2/10 | 3/73 components tested, 0/3 hooks, 0/10 contexts |
| **Test quality (depth)** | 7/10 | Existing tests are well-written and meaningful |
| **Test infrastructure** | 8/10 | Good MSW setup, proper provider wrappers, clean lifecycle |
| **Hook quality** | 7/10 | Well-structured, proper memoization. Missing abort controllers. |

### Top 5 Priority Actions (i18n + Tests)

1. **[HIGH] i18n ConfirmDeleteDialog**: Add `useTranslation('common')` — 6 hardcoded strings, used in 12+ locations
2. **[HIGH] i18n TenantSettingsPage**: Either use the existing `settings` namespace or audit & i18n-ify the page (1998 lines of likely hardcoded text)
3. **[HIGH] Test `useEntityList` hook**: 376 lines of complex state management with zero tests — pagination, debounced search, sort, filter, CRUD all untested
4. **[HIGH] Test `DataTable` + `ConfirmDeleteDialog`**: Most-reused common components, zero tests
5. **[MEDIUM] Add AbortController to `useEntityList.fetchEntities`**: Prevents stale data on rapid tenant switching
6. **[MEDIUM] Clean up ~40 unused i18n keys**: Remove or wire up to actual UI code
7. **[MEDIUM] Add i18n namespace tests**: `i18n.test.tsx` tests 7/13 namespaces — add tests for `conversations`, `widgetDesigner`, `reactAgent`, `sidebar`, `settings`, `notifications`