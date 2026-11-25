"""AEL: known answers, the default economy across seeds, entities, and scale timings."""
import statistics
import time

from common import TOOLS, run_dir, save, log  # noqa: F401
import economy

SEEDS = list(range(1, 9))


def summarize(results):
    keys = results[0]["moments"].keys()
    return {k: {"mean": statistics.mean(r["moments"][k] for r in results),
                "sd": statistics.stdev(r["moments"][k] for r in results)} for k in keys}


def main():
    started = time.strftime("%Y-%m-%d %H:%M:%S")
    d = run_dir("ael-baseline")
    known = [{"test": n, "pass": ok, "detail": det} for n, ok, det in economy.known_answers()]
    save(d, "known-answers.json", known)

    base = [economy.default_config(1000, 50, 200, s) for s in SEEDS]
    res = economy.run_many(base)
    out = {"config": {"households": 1000, "firms": 50, "periods": 200, "burn": base[0]["burn"], "seeds": SEEDS},
           "moments": summarize(res), "max_accounting_error": max(r["accounting_error"] for r in res)}

    ent = []
    for s in SEEDS:
        c = economy.default_config(1000, 50, 200, s)
        c["entities"] = [{"type": "foreign"}, {"type": "pension_fund", "count": 3}]
        ent.append(c)
    res_e = economy.run_many(ent)
    out["with_entities"] = {"entities": "foreign + 3 pension funds", "moments": summarize(res_e),
                            "max_accounting_error": max(r["accounting_error"] for r in res_e),
                            "entity_summary_seed1": res_e[0].get("entities")}
    save(d, "baseline.json", out)

    scale = []
    for hh, firms in [(1000, 50), (10000, 1000), (100000, 1000)]:
        c = economy.default_config(hh, firms, 200, 1)
        t0 = time.time()
        r = economy.run(c)
        scale.append({"households": hh, "firms": firms, "periods": 200, "seconds": round(time.time() - t0, 2),
                      "accounting_error": r["accounting_error"], "unemployment": r["moments"]["unemployment"],
                      "inflation": r["moments"]["inflation"]})
        print(scale[-1], flush=True)
    save(d, "scale.json", scale)
    log(d, started)
    print("known answers:", all(k["pass"] for k in known))
    print(out["moments"])


if __name__ == "__main__":
    main()
