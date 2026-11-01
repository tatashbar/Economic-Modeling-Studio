---
name: build-financial-programming
description: "Builds an integrated financial-programming framework consistent across real, fiscal, monetary and external sectors."
---
<!-- Generated from .claude/skills/build-financial-programming/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-financial-programming — Build Financial Programming

**Category:** Build · **Primary agent:** `financial-programming-specialist`

Builds an integrated financial-programming framework consistent across real, fiscal, monetary and external sectors.

Arguments: whatever the user wrote after the command name.

## Purpose
Build an integrated financial-programming framework: a consistent set of real, fiscal, monetary and external accounts linked by identities and a small number of behavioral relationships, used to design and check macroeconomic programs and to compute financing gaps. The output is a framework in which every identity closes in code and every behavioral assumption is sourced.

**Use it when** a program, budget or medium-term framework needs cross-sector consistency, financing gaps must be identified, or a counterpart needs a transparent accounting framework to own.

**Do not use it when** behavioral dynamics and expectations dominate the question (`/build-semi-structural`, `/build-dsge`) or when the question is only about debt dynamics (`/debt-sustainability`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Data sheet with sectoral accounts
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `financial-programming-specialist` — primary agent; coordinates the work and integrates results
- `balance-of-payments-specialist` — Builds balance-of-payments and international investment position analyses
- `debt-sustainability-analyst` — Builds debt sustainability analyses
- `rmsm-three-gap-modeler` — Builds revised minimum standard, three-gap and growth-financing models for low-income and developing economies

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Frequency | annual, quarterly | Data needs; program monitoring |
| Sector coverage | central government or general government; depository corporations or broader | Consistency and data availability |
| Closure | which variable absorbs the gap (financing, reserves, spending) | Policy interpretation |
| Behavioral equations | trade elasticities, money demand, revenue elasticities, import propensities | Scenario responses |
| Exchange-rate regime | fixed, managed, flexible | Monetary–external links |

## Workflow
1. Lay out sectoral accounts and identities; implement in code with assertions
   - National accounts, fiscal, monetary survey and BoP; saving–investment and sectoral balance links
   - Assertions fail loudly on any residual
2. Specify behavioral relationships and their sources
   - Each elasticity or ratio with estimate, sample and source; ranges where uncertain
3. Build baseline and alternative scenarios with financing gaps
   - Gaps shown explicitly, not absorbed into residuals
4. Run consistency checks across fiscal, monetary, BoP and national accounts
   - Reconcile data discrepancies and document them (`/data-requirements`)
5. Document assumptions for program-design use
   - Make the framework simple enough for counterparts to operate
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Checkpoints with the user
- After the accounts layout: confirm coverage and the closure variable
- After behavioral assumptions: confirm sources and ranges
- After the baseline: confirm the macro story before alternatives

## Common pitfalls
- Gaps hidden in errors and omissions or statistical discrepancies
- Mixing cash and accrual fiscal data
- Behavioral parameters from different periods or countries without justification
- Frameworks too complex for counterparts to maintain

## Output
`models/financial-programming/<country>/ (+ model.lego.json)`

The folder holds the accounts code with identity assertions, the behavioral-parameter table, baseline and scenario files, the consistency report and the lego manifest.

## Gate / verdict
- All sectoral identities close
- Behavioral parameters are sourced
- Lego manifest passes `python tools/lego.py check`
- Financing gaps are shown explicitly
- Cross-sector consistency checks are recorded

## Suggested next steps
- `/debt-sustainability`
- `/validate-model`
- `/lego-map`
