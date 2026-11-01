---
name: local-projections
description: "Estimates impulse responses and state-dependent effects with local projections; compares with VAR."
---
<!-- Generated from .claude/skills/local-projections/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /local-projections — Local Projections

**Category:** Estimation · **Primary agent:** `local-projections-specialist`

Estimates impulse responses and state-dependent effects with local projections; compares with VAR.

Arguments: whatever the user wrote after the command name.

## Purpose
Estimate impulse responses by local projections, horizon by horizon, including state-dependent and nonlinear responses, with inference that respects overlapping horizons, and compare the results with VAR-based responses. The output is a set of responses with honest bands and an explanation of any differences from the VAR.

**Use it when** responses to an identified shock are needed, state dependence (slack, lower bound, debt) is of interest, or panel data across countries or regions are available.

**Do not use it when** the shock is not identified (`/identify-shocks` first) or the sample is so short that the efficiency of a VAR is needed (`/estimate-var`).

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Shock | narrative, high-frequency, VAR-identified, instrument | Identification |
| Controls | lags of outcome and shock, other macro controls | Bias and variance |
| Inference | HAC, lag-augmented, bootstrap | Coverage of bands |
| Smoothing | none, smooth LP, Bayesian LP | Noise at long horizons |
| State dependence | interaction terms, regime indicators | Nonlinear effects |

## Workflow
1. Specify horizons, controls, and state variables
   - Define states before estimation; avoid data-mined thresholds
2. Estimate with HAC/bootstrap inference; apply smoothing if appropriate
3. Estimate state-dependent responses
   - Test differences across states, not only within-state significance
4. Compare to VAR-based IRFs and explain differences

## Checkpoints with the user
- After specification: confirm horizons, controls and states
- After results: confirm interpretation of state differences

## Common pitfalls
- Noisy long-horizon responses over-interpreted
- States defined after seeing results
- Comparing within-state significance instead of testing differences
- Ignoring compositional changes across horizons in panels

## Output
`docs/models/<name>/lp-results.md`; code and settings in `models/econometrics/<name>/`

The results document reports specifications, responses with bands, state-dependent results and the VAR comparison; code and settings allow exact rerun.

## Gate / verdict
- Inference accounts for overlapping horizons
- Differences across states are formally tested
- Differences from VAR responses are explained

## Suggested next steps
- `/validate-model`
- `/policy-simulation`
