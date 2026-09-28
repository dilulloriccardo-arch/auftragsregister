#!/usr/bin/env python3
"""Charts as HTML/CSS: text stays in CSS pixels on every screen, values are real text
(no hover-only data), and the markup is its own data table. No script, no SVG.

Two components serve every chart on the site:
- month_columns(): awards per month (home, canton, buyer, sector pages)
- rank_list():     a ranked list with a bar under each label (CPV divisions on canton and
                   buyer pages, amount bands on company pages, open tenders per canton)
One hue (--mark). Incomplete months are STRIPED (hatch plus outline), not paler: on the dark
panel a paler column rendered darker, and the note calling it "lighter" pointed the reader at
the wrong columns (verifier, 28.09.2026). A striped key swatch opens the note that explains them.
"""
from __future__ import annotations

import html

import formato
import lingue

CSS = """
figure .lede{color:var(--muted);font-size:14px;margin:6px 0 0;max-width:70ch}
figure h3{font-size:17px;margin:0}
figure .note{color:var(--muted);font-size:12.5px;margin:12px 0 0;max-width:80ch}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
.mc .unit{font-size:11.5px;color:var(--muted);margin:14px 0 10px}
.cc{display:grid;grid-template-columns:auto minmax(0,1fr);gap:0 8px}
.cc .yax{position:relative;height:160px;min-width:2.4em;font-size:11.5px;color:var(--muted);
  font-variant-numeric:tabular-nums}
.cc .yax span{position:absolute;right:0;transform:translateY(50%);line-height:1}
.cc table{width:100%;border-collapse:collapse;table-layout:fixed}
.cc tbody{display:flex;align-items:flex-end;height:160px;gap:2px;
  background:linear-gradient(var(--rule),var(--rule)) 0 0/100% 1px no-repeat,
    linear-gradient(var(--rule),var(--rule)) 0 50%/100% 1px no-repeat,
    linear-gradient(var(--rule-strong),var(--rule-strong)) 0 100%/100% 1px no-repeat}
.cc.nomid tbody{background:linear-gradient(var(--rule),var(--rule)) 0 0/100% 1px no-repeat,
    linear-gradient(var(--rule-strong),var(--rule-strong)) 0 100%/100% 1px no-repeat}
.cc tr{flex:1;min-width:0;display:flex;height:100%;position:relative}
.cc th,.cc td{padding:0;border:0}
.cc td{flex:1;display:flex;flex-direction:column;justify-content:flex-end;height:100%}
.cc td span{display:block;position:relative;background:var(--mark);border-radius:3px 3px 0 0}
.cc tr.part td span{background:repeating-linear-gradient(-45deg,var(--mark) 0 2px,transparent 2px 5px);
  box-shadow:inset 0 0 0 1.5px var(--mark);min-height:7px}
figure .note .key{display:inline-block;width:.95em;height:.95em;margin:0 .45em -.12em 0;
  border-radius:2px;background:repeating-linear-gradient(-45deg,var(--mark) 0 2px,transparent 2px 5px);
  box-shadow:inset 0 0 0 1.5px var(--mark)}
.cc tr.zero td span{display:none}
.cc td b{position:absolute;bottom:100%;left:50%;transform:translateX(-50%);margin-bottom:4px;
  font-size:11.5px;line-height:1;font-weight:600;color:var(--ink);white-space:nowrap}
.cc tr:first-child td b{left:0;transform:none}
.cc tr:last-child td b{left:auto;right:0;transform:none}
.cc .xax{grid-column:2;display:flex;gap:2px;margin-top:6px;font-size:11.5px;color:var(--muted)}
.cc .xax>span{flex:1;min-width:0;white-space:nowrap;overflow:visible}
.cc .xax span.yr{color:var(--ink);font-weight:600}
.cc .xax span.r0{display:flex;justify-content:flex-end}
.cc .xax .m{font-weight:400;color:var(--muted)}
@media(max-width:600px){.cc .xax span.q{visibility:hidden}}
.bl{list-style:none;margin:16px 0 0;padding:0}
.bl li{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;padding:9px 0;
  border-bottom:1px solid var(--rule);break-inside:avoid}
.bl .lab{font-size:14px;line-height:1.35}
.bl .val{font-size:13.5px;text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.bl .val small{color:var(--muted);font-size:12px;margin-left:8px}
.bl .trk{grid-column:1/-1;height:6px}
.bl .trk i{display:block;height:6px;background:var(--mark);border-radius:0 3px 3px 0}
.bl li.oth .lab,.bl li.oth .val{color:var(--muted)}
@media(min-width:861px){.bl.two{columns:2;column-gap:48px}}
"""

