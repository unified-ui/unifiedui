# Tracing Visualization Dialog - Technical Specification v2

> **Purpose**: Complete implementation specification for a modular Tracing Visualization Dialog in React.
> **Version**: 2.0 - Complete rewrite based on DESIGN.md requirements

---

## 1. Project Context

### 1.1 Technology Stack
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Framework**: Mantine v7+
- **Canvas Library**: `@xyflow/react` (installed)
- **Layout Algorithm**: `@dagrejs/dagre` (installed)
- **Styling**: CSS Modules + CSS Custom Properties

### 1.2 Design System Reference

**ALL styling MUST use CSS Custom Properties from `src/styles/variables.css`.**

Available variables:
```
COLORS:
  Primary:    --color-primary-{50,100,200,300,400,500,600,700,800,900}
  Secondary:  --color-secondary-{50-900}
  Success:    --color-success-{50,500,600,700}
  Warning:    --color-warning-{50,500,600,700}
  Error:      --color-error-{50,500,600,700}
  Info:       --color-info-{50,500,600,700}
  Gray:       --color-gray-{0,50,100,200,300,400,500,600,700,800,900}

SEMANTIC:
  Backgrounds: --bg-app, --bg-paper, --bg-elevated, --bg-overlay
  Text:        --text-primary, --text-secondary, --text-disabled, --text-link
  Borders:     --border-default, --border-light, --border-medium, --border-focus

SPACING:
  --spacing-xs (4px), --spacing-sm (8px), --spacing-md (16px)
  --spacing-lg (24px), --spacing-xl (32px), --spacing-2xl (48px)

RADIUS:
  --radius-xs (2px), --radius-sm (4px), --radius-md (8px)
  --radius-lg (12px), --radius-xl (16px), --radius-full

SHADOWS:
  --shadow-xs, --shadow-sm, --shadow-md, --shadow-lg, --shadow-xl

TYPOGRAPHY:
  --font-size-xs (12px), --font-size-sm (14px), --font-size-md (16px)
  --font-weight-regular (400), --font-weight-medium (500), --font-weight-semibold (600)

TRANSITIONS:
  --transition-fast (150ms), --transition-normal (250ms)

Z-INDEX:
  --z-dropdown (100), --z-sticky (200), --z-overlay (300), --z-modal (400)
```

### 1.3 File Location
```
src/components/tracing/
```

---

## 2. Data Model

### 2.1 TypeScript Types (from `src/api/types.ts`)

```typescript
export type TraceContextType = 'conversation' | 'autonomous_agent';

export const TraceNodeType = {
  AGENT: 'agent',
  TOOL: 'tool',
  LLM: 'llm',
  CHAIN: 'chain',
  RETRIEVER: 'retriever',
  WORKFLOW: 'workflow',
  FUNCTION: 'function',
  HTTP: 'http',
  CODE: 'code',
  CONDITIONAL: 'conditional',
  LOOP: 'loop',
  CUSTOM: 'custom',
} as const;

export const TraceNodeStatus = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  SKIPPED: 'skipped',
  CANCELLED: 'cancelled',
} as const;

export interface TraceNodeDataIO {
  text?: string;
  arguments?: Record<string, unknown>;
  extraData?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface TraceNodeData {
  input?: TraceNodeDataIO | null;
  output?: TraceNodeDataIO | null;
}

export interface TraceNodeResponse {
  id: string;
  name: string;
  type: TraceNodeType | string;
  referenceId?: string;
  startAt?: string;
  endAt?: string;
  duration?: number;
  status: TraceNodeStatus | string;
  error?: string;
  logs?: string[];
  data?: TraceNodeData;
  nodes?: TraceNodeResponse[];  // Hierarchical sub-nodes
  metadata?: Record<string, unknown>;
}

export interface FullTraceResponse {
  id: string;
  tenantId: string;
  applicationId?: string;
  conversationId?: string;
  autonomousAgentId?: string;
  contextType: TraceContextType | string;
  referenceId?: string;
  referenceName?: string;
  referenceMetadata?: Record<string, unknown>;
  logs?: Array<string | Record<string, unknown>>;
  nodes: TraceNodeResponse[];
  createdAt: string;
  updatedAt: string;
}
```

