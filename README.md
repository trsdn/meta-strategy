# Meta Strategy

AI-powered TradingView indicator-to-strategy converter. Translates visual Pine Script indicators into backtestable strategy scripts using a structured prompt template workflow.

## What This Does

TradingView **indicators** show signals on a chart but can't be backtested. TradingView **strategies** can be backtested (Win Rate, Profit Factor, Drawdown). This tool automates the conversion:

1. **Define** entry/exit rules in a YAML file
2. **Generate** a filled AI prompt from the indicator source + rules
3. **Validate** the generated Pine Script for common pitfalls

## Strategy Catalog

| Strategy | Entry | Exit | Expected Result |
|----------|-------|------|-----------------|
| **Bollinger Bands** (Breakout) | Close > Upper Band | Close < Lower Band | ~1,187% Net Profit |
| **SuperTrend** | Trend turns Green | Trend turns Red | — |
| **Bull Market Support Band** | 20w SMA/EMA cross up | 20w SMA/EMA cross down | ~736% Net Profit |

Pre-generated strategy files are in [`strategies/output/`](strategies/output/).

## Quick Start

```bash
# Install
uv sync --dev

# List available strategies
uv run python -m meta_strategy.cli list

# Validate a strategy definition
uv run python -m meta_strategy.cli validate strategies/definitions/bollinger-bands.yml

# Generate a filled prompt for AI conversion
uv run python -m meta_strategy.cli generate strategies/definitions/bollinger-bands.yml

# Validate a Pine Script file for pitfalls
uv run python -m meta_strategy.cli validate-pine strategies/output/ai-bollinger-bands.pine
```

## How It Works

### The Meta-Strategy Workflow

```
Indicator Source Code + Entry/Exit Rules (YAML)
        ↓
  Prompt Template (prompt.md) filled by engine
        ↓
  AI produces Pine Script v6 strategy
        ↓
  Validator checks for common pitfalls
        ↓
  Ready-to-use .pine file for TradingView backtesting
```

### Adding a New Strategy

1. Save the indicator source to `strategies/indicators/your-indicator.pine`
2. Create a definition at `strategies/definitions/your-strategy.yml`:

```yaml
name: "Your Strategy"
indicator_source: "strategies/indicators/your-indicator.pine"
entry_condition: "describe when to go Long"
exit_condition: "describe when to close Long"
special_instructions:
  - "Any AI correction notes"
```

3. Generate the prompt: `uv run python -m meta_strategy.cli generate strategies/definitions/your-strategy.yml`
4. Use the prompt with an AI model to produce the strategy code
5. Validate: `uv run python -m meta_strategy.cli validate-pine output.pine`

## Common Pitfalls

The validator detects these issues automatically:

| Pitfall | Severity | Description |
|---------|----------|-------------|
| `lookahead_on` | 🔴 Critical | Produces false backtest results (future peeking) |
| Missing gap fill | 🟡 Warning | `request.security()` without `gaps=` causes staircase lines |
| Invalid variables | 🔴 Critical | `strategy.commission.percent` as variable doesn't exist |
| Wrong name prefix | ℹ️ Info | Strategy names should start with "AI - " |
| Line breaks in calls | 🟡 Warning | Pine Script doesn't support multi-line function calls |

## Development

```bash
uv run python -m pytest tests/ -v        # Run tests (27 tests)
uv run ruff check src/                    # Lint
uv run ruff format src/                   # Format
uv run mypy src/                          # Type check
```

## Project Structure

```
├── prompt.md                              # Pine Script conversion prompt template
├── input.md                               # Strategy research / video content summary
├── strategies/
│   ├── definitions/                       # YAML strategy definitions
│   │   ├── bollinger-bands.yml
│   │   ├── supertrend.yml
│   │   └── bull-market-support-band.yml
│   ├── indicators/                        # Raw indicator source code
│   │   ├── bollinger-bands.pine
│   │   ├── supertrend.pine
│   │   └── bull-market-support-band.pine
│   └── output/                            # Generated strategy files
│       ├── ai-bollinger-bands.pine
│       ├── ai-supertrend.pine
│       └── ai-bull-market-support-band.pine
├── src/meta_strategy/
│   ├── models.py                          # StrategyDefinition Pydantic model
│   ├── engine.py                          # Prompt template engine
│   ├── validator.py                       # Pine Script pitfall validator
│   └── cli.py                            # Typer CLI
└── tests/                                 # 27 tests
```

## License

MIT
