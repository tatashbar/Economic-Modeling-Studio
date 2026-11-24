#!/usr/bin/env python3
"""Known-answer exercises: small synthetic cases whose correct answer is known exactly.

Before a validator trusts a model's numbers, it reproduces these with the model's own code and toolchain.
A model that cannot get a known answer right is not validated, whatever its other checks say. They are also
self-contained teaching exercises: each one runs on its own, from a task folder.

Usage:
  python tools/known_answer.py list
  python tools/known_answer.py make <case> --out DIR      writes the inputs and TASK.md (never the answer)
  python tools/known_answer.py check <case> RESULT.json [--report FILE]
      compares the result with the known answer; exit code 1 if anything differs or is missing

The answers are computed here, not stored in the task folder. The point is that the model computes them
independently: the validator runs the model's code on the inputs and only then runs `check`.
Standard library only.
"""
import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bridge  # noqa: E402

QUARTERS = ["2025Q1", "2025Q2", "2025Q3", "2025Q4"]


def _write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _csv(rows, header=("period", "value")):
    return ",".join(header) + "\n" + "".join(",".join(str(x) for x in r) + "\n" for r in rows)


# ------------------------------------------------------------------ cases
def _bridge_case(role, method, answer_key):
    def make(out):
        _write(os.path.join(out, "quarterly.csv"), _csv([(q, v) for q, v in zip(QUARTERS, (1, 2, 3, 4))]))
    def expected():
        return {answer_key: bridge.convert(list(zip(QUARTERS, (1, 2, 3, 4))), method, "Q", "A")[0][1]}
    return make, expected


def _make_incomplete(out):
    _write(os.path.join(out, "quarterly.csv"), _csv([("2025Q1", 1), ("2025Q2", 2), ("2025Q2", 3), ("2025Q4", 4)]))


AR_SEED, AR_RHO, AR_N, AR_BURN = 20261124, 0.7, 400, 100


def _ar1_series():
    rng = random.Random(AR_SEED)
    y, out = 0.0, []
    for t in range(AR_BURN + AR_N):
        y = AR_RHO * y + rng.gauss(0.0, 1.0)
        if t >= AR_BURN:
            out.append(round(y, 10))
    return out


def _make_ar1(out):
    _write(os.path.join(out, "series.csv"), _csv([(t + 1, v) for t, v in enumerate(_ar1_series())], ("t", "y")))


def _expected_ar1():
    y = _ar1_series()
    num = sum(a * b for a, b in zip(y[1:], y[:-1]))
    den = sum(b * b for b in y[:-1])
    return {"rho_hat": num / den}


VAR_A = [[0.5, 0.1], [0.2, 0.4]]
VAR_B = [[1.0, 0.0], [0.3, 1.0]]


def _matmul(x, y):
    return [[sum(x[i][k] * y[k][j] for k in range(len(y))) for j in range(len(y[0]))] for i in range(len(x))]


def _make_var(out):
    _write(os.path.join(out, "var.json"), json.dumps({"A": VAR_A, "B": VAR_B, "horizons": 8}, indent=2) + "\n")


def _expected_var():
    irf, p = [], VAR_B
    for _ in range(9):
        irf.append(p)
        p = _matmul(VAR_A, p)
    return {"irf": irf}


SOLOW = {"s": 0.25, "n": 0.01, "delta": 0.05, "alpha": 0.33}


def _make_solow(out):
    _write(os.path.join(out, "parameters.json"), json.dumps(SOLOW, indent=2) + "\n")


def _expected_solow():
    k = (SOLOW["s"] / (SOLOW["n"] + SOLOW["delta"])) ** (1.0 / (1.0 - SOLOW["alpha"]))
    y = k ** SOLOW["alpha"]
    return {"k": k, "y": y, "c": (1.0 - SOLOW["s"]) * y}


DEBT = {"r": 0.03, "g": 0.05, "primary_balance": -0.01}


def _make_debt(out):
    _write(os.path.join(out, "parameters.json"), json.dumps(DEBT, indent=2) + "\n")


