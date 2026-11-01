# Lego View: Models as Sets of Bricks

Every model in the studio can be shown, and changed, as a **lego set**. You can see what the model is made of, snap a component on (a trade sector, a carbon-pricing block, a labor market), take one off, or swap one for an alternative, and the studio checks that the pieces still fit.

## The idea in one picture

| Lego | In the studio | Meaning |
|---|---|---|
| **Baseplate** | the core model | e.g. a gap model or a DSGE. Everything else plugs into it. A model has exactly one. |
| **Brick** | a component | a trade sector, a fiscal block, a financial accelerator, a CGE, a microsimulation, a fan-chart tool |
| **Stud** (on top) | a variable the brick **provides** | e.g. `net_exports`, with a unit |
| **Tube** (underneath) | a variable the brick **needs** | e.g. `real_exchange_rate`, with a unit and a timing (same period or lagged) |
| **Open stud** | a needed variable nothing provides | the model runs on a **stub**: a documented fallback such as "exogenous baseline path" |
| **Parts bin** | detached bricks | kept in the set, not deleted, ready to snap back on |
| **Slot** | a place only one brick may fill | e.g. the monetary policy rule: Taylor rule *or* managed-FX rule, never both |

**Why stubs matter.** A model without a trade sector still needs net exports to close the demand side. The core declares that, without a trade brick, net exports follow an exogenous path. The model therefore runs on its own, and attaching a trade brick *replaces the stub with an endogenous channel*. Detaching it switches the stub back on. Nothing breaks, and you can see exactly which feedback you switched on or off.

## What you do

| You want to | Command | What happens |
|---|---|---|
| Turn a new or existing model into a lego set | `/lego-map` | the studio proposes where to cut the model, you approve, it writes `model.lego.json` |
| See the set | `/lego-show` | text drawing, optional HTML picture or Mermaid diagram; open studs and suggested bricks |
| Add a brick (e.g. trade) | `/lego-add` | plan first: new joints, stubs retired, new simultaneous blocks, warnings. Applied only after you approve |
| Remove a brick | `/lego-detach` | stubs take over; the brick goes to the parts bin; refused if something depends on it with no stub |
| Replace a brick with an alternative | `/lego-swap` | like-for-like in the same slot; both versions compared on the same scenarios |
| Check that everything fits | `/lego-check` | all studs connected, units and frequencies consistent, identities verifiable |
| Create a brick that is not in the catalog | `/lego-brick` | defines its studs, tubes, stubs, slot and checks |

Every `/build-*` command now ends by registering the model as a lego set, so models start modular.

## What the check guarantees (and what it does not)
**Checked automatically** (`python tools/lego.py check`):
- exactly one baseplate; no two bricks provide the same variable; exclusive slots filled once
- every needed variable has a provider or a stub (otherwise an **OPEN stud** error)
- ports have units; a brick on a different frequency (e.g. an annual CGE on a quarterly core) should declare a **bridge**; the check warns until it does
- declared accounting identities (e.g. balance of payments) can be verified from the attached bricks and stubs
- **simultaneous blocks**: bricks that depend on each other in the same period are listed, with the solve order
- change history and revision count; bricks next to a changed brick are marked **stale** until re-validated
- **inside each brick** (when elements are declared): equations that do not match the endogenous variables, parameters that are assumptions without a source, and constraints not yet verified in a run. These are warnings and notes, never errors

**Not guaranteed by the tool.** It checks the *wiring*, not the economics. It cannot tell you that the elasticities in a new trade brick are sensible, or that the code implements the variables it declares. That is what `/lego-check` (manifest against code), the neutral-attachment test, calibration and `/validate-model` are for:

> **Neutral-attachment test.** After attaching a brick, set it to neutral values (no tariff change, elasticities that reproduce the old exogenous path). The baseline must match the pre-attachment baseline. If it does not, the joint is wrong.

## The picture
`python tools/lego.py show <manifest> --html view.html` writes a self-contained page (no scripts, no internet needed) with an isometric 3D scene:

- the **baseplate** is the core model, with its name along the front edge; the dashed yellow sockets on its front row are the core's open studs
- each **brick** has shaded faces, round studs, its name and a summary on the long face, and its kind on the short face; the round badge is **✓ validated**, a **ring** for not yet validated, **!** for stale (and a yellow outline)
- dashed yellow **sockets** on top of a brick are that brick's open studs (inputs running on a stub)
- **ghost bricks** (dashed, translucent, with a +) are catalog bricks that would fill an open stud, placed where they would go
- bricks **stack vertically, with no limit on the number of levels**: a brick on layer 2 or higher stands on the brick whose outputs it reads, so towers can be as tall as the model is deep (set `"layer"` on a brick to raise it, and `"on": "<brick id>"` to choose its host)
- the picture has two layouts. **grid** (the default) stands the towers side by side, tallest at the back. **pyramid** (`python tools/lego.py arrange <manifest> --apply`) builds the bricks into a stepped pyramid: each step one level up, narrower and set back, resting on the step below, with foundation components at the bottom and bricks that read them higher up; above the top step it continues as a stair as high as needed. Positions are stored in each brick's `"place"` (`x`, `y`, `level`, and `rot` 0 or 90), so any brick can be moved by hand; bricks without a place stand in the front yard. `arrange --style grid` clears the positions. Positions only affect the picture, never the wiring
- the **studs show what each brick is made of**: they are shared among its elements in proportion to their counts. Yellow **x** variables, blue **=** equations, red **θ** parameters, orange **ε** shocks, green **D** data series, purple **≤** constraints. The brick colour stays the component type, so the picture answers two questions at once: which part of the economy, and what it is built from. A switch under the picture colours the studs by component instead; a brick without declared elements keeps plain studs
- the **Inside the bricks** panel lists each brick with a bar split by element, the counts by status (endogenous or exogenous; estimated, calibrated or assumed; verified or unverified; data vintage) and its findings
- **hover** a brick to fade everything it is not connected to; the hover text also lists its elements
- detached bricks sit in the **parts bin** below; the panels at the side list stubs, joints, simultaneous blocks, identities and problems

## Files
| File | Purpose |
|---|---|
| `models/<family>/<name>/model.lego.json` | the manifest of one model: bricks, ports, slots, identities, history |
| `lego/catalog/*.json` | reusable brick specs (interfaces and checks only; no code or parameters) |
| `lego/ports.json` | shared variable names with units, so bricks agree on what a variable is |
| `lego/examples/*.lego.json` and `.html` | worked examples: a starter set and the full small open-economy set, each built as a stepped pyramid |
| `tools/lego.py` | the engine: catalog, new, show, check, attach, detach, swap, validate, arrange, elements |
| `tools/lego_view.py` | the 3D picture renderer (isometric SVG inside a self-contained HTML page) |

## Command-line use
```
python tools/lego.py catalog [--kind sector]
python tools/lego.py new models/dsge/my-model/model.lego.json --name "My model" --freq Q --class medium --bricks core-gap-open world-exogenous monetary-taylor
python tools/lego.py show  <manifest> [--html view.html] [--mermaid]
python tools/lego.py check <manifest>
python tools/lego.py attach <manifest> trade-sector-armington            # plan only
python tools/lego.py attach <manifest> trade-sector-armington --apply    # make the change
python tools/lego.py detach <manifest> financial-accelerator --apply
python tools/lego.py swap   <manifest> monetary-taylor monetary-fx-managed --apply
python tools/lego.py validate <manifest> fiscal-debt-rule --report validation/my-model/validation-report.md --apply
python tools/lego.py arrange <manifest> --apply                          # build the picture as a stepped pyramid
python tools/lego.py elements <manifest> core-gap-open --from-mod models/dsge/my-model/core.mod --apply
python tools/lego.py elements <manifest> fiscal-debt-rule --set parameters.assumed=2 data.vintage=2026Q2 --apply
```
Changes are shown as a plan and are written only with `--apply`. A change that introduces errors is refused unless `--force` is given.

