"""Local backtesting engine for all three strategies.

Implements the exact same entry/exit logic as the Pine Script strategies
but runs locally with real market data via yfinance + backtesting.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Strategy
from backtesting.lib import (
    FractionalBacktest as _FractionalBacktest,
)
from backtesting.lib import (
    crossover,
)


class Backtest(_FractionalBacktest):
    """FractionalBacktest with numpy read-only array workaround."""

    def run(self, **kwargs) -> pd.Series:
        # Workaround: FractionalBacktest.run() does `indicator /= unit` which
        # fails on read-only numpy arrays. We make them writable first.
        from contextlib import contextmanager

        original_run = _FractionalBacktest.__bases__[0].run  # Backtest.run

        @contextmanager
        def _patch(obj, attr, val):
            orig = getattr(obj, attr)
            setattr(obj, attr, val)
            try:
                yield
            finally:
                setattr(obj, attr, orig)

        with _patch(self, '_data', self._FractionalBacktest__data):
            result = original_run(self, **kwargs)

        trades = result['_trades']
        trades['Size'] *= self._fractional_unit
        trades[['EntryPrice', 'ExitPrice', 'TP', 'SL']] /= self._fractional_unit

        indicators = result['_strategy']._indicators
        for indicator in indicators:
            if indicator._opts['overlay']:
                indicator.setflags(write=True)
                indicator /= self._fractional_unit

        return result


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


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    """Relative Strength Index."""
    close = pd.Series(close)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd_line(close: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
    """MACD line (fast EMA - slow EMA)."""
    close = pd.Series(close)
    return close.ewm(span=fast, adjust=False).mean() - close.ewm(span=slow, adjust=False).mean()


def macd_signal(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
    """MACD signal line."""
    close = pd.Series(close)
    ml = close.ewm(span=fast, adjust=False).mean() - close.ewm(span=slow, adjust=False).mean()
    return ml.ewm(span=signal, adjust=False).mean()


def sma(close: pd.Series, length: int = 200) -> pd.Series:
    """Simple Moving Average."""
    close = pd.Series(close)
    return close.rolling(length).mean()


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


class RSIStrategy(Strategy):
    """RSI overbought/oversold with 200 SMA trend filter.

    Entry: RSI < 30 (oversold) AND close > 200 SMA (uptrend)
    Exit: RSI > 70 (overbought)
    """
    rsi_length = 14
    overbought = 70
    oversold = 30
    sma_length = 200

    def init(self):
        self.rsi_val = self.I(rsi, self.data.Close, self.rsi_length)
        self.sma_val = self.I(sma, self.data.Close, self.sma_length)

    def next(self):
        if not self.position:
            if self.rsi_val[-1] < self.oversold and self.data.Close[-1] > self.sma_val[-1]:
                self.buy()
        elif self.rsi_val[-1] > self.overbought:
            self.position.close()


class MACDStrategy(Strategy):
    """MACD crossover strategy.

    Entry: MACD line crosses above signal line
    Exit: MACD line crosses below signal line
    """
    fast = 12
    slow = 26
    signal_length = 9

    def init(self):
        self.macd = self.I(macd_line, self.data.Close, self.fast, self.slow)
        self.signal = self.I(macd_signal, self.data.Close, self.fast, self.slow, self.signal_length)

    def next(self):
        if not self.position:
            if crossover(self.macd, self.signal):
                self.buy()
        elif crossover(self.signal, self.macd):
            self.position.close()


class ConfluenceStrategy(Strategy):
    """Multi-indicator confluence strategy.

    Combines BB, RSI, and MACD for higher-confidence signals.
    Entry: Close > BB upper AND RSI < 70 AND MACD > Signal (momentum + breakout + not overbought)
    Exit: Close < BB lower OR RSI > 80
    """
    bb_length = 20
    bb_mult = 2.0
    rsi_length = 14
    macd_fast = 12
    macd_slow = 26
    macd_signal_len = 9

    def init(self):
        self.bb_upper = self.I(bollinger_upper, self.data.Close, self.bb_length, self.bb_mult)
        self.bb_lower = self.I(bollinger_lower, self.data.Close, self.bb_length, self.bb_mult)
        self.rsi_val = self.I(rsi, self.data.Close, self.rsi_length)
        self.macd_val = self.I(macd_line, self.data.Close, self.macd_fast, self.macd_slow)
        self.macd_sig = self.I(macd_signal, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal_len)

    def next(self):
        if not self.position:
            if (self.data.Close[-1] > self.bb_upper[-1]
                    and self.rsi_val[-1] < 70
                    and self.macd_val[-1] > self.macd_sig[-1]):
                self.buy()
        elif self.data.Close[-1] < self.bb_lower[-1] or self.rsi_val[-1] > 80:
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
    "rsi": RSIStrategy,
    "macd": MACDStrategy,
    "confluence": ConfluenceStrategy,
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


# === Multi-asset support (#13) ===

DEFAULT_ASSETS = ["BTC-USD", "ETH-USD", "SPY", "AAPL", "MSFT", "GOOG"]


def run_multi_asset(
    strategy_name: str,
    symbols: list[str] | None = None,
    start: str = "2018-01-01",
    **kwargs,
) -> list[dict]:
    """Run a strategy across multiple assets."""
    symbols = symbols or DEFAULT_ASSETS
    results = []
    for sym in symbols:
        try:
            result = run_backtest(strategy_name, symbol=sym, start=start, **kwargs)
            results.append(result)
        except Exception as e:
            results.append({
                "strategy": strategy_name,
                "symbol": sym,
                "period": f"{start} → error",
                "return_pct": 0.0,
                "buy_hold_return_pct": 0.0,
                "win_rate_pct": 0.0,
                "num_trades": 0,
                "max_drawdown_pct": 0.0,
                "sharpe_ratio": 0.0,
                "final_equity": 0.0,
                "error": str(e),
            })
    return results


# === Parameter optimization with grid search (#14) ===

PARAM_GRIDS: dict[str, dict[str, list]] = {
    "bollinger-bands": {
        "length": [10, 15, 20, 25, 30],
        "mult": [1.5, 2.0, 2.5, 3.0],
    },
    "supertrend": {
        "period": [7, 10, 14, 20],
        "factor": [1.5, 2.0, 3.0, 4.0],
    },
    "bull-market-support-band": {
        "sma_length": [15, 20, 25],
        "ema_length": [18, 21, 25],
    },
    "rsi": {
        "rsi_length": [7, 14, 21],
        "oversold": [20, 30, 40],
    },
    "macd": {
        "fast": [8, 12, 16],
        "slow": [21, 26, 30],
    },
    "confluence": {
        "bb_length": [15, 20, 25],
        "rsi_length": [10, 14, 21],
    },
}


def _extract_metrics(stats) -> dict:
    """Extract standard metrics from backtesting.py stats Series."""
    return {
        "return_pct": round(float(stats["Return [%]"]), 2),
        "sharpe_ratio": round(float(stats["Sharpe Ratio"]), 2) if not pd.isna(stats["Sharpe Ratio"]) else 0.0,
        "num_trades": int(stats["# Trades"]),
        "max_drawdown_pct": round(float(stats["Max. Drawdown [%]"]), 2),
        "win_rate_pct": round(float(stats["Win Rate [%]"]), 2) if not pd.isna(stats["Win Rate [%]"]) else 0.0,
    }


def optimize_strategy(
    strategy_name: str,
    symbol: str = "BTC-USD",
    start: str = "2018-01-01",
    end: str | None = None,
    cash: float = 100_000.0,
    commission: float = 0.001,
    param_grid: dict[str, list] | None = None,
    split: float = 0.7,
) -> list[dict]:
    """Grid search over parameter combinations with optional train/test split.

    Args:
        split: Fraction of data for training (0.0-1.0). Default 0.7 = 70% train, 30% test.
               Use 1.0 for legacy behavior (no split).
    """
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    if not 0.0 < split <= 1.0:
        raise ValueError(f"split must be in (0, 1.0], got {split}")

    grid = param_grid or PARAM_GRIDS.get(strategy_name, {})
    if not grid:
        raise ValueError(f"No parameter grid defined for {strategy_name}")

    data = fetch_data(symbol, start, end)
    strategy_cls = STRATEGIES[strategy_name]

    has_split = split < 1.0
    if has_split:
        split_idx = int(len(data) * split)
        train_data = data.iloc[:split_idx]
        test_data = data.iloc[split_idx:]
    else:
        train_data = data
        test_data = None

    import itertools
    param_names = list(grid.keys())
    param_values = list(grid.values())
    combinations = list(itertools.product(*param_values))

    results = []
    for combo in combinations:
        params = dict(zip(param_names, combo))
        try:
            bt_train = Backtest(train_data, strategy_cls, cash=cash, commission=commission, exclusive_orders=True)
            train_stats = bt_train.run(**params)
            entry = {"params": params}
            train_metrics = _extract_metrics(train_stats)

            if has_split:
                entry["is_return_pct"] = train_metrics["return_pct"]
                entry["is_sharpe_ratio"] = train_metrics["sharpe_ratio"]
                entry["is_num_trades"] = train_metrics["num_trades"]
                entry["is_max_drawdown_pct"] = train_metrics["max_drawdown_pct"]
                entry["is_win_rate_pct"] = train_metrics["win_rate_pct"]

                bt_test = Backtest(test_data, strategy_cls, cash=cash, commission=commission, exclusive_orders=True)
                test_stats = bt_test.run(**params)
                oos_metrics = _extract_metrics(test_stats)
                entry["return_pct"] = oos_metrics["return_pct"]
                entry["sharpe_ratio"] = oos_metrics["sharpe_ratio"]
                entry["num_trades"] = oos_metrics["num_trades"]
                entry["max_drawdown_pct"] = oos_metrics["max_drawdown_pct"]
                entry["win_rate_pct"] = oos_metrics["win_rate_pct"]
            else:
                entry.update(train_metrics)

            results.append(entry)
        except Exception:
            pass

    sort_key = "sharpe_ratio"
    results.sort(key=lambda r: r[sort_key], reverse=True)
    return results


# === Walk-forward analysis (#15) ===

def _optimize_on_data(train_data, strategy_cls, grid, cash, commission):
    """Find best params by grid search on training data. Returns (best_params, best_sharpe)."""
    best_params = {}
    best_sharpe = -999.0
    if grid:
        import itertools
        param_names = list(grid.keys())
        for combo in itertools.product(*grid.values()):
            params = dict(zip(param_names, combo))
            try:
                bt = Backtest(train_data, strategy_cls, cash=cash, commission=commission, exclusive_orders=True)
                stats = bt.run(**params)
                sharpe = float(stats["Sharpe Ratio"]) if not pd.isna(stats["Sharpe Ratio"]) else -999.0
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_params = params
            except Exception:
                pass
    return best_params, best_sharpe


def _evaluate_fold(train_data, test_data, strategy_cls, grid, cash, commission, fold_num):
    """Optimize on train, evaluate on test. Returns fold dict or None."""
    best_params, best_sharpe = _optimize_on_data(train_data, strategy_cls, grid, cash, commission)
    try:
        bt = Backtest(test_data, strategy_cls, cash=cash, commission=commission, exclusive_orders=True)
        test_stats = bt.run(**best_params)
        return {
            "fold": fold_num,
            "train_period": f"{train_data.index[0].strftime('%Y-%m-%d')} → {train_data.index[-1].strftime('%Y-%m-%d')}",
            "test_period": f"{test_data.index[0].strftime('%Y-%m-%d')} → {test_data.index[-1].strftime('%Y-%m-%d')}",
            "best_params": best_params,
            "train_sharpe": round(best_sharpe, 2) if best_sharpe > -999 else 0.0,
            "test_return_pct": round(float(test_stats["Return [%]"]), 2),
            "test_sharpe": round(float(test_stats["Sharpe Ratio"]), 2) if not pd.isna(test_stats["Sharpe Ratio"]) else 0.0,
            "test_trades": int(test_stats["# Trades"]),
            "test_max_dd_pct": round(float(test_stats["Max. Drawdown [%]"]), 2),
        }
    except Exception:
        return None


def _sequential_folds(data, n_splits, train_pct):
    """Generate (train_data, test_data, fold_num) for sequential non-overlapping windows."""
    n = len(data)
    window_size = n // n_splits
    for i in range(n_splits):
        fold_start = i * window_size
        fold_end = min((i + 1) * window_size, n)
        fold_data = data.iloc[fold_start:fold_end]
        if len(fold_data) < 50:
            continue
        train_end = int(len(fold_data) * train_pct)
        train_data = fold_data.iloc[:train_end]
        test_data = fold_data.iloc[train_end:]
        if len(train_data) < 30 or len(test_data) < 10:
            continue
        yield train_data, test_data, i + 1


def _rolling_folds(data, train_bars, step):
    """Generate (train_data, test_data, fold_num) for rolling fixed-size window."""
    n = len(data)
    fold_num = 0
    i = 0
    while i + train_bars + step <= n:
        fold_num += 1
        train_data = data.iloc[i:i + train_bars]
        test_data = data.iloc[i + train_bars:i + train_bars + step]
        if len(train_data) < 30 or len(test_data) < 10:
            i += step
            continue
        yield train_data, test_data, fold_num
        i += step


def _expanding_folds(data, train_bars, step):
    """Generate (train_data, test_data, fold_num) for expanding window (train grows from start)."""
    n = len(data)
    fold_num = 0
    train_end = train_bars
    while train_end + step <= n:
        fold_num += 1
        train_data = data.iloc[:train_end]
        test_data = data.iloc[train_end:train_end + step]
        if len(train_data) < 30 or len(test_data) < 10:
            train_end += step
            continue
        yield train_data, test_data, fold_num
        train_end += step


def walk_forward(
    strategy_name: str,
    symbol: str = "BTC-USD",
    start: str = "2018-01-01",
    end: str | None = None,
    cash: float = 100_000.0,
    commission: float = 0.001,
    n_splits: int = 5,
    train_pct: float = 0.7,
    mode: str = "sequential",
    train_bars: int | None = None,
    step: int | None = None,
) -> dict:
    """Walk-forward analysis with multiple windowing modes.

    Modes:
        sequential: Split into n_splits non-overlapping chunks (original behavior).
        rolling: Fixed-size train window slides forward by step bars.
        expanding: Train grows from start, test is next step bars.

    Args:
        mode: 'sequential', 'rolling', or 'expanding'.
        train_bars: Training window size in bars (rolling/expanding modes).
        step: Step size in bars for sliding the window (rolling/expanding modes).
    """
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    if mode not in ("sequential", "rolling", "expanding"):
        raise ValueError(f"mode must be 'sequential', 'rolling', or 'expanding', got '{mode}'")

    data = fetch_data(symbol, start, end)
    strategy_cls = STRATEGIES[strategy_name]
    grid = PARAM_GRIDS.get(strategy_name, {})

    if mode == "sequential":
        fold_gen = _sequential_folds(data, n_splits, train_pct)
    elif mode == "rolling":
        tb = train_bars or 500
        st = step or 100
        fold_gen = _rolling_folds(data, tb, st)
    else:  # expanding
        tb = train_bars or 500
        st = step or 100
        fold_gen = _expanding_folds(data, tb, st)

    folds = []
    for train_data, test_data, fold_num in fold_gen:
        result = _evaluate_fold(train_data, test_data, strategy_cls, grid, cash, commission, fold_num)
        if result:
            folds.append(result)

    avg_test_return = np.mean([f["test_return_pct"] for f in folds]) if folds else 0.0
    avg_test_sharpe = np.mean([f["test_sharpe"] for f in folds]) if folds else 0.0

    return {
        "strategy": strategy_name,
        "symbol": symbol,
        "mode": mode,
        "n_splits": n_splits if mode == "sequential" else len(folds),
        "train_pct": train_pct if mode == "sequential" else None,
        "train_bars": train_bars if mode != "sequential" else None,
        "step": step if mode != "sequential" else None,
        "folds": folds,
        "avg_test_return_pct": round(float(avg_test_return), 2),
        "avg_test_sharpe": round(float(avg_test_sharpe), 2),
    }
