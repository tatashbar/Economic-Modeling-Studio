---
name: estimate-dsge
description: "Estimates a DSGE model by Bayesian methods with identification analysis, convergence diagnostics and fit evaluation."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /estimate-dsge — Estimate DSGE

**Category:** Estimation · **Primary agent:** `bayesian-dsge-estimation-specialist`

Estimates a DSGE model by Bayesian methods with identification analysis, convergence diagnostics and fit evaluation.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Built model
   - Calibration plan
   - Data pipeline
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `bayesian-dsge-estimation-specialist` — primary agent; coordinates the work and integrates results
- `state-space-kalman-specialist` — Builds state-space models
- `simulation-based-inference-specialist` — Estimates complex models with neural simulation-based inference
- `perturbation-solution-specialist` — Solves DSGE models by perturbation (1st-3rd order), pruning, and verifies determinacy and accuracy

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Run prior predictive checks and identification diagnostics
2. Estimate with MCMC or SMC; run multiple chains and convergence diagnostics
3. Compare prior vs. posterior; flag weakly identified parameters
4. Evaluate fit: marginal likelihood, posterior predictive, out-of-sample forecasts
5. Archive posterior draws and the exact run configuration

## Output
`docs/models/<name>/estimation-report.md`

## Gate / verdict
- Convergence diagnostics pass
- Identification issues documented
- Posterior draws archived

## Suggested next steps
- `/validate-model`
- `/backtest`
