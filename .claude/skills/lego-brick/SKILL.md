---
name: lego-brick
description: "Creates a new brick spec for the catalog: purpose, ports (with units and timing), stubs, slot, frequency and bridge, and the checks it must pass."
argument-hint: "[brick id and purpose]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /lego-brick — Lego Brick

**Category:** Lego (Modular Models) · **Primary agent:** `modeling-methodology-specialist`

Creates a new brick spec for the catalog: purpose, ports (with units and timing), stubs, slot, frequency and bridge, and the checks it must pass.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - The component's purpose and, if it exists, its specification or code
   - `lego/ports.json`
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `modeling-methodology-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense
- `python-julia-engineer` — Engineers Python, Julia and R modeling code

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Ask what the brick does, which variables it needs and produces, and at which frequency
2. Reuse port names from `lego/ports.json`. For a new variable, agree the name, unit and description with the user and add it to `lego/ports.json`
3. For each required input, decide: hard requirement, or a stub with a documented fallback. For each lag, state whether the dependence is on the previous period
4. Pick a slot if the brick is an alternative to another (monetary rule, sectoral structure). A different frequency from the usual core needs a bridge note
5. List the checks the brick must pass (identities, calibration targets, neutral-attachment test)
6. Write `lego/catalog/<id>.json` after approval, then verify with `python tools/lego.py catalog`. If the component itself still has to be built, point to the matching `/build-*` command

## Output
`lego/catalog/<id>.json (and lego/ports.json if new ports are added)`

## Gate / verdict
- Every port has a unit
- Every requirement without a stub is intentional
- The spec loads (`catalog` lists it)

## Suggested next steps
- `/lego-add`
- `/lego-map`
