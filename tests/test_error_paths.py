"""Tests for error paths: malformed YAML, empty data, CLI edge cases."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
import yaml
from typer.testing import CliRunner

from meta_strategy.cli import app

runner = CliRunner()


# === Malformed YAML tests ===


def test_validate_malformed_yaml_syntax(tmp_path: Path) -> None:
    """Validate command handles YAML syntax errors gracefully."""
    bad = tmp_path / "bad.yml"
    bad.write_text("name: [unterminated")
    result = runner.invoke(app, ["validate", str(bad)])
    assert result.exit_code == 1


def test_validate_yaml_wrong_types(tmp_path: Path) -> None:
    """Validate rejects YAML where fields have wrong types."""
    bad = tmp_path / "bad.yml"
    bad.write_text(yaml.dump({"name": 123, "entry_condition": True}))
    result = runner.invoke(app, ["validate", str(bad)])
    assert result.exit_code == 1


def test_validate_yaml_empty_file(tmp_path: Path) -> None:
    """Validate handles empty YAML file."""
    empty = tmp_path / "empty.yml"
    empty.write_text("")
    result = runner.invoke(app, ["validate", str(empty)])
    assert result.exit_code == 1


# === CLI list command error paths ===


def test_list_missing_definitions_dir(tmp_path: Path) -> None:
    """List command handles non-existent definitions directory."""
    result = runner.invoke(app, ["list", "--definitions-dir", str(tmp_path / "nonexistent")])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_list_with_malformed_yaml(tmp_path: Path) -> None:
    """List command shows error for malformed YAML but continues."""
    defs_dir = tmp_path / "definitions"
    defs_dir.mkdir()
    (defs_dir / "good.yml").write_text(
        yaml.dump(
            {
                "name": "Good Strategy",
                "indicator_source": "test.pine",
                "entry_condition": "buy",
                "exit_condition": "sell",
            }
        )
    )
    (defs_dir / "bad.yml").write_text("name: [broken")
    result = runner.invoke(app, ["list", "--definitions-dir", str(defs_dir)])
    assert result.exit_code == 0
    assert "❌" in result.stdout
    assert "Good Strategy" in result.stdout


# === CLI validate-pine error paths ===


def test_validate_pine_nonexistent_file() -> None:
    """validate-pine handles missing file."""
    result = runner.invoke(app, ["validate-pine", "/nonexistent/file.pine"])
    assert result.exit_code != 0


# === fetch_data error paths ===


def test_fetch_data_invalid_interval() -> None:
    """fetch_data raises ValueError for unsupported intervals."""
    from meta_strategy.backtest import fetch_data

    with pytest.raises(ValueError, match="Unsupported interval"):
        fetch_data("BTC-USD", interval="2h")


def test_fetch_data_empty_dataframe() -> None:
    """fetch_data with mocked empty response returns empty DataFrame."""
    from meta_strategy.backtest import fetch_data

    with patch("meta_strategy.backtest.fetch_data") as mock_fetch:
        mock_fetch.return_value = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
        result = mock_fetch("INVALID-SYMBOL-XYZ")
        assert result.empty


# === generate command error paths ===


def test_generate_missing_yaml_file() -> None:
    """Generate command fails with missing YAML file."""
    result = runner.invoke(app, ["generate", "/nonexistent/file.yml"])
    assert result.exit_code != 0


def test_generate_missing_template(tmp_path: Path) -> None:
    """Generate command fails with missing template."""
    yaml_path = tmp_path / "test.yml"
    yaml_path.write_text(
        yaml.dump(
            {
                "name": "Test",
                "indicator_source": "test.pine",
                "entry_condition": "buy",
                "exit_condition": "sell",
            }
        )
    )
    result = runner.invoke(app, ["generate", str(yaml_path), "--template", "/nonexistent/prompt.md"])
    assert result.exit_code != 0
