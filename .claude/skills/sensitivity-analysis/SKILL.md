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

## Workflow
1. Define output metrics and plausible parameter/assumption ranges with rationale
2. Run Sobol/Morris or Monte Carlo analysis
3. Rank drivers and test whether conclusions are robust to them
4. Report structural uncertainty if alternative models exist

## Output
`validation/<model>/sensitivity-report.md`

## Gate / verdict
- Ranges justified; top drivers identified

## Suggested next steps
- `/validate-model`
- `/robustness-check`
