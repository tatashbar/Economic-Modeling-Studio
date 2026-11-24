#!/usr/bin/env python3
"""Studio protocol: one machine interface to the studio for AI agents and programs.

Humans use the commands (lego.py, bridge.py, known_answer.py, ...). Agents use this protocol: compact JSON
messages, numbered finding codes with ready-made fixes, state fingerprints for safe concurrent writes, and a
handshake (`hello`) that teaches an agent the whole protocol in one call. Every response can be turned back
into plain language with the `say` operation, so a person can read any part of an agent's work.

Message (one object, or a list of objects for a batch):
    {"op": "lego.check", "a": {"m": "lego/examples/small-open-economy.lego.json"}, "id": 7}
Response:
    {"id": 7, "ok": true, "r": {...}, "e": [[211, "fiscal-debt-rule", "output_gap"]], "w": [...], "h": "3fa2c1d09b7e"}

Transports (all carry the same messages):
    python tools/studio_api.py hello                      the handshake, printed
    python tools/studio_api.py call '<json message>'      one message (or a batch) from the command line
    python tools/studio_api.py serve                      JSON lines on stdin and stdout: one process, many messages
    python tools/mcp_server.py                            the same operations as MCP tools (see docs/agents.md)

Extensions: a Python file in extensions/ that defines register(api) can add operations, finding codes and
state sources. See docs/agents.md.
"""
import copy
import glob
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
import time
import traceback
from contextlib import redirect_stdout

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import bridge as bridgemod  # noqa: E402
import known_answer as kamod  # noqa: E402
import lego  # noqa: E402

PROTOCOL = "esp/1"


def _studio_version():
    try:
        with open(os.path.join(ROOT, "studio-config.yaml"), encoding="utf-8") as f:
            mt = re.search(r'version:\s*"([^"]+)"', f.read())
        return mt.group(1) if mt else "?"
    except OSError:
        return "?"


VERSION = _studio_version()
LIMITS = {"batch": 1000, "message_bytes": 8_000_000}


# ------------------------------------------------------------------ registry
class OpError(Exception):
    """A refused request: a code from CODES, a message for people and optional data and fixes for agents."""

    def __init__(self, code, msg, data=None, fix=None):
        super().__init__(msg)
        self.code, self.msg, self.data, self.fix = code, msg, data, fix


OPS = {}
SOURCES = {}          # key in "a" -> function(a) returning a Source
HOOKS = {"before": [], "after": []}   # before(op, a, ctx) may raise OpError; after(op, a, resp, ctx)

CODES = {
    # protocol (1xx)
    100: ("bad_message", "the message is not valid JSON or not an object with an 'op'"),
    101: ("unknown_op", "no operation with this name; call hello or ops for the list"),
    102: ("missing_arg", "a required argument is missing"),
    103: ("bad_arg", "an argument has the wrong type or value"),
    104: ("human_only", "this operation records a person's judgment and is not available to agents"),
    105: ("limit", "the request is over a limit given in hello"),
    106: ("not_found", "the manifest, brick, case or object does not exist"),
    107: ("internal", "the operation failed unexpectedly; the message has the details"),
    108: ("refused", "the studio refused the operation; the message says why"),
    # model wiring errors (2xx)
    201: ("duplicate_brick", "two bricks have the same id"),
    202: ("unknown_kind", "a brick has a kind the studio does not know"),
    203: ("bad_status", "a brick's status is not attached or detached"),
    204: ("bad_validation", "a brick's validation is not validated, unvalidated or stale"),
    205: ("undefined_port", "a brick uses a port that is not in the manifest's port list"),
    206: ("baseplate_count", "a model needs exactly one attached baseplate"),
    207: ("double_provider", "several bricks provide the same port"),
    208: ("slot_conflict", "several bricks fill the same slot"),
    209: ("slot_empty", "a required slot is empty"),
    210: ("open_stud", "a brick needs a port that nothing provides and it has no stub"),
    211: ("bridge_no_method", "a port crosses a frequency boundary without a declared conversion method"),
    212: ("bridge_bad_freq", "a bridge uses a frequency other than A, Q or M"),
    213: ("bridge_wrong_direction", "the declared method converts in the wrong direction"),
    214: ("bridge_test_failed", "the bridge failed its known-answer tests"),
    215: ("identity_broken", "an accounting identity cannot be verified"),
    216: ("registry_port", "a port is not defined in lego/ports.json"),
    217: ("unit_mismatch", "the manifest and the registry give a port different units"),
    218: ("blocked", "the change would add errors, so nothing was written (force overrides)"),
    219: ("conflict", "the state changed since the base fingerprint you gave; read it again and retry"),
    220: ("brick_state", "the brick is not in the state this operation needs"),
    299: ("model_error", "another wiring error; see the message"),
    # model warnings (3xx)
    301: ("bridge_missing", "a brick runs at another frequency and declares no bridge"),
    302: ("bridge_note_only", "the bridge is a text note, which cannot be tested"),
    303: ("measure_mismatch", "the method treats a port as a flow, stock or rate other than its declared measure"),
    304: ("bridge_untested", "the bridge has not been tested since it last changed"),
    305: ("signoff_unvalidated", "a brick is signed off but its numbers are not validated"),
    306: ("bad_place", "a brick's picture position is not valid"),
    307: ("overlap", "two bricks occupy the same space in the picture"),
    308: ("floating", "a brick stands on nothing in the picture"),
    309: ("not_square", "a brick has a different number of equations and endogenous variables"),
    310: ("unverified_constraint", "a validated brick has constraints not yet verified in a run"),
    399: ("model_warning", "another warning; see the message"),
    # validation and known answers (4xx)
    401: ("known_answer_failed", "a known-answer check failed"),
    402: ("untestable", "the brick cannot be validated before its bridge is testable"),
    403: ("bridge_not_passed", "the bridge has not passed its tests in its current form"),
    404: ("refused_input", "the data were refused before conversion (incomplete or duplicated periods)"),
}

