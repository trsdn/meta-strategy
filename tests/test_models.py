"""Tests for StrategyDefinition model."""

from pathlib import Path

import pytest
import yaml

from meta_strategy.models import StrategyDefinition


def test_valid_definition():
    """Valid YAML creates a StrategyDefinition."""
    data = {
        "name": "Test Strategy",
        "indicator_source": "indicators/test.pine",
        "entry_condition": "close > upper",
        "exit_condition": "close < lower",
    }
    defn = StrategyDefinition(**data)
    assert defn.name == "Test Strategy"
    assert defn.entry_condition == "close > upper"
    assert defn.exit_condition == "close < lower"
    assert defn.special_instructions == []
    assert defn.strategy_params == {}


def test_missing_required_field():
    """Missing required field raises ValidationError."""
    data = {
        "name": "Test Strategy",
        # missing indicator_source, entry_condition, exit_condition
    }
    with pytest.raises(Exception):
        StrategyDefinition(**data)


def test_default_values():
    """Optional fields have sensible defaults."""
    data = {
        "name": "Test",
        "indicator_source": "test.pine",
        "entry_condition": "buy",
        "exit_condition": "sell",
    }
    defn = StrategyDefinition(**data)
    assert defn.special_instructions == []
    assert defn.strategy_params == {}


def test_special_instructions():
    """Special instructions are preserved."""
    data = {
        "name": "Test",
        "indicator_source": "test.pine",
        "entry_condition": "buy",
        "exit_condition": "sell",
        "special_instructions": ["Fill gaps", "Invert logic check"],
    }
    defn = StrategyDefinition(**data)
    assert len(defn.special_instructions) == 2
    assert "Fill gaps" in defn.special_instructions


def test_resolve_indicator_path_relative(tmp_path):
    """Indicator path resolves relative to base_dir."""
    defn = StrategyDefinition(
        name="Test",
        indicator_source="indicators/test.pine",
        entry_condition="buy",
        exit_condition="sell",
    )
    resolved = defn.resolve_indicator_path(tmp_path)
    assert resolved == tmp_path / "indicators" / "test.pine"


def test_yaml_roundtrip(tmp_path):
    """YAML file loads into valid StrategyDefinition."""
    yaml_content = {
        "name": "Bollinger Bands",
        "indicator_source": "strategies/indicators/bollinger-bands.pine",
        "entry_condition": "close > upper band",
        "exit_condition": "close < lower band",
        "special_instructions": ["Buy on breakout, not reversion"],
    }
    yaml_path = tmp_path / "test.yml"
    yaml_path.write_text(yaml.dump(yaml_content))

    loaded = yaml.safe_load(yaml_path.read_text())
    defn = StrategyDefinition(**loaded)
    assert defn.name == "Bollinger Bands"
    assert len(defn.special_instructions) == 1
