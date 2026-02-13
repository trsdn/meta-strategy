# Sprint 3 Log — 2026-02-13

**Goal**: Run all three strategies locally with real BTC data — no TradingView needed
**Planned**: 2 issues (#11-#12)
**Result**: 2/2 done ✅

| # | Issue | ICE | Status |
|---|-------|-----|--------|
| 11 | Python backtesting engine | 9 | done |
| 12 | Comparison report | 6 | done |

## Key Results

| Strategy | Return | Buy & Hold | Trades | Max DD | Sharpe |
|----------|--------|-----------|--------|--------|--------|
| Bollinger Bands | 1804% | 419% | 29 | -53% | 0.67 |
| SuperTrend | -64% | 390% | 953 | -76% | -0.39 |
| Bull Market Support Band | 211% | 880% | 16 | -66% | 0.28 |

**Best performer**: Bollinger Bands (1804% return, 4.3× buy & hold)

## Technical Notes
- Fixed `backtesting.py` `_Array` vs `pd.Series` compatibility (all indicator functions convert at entry)
- Fixed SuperTrend NaN propagation bug in band initialization
- Default cash increased to $100K to handle high-priced assets like BTC
- SuperTrend underperforms on daily data (too many signals) — may improve with longer period or weekly timeframe

## Huddles
