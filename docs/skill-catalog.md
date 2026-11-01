# Skill Catalog

85 slash commands. Source of truth: `.claude/skills/`.

## Onboarding

| Command | Primary agent | What it does |
|---|---|---|
| `/start`  | `project-planning-specialist` | First-time entry point. Asks what you want to model, detects project stage, and routes you to the right workflow. |
| `/help` [topic|skill-name|agent-name] | `project-planning-specialist` | Explains what the studio can do, lists skills and agents by category, and suggests what to do next based on project stage. |
| `/project-stage-detect`  | `project-planning-specialist` | Detects the project's stage (concept, design, build, estimate, validate, operate) from its files and reports gaps. |
| `/setup-environment` [matlab-dynare|python|julia|r|mixed] | `python-julia-engineer` | Sets up language toolchains, project folders, data classification levels and studio configuration for the chosen model stack. |
| `/adopt` [path-to-existing-model] | `modeling-methodology-specialist` | Brings an existing model or codebase into the studio: inventories it, reverse-documents it and plans validation and migration. |
| `/settings` [show|set <key> <value>] | `project-planning-specialist` | Views or changes studio configuration: rigor level, default languages, review requirements and confidentiality defaults. |

## Scoping & Design

| Command | Primary agent | What it does |
|---|---|---|
| `/scope-question` [question or topic] | `economic-reasoning-specialist` | Turns a policy question into a precise modeling question: decision, audience, horizon, outputs and acceptable uncertainty. |
| `/model-brief` [model name] | `project-planning-specialist` | Creates the model brief: purpose, model class, mechanisms, data, validation level, team, timeline and risks. |
| `/select-model-class` [question or path to scope note] | `economic-reasoning-specialist` | Recommends the model class for a question (small/medium/large; traditional, structural, data-driven, AI) with trade-offs and benchmarks. |
| `/literature-review` [topic] | `economic-reasoning-specialist` | Reviews the theoretical and empirical literature and existing models in use for a modeling question. |
| `/model-spec` [model name] | `modeling-methodology-specialist` | Writes the model specification: equations, timing, closures, steady state, shocks, observables and known limitations. |
| `/calibration-plan` [model name] | `bayesian-dsge-estimation-specialist` | Plans calibration and estimation: parameter sources, priors, moments, targets, identification checks. |
| `/data-requirements` [model name] | `data-engineer` | Defines data requirements and checks availability, vintages, confidentiality classification and quality for a model. |
| `/quick-model` [question] | `semi-structural-gap-modeler` | Fast path for a small model or back-of-envelope analysis: minimal spec, minimal checks, clear 'not for publication' label. |

## Build

| Command | Primary agent | What it does |
|---|---|---|
| `/build-semi-structural` [country|model name] | `semi-structural-gap-modeler` | Builds a small or medium semi-structural gap/projection model with calibration, filters and baseline. |
| `/build-fpas` [country|system name] | `fpas-modeler` | Designs and builds a forecasting and policy analysis system: core model, nowcasts, judgment layer, forecast process. |
| `/build-financial-programming` [country] | `financial-programming-specialist` | Builds an integrated financial-programming framework consistent across real, fiscal, monetary and external sectors. |
| `/build-dsge` [model name] | `open-economy-dsge-specialist` | Builds a DSGE model (small, medium or large) from approved spec: derivation, code, solution, tests, IRFs. |
| `/build-hank` [model name] | `hank-specialist` | Builds a heterogeneous-agent (HANK) model with household block, sequence-space solution and distributional outputs. |
| `/build-multicountry` [model name] | `multi-country-dsge-specialist` | Builds or extends a large multi-country model with trade and financial linkages and global scenarios. |
| `/build-sfc` [model name] | `sfc-modeler` | Builds a stock-flow consistent model with balance-sheet and transaction matrices and scenario runs. |
| `/build-abm` [model name] | `agent-based-modeling-specialist` | Builds an agent-based model with ODD documentation, calibration, validation and experiment design. |
| `/build-game-model` [model name] | `game-theory-specialist` | Builds a game-theoretic or mechanism-design model: specification, equilibria, computation and policy interpretation. |
| `/build-io-sam` [country|region set] | `input-output-sam-specialist` | Builds input-output, supply-use and SAM frameworks with multipliers, linkages, multi-regional and environmentally extended extensions. |
| `/build-cge` [model name] | `cge-modeling-specialist` | Builds a CGE model (static or recursive-dynamic, single- or multi-region) with benchmark replication, closures, elasticity sensitivity and welfare decomposition. |
| `/build-trade-model` [model name] | `trade-policy-simulation-specialist` | Builds a trade model: gravity and structural gravity estimation, quantitative trade general equilibrium, and global value chain accounting. |
| `/build-climate-macro` [model name] | `climate-macro-specialist` | Builds a climate-macro model: climate-augmented macro or integrated-assessment-style model with damage functions, abatement and carbon pricing. |

