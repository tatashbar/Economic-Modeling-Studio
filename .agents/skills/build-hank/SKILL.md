---
name: build-hank
description: "Builds a heterogeneous-agent (HANK) model with household block, sequence-space solution and distributional outputs."
---
<!-- Generated from .claude/skills/build-hank/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-hank — Build HANK

**Category:** Build · **Primary agent:** `hank-specialist`

Builds a heterogeneous-agent (HANK) model with household block, sequence-space solution and distributional outputs.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec with household heterogeneity
   - Micro data targets
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `hank-specialist` — primary agent; coordinates the work and integrates results
- `neural-solver-specialist` — Solves high-dimensional economic models with neural networks
- `inequality-distribution-specialist` — Analyzes inequality and distribution
- `numerical-methods-specialist` — Specializes in numerical methods

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Implement the household block (endogenous grid method) and test it against known cases
2. Compute steady-state distribution and sequence-space Jacobians
3. Assemble general equilibrium; verify market clearing
4. Calibrate to micro and aggregate moments
5. Produce aggregate and distributional IRFs
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/dsge/<name>-hank/ (+ model.lego.json)`

## Gate / verdict
- Market clearing and aggregation checks pass
- Micro targets are matched or gaps documented
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/validate-model`
- `/distributional-analysis`
- `/lego-map`
