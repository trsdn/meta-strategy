---
name: New Custom Agent
description: Template for creating a new specialized agent definition
---

# New Custom Agent

Guide for creating a new specialized agent in `.github/agents/`.

## Steps

### 1. Define the Agent

Determine the agent's:
- **Name**: kebab-case identifier (e.g., `performance-analyst`)
- **Description**: One-sentence summary of what this agent does
- **Domain**: What area of expertise it covers

### 2. Create the Agent File

Create `.github/agents/NAME.agent.md` with this structure:

```markdown
---
name: Agent Name
description: One-sentence description of the agent's purpose
tools: ['editFiles', 'runCommand', 'search']
---

# Agent: Agent Name

## Role

[What this agent specializes in. Be specific about the domain and responsibilities.]

## Capabilities

- [Capability 1 — what it can do]
- [Capability 2 — what it can do]
- [Capability 3 — what it can do]

## Workflow

1. [Step 1 — how the agent approaches tasks]
2. [Step 2 — analysis or implementation phase]
3. [Step 3 — verification phase]

## Verification

Before claiming work is done, the agent must:
- [Verification step 1]
- [Verification step 2]

## Guidelines

- [Rule 1 — domain-specific constraint]
- [Rule 2 — quality standard]
- [Rule 3 — safety rule]
```

### 3. Register in AGENTS.md

Add the new agent to the **Available Agents** table in `AGENTS.md`:

```markdown
| Agent Name | `@agent-name` | Brief description of use case |
```

### 4. Verify

- Confirm the agent file exists in `.github/agents/`
- Confirm the AGENTS.md table is updated
- Test by invoking `@agent-name` in a Copilot CLI session
