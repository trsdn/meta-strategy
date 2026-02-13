"""Tests for the prompt template engine."""

from pathlib import Path

import pytest

from meta_strategy.engine import render_prompt
from meta_strategy.models import StrategyDefinition


@pytest.fixture
def template_file(tmp_path):
    """Create a minimal prompt template."""
    template = tmp_path / "prompt.md"
    template.write_text(
        'You are a professional PineScript version=6 developer.\n'
        'Go Long when…\n'
        'Close Long when…\n'
        'strategy("NAME", overlay=true)\n'
        'This is the code of the Indicator:\n'
        '[YOUR STRATEGY CODE GOES HERE]\n'
    )
    return template


@pytest.fixture
def indicator_file(tmp_path):
    """Create a minimal indicator source."""
    ind = tmp_path / "indicators" / "test.pine"
    ind.parent.mkdir(parents=True)
    ind.write_text('//@version=5\nindicator("Test", overlay=true)\nplot(close)\n')
    return ind


@pytest.fixture
def definition(indicator_file):
    """Create a basic strategy definition."""
    return StrategyDefinition(
        name="Test Strategy",
        indicator_source=str(indicator_file),
        entry_condition="close is above the upper band",
        exit_condition="close is below the lower band",
    )


def test_basic_rendering(template_file, definition):
    """Prompt is correctly filled with entry/exit conditions and source."""
    result = render_prompt(definition, template_file)
    assert "Go Long when close is above the upper band" in result
    assert "Close Long when close is below the lower band" in result
    assert 'strategy("AI - Test Strategy"' in result
    assert '//@version=5' in result
    assert 'plot(close)' in result
    assert "[YOUR STRATEGY CODE GOES HERE]" not in result


def test_special_instructions(template_file, indicator_file):
    """Special instructions are appended to the prompt."""
    defn = StrategyDefinition(
        name="Test",
        indicator_source=str(indicator_file),
        entry_condition="buy signal",
        exit_condition="sell signal",
        special_instructions=["Fill gaps in security calls", "Verify logic is not inverted"],
    )
    result = render_prompt(defn, template_file)
    assert "Additional instructions:" in result
    assert "- Fill gaps in security calls" in result
    assert "- Verify logic is not inverted" in result


def test_missing_indicator_file(template_file, tmp_path):
    """FileNotFoundError raised when indicator source is missing."""
    defn = StrategyDefinition(
        name="Test",
        indicator_source=str(tmp_path / "nonexistent.pine"),
        entry_condition="buy",
        exit_condition="sell",
    )
    with pytest.raises(FileNotFoundError, match="Indicator source not found"):
        render_prompt(defn, template_file)


def test_missing_template():
    """FileNotFoundError raised when template is missing."""
    defn = StrategyDefinition(
        name="Test",
        indicator_source="test.pine",
        entry_condition="buy",
        exit_condition="sell",
    )
    with pytest.raises(FileNotFoundError, match="Template not found"):
        render_prompt(defn, Path("/nonexistent/prompt.md"))


def test_no_special_instructions(template_file, definition):
    """No 'Additional instructions' section when list is empty."""
    result = render_prompt(definition, template_file)
    assert "Additional instructions:" not in result
