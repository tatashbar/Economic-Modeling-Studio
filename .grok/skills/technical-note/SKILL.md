---
name: technical-note
description: "Writes a technical note or methodology paper from model work: motivation, method, results, robustness, limits."
---
<!-- Generated from .claude/skills/technical-note/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /technical-note — Technical Note

**Category:** Documentation · **Primary agent:** `technical-documentation-specialist`

Writes a technical note or methodology paper from model work: motivation, method, results, robustness, limits.

Arguments: whatever the user wrote after the command name.

## Purpose
Write a technical note or methodology paper from model work: motivation, method, data, results, robustness and limitations, written for modelers and reviewers, with notation consistent with the specification and every number linked to a model run. The output can be reviewed, replicated and cited.

**Use it when** a model, method or analysis must be documented for peers, reviewers or publication.

**Do not use it when** the audience is non-technical (`/policy-brief`) or a short use summary is enough (`/model-card`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Model outputs
   - Validation report
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `technical-documentation-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Audience | internal modelers, external reviewers, journal | Depth and style |
| Structure | methodology paper, results note, model documentation | Emphasis |
| Robustness | appendix tables, main text | Visibility |

## Workflow
1. Agree audience and outline with the user
2. Draft section by section; keep notation consistent with the model spec
   - Cite literature verified against sources
3. Link all numbers to model runs; include limitations
4. Run a replication check on key tables

## Checkpoints with the user
- After the outline
- After each major section

## Common pitfalls
- Notation drifting from the specification
- Robustness relegated or omitted
- Unverified citations

## Output
`docs/notes/<name>.md`

The note includes motivation, method, data, results, robustness, limitations and references, with a notation table and links to model runs.

## Gate / verdict
- All numbers link to a model run in the registry
- Key tables pass a replication check
- Limitations are stated in the main text

## Suggested next steps
- `/policy-brief`
