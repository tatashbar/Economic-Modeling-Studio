#!/usr/bin/env python3
"""Lego view of an economic model.

A model is a LEGO SET: one baseplate (the core model) plus bricks (components such as a trade
sector, a fiscal block, a carbon-pricing block). Bricks connect through studs (ports): named
variables with units and timing. A brick that is not attached leaves open studs; the consumer's
declared STUB (a documented fallback such as "exogenous baseline path") keeps the model running.

Manifest: <model folder>/model.lego.json     Catalog: lego/catalog/*.json     Ports: lego/ports.json

Commands (changes are shown as a plan; nothing is written without --apply):
  catalog                         list reusable bricks
  new <manifest> --name N --freq Q --class medium --bricks ID [ID ...]
  show <manifest> [--html FILE] [--mermaid]
  check <manifest>                exit code 1 if there are errors
  attach <manifest> <brick-id|file> [--apply] [--force]
  detach <manifest> <brick-id> [--apply] [--force]
  swap <manifest> <old-brick-id> <new-brick-id|file> [--apply] [--force]
  arrange <manifest> [--style pyramid|grid] [--apply]
  validate <manifest> <brick-id> --report FILE [--apply]
  elements <manifest> <brick-id> [--from-mod FILE] [--set KEY=VALUE ...] [--apply]

Inside each brick: an optional "elements" block declares what the brick is made of (variables, equations,
parameters, shocks, data series, constraints), with their status (estimated, calibrated or assumed parameters;
verified or unverified constraints). The picture colours each brick's studs by these elements, and `check` flags
equation counts that do not match the endogenous variables, unsourced parameters and unverified constraints.
"""
import argparse
import copy
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_DIR = os.path.join(ROOT, "lego", "catalog")
PORTS_FILE = os.path.join(ROOT, "lego", "ports.json")

KINDS = ["baseplate", "environment", "policy", "fiscal", "external", "financial", "sector", "climate",
         "household", "satellite", "output"]
LAYER = {"baseplate": 0, "environment": 1, "policy": 1, "fiscal": 1, "external": 1, "financial": 1, "sector": 1,
         "climate": 1, "household": 1, "satellite": 2, "output": 2}
VALIDATION = ("validated", "unvalidated", "stale")
STATUS = ("attached", "detached")
MARK = {"validated": "[v]", "unvalidated": "[ ]", "stale": "[~]"}


# ------------------------------------------------------------------ io
def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_catalog():
    cat = {}
    if os.path.isdir(CATALOG_DIR):
        for fn in sorted(os.listdir(CATALOG_DIR)):
            if fn.endswith(".json"):
                b = read_json(os.path.join(CATALOG_DIR, fn))
                cat[b["id"]] = b
    return cat


def load_ports():
    return read_json(PORTS_FILE) if os.path.exists(PORTS_FILE) else {}


# ------------------------------------------------------------------ brick helpers
def reqs(b):
    out = []
    for r in b.get("requires", []):
        if isinstance(r, str):
            r = {"port": r}
        out.append({"port": r["port"], "lag": int(r.get("lag", 0)), "stub": r.get("stub")})
    return out


def provs(b):
    return [p if isinstance(p, str) else p["port"] for p in b.get("provides", [])]


def find(m, bid):
    for b in m.get("bricks", []):
        if b.get("id") == bid:
            return b
    return None


def attached(m):
    return [b for b in m.get("bricks", []) if b.get("status", "attached") == "attached"]


def layer_of(b):
    return b.get("layer", LAYER.get(b.get("kind"), 1))


def supports(att):
    """Which bricks each brick stands on: {id: set of ids}. A brick stands on every brick whose outputs it reads,
    unless that brick sits on a higher layer. Between bricks on the same layer, reading is enough (the fiscal rule
    stands on the oil sector whose revenue it reads), except inside a loop: bricks that read each other, directly or
    round a cycle, stand side by side. The result has no cycles, so it can be built from the bottom up."""
    ids = {b["id"]: b for b in att}
    reads = {b["id"]: {o["id"] for o in att if o is not b and {q["port"] for q in reqs(b)} & set(provs(o))} for b in att}

    def reach(a):  # bricks reachable from a along same-layer reads
        seen, todo = set(), [a]
        while todo:
            for o in reads[todo.pop()]:
                if o not in seen and layer_of(ids[o]) == layer_of(ids[a]):
                    seen.add(o)
                    todo.append(o)
        return seen

    loops = {a: reach(a) for a in ids}
    return {a: {o for o in reads[a] if layer_of(ids[o]) < layer_of(ids[a])
                or (layer_of(ids[o]) == layer_of(ids[a]) and a not in loops[o])} for a in ids}


def depths(att):
    """Height of each brick in the stacking order: 1 for a brick that stands on nothing, else one more than the
    tallest brick it stands on."""
    sup, d = supports(att), {}

    def depth(a):
        if a not in d:
            d[a] = 1 + max((depth(o) for o in sup[a]), default=0)
        return d[a]

    for a in sup:
        depth(a)
    return d


# ------------------------------------------------------------------ elements (what a brick is made of)
# element -> the status breakdown it may carry; a plain whole number is also accepted
ELEMENTS = {"variables": ("endogenous", "exogenous"), "equations": (), "parameters": ("estimated", "calibrated", "assumed"),
            "shocks": (), "data": ("series",), "constraints": ("verified", "unverified")}
ELEMENT_SYMBOL = {"variables": "x", "equations": "=", "parameters": "θ", "shocks": "ε", "data": "D", "constraints": "≤"}
ELEMENT_TEXT = ("vintage", "source")  # free-text fields allowed inside an element (e.g. data vintage)


def elements_of(b):
    """Normalized elements of a brick and the problems found: ({name: {"total": n, "parts": {...}, "text": {...}}}, [msg])."""
    raw, out, probs = b.get("elements"), {}, []
    if raw is None:
        return out, probs
    if not isinstance(raw, dict):
        return out, ["elements must be an object such as {\"variables\": 12, \"equations\": 12}"]
    whole = lambda v: isinstance(v, int) and not isinstance(v, bool) and v >= 0
    for name, v in raw.items():
        if name not in ELEMENTS:
            probs.append(f"unknown element '{name}' (use: {', '.join(ELEMENTS)})")
            continue
        if whole(v):
            out[name] = {"total": v, "parts": {}, "text": {}}
            continue
        if not isinstance(v, dict):
            probs.append(f"element '{name}' must be a whole number or an object")
            continue
        parts, text = {}, {}
        for k, x in v.items():
            if k in ELEMENT_TEXT:
                text[k] = str(x)
            elif k not in ELEMENTS[name]:
                probs.append(f"element '{name}': unknown field '{k}' (use: {', '.join(ELEMENTS[name] + ELEMENT_TEXT) or 'a whole number'})")
            elif not whole(x):
                probs.append(f"element '{name}.{k}' must be a whole number")
            else:
                parts[k] = x
        out[name] = {"total": sum(parts.values()), "parts": parts, "text": text}
    return out, probs


