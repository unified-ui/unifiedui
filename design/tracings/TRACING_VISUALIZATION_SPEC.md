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

## 13. Layout-Algorithmus (Spaltenbasiert)

### 13.1 Grundprinzip

Das Canvas wird als **Tabelle** betrachtet:
- **Spalten** = horizontale Stufen (Root-Nodes definieren ihre Spalte)
- **Zeilen** = vertikale Positionen (lückenlos von oben nach unten gefüllt)
- **Root-Nodes (N1, N2, N3)** sind die "Spaltenheader" - sie kommen IMMER als erstes in ihrer Spalte
- **Sortierung erfolgt spaltenweise** basierend auf der Y-Position des Parents in der vorherigen Spalte

### 13.2 Test-Datenstruktur

```
N1 (column=0)
├── S1a (column=1)
│   ├── S1a1 (column=2)
│   └── S1a2 (column=2)
├── S1b (column=1)
│   ├── S1b1 (column=2)
│   └── S1b2 (column=2)
│       ├── S1b2a (column=3)
│       │   └── S1b2a1 (column=4)
│       │       └── S1b2a1a (column=5)
│       └── S1b2b (column=3)
└── S1c (column=1)

N2 (column=1)
├── S2a (column=2)
│   ├── S2a1 (column=3)
│   ├── S2a2 (column=3)
│   └── S2a3 (column=3)
└── S2b (column=2)

N3 (column=2)
├── S3a (column=3)
└── S3b (column=3)
    ├── S3b1 (column=4)
    └── S3b2 (column=4)
```

### 13.3 Erwartetes tabellarisches Layout

**WICHTIG:** SubNodes dürfen NIE höher als ihr Parent sein! (`row >= parent.row`)

| Row | Spalte 0 | Spalte 1 | Spalte 2 | Spalte 3 | Spalte 4 | Spalte 5 |
|-----|----------|----------|----------|----------|----------|----------|
| 0   | **N1**   | **N2**   | **N3**   |          |          |          | ← NUR Root-Nodes
| 1   |          | S1a      | S2a      | S3a      |          |          |
| 2   |          | S1b      | S2b      | S3b      | S3b1     |          | ← S3b1 auf Row 2 (= parent S3b)
| 3   |          | S1c      | S1a1     | S2a1     | S3b2     |          |
| 4   |          |          | S1a2     | S2a2     |          |          |
| 5   |          |          | S1b1     | S2a3     |          |          |
| 6   |          |          | S1b2     | S1b2a    | S1b2a1   | S1b2a1a  | ← Alle auf Row 6 (= parent chain)
| 7   |          |          |          | S1b2b    |          |          |

### 13.4 Visuelles Layout (Horizontal)

```
Spalte 0      Spalte 1      Spalte 2      Spalte 3      Spalte 4      Spalte 5
   │             │             │             │             │             │
   │  ┌───┐      │  ┌───┐      │  ┌───┐      │             │             │         Row 0
   │  │ N1│──────┼─▶│ N2│──────┼─▶│ N3│      │             │             │
   │  └───┘      │  └───┘      │  └───┘      │             │             │
   │     │       │     │       │     │       │  ┌────┐     │             │
   │     │       │  ┌────┐     │  ┌────┐     │  │ S3a│     │             │         Row 1
   │     ├───────┼─▶│ S1a│     │  │ S2a│     │  └────┘     │             │
   │     │       │  └────┘     │  └────┘     │  ┌────┐     │  ┌─────┐    │
   │     │       │  ┌────┐     │  ┌────┐     │  │ S3b│─────┼─▶│S3b1 │    │         Row 2
   │     ├───────┼─▶│ S1b│     │  │ S2b│     │  └────┘     │  └─────┘    │
   │     │       │  └────┘     │  └────┘     │  ┌─────┐    │  ┌─────┐    │
   │     │       │  ┌────┐     │  ┌─────┐    │  │S2a1 │    │  │S3b2 │    │         Row 3
   │     └───────┼─▶│ S1c│     │  │S1a1 │    │  └─────┘    │  └─────┘    │
   │             │  └────┘     │  └─────┘    │  ┌─────┐    │             │
   │             │             │  ┌─────┐    │  │S2a2 │    │             │         Row 4
   │             │             │  │S1a2 │    │  └─────┘    │             │
   │             │             │  └─────┘    │  ┌─────┐    │             │
   │             │             │  ┌─────┐    │  │S2a3 │    │             │         Row 5
   │             │             │  │S1b1 │    │  └─────┘    │             │
   │             │             │  └─────┘    │  ┌──────┐   │  ┌───────┐  │  ┌────────┐
   │             │             │  ┌─────┐    │  │S1b2a │───┼─▶│S1b2a1 │──┼─▶│S1b2a1a │  Row 6
   │             │             │  │S1b2 │────┼─▶└──────┘   │  └───────┘  │  └────────┘
   │             │             │  └─────┘    │  ┌──────┐   │             │
   │             │             │             │  │S1b2b │   │             │         Row 7
   │             │             │             │  └──────┘   │             │
```

