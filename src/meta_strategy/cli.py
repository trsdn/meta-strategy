"""Meta Strategy CLI — TradingView indicator-to-strategy converter."""

from pathlib import Path
from typing import Optional

import typer
import yaml

from .engine import render_prompt
from .models import StrategyDefinition
from .validator import Severity, validate_pine_script

app = typer.Typer(
    name="meta-strategy",
    help="AI-powered TradingView indicator-to-strategy converter",
)


@app.command()
def generate(
    definition_path: Path = typer.Argument(..., help="Path to YAML strategy definition"),
    template: Path = typer.Option(Path("prompt.md"), help="Path to prompt template"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file (default: stdout)"),
    base_dir: Path = typer.Option(Path("."), help="Base directory for resolving relative paths"),
) -> None:
    """Generate a filled prompt from a strategy definition."""
    if not definition_path.exists():
        typer.echo(f"Error: Definition file not found: {definition_path}", err=True)
        raise typer.Exit(1)

    data = yaml.safe_load(definition_path.read_text())
    defn = StrategyDefinition(**data)
    result = render_prompt(defn, template, base_dir)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result)
        typer.echo(f"Prompt written to {output}")
    else:
        typer.echo(result)


@app.command()
def validate(
    definition_path: Path = typer.Argument(..., help="Path to YAML strategy definition"),
) -> None:
    """Validate a strategy definition YAML against the schema."""
    if not definition_path.exists():
        typer.echo(f"Error: File not found: {definition_path}", err=True)
        raise typer.Exit(1)

    try:
        data = yaml.safe_load(definition_path.read_text())
        defn = StrategyDefinition(**data)
        typer.echo(f"✅ Valid: {defn.name}")
        typer.echo(f"   Entry: {defn.entry_condition}")
        typer.echo(f"   Exit: {defn.exit_condition}")
        typer.echo(f"   Special instructions: {len(defn.special_instructions)}")
    except Exception as e:
        typer.echo(f"❌ Invalid: {e}", err=True)
        raise typer.Exit(1)


@app.command(name="validate-pine")
def validate_pine(
    pine_path: Path = typer.Argument(..., help="Path to Pine Script file"),
) -> None:
    """Validate a Pine Script file for common pitfalls."""
    if not pine_path.exists():
        typer.echo(f"Error: File not found: {pine_path}", err=True)
        raise typer.Exit(1)

    content = pine_path.read_text()
    warnings = validate_pine_script(content)

    if not warnings:
        typer.echo(f"✅ No issues found in {pine_path}")
        return

    for w in warnings:
        icon = "🔴" if w.severity == Severity.CRITICAL else "🟡" if w.severity == Severity.WARNING else "ℹ️"
        typer.echo(f"{icon} Line {w.line_number}: [{w.rule}] {w.message}")
        typer.echo(f"   💡 {w.suggestion}")

    critical_count = sum(1 for w in warnings if w.severity == Severity.CRITICAL)
    if critical_count > 0:
        typer.echo(f"\n❌ {critical_count} critical issue(s) found")
        raise typer.Exit(1)


@app.command(name="list")
def list_definitions(
    definitions_dir: Path = typer.Option(Path("strategies/definitions"), help="Directory with YAML definitions"),
) -> None:
    """List all strategy definitions."""
    if not definitions_dir.exists():
        typer.echo(f"Error: Directory not found: {definitions_dir}", err=True)
        raise typer.Exit(1)

    yamls = sorted(definitions_dir.glob("*.yml")) + sorted(definitions_dir.glob("*.yaml"))
    if not yamls:
        typer.echo("No strategy definitions found.")
        return

    for path in yamls:
        try:
            data = yaml.safe_load(path.read_text())
            defn = StrategyDefinition(**data)
            typer.echo(f"  📊 {defn.name:30s} ({path.name})")
        except Exception as e:
            typer.echo(f"  ❌ {path.name}: {e}")


