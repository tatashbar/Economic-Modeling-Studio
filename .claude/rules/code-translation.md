---
paths:
  - "translations/**"
---
# Rules: Code Translation

- The source code is read-only. Never edit, move, reformat or delete files in the source folder; `source-manifest.json` holds their fingerprints and `python tools/translate.py verify-source <workspace>` must pass at sign-off
- Uploaded source folders go to `translations/incoming/<name>/`, which git ignores; do not commit third-party or confidential code
- Work from an approved `plan.md`; translated code goes to `target/` only, and agents write only to the paths the plan gives them
- Every target file starts with a header naming its source file (and line range where a file is split)
- First pass is faithful: same behavior, same outputs and file names, bugs kept and logged; refactoring and fixes come after equivalence, as separate approved changes re-tested against the same reference outputs
- Make every default explicit where languages differ: missing values, sorting, rounding, indexing, storage order, standard-error type, degrees of freedom, quantile definition, base category, solver, tolerances
- Every construct that does not translate one-to-one gets a row in `construct-log.md` with its effect on results
- Reference outputs come from the source (run here or supplied by the user, with provenance); never from the translation and never invented. Without them, equivalence is `NOT ASSESSED — NO REFERENCE OUTPUTS`
- Write outputs at full precision under the source's file names; compare with `python tools/translate.py compare` using tolerances fixed before the comparison
- Random draws: read the source's exported draws or compare distributions; never claim equal draws from equal seeds across software
- Target code follows the studio rules for its language and folder (`r-code.md`, `stata-code.md`, `eviews-code.md`, `gempack-code.md`, `model-code.md`, and the others) and runs from a clean start with one command
- The equivalence verdict comes from `translation-equivalence-auditor`, who did not translate the code
