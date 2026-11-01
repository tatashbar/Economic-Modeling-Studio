---
name: identify-shocks
description: "Constructs and tests structural shock series (narrative, high-frequency, proxy) and documents identification."
argument-hint: "[shock type]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /identify-shocks — Identify Shocks

**Category:** Estimation · **Primary agent:** `shock-identification-specialist`

Constructs and tests structural shock series (narrative, high-frequency, proxy) and documents identification.

Arguments: `$ARGUMENTS`

## Purpose
Construct and test a structural shock series (narrative, high-frequency, or proxy instrument) that can be used to identify causal effects in VARs, local projections and model validation. The output is a documented series whose concept, exclusion assumption, strength and exogeneity are tested and whose behavior around known events has been checked.

**Use it when** a credible measure of monetary, fiscal, oil, uncertainty or financial shocks is needed as an instrument or regressor.

**Do not use it when** recursive or sign-restricted VAR identification is sufficient (`/estimate-var`), or an existing validated series can be reused.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Event/high-frequency data
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `shock-identification-specialist` — primary agent; coordinates the work and integrates results
- `nlp-text-as-data-specialist` — Turns text into economic data
- `var-vecm-specialist` — Builds VAR, SVAR and VECM models

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Approach | narrative records, high-frequency surprises, proxy from model residuals | Exogeneity argument |
| Event window | 30 minutes, daily, monthly | Contamination and power |
| Information effects | control for forecasts, separate information and policy components | Interpretation |
| Frequency aggregation | sum, average, last event | Use in monthly or quarterly models |

## Workflow
1. Define the shock concept and the exclusion assumption
   - State what the series must not be correlated with
2. Build the series; test strength and exogeneity
   - First-stage F statistics, predictability from past data and forecasts
3. Cross-check against known events and alternative series
4. Archive the series with documentation
   - Source records, construction code, vintage and known limitations

## Checkpoints with the user
- After defining the concept: confirm the exclusion assumption
- After tests: confirm strength is adequate for intended uses

## Common pitfalls
- High-frequency surprises contaminated by information effects
- Weak instruments used without robust inference
- Narrative coding that uses hindsight
- Aggregation that dilutes the shock

## Output
`data/processed/shocks/<shock>.csv and docs/models/<name>/shock-note.md`

The shock series is stored with its construction code; the note documents the concept, sources, tests, event checks and limitations.

## Gate / verdict
- Instrument strength and exogeneity tests reported
- Weak-instrument-robust inference is recommended where strength is marginal
- Construction is reproducible from sources

## Suggested next steps
- `/local-projections`
- `/estimate-var`
