#!/usr/bin/env python3
"""The improvement loop: many agents propose changes to a model, the studio scores them all, keeps the best,
and guards against changes that only look good on the cases the agents can see.

A STUDY says what "better" means (targets for the model's results, with weights), what may change (parameters
within bounds, optionally behaviour rules), on which cases it is scored (training seeds, which agents see), and on
which it is checked before a change is accepted (hidden seeds, which agents never see). Each round, the loop scores
every candidate waiting (proposed by agents, or made by the loop itself by varying the best ones) in parallel
processes, ranks them, and promotes a new champion to the study's track only if it is better AND holds up on the
hidden seeds. Everything is logged on the shared workspace, so people can read the report, freeze parameters,
leave constraints or pause the study at any time.

    python tools/evolve.py start calib --track eco --target unemployment=0.06 --target inflation=0.02 \\
        --free search=1:8 --free theta_w=0:0.1 --budget 400
    python tools/evolve.py run calib [--rounds 10] [--workers 8]
    python tools/evolve.py status calib
    python tools/evolve.py stop calib

For agents: evolve.start, evolve.propose, evolve.step, evolve.status, evolve.best in the studio protocol.
"""
import argparse
import copy
import json
import math
import os
import random
import sys
import time
import zlib

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)

API = None
SCHEMA = """
CREATE TABLE IF NOT EXISTS studies (name TEXT PRIMARY KEY, track TEXT, spec TEXT, hidden TEXT, status TEXT,
    round INTEGER DEFAULT 0, evals INTEGER DEFAULT 0, champion INTEGER, created REAL, by TEXT);
CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY AUTOINCREMENT, study TEXT, round INTEGER, by TEXT,
    params TEXT, rules TEXT, note TEXT, status TEXT, loss REAL, moments TEXT, hidden_loss REAL, reason TEXT, ts REAL);
CREATE INDEX IF NOT EXISTS cand_study ON candidates(study, status);
"""
OBJECTIVES = {}


def objective(kind):
    """Register how a kind of model is scored: fn(spec, states, seeds, workers) -> list of (loss, moments, reason)."""
    def deco(fn):
        OBJECTIVES[kind] = fn
        return fn
    return deco


def _loss(moments, targets):
    total = 0.0
    for k, (target, weight) in targets.items():
        v = moments.get(k)
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return float("inf")
        scale = max(abs(target), 0.01)
        total += weight * ((v - target) / scale) ** 2
    return total


@objective("economy")
def _economy_objective(spec, states, seeds, workers):
    import economy
    flat = [(i, dict(copy.deepcopy(s), seed=sd)) for i, s in enumerate(states) for sd in seeds]
    out = [[] for _ in states]
    good = []
    for i, cfg in flat:
        probs = economy.check_config(cfg)
        if probs:
            out[i].append({"error": probs[0][2]})
        else:
            good.append((i, cfg))
    if good:
        results = economy.run_many([c for _, c in good], workers=workers)
        for (i, _), r in zip(good, results):
            out[i].append(r)
    scored = []
    targets = {k: tuple(v) for k, v in spec["targets"].items()}
    for i, runs in enumerate(out):
        bad = [r["error"] for r in runs if "error" in r]
        if bad:
            scored.append((float("inf"), {}, f"invalid: {bad[0]}"))
            continue
        if states[i].get("money_check", True) and \
                max(r["accounting_error"] for r in runs) > spec.get("max_accounting_error", 1e-9):
            scored.append((float("inf"), {}, "bookkeeping error: money appeared or vanished without a recorded flow"))
            continue
        m = economy.average(runs)
        scored.append((_loss(m, targets), m, ""))
    return scored


@objective("lego")
def _lego_objective(spec, states, seeds, workers):
    import lego
    out = []
    for s in states:
        rep = lego.check(s)
        m = {"errors": len(rep["errors"]), "warnings": len(rep["warnings"]), "stubs": len(rep["stubs"]),
             "joints": len(rep["joints"]), "validated": rep["validation"].get("validated", 0)}
        targets = {k: tuple(v) for k, v in (spec.get("targets") or {"errors": [0, 100], "warnings": [0, 10]}).items()}
        out.append((sum(w * (m.get(k, 0) - t) ** 2 for k, (t, w) in targets.items()), m, ""))
    return out


