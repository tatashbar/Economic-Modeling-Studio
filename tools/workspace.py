#!/usr/bin/env python3
"""A shared workspace where many agents build models together and people can look in and steer at any time.

Agents work on TRACKS: named lines of work, each pointing at the current state of a model (a lego manifest, an
economy configuration, or any JSON). Every state is stored once by its fingerprint, every write is a
compare-and-swap on the track's head (so no write is ever lost or silently overwritten), and every operation is
logged. People read a plain-language report of any track at any moment, and post notes, constraints, freezes,
pauses and vetoes into an inbox that agents must read before they can write again.

Storage: one SQLite file (standard library), safe for many processes at once.
Default: production/session-state/workspace.db, or the STUDIO_WORKSPACE environment variable, or a.ws.

For people:
    python tools/workspace.py status                      tracks, agents, unread messages
    python tools/workspace.py report main                 what happened on a track, in plain language
    python tools/workspace.py note "keep the debt rule annual" [--to main]
    python tools/workspace.py constraint "no brick may remove the fiscal rule" [--to main]
    python tools/workspace.py freeze main fiscal-debt-rule     agents can no longer change that brick
    python tools/workspace.py pause main | resume main         stop and restart all writes on a track
    python tools/workspace.py veto main <event-seq> "reason"   roll the track back to the state before that event
    python tools/workspace.py answer <message-id> "text"       answer an agent's question
    python tools/workspace.py log [main] [--limit 50]

For agents: the ws.* operations of the studio protocol (tools/studio_api.py), and t=<track> wherever a model
is expected, for example {"op": "lego.attach", "a": {"t": "main", "brick": "trade-sector-armington", "apply": true}}.
"""
import argparse
import json
import os
import sqlite3
import sys
import threading
import time

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
DEFAULT_DB = os.path.join(ROOT, "production", "session-state", "workspace.db")
HUMAN_KINDS = ("constraint", "freeze", "unfreeze", "pause", "resume", "veto", "answer")
AGENT_KINDS = ("note", "question", "proposal", "progress")
READ_ONLY_OPS = ("hello", "ops", "explain", "say")

SCHEMA = """
CREATE TABLE IF NOT EXISTS objects (h TEXT PRIMARY KEY, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tracks (name TEXT PRIMARY KEY, head TEXT NOT NULL, parent TEXT, goal TEXT, kind TEXT,
    status TEXT NOT NULL DEFAULT 'open', score REAL, writes INTEGER NOT NULL DEFAULT 0, created REAL, by TEXT);
CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, agent TEXT, track TEXT, op TEXT,
    args TEXT, ok INTEGER, codes TEXT, before TEXT, after TEXT);
CREATE INDEX IF NOT EXISTS events_track ON events(track, seq);
CREATE TABLE IF NOT EXISTS agents (name TEXT PRIMARY KEY, role TEXT, joined REAL, seen REAL, cursor INTEGER DEFAULT 0,
    ops INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS inbox (id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, sender TEXT, target TEXT, kind TEXT,
    body TEXT, ref INTEGER);
CREATE TABLE IF NOT EXISTS freezes (track TEXT, brick TEXT, by TEXT, ts REAL, PRIMARY KEY (track, brick));
CREATE TABLE IF NOT EXISTS leases (resource TEXT PRIMARY KEY, agent TEXT, expires REAL);
"""

_local = threading.local()
API = None


def db_path(a=None):
    return (a or {}).get("ws") or os.environ.get("STUDIO_WORKSPACE") or DEFAULT_DB


def conn(path):
    cache = getattr(_local, "conns", None)
    if cache is None:
        cache = _local.conns = {}
    c = cache.get(path)
    if c is None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        c = sqlite3.connect(path, timeout=60, isolation_level=None, check_same_thread=False)
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA synchronous=NORMAL")
        c.execute("PRAGMA busy_timeout=60000")
        c.executescript(SCHEMA)
        cache[path] = c
    return c


class Tx:
    """BEGIN IMMEDIATE ... COMMIT, retried when the database is busy."""

    def __init__(self, c):
        self.c = c

    def __enter__(self):
        for i in range(200):
            try:
                self.c.execute("BEGIN IMMEDIATE")
                return self.c
            except sqlite3.OperationalError as x:
                if "locked" not in str(x) and "busy" not in str(x):
                    raise
                time.sleep(0.005 * (1 + i % 10))
        raise RuntimeError("the workspace is busy")

    def __exit__(self, kind, *_):
        self.c.execute("COMMIT" if kind is None else "ROLLBACK")
        return False