### 13.4b Tabellarisches Layout (Vertikal)

Im vertikalen Modus werden **Spalten zu Zeilen** und **Rows zu Spalten**:
- Spalte → Y-Achse (von oben nach unten)
- Row → X-Achse (von links nach rechts)

| Zeile    | Row 0    | Row 1    | Row 2    | Row 3    | Row 4    | Row 5    | Row 6    | Row 7    |
|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| Spalte 0 | **N1**   |          |          |          |          |          |          |          |
| Spalte 1 | **N2**   | S1a      | S1b      | S1c      |          |          |          |          |
| Spalte 2 | **N3**   | S2a      | S2b      | S1a1     | S1a2     | S1b1     | S1b2     |          |
| Spalte 3 |          | S3a      | S3b      | S2a1     | S2a2     | S2a3     | S1b2a    | S1b2b    |
| Spalte 4 |          |          | S3b1     | S3b2     |          |          | S1b2a1   |          |
| Spalte 5 |          |          |          |          |          |          | S1b2a1a  |          |

### 13.4c Visuelles Layout (Vertikal)

```
         Row 0       Row 1       Row 2       Row 3       Row 4       Row 5       Row 6       Row 7
           │           │           │           │           │           │           │           │
Spalte 0 ──┼──┌───┐    │           │           │           │           │           │           │
           │  │ N1│    │           │           │           │           │           │           │
           │  └─┬─┘    │           │           │           │           │           │           │
           │    │      │           │           │           │           │           │           │
           │    ▼      │           │           │           │           │           │           │
Spalte 1 ──┼──┌───┐────┼──┌────┐───┼──┌────┐───┼──┌────┐   │           │           │           │
           │  │ N2│    │  │ S1a│   │  │ S1b│   │  │ S1c│   │           │           │           │
           │  └─┬─┘    │  └──┬─┘   │  └──┬─┘   │  └────┘   │           │           │           │
           │    │      │     │     │     │     │           │           │           │           │
           │    ▼      │     ▼     │     ▼     │           │           │           │           │
Spalte 2 ──┼──┌───┐────┼──┌────┐───┼──┌────┐───┼──┌─────┐──┼──┌─────┐──┼──┌─────┐──┼──┌─────┐  │
           │  │ N3│    │  │ S2a│   │  │ S2b│   │  │S1a1 │  │  │S1a2 │  │  │S1b1 │  │  │S1b2 │  │
           │  └─┬─┘    │  └──┬─┘   │  └────┘   │  └─────┘  │  └─────┘  │  └─────┘  │  └──┬──┘  │
           │    │      │     │     │           │           │           │           │     │     │
           │    ▼      │     ▼     │     ▼     │     ▼     │     ▼     │     ▼     │     ▼     │
Spalte 3 ──┼──         ┼──┌────┐───┼──┌────┐───┼──┌─────┐──┼──┌─────┐──┼──┌─────┐──┼──┌──────┐─┼──┌──────┐
           │           │  │ S3a│   │  │ S3b│   │  │S2a1 │  │  │S2a2 │  │  │S2a3 │  │  │S1b2a │ │  │S1b2b │
           │           │  └────┘   │  └──┬─┘   │  └─────┘  │  └─────┘  │  └─────┘  │  └──┬───┘ │  └──────┘
           │           │           │     │     │           │           │           │     │     │
           │           │           │     ▼     │     ▼     │           │           │     ▼     │
Spalte 4 ──┼──         ┼──         ┼──┌─────┐──┼──┌─────┐  │           │           ┼──┌───────┐│
           │           │           │  │S3b1 │  │  │S3b2 │  │           │           │  │S1b2a1 ││
           │           │           │  └─────┘  │  └─────┘  │           │           │  └───┬───┘│
           │           │           │           │           │           │           │      │    │
           │           │           │           │           │           │           │      ▼    │
Spalte 5 ──┼──         ┼──         ┼──         ┼──         ┼──         ┼──         ┼──┌────────┐
           │           │           │           │           │           │           │  │S1b2a1a │
           │           │           │           │           │           │           │  └────────┘
```

**Legende:**
- **Spalten** gehen jetzt von OBEN nach UNTEN (Y-Achse)
- **Rows** gehen jetzt von LINKS nach RECHTS (X-Achse)
- Root-Chain (N1 → N2 → N3) verläuft VERTIKAL
- SubNodes verzweigen nach RECHTS

### 13.5 Kernregeln

1. **Root-Nodes sind Spaltenheader:**
   - `N1.column = 0` → N1 ist Header von Spalte 0
   - `N2.column = 1` → N2 ist Header von Spalte 1
   - `N3.column = 2` → N3 ist Header von Spalte 2
   - Header kommen IMMER bei Row 0 ihrer Spalte

2. **SubNodes gehen in die nächste Spalte:**
   - `SubNode.column = Parent.column + 1`

