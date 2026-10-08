"""One formatter for every number and date the site prints.

The owner's complaint (28.09.2026): "991,939,563 — these should be rounded, and it concerns
ALL the site's content". Figures were printed at full precision in some places and as
"Mio." in others, dates as ISO on the English pages, and each builder had its own helper.
Every count, amount, percentage and date now goes through this module, so a page cannot
mix conventions again. Amounts are rounded to at most three significant digits everywhere
except the award page, which is the official record and keeps the exact published figure.

genera.main() sets formato.LANG per language pass and formato.MONTHS = lingue.MONTHS;
genera.py and grafici.py both import it.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import html

LANG = "de"
NBSP, NNBSP = "\u00a0", "\u202f"
GROUP = {"de": "’", "it": "’", "fr": NNBSP, "en": ","}
DEC = {"de": ",", "fr": ",", "it": ",", "en": "."}          # rounded figures only
UNITS = {"de": ("Mio.", "Mrd."), "fr": ("mio", "mrd"), "it": ("mio.", "mia."), "en": ("m", "bn")}
MONTHS = {}   # filled from lingue.MONTHS by genera.main(): {lang: (abbr12, full12)}


def _q(x, exp: str) -> Decimal:
    return Decimal(str(x)).quantize(Decimal(exp), rounding=ROUND_HALF_UP)


def _group(i: int) -> str:
    return f"{i:,}".replace(",", GROUP[LANG])


def count(n) -> str:
    """Exact count, grouped from 1000 up: 1’432 / 1 432 / 1,432. Never for years or codes."""
    return _group(int(n))


def _dec1(d: Decimal) -> str:
    """One decimal, trailing ',0' dropped: 2,1 / 30,1 / 1."""
    s = f"{d:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return s.replace(".", DEC[LANG])


def num1(x) -> str:
    """An average: whole number from 10 up (grouped), one decimal below ('7,5' / '7.5')."""
    return count(int(_q(x, "1"))) if x >= 10 else _dec1(_q(x, "0.1"))


def amount(v) -> str:
    """Rounded amount WITHOUT currency: '992 Mio.' / '992 mio' / '992 mio.' / '992m'.
    >= 999'500'000 -> billions, 1 decimal; >= 99'950'000 -> whole millions;
    >= 999'500 -> millions, 1 decimal; >= 10'000 -> nearest thousand; >= 100 -> whole francs;
    < 100 -> Rappen kept (unit prices), decimal POINT in every language."""
    if v is None or not v:
        return ""
    v = float(v)
    mn, bn = UNITS[LANG]
    sep = "" if LANG == "en" else NBSP
    if v >= 999_500_000:
        return _dec1(_q(v / 1e9, "0.1")) + sep + bn
    if v >= 99_950_000:
        return _group(int(_q(v / 1e6, "1"))) + sep + mn
    if v >= 999_500:
        return _dec1(_q(v / 1e6, "0.1")) + sep + mn
    if v >= 10_000:
        return _group(int(_q(v, "1E3")))
    if v >= 100:
        return _group(int(_q(v, "1")))
    return f"{_q(v, '0.01'):.2f}"


def shown(v) -> float:
    """The value amount() prints, as a number: 999’696.20 -> 1’000’000 ('1 Mio.'),
    99’692.52 -> 100’000. Anything that sorts amounts into bands uses this, so an award
    shown as '1 Mio.' is never counted under 'bis unter 1 Mio.' (verifier, 28.09.2026)."""
    if v is None or not v:
        return 0.0
    v = float(v)
    if v >= 999_500_000:
        return float(_q(v / 1e9, "0.1")) * 1e9
    if v >= 99_950_000:
        return float(_q(v / 1e6, "1")) * 1e6
    if v >= 999_500:
        return float(_q(v / 1e6, "0.1")) * 1e6
    if v >= 10_000:
        return float(_q(v, "1E3"))
    if v >= 100:
        return float(_q(v, "1"))
    return float(_q(v, "0.01"))


def money(v, cur: str = "CHF") -> str:
    """Rounded amount WITH currency: '992 Mio. CHF' / 'CHF 992m' / '1,2 Mio. EUR'."""
    a = amount(v)
    if not a:
        return ""
    return f"{cur}{NBSP}{a}" if LANG == "en" else f"{a}{NBSP}{cur}"


def _value(v) -> str:
    """The machine-readable value of a <data> element, rounded the same way as the exact
    figure in its tooltip: float formatting rounded a median of 247’575.625 down to .62
    while the tooltip, rounded half up, said .63 (384 company pages)."""
    return f"{_q(v, '0.01'):.2f}"


def money_data(v, cur: str = "CHF") -> str:
    """A rounded amount in running text or a list (HTML), with the exact figure on hover:
    '<data value="331000000.00" title="331’042’118.20 CHF">331 Mio. CHF</data>'."""
    m = money(v, cur)
    if not m:
        return ""
    return f'<data value="{_value(v)}" title="{html.escape(exact(v, cur))}">{html.escape(m)}</data>'


def _exact_num(v) -> str:
    d = _q(v, "0.01")
    whole = int(d)
    return _group(whole) if d == whole else _group(whole) + "." + f"{d:.2f}".split(".")[1]


def exact(v, cur: str = "CHF") -> str:
    """The amount as published: Rappen kept when present, decimal point (Swiss money convention).
    '505’714.45 CHF' / '505 714.45 CHF' / '505’714.45 CHF' / 'CHF 505,714.45'; integers without decimals."""
    if v is None or not v:
        return ""
    s = _exact_num(v)
    return f"{cur}{NBSP}{s}" if LANG == "en" else f"{s}{NBSP}{cur}"


def exact_tile(v, cur: str = "CHF") -> str:
    """The exact amount as a KPI tile value (HTML), for the award page: digits in one unbreakable
    span, currency small. A line may break only before the currency, never inside the number or
    inside 'CHF' ('827’782.5|5 CHF' and '612’450 C|HF' on 390px phones, verifier 28.09.2026)."""
    if v is None or not v:
        return ""
    t = f'<data value="{_value(v)}">'
    n = html.escape(_exact_num(v))
    if LANG == "en":
        return t + f'<small>{cur}{NBSP}</small><span class="n">{n}</span></data>'
    return t + f'<span class="n">{n}</span> <small>{cur}</small></data>'


def cell(v, cur: str = "CHF", empty_sr: str = "") -> str:
    """Table cell content (HTML): rounded figure without the column's currency, exact value in title.
    Foreign currency keeps its code: '1,2 Mio. EUR'. Missing: '–' + visually hidden reason."""
    if v is None or not v:
        return "–" + (f'<span class="sr"> {html.escape(empty_sr)}</span>' if empty_sr else "")
    txt = amount(v) if cur == "CHF" else money(v, cur)
    return (f'<data value="{_value(v)}" title="{html.escape(exact(v, cur))}">'
            f"{html.escape(txt)}</data>")


def exact_cell(v, cur: str = "CHF", empty_sr: str = "") -> str:
    """Table cell content (HTML) on the award page, the official record: the amount as published,
    Rappen kept, without the column's currency; a foreign currency keeps its code. The lots of a
    project are listed there in a table (08.10.2026). Missing: as in cell()."""
    if v is None or not v:
        return "–" + (f'<span class="sr"> {html.escape(empty_sr)}</span>' if empty_sr else "")
    txt = _exact_num(v) if cur == "CHF" else exact(v, cur)
    return f'<data value="{_value(v)}">{html.escape(txt)}</data>'


def tile(v, cur: str = "CHF") -> str:
    """KPI tile value (HTML): number big, currency small. '<span class="n">992 Mio.</span> <small>CHF</small>'
    / '<small>CHF </small><span class="n">992m</span>'. The number and its unit never break; on a
    narrow tile the currency moves to the next line as a whole word (an ordinary space before it)."""
    a = amount(v)
    if not a:
        return ""
    t = f'<data value="{_value(v)}" title="{html.escape(exact(v, cur))}">'
    if LANG == "en":
        return t + f'<small>{cur}{NBSP}</small><span class="n">{html.escape(a)}</span></data>'
    return t + f'<span class="n">{html.escape(a)}</span> <small>{cur}</small></data>'


def pct(x: float) -> str:
    """Whole percent; '<1 %' for 0 < x < 0.5 and '>99 %' for 99.5 <= x < 100, so a share that is
    not the whole never reads '100 %'. de '6 %', fr '6 %', it '6%', en '6%'."""
    s = "<1" if 0 < x < 0.5 else ">99" if 99.5 <= x < 100 else str(int(_q(x, "1")))
    return s + {"de": NBSP + "%", "fr": NNBSP + "%"}.get(LANG, "%")


def pcts(vals: list, total: float) -> list[str]:
    """Shares of a whole as pct() writes them, rounded by largest remainder when the values ARE
    the whole, so a list of shares adds up to 100 (Uri's branches read 102 %; verifier,
    28.09.2026). Otherwise each is rounded on its own."""
    if not total:
        return ["" for _v in vals]
    raw = [100 * v / total for v in vals]
    if abs(sum(vals) - total) > 1e-9:
        return [pct(r) for r in raw]
    base = [int(r) for r in raw]
    need = 100 - sum(base)
    # equal values keep equal shares ('1 · 8 %' beside '1 · 7 %' would read as an error):
    # the remainders are handed out by group, and a group that does not fit whole gets its
    # point only if that lands nearer to 100
    groups: dict = {}
    for i, v in enumerate(vals):
        groups.setdefault(v, []).append(i)
    for g in sorted(groups.values(), key=lambda g: -(raw[g[0]] - base[g[0]])):
        if need <= 0 or raw[g[0]] == base[g[0]]:
            break
        if len(g) <= need or len(g) - need < need:
            for i in g:
                base[i] += 1
            need -= len(g)
    out = []
    for r, b in zip(raw, base):
        s = "<1" if 0 < r and b == 0 else ">99" if r < 100 and b == 100 else str(b)
        out.append(s + {"de": NBSP + "%", "fr": NNBSP + "%"}.get(LANG, "%"))
    return out


def _d(iso: str):
    return int(iso[:4]), int(iso[5:7]), int(iso[8:10])


def date(iso: str) -> str:
    """25.09.2026 (de/fr/it) · 25 Sep 2026 (en)."""
    if not iso or len(iso) < 10:
        return ""
    y, m, d = _d(iso)
    if LANG == "en":
        return f"{d}{NBSP}{MONTHS['en'][0][m-1]}{NBSP}{y}"
    return f"{d:02d}.{m:02d}.{y}"


def date_short(iso: str) -> str:
    """25.09. (de/fr/it) · 25 Sep (en)."""
    if not iso or len(iso) < 10:
        return ""
    y, m, d = _d(iso)
    return f"{d}{NBSP}{MONTHS['en'][0][m-1]}" if LANG == "en" else f"{d:02d}.{m:02d}."


def clock(iso: str) -> str:
    """The published local time of a deadline, as each language writes a time in Switzerland:
    '12.00 Uhr', '12 h 00', '12:00'; '' when there is none or it is 00:00. Split out of deadline()
    for 'läuft heute ab, 12.00 Uhr' in the tender lists (08.10.2026)."""
    t = iso[11:16] if len(iso or "") >= 16 and iso[10] == "T" else ""
    if not t or t == "00:00":
        return ""
    h, m = t[:2], t[3:5]
    if LANG == "de":
        return f"{int(h)}.{m}{NBSP}Uhr"
    if LANG == "fr":
        return f"{int(h)}{NNBSP}h{NNBSP}{m}"
    return t


def deadline(iso: str) -> str:
    """Date plus the published local time when there is one, as each language writes a time
    in Switzerland: '25.09.2026, 12.00 Uhr', '25.09.2026, 12 h 00', '25.09.2026, 12:00'."""
    s, t = date(iso), clock(iso)
    return f"{s}, {t}" if s and t else s


def month(ym: str, full: bool = False) -> str:
    """'Sept. 2026' / 'sept. 2026' / 'set. 2026' / 'Sep 2026'; full=True: 'September 2026'."""
    y, m = int(ym[:4]), int(ym[5:7])
    return MONTHS[LANG][1 if full else 0][m - 1] + NBSP + str(y)


def month_abbr(m: int) -> str:
    return MONTHS[LANG][0][m - 1]


AND = {"de": "und", "fr": "et", "it": "e", "en": "and"}


def month_range(a: str, b: str) -> str:
    """A span of months in a note: 'Sept.–Okt. 2024' within one year, 'Dez. 2024 – Jan. 2025'
    across two; one month -> 'Okt. 2024'."""
    if a[:7] == b[:7]:
        return month(a)
    if a[:4] == b[:4]:
        return f"{month_abbr(int(a[5:7]))}–{month(b)}"
    return f"{month(a)}{NBSP}– {month(b)}"


def month_list(keys: list[str]) -> str:
    """Two or more months joined as prose: 'Feb. und März 2026', 'Dez. 2025 und Jan. 2026',
    'Feb., März und Mai 2026'. The year is written once when all share it."""
    keys = sorted(keys)
    same = len({k[:4] for k in keys}) == 1
    parts = [month_abbr(int(k[5:7])) if same else month(k) for k in keys]
    if same:
        parts[-1] = month(keys[-1])
    head = ", ".join(parts[:-1])
    return f"{head} {AND[LANG]} {parts[-1]}" if head else parts[-1]


def period(a: str, b: str) -> str:
    """'Okt. 2024 – Sept. 2026' (no-break space before the dash); one month -> 'Sept. 2026'."""
    return month(a) if a[:7] == b[:7] else f"{month(a)}{NBSP}– {month(b)}"


def time_tag(iso: str, text: str) -> str:
    return f'<time datetime="{iso[:10]}">{html.escape(text)}</time>' if text else ""