# message pattern -> code, with named groups b (brick), s (subject), x and y (details)
PATTERNS = [
    (201, r"duplicate brick id '(?P<b>[^']+)'"),
    (202, r"(?P<b>[^\s:]+): unknown kind '(?P<s>[^']*)'"),
    (203, r"(?P<b>[^\s:]+): status must be"),
    (204, r"(?P<b>[^\s:]+): validation must be"),
    (205, r"(?P<b>[^\s:]+): port '(?P<s>[^']+)' is not defined in the manifest"),
    (206, r"exactly one attached baseplate; found (?P<s>\d+)"),
    (207, r"port '(?P<s>[^']+)' is provided by several bricks: (?P<b>[^(]+?) \("),
    (208, r"slot '(?P<s>[^']+)' is filled by several bricks: (?P<b>.+)"),
    (209, r"required slot '(?P<s>[^']+)' is empty"),
    (210, r"OPEN stud: '(?P<b>[^']+)' requires '(?P<s>[^']+)'"),
    (211, r"(?P<b>[^\s:]+): the bridge does not say how '(?P<s>[^']+)' converts from (?P<x>\w) to (?P<y>\w)"),
    (212, r"(?P<b>[^\s:]+): bridge for '(?P<s>[^']+)': frequencies must be"),
    (214, r"(?P<b>[^\s:]+): bridge known-answer tests FAILED"),
    (213, r"(?P<b>[^\s:]+): bridge for '(?P<s>[^']+)': "),
    (215, r"identity '(?P<s>[^']+)' cannot be verified"),
    (216, r"port '(?P<s>[^']+)' is not defined in lego/ports.json"),
    (217, r"port '(?P<s>[^']+)': manifest unit"),
    (301, r"(?P<b>[^\s:]+): frequency (?P<x>\w) differs from the model's (?P<y>\w) and no bridge"),
    (302, r"(?P<b>[^\s:]+): the bridge is only a note"),
    (303, r"(?P<b>[^\s:]+): bridge for '(?P<s>[^']+)' uses (?P<x>\w+), which treats .* declared (?:a |an )?(?P<y>flow|stock|rate)"),
    (304, r"(?P<b>[^\s:]+): bridge declared .* not tested"),
    (305, r"(?P<b>[^\s:]+): signed off by"),
    (306, r"(?P<b>[^\s:]+): place needs"),
    (307, r"picture: (?P<b>\S+) and (?P<s>\S+) occupy"),
    (308, r"picture: (?P<b>\S+) on level"),
    (309, r"(?P<b>[^\s:]+): (?P<x>\d+) equations for (?P<y>\d+) endogenous"),
    (310, r"(?P<b>[^\s:]+): (?P<x>\d+) constraint\(s\) not yet verified"),
]
_COMPILED = [(c, re.compile(p)) for c, p in PATTERNS]


def op(name, summary, args=None, mutates=False, human=False, group=None):
    """Register an operation. args: {name: "type[?] description"}; a '?' after the type marks it optional."""
    def deco(fn):
        OPS[name] = {"fn": fn, "summary": summary, "args": args or {}, "mutates": mutates, "human": human,
                     "group": group or name.split(".")[0]}
        return fn
    return deco


def code(n, slug, meaning):
    """Extensions add finding codes here (use 900-999; 5xx workspace, 6xx economy and 7xx loop are taken)."""
    if n in CODES and CODES[n][0] != slug:
        raise ValueError(f"code {n} is already used by {CODES[n][0]}")
    CODES[n] = (slug, meaning)


def source(key, fn):
    SOURCES[key] = fn


# ------------------------------------------------------------------ state
def fingerprint(doc):
    return hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:12]


class Source:
    """Where a model lives: inline in the message (d), a manifest file (m), or an extension's store (t)."""

    def __init__(self, doc, name, saver=None, inline=False):
        self.doc, self.name, self.saver, self.inline = doc, name, saver, inline
        self.h = fingerprint(doc)

    def save(self, doc, a):
        if self.saver is None:
            raise OpError(108, f"{self.name} cannot be written")
        return self.saver(doc, a)


def _path(p):
    if os.path.isabs(p) or os.path.exists(p):
        return p
    return os.path.join(ROOT, p)


_FILE_CACHE = {}


def _file_source(a):
    path = _path(a["m"])
    if not os.path.isfile(path):
        raise OpError(106, f"manifest not found: {a['m']}")
    st = os.stat(path)
    key = (path, st.st_mtime_ns, st.st_size)
    if key not in _FILE_CACHE:
        if len(_FILE_CACHE) > 256:
            _FILE_CACHE.clear()
        _FILE_CACHE[key] = lego.read_json(path)
    src = Source(copy.deepcopy(_FILE_CACHE[key]), a["m"])

    def save(doc, a2):
        # compare-and-swap on the file: re-read, check the fingerprint, write to a temp file, then rename
        cur = lego.read_json(path)
        if a2.get("base") and fingerprint(cur) != a2["base"]:
            raise OpError(219, f"{a['m']} changed since {a2['base']} (now {fingerprint(cur)})",
                          data={"h": fingerprint(cur)})
        tmp = f"{path}.{os.getpid()}.tmp"
        lego.write_json(tmp, doc)
        os.replace(tmp, path)
        return {"saved": a["m"]}
    src.saver = save
    return src


def _inline_source(a):
    if not isinstance(a["d"], dict):
        raise OpError(103, "d must be a manifest object")
    return Source(copy.deepcopy(a["d"]), "inline", inline=True)


source("m", _file_source)
source("d", _inline_source)


def resolve(a):
    for key, fn in SOURCES.items():
        if key in a:
            return fn(a)
    raise OpError(102, f"say where the model is: one of {', '.join(sorted(SOURCES))} "
                       "(m = manifest path, d = inline manifest)")


# ------------------------------------------------------------------ findings
def finding(msg, warning=False):
    """Turn one message from lego.check into [code, brick, subject, ...details]."""
    for c, rx in _COMPILED:
        mt = rx.search(msg)
        if mt:
            g = mt.groupdict()
            row = [c, (g.get("b") or "").strip()]
            for k in ("s", "x", "y"):
                if g.get(k):
                    row.append(g[k])
            return row
    return [399 if warning else 299, "", msg]


