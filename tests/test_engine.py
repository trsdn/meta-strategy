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
        "You are a professional PineScript version=6 developer.\n"
        "Go Long when…\n"
        "Close Long when…\n"
        'strategy("NAME", overlay=true)\n'
        "This is the code of the Indicator:\n"
        "[YOUR STRATEGY CODE GOES HERE]\n"
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
    assert "//@version=5" in result
    assert "plot(close)" in result
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


def test_strategy_params_field(indicator_file):
    """strategy_params field stores override parameters."""
    defn = StrategyDefinition(
        name="Params Test",
        indicator_source=str(indicator_file),
        entry_condition="buy",
        exit_condition="sell",
        strategy_params={"length": 30, "mult": 2.5, "use_ema": True},
    )
    assert defn.strategy_params["length"] == 30
    assert defn.strategy_params["mult"] == 2.5
    assert defn.strategy_params["use_ema"] is True


def test_strategy_params_default_empty(definition):
    """strategy_params defaults to empty dict."""
    assert definition.strategy_params == {}


def test_resolve_indicator_path_absolute(tmp_path):
    """Absolute indicator path is returned unchanged regardless of base_dir."""
    abs_path = tmp_path / "indicators" / "test.pine"
    defn = StrategyDefinition(
        name="Test",
        indicator_source=str(abs_path),
        entry_condition="buy",
        exit_condition="sell",
    )
    resolved = defn.resolve_indicator_path(base_dir=Path("/some/other/dir"))
    assert resolved == abs_path


def test_resolve_indicator_path_with_base_dir(tmp_path):
    """Relative indicator path is resolved against base_dir."""
    defn = StrategyDefinition(
        name="Test",
        indicator_source="indicators/test.pine",
        entry_condition="buy",
        exit_condition="sell",
    )
    resolved = defn.resolve_indicator_path(base_dir=tmp_path)
    assert resolved == tmp_path / "indicators" / "test.pine"


def test_resolve_indicator_path_no_base_dir():
    """Relative path without base_dir stays relative."""
    defn = StrategyDefinition(
        name="Test",
        indicator_source="indicators/test.pine",
        entry_condition="buy",
        exit_condition="sell",
    )
    resolved = defn.resolve_indicator_path(base_dir=None)
    assert resolved == Path("indicators/test.pine")


def test_render_with_base_dir(tmp_path):
    """render_prompt resolves indicator path via base_dir."""
    # Set up indicator at base_dir/indicators/test.pine
    ind = tmp_path / "indicators" / "test.pine"
    ind.parent.mkdir(parents=True)
    ind.write_text('//@version=5\nindicator("Test")\nplot(close)\n')

    # Template in a different directory
    template = tmp_path / "templates" / "prompt.md"
    template.parent.mkdir()
    template.write_text(
        "You are a professional PineScript version=6 developer.\n"
        "Go Long when…\nClose Long when…\n"
        'strategy("NAME", overlay=true)\n[YOUR STRATEGY CODE GOES HERE]\n'
    )

    defn = StrategyDefinition(
        name="Base Dir Test",
        indicator_source="indicators/test.pine",
        entry_condition="buy",
        exit_condition="sell",
    )
    result = render_prompt(defn, template, base_dir=tmp_path)
    assert "plot(close)" in result
    assert 'AI - Base Dir Test' in result


def test_empty_indicator_file(tmp_path):
    """Engine handles empty indicator source file."""
    ind = tmp_path / "empty.pine"
    ind.write_text("")

    template = tmp_path / "prompt.md"
    template.write_text(
        "Go Long when…\nClose Long when…\n"
        'strategy("NAME")\n[YOUR STRATEGY CODE GOES HERE]\n'
    )

    defn = StrategyDefinition(
        name="Empty",
        indicator_source=str(ind),
        entry_condition="buy",
        exit_condition="sell",
    )
    result = render_prompt(defn, template)
    assert "[YOUR STRATEGY CODE GOES HERE]" not in result
    assert "Go Long when buy" in result


def test_unicode_content(tmp_path):
    """Engine handles unicode in indicator and definition."""
    ind = tmp_path / "unicode.pine"
    ind.write_text('//@version=5\n// Ünïcödé cömmënt ñ\nplot(close)\n')

    template = tmp_path / "prompt.md"
    template.write_text(
        "Go Long when…\nClose Long when…\n"
        'strategy("NAME")\n[YOUR STRATEGY CODE GOES HERE]\n'
    )

    defn = StrategyDefinition(
        name="Ünïcödé Strategy",
        indicator_source=str(ind),
        entry_condition="Preis über Widerstand",
        exit_condition="Preis unter Unterstützung",
    )
    result = render_prompt(defn, template)
    assert "Ünïcödé" in result
    assert "Preis über Widerstand" in result


def test_template_without_placeholders(tmp_path, indicator_file):
    """Template missing expected placeholders returns template mostly unchanged."""
    template = tmp_path / "plain.md"
    template.write_text("This template has no standard placeholders.\n")

    defn = StrategyDefinition(
        name="Test",
        indicator_source=str(indicator_file),
        entry_condition="buy",
        exit_condition="sell",
    )
    result = render_prompt(defn, template)
    assert "This template has no standard placeholders." in result