def _dump(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def put_object(c, doc):
    h = API.fingerprint(doc)
    c.execute("INSERT OR IGNORE INTO objects (h, body) VALUES (?, ?)", (h, _dump(doc)))
    return h


def get_object(c, h):
    row = c.execute("SELECT body FROM objects WHERE h = ?", (h,)).fetchone()
    if row is None:
        raise API.OpError(106, f"no stored state {h}")
    return json.loads(row[0])


def track_row(c, name):
    row = c.execute("SELECT name, head, parent, goal, kind, status, score, writes, created, by FROM tracks "
                    "WHERE name = ?", (name,)).fetchone()
    if row is None:
        raise API.OpError(106, f"no track '{name}' (ws.tracks lists them)")
    return dict(zip(("name", "head", "parent", "goal", "kind", "status", "score", "writes", "created", "by"), row))


def agent_of(a, ctx):
    return a.get("as") or ctx.get("agent") or ("person" if ctx.get("human") else "anonymous")


# ------------------------------------------------------------------ the track as a model source
def _track_source(a):
    path = db_path(a)
    c = conn(path)
    tr = track_row(c, a["t"])
    doc = get_object(c, tr["head"])
    src = API.Source(doc, f"track {a['t']}")
    head = tr["head"]

    def save(new, a2):
        if a2.get("base") and a2["base"] != head:
            raise API.OpError(219, f"track {a['t']} moved on from {a2['base']} (now {head})", data={"h": head})
        with Tx(c):
            h = put_object(c, new)
            cur = c.execute("UPDATE tracks SET head = ?, writes = writes + 1 WHERE name = ? AND head = ?",
                            (h, a["t"], head))
            if cur.rowcount != 1:
                now = c.execute("SELECT head FROM tracks WHERE name = ?", (a["t"],)).fetchone()[0]
                raise API.OpError(219, f"track {a['t']} changed while you worked (now {now}); read it and retry",
                                  data={"h": now})
        return {"saved": f"track {a['t']}", "h": h}
    src.saver = save
    return src


# ------------------------------------------------------------------ guards and the log
def _touches(op, a):
    """The bricks an operation would change, for freezes."""
    out = set()
    if a.get("b"):
        out.add(a["b"])
    br = a.get("brick")
    if isinstance(br, str):
        out.add(os.path.splitext(os.path.basename(br))[0].replace(".lego", ""))
    elif isinstance(br, dict) and br.get("id"):
        out.add(br["id"])
    return out


def _before(op, a, ctx):
    ctx.pop("_ws_before", None)
    if "t" not in a:
        return
    spec = API.ops.get(op) or {}
    if not spec.get("mutates") or not a.get("apply"):
        return
    c = conn(db_path(a))
    tr = track_row(c, a["t"])
    ctx["_ws_before"] = tr["head"]
    if tr["status"] == "paused":
        raise API.OpError(501, f"track {a['t']} is paused by a person; read your inbox (ws.inbox) and wait",
                          fix=[{"op": "ws.inbox", "a": {}}])
    if tr["status"] == "closed":
        raise API.OpError(501, f"track {a['t']} is closed")
    frozen = {r[0] for r in c.execute("SELECT brick FROM freezes WHERE track IN (?, '*')", (a["t"],))}
    hit = sorted(_touches(op, a) & frozen)
    if hit:
        raise API.OpError(502, f"frozen by a person on track {a['t']}: {', '.join(hit)}")
    who = agent_of(a, ctx)
    if not ctx.get("human"):
        row = c.execute("SELECT cursor FROM agents WHERE name = ?", (who,)).fetchone()
        cursor = row[0] if row else 0
        n = c.execute("SELECT COUNT(*) FROM inbox WHERE id > ? AND kind IN ('constraint', 'pause', 'veto', 'answer') "
                      "AND sender != ? AND target IN ('*', ?, ?)",
                      (cursor, who, f"track:{a['t']}", f"agent:{who}")).fetchone()[0]
        if n:
            raise API.OpError(503, f"{n} message(s) from a person wait in your inbox; read them (ws.inbox) first",
                              fix=[{"op": "ws.inbox", "a": {"as": who}}])


def _after(op, a, resp, ctx):
    spec = API.ops.get(op) or {}
    logged = spec.get("mutates") or op in ("ws.post", "ws.join")
    if not logged or ("t" not in a and not op.startswith("ws.") and not ctx.get("ws_log_all")):
        return
    track = a.get("t") or (a.get("name") if op == "ws.track" else None) or a.get("into")
    try:
        c = conn(db_path(a))
        who = agent_of(a, ctx)
        codes = [row[0] for row in (resp.get("e") or []) + (resp.get("w") or []) if row and isinstance(row[0], int)]
        small = {k: v for k, v in a.items() if k not in ("d", "ws", "as", "resp") and len(_dump(v)) < 400}
        r = resp.get("r") if isinstance(resp.get("r"), dict) else {}
        after = (r.get("h") or resp.get("h")) if r.get("applied") else None
        before = ctx.pop("_ws_before", None)
        with Tx(c):
            c.execute("INSERT INTO events (ts, agent, track, op, args, ok, codes, before, after) VALUES "
                      "(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (time.time(), who, track, op, _dump(small), int(bool(resp.get("ok"))), _dump(codes),
                       before, after))
            c.execute("INSERT INTO agents (name, role, joined, seen, ops) VALUES (?, '', ?, ?, 1) "
                      "ON CONFLICT(name) DO UPDATE SET seen = excluded.seen, ops = ops + 1", (who, time.time(), time.time()))
        if not ctx.get("human"):
            row = c.execute("SELECT cursor FROM agents WHERE name = ?", (who,)).fetchone()
            n = c.execute("SELECT COUNT(*) FROM inbox WHERE id > ? AND sender != ? AND target IN ('*', ?, ?)",
                          (row[0] if row else 0, who, f"track:{a.get('t')}", f"agent:{who}")).fetchone()[0]
            if n:
                resp["inbox"] = n
    except Exception:  # noqa: BLE001 - the log must never break an operation
        pass


