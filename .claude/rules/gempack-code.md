---
paths:
  - "**/*.tab"
  - "**/*.cmf"
  - "models/**/gtap*/**"
---
# Rules: GEMPACK and GTAP Code

- The model code is the TABLO file (`.tab`); record which model and version it is (for example standard GTAP 7, GTAP-E, GTAP-POWER) and every change made to it
- One command file (`.cmf`) per experiment holds the files used, the closure, the shocks and the solution method; never run an experiment from settings saved only in RunGTAP or another interface
- The closure is written out in the `.cmf` and justified; report results under a second closure where they matter
- Solve with a multi-step method (Gragg with extrapolation, for example 2-4-6 steps) and report the extrapolation accuracy; a one-step Johansen solution is for checks only
- Check the benchmark before any shock: a zero-shock run (homogeneity test with a numeraire shock) reproduces the database
- Keep the aggregation mapping (GTAPAgg or FlexAgg sectors, regions and endowments) with the model and record the database version and base year (for example GTAP 11, 2017)
- Elasticities are sourced; report systematic sensitivity on the key ones (Armington, CET, factor mobility)
- Report welfare as equivalent variation with its decomposition (allocative, terms of trade, endowment, technical change), and use subtotals to split results by shock
- Export results from the solution file (`.sl4`) to CSV with SLTOHT or ViewHAR into `output/<run-id>/`, together with the `.cmf` and the log of the run
- **The GTAP database is licensed.** Keep it in `data/raw/gtap/` (outside git), never commit, share or upload the database or files derived from it at full detail, and record the license holder; only aggregated results may leave the studio
- Run in batch from the command line (the compiled model with `-cmf`, or `gemsim`) so every experiment reruns with one command