def _expected_debt():
    r, g, pb = DEBT["r"], DEBT["g"], DEBT["primary_balance"]
    return {"debt_ratio": -pb * (1 + g) / (g - r)}


_flow = _bridge_case("flow", "sum", "annual")
_stock = _bridge_case("stock", "last", "annual")
_avg = _bridge_case("rate", "average", "annual")

CASES = {
    "bridge-flow": {
        "area": "frequency bridges", "make": _flow[0], "expected": _flow[1], "tol": 1e-9,
        "title": "Quarterly flow to an annual total",
        "task": "quarterly.csv holds a FLOW (for example quarterly GDP or a deficit in currency units). Convert it to "
                "the annual value for 2025 with the model's own bridge code. Write RESULT.json as "
                "{\"annual\": <number>, \"method\": \"<the method you used>\"}.",
    },
    "bridge-stock": {
        "area": "frequency bridges", "make": _stock[0], "expected": _stock[1], "tol": 1e-9,
        "title": "End-of-quarter stock to a year-end value",
        "task": "quarterly.csv holds an END-OF-QUARTER STOCK (for example government debt). Convert it to the 2025 "
                "year-end value with the model's own bridge code. Write RESULT.json as "
                "{\"annual\": <number>, \"method\": \"<the method you used>\"}.",
    },
    "bridge-average": {
        "area": "frequency bridges", "make": _avg[0], "expected": _avg[1], "tol": 1e-9,
        "title": "Quarterly rate to an annual average",
        "task": "quarterly.csv holds a RATE (for example the policy interest rate, % p.a.). Convert it to the 2025 "
                "annual average with the model's own bridge code. Write RESULT.json as "
                "{\"annual\": <number>, \"method\": \"<the method you used>\"}.",
    },
    "bridge-incomplete": {
        "area": "frequency bridges", "make": _make_incomplete, "expected": lambda: {"refused": True}, "tol": 0,
        "title": "Four rows that are not a year",
        "task": "quarterly.csv has four rows for 2025, but Q2 appears twice and Q3 is missing. A correct bridge "
                "refuses to aggregate it, whatever the method. Run the model's bridge on it and write RESULT.json as "
                "{\"refused\": true, \"message\": \"<the error it gave>\"} if it refused, or {\"refused\": false, "
                "\"annual\": <number>} if it produced a number.",
    },
    "ar1-ols": {
        "area": "estimation", "make": _make_ar1, "expected": _expected_ar1, "tol": 1e-6,
        "title": "AR(1) coefficient by OLS",
        "task": f"series.csv holds {AR_N} observations of y simulated from y_t = {AR_RHO} y_(t-1) + e_t. Estimate rho "
                "by OLS of y_t on y_(t-1) WITHOUT a constant, on the data as given, with the model's estimation code. "
                "Write RESULT.json as {\"rho_hat\": <number>}. (The answer is the OLS estimate on these data, not the "
                "true value; the tolerance is 1e-6.)",
    },
    "var-irf": {
        "area": "structural dynamics", "make": _make_var, "expected": _expected_var, "tol": 1e-9,
        "title": "Impulse responses of a known VAR(1)",
        "task": "var.json gives a VAR(1) x_t = A x_(t-1) + B e_t with two variables and two shocks. Compute the impulse "
                "responses for horizons 0 to 8 with the model's own code. Write RESULT.json as "
                "{\"irf\": [M_0, M_1, ..., M_8]}, where M_h is a 2x2 list of lists and M_h[i][j] is the response of "
                "variable i to shock j at horizon h.",
    },
    "solow-steady-state": {
        "area": "steady state", "make": _make_solow, "expected": _expected_solow, "tol": 1e-9,
        "title": "Solow steady state per worker",
        "task": "parameters.json gives a Solow model in per-worker terms with Cobb-Douglas output y = k^alpha, saving "
                "rate s, population growth n and depreciation delta (no technology growth). Solve the steady state "
                "with the model's own solver. Write RESULT.json as {\"k\": <number>, \"y\": <number>, \"c\": <number>}.",
    },
    "debt-steady-state": {
        "area": "steady state", "make": _make_debt, "expected": _expected_debt, "tol": 1e-9,
        "title": "Steady-state debt ratio",
        "task": "parameters.json gives the interest rate r, the growth rate g and a constant primary balance (share of "
                "GDP, negative is a deficit) for b_(t+1) = (1+r)/(1+g) b_t - primary_balance. Compute the debt ratio "
                "at which debt is stable, with the model's own code. Write RESULT.json as {\"debt_ratio\": <number>}.",
    },
}