# ------------------------------------------------------------------ storage (on the workspace database)
def _db(a):
    import workspace
    c = workspace.conn(workspace.db_path(a))
    c.executescript(SCHEMA)
    return c, workspace


def _study(c, name):
    row = c.execute("SELECT name, track, spec, hidden, status, round, evals, champion FROM studies WHERE name = ?",
                    (name,)).fetchone()
    if row is None:
        raise API.OpError(106, f"no study '{name}' (evolve.status lists them)")
    return {"name": row[0], "track": row[1], "spec": json.loads(row[2]), "hidden": json.loads(row[3]),
            "status": row[4], "round": row[5], "evals": row[6], "champion": row[7]}


def _apply(base, params, rules):
    s = copy.deepcopy(base)
    if params:
        s.setdefault("params", {}).update(params)
    if rules:
        s.setdefault("rules", {}).update(rules)
    return s


def _frozen(c, track):
    return {r[0] for r in c.execute("SELECT brick FROM freezes WHERE track IN (?, '*')", (track,))}


def _validate_candidate(st, params, rules, frozen):
    free = st["spec"]["free"]
    for k, v in (params or {}).items():
        if k not in free:
            raise API.OpError(701, f"'{k}' is not free to change in this study (free: {', '.join(sorted(free))})")
        if k in frozen:
            raise API.OpError(502, f"'{k}' is frozen by a person")
        lo, hi = free[k]
        if not isinstance(v, (int, float)) or not lo <= v <= hi:
            raise API.OpError(701, f"{k} = {v} is outside the study's range [{lo}, {hi}]")
    if rules and not st["spec"].get("rules_free"):
        raise API.OpError(701, "this study does not allow changes to behaviour rules")
    for k in rules or {}:
        if f"rule:{k}" in frozen:
            raise API.OpError(502, f"rule '{k}' is frozen by a person")


# ------------------------------------------------------------------ the loop's own proposals
def _mutations(st, best, pool, n, rng, frozen):
    """Vary the best candidates: a few parameters at a time, by a step that shrinks as the study goes on."""
    free = {k: v for k, v in st["spec"]["free"].items() if k not in frozen}
    if not free:
        return []
    out = []
    step = max(0.02, 0.3 * (0.85 ** st["round"]))
    parents = [best] + pool[:4] if best else pool[:5]
    parents = [p for p in parents if p] or [{}]
    for i in range(n):
        a = dict(parents[i % len(parents)])
        if len(parents) > 1 and rng.random() < 0.3:               # crossover with another good candidate
            b = parents[rng.randrange(len(parents))]
            for k in free:
                if k in b and rng.random() < 0.5:
                    a[k] = b[k]
        for k in rng.sample(sorted(free), max(1, min(len(free), int(rng.random() * 3) + 1))):
            lo, hi = free[k]
            cur = a.get(k, st["spec"]["start"].get(k, (lo + hi) / 2))
            v = cur + rng.gauss(0, step * (hi - lo))
            v = min(hi, max(lo, v))
            if isinstance(st["spec"]["start"].get(k), int) and float(lo).is_integer() and float(hi).is_integer():
                v = int(round(v))
            a[k] = v
        out.append(a)
    return out


