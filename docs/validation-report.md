# Strategy Validation Report

## Reference Period
**BTC-USD, 2020-01-01 → 2024-08-01** (matching the approximate timeframe from the [source video](https://docs.google.com/document/d/1r_xGmufV5gqnbsNQvOCn7Yfv1ZXnwryCCf9ndw-4wrc/edit?usp=sharing)).

## Results vs Video Claims

| Strategy | Timeframe | Video Claim | Our Result | Trades | Sharpe | Verdict |
|----------|-----------|-------------|------------|--------|--------|---------|
| **Bollinger Bands** | Daily | ~1,187% | **1,212%** | 14 | 0.88 | ✅ **Validated** |
| **Bull Market Support Band** | Weekly | ~736% | **668%** | 6 | 0.76 | ✅ **Close match** |
| **SuperTrend** | Daily | (no claim) | **952%** | 19 | 0.88 | ✅ **Profitable** |

### Notes

- **Bollinger Bands**: Within 2% of the video's claimed return. Logic matches exactly: buy when close > upper band, sell when close < lower band.
- **BMSB**: Within 9% of the video's claim. Minor difference likely due to exact start/end dates and yfinance vs TradingView data. Uses SMA(20) + EMA(21) on weekly candles as designed.
- **SuperTrend**: No return was claimed in the video. Our implementation produces strong results with proper direction logic (bullish checks lower band for support break, bearish checks upper band for resistance break).

## Bugs Found & Fixed

### SuperTrend Direction Bug (Critical)
- **Before fix**: -88% return, 1,366 trades, -0.65 Sharpe
- **Root cause**: Direction check compared close against the **wrong** band — bullish checked upper (always true), bearish checked lower (always true), causing direction to flip every 1.1 bars
- **Fix**: Bullish only flips bearish when close breaks **below lower band** (support lost); bearish only flips bullish when close breaks **above upper band** (resistance broken)
- **PR**: #77

### BMSB Weekly Approximation Bug
- **Before fix**: 289% return on daily with `× 5` length hack
- **Root cause**: `weekly_sma`/`weekly_ema` multiplied SMA/EMA length by 5 to fake weekly on daily data. A 100-day SMA ≠ 20-week SMA (different values, wrong crossover signals)
- **Fix**: Use plain `sma(20)`/`ema(21)` — run on `--interval 1wk` as the indicator was designed
- **PR**: #74

## Full Backtest (2018 → present)

| Strategy | Return | B&H | Trades | Max DD | Sharpe |
|----------|--------|-----|--------|--------|--------|
| Bollinger Bands | 1,818% | 824% | 29 | -53% | 0.66 |
| SuperTrend | 1,906% | 407% | 40 | -43% | 0.70 |
| BMSB (weekly) | 2,040% | 711% | 10 | -60% | 0.68 |

All three original strategies from input.md are validated and profitable.
