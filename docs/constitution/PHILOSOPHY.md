# The AI-Scrum Manifesto

*Inspired by the [Agile Manifesto](https://agilemanifesto.org) (2001) — adapted for human-AI collaboration.*

---

The Agile Manifesto was written for teams of humans. We work differently: a human and an AI agent, building software together. The dynamics are fundamentally new — the agent never sleeps, never forgets a checklist, and can run a full sprint in hours. But it also can't set strategic direction, doesn't feel user pain, and will confidently ship nonsense if not grounded in process.

This manifesto captures what we've learned about making that collaboration work.

---

## We have come to value

### Autonomous execution over constant approval
The agent should run sprints end-to-end without asking permission for every line of code. Clear escalation criteria replace endless approval loops. The human sets direction; the agent executes.

*...while maintaining clear escalation for decisions that matter.*

### Verified evidence over claimed completion
"Tests pass" means showing the output, not saying the words. The agent must run the command, read the result, and only then claim success. Trust is built through evidence, not confidence.

*...because an AI that says "should work" is worse than one that says "it failed."*

### Sprint discipline over feature chasing
Complete what you start. New ideas go to the backlog, not into the current sprint. Context-switching wastes the agent's strongest asset: sustained, focused execution without distraction.

*...because the backlog exists so good ideas don't get lost and current work doesn't get abandoned.*

### Continuous process improvement over static workflows
Every retrospective must evaluate the process itself — not just the deliverables. Agents, prompts, and workflows are living artifacts. What caused friction gets automated. What failed gets fixed. The process improves every sprint.

*...because a team that only ships features but never improves how it works will plateau.*

---

## Principles Behind the Manifesto

*Derived from real sprints, real failures, and real corrections.*

1. **The best architecture emerges from small, tested diffs** — not grand rewrites. One feature per PR. Standalone modules first, integration second.

2. **Quality gates are non-negotiable.** Every feature gets tests. Every PR gets CI. Every claim gets verification. Skipping gates doesn't save time — it creates rework.

3. **The human brings judgment; the agent brings throughput.** Don't make the agent decide strategy. Don't make the human write boilerplate. Play to each side's strengths.

4. **Documentation is not overhead — it's memory.** The agent has no memory between sessions. Sprint logs, issue comments, and velocity data are how continuity survives session boundaries.

5. **Escalation is a feature, not a failure.** Knowing when to stop and ask is a sign of a well-configured process, not a broken one. MUST-escalate criteria protect the project from autonomous overreach.

6. **Process improvements compound.** Sprint 1 is rough. Sprint 5 is smoother. Sprint 10 has custom agents, automated gates, and a velocity history. Each retro makes the next sprint better.

7. **Evidence before assertions, always.** The agent must never say "done" without proof. The human must never accept "done" without checking. Trust, but verify — on both sides.

8. **The backlog is sacred.** Ideas don't get lost — they get queued. Issues are the only task system. If it's not an issue, it doesn't exist.

9. **Velocity is descriptive, not prescriptive.** Track it to understand capacity. Don't use it to pressure. A sprint that delivers 5 solid issues beats one that "delivers" 10 untested ones.

10. **The agent is not a junior developer — it's a different kind of collaborator.** It doesn't need motivation, but it does need constraints. It doesn't forget instructions, but it does hallucinate. Design the process for what it actually is, not what you wish it were.

11. **Welcome scope changes — route them through the backlog, not mid-sprint pivots.** Changing direction is fine; abandoning work-in-progress silently is not. New ideas get an issue, a score, and a place in the next planning session. The backlog is how good ideas survive without derailing current work.

12. **Simplicity — maximize the work not done.** Prefer config changes over code changes. Prefer existing tools over new ones. The best feature is the one you didn't need to build. Every line of code is a liability; every automation that replaces manual work is an asset.

---

## For Your Project

Below this manifesto, add your project-specific philosophy:

### Core Mission

Convert TradingView indicators into backtestable strategies and validate them locally with real market data.

### Project Principles (In Priority Order)

1. **Strategy Accuracy** — Backtest results must reflect real market behavior. No repainting, no lookahead bias, no inverted entry/exit logic.
2. **Quality** — 58 tests, CI pipeline, lint + type checks. Every strategy change is verified before merge.
3. **Velocity** — Autonomous sprint execution. The agent runs full sprint cycles; the stakeholder steers direction.
4. **Simplicity** — YAML-driven strategy definitions, config over code. The best strategy is the one that doesn't need custom code.

### Decision Framework

When evaluating any change, ask:
1. **Does it break existing stability?** → If yes, reconsider
2. **Is it tested and reviewed?** → If no, add tests first
3. **Does it follow our ADRs?** → If no, propose ADR change or find alternative
4. **Is it the simplest approach?** → If no, simplify

### What We DON'T Optimize

- Not pursuing live trading — we generate and validate strategies, not execute them
- Not optimizing for maximum strategy count — quality over quantity
- Not chasing real-time data feeds — local CSV backtesting is sufficient

---

**Review Schedule**: Every 5th sprint retro
**Inspired by**: [The Agile Manifesto](https://agilemanifesto.org) — Kent Beck, Mike Beedle, Arie van Bennekum, Alistair Cockburn, Ward Cunningham, Martin Fowler, et al., 2001
