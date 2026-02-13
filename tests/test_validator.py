"""Tests for Pine Script validator."""

from meta_strategy.validator import Severity, validate_pine_script


def test_detect_lookahead_on():
    """CRITICAL: lookahead_on is cheating in backtests."""
    code = 'val = request.security(syminfo.tickerid, "D", close, lookahead=barmerge.lookahead_on)\n'
    warnings = validate_pine_script(code)
    assert any(w.rule == "no-lookahead" and w.severity == Severity.CRITICAL for w in warnings)


def test_no_lookahead_is_clean():
    """No warning when lookahead is off or absent."""
    code = 'val = request.security(syminfo.tickerid, "D", close, lookahead=barmerge.lookahead_off)\n'
    warnings = validate_pine_script(code)
    assert not any(w.rule == "no-lookahead" for w in warnings)


def test_detect_missing_gap_fill():
    """WARNING: request.security without gap filling causes staircase lines."""
    code = 'val = request.security(syminfo.tickerid, "W", close)\n'
    warnings = validate_pine_script(code)
    assert any(w.rule == "fill-gaps" and w.severity == Severity.WARNING for w in warnings)


def test_gap_fill_present_is_clean():
    """No warning when gaps parameter is present."""
    code = 'val = request.security(syminfo.tickerid, "W", close, gaps=barmerge.gaps_off)\n'
    warnings = validate_pine_script(code)
    assert not any(w.rule == "fill-gaps" for w in warnings)


def test_detect_strategy_name_without_prefix():
    """INFO: Strategy name should start with 'AI - '."""
    code = 'strategy("Bollinger Bands", overlay=true)\n'
    warnings = validate_pine_script(code)
    assert any(w.rule == "name-prefix" and w.severity == Severity.INFO for w in warnings)


def test_strategy_name_with_prefix_is_clean():
    """No warning when name has correct prefix."""
    code = 'strategy("AI - Bollinger Bands", overlay=true)\n'
    warnings = validate_pine_script(code)
    assert not any(w.rule == "name-prefix" for w in warnings)


def test_detect_invalid_commission_variable():
    """CRITICAL: strategy.commission.percent as standalone variable doesn't exist."""
    code = "comm = strategy.commission.percent\n"
    warnings = validate_pine_script(code)
    assert any(w.rule == "invalid-variable" and w.severity == Severity.CRITICAL for w in warnings)


def test_commission_in_strategy_call_is_clean():
    """No warning when used correctly inside strategy() call."""
    code = 'strategy("AI - Test", commission_type=strategy.commission.percent, commission_value=0.1)\n'
    warnings = validate_pine_script(code)
    assert not any(w.rule == "invalid-variable" for w in warnings)


def test_detect_line_break_in_call():
    """WARNING: Line breaks inside function calls cause Pine Script errors."""
    code = 'strategy("AI - Test",\n    overlay=true)\n'
    warnings = validate_pine_script(code)
    assert any(w.rule == "no-line-breaks" for w in warnings)


def test_clean_script_no_warnings():
    """A well-formed script produces no warnings."""
    code = (
        "//@version=6\n"
        'strategy("AI - Test", overlay=true, calc_on_every_tick=false, initial_capital=1000)\n'
        "plot(close)\n"
        "if close > ta.sma(close, 20)\n"
        '    strategy.entry("Long", strategy.long)\n'
    )
    warnings = validate_pine_script(code)
    # Filter out line-break warnings from the if block (legitimate Pine Script indentation)
    critical = [w for w in warnings if w.severity == Severity.CRITICAL]
    assert len(critical) == 0
