#!/usr/bin/env python3
"""Inline SVG charts for the register.

No script, no library: every chart is markup the page already carries, so it paints
with the first byte and works with JavaScript off. Hover text rides in an SVG <title>,
which browsers surface natively and screen readers announce — an interaction layer
that costs nothing.

The specs are fixed across every chart here: bars capped at 24px with a 4px rounded
data-end and a square baseline, hairline recessive gridlines, dots at r>=4 with a 2px
ring in the surface colour, and a 2px gap between touching marks. Labels are placed
selectively — the extreme, the endpoint — never one on every mark, because a number
beside everything goes unread.

Colour is one hue: every chart here plots a single series, so identity needs no
palette and the mark carries magnitude alone. Dark mode gets its own step rather than
an inversion. Text never wears the data colour.
"""
from __future__ import annotations

import html
from datetime import date

# Chart tokens. Defined here and mirrored into the stylesheet so a chart and the page
# around it move together when either changes.
CSS = """
.chart{width:100%;height:auto;display:block;margin:14px 0 4px;overflow:visible}
.chart .grid{stroke:var(--rule);stroke-width:1;fill:none}
.chart .axis{fill:var(--muted);font-size:10.5px;letter-spacing:.02em}
.chart .mark{fill:var(--mark)}
.chart .mark-soft{fill:var(--mark);opacity:.28}
/* the ring separates overlapping dots, so it has to be the colour of the
   surface the chart actually sits on — the panel, not the page */
.chart .ring{stroke:var(--panel);stroke-width:1.5}
.chart .lab{fill:var(--ink);font-size:11px;font-variant-numeric:tabular-nums}
.chart .lab-mute{fill:var(--muted);font-size:10.5px;font-variant-numeric:tabular-nums}
.chart-note{color:var(--muted);font-size:11.5px;margin:2px 0 0}
figure{margin:0}
figcaption{color:var(--muted);font-size:11.5px;margin-top:6px}
"""

TOKENS_LIGHT = "--mark:oklch(52% .13 245);"
TOKENS_DARK = "--mark:oklch(72% .13 245);"


def _e(s) -> str:
    return html.escape(str(s), quote=True) if s is not None else ""


def _num(v: float) -> str:
    return f"{v:,.0f}".replace(",", "’")


# Set per language pass by the generator: Mrd./Mio. are German abbreviations and read
# foreign on the French and Italian charts.
BILLION, MILLION, DEC = "Mrd.", "Mio.", ","


def _compact(v: float) -> str:
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.1f}".replace(".", DEC) + f" {BILLION}"
    if v >= 1_000_000:
        return f"{v/1_000_000:.0f} {MILLION}"
    if v >= 1_000:
        return f"{v/1_000:.0f}k"
    return _num(v)


def _wcut(t: str, n: int) -> str:
    """Bar labels cut on a word boundary — mid-word ends read as damage."""
    t = (t or "").strip()
    if len(t) <= n:
        return t
    c = t[:n]
    if " " in c[max(0, n - 14):]:
        c = c[:c.rfind(" ")]
    return c.rstrip(" ,.;:-–—/") + "…"


def bars(items: list[tuple[str, float]], *, unit: str = "", title: str = "",
         width: int = 460, row: int = 30, max_rows: int = 10) -> str:
    """Horizontal bars: magnitude across a handful of named things.

    Names sit outside the bar, always — a label inside a short bar either overflows or
    gets clipped, and clipping the first characters is worse than no label at all.
    """
    items = [(k, v) for k, v in items if v][:max_rows]
    if not items:
        return ""
    top = max(v for _, v in items)
    lab_w = 168
    bar_w = width - lab_w - 58
    h = row * len(items)
    out = [f'<svg class="chart" viewBox="0 0 {width} {h}" role="img" '
           f'aria-label="{_e(title)}" preserveAspectRatio="xMinYMin meet">']
    for i, (k, v) in enumerate(items):
        y = i * row
        w = max(2, round(bar_w * v / top))
        out.append(
            f'<text class="axis" x="0" y="{y + row/2 + 3.5}">{_e(_wcut(k, 30))}</text>'
            # 4px rounded data-end, square at the baseline: rx on a rect rounds both
            # ends, so the bar is drawn as a path instead
            f'<path class="mark" d="M{lab_w} {y+5} h{max(0, w-4)} a4 4 0 0 1 4 4 '
            f'v{row-18} a4 4 0 0 1 -4 4 h-{max(0, w-4)} z">'
            f'<title>{_e(k)}: {_e(_num(v))}{_e(" " + unit if unit else "")}</title></path>'
            f'<text class="lab" x="{lab_w + w + 8}" y="{y + row/2 + 3.5}">{_e(_compact(v))}</text>')
    out.append("</svg>")
    return "".join(out)


