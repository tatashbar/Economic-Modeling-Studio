---
paths:
  - "tests/**"
  - "**/test_*.py"
  - "**/*_test.jl"
  - "**/test_*.m"
---
# Rules: Tests

- Tests verify identities, steady state, known analytical cases and regression baselines
- Use tolerance-based comparisons for floating point; document tolerances
- Tests must be deterministic: fixed seeds, no network access
- Add a regression test for every bug fixed