3. **⚠️ KEIN HOCHRUTSCHEN - SubNodes mindestens auf Parent-Row:**
   - `SubNode.row >= Parent.row` (IMMER!)
   - Ein SubNode darf NIE oberhalb seines Parents erscheinen
   - Beispiel: S3b ist auf Row 2 → S3b1 muss mindestens Row 2 sein
   - Beispiel: S1b2a ist auf Row 6 → S1b2a1 muss mindestens Row 6 sein

4. **Sortierung innerhalb einer Spalte:**
   - **Erst:** Root-Node dieser Spalte (falls vorhanden)
   - **Dann:** Alle anderen Nodes, sortiert nach:
     - `parent.row` AUFSTEIGEND (wer weiter oben sitzt, dessen Kinder kommen zuerst)
     - `localIndex` AUFSTEIGEND (Reihenfolge innerhalb Siblings)

5. **Spalten werden von LINKS nach RECHTS berechnet:**
   - Erst Spalte 0 → dann Spalte 1 (basierend auf Spalte 0) → dann Spalte 2 (basierend auf Spalte 1) → usw.

### 13.6 Algorithmus (Pseudo-Code)

```typescript
interface LayoutNode {
    id: string;
    column: number;
    row: number;
    x: number;
    y: number;
    parentId: string | null;
    localIndex: number;          // Index innerhalb der Siblings
    isRoot: boolean;             // Ist dies ein Root-Node (N1, N2, N3)?
    originalNode: TraceNodeResponse;
}

function layoutNodes(rootNodes: TraceNodeResponse[]): LayoutNode[] {
    const allNodes: LayoutNode[] = [];
    const nodeMap: Map<string, LayoutNode> = new Map();
    
    // === PHASE 1: Alle Nodes sammeln mit Spalten-Zuweisung ===
    function traverse(
        node: TraceNodeResponse, 
        column: number, 
        parentId: string | null,
        localIndex: number,
        isRoot: boolean
    ): void {
        const layoutNode: LayoutNode = {
            id: node.id,
            column,
            row: -1,  // wird später berechnet
            x: 0,
            y: 0,
            parentId,
            localIndex,
            isRoot,
            originalNode: node
        };
        
        allNodes.push(layoutNode);
        nodeMap.set(node.id, layoutNode);
        
        // SubNodes bekommen column + 1
        if (node.nodes) {
            for (let i = 0; i < node.nodes.length; i++) {
                traverse(node.nodes[i], column + 1, node.id, i, false);
            }
        }
    }
    
    // Root-Nodes: N1=col0, N2=col1, N3=col2
    for (let i = 0; i < rootNodes.length; i++) {
        traverse(rootNodes[i], i, null, i, true);
    }
    
    // === PHASE 2: Spaltenweise Row-Berechnung (LINKS → RECHTS) ===
    const maxColumn = Math.max(...allNodes.map(n => n.column));
    
    for (let col = 0; col <= maxColumn; col++) {
        const nodesInColumn = allNodes.filter(n => n.column === col);
        
        // Sortieren
        nodesInColumn.sort((a, b) => {
            // 1. Root-Nodes ZUERST
            if (a.isRoot && !b.isRoot) return -1;
            if (!a.isRoot && b.isRoot) return 1;
            
            // 2. Nach Parent-Row (wer weiter oben, dessen Kinder zuerst)
            const parentA = a.parentId ? nodeMap.get(a.parentId) : null;
            const parentB = b.parentId ? nodeMap.get(b.parentId) : null;
            const parentRowA = parentA?.row ?? -1;
            const parentRowB = parentB?.row ?? -1;
            
            if (parentRowA !== parentRowB) {
                return parentRowA - parentRowB;  // kleinere Row = weiter oben
            }
            
            // 3. Nach localIndex (Reihenfolge innerhalb Siblings)
            return a.localIndex - b.localIndex;
        });
        
        // Row zuweisen mit "Kein Hochrutschen"-Regel
        // Ein SubNode darf NIE oberhalb seines Parents erscheinen!
        const hasRootInColumn = nodesInColumn.some(n => n.isRoot);
        let nextAvailableRow = hasRootInColumn ? 0 : 1;
        
        for (const node of nodesInColumn) {
            const parent = node.parentId ? nodeMap.get(node.parentId) : null;
            const minRow = parent ? parent.row : 0;
            
            // Row ist das Maximum aus: nächste verfügbare Row ODER Parent-Row
            node.row = Math.max(nextAvailableRow, minRow);
            nextAvailableRow = node.row + 1;
        }
    }
    
    // === PHASE 3: X/Y Positionen berechnen ===
    for (const node of allNodes) {
        node.x = START_X + node.column * HORIZONTAL_GAP;
        node.y = START_Y + node.row * VERTICAL_GAP;
    }
    
    return allNodes;
}
```

### 13.7 Beispiel-Berechnung

**Spalte 0:**
```
Nodes: [N1]
Sortiert: N1 (isRoot=true)
Ergebnis: N1.row = 0
```