def _suggest_method(measure, src, dst):
    agg = bridgemod.direction(src, dst) == "aggregate"
    return {"flow": "sum" if agg else "split", "stock": "last" if agg else "interpolate",
            "average": "average" if agg else "repeat"}.get(measure or "average", "average" if agg else "repeat")


def fixes(doc, rep, codes_rows):
    """Ready-made operations that would fix a finding. An agent can send them back unchanged."""
    out = []
    ports = doc.get("ports", {})
    registry = None
    for row in codes_rows:
        c, b = row[0], row[1]
        if c == 211:
            port, src, dst = row[2], row[3], row[4]
            measure = (ports.get(port) or {}).get("measure")
            if not measure:
                registry = lego.load_ports() if registry is None else registry
                measure = (registry.get(port) or {}).get("measure")
            out.append({"op": "lego.bridge", "a": {"b": b, "p": port, "method": _suggest_method(measure, src, dst)}})
        elif c in (301, 302):
            out.append({"op": "lego.bridge", "a": {"b": b, "auto": True}})
        elif c == 303:
            port = row[2]
            e = next((x for x in rep.get("bridges", []) if x["brick"] == b and x["port"] == port), None)
            if e:
                measure = {"rate": "average"}.get(row[4] if len(row) > 4 else "", row[4] if len(row) > 4 else None)
                out.append({"op": "lego.bridge", "a": {"b": b, "p": port,
                                                      "method": _suggest_method(measure, e["from"], e["to"])}})
        elif c in (304, 214):
            out.append({"op": "lego.bridge_test", "a": {"apply": True}})
        elif c == 210:
            port = row[2]
            cands = [cid for cid, spec in lego.load_catalog().items() if port in lego.provs(spec)]
            if cands:
                out.append({"op": "lego.attach", "a": {"brick": cands[0]}})
                if len(cands) > 1:
                    out[-1]["alt"] = cands[1:4]
    seen, unique = set(), []
    for f in out:
        key = json.dumps(f, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def report(doc, full=False, rep=None):
    rep = rep if rep is not None else lego.check(doc)
    e = [finding(x) for x in rep["errors"]]
    w = [finding(x, True) for x in rep["warnings"]]
    if full:
        for row, msg in zip(e, rep["errors"]):
            row.append(msg) if row[0] != 299 else None
        for row, msg in zip(w, rep["warnings"]):
            row.append(msg) if row[0] != 399 else None
    return rep, e, w


# ------------------------------------------------------------------ dispatch
def _ok(r=None, **kw):
    out = {"ok": True, "r": r if r is not None else {}}
    out.update({k: v for k, v in kw.items() if v is not None})
    return out


def _check_args(spec, a):
    for name, desc in spec["args"].items():
        typ = desc.split(" ", 1)[0]
        optional = typ.endswith("?")
        if not optional and name not in a and not (name in ("m", "d") and any(k in a for k in SOURCES)):
            raise OpError(102, f"argument '{name}' is required ({desc})")


def handle(msg, ctx=None):
    """Handle one message (dict) and return one response (dict). Never raises."""
    ctx = ctx if ctx is not None else {}
    mid = msg.get("id") if isinstance(msg, dict) else None
    t0 = time.perf_counter()
    name, a = None, {}
    try:
        if not isinstance(msg, dict) or not isinstance(msg.get("op"), str):
            raise OpError(100, "a message is an object with an 'op' string")
        name, a = msg["op"], msg.get("a") or {}
        if not isinstance(a, dict):
            raise OpError(103, "'a' must be an object")
        spec = OPS.get(name)
        if spec is None:
            close = [o for o in OPS if o.split(".")[-1] == name.split(".")[-1]][:3]
            raise OpError(101, f"unknown operation '{name}'" + (f"; did you mean {', '.join(close)}?" if close else ""))
        if spec["human"] and not ctx.get("human"):
            raise OpError(104, f"'{name}' records a person's judgment; a person runs it with the command line")
        _check_args(spec, a)
        for h in HOOKS["before"]:
            h(name, a, ctx)
        resp = spec["fn"](a, ctx)
    except OpError as x:
        resp = {"ok": False, "e": [[x.code, x.msg]]}
        if x.data is not None:
            resp["r"] = x.data
        if x.fix:
            resp["fix"] = x.fix
    except SystemExit as x:            # the human tools stop with SystemExit and a message
        resp = {"ok": False, "e": [[_systemexit_code(str(x)), str(x)]]}
    except Exception as x:  # noqa: BLE001 - reported to the caller, never crashes the server
        resp = {"ok": False, "e": [[107, f"{type(x).__name__}: {x}"]]}
        if ctx.get("debug"):
            resp["trace"] = traceback.format_exc()
    if name in OPS and isinstance(a, dict):
        for h in HOOKS["after"]:          # after-hooks see refusals too, so the log is complete
            try:
                h(name, a, resp, ctx)
            except Exception:  # noqa: BLE001
                pass
    if mid is not None:
        resp = dict({"id": mid}, **resp)
    if ctx.get("timing"):
        resp["ms"] = round((time.perf_counter() - t0) * 1000, 3)
    return resp


def _systemexit_code(text):
    t = text.lower()
    if "not found" in t or "not an attached brick" in t:
        return 106
    if "already attached" in t or "cannot be" in t:
        return 220
    if "bridge" in t:
        return 403 if "has not passed" in t else 402
    return 108


def handle_any(payload, ctx=None):
    """A message or a batch (list). A batch stops at the first failure when ctx['stop'] is true."""
    if isinstance(payload, list):
        if len(payload) > LIMITS["batch"]:
            return {"ok": False, "e": [[105, f"a batch holds at most {LIMITS['batch']} messages"]]}
        out = []
        for m in payload:
            r = handle(m, ctx)
            out.append(r)
            if ctx and ctx.get("stop") and not r.get("ok"):
                break
        return out
    return handle(payload, ctx)


def handle_text(line, ctx=None):
    try:
        payload = json.loads(line)
    except ValueError as x:
        return {"ok": False, "e": [[100, f"not JSON: {x}"]]}
    return handle_any(payload, ctx)


# ------------------------------------------------------------------ protocol operations
def _arg_schema(spec):
    props, req = {}, []
    tmap = {"str": "string", "int": "integer", "num": "number", "bool": "boolean", "obj": "object", "list": "array",
            "any": None}
    for name, desc in spec["args"].items():
        typ, _, text = desc.partition(" ")
        optional = typ.endswith("?")
        t = tmap.get(typ.rstrip("?"), "string")
        props[name] = {"description": text} if t is None else {"type": t, "description": text}
        if not optional and name not in ("m", "d"):
            req.append(name)
    return {"type": "object", "properties": props, "required": req}


def describe_ops(group=None):
    return {n: {"s": s["summary"], "a": s["args"], **({"mut": 1} if s["mutates"] else {}),
                **({"human": 1} if s["human"] else {})}
            for n, s in sorted(OPS.items()) if not group or s["group"] == group}


@op("hello", "the handshake: protocol, conventions, operations, finding codes and limits", {
    "brief": "bool? true leaves out the operation list (fetch it with ops)"})
def _hello(a, ctx):
    r = {
        "protocol": PROTOCOL, "studio": VERSION,
        "keys": {"op": "operation", "a": "arguments", "id": "your message id, echoed", "ok": "true or false",
                 "r": "result", "e": "errors as [code, brick, subject, ...]", "w": "warnings, same form",
                 "h": "fingerprint of the state after the operation", "fix": "operations that would fix the findings",
                 "m": "manifest path", "d": "inline manifest", "t": "workspace track", "b": "brick id", "p": "port",
                 "base": "the fingerprint your change assumes; a mismatch is refused with code 219"},
        "rules": [
            "A batch is a JSON list of messages; responses come back in the same order.",
            "Mutating operations are plans unless a.apply is true. A plan returns the new state's fingerprint and, "
            "for inline models (d), the new model itself, so you can chain plans without writing anything.",
            "Send base with every write. On code 219, read the state again and retry.",
            "Finding codes are stable; messages are for people. Send fix entries back unchanged to apply them.",
            "Operations marked human are refused: sign-off is a person's judgment.",
            "Use 'say' to turn any response into plain language for a person.",
        ],
        "codes": {str(k): v[0] for k, v in sorted(CODES.items())},
        "limits": LIMITS,
        "sources": sorted(SOURCES),
    }
    if not a.get("brief"):
        r["ops"] = describe_ops()
    return _ok(r)


@op("ops", "the list of operations with their arguments", {"group": "str? only this group, e.g. lego or ws"})
def _ops(a, ctx):
    return _ok(describe_ops(a.get("group")))


@op("explain", "what finding or error codes mean", {"codes": "list? codes to explain; all if omitted"})
def _explain(a, ctx):
    want = a.get("codes") or sorted(CODES)
    return _ok({str(c): {"name": CODES[int(c)][0], "meaning": CODES[int(c)][1]} for c in want if int(c) in CODES})


def say(resp):
    """Plain language for a person, from any response or batch of responses."""
    if isinstance(resp, list):
        return "\n".join(say(r) for r in resp)
    lines = []
    head = "Done." if resp.get("ok") else "Refused."
    if resp.get("id") is not None:
        head = f"[{resp['id']}] {head}"
    lines.append(head)
    for label, key in (("Error", "e"), ("Warning", "w")):
        for row in resp.get(key, []):
            c = row[0]
            name, meaning = CODES.get(c, ("?", "unknown code"))
            detail = [str(x) for x in row[1:] if x not in ("", None)]
            if detail and len(detail[-1]) > 40:   # a full message is already plain language
                lines.append(f"  {label} {c}: {detail[-1]}")
            else:
                lines.append(f"  {label} {c} ({meaning})" + (f": {', '.join(detail)}" if detail else ""))
    r = resp.get("r")
    if isinstance(r, dict):
        if "summary" in r:
            lines.append("  " + r["summary"])
        for k in ("saved", "h", "revision"):
            if k in r:
                lines.append(f"  {k}: {r[k]}")
    for f in resp.get("fix", []):
        lines.append(f"  Suggested fix: {f['op']} {json.dumps(f.get('a', {}))}")
    return "\n".join(lines)


@op("say", "turn a response, or a list of responses, into plain language for a person", {
    "resp": "any the response object or list"})
def _say(a, ctx):
    return _ok({"text": say(a["resp"])})


# ------------------------------------------------------------------ lego operations
def _counts(rep):
    return {"joints": len(rep["joints"]), "stubs": len(rep["stubs"]), "bridges": len(rep.get("bridges", [])),
            "blocks": len(rep["sim_blocks"]), "validated": rep["validation"].get("validated", 0),
            "stale": rep["validation"].get("stale", 0), "signed": rep.get("signoff", {}).get("approved", 0)}


@op("lego.catalog", "reusable bricks: id, kind, frequency, what each provides and requires", {
    "kind": "str? only this kind", "port": "str? only bricks that provide this port"})
def _catalog(a, ctx):
    out = {}
    for cid, b in lego.load_catalog().items():
        if a.get("kind") and b.get("kind") != a["kind"]:
            continue
        if a.get("port") and a["port"] not in lego.provs(b):
            continue
        out[cid] = {"k": b.get("kind"), "f": b.get("freq"), "p": lego.provs(b),
                    "q": [q["port"] for q in lego.reqs(b)]}
    return _ok(out)


@op("lego.ports", "the shared port registry: unit, timing and measure of every variable", {})
def _ports(a, ctx):
    return _ok(lego.load_ports())


@op("lego.get", "read a model; returns its fingerprint and, with full, the model itself", {
    "m": "str manifest path (or d, or t)", "full": "bool? include the model"})
def _get(a, ctx):
    src = resolve(a)
    r = {"name": src.doc.get("name"), "freq": src.doc.get("freq"), "revision": src.doc.get("revision"),
         "bricks": {b["id"]: b.get("status", "attached") for b in src.doc.get("bricks", [])}}
    if a.get("full"):
        r["d"] = src.doc
    return _ok(r, h=src.h)


@op("lego.check", "check the wiring: errors and warnings as codes, counts, and fixes", {
    "m": "str manifest path (or d, or t)", "strict": "bool? warnings count as failure",
    "full": "bool? add the plain-language message to each finding", "detail": "bool? joints, stubs and bridges too"})
def _check(a, ctx):
    src = resolve(a)
    rep, e, w = report(src.doc, a.get("full"))
    r = {"pass": not e and not (a.get("strict") and w), "n": _counts(rep)}
    if a.get("detail"):
        r.update({k: rep[k] for k in ("joints", "stubs", "order", "sim_blocks", "wiring")})
        r["bridges"] = rep.get("bridges", [])
    fx = fixes(src.doc, rep, e + w)
    return _ok(r, e=e or None, w=w or None, h=src.h, fix=fx or None)


def _commit(src, a, m2, rep, d, extra=None):
    """Shared end of every change: plan, or write with compare-and-swap."""
    _, e, w = report(m2, a.get("full"), rep)
    new = [finding(x) for x in d.get("new_errors", [])] + [[216 if "ports.json" in x else 217, "", x]
                                                           for x in d.get("setup_errors", [])]
    blocked = bool(new or e)
    r = {"applied": False, "revision": m2.get("revision"), "n": _counts(rep)}
    if d:
        r["delta"] = {k: v for k, v in (("+joints", d.get("joints_added")), ("-joints", d.get("joints_removed")),
                                        ("+stubs", [[s["consumer"], s["port"]] for s in d.get("stubs_activated", [])]),
                                        ("-stubs", [[s["consumer"], s["port"]] for s in d.get("stubs_retired", [])]),
                                        ("stale", d.get("neighbours"))) if v}
    if extra:
        r.update(extra)
    h = fingerprint(m2)
    if a.get("apply"):
        if blocked and not a.get("force"):
            raise OpError(218, "the change would leave errors; nothing was written",
                          data={"new": new, "e": e}, fix=fixes(m2, rep, e))
        if src.inline:
            r["d"] = m2
        else:
            if a.get("base") and a["base"] != src.h:
                raise OpError(219, f"the state changed since {a['base']} (now {src.h})", data={"h": src.h})
            r.update(src.save(m2, a))
        r["applied"] = True
    elif src.inline:
        r["d"] = m2
    r["blocked"] = blocked
    return _ok(r, e=e or None, w=w or None, h=h, fix=fixes(m2, rep, e + w) or None)


def _spec(ref):
    try:
        return lego.resolve_spec(ref, lego.load_catalog())
    except SystemExit:
        raise OpError(106, f"brick '{ref}' is not in the catalog or a file")


@op("lego.new", "start a model from catalog bricks; returns it inline (and writes it with m and apply)", {
    "name": "str model name", "bricks": "list brick ids from the catalog", "freq": "str? A, Q or M (default Q)",
    "cls": "str? small, medium, large or ai", "m": "str? path to write with apply", "apply": "bool? write it"},
    mutates=True)
def _new(a, ctx):
    doc = {"lego_version": 1, "name": a["name"], "class": a.get("cls", "medium"), "freq": a.get("freq", "Q"),
           "revision": 1, "ports": {}, "required_slots": [], "identities": [], "bricks": [], "history": []}
    errs = []
    for ref in a["bricks"]:
        spec = _spec(ref)
        b = lego.new_brick(spec)
        lego._merge_ports(doc, b, errs)
        doc["bricks"].append(b)
        lego._merge_identities(doc, spec)
    lego._stamp(doc, "create", ",".join(a["bricks"]))
    doc["revision"] = 1
    rep = lego.check(doc)
    if a.get("m") and a.get("apply"):
        path = _path(a["m"])
        if os.path.exists(path) and not a.get("force"):
            raise OpError(108, f"{a['m']} exists (force overwrites)")
        if rep["errors"] and not a.get("force"):
            raise OpError(218, "the new model has errors; nothing was written", data={"e": report(doc, False, rep)[1]})
        lego.write_json(path, doc)
        return _ok({"applied": True, "saved": a["m"], "n": _counts(rep)}, h=fingerprint(doc),
                   e=report(doc, False, rep)[1] or None)
    _, e, w = report(doc, a.get("full"), rep)
    return _ok({"applied": False, "d": doc, "n": _counts(rep)}, e=e or None, w=w or None, h=fingerprint(doc),
               fix=fixes(doc, rep, e + w) or None)


@op("lego.attach", "add a brick (catalog id, file, or inline spec); a plan unless apply", {
    "m": "str manifest path (or d, or t)", "brick": "any catalog id, file path, or a brick object",
    "apply": "bool? write it", "base": "str? fingerprint the change assumes", "force": "bool? write despite errors",
    "note": "str? why"}, mutates=True)
def _attach(a, ctx):
    src = resolve(a)
    spec = copy.deepcopy(a["brick"]) if isinstance(a["brick"], dict) else _spec(a["brick"])
    m2, rep, d = lego.plan_attach(src.doc, spec, a.get("note", ""))
    return _commit(src, a, m2, rep, d)


@op("lego.detach", "move a brick to the parts bin; a plan unless apply", {
    "m": "str manifest path (or d, or t)", "b": "str brick id", "apply": "bool? write it",
    "base": "str? fingerprint the change assumes", "force": "bool? write despite errors", "note": "str? why"},
    mutates=True)
def _detach(a, ctx):
    src = resolve(a)
    m2, rep, d = lego.plan_detach(src.doc, a["b"], a.get("note", ""))
    return _commit(src, a, m2, rep, d)


@op("lego.swap", "replace one brick with another; a plan unless apply", {
    "m": "str manifest path (or d, or t)", "b": "str brick to take out", "brick": "any replacement id, file or object",
    "apply": "bool? write it", "base": "str? fingerprint", "force": "bool? write despite errors", "note": "str? why"},
    mutates=True)
def _swap(a, ctx):
    src = resolve(a)
    spec = copy.deepcopy(a["brick"]) if isinstance(a["brick"], dict) else _spec(a["brick"])
    m2, rep, d = lego.plan_swap(src.doc, a["b"], spec, a.get("note", ""))
    return _commit(src, a, m2, rep, d)


PATCHABLE = ("freq", "bridge", "requires", "provides", "slot", "summary", "elements", "code", "place", "params")


def _changed_brick(m2, bid, why):
    b = lego.find(m2, bid)
    if b.get("validation") == "validated":
        b["validation"] = "stale"
    lego._withdraw_signoff(b, why)
    lego._mark_stale(m2, lego.neighbours(m2, bid))


@op("lego.patch", "change fields of one brick (freq, bridge, requires, provides, slot, elements, params, ...)", {
    "m": "str manifest path (or d, or t)", "b": "str brick id", "set": "obj fields and their new values",
    "apply": "bool? write it", "base": "str? fingerprint", "force": "bool? write despite errors", "note": "str? why"},
    mutates=True)
def _patch(a, ctx):
    src = resolve(a)
    if not isinstance(a["set"], dict) or not a["set"]:
        raise OpError(103, "set must be a non-empty object")
    bad = sorted(set(a["set"]) - set(PATCHABLE))
    if bad:
        raise OpError(103, f"these fields cannot be patched: {', '.join(bad)} (allowed: {', '.join(PATCHABLE)})")
    before = lego.check(src.doc)
    m2 = copy.deepcopy(src.doc)
    b = lego.find(m2, a["b"])
    if b is None:
        raise OpError(106, f"no brick '{a['b']}'")
    for k, v in a["set"].items():
        if v is None:
            b.pop(k, None)
        else:
            b[k] = copy.deepcopy(v)
    errs = []
    lego._merge_ports(m2, b, errs)
    cosmetic = set(a["set"]) <= {"place", "summary"}
    if not cosmetic:
        _changed_brick(m2, a["b"], "patched: " + ", ".join(sorted(a["set"])))
    lego._stamp(m2, "patch", a["b"], a.get("note", ", ".join(sorted(a["set"]))))
    rep = lego.check(m2)
    d = lego._diff(before, rep)
    d["setup_errors"] = errs
    d["neighbours"] = [] if cosmetic else sorted(lego.neighbours(m2, a["b"]))
    return _commit(src, a, m2, rep, d)


@op("lego.bridge", "declare how a brick's ports convert between frequencies (auto picks from each port's measure)", {
    "m": "str manifest path (or d, or t)", "b": "str brick id", "p": "str? port", "method": "str? method for p",
    "methods": "obj? {port: method}", "auto": "bool? a method for every crossing port, from its measure",
    "apply": "bool? write it", "base": "str? fingerprint", "force": "bool? write despite errors"}, mutates=True)
def _bridge(a, ctx):
    src = resolve(a)
    b = lego.find(src.doc, a["b"])
    if b is None:
        raise OpError(106, f"no brick '{a['b']}'")
    cur = b.get("bridge") if isinstance(b.get("bridge"), dict) else {}
    methods = dict(cur.get("methods") or {})
    if a.get("methods"):
        methods.update(a["methods"])
    if a.get("p"):
        if not a.get("method"):
            raise OpError(102, "method is required with p")
        methods[a["p"]] = a["method"]
    if a.get("auto"):
        rep = lego.check(src.doc)
        mf = src.doc.get("freq")
        freq = {x["id"]: x.get("freq") or mf for x in lego.attached(src.doc)}
        registry = lego.load_ports()
        for j in rep["joints"]:
            for side, other in (("from", "to"), ("to", "from")):
                if j[side] == a["b"] and freq.get(j[other], mf) != freq[a["b"]]:
                    s, t = (freq[a["b"]], freq[j[other]]) if side == "from" else (freq[j[other]], freq[a["b"]])
                    meas = (src.doc.get("ports", {}).get(j["port"]) or {}).get("measure") or \
                        (registry.get(j["port"]) or {}).get("measure")
                    methods.setdefault(j["port"], _suggest_method(meas, s, t))
    for p, mth in methods.items():
        if mth not in bridgemod.METHODS:
            raise OpError(103, f"'{mth}' is not a method; use one of {', '.join(bridgemod.METHODS)}")
    new = dict(cur)
    new["methods"] = methods
    a2 = dict(a, set={"bridge": new})
    return _patch(a2, ctx)


@op("lego.bridge_test", "known-answer tests of every declared bridge; apply records the result", {
    "m": "str manifest path (or d, or t)", "data": "obj? {port: [[period, value], ...]} to convert as well",
    "apply": "bool? record the result", "base": "str? fingerprint"}, mutates=True)
def _bridge_test(a, ctx):
    src = resolve(a)
    rep = lego.check(src.doc)
    results, out, e = {}, [], []
    for bid in rep["untestable"]:
        e.append([402, bid])
    for x in rep["bridges"]:
        cases = bridgemod.known_answers(x["method"], x["from"], x["to"])
        ok = all(c[3] for c in cases)
        row = {"b": x["brick"], "p": x["port"], "from": x["from"], "to": x["to"], "method": x["method"], "pass": ok}
        rows = (a.get("data") or {}).get(x["port"])
        if rows is not None:
            try:
                row["out"] = bridgemod.convert([tuple(r) for r in rows], x["method"], x["from"], x["to"])
            except (bridgemod.BridgeError, ValueError, IndexError) as err:
                ok = row["pass"] = False
                e.append([404, x["brick"], x["port"], str(err)])
        if not ok and not rows:
            e.append([214, x["brick"], x["port"]])
        out.append(row)
        results.setdefault(x["brick"], []).append(ok)
    r = {"tests": out, "pass": not e}
    if a.get("apply") and results:
        m2 = copy.deepcopy(src.doc)
        today = time.strftime("%Y-%m-%d")
        for bid, oks in results.items():
            mine = [x for x in rep["bridges"] if x["brick"] == bid]
            lego.find(m2, bid)["bridge_test"] = {"result": "pass" if all(oks) else "fail", "on": today,
                                                 "signature": lego._bridge_signature(mine)}
        lego._stamp(m2, "bridge-test", ",".join(sorted(results)), "passed" if not e else "failed")
        if src.inline:
            r["d"] = m2
        else:
            if a.get("base") and a["base"] != src.h:
                raise OpError(219, f"the state changed since {a['base']} (now {src.h})", data={"h": src.h})
            r.update(src.save(m2, a))
        r["applied"] = True
        return _ok(r, e=e or None, h=fingerprint(m2))
    return _ok(r, e=e or None, h=src.h)


@op("lego.validate", "record an independent validator's verdict on a brick's numbers, with the report as evidence", {
    "m": "str manifest path (or d, or t)", "b": "str brick id", "status": "str? validated, unvalidated or stale",
    "report": "str path to the validation report (needed for validated)", "apply": "bool? write it",
    "base": "str? fingerprint"}, mutates=True)
def _validate(a, ctx):
    src = resolve(a)
    status = a.get("status", "validated")
    b = lego.find(src.doc, a["b"])
    if b is None or b.get("status", "attached") != "attached":
        raise OpError(106, f"'{a['b']}' is not an attached brick")
    if status == "validated":
        if not a.get("report") or not os.path.isfile(_path(a["report"])):
            raise OpError(102, "report must name an existing validation report")
        rep = lego.check(src.doc)
        if a["b"] in rep.get("untestable", []):
            raise OpError(402, f"{a['b']} needs a testable bridge first", fix=[{"op": "lego.bridge",
                                                                              "a": {"b": a["b"], "auto": True}}])
        mine = [x for x in rep.get("bridges", []) if x["brick"] == a["b"]]
        t = b.get("bridge_test") or {}
        if mine and not (t.get("result") == "pass" and t.get("signature") == lego._bridge_signature(mine)):
            raise OpError(403, f"{a['b']}: run the bridge tests first",
                          fix=[{"op": "lego.bridge_test", "a": {"apply": True}}])
    m2 = copy.deepcopy(src.doc)
    b2 = lego.find(m2, a["b"])
    b2["validation"] = status
    if status == "validated":
        b2["validation_report"] = a["report"].replace("\\", "/")
        b2["validated_on"] = time.strftime("%Y-%m-%d")
    else:
        b2.pop("validated_on", None)
        lego._withdraw_signoff(b2, f"numbers marked {status}")
    lego._stamp(m2, "validate", a["b"], status)
    rep = lego.check(m2)
    return _commit(src, a, m2, rep, {})


@op("lego.approve", "the economist's sign-off: refused to agents; a person runs lego.py approve", {
    "m": "str manifest path", "b": "str brick id", "by": "str the person's name"}, mutates=True, human=True)
def _approve(a, ctx):  # reachable only from a human channel
    raise OpError(104, "use: python tools/lego.py approve <manifest> <brick> --by NAME --apply")


@op("lego.text", "the human-readable check of a model, as the command line prints it", {
    "m": "str manifest path (or d, or t)"})
def _text(a, ctx):
    src = resolve(a)
    rep = lego.check(src.doc)
    return _ok({"text": lego.render_text(src.doc, rep, lego.load_catalog())}, h=src.h)


# ------------------------------------------------------------------ bridges and known answers
@op("bridge.methods", "the conversion methods: direction and the measure each one assumes", {})
def _methods(a, ctx):
    return _ok({k: {"dir": v[0], "measure": v[1]} for k, v in bridgemod.METHODS.items()})


@op("bridge.convert", "convert a series between frequencies with a declared method; refuses incomplete periods", {
    "rows": "list [[period, value], ...] e.g. [['2025Q1', 1.0], ...]", "method": "str method",
    "from": "str A, Q or M", "to": "str A, Q or M"})
def _convert(a, ctx):
    prob = bridgemod.fits(a["method"], a["from"], a["to"])
    if prob:
        raise OpError(213, prob)
    try:
        return _ok({"rows": bridgemod.convert([tuple(r) for r in a["rows"]], a["method"], a["from"], a["to"])})
    except bridgemod.BridgeError as x:
        raise OpError(404, str(x))


@op("ka.list", "known-answer cases: id, area, title", {})
def _ka_list(a, ctx):
    return _ok({k: {"area": c["area"], "title": c["title"], "tol": c["tol"]} for k, c in kamod.CASES.items()})


@op("ka.task", "a known-answer task: its inputs inline and the instructions (never the answer)", {
    "case": "str case id"})
def _ka_task(a, ctx):
    c = kamod.CASES.get(a["case"])
    if c is None:
        raise OpError(106, f"no case '{a['case']}'")
    d = tempfile.mkdtemp(prefix="ka-")
    try:
        with redirect_stdout(io.StringIO()):
            c["make"](d)
        files = {}
        for p in sorted(glob.glob(os.path.join(d, "*"))):
            with open(p, encoding="utf-8") as f:
                files[os.path.basename(p)] = f.read()
    finally:
        for p in glob.glob(os.path.join(d, "*")):
            os.remove(p)
        os.rmdir(d)
    return _ok({"task": c["task"], "files": files, "tol": c["tol"]})


@op("ka.check", "check a result against the known answer", {"case": "str case id", "result": "obj your result"})
def _ka_check(a, ctx):
    if a["case"] not in kamod.CASES:
        raise OpError(106, f"no case '{a['case']}'")
    rows = kamod.check_result(a["case"], a["result"])
    bad = [[r[0], r[1], r[2]] for r in rows if not r[3]]
    resp = _ok({"pass": not bad, "values": len(rows), "failed": bad[:20]})
    if bad:
        resp["e"] = [[401, "", a["case"], f"{len(bad)} of {len(rows)} values"]]
    return resp


# ------------------------------------------------------------------ the studio's specialist agents and skills
def _md_files(kind):
    """{name: (description, body)} for .claude/agents/*.md or .claude/skills/*/SKILL.md."""
    pattern = os.path.join(ROOT, ".claude", "agents", "*.md") if kind == "agents" else \
        os.path.join(ROOT, ".claude", "skills", "*", "SKILL.md")
    out = {}
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        name = os.path.basename(path)[:-3] if kind == "agents" else os.path.basename(os.path.dirname(path))
        mt = re.search(r'^description:\s*"?(.*?)"?\s*$', text, re.M)
        body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S).strip()
        out[name] = (mt.group(1) if mt else "", body)
    return out


