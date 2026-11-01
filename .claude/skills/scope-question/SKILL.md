---
name: scope-question
description: "Turns a policy question into a precise modeling question: decision, audience, horizon, outputs and acceptable uncertainty."
argument-hint: "[question or topic]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /scope-question — Scope Question

**Category:** Scoping & Design · **Primary agent:** `economic-reasoning-specialist`

Turns a policy question into a precise modeling question: decision, audience, horizon, outputs and acceptable uncertainty.

Arguments: `$ARGUMENTS`

## Purpose
Turn a broad policy question into a precise modeling question: the decision it informs, who decides and when, the horizon and outputs needed, the mechanisms that matter, and the uncertainty that is acceptable. The output is a one-page scoping note that prevents building the wrong model.

**Use it when** starting any modeling project, or when a request is vague ("what is the impact of X?").

**Do not use it when** the question is already scoped and the model class is the open issue (`/select-model-class`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - User's description of the question
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `economic-reasoning-specialist` — primary agent; coordinates the work and integrates results
- `policy-relevance-specialist` — Clarifies the decision, audience and deadline, and reviews outputs for decision-relevance, honest uncertainty and appropriate caveats
- `stakeholder-liaison-specialist` — Interfaces with stakeholders and counterparts

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Output type | point estimate, density, scenarios, welfare ranking | Model class and validation |
| Horizon | nowcast, short term, medium term, long term | Model class |
| Coverage | one country, region, global | Model size |
| Precision needed | order of magnitude, tight range | Effort and time |

## Workflow
1. Ask: what decision will this inform, who decides, by when, and what would change their mind?
2. Clarify horizon, frequency, country coverage, and outputs required (point, density, scenario, welfare)
3. List the economic mechanisms that matter and those that can be ignored
   - Note which mechanisms are contested and need alternatives
4. Draft a one-page scoping note and ask the user to approve each section

## Checkpoints with the user
- After the decision questions
- After each section of the scoping note

## Common pitfalls
- Starting from the model the team already has rather than the question
- Unstated success criteria
- Mechanisms included because they are fashionable rather than relevant

## Output
`docs/briefs/<name>-scope.md`

The scoping note states the decision, audience, deadline, horizon, outputs, mechanisms, acceptable uncertainty and success criteria.

## Gate / verdict
- Decision, audience, horizon and success criteria are all stated
- Mechanisms to include and to ignore are listed

## Suggested next steps
- `/select-model-class`
- `/model-brief`
