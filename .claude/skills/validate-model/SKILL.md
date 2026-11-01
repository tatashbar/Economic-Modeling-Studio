---
name: validate-model
description: "Runs independent model validation sized to risk level: conceptual soundness, implementation, outcomes, benchmarking. Issues a rating."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /validate-model — Validate Model

**Category:** Validation & QA · **Primary agent:** `model-validation-specialist`

Runs independent model validation sized to risk level: conceptual soundness, implementation, outcomes, benchmarking. Issues a rating.

Arguments: `$ARGUMENTS`

## Purpose
Run an independent validation of a model, sized to its risk level: conceptual soundness, implementation correctness (including independent re-implementation of core outputs), outcomes analysis and benchmarking, with findings rated by severity and an overall rating. For modular lego models, each brick and each joint is validated separately and the results are recorded in the manifest.

**Use it when** a model is to be used for advice, official forecasts or publication, after material changes, or for periodic revalidation.

**Do not use it when** the component is an AI/ML/LLM system (`/ai-audit`), or only a code check is needed (`/code-review`).

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

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Depth | proportional to risk level | Evidence required |
| Re-implementation | full, core outputs, key equations | Assurance |
| Benchmarks | simple econometric models, alternative structural models | Added-value evidence |
| Lego scope | whole set, changed bricks and joints | Effort for modular models |

## Workflow
1. Confirm validators are independent of the builders; record this in the report
2. Conceptual soundness: assumptions, literature, limitations
   - Check intended use against the design domain
3. Implementation: independent re-implementation of core outputs; unit tests; identity checks
   - For lego models, check each brick's declared elements against the code: equations match endogenous variables, unsourced (assumed) parameters appear in sensitivity runs, and constraints are verified in a run
4. Outcomes: backtests, benchmark comparison, sensitivity and stress cases
5. Issue findings with severity (High/Medium/Low) and a rating: PASS / PASS WITH CONDITIONS / FAIL / NOT ASSESSED
6. If the model has a model.lego.json, validate each brick and each joint separately (interfaces, units, timing, neutral-attachment test); treat stale bricks as unvalidated. For each brick rated PASS (or PASS WITH CONDITIONS, with the conditions in the report), record it with `python tools/lego.py validate <manifest> <brick> --report validation/<model>/validation-report.md --apply`

## Checkpoints with the user
- After scope: confirm depth and benchmarks
- Before the rating: review high-severity findings

## Common pitfalls
- Builders validating their own model
- Findings without evidence
- Validating bricks but not joints
- Ignoring use outside the design domain

## Output
`validation/<model>/validation-report.md`

The report states independence, scope, findings with evidence and severity, the rating, conditions of use, and per-brick and per-joint results for lego models.

## Gate / verdict
- PASS requires: no open High findings, core outputs independently reproduced, benchmark comparison shown
- Findings cite evidence (code, data, results)
- Conditions of use state the design domain

## Suggested next steps
- `/model-risk-review`
- `/model-card`
- `/model-release`
