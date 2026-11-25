"""Swarm: 100 built-in agents calibrate the AEL economy through the protocol and the shared workspace; a person
steps in after round 3, leaves a constraint and freezes theta_w. Saves stdout, the final report and the workspace."""
import os
import subprocess
import sys
import time

from common import TOOLS, run_dir, log

started = time.strftime("%Y-%m-%d %H:%M:%S")
d = run_dir("swarm")
ws = os.path.join(d, "workspace.db")
if os.path.exists(ws):
    os.remove(ws)
cmd = [sys.executable, os.path.join(TOOLS, "swarm.py"), "--agents", "100", "--households", "1000", "--rounds", "6",
       "--person-at", "3", "keep the tax rate as it is", "--ws", ws, "--report", os.path.join(d, "swarm-report.md")]
t0 = time.time()
p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
with open(os.path.join(d, "stdout.txt"), "w", encoding="utf-8") as f:
    f.write(p.stdout + "\n--- stderr ---\n" + p.stderr)
log(d, started, {"command": cmd[1:], "returncode": p.returncode, "seconds": round(time.time() - t0, 1)})
print(p.stdout[-4000:])
print(p.stderr[-2000:])
