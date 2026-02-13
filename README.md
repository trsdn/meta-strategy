# Meta Strategy

AI-powered TradingView indicator-to-strategy converter with a full local backtesting engine. Translates Pine Script indicators into backtestable strategies, runs them locally on real market data, and provides optimization, risk analysis, and reporting tools.

## What This Does

TradingView **indicators** show signals on a chart but can't be backtested. TradingView **strategies** can be backtested (Win Rate, Profit Factor, Drawdown). This tool:

1. **Converts** indicators → strategies via structured AI prompts
2. **Backtests** strategies locally with real market data (no TradingView needed)
3. **Optimizes** parameters via grid search and walk-forward analysis
4. **Analyzes** risk with Monte Carlo simulation and extended metrics
5. **Reports** results as HTML dashboards, CSV, or JSON

## Strategy Catalog

| Strategy | Entry | Exit | BTC-USD Return | Sharpe |
|----------|-------|------|---------------|--------|
| **Bollinger Bands** | Close > Upper Band | Close < Lower Band | 1,804% | 0.67 |
| **SuperTrend** | Direction flips to +1 | Direction flips to -1 | -64% | -0.39 |
| **Bull Market Support Band** | EMA > SMA crossover | SMA > EMA crossunder | 211% | 0.28 |
| **RSI** | RSI < 30 + above 200 SMA | RSI > 70 | — | — |
| **MACD** | MACD crosses above signal | MACD crosses below signal | — | — |
| **Confluence** | BB breakout + RSI ok + MACD up | BB lower or RSI > 80 | — | — |

## Quick Start

```bash
# Install
uv sync --dev

# Run all backtests
meta-strategy backtest-all

# Backtest a single strategy
meta-strategy backtest bollinger-bands --symbol BTC-USD

# Optimize parameters
meta-strategy optimize bollinger-bands --top 10

# Walk-forward analysis
meta-strategy walk-forward bollinger-bands --splits 5

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
| `backtest-all` | Run all strategies, show comparison table |
| `multi-asset` | Run a strategy across multiple assets |
| `optimize` | Grid search parameter optimization |
| `walk-forward` | Walk-forward out-of-sample validation |
| `monte-carlo` | Monte Carlo trade resampling simulation |
| `risk-metrics` | Extended risk metrics (Sortino, Calmar, etc.) |
| `report` | Generate HTML report with equity curve |
| `dashboard` | Generate comparison dashboard for all strategies |
| `export` | Export results to CSV or JSON |
| `generate` | Generate AI prompt from strategy definition |
| `validate` | Validate a YAML strategy definition |
| `validate-pine` | Validate Pine Script for common pitfalls |
| `list` | List available strategy definitions |

## Development

```bash
uv run python -m pytest tests/ -v        # Run tests (58+ tests)
uv run ruff check src/                    # Lint
uv run ruff format src/                   # Format
uv run mypy src/                          # Type check
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
│   ├── definitions/      # YAML strategy definitions
│   ├── indicators/       # Raw indicator Pine Script source
│   └── output/           # Generated strategies + backtest results
├── tests/                # 58+ tests
└── docs/
    ├── sprints/          # Sprint logs and velocity tracking
    └── architecture/     # ADRs
```

## License

MIT
