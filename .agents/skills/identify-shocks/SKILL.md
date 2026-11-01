---
name: identify-shocks
description: "Constructs and tests structural shock series (narrative, high-frequency, proxy) and documents identification."
---
<!-- Generated from .claude/skills/identify-shocks/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /identify-shocks — Identify Shocks

**Category:** Estimation · **Primary agent:** `shock-identification-specialist`

Constructs and tests structural shock series (narrative, high-frequency, proxy) and documents identification.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Event/high-frequency data
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `shock-identification-specialist` — primary agent; coordinates the work and integrates results
- `nlp-text-as-data-specialist` — Turns text into economic data
- `var-vecm-specialist` — Builds VAR, SVAR and VECM models

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Define the shock concept and the exclusion assumption
2. Build the series; test strength and exogeneity
3. Cross-check against known events and alternative series
4. Archive the series with documentation

## Output
`data/processed/shocks/<shock>.csv and docs/models/<name>/shock-note.md`

## Gate / verdict
- Instrument strength and exogeneity tests reported

## Suggested next steps
- `/local-projections`
- `/estimate-var`
