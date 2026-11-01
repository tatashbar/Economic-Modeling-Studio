---
name: lego-swap
description: "Swaps one brick for an alternative that fills the same slot, for example a Taylor rule for a managed-FX rule, or an input-output brick for a CGE."
argument-hint: "[manifest path] [old brick id] [new brick id | file]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /lego-swap — Lego Swap

**Category:** Lego (Modular Models) · **Primary agent:** `modeling-methodology-specialist`

Swaps one brick for an alternative that fills the same slot, for example a Taylor rule for a managed-FX rule, or an input-output brick for a CGE.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - A model.lego.json manifest
   - The replacement brick
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `modeling-methodology-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense
- `model-validation-specialist` — Performs independent model validation
- `policy-relevance-specialist` — Clarifies the decision, audience and deadline, and reviews outputs for decision-relevance, honest uncertainty and appropriate caveats

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Dry-run: `python tools/lego.py swap <manifest> <old> <new>`. Compare the two bricks: ports lost and gained, new joints, new simultaneous blocks, bridges needed
2. Resolve errors; if ports consumed by others are lost, either the consumers need stubs or the swap is not like-for-like
3. Apply with `--apply --note '<why>'`
4. Run both versions on the same scenarios and tabulate the differences (this is a structural-uncertainty exercise, so report it as such)
5. Re-validate the new brick and its neighbours

## Output
`Updated model.lego.json and a comparison table in docs/models/<name>/`

## Gate / verdict
- Like-for-like on the slot, or the differences are documented
- Both versions compared on identical scenarios

## Suggested next steps
- `/lego-check`
- `/robustness-check`
