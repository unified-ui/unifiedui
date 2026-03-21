# unified-ui — Local Development Environment

Docker Compose setup for running the complete unified-ui platform locally with hot-reload on all services.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Frontend (React/Vite)                             │
│                      localhost:5173                                  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│   Platform   │  │    Agent     │  │  Sample REST API │
│   Service    │  │   Service    │  │     Agent        │
│  :8000 (Py)  │  │  :8085 (Go)  │  │   :8087 (Py)    │
└──────┬───────┘  └──────┬───────┘  └──────────────────┘
       │                 │
       │                 ▼
       │          ┌──────────────┐
       │          │  ReACT Agent │
       │          │   Service    │
       │          │  :8086 (Py)  │
       │          └──────────────┘
       │
┌──────┴──────────────────────────────────────────────────────────────┐
│                        Infrastructure                                │
│  PostgreSQL :5432 │ MongoDB :27017 │ Redis :6379 │ RabbitMQ :5672   │
│  Vault :8200      │ n8n :5678                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Docker Desktop
- All service repositories cloned as siblings:

```
Developer/repos/
├── unifiedui/                          # This repo (docker/local/)
├── unified-ui-platform-service/
├── unified-ui-agent-service/
├── unified-ui-frontend-service/
├── unified-ui-re-act-agent-service/
└── unifiedui-sample-rest-api-agent/
```

## Quick Start

```bash
# 1. Copy environment file and configure
cp .env.example .env

# 2. Edit .env — set your MSAL credentials and SYSTEM_ADMIN_EMAIL
#    (see "Configuration" section below)

# 3. Start everything
docker compose up -d --build

# 4. Open the app
open http://localhost:5173
```

## Commands

### Start / Stop

```bash
# Start all services (build images first time or after Dockerfile changes)
docker compose up -d --build

# Start without rebuilding (faster, uses cached images)
docker compose up -d

# Stop all services (keeps volumes/data)
docker compose down

# Stop and remove all data (clean slate)
docker compose down -v
```

### Start Individual Services

```bash
# Start only infrastructure
docker compose up -d unifiedui-database unifiedui-docdatabase unifiedui-cache unifiedui-vault unifiedui-message-broker

# Start a specific service (+ its dependencies)
docker compose up -d unifiedui-platform
docker compose up -d unifiedui-frontend

# Rebuild and restart a single service
docker compose up -d --build unifiedui-platform
```

### Logs

```bash
# Follow all logs
docker compose logs -f

# Follow a specific service
docker compose logs -f unifiedui-platform
docker compose logs -f unifiedui-agent
docker compose logs -f unifiedui-frontend

# Show last 50 lines
docker compose logs --tail 50 unifiedui-platform
```

### Status & Debugging

```bash
# Show container status and health
docker compose ps

# Execute a command inside a container
docker exec -it unifiedui-platform bash
docker exec -it unifiedui-agent sh

# Run database migration manually
docker exec -it unifiedui-platform uv run alembic upgrade head
```

## Configuration

### Required: `.env` File

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `MSAL_CLIENT_ID` | Yes | Azure App Registration Client ID |
| `MSAL_CLIENT_SECRET` | Yes | Azure App Registration Client Secret |
| `MSAL_TENANT_ID` | Yes | Azure AD Tenant ID |
| `MSAL_AUTHORITY` | Yes | MSAL authority URL (default: `https://login.microsoftonline.com/common`) |
| `MSAL_API_SCOPE` | Yes | API scope for access tokens |
| `SYSTEM_ADMIN_EMAIL` | Recommended | Email of the system admin (can create organizations). Leave empty to allow any user. |

> Don't have an App Registration yet? Follow the [MSAL App Registration Guide](../../docs/MSAL_APP_REGISTRATION.md) to set one up.
| `AZURE_OPENAI_*` | No | Azure OpenAI credentials for Sample Agent LLM features. Leave empty for echo-only mode. |

