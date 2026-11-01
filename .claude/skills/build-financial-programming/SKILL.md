---
name: build-financial-programming
description: "Builds an integrated financial-programming framework consistent across real, fiscal, monetary and external sectors."
argument-hint: "[country]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-financial-programming — Build Financial Programming

**Category:** Build · **Primary agent:** `financial-programming-specialist`

Builds an integrated financial-programming framework consistent across real, fiscal, monetary and external sectors.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Data sheet with sectoral accounts
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `financial-programming-specialist` — primary agent; coordinates the work and integrates results
- `balance-of-payments-specialist` — Builds balance-of-payments and international investment position analyses
- `debt-sustainability-analyst` — Builds debt sustainability analyses
- `rmsm-three-gap-modeler` — Builds revised minimum standard, three-gap and growth-financing models for low-income and developing economies

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Lay out sectoral accounts and identities; implement in code with assertions
2. Specify behavioral relationships and their sources
3. Build baseline and alternative scenarios with financing gaps
4. Run consistency checks across fiscal, monetary, BoP and national accounts
5. Document assumptions for program-design use
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/financial-programming/<country>/ (+ model.lego.json)`

## Gate / verdict
- All sectoral identities close
- Behavioral parameters are sourced
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/debt-sustainability`
- `/validate-model`
- `/lego-map`
