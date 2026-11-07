#!/usr/bin/env python3
"""Read research notes and inventory data files for /research-plan. Standard library only.

Usage:  python tools/intake.py note <file.docx|.md|.txt|.pdf>
            numbered paragraphs ([P1], [P2], ...), headings marked with '#', table rows joined with ' | '.
            PDF needs its text layer and the optional pypdf package; otherwise read the PDF directly
            or save it as DOCX or text.
        python tools/intake.py data <file.xlsx|.xlsm|.csv> [--json]
            per sheet: size, header row, layout (wide panel with years in columns, long table, other),
            entities, indicators, year range, filled share, error cells, formulas, vintage hints.
        python tools/intake.py tidy <file.xlsx|.csv> --sheet <name> --out <file.csv>
            reshapes a wide panel (one row per country and indicator, one column per year) to a
            long CSV: entity, code, indicator, year, value.
        python tools/intake.py formulas <file.xlsx> --sheet <name> [--row N]
            the formulas behind a calculation sheet: for one row (default: the first row with formulas),
            each cell's column, block title, header and formula. Use it to compare the method actually
            coded with the method the note describes.

The tool reads only; it never changes the input files.
"""
import argparse
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
      "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
M = "{%s}" % NS["m"]
W = "{%s}" % NS["w"]
ERRORS = {"#N/A", "#VALUE!", "#REF!", "#DIV/0!", "#NUM!", "#NAME?", "#NULL!"}
ENTITY_COLS = ("country", "countryname", "name", "economy", "entity", "area")
CODE_COLS = ("country.id", "countrycode", "iso3", "iso", "code", "country code", "series_code")
INDICATOR_COLS = ("indicator", "indicator.id", "series", "variable", "concept", "series_code")
VINTAGE_COLS = ("dataset", "publication_date", "update_date", "vintage", "release")


