---
name: setup-environment
description: "Sets up language toolchains, project folders, data classification levels and studio configuration for the chosen model stack."
argument-hint: "[matlab-dynare|python|julia|r|mixed]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /setup-environment — Setup Environment

**Category:** Onboarding · **Primary agent:** `python-julia-engineer`

Sets up language toolchains, project folders, data classification levels and studio configuration for the chosen model stack.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - studio-config.yaml
   - installed toolchains
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `python-julia-engineer` — primary agent; coordinates the work and integrates results
- `matlab-dynare-engineer` — Engineers MATLAB, Dynare, IRIS, RISE and Octave codebases; legacy model maintenance and migration
- `reproducibility-engineer` — Guarantees reproducibility
- `data-governance-metadata-specialist` — Owns data governance and metadata

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Ask which stack(s) the team uses and which are approved by your IT policy
2. Create or verify the folder skeleton and data classification levels (`data/raw`, `data/processed`, `data/restricted`)
3. Propose environment files (lock files, containers) and ask before creating them
4. Record decisions in `studio-config.yaml` and a stack ADR
5. Verify by running a minimal smoke test in each chosen language

## Output
`studio-config.yaml and docs/architecture/adr-stack.md`

## Gate / verdict
- Smoke test runs from a clean shell
- Confidential-data handling is configured before any data is added

## Suggested next steps
- `/data-requirements`
- `/model-brief`
