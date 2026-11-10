---
name: translate-model
description: "Translates a model definition (Dynare, IRIS, RISE, GAMS, GEMPACK, AMPL, TROLL, EViews model, MATLAB or Python model code) to another tool, matching steady state, solution, IRFs, moments or benchmark solutions."
---
<!-- Generated from .claude/skills/translate-model/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /translate-model — Translate Model

**Category:** Code Translation · **Primary agent:** `model-code-translation-specialist`

Translates a model definition (Dynare, IRIS, RISE, GAMS, GEMPACK, AMPL, TROLL, EViews model, MATLAB or Python model code) to another tool, matching steady state, solution, IRFs, moments or benchmark solutions.

Arguments: whatever the user wrote after the command name.

## Purpose
Move an economic model, not just its code, to another tool: a Dynare model to Python or Julia, an IRIS projection model to Python, a GAMS CGE model to Pyomo, GAMSPy or JuMP, a GEMPACK model to GAMS, a Python model to Dynare. The skill checks the model at each level (equations, steady state, determinacy, solution, IRFs and moments, estimation or scenarios; for CGE, benchmark replication and reference shocks), so a translation that runs but solves a different model is caught. The output is the translated model with its comparison results and a lego manifest.

**Use it when** the object to translate is a model definition whose solution must be reproduced.

**Do not use it when** the code is data preparation or estimation only (`/translate-code` with the statistical translator), or when the model should be rebuilt from its specification rather than translated (`/build-dsge`, `/build-cge`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Model files (with any included files, steady-state files, data and calibration files)
   - Target tool
   - Reference results: the source's steady state, eigenvalues, IRFs, moments, solutions or scenario outputs
   If reference results are `ABSENT` and the source cannot be run here, equivalence is **`NOT ASSESSED — NO REFERENCE OUTPUTS`**.
2. **Check confidentiality.** Identify the classification of the model and its data (`.claude/docs/confidentiality-and-ai-use.md`); licensed databases such as GTAP are never copied or shared.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `model-code-translation-specialist` — primary agent; translates the model and runs the level-by-level checks
- `source-code-analyst` — Writes the model out as equations with timing and transformations
- `translation-equivalence-auditor` — Compares results independently and gives the verdict
- `matlab-dynare-engineer` — Runs the Dynare, IRIS or MATLAB source and reads its expanded model
- `python-julia-engineer` — Engineers the Python or Julia target
- `perturbation-solution-specialist` — Checks solutions, determinacy and higher-order approximations
- `cge-modeling-specialist` — Checks CGE closures, benchmark replication and levels forms of linearized models
- `symbolic-derivation-specialist` — Derives and checks equations, steady states and Jacobians symbolically

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Target solution method | same algorithm as the source; a different algorithm shown to give the same solution | Ease of matching |
| Steady state | analytical; numerical with the source's starting values | Which steady state is found |
| Representation | levels; logs; linearized percentage changes | Comparability of results and size of shocks that match |
| Checks | steady state and IRFs; plus moments; plus estimation or scenario outputs | Strength of evidence |

## Workflow
1. Run `python tools/translate.py plan <model-folder> --to <target>`; extract the expanded model from the source where possible (Dynare writes it; GAMS can list equations).
2. The source-code analyst writes the equations with timing, transformations, parameters and shocks into `behavior-spec.md`.
3. Translate the model; reproduce the steady state; compare values and residuals.
4. Reproduce determinacy and the solution (eigenvalues, decision rules); then IRFs and moments with the same normalization and settings.
5. For CGE and optimization models: zero-shock benchmark replication, Walras check, model and solver status, then reference shocks; for linearized GEMPACK sources, compare small shocks exactly and large shocks within the multi-step accuracy.
6. Estimation or scenarios last, with priors, data and options carried over.
7. Compare with `python tools/translate.py compare`, write the construct log and the report; register a lego manifest for the translated model (`python tools/lego.py new`).

## Checkpoints with the user
- After the equations: confirm the model as written out
- After the steady state and solution: review differences before IRFs and scenarios

## Common pitfalls
- Timing shifted by one period; log and level variables mixed
- Another steady state found by a numerical solver
- IRFs compared with different shock sizes or normalizations; simulated against theoretical moments
- Linearized and levels models compared under large shocks
- Dynare macro code translated instead of the expanded model

## Output
`translations/<name>-to-<target>/` and the translated model under `models/<family>/<name>/` once approved

The workspace holds the behavior spec (equations), the translated model, comparisons by level, the construct log, the equivalence report and the translation report.

## Gate / verdict
- Steady state, determinacy, IRFs and moments (or benchmark and reference solutions) match within tolerance, or differences explained
- Verdict from the `translation-equivalence-auditor`

## Suggested next steps
- `/validate-model`
- `/lego-map`
- `/model-card`
