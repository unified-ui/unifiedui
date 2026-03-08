# ReACT Agent Reasoning UI Concept

## Overview

The ReACT Agent streams **22 SSE event types** during execution. Beyond the standard `TEXT_STREAM` content, the agent emits structured events for its internal reasoning process: thinking steps, tool calls, multi-agent coordination, planning, and synthesis. This concept defines how these events are rendered in the chat UI with a collapsible reasoning toggle — similar to GitHub Copilot's "Thinking..." or Claude's "Extended Thinking" patterns.

## SSE Event Categories

| Category | Events | Description |
|----------|--------|-------------|
| **Content** | `TEXT_STREAM` | Final assistant response text |
| **Reasoning** | `REASONING_START`, `REASONING_STREAM`, `REASONING_END` | Agent's internal thinking/chain-of-thought |
| **Tool Call** | `TOOL_CALL_START`, `TOOL_CALL_STREAM`, `TOOL_CALL_END` | Tool invocation with name, input, and result |
| **Plan** | `PLAN_START`, `PLAN_STREAM`, `PLAN_COMPLETE` | Multi-step execution plan |
| **Sub-Agent** | `SUB_AGENT_START`, `SUB_AGENT_STREAM`, `SUB_AGENT_END` | Delegated sub-agent execution |
| **Synthesis** | `SYNTHESIS_START`, `SYNTHESIS_STREAM` | Final answer synthesis from gathered data |
| **Infrastructure** | `STREAM_START`, `STREAM_END`, `STREAM_NEW_MESSAGE`, `MESSAGE_COMPLETE`, `TITLE_GENERATION`, `ERROR`, `TRACE` | Stream lifecycle and metadata |

## UI Design

### 1. Reasoning Toggle (Collapsible Section)

Every assistant message from a ReACT agent gets a **reasoning section** rendered above the final response. It is collapsed by default after streaming ends, but expanded during active streaming.

```
┌─────────────────────────────────────────────────────┐
│ 🤖 Assistant                                        │
│                                                     │
│ ▼ Reasoning (3 steps · 2 tools · 4.2s)             │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 💭 Thinking                                     │ │
│ │ I need to look up the current weather...        │ │
│ │                                                 │ │
│ │ 🔧 get_weather(location="Berlin")               │ │
│ │ ┌─ Result ────────────────────────────────────┐ │ │
│ │ │ {"temp": 18, "condition": "partly cloudy"}  │ │ │
│ │ └─────────────────────────────────────────────┘ │ │
│ │                                                 │ │
│ │ 💭 Thinking                                     │ │
│ │ Now I have the weather data, let me format...   │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ The current weather in Berlin is 18°C, partly       │
│ cloudy. Perfect for a walk in the park! 🌤️          │
│                                                     │
│ ─── 👍 👎 📋 ───                                     │
└─────────────────────────────────────────────────────┘
```

### 2. Reasoning Step Types

Each step within the reasoning section is rendered with a distinct visual indicator:

| Step Type | Icon | Label | Content |
|-----------|------|-------|---------|
| Reasoning | 💭 | "Thinking" | Streamed reasoning text (Markdown) |
| Tool Call | 🔧 | Tool name | Tool name + input params + result (code block) |
| Plan | 📋 | "Plan" | Numbered plan steps (Markdown) |
| Sub-Agent | 🤖 | Agent name | Sub-agent name + delegated task + result |
| Synthesis | ✨ | "Synthesizing" | Synthesis streamed text |

### 3. Streaming Behavior

During active streaming, the reasoning section is **always expanded** and auto-scrolls:

```
┌─────────────────────────────────────────────────────┐
│ 🤖 Assistant                                        │
│                                                     │
│ ▼ Reasoning (streaming...)                          │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 💭 Thinking                                     │ │
│ │ I need to look up the current weather in...█    │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ █ (waiting for response...)                         │
└─────────────────────────────────────────────────────┘
```

After `STREAM_END`:
- Reasoning section **collapses automatically**
- Summary line shows: step count, tool count, duration
- User can toggle open/closed manually

### 4. Tool Call Rendering

Tool calls have three phases rendered inline:

```
🔧 get_weather
├── Input: {"location": "Berlin", "units": "metric"}
└── Result: {"temp": 18, "condition": "partly cloudy", "humidity": 65}
```

- **Start** (`TOOL_CALL_START`): Shows tool name with spinner
- **Stream** (`TOOL_CALL_STREAM`): Streams input/intermediate output
- **End** (`TOOL_CALL_END`): Shows final result in a collapsible code block

### 5. Multi-Agent Rendering

Sub-agent execution is shown as a nested block:

```
🤖 research-agent
├── Task: "Find recent papers on quantum computing"
├── 💭 Thinking: Searching academic databases...
├── 🔧 search_papers(query="quantum computing 2024")
└── Result: Found 3 relevant papers...
```

### 6. Plan Rendering

Plans are shown as a numbered checklist that updates as steps complete:

