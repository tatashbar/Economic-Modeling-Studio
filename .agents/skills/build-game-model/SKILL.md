---
name: build-game-model
description: "Builds a game-theoretic or mechanism-design model: specification, equilibria, computation and policy interpretation."
---
<!-- Generated from .claude/skills/build-game-model/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-game-model — Build Game Model

**Category:** Build · **Primary agent:** `game-theory-specialist`

Builds a game-theoretic or mechanism-design model: specification, equilibria, computation and policy interpretation.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec with players, actions, information, payoffs
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `game-theory-specialist` — primary agent; coordinates the work and integrates results
- `mechanism-design-specialist` — Designs mechanisms and incentives
- `policy-interaction-games-specialist` — Models policy interaction
- `sovereign-crisis-games-specialist` — Models sovereign debt, default and currency crises

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Formalize players, strategies, information and payoffs from economic primitives
2. Solve for equilibria (analytical and numerical); list all equilibria and the selection argument
3. Run comparative statics and welfare analysis
4. Calibrate where feasible and test against stylized facts
5. Translate into policy implications and caveats
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/games/<name>/ (+ model.lego.json)`

## Gate / verdict
- All equilibria found are reported
- Payoffs trace to primitives
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/validate-model`
- `/policy-simulation`
- `/lego-map`
