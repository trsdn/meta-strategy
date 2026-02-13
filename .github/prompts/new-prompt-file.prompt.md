---
name: New Prompt File
description: Template for creating a new reusable workflow prompt
---

# New Prompt File

Guide for creating a new reusable workflow prompt in `.github/prompts/`.

## Steps

### 1. Define the Prompt

Determine the prompt's:
- **Name**: kebab-case identifier (e.g., `data-migration`)
- **Description**: One-sentence summary of when to use this prompt
- **Trigger**: What slash command activates it (e.g., `/data-migration`)

### 2. Create the Prompt File

Create `.github/prompts/NAME.prompt.md` with this structure:

```markdown
---
name: Human-Readable Name
description: One-sentence description of the workflow
---

# Workflow Name

Brief description of what this workflow accomplishes and when to use it.

## Steps

### 1. [First Phase]

[What to do in this phase. Be specific about inputs, actions, and expected outputs.]

### 2. [Second Phase]

[Next phase of the workflow.]

### 3. [Verification Phase]

[How to verify the workflow completed successfully.]
```

### 3. Register in AGENTS.md

Add the new prompt to the **Available Prompts** table in `AGENTS.md`:

```markdown
| `prompt-name` | Brief description of use case |
```

### 4. Verify

- Confirm the prompt file exists in `.github/prompts/`
- Confirm the AGENTS.md table is updated
- Test by typing `/prompt-name` in a Copilot CLI session
