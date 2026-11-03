---
paths:
  - "models/**"
---
# Rules: Model Code

- No hard-coded parameter values in equations or solver code; parameters come from a parameter file or block with sources
- Every model has a documented timing convention, units and base period
- Assert accounting identities and steady-state residuals in tests
- Use fixed random seeds for any stochastic routine; seeds are logged
- Never overwrite a baseline; write new results to a new, versioned path
- Models must run from a clean checkout with one documented command
- Every run saves its results (tables, charts, simulated paths, impulse responses, forecasts) to `output/<run-id>/` inside the model folder, with a `run-log.md` recording the date, the command, the code version, the data vintage, the parameter file and the seed; results first shown in a chat are saved there too
- Model code lives in files in the model folder, in an approved language (`toolchains` in `studio-config.yaml`), never only in a chat or a notebook
