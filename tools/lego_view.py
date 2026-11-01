"""Isometric 3D picture of a lego set (self-contained HTML + inline SVG, no scripts, no external files).

Geometry: x runs to the lower right, y to the lower left, z up. Bricks are 6 x 3 studs and 1.2 studs high
(real lego proportions). The core model is the baseplate; component bricks sit on it; bricks on higher layers
stand on the bricks whose outputs they read, so towers can be several levels high. Dashed yellow sockets on a brick are open studs
(inputs running on a stub); dashed ghost bricks are catalog bricks that would fill them; a parts-bin brick that would fill one says so on the shelf.
"""
import heapq
import html as htmllib

U = 28.0                                  # pixels per stud pitch
CX, CY = U * 0.8660254, U * 0.5           # isometric axes
BH, PH, SH, SR = 1.2, 0.7, 0.2, 0.3       # brick height, plate thickness, stud height, stud radius (in studs)
BW, BD, GAP = 6, 3, 2                     # brick footprint and gap between bricks on the plate
MAX_GHOSTS = 6

PALETTE = {"baseplate": "#3f9b46", "environment": "#8d6e63", "policy": "#1e88e5", "fiscal": "#f6b21b",
           "external": "#e53935", "financial": "#8e24aa", "sector": "#fb8c00", "climate": "#00897b",
           "household": "#d81b60", "satellite": "#607d8b", "output": "#455a64"}
# what a brick is made of; shown on its studs and in the "Inside the bricks" panel (always with a symbol, never by colour alone)
ELEMENT_STYLE = {"variables": ("#f2b705", "x", "variables"), "equations": ("#2f6fd6", "=", "equations"),
                 "parameters": ("#d64541", "θ", "parameters"), "shocks": ("#ef7d22", "ε", "shocks"),
                 "data": ("#2e9d57", "D", "data series"), "constraints": ("#8246c4", "≤", "constraints")}


def _element_studs(el, n):
    """Share n studs among the elements in proportion to their counts (largest remainder, at least one each)."""
    w = [(k, el[k]["total"]) for k in ELEMENT_STYLE if k in el and el[k]["total"] > 0]
    tot = sum(v for _, v in w)
    if not w or n <= 0:
        return []
    if len(w) >= n:
        w = sorted(w, key=lambda t: -t[1])[:n]
        tot = sum(v for _, v in w)
    base = {k: max(1, int(n * v / tot)) for k, v in w}
    while sum(base.values()) > n:
        k = max(base, key=lambda k: (base[k], -dict(w)[k]))
        base[k] -= 1
    rem = sorted(w, key=lambda t: -(n * t[1] / tot - int(n * t[1] / tot)))
    i = 0
    while sum(base.values()) < n:
        base[rem[i % len(rem)][0]] += 1
        i += 1
    return [ELEMENT_STYLE[k][0] for k, _ in w for _ in range(base[k])]


# ------------------------------------------------------------------ colour and geometry helpers
def _rgb(c):
    c = c.lstrip("#")
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def shade(c, f):
    """f > 0 lightens toward white, f < 0 darkens toward black."""
    t = 255 if f > 0 else 0
    f = abs(f)
    return "#%02x%02x%02x" % tuple(round(v + (t - v) * f) for v in _rgb(c))


def _ink(c):
    r, g, b = [v / 255 for v in _rgb(c)]
    return "#1d1d1d" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.6 else "#ffffff"


def P(x, y, z):
    return ((x - y) * CX, (x + y) * CY - z * U)


def _pts(*ps):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in ps)


def _faces(x, y, z, w, d, h):
    top = _pts(P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h))
    left = _pts(P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h))
    right = _pts(P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h))
    return top, left, right


class _It:
    __slots__ = ("kind", "x", "y", "z", "w", "d", "h", "data")

    def __init__(self, kind, x, y, z, w, d, h, data=None):
        self.kind, self.x, self.y, self.z, self.w, self.d, self.h, self.data = kind, x, y, z, w, d, h, data

    @property
    def x1(self):
        return self.x + self.w

    @property
    def y1(self):
        return self.y + self.d

    @property
    def z1(self):
        return self.z + self.h

    def corners(self):
        zt = self.z + self.h + (SH if self.kind in ("brick", "ghost", "stud") else 0)
        return [P(a, b, c) for a in (self.x, self.x1) for b in (self.y, self.y1) for c in (self.z, zt)]


