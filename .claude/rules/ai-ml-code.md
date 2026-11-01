---
paths:
  - "models/ai/**"
---
# Rules: AI ML Code

- Build the traditional benchmark first and record its score
- Use time-aware splits; no randomized splits on time series; verify no look-ahead
- Log every run: code version, data version, seed, hyperparameters, metrics
- Select hyperparameters and models using validation data only; test data are touched once
- Report calibration and uncertainty, not only point accuracy
- Document compute and failure cases; save interpretability outputs
