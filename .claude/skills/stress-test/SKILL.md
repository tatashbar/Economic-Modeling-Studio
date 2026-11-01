---
name: stress-test
description: "Runs macro-financial stress tests: scenario design, satellite models, bank and sector results, policy implications."
argument-hint: "[sector or system]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /stress-test — Stress Test

**Category:** Analysis · **Primary agent:** `financial-stability-stress-testing-specialist`

Runs macro-financial stress tests: scenario design, satellite models, bank and sector results, policy implications.

Arguments: `$ARGUMENTS`

## Purpose
Run a macro-financial stress test: design severe but plausible scenarios calibrated to history and current vulnerabilities, map them to credit losses, income and funding pressures through validated satellite models, compute capital and liquidity outcomes including second-round effects, and draw policy implications. The output identifies vulnerabilities and capital or liquidity shortfalls with their sensitivity to assumptions.

**Use it when** assessing resilience of banks, non-banks or the financial system, or the fiscal implications of financial stress.

**Do not use it when** only macro scenarios are needed without financial-sector mapping (`/scenario-analysis`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Balance-sheet data
   - Macro scenarios
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `financial-stability-stress-testing-specialist` — primary agent; coordinates the work and integrates results
- `macroprudential-housing-specialist` — Analyzes macroprudential policy and housing/credit cycles
- `scenario-risk-analysis-specialist` — Designs scenarios and risk assessments
- `banking-credit-specialist` — Models banks and credit markets

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Scenario severity | historical analogues, statistical percentiles, reverse stress | Credibility |
| Coverage | largest banks, all banks, non-banks | System view |
| Balance sheet | static, dynamic | Interpretation |
| Channels | credit, market, funding, contagion, fire sales | Completeness |
| Horizon | 1–3 years | Loss accumulation |

## Workflow
1. Design severity-calibrated scenarios and document the calibration
2. Map to risk drivers with validated satellite models
   - Validate satellites out of sample on historical losses
3. Compute losses, capital and liquidity outcomes with second-round effects
   - Interbank and common-exposure contagion; fire sales where relevant
4. Report vulnerabilities and policy responses

## Checkpoints with the user
- After scenario design: confirm severity
- After results: confirm policy implications

## Common pitfalls
- Scenarios milder than past crises
- Static balance sheets read as forecasts
- Ignoring liquidity–solvency interactions
- Second-round effects omitted without flag

## Output
`forecasts/stress-tests/<name>.md`

The report covers scenario calibration, satellite models and validation, losses and capital and liquidity outcomes by institution or sector, second-round effects, and policy implications.

## Gate / verdict
- Severity calibrated; satellite models validated
- Balance-sheet assumptions are stated
- Second-round effects are estimated or their omission is flagged

## Suggested next steps
- `/policy-brief`
- `/team-stress-test`