**Spalte 1:**
```
Nodes: [N2, S1a, S1b, S1c]
Sortiert:
  1. N2 (isRoot=true) → row=0
  2. S1a (parent=N1, parentRow=0, localIndex=0) → row=1
  3. S1b (parent=N1, parentRow=0, localIndex=1) → row=2
  4. S1c (parent=N1, parentRow=0, localIndex=2) → row=3
```

**Spalte 2:**
```
Nodes: [N3, S2a, S2b, S1a1, S1a2, S1b1, S1b2]
Sortiert:
  1. N3 (isRoot=true) → row=0
  2. S2a (parent=N2, parentRow=0, localIndex=0) → row=1
  3. S2b (parent=N2, parentRow=0, localIndex=1) → row=2
  4. S1a1 (parent=S1a, parentRow=1, localIndex=0) → row=3
  5. S1a2 (parent=S1a, parentRow=1, localIndex=1) → row=4
  6. S1b1 (parent=S1b, parentRow=2, localIndex=0) → row=5
  7. S1b2 (parent=S1b, parentRow=2, localIndex=1) → row=6
```

**Spalte 3:**
```
Nodes: [S3a, S3b, S2a1, S2a2, S2a3, S1b2a, S1b2b]
Kein Root-Node → nextRow=1
Sortiert + "Kein Hochrutschen":
  1. S3a: max(nextRow=1, parentRow=0) = 1, nextRow=2
  2. S3b: max(nextRow=2, parentRow=0) = 2, nextRow=3
  3. S2a1: max(nextRow=3, parentRow=1) = 3, nextRow=4
  4. S2a2: max(nextRow=4, parentRow=1) = 4, nextRow=5
  5. S2a3: max(nextRow=5, parentRow=1) = 5, nextRow=6
  6. S1b2a: max(nextRow=6, parentRow=6) = 6, nextRow=7  ← Parent ist auf Row 6!
  7. S1b2b: max(nextRow=7, parentRow=6) = 7, nextRow=8
```

**Spalte 4:**
```
Nodes: [S3b1, S3b2, S1b2a1]
Kein Root-Node → nextRow=1
Sortiert + "Kein Hochrutschen":
  1. S3b1: max(nextRow=1, parentRow=2) = 2, nextRow=3  ← Parent S3b ist auf Row 2!
  2. S3b2: max(nextRow=3, parentRow=2) = 3, nextRow=4
  3. S1b2a1: max(nextRow=4, parentRow=6) = 6, nextRow=7  ← Parent S1b2a ist auf Row 6!
```

**Spalte 5:**
```
Nodes: [S1b2a1a]
Kein Root-Node → nextRow=1
Sortiert + "Kein Hochrutschen":
  1. S1b2a1a: max(nextRow=1, parentRow=6) = 6  ← Parent S1b2a1 ist auf Row 6!
```

### 13.8 Variablen-Definition

```typescript
// Konstanten
const HORIZONTAL_GAP = 200;     // Abstand zwischen Spalten (X-Richtung)
const VERTICAL_GAP = 100;       // Abstand zwischen Nodes in einer Spalte (Y-Richtung)
const NODE_WIDTH = 120;
const NODE_HEIGHT = 80;
const START_X = 50;
const START_Y = 50;
```

### 13.9 Algorithmus: Vertikaler Modus

**Transformation: X ↔ Y tauschen**

```typescript
// Horizontaler Modus
node.x = START_X + column * HORIZONTAL_GAP
node.y = START_Y + row * VERTICAL_GAP

// Vertikaler Modus  
node.x = START_X + row * VERTICAL_GAP      // row wird zu X
node.y = START_Y + column * HORIZONTAL_GAP // column wird zu Y
```

### 13.10 Edge-Generierung

```typescript
function generateEdges(layoutNodes: LayoutNode[]): Edge[] {
    const edges: Edge[] = [];
    const nodeMap = new Map(layoutNodes.map(n => [n.id, n]));
    
    // 1. Root-to-Root Chain (N1 → N2 → N3)
    const rootNodes = layoutNodes
        .filter(n => n.isRoot)
        .sort((a, b) => a.column - b.column);
    
    for (let i = 0; i < rootNodes.length - 1; i++) {
        edges.push({
            id: `root-${rootNodes[i].id}->${rootNodes[i+1].id}`,
            source: rootNodes[i].id,
            target: rootNodes[i+1].id,
            type: 'smoothstep',
            animated: true,
            style: { stroke: 'var(--color-primary-400)', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed }
        });
    }
    
    // 2. Parent → SubNode Edges
    for (const node of layoutNodes) {
        if (node.parentId) {
            edges.push({
                id: `sub-${node.parentId}->${node.id}`,
                source: node.parentId,
                target: node.id,
                type: 'smoothstep',
                style: { stroke: 'var(--color-secondary-400)', strokeWidth: 2 },
                markerEnd: { type: MarkerType.ArrowClosed }
            });
        }
    }
    
    return edges;
}
```

### 13.11 Handle-Positionen

