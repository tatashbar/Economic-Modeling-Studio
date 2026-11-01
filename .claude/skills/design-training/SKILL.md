---
name: design-training
description: "Designs a capacity-development program: needs assessment, curriculum, labs, assessment and ownership-transfer plan."
argument-hint: "[audience and model]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /design-training — Design Training

**Category:** Capacity Development · **Primary agent:** `training-curriculum-designer`

Designs a capacity-development program: needs assessment, curriculum, labs, assessment and ownership-transfer plan.

Arguments: `$ARGUMENTS`

## Purpose
Design a capacity-development program that leaves counterparts able to run, maintain and extend a model on their own: needs assessment, a progressive curriculum by model class, labs with open or synthetic data, assessments, and a clear criterion for transferring model ownership, followed by mentoring. The output is a program measured by what participants can do, not by attendance.

**Use it when** a model is handed over, a counterpart institution builds modeling capacity, or a team adopts a new model class.

**Do not use it when** a single exercise is enough (`/create-exercise`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Counterpart description
   - Model to be transferred
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `training-curriculum-designer` — primary agent; coordinates the work and integrates results
- `technical-documentation-specialist` — Writes technical documentation
- `stakeholder-liaison-specialist` — Interfaces with stakeholders and counterparts

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Level | introductory, intermediate, advanced | Curriculum |
| Model classes | gap models, FPAS, DSGE, CGE, econometrics, ML | Content |
| Delivery | workshops, blended, embedded mentoring | Retention |
| Ownership criterion | independent forecast round, model modification, validation | Success measure |

## Workflow
1. Assess counterpart skills, tools, data access and goals
2. Design a progressive curriculum by model class; create labs with open or synthetic data
   - Use lego sets to teach model structure by assembling and swapping bricks
3. Define assessments and the criterion for model ownership transfer
4. Draft follow-up mentoring schedule

## Checkpoints with the user
- After the needs assessment
- After the curriculum outline

## Common pitfalls
- Lecture-heavy delivery
- Labs that depend on confidential data
- No follow-up after workshops

## Output
`docs/training/<program>/`

The program folder holds the needs assessment, curriculum, labs, assessments, ownership criterion and mentoring schedule.

## Gate / verdict
- Training data are non-confidential or synthetic; ownership-transfer criterion defined
- Assessments are practical tasks

## Suggested next steps
- `/create-exercise`
