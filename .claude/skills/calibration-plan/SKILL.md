---
name: calibration-plan
description: "Plans calibration and estimation: parameter sources, priors, moments, targets, identification checks."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /calibration-plan — Calibration Plan

**Category:** Scoping & Design · **Primary agent:** `bayesian-dsge-estimation-specialist`

Plans calibration and estimation: parameter sources, priors, moments, targets, identification checks.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - docs/models/<name>/model-spec.md
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `bayesian-dsge-estimation-specialist` — primary agent; coordinates the work and integrates results
- `emde-lic-dsge-specialist` — Adapts structural models to emerging, developing and low-income economies
- `var-vecm-specialist` — Builds VAR, SVAR and VECM models

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Classify parameters: calibrate, estimate, or fix at literature values
2. Source each calibrated value (data moment, micro study, published estimate)
3. Specify priors with rationale; plan prior predictive checks
4. List calibration targets and the identification diagnostics to run

## Output
`docs/models/<name>/calibration-plan.md`

## Gate / verdict
- Every parameter has a classification and a source or prior

## Suggested next steps
- `/estimate-dsge`
- `/calibrate-model`
