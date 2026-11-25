"""AEL policy experiments on the economy calibrated by RSIM (replication 1 champion), with common random numbers:
each scenario is run on the same seeds as its baseline, and responses are scenario minus baseline, averaged over seeds.

S1  fiscal expansion: government purchases share +3 points from period T0, under the default policy rule
S2  the same expansion when the policy rule is replaced by strict inflation targeting (rule swapped, no code)
S3  a larger expansion (+6 points), with and without a debt brake written as a parameter rule
"""
import json
import os
import statistics
import time

from common import OUT, run_dir, save, log
import economy

SEEDS = list(range(201, 217))
HH, FIRMS, PERIODS, T0 = 1000, 50, 240, 160
STRICT = "max(0, rstar + pistar + 3.0 * (pi - pistar))"
BRAKE = {"surcharge": "0.05 if debt > 0.9 else 0", "tau": "0.22 + surcharge"}
HORIZONS = [0, 4, 8, 20, 40, 79]


def champion():
    p = os.path.join(OUT, "rsim", "rsim-vs-random.json")
    with open(p, encoding="utf-8") as f:
        res = json.load(f)
    return res["reps"][0]["rsim"]["champion"]["params"]


def cfgs(params, rules=None, param_rules=None, shocks=None, checks=None):
    out = []
    for s in SEEDS:
        c = economy.default_config(HH, FIRMS, PERIODS, s)
        c["params"].update(params)
        if rules:
            c["rules"] = dict(rules)
        if param_rules:
            c["param_rules"] = dict(param_rules)
        if shocks:
            c["shocks"] = list(shocks)
        if checks:
            c["checks"] = dict(checks)
        out.append(c)
    return out


def series(runs):
    keys = ["u", "pi", "rate", "debt_gdp"]
    res = {}
    for k in keys:
        res[k] = [[x for x in r["series"][k]] for r in runs]
    # the engine's "gdp" series is real output (units sold); nominal output is gdp * pbar
    res["real_gdp"] = [[g for g in r["series"]["gdp"]] for r in runs]
    return res


def irf(base, scen):
    out = {}
    for k in base:
        diffs = []
        for b, s in zip(base[k], scen[k]):
            diffs.append([(y - x) if (x is not None and y is not None) else None for x, y in zip(b, s)])
        T = len(diffs[0])
        path, sd = [], []
        for t in range(T):
            v = [dd[t] for dd in diffs if dd[t] is not None]
            if k == "real_gdp":
                bv = [bb[t] for bb in base[k] if bb[t]]
                v = [100 * x / statistics.mean(bv) for x in v]       # percent of baseline level
            path.append(statistics.mean(v) if v else None)
            sd.append(statistics.stdev(v) / len(v) ** 0.5 if len(v) > 1 else None)
        out[k] = {"mean": path, "se": sd}
    return out


def at(resp, start):
    return {k: {h: {"mean": v["mean"][start + h], "se": v["se"][start + h]} for h in HORIZONS
                if start + h < len(v["mean"])} for k, v in resp.items()}


def main():
    started = time.strftime("%Y-%m-%d %H:%M:%S")
    d = run_dir("ael-policy")
    P = champion()
    g0 = economy.PARAMS["g_share"][0]
    shock3 = [{"param": "g_share", "value": g0 + 0.03, "at": T0}]
    shock6 = [{"param": "g_share", "value": g0 + 0.06, "at": T0}]
    checks = {"unemployment below 15%": "u < 0.15"}
    runs = {}
    plan = {"base": cfgs(P, checks=checks), "s1": cfgs(P, shocks=shock3, checks=checks),
            "base_strict": cfgs(P, rules={"policy": STRICT}), "s2": cfgs(P, rules={"policy": STRICT}, shocks=shock3),
            "s3_nobrake": cfgs(P, shocks=shock6), "base_brake": cfgs(P, param_rules=BRAKE),
            "s3_brake": cfgs(P, param_rules=BRAKE, shocks=shock6)}
    for k, c in plan.items():
        t0 = time.time()
        runs[k] = economy.run_many(c, series=True)
        print(k, round(time.time() - t0, 1), "s", flush=True)
    S = {k: series(v) for k, v in runs.items()}
    # the series include the burn-in; find the index of period T0 in the recorded series
    n = len(S["base"]["u"][0])
    start = T0 - (PERIODS - n)
    out = {"champion_params": P, "seeds": SEEDS, "periods": PERIODS, "shock_period": T0, "series_length": n,
           "series_start_index_of_shock": start, "strict_rule": STRICT, "brake": BRAKE,
           "max_accounting_error": max(r["accounting_error"] for v in runs.values() for r in v),
           "baseline_moments": economy.average(runs["base"]),
           "checks_seed1": runs["base"][0].get("checks"),
           "irf": {"s1_default_rule": irf(S["base"], S["s1"]), "s2_strict_rule": irf(S["base_strict"], S["s2"]),
                   "s3_no_brake": irf(S["base"], S["s3_nobrake"]), "s3_brake": irf(S["base"], S["s3_brake"])}}
    out["table"] = {k: at(v, start) for k, v in out["irf"].items()}
    # paths (levels) of debt and tax-relevant states for the brake case, averaged over seeds
    out["levels"] = {k: {s: [statistics.mean(x[t] for x in S[k][s] if x[t] is not None) for t in range(n)]
                         for s in ("debt_gdp", "u", "pi", "rate")} for k in ("base", "s3_nobrake", "s3_brake")}
    out["param_rule_paths_seed1"] = {k: v for k, v in runs["s3_brake"][0]["series"].items() if k in ("param:surcharge", "param:tau")}
    out["share_periods_brake_on"] = statistics.mean(
        sum(1 for x in r["series"]["param:surcharge"][T0:] if x and x > 0) / (PERIODS - T0) for r in runs["s3_brake"])
    save(d, "policy.json", out)
    log(d, started)
    print(json.dumps(out["table"], indent=0)[:3000])


if __name__ == "__main__":
    main()
