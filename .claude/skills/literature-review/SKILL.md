---
name: literature-review
description: "Reviews the theoretical and empirical literature and existing models in use for a modeling question."
argument-hint: "[topic]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /literature-review — Literature Review

**Category:** Scoping & Design · **Primary agent:** `economic-reasoning-specialist`

Reviews the theoretical and empirical literature and existing models in use for a modeling question.

Arguments: `$ARGUMENTS`

## Purpose
Review the theory, empirical evidence and existing models relevant to a modeling question, so that mechanisms, parameter values and benchmarks are grounded in what is known. The output is an annotated bibliography and an evidence table in which every number is traceable to a verified source and anything unverified is clearly flagged.

**Use it when** starting a model, choosing calibrations, explaining results, or checking whether a finding is in line with the literature.

**Do not use it when** a quick orientation is enough and no numbers will be used.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Topic; document corpus if available (`docs/references/`)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `economic-reasoning-specialist` — primary agent; coordinates the work and integrates results
- `growth-productivity-specialist` — Analyzes growth and productivity
- `llm-economic-analyst` — Uses LLMs for economic analysis
- `rag-knowledge-specialist` — Builds retrieval-augmented knowledge systems over document collections

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Scope | mechanisms, parameter estimates, existing models, policy evidence | Focus of the table |
| Sources | project reference collection, journals, working papers | Coverage and reliability |
| Depth | key references, systematic review, meta-analysis | Effort and confidence |
| Country focus | global, region, comparable economies | Transferability |

## Workflow
1. Search the project's reference collection first; use external sources only where permitted
2. Summarize the core theoretical mechanisms, standard calibrations and empirical estimates
   - Note sample, method and country for each estimate
3. List existing models and known strengths and weaknesses
4. Verify every cited number against its source; mark unverifiable claims clearly
   - Never cite from memory alone
5. Produce an annotated bibliography and an evidence table

## Checkpoints with the user
- After scope: confirm questions the review must answer
- After the evidence table: confirm which estimates feed the model

## Common pitfalls
- Citations from memory that turn out wrong
- Estimates transferred across very different economies
- Ignoring publication bias in the literature
- Reviewing only supportive evidence

## Output
`docs/references/<topic>-review.md`

The review contains the annotated bibliography, the evidence table with sample, method and country for each estimate, and flags on unverified items.

## Gate / verdict
- Every cited number is traceable to a source; unverified items are flagged
- Evidence contrary to the expected result is included

## Suggested next steps
- `/model-spec`
- `/calibration-plan`