**Horizontal Mode:**
```typescript
sourcePosition: Position.Right   // Edges gehen nach rechts raus
targetPosition: Position.Left    // Edges kommen von links rein
```

**Vertical Mode:**
```typescript
sourcePosition: Position.Bottom  // Edges gehen nach unten raus
targetPosition: Position.Top     // Edges kommen von oben rein
```

### 13.12 Zusammenfassung der Kernlogik

| Schritt | Beschreibung |
|---------|--------------|
| 1. Spalten zuweisen | `N[i].column = i`, `SubNode.column = parent.column + 1` |
| 2. Nodes sammeln | Mit `parentId`, `localIndex`, `isRoot` |
| 3. Spaltenweise sortieren | Links → Rechts, basierend auf `parent.row` |
| 4. Sortierlogik | `isRoot FIRST` → `parent.row ASC` → `localIndex ASC` |
| 5. Kein Hochrutschen | `node.row = max(nextRow, parent.row)` |
| 6. Positionen | `x = col * H_GAP`, `y = row * V_GAP` (horizontal) |
| 7. Edges | Root-Chain + Parent→SubNode Verbindungen |

**Ergebnis:** Tabellarische Struktur ohne Lücken, Root-Nodes als Header, Kinder folgen ihrer Parent-Position (NIE darüber!).

---

## 14. Collapse/Expand Logik

### 14.1 Grundprinzip

Wenn ein Node collapsed/expanded wird, **wird die GESAMTE Tabelle neu berechnet**.

### 14.2 State-Management

```typescript
// Im TracingContext
canvasCollapsed: Set<string>;  // Set von Node-IDs die collapsed sind

toggleCanvasCollapse: (nodeId: string) => void;
```

### 14.3 Collapse-Verhalten

**Wenn ein Node collapsed wird:**
1. Node-ID wird zu `canvasCollapsed` hinzugefügt
2. **Alle Nachfahren (rekursiv) werden aus der Berechnung ausgeschlossen**
3. Layout wird komplett neu berechnet
4. Rows werden neu vergeben (ohne Lücken!)

**Beispiel: S1b wird collapsed**

**Vorher (S1b expanded):**
| Row | Spalte 1 | Spalte 2 | Spalte 3 |
|-----|----------|----------|----------|
| 1   | S1a      | S2a      | S3a      |
| 2   | S1b      | S2b      | S3b      |
| 3   | S1c      | S1a1     | S2a1     |
| 4   |          | S1a2     | S2a2     |
| 5   |          | S1b1     | S2a3     |  ← S1b1 und S1b2 sind Kinder von S1b
| 6   |          | S1b2     | S1b2a    |
| 7   |          |          | S1b2b    |

**Nachher (S1b collapsed):**
| Row | Spalte 1 | Spalte 2 | Spalte 3 |
|-----|----------|----------|----------|
| 1   | S1a      | S2a      | S3a      |
| 2   | S1b [+]  | S2b      | S3b      |  ← S1b zeigt [+] Button
| 3   | S1c      | S1a1     | S2a1     |
| 4   |          | S1a2     | S2a2     |
| 5   |          |          | S2a3     |  ← Rows rutschen nach oben!

**S1b1, S1b2, S1b2a, S1b2b, S1b2a1, S1b2a1a** sind ALLE versteckt und werden bei der Layout-Berechnung ignoriert.

### 14.4 Expand-Verhalten

**Wenn ein Node expanded wird:**
1. Node-ID wird aus `canvasCollapsed` entfernt
2. **Alle Nachfahren werden wieder in die Berechnung einbezogen**
3. Layout wird komplett neu berechnet
4. Rows werden neu vergeben (SubNodes erscheinen wieder)

### 14.5 Algorithmus-Integration

```typescript
function layoutNodes(
    rootNodes: TraceNodeResponse[], 
    collapsedNodes: Set<string>
): LayoutNode[] {
    const allNodes: LayoutNode[] = [];
    const nodeMap: Map<string, LayoutNode> = new Map();
    
    // === PHASE 1: Nodes sammeln (mit Collapse-Filter) ===
    function traverse(
        node: TraceNodeResponse, 
        column: number, 
        parentId: string | null,
        localIndex: number,
        isRoot: boolean
    ): void {
        const layoutNode: LayoutNode = {
            id: node.id,
            column,
            row: -1,
            x: 0,
            y: 0,
            parentId,
            localIndex,
            isRoot,
            hasChildren: (node.nodes?.length ?? 0) > 0,
            isCollapsed: collapsedNodes.has(node.id),
            originalNode: node
        };
        
        allNodes.push(layoutNode);
        nodeMap.set(node.id, layoutNode);
        
        // ⚠️ NUR wenn Node NICHT collapsed ist, werden Kinder traversiert!
        if (node.nodes && !collapsedNodes.has(node.id)) {
            for (let i = 0; i < node.nodes.length; i++) {
                traverse(node.nodes[i], column + 1, node.id, i, false);
            }
        }
    }
    
    // Root-Nodes traversieren
    for (let i = 0; i < rootNodes.length; i++) {
        traverse(rootNodes[i], i, null, i, true);
    }
    
    // === PHASE 2 + 3: Row-Berechnung (wie vorher) ===
    // ... (Rest des Algorithmus bleibt gleich)
    
    return allNodes;
}
```

