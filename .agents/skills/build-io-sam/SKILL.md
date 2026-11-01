---
name: build-io-sam
description: "Builds input-output, supply-use and SAM frameworks with multipliers, linkages, multi-regional and environmentally extended extensions."
---
<!-- Generated from .claude/skills/build-io-sam/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-io-sam — Build IO SAM

**Category:** Build · **Primary agent:** `input-output-sam-specialist`

Builds input-output, supply-use and SAM frameworks with multipliers, linkages, multi-regional and environmentally extended extensions.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Supply-use or input-output tables
   - National accounts for the base year
   - Classification concordances
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `input-output-sam-specialist` — primary agent; coordinates the work and integrates results
- `national-accounts-specialist` — Specializes in national accounts and macro statistics
- `production-networks-specialist` — Models production networks and supply chains
- `trade-gvc-specialist` — Models trade and global value chains
- `carbon-pricing-emissions-specialist` — Analyzes carbon pricing and emissions policy

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Choose the framework (national IO, supply-use, SAM, multi-regional) and the sector classification; ask the user to approve
2. Construct and balance the tables (RAS/GRAS/cross-entropy where needed); automate balance checks
3. Compute Leontief/Ghosh inverses, multipliers, linkages and, if relevant, value-added and environmental extensions
4. Run impact analyses and state the fixed-coefficient limitations alongside results
5. Document concordances, data sources, adjustments and reproduction steps
6. Register the model as a lego set (`/lego-map`; a stand-alone table uses the `core-io-leontief` baseplate): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/io-sam/<name>/ (+ model.lego.json)`

## Gate / verdict
- Row and column totals balance to tolerance
- Hawkins-Simon condition verified
- Adjustments and concordances documented
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/build-cge`
- `/supply-chain-shock`
- `/validate-model`
- `/lego-map`
