---
name: build-sfc
description: "Builds a stock-flow consistent model with balance-sheet and transaction matrices and scenario runs."
---
<!-- Generated from .claude/skills/build-sfc/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-sfc — Build SFC

**Category:** Build · **Primary agent:** `sfc-modeler`

Builds a stock-flow consistent model with balance-sheet and transaction matrices and scenario runs.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Flow-of-funds and national accounts data
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `sfc-modeler` — primary agent; coordinates the work and integrates results
- `financial-stability-stress-testing-specialist` — Builds systemic risk and stress-testing frameworks

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Define the transaction-flow and balance-sheet matrices
2. Derive equations and verify stock-flow consistency by construction
3. Calibrate to data and run baseline
4. Run debt, credit and policy shock scenarios
5. Compare dynamics with a DSGE or semi-structural benchmark
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/sfc/<name>/ (+ model.lego.json)`

## Gate / verdict
- Matrices balance
- No redundant-identity violations
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/validate-model`
- `/scenario-analysis`
- `/lego-map`
