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


@app.command(name="multi-asset")
def multi_asset_cmd(
    strategy_name: str = typer.Argument(..., help="Strategy name"),
    symbols: str = typer.Option("BTC-USD,ETH-USD,SPY,AAPL", help="Comma-separated symbols"),
    start: str = typer.Option("2018-01-01", help="Backtest start date"),
    cash: float = typer.Option(100_000.0, help="Initial capital"),
    commission: float = typer.Option(0.001, help="Commission rate"),
) -> None:
    """Run a strategy across multiple assets."""
    from .backtest import run_multi_asset

    symbol_list = [s.strip() for s in symbols.split(",")]
    typer.echo(f"📊 Running {strategy_name} across {len(symbol_list)} assets...\n")

    results = run_multi_asset(strategy_name, symbols=symbol_list, start=start, cash=cash, commission=commission)

    header = f"{'Symbol':<12} {'Return%':>10} {'B&H%':>10} {'WinRate%':>10} {'Trades':>8} {'MaxDD%':>10} {'Sharpe':>8}"
    sep = "-" * len(header)
    typer.echo(header)
    typer.echo(sep)
    for r in results:
        if "error" in r:
            typer.echo(f"{r['symbol']:<12} {'ERROR':>10}")
        else:
            typer.echo(f"{r['symbol']:<12} {r['return_pct']:>10.2f} {r['buy_hold_return_pct']:>10.2f} {r['win_rate_pct']:>10.2f} {r['num_trades']:>8d} {r['max_drawdown_pct']:>10.2f} {r['sharpe_ratio']:>8.2f}")
    typer.echo(sep)

    valid = [r for r in results if "error" not in r and r["num_trades"] > 0]
    if valid:
        best = max(valid, key=lambda r: r["sharpe_ratio"])
        typer.echo(f"\n🏆 Best Sharpe: {best['symbol']} ({best['sharpe_ratio']:.2f})")


@app.command()
def optimize(
    strategy_name: str = typer.Argument(..., help="Strategy name"),
    symbol: str = typer.Option("BTC-USD", help="Asset symbol"),
    start: str = typer.Option("2018-01-01", help="Start date"),
    top: int = typer.Option(10, help="Show top N results"),
    cash: float = typer.Option(100_000.0, help="Initial capital"),
    split: float = typer.Option(0.7, help="Train/test split ratio (0.7 = 70%% train). Use 1.0 for no split."),
) -> None:
    """Grid search parameter optimization with train/test split."""
    from .backtest import optimize_strategy, PARAM_GRIDS

    grid = PARAM_GRIDS.get(strategy_name, {})
    import itertools
    n_combos = 1
    for v in grid.values():
        n_combos *= len(v)

    has_split = split < 1.0
    split_label = f", {split:.0%} train" if has_split else ""
    typer.echo(f"🔍 Optimizing {strategy_name} on {symbol} ({n_combos} combinations{split_label})...\n")

    results = optimize_strategy(strategy_name, symbol=symbol, start=start, cash=cash, split=split)

    if has_split:
        header = f"{'Rank':<6} {'Params':<35} {'IS Ret%':>9} {'IS Sharpe':>10} {'OOS Ret%':>9} {'OOS Sharpe':>11} {'Trades':>8} {'MaxDD%':>8} {'WinR%':>8}"
        sep = "-" * len(header)
        typer.echo(header)
        typer.echo(sep)
        for i, r in enumerate(results[:top], 1):
            params_str = ", ".join(f"{k}={v}" for k, v in r["params"].items())
            typer.echo(f"{i:<6} {params_str:<35} {r['is_return_pct']:>9.2f} {r['is_sharpe_ratio']:>10.2f} {r['return_pct']:>9.2f} {r['sharpe_ratio']:>11.2f} {r['num_trades']:>8d} {r['max_drawdown_pct']:>8.2f} {r['win_rate_pct']:>8.2f}")
    else:
        header = f"{'Rank':<6} {'Params':<40} {'Return%':>10} {'Sharpe':>8} {'Trades':>8} {'MaxDD%':>10} {'WinRate%':>10}"
        sep = "-" * 92
        typer.echo(header)
        typer.echo(sep)
        for i, r in enumerate(results[:top], 1):
            params_str = ", ".join(f"{k}={v}" for k, v in r["params"].items())
            typer.echo(f"{i:<6} {params_str:<40} {r['return_pct']:>10.2f} {r['sharpe_ratio']:>8.2f} {r['num_trades']:>8d} {r['max_drawdown_pct']:>10.2f} {r['win_rate_pct']:>10.2f}")
    typer.echo(sep)

    if results:
        best = results[0]
        if has_split:
            typer.echo(f"\n🏆 Best params: {best['params']} (OOS Sharpe: {best['sharpe_ratio']:.2f}, IS Sharpe: {best['is_sharpe_ratio']:.2f})")
            from .backtest import check_overfitting
            warning = check_overfitting(best)
            if warning:
                ratio_str = f"{warning['ratio']:.1f}×" if warning["ratio"] != float("inf") else "∞×"
                typer.echo(f"\n⚠️  OVERFITTING WARNING: In-sample Sharpe ({warning['is_sharpe']:.2f}) is {ratio_str} out-of-sample Sharpe ({warning['oos_sharpe']:.2f}). Results may not generalize.")
        else:
            typer.echo(f"\n🏆 Best params: {best['params']} (Sharpe: {best['sharpe_ratio']:.2f}, Return: {best['return_pct']:.2f}%)")


