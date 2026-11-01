---
name: nowcast
description: "Builds and runs a nowcasting system with release calendar, news decomposition and real-time evaluation."
argument-hint: "[target variable]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /nowcast — Nowcast

**Category:** Estimation · **Primary agent:** `dfm-nowcasting-specialist`

Builds and runs a nowcasting system with release calendar, news decomposition and real-time evaluation.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Indicator data
   - Release calendar
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `dfm-nowcasting-specialist` — primary agent; coordinates the work and integrates results
- `high-frequency-data-specialist` — Handles high-frequency and alternative data
- `nlp-text-as-data-specialist` — Turns text into economic data
- `forecast-evaluation-specialist` — Evaluates forecasts

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Select and validate indicators with release timing
2. Estimate DFM/bridge/MIDAS (and optionally ML) nowcasts
3. Run pseudo-real-time evaluation with vintages
4. Produce nowcast with predictive density and news decomposition
5. Set up a schedule for updating

## Output
`forecasts/nowcasts/<target>-<date>.md`; model code in `models/econometrics/<name>/`

## Gate / verdict
- Pseudo-real-time evaluation performed
- Predictive density provided

## Suggested next steps
- `/forecast-round`
- `/chart-pack`
