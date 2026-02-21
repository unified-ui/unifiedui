# Contributing to unified-ui

Thank you for your interest in contributing to unified-ui! This document provides guidelines and information for contributors.

## Code of Conduct

Be respectful and constructive. We welcome contributions from everyone regardless of experience level.

## Getting Started

### Repository Structure

unified-ui consists of three main services:

| Repository | Description | Tech Stack |
|------------|-------------|------------|
| [unified-ui-platform-service](https://github.com/enricogoerlitz/unified-ui-platform-service) | Auth, RBAC, Core Database | Python 3.13, FastAPI, PostgreSQL |
| [unified-ui-agent-service](https://github.com/enricogoerlitz/unified-ui-agent-service) | AI Backend Abstraction | Go 1.24, Gin, MongoDB |
| [unified-ui-frontend-service](https://github.com/enricogoerlitz/unified-ui-frontend-service) | React Frontend | TypeScript 5.9, React 19, Vite 7 |

### Prerequisites

- **Platform Service**: Python 3.13+, uv, PostgreSQL, Redis
- **Agent Service**: Go 1.24+, MongoDB, Redis
- **Frontend Service**: Node.js 22+, npm

## Development Workflow

### 1. Fork and Clone

```bash
# Fork the relevant repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/unified-ui-{service}.git
cd unified-ui-{service}
```

### 2. Create a Branch

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming convention:
- `feat/` — New features
- `fix/` — Bug fixes
- `docs/` — Documentation only
- `refactor/` — Code refactoring
- `test/` — Test additions/changes
- `chore/` — Maintenance tasks

### 3. Make Changes

- Follow the coding style of each service (see TOOLING.md in each repo)
- Write tests for new functionality
- Update documentation if needed
- Keep commits focused and atomic

### 4. Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**Examples**:
```
feat(handlers): add message reactions endpoint
fix(auth): handle expired refresh tokens
docs(readme): update installation instructions
chore(deps): update fastapi to 0.125.0
```

### 5. Run Tests

Before submitting, run tests locally:

**Platform Service**:
```bash
pytest tests/ -n auto --no-header -q
ruff check . && ruff format --check .
```

**Agent Service**:
```bash
make test
make lint
```

**Frontend Service**:
```bash
npx vitest run
npm run lint
```

### 6. Submit Pull Request

- Push your branch to your fork
- Open a PR against the `main` branch (or `develop` if applicable)
- Fill out the PR template
- Wait for CI checks to pass
- Respond to review feedback

## Code Quality Standards

### General Rules

1. **No comments in code** — Code should be self-documenting. Only docstrings are allowed.
2. **Type annotations everywhere** — Explicit types for all function parameters and returns.
3. **Tests required** — Minimum 80% coverage for new code.
4. **Follow existing patterns** — Look at existing code for guidance.

### Service-Specific Guidelines

Each service has detailed guidelines in its respective:
- `TOOLING.md` — Development tooling and commands
- `.github/copilot-instructions/` — Copilot-specific coding guidelines

## Reporting Issues

### Bug Reports

Use the **Bug Report** template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, browser, service version)

### Feature Requests

Use the **Feature Request** template and include:
- Problem/motivation
- Proposed solution
- Impact assessment

## Questions?

- Open a **Question** issue
- Check existing issues and documentation first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to unified-ui! 🚀
