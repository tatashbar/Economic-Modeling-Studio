---
name: team-country-analysis
description: "Orchestrates a country analysis: macro outlook, external, fiscal, financial, risks, policy options and note."
argument-hint: "[country]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /team-country-analysis — Team Country Analysis

**Category:** Team Orchestration · **Primary agent:** `economic-reasoning-specialist`

Orchestrates a country analysis: macro outlook, external, fiscal, financial, risks, policy options and note.

Arguments: `$ARGUMENTS`

## Purpose
Orchestrate a country analysis: collect context from counterparts, build a consistent baseline outlook, assess the external position, debt sustainability and financial stability in parallel, construct risks and downside scenarios, and deliver a policy note with charts, reviewed for economic logic and policy relevance. The output is an integrated country package in which all numbers come from approved models and reconcile across sections.

**Use it when** a full country assessment is needed for surveillance, a program discussion or a policy dialogue.

**Do not use it when** only one component is needed (`/forecast-round`, `/external-assessment`, `/debt-sustainability`, `/stress-test`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Country data
   - Context and requirements
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `economic-reasoning-specialist` — primary agent; coordinates the work and integrates results
- `fpas-modeler` — Builds forecasting and policy analysis systems (FPAS) for inflation-targeting and transitioning regimes
- `ipf-low-income-specialist` — Applies the Integrated Policy Framework to low-income countries
- `external-assessment-specialist` — Conducts external-sector assessments
- `debt-sustainability-analyst` — Builds debt sustainability analyses
- `financial-stability-stress-testing-specialist` — Builds systemic risk and stress-testing frameworks
- `scenario-risk-analysis-specialist` — Designs scenarios and risk assessments
- `stakeholder-liaison-specialist` — Interfaces with stakeholders and counterparts
- `policy-brief-writer` — Writes policy briefs and notes
- `visualization-dashboard-specialist` — Designs charts and dashboards

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Phase 1: stakeholder-liaison-specialist collects context, stakeholders' views and data issues
2. Phase 2 (parallel): baseline outlook, external assessment, DSA and financial-stability analysis
   - All components share one macro baseline and data vintage
3. Phase 3: scenario-risk-analysis-specialist builds risks and downside scenarios on the consistent baseline
4. Phase 4: policy-brief-writer drafts the note; visualization-dashboard-specialist builds the chart pack
5. Phase 5: economic-reasoning-specialist and policy-relevance-specialist review; model-risk-governance-specialist confirms that all models used are approved

## Checkpoints with the user
- End of Phase 1: confirm context and assumptions
- End of Phase 3: confirm risks and scenarios
- Before release: approve the note

## Common pitfalls
- Components built on different baselines or vintages
- Unapproved models used under time pressure
- Risks relegated to an annex

## Output
`forecasts/country-analysis/<country>-<date>/`

The package holds the baseline, component analyses, scenarios, the note, the chart pack and review records.

## Gate / verdict
- All models used are approved; risks and uncertainty are in the main text
- All components share one baseline and data vintage

## Suggested next steps
- `/policy-brief`
- `/retrospective`
