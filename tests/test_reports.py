"""Tests for the reporting module."""

import json
import os
import tempfile

import pandas as pd

from meta_strategy.reports import (
    _svg_equity_chart,
    export_results_csv,
    export_results_json,
)


def test_svg_equity_chart_basic():
    """SVG chart renders with equity data."""
    equity = pd.Series([100_000, 110_000, 105_000, 120_000, 115_000])
    svg = _svg_equity_chart({"test": equity})
    assert "<svg" in svg
    assert "polyline" in svg
    assert "test" in svg


def test_svg_equity_chart_multiple():
    """SVG chart renders multiple curves."""
    eq1 = pd.Series([100, 110, 120])
    eq2 = pd.Series([100, 90, 95])
    svg = _svg_equity_chart({"strategy-a": eq1, "strategy-b": eq2})
    assert svg.count("polyline") == 2
    assert "strategy-a" in svg
    assert "strategy-b" in svg


def test_svg_equity_chart_empty():
    """SVG chart handles empty input."""
    svg = _svg_equity_chart({})
    assert svg == ""


def test_export_json():
    """Export results to JSON."""
    results = [
        {"strategy": "test", "return_pct": 50.0, "num_trades": 5},
    ]
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        export_results_json(results, path)
        with open(path) as f:
            loaded = json.loads(f.read())
        assert len(loaded) == 1
        assert loaded[0]["strategy"] == "test"
        assert loaded[0]["return_pct"] == 50.0
    finally:
        os.unlink(path)


def test_export_csv():
    """Export results to CSV."""
    results = [
        {"strategy": "a", "return_pct": 10.0, "num_trades": 3},
        {"strategy": "b", "return_pct": 20.0, "num_trades": 7},
    ]
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    try:
        export_results_csv(results, path)
        df = pd.read_csv(path)
        assert len(df) == 2
        assert list(df.columns) == ["strategy", "return_pct", "num_trades"]
    finally:
        os.unlink(path)


def test_export_csv_empty():
    """Export CSV handles empty results."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    try:
        export_results_csv([], path)
        # File should not have been written (or exist from temp)
    finally:
        os.unlink(path)