# ------------------------------------------------------------------ comparison
def _compare(want, got, tol, path=""):
    """Yield (path, expected, got, ok) for every leaf of the expected answer."""
    if isinstance(want, dict):
        if not isinstance(got, dict):
            yield (path or "result", "an object", got, False)
            return
        for k, v in want.items():
            if k not in got:
                yield (f"{path}{k}", v, "missing", False)
            else:
                yield from _compare(v, got[k], tol, f"{path}{k}.")
    elif isinstance(want, list):
        if not isinstance(got, list) or len(got) != len(want):
            yield (path.rstrip("."), f"a list of {len(want)}", got if not isinstance(got, list) else f"{len(got)} items", False)
            return
        for i, (a, b) in enumerate(zip(want, got)):
            yield from _compare(a, b, tol, f"{path}[{i}].")
    elif isinstance(want, bool):
        yield (path.rstrip("."), want, got, got is want)
    else:
        try:
            ok = abs(float(got) - float(want)) <= tol * max(1.0, abs(float(want)))
        except (TypeError, ValueError):
            ok = False
        yield (path.rstrip("."), want, got, ok)


def check_result(case, result):
    c = CASES[case]
    return list(_compare(c["expected"](), result, c["tol"]))


# ------------------------------------------------------------------ commands
def _cmd_list(a):
    for cid, c in CASES.items():
        print(f"{cid:<20} {c['area']:<20} {c['title']}")


def _cmd_make(a):
    c = CASES[a.case]
    c["make"](a.out)
    _write(os.path.join(a.out, "TASK.md"),
           f"# Known-answer exercise: {c['title']}\n\n{c['task']}\n\n"
           f"Use the model's own code and toolchain, not a hand calculation. Then run:\n\n"
           f"    python tools/known_answer.py check {a.case} RESULT.json\n\n"
           f"Tolerance: {c['tol'] or 'exact'}. A failure means the model is not validated until it is explained and fixed.\n")
    print(f"wrote {a.out}: inputs and TASK.md for '{a.case}' (the answer is not included)")


def _cmd_check(a):
    with open(a.result, encoding="utf-8") as f:
        result = json.load(f)
    rows = check_result(a.case, result)
    bad = [r for r in rows if not r[3]]
    lines = [f"Known-answer check: {a.case} ({CASES[a.case]['title']})"]
    for path, want, got, ok in rows:
        if len(rows) <= 12 or not ok:
            lines.append(f"  {'PASS' if ok else 'FAIL'}  {path}: expected {want}, got {got}")
    if len(rows) > 12 and not bad:
        lines.append(f"  PASS  all {len(rows)} values")
    lines.append(f"RESULT: {'PASS' if not bad else f'FAIL ({len(bad)} of {len(rows)} values differ or are missing)'}")
    print("\n".join(lines))
    if a.report:
        with open(a.report, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(["", "```"] + lines + ["```", ""]))
        print(f"appended to {a.report}")
    sys.exit(1 if bad else 0)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Known-answer exercises for validators")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.set_defaults(fn=_cmd_list)
    p = sub.add_parser("make"); p.add_argument("case", choices=list(CASES)); p.add_argument("--out", required=True)
    p.set_defaults(fn=_cmd_make)
    p = sub.add_parser("check"); p.add_argument("case", choices=list(CASES)); p.add_argument("result")
    p.add_argument("--report", help="append the check to this validation report"); p.set_defaults(fn=_cmd_check)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