# ------------------------------------------------------------------ operations
def register(api):
    global API
    API = api
    api.code(701, "outside_study", "the candidate changes something the study does not allow, or out of its range")
    api.code(702, "overfit", "the candidate did better on the training cases but not on the hidden ones")
    api.code(703, "budget_spent", "the study has used its evaluation budget")
    api.code(704, "study_closed", "the study is stopped or paused")
    op, ok, E = api.op, api.ok, api.OpError
    WS = "str? workspace file"

    @op("evolve.start", "start a study: targets for the results, what may change, training and hidden cases, budget", {
        "name": "str study name", "t": "str the workspace track with the model (its head is the starting point)",
        "targets": "obj {result: [target, weight]}, e.g. {\"unemployment\": [0.06, 1]}",
        "free": "obj {parameter: [low, high]} that candidates may change", "rules_free": "bool? candidates may rewrite rules",
        "seeds": "list? training seeds (default [1, 2])", "hidden": "int? number of hidden seeds (default 2)",
        "budget": "int? most model evaluations (default 500)", "pop": "int? loop proposals per round (default 8)",
        "tolerance": "num? how much worse the hidden cases may be than the training ones (default 0.5 = 50%)",
        "as": "str? your agent name", "ws": WS}, mutates=True)
    def start(a, ctx):
        c, ws = _db(a)
        tr = ws.track_row(c, a["t"])
        if tr["kind"] not in OBJECTIVES:
            raise E(103, f"track {a['t']} is of kind {tr['kind']}; studies can score: {', '.join(OBJECTIVES)}")
        base = ws.get_object(c, tr["head"])
        start_params = {k: (base.get("params") or {}).get(k) for k in a["free"]}
        rng = random.SystemRandom()
        hidden = {"seeds": [rng.randrange(10_000, 10_000_000) for _ in range(int(a.get("hidden", 2)))]}
        spec = {"kind": tr["kind"], "targets": a["targets"], "free": a["free"], "rules_free": bool(a.get("rules_free")),
                "seeds": a.get("seeds") or [1, 2], "budget": int(a.get("budget", 500)), "pop": int(a.get("pop", 8)),
                "tolerance": float(a.get("tolerance", 0.5)), "start": start_params}
        with ws.Tx(c):
            if c.execute("SELECT 1 FROM studies WHERE name = ?", (a["name"],)).fetchone():
                raise E(108, f"study '{a['name']}' exists")
            c.execute("INSERT INTO studies (name, track, spec, hidden, status, created, by) VALUES (?, ?, ?, ?, 'open', ?, ?)",
                      (a["name"], a["t"], json.dumps(spec), json.dumps(hidden), time.time(), ws.agent_of(a, ctx)))
            c.execute("INSERT INTO candidates (study, round, by, params, rules, note, status, ts) VALUES "
                      "(?, 0, 'start', ?, '{}', 'the starting point', 'pending', ?)",
                      (a["name"], json.dumps(start_params), time.time()))
        return ok({"study": a["name"], "seeds": spec["seeds"], "hidden_seeds": len(hidden["seeds"]),
                   "budget": spec["budget"]})

    @op("evolve.propose", "propose a candidate: new values for free parameters (and rules, if the study allows)", {
        "name": "str study", "params": "obj? {parameter: value}", "rules": "obj? {rule: formula}",
        "note": "str? why you think it is better", "as": "str? your agent name", "ws": WS}, mutates=True)
    def propose(a, ctx):
        c, ws = _db(a)
        st = _study(c, a["name"])
        if st["status"] != "open":
            raise E(704, f"study {a['name']} is {st['status']}")
        ws._before("evolve.propose", {"t": st["track"], "apply": True, **({"ws": a["ws"]} if a.get("ws") else {})},
                   ctx)                            # paused track or unread messages from a person: refused
        _validate_candidate(st, a.get("params"), a.get("rules"), _frozen(c, st["track"]))
        if a.get("rules"):
            import economy
            for k, f in a["rules"].items():
                try:
                    economy.compile_rule(k, f, dict({p: v[0] for p, v in economy.PARAMS.items()}, **(a.get("params") or {})))
                except (economy.RuleError, KeyError) as x:
                    raise E(601, str(x))
        with ws.Tx(c):
            cur = c.execute("INSERT INTO candidates (study, round, by, params, rules, note, status, ts) VALUES "
                            "(?, ?, ?, ?, ?, ?, 'pending', ?)",
                            (a["name"], st["round"], ws.agent_of(a, ctx), json.dumps(a.get("params") or {}),
                             json.dumps(a.get("rules") or {}), a.get("note", ""), time.time()))
        pending = c.execute("SELECT COUNT(*) FROM candidates WHERE study = ? AND status = 'pending'", (a["name"],)).fetchone()[0]
        return ok({"id": cur.lastrowid, "pending": pending})

    @op("evolve.step", "one round: score every waiting candidate (plus the loop's own) in parallel, rank, promote", {
        "name": "str study", "workers": "int? parallel processes", "max": "int? most candidates to score this round",
        "as": "str? your agent name", "ws": WS}, mutates=True)
    def step(a, ctx):
        return ok(run_round(a, ctx))

    @op("evolve.status", "a study's progress: round, evaluations, champion and leaderboard (never the hidden cases)", {
        "name": "str? study (all studies if omitted)", "top": "int? leaderboard size (default 10)", "ws": WS})
    def status(a, ctx):
        c, ws = _db(a)
        if not a.get("name"):
            return ok({r[0]: {"track": r[1], "status": r[2], "round": r[3], "evals": r[4]} for r in
                       c.execute("SELECT name, track, status, round, evals FROM studies ORDER BY name")})
        st = _study(c, a["name"])
        rows = c.execute("SELECT id, round, by, params, rules, loss, hidden_loss, status, note FROM candidates WHERE "
                         "study = ? AND loss IS NOT NULL ORDER BY loss LIMIT ?", (a["name"], int(a.get("top", 10)))).fetchall()
        counts = dict(c.execute("SELECT status, COUNT(*) FROM candidates WHERE study = ? GROUP BY status", (a["name"],)))
        champ = None
        if st["champion"]:
            r = c.execute("SELECT id, by, params, rules, loss, hidden_loss, moments FROM candidates WHERE id = ?",
                          (st["champion"],)).fetchone()
            champ = {"id": r[0], "by": r[1], "params": json.loads(r[2]), "rules": json.loads(r[3]), "loss": r[4],
                     "moments": json.loads(r[6] or "{}")}
            if ctx.get("human"):
                champ["hidden_loss"] = r[5]      # agents see only whether a candidate held up, never by how much
        spec = {k: v for k, v in st["spec"].items() if k != "start"}
        return ok({"status": st["status"], "round": st["round"], "evals": st["evals"], "budget": spec["budget"],
                   "targets": spec["targets"], "free": spec["free"], "counts": counts, "champion": champ,
                   "board": [{"id": r[0], "round": r[1], "by": r[2], "params": json.loads(r[3]), "loss": r[5],
                              "status": r[7], **({"note": r[8]} if r[8] else {})} for r in rows]})

    @op("evolve.stop", "stop or reopen a study (people only)", {"name": "str study", "reopen": "bool? reopen it",
                                                               "ws": WS}, mutates=True, human=True)
    def stop(a, ctx):
        c, ws = _db(a)
        _study(c, a["name"])
        with ws.Tx(c):
            c.execute("UPDATE studies SET status = ? WHERE name = ?", ("open" if a.get("reopen") else "stopped", a["name"]))
        return ok({"study": a["name"], "status": "open" if a.get("reopen") else "stopped"})

    return api


