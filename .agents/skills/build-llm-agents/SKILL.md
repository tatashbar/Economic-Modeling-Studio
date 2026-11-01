---
name: build-llm-agents
description: "Builds LLM-agent economic simulations (synthetic households, firms, forecasters, negotiators) with sensitivity and human-data checks."
---
<!-- Generated from .claude/skills/build-llm-agents/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-llm-agents — Build LLM Agents

**Category:** Build (AI) · **Primary agent:** `llm-agent-simulation-specialist`

Builds LLM-agent economic simulations (synthetic households, firms, forecasters, negotiators) with sensitivity and human-data checks.

Arguments: whatever the user wrote after the command name.

## Purpose
Build an economic simulation populated by LLM-powered agents (synthetic households, firms, forecasters or negotiators) and measure how much of what they do reflects stable behavior rather than prompt wording or model choice. The output is an exploratory simulation with sensitivity and reproducibility evidence, compared with human data wherever it exists.

**Use it when** piloting surveys or experiments, exploring expectation formation and reactions to communication, or prototyping behavioral rules for agent-based models.

**Do not use it when** results will be presented as evidence of human behavior without validation, or when a calibrated behavioral or agent-based model already answers the question (`/build-abm`).

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

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Personas | survey-grounded demographics, stylized types | Representativeness |
| Information and memory | fixed context, evolving memory, news feeds | Dynamics of beliefs |
| Protocol | survey questions, market game, negotiation | What is measured |
| Models | at least two LLMs; versions pinned | Model dependence |
| Validation data | human surveys, lab experiments | Strength of conclusions |

## Workflow
1. Specify agent personas, information sets, memory and decision protocols
   - Use structured outputs; record prompts and versions
2. Run pilot simulations across prompts, seeds and at least two LLMs
3. Compare behavior to human experimental or survey evidence
   - Compare means, dispersion, treatment effects and heterogeneity
   - Check for contamination from well-known published experiments
4. Quantify prompt and model sensitivity; label results exploratory unless validated
5. Document reproducibility details (model versions, temperature, seeds)

## Checkpoints with the user
- After the design: confirm personas and protocol
- After pilots: confirm sensitivity is acceptable before scaling
- Before reporting: agree on the labeling of results

## Common pitfalls
- Treating simulated agents as representative humans
- Results driven by one prompt wording
- LLMs reciting famous experiments rather than behaving
- Large simulated samples giving false precision

## Output
`models/llm/<name>-agents/`

The folder holds persona and protocol definitions, prompts, run scripts, raw outputs, sensitivity analysis, the human-data comparison and a reproducibility record.

## Gate / verdict
- Sensitivity across prompts and models reported
- Output labelled exploratory unless validated against human data
- Prompts, model versions, temperature and seeds are archived
- Contamination risk is assessed

## Suggested next steps
- `/ai-audit`
- `/policy-simulation`