def timeline(points: list[tuple[str, float]], *, title: str = "", width: int = 640,
             height: int = 120, unit: str = "CHF") -> str:
    """One dot per award on a date axis, area by amount.

    The shape of a firm's public work — how often, how big — is the thing a reader
    wants first and a table makes them assemble in their head. Dots without an amount
    still appear, at the floor size and lighter: dropping them would understate how
    often the firm wins.
    """
    pts = [(d, v) for d, v in points if d]
    if len(pts) < 2:
        return ""
    xs = sorted(pts, key=lambda p: p[0])
    d0, d1 = date.fromisoformat(xs[0][0][:10]), date.fromisoformat(xs[-1][0][:10])
    span = max((d1 - d0).days, 1)
    vals = [v for _, v in xs if v]
    vmax = max(vals) if vals else 1
    pad_l, pad_r, pad_b = 8, 8, 22
    plot_w = width - pad_l - pad_r
    cy = (height - pad_b) / 2
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
           f'aria-label="{_e(title)}" preserveAspectRatio="xMinYMin meet">',
           f'<line class="grid" x1="{pad_l}" y1="{cy}" x2="{width-pad_r}" y2="{cy}"/>']
    for d, v in xs:
        x = pad_l + plot_w * (date.fromisoformat(d[:10]) - d0).days / span
        r = 4 + (10 * (v / vmax) ** 0.5 if v else 0)      # area, not radius, carries value
        cls = "mark" if v else "mark-soft"
        amt = f"{_num(v)} {unit}" if v else "—"
        out.append(f'<circle class="{cls} ring" cx="{x:.1f}" cy="{cy}" r="{r:.1f}">'
                   f'<title>{_e(d[:10])} · {_e(amt)}</title></circle>')
    out.append(f'<text class="axis" x="{pad_l}" y="{height-6}">{_e(xs[0][0][:7])}</text>'
               f'<text class="axis" x="{width-pad_r}" y="{height-6}" '
               f'text-anchor="end">{_e(xs[-1][0][:7])}</text>')
    if vals:
        out.append(f'<text class="lab-mute" x="{pad_l}" y="14">'
                   f'{_e(_compact(max(vals)))} {_e(unit)} max</text>')
    out.append("</svg>")
    return "".join(out)


def columns(series: list[tuple[str, float]], *, title: str = "", width: int = 640,
            height: int = 130, label_every: int = 3) -> str:
    """Volume over time. Columns because the periods are discrete counts, not a flow."""
    series = [s for s in series if s]
    if len(series) < 3:
        return ""
    top = max(v for _, v in series) or 1
    pad_b, pad_t = 20, 14
    plot_h = height - pad_b - pad_t
    slot = width / len(series)
    bw = min(24, slot - 2)                      # 2px surface gap between neighbours
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
           f'aria-label="{_e(title)}" preserveAspectRatio="xMinYMin meet">',
           f'<line class="grid" x1="0" y1="{height-pad_b}" x2="{width}" '
           f'y2="{height-pad_b}"/>']
    for i, (k, v) in enumerate(series):
        h = max(2, round(plot_h * v / top))
        x = i * slot + (slot - bw) / 2
        y = height - pad_b - h
        out.append(
            f'<path class="mark" d="M{x:.1f} {y+4} a4 4 0 0 1 4 -4 h{bw-8:.1f} '
            f'a4 4 0 0 1 4 4 v{h-4} h-{bw:.1f} z">'
            f'<title>{_e(k)}: {_e(_num(v))}</title></path>')
        if i % label_every == 0 or i == len(series) - 1:
            out.append(f'<text class="axis" x="{x + bw/2:.1f}" y="{height-6}" '
                       f'text-anchor="middle">{_e(k[-5:] if len(k) > 5 else k)}</text>')
    hi = max(range(len(series)), key=lambda i: series[i][1])
    hx = hi * slot + slot / 2
    hy = height - pad_b - round(plot_h * series[hi][1] / top)
    out.append(f'<text class="lab" x="{hx:.1f}" y="{max(10, hy-5):.1f}" '
               f'text-anchor="middle">{_e(_num(series[hi][1]))}</text>')
    out.append("</svg>")
    return "".join(out)
