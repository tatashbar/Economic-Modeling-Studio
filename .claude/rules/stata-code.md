---
paths:
  - "**/*.do"
  - "**/*.ado"
---
# Rules: Stata Code

- One master do-file (`run.do`) runs the model from a clean start; it calls the other do-files in order
- Pin the version at the top of every do-file (`version 17` or the version you use) and start with `clear all` and `set more off`
- Use relative paths from the model folder; never `cd` to a personal folder
- Set and log the seed (`set seed`) before any bootstrap, simulation or random split
- Read data from a frozen vintage in `data/processed/`; never overwrite a source `.dta`
- Write a text log for each run (`log using "output/<run-id>/stata-log.txt", text replace`) next to the run log
- Save estimates and tables with `esttab`, `putexcel` or `export delimited` to `output/<run-id>/`, and graphs with `graph export` as PNG or PDF
- Record user-written packages (`ssc install`, `net install`) and their versions in the model README; prefer built-in commands
- Run in batch mode for reproducibility (`stata-mp -b do run.do` or the edition you have)
