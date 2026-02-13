"""Tests for the risk analysis module."""

import numpy as np
import pandas as pd

from meta_strategy.risk import _max_consecutive, compute_risk_metrics


def test_compute_risk_metrics_uptrend():
    """Risk metrics for a growing equity curve with some volatility."""
    np.random.seed(42)
    # Strong uptrend but with enough noise for some down days
    base = np.array([100_000 + i * 100 for i in range(252)], dtype=float)
    noise = np.cumsum(np.random.normal(0, 200, 252))
    equity = pd.Series(base + noise)
    m = compute_risk_metrics(equity)

    assert m["total_return_pct"] > 0
    assert m["calmar_ratio"] > 0
    assert m["max_drawdown_pct"] >= 0
    assert m["max_consecutive_losses"] >= 0
    assert m["max_consecutive_wins"] >= 0
    assert m["profit_factor"] > 0
    # Sortino should be positive for a strong uptrend with some downside vol
    assert m["sortino_ratio"] > 0


def test_compute_risk_metrics_downtrend():
    """Risk metrics for a declining equity curve."""
    equity = pd.Series([100_000 - i * 200 for i in range(252)])
    m = compute_risk_metrics(equity)

    assert m["total_return_pct"] < 0
    assert m["max_drawdown_pct"] > 0
    assert m["max_consecutive_losses"] > 0


def test_compute_risk_metrics_flat():
    """Risk metrics for flat equity."""
    equity = pd.Series([100_000.0] * 100)
    m = compute_risk_metrics(equity)

    assert m["total_return_pct"] == 0.0
    assert m["sortino_ratio"] == 0.0
    assert m["max_drawdown_pct"] == 0.0


def test_compute_risk_metrics_too_short():
    """Risk metrics handles very short series."""
    equity = pd.Series([100_000.0])
    m = compute_risk_metrics(equity)
    assert m["sortino_ratio"] == 0.0


def test_max_consecutive():
    """Max consecutive 1s in binary series."""
    s = pd.Series([1, 1, 0, 1, 1, 1, 0, 1])
    assert _max_consecutive(s) == 3


def test_max_consecutive_all_zeros():
    """Max consecutive with no 1s."""
    s = pd.Series([0, 0, 0])
    assert _max_consecutive(s) == 0


def test_max_consecutive_empty():
    """Max consecutive with empty series."""
    s = pd.Series([], dtype=int)
    assert _max_consecutive(s) == 0
