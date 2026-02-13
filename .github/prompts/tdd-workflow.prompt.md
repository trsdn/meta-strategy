---
name: TDD Workflow
description: Test-Driven Development with Red-Green-Refactor cycle
---

# TDD Workflow

Write failing tests first, then implement code to make them pass.

> **When to use**: RECOMMENDED for all feature issues. REQUIRED when the issue has Given/When/Then acceptance criteria. The acceptance criteria on the issue ARE your test specifications.

## When to Use

- Implementing a user story with acceptance criteria
- Building new features with clear requirements
- Refactoring with safety net

## When NOT to Use

- Exploratory prototyping
- UI/visual changes
- One-off scripts
- Documentation changes

## The TDD Cycle

```
┌─────────────────────────────────────────────┐
│  1. RED    │  Write a failing test          │
├─────────────────────────────────────────────┤
│  2. GREEN  │  Write minimal code to pass    │
├─────────────────────────────────────────────┤
│  3. REFACTOR │  Improve code, keep tests green │
└─────────────────────────────────────────────┘
         ↑                                    │
         └────────────────────────────────────┘
```

## Workflow Steps

### Step 1: Parse Acceptance Criteria

Convert each Given/When/Then into a test case.

### Step 2: Write Test File First

Create test file before implementation.

| Language | Pattern | Example |
|----------|---------|---------|
| Python | `test_<module>.py` | `test_logout.py` |
| JavaScript | `<module>.test.js` | `logout.test.js` |
| TypeScript | `<module>.spec.ts` | `logout.spec.ts` |
| Go | `<module>_test.go` | `logout_test.go` |

### Step 3: Run Test (Expect Failure)

```bash
uv run pytest tests/path/test_module.py -v
```

**Expected output:** RED (failing test)

### Step 4: Implement Minimum Code

Write just enough to make the test pass.

### Step 5: Run Test (Expect Pass)

**Expected output:** GREEN (all tests pass)

### Step 6: Refactor

Improve code quality while keeping tests green:
- Extract helper functions
- Improve naming
- Remove duplication
- Add type hints

### Step 7: Repeat for Next Criterion

## Test Structure Template (Python)

```python
"""Tests for [feature] - Issue #XXX"""
import pytest


class TestFeatureName:
    """Tests for [acceptance criteria group]"""

    @pytest.fixture
    def setup_data(self):
        """Given: [precondition]"""
        return create_test_data()

    def test_when_action_then_result(self, setup_data):
        """
        Given: [precondition]
        When: [action]
        Then: [expected result]
        """
        result = function_under_test(setup_data)
        assert result == expected_value

    def test_edge_case(self, setup_data):
        """Edge case: [description]"""
        pass
```

## Checklist Before Implementation

- [ ] All acceptance criteria have corresponding tests
- [ ] Tests are in correct location (`tests/` mirror of `src/`)
- [ ] Test file created before implementation file
- [ ] Tests run and fail for the right reason
- [ ] Edge cases identified and have tests
