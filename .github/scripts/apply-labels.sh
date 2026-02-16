#!/bin/bash
#
# Script to apply GitHub labels to the repository
# Requires: GitHub CLI (gh) to be installed and authenticated
#
# Usage: ./apply-labels.sh

set -e

echo "🏷️  Applying GitHub labels to unified-ui repository..."
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Type labels
echo "Creating type labels..."
gh label create "bug" --description "Something isn't working" --color "d73a4a" --force || true
gh label create "enhancement" --description "New feature or request" --color "a2eeef" --force || true
gh label create "task" --description "General task or chore" --color "d4c5f9" --force || true
gh label create "documentation" --description "Improvements or additions to documentation" --color "0075ca" --force || true
gh label create "refactor" --description "Code refactoring" --color "fbca04" --force || true

# Priority labels
echo "Creating priority labels..."
gh label create "priority: critical" --description "Critical priority - needs immediate attention" --color "b60205" --force || true
gh label create "priority: high" --description "High priority" --color "d93f0b" --force || true
gh label create "priority: medium" --description "Medium priority" --color "fbca04" --force || true
gh label create "priority: low" --description "Low priority" --color "0e8a16" --force || true

# Status labels
echo "Creating status labels..."
gh label create "status: needs-triage" --description "Needs initial review and prioritization" --color "ededed" --force || true
gh label create "status: blocked" --description "Blocked by another issue or external dependency" --color "b60205" --force || true
gh label create "status: in-progress" --description "Work is in progress" --color "0052cc" --force || true
gh label create "status: ready-for-review" --description "Ready for review" --color "0e8a16" --force || true
gh label create "status: needs-revision" --description "Needs changes after review" --color "e99695" --force || true

# Service labels
echo "Creating service labels..."
gh label create "service: frontend" --description "Frontend service (React/TypeScript)" --color "61dafb" --force || true
gh label create "service: platform" --description "Platform service (Python/FastAPI)" --color "3776ab" --force || true
gh label create "service: agent" --description "Agent service (Go)" --color "00add8" --force || true
gh label create "service: infra" --description "Infrastructure/DevOps/CI/CD" --color "5319e7" --force || true

# Release labels
echo "Creating release labels..."
gh label create "release: v0.1.0" --description "Planned for v0.1.0 release" --color "006b75" --force || true
gh label create "release: v0.2.0" --description "Planned for v0.2.0 release" --color "006b75" --force || true
gh label create "release: v0.3.0" --description "Planned for v0.3.0 release" --color "006b75" --force || true
gh label create "release: v1.0.0" --description "Planned for v1.0.0 release" --color "006b75" --force || true

# Special labels
echo "Creating special labels..."
gh label create "good first issue" --description "Good for newcomers" --color "7057ff" --force || true
gh label create "help wanted" --description "Extra attention is needed" --color "008672" --force || true
gh label create "question" --description "Further information is requested" --color "d876e3" --force || true
gh label create "duplicate" --description "This issue or pull request already exists" --color "cfd3d7" --force || true
gh label create "wontfix" --description "This will not be worked on" --color "ffffff" --force || true
gh label create "invalid" --description "This doesn't seem right" --color "e4e669" --force || true
gh label create "security" --description "Security-related issue" --color "ee0701" --force || true
gh label create "breaking-change" --description "Breaking API or behavior change" --color "d93f0b" --force || true
gh label create "dependencies" --description "Dependency updates" --color "0366d6" --force || true
gh label create "copilot" --description "GitHub Copilot assisted development" --color "8b949e" --force || true
gh label create "needs-discussion" --description "Needs team discussion before proceeding" --color "d4c5f9" --force || true

echo ""
echo "✅ All labels have been created successfully!"
echo ""
echo "View labels at: https://github.com/unified-ui/unifiedui/labels"
