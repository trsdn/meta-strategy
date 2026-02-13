"""Tests for the CLI tool."""

from pathlib import Path

import yaml
from typer.testing import CliRunner

from meta_strategy.cli import app

runner = CliRunner()


def _write_definition(tmp_path: Path, name: str = "Test Strategy") -> Path:
    """Helper to write a valid YAML definition."""
    indicator = tmp_path / "indicators" / "test.pine"
    indicator.parent.mkdir(parents=True, exist_ok=True)
    indicator.write_text('//@version=5\nindicator("Test", overlay=true)\nplot(close)\n')

    defn = {
        "name": name,
        "indicator_source": str(indicator),
        "entry_condition": "close > upper",
        "exit_condition": "close < lower",
    }
    yaml_path = tmp_path / "test.yml"
    yaml_path.write_text(yaml.dump(defn))
    return yaml_path


def _write_template(tmp_path: Path) -> Path:
    """Helper to write a minimal prompt template."""
    template = tmp_path / "prompt.md"
    template.write_text(
        "You are a professional PineScript version=6 developer.\n"
        "Go Long when…\n"
        "Close Long when…\n"
        'strategy("NAME", overlay=true)\n'
        "[YOUR STRATEGY CODE GOES HERE]\n"
    )
    return template


def test_generate_happy_path(tmp_path):
    """Generate command produces filled prompt."""
    yaml_path = _write_definition(tmp_path)
    template = _write_template(tmp_path)

    result = runner.invoke(app, ["generate", str(yaml_path), "--template", str(template)])
    assert result.exit_code == 0
    assert "Go Long when close > upper" in result.stdout
    assert "AI - Test Strategy" in result.stdout


def test_validate_valid_yaml(tmp_path):
    """Validate command accepts valid YAML."""
    yaml_path = _write_definition(tmp_path)

    result = runner.invoke(app, ["validate", str(yaml_path)])
    assert result.exit_code == 0
    assert "✅ Valid" in result.stdout


def test_validate_invalid_yaml(tmp_path):
    """Validate command rejects invalid YAML."""
    bad_yaml = tmp_path / "bad.yml"
    bad_yaml.write_text(yaml.dump({"name": "Test"}))  # missing required fields

    result = runner.invoke(app, ["validate", str(bad_yaml)])
    assert result.exit_code == 1


def test_list_command(tmp_path):
    """List command shows strategy definitions."""
    defs_dir = tmp_path / "definitions"
    defs_dir.mkdir()

    for name in ["Strategy A", "Strategy B"]:
        defn = {
            "name": name,
            "indicator_source": "test.pine",
            "entry_condition": "buy",
            "exit_condition": "sell",
        }
        (defs_dir / f"{name.lower().replace(' ', '-')}.yml").write_text(yaml.dump(defn))

    result = runner.invoke(app, ["list", "--definitions-dir", str(defs_dir)])
    assert result.exit_code == 0
    assert "Strategy A" in result.stdout
    assert "Strategy B" in result.stdout


def test_validate_pine_clean(tmp_path):
    """validate-pine accepts clean script."""
    pine = tmp_path / "test.pine"
    pine.write_text('//@version=6\nstrategy("AI - Test", overlay=true)\nplot(close)\n')

    result = runner.invoke(app, ["validate-pine", str(pine)])
    assert result.exit_code == 0
    assert "No issues found" in result.stdout


def test_validate_pine_with_issues(tmp_path):
    """validate-pine detects lookahead_on."""
    pine = tmp_path / "bad.pine"
    pine.write_text('val = request.security(syminfo.tickerid, "D", close, lookahead=barmerge.lookahead_on)\n')

    result = runner.invoke(app, ["validate-pine", str(pine)])
    assert result.exit_code == 1
    assert "no-lookahead" in result.stdout
