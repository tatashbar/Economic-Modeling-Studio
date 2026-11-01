---
name: stress-test
description: "Runs macro-financial stress tests: scenario design, satellite models, bank and sector results, policy implications."
argument-hint: "[sector or system]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /stress-test — Stress Test

**Category:** Analysis · **Primary agent:** `financial-stability-stress-testing-specialist`

Runs macro-financial stress tests: scenario design, satellite models, bank and sector results, policy implications.

Arguments: `$ARGUMENTS`

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

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

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
