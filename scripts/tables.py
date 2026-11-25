"""Tables, figure captions and in-text numbers, all read from saved run outputs (paper/em2026/output)."""
import json
import os
import statistics

from common import OUT


def J(*p):
    path = os.path.join(OUT, *p)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def f(x, n=3):
    return f"{x:.{n}f}"


def pct(x, n=1):
    return f"{100 * x:.{n}f}"


AGENT_AREAS = [
    ("Framing, methods and governance", 6, "economic reasoning, methodology, model-risk governance, research notes"),
    ("Macro models: small, medium, traditional", 6, "semi-structural gap, FPAS, financial programming, three-gap, SFC"),
    ("Structural macro: DSGE, HANK, solution methods", 10, "open-economy and multi-country DSGE, HANK, perturbation, ZLB"),
    ("Econometrics and time series", 8, "VAR/VECM, BVAR, DFM nowcasting, local projections, state space"),
    ("Forecasting and scenarios", 3, "forecast evaluation and combination, scenario and risk analysis"),
    ("Input-output, CGE, trade and sectoral", 7, "IO and SAM, CGE, trade policy, production networks, agriculture"),
    ("Climate, energy and natural resources", 6, "climate-macro, carbon pricing, physical risk, commodities"),
    ("Fiscal and public finance", 6, "debt sustainability, multipliers, microsimulation, fiscal risk"),
    ("Monetary and financial", 9, "policy rules, inflation, yield curve, banks, macroprudential, stress tests"),
    ("External sector and global linkages", 4, "balance of payments, external assessment, capital flows, spillovers"),
    ("Integrated policy framework", 4, "policy mix by shock and friction, FX intervention, low-income countries"),
    ("Growth, labour, distribution, development", 5, "growth, labour and demography, inequality, fragility, AI economy"),
    ("AI and machine learning", 16, "deep learning, deep RL, neural solvers, LLM analysis and agents, causal ML"),
    ("Games, agents and strategic behaviour", 6, "game theory, mechanism design, agent-based models, wargames"),
    ("Data and statistics", 7, "pipelines, national accounts, survey microdata, data quality, governance"),
    ("Computation and engineering", 7, "Dynare/MATLAB, Python/Julia, HPC, MLOps, reproducibility, symbolic"),
    ("Code translation", 6, "planning, source analysis, statistical, model and legacy code, equivalence"),
    ("Validation, risk and ethics", 6, "validation, backtesting, sensitivity, replication audit, red-teaming"),
    ("Communication and capacity building", 5, "policy briefs, documentation, visualisation, training"),
]
assert sum(a[1] for a in AGENT_AREAS) == 127

GATES = [
    ("Concept", "Scope note; model brief with purpose, non-purposes, model class and risk level"),
    ("Design", "Specification with matching equation and unknown counts; calibration plan; data sheet with classification; simple benchmark defined"),
    ("Build", "Code in the model folder; tests passing (identities, steady state or benchmark replication, regression); no hard-coded parameters; code review"),
    ("Estimate", "Estimation or calibration report; convergence and identification evidence; fit and out-of-sample results"),
    ("Validate", "Independent validation report with a rating other than fail; no open high-severity findings; replication report; AI audit where AI is used"),
    ("Release", "Release recommendation approved; model card; release notes; registry entry; replication package"),
]

CONTROLS = [
    ("Read a plain-language report of a track", "-", "allowed"),
    ("Leave a note", "appears in every agent's inbox", "allowed"),
    ("Leave a constraint", "agents cannot write until they have read it (503)", "refused (104)"),
    ("Freeze a brick or parameter", "no agent can change it on that track (502)", "refused (104)"),
    ("Pause or resume a track", "no writes until it resumes (501); reading still works", "refused (104)"),
    ("Undo (veto) an event", "the track returns to its state before the event", "refused (104)"),
    ("Answer an agent's question", "the answer is delivered to the agent", "refused (104)"),
    ("Stop or reopen an improvement study", "no further rounds (704)", "refused (104)"),
    ("Give the economist's sign-off on a brick", "recorded with name, date and note", "refused (104)"),
]

