#!/usr/bin/env python3
"""SubagentStart hook: append an audit-trail line for every subagent that starts."""
import datetime
import json
import os
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    data = {}

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = os.path.join(root, "production", "session-state")
os.makedirs(d, exist_ok=True)
rec = {
    "time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "agent": data.get("agent_type") or data.get("subagent_type") or data.get("agent_name") or "unknown",
    "agent_id": data.get("agent_id", ""),
    "session": data.get("session_id", ""),
}
with open(os.path.join(d, "agent-audit.log"), "a", encoding="utf-8") as f:
    f.write(json.dumps(rec) + "\n")
sys.exit(0)
