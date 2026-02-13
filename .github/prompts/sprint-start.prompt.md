---
name: Sprint Start
description: Start sprint execution with quality gates and daily huddles
---

# Sprint Start

You are the **Scrum Master**. Begin sprint execution.

**Stakeholder model**: Per `docs/constitution/PROCESS.md`, sprints start automatically.
Only escalate if MUST criteria are met. No consent gate needed.

## Step 1: Gather State

```bash
git log --oneline -10
git status
git stash list
gh issue list --label "priority:high"
gh issue list --label "status:in-progress"
```

## Step 2: Load Sprint Backlog

If sprint planning was run, use the Planned items:

```bash
gh issue list --milestone "Sprint N" --label "status:planned"
```

Otherwise, present prioritized candidates and select based on ICE scoring.

Determine the sprint number from `docs/sprints/velocity.md` (increment from last sprint).

## Step 3: Create Sprint Log

Create a sprint log file to document huddle results and decisions during execution:

```bash
mkdir -p docs/sprints
cat > docs/sprints/sprint-N-log.md << 'EOF'
# Sprint N Log — [Date]

**Goal**: [sprint goal]
**Planned**: [number] issues

## Huddles

[Huddles will be appended here after each issue completes]
EOF
```

## Step 4: Start Execution

Check `docs/constitution/PROCESS.md` MUST escalation criteria:
- If any sprint issue triggers MUST criteria → notify stakeholder, wait for that issue only
- Otherwise → **begin execution immediately** (no consent gate)

Send summary notification:
```bash
scripts/copilot-notify.sh "🚀 Sprint N Starting" "Goal: [theme]. Issues: #A, #B, #C..."
```

## Step 5: Execute (issue by issue)

For each issue in the sprint backlog:

### 5a. Start Issue

Update status label. Create worktree:

```bash
gh issue edit N --remove-label "status:planned" --add-label "status:in-progress"
```

```bash
git worktree add -b <branch-name> ../<project>-<short-id> main
cd ../<project>-<short-id>
```

### 5b. Pre-Implementation Check

Before writing code for each issue:
1. **Read the acceptance criteria** on the issue — they define "done"
2. **For new modules**: define the interface first (function signatures, types, contracts) before implementation
3. **Write test stubs** from the acceptance criteria before writing production code

This is not full spec-driven development — it's just-enough precision to prevent the agent from building the wrong thing.

### 5c. Implementation Flow

```
implement → lint/type-check → write unit tests → validate → code review → PR → merge
```

### 5d. Quality Gates

**⛔ TEST GATE**: Every feature PR MUST include unit tests.
- Use `@test-engineer` agent after implementation, before PR
- Minimum 3 tests per feature (happy path, edge case, parameter effect)
- Tests must verify **actual behavior**, not just "runs without error"

**⛔ DEFINITION OF DONE** (see `.github/copilot-instructions.md` for full checklist):
- Code + lint + types clean
- Unit tests (min 3, behavior-verifying)
- PR reviewed + squash-merged
- CI green before merge
- Issue closed with summary
- **Issue closed**: Status labels removed

### 5e. 🔄 Daily Huddle (after each issue completes)

**Do NOT skip this.**

**Document the huddle in two places:**

**1. Comment on the completed issue** (persistent record):

```bash
gh issue comment N --body "### Huddle — Sprint X, Issue X/Y done

**Outcome**: [what was delivered, key metric or result]
**Key learning**: [anything discovered during implementation]
**Decision**: [any re-prioritization or scope change]
**Next**: #M — [title]"
```

**2. Append to sprint log** (`docs/sprints/sprint-N-log.md`):

```markdown
### Huddle — After Issue #N ([timestamp])

**Completed**: #N — [outcome]
**Sprint progress**: X/Y issues done
**Key learning**: [anything that changes the plan?]

**Plan check**:
- Does anything we learned change the priority of remaining issues?
- Should we re-order?
- Any blockers?

**Next up**: #M — [title]
```

## Constraints

- **WIP**: 1 issue at a time — finish before starting next
- **Sprint focus**: Never silently abandon an in-progress issue

## ⛔ Agent Dispatch Rules

| Task | Agent | Why |
|------|-------|-----|
| Code implementation | `@code-developer` | Multi-file reasoning |
| Writing tests | `@test-engineer` | Behavior understanding |
| Code review | `@code-developer` | Architectural judgment |
| Research/docs | `@research-agent` / `@documentation-agent` | Synthesis |

**⛔ CI GATE**: After creating a PR, wait 3-5 minutes for CI to complete. Verify green with `gh run list --branch <branch> --limit 3` BEFORE merging.

## Output Format

```markdown
## Sprint — [Date]

### Sprint Backlog (ordered)
1. #N: [Title] (priority, orchestration)
2. #M: [Title] (priority, orchestration)

### Progress
- [X] #N — Done (PR #P)
- [ ] #M — Next
```

When all issues are done or time is exhausted → run sprint review and sprint retro.