@app.command(name="walk-forward")
def walk_forward_cmd(
    strategy_name: str = typer.Argument(..., help="Strategy name"),
    symbol: str = typer.Option("BTC-USD", help="Asset symbol"),
    start: str = typer.Option("2018-01-01", help="Start date"),
    splits: int = typer.Option(5, help="Number of walk-forward splits (sequential mode)"),
    train_pct: float = typer.Option(0.7, help="Training set percentage (sequential mode)"),
    cash: float = typer.Option(100_000.0, help="Initial capital"),
    mode: str = typer.Option("sequential", help="Windowing mode: sequential, rolling, or expanding"),
    train_bars: Optional[int] = typer.Option(None, help="Training window size in bars (rolling/expanding)"),
    step: Optional[int] = typer.Option(None, help="Step size in bars (rolling/expanding)"),
) -> None:
    """Walk-forward analysis with out-of-sample validation."""
    from .backtest import walk_forward

    if mode == "sequential":
        label = f"{splits} folds, {train_pct:.0%} train"
    else:
        tb = train_bars or 500
        st = step or 100
        label = f"{mode}, {tb} train bars, {st} step"
    typer.echo(f"🔄 Walk-forward analysis: {strategy_name} on {symbol} ({label})...\n")

    result = walk_forward(
        strategy_name, symbol=symbol, start=start, n_splits=splits,
        train_pct=train_pct, cash=cash, mode=mode, train_bars=train_bars, step=step,
    )

    for f in result["folds"]:
        params_str = ", ".join(f"{k}={v}" for k, v in f["best_params"].items()) if f["best_params"] else "default"
        typer.echo(f"  Fold {f['fold']}: train {f['train_period']} | test {f['test_period']}")
        typer.echo(f"          params: {params_str}")
        typer.echo(f"          train Sharpe: {f['train_sharpe']:.2f} → test Return: {f['test_return_pct']:.2f}%, Sharpe: {f['test_sharpe']:.2f}, Trades: {f['test_trades']}, MaxDD: {f['test_max_dd_pct']:.2f}%")
        typer.echo("")

    typer.echo(f"📊 Average out-of-sample: Return {result['avg_test_return_pct']:.2f}%, Sharpe {result['avg_test_sharpe']:.2f}")

    stability = result.get("param_stability", {})
    if stability and stability.get("params_per_fold"):
        typer.echo(f"\n📋 Parameter Stability: {stability['score_pct']:.0f}% stable")
        if stability["changes"]:
            typer.echo("   ⚠️  Unstable parameters (>50% change between consecutive folds):")
            for c in stability["changes"]:
                typer.echo(f"      {c['param']}: fold {c['fold_from']}→{c['fold_to']}: {c['prev']} → {c['curr']} ({c['pct_change']:.0f}% change)")
        else:
            typer.echo("   ✅ All parameters consistent across folds")


@app.command()
def report(
    strategy_name: str = typer.Argument(..., help="Strategy name"),
    symbol: str = typer.Option("BTC-USD", help="Asset symbol"),
    start: str = typer.Option("2018-01-01", help="Start date"),
    output: str = typer.Option("strategies/output/report.html", help="Output HTML path"),
    cash: float = typer.Option(100_000.0, help="Initial capital"),
) -> None:
    """Generate HTML report with equity curve for a strategy."""
    from .reports import generate_html_report

    typer.echo(f"📝 Generating report for {strategy_name} on {symbol}...")
    generate_html_report(strategy_name, symbol=symbol, start=start, cash=cash, output_path=output)
    typer.echo(f"✅ Report saved to {output}")


@app.command()
def dashboard(
    symbol: str = typer.Option("BTC-USD", help="Asset symbol"),
    start: str = typer.Option("2018-01-01", help="Start date"),
    output: str = typer.Option("strategies/output/dashboard.html", help="Output HTML path"),
    cash: float = typer.Option(100_000.0, help="Initial capital"),
) -> None:
    """Generate comparison dashboard for all strategies."""
    from .reports import generate_dashboard

    typer.echo(f"📊 Generating dashboard for all strategies on {symbol}...")
    generate_dashboard(symbol=symbol, start=start, cash=cash, output_path=output)
    typer.echo(f"✅ Dashboard saved to {output}")


