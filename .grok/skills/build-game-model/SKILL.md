---
name: build-game-model
description: "Builds a game-theoretic or mechanism-design model: specification, equilibria, computation and policy interpretation."
---
<!-- Generated from .claude/skills/build-game-model/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-game-model — Build Game Model

**Category:** Build · **Primary agent:** `game-theory-specialist`

Builds a game-theoretic or mechanism-design model: specification, equilibria, computation and policy interpretation.

Arguments: whatever the user wrote after the command name.

## Purpose
Build a game-theoretic or mechanism-design model in which outcomes depend on strategic interaction: policymakers, creditors, firms or countries choosing actions that depend on what others do. The output is a specified game, all of its equilibria within the search, an explicit selection argument where several exist, and policy implications whose dependence on timing, information and commitment is shown.

**Use it when** strategy is central: policy coordination, credibility and commitment, bargaining and restructuring, auctions and incentive design, crisis coordination.

**Do not use it when** agents take prices as given and strategic interaction is negligible (`/build-dsge`, `/build-cge`), or learning dynamics among many agents are the focus (`/build-abm`, `/build-drl-policy`).

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

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Game form | normal-form, extensive-form, repeated, dynamic stochastic | Equilibrium concepts available |
| Information | complete, incomplete (Bayesian), global games | Multiplicity and selection |
| Commitment | commitment, discretion, reputation | Time-consistency and welfare |
| Solution | analytical, numerical enumeration, homotopy, value iteration | Completeness of the equilibrium set |
| Calibration | stylized, calibrated to data | Quantitative interpretation |

## Workflow
1. Formalize players, strategies, information and payoffs from economic primitives
   - Payoffs derived from objectives (mandates, profits, utility), not chosen to reach a result
2. Solve for equilibria (analytical and numerical); list all equilibria and the selection argument
   - Verify equilibrium conditions numerically
3. Run comparative statics and welfare analysis
   - Vary timing, information and commitment assumptions
4. Calibrate where feasible and test against stylized facts
5. Translate into policy implications and caveats
   - State which conclusions survive alternative assumptions
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Checkpoints with the user
- After formalization: confirm players, timing and payoffs
- After solution: confirm the selection argument if equilibria are multiple
- Before policy implications: confirm which assumptions are realistic for the case

## Common pitfalls
- Reporting one equilibrium when several exist
- Assuming commitment the player cannot deliver
- Payoffs reverse-engineered from the desired outcome
- Off-equilibrium beliefs left unspecified in dynamic games

## Output
`models/games/<name>/ (+ model.lego.json)`

The folder holds the game specification, solution code, equilibrium list with verification, comparative statics, calibration files where used and the lego manifest.

## Gate / verdict
- All equilibria found are reported
- Payoffs trace to primitives
- Lego manifest passes `python tools/lego.py check`
- Equilibrium conditions are verified numerically
- Sensitivity to timing, information and commitment is reported

## Suggested next steps
- `/validate-model`
- `/policy-simulation`
- `/lego-map`