def run_round(a, ctx):
    c, ws = _db(a)
    st = _study(c, a["name"])
    E = API.OpError
    if st["status"] != "open":
        raise E(704, f"study {a['name']} is {st['status']}")
    tr = ws.track_row(c, st["track"])
    if tr["status"] != "open":
        raise E(501, f"track {st['track']} is {tr['status']}; the study waits for a person")
    spec = st["spec"]
    left = spec["budget"] - st["evals"]
    per = len(spec["seeds"])
    if left < per:
        with ws.Tx(c):
            c.execute("UPDATE studies SET status = 'done' WHERE name = ?", (a["name"],))
        raise E(703, f"study {a['name']} has used its budget of {spec['budget']} evaluations")
    frozen = _frozen(c, st["track"])
    base = ws.get_object(c, tr["head"])
    # 1. the candidates to score: agents' proposals first, then the loop's own variations of the best
    pend = c.execute("SELECT id, params, rules FROM candidates WHERE study = ? AND status = 'pending' ORDER BY id",
                     (a["name"],)).fetchall()
    cap = min(int(a.get("max", 10 ** 9)), left // per)
    pend = pend[:cap]
    rng = random.Random(zlib.crc32(f"{a['name']}:{st['round']}".encode()))
    best_rows = c.execute("SELECT params FROM candidates WHERE study = ? AND status IN ('scored', 'champion') "
                          "AND loss < 1e300 ORDER BY loss LIMIT 5", (a["name"],)).fetchall()
    pool = [json.loads(r[0]) for r in best_rows]
    champ = None
    if st["champion"]:
        champ = json.loads(c.execute("SELECT params FROM candidates WHERE id = ?", (st["champion"],)).fetchone()[0])
    room = max(0, min(spec["pop"], cap - len(pend)))
    made = _mutations(st, champ, pool, room, rng, frozen) if (pool or champ) and room else []
    with ws.Tx(c):
        for p in made:
            cur = c.execute("INSERT INTO candidates (study, round, by, params, rules, note, status, ts) VALUES "
                            "(?, ?, 'loop', ?, '{}', 'a variation of the best so far', 'pending', ?)",
                            (a["name"], st["round"], json.dumps(p), time.time()))
            pend.append((cur.lastrowid, json.dumps(p), "{}"))
    if not pend:
        return {"round": st["round"], "scored": 0, "note": "nothing to score"}
    # 2. score them all in parallel on the training seeds
    cands = [(cid, json.loads(p), json.loads(r)) for cid, p, r in pend]
    states = [_apply(base, p, r) for _, p, r in cands]
    t0 = time.time()
    scores = OBJECTIVES[spec["kind"]](spec, states, spec["seeds"], a.get("workers"))
    # 3. rank; a new leader must also hold up on the hidden seeds before it becomes the champion
    cur_loss = float("inf")
    if st["champion"]:
        cur_loss = c.execute("SELECT loss FROM candidates WHERE id = ?", (st["champion"],)).fetchone()[0]
    order = sorted(range(len(cands)), key=lambda i: scores[i][0])
    promoted, refused = None, []
    hidden_evals = 0
    for i in order:
        loss = scores[i][0]
        if not loss < cur_loss:
            break
        hscore = OBJECTIVES[spec["kind"]](spec, [states[i]], st["hidden"]["seeds"], a.get("workers"))[0]
        hidden_evals += len(st["hidden"]["seeds"])
        allowed = max(loss * (1 + spec["tolerance"]), loss + 0.05)
        if hscore[0] <= allowed:
            promoted = (i, hscore[0])
            break
        refused.append((cands[i][0], hscore[0]))
        if len(refused) >= 3:
            break
    with ws.Tx(c):
        for i, (cid, p, r) in enumerate(cands):
            loss, m, reason = scores[i]
            status = "rejected" if reason else "scored"
            c.execute("UPDATE candidates SET loss = ?, moments = ?, status = ?, reason = ? WHERE id = ?",
                      (loss if loss < float("inf") else 1e308, json.dumps(m), status, reason, cid))
        for cid, hl in refused:
            c.execute("UPDATE candidates SET status = 'overfit', hidden_loss = ? WHERE id = ?", (hl, cid))
        c.execute("UPDATE studies SET round = round + 1, evals = evals + ? WHERE name = ?",
                  (len(cands) * per + hidden_evals, a["name"]))
    result = {"round": st["round"] + 1, "scored": len(cands), "seconds": round(time.time() - t0, 2),
              "best_this_round": min(s[0] for s in scores) if scores else None, "overfit_refused": [r[0] for r in refused]}
    if promoted:
        i, hl = promoted
        cid = cands[i][0]
        new_state = dict(states[i], moments=scores[i][1])
        who = dict(ctx, agent=f"evolve:{a['name']}", human=False)
        msg = {"op": "ws.put", "a": {"t": st["track"], "d": new_state, "base": tr["head"], "score": scores[i][0],
                                     **({"ws": a["ws"]} if a.get("ws") else {})}}
        put = API.handle(msg, who)
        if not put.get("ok") and put["e"][0][0] == 503:      # people left messages: read them, report them, retry
            inbox = API.handle({"op": "ws.inbox", "a": {"ws": a["ws"]} if a.get("ws") else {}}, who)["r"]
            result["read_from_people"] = [m["text"] for m in inbox["msgs"]]
            put = API.handle(msg, who)
        if put.get("ok"):
            with ws.Tx(c):
                c.execute("UPDATE candidates SET status = 'champion', hidden_loss = ? WHERE id = ?", (hl, cid))
                c.execute("UPDATE studies SET champion = ? WHERE name = ?", (cid, a["name"]))
            result["champion"] = {"id": cid, "loss": scores[i][0], "params": cands[i][1],
                                  "by": c.execute("SELECT by FROM candidates WHERE id = ?", (cid,)).fetchone()[0]}
        else:
            result["not_promoted"] = put["e"][0][1]       # a person paused, froze or the track moved: try next round
    return result


# ------------------------------------------------------------------ command line for people
def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import studio_api as S
    S.load_extensions()
    ap = argparse.ArgumentParser(description="The improvement loop")
    ap.add_argument("--ws")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start")
    p.add_argument("name"); p.add_argument("--track", required=True)
    p.add_argument("--target", action="append", default=[], metavar="RESULT=VALUE[:WEIGHT]")
    p.add_argument("--free", action="append", default=[], metavar="PARAM=LOW:HIGH")
    p.add_argument("--budget", type=int, default=500); p.add_argument("--pop", type=int, default=8)
    p.add_argument("--seeds", type=int, nargs="+", default=[1, 2])
    p = sub.add_parser("run"); p.add_argument("name"); p.add_argument("--rounds", type=int, default=10)
    p.add_argument("--workers", type=int)
    p = sub.add_parser("status"); p.add_argument("name", nargs="?")
    p = sub.add_parser("stop"); p.add_argument("name")
    a = ap.parse_args(argv)
    ctx = {"human": True, "agent": os.environ.get("USERNAME") or os.environ.get("USER") or "person"}
    base = {"ws": a.ws} if a.ws else {}

    def call(op, **kw):
        r = S.handle({"op": op, "a": dict(base, **kw)}, ctx)
        if not r.get("ok"):
            print(S.say(r))
            sys.exit(1)
        return r["r"]
    if a.cmd == "start":
        targets = {}
        for t in a.target:
            k, _, v = t.partition("=")
            val, _, w = v.partition(":")
            targets[k] = [float(val), float(w or 1)]
        free = {}
        for f in a.free:
            k, _, v = f.partition("=")
            lo, _, hi = v.partition(":")
            free[k] = [float(lo), float(hi)]
        r = call("evolve.start", name=a.name, t=a.track, targets=targets, free=free, budget=a.budget, pop=a.pop,
                 seeds=a.seeds)
        print(f"study {a.name} started on track {a.track}: {r['hidden_seeds']} hidden seeds, budget {r['budget']}")
    elif a.cmd == "run":
        for _ in range(a.rounds):
            r = S.handle({"op": "evolve.step", "a": dict(base, name=a.name, workers=a.workers)}, ctx)
            if not r.get("ok"):
                print(S.say(r))
                break
            r = r["r"]
            line = f"round {r['round']}: {r['scored']} scored in {r.get('seconds', 0)}s, best {r.get('best_this_round')}"
            if r.get("champion"):
                ch = r["champion"]
                line += f"; NEW CHAMPION {ch['id']} by {ch['by']}, distance to targets {ch['loss']:.4g}"
            if r.get("overfit_refused"):
                line += f"; refused as overfit: {r['overfit_refused']}"
            print(line)
    elif a.cmd == "status":
        r = call("evolve.status", **({"name": a.name} if a.name else {}))
        print(json.dumps(r, indent=1))
    elif a.cmd == "stop":
        call("evolve.stop", name=a.name)
        print(f"study {a.name} stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
