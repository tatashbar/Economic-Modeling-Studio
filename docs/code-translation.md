# Code translation

The studio translates code between the languages and software used for economic models. Point it at a folder, or upload one, name the target, and a team of agents analyzes the source, plans the work, translates file by file and tests whether the translation reproduces the source's outputs.

## Quick start

```
/translate-code path/to/code python
```

Without arguments, `/translate-code` asks for the folder and shows the targets to choose from. An uploaded folder is copied to `translations/incoming/<name>/`, which git ignores. The source folder is never changed.

Other commands:

| Command | What it does |
|---|---|
| `/code-inventory` | Languages, files, call graph, data in and out, packages, risky constructs, entry points |
| `/translation-plan` | The plan only: file mapping, agents, libraries, pitfalls and idioms for the pair, decisions, tolerances |
| `/translate-code` | The whole translation, from inventory to signed-off package |
| `/translate-model` | A model definition (Dynare, IRIS, GAMS, GEMPACK and others), checked on steady state, solution, IRFs and moments or benchmark solutions |
| `/equivalence-test` | Compares the outputs of two codes with fixed tolerances and gives a verdict |

## How the agents work together

1. **`source-code-analyst`** reads the source and writes down what each file computes, the state it carries and the defaults it relies on.
2. **`code-translation-architect`** writes the plan, assigns files in dependency order and integrates the result.
3. Three translators work in parallel on independent files:
   - **`statistical-code-translation-specialist`**: Stata, R, Python, SAS, SPSS, EViews, RATS, gretl, LIMDEP, Stan and JAGS
   - **`model-code-translation-specialist`**: Dynare, IRIS, RISE, MATLAB, Octave, Julia, GAMS, GEMPACK, AMPL, TROLL, C and C++
   - **`legacy-code-translation-specialist`**: COBOL, Fortran, GAUSS, TSP, Excel and VBA, FAME and AREMOS, SQL
4. **`translation-equivalence-auditor`**, who did not translate anything, compares the outputs and gives the verdict.

Engineering agents for the target (`matlab-dynare-engineer`, `python-julia-engineer`, `reproducibility-engineer`) and domain specialists (solution methods, CGE, panel econometrics) join where needed.

## The workspace

`python tools/translate.py plan <source> --to <target>` creates `translations/<name>-to-<target>/`:

| File or folder | Contents |
|---|---|
| `inventory.md`, `inventory.json` | Files by language, call graph, data in and out, packages, constructs to check, translation order |
| `source-manifest.json` | A fingerprint of every source file, checked at the end |
| `plan.md` | Checks, decisions for the user, file mapping with agents, pitfalls and idioms for the pair, equivalence plan, sign-off list |
| `behavior-spec.md` | What each source file computes (written by the analyst) |
| `target/` | The translated code, with a README and a one-command run |
| `reference-outputs/`, `translated-outputs/` | Outputs of the source and of the translation, at full precision and with the same names |
| `construct-log.md` | Every construct that did not translate one-to-one, and its effect |
| `equivalence/report.md` | Cell-by-cell comparison and verdict |
| `translation-report.md` | Scope, mapping, evidence, differences, what was not assessed, how to run |

## The tool

```
python tools/translate.py languages [--kind statistical] [--target-only]
python tools/translate.py idioms --from stata --to python [--task robust]
python tools/translate.py inventory <folder> [--out <folder>]
python tools/translate.py plan <folder> --to <target> [--name <name>]
python tools/translate.py compare <reference-dir> <translated-dir> [--key id year] [--rtol 1e-6] [--atol 1e-9] [--out report.md]
python tools/translate.py verify-source <workspace>
```

`compare` reads CSV (any common delimiter) and JSON outputs and compares them cell by cell within `atol + rtol x |reference|`. It treats the usual missing-value codes (`.`, `NA`, `NaN`, blank, `NULL`) as equal to each other, and Fortran exponents such as `1.5D+00` as numbers. Rows are matched by order or by key columns, and other files by content. It exits with code 1 if anything differs.

## Languages and software

The list and the pitfalls of each language live in [`docs/translation/languages.json`](translation/languages.json). Common operations side by side, with the defaults that make them differ, are in [`docs/translation/idioms.json`](translation/idioms.json). After editing the list, refresh this table with `python tools/translate.py languages --write-doc`.

