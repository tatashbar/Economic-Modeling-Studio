#!/usr/bin/env python3
"""Agent Economy Lab (AEL): agent-based economies at the scale you choose (for example 10,000 households and
1,000 firms), with a bank, a government and a monetary authority, stock-flow consistent by construction.
Standard library only.

Every payment moves money from one account to another, so the sum of all accounts (households, firms, the
government, the bank) never changes: the run checks it every period and reports the largest error. Behaviour
rules (consumption, prices, wages, the policy rate) are formulas that people and agents can replace without
writing code: a formula is checked against a short list of allowed names and functions before it runs.

    python tools/economy.py run [--households 1000] [--firms 50] [--periods 200] [--seed 1] [--set mpc_y=0.7]
    python tools/economy.py run --config economy.json --out run.json
    python tools/economy.py run --entity foreign --entity pension_fund:3    with other entities added
    python tools/economy.py rules                     the behaviour rules, their formulas and variables
    python tools/economy.py entities                  the kinds of entities that can be added, and how to define new ones
    python tools/economy.py known                     known-answer tests of the engine
    python tools/economy.py scale                     households from 1,000 to 100,000: time per run

For agents: economy.new, economy.run, economy.check, economy.rules, economy.known in the studio protocol.
"""
import argparse
import ast
import copy
import json
import math
import os
import random
import sys
import time

PARAMS = {
    # structure
    "prod": (1.0, 0.1, 10, "output per efficiency unit of labor"),
    "z_sigma": (0.3, 0.0, 1.5, "dispersion of household productivity (log standard deviation)"),
    # households
    "mpc_y": (0.85, 0.0, 1.0, "share of disposable income consumed"),
    "mpc_w": (0.06, 0.0, 1.0, "share of deposits consumed each quarter"),
    "rate_sens": (3.0, 0.0, 50.0, "how much a higher real interest rate cuts spending out of deposits"),
    "res_decay": (0.1, 0.0, 1.0, "fall in the reservation wage per quarter of unemployment"),
    "search": (4, 1, 20, "firms a household visits when shopping or looking for work"),
    # firms
    "theta_p": (0.04, 0.0, 0.5, "largest price change per quarter"),
    "theta_w": (0.02, 0.0, 0.5, "largest wage change per quarter"),
    "inv_target": (0.15, 0.0, 2.0, "target inventory, as a share of expected sales"),
    "lam": (0.5, 0.0, 1.0, "weight of the latest sales in expected sales"),
    "payout": (0.9, 0.0, 1.0, "share of profits paid out to households"),
    "cash_buffer": (1.0, 0.0, 20.0, "deposits a firm keeps, in quarters of its wage bill; it pays out cash above that"),
    "markup": (0.15, 0.0, 2.0, "highest markup over unit labor cost"),
    "markup_lo": (0.02, 0.0, 2.0, "lowest markup over unit labor cost"),
    # government
    "tau": (0.22, 0.0, 0.9, "tax rate on wage, dividend and interest income"),
    "benefit": (0.4, 0.0, 1.5, "unemployment benefit as a share of the average wage"),
    "g_share": (0.18, 0.0, 0.6, "government purchases as a share of the previous quarter's nominal output"),
    "debt_target": (0.6, 0.0, 3.0, "government debt the fiscal rule aims at, as a share of annual nominal output"),
    "fiscal_rho": (0.05, 0.0, 1.0, "share of the gap between debt and its target closed by purchases each quarter"),
    # money and credit
    "rstar": (0.02, -0.05, 0.1, "neutral real interest rate, annual"),
    "pistar": (0.02, -0.05, 0.2, "inflation target, annual"),
    "phi_pi": (1.5, 0.0, 5.0, "policy rate response to inflation"),
    "phi_u": (0.5, 0.0, 5.0, "policy rate response to unemployment"),
    "ustar": (0.06, 0.0, 0.5, "unemployment rate at which the economy is at potential"),
    "spread": (0.03, 0.0, 0.3, "loan rate over the policy rate, annual"),
    "dep_share": (0.0, 0.0, 1.0, "deposit rate as a share of the policy rate (deposits are paid from the bank's income)"),
    "default_after": (6, 1, 100, "a firm whose debt exceeds this many quarters of its wage bill defaults"),
    # initial conditions
    "w0": (6.0, 0.0, 1000, "initial deposits of a household"),
    "firm_w0": (20.0, 0.0, 10000, "initial deposits of a firm"),
}

FUNCS = {"min": min, "max": max, "abs": abs, "exp": math.exp, "log": math.log, "sqrt": math.sqrt}
RULES = {
    "consume": {"vars": ("y", "w", "p", "u", "z", "r", "pi"),
                "doc": "spending of one household this quarter: y disposable income, w deposits, p average price, "
                       "u unemployment rate, z productivity, r policy rate (annual), pi inflation (annual)",
                "default": "min(w + y, mpc_y * y + mpc_w * w * max(0, 1 - rate_sens * (r - pi - rstar)))"},
    "price": {"vars": ("p", "pbar", "inv", "target", "cost", "shock"),
              "doc": "a firm's new price: p its price, pbar the average price, inv unsold stock, target the stock it "
                     "aims at, cost unit labor cost, shock uniform 0-1. Prices stay in a band of markups over cost.",
              "default": "min(cost * (1 + markup), max(cost * (1 + markup_lo), p * (1 + theta_p * shock) if inv < target "
                         "else p * (1 - theta_p * shock)))"},
    "wage": {"vars": ("wage", "vac", "u", "pi", "shock"),
             "doc": "a firm's new wage offer per efficiency unit: wage its offer, vac vacancies it could not fill, "
                    "u unemployment rate, pi inflation (annual), shock uniform 0-1",
             "default": "wage * (1 + theta_w * shock) if vac > 0 else (wage * (1 - theta_w * shock) if u > ustar else wage)"},
    "policy": {"vars": ("pi", "u"), "doc": "the annual policy rate: pi annual inflation, u unemployment rate",
               "default": "max(0, rstar + pistar + phi_pi * (pi - pistar) + phi_u * (ustar - u))"},
}
ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp, ast.Call, ast.Name,
                 ast.Load, ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.USub, ast.UAdd,
                 ast.And, ast.Or, ast.Not, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)


