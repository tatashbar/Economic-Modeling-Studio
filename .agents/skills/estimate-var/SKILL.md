---
name: estimate-var
description: "Estimates VAR/SVAR/VECM models with diagnostics, identification and impulse responses."
---
<!-- Generated from .claude/skills/estimate-var/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /estimate-var — Estimate VAR

**Category:** Estimation · **Primary agent:** `var-vecm-specialist`

Estimates VAR/SVAR/VECM models with diagnostics, identification and impulse responses.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Data sheet
   - Identification scheme
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `var-vecm-specialist` — primary agent; coordinates the work and integrates results
- `shock-identification-specialist` — Identifies structural shocks
- `data-quality-seasonal-specialist` — Ensures data quality

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Test integration order and cointegration; choose lag length and deterministic terms
2. Estimate the reduced form; run stability and residual diagnostics
3. Apply identification and compute IRFs, FEVD with bands
4. Run robustness under an alternative identification or specification

## Output
`docs/models/<name>/var-results.md`; code and settings in `models/econometrics/<name>/`

## Gate / verdict
- Stability and residual tests reported
- Robustness to identification shown

## Suggested next steps
- `/validate-model`
- `/scenario-analysis`
