#!/usr/bin/env python3
"""Inline SVG figures for the register.

No JavaScript and no chart library: every figure is SVG the generator writes into the
page, so it costs one request, renders before any script could run, and prints. Colour
comes from the page's CSS variables, so the figures follow light and dark without a
second palette to keep in sync.

Specs follow the house data-viz rules: bars capped at 24px with a 4px rounded
data-end and a square foot on the baseline, a 2px surface gap between neighbours,
markers at least 8px across with a 2px surface ring, hairline recessive gridlines,
and labels only on the extremes — a number on every mark is chaos that goes unread.
Every series here is single-hue, so there is no legend to draw and no categorical
palette to validate.

Hover is a native SVG <title>: it needs no script, it is what a screen reader reads,
and it survives with JavaScript switched off.
"""
from __future__ import annotations

import html
from datetime import date

MARK = "var(--accent)"
GRID = "var(--rule)"
SURFACE = "var(--paper)"
INK = "var(--muted)"


def _e(s) -> str:
    return html.escape(str(s)) if s is not None else ""


def _nice(v: float) -> str:
    """Axis ticks the eye can read: 1,2 Mio. rather than 1234567."""
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.1f}".replace(".", ",") + " Mia."
    if v >= 1_000_000:
        return f"{v/1_000_000:.0f} Mio."
    if v >= 1_000:
        return f"{v/1_000:.0f}k"
    return f"{v:.0f}"


def _frame(w: int, h: int, title: str, desc: str, body: str) -> str:
    # width:100% with height:auto is what actually makes an SVG responsive. A fixed
    # pixel height plus preserveAspectRatio="meet" scales the drawing to that height
    # and left-aligns it, leaving a third of a wide container empty — which is exactly
    # what it did before this line was written.
    return (f'<figure class="fig-chart"><svg viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{_e(title)}" preserveAspectRatio="xMidYMid meet" '
            f'style="display:block;width:100%;height:auto;overflow:visible">'
            f"<title>{_e(title)}</title><desc>{_e(desc)}</desc>{body}</svg>"
            f'<figcaption class="fig-cap">{_e(desc)}</figcaption></figure>')


# --------------------------------------------------------------------- timeline

def timeline(rows: list, title: str, caption: str, fmt_money) -> str:
    """One dot per award: date across, published amount up, with a readable scale.

    The amount is encoded once, by height, against labelled gridlines — encoding it a
    second time as dot size would leave the reader with two channels saying the same
    thing and a vertical axis they cannot read.

    Awards with no published amount are real and must not vanish, so they sit below the
    baseline as open marks in their own band: a chart that silently drops rows is worse
    than no chart.
    """
    pts = []
    for r in rows:
        d = (r.get("publicationDate") or "")[:10]
        if len(d) != 10:
            continue
        p = r.get("winnerPrice")
        pts.append((d, p if isinstance(p, (int, float)) and p > 0 else None, r))
    if len(pts) < 3:
        return ""
    pts.sort(key=lambda x: x[0])
    amounts = [p for _, p, _ in pts if p]
    if not amounts:
        return ""
    days = [date.fromisoformat(d).toordinal() for d, _, _ in pts]
    lo, hi = min(days), max(days)
    span = max(hi - lo, 1)
    top = max(amounts)

    W, H = 720, 200
    PADL, PADR, PADT = 62, 10, 16
    BASE_Y, NULL_Y = 152, 172       # priced dots above, unpriced in their own band
    plot_h = BASE_Y - PADT
    x = lambda o: PADL + (o - lo) / span * (W - PADL - PADR)
    # square root, so a dot twice as high is not read as twice the money by area
    y = lambda v: BASE_Y - plot_h * (v / top) ** 0.5

    body = []
    for frac in (1.0, 0.5, 0.25):
        v = top * frac
        gy = y(v)
        body.append(f'<line x1="{PADL}" y1="{gy:.1f}" x2="{W-PADR}" y2="{gy:.1f}" '
                    f'stroke="{GRID}" stroke-width="1"/>'
                    f'<text x="{PADL-8}" y="{gy+4:.1f}" fill="{INK}" font-size="11" '
                    f'text-anchor="end" style="font-variant-numeric:tabular-nums">'
                    f"{_nice(v)}</text>")
    body.append(f'<line x1="{PADL}" y1="{BASE_Y}" x2="{W-PADR}" y2="{BASE_Y}" '
                f'stroke="{GRID}" stroke-width="1"/>')

    n_null = 0
    for d, p, r in pts:
        cx = x(date.fromisoformat(d).toordinal())
        name = (r.get("title") or "")[:70]
        if p:
            tip = f"{d} · {fmt_money(p)} CHF" + (f" · {name}" if name else "")
            body.append(f'<circle cx="{cx:.1f}" cy="{y(p):.1f}" r="4.5" fill="{MARK}" '
                        f'fill-opacity="0.8" stroke="{SURFACE}" stroke-width="2">'
                        f"<title>{_e(tip)}</title></circle>")
        else:
            n_null += 1
            tip = f"{d} · kein publizierter Betrag" + (f" · {name}" if name else "")
            # 0.75, not the 0.55 this started at: measured against the light surface,
            # 0.55 gives a contrast ratio of 2.53 and WCAG asks 3.0 of a graphic that
            # carries meaning. 0.65 is the first passing step; 0.75 leaves headroom.
            body.append(f'<circle cx="{cx:.1f}" cy="{NULL_Y}" r="3.5" fill="none" '
                        f'stroke="{MARK}" stroke-width="1.6" stroke-opacity="0.75">'
                        f"<title>{_e(tip)}</title></circle>")

    body.append(f'<text x="{PADL}" y="{H-4}" fill="{INK}" font-size="11">{pts[0][0][:7]}</text>')
    body.append(f'<text x="{W-PADR}" y="{H-4}" fill="{INK}" font-size="11" '
                f'text-anchor="end">{pts[-1][0][:7]}</text>')
    if n_null:
        body.append(f'<text x="{PADL-8}" y="{NULL_Y+4}" fill="{INK}" font-size="10.5" '
                    f'text-anchor="end" opacity="0.85">o. B.</text>')
    return _frame(W, H, title, caption, "".join(body))