CODES = [
    ("1xx", "protocol", "100 bad message; 101 unknown operation; 104 for people only; 105 over a limit"),
    ("2xx", "wiring errors", "206 baseplate count; 207 two providers; 210 open input without closure; 211 bridge without method; 215 identity broken; 218 change blocked; 219 state changed"),
    ("3xx", "warnings", "301 no bridge; 302 bridge is a note; 303 method contradicts measure; 304 bridge untested; 309 equations and variables differ"),
    ("4xx", "validation", "401 known answer failed; 402 untestable; 403 bridge not passed; 404 input refused"),
    ("5xx", "shared workspace", "501 paused; 502 frozen; 503 unread message from a person; 504 lease held"),
    ("6xx", "economy engine (AEL)", "601 invalid rule; 602 parameter out of bounds; 603 money not conserved; 606 invalid entity"),
    ("7xx", "improvement loop (RSIM)", "701 outside the study; 702 overfit; 703 budget spent; 704 study closed"),
]


def lego_rows():
    L = J("lego", "lego-experiments.json")
    if not L:
        return [], {}
    rows = []
    blocked = {}
    for r in L["attach_sweep"]:
        raw = r.get("raw", {})
        codes = [str(x[0]) for x in (raw.get("e") or [])] + [str(x[0]) for x in (raw.get("w") or [])]
        if r.get("blocked"):
            blocked[r["brick"]] = raw.get("e")
        rows.append([r["brick"], r["new_joints"], r["stubs_retired"], r["stubs_activated"],
                     len(r["revalidate"]), ", ".join(codes) or "none", "blocked" if r["blocked"] else "can apply"])
    return rows, blocked


def values():
    V = {"author_email": "tatashbar@imf.org",
         "replication_link": "https://github.com/tatashbar/Economic-Modeling-Studio/tree/economic-modelling-2026"}
    B = J("ael-baseline", "baseline.json")
    S = J("ael-baseline", "scale.json")
    K = J("ael-baseline", "known-answers.json")
    if B:
        m = B["moments"]
        V.update(base_u=pct(m["unemployment"]["mean"], 2), base_pi=pct(m["inflation"]["mean"], 2),
                 base_gini=f(m["wealth_gini"]["mean"], 3), base_debt=pct(m["debt_gdp"]["mean"], 1),
                 base_rate=pct(m["policy_rate"]["mean"], 2), base_acc=f"{B['max_accounting_error']:.1e}",
                 ent_acc=f"{B['with_entities']['max_accounting_error']:.1e}", n_known=len(K or []))
    if S:
        V.update(t1k=f(S[0]["seconds"], 1), t10k=f(S[1]["seconds"], 1), t100k=f(S[2]["seconds"], 0),
                 acc100k=f"{S[2]['accounting_error']:.1e}")
    L = J("lego", "lego-experiments.json")
    if L:
        sw = L["attach_sweep"]
        V.update(n_sweep=len(sw), n_blocked=sum(1 for r in sw if r["blocked"]),
                 sweep_ms_max=f(max(r["ms"] for r in sw), 0), sweep_ms_med=f(statistics.median(r["ms"] for r in sw), 0))
    R = J("rsim", "rsim-vs-random.json")
    if R and R.get("reps"):
        reps = R["reps"]
        V.update(n_reps=len(reps), budget=R["budget"], def_test=f(R["default_on_test"]["loss"], 3))
        rt = [r["test"]["rsim"]["loss"] for r in reps]
        bt = [r["test"]["random"]["loss"] for r in reps]
        V.update(rsim_test_mean=f(statistics.mean(rt), 3), rand_test_mean=f(statistics.mean(bt), 3),
                 rsim_wins=sum(1 for a, b in zip(rt, bt) if a < b),
                 overfit_total=sum(r["rsim"]["counts"].get("overfit", 0) for r in reps))
    P = J("ael-policy", "policy.json")
    if P:
        V.update(pol_acc=f"{P['max_accounting_error']:.1e}", brake_share=pct(P.get("share_periods_brake_on", 0), 0))
    W = J("swarm", "swarm-summary.json")
    if W:
        V.update({f"sw_{k}": (f"{v:,}" if isinstance(v, int) else f"{v:.2f}") for k, v in W.items()
                  if not isinstance(v, (dict, list))})
    return V


