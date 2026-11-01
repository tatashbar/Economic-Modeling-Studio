---
name: calibrate-model
description: "Calibrates a model to targets: moments, micro evidence and published estimates, with sensitivity of targets to parameters."
---
<!-- Generated from .claude/skills/calibrate-model/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /calibrate-model — Calibrate Model

**Category:** Estimation · **Primary agent:** `bayesian-dsge-estimation-specialist`

Calibrates a model to targets: moments, micro evidence and published estimates, with sensitivity of targets to parameters.

Arguments: whatever the user wrote after the command name.

## Purpose
Calibrate a model's parameters to data moments, micro evidence and published estimates in a way that is transparent and testable: every parameter has a source, the mapping from targets to parameters is understood, and the model is judged on moments it was not calibrated to match. The output is a calibration sheet that a reviewer can audit line by line.

**Use it when** a model is not estimated (or only partly), when estimation is weakly informative, or when steady-state ratios must match national accounts.

**Do not use it when** full-information estimation is feasible and planned (`/estimate-dsge`), or when the parameter plan itself has not been agreed (`/calibration-plan`).

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Target sample | full sample, recent regime, excluding crises | Steady-state ratios and volatilities |
| Method | exact matching, minimum distance with weights | Fit versus robustness |
| Micro evidence | household and firm studies, meta-analyses | Discipline on behavioral parameters |
| Untargeted checks | second moments, IRFs from VARs, distributional facts | Validation strength |

## Workflow
1. Compute target moments from data with the data's uncertainty
   - Bootstrap or HAC standard errors for moments; note sample choices
2. Choose parameters by matching or by minimum distance
3. Assess which parameters are pinned down by which targets
   - Jacobian of moments with respect to parameters; flag weakly pinned parameters
4. Record the calibration sheet with sources
   - Value, source, target, sensitivity for each parameter; label assumptions
5. Report moment fit and untargeted moments

## Checkpoints with the user
- After target moments: confirm the sample and targets
- After matching: review weakly pinned parameters and their assumptions

## Common pitfalls
- Targets from a non-representative period without saying so
- Parameters borrowed from studies of different economies or horizons
- Claiming fit on targeted moments as validation
- Many parameters loosely pinned by few targets

## Output
`docs/models/<name>/calibration-sheet.md`

The calibration sheet lists every parameter with value, source, target and sensitivity, and reports targeted and untargeted fit.

## Gate / verdict
- Untargeted moments reported
- Every parameter sourced
- Weakly pinned parameters are flagged with sensitivity results
- Target-sample choices are documented

## Suggested next steps
- `/validate-model`
- `/sensitivity-analysis`
