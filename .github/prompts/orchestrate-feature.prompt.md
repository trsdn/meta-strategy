---
name: Orchestrate Feature
description: Full pipeline from implementation through testing, review, PR, and issue closure
---

# Orchestrate Feature

Full implementation pipeline for a feature issue: implement → test → review → PR → close.

## Prerequisites

- A GitHub issue with acceptance criteria
- Issue assigned to current sprint

## Step 1: Start Issue

```bash
gh issue edit N --add-label "status:in-progress"
```

```bash
git worktree add -b feat/issue-N-short-description ../project-N main
cd ../project-N
```

## Step 2: Implement

Use `@code-developer` agent for implementation:
- Read the issue's acceptance criteria
- Implement the minimal change
- Follow existing code patterns

## Step 3: Test

Use `@test-engineer` agent for testing:
- Minimum 3 tests per feature (happy path, edge case, parameter effect)
- Tests must verify **actual behavior changes**
- Run full test suite to check for regressions

## Step 4: Verify

```bash
uv run ruff check src/            # Lint
uv run mypy src/                   # Type check
uv run pytest tests/ -v            # Tests
```

All must pass with 0 errors.

## Step 5: Code Review

Review the changes for:
- Security issues
- Performance concerns
- Code quality
- Test coverage

## Step 6: Create PR

```bash
git add -A && git commit -m "feat(scope): description (fixes #N)"
git push -u origin HEAD
gh pr create --draft --title "feat(scope): description" --body "closes #N"
```

## Step 7: Wait for CI

```bash
# Wait 3-5 minutes, then check
gh run list --branch $(git branch --show-current) --limit 3
```

**⛔ Never merge without CI green.**

## Step 8: Merge and Close

```bash
gh pr merge --squash --delete-branch
gh issue close N --comment "Completed in PR #M. [summary of what was delivered]"
```

Remove status labels:

```bash
gh issue edit N --remove-label "status:in-progress"
```

## Step 9: Cleanup

```bash
cd ..
git worktree remove project-N
```

## Step 10: Daily Huddle

Document the huddle on the issue and sprint log (see sprint-start prompt for format).