def element_flags(b, el):
    """Findings that matter for the model, in order of severity: (level, message) with level 'warn' or 'note'."""
    f = []
    endo = el.get("variables", {}).get("parts", {}).get("endogenous")
    if endo is None and "variables" in el and not el["variables"]["parts"]:
        endo = el["variables"]["total"]
    eq = el.get("equations", {}).get("total")
    if endo is not None and eq is not None and endo != eq:
        f.append(("warn", f"{eq} equations for {endo} endogenous variables (the brick's system is not square)"))
    unver = el.get("constraints", {}).get("parts", {}).get("unverified", 0)
    if unver:
        f.append(("warn" if b.get("validation") == "validated" else "note",
                  f"{unver} constraint(s) not yet verified in a run" + (" although the brick is marked validated"
                                                                        if b.get("validation") == "validated" else "")))
    assumed = el.get("parameters", {}).get("parts", {}).get("assumed", 0)
    if assumed:
        f.append(("note", f"{assumed} parameter(s) are assumptions without a source (show them in sensitivity runs)"))
    return f


def elements_line(el):
    """Compact text such as: x 14 (12 endogenous, 2 exogenous) · = 12 · θ 18 (6 estimated, 12 calibrated)."""
    bits = []
    for name in ELEMENTS:
        if name not in el:
            continue
        e = el[name]
        nz = [(k, n) for k, n in e["parts"].items() if n and not (name == "data" and k == "series")]
        extra = nz[0][0] if len(nz) == 1 else ", ".join(f"{n} {k}" for k, n in nz)
        extra = ", ".join(x for x in (extra, *(f"{k} {t}" for k, t in e["text"].items())) if x)
        noun = "data series" if name == "data" else (name[:-1] if e["total"] == 1 else name)
        bits.append(f"{ELEMENT_SYMBOL[name]} {e['total']} {noun}" + (f" ({extra})" if extra else ""))
    return " · ".join(bits)


