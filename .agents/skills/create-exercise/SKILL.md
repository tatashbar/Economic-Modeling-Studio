---
name: create-exercise
description: "Creates a hands-on exercise, case study, or policy wargame with scenario, roles, materials, facilitator guide and debrief."
---
<!-- Generated from .claude/skills/create-exercise/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /create-exercise — Create Exercise

**Category:** Capacity Development · **Primary agent:** `policy-wargame-facilitator`

Creates a hands-on exercise, case study, or policy wargame with scenario, roles, materials, facilitator guide and debrief.

Arguments: whatever the user wrote after the command name.

## Purpose
Create a hands-on exercise, case study or policy wargame in which participants make decisions with a model: a realistic scenario, roles, information injects, scoring, a facilitator guide and debrief questions. The output is a piloted exercise that teaches through decisions and their consequences, built on a validated model and free of confidential data.

**Use it when** training analysts or policymakers, preparing for crises, or testing coordination and playbooks.

**Do not use it when** a full curriculum is needed (`/design-training`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Learning goal
   - Audience
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `policy-wargame-facilitator` — primary agent; coordinates the work and integrates results
- `training-curriculum-designer` — Designs training and capacity development
- `llm-agent-simulation-specialist` — Builds LLM-based economic agents and simulations

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Format | lab exercise, case study, tabletop, wargame | Interaction level |
| Engine | validated model, lego set, LLM-agent role players, expert adjudication | Realism and cost |
| Audience | analysts, senior officials, mixed | Difficulty and focus |
| Duration | hours, days | Depth |

## Workflow
1. Define learning outcomes and the decision situation
2. Design scenario, roles, information injects and scoring; optionally use an LLM-agent or model engine
   - Build injects from a validated scenario; lego exercises can ask participants to attach, swap and validate bricks
3. Write the facilitator guide and debrief questions
4. Pilot with a small group; revise

## Checkpoints with the user
- After learning outcomes
- After the pilot

## Common pitfalls
- Inconsistent injects
- Too many injects for the time
- Outcomes treated as forecasts
- Debriefs that skip failures

## Output
`docs/training/exercises/<name>/`

The exercise folder holds the scenario, roles, injects, scoring, participant materials, facilitator guide, debrief questions and pilot notes.

## Gate / verdict
- Scenario is consistent with a validated model; confidential information is excluded
- Learning outcomes are assessed in the debrief

## Suggested next steps
- `/design-training`
