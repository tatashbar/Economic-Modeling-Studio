---
name: model-risk-review
description: "Independent model risk review: aggregates validation, ethics, confidentiality and use-limit checks; approves or blocks release."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /model-risk-review — Model Risk Review

**Category:** Validation & QA · **Primary agent:** `model-risk-governance-specialist`

Independent model risk review: aggregates validation, ethics, confidentiality and use-limit checks; approves or blocks release.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Validation report
   - Model card
   - Data classification
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `model-risk-governance-specialist` — primary agent; coordinates the work and integrates results
- `model-validation-specialist` — Performs independent model validation
- `ai-ethics-fairness-specialist` — Reviews AI ethics and fairness
- `data-governance-metadata-specialist` — Owns data governance and metadata

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Collect validation findings and their status
2. Check confidentiality, ethics and use-limit constraints
3. Decide: APPROVED / APPROVED WITH CONDITIONS / BLOCKED, and record conditions and owners
4. Update the model inventory

## Output
`validation/<model>/model-risk-decision.md`

## Gate / verdict
- High-severity open findings block approval

## Suggested next steps
- `/model-release`
