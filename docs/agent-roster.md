# Agent Roster

119 agents, grouped by area of expertise. Source of truth: `.claude/agents/`.

| Area | Agents |
|---|---|
| Framing, Methods & Governance | 5 |
| Macro Models: Small, Medium & Traditional | 6 |
| Structural Macro: DSGE, HANK & Solution Methods | 10 |
| Econometrics & Time Series | 8 |
| Forecasting & Scenarios | 3 |
| Input-Output, CGE, Trade & Sectoral Models | 7 |
| Climate, Energy & Natural Resources | 6 |
| Fiscal & Public Finance | 6 |
| Monetary & Financial | 9 |
| External Sector & Global Linkages | 4 |
| Integrated Policy Framework (IPF) | 4 |
| Growth, Labor, Distribution & Development | 5 |
| AI & Machine Learning | 16 |
| Games, Agents & Strategic Behavior | 6 |
| Data & Statistics | 6 |
| Computation & Engineering | 7 |
| Validation, Risk & Ethics | 6 |
| Communication & Capacity Building | 5 |

## Framing, Methods & Governance (5)

| Agent | Role |
|---|---|
| [`economic-reasoning-specialist`](../.claude/agents/economic-reasoning-specialist.md) | Frames the economic question and tests whether results make economic sense: mechanisms, stylized facts, plausibility and fitness-for-purpose. |
| [`modeling-methodology-specialist`](../.claude/agents/modeling-methodology-specialist.md) | Chooses methods and architecture across model families, sets code and data standards, and resolves technical trade-offs between traditional, structural and AI approaches. |
| [`model-risk-governance-specialist`](../.claude/agents/model-risk-governance-specialist.md) | Defines model risk levels and validation depth, enforces builder-validator independence, governs AI/LLM use and recommends release or block. |
| [`policy-relevance-specialist`](../.claude/agents/policy-relevance-specialist.md) | Clarifies the decision, audience and deadline, and reviews outputs for decision-relevance, honest uncertainty and appropriate caveats. |
| [`project-planning-specialist`](../.claude/agents/project-planning-specialist.md) | Plans and sequences modeling work: scope, milestones sized to model class, dependencies, phase gates and calendars. |

## Macro Models: Small, Medium & Traditional (6)

| Agent | Role |
|---|---|
| [`semi-structural-gap-modeler`](../.claude/agents/semi-structural-gap-modeler.md) | Builds quarterly projection and semi-structural gap models: IS curve, Phillips curve, UIP, policy rule, filters. |
| [`fpas-modeler`](../.claude/agents/fpas-modeler.md) | Builds forecasting and policy analysis systems (FPAS) for inflation-targeting and transitioning regimes. |
| [`financial-programming-specialist`](../.claude/agents/financial-programming-specialist.md) | Builds financial programming frameworks: consistent monetary, fiscal, external and real-sector accounts for program design and policy analysis. |
| [`rmsm-three-gap-modeler`](../.claude/agents/rmsm-three-gap-modeler.md) | Builds revised minimum standard, three-gap and growth-financing models for low-income and developing economies. |
| [`sfc-modeler`](../.claude/agents/sfc-modeler.md) | Builds stock-flow consistent models linking real activity, balance sheets, credit and financial flows. |
| [`macroeconometric-model-specialist`](../.claude/agents/macroeconometric-model-specialist.md) | Builds and maintains large-scale macroeconometric models: error-correction equations, bloc structure, simulation and solution. |

## Structural Macro: DSGE, HANK & Solution Methods (10)

