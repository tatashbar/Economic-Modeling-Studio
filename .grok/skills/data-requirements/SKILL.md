---
name: data-requirements
description: "Defines data requirements and checks availability, vintages, confidentiality classification and quality for a model."
---
<!-- Generated from .claude/skills/data-requirements/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /data-requirements — Data Requirements

**Category:** Scoping & Design · **Primary agent:** `data-engineer`

Defines data requirements and checks availability, vintages, confidentiality classification and quality for a model.

Arguments: whatever the user wrote after the command name.

## Purpose
Define what data a model needs and check, series by series, whether they exist, where they come from, what they mean, how reliable they are, and how confidential they are. The output is a data sheet and a pipeline plan that prevent late surprises: missing series, mismatched concepts, short samples or data that cannot legally be used.

**Use it when** a model is scoped and its observables and calibration targets are known, or an existing model moves to a new country.

**Do not use it when** the data pipeline already exists and only needs refreshing.

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Sources | national statistics, international databases, private data | Coverage, cost, licensing |
| Frequency | annual, quarterly, monthly | Model design |
| Sample | full history, post-break | Estimation reliability |
| Treatments | seasonal adjustment, splicing, interpolation | Data quality |

## Workflow
1. List the observables, frequency, sample and concept for each series
   - Match each concept to the model variable definition
2. Check availability and source; classify confidentiality class
   - Record licenses and redistribution rights
3. Assess quality (revisions, breaks, seasonality) and propose treatments
4. Produce a data sheet and pipeline plan
   - Note vintages needed for real-time evaluation

## Checkpoints with the user
- After the list: confirm observables and samples
- After quality review: confirm proposed treatments

## Common pitfalls
- Concepts that differ from model definitions (cash versus accrual, gross versus net)
- Licenses checked too late
- Ignoring breaks and rebasing
- No plan for vintages

## Output
`docs/models/<name>/data-sheet.md`

The data sheet lists each series with definition, source, frequency, sample, classification, license, quality notes and proposed treatments, plus the pipeline plan.

## Gate / verdict
- Each series has a source, definition, classification and quality note
- Licenses and redistribution rights are recorded
- Concept mismatches with the model are documented

## Suggested next steps
- `/calibration-plan`
- `/build-dsge`
