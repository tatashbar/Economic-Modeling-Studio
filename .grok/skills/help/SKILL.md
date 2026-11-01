---
name: help
description: "Explains what the studio can do, lists skills and agents by category, and suggests what to do next based on project stage."
---
<!-- Generated from .claude/skills/help/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /help — Help

**Category:** Onboarding · **Primary agent:** `project-planning-specialist`

Explains what the studio can do, lists skills and agents by category, and suggests what to do next based on project stage.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - `.claude/skills/`
   - `.claude/agents/`
   - production/stage.txt (optional)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `project-planning-specialist` — primary agent; coordinates the work and integrates results

## Workflow
1. If a skill or agent name is given, read its file and explain it in plain language with an example
2. Otherwise detect the project stage and list the skills available at this stage
3. Show the map of areas of expertise and the agents in each
4. Recommend next steps

## Output
`(conversation only)`

## Gate / verdict
- The answer cites actual files; nothing is invented

## Suggested next steps
- `/start`
- `/project-stage-detect`
