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

## Purpose
Build a deep-learning or foundation-model forecaster and find out honestly whether it beats the statistical benchmarks that macro forecasters already use. The output is a forecaster evaluated in pseudo-real time with rolling origins, scored on point and density accuracy and calibration, with a documented account of where it wins, loses and fails.

**Use it when** there are many series, likely nonlinearities or mixed frequencies, or when a pretrained time-series model should be tested on a country's data.

**Do not use it when** the sample is short and a BVAR or DFM is the natural tool (`/estimate-bvar`, `/nowcast`), or when structural interpretation is required (`/build-semi-structural`).

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

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Architecture | LSTM/GRU, TCN, transformer/TFT, N-BEATS, foundation model | Capacity and data needs |
| Global versus local | one model across many series or one per series | Sample size effectively available |
| Outputs | point, quantiles, full density | Risk analysis capability |
| Training window | expanding, rolling | Adaptation to breaks |
| Benchmarks | AR, BVAR, DFM, simple combinations | Bar for success |

## Workflow
1. Define target, horizons, information set and the rolling-origin protocol before training
   - Use data vintages where available; record release calendars
2. Build benchmarks first (AR, BVAR, DFM) and record their scores
3. Train candidate architectures including a pretrained foundation model; log every run
   - Tune only on validation windows; record seeds and hyperparameters
   - Check whether the foundation model's training data may overlap the evaluation period
4. Evaluate point and density forecasts; test calibration
   - Equal-accuracy tests against benchmarks; PIT and coverage
5. Document where the model wins, loses and fails; propose an ensemble if it adds value
   - Report by subperiod, including stress periods
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Checkpoints with the user
- After the protocol: confirm targets, horizons and the information set
- After benchmarks: confirm the bar the model must clear
- After evaluation: decide on ensemble inclusion

## Common pitfalls
- Random splits or look-ahead in scaling and features
- Weak benchmarks
- Reporting the best seed
- Averages that hide failures in stress periods

## Output
`models/ai/<name>/ and docs/models/<name>/experiment-log.md (+ model.lego.json)`

The model folder holds code, benchmark scripts, training logs and evaluation results; the experiment log records every run with seeds, data vintages and scores; the lego manifest registers the forecaster as a satellite brick.

## Gate / verdict
- Benchmarks were built first
- Results use time-aware splits and pseudo-real-time data
- Calibration reported
- Lego manifest passes `python tools/lego.py check`
- Performance is reported by subperiod and across seeds
- Foundation-model data overlap is assessed

## Suggested next steps
- `/validate-model`
- `/ai-audit`
- `/lego-map`
