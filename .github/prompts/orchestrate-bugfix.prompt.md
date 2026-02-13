---
name: Orchestrate Bugfix
description: Full pipeline from reproduction test through fix, verification, and review
---

# Orchestrate Bugfix

Full bugfix pipeline: repro test → fix → verify → review → PR → close.

## Prerequisites

- A GitHub issue describing the bug
- Reproduction steps (or enough info to create them)

## Step 1: Start Issue

```bash
gh issue edit N --add-label "status:in-progress"
```

```bash
git worktree add -b fix/issue-N-short-description ../project-N main
cd ../project-N
```

## Step 2: Write Reproduction Test

**This test MUST FAIL before the fix is applied.**

```python
def test_bug_N_regression():
    """Regression test for #N — [bug description]"""
    # Reproduce the exact conditions from the bug report
    result = buggy_function(trigger_input)
    assert result == expected_correct_behavior
```

```bash
uv run pytest tests/path/test_file.py::test_bug_N_regression -v
# Expected: FAIL
```

## Step 3: Fix the Bug

Use `@code-developer` agent:
- Make the minimal change to fix the bug
- Don't refactor unrelated code

## Step 4: Verify Fix

```bash
# Regression test now passes
uv run pytest tests/path/test_file.py::test_bug_N_regression -v
# Expected: PASS

# All other tests still pass
uv run pytest tests/ -v

# Lint and types clean
uv run ruff check src/
uv run mypy src/
```

## Step 5: Red-Green Verification

Confirm the test actually catches the bug:

```bash
# Revert fix temporarily
git stash

# Test should FAIL (proves it catches the bug)
uv run pytest tests/path/test_file.py::test_bug_N_regression -v
# Expected: FAIL

# Restore fix
git stash pop
```

## Step 6: Create PR

```bash
git add -A && git commit -m "fix(scope): description (fixes #N)"
git push -u origin HEAD
gh pr create --draft --title "fix(scope): description" --body "fixes #N

## What was broken
[Description]

## Root cause
[What caused it]

## Fix
[What was changed]

## Verification
- Regression test added: test_bug_N_regression
- Red-green cycle verified"
```

## Step 7: Wait for CI

```bash
gh run list --branch $(git branch --show-current) --limit 3
```

**⛔ Never merge without CI green.**

## Step 8: Merge and Close

```bash
gh pr merge --squash --delete-branch
gh issue close N --comment "Fixed in PR #M. Regression test added."
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
