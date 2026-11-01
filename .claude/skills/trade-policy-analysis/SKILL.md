---
name: trade-policy-analysis
description: "Simulates trade policy and tariff scenarios with quantitative trade and CGE models, including retaliation, value-chain propagation and welfare effects."
argument-hint: "[trade scenario]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /trade-policy-analysis — Trade Policy Analysis

**Category:** Analysis · **Primary agent:** `trade-policy-simulation-specialist`

Simulates trade policy and tariff scenarios with quantitative trade and CGE models, including retaliation, value-chain propagation and welfare effects.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved trade or CGE model
   - Tariff and trade-cost data
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `trade-policy-simulation-specialist` — primary agent; coordinates the work and integrates results
- `cge-modeling-specialist` — Builds computable general equilibrium models
- `trade-gvc-specialist` — Models trade and global value chains
- `production-networks-specialist` — Models production networks and supply chains
- `global-spillover-specialist` — Analyzes global spillovers

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Define the scenario: instruments, countries, sectors, retaliation and timing
2. Run in at least two models or elasticity sets
3. Decompose effects: terms of trade, efficiency, reallocation, value-chain propagation
4. Report winners and losers by country, sector and, where possible, household group
5. State elasticity and closure dependence of the conclusions

## Output
`forecasts/trade/<name>.md`

## Gate / verdict
- At least two models or elasticity sets used
- Trade balance treatment stated

## Suggested next steps
- `/policy-brief`
- `/chart-pack`