def rsim_table():
    R = J("rsim", "rsim-vs-random.json")
    rows = []
    if not R:
        return rows
    for r in R["reps"]:
        rs, rd = r["rsim"], r["random"]
        rows.append([r["rep"], f(rs["champion"]["loss"], 3), f(r["test"]["rsim"]["loss"], 3),
                     rs["counts"].get("overfit", 0), f(rd["best_loss"], 3), f(r["test"]["random"]["loss"], 3)])
    reps = R["reps"]
    m = lambda g: f(statistics.mean(g(r) for r in reps), 3)  # noqa: E731
    rows.append(["Mean", m(lambda r: r["rsim"]["champion"]["loss"]), m(lambda r: r["test"]["rsim"]["loss"]),
                 sum(x[3] for x in rows), m(lambda r: r["random"]["best_loss"]), m(lambda r: r["test"]["random"]["loss"])])
    return rows


def rsim_moments_table():
    R = J("rsim", "rsim-vs-random.json")
    if not R:
        return []
    tg = R["targets"]
    rows = []
    d0 = R["default_on_test"]["moments"]
    for k in ("unemployment", "inflation", "wealth_gini"):
        row = [k.replace("_", " "), f(tg[k][0], 3), f(d0[k], 3)]
        row.append(f(statistics.mean(r["test"]["rsim"]["moments"][k] for r in R["reps"]), 3))
        row.append(f(statistics.mean(r["test"]["random"]["moments"][k] for r in R["reps"]), 3))
        rows.append(row)
    return rows


def policy_table():
    P = J("ael-policy", "policy.json")
    if not P:
        return []
    rows = []
    names = {"s1_default_rule": "S1 default rule", "s2_strict_rule": "S2 strict inflation targeting",
             "s3_no_brake": "S3 +6 pp, no brake", "s3_brake": "S3 +6 pp, debt brake"}
    for key, label in names.items():
        tb = P["table"][key]
        for h in ("0", "4", "20", "79"):
            if h not in tb["real_gdp"]:
                continue
            g = tb["real_gdp"][h]
            rows.append([label, h, f"{g['mean']:.2f} ({g['se']:.2f})",
                         f"{100 * tb['u'][h]['mean']:.2f}", f"{100 * tb['pi'][h]['mean']:.2f}",
                         f"{100 * tb['rate'][h]['mean']:.2f}", f"{100 * tb['debt_gdp'][h]['mean']:.1f}"])
    return rows


def ael_table():
    B = J("ael-baseline", "baseline.json")
    if not B:
        return []
    labels = [("unemployment", "Unemployment rate", 100, 2), ("inflation", "Inflation, annual", 100, 2),
              ("policy_rate", "Policy rate, annual", 100, 2), ("growth_sd", "SD of output growth", 100, 2),
              ("growth_ac1", "Autocorrelation of output growth", 1, 2), ("cons_share", "Consumption share", 100, 1),
              ("debt_gdp", "Public debt, share of annual output", 100, 1), ("wealth_gini", "Wealth Gini", 1, 3),
              ("default_rate", "Firm default rate per period", 100, 3)]
    rows = []
    for k, lab, sc, n in labels:
        a, e = B["moments"][k], B["with_entities"]["moments"][k]
        rows.append([lab, f"{sc * a['mean']:.{n}f} ({sc * a['sd']:.{n}f})", f"{sc * e['mean']:.{n}f} ({sc * e['sd']:.{n}f})"])
    rows.append(["Largest accounting gap (relative)", f"{B['max_accounting_error']:.1e}",
                 f"{B['with_entities']['max_accounting_error']:.1e}"])
    return rows