### 2.2 Data Hierarchy Example
```
FullTraceResponse (Root)
├── referenceName: "Microsoft Foundry Conversation"
├── contextType: "conversation"
├── logs: ["log1", "log2", ...]
├── referenceMetadata: { project_endpoint: "...", ... }
└── nodes: [
    ├── Node 1 (type: "llm", status: "completed")
    │   ├── data.input.text: "Hello"
    │   └── nodes: []
    │
    ├── Node 2 (type: "workflow", status: "completed")
    │   └── nodes: [  <- SUB-NODES
    │       ├── SubNode 2.1
    │       ├── SubNode 2.2
    │       └── SubNode 2.3
    │   ]
    │
    └── Node 3 (type: "llm")
        └── nodes: []
]
```

---

## 3. Component Architecture

### 3.1 File Structure
```
src/components/tracing/
├── TracingContext.tsx              # React Context for shared state
├── TracingVisualDialog.tsx         # Main modal container
├── TracingVisualDialog.module.css
├── TracingSubHeader.tsx            # Floating info bar over canvas
├── TracingSubHeader.module.css
├── TracingCanvasView.tsx           # @xyflow/react canvas
├── TracingCanvasView.module.css
├── TracingHierarchyView.tsx        # Tree sidebar (right)
├── TracingHierarchyView.module.css
├── TracingDataSection.tsx          # Logs + Input/Output (bottom)
├── TracingDataSection.module.css
└── index.ts
```

### 3.2 Context State

```typescript
interface TracingContextState {
  // Data
  traces: FullTraceResponse[];
  selectedTrace: FullTraceResponse | null;
  selectedNode: TraceNodeResponse | null;
  
  // UI State
  layoutDirection: 'horizontal' | 'vertical';
  zoomLevel: number;
  hierarchyCollapsed: Set<string>;  // Collapsed nodes in hierarchy view
  canvasCollapsed: Set<string>;     // Collapsed nodes in canvas view
  
  // Actions
  selectTrace: (traceId: string) => void;
  selectNode: (nodeId: string | null) => void;
  toggleHierarchyCollapse: (nodeId: string) => void;
  toggleCanvasCollapse: (nodeId: string) => void;
  setLayoutDirection: (dir: 'horizontal' | 'vertical') => void;
  setZoomLevel: (level: number) => void;
  centerOnNode: (nodeId: string) => void;
  resetCanvasView: () => void;
}
```

---

## 4. Dialog Layout (TracingVisualDialog)

