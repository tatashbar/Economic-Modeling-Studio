---
name: debt-decomposition
description: "Decomposes changes in debt ratios into drivers (interest, growth, primary balance, policy, exchange rate, stock-flow) by country and aggregated by group."
argument-hint: "[countries or group] [period]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /debt-decomposition — Debt Decomposition

**Category:** Analysis · **Primary agent:** `debt-sustainability-analyst`

Decomposes changes in debt ratios into drivers (interest, growth, primary balance, policy, exchange rate, stock-flow) by country and aggregated by group.

Arguments: `$ARGUMENTS`

## Purpose
Explain why public (or external) debt ratios change over a historical or projection period: how much comes from interest costs, nominal growth, the primary balance and its policy and non-policy parts, exchange-rate valuation of foreign-currency debt, and stock-flow adjustments. The decomposition is computed country by country and aggregated by region or other group so that group contributions add up exactly. When a user brings an existing decomposition, the skill reproduces it first, then compares it with the standard debt-dynamics identity.

**Use it when** a chart or table needs the drivers of debt changes across countries, or an existing spreadsheet decomposition must be replicated and checked.

**Do not use it when** the question is whether debt is sustainable under stress (`/debt-sustainability`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Gross debt (levels or ratios), nominal GDP, overall and primary balances by country and year
   - Foreign-currency debt share or stock and exchange rates (for the valuation term)
   - A policy measure for the fiscal split (for example the structural or cyclically adjusted balance, or measures data) (optional)
   - Country classification for groups; an existing decomposition to replicate (optional)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `debt-sustainability-analyst` — primary agent; coordinates the work and integrates results
- `cross-country-indicators-specialist` — Builds cross-country indicator analyses from panel databases: country groups, constant samples, aggregation, vulnerability thresholds, heatmaps and typologies
- `fiscal-risk-specialist` — Assesses fiscal risks
- `national-accounts-specialist` — Specializes in national accounts and macro statistics

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Framework | standard debt-dynamics identity (interest, real growth, inflation, exchange rate, primary balance, residual); a user-specified bottom-up split | Which drivers exist and how the residual is defined |
| Measurement | change in the debt ratio; change in debt in a common currency | Aggregation across countries; exchange-rate effects inside other terms |
| Fiscal split | primary balance only; policy versus non-policy using structural balance or measures data | Whether "policy" is identified and how well |
| Exchange-rate term | foreign-currency share of debt with bilateral rates; all foreign-currency debt in US dollars | Valuation effect size |
| Aggregation | sum of country contributions in common currency over group GDP; GDP-weighted; simple average | Group results and their weights |
| Sample | constant sample of countries with complete data; all available | Comparability across years |

## Workflow
1. Agree the framework, measurement, sample and groups; write the formulas for every term
   - When replicating, write the author's formulas and assumptions as stated, including the residual definition
2. Build the tidy panel and the constant sample; report sample sizes by group
3. Compute the decomposition country by country; check that the terms sum exactly to the change (residual reported as its own term)
4. Aggregate to groups and the total; check that group contributions add up to the total
5. Replication check against the supplied numbers, within tolerance; log any discrepancy and its cause
6. Compare with the standard identity: same drivers ranked the same way? Where do they differ and why?
7. Sensitivity: base year, currency, foreign-currency assumption, policy measure, sample

## Checkpoints with the user
- After the formulas: confirm framework, assumptions and the residual definition
- After the replication check: confirm the match before comparing frameworks
- Before charts: confirm groups, ordering and labels

## Common pitfalls
- A large residual reported as "other" without explanation
- Exchange-rate valuation mixed into growth or into the residual when debt is measured in a common currency
- Policy effects inferred from structural balances without saying how noisy they are
- Group results that move because the sample changed
- Contributions that do not add up to the total
- A base-year level subtracted once while flows are summed over several years, so the level carried forward is labelled as a change
- A valuation term that does not match the currency of measurement (with debt in US dollars, depreciation changes the dollar value of local-currency debt, not of foreign-currency debt)

## Output
`docs/models/<name>/debt-decomposition.md`; code and data in `models/semi-structural/<name>/`

The report states the framework and formulas, sample and groups, country and group contributions, the replication check, the comparison with the standard identity and the sensitivity results. Every run saves its results to `output/<run-id>/` in the model folder, with a run log (`.claude/rules/model-code.md`).

## Gate / verdict
- Terms sum exactly to the change for every country and group, with the residual shown
- Group contributions add up to the total
- Replication of any supplied decomposition is within tolerance or explained
- Sample, weights and vintage are stated on every chart

## Suggested next steps
- `/debt-sustainability`
- `/vulnerability-dashboard`
- `/chart-pack`
