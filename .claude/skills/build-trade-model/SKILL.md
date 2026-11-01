---
name: build-trade-model
description: "Builds a trade model: gravity and structural gravity estimation, quantitative trade general equilibrium, and global value chain accounting."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-trade-model — Build Trade Model

**Category:** Build · **Primary agent:** `trade-policy-simulation-specialist`

Builds a trade model: gravity and structural gravity estimation, quantitative trade general equilibrium, and global value chain accounting.

Arguments: `$ARGUMENTS`

## Purpose
Build a trade model fit for the question: reduced-form or structural gravity estimation of trade costs and policy effects, a quantitative general-equilibrium trade model solved in changes, or value-chain accounting. The output reproduces baseline trade flows, makes the trade-balance treatment explicit, and reports welfare and sectoral effects across the plausible range of trade elasticities.

**Use it when** the question involves tariffs, trade agreements, trade costs, retaliation, value chains or trade exposure across partners and sectors.

**Do not use it when** domestic tax and factor-market detail dominates (`/build-cge`) or the question is a supply disruption through production networks (`/supply-chain-shock`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Bilateral trade data
   - Tariff and trade-cost data
   - Global input-output tables (optional)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `trade-policy-simulation-specialist` — primary agent; coordinates the work and integrates results
- `trade-gvc-specialist` — Models trade and global value chains
- `production-networks-specialist` — Models production networks and supply chains
- `cge-modeling-specialist` — Builds computable general equilibrium models

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Model type | reduced-form gravity, structural gravity, quantitative GE (Armington, Eaton–Kortum), CGE | Counterfactual capability |
| Sectors | single, multi-sector, with input-output links | Amplification through intermediates |
| Trade balance | balanced trade, fixed deficits | Counterfactual results |
| Elasticities | estimated, sourced from literature, ranges | Welfare magnitudes |
| Data | product-level trade, global IO tables | Coverage and detail |

## Workflow
1. Define the question and choose between reduced-form gravity, structural gravity, quantitative GE trade or CGE
2. Estimate trade elasticities and trade costs with PPML and high-dimensional fixed effects
   - Exporter–year, importer–year and pair fixed effects; treatment of zeros
3. Calibrate the GE model and solve counterfactuals in changes
   - Use observed trade shares; state the solution algorithm and convergence
4. Check the model reproduces baseline trade flows and the trade balance treatment is explicit
5. Report welfare and sectoral effects with elasticity sensitivity
   - Decompose welfare; compare results with and without input-output links
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Checkpoints with the user
- After choosing the model type: confirm sectors and partners
- After estimation: confirm elasticities and ranges
- Before reporting: confirm the trade-balance treatment

## Common pitfalls
- OLS gravity on logs with zeros dropped
- Single-sector models for policies hitting intermediates
- Trade-flow changes reported as welfare
- Elasticities from different aggregation levels

## Output
`models/trade/<name>/ (+ model.lego.json)`

The folder holds data, estimation scripts and results, the GE model and counterfactual scripts, the elasticity table with sources, results with welfare decomposition and the lego manifest.

## Gate / verdict
- Baseline trade flows reproduced
- Elasticity sources and ranges documented
- Trade balance closure stated
- Lego manifest passes `python tools/lego.py check`
- Gravity estimates use PPML with appropriate fixed effects
- Welfare is decomposed into its sources

## Suggested next steps
- `/trade-policy-analysis`
- `/validate-model`
- `/lego-map`
