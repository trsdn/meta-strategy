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
