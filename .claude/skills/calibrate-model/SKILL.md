---
name: calibrate-model
description: "Calibrates a model to targets: moments, micro evidence and published estimates, with sensitivity of targets to parameters."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /calibrate-model — Calibrate Model

**Category:** Estimation · **Primary agent:** `bayesian-dsge-estimation-specialist`

Calibrates a model to targets: moments, micro evidence and published estimates, with sensitivity of targets to parameters.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Calibration plan
   - Target data
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `bayesian-dsge-estimation-specialist` — primary agent; coordinates the work and integrates results
- `emde-lic-dsge-specialist` — Adapts structural models to emerging, developing and low-income economies
- `sensitivity-uncertainty-specialist` — Quantifies uncertainty and sensitivity

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Compute target moments from data with the data's uncertainty
2. Choose parameters by matching or by minimum distance
3. Assess which parameters are pinned down by which targets
4. Record the calibration sheet with sources
5. Report moment fit and untargeted moments

## Output
`docs/models/<name>/calibration-sheet.md`

## Gate / verdict
- Untargeted moments reported
- Every parameter sourced

## Suggested next steps
- `/validate-model`
- `/sensitivity-analysis`
