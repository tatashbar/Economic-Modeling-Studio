---
name: build-semi-structural
description: "Builds a small or medium semi-structural gap/projection model with calibration, filters and baseline."
argument-hint: "[country|model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-semi-structural — Build Semi Structural

**Category:** Build · **Primary agent:** `semi-structural-gap-modeler`

Builds a small or medium semi-structural gap/projection model with calibration, filters and baseline.

Arguments: `$ARGUMENTS`

## Purpose
Build a small or medium semi-structural gap and projection model: aggregate demand, Phillips curve, policy rule, exchange-rate and external blocks, with unobserved trends and gaps filtered from data. The output is a transparent, calibrated model with a baseline, a shock-response pack and tests, suitable for forecasting and policy analysis in an FPAS.

**Use it when** a transparent projection model is needed for regular forecasting and policy discussions, data are limited, or counterparts need a model they can own and explain.

**Do not use it when** microfoundations, welfare or regime changes are central (`/build-dsge`), or an accounting framework is needed (`/build-financial-programming`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec
   - Data sheet
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `semi-structural-gap-modeler` — primary agent; coordinates the work and integrates results
- `state-space-kalman-specialist` — Builds state-space models
- `monetary-policy-rules-specialist` — Designs and evaluates monetary policy rules
- `expectations-learning-specialist` — Models expectations formation

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Size | core (4 equations), extended (fiscal, external, financial blocks) | Story richness versus maintenance |
| Trends | random walks, local linear trends, steady-state anchors | Potential output and neutral rate paths |
| Policy rule | inflation-forecast-based, Taylor-type, exchange-rate terms | Policy experiments |
| Exchange rate | UIP with premium, managed regime | External transmission |
| Parameter choice | calibration, Bayesian estimation, mix | Fit versus economic discipline |

## Workflow
1. Implement the equations and gap filters; set up code in `models/semi-structural/<name>/`
   - Separate files for parameters, equations, filtering and simulation
2. Calibrate or estimate; check steady state and impulse responses against expected signs
   - Compare persistence and pass-through with empirical evidence
3. Create the baseline run and shock-response pack
   - Standard shocks: demand, cost-push, policy, exchange-rate premium, foreign demand, commodity prices
4. Write tests: steady-state residuals, accounting identities, IRF sign checks
5. Document and hand over to validation
   - Model card and user guide (`/model-card`)
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Checkpoints with the user
- After the equations: confirm blocks and the policy rule
- After calibration: confirm IRF signs and magnitudes make sense
- After the baseline: confirm the filtered gaps and trends tell a plausible story

## Common pitfalls
- Filtered gaps driven by end-point problems
- Parameters tuned to fit without economic plausibility
- Exchange-rate blocks that ignore the actual regime
- Overlays used to fix a misspecified equation

## Output
`models/semi-structural/<name>/ (+ model.lego.json)`

The folder holds model code, calibration, filtering and baseline files, the shock-response pack, tests, documentation and the lego manifest.

## Gate / verdict
- Steady state residuals ≈ 0
- IRF signs and magnitudes are plausible and documented
- Lego manifest passes `python tools/lego.py check`
- Filtered trends and gaps are reviewed for end-point sensitivity
- Tests for identities and IRF signs pass

## Suggested next steps
- `/validate-model`
- `/forecast-round`
- `/lego-map`
