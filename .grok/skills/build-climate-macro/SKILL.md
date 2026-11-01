---
name: build-climate-macro
description: "Builds a climate-macro model: climate-augmented macro or integrated-assessment-style model with damage functions, abatement and carbon pricing."
---
<!-- Generated from .claude/skills/build-climate-macro/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-climate-macro — Build Climate Macro

**Category:** Build · **Primary agent:** `climate-macro-specialist`

Builds a climate-macro model: climate-augmented macro or integrated-assessment-style model with damage functions, abatement and carbon pricing.

Arguments: whatever the user wrote after the command name.

## Purpose
Build a model that connects climate and the macroeconomy: emissions from economic activity, damages from warming, abatement and its costs, carbon pricing and its revenue, and adaptation. The output is a model whose normative choices (damages, discounting) are explicit and varied, and whose results are presented as ranges that reflect deep uncertainty.

**Use it when** the question involves carbon pricing paths, the social cost of carbon, long-run damages, transition dynamics, or the macro and fiscal implications of climate scenarios.

**Do not use it when** the question is a near-term carbon-tax incidence or revenue estimate (`/carbon-pricing-analysis`), a scenario translation into an existing macro model (`/climate-scenario`), or sector-level detail without macro feedback (`/build-io-sam`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec
   - Emissions and energy data
   - Damage-function evidence
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `climate-macro-specialist` — primary agent; coordinates the work and integrates results
- `carbon-pricing-emissions-specialist` — Analyzes carbon pricing and emissions policy
- `physical-climate-risk-specialist` — Quantifies physical climate risk
- `transition-risk-energy-specialist` — Analyzes energy systems and transition risk
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Model family | climate-augmented DSGE, IAM (DICE-type), multi-sector, CGE-linked | Horizon, policy detail, uncertainty treatment |
| Damage function | quadratic level damages, growth damages, empirically estimated nonlinear, tipping points | Size and timing of losses |
| Discounting | Ramsey parameters, declining rates, descriptive versus prescriptive | Present value of damages and optimal carbon price |
| Energy detail | aggregate emissions intensity, energy nest, explicit technologies | Abatement costs and transition dynamics |
| Uncertainty | deterministic scenarios, Monte Carlo over parameters, robust decision | How uncertainty is reported |

## Workflow
1. Choose the structure (climate-augmented DSGE, IAM-style, multi-sector, CGE-linked) with the user
   - Match the horizon and policy question to the family; state what the model cannot answer
2. Specify emissions, abatement, damage and (if relevant) adaptation blocks; document discounting and damage-function choices
   - Label normative choices as such; keep alternatives ready to run
3. Calibrate and test the model against historical emissions and energy intensity
   - Reconcile with national inventories and energy balances
4. Run baseline and policy pathways; test sensitivity to damages, discounting and technology costs
   - Include orderly and delayed transition paths where relevant
5. Report deep uncertainty as ranges and document limitations
   - Show results across damage functions and discount rates side by side
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Checkpoints with the user
- After choosing the structure: confirm the horizon and questions
- After specifying damages and discounting: confirm which alternatives to report
- After baseline calibration: confirm the emissions baseline

## Common pitfalls
- A single damage function presented as fact
- Discount rates chosen without stating their normative basis
- Technology-cost assumptions anchored on outdated estimates
- Mixing scenario sources with incompatible assumptions

## Output
`models/climate/<name>/ (+ model.lego.json)`

The folder holds model code, calibration and emissions-baseline files, scenario scripts, the sensitivity pack across damages, discounting and technology costs, the limitations note and the lego manifest.

## Gate / verdict
- Damage-function and discount-rate alternatives shown
- Emissions accounting consistent with the baseline
- Lego manifest passes `python tools/lego.py check`
- Normative choices are labeled and alternatives reported side by side
- Results are presented as ranges, not single paths

## Suggested next steps
- `/climate-scenario`
- `/carbon-pricing-analysis`
- `/validate-model`
- `/lego-map`