- **Validation status.** `validate` records an independent validation result for one brick, with the report as evidence. Attaching, detaching or swapping a neighbour later marks it stale.
- **Identities come with bricks.** A catalog brick can declare the accounting identities it brings (the fiscal brick brings public debt dynamics, the external brick the balance of payments). They are added to the manifest when the brick is attached and set aside while it is in the parts bin.
- **Elements.** `elements` declares what a brick is made of. `--from-mod` counts a Dynare file: `var` (endogenous), `varexo_det` (exogenous), `varexo` (shocks), `parameters` (estimated if listed in `estimated_params`, calibrated otherwise), equations in the `model` block (tags and `#` model-local variables excluded), `varobs` (data series) and `occbin_constraints` (constraints, unverified until a run checks them). Only top-level declarations count, so `var e_y;` inside a `shocks` block is not a variable. Macro conditionals (`@#define`, `@#if`, `@#ifdef`, `@#else`) are followed so that only the active branch is counted; `@#for` loops and `@#include` are not expanded, and the command says so. `--set` adds or corrects what the code cannot tell, such as which calibrated parameters are assumptions without a source, a data vintage, or constraints now verified. Marking parameters as `assumed` takes them out of the calibrated ones, and marking constraints `verified` takes them out of the unverified ones, so totals stay as counted. A recount after a code change keeps these judgments and the data vintage. Without `--from-mod` or `--set` it shows the current declaration.
- **Parts bin.** A detached brick that would fill an open stud is suggested first. If its catalog definition has changed since it was detached, re-attaching takes the current definition and marks the brick unvalidated.

## Manifest format (short)
```json
{
  "name": "My model", "class": "medium", "freq": "Q", "revision": 3,
  "ports": {"net_exports": {"unit": "contribution to GDP growth, pp", "desc": "..."}},
  "required_slots": ["monetary_policy_rule"],
  "identities": [{"name": "balance of payments", "ports": ["current_account", "net_exports", "net_foreign_assets"], "brick": "external-bop-nfa"}],
  "bricks": [{
    "id": "trade-sector-armington", "kind": "sector", "freq": "Q", "status": "attached", "validation": "unvalidated",
    "slot": null, "bridge": null, "code": "models/trade/my-trade/",
    "elements": {"variables": {"endogenous": 9}, "equations": 9, "parameters": {"estimated": 3, "calibrated": 5, "assumed": 1},
                 "shocks": 1, "data": {"series": 4, "vintage": "2026Q2"}, "constraints": {"verified": 1, "unverified": 0}},
    "provides": ["net_exports"],
    "requires": ["real_exchange_rate", {"port": "tariff_rate", "stub": "unchanged baseline tariff path"},
                 {"port": "output_gap", "lag": 1}]
  }]
}
```
- `requires` entries are a port name, or an object with `lag` (1 = uses the previous period) and `stub` (the documented fallback; no stub means a hard requirement).
- `kind` is one of: baseplate, environment, policy, fiscal, external, financial, sector, climate, household, satellite, output.
- `status` is `attached` or `detached`; `validation` is `validated`, `unvalidated` or `stale`; a validated brick also records `validation_report` and `validated_on`.
- An identity with a `brick` belongs to that brick and is checked only while the brick is attached.
- `elements` is optional. Each element is a whole number or an object with its status fields: variables (`endogenous`, `exogenous`), parameters (`estimated`, `calibrated`, `assumed`), data (`series`, plus a free-text `vintage`), constraints (`verified`, `unverified`); equations and shocks are whole numbers. `elements_source` records the file they were counted from.

## Adding your own bricks
The catalog covers a small open-economy set (core, rest of world, two monetary rules, fiscal, trade, external, financial, labor, commodities, carbon and energy, physical climate damage, input-output, CGE, household incidence, fan charts), integrated-policy-framework tools (FX intervention, capital flow measures, macroprudential policy) and a baseplate for stand-alone input-output or SAM models (`core-io-leontief`). It is a starting point, not a complete library. Use `/lego-brick` to add yours, and build the component itself with the relevant `/build-*` command.

## Limits
- One baseplate per set. Bricks inside a strongly simultaneous system (for example the household and firm blocks of one DSGE) are better kept as a single brick than cut apart.
- The tool does not run models. It manages the structure; solving, calibrating and simulating stay in your model code.
- Ports are scalar or named series. Distributions, matrices (such as an input-output table) and cross-country blocks should be agreed as named ports with a documented shape.
