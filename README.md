# unified-ui

> **unified-ui for your AI** — One interface for all your AI agents, regardless of origin.

## Overview

**unifiedui** is a unified integration platform that transforms the complexity of managing multiple AI systems into a single, cohesive experience. Organizations today deploy agents across diverse platforms—Microsoft Foundry, n8n, LangGraph, Copilot, and custom solutions—resulting in fragmented user experiences, inconsistent monitoring, and operational silos. unifiedui eliminates these challenges by providing a unified interface where every agent converges into one platform.

### Key Features

- 🎯 **Unified Chat Interface** — Single, consistent chat experience for all AI agents
- 🔌 **Multi-Platform Integration** — Microsoft Foundry, n8n, LangGraph, Copilot, and custom agents
- 🎨 **Flexible Widget System** — Custom UI components embedded into conversations
- 📊 **Centralized Tracing** — Unified observability across all agents
- 🔐 **Enterprise Authentication** — Microsoft Entra ID, Google OAuth, and more
- 🌍 **Cloud-Agnostic** — Deploy on Azure, AWS, GCP, or on-premises
- 🚀 **Autonomous Agent Support** — Background agents with centralized tracing

## The Problem unifiedui Solves

### Fragmented AI Experiences
- **Inconsistent interfaces**: Each platform has its own chat experience
- **Missing UI layers**: Custom agents (e.g., LangGraph) often lack user interfaces
- **Scattered monitoring**: Tracing data lives in disparate systems

### Integration Complexity
- Custom API integrations for each agent system
- Bespoke authentication and authorization flows
- Redundant implementations of common features

### Rapid Technology Obsolescence
- Agent frameworks evolve quickly; today's tools may be tomorrow's legacy
- **unifiedui decouples agent frameworks from user experience**
- Integrate legacy and modern systems simultaneously
- Seamless transitions without disrupting end users

---

## Documentation

### Project Documentation
- [Contributing Guide](CONTRIBUTING.md) - Development workflow, branching strategy, and contribution guidelines
- [Changelog](CHANGELOG.md) - Version history and release notes
- [Copilot Integration](COPILOT_INTEGRATION.md) - GitHub Copilot usage and code review integration

### Design Documentation
- [Frontend Requirements](design/frontend/REQUIREMENTS.md) - Frontend refactoring requirements
- [Implementation Concept](design/frontend/IMPLEMENTATION_CONCEPT_V2.md) - UI refactoring implementation plan
- [RBAC UI Concept](design/frontend/RBAC_UI_CONCEPT.md) - Role-based access control UI design
- [Tracing Visualization](design/tracings/TRACING_VISUALIZATION_SPEC.md) - Tracing UI specifications

### GitHub Templates
- [Issue Templates](.github/ISSUE_TEMPLATE/) - Bug reports, feature requests, and task templates
- [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md) - PR submission guidelines

## Getting Started

### Prerequisites

- **Frontend Service**: Node.js 20+, npm
- **Platform Service**: Python 3.11+
- **Agent Service**: Go 1.21+

### Development Workflow

1. **Fork or Clone** the repository
2. **Create a branch** following our [branching strategy](CONTRIBUTING.md#branching-strategy)
3. **Make your changes** following our [coding standards](CONTRIBUTING.md#code-quality-standards)
4. **Run tests** to ensure everything works
5. **Submit a PR** using our [PR template](.github/PULL_REQUEST_TEMPLATE.md)

For detailed instructions, see [CONTRIBUTING.md](CONTRIBUTING.md).

### Quick Commands

```sh
# Frontend development
npm run dev

# Platform service
uvicorn unifiedui.app:app --reload
make run

# Agent service
go run main.go
```

## Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) to learn about:

- Development workflow
- Branching strategy (Git Flow)
- Commit message conventions
- Pull request process
- Code quality standards
- Testing requirements

## Release Management

We follow [Semantic Versioning](https://semver.org/) (SemVer) for releases:

- **v0.1.0** - Initial release with core features
- **v0.2.0** - LangChain/LangGraph integration and chat widgets
- **v0.3.0** - Cloud deployment and advanced authentication

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## CI/CD

Our CI/CD pipeline includes:

- ✅ Automated linting (ESLint, Ruff, golangci-lint)
- ✅ Comprehensive testing (Vitest, pytest, Go tests)
- ✅ PR validation and semantic checks
- ✅ GitHub Copilot code reviews
- ✅ Coverage reporting

Workflows are defined in [.github/workflows/](.github/workflows/).

## Community

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/unified-ui/unifiedui/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/unified-ui/unifiedui/discussions)
- **Pull Requests**: Contribute code via [Pull Requests](https://github.com/unified-ui/unifiedui/pulls)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