| Agent | Role |
|---|---|
| [`optimal-policy-control-specialist`](../.claude/agents/optimal-policy-control-specialist.md) | Solves optimal policy problems: linear-quadratic control, Ramsey and timeless-perspective policy, robust control and decision under uncertainty. |
| [`open-economy-dsge-specialist`](../.claude/agents/open-economy-dsge-specialist.md) | Builds small open-economy DSGE models: UIP, pricing-to-market, trade, terms of trade, exchange-rate pass-through. |
| [`multi-country-dsge-specialist`](../.claude/agents/multi-country-dsge-specialist.md) | Builds large multi-country DSGE models for spillovers, global shocks and policy coordination. |
| [`financial-frictions-dsge-specialist`](../.claude/agents/financial-frictions-dsge-specialist.md) | Builds DSGE models with financial frictions: BGG, banking, collateral constraints, sudden stops, macro-financial feedback. |
| [`hank-specialist`](../.claude/agents/hank-specialist.md) | Builds heterogeneous-agent (HANK) models: household heterogeneity, MPC distribution, distributional monetary and fiscal policy. |
| [`perturbation-solution-specialist`](../.claude/agents/perturbation-solution-specialist.md) | Solves DSGE models by perturbation (1st-3rd order), pruning, and verifies determinacy and accuracy. |
| [`global-solution-specialist`](../.claude/agents/global-solution-specialist.md) | Solves models globally: projection, time iteration, value-function iteration, for strong nonlinearity and constraints. |
| [`bayesian-dsge-estimation-specialist`](../.claude/agents/bayesian-dsge-estimation-specialist.md) | Estimates DSGE models by Bayesian methods (MCMC, SMC) and checks identification, priors and fit. |
| [`obc-zlb-specialist`](../.claude/agents/obc-zlb-specialist.md) | Handles occasionally binding constraints: zero lower bound, borrowing limits, regime switches in structural models. |
| [`emde-lic-dsge-specialist`](../.claude/agents/emde-lic-dsge-specialist.md) | Adapts structural models to emerging, developing and low-income economies: dollarization, informality, aid, commodities, fiscal limits. |

## Econometrics & Time Series (8)

| Agent | Role |
|---|---|
| [`var-vecm-specialist`](../.claude/agents/var-vecm-specialist.md) | Builds VAR, SVAR and VECM models: lag selection, stability, cointegration, impulse responses, variance decompositions. |
| [`bayesian-var-specialist`](../.claude/agents/bayesian-var-specialist.md) | Builds Bayesian VARs: Minnesota, SSVS, large BVARs, hierarchical priors, mixed-frequency and conditional forecasting. |
| [`dfm-nowcasting-specialist`](../.claude/agents/dfm-nowcasting-specialist.md) | Builds dynamic factor models and nowcasts: mixed frequency, ragged edge, news decomposition, bridge equations. |
| [`local-projections-specialist`](../.claude/agents/local-projections-specialist.md) | Estimates impulse responses with local projections and smooth LP: state dependence, inference, comparison with VARs. |
| [`panel-causal-inference-specialist`](../.claude/agents/panel-causal-inference-specialist.md) | Panel econometrics and causal inference: fixed effects, GMM, difference-in-differences, synthetic control, IV, event studies. |
| [`tvp-regime-switching-specialist`](../.claude/agents/tvp-regime-switching-specialist.md) | Builds time-varying parameter, stochastic-volatility, Markov-switching and structural-break models. |
| [`state-space-kalman-specialist`](../.claude/agents/state-space-kalman-specialist.md) | Builds state-space models: Kalman filter/smoother, unobserved components, trend-cycle, missing data, likelihood evaluation. |
| [`shock-identification-specialist`](../.claude/agents/shock-identification-specialist.md) | Identifies structural shocks: sign/zero restrictions, narrative, high-frequency, external instruments, heteroskedasticity. |

## Forecasting & Scenarios (3)

| Agent | Role |
|---|---|
| [`forecast-evaluation-specialist`](../.claude/agents/forecast-evaluation-specialist.md) | Evaluates forecasts: point and density accuracy, proper scoring rules, calibration, bias tests, forecast comparison. |
| [`scenario-risk-analysis-specialist`](../.claude/agents/scenario-risk-analysis-specialist.md) | Designs scenarios and risk assessments: fan charts, risk-balance, alternative scenarios, growth-at-risk, tail risks. |
| [`forecast-combination-specialist`](../.claude/agents/forecast-combination-specialist.md) | Combines forecasts: model averaging, ensemble weights, stacking, opinion pools, model-and-judgment reconciliation. |