### 4.1 Overall Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER                                                                 │
│  [Icon] "Tracing for {referenceName}"                          [Close] │
│         {contextType} Badge                                             │
├─────────────────────────────────────────────────────────────┬───────────┤
│                                                             │           │
│  ┌─ SUBHEADER (floating over canvas) ─────────────────────┐ │ HIERARCHY │
│  │ trace_id │ node_name │ startAt → endAt │ status        │ │   VIEW    │
│  └────────────────────────────────────────────────────────┘ │           │
│                                                             │  (1/4 w)  │
│  ┌─ CANVAS VIEW ──────────────────────────────────────────┐ │  resize-  │
│  │                                                        │ │   able    │
│  │   [Node 1] ───▶ [Node 2] ───▶ [Node 3]                │ │           │
│  │                     │                                  │ │  - Tree   │
│  │                     ├──▶ [SubNode A]                   │ │  - Click  │
│  │                     └──▶ [SubNode B]                   │ │    to     │
│  │                                                        │ │   select  │
│  │  (initial 2/3 height, vertically resizable)           │ │           │
│  └────────────────────────────────────────────────────────┘ │           │
│                                                             │           │
│  ┌─ DATA SECTION ─────────────────────────────────────────┐ │           │
│  │                                                        │ │           │
│  │  ┌──────────┐  ┌──────────────────────────────────┐   │ │           │
│  │  │  LOGS    │  │  INPUT / OUTPUT                  │   │ │           │
│  │  │          │  │                                  │   │ │           │
│  │  │  - log1  │  │  ┌─────────┬─────────┐          │   │ │           │
│  │  │  - log2  │  │  │  INPUT  │ OUTPUT  │          │   │ │           │
│  │  │  - log3  │  │  │         │         │          │   │ │           │
│  │  │          │  │  │  Text   │  Text   │          │   │ │           │
│  │  │  (1/4w)  │  │  │ ▸meta   │ ▸meta   │          │   │ │           │
│  │  │          │  │  │ ▸extra  │ ▸extra  │          │   │ │           │
│  │  │          │  │  │  (1/2)  │  (1/2)  │          │   │ │           │
│  │  │          │  │  └─────────┴─────────┘          │   │ │           │
│  │  └──────────┘  └──────────────────────────────────┘   │ │           │
│  │                                                        │ │           │
│  │  (initial 1/3 height, vertically resizable)           │ │           │
│  └────────────────────────────────────────────────────────┘ │           │
│                                                             │           │
│                        (3/4 width)                          │           │
└─────────────────────────────────────────────────────────────┴───────────┘
```

### 4.2 Modal Settings
- **Size**: `calc(100vw - 80px)` width, `calc(100vh - 60px)` height
- **Radius**: `--radius-lg`
- **Overlay**: Blur effect (user sees app behind)
- **NOT fullScreen**

### 4.3 Resizable Panels
- **Vertical**: Between Canvas View and Data Section (drag border)
- **Horizontal**: Between Main Area (Canvas+Data) and Hierarchy View

---

## 5. Component Specifications

### 5.1 Header

```
┌────────────────────────────────────────────────────────────────┐
│ [TracingIcon]  Tracing for {referenceName}             [Close]│
│                [contextType Badge]                             │
└────────────────────────────────────────────────────────────────┘
```

- **Icon**: `IconChartDots` or similar from @tabler/icons-react
- **Title**: "Tracing for {trace.referenceName}"
- **Subtitle/Badge**: Shows `contextType` (e.g., "conversation" or "autonomous_agent")
- **Close Button**: Top-right corner

---

### 5.2 TracingSubHeader (Floating)

```
┌─────────────────────────────────────────────────────────────────┐
│ ID: abc123...  │  Node: User Message  │  12:45:00 → 12:45:01  │  ✓ completed │
└─────────────────────────────────────────────────────────────────┘
```

**Position**: Fixed, floating OVER the canvas (not over Hierarchy View)

**Content when NO node selected (Root)**:
- `trace.id` (shortened with ...)
- "Root"
- `trace.createdAt` (formatted)
- `contextType`

**Content when node IS selected**:
- `trace.id` (shortened)
- `selectedNode.name`
- `selectedNode.startAt` → `selectedNode.endAt` (if exists)
- `selectedNode.status` with icon

**Status Icons**:
- completed: ✓ (green)
- failed: ✗ (red)
- running: spinner (orange)
- pending: clock (gray)
- skipped/cancelled: dash (gray)

---

### 5.3 TracingCanvasView (@xyflow/react)

**Purpose**: Visual workflow canvas with connected nodes.

#### Node Appearance
```
┌────────────────────────────┐
│                            │
│         [Icon]             │
│                            │
│      {node.name}           │
│                            │
│              [StatusIcon]  │
└────────────────────────────┘
```

**Node Styling**:
- Shape: Rectangular with rounded corners (`--radius-md`)
- Size: ~120px wide, ~80px tall
- Center: Icon based on `node.type`
- Below icon: `node.name` (truncated if too long)
- Bottom-right: Status icon (✓, ✗, spinner, etc.)

**Special Rounding Rules**:
- First node in sequence: Extra rounded on LEFT side (`--radius-xl`)
- Last node in sequence: Extra rounded on RIGHT side (`--radius-xl`)
- Other nodes: Standard rounding (`--radius-md`)

**Border Colors by Status**:
- `completed`: `--color-success-500` (green)
- `failed`: `--color-error-500` (red)
- `running`: `--color-warning-500` (orange, animated)
- `pending`: `--color-gray-400`
- `skipped`/`cancelled`: `--color-gray-500`

**Selected State**: Add `--shadow-md`

#### Node Connections (Edges)

```
[Node 1] ───▶ [Node 2] ───▶ [Node 3]    ← Primary flow (horizontal)
                  │
                  ├──[1]──▶ [SubNode A]  ← Sub-node branch
                  │              │
                  │              └──[1]──▶ [SubSubNode X]
                  │
                  └──[2]──▶ [SubNode B]
