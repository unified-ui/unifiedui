# Tracing Visualization Dialog - Technical Specification

> **Purpose**: This document serves as a complete implementation specification for a modular Tracing Visualization Dialog in React. It is designed to be used as a prompt for AI-assisted code generation with Claude Opus 4.5.

---

## 1. Project Context

### 1.1 Technology Stack
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Framework**: Mantine v7+
- **Canvas Library**: `@xyflow/react` (already installed)
- **Styling**: CSS Modules + CSS Custom Properties (see `src/styles/variables.css`)
- **Routing**: React Router v6

### 1.2 Design System
All styling MUST use CSS Custom Properties from `src/styles/variables.css`:
```css
/* Colors */
--color-primary-{50-900}, --color-gray-{0-900}
--color-success-500, --color-error-500, --color-warning-500

/* Semantic */
--bg-app, --bg-paper, --text-primary, --text-secondary, --border-default

/* Spacing */
--spacing-xs (4px), --spacing-sm (8px), --spacing-md (16px), --spacing-lg (24px), --spacing-xl (32px)

/* Other */
--radius-sm/md/lg, --shadow-sm/md/lg, --font-weight-medium/semibold/bold
```

### 1.3 File Location
All tracing components go in: `src/components/tracing/`

---

## 2. Data Model

### 2.1 TypeScript Types (already defined in `src/api/types.ts`)

```typescript
// Trace Context Type
export type TraceContextType = 'conversation' | 'autonomous_agent';

// Node Types
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

// Node Status
export const TraceNodeStatus = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  SKIPPED: 'skipped',
  CANCELLED: 'cancelled',
} as const;

// Node Data IO
export interface TraceNodeDataIO {
  text?: string;
  arguments?: Record<string, unknown>;
  extraData?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

// Node Data
export interface TraceNodeData {
  input?: TraceNodeDataIO | null;
  output?: TraceNodeDataIO | null;
}

// Single Node (hierarchical - can have sub-nodes)
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
  nodes?: TraceNodeResponse[];  // SUB-NODES (hierarchical!)
  metadata?: Record<string, unknown>;
  createdAt?: string;
  updatedAt?: string;
}

// Full Trace Response
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

// API Response
export interface FullTracesListResponse {
  traces: FullTraceResponse[];
  total: number;
}
```

### 2.2 Sample Data Structure
```
Trace (Root)
├── referenceName: "Microsoft Foundry Conversation"
├── contextType: "conversation"
├── referenceId: "conv_abc123"
├── referenceMetadata: { project_endpoint: "...", ... }
├── logs: ["log1", "log2"]
└── nodes: [
    ├── Node 1 (User Message)
    │   ├── type: "llm", status: "completed"
    │   ├── data.input.text: "Hello"
    │   └── nodes: []  (no sub-nodes)
    │
    ├── Node 2 (SendActivity - Container)
    │   ├── type: "workflow", status: "completed"
    │   └── nodes: [  (HAS SUB-NODES!)
    │       ├── SubNode 2.1 (Assistant Response)
    │       ├── SubNode 2.2 (Invoke Azure Agent)
    │       └── SubNode 2.3 (End Conversation)
    │   ]
    │
    └── Node 3 (User Message)
        ├── type: "llm", status: "completed"
        └── nodes: []
]
```

---

## 3. Component Architecture

### 3.1 Module Overview

```
src/components/tracing/
├── TracingContext.tsx          # React Context for shared state
├── TracingVisualDialog.tsx     # Main modal dialog (container)
├── TracingVisualDialog.module.css
│
├── TracingCanvasView.tsx       # @xyflow/react based canvas
├── TracingCanvasView.module.css
├── CanvasNode.tsx              # Custom xyflow node component
├── CanvasEdge.tsx              # Custom xyflow edge component (optional)
│
├── TracingHierarchyView.tsx    # Tree hierarchy sidebar
├── TracingHierarchyView.module.css
│
├── TracingDataSection.tsx      # Bottom panel (Logs + Input/Output)
├── TracingDataSection.module.css
│
├── TracingSubHeader.tsx        # Fixed info bar above canvas
├── TracingSubHeader.module.css
│
└── index.ts                    # Barrel exports
```

