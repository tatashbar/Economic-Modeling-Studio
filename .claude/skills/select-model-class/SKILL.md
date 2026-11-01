---
name: select-model-class
description: "Recommends the model class for a question (small/medium/large; traditional, structural, data-driven, AI) with trade-offs and benchmarks."
argument-hint: "[question or path to scope note]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /select-model-class — Select Model Class

**Category:** Scoping & Design · **Primary agent:** `economic-reasoning-specialist`

Recommends the model class for a question (small/medium/large; traditional, structural, data-driven, AI) with trade-offs and benchmarks.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - docs/briefs/<name>-scope.md or an equivalent description
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `economic-reasoning-specialist` — primary agent; coordinates the work and integrates results
- `semi-structural-gap-modeler` — Builds quarterly projection and semi-structural gap models
- `open-economy-dsge-specialist` — Builds small open-economy DSGE models
- `var-vecm-specialist` — Builds VAR, SVAR and VECM models
- `deep-learning-architect` — Designs deep learning architectures for macro-financial data

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Ask the relevant specialists (in parallel) for their best candidate approach and its main weakness
2. Compare candidates on: question fit, transparency, data needs, build time, validation effort, run time, communicability
3. Present 2-4 options with a recommendation; always include a simple benchmark
4. Record the user's decision in an ADR

## Output
`docs/architecture/adr-model-class-<name>.md`

## Gate / verdict
- At least one simple benchmark is included
- Reasons for rejecting alternatives are recorded

## Suggested next steps
- `/model-brief`
- `/quick-model`
