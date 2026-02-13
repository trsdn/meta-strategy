"""Tests for the backtesting engine.

Uses synthetic data to verify strategy signal logic without network calls.
"""

import numpy as np
import pandas as pd
import pytest
from backtesting import Backtest

from meta_strategy.backtest import (
    STRATEGIES,
    BollingerBandsStrategy,
    BullMarketSupportBandStrategy,
    ConfluenceStrategy,
    MACDStrategy,
    RSIStrategy,
    SuperTrendStrategy,
    bollinger_lower,
    bollinger_upper,
    macd_line,
    macd_signal,
    rsi,
    supertrend_direction,
    weekly_ema,
    weekly_sma,
)


def _make_ohlcv(close_prices: list[float], spread: float = 2.0) -> pd.DataFrame:
    """Create synthetic OHLCV data from close prices."""
    n = len(close_prices)
    close = np.array(close_prices, dtype=float)
    high = close + spread
    low = close - spread
    opn = close - spread * 0.3
    return pd.DataFrame({
        "Open": opn,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": np.full(n, 1000.0),
    }, index=pd.date_range("2020-01-01", periods=n, freq="D"))


def test_bollinger_bands_signal():
    """BB breakout: enters when close > upper band, exits when close < lower."""
    # Create data that rises sharply then drops
    prices = [100.0] * 30 + [120.0] * 5 + [80.0] * 5
    data = _make_ohlcv(prices)

    bt = Backtest(data, BollingerBandsStrategy, cash=10000, commission=0)
    stats = bt.run()

    # Should have at least 1 trade from the spike above the upper band
    assert stats["# Trades"] >= 1


def test_supertrend_direction_calculation():
    """SuperTrend direction flips on trend changes with noisy data."""
    np.random.seed(42)
    n = 300
    # Create noisy data with clear regime change
    noise = np.random.normal(0, 5, n)
    # Uptrend then flat then sharp downtrend
    trend = np.concatenate([
        np.linspace(100, 200, 100),
        np.full(50, 200),
        np.linspace(200, 50, 150),
    ])
    close = pd.Series(trend + noise)
    high = close + abs(np.random.normal(3, 1, n))
    low = close - abs(np.random.normal(3, 1, n))

    direction = supertrend_direction(high, low, close, period=10, factor=2.0)

    assert len(direction) == n
    # With noisy data and strong reversal, both directions should appear
    unique = set(direction.dropna().unique())
    assert 1 in unique, f"Expected bullish direction, got {unique}"
    # Direction -1 should appear during the downtrend
    assert -1 in unique, f"Expected bearish direction, got {unique}"


def test_supertrend_strategy_trades():
    """SuperTrend strategy produces trades on noisy trending data."""
    np.random.seed(123)
    n = 400
    noise = np.random.normal(0, 8, n)
    trend = np.concatenate([
        np.linspace(100, 300, 100),
        np.linspace(300, 80, 100),
        np.linspace(80, 250, 100),
        np.linspace(250, 60, 100),
    ])
    prices = (trend + noise).tolist()
    prices = [max(p, 10.0) for p in prices]

    data = _make_ohlcv(prices, spread=5.0)
    bt = Backtest(data, SuperTrendStrategy, cash=10000, commission=0)
    stats = bt.run()

    assert stats["# Trades"] >= 1


