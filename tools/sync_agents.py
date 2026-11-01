#!/usr/bin/env python3
"""Generate the files other coding agents read from the single source in .claude/.

Source (edit these):        .claude/skills/*/SKILL.md, .claude/rules/*.md
Generated (do not edit):    .agents/skills/   Codex, Cursor, Gemini CLI / Antigravity, Copilot and other Agent Skills tools
                            .grok/skills/     Grok Build
                            .cursor/rules/    Cursor path-scoped rules (.mdc)
                            AGENTS.md         the rules table between the GENERATED markers

Skill bodies are made tool-neutral: the Claude Code placeholders ($ARGUMENTS, the Task tool) are replaced
and only the portable frontmatter (name, description) is kept.

Usage:  python tools/sync_agents.py            write the generated files
        python tools/sync_agents.py --check    exit 1 if anything is out of date (used by validate_studio.py)
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_TARGETS = [".agents/skills", ".grok/skills"]
BANNER = "<!-- Generated from .claude/{src} by tools/sync_agents.py. Edit the source, then run the script. -->"
RULES_BEGIN, RULES_END = "<!-- BEGIN GENERATED: rules -->", "<!-- END GENERATED: rules -->"

ARGS_OLD = "Arguments: `$ARGUMENTS`"
ARGS_NEW = "Arguments: whatever the user wrote after the command name."
TASK_OLD = ("Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. "
            "Subagents only write to the paths named in your instructions.")
TASK_NEW = ("Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as "
            "subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its "
            "instructions in turn. Subagents only write to the paths named in your instructions.")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def split_frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError("missing frontmatter")
    return m.group(1), text[m.end():]


def field(front, key):
    m = re.search(rf"^{key}:\s*(.*)$", front, re.M)
    return m.group(1).strip() if m else None


def portable_skill(name, text):
    front, body = split_frontmatter(text)
    if field(front, "name") != name:
        raise ValueError(f"skill folder '{name}' and frontmatter name '{field(front, 'name')}' differ")
    head = f"---\nname: {name}\ndescription: {field(front, 'description')}\n---\n"
    body = body.replace(ARGS_OLD, ARGS_NEW).replace(TASK_OLD, TASK_NEW)
    return head + BANNER.format(src=f"skills/{name}/SKILL.md") + "\n" + body


def rule_paths(front):
    return re.findall(r'^\s*-\s*"?([^"\n]+?)"?\s*$', front, re.M)


def cursor_rule(name, text):
    front, body = split_frontmatter(text)
    title = re.search(r"^# Rules: (.+)$", body, re.M)
    paths = rule_paths(front)
    head = [f"description: {title.group(1) if title else name} standards"]
    head += [f"globs: {','.join(paths)}", "alwaysApply: false"] if paths else ["alwaysApply: true"]
    return "---\n" + "\n".join(head) + "\n---\n" + BANNER.format(src=f"rules/{name}.md") + "\n" + body


def rules_table():
    rows = ["| When you work on | Follow |", "|---|---|"]
    for p in sorted(glob.glob(os.path.join(ROOT, ".claude", "rules", "*.md"))):
        front, _ = split_frontmatter(read(p))
        paths = ", ".join(f"`{x}`" for x in rule_paths(front)) or "any file"
        rows.append(f"| {paths} | `.claude/rules/{os.path.basename(p)}` |")
    return "\n".join(rows)


def expected():
    """Map of relative path -> content for every generated file."""
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, ".claude", "skills", "*", "SKILL.md"))):
        name = os.path.basename(os.path.dirname(p))
        text = portable_skill(name, read(p))
        for t in SKILL_TARGETS:
            out[f"{t}/{name}/SKILL.md"] = text
    for p in sorted(glob.glob(os.path.join(ROOT, ".claude", "rules", "*.md"))):
        name = os.path.splitext(os.path.basename(p))[0]
        out[f".cursor/rules/{name}.mdc"] = cursor_rule(name, read(p))
    agents = read(os.path.join(ROOT, "AGENTS.md"))
    i, j = agents.index(RULES_BEGIN) + len(RULES_BEGIN), agents.index(RULES_END)
    out["AGENTS.md"] = agents[:i] + "\n" + rules_table() + "\n" + agents[j:]
    return out


def stale(exp):
    """Generated files on disk that no longer have a source."""
    found = set()
    for t in SKILL_TARGETS:
        found |= {os.path.relpath(p, ROOT).replace("\\", "/") for p in glob.glob(os.path.join(ROOT, t, "*", "SKILL.md"))}
    found |= {os.path.relpath(p, ROOT).replace("\\", "/") for p in glob.glob(os.path.join(ROOT, ".cursor", "rules", "*.mdc"))}
    return sorted(found - set(exp))


def main():
    check = "--check" in sys.argv
    exp = expected()
    stale_list = stale(exp)
    differ = [rel for rel, text in exp.items()
              if not os.path.exists(os.path.join(ROOT, rel)) or read(os.path.join(ROOT, rel)) != text]
    if check:
        if differ or stale_list:
            for rel in differ:
                print(f"out of date: {rel}")
            for rel in stale_list:
                print(f"no source:   {rel}")
            print("run: python tools/sync_agents.py")
            sys.exit(1)
        print(f"OK: {len(exp)} generated files in sync")
        return
    for rel in differ:
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(exp[rel])
    for rel in stale_list:
        os.remove(os.path.join(ROOT, rel))
        d = os.path.dirname(os.path.join(ROOT, rel))
        if not os.listdir(d):
            os.rmdir(d)
    print(f"wrote {len(differ)} file(s), removed {len(stale_list)}; {len(exp)} generated files in sync")


if __name__ == "__main__":
    main()