_e = lambda s: html.escape(str(s), quote=True) if s is not None else ""


def _nice(top: int) -> int:
    """The axis maximum: the smallest whole 1/1.5/2/2.5/3/4/5/6/8 x 10^k at or above top plus
    10 % headroom (at least 2).

    Only 1/2/5 steps left the tallest column at 44 % of the plot (22 on a 0-50 axis, 24
    charts per language), and a column reaching the very top pushed its value label into the
    axis caption above the plot (148 collisions; verifier 28.09.2026). With these steps and the
    headroom the tallest column fills 67-91 % of the height and its label stays inside."""
    need = max(top * 1.1, 2)
    k = 1
    while True:
        for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8):
            v = m * k
            if v == int(v) and v >= need:
                return int(v)
        k *= 10


def peak_months(series, partial) -> list[str]:
    """The complete month(s) with the most awards, all of them when several tie."""
    comp = [(k, v) for k, v in series if k not in partial]
    top = max((v for _k, v in comp), default=0)
    return [k for k, v in comp if v == top] if top else []


def month_columns(series, *, fig_id: str, title: str, takeaway: str, unit_label: str,
                  units: tuple[str, str], partial: set, notes: list[str]) -> str:
    """series: [(YYYY-MM, count)] consecutive months, zeros filled; partial: months drawn striped.
    The caller has already applied the minimum-data rule. The note opens with a striped key
    only when a striped column is actually drawn (a partial month with at least one award)."""
    keys = [k for k, _ in series]
    vals = dict(series)
    pos = {k: i for i, k in enumerate(keys)}
    top = max(vals.values()) or 1
    ymax = _nice(top)
    mid = ymax // 2 if ymax % 2 == 0 else None
    complete = [k for k in keys if k not in partial]
    # the busiest complete month(s): a tie is labelled on every tied column, or on none when
    # two of them sit within two slots (their labels would collide); the takeaway names them
    # all (122 charts per language named one month of a tie, verifier 28.09.2026)
    peaks = peak_months(series, partial)
    far = all(abs(pos[a] - pos[b]) > 2 for a in peaks for b in peaks if a < b)
    lab = set(peaks) if far else set()
    last = complete[-1] if complete else None
    if last and last not in peaks and all(abs(pos[last] - pos[p]) > 2 for p in peaks):
        lab.add(last)
    # a running month already above the peak gets its value too, or the tallest column on the
    # chart is the one unlabelled (the takeaway names the peak of COMPLETE months only) —
    # unless a label within two slots sits at nearly the same height and would collide
    cur = keys[-1] if keys[-1] in partial else None
    pk = vals[peaks[0]] if peaks else 0
    if cur and vals[cur] > pk and all(
            abs(pos[k] - len(keys) + 1) > 2 or abs(vals[cur] - vals[k]) >= .15 * ymax for k in lab):
        lab.add(cur)
    colon = lingue.COLON[formato.LANG]
    rows = []
    for k in keys:
        v = vals[k]
        cls = " ".join(c for c in ("part" if k in partial else "", "zero" if v == 0 else "") if c)
        unit = units[0] if v == 1 else units[1]
        tip = f"{formato.month(k, full=True)}{colon} {formato.count(v)} {unit}"
        # the visible label is hidden from screen readers: the cell's own text already says
        # "7 aggiudicazioni", and they heard "7 7 aggiudicazioni" (verifier, 28.09.2026)
        b = f'<b aria-hidden="true">{_e(formato.count(v))}</b>' if k in lab and v else ""
        rows.append(f'<tr{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>'
                    f'<th scope="row" class="sr">{_e(formato.month(k, full=True))}</th>'
                    f'<td title="{_e(tip)}"><span style="height:{100 * v / ymax:.1f}%">{b}</span>'
                    f'<em class="sr">{_e(formato.count(v))} {_e(unit)}</em></td></tr>')
    # x axis: slot 0 always names its month AND year ('Okt. 2024'): an axis opening on a bare
    # "Okt." left the reader guessing the year (80 charts per language), and a bare "2024"
    # under an October column read as January (verifier, 28.09.2026). The label ends at the
    # first column's right edge and hangs left under the y axis, so it never runs into the
    # next label, the January year included; then every January, and Apr/Jul/Oct in between,
    # never within two slots of a label already placed. (The plot column is minmax(0,1fr): the
    # hanging label must not widen it, or the page scrolls sideways at 320 px.)
    xs, lastpos = [], -99
    first_jan = next((i for i, k in enumerate(keys) if k[5:7] == "01"), None)
    for i, k in enumerate(keys):
        m = int(k[5:7])
        if i == 0 and m != 1:
            xs.append(f'<span class="yr r0"><span class="m">{_e(formato.month_abbr(m))}{formato.NBSP}'
                      f'</span>{k[:4]}</span>')
            lastpos = i
        elif m == 1:
            xs.append(f'<span class="yr">{k[:4]}</span>')
            lastpos = i
        elif m in (4, 7, 10) and i - lastpos > 2 and (first_jan is None or i < first_jan - 2 or i > first_jan):
            xs.append(f'<span class="q">{_e(formato.month_abbr(m))}</span>')
            lastpos = i
        else:
            xs.append("<span></span>")
    ticks = [(ymax, 100.0)] + ([(mid, 50.0)] if mid else []) + [(0, 0.0)]
    yax = "".join(f'<span style="bottom:{p:.0f}%">{_e(formato.count(t))}</span>' for t, p in ticks)
    note = " ".join(n for n in notes if n)
    key = '<i class="key" aria-hidden="true"></i>' if any(vals[k] for k in keys if k in partial) else ""
    return (f'<figure class="mc" aria-labelledby="{fig_id}" aria-describedby="{fig_id}-t">'
            f'<h3 id="{fig_id}">{_e(title)}</h3>'
            + (f'<p class="lede" id="{fig_id}-t">{_e(takeaway)}</p>' if takeaway else "")
            + f'<p class="unit" aria-hidden="true">{_e(unit_label)}</p>'
            f'<div class="cc{"" if mid else " nomid"}"><div class="yax" aria-hidden="true">{yax}</div>'
            f'<table><caption class="sr">{_e(title)}</caption><tbody>{"".join(rows)}</tbody></table>'
            f'<div class="xax" aria-hidden="true">{"".join(xs)}</div></div>'
            + (f'<p class="note">{key}{_e(note)}</p>' if note else "") + "</figure>")


