# ADR-001: Consolidation to a Single Monorepo

- **Status**: Under Evaluation
- **Date**: 2026-03-09
- **Decision Makers**: Enrico Goerlitz (sole developer)

---

## Context

The unified-ui platform currently consists of 5 independent service repositories plus 1 documentation repo:

| Repository | Language | Framework | Package Manager |
|------------|----------|-----------|-----------------|
| unified-ui-platform-service | Python 3.13 | FastAPI | uv |
| unified-ui-agent-service | Go 1.24 | Gin | go mod |
| unified-ui-frontend-service | TypeScript | React 19 / Vite | npm |
| unified-ui-re-act-agent-service | Python 3.13 | FastAPI | uv |
| unifiedui-sdk | Python 3.13 | — | uv |
| unifiedui (docs) | — | — | — |

The question is whether to consolidate all of these into a single monorepo.

---

## Claimed Advantages (with Critical Assessment)

### 1. "Shared Python/Go models in one place"

**Partially valid, but overstated.**

- The only real shared code today is the `unifiedui-sdk`, which is consumed by `re-act-agent-service` as a pip dependency (`0.1.3`).
- `platform-service` and `re-act-agent-service` both use Pydantic v2, but they define **independent schemas** for different domains (tenant/RBAC vs. agent execution). These models are not shared — they just use the same framework.
- The Go `agent-service` cannot share Python models at all. It defines its own DTOs in `internal/domain/models/`. A monorepo does not change this fundamental language boundary.
- **Verdict**: The SDK already solves the shared-model problem via versioned package releases. A monorepo adds path-based imports but does not unlock new sharing that the SDK doesn't already provide.

### 2. "Unified release management: one version for all services"

**This is a disadvantage, not an advantage.**

- The services have fundamentally different release cadences. A bug fix in the frontend should not bump the version of the Go agent service.
- With independent repos, you can release `platform-service v2.3.1` without touching `agent-service v1.8.0`. In a monorepo with unified versioning, every release implies all services changed — which is misleading.
- Monorepos that work well (Google, Meta) use **per-package versioning**, not unified versions. That negates this claimed advantage.
- **Verdict**: Independent versioning per service is more accurate and more useful for changelogs, rollbacks, and deployment decisions.

### 3. "Simplified repository configuration"

**True for setup, but adds ongoing complexity.**

- Yes, you deduplicate some config: one `.github/` folder, one `pre-commit-config.yaml`, one CI pipeline.
- But: you now need a **polyglot CI pipeline** that detects which services changed and only runs the relevant test/lint/build steps. This is significantly more complex than 5 simple, single-language pipelines.
- Tools like `ruff`, `golangci-lint`, and `eslint` need separate configurations anyway — they don't simplify by being in one repo.
- **Verdict**: Net neutral. Initial setup is simpler, but ongoing CI/CD maintenance is harder.

### 4. "Single branching concept for one developer"

**Valid today, problematic tomorrow.**

- As a solo developer, switching between repos is friction. A monorepo genuinely reduces this.
- However, this advantage disappears the moment a second contributor joins. At that point, the monorepo requires careful path-based ownership rules (`CODEOWNERS`), selective CI triggers, and merge queue discipline.
- **Verdict**: Legitimate short-term convenience. Should not drive an architectural decision.

---

## Critical Problems with Consolidation

### P1: Polyglot Build Complexity

This is not a homogeneous stack. You have three completely different ecosystems:

| Ecosystem | Build | Lint | Test | Type Check |
|-----------|-------|------|------|------------|
| Python (uv) | `uv sync` | `ruff` | `pytest` | `mypy` |
| Go | `go build` | `golangci-lint` | `go test` | built-in |
| TypeScript (npm) | `npm run build` | `eslint` | `vitest` | `tsc` |

A monorepo CI pipeline must:
- Detect which paths changed (e.g., `services/platform/**` vs. `services/frontend/**`).
- Run only the relevant toolchain.
- Handle different Docker builds per service.
- Manage separate deployment targets.

This is solvable (e.g., GitHub Actions path filters, Nx, Turborepo for JS, custom Makefiles), but it adds **significant overhead** compared to 5 independent, simple pipelines.

### P2: Dependency Isolation Loss

- `platform-service` and `re-act-agent-service` use `uv` with independent `pyproject.toml` files and lock files. In a monorepo, you must decide: shared virtual environment or per-service venvs?
- Shared venv risks dependency conflicts (e.g., different `sqlalchemy` versions). Per-service venvs negates the "shared models" benefit.
- Go modules and npm already isolate by design, but the Python story is messy in monorepos.

### P3: Docker Build Context Bloat

- Each service currently has a lean Docker build context (only its own code).
- In a monorepo, Docker build contexts grow unless you carefully set `.dockerignore` or use multi-stage builds with targeted `COPY` commands. This slows CI builds.

