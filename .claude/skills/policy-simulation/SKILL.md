---
name: policy-simulation
description: "Simulates policy options (rates, fiscal, macroprudential, FX) in the chosen model(s) with welfare and distributional effects."
argument-hint: "[policy options]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /policy-simulation — Policy Simulation

**Category:** Analysis · **Primary agent:** `economic-reasoning-specialist`

Simulates policy options (rates, fiscal, macroprudential, FX) in the chosen model(s) with welfare and distributional effects.

Arguments: `$ARGUMENTS`

## Purpose
Simulate concrete policy options (interest-rate paths, fiscal measures, macroprudential tools, FX intervention and capital flow measures) in at least two models, and compare their effects on growth, inflation, debt, financial stability and distribution. The output is a comparison of options that states which conclusions hold across models and which depend on a particular model.

**Use it when** decision-makers must choose between policy options, or the effects of a proposed measure must be quantified.

**Do not use it when** the models are not yet validated (`/validate-model`), or the question is a scenario about external events rather than policy choices (`/scenario-analysis`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved models
   - Policy options description
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `economic-reasoning-specialist` — primary agent; coordinates the work and integrates results
- `monetary-policy-rules-specialist` — Designs and evaluates monetary policy rules
- `fiscal-multiplier-specialist` — Estimates and simulates fiscal multipliers
- `macroprudential-housing-specialist` — Analyzes macroprudential policy and housing/credit cycles
- `optimal-policy-control-specialist` — Solves optimal policy problems
- `ipf-general-specialist` — Chooses the policy mix (monetary, FX intervention, capital flow, macroprudential, fiscal) by shock and friction

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Options | instruments, sizes, timing, combinations | Policy space covered |
| Implementation | announced or surprise, credible or not, temporary or permanent | Expectations effects |
| Models | semi-structural, DSGE, multi-country, lego assemblies with policy bricks | Model dependence |
| Evaluation | loss functions, welfare, distribution | Ranking of options |

## Workflow
1. Define policy options and their implementation details (instrument, timing, credibility)
2. Run each option in at least two models
   - Attach policy bricks to a validated base where needed (`/lego-add`)
3. Compare outcomes: growth, inflation, debt, financial stability, distribution
   - Use consistent shocks and baselines across models
4. Summarize trade-offs and model-dependence of conclusions

## Checkpoints with the user
- After defining options: confirm implementation details
- After results: confirm which trade-offs to emphasize

## Common pitfalls
- Comparing options with inconsistent baselines
- Assuming full credibility without saying so
- Results from one model presented as robust
- Ignoring distributional effects

## Output
`forecasts/policy-simulations/<name>.md`

The report defines each option, presents outcomes by model, compares trade-offs and states which conclusions are robust.

## Gate / verdict
- At least two models used
- Trade-offs and model dependence stated
- Credibility and timing assumptions are stated
- Baselines and shocks are consistent across models

## Suggested next steps
- `/policy-brief`
- `/chart-pack`
