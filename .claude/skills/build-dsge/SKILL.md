---
name: build-dsge
description: "Builds a DSGE model (small, medium or large) from approved spec: derivation, code, solution, tests, IRFs."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-dsge — Build DSGE

**Category:** Build · **Primary agent:** `open-economy-dsge-specialist`

Builds a DSGE model (small, medium or large) from approved spec: derivation, code, solution, tests, IRFs.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec
   - Calibration plan
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `open-economy-dsge-specialist` — primary agent; coordinates the work and integrates results
- `perturbation-solution-specialist` — Solves DSGE models by perturbation (1st-3rd order), pruning, and verifies determinacy and accuracy
- `matlab-dynare-engineer` — Engineers MATLAB, Dynare, IRIS, RISE and Octave codebases; legacy model maintenance and migration
- `financial-frictions-dsge-specialist` — Builds DSGE models with financial frictions
- `symbolic-derivation-specialist` — Derives and verifies model equations with computer algebra
- `ipf-micro-specialist` — Builds microfounded IPF models with FX intervention, capital flow rules and occasionally binding external constraints

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Implement the model in the chosen toolchain (Dynare/Julia/Python) with a clean parameter block
2. Compute steady state; verify residuals and Blanchard-Kahn conditions
3. Solve at the chosen order; check accuracy with Euler errors
4. Produce IRFs for standard shocks; compare to spec expectations
5. Write tests and hand over to estimation and validation
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/dsge/<name>/ (+ model.lego.json)`

## Gate / verdict
- Determinacy verified
- Steady-state ratios match targets
- Accuracy report present
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/estimate-dsge`
- `/validate-model`
- `/lego-map`
