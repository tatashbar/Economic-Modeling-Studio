"""Shared helpers for the paper's experiments: paths, run logs and the pinned studio version."""
import json
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # paper/em2026

def _find_ems():
    """The studio's root: EMS_ROOT if set, else a folder 'ems' next to this one, else the nearest parent with tools/economy.py."""
    if os.environ.get("EMS_ROOT"):
        return os.environ["EMS_ROOT"]
    if os.path.isfile(os.path.join(ROOT, "ems", "tools", "economy.py")):
        return os.path.join(ROOT, "ems")
    d = ROOT
    while True:
        if os.path.isfile(os.path.join(d, "tools", "economy.py")):
            return d
        up = os.path.dirname(d)
        if up == d:
            raise SystemExit("cannot find the studio (tools/economy.py); set EMS_ROOT")
        d = up


EMS = _find_ems()                                  # Economic Modeling Studio (results use commit 76797db)
TOOLS = os.path.join(EMS, "tools")
OUT = os.path.join(ROOT, "output")
sys.path.insert(0, TOOLS)


def commit():
    try:
        return subprocess.check_output(["git", "-C", EMS, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def run_dir(name):
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    return d


def save(d, fname, obj):
    with open(os.path.join(d, fname), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)


def log(d, started, extra=None):
    info = {"script": os.path.basename(sys.argv[0]), "args": sys.argv[1:], "started": started,
            "finished": time.strftime("%Y-%m-%d %H:%M:%S"), "studio_commit": commit(),
            "python": sys.version.split()[0], "platform": platform.platform(),
            "cpus": os.cpu_count()}
    info.update(extra or {})
    save(d, "run-log.json", info)
