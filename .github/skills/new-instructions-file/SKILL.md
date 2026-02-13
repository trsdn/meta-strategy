---
name: new-instructions-file
description: "Create new instructions file. Triggers on: 'create instructions', 'new instructions'."
---

# New Instructions File

Guide for creating directory-specific instructions that GitHub Copilot automatically loads.

## Background

GitHub Copilot supports `copilot-instructions.md` files in subdirectories. When Copilot works in a directory, it automatically loads the instructions from that directory's `copilot-instructions.md`, providing context-specific rules.

## Steps

### 1. Identify the Directory

Choose a directory that has specific conventions worth documenting:
- `tests/` — test conventions, fixtures, naming patterns
- `scripts/` — script conventions, execution protocols
- `src/` — source code conventions, module patterns
- Any subdirectory with domain-specific rules

### 2. Create the Instructions File

Create `<directory>/copilot-instructions.md` with area-specific conventions:

```markdown
# [Directory Name] Instructions

## Purpose

[What this directory contains and its role in the project.]

## Conventions

- [Convention 1 — naming, structure, or pattern rules]
- [Convention 2 — required elements or standards]
- [Convention 3 — anti-patterns to avoid]

## Key Files

| File | Purpose |
|------|---------|
| [file] | [what it does] |

## Common Tasks

### [Task 1]

[How to accomplish this task in this directory.]

### [Task 2]

[How to accomplish this task in this directory.]
```

### 3. Reference in Main Instructions (Optional)

If the project uses a central instructions file, add a reference to the new file:

```markdown
## Nested Context

Directory-specific instructions are auto-loaded:
- `tests/copilot-instructions.md` — test conventions
- `<new-dir>/copilot-instructions.md` — [description]
```

### 4. Verify

- Confirm the file is in the correct directory
- Test by working in that directory and verifying Copilot loads the context
