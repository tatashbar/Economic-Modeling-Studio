---
name: code-review
description: "Reviews model and pipeline code for correctness, numerical soundness, reproducibility and standards compliance."
---
<!-- Generated from .claude/skills/code-review/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /code-review — Code Review

**Category:** Validation & QA · **Primary agent:** `python-julia-engineer`

Reviews model and pipeline code for correctness, numerical soundness, reproducibility and standards compliance.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Code at path
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `python-julia-engineer` — primary agent; coordinates the work and integrates results
- `numerical-methods-specialist` — Specializes in numerical methods
- `reproducibility-engineer` — Guarantees reproducibility

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Read the code against the spec and `.claude/rules/` for the path
2. Check numerics: tolerances, conditioning, units, timing conventions
3. Check reproducibility: seeds, versions, hard-coded paths and parameters
4. Check tests: coverage of identities, steady state and edge cases
5. List findings by severity with concrete fixes

## Output
`validation/code-reviews/<name>.md`

## Gate / verdict
- No hard-coded parameters or paths in model code; tests exist for identities

## Suggested next steps
- `/validate-model`
