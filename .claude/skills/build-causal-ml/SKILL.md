---
name: build-causal-ml
description: "Builds a causal machine-learning analysis (double ML, causal forests) with identification argument and sensitivity checks."
argument-hint: "[treatment and outcome]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-causal-ml — Build Causal ML

**Category:** Build (AI) · **Primary agent:** `causal-ml-specialist`

Builds a causal machine-learning analysis (double ML, causal forests) with identification argument and sensitivity checks.

Arguments: `$ARGUMENTS`

## Purpose
Build a causal machine-learning analysis that estimates treatment effects, and how they vary across units, with double/debiased ML or causal forests, while keeping identification explicit. The output is an estimate whose identifying assumptions are written down before estimation, compared with a conventional econometric estimate, and tested for sensitivity to unobserved confounding.

**Use it when** there are many potential controls, heterogeneity of effects matters for targeting, or flexible functional forms are needed for nuisance functions in an otherwise well-identified design.

**Do not use it when** there is no credible identification strategy (ML will not create one), or a standard panel or quasi-experimental design answers the question directly (`/local-projections`, `/policy-simulation`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Data sheet
   - Identification argument
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `causal-ml-specialist` — primary agent; coordinates the work and integrates results
- `panel-causal-inference-specialist` — Panel econometrics and causal inference
- `interpretable-ml-specialist` — Makes AI models explainable

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Identification | selection on observables, IV, difference-in-differences with ML controls | Credibility of the estimate |
| Estimand | ATE, ATT, CATE, policy value | What is reported |
| Learners | lasso, random forests, boosting, neural networks, ensembles | Nuisance-function quality |
| Heterogeneity method | causal forests, best linear predictor, sorted group effects | Reliability of subgroup findings |
| Sensitivity | omitted-variable-bias bounds, placebo tests | Robustness statement |

## Workflow
1. Write the identification argument and assumptions before touching the data
   - Draw the causal diagram; list confounders and why unobserved ones are unlikely to matter
2. Implement with cross-fitting; compare to a standard econometric estimate
   - Check overlap; trim if needed and report what was trimmed
3. Estimate heterogeneous effects and test stability
   - Validate heterogeneity on held-out data; avoid data-mined subgroups
4. Run sensitivity to unobserved confounding and specification
5. Write the result in terms of what the evidence supports and what it does not
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Checkpoints with the user
- After the identification note: confirm assumptions are acceptable
- After the main estimate: confirm the estimand before heterogeneity work
- Before reporting heterogeneity: confirm which subgroups are policy-relevant

## Common pitfalls
- ML flexibility presented as identification
- No cross-fitting
- Poor overlap ignored
- Heterogeneity found by search reported as fact

## Output
`models/ai/<name>-causal/ (+ model.lego.json)`

The folder holds the identification note, estimation code with cross-fitting, overlap diagnostics, heterogeneity analysis, sensitivity results and the lego manifest.

## Gate / verdict
- Identification assumptions stated
- Comparison with a conventional estimate
- Sensitivity analysis present
- Lego manifest passes `python tools/lego.py check`
- Cross-fitting and overlap diagnostics are documented
- Heterogeneity results are validated out of sample

## Suggested next steps
- `/validate-model`
- `/technical-note`
- `/lego-map`
