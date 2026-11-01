---
name: lego-check
description: "Checks a lego model: all studs connected or stubbed, no duplicate providers, slots filled, units and frequencies consistent, identities verifiable, simultaneous blocks listed."
argument-hint: "[manifest path]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /lego-check — Lego Check

**Category:** Lego (Modular Models) · **Primary agent:** `model-validation-specialist`

Checks a lego model: all studs connected or stubbed, no duplicate providers, slots filled, units and frequencies consistent, identities verifiable, simultaneous blocks listed.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - A model.lego.json manifest
   - The model code or specification (to compare the declared ports with what is implemented)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `model-validation-specialist` — primary agent; coordinates the work and integrates results
- `modeling-methodology-specialist` — Chooses methods and architecture across model families, sets code and data standards, and resolves technical trade-offs between traditional, structural and AI approaches
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Run `python tools/lego.py check <manifest>` and report errors, warnings and notes
2. Compare the manifest with the code: every declared provided variable exists in the code with that unit; no variable crosses a brick boundary without being declared
3. Check timing: lagged joints are really lagged in the code; same-period joints sit in a simultaneous block that the solver handles jointly
4. Check frequencies: each brick on a different frequency has a declared bridge, and the bridge is implemented and tested
5. Check identities: each declared accounting identity holds numerically in a run, not only on paper
6. List bricks that are unvalidated or stale and block release until they are validated

## Output
`(conversation); optionally validation/<model>/lego-check.md`

## Gate / verdict
- Verdict: PASS / PASS WITH CONDITIONS / FAIL / NOT ASSESSED (if the code is absent, the manifest-to-code comparison is NOT ASSESSED)

## Suggested next steps
- `/validate-model`
- `/model-release`