def _depth_sort(items):
    """Painter's order for non-overlapping axis-aligned boxes seen from the +x, +y, +z corner."""
    n, eps = len(items), 1e-6

    def after(p, q):
        return p.x >= q.x1 - eps or p.y >= q.y1 - eps or p.z >= q.z1 - eps

    follow = [[] for _ in range(n)]
    indeg = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and after(items[i], items[j]) and not after(items[j], items[i]):
                follow[j].append(i)
                indeg[i] += 1
    key = lambda i: (items[i].x + items[i].y + items[i].z, items[i].x, items[i].z)
    heap = [(key(i), i) for i in range(n) if indeg[i] == 0]
    heapq.heapify(heap)
    out, seen = [], set()
    while heap:
        _, i = heapq.heappop(heap)
        out.append(items[i])
        seen.add(i)
        for k in follow[i]:
            indeg[k] -= 1
            if indeg[k] == 0:
                heapq.heappush(heap, (key(k), k))
    out += [items[i] for i in sorted(set(range(n)) - seen, key=key)]
    return out


# ------------------------------------------------------------------ svg pieces
def _stud_def(sid, color):
    rx, ry, sh = SR * U * 1.2247, SR * U * 0.7071, SH * U
    return (f'<g id="{sid}"><path d="M{-rx:.1f},0 V{-sh:.1f} H{rx:.1f} V0 A{rx:.1f},{ry:.1f} 0 0 1 {-rx:.1f},0 Z" '
            f'fill="{shade(color, -0.14)}"/>'
            f'<ellipse cy="{-sh:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{shade(color, 0.2)}" stroke="{shade(color, -0.32)}" stroke-width=".6"/>'
            f'<ellipse cx="{-rx * 0.22:.1f}" cy="{-sh - ry * 0.25:.1f}" rx="{rx * 0.45:.1f}" ry="{ry * 0.38:.1f}" fill="#fff" opacity=".3"/></g>')


def _socket(cx, cy):
    rx, ry = SR * U * 1.2247, SR * U * 0.7071
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#000" fill-opacity=".38" '
            f'stroke="#ffd54f" stroke-width="1.5" stroke-dasharray="3 2"/>')


def _badge(val, cx, cy):
    """Round tile on a face: check = validated, ring = unvalidated, ! = stale."""
    if val == "validated":
        return (f'<circle cx="{cx}" cy="{cy}" r="7.5" fill="#2e9d4f" stroke="#fff" stroke-width="1"/>'
                f'<text x="{cx}" y="{cy + 3.6}" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">✓</text>')
    if val == "stale":
        return (f'<circle cx="{cx}" cy="{cy}" r="7.5" fill="#ffb300" stroke="#fff" stroke-width="1"/>'
                f'<text x="{cx}" y="{cy + 3.6}" font-size="10" font-weight="800" fill="#3b2a00" text-anchor="middle">!</text>')
    return f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="#fff" stroke-opacity=".85" stroke-width="1.6"/>'


def _fit(text, avail, fs_max, fs_min=6.5, k=0.58):
    fs = min(fs_max, avail / (k * max(len(text), 1)))
    if fs >= fs_min:
        return text, fs
    keep = max(4, int(avail / (k * fs_min)) - 1)
    return text[:keep] + "…", fs_min


def _ref(sid, x, y):
    return f'<use href="#{sid}" x="{x:.1f}" y="{y:.1f}"/>'


