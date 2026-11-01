# Model Classes: Small, Medium, Large (and AI)

One lifecycle, different depth. Choose the simplest model that can answer the question.

| | Small | Medium | Large | AI-based |
|---|---|---|---|---|
| Typical size | Up to ~30 equations or a handful of variables | ~30-300 equations; estimated multi-block | Hundreds to thousands of equations; multi-country, multi-sector, high-dimensional state | Defined by learned components |
| Examples | 3-equation NK, gap model, financial programming, DSA, small BVAR, small IO or SAM multiplier model, gravity regression | FPAS core model, medium open-economy DSGE, BVAR/DFM suites, single-country CGE, SFC, regional IO, quantitative trade model | Multi-country DSGE, large macroeconometric models, multi-region multi-sector CGE, global IO/trade systems, HANK with rich heterogeneity, climate-macro IAM | Deep forecasters, DRL policy, neural solvers, LLM pipelines, ABM with learned agents |
| Typical timeline | Days to 2 weeks | Weeks to 3 months | 3 months to years | Weeks to months, plus audit |
| Validation | Peer review + tests | Independent validation | Independent validation + periodic revalidation | Independent validation + `/ai-audit` |
| Documentation | Short model card | Full spec + model card | Full spec, model card, user guide, replication package | Model card + experiment log + evaluation card |
| Compute | Laptop | Laptop / workstation | HPC / GPU / parallel | GPU as needed |

## Which family for which question
| If the question is about... | Start with |
|---|---|
| Near-term outlook, policy trade-offs in a small system | Semi-structural / FPAS (`/build-semi-structural`, `/build-fpas`) |
| Dynamics and shocks with micro-foundations; welfare | DSGE (`/build-dsge`), HANK if distribution matters (`/build-hank`) |
| Sectoral structure, multipliers, linkages | Input-output / SAM (`/build-io-sam`) |
| Economy-wide effects of taxes, tariffs, subsidies, reform | CGE (`/build-cge`) |
| Tariffs, trade agreements, value chains | Trade models (`/build-trade-model`) |
| Climate policy, carbon prices, physical risk | Climate-macro and CGE/IO (`/build-climate-macro`, `/carbon-pricing-analysis`) |
| Empirical dynamics, causal effects | VAR / local projections / panel methods (`/estimate-var`, `/local-projections`) |
| Debt, fiscal adjustment, financing | DSA and fiscal models (`/debt-sustainability`) |
| Stability of the financial system | Stress tests, network and bank models (`/stress-test`) |
| Strategic interaction, heterogeneous behavior | Games and agent-based models (`/build-game-model`, `/build-abm`) |
| High-dimensional models, forecasting with many predictors, text | AI methods, benchmark first (`/team-ai-model`) |

## Choosing
1. Start with `/scope-question`, then `/select-model-class`.
2. A larger model must be justified by a question a smaller one cannot answer.
3. Combine rather than choose where helpful: a small core model with satellites, a CGE linked to a household microsimulation, a structural model with a neural solver, a DSGE benchmark with an ML forecaster.
4. For high-stakes questions, cross-check conclusions across at least two model classes.

## Effort by class
- **Small:** `/quick-model` → `/validate-model` (peer-review depth) → `/model-card` (short).
- **Medium:** `/model-brief` → `/model-spec` → `/data-requirements` → `/build-*` → `/estimate-*` → `/validate-model` → `/model-release`.
- **Large:** as medium, plus architecture decision records, a parallel/HPC plan, staged integration by block, periodic revalidation and user training (`/design-training`).
- **AI:** benchmark first, experiment log, `/ai-audit` before `/model-release`.