class RuleError(ValueError):
    pass


def compile_rule(name, expr, params):
    """A formula becomes a fast function, after checking that it uses only allowed names and operations."""
    return compile_formula(name, expr, RULES[name]["vars"], params)


def compile_formula(name, expr, variables, params):
    """Check a formula against the whitelist (its variables, the parameters, numbers and FUNCS), then compile it."""
    spec = {"vars": tuple(variables)}
    if not isinstance(expr, str) or len(expr) > 2000:
        raise RuleError(f"{name}: a rule is a formula of at most 2000 characters")
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as x:
        raise RuleError(f"{name}: not a formula ({x.msg})")
    allowed = set(spec["vars"]) | set(params) | set(FUNCS)
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise RuleError(f"{name}: '{type(node).__name__}' is not allowed in a rule")
        if isinstance(node, ast.Name) and node.id not in allowed:
            raise RuleError(f"{name}: unknown name '{node.id}' (allowed: {', '.join(sorted(spec['vars']))}, "
                            f"the parameters and {', '.join(sorted(FUNCS))})")
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id in FUNCS):
            raise RuleError(f"{name}: only {', '.join(sorted(FUNCS))} can be called")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            raise RuleError(f"{name}: only numbers can appear as constants")
    lam = ast.Expression(body=ast.Lambda(
        args=ast.arguments(posonlyargs=[], args=[ast.arg(arg=v) for v in spec["vars"]], kwonlyargs=[], kw_defaults=[],
                           defaults=[]), body=tree.body))
    code = compile(ast.fix_missing_locations(lam), f"<rule {name}>", "eval")
    env = dict(FUNCS)
    env.update(params)
    env["__builtins__"] = {}
    return eval(code, env)  # noqa: S307 - the tree was checked against a whitelist above


# ------------------------------------------------------------------ entity types
# Households, firms, the bank, the government and the monetary authority are always there. Other kinds of entities
# are added per economy under "entities". Each kind is a set of parameters and three flow formulas, evaluated every
# quarter for each entity of that kind:
#   levy  money it collects from households (in proportion to their deposits, never more than they hold)
#   pay   money it pays to households (all, the employed or the unemployed, in equal parts)
#   buy   money it spends on goods, bought from firms' stocks after the government
# Every flow moves money between accounts, so the accounting check covers entities too. An entity's balance earns
# the deposit rate or, if negative, pays the loan rate to the bank, like the government's.
ENTITY_VARS = ("gdp", "cons", "wages", "dep", "bal", "u", "pi", "r", "t", "share", "shock")
ENTITY_VAR_DOC = ("gdp nominal output last quarter, cons household spending last quarter, wages the wage bill this "
                  "quarter, dep household deposits, bal the entity's own balance, u unemployment, pi inflation (annual), "
                  "r policy rate (annual), t the quarter, share 1/count for entities of one kind, shock uniform 0-1")
FLOWS = ("levy", "pay", "buy")
PAY_TO = ("all", "employed", "unemployed")
ENTITY_TYPES = {}


def entity_type(name, doc, params, flows, pay_to="all", start=0.0):
    """Register a kind of entity. params: {name: (default, low, high, meaning)}; flows: formulas for levy, pay, buy.
    Extensions can call this to add kinds; agents and people can also define one in a configuration ('custom')."""
    if not str(name).replace("_", "").isalnum():
        raise ValueError("an entity type name uses letters, digits and _ only")
    ENTITY_TYPES[name] = {"doc": doc, "params": dict(params), "flows": {f: flows.get(f, "0") for f in FLOWS},
                          "pay_to": pay_to, "start": float(start)}


entity_type("foreign", "the rest of the world: buys exports from firms and sells imports to households",
            {"export_share": (0.12, 0.0, 1.0, "exports as a share of last quarter's nominal output"),
             "import_share": (0.12, 0.0, 1.0, "imports as a share of last quarter's household spending"),
             "export_var": (0.2, 0.0, 2.0, "how much export demand varies from quarter to quarter")},
            {"buy": "share * export_share * gdp * (1 + export_var * (shock - 0.5))",
             "levy": "share * import_share * cons", "pay": "0"})
entity_type("pension_fund", "a fund that collects contributions on wages and pays out part of its assets to all households",
            {"contrib": (0.05, 0.0, 0.5, "contributions as a share of the wage bill"),
             "payout": (0.08, 0.0, 1.0, "share of its assets paid out each quarter")},
            {"levy": "share * contrib * wages", "pay": "payout * max(0, bal)", "buy": "0"})
entity_type("charity", "collects donations from households and pays them to the unemployed",
            {"donation": (0.002, 0.0, 0.1, "donations as a share of household deposits")},
            {"levy": "share * donation * dep", "pay": "max(0, bal)", "buy": "0"}, pay_to="unemployed")
entity_type("custom", "an entity defined entirely by its own parameters and flow formulas in the configuration",
            {}, {"levy": "0", "pay": "0", "buy": "0"})


def _entity_params(spec, P):
    typ = ENTITY_TYPES[spec["type"]]
    names = dict(P)
    names.update({k: v[0] for k, v in typ["params"].items()})
    names.update(spec.get("params") or {})
    return names


