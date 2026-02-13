"""Local backtesting engine for all three strategies.

Implements the exact same entry/exit logic as the Pine Script strategies
but runs locally with real market data via yfinance + backtesting.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover


# === Indicator functions (used by backtesting.py's self.I()) ===

def bollinger_upper(close: pd.Series, length: int = 20, mult: float = 2.0) -> pd.Series:
    close = pd.Series(close)
    basis = close.rolling(length).mean()
    dev = mult * close.rolling(length).std(ddof=0)
    return basis + dev


def bollinger_lower(close: pd.Series, length: int = 20, mult: float = 2.0) -> pd.Series:
    close = pd.Series(close)
    basis = close.rolling(length).mean()
    dev = mult * close.rolling(length).std(ddof=0)
    return basis - dev


def supertrend_line(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 10, factor: float = 3.0) -> pd.Series:
    """Calculate SuperTrend line. Returns the supertrend value per bar."""
    high, low, close = pd.Series(high), pd.Series(low), pd.Series(close)
    hl2 = (high + low) / 2
    # ATR calculation
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    upper_band = hl2 + factor * atr
    lower_band = hl2 - factor * atr

    n = len(close)
    st = np.zeros(n)
    direction = np.ones(n, dtype=int)
    final_upper = upper_band.values.copy()
    final_lower = lower_band.values.copy()

    for i in range(1, n):
        if np.isnan(lower_band.iloc[i]) or np.isnan(upper_band.iloc[i]):
            continue
        # Initialize on first valid bar
        if np.isnan(final_lower[i - 1]):
            final_lower[i] = lower_band.iloc[i]
            final_upper[i] = upper_band.iloc[i]
            st[i] = final_lower[i]
            continue
        # Lower band (support) — only moves up
        if lower_band.iloc[i] > final_lower[i - 1] or close.iloc[i - 1] < final_lower[i - 1]:
            final_lower[i] = lower_band.iloc[i]
        else:
            final_lower[i] = final_lower[i - 1]

        # Upper band (resistance) — only moves down
        if upper_band.iloc[i] < final_upper[i - 1] or close.iloc[i - 1] > final_upper[i - 1]:
            final_upper[i] = upper_band.iloc[i]
        else:
            final_upper[i] = final_upper[i - 1]

        # Direction
        if direction[i - 1] == -1 and close.iloc[i] > final_lower[i - 1]:
            direction[i] = 1
        elif direction[i - 1] == 1 and close.iloc[i] < final_upper[i - 1]:
            direction[i] = -1
        else:
            direction[i] = direction[i - 1]

        st[i] = final_lower[i] if direction[i] == 1 else final_upper[i]

    return pd.Series(st, index=close.index)


def supertrend_direction(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 10, factor: float = 3.0) -> pd.Series:
    """Returns +1 for bullish (green), -1 for bearish (red)."""
    high, low, close = pd.Series(high), pd.Series(low), pd.Series(close)
    hl2 = (high + low) / 2
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    upper_band = hl2 + factor * atr
    lower_band = hl2 - factor * atr

    n = len(close)
    direction = np.ones(n, dtype=int)
    final_upper = upper_band.values.copy()
    final_lower = lower_band.values.copy()

    for i in range(1, n):
        if np.isnan(lower_band.iloc[i]) or np.isnan(upper_band.iloc[i]):
            continue
        # Initialize on first valid bar
        if np.isnan(final_lower[i - 1]):
            final_lower[i] = lower_band.iloc[i]
            final_upper[i] = upper_band.iloc[i]
            continue
        # Lower band (support) — only moves up
        if lower_band.iloc[i] > final_lower[i - 1] or close.iloc[i - 1] < final_lower[i - 1]:
            final_lower[i] = lower_band.iloc[i]
        else:
            final_lower[i] = final_lower[i - 1]
        # Upper band (resistance) — only moves down
        if upper_band.iloc[i] < final_upper[i - 1] or close.iloc[i - 1] > final_upper[i - 1]:
            final_upper[i] = upper_band.iloc[i]
        else:
            final_upper[i] = final_upper[i - 1]
        # Direction
        if direction[i - 1] == -1 and close.iloc[i] > final_lower[i - 1]:
            direction[i] = 1
        elif direction[i - 1] == 1 and close.iloc[i] < final_upper[i - 1]:
            direction[i] = -1
        else:
            direction[i] = direction[i - 1]

    return pd.Series(direction, index=close.index)


def weekly_sma(close: pd.Series, length: int = 20) -> pd.Series:
    """Simulate weekly SMA on daily data (5 trading days per week)."""
    close = pd.Series(close)
    weekly_length = length * 5
    return close.rolling(weekly_length).mean()


def weekly_ema(close: pd.Series, length: int = 21) -> pd.Series:
    """Simulate weekly EMA on daily data."""
    close = pd.Series(close)
    weekly_length = length * 5
    return close.ewm(span=weekly_length, adjust=False).mean()


# === Strategy classes ===

class BollingerBandsStrategy(Strategy):
    """Bollinger Bands trend-following breakout.

    Entry: Close > Upper Band (buying strength)
    Exit: Close < Lower Band
    Expected: ~1,187% Net Profit (from input.md)
    """
    length = 20
    mult = 2.0

    def init(self):
        self.upper = self.I(bollinger_upper, self.data.Close, self.length, self.mult)
        self.lower = self.I(bollinger_lower, self.data.Close, self.length, self.mult)

    def next(self):
        if not self.position:
            if self.data.Close[-1] > self.upper[-1]:
                self.buy()
        elif self.data.Close[-1] < self.lower[-1]:
            self.position.close()


class SuperTrendStrategy(Strategy):
    """SuperTrend trend-following.

    Entry: Trend turns Green (direction changes from -1 to +1)
    Exit: Trend turns Red (direction changes from +1 to -1)
    """
    period = 10
    factor = 3.0

    def init(self):
        self.direction = self.I(supertrend_direction, self.data.High, self.data.Low, self.data.Close, self.period, self.factor)

    def next(self):
        if not self.position:
            if self.direction[-1] == 1 and self.direction[-2] == -1:
                self.buy()
        elif self.direction[-1] == -1 and self.direction[-2] == 1:
            self.position.close()


class BullMarketSupportBandStrategy(Strategy):
    """Bull Market Support Band (20w SMA + 21w EMA crossover).

    Entry: EMA crosses above SMA (bullish crossover)
    Exit: EMA crosses below SMA (bearish crossunder)
    Expected: ~736% Net Profit (from input.md)
    """
    sma_length = 20
    ema_length = 21

    def init(self):
        self.sma = self.I(weekly_sma, self.data.Close, self.sma_length)
        self.ema = self.I(weekly_ema, self.data.Close, self.ema_length)

    def next(self):
        if not self.position:
            if crossover(self.ema, self.sma):
                self.buy()
        elif crossover(self.sma, self.ema):
            self.position.close()


# === Data fetching ===

def fetch_data(symbol: str = "BTC-USD", start: str = "2018-01-01", end: str | None = None) -> pd.DataFrame:
    """Fetch OHLCV data via yfinance."""
    import yfinance as yf
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end, auto_adjust=True)
    # backtesting.py expects columns: Open, High, Low, Close, Volume
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.index.name = None
    return df


# === Run backtest ===

STRATEGIES = {
    "bollinger-bands": BollingerBandsStrategy,
    "supertrend": SuperTrendStrategy,
    "bull-market-support-band": BullMarketSupportBandStrategy,
}


def run_backtest(
    strategy_name: str,
    symbol: str = "BTC-USD",
    start: str = "2018-01-01",
    end: str | None = None,
    cash: float = 100_000.0,
    commission: float = 0.001,
) -> dict:
    """Run a backtest and return results as a dict."""
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(STRATEGIES.keys())}")

    data = fetch_data(symbol, start, end)
    strategy_cls = STRATEGIES[strategy_name]

    bt = Backtest(data, strategy_cls, cash=cash, commission=commission, exclusive_orders=True)
    stats = bt.run()

    return {
        "strategy": strategy_name,
        "symbol": symbol,
        "period": f"{start} → {data.index[-1].strftime('%Y-%m-%d')}",
        "return_pct": round(float(stats["Return [%]"]), 2),
        "buy_hold_return_pct": round(float(stats["Buy & Hold Return [%]"]), 2),
        "win_rate_pct": round(float(stats["Win Rate [%]"]), 2) if not pd.isna(stats["Win Rate [%]"]) else 0.0,
        "num_trades": int(stats["# Trades"]),
        "max_drawdown_pct": round(float(stats["Max. Drawdown [%]"]), 2),
        "sharpe_ratio": round(float(stats["Sharpe Ratio"]), 2) if not pd.isna(stats["Sharpe Ratio"]) else 0.0,
        "final_equity": round(float(stats["Equity Final [$]"]), 2),
    }


def run_all_backtests(symbol: str = "BTC-USD", start: str = "2018-01-01", **kwargs) -> list[dict]:
    """Run all strategies and return results."""
    results = []
    for name in STRATEGIES:
        result = run_backtest(name, symbol=symbol, start=start, **kwargs)
        results.append(result)
    return results
