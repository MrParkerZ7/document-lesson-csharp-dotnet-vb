#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brief_pdf.py — reusable renderer for the `brief` command family (PDF **format 01**).

Produces the color-sectioned, card-based, focus-by-topic briefing style
(see ../prompts/PROMPT_BRIEF_PDF_STANDARD.md). A generator only needs to
build a `blocks` list and call render_brief(); all styling lives here so every
brief/guide/explore/report looks consistent.

Pipeline: blocks -> styled HTML -> Edge headless --print-to-pdf.

NOTE ON THE FILENAME: this module is *imported by name* (`from brief_pdf import ...`)
by every generator script, so it must be a valid Python identifier — hence
underscores, unlike the sibling `pdf-engine-reference.py` which is loaded by path.

This is PDF **format 01 (`briefing-cards`)** in `../pdf-styles/` — a distinct block
renderer, NOT a CSS skin of the long-form engine. See `../pdf-styles/INDEX.md`
§ Formats vs skins.

Usage (from a target's 0-script/):
    import sys, pathlib
    sys.path.insert(0, r"D:\\Programing\\claude-prompt-root-master\\shared\\workflows")
    from brief_pdf import render_brief, pill, tag, link, PALETTE

    blocks = [
      {"type":"story","heading":"...","html":"...<b>bold</b>..."},
      {"type":"legend","label":"STATUS","chips":[pill("Ready","green"), pill("Blocked","red")]},
      {"type":"cards","band":{"title":"A · Section","note":"owner","tone":"teal"},
        "cards":[{"num":1,"title":"...","tags":[tag("App Owner","sky")],"pills":[pill("Ready","green")],
                  "what":"one-liner","lines":[("Why","..."),("How","...")]}]},
      {"type":"table","heading":"At a glance","cols":["#","Item","Status"],
        "rows":[["1","Foo", pill("Ready","green")]]},
      {"type":"callout","variant":"warn","heading":"Blocking","items":["a","b"]},
      {"type":"footer","html":"<b>Sequence:</b> ..."},
    ]
    render_brief(out_pdf, "Title", "subtitle line", blocks)

Block types: story · twocol · threecol · legend · cards · table · callout · footer ·
mermaid · kpi · chart · chartrow · image · imagerow · toc · html (raw).

    {"type":"toc","heading":"Contents","depth":2}   # two-pass; real page numbers, verified

A block may set "_keep_with_next": True to print in one unbreakable group with the START of the
block after it (a section opener that must not be stranded at a page foot away from its first
figure); when that block is a picture, its reading continues after the group and may break.

❗ ESCAPING IS NOT UNIFORM. `caption` (chart + mermaid) and every `heading` are
HTML-ESCAPED -- markup in them prints literally, so keep them PLAIN TEXT. The chart
`note`, and the `html` of story / callout / footer / box, are inserted RAW and do
take markup. Table cells are raw too (that is how pill()/link()/sparkline() work).

Sourced-image blocks (format 04 `illustrated-dossier`; build them with pdf_images.py so the
credit line and the source link come from the file's own licence record):
    {"type":"image","heading":"...","src":"file:///...|data:...","caption":"what is visible",
     "credit":"Author · CC BY-SA 4.0 · <a ...>source</a>","note":"the reading","plate":True}
    {"type":"imagerow","images":[{...},{...}]}   # two pictures side by side
`plate` gives the picture its own page. `credit` and `note` are RAW html (they carry links);
`heading`, `caption` and `alt` are escaped.

Analytics blocks (need chart_svg.py):
    {"type":"kpi","heading":"...","items":[{"label":"Range","value":"325 mi","sub":"EPA",
                                            "tone":"teal","delta":"-7%","spark":[3,5,4,6]}]}
    {"type":"chart","heading":"...","caption":"...","note":"reading of the data",
     "kind":"bar","args":{...}}          # or pass a ready SVG as "svg"
    {"type":"chartrow","charts":[{...},{...}]}   # two charts side by side
"""
import subprocess, pathlib, html as _H, shutil, glob, re, os, sys, unicodedata

try:                      # analytics primitives (formats 00 / 02). Optional:
    import chart_svg as _CS   # a brief with no chart blocks renders fine without it.
except Exception:             # noqa: BLE001
    _CS = None

# Optional: only needed for a TOC with resolved page numbers (the two-pass path).
# Without them a `toc` block still renders -- just without the page column.
try:
    from pypdf import PdfReader, PdfWriter
except Exception:             # noqa: BLE001
    PdfReader = PdfWriter = None
try:
    from reportlab.pdfgen import canvas as _rl_canvas
    from reportlab.lib.pagesizes import A4 as _RL_A4
except Exception:             # noqa: BLE001
    _rl_canvas = None

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def _find_mmdc():
    """Locate the mermaid-cli (mmdc): PATH, then the npx cache. Returns [node, cli.js] or None.
    Renders mermaid -> SVG using its bundled mermaid + local Puppeteer Chrome (no download / cert needed)."""
    exe = shutil.which("mmdc")
    if exe:
        return [exe]
    node = shutil.which("node") or r"C:\Program Files\nodejs\node.exe"
    pats = [os.path.expanduser(r"~\AppData\Local\npm-cache\_npx\*\node_modules\@mermaid-js\mermaid-cli\src\cli.js")]
    for pat in pats:
        hits = glob.glob(pat)
        if hits and pathlib.Path(node).exists():
            return [node, hits[0]]
    return None


# ---------------------------------------------------------------------------
# MERMAID ON A4 — constraints found by rendering, not by reading the docs.
# (Discovered while authoring the format-03 gallery sample, 2026-09-07.)
#
# 1. `classDef` works in flowchart, stateDiagram-v2 and classDiagram ONLY.
#    Putting classDef in a mindmap makes mmdc emit NOTHING -- a silent failure
#    that lands in the fallback code-block path below. For the other families
#    carry colour with a leading init directive instead:
#      %%{init: {"themeVariables": {...}}}%%
#    sequence -> actorBkg/noteBkgColor/activationBkgColor · ER -> mainBkg/nodeBorder
#    journey  -> fillType0..3 · gantt -> task/active/done/critBkgColor
#    mindmap  -> cScale0 (root), cScale1..N (branches, declaration order)
#    timeline -> cScale0..N (one per period)
# 2. JOURNEY CLIPS. A journey SVG carries an explicit height and renders ~1:1 in
#    the Edge print path; wider than ~1200 viewBox units and the right-hand
#    sections are silently cut off. Budget ~200 units/task at defaults, ~155 with
#    {"journey": {"width": 95, "taskMargin": 22, "leftMargin": 70}}.
# 3. GANTT defaults are illegible on wide bars: in-bar label colour is white and
#    section band 3 is bright yellow. Pin all four of taskTextColor /
#    taskTextDarkColor / taskTextLightColor / taskTextOutsideColor, plus
#    sectionBkgColor2.
# 4. Every classDef fill needs an explicit `color:#1f2937` (repo theme-safe rule)
#    or labels vanish against the viewer's theme.
# ---------------------------------------------------------------------------
def render_mermaid_svg(code, tmp_dir, idx=0):
    """Render one mermaid diagram to an inline SVG string (namespaced id). None on any failure -> caller falls back."""
    mmdc = _find_mmdc()
    if not mmdc:
        return None
    tmp_dir = pathlib.Path(tmp_dir)
    src = tmp_dir / f"_mmd_{idx}.mmd"
    out = tmp_dir / f"_mmd_{idx}.svg"
    src.write_text(code, encoding="utf-8")
    if out.exists():
        out.unlink()
    env = dict(os.environ, NODE_TLS_REJECT_UNAUTHORIZED="0")
    try:
        subprocess.run(mmdc + ["-i", str(src), "-o", str(out), "-b", "transparent"],
                       capture_output=True, timeout=150, env=env)
    except Exception:
        return None
    if not out.exists():
        return None
    svg = out.read_text(encoding="utf-8", errors="replace")
    svg = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg)          # drop xml decl for inline embedding
    svg = re.sub(r"<!DOCTYPE[^>]*>", "", svg, flags=re.I)
    svg = svg.replace("my-svg", f"mmd{idx}")                  # namespace the root id
    svg = re.sub(r'(<svg\b[^>]*?)\swidth="100%"', r"\1", svg, count=1)  # drop width=100% -> use viewBox
    return svg


# named (fg, bg) tones for pills/tags/section bands
PALETTE = {
    "green":  ("#065F46", "#D1FAE5"), "amber": ("#92400E", "#FEF3C7"),
    "red":    ("#991B1B", "#FEE2E2"), "slate": ("#334155", "#E2E8F0"),
    "sky":    ("#0369A1", "#E0F2FE"), "violet":("#6D28D9", "#EDE9FE"),
    "rose":   ("#BE185D", "#FCE7F3"), "teal":  ("#0F766E", "#CCFBF1"),
    "blue":   ("#1D4ED8", "#DBEAFE"), "indigo":("#4338CA", "#E0E7FF"),
    "navy":   ("#1A237E", "#E8EAF6"),
}
BAND = {"teal": "#0F766E", "blue": "#1D4ED8", "indigo": "#4338CA", "amber": "#B45309",
        "sky": "#0369A1", "violet": "#6D28D9", "rose": "#BE185D", "navy": "#1A237E", "slate": "#334155"}
CALLOUT = {  # variant -> (title_fg, border, bg)
    "warn":   ("#991B1B", "#DC2626", "#FEF2F2"),
    "action": ("#1E40AF", "#2563EB", "#EFF6FF"),
    "ok":     ("#065F46", "#10B981", "#ECFDF5"),
    "info":   ("#1A237E", "#1A237E", "#F1F5F9"),
    "summary": ("#3730A3", "#4F46E5", "#EEF2FF"),
}


def esc(s):
    return _H.escape(str(s))


def pill(text, tone="slate"):
    fg, bg = PALETTE.get(tone, PALETTE["slate"])
    return f'<span class="pill" style="color:{fg};background:{bg}">● {esc(text)}</span>'


def tag(text, tone="sky"):
    fg, bg = PALETTE.get(tone, PALETTE["sky"])
    return f'<span class="tag" style="color:{fg};background:{bg};border-color:{fg}">{esc(text)}</span>'


def link(text, url):
    """Real clickable hyperlink (portal, doc, job, mailbox). Use `mailto:` prefix in url for emails.
    Always use this instead of writing a bare URL as plain text."""
    return f'<a class="lnk" href="{esc(url)}">{esc(text)}</a>'


def _box(b):
    hh = f'<div class="bx-h">{esc(b["heading"])}</div>' if b.get("heading") else ""
    if b.get("items"):
        inner = "<ul>" + "".join(f"<li>{it}</li>" for it in b["items"]) + "</ul>"
    else:
        inner = b.get("html", "")
    top = f'border-top:3px solid {BAND.get(b.get("tone", "slate"), "#9CA3AF")};' if b.get("tone") else ""
    return f'<div class="box" style="{top}">{hh}{inner}</div>'


def _card(c):
    tags = "".join(c.get("tags", []))
    pills = "".join(c.get("pills", []))
    lines = "".join(
        f'<div class="row"><span class="lbl">{esc(l)}</span><span class="val">{v}</span></div>'
        for l, v in c.get("lines", []))
    num = f'<span class="num">{c["num"]}</span>' if c.get("num") is not None else ""
    what = f'<div class="what">{c["what"]}</div>' if c.get("what") else ""
    return (f'<div class="card"><div class="chead">{num}<span class="cname">{esc(c["title"])}</span>'
            f'{tags}{pills}</div>{what}{lines}</div>')


def _chart(b, bare=False):
    """One figure: heading + SVG + caption + interpretation note."""
    svg = b.get("svg")
    if not svg and b.get("kind") and _CS:
        fn = getattr(_CS, b["kind"], None)
        if fn:
            try:
                svg = fn(**b.get("args", {}))
            except Exception as e:                                  # noqa: BLE001
                svg = (f'<div class="mmd-fallback"><div class="mmd-warn">chart '
                       f'{esc(b["kind"])} failed: {esc(type(e).__name__)}</div></div>')
    if not svg:
        return ""
    hh = f'<div class="figh">{esc(b["heading"])}</div>' if b.get("heading") else ""
    cap = f'<div class="figc">{esc(b["caption"])}</div>' if b.get("caption") else ""
    note = f'<div class="fign">{b["note"]}</div>' if b.get("note") else ""
    return f'<div class="fig{" figbare" if bare else ""}">{hh}<div class="figbody">{svg}</div>{cap}{note}</div>'


def _image(b, bare=False):
    """One sourced picture: heading + <img> + caption + credit + reading.

    The src must already be local (a file:// URL or a data: URI) — Edge prints with no network, so
    a remote URL would silently produce an empty frame. pdf_images.py guarantees that, and builds
    the credit line the licence requires."""
    src = b.get("src")
    if not src:
        return ""
    hh = f'<div class="figh">{esc(b["heading"])}</div>' if b.get("heading") else ""
    cap = f'<div class="figc">{esc(b["caption"])}</div>' if b.get("caption") else ""
    cr = f'<div class="imgcr">{b["credit"]}</div>' if b.get("credit") else ""
    note = f'<div class="fign">{b["note"]}</div>' if b.get("note") else ""
    cls = "img" + (" imgplate" if b.get("plate") and not bare else "") + (" imgbare" if bare else "")
    # A low-resolution figure blown up to the column width prints as a grey smear; `max_w_in`
    # (set by pdf_images.image_block from the file's own pixel width) stops the upscale. It is
    # capped at 100% of whatever box the picture sits in: inside an `imagerow` the column is half
    # the page, and an inline width in inches wider than that column overflows the sheet — which
    # makes Chromium shrink the WHOLE document to fit, silently, at print time.
    caps = []
    if b.get("max_w_in"):
        caps.append("max-width:min(100%%,%.2fin)" % float(b["max_w_in"]))
    if b.get("max_h_in"):
        # A tall picture that cannot fit the rest of the page jumps to the next one and leaves a
        # hole behind it; capping its height lets it travel with the prose it belongs to.
        caps.append("max-height:%.2fin" % float(b["max_h_in"]))
    style = ' style="%s"' % ";".join(caps) if caps else ""
    # `.imgk` (heading, picture, caption, credit) never splits; the reading after it may run on to
    # the next page. A block unbreakable down to the end of a long reading is 6-8 in tall, and
    # wherever it did not fit it jumped whole and left the page before it part-empty.
    return (f'<div class="{cls}"><div class="imgk">{hh}<div class="imgbody">'
            f'<img src="{esc(src)}" alt="{esc(b.get("alt", ""))}"{style}></div>{cap}{cr}</div>{note}</div>')


def _kpi_row(b):
    """A row of KPI tiles — the headline numbers a reader should leave with."""
    cells = []
    for k in b.get("items", []):
        fg, _bg = PALETTE.get(k.get("tone", "navy"), PALETTE["navy"])
        delta = ""
        if k.get("delta") is not None:
            d = k["delta"]
            up = str(d).lstrip().startswith("+") or (isinstance(d, (int, float)) and d > 0)
            delta = (f'<span class="kd" style="color:{"#059669" if up else "#DC2626"}">'
                     f'{"▲" if up else "▼"} {esc(d)}</span>')
        spark = _CS.sparkline(k["spark"], tone=k.get("sparktone", "blue")) if (k.get("spark") and _CS) else ""
        sub = f'<div class="ks">{esc(k["sub"])}</div>' if k.get("sub") else ""
        cells.append(f'<div class="kpi" style="border-top:3px solid {fg}">'
                     f'<div class="kl">{esc(k.get("label", ""))}</div>'
                     f'<div class="kv" style="color:{fg}">{esc(k.get("value", ""))}{delta}</div>'
                     f'{sub}{f"<div class='kspark'>{spark}</div>" if spark else ""}</div>')
    if not cells:
        return ""
    hh = f'<h2>{esc(b["heading"])}</h2>' if b.get("heading") else ""
    return (hh + f'<div class="kpis" style="grid-template-columns:repeat({len(cells)},1fr)">'
            + "".join(cells) + "</div>")


def _block(b):
    t = b["type"]
    if t == "html":
        return b["html"]
    if t == "story":
        hh = f'<div class="ct">{esc(b["heading"])}</div>' if b.get("heading") else ""
        return f'<div class="story">{hh}{b.get("html", "")}</div>'
    if t in ("twocol", "threecol"):
        cls = "two" if t == "twocol" else "three"
        return f'<div class="{cls}">' + "".join(_box(x) for x in b["boxes"]) + "</div>"
    if t == "legend":
        lab = f'<b class="lgl">{esc(b["label"])}:</b>' if b.get("label") else ""
        return f'<div class="legend">{lab}{"".join(b["chips"])}</div>'
    if t == "cards":
        band = b.get("band")
        bh = ""
        if band:
            color = BAND.get(band.get("tone", "navy"), "#1A237E")
            note = f'<span class="bnote">{esc(band.get("note", ""))}</span>' if band.get("note") else ""
            bh = (f'<div class="band" style="background:{color}">'
                  f'<span class="btitle">{esc(band["title"])}</span>{note}</div>')
        grid = '<div class="grid">' + "".join(_card(c) for c in b["cards"]) + "</div>"
        return f'<div class="section">{bh}{grid}</div>'
    if t == "table":
        hh = f'<h2>{esc(b["heading"])}</h2>' if b.get("heading") else ""
        # <thead> is what makes Chromium repeat the column header on every page the table spans;
        # a bare header <tr> printed once, and the rows on the next page had no column labels.
        head = "<thead><tr>" + "".join(f"<th>{esc(c)}</th>" for c in b["cols"]) + "</tr></thead>"
        rows = ("<tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                                    for r in b["rows"]) + "</tbody>")
        return f'{hh}<table class="sum">{head}{rows}</table>'
    if t == "callout":
        fg, bd, bg = CALLOUT.get(b.get("variant", "info"), CALLOUT["info"])
        hh = f'<div class="ct" style="color:{fg}">{esc(b["heading"])}</div>' if b.get("heading") else ""
        if b.get("items"):
            body = "<ol>" + "".join(f"<li>{it}</li>" for it in b["items"]) + "</ol>"
        else:
            body = b.get("html", "")
        return (f'<div class="callout" style="background:{bg};border-color:#e5b4b4;'
                f'border-left:5px solid {bd}">{hh}{body}</div>')
    if t == "mermaid":
        cap = f'<div class="mmd-cap">{esc(b["caption"])}</div>' if b.get("caption") else ""
        hh = f'<h2>{esc(b["heading"])}</h2>' if b.get("heading") else ""
        wrap = "mmd-inline" if b.get("inline") else "mmd-page"
        svg = b.get("_svg")
        if svg:
            inner = f'{hh}<div class="mmd">{svg}</div>{cap}'
        else:
            inner = (f'{hh}<div class="mmd-fallback"><div class="mmd-warn">⚠ diagram not rendered '
                     f'(mermaid engine unavailable) — source:</div>'
                     f'<pre>{esc(b.get("code", ""))}</pre></div>{cap}')
        return f'<div class="{wrap}">{inner}</div>'
    if t == "kpi":
        return _kpi_row(b)
    if t == "chart":
        return _chart(b)
    if t == "chartrow":
        return '<div class="crow">' + "".join(_chart(c, bare=True) for c in b.get("charts", [])) + "</div>"
    if t == "image":
        return _image(b)
    if t == "imagerow":
        return '<div class="irow">' + "".join(_image(c, bare=True) for c in b.get("images", [])) + "</div>"
    if t == "footer":
        return f'<div class="foot">{b.get("html", "")}</div>'
    return ""


CSS = """
@page { size:A4; margin:7mm 7mm 9mm 7mm; }
* { box-sizing:border-box; }
body { font-family:'Segoe UI',Calibri,Arial,sans-serif; color:#1f2937; font-size:9.5pt; line-height:1.38; margin:0; }
.h1 { background:#1A237E; color:#fff; padding:12px 16px; border-radius:7px 7px 0 0; }
.h1 .t { font-size:16pt; font-weight:700; } .h1 .s { font-size:9pt; opacity:.9; margin-top:2px; }
.sub { background:#E8EAF6; color:#1A237E; font-size:8.5pt; padding:6px 16px; border-radius:0 0 7px 7px; margin-bottom:10px; }
h2 { font-size:11pt; color:#1A237E; margin:15px 0 6px; border-bottom:2px solid #C5CAE9; padding-bottom:3px; }
.mmd-page { page-break-before:always; page-break-after:always; break-before:page; break-after:page; }
.mmd-page .mmd svg { max-height:9in; }
.mmd-inline { margin:8px 0; page-break-inside:avoid; break-inside:avoid; }
.mmd { text-align:center; margin:8px 0; page-break-inside:avoid; }
.mmd svg { max-width:100%; max-height:8.4in; height:auto; width:auto; }
.mmd-cap { font-size:8pt; color:#6b7280; text-align:center; margin:2px 0 8px; }
.mmd-fallback { border:1px dashed #9CA3AF; border-radius:6px; padding:8px 10px; background:#F9FAFB; margin:8px 0; }
.mmd-fallback .mmd-warn { font-size:8pt; color:#92400E; margin-bottom:4px; }
.mmd-fallback pre { font-size:7.6pt; white-space:pre-wrap; margin:0; }
.pill { font-size:7.8pt; font-weight:700; padding:2px 8px; border-radius:20px; white-space:nowrap; }
.tag { font-size:7.4pt; font-weight:700; padding:1px 7px; border-radius:4px; border:1px solid; white-space:nowrap; margin-right:3px; }
a.lnk, a { color:#1D4ED8; text-decoration:underline; word-break:break-all; }
.legend { margin:8px 0 4px; } .legend .lgl { font-size:8pt; color:#6B7280; margin-right:4px; }
.legend .pill,.legend .tag { margin-right:4px; }
.story { background:#F1F5F9; border:1px solid #CBD5E1; border-left:5px solid #1A237E; border-radius:6px; padding:9px 13px; margin:10px 0; }
.story .ct { color:#1A237E; font-weight:700; font-size:10.5pt; margin-bottom:3px; } .story b { color:#0D1440; } .story p { margin:3px 0; }
.two { display:grid; grid-template-columns:1fr 1fr; gap:9px; margin:6px 0; }
.three { display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin:6px 0; }
.box { border:1px solid #E5E7EB; border-radius:6px; padding:8px 11px; background:#fff; }
.box .bx-h { font-weight:700; font-size:9.3pt; margin-bottom:4px; color:#111827; }
.box ul { margin:0; padding-left:16px; } .box li { margin:2px 0; font-size:8.7pt; } .box p { margin:2px 0; font-size:8.7pt; }
.section { margin:12px 0; page-break-inside:avoid; }
.band { color:#fff; padding:6px 12px; border-radius:6px 6px 0 0; display:flex; justify-content:space-between; align-items:baseline; }
.band .btitle { font-weight:700; font-size:10.5pt; } .band .bnote { font-size:8pt; opacity:.92; }
.grid { display:grid; grid-template-columns:1fr; gap:7px; padding:8px; background:#F9FAFB; border:1px solid #E5E7EB; border-top:none; border-radius:0 0 6px 6px; }
.card { background:#fff; border:1px solid #E5E7EB; border-radius:6px; padding:8px 10px; page-break-inside:avoid; }
.chead { display:flex; align-items:center; gap:6px; margin-bottom:4px; flex-wrap:wrap; }
.num { background:#1A237E; color:#fff; font-size:8pt; font-weight:700; width:18px; height:18px; border-radius:50%; text-align:center; line-height:18px; flex:none; }
.cname { font-weight:700; font-size:9.7pt; color:#111827; }
.what { color:#374151; margin-bottom:5px; }
.row { display:flex; gap:6px; margin:2px 0; }
.lbl { color:#6B7280; font-size:7.6pt; font-weight:700; text-transform:uppercase; letter-spacing:.3px; width:70px; flex:none; padding-top:1px; }
.val { color:#374151; font-size:8.6pt; flex:1; }
table.sum { border-collapse:collapse; width:100%; margin:4px 0 6px; }
table.sum th { background:#37474F; color:#fff; text-align:left; padding:4px 8px; font-size:8pt; }
table.sum td { border:1px solid #E5E7EB; padding:4px 8px; font-size:8.4pt; vertical-align:middle; }
table.sum tbody tr:nth-child(odd) td { background:#F8FAFC; }
table.sum thead { display:table-header-group; }
table.sum tr { page-break-inside:avoid; break-inside:avoid; }
.callout { border-radius:6px; padding:9px 13px; margin:10px 0; }
.callout .ct { font-weight:700; font-size:10pt; margin-bottom:3px; }
.callout ol,.callout ul { margin:4px 0 0; padding-left:18px; } .callout li { margin:2px 0; }
.toc { margin:10px 0 14px; padding:10px 14px; background:#F8FAFC; border:1px solid #E2E8F0; border-left:5px solid #1A237E; border-radius:6px; page-break-inside:avoid; }
.toc .tocT { font-weight:700; font-size:11.5pt; color:#1A237E; margin-bottom:6px; }
.toc .trow { display:flex; align-items:baseline; }
.toc .ttxt { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:82%; }
.toc a { color:#1f2937; text-decoration:none; }
.toc .tdots { flex:1; border-bottom:1.5px dotted #9CA3AF; margin:0 6px; height:.7em; }
.toc .tpg { color:#4B5563; font-size:8.6pt; min-width:1.6em; text-align:right; font-weight:700; }
.toc .tl1 { font-weight:700; font-size:9.5pt; margin-top:4px; color:#111827; }
.toc .tl2 { margin-left:1.6em; font-size:8.8pt; }
.toc .tl2 a { color:#374151; }
.toc .tocN { font-size:8pt; color:#6B7280; margin-top:6px; }
.pgm { display:block; height:1px; margin:0; padding:0; font-size:1px; line-height:1px; overflow:hidden; white-space:nowrap; color:transparent; }
.pgm.pgma { position:absolute; left:0; top:0; }
.toc .tpg.ghost { color:transparent; }
.kpis { display:grid; gap:8px; margin:8px 0; }
.kpi { background:#fff; border:1px solid #E5E7EB; border-radius:7px; padding:8px 10px; page-break-inside:avoid; }
.kpi .kl { font-size:7.6pt; color:#6B7280; font-weight:700; text-transform:uppercase; letter-spacing:.4px; }
.kpi .kv { font-size:17pt; font-weight:700; line-height:1.12; margin:2px 0; }
.kpi .kd { font-size:8pt; font-weight:700; margin-left:5px; }
.kpi .ks { font-size:8pt; color:#6B7280; }
.kpi .kspark { margin-top:3px; }
.fig { margin:10px 0; page-break-inside:avoid; break-inside:avoid; }
.fig .figh { font-weight:700; font-size:10pt; color:#1A237E; margin-bottom:4px; border-bottom:2px solid #C5CAE9; padding-bottom:2px; }
.fig .figbody { text-align:center; }
.fig .figc { font-size:8pt; color:#6b7280; text-align:center; margin-top:3px; }
.fig .fign { font-size:8.4pt; color:#374151; margin-top:5px; background:#F8FAFC; border-left:3px solid #C5CAE9; padding:5px 9px; border-radius:0 4px 4px 0; }
.crow { display:grid; grid-template-columns:1fr 1fr; gap:11px; margin:10px 0; page-break-inside:avoid; }
.crow .fig { margin:0; }
.img { margin:10px 0; }
.img .imgk { page-break-inside:avoid; break-inside:avoid; }
.img.imgcont { margin-top:-10px; }
.img .figh { font-weight:700; font-size:10pt; color:#1A237E; margin-bottom:4px; border-bottom:2px solid #C5CAE9; padding-bottom:2px; }
.img .imgbody { text-align:center; }
.img .imgbody img { max-width:100%; max-height:4.9in; width:auto; height:auto; border:1px solid #E5E7EB; border-radius:5px; }
.img .figc { font-size:8pt; color:#6b7280; text-align:left; margin-top:4px; }
.img .imgcr { font-size:7.2pt; color:#9CA3AF; text-align:left; margin-top:2px; }
.img .imgcr a { color:#6B7280; text-decoration:none; border-bottom:1px dotted #9CA3AF; word-break:normal; }
.img .fign { font-size:8.4pt; color:#374151; margin-top:6px; background:#F8FAFC; border-left:3px solid #C5CAE9; padding:5px 9px; border-radius:0 4px 4px 0; orphans:3; widows:3; page-break-before:avoid; break-before:avoid; }
.imgplate { page-break-before:always; page-break-after:always; break-before:page; break-after:page; }
.imgplate .imgbody img { max-height:8.1in; }
.irow { display:grid; grid-template-columns:1fr 1fr; gap:11px; margin:10px 0; page-break-inside:avoid; break-inside:avoid; }
.irow .img { margin:0; }
.irow .img .imgbody img { max-height:3.1in; }
svg.cw { display:block; margin:0 auto; }
svg.spark { vertical-align:middle; }
.foot { margin-top:12px; background:#ECFDF5; border:1px solid #A7F3D0; border-radius:6px; padding:9px 13px; font-size:9pt; page-break-inside:avoid; break-inside:avoid; } .foot b { color:#065F46; }
"""


# ---------------------------------------------------------------------------
# Table of contents (two-pass, page numbers resolved from the rendered PDF, then verified).
#
# Pass 1 renders an invisible 1px marker (@@B<i>@@) INSIDE every TOC-listed block --
# pinned to the heading line of a story or callout, otherwise in the block's first
# container (see _with_marker) -- and pypdf reads which page each marker landed on. The marker has to travel with its block: placed in front of it, as it
# once was, it stayed behind whenever an unbreakable block (figure, picture row,
# card section, kept table) moved to the next page, and the Contents named the
# page before. Pass 1 also prints the Contents with transparent placeholder page
# numbers, so its rows are exactly as tall as pass 2's. Pass 2 re-renders with the
# real numbers and EMPTY markers of the same size -- identical geometry, and no
# stray tokens in the delivered PDF. Finally the delivered PDF is re-read and each
# entry is checked against the page its heading actually prints on
# (_toc_mismatches); render_brief raises TocMismatch on any disagreement, because
# visual QA does not catch a Contents number that is one page off.
# ---------------------------------------------------------------------------
_TOC_TYPES = ("story", "cards", "table", "kpi", "chart", "chartrow", "mermaid", "image", "imagerow")


def _toc_label(b):
    """The heading a block contributes to the TOC (cards carry theirs on the band)."""
    if b.get("type") == "cards":
        return ((b.get("band") or {}).get("title") or "").strip() or None
    h = b.get("heading")
    return h.strip() if isinstance(h, str) and h.strip() else None


def _toc_collect(blocks, depth=2):
    """-> [(level, block_index, label)].

    Level comes from the heading's own numbering: "4.2 - x" is level 2, "4 - x" is
    level 1. A block sets "toc": False to stay out, or "toc": 1|2 to force a level
    (which also opts in a type that is not structural by default, e.g. a callout).
    """
    out = []
    for i, b in enumerate(blocks):
        t = b.get("type")
        if t == "toc":
            continue
        opt = b.get("toc")
        if opt is False:
            continue
        if t in ("chartrow", "imagerow"):         # one entry per inner figure, same anchor
            inner = b.get("charts") if t == "chartrow" else b.get("images")
            labels = [c.get("heading") for c in (inner or []) if c.get("heading")]
        else:
            lab = _toc_label(b)
            labels = [lab] if lab else []
        if not labels:
            continue
        if opt is None and t not in _TOC_TYPES:   # callouts/footers are commentary, not structure
            continue
        for lab in labels:
            lvl = opt if isinstance(opt, int) else (2 if re.match(r"^\s*\d+\.\d+", lab) else 1)
            if lvl <= depth:
                out.append((lvl, i, lab.strip()))
    return out


def _toc_html(b, entries, pages=None, ghost=False):
    """The Contents block. `pages` fills the page column.

    `ghost` (pass 1) prints a transparent placeholder number and the dot leader in every row. The
    rows then have exactly the geometry pass 2 gives them; without the column, pass-1 rows were a
    hair shorter, and over a long Contents that let a block near a page foot fit in pass 1 and
    move to the next page in pass 2 — after its number had been measured."""
    if ghost:
        pages = {i: "88" for _l, i, _x in entries}
    rows = []
    for lvl, i, lab in entries:
        pg = ('<span class="tpg%s">%s</span>' % (" ghost" if ghost else "", pages.get(i, ""))
              if pages else "")
        dots = '<span class="tdots"></span>' if pages else ""
        rows.append('<div class="trow tl%d"><span class="ttxt"><a href="#tb%d">%s</a></span>%s%s</div>'
                    % (lvl, i, esc(lab), dots, pg))
    note = '<div class="tocN">%s</div>' % b["note"] if b.get("note") else ""
    return ('<div class="toc"><div class="tocT">%s</div>%s%s</div>'
            % (esc(b.get("heading", "Contents")), "".join(rows), note))


# A block's own first container. Only tags that may legally hold a <div>: a marker pushed into a
# <table> or <p> would be hoisted back out, in front of the block, by the HTML parser.
_MARK_HOST = re.compile(r'<(?:div|section|article|figure|header|h[1-6])\b[^>]*>')
_MARK_GRID = re.compile(r'<div\s+class="(?:crow|irow|two|three|kpis)\b')
_AVOID = "break-inside:avoid;page-break-inside:avoid;"
# A story / callout heading line, or a picture's unbreakable group, that is the host's FIRST child —
# see _with_marker.
_MARK_HEAD = re.compile(r'<div\s+class="(?:ct|imgk)"[^>]*>')


def _with_marker(i, h, token):
    """Put block i's page marker (and its anchor id) INSIDE the block's first container.

    In front of the block, the marker was left behind whenever the block could not fit and moved
    on — figures, picture rows, card sections and kept tables are all break-inside:avoid — so the
    Contents named the page BEFORE the one the block printed on (10 of 33 entries in the
    2026-09-13 format-04 sample). A sibling marker with break-after:avoid does not help: Chromium
    ignores it before an unbreakable block, and a plate's forced page break still lands after it.
    Inside the container, whatever moves the block moves the marker.
      * a grid wrapper (.crow/.irow/.two/.three/.kpis) gets it one level deeper, in its first
        cell: as a direct grid child the marker would take a grid cell of its own;
      * the host is made break-inside:avoid, so it cannot fragment between the 1px marker line and
        its first line of content (marker on one page, heading on the next) — EXCEPT a story or
        callout, whose first child is its `.ct` heading line, and a picture, whose first child is
        its unbreakable `.imgk` group (heading, picture, caption, credit): there the marker is
        pinned onto that child (position:absolute, no space taken) and the box is left breakable,
        because an unbreakable long story, or a picture with a long reading, jumps whole to the next
        page and leaves the page before it part-empty;
      * the id rides on the marker, so a Contents link lands exactly where the block starts.
    A block that opens with anything else (raw html starting with a <table>, a <p>, bare text)
    gets the marker in front of it — right unless that block moves, and render_brief's check
    raises TocMismatch if it does."""
    mk = '<div class="pgm" id="tb%d">%s</div>' % (i, token)
    lead = len(h) - len(h.lstrip())
    m = _MARK_HOST.match(h, lead)
    if m and _MARK_GRID.match(h, lead):
        m = _MARK_HOST.search(h, m.end()) or m          # step into the first grid cell
    if not m:
        return mk + h
    hm = None if _MARK_GRID.match(h, lead) else _MARK_HEAD.match(h, m.end())
    if hm:
        # The box opens with its heading line: pin the marker to that line. Absolutely positioned,
        # it takes no space in either pass and prints on the heading's page, and the box stays free
        # to break — break-inside:avoid on a long story moved the whole story to the next page and
        # left ~3 in of white under the Contents (format-04 sample, 2026-09-13).
        head = _with_style(h[hm.start():hm.end()], "position:relative;")
        return (h[:hm.start()] + head + '<span class="pgm pgma" id="tb%d">%s</span>' % (i, token)
                + h[hm.end():])
    return h[:m.start()] + _with_style(h[m.start():m.end()], _AVOID) + mk + h[m.end():]


def _with_style(tag, css):
    """An opening tag with `css` prepended to its style attribute (one is added if absent)."""
    sm = re.search(r'\sstyle\s*=\s*["\']', tag)
    return tag[:sm.end()] + css + tag[sm.end():] if sm else tag[:-1] + ' style="%s">' % css


def _body_html(blocks, entries, pages=None, pass1=False):
    """Render every block: TOC anchors + page markers, and `_keep_with_next` groups.

    `pass1` is the measuring pass: markers carry their @@B<i>@@ token and the Contents prints ghost
    page numbers. Every other render emits the same 1px markers EMPTY — the same geometry, and the
    delivered PDF holds no token for copy-paste, search or a screen reader to trip over."""
    anchored = {i for _, i, _ in entries}

    def one(i):
        b = blocks[i]
        if b.get("type") == "toc":
            return _toc_html(b, entries, pages, ghost=pass1)
        h = _block(b)
        if i in anchored:
            h = _with_marker(i, h, ("@@B%d@@" % i) if pass1 else "")
        return h

    parts, i = [], 0
    while i < len(blocks):
        j = i                                      # a run of flagged blocks + the block they lead into
        while blocks[j].get("_keep_with_next") and j + 1 < len(blocks):
            j += 1
        if j == i:
            parts.append(one(i))
        else:
            head, tail = [one(k) for k in range(i, j + 1)], ""
            # The group keeps a lead-in with the START of what it leads into. For a picture that is
            # its heading, picture, caption and credit; its reading continues after the group in a
            # box of its own. Holding the whole reading too made a ~6.5 in unbreakable group that
            # jumped whole and left the space before it empty (AWS 04, 2026-09-13).
            last = blocks[j]
            if last.get("type") == "image" and not last.get("plate"):
                cut = head[-1].rfind('<div class="fign">')
                if cut > 0 and head[-1].endswith("</div>"):
                    head[-1], tail = (head[-1][:cut] + "</div>",
                                      '<div class="img imgcont">' + head[-1][cut:])
            parts.append('<div style="page-break-inside:avoid;break-inside:avoid">%s</div>%s'
                         % ("".join(head), tail))
        i = j + 1
    return "".join(parts)


def _norm(t):
    return re.sub(r"\s+", "", t or "")


class TocMismatch(RuntimeError):
    """A Contents entry names a page its heading does not print on (raised by render_brief).

    `.wrong` lists every bad entry as {label, listed, found, link}: the page the Contents gives, the
    pages the heading text was found on, and the page the entry's link lands on. `.pdf` is the
    delivered file, already written, kept so the fault can be inspected."""

    def __init__(self, pdf, wrong, total):
        self.pdf, self.wrong, self.total = pdf, wrong, total
        rows = ["  %r lists p%s; heading prints on %s; link lands on %s" % (
            w["label"], w["listed"] if w["listed"] is not None else "?",
            ", ".join("p%d" % n for n in w["found"]) or "no page",
            "p%d" % w["link"] if w["link"] is not None else "-") for w in wrong]
        super().__init__("brief_pdf: %d of %d Contents entr%s wrong in %s:\n%s"
                         % (len(wrong), total, "y is" if total == 1 else "ies are", pdf,
                            "\n".join(rows)))


def _text_key(s):
    """Letters and digits only, NFKC- and case-folded: what any PDF text layer preserves.

    Symbols go BEFORE folding: a leading ⚠ / ⓘ / 🔍 may come from a fallback font whose text layer
    maps it differently or not at all, and NFKC would turn ⓘ into "i". Whitespace goes too, so a
    heading that wraps onto a second line still matches."""
    s = "".join(ch for ch in (s or "") if ch.isalnum())
    return "".join(ch for ch in unicodedata.normalize("NFKC", s).casefold() if ch.isalnum())


def _page_keys_outside_links(pdf):
    """-> ([text key per page], {anchor name: 1-based page}) read from a delivered PDF.

    Text inside an internal link is left out — every Contents row is one, and the Contents repeats
    each heading, so without this an entry listed on the Contents' own page would always "find"
    its heading there. Uses PyMuPDF's word boxes when it is installed, pypdf's text positions
    otherwise. A link rect is padded by 3pt: a row's text origin can sit a fraction outside it."""
    try:
        import fitz
    except Exception:                                  # noqa: BLE001
        fitz = None
    pad = 3.0
    inside = lambda x, y, rects: any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in rects)
    keys, dests = [], {}
    if fitz is not None:
        doc = fitz.open(str(pdf))
        try:
            for page in doc:
                rects = [(l["from"].x0 - pad, l["from"].y0 - pad, l["from"].x1 + pad, l["from"].y1 + pad)
                         for l in page.get_links() if l.get("kind") in (fitz.LINK_GOTO, fitz.LINK_NAMED)]
                words = [w[4] for w in page.get_text("words", sort=False)
                         if not inside((w[0] + w[2]) / 2, (w[1] + w[3]) / 2, rects)]
                keys.append(_text_key("".join(words)))
            try:
                for name, d in (doc.resolve_names() or {}).items():
                    if isinstance(d, dict) and isinstance(d.get("page"), int) and d["page"] >= 0:
                        dests[str(name)] = d["page"] + 1
            except Exception:                          # noqa: BLE001 — old PyMuPDF: no link check
                pass
        finally:
            doc.close()
        return keys, dests
    reader = PdfReader(str(pdf))
    for page in reader.pages:
        rects = []
        for a in page.get("/Annots") or []:
            try:
                a = a.get_object()
                act = a.get("/A") or {}
                if a.get("/Subtype") != "/Link" or (a.get("/Dest") is None and act.get("/S") != "/GoTo"):
                    continue
                x0, y0, x1, y1 = [float(v) for v in a["/Rect"]]
                rects.append((min(x0, x1) - pad, min(y0, y1) - pad, max(x0, x1) + pad, max(y0, y1) + pad))
            except Exception:                          # noqa: BLE001
                continue
        chunks = []

        def visit(text, cm, tm, _font, _size, rects=rects, chunks=chunks):
            if text and text.strip():
                x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
                y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
                if not inside(x, y, rects):
                    chunks.append(text)
        page.extract_text(visitor_text=visit)
        keys.append(_text_key("".join(chunks)))
    try:
        for name, d in reader.named_destinations.items():
            pn = reader.get_destination_page_number(d)
            if pn is not None and pn >= 0:
                dests[str(name).lstrip("/")] = pn + 1
    except Exception:                                  # noqa: BLE001
        pass
    return keys, dests


def _toc_mismatches(pdf, entries, pages):
    """Every Contents entry of a delivered PDF whose page is not where its heading prints.

    An entry is wrong when its heading text is not on the page it lists (outside the Contents
    rows), when it has no page at all, or when its link lands on another page. The text test
    cannot see an ECHO — the same heading quoted on the listed page by, say, an index table —
    but the link test can: the anchor sits inside the block itself."""
    keys, dests = _page_keys_outside_links(pdf)
    wrong = []
    for _lvl, i, lab in entries:
        k, listed, link = _text_key(lab), pages.get(i), dests.get("tb%d" % i)
        found = [n for n, t in enumerate(keys, start=1) if k and k in t]
        bad = (listed is None or (k and listed not in found)
               or (link is not None and link != listed))
        if bad:
            wrong.append({"label": lab, "listed": listed, "found": found, "link": link})
    return wrong


def render_brief(out_pdf, title, subtitle, blocks, tmp_dir=None, verify_toc=True):
    """Render blocks to a PDF. Returns the output Path. Raises if Edge produced nothing.

    A {"type":"toc"} block triggers a TWO-PASS render so its page numbers are real: pass 1 measures
    where each listed block lands, pass 2 prints the numbers. With `verify_toc` (the default) the
    delivered PDF is then checked entry by entry against the page each heading actually prints on,
    and any disagreement raises TocMismatch listing every wrong entry. Degrades to a single pass
    (TOC without page numbers, so nothing to verify) when pypdf is unavailable or the page read
    fails — said on stderr, never silently.
    """
    out_pdf = pathlib.Path(out_pdf).resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = (pathlib.Path(tmp_dir) if tmp_dir else (out_pdf.parent.parent / "scratch")).resolve()
    tmp_dir.mkdir(parents=True, exist_ok=True)
    head = ('<div class="h1"><div class="t">%s</div><div class="s">%s</div></div>'
            % (esc(title), esc(subtitle)))
    # pre-render mermaid once — reused by both passes so pagination cannot drift
    for i, b in enumerate(blocks):
        if b.get("type") == "mermaid" and "_svg" not in b:
            b["_svg"] = render_mermaid_svg(b.get("code", ""), tmp_dir, i)

    tocb = next((b for b in blocks if b.get("type") == "toc"), None)
    entries = _toc_collect(blocks, tocb.get("depth", 2)) if tocb else []

    def emit(pages=None, pass1=False):
        doc = ("<!DOCTYPE html><html><head><meta charset='utf-8'><style>%s</style></head>"
               "<body>%s%s</body></html>" % (CSS, head, _body_html(blocks, entries, pages, pass1)))
        tmp = tmp_dir / (out_pdf.stem + ".render.html")
        tmp.write_text(doc, encoding="utf-8")
        _print_pdf(tmp, out_pdf, tmp_dir)
        if not out_pdf.exists():
            raise SystemExit("brief_pdf: Edge produced no PDF")

    if not entries or PdfReader is None:
        emit()                                    # single pass: nothing to number
        return out_pdf

    emit(pass1=True)                              # pass 1 — measure
    pages, why = {}, "no page marker was found in the text layer"
    try:
        texts = [_norm(pg.extract_text() or "") for pg in PdfReader(str(out_pdf)).pages]
        for _lvl, i, _lab in entries:
            needle = "@@B%d@@" % i
            for pno, txt in enumerate(texts, start=1):
                if needle in txt:
                    pages[i] = pno
                    break
    except Exception as e:                        # noqa: BLE001 — degrade, never ship pass 1
        pages, why = {}, "%s: %s" % (type(e).__name__, e)
    if not pages:
        print("brief_pdf: Contents printed WITHOUT page numbers (%s)" % why, file=sys.stderr)
    emit(pages or None)                           # pass 2 — same geometry, numbers filled, no tokens
    if not pages:
        return out_pdf
    if tocb.get("page_numbers", True) and _rl_canvas is not None:
        _stamp_page_numbers(out_pdf)
    if verify_toc:
        wrong = _toc_mismatches(out_pdf, entries, pages)
        if wrong:
            raise TocMismatch(out_pdf, wrong, len(entries))
    return out_pdf


def _print_pdf(html_path, out_pdf, tmp_dir):
    """Edge headless -> PDF, with the legacy-flag fallback."""
    if out_pdf.exists():
        try:
            out_pdf.unlink()
        except OSError:
            pass
    url = "file:///" + str(html_path).replace("\\", "/")
    prof = tmp_dir / "edge-profile"
    try:
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-first-run",
                        "--no-pdf-header-footer", "--user-data-dir=%s" % prof,
                        "--print-to-pdf=%s" % out_pdf, url], capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        pass
    if not out_pdf.exists():
        try:
            subprocess.run([EDGE, "--headless", "--disable-gpu", "--user-data-dir=%s" % prof,
                            "--print-to-pdf-no-header", "--print-to-pdf=%s" % out_pdf, url],
                           capture_output=True, timeout=120)
        except subprocess.TimeoutExpired:
            pass


def _named_dest_count(reader):
    try:
        return len(reader.named_destinations)
    except Exception:                              # noqa: BLE001
        return 0


def _stamp_page_numbers(pdf_path):
    """Bottom-centre `n / N` so the printed paper matches the TOC.

    The writer is CLONED from the reader. A fresh PdfWriter() + add_page() copies the pages but not
    the document catalog, which silently dropped the named destinations every Contents link points
    at (no Contents link worked) and the tag tree (/StructTreeRoot, /MarkInfo, /Lang). Losing
    destinations again raises instead of shipping dead links."""
    import io as _io
    reader = PdfReader(str(pdf_path))
    n = len(reader.pages)
    dests_before = _named_dest_count(reader)
    buf = _io.BytesIO()
    c = _rl_canvas.Canvas(buf, pagesize=_RL_A4)
    for i in range(n):
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.45, 0.45, 0.45)
        c.drawCentredString(_RL_A4[0] / 2, 12, "%d / %d" % (i + 1, n))
        c.showPage()
    c.save()
    buf.seek(0)
    overlay = PdfReader(buf)
    writer = PdfWriter(clone_from=reader)
    for i, page in enumerate(writer.pages):
        try:
            page.merge_page(overlay.pages[i])
        except Exception:                          # noqa: BLE001
            pass
    with open(pdf_path, "wb") as f:
        writer.write(f)
    after = _named_dest_count(PdfReader(str(pdf_path)))
    if after < dests_before:
        raise RuntimeError("brief_pdf: stamping page numbers dropped %d of %d named destinations "
                           "(Contents links would be dead) in %s"
                           % (dests_before - after, dests_before, pdf_path))
