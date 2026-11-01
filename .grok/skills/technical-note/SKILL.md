---
name: technical-note
description: "Writes a technical note or methodology paper from model work: motivation, method, results, robustness, limits."
---
<!-- Generated from .claude/skills/technical-note/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /technical-note — Technical Note

**Category:** Documentation · **Primary agent:** `technical-documentation-specialist`

Writes a technical note or methodology paper from model work: motivation, method, results, robustness, limits.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Model outputs
   - Validation report
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `technical-documentation-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Agree audience and outline with the user
2. Draft section by section; keep notation consistent with the model spec
3. Link all numbers to model runs; include limitations
4. Run a replication check on key tables

## Output
`docs/notes/<name>.md`

## Gate / verdict
- All numbers link to a model run in the registry

## Suggested next steps
- `/policy-brief`