## Build (AI)

| Command | Primary agent | What it does |
|---|---|---|
| `/build-deep-forecaster` [target variable(s)] | `time-series-deep-learning-specialist` | Builds a deep-learning or foundation-model forecaster with rolling-origin evaluation against statistical benchmarks. |
| `/build-drl-policy` [policy problem] | `deep-reinforcement-learning-specialist` | Builds a deep reinforcement learning policy environment and agent for monetary, fiscal or macroprudential policy. |
| `/build-neural-solver` [model name] | `neural-solver-specialist` | Builds a neural-network solver for a high-dimensional or heterogeneous-agent model and certifies its accuracy. |
| `/build-llm-pipeline` [task description] | `llm-economic-analyst` | Builds an LLM pipeline for extraction, classification or analysis with verification, evaluation and confidentiality controls. |
| `/build-llm-agents` [simulation design] | `llm-agent-simulation-specialist` | Builds LLM-agent economic simulations (synthetic households, firms, forecasters, negotiators) with sensitivity and human-data checks. |
| `/build-rag-kb` [document collection] | `rag-knowledge-specialist` | Builds a retrieval-augmented knowledge base over document collections with access control and faithfulness evaluation. |
| `/build-causal-ml` [treatment and outcome] | `causal-ml-specialist` | Builds a causal machine-learning analysis (double ML, causal forests) with identification argument and sensitivity checks. |

## Estimation

| Command | Primary agent | What it does |
|---|---|---|
| `/estimate-var` [variables|spec path] | `var-vecm-specialist` | Estimates VAR/SVAR/VECM models with diagnostics, identification and impulse responses. |
| `/estimate-bvar` [variables|spec path] | `bayesian-var-specialist` | Estimates Bayesian VARs with prior choice, hyperparameter selection, conditional forecasts and out-of-sample checks. |
| `/estimate-dsge` [model name] | `bayesian-dsge-estimation-specialist` | Estimates a DSGE model by Bayesian methods with identification analysis, convergence diagnostics and fit evaluation. |
| `/calibrate-model` [model name] | `bayesian-dsge-estimation-specialist` | Calibrates a model to targets: moments, micro evidence and published estimates, with sensitivity of targets to parameters. |
| `/nowcast` [target variable] | `dfm-nowcasting-specialist` | Builds and runs a nowcasting system with release calendar, news decomposition and real-time evaluation. |
| `/local-projections` [shock and outcome] | `local-projections-specialist` | Estimates impulse responses and state-dependent effects with local projections; compares with VAR. |
| `/identify-shocks` [shock type] | `shock-identification-specialist` | Constructs and tests structural shock series (narrative, high-frequency, proxy) and documents identification. |

## Analysis

