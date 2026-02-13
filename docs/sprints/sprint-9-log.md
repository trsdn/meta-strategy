# Sprint 9 Log — 2026-02-13

**Goal**: Multi-timeframe backtesting, B&H normalization, lint cleanup
**Planned**: 5 issues
**Completed**: 5/5 (100%)

## Delivered

| # | Issue | PR | Outcome |
|---|-------|----|---------|
| #44 | Fix 69 ruff lint errors | #49 | ✅ Done — all 69 errors resolved, CI lint enforced |
| #45 | Normalize B&H baseline | #50 | ✅ Done — detect_warmup() + normalized B&H in backtest-all |
| #46 | Show warmup bars in output | #51 | ✅ Done — effective start date shown when warmup > 0 |
| #47 | Add --interval CLI param | #52 | ✅ Done — 1h/4h/1d/etc. across all commands |
| #48 | Skip BMSB on sub-daily | #53 | ✅ Done — BMSB skipped in backtest-all, warned in backtest |

## Sprint Metrics

| Metric | Value |
|--------|-------|
| Issues planned | 5 |
| Issues completed | 5 |
| Issues carried over | 0 |
| PRs merged | 5 (#49-#53) |
| Files changed | 14 |
| Lines +/- | +657/-200 |
| Tests (before → after) | 73 → 85 |
| New tests written | 12 |

## Huddles

### Huddle 1 — Issue #44
- Resolved 69 ruff lint errors (27 auto-fixed, 34 E501, 8 other)
- Configured B008 (Typer pattern) and B017 as ignored
- Removed continue-on-error from CI lint step

### Huddle 2 — Issue #45
- Initial approach (trim data) failed: backtesting.py recalculates B&H per indicator warmup
- Final approach: run full backtests, override B&H with normalized value from max warmup bar
- detect_warmup() calculates per-strategy warmup from indicator NaN analysis

### Huddle 3 — Issue #46
- Added warmup_bars and effective_start to run_backtest() result
- CLI shows "Effective start: YYYY-MM-DD (N warmup bars skipped)"

### Huddle 4 — Issue #47
- Threaded interval through 6 functions and 4 CLI commands
- Sub-daily auto-clamps start date (yfinance 730-day limit)
- VALID_INTERVALS and SUB_DAILY_INTERVALS constants

### Huddle 5 — Issue #48
- run_all_backtests() skips BMSB on sub-daily with skipped marker
- CLI shows ⏭️ note for skipped, ⚠️ warning for individual backtest

## Retrospective

### What went well
- **Zero blockers**: All 5 issues completed without interruption
- **B&H normalization design**: Initial approach failed (trim data), pivoted quickly to override approach
- **Velocity recovery**: 12.5 issues/hr vs 4.7 in Sprint 8 — no unplanned work, no CI debugging
- **Test discipline**: 12 new tests, all green throughout

### What could improve
- **detect_warmup() is coupled to strategy classes**: Uses `if strategy_cls is X` pattern. Adding new strategies requires editing detect_warmup(). Consider registry pattern.
- **ruff format undoes manual E501 fixes**: Had to re-fix a validator line that ruff reformatted back over 120 chars

### Action items
- None blocking. detect_warmup coupling is minor (6 strategies, stable).