### 3.2 Context State (TracingContext.tsx)

```typescript
interface TracingContextState {
  // Data
  traces: FullTraceResponse[];
  selectedTrace: FullTraceResponse | null;
  selectedNode: TraceNodeResponse | null;
  
  // UI State
  layoutDirection: 'horizontal' | 'vertical';
  zoomLevel: number;
  collapsedNodeIds: Set<string>;
  
  // Actions
  selectTrace: (traceId: string) => void;
  selectNode: (nodeId: string | null) => void;
  toggleNodeCollapse: (nodeId: string) => void;
  setLayoutDirection: (dir: 'horizontal' | 'vertical') => void;
  setZoomLevel: (level: number) => void;
  centerOnNode: (nodeId: string) => void;  // For canvas navigation
}
```

---

## 4. Component Specifications

### 4.1 TracingVisualDialog (Main Container)

**Purpose**: Modal dialog containing all tracing visualization components.

**Props**:
```typescript
interface TracingVisualDialogProps {
  opened: boolean;
  onClose: () => void;
  traces: FullTraceResponse[];
  initialTraceId?: string;  // Pre-select a specific trace
}
```

**Layout** (inside Modal):
```
┌─────────────────────────────────────────────────────────────────┐
│ [Header] Icon + "Tracing for {referenceName}" + Close Button   │
├─────────────────────────────────────────────────────────────────┤
│ [SubHeader] trace_id | node_name | startAt-endAt | status      │
├───────────────────────────────────────┬─────────────────────────┤
│                                       │                         │
│  ┌─────────────────────────────────┐  │   [Hierarchy View]     │
│  │                                 │  │   - Tree structure      │
│  │       [Canvas View]             │  │   - Collapsible items   │
│  │       @xyflow/react             │  │   - Click to select     │
│  │                                 │  │                         │
│  │       (2/3 height)              │  │   (Full height, 1/4     │
│  │                                 │  │    width, resizable)    │
│  └─────────────────────────────────┘  │                         │
│  ┌─────────────────────────────────┐  │                         │
│  │       [Data Section]            │  │                         │
│  │       Logs | Input | Output     │  │                         │
│  │       (1/3 height, resizable)   │  │                         │
│  └─────────────────────────────────┘  │                         │
│                                       │                         │
│              (3/4 width)              │                         │
└───────────────────────────────────────┴─────────────────────────┘
```

**Note**: SubHeader is more a floating label over the canvas view, not a real sub header und not over the [Hierarchy View].

**Modal Settings**:
- Size: `calc(100vw - 80px)` width, `calc(100vh - 60px)` height
- Rounded corners: `radius="lg"`
- Overlay: Blur effect
- NOT fullScreen (user can see app behind)

**Resizable Panels**:
- Vertical resize between Canvas and Data Section
- Horizontal resize between Main Area and Hierarchy

---

### 4.2 TracingCanvasView (@xyflow/react)

**Purpose**: Visual workflow canvas showing nodes and their connections.

**Implementation with @xyflow/react**:
```typescript
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  type Node,
  type Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
```

**Node Transformation**:
Convert `TraceNodeResponse[]` to xyflow `Node[]`:
```typescript
interface CanvasNodeData {
  name: string;
  type: TraceNodeType | string;
  status: TraceNodeStatus | string;
  duration?: number;
  hasSubNodes: boolean;
  isCollapsed: boolean;
}

// Each TraceNodeResponse becomes a Node
// Sub-nodes become separate nodes with edges from parent
```

**Edge Transformation**:
```typescript
// Sequential edges: Node[i] → Node[i+1] (for root nodes)
// Parent-Child edges: Parent → Child (for sub-nodes)

const edge: Edge = {
  id: `${sourceId}-${targetId}`,
  source: sourceId,
  target: targetId,
  type: 'smoothstep',  // or 'bezier'
  markerEnd: {
    type: MarkerType.ArrowClosed,
    color: '#42a5f5',  // primary blue
  },
  style: { stroke: '#42a5f5', strokeWidth: 2 },
  animated: false,  // true for 'running' status
};
```

