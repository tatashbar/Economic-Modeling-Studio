---
name: forecast-round
description: "Runs a complete forecast round: data freeze, nowcast, model runs, judgment, review and sign-off."
argument-hint: "[round id, e.g. 2026Q4]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /forecast-round — Forecast Round

**Category:** Analysis · **Primary agent:** `fpas-modeler`

Runs a complete forecast round: data freeze, nowcast, model runs, judgment, review and sign-off.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved models
   - Data pipeline
   - Previous round package
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `fpas-modeler` — primary agent; coordinates the work and integrates results
- `dfm-nowcasting-specialist` — Builds dynamic factor models and nowcasts
- `forecast-combination-specialist` — Combines forecasts
- `stakeholder-liaison-specialist` — Interfaces with stakeholders and counterparts
- `visualization-dashboard-specialist` — Designs charts and dashboards

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Freeze the data vintage and archive it
2. Update nowcasts and run core and satellite models (in parallel)
3. Combine forecasts; log every judgment overlay with owner and rationale
4. Produce shock decomposition, risks and the forecast story
5. Review with economic-reasoning-specialist and policy-relevance-specialist; archive the round package

## Output
`forecasts/<round>/`

## Gate / verdict
- Reproducible from frozen vintage
- Overlays logged
- Risks and uncertainty stated

## Suggested next steps
- `/chart-pack`
- `/policy-brief`
