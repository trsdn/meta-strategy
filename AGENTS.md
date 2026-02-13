# Meta Strategy — Agent Instructions

These instructions apply to all Copilot agents working in this repository.

## Project Overview

**Meta Strategy** converts TradingView indicators into backtestable Pine Script v6 strategy scripts. The project provides:

1. **A Python CLI tool** (`src/`) that takes indicator source code + entry/exit rules and produces a complete strategy script using the prompt template
2. **A library of converted strategies** (`strategies/`) — ready-to-use `.pine` files for TradingView
3. **Strategy definitions** (`strategies/definitions/`) — YAML configs defining entry/exit logic per indicator

The three initial strategies are Bull Market Support Band, Bollinger Bands (trend-following breakout), and SuperTrend.

## Project Priorities

1. **Correctness over speed**: Strategy logic must match the defined entry/exit rules exactly — inverted logic is a critical bug
2. **No repainting**: All strategies use `close` price, never `lookahead_on`, execute on next bar open
3. **Small, testable diffs**: One strategy or feature per PR
4. **Config-driven**: Strategy definitions in YAML, not hardcoded

## Repo Structure

- `input.md` — research input / video content summaries for backtesting strategies
- `prompt.md` — Pine Script v6 conversion prompt template
- `strategies/` — generated `.pine` strategy files (output artifacts)
- `strategies/definitions/` — YAML strategy definitions (entry/exit rules, indicator source)
- `strategies/indicators/` — raw indicator source code (Pine Script)
- `src/` — Python CLI tool for strategy generation
- `tests/` — test suite (Python + Pine Script validation)
- `docs/` — documentation, sprint logs, ADRs
- `scripts/` — utility scripts

## Key Commands

```bash
# Run tests
uv run pytest tests/ -v

# Lint and format
uv run ruff check src/ && uv run ruff format src/

# Type check
uv run mypy src/

# Generate a strategy from definition
uv run python -m meta_strategy generate strategies/definitions/bollinger-bands.yml

# Validate Pine Script syntax
uv run python -m meta_strategy validate strategies/ai-bollinger-bands.pine
```

## Coding Conventions

### Python (src/, tests/)
- Python 3.11+ with type hints
- Pydantic for config/strategy definition models
- Typer for CLI
- pytest for testing
- Keep code readable; avoid clever one-liners

### Pine Script (strategies/)
- Pine Script v6 syntax
- All strategies use `strategy()` not `indicator()`
- Never use `lookahead_on`
- Never use line breaks in function calls, IFs, loops, or variable definitions
- Always fill gaps when using `request.security()`
- Always prefix strategy names with "AI - "
- Use `close` price for decisions (no repainting)

## Architectural Decisions

See `docs/architecture/ADR.md` for immutable architectural decisions.

## Safety

- Don't delete or overwrite generated `.pine` files in `strategies/` unless explicitly asked
- Don't edit `.env` or `.db` files directly
- Don't modify ADRs without explicit confirmation
- Never use `lookahead_on` in any Pine Script — it produces false backtest results

## Available Agents

| Agent | Invoke With | Use For |
|-------|------------|---------|
| Code Developer | `@code-developer` | Write/improve code, refactoring |
| Test Engineer | `@test-engineer` | Write tests, coverage analysis |
| Documentation | `@documentation-agent` | Technical docs, README |
| Security Reviewer | `@security-reviewer` | Security audit, credential scan |
| Research Agent | `@research-agent` | Research topics, propose solutions |
| Architect | `@architect` | ADR compliance, system design review |
| Release Agent | `@release-agent` | Versioning, changelogs, release readiness |
| Challenger | `@challenger` | Adversarial review of decisions and sprints |
| CI Fixer | `@ci-fixer` | Diagnose and fix CI/CD failures |
| Copilot Customization Builder | `@copilot-customization-builder` | Create agents, skills, instructions |

## Available Skills

| Skill | Use For |
|-------|---------|
| `sprint-planning` | Triage backlog, score ICE, select sprint scope |
| `sprint-start` | Begin sprint execution with quality gates |
| `sprint-review` | Demo deliverables, metrics, acceptance |
| `sprint-retro` | Process improvements, velocity tracking |
| `refine` | Turn `type:idea` issues into concrete backlog items with acceptance criteria |
| `orchestrate-feature` | Full feature pipeline |
| `orchestrate-bugfix` | Full bugfix pipeline |
| `code-review` | Structured code review |
| `create-pr` | Create PR with conventional title |
| `tdd-workflow` | Test-driven development cycle |
| `architecture-review` | Evaluate change for ADR compliance |
| `release-check` | Assess release readiness |
| `direction-gate` | Structured review before strategic pivots |
| `issue-triage` | Triage issues needing attention |
| `new-custom-agent` | Template for creating a new agent |
| `new-prompt-file` | Template for creating a new skill |
| `new-instructions-file` | Template for creating instructions file |
| `subagent-dispatch` | Execute plans with independent subagents |
| `web-research` | Structured web research with citations |
| `writing-plans` | Implementation plans with bite-sized tasks |
