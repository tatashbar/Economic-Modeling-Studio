---
name: backtest
description: "Runs historical and pseudo-real-time backtests with information-set checks and regime-specific performance."
---
<!-- Generated from .claude/skills/backtest/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /backtest — Backtest

**Category:** Validation & QA · **Primary agent:** `backtesting-specialist`

Runs historical and pseudo-real-time backtests with information-set checks and regime-specific performance.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Model code
   - Data vintages
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `backtesting-specialist` — primary agent; coordinates the work and integrates results
- `forecast-evaluation-specialist` — Evaluates forecasts

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Define windows, horizons and the information set at each origin
2. Verify no look-ahead with automated checks
3. Run the backtest; compute point and density scores against naive benchmarks
4. Report calm vs. stress-period performance

## Output
`validation/<model>/backtest-report.md`

## Gate / verdict
- No look-ahead verified
- Benchmarks included

## Suggested next steps
- `/validate-model`
- `/forecast-round`