def check_entities(cfg):
    probs = []
    P = dict({k: v[0] for k, v in PARAMS.items()}, **(cfg.get("params") or {}))
    seen = set()
    for n, e in enumerate(cfg.get("entities") or []):
        label = f"entities[{n}]"
        if not isinstance(e, dict) or e.get("type") not in ENTITY_TYPES:
            probs.append([606, label, f"{label}: type must be one of {', '.join(sorted(ENTITY_TYPES))}"])
            continue
        typ = ENTITY_TYPES[e["type"]]
        name = e.get("name", e["type"])
        if name in seen:
            probs.append([606, label, f"{label}: two entities are named '{name}'; give each a name"])
        seen.add(name)
        c = e.get("count", 1)
        if not isinstance(c, int) or not 1 <= c <= 100000:
            probs.append([606, label, f"{label}: count must be a whole number from 1 to 100,000"])
        for k, v in (e.get("params") or {}).items():
            if not str(k).isidentifier() or k in ENTITY_VARS or k in FUNCS:
                probs.append([606, label, f"{label}: '{k}' cannot be a parameter name"])
            elif not isinstance(v, (int, float)) or abs(v) > 1e12 or v != v:
                probs.append([606, label, f"{label}: parameter {k} must be a number"])
            elif k in typ["params"] and not typ["params"][k][1] <= v <= typ["params"][k][2]:
                lo, hi = typ["params"][k][1], typ["params"][k][2]
                probs.append([602, label, f"{label}: {k} = {v} is outside [{lo}, {hi}]"])
        if e.get("pay_to", typ["pay_to"]) not in PAY_TO:
            probs.append([606, label, f"{label}: pay_to must be one of {', '.join(PAY_TO)}"])
        for f, expr in (e.get("flows") or {}).items():
            if f not in FLOWS:
                probs.append([606, label, f"{label}: flows are {', '.join(FLOWS)}, not '{f}'"])
        if probs and probs[-1][1] == label:
            continue
        names = _entity_params(e, P)
        for f in FLOWS:
            try:
                compile_formula(f"{name}.{f}", (e.get("flows") or {}).get(f, typ["flows"][f]), ENTITY_VARS, names)
            except RuleError as x:
                probs.append([601, label, str(x)])
    return probs


def _build_entities(cfg, P):
    out = []
    for e in cfg.get("entities") or []:
        typ = ENTITY_TYPES[e["type"]]
        names = _entity_params(e, P)
        fns = {f: compile_formula(f, (e.get("flows") or {}).get(f, typ["flows"][f]), ENTITY_VARS, names)
               for f in FLOWS}
        count = e.get("count", 1)
        for i in range(count):
            out.append({"name": e.get("name", e["type"]), "type": e["type"], "bal": float(e.get("start", typ["start"])),
                        "share": 1.0 / count, "pay_to": e.get("pay_to", typ["pay_to"]), "fns": fns, "budget": 0.0,
                        "levied": 0.0, "paid": 0.0, "bought": 0.0})
    return out


def default_config(households=1000, firms=50, periods=200, seed=1):
    return {"economy_version": 1, "households": households, "firms": firms, "periods": periods, "burn": 50,
            "seed": seed, "params": {k: v[0] for k, v in PARAMS.items()}, "rules": {}, "shocks": [], "entities": []}


def check_config(cfg):
    """Problems as [code, subject, message]: 601 bad rule, 602 parameter out of bounds, 605 bad structure."""
    probs = []
    for k in ("households", "firms", "periods"):
        v = cfg.get(k)
        if not isinstance(v, int) or v < 1:
            probs.append([605, k, f"{k} must be a positive whole number"])
    if isinstance(cfg.get("households"), int) and cfg["households"] > 1_000_000:
        probs.append([605, "households", "at most 1,000,000 households"])
    if isinstance(cfg.get("firms"), int) and isinstance(cfg.get("households"), int) and cfg["firms"] > cfg["households"]:
        probs.append([605, "firms", "more firms than households"])
    params = dict({k: v[0] for k, v in PARAMS.items()}, **(cfg.get("params") or {}))
    for k, v in (cfg.get("params") or {}).items():
        if k not in PARAMS:
            probs.append([602, k, f"unknown parameter '{k}'"])
        elif not isinstance(v, (int, float)) or not PARAMS[k][1] <= v <= PARAMS[k][2]:
            probs.append([602, k, f"{k} = {v} is outside [{PARAMS[k][1]}, {PARAMS[k][2]}]"])
    for name, expr in (cfg.get("rules") or {}).items():
        if name not in RULES:
            probs.append([601, name, f"unknown rule '{name}' (rules: {', '.join(RULES)})"])
            continue
        try:
            compile_rule(name, expr, params)
        except RuleError as x:
            probs.append([601, name, str(x)])
    for s in cfg.get("shocks") or []:
        if s.get("param") not in PARAMS or not isinstance(s.get("at"), int):
            probs.append([605, "shocks", f"a shock needs a known param, a value and a period 'at': {s}"])
    return probs + check_entities(cfg)


def _gini(xs):
    xs = sorted(max(0.0, x) for x in xs)
    n, s = len(xs), sum(xs)
    if n == 0 or s <= 0:
        return 0.0
    return (2 * sum((i + 1) * x for i, x in enumerate(xs)) / (n * s)) - (n + 1) / n


