"""Modular composition: check, change-impact plans for every catalog brick, a swap, a detach and the bridge sequence.
All operations go through the studio protocol (studio_api.handle) on inline models, so nothing in the repo is written."""
import copy
import glob
import json
import os
import time

from common import EMS, run_dir, save, log
import studio_api as S

S.load_extensions()
AGENT = {"agent": "paper-script"}


def call(op, **a):
    return S.handle({"op": op, "a": a}, AGENT)


def counts(r):
    return (r.get("r") or {}).get("n")


def main():
    started = time.strftime("%Y-%m-%d %H:%M:%S")
    d = run_dir("lego")
    with open(os.path.join(EMS, "lego/examples/small-open-economy.lego.json"), encoding="utf-8") as f:
        base = json.load(f)
    out = {"base_check": call("lego.check", d=base, detail=True),
           "base_text": call("lego.text", d=base)["r"]}
    attached = {b["id"] for b in base["bricks"] if b.get("status", "attached") != "detached"}

    sweep = []
    for path in sorted(glob.glob(os.path.join(EMS, "lego/catalog/*.json"))):
        bid = os.path.splitext(os.path.basename(path))[0]
        if bid in attached:
            continue
        t0 = time.perf_counter()
        r = call("lego.attach", d=copy.deepcopy(base), brick=bid)
        ms = (time.perf_counter() - t0) * 1000
        row = {"brick": bid, "ok": r.get("ok"), "ms": round(ms, 1)}
        if r.get("ok"):
            delta = r["r"].get("delta", {})
            row.update({"blocked": r["r"].get("blocked"), "n": r["r"].get("n"),
                        "new_joints": len(delta.get("+joints", [])), "stubs_retired": len(delta.get("-stubs", [])),
                        "stubs_activated": len(delta.get("+stubs", [])), "revalidate": delta.get("stale", []),
                        "findings": r.get("e") or r["r"].get("findings") or r["r"].get("errors"),
                        "warnings": r.get("w") or r["r"].get("warnings")})
        else:
            row["error"] = r.get("e")
        row["raw"] = r
        sweep.append(row)
        print(bid, row.get("blocked"), row.get("new_joints"), row.get("stubs_retired"), row.get("stubs_activated"),
              row.get("error"), flush=True)
    out["attach_sweep"] = sweep

    out["swap_taylor_to_managed_fx"] = call("lego.swap", d=copy.deepcopy(base), b="monetary-taylor",
                                            brick="monetary-fx-managed")
    out["detach_fiscal"] = call("lego.detach", d=copy.deepcopy(base), b="fiscal-debt-rule")
    out["detach_baseplate"] = call("lego.detach", d=copy.deepcopy(base), b="core-gap-open")

    # bridge sequence: fiscal brick made annual, then the fixes the protocol returns, applied one by one
    seq = []
    m = copy.deepcopy(base)
    r = call("lego.patch", d=m, b="fiscal-debt-rule", set={"freq": "A"})
    seq.append(("patch freq=A", r))
    m = r["r"].get("d", m) if r.get("ok") else m
    r = call("lego.check", d=m, strict=True, full=True)
    seq.append(("check strict", r))
    r = call("lego.bridge", d=m, b="fiscal-debt-rule", auto=True)
    seq.append(("bridge auto", r))
    m = r["r"].get("d", m) if r.get("ok") else m
    r = call("lego.check", d=m, strict=True, full=True)
    seq.append(("check strict", r))
    r = call("lego.bridge_test", d=m, apply=True)
    seq.append(("bridge_test apply", r))
    m = r["r"].get("d", m) if r.get("ok") else m
    r = call("lego.check", d=m, strict=True, full=True)
    seq.append(("check strict", r))
    r = S.handle({"op": "lego.approve", "a": {"d": m, "b": "fiscal-debt-rule", "by": "agent"}}, AGENT)
    seq.append(("approve by an agent", r))
    out["bridge_sequence"] = [{"step": s, "response": r} for s, r in seq]
    for s, r in seq:
        print(s, json.dumps({k: r.get(k) for k in ("ok", "e", "w")})[:400], json.dumps(counts(r)), flush=True)

    save(d, "lego-experiments.json", out)
    log(d, started)


if __name__ == "__main__":
    main()
