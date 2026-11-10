---
name: code-inventory
description: "Inventories a code folder in any language used for economic models: languages, files, call graph, data in and out, packages, risky constructs, entry points and translation order."
---
<!-- Generated from .claude/skills/code-inventory/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /code-inventory — Code Inventory

**Category:** Code Translation · **Primary agent:** `source-code-analyst`

Inventories a code folder in any language used for economic models: languages, files, call graph, data in and out, packages, risky constructs, entry points and translation order.

Arguments: whatever the user wrote after the command name.

## Purpose
Find out what a code folder contains before anyone translates, adopts or validates it. The automatic scan (`python tools/translate.py inventory`) detects the language of each file (including shared extensions such as `.m`, `.mod`, `.prg`, `.src`, `.inp`), lines of code, the files each one calls, data files it reads and writes, packages, constructs that often change results when code moves (missing-value rules, unstable sorts, implicit typing, packed decimals, global state, random draws, absolute paths), entry points and an order in which called files come first. The analyst then reads the code to confirm and complete it.

**Use it when** you receive code you did not write, before `/translate-code` or `/adopt`, or to size a migration.

**Do not use it when** the full translation is wanted now; `/translate-code` runs the inventory as its first step.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Source folder (a path, or an uploaded folder copied to `translations/incoming/<name>/`)
   If it is `ABSENT`, ask for it.
2. **Check confidentiality.** Identify the classification of the code and any data in the folder (`.claude/docs/confidentiality-and-ai-use.md`). The scan reads files locally; restricted content is not quoted into prompts or external services.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `source-code-analyst` — primary agent; runs and confirms the inventory
- `code-translation-architect` — Sizes the work and suggests targets if a translation follows

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Run `python tools/translate.py inventory <source-folder>` (add `--out <folder>` to save `inventory.md` and `inventory.json`).
2. Read the entry points and follow the calls; add dependencies the scan cannot see (macros, `eval`, file names in variables, ado-files, toolboxes, libraries, copybooks, Excel links).
3. For spreadsheets, list the formulas behind calculation sheets with `python tools/intake.py formulas <file> --sheet <name>`.
4. Mark dead code, one-off scripts and tests; list missing inputs.
5. Summarize: languages and size, what the code produces, external dependencies, risky constructs, and the effort to translate to the likely targets.

## Checkpoints with the user
- After the scan: confirm the entry points and the outputs that matter

## Common pitfalls
- Treating the automatic call graph as complete
- Missing data or code the folder expects but does not contain
- Reading comments as facts about behavior

## Output
`translations/<name>-inventory/inventory.md` (or inside the translation workspace when part of `/translate-code`)

The inventory lists languages, files in translation order, calls, data in and out, packages, constructs to check, entry points, data files and missing pieces.

## Gate / verdict
- Every file classified (code by language, data, other)
- Entry points and key outputs confirmed by reading the code

## Suggested next steps
- `/translation-plan`
- `/translate-code`
- `/adopt`