@app.command()
def backtest(
    strategy_name: str = typer.Argument(..., help="Strategy name: bollinger-bands, supertrend, bull-market-support-band"),
    symbol: str = typer.Option("BTC-USD", help="Asset symbol (yfinance format)"),
    start: str = typer.Option("2018-01-01", help="Backtest start date"),
    end: Optional[str] = typer.Option(None, help="Backtest end date (default: today)"),
    cash: float = typer.Option(100_000.0, help="Initial capital"),
    commission: float = typer.Option(0.001, help="Commission rate (0.001 = 0.1%)"),
) -> None:
    """Run a backtest for a single strategy."""
    from .backtest import STRATEGIES, run_backtest

    if strategy_name not in STRATEGIES:
        typer.echo(f"❌ Unknown strategy: {strategy_name}", err=True)
        typer.echo(f"   Available: {', '.join(STRATEGIES.keys())}", err=True)
        raise typer.Exit(1)

    typer.echo(f"📊 Running {strategy_name} on {symbol} ({start} → {end or 'today'})...")
    result = run_backtest(strategy_name, symbol=symbol, start=start, end=end, cash=cash, commission=commission)

    typer.echo(f"\n{'='*60}")
    typer.echo(f"  Strategy:        {result['strategy']}")
    typer.echo(f"  Symbol:          {result['symbol']}")
    typer.echo(f"  Period:          {result['period']}")
    typer.echo(f"  Return:          {result['return_pct']:>10.2f}%")
    typer.echo(f"  Buy & Hold:      {result['buy_hold_return_pct']:>10.2f}%")
    typer.echo(f"  Win Rate:        {result['win_rate_pct']:>10.2f}%")
    typer.echo(f"  # Trades:        {result['num_trades']:>10d}")
    typer.echo(f"  Max Drawdown:    {result['max_drawdown_pct']:>10.2f}%")
    typer.echo(f"  Sharpe Ratio:    {result['sharpe_ratio']:>10.2f}")
    typer.echo(f"  Final Equity:    ${result['final_equity']:>10.2f}")
    typer.echo(f"{'='*60}")


@app.command(name="backtest-all")
def backtest_all(
    symbol: str = typer.Option("BTC-USD", help="Asset symbol"),
    start: str = typer.Option("2018-01-01", help="Backtest start date"),
    end: Optional[str] = typer.Option(None, help="Backtest end date"),
    cash: float = typer.Option(100_000.0, help="Initial capital"),
    commission: float = typer.Option(0.001, help="Commission rate"),
    save: bool = typer.Option(False, help="Save results to strategies/output/backtest-results.md"),
) -> None:
    """Run all strategies and show comparison table."""
    from .backtest import run_all_backtests

    typer.echo(f"📊 Running all strategies on {symbol} ({start} → {end or 'today'})...\n")
    results = run_all_backtests(symbol=symbol, start=start, end=end, cash=cash, commission=commission)

    # Print comparison table
    header = f"{'Strategy':<28} {'Return%':>10} {'B&H%':>10} {'WinRate%':>10} {'Trades':>8} {'MaxDD%':>10} {'Sharpe':>8} {'Equity$':>12}"
    sep = "-" * len(header)
    typer.echo(header)
    typer.echo(sep)
    for r in results:
        typer.echo(f"{r['strategy']:<28} {r['return_pct']:>10.2f} {r['buy_hold_return_pct']:>10.2f} {r['win_rate_pct']:>10.2f} {r['num_trades']:>8d} {r['max_drawdown_pct']:>10.2f} {r['sharpe_ratio']:>8.2f} {r['final_equity']:>12.2f}")
    typer.echo(sep)

    # Best performer
    best = max(results, key=lambda r: r["return_pct"])
    typer.echo(f"\n🏆 Best performer: {best['strategy']} ({best['return_pct']:.2f}%)")

    if save:
        _save_results_markdown(results, symbol)
        typer.echo(f"📄 Results saved to strategies/output/backtest-results.md")


def _save_results_markdown(results: list[dict], symbol: str) -> None:
    """Save backtest results as markdown."""
    output_path = Path("strategies/output/backtest-results.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Backtest Results — {symbol}\n",
        f"Generated by meta-strategy local backtesting engine.\n",
        "",
        "| Strategy | Return % | Buy & Hold % | Win Rate % | Trades | Max DD % | Sharpe | Final Equity |",
        "|----------|----------|-------------|-----------|--------|---------|--------|-------------|",
    ]
    for r in results:
        lines.append(f"| {r['strategy']} | {r['return_pct']:.2f} | {r['buy_hold_return_pct']:.2f} | {r['win_rate_pct']:.2f} | {r['num_trades']} | {r['max_drawdown_pct']:.2f} | {r['sharpe_ratio']:.2f} | ${r['final_equity']:.2f} |")

    best = max(results, key=lambda r: r["return_pct"])
    lines.extend(["", f"**🏆 Best performer: {best['strategy']}** ({best['return_pct']:.2f}%)", ""])

    output_path.write_text("\n".join(lines))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
