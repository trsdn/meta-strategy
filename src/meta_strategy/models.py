"""Strategy definition models for meta-strategy."""

from pathlib import Path

from pydantic import BaseModel, Field


class StrategyDefinition(BaseModel):
    """YAML-driven strategy definition per ADR-002.

    Each definition captures everything needed to generate a Pine Script
    strategy from an indicator: source code reference, entry/exit logic,
    and any special instructions for the AI conversion.
    """

    name: str = Field(description="Strategy name (will be prefixed with 'AI - ')")
    indicator_source: str = Field(description="Path to Pine Script indicator source file")
    entry_condition: str = Field(description="When to go Long (natural language)")
    exit_condition: str = Field(description="When to close Long (natural language)")
    special_instructions: list[str] = Field(default_factory=list, description="Additional instructions for the AI conversion")
    strategy_params: dict[str, str | int | float | bool] = Field(default_factory=dict, description="Override default strategy parameters")

    def resolve_indicator_path(self, base_dir: Path | None = None) -> Path:
        """Resolve the indicator source path relative to base_dir."""
        path = Path(self.indicator_source)
        if base_dir and not path.is_absolute():
            path = base_dir / path
        return path
