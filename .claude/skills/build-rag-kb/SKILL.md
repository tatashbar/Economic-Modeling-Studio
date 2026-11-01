---
name: build-rag-kb
description: "Builds a retrieval-augmented knowledge base over document collections with access control and faithfulness evaluation."
argument-hint: "[document collection]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-rag-kb — Build RAG Kb

**Category:** Build (AI) · **Primary agent:** `rag-knowledge-specialist`

Builds a retrieval-augmented knowledge base over document collections with access control and faithfulness evaluation.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Document collection
   - Access-control policy
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `rag-knowledge-specialist` — primary agent; coordinates the work and integrates results
- `data-governance-metadata-specialist` — Owns data governance and metadata
- `llm-red-team-specialist` — Red-teams LLM systems
- `mlops-engineer` — Engineers MLOps for models

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Inventory documents, classify confidentiality, and set access rules
2. Design chunking, embeddings, hybrid retrieval and citation formatting
3. Create a question set with gold answers and citations
4. Evaluate retrieval recall, answer faithfulness and refusal behavior
5. Red-team with prompt-injection documents; deploy with monitoring

## Output
`models/llm/<name>-rag/`

## Gate / verdict
- Access control enforced at retrieval time
- Faithfulness and injection tests passed

## Suggested next steps
- `/ai-audit`
- `/model-release`
