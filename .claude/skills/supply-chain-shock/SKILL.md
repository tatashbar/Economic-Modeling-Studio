---
name: supply-chain-shock
description: "Analyzes sectoral and supply-chain shocks with input-output and production-network models: propagation, bottlenecks, and price and quantity effects."
argument-hint: "[shock description]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /supply-chain-shock — Supply Chain Shock

**Category:** Analysis · **Primary agent:** `production-networks-specialist`

Analyzes sectoral and supply-chain shocks with input-output and production-network models: propagation, bottlenecks, and price and quantity effects.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - IO or network data
   - Shock description
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `production-networks-specialist` — primary agent; coordinates the work and integrates results
- `input-output-sam-specialist` — Builds input-output, supply-use and social accounting matrix frameworks
- `trade-gvc-specialist` — Models trade and global value chains
- `physical-climate-risk-specialist` — Quantifies physical climate risk
- `commodity-markets-specialist` — Models commodity markets

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Define the shock: sector, region, size, duration and substitution assumptions
2. Propagate through the network with low and high substitutability
3. Estimate output, price, employment and trade effects; identify bottlenecks
4. Compare with a first-order (Hulten-style) approximation and explain differences
5. Evaluate mitigation options: diversification, stockpiles, reshoring

## Output
`forecasts/sectoral/<name>-supply-chain.md`

## Gate / verdict
- Results shown for low and high substitution
- Data coverage limits disclosed

## Suggested next steps
- `/policy-brief`
- `/scenario-analysis`