# ------------------------------------------------------------------------- bars

def bars(items: list, title: str, caption: str, value_fmt=None, href=None) -> str:
    """Horizontal bars for magnitude across categories: sectors, firms, authorities."""
    items = [(str(k), v) for k, v in items if v]
    if len(items) < 2:
        return ""
    items = items[:10]
    top = max(v for _, v in items)
    ROW, GAP, BAR = 30, 2, 18
    LABEL_W, VAL_W, W = 250, 62, 720
    H = len(items) * ROW
    track = W - LABEL_W - VAL_W
    body = []
    for i, (k, v) in enumerate(items):
        y = i * ROW + (ROW - BAR) / 2
        wid = max(3.0, track * v / top)
        label = k if len(k) <= 38 else k[:37] + "…"
        val = value_fmt(v) if value_fmt else f"{v}"
        body.append(
            f'<text x="0" y="{y+BAR*0.72:.0f}" fill="{INK}" font-size="12.5">{_e(label)}</text>'
            f'<path d="M{LABEL_W} {y:.0f} h{wid-4:.1f} a4 4 0 0 1 4 4 v{BAR-8} '
            f'a4 4 0 0 1 -4 4 h{-(wid-4):.1f} z" fill="{MARK}" fill-opacity="0.85">'
            f"<title>{_e(k)}: {_e(val)}</title></path>"
            f'<text x="{W}" y="{y+BAR*0.72:.0f}" fill="{INK}" font-size="12" '
            f'text-anchor="end" style="font-variant-numeric:tabular-nums">{_e(val)}</text>')
    return _frame(W, H, title, caption, "".join(body))


# ---------------------------------------------------------------------- columns

def columns(by_month: dict, title: str, caption: str) -> str:
    """Monthly volume. Columns, because the reader compares one month against another."""
    keys = sorted(by_month)
    if len(keys) < 4:
        return ""
    vals = [by_month[k] for k in keys]
    top = max(vals) or 1
    W, H, PADB, PADT = 720, 150, 26, 16
    plot = H - PADB - PADT
    slot = W / len(keys)
    bar = min(24.0, slot - 2)          # the 2px surface gap between neighbours
    body = [f'<line x1="0" y1="{H-PADB}" x2="{W}" y2="{H-PADB}" stroke="{GRID}" stroke-width="1"/>']
    for i, k in enumerate(keys):
        v = by_month[k]
        h = max(2.0, plot * v / top)
        x = i * slot + (slot - bar) / 2
        y = H - PADB - h
        r = min(4.0, bar / 2, h)
        body.append(
            f'<path d="M{x:.1f} {H-PADB} v{-(h-r):.1f} a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {-r:.1f} '
            f'h{bar-2*r:.1f} a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {r:.1f} v{h-r:.1f} z" '
            f'fill="{MARK}" fill-opacity="0.85"><title>{_e(k)}: {v}</title></path>')
    peak = keys[vals.index(top)]
    px = keys.index(peak) * slot + slot / 2
    body.append(f'<text x="{px:.0f}" y="{H-PADB-plot-2:.0f}" fill="{INK}" font-size="11" '
                f'text-anchor="middle">{top}</text>')
    body.append(f'<text x="0" y="{H-8}" fill="{INK}" font-size="11">{keys[0]}</text>')
    body.append(f'<text x="{W}" y="{H-8}" fill="{INK}" font-size="11" '
                f'text-anchor="end">{keys[-1]}</text>')
    return _frame(W, H, title, caption, "".join(body))
