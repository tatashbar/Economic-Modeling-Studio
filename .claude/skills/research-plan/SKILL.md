---
name: research-plan
description: "Takes a research note or plan, a short description and data files, turns them into modeling tasks with replication and open-method tracks, runs them and reports results section by section."
argument-hint: "[note path] [data paths] [short description]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /research-plan — Research Plan

**Category:** Scoping & Design · **Primary agent:** `research-note-analyst`

Takes a research note or plan, a short description and data files, turns them into modeling tasks with replication and open-method tracks, runs them and reports results section by section.

Arguments: `$ARGUMENTS`

## Purpose
Start from the documents economists actually have: a research note or work plan (DOCX, PDF, Markdown or text) that describes the questions, the charts wanted and often the method and assumptions already used, plus the spreadsheets that come with it. The skill reads the note, inventories the data, splits the note into analytical tasks, and for each task sets up two tracks: a **replication track** that reproduces the author's method and assumptions, and an **open track** in which the studio proposes the method it would choose with more freedom. It then runs the tasks through the studio's existing skills, reconciles the two tracks, and assembles the results against the note's own sections.

**Use it when** a user brings a note, plan, terms of reference or chart narrative with data and asks the studio to help with the modeling and results.

**Do not use it when** there is a single, well-defined question and no document (`/scope-question`), or an existing model to bring in (`/adopt`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - The research note or plan
   - A short description from the user: what they want back, for whom, by when
   - Data files named in or supplied with the note (optional; tasks without data are marked)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Notes and data that are not public are classified before they are read: keep them outside git (`data/raw/<project>/`), never copy their content into committed files, prompts to external services or logs unless the class allows it, and do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `research-note-analyst` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense
- `modeling-methodology-specialist` — Chooses methods and architecture across model families, sets code and data standards, and resolves technical trade-offs between traditional, structural and AI approaches
- `cross-country-indicators-specialist` — Builds cross-country indicator analyses from panel databases: country groups, constant samples, aggregation, vulnerability thresholds, heatmaps and typologies
- `data-governance-metadata-specialist` — Owns data governance and metadata
- `project-planning-specialist` — Plans scope, sequencing, dependencies and phase gates

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Tracks | replication only, open only, both with reconciliation | Whether the result checks the author's method, challenges it, or both |
| Scope | all sections, priority sections first | Effort and order |
| Freedom in the open track | same data and sample, same data with any method, new data allowed | How far the studio may depart from the note |
| Grouping | as in the note (for example regions), alternative groups, country level | Aggregation and chart design |
| Outputs | charts and tables for the note, technical annex, policy brief | Effort and audience |

## Workflow
1. Read the user's short description; confirm what they want back, the audience and the deadline
2. Read the note with numbered paragraphs (`python tools/intake.py note <file>`; for PDF without a text layer, read it directly)
   - List sections, the result each one asks for, stated methods and assumptions, and open questions, each with its paragraph number
3. Inventory the data (`python tools/intake.py data <file>` for each workbook or CSV)
   - Sheets, layouts, indicators, units, years, vintages, countries, error cells and calculation sheets
   - Map every task to its data; mark gaps `NOT ASSESSED — NO DATA` and name the source that would fill them
   - Read the formulas behind the supplied numbers (`python tools/intake.py formulas <file> --sheet <name>`) and list every place where the method coded differs from the method the note describes (thresholds, baselines, signs, currency, samples); these are findings for the author, not errors to fix silently
4. Write the research brief (`docs/templates/research-brief.md`): task map, assumption list, data map, replication specification and open-track proposal per task, routing to skills, priorities and checkpoints; wait for approval
5. Run the tasks through the studio's skills, in parallel where they are independent
   - Decompositions of debt or other stocks: `/debt-decomposition`
   - Indicator dashboards, heatmaps, shares above thresholds: `/vulnerability-dashboard`
   - Shock scenarios, including probability-weighted scenarios: `/scenario-analysis`, `/fan-chart`
   - Standardized debt stress tests: `/debt-sustainability`
   - Country types and tailored recommendations: `/country-typology`, then `/policy-brief`
   - A new model where a task needs one: `/select-model-class`, then the build command for the family
6. Replication track first: reproduce the supplied spreadsheet numbers within tolerance, then run the open track on the same data and sample
7. Reconcile: for each task compare the two tracks (sign, ranking, size of the gap) and name the assumption that drives each difference; report errors found in the original calculation plainly
8. Assemble the results pack by the note's sections, with the charts and tables each section asked for, the reconciliation and the caveats

## Checkpoints with the user
- After the note is read: confirm the task list, the assumption list and the open questions
- After the research brief: approve tracks, scope, priorities and the freedom given to the open track
- After the replication track: confirm the match with the supplied numbers before the open track is compared
- Before the results pack: review the reconciliation and the caveats

## Common pitfalls
- Building a structural model when the note asks for an accounting exercise, or the reverse
- Silently correcting the author's assumptions in the replication track
- Comparing tracks that use different samples or vintages without saying so
- Trusting the note's description of a calculation without reading the spreadsheet formulas behind it
- Sheets that stack a second block (aggregates, a copy of the data) below the data, so country codes repeat
- Losing the link between a result and the paragraph that asked for it
- Copying internal note content or data into committed files or external services

## Output
`docs/briefs/<project>/research-brief.md`; results pack in `docs/briefs/<project>/results/`

The research brief holds the task map with source paragraphs, the assumption list, the data map, the two tracks per task, routing and plan. The results pack holds the charts and tables by section of the note, the reconciliation report and the caveats; model code and runs live in the model folders named by the routed skills. Every run saves its results to `output/<run-id>/` in the model folder, with a run log (`.claude/rules/model-code.md`).

## Gate / verdict
- Every task points to a paragraph of the note, and every stated assumption is implemented or listed as not implementable
- The replication track matches the supplied numbers within tolerance, or the discrepancies are explained
- Every difference between the tracks is explained
- Inputs were classified and are stored where their class allows

## Suggested next steps
- `/debt-decomposition`
- `/vulnerability-dashboard`
- `/scenario-analysis`
- `/country-typology`
- `/policy-brief`
