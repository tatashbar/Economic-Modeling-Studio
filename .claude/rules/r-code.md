---
paths:
  - "**/*.R"
  - "**/*.Rmd"
  - "**/*.qmd"
---
# Rules: R Code

- One master script (`run.R`) runs the model from a clean session with `Rscript run.R`; it sources the other scripts in order
- Pin package versions with `renv` and commit `renv.lock`; record the R version
- Use relative paths from the model folder (or `here::here()`); never `setwd()` to a personal folder
- No `rm(list = ls())` or reliance on objects left in the workspace; scripts start from a fresh session
- Set and log the seed (`set.seed`) before any bootstrap, simulation or random split
- Read data from a frozen vintage in `data/processed/`; never overwrite a source file
- Save tables with `write.csv` or `saveRDS` and charts with `ggsave` or `png()` to `output/<run-id>/`; write the session details (`sessionInfo()`) to the run log
- Put reusable functions in `R/` and test them with `testthat` in `tests/testthat/`
- R Markdown and Quarto files are for reports; results they show must come from scripts that save them to `output/<run-id>/`
