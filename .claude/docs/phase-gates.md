# Phase Gates

Run with `/gate-check <stage>`. Verdicts: **PASS**, **CONCERNS** (proceed with named conditions), **FAIL**, **NOT ASSESSED** (required evidence absent; never treated as a pass).

| Gate | Exit criteria (evidence) | Reviewed by |
|---|---|---|
| **Concept** | Scope note (`docs/briefs/`); model brief with purpose, non-purposes, model class and risk level | `economic-reasoning-specialist`, `project-planning-specialist` |
| **Design** | Model spec with matching equation/unknown counts; calibration plan; data sheet with classification; simple benchmark defined | `modeling-methodology-specialist`, `economic-reasoning-specialist` |
| **Build** | Code in `models/`; tests passing (identities, steady state or benchmark replication, regression); no hard-coded parameters; code review done; for AI: experiment log and benchmark scores | `modeling-methodology-specialist` |
| **Estimate** | Estimation or calibration report; convergence and identification evidence; fit and out-of-sample results | `modeling-methodology-specialist`, `economic-reasoning-specialist` |
| **Validate** | Independent validation report with rating not FAIL; no open High findings; replication report; for AI: `/ai-audit` | `model-risk-governance-specialist` |
| **Release** | Release recommendation APPROVED; model card; release notes; registry entry; replication package | `model-risk-governance-specialist`, `project-planning-specialist` |

Rules:
- A phase does not start before the previous gate is PASS, or CONCERNS with named owners and dates.
- The gate report lists each criterion as FOUND or ABSENT with a file path.
- A waiver needs a written rationale from the user and is recorded in the gate report.
