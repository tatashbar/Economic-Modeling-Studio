---
name: climate-scenario
description: "Runs climate and transition scenarios: translating climate pathways to macro, fiscal and financial impacts."
argument-hint: "[scenario set]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /climate-scenario — Climate Scenario

**Category:** Analysis · **Primary agent:** `climate-macro-specialist`

Runs climate and transition scenarios: translating climate pathways to macro, fiscal and financial impacts.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Climate scenario data
   - Macro model
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `climate-macro-specialist` — primary agent; coordinates the work and integrates results
- `transition-risk-energy-specialist` — Analyzes energy systems and transition risk
- `fragility-disaster-specialist` — Analyzes fragility, conflict, pandemics and natural disasters
- `fiscal-risk-specialist` — Assesses fiscal risks
- `carbon-pricing-emissions-specialist` — Analyzes carbon pricing and emissions policy
- `physical-climate-risk-specialist` — Quantifies physical climate risk

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Select pathway assumptions and map them to macro drivers
2. Run physical and transition channels separately and jointly
3. Report impacts with deep-uncertainty ranges; show damage-function alternatives
4. Summarize fiscal and financial implications and adaptation needs

## Output
`forecasts/climate/<name>.md`

## Gate / verdict
- Alternatives to damage function and discount rate shown

## Suggested next steps
- `/policy-brief`
- `/distributional-analysis`