### 14.6 React-Flow Node Data

```typescript
interface TraceNodeData {
    label: string;
    type: string;
    status: string;
    
    // Collapse-Funktionalität
    hasChildren: boolean;           // true wenn Node SubNodes hat
    isCollapsed: boolean;           // true wenn collapsed
    onToggleCollapse: () => void;   // Callback zum Togglen
}
```

### 14.7 Edge-Filterung

Edges werden NUR für sichtbare Nodes generiert:

```typescript
function generateEdges(layoutNodes: LayoutNode[]): Edge[] {
    const visibleNodeIds = new Set(layoutNodes.map(n => n.id));
    const edges: Edge[] = [];
    
    // ... Edge-Generierung ...
    
    // NUR Edges hinzufügen, deren Source UND Target sichtbar sind
    if (visibleNodeIds.has(source) && visibleNodeIds.has(target)) {
        edges.push(edge);
    }
    
    return edges;
}
```

### 14.8 Zusammenfassung

| Aktion | Effekt |
|--------|--------|
| **Collapse** | Kinder werden aus Layout entfernt, Rows rutschen nach |
| **Expand** | Kinder werden wieder eingefügt, Layout wird neu berechnet |
| **Jede Änderung** | KOMPLETTE Neuberechnung der gesamten Tabelle |
| **Button** | [−] wenn expanded, [+] wenn collapsed |
| **Rekursiv** | Collapse versteckt ALLE Nachfahren (nicht nur direkte Kinder) |

---

## 15. Tracing Sidebar (ConversationsPage Integration)

Diese Sektion dokumentiert die **aktuelle Implementierung** der Tracing Sidebar auf der ConversationsPage.

### 15.1 Übersicht

Die Tracing Sidebar ist eine kompakte Variante der Tracing-Visualisierung, die rechts neben dem Chat auf der ConversationsPage angezeigt wird. Sie ermöglicht Benutzern, Traces zu navigieren und Details zu Nodes zu sehen, ohne die Chat-Ansicht zu verlassen.

### 15.2 Integration auf ConversationsPage

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MAIN LAYOUT                                                                │
├───────────┬─────────────────────────────────────────────────────┬───────────┤
│           │                                                     │           │
│  CHAT     │                   CHAT AREA                         │  TRACING  │
│ SIDEBAR   │                                                     │  SIDEBAR  │
│           │  ┌─────────────────────────────────────────────┐   │           │
│ (280px)   │  │  Chat Header                                │   │  (320px)  │
│           │  │  [App Select] [Actions] [Tracing Toggle]    │   │           │
│           │  ├─────────────────────────────────────────────┤   │           │
│           │  │                                             │   │           │
│           │  │              Chat Messages                  │   │           │
│           │  │                                             │   │           │
│           │  │              [User Message]                 │   │           │
│           │  │              [Assistant Message] ◀──────────│───│── Klick   │
│           │  │              [User Message]                 │   │   synchr. │
│           │  │                                             │   │           │
│           │  ├─────────────────────────────────────────────┤   │           │
│           │  │              Chat Input                     │   │           │
│           │  └─────────────────────────────────────────────┘   │           │
│           │                                                     │           │
└───────────┴─────────────────────────────────────────────────────┴───────────┘
```

**Toggle-Mechanismus:**
- Button im ChatHeader: `IconChartDots` Icon
- State: `tracingSidebarVisible` (useState)
- Sidebar wird nur angezeigt wenn `tracingSidebarVisible && traces.length > 0`

### 15.3 Komponenten-Hierarchie

```
ConversationsPage.tsx
└── TracingProvider (nur wenn tracingSidebarVisible && traces.length > 0)
    └── TracingSidebar
        └── TracingHierarchyView (variant="compact", showHeader=true, showDataPanels=true)
            ├── Header ("Tracing Hierarchie" + Fullscreen Button)
            ├── Tree Area (ScrollArea)
            │   └── TraceRootItem(s)
            │       └── TreeItem(s) (rekursiv)
            └── DataPanelsSection (resizable)
                ├── CollapsiblePanel: Logs
                ├── CollapsiblePanel: Input/Output (nur wenn Node ausgewählt)
                └── CollapsiblePanel: Metadata
