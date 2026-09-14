# -*- coding: utf-8 -*-
"""
chart_svg.py — dependency-free inline-SVG chart primitives for the PDF brief family.

Why SVG-in-Python and not a JS chart library: these charts are printed by Edge
headless with no network. A CDN <script> would silently render nothing, and a
bundled JS lib still needs a paint pass we cannot verify. Every function here
returns a finished <svg> string that Edge lays out like any other element —
deterministic, vector-sharp at print DPI, and diffable in git.

Used by PDF formats 00 (`full-spectrum`) and 02 (`analytics-deep`) via
brief_pdf.py's `chart` / `kpi` block types. See ../pdf-styles/INDEX.md.

All sizes are user units on a viewBox; the wrapper CSS scales to column width.
Every function is pure: same args -> byte-identical SVG (no randomness, no clock).
"""
import html as _H
import math

# ---------------------------------------------------------------- palette ----
# Series colors chosen for print: distinguishable in CMYK and in greyscale
# (alternating light/dark value), colour-blind-safe ordering.
SERIES = ["#1D4ED8", "#0F766E", "#B45309", "#6D28D9", "#BE185D",
          "#0369A1", "#4D7C0F", "#9F1239", "#334155", "#0891B2"]
GRID = "#E5E7EB"
AXIS = "#9CA3AF"
INK = "#1f2937"
MUTED = "#6B7280"
FONT = "'Segoe UI',Calibri,Arial,sans-serif"

TONE = {  # semantic tones, aligned with brief_pdf's PALETTE
    "green": "#059669", "amber": "#D97706", "red": "#DC2626", "slate": "#475569",
    "sky": "#0284C7", "violet": "#7C3AED", "rose": "#E11D48", "teal": "#0D9488",
    "blue": "#2563EB", "indigo": "#4F46E5", "navy": "#1A237E",
}


def esc(s):
    return _H.escape(str(s))


