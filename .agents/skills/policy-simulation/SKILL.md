---
name: policy-simulation
description: "Simulates policy options (rates, fiscal, macroprudential, FX) in the chosen model(s) with welfare and distributional effects."
---
<!-- Generated from .claude/skills/policy-simulation/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /policy-simulation — Policy Simulation

**Category:** Analysis · **Primary agent:** `economic-reasoning-specialist`

Simulates policy options (rates, fiscal, macroprudential, FX) in the chosen model(s) with welfare and distributional effects.

Arguments: whatever the user wrote after the command name.

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Define policy options and their implementation details (instrument, timing, credibility)
2. Run each option in at least two models
3. Compare outcomes: growth, inflation, debt, financial stability, distribution
4. Summarize trade-offs and model-dependence of conclusions

## Output
`forecasts/policy-simulations/<name>.md`

## Gate / verdict
- At least two models used
- Trade-offs and model dependence stated

## Suggested next steps
- `/policy-brief`
- `/chart-pack`
