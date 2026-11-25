"""Summarise the swarm run from its saved stdout and workspace (output/swarm), including how the freeze was applied."""
import json
import os
import re
import sqlite3

from common import OUT, save

d = os.path.join(OUT, "swarm")
txt = open(os.path.join(d, "stdout.txt"), encoding="utf-8").read()
c = sqlite3.connect(os.path.join(d, "workspace.db"))
freeze_ts = c.execute("SELECT ts FROM freezes WHERE brick = 'theta_w'").fetchone()[0]
champs = c.execute("SELECT id, round, by, params, ts, loss, hidden_loss FROM candidates WHERE status = 'champion' ORDER BY id").fetchall()
late = [{"id": r[0], "proposed_before_freeze": r[4] < freeze_ts, "theta_w": json.loads(r[3]).get("theta_w")}
        for r in champs if "theta_w" in json.loads(r[3])]
dist = [float(x) for x in re.findall(r"distance ([0-9.]+)\n", txt)]
dist = [float(x) for x in re.findall(r"^round \d+:.*?distance ([0-9.]+)", txt, re.M)]
RES = re.search(r"results: unemployment ([0-9.]+), inflation ([0-9.]+), wealth_gini ([0-9.]+)", txt)
s = {
    "agents": 100,
    "messages": int(re.search(r"(\d+) protocol messages", txt).group(1)),
    "seconds": int(re.search(r"messages in (\d+)s", txt).group(1)),
    "rounds": len(re.findall(r"^round \d+:", txt, re.M)),
    "dist_first": dist[0], "dist_last": dist[-1],
    "hidden_last": float(re.search(r"hidden cases ([0-9.]+)", txt).group(1)),
    "refused_503": int(re.search(r"503: (\d+)", txt).group(1)),
    "refused_504": int(re.search(r"504: (\d+)", txt).group(1)),
    "overfit": len(re.findall(r"refused by the hidden cases", txt)),
    "readers": int(re.search(r"(\d+) agents had read", txt).group(1)),
    "u": float(RES.group(1)), "pi": float(RES.group(2)), "gini": float(RES.group(3)),
    "theta_w_changes_after_freeze": late,
}
save(d, "swarm-summary.json", s)
print(json.dumps(s, indent=1))
