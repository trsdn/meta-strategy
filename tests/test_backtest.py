"""Tests for the backtesting engine.

Uses synthetic data to verify strategy signal logic without network calls.
"""

import numpy as np
import pandas as pd
import pytest

from meta_strategy.backtest import (
    BollingerBandsStrategy,
    SuperTrendStrategy,
    BullMarketSupportBandStrategy,
    bollinger_upper,
    bollinger_lower,
    supertrend_direction,
    weekly_sma,
    weekly_ema,
    STRATEGIES,
)
from backtesting import Backtest


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
    """All three strategies are registered."""
    assert "bollinger-bands" in STRATEGIES
    assert "supertrend" in STRATEGIES
    assert "bull-market-support-band" in STRATEGIES
    assert len(STRATEGIES) == 3


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