## Input-Output, CGE, Trade & Sectoral Models (7)

| Agent | Role |
|---|---|
| [`input-output-sam-specialist`](../.claude/agents/input-output-sam-specialist.md) | Builds input-output, supply-use and social accounting matrix frameworks: Leontief multipliers, multi-regional IO, SAM balancing, linkage and impact analysis. |
| [`cge-modeling-specialist`](../.claude/agents/cge-modeling-specialist.md) | Builds computable general equilibrium models: static and recursive-dynamic, single- and multi-region (GTAP-style), closures, elasticities and welfare analysis. |
| [`trade-policy-simulation-specialist`](../.claude/agents/trade-policy-simulation-specialist.md) | Simulates trade policy with quantitative trade models: structural gravity, Armington, Eaton-Kortum, tariffs, non-tariff measures, trade agreements and welfare counterfactuals. |
| [`production-networks-specialist`](../.claude/agents/production-networks-specialist.md) | Models production networks and supply chains: sectoral linkages, shock propagation, bottlenecks, concentration and resilience. |
| [`regional-spatial-economics-specialist`](../.claude/agents/regional-spatial-economics-specialist.md) | Models regional and spatial economies: spatial equilibrium, urban and regional models, agglomeration, migration, regional multipliers and place-based policy. |
| [`agriculture-food-security-specialist`](../.claude/agents/agriculture-food-security-specialist.md) | Models agriculture and food systems: sectoral partial-equilibrium models, food prices, yields, climate impacts, trade and subsidies, food security and welfare. |
| [`trade-gvc-specialist`](../.claude/agents/trade-gvc-specialist.md) | Models trade and global value chains: gravity, structural gravity, input-output linkages, tariffs, supply-chain shocks. |

## Climate, Energy & Natural Resources (6)

| Agent | Role |
|---|---|
| [`carbon-pricing-emissions-specialist`](../.claude/agents/carbon-pricing-emissions-specialist.md) | Analyzes carbon pricing and emissions policy: carbon taxes, emissions trading, border adjustments, revenue recycling, abatement costs and emissions accounting. |
| [`physical-climate-risk-specialist`](../.claude/agents/physical-climate-risk-specialist.md) | Quantifies physical climate risk: hazards, exposure, vulnerability, damage functions, adaptation and climate-conditioned macro and financial impacts. |
| [`extractives-natural-resources-specialist`](../.claude/agents/extractives-natural-resources-specialist.md) | Analyzes resource-rich economies: extractive revenues, fiscal regimes, sovereign wealth funds, Dutch disease, depletion and commodity-linked fiscal rules. |
| [`commodity-markets-specialist`](../.claude/agents/commodity-markets-specialist.md) | Models commodity markets: oil, gas, metals, food, price shocks, supply-demand balances, commodity-exporter and importer impacts. |
| [`climate-macro-specialist`](../.claude/agents/climate-macro-specialist.md) | Models climate and macro: integrated assessment, climate DSGE, physical risks, carbon pricing, adaptation, climate scenarios. |
| [`transition-risk-energy-specialist`](../.claude/agents/transition-risk-energy-specialist.md) | Analyzes energy systems and transition risk: energy balances, stranded assets, subsidies, green investment, sectoral transition. |

## Fiscal & Public Finance (6)

