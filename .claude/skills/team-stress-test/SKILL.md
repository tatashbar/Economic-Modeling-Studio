---
name: team-stress-test
description: "Orchestrates a macro-financial stress-test exercise: scenarios, satellite models, network contagion, results and policy options."
argument-hint: "[system or sector]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /team-stress-test — Team Stress Test

**Category:** Team Orchestration · **Primary agent:** `financial-stability-stress-testing-specialist`

Orchestrates a macro-financial stress-test exercise: scenarios, satellite models, network contagion, results and policy options.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Balance-sheet data
   - Scenario design brief
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `financial-stability-stress-testing-specialist` — primary agent; coordinates the work and integrates results
- `macroprudential-housing-specialist` — Analyzes macroprudential policy and housing/credit cycles
- `scenario-risk-analysis-specialist` — Designs scenarios and risk assessments
- `graph-ml-specialist` — Models networks with graph methods
- `financial-frictions-dsge-specialist` — Builds DSGE models with financial frictions
- `model-validation-specialist` — Performs independent model validation
- `policy-brief-writer` — Writes policy briefs and notes

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Phase 1: scenario-risk-analysis-specialist and economic-reasoning-specialist design scenarios; user approves severity
2. Phase 2 (parallel): satellite models, network contagion, and DSGE feedback runs
3. Phase 3: stress-testing specialist aggregates results and capital/liquidity outcomes
4. Phase 4: independent validation of the satellite models and aggregation
5. Phase 5: policy-brief-writer prepares results and policy options

## Output
`forecasts/stress-tests/<name>/`

## Gate / verdict
- Scenario calibration documented; validation complete

## Suggested next steps
- `/policy-brief`
