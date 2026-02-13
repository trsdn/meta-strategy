# Changelog

## v1.0.0 — Strategy Validation & Statistical Analysis

### Added
- **HTML validation report** — interactive report with equity curves, trade lists, and B&H comparison (`docs/validation-report.html`)
- **Statistical significance tests** — Sharpe ratio t-test, paired t-test vs B&H, trade return significance, win rate binomial test (scipy)
- **Trade markers toggle** — show/hide buy (▲ green) and sell (▼ red) triangles on equity charts
- **Collapsible trade lists** — per-strategy entry/exit dates, prices, P&L, and return %
- **Strict mypy** — `disallow_untyped_defs = true` across entire codebase
- **Error path tests** — 10 tests covering invalid inputs, missing data, edge cases
- **Warmup registry pattern** — `warmup_indicators()` classmethod per strategy

### Fixed
- **SuperTrend direction bug** (critical) — direction check compared wrong band, causing 1,366 false trades → fixed to 40 trades, -88% → +1,906%
- **BMSB weekly approximation** — `weekly_sma`/`weekly_ema` (length × 5) replaced with native weekly interval, 289% → 2,039%

### Changed
- Version bump 0.3.0 → 1.0.0
- All 3 core strategies validated against source video claims
- Test count: 109 → 128
- Added scipy dependency for statistical tests

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
