---
name: team-country-analysis
description: "Orchestrates a country analysis: macro outlook, external, fiscal, financial, risks, policy options and note."
---
<!-- Generated from .claude/skills/team-country-analysis/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /team-country-analysis — Team Country Analysis

**Category:** Team Orchestration · **Primary agent:** `economic-reasoning-specialist`

Orchestrates a country analysis: macro outlook, external, fiscal, financial, risks, policy options and note.

Arguments: whatever the user wrote after the command name.

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Phase 1: stakeholder-liaison-specialist collects context, stakeholders' views and data issues
2. Phase 2 (parallel): baseline outlook, external assessment, DSA and financial-stability analysis
3. Phase 3: scenario-risk-analysis-specialist builds risks and downside scenarios on the consistent baseline
4. Phase 4: policy-brief-writer drafts the note; visualization-dashboard-specialist builds the chart pack
5. Phase 5: economic-reasoning-specialist and policy-relevance-specialist review; model-risk-governance-specialist confirms that all models used are approved

## Output
`forecasts/country-analysis/<country>-<date>/`

## Gate / verdict
- All models used are approved; risks and uncertainty are in the main text

## Suggested next steps
- `/policy-brief`
- `/retrospective`
