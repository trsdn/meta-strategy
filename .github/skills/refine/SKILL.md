---
name: refine
description: "Turn type:idea issues into concrete backlog issues with acceptance criteria. Triggers on: 'refine', 'refinement', 'process ideas', 'backlog refinement'."
---

# Backlog Refinement

You are the **Product Owner + Scrum Master** running backlog refinement autonomously.

**Purpose**: Turn `type:idea` issues into concrete, implementable issues with acceptance criteria.

**No code changes during refinement. Only research, decomposition, and issue creation.**

## Step 1: Find Ideas

```bash
gh issue list --label "type:idea" --state open
```

If no ideas found, report "No ideas to refine" and stop.

## Step 2: For Each Idea

### 2a. Research

- Read the idea issue carefully
- Research the topic: web search for best practices, patterns, prior art
- Analyze the codebase for relevant existing code
- Identify dependencies and constraints

### 2b. Decompose

Break the idea into 3-8 concrete issues. Each issue MUST have:

- **Clear title** (imperative: "Add X", "Implement Y", not "X should be added")
- **Description** with context and approach
- **Acceptance criteria** (testable, specific)
- **Suggested priority** (ICE score)
- **Estimated scope** (config-only / small / medium / large)

### 2c. Present Decomposition

Before creating issues, present the breakdown:

```
## Refinement: [Idea Title] (#N)

**Research summary**: [what was learned, key decisions]

**Proposed issues:**

1. **[Title]** — [1-line description] | Priority: [H/M/L] | Scope: [size]
   - AC: [acceptance criteria]
2. ...

**Total**: X issues | Estimated: Y sprint points
**Dependencies**: [any ordering constraints]
```

### 2d. Escalation Check

- If >8 issues generated → SHOULD escalate (notify stakeholder, continue if no response)
- If idea requires strategic direction → MUST escalate
- If idea conflicts with existing architecture/ADRs → MUST escalate

### 2e. Create Issues

```bash
gh issue create \
  --title "[issue title]" \
  --body "[description with acceptance criteria]" \
  --label "priority:[high|medium|low]"
```

Do NOT add `status:planned` — issues go to backlog. Sprint planning picks them up.

### 2f. Close the Idea

```bash
gh issue comment N --body "### Refined into concrete issues

**Research**: [brief summary]
**Issues created**: #X, #Y, #Z
**Ready for**: Next sprint planning cycle"

gh issue close N --reason completed
```

## Step 3: Summary

After processing all ideas:

```
## Refinement Summary

- Ideas processed: X
- Issues created: Y
- Ready for next /sprint-planning
```

## Constraints

- Do NOT write code during refinement
- Do NOT add issues to current sprint (they go to backlog)
- Do NOT skip acceptance criteria — every issue needs them
- Research before decomposing — understand the domain first