| Command | Primary agent | What it does |
|---|---|---|
| `/forecast-round` [round id, e.g. 2026Q4] | `fpas-modeler` | Runs a complete forecast round: data freeze, nowcast, model runs, judgment, review and sign-off. |
| `/scenario-analysis` [scenario description] | `scenario-risk-analysis-specialist` | Designs and runs scenarios and risk assessments with consistent assumptions across models. |
| `/policy-simulation` [policy options] | `economic-reasoning-specialist` | Simulates policy options (rates, fiscal, macroprudential, FX) in the chosen model(s) with welfare and distributional effects. |
| `/fan-chart` [variable(s)] | `scenario-risk-analysis-specialist` | Produces density forecasts and fan charts with documented uncertainty method and calibration checks. |
| `/debt-sustainability` [country] | `debt-sustainability-analyst` | Runs debt sustainability analysis: baseline, shocks, stochastic fan charts, realism checks and financing needs. |
| `/stress-test` [sector or system] | `financial-stability-stress-testing-specialist` | Runs macro-financial stress tests: scenario design, satellite models, bank and sector results, policy implications. |
| `/spillover-analysis` [shock and country set] | `global-spillover-specialist` | Quantifies cross-country spillovers from a global shock using multiple models and country-vulnerability measures. |
| `/external-assessment` [country] | `external-assessment-specialist` | Runs an external sector assessment: current-account norm, REER gap, reserves, NIIP, with ranges and judgment. |
| `/climate-scenario` [scenario set] | `climate-macro-specialist` | Runs climate and transition scenarios: translating climate pathways to macro, fiscal and financial impacts. |
| `/distributional-analysis` [policy or shock] | `inequality-distribution-specialist` | Analyzes distributional effects of a policy or shock using microsimulation, HANK links or survey-based incidence. |
| `/carbon-pricing-analysis` [policy design] | `carbon-pricing-emissions-specialist` | Analyzes carbon pricing and emissions policy: tax or trading design, border adjustment, revenue recycling, competitiveness and distributional effects. |
| `/trade-policy-analysis` [trade scenario] | `trade-policy-simulation-specialist` | Simulates trade policy and tariff scenarios with quantitative trade and CGE models, including retaliation, value-chain propagation and welfare effects. |
| `/supply-chain-shock` [shock description] | `production-networks-specialist` | Analyzes sectoral and supply-chain shocks with input-output and production-network models: propagation, bottlenecks, and price and quantity effects. |

## Validation & QA

| Command | Primary agent | What it does |
|---|---|---|
| `/validate-model` [model name] | `model-validation-specialist` | Runs independent model validation sized to risk level: conceptual soundness, implementation, outcomes, benchmarking. Issues a rating. |
| `/backtest` [model name] [window] | `backtesting-specialist` | Runs historical and pseudo-real-time backtests with information-set checks and regime-specific performance. |
| `/sensitivity-analysis` [model name] [output of interest] | `sensitivity-uncertainty-specialist` | Runs global sensitivity and uncertainty analysis to rank assumptions and parameters that drive results. |
| `/replicate` [model name or package path] | `replication-auditor` | Replicates results from the replication package on a clean environment and traces published numbers to code and data. |
| `/model-risk-review` [model name] | `model-risk-governance-specialist` | Independent model risk review: aggregates validation, ethics, confidentiality and use-limit checks; approves or blocks release. |
| `/code-review` [path] | `python-julia-engineer` | Reviews model and pipeline code for correctness, numerical soundness, reproducibility and standards compliance. |
| `/robustness-check` [result or claim to test] | `model-validation-specialist` | Tests conclusions under alternative models, identification schemes, samples, priors and data vintages. |
| `/ai-audit` [model name] | `model-risk-governance-specialist` | Audits AI/ML/LLM components: benchmarks, leakage, calibration, explainability, bias, red-team, confidentiality, monitoring. |

## Documentation

| Command | Primary agent | What it does |
|---|---|---|
| `/model-card` [model name] | `technical-documentation-specialist` | Writes the model card: purpose, limits, data, performance, validation status, risks and appropriate use. |
| `/technical-note` [topic] | `technical-documentation-specialist` | Writes a technical note or methodology paper from model work: motivation, method, results, robustness, limits. |
| `/policy-brief` [topic and audience] | `policy-relevance-specialist` | Writes a policy brief: key message, evidence, risks, options and caveats in plain, honest language. |
| `/chart-pack` [results path] | `visualization-dashboard-specialist` | Produces a chart pack from code: fan charts, shock decompositions, scenario comparisons, with consistent style and labelling. |

