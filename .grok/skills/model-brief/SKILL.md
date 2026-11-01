---
name: model-brief
description: "Creates the model brief: purpose, model class, mechanisms, data, validation level, team, timeline and risks."
---
<!-- Generated from .claude/skills/model-brief/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /model-brief — Model Brief

**Category:** Scoping & Design · **Primary agent:** `project-planning-specialist`

Creates the model brief: purpose, model class, mechanisms, data, validation level, team, timeline and risks.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - docs/briefs/<name>-scope.md (recommended)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `project-planning-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense
- `modeling-methodology-specialist` — Chooses methods and architecture across model families, sets code and data standards, and resolves technical trade-offs between traditional, structural and AI approaches
- `model-risk-governance-specialist` — Defines model risk levels and validation depth, enforces builder-validator independence, governs AI/LLM use and recommends release or block

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Collect the scoping note, the chosen model class and available resources
2. Draft the brief from `docs/templates/model-brief.md`, one section at a time, with approval for each
3. Assign risk level with the model-risk-governance-specialist
4. Set milestones sized to the model class and flag dependencies

## Output
`docs/models/<name>/model-brief.md`

## Gate / verdict
- Purpose and non-purposes are stated
- Risk level and validation depth are agreed

## Suggested next steps
- `/literature-review`
- `/model-spec`
