---
name: retrospective
description: "Runs a retrospective on a forecast round, model build or project: what worked, what failed, what to change."
---
<!-- Generated from .claude/skills/retrospective/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /retrospective — Retrospective

**Category:** Governance · **Primary agent:** `project-planning-specialist`

Runs a retrospective on a forecast round, model build or project: what worked, what failed, what to change.

Arguments: whatever the user wrote after the command name.

## Purpose
Run a retrospective on a forecast round, model build or project: gather the facts, decompose forecast errors into data, model, judgment and unforeseen shocks, and turn lessons into actions with owners. The output improves the next round rather than assigning blame.

**Use it when** a forecast round or project ends, or after a large forecast miss.

**Do not use it when** the aim is to re-plan an ongoing project (`/milestone-review`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Project artifacts
   - Forecast errors if relevant
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `project-planning-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense
- `forecast-evaluation-specialist` — Evaluates forecasts

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Gather facts: plan vs. actual, forecast errors, issues, rework
2. Decompose errors by data, model, judgment and shocks where relevant
   - Use data revisions, model reruns with final data and the overlay log
3. Identify process and methodology changes
4. Record actions with owners

## Checkpoints with the user
- After the error decomposition: agree the main lessons

## Common pitfalls
- Attributing every miss to unforeseeable shocks
- Lessons without actions
- Ignoring what went well

## Output
`production/retrospectives/<name>-<date>.md`

The record documents facts, error decomposition, lessons, and actions with owners and dates.

## Gate / verdict
- Each lesson has an action and an owner
- Error decomposition uses the overlay log where judgment was applied

## Suggested next steps
- `/milestone-review`
