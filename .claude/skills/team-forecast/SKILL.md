---
name: team-forecast
description: "Orchestrates a full forecast round across nowcasting, core model, ML ensemble, judgment, risks, charts and brief."
argument-hint: "[round id]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /team-forecast — Team Forecast

**Category:** Team Orchestration · **Primary agent:** `fpas-modeler`

Orchestrates a full forecast round across nowcasting, core model, ML ensemble, judgment, risks, charts and brief.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Frozen data vintage
   - Approved models
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `fpas-modeler` — primary agent; coordinates the work and integrates results
- `dfm-nowcasting-specialist` — Builds dynamic factor models and nowcasts
- `time-series-deep-learning-specialist` — Builds deep sequence and foundation-model forecasters
- `bayesian-var-specialist` — Builds Bayesian VARs
- `forecast-combination-specialist` — Combines forecasts
- `scenario-risk-analysis-specialist` — Designs scenarios and risk assessments
- `stakeholder-liaison-specialist` — Interfaces with stakeholders and counterparts
- `visualization-dashboard-specialist` — Designs charts and dashboards
- `policy-brief-writer` — Writes policy briefs and notes

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Phase 1: data-engineer freezes the vintage; data-quality checks run
2. Phase 2 (parallel): nowcast, core model, BVAR and ML forecasters run
3. Phase 3: forecast-combination-specialist combines; stakeholder-liaison-specialist logs overlays with stakeholders
4. Phase 4 (parallel): scenario-risk-analysis-specialist builds risks; visualization-dashboard-specialist builds charts
5. Phase 5: policy-brief-writer drafts the brief; economic-reasoning-specialist and policy-relevance-specialist review; archive the package

## Output
`forecasts/<round>/`

## Gate / verdict
- Reproducible; overlays logged; risk balance stated

## Suggested next steps
- `/retrospective`
- `/policy-brief`
