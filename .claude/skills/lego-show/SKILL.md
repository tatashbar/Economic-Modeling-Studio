---
name: lego-show
description: "Shows a model as a lego set: baseplate, bricks, joints, open studs, parts bin and suggested bricks, in text, an HTML picture, or a Mermaid diagram."
argument-hint: "[manifest path] [--html] [--mermaid]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /lego-show — Lego Show

**Category:** Lego (Modular Models) · **Primary agent:** `modeling-methodology-specialist`

Shows a model as a lego set: baseplate, bricks, joints, open studs, parts bin and suggested bricks, in text, an HTML picture, or a Mermaid diagram.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - A model.lego.json manifest (create one with /lego-map)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `modeling-methodology-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Run `python tools/lego.py show <manifest>` and read the output to the user in plain language: what the core is, which bricks are attached, what each exchanges
2. Explain the open studs: which inputs currently run on stubs and what that means economically (for example 'exports are exogenous, so the exchange rate cannot affect demand through trade')
3. Offer the catalog bricks that would fill each open stud, and the parts bin of detached bricks
4. Point out simultaneous blocks (solved jointly) and the solve order
5. On request, write the picture with `--html <file>` (a self-contained page) or `--mermaid` for documents. Bricks stack on the bricks whose outputs they read, with no limit on levels. To build the picture as a stepped pyramid, show the plan of `python tools/lego.py arrange <manifest>` and, with approval, add `--apply`; `--style grid` returns to the default. Positions change the picture only, never the wiring; report any `picture:` warnings from `check`

## Output
`(conversation); optionally lego-view.html next to the manifest`

## Gate / verdict
- The description matches the tool's output; nothing is inferred beyond it

## Suggested next steps
- `/lego-add`
- `/lego-detach`
- `/lego-swap`
