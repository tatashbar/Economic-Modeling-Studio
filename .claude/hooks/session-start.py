#!/usr/bin/env python3
"""SessionStart hook: print studio context (stage, active task, latest gate) for the session."""
import os
import glob


def read(path, limit=40):
    try:
        with open(path, encoding="utf-8") as f:
            return "".join(f.readlines()[:limit]).strip()
    except OSError:
        return ""


root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("=== Economic Modeling Studio ===")
stage = read(os.path.join(root, "production", "stage.txt"), 1)
print(f"Project stage: {stage or 'not detected (run /project-stage-detect or /start)'}")

active = read(os.path.join(root, "production", "session-state", "active.md"))
if active:
    print("\n--- Active session state (production/session-state/active.md) ---")
    print(active)

gates = sorted(glob.glob(os.path.join(root, "production", "gates", "*.md")), key=os.path.getmtime)
if gates:
    print(f"\nLatest gate report: {os.path.relpath(gates[-1], root)}")

print("\nRules: no fabricated data; independent validation; benchmark first; respect data classification levels.")
print("Type /start to begin or /help for options.")