**Layout Algorithm**:
```typescript
// Horizontal mode (default):
// - Root nodes: left-to-right
// - Sub-nodes: branch downward from parent

// Vertical mode:
// - Root nodes: top-to-bottom
// - Sub-nodes: branch rightward from parent

// Use dagre or elkjs for automatic layout:
// npm install @dagrejs/dagre
```

**Custom Node Component (CanvasNode)**:
```typescript
interface CanvasNodeProps {
  data: CanvasNodeData;
  selected: boolean;
}

// Visual:
// ┌────────────────────────────┐
// │ [StatusDot] [Icon] Name    │
// │                   Duration │
// └────────────────────────────┘
//
// - Width: ~180px, Height: ~50px
// - Rounded corners (more rounded on first/last)
// - Border color based on status:
//   - completed: green (--color-success-500)
//   - failed: red (--color-error-500)
//   - running: orange (--color-warning-500)
//   - pending: gray (--color-gray-400)
// - Selected: Add shadow
// - Icon based on node.type
```

**Icon Mapping**:
```typescript
const nodeTypeIcons = {
  agent: IconRobot,
  tool: IconTool,
  llm: IconBrain,
  chain: IconLink,
  workflow: IconChartDots,
  http: IconWorldWww,
  code: IconCode,
  function: IconCode,
  custom: IconForms,
};
```

**Controls**:
- Zoom In/Out buttons
- Reset view button
- Layout toggle (horizontal/vertical)
- Mini-map (optional, bottom-right)

**Interactions**:
- Pan: Click and drag on canvas
- Zoom: Scroll wheel or pinch (trackpad)
- Select node: Click on node → updates context → Data Section shows node details
- Center on node: When node selected in Hierarchy, canvas navigates to it

---

### 4.3 TracingHierarchyView

**Purpose**: Tree-structured navigation of traces and nodes.

**Layout**:
```
┌─────────────────────────────────┐
│ [Trace 1 - referenceName]   ▾  │  ← Collapsible
│   │                            │
│   ├─[llm] User Message     ✓   │  ← Status icon
│   │                            │
│   ├─[workflow] SendActivity ✓  │  ← Has children, collapsible
│   │   │                        │
│   │   ├─[llm] Assistant... ✓   │
│   │   └─[llm] Assistant... ✓   │
│   │                            │
│   └─[llm] User Message     ✓   │
│                                │
│ [Trace 2 - referenceName]   ▾  │  ← Only for conversations
│   └─ ...                       │     with multiple traces
└─────────────────────────────────┘
```

**Features**:
- Curved connecting lines (like Foundry/VSCode tree)
- Indentation per hierarchy level (~20px)
- Badge showing `node.type`
- Name (truncated with `...` if too long)
- Status icon (checkmark, X, spinner, etc.)
- Click to select (updates Canvas + Data Section)
- Expand/Collapse for nodes with sub-nodes

**Styling**:
```css
.hierarchyItem {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  cursor: pointer;
  border-radius: var(--radius-sm);
}

.hierarchyItem:hover {
  background: var(--bg-hover);
}

.hierarchyItem.selected {
  background: var(--color-primary-50);
}

.connector {
  /* Curved line connecting to parent */
  border-left: 1px solid var(--border-default);
  border-bottom: 1px solid var(--border-default);
  border-radius: 0 0 0 8px;
}
```

---

### 4.4 TracingDataSection

**Purpose**: Display details for selected node (or root trace).

**Layout**:
```
┌──────────────┬──────────────────────────────────────────┐
│              │  [Tabs: Input/Output | Metadata]         │
│   [Logs]     ├──────────────────────────────────────────┤
│              │  ┌──────────────┬──────────────┐         │
│   - log 1    │  │   [Input]    │   [Output]   │         │
│   - log 2    │  │              │              │         │
│   - log 3    │  │  Text:       │  Text:       │         │
│              │  │  "Hello"     │  "Hi there"  │         │
│   (1/4 w)    │  │              │              │         │
│              │  │  ▸ metadata  │  ▸ metadata  │         │
│              │  │  ▸ extraData │  ▸ extraData │         │
│              │  │              │              │         │
│              │  │   (1/2)      │    (1/2)     │         │
│              │  └──────────────┴──────────────┘         │
│              │              (3/4 width)                 │
└──────────────┴──────────────────────────────────────────┘
```

