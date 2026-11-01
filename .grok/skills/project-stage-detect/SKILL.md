---
name: project-stage-detect
description: "Detects the project's stage (concept, design, build, estimate, validate, operate) from its files and reports gaps."
---
<!-- Generated from .claude/skills/project-stage-detect/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /project-stage-detect — Project Stage Detect

**Category:** Onboarding · **Primary agent:** `project-planning-specialist`

Detects the project's stage (concept, design, build, estimate, validate, operate) from its files and reports gaps.

Arguments: whatever the user wrote after the command name.

## Purpose
Detect where a modeling project stands (concept, design, build, estimate, validate or operate) from the evidence in its files, and list what is missing at each stage and which gate is owed. A stage is claimed only when its evidence exists.

**Use it when** starting a session on an existing project, before a gate check, or when the user is unsure what to do next.

**Do not use it when** the stage is known and the user wants to proceed.

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
   - Include lego manifests and their brick validation status
2. Map artifacts to stages: Concept (brief) → Design (spec, calibration plan, data requirements) → Build (code, tests) → Estimate (results) → Validate (validation report) → Operate (releases, forecast rounds)
3. List missing artifacts per stage and the gate each stage owes
4. Write the detected stage to `production/stage.txt` after the user confirms

## Checkpoints with the user
- Before writing the stage file

## Common pitfalls
- Claiming a stage from file names without checking content
- Skipping earlier-stage gaps

## Output
`production/stage.txt`

The stage file records the detected stage; the report in conversation lists evidence and gaps per stage.

## Gate / verdict
- Stage is only claimed if its evidence files exist
- Gaps in earlier stages are listed even when later artifacts exist

## Suggested next steps
- `/gate-check`
- `/help`
