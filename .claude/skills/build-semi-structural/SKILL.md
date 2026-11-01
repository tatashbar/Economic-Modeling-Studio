---
name: build-semi-structural
description: "Builds a small or medium semi-structural gap/projection model with calibration, filters and baseline."
argument-hint: "[country|model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-semi-structural — Build Semi Structural

**Category:** Build · **Primary agent:** `semi-structural-gap-modeler`

Builds a small or medium semi-structural gap/projection model with calibration, filters and baseline.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec
   - Data sheet
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `semi-structural-gap-modeler` — primary agent; coordinates the work and integrates results
- `state-space-kalman-specialist` — Builds state-space models
- `monetary-policy-rules-specialist` — Designs and evaluates monetary policy rules
- `expectations-learning-specialist` — Models expectations formation

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Implement the equations and gap filters; set up code in `models/semi-structural/<name>/`
2. Calibrate or estimate; check steady state and impulse responses against expected signs
3. Create the baseline run and shock-response pack
4. Write tests: steady-state residuals, accounting identities, IRF sign checks
5. Document and hand over to validation
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/semi-structural/<name>/ (+ model.lego.json)`

## Gate / verdict
- Steady state residuals ≈ 0
- IRF signs and magnitudes are plausible and documented
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/validate-model`
- `/forecast-round`
- `/lego-map`