def _brick_svg(it, stud_id, e):
    d = it.data
    x, y, z, w, dd, h = it.x, it.y, it.z, it.w, it.d, it.h
    c, ghost = d["color"], it.kind == "ghost"
    top, left, right = _faces(x, y, z, w, dd, h)
    lc, rc, tc = c, shade(c, -0.26), shade(c, 0.2)
    ink_l, ink_r = _ink(lc), _ink(rc)
    if ghost:
        ink_l = ink_r = shade(c, -0.45)
        st = f'stroke="{shade(c, -0.1)}" stroke-width="1.8" stroke-dasharray="5 3" stroke-linejoin="round"'
        faces = (f'<polygon class="lf" points="{left}" fill="#ffffff" fill-opacity=".72" {st}/>'
                 f'<polygon class="rf" points="{right}" fill="#ffffff" fill-opacity=".55" {st}/>'
                 f'<polygon class="tp" points="{top}" fill="#ffffff" fill-opacity=".6" {st}/>')
    else:
        ec = shade(c, -0.38)
        st = f'stroke="{ec}" stroke-width=".8" stroke-linejoin="round"'
        faces = (f'<polygon class="lf" points="{left}" fill="{lc}" {st}/>'
                 f'<polygon class="rf" points="{right}" fill="{rc}" {st}/>'
                 f'<polygon class="tp" points="{top}" fill="{tc}" {st}/>'
                 f'<polyline points="{_pts(P(x, y + dd, z + h), P(x + w, y + dd, z + h), P(x + w, y + dd, z))}" '
                 f'fill="none" stroke="#fff" stroke-opacity=".4" stroke-width="1.1" stroke-linejoin="round"/>')
    out = [faces]
    if ghost:
        ox, oy = P(x, y, z + h)
        k = shade(c, -0.1)
        out.append(f'<g transform="matrix(0.866 0.5 -0.866 0.5 {ox:.1f} {oy:.1f}) translate({w * U / 2:.1f} {dd * U / 2:.1f}) rotate(45)" fill="{k}">'
                   f'<rect x="-11" y="-2.6" width="22" height="5.2" rx="1.2"/><rect x="-2.6" y="-11" width="5.2" height="22" rx="1.2"/></g>')
    else:
        cells = [(i, j) for j in range(dd) for i in range(w)]
        sock = set(sorted(cells, key=lambda t: (-t[1], t[0]))[:d["sockets"]])
        studs = [t for t in cells if t not in sock]  # back row first, so each element forms a band
        ecol = dict(zip(sorted(studs, key=lambda t: (t[1], t[0]) if w >= dd else (t[0], t[1])),
                        _element_studs(d.get("elements") or {}, len(studs))))
        kd, el = [], []
        for i, j in sorted(cells, key=lambda t: (t[0] + t[1], t[0])):
            sx, sy = P(x + i + 0.5, y + j + 0.5, z + h)
            if (i, j) in sock:
                kd.append(_socket(sx, sy))
                el.append(_socket(sx, sy))
            else:
                kd.append(_ref(stud_id[c], sx, sy))
                el.append(_ref(stud_id[ecol.get((i, j), c)], sx, sy))
        if ecol:  # two sets of studs: by element (default) or by component; the legend switch picks one
            out.append(f'<g class="se">{"".join(el)}</g><g class="sk">{"".join(kd)}</g>')
        else:
            out.append("".join(kd))
    # name on the long face, kind on the short face: the lower-left face for a brick along x, the lower-right face
    # for a brick turned along y
    left = (f'matrix(0.866 0.5 0 1 {P(x, y + dd, z + h)[0]:.1f} {P(x, y + dd, z + h)[1]:.1f})', w, ink_l)
    right = (f'matrix(0.866 -0.5 0 1 {P(x + w, y + dd, z + h)[0]:.1f} {P(x + w, y + dd, z + h)[1]:.1f})', dd, ink_r)
    (tf, length, ink), (tf2, length2, ink2) = (right, left) if dd > w else (left, right)
    avail = length * U - 8 - 26
    label, fs = _fit(d["label"], avail, 11.5)
    sub, fs2 = _fit(d["sub"], avail, 8.2, 6.0, 0.55)
    out.append(f'<g transform="{tf}" fill="{ink}">'
               f'<text x="8" y="{h * U * 0.47:.1f}" font-size="{fs:.1f}" font-weight="700">{e(label)}</text>'
               f'<text x="8" y="{h * U * 0.8:.1f}" font-size="{fs2:.1f}" opacity=".85">{e(sub)}</text>'
               + ("" if ghost else _badge(d["val"], round(length * U - 14, 1), round(h * U / 2, 1))) + '</g>')
    out.append(f'<g transform="{tf2}" fill="{ink2}">'
               f'<text x="{length2 * U / 2:.1f}" y="{h * U * 0.62:.1f}" font-size="8" font-weight="600" letter-spacing=".6" '
               f'text-anchor="middle" opacity=".9">{e(d["kind"].upper())}</text></g>')
    cls = "b" + (" stale" if d["val"] == "stale" and not ghost else "") + (" ghost" if ghost else "") \
        + (" bin" if d.get("bin") else "") + "".join(f" r{k}" for k in d["rel"])
    gid = f' id="b{d["gi"]}"' if d["gi"] is not None else ""
    return f'<g class="{cls}"{gid}><title>{e(d["tip"])}</title>{"".join(out)}</g>'


def _plate_svg(it, stud_id, e):
    d = it.data
    x, y, z, w, dd, h = it.x, it.y, it.z, it.w, it.d, it.h
    c = d["color"]
    top, left, right = _faces(x, y, z, w, dd, h)
    ec = shade(c, -0.4)
    st = f'stroke="{ec}" stroke-width=".8" stroke-linejoin="round"'
    ink = _ink(c)
    label, fs = _fit(d["label"], w * U - 40, 10.5)
    ox, oy = P(x, y + dd, z + h)
    return (f'<g class="b{" stale" if d["val"] == "stale" else ""}{"".join(f" r{k}" for k in d["rel"])}" id="b{d["gi"]}">'
            f'<title>{e(d["tip"])}</title>'
            f'<polygon class="lf" points="{left}" fill="{c}" {st}/>'
            f'<polygon class="rf" points="{right}" fill="{shade(c, -0.26)}" {st}/>'
            f'<polygon class="tp" points="{top}" fill="{shade(c, 0.12)}" {st}/>'
            f'<polyline points="{_pts(P(x, y + dd, z + h), P(x + w, y + dd, z + h), P(x + w, y + dd, z))}" fill="none" '
            f'stroke="#fff" stroke-opacity=".4" stroke-width="1.1"/>'
            f'<g transform="matrix(0.866 0.5 0 1 {ox:.1f} {oy:.1f})" fill="{ink}">'
            f'<text x="10" y="{h * U * 0.66:.1f}" font-size="{fs:.1f}" font-weight="700" letter-spacing=".3">{e(label)}</text>'
            + ("" if d["val"] is None else _badge(d["val"], round(w * U - 14, 1), round(h * U / 2, 1))) +
            '</g></g>')


