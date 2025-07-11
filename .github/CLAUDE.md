# CLAUDE.md - GitHub Configuration

This file provides guidance to Claude Code when working with GitHub-related configurations and workflows.

## Directory Overview

The `.github/` directory contains GitHub-specific configurations:
- Issue templates
- Workflow definitions (CI/CD)
- Project documentation
- Community health files

## Structure

```
.github/
├── ISSUE_TEMPLATE/      # Issue and PR templates
│   ├── epic.md
│   ├── feature.md
│   ├── bug.md
│   ├── enhancement.md
│   ├── task.md
│   └── config.yml
├── ISSUES/              # Detailed issue specifications
│   ├── EPIC-*.md       # Epic descriptions
│   ├── FEATURE-*.md    # Feature specifications
│   └── PROJECT_ROADMAP.md
├── workflows/           # GitHub Actions workflows
└── CLAUDE.md           # This file
```

## Working with Issues

### Creating New Epics

1. Use the epic template format
2. Number sequentially (EPIC-006, EPIC-007, etc.)
3. Include all required sections
4. Link related features

### Creating New Features

1. Link to parent epic
2. Define clear acceptance criteria
3. Break down into subtasks
4. Estimate complexity

### Issue Labels

Apply appropriate labels:
- Priority: `P0-critical`, `P1-high`, `P2-medium`, `P3-low`
- Component: `graphiti`, `unstract`, `unified-api`, `infrastructure`
- Status: `planning`, `ready`, `in-progress`, `blocked`, `completed`
- Type: `epic`, `feature`, `bug`, `enhancement`, `task`

## GitHub Actions Workflows

### Workflow Structure

```yaml
name: Workflow Name
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Step name
        run: command
```

### Common Workflows to Implement

1. **PR Validation** (`pr-validation.yml`)
   - Run tests
   - Check code style
   - Verify documentation

2. **Docker Build** (`docker-build.yml`)
   - Build images
   - Scan for vulnerabilities
   - Push to registry

3. **Release** (`release.yml`)
   - Tag versions
   - Generate changelog
   - Create GitHub release

4. **Deploy** (`deploy-staging.yml`, `deploy-prod.yml`)
   - Deploy to environments
   - Run smoke tests
   - Notify team

### Secrets Management

Required secrets:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `OPENAI_API_KEY`
- `SLACK_WEBHOOK`
- `KUBECONFIG`

## Best Practices

### For Issues

1. **Be Specific**: Clear titles and descriptions
2. **Use Templates**: Don't skip template sections
3. **Link Relations**: Connect related issues
4. **Update Status**: Keep labels current
5. **Close Properly**: Link PRs that close issues

### For Workflows

1. **Cache Dependencies**: Speed up builds
2. **Use Matrix Builds**: Test multiple versions
3. **Fail Fast**: Stop on first failure
4. **Secure Secrets**: Never hardcode sensitive data
5. **Document Steps**: Add comments for complex logic

### For Documentation

1. **Keep Updated**: Update docs with code changes
2. **Use Diagrams**: Visualize complex concepts
3. **Add Examples**: Show don't just tell
4. **Version Docs**: Tag documentation versions
5. **Review Regularly**: Audit for accuracy

## Automation Ideas

### Issue Automation

```yaml
# Auto-label based on files changed
- path: "unified-api/**"
  labels: ["unified-api"]
- path: "graphiti/**"
  labels: ["graphiti"]
```

### PR Automation

```yaml
# Auto-assign reviewers
reviewers:
  - teamA
code_owners:
  - path: "unified-api/"
    owners: ["@api-team"]
```

### Release Automation

```yaml
# Semantic versioning
- feat: minor version bump
- fix: patch version bump
- BREAKING CHANGE: major version bump
```

## Issue Tracking Commands

Useful commands for issue management:

```bash
# List all epics
gh issue list --label "epic"

# List high priority issues
gh issue list --label "P1-high"

# Create new issue
gh issue create --template feature.md

# View issue
gh issue view 123

# Update labels
gh issue edit 123 --add-label "in-progress"
```

## Monitoring Project Health

Check these metrics:
1. Open issues by priority
2. PR merge time
3. Issue resolution time
4. Test coverage trends
5. Build success rate

## Tips for Claude Code

When working with GitHub configurations:
1. Validate YAML syntax before committing
2. Test workflows in feature branches
3. Use workflow dispatch for manual testing
4. Check permissions for GitHub tokens
5. Monitor action usage limits

Remember: Good GitHub configuration enables smooth collaboration and automated workflows!