---
name: milestone-review
description: "Reviews progress against milestones: scope, schedule, risk, quality, dependencies and re-planning."
argument-hint: "[milestone or project]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /milestone-review — Milestone Review

**Category:** Governance · **Primary agent:** `project-planning-specialist`

Reviews progress against milestones: scope, schedule, risk, quality, dependencies and re-planning.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Project plan
   - Production notes
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `project-planning-specialist` — primary agent; coordinates the work and integrates results
- `modeling-methodology-specialist` — Chooses methods and architecture across model families, sets code and data standards, and resolves technical trade-offs between traditional, structural and AI approaches
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Compare plan and actuals; list slippage and causes
2. Review risk register and open validation issues
3. Recommend scope or schedule changes with trade-offs
4. Update the plan after approval

## Output
`production/milestones/<name>-<date>.md`

## Gate / verdict
- Slippage has causes and owners

## Suggested next steps
- `/retrospective`
- `/gate-check`
