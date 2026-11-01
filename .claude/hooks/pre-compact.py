#!/usr/bin/env python3
"""PreCompact hook: remind to preserve session state before context is compacted."""
import os

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(root, "production", "session-state", "active.md")
print("Before compaction: keep decisions, approved sections, data vintages, model versions and open questions.")
if os.path.exists(path):
    print("Session state file: production/session-state/active.md (re-read it after compaction).")
else:
    print("No production/session-state/active.md yet. Write one with the current task, decisions and next step.")
