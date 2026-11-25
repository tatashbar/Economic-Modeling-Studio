# Replication files: "Modular macroeconomic modelling with AI agents: An open agentic framework for policy analysis"

Tohid Atashbar, *Economic Modelling* (submitted).

These files reproduce every number, table and figure in the paper. All results were produced with Economic Modeling Studio **version 3.3.0, commit `76797dbce6433ce570e8d64ceca4e87bd2433746`**. Later commits may give slightly different results.

## Requirements
- Python 3.9 or later. The studio's engines use only the standard library.
- `matplotlib` (figures) and `python-docx` (Word tables), only for `fig_*.py` and `build_docx.py`.
- No external data: every economy is simulated, and the model manifests ship with the studio.

## How to run
These files sit on their own branch, apart from the studio's main code. Check out the studio at the commit above and put this branch in a folder inside it (the scripts find the studio root on their own; set `EMS_ROOT` to point elsewhere):

```
git clone https://github.com/tatashbar/Economic-Modeling-Studio.git ems
cd ems && git checkout 76797dbce6433ce570e8d64ceca4e87bd2433746
git clone --branch economic-modelling-2026 --single-branch https://github.com/tatashbar/Economic-Modeling-Studio.git replication
cd replication
```

| Step | Command | Output (`output/<run>/`) | Paper |
|---|---|---|---|
| 1 | `python scripts/lego_experiments.py` | `lego/` change-impact plans, swap, detach, bridge sequence | Section 7, Tables 5-6 |
| 2 | `python scripts/ael_baseline.py` | `ael-baseline/` known answers, moments, entities, scale | Section 8.3, Tables 7-9 |
| 3 | `python scripts/rsim_vs_random.py --reps 3 --budget 400 --pop 16` | `rsim/` RSIM and random-search studies, test scores | Sections 8.4-8.5, Tables 10-11, Fig. 2 |
| 4 | `python scripts/ael_policy.py` | `ael-policy/` policy experiments (uses the step-3 champion) | Section 8.6, Table 12, Fig. 3 |
| 5 | `python scripts/swarm_run.py` | `swarm/` 100-agent swarm with a person stepping in | Section 8.7 |
| 6 | `python scripts/fig_results.py` | `figures/` (Fig. 1 is the studio's own lego picture, `docs/images/lego-full-set-v2.png`) | Figs. 2, 3 |

Each run folder has a `run-log.json` with the script, start and end time, studio commit, Python version and platform. `scripts/tables.py` reads the saved outputs and holds every table and in-text number.

## Notes on reproducibility
- The AEL is deterministic given a seed. The policy experiments and the random-search benchmark reproduce exactly.
- RSIM's loop variations are deterministic given the study name and round. Its **hidden seeds are drawn at random when a study starts**, by design, so that no one can tune to them. Training trajectories therefore reproduce, while the choice of champion can differ when a candidate is refused as overfit. The hidden seeds used for the paper are recorded in `output/rsim/rsim-vs-random.json` (`hidden_seeds_record`).
- Run times depend on the machine. The paper's times come from a 16-core Windows desktop computer, and the 100,000-household run shared the processor with step 3.

## Licence
MIT, as for the studio.