def rank_list(items, *, fig_id: str, title: str | None = None, labelledby: str | None = None,
              lede: str = "", other=None, total: int | None = None, two_cols: bool = False,
              note: str = "") -> str:
    """items: [(label, href or None, value, value_text)] in display order; other: same shape
    or None (muted, no bar). total set -> each row shows its share. Bars scale to the largest
    item; fewer than 3 items -> no bars."""
    mx = max((v for _, _, v, _ in items), default=0) or 1
    bars = len(items) >= 3
    li = []
    rows = items + ([other] if other else [])
    shares = formato.pcts([v for _, _, v, _ in rows], total) if total else []
    for i, (lab, href, v, vt) in enumerate(rows):
        oth = other is not None and i == len(items)
        name = f'<a href="{_e(href)}">{_e(lab)}</a>' if href else _e(lab)
        share = f"<small>{_e(shares[i])}</small>" if total else ""
        trk = ""
        if bars and not oth:
            trk = ('<span class="trk" aria-hidden="true">'
                   + (f'<i style="width:{max(1.0, 100 * v / mx):.1f}%"></i>' if v else "") + "</span>")
        li.append(f'<li{" class=" + chr(34) + "oth" + chr(34) if oth else ""}><span class="lab">{name}</span>'
                  f'<span class="val">{_e(vt)}{share}</span>{trk}</li>')
    lab_attr = labelledby or fig_id
    return (f'<figure class="rk" aria-labelledby="{lab_attr}">'
            + (f'<h3 id="{fig_id}">{_e(title)}</h3>' if title else "")
            + (f'<p class="lede">{_e(lede)}</p>' if lede else "")
            + f'<ol class="bl{" two" if two_cols else ""}">{"".join(li)}</ol>'
            + (f'<p class="note">{_e(note)}</p>' if note else "") + "</figure>")
