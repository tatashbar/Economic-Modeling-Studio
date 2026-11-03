---
paths:
  - "**/*.prg"
  - "**/*.wf1"
---
# Rules: EViews Code

- One master program (`run.prg`) runs the model from scratch; it calls the other programs in order (`include` or `exec`)
- The workfile is an output, never the source: `run.prg` creates it (`wfcreate`), imports data from a frozen vintage in `data/processed/` and rebuilds every object; never edit a `.wf1` by hand or keep results only in it
- Write equations, model objects, add factors and scenarios in programs (`model`, `append`, `addassign`, `scenario`), not by clicking in the interface
- Use relative paths from the model folder (`%0` or `cd` to the program's own folder); never a personal folder
- Set and log the seed (`rndseed`) before any bootstrap, stochastic simulation or random draw; record the EViews version in the run log
- Save results to `output/<run-id>/`: tables with `freeze` then `save` or `wfsave` to CSV, graphs with `graph.save` as PNG or PDF, series and forecasts with `wfsave` or `pagesave` to CSV
- Store parameter values and calibration choices in a scalar or table block at the top of the program with sources, not inside equations
- Run in batch from the command line (`EViews.exe /run run.prg` or the executable you have) or from Python with `pyeviews`, and end the program with `exit` so batch runs close
