---
name: Sprint Review
description: Review sprint deliverables, metrics, and autonomous acceptance
---

# Sprint Review

You are the **Scrum Master** presenting sprint results.

**This is a demo and acceptance ceremony. Do NOT start new work.**

**Stakeholder model**: Per `docs/constitution/PROCESS.md`, the user is a Stakeholder, not PO.
Sprint review runs autonomously unless MUST escalation criteria are met.
Replace the full review ceremony with a sprint summary notification.

## Step 1: Gather Evidence

```bash
# Commits this sprint
git log --oneline --since="8 hours ago"

# Uncommitted changes
git status
git diff --stat

# Merged PRs
gh pr list --state merged --limit 15

# Closed issues
gh issue list --state closed --limit 20

# Still in progress
gh issue list --state open --label "status:in-progress"
```

**If uncommitted changes exist**: STOP and decide whether to commit first.

## Step 2: Delivery Report

```markdown
## Sprint Review — [Date]

### Delivered
| # | Issue | PR | Outcome |
|---|-------|----|---------|
| N | Title | #M | ✅ Done / ⚠️ Partial / ❌ Blocked |

### Sprint Metrics
| Metric | Value |
|--------|-------|
| Issues planned | |
| Issues completed | |
| Issues carried over | |
| PRs merged | |
| Files changed | |
| Lines +/- | |
| Tests (before → after) | |
| New tests written | |
| Bugs found during sprint | |
```

## Step 3: Stakeholder Acceptance

Check `docs/constitution/PROCESS.md` escalation criteria:

**MUST escalate** (ask stakeholder explicitly):
- Strategic direction changes
- ADR changes or new ADRs
- Constitution changes
- New heavyweight dependencies
- Production deployment decisions
- Data source changes
- Spending decisions

**Otherwise**: Accept deliverables autonomously. Present summary in chat and send notification.
Do NOT ask "do you accept?" for standard sprints — the stakeholder model says this is autonomous.

If MUST criteria ARE met:
- Ask: **"These deliverables include [criteria]. Do you accept?"**
- Wait for explicit approval before proceeding.

## Step 4: Issue Cleanup

For each issue touched:
- **DONE** → Close with summary, remove status labels
- **Partial** → Comment progress, set `status:planned`
- **Blocked** → Label, document why

Create issues for any discovered work:

```bash
gh issue create --title "[Type]: Description" --label "priority:X" --body "..."
```

## Step 5: Carry-over

```markdown
### Carry-over Items
- #N: [What's left, why not completed]
```

Move incomplete items back to Planned with notes.

## Step 6: Notify

```bash
scripts/copilot-notify.sh "📋 Sprint Review" "Done: X/Y issues. Key: [finding]"
```

After review, run sprint retro for process improvement.