```

### 15.4 TracingSidebar Komponente

**Datei:** `src/components/tracing/TracingSidebar.tsx`

```typescript
interface TracingSidebarProps {
  onOpenFullscreen?: () => void;  // Callback für Vollbild-Dialog
}
```

**Funktion:**
- Wrapper-Komponente für `TracingHierarchyView`
- Konfiguriert die Hierarchy View für den Sidebar-Modus:
  - `variant="compact"` - Kompaktes Layout ohne Border
  - `showHeader={true}` - Zeigt Header mit Titel und Fullscreen-Button
  - `showDataPanels={true}` - Aktiviert VS Code-style Panels unten

**CSS:**
```css
.container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
}
```

### 15.5 TracingHierarchyView (Kern-Komponente)

**Datei:** `src/components/tracing/TracingHierarchyView.tsx`

```typescript
interface TracingHierarchyViewProps {
  variant?: 'full' | 'compact';  // 'full' für Dialog, 'compact' für Sidebar
  showHeader?: boolean;          // Header mit Titel anzeigen
  showDataPanels?: boolean;      // VS Code-style Data Panels anzeigen
  onOpenFullscreen?: () => void; // Callback für Fullscreen Button
}
```

#### 15.5.1 Layout-Struktur (Sidebar-Mode)

```
┌───────────────────────────────────────┐
│ HEADER                                │
│ "Tracing Hierarchie"      [Fullscreen]│
├───────────────────────────────────────┤
│                                       │
│ TREE AREA (ScrollArea, flex: 1)       │
│                                       │
│ ▾ [conversation] Microsoft Foundry ✓  │
│   ├──[llm] User Message           ✓   │
│   ├──▾ [workflow] SendActivity    ✓   │
│   │   ├──[llm] Assistant...       ✓   │
│   │   └──[llm] Assistant...       ✓   │
│   └──[llm] User Message           ✓   │
│                                       │
├───────────────────────────────────────┤
│ ═══════ RESIZE HANDLE ════════════    │
├───────────────────────────────────────┤
│                                       │
│ DATA PANELS SECTION (resizable)       │
│                                       │
│ ▸ LOGS                          [3]   │
│ ▾ INPUT / OUTPUT                      │
│   ┌───────────────────────────────┐   │
│   │ INPUT                         │   │
│   │ Text: "Hello world"           │   │
│   │ ▸ Arguments                   │   │
│   │ ▸ Metadata                    │   │
│   ├───────────────────────────────┤   │
│   │ OUTPUT                        │   │
│   │ Text: "Hi! How can I help?"   │   │
│   │ ▸ Arguments                   │   │
│   │ ▸ Metadata                    │   │
│   └───────────────────────────────┘   │
│ ▸ METADATA                            │
│                                       │
└───────────────────────────────────────┘
```

#### 15.5.2 Sub-Komponenten

**TreeItem:**
```typescript
interface TreeItemProps {
  node: TraceNodeResponse;
  depth: number;              // Indentation Level
  isSelected: boolean;
  isExpanded: boolean;
  onSelect: (nodeId: string) => void;
  onToggle: (nodeId: string) => void;
}
```

**TraceRootItem:** (für Trace-Root-Elemente)
```typescript
interface TraceRootItemProps {
  trace: FullTraceResponse;
  isSelected: boolean;        // Root ist selected wenn selectedNode === null
  isExpanded: boolean;
  onSelect: () => void;
  onToggle: () => void;
}
```

**CollapsiblePanel:** (VS Code-style)
```typescript
interface CollapsiblePanelProps {
  title: string;
  icon: React.ReactNode;
  defaultOpen?: boolean;
  children: React.ReactNode;
  badge?: number;            // Badge mit Zähler (z.B. für Logs)
}
```

**DataPanelsSection:**
```typescript
interface DataPanelsSectionProps {
  panelsHeight: number;                      // Aktuelle Höhe (resizable)
  onResizeStart: (e: React.MouseEvent) => void;
}
```

### 15.6 Daten-Anzeige-Logik

**Wenn Root (kein Node) ausgewählt:**
- **Logs:** `selectedTrace.logs`
- **Input/Output:** NICHT angezeigt (Panel versteckt)
- **Metadata:** `selectedTrace.referenceMetadata`

**Wenn Node ausgewählt:**
- **Logs:** `selectedNode.logs`
- **Input/Output:** 
  - Input: `selectedNode.data.input` (text, arguments, metadata, extraData)
  - Output: `selectedNode.data.output` (text, arguments, metadata, extraData)
- **Metadata:** `selectedNode.metadata`

### 15.7 Input/Output Panel Struktur

```
┌─────────────────────────────────────┐
│ INPUT                               │
├─────────────────────────────────────┤
│ Text:                               │
│ "Hello, how are you?"               │
│                                     │
│ ▸ Arguments                         │
│   ┌─ { "param1": "value" } ─┐       │
│   └─────────────────────────┘       │
│                                     │
│ ▸ Metadata                          │
│   (collapsed by default)            │
│                                     │
│ ▸ Extra Data                        │
│   (collapsed by default)            │
├─────────────────────────────────────┤
│ ─────────── DIVIDER ───────────     │
├─────────────────────────────────────┤
│ OUTPUT                              │
├─────────────────────────────────────┤
│ Text:                               │
│ "I'm doing well, thanks!"           │
│                                     │
│ ▸ Arguments                         │
│ ▸ Metadata                          │
│ ▸ Extra Data                        │
└─────────────────────────────────────┘
```

### 15.8 JSON Viewer Komponente

**Funktion:** Zeigt JSON-Daten collapsible an

```typescript
interface JsonViewerProps {
  data: unknown;
  initialCollapsed?: boolean;  // Default: true für große Objekte
}
```

**Verhalten:**
- Kleine Objekte (≤5 Zeilen): Vollständig angezeigt
- Große Objekte (>5 Zeilen): 
  - Collapsed: Zeigt erste 3 Zeilen + "..."
  - Toggle-Button mit Zeilenanzahl

### 15.9 Message-to-Trace Synchronisation

**Bidirektionale Synchronisation zwischen Chat und Tracing:**

```
Chat Message              Tracing Node
─────────────────────────────────────────
extMessageId     ←→      node.referenceId
```

**Von Message zu Trace:**
1. User klickt auf "View Trace" Button bei einer Message
2. `handleViewTrace(extMessageId)` wird aufgerufen
3. TracingSidebar wird geöffnet (falls nicht offen)
4. Node mit passendem `referenceId` wird selektiert
5. Chat-Message wird highlighted (`highlightedExtMessageId`)

**Von Trace zu Message:**
1. User klickt auf Node in der Hierarchy
2. `onNodeReferenceIdChange(referenceId)` Callback wird aufgerufen
3. `highlightedMessageExtId` wird gesetzt
4. Entsprechende Chat-Message wird highlighted

### 15.10 TracingContext Integration

**Provider-Props in ConversationsPage:**
```typescript
<TracingProvider 
  traces={traces}
  initialNodeReferenceId={selectedNodeReferenceId}
  onNodeReferenceIdChange={setHighlightedMessageExtId}