## Governance

| Command | Primary agent | What it does |
|---|---|---|
| `/gate-check` [concept|design|build|estimate|validate|release] | `project-planning-specialist` | Runs a phase gate: checks exit criteria for the current stage and returns PASS / CONCERNS / FAIL / NOT ASSESSED. |
| `/milestone-review` [milestone or project] | `project-planning-specialist` | Reviews progress against milestones: scope, schedule, risk, quality, dependencies and re-planning. |
| `/retrospective` [project or round] | `project-planning-specialist` | Runs a retrospective on a forecast round, model build or project: what worked, what failed, what to change. |
| `/model-release` [model name] [version] | `project-planning-specialist` | Releases a model version: checks approvals, tags code, data and parameters, updates the registry and writes release notes. |

## Team Orchestration

| Command | Primary agent | What it does |
|---|---|---|
| `/team-dsge` [model name] | `open-economy-dsge-specialist` | Orchestrates the full DSGE team: spec, build, solve, estimate, validate and document a structural model end to end. |
| `/team-forecast` [round id] | `fpas-modeler` | Orchestrates a full forecast round across nowcasting, core model, ML ensemble, judgment, risks, charts and brief. |
| `/team-stress-test` [system or sector] | `financial-stability-stress-testing-specialist` | Orchestrates a macro-financial stress-test exercise: scenarios, satellite models, network contagion, results and policy options. |
| `/team-ai-model` [AI model project] | `deep-learning-architect` | Orchestrates an AI model project end to end: benchmark first, AI build, interpretation, audit, MLOps and release. |
| `/team-fiscal` [country] | `debt-sustainability-analyst` | Orchestrates a fiscal analysis package: DSA, multipliers, microsimulation, investment and risk, integrated into one report. |
| `/team-country-analysis` [country] | `economic-reasoning-specialist` | Orchestrates a country analysis: macro outlook, external, fiscal, financial, risks, policy options and note. |

## Capacity Development

| Command | Primary agent | What it does |
|---|---|---|
| `/design-training` [audience and model] | `training-curriculum-designer` | Designs a capacity-development program: needs assessment, curriculum, labs, assessment and ownership-transfer plan. |
| `/create-exercise` [learning goal] | `policy-wargame-facilitator` | Creates a hands-on exercise, case study, or policy wargame with scenario, roles, materials, facilitator guide and debrief. |

## Lego (Modular Models)

| Command | Primary agent | What it does |
|---|---|---|
| `/lego-map` [model path | new model name] | `modeling-methodology-specialist` | Represents a model as a lego set: a baseplate (core), bricks (components) and studs (interfaces), saved as model.lego.json. For a new model or an existing one. |
| `/lego-show` [manifest path] [--html] [--mermaid] | `modeling-methodology-specialist` | Shows a model as a lego set: baseplate, bricks, joints, open studs, parts bin and suggested bricks, in text, an HTML picture, or a Mermaid diagram. |
| `/lego-add` [manifest path] [brick id | brick file] | `modeling-methodology-specialist` | Adds a brick to a model, for example a trade sector, carbon-pricing block or labor market, after checking the wiring and listing what changes. |
| `/lego-detach` [manifest path] [brick id] | `modeling-methodology-specialist` | Detaches a brick from a model and keeps it in the parts bin. Inputs that depended on it switch to their declared stubs so the model keeps running. |
| `/lego-swap` [manifest path] [old brick id] [new brick id | file] | `modeling-methodology-specialist` | Swaps one brick for an alternative that fills the same slot, for example a Taylor rule for a managed-FX rule, or an input-output brick for a CGE. |
| `/lego-check` [manifest path] | `model-validation-specialist` | Checks a lego model: all studs connected or stubbed, no duplicate providers, slots filled, units and frequencies consistent, identities verifiable, simultaneous blocks listed. |
| `/lego-brick` [brick id and purpose] | `modeling-methodology-specialist` | Creates a new brick spec for the catalog: purpose, ports (with units and timing), stubs, slot, frequency and bridge, and the checks it must pass. |
