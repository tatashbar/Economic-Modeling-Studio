#!/usr/bin/env python3
"""PostToolUse hook for Write/Edit: check required document sections and scan for secrets.

Exit code 2 feeds the message back to the agent (the write has already happened).
"""
import json
import os
import re
import sys

REQUIRED = {
    "model-spec.md": ["Notation, timing and units", "Parameters", "Known limitations"],
    "model-brief.md": ["Purpose", "Non-purposes", "Risk level and validation depth"],
    "model-card.md": ["Intended use", "Out-of-scope use", "Limitations and failure modes", "Validation status"],
    "validation-report.md": ["Independence statement", "Findings", "Rating"],
    "estimation-report.md": ["Convergence diagnostics", "Identification"],
}
SECRETS = [r"sk-[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"-----BEGIN (RSA |EC )?PRIVATE KEY-----",
           r"ghp_[A-Za-z0-9]{30,}", r"(?i)(api[_-]?key|secret|password)\s*[:=]\s*['\"][^'\"]{12,}['\"]"]

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    sys.exit(0)

path = (data.get("tool_input") or {}).get("file_path") or data.get("file_path")  # Claude Code / Cursor
if not path or not os.path.isfile(path):
    sys.exit(0)
try:
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
except OSError:
    sys.exit(0)

problems = []
for pat in SECRETS:
    if re.search(pat, text):
        problems.append("possible secret or credential found; remove it and rotate if real")
        break

name = os.path.basename(path).lower()
norm = path.replace("\\", "/")
if name in REQUIRED and "/docs/templates/" not in norm:
    missing = [h for h in REQUIRED[name] if not re.search(r"^#+\s*" + re.escape(h), text, re.M | re.I)]
    if missing:
        problems.append(f"missing required section(s): {', '.join(missing)} (see docs/templates/{name})")

if problems:
    print(f"Check {os.path.basename(path)}: " + "; ".join(problems), file=sys.stderr)
    sys.exit(2)
sys.exit(0)
