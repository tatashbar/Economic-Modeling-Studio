---
paths:
  - "models/semi-structural/**"
  - "models/fpas/**"
  - "models/financial-programming/**"
---
# Rules: Semi Structural Code

- Document the closure and the steady state of every gap model
- Output-gap and trend estimates report one-sided (real-time) and smoothed versions
- Judgment overlays are separate inputs, never edited into model equations
- Financial-programming identities (fiscal, monetary, external) are asserted in code
