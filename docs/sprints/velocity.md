# Sprint Velocity

Track sprint-over-sprint performance to calibrate future sprint sizing.

| Sprint | Date | Goal | Planned | Done | Carry | ~Hours | Issues/Hr | Notes |
|--------|------|------|---------|------|-------|--------|-----------|-------|
| 1 | 2026-02-13 | Foundation: schema, engine, indicators, definitions | 6 | 6 | 0 | ~0.5 | 12.0 | First sprint — setup + foundation |
| 2 | 2026-02-13 | CLI, validator, README, strategy generation | 4 | 4 | 0 | ~0.3 | 13.3 | All backlog cleared |
| 3 | 2026-02-13 | Local backtesting engine + comparison report | 2 | 2 | 0 | ~0.5 | 4.0 | Fixed _Array compat, NaN propagation |
| 4 | 2026-02-13 | Multi-asset, optimization, walk-forward | 3 | 3 | 0 | ~0.3 | 10.0 | Grid search, walk-forward analysis |
| 5 | 2026-02-13 | HTML reports, dashboard, CSV/JSON export | 3 | 3 | 0 | ~0.3 | 10.0 | SVG equity curves, dark theme |
| 6 | 2026-02-13 | RSI, MACD, confluence strategies | 3 | 3 | 0 | ~0.3 | 10.0 | 6 total strategies now |
| 7 | 2026-02-13 | CI, Monte Carlo, risk metrics, docs | 4 | 4 | 0 | ~0.3 | 13.3 | Full robustness suite |
| 8 | 2026-02-13 | Backtesting robustness: fractional, OOS, overfitting | 6 | 6+1 | 0 | ~1.5 | 4.7 | +1 unplanned (CI runner). Session restart mid-sprint. |
| 9 | 2026-02-13 | Multi-timeframe, B&H normalization, lint cleanup | 5 | 5 | 0 | ~0.4 | 12.5 | Clean sprint, no blockers |

## How to Read This

- **Planned**: Issues committed to the sprint during planning
- **Done**: Issues completed and moved to Done
- **Carry**: Issues carried over to next sprint (Planned - Done)
- **~Hours**: Approximate time spent (session duration)
- **Issues/Hr**: Done / Hours — velocity metric

## Velocity Trends

- **Average velocity**: ~9.9 issues/hr across 9 sprints
- **Best sprint type**: Foundation/setup sprints (12-13 issues/hr)
- **Slowest sprint**: Sprint 8 (4.7 issues/hr) — session restart, CI runner setup, real debugging (numpy bug)
- **Sprint 9 recovery**: 12.5 issues/hr — clean execution, no blockers
- **Recommended sprint size**: 4-6 issues (complex features), 6-8 (routine)
