---
name: sensitivity-analysis
description: "Runs global sensitivity and uncertainty analysis to rank assumptions and parameters that drive results."
argument-hint: "[model name] [output of interest]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /sensitivity-analysis — Sensitivity Analysis

**Category:** Validation & QA · **Primary agent:** `sensitivity-uncertainty-specialist`

Runs global sensitivity and uncertainty analysis to rank assumptions and parameters that drive results.

Arguments: `$ARGUMENTS`

## Purpose
Rank the parameters and assumptions that drive a model's results using global methods, propagate their uncertainty, and test whether the conclusions survive plausible ranges of the top drivers. The output is a key-driver ranking and a statement of how uncertain the results really are, including structural uncertainty where alternative models exist.

**Use it when** a model's results will inform decisions, calibration is uncertain, or reviewers ask which assumptions matter.

**Do not use it when** the question is whether conclusions survive other models or identification schemes (`/robustness-check`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Model code
   - Parameter ranges
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `sensitivity-uncertainty-specialist` — primary agent; coordinates the work and integrates results
- `bayesian-dsge-estimation-specialist` — Estimates DSGE models by Bayesian methods (MCMC, SMC) and checks identification, priors and fit

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Method | Morris screening, Sobol indices, Monte Carlo propagation | Interaction detection and cost |
| Ranges | posterior intervals, literature ranges, expert ranges | Plausibility |
| Outputs | decision-relevant metrics | Relevance |
| Cost control | surrogate models, sparse sampling | Feasibility |

## Workflow
1. Define output metrics and plausible parameter/assumption ranges with rationale
2. Run Sobol/Morris or Monte Carlo analysis
   - Check convergence of indices; report total-effect indices for interactions
3. Rank drivers and test whether conclusions are robust to them
4. Report structural uncertainty if alternative models exist

## Checkpoints with the user
- After ranges: confirm their sources
- After ranking: confirm which drivers need further evidence

## Common pitfalls
- One-at-a-time sensitivity in nonlinear models
- Ranges without sources
- Outputs that do not relate to the decision

## Output
`validation/<model>/sensitivity-report.md`

The report presents ranges with sources, methods, index estimates with convergence, the key-driver ranking and the robustness of conclusions.

## Gate / verdict
- Ranges justified; top drivers identified
- Index convergence is checked
- Interactions are assessed with total-effect indices

## Suggested next steps
- `/validate-model`
- `/robustness-check`
