---
name: literature-review
description: "Reviews the theoretical and empirical literature and existing models in use for a modeling question."
---
<!-- Generated from .claude/skills/literature-review/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /literature-review — Literature Review

**Category:** Scoping & Design · **Primary agent:** `economic-reasoning-specialist`

Reviews the theoretical and empirical literature and existing models in use for a modeling question.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Topic; document corpus if available (`docs/references/`)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `economic-reasoning-specialist` — primary agent; coordinates the work and integrates results
- `growth-productivity-specialist` — Analyzes growth and productivity
- `llm-economic-analyst` — Uses LLMs for economic analysis
- `rag-knowledge-specialist` — Builds retrieval-augmented knowledge systems over document collections

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Search the project's reference collection first; use external sources only where permitted
2. Summarize the core theoretical mechanisms, standard calibrations and empirical estimates
3. List existing models and known strengths and weaknesses
4. Verify every cited number against its source; mark unverifiable claims clearly
5. Produce an annotated bibliography and an evidence table

## Output
`docs/references/<topic>-review.md`

## Gate / verdict
- Every cited number is traceable to a source; unverified items are flagged

## Suggested next steps
- `/model-spec`
- `/calibration-plan`
