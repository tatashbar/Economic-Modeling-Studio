# Model Risk Levels

The level is set in the model brief by `model-risk-governance-specialist` together with `economic-reasoning-specialist`, and agreed with the user. It determines validation depth and review frequency.

| Level | Criteria (any) | Validation | Revalidation |
|---|---|---|---|
| **Low** | Exploratory; internal; not published; no direct policy use | Peer review + tests; labelled "exploratory" | On major change |
| **Medium** | Informs advice; feeds a forecast; limited audience | Independent validation (standard depth) | Every 24 months or on major change |
| **High** | Feeds published numbers or decisions; large or multi-country; AI/LLM in the decision path; sensitive data | Independent validation (full depth), replication, benchmark and sensitivity; `/ai-audit` when AI is involved | Every 12 months, on major change, or when performance degrades |

Principles:
- Builders and validators are independent.
- Findings are rated High (blocks release), Medium (condition with a date) or Low (tracked).
- AI components in the decision path default to High until shown otherwise.
- Every model has an owner, a model card and a registry entry (`production/model-registry.md`).
- Use limits: a model may not be used for purposes named as non-purposes in its card.
