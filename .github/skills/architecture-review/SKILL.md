---
name: architecture-review
description: "Evaluate architectural decisions, propose ADRs. Triggers on: 'architecture review', 'ADR', 'design review'."
---

# Architecture Review

Evaluate a proposed change against the project's architectural decisions and design principles.

## Steps

### 1. Load ADRs

Read `docs/architecture/ADR.md` and understand all current architectural decisions.

### 2. Identify the Proposed Change

Determine the scope and nature of the change being evaluated:
- What modules/components are affected?
- What new patterns or dependencies are introduced?
- What existing patterns are modified?

### 3. Check Against Each ADR

For each ADR, evaluate whether the proposed change:
- **Complies** — follows the decision as intended
- **Violates** — directly contradicts the decision
- **Extends** — introduces a pattern not covered by existing ADRs

### 4. Flag Violations

For each violation found:
- Cite the specific ADR number and title
- Explain how the change violates it
- Assess severity (blocking vs. advisory)

### 5. Suggest Alternatives

For each violation, propose an alternative approach that:
- Achieves the same goal
- Complies with existing ADRs
- Minimizes disruption to the current architecture

### 6. Identify ADR Gaps

If the change introduces patterns not covered by existing ADRs:
- Recommend whether a new ADR should be created
- Draft the ADR in standard format if appropriate

### 7. Report Compliance Status

Produce a summary:
- ✅ **Compliant** — no violations, safe to proceed
- ⚠️ **Needs Changes** — violations found, alternatives available
- ⛔ **Blocked** — fundamental architectural conflict, requires ADR discussion
