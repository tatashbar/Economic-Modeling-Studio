#!/usr/bin/env python3
"""Git pre-commit guard: works the same whichever coding agent (or person) makes the commit.

Blocks staging restricted or confidential data, raw data, credential files, and text that looks like a secret.
Enable once per clone:  git config core.hooksPath .githooks
Run by hand:            python tools/precommit_guard.py [paths...]   (default: the staged files)
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCKED_PATHS = [
    (r"(^|/)data/(restricted|confidential)/", "restricted or confidential data"),
    (r"(^|/)data/raw/", "raw data (versioned outside git)"),
    (r"(^|/)\.env(\.|$)|(^|/)credentials|\.pem$|\.key$|(^|/)id_rsa", "a credential file"),
]
ALLOWED = re.compile(r"(^|/)\.gitkeep$")
SECRETS = [r"sk-[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"-----BEGIN (RSA |EC )?PRIVATE KEY-----",
           r"ghp_[A-Za-z0-9]{30,}", r"(?i)(api[_-]?key|secret|password)\s*[:=]\s*['\"][^'\"]{12,}['\"]"]


def staged():
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p]


def problems(paths):
    found = []
    for p in paths:
        norm = p.replace("\\", "/")
        if ALLOWED.search(norm):
            continue
        hit = next((why for pat, why in BLOCKED_PATHS if re.search(pat, norm, re.I)), None)
        if hit:
            found.append(f"{p}: {hit}")
            continue
        full = os.path.join(ROOT, p)
        try:
            with open(full, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue  # binary or unreadable: path checks above still apply
        if any(re.search(s, text) for s in SECRETS):
            found.append(f"{p}: looks like it contains a secret")
    return found


def main():
    paths = sys.argv[1:] or staged()
    found = problems(paths)
    if found:
        print("Commit blocked by the studio's pre-commit guard:", file=sys.stderr)
        for f in found:
            print(f"  - {f}", file=sys.stderr)
        print("Unstage these files (git restore --staged <file>). See .claude/docs/confidentiality-and-ai-use.md.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