def _strip_mod(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return re.sub(r"(?m)^\s*%[^\n]*", " ", text)


def _macro_value(expr, defs):
    """Value of a simple macro expression (numbers, true/false, defined names, comparisons, &&, ||, !), or None."""
    out = []
    for tok in re.findall(r"\d+(?:\.\d+)?|[A-Za-z_]\w*|==|!=|<=|>=|&&|\|\||[!<>()]|\"[^\"]*\"|\S", expr.strip()):
        if tok in ("true", "false"):
            out.append("1" if tok == "true" else "0")
        elif re.match(r"^[A-Za-z_]\w*$", tok):
            if tok not in defs:
                return None
            out.append(repr(defs[tok]))
        elif tok in ("&&", "||"):
            out.append(" and " if tok == "&&" else " or ")
        elif tok == "!":
            out.append(" not ")
        elif re.match(r"^(\d+(\.\d+)?|==|!=|<=|>=|[<>()]|\"[^\"]*\")$", tok):
            out.append(tok)
        else:
            return None
    try:
        return eval("".join(out), {"__builtins__": {}}, {})  # only literals and operators reach this point
    except Exception:
        return None


def _macro(text, notes):
    """Apply the Dynare macro conditionals (@#define, @#if, @#ifdef, @#ifndef, @#else, @#endif) so that only the
    active branch is counted. Loops and includes are not expanded; a note then says the counts may be incomplete."""
    defs, stack, out = {}, [], []
    active = lambda: all(a for a, _ in stack)
    for line in text.split("\n"):
        st = line.strip()
        if not st.startswith("@#"):
            if active():
                out.append(line)
            continue
        d = st[2:].strip()
        kw = (d.split() or [""])[0]
        if kw == "define":
            mm = re.match(r"define\s+(\w+)\s*=\s*(.+)$", d)
            if mm and active():
                v = _macro_value(mm.group(2), defs)
                defs[mm.group(1)] = v if v is not None else mm.group(2).strip()
        elif kw in ("if", "ifdef", "ifndef"):
            arg = d[len(kw):].strip()
            v = _macro_value(arg, defs) if kw == "if" else ((arg in defs) == (kw == "ifdef"))
            if v is None:
                notes.append(f"macro condition '@#{d}' could not be evaluated; its first branch was counted")
                v = True
            stack.append((bool(v), bool(v)))
        elif kw == "else" and stack:
            _, taken = stack.pop()
            stack.append((not taken, True))
        elif kw == "endif" and stack:
            stack.pop()
        elif kw in ("for", "include", "includepath") and not any(f"@#{kw} " in n for n in notes):
            notes.append(f"@#{kw} is not expanded, so the counts may be incomplete: check them against the model")
    return "\n".join(out)


# blocks that close with `end;` and may repeat names without declaring them (for example `var e_y;` in shocks)
_MOD_BLOCKS = ("shocks", "mshocks", "heteroskedastic_shocks", "conditional_forecast_paths", "initval", "endval", "histval",
               "steady_state_model", "model", "estimated_params", "estimated_params_init", "estimated_params_bounds",
               "estimated_params_remove", "observation_trends", "deterministic_trends", "optim_weights", "osr_params_bounds",
               "ramsey_constraints", "occbin_constraints", "model_replace", "model_remove", "matched_moments",
               "filter_initial_state", "irf_calibration", "moment_calibration", "generate_irfs", "svar_identification",
               "planner_objective", "pac_target_info", "verbatim", "epilogue", "perfect_foresight_controlled_paths")


def _block(t, name):
    m = re.search(rf"(?ms)^\s*{name}\b(?:\([^)]*\))?\s*;(.*?)^\s*end\s*;", t)
    return m.group(1) if m else None


def _names(stmt):
    stmt = re.sub(r"\$[^$]*\$", " ", stmt)        # TeX names
    stmt = re.sub(r"\([^()]*\)", " ", stmt)        # options and long names
    return [t for t in re.split(r"[\s,]+", stmt) if re.match(r"^[A-Za-z_]\w*$", t)]


def elements_from_mod(text, notes=None):
    """Count the elements of a Dynare .mod file. Parameters in estimated_params are 'estimated', the rest 'calibrated';
    the file cannot tell which calibrated values lack a source, so 'assumed' is left for the modeler to set.
    Findings about the count itself (macros that were not expanded) are appended to `notes` when a list is given."""
    notes = [] if notes is None else notes
    t = _macro(_strip_mod(text), notes)
    top = re.sub(rf"(?ms)^\s*(?:{'|'.join(_MOD_BLOCKS)})\b(?:\([^)]*\))?\s*;.*?^\s*end\s*;", " ", t)  # declarations only
    decl = lambda kw: list(dict.fromkeys(n for s in re.findall(rf"(?m)^\s*{kw}\b(?:\([^)]*\))?([^;]*);", top)
                                         for n in _names(s)))
    endo, exo, exo_det, params = decl("var"), decl("varexo"), decl("varexo_det"), decl("parameters")
    obs = decl("varobs")
    model = _block(t, "model")
    eqs = 0
    if model is not None:
        body = re.sub(r"\[[^\]]*\]", " ", model)  # equation tags
        eqs = sum(1 for s in body.split(";") if s.strip() and not s.strip().startswith("#"))
    est = _block(t, "estimated_params")
    est_names = set()
    if est:
        for line in est.split(";"):
            head = line.strip().split(",")[0].strip()
            if head and not head.startswith(("stderr", "corr")):
                est_names.add(head)
    n_est = len([p for p in params if p in est_names])
    occ = _block(t, "occbin_constraints")
    n_con = len(re.findall(r"\bname\s+'", occ)) if occ else 0
    el = {"variables": {"endogenous": len(endo), "exogenous": len(exo_det)}, "equations": eqs,
          "parameters": {"estimated": n_est, "calibrated": len(params) - n_est, "assumed": 0}, "shocks": len(exo)}
    if obs:
        el["data"] = {"series": len(obs)}
    if n_con:
        el["constraints"] = {"verified": 0, "unverified": n_con}
    return el


def stacks(m):
    """Arrange the attached bricks (except the baseplate) into towers standing on the baseplate.

    A brick that reads no other brick stands on the plate. Any other brick goes on top of the tower that supplies
    its inputs, preferring the tower whose top brick it reads most (then the taller supplier), so towers can be any height (for example
    world prices -> oil sector -> fiscal rule). Which bricks a brick may stand on is set by `supports`: never on a
    higher layer, and never on a brick it shares a loop with. A brick may name its host with "on": "<id>".
    Returns a list of towers, each a list of bricks from the bottom up.
    """
    att = [b for b in attached(m) if b.get("kind") != "baseplate"]
    sup, dep = supports(att), depths(att)
    towers = []
    for b in sorted(att, key=lambda b: (dep[b["id"]], layer_of(b), b["id"])):
        need = {q["port"] for q in reqs(b)}
        below = lambda x: x["id"] in sup[b["id"]]
        best, best_key = None, None
        for t in towers:
            if dep[t[-1]["id"]] >= dep[b["id"]] or layer_of(t[-1]) > layer_of(b):
                continue
            if b.get("on"):
                key = (int(any(x["id"] == b["on"] for x in t)),)
            else:
                key = (len(need & set(provs(t[-1]))) if below(t[-1]) else 0,
                       len(need & {p for x in t if below(x) for p in provs(x)}), dep[t[-1]["id"]], -len(t))
            if key[0] > 0 or (len(key) > 1 and key[1] > 0):
                if best_key is None or key > best_key:
                    best, best_key = t, key
        if best is not None:
            best.append(b)
        else:
            towers.append([b])
    return towers


# ------------------------------------------------------------------ layouts (where bricks stand in the picture)
BRICK_L, BRICK_S = 6, 3   # brick footprint in studs (long and short side)


def footprint(place):
    """(x, y, w, d) of a placed brick; rot 90 turns the long side along y."""
    w, d = (BRICK_S, BRICK_L) if place.get("rot") == 90 else (BRICK_L, BRICK_S)
    return place["x"], place["y"], w, d


def _overlap(a, b):
    ax, ay, aw, ad = a
    bx, by, bw, bd = b
    return min(ax + aw, bx + bw) > max(ax, bx) and min(ay + ad, by + bd) > max(ay, by)


def pyramid_plan(m, origin=2):
    """Build the bricks into a stepped pyramid (a terraced temple) on the baseplate. Each step is one level higher,
    narrower by half a brick on both sides and set back by two studs, so it rests on the step below while the front
    face (and label) of every brick stays in view. A brick is laid above the bricks it stands on (see `supports`):
    the bricks whose outputs it reads, on its own layer or a lower one. There is no height limit: above the top step
    the pyramid continues as a stair of single bricks as high as the model needs. Returns {brick id: place}."""
    att = [b for b in attached(m) if b.get("kind") != "baseplate"]
    sup, dep = supports(att), depths(att)
    # each step is as wide as the bricks that belong on it; a step never outgrows the one below, so the surplus
    # moves up a step (still above everything it stands on)
    widths, carry = [], 0
    for d in range(1, max(dep.values(), default=1) + 1):
        avail = sum(1 for v in dep.values() if v == d) + carry
        w = avail if not widths else min(avail, widths[-1])
        widths.append(w)
        carry = avail - w
    while carry:
        widths.append(min(carry, widths[-1]))
        carry -= widths[-1]
    widths = [w for w in widths if w] or [1]
    k = widths[0]
    rows = []  # per step: list of (x, y)
    y_base = origin + 2 * (len(widths) - 1)
    for t, w in enumerate(widths):
        rows.append([(origin + BRICK_S * (k - w) + BRICK_L * i, y_base - 2 * t) for i in range(w)])

    def slots(c):
        while len(rows) < c:  # above the top step: a stair of single bricks, as high as needed
            x, y = rows[-1][len(rows[-1]) // 2]
            rows.append([(x, y - 2)])
        return [dict(x=x, y=y, rot=0, level=c) for x, y in rows[c - 1]]

    occupied, level_of, plan = {}, {}, {}
    order = sorted(att, key=lambda b: (dep[b["id"]], layer_of(b), -sum(1 for o in att if {q["port"] for q in reqs(o)} & set(provs(b))), b["id"]))
    for b in order:
        need = {q["port"] for q in reqs(b)}
        hosts = [o for o in att if o["id"] in level_of and o["id"] in sup[b["id"]]]
        c = max((level_of[o["id"]] for o in hosts), default=0) + 1
        best, relaxed = None, False
        while best is None:
            if c > 1 and not occupied.get(c - 1):  # nothing to rest on at this height
                if relaxed:
                    break  # no supported place anywhere: the brick goes in the yard
                c, relaxed = 1, True  # take the lowest free supported place instead
            below = occupied.get(c - 1, [])
            taken = [footprint(p) for p, _ in occupied.get(c, [])]
            cands = []
            for j, slot in enumerate(slots(c)):
                fp = footprint(slot)
                if any(_overlap(fp, x) for x in taken):
                    continue
                under = [o for p, o in below if _overlap(fp, footprint(p))]
                if c > 1 and not under:
                    continue  # nothing to rest on yet
                centre = abs(j - (len(rows[c - 1]) - 1) / 2)
                cands.append(((sum(bool(need & set(provs(o))) for o in under), len(under), -centre), slot))
            if cands:
                best = max(cands, key=lambda t: t[0])[1]
            else:
                c += 1
        if best is None:
            continue
        plan[b["id"]] = best
        level_of[b["id"]] = best["level"]
        occupied.setdefault(best["level"], []).append((best, b))
    return plan


def resolve_spec(ref, cat):
    if ref in cat:
        return copy.deepcopy(cat[ref])
    if os.path.isfile(ref):
        return read_json(ref)
    raise SystemExit(f"brick '{ref}' not found in the catalog or as a file (see: lego.py catalog)")


def new_brick(spec):
    b = {k: v for k, v in spec.items() if k not in ("checks", "identities")}
    b["checks"] = spec.get("checks", [])
    b.setdefault("freq", None)
    b["status"] = "attached"
    b["validation"] = "unvalidated"
    b.setdefault("code", None)
    return b


INTERFACE = ("kind", "freq", "slot", "bridge", "provides", "requires")


def _merge_identities(m, spec):
    """Accounting identities a brick brings (e.g. debt dynamics) are added to the manifest, owned by that brick."""
    have = {i["name"] for i in m.setdefault("identities", [])}
    for idn in spec.get("identities", []):
        if idn["name"] not in have:
            m["identities"].append({"name": idn["name"], "ports": list(idn["ports"]), "brick": spec["id"]})


# ------------------------------------------------------------------ analysis
def _tarjan(nodes, edges):
    index, low, onstack, stack, out = {}, {}, set(), [], []
    counter = [0]

    def strong(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        onstack.add(v)
        for w in sorted(edges.get(v, [])):
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in onstack:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                onstack.discard(w)
                comp.append(w)
                if w == v:
                    break
            out.append(sorted(comp))

    for v in sorted(nodes):
        if v not in index:
            strong(v)
    return out


def check(m):
    r = {"errors": [], "warnings": [], "info": [], "joints": [], "stubs": [], "sim_blocks": [], "order": [],
         "identities": [], "unused": [], "validation": {}}
    E, W, I = r["errors"], r["warnings"], r["info"]
    ports = m.get("ports", {})
    bricks = m.get("bricks", [])
    ids = [b.get("id") for b in bricks]
    for i in sorted({x for x in ids if ids.count(x) > 1}):
        E.append(f"duplicate brick id '{i}'")
    for b in bricks:
        bid = b.get("id", "?")
        if b.get("kind") not in KINDS:
            E.append(f"{bid}: unknown kind '{b.get('kind')}'")
        if b.get("status", "attached") not in STATUS:
            E.append(f"{bid}: status must be one of {STATUS}")
        if b.get("validation", "unvalidated") not in VALIDATION:
            E.append(f"{bid}: validation must be one of {VALIDATION}")
        for p in provs(b) + [q["port"] for q in reqs(b)]:
            if p not in ports:
                E.append(f"{bid}: port '{p}' is not defined in the manifest's port list")
    att = attached(m)
    bp = [b["id"] for b in att if b.get("kind") == "baseplate"]
    if len(bp) != 1:
        E.append(f"a model needs exactly one attached baseplate; found {len(bp)}")

    providers = {}
    for b in att:
        for p in provs(b):
            providers.setdefault(p, []).append(b["id"])
    for p, v in sorted(providers.items()):
        if len(v) > 1:
            E.append(f"port '{p}' is provided by several bricks: {', '.join(v)} (use /lego-swap to replace one)")

    slots = {}
    for b in att:
        if b.get("slot"):
            slots.setdefault(b["slot"], []).append(b["id"])
    for s, v in sorted(slots.items()):
        if len(v) > 1:
            E.append(f"slot '{s}' is filled by several bricks: {', '.join(v)}")
    for s in m.get("required_slots", []):
        if s not in slots:
            E.append(f"required slot '{s}' is empty")

    consumed = set()
    for b in att:
        for q in reqs(b):
            others = [x for x in providers.get(q["port"], []) if x != b["id"]]
            if others:
                r["joints"].append({"from": others[0], "port": q["port"], "to": b["id"], "lag": q["lag"]})
                consumed.add(q["port"])
            elif q["port"] in providers:
                continue
            elif q["stub"]:
                r["stubs"].append({"consumer": b["id"], "port": q["port"], "stub": q["stub"]})
            else:
                E.append(f"OPEN stud: '{b['id']}' requires '{q['port']}' and no attached brick provides it (no stub declared)")
    for p, v in sorted(providers.items()):
        if p not in consumed:
            r["unused"].append({"port": p, "brick": v[0]})

    mf = m.get("freq")
    for b in att:
        bf = b.get("freq") or mf
        if bf != mf:
            if b.get("bridge"):
                I.append(f"{b['id']}: frequency {bf} vs model {mf}, bridged by: {b['bridge']}")
            else:
                W.append(f"{b['id']}: frequency {bf} differs from the model's {mf} and no bridge is declared "
                         f"(temporal aggregation or disaggregation, and which direction feeds which)")

    stub_ports = {s["port"] for s in r["stubs"]}
    att_ids = {b["id"] for b in att}
    for idn in m.get("identities", []):
        if idn.get("brick") and idn["brick"] not in att_ids:
            continue  # brought by a brick that is now in the parts bin
        missing = [p for p in idn.get("ports", []) if p not in providers and p not in stub_ports]
        via = [p for p in idn.get("ports", []) if p not in providers and p in stub_ports]
        if missing:
            status = "BROKEN"
            E.append(f"identity '{idn['name']}' cannot be verified: nothing provides or stubs {', '.join(missing)}")
        elif via:
            status = "satisfied via stub (exogenous: " + ", ".join(via) + ")"
        else:
            status = "satisfied"
        r["identities"].append({"name": idn["name"], "status": status})

    edges = {b["id"]: set() for b in att}
    for j in r["joints"]:
        if j["lag"] == 0 and j["from"] != j["to"]:
            edges[j["from"]].add(j["to"])
    comps = _tarjan(set(edges), edges)
    r["sim_blocks"] = [c for c in comps if len(c) > 1]
    r["order"] = list(reversed(comps))

    # positions in the picture (hand-edited or from `arrange`): only warnings, they never affect the model
    placed = []
    for b in att:
        p = b.get("place")
        if not p or b.get("kind") == "baseplate":
            continue
        if not all(isinstance(p.get(k), int) for k in ("x", "y", "level")) or p["level"] < 1 or p.get("rot", 0) not in (0, 90):
            W.append(f"{b['id']}: place needs whole-number x, y and level (1 or more) and rot 0 or 90")
            continue
        placed.append((b["id"], p["level"], footprint(p)))
    for i, (a, la, fa) in enumerate(placed):
        for c, lc, fc in placed[i + 1:]:
            if la == lc and _overlap(fa, fc):
                W.append(f"picture: {a} and {c} occupy the same space on level {la}")
        if la > 1 and not any(lb == la - 1 and _overlap(fa, fb) for _, lb, fb in placed):
            W.append(f"picture: {a} on level {la} has nothing under it")

    # what each brick is made of: optional, so problems here are warnings and notes, never errors
    r["elements"] = {}
    for b in att:
        el, probs = elements_of(b)
        W += [f"{b['id']}: {p}" for p in probs]
        if el:
            r["elements"][b["id"]] = el
            for level, msg in element_flags(b, el):
                (W if level == "warn" else I).append(f"{b['id']}: {msg}")

    counts = {"validated": 0, "unvalidated": 0, "stale": 0}
    for b in att:
        counts[b.get("validation", "unvalidated")] = counts.get(b.get("validation", "unvalidated"), 0) + 1
    r["validation"] = counts
    return r


def neighbours(m, bid):
    rep = check(m)
    nb = set()
    for j in rep["joints"]:
        if j["from"] == bid:
            nb.add(j["to"])
        if j["to"] == bid:
            nb.add(j["from"])
    nb.discard(bid)
    return nb


def model_validation(m, rep):
    c = rep["validation"]
    if c.get("stale"):
        return "STALE (re-validate changed bricks and their joints)"
    if c.get("unvalidated"):
        return "UNVALIDATED parts present"
    return "all attached bricks validated"


# ------------------------------------------------------------------ change plans
def _stamp(m, action, brick, note=""):
    m["revision"] = int(m.get("revision", 0)) + 1
    m.setdefault("history", []).append({"date": datetime.date.today().isoformat(), "action": action, "brick": brick,
                                        "note": note})


def _merge_ports(m, spec_b, errs):
    registry = load_ports()
    for p in provs(spec_b) + [q["port"] for q in reqs(spec_b)]:
        if p in m["ports"]:
            continue
        if p in registry:
            m["ports"][p] = registry[p]
        else:
            errs.append(f"port '{p}' is not defined in lego/ports.json (define it with /lego-brick: name, unit, description)")


def _mark_stale(m, ids):
    for i in ids:
        b = find(m, i)
        if b and b.get("validation") == "validated":
            b["validation"] = "stale"


def _diff(before, after):
    key = lambda s: (s["consumer"], s["port"])
    bs, as_ = {key(s): s for s in before["stubs"]}, {key(s): s for s in after["stubs"]}
    jb = {(j["from"], j["port"], j["to"]) for j in before["joints"]}
    ja = {(j["from"], j["port"], j["to"]) for j in after["joints"]}
    return {
        "stubs_retired": [bs[k] for k in sorted(set(bs) - set(as_))],
        "stubs_activated": [as_[k] for k in sorted(set(as_) - set(bs))],
        "joints_added": sorted(ja - jb),
        "joints_removed": sorted(jb - ja),
        "new_errors": [e for e in after["errors"] if e not in before["errors"]],
        "new_warnings": [w for w in after["warnings"] if w not in before["warnings"]],
        "new_sim_blocks": [b for b in after["sim_blocks"] if b not in before["sim_blocks"]],
        "sim_blocks_changed": (before["sim_blocks"], after["sim_blocks"]) if before["sim_blocks"] != after["sim_blocks"] else None,
    }


def _refresh(m2, existing, spec, errs, notes):
    """A brick taken back from the parts bin follows its current definition if that has changed."""
    changed = [k for k in INTERFACE if existing.get(k) != spec.get(k) and not (k == "freq" and spec.get(k) is None)]
    if not changed:
        return
    for k in INTERFACE + ("summary", "name"):
        if k in spec:
            existing[k] = copy.deepcopy(spec[k])
    existing["checks"] = spec.get("checks", existing.get("checks", []))
    _merge_ports(m2, existing, errs)
    existing["validation"] = "unvalidated"
    notes.append(f"{spec['id']}: the parts-bin copy differs from the current definition ({', '.join(changed)}); "
                 "the current definition is used and the brick is marked unvalidated")


def plan_attach(m, spec, note=""):
    m2, before = copy.deepcopy(m), check(m)
    errs = []
    existing = find(m2, spec["id"])
    if existing is not None and existing.get("status") == "attached":
        raise SystemExit(f"'{spec['id']}' is already attached")
    notes = []
    if existing is not None:
        existing["status"] = "attached"
        if existing.get("validation") == "validated":
            existing["validation"] = "stale"
        _refresh(m2, existing, spec, errs, notes)
        action, changed = "reattach", existing
    else:
        changed = new_brick(spec)
        _merge_ports(m2, changed, errs)
        for p in provs(changed) + [q["port"] for q in reqs(changed)]:
            reg = load_ports().get(p)
            if p in m.get("ports", {}) and reg and m["ports"][p].get("unit") != reg.get("unit"):
                errs.append(f"port '{p}': manifest unit '{m['ports'][p].get('unit')}' differs from the registry unit '{reg.get('unit')}'")
        m2["bricks"].append(changed)
        action = "attach"
    _merge_identities(m2, spec)
    after = check(m2)
    d = _diff(before, after)
    nb = neighbours(m2, spec["id"])
    d["neighbours"] = sorted(nb)
    d["setup_errors"] = errs
    d["notes"] = notes
    _mark_stale(m2, nb)
    _stamp(m2, action, spec["id"], note)
    return m2, after, d


def plan_detach(m, bid, note=""):
    b = find(m, bid)
    if b is None or b.get("status", "attached") != "attached":
        raise SystemExit(f"'{bid}' is not an attached brick")
    if b.get("kind") == "baseplate":
        raise SystemExit("the baseplate cannot be detached; swap the core instead")
    before = check(m)
    nb = neighbours(m, bid)
    m2 = copy.deepcopy(m)
    find(m2, bid)["status"] = "detached"
    after = check(m2)
    d = _diff(before, after)
    d["neighbours"] = sorted(nb)
    d["setup_errors"] = []
    _mark_stale(m2, nb)
    _stamp(m2, "detach", bid, note)
    return m2, after, d


def plan_swap(m, old, spec, note=""):
    if find(m, old) is None or find(m, old).get("status") != "attached":
        raise SystemExit(f"'{old}' is not an attached brick")
    if spec["id"] == old:
        raise SystemExit(f"'{old}' cannot be swapped for itself")
    if find(m, spec["id"]) is not None and find(m, spec["id"]).get("status", "attached") == "attached":
        raise SystemExit(f"'{spec['id']}' is already attached; to remove '{old}', use detach")
    before = check(m)
    nb_old = neighbours(m, old)
    m1 = copy.deepcopy(m)
    find(m1, old)["status"] = "detached"
    errs, notes = [], []
    existing = find(m1, spec["id"])
    if existing is not None:
        existing["status"] = "attached"
        existing["validation"] = "stale" if existing.get("validation") == "validated" else existing.get("validation", "unvalidated")
        _refresh(m1, existing, spec, errs, notes)
        changed = existing
    else:
        changed = new_brick(spec)
        _merge_ports(m1, changed, errs)
        m1["bricks"].append(changed)
    _merge_identities(m1, spec)
    after = check(m1)
    d = _diff(before, after)
    d["neighbours"] = sorted(nb_old | neighbours(m1, spec["id"]))
    d["setup_errors"] = errs
    d["notes"] = notes
    d["lost_ports"] = sorted(set(provs(find(m, old))) - set(provs(changed)))
    d["gained_ports"] = sorted(set(provs(changed)) - set(provs(find(m, old))))
    _mark_stale(m1, d["neighbours"])
    _stamp(m1, "swap", f"{old} -> {spec['id']}", note)
    return m1, after, d


# ------------------------------------------------------------------ text output
def _box_rows(labels, width=100):
    """Draw labels as boxes, wrapping to the width; returns list of text lines."""
    lines, row, rw = [], [], 0
    for lab in labels:
        w = len(lab) + 4
        if row and rw + w + 1 > width:
            lines += _emit(row)
            row, rw = [], 0
        row.append(lab)
        rw += w + 1
    if row:
        lines += _emit(row)
    return lines


def _emit(row):
    top = " ".join("+" + "-" * (len(x) + 2) + "+" for x in row)
    mid = " ".join("| " + x + " |" for x in row)
    return [top, mid, top]


def suggestions(m, rep, cat):
    """Bricks that would fill open studs: from the parts bin first, then from the catalog."""
    stubbed = {s["port"] for s in rep["stubs"]}
    have = {b["id"]: b for b in m.get("bricks", [])}
    out = []
    for b in m.get("bricks", []):
        if b.get("status") == "detached":
            fills = sorted(set(provs(b)) & stubbed)
            if fills:
                out.append((b["id"], fills))
    for cid, c in sorted(cat.items()):
        if cid in have:
            continue
        fills = sorted(set(provs(c)) & stubbed)
        if fills:
            out.append((cid, fills))
    return out


def render_text(m, rep, cat):
    att = attached(m)
    det = [b for b in m.get("bricks", []) if b.get("status") == "detached"]
    o = []
    o.append(f"LEGO SET: {m.get('name', '?')}   (class {m.get('class', '?')}, frequency {m.get('freq', '?')}, revision {m.get('revision', 0)})")
    o.append(f"Bricks attached: {len(att)}   detached: {len(det)}   validation: {model_validation(m, rep)}")
    if m.get("layout"):
        o.append(f"Picture layout: {m['layout']} (positions set with `lego.py arrange`; edit a brick's \"place\" to move it)")
    o.append("Legend: [v] validated   [ ] unvalidated   [~] stale (changed since validation)")
    o.append("")
    layers = {}
    for b in att:
        if b.get("kind") != "baseplate":
            layers.setdefault(layer_of(b), []).append(b)
    for ly in sorted(layers, reverse=True):
        labels = [f"{b['id']} {MARK.get(b.get('validation', 'unvalidated'))}" for b in layers[ly]]
        rows = _box_rows(labels)
        o.append(f"LAYER {ly}  " + rows[0])
        o += ["         " + x for x in rows[1:]]
    for b in att:
        if b.get("kind") == "baseplate":
            lab = f"BASEPLATE: {b['id']} {MARK.get(b.get('validation', 'unvalidated'))}"
            bar = "+" + "=" * (max(len(lab) + 2, 60)) + "+"
            o.append("BASE     " + bar)
            o.append("         | " + lab.ljust(max(len(lab) + 1, 59)) + "|")
            o.append("         " + bar)
    tall = [t for t in stacks(m) if len(t) > 1]
    if tall:
        o.append("")
        o.append("STACKS (bottom -> top; a brick sits on the bricks whose outputs it reads):")
        for t in tall:
            o.append("  " + "  >  ".join(f"{b['id']} {MARK.get(b.get('validation', 'unvalidated'))}" for b in t))
    o.append("")
    if rep.get("elements"):
        o.append("INSIDE THE BRICKS (x variables, = equations, θ parameters, ε shocks, D data series, ≤ constraints):")
        for b in att:
            if b["id"] in rep["elements"]:
                o.append(f"  {b['id']:<26} {elements_line(rep['elements'][b['id']])}")
        missing = [b["id"] for b in att if b["id"] not in rep["elements"]]
        if missing:
            o.append("  not declared yet: " + ", ".join(missing) + "  (lego.py elements <manifest> <brick> --from-mod FILE)")
        o.append("")
    if rep["stubs"]:
        o.append("OPEN STUDS (inputs using a stub; attach a brick to fill them):")
        for s in rep["stubs"]:
            o.append(f"  - {s['port']:<22} used by {s['consumer']:<22} stub: {s['stub']}")
        sg = suggestions(m, rep, cat)
        if sg:
            binned = {b["id"] for b in m.get("bricks", []) if b.get("status") == "detached"}
            o.append("  Bricks that would fill these (parts bin first, then catalog):")
            for cid, fills in sg:
                o.append(f"    + {cid}  (fills: {', '.join(fills)}){'  [in parts bin]' if cid in binned else ''}")
        o.append("")
    if det:
        o.append("PARTS BIN (detached, kept in the manifest; reattach with `attach`):")
        for b in det:
            o.append(f"  - {b['id']}  ({b.get('kind')})  provides: {', '.join(provs(b)) or '-'}")
        o.append("")
    o.append("JOINTS (provider --port--> consumer; lag = uses previous period):")
    for j in rep["joints"]:
        tag = f"  lag {j['lag']}" if j["lag"] else ""
        o.append(f"  {j['from']} --{j['port']}--> {j['to']}{tag}")
    if not rep["joints"]:
        o.append("  (none)")
    o.append("")
    if rep["sim_blocks"]:
        o.append("SIMULTANEOUS BLOCKS (bricks that depend on each other in the same period; solved jointly):")
        for b in rep["sim_blocks"]:
            o.append("  - " + ", ".join(b))
    else:
        o.append("SIMULTANEOUS BLOCKS: none (bricks can be solved one after another)")
    o.append("SOLVE ORDER: " + "  ->  ".join("{" + ", ".join(c) + "}" if len(c) > 1 else c[0] for c in rep["order"]))
    if rep["identities"]:
        o.append("")
        o.append("IDENTITIES:")
        for i in rep["identities"]:
            o.append(f"  - {i['name']}: {i['status']}")
    o.append("")
    for tag, items in (("ERRORS", rep["errors"]), ("WARNINGS", rep["warnings"]), ("NOTES", rep["info"])):
        if items:
            o.append(f"{tag}:")
            o += [f"  - {x}" for x in items]
    if not rep["errors"]:
        o.append("RESULT: OK (no errors)")
    else:
        o.append(f"RESULT: {len(rep['errors'])} error(s)")
    return "\n".join(o)


def render_plan(title, m_before, rep_after, d):
    o = [f"PLAN: {title}"]
    if d.get("setup_errors"):
        o += ["Problems with the brick itself:"] + [f"  - {e}" for e in d["setup_errors"]]
    if d.get("notes"):
        o += ["Notes:"] + [f"  - {e}" for e in d["notes"]]
    if d.get("lost_ports"):
        o.append("Ports lost (provided by the old brick, not by the new): " + ", ".join(d["lost_ports"]))
    if d.get("gained_ports"):
        o.append("Ports gained: " + ", ".join(d["gained_ports"]))
    if d["joints_added"]:
        o.append("New joints:")
        o += [f"  + {a} --{p}--> {c}" for a, p, c in d["joints_added"]]
    if d["joints_removed"]:
        o.append("Joints removed:")
        o += [f"  - {a} --{p}--> {c}" for a, p, c in d["joints_removed"]]
    if d["stubs_retired"]:
        o.append("Stubs retired (these inputs become endogenous):")
        o += [f"  + {s['consumer']}.{s['port']}  (was: {s['stub']})" for s in d["stubs_retired"]]
    if d["stubs_activated"]:
        o.append("Stubs activated (these inputs become exogenous):")
        o += [f"  ! {s['consumer']}.{s['port']}  -> {s['stub']}" for s in d["stubs_activated"]]
    if d.get("sim_blocks_changed"):
        fmt = lambda bl: "; ".join("{" + ", ".join(b) + "}" for b in bl) or "none"
        before, after = d["sim_blocks_changed"]
        o.append(f"Simultaneous blocks (solved jointly) change: {fmt(before)}  ->  {fmt(after)}")
    if d["new_warnings"]:
        o += ["New warnings:"] + [f"  - {w}" for w in d["new_warnings"]]
    if d["new_errors"]:
        o += ["New ERRORS:"] + [f"  - {e}" for e in d["new_errors"]]
    if d["neighbours"]:
        o.append("Neighbouring bricks to re-validate (marked stale if they were validated): " + ", ".join(d["neighbours"]))
    other = [e for e in rep_after["errors"] if e not in d["new_errors"]]
    if other:
        o += ["Existing errors still present:"] + [f"  - {e}" for e in other]
    return "\n".join(o)


def render_mermaid(m, rep):
    o = ["```mermaid", "flowchart BT"]
    for b in m.get("bricks", []):
        shape = f'{b["id"]}["{b["id"]}<br/>{b.get("kind")}"]'
        o.append("  " + shape + (":::detached" if b.get("status") == "detached" else ""))
    for j in rep["joints"]:
        o.append(f'  {j["from"]} -->|"{j["port"]}{" (lag)" if j["lag"] else ""}"| {j["to"]}')
    for i, s in enumerate(rep["stubs"]):
        o.append(f'  stub{i}(("stub: {s["port"]}")) -.-> {s["consumer"]}')
    o.append("  classDef detached stroke-dasharray: 5 5,fill:#eee,color:#777;")
    o.append("```")
    return "\n".join(o)


# ------------------------------------------------------------------ html output
def render_html(m, rep, cat):
    """Isometric 3D picture (self-contained HTML with inline SVG); see tools/lego_view.py."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import lego_view
    helpers = {"attached": attached, "provs": provs, "reqs": reqs, "layer_of": layer_of, "stacks": stacks, "footprint": footprint,
               "suggestions": suggestions, "model_validation": model_validation, "elements_of": elements_of,
               "elements_line": elements_line, "element_flags": element_flags}
    return lego_view.render(m, rep, cat, helpers)


# ------------------------------------------------------------------ commands
def load_manifest(path):
    if not os.path.isfile(path):
        raise SystemExit(f"manifest not found: {path}")
    return read_json(path)


def cmd_catalog(a):
    cat = load_catalog()
    for cid, b in cat.items():
        if a.kind and b.get("kind") != a.kind:
            continue
        print(f"{cid:<28} {b.get('kind'):<11} {b.get('freq') or '-':<2} provides: {', '.join(provs(b)) or '-'}")
        print(f"{'':<28} requires: {', '.join(q['port'] + ('*' if q['stub'] else '') for q in reqs(b)) or '-'}")
    print("\n(* = has a stub, i.e. optional)")


def cmd_new(a):
    cat, registry = load_catalog(), load_ports()
    if os.path.exists(a.manifest) and not a.force:
        raise SystemExit(f"{a.manifest} exists (use --force to overwrite)")
    m = {"lego_version": 1, "name": a.name, "class": a.cls, "freq": a.freq, "revision": 1, "ports": {},
         "required_slots": [], "identities": [], "bricks": [], "history": []}
    for ref in a.bricks:
        spec = resolve_spec(ref, cat)
        b = new_brick(spec)
        errs = []
        _merge_ports(m, b, errs)
        if errs:
            raise SystemExit("; ".join(errs))
        m["bricks"].append(b)
        _merge_identities(m, spec)
    _stamp(m, "create", ",".join(a.bricks))
    m["revision"] = 1
    rep = check(m)
    if rep["errors"]:
        print(render_text(m, rep, cat))
        raise SystemExit(f"{a.manifest} not written: fix the {len(rep['errors'])} error(s) above "
                         "(add a baseplate or the missing bricks, or create one with /lego-brick)")
    write_json(a.manifest, m)
    print(f"created {a.manifest}: {len(m['bricks'])} brick(s)")
    print(render_text(m, rep, cat))


def cmd_show(a):
    m = load_manifest(a.manifest)
    cat = load_catalog()
    rep = check(m)
    print(render_text(m, rep, cat))
    if a.mermaid:
        print()
        print(render_mermaid(m, rep))
    if a.html:
        with open(a.html, "w", encoding="utf-8", newline="\n") as f:
            f.write(render_html(m, rep, cat))
        print(f"\nwrote {a.html}")


def cmd_check(a):
    m = load_manifest(a.manifest)
    rep = check(m)
    print(render_text(m, rep, load_catalog()))
    sys.exit(1 if rep["errors"] else 0)


def _finish(a, title, m2, rep, d):
    print(render_plan(title, None, rep, d))
    blocked = bool(d["new_errors"] or d["setup_errors"] or rep["errors"])
    if not a.apply:
        if blocked:
            print("\nThis change would be BLOCKED by the errors above (nothing written). --force overrides.")
        else:
            print("\n(dry run: nothing written. Re-run with --apply to make the change.)")
        sys.exit(1 if blocked else 0)
    if blocked and not a.force:
        print("\nNOT applied: errors above. Fix them, or use --force to apply anyway.")
        sys.exit(1)
    write_json(a.manifest, m2)
    print(f"\napplied: {a.manifest} is now revision {m2['revision']}")


def cmd_attach(a):
    m = load_manifest(a.manifest)
    spec = resolve_spec(a.brick, load_catalog())
    m2, rep, d = plan_attach(m, spec, a.note or "")
    _finish(a, f"attach {spec['id']}", m2, rep, d)


def cmd_detach(a):
    m = load_manifest(a.manifest)
    m2, rep, d = plan_detach(m, a.brick, a.note or "")
    _finish(a, f"detach {a.brick}", m2, rep, d)


def cmd_arrange(a):
    """Set where bricks stand in the picture. 'pyramid' builds a stepped pyramid; 'grid' clears positions.
    Positions are only for the picture: they never change the wiring. Edit a brick's "place" to move it."""
    m = load_manifest(a.manifest)
    m2 = copy.deepcopy(m)
    for b in m2.get("bricks", []):
        b.pop("place", None)
    if a.style == "grid":
        m2.pop("layout", None)
        print("PLAN: arrange as grid (bricks stand side by side; towers where a brick reads the one below)")
    else:
        plan = pyramid_plan(m2)
        m2["layout"] = "pyramid"
        print("PLAN: arrange as a stepped pyramid (each step one level up, narrower and set back, resting on the step below)")
        for b in attached(m2):
            if b["id"] in plan:
                b["place"] = plan[b["id"]]
                p = plan[b["id"]]
                print(f"  {b['id']:<28} level {p['level']}  x {p['x']:>2}  y {p['y']:>2}  {'along y' if p['rot'] == 90 else 'along x'}")
        rest = [b["id"] for b in attached(m2) if b.get("kind") != "baseplate" and b["id"] not in plan]
        if rest:
            print("  in the yard (nothing to rest on): " + ", ".join(rest))
    _stamp(m2, "arrange", a.style, a.note or "")
    if not a.apply:
        print("\n(dry run: nothing written. Re-run with --apply to make the change.)")
        return
    write_json(a.manifest, m2)
    print(f"\napplied: {a.manifest} is now revision {m2['revision']}")


def cmd_validate(a):
    """Record the outcome of an independent validation for one attached brick, with the report as evidence."""
    m = load_manifest(a.manifest)
    b = find(m, a.brick)
    if b is None or b.get("status", "attached") != "attached":
        raise SystemExit(f"'{a.brick}' is not an attached brick")
    if a.status == "validated":
        if not a.report:
            raise SystemExit("--report <path to the validation report> is required to mark a brick validated")
        if not os.path.isfile(a.report):
            raise SystemExit(f"validation report not found: {a.report}")
    m2 = copy.deepcopy(m)
    b2 = find(m2, a.brick)
    old = b2.get("validation", "unvalidated")
    b2["validation"] = a.status
    if a.status == "validated":
        b2["validation_report"] = a.report.replace("\\", "/")
        b2["validated_on"] = datetime.date.today().isoformat()
    else:
        b2.pop("validated_on", None)
    _stamp(m2, "validate", a.brick, a.note or f"{old} -> {a.status}" + (f" ({a.report})" if a.report else ""))
    print(f"PLAN: mark {a.brick} {a.status} (was {old})" + (f"; evidence: {a.report}" if a.report else ""))
    if not a.apply:
        print("\n(dry run: nothing written. Re-run with --apply to make the change.)")
        return
    write_json(a.manifest, m2)
    print(f"\napplied: {a.manifest} is now revision {m2['revision']}")


def _set_element(el, spec):
    key, _, val = spec.partition("=")
    name, _, field = key.strip().partition(".")
    if name not in ELEMENTS or not val:
        raise SystemExit(f"--set {spec}: use ELEMENT=N or ELEMENT.FIELD=N with ELEMENT one of {', '.join(ELEMENTS)}")
    if field in ELEMENT_TEXT:
        cur = el.get(name)
        el[name] = dict(cur) if isinstance(cur, dict) else ({"series": cur} if name == "data" and isinstance(cur, int) else {})
        el[name][field] = val
        return
    if not val.isdigit():
        raise SystemExit(f"--set {spec}: the value must be a whole number")
    if not field:
        el[name] = int(val)
        return
    if field not in ELEMENTS[name]:
        raise SystemExit(f"--set {spec}: '{name}' has the fields {', '.join(ELEMENTS[name] + ELEMENT_TEXT)}")
    cur = el.get(name)
    el[name] = dict(cur) if isinstance(cur, dict) else {}
    el[name][field] = int(val)


def cmd_elements(a):
    """Declare what a brick is made of: counted from a Dynare .mod file, set by hand, or both (--set after --from-mod)."""
    m = load_manifest(a.manifest)
    b = find(m, a.brick)
    if b is None:
        raise SystemExit(f"'{a.brick}' is not a brick in {a.manifest}")
    m2 = copy.deepcopy(m)
    b2 = find(m2, a.brick)
    el = copy.deepcopy(b2.get("elements") or {})
    count_notes = []
    src = a.from_mod or (b.get("code") if not a.set and str(b.get("code") or "").endswith(".mod") else None)
    if src:
        if not os.path.isfile(src):
            raise SystemExit(f"model file not found: {src}")
        with open(src, encoding="utf-8", errors="replace") as f:
            counted = elements_from_mod(f.read(), count_notes)
        before = {k: (v if isinstance(v, dict) else {}) for k, v in el.items()}
        el.update(counted)
        # a recount keeps the modeler's judgments: assumed parameters, the data vintage, constraints already verified
        keep_assumed = before.get("parameters", {}).get("assumed", 0)
        if keep_assumed and keep_assumed <= counted["parameters"]["calibrated"]:
            el["parameters"]["calibrated"] -= keep_assumed
            el["parameters"]["assumed"] = keep_assumed
        for k, v in before.items():
            for field in ELEMENT_TEXT:
                if field in v and isinstance(el.get(k), dict):
                    el[k].setdefault(field, v[field])
        verified = before.get("constraints", {}).get("verified", 0)
        if verified and isinstance(el.get("constraints"), dict):
            total = el["constraints"].get("verified", 0) + el["constraints"].get("unverified", 0)
            el["constraints"]["verified"] = min(verified, total)
            el["constraints"]["unverified"] = total - el["constraints"]["verified"]
        b2["elements_source"] = src.replace("\\", "/")
    sizes = {k: sum(x for x in v.values() if isinstance(x, int)) for k, v in el.items() if isinstance(v, dict)}
    keys = {s.partition("=")[0].strip() for s in a.set or []}
    for s in a.set or []:
        _set_element(el, s)
    # assumed parameters are calibrated values without a source, and a verified constraint was unverified before:
    # marking them moves them between statuses and leaves the total unchanged (unless both sides are set explicitly)
    for name, moved, frm in (("parameters", "assumed", "calibrated"), ("constraints", "verified", "unverified")):
        if f"{name}.{moved}" in keys and f"{name}.{frm}" not in keys and sizes.get(name) and isinstance(el.get(name), dict):
            rest = sum(x for k, x in el[name].items() if isinstance(x, int) and k not in (moved, frm))
            el[name][frm] = max(0, sizes[name] - rest - el[name][moved])
    if not src and not a.set:
        cur, probs = elements_of(b)
        print(f"{a.brick}: {elements_line(cur) or 'no elements declared'}")
        for p in probs:
            print(f"  problem: {p}")
        print("\nSet them with --from-mod FILE (a Dynare model) and/or --set ELEMENT[.FIELD]=N, then --apply.")
        return
    b2["elements"] = el
    norm, probs = elements_of(b2)
    if probs:
        raise SystemExit("; ".join(probs))
    _stamp(m2, "elements", a.brick, a.note or (f"counted from {src}" if src else "set by hand"))
    print(f"PLAN: {a.brick} is made of: {elements_line(norm)}")
    for n_ in count_notes:
        print(f"  counting: {n_}")
    for level, msg in element_flags(b2, norm):
        print(f"  {'warning' if level == 'warn' else 'note'}: {msg}")
    if b.get("validation") == "validated" and b.get("elements") != el:
        print("  note: the brick is marked validated; if its code changed, re-validate it before release")
    if not a.apply:
        print("\n(dry run: nothing written. Re-run with --apply to make the change.)")
        return
    write_json(a.manifest, m2)
    print(f"\napplied: {a.manifest} is now revision {m2['revision']}")


def cmd_swap(a):
    m = load_manifest(a.manifest)
    spec = resolve_spec(a.new, load_catalog())
    m2, rep, d = plan_swap(m, a.old, spec, a.note or "")
    _finish(a, f"swap {a.old} -> {spec['id']}", m2, rep, d)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Lego view of an economic model")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("catalog"); p.add_argument("--kind"); p.set_defaults(fn=cmd_catalog)
    p = sub.add_parser("new"); p.add_argument("manifest"); p.add_argument("--name", required=True)
    p.add_argument("--freq", default="Q"); p.add_argument("--class", dest="cls", default="medium")
    p.add_argument("--bricks", nargs="+", required=True); p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_new)
    p = sub.add_parser("show"); p.add_argument("manifest"); p.add_argument("--html"); p.add_argument("--mermaid", action="store_true"); p.set_defaults(fn=cmd_show)
    p = sub.add_parser("check"); p.add_argument("manifest"); p.set_defaults(fn=cmd_check)
    for name, fn, extra in (("attach", cmd_attach, ["brick"]), ("detach", cmd_detach, ["brick"]), ("swap", cmd_swap, ["old", "new"])):
        p = sub.add_parser(name); p.add_argument("manifest")
        for x in extra:
            p.add_argument(x)
        p.add_argument("--apply", action="store_true"); p.add_argument("--force", action="store_true"); p.add_argument("--note")
        p.set_defaults(fn=fn)
    p = sub.add_parser("arrange", help="set where bricks stand in the picture: a stepped pyramid, or a grid")
    p.add_argument("manifest"); p.add_argument("--style", choices=("pyramid", "grid"), default="pyramid")
    p.add_argument("--apply", action="store_true"); p.add_argument("--note"); p.set_defaults(fn=cmd_arrange)
    p = sub.add_parser("validate", help="record a brick's validation status, with the report as evidence")
    p.add_argument("manifest"); p.add_argument("brick")
    p.add_argument("--status", choices=VALIDATION, default="validated"); p.add_argument("--report")
    p.add_argument("--apply", action="store_true"); p.add_argument("--note"); p.set_defaults(fn=cmd_validate)
    p = sub.add_parser("elements", help="declare what a brick is made of: variables, equations, parameters, shocks, data, constraints")
    p.add_argument("manifest"); p.add_argument("brick"); p.add_argument("--from-mod", help="count them from a Dynare .mod file")
    p.add_argument("--set", nargs="+", metavar="ELEMENT[.FIELD]=N", help="e.g. parameters.assumed=3 data.vintage=2026Q2")
    p.add_argument("--apply", action="store_true"); p.add_argument("--note"); p.set_defaults(fn=cmd_elements)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
