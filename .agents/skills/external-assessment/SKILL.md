---
name: external-assessment
description: "Runs an external sector assessment: current-account norm, REER gap, reserves, NIIP, with ranges and judgment."
---
<!-- Generated from .claude/skills/external-assessment/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /external-assessment — External Assessment

**Category:** Analysis · **Primary agent:** `external-assessment-specialist`

Runs an external sector assessment: current-account norm, REER gap, reserves, NIIP, with ranges and judgment.

Arguments: whatever the user wrote after the command name.

## Purpose
Assess whether a country's external position is in line with fundamentals and desirable policies: current-account norm and gap, real-exchange-rate gap, reserve adequacy and the sustainability of the net international investment position. Several methods are combined into a range, judgment adjustments are disclosed, and policy gaps behind imbalances are identified.

**Use it when** an external sector assessment is required for surveillance, a program, or advice on exchange-rate and reserve policy.

**Do not use it when** only BoP projections are needed (`/build-financial-programming`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - BoP/IIP data
   - Exchange-rate data
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `external-assessment-specialist` — primary agent; coordinates the work and integrates results
- `balance-of-payments-specialist` — Builds balance-of-payments and international investment position analyses
- `capital-flows-ipf-specialist` — Models capital flows and integrated policy frameworks
- `ipf-external-specialist` — Models FX-market frictions, external borrowing limits, FX intervention, reserves and capital flow measures

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Methods | panel regression norms, external sustainability approach, structural models | Range of gaps |
| Elasticities | trade elasticities to convert CA gaps to REER gaps | REER gap size |
| Reserve metric | import cover, short-term debt, composite risk-weighted, cost–benefit | Adequacy judgment |
| Adjustments | temporary factors, measurement issues | Judgment transparency |

## Workflow
1. Estimate current account norm and REER gap by multiple methods
   - Adjust for cyclical and temporary factors first
2. Assess reserve adequacy and NIIP sustainability
3. Combine into a range and document judgment adjustments
   - Cross-check with market and competitiveness indicators
4. Draft the assessment with policy implications
   - Identify fiscal, credit, reserve and capital-control policy gaps

## Checkpoints with the user
- After method results: confirm the range
- Before drafting: confirm judgment adjustments

## Common pitfalls
- One method reported as the assessment
- Undisclosed judgment adjustments
- Regression residuals treated as misalignment without scrutiny
- One-size-fits-all reserve metrics

## Output
`forecasts/external/<country>-<date>.md`

The assessment reports gaps by method, the combined range, reserve and NIIP analysis, judgment adjustments and policy implications.

## Gate / verdict
- Methods' ranges reported; judgment transparent
- Cross-checks with market and qualitative indicators are reported
- Reserve metric fits the country type

## Suggested next steps
- `/policy-brief`
- `/team-country-analysis`
