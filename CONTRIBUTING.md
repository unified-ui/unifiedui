# Contributing to unified-ui

Thank you for your interest in contributing to **unified-ui**! This document outlines our development workflow, branching strategy, and best practices.

## Table of Contents

- [Development Workflow](#development-workflow)
- [Branching Strategy](#branching-strategy)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Quality Standards](#code-quality-standards)
- [Release Process](#release-process)
- [Branch Protection Rules](#branch-protection-rules)

## Development Workflow

### Getting Started

1. Fork the repository (for external contributors) or create a feature branch (for team members)
2. Set up your development environment
3. Make your changes following our coding standards
4. Test your changes thoroughly
5. Submit a pull request

### Environment Setup

Refer to the main [README.md](./README.md) for detailed setup instructions for each service:
- **Frontend Service**: React + TypeScript
- **Platform Service**: Python (FastAPI)
- **Agent Service**: Go

## Branching Strategy

We follow a **Git Flow** inspired branching model with the following branch types:

### Main Branches

- **`main`**: Production-ready code. Protected branch.
  - Always stable and deployable
  - Direct commits are not allowed
  - Only accepts merges from `release/*` or `hotfix/*` branches

- **`develop`**: Integration branch for features. Protected branch.
  - Latest development changes
  - Features are merged here first
  - Source for release branches

### Supporting Branches

#### Feature Branches
- **Naming**: `feature/<issue-number>-<short-description>`
- **Example**: `feature/123-add-chat-widget-designer`
- **Source**: `develop`
- **Merge target**: `develop`
- **Lifecycle**: Deleted after merge
- **Purpose**: New features or enhancements

```bash
# Create a feature branch
git checkout develop
git pull origin develop
git checkout -b feature/123-add-chat-widget-designer

# When complete, create a PR to develop
```

#### Bugfix Branches
- **Naming**: `bugfix/<issue-number>-<short-description>`
- **Example**: `bugfix/456-fix-cors-headers`
- **Source**: `develop`
- **Merge target**: `develop`
- **Lifecycle**: Deleted after merge
- **Purpose**: Bug fixes for upcoming releases

#### Release Branches
- **Naming**: `release/<version>`
- **Example**: `release/0.1.0`
- **Source**: `develop`
- **Merge target**: `main` and `develop`
- **Lifecycle**: Deleted after merge
- **Purpose**: Prepare for production release

```bash
# Create a release branch
git checkout develop
git pull origin develop
git checkout -b release/0.1.0

# Make release preparations (version bumps, changelog updates)
# Then merge to main and develop
```

#### Hotfix Branches
- **Naming**: `hotfix/<version>`
- **Example**: `hotfix/0.1.1`
- **Source**: `main`
- **Merge target**: `main` and `develop`
- **Lifecycle**: Deleted after merge
- **Purpose**: Critical fixes for production

```bash
# Create a hotfix branch
git checkout main
git pull origin main
git checkout -b hotfix/0.1.1

# Fix the critical issue
# Then merge to main and develop
```

#### Copilot Branches
- **Naming**: `copilot/<task-description>`
- **Example**: `copilot/setup-github-organisation`
- **Source**: `main` or `develop`
- **Merge target**: `develop` or directly to target branch
- **Lifecycle**: Deleted after merge
- **Purpose**: AI-assisted development tasks via GitHub Copilot

### Branch Visualization

```
main          ─────●─────────────●─────────●──────>
                    │             │         │
                    │        ┌────┘    ┌────┘
release/*           │        │         │
                    │        ●─────●   ●─────●
                    │         └────┐    └────┐
develop       ──────●─────●─────●──●────●────●───>
                     │     │     │       │
                     │     │     │       │
feature/*            ●─────●     │       │
                               │       │
bugfix/*                       ●─────●
```

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Build system or dependency changes
- **ci**: CI/CD configuration changes
- **chore**: Other changes (e.g., updating .gitignore)

### Scopes (Examples)

- `frontend`: Frontend service changes
- `platform`: Platform service changes
- `agent`: Agent service changes
- `auth`: Authentication/authorization
- `api`: API changes
- `ui`: User interface
- `docs`: Documentation

### Examples

```bash
feat(frontend): add chat widget designer page

Implement new page for designing form-based chat widgets with
drag-and-drop field builder and real-time preview.

Closes #123
```

```bash
fix(agent): resolve CORS header issue in platform service

Add X-Service-Key to allowed CORS headers to enable proper
communication between agent service and platform service.

Fixes #456
```

## Pull Request Process

### Before Creating a PR

1. **Update your branch** with the latest changes from the target branch
2. **Run linters** and ensure code quality
3. **Run tests** and ensure all pass
4. **Update documentation** if needed
5. **Review your own changes** before requesting review

### PR Requirements

- [ ] Descriptive title following commit convention
- [ ] Detailed description of changes
- [ ] Links to related issues
- [ ] Screenshots for UI changes
- [ ] Tests added or updated
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] All CI checks passing

### PR Review Process

1. Create PR using the provided template
2. Request review from team members
3. Address review comments
4. Obtain required approvals (minimum 1 for feature branches)
5. Copilot review integration will automatically review code
6. Merge using "Squash and merge" for feature branches

### Merging Strategies

- **Feature/Bugfix → develop**: Squash and merge
- **Release → main**: Create merge commit
- **Release → develop**: Create merge commit
- **Hotfix → main/develop**: Create merge commit

## Code Quality Standards

### Linting

Each service has its own linting configuration:

- **Frontend**: ESLint + Prettier (TypeScript/React)
- **Platform Service**: Ruff (Python)
- **Agent Service**: golangci-lint (Go)

Run linters before committing:

```bash
# Frontend
npm run lint

# Platform Service
ruff check .

# Agent Service
golangci-lint run
```

### Testing

Maintain high test coverage (target: 80%):

- **Frontend**: Vitest + React Testing Library
- **Platform Service**: pytest
- **Agent Service**: Go testing framework

```bash
# Frontend
npm run test

# Platform Service
pytest -n auto --cov

# Agent Service
go test ./...
```

### Code Reviews

All code must be reviewed by at least one team member:

- **Focus areas**: Logic, security, performance, readability
- **Automated reviews**: GitHub Copilot reviews are integrated
- **Response time**: Aim to review within 24 hours
- **Be constructive**: Provide helpful feedback and suggestions

## Release Process

We follow [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** version (1.0.0): Breaking changes
- **MINOR** version (0.1.0): New features, backward compatible
- **PATCH** version (0.0.1): Bug fixes, backward compatible

### Release Workflow

1. **Create Release Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/X.Y.Z
   ```

2. **Prepare Release**
   - Update version numbers in all services
   - Update CHANGELOG.md with release notes
   - Run full test suite
   - Fix any issues found

3. **Merge to Main**
   ```bash
   git checkout main
   git pull origin main
   git merge --no-ff release/X.Y.Z
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin main --tags
   ```

4. **Merge Back to Develop**
   ```bash
   git checkout develop
   git pull origin develop
   git merge --no-ff release/X.Y.Z
   git push origin develop
   ```

5. **Delete Release Branch**
   ```bash
   git branch -d release/X.Y.Z
   git push origin --delete release/X.Y.Z
   ```

6. **Create GitHub Release**
   - Go to GitHub Releases page
   - Create new release from tag
   - Copy changelog entries
   - Publish release

### Release Tags

- Format: `vX.Y.Z` (e.g., `v0.1.0`, `v1.0.0`)
- Pre-releases: `vX.Y.Z-beta.N`, `vX.Y.Z-rc.N`
- Tags are created on `main` branch only

## Branch Protection Rules

### `main` Branch

- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Dismiss stale approvals when new commits are pushed
- ✅ Require review from code owners (when CODEOWNERS file exists)
- ✅ Require status checks to pass:
  - Linting
  - Tests (all services)
  - Build verification
- ✅ Require branches to be up to date before merging
- ✅ Require conversation resolution before merging
- ✅ Require linear history (no merge commits except from release/hotfix)
- ✅ Restrict who can push to matching branches (admins only)
- ✅ Do not allow force pushes
- ✅ Do not allow deletions

### `develop` Branch

- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass:
  - Linting
  - Tests (all services)
- ✅ Require branches to be up to date before merging
- ✅ Require conversation resolution before merging
- ✅ Do not allow force pushes
- ✅ Do not allow deletions

## Additional Resources

- [README.md](./README.md) - Project overview and setup
- [CHANGELOG.md](./CHANGELOG.md) - Version history and changes
- [Issue Templates](.github/ISSUE_TEMPLATE/) - Templates for reporting issues
- [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md) - PR template

## Questions?

If you have questions or need help:

1. Check existing documentation
2. Search for similar issues
3. Create a new issue with the `question` label
4. Reach out to the team

Thank you for contributing to unified-ui! 🚀