```
📋 Execution Plan
  1. ✅ Look up current weather data
  2. ✅ Check for weather alerts
  3. ⏳ Format response with recommendations
```

## State Management

### `useReActChat` Hook

A new hook extending `useChat` with reasoning-specific state:

```typescript
interface ReActStreamState {
  reasoningSteps: ReasoningStep[];
  isReasoningExpanded: boolean;
  activeStepType: 'reasoning' | 'tool_call' | 'plan' | 'sub_agent' | 'synthesis' | null;
  activeStepContent: string;
  toolCalls: ToolCallState[];
  planSteps: PlanStep[];
  subAgents: SubAgentState[];
}

interface ReasoningStep {
  id: string;
  type: 'reasoning' | 'tool_call' | 'plan' | 'sub_agent' | 'synthesis';
  content: string;
  toolName?: string;
  toolInput?: string;
  toolResult?: string;
  agentName?: string;
  startedAt: number;
  completedAt?: number;
}
```

### Event-to-State Mapping

| SSE Event | State Update |
|-----------|-------------|
| `REASONING_START` | Push new step `{type: 'reasoning'}`, set `activeStepType` |
| `REASONING_STREAM` | Append to `activeStepContent` |
| `REASONING_END` | Finalize step, clear `activeStepType` |
| `TOOL_CALL_START` | Push new step `{type: 'tool_call', toolName}` |
| `TOOL_CALL_STREAM` | Append tool stream content |
| `TOOL_CALL_END` | Finalize tool result |
| `PLAN_START` | Push new step `{type: 'plan'}` |
| `PLAN_STREAM` | Append plan content |
| `PLAN_COMPLETE` | Finalize plan |
| `SUB_AGENT_START` | Push new step `{type: 'sub_agent', agentName}` |
| `SUB_AGENT_STREAM` | Append sub-agent content |
| `SUB_AGENT_END` | Finalize sub-agent |
| `SYNTHESIS_START` | Push new step `{type: 'synthesis'}` |
| `SYNTHESIS_STREAM` | Append synthesis content |
| `STREAM_END` | Collapse reasoning, compute summary |

## Component Hierarchy

```
ChatContent
└── MessageBubble (type=assistant, from ReACT agent)
    ├── ReasoningSection              ← new component
    │   ├── ReasoningSummaryBar       ← collapsed header with toggle
    │   └── ReasoningStepList         ← expanded content
    │       ├── ReasoningStep (💭)
    │       ├── ToolCallStep (🔧)
    │       ├── PlanStep (📋)
    │       ├── SubAgentStep (🤖)
    │       └── SynthesisStep (✨)
    └── MarkdownContent               ← final response (existing)
```

## Playground Integration

The `ReActAgentDeveloperPage` right panel currently has a non-functional playground. The integration:

1. Playground sends messages via a **new API route** on the Agent Service: `POST /api/v1/agent-service/tenants/{tenantId}/playground/react-agent/stream`
2. This route receives the full agent config (from the dev page left panel) + the message
3. The Agent Service forwards to the ReACT Service at port 8086
4. SSE events stream back and render with the full reasoning UI
5. No conversation persistence — playground messages are local state only

### Playground-specific Behavior

- Always show reasoning expanded (developer mode)
- Show raw SSE event log in a debug panel (optional toggle)
- Show execution timing per step
- No reactions, no message persistence
- Reset button to clear chat

## File Structure

```
src/
├── components/
│   └── chat/
│       ├── ReasoningSection/
│       │   ├── ReasoningSection.tsx
│       │   ├── ReasoningSummaryBar.tsx
│       │   ├── ReasoningStepList.tsx
│       │   └── steps/
│       │       ├── ReasoningStep.tsx
│       │       ├── ToolCallStep.tsx
│       │       ├── PlanStep.tsx
│       │       ├── SubAgentStep.tsx
│       │       └── SynthesisStep.tsx
│       └── ChatContent/
│           └── ChatContent.tsx        ← extend with ReasoningSection
├── hooks/
│   └── chat/
│       ├── useChat.ts                 ← existing
│       └── useReActChat.ts            ← new hook for reasoning state
└── api/
    ├── types.ts                       ← SSE types already added
    └── client.ts                      ← callbacks already added
```

## Design Decisions

1. **Reasoning is per-message** — Each assistant message owns its reasoning state. Multiple messages in one conversation can each have their own reasoning sections.

2. **Collapsed by default after streaming** — To avoid overwhelming non-technical users. Developers in the playground always see it expanded.

3. **Markdown rendering in reasoning** — Reasoning text and tool results are rendered as Markdown for readability (code blocks, lists, etc.).

4. **No separate trace view for reasoning** — Reasoning steps are shown inline in the message. The existing trace sidebar shows the full execution trace (from the tracing system), which is complementary but separate.

5. **Graceful degradation** — If a ReACT agent only emits `TEXT_STREAM` (no reasoning events), the message renders exactly like a standard chat message. The reasoning section only appears when reasoning events are received.
