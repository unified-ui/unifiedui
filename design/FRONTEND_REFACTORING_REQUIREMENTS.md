# Frontend Refactoring - Requirements Document v1.0

**Project**: unified-ui Frontend Service  
**Version**: 1.0  
**Date**: 27. January 2026  
**Status**: Draft - Ready for Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Scope & Affected Components](#2-scope--affected-components)
3. [Requirements by Area](#3-requirements-by-area)
   - [3.1 Sidebar Component](#31-sidebar-component)
   - [3.2 Chat Agents Page (Applications Page)](#32-chat-agents-page-applications-page)
   - [3.3 Autonomous Agents Page](#33-autonomous-agents-page)
   - [3.4 Tenant Settings Page](#34-tenant-settings-page)
   - [3.5 Internationalization (i18n)](#35-internationalization-i18n)
4. [Implementation Plan](#4-implementation-plan)
5. [Acceptance Criteria](#5-acceptance-criteria)
6. [Risk Assessment & Mitigation](#6-risk-assessment--mitigation)

---

## 1. Executive Summary

This document outlines the requirements for a comprehensive frontend refactoring initiative targeting UI/UX improvements, consistency enhancements, and full internationalization to English across the unified-ui frontend service.

### Key Objectives

1. **Consistency**: Ensure all dialogs, sidebars, and components follow the same design patterns
2. **Usability**: Fix interaction issues (stopPropagation, tooltip for truncated text)
3. **Internationalization**: Convert all German text to English
4. **State Management**: Optimize data fetching and caching behavior

---

## 2. Scope & Affected Components

### Files to Modify

| Component | File Path | Priority |
|-----------|-----------|----------|
| Sidebar | `src/components/layout/Sidebar/Sidebar.tsx` | High |
| SidebarDataList | `src/components/layout/Sidebar/SidebarDataList.tsx` | High |
| GlobalChatSidebar | `src/components/layout/GlobalChatSidebar/GlobalChatSidebar.tsx` | High |
| ApplicationsPage | `src/pages/ApplicationsPage/ApplicationsPage.tsx` | High |
| AutonomousAgentsPage | `src/pages/AutonomousAgentsPage/AutonomousAgentsPage.tsx` | Medium |
| TenantSettingsPage | `src/pages/TenantSettingsPage/TenantSettingsPage.tsx` | Medium |
| CreateApplicationDialog | `src/components/dialogs/CreateApplicationDialog.tsx` | Medium |
| CreateAutonomousAgentDialog | `src/components/dialogs/CreateAutonomousAgentDialog.tsx` | Medium |
| CreateCustomGroupDialog | `src/components/dialogs/CreateCustomGroupDialog.tsx` | Medium |
| CreateToolDialog | `src/components/dialogs/CreateToolDialog.tsx` | Medium |
| EditCustomGroupDialog | `src/components/dialogs/EditCustomGroupDialog/EditCustomGroupDialog.tsx` | Medium |
| DataTableRow | `src/components/common/DataTable/DataTableRow.tsx` | Medium |
| All Dialogs | Various | Low (i18n) |

### New Files to Create

| Component | File Path | Description |
|-----------|-----------|-------------|
| TracesPage | `src/pages/TracesPage/TracesPage.tsx` | Placeholder page for Traces |

---

## 3. Requirements by Area

### 3.1 Sidebar Component

#### REQ-SB-001: Conversations Sidebar Redesign

**Current State:**
- When hovering over "Conversations" nav item, a special `GlobalChatSidebar` appears
- This sidebar has a different design (title + subtitle per item) compared to other data lists

**Required Change:**
- Replace `GlobalChatSidebar` with standard `SidebarDataList` component
- Extend `SidebarDataList` to support **title AND subtitle** for items
- Keep the visual style consistent with other sidebars (Applications, Autonomous Agents)
- Display conversation name (title) and associated application name (subtitle)

**Affected Files:**
- `src/components/layout/Sidebar/Sidebar.tsx`
- `src/components/layout/Sidebar/SidebarDataList.tsx`
- `src/components/layout/GlobalChatSidebar/GlobalChatSidebar.tsx` (potentially remove)

**Technical Implementation:**

1. Extend `DataListItem` interface:
```typescript
export interface DataListItem {
  id: string;
  name: string;
  subtitle?: string;  // NEW: Optional subtitle
  link: string;
  icon?: React.ReactNode;
}
```

2. Update `SidebarDataList` to render subtitle when present:
```tsx
{/* Item rendering */}
<Stack gap={2}>
  <Text size="sm" truncate>{item.name}</Text>
  {item.subtitle && (
    <Text size="xs" c="dimmed" truncate>{item.subtitle}</Text>
  )}
</Stack>
```

3. Add "conversations" to `EntityType`:
```typescript
type EntityType = 'applications' | 'autonomous-agents' | 'chat-widgets' | 'conversations';
```

4. Create conversation data fetching in `SidebarDataContext`

---

#### REQ-SB-002: Persist Expanded State in LocalStorage

**Current State:**
- The `SidebarDataList` can be expanded (wider panel)
- Expanded state is not persisted across sessions

**Required Change:**
- Persist expanded state in localStorage per entity type
- Restore expanded state when component mounts

**Implementation:**

```typescript
const EXPAND_STORAGE_KEY = 'unified-ui:sidebar-expanded';

// On mount - read from localStorage
useEffect(() => {
  const stored = localStorage.getItem(EXPAND_STORAGE_KEY);
  if (stored) {
    const expandedStates = JSON.parse(stored);
    if (activeEntity && expandedStates[activeEntity]) {
      setIsDataListExpanded(true);
    }
  }
}, [activeEntity]);

// On expand toggle - persist to localStorage
const handleToggleExpand = useCallback(() => {
  setIsDataListExpanded(prev => {
    const newValue = !prev;
    const stored = localStorage.getItem(EXPAND_STORAGE_KEY);
    const expandedStates = stored ? JSON.parse(stored) : {};
    if (activeEntity) {
      expandedStates[activeEntity] = newValue;
      localStorage.setItem(EXPAND_STORAGE_KEY, JSON.stringify(expandedStates));
    }
    return newValue;
  });
}, [activeEntity]);
```

**Affected Files:**
- `src/components/layout/Sidebar/Sidebar.tsx`

---

#### REQ-SB-003: Add Traces Navigation Item

**Current State:**
- No "Traces" navigation item in the sidebar

**Required Change:**
- Add "Traces" navigation item at the bottom of the main nav section (after Autonomous Agents)
- No hover data list for this item (just direct navigation)
- Link to `/traces` (placeholder page for now - 404 or dedicated page)

**Implementation:**

1. Update `mainNavItemsBottom` array:
```typescript
const mainNavItemsBottom: NavItem[] = [
  { icon: IconTool, label: 'ReACT-Agent\nDevelopment', path: '/tenant-settings?tab=tools' },
  { icon: IconBrandWechat, label: 'Chat\nWidgets', path: '/chat-widgets', hasDataList: true, entityType: 'chat-widgets' },
  { icon: IconHistory, label: 'Traces', path: '/traces', hasDataList: false }, // NEW
];
```

2. Create placeholder page:
```typescript
// src/pages/TracesPage/TracesPage.tsx
export const TracesPage: FC = () => {
  return (
    <MainLayout>
      <PageContainer>
        <PageHeader title="Traces" description="Coming soon..." />
        <Alert color="blue">This feature is under development.</Alert>
      </PageContainer>
    </MainLayout>
  );
};
```

3. Add route in router configuration

**Affected Files:**
- `src/components/layout/Sidebar/Sidebar.tsx`
- `src/pages/TracesPage/TracesPage.tsx` (new)
- `src/routes/index.tsx`

---

### 3.2 Chat Agents Page (Applications Page)

#### REQ-CA-001: Fix stopPropagation on Interactive Elements

**Current State:**
- Clicking on the status toggle in DataTable triggers row navigation
- Clicking on context menu items triggers row navigation
- Expected: Interactive elements should NOT trigger row click

**Required Change:**
- Add `onClick={(e) => e.stopPropagation()}` to:
  - Status Switch component
  - Context menu ActionIcon (three dots)
  - All menu items

**Affected Files:**
- `src/components/common/DataTable/DataTableRow.tsx`

**Implementation:**

```tsx
// Status Switch - prevent row click
<Switch
  checked={item.isActive}
  onChange={(e) => {
    e.stopPropagation(); // Stop propagation
    onStatusChange?.(item.id, e.target.checked);
  }}
  onClick={(e) => e.stopPropagation()} // Also stop on click
/>

// Context Menu ActionIcon
<Menu position="bottom-end" withArrow>
  <Menu.Target>
    <ActionIcon 
      variant="subtle" 
      onClick={(e) => e.stopPropagation()} // Stop propagation
    >
      <IconDots size={16} />
    </ActionIcon>
  </Menu.Target>
  <Menu.Dropdown onClick={(e) => e.stopPropagation()}>
    {/* Menu items */}
  </Menu.Dropdown>
</Menu>
```

---

#### REQ-CA-002: Context Menu Opens Correct Dialog

**Current State:**
- Clicking "Edit" in context menu navigates to conversation (due to missing stopPropagation)

**Required Change:**
- "Edit" should open the Edit dialog (via URL params: `?editItemId={id}&tab=details`)
- "Manage Access" should open Edit dialog with access tab (via URL params: `?editItemId={id}&tab=access`)

**Note:** This is mostly fixed by REQ-CA-001. Ensure handlers use `setSearchParams` correctly.

---

#### REQ-CA-003: Add Dividers Around Type-Specific Fields in Create Dialog

**Current State:**
- CreateApplicationDialog has a Divider ABOVE type-specific fields
- No Divider BELOW type-specific fields (before Description)

**Required Change:**
- Add Divider after type-specific fields section, before Description field
- This creates a visual grouping for type-specific configuration

**Visual Structure:**
```
[Name]
[Type]
[Tags]
─────────────── (Divider)
[N8N/Foundry specific fields]
─────────────── (Divider) ← NEW
[Description]
[Buttons]
```

**Affected Files:**
- `src/components/dialogs/CreateApplicationDialog.tsx`
- `src/components/dialogs/EditApplicationDialog/EditApplicationDialog.tsx`

**Implementation:**
```tsx
{/* Type-specific fields */}
{values.type && <Divider my="md" />}
{/* ...type specific fields... */}
{values.type && <Divider my="md" />}  {/* NEW */}

{/* Description - always at the end */}
<Textarea
  label="Description"
  {...form.getInputProps('description')}
/>
```

---

#### REQ-CA-004: Tooltip for Truncated Name/Description

**Current State:**
- Name and description are truncated with ellipsis when too long
- No way for users to see the full text

**Required Change:**
- Wrap truncated text in Mantine `Tooltip`
- Show full text on hover
- Only show tooltip if text is actually truncated (text-overflow applied)

**Affected Files:**
- `src/components/common/DataTable/DataTableRow.tsx`

**Implementation:**

```tsx
import { Tooltip } from '@mantine/core';

// For name
<Tooltip 
  label={item.name} 
  disabled={!item.name || item.name.length < 30}
  multiline
  maw={300}
>
  <Text fw={600} size="md" truncate className={classes.itemName}>
    {item.name}
  </Text>
</Tooltip>

// For description
{item.description && (
  <Tooltip 
    label={item.description} 
    disabled={!item.description || item.description.length < 50}
    multiline
    maw={400}
  >
    <Text size="sm" c="dimmed" truncate className={classes.itemDescription}>
      {item.description}
    </Text>
  </Tooltip>
)}
```

---

### 3.3 Autonomous Agents Page

#### REQ-AA-001: Add Dividers in Create Dialog

**Same as REQ-CA-003**

**Affected Files:**
- `src/components/dialogs/CreateAutonomousAgentDialog.tsx`
- `src/components/dialogs/EditAutonomousAgentDialog/EditAutonomousAgentDialog.tsx`

---

#### REQ-AA-002: Tooltip for Truncated Text

**Same as REQ-CA-004** - Apply to AutonomousAgentsPage DataTable

---

### 3.4 Tenant Settings Page

#### REQ-TS-001: Fix Create Custom Group Dialog Height

**Current State:**
- Create Custom Group dialog appears too high on the screen

**Required Change:**
- Ensure modal is vertically centered (like other dialogs)
- Use consistent modal props

**Affected Files:**
- `src/components/dialogs/CreateCustomGroupDialog.tsx`

**Implementation:**
```tsx
<Modal
  opened={opened}
  onClose={handleClose}
  title="Create Custom Group"
  size="md"
  centered  // ADD THIS
>
```

---

#### REQ-TS-002: Fix Edit Custom Group Dialog - Prevent Refetch on Tab Switch

**Current State:**
- Switching tabs in EditCustomGroupDialog causes data to be refetched
- Other edit dialogs preserve state when switching tabs

**Required Change:**
- Load data ONCE when dialog opens
- Do NOT reload when switching between tabs
- Keep form state and principals state in memory

**Root Cause Analysis:**
The issue is in `EditCustomGroupDialog.tsx`:
- `fetchCustomGroup` is called in useEffect that depends on `opened` AND `activeTab`
- Should only depend on `opened` and `customGroupId`

**Affected Files:**
- `src/components/dialogs/EditCustomGroupDialog/EditCustomGroupDialog.tsx`

**Implementation:**

```tsx
// BEFORE (problematic)
useEffect(() => {
  if (opened && customGroupId) {
    fetchCustomGroup();
    fetchPrincipals();
  }
}, [opened, customGroupId, activeTab]); // activeTab causes refetch!

// AFTER (correct)
useEffect(() => {
  if (opened && customGroupId) {
    fetchCustomGroup();
  }
}, [opened, customGroupId]); // Only fetch when dialog opens

// Separate effect for principals (only once)
useEffect(() => {
  if (opened && customGroupId && !principalsFetched) {
    fetchPrincipals();
  }
}, [opened, customGroupId, principalsFetched]);
```

---

#### REQ-TS-003: Fix Create Tool Dialog Height

**Same as REQ-TS-001**

**Affected Files:**
- `src/components/dialogs/CreateToolDialog.tsx`

---

#### REQ-TS-004: Different Badge Colors for Tool Types

**Current State:**
- All tool types have the same badge color in the table

**Required Change:**
- MCP_SERVER → Blue badge
- OPENAPI_DEFINITION → Green badge

**Affected Files:**
- `src/pages/TenantSettingsPage/TenantSettingsPage.tsx` (Tools table section)

**Implementation:**

```tsx
const TOOL_TYPE_COLORS: Record<string, string> = {
  MCP_SERVER: 'blue',
  OPENAPI_DEFINITION: 'green',
};

// In table render:
<Badge color={TOOL_TYPE_COLORS[tool.type] || 'gray'}>
  {tool.type.replace(/_/g, ' ')}
</Badge>
```

---

#### REQ-TS-005: Reorder Tools Table Columns

**Current State:**
- Column order: Name | Type | Actions

**Required Change:**
- Column order: Name | Description | Type | Actions
- Make Type column narrower

**Affected Files:**
- `src/pages/TenantSettingsPage/TenantSettingsPage.tsx`

---

#### REQ-TS-006: Add Type Filter to Tools List

**Current State:**
- Only search filter available

**Required Change:**
- Add type filter dropdown next to search
- Options: "All", "MCP Server", "OpenAPI Definition"

**Affected Files:**
- `src/pages/TenantSettingsPage/TenantSettingsPage.tsx`

**Implementation:**

```tsx
const [toolsTypeFilter, setToolsTypeFilter] = useState<string | null>(null);

// Filter logic
const filteredTools = useMemo(() => {
  let result = tools;
  if (toolsTypeFilter) {
    result = result.filter(t => t.type === toolsTypeFilter);
  }
  // ... search filter ...
  return result;
}, [tools, toolsTypeFilter, debouncedToolsSearch]);

// UI
<Group gap="sm">
  <TextInput
    placeholder="Search tools..."
    leftSection={<IconSearch size={16} />}
    value={toolsSearch}
    onChange={(e) => setToolsSearch(e.target.value)}
  />
  <Select
    placeholder="All Types"
    clearable
    data={[
      { value: 'MCP_SERVER', label: 'MCP Server' },
      { value: 'OPENAPI_DEFINITION', label: 'OpenAPI Definition' },
    ]}
    value={toolsTypeFilter}
    onChange={setToolsTypeFilter}
    style={{ width: 180 }}
  />
</Group>
```

---

### 3.5 Internationalization (i18n)

#### REQ-I18N-001: Convert All German Text to English

**Current State:**
- Mixed language - some components use German text
- Validation messages, labels, placeholders in German

**Required Change:**
- Convert ALL user-facing text to English
- This includes:
  - Form labels
  - Validation messages
  - Button text
  - Placeholder text
  - Error messages
  - Toast notifications

**Affected Files (non-exhaustive):**
- All dialogs in `src/components/dialogs/`
- All pages in `src/pages/`
- Common components

**Examples of Required Changes:**

| German | English |
|--------|---------|
| "Name ist erforderlich" | "Name is required" |
| "Beschreibung darf maximal 2000 Zeichen lang sein" | "Description must be less than 2000 characters" |
| "Typ ist erforderlich" | "Type is required" |
| "Erstellen" | "Create" |
| "Abbrechen" | "Cancel" |
| "Löschen bestätigen" | "Confirm Delete" |
| "Speichern" | "Save" |
| "Schließen" | "Close" |

**Systematic Approach:**
1. Search codebase for German patterns: `ist erforderlich`, `darf maximal`, `Zeichen`, etc.
2. Replace each occurrence with English equivalent
3. Verify no German remains with search

---

## 4. Implementation Plan

### Phase 1: Critical Fixes (Day 1)

| # | Task | REQ | Estimated Effort |
|---|------|-----|------------------|
| 1 | Fix stopPropagation in DataTableRow | REQ-CA-001 | 30 min |
| 2 | Add tooltips for truncated text | REQ-CA-004 | 45 min |
| 3 | Persist sidebar expand state | REQ-SB-002 | 30 min |

### Phase 2: Dialog Improvements (Day 1-2)

| # | Task | REQ | Estimated Effort |
|---|------|-----|------------------|
| 4 | Add dividers in Create/Edit Application dialogs | REQ-CA-003 | 30 min |
| 5 | Add dividers in Create/Edit AutoAgent dialogs | REQ-AA-001 | 30 min |
| 6 | Fix dialog centering (CustomGroup, Tool) | REQ-TS-001, REQ-TS-003 | 20 min |
| 7 | Fix EditCustomGroupDialog refetch | REQ-TS-002 | 45 min |

### Phase 3: Settings Page Improvements (Day 2)

| # | Task | REQ | Estimated Effort |
|---|------|-----|------------------|
| 8 | Tool type badge colors | REQ-TS-004 | 20 min |
| 9 | Reorder tools table columns | REQ-TS-005 | 20 min |
| 10 | Add type filter to tools | REQ-TS-006 | 45 min |

### Phase 4: Sidebar & Navigation (Day 2-3)

| # | Task | REQ | Estimated Effort |
|---|------|-----|------------------|
| 11 | Redesign Conversations sidebar | REQ-SB-001 | 2 hours |
| 12 | Add Traces nav item + page | REQ-SB-003 | 1 hour |

### Phase 5: Internationalization (Day 3)

| # | Task | REQ | Estimated Effort |
|---|------|-----|------------------|
| 13 | Convert all text to English | REQ-I18N-001 | 2-3 hours |

**Total Estimated Effort: ~2-3 days**

---

## 5. Acceptance Criteria

### Sidebar

- [ ] **AC-SB-001**: Hovering "Conversations" shows `SidebarDataList` with title + subtitle
- [ ] **AC-SB-002**: Sidebar expanded state persists after page reload
- [ ] **AC-SB-003**: "Traces" nav item visible and links to `/traces`

### Chat Agents Page

- [ ] **AC-CA-001**: Clicking status toggle does NOT navigate to conversation
- [ ] **AC-CA-002**: Context menu Edit opens edit dialog, not navigation
- [ ] **AC-CA-003**: Create dialog has dividers above AND below type-specific fields
- [ ] **AC-CA-004**: Hovering truncated name/description shows full text tooltip

### Autonomous Agents Page

- [ ] **AC-AA-001**: Same as AC-CA-003 for Autonomous Agent dialogs
- [ ] **AC-AA-002**: Same as AC-CA-004 for Autonomous Agents list

### Settings Page

- [ ] **AC-TS-001**: Create Custom Group dialog is vertically centered
- [ ] **AC-TS-002**: Switching tabs in Edit Custom Group does NOT refetch data
- [ ] **AC-TS-003**: Create Tool dialog is vertically centered
- [ ] **AC-TS-004**: MCP Server and OpenAPI Definition have different badge colors
- [ ] **AC-TS-005**: Tools table shows: Name | Description | Type | Actions
- [ ] **AC-TS-006**: Tools list has type filter dropdown

### Internationalization

- [ ] **AC-I18N-001**: Zero German text visible in UI
- [ ] **AC-I18N-002**: All validation messages in English
- [ ] **AC-I18N-003**: All button labels in English

---

## 6. Risk Assessment & Mitigation

### Risk 1: Breaking Existing Functionality

**Risk**: Changes to DataTableRow may affect other pages using it  
**Probability**: Medium  
**Impact**: High  
**Mitigation**: 
- Test all pages using DataTable after changes
- Use optional props for new features
- Add stopPropagation without changing callback signatures

### Risk 2: State Management Issues

**Risk**: EditCustomGroupDialog fix may introduce new bugs  
**Probability**: Low  
**Impact**: Medium  
**Mitigation**:
- Follow exact pattern from working EditApplicationDialog
- Test tab switching multiple times
- Test form submission after tab switches

### Risk 3: Missing German Text

**Risk**: Some German text may be missed during i18n  
**Probability**: Medium  
**Impact**: Low  
**Mitigation**:
- Use grep to search for German-specific characters (ä, ö, ü, ß)
- Search for common German words
- Manual review of each page

### Risk 4: Conversations Sidebar Performance

**Risk**: Loading conversations data may slow down sidebar hover  
**Probability**: Low  
**Impact**: Medium  
**Mitigation**:
- Use existing caching pattern from SidebarDataContext
- Lazy load only when hovering
- Limit initial load to 20 items

---

## 7. Critical Review & Adjustments

### Review Point 1: Conversations Sidebar Integration

**Original Plan**: Add "conversations" to `EntityType` in `SidebarDataContext`

**Concern**: The `SidebarDataContext` currently only handles:
- applications (QuickListItemResponse)
- autonomous-agents (QuickListItemResponse)  
- chat-widgets (QuickListItemResponse)

Conversations need DIFFERENT data:
- conversation.name (title)
- application.name (subtitle) - requires joining/lookup

**Adjusted Approach**:
1. Create a SEPARATE conversations state in `SidebarDataContext`
2. Fetch conversations with application names in a single API call OR
3. Store application ID → name map and resolve client-side
4. Keep `GlobalChatSidebar` as the source for conversations logic, but RENDER via `SidebarDataList`

**Implementation Detail**:
```typescript
// New state in SidebarDataContext
conversations: Array<{
  id: string;
  name: string;
  applicationId: string;
  applicationName: string;
}>;

// Or: Fetch in Sidebar.tsx directly (simpler, keeps existing pattern)
// Since GlobalChatSidebar already fetches this data, we can:
// Option A: Move fetch logic to SidebarDataContext
// Option B: Keep fetch in GlobalChatSidebar but use SidebarDataList for rendering
```

**Final Decision**: **Option B** - Keep fetch logic in existing location but refactor `GlobalChatSidebar` to use `SidebarDataList` component with extended props. This minimizes changes to the context and keeps conversation-specific logic contained.

---

### Review Point 2: SidebarDataList Subtitle Support

**Concern**: Adding `subtitle` to all `DataListItem` instances might cause visual inconsistency when some items have subtitles and others don't.

**Adjusted Approach**:
- Make subtitle rendering conditional: `{item.subtitle && <Text>...`
- Add CSS to ensure consistent row heights even when subtitle is absent
- Consider: Should ALL sidebar items eventually have subtitles? (e.g., Applications → type as subtitle)

**Decision**: Implement as optional, no visual changes for items without subtitles.

---

### Review Point 3: Tooltip for Truncated Text

**Concern**: Showing tooltip on ALL text regardless of truncation could be annoying

**Adjusted Approach**:
- Use Mantine's `Tooltip` with `disabled` prop when text fits
- Calculate if text is truncated using ref + comparison (more complex)
- OR: Simple heuristic based on character count (simpler, less accurate)

**Decision**: Use character count heuristic initially. If user feedback indicates issues, implement proper truncation detection later.

```typescript
// Simple heuristic
const TOOLTIP_THRESHOLD_NAME = 25;
const TOOLTIP_THRESHOLD_DESC = 50;

<Tooltip 
  label={item.name} 
  disabled={item.name.length <= TOOLTIP_THRESHOLD_NAME}
  ...
/>
```

---

### Review Point 4: Traces Page Placeholder

**Concern**: Creating a 404 placeholder may confuse users who see it in navigation

**Adjusted Approach**: Create a proper "Coming Soon" placeholder page with:
- Clear message that feature is in development
- Consistent with app design
- No navigation to non-existent routes

**Decision**: Create `TracesPage` as a proper placeholder with informative content.

---

### Review Point 5: Edit Dialog Refetch Issue

**Root Cause Analysis**: After reviewing `EditCustomGroupDialog.tsx`:

```typescript
// The effect likely has activeTab in dependencies
useEffect(() => {
  if (opened && customGroupId) {
    fetchCustomGroup();
    setPrincipalsFetched(false); // This resets the flag!
  }
}, [opened, customGroupId]); // Need to verify actual dependencies
```

**Potential Issues**:
1. `principalsFetched` flag reset when switching tabs
2. `fetchPrincipals` called on every tab switch
3. Form state not preserved

**Adjusted Implementation**:
```typescript
// Only reset when dialog OPENS (not on tab change)
useEffect(() => {
  if (opened && customGroupId) {
    // Reset all state
    setCustomGroup(null);
    setPrincipals([]);
    setPrincipalsFetched(false);
    // Fetch fresh data
    fetchCustomGroup();
    fetchPrincipals();
  }
}, [opened, customGroupId]); // Do NOT include activeTab

// Tab change should NOT trigger any fetches
const handleTabChange = (tab: TabValue) => {
  setActiveTab(tab);
  onTabChange?.(tab);
  // NO fetch calls here
};
```

---

### Review Point 6: German Text Search Strategy

**More Robust Search Patterns**:
```bash
# Search for German-specific patterns
grep -r "ist erforderlich" src/
grep -r "darf maximal" src/
grep -r "Zeichen lang" src/
grep -r "erfolgreich" src/
grep -r "Fehler" src/
grep -r "Beschreibung" src/
grep -r "Erstellen" src/
grep -r "Abbrechen" src/
grep -r "Löschen" src/
grep -r "Speichern" src/

# Search for German umlauts
grep -rP "[äöüÄÖÜß]" src/
```

---

## 8. Updated Implementation Priority

Based on critical review, adjusted priority:

### Must-Have (P0)
1. REQ-CA-001: stopPropagation fixes (blocking UX issue)
2. REQ-TS-002: Edit dialog refetch fix (data consistency)
3. REQ-I18N-001: English translations (professional appearance)

### Should-Have (P1)  
4. REQ-CA-003/REQ-AA-001: Dialog dividers (visual consistency)
5. REQ-CA-004: Tooltips for truncated text (usability)
6. REQ-TS-001/003: Dialog centering (visual polish)

### Nice-to-Have (P2)
7. REQ-SB-001: Conversations sidebar redesign (larger change)
8. REQ-SB-002: Persist expand state (convenience)
9. REQ-SB-003: Traces page (placeholder)
10. REQ-TS-004/005/006: Tools table improvements

---

## Appendix A: File Reference

### Dialog Files with German Text (to translate)

```
src/components/dialogs/CreateApplicationDialog.tsx
src/components/dialogs/CreateAutonomousAgentDialog.tsx
src/components/dialogs/CreateCredentialDialog.tsx
src/components/dialogs/CreateToolDialog.tsx
src/components/dialogs/EditApplicationDialog/EditApplicationDialog.tsx
src/components/dialogs/EditAutonomousAgentDialog/EditAutonomousAgentDialog.tsx
```

### Sidebar Related Files

```
src/components/layout/Sidebar/Sidebar.tsx
src/components/layout/Sidebar/SidebarDataList.tsx
src/components/layout/Sidebar/SidebarDataList.module.css
src/components/layout/GlobalChatSidebar/GlobalChatSidebar.tsx
src/contexts/SidebarDataContext.tsx
```

### DataTable Files

```
src/components/common/DataTable/DataTable.tsx
src/components/common/DataTable/DataTableRow.tsx
src/components/common/DataTable/DataTableToolbar.tsx
```

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-27 | Initial document | System |

---

*End of Requirements Document*