| Agent | Role |
|---|---|
| [`revenue-tax-policy-specialist`](../.claude/agents/revenue-tax-policy-specialist.md) | Forecasts and analyzes tax revenue: elasticities and buoyancy, tax gaps, VAT, corporate and personal income tax modeling, reform revenue estimates and compliance. |
| [`debt-sustainability-analyst`](../.claude/agents/debt-sustainability-analyst.md) | Builds debt sustainability analyses: baseline, stress tests, fan charts, realism tools, market-access and low-income frameworks. |
| [`fiscal-multiplier-specialist`](../.claude/agents/fiscal-multiplier-specialist.md) | Estimates and simulates fiscal multipliers: state-dependent, composition-dependent, open-economy, DSGE and empirical evidence. |
| [`tax-benefit-microsimulation-specialist`](../.claude/agents/tax-benefit-microsimulation-specialist.md) | Builds tax-benefit microsimulation: revenue estimation, distributional analysis, behavioral responses, subsidy and transfer reform. |
| [`public-investment-specialist`](../.claude/agents/public-investment-specialist.md) | Analyzes public investment: efficiency, capital stocks, growth effects, PPP and infrastructure, investment-growth models. |
| [`fiscal-risk-specialist`](../.claude/agents/fiscal-risk-specialist.md) | Assesses fiscal risks: contingent liabilities, SOEs, financial-sector support, disasters, pensions, climate and demographics. |

## Monetary & Financial (9)

| Agent | Role |
|---|---|
| [`banking-credit-specialist`](../.claude/agents/banking-credit-specialist.md) | Models banks and credit markets: lending supply and demand, bank balance sheets, funding costs, pass-through to lending rates and credit-cycle dynamics. |
| [`expectations-learning-specialist`](../.claude/agents/expectations-learning-specialist.md) | Models expectations formation: survey and market-based expectations, adaptive learning, rational inattention, bounded rationality and anchoring. |
| [`monetary-policy-rules-specialist`](../.claude/agents/monetary-policy-rules-specialist.md) | Designs and evaluates monetary policy rules: Taylor-type, optimal, robust, forecast-based, average inflation targeting, regime comparison. |
| [`unconventional-policy-specialist`](../.claude/agents/unconventional-policy-specialist.md) | Analyzes unconventional policy: QE/QT, forward guidance, yield-curve control, balance-sheet policy, FX-based tools. |
| [`inflation-dynamics-specialist`](../.claude/agents/inflation-dynamics-specialist.md) | Analyzes inflation: Phillips curves, expectations, pass-through, supply shocks, non-linearity, trend inflation, sectoral decompositions. |
| [`yield-curve-specialist`](../.claude/agents/yield-curve-specialist.md) | Models yield curves and term premia: affine term-structure, Nelson-Siegel, macro-finance, risk premia, sovereign spreads. |
| [`financial-stability-stress-testing-specialist`](../.claude/agents/financial-stability-stress-testing-specialist.md) | Builds systemic risk and stress-testing frameworks: bank solvency/liquidity, CoVaR, SRISK, contagion, macro-financial scenarios. |
| [`macroprudential-housing-specialist`](../.claude/agents/macroprudential-housing-specialist.md) | Analyzes macroprudential policy and housing/credit cycles: CCyB, LTV/DSTI, credit gaps, house-price models. |
| [`digital-money-fintech-specialist`](../.claude/agents/digital-money-fintech-specialist.md) | Analyzes digital money and fintech: CBDC, stablecoins, crypto assets, payment systems, financial inclusion, monetary implications. |

## External Sector & Global Linkages (4)

| Agent | Role |
|---|---|
| [`capital-flows-ipf-specialist`](../.claude/agents/capital-flows-ipf-specialist.md) | Models capital flows and integrated policy frameworks: FX intervention, capital flow measures, monetary-macroprudential-FX mix. |
| [`balance-of-payments-specialist`](../.claude/agents/balance-of-payments-specialist.md) | Builds balance-of-payments and international investment position analyses: current account, financing, valuation effects. |
| [`external-assessment-specialist`](../.claude/agents/external-assessment-specialist.md) | Conducts external-sector assessments: current account norms, real-exchange-rate gaps, reserve adequacy, NIIP, multiple methodologies. |
| [`global-spillover-specialist`](../.claude/agents/global-spillover-specialist.md) | Analyzes global spillovers: monetary, fiscal, financial, trade shocks, global financial cycle, multi-model comparison. |

## Integrated Policy Framework (IPF) (4)

