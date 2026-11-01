---
name: replicate
description: "Replicates results from the replication package on a clean environment and traces published numbers to code and data."
---
<!-- Generated from .claude/skills/replicate/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /replicate — Replicate

**Category:** Validation & QA · **Primary agent:** `replication-auditor`

Replicates results from the replication package on a clean environment and traces published numbers to code and data.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Replication package
   - Published outputs
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `replication-auditor` — primary agent; coordinates the work and integrates results
- `reproducibility-engineer` — Guarantees reproducibility

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Build the clean environment from lock files or containers
2. Run the one-command replication and compare outputs with tolerance
3. Trace each table/chart number to its script and data version
4. Log discrepancies and root causes

## Output
`validation/<model>/replication-report.md`

## Gate / verdict
- Outputs reproduced within tolerance, or discrepancies logged with cause

## Suggested next steps
- `/validate-model`
- `/model-release`
