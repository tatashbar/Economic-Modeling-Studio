---
name: translation-plan
description: "Plans a code translation: file mapping in dependency order, target libraries, agents, idioms and pitfalls for the language pair, decisions, tolerances and the equivalence test."
---
<!-- Generated from .claude/skills/translation-plan/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /translation-plan — Translation Plan

**Category:** Code Translation · **Primary agent:** `code-translation-architect`

Plans a code translation: file mapping in dependency order, target libraries, agents, idioms and pitfalls for the language pair, decisions, tolerances and the equivalence test.

Arguments: whatever the user wrote after the command name.

## Purpose
Produce an approved plan before any target code is written. `python tools/translate.py plan` creates the workspace and a draft with the file mapping, the agent for each file, the pitfalls of the source and target languages, the idioms for the pair (`python tools/translate.py idioms --from <source> --to <target>`), checks on the toolchain and on whether the source can be run here, and the equivalence plan. The architect completes it with target libraries, decisions and effort.

**Use it when** a translation is being scoped, costed or compared across targets (for example Python against Julia for a MATLAB model).

**Do not use it when** the plan is to be executed right away; `/translate-code` includes this step.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Source folder
   - Target language or software (or two to compare)
   If either is `ABSENT`, ask for it and show `python tools/translate.py languages --target-only`.
2. **Check confidentiality.** Identify the classification of the code and data (`.claude/docs/confidentiality-and-ai-use.md`).
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `code-translation-architect` — primary agent; writes and defends the plan
- `source-code-analyst` — Confirms the inventory and the outputs that define success
- `statistical-code-translation-specialist` — Advises on statistical libraries and defaults
- `model-code-translation-specialist` — Advises on model, solver and optimization libraries
- `legacy-code-translation-specialist` — Advises on legacy arithmetic, layouts and spreadsheets
- `translation-equivalence-auditor` — Sets the tolerances and the equivalence plan

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Target | the approved toolchains that fit the code | Libraries, effort, who can maintain it |
| Fidelity | faithful then idiomatic; faithful only; idiomatic rewrite | Strength of the equivalence evidence |
| Structure | one file per source file; package | Ease of checking against maintainability |
| Tolerances | by output type | Pass criteria |

## Workflow
1. Run `python tools/translate.py plan <source> --to <target> [--name <name>]`.
2. Review the inventory with the source-code analyst; agree the outputs that define success.
3. Choose target libraries for each construct family; list the defaults that must be set explicitly.
4. Set tolerances and the handling of random draws with the equivalence auditor.
5. Estimate effort by file and flag what may not translate (for example regime-switching solvers, proprietary toolboxes).
6. Present the plan and the decisions; record the user's choices in `plan.md`.

## Checkpoints with the user
- Approve the plan, decisions and tolerances before any translation

## Common pitfalls
- Choosing a target library whose defaults cannot be set to match the source
- No plan for reference outputs when the source software is not available
- Tolerances left to be decided after the comparison

## Output
`translations/<name>-to-<target>/plan.md`

The plan holds the summary, checks, decisions, file mapping, constructs to check, pitfalls, idioms, the equivalence plan and the sign-off list.

## Gate / verdict
- Plan approved by the user, with decisions and tolerances recorded

## Suggested next steps
- `/translate-code`
- `/translate-model`
