---
name: build-climate-macro
description: "Builds a climate-macro model: climate-augmented macro or integrated-assessment-style model with damage functions, abatement and carbon pricing."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-climate-macro — Build Climate Macro

**Category:** Build · **Primary agent:** `climate-macro-specialist`

Builds a climate-macro model: climate-augmented macro or integrated-assessment-style model with damage functions, abatement and carbon pricing.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec
   - Emissions and energy data
   - Damage-function evidence
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `climate-macro-specialist` — primary agent; coordinates the work and integrates results
- `carbon-pricing-emissions-specialist` — Analyzes carbon pricing and emissions policy
- `physical-climate-risk-specialist` — Quantifies physical climate risk
- `transition-risk-energy-specialist` — Analyzes energy systems and transition risk
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Choose the structure (climate-augmented DSGE, IAM-style, multi-sector, CGE-linked) with the user
2. Specify emissions, abatement, damage and (if relevant) adaptation blocks; document discounting and damage-function choices
3. Calibrate and test the model against historical emissions and energy intensity
4. Run baseline and policy pathways; test sensitivity to damages, discounting and technology costs
5. Report deep uncertainty as ranges and document limitations
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/climate/<name>/ (+ model.lego.json)`

## Gate / verdict
- Damage-function and discount-rate alternatives shown
- Emissions accounting consistent with the baseline
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/climate-scenario`
- `/carbon-pricing-analysis`
- `/validate-model`
- `/lego-map`
