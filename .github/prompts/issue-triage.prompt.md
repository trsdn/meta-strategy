---
name: issue-triage
description: "Triage open GitHub issues — identify items needing milestones, labels, or investigation"
---

# Issue Triage

Query and triage open GitHub issues that need attention. Identify items needing milestones, labels, priority scoring, or investigation.

## Step 1: Query Open Issues

```bash
# All open issues
gh issue list --state open --limit 50

# Issues without labels
gh issue list --state open --limit 50 | grep -v "priority:"

# Issues without milestones
gh issue list --state open --limit 50 --json number,title,milestone \
  --jq '.[] | select(.milestone == null) | "#\(.number) \(.title)"'

# Stale issues (no activity in 30+ days)
gh issue list --state open --limit 50 --json number,title,updatedAt \
  --jq '.[] | select(.updatedAt < (now - 2592000 | todate)) | "#\(.number) \(.title)"'
```

## Step 2: Categorize Issues

For each issue needing attention:

| Category | Action |
|----------|--------|
| **Missing priority label** | Score with ICE, add label |
| **Missing milestone** | Assign to current or next sprint |
| **Stale (30+ days)** | Close if irrelevant, re-prioritize if still valid |
| **Needs investigation** | Add `needs-investigation` label, comment what's unclear |
| **Duplicate** | Close as duplicate, link to original |
| **Not actionable** | Request clarification or close |

## Step 3: ICE Scoring

For unlabeled issues, apply ICE scoring:

| Dimension | High (3) | Medium (2) | Low (1) |
|-----------|----------|------------|---------|
| **Impact** | Core functionality or architecture | Improves robustness or tooling | Nice-to-have |
| **Confidence** | Strong evidence or clear requirements | Some evidence | Speculative |
| **Effort** | Config-only, < 1 sprint | Minor code + testing | Multi-sprint |

Score = Impact × Confidence / Effort
- ≥ 4 → `priority:high`
- 2-3 → `priority:medium`
- < 2 → `priority:low`

```bash
gh issue edit <NUMBER> --add-label "priority:high"
```

## Step 4: Label Assignment

Assign labels based on priority and readiness:

| Condition | Action |
|-----------|--------|
| High priority, clear requirements | Add `status:planned`, assign to milestone |
| Medium priority, needs more detail | Priority label only (stays in backlog) |
| Low priority or speculative | Priority label only (stays in backlog) |
| Needs investigation first | Add `needs-investigation` label |

```bash
gh issue edit N --add-label "priority:high" --add-label "status:planned"
gh issue edit N --milestone "Sprint X"
```

## Step 5: Report

```markdown
## Triage Report — [Date]

### Triaged
| # | Title | Action | Priority |
|---|-------|--------|----------|
| N | Title | Labeled / Closed / Moved | high/medium/low |

### Needs Attention
- #N: [Why it needs human input]

### Stats
- Issues triaged: N
- Labels added: N
- Issues closed: N
- Stale issues identified: N
```
