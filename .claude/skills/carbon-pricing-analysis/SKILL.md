---
name: carbon-pricing-analysis
description: "Analyzes carbon pricing and emissions policy: tax or trading design, border adjustment, revenue recycling, competitiveness and distributional effects."
argument-hint: "[policy design]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /carbon-pricing-analysis — Carbon Pricing Analysis

**Category:** Analysis · **Primary agent:** `carbon-pricing-emissions-specialist`

Analyzes carbon pricing and emissions policy: tax or trading design, border adjustment, revenue recycling, competitiveness and distributional effects.

Arguments: `$ARGUMENTS`

## Purpose
Analyze a carbon tax, emissions trading system or related measure end to end: emissions and economic effects, public revenue and its use, competitiveness and leakage, border adjustments, and who bears the cost. The output is an assessment that shows trade-offs across design options and states how much the conclusions depend on models, closures and elasticities.

**Use it when** a government or analyst is designing, reforming or evaluating carbon pricing, fossil-fuel subsidy reform, or a border carbon adjustment.

**Do not use it when** long-run damages and optimal carbon paths are the question (`/build-climate-macro`), or macro scenario translation is needed (`/climate-scenario`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Emissions baseline
   - Approved CGE, IO or macro model
   - Household data for incidence (optional)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `carbon-pricing-emissions-specialist` — primary agent; coordinates the work and integrates results
- `cge-modeling-specialist` — Builds computable general equilibrium models
- `climate-macro-specialist` — Models climate and macro
- `tax-benefit-microsimulation-specialist` — Builds tax-benefit microsimulation
- `trade-policy-simulation-specialist` — Simulates trade policy with quantitative trade models
- `input-output-sam-specialist` — Builds input-output, supply-use and social accounting matrix frameworks

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Instrument | tax, trading with price floor/ceiling, feebates, standards | Price certainty versus quantity certainty |
| Coverage | power and industry, transport and buildings, economy-wide | Emissions and incidence |
| Revenue use | lump-sum transfers, labor-tax cuts, targeted support, investment, deficit reduction | Efficiency and progressivity |
| Trade treatment | free allocation, output-based rebates, border adjustment | Leakage and competitiveness |
| Models | IO price model, CGE, macro model, microsimulation | Coverage of channels |

## Workflow
1. Define the policy design: instrument, price path, coverage, revenue use and border treatment
   - Build the emissions baseline with documented accounting conventions
2. Compute emissions, output, price and fiscal effects with at least two models or closures
3. Analyze competitiveness, leakage and border-adjustment effects
   - Identify emissions-intensive trade-exposed sectors
4. Estimate distributional incidence and compensation options
   - Direct (fuel) and indirect (goods) effects by decile and region; cost of compensation
5. Report trade-offs with uncertainty and the dependence on assumptions

## Checkpoints with the user
- After the design: confirm price path, coverage and revenue options to compare
- After first results: confirm which compensation options to cost

## Common pitfalls
- Mixing production- and consumption-based emissions
- Incidence reported without offsetting transfers
- Ignoring interactions with existing energy taxes and subsidies
- Overstating leakage

## Output
`forecasts/climate/<name>-carbon-pricing.md`

The report covers the design, emissions baseline, economic and fiscal effects, competitiveness and leakage, distributional incidence with compensation, and sensitivity to models and elasticities.

## Gate / verdict
- Revenue recycling variants shown
- Distributional effects reported
- Emissions accounting conventions are documented
- Results are shown for at least two models or closures

## Suggested next steps
- `/policy-brief`
- `/distributional-analysis`
