"""Meta Strategy CLI — TradingView indicator-to-strategy converter."""

from pathlib import Path

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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
