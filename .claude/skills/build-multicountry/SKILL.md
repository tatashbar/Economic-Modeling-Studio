---
name: build-multicountry
description: "Builds or extends a large multi-country model with trade and financial linkages and global scenarios."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-multicountry — Build Multicountry

**Category:** Build · **Primary agent:** `multi-country-dsge-specialist`

Builds or extends a large multi-country model with trade and financial linkages and global scenarios.

Arguments: `$ARGUMENTS`

## Purpose
Build or extend a large multi-country model with trade and financial linkages for global scenarios and spillover analysis. The output is a model in which global accounting closes (world trade balances, net foreign assets sum to zero), each region is calibrated, results are benchmarked against a reduced-form alternative, and runtime is good enough for regular use.

**Use it when** spillovers, global scenarios or coordinated policies across several economies are the question, and bilateral trade and financial links matter.

**Do not use it when** a single small open economy with a foreign block suffices (`/build-dsge`), or the question is empirical spillover estimation (`/spillover-analysis`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec
   - Bilateral trade and financial data
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `multi-country-dsge-specialist` — primary agent; coordinates the work and integrates results
- `global-spillover-specialist` — Analyzes global spillovers
- `trade-gvc-specialist` — Models trade and global value chains
- `hpc-gpu-engineer` — Engineers high-performance computing

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Regions | number of countries and rest-of-world blocks | Detail versus runtime |
| Model type per block | DSGE, semi-structural, mixed | Consistency and speed |
| Linkages | trade, commodities, financial (portfolio, banking), confidence | Spillover channels |
| Bilateral weights | trade, financial, time-varying or fixed | Transmission strength |
| Solution | stacked linear, block recursive, nonlinear | Speed and accuracy |

## Workflow
1. Define the regional blocks and bilateral matrices; verify consistency
   - World exports equal world imports; bilateral asset positions sum consistently
2. Implement the model with a block structure for speed
3. Calibrate each region and cross-check steady-state aggregates
   - Steady-state trade and NFA positions match data
4. Run standard global scenarios and compare to a reduced-form benchmark
   - Compare spillovers with GVAR or panel estimates (`/spillover-analysis`)
5. Profile runtime and parallelize where useful
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Checkpoints with the user
- After defining blocks: confirm regions and linkages
- After calibration: confirm steady-state aggregates
- After benchmark comparison: agree on how differences will be explained

## Common pitfalls
- Global accounts that do not close
- Bilateral weights from one year applied to all periods without checking
- Regions calibrated inconsistently with each other
- Spillovers driven by a single channel left unexamined

## Output
`models/multicountry/<name>/ (+ model.lego.json)`

The folder holds regional blocks, bilateral matrices, calibration files, global scenario scripts, the benchmark comparison, runtime profile and the lego manifest.

## Gate / verdict
- Global accounting closes
- Benchmark comparison documented
- Lego manifest passes `python tools/lego.py check`
- Each region's calibration targets are documented
- Runtime is profiled and reported

## Suggested next steps
- `/spillover-analysis`
- `/validate-model`
- `/lego-map`
