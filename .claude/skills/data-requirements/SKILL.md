---
name: data-requirements
description: "Defines data requirements and checks availability, vintages, confidentiality classification and quality for a model."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /data-requirements — Data Requirements

**Category:** Scoping & Design · **Primary agent:** `data-engineer`

Defines data requirements and checks availability, vintages, confidentiality classification and quality for a model.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - docs/models/<name>/model-spec.md
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `data-engineer` — primary agent; coordinates the work and integrates results
- `national-accounts-specialist` — Specializes in national accounts and macro statistics
- `data-governance-metadata-specialist` — Owns data governance and metadata
- `survey-microdata-specialist` — Works with household and firm survey microdata

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. List the observables, frequency, sample and concept for each series
2. Check availability and source; classify confidentiality class
3. Assess quality (revisions, breaks, seasonality) and propose treatments
4. Produce a data sheet and pipeline plan

## Output
`docs/models/<name>/data-sheet.md`

## Gate / verdict
- Each series has a source, definition, classification and quality note

## Suggested next steps
- `/calibration-plan`
- `/build-dsge`
