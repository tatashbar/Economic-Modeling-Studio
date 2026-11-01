# Coordination

The studio is organized by **areas of expertise**, not by reporting lines. No agent manages another; agents consult each other as peers, and the **user decides**.

## How work is coordinated
1. **Slash commands drive the work.** Each command names a *primary agent* and the agents that join it. The main session runs them as subagents, in parallel where steps are independent, and integrates the results. Subagents cannot launch further subagents.
2. **Peers consult peers.** Every agent lists the specialists it works most closely with. Consult them directly when a question crosses areas (e.g. the CGE and carbon-pricing specialists on a carbon-tax scenario).
3. **Five cross-cutting functions** are available to everyone. They are advisors, not managers:

| Function | Consult for |
|---|---|
| `economic-reasoning-specialist` | framing the question, economic plausibility, fitness-for-purpose |
| `modeling-methodology-specialist` | choice of method, architecture, standards, technical trade-offs |
| `model-risk-governance-specialist` | model risk level, independent validation, AI governance, confidentiality; release recommendation |
| `policy-relevance-specialist` | audience, decision relevance, tone, caveats |
| `project-planning-specialist` | scope, sequencing, dependencies, phase gates |

## Disagreements
- Settle disputes on the evidence: set out the options, what each assumes, and what would change the conclusion.
- If it cannot be settled on the evidence, present the options and trade-offs to the user, who decides.
- A `model-risk-governance-specialist` recommendation to block a release stands until the underlying finding is closed or the user accepts the risk in writing.

## Independence
- The agents (or people) who build a model do not validate it. Validation uses `model-validation-specialist`, `backtesting-specialist`, `replication-auditor` and others who had no part in the build.
- Validators raise findings; they do not edit the model under review.

## Rules for working together
- Agents write only to paths named in their instructions; no unilateral edits to other agents' artifacts.
- A change to a specification, calibration or data vintage triggers re-checking of dependent models, forecasts and documents (`project-planning-specialist` tracks this).
- Independent tasks (separate model runs, data pulls, reviews) run in parallel; integration steps run in sequence.

## Typical routing
| Question | Start with |
|---|---|
| "Which model should we use?" | `/select-model-class` |
| "Build a DSGE for country X" | `/team-dsge` |
| "Build an input-output or CGE model" | `/build-io-sam`, `/build-cge` |
| "What would these tariffs do?" | `/trade-policy-analysis` |
| "Cost and incidence of a carbon price" | `/carbon-pricing-analysis` |
| "Produce this quarter's forecast" | `/team-forecast` |
| "Can we trust this AI model?" | `/ai-audit` |
| "Prepare a country analysis" | `/team-country-analysis` |
| "Train colleagues on a model" | `/design-training` |
