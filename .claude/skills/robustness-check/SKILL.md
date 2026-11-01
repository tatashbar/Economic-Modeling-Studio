---
name: robustness-check
description: "Tests conclusions under alternative models, identification schemes, samples, priors and data vintages."
argument-hint: "[result or claim to test]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /robustness-check — Robustness Check

**Category:** Validation & QA · **Primary agent:** `model-validation-specialist`

Tests conclusions under alternative models, identification schemes, samples, priors and data vintages.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Result to test
   - Alternative specs
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `model-validation-specialist` — primary agent; coordinates the work and integrates results
- `sensitivity-uncertainty-specialist` — Quantifies uncertainty and sensitivity
- `forecast-combination-specialist` — Combines forecasts

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Define which dimensions of the result could plausibly change
2. Re-run under alternatives: model, identification, sample, priors, vintage
3. Summarize which conclusions are robust and which are not
4. Recommend wording changes for non-robust conclusions

## Output
`validation/<model>/robustness-report.md`

## Gate / verdict
- Non-robust conclusions are flagged in outputs

## Suggested next steps
- `/validate-model`
- `/policy-brief`
