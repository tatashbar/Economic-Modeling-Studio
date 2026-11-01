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

## Workflow
1. Define the regional blocks and bilateral matrices; verify consistency
2. Implement the model with a block structure for speed
3. Calibrate each region and cross-check steady-state aggregates
4. Run standard global scenarios and compare to a reduced-form benchmark
5. Profile runtime and parallelize where useful
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/multicountry/<name>/ (+ model.lego.json)`

## Gate / verdict
- Global accounting closes
- Benchmark comparison documented
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/spillover-analysis`
- `/validate-model`
- `/lego-map`
