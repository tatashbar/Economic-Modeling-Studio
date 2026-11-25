"""RSIM: the improvement loop (tools/evolve.py) calibrating the AEL economy, against a random-search benchmark with the
same budget of model runs. Both champions are then re-scored on test seeds that neither procedure saw.

    python rsim_vs_random.py --reps 3 --budget 400
"""
import argparse
import os
import random
import time

from common import run_dir, save, log
import economy
import evolve
import studio_api as S

S.load_extensions()
FREE = {"z_sigma": [0.0, 1.2], "search": [1, 8], "res_decay": [0.0, 0.3], "theta_w": [0.0, 0.08],
        "theta_p": [0.0, 0.15], "mpc_w": [0.01, 0.15], "rate_sens": [0.0, 10.0], "phi_pi": [1.0, 3.0],
        "inv_target": [0.05, 0.6]}
TARGETS = {"unemployment": [0.06, 1.0], "inflation": [0.02, 1.0], "wealth_gini": [0.35, 0.5]}
TRAIN = [1, 2]
TEST = list(range(101, 109))
HH, FIRMS, PERIODS = 1000, 50, 200
PERSON = {"human": True, "agent": "paper-author"}


def loss_of(params, seeds):
    cfgs = []
    for s in seeds:
        c = economy.default_config(HH, FIRMS, PERIODS, s)
        c["params"].update(params)
        cfgs.append(c)
    runs = economy.run_many(cfgs)
    m = economy.average(runs)
    return evolve._loss(m, {k: tuple(v) for k, v in TARGETS.items()}), m, max(r["accounting_error"] for r in runs)


def rsim(rep, budget, pop, wsfile):
    cfg = economy.default_config(HH, FIRMS, PERIODS, 1)
    r = S.handle({"op": "ws.track", "a": {"name": f"eco{rep}", "d": cfg, "kind": "economy", "ws": wsfile,
                                          "goal": "calibrate to targets"}}, PERSON)
    assert r["ok"], r
    r = S.handle({"op": "evolve.start", "a": {"name": f"calib{rep}", "t": f"eco{rep}", "targets": TARGETS, "free": FREE,
                                              "budget": budget, "seeds": TRAIN, "pop": pop, "ws": wsfile}}, PERSON)
    assert r["ok"], r
    rounds = []
    while True:
        r = S.handle({"op": "evolve.step", "a": {"name": f"calib{rep}", "ws": wsfile}}, PERSON)
        if not r["ok"]:
            break
        x = r["r"]
        st = S.handle({"op": "evolve.status", "a": {"name": f"calib{rep}", "ws": wsfile}}, PERSON)["r"]
        rounds.append({"round": x["round"], "scored": x["scored"], "best_this_round": x.get("best_this_round"),
                       "overfit_refused": len(x.get("overfit_refused", [])), "new_champion": bool(x.get("champion")),
                       "champion_loss": (st["champion"] or {}).get("loss"), "evals": st["evals"]})
        print(f"  rsim rep {rep} round {x['round']}: champion {rounds[-1]['champion_loss']}, evals {st['evals']}",
              flush=True)
    st = S.handle({"op": "evolve.status", "a": {"name": f"calib{rep}", "ws": wsfile}}, PERSON)["r"]
    return {"rounds": rounds, "champion": st["champion"], "counts": st["counts"], "evals": st["evals"]}


def random_search(rep, budget):
    rng = random.Random(1000 + rep)
    n = budget // len(TRAIN)
    best, path = None, []
    start = {k: economy.PARAMS[k][0] for k in FREE}
    cands = [start] + [{k: (rng.randint(int(lo), int(hi)) if k == "search" else rng.uniform(lo, hi))
                        for k, (lo, hi) in FREE.items()} for _ in range(n - 1)]
    targets = {k: tuple(v) for k, v in TARGETS.items()}
    chunk = 16                                          # same scores as one-by-one; batched only for speed
    for start_i in range(0, len(cands), chunk):
        batch = cands[start_i:start_i + chunk]
        cfgs = []
        for p in batch:
            for s in TRAIN:
                c = economy.default_config(HH, FIRMS, PERIODS, s)
                c["params"].update(p)
                cfgs.append(c)
        runs = economy.run_many(cfgs)
        for j, p in enumerate(batch):
            rr = runs[j * len(TRAIN):(j + 1) * len(TRAIN)]
            m = economy.average(rr)
            loss = evolve._loss(m, targets)
            if best is None or loss < best[0]:
                best = (loss, p, m)
        path.append({"evals": (start_i + len(batch)) * len(TRAIN), "best_loss": best[0]})
    print(f"  random rep {rep}: best training loss {best[0]:.4g}", flush=True)
    return {"best_loss": best[0], "params": best[1], "moments": best[2], "path": path}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--budget", type=int, default=400)
    ap.add_argument("--pop", type=int, default=16)
    a = ap.parse_args()
    started = time.strftime("%Y-%m-%d %H:%M:%S")
    d = run_dir("rsim")
    wsfile = os.path.join(d, "workspace.db")
    if os.path.exists(wsfile):
        os.remove(wsfile)
    start = {k: economy.PARAMS[k][0] for k in FREE}
    out = {"targets": TARGETS, "free": FREE, "train_seeds": TRAIN, "test_seeds": TEST, "budget": a.budget,
           "economy": {"households": HH, "firms": FIRMS, "periods": PERIODS}}
    l0, m0, _ = loss_of(start, TEST)
    out["default_on_test"] = {"loss": l0, "moments": m0}
    reps = []
    for rep in range(1, a.reps + 1):
        t0 = time.time()
        rs = rsim(rep, a.budget, a.pop, wsfile)
        t1 = time.time()
        rd = random_search(rep, a.budget)
        t2 = time.time()
        rl, rm, rerr = loss_of(rs["champion"]["params"], TEST)
        bl, bm, berr = loss_of(rd["params"], TEST)
        reps.append({"rep": rep, "rsim": rs, "random": rd, "rsim_seconds": round(t1 - t0, 1),
                     "random_seconds": round(t2 - t1, 1),
                     "test": {"rsim": {"loss": rl, "moments": rm, "acc_err": rerr},
                              "random": {"loss": bl, "moments": bm, "acc_err": berr}}})
        print(f"rep {rep}: TEST loss rsim {rl:.4g} vs random {bl:.4g} (default {l0:.4g})", flush=True)
        save(d, "rsim-vs-random.json", dict(out, reps=reps))
    # hidden seeds are drawn by the studio at random; a person may read them afterwards for the record
    import sqlite3
    c = sqlite3.connect(wsfile)
    out["hidden_seeds_record"] = {r[0]: r[1] for r in c.execute("SELECT name, hidden FROM studies")}
    out["reps"] = reps
    save(d, "rsim-vs-random.json", out)
    log(d, started, {"reps": a.reps, "budget": a.budget, "pop": a.pop})


if __name__ == "__main__":
    main()
