---
paths:
  - "models/**/model.lego.json"
  - "lego/**"
---
# Rules: Lego Manifests

- Every variable exchanged between bricks is a declared port with a unit from `lego/ports.json`
- Every required input has a source brick or a documented stub; a requirement without a stub is intentional
- Declare lags explicitly; same-period dependencies form simultaneous blocks that the solver must handle jointly
- A brick on a different frequency from the core declares a bridge with a method for each port it exchanges (`sum`, `average`, `last`, `first`, `split`, `repeat`, `interpolate`), never only a text note, and the bridge passes `python tools/lego.py bridge-test --apply` before the brick is validated
- Keep the three records apart: wiring (`check`), numbers (`validate`, after `/validate-model`) and sign-off (`approve --by NAME`, only by the economist, only after the numbers). Never infer one from another; run `check --strict` before release
- Change the set of bricks only with `python tools/lego.py attach|detach|swap --apply`, and record validation results only with `python tools/lego.py validate`, so the history, revision and stale markers stay correct
- Ports, required slots and identities may be edited by hand; run `python tools/lego.py check` afterwards
- Picture positions (`place`) come from `python tools/lego.py arrange` or are edited by hand; they never change the wiring, and `check` warns if bricks overlap or float
- A brick is marked validated only with a validation report as evidence (`validate --report <path>`)
- A brick changed since validation is stale and is re-validated, with its neighbours, before release
- Declare each brick's elements (variables, equations, parameters, shocks, data, constraints) with `python tools/lego.py elements`, counted from the code where possible; mark unsourced parameters as `assumed` and constraints as `verified` only after a run confirms them