def _find(kind, a):
    items = _md_files(kind)
    words = [w for w in re.split(r"\W+", (a.get("query") or "").lower()) if w]
    rows = []
    for name, (desc, _) in items.items():
        hay = f"{name} {desc}".lower()
        score = sum(hay.count(w) for w in words)
        if score or not words:
            rows.append((-score, name, desc))
    rows.sort()
    return {n: d for _, n, d in rows[: int(a.get("limit", 200))]}


@op("agents.list", "the studio's specialist agents (an outside agent can take on any of them); query filters them", {
    "query": "str? words to look for in names and descriptions", "limit": "int? most results"})
def _agents_list(a, ctx):
    return _ok(_find("agents", a))


@op("agents.get", "a specialist's full instructions: what it knows, the checks it runs, the mistakes it watches for", {
    "name": "str the agent's name, from agents.list"})
def _agents_get(a, ctx):
    items = _md_files("agents")
    if a["name"] not in items:
        raise OpError(106, f"no agent '{a['name']}' (agents.list lists them)")
    desc, body = items[a["name"]]
    return _ok({"name": a["name"], "description": desc, "instructions": body})


@op("agents.brief", "a ready-to-use brief: a specialist's instructions plus your task, to give to your own model or "
    "subagent", {"name": "str the agent's name", "task": "str what you want the specialist to do"})
