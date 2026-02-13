# Sprint 8 Log — 2026-02-13

**Goal**: Harden backtesting robustness: fractional trading, out-of-sample validation, and overfitting detection
**Planned**: 6 issues

## Huddles

### Huddle — After Issue #29

**Completed**: #29 — FractionalBacktest enabled, all 6 strategies work on BTC-USD without margin warnings (PR #36)
**Sprint progress**: 1/6 issues done
**Key learning**: numpy read-only array flags need explicit unlock for in-place operations on backtesting.py indicators

**Plan check**: No changes needed. CI has pre-existing config issue (externally managed Python) — not related to our changes.

**Next up**: #34 — Train/test split for optimize command

### Huddle — After Issue #34

**Completed**: #34 — Train/test split for optimize added, IS/OOS metrics, --split CLI param (PR #37)
**Sprint progress**: 2/6 issues done
**Key learning**: _extract_metrics() helper reduces duplication; #35 dependency unblocked

**Plan check**: No changes. Moving to #31 (rolling window) next — unblocks #32 (expanding window).

**Next up**: #31 — Rolling window walk-forward
