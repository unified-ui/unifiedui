# Copilot Instructions — unified-ui

## Project Overview

**unified-ui** is a unified integration platform for AI agent systems that provides a single, cohesive interface for managing agents across multiple platforms including Microsoft Foundry, n8n, LangGraph, Copilot, and custom solutions.

This is the **entry repository** containing project documentation, architecture overviews, and integration guides. It does not contain application code.

## Repository Structure

The unified-ui platform consists of the following service repositories:

| Repository | Description | Language |
|------------|-------------|----------|
| [unified-ui-platform-service](https://github.com/unified-ui/unified-ui-platform-service) | Core backend API — tenants, agents, credentials, RBAC | Python (FastAPI) |
| [unified-ui-agent-service](https://github.com/unified-ui/unified-ui-agent-service) | Agent execution, SSE streaming, tracing | Go (Gin) |
| [unified-ui-frontend-service](https://github.com/unified-ui/unified-ui-frontend-service) | Web UI — React SPA | TypeScript (React) |
| [unified-ui-re-act-agent-service](https://github.com/unified-ui/unified-ui-re-act-agent-service) | ReACT Agent execution engine | Python (FastAPI) |
| [unifiedui-sdk](https://github.com/unified-ui/unifiedui-sdk) | Python SDK for external integrations | Python |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Frontend Service                               │
│                        (React / TypeScript)                              │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTPS/SSE
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Agent Service (Go)                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │   Foundry    │ │     n8n      │ │   Copilot    │ │ ReACT Agent  │   │
│  │   Adapter    │ │   Adapter    │ │   Adapter    │ │   Client     │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└───────────┬─────────────┬────────────────┬────────────────┬─────────────┘
            │             │                │                │
            ▼             ▼                ▼                ▼
    ┌───────────┐  ┌───────────┐   ┌───────────┐   ┌────────────────────┐
    │ Microsoft │  │    n8n    │   │  Copilot  │   │ ReACT Agent Service│
    │  Foundry  │  │ Workflows │   │    API    │   │   (Python/SDK)     │
    └───────────┘  └───────────┘   └───────────┘   └────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        Platform Service (Python)                         │
│                     Tenants, RBAC, Credentials, Agents                   │
└─────────────────────────────────────────┬───────────────────────────────┘
                                          │
                      ┌───────────────────┼───────────────────┐
                      ▼                   ▼                   ▼
               ┌───────────┐       ┌───────────┐       ┌───────────┐
               │ PostgreSQL│       │   Redis   │       │   Vault   │
               │           │       │  (Cache)  │       │ (Secrets) │
               └───────────┘       └───────────┘       └───────────┘
```

## Key Features

- **Multi-Platform Integration**: Microsoft Foundry, n8n, LangGraph, Copilot, custom REST
- **Unified Chat Interface**: Single chat experience for all AI agents
- **Centralized Tracing**: Observability across all agent types
- **Multi-Tenant RBAC**: Enterprise-grade access control
- **SSE Streaming**: Real-time response streaming with 22 event types

## Documentation

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview and quick start |
| [docs/n8n-unified-ui-integration/](../docs/n8n-unified-ui-integration/) | n8n integration guide |

## Contributing

Please see the individual service repositories for contribution guidelines:

- Each service has its own `CONTRIBUTING.md` and coding standards
- All services use Conventional Commits for commit messages
- PRs should be made against the respective service repository

## Development Setup

Refer to the README.md files in each service repository for setup instructions.

### Service Ports (Local Development)

| Service | Port |
|---------|------|
| Platform Service | 8000 |
| Agent Service | 8085 |
| ReACT Agent Service | 8086 |
| Frontend | 5173 |

## Copilot Self-Debugging — REQ 007

This entry repo hosts the **debug toolkit** that lets Copilot inspect and call any service end-to-end without an OAuth flow. See `scripts/debug/` and `docker/local/docker-compose.debug.yml`.

### Components

| Path | Purpose |
|------|---------|
| `scripts/debug/README.md` | Cheatsheet (DB connection strings, common recipes) |
| `scripts/debug/db_inspect.py` | Python REPL helper — `pg`, `mongo`, `redis` globals |
| `scripts/debug/backdoor_call.py` | HTTP helper — calls platform / agent service as any synthesised user via `X-Debug-*` headers |
| `scripts/debug/foundry_smoke.py` | Foundry helper — prompt iteration / model smoke tests via the project's OpenAI v1 endpoint |
| `docker/local/docker-compose.debug.yml` | Compose override that flips `ENABLE_DEBUG_BACK_DOOR=true` on platform + agent service |

### One-command setup

```bash
cd unifiedui/docker/local
export DEBUG_BACK_DOOR_SECRET=$(openssl rand -hex 32)
docker compose -f docker-compose.yml -f docker-compose.debug.yml up -d
```

Then in another shell:
```bash
cd unifiedui/scripts/debug
export DEBUG_BACK_DOOR_SECRET=<same secret>
uv run --with httpx python -i backdoor_call.py
>>> platform.get("/identity/me")
```

### Backdoor headers (across services)

| Header | Required | Notes |
|--------|----------|-------|
| `X-Debug-Backdoor` | yes | Must equal `DEBUG_BACK_DOOR_SECRET` (≥ 32 chars) |
| `X-Debug-User-Id` | yes | Becomes `oid` claim |
| `X-Debug-User-Upn` | yes | Becomes `mail` / `upn` |
| `X-Debug-User-Name` | no | Display name |
| `X-Debug-Tenant-Id` | no | AAD tenant id |
| `X-Debug-Groups` | no | Comma-separated group ids |
| `X-Debug-Roles` | no | Comma-separated role names |

Identical contract on platform-service (Python) and agent-service (Go). Synthesises a `MockIdentityToken` → flows through normal RBAC pipeline → no special-case routing.

### Production guards

- Backdoor refuses to start when `DEPLOYMENT_MODE=production` (both services).
- `ENABLE_DEBUG_BACK_DOOR=true` requires `ALLOW_MOCK_IDENTITY_PROVIDER=true` (platform-service).
- Healthcheck endpoints expose `debug_backdoor_enabled: bool` so the frontend / monitoring can detect the flag.
- Frontend shows a persistent yellow banner whenever the active session uses the debug provider.

## Microsoft Foundry — Copilot Workflow

The platform-service `.env` ships with `FOUNDRY_PROJECT_*` variables for Copilot debugging. They are NOT consumed by the running services — they exist purely so Copilot can iterate on prompts against a real Foundry project.

### What Copilot CAN do (api-key only, no AAD)

- `foundry_smoke.ping()` — verify a deployment is reachable
- `foundry_smoke.ask("gpt-4.1", "...", system="...")` — single-turn prompt iteration
- `foundry_smoke.chat(...)` — multi-turn conversation
- `foundry_smoke.list_models()` — list catalog model IDs

```bash
cd unified-ui-platform-service && set -a && source .env && set +a
cd ../unifiedui/scripts/debug
uv run --with httpx python -i foundry_smoke.py
>>> ask("gpt-4.1", "Summarise REQ 007 in one sentence.")
```

### What Copilot CANNOT do (without explicit user setup)

Foundry **agent CRUD** (create / list / delete `assistants`) requires AAD identity in the Foundry project's tenant + Azure AI Developer role. The shipped API key does NOT grant this. If the user wants Copilot to manage agents:

1. User runs `az login --tenant <foundry-tenant>` and grants Copilot's identity Azure AI Developer on the project
2. Use the `foundry` MCP tools (`agent_get`, `agent_update`, `agent_invoke`, `agent_delete`)

### Naming convention — MANDATORY

Any Foundry resource Copilot creates (agent, dataset, evaluator, deployment) MUST be prefixed with **`co-debug-`**, e.g. `co-debug-summary-test`, `co-debug-eval-2026-04`. This lets the user bulk-delete Copilot's experiments via the Foundry portal without touching production assets. **Never modify or delete a resource that is NOT prefixed `co-debug-`.**

## License

MIT License — see [LICENSE](../LICENSE)
