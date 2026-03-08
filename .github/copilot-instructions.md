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

## License

MIT License — see [LICENSE](../LICENSE)