| Agent | Role |
|---|---|
| [`ipf-general-specialist`](../.claude/agents/ipf-general-specialist.md) | Applies the Integrated Policy Framework: maps shocks and country characteristics to the joint use of monetary policy, capital flow measures, FX intervention and macroprudential policy. |
| [`ipf-external-specialist`](../.claude/agents/ipf-external-specialist.md) | Models the external side of the IPF with the IPF diagram: shallow FX markets and UIP premia, external borrowing limits and sudden stops, FX intervention and reserves, capital flow measures. |
| [`ipf-micro-specialist`](../.claude/agents/ipf-micro-specialist.md) | Builds and solves microfounded quantitative IPF models, solved nonlinearly with welfare analysis. |
| [`ipf-low-income-specialist`](../.claude/agents/ipf-low-income-specialist.md) | Applies the IPF to low-income countries: strong frictions, low reserves, weak transmission, capacity and governance constraints, policy coherence. |

## Growth, Labor, Distribution & Development (5)

| Agent | Role |
|---|---|
| [`inequality-distribution-specialist`](../.claude/agents/inequality-distribution-specialist.md) | Analyzes inequality and distribution: household heterogeneity, poverty, gender, incidence, distributional national accounts. |
| [`labor-demography-specialist`](../.claude/agents/labor-demography-specialist.md) | Models labor markets and demographics: unemployment, participation, search-matching, migration, aging, pensions, human capital. |
| [`growth-productivity-specialist`](../.claude/agents/growth-productivity-specialist.md) | Analyzes growth and productivity: growth accounting, convergence, structural reform effects, innovation, growth diagnostics. |
| [`fragility-disaster-specialist`](../.claude/agents/fragility-disaster-specialist.md) | Analyzes fragility, conflict, pandemics and natural disasters: macro impacts, resilience, post-shock recovery, financing. |
| [`ai-digital-economy-specialist`](../.claude/agents/ai-digital-economy-specialist.md) | Analyzes AI and the digital economy: labor-market exposure, productivity, task models, inequality, market concentration, policy. |

## AI & Machine Learning (16)

| Agent | Role |
|---|---|
| [`deep-learning-architect`](../.claude/agents/deep-learning-architect.md) | Designs deep learning architectures for macro-financial data: MLPs, CNNs, attention, regularization, small-data strategies. |
| [`time-series-deep-learning-specialist`](../.claude/agents/time-series-deep-learning-specialist.md) | Builds deep sequence and foundation-model forecasters: LSTM/GRU, TCN, transformers, TFT, N-BEATS, pretrained time-series models. |
| [`deep-reinforcement-learning-specialist`](../.claude/agents/deep-reinforcement-learning-specialist.md) | Applies deep reinforcement learning to policy problems: optimal monetary, fiscal and macroprudential policy, robust policy under uncertainty. |
| [`neural-solver-specialist`](../.claude/agents/neural-solver-specialist.md) | Solves high-dimensional economic models with neural networks: deep equilibrium nets, physics-informed networks, deep value/policy approximators. |
| [`simulation-based-inference-specialist`](../.claude/agents/simulation-based-inference-specialist.md) | Estimates complex models with neural simulation-based inference: neural posterior/likelihood estimation, amortized Bayesian inference. |
| [`llm-economic-analyst`](../.claude/agents/llm-economic-analyst.md) | Uses LLMs for economic analysis: reading policy documents, extracting data and facts, drafting analysis under strict verification. |
| [`llm-agent-simulation-specialist`](../.claude/agents/llm-agent-simulation-specialist.md) | Builds LLM-based economic agents and simulations: expectation formation, survey experiments, negotiation, synthetic households and firms. |
| [`llm-model-copilot-specialist`](../.claude/agents/llm-model-copilot-specialist.md) | Uses LLMs to accelerate modeling: code translation, Dynare/Python/Julia generation, equation derivation checks, test writing, documentation. |
| [`rag-knowledge-specialist`](../.claude/agents/rag-knowledge-specialist.md) | Builds retrieval-augmented knowledge systems over document collections: reports, country files, methodology notes, model manuals. |
| [`nlp-text-as-data-specialist`](../.claude/agents/nlp-text-as-data-specialist.md) | Turns text into economic data: monetary policy communication, news sentiment, policy uncertainty, topic models, narrative indices. |
| [`causal-ml-specialist`](../.claude/agents/causal-ml-specialist.md) | Applies causal machine learning: double/debiased ML, causal forests, heterogeneous treatment effects, high-dimensional controls. |
| [`graph-ml-specialist`](../.claude/agents/graph-ml-specialist.md) | Models networks with graph methods: trade, supply chains, interbank exposure, contagion, graph neural networks. |
| [`generative-ai-scenario-specialist`](../.claude/agents/generative-ai-scenario-specialist.md) | Uses generative models (VAEs, GANs, diffusion, LLMs) to create scenarios, synthetic data and stress paths. |
| [`multi-agent-rl-specialist`](../.claude/agents/multi-agent-rl-specialist.md) | Builds multi-agent reinforcement learning systems for strategic economic interaction: markets, policymakers, firms, international coordination. |
| [`interpretable-ml-specialist`](../.claude/agents/interpretable-ml-specialist.md) | Makes AI models explainable: feature attribution, partial dependence, surrogate models, uncertainty and economic plausibility tests. |
| [`differentiable-programming-specialist`](../.claude/agents/differentiable-programming-specialist.md) | Builds differentiable economic models in JAX/PyTorch/Julia: autodiff for estimation, calibration, sensitivity and optimal policy. |

