---
name: setup-environment
description: "Sets up language toolchains, project folders, data classification levels and studio configuration for the chosen model stack."
---
<!-- Generated from .claude/skills/setup-environment/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /setup-environment — Setup Environment

**Category:** Onboarding · **Primary agent:** `python-julia-engineer`

Sets up language toolchains, project folders, data classification levels and studio configuration for the chosen model stack.

Arguments: whatever the user wrote after the command name.

## Purpose
Set up the technical foundation for modeling work: approved language toolchains, folder structure with data classification levels, reproducible environment files, and studio configuration, verified by a smoke test in each chosen language. Confidential-data handling is configured before any data enter the project.

**Use it when** starting a new project or onboarding a team to the studio.

**Do not use it when** only configuration values change (`/settings`).

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Languages | Python, Julia, R, MATLAB/Dynare | Toolchains and skills used |
| Environments | lock files, containers | Reproducibility |
| Data classes | public, internal, restricted, confidential | Handling rules |

## Workflow
1. Ask which stack(s) the team uses and which are approved by your IT policy
2. Create or verify the folder skeleton and data classification levels (`data/raw`, `data/processed`, `data/restricted`)
3. Propose environment files (lock files, containers) and ask before creating them
4. Record decisions in `studio-config.yaml` and a stack ADR
5. Verify by running a minimal smoke test in each chosen language
   - Include `python tools/lego.py` on a sample manifest to confirm the lego engine runs

## Checkpoints with the user
- Before creating environment files
- Before recording the stack decision

## Common pitfalls
- Tools not approved by institutional IT
- Unpinned environments
- Data added before classification is configured

## Output
`studio-config.yaml and docs/architecture/adr-stack.md`

The configuration file records the stack and defaults; the ADR records the decision and its reasons.

## Gate / verdict
- Smoke test runs from a clean shell
- Confidential-data handling is configured before any data is added
- Environment files pin versions

## Suggested next steps
- `/data-requirements`
- `/model-brief`
