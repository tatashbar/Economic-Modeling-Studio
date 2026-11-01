---
name: scope-question
description: "Turns a policy question into a precise modeling question: decision, audience, horizon, outputs and acceptable uncertainty."
---
<!-- Generated from .claude/skills/scope-question/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /scope-question — Scope Question

**Category:** Scoping & Design · **Primary agent:** `economic-reasoning-specialist`

Turns a policy question into a precise modeling question: decision, audience, horizon, outputs and acceptable uncertainty.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - User's description of the question
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `economic-reasoning-specialist` — primary agent; coordinates the work and integrates results
- `policy-relevance-specialist` — Clarifies the decision, audience and deadline, and reviews outputs for decision-relevance, honest uncertainty and appropriate caveats
- `stakeholder-liaison-specialist` — Interfaces with stakeholders and counterparts

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Ask: what decision will this inform, who decides, by when, and what would change their mind?
2. Clarify horizon, frequency, country coverage, and outputs required (point, density, scenario, welfare)
3. List the economic mechanisms that matter and those that can be ignored
4. Draft a one-page scoping note and ask the user to approve each section

## Output
`docs/briefs/<name>-scope.md`

## Gate / verdict
- Decision, audience, horizon and success criteria are all stated

## Suggested next steps
- `/select-model-class`
- `/model-brief`
