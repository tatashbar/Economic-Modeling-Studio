---
name: model-risk-review
description: "Independent model risk review: aggregates validation, ethics, confidentiality and use-limit checks; approves or blocks release."
---
<!-- Generated from .claude/skills/model-risk-review/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /model-risk-review — Model Risk Review

**Category:** Validation & QA · **Primary agent:** `model-risk-governance-specialist`

Independent model risk review: aggregates validation, ethics, confidentiality and use-limit checks; approves or blocks release.

Arguments: whatever the user wrote after the command name.

## Purpose
Make the release decision for a model: bring together validation findings, AI audits, ethics, confidentiality and use limits, and decide whether the model is approved, approved with conditions, or blocked, with owners and deadlines for every condition. The output is a recorded decision and an updated model inventory.

**Use it when** a model or major model change is ready for use in advice, forecasts or publication.

**Do not use it when** validation has not yet been done (`/validate-model`, `/ai-audit`).

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Risk level | low, medium, high | Evidence required |
| Conditions | use limits, monitoring, remediation deadlines | Scope of approval |
| Review cycle | annual, on change | Ongoing assurance |

## Workflow
1. Collect validation findings and their status
   - Include lego brick validation status where relevant
2. Check confidentiality, ethics and use-limit constraints
3. Decide: APPROVED / APPROVED WITH CONDITIONS / BLOCKED, and record conditions and owners
4. Update the model inventory

## Checkpoints with the user
- Before the decision: review open findings and proposed conditions

## Common pitfalls
- Approving with conditions that have no owners or deadlines
- Ignoring use outside the design domain
- Inventory not updated

## Output
`validation/<model>/model-risk-decision.md`

The decision record lists the evidence reviewed, open findings, the decision, conditions with owners and deadlines, use limits and the next review date.

## Gate / verdict
- High-severity open findings block approval
- Conditions have owners and deadlines
- The model inventory is updated

## Suggested next steps
- `/model-release`
