---
name: validate-model
description: "Runs independent model validation sized to risk level: conceptual soundness, implementation, outcomes, benchmarking. Issues a rating."
---
<!-- Generated from .claude/skills/validate-model/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /validate-model — Validate Model

**Category:** Validation & QA · **Primary agent:** `model-validation-specialist`

Runs independent model validation sized to risk level: conceptual soundness, implementation, outcomes, benchmarking. Issues a rating.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Model spec
   - Code
   - Calibration/estimation results
   - Model card (if exists)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `model-validation-specialist` — primary agent; coordinates the work and integrates results
- `backtesting-specialist` — Designs and runs backtests
- `sensitivity-uncertainty-specialist` — Quantifies uncertainty and sensitivity
- `replication-auditor` — Audits replication

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Confirm validators are independent of the builders; record this in the report
2. Conceptual soundness: assumptions, literature, limitations
3. Implementation: independent re-implementation of core outputs; unit tests; identity checks
4. Outcomes: backtests, benchmark comparison, sensitivity and stress cases
5. Issue findings with severity (High/Medium/Low) and a rating: PASS / PASS WITH CONDITIONS / FAIL / NOT ASSESSED
6. If the model has a model.lego.json, validate each brick and each joint separately (interfaces, units, timing, neutral-attachment test); treat stale bricks as unvalidated. For each brick rated PASS (or PASS WITH CONDITIONS, with the conditions in the report), record it with `python tools/lego.py validate <manifest> <brick> --report validation/<model>/validation-report.md --apply`

## Output
`validation/<model>/validation-report.md`

## Gate / verdict
- PASS requires: no open High findings, core outputs independently reproduced, benchmark comparison shown

## Suggested next steps
- `/model-risk-review`
- `/model-card`
- `/model-release`
