# Economic Modeling Studio — Instructions for Coding Agents

This project turns a coding-agent session into a coordinated economic modeling studio: 119 specialist agents, 85 workflow commands, path-scoped rules, templates and guardrails. It covers small, medium and large models across semi-structural, structural (DSGE, HANK, multi-country), input-output / CGE / trade, climate and energy, econometric, and data-driven and AI-based approaches.

These instructions apply to any coding agent: Claude Code, Codex, Cursor, Grok Build, Gemini CLI / Antigravity, GitHub Copilot and others that read `AGENTS.md`.

The user is the decision maker. Agents advise, build and challenge; they do not decide economics or policy. Agents are organized by area of expertise, not by reporting lines.

## At the start of a session
1. Read `production/session-state/active.md` and `production/stage.txt` if they exist. Resume from them.
2. If there is no active task, offer the `start` command (onboarding and routing) or `help` (what exists).

## Commands, agents and rules
| What | Where | How to use it |
|---|---|---|
| Workflow commands (85) | `.claude/skills/<name>/SKILL.md`, mirrored to `.agents/skills/` and `.grok/skills/` | Invoke by name: `/name` in Claude Code, Cursor, Grok and Gemini; `$name` in Codex. Any agent can also read the file and follow it. Catalog: `docs/skill-catalog.md` |
| Specialist agents (119) | `.claude/agents/<name>.md` | Run as subagents where your tool supports them; otherwise read the agent's file and apply its instructions. Roster: `docs/agent-roster.md` |
| Path-scoped rules | `.claude/rules/*.md`, mirrored to `.cursor/rules/` | Before editing a file, follow every rule whose paths match it (table below) |
| Process documents | `.claude/docs/` | Collaboration protocol, coordination, phase gates, risk levels, model classes, confidentiality |

The files under `.agents/`, `.grok/` and `.cursor/rules/` are generated. Edit the sources in `.claude/`, then run `python tools/sync_agents.py`.

<!-- BEGIN GENERATED: rules -->
| When you work on | Follow |
|---|---|
| `models/ai/**` | `.claude/rules/ai-ml-code.md` |
| `data/**`, `pipelines/**`, `src/data/**` | `.claude/rules/data-pipelines.md` |
| `docs/**` | `.claude/rules/documentation.md` |
| `models/dsge/**`, `models/multicountry/**` | `.claude/rules/dsge-code.md` |
| `models/econometrics/**` | `.claude/rules/econometrics-code.md` |
| `forecasts/**` | `.claude/rules/forecasts.md` |
| `models/**/model.lego.json`, `lego/**` | `.claude/rules/lego-manifests.md` |
| `models/llm/**` | `.claude/rules/llm-code.md` |
| `models/**` | `.claude/rules/model-code.md` |
| `notebooks/**`, `scripts/**` | `.claude/rules/notebooks-and-scripts.md` |
| `data/restricted/**`, `data/confidential/**` | `.claude/rules/restricted-data.md` |
| `models/ai/**/*drl*/**`, `models/ai/**/*rl*/**` | `.claude/rules/rl-code.md` |
| `models/io-sam/**`, `models/cge/**`, `models/trade/**`, `models/climate/**` | `.claude/rules/sectoral-trade-climate-code.md` |
| `models/semi-structural/**`, `models/fpas/**`, `models/financial-programming/**` | `.claude/rules/semi-structural-code.md` |
| `tests/**`, `**/test_*.py`, `**/*_test.jl`, `**/test_*.m` | `.claude/rules/tests.md` |
| `validation/**` | `.claude/rules/validation.md` |
<!-- END GENERATED: rules -->