## Games, Agents & Strategic Behavior (6)

| Agent | Role |
|---|---|
| [`game-theory-specialist`](../.claude/agents/game-theory-specialist.md) | Builds game-theoretic models: Nash, subgame-perfect, Bayesian, dynamic and repeated games for policy interaction. |
| [`mechanism-design-specialist`](../.claude/agents/mechanism-design-specialist.md) | Designs mechanisms and incentives: auctions, debt-issuance design, program conditionality, contracts, matching. |
| [`agent-based-modeling-specialist`](../.claude/agents/agent-based-modeling-specialist.md) | Builds agent-based macro and financial models: heterogeneous boundedly-rational agents, networks, emergent dynamics, calibration. |
| [`policy-interaction-games-specialist`](../.claude/agents/policy-interaction-games-specialist.md) | Models policy interaction: monetary-fiscal games, international coordination, central-bank commitment vs. discretion, strategic spillovers. |
| [`sovereign-crisis-games-specialist`](../.claude/agents/sovereign-crisis-games-specialist.md) | Models sovereign debt, default and currency crises: Eaton-Gersovitz, bargaining, global games, bank runs, restructuring. |
| [`policy-wargame-facilitator`](../.claude/agents/policy-wargame-facilitator.md) | Designs and runs policy wargames, tabletop exercises and serious games for crisis preparedness and training. |

## Data & Statistics (6)

| Agent | Role |
|---|---|
| [`survey-microdata-specialist`](../.claude/agents/survey-microdata-specialist.md) | Works with household and firm survey microdata: sampling design, weights, harmonization, imputation, income and consumption aggregates and small-area estimation. |
| [`data-engineer`](../.claude/agents/data-engineer.md) | Builds data pipelines: ingestion from APIs and files, transformation, versioning, scheduling, lineage and tests. |
| [`national-accounts-specialist`](../.claude/agents/national-accounts-specialist.md) | Specializes in national accounts and macro statistics: GDP, sectoral accounts, fiscal, monetary and BoP statistics, methodology and revisions. |
| [`high-frequency-data-specialist`](../.claude/agents/high-frequency-data-specialist.md) | Handles high-frequency and alternative data: daily/weekly indicators, financial, payments, mobility, satellite, web-scraped data. |
| [`data-quality-seasonal-specialist`](../.claude/agents/data-quality-seasonal-specialist.md) | Ensures data quality: outliers, revisions, seasonality, calendar effects, structural breaks, missing data, filtering. |
| [`data-governance-metadata-specialist`](../.claude/agents/data-governance-metadata-specialist.md) | Owns data governance and metadata: confidentiality classes, licensing, SDMX metadata, catalogues, access control, privacy. |

