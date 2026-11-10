---
name: translate-code
description: "Translates a code folder from one language or software to another (Stata, R, Python, MATLAB, Dynare, EViews, SAS, GAMS, Fortran, COBOL and more), with specialist agents and an equivalence test against the source."
---
<!-- Generated from .claude/skills/translate-code/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /translate-code — Translate Code

**Category:** Code Translation · **Primary agent:** `code-translation-architect`

Translates a code folder from one language or software to another (Stata, R, Python, MATLAB, Dynare, EViews, SAS, GAMS, Fortran, COBOL and more), with specialist agents and an equivalence test against the source.

Arguments: whatever the user wrote after the command name.

## Purpose
Take a folder of model or analysis code, written in one or several languages, and produce a working translation in the target language that reproduces the source's outputs. A team of agents analyzes the source, plans the work, translates file by file in dependency order, and an independent auditor compares the outputs of both codes. The output is a translation workspace with the translated code, a construct log of everything that did not translate one-to-one, an equivalence report and a translation report.

**Use it when** code must move to another language or software: for maintenance, licensing, speed, teaching, or to combine models written in different tools.

**Do not use it when** only an inventory is needed (`/code-inventory`), the code is a single model definition file whose solution must be matched (`/translate-model` does this with model-specific checks), or the outputs of an existing translation only need checking (`/equivalence-test`).

## Supported languages and software
Run `python tools/translate.py languages` for the list, or read `docs/code-translation.md`. In short:
- **Statistical and econometric:** Stata, R, Python, SAS, SPSS, EViews, RATS, gretl, Ox, LIMDEP/NLOGIT, TSP
- **Numerical:** Python, Julia, MATLAB, Octave, Scilab, Mathematica, Maple, C and C++
- **Model languages:** Dynare, IRIS, RISE, TROLL, GEMPACK
- **Optimization and CGE:** GAMS, AMPL (and Pyomo, GAMSPy, JuMP as targets)
- **Bayesian:** Stan, JAGS, BUGS
- **Legacy and data:** COBOL, Fortran, GAUSS, Excel formulas and VBA, FAME/AREMOS, SQL

Targets: Python, R, Julia, MATLAB, Octave, Dynare, IRIS, Stata, EViews, SAS, gretl, GAMS, GEMPACK, Fortran, C/C++, Stan and SQL, limited to the toolchains approved in `studio-config.yaml` unless the user confirms otherwise.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Source folder: a path the user gives, or a folder the user uploads (copy uploads to `translations/incoming/<name>/`, which git ignores)
   - Target language or software
   - Reference outputs: produced by running the source here, or files the user supplies
   If the source folder or the target is `ABSENT`, ask for it: show the list of supported languages and let the user choose the target. If reference outputs are `ABSENT` and the source cannot be run here, the translation can proceed but equivalence is **`NOT ASSESSED — NO REFERENCE OUTPUTS`**: say so in the plan and the report.
2. **Check confidentiality.** Source code and the data next to it can be confidential. Identify their classification (`.claude/docs/confidentiality-and-ai-use.md`) before reading them; restricted code or data never go into prompts or external services, and are not copied into the studio.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `code-translation-architect` — primary agent; plans, assigns and integrates the work, and signs off the package
- `source-code-analyst` — Maps the source and writes down what each file computes
- `statistical-code-translation-specialist` — Translates statistical and econometric code
- `model-code-translation-specialist` — Translates model and numerical code
- `legacy-code-translation-specialist` — Translates legacy code, spreadsheets and database scripts
- `translation-equivalence-auditor` — Tests equivalence independently and gives the verdict
- `matlab-dynare-engineer` — Engineers MATLAB, Dynare, IRIS and Octave code
- `python-julia-engineer` — Engineers Python, Julia and R code
- `reproducibility-engineer` — Pins environments and makes the package run with one command

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Fidelity | faithful first, then idiomatic; faithful only; idiomatic rewrite | Whether equivalence can be shown step by step |
| Target structure | one file per source file; package with modules | Ease of side-by-side checking against maintainability |
| Target libraries | for example statsmodels or linearmodels or pyfixest; fixest or plm; Pyomo or GAMSPy or JuMP | Which defaults must be overridden to match the source |
| Reference outputs | run the source here; user-supplied outputs; published results | Strength of the equivalence evidence |
| Tolerances | exact; relative 1e-6; 1e-4 for solvers; distribution tests | Pass criteria |
| Bugs found in the source | keep and log; fix after equivalence | Whether the first translation can be proven equivalent |

## Workflow
1. **Intake.** Confirm the source folder and target; copy uploads to `translations/incoming/<name>/`. Run `python tools/translate.py plan <source> --to <target> [--name <name>]`. It creates `translations/<name>-to-<target>/` with the inventory, the source fingerprints, a draft `plan.md`, `construct-log.md` and folders for target code and outputs. The source is never changed.
2. **Analysis** (`source-code-analyst`). Confirm the inventory by reading the code, add dependencies the scan missed, write `behavior-spec.md` (inputs, outputs, state, computation and defaults of each file) and agree the outputs that define success.
3. **Plan approval.** The architect completes `plan.md`: file mapping, agents, target libraries, decisions, tolerances and the equivalence plan. **Stop for the user's approval.**
4. **Reference outputs.** Run the source where the software exists, writing full-precision outputs to `reference-outputs/`; otherwise copy the outputs the user supplies and record their provenance.
5. **Translation** (in dependency order; independent files in parallel). Statistical, model and legacy translators write to `target/` only. Every target file starts with a header naming its source file; every construct that does not translate one-to-one goes in `construct-log.md`. Target code follows the studio rules for its language (`.claude/rules/`).
   - Data steps are checked before estimation, steady states before solutions, record layouts before logic
6. **Run and compare** (`translation-equivalence-auditor`). Run the translated package from a clean start into `translated-outputs/`; run `python tools/translate.py compare reference-outputs translated-outputs --out equivalence/report.md` (add `--key` for keyed tables); trace each difference to its cause with the translators.
7. **Sign-off.** `python tools/translate.py verify-source translations/<name>-to-<target>`; write `translation-report.md` (scope, mapping, equivalence verdict and evidence, construct log summary, what was not assessed, how to run). Offer the idiomatic pass, re-tested against the same reference outputs.

## Checkpoints with the user
- After intake: confirm source, target, purpose and confidentiality
- After analysis: approve the plan, the outputs to compare and the tolerances
- After comparison: review differences and accept or reject the explanations

## Common pitfalls
- Translating line by line without the behavior spec
- Changing behavior during the faithful pass ("while we are here")
- Comparing rounded or display outputs; comparing coefficients but not standard errors or samples
- Comparing random draws across software as if seeds carried over
- Missing dependencies: ado-files, toolboxes, GAUSS libraries, copybooks, Excel links, Dynare macros

## Output
`translations/<name>-to-<target>/`

The workspace holds `inventory.md`, `source-manifest.json`, `behavior-spec.md`, `plan.md`, `target/` (translated code with a README and a one-command run), `reference-outputs/`, `translated-outputs/`, `construct-log.md`, `equivalence/report.md` and `translation-report.md`.

## Gate / verdict
- EQUIVALENT, EQUIVALENT WITH EXPLAINED DIFFERENCES, NOT EQUIVALENT, or NOT ASSESSED (with what is missing), from the `translation-equivalence-auditor`
- The source is unchanged (`verify-source` passes)
- Every source file is translated or excluded with a reason

## Suggested next steps
- `/equivalence-test`
- `/code-review`
- `/adopt`
- `/validate-model`
- `/model-card`
