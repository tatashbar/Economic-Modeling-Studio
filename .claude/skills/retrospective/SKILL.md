---
name: retrospective
description: "Runs a retrospective on a forecast round, model build or project: what worked, what failed, what to change."
argument-hint: "[project or round]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /retrospective — Retrospective

**Category:** Governance · **Primary agent:** `project-planning-specialist`

Runs a retrospective on a forecast round, model build or project: what worked, what failed, what to change.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Project artifacts
   - Forecast errors if relevant
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `project-planning-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense
- `forecast-evaluation-specialist` — Evaluates forecasts

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Gather facts: plan vs. actual, forecast errors, issues, rework
2. Decompose errors by data, model, judgment and shocks where relevant
3. Identify process and methodology changes
4. Record actions with owners

## Output
`production/retrospectives/<name>-<date>.md`

## Gate / verdict
- Each lesson has an action and an owner

## Suggested next steps
- `/milestone-review`
