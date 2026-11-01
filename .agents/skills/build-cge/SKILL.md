---
name: build-cge
description: "Builds a CGE model (static or recursive-dynamic, single- or multi-region) with benchmark replication, closures, elasticity sensitivity and welfare decomposition."
---
<!-- Generated from .claude/skills/build-cge/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-cge — Build CGE

**Category:** Build · **Primary agent:** `cge-modeling-specialist`

Builds a CGE model (static or recursive-dynamic, single- or multi-region) with benchmark replication, closures, elasticity sensitivity and welfare decomposition.

Arguments: whatever the user wrote after the command name.

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Approved model-spec
   - Balanced SAM or global database
   - Elasticity sources
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `cge-modeling-specialist` — primary agent; coordinates the work and integrates results
- `input-output-sam-specialist` — Builds input-output, supply-use and social accounting matrix frameworks
- `trade-policy-simulation-specialist` — Simulates trade policy with quantitative trade models
- `tax-benefit-microsimulation-specialist` — Builds tax-benefit microsimulation
- `carbon-pricing-emissions-specialist` — Analyzes carbon pricing and emissions policy

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Workflow
1. Agree the structure: regions, sectors, factors, production nests, trade treatment and closures
2. Calibrate to the SAM; implement as a complementarity problem; replicate the benchmark exactly
3. Test homogeneity, Walras' law and numeraire invariance
4. Run policy scenarios under at least two closures; run systematic sensitivity on key elasticities
5. Report sectoral, welfare (EV/CV) and, where possible, household effects; document the model for handover
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/cge/<name>/ (+ model.lego.json)`

## Gate / verdict
- Benchmark replicated to tolerance
- Closure and elasticity sensitivity reported
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/trade-policy-analysis`
- `/carbon-pricing-analysis`
- `/distributional-analysis`
- `/validate-model`
- `/lego-map`
