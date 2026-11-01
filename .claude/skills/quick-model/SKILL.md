---
name: quick-model
description: "Fast path for a small model or back-of-envelope analysis: minimal spec, minimal checks, clear 'not for publication' label."
argument-hint: "[question]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /quick-model — Quick Model

**Category:** Scoping & Design · **Primary agent:** `semi-structural-gap-modeler`

Fast path for a small model or back-of-envelope analysis: minimal spec, minimal checks, clear 'not for publication' label.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - User question
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `semi-structural-gap-modeler` — primary agent; coordinates the work and integrates results
- `financial-programming-specialist` — Builds financial programming frameworks

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Ask the single most decision-relevant question and the time budget
2. Pick the smallest suitable model and write a half-page spec
3. Build and run with at least two internal consistency checks
4. Label output 'exploratory — not validated' and list what would be needed to promote it

## Output
`docs/models/<name>/quick-note.md`

## Gate / verdict
- Output is labelled exploratory; promotion requires `/model-brief` and `/validate-model`

## Suggested next steps
- `/model-brief`
- `/scenario-analysis`
