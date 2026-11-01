---
name: ai-audit
description: "Audits AI/ML/LLM components: benchmarks, leakage, calibration, explainability, bias, red-team, confidentiality, monitoring."
argument-hint: "[model name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /ai-audit — AI Audit

**Category:** Validation & QA · **Primary agent:** `model-risk-governance-specialist`

Audits AI/ML/LLM components: benchmarks, leakage, calibration, explainability, bias, red-team, confidentiality, monitoring.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Experiment log
   - Model code
   - Evaluation card
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `model-risk-governance-specialist` — primary agent; coordinates the work and integrates results
- `ai-ethics-fairness-specialist` — Reviews AI ethics and fairness
- `llm-red-team-specialist` — Red-teams LLM systems
- `interpretable-ml-specialist` — Makes AI models explainable
- `model-validation-specialist` — Performs independent model validation

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Check data splits for leakage and benchmark fairness
2. Check calibration, uncertainty and stability across seeds, windows and versions
3. Review explainability and economic plausibility of learned relationships
4. Review bias by country group and income level; for LLMs run the red-team harness
5. Review confidentiality and human-oversight design; define monitoring

## Output
`validation/<model>/ai-audit.md`

## Gate / verdict
- Verdict: PASS / PASS WITH CONDITIONS / FAIL; failures block release

## Suggested next steps
- `/validate-model`
- `/model-risk-review`
