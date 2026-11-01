---
name: external-assessment
description: "Runs an external sector assessment: current-account norm, REER gap, reserves, NIIP, with ranges and judgment."
---
<!-- Generated from .claude/skills/external-assessment/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /external-assessment — External Assessment

**Category:** Analysis · **Primary agent:** `external-assessment-specialist`

Runs an external sector assessment: current-account norm, REER gap, reserves, NIIP, with ranges and judgment.

Arguments: whatever the user wrote after the command name.

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

## Workflow
1. Estimate current account norm and REER gap by multiple methods
2. Assess reserve adequacy and NIIP sustainability
3. Combine into a range and document judgment adjustments
4. Draft the assessment with policy implications

## Output
`forecasts/external/<country>-<date>.md`

## Gate / verdict
- Methods' ranges reported; judgment transparent

## Suggested next steps
- `/policy-brief`
- `/team-country-analysis`