### P4: Git History and Repository Size

- The Go service produces binaries (`agent-service`, `main`, `server` are checked in or built locally). The frontend has `node_modules` and build artifacts.
- `git clone` becomes heavier. `git log` intermixes unrelated service changes.
- Bisecting a bug in one service requires wading through commits from all services.

### P5: Pre-commit Overhead

- Currently each repo runs only its relevant pre-commit hooks (Python repos run `ruff`/`mypy`, Go runs `go-fmt`/`golangci-lint`, frontend runs `eslint`/`tsc`).
- In a monorepo, `pre-commit run --all-files` runs **all hooks on all files**, dramatically slowing down the feedback loop. Path-scoped pre-commit configs exist but are harder to maintain.

### P6: Open Source Perception

- Separate repos look more professional and modular for an open-source project.
- Contributors can clone and work on just the service they care about.
- A monorepo intimidates potential contributors who only want to fix a frontend bug but must clone the entire platform.

---

## What Would a Monorepo Structure Look Like?

If you proceed despite the above concerns, this is a reasonable layout:

```
unified-ui/
├── .github/
│   └── workflows/
│       ├── ci-platform.yml          # path: services/platform/**
│       ├── ci-agent.yml             # path: services/agent/**
│       ├── ci-frontend.yml          # path: services/frontend/**
│       ├── ci-react-agent.yml       # path: services/react-agent/**
│       ├── ci-sdk.yml               # path: sdk/**
│       └── cd-release.yml
├── services/
│   ├── platform/                    # Python/FastAPI — own pyproject.toml, uv.lock
│   │   ├── pyproject.toml
│   │   ├── alembic/
│   │   ├── unifiedui/
│   │   ├── tests/
│   │   └── docker/
│   ├── agent/                       # Go/Gin — own go.mod, go.sum
│   │   ├── go.mod
│   │   ├── cmd/
│   │   ├── internal/
│   │   ├── tests/
│   │   └── docker/
│   ├── frontend/                    # React/TS — own package.json, node_modules
│   │   ├── package.json
│   │   ├── src/
│   │   ├── public/
│   │   └── docker/
│   └── react-agent/                 # Python/FastAPI — own pyproject.toml
│       ├── pyproject.toml
│       ├── app/
│       ├── tests/
│       └── docker/
├── sdk/                             # Python SDK — own pyproject.toml
│   ├── pyproject.toml
│   ├── src/
│   └── tests/
├── docs/
│   ├── adr/
│   └── ...
├── docker-compose.yml               # Orchestrates all services locally
├── Makefile                         # Top-level commands: make test-all, make lint-all
├── .pre-commit-config.yaml
├── CONTRIBUTING.md
├── CHANGELOG.md
└── README.md
```

Key rules for this structure:
- **Each service keeps its own dependency files** (`pyproject.toml`, `go.mod`, `package.json`). No shared virtual environments.
- **CI workflows use path filters** to only run affected service pipelines.
- **Per-service versioning** via tags like `platform/v2.3.1`, `agent/v1.8.0`.
- **Top-level Makefile** provides convenience commands (`make test-platform`, `make lint-all`).

---

## Recommendation

**Do not consolidate at this time.** The current multi-repo setup is appropriate for the following reasons:

| Factor | Multi-Repo | Monorepo |
|--------|-----------|----------|
| Polyglot stack (Python + Go + TypeScript) | ✅ Natural isolation | ❌ Complex CI orchestration |
| Shared code (SDK) | ✅ Versioned package | ⚠️ Path imports, tighter coupling |
| Solo developer convenience | ⚠️ Repo switching friction | ✅ Everything in one place |
| CI/CD simplicity | ✅ One language per pipeline | ❌ Path filters, selective builds |
| Future contributors | ✅ Focused repos | ❌ Intimidating clone |
| Independent deployability | ✅ Natural | ⚠️ Requires discipline |
| Release management | ✅ Per-service versions | ❌ Misleading unified version |
| Docker builds | ✅ Lean contexts | ⚠️ Requires careful .dockerignore |

**The sole legitimate advantage — reduced repo-switching for a solo dev — does not outweigh the added CI/CD complexity and the loss of natural service isolation that polyglot repos provide.**

### If repo-switching friction is the main pain point, consider these alternatives:

1. **VS Code multi-root workspace** (you already have this!) — open all repos in one window.
2. **Shared GitHub Actions** — extract common workflow steps into a reusable `.github` org-level repo.
3. **Local dev script** — a single `make dev` that starts all services via docker-compose across repos.

---

## Decision

**Status: Rejected** — Keep the current multi-repo architecture. Revisit if the team grows to 3+ developers working across service boundaries simultaneously, at which point a monorepo with proper tooling (Nx, Bazel, or Pants) might become justified.