**State-dependent content**:
```typescript
if (selectedNode === null) {
  // Show ROOT data:
  // - Logs: trace.logs
  // - Metadata tab: trace.referenceMetadata as JSON
  // - No Input/Output tab
} else {
  // Show NODE data:
  // - Logs: selectedNode.logs
  // - Input: selectedNode.data?.input
  // - Output: selectedNode.data?.output
  // - Metadata: selectedNode.metadata
}
```

**Input/Output Display**:
```typescript
// For each (input/output):
// 1. Text (if exists) - displayed prominently
// 2. metadata - collapsible JSON viewer
// 3. extraData - collapsible JSON viewer
// 4. Any other fields - collapsible JSON viewer

// Use Mantine's JsonInput or a custom JSON tree viewer
// Or use react-json-view-lite for collapsible JSON
```

**Resizable**:
- Horizontal resize between Logs and Input/Output panels
- Vertical resize between Input and Output (optional)

---

### 4.5 TracingSubHeader

**Purpose**: Fixed info bar showing current selection details.

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│ TraceID: abc123  │  Node: User Message  │  12:45:00 → 12:45:01  │  ✓ completed  │
└─────────────────────────────────────────────────────────────────┘
```

**Content**:
```typescript
// Always show:
// - trace.id (shortened)

// If node selected:
// - node.name
// - node.startAt → node.endAt (formatted time)
// - node.status with icon

// If no node selected:
// - "Root"
// - trace.createdAt
// - contextType badge
```

---

## 5. API Integration

### 5.1 Endpoints

**Conversation Traces**:
```
GET /api/v1/agent-service/tenants/{tenantId}/conversations/{conversationId}/traces
Response: { traces: FullTraceResponse[], total: number }
```

**Autonomous Agent Traces**:
```
GET /api/v1/agent-service/tenants/{tenantId}/autonomous-agents/{autonomousAgentId}/traces
Response: { traces: FullTraceResponse[], total: number }
```

### 5.2 API Client Methods (add to `src/api/client.ts`)

```typescript
// In UnifiedUIAPIClient class:

async getConversationTraces(
  tenantId: string,
  conversationId: string
): Promise<FullTracesListResponse> {
  return this.request('GET', 
    `/agent-service/tenants/${tenantId}/conversations/${conversationId}/traces`
  );
}

async getAutonomousAgentTraces(
  tenantId: string,
  autonomousAgentId: string
): Promise<FullTracesListResponse> {
  return this.request('GET',
    `/agent-service/tenants/${tenantId}/autonomous-agents/${autonomousAgentId}/traces`
  );
}
```

---

## 6. Development Page

### 6.1 Route
```
/dev/tracing?conversationId={id}
/dev/tracing?autonomousAgentId={id}
```

### 6.2 TracingDialogDevelopmentPage

```typescript
// src/pages/TracingDialogDevelopmentPage/TracingDialogDevelopmentPage.tsx

