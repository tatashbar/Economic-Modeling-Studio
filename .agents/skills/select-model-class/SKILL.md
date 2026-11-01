---
name: select-model-class
description: "Recommends the model class for a question (small/medium/large; traditional, structural, data-driven, AI) with trade-offs and benchmarks."
---
<!-- Generated from .claude/skills/select-model-class/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /select-model-class — Select Model Class

**Category:** Scoping & Design · **Primary agent:** `economic-reasoning-specialist`

Recommends the model class for a question (small/medium/large; traditional, structural, data-driven, AI) with trade-offs and benchmarks.

Arguments: whatever the user wrote after the command name.

## Purpose
Recommend the model class that best fits a scoped question (small or large; accounting, semi-structural, structural, econometric, data-driven or AI), with the trade-offs made explicit and a simple benchmark always included. The output is an architecture decision record that documents why the chosen class won and why the alternatives lost.

**Use it when** a question is scoped (`/scope-question`) and the team must choose what to build or reuse.

**Do not use it when** the model class is fixed by an institutional decision; then document it directly in the brief (`/model-brief`).

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Criterion | What to compare |
|---|---|
| Question fit | Can the class answer the question at all? |
| Transparency | Can users understand and explain results? |
| Data needs | Are the required data available at the right frequency? |
| Build and validation effort | Weeks or months; depth of validation needed |
| Run time | Fit for regular use or one-off |
| Modularity | Can existing lego bricks be reused or attached? |

## Workflow
1. Ask the relevant specialists (in parallel) for their best candidate approach and its main weakness
2. Compare candidates on: question fit, transparency, data needs, build time, validation effort, run time, communicability
   - Check which candidates can reuse existing lego sets and bricks
3. Present 2-4 options with a recommendation; always include a simple benchmark
4. Record the user's decision in an ADR

## Checkpoints with the user
- After candidates: confirm the comparison criteria
- At the recommendation: record the decision

## Common pitfalls
- Choosing the most sophisticated model by default
- No simple benchmark to judge added value
- Ignoring counterpart capacity to maintain the model

## Output
`docs/architecture/adr-model-class-<name>.md`

The ADR records the question, candidates, comparison, decision, benchmark and reasons for rejecting alternatives.

## Gate / verdict
- At least one simple benchmark is included
- Reasons for rejecting alternatives are recorded
- Maintenance capacity is considered in the decision

## Suggested next steps
- `/model-brief`
- `/quick-model`
