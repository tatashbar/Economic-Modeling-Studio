---
name: stress-test
description: "Runs macro-financial stress tests: scenario design, satellite models, bank and sector results, policy implications."
---
<!-- Generated from .claude/skills/stress-test/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /stress-test — Stress Test

**Category:** Analysis · **Primary agent:** `financial-stability-stress-testing-specialist`

Runs macro-financial stress tests: scenario design, satellite models, bank and sector results, policy implications.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Balance-sheet data
   - Macro scenarios
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `financial-stability-stress-testing-specialist` — primary agent; coordinates the work and integrates results
- `macroprudential-housing-specialist` — Analyzes macroprudential policy and housing/credit cycles
- `scenario-risk-analysis-specialist` — Designs scenarios and risk assessments
- `banking-credit-specialist` — Models banks and credit markets

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Design severity-calibrated scenarios and document the calibration
2. Map to risk drivers with validated satellite models
3. Compute losses, capital and liquidity outcomes with second-round effects
4. Report vulnerabilities and policy responses

## Output
`forecasts/stress-tests/<name>.md`

## Gate / verdict
- Severity calibrated; satellite models validated

## Suggested next steps
- `/policy-brief`
- `/team-stress-test`
