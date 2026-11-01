#!/usr/bin/env python3
"""PreToolUse hook for shell tools: block destructive commands and exfiltration of protected data.

Exit code 2 blocks the call and returns the message on stderr to the agent.
"""
import glob
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


cmd = (data.get("tool_input") or {}).get("command", "") or data.get("command", "") or ""  # Claude Code / Cursor
low = cmd.lower()

DESTRUCTIVE = [
    (r"\brm\s+(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r|--recursive|--force)", "recursive/forced delete"),
    (r"remove-item\b.*-recurse", "recursive delete"),
    (r"-recurse\b.*\|\s*remove-item\b", "recursive delete"),
    (r"\bgit\s+push\b.*(--force|\s-f\b|\s\+)", "force push"),
    (r"\bgit\s+reset\s+--hard", "hard reset"),
    (r"\bgit\s+clean\b.*-[a-z]*f", "git clean"),
    (r"\bsudo\b", "privilege escalation"),
    (r"\bchmod\s+777", "world-writable permissions"),
    (r"\bformat\s+[a-z]:", "disk format"),
]
# Check each statement on its own, so a harmless `Get-ChildItem -Recurse` later on the line does not
# turn an unrelated `Remove-Item file` into a "recursive delete". Pipelines stay in one statement.
for stmt in re.split(r";|&&|\|\||\n", low):
    for pat, why in DESTRUCTIVE:
        if re.search(pat, stmt):
            block(f"BLOCKED: {why} is not allowed in this studio. Ask the user to run it manually if truly needed.")

NETWORK = r"\b(curl|wget|scp|sftp|ftp|invoke-webrequest|invoke-restmethod|iwr|irm|nc|netcat|rclone|aws\s+s3|az\s+storage)\b"
if re.search(NETWORK, low) and re.search(r"data[\\/]+(restricted|confidential)", low):
    block("BLOCKED: restricted/confidential data must not be sent over the network. See .claude/docs/confidentiality-and-ai-use.md.")

if re.search(r"\bgit\s+(add|commit)\b", low) and re.search(r"data[\\/]+(restricted|raw)|\.env\b", low):
    block("BLOCKED: do not stage restricted data, raw data or .env files for commit.")

# Raw data is immutable (the file-tool guard covers Write/Edit; this covers the shell). A new vintage may be
# written into data/raw, but a shell command may not change, move, overwrite or delete a raw file that exists.
RAW_PATH = r"""((?:[A-Za-z]:)?[^\s'"<>|;&()]*data[\\/]+raw[\\/]+[^\s'"<>|;&()]*)"""
# commands that change, move or delete the paths they are given
MODIFY = (r"\b(rm|del|erase|rmdir|mv|move|ren|rename|truncate|shred|unlink|ri|mi|rni)\b|\bsed\b.*\s(-i|--in-place)"
          r"|\bperl\b.*\s-\w*i|\b(remove|move|rename)-item\b|\b(clear|set|add)-content\b|\bout-file\b")
# commands that overwrite their last argument
COPY = r"\b(cp|copy|cpi|copy-item|xcopy|robocopy)\b"
base = data.get("cwd") or os.getcwd()


def raw_exists(path):
    full = path if os.path.isabs(path) else os.path.join(base, path)
    return bool(glob.glob(full)) if any(ch in full for ch in "*?[") else os.path.exists(full)


for stmt in re.split(r";|&&|\|\||\n", cmd):
    for seg in stmt.split("|"):  # each pipeline segment on its own: reading raw data into a pipeline is fine
        paths = re.findall(RAW_PATH, seg)
        if not any(raw_exists(x) for x in paths):
            continue
        redirect = re.search(r"(?:>>?|\btee\b(?:\s+-\w+)*)\s*['\"]?" + RAW_PATH, seg)
        overwrite = re.search(COPY, seg, re.I) and seg.rstrip().rstrip("'\"").endswith(paths[-1]) and raw_exists(paths[-1])
        if re.search(MODIFY, seg, re.I) or (redirect and raw_exists(redirect.group(1))) or overwrite:
            block("BLOCKED: data/raw is immutable. Write a new vintage file or a processed version instead.")

allow()
