"""Pine Script syntax validator for common pitfalls.

Checks generated Pine Script strategies for issues documented in input.md
and prompt.md — lookahead, gap filling, line breaks, naming, etc.
"""

import re
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationWarning:
    """A validation finding in Pine Script code."""

    line_number: int
    severity: Severity
    rule: str
    message: str
    suggestion: str


def validate_pine_script(content: str) -> list[ValidationWarning]:
    """Validate Pine Script content for common pitfalls.

    Args:
        content: The Pine Script source code to validate

    Returns:
        List of validation warnings found
    """
    warnings: list[ValidationWarning] = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        warnings.extend(_check_lookahead(i, line))
        warnings.extend(_check_missing_gap_fill(i, line))
        warnings.extend(_check_invalid_variables(i, line))
        warnings.extend(_check_strategy_name_prefix(i, line))

    warnings.extend(_check_line_breaks_in_calls(lines))

    return warnings


def _check_lookahead(line_num: int, line: str) -> list[ValidationWarning]:
    """Detect lookahead_on usage — this is cheating in backtests."""
    if "lookahead_on" in line or "lookahead=barmerge.lookahead_on" in line:
        return [ValidationWarning(
            line_number=line_num,
            severity=Severity.CRITICAL,
            rule="no-lookahead",
            message="lookahead_on detected — this produces false backtest results",
            suggestion="Remove lookahead_on or use barmerge.lookahead_off",
        )]
    return []


def _check_missing_gap_fill(line_num: int, line: str) -> list[ValidationWarning]:
    """Detect request.security() calls without gap filling."""
    if "request.security(" in line and "gaps" not in line and "fillgaps" not in line.lower():
        return [ValidationWarning(
            line_number=line_num,
            severity=Severity.WARNING,
            rule="fill-gaps",
            message="request.security() without gap filling — may cause staircase lines",
            suggestion="Add gaps=barmerge.gaps_off or fillgaps=true",
        )]
    return []


def _check_invalid_variables(line_num: int, line: str) -> list[ValidationWarning]:
    """Detect Pine Script variables that don't exist."""
    warnings = []
    stripped = line.strip()
    # Skip comments
    if stripped.startswith("//"):
        return []
    # Only flag when used as standalone variables, not inside strategy() params
    if "strategy.commission.percent" in line and "commission_type" not in line:
        warnings.append(ValidationWarning(
            line_number=line_num,
            severity=Severity.CRITICAL,
            rule="invalid-variable",
            message="strategy.commission.percent used as variable — does not exist in Pine Script",
            suggestion="Set commission in the strategy() function: commission_type=strategy.commission.percent",
        ))
    if ("strategy.slippage" in line and "slippage" not in line.split("strategy.slippage")[0]
            and not re.search(r'strategy\s*\(.*strategy\.slippage', line)
            and (stripped.startswith("strategy.slippage") or "= strategy.slippage" in line)):
        warnings.append(ValidationWarning(
            line_number=line_num,
            severity=Severity.CRITICAL,
            rule="invalid-variable",
            message="strategy.slippage used as variable — does not exist in Pine Script",
            suggestion="Set slippage in the strategy() function: slippage=N",
        ))
    return warnings


def _check_strategy_name_prefix(line_num: int, line: str) -> list[ValidationWarning]:
    """Check strategy name starts with 'AI - '."""
    match = re.search(r'strategy\s*\(\s*"([^"]+)"', line)
    if match:
        name = match.group(1)
        if not name.startswith("AI - "):
            return [ValidationWarning(
                line_number=line_num,
                severity=Severity.INFO,
                rule="name-prefix",
                message=f'Strategy name "{name}" does not start with "AI - "',
                suggestion=f'Rename to "AI - {name}"',
            )]
    return []


def _check_line_breaks_in_calls(lines: list[str]) -> list[ValidationWarning]:
    """Detect line breaks inside function calls, IFs, loops, or variable definitions.

    Pine Script does not support multi-line expressions in most contexts.
    A heuristic: if a line ends with a comma, operator, or opening paren
    and the next non-empty line is not a new statement, it's likely a broken call.
    """
    warnings = []
    continuation_pattern = re.compile(r".*[,(+\-*/=]\s*$")

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip comments and empty lines
        if not stripped or stripped.startswith("//"):
            continue
        # Skip function/method definitions (they legitimately span lines)
        if stripped.endswith("=>"):
            continue
        # Check if line ends with continuation character
        if continuation_pattern.match(stripped):
            # Check next non-empty line
            for j in range(i + 1, min(i + 3, len(lines))):
                next_stripped = lines[j].strip()
                if not next_stripped or next_stripped.startswith("//"):
                    continue
                # If next line is indented and doesn't start a new statement, likely a broken call
                if lines[j].startswith(" ") or lines[j].startswith("\t"):
                    warnings.append(ValidationWarning(
                        line_number=i + 1,
                        severity=Severity.WARNING,
                        rule="no-line-breaks",
                        message="Possible line break in function call/expression — Pine Script may not support this",
                        suggestion="Put the entire expression on a single line",
                    ))
                break

    return warnings