def run(cfg, series=False):
    """Simulate one economy. Returns moments, optional per-quarter series, and the accounting check."""
    probs = check_config(cfg)
    if probs:
        raise RuleError("; ".join(p[2] for p in probs))
    t_start = time.perf_counter()
    P = {k: v[0] for k, v in PARAMS.items()}
    P.update(cfg.get("params") or {})
    rng = random.Random(cfg.get("seed", 1))
    H, F, T = cfg["households"], cfg["firms"], cfg["periods"]
    burn = min(cfg.get("burn", 50), max(0, T - 2))
    rules = {n: compile_rule(n, (cfg.get("rules") or {}).get(n, RULES[n]["default"]), P) for n in RULES}
    consume, price_rule, wage_rule, policy_rule = rules["consume"], rules["price"], rules["wage"], rules["policy"]
    shocks = {}
    for s in cfg.get("shocks") or []:
        shocks.setdefault(s["at"], []).append(s)

    # ---------------------------------------------------------------- agents and accounts
    z = [math.exp(rng.gauss(-0.5 * P["z_sigma"] ** 2, P["z_sigma"])) for _ in range(H)]
    hh = [float(P["w0"])] * H                      # household deposits (never below zero)
    employer = [-1] * H
    res = [1.0] * H                                # reservation wage per efficiency unit
    firm = [float(P["firm_w0"])] * F               # firm deposits (negative = a loan from the bank)
    price = [1.0 + 0.05 * (rng.random() - 0.5) for _ in range(F)]
    wage = [1.0 / (1 + P["markup"])] * F           # wage offer per efficiency unit
    inv = [0.0] * F
    left = [0.0] * F                               # inventory left unsold at the end of the last quarter
    workers = [[] for _ in range(F)]
    eff = [0.0] * F                                # efficiency units employed
    exp_sales = [H * 0.9 * P["prod"] / F] * F
    vac_left = [0] * F
    gov, bank = 0.0, 0.0
    # hire an initial workforce so the economy starts near full employment
    order = list(range(H))
    rng.shuffle(order)
    for n, i in enumerate(order[: int(H * 0.94)]):
        j = n % F
        employer[i] = j
        workers[j].append(i)
        eff[j] += z[i]
    gov = -P["debt_target"] * 4 * sum(eff) * P["prod"]     # the government starts at its debt target
    ents = _build_entities(cfg, P)
    total0 = sum(hh) + sum(firm) + gov + bank + sum(e["bal"] for e in ents)

    pi, u, pbar_prev = P["pistar"], 1 - sum(1 for e in employer if e >= 0) / H, sum(price) / F
    gdp_nom_prev = sum(eff) * P["prod"] * pbar_prev
    dividends_hh = 0.0
    cons_prev = 0.8 * gdp_nom_prev
    out = {k: [] for k in ("gdp", "u", "pi", "rate", "pbar", "wage", "cons", "debt_gdp", "gini", "defaults",
                           "err", "deposits", "income", "firms_dep", "gov", "bank", "inv", "emp_eff", "entities")}
    max_err, defaults_total = 0.0, 0
    for t in range(T):
        for s in shocks.get(t, []):
            P[s["param"]] = s["value"]
            rules = {n: compile_rule(n, (cfg.get("rules") or {}).get(n, RULES[n]["default"]), P) for n in RULES}
            consume, price_rule, wage_rule, policy_rule = rules["consume"], rules["price"], rules["wage"], rules["policy"]
        # 1. the policy rate and interest: deposits earn it from the bank, loans pay the loan rate to it
        rate = policy_rule(pi, u)
        rd, rl = P["dep_share"] * rate / 4, (rate + P["spread"]) / 4
        paid, tax = 0.0, 0.0
        tau = P["tau"]
        for i in range(H):
            x = hh[i] * rd
            hh[i] += x - tau * x                    # interest, net of tax
            paid += x
            tax += tau * x
        for j in range(F):
            x = firm[j] * (rd if firm[j] > 0 else rl)
            firm[j] += x
            paid += x
        x = gov * (rd if gov > 0 else rl)
        gov += x + tax
        paid += x
        for e in ents:
            x = e["bal"] * (rd if e["bal"] > 0 else rl)
            e["bal"] += x
            paid += x
        bank -= paid
        # 2. firms plan output and hire or fire
        for j in range(F):
            need = max(0.0, exp_sales[j] * (1 + P["inv_target"]) - inv[j]) / P["prod"]
            gap = need - eff[j]
            avg_z = eff[j] / len(workers[j]) if workers[j] else 1.0
            if gap < -avg_z and workers[j]:
                for _ in range(min(len(workers[j]) - 1, int(-gap / avg_z))):
                    i = workers[j].pop(rng.randrange(len(workers[j])))
                    employer[i] = -1
                    eff[j] -= z[i]
                vac_left[j] = 0
            else:
                vac_left[j] = max(0, int(math.ceil(gap / avg_z)))
        # 3. the labor market: each unemployed household visits a few firms and takes the best offer
        hiring = [j for j in range(F) if vac_left[j] > 0]
        unemployed = [i for i in range(H) if employer[i] < 0]
        rng.shuffle(unemployed)
        k = int(P["search"])
        for i in unemployed:
            if not hiring:
                break
            best = -1
            for j in (hiring if len(hiring) <= k else rng.sample(hiring, k)):
                if vac_left[j] > 0 and wage[j] >= res[i] * 0.999 and (best < 0 or wage[j] > wage[best]):
                    best = j
            if best >= 0:
                employer[i] = best
                workers[best].append(i)
                eff[best] += z[i]
                vac_left[best] -= 1
                res[i] = wage[best]
                if vac_left[best] == 0:
                    hiring.remove(best)
            else:
                res[i] *= 1 - P["res_decay"]
        # 4. production, wages, benefits and taxes
        wage_bill = [0.0] * F
        avg_wage = 0.0
        n_emp = 0
        for j in range(F):
            inv[j] += P["prod"] * eff[j]
        income = [0.0] * H
        for j in range(F):
            wj = wage[j]
            for i in workers[j]:
                pay = wj * z[i]
                wage_bill[j] += pay
                income[i] = pay
                avg_wage += pay
                n_emp += 1
            firm[j] -= wage_bill[j]
        avg_wage = avg_wage / n_emp if n_emp else wage[0]
        b = P["benefit"] * avg_wage
        taxes, benefits = 0.0, 0.0
        div_each = dividends_hh / H
        for i in range(H):
            gross = income[i] + div_each
            tx = P["tau"] * gross
            taxes += tx
            if employer[i] < 0:
                gross += b
                benefits += b
            hh[i] += gross - tx
            income[i] = gross - tx
        gov += taxes - benefits
        # 4b. other entities: levies on and payments to households, and their purchases this quarter
        if ents:
            wages_total = sum(wage_bill)
            for e in ents:
                dep_total = sum(hh)
                v = (gdp_nom_prev, cons_prev, wages_total, dep_total, e["bal"], u, pi, rate, t, e["share"], rng.random())
                levy = min(max(0.0, e["fns"]["levy"](*v)), dep_total)
                if levy > 0:
                    f = levy / dep_total
                    got = 0.0
                    for i in range(H):
                        x = hh[i] * f
                        hh[i] -= x
                        got += x
                    e["bal"] += got
                    e["levied"] += got
                pay = max(0.0, e["fns"]["pay"](*v))
                to = [i for i in range(H) if e["pay_to"] == "all" or (employer[i] >= 0) == (e["pay_to"] == "employed")]
                if pay > 0 and to:
                    each = pay / len(to)
                    for i in to:
                        hh[i] += each
                        income[i] += each
                    e["bal"] -= each * len(to)
                    e["paid"] += each * len(to)
                e["budget"] = max(0.0, e["fns"]["buy"](*v))
        # 5. prices
        pbar = sum(price) / F
        for j in range(F):
            cost = wage[j] / P["prod"]
            price[j] = max(1e-6, price_rule(price[j], pbar, left[j], P["inv_target"] * exp_sales[j], cost, rng.random()))
        # 6. the goods market: the government buys first, then households spend at the cheapest of a few firms.
        #    Demand a firm could not serve is recorded, so that firms plan on demand, not only on sales.
        sales = [0.0] * F
        revenue = [0.0] * F
        unmet = [0.0] * F
        cons_total = 0.0
        # fiscal rule: purchases rise when debt is below its target and fall when it is above
        g_budget = max(0.0, P["g_share"] * gdp_nom_prev
                       + P["fiscal_rho"] * (gov + P["debt_target"] * 4 * gdp_nom_prev))
        stock = sum(inv)
        if stock > 0 and g_budget > 0:
            for j in range(F):
                if inv[j] <= 0:
                    continue
                want = g_budget * inv[j] / stock / price[j]
                q = min(inv[j], want)
                unmet[j] += want - q
                inv[j] -= q
                sales[j] += q
                revenue[j] += q * price[j]
                gov -= q * price[j]
        for e in ents:                               # other entities buy after the government
            stock = sum(inv)
            if e["budget"] <= 0 or stock <= 0:
                continue
            for j in range(F):
                if inv[j] <= 0:
                    continue
                want = e["budget"] * inv[j] / stock / price[j]
                q = min(inv[j], want)
                unmet[j] += want - q
                inv[j] -= q
                sales[j] += q
                revenue[j] += q * price[j]
                e["bal"] -= q * price[j]
                e["bought"] += q * price[j]
        hh_order = list(range(H))
        rng.shuffle(hh_order)
        F_list = range(F)
        for i in hh_order:
            budget = consume(income[i], hh[i] - income[i], pbar, u, z[i], rate, pi)
            budget = max(0.0, min(budget, hh[i]))
            if budget <= 0:
                continue
            visited = sorted(rng.sample(F_list, min(k, F)), key=price.__getitem__)
            for j in visited:
                if inv[j] <= 0:
                    continue
                q = min(inv[j], budget / price[j])
                spend = q * price[j]
                inv[j] -= q
                sales[j] += q
                revenue[j] += spend
                hh[i] -= spend
                budget -= spend
                cons_total += spend
                if budget <= 1e-12:
                    break
            if budget > 1e-12:
                j = visited[0]                       # the cheapest firm visited sees the demand it could not serve
                unmet[j] += budget / price[j]
        # 7. profits, dividends, wage offers, defaults
        dividends_hh = 0.0
        defaults = 0
        left = list(inv)
        for j in range(F):
            firm[j] += revenue[j]
            profit = revenue[j] - wage_bill[j]
            if firm[j] > 0:
                d = min(firm[j], P["payout"] * max(0.0, profit) + max(0.0, firm[j] - P["cash_buffer"] * wage_bill[j]))
                firm[j] -= d
                dividends_hh += d
            exp_sales[j] += P["lam"] * (sales[j] + unmet[j] - exp_sales[j])
            wage[j] = max(1e-6, wage_rule(wage[j], vac_left[j], u, pi, rng.random()))
            if firm[j] < -P["default_after"] * max(wage_bill[j], 1e-9):
                bank += firm[j]                     # the bank writes off the loan
                firm[j] = 0.0
                for i in workers[j]:
                    employer[i] = -1
                workers[j], eff[j], inv[j] = [], 0.0, 0.0
                price[j], wage[j] = pbar, avg_wage / max(1e-9, sum(z) / H)
                exp_sales[j] = sum(exp_sales) / F
                defaults += 1
        defaults_total += defaults
        # bank dividends: the bank pays its positive equity above zero to households, as dividends next quarter
        if bank > 0:
            dividends_hh += bank
            bank = 0.0
        # 8. the period's statistics and the accounting check
        gdp = sum(sales)
        pbar_new = sum(p * s for p, s in zip(price, sales)) / gdp if gdp > 0 else sum(price) / F
        pi = (pbar_new / pbar_prev) ** 4 - 1 if pbar_prev > 0 else 0.0
        pbar_prev = pbar_new
        u = 1 - sum(1 for e in employer if e >= 0) / H
        gdp_nom_prev = gdp * pbar_new
        cons_prev = cons_total
        total = sum(hh) + sum(firm) + gov + bank + dividends_hh + sum(e["bal"] for e in ents)
        err = abs(total - total0) / max(1.0, abs(total0))
        max_err = max(max_err, err)
        for key, val in (("gdp", gdp), ("u", u), ("pi", pi), ("rate", rate), ("pbar", pbar_new), ("wage", avg_wage),
                         ("cons", cons_total), ("debt_gdp", -gov / (4 * gdp_nom_prev) if gdp_nom_prev else 0.0),
                         ("defaults", defaults), ("err", err), ("deposits", sum(hh) / H),
                         ("income", sum(income) / H), ("firms_dep", sum(firm)), ("gov", gov), ("bank", bank), ("inv", sum(inv)), ("emp_eff", sum(eff)),
                         ("entities", sum(e["bal"] for e in ents))):
            out[key].append(val)
        out["gini"].append(_gini(hh) if (t == T - 1 or series) else (out["gini"][-1] if out["gini"] else 0.0))

    # ---------------------------------------------------------------- moments after the burn-in
    def mean(xs):
        return sum(xs) / len(xs) if xs else 0.0

    def sd(xs):
        m = mean(xs)
        return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) if len(xs) > 1 else 0.0
    g = out["gdp"][burn:]
    growth = [math.log(b / a) for a, b in zip(g, g[1:]) if a > 0 and b > 0]
    ac = 0.0
    if len(growth) > 2 and sd(growth) > 0:
        m = mean(growth)
        ac = sum((x - m) * (y - m) for x, y in zip(growth, growth[1:])) / ((len(growth) - 1) * sd(growth) ** 2)
    nominal = [x * p for x, p in zip(out["gdp"][burn:], out["pbar"][burn:])]
    moments = {"unemployment": mean(out["u"][burn:]), "inflation": mean(out["pi"][burn:]),
               "growth_sd": sd(growth), "growth_ac1": ac, "policy_rate": mean(out["rate"][burn:]),
               "cons_share": mean([c / n for c, n in zip(out["cons"][burn:], nominal) if n > 0]),
               "debt_gdp": out["debt_gdp"][-1], "wealth_gini": out["gini"][-1],
               "default_rate": defaults_total / (F * T), "output": mean(g)}
    res_ = {"moments": moments, "accounting_error": max_err, "seconds": round(time.perf_counter() - t_start, 3),
            "households": H, "firms": F, "periods": T}
    if ents:
        summary = {}
        for e in ents:
            s = summary.setdefault(e["name"], {"type": e["type"], "count": 0, "levied": 0.0, "paid": 0.0,
                                               "bought": 0.0, "balance": 0.0})
            s["count"] += 1
            for key in ("levied", "paid", "bought"):
                s[key] += e[key]
            s["balance"] += e["bal"]
        res_["entities"] = summary
    if series:
        res_["series"] = {k: [round(x, 6) for x in v] for k, v in out.items()}
    return res_


