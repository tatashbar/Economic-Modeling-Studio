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

## Purpose
Translate climate pathways (orderly, delayed or disorderly transitions; higher or lower warming) into macro, fiscal and financial impacts for a country, running physical-risk and transition-risk channels separately and together. The output is a set of conditional scenarios with deep-uncertainty ranges and explicit damage and discounting alternatives.

**Use it when** climate scenarios are needed for projections, fiscal-risk statements, financial stress tests or adaptation planning.

**Do not use it when** a new climate-macro model must be built (`/build-climate-macro`) or a carbon-pricing design is the question (`/carbon-pricing-analysis`).

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

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Pathways | published scenario sets, custom | Comparability and consistency |
| Channels | physical, transition, both | Coverage of risks |
| Models | macro model with climate bricks, CGE, sector models | Channel detail |
| Damages | level, growth, hazard-based | Size of physical losses |
| Horizon | to 2030, 2050, 2100 | Relevance of each channel |

## Workflow
1. Select pathway assumptions and map them to macro drivers
   - Carbon prices, energy prices, productivity, investment, hazard frequencies
2. Run physical and transition channels separately and jointly
3. Report impacts with deep-uncertainty ranges; show damage-function alternatives
4. Summarize fiscal and financial implications and adaptation needs
   - Feed results into fiscal-risk and stress-test work where relevant (`/stress-test`)

## Checkpoints with the user
- After mapping: confirm pathway sources and translations
- After results: confirm ranges and how they will be communicated

## Common pitfalls
- Mixing scenario sources with incompatible assumptions
- Single damage function presented as fact
- Long-run damages treated as short-run shocks
- Ignoring transition inflation and investment

## Output
`forecasts/climate/<name>.md`

The report documents pathway translations, separate and joint channel results, uncertainty ranges, damage alternatives and fiscal and financial implications.

## Gate / verdict
- Alternatives to damage function and discount rate shown
- Physical and transition channels are reported separately and jointly
- Pathway translations are documented

## Suggested next steps
- `/policy-brief`
- `/distributional-analysis`
