---
name: distributional-analysis
description: "Analyzes distributional effects of a policy or shock using microsimulation, HANK links or survey-based incidence."
---
<!-- Generated from .claude/skills/distributional-analysis/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /distributional-analysis — Distributional Analysis

**Category:** Analysis · **Primary agent:** `inequality-distribution-specialist`

Analyzes distributional effects of a policy or shock using microsimulation, HANK links or survey-based incidence.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Household survey data
   - Macro scenario
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `inequality-distribution-specialist` — primary agent; coordinates the work and integrates results
- `tax-benefit-microsimulation-specialist` — Builds tax-benefit microsimulation
- `hank-specialist` — Builds heterogeneous-agent (HANK) models
- `survey-microdata-specialist` — Works with household and firm survey microdata

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Define groups and welfare measure (income, consumption, real purchasing power)
2. Map macro changes to households; include price and employment channels
3. Compute winners/losers, poverty and inequality changes with sampling uncertainty
4. Propose compensation or mitigation options and their cost

## Output
`forecasts/distribution/<name>.md`

## Gate / verdict
- Sampling uncertainty reported

## Suggested next steps
- `/policy-brief`
- `/chart-pack`
