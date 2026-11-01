#!/usr/bin/env python3
"""PreToolUse hook for file tools: protect restricted data, secrets and immutable raw data.

Exit code 2 blocks the call and returns the message on stderr to the agent.
"""
import json
import os
import re
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    sys.exit(0)

# Cursor's permission hooks expect a JSON decision on stdout; Claude Code only needs the exit code.
CURSOR = data.get("hook_event_name") in ("beforeShellExecution", "beforeReadFile")


def block(msg):
    print(msg, file=sys.stderr)
    if CURSOR:
        print(json.dumps({"permission": "deny", "user_message": msg, "agent_message": msg}))
    sys.exit(2)


def allow():
    if CURSOR:
        print(json.dumps({"permission": "allow"}))
    sys.exit(0)


tool = data.get("tool_name", "")
ti = data.get("tool_input") or data  # Claude Code nests the input; Cursor sends file_path at the top level
cands = [str(ti.get(k)) for k in ("file_path", "path", "pattern", "glob") if ti.get(k)]
norm = [c.replace("\\", "/").lower() for c in cands]

for p in norm:
    if re.search(r"(^|/)data/(restricted|confidential)(/|$)", p):
        block("BLOCKED: data/restricted holds restricted or confidential data and is off-limits to agents. "
              "Ask the user for aggregated or synthetic stand-ins.")
    if re.search(r"(^|/)\.env(\.|$)|(^|/)credentials|\.pem$|\.key$|id_rsa", p):
        block("BLOCKED: credential and secret files are off-limits.")

if tool in ("Write", "Edit", "MultiEdit"):
    for c, p in zip(cands, norm):
        if re.search(r"(^|/)data/raw/", p) and os.path.exists(c):
            block("BLOCKED: data/raw is immutable. Write a new vintage file or a processed version instead.")

allow()
