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

## Workflow
1. Define the question and choose between reduced-form gravity, structural gravity, quantitative GE trade or CGE
2. Estimate trade elasticities and trade costs with PPML and high-dimensional fixed effects
3. Calibrate the GE model and solve counterfactuals in changes
4. Check the model reproduces baseline trade flows and the trade balance treatment is explicit
5. Report welfare and sectoral effects with elasticity sensitivity
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/trade/<name>/ (+ model.lego.json)`

## Gate / verdict
- Baseline trade flows reproduced
- Elasticity sources and ranges documented
- Trade balance closure stated
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/trade-policy-analysis`
- `/validate-model`
- `/lego-map`