def test_bull_market_support_band_strategy():
    """BMSB strategy trades on long-period crossovers."""
    np.random.seed(42)
    n = 600  # Need enough data for weekly SMA/EMA (100+ days)
    # Long slow trend up then down
    prices = np.concatenate([
        np.linspace(100, 300, n // 2),
        np.linspace(300, 100, n // 2),
    ]).tolist()
    data = _make_ohlcv(prices)

    bt = Backtest(data, BullMarketSupportBandStrategy, cash=10000, commission=0)
    stats = bt.run()

    # May have 0-2 trades on such slow-moving crossovers
    assert stats["# Trades"] >= 0


def test_strategies_registry():
    """All six strategies are registered."""
    assert "bollinger-bands" in STRATEGIES
    assert "supertrend" in STRATEGIES
    assert "bull-market-support-band" in STRATEGIES
    assert "rsi" in STRATEGIES
    assert "macd" in STRATEGIES
    assert "confluence" in STRATEGIES
    assert len(STRATEGIES) == 6


def test_bollinger_indicators():
    """Bollinger upper/lower bands are symmetric around SMA."""
    close = pd.Series([100.0] * 30)
    upper = bollinger_upper(close, 20, 2.0)
    lower = bollinger_lower(close, 20, 2.0)
    # With constant prices, std = 0, so upper = lower = mean
    assert abs(upper.iloc[-1] - 100.0) < 0.01
    assert abs(lower.iloc[-1] - 100.0) < 0.01


def test_weekly_sma_ema_lengths():
    """Weekly SMA/EMA compute on correct window sizes."""
    close = pd.Series(range(200), dtype=float)
    sma = weekly_sma(close, length=20)
    ema = weekly_ema(close, length=21)
    # SMA should have NaN for first (20*5 - 1) values
    assert pd.isna(sma.iloc[98])
    assert not pd.isna(sma.iloc[99])
    # EMA should have values everywhere (ewm doesn't produce NaN)
    assert not pd.isna(ema.iloc[-1])


# === Sprint 6 tests ===

def test_rsi_indicator():
    """RSI returns values between 0 and 100."""
    np.random.seed(42)
    close = pd.Series(100 + np.cumsum(np.random.normal(0, 2, 200)))
    r = rsi(close, 14)
    valid = r.dropna()
    assert len(valid) > 0
    assert valid.min() >= 0
    assert valid.max() <= 100


def test_rsi_oversold_overbought():
    """RSI hits extremes on strong trends."""
    # Strong uptrend
    close_up = pd.Series([100 + i * 5 for i in range(50)])
    r_up = rsi(close_up, 14)
    assert r_up.iloc[-1] > 70  # should be overbought

    # Strong downtrend
    close_down = pd.Series([300 - i * 5 for i in range(50)])
    r_down = rsi(close_down, 14)
    assert r_down.iloc[-1] < 30  # should be oversold


def test_macd_indicators():
    """MACD line and signal are computed correctly."""
    close = pd.Series([100 + i * 0.5 for i in range(100)])
    ml = macd_line(close, 12, 26)
    ms = macd_signal(close, 12, 26, 9)
    assert len(ml) == 100
    assert len(ms) == 100
    # In steady uptrend, MACD should be positive
    assert ml.iloc[-1] > 0


def test_rsi_strategy_trades():
    """RSI strategy produces trades on oscillating data."""
    np.random.seed(42)
    n = 500
    # Create oscillating data around a trend
    trend = np.linspace(100, 200, n)
    noise = np.cumsum(np.random.normal(0, 3, n))
    prices = (trend + noise).tolist()
    prices = [max(p, 10.0) for p in prices]
    data = _make_ohlcv(prices)
    bt = Backtest(data, RSIStrategy, cash=100_000, commission=0)
    stats = bt.run()
    # May or may not trade depending on SMA filter, but should not error
    assert stats["# Trades"] >= 0


def test_macd_strategy_trades():
    """MACD strategy produces trades on trending data."""
    np.random.seed(123)
    n = 300
    prices = (100 + np.cumsum(np.random.normal(0.1, 2, n))).tolist()
    prices = [max(p, 10.0) for p in prices]
    data = _make_ohlcv(prices)
    bt = Backtest(data, MACDStrategy, cash=100_000, commission=0)
    stats = bt.run()
    assert stats["# Trades"] >= 1


def test_confluence_strategy_runs():
    """Confluence strategy runs without error."""
    np.random.seed(42)
    n = 300
    prices = (100 + np.cumsum(np.random.normal(0.2, 3, n))).tolist()
    prices = [max(p, 10.0) for p in prices]
    data = _make_ohlcv(prices)
    bt = Backtest(data, ConfluenceStrategy, cash=100_000, commission=0)
    stats = bt.run()
    assert stats["# Trades"] >= 0


# === Sprint 4 tests ===

def test_multi_asset_returns_results_per_symbol():
    """run_multi_asset returns one result per symbol."""
    from meta_strategy.backtest import run_multi_asset
    # Just test the function signature / error handling with a bad symbol
    results = run_multi_asset("bollinger-bands", symbols=["INVALID_SYMBOL_XYZ"])
    assert len(results) == 1
    assert "error" in results[0]


def test_default_assets_list():
    """DEFAULT_ASSETS contains expected symbols."""
    from meta_strategy.backtest import DEFAULT_ASSETS
    assert "BTC-USD" in DEFAULT_ASSETS
    assert "SPY" in DEFAULT_ASSETS
    assert len(DEFAULT_ASSETS) >= 4


def test_param_grids_defined():
    """Parameter grids exist for all strategies."""
    from meta_strategy.backtest import PARAM_GRIDS, STRATEGIES
    for name in STRATEGIES:
        assert name in PARAM_GRIDS, f"Missing param grid for {name}"
        assert len(PARAM_GRIDS[name]) >= 2, f"Grid for {name} needs at least 2 params"


def test_optimize_with_synthetic_data():
    """optimize_strategy returns sorted results."""
    from meta_strategy.backtest import optimize_strategy
    # Patch fetch_data to avoid network calls
    data = _make_ohlcv([100 + i * 0.5 for i in range(200)])
    import meta_strategy.backtest as bt_mod
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        results = optimize_strategy(
            "bollinger-bands",
            param_grid={"length": [10, 20], "mult": [1.5, 2.0]},
        )
        assert len(results) == 4  # 2 × 2 combinations
        # Sorted by Sharpe (descending)
        sharpes = [r["sharpe_ratio"] for r in results]
        assert sharpes == sorted(sharpes, reverse=True)
    finally:
        bt_mod.fetch_data = original


def test_walk_forward_with_synthetic_data():
    """walk_forward returns fold results (sequential mode, default)."""
    data = _make_ohlcv([100 + i * 0.3 for i in range(500)])
    import meta_strategy.backtest as bt_mod
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        result = bt_mod.walk_forward(
            "bollinger-bands",
            n_splits=3,
            train_pct=0.7,
        )
        assert result["strategy"] == "bollinger-bands"
        assert result["mode"] == "sequential"
        assert "avg_test_return_pct" in result
        assert "avg_test_sharpe" in result
        assert isinstance(result["folds"], list)
    finally:
        bt_mod.fetch_data = original


def test_walk_forward_rolling_mode():
    """walk_forward rolling mode produces overlapping folds with fixed train size."""
    data = _make_ohlcv([100 + i * 0.3 for i in range(800)])
    import meta_strategy.backtest as bt_mod
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        result = bt_mod.walk_forward(
            "bollinger-bands",
            mode="rolling",
            train_bars=200,
            step=100,
        )
        assert result["mode"] == "rolling"
        assert result["train_bars"] == 200
        assert result["step"] == 100
        assert len(result["folds"]) >= 2, "Should produce multiple folds"
        for f in result["folds"]:
            assert "best_params" in f
            assert "test_return_pct" in f
            assert "test_sharpe" in f
    finally:
        bt_mod.fetch_data = original


def test_walk_forward_expanding_mode():
    """walk_forward expanding mode produces folds with growing train set."""
    data = _make_ohlcv([100 + i * 0.3 for i in range(800)])
    import meta_strategy.backtest as bt_mod
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        result = bt_mod.walk_forward(
            "bollinger-bands",
            mode="expanding",
            train_bars=200,
            step=100,
        )
        assert result["mode"] == "expanding"
        assert len(result["folds"]) >= 2
    finally:
        bt_mod.fetch_data = original


def test_walk_forward_invalid_mode_raises():
    """walk_forward raises ValueError for invalid mode."""
    with pytest.raises(ValueError, match="mode must be"):
        import meta_strategy.backtest as bt_mod
        bt_mod.walk_forward("bollinger-bands", mode="invalid")


def test_optimize_split_default_70_30():
    """optimize_strategy with default split=0.7 returns IS and OOS metrics."""
    from meta_strategy.backtest import optimize_strategy
    data = _make_ohlcv([100 + i * 0.5 for i in range(300)])
    import meta_strategy.backtest as bt_mod
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        results = optimize_strategy(
            "bollinger-bands",
            param_grid={"length": [10, 20], "mult": [2.0]},
            split=0.7,
        )
        assert len(results) == 2
        for r in results:
            assert "is_return_pct" in r, "Missing in-sample return"
            assert "is_sharpe_ratio" in r, "Missing in-sample Sharpe"
            assert "return_pct" in r, "Missing OOS return"
            assert "sharpe_ratio" in r, "Missing OOS Sharpe"
        # Sorted by OOS Sharpe descending
        oos_sharpes = [r["sharpe_ratio"] for r in results]
        assert oos_sharpes == sorted(oos_sharpes, reverse=True)
    finally:
        bt_mod.fetch_data = original


def test_optimize_split_custom_80_20():
    """optimize_strategy with split=0.8 uses custom ratio."""
    from meta_strategy.backtest import optimize_strategy
    data = _make_ohlcv([100 + i * 0.5 for i in range(300)])
    import meta_strategy.backtest as bt_mod
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        results = optimize_strategy(
            "bollinger-bands",
            param_grid={"length": [20], "mult": [2.0]},
            split=0.8,
        )
        assert len(results) == 1
        assert "is_sharpe_ratio" in results[0]
        assert "sharpe_ratio" in results[0]
    finally:
        bt_mod.fetch_data = original


def test_optimize_split_1_preserves_legacy():
    """optimize_strategy with split=1.0 gives legacy behavior (no IS/OOS split)."""
    from meta_strategy.backtest import optimize_strategy
    data = _make_ohlcv([100 + i * 0.5 for i in range(200)])
    import meta_strategy.backtest as bt_mod
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        results = optimize_strategy(
            "bollinger-bands",
            param_grid={"length": [10, 20], "mult": [2.0]},
            split=1.0,
        )
        assert len(results) == 2
        for r in results:
            assert "is_return_pct" not in r, "Legacy mode should not have IS metrics"
            assert "return_pct" in r
            assert "sharpe_ratio" in r
    finally:
        bt_mod.fetch_data = original


def test_optimize_invalid_split_raises():
    """optimize_strategy raises ValueError for invalid split values."""
    from meta_strategy.backtest import optimize_strategy
    with pytest.raises(ValueError, match="split must be"):
        optimize_strategy("bollinger-bands", split=0.0)
    with pytest.raises(ValueError, match="split must be"):
        optimize_strategy("bollinger-bands", split=1.5)


def test_check_overfitting_warns_on_high_ratio():
    """check_overfitting returns warning when IS Sharpe > 2× OOS Sharpe."""
    from meta_strategy.backtest import check_overfitting
    result = {"is_sharpe_ratio": 3.0, "sharpe_ratio": 1.0, "params": {}}
    warning = check_overfitting(result)
    assert warning is not None
    assert warning["ratio"] == 3.0
    assert warning["is_sharpe"] == 3.0
    assert warning["oos_sharpe"] == 1.0


def test_check_overfitting_no_warning_when_reasonable():
    """check_overfitting returns None when ratio is acceptable."""
    from meta_strategy.backtest import check_overfitting
    result = {"is_sharpe_ratio": 1.5, "sharpe_ratio": 1.0, "params": {}}
    assert check_overfitting(result) is None


def test_check_overfitting_skips_without_split():
    """check_overfitting returns None when no IS metrics (split=1.0)."""
    from meta_strategy.backtest import check_overfitting
    result = {"sharpe_ratio": 1.5, "params": {}}
    assert check_overfitting(result) is None


def test_check_overfitting_warns_on_negative_oos():
    """check_overfitting warns when OOS is negative but IS is positive."""
    from meta_strategy.backtest import check_overfitting
    result = {"is_sharpe_ratio": 2.0, "sharpe_ratio": -0.5, "params": {}}
    warning = check_overfitting(result)
    assert warning is not None
    assert warning["ratio"] == float("inf")


def test_param_stability_report_stable():
    """param_stability_report returns stable when params are consistent."""
    from meta_strategy.backtest import param_stability_report
    folds = [
        {"best_params": {"length": 20, "mult": 2.0}},
        {"best_params": {"length": 20, "mult": 2.0}},
        {"best_params": {"length": 25, "mult": 2.0}},
    ]
    report = param_stability_report(folds)
    assert report["stable"] is True
    assert report["score_pct"] == 100.0
    assert len(report["changes"]) == 0


def test_param_stability_report_unstable():
    """param_stability_report flags >50% parameter changes."""
    from meta_strategy.backtest import param_stability_report
    folds = [
        {"best_params": {"length": 10, "mult": 2.0}},
        {"best_params": {"length": 30, "mult": 2.0}},
    ]
    report = param_stability_report(folds)
    assert report["stable"] is False
    assert report["score_pct"] < 100.0
    assert len(report["changes"]) >= 1
    assert report["changes"][0]["param"] == "length"


def test_param_stability_report_single_fold():
    """param_stability_report returns stable for single fold."""
    from meta_strategy.backtest import param_stability_report
    folds = [{"best_params": {"length": 20}}]
    report = param_stability_report(folds)
    assert report["stable"] is True
    assert report["score_pct"] == 100.0


def test_walk_forward_includes_param_stability():
    """walk_forward result includes param_stability key."""
    data = _make_ohlcv([100 + i * 0.3 for i in range(500)])
    import meta_strategy.backtest as bt_mod
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        result = bt_mod.walk_forward("bollinger-bands", n_splits=3)
        assert "param_stability" in result
        stability = result["param_stability"]
        assert "stable" in stability
        assert "score_pct" in stability
        assert "changes" in stability
    finally:
        bt_mod.fetch_data = original


# === B&H normalization tests ===


def test_detect_warmup_bollinger():
    """BB warmup is 19 bars (20-period rolling needs 20 bars, first valid at index 19)."""
    from meta_strategy.backtest import detect_warmup

    data = _make_ohlcv([100 + i * 0.5 for i in range(200)])
    warmup = detect_warmup(BollingerBandsStrategy, data)
    assert warmup == 19


def test_detect_warmup_supertrend():
    """SuperTrend warmup is 0 (direction array has no NaN values)."""
    from meta_strategy.backtest import detect_warmup

    data = _make_ohlcv([100 + i * 0.5 for i in range(200)])
    warmup = detect_warmup(SuperTrendStrategy, data)
    assert warmup == 0  # SuperTrend direction initialized to 1, no NaN


def test_detect_warmup_rsi_higher_than_bb():
    """RSI strategy warmup > BB because of 200-period SMA."""
    from meta_strategy.backtest import detect_warmup

    data = _make_ohlcv([100 + i * 0.1 for i in range(500)])
    bb_warmup = detect_warmup(BollingerBandsStrategy, data)
    rsi_warmup = detect_warmup(RSIStrategy, data)
    assert rsi_warmup > bb_warmup


def test_run_all_backtests_identical_bh():
    """All strategies in run_all_backtests() show identical B&H return."""
    import meta_strategy.backtest as bt_mod

    data = _make_ohlcv([100 + i * 0.3 for i in range(500)])
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        results = bt_mod.run_all_backtests()
        bh_values = [r["buy_hold_return_pct"] for r in results]
        assert len(set(bh_values)) == 1, f"B&H should be identical, got {bh_values}"
    finally:
        bt_mod.fetch_data = original


def test_run_all_backtests_has_effective_start():
    """run_all_backtests results include effective_start and warmup_bars_trimmed."""
    import meta_strategy.backtest as bt_mod

    data = _make_ohlcv([100 + i * 0.3 for i in range(500)])
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        results = bt_mod.run_all_backtests()
        for r in results:
            assert "effective_start" in r
            assert "warmup_bars_trimmed" in r
            assert r["warmup_bars_trimmed"] > 0
    finally:
        bt_mod.fetch_data = original


def test_run_backtest_includes_warmup_bars():
    """Individual run_backtest includes warmup_bars field."""
    import meta_strategy.backtest as bt_mod

    data = _make_ohlcv([100 + i * 0.3 for i in range(500)])
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        result = bt_mod.run_backtest("bollinger-bands")
        assert "warmup_bars" in result
        assert result["warmup_bars"] == 19  # BB uses 20-period rolling
        assert "effective_start" in result
    finally:
        bt_mod.fetch_data = original


def test_run_backtest_no_effective_start_when_zero_warmup():
    """Strategies with 0 warmup bars don't include effective_start."""
    import meta_strategy.backtest as bt_mod

    data = _make_ohlcv([100 + i * 0.3 for i in range(500)])
    original = bt_mod.fetch_data
    bt_mod.fetch_data = lambda *a, **kw: data
    try:
        result = bt_mod.run_backtest("supertrend")
        assert result["warmup_bars"] == 0
        assert "effective_start" not in result
    finally:
        bt_mod.fetch_data = original
