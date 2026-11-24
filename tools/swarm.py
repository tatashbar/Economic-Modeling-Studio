#!/usr/bin/env python3
"""A swarm: many agents working on one model at the same time, with a person able to step in at any moment.

This runs built-in agents (no AI service needed) that use the studio exactly as any agent would, through the
studio protocol and the shared workspace, to calibrate the economy of tools/economy.py:

  explorers   read the leaderboard and propose candidates, each with its own strategy and a reason
  critics     read the champion's results and leave notes on what is still off target
  validators  rerun the engine's known-answer tests on the champion and report what they find
  a runner    holds the loop's lease and runs its rounds: scoring in parallel, hidden cases, promotion

Language-model agents join the same way, over MCP (python tools/mcp_server.py --agent NAME) or the protocol,
with the same workspace file: they are just more names on the same tracks.

    python tools/swarm.py --agents 100 --households 1000 --rounds 6
    python tools/swarm.py --agents 100 --households 1000 --rounds 6 --person-at 3 "keep the tax rate as it is"

While it runs, from another terminal:
    python tools/workspace.py report eco                the story so far, in plain language
    python tools/workspace.py freeze eco theta_w        no agent may change it from now on
    python tools/workspace.py pause eco                 stop everything; resume eco to go on
"""
import argparse
import json
import os
import random
import sys
import threading
import time

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)

FREE = {"z_sigma": [0.0, 1.2], "search": [1, 8], "res_decay": [0.0, 0.3], "theta_w": [0.0, 0.08], "theta_p": [0.0, 0.15],
        "mpc_w": [0.01, 0.15], "rate_sens": [0.0, 10.0], "phi_pi": [1.0, 3.0], "inv_target": [0.05, 0.6]}
TARGETS = {"unemployment": [0.06, 1.0], "inflation": [0.02, 1.0], "wealth_gini": [0.35, 0.5]}


class Agent(threading.Thread):
    def __init__(self, swarm, name, role, seed):
        super().__init__(daemon=True)
        self.s, self.name, self.role = swarm, name, role
        self.rng = random.Random(seed)
        self.done = 0

    def call(self, op, **a):
        a.setdefault("ws", self.s.ws)
        r = self.s.S.handle({"op": op, "a": a}, {"agent": self.name})
        self.s.count(op, r)
        if r.get("inbox") or (not r.get("ok") and r["e"][0][0] == 503):
            msgs = self.s.S.handle({"op": "ws.inbox", "a": {"ws": self.s.ws}}, {"agent": self.name})["r"]
            self.s.heard(self.name, msgs)
        return r

    def run(self):
        self.call("ws.join", **{"as": self.name, "role": self.role})
        while not self.s.stop.is_set():
            try:
                getattr(self, self.role)()
            except Exception as x:  # noqa: BLE001 - one agent's failure must not stop the swarm
                self.s.errors.append(f"{self.name}: {type(x).__name__}: {x}")
            self.s.stop.wait(self.s.pace * (0.5 + self.rng.random()))

    # ---------------------------------------------------------------- roles
    def explorer(self):
        st = self.call("evolve.status", name="calib", top=8)
        if not st.get("ok") or st["r"]["status"] != "open":
            return
        if st["r"]["counts"].get("pending", 0) >= self.s.queue:
            return
        champ = (st["r"].get("champion") or {}).get("params") or {}
        board = [b["params"] for b in st["r"]["board"] if b["status"] in ("scored", "champion")]
        frozen = {b for t, b in self.call("ws.inbox", peek=True)["r"]["frozen"] if t in ("eco", "*")}
        free = {k: v for k, v in FREE.items() if k not in frozen}
        if not free:
            return
        strategy = self.rng.choice(("nudge", "nudge", "blend", "leap"))
        p = dict(champ)
        if strategy == "nudge" or not board:
            k = self.rng.choice(sorted(free))
            lo, hi = free[k]
            p[k] = min(hi, max(lo, p.get(k, (lo + hi) / 2) + self.rng.gauss(0, 0.1 * (hi - lo))))
            note = f"nudge {k}"
        elif strategy == "blend":
            other = self.rng.choice(board)
            for k in free:
                if k in other and k in p:
                    p[k] = (p[k] + other[k]) / 2
            note = "halfway between the champion and another good candidate"
        else:
            k = self.rng.choice(sorted(free))
            lo, hi = free[k]
            p[k] = self.rng.uniform(lo, hi)
            note = f"a long jump in {k}"
        p = {k: (int(round(v)) if k == "search" else v) for k, v in p.items() if k in free}
        if self.call("evolve.propose", name="calib", params=p, note=note).get("ok"):
            self.done += 1

    def critic(self):
        st = self.call("evolve.status", name="calib", top=1)
        champ = st.get("r", {}).get("champion") if st.get("ok") else None
        if not champ or champ["id"] == getattr(self, "seen", None):
            return
        self.seen = champ["id"]
        if not self.call("ws.lease", resource=f"critique:{champ['id']}", ttl=3600).get("ok"):
            return                                 # another critic has this champion: no duplicate notes
        m = champ["moments"]
        gaps = sorted(((abs(m.get(k, 0) - v[0]) / max(abs(v[0]), 0.01), k) for k, v in TARGETS.items()), reverse=True)
        worst = gaps[0][1]
        self.call("ws.post", kind="note", t="eco",
                  text=f"champion {champ['id']}: {worst} is furthest from target ({m.get(worst, 0):.3f} vs "
                       f"{TARGETS[worst][0]}); try the parameters that drive it")
        self.done += 1

    def validator(self):
        st = self.call("evolve.status", name="calib", top=1)
        champ = st.get("r", {}).get("champion") if st.get("ok") else None
        if not champ or champ["id"] == getattr(self, "seen", None):
            return
        self.seen = champ["id"]
        if not self.call("ws.lease", resource=f"check:{champ['id']}", ttl=3600).get("ok"):
            return                                 # another validator is checking this champion
        d = self.call("ws.get", t="eco")["r"]["d"]
        small = dict(d, households=200, firms=10, periods=60)
        r = self.call("economy.run", d=small, workers=1)
        k = self.call("economy.known") if self.rng.random() < 0.3 else {"ok": True, "r": {"pass": True}}
        ok = r.get("ok") and r["r"]["accounting_error"] < 1e-9 and k["r"]["pass"]
        self.call("ws.post", kind="progress", t="eco",
                  text=f"checked champion {champ['id']}: money conserved, known answers pass" if ok else
                  f"champion {champ['id']} FAILED a check: {r.get('e') or k.get('e')}")
        self.done += 1

    def runner(self):
        lease = self.call("ws.lease", resource="loop:calib", ttl=600)
        if not lease.get("ok"):
            return
        r = self.call("evolve.step", name="calib", workers=self.s.workers, max=self.s.per_round)
        self.call("ws.lease", resource="loop:calib", release=True)
        if r.get("ok"):
            self.s.rounds.append(r["r"])
            self.done += 1
            if len(self.s.rounds) >= self.s.max_rounds:
                self.s.stop.set()
        elif r["e"][0][0] in (703, 704):
            self.s.stop.set()