def _agents_brief(a, ctx):
    items = _md_files("agents")
    if a["name"] not in items:
        raise OpError(106, f"no agent '{a['name']}' (agents.list lists them)")
    desc, body = items[a["name"]]
    brief = (f"Act as the studio's specialist '{a['name']}' ({desc}). Follow these instructions, then do the task.\n\n"
             f"{body}\n\n## Task\n{a['task']}\n\nUse the studio's operations (hello lists them) to check your work: "
             "findings come back as codes with fixes. The economist's sign-off is given by a person, never by you.")
    return _ok({"brief": brief})


@op("skills.list", "the studio's skills (workflow commands such as /build-dsge); query filters them", {
    "query": "str? words to look for", "limit": "int? most results"})
def _skills_list(a, ctx):
    return _ok(_find("skills", a))


@op("skills.get", "a skill's full workflow: the steps, where it stops for approval, which agents do the work", {
    "name": "str the skill's name, from skills.list"})
def _skills_get(a, ctx):
    items = _md_files("skills")
    if a["name"] not in items:
        raise OpError(106, f"no skill '{a['name']}' (skills.list lists them)")
    desc, body = items[a["name"]]
    return _ok({"name": a["name"], "description": desc, "workflow": body})


# ------------------------------------------------------------------ extensions
class _Api:
    """What an extension's register(api) receives."""
    op = staticmethod(op)
    code = staticmethod(code)
    source = staticmethod(source)
    OpError = OpError
    Source = Source
    ok = staticmethod(_ok)
    resolve = staticmethod(resolve)
    fingerprint = staticmethod(fingerprint)
    hooks = HOOKS
    handle = staticmethod(handle)
    ROOT = ROOT
    lego = lego
    ops = OPS
    codes = CODES


