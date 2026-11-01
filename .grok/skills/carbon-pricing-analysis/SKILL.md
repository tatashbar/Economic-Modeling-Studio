---
name: carbon-pricing-analysis
description: "Analyzes carbon pricing and emissions policy: tax or trading design, border adjustment, revenue recycling, competitiveness and distributional effects."
---
<!-- Generated from .claude/skills/carbon-pricing-analysis/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /carbon-pricing-analysis — Carbon Pricing Analysis

**Category:** Analysis · **Primary agent:** `carbon-pricing-emissions-specialist`

Analyzes carbon pricing and emissions policy: tax or trading design, border adjustment, revenue recycling, competitiveness and distributional effects.

Arguments: whatever the user wrote after the command name.

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Define the policy design: instrument, price path, coverage, revenue use and border treatment
2. Compute emissions, output, price and fiscal effects with at least two models or closures
3. Analyze competitiveness, leakage and border-adjustment effects
4. Estimate distributional incidence and compensation options
5. Report trade-offs with uncertainty and the dependence on assumptions

## Output
`forecasts/climate/<name>-carbon-pricing.md`

## Gate / verdict
- Revenue recycling variants shown
- Distributional effects reported

## Suggested next steps
- `/policy-brief`
- `/distributional-analysis`