>
  <TracingSidebar onOpenFullscreen={handleOpenTracingFullscreen} />
</TracingProvider>
```

**Context-State für Sidebar:**
```typescript
// Aus TracingContext
const {
  selectedTrace,                    // Aktuell ausgewählter Trace
  selectedNode,                     // Aktuell ausgewählter Node (null = Root)
  hierarchyCollapsed,               // Set<string> - collapsed Node IDs
  selectNode,                       // (nodeId: string | null) => void
  toggleHierarchyCollapse,          // (nodeId: string) => void
  findNodeForMessage,               // (extMessageId: string) => TraceNodeResponse | null
  selectNodeByExtMessageId,         // (extMessageId: string) => boolean
} = useTracing();
```

### 15.11 CSS Styling (Sidebar-spezifisch)

**ConversationsPage.module.css:**
```css
.tracingSidebarWrapper {
  width: 320px;
  min-width: 320px;
  border-left: 1px solid var(--border-default);
  background-color: var(--bg-paper);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chatSection.withTracingSidebar {
  /* Chat-Bereich schrumpft automatisch durch flex */
}
```

**TracingHierarchyView.module.css (Auszug):**
```css
/* Container für compact Variant */
.containerCompact {
  border-left: none;  /* Border wird von Wrapper gesetzt */
}

/* Data Panels Section */
.dataPanelsSection {
  display: flex;
  flex-direction: column;
  min-height: 100px;
  border-top: 1px solid var(--border-default);
  background: var(--bg-app);
  flex-shrink: 0;
}

/* Resize Handle */
.panelsResizeHandle {
  height: 4px;
  cursor: row-resize;
  background: transparent;
  transition: background-color var(--transition-fast);
}

.panelsResizeHandle:hover {
  background: var(--color-primary-200);
}
```

### 15.12 Resize-Mechanismus (Data Panels)

**State:**
```typescript
const [panelsHeight, setPanelsHeight] = useState(200);  // Initial: 200px
```

**Handler:**
```typescript
const handlePanelsResizeStart = useCallback((e: React.MouseEvent) => {
  e.preventDefault();
  isResizing.current = true;

  const handleMouseMove = (moveEvent: MouseEvent) => {
    if (!isResizing.current || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const newHeight = rect.bottom - moveEvent.clientY;
    // Constraint: min 100px, max = container height - 100px
    setPanelsHeight(Math.min(Math.max(newHeight, 100), rect.height - 100));
  };

  const handleMouseUp = () => {
    isResizing.current = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);
}, []);
```

### 15.13 Zusammenfassung der aktuellen Implementierung

| Feature | Status | Beschreibung |
|---------|--------|--------------|
| **Sidebar Toggle** | ✅ | Button im ChatHeader |
| **Tree Hierarchie** | ✅ | TraceRoot + TreeItems mit Expand/Collapse |
| **Node Selektion** | ✅ | Klick selektiert, Sync mit Canvas (in Dialog) |
| **Data Panels** | ✅ | Logs, Input/Output, Metadata |
| **Collapsible Sections** | ✅ | VS Code-style Panels |
| **JSON Viewer** | ✅ | Collapsible für große Objekte |
| **Resize Handle** | ✅ | Vertikale Größenänderung der Data Panels |
| **Message-to-Trace Sync** | ✅ | Bidirektionale Synchronisation |
| **Fullscreen Button** | ✅ | Öffnet TracingVisualDialog |

---

