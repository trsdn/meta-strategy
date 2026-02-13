# Architectural Decision Records

## How to Add ADRs

When making a significant architectural decision, document it here using this format:

```markdown
## ADR-NNN: [Title]

**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-NNN
**Date**: YYYY-MM-DD

### Context

[Why this decision needs to be made. What problem are we solving?]

### Decision

[What we decided to do.]

### Consequences

**Positive:**
- [Benefit 1]
- [Benefit 2]

**Negative:**
- [Trade-off 1]
- [Trade-off 2]

**Risks:**
- [Risk 1]
```

### Rules

- ADRs are **append-only** — never delete, only supersede
- Changing an ADR requires **stakeholder approval** (MUST escalate)
- Number sequentially: ADR-001, ADR-002, etc.
- Keep decisions atomic — one decision per ADR

---

## ADR-001: Example Decision — Use GitHub Issues as Sole Task System

**Status**: Accepted
**Date**: {{DATE}}

### Context

The project needs a single source of truth for task tracking. Using multiple systems (internal todo lists, chat history, external tools) creates fragmentation and lost context.

### Decision

GitHub Issues is the ONLY task tracking system. All work items, bugs, features, and tasks must be tracked as GitHub Issues. No internal todo lists, chat-based tracking, or external tools.

### Consequences

**Positive:**
- Single source of truth for all work
- Traceable audit trail via issue comments
- Integration with PRs, commits, and CI
- Labels + milestones provide visual workflow

**Negative:**
- Requires discipline to always create issues
- Minor overhead for trivial tasks
- Dependent on GitHub availability

**Risks:**
- Team members may forget to create issues for discovered work
