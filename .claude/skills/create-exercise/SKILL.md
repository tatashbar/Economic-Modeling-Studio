---
name: create-exercise
description: "Creates a hands-on exercise, case study, or policy wargame with scenario, roles, materials, facilitator guide and debrief."
argument-hint: "[learning goal]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /create-exercise — Create Exercise

**Category:** Capacity Development · **Primary agent:** `policy-wargame-facilitator`

Creates a hands-on exercise, case study, or policy wargame with scenario, roles, materials, facilitator guide and debrief.

Arguments: `$ARGUMENTS`

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

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Define learning outcomes and the decision situation
2. Design scenario, roles, information injects and scoring; optionally use an LLM-agent or model engine
3. Write the facilitator guide and debrief questions
4. Pilot with a small group; revise

## Output
`docs/training/exercises/<name>/`

## Gate / verdict
- Scenario is consistent with a validated model; confidential information is excluded

## Suggested next steps
- `/design-training`
