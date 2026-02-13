"""Prompt template engine for meta-strategy.

Takes a prompt template (prompt.md) and a StrategyDefinition,
produces a filled prompt ready for AI consumption.
"""

from pathlib import Path

from .models import StrategyDefinition


def render_prompt(definition: StrategyDefinition, template_path: str | Path, base_dir: Path | None = None) -> str:
    """Render a filled prompt from a template and strategy definition.

    Args:
        definition: The strategy definition with entry/exit logic
        template_path: Path to the prompt template (prompt.md)
        base_dir: Base directory for resolving relative indicator paths

    Returns:
        Filled prompt string ready for AI consumption

    Raises:
        FileNotFoundError: If template or indicator source file not found
    """
    template_path = Path(template_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    template = template_path.read_text()

    indicator_path = definition.resolve_indicator_path(base_dir)
    if not indicator_path.exists():
        raise FileNotFoundError(f"Indicator source not found: {indicator_path}")

    indicator_source = indicator_path.read_text()

    # Fill entry/exit conditions
    result = template.replace("Go Long when…", f"Go Long when {definition.entry_condition}")
    result = result.replace("Close Long when…", f"Close Long when {definition.exit_condition}")

    # Replace strategy name in the strategy() call
    result = result.replace('strategy("NAME"', f'strategy("AI - {definition.name}"')

    # Replace indicator source code placeholder
    result = result.replace("[YOUR STRATEGY CODE GOES HERE]", indicator_source)

    # Append special instructions if any
    if definition.special_instructions:
        instructions_text = "\n".join(f"- {instr}" for instr in definition.special_instructions)
        result = result.rstrip() + "\n\nAdditional instructions:\n" + instructions_text + "\n"

    return result
