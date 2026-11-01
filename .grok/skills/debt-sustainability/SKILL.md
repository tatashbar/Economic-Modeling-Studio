---
name: debt-sustainability
description: "Runs debt sustainability analysis: baseline, shocks, stochastic fan charts, realism checks and financing needs."
---
<!-- Generated from .claude/skills/debt-sustainability/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /debt-sustainability — Debt Sustainability

**Category:** Analysis · **Primary agent:** `debt-sustainability-analyst`

Runs debt sustainability analysis: baseline, shocks, stochastic fan charts, realism checks and financing needs.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Fiscal and macro baseline
   - Debt composition data
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `debt-sustainability-analyst` — primary agent; coordinates the work and integrates results
- `fiscal-risk-specialist` — Assesses fiscal risks
- `sovereign-crisis-games-specialist` — Models sovereign debt, default and currency crises
- `revenue-tax-policy-specialist` — Forecasts and analyzes tax revenue
- `extractives-natural-resources-specialist` — Analyzes resource-rich economies

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Build the baseline and verify the debt-dynamics decomposition
2. Apply standardized and tailored shocks; run stochastic simulations
3. Run realism checks vs. history and peers
4. Assess financing needs, contingent liabilities and rollover risk
5. Write the risk assessment with explicit limits

## Output
`forecasts/dsa/<country>-<date>.md`

## Gate / verdict
- Decomposition closes exactly
- Realism checks documented

## Suggested next steps
- `/policy-brief`
- `/team-fiscal`
