---
name: build-fpas
description: "Designs and builds a forecasting and policy analysis system: core model, nowcasts, judgment layer, forecast process."
argument-hint: "[country|system name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-fpas — Build FPAS

**Category:** Build · **Primary agent:** `fpas-modeler`

Designs and builds a forecasting and policy analysis system: core model, nowcasts, judgment layer, forecast process.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Core model or approved model-spec
   - Data pipeline
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `fpas-modeler` — primary agent; coordinates the work and integrates results
- `dfm-nowcasting-specialist` — Builds dynamic factor models and nowcasts
- `stakeholder-liaison-specialist` — Interfaces with stakeholders and counterparts
- `visualization-dashboard-specialist` — Designs charts and dashboards

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Define the forecast process calendar, roles and sign-offs
2. Integrate core model, near-term nowcast tools and judgment-overlay log
3. Build the shock-decomposition and forecast-story templates
4. Run a mock forecast round on historical data and review lessons
5. Prepare training material for the counterpart team
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/fpas/<name>/ and docs/models/<name>/fpas-design.md (+ model.lego.json)`

## Gate / verdict
- A full mock round runs end-to-end from a frozen data vintage
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/forecast-round`
- `/design-training`
- `/lego-map`