def _run_one(args):
    cfg, series = args
    return run(cfg, series)


def run_many(cfgs, workers=None, series=False):
    """Many runs (seeds, scenarios, candidates) in parallel processes."""
    main_file = getattr(sys.modules.get("__main__"), "__file__", None)
    if len(cfgs) == 1 or workers == 1 or not (main_file and os.path.isfile(main_file)):
        return [run(c, series) for c in cfgs]       # one run, or no importable main module to spawn from
    import concurrent.futures as cf
    workers = workers or min(len(cfgs), os.cpu_count() or 2)
    with cf.ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_run_one, [(c, series) for c in cfgs]))


def average(results):
    keys = results[0]["moments"].keys()
    return {k: sum(r["moments"][k] for r in results) / len(results) for k in keys}


# ------------------------------------------------------------------ known answers for the engine
def known_answers():
    """(name, ok, detail): accounting, determinism, a stationary wealth level and the policy rule."""
    rows = []
    base = default_config(households=300, firms=15, periods=80)
    r1, r2 = run(base), run(base)
    rows.append(("money is conserved every quarter", r1["accounting_error"] < 1e-9,
                 f"largest relative error {r1['accounting_error']:.2e}"))
    rows.append(("same seed, same economy", r1["moments"] == r2["moments"], "moments identical"))
    r3 = run(dict(base, seed=2))
    rows.append(("another seed, another draw", r3["moments"] != r1["moments"], "moments differ"))
    # stationary deposits: one household type, no taxes, no government, no interest, fixed prices and wages.
    # With spending c = mpc_y * y + mpc_w * w, deposits settle where c = y: w* = (1 - mpc_y) * y / mpc_w.
    cfg = default_config(households=200, firms=10, periods=400)
    cfg["burn"] = 300
    cfg["params"].update({"z_sigma": 0.0, "tau": 0.0, "benefit": 0.0, "g_share": 0.0, "rstar": 0.0, "pistar": 0.0,
                          "phi_pi": 0.0, "phi_u": 0.0, "spread": 0.0, "theta_p": 0.0, "theta_w": 0.0, "payout": 1.0,
                          "mpc_y": 0.8, "mpc_w": 0.1, "search": 10, "fiscal_rho": 0.0, "debt_target": 0.0})
    cfg["params"].update({"w0": 0.4, "firm_w0": 2.0})   # little money: demand, not capacity, sets output
    cfg["rules"] = {"wage": "wage", "price": "p", "policy": "0", "consume": "min(w + y, mpc_y * y + mpc_w * w)"}
    s = run(cfg, series=True)["series"]
    y = sum(s["income"][-100:]) / 100
    got = sum(s["deposits"][-100:]) / 100
    expected = (1 - 0.8) * y / 0.1
    rows.append(("stationary deposits equal (1 - mpc_y) y / mpc_w", abs(got - expected) <= 0.01 * expected,
                 f"expected {expected:.4f}, got {got:.4f}"))
    # an entity added by configuration: it collects exactly 10 a quarter, and money is still conserved
    cfg = default_config(households=200, firms=10, periods=50)
    cfg["params"]["dep_share"] = 0.0
    cfg["entities"] = [{"type": "custom", "name": "collector", "params": {"take": 10}, "flows": {"levy": "take"}},
                       {"type": "foreign"}, {"type": "pension_fund", "count": 2}]
    r = run(cfg)
    got = r["entities"]["collector"]["balance"]
    rows.append(("an entity added by configuration collects exactly what its formula says",
                 abs(got - 500) < 1e-9 and r["accounting_error"] < 1e-9,
                 f"expected 500, got {got:.9f}; accounts off by {r['accounting_error']:.1e}"))
    # the policy rule at known points
    pol = compile_rule("policy", RULES["policy"]["default"], {k: v[0] for k, v in PARAMS.items()})
    want = 0.02 + 0.02 + 1.5 * (0.04 - 0.02) + 0.5 * (0.06 - 0.08)
    rows.append(("policy rule at inflation 4% and unemployment 8%", abs(pol(0.04, 0.08) - want) < 1e-12,
                 f"expected {want:.4f}, got {pol(0.04, 0.08):.4f}"))
    rows.append(("policy rate is not negative", pol(-0.10, 0.30) == 0, f"got {pol(-0.10, 0.30)}"))
    try:
        compile_rule("consume", "__import__('os')", {})
        rows.append(("a rule cannot call anything outside the list", False, "accepted"))
    except RuleError:
        rows.append(("a rule cannot call anything outside the list", True, "refused"))
    return rows