## Non-negotiable rules
1. **Collaborate, don't decide autonomously.** Ask → options → decision → draft → approval → write. See `.claude/docs/collaboration-protocol.md`.
2. **Independence.** The builder of a model never validates it.
3. **No fabrication.** Never invent data, parameters, citations or results. Missing inputs → `NOT ASSESSED — NO DATA`.
4. **Benchmark first.** Every complex or AI model is compared with a simple, transparent benchmark.
5. **Reproducibility.** Seeds, versions, data vintages, and a one-command replication path for every released result.
6. **Uncertainty is part of the result.** No forecast, scenario or estimate leaves the studio without uncertainty and key assumptions.
7. **Confidentiality.** Respect data classification levels. Never read `data/restricted/`. No restricted or confidential data in prompts, logs or external services without written authorization. See `.claude/docs/confidentiality-and-ai-use.md`.
8. **Raw data is immutable.** Never change, move or delete a file in `data/raw/`; write a new vintage or a processed version.
9. **AI outputs are claims until verified.** LLM-produced numbers, citations and code need source traceability and tests.
10. **No release without review.** See `.claude/docs/phase-gates.md` and `.claude/docs/model-risk-levels.md`.

## Model classes and workflow
Small, medium and large models share one lifecycle with different depth: **Concept → Design → Build → Estimate → Validate → Release/Operate**. See `.claude/docs/model-classes.md`. Settings live in `studio-config.yaml`.

## Lego view (modular models)
Models are represented as a **lego set**: one baseplate (the core model) plus bricks (components such as a trade sector or a carbon-pricing block) that connect through studs (declared variables with units and timing). A needed input that no brick provides runs on a documented **stub**, so a model works without optional components and a brick can be attached, detached or swapped without breaking it. The manifest is `models/<family>/<name>/model.lego.json`, the engine is `python tools/lego.py`, and the catalog is `lego/catalog/`. Commands: `lego-map`, `lego-show`, `lego-add`, `lego-detach`, `lego-swap`, `lego-check`, `lego-brick`. Every `build-*` command registers a manifest. Always show the plan (dry run) and get approval before `--apply`. Record a brick's validation result only with `python tools/lego.py validate <manifest> <brick> --report <path>`. Bricks stack vertically with no limit on levels; `python tools/lego.py arrange <manifest> --apply` builds the picture as a stepped pyramid (positions only, never wiring). Declare what each brick is made of (variables, equations, parameters, shocks, data, constraints) with `python tools/lego.py elements <manifest> <brick> --from-mod <file>` or `--set`; the picture colours studs by these elements and `check` flags non-square bricks, unsourced parameters and unverified constraints. The tool checks wiring only; economics stays with calibration and validation. Guide: `docs/lego.md`.

## Directory map
| Path | Purpose |
|---|---|
| `models/<family>/<name>/` | Model code: semi-structural, fpas, financial-programming, dsge, multicountry, io-sam, cge, trade, climate, sfc, abm, games, ai, llm, econometrics; with `model.lego.json` (not needed for estimation-only econometric models) |
| `lego/` | Brick catalog, shared port definitions and worked examples for the lego view |
| `data/{raw,processed,external,restricted}` | Data by classification; raw is immutable; restricted is protected |
| `forecasts/` | Forecast rounds, nowcasts, scenarios, DSAs, stress tests, trade and climate analyses |
| `validation/` | Independent validation reports and audits |
| `docs/` | Briefs, model docs, notes, references, training, templates (`docs/templates/`) |
| `production/` | Session state, gates, milestones, retrospectives, releases, model registry |
| `tests/` | Tests for model code and pipelines |
| `.claude/` | Source of agents, commands, rules, hooks, process documents and Claude Code settings |
| `.agents/`, `.grok/`, `.cursor/` | Generated copies for other agents, and Cursor hooks |

## Session state
Keep `production/session-state/active.md` current: task, completed sections, decisions, next step.

## Guardrails
The guard scripts in `.claude/hooks/` block destructive commands, reads of restricted data and secrets, and changes to existing raw data. They run automatically in Claude Code (`.claude/settings.json`) and Cursor (`.cursor/hooks.json`). In every tool, the git pre-commit guard blocks committing restricted data, raw data and secrets: enable it once with `git config core.hooksPath .githooks`. Where no hook runs, the rules above still apply.

## Scope note
This is a template for work with public data. Before using non-public data, follow your organization's IT and data-governance requirements (see `.claude/docs/confidentiality-and-ai-use.md`).
