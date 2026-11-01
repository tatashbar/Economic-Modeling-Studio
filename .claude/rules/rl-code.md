---
paths:
  - "models/ai/**/*drl*/**"
  - "models/ai/**/*rl*/**"
---
# Rules: Rl Code

- The reward must be the documented welfare criterion; changes need approval from economic-reasoning-specialist and the user
- Verify the environment against known-optimal cases before training
- Train with multiple seeds and report the distribution of outcomes
- Compare with simple rules; run an out-of-distribution stress test
