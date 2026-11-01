---
name: project-stage-detect
description: "Detects the project's stage (concept, design, build, estimate, validate, operate) from its files and reports gaps."
argument-hint: "[none]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /project-stage-detect — Project Stage Detect

**Category:** Onboarding · **Primary agent:** `project-planning-specialist`

Detects the project's stage (concept, design, build, estimate, validate, operate) from its files and reports gaps.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - models/
   - docs/
   - validation/
   - forecasts/
   - production/
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `project-planning-specialist` — primary agent; coordinates the work and integrates results

## Workflow
1. Scan `models/`, `data/`, `docs/`, `validation/`, `forecasts/` and `production/` for artifacts
2. Map artifacts to stages: Concept (brief) → Design (spec, calibration plan, data requirements) → Build (code, tests) → Estimate (results) → Validate (validation report) → Operate (releases, forecast rounds)
3. List missing artifacts per stage and the gate each stage owes
4. Write the detected stage to `production/stage.txt` after the user confirms

## Output
`production/stage.txt`

## Gate / verdict
- Stage is only claimed if its evidence files exist

## Suggested next steps
- `/gate-check`
- `/help`
