---
name: calibration-plan
description: "Plans calibration and estimation: parameter sources, priors, moments, targets, identification checks."
---
<!-- Generated from .claude/skills/calibration-plan/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /calibration-plan — Calibration Plan

**Category:** Scoping & Design · **Primary agent:** `bayesian-dsge-estimation-specialist`

Plans calibration and estimation: parameter sources, priors, moments, targets, identification checks.

Arguments: whatever the user wrote after the command name.

## Purpose
Plan, before any code is run, how each parameter of a model will be set: calibrated to data, estimated with a stated prior, or fixed at a literature value, with the source and the identification checks that will be used. The output is a plan that prevents ad hoc tuning later and tells reviewers in advance what will count as evidence.

**Use it when** a model specification is agreed and the team is about to calibrate or estimate it.

**Do not use it when** the calibration is already done and needs documenting (`/calibrate-model`) or estimation is in progress (`/estimate-dsge`).

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Split | which parameters to calibrate, estimate or fix | Data requirements and identification |
| Prior families | beta, gamma, inverse gamma, normal; endogenous priors | What data must override |
| Targets | steady-state ratios, second moments, IRF matching | Discipline on dynamics |
| Identification checks | local identification, prior–posterior overlap, simulation recovery | Credibility |

## Workflow
1. Classify parameters: calibrate, estimate, or fix at literature values
2. Source each calibrated value (data moment, micro study, published estimate)
   - Prefer evidence from comparable economies and periods
3. Specify priors with rationale; plan prior predictive checks
4. List calibration targets and the identification diagnostics to run
   - Include a simulation–recovery exercise for estimated parameters

## Checkpoints with the user
- After classification: confirm the split
- After priors: confirm their rationale

## Common pitfalls
- Priors chosen to deliver expected results
- Literature values from different contexts used without comment
- No plan for parameters the data cannot identify

## Output
`docs/models/<name>/calibration-plan.md`

The plan lists every parameter with its treatment, source or prior with rationale, targets, and the identification diagnostics to run.

## Gate / verdict
- Every parameter has a classification and a source or prior
- Identification diagnostics are listed for every estimated parameter

## Suggested next steps
- `/estimate-dsge`
- `/calibrate-model`
