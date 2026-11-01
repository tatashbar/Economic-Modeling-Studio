---
name: build-neural-solver
description: "Builds a neural-network solver for a high-dimensional or heterogeneous-agent model and certifies its accuracy."
---
<!-- Generated from .claude/skills/build-neural-solver/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-neural-solver — Build Neural Solver

**Category:** Build (AI) · **Primary agent:** `neural-solver-specialist`

Builds a neural-network solver for a high-dimensional or heterogeneous-agent model and certifies its accuracy.

Arguments: whatever the user wrote after the command name.

## Purpose
Build a neural-network solver for an economic model too high-dimensional for grid methods (many states, heterogeneous agents, occasionally binding constraints) and certify its accuracy. The output is a solver whose residuals are reported on held-out states and which matches a classical solution on a test case where both can be computed, plus an optional fast surrogate for estimation or policy loops.

**Use it when** global solutions are needed in high dimensions, or a fast surrogate is needed inside estimation or optimization.

**Do not use it when** perturbation or grid methods are adequate (`/build-dsge`, `/build-hank`), or the model's equilibrium conditions are not yet verified.

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Loss | Euler residuals, Bellman residuals, all equilibrium conditions | What accuracy means |
| State sampling | ergodic simulation, grids, mixtures | Coverage of relevant states |
| Constraints | Fischer–Burmeister, bounded outputs, penalties | Constraint satisfaction |
| Architecture | MLP, permutation-invariant networks for many agents | Scalability |
| Framework | JAX, PyTorch, Julia | Speed and autodiff |

## Workflow
1. Formulate equilibrium conditions as residual losses (Euler/Bellman/market clearing)
2. Certify on a low-dimensional version with a classical solution
   - Compare policy functions and simulated moments
3. Scale to full dimensionality; track residuals on held-out states
   - Report mean, max and percentile residuals, including tails of the ergodic distribution
4. Handle constraints with smooth complementarity transforms
5. Export a fast surrogate for estimation or policy loops
   - Document the surrogate's accuracy over the parameter range used
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Checkpoints with the user
- After formulation: confirm the conditions and losses
- After certification: confirm accuracy is adequate
- Before surrogate export: confirm the parameter range

## Common pitfalls
- Training residuals reported as accuracy
- States sampled away from the ergodic set
- Constraint violations in rare states ignored
- Surrogates used outside their trained range

## Output
`models/ai/<name>-solver/ (+ model.lego.json)`

The folder holds the solver code, certification results, residual statistics, the surrogate and its accuracy report, and the lego manifest.

## Gate / verdict
- Matches classical solution on the test case
- Held-out residual statistics reported
- Lego manifest passes `python tools/lego.py check`
- Constraint violations are measured and reported
- Results are stable across seeds

## Suggested next steps
- `/validate-model`
- `/estimate-dsge`
- `/lego-map`
