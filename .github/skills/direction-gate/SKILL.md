---
name: direction-gate
description: "Evaluate strategic direction changes before execution. Triggers on: 'direction change', 'strategic decision', 'pivot'."
---

# Direction Gate

**MANDATORY before any strategic direction change.** This gate prevents costly pivots without proper analysis and stakeholder alignment.

## When This Gate Applies

- Changing project paradigm or core approach
- Modifying or adding Architectural Decision Records (ADRs)
- Abandoning a direction that has received significant investment
- Changing success metrics or project goals
- Adding heavyweight dependencies (new frameworks, services, databases)

## Step 1: Document the Proposal

Create a proposal document with:

```markdown
## Direction Change Proposal — [Date]

### What
[Describe the proposed change in 2-3 sentences]

### Why
[What problem does this solve? What evidence triggered this?]

### Evidence
- [Data point 1]
- [Data point 2]
- [Metric or observation that supports the change]

### What We're Giving Up
[What existing work, direction, or investment does this replace?]

### Reversibility
- Can this be reversed? [Yes / Partially / No]
- Cost of reversal: [Low / Medium / High]

### Alternatives Considered
1. [Alternative 1 — why rejected]
2. [Alternative 2 — why rejected]
```

## Step 2: Run Challenger Review

Invoke the `@challenger` agent to adversarially review the proposal:

- Does the evidence actually support the change?
- What assumptions are we making?
- What's the opportunity cost?
- Would we choose this direction if starting fresh?

## Step 3: Stakeholder Notification

This is a **MUST escalate** item per `docs/constitution/PROCESS.md`. Present the proposal and challenger review to the stakeholder and wait for explicit approval.

```bash
scripts/copilot-notify.sh "🚦 Direction Gate" "Strategic change proposed: [summary]. Review needed."
```

## Step 4: Record Decision

If approved, document the decision:

```bash
# If it involves an ADR change
# Update docs/architecture/ADR.md with the new decision

# Comment on the relevant issue
gh issue comment <NUMBER> --body "Direction gate passed: [summary of decision]"
```

If rejected, document why and what alternative was chosen.

## Checklist

- [ ] Proposal document created with evidence
- [ ] Challenger review completed
- [ ] Stakeholder notified and explicitly approved
- [ ] Decision recorded (ADR updated if applicable)
- [ ] Affected issues updated
