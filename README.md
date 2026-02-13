# Meta Strategy

AI-powered TradingView indicator-to-strategy converter with a full local backtesting engine. Translates Pine Script indicators into backtestable strategies, runs them locally on real market data, and provides optimization, risk analysis, and reporting tools.

## What This Does

TradingView **indicators** show signals on a chart but can't be backtested. TradingView **strategies** can be backtested (Win Rate, Profit Factor, Drawdown). This tool:

1. **Converts** indicators → strategies via structured AI prompts
2. **Backtests** strategies locally with real market data (no TradingView needed)
3. **Optimizes** parameters via grid search with train/test split
4. **Validates** walk-forward with rolling/expanding windows and overfitting detection
5. **Analyzes** risk with Monte Carlo simulation and extended metrics
6. **Reports** results as HTML dashboards, CSV, or JSON

## Strategy Catalog

All 6 strategies have YAML definitions, indicator sources, and generated AI prompts.

| Strategy | Entry | Exit |
|----------|-------|------|
| **Bollinger Bands** | Close > Upper Band (breakout) | Close < Lower Band |
| **SuperTrend** | Direction flips to +1 (bullish) | Direction flips to -1 (bearish) |
| **Bull Market Support Band** | EMA > SMA crossover | SMA > EMA crossunder |
| **RSI** | RSI < 30 + above 200 SMA | RSI > 70 |
| **MACD** | MACD crosses above signal | MACD crosses below signal |
| **Confluence** | BB breakout + RSI < 70 + MACD > Signal | Close < BB lower OR RSI > 80 |

> **Note:** `backtest-all` normalizes Buy & Hold returns across strategies by accounting for indicator warmup periods. Use `--interval` to test on different timeframes (1h, 4h, 1d).

## Quick Start

```bash
# Install
uv sync --extra dev

# Run all backtests (daily candles, BTC-USD)
meta-strategy backtest-all

# Backtest on hourly candles
meta-strategy backtest bollinger-bands --symbol BTC-USD --interval 1h

# Optimize parameters with train/test split
meta-strategy optimize bollinger-bands --top 10 --split 0.7

# Walk-forward analysis (rolling windows)
meta-strategy walk-forward bollinger-bands --mode rolling --train-bars 500 --step 100

# Monte Carlo simulation
meta-strategy monte-carlo bollinger-bands --simulations 1000

# Extended risk metrics
meta-strategy risk-metrics bollinger-bands

# Multi-asset comparison
meta-strategy multi-asset bollinger-bands --symbols BTC-USD,ETH-USD,SPY

# Generate HTML dashboard
meta-strategy dashboard --output dashboard.html

# Export results
meta-strategy export --fmt json
meta-strategy export --fmt csv
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `backtest` | Run backtest for a single strategy |
| `backtest-all` | Run all strategies with normalized B&H comparison |
| `multi-asset` | Run a strategy across multiple assets |
| `optimize` | Grid search with train/test split and overfitting detection |
| `walk-forward` | Walk-forward validation (sequential/rolling/expanding) |
| `monte-carlo` | Monte Carlo trade resampling simulation |
| `risk-metrics` | Extended risk metrics (Sortino, Calmar, etc.) |
| `report` | Generate HTML report with equity curve |
| `dashboard` | Generate comparison dashboard for all strategies |
| `export` | Export results to CSV or JSON |
| `generate` | Generate AI prompt from strategy definition |
| `validate` | Validate a YAML strategy definition |
| `validate-pine` | Validate Pine Script for common pitfalls |
| `list` | List available strategy definitions |

### Key Options

| Option | Available On | Description |
|--------|-------------|-------------|
| `--interval` | backtest, backtest-all, optimize, walk-forward | Candle interval: 1h, 4h, 1d (default: 1d) |
| `--split` | optimize | Train/test split ratio (default: 0.7) |
| `--mode` | walk-forward | Window mode: sequential, rolling, expanding |
| `--cash` | all backtest commands | Initial capital (default: $100k) |

## Development

```bash
uv run pytest tests/ -v        # Run tests (85+ tests)
uv run ruff check src/          # Lint
uv run ruff format src/         # Format
uv run mypy src/                # Type check
```

## Project Structure

```
├── src/meta_strategy/
│   ├── backtest.py       # 6 strategy classes, indicators, optimization, walk-forward
│   ├── reports.py        # HTML reports, SVG equity charts, CSV/JSON export
│   ├── risk.py           # Monte Carlo simulation, extended risk metrics
│   ├── models.py         # StrategyDefinition Pydantic model
│   ├── engine.py         # Prompt template engine
│   ├── validator.py      # Pine Script pitfall validator
│   └── cli.py            # Typer CLI (14 commands)
├── strategies/
│   ├── definitions/      # 6 YAML strategy definitions
│   ├── indicators/       # 6 Pine Script indicator sources
│   └── ai-*.pine         # Generated AI conversion prompts
├── tests/                # 85+ tests
└── docs/
    ├── sprints/          # Sprint logs and velocity tracking
    └── architecture/     # ADRs
```

## License

MIT