# ------------------------------------------------------------------ protocol operations
def register(api):
    api.code(601, "bad_rule", "a behaviour rule is not a valid formula or uses names that are not allowed")
    api.code(602, "bad_param", "a parameter is unknown or outside its bounds")
    api.code(603, "not_conserved", "money was created or destroyed: the accounts do not add up")
    api.code(605, "bad_economy", "the economy's structure is not valid")
    api.code(606, "bad_entity", "an entity in the economy is not valid: unknown type, bad count, parameter or flow")
    op, ok, E = api.op, api.ok, api.OpError

    def cfg_of(a):
        if "d" in a or "t" in a or "m" in a:
            src = api.resolve(a)
            return src.doc, src.h
        raise E(102, "give the economy: d (inline), t (workspace track) or m (file)")

    @op("economy.new", "a new economy configuration with the default parameters and rules", {
        "households": "int? default 1000", "firms": "int? default 50", "periods": "int? quarters, default 200",
        "seed": "int? default 1", "params": "obj? parameters to change",
        "entities": "list? other entities, e.g. [{\"type\": \"foreign\"}, {\"type\": \"custom\", \"name\": ..., "
                    "\"params\": {...}, \"flows\": {\"levy\": ..., \"pay\": ..., \"buy\": ...}}]"})
    def new(a, ctx):
        cfg = default_config(a.get("households", 1000), a.get("firms", 50), a.get("periods", 200), a.get("seed", 1))
        cfg["params"].update(a.get("params") or {})
        cfg["entities"] = list(a.get("entities") or [])
        probs = check_config(cfg)
        return ok({"d": cfg}, e=[[c, s, m] for c, s, m in probs] or None, h=api.fingerprint(cfg))

    @op("economy.entities", "the kinds of entities an economy can add, with their parameters and flow formulas", {})
    def entities(a, ctx):
        return ok({"vars": ENTITY_VAR_DOC, "flows": {"levy": "collected from households, in proportion to deposits",
                                                     "pay": "paid to households in equal parts (pay_to: all, employed "
                                                            "or unemployed)",
                                                     "buy": "spent on goods from firms' stocks, after the government"},
                   "types": {k: {"doc": v["doc"], "params": {p: {"v": d[0], "lo": d[1], "hi": d[2], "s": d[3]}
                                                             for p, d in v["params"].items()},
                                 "flows": v["flows"], "pay_to": v["pay_to"]} for k, v in ENTITY_TYPES.items()}})

    @op("economy.params", "the parameters: default, lower and upper bound, meaning", {})
    def params(a, ctx):
        return ok({k: {"v": v[0], "lo": v[1], "hi": v[2], "s": v[3]} for k, v in PARAMS.items()})

    @op("economy.rules", "the behaviour rules: their variables, meaning and default formulas", {})
    def rules(a, ctx):
        return ok({k: {"vars": v["vars"], "doc": v["doc"], "default": v["default"]} for k, v in RULES.items()})

    @op("economy.check", "check an economy configuration: parameters within bounds, rules valid", {
        "d": "obj? inline configuration (or t, or m)"})
    def check(a, ctx):
        cfg, h = cfg_of(a)
        probs = check_config(cfg)
        return ok({"pass": not probs}, e=[[c, s, m] for c, s, m in probs] or None, h=h)

    @op("economy.run", "simulate the economy; returns moments and the accounting check (seeds run in parallel)", {
        "d": "obj? inline configuration (or t, or m)", "seeds": "list? run once per seed and average",
        "series": "bool? include the quarterly series", "set": "obj? parameters to change for this run only",
        "workers": "int? parallel processes"})
    def run_op(a, ctx):
        cfg, h = cfg_of(a)
        cfg = copy.deepcopy(cfg)
        if a.get("set"):
            cfg.setdefault("params", {}).update(a["set"])
        probs = check_config(cfg)
        if probs:
            raise E(probs[0][0], probs[0][2], data={"problems": probs})
        seeds = a.get("seeds") or [cfg.get("seed", 1)]
        res = run_many([dict(cfg, seed=s) for s in seeds], a.get("workers"), bool(a.get("series")))
        err = max(r["accounting_error"] for r in res)
        out = {"moments": average(res), "accounting_error": err, "runs": len(res),
               "seconds": round(sum(r["seconds"] for r in res), 3)}
        if res[0].get("entities"):
            out["entities"] = res[0]["entities"]
        if len(res) > 1:
            out["by_seed"] = [r["moments"] for r in res]
        if a.get("series"):
            out["series"] = res[0]["series"]
        resp = ok(out, h=h)
        if err > 1e-9:
            resp["e"] = [[603, "", f"accounts off by {err:.2e}"]]
        return resp

    @op("economy.known", "known-answer tests of the economy engine", {})
    def known(a, ctx):
        rows = known_answers()
        bad = [[r[0], r[2]] for r in rows if not r[1]]
        return ok({"pass": not bad, "tests": [[r[0], bool(r[1]), r[2]] for r in rows]},
                  e=[[604, "", n, d] for n, d in bad] or None)

    api.code(604, "economy_known_answer_failed", "a known-answer test of the economy engine failed")
    return api