# ------------------------------------------------------------------ operations
def register(api):
    global API
    API = api
    api.source("t", _track_source)
    api.hooks["before"].append(_before)
    api.hooks["after"].append(_after)
    api.code(501, "paused", "a person paused or closed this track")
    api.code(502, "frozen", "a person froze this brick on this track")
    api.code(503, "unread_from_person", "a person left messages you must read before writing")
    api.code(504, "lease_held", "another agent holds this lease")
    op, ok, E = api.op, api.ok, api.OpError
    WS = "str? workspace file (default: STUDIO_WORKSPACE or production/session-state/workspace.db)"
    AS = "str? your agent name"

    @op("ws.join", "join the workspace: your name, your role; returns the open tracks and your unread messages", {
        "as": "str your agent name, unique", "role": "str? builder, critic, validator, explorer, ...", "ws": WS})
    def join(a, ctx):
        c = conn(db_path(a))
        now = time.time()
        with Tx(c):
            c.execute("INSERT INTO agents (name, role, joined, seen) VALUES (?, ?, ?, ?) ON CONFLICT(name) DO UPDATE "
                      "SET role = excluded.role, seen = excluded.seen", (a["as"], a.get("role", ""), now, now))
        tracks = [r[0] for r in c.execute("SELECT name FROM tracks WHERE status != 'closed' ORDER BY name")]
        cur = c.execute("SELECT cursor FROM agents WHERE name = ?", (a["as"],)).fetchone()[0]
        unread = c.execute("SELECT COUNT(*) FROM inbox WHERE id > ? AND target IN ('*', ?)",
                           (cur, f"agent:{a['as']}")).fetchone()[0]
        return ok({"tracks": tracks, "unread": unread})

    @op("ws.track", "start a track from a manifest (m), an inline model (d) or another track (from)", {
        "name": "str new track name", "m": "str? manifest path", "d": "any? inline model or any JSON state",
        "from": "str? track to fork", "goal": "str? what this line of work is for",
        "kind": "str? lego, economy or json", "as": AS, "ws": WS}, mutates=True)
    def track(a, ctx):
        c = conn(db_path(a))
        parent = None
        if a.get("from"):
            src = track_row(c, a["from"])
            doc, parent, kind = get_object(c, src["head"]), a["from"], a.get("kind") or src["kind"]
        elif "d" in a:
            doc, kind = a["d"], a.get("kind") or ("lego" if isinstance(a["d"], dict) and "bricks" in a["d"] else "json")
        elif a.get("m"):
            doc, kind = api.resolve({"m": a["m"]}).doc, a.get("kind") or "lego"
        else:
            raise E(102, "give m, d or from")
        with Tx(c):
            if c.execute("SELECT 1 FROM tracks WHERE name = ?", (a["name"],)).fetchone():
                raise E(108, f"track '{a['name']}' exists")
            h = put_object(c, doc)
            c.execute("INSERT INTO tracks (name, head, parent, goal, kind, created, by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (a["name"], h, parent, a.get("goal", ""), kind, time.time(), agent_of(a, ctx)))
        return ok({"track": a["name"], "kind": kind, "h": h}, h=h)

    @op("ws.tracks", "every track: head fingerprint, status, kind, writes, score, goal", {"ws": WS})
    def tracks(a, ctx):
        c = conn(db_path(a))
        rows = c.execute("SELECT name, head, parent, goal, kind, status, score, writes FROM tracks ORDER BY name")
        return ok({r[0]: {"h": r[1], "parent": r[2], "goal": r[3], "kind": r[4], "status": r[5], "score": r[6],
                          "writes": r[7]} for r in rows})

    @op("ws.get", "the current state of a track, any kind", {"t": "str track", "ws": WS})
    def get(a, ctx):
        c = conn(db_path(a))
        tr = track_row(c, a["t"])
        return ok({"d": get_object(c, tr["head"]), "kind": tr["kind"], "status": tr["status"]}, h=tr["head"])

    @op("ws.put", "replace the state of a track (any JSON) if it is still at base", {
        "t": "str track", "d": "any the new state", "base": "str the fingerprint you read", "score": "num? a score",
        "as": AS, "ws": WS, "apply": "bool? must be true"}, mutates=True)
    def put(a, ctx):
        a = dict(a, apply=True)
        _before("ws.put", a, ctx)
        src = _track_source(a)
        res = src.save(a["d"], a)
        if a.get("score") is not None:
            c = conn(db_path(a))
            with Tx(c):
                c.execute("UPDATE tracks SET score = ? WHERE name = ?", (float(a["score"]), a["t"]))
        return ok(dict(res, applied=True), h=res["h"])

    @op("ws.promote", "make another track point at this track's state, if that track is still at base", {
        "t": "str track whose state is promoted", "into": "str track to move", "base": "str into's head you read",
        "as": AS, "ws": WS}, mutates=True)
    def promote(a, ctx):
        _before("ws.promote", dict(a, t=a["into"], apply=True), ctx)
        c = conn(db_path(a))
        src = track_row(c, a["t"])
        with Tx(c):
            cur = c.execute("UPDATE tracks SET head = ?, writes = writes + 1, score = ? WHERE name = ? AND head = ?",
                            (src["head"], src["score"], a["into"], a["base"]))
            if cur.rowcount != 1:
                raise E(219, f"track {a['into']} moved on; read it and retry")
        return ok({"into": a["into"], "h": src["head"], "applied": True}, h=src["head"])

    @op("ws.inbox", "your unread messages from people and agents; reading them marks them read", {
        "as": AS, "peek": "bool? do not mark them read", "ws": WS})
    def inbox(a, ctx):
        c = conn(db_path(a))
        who = agent_of(a, ctx)
        row = c.execute("SELECT cursor FROM agents WHERE name = ?", (who,)).fetchone()
        cur = row[0] if row else 0
        tracks_ = [r[0] for r in c.execute("SELECT name FROM tracks")]
        targets = ["*", f"agent:{who}"] + [f"track:{t}" for t in tracks_]
        rows = c.execute(f"SELECT id, ts, sender, target, kind, body, ref FROM inbox WHERE id > ? AND sender != ? AND "
                         f"target IN ({','.join('?' * len(targets))}) ORDER BY id", [cur, who] + targets).fetchall()
        msgs = [{"id": r[0], "from": r[2], "to": r[3], "kind": r[4], "text": r[5], **({"ref": r[6]} if r[6] else {})}
                for r in rows]
        if not a.get("peek"):
            last = c.execute("SELECT COALESCE(MAX(id), 0) FROM inbox").fetchone()[0]
            with Tx(c):
                c.execute("INSERT INTO agents (name, role, joined, seen, cursor) VALUES (?, '', ?, ?, ?) "
                          "ON CONFLICT(name) DO UPDATE SET cursor = excluded.cursor, seen = excluded.seen",
                          (who, time.time(), time.time(), last))
        frozen = [list(r) for r in c.execute("SELECT track, brick FROM freezes")]
        constraints = [r[0] for r in c.execute("SELECT body FROM inbox WHERE kind = 'constraint' ORDER BY id")]
        return ok({"msgs": msgs, "constraints": constraints, "frozen": frozen})

    @op("ws.post", "post a message: agents post note, question, proposal or progress; people also post constraint, "
        "freeze, unfreeze, pause, resume, veto and answer", {
            "kind": "str message kind", "text": "str? the message", "to": "str? * (everyone), track:NAME or agent:NAME",
            "t": "str? track (for freeze, pause, veto)", "b": "str? brick (for freeze)", "ref": "int? event or message id",
            "as": AS, "ws": WS})
    def post(a, ctx):
        kind = a["kind"]
        if kind not in HUMAN_KINDS + AGENT_KINDS:
            raise E(103, f"kind must be one of {', '.join(HUMAN_KINDS + AGENT_KINDS)}")
        if kind in HUMAN_KINDS and not ctx.get("human"):
            raise E(104, f"'{kind}' is for people; agents post {', '.join(AGENT_KINDS)}")
        c = conn(db_path(a))
        who = agent_of(a, ctx)
        target = a.get("to") or (f"track:{a['t']}" if a.get("t") else "*")
        result = {}
        with Tx(c):
            if kind in ("freeze", "unfreeze"):
                if not a.get("t") or not a.get("b"):
                    raise E(102, "freeze needs t and b ('*' for every track)")
                if kind == "freeze":
                    c.execute("INSERT OR REPLACE INTO freezes VALUES (?, ?, ?, ?)", (a["t"], a["b"], who, time.time()))
                else:
                    c.execute("DELETE FROM freezes WHERE track = ? AND brick = ?", (a["t"], a["b"]))
            elif kind in ("pause", "resume"):
                cur = c.execute("UPDATE tracks SET status = ? WHERE name = ?",
                                ("paused" if kind == "pause" else "open", a.get("t")))
                if cur.rowcount != 1:
                    raise E(106, f"no track '{a.get('t')}'")
            elif kind == "veto":
                row = c.execute("SELECT track, before, after FROM events WHERE seq = ?", (a.get("ref"),)).fetchone()
                if row is None or not row[0]:
                    raise E(106, f"no event {a.get('ref')} on a track")
                prior = row[1]
                if not prior:
                    raise E(108, f"event {a['ref']} has no earlier state to return to")
                c.execute("UPDATE tracks SET head = ?, writes = writes + 1 WHERE name = ?", (prior, row[0]))
                target = f"track:{row[0]}"
                result["restored"] = prior
            text = a.get("text") or {"freeze": f"{a.get('b')} is frozen on {a.get('t')}",
                                     "unfreeze": f"{a.get('b')} is no longer frozen on {a.get('t')}",
                                     "pause": f"track {a.get('t')} is paused", "resume": f"track {a.get('t')} resumed",
                                     "veto": f"event {a.get('ref')} was vetoed"}.get(kind, "")
            cur = c.execute("INSERT INTO inbox (ts, sender, target, kind, body, ref) VALUES (?, ?, ?, ?, ?, ?)",
                            (time.time(), who, target, kind, text, a.get("ref")))
            result["id"] = cur.lastrowid
        return ok(result)

    @op("ws.log", "the operations on a track (or all), newest last: [seq, time, agent, op, ok, codes, state]", {
        "t": "str? track", "since": "int? after this seq", "limit": "int? at most this many (default 200)",
        "agent": "str? only this agent", "ws": WS})
    def log(a, ctx):
        c = conn(db_path(a))
        q, args = "SELECT seq, ts, agent, track, op, args, ok, codes, after FROM events WHERE seq > ?", [a.get("since", 0)]
        if a.get("t"):
            q += " AND track = ?"
            args.append(a["t"])
        if a.get("agent"):
            q += " AND agent = ?"
            args.append(a["agent"])
        rows = c.execute(q + " ORDER BY seq DESC LIMIT ?", args + [int(a.get("limit", 200))]).fetchall()[::-1]
        return ok({"events": [[r[0], round(r[1], 3), r[2], r[4], r[6], json.loads(r[7] or "[]"), r[8]] for r in rows],
                   "last": rows[-1][0] if rows else a.get("since", 0)})

    @op("ws.lease", "take or renew a lease on a resource (a brick, a track, a task) for some seconds", {
        "resource": "str what to lease", "ttl": "num? seconds (default 60)", "release": "bool? give it back",
        "as": AS, "ws": WS})
    def lease(a, ctx):
        c = conn(db_path(a))
        who, now = agent_of(a, ctx), time.time()
        with Tx(c):
            row = c.execute("SELECT agent, expires FROM leases WHERE resource = ?", (a["resource"],)).fetchone()
            if a.get("release"):
                if row and row[0] == who:
                    c.execute("DELETE FROM leases WHERE resource = ?", (a["resource"],))
                return ok({"released": a["resource"]})
            if row and row[0] != who and row[1] > now:
                raise E(504, f"{a['resource']} is leased by {row[0]} for {row[1] - now:.0f}s more",
                        data={"holder": row[0], "expires_in": round(row[1] - now, 1)})
            c.execute("INSERT OR REPLACE INTO leases VALUES (?, ?, ?)", (a["resource"], who, now + float(a.get("ttl", 60))))
        return ok({"resource": a["resource"], "holder": who, "ttl": float(a.get("ttl", 60))})

    @op("ws.status", "tracks, agents and messages at a glance", {"ws": WS})
    def status(a, ctx):
        c = conn(db_path(a))
        tr = [dict(zip(("name", "status", "kind", "writes", "score"), r)) for r in
              c.execute("SELECT name, status, kind, writes, score FROM tracks ORDER BY name")]
        ag = [dict(zip(("name", "role", "ops", "seen"), r)) for r in
              c.execute("SELECT name, role, ops, seen FROM agents ORDER BY ops DESC")]
        ev = c.execute("SELECT COUNT(*), COALESCE(SUM(ok), 0) FROM events").fetchone()
        qs = [dict(zip(("id", "from", "text"), r)) for r in c.execute(
            "SELECT i.id, i.sender, i.body FROM inbox i WHERE i.kind = 'question' AND NOT EXISTS "
            "(SELECT 1 FROM inbox j WHERE j.kind = 'answer' AND j.ref = i.id) ORDER BY i.id")]
        return ok({"tracks": tr, "agents": len(ag), "top_agents": ag[:10], "events": ev[0], "ok_events": ev[1],
                   "open_questions": qs})

    @op("ws.report", "a plain-language report of a track for a person: goal, state, who did what, open questions", {
        "t": "str track", "since": "int? only events after this seq", "limit": "int? at most this many events (default 40)",
        "ws": WS})
    def report_op(a, ctx):
        return ok({"text": report(a)})

    return api


# ------------------------------------------------------------------ the report for people
VERBS = {"lego.attach": "added brick {brick}", "lego.detach": "took out brick {b}", "lego.swap": "swapped {b} for {brick}",
         "lego.patch": "changed {b} ({fields})", "lego.bridge": "declared the bridge of {b}",
         "lego.bridge_test": "ran the bridge tests", "lego.validate": "recorded validation of {b}",
         "ws.track": "started track {name}", "ws.put": "wrote a new state", "ws.promote": "promoted it into {into}",
         "ws.post": "posted a {kind}: {text}", "evolve.step": "ran a round of the improvement loop",
         "evolve.propose": "proposed a candidate", "economy.run": "ran the economy"}


def _sentence(op, args, ok, codes):
    CODES = API.codes
    try:
        a = json.loads(args or "{}")
    except ValueError:
        a = {}
    a.setdefault("fields", ", ".join(sorted((a.get("set") or {}).keys())))
    tmpl = VERBS.get(op, op)
    if op == "ws.post" and not a.get("text"):
        tmpl = {"freeze": "froze {b}", "unfreeze": "unfroze {b}", "pause": "paused the track",
                "resume": "resumed the track", "veto": "vetoed event {ref}"}.get(a.get("kind"), "posted a {kind}")
    class Blank(dict):
        def __missing__(self, key):
            return "?"
    try:
        text = tmpl.format_map(Blank({k: (v if not isinstance(v, (dict, list)) else "...") for k, v in a.items()}))
    except (KeyError, IndexError, ValueError):
        text = op
    mutating = op in VERBS and not op.startswith("ws.post")
    if mutating and op not in ("ws.track", "ws.put", "ws.promote") and not a.get("apply"):
        text = "planned (did not write): " + text
    if not ok:
        text += " - REFUSED"
    names = sorted({CODES.get(c, ("?",))[0].replace("_", " ") for c in codes})
    if names:
        text += f" [{'; '.join(names[:4])}{' ...' if len(names) > 4 else ''}]"
    return text


def report(a):
    c = conn(db_path(a))
    tr = track_row(c, a["t"])
    doc = get_object(c, tr["head"])
    lines = [f"# Track {tr['name']}", ""]
    if tr["goal"]:
        lines.append(f"Goal: {tr['goal']}")
    lines.append(f"Status: {tr['status']}. Kind: {tr['kind']}. Writes: {tr['writes']}. State: {tr['head']}"
                 + (f". Score: {tr['score']:.6g}" if tr["score"] is not None else "") +
                 (f". Forked from {tr['parent']}" if tr["parent"] else "") + ".")
    if tr["kind"] == "lego" and isinstance(doc, dict) and "bricks" in doc:
        import lego
        rep = lego.check(doc)
        att = [b["id"] for b in lego.attached(doc)]
        lines += ["", "## The model now",
                  f"{doc.get('name', '')}: {len(att)} bricks attached ({', '.join(att)}).",
                  f"{len(rep['errors'])} error(s), {len(rep['warnings'])} warning(s); "
                  f"{rep['validation'].get('validated', 0)} brick(s) validated, "
                  f"{rep.get('signoff', {}).get('approved', 0)} signed off."]
        for e in rep["errors"][:10]:
            lines.append(f"- Error: {e}")
        for w in rep["warnings"][:10]:
            lines.append(f"- Warning: {w}")
    elif tr["kind"] == "economy" and isinstance(doc, dict):
        lines += ["", "## The economy now",
                  f"{doc.get('households', '?')} households, {doc.get('firms', '?')} firms, "
                  f"{doc.get('periods', '?')} periods."]
        if doc.get("params"):
            lines.append("Parameters: " + ", ".join(f"{k} = {v:.4g}" if isinstance(v, (int, float)) else f"{k} = {v}"
                                                   for k, v in sorted(doc["params"].items())))
        if doc.get("moments"):
            lines.append("Last run: " + ", ".join(f"{k} {v:.4g}" for k, v in sorted(doc["moments"].items())
                                                  if isinstance(v, (int, float))))
    frozen = [r[0] for r in c.execute("SELECT brick FROM freezes WHERE track IN (?, '*')", (a["t"],))]
    constraints = [r[0] for r in c.execute(
        "SELECT body FROM inbox WHERE kind = 'constraint' AND target IN ('*', ?) ORDER BY id", (f"track:{a['t']}",))]
    if frozen or constraints:
        lines += ["", "## What people have set"]
        lines += [f"- Frozen: {b}" for b in frozen] + [f"- Constraint: {x}" for x in constraints]
    rows = c.execute("SELECT seq, ts, agent, op, args, ok, codes FROM events WHERE track = ? AND seq > ? "
                     "ORDER BY seq DESC LIMIT ?", (a["t"], int(a.get("since", 0)), int(a.get("limit", 40)))).fetchall()
    total = c.execute("SELECT COUNT(*), COUNT(DISTINCT agent), COALESCE(SUM(1 - ok), 0) FROM events WHERE track = ?",
                      (a["t"],)).fetchone()
    lines += ["", "## What happened",
              f"{total[0]} operation(s) by {total[1]} agent(s), {total[2]} refused. The latest, oldest first:"]
    for seq, ts, agent, op, args, ok, codes in rows[::-1]:
        lines.append(f"- [{seq}] {time.strftime('%H:%M:%S', time.localtime(ts))} {agent}: "
                     f"{_sentence(op, args, ok, json.loads(codes or '[]'))}")
    busiest = c.execute("SELECT agent, COUNT(*) FROM events WHERE track = ? GROUP BY agent ORDER BY 2 DESC LIMIT 5",
                        (a["t"],)).fetchall()
    if busiest:
        lines += ["", "Most active: " + ", ".join(f"{n} ({k})" for n, k in busiest) + "."]
    qs = c.execute("SELECT i.id, i.sender, i.body FROM inbox i WHERE i.kind IN ('question', 'proposal') AND "
                   "i.target IN ('*', ?) AND NOT EXISTS (SELECT 1 FROM inbox j WHERE j.kind = 'answer' AND j.ref = i.id) "
                   "ORDER BY i.id", (f"track:{a['t']}",)).fetchall()
    if qs:
        lines += ["", "## Waiting for a person"]
        lines += [f"- [{i}] {s} asks: {b}  (answer: python tools/workspace.py answer {i} \"...\")" for i, s, b in qs]
    return "\n".join(lines)


# ------------------------------------------------------------------ command line for people
def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, TOOLS)
    import studio_api as S
    S.load_extensions()
    ap = argparse.ArgumentParser(description="The shared workspace, for people")
    ap.add_argument("--ws", help="workspace file")
    ap.add_argument("--as", dest="who", default=os.environ.get("USERNAME") or os.environ.get("USER") or "person")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    p = sub.add_parser("report"); p.add_argument("track"); p.add_argument("--limit", type=int, default=40)
    p = sub.add_parser("log"); p.add_argument("track", nargs="?"); p.add_argument("--limit", type=int, default=50)
    for k in ("note", "constraint"):
        p = sub.add_parser(k); p.add_argument("text"); p.add_argument("--to", default="*")
    for k in ("pause", "resume"):
        p = sub.add_parser(k); p.add_argument("track")
    for k in ("freeze", "unfreeze"):
        p = sub.add_parser(k); p.add_argument("track"); p.add_argument("brick")
    p = sub.add_parser("veto"); p.add_argument("track"); p.add_argument("seq", type=int); p.add_argument("reason")
    p = sub.add_parser("answer"); p.add_argument("id", type=int); p.add_argument("text")
    p = sub.add_parser("track", help="start a track from a manifest"); p.add_argument("name"); p.add_argument("manifest")
    p.add_argument("--goal", default="")
    a = ap.parse_args(argv)
    ctx = {"human": True, "agent": a.who}
    base = {"ws": a.ws} if a.ws else {}

    def run(op, **kw):
        r = S.handle({"op": op, "a": dict(base, **kw)}, ctx)
        if not r.get("ok"):
            print(S.say(r))
            sys.exit(1)
        return r["r"]
    if a.cmd == "status":
        r = run("ws.status")
        for t in r["tracks"]:
            print(f"track {t['name']:<20} {t['status']:<7} {t['kind']:<8} writes {t['writes']:<6}"
                  + (f" score {t['score']:.6g}" if t["score"] is not None else ""))
        print(f"{r['agents']} agent(s); {r['events']} operation(s), {r['ok_events']} accepted")
        for q in r["open_questions"]:
            print(f"question [{q['id']}] from {q['from']}: {q['text']}")
    elif a.cmd == "report":
        print(run("ws.report", t=a.track, limit=a.limit)["text"])
    elif a.cmd == "log":
        r = run("ws.log", **({"t": a.track} if a.track else {}), limit=a.limit)
        for seq, ts, agent, op, ok, codes, h in r["events"]:
            print(f"{seq:>6} {time.strftime('%H:%M:%S', time.localtime(ts))} {agent:<16} {op:<18} "
                  f"{'ok' if ok else 'REFUSED'} {codes if codes else ''}")
    elif a.cmd in ("note", "constraint"):
        print(f"posted [{run('ws.post', kind=a.cmd, text=a.text, to=a.to)['id']}]")
    elif a.cmd in ("pause", "resume"):
        run("ws.post", kind=a.cmd, t=a.track)
        print(f"track {a.track}: {a.cmd}d")
    elif a.cmd in ("freeze", "unfreeze"):
        run("ws.post", kind=a.cmd, t=a.track, b=a.brick)
        print(f"{a.brick} on {a.track}: {a.cmd}d")
    elif a.cmd == "veto":
        r = run("ws.post", kind="veto", t=a.track, ref=a.seq, text=a.reason)
        print(f"track {a.track} is back at {r.get('restored')}")
    elif a.cmd == "answer":
        run("ws.post", kind="answer", ref=a.id, text=a.text)
        print("answered")
    elif a.cmd == "track":
        r = run("ws.track", name=a.name, m=a.manifest, goal=a.goal)
        print(f"track {a.name} started at {r['h']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
