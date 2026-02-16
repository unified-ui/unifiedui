# .github Directory

This directory contains GitHub-specific configuration files for the unified-ui repository.

## Contents

### Issue Templates (`ISSUE_TEMPLATE/`)

Templates for creating standardized issues:

- **`bug_report.yml`** - Report bugs or unexpected behavior
- **`feature_request.yml`** - Suggest new features or enhancements
- **`task.yml`** - Create tasks, chores, or maintenance work
- **`config.yml`** - Configuration for issue templates (disables blank issues)

### Pull Request Template

- **`PULL_REQUEST_TEMPLATE.md`** - Standardized template for all pull requests

### Workflows (`workflows/`)

GitHub Actions CI/CD workflows:

- **`lint.yml`** - Runs linters for all services (ESLint, Ruff, golangci-lint, markdownlint)
- **`test.yml`** - Runs test suites for all services (Vitest, pytest, Go tests)
- **`pr-validation.yml`** - Validates PRs (title, branch name, conflicts, secrets)

### Code Owners

- **`CODEOWNERS`** - Defines code ownership for automatic reviewer assignment

### Labels Configuration

- **`labels.yml`** - Documents recommended repository labels
- **`scripts/apply-labels.sh`** - Script to apply labels to the repository

## Usage

### Creating Issues

1. Go to the [Issues](https://github.com/unified-ui/unifiedui/issues) page
2. Click "New Issue"
3. Select the appropriate template (Bug Report, Feature Request, or Task)
4. Fill out the template completely
5. Submit the issue

### Creating Pull Requests

1. Create a feature branch following our [branching strategy](../CONTRIBUTING.md#branching-strategy)
2. Make your changes and commit them
3. Push your branch to GitHub
4. Open a pull request - the template will be automatically loaded
5. Fill out the template sections
6. Request reviews from code owners (automatic via CODEOWNERS)
7. Address review comments
8. Merge when approved and all checks pass

### Applying Labels

To apply the recommended labels to the repository:

```bash
cd .github/scripts
./apply-labels.sh
```

Alternatively, apply labels manually via the GitHub web interface or CLI.

### Workflows

Workflows run automatically on:
- Pull requests to `main` and `develop` branches
- Pushes to `main` and `develop` branches

View workflow runs at: https://github.com/unified-ui/unifiedui/actions

## Configuration Files

### yamllint (`../.yamllint.yml`)

Configures YAML linting for GitHub Actions and other YAML files.

### markdownlint (`../.markdownlint.json`)

Configures Markdown linting for documentation files.

## Maintenance

### Updating Templates

When updating templates:
1. Test them with example data
2. Document any changes in CHANGELOG.md
3. Notify the team of changes

### Adding New Workflows

When adding new workflows:
1. Follow the existing structure
2. Use concurrency groups to prevent race conditions
3. Test the workflow in a feature branch first
4. Document the workflow in this README

### Modifying CODEOWNERS

When updating CODEOWNERS:
1. Ensure all paths are correct
2. Test that the right people are assigned
3. Coordinate with team members

## Best Practices

### Issue Templates
- Keep templates concise but comprehensive
- Use dropdowns for predefined choices
- Make critical fields required
- Provide helpful descriptions

### Workflows
- Use caching to speed up builds
- Run jobs in parallel when possible
- Fail fast when appropriate
- Use concurrency groups to cancel outdated runs

### Labels
- Apply labels consistently
- Use priority labels for triage
- Tag releases appropriately
- Keep label descriptions clear

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Issue Templates Documentation](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates)
- [CODEOWNERS Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

## Support

For questions about GitHub configuration:
- Review existing documentation
- Check GitHub's official documentation
- Create an issue with the `question` label
- Contact the DevOps team

---

**Maintained by**: DevOps Team  
**Last Updated**: February 2026
