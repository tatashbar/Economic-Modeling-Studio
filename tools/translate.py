#!/usr/bin/env python3
"""Code translation between the languages and software used for economic models. Standard library only.

Usage:  python tools/translate.py languages [--kind K] [--target-only] [--json]
            the languages and software the studio translates from and to (docs/translation/languages.json).
        python tools/translate.py idioms --from stata --to python [--task text]
            common operations side by side, with the defaults that make them differ (docs/translation/idioms.json).
        python tools/translate.py inventory <source-folder> [--out dir] [--json]
            every file with its language, size, the files it calls, data it reads and writes, packages,
            risky constructs, entry points and a translation order (called files first).
        python tools/translate.py plan <source-folder> --to <target> [--name N] [--out translations]
            creates the translation workspace translations/<name>-to-<target>/: inventory, a fingerprint of
            every source file, plan.md (file mapping in translation order, agents, pitfalls, idioms, decisions,
            equivalence plan), construct-log.md and folders for target code and both sets of outputs.
        python tools/translate.py compare <reference-dir> <translated-dir> [--rtol 1e-6] [--atol 1e-9]
                                          [--key col ...] [--pair ref=new ...] [--out report.md]
            compares the outputs of the source and the translated code: CSV and JSON cell by cell within
            tolerance, other files by content. Exit code 1 if anything differs.
        python tools/translate.py verify-source <workspace>
            checks that no source file has changed since the plan was made. Exit code 1 if one has.

The tool reads the source folder only; it never changes it.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG_FILE = os.path.join(ROOT, "docs", "translation", "languages.json")
IDIOM_FILE = os.path.join(ROOT, "docs", "translation", "idioms.json")
DOC_FILE = os.path.join(ROOT, "docs", "code-translation.md")
DOC_BEGIN, DOC_END = "<!-- BEGIN GENERATED: languages -->", "<!-- END GENERATED: languages -->"

DATA_EXT = {".csv", ".tsv", ".txt", ".dat", ".xlsx", ".xls", ".dta", ".sas7bdat", ".sav", ".rds", ".rda", ".rdata",
            ".mat", ".gdx", ".har", ".wf1", ".gdt", ".parquet", ".feather", ".json", ".xml", ".h5", ".npy", ".npz",
            ".pkl", ".db", ".sqlite", ".prn"}
SKIP_DIRS = {".git", "__pycache__", ".ipynb_checkpoints", ".venv", "node_modules", ".Rproj.user", "renv"}
TARGET_EXT = {"python": ".py", "r": ".R", "julia": ".jl", "matlab": ".m", "octave": ".m", "dynare": ".mod",
              "stata": ".do", "eviews": ".prg", "sas": ".sas", "gams": ".gms", "gempack": ".tab", "fortran": ".f90",
              "c": ".cpp", "stan": ".stan", "sql": ".sql", "gretl": ".inp", "iris": ".model"}
AGENT_BY_KIND = {"statistical": "statistical-code-translation-specialist",
                 "model": "model-code-translation-specialist", "optimization": "model-code-translation-specialist",
                 "numerical": "model-code-translation-specialist", "bayesian": "statistical-code-translation-specialist",
                 "legacy": "legacy-code-translation-specialist", "spreadsheet": "legacy-code-translation-specialist",
                 "database": "legacy-code-translation-specialist"}
EXECUTABLES = {"python": ["python", "python3"], "r": ["Rscript"], "stata": ["stata-mp", "stata-se", "stata", "StataMP-64", "StataSE-64"],
               "matlab": ["matlab"], "octave": ["octave", "octave-cli"], "dynare": ["matlab", "octave"], "iris": ["matlab"],
               "julia": ["julia"], "eviews": ["EViews", "EViews13", "EViews12"], "sas": ["sas"], "gams": ["gams"],
               "gempack": ["tablo"], "fortran": ["gfortran", "ifort", "ifx"], "c": ["gcc", "g++", "clang", "cl"],
               "cobol": ["cobc"], "gretl": ["gretlcli"], "stan": ["stanc"], "sql": ["sqlite3", "psql"], "ox": ["oxl"],
               "scilab": ["scilab-cli"], "mathematica": ["wolframscript"], "gauss": ["tgauss"]}
COMMENT = {"python": ["#"], "r": ["#"], "julia": ["#"], "stata": ["*", "//"], "matlab": ["%"], "octave": ["%", "#"],
           "dynare": ["//", "%"], "iris": ["%", "//"], "eviews": ["'"], "sas": ["*"], "gauss": ["//", "@"],
           "gams": ["*"], "gempack": ["!"], "fortran": ["!", "c ", "C ", "*"], "c": ["//"], "cobol": ["*"],
           "sql": ["--"], "stan": ["//"], "gretl": ["#"], "ox": ["//"], "excel": ["'"], "scilab": ["//"],
           "mathematica": ["(*"], "rats": ["*"], "tsp": ["?"], "spss": ["*"]}

# risky constructs: (language or '*', label, regex)
FLAGS = [
    ("*", "absolute path (not portable)", r"(?<![\w/])[A-Za-z]:[\\/][\w\\/ .-]+|(?<![\w.])/(?:Users|home|mnt|data)/[\w/ .-]+"),
    ("*", "random draws (seeds and streams differ across software)", r"\b(?:runiform|rnormal|rnorm|runif|rand[ni]?|randn|rng|set\s+seed|set\.seed|default_rng|random\.seed|streaminit|rndseed|Random\.seed!)\b"),
    ("*", "network access", r"https?://"),
    ("stata", "generate without a storage type (float, about 7 digits)", r"^\s*(?:gen|generate)\s+(?!double|float|byte|int|long|str)\w+\s*="),
    ("stata", "sort without the stable option", r"^\s*(?:sort|bysort|bys)\b(?![^\n]*stable)"),
    ("stata", "global macros", r"^\s*global\s+\w+"),
    ("stata", "user-written package install", r"\b(?:ssc|net)\s+install\b"),
    ("stata", "comparison that may include missing values", r"\bif\s+[^\n]*?\w\s*>=?\s*[\w.]+"),
    ("r", "setwd (machine-specific folder)", r"\bsetwd\s*\("),
    ("r", "attach (hidden scope)", r"\battach\s*\("),
    ("r", "global assignment <<-", r"<<-"),
    ("r", "vcovHC without an explicit type (defaults to HC3)", r"vcovHC\s*\((?![^)]*type)"),
    ("python", "np.std or np.var (ddof=0 by default)", r"\bnp\.(?:std|var)\s*\("),
    ("python", "legacy global NumPy random state", r"\bnp\.random\.(?:seed|rand|randn|normal|uniform)\s*\("),
    ("python", "chained pandas assignment", r"\]\[[^\]]+\]\s*="),
    ("matlab", "global variables", r"^\s*global\s+\w+"),
    ("matlab", "eval (code built at run time)", r"\beval[a-z]*\s*\("),
    ("matlab", "cd (machine-specific folder)", r"^\s*cd[\s(]"),
    ("octave", "global variables", r"^\s*global\s+\w+"),
    ("dynare", "macro processor (translate the expanded model)", r"^\s*@#"),
    ("dynare", "linear model", r"\bmodel\s*\(\s*linear"),
    ("dynare", "numerical steady state (steady with initval)", r"^\s*steady\b"),
    ("dynare", "estimation (priors, data and options to carry over)", r"^\s*estimation\s*\("),
    ("dynare", "stochastic simulation options", r"^\s*stoch_simul\b"),
    ("eviews", "sample state (smpl persists)", r"^\s*smpl\b"),
    ("eviews", "default coefficient vector c(n)", r"\bc\(\d+\)"),
    ("eviews", "model object solve", r"\.solve\b"),
    ("sas", "LAG inside a conditional (queue semantics)", r"\bif\b[^;]*\blag\d*\s*\("),
    ("sas", "RETAIN (state across rows)", r"\bretain\b"),
    ("sas", "macro language", r"%macro\b|%let\b"),
    ("sas", "MERGE (many-to-many is not a Cartesian product)", r"^\s*merge\b"),
    ("fortran", "no IMPLICIT NONE (implicit typing)", None),
    ("fortran", "COMMON or EQUIVALENCE (shared memory)", r"^\s*(?:common|equivalence)\b"),
    ("fortran", "GOTO or arithmetic IF", r"\bgo\s*to\b|^\s*if\s*\([^)]*\)\s*\d+\s*,\s*\d+\s*,\s*\d+"),
    ("fortran", "single-precision literal (add d0 or _dp)", r"(?<![\w.])\d+\.\d+(?![\w.])(?![dD_])"),
    ("cobol", "REDEFINES (overlaid layouts)", r"\bREDEFINES\b"),
    ("cobol", "packed decimal COMP-3", r"\bCOMP-3\b|\bPACKED-DECIMAL\b"),
    ("cobol", "GO TO or PERFORM THRU", r"\bGO\s+TO\b|\bPERFORM\s+\S+\s+THRU\b"),
    ("cobol", "variable-length table (OCCURS DEPENDING ON)", r"\bOCCURS\b[^.]*\bDEPENDING\b"),
    ("cobol", "arithmetic without ROUNDED (truncates)", r"\b(?:COMPUTE|DIVIDE|MULTIPLY)\b(?![^.]*\bROUNDED\b)"),
    ("gams", "dollar conditions", r"\$\s*\(|\w\$\w"),
    ("gams", "solve statement (check model and solver status)", r"^\s*solve\b"),
    ("gempack", "linearized percentage-change equations", r"^\s*equation\b"),
    ("excel", "VBA Round (half to even)", r"\bRound\s*\("),
    ("gauss", "global variables changed inside procedures", r"^\s*clearg\b|^\s*declare\b"),
]
CALL_PATTERNS = {
    "stata": r"^\s*(?:do|run|include)\s+\"?([^\"\s,]+)",
    "r": r"\bsource\s*\(\s*[\"']([^\"']+)",
    "julia": r"\binclude\s*\(\s*\"([^\"]+)",
    "dynare": r"@#include\s+\"([^\"]+)",
    "eviews": r"^\s*(?:run|include|exec)\s+\"?([^\"\s]+)",
    "sas": r"%include\s+[\"']([^\"']+)",
    "gams": r"\$(?:include|batinclude|libinclude)\s+\"?([^\"\s]+)",
    "fortran": r"^\s*include\s+['\"]([^'\"]+)",
    "c": r"#include\s+\"([^\"]+)",
    "gauss": r"#include\s+([\w./]+)|^\s*run\s+([\w./]+)",
    "ox": r"#include\s+[\"<]([^\">]+)",
    "gretl": r"^\s*(?:include|run)\s+([\w./]+)",
}
STEM_CALLS = {
    "matlab": r"(?<![\w.])({stems})\s*(?:\(|;|$)",
    "octave": r"(?<![\w.])({stems})\s*(?:\(|;|$)",
    "python": r"^\s*(?:from\s+\.?({stems})\s+import|import\s+({stems})\b)",
    "fortran": r"\bcall\s+({stems})\b|^\s*use\s+({stems})\b",
    "cobol": r"\bCOPY\s+({stems})\b|\bCALL\s+['\"]({stems})['\"]",
}
PACKAGE_PATTERNS = {
    "stata": r"\b(?:ssc|net)\s+install\s+(\w+)",
    "r": r"\b(?:library|require|requireNamespace)\s*\(\s*[\"']?(\w[\w.]*)|\b(\w[\w.]*)::",
    "python": r"^\s*(?:import|from)\s+(\w+)",
    "julia": r"^\s*(?:using|import)\s+(\w+)",
    "fortran": r"^\s*use\s+(\w+)",
}
WRITE_WORDS = re.compile(r"\b(?:save|saveold|export|outsheet|outfile|putexcel|esttab|estout|graph\s+export|write\w*|to_csv|to_excel|to_parquet|"
                         r"savefig|ggsave|saveRDS|wfsave|execute_unload|unload|fprintf|dlmwrite|csvwrite|xlswrite|writetable|"
                         r"sink|dump|open\s*\([^)]*['\"][wa]['\"])\b", re.I)


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read().replace("\r\n", "\n")
    except OSError:
        return ""


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def load_languages():
    with open(LANG_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_idioms():
    with open(IDIOM_FILE, encoding="utf-8") as f:
        return json.load(f)


def lang_index():
    return {l["id"]: l for l in load_languages()["languages"]}


def ext_map():
    m = {}
    for l in load_languages()["languages"]:
        for e in l["extensions"]:
            if l["id"] not in m.setdefault(e.lower(), []):
                m[e.lower()].append(l["id"])
    return m


def detect(path, text=None):
    """Language of one file: by extension, with content checks where extensions are shared. None for data and other files."""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls"):
        return None  # data, unless it has macros (.xlsm, .xlsb)
    if ext in (".dta", ".sas7bdat", ".sav", ".mat", ".gdx", ".har", ".wf1", ".gdt", ".dat"):
        return None
    cands = ext_map().get(ext, [])
    if not cands:
        return None
    if len(cands) == 1 and ext not in (".m", ".inc", ".src"):
        return cands[0]
    t = text if text is not None else read_text(path)[:20000]
    if ext == ".m":
        if re.search(r"\(\*|:=\s|\[\[|Module\[", t):
            return "mathematica"
        if re.search(r"^\s*(?:endif|endfor|endwhile|endfunction)\b|^\s*#(?!!)|printf\s*\(", t, re.M):
            return "octave"
        return "matlab"
    if ext == ".mod":
        if re.search(r"^\s*(?:var|varexo|parameters)\b[^;]*;", t, re.M) and re.search(r"^\s*model\s*(?:\(|;)", t, re.M):
            return "dynare"
        if re.search(r"^\s*(?:param|set|subject\s+to|minimize|maximize|s\.t\.)\b", t, re.M):
            return "ampl"
        return "dynare"
    if ext == ".inc":
        if re.search(r"^\s*(?:equations?|positive\s+variables?|parameters?|sets?)\b|\$\(|=e=", t, re.M | re.I):
            return "gams"
        return "dynare"
    if ext == ".prg":
        if re.search(r"^\s*(?:wfopen|wfcreate|smpl|series|equation|genr|pagecreate)\b", t, re.M | re.I):
            return "eviews"
        if re.search(r"^\s*(?:calendar|cal|allocate|linreg)\b", t, re.M | re.I):
            return "rats"
        if re.search(r"\bretp\b|^\s*proc\b|^\s*let\b", t, re.M):
            return "gauss"
        return "eviews"
    if ext == ".src":
        if re.search(r"\bretp\b|^\s*proc\b", t, re.M):
            return "gauss"
        if re.search(r"^\s*(?:calendar|allocate|linreg|procedure)\b", t, re.M | re.I):
            return "rats"
        return "troll" if re.search(r"^\s*(?:addeq|simstart|dosim)\b", t, re.M | re.I) else "gauss"
    if ext == ".inp":
        if re.search(r"^\s*(?:addeq|simstart|usemod|dosim)\b", t, re.M | re.I):
            return "troll"
        return "gretl"
    return cands[0]


def comment_or_blank(line, lang):
    s = line.strip()
    if not s:
        return True
    if lang == "fortran" and line[:1] in ("c", "C", "*", "!"):
        return True
    if lang == "cobol" and len(line) > 6 and line[6] in "*/":
        return True
    return any(s.startswith(p.strip()) for p in COMMENT.get(lang, []) if p.strip())


def walk(src):
    for d, dirs, files in os.walk(src):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            yield os.path.join(d, f)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory(src):
    src = os.path.abspath(src)
    if not os.path.isdir(src):
        raise SystemExit(f"not a folder: {src}")
    files, data, other = [], [], []
    for p in walk(src):
        rel = os.path.relpath(p, src).replace("\\", "/")
        ext = os.path.splitext(p)[1].lower()
        size = os.path.getsize(p)
        text = read_text(p) if size < 5_000_000 else ""
        lang = detect(p, text[:20000])
        if lang:
            lines = text.split("\n")
            code = sum(1 for ln in lines if not comment_or_blank(ln, lang))
            files.append({"path": rel, "language": lang, "lines": len(lines), "code_lines": code, "bytes": size,
                          "_text": text})
        elif ext in DATA_EXT or ext in (".xlsx", ".xls"):
            data.append({"path": rel, "bytes": size})
        else:
            other.append({"path": rel, "bytes": size})

    by_name = {}
    for f in files:
        by_name.setdefault(os.path.basename(f["path"]).lower(), []).append(f["path"])
        by_name.setdefault(os.path.splitext(os.path.basename(f["path"]))[0].lower(), []).append(f["path"])
    stems_by_lang = {}
    for f in files:
        stems_by_lang.setdefault(f["language"], []).append(re.escape(os.path.splitext(os.path.basename(f["path"]))[0]))

    for f in files:
        text, lang = f.pop("_text"), f["language"]
        calls = set()
        pat = CALL_PATTERNS.get(lang)
        if pat:
            for m in re.finditer(pat, text, re.M | re.I):
                target = next((g for g in m.groups() if g), "")
                base = os.path.basename(target.replace("\\", "/")).lower()
                for cand in (base, os.path.splitext(base)[0], base + ".do", base + ".prg"):
                    for hit in by_name.get(cand, []):
                        if hit != f["path"]:
                            calls.add(hit)
        stem_pat = STEM_CALLS.get(lang)
        if stem_pat and stems_by_lang.get(lang):
            rx = re.compile(stem_pat.format(stems="|".join(stems_by_lang[lang])), re.M | re.I)
            for m in rx.finditer(text):
                name = next((g for g in m.groups() if g), "").lower()
                for hit in by_name.get(name, []):
                    if hit != f["path"]:
                        calls.add(hit)
        if lang in ("matlab", "octave") and re.search(r"^\s*dynare\s", text, re.M):
            for m in re.finditer(r"^\s*dynare\s+([\w.]+)", text, re.M):
                n = m.group(1).lower()
                for hit in by_name.get(n, []) + by_name.get(n + ".mod", []):
                    calls.add(hit)
        f["calls"] = sorted(calls)

        reads, writes = set(), set()
        for line in text.split("\n"):
            if comment_or_blank(line, lang):
                continue
            for m in re.finditer(r"[\"']?([\w./\\:~-]+\.(?:csv|tsv|xlsx?|dta|sas7bdat|sav|rds|rda|rdata|mat|gdx|har|wf1|gdt|parquet|feather|json|txt|dat|prn|h5|npy|npz|pkl|png|pdf|svg|tex))\b",
                                 line, re.I):
                name = m.group(1).replace("\\", "/")
                (writes if WRITE_WORDS.search(line) else reads).add(name)
        f["reads"], f["writes"] = sorted(reads), sorted(writes)

        pk = set()
        pat = PACKAGE_PATTERNS.get(lang)
        if pat:
            for m in re.finditer(pat, text, re.M):
                name = next((g for g in m.groups() if g), None)
                if name:
                    pk.add(name)
        f["packages"] = sorted(pk)

        flags = {}
        for fl_lang, label, rx in FLAGS:
            if fl_lang not in ("*", lang):
                continue
            if rx is None:  # fortran implicit typing
                if lang == "fortran" and not re.search(r"implicit\s+none", text, re.I):
                    flags[label] = 1
                continue
            n = len(re.findall(rx, text, re.M | re.I if lang in ("fortran", "cobol", "sas", "gams") else re.M))
            if n:
                flags[label] = n
        f["flags"] = flags

    called = {c for f in files for c in f["calls"]}
    entry = [f["path"] for f in files if f["path"] not in called]
    order = translation_order(files)
    langs = {}
    for f in files:
        l = langs.setdefault(f["language"], {"files": 0, "lines": 0, "code_lines": 0})
        l["files"] += 1
        l["lines"] += f["lines"]
        l["code_lines"] += f["code_lines"]
    return {"source": src, "made": dt.datetime.now().isoformat(timespec="seconds"), "languages": langs,
            "files": files, "data_files": data, "other_files": other, "entry_points": entry, "order": order}


def translation_order(files):
    """Called files before the files that call them; cycles are kept together and reported in input order."""
    deps = {f["path"]: set(f["calls"]) for f in files}
    done, order, visiting = set(), [], set()

    def visit(n):
        if n in done or n in visiting:
            return
        visiting.add(n)
        for d in sorted(deps.get(n, ())):
            visit(d)
        visiting.discard(n)
        done.add(n)
        order.append(n)

    for f in files:
        visit(f["path"])
    return order


def inventory_md(inv):
    L = [f"# Code inventory", "", f"Source: `{inv['source']}`  ", f"Made: {inv['made']}", "", "## Languages", "",
         "| Language | Files | Lines | Code lines |", "|---|---|---|---|"]
    names = lang_index()
    for k, v in sorted(inv["languages"].items(), key=lambda kv: -kv[1]["code_lines"]):
        L.append(f"| {names.get(k, {}).get('name', k)} | {v['files']} | {v['lines']} | {v['code_lines']} |")
    L += ["", "## Files in translation order (called files first)", "",
          "| # | File | Language | Code lines | Calls | Reads | Writes | Packages |", "|---|---|---|---|---|---|---|---|"]
    byp = {f["path"]: f for f in inv["files"]}
    for i, p in enumerate(inv["order"], 1):
        f = byp[p]
        L.append(f"| {i} | `{p}` | {f['language']} | {f['code_lines']} | {', '.join(f['calls']) or '-'} | "
                 f"{', '.join(f['reads']) or '-'} | {', '.join(f['writes']) or '-'} | {', '.join(f['packages']) or '-'} |")
    L += ["", "## Entry points (not called by another file)", ""] + [f"- `{p}`" for p in inv["entry_points"]]
    L += ["", "## Constructs to check", "", "| File | Construct | Count |", "|---|---|---|"]
    n = 0
    for p in inv["order"]:
        for label, c in byp[p]["flags"].items():
            L.append(f"| `{p}` | {label} | {c} |")
            n += 1
    if not n:
        L.append("| - | none found by the automatic scan | - |")
    L += ["", "## Data files in the folder", ""] + ([f"- `{d['path']}` ({d['bytes']:,} bytes)" for d in inv["data_files"]] or ["- none"])
    L += ["", "## Other files", ""] + ([f"- `{d['path']}`" for d in inv["other_files"]] or ["- none"])
    L += ["", "The scan is automatic and approximate: dependencies built at run time (macros, eval, file names in variables) "
          "are not found. The source-code analyst confirms the list by reading the code.", ""]
    return "\n".join(L)


def approved_toolchains():
    try:
        t = read_text(os.path.join(ROOT, "studio-config.yaml"))
        m = re.search(r"approved:\s*\[([^\]]*)\]", t)
        return [x.strip().strip("\"'") for x in m.group(1).split(",")] if m else []
    except OSError:
        return []


def available(lang):
    return [e for e in EXECUTABLES.get(lang, []) if shutil.which(e)]


def target_name(path, target):
    stem, ext = os.path.splitext(path)
    d, base = os.path.split(stem)
    if target in ("python", "julia"):
        base = re.sub(r"\W+", "_", base).strip("_").lower() or "module"
        if base[0].isdigit():
            base = "m_" + base
    if os.path.splitext(path)[1].lower() == TARGET_EXT.get(target, "").lower():
        base += "_translated"
    return "/".join(x for x in (d.replace("\\", "/"), base + TARGET_EXT.get(target, ext)) if x)


def idiom_rows(src_lang, tgt_lang):
    I = load_idioms()
    if src_lang not in I["columns"] or tgt_lang not in I["columns"]:
        return []
    return [r for r in I["idioms"] if r.get(src_lang) and r.get(tgt_lang)]


def plan(src, target, name=None, out=None):
    langs = lang_index()
    if target not in langs or not langs[target]["target"]:
        ok = ", ".join(sorted(k for k, v in langs.items() if v["target"]))
        raise SystemExit(f"'{target}' is not a supported target. Targets: {ok}")
    inv = inventory(src)
    if not inv["files"]:
        raise SystemExit(f"no source code found in {src}")
    name = name or re.sub(r"[^\w-]+", "-", os.path.basename(os.path.abspath(src))).strip("-").lower() or "code"
    ws = os.path.join(out or os.path.join(ROOT, "translations"), f"{name}-to-{target}")
    if os.path.exists(os.path.join(ws, "plan.md")):
        raise SystemExit(f"workspace exists: {ws} (choose another --name or remove it)")
    for sub in ("target", "reference-outputs", "translated-outputs", "equivalence"):
        os.makedirs(os.path.join(ws, sub), exist_ok=True)

    manifest = {"source": inv["source"], "made": inv["made"],
                "files": {os.path.relpath(p, inv["source"]).replace("\\", "/"): sha256(p) for p in walk(inv["source"])}}
    with open(os.path.join(ws, "source-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    with open(os.path.join(ws, "inventory.json"), "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=1)
    with open(os.path.join(ws, "inventory.md"), "w", encoding="utf-8") as f:
        f.write(inventory_md(inv))

    tl = langs[target]
    approved = approved_toolchains()
    src_langs = sorted(inv["languages"], key=lambda k: -inv["languages"][k]["code_lines"])
    byp = {f["path"]: f for f in inv["files"]}
    L = [f"# Translation plan: {name} to {tl['name']}", "",
         f"Source: `{inv['source']}` (read-only; fingerprints in `source-manifest.json`)  ",
         f"Target: {tl['name']}  ", f"Made: {inv['made']}  ", "Status: DRAFT, waiting for approval", "",
         "## Summary", "",
         f"- {len(inv['files'])} source files, {sum(f['code_lines'] for f in inv['files']):,} code lines, "
         f"in {', '.join(langs.get(k, {}).get('name', k) for k in src_langs)}.",
         f"- Entry points: {', '.join('`' + p + '`' for p in inv['entry_points']) or 'none found'}.",
         f"- Data files in the folder: {len(inv['data_files'])}.", ""]
    L += ["## Checks before translating", ""]
    tc = tl.get("toolchain")
    if tc and tc in approved:
        L.append(f"- Target toolchain `{tc}` is approved in `studio-config.yaml`.")
    else:
        L.append(f"- **Target toolchain is not in the approved list** (`studio-config.yaml`: {', '.join(approved) or 'none'}). "
                 f"Confirm with the user and the organization's IT policy before writing target code.")
    for k in src_langs:
        ex = available(k)
        L.append(f"- Source software {langs.get(k, {}).get('name', k)}: "
                 + (f"found on this machine ({', '.join(ex)}); reference outputs can be produced here."
                    if ex else "not found on this machine. Reference outputs must come from the user (outputs saved by the "
                               "original code), or equivalence is `NOT ASSESSED — NO REFERENCE OUTPUTS`."))
    ex = available(target)
    L.append(f"- Target software: " + (f"found ({', '.join(ex)})." if ex else "not found on this machine; set it up with `/setup-environment` first."))
    L.append("- Confidentiality: classify the source code and any data next to it before reading them "
             "(`.claude/docs/confidentiality-and-ai-use.md`). Restricted code or data stay out of prompts and external services.")
    L.append("")
    L += ["## Decisions for the user (options; recommendation first)", "",
          "| Decision | Options | Recommendation |", "|---|---|---|",
          "| Fidelity | (a) faithful first: same results, same structure, bugs kept and logged; (b) faithful then idiomatic refactor; (c) idiomatic rewrite | (b): faithful translation proven equivalent, then a separate idiomatic pass re-tested against the same outputs |",
          "| Structure | (a) one target file per source file; (b) a package with modules by function | (a) for the first pass; it keeps the side-by-side mapping simple |",
          "| Reference outputs | (a) run the source here; (b) outputs supplied by the user; (c) outputs from a published paper | (a) where the software is available, else (b) |",
          "| Tolerances | exact for counts and identifiers; relative 1e-6 for estimates; 1e-4 for iterative solutions and optimizers; distribution tests for simulations | as listed, recorded in the equivalence report |",
          "| Random draws | (a) export source draws and read them in the target; (b) compare distributions | (a) where the source can be run |",
          "| Known bugs found | (a) keep and log; (b) fix during translation | (a), fixes as a separate approved change after equivalence |", ""]
    L += ["## File mapping in translation order", "",
          "Called files come before the files that call them. Data files are not translated; the target reads the same files.", "",
          "| # | Source file | Language | Code lines | Target file | Agent | Status |", "|---|---|---|---|---|---|---|"]
    for i, p in enumerate(inv["order"], 1):
        f = byp[p]
        agent = AGENT_BY_KIND.get(langs.get(f["language"], {}).get("kind"), "model-code-translation-specialist")
        L.append(f"| {i} | `{p}` | {f['language']} | {f['code_lines']} | `target/{target_name(p, target)}` | `{agent}` | to do |")
    L += ["", "## Constructs to check (automatic scan)", ""]
    flagged = [(p, l, c) for p in inv["order"] for l, c in byp[p]["flags"].items()]
    L += [f"- `{p}`: {l} ({c})" for p, l, c in flagged] or ["- none found by the scan; the analyst still reads every file."]
    L += ["", "## Pitfalls for this pair", ""]
    for k in src_langs:
        L.append(f"### Source: {langs.get(k, {}).get('name', k)}")
        L += [f"- {x}" for x in langs.get(k, {}).get("pitfalls", [])] + [""]
    L.append(f"### Target: {tl['name']}")
    L += [f"- {x}" for x in tl.get("pitfalls", [])] + ["", "### Every translation"]
    L += [f"- {x}" for x in load_languages()["general"]] + [""]
    rows = [(k, r) for k in src_langs for r in idiom_rows(k, target)]
    if rows:
        L += ["## Idioms for this pair", "", f"| Task | Source | Target | Note |", "|---|---|---|---|"]
        for k, r in rows:
            cell = lambda s: (s or "").replace("|", "\\|").replace("\n", "<br>")
            L.append(f"| {r['task']} | `{cell(r[k])}` | `{cell(r[target])}` | {cell(r.get('note'))} |")
        L.append("")
    outs = sorted({w for f in inv["files"] for w in f["writes"]})
    L += ["## Equivalence plan", "",
          "1. Produce reference outputs from the source code into `reference-outputs/` (or copy the outputs the user supplies), "
          "writing full precision, not display formats.",
          "2. Run the translated code from a clean start into `translated-outputs/`, with the same file names.",
          "3. Compare: `python tools/translate.py compare reference-outputs translated-outputs --out equivalence/report.md`.",
          "4. Explain every difference (cause, size, accepted or fixed) in `construct-log.md`.",
          "5. Check the source is unchanged: `python tools/translate.py verify-source <this folder>`.", "",
          "Outputs the source writes (automatic scan):", ""] + ([f"- `{o}`" for o in outs] or ["- none found; agree the outputs to compare with the user."])
    L += ["", "## Sign-off", "", "- [ ] Plan approved by the user", "- [ ] All files translated", "- [ ] Equivalence report: PASS or differences explained",
          "- [ ] Independent review by `translation-equivalence-auditor`", "- [ ] Translation report written", ""]
    with open(os.path.join(ws, "plan.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    with open(os.path.join(ws, "construct-log.md"), "w", encoding="utf-8") as f:
        f.write("# Construct log\n\nOne row for every construct that did not translate one-to-one: different defaults, missing "
                "functions, bugs kept from the source, approximations and every difference found by the equivalence test.\n\n"
                "| # | Source file:line | Construct | Target choice | Effect on results | Verified by |\n|---|---|---|---|---|---|\n")
    with open(os.path.join(ws, "target", "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {name} in {tl['name']}\n\nTranslated from `{inv['source']}`. Run from this folder:\n\n```\n{tl['run']}\n```\n\n"
                "Each file starts with a header naming its source file. See `../plan.md` and `../construct-log.md`.\n")
    return ws


# ---------- compare ----------

MISSING = {"", "na", "nan", ".", "null", "none", "n/a", "#n/a", "missing", "-nan", "inf_missing"}


def num(s):
    s = s.strip()
    if s.lower() in MISSING:
        return "missing"
    for v in (s, s.replace("D", "E").replace("d", "e")):  # Fortran writes 1.5D+00
        try:
            return float(v)
        except ValueError:
            pass
    return None


def close(a, b, rtol, atol):
    if math.isnan(a) and math.isnan(b):
        return True
    if math.isinf(a) or math.isinf(b):
        return a == b
    return abs(a - b) <= atol + rtol * abs(a)


def read_csv(path):
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        rows = list(csv.reader(f, dialect))
    rows = [r for r in rows if any(c.strip() for c in r)]
    return (rows[0], rows[1:]) if rows else ([], [])


def structural(res, msg):
    res["issues"].append(msg)
    res["structural"] += 1


def compare_csv(ref, new, rtol, atol, keys):
    h1, r1 = read_csv(ref)
    h2, r2 = read_csv(new)
    norm = lambda h: [c.strip().lower() for c in h]
    n1, n2 = norm(h1), norm(h2)
    res = {"rows": (len(r1), len(r2)), "issues": [], "structural": 0, "max_abs": 0.0, "max_rel": 0.0, "worst": None, "cells": 0, "bad": 0}
    only1, only2 = [c for c in n1 if c not in n2], [c for c in n2 if c not in n1]
    if only1:
        structural(res, f"columns only in the reference: {', '.join(only1)}")
    if only2:
        structural(res, f"columns only in the translation: {', '.join(only2)}")
    common = [c for c in n1 if c in n2]
    i1, i2 = {c: n1.index(c) for c in common}, {c: n2.index(c) for c in common}
    keys = [k.lower() for k in keys or []]
    if keys and all(k in common for k in keys):
        kf = lambda r, idx: tuple(r[idx[k]].strip() if idx[k] < len(r) else "" for k in keys)
        m2 = {kf(r, i2): r for r in r2}
        pairs = [(r, m2.get(kf(r, i1))) for r in r1]
        miss = sum(1 for _, b in pairs if b is None)
        extra = len(r2) - (len(r1) - miss)
        if miss:
            structural(res, f"{miss} reference rows have no match in the translation by {', '.join(keys)}")
        if extra > 0:
            structural(res, f"{extra} translation rows have no match in the reference")
        pairs = [(a, b) for a, b in pairs if b is not None]
    else:
        if keys:
            res["issues"].append(f"key columns not found in both files: {', '.join(keys)}; compared by row order")
        if len(r1) != len(r2):
            structural(res, f"row counts differ: {len(r1)} against {len(r2)}")
        pairs = list(zip(r1, r2))
    for rn, (a, b) in enumerate(pairs, 1):
        for c in common:
            va = a[i1[c]] if i1[c] < len(a) else ""
            vb = b[i2[c]] if i2[c] < len(b) else ""
            res["cells"] += 1
            xa, xb = num(va), num(vb)
            if xa == "missing" or xb == "missing":
                ok = xa == xb
                if not ok and res["bad"] < 20:
                    res["issues"].append(f"row {rn}, {c}: missing in one file only ({va!r} against {vb!r})")
            elif isinstance(xa, float) and isinstance(xb, float):
                d = abs(xa - xb)
                rel = d / abs(xa) if xa else (0.0 if d == 0 else math.inf)
                if d > res["max_abs"]:
                    res["max_abs"], res["worst"] = d, f"row {rn}, {c}: {va} against {vb}"
                res["max_rel"] = max(res["max_rel"], rel if not math.isinf(rel) else res["max_rel"])
                ok = close(xa, xb, rtol, atol)
                if not ok and res["bad"] < 20:
                    res["issues"].append(f"row {rn}, {c}: {va} against {vb} (difference {d:.3g})")
            else:
                ok = va.strip() == vb.strip()
                if not ok and res["bad"] < 20:
                    res["issues"].append(f"row {rn}, {c}: {va!r} against {vb!r}")
            if not ok:
                res["bad"] += 1
    return res


def flatten(x, prefix=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flatten(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from flatten(v, f"{prefix}[{i}]")
    else:
        yield prefix, x


def compare_json(ref, new, rtol, atol):
    a, b = (dict(flatten(load_json(p))) for p in (ref, new))
    res = {"rows": (len(a), len(b)), "issues": [], "max_abs": 0.0, "max_rel": 0.0, "worst": None, "cells": 0, "bad": 0}
    for k in sorted(set(a) | set(b)):
        res["cells"] += 1
        if k not in a or k not in b:
            res["bad"] += 1
            res["issues"].append(f"{k}: only in the {'reference' if k in a else 'translation'}")
            continue
        x, y = a[k], b[k]
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
            d = abs(x - y)
            if d > res["max_abs"]:
                res["max_abs"], res["worst"] = d, f"{k}: {x} against {y}"
            if x:
                res["max_rel"] = max(res["max_rel"], d / abs(x))
            if not close(float(x), float(y), rtol, atol):
                res["bad"] += 1
                res["issues"].append(f"{k}: {x} against {y}")
        elif x != y:
            res["bad"] += 1
            res["issues"].append(f"{k}: {x!r} against {y!r}")
    return res


def compare(ref_dir, new_dir, rtol=1e-6, atol=1e-9, keys=None, pairs=None, text=False):
    found = []
    if pairs:
        for p in pairs:
            a, b = p.split("=", 1)
            found.append((a, os.path.join(ref_dir, a), os.path.join(new_dir, b)))
    else:
        for p in walk(ref_dir):
            rel = os.path.relpath(p, ref_dir).replace("\\", "/")
            found.append((rel, p, os.path.join(new_dir, rel)))
        extra = sorted(os.path.relpath(p, new_dir).replace("\\", "/") for p in walk(new_dir)
                       if not os.path.exists(os.path.join(ref_dir, os.path.relpath(p, new_dir))))
    results = []
    for rel, a, b in found:
        ext = os.path.splitext(rel)[1].lower()
        if not os.path.exists(b):
            results.append((rel, "MISSING", {"issues": ["no file with this name in the translated outputs"]}))
            continue
        if ext in (".csv", ".tsv"):
            r = compare_csv(a, b, rtol, atol, keys)
        elif ext == ".json":
            try:
                r = compare_json(a, b, rtol, atol)
            except ValueError as e:
                r = {"issues": [f"cannot parse JSON: {e}"], "bad": 1}
        elif ext in (".txt", ".md", ".log") and not text:
            results.append((rel, "SKIPPED", {"issues": ["text file; pass --text to compare it"]}))
            continue
        else:
            same = sha256(a) == sha256(b)
            r = {"issues": [] if same else ["content differs"], "bad": 0 if same else 1}
        status = "FAIL" if r.get("bad") or r.get("structural") else "PASS"
        results.append((rel, status, r))
    return results, ([] if pairs else extra)


def compare_md(results, extra, ref_dir, new_dir, rtol, atol):
    ok = all(s in ("PASS", "SKIPPED") for _, s, _ in results) and results
    L = ["# Equivalence report", "", f"Reference outputs: `{ref_dir}`  ", f"Translated outputs: `{new_dir}`  ",
         f"Tolerance: |reference - translation| <= {atol:g} + {rtol:g} x |reference|  ",
         f"Made: {dt.datetime.now().isoformat(timespec='seconds')}", "",
         f"**Verdict: {'PASS' if ok else 'FAIL'}** ({sum(1 for _, s, _ in results if s == 'PASS')} of {len(results)} files pass)", "",
         "| File | Status | Rows (ref, new) | Cells compared | Cells outside tolerance | Max abs. difference | Max rel. difference | Largest difference |",
         "|---|---|---|---|---|---|---|---|"]
    for rel, s, r in results:
        rows = r.get("rows")
        L.append(f"| `{rel}` | {s} | {rows if rows else '-'} | {r.get('cells', '-')} | {r.get('bad', '-')} | "
                 f"{r['max_abs']:.3g} | {r['max_rel']:.3g} | {r.get('worst') or '-'} |" if "max_abs" in r else
                 f"| `{rel}` | {s} | - | - | {r.get('bad', '-')} | - | - | - |")
    for rel, s, r in results:
        if r.get("issues") and s != "SKIPPED":
            L += ["", f"## {rel}", ""] + [f"- {i}" for i in r["issues"][:25]]
    if extra:
        L += ["", "## Files only in the translated outputs", ""] + [f"- `{e}`" for e in extra]
    L += ["", "Every difference is explained in `construct-log.md` (cause, size, accepted or fixed) before sign-off.", ""]
    return "\n".join(L), bool(ok)


def verify_source(ws):
    man = load_json(os.path.join(ws, "source-manifest.json"))
    src = man["source"]
    now = {os.path.relpath(p, src).replace("\\", "/"): sha256(p) for p in walk(src)} if os.path.isdir(src) else {}
    changed = sorted(k for k in man["files"] if k in now and now[k] != man["files"][k])
    removed = sorted(k for k in man["files"] if k not in now)
    added = sorted(k for k in now if k not in man["files"])
    return changed, removed, added


# ---------- languages table ----------

def languages_md():
    langs = load_languages()["languages"]
    approved = approved_toolchains()
    L = ["| Language or software | Kind | Files | From | To | Studio toolchain |", "|---|---|---|---|---|---|"]
    for l in langs:
        tc = l.get("toolchain")
        L.append(f"| {l['name']} | {l['kind']} | {' '.join('`' + e + '`' for e in l['extensions'])} | "
                 f"{'yes' if l['source'] else '-'} | {'yes' if l['target'] else '-'} | "
                 f"{('`' + tc + '`' + ('' if tc in approved else ' (not approved)')) if tc else '-'} |")
    return "\n".join(L)


def write_doc():
    t = read_text(DOC_FILE)
    new = re.sub(re.escape(DOC_BEGIN) + r".*?" + re.escape(DOC_END), DOC_BEGIN + "\n" + languages_md() + "\n" + DOC_END, t, flags=re.S)
    if new != t:
        with open(DOC_FILE, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
    return new != t


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("languages")
    s.add_argument("--kind")
    s.add_argument("--target-only", action="store_true")
    s.add_argument("--json", action="store_true")
    s.add_argument("--write-doc", action="store_true", help="refresh the table in docs/code-translation.md")
    s = sub.add_parser("idioms")
    s.add_argument("--from", dest="src", required=True)
    s.add_argument("--to", dest="tgt", required=True)
    s.add_argument("--task")
    s = sub.add_parser("inventory")
    s.add_argument("source")
    s.add_argument("--out")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("plan")
    s.add_argument("source")
    s.add_argument("--to", dest="target", required=True)
    s.add_argument("--name")
    s.add_argument("--out")
    s = sub.add_parser("compare")
    s.add_argument("reference")
    s.add_argument("translated")
    s.add_argument("--rtol", type=float, default=1e-6)
    s.add_argument("--atol", type=float, default=1e-9)
    s.add_argument("--key", nargs="*")
    s.add_argument("--pair", nargs="*")
    s.add_argument("--text", action="store_true")
    s.add_argument("--out")
    s = sub.add_parser("verify-source")
    s.add_argument("workspace")
    a = ap.parse_args(argv)

    if a.cmd == "languages":
        if a.write_doc:
            print("updated" if write_doc() else "up to date", DOC_FILE)
            return 0
        langs = [l for l in load_languages()["languages"] if (not a.kind or l["kind"] == a.kind) and (l["target"] or not a.target_only)]
        if a.json:
            print(json.dumps(langs, indent=1))
        else:
            for l in langs:
                print(f"{l['id']:<12} {l['kind']:<12} from {'yes' if l['source'] else 'no ':<3}  to {'yes' if l['target'] else 'no ':<3}  {l['name']}")
        return 0
    if a.cmd == "idioms":
        cols = load_idioms()["columns"]
        for x in (a.src, a.tgt):
            if x not in cols:
                print(f"no idiom column for '{x}'. Columns: {', '.join(cols)}. Use the language pitfalls instead "
                      f"(python tools/translate.py languages --json).")
                return 1
        for r in idiom_rows(a.src, a.tgt):
            if a.task and a.task.lower() not in r["task"].lower():
                continue
            print(f"## {r['task']}\n  {a.src}: {r[a.src]}\n  {a.tgt}: {r[a.tgt]}" + (f"\n  note: {r['note']}" if r.get("note") else "") + "\n")
        return 0
    if a.cmd == "inventory":
        inv = inventory(a.source)
        if a.out:
            os.makedirs(a.out, exist_ok=True)
            write_text(os.path.join(a.out, "inventory.json"), json.dumps(inv, indent=1))
            write_text(os.path.join(a.out, "inventory.md"), inventory_md(inv))
            print(os.path.join(a.out, "inventory.md"))
        print(json.dumps(inv, indent=1) if a.json else inventory_md(inv))
        return 0
    if a.cmd == "plan":
        ws = plan(a.source, a.target, a.name, a.out)
        print(f"workspace: {ws}\nnext: review {os.path.join(ws, 'plan.md')} with the user")
        return 0
    if a.cmd == "compare":
        results, extra = compare(a.reference, a.translated, a.rtol, a.atol, a.key, a.pair, a.text)
        md, ok = compare_md(results, extra, a.reference, a.translated, a.rtol, a.atol)
        if a.out:
            os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
            write_text(a.out, md)
        print(md)
        return 0 if ok else 1
    if a.cmd == "verify-source":
        changed, removed, added = verify_source(a.workspace)
        for label, xs in (("changed", changed), ("removed", removed), ("added", added)):
            for x in xs:
                print(f"{label}: {x}")
        bad = changed or removed
        print("FAIL: the source changed since the plan was made" if bad else "OK: source unchanged" + (" (new files added)" if added else ""))
        return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