## Computation & Engineering (7)

| Agent | Role |
|---|---|
| [`symbolic-derivation-specialist`](../.claude/agents/symbolic-derivation-specialist.md) | Derives and verifies model equations with computer algebra: first-order conditions, log-linearization, steady states, analytical Jacobians and code generation. |
| [`matlab-dynare-engineer`](../.claude/agents/matlab-dynare-engineer.md) | Engineers MATLAB, Dynare, IRIS, RISE and Octave codebases; legacy model maintenance and migration. |
| [`python-julia-engineer`](../.claude/agents/python-julia-engineer.md) | Engineers Python, Julia and R modeling code: packages, typing, testing, performance, notebooks to production. |
| [`hpc-gpu-engineer`](../.claude/agents/hpc-gpu-engineer.md) | Engineers high-performance computing: GPUs, parallel estimation, cluster jobs, large simulation workloads, cost control. |
| [`mlops-engineer`](../.claude/agents/mlops-engineer.md) | Engineers MLOps for models: experiment tracking, model registry, deployment, monitoring, drift detection, CI/CD. |
| [`numerical-methods-specialist`](../.claude/agents/numerical-methods-specialist.md) | Specializes in numerical methods: root finding, optimization, quadrature, interpolation, linear algebra, stochastic simulation. |
| [`reproducibility-engineer`](../.claude/agents/reproducibility-engineer.md) | Guarantees reproducibility: environments, containers, seeds, data vintages, code review, automated tests, replication packages. |

## Validation, Risk & Ethics (6)

| Agent | Role |
|---|---|
| [`model-validation-specialist`](../.claude/agents/model-validation-specialist.md) | Performs independent model validation: conceptual soundness, implementation checks, outcomes analysis, benchmarking. |
| [`backtesting-specialist`](../.claude/agents/backtesting-specialist.md) | Designs and runs backtests: historical simulation, pseudo-out-of-sample, stress backtests, real-time vintage backtests. |
| [`sensitivity-uncertainty-specialist`](../.claude/agents/sensitivity-uncertainty-specialist.md) | Quantifies uncertainty and sensitivity: global sensitivity analysis, parameter and model uncertainty, robustness, Monte Carlo. |
| [`replication-auditor`](../.claude/agents/replication-auditor.md) | Audits replication: reruns code from scratch, checks data lineage, numbers in publications, code-to-document consistency. |
| [`ai-ethics-fairness-specialist`](../.claude/agents/ai-ethics-fairness-specialist.md) | Reviews AI ethics and fairness: bias, explainability, accountability, human oversight, AI regulation, responsible use. |
| [`llm-red-team-specialist`](../.claude/agents/llm-red-team-specialist.md) | Red-teams LLM systems: hallucination, prompt injection, data leakage, jailbreaks, robustness, evaluation harnesses. |

## Communication & Capacity Building (5)

| Agent | Role |
|---|---|
| [`policy-brief-writer`](../.claude/agents/policy-brief-writer.md) | Writes policy briefs and notes: key messages, plain-language explanation, honest uncertainty, tables and boxes. |
| [`technical-documentation-specialist`](../.claude/agents/technical-documentation-specialist.md) | Writes technical documentation: model specifications, equations, model cards, user guides, replication READMEs. |
| [`visualization-dashboard-specialist`](../.claude/agents/visualization-dashboard-specialist.md) | Designs charts and dashboards: fan charts, shock decompositions, interactive monitoring tools, accessible and publication-ready visuals. |
| [`stakeholder-liaison-specialist`](../.claude/agents/stakeholder-liaison-specialist.md) | Interfaces with stakeholders and counterparts: requirements, assumptions, feedback, judgment overlays, translating needs to modeling tasks. |
| [`training-curriculum-designer`](../.claude/agents/training-curriculum-designer.md) | Designs training and capacity development: courses, hands-on labs, model workshops, train-the-trainer, assessments. |
