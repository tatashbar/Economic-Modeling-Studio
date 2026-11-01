---
name: fan-chart
description: "Produces density forecasts and fan charts with documented uncertainty method and calibration checks."
---
<!-- Generated from .claude/skills/fan-chart/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /fan-chart — Fan Chart

**Category:** Analysis · **Primary agent:** `scenario-risk-analysis-specialist`

Produces density forecasts and fan charts with documented uncertainty method and calibration checks.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Forecast models and error history
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `scenario-risk-analysis-specialist` — primary agent; coordinates the work and integrates results
- `forecast-evaluation-specialist` — Evaluates forecasts
- `visualization-dashboard-specialist` — Designs charts and dashboards

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Choose the method (model-based, historical errors, quantile regression)
2. Compute densities and risk balance; check coverage on past forecasts
3. Render charts with consistent style; label vintage and method

## Output
`forecasts/<round>/fan-charts/`

## Gate / verdict
- Historical coverage is checked
- Method documented on the chart

## Suggested next steps
- `/chart-pack`
- `/forecast-round`
