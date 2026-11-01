---
name: build-llm-agents
description: "Builds LLM-agent economic simulations (synthetic households, firms, forecasters, negotiators) with sensitivity and human-data checks."
---
<!-- Generated from .claude/skills/build-llm-agents/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-llm-agents — Build LLM Agents

**Category:** Build (AI) · **Primary agent:** `llm-agent-simulation-specialist`

Builds LLM-agent economic simulations (synthetic households, firms, forecasters, negotiators) with sensitivity and human-data checks.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Simulation design
   - Human data for calibration (if any)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `llm-agent-simulation-specialist` — primary agent; coordinates the work and integrates results
- `agent-based-modeling-specialist` — Builds agent-based macro and financial models
- `multi-agent-rl-specialist` — Builds multi-agent reinforcement learning systems for strategic economic interaction

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Specify agent personas, information sets, memory and decision protocols
2. Run pilot simulations across prompts, seeds and at least two LLMs
3. Compare behavior to human experimental or survey evidence
4. Quantify prompt and model sensitivity; label results exploratory unless validated
5. Document reproducibility details (model versions, temperature, seeds)

## Output
`models/llm/<name>-agents/`

## Gate / verdict
- Sensitivity across prompts and models reported
- Output labelled exploratory unless validated against human data

## Suggested next steps
- `/ai-audit`
- `/policy-simulation`