# ------------------------------------------------------------------ command line
def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="An agent-based economy")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("--config")
    p.add_argument("--households", type=int, default=1000)
    p.add_argument("--firms", type=int, default=50)
    p.add_argument("--periods", type=int, default=200)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--seeds", type=int, help="run this many seeds in parallel and average")
    p.add_argument("--set", nargs="*", default=[], metavar="PARAM=VALUE")
    p.add_argument("--entity", action="append", default=[], metavar="TYPE[:COUNT]",
                   help="add entities of a kind, e.g. --entity foreign --entity pension_fund:3")
    p.add_argument("--out")
    sub.add_parser("rules")
    sub.add_parser("params")
    sub.add_parser("entities")
    sub.add_parser("known")
    p = sub.add_parser("scale")
    p.add_argument("--max", type=int, default=100000)
    a = ap.parse_args(argv)
    if a.cmd == "rules":
        for k, v in RULES.items():
            print(f"{k}: {v['doc']}\n    {v['default']}\n")
    elif a.cmd == "entities":
        print(f"Variables in flow formulas: {ENTITY_VAR_DOC}\n")
        for k, v in ENTITY_TYPES.items():
            print(f"{k}: {v['doc']} (pays: {v['pay_to']})")
            for f in FLOWS:
                print(f"    {f:<5} {v['flows'][f]}")
            for p_, d in v["params"].items():
                print(f"    {p_} = {d[0]:g} [{d[1]:g}, {d[2]:g}]  {d[3]}")
            print()
    elif a.cmd == "params":
        for k, v in PARAMS.items():
            print(f"{k:<14} {v[0]:<8g} [{v[1]:g}, {v[2]:g}]  {v[3]}")
    elif a.cmd == "known":
        rows = known_answers()
        for name, good, detail in rows:
            print(f"{'PASS' if good else 'FAIL'}  {name}: {detail}")
        print(f"RESULT: {'PASS' if all(r[1] for r in rows) else 'FAIL'}")
        return 0 if all(r[1] for r in rows) else 1
    elif a.cmd == "scale":
        n = 1000
        while n <= a.max:
            r = run(default_config(households=n, firms=max(10, n // 20), periods=100))
            m = r["moments"]
            print(f"{n:>8} households {max(10, n // 20):>6} firms  100 quarters  {r['seconds']:>7.2f}s  "
                  f"unemployment {m['unemployment']:.3f}  accounts off by {r['accounting_error']:.1e}")
            n *= 10
    else:
        cfg = default_config(a.households, a.firms, a.periods, a.seed)
        if a.config:
            with open(a.config, encoding="utf-8") as f:
                cfg = json.load(f)
        for kv in a.set:
            k, _, v = kv.partition("=")
            cfg["params"][k] = float(v)
        for spec in a.entity:
            typ, _, n = spec.partition(":")
            cfg.setdefault("entities", []).append({"type": typ, "count": int(n or 1)})
        probs = check_config(cfg)
        if probs:
            print("\n".join(p[2] for p in probs))
            return 1
        cfgs = [dict(cfg, seed=cfg["seed"] + s) for s in range(a.seeds)] if a.seeds else [cfg]
        res = run_many(cfgs, series=not a.seeds)
        m = average(res)
        print(f"{cfg['households']} households, {cfg['firms']} firms, {cfg['periods']} quarters, {len(res)} run(s), "
              f"{sum(r['seconds'] for r in res):.2f}s of compute")
        for k, v in m.items():
            print(f"  {k:<14} {v:.4f}")
        print(f"  accounts off by at most {max(r['accounting_error'] for r in res):.1e} (relative)")
        for name, s in (res[0].get("entities") or {}).items():
            print(f"  {name} ({s['type']}, {s['count']}): collected {s['levied']:.1f}, paid {s['paid']:.1f}, "
                  f"bought {s['bought']:.1f}, balance {s['balance']:.1f}")
        if a.out:
            with open(a.out, "w", encoding="utf-8") as f:
                json.dump({"config": cfg, "results": res}, f, indent=1)
            print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
