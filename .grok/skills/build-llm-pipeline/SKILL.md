---
name: build-llm-pipeline
description: "Builds an LLM pipeline for extraction, classification or analysis with verification, evaluation and confidentiality controls."
---
<!-- Generated from .claude/skills/build-llm-pipeline/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-llm-pipeline — Build LLM Pipeline

**Category:** Build (AI) · **Primary agent:** `llm-economic-analyst`

Builds an LLM pipeline for extraction, classification or analysis with verification, evaluation and confidentiality controls.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Task definition
   - Labelled evaluation sample
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `llm-economic-analyst` — primary agent; coordinates the work and integrates results
- `nlp-text-as-data-specialist` — Turns text into economic data
- `llm-red-team-specialist` — Red-teams LLM systems
- `data-governance-metadata-specialist` — Owns data governance and metadata

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Classify input data by confidentiality; confirm the allowed model/endpoint before any prompt is written
2. Create a labelled evaluation set before building prompts
3. Design structured-output prompts and verification steps (source cross-check, schema validation)
4. Evaluate accuracy, numeric faithfulness and stability across prompt/model versions
5. Document failure modes, human review requirements and monitoring

## Output
`models/llm/<name>/ and docs/models/<name>/llm-eval-card.md`

## Gate / verdict
- Confidentiality approved
- Evaluation on a labelled set meets agreed thresholds
- Human review defined

## Suggested next steps
- `/ai-audit`
- `/validate-model`
