---
name: writing-plans
description: "Write implementation plans before coding. Triggers on: 'write plan', 'implementation plan', 'plan this'."
---

# Writing Plans

Create an implementation plan before touching code. Plans assume the executing engineer has zero codebase context.

## When to Use

- Before implementing a feature with multiple files or steps
- Before a refactoring that touches several modules
- When an issue needs more than a single commit to complete
- Before dispatching subagents

## Step 1: Understand the Requirement

- Read the issue and acceptance criteria
- Explore relevant code paths
- Identify affected files and modules
- Note any dependencies or constraints

## Step 2: Write the Plan

Save to `docs/plans/YYYY-MM-DD-<feature-name>.md`:

```markdown
# Plan: [Feature Name]

**Issue**: #N
**Date**: YYYY-MM-DD
**Author**: Copilot

## Goal
[One sentence: what does this accomplish?]

## Affected Files
- `path/to/file1.py` — [what changes]
- `path/to/file2.py` — [what changes]
- `tests/test_file1.py` — [new test file]

## Tasks

### Task 1: [Description]
**Files**: `path/to/file.py`
**Acceptance**: [What "done" looks like]

Steps:
1. Write failing test for [behavior]
2. Run test — expect RED
3. Implement [minimal code]
4. Run test — expect GREEN
5. Commit: "test: add [test name]" / "feat: implement [feature]"

### Task 2: [Description]
...

## Dependencies
- Task 2 depends on Task 1 (uses types defined there)
- Tasks 3 and 4 are independent (can run in parallel)

## Risks
- [Risk 1 — mitigation]
```

## Plan Quality Rules

### Bite-Sized Tasks
Each task should take **2-5 minutes** to execute:
- Write a failing test → run it → implement → run tests → commit
- If a task description is longer than 5 lines, split it

### TDD by Default
Every task that changes behavior follows Red-Green-Refactor:
1. Write failing test
2. Run test (expect failure)
3. Write minimal implementation
4. Run test (expect pass)
5. Refactor if needed
6. Commit

### Self-Contained Context
Each task must include:
- Exact file paths
- What to change (not just "update the module")
- Acceptance criteria
- Commit message

## Principles

- **DRY** — Don't repeat yourself. Reuse existing utilities.
- **YAGNI** — Don't build features not in the current issue.
- **TDD** — Tests before implementation, always.
- **Frequent Commits** — One commit per task minimum.
- **Zero Context Assumption** — Write as if the reader has never seen the codebase.

## Step 3: Review the Plan

Before executing:
- [ ] Every task has clear acceptance criteria
- [ ] Tasks are ordered by dependency
- [ ] Independent tasks are marked for parallel execution
- [ ] Each task is ≤5 minutes of work
- [ ] All affected files are listed
- [ ] Risks are documented