def _assemble(items, floor_shadows, cls, pad=(26, 22, 26, 34), top_shadows=()):
    """items: boxes in draw order. Returns an <svg> string."""
    e = htmllib.escape
    stud_cols = []
    for it in items:
        if it.kind in ("brick", "stud"):
            for col in [it.data["color"]] + [ELEMENT_STYLE[k][0] for k in (it.data.get("elements") or {})]:
                if col not in stud_cols:
                    stud_cols.append(col)
    stud_id = {c: "s" + c.lstrip("#") for c in stud_cols}
    pts_all = [p for it in items for p in it.corners()]
    for poly in list(floor_shadows) + list(top_shadows):
        pts_all += poly
    minx, maxx = min(p[0] for p in pts_all), max(p[0] for p in pts_all)
    miny, maxy = min(p[1] for p in pts_all), max(p[1] for p in pts_all)
    vx, vy = minx - pad[0], miny - pad[1] - 14
    vw, vh = (maxx - minx) + pad[0] + pad[2], (maxy - miny) + pad[1] + pad[3] + 14
    body = []
    for poly in floor_shadows:
        body.append(f'<polygon points="{_pts(*poly)}" fill="#1b2735" opacity=".24" filter="url(#blur)"/>')
    for it in items:
        if it.kind == "plate":
            body.append(_plate_svg(it, stud_id, e))
            for poly in top_shadows:
                body.append(f'<polygon points="{_pts(*poly)}" fill="#0b1b0b" opacity=".28" filter="url(#blur2)"/>')
        elif it.kind in ("brick", "ghost"):
            body.append(_brick_svg(it, stud_id, e))
        elif it.kind == "stud":
            sx, sy = P(it.x + 0.5, it.y + 0.5, it.z)
            body.append(_ref(stud_id[it.data["color"]], sx, sy))
        elif it.kind == "socket":
            sx, sy = P(it.x + 0.5, it.y + 0.5, it.z)
            body.append(_socket(sx, sy))
    defs = "".join(_stud_def(sid, col) for col, sid in stud_id.items())
    defs += ('<filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="7"/></filter>'
             '<filter id="blur2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.4"/></filter>')
    return (f'<svg class="{cls}" viewBox="{vx:.0f} {vy:.0f} {vw:.0f} {vh:.0f}" role="img" '
            f'aria-label="3D lego view of the model"><defs>{defs}</defs>{"".join(body)}</svg>')