All other variables (database passwords, service keys, etc.) have working defaults for local development.

## Services

| Service | Container | Port | Hot Reload |
|---------|-----------|------|------------|
| Frontend | `unifiedui-frontend` | [localhost:5173](http://localhost:5173) | Vite HMR |
| Platform Service | `unifiedui-platform` | [localhost:8000](http://localhost:8000) | uvicorn `--reload` |
| Agent Service | `unifiedui-agent` | [localhost:8085](http://localhost:8085) | Air (Go) |
| ReACT Agent Service | `unifiedui-react-agent` | [localhost:8086](http://localhost:8086) | uvicorn `--reload` |
| Sample REST API Agent | `unifiedui-sample-agent` | [localhost:8087](http://localhost:8087) | uvicorn `--reload` |
| n8n | `n8n` | [localhost:5678](http://localhost:5678) | — |
| PostgreSQL | `unifiedui-database` | localhost:5432 | — |
| MongoDB | `unifiedui-docdatabase` | localhost:27017 | — |
| Redis | `unifiedui-cache` | localhost:6379 | — |
| RabbitMQ | `unifiedui-message-broker` | localhost:5672 / [Management :15672](http://localhost:15672) | — |
| HashiCorp Vault | `unifiedui-vault` | [localhost:8200](http://localhost:8200) | — |

## Hot Reload

All application services support hot reload — edit source code and changes are picked up automatically:

- **Python services** (Platform, ReACT Agent, Sample Agent): `uvicorn --reload` watches for file changes
- **Go service** (Agent): [Air](https://github.com/air-verse/air) watches `.go` files and rebuilds
- **Frontend** (React): Vite HMR with filesystem polling (required for Docker on macOS)

Source code is bind-mounted from the host into containers, so you edit files normally in your IDE.

## File Structure

```
docker/local/
├── docker-compose.yml          # Root orchestrator (includes all *.yml)
├── .env                        # Your local config (git-ignored)
├── .env.example                # Template with documentation
├── infra.yml                   # PostgreSQL, MongoDB, Redis, RabbitMQ, Vault
├── n8n.yml                     # n8n + its PostgreSQL
├── platform.yml                # Platform Service (Python/FastAPI)
├── agent.yml                   # Agent Service (Go/Gin)
├── frontend.yml                # Frontend (React/Vite)
├── react-agent.yml             # ReACT Agent Service (Python/FastAPI)
├── sample-agent.yml            # Sample REST API Agent (Python/FastAPI)
├── dockerfiles/                # Dockerfiles for each service
├── config/
│   └── vite.docker.config.ts   # Vite config override with polling for Docker
├── vault/
│   ├── vault-config.hcl        # Vault server configuration
│   └── vault-entrypoint.sh     # Auto-init, unseal, and seed service keys
└── n8n/
    └── nginx.conf              # (legacy, unused)
```

## Troubleshooting

### Platform Service fails to start
Check logs: `docker compose logs unifiedui-platform`. Common issues:
- Database not ready yet → the service depends on health checks, just wait
- Migration error → run `docker exec -it unifiedui-platform uv run alembic upgrade head`

### Organization dialog doesn't appear after login
Set `SYSTEM_ADMIN_EMAIL` in `.env` to your MSAL login email, then restart the platform service.

### Frontend changes not reflecting
Vite HMR uses filesystem polling in Docker. Changes should appear within ~1 second. If not, check that `src/` is properly mounted: `docker exec -it unifiedui-frontend ls /app/src`

### Vault issues
Vault auto-initializes on first start. If it gets stuck, remove its volume and restart:
```bash
docker compose down unifiedui-vault
docker volume rm unifiedui-local_vault_data
docker compose up -d unifiedui-vault
```

### Clean restart
```bash
docker compose down -v    # Stop everything and delete all data
docker compose up -d --build  # Fresh build
```