def known_table():
    K = J("ael-baseline", "known-answers.json") or []
    return [[k["test"], "pass" if k["pass"] else "FAIL", k["detail"]] for k in K]


def scale_table():
    S = J("ael-baseline", "scale.json") or []
    return [[f"{s['households']:,}", f"{s['firms']:,}", s["periods"], f(s["seconds"], 1), f"{s['accounting_error']:.1e}"] for s in S]


def bridge_rows():
    L = J("lego", "lego-experiments.json")
    if not L:
        return []
    rows = []
    for st in L["bridge_sequence"]:
        r = st["response"]
        codes = [str(x[0]) for x in (r.get("e") or [])] + [str(x[0]) for x in (r.get("w") or [])]
        rows.append([st["step"], "yes" if r.get("ok") else "refused", ", ".join(codes) or "none"])
    return rows


lego_sweep, _ = lego_rows()

TABLES = {
    "layers": {"caption_label": "Table 1.", "caption": "Architecture of the framework in five layers.",
               "header": ["Layer", "What it holds", "Role"], "widths": [2.8, 7.7, 5.0],
               "rows": [["Knowledge", "127 specialist agents in 19 areas; 94 skills; path-scoped rules; templates; copies of the instructions for every coding agent", "What agents know and how each job is done (Section 4)"],
                        ["Model", "One manifest per model: baseplate, bricks, ports with units and timing, closures, slots, identities, change history, three records per brick", "The lego-like description of each model (Section 5)"],
                        ["Engine", "Manifest engine (checks, plans, bridges); known-answer exercises; code translation; Agent Economy Lab (AEL); improvement loop (RSIM)", "Every economic computation; deterministic, checked and logged"],
                        ["Interface", "JSON protocol with numbered findings and fixes; MCP server; gateway to many MCP servers; shared workspace (tracks, leases, logs)", "How people and outside agents use the engines (Section 6)"],
                        ["Governance (across all layers)", "Hooks and commit guard; phase gates; model risk levels; builder-validator independence; audit log; sign-off by people only", "Rules enforced by software where possible"]],
               "note": "People and outside agents, LLM-based or rule-based, use the same interface; only people can pause, freeze, veto and sign off. Agents propose; engines check and log."},
    "agents": {"caption_label": "Table 2.", "caption": "Specialist agents by area of expertise.",
               "header": ["Area", "Agents", "Examples"], "rows": [list(a) for a in AGENT_AREAS] + [["Total", 127, ""]]},
    "gates": {"caption_label": "Table 3.", "caption": "Phase gates and their exit criteria.",
              "header": ["Gate", "Evidence required"], "rows": [list(g) for g in GATES],
              "note": "A gate returns pass, concerns (with named owners and dates), fail or not assessed; missing evidence is never a pass."},
    "controls": {"caption_label": "Table 4.", "caption": "Controls kept by people in the shared workspace.",
                 "header": ["Operation", "Effect on agents (code)", "If an agent tries it"], "rows": [list(c) for c in CONTROLS]},
    "sweep": {"caption_label": "Table 5.", "caption": "Change-impact plans for attaching each catalogue brick to the small open-economy model.",
              "header": ["Brick", "New joints", "Closures retired", "Closures activated", "Bricks to revalidate", "Findings", "Plan"],
              "rows": lego_sweep,
              "note": "Dry-run plans computed through the protocol on an inline copy of the model; nothing was written. A plan is blocked when it would add an error (for example a second baseplate, two providers of the policy rate, or an open input without a closure)."},
    "bridge": {"caption_label": "Table 6.", "caption": "Protocol sequence when the fiscal brick is moved to annual frequency.",
               "header": ["Step", "Accepted", "Finding codes"], "rows": bridge_rows(),
               "note": "Each fix was taken from the previous response. Code 301: no bridge declared; 304: bridge declared but untested; 104: operation reserved for people."},
    "known": {"caption_label": "Table 7.", "caption": "Known-answer tests of the Agent Economy Lab.",
              "header": ["Test", "Result", "Detail"], "rows": known_table()},
    "ael": {"caption_label": "Table 8.", "caption": "Moments of the default AEL economy (1,000 households, 50 firms; mean and standard deviation across 8 seeds).",
            "header": ["Moment", "Default economy", "With foreign sector and 3 pension funds"], "rows": ael_table(),
            "note": "200 quarters per run, of which the first 50 are discarded. Unemployment, inflation, rates, growth and default in percent."},
    "scale": {"caption_label": "Table 9.", "caption": "Run time and accounting gap by scale (one seed, 200 quarters).",
              "header": ["Households", "Firms", "Quarters", "Seconds", "Largest accounting gap"], "rows": scale_table(),
              "note": "Single process on a 16-core desktop computer. The 100,000-household run shared the processor with the calibration experiment of Section 8.4, so its time is an upper bound."},
    "rsim": {"caption_label": "Table 10.", "caption": "RSIM against random search with the same budget of model runs.",
             "header": ["Replication", "RSIM training loss", "RSIM test loss", "Refused as overfit", "Random search training loss", "Random search test loss"],
             "rows": rsim_table(),
             "note": "Loss: weighted sum of squared relative gaps to targets for unemployment (6%), inflation (2%) and the wealth Gini (0.35, weight 0.5). Training: seeds 1 and 2. Test: seeds 101-108, seen by neither procedure. Budget: 400 model runs per procedure; for RSIM this includes the 6-7% of runs spent on its two hidden seeds."},
    "rsim_moments": {"caption_label": "Table 11.", "caption": "Targeted moments on the test seeds.",
                     "header": ["Moment", "Target", "Default parameters", "RSIM champion (mean)", "Random search best (mean)"],
                     "rows": rsim_moments_table()},
    "policy": {"caption_label": "Table 12.", "caption": "Responses to a permanent rise in government purchases in the calibrated AEL economy.",
               "header": ["Scenario", "Quarters after", "Real output, % (s.e.)", "Unemployment, pp", "Inflation, pp", "Policy rate, pp", "Debt/GDP, pp"],
               "rows": policy_table(),
               "note": "Scenario minus baseline with common random numbers, mean over 16 seeds; standard errors across seeds in parentheses. S1 and S2: purchases share +3 points; S3: +6 points. S2 compares with a baseline under the same strict rule."},
    "codes": {"caption_label": "Table A.1.", "caption": "Finding codes of the protocol.",
              "header": ["Range", "Area", "Examples"], "rows": [list(c) for c in CODES]},
}

FIGURES = {
    "lego": {"file": "Figure_1.png", "caption_label": "Fig. 1.",
             "caption": "A small open-economy model drawn from its manifest. The baseplate is the core gap model; bricks stand on the bricks whose outputs they read; stud colours show what each brick is made of (variables, equations, parameters, shocks, data, constraints). The translucent brick is a catalogue component that would fill an open input."},
    "rsim": {"file": "Figure_2.png", "caption_label": "Fig. 2.",
             "caption": "Best training loss against model runs used, RSIM and random search, three replications each."},
    "policy": {"file": "Figure_3.png", "caption_label": "Fig. 3.", "width": 14.5,
               "caption": "Responses to a permanent three-point rise in the government purchases share under the default and a strict inflation-targeting rule, and to a six-point rise with and without a debt brake (mean over 16 seeds, scenario minus baseline)."},
}