api = _Api()
LOADED = []


def load_extensions(folders=None):
    """Built-in modules first (workspace, economy, evolve, swarm), then extensions/*.py and STUDIO_EXTENSIONS folders."""
    for mod in ("workspace", "economy", "evolve", "swarm"):
        path = os.path.join(TOOLS, mod + ".py")
        if os.path.exists(path) and mod not in LOADED:
            m = importlib.import_module(mod)
            if hasattr(m, "register"):
                m.register(api)
                LOADED.append(mod)
    folders = folders or [os.path.join(ROOT, "extensions")] + \
        [p for p in os.environ.get("STUDIO_EXTENSIONS", "").split(os.pathsep) if p]
    for folder in folders:
        for path in sorted(glob.glob(os.path.join(folder, "*.py"))):
            name = "ext_" + os.path.splitext(os.path.basename(path))[0]
            if name in LOADED:
                continue
            spec = importlib.util.spec_from_file_location(name, path)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            if hasattr(m, "register"):
                m.register(api)
                LOADED.append(name)
    return LOADED


# ------------------------------------------------------------------ command line
def serve(stdin=None, stdout=None, ctx=None):
    """JSON lines: one message (or batch) per line in, one response per line out."""
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        stdout.write(json.dumps(handle_text(line, ctx), separators=(",", ":"), ensure_ascii=False) + "\n")
        stdout.flush()


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    argv = sys.argv[1:] if argv is None else argv
    load_extensions()
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    human = "--human" in rest
    say_it = "--say" in rest
    rest = [x for x in rest if x not in ("--human", "--say")]
    ctx = {"human": human, "timing": True}
    if cmd == "hello":
        print(json.dumps(handle({"op": "hello"}, ctx), indent=1))
    elif cmd == "call":
        text = rest[0] if rest else sys.stdin.read()
        if text == "-":
            text = sys.stdin.read()
        resp = handle_text(text, ctx)
        print(say(resp) if say_it else json.dumps(resp, indent=1, ensure_ascii=False))
        ok = all(r.get("ok") for r in resp) if isinstance(resp, list) else resp.get("ok")
        return 0 if ok else 1
    elif cmd == "serve":
        serve(ctx={"human": False})
    elif cmd == "codes":
        for c, (slug, meaning) in sorted(CODES.items()):
            print(f"{c}  {slug:<22} {meaning}")
    else:
        print(f"unknown command '{cmd}'; use hello, call, serve or codes")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
