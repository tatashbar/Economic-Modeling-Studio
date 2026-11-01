---
name: lego-add
description: "Adds a brick to a model, for example a trade sector, carbon-pricing block or labor market, after checking the wiring and listing what changes."
argument-hint: "[manifest path] [brick id | brick file]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /lego-add — Lego Add

**Category:** Lego (Modular Models) · **Primary agent:** `modeling-methodology-specialist`

Adds a brick to a model, for example a trade sector, carbon-pricing block or labor market, after checking the wiring and listing what changes.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - A model.lego.json manifest
   - The brick: a catalog entry, or a spec created with /lego-brick
   - Code or specification for the brick (to implement and calibrate it)
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `modeling-methodology-specialist` — primary agent; coordinates the work and integrates results
- `economic-reasoning-specialist` — Frames the economic question and tests whether results make economic sense
- `model-validation-specialist` — Performs independent model validation
- `python-julia-engineer` — Engineers Python, Julia and R modeling code

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Identify the need. If the model lacks a component (for example trade), check `python tools/lego.py show` for open studs and `catalog` for a matching brick. If none exists, run `/lego-brick`, and build the component with the relevant `/build-*` command
2. Dry-run: `python tools/lego.py attach <manifest> <brick>`. Present the plan: new joints, stubs retired (inputs that become endogenous), stubs activated, new simultaneous blocks, frequency or bridge warnings, conflicts, and the neighbours that must be re-validated
3. Ask the user to approve. Resolve any error first (conflicting provider or slot, missing port definition, unit mismatch, missing bridge). Do not use `--force` unless the user explicitly asks
4. Apply with `--apply --note '<why>'`
5. Neutral-attachment test: run the model with the new brick set to its neutral values (for example zero tariff change, trade elasticities that reproduce the previous exogenous path). The baseline must match the pre-attachment baseline within tolerance. If it does not, the joint is wrong
6. Calibrate the new brick and the parameters of its neighbours that it touches, re-run the baseline, and compare with the previous baseline. Explain every difference through the new channel
7. Re-verify the accounting identities and re-validate the bricks marked stale (`/validate-model` on those bricks and their joints)

## Output
`Updated model.lego.json (+ history entry) and a short change note in docs/models/<name>/`

## Gate / verdict
- No errors from `check`
- Neutral-attachment test passes within tolerance
- Identities re-verified
- Neighbouring bricks re-validated before any release

## Suggested next steps
- `/lego-check`
- `/validate-model`
- `/model-release`
