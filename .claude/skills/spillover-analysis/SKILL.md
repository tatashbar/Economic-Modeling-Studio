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

## Workflow
1. Define the shock and propagation channels
2. Estimate with at least two approaches (structural and reduced-form)
3. Compare estimates and explain divergence
4. Map vulnerability by country

## Output
`forecasts/spillovers/<name>.md`

## Gate / verdict
- At least two methods used

## Suggested next steps
- `/policy-brief`
- `/chart-pack`
