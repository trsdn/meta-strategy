---
name: Release Check
description: Assess release readiness — version, changelog, tests, CI status
---

# Release Check

Verify that the project is ready for a new release.

## Steps

### 1. Check Version Tag

- Determine the current version from `pyproject.toml` or version file
- Verify the version follows semantic versioning
- Confirm no existing tag conflicts

### 2. Verify Changelog

- Check that `CHANGELOG.md` exists and is up to date
- Verify all merged PRs since last release are documented
- Confirm changelog entries follow the project's format

### 3. Run Full Test Suite

```bash
make check  # or equivalent: lint + typecheck + tests
```

- All tests must pass
- No lint errors
- No type errors

### 4. Check CI Status

```bash
gh run list --branch main --limit 5
```

- Latest CI run on main must be green
- No failing required checks

### 5. Verify No WIP Branches

```bash
gh pr list --state open
```

- Review open PRs for any that should be included in this release
- Flag any PRs marked as blocking

### 6. Check for Breaking Changes

- Review commits since last release for breaking changes
- If breaking changes exist, verify version bump is major
- Confirm migration guide exists if needed

### 7. Generate Release Summary

Produce a release readiness report:

```markdown
## Release Readiness — v[X.Y.Z]

| Check | Status | Notes |
|-------|--------|-------|
| Version | ✅/⛔ | [details] |
| Changelog | ✅/⛔ | [details] |
| Tests | ✅/⛔ | [pass/fail count] |
| CI | ✅/⛔ | [last run status] |
| Open PRs | ✅/⚠️ | [count, any blockers] |
| Breaking changes | ✅/⚠️ | [details] |

**Recommendation**: Ready to release / Blocked by [X]
```
