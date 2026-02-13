---
name: sprint-planning
description: "Triage backlog, score issues, select sprint scope. Triggers on: 'sprint planning', 'plan sprint', 'planning start'."
---

# Sprint Planning

You are the **Scrum Master** running sprint planning autonomously.

**Stakeholder model**: Per `docs/constitution/PROCESS.md`, sprints plan and start automatically.
Only escalate if MUST criteria are met (ADR changes, strategic direction, new dependencies, etc.).

**No code changes during planning. Only issue management, research, and documentation.**

## Step 1: Review Issue Status

```bash
gh issue list --label "status:planned"
gh issue list --label "status:in-progress"
gh issue list --label "priority:high"
gh issue list --label "priority:medium"
gh issue list --limit 30
```

## Step 2: Triage Unlabeled Issues

Score using ICE framework:

| Dimension | High (3) | Medium (2) | Low (1) |
|-----------|----------|------------|---------|
| **Impact** | Core functionality or architecture | Improves robustness or tooling | Nice-to-have |
| **Confidence** | Strong evidence or clear requirements | Some evidence | Speculative |
| **Effort** | Config-only, < 1 sprint | Minor code + testing | Multi-sprint |

Score = Impact × Confidence / Effort. ≥4 = high, 2-3 = medium, <2 = low.

```bash
gh issue edit N --add-label "priority:high"
```

### Acceptance Criteria Gate

Before adding an issue to the sprint:
1. Does the issue have testable acceptance criteria? If not → write them now and add to the issue
2. For new modules: is there an interface sketch (function signatures, input/output)? If not → add it
3. Is the scope boundary clear (what's in, what's out)? If not → clarify

**Never plan an issue that says "improve X" without defining what "improved" means measurably.**

## Step 3: Elaborate Top Issues

For high-priority issues missing detail:
- Acceptance criteria
- Approach sketch (direction, not full plan)
- Dependencies
- Risks

## Step 4: Research Open Questions

If issues need research before prioritization:
- Search documentation, check codebase, review existing implementations
- Document findings

## Step 5: Create New Issues

Capture ideas discovered during discussion:

```bash
gh issue create --title "[Type]: Description" --label "priority:X" --body "..."
```

## Step 6: Select Sprint Scope

Select top 7 candidates by ICE score. Check `docs/constitution/PROCESS.md` MUST criteria:
- If any selected issue triggers a MUST escalation → notify stakeholder and wait
- Otherwise → proceed autonomously (no need to ask "which issues?")

Consider velocity from prior sprints (check `docs/sprints/velocity.md`).

## Step 6b: Define Sprint Goal

Define a one-sentence sprint goal:

Examples:
- "Establish core authentication module with tests"
- "Improve CI pipeline reliability and speed"
- "Add input validation across all API endpoints"

Label all sprint items with `sprint:N` (incrementing from last sprint).

## Step 7: Finalize Sprint

**MANDATORY**: Add `status:planned` label and assign milestone to all agreed items.

```bash
gh issue edit N --add-label "status:planned"
gh issue edit N --milestone "Sprint X"
```

Verify by listing planned issues:

```bash
gh issue list --milestone "Sprint X" --label "status:planned"
```

## Step 8: Present Summary

```markdown
## Sprint N Planning — [Date]

### Sprint Goal
[One sentence theme]

### Sprint Backlog (agreed)
| # | Title | Priority | Est. Effort | Orchestration |
|---|-------|----------|-------------|---------------|

### Dependencies
- #Y depends on #X

### Sprint Assignments
- Issues triaged: N
- Issues elaborated: N
- New issues created: N
- Labeled `status:planned`: N
- Assigned to milestone: N

### Velocity Reference
Prior sprint: X issues in ~Yh (from docs/sprints/velocity.md)
```

After planning is complete, **proceed directly to sprint execution** (no separate start needed).
The sprint starts automatically per the stakeholder model. Send a summary notification.
