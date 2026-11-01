---
name: gate-check
description: "Runs a phase gate: checks exit criteria for the current stage and returns PASS / CONCERNS / FAIL / NOT ASSESSED."
argument-hint: "[concept|design|build|estimate|validate|release]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /gate-check — Gate Check

**Category:** Governance · **Primary agent:** `project-planning-specialist`

Runs a phase gate: checks exit criteria for the current stage and returns PASS / CONCERNS / FAIL / NOT ASSESSED.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Stage artifacts
   - studio-config.yaml
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `project-planning-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense
- `modeling-methodology-specialist` — Chooses methods and architecture across model families, sets code and data standards, and resolves technical trade-offs between traditional, structural and AI approaches
- `model-risk-governance-specialist` — Defines model risk levels and validation depth, enforces builder-validator independence, governs AI/LLM use and recommends release or block

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Read the gate definition in `.claude/docs/phase-gates.md`
2. Check every criterion against actual files; mark FOUND or ABSENT
3. Ask the economic-reasoning, methodology and model-risk specialists for a verdict on their criteria
4. Return an overall verdict with blockers, owners and next actions

## Output
`production/gates/<stage>-<date>.md`

## Gate / verdict
- Verdict 'NOT ASSESSED' if required evidence is absent — never a pass by default

## Suggested next steps
- `/milestone-review`
