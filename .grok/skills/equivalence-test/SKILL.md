---
name: equivalence-test
description: "Tests whether translated code reproduces the source: reference outputs, tolerances, cell-by-cell comparison, edge cases, diagnosis of differences and a verdict."
---
<!-- Generated from .claude/skills/equivalence-test/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /equivalence-test — Equivalence Test

**Category:** Code Translation · **Primary agent:** `translation-equivalence-auditor`

Tests whether translated code reproduces the source: reference outputs, tolerances, cell-by-cell comparison, edge cases, diagnosis of differences and a verdict.

Arguments: whatever the user wrote after the command name.

## Purpose
Show, with evidence, whether two codes compute the same thing: a translation and its source, two implementations of a model, or a code before and after refactoring. Outputs are compared at full precision with tolerances fixed in advance (`python tools/translate.py compare`), differences are traced to their first point of divergence, and the auditor issues a verdict. The output is an equivalence report.

**Use it when** a translation or refactor is finished or disputed, or two implementations of the same model disagree.

**Do not use it when** there are no reference outputs and no way to produce them; record `NOT ASSESSED — NO REFERENCE OUTPUTS` instead.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Reference outputs (from the source)
   - Translated outputs (from a clean-start run of the translation)
   - Tolerances (from the plan, or agreed now before comparing)
   If reference or translated outputs are `ABSENT`, that comparison is **`NOT ASSESSED — NO DATA`**: name what is missing and which skill produces it.
2. **Check confidentiality.** Identify the classification of the outputs (`.claude/docs/confidentiality-and-ai-use.md`).
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `translation-equivalence-auditor` — primary agent; designs the test, compares and gives the verdict
- `replication-auditor` — Checks the provenance of reference outputs and the clean-start run
- `reproducibility-engineer` — Sets up the clean environment for both runs

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Tolerances | exact; relative 1e-6; 1e-4 for solvers; by output | Pass criteria |
| Matching rows | by order; by key columns | Robustness to sorting differences |
| Random draws | source draws read by the target; distribution tests | What "equal" means for simulations |
| Edge cases | normal run only; plus constructed edge inputs | Coverage |

## Workflow
1. Fix the outputs to compare and the tolerances before looking at results; record them.
2. Check provenance of reference outputs (software, version, date, command) and run the translation from a clean start.
3. Run `python tools/translate.py compare <reference-dir> <translated-dir> [--key id year] [--rtol R] [--atol A] --out equivalence/report.md`. Files are matched by name; use `--pair ref.csv=new.csv` when names differ.
4. For each difference, compare intermediate outputs in order to find where the codes diverge; classify the cause (translation error, default, numerical tolerance, library version, source bug).
5. Run edge cases through both codes where the source can be run.
6. If the comparison is part of a translation, run `python tools/translate.py verify-source <workspace>`.
7. Write the verdict with its evidence.

## Checkpoints with the user
- Before comparing: approve outputs and tolerances
- After comparing: review each explained difference

## Common pitfalls
- Changing tolerances after seeing the differences
- Comparing display-rounded outputs
- Treating any difference below the eye's resolution as rounding without finding the cause

## Output
`translations/<name>-to-<target>/equivalence/report.md` (or `validation/<model>/equivalence-report.md` outside a translation)

The report gives tolerances, per-file results with maximum differences, the diagnosis of each difference and the verdict.

## Gate / verdict
- EQUIVALENT, EQUIVALENT WITH EXPLAINED DIFFERENCES, NOT EQUIVALENT, or NOT ASSESSED

## Suggested next steps
- `/validate-model`
- `/replicate`
- `/model-release`
