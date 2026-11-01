---
name: debt-sustainability
description: "Runs debt sustainability analysis: baseline, shocks, stochastic fan charts, realism checks and financing needs."
argument-hint: "[country]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /debt-sustainability — Debt Sustainability

**Category:** Analysis · **Primary agent:** `debt-sustainability-analyst`

Runs debt sustainability analysis: baseline, shocks, stochastic fan charts, realism checks and financing needs.

Arguments: `$ARGUMENTS`

## Purpose
Run a debt sustainability analysis: a baseline whose debt dynamics decompose exactly into primary balance, interest, growth, inflation, exchange-rate and stock-flow effects; standardized and tailored stress tests; stochastic fan charts; realism checks; and an assessment of financing needs and debt-structure risks. The output is a sustainability judgment stated in probabilistic terms with its limits.

**Use it when** public or external debt must be assessed for a budget, program, risk statement or restructuring discussion.

**Do not use it when** a structural default model is needed for spreads and crisis zones (`/build-game-model`), or the full macro framework is missing (`/build-financial-programming`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Fiscal and macro baseline
   - Debt composition data
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `debt-sustainability-analyst` — primary agent; coordinates the work and integrates results
- `fiscal-risk-specialist` — Assesses fiscal risks
- `sovereign-crisis-games-specialist` — Models sovereign debt, default and currency crises
- `revenue-tax-policy-specialist` — Forecasts and analyzes tax revenue
- `extractives-natural-resources-specialist` — Analyzes resource-rich economies

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Coverage | central government, general government, plus SOEs and guarantees | Measured debt and risks |
| Framework | market-access framework, low-income-country framework | Indicators and thresholds |
| Stochastic method | VAR-based shocks, bootstrapped history | Fan-chart width |
| Tailored shocks | contingent liabilities, disasters, commodity prices | Country-specific risks |
| Horizon | 5, 10 years or longer | Visibility of long-run pressures |

## Workflow
1. Build the baseline and verify the debt-dynamics decomposition
   - State coverage; include stock-flow adjustments explicitly
2. Apply standardized and tailored shocks; run stochastic simulations
   - Include combined shocks and contingent-liability realizations
3. Run realism checks vs. history and peers
   - Fiscal adjustment against historical distributions; growth–adjustment consistency with multipliers
4. Assess financing needs, contingent liabilities and rollover risk
5. Write the risk assessment with explicit limits

## Checkpoints with the user
- After the baseline: confirm macro and fiscal assumptions
- After stress tests: confirm tailored shocks capture country risks

## Common pitfalls
- Optimistic baselines with large adjustment and unchanged growth
- Narrow coverage missing SOEs and guarantees
- Ignoring exchange-rate valuation
- Fan charts from calm periods only

## Output
`forecasts/dsa/<country>-<date>.md`

The report presents the baseline and decomposition, stress tests, fan charts, realism checks, financing needs and the risk assessment with limits.

## Gate / verdict
- Decomposition closes exactly
- Realism checks documented
- Coverage is stated and contingent liabilities are stress-tested
- The judgment states its probability basis

## Suggested next steps
- `/policy-brief`
- `/team-fiscal`