# ------------------------------------------------------------------ the scene
def _scene(m, rep, cat, helpers):
    attached, provs, reqs, layer_of, suggestions = (helpers[k] for k in
                                                    ("attached", "provs", "reqs", "layer_of", "suggestions"))
    att = attached(m)
    gid = {b["id"]: i for i, b in enumerate(att)}
    stubs_by = {}
    for s in rep["stubs"]:
        stubs_by.setdefault(s["consumer"], []).append(s)
    rel = {b["id"]: set() for b in att}
    for j in rep["joints"]:
        if j["from"] in rel and j["to"] in rel and j["from"] != j["to"]:
            rel[j["from"]].add(j["to"])
            rel[j["to"]].add(j["from"])

    def data(b, bin_=False):
        kind = b.get("kind", "")
        st = stubs_by.get(b["id"], [])
        needs = ", ".join(q["port"] + (" (stub: " + q["stub"] + ")" if q["stub"] and any(s["port"] == q["port"] for s in st) else "")
                          for q in reqs(b)) or "nothing"
        el = helpers["elements_of"](b)[0]
        tip = (f'{b["id"]} ({kind}, {b.get("validation", "unvalidated")})\n{b.get("summary", "")}\n'
               f'provides: {", ".join(provs(b)) or "nothing"}\nneeds: {needs}')
        if el:
            tip += "\ninside: " + helpers["elements_line"](el)
            tip += "".join(f"\n{'⚠' if lv == 'warn' else '•'} {msg}" for lv, msg in helpers["element_flags"](b, el))
        return dict(label=b["id"], sub=f'{kind} · gives {len(provs(b))} · needs {len(reqs(b))}', kind=kind, elements=el,
                    color=PALETTE.get(kind, "#888"), val=b.get("validation", "unvalidated"), tip=tip,
                    sockets=len({s["port"] for s in st}), gi=gid.get(b["id"]), bin=bin_,
                    rel=sorted(gid[r] for r in rel.get(b["id"], ()) if r in gid))

    core = next((b for b in att if b.get("kind") == "baseplate"), None)
    towers = helpers["stacks"](m)  # bricks stack on the bricks whose outputs they read, any number of levels high
    binned_ids = {b["id"] for b in m.get("bricks", []) if b.get("status") == "detached"}
    sug = [s for s in suggestions(m, rep, cat) if s[0] not in binned_ids]  # parts-bin bricks are labelled on the shelf
    ghosts = sug[:MAX_GHOSTS]
    # each entry: (kind, brick or catalog id, x, y, level, w, d)
    layout = []
    placed = [b for b in att if b is not core and b.get("place")]
    if placed:  # positions written by `lego.py arrange` (or by hand): build exactly that
        for b in placed:
            x, y, w, d = helpers["footprint"](b["place"])
            layout.append(("brick", b, x, y, int(b["place"].get("level", 1)), w, d))
        W = max(x + w for _, _, x, _, _, w, _ in layout) + GAP
        yard_y = max(y + d for _, _, _, y, _, _, d in layout) + GAP + 1
        yard = [("brick", b) for b in att if b is not core and not b.get("place")] + [("ghost", cid) for cid, _ in ghosts]
        per_row = max(1, (W - GAP) // (BW + GAP))
        for k, (kind, ref) in enumerate(yard):  # the front yard: new bricks not yet placed, and suggestions
            layout.append((kind, ref, GAP + (k % per_row) * (BW + GAP), yard_y + (k // per_row) * (BD + GAP), 1, BW, BD))
        D = (yard_y + (-(-len(yard) // per_row)) * (BD + GAP)) if yard else yard_y
        D = max(D, yard_y)
    else:  # grid: towers side by side, taller towers further back so they do not hide others; ghosts in front
        slots = [("tower", t) for t in sorted(towers, key=lambda t: -len(t))] + [("ghost", cid) for cid, _ in ghosts]
        n = len(slots)
        cols = 1 if n <= 1 else 2 if n <= 4 else 3 if n <= 9 else 4
        rows = max(1, -(-n // cols))
        W = max(cols * (BW + GAP) + GAP, 8)
        D = rows * (BD + GAP) + GAP
        cells = sorted(((c, r) for r in range(rows) for c in range(cols)),
                       key=lambda cr: (cr[0] * (BW + GAP) + cr[1] * (BD + GAP), cr[0]))[:n]  # back (small x + y) first
        for (kind, ref), (c, r) in zip(slots, cells):
            x, y = GAP + c * (BW + GAP), GAP + r * (BD + GAP)
            if kind == "tower":
                layout += [("brick", b, x, y, level + 1, BW, BD) for level, b in enumerate(ref)]
            else:
                layout.append((kind, ref, x, y, 1, BW, BD))

    items, covered, pos = [], set(), {}
    plate_data = None
    if core is not None:
        plate_data = data(core)
        plate_data["label"] = f"BASEPLATE · {core['id']}"
        plate_data["color"] = PALETTE["baseplate"]
        plate_data["tip"] = "BASEPLATE: " + plate_data["tip"]
    else:
        plate_data = dict(label="BASEPLATE MISSING", color="#9aa5b1", val=None, tip="No baseplate attached", gi=-1, rel=[])
    items.append(_It("plate", 0, 0, 0, W, D, PH, plate_data))
    fills = dict(sug)
    for kind, ref, x, y, level, w, d in layout:
        if level == 1:
            for i in range(w):
                for j in range(d):
                    covered.add((x + i, y + j))
        if kind == "brick":
            it = _It("brick", x, y, PH + (level - 1) * BH, w, d, BH, data(ref))
            pos[ref["id"]] = it
        else:
            cb = cat[ref]
            dt = data(dict(cb, id=cb["id"], status="attached"))
            dt.update(gi=None, rel=[], val="unvalidated", sockets=0,
                      sub="fills: " + ", ".join(fills.get(ref, [])),
                      tip=f'Suggested brick: {cb["id"]}\n{cb.get("summary", "")}\nwould fill: {", ".join(fills.get(ref, []))}')
            it = _It("ghost", x, y, PH, w, d, BH, dt)
        items.append(it)
    # plate studs (open studs of the core are dashed sockets on the front row)
    n_sock = min(len({s["port"] for s in stubs_by.get(core["id"], [])}) if core else 0, W)
    sock_cells = {(i, D - 1) for i in range(n_sock)}
    for i in range(W):
        for j in range(D):
            if (i, j) in covered:
                continue
            kind = "socket" if (i, j) in sock_cells else "stud"
            items.append(_It(kind, i, j, PH, 1, 1, 0.001, dict(color=shade(PALETTE["baseplate"], 0.12))))
    floor = [[P(W + 1.4, 1.2, 0), P(W + 1.4, D + 1.4, 0), P(1.2, D + 1.4, 0), P(0.6, D + 0.4, 0), P(W + 0.4, 0.6, 0)]]
    tops = []
    for it in items:
        if it.kind in ("brick", "ghost") and it.z == PH:
            tops.append([P(it.x + 0.5, it.y + 0.5, PH), P(it.x1 + 0.5, it.y + 0.5, PH),
                         P(it.x1 + 0.5, it.y1 + 0.5, PH), P(it.x + 0.5, it.y1 + 0.5, PH)])
    hover = []
    for gi in range(len(att)):
        hover.append(f".scene:has(#b{gi}:hover) .b:not(#b{gi}):not(.r{gi}){{opacity:.3}}")
    return _assemble(_depth_sort(items), floor, "scene", top_shadows=tops), "".join(hover), sug[MAX_GHOSTS:], data


def _shelf(det, data_fn, fills):
    out = []
    for b in det:
        d = data_fn(b, bin_=True)
        d.update(gi=None, rel=[], val=b.get("validation", "unvalidated"))
        if fills.get(b["id"]):
            d["sub"] = "would fill: " + ", ".join(fills[b["id"]])
            d["tip"] += "\nwould fill open studs: " + ", ".join(fills[b["id"]])
        out.append(_assemble([_It("brick", 0, 0, 0, BW, BD, BH, d)],
                             [[P(1, 1, 0), P(BW + 1, 1, 0), P(BW + 1, BD + 1, 0), P(1, BD + 1, 0)]],
                             "bin-brick", pad=(14, 10, 14, 16)))
    return "".join(out)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lego set: %%TITLE%%</title>
<style>
:root{--ink:#1f2933;--mut:#617080;--line:#e3e8ee;--card:#fff;--bg:#f3f5f9}
*{box-sizing:border-box}
body{margin:0;font-family:"Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif;color:var(--ink);background:var(--bg)}
header{padding:22px 32px 4px}
h1{margin:0;font-size:24px;letter-spacing:-.2px}
.chips{margin-top:10px;display:flex;flex-wrap:wrap;gap:8px}
.chip{font-size:12px;padding:4px 11px;border-radius:999px;background:#fff;border:1px solid var(--line);color:var(--mut)}
.chip.ok{background:#e8f5e9;border-color:#c8e6c9;color:#2e7d32}
.chip.warn{background:#fff8e1;border-color:#ffe082;color:#8a6500}
.chip.bad{background:#ffebee;border-color:#ffcdd2;color:#c62828}
main{display:flex;gap:20px;padding:14px 32px 36px;align-items:flex-start;flex-wrap:wrap}
.stage{flex:1 1 720px;min-width:0;display:flex;flex-direction:column;gap:16px}
.side{flex:0 1 360px;min-width:280px;display:flex;flex-direction:column;gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:0 1px 2px rgba(16,24,40,.04),0 10px 28px rgba(16,24,40,.06)}
.canvas{background:radial-gradient(ellipse at 50% 30%,#fff 0%,#eef2f8 62%,#e5eaf2 100%);padding:10px 10px 4px;border-radius:14px}
.scene{display:block;width:100%;height:auto;max-height:80vh}
.scene text{font-family:"Segoe UI",system-ui,Arial,sans-serif;pointer-events:none}
.b{transition:opacity .18s}
.b:hover .tp{filter:brightness(1.1)}
.b.stale .lf,.b.stale .rf,.b.stale .tp{stroke:#ffb300;stroke-width:2.2}
.b.bin{opacity:.8}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;padding:10px 16px 12px;font-size:12px;color:var(--mut)}
.legend i{display:inline-block;vertical-align:-3px;margin-right:6px}
.sock{width:16px;height:10px;border-radius:50%;border:1.6px dashed #ffd54f;background:#444}
.gh{width:20px;height:12px;border:1.6px dashed #fb8c00;border-radius:3px}
.st{width:14px;height:14px;border-radius:50%;background:#ffb300;color:#3b2a00;font:700 10px/14px Arial;text-align:center}
.ok{width:14px;height:14px;border-radius:50%;background:#2e9d4f;color:#fff;font:700 10px/14px Arial;text-align:center}
.ring{width:12px;height:12px;border-radius:50%;border:1.8px solid #8a97a6}
section.card{padding:14px 18px 16px}
h3{margin:0 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:.7px;color:var(--mut)}
ul{margin:0;padding-left:18px;font-size:13px;line-height:1.55}
code{background:#eef1f5;padding:0 4px;border-radius:4px;font-size:12px}
.err{color:#c62828}.warn{color:#b26a00}
.shelf{display:flex;flex-wrap:wrap;gap:6px;align-items:flex-end;min-height:30px}
.bin-brick{width:210px;height:auto}
.empty{color:#97a3b1;font-size:13px;margin:0}
.hint{font-size:12px;color:var(--mut);margin:0 0 0 2px}
.switch{display:inline-flex;align-items:center;gap:6px;font-weight:600;color:var(--ink);cursor:pointer}
body:has(#elmode:checked) .sk,body:not(:has(#elmode:checked)) .se{display:none}
body:not(:has(#elmode:checked)) .eleg{opacity:.45}
.ec{display:inline-flex;align-items:center;gap:4px;font-size:12px;color:var(--ink);white-space:nowrap}
.ec b{display:inline-block;min-width:17px;height:17px;padding:0 3px;border-radius:5px;background:var(--c);color:#fff;
  font:700 11px/17px "Segoe UI",Arial,sans-serif;text-align:center;box-shadow:inset 0 -2px 0 rgba(0,0,0,.18)}
.ec b.lt{color:#2b2100}
.ec small{color:var(--mut);font-size:11px}
.an{display:flex;flex-direction:column;gap:10px}
.an-row{display:grid;grid-template-columns:minmax(150px,210px) 1fr;gap:4px 14px;align-items:center;padding:8px 0;border-top:1px solid var(--line)}
.an-row:first-child{border-top:0}
.an-name{display:flex;align-items:center;gap:7px;font-size:13px;font-weight:600;min-width:0}
.an-name i{flex:0 0 12px;height:12px;border-radius:3px}
.an-name span{font-weight:400;color:var(--mut);font-size:11px}
.an-bar{display:flex;height:12px;border-radius:6px;overflow:hidden;background:#eef1f5}
.an-bar span{display:block;min-width:3px}
.an-counts{grid-column:2;display:flex;flex-wrap:wrap;gap:4px 12px}
.an-flags{grid-column:2;font-size:12px;line-height:1.5}
.an-flags .w{color:#b26a00}.an-flags .n{color:var(--mut)}
.an-none{grid-column:2;font-size:12px;color:#97a3b1}
@media (max-width:640px){.an-row{grid-template-columns:1fr}.an-counts,.an-flags,.an-none{grid-column:1}}
%%HOVER%%
</style></head><body>
<header><h1>%%NAME%%</h1><div class="chips">%%CHIPS%%</div></header>
<main>
<div class="stage">
<div class="card"><div class="canvas">%%SCENE%%</div>
<div class="legend">
<span><i class="ok">✓</i>validated</span><span><i class="ring"></i>not yet validated</span><span><i class="st">!</i>stale (changed since validation)</span>
<span><i class="sock"></i>open stud: input running on a stub</span><span><i class="gh"></i>suggested brick that would fill it</span>
<span>Bricks sit on the baseplate; satellites and outputs sit on the brick they read. Hover a brick to see what it connects to.</span></div>
<div class="legend"><label class="switch"><input type="checkbox" id="elmode" checked>Studs show what each brick is made of</label>
<span class="eleg">%%ELEGEND%%</span><span>Brick colour shows the component; untick to colour the studs by component too.</span></div></div>
<section class="card"><h3>Inside the bricks</h3><div class="an">%%ANATOMY%%</div></section>
<section class="card"><h3>Parts bin (detached bricks)</h3><div class="shelf">%%SHELF%%</div></section>
</div>
<div class="side">
<section class="card"><h3>Open studs (stubs)</h3><ul>%%STUBS%%</ul>%%MORE%%</section>
<section class="card"><h3>Joints</h3><ul>%%JOINTS%%</ul></section>
<section class="card"><h3>Simultaneous blocks</h3><ul>%%SIMS%%</ul></section>
<section class="card"><h3>Identities</h3><ul>%%IDS%%</ul></section>
<section class="card"><h3>Errors and warnings</h3><ul>%%PROBS%%</ul></section>
</div></main></body></html>
"""


def render(m, rep, cat, helpers):
    e = htmllib.escape
    att = helpers["attached"](m)
    det = [b for b in m.get("bricks", []) if b.get("status") == "detached"]
    scene, hover, more, data_fn = _scene(m, rep, cat, helpers)
    shelf = _shelf(det, data_fn, dict(helpers["suggestions"](m, rep, cat))) or '<p class="empty">empty. Detached bricks appear here and can be snapped back on.</p>'
    verdict = helpers["model_validation"](m, rep)
    vcls = "bad" if rep["errors"] else ("ok" if verdict.startswith("all attached") else "warn")
    chips = "".join(f'<span class="chip {c}">{e(t)}</span>' for c, t in (
        ("", f"class {m.get('class', '?')}"), ("", f"frequency {m.get('freq', '?')}"), ("", f"revision {m.get('revision', 0)}"),
        ("", f"{len(att)} attached, {len(det)} detached"),
        (vcls, ("errors: " + str(len(rep["errors"]))) if rep["errors"] else verdict)))
    li = lambda xs: "".join(xs) or "<li>none</li>"
    stubs = li(f"<li><b>{e(s['consumer'])}</b> &larr; <code>{e(s['port'])}</code>: {e(s['stub'])}</li>" for s in rep["stubs"])
    joints = li(f"<li>{e(j['from'])} &rarr; <code>{e(j['port'])}</code> &rarr; {e(j['to'])}{' (lag ' + str(j['lag']) + ')' if j['lag'] else ''}</li>" for j in rep["joints"])
    sims = li(f"<li>{e(', '.join(b))}</li>" for b in rep["sim_blocks"])
    ids = li(f"<li>{e(i['name'])}: {e(i['status'])}</li>" for i in rep["identities"]) if rep["identities"] else "<li>none declared</li>"
    probs = li([f"<li class='err'>{e(x)}</li>" for x in rep["errors"]] + [f"<li class='warn'>{e(x)}</li>" for x in rep["warnings"]])
    chip = lambda k, n=None, note="": (f'<span class="ec" style="--c:{ELEMENT_STYLE[k][0]}" title="{ELEMENT_STYLE[k][2]}"><b{" class=lt" if k == "variables" else ""}>'
                                       f'{ELEMENT_STYLE[k][1]}</b>{"" if n is None else n}'
                                       f'{" " + ELEMENT_STYLE[k][2] if n is None else ""}{f" <small>{e(note)}</small>" if note else ""}</span>')
    elegend = " ".join(chip(k) for k in ELEMENT_STYLE)
    rows = []
    for b in att:
        el = rep.get("elements", {}).get(b["id"])
        name = (f'<div class="an-name"><i style="background:{PALETTE.get(b.get("kind"), "#888")}"></i>{e(b["id"])}'
                f'<span>{e(b.get("kind", ""))}</span></div>')
        if not el:
            rows.append(f'<div class="an-row">{name}<div class="an-none">elements not declared yet '
                        f'(<code>lego.py elements</code>)</div></div>')
            continue
        bar = "".join(f'<span style="flex:{el[k]["total"]};background:{ELEMENT_STYLE[k][0]}" '
                      f'title="{el[k]["total"]} {ELEMENT_STYLE[k][2]}"></span>' for k in ELEMENT_STYLE if k in el and el[k]["total"])
        counts = []
        for k in ELEMENT_STYLE:
            if k in el:
                nz = [(p, n) for p, n in el[k]["parts"].items() if n and not (k == "data" and p == "series")]
                parts = [p for p, _ in nz] if len(nz) == 1 else [f"{n} {p}" for p, n in nz]  # "22 endogenous", not "22 22 endogenous"
                parts += [("vintage " if f == "vintage" else "") + t for f, t in el[k]["text"].items()]
                counts.append(chip(k, el[k]["total"], " · ".join(parts)))
        flags = "".join(f'<div class="{"w" if lv == "warn" else "n"}">{"⚠" if lv == "warn" else "•"} {e(msg)}</div>'
                        for lv, msg in helpers["element_flags"](b, el))
        rows.append(f'<div class="an-row">{name}<div class="an-bar">{bar}</div><div class="an-counts">{"".join(counts)}</div>'
                    + (f'<div class="an-flags">{flags}</div>' if flags else "") + "</div>")
    anatomy = "".join(rows) or '<p class="empty">no bricks attached</p>'
    more_html = ""
    if more:
        more_html = ('<p class="hint">More bricks in the catalog that would help: '
                     + ", ".join(f"<code>{e(cid)}</code>" for cid, _ in more) + "</p>")
    page = PAGE
    for k, v in (("%%TITLE%%", e(m.get("name", ""))), ("%%NAME%%", e(m.get("name", "Model"))), ("%%HOVER%%", hover),
                 ("%%CHIPS%%", chips), ("%%SCENE%%", scene), ("%%SHELF%%", shelf), ("%%STUBS%%", stubs),
                 ("%%MORE%%", more_html), ("%%ELEGEND%%", elegend), ("%%ANATOMY%%", anatomy), ("%%JOINTS%%", joints), ("%%SIMS%%", sims), ("%%IDS%%", ids), ("%%PROBS%%", probs)):
        page = page.replace(k, v)
    return page
