# Changelog

All notable changes to the **unified-ui** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v0.1.0
- Unified chat interface for all AI agents
- Multi-platform integration (Microsoft Foundry, n8n, LangGraph)
- Flexible widget system with custom UI components
- Centralized tracing across all agents
- Enterprise authentication (Microsoft Entra ID, Google OAuth)
- Basic RBAC (Role-Based Access Control)

### Planned for v0.2.0
- LangChain + LangGraph integration via REST API
- Python unified-ui SDK for streaming and tracing
- Real-time updates for reasoning and tool calls
- Chat widgets (Single-Select, Multi-Select)
- Connection testing for external platforms
- Dynamic dropdowns for external data sources

### Planned for v0.3.0
- Azure Cloud deployment configurations
- LDAP and Kerberos authentication providers
- Microsoft Copilot integration
- Feedback framework integration
- Form widgets support
- Simple ReACT Agent with MCP Server support
- OpenAPI definition as tool for ReACT Agent
- Agent Playground for development

## Release Notes Guidelines

When creating a new release, follow this structure:

### [X.Y.Z] - YYYY-MM-DD

#### Added
- New features and capabilities

#### Changed
- Changes to existing functionality

#### Deprecated
- Features that will be removed in future releases

#### Removed
- Features that have been removed

#### Fixed
- Bug fixes and corrections

#### Security
- Security fixes and improvements

---

## Example Release Entry

```markdown
## [0.1.0] - 2026-03-01

### Added
- Unified chat interface supporting multiple AI platforms
- Integration with Microsoft Foundry for AI agents
- Integration with n8n workflows as autonomous agents
- Centralized tracing and observability system
- Enterprise authentication via Microsoft Entra ID
- Role-based access control (RBAC) for tenants and applications
- Chat widget system for custom UI components
- File upload support in conversations
- Responsive UI with dark mode support

### Changed
- Refactored frontend structure for better maintainability
- Updated API endpoints for consistency
- Improved error handling across all services

### Fixed
- CORS header issues between agent and platform services
- Application favorites API endpoint method
- Message streaming stability improvements

### Security
- Implemented service-to-service authentication with X-Service-Key
- Added input validation for all API endpoints
- Enhanced token refresh mechanism

[0.1.0]: https://github.com/unified-ui/unifiedui/releases/tag/v0.1.0
```

---

## Version History

<!-- Releases will be added here in reverse chronological order -->

## [Unreleased]
- Initial repository setup
- Documentation for GitHub organization and project management
- CI/CD workflows configuration
- Branch protection rules documentation

---

## How to Update This Changelog

### For Development

When working on a feature or fix:
1. Add your change under `[Unreleased]` in the appropriate section
2. Use present tense ("Add feature" not "Added feature")
3. Be concise but descriptive
4. Link to relevant issues/PRs when applicable

### For Releases

When creating a release:
1. Create a new section with version and date: `## [X.Y.Z] - YYYY-MM-DD`
2. Move relevant items from `[Unreleased]` to the new release section
3. Change verbs to past tense ("Added feature" not "Add feature")
4. Add comparison link at the bottom of the file
5. Update the `[Unreleased]` link to compare with the new version

### Links

For GitHub-hosted projects, add comparison links at the bottom:

```markdown
[Unreleased]: https://github.com/unified-ui/unifiedui/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/unified-ui/unifiedui/releases/tag/v0.1.0
```

---

**Note**: This changelog is maintained manually. All team members are responsible for updating it when making significant changes.
