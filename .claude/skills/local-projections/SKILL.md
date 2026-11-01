---
name: local-projections
description: "Estimates impulse responses and state-dependent effects with local projections; compares with VAR."
argument-hint: "[shock and outcome]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /local-projections — Local Projections

**Category:** Estimation · **Primary agent:** `local-projections-specialist`

Estimates impulse responses and state-dependent effects with local projections; compares with VAR.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Data sheet
   - Shock series
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `local-projections-specialist` — primary agent; coordinates the work and integrates results
- `shock-identification-specialist` — Identifies structural shocks
- `fiscal-multiplier-specialist` — Estimates and simulates fiscal multipliers

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Specify horizons, controls, and state variables
2. Estimate with HAC/bootstrap inference; apply smoothing if appropriate
3. Estimate state-dependent responses
4. Compare to VAR-based IRFs and explain differences

## Output
`docs/models/<name>/lp-results.md`; code and settings in `models/econometrics/<name>/`

## Gate / verdict
- Inference accounts for overlapping horizons

## Suggested next steps
- `/validate-model`
- `/policy-simulation`