def _n(v):
    """Compact number format: 1234567 -> 1.23M, 1234 -> 1.2k."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    def _trim(t):
        return t.rstrip("0").rstrip(".") if "." in t else t
    a = abs(v)
    if a >= 1e9:
        s = _trim("%.2f" % (v / 1e9)) + "B"
    elif a >= 1e6:
        s = _trim("%.2f" % (v / 1e6)) + "M"
    elif a >= 1e3:
        s = _trim("%.1f" % (v / 1e3)) + "k"
    elif a == int(a):
        s = str(int(v))
    else:
        s = _trim("%.2f" % v)
    return s


def _nice(x):
    """Round x up to a nice 1/2/5 x 10^n number — for axis tick steps."""
    if x == 0:
        return 1
    exp = math.floor(math.log10(abs(x)))
    f = abs(x) / (10 ** exp)
    nf = 1 if f <= 1 else (2 if f <= 2 else (5 if f <= 5 else 10))
    return nf * (10 ** exp)


def _ticks(lo, hi, count=5):
    """Nice tick values spanning [lo, hi]."""
    if hi == lo:
        hi = lo + 1
    step = _nice((hi - lo) / max(1, count))
    start = math.floor(lo / step) * step
    end = math.ceil(hi / step) * step
    out = []
    v = start
    while v <= end + step * 1e-9:
        out.append(round(v, 10))
        v += step
    return out


def _txt(x, y, s, size=10, fill=INK, anchor="start", weight="normal", rot=None):
    tr = ' transform="rotate(%s,%.1f,%.1f)"' % (rot, x, y) if rot is not None else ""
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s" font-weight="%s"%s>%s</text>'
            % (x, y, FONT, size, fill, anchor, weight, tr, esc(s)))


def _svg(w, h, body, cls="cw"):
    # width:100% but capped at the chart's NATURAL width -- a narrow chart
    # (heatmap/gauge/radar) must never be upscaled to the column width.
    return ('<svg class="%s" viewBox="0 0 %s %s" style="width:100%%;max-width:%spx;height:auto" '
            'preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" '
            'role="img">%s</svg>' % (cls, w, h, w, body))


def _grid_y(x0, x1, ticks, sy, labels=True, fmt=None):
    fmt = fmt or _n
    g = []
    for t in ticks:
        y = sy(t)
        g.append('<line x1="%s" y1="%.1f" x2="%s" y2="%.1f" stroke="%s" stroke-width="1"/>'
                 % (x0, y, x1, y, GRID))
        if labels:
            g.append(_txt(x0 - 6, y + 3.5, fmt(t), 9.5, MUTED, "end"))
    return "".join(g)


def _legend(items, x, y, size=10):
    """items = [(label, color)] laid out horizontally."""
    out = []
    cx = x
    for lab, col in items:
        out.append('<rect x="%.1f" y="%.1f" width="10" height="10" rx="2" fill="%s"/>' % (cx, y - 8, col))
        out.append(_txt(cx + 14, y, lab, size, MUTED))
        cx += 14 + len(str(lab)) * (size * 0.56) + 18
    return "".join(out)


# ------------------------------------------------------------------ charts ---
def bar(data, height=230, width=760, ylabel=None, tone=None, target=None,
        show_values=True, rotate_labels=False):
    """Vertical bars. data = [(label, value), ...]. `target` draws a dashed goal line."""
    if not data:
        return ""
    labels = [d[0] for d in data]
    vals = [float(d[1]) for d in data]
    color = TONE.get(tone, SERIES[0]) if tone else SERIES[0]
    L, R, T, B = 54, 14, (24 if ylabel else 16), (56 if rotate_labels else 34)
    hi_src = vals + ([float(target)] if target is not None else [])
    tk = _ticks(min(0, min(vals)), max(hi_src))
    y0, y1 = height - B, T
    span_v = (tk[-1] - tk[0]) or 1

    def sy(v):
        return y1 + (tk[-1] - v) / span_v * (y0 - y1)

    n = len(data)
    span = (width - L - R) / n
    bw = min(span * 0.62, 64)
    p = [_grid_y(L, width - R, tk, sy)]
    for i, (lab, v) in enumerate(zip(labels, vals)):
        cx = L + span * i + span / 2
        yv, yz = sy(v), sy(0)
        top, hgt = min(yv, yz), abs(yz - yv)
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s"/>'
                 % (cx - bw / 2, top, bw, max(hgt, 0.6), color))
        if show_values:
            p.append(_txt(cx, top - 5, _n(v), 9.5, INK, "middle", "bold"))
        if rotate_labels:
            p.append(_txt(cx, y0 + 12, lab, 9, MUTED, "end", rot=-38))
        else:
            p.append(_txt(cx, y0 + 15, lab, 9.5, MUTED, "middle"))
    if target is not None:
        yt = sy(float(target))
        p.append('<line x1="%s" y1="%.1f" x2="%s" y2="%.1f" stroke="%s" stroke-width="1.5" '
                 'stroke-dasharray="6 4"/>' % (L, yt, width - R, yt, TONE["red"]))
        p.append(_txt(width - R - 2, yt - 5, "target " + _n(target), 9, TONE["red"], "end", "bold"))
    p.append('<line x1="%s" y1="%.1f" x2="%s" y2="%.1f" stroke="%s" stroke-width="1.2"/>'
             % (L, sy(0), width - R, sy(0), AXIS))
    if ylabel:
        p.append(_txt(8, 10, ylabel, 9, MUTED))
    return _svg(width, height, "".join(p))


def hbar(data, width=760, show_values=True, tone=None, labelw=170):
    """Horizontal ranked bars — best for long labels / league tables."""
    if not data:
        return ""
    data = list(data)
    rowh = 26
    height = len(data) * rowh + 18
    color = TONE.get(tone, SERIES[0]) if tone else SERIES[0]
    L, R = labelw, 54
    hi = max(float(d[1]) for d in data) or 1
    p = []
    for i, (lab, v) in enumerate(data):
        y = 8 + i * rowh
        w = (width - L - R) * (float(v) / hi)
        p.append(_txt(L - 8, y + 13, lab, 9.5, INK, "end"))
        p.append('<rect x="%s" y="%.1f" width="%.1f" height="15" rx="3" fill="#F1F5F9"/>'
                 % (L, y + 3, width - L - R))
        p.append('<rect x="%s" y="%.1f" width="%.1f" height="15" rx="3" fill="%s"/>'
                 % (L, y + 3, max(w, 1), color))
        if show_values:
            p.append(_txt(L + w + 6, y + 15, _n(v), 9.5, INK, "start", "bold"))
    return _svg(width, height, "".join(p))


def grouped_bar(categories, series, height=250, width=760, ylabel=None):
    """series = [(name, [v per category]), ...]"""
    if not categories or not series:
        return ""
    L, R, T, B = 54, 14, 26, 46
    allv = [float(v) for _, vs in series for v in vs]
    tk = _ticks(min(0, min(allv)), max(allv))
    y0, y1 = height - B, T
    span_v = (tk[-1] - tk[0]) or 1

    def sy(v):
        return y1 + (tk[-1] - v) / span_v * (y0 - y1)

    n, m = len(categories), len(series)
    span = (width - L - R) / n
    bw = min(span * 0.78 / m, 34)
    p = [_grid_y(L, width - R, tk, sy)]
    for ci in range(n):
        base = L + span * ci + span / 2 - (bw * m) / 2
        for si, (name, vs) in enumerate(series):
            v = float(vs[ci]) if ci < len(vs) else 0.0
            yv, yz = sy(v), sy(0)
            p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"/>'
                     % (base + si * bw, min(yv, yz), max(bw - 2, 2), max(abs(yz - yv), 0.6),
                        SERIES[si % len(SERIES)]))
        p.append(_txt(L + span * ci + span / 2, y0 + 15, categories[ci], 9.5, MUTED, "middle"))
    p.append('<line x1="%s" y1="%.1f" x2="%s" y2="%.1f" stroke="%s" stroke-width="1.2"/>'
             % (L, sy(0), width - R, sy(0), AXIS))
    p.append(_legend([(s[0], SERIES[i % len(SERIES)]) for i, s in enumerate(series)], L, 12))
    if ylabel:
        p.append(_txt(8, 10, ylabel, 9, MUTED))
    return _svg(width, height, "".join(p))


def stacked_bar(categories, series, height=250, width=760, pct=False):
    """Stacked (or 100%-stacked when pct=True). series = [(name, [v...]), ...]"""
    if not categories or not series:
        return ""
    L, R, T, B = 54, 14, 26, 46
    n = len(categories)
    totals = [sum(float(s[1][i]) if i < len(s[1]) else 0.0 for s in series) for i in range(n)]
    hi = 100 if pct else (max(totals) if totals else 1)
    tk = _ticks(0, hi)
    y0, y1 = height - B, T
    span_v = (tk[-1] - tk[0]) or 1

    def sy(v):
        return y1 + (tk[-1] - v) / span_v * (y0 - y1)

    span = (width - L - R) / n
    bw = min(span * 0.6, 62)
    p = [_grid_y(L, width - R, tk, sy, fmt=(lambda t: _n(t) + "%") if pct else _n)]
    for ci in range(n):
        cx = L + span * ci + span / 2
        acc = 0.0
        for si, (name, vs) in enumerate(series):
            v = float(vs[ci]) if ci < len(vs) else 0.0
            if pct and totals[ci]:
                v = v / totals[ci] * 100.0
            yb, yt = sy(acc), sy(acc + v)
            p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                     % (cx - bw / 2, yt, bw, max(yb - yt, 0), SERIES[si % len(SERIES)]))
            if (yb - yt) > 13:
                p.append(_txt(cx, (yb + yt) / 2 + 3.5, _n(round(v, 1)), 8.6, "#fff", "middle", "bold"))
            acc += v
        p.append(_txt(cx, y0 + 15, categories[ci], 9.5, MUTED, "middle"))
    p.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.2"/>'
             % (L, y0, width - R, y0, AXIS))
    p.append(_legend([(s[0], SERIES[i % len(SERIES)]) for i, s in enumerate(series)], L, 12))
    return _svg(width, height, "".join(p))


def line(labels, series, height=250, width=760, area=False, ylabel=None,
         markers=True, band=None):
    """Multi-series line/area. series=[(name,[v...])]. band=(lo[],hi[]) draws a range ribbon."""
    if not labels or not series:
        return ""
    L, R, T, B = 54, 16, 26, 40
    allv = [float(v) for _, vs in series for v in vs if v is not None]
    if band:
        allv += [float(v) for v in list(band[0]) + list(band[1]) if v is not None]
    tk = _ticks(min(allv), max(allv))
    y0, y1 = height - B, T
    n = len(labels)
    span_v = (tk[-1] - tk[0]) or 1

    def sx(i):
        return L + (width - L - R) * (i / max(1, n - 1))

    def sy(v):
        return y1 + (tk[-1] - float(v)) / span_v * (y0 - y1)

    p = [_grid_y(L, width - R, tk, sy)]
    if band:
        lo, hi = band
        pts = ["%.1f,%.1f" % (sx(i), sy(hi[i])) for i in range(n)]
        pts += ["%.1f,%.1f" % (sx(i), sy(lo[i])) for i in range(n - 1, -1, -1)]
        p.append('<polygon points="%s" fill="%s" opacity="0.10"/>' % (" ".join(pts), SERIES[0]))
    for si, (name, vs) in enumerate(series):
        col = SERIES[si % len(SERIES)]
        pts = [(sx(i), sy(v)) for i, v in enumerate(vs) if v is not None]
        if not pts:
            continue
        d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        if area and si == 0:
            p.append('<polygon points="%s %.1f,%.1f %.1f,%.1f" fill="%s" opacity="0.13"/>'
                     % (d, pts[-1][0], sy(tk[0]), pts[0][0], sy(tk[0]), col))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % (d, col))
        if markers:
            for x, y in pts:
                p.append('<circle cx="%.1f" cy="%.1f" r="2.8" fill="#fff" stroke="%s" stroke-width="1.8"/>'
                         % (x, y, col))
    step = max(1, n // 12)
    for i, lab in enumerate(labels):
        if i % step == 0 or i == n - 1:
            p.append(_txt(sx(i), y0 + 15, lab, 9.2, MUTED, "middle"))
    p.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.2"/>'
             % (L, y0, width - R, y0, AXIS))
    p.append(_legend([(s[0], SERIES[i % len(SERIES)]) for i, s in enumerate(series)], L, 12))
    if ylabel:
        p.append(_txt(8, 10, ylabel, 9, MUTED))
    return _svg(width, height, "".join(p))


def donut(data, height=240, width=760, center=None, sub=None, thickness=42):
    """data=[(label,value)]. Ring at left, value+share legend at right."""
    if not data:
        return ""
    total = sum(float(d[1]) for d in data) or 1.0
    cx, cy = 132, height / 2
    r = min(height / 2 - 12, 92)
    ri = r - thickness
    p = []
    ang = -math.pi / 2
    for i, (lab, v) in enumerate(data):
        frac = float(v) / total
        a2 = ang + frac * 2 * math.pi
        large = 1 if frac > 0.5 else 0
        x1, y1 = cx + r * math.cos(ang), cy + r * math.sin(ang)
        x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        x3, y3 = cx + ri * math.cos(a2), cy + ri * math.sin(a2)
        x4, y4 = cx + ri * math.cos(ang), cy + ri * math.sin(ang)
        p.append('<path d="M%.1f,%.1f A%s,%s 0 %s 1 %.1f,%.1f L%.1f,%.1f A%s,%s 0 %s 0 %.1f,%.1f Z" fill="%s"/>'
                 % (x1, y1, r, r, large, x2, y2, x3, y3, ri, ri, large, x4, y4, SERIES[i % len(SERIES)]))
        ang = a2
    if center:
        p.append(_txt(cx, cy + 2, center, 20, INK, "middle", "bold"))
        if sub:
            p.append(_txt(cx, cy + 18, sub, 9.5, MUTED, "middle"))
    ly = cy - len(data) * 11 + 6
    for i, (lab, v) in enumerate(data):
        y = ly + i * 22
        p.append('<rect x="266" y="%.1f" width="11" height="11" rx="2" fill="%s"/>' % (y - 9, SERIES[i % len(SERIES)]))
        p.append(_txt(284, y, lab, 10, INK))
        p.append(_txt(284, y + 12, "%s  ·  %.1f%%" % (_n(v), float(v) / total * 100), 9, MUTED))
    return _svg(width, height, "".join(p))


def sparkline(values, width=120, height=26, tone="blue", fill=True):
    """Tiny inline trend — for table cells and KPI tiles."""
    vs = [float(v) for v in values if v is not None]
    if len(vs) < 2:
        return ""
    lo, hi = min(vs), max(vs)
    rng = (hi - lo) or 1
    col = TONE.get(tone, SERIES[0])
    n = len(vs)
    pts = [((width - 4) * i / (n - 1) + 2, height - 3 - (v - lo) / rng * (height - 8))
           for i, v in enumerate(vs)]
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    p = []
    if fill:
        p.append('<polygon points="%s %.1f,%s %.1f,%s" fill="%s" opacity="0.15"/>'
                 % (d, pts[-1][0], height, pts[0][0], height, col))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linejoin="round"/>' % (d, col))
    p.append('<circle cx="%.1f" cy="%.1f" r="2.2" fill="%s"/>' % (pts[-1][0], pts[-1][1], col))
    return ('<svg class="spark" viewBox="0 0 %s %s" width="%s" height="%s" '
            'xmlns="http://www.w3.org/2000/svg">%s</svg>' % (width, height, width, height, "".join(p)))


def progress(rows, width=760, tone="teal", show_pct=True, labelw=190):
    """rows = [(label, pct)] or [(label, pct, note)] — 0..100 completion bars."""
    if not rows:
        return ""
    rowh = 30
    height = len(rows) * rowh + 10
    col = TONE.get(tone, SERIES[0])
    p = []
    for i, r in enumerate(rows):
        lab, pct = r[0], float(r[1])
        note = r[2] if len(r) > 2 else None
        y = 6 + i * rowh
        p.append(_txt(0, y + 12, lab, 9.6, INK))
        bx = labelw
        bw = width - labelw - 54
        p.append('<rect x="%s" y="%.1f" width="%.1f" height="14" rx="7" fill="#EEF2F7"/>' % (bx, y + 3, bw))
        c = TONE["red"] if pct < 34 else (TONE["amber"] if pct < 67 else col)
        p.append('<rect x="%s" y="%.1f" width="%.1f" height="14" rx="7" fill="%s"/>'
                 % (bx, y + 3, max(bw * pct / 100.0, 2), c))
        if show_pct:
            p.append(_txt(width - 48, y + 15, "%.0f%%" % pct, 9.6, INK, "start", "bold"))
        if note:
            p.append(_txt(bx, y + 26, note, 8.4, MUTED))
    return _svg(width, height, "".join(p))


def bullet(rows, width=760):
    """Actual-vs-target bullet bars. rows=[(label, actual, target, max)]"""
    if not rows:
        return ""
    rowh = 34
    height = len(rows) * rowh + 10
    L, R = 180, 62
    p = []
    for i, (lab, act, tgt, mx) in enumerate(rows):
        y = 8 + i * rowh
        bw = width - L - R
        p.append(_txt(0, y + 14, lab, 9.6, INK))
        p.append('<rect x="%s" y="%.1f" width="%.1f" height="16" rx="3" fill="#F1F5F9"/>' % (L, y + 4, bw))
        p.append('<rect x="%s" y="%.1f" width="%.1f" height="16" fill="#E8EDF3"/>' % (L, y + 4, bw * 0.66))
        aw = bw * (float(act) / (float(mx) or 1))
        good = float(act) >= float(tgt)
        p.append('<rect x="%s" y="%.1f" width="%.1f" height="8" rx="2" fill="%s"/>'
                 % (L, y + 8, max(aw, 2), TONE["green"] if good else TONE["amber"]))
        tx = L + bw * (float(tgt) / (float(mx) or 1))
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.4"/>'
                 % (tx, y + 2, tx, y + 22, INK))
        p.append(_txt(width - R + 6, y + 16, "%s/%s" % (_n(act), _n(tgt)), 9.2,
                      TONE["green"] if good else TONE["amber"], "start", "bold"))
    return _svg(width, height, "".join(p))


def heatmap(rows, cols, matrix, width=760, cell=32, tone="blue", fmt=None):
    """matrix[r][c] numeric (None = blank). Colour intensity = share of max."""
    if not rows or not cols:
        return ""
    L, T = 152, 30
    w = min(width, L + len(cols) * cell + 12)
    height = T + len(rows) * cell + 8
    flat = [float(v) for r in matrix for v in r if v is not None]
    hi = max(flat) if flat else 1
    base = TONE.get(tone, SERIES[0])
    p = []
    for ci, c in enumerate(cols):
        p.append(_txt(L + ci * cell + cell / 2, T - 8, c, 8.8, MUTED, "middle"))
    for ri, rlab in enumerate(rows):
        p.append(_txt(L - 8, T + ri * cell + cell / 2 + 3.5, rlab, 9.4, INK, "end"))
        for ci in range(len(cols)):
            v = matrix[ri][ci] if ci < len(matrix[ri]) else None
            x, y = L + ci * cell, T + ri * cell
            if v is None:
                p.append('<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="#F8FAFC"/>'
                         % (x, y, cell - 2, cell - 2))
                continue
            op = 0.12 + 0.88 * (float(v) / hi if hi else 0)
            p.append('<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="%s" opacity="%.2f"/>'
                     % (x, y, cell - 2, cell - 2, base, op))
            p.append(_txt(x + (cell - 2) / 2, y + cell / 2 + 3, fmt(v) if fmt else _n(v), 8.2,
                          "#fff" if op > 0.55 else INK, "middle", "bold"))
    return _svg(w, height, "".join(p))


def scatter(points, height=260, width=760, xlabel=None, ylabel=None, labels=True):
    """points = [(x, y, label?, tone?)]"""
    if not points:
        return ""
    L, R, T, B = 54, 16, 18, 40
    xs = [float(p[0]) for p in points]
    ys = [float(p[1]) for p in points]
    tkx, tky = _ticks(min(xs), max(xs), 5), _ticks(min(ys), max(ys), 5)
    y0, y1 = height - B, T
    spx = (tkx[-1] - tkx[0]) or 1
    spy = (tky[-1] - tky[0]) or 1

    def sx(v):
        return L + (float(v) - tkx[0]) / spx * (width - L - R)

    def sy(v):
        return y1 + (tky[-1] - float(v)) / spy * (y0 - y1)

    p = [_grid_y(L, width - R, tky, sy)]
    for t in tkx:
        p.append('<line x1="%.1f" y1="%s" x2="%.1f" y2="%s" stroke="%s" stroke-width="1"/>'
                 % (sx(t), y1, sx(t), y0, GRID))
        p.append(_txt(sx(t), y0 + 15, _n(t), 9.2, MUTED, "middle"))
    for i, pt in enumerate(points):
        x, y = sx(pt[0]), sy(pt[1])
        col = TONE.get(pt[3], SERIES[i % len(SERIES)]) if len(pt) > 3 else SERIES[i % len(SERIES)]
        p.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" opacity="0.82"/>' % (x, y, col))
        if labels and len(pt) > 2 and pt[2]:
            p.append(_txt(x + 9, y + 3.5, pt[2], 8.8, INK))
    p.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.2"/>'
             % (L, y0, width - R, y0, AXIS))
    if xlabel:
        p.append(_txt(width - R, height - 6, xlabel, 9, MUTED, "end"))
    if ylabel:
        p.append(_txt(8, 10, ylabel, 9, MUTED))
    return _svg(width, height, "".join(p))


def gauge(value, vmax=100, width=260, height=150, label=None, tone=None, bands=None):
    """Half-circle gauge. bands=[(upto, color)] for zoned backgrounds."""
    cx, cy = width / 2, height - 22
    r = min(width / 2 - 14, 96)
    th = 22
    frac = max(0.0, min(1.0, float(value) / (float(vmax) or 1)))
    col = TONE.get(tone) if tone else (TONE["red"] if frac < .34 else
                                       TONE["amber"] if frac < .67 else TONE["green"])

    def arc(f0, f1, color, thick):
        a0, a1 = math.pi + f0 * math.pi, math.pi + f1 * math.pi
        x1, y1 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x2, y2 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        return ('<path d="M%.1f,%.1f A%s,%s 0 0 1 %.1f,%.1f" fill="none" stroke="%s" '
                'stroke-width="%s" stroke-linecap="round"/>' % (x1, y1, r, r, x2, y2, color, thick))

    p = [arc(0, 1, "#EEF2F7", th)]
    if bands:
        prev = 0.0
        for upto, c in bands:
            f = max(0.0, min(1.0, float(upto) / (float(vmax) or 1)))
            p.append(arc(prev, f, c, th * 0.42))
            prev = f
    if frac > 0:
        p.append(arc(0, frac, col, th))
    p.append(_txt(cx, cy - 6, _n(value), 26, INK, "middle", "bold"))
    if label:
        p.append(_txt(cx, cy + 14, label, 9.6, MUTED, "middle"))
    return _svg(width, height, "".join(p), cls="cw gauge")


def waterfall(steps, height=250, width=760, ylabel=None):
    """steps = [(label, delta)]; a (label, None) entry draws the running total."""
    if not steps:
        return ""
    L, R, T, B = 54, 14, 18, 48
    acc = 0.0
    run = []
    for lab, d in steps:
        if d is None:
            run.append((lab, 0.0, acc, True))
        else:
            run.append((lab, acc, acc + float(d), False))
            acc += float(d)
    vals = [v for r in run for v in (r[1], r[2])]
    tk = _ticks(min(0, min(vals)), max(vals))
    y0, y1 = height - B, T
    span_v = (tk[-1] - tk[0]) or 1

    def sy(v):
        return y1 + (tk[-1] - v) / span_v * (y0 - y1)

    n = len(run)
    span = (width - L - R) / n
    bw = min(span * 0.6, 56)
    p = [_grid_y(L, width - R, tk, sy)]
    for i, (lab, a, b, is_total) in enumerate(run):
        cx = L + span * i + span / 2
        if is_total:
            top, bot = sy(b), sy(0)
            col = TONE["navy"]
            delta = b
        else:
            top, bot = sy(max(a, b)), sy(min(a, b))
            col = TONE["green"] if b >= a else TONE["red"]
            delta = b - a
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"/>'
                 % (cx - bw / 2, top, bw, max(bot - top, 1.2), col))
        p.append(_txt(cx, top - 5, ("+" if delta > 0 and not is_total else "") + _n(delta),
                      9, INK, "middle", "bold"))
        p.append(_txt(cx, y0 + 14, lab, 8.8, MUTED, "middle"))
        if i < n - 1 and not run[i + 1][3]:
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1" '
                     'stroke-dasharray="3 3"/>' % (cx + bw / 2, sy(b), cx + span - bw / 2, sy(b), AXIS))
    p.append('<line x1="%s" y1="%.1f" x2="%s" y2="%.1f" stroke="%s" stroke-width="1.2"/>'
             % (L, sy(0), width - R, sy(0), AXIS))
    if ylabel:
        p.append(_txt(8, 10, ylabel, 9, MUTED))
    return _svg(width, height, "".join(p))


def radar(axes, series, size=300):
    """axes=[names], series=[(name,[0..100 per axis])]"""
    if not axes or not series:
        return ""
    cx = cy = size / 2
    r = size / 2 - 42
    n = len(axes)
    p = []
    for ring in (0.25, 0.5, 0.75, 1.0):
        pts = [(cx + r * ring * math.cos(-math.pi / 2 + 2 * math.pi * i / n),
                cy + r * ring * math.sin(-math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
        p.append('<polygon points="%s" fill="none" stroke="%s"/>'
                 % (" ".join("%.1f,%.1f" % (x, y) for x, y in pts), GRID))
    for i, ax in enumerate(axes):
        a = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        p.append('<line x1="%s" y1="%s" x2="%.1f" y2="%.1f" stroke="%s"/>' % (cx, cy, x, y, GRID))
        lx, ly = cx + (r + 18) * math.cos(a), cy + (r + 18) * math.sin(a)
        anchor = "middle" if abs(math.cos(a)) < 0.3 else ("start" if math.cos(a) > 0 else "end")
        p.append(_txt(lx, ly + 3, ax, 9, MUTED, anchor))
    for si, (name, vs) in enumerate(series):
        col = SERIES[si % len(SERIES)]
        pts = []
        for i in range(n):
            v = (float(vs[i]) if i < len(vs) else 0.0) / 100.0
            a = -math.pi / 2 + 2 * math.pi * i / n
            pts.append((cx + r * v * math.cos(a), cy + r * v * math.sin(a)))
        d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        p.append('<polygon points="%s" fill="%s" opacity="0.16" stroke="%s" stroke-width="2"/>' % (d, col, col))
    p.append(_legend([(s[0], SERIES[i % len(SERIES)]) for i, s in enumerate(series)], 8, size - 6))
    return _svg(size, size, "".join(p))
