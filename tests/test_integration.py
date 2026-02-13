"""Integration tests: YAML → generate → validate round-trip.

Tests the core pipeline with actual strategy definitions and prompt template.
"""

from pathlib import Path

import pytest

from meta_strategy.engine import render_prompt
from meta_strategy.models import StrategyDefinition
from meta_strategy.validator import validate_pine_script

REPO_ROOT = Path(__file__).parent.parent
DEFINITIONS_DIR = REPO_ROOT / "strategies" / "definitions"
TEMPLATE_PATH = REPO_ROOT / "prompt.md"

STRATEGY_YAMLS = [
    "bollinger-bands.yml",
    "supertrend.yml",
    "bull-market-support-band.yml",
    "rsi.yml",
    "macd.yml",
    "confluence.yml",
]


@pytest.mark.parametrize("yaml_file", STRATEGY_YAMLS)
def test_yaml_loads_as_valid_definition(yaml_file: str) -> None:
    """Each YAML file parses into a valid StrategyDefinition."""
    import yaml

    path = DEFINITIONS_DIR / yaml_file
    assert path.exists(), f"Missing definition: {path}"
    with open(path) as f:
        data = yaml.safe_load(f)
    defn = StrategyDefinition(**data)
    assert defn.name
    assert defn.entry_condition
    assert defn.exit_condition
    assert defn.indicator_source


@pytest.mark.parametrize("yaml_file", STRATEGY_YAMLS)
def test_indicator_source_exists(yaml_file: str) -> None:
    """Each YAML's indicator_source points to an existing file."""
    import yaml

    path = DEFINITIONS_DIR / yaml_file
    with open(path) as f:
        data = yaml.safe_load(f)
    defn = StrategyDefinition(**data)
    indicator_path = defn.resolve_indicator_path(REPO_ROOT)
    assert indicator_path.exists(), f"Missing indicator: {indicator_path}"


@pytest.mark.parametrize("yaml_file", STRATEGY_YAMLS)
def test_generate_produces_valid_prompt(yaml_file: str) -> None:
    """generate renders a prompt with entry/exit conditions and indicator source."""
    import yaml

    path = DEFINITIONS_DIR / yaml_file
    with open(path) as f:
        data = yaml.safe_load(f)
    defn = StrategyDefinition(**data)

    if not TEMPLATE_PATH.exists():
        pytest.skip("prompt.md not found at repo root")

    result = render_prompt(defn, TEMPLATE_PATH, base_dir=REPO_ROOT)

    # Prompt should contain the entry/exit conditions
    assert defn.entry_condition in result
    assert defn.exit_condition in result
    # Strategy name should be prefixed
    assert f"AI - {defn.name}" in result
    # Placeholder should be replaced
    assert "[YOUR STRATEGY CODE GOES HERE]" not in result
    # Should contain indicator source code
    assert "//@version=5" in result


@pytest.mark.parametrize("yaml_file", STRATEGY_YAMLS)
def test_generated_prompt_passes_validation(yaml_file: str) -> None:
    """Generated prompt files have no unexpected critical issues beyond template patterns."""
    import yaml

    path = DEFINITIONS_DIR / yaml_file
    with open(path) as f:
        data = yaml.safe_load(f)
    defn = StrategyDefinition(**data)

    if not TEMPLATE_PATH.exists():
        pytest.skip("prompt.md not found at repo root")

    result = render_prompt(defn, TEMPLATE_PATH, base_dir=REPO_ROOT)
    issues = validate_pine_script(result)

    # The template intentionally contains lookahead_on and strategy.commission.percent
    # as negative examples/instructions. Filter those out.
    unexpected = [
        i
        for i in issues
        if i.severity.value == "critical" and "lookahead" not in i.rule and "invalid-variable" not in i.rule
    ]
    assert len(unexpected) == 0, f"Unexpected critical issues: {unexpected}"
