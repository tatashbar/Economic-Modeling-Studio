#!/usr/bin/env python3
"""Validate the studio's integrity.

Checks: agent count and frontmatter, skill frontmatter, agent references in skills and
agents, links to next skills, rules/templates present, hooks parse, settings.json valid,
copies for other coding agents in sync with .claude/ (tools/sync_agents.py), Cursor hooks valid.

Usage: python tools/validate_studio.py [--expect-agents 119] [--expect-skills 85]
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []


def err(msg):
    errors.append(msg)


def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(f"{path}: missing frontmatter")
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect-agents", type=int, default=119)
    ap.add_argument("--expect-skills", type=int, default=85)
    args = ap.parse_args()

    agents = {}
    for p in sorted(glob.glob(os.path.join(ROOT, ".claude", "agents", "*.md"))):
        fm, text = frontmatter(p)
        slug = os.path.basename(p)[:-3]
        for key in ("name", "description", "tools", "model"):
            if not fm.get(key):
                err(f"agent {slug}: missing '{key}'")
        if fm.get("name") != slug:
            err(f"agent {slug}: name '{fm.get('name')}' does not match filename")
        agents[slug] = text
    if len(agents) != args.expect_agents:
        err(f"expected {args.expect_agents} agents, found {len(agents)}")

    for slug, text in agents.items():
        m = re.search(r"^- \*\*Works closely with:\*\* (.+)$", text, re.M)
        peers = re.findall(r"`([a-z0-9-]+)`", m.group(1)) if m else []
        if len(peers) < 2:
            err(f"agent {slug}: lists fewer than 2 peers under 'Works closely with'")
        if slug in peers:
            err(f"agent {slug}: lists itself as a peer")
        for ref in re.findall(r"`([a-z0-9-]+)`", text):
            if ref.endswith(("-specialist", "-lead", "-director", "-modeler", "-engineer", "-analyst", "-economist",
                             "-writer", "-designer", "-liaison", "-facilitator", "-auditor", "-architect")):
                if ref not in agents:
                    err(f"agent {slug}: references unknown agent '{ref}'")

    skills = {}
    for p in sorted(glob.glob(os.path.join(ROOT, ".claude", "skills", "*", "SKILL.md"))):
        fm, text = frontmatter(p)
        slug = os.path.basename(os.path.dirname(p))
        for key in ("name", "description", "allowed-tools"):
            if not fm.get(key):
                err(f"skill {slug}: missing '{key}'")
        if fm.get("name") != slug:
            err(f"skill {slug}: name mismatch")
        skills[slug] = text
    if len(skills) != args.expect_skills:
        err(f"expected {args.expect_skills} skills, found {len(skills)}")

    for slug, text in skills.items():
        for a in re.findall(r"^- `([a-z0-9-]+)` —", text, re.M):
            if a not in agents:
                err(f"skill {slug}: unknown agent '{a}'")
        m = re.search(r"\*\*Primary agent:\*\* `([a-z0-9-]+)`", text)
        if not m or m.group(1) not in agents:
            err(f"skill {slug}: missing or unknown primary agent")
        for n in re.findall(r"^- `/([a-z0-9-]+)`", text, re.M):
            if n not in skills:
                err(f"skill {slug}: next step '/{n}' does not exist")

    # files named by templates in docs
    for t in ("model-brief", "model-spec", "model-card", "validation-report"):
        if not os.path.exists(os.path.join(ROOT, "docs", "templates", f"{t}.md")):
            err(f"missing template {t}")

    for p in glob.glob(os.path.join(ROOT, ".claude", "hooks", "*.py")):
        try:
            compile(open(p, encoding="utf-8").read(), p, "exec")
        except SyntaxError as e:
            err(f"hook {p}: {e}")

    try:
        settings = json.load(open(os.path.join(ROOT, ".claude", "settings.json"), encoding="utf-8"))
        for evt, entries in settings.get("hooks", {}).items():
            for e in entries:
                for h in e["hooks"]:
                    m = re.search(r"([a-z-]+\.py)\s*$", h["command"])
                    if m and not os.path.exists(os.path.join(ROOT, ".claude", "hooks", m.group(1))):
                        err(f"settings: hook script {m.group(1)} missing ({evt})")
    except (OSError, ValueError) as e:
        err(f"settings.json: {e}")

    # lego catalog, shared ports and shipped examples
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    try:
        import lego
        ports = lego.load_ports()
        cat = lego.load_catalog()
        if not cat:
            err("lego: catalog is empty")
        for cid, b in cat.items():
            if b.get("kind") not in lego.KINDS:
                err(f"lego brick {cid}: unknown kind '{b.get('kind')}'")
            for p in lego.provs(b) + [q["port"] for q in lego.reqs(b)]:
                if p not in ports:
                    err(f"lego brick {cid}: port '{p}' is not defined in lego/ports.json")
            for idn in b.get("identities", []):
                for p in idn.get("ports", []):
                    if p not in ports:
                        err(f"lego brick {cid}: identity '{idn.get('name')}' uses undefined port '{p}'")
        for p, v in ports.items():
            if not v.get("unit"):
                err(f"lego port {p}: missing unit")
        for ex in glob.glob(os.path.join(ROOT, "lego", "examples", "*.lego.json")):
            rep = lego.check(lego.read_json(ex))
            for e in rep["errors"]:
                err(f"lego example {os.path.basename(ex)}: {e}")
    except Exception as e:  # pragma: no cover - reported as a failure of the check itself
        err(f"lego: {type(e).__name__}: {e}")

    # copies for other coding agents (AGENTS.md rules table, .agents/, .grok/, .cursor/rules/)
    try:
        import sync_agents
        exp = sync_agents.expected()
        for rel, text in exp.items():
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path) or sync_agents.read(path) != text:
                err(f"{rel} is out of date; run python tools/sync_agents.py")
        for rel in sync_agents.stale(exp):
            err(f"{rel} has no source in .claude/; run python tools/sync_agents.py")
        hooks = json.load(open(os.path.join(ROOT, ".cursor", "hooks.json"), encoding="utf-8"))
        for evt, defs in hooks.get("hooks", {}).items():
            for h in defs:
                m = re.search(r"([a-z-]+\.py)\s*$", h.get("command", ""))
                if not m or not os.path.exists(os.path.join(ROOT, ".claude", "hooks", m.group(1))):
                    err(f".cursor/hooks.json: {evt} points to a missing guard script")
    except Exception as e:  # pragma: no cover
        err(f"agent adapters: {type(e).__name__}: {e}")

    if errors:
        print(f"FAILED: {len(errors)} problem(s)")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"OK: {len(agents)} agents, {len(skills)} skills, hooks, settings, lego catalog and agent adapters valid")


if __name__ == "__main__":
    main()
