---
name: Code Review
description: Structured code review with security, performance, and quality checklists
---

# Code Review

Perform thorough, structured code reviews focusing on security, performance, maintainability, and correctness.

## Review Process

### 1. Understand the Change

Before reviewing, gather context:

```bash
git diff main...HEAD
# Or for a specific PR
gh pr diff <number>
```

### 2. Review Checklist

#### Security 🔒

- [ ] No hardcoded secrets, API keys, or passwords
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] Authentication/authorization checks present
- [ ] Sensitive data not logged
- [ ] Dependencies are up to date (no known CVEs)

#### Performance ⚡

- [ ] No N+1 query patterns
- [ ] Expensive operations not in loops
- [ ] Appropriate caching where needed
- [ ] No memory leaks (event listeners cleaned up)
- [ ] Lazy loading for large data sets
- [ ] Database indexes for queried fields

#### Code Quality 📐

- [ ] Single responsibility principle
- [ ] DRY (Don't Repeat Yourself)
- [ ] Meaningful variable/function names
- [ ] Functions are reasonably sized (< 50 lines)
- [ ] No dead code or commented-out code
- [ ] Error handling is comprehensive

#### Testing 🧪

- [ ] New code has tests
- [ ] Edge cases covered
- [ ] Tests are readable and maintainable
- [ ] Mocks are appropriate (not over-mocked)

#### Documentation 📝

- [ ] Public APIs documented
- [ ] Complex logic has comments
- [ ] README updated if needed
- [ ] Breaking changes documented

### 3. Comment Format

```text
**[SEVERITY]** Brief description

**Location:** file.py:42

**Issue:**
Explanation of the problem.

**Suggestion:**
Recommended fix.

**Why:**
Explanation of why this matters.
```

Severity levels:

- 🔴 **BLOCKER** — Must fix before merge
- 🟠 **MAJOR** — Should fix, significant issue
- 🟡 **MINOR** — Nice to fix, minor issue
- 🔵 **SUGGESTION** — Optional improvement
- 💚 **PRAISE** — Highlight good code

### 4. Generate Review Summary

```markdown
## Review Summary

**Overall:** ✅ Approved / ⚠️ Changes Requested / ❌ Needs Work

### Stats
- Files reviewed: X
- Issues found: X (Y blockers, Z major)

### Highlights
- 💚 Good practices observed

### Required Changes
1. 🔴 [Blocker description]
2. 🟠 [Major issue description]

### Suggestions
1. 🔵 [Optional improvement]
```
