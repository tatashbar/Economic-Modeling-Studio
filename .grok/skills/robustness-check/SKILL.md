---
name: robustness-check
description: "Tests conclusions under alternative models, identification schemes, samples, priors and data vintages."
---
<!-- Generated from .claude/skills/robustness-check/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /robustness-check — Robustness Check

**Category:** Validation & QA · **Primary agent:** `model-validation-specialist`

Tests conclusions under alternative models, identification schemes, samples, priors and data vintages.

Arguments: whatever the user wrote after the command name.

## Purpose
Test whether the conclusions of an analysis survive reasonable alternatives: other models, identification schemes, samples, priors and data vintages. The output separates robust conclusions from fragile ones and proposes wording that matches the strength of the evidence.

**Use it when** results will inform decisions or publication, or when reviewers question a specific modeling choice.

**Do not use it when** the aim is to rank parameter drivers within one model (`/sensitivity-analysis`).

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Result to test
   - Alternative specs
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `model-validation-specialist` — primary agent; coordinates the work and integrates results
- `sensitivity-uncertainty-specialist` — Quantifies uncertainty and sensitivity
- `forecast-combination-specialist` — Combines forecasts

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Dimension | Typical alternatives |
|---|---|
| Model | alternative model class or specification |
| Identification | alternative restrictions or instruments |
| Sample | excluding crises, post-break, longer history |
| Priors | wider, alternative families |
| Data | earlier vintages, alternative sources |

## Workflow
1. Define which dimensions of the result could plausibly change
   - Focus on the conclusions that matter for the decision
2. Re-run under alternatives: model, identification, sample, priors, vintage
3. Summarize which conclusions are robust and which are not
4. Recommend wording changes for non-robust conclusions

## Checkpoints with the user
- After choosing dimensions: confirm alternatives are reasonable
- After results: agree wording changes

## Common pitfalls
- Only testing alternatives that are expected to agree
- Treating robustness of signs as robustness of magnitudes
- Not changing the wording when a conclusion is fragile

## Output
`validation/<model>/robustness-report.md`

The report lists each conclusion, the alternatives tested, results and a robustness rating, with recommended wording.

## Gate / verdict
- Non-robust conclusions are flagged in outputs
- Alternatives include at least one that could plausibly overturn the main conclusion

## Suggested next steps
- `/validate-model`
- `/policy-brief`
