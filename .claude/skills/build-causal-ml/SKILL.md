---
name: build-causal-ml
description: "Builds a causal machine-learning analysis (double ML, causal forests) with identification argument and sensitivity checks."
argument-hint: "[treatment and outcome]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-causal-ml — Build Causal ML

**Category:** Build (AI) · **Primary agent:** `causal-ml-specialist`

Builds a causal machine-learning analysis (double ML, causal forests) with identification argument and sensitivity checks.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Data sheet
   - Identification argument
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `causal-ml-specialist` — primary agent; coordinates the work and integrates results
- `panel-causal-inference-specialist` — Panel econometrics and causal inference
- `interpretable-ml-specialist` — Makes AI models explainable

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Write the identification argument and assumptions before touching the data
2. Implement with cross-fitting; compare to a standard econometric estimate
3. Estimate heterogeneous effects and test stability
4. Run sensitivity to unobserved confounding and specification
5. Write the result in terms of what the evidence supports and what it does not
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/ai/<name>-causal/ (+ model.lego.json)`

## Gate / verdict
- Identification assumptions stated
- Comparison with a conventional estimate
- Sensitivity analysis present
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/validate-model`
- `/technical-note`
- `/lego-map`
