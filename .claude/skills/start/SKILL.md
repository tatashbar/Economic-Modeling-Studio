---
name: start
description: "First-time entry point. Asks what you want to model, detects project stage, and routes you to the right workflow."
argument-hint: "[none]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /start — Start

**Category:** Onboarding · **Primary agent:** `project-planning-specialist`

First-time entry point. Asks what you want to model, detects project stage, and routes you to the right workflow.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - production/stage.txt (optional)
   - studio-config.yaml
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `project-planning-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense
- `modeling-methodology-specialist` — Chooses methods and architecture across model families, sets code and data standards, and resolves technical trade-offs between traditional, structural and AI approaches

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Greet the user and ask what they are trying to achieve: a question to answer, a model to build, a forecast to produce, a model to validate, or an existing model to adopt
2. Ask the model size class (small, medium, large), the audience and the deadline
3. Run `/project-stage-detect` logic to see what already exists
4. Recommend the first three skills to run, with reasons, and wait for the user's choice
5. Write the choice to `production/session-state/active.md`

## Output
`production/session-state/active.md`

## Gate / verdict
- The user has chosen a path; nothing is written before the user agrees

## Suggested next steps
- `/scope-question`
- `/adopt`
- `/project-stage-detect`
