---
name: create-pr
description: "Create GitHub pull requests. Triggers on: 'create PR', 'pull request', 'submit PR'."
---

# Create Pull Request

Creates GitHub PRs with titles following Conventional Commits format.

## PR Title Format

```
<type>(<scope>): <summary>
```

### Types (required)

| Type | Description | Changelog |
|------|-------------|-----------|
| `feat` | New feature | Yes |
| `fix` | Bug fix | Yes |
| `perf` | Performance improvement | Yes |
| `test` | Adding/correcting tests | No |
| `docs` | Documentation only | No |
| `refactor` | Code change (no bug fix or feature) | No |
| `build` | Build system or dependencies | No |
| `ci` | CI configuration | No |
| `chore` | Routine tasks, maintenance | No |

### Scopes (optional but recommended)

Define scopes based on your project structure. Examples:
- `core` — Core/backend changes
- `api` — API endpoint changes
- `ui` — Frontend/UI changes
- `cli` — CLI changes
- `config` — Configuration changes

### Summary Rules

- Use imperative present tense: "Add" not "Added"
- Capitalize first letter
- No period at the end

## Steps

1. **Check current state**:
   ```bash
   git status
   git diff --stat
   git log origin/main..HEAD --oneline
   ```

2. **Analyze changes** to determine type, scope, and summary.

3. **Push branch if needed**:
   ```bash
   git push -u origin HEAD
   ```

4. **Create PR**:
   ```bash
   gh pr create --draft --title "<type>(<scope>): <summary>" --body "## Summary

   [Describe what the PR does]

   ## Related Issues

   closes #N

   ## Checklist

   - [ ] Tests included
   - [ ] Lint passes
   - [ ] Documentation updated (if needed)"
   ```

## Validation

The PR title must match this pattern:
```
^(feat|fix|perf|test|docs|refactor|build|ci|chore|revert)(\([a-zA-Z0-9 ]+\))?!?: [A-Z].+[^.]$
```

## Examples

```
feat(core): Add user authentication module
fix(api): Resolve memory leak in request handler
docs: Update installation instructions
refactor(cli): Simplify command parsing logic
feat(api)!: Remove deprecated v1 endpoints
```
