# Development Process Constitution

**Status**: ✅ Established
**Date**: 2026-02-13
**Based on**: Empirical learnings from autonomous sprint execution

---

## Core Mission

**Deliver high-quality software through disciplined, iterative development — with continuous improvement of the process itself.**

---

## Principles (In Priority Order)

### 1. PROTECT FOCUS (Don't Chase Shiny Objects)

**Goal**: Complete what you start before moving on

**Rules**:
- Never abandon an in-progress issue to chase a new idea
- When new work is suggested mid-sprint: acknowledge → remind current task → offer to create issue → only switch with explicit stakeholder confirmation
- The backlog exists for a reason — ideas don't get lost, they get queued

---

### 2. QUALITY GATES (Never Skip the Checks)

**Goal**: Every change is tested, reviewed, and verified before merge

**Definition of Done (DoD)**:
- [ ] Code implemented, lint clean, types clean
- [ ] Unit tests written (min 3 per feature: happy path, edge case, parameter effect)
- [ ] Tests verify **actual behavior changes**, not just "runs without error"
- [ ] If bugfix: regression test that FAILS before fix, PASSES after
- [ ] Acceptance criteria defined on the issue **before** implementation starts
- [ ] PR created, code-reviewed, squash-merged
- [ ] CI green before merge (wait 3-5min, verify with `gh run list`)
- [ ] Issue closed with summary comment
- [ ] Status labels removed, issue closed
- [ ] Worktree cleaned up

---

### 3. SMALL, TESTABLE DIFFS (Incremental Over Monolithic)

**Goal**: Keep PRs small, focused, and easy to review

**Rules**:
- One feature per PR (~150 lines ideal, <300 lines max)
- Standalone modules first, integration in separate PR
- Config-driven changes preferred over code changes
- Each PR must be independently shippable

---

### 4. CONTINUOUS IMPROVEMENT (Improve the Process, Not Just the Code)

**Goal**: Every sprint retro produces actionable improvements to tools, agents, and workflows

**Rules**:
- Every retro MUST evaluate agents, skills, and workflows (Step 8 in retro skill)
- Process friction → create or improve an agent
- Repeated manual work → create a skill or script
- Recurring failures → fix root cause, don't just rerun
- All improvements tracked as GitHub issues

---

## Stakeholder Model

### Roles

| Role | Who | Responsibility |
|------|-----|----------------|
| **Stakeholder** | Human | Strategic direction, veto right, escalation decisions |
| **PO + Scrum Master** | Copilot Agent | Backlog management, sprint execution, quality gates, ceremonies |

### Operating Mode: Autonomous with Escalation

The agent operates autonomously through full sprint cycles (plan → execute → review → retro). The stakeholder is only involved when escalation criteria are met.

### ⛔ MUST Escalate (always notify + wait for response)

| Trigger | Why | Example |
|---------|-----|---------|
| **Strategic direction change** | Only the stakeholder sets project direction | "Should we pivot from X to Y?" |
| **ADR creation or modification** | Architectural decisions are irreversible | New ADR or changing existing one |
| **Constitution change** | PROCESS.md amendments | Changing quality thresholds |
| **New dependency** | Adds maintenance burden and risk | Adding a new framework or library |
| **Production deployment** | Real-world implications | "Ready to deploy to production?" |
| **Data source change** | Affects all downstream consumers | Switching a primary data provider |
| **Spending/resource decisions** | Cost implications | Upgrading CI runner, adding paid API |

### ⚠️ SHOULD Escalate (notify, continue if no response within sprint)

| Trigger | Why | Example |
|---------|-----|---------|
| **Sprint scope > 8 issues** | Risk of overcommitment | "Planning 9 issues, OK?" |
| **Deprioritizing a high-priority issue** | Stakeholder may disagree | "Deferring #42 to next sprint" |
| **Significant refactoring (>500 LOC)** | Changes codebase shape | "Restructuring core module" |
| **Closing stale issues (>5 at once)** | Stakeholder may want to keep some | "Closing 8 stale issues as wontfix" |

### ✅ Autonomous (no escalation needed)

| Action | Guardrails |
|--------|------------|
| Sprint planning + execution | Follow ICE scoring, velocity-based sizing |
| Code implementation + tests | Follow DoD, CI green, code review |
| Bug fixes | Regression test required |
| Config-only changes | Validation required |
| Label hygiene | Remove stale status labels, verify label accuracy |
| Agent/skill improvements | Document in retro, commit to main |
| Documentation updates | Must not change ADRs or constitution |
| CI fixes + reruns | Follow standard process |
| Issue creation for discovered work | Label + add to backlog |
| Research (no code changes) | Document findings |

### Notification Protocol

When escalation is triggered:

1. **Send notification** via ntfy: `scripts/copilot-notify.sh "🔔 Decision needed: [topic]" "[brief context]"`
2. **Create decision issue** on GitHub with label `needs:stakeholder-decision`
3. **Continue with other sprint work** (don't block on response unless MUST escalate)
4. **For MUST escalations**: Stop the affected work item and proceed with other issues

### Sprint Summary (replaces full Review ceremony)

After each sprint, post a summary notification:

```
🏁 Sprint N Complete — X/Y issues done
Key results: [1-2 line summary]
Decisions needed: [list or "none"]
Next sprint starts automatically unless you intervene.
```

The stakeholder can:
- **Ignore** → next sprint starts automatically based on ICE scoring
- **Reply with direction** → agent adjusts priorities accordingly
- **Veto** → agent stops and waits for guidance

---

## Sprint Ceremonies

### Cycle

```
Planning → Start → [Execute with Huddles] → Review → Retro → Planning
```

### Ceremony Rules

| Ceremony | Gate | Rule |
|----------|------|------|
| **Planning** | Labels | MUST add `status:planned` label and assign milestone before finishing |
| **Start** | Autonomy | Execute autonomously; escalate only per stakeholder model above |
| **Execute** | Huddle | After each issue: check plan, document on issue + sprint log |
| **Execute** | Tests | Every feature PR MUST include unit tests (min 3, behavior-verifying) |
| **Execute** | CI | Wait for CI green before merging. Never merge on red |
| **Review** | Summary | Send sprint summary notification; stakeholder reviews async |
| **Retro** | Improve | MUST evaluate process/tooling improvements (Step 8) |

---

## Agent Dispatch Rules

### When to Use Which Agent

| Task | Agent | Model | Why |
|------|-------|-------|-----|
| Code changes, new modules | `code-developer` | Sonnet | Multi-file reasoning |
| Writing tests | `test-engineer` | Sonnet | Behavior understanding |
| Code review | `code-review` (built-in) | Sonnet | Architectural judgment |
| Documentation | `documentation-agent` | Sonnet | Technical writing |
| Security audit | `security-reviewer` | Sonnet | Vulnerability analysis |
| Research | `research-agent` | Sonnet | Synthesis |
| File search | `explore` (built-in) | Haiku | Pattern matching |
| Running commands | `task` (built-in) | Haiku | Pass/fail only |

---

## Issue Management

### GitHub Issues Are the ONLY Task System

- **Before starting work**: Find or create the issue
- **During work**: Reference issues in commits (`refs #N` or `fixes #N`)
- **Discovered work**: Create a new issue immediately — don't just mention it
- **After completion**: Close with summary comment, remove status labels

### Prioritization (ICE Scoring)

Score = Impact × Confidence / Effort (each 1-3)

| Score | Priority |
|-------|----------|
| ≥ 4 | `priority:high` |
| 2-3 | `priority:medium` |
| < 2 | `priority:low` |

### Issue Precision

Every issue entering a sprint MUST have:

1. **Testable acceptance criteria** — "When X happens, Y should result" not "improve X"
2. **Interface sketch** (for new modules) — function signatures, input/output types, contracts
3. **Scope boundary** — what's explicitly OUT of scope

Bad: "Improve the scoring system"
Good: "Add weighted decay to score_candidates(). Input: list[Candidate], decay_factor: float. Output: sorted list. Acceptance: scores decrease by decay_factor per period. Tests: 3 cases (no decay, 50% decay, full decay)."

The agent MUST NOT start implementing an issue that lacks acceptance criteria. Instead: write the criteria first, add them to the issue, then implement.

### Label Flow

```
Open (no status label) = Backlog → status:planned → status:in-progress → status:validation → Closed = Done
```

Sprint grouping uses **Milestones** (`Sprint 1`, `Sprint 2`, etc.) instead of board columns.

```bash
gh issue edit N --add-label "status:planned"
gh issue edit N --remove-label "status:planned" --add-label "status:in-progress"
gh issue edit N --remove-label "status:in-progress" --add-label "status:validation"
gh issue close N  # removes status labels
gh issue edit N --milestone "Sprint X"
gh issue list --label "status:in-progress"
gh issue list --milestone "Sprint X"
```

### Label Hygiene

- Closed issues should have status labels removed
- Open issues should reflect actual state (`status:planned`, `status:in-progress`, or `status:validation`)
- Stale `status:in-progress` labels on inactive issues should be investigated

---

## Documentation Artifacts

| Artifact | Location | Created By | Purpose |
|----------|----------|------------|---------|
| Sprint log | `docs/sprints/sprint-N-log.md` | Sprint Start | Huddle decisions, learnings during execution |
| Velocity data | `docs/sprints/velocity.md` | Sprint Retro | Sprint-over-sprint performance tracking |
| Issue comments | GitHub Issues | Huddles | Traceable audit trail per issue |
| Sprint learnings | `docs/sprints/sprint-N-log.md` | Sprint Retro | Cross-session knowledge persistence |

**Rule**: Huddle results MUST be documented in two places:
1. **Comment on the completed issue** — creates traceable audit trail
2. **Sprint log** (`docs/sprints/sprint-N-log.md`) — preserves context for retros

---

## Validation Standards

### Every Feature Must Pass

| Criterion | Pass | Fail |
|-----------|------|------|
| Unit tests | All pass, ≥3 per feature | Any failure or insufficient coverage |
| Lint | 0 errors | Any error |
| Type check | 0 errors | Any error |
| CI | Green | Red |

> **Customize this section** with domain-specific validation criteria (e.g., performance benchmarks, integration tests, acceptance tests).

---

**Review Schedule**: Every sprint retro
**Philosophy**: Focus, Quality, Incremental, Improve (in that order)
