---
name: build-llm-pipeline
description: "Builds an LLM pipeline for extraction, classification or analysis with verification, evaluation and confidentiality controls."
argument-hint: "[task description]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-llm-pipeline — Build LLM Pipeline

**Category:** Build (AI) · **Primary agent:** `llm-economic-analyst`

Builds an LLM pipeline for extraction, classification or analysis with verification, evaluation and confidentiality controls.

Arguments: `$ARGUMENTS`

## Purpose
Build an LLM pipeline for extraction, classification or analysis of economic documents that is evaluated like a measurement instrument: confidentiality cleared first, a labelled evaluation set built before prompts, structured outputs verified against sources, and accuracy measured against agreed thresholds. The output is a pipeline with an evaluation card and defined human review.

**Use it when** large document collections must be read for numbers, measures, stances or facts, or text must be classified at scale.

**Do not use it when** questions are answered from a document collection with citations (`/build-rag-kb`), or the task is to simulate agents (`/build-llm-agents`).

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

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Model and endpoint | internal, approved external, local | Confidentiality and quality |
| Output format | JSON schema, labels, short text | Verifiability |
| Verification | source quotation, cross-check with databases, consistency reruns | Error detection |
| Thresholds | accuracy and numeric faithfulness targets | Release decision |
| Human review | full, sampled, exceptions only | Cost and risk |

## Workflow
1. Classify input data by confidentiality; confirm the allowed model/endpoint before any prompt is written
2. Create a labelled evaluation set before building prompts
   - Cover document types, languages and hard cases; keep a held-out portion
3. Design structured-output prompts and verification steps (source cross-check, schema validation)
4. Evaluate accuracy, numeric faithfulness and stability across prompt/model versions
   - Error analysis by field and document type
5. Document failure modes, human review requirements and monitoring
   - Freeze prompt versions; rerun evaluation after any model change

## Checkpoints with the user
- After the confidentiality check: confirm the endpoint
- After the evaluation set: confirm thresholds
- After evaluation: approve release and review level

## Common pitfalls
- Prompts tuned on the evaluation set
- Fluent outputs accepted without source checks
- Silent model-version changes
- Confidential documents sent to unapproved services

## Output
`models/llm/<name>/ and docs/models/<name>/llm-eval-card.md`

The pipeline folder holds prompts, schemas, code, the evaluation set and results; the evaluation card documents accuracy, failure modes, human review and monitoring.

## Gate / verdict
- Confidentiality approved
- Evaluation on a labelled set meets agreed thresholds
- Human review defined
- Every extracted number is traceable to its source
- Evaluation is rerun after any model or prompt change

## Suggested next steps
- `/ai-audit`
- `/validate-model`
