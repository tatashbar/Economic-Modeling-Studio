---
name: build-deep-forecaster
description: "Builds a deep-learning or foundation-model forecaster with rolling-origin evaluation against statistical benchmarks."
argument-hint: "[target variable(s)]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-deep-forecaster — Build Deep Forecaster

**Category:** Build (AI) · **Primary agent:** `time-series-deep-learning-specialist`

Builds a deep-learning or foundation-model forecaster with rolling-origin evaluation against statistical benchmarks.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Data sheet
   - Benchmark models (AR, BVAR or DFM)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `time-series-deep-learning-specialist` — primary agent; coordinates the work and integrates results
- `deep-learning-architect` — Designs deep learning architectures for macro-financial data
- `forecast-evaluation-specialist` — Evaluates forecasts
- `dfm-nowcasting-specialist` — Builds dynamic factor models and nowcasts

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Define target, horizons, information set and the rolling-origin protocol before training
2. Build benchmarks first (AR, BVAR, DFM) and record their scores
3. Train candidate architectures including a pretrained foundation model; log every run
4. Evaluate point and density forecasts; test calibration
5. Document where the model wins, loses and fails; propose an ensemble if it adds value
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/ai/<name>/ and docs/models/<name>/experiment-log.md (+ model.lego.json)`

## Gate / verdict
- Benchmarks were built first
- Results use time-aware splits and pseudo-real-time data
- Calibration reported
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/validate-model`
- `/ai-audit`
- `/lego-map`
