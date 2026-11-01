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

## Purpose
Run a complete forecast round: freeze and archive the data vintage, update nowcasts, run the core and satellite models, combine results, apply and log judgment, build the shock decomposition, risks and forecast story, and complete review and sign-off. The output is a round package that anyone can reproduce from the frozen vintage, with every overlay traceable.

**Use it when** producing a regular projection for policy decisions or publication.

**Do not use it when** the forecasting system itself must be designed (`/build-fpas`) or a single nowcast is needed (`/nowcast`).

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

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Data cut-off | fixed date, after key releases | Information content |
| Models | core model plus satellites (lego bricks), suite | Coverage and consistency |
| Combination | core-model led, weighted combination | Story coherence |
| Judgment | add-factors, tuned shocks, conditioning paths | Traceability |
| Outputs | baseline, scenarios, fan charts, policy path | Communication |

## Workflow
1. Freeze the data vintage and archive it
2. Update nowcasts and run core and satellite models (in parallel)
   - Validate the lego assembly before running (`python tools/lego.py validate`)
3. Combine forecasts; log every judgment overlay with owner and rationale
4. Produce shock decomposition, risks and the forecast story
   - Compare with the previous round and explain revisions
5. Review with economic-reasoning-specialist and policy-relevance-specialist; archive the round package

## Checkpoints with the user
- After the data freeze: confirm the cut-off
- After model runs: agree overlays
- Before sign-off: confirm the story and risks

## Common pitfalls
- Data changes after the freeze
- Overlays without records
- Stories not supported by decompositions
- No explanation of revisions from the previous round

## Output
`forecasts/<round>/`

The round folder holds the frozen vintage, model runs, overlay log, decompositions, fan charts, scenarios, the forecast story and review records.

## Gate / verdict
- Reproducible from frozen vintage
- Overlays logged
- Risks and uncertainty stated
- Revisions from the previous round are explained
- Review sign-offs are recorded

## Suggested next steps
- `/chart-pack`
- `/policy-brief`