@app.command()
def export(
    symbol: str = typer.Option("BTC-USD", help="Asset symbol"),
    start: str = typer.Option("2018-01-01", help="Start date"),
    fmt: str = typer.Option("json", help="Export format: json or csv"),
    output: str = typer.Option("strategies/output/results", help="Output path (without extension)"),
    cash: float = typer.Option(100_000.0, help="Initial capital"),
) -> None:
    """Export backtest results to CSV or JSON."""
    from .backtest import run_all_backtests
    from .reports import export_results_json, export_results_csv

    typer.echo(f"📦 Running all strategies and exporting as {fmt}...")
    results = run_all_backtests(symbol=symbol, start=start, cash=cash)

    if fmt == "json":
        path = f"{output}.json"
        export_results_json(results, path)
    elif fmt == "csv":
        path = f"{output}.csv"
        export_results_csv(results, path)
    else:
        typer.echo(f"❌ Unknown format: {fmt}. Use 'json' or 'csv'.", err=True)
        raise typer.Exit(1)

    typer.echo(f"✅ Results exported to {path}")


@app.command(name="monte-carlo")
def monte_carlo_cmd(
    strategy_name: str = typer.Argument(..., help="Strategy name"),
    symbol: str = typer.Option("BTC-USD", help="Asset symbol"),
    start: str = typer.Option("2018-01-01", help="Start date"),
    simulations: int = typer.Option(1000, help="Number of Monte Carlo simulations"),
    cash: float = typer.Option(100_000.0, help="Initial capital"),
) -> None:
    """Monte Carlo simulation for strategy robustness."""
    from .risk import monte_carlo

    typer.echo(f"🎲 Running {simulations} Monte Carlo simulations for {strategy_name} on {symbol}...\n")
    result = monte_carlo(strategy_name, symbol=symbol, start=start, cash=cash, n_simulations=simulations)

    if result["n_trades"] == 0:
        typer.echo("⚠️  No trades were generated — cannot run simulation.")
        return

    typer.echo(f"  Original Return:    {result['original_return_pct']:>10.2f}%")
    typer.echo(f"  Simulations:        {result['n_simulations']:>10d}")
    typer.echo(f"  Trades resampled:   {result['n_trades']:>10d}")
    typer.echo("")
    typer.echo(f"  5th percentile:     {result['p5_return_pct']:>10.2f}%  (worst case)")
    typer.echo(f"  Median:             {result['median_return_pct']:>10.2f}%")
    typer.echo(f"  95th percentile:    {result['p95_return_pct']:>10.2f}%  (best case)")
    typer.echo(f"  Mean:               {result['mean_return_pct']:>10.2f}%")
    typer.echo(f"  Std Dev:            {result['std_return_pct']:>10.2f}%")
    typer.echo(f"  P(Profit):          {result['prob_profit_pct']:>10.1f}%")


@app.command(name="risk-metrics")
def risk_metrics_cmd(
    strategy_name: str = typer.Argument(..., help="Strategy name"),
    symbol: str = typer.Option("BTC-USD", help="Asset symbol"),
    start: str = typer.Option("2018-01-01", help="Start date"),
    cash: float = typer.Option(100_000.0, help="Initial capital"),
) -> None:
    """Extended risk metrics (Sortino, Calmar, profit factor, etc.)."""
    from .risk import run_risk_analysis

    typer.echo(f"📊 Computing risk metrics for {strategy_name} on {symbol}...\n")
    m = run_risk_analysis(strategy_name, symbol=symbol, start=start, cash=cash)

    typer.echo(f"  Sharpe Ratio:           {m['sharpe_ratio']:>10.3f}")
    typer.echo(f"  Sortino Ratio:          {m['sortino_ratio']:>10.3f}")
    typer.echo(f"  Calmar Ratio:           {m['calmar_ratio']:>10.3f}")
    typer.echo(f"  Profit Factor:          {m['profit_factor']:>10.3f}")
    typer.echo(f"  Recovery Factor:        {m['recovery_factor']:>10.3f}")
    typer.echo(f"  Annual Return:          {m['annual_return_pct']:>10.2f}%")
    typer.echo(f"  Max Drawdown:           {m['max_drawdown_pct']:>10.2f}%")
    typer.echo(f"  Downside Deviation:     {m['downside_deviation']:>10.4f}")
    typer.echo(f"  Max Consecutive Losses: {m['max_consecutive_losses']:>10d}")
    typer.echo(f"  Max Consecutive Wins:   {m['max_consecutive_wins']:>10d}")
    typer.echo(f"  # Trades:               {m['num_trades']:>10d}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
