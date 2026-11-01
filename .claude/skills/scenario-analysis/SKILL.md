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

## Purpose
Design and run scenarios (coherent narratives of what could happen, translated into consistent shocks across the relevant models) and compare them with the baseline, explaining the transmission. The output is a set of conditional scenarios with explicit assumptions, and likelihood language only where a method supports it.

**Use it when** risks to a baseline must be explored, stress narratives prepared, or decision-makers need "what if" analysis.

**Do not use it when** density forecasts are the right communication (`/fan-chart`), or financial-sector losses are the focus (`/stress-test`).

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

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Narrative | external shock, domestic shock, policy shift, combined | Relevance |
| Severity | plausible, severe, reverse-engineered to breaking points | Use of results |
| Models | core model, satellites, multi-country | Channel coverage |
| Policy response | endogenous, fixed, alternative responses | Interpretation |
| Probability | none, model-based, expert-elicited | Likelihood language |

## Workflow
1. Define the scenario narrative, shocks and what is held constant
   - Calibrate severity to historical episodes where possible
2. Translate to model inputs in each relevant model; ensure consistency
3. Run scenarios; compare to baseline with transmission explanation
4. Assign likelihood language only if a method supports it

## Checkpoints with the user
- After the narrative: confirm shocks and assumptions
- After results: confirm communication of likelihood

## Common pitfalls
- Inconsistent shock translations across models
- Unstated policy responses
- Scenarios presented as forecasts
- Probability words without a method

## Output
`forecasts/scenarios/<name>.md`

The report describes each narrative, the shock translations, results versus baseline with transmission, and the basis for any likelihood statements.

## Gate / verdict
- Scenario labelled as conditional; assumptions explicit
- Shock translations are consistent across models
- Policy-response assumptions are stated

## Suggested next steps
- `/chart-pack`
- `/policy-brief`