<!-- BEGIN GENERATED: languages -->
| Language or software | Kind | Files | From | To | Studio toolchain |
|---|---|---|---|---|---|
| Python (NumPy, pandas, SciPy, statsmodels, linearmodels) | numerical | `.py` `.ipynb` | yes | yes | `python` |
| R | statistical | `.R` `.r` `.Rmd` `.qmd` `.Rproj` | yes | yes | `r` |
| Stata (do-files, ado-files, Mata) | statistical | `.do` `.ado` `.mata` `.dta` | yes | yes | `stata` |
| MATLAB (with Econometrics, Optimization and Statistics toolboxes) | numerical | `.m` `.mat` `.mlx` | yes | yes | `matlab-dynare` |
| GNU Octave | numerical | `.m` | yes | yes | `matlab-dynare` |
| Julia | numerical | `.jl` | yes | yes | `julia` |
| Dynare (.mod files, run in MATLAB or Octave) | model | `.mod` `.inc` | yes | yes | `matlab-dynare` |
| IRIS toolbox (MATLAB; .model files) | model | `.model` `.mdl` | yes | yes | `matlab-dynare` |
| RISE toolbox (MATLAB; regime-switching models) | model | `.rs` `.dsge` | yes | - | `matlab-dynare` |
| EViews (programs and workfiles) | statistical | `.prg` `.wf1` | yes | yes | `eviews` |
| SAS (data step, PROCs, macro language) | statistical | `.sas` `.sas7bdat` | yes | yes | - |
| SPSS syntax | statistical | `.sps` `.sav` | yes | - | - |
| GAUSS | legacy | `.gss` `.src` `.prg` `.g` | yes | - | - |
| RATS / WinRATS | statistical | `.rpf` `.prg` `.src` | yes | - | - |
| gretl (hansl scripts) | statistical | `.inp` `.gdt` | yes | yes | - |
| Ox | numerical | `.ox` `.oxh` | yes | - | - |
| LIMDEP / NLOGIT | statistical | `.lim` | yes | - | - |
| TSP | legacy | `.tsp` | yes | - | - |
| TROLL (macroeconometric models) | model | `.inp` `.src` `.mod` | yes | - | - |
| FAME / AREMOS (time-series databases and scripts) | database | `.pro` `.inp` `.cmd` | yes | - | - |
| GAMS (CGE and optimization models) | optimization | `.gms` `.inc` `.gdx` | yes | yes | `gams` |
| GEMPACK (TABLO .tab, command .cmf; GTAP) | model | `.tab` `.cmf` `.har` `.sti` `.prm` | yes | yes | `gempack` |
| AMPL | optimization | `.mod` `.dat` `.run` | yes | - | - |
| Fortran (77 and 90+) | legacy | `.f` `.for` `.f77` `.f90` `.f95` `.f03` `.f08` | yes | yes | - |
| C and C++ | numerical | `.c` `.h` `.cpp` `.cc` `.hpp` | yes | yes | - |
| COBOL | legacy | `.cbl` `.cob` `.cpy` `.cobol` | yes | - | - |
| Excel workbooks (formulas) and VBA macros | spreadsheet | `.xlsx` `.xlsm` `.xls` `.xlsb` `.bas` `.cls` `.frm` | yes | - | - |
| Mathematica / Wolfram Language | numerical | `.nb` `.wl` `.m` | yes | - | - |
| Maple | numerical | `.mw` `.mpl` | yes | - | - |
| Scilab | numerical | `.sce` `.sci` | yes | - | - |
| Stan, JAGS and BUGS (Bayesian models) | bayesian | `.stan` `.bug` `.jags` `.odc` | yes | yes | - |
| SQL | database | `.sql` | yes | yes | - |
<!-- END GENERATED: languages -->

"From" means the studio reads and translates code in that language; "To" means it writes code in it. Targets outside the approved toolchains in `studio-config.yaml` need the user's confirmation and their organization's approval.

## What makes translations go wrong

Defaults differ more often than functions do. The checks the agents run first:

- **Missing values.** Stata treats missing as larger than any number and SAS as smaller; R propagates NA; pandas skips NaN in means but NumPy does not.
- **Standard errors.** Stata's robust errors are HC1, but R's `vcovHC` defaults to HC3. Clustered errors use different small-sample factors in different packages.
- **Rounding.** R, Python and VBA round half to even; Stata, MATLAB, SAS and Excel worksheets round half away from zero.
- **Indexing and storage.** Python, C and Ox count from 0. MATLAB, R, Julia and Fortran store arrays by column, NumPy by row.
- **Lags and sorting.** Stata and EViews lags respect gaps in the time index; positional shifts do not. Unstable sorts change which duplicate is kept.
- **Precision.** Stata `generate` creates float by default; Fortran literals are single precision without `d0`; COBOL decimals need exact decimal arithmetic.
- **Random numbers.** The same seed gives different draws in every language.
- **Model timing and representation.** Dynare dates stocks by the period they are chosen. Log and level variables, linearized and levels CGE forms, and theoretical and simulated moments are not interchangeable.

## Rules

Translation workspaces follow [`.claude/rules/code-translation.md`](../.claude/rules/code-translation.md): the source is read-only, the first pass is faithful, every default is explicit, every difference is logged, and the verdict comes from an auditor who did not translate the code.
