---
name: build-abm
description: "Builds an agent-based model with ODD documentation, calibration, validation and experiment design."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-abm — Build ABM

**Category:** Build · **Primary agent:** `agent-based-modeling-specialist`

Builds an agent-based model with ODD documentation, calibration, validation and experiment design.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec with agent rules
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `agent-based-modeling-specialist` — primary agent; coordinates the work and integrates results
- `simulation-based-inference-specialist` — Estimates complex models with neural simulation-based inference
- `hpc-gpu-engineer` — Engineers high-performance computing

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Document the model with the ODD protocol before coding
2. Implement with explicit random-seed management and unit tests for agent rules
3. Calibrate by indirect inference or SBI; check stylized facts
4. Design experiments and run with enough replications for stable estimates
5. Report sensitivity to parameters and seeds
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/abm/<name>/ (+ model.lego.json)`

## Gate / verdict
- ODD complete
- Stylized-facts validation and seed-robustness reported
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/validate-model`
- `/policy-simulation`
- `/lego-map`
