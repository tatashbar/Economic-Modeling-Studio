---
name: model-card
description: "Writes the model card: purpose, limits, data, performance, validation status, risks and appropriate use."
---
<!-- Generated from .claude/skills/model-card/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /model-card — Model Card

**Category:** Documentation · **Primary agent:** `technical-documentation-specialist`

Writes the model card: purpose, limits, data, performance, validation status, risks and appropriate use.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Model spec
   - Results
   - Validation report (if available)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `technical-documentation-specialist` — primary agent; coordinates the work and integrates results
- `model-validation-specialist` — Performs independent model validation

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Collect facts from the spec, results and validation report
2. Draft each section of `docs/templates/model-card.md` with the user's approval
3. State intended uses and explicit non-uses
4. Verify claims against artifacts

## Output
`docs/models/<name>/model-card.md`

## Gate / verdict
- Intended and non-intended uses are explicit; every performance claim links to evidence

## Suggested next steps
- `/model-release`
- `/technical-note`
