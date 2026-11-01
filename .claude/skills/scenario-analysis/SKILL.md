---
name: scenario-analysis
description: "Designs and runs scenarios and risk assessments with consistent assumptions across models."
argument-hint: "[scenario description]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /scenario-analysis — Scenario Analysis

**Category:** Analysis · **Primary agent:** `scenario-risk-analysis-specialist`

Designs and runs scenarios and risk assessments with consistent assumptions across models.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Baseline
   - Approved models
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `scenario-risk-analysis-specialist` — primary agent; coordinates the work and integrates results
- `generative-ai-scenario-specialist` — Uses generative models (VAEs, GANs, diffusion, LLMs) to create scenarios, synthetic data and stress paths
- `global-spillover-specialist` — Analyzes global spillovers

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Define the scenario narrative, shocks and what is held constant
2. Translate to model inputs in each relevant model; ensure consistency
3. Run scenarios; compare to baseline with transmission explanation
4. Assign likelihood language only if a method supports it

## Output
`forecasts/scenarios/<name>.md`

## Gate / verdict
- Scenario labelled as conditional; assumptions explicit

## Suggested next steps
- `/chart-pack`
- `/policy-brief`
