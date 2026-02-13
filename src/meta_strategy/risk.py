"""Risk analysis module: Monte Carlo simulation and extended risk metrics.

Provides robustness testing through trade resampling and additional
risk-adjusted performance metrics beyond Sharpe ratio.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Backtest

from .backtest import STRATEGIES, fetch_data

# === Extended Risk Metrics (#24) ===

def compute_risk_metrics(equity_series: pd.Series, risk_free_rate: float = 0.0) -> dict:
    """Compute extended risk metrics from an equity curve.

    Args:
        equity_series: Daily equity values
        risk_free_rate: Annualized risk-free rate (default 0)

    Returns:
        Dict with Sortino, Calmar, max consecutive losses, etc.
    """
    returns = equity_series.pct_change().dropna()

    if len(returns) < 2:
        return _empty_metrics()

    # Annualization factor (252 trading days)
    ann = 252

    # Sortino Ratio — penalizes only downside volatility
    downside = returns[returns < 0]
    downside_std = downside.std() * np.sqrt(ann) if len(downside) > 0 else 0.0
    mean_return = returns.mean() * ann
    sortino = (mean_return - risk_free_rate) / downside_std if downside_std > 0 else 0.0

    # Calmar Ratio — return / max drawdown
    cummax = equity_series.cummax()
    drawdown = (equity_series - cummax) / cummax
    max_dd = abs(drawdown.min())
    total_return = (equity_series.iloc[-1] / equity_series.iloc[0]) - 1
    years = len(returns) / ann
    annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0.0
    calmar = annual_return / max_dd if max_dd > 0 else 0.0

    # Max consecutive losses
    is_loss = (returns < 0).astype(int)
    max_consec_losses = _max_consecutive(is_loss)

    # Max consecutive wins
    is_win = (returns > 0).astype(int)
    max_consec_wins = _max_consecutive(is_win)

    # Profit factor
    gross_profit = returns[returns > 0].sum()
    gross_loss = abs(returns[returns < 0].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    # Recovery factor
    recovery_factor = total_return / max_dd if max_dd > 0 else 0.0

    return {
        "sortino_ratio": round(float(sortino), 3),
        "calmar_ratio": round(float(calmar), 3),
        "max_consecutive_losses": int(max_consec_losses),
        "max_consecutive_wins": int(max_consec_wins),
        "profit_factor": round(float(profit_factor), 3),
        "recovery_factor": round(float(recovery_factor), 3),
        "annual_return_pct": round(float(annual_return * 100), 2),
        "downside_deviation": round(float(downside_std), 4),
        "max_drawdown_pct": round(float(max_dd * 100), 2),
        "total_return_pct": round(float(total_return * 100), 2),
    }


def _max_consecutive(binary_series: pd.Series) -> int:
    """Count max consecutive 1s in a binary series."""
    if len(binary_series) == 0:
        return 0
    groups = binary_series.ne(binary_series.shift()).cumsum()
    return int(binary_series.groupby(groups).sum().max()) if binary_series.any() else 0


def _empty_metrics() -> dict:
    return {
        "sortino_ratio": 0.0,
        "calmar_ratio": 0.0,
        "max_consecutive_losses": 0,
        "max_consecutive_wins": 0,
        "profit_factor": 0.0,
        "recovery_factor": 0.0,
        "annual_return_pct": 0.0,
        "downside_deviation": 0.0,
        "max_drawdown_pct": 0.0,
        "total_return_pct": 0.0,
    }


# === Monte Carlo Simulation (#23) ===

def monte_carlo(
    strategy_name: str,
    symbol: str = "BTC-USD",
    start: str = "2018-01-01",
    end: str | None = None,
    cash: float = 100_000.0,
    commission: float = 0.001,
    n_simulations: int = 1000,
    seed: int | None = 42,
) -> dict:
    """Monte Carlo simulation via trade return resampling.

    Runs the strategy once, extracts individual trade returns,
    then resamples them N times to build a distribution of outcomes.
    """
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    data = fetch_data(symbol, start, end)
    strategy_cls = STRATEGIES[strategy_name]
    bt = Backtest(data, strategy_cls, cash=cash, commission=commission, exclusive_orders=True)
    stats = bt.run()

    # Extract trade returns
    trades_df = stats["_trades"]
    if trades_df.empty:
        return {
            "strategy": strategy_name,
            "symbol": symbol,
            "n_trades": 0,
            "n_simulations": n_simulations,
            "percentiles": {},
            "median_return_pct": 0.0,
            "p5_return_pct": 0.0,
            "p95_return_pct": 0.0,
            "prob_profit_pct": 0.0,
        }

    trade_returns = trades_df["ReturnPct"].values / 100.0  # Convert from percentage
    n_trades = len(trade_returns)

    rng = np.random.default_rng(seed)
    sim_returns = []

    for _ in range(n_simulations):
        # Resample trades with replacement
        sampled = rng.choice(trade_returns, size=n_trades, replace=True)
        # Compound returns
        total = np.prod(1 + sampled) - 1
        sim_returns.append(total * 100)  # Back to percentage

    sim_returns = np.array(sim_returns)
    percentiles = {
        "p5": round(float(np.percentile(sim_returns, 5)), 2),
        "p25": round(float(np.percentile(sim_returns, 25)), 2),
        "p50": round(float(np.percentile(sim_returns, 50)), 2),
        "p75": round(float(np.percentile(sim_returns, 75)), 2),
        "p95": round(float(np.percentile(sim_returns, 95)), 2),
    }

    return {
        "strategy": strategy_name,
        "symbol": symbol,
        "n_trades": n_trades,
        "n_simulations": n_simulations,
        "original_return_pct": round(float(stats["Return [%]"]), 2),
        "percentiles": percentiles,
        "median_return_pct": percentiles["p50"],
        "p5_return_pct": percentiles["p5"],
        "p95_return_pct": percentiles["p95"],
        "prob_profit_pct": round(float((sim_returns > 0).mean() * 100), 1),
        "mean_return_pct": round(float(sim_returns.mean()), 2),
        "std_return_pct": round(float(sim_returns.std()), 2),
    }


def run_risk_analysis(
    strategy_name: str,
    symbol: str = "BTC-USD",
    start: str = "2018-01-01",
    end: str | None = None,
    cash: float = 100_000.0,
    commission: float = 0.001,
) -> dict:
    """Run a strategy and return extended risk metrics."""
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    data = fetch_data(symbol, start, end)
    strategy_cls = STRATEGIES[strategy_name]
    bt = Backtest(data, strategy_cls, cash=cash, commission=commission, exclusive_orders=True)
    stats = bt.run()

    equity = stats["_equity_curve"]["Equity"]
    metrics = compute_risk_metrics(equity)
    metrics["strategy"] = strategy_name
    metrics["symbol"] = symbol
    metrics["num_trades"] = int(stats["# Trades"])
    metrics["sharpe_ratio"] = round(float(stats["Sharpe Ratio"]), 3) if not pd.isna(stats["Sharpe Ratio"]) else 0.0

    return metrics