```

**Edge Properties**:
- Type: `smoothstep` or `bezier`
- Arrow: `MarkerType.ArrowClosed`
- Color: `--color-primary-400` (#42a5f5)
- Width: 2px
- Animated: true for `running` status

**Branch Labels**: Small numbered badge at branch point (1, 2, 3...)

#### Layout Modes

**Horizontal (default)**:
- Root nodes: Left → Right
- Sub-nodes: Branch downward

**Vertical**:
- Root nodes: Top → Bottom
- Sub-nodes: Branch rightward

**Layout Algorithm**: Use `@dagrejs/dagre` for automatic positioning

#### Canvas Controls
- **Zoom In/Out**: Buttons + scroll wheel + trackpad pinch
- **Pan**: Click-drag on canvas OR two-finger swipe on trackpad
- **Reset View**: Button to center and fit all nodes
- **Layout Toggle**: Button to switch horizontal/vertical
- **MiniMap**: Optional, bottom-right corner

#### Collapse/Expand for Sub-Nodes

**Implementation**: Button is placed **on the parent node itself** (not on the edge).

```
┌────────────────────────────┐
│                            │
│         [Icon]             │
│                            │
│      {node.name}           │
│                            │
│              [StatusIcon]  │
└────────────────────────────┘──[−]
                                 ↑
                            Collapse button
                            (positioned based on sourcePosition)
```

**Button Positioning**:
- **Horizontal Layout** (sourcePosition = Right): Button appears to the RIGHT of the node
- **Vertical Layout** (sourcePosition = Bottom): Button appears BELOW the node
- Position offset: ~30px from node edge

**Button Appearance**:
- Shape: Circular, 22px diameter
- Background: `--bg-paper` (white/dark based on theme)
- Border: 2px solid `--color-gray-400`
- Icon: `IconMinus` when expanded, `IconPlus` when collapsed
- Hover: Border changes to `--color-primary-500`, slight scale (1.15x)

**Behavior**:
- **Click on (−)**: Hides all child nodes and edges → Button changes to (+)
- **Click on (+)**: Shows all child nodes and edges → Button changes to (−)
- Collapse state is tracked per-node in `canvasCollapsed: Set<string>`
- Collapsing a parent automatically hides entire sub-tree (recursive)
- Button is ALWAYS visible on the node (even when children are hidden)

**Node Data Interface**:
```typescript
interface TraceNodeData {
  label: string;
  type: string;
  status: string;
  // ... other props
  
