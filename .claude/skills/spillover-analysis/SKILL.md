---
name: spillover-analysis
description: "Quantifies cross-country spillovers from a global shock using multiple models and country-vulnerability measures."
argument-hint: "[shock and country set]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /spillover-analysis — Spillover Analysis

**Category:** Analysis · **Primary agent:** `global-spillover-specialist`

Quantifies cross-country spillovers from a global shock using multiple models and country-vulnerability measures.

Arguments: `$ARGUMENTS`

## Purpose
Quantify how a shock in a large economy or in global markets spills over to other countries, using at least one structural and one reduced-form approach, explaining why their estimates differ, and mapping which countries are most vulnerable and why. The output is a range of spillover estimates with a channel decomposition and a vulnerability map.

**Use it when** assessing effects of foreign monetary tightening, growth slowdowns, commodity shocks, financial stress or trade policy on a country or group of countries.

**Do not use it when** a full multi-country model must be built first (`/build-multicountry`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Multi-country model or GVAR
   - Country data
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `global-spillover-specialist` — primary agent; coordinates the work and integrates results
- `multi-country-dsge-specialist` — Builds large multi-country DSGE models for spillovers, global shocks and policy coordination
- `capital-flows-ipf-specialist` — Models capital flows and integrated policy frameworks
- `trade-policy-simulation-specialist` — Simulates trade policy with quantitative trade models

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Shock | identified policy shock, growth shock, risk-off, commodity | Interpretation |
| Methods | GVAR, panel local projections, multi-country structural model | Range of estimates |
| Channels | trade, commodity, financial, confidence | Decomposition |
| Vulnerability measures | openness, dollar debt, reserves, regime | Country ranking |

## Workflow
1. Define the shock and propagation channels
   - Identify the source shock; do not use reduced-form innovations
2. Estimate with at least two approaches (structural and reduced-form)
3. Compare estimates and explain divergence
4. Map vulnerability by country
   - Exposure times sensitivity times buffers

## Checkpoints with the user
- After defining the shock: confirm identification
- After estimates: agree how to present the range

## Common pitfalls
- Common global shocks mistaken for spillovers
- Pooled averages hiding heterogeneity
- Ignoring recipient-country policy responses
- Trade channels overweighted when finance dominates

## Output
`forecasts/spillovers/<name>.md`

The report presents the shock, estimates by method, the reconciliation, channel decomposition and a country vulnerability map.

## Gate / verdict
- At least two methods used
- The source shock is identified
- Country heterogeneity is shown

## Suggested next steps
- `/policy-brief`
- `/chart-pack`