export const TracingDialogDevelopmentPage: FC = () => {
  const [searchParams] = useSearchParams();
  const { apiClient, selectedTenant } = useIdentity();
  
  const conversationId = searchParams.get('conversationId');
  const autonomousAgentId = searchParams.get('autonomousAgentId');
  
  const [traces, setTraces] = useState<FullTraceResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpened, setDialogOpened] = useState(false);

  useEffect(() => {
    const fetchTraces = async () => {
      if (!apiClient || !selectedTenant) return;
      
      try {
        let response: FullTracesListResponse;
        if (conversationId) {
          response = await apiClient.getConversationTraces(
            selectedTenant.id, conversationId
          );
        } else if (autonomousAgentId) {
          response = await apiClient.getAutonomousAgentTraces(
            selectedTenant.id, autonomousAgentId
          );
        } else {
          return;
        }
        
        setTraces(response.traces);
        setDialogOpened(true);  // Open dialog when data loaded
      } catch (error) {
        console.error('Failed to fetch traces:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchTraces();
  }, [apiClient, selectedTenant, conversationId, autonomousAgentId]);

  return (
    <MainLayout>
      <Container>
        {loading && <Loader />}
        {!loading && traces.length === 0 && (
          <Alert>No traces found. Provide ?conversationId= or ?autonomousAgentId=</Alert>
        )}
      </Container>
      
      <TracingVisualDialog
        opened={dialogOpened}
        onClose={() => setDialogOpened(false)}
        traces={traces}
      />
    </MainLayout>
  );
};
```

### 6.3 Add Route
In `src/routes/index.tsx`:
```typescript
{
  path: '/dev/tracing',
  element: <TracingDialogDevelopmentPage />,
}
```

---

## 7. Modular Reuse Scenarios

### 7.1 In Chat View (Quick Hierarchy Only)
```tsx
// Just the hierarchy, no canvas
<TracingProvider traces={traces}>
  <TracingHierarchyView compact />
</TracingProvider>
```

### 7.2 In Autonomous Agent Page (Full Dialog)
```tsx
<TracingVisualDialog
  opened={showTracing}
  onClose={() => setShowTracing(false)}
  traces={agentTraces}
/>
```

### 7.3 Embedded Canvas Only
```tsx
<TracingProvider traces={traces}>
  <TracingCanvasView width="100%" height={400} />
</TracingProvider>
```

---

## 8. Implementation Checklist

### Phase 1: Foundation
- [ ] Create `TracingContext.tsx` with state management
- [ ] Create basic `TracingVisualDialog.tsx` with layout structure
- [ ] Add API client methods for fetching traces
- [ ] Create development page with route

### Phase 2: Canvas (Priority)
- [ ] Install/configure @xyflow/react
- [ ] Create `CanvasNode.tsx` custom node component
- [ ] Implement node/edge transformation from trace data
- [ ] Add layout algorithm (dagre or custom)
- [ ] Implement pan/zoom controls
- [ ] Add layout direction toggle

### Phase 3: Hierarchy
- [ ] Create `TracingHierarchyView.tsx`
- [ ] Implement tree structure with curved connectors
- [ ] Add expand/collapse functionality
- [ ] Connect to context (selection sync)

### Phase 4: Data Section
- [ ] Create `TracingDataSection.tsx`
- [ ] Implement Logs panel
- [ ] Implement Input/Output display with JSON viewers
- [ ] Add tab switching (Input/Output vs Metadata)
- [ ] Add resizable panels

### Phase 5: Polish
- [ ] Add SubHeader component
- [ ] Implement center-on-node navigation
- [ ] Add keyboard shortcuts
- [ ] Add loading/error states
- [ ] Performance optimization (virtualization for large traces)

---

## 9. Testing Data

Use the following query parameters for testing:
```
# Conversation with multiple nodes
/dev/tracing?conversationId=fe8f3138-3745-4879-b91b-6a3cb5d03303

# Autonomous agent traces
/dev/tracing?autonomousAgentId=741776fc-e59a-4d81-8ca0-129acacaeab2
```

---

## 10. Dependencies

### Required
```json
{
  "@xyflow/react": "^12.x",
  "@mantine/core": "^7.x",
  "@tabler/icons-react": "^3.x"
}
```

### Recommended for Layout
```bash
npm install @dagrejs/dagre
# OR
npm install elkjs
```

### Recommended for JSON Display
```bash
npm install react-json-view-lite
# OR use Mantine's JsonInput in read-only mode
```

---

## 11. Notes for Implementation

1. **@xyflow/react is the source of truth for canvas** - Do not manually calculate node positions or draw SVG lines. Use xyflow's built-in layout, edges, and markers.

2. **Context is key** - All components share state via `TracingContext`. Selection in Hierarchy → updates Canvas + Data Section.

3. **Hierarchical data** - Nodes can have `nodes[]` sub-nodes. Transform these into separate xyflow nodes with parent-child edges.

4. **Status colors** - Use consistent colors from CSS variables:
   - completed: `--color-success-500`
   - failed: `--color-error-500`
   - running: `--color-warning-500`
   - pending/skipped/cancelled: `--color-gray-400/500/600`

5. **Resizable panels** - Use CSS `resize` property or a library like `react-resizable-panels`.

6. **Performance** - For traces with 100+ nodes, consider virtualization in the Hierarchy view.

---

**End of Specification**