  // Collapse functionality
  hasChildren?: boolean;        // true if node has sub-nodes
  isCollapsed?: boolean;        // true if children are hidden
  onToggleCollapse?: () => void; // callback to toggle collapse state
}
```

**CSS Class**: `.collapseButton` in `TracingCanvasView.module.css`

---

### 5.4 TracingHierarchyView (Right Sidebar)

**Purpose**: Tree-structured navigation of traces and nodes.

```
┌─────────────────────────────────────┐
│ ▾ [conversation] Microsoft Foundry ✓│  ← Trace (collapsible)
│   │                                 │
│   ├──[llm] User Message         ✓   │  ← Node with type badge
│   │                                 │
│   ├──▾ [workflow] SendActivity  ✓   │  ← Node with children
│   │   │                             │
│   │   ├──[llm] Assistant...     ✓   │  ← Sub-node
│   │   └──[llm] Assistant...     ✓   │
│   │                                 │
│   └──[llm] User Message         ✓   │
│                                     │
│ ▾ [conversation] Trace 2        ✓   │  ← Multiple traces
│   └── ...                           │     (only for conversations)
└─────────────────────────────────────┘
```

**Features**:
- **Curved connecting lines**: Like VSCode/Foundry tree (see reference image)
- **Indentation**: ~20px per hierarchy level
- **Type Badge**: Shows `node.type` or `contextType` for root
- **Name**: Truncated with "..." if too long
- **Status Icon**: Checkmark, X, spinner based on status
- **Click**: Selects item → Updates Canvas + Data Section
- **Expand/Collapse**: For nodes with children

**Item Structure**:
```
[▾] [Badge: type] {name}  [StatusIcon]
```

**Tree Connectors**:
- Vertical line from parent
- Curved corner (L-shaped with rounded bottom-left)
- Connects to child item

**Selection**:
- Selected item: Highlighted background (`--color-primary-50`)
- Canvas navigates to selected node and centers it

---

### 5.5 TracingDataSection (Bottom Panel)

**Purpose**: Display logs and input/output data.

```
┌────────────────────┬────────────────────────────────────────────────────┐
│                    │  [Tabs: Input/Output | Metadata (only for root)]  │
│      LOGS          ├────────────────────────────────────────────────────┤
│                    │                                                    │
│  - Log entry 1     │  ┌─────────────────┬─────────────────┐            │
│  - Log entry 2     │  │     INPUT       │     OUTPUT      │            │
│  - Log entry 3     │  │                 │                 │            │
│  - Log entry 4     │  │  Text:          │  Text:          │            │
│                    │  │  "Hello world"  │  "Response..."  │            │
│                    │  │                 │                 │            │
│  (1/4 width)       │  │  ▸ metadata     │  ▸ metadata     │  (expand.) │
│  (resizable)       │  │  ▸ extraData    │  ▸ extraData    │            │
│                    │  │                 │                 │            │
│                    │  │    (1/2 each, resizable)          │            │
│                    │  └─────────────────┴─────────────────┘            │
│                    │                                                    │
│                    │                 (3/4 width)                        │
└────────────────────┴────────────────────────────────────────────────────┘
```

#### State-Dependent Content

**When NO node selected (Root)**:
- **Logs**: `trace.logs`
- **Tabs**: Show "Metadata" tab only
- **Metadata Tab**: `trace.referenceMetadata` as JSON tree

**When node IS selected**:
- **Logs**: `selectedNode.logs` (or empty if none)
- **Tabs**: Show "Input/Output" tab (default) + "Metadata" tab
- **Input/Output Tab**: Split view with Input left, Output right
- **Metadata Tab**: `selectedNode.metadata` as JSON tree

#### Logs Panel (Left)
- Header: "Logs" 
- Scrollable list of log entries
- Log entry format: Simple text or expandable JSON

#### Input/Output Panel (Right)
**For each (Input and Output)**:
1. **Text**: Prominently displayed at top (if exists)
2. **▸ metadata**: Collapsible JSON viewer
3. **▸ extraData**: Collapsible JSON viewer
4. **▸ arguments**: Collapsible JSON viewer (if exists)

**Default state**: Text expanded, metadata/extraData collapsed

#### Resizable
- Horizontal: Between Logs and Input/Output
- Vertical: Between Input and Output (optional)

---

## 6. Icon Mapping

```typescript
const nodeTypeIcons: Record<string, TablerIcon> = {
  agent: IconRobot,
  tool: IconTool,
  llm: IconBrain,
  chain: IconLink,
  workflow: IconChartDots,
  http: IconWorldWww,
  code: IconCode,
  function: IconCode,
  retriever: IconDatabase,
  conditional: IconGitBranch,
  loop: IconRepeat,
  custom: IconForms,
};