# ---------------------------------------------------------------- notes
def note_paragraphs(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return _docx_paragraphs(path)
    if ext == ".pdf":
        try:
            import pypdf  # optional
        except ImportError:
            raise SystemExit("PDF: install pypdf for its text layer, or read the PDF directly, "
                             "or save it as DOCX or text and run this again.")
        text = "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(path).pages)
        return [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    return [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]


def _docx_paragraphs(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    out = []

    def text_of(el):
        return "".join(t.text or "" for t in el.iter(W + "t")).strip()

    for el in body:
        if el.tag == W + "p":
            t = text_of(el)
            if not t:
                continue
            style = el.find(f"{W}pPr/{W}pStyle")
            val = style.get(W + "val", "") if style is not None else ""
            m = re.search(r"(\d)$", val) if val.lower().startswith(("heading", "title")) else None
            out.append(("#" * (int(m.group(1)) if m else 1) + " " + t) if val.lower().startswith(("heading", "title")) else t)
        elif el.tag == W + "tbl":
            for tr in el.iter(W + "tr"):
                cells = [text_of(tc) for tc in tr.findall(W + "tc")]
                if any(cells):
                    out.append(" | ".join(cells))
    return out


# ---------------------------------------------------------------- spreadsheets
def _col_index(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def _shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    out = []
    with z.open("xl/sharedStrings.xml") as f:
        for _, el in ET.iterparse(f):
            if el.tag == M + "si":
                out.append("".join(t.text or "" for t in el.iter(M + "t")))
                el.clear()
    return out


def xlsx_sheets(path):
    """[(name, member path)] in workbook order."""
    with zipfile.ZipFile(path) as z:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = {r.get("Id"): r.get("Target") for r in rels.findall("pr:Relationship", NS)}
    out = []
    for s in wb.find(M + "sheets"):
        t = target[s.get("{%s}id" % NS["r"])].lstrip("/")
        out.append((s.get("name"), t if t.startswith("xl/") else "xl/" + t))
    return out


def xlsx_rows(path, member, max_rows=None):
    """Yield (row values, formula count, error count) per non-empty row; values are str, float or None."""
    with zipfile.ZipFile(path) as z:
        shared = _shared_strings(z)
        with z.open(member) as f:
            n = 0
            for _, el in ET.iterparse(f):
                if el.tag != M + "row":
                    continue
                vals, formulas, errs = {}, 0, 0
                for c in el.findall(M + "c"):
                    t, v = c.get("t"), c.find(M + "v")
                    if c.find(M + "f") is not None:
                        formulas += 1
                    if t == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter(M + "t"))
                    elif v is None or v.text is None:
                        continue
                    elif t == "s":
                        val = shared[int(v.text)]
                    elif t in ("str", "e"):
                        val = v.text
                    elif t == "b":
                        val = v.text == "1"
                    else:
                        try:
                            val = float(v.text)
                        except ValueError:
                            val = v.text
                    if t == "e" or (isinstance(val, str) and val.strip() in ERRORS):
                        errs += 1
                    vals[_col_index(c.get("r"))] = val
                el.clear()
                if vals:
                    width = max(vals) + 1
                    yield [vals.get(i) for i in range(width)], formulas, errs
                    n += 1
                    if max_rows and n >= max_rows:
                        return


def csv_rows(path, max_rows=None):
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if max_rows and i >= max_rows:
                return
            vals = [_num(x) if x != "" else None for x in row]
            if any(v is not None for v in vals):
                yield vals, 0, sum(1 for x in row if x.strip() in ERRORS)


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return x


def _year(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f == int(f) and 1900 <= f <= 2100 else None


def _find(header, names):
    low = [str(h).strip().lower() if h is not None else "" for h in header]
    for n in names:
        if n in low:
            return low.index(n)
    return None


def _first_block(body, header, cols):
    """Rows up to the first repeat of the header (sheets often stack calculation blocks below the data)."""
    keys = [c for c in cols if c is not None and header[c] is not None]
    stops = [i for i, r in enumerate(body) if keys and any(c < len(r) and r[c] == header[c] for c in keys)]
    return (body[:stops[0]] if stops else body), len(stops)


def inventory_rows(rows, max_scan=200000):
    head, data, formulas, errors, n = [], [], 0, 0, 0
    for vals, f, e in rows:
        n += 1
        formulas += f
        errors += e
        if n <= 30:
            head.append(vals)
        if len(data) < max_scan:
            data.append(vals)
    info = {"rows": n, "formulas": formulas, "error_cells": errors}
    if not head:
        info["layout"] = "empty"
        return info
    filled = [sum(v is not None for v in r) for r in head]
    hi = filled.index(max(filled))
    header = head[hi]
    info["header_row"] = hi + 1
    info["columns"] = max(len(r) for r in data)
    years = [(i, _year(h)) for i, h in enumerate(header) if _year(h)]
    ent, code, ind = _find(header, ENTITY_COLS), _find(header, CODE_COLS), _find(header, INDICATOR_COLS)
    body, repeats = _first_block(data[hi + 1:], header, (ent, ind))
    if repeats:
        info["blocks"] = f"{1 + repeats} (the header repeats; figures below describe the first block of {len(body)} rows)"
    if len(years) >= 5:
        info["layout"] = "wide panel (years in columns)"
        info["years"] = f"{min(y for _, y in years)}-{max(y for _, y in years)}"
        cells = [r[i] if i < len(r) else None for r in body for i, _ in years]
        num = sum(isinstance(c, float) for c in cells)
        info["filled_share"] = round(num / len(cells), 3) if cells else 0.0
        last = {}
        for r in body:
            for i, y in years:
                if i < len(r) and isinstance(r[i], float):
                    last[y] = last.get(y, 0) + 1
        if last:
            info["latest_year_with_data"] = max(last)
    elif _find(header, ("year", "period", "time")) is not None:
        info["layout"] = "long table (one row per observation)"
    else:
        info["layout"] = "table"
    for key, col in (("entities", ent), ("indicators", ind)):
        if col is not None:
            vals = [r[col] for r in body if col < len(r) and r[col] not in (None, "")]
            uniq = list(dict.fromkeys(str(v) for v in vals))
            info[key] = len(uniq)
            info[key + "_sample"] = [u[:60] for u in uniq[:5]]
    if code is not None:
        info["code_column"] = str(header[code])
    hints = []
    for c in (_find(header, (n,)) for n in VINTAGE_COLS):
        if c is not None:
            hints += list(dict.fromkeys(str(r[c]) for r in body[:2000] if c < len(r) and r[c] not in (None, "")))[:2]
    if hints:
        info["vintage_hints"] = hints[:4]
    if formulas:
        info["note"] = "calculation sheet: values are the cached results of formulas"
    return info


def inventory(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return {os.path.basename(path): inventory_rows(csv_rows(path))}
    return {name: inventory_rows(xlsx_rows(path, member)) for name, member in xlsx_sheets(path)}


def tidy(path, sheet, out):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        rows = csv_rows(path)
    else:
        members = dict(xlsx_sheets(path))
        if sheet not in members:
            raise SystemExit(f"sheet '{sheet}' not found; sheets: {', '.join(members)}")
        rows = xlsx_rows(path, members[sheet])
    rows = [r for r, _, _ in rows]
    head = rows[:30]
    filled = [sum(v is not None for v in r) for r in head]
    hi = filled.index(max(filled))
    header = rows[hi]
    years = [(i, _year(h)) for i, h in enumerate(header) if _year(h)]
    if len(years) < 5:
        raise SystemExit("not a wide panel: fewer than five year columns in the header row")
    ent, code, ind = _find(header, ENTITY_COLS), _find(header, CODE_COLS), _find(header, INDICATOR_COLS)
    body, _ = _first_block(rows[hi + 1:], header, (ent, ind))
    n = 0
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entity", "code", "indicator", "year", "value"])
        for r in body:
            get = lambda c: (r[c] if c is not None and c < len(r) else None)
            for i, y in years:
                v = get(i)
                if isinstance(v, float):
                    w.writerow([get(ent), get(code), get(ind), y, repr(v)])
                    n += 1
    return n


def _letters(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def _shift(formula, dcol, drow):
    """Move the relative references of a shared formula from its master cell to another cell."""
    def cell(m):
        cabs, col, rabs, row = m.groups()
        if not cabs:
            col = _letters(_col_index(col) + dcol)
        if not rabs:
            row = str(int(row) + drow)
        return f"{cabs}{col}{rabs}{row}"
    return re.sub(r'(?<![A-Za-z_."])(\$?)([A-Z]{1,3})(\$?)(\d+)(?![\d(])', cell, formula)


def formulas(path, sheet, row=None):
    """[(column, block title, header, formula)] for one row of a sheet. Block titles carry forward from the
    nearest row with text above the header; shared formulas are translated from their master cell."""
    members = dict(xlsx_sheets(path))
    if sheet not in members:
        raise SystemExit(f"sheet '{sheet}' not found; sheets: {', '.join(members)}")
    values, masters = {}, {}
    found = None
    with zipfile.ZipFile(path) as z:
        shared = _shared_strings(z)
        with z.open(members[sheet]) as f:
            for _, el in ET.iterparse(f):
                if el.tag != M + "row":
                    continue
                r = int(el.get("r"))
                cells = {}
                for c in el.findall(M + "c"):
                    col = _col_index(c.get("r"))
                    fx, v = c.find(M + "f"), c.find(M + "v")
                    if fx is not None:
                        si = fx.get("si")
                        if fx.text and si is not None:
                            masters[si] = (fx.text, col, r)
                        if fx.text:
                            cells[col] = ("f", "=" + fx.text)
                        elif si in masters:
                            text, mcol, mrow = masters[si]
                            cells[col] = ("f", "=" + _shift(text, col - mcol, r - mrow))
                        else:
                            cells[col] = ("f", f"(shared formula {si}, master not found)")
                    elif c.get("t") == "inlineStr":
                        cells[col] = ("v", "".join(x.text or "" for x in c.iter(M + "t")))
                    elif v is not None and v.text is not None:
                        cells[col] = ("v", shared[int(v.text)] if c.get("t") == "s" else v.text)
                el.clear()
                if r <= 30 or (row and r == row):
                    values[r] = cells
                if found is None and (r == row or (row is None and any(k == "f" for k, _ in cells.values()))):
                    found = r
                if found is not None and r >= found and r > 30:
                    break
    if found is None:
        return found, []
    head = [r for r in sorted(values) if r < found]
    hdr = max(head, key=lambda r: sum(k == "v" for k, _ in values[r].values()), default=None)
    trow = next((r for r in sorted(values, reverse=True) if hdr and r < hdr and values[r]), None)
    out, title = [], ""
    for col in sorted(values[found]):
        kind, text = values[found][col]
        if kind != "f":
            continue
        if trow:
            prev = [c for c in values[trow] if c <= col]
            title = values[trow][max(prev)][1] if prev else ""
        header = values[hdr].get(col, ("", ""))[1] if hdr else ""
        out.append((_letters(col), title, header, text))
    return found, out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("note")
    a.add_argument("file")
    b = sub.add_parser("data")
    b.add_argument("file")
    b.add_argument("--json", action="store_true")
    c = sub.add_parser("tidy")
    c.add_argument("file")
    c.add_argument("--sheet", default="")
    c.add_argument("--out", required=True)
    d = sub.add_parser("formulas")
    d.add_argument("file")
    d.add_argument("--sheet", required=True)
    d.add_argument("--row", type=int)
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.cmd == "note":
        for i, p in enumerate(note_paragraphs(args.file), 1):
            print(f"[P{i}] {p}")
    elif args.cmd == "data":
        inv = inventory(args.file)
        if args.json:
            print(json.dumps(inv, indent=2))
            return
        print(f"# {os.path.basename(args.file)}: {len(inv)} sheet(s)")
        for name, info in inv.items():
            print(f"\n## {name}")
            for k, v in info.items():
                print(f"- {k}: {', '.join(map(str, v)) if isinstance(v, list) else v}")
    elif args.cmd == "tidy":
        n = tidy(args.file, args.sheet, args.out)
        print(f"wrote {n} observations to {args.out}")
    else:
        r, cells = formulas(args.file, args.sheet, args.row)
        if r is None:
            print("no formulas found")
            return
        print(f"# {args.sheet}, row {r}")
        for col, title, header, text in cells:
            print(f"- {col} | {title} | {header} | {text}")


if __name__ == "__main__":
    main()
