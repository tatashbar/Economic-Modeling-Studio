#!/usr/bin/env python3
"""Frequency bridges: convert a series between annual (A), quarterly (Q) and monthly (M) data.

A bridge must say HOW each variable converts, because the same numbers give different answers:
quarterly values 1, 2, 3, 4 are an annual total of 10 for a flow, a year-end value of 4 for an
end-of-period stock, and an annual average of 2.5 for a rate. The method is the record of that choice.

Aggregation (higher to lower frequency)       Disaggregation (lower to higher frequency)
  sum      flows (GDP, deficits, trade)          split        flows: each sub-period gets an equal share
  average  rates and averages (interest rate)    repeat       rates and averages: each sub-period gets the value
  last     end-of-period stocks (debt)           interpolate  end-of-period stocks: linear path between
  first    start-of-period stocks                             consecutive period-end values

Before converting, every target period must be complete: each sub-period present exactly once. Four
quarterly rows are not a year if Q2 appears twice and Q3 is missing; that is refused, not averaged.

Usage:
  python tools/bridge.py methods
  python tools/bridge.py test [--method M] [--from Q --to A]     known-answer tests of the methods
  python tools/bridge.py convert IN.csv --method sum --from Q --to A [--out OUT.csv]
      IN.csv has two columns, period and value (periods like 2025, 2025Q1, 2025M01).

Standard library only. Models written in Python can import it: from bridge import convert.
"""
import argparse
import csv
import re
import sys

PER_YEAR = {"A": 1, "Q": 4, "M": 12}
METHODS = {
    "sum": ("aggregate", "flow"), "average": ("aggregate", "average"),
    "last": ("aggregate", "stock"), "first": ("aggregate", "stock"),
    "split": ("disaggregate", "flow"), "repeat": ("disaggregate", "average"),
    "interpolate": ("disaggregate", "stock"),
}
# the disaggregation that each aggregation reverses (used for round-trip tests)
INVERSE = {"split": "sum", "repeat": "average", "interpolate": "last"}
TOL = 1e-9


class BridgeError(ValueError):
    pass


def direction(src, dst):
    """'aggregate' when going to a lower frequency (Q to A), 'disaggregate' when going higher (A to Q)."""
    for f in (src, dst):
        if f not in PER_YEAR:
            raise BridgeError(f"unknown frequency '{f}' (use A, Q or M)")
    if src == dst:
        return "same"
    return "aggregate" if PER_YEAR[src] > PER_YEAR[dst] else "disaggregate"


def fits(method, src, dst):
    """Problem text if the method cannot convert src to dst, else None."""
    if method not in METHODS:
        return f"unknown method '{method}' (use one of {', '.join(METHODS)})"
    want = direction(src, dst)
    if want == "same":
        return None
    if METHODS[method][0] != want:
        ok = [k for k, v in METHODS.items() if v[0] == want]
        return f"'{method}' cannot go from {src} to {dst}; that is {want}d with {', '.join(ok)}"
    return None


def parse(label, freq):
    """(year, sub-period) from a label such as 2025, 2025Q1, 2025-Q1, 2025M01 or 2025-01."""
    s = str(label).strip().upper()
    if freq == "A":
        m = re.fullmatch(r"(\d{4})", s)
        if m:
            return int(m.group(1)), 1
    elif freq == "Q":
        m = re.fullmatch(r"(\d{4})-?Q([1-4])", s)
        if m:
            return int(m.group(1)), int(m.group(2))
    elif freq == "M":
        m = re.fullmatch(r"(\d{4})(?:-?M|-)(\d{1,2})", s)
        if m and 1 <= int(m.group(2)) <= 12:
            return int(m.group(1)), int(m.group(2))
    raise BridgeError(f"period '{label}' is not a valid {freq} period (examples: 2025, 2025Q1, 2025M01)")


def label(year, sub, freq):
    return str(year) if freq == "A" else f"{year}Q{sub}" if freq == "Q" else f"{year}M{sub:02d}"


