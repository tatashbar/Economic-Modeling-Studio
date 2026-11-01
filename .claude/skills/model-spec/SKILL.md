---
name: model-spec
description: "Writes the model specification: equations, timing, closures, steady state, shocks, observables and known limitations."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /model-spec — Model Spec

**Category:** Scoping & Design · **Primary agent:** `modeling-methodology-specialist`

Writes the model specification: equations, timing, closures, steady state, shocks, observables and known limitations.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - docs/models/<name>/model-brief.md
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `modeling-methodology-specialist` — primary agent; coordinates the work and integrates results
- `open-economy-dsge-specialist` — Builds small open-economy DSGE models
- `semi-structural-gap-modeler` — Builds quarterly projection and semi-structural gap models
- `deep-learning-architect` — Designs deep learning architectures for macro-financial data

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Select the specialists for the model class and have them draft section by section
2. Define notation, timing conventions and units; list all equations and the closure
3. Derive the steady state and the log-linearization (or the architecture and loss for AI models)
4. List shocks, observables, parameters and identification concerns
5. State known limitations and non-purposes

## Output
`docs/models/<name>/model-spec.md`

## Gate / verdict
- Every endogenous variable has an equation; counts of equations and unknowns match
- Steady state is derived or the computation approach is stated

## Suggested next steps
- `/calibration-plan`
- `/data-requirements`
