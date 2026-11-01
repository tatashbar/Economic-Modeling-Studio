---
name: build-neural-solver
description: "Builds a neural-network solver for a high-dimensional or heterogeneous-agent model and certifies its accuracy."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-neural-solver — Build Neural Solver

**Category:** Build (AI) · **Primary agent:** `neural-solver-specialist`

Builds a neural-network solver for a high-dimensional or heterogeneous-agent model and certifies its accuracy.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec
   - Reference solution on a low-dimensional version
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `neural-solver-specialist` — primary agent; coordinates the work and integrates results
- `global-solution-specialist` — Solves models globally
- `hank-specialist` — Builds heterogeneous-agent (HANK) models
- `differentiable-programming-specialist` — Builds differentiable economic models in JAX/PyTorch/Julia

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Formulate equilibrium conditions as residual losses (Euler/Bellman/market clearing)
2. Certify on a low-dimensional version with a classical solution
3. Scale to full dimensionality; track residuals on held-out states
4. Handle constraints with smooth complementarity transforms
5. Export a fast surrogate for estimation or policy loops
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/ai/<name>-solver/ (+ model.lego.json)`

## Gate / verdict
- Matches classical solution on the test case
- Held-out residual statistics reported
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/validate-model`
- `/estimate-dsge`
- `/lego-map`