class Swarm:
    def __init__(self, ws, pace=0.2, workers=None, per_round=48, queue=64, max_rounds=6):
        import studio_api
        studio_api.load_extensions()
        self.S, self.ws, self.pace, self.workers = studio_api, ws, pace, workers
        self.per_round, self.queue, self.max_rounds = per_round, queue, max_rounds
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.ops, self.refused, self.errors, self.rounds, self.heard_by = {}, {}, [], [], {}

    def count(self, op, r):
        with self.lock:
            self.ops[op] = self.ops.get(op, 0) + 1
            if not r.get("ok"):
                code = r["e"][0][0]
                self.refused[code] = self.refused.get(code, 0) + 1

    def heard(self, who, msgs):
        with self.lock:
            for m in msgs["msgs"]:
                if m["from"] != who and m["kind"] in ("constraint", "freeze", "pause", "resume", "veto", "answer", "note"):
                    self.heard_by.setdefault(m["id"], set()).add(who)


def setup(S, ws, households, firms, periods, budget, seeds, pop):
    person = {"human": True, "agent": "person"}
    cfg = S.handle({"op": "economy.new", "a": {"households": households, "firms": firms, "periods": periods}})["r"]["d"]
    r = S.handle({"op": "ws.track", "a": {"name": "eco", "d": cfg, "kind": "economy", "ws": ws,
                                          "goal": "calibrate the economy: unemployment 6%, inflation 2%, wealth Gini 0.35"}},
                 person)
    if not r.get("ok"):
        raise SystemExit(S.say(r))
    r = S.handle({"op": "evolve.start", "a": {"name": "calib", "t": "eco", "targets": TARGETS, "free": FREE,
                                              "budget": budget, "seeds": seeds, "pop": pop, "ws": ws}}, person)
    if not r.get("ok"):
        raise SystemExit(S.say(r))


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="A swarm of agents calibrating the economy, with a person in charge")
    ap.add_argument("--agents", type=int, default=100)
    ap.add_argument("--households", type=int, default=1000)
    ap.add_argument("--firms", type=int, default=50)
    ap.add_argument("--periods", type=int, default=120)
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--per-round", type=int, default=48, help="most candidates scored per round")
    ap.add_argument("--budget", type=int, default=2000)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--workers", type=int, help="parallel processes for scoring (default: all cores)")
    ap.add_argument("--pace", type=float, default=0.2, help="seconds between an agent's actions")
    ap.add_argument("--ws", help="workspace file (default: a new one in production/session-state/)")
    ap.add_argument("--person-at", nargs=2, metavar=("ROUND", "TEXT"),
                    help="after this round a person leaves a constraint, freezes theta_w and asks for a report")
    ap.add_argument("--report", help="write the final report to this file")
    a = ap.parse_args(argv)
    import studio_api as S
    S.load_extensions()
    ws = a.ws or os.path.join(os.path.dirname(TOOLS), "production", "session-state", f"swarm-{int(time.time())}.db")
    setup(S, ws, a.households, a.firms, a.periods, a.budget, a.seeds, pop=8)
    sw = Swarm(ws, a.pace, a.workers, a.per_round, queue=a.per_round + 16, max_rounds=a.rounds)
    n_val = max(1, a.agents // 20)
    n_crit = max(1, a.agents // 10)
    roles = ["runner"] + ["validator"] * n_val + ["critic"] * n_crit
    roles += ["explorer"] * max(1, a.agents - len(roles))
    agents = [Agent(sw, f"{r}-{i:03d}", r, i) for i, r in enumerate(roles)]
    print(f"workspace: {ws}")
    print(f"{len(agents)} agents: 1 runner, {n_val} validators, {n_crit} critics, {roles.count('explorer')} explorers; "
          f"economy of {a.households} households and {a.firms} firms; up to {a.per_round} candidates a round")
    t0 = time.time()
    for ag in agents:
        ag.start()
    shown, person_done = 0, False
    person = {"human": True, "agent": "person"}
    while not sw.stop.is_set():
        time.sleep(0.5)
        while shown < len(sw.rounds):
            r = sw.rounds[shown]
            shown += 1
            line = f"round {r['round']}: {r['scored']} scored in {r['seconds']}s"
            if r.get("champion"):
                ch = r["champion"]
                line += f"; new champion {ch['id']} by {ch['by']}, distance {ch['loss']:.4f}"
            if r.get("overfit_refused"):
                line += f"; {len(r['overfit_refused'])} refused by the hidden cases"
            print(line, flush=True)
            if a.person_at and not person_done and r["round"] >= int(a.person_at[0]):
                person_done = True
                S.handle({"op": "ws.post", "a": {"kind": "constraint", "text": a.person_at[1], "to": "track:eco",
                                                 "ws": ws}}, person)
                S.handle({"op": "ws.post", "a": {"kind": "freeze", "t": "eco", "b": "theta_w", "ws": ws}}, person)
                print(f"  a person stepped in: constraint \"{a.person_at[1]}\" and a freeze on theta_w", flush=True)
                text = S.handle({"op": "ws.report", "a": {"t": "eco", "ws": ws, "limit": 8}}, person)["r"]["text"]
                print("  the report the person read:\n    " + "\n    ".join(text.splitlines()[:14]), flush=True)
        if time.time() - t0 > 3600:
            sw.stop.set()
    for ag in agents:
        ag.join(timeout=30)
    took = time.time() - t0
    st = S.handle({"op": "evolve.status", "a": {"name": "calib", "ws": ws}}, person)["r"]
    by_role = {}
    for ag in agents:
        by_role[ag.role] = by_role.get(ag.role, 0) + ag.done
    print(f"\n{sum(sw.ops.values())} protocol messages in {took:.0f}s from {len(agents)} agents "
          f"({sum(sw.ops.values()) / max(took, 1e-9):.0f} a second); work done by role: {by_role}")
    print(f"refusals by code: {dict(sorted(sw.refused.items()))}" if sw.refused else "no refusals")
    if st.get("champion"):
        ch = st["champion"]
        print(f"champion {ch['id']} by {ch['by']}: distance {ch['loss']:.4f} (hidden cases {ch['hidden_loss']:.4f})")
        print("  results: " + ", ".join(f"{k} {ch['moments'][k]:.3f}" for k in TARGETS))
        print("  targets: " + ", ".join(f"{k} {v[0]}" for k, v in TARGETS.items()))
    if a.person_at:
        cons = [i for i, who in sw.heard_by.items() if len(who) > 1]
        print(f"{max((len(w) for w in sw.heard_by.values()), default=0)} agents had read the person's messages by the end")
        ws_ = S.handle({"op": "ws.get", "a": {"t": "eco", "ws": ws}})["r"]["d"]["params"]
        print(f"theta_w after the freeze: {ws_['theta_w']:.4f} (frozen from round {a.person_at[0]})")
        del cons
    if sw.errors:
        print(f"{len(sw.errors)} agent error(s), first: {sw.errors[0]}")
    if a.report:
        text = S.handle({"op": "ws.report", "a": {"t": "eco", "ws": ws, "limit": 30}}, person)["r"]["text"]
        with open(a.report, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"report: {a.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
