---
name: country-typology
description: "Groups countries into policy-relevant types from data, by transparent rules or clustering, and maps each type to tailored policy options."
---
<!-- Generated from .claude/skills/country-typology/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /country-typology — Country Typology

**Category:** Analysis · **Primary agent:** `cross-country-indicators-specialist`

Groups countries into policy-relevant types from data, by transparent rules or clustering, and maps each type to tailored policy options.

Arguments: whatever the user wrote after the command name.

## Purpose
Turn general advice into tailored advice: assign each country to a type (for example high debt with large refinancing needs, commodity exporter, large exposure to state-owned enterprises and guarantees, lower capacity, moderate debt with high shock exposure) using indicators and transparent rules or clustering, list the countries in each type, and map each type to its main issue and priority policy responses. When a user brings a typology table, the skill implements it as rules on data, shows which countries fall in each type, and tests how stable the assignment is.

**Use it when** recommendations must differ by country circumstance, or a proposed typology needs data behind it.

**Do not use it when** the work is a single country's policy options (`/policy-simulation`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Indicator panel for the countries (debt, financing needs, commodity dependence, contingent liabilities, revenue capacity, buffers, shock exposure)
   - Country classification (export structure, income, region)
   - A proposed typology or policy table (optional)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `cross-country-indicators-specialist` — primary agent; coordinates the work and integrates results
- `debt-sustainability-analyst` — Builds debt sustainability analyses
- `fiscal-risk-specialist` — Assesses fiscal risks
- `policy-relevance-specialist` — Clarifies the decision, audience and deadline, and reviews outputs for decision-relevance
- `policy-brief-writer` — Writes policy briefs

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Method | rules on indicator thresholds; clustering (k-means, hierarchical) on standardized indicators; expert assignment checked against data | Transparency versus data-driven grouping |
| Overlap | one type per country; several types allowed with a primary type | Simplicity versus realism |
| Indicators | one or two per type; a composite per type | Robustness and explainability |
| Policy mapping | a supplied table; literature-based options; both | Source of the recommendations |

## Workflow
1. Agree the types, the indicators and rule (or clustering) behind each, and whether countries may belong to several types
2. Build the indicator panel; assign countries; list the countries in each type with the values that put them there
3. Stability: change thresholds, years and indicators; report countries that switch type
4. Map each type to its main issue and priority responses, with the evidence or source for each response
5. Sense-check with the user: countries whose assignment looks wrong are examined, not silently moved

## Checkpoints with the user
- After the rules: confirm types and indicators
- After the assignment: review the country lists and borderline cases
- Before the policy table: confirm the source of each recommendation

## Common pitfalls
- Types defined so loosely that every country qualifies
- Recommendations attached to types without evidence or source
- Clusters with no economic interpretation
- Hiding borderline countries that switch type under small changes

## Output
`docs/models/<name>/country-typology.md`; code and data in `models/econometrics/<name>/`

The report lists the types, rules or clustering method, the countries in each type with their indicator values, the stability results and the policy table by type. Every run saves its results to `output/<run-id>/` in the model folder, with a run log (`.claude/rules/model-code.md`).

## Gate / verdict
- Every country assignment can be traced to data and a rule
- Borderline and switching countries are listed
- Every policy response has a stated source or rationale

## Suggested next steps
- `/policy-brief`
- `/scenario-analysis`