const statusIcons: Record<string, { icon: TablerIcon; color: string }> = {
  completed: { icon: IconCheck, color: 'var(--color-success-500)' },
  failed: { icon: IconX, color: 'var(--color-error-500)' },
  running: { icon: IconLoader, color: 'var(--color-warning-500)' },
  pending: { icon: IconClock, color: 'var(--color-gray-400)' },
  skipped: { icon: IconPlayerSkipForward, color: 'var(--color-gray-500)' },
  cancelled: { icon: IconBan, color: 'var(--color-gray-600)' },
};
```

---

## 7. API Integration

### 7.1 Endpoints

```
GET /api/v1/agent-service/tenants/{tenantId}/conversations/{conversationId}/traces
GET /api/v1/agent-service/tenants/{tenantId}/autonomous-agents/{autonomousAgentId}/traces

Response: { traces: FullTraceResponse[], total: number }
```

### 7.2 API Client Methods

```typescript
// Already implemented in src/api/client.ts
async getConversationTraces(tenantId: string, conversationId: string): Promise<FullTracesListResponse>
async getAutonomousAgentTraces(tenantId: string, autonomousAgentId: string): Promise<FullTracesListResponse>
```

---

## 8. Development Page

### 8.1 Route
```
/dev/tracing?conversationId={id}
/dev/tracing?autonomousAgentId={id}
```

### 8.2 Behavior
1. Parse query parameters
2. Fetch traces from API
3. Open TracingVisualDialog automatically when data loaded
4. Pre-select first trace

---

## 9. Keyboard Shortcuts (Optional Enhancement)

- `Escape`: Close dialog / Deselect node
- `Arrow Up/Down`: Navigate hierarchy
- `Enter`: Select highlighted item
- `+/-`: Zoom in/out
- `0`: Reset zoom
- `H/V`: Toggle horizontal/vertical layout

---

## 10. Implementation Priority

### Phase 1: Core Structure
1. [ ] TracingContext with full state management
2. [ ] TracingVisualDialog layout with resizable panels
3. [ ] Header with title and close button

### Phase 2: Canvas (Priority)
4. [ ] TracingCanvasView with @xyflow/react
5. [ ] Custom node component with status styling
6. [ ] Edge transformation with arrows
7. [ ] Dagre layout (horizontal/vertical)
8. [ ] Pan/zoom controls

### Phase 3: SubHeader
9. [ ] TracingSubHeader floating component
10. [ ] Dynamic content based on selection

### Phase 4: Hierarchy
11. [ ] TracingHierarchyView tree structure
12. [ ] Curved connectors
13. [ ] Expand/collapse
14. [ ] Selection sync with canvas

### Phase 5: Data Section
15. [ ] TracingDataSection layout
16. [ ] Logs panel
17. [ ] Input/Output with tabs
18. [ ] Collapsible JSON viewers
19. [ ] Resizable panels

### Phase 6: Polish
20. [ ] Center-on-node navigation
21. [ ] Keyboard shortcuts
22. [ ] Loading/error states
23. [ ] Performance optimization

---

## 11. Testing URLs

```
/dev/tracing?conversationId=fe8f3138-3745-4879-b91b-6a3cb5d03303
/dev/tracing?autonomousAgentId=741776fc-e59a-4d81-8ca0-129acacaeab2
```

---

## 12. Dependencies

**Required** (already installed):
```json
{
  "@xyflow/react": "^12.x",
  "@dagrejs/dagre": "^1.x",
  "@mantine/core": "^7.x",
  "@tabler/icons-react": "^3.x"
}
```

**Recommended for JSON display**:
```bash
npm install react-json-view-lite
```

---

**End of Specification v2**
