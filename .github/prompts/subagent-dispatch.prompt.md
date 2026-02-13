---
name: subagent-dispatch
description: "Execute implementation plans by dispatching independent subagents per task with two-stage review"
---

# Subagent Dispatch

Execute an implementation plan by dispatching independent subagents for each task, with two-stage review for quality.

**⛔ REQUIRES a user-approved plan before starting.** Never dispatch subagents without explicit consent.

## Prerequisites

- An approved implementation plan exists (created via `writing-plans` or equivalent)
- Plan has been reviewed and approved by the stakeholder
- Each task in the plan is independent enough to be executed by a single subagent

## Step 1: Read the Plan

Load the approved plan and identify all tasks. Each task should have:
- Clear scope and deliverables
- File paths to create or modify
- Acceptance criteria
- Dependencies on other tasks (if any)

## Step 2: Dispatch Subagents

For each independent task:

1. **Create directory structure** if needed (`mkdir -p`)
2. **Pre-create empty files** if the subagent needs to create new files (custom agents lack `create` tool)
3. **Dispatch one subagent per task** with full context:
   - What to implement
   - Which files to modify
   - Acceptance criteria from the plan
   - Any constraints or conventions

**Rules:**
- One task per subagent — never bundle multiple tasks
- Include full context — subagents have no memory of previous tasks
- Specify unique names for classes/functions to avoid conflicts
- Run independent tasks in parallel when possible

## Step 3: Two-Stage Review

After each subagent completes:

### Stage 1: Spec Compliance
- Does the output match the plan's acceptance criteria?
- Are all required files created/modified?
- Does it integrate correctly with other completed tasks?

### Stage 2: Code Quality
- Run linter: check for style violations
- Run type checker: verify type annotations
- Run tests: ensure nothing is broken
- Review for readability and maintainability

## Step 4: Commit

After all tasks pass review:

```bash
git add -A
git commit -m "feat: [description from plan]

Refs #<issue-number>"
```

## Rules

- **Never dispatch without an approved plan** — this is non-negotiable
- **One task per subagent** — keeps scope clear and failures isolated
- **Verify output independently** — don't trust agent claims, check the diff
- **Pre-create files for custom agents** — they can only edit existing files
- **Full context in every prompt** — subagents are stateless
