---
name: estimate-bvar
description: "Estimates Bayesian VARs with prior choice, hyperparameter selection, conditional forecasts and out-of-sample checks."
argument-hint: "[variables|spec path]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /estimate-bvar — Estimate Bvar

**Category:** Estimation · **Primary agent:** `bayesian-var-specialist`

Estimates Bayesian VARs with prior choice, hyperparameter selection, conditional forecasts and out-of-sample checks.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Data sheet
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `bayesian-var-specialist` — primary agent; coordinates the work and integrates results
- `tvp-regime-switching-specialist` — Builds time-varying parameter, stochastic-volatility, Markov-switching and structural-break models
- `forecast-evaluation-specialist` — Evaluates forecasts

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Choose prior family and select hyperparameters by a documented rule
2. Estimate; check convergence and stability
3. Produce unconditional and conditional forecasts
4. Evaluate out-of-sample against random walk and AR benchmarks

## Output
`docs/models/<name>/bvar-results.md`; code and settings in `models/econometrics/<name>/`

## Gate / verdict
- Out-of-sample comparison with benchmarks present

## Suggested next steps
- `/forecast-round`
- `/validate-model`
