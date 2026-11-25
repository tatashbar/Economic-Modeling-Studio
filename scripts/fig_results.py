"""Fig. 2 (RSIM vs random search) and Fig. 3 (policy responses), read from saved run outputs."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import ROOT
from tables import J

FIG = os.path.join(ROOT, "figures")
plt.rcParams.update({"font.size": 9.5, "font.family": "Palatino Linotype", "axes.edgecolor": "#4a4a4a",
                     "axes.labelcolor": "#2b2b2b", "xtick.color": "#4a4a4a", "ytick.color": "#4a4a4a",
                     "axes.titleweight": "bold"})
TEAL, WINE, OCHRE, INDIGO = "#00676B", "#9E1B32", "#C99A2E", "#3B3B98"

R = J("rsim", "rsim-vs-random.json")
if R:
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    for r in R["reps"]:
        xs = [x["evals"] for x in r["rsim"]["rounds"] if x["champion_loss"] is not None]
        ys = [x["champion_loss"] for x in r["rsim"]["rounds"] if x["champion_loss"] is not None]
        ax.plot(xs, ys, "-o", ms=2.5, color=TEAL, alpha=0.9, label="RSIM" if r["rep"] == 1 else None)
        ax.plot([p["evals"] for p in r["random"]["path"]], [p["best_loss"] for p in r["random"]["path"]], "--",
                color=WINE, alpha=0.9, label="Random search" if r["rep"] == 1 else None)
    ax.set_yscale("log")
    ax.set_xlabel("Model runs used (training seeds, plus hidden seeds for RSIM)")
    ax.set_ylabel("Best training loss (log scale)")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"Figure_2.{ext}"), dpi=400)

P = J("ael-policy", "policy.json")
if P:
    s0 = P["series_start_index_of_shock"]
    H = 80
    panels = [("real_gdp", "Real output (% of baseline)", 1), ("u", "Unemployment (pp)", 100),
              ("pi", "Inflation (pp)", 100), ("rate", "Policy rate (pp)", 100), ("debt_gdp", "Debt/GDP (pp)", 100)]
    cases = [("s1_default_rule", "+3 pp, default rule", TEAL, "-"),
             ("s2_strict_rule", "+3 pp, strict inflation targeting", OCHRE, "--"),
             ("s3_no_brake", "+6 pp, no debt brake", WINE, "-"),
             ("s3_brake", "+6 pp, debt brake", INDIGO, ":")]
    fig, grid = plt.subplots(3, 2, figsize=(6.6, 8.2))
    axes = grid.flatten()
    for ax, (k, lab, sc) in zip(axes, panels):
        for key, name, col, ls in cases:
            m = P["irf"][key][k]["mean"][s0 - 4:s0 + H]
            ax.plot(range(-4, -4 + len(m)), [sc * x if x is not None else None for x in m], ls, color=col, lw=1.3, label=name)
        ax.axhline(0, color="#999999", lw=0.6)
        ax.axvline(0, color="#bbbbbb", lw=0.6)
        ax.set_title(lab, fontsize=10)
        ax.set_xlabel("Quarters after the change")
        ax.spines[["top", "right"]].set_visible(False)
    h, l = axes[0].get_legend_handles_labels()
    axes[5].axis("off")
    axes[5].legend(h, l, loc="center", frameon=False, fontsize=9, title="Scenario")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"Figure_3.{ext}"), dpi=400)
print("figures done")