def _groups(rows, src, dst):
    """Group source rows into target periods, refusing incomplete or duplicated groups."""
    k = PER_YEAR[src] // PER_YEAR[dst]
    if PER_YEAR[src] % PER_YEAR[dst]:
        raise BridgeError(f"{src} does not nest in {dst}")
    groups = {}
    for p, v in rows:
        y, s = parse(p, src)
        tgt = (y, (s - 1) // k + 1)
        groups.setdefault(tgt, []).append((s, p, v))
    out = []
    for tgt in sorted(groups):
        items = sorted(groups[tgt])
        first = (tgt[1] - 1) * k + 1
        expected = list(range(first, first + k))
        subs = [s for s, _, _ in items]
        if subs != expected:
            dup = sorted({label(tgt[0], s, src) for s in subs if subs.count(s) > 1})
            miss = [label(tgt[0], s, src) for s in expected if s not in subs]
            why = "; ".join(x for x in (f"duplicated: {', '.join(dup)}" if dup else "",
                                         f"missing: {', '.join(miss)}" if miss else "") if x)
            raise BridgeError(f"{label(*tgt, dst)} is incomplete: {len(items)} rows but it needs each of its {k} "
                              f"{src} periods exactly once ({why}); nothing was converted")
        out.append((tgt, [float(v) for _, _, v in items]))
    return out


def convert(rows, method, src, dst):
    """Convert [(period, value), ...] from frequency src to dst. Raises BridgeError on any problem."""
    prob = fits(method, src, dst)
    if prob:
        raise BridgeError(prob)
    rows = list(rows)
    if not rows:
        raise BridgeError("no data")
    if src == dst:
        return [(p, float(v)) for p, v in rows]
    if direction(src, dst) == "aggregate":
        f = {"sum": sum, "average": lambda x: sum(x) / len(x), "last": lambda x: x[-1], "first": lambda x: x[0]}[method]
        return [(label(*tgt, dst), f(vals)) for tgt, vals in _groups(rows, src, dst)]
    k = PER_YEAR[dst] // PER_YEAR[src]
    seen, parsed = set(), []
    for p, v in rows:
        key = parse(p, src)
        if key in seen:
            raise BridgeError(f"{p} appears more than once; nothing was converted")
        seen.add(key)
        parsed.append((key, float(v)))
    parsed.sort()
    for (a, _), (b, _) in zip(parsed, parsed[1:]):
        if (b[0] * PER_YEAR[src] + b[1]) - (a[0] * PER_YEAR[src] + a[1]) != 1:
            raise BridgeError(f"gap between {label(*a, src)} and {label(*b, src)}; nothing was converted")
    out = []
    for i, ((y, s), v) in enumerate(parsed):
        subs = [(y, (s - 1) * k + j) for j in range(1, k + 1)]
        if method == "split":
            vals = [v / k] * k
        elif method == "repeat":
            vals = [v] * k
        else:  # interpolate: linear from the previous period-end value to this one
            if i == 0:
                continue  # the first period only anchors the path
            prev = parsed[i - 1][1]
            vals = [prev + (v - prev) * j / k for j in range(1, k + 1)]
        out += [(label(yy, ss, dst), x) for (yy, ss), x in zip(subs, vals)]
    if method == "interpolate" and not out:
        raise BridgeError("interpolate needs at least two period-end values (the first one anchors the path)")
    return out


# ------------------------------------------------------------------ known-answer tests
def _close(a, b):
    return abs(a - b) <= TOL * max(1.0, abs(b))


def known_answers(method, src="Q", dst="A"):
    """Run the known-answer cases for one method and frequency pair. Returns [(case, expected, got, ok)]."""
    prob = fits(method, src, dst)
    if prob:
        return [("method fits the frequencies", "yes", prob, False)]
    res = []
    if direction(src, dst) == "same":
        return [("same frequency", "no conversion", "no conversion", True)]
    if direction(src, dst) == "aggregate":
        k = PER_YEAR[src] // PER_YEAR[dst]
        vals = list(range(1, k + 1))
        rows = [(label(2025, s, src), v) for s, v in zip(range(1, k + 1), vals)]
        want = {"sum": sum(vals), "average": sum(vals) / k, "last": vals[-1], "first": vals[0]}[method]
        try:
            got = convert(rows, method, src, dst)[0][1]
            res.append((f"{', '.join(map(str, vals))} as {METHODS[method][1]} ({method})", want, got, _close(got, want)))
        except BridgeError as e:
            res.append((f"{method} of 1..{k}", want, str(e), False))
        bad = list(rows)
        bad[2] = (label(2025, 2, src), vals[2])  # the third sub-period replaced by a second copy of the second
        try:
            convert(bad, method, src, dst)
            res.append(("duplicated sub-period, one missing", "refused", "converted anyway", False))
        except BridgeError:
            res.append(("duplicated sub-period, one missing", "refused", "refused", True))
        try:
            convert(rows[:-1], method, src, dst)
            res.append(("incomplete period", "refused", "converted anyway", False))
        except BridgeError:
            res.append(("incomplete period", "refused", "refused", True))
        return res
    k = PER_YEAR[dst] // PER_YEAR[src]
    if method == "interpolate":
        rows = [(label(2024, PER_YEAR[src], src), 4.0), (label(2025, 1, src), 8.0)]
        want = [4.0 + 4.0 * j / k for j in range(1, k + 1)]
        case = "period-end values 4 then 8 (interpolate)"
    else:
        rows = [(label(2025, 1, src), 10.0)]
        want = [10.0 / k] * k if method == "split" else [10.0] * k
        case = f"10 as {METHODS[method][1]} ({method})"
    try:
        got = [v for _, v in convert(rows, method, src, dst)]
        ok = len(got) == len(want) and all(_close(a, b) for a, b in zip(got, want))
        res.append((case, _fmt(want), _fmt(got), ok))
        back = convert(convert(rows, method, src, dst), INVERSE[method], dst, src)
        orig = rows[-1:] if method == "interpolate" else rows
        ok2 = len(back) == len(orig) and all(_close(a[1], b[1]) for a, b in zip(back, orig))
        res.append((f"round trip with {INVERSE[method]}", _fmt([v for _, v in orig]), _fmt([v for _, v in back]), ok2))
    except BridgeError as e:
        res.append((case, _fmt(want), str(e), False))
    dup = [rows[-1], rows[-1]]
    try:
        convert(dup, method, src, dst)
        res.append(("duplicated period", "refused", "converted anyway", False))
    except BridgeError:
        res.append(("duplicated period", "refused", "refused", True))
    return res


def _fmt(x):
    if isinstance(x, list):
        return ", ".join(_fmt(v) for v in x)
    if isinstance(x, float):
        return f"{x:g}"
    return str(x)


# ------------------------------------------------------------------ command line
def _cmd_methods(a):
    for k, (d, measure) in METHODS.items():
        print(f"{k:<12} {d:<13} for {measure} variables")


def _cmd_test(a):
    pairs = [(a.src, a.dst)] if a.src and a.dst else [("Q", "A"), ("M", "Q"), ("M", "A"), ("A", "Q"), ("Q", "M")]
    failed = 0
    for src, dst in pairs:
        for m in ([a.method] if a.method else [k for k, v in METHODS.items() if v[0] == direction(src, dst)]):
            for case, want, got, ok in known_answers(m, src, dst):
                failed += not ok
                print(f"{'PASS' if ok else 'FAIL'}  {src} to {dst}  {m:<11} {case}: expected {_fmt(want)}, got {_fmt(got)}")
    print(f"\n{'all known-answer cases passed' if not failed else f'{failed} case(s) FAILED'}")
    sys.exit(1 if failed else 0)


def _cmd_convert(a):
    with open(a.csv, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and r[0].strip()]
    if rows and not re.match(r"\d{4}", rows[0][0].strip()):
        rows = rows[1:]  # header
    try:
        out = convert([(r[0], r[1]) for r in rows], a.method, a.src, a.dst)
    except (BridgeError, ValueError, IndexError) as e:
        raise SystemExit(f"not converted: {e}")
    lines = ["period,value"] + [f"{p},{v:.12g}" for p, v in out]
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
        print(f"wrote {a.out}: {len(out)} {a.dst} periods ({a.method})")
    else:
        print("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Frequency bridges with a declared method and completeness checks")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("methods"); p.set_defaults(fn=_cmd_methods)
    p = sub.add_parser("test"); p.add_argument("--method", choices=list(METHODS))
    p.add_argument("--from", dest="src", choices=list(PER_YEAR)); p.add_argument("--to", dest="dst", choices=list(PER_YEAR))
    p.set_defaults(fn=_cmd_test)
    p = sub.add_parser("convert"); p.add_argument("csv"); p.add_argument("--method", required=True, choices=list(METHODS))
    p.add_argument("--from", dest="src", required=True, choices=list(PER_YEAR))
    p.add_argument("--to", dest="dst", required=True, choices=list(PER_YEAR)); p.add_argument("--out")
    p.set_defaults(fn=_cmd_convert)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
