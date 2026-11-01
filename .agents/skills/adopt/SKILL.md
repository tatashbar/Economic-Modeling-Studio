---
name: adopt
description: "Brings an existing model or codebase into the studio: inventories it, reverse-documents it and plans validation and migration."
---
<!-- Generated from .claude/skills/adopt/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /adopt — Adopt

**Category:** Onboarding · **Primary agent:** `modeling-methodology-specialist`

Brings an existing model or codebase into the studio: inventories it, reverse-documents it and plans validation and migration.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Existing model code/documents at the given path
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `modeling-methodology-specialist` — primary agent; coordinates the work and integrates results
- `reproducibility-engineer` — Guarantees reproducibility
- `technical-documentation-specialist` — Writes technical documentation
- `model-validation-specialist` — Performs independent model validation
- `matlab-dynare-engineer` — Engineers MATLAB, Dynare, IRIS, RISE and Octave codebases; legacy model maintenance and migration

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Inventory files, languages, dependencies, data and entry points
2. Reverse-document equations, assumptions and parameters from the code; flag undocumented behavior
3. Run the model if possible and capture baseline outputs as the reference
4. Rate model risk level and produce a gap list against studio standards
5. Propose a prioritized adoption plan (document, test, validate, migrate)
6. Draft a lego manifest of the existing model (`/lego-map`) so its components, interfaces and simultaneous blocks are explicit before any change

## Output
`docs/models/<model>/adoption-report.md`

## Gate / verdict
- Baseline outputs are captured before any code is changed

## Suggested next steps
- `/validate-model`
- `/model-card`
