# Changelog

## v0.3.0 — Backtesting Robustness & Multi-Timeframe

### Added
- **Train/test split** for parameter optimization (`--split 0.7` = 70% train, 30% OOS)
- **Rolling and expanding walk-forward** modes (`--mode rolling/expanding`)
- **Overfitting detection** — warns when in-sample Sharpe > 2× out-of-sample
- **Parameter stability report** — flags parameter drift across walk-forward folds
- **B&H normalization** — `backtest-all` shows identical Buy & Hold baseline across strategies
- **Warmup detection** — `detect_warmup()` identifies indicator warmup bars automatically
- **Multi-timeframe support** — `--interval 1h/4h/1d` across all backtest commands
- **BMSB sub-daily skip** — `backtest-all` skips BMSB on sub-daily intervals with note
- **Integration tests** — 24 parameterized tests validating YAML → generate → validate pipeline
- **Strategy artifacts** — YAML definitions + Pine Script files for all 6 strategies
- **README limitations section** — disclaimers about local vs TradingView differences

### Changed
- `FractionalBacktest` numpy workaround for read-only indicator arrays
- Lint: 69 pre-existing ruff errors resolved, CI lint enforced (no continue-on-error)
- README: aligned with actual features, removed unverified return numbers
- Install command: `uv sync --extra dev` (not `--dev`)
- Self-hosted CI runner configured for meta-strategy repo
- Test count: 58 → 109

### Fixed
- Fractional trading crash on numpy read-only arrays (#29)
- B&H return differed across strategies due to indicator warmup (#45)
- 69 ruff lint errors (E501, B905, B904, SIM102, etc.) (#44)

## v0.2.0 — Template Sync

### Added
- `/refine` ceremony — turns `type:idea` issues into concrete backlog items
- `type:idea` label for lightweight stakeholder input
- Drift control — sprint scope lock, huddle drift checks, boundary review
- Spec-driven best practices — acceptance criteria gates, pre-implementation checks
- PHILOSOPHY.md — AI-Scrum Manifesto adapted for meta-strategy
- Notification script (scripts/copilot-notify.sh)

### Changed
- Sprint cycle: refine → plan → start → execute → review → retro
- Updated AGENTS.md, copilot-instructions.md, PROCESS.md from template v0.2.0
- Makefile updated with full shortcut targets

## v0.1.0 — Initial Release

### Added
- Sprints 1-7: Schema, engine, CLI, validator, backtesting, optimization, reporting, risk analysis
- 6 trading strategies (BB, SuperTrend, BMSB, RSI, MACD, Confluence)
- 14 CLI commands
- 58 tests
