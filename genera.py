#!/usr/bin/env python3
"""Build the static register from simap award and tender data.

The look follows the design canvas: a printed register rather than a product page —
hairline rules instead of cards, an asymmetric grid with the metadata on a rail,
tabular figures, running heads. Source Serif 4 sets the headings, IBM Plex Sans the
data, IBM Plex Mono the publication numbers and CPV codes.

Every page has to earn its place in an index. A page carrying a company name and one
line of data is thin content, and thin content is what search engines drop — so a
company page is written only when the record behind it is worth reading, and it
carries the full award list, the aggregates computed from it, the open tenders that
match the company's own history, and links out to its sector and canton.

Legal: simap's API terms permit commercial reuse and passing data to third parties
(§4) provided the data is not altered in content, stays visually distinct from
commentary, and carries the notice verbatim (§5). The notice is in the footer of
every page that shows publication data, commentary sits in its own marked block, and
no figure is recomputed into something the source did not say.
"""
from __future__ import annotations

import collections
import html
import json
import pathlib
import re
import shutil
import unicodedata
from datetime import date

import grafici
import lingue
from lingue import LANGS, NAMES

ROOT = pathlib.Path(__file__).resolve().parent
DATI = ROOT / "dati"
OUT = ROOT / "docs"
# The canonical origin. Kept in a file rather than in code so the domain can be set
# once, without editing the generator; every canonical link and the sitemap use it.
# The canonical origin, and the path the site is served from. GitHub Pages serves a
# project site from /<repo>/, so every root-relative link needs that prefix; a custom
# domain serves from the root and BASE is empty. Both live in dominio.txt: first line
# the origin, optional second line the base path.
_DOMAIN = ROOT / "dominio.txt"
_lines = (_DOMAIN.read_text().strip().splitlines() if _DOMAIN.exists()
          else ["https://example.invalid"])
SITE = _lines[0].strip().rstrip("/")
# Search Console proves ownership with a meta tag. The token is pasted into
# search-console.txt once; the tag then rides on every page automatically.
_SC = ROOT / "search-console.txt"
VERIFY = (f'<meta name="google-site-verification" content="{_SC.read_text().strip()}">\n'
          if _SC.exists() and _SC.read_text().strip() else "")
BASE = (_lines[1].strip().rstrip("/") if len(_lines) > 1 else "")
# Every absolute URL the site declares about itself — canonical, hreflang, breadcrumb
# item, sitemap <loc> — has to carry the base path too. Using SITE alone published
# 75,141 canonicals and 375,705 hreflang alternates pointing at 404s, which would have
# made a Search Console submission return "not found" for the entire site.
ORIGIN = SITE + BASE
DISCLAIMER = lingue.PROSE["disclaimer"]["de"]   # prescribed verbatim by simap's terms
LANG = "de"                                     # set per pass by main()


class _Words:
    """Chrome strings reached by attribute rather than by call.

    Python 3.11 forbids reusing the delimiter quote inside an f-string
    expression, and this template code is nothing but f-strings — so an
    attribute lookup keeps every substitution quote-free.
    """

    def __getattr__(self, key: str) -> str:
        return lingue.t(key, LANG)


class _Prose:
    def __getattr__(self, key: str) -> str:
        return lingue.p(key, LANG)


def _m(key: str, **kw) -> str:
    return lingue.m(key, LANG, **kw)


class _Idx:
    def __getattr__(self, key: str) -> str:
        return lingue.i(key, LANG)


_i = _Idx()


def _if(key: str, **kw) -> str:
    return lingue.i(key, LANG, **kw)


_ = _Words()
_p = _Prose()
MIN_AWARDS = 2          # below this a company page is thin; the record still shows in hubs
TODAY = date.today().isoformat()

CANTONS = {
    "AG": "Aargau", "AI": "Appenzell Innerrhoden", "AR": "Appenzell Ausserrhoden",
    "BE": "Bern", "BL": "Basel-Landschaft", "BS": "Basel-Stadt", "FR": "Freiburg",
    "GE": "Genf", "GL": "Glarus", "GR": "Graubünden", "JU": "Jura", "LU": "Luzern",
    "NE": "Neuenburg", "NW": "Nidwalden", "OW": "Obwalden", "SG": "St. Gallen",
    "SH": "Schaffhausen", "SO": "Solothurn", "SZ": "Schwyz", "TG": "Thurgau",
    "TI": "Tessin", "UR": "Uri", "VD": "Waadt", "VS": "Wallis", "ZG": "Zug",
    "ZH": "Zürich",
}


# --------------------------------------------------------------------- helpers

def slug(s: str) -> str:
    # The umlaut expansion has to happen BEFORE normalising: NFKD decomposes ä into
    # a + combining diaeresis, so a .replace("ä", "ae") afterwards finds nothing and
    # every umlaut collapses to the bare vowel. That silently merged Stämpfli AG and
    # Stampfli AG — two different companies — onto one page, and gave every German
    # name the transliteration nobody uses (muller rather than mueller).
    s = (s or "").lower()
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:70] or "x"


def e(v) -> str:
    return html.escape(str(v)) if v is not None else ""


def chf(v) -> str:
    """Swiss thousands separator, the way the register writes figures."""
    return f"{v:,.0f}".replace(",", "’") if isinstance(v, (int, float)) and v else ""


def chf_big(v) -> str:
    """Headline sums only. A register writes figures in full, but 5’673’988’931 in a
    27px serif overflows its neighbour on a 375px screen, and an unreadable number
    states nothing. Detail pages keep the exact figure."""
    if not isinstance(v, (int, float)) or not v:
        return ""
    if v >= 1_000_000_000:
        # comma is the decimal mark in Swiss German; replace it in the number only,
        # or the abbreviation's full stop becomes "Mrd," too
        return f"{v / 1_000_000_000:.2f}".replace(".", ",") + " Mrd."
    if v >= 10_000_000:
        return f"{v / 1_000_000:.0f} Mio."
    return chf(v)


def plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def dmy(iso: str) -> str:
    """Short German date: 28.08 — day before month, unlike the ISO the source uses."""
    return f"{iso[8:10]}.{iso[5:7]}" if iso and len(iso) >= 10 else ""


def dmyy(iso: str) -> str:
    """Full German date: 09.10.2026."""
    return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}" if iso and len(iso) >= 10 else ""


def fit_title(text: str, suffix: str, limit: int = 64) -> str:
    """A title Google will not truncate: cut on a word boundary, keep the suffix."""
    room = limit - len(suffix)
    text = " ".join(text.split())
    if len(text) <= room:
        return text + suffix
    cut = text[:room]
    if " " in cut[max(0, room - 22):]:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip(" ,.;:-–—") + "…" + suffix


def zuschlag(n: int) -> str:
    one, many = lingue.PLURALS[LANG]
    return plural(n, one, many)


def de(row: dict, field: str) -> str:
    """German text where the publication carries a translation, else as published."""
    t = ((row.get("translations") or {}).get(field) or {})
    return (t.get("de") or row.get(field) or "").strip()


def winners(row: dict) -> list[str]:
    w = (row.get("winnerName") or "").strip()
    if not w:
        return []
    return [p.strip() for p in re.split(r"\s*;\s*|\s+/\s+|\n", w) if len(p.strip()) > 2]


def sig(code) -> str:
    """Significant digits of a CPV code: 45000000 -> '45' (a bucket, not a category)."""
    return str(code).rstrip("0") or str(code)[:2]


def load() -> tuple[list, list]:
    awards, seen = [], set()
    for f in sorted(DATI.glob("aggiudicazioni_*.json")):
        for a in json.loads(f.read_text()):
            k = a.get("publicationId") or a.get("publicationNumber")
            if k and k in seen:
                continue
            seen.add(k)
            awards.append(a)
    p = DATI / "gare_aperte.json"
    opens = [t for t in json.loads(p.read_text())
             if (t.get("offerDeadline") or "")[:10] >= TODAY] if p.exists() else []
    return awards, opens


# ------------------------------------------------------------------ the chrome

CSS = """
:root{
  --paper:oklch(99% .004 250); --ink:oklch(20% .018 250); --muted:oklch(50% .015 250);
  --rule:oklch(89% .008 250); --rule-strong:oklch(72% .012 250);
  --accent:oklch(46% .10 245); --signal:oklch(52% .10 62); --wash:oklch(97% .006 250);
}
@media (prefers-color-scheme:dark){:root{
  --paper:oklch(17% .015 250); --ink:oklch(93% .008 250); --muted:oklch(68% .015 250);
  --rule:oklch(29% .012 250); --rule-strong:oklch(42% .015 250);
  --accent:oklch(76% .10 245); --signal:oklch(78% .10 62); --wash:oklch(21% .014 250);
}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,-apple-system,sans-serif;font-size:15px;
  line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:0 28px 56px}
a{color:var(--accent);text-decoration:none;text-underline-offset:3px}
a:hover{text-decoration:underline}
a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums}
.num{font-variant-numeric:tabular-nums}
.eyebrow{font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--muted);
  font-weight:500;margin:0}
.masthead{display:flex;justify-content:space-between;align-items:baseline;gap:16px;
  padding:20px 0 14px;border-bottom:2px solid var(--ink);flex-wrap:wrap}
.masthead a.name{font-family:"Source Serif 4",Georgia,serif;font-weight:700;font-size:19px;
  letter-spacing:-.01em;color:var(--ink)}
.masthead a.name:hover{text-decoration:none;color:var(--accent)}
.runhead{display:flex;justify-content:space-between;gap:16px;padding:9px 0;
  border-bottom:1px solid var(--rule);font-size:11px;letter-spacing:.13em;
  text-transform:uppercase;color:var(--muted)}
h1{font-family:"Source Serif 4",Georgia,serif;font-weight:700;letter-spacing:-.021em;
  line-height:1.08;margin:0;text-wrap:balance;font-size:clamp(28px,4.4vw,42px)}
h2{font-family:"Source Serif 4",Georgia,serif;font-weight:600;font-size:19px;margin:0;
  letter-spacing:-.01em}
.title{display:grid;grid-template-columns:1fr 240px;gap:52px;align-items:start;
  padding:36px 0 26px;border-bottom:1px solid var(--rule-strong)}
.title p.sum{margin:14px 0 0;color:var(--muted);font-size:16px;max-width:54ch}
.rail{border-left:1px solid var(--rule);padding-left:20px;font-size:13px}
.rail dt{font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);
  margin-top:13px;font-weight:600}
.rail dt:first-child{margin-top:0}
.rail dd{margin:3px 0 0;font-size:14px}
.figures{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  border-bottom:1px solid var(--rule-strong)}
.fig{padding:20px 18px 18px 0;border-right:1px solid var(--rule)}
.fig:last-child{border-right:0}
.fig b{display:block;font-family:"Source Serif 4",Georgia,serif;font-weight:600;
  font-size:clamp(21px,4.6vw,27px);letter-spacing:-.02em;font-variant-numeric:tabular-nums;
  line-height:1;overflow-wrap:anywhere}
.fig span{display:block;margin-top:6px;font-size:11px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--muted)}
.sec{margin-top:34px}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse}
th{text-align:left;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);font-weight:600;padding:0 12px 7px 0;
  border-bottom:1px solid var(--rule-strong);white-space:nowrap}
td{padding:11px 12px 11px 0;border-bottom:1px solid var(--rule);vertical-align:top;
  font-size:14px}
td.r,th.r{text-align:right;padding-right:0}
td.sub,.sub{color:var(--muted);font-size:12.5px}
ul.plain{list-style:none;margin:0;padding:0}
ul.plain li{padding:11px 0;border-bottom:1px solid var(--rule)}
.row{display:flex;justify-content:space-between;gap:16px;align-items:baseline}
.when{color:var(--signal);font-size:12.5px;font-variant-numeric:tabular-nums;
  white-space:nowrap}
.tags{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}
.tag{border:1px solid var(--rule-strong);padding:4px 10px;font-size:12px;color:var(--ink);
  font-variant-numeric:tabular-nums}
.tag:hover{border-color:var(--accent);color:var(--accent);text-decoration:none}
.tag.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.state{display:inline-flex;align-items:center;gap:7px;font-size:11px;letter-spacing:.12em;
  text-transform:uppercase;font-weight:600;color:var(--signal)}
.state i{width:7px;height:7px;background:var(--signal);border-radius:50%;display:block}
.winner{border:1px solid var(--rule-strong);padding:18px 20px;margin:6px 0 0}
.winner .who{font-family:"Source Serif 4",Georgia,serif;font-size:21px;font-weight:600;
  letter-spacing:-.01em}
.official{margin-top:22px;padding:13px 15px;background:var(--wash);
  border-left:2px solid var(--accent);font-size:12.5px;color:var(--muted)}
.prose p{margin:0 0 14px;font-size:15px;line-height:1.65;max-width:64ch}
.bar{display:block;height:3px;background:var(--accent);margin-top:6px;opacity:.7}
.fig-chart{margin:14px 0 0;padding:0}
.fig-chart svg{max-width:100%}
.fig-cap{margin-top:9px;font-size:12px;color:var(--muted);max-width:66ch}
.figs{display:grid;gap:26px;margin-top:4px}
.cols{display:grid;grid-template-columns:1fr 300px;gap:54px;padding-top:32px;
  align-items:start}
.half{display:grid;grid-template-columns:1fr 1fr;gap:54px;padding-top:32px;align-items:start}
.langs{display:flex;gap:14px;padding:10px 0 0;font-size:12.5px;justify-content:flex-end}
.langs .on{color:var(--muted)}
footer{border-top:1px solid var(--rule);margin-top:44px;padding-top:16px;
  color:var(--muted);font-size:12.5px}
footer p{margin:0 0 6px;max-width:78ch}
@media(max-width:860px){
  .title,.cols,.half{grid-template-columns:1fr;gap:26px}
  .rail{border-left:0;border-top:1px solid var(--rule);padding:16px 0 0}
  .fig{border-right:0;border-bottom:1px solid var(--rule)}
}
"""

HEAD = """<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{site}{path}">
{alts}
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&amp;family=IBM+Plex+Sans:wght@400;500;600&amp;family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&amp;display=swap">
<link rel="stylesheet" href="{base}/style.css">
{verify}</head><body>
<div class="wrap">
<div class="masthead"><a class="name" href="{base}/{lang}/">{sitename}</a>
<span class="eyebrow">{kicker}</span></div>
<nav class="langs" aria-label="{langlabel}">{langnav}</nav>
"""

FOOT = """<footer><p>{disc}</p>
<p>{srcnote}</p>
<p>{source}: <a href="https://www.simap.ch">simap.ch</a> — {official}. {asof} {today}.</p>
</footer></div></body></html>"""


SECTIONS = {"unternehmen": "companies", "auftraggeber": "buyers",
            "kanton": "cantons", "bereich": "sectors", "auftrag": "contracts",
            "ausschreibungen": "tenders"}

# Sections that actually have an index page. /auftrag/ deliberately has none — 14,987
# awards do not belong in one alphabetical list, and the sitemap already carries them —
# so a breadcrumb must not claim that level: it would point at a 404 and Google reads
# breadcrumbs as a promise about the site's shape.
INDEXED = {"unternehmen", "auftraggeber", "kanton", "bereich", "ausschreibungen"}


def breadcrumbs(path: str, leaf: str) -> str:
    """Schema.org trail, so a result shows Register > Unternehmen > HOLINGER AG rather
    than a bare URL. Only claims the structure the site actually has."""
    parts = [x for x in path.strip("/").split("/") if x]
    if parts and parts[0] in LANGS:
        parts = parts[1:]
    crumbs = [{"@type": "ListItem", "position": 1, "name": _.register,
               "item": f"{ORIGIN}/{LANG}/"}]
    if parts:
        sec = parts[0]
        pos = 2
        if sec in INDEXED:
            crumbs.append({"@type": "ListItem", "position": pos,
                           "name": lingue.t(SECTIONS.get(sec, "register"), LANG),
                           "item": f"{ORIGIN}/{LANG}/{sec}/"})
            pos += 1
        if len(parts) > 1:
            crumbs.append({"@type": "ListItem", "position": pos, "name": leaf,
                           "item": ORIGIN + path})
    return ('<script type="application/ld+json">'
            + json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                          "itemListElement": crumbs}, ensure_ascii=False)
            + "</script>")


def lang_path(path: str, lang: str) -> str:
    """The same page in another language: only the language segment changes."""
    parts = [x for x in path.strip("/").split("/") if x]
    if parts and parts[0] in LANGS:
        parts[0] = lang
    else:
        parts = [lang] + parts
    return "/" + "/".join(parts) + "/"


def page(title: str, desc: str, body: str, path: str, kicker: str = "",
         leaf: str = "") -> str:
    # hreflang tells the search engine these are one page in four languages, not four
    # pages competing with each other for the same query.
    alts = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{ORIGIN}{lang_path(path, l)}">'
        for l in LANGS) + f'\n<link rel="alternate" hreflang="x-default" href="{ORIGIN}/">'
    nav = "".join(
        (f'<span class="on">{e(NAMES[l])}</span>' if l == LANG
         else f'<a href="{BASE}{lang_path(path, l)}">{e(NAMES[l])}</a>') for l in LANGS)
    return (HEAD.format(title=e(title), desc=e(desc), site=ORIGIN, base=BASE, path=path,
                        kicker=e(kicker or _.register), lang=LANG, alts=alts,
                        verify=VERIFY,
                        sitename=e(_.site), langnav=nav, langlabel=e(_.language))
            + breadcrumbs(path, leaf or title.split(" — ")[0])
            + body + FOOT.format(disc=e(DISCLAIMER), today=TODAY,
                                 srcnote=e(_p.translation_note), source=e(_.source),
                                 asof=e(_.as_of), official=e(_p.source_note)))


def write(path: str, content: str) -> None:
    f = OUT / path.lstrip("/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")


# --------------------------------------------------------------- the analysis

def profile(awards: list) -> dict:
    """One record per company, built only from what the publications actually say.

    Keyed by SLUG, not by the raw name: the register spells the same firm several ways
    ("CSD INGENIEURE AG" and "CSD Ingenieure AG", "Bolliger & Co. AG" and
    "Bolliger + Co. AG"), and keying by name made each variant its own company writing
    to the same file — so the second silently overwrote the first and half that firm's
    awards vanished from its page. The spelling shown is the one the register uses most
    often for that firm.
    """
    comp = {}
    variants: dict[str, collections.Counter] = {}
    for a in awards:
        ws = winners(a)
        for raw in ws:
            n = slug(raw)
            variants.setdefault(n, collections.Counter())[raw] += 1
            c = comp.setdefault(n, {"awards": [], "value": 0.0, "amounts": [],
                                    "cpv": collections.Counter(), "cant": collections.Counter(),
                                    "buyers": collections.Counter(), "sig": set()})
            c["awards"].append(a)
            p = a.get("winnerPrice")
            # a joint award names several firms for one price; splitting it would
            # invent a figure the register never published
            if isinstance(p, (int, float)) and p and len(ws) == 1:
                c["value"] += p
                c["amounts"].append(p)
            if a.get("cpvCode"):
                c["cpv"][(str(a["cpvCode"]), de(a, "cpvLabel") or a.get("cpvLabel") or "")] += 1
                c["sig"].add(sig(a["cpvCode"]))
            if a.get("canton"):
                c["cant"][a["canton"]] += 1
            if a.get("buyerName"):
                c["buyers"][a["buyerName"]] += 1
    for n, c in comp.items():
        c["name"] = variants[n].most_common(1)[0][0]
    return comp


def matches(comp: dict, opens: list) -> dict:
    """Open tenders that match a company's own record.

    Weighted by how specific the CPV code is: 45000000 "Bauarbeiten" is not a category
    but the absence of one, so matching on it offers a cabling firm a football pitch.
    Four significant digits in common is the floor.
    """
    out = {}
    for name, c in comp.items():
        scored = []
        for t in opens:
            if not t.get("cpvCode"):
                continue
            ts, best = sig(t["cpvCode"]), 0
            for cs in c["sig"]:
                k = 0
                while k < min(len(cs), len(ts)) and cs[k] == ts[k]:
                    k += 1
                best = max(best, k)
            if best >= 4:
                scored.append((best + (1 if t.get("canton") in c["cant"] else 0), t))
        if scored:
            out[name] = [t for _, t in sorted(scored, key=lambda x: -x[0])[:6]]
    return out


def per_month(rows: list) -> dict:
    """Publication counts by month — the dimension the tables do not carry."""
    c = collections.Counter((r.get("publicationDate") or "")[:7] for r in rows
                            if (r.get("publicationDate") or "")[:7])
    if not c:
        return {}
    keys = sorted(c)
    # fill the gaps: a month with no awards is a fact, and leaving it out would
    # squeeze the axis and quietly imply activity that was not there
    out, y, m = {}, int(keys[0][:4]), int(keys[0][5:7])
    ly, lm = int(keys[-1][:4]), int(keys[-1][5:7])
    while (y, m) <= (ly, lm):
        out[f"{y:04d}-{m:02d}"] = c.get(f"{y:04d}-{m:02d}", 0)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def median(xs: list) -> float:
    xs = sorted(xs)
    if not xs:
        return 0.0
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


# ---------------------------------------------------------------- company page

def sector_pages(awards: list, floor: int = 3) -> set[str]:
    """Which CPV codes get their own page. Computed before anything links to one:
    linking to a page the build never writes is a 404 for the reader and a wasted
    crawl for the search engine."""
    n = collections.Counter(str(a["cpvCode"]) for a in awards if a.get("cpvCode"))
    return {c for c, k in n.items() if k >= floor}


def peers(comp: dict, keep: set[str]) -> dict:
    """Companies that bid for the same work in the same place.

    Useful to the reader — a procurement officer or a competitor comparing bidders —
    and it links leaf pages to each other, which is how a crawler reaches the deep
    ones. Grouped on the SIGNIFICANT CPV digits, so 45000000 does not put every
    builder in the country in the same group.
    """
    groups = collections.defaultdict(list)
    for name, c in comp.items():
        if name not in keep or not c["cpv"]:
            continue
        code = sig(c["cpv"].most_common(1)[0][0][0])[:4]
        cant = c["cant"].most_common(1)[0][0] if c["cant"] else ""
        groups[(code, cant)].append(name)
    out = {}
    for (code, cant), names in groups.items():
        if len(names) < 2:
            continue
        ranked = sorted(names, key=lambda n: -len(comp[n]["awards"]))
        for n in names:
            others = [x for x in ranked if x != n][:6]
            if others:
                out[n] = (others, cant)
    return out


def build_companies(comp: dict, open_for: dict, sectors: set[str],
                    buyer_slugs: set[str], peer_map: dict) -> dict:
    pages = {}
    for s, c in comp.items():
        rows = sorted(c["awards"], key=lambda a: a.get("publicationDate") or "", reverse=True)
        if len(rows) < MIN_AWARDS:
            continue
        name = c["name"]
        years = sorted({(a.get("publicationDate") or "")[:7] for a in rows if a.get("publicationDate")})
        span = ""
        if years:
            fmt = lambda y: f"{y[5:7]}/{y[:4]}"
            span = fmt(years[0]) if len(years) == 1 else f"{fmt(years[0])} – {fmt(years[-1])}"
        sector = c["cpv"].most_common(1)[0][0][1] if c["cpv"] else ""
        cants = [k for k, _ in c["cant"].most_common(4)]

        b = [f'<div class="title"><div><p class="eyebrow">'
             + " · ".join(x for x in (sector[:44], CANTONS.get(cants[0], cants[0]) if cants else "") if x)
             + f'</p><h1>{e(name)}</h1>'
             f'<p class="sum">' + e(_m("company_lead", n=zuschlag(len(rows)),
                                       span=(f", {span}" if span else ""),
                                       b=_m("buyers_count", k=len(c["buyers"]))))
             + '</p></div><dl class="rail">']
        if sector:
            b.append(f"<dt>{_.main_sector}</dt><dd>{e(sector)}</dd>")
        if c["cpv"]:
            b.append(f'<dt>CPV</dt><dd class="mono">{e(c["cpv"].most_common(1)[0][0][0])}</dd>')
        if cants:
            b.append(f"<dt>{_.cantons}</dt><dd>" + " · ".join(e(x) for x in cants) + "</dd>")
        b.append("</dl></div>")

        b.append('<div class="figures">')
        b.append(f'<div class="fig"><b>{len(rows)}</b><span>{_.awards}</span></div>')
        if c["value"]:
            b.append(f'<div class="fig"><b>{chf(c["value"])}</b><span>{_.sum}</span></div>')
        b.append(f'<div class="fig"><b>{len(c["buyers"])}</b><span>{_.buyers}</span></div>')
        if len(c["amounts"]) > 1:
            b.append(f'<div class="fig"><b>{chf(median(c["amounts"]))}</b><span>{_.median}</span></div>')
        b.append("</div>")

        tl = grafici.timeline(rows, _p.chart_timeline, _p.chart_timeline_cap, chf)
        if tl:
            b.append(f'<div class="sec"><div class="runhead">'
                     f'<span>{_p.chart_timeline}</span><span>{len(rows)}</span></div>{tl}</div>')
        b.append(f'<div class="sec"><div class="runhead"><span>{_.awards}</span>'
                 f'<span>{_.chronological}</span></div><div class="scroll"><table><thead><tr>'
                 f'<th style="width:96px">{_.date}</th><th>{_.contract}</th><th>{_.buyer}</th>'
                 f'<th style="width:44px">{_.canton_abbr}</th><th class="r">{_.amount}</th>'
                 "</tr></thead><tbody>")
        for a in rows:
            b.append(
                f'<tr><td class="mono" style="font-size:12.5px">{e((a.get("publicationDate") or "")[:10])}</td>'
                f'<td><a href="{BASE}/{LANG}/auftrag/{e(a.get("projectId"))}/">{e(de(a, "title")[:130])}</a></td>'
                f'<td>{e(a.get("buyerName"))}</td><td>{e(a.get("canton"))}</td>'
                f'<td class="r num">{e(chf(a.get("winnerPrice")))}</td></tr>')
        b.append("</tbody></table></div></div>")

        m = open_for.get(s, [])
        if m:
            b.append('<div class="sec"><div class="runhead"><span>Offene Ausschreibungen '
                     f'im selben Bereich</span><span>{len(m)}</span></div>'
                     '<p class="sub" style="margin:10px 0 0">Laufende Ausschreibungen, deren '
                     "CPV-Code den bisherigen Zuschlägen dieses Unternehmens entspricht.</p>"
                     '<ul class="plain" style="margin-top:10px">')
            for t in m:
                b.append(f'<li><div class="row"><div><a href="{BASE}/{LANG}/auftrag/{e(t.get("projectId"))}/">'
                         f'{e(de(t, "title")[:120])}</a><span class="sub" style="display:block;'
                         f'margin-top:3px">{e(t.get("buyerName"))} · {e(t.get("canton"))} · '
                         f'{e(de(t, "cpvLabel") or t.get("cpvLabel") or "")[:44]}</span></div>'
                         f'<span class="when">bis {e(dmyy(t.get("offerDeadline") or ""))}</span>'
                         "</div></li>")
            b.append("</ul></div>")

        if c["cpv"]:
            b.append(f'<div class="sec"><div class="runhead"><span>{_.activities}</span>'
                     f'<span>{len(c["cpv"])}</span></div><ul class="plain">')
            for (code, label), k in c["cpv"].most_common(8):
                cell = (f'<a href="{BASE}/{LANG}/bereich/{e(code)}/">{e(label)}</a>' if code in sectors
                        else e(label))
                b.append(f'<li><div class="row">{cell}'
                         f'<span class="sub num">{zuschlag(k)}</span></div></li>')
            b.append("</ul></div>")

        if c["buyers"]:
            b.append(f'<div class="sec"><div class="runhead"><span>{_.buyers}</span>'
                     f'<span>{len(c["buyers"])}</span></div><div class="tags">')
            for bu, k in c["buyers"].most_common(12):
                sl = slug(bu)
                b.append(f'<a class="tag" href="{BASE}/{LANG}/auftraggeber/{e(sl)}/">{e(bu[:52])} · {k}</a>'
                         if sl in buyer_slugs else f'<span class="tag">{e(bu[:52])} · {k}</span>')
            b.append("</div></div>")

        pr = peer_map.get(s)
        if pr:
            others, cant = pr
            b.append('<div class="sec"><div class="runhead"><span>Weitere Anbieter im '
                     f'selben Bereich</span><span>{e(CANTONS.get(cant, cant))}</span></div>'
                     '<ul class="plain">')
            for o in others:
                oc = comp[o]
                b.append(f'<li><div class="row"><a href="{BASE}/{LANG}/unternehmen/{e(o)}/">{e(oc["name"])}</a>'
                         f'<span class="sub num">{zuschlag(len(oc["awards"]))}</span></div></li>')
            b.append("</ul></div>")

        desc = _m("company_desc", name=name, n=zuschlag(len(rows)),
                  val=(f", {chf(c['value'])} CHF" if c["value"] else ""),
                  span=(f", {span}" if span else ""))
        pages[s] = {"name": name, "n": len(rows), "value": c["value"],
                    "cant": cants[0] if cants else "", "sector": sector}
        write(f"/{LANG}/unternehmen/{s}/index.html",
              page(fit_title(name, _m("company_title")), desc[:180],
                   "\n".join(b), f"/{LANG}/unternehmen/{s}/", _.companies))
    return pages


# ----------------------------------------------------------------- award page

def build_awards(awards: list, opens: list, pages: dict, sectors: set[str],
                 buyer_slugs: set[str]) -> int:
    by_project = {}
    for a in awards:
        by_project.setdefault(a.get("projectId"), {})["award"] = a
    for t in opens:
        by_project.setdefault(t.get("projectId"), {})["open"] = t
    n = 0
    for pid, rec in by_project.items():
        if not pid:
            continue
        src = rec.get("open") or rec.get("award")
        aw = rec.get("award")
        title = de(src, "title")
        if not title:
            continue
        is_open = "open" in rec
        award = (aw or {}).get("award") or {}

        b = [f'<div class="title"><div><span class="state"><i></i>'
             + (_.tender_open if is_open else _.award_granted)
             + f'</span><h1 style="margin-top:12px;font-size:clamp(24px,3.4vw,34px)">'
             f'{e(title)}</h1></div><dl class="rail">']
        if src.get("publicationNumber"):
            b.append(f'<dt>{_.publication}</dt><dd class="mono">{e(src["publicationNumber"])}</dd>')
        if src.get("publicationDate"):
            b.append(f'<dt>{_.published_on}</dt><dd class="mono">{e(src["publicationDate"][:10])}</dd>')
        if src.get("processType"):
            b.append(f"<dt>{_.procedure}</dt><dd>{e(src['processType'])}</dd>")
        b.append("</dl></div>")

        figs = []
        if is_open and src.get("offerDeadline"):
            figs.append(f'<div class="fig"><b>{e(src["offerDeadline"][:10])}</b>'
                        f"<span>{_.deadline}</span></div>")
        if aw and aw.get("winnerPrice"):
            figs.append(f'<div class="fig"><b>{chf(aw["winnerPrice"])}</b>'
                        f"<span>{_.sum}</span></div>")
        if award.get("numberOfSubmissions"):
            figs.append(f'<div class="fig"><b>{e(award["numberOfSubmissions"])}</b>'
                        f"<span>{_.offers}</span></div>")
        if src.get("canton"):
            figs.append(f'<div class="fig"><b>{e(src["canton"])}</b><span>{_.canton}</span></div>')
        if figs:
            b.append('<div class="figures">' + "".join(figs) + "</div>")

        b.append('<div class="cols"><div class="prose">')
        ws = winners(aw) if aw else []
        if ws:
            b.append(f'<div class="runhead"><span>{_.award}</span>'
                     f'<span>{plural(len(ws), "Anbieter", "Anbieter")}</span></div>')
            for w in ws:
                s = slug(w)
                known = pages.get(s)
                link = (f'<a href="{BASE}/{LANG}/unternehmen/{e(s)}/" class="who">{e(w)}</a>'
                        if known else f'<span class="who">{e(w)}</span>')
                extra = []
                if aw.get("winnerPrice") and len(ws) == 1:
                    extra.append(f'{chf(aw["winnerPrice"])} CHF')
                if known:
                    extra.append(f'{zuschlag(known["n"])} im Register')
                b.append(f'<div class="winner">{link}'
                         + (f'<div class="sub" style="margin-top:5px">' + " · ".join(extra)
                            + "</div>" if extra else "") + "</div>")
        if award.get("justification"):
            b.append(f'<h2 style="margin:34px 0 12px">{_.reason}</h2><p>'
                     + e(award["justification"][:1500]) + "</p>")
        body_txt = de(src, "description")
        if body_txt:
            b.append(f'<h2 style="margin:30px 0 12px">{_.description}</h2><p>'
                     + e(body_txt[:1600]) + "</p>")
        if src.get("simapUrl"):
            b.append(f'<div class="official">Amtliche Publikation: '
                     f'<a href="{e(src["simapUrl"])}">Projekt {e(src.get("projectNumber") or "")} '
                     "auf simap.ch ansehen</a> — massgebend ist ausschliesslich die dortige "
                     "Veröffentlichung.</div>")
        b.append("</div><div>")

        b.append(f'<div class="runhead"><span>{_.details}</span><span></span></div>'
                 '<div class="scroll"><table><tbody>')
        cpv = f'<span class="mono">{e(src.get("cpvCode") or "")}</span>' + (
            "<br>" + e(de(src, "cpvLabel") or src.get("cpvLabel") or "")
            if (src.get("cpvLabel") or de(src, "cpvLabel")) else "")
        bslug = slug(src.get("buyerName") or "")
        buyer_cell = (f'<a href="{BASE}/{LANG}/auftraggeber/{e(bslug)}/">{e(src.get("buyerName"))}</a>'
                      if bslug in buyer_slugs else e(src.get("buyerName")))
        for label, val in [(_.buyer, buyer_cell if src.get("buyerName") else ""),
                           (_.place, e(src.get("city"))),
                           (_.canton, e(CANTONS.get(src.get("canton"), src.get("canton") or ""))),
                           (_.type, e(src.get("orderType"))),
                           ("CPV", cpv if src.get("cpvCode") else ""),
                           (_.treaty, e(src.get("stateContractArea")))]:
            if val:
                b.append(f'<tr><th style="width:112px;text-transform:none;letter-spacing:0;'
                         f'font-size:13px;font-weight:500;border-bottom:1px solid var(--rule);'
                         f'padding:9px 12px 9px 0">{label}</th><td>{val}</td></tr>')
        b.append("</tbody></table></div>")
        links = []
        if src.get("canton"):
            links.append(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(src["canton"])}/">'
                         f'{e(_if("contracts_in", c=src["canton"]))}</a>')
        if str(src.get("cpvCode") or "") in sectors:
            links.append(f'<a class="tag" href="{BASE}/{LANG}/bereich/{e(src["cpvCode"])}/">{e(_i.same_sector)}</a>')
        if links:
            b.append('<div class="tags">' + "".join(links) + "</div>")
        b.append("</div></div>")

        desc = f"{title[:110]} — {src.get('buyerName') or ''}"
        if is_open and src.get("offerDeadline"):
            desc += f", Eingabefrist {src['offerDeadline'][:10]}"
        elif aw and aw.get("winnerPrice"):
            desc += f", Zuschlag {chf(aw['winnerPrice'])} CHF" + (f" an {ws[0]}" if ws else "")
        write(f"/{LANG}/auftrag/{pid}/index.html",
              page(fit_title(title, _m("tender_suffix") if is_open else _m("award_suffix")),
                   desc[:180], "\n".join(b), f"/{LANG}/auftrag/{pid}/",
                   "Ausschreibung" if is_open else "Zuschlag"))
        n += 1
    return n


# ------------------------------------------------------------------ buyer page

def build_buyers(awards: list, comp: dict, pages: dict, sectors: set[str],
                 floor: int = 3) -> list:
    """A page per contracting authority. "Welche Aufträge hat die Gemeinde X
    vergeben" is a proper-name search with a real reader behind it — a resident, a
    journalist, a competitor — and no site answers it today."""
    by = collections.defaultdict(list)
    for a in awards:
        if a.get("buyerName"):
            by[a["buyerName"]].append(a)
    out = []
    for name, rows in sorted(by.items(), key=lambda kv: -len(kv[1])):
        if len(rows) < floor:
            continue
        sl = slug(name)
        total = sum(a.get("winnerPrice") or 0 for a in rows
                    if isinstance(a.get("winnerPrice"), (int, float)))
        table, nfirms = firm_table(rows, comp, pages, limit=40)
        cants = collections.Counter(a["canton"] for a in rows if a.get("canton"))
        sect = collections.Counter(
            (de(a, "cpvLabel") or a.get("cpvLabel") or "", str(a.get("cpvCode") or ""))
            for a in rows if a.get("cpvCode"))
        cant = cants.most_common(1)[0][0] if cants else ""
        b = [f'<div class="title"><div><p class="eyebrow">Auftraggeber'
             + (f" · {e(CANTONS.get(cant, cant))}" if cant else "") + f'</p><h1>{e(name)}</h1>'
             f'<p class="sum">' + e(_m("buyer_lead", n=zuschlag(len(rows)), f=nfirms))
             + '</p></div><dl class="rail">'
             + (f"<dt>{_.canton}</dt><dd>{e(cant)}</dd>" if cant else "")
             + f"<dt>{_.companies}</dt><dd>{nfirms}</dd></dl></div>",
             '<div class="figures">',
             f'<div class="fig"><b>{len(rows)}</b><span>{_.awards}</span></div>',
             f'<div class="fig"><b>{nfirms}</b><span>{_.companies}</span></div>']
        if total:
            b.append(f'<div class="fig"><b>{chf_big(total)}</b><span>{_.sum}</span></div>')
        b.append("</div>")
        b.append(f'<div class="half"><div><div class="runhead"><span>{_.companies}</span>'
                 f'<span>{_.by_awards}</span></div>' + table + "</div><div>")
        b.append(f'<div class="runhead"><span>{_.sectors}</span><span>CPV</span></div>'
                 '<ul class="plain">')
        top = sect.most_common(1)[0][1] if sect else 1
        for (label, code), k in sect.most_common(8):
            cell = (f'<a href="{BASE}/{LANG}/bereich/{e(code)}/">{e(label[:48])}</a>' if code in sectors
                    else e(label[:48]))
            b.append(f'<li><div class="row">{cell}<span class="sub num">{k}</span></div>'
                     f'<span class="bar" style="width:{max(4, round(k / top * 100))}%"></span></li>')
        b.append("</ul></div></div>")
        b.append(f'<div class="sec"><div class="runhead"><span>{_.awards}</span>'
                 f"<span>{_.chronological}</span></div><div class=\"scroll\"><table><thead><tr>"
                 f'<th style="width:96px">{_.date}</th><th>{_.contract}</th><th>{_.award}</th>'
                 '<th class="r">Betrag CHF</th></tr></thead><tbody>')
        for a in sorted(rows, key=lambda x: x.get("publicationDate") or "", reverse=True)[:60]:
            ws = winners(a)
            who = " · ".join(
                (f'<a href="{BASE}/{LANG}/unternehmen/{e(slug(w))}/">{e(w)}</a>'
                 if slug(w) in pages else e(w)) for w in ws) or "—"
            b.append(f'<tr><td class="mono" style="font-size:12.5px">'
                     f'{e((a.get("publicationDate") or "")[:10])}</td>'
                     f'<td><a href="{BASE}/{LANG}/auftrag/{e(a.get("projectId"))}/">{e(de(a, "title")[:110])}</a></td>'
                     f"<td>{who}</td><td class=\"r num\">{e(chf(a.get('winnerPrice')))}</td></tr>")
        b.append("</tbody></table></div></div>")
        write(f"/{LANG}/auftraggeber/{sl}/index.html",
              page(fit_title(name, _m("buyer_title")),
                   _m("buyer_desc", name=name, n=zuschlag(len(rows)), f=nfirms),
                   "\n".join(b), f"/{LANG}/auftraggeber/{sl}/", _.buyers))
        out.append((sl, name, len(rows)))
    return out


# ------------------------------------------------------------------- the hubs

def firm_table(rows: list, comp: dict, pages: dict, limit: int = 60) -> str:
    """Companies ranked within THESE rows.

    The sum is computed from the rows passed in, never from the company's global
    total: on a buyer's page the column reads as "what this authority awarded them",
    and a global figure there states something the register never published.
    """
    # Counted by slug, not by spelling: the register writes the same firm several
    # ways, and counting the strings put it in the table twice with its awards split.
    firms = collections.Counter()
    sums: dict[str, float] = collections.defaultdict(float)
    seen_name: dict[str, str] = {}
    for r in rows:
        ws = winners(r)
        for w in ws:
            k = slug(w)
            firms[k] += 1
            seen_name.setdefault(k, w)
            p = r.get("winnerPrice")
            if isinstance(p, (int, float)) and p and len(ws) == 1:
                sums[k] += p
    out = [f'<div class="scroll"><table><thead><tr><th>{_.companies}</th>'
           f'<th class="r">{_.awards}</th><th class="r">{_.sum}</th></tr></thead><tbody>']
    for sl, k in firms.most_common(limit):
        label = (comp.get(sl) or {}).get("name") or seen_name.get(sl, sl)
        cell = (f'<a href="{BASE}/{LANG}/unternehmen/{e(sl)}/">{e(label)}</a>'
                if sl in pages else e(label))
        out.append(f'<tr><td>{cell}</td><td class="r num">{k}</td>'
                   f'<td class="r num">{e(chf(sums.get(sl, 0)))}</td></tr>')
    out.append("</tbody></table></div>")
    return "\n".join(out), len(firms)


def build_hubs(awards: list, comp: dict, pages: dict, sectors: set[str]) -> tuple[list, list]:
    by_cant, by_cpv = collections.defaultdict(list), collections.defaultdict(list)
    for a in awards:
        if a.get("canton"):
            by_cant[a["canton"]].append(a)
        if a.get("cpvCode"):
            by_cpv[str(a["cpvCode"])].append(a)

    cant_list = sorted(by_cant.items(), key=lambda kv: -len(kv[1]))
    nav = '<div class="tags" style="margin-top:26px;padding-top:22px;border-top:1px solid var(--rule)">' \
          + "".join(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(c)}/">{e(c)} {len(r)}</a>'
                    for c, r in cant_list) + "</div>"

    for code, rows in cant_list:
        name = CANTONS.get(code, code)
        table, nfirms = firm_table(rows, comp, pages)
        total = sum(a.get("winnerPrice") or 0 for a in rows
                    if isinstance(a.get("winnerPrice"), (int, float)))
        sect = collections.Counter(
            (de(a, "cpvLabel") or a.get("cpvLabel") or "", str(a.get("cpvCode") or ""))
            for a in rows if a.get("cpvCode"))
        top = sect.most_common(1)[0][1] if sect else 1
        b = [f'<div class="title"><div><p class="eyebrow">Kanton</p><h1>{e(name)}</h1>'
             f'<p class="sum">' + e(_m("canton_lead", n=zuschlag(len(rows)), f=nfirms))
             + "</p></div>"
             f'<dl class="rail"><dt>Kürzel</dt><dd class="mono">{e(code)}</dd>'
             f'<dt>{_.buyers}</dt><dd>{len({a.get("buyerName") for a in rows})}</dd></dl></div>',
             '<div class="figures">',
             f'<div class="fig"><b>{len(rows)}</b><span>{_.awards}</span></div>',
             f'<div class="fig"><b>{nfirms}</b><span>{_.companies}</span></div>']
        if total:
            b.append(f'<div class="fig"><b>{chf_big(total)}</b><span>{_.sum}</span></div>')
        b.append("</div>")
        b.append(f'<div class="half"><div><div class="runhead"><span>{_.companies}</span>'
                 f"<span>{_.by_awards}</span></div>" + table + "</div>")
        b.append(f'<div><div class="runhead"><span>{_.sectors}</span><span>CPV</span></div>'
                 '<ul class="plain">')
        for (label, code2), k in sect.most_common(10):
            cell = (f'<a href="{BASE}/{LANG}/bereich/{e(code2)}/">{e(label[:52])}</a>' if code2 in sectors
                    else e(label[:52]))
            b.append(f'<li><div class="row">{cell}<span class="sub num">{k}</span></div>'
                     f'<span class="bar" style="width:{max(4, round(k / top * 100))}%"></span></li>')
        b.append("</ul></div></div>")
        col = grafici.columns(per_month(rows), _p.chart_months, _p.chart_months_cap)
        if col:
            b.append(f'<div class="sec"><div class="runhead"><span>{_p.chart_months}</span>'
                     f'<span>{len(rows)}</span></div>{col}</div>')
        b.append(nav)
        write(f"/{LANG}/kanton/{code}/index.html",
              page(fit_title(_m("canton_title", name=name), _m("canton_suffix")),
                   _m("canton_desc", n=zuschlag(len(rows)), name=name, f=nfirms),
                   "\n".join(b), f"/{LANG}/kanton/{code}/", _.canton))

    cpv_list = [(c, r) for c, r in sorted(by_cpv.items(), key=lambda kv: -len(kv[1]))
                if c in sectors]
    for code, rows in cpv_list:
        label = next((de(a, "cpvLabel") or a.get("cpvLabel") for a in rows
                      if de(a, "cpvLabel") or a.get("cpvLabel")), code)
        table, nfirms = firm_table(rows, comp, pages)
        cants = collections.Counter(a["canton"] for a in rows if a.get("canton"))
        b = [f'<div class="title"><div><p class="eyebrow">Bereich · CPV {e(code)}</p>'
             f'<h1>{e(label)}</h1><p class="sum">'
             + e(_m("sector_lead", n=zuschlag(len(rows)), f=nfirms)) + "</p></div>"
             f'<dl class="rail"><dt>CPV</dt><dd class="mono">{e(code)}</dd>'
             f'<dt>{_.cantons}</dt><dd>{len(cants)}</dd></dl></div>',
             '<div class="figures">',
             f'<div class="fig"><b>{len(rows)}</b><span>{_.awards}</span></div>',
             f'<div class="fig"><b>{nfirms}</b><span>{_.companies}</span></div>',
             f'<div class="fig"><b>{len(cants)}</b><span>{_.cantons}</span></div></div>',
             f'<div class="sec"><div class="runhead"><span>{_.companies}</span>'
             f"<span>{_.by_awards}</span></div>" + table + "</div>",
             (lambda g: f'<div class="sec"><div class="runhead">'
                        f'<span>{_p.chart_months}</span><span>{len(rows)}</span></div>'
                        f'{g}</div>' if g else "")(
                 grafici.columns(per_month(rows), _p.chart_months, _p.chart_months_cap)),
             '<div class="tags" style="margin-top:24px">'
             + "".join(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(c)}/">{e(c)} {k}</a>'
                       for c, k in cants.most_common(14)) + "</div>"]
        write(f"/{LANG}/bereich/{code}/index.html",
              page(fit_title(label, _m("sector_suffix", code=code)),
                   _m("sector_desc", n=zuschlag(len(rows)), label=label, f=nfirms),
                   "\n".join(b), f"/{LANG}/bereich/{code}/", _.sectors))
    return cant_list, cpv_list


# ------------------------------------------------------------- open tenders

def build_open(opens: list, sectors: set[str], buyer_slugs: set[str]) -> int:
    """The open tenders, whole and by canton.

    This is the part with intent behind it: someone searching for current tenders is
    looking to bid, not to browse. The pages carry the deadline first, because that is
    the fact that decides whether the rest matters.
    """
    def table(rows: list) -> str:
        out = ['<div class="scroll"><table><thead><tr><th style="width:104px">Eingabefrist</th>'
               '<th>Ausschreibung</th><th>Auftraggeber</th><th style="width:44px">Kt.</th>'
               "</tr></thead><tbody>"]
        for t in sorted(rows, key=lambda x: x.get("offerDeadline") or "9999"):
            out.append(
                f'<tr><td class="when mono" style="font-size:12.5px">'
                f'{e(dmyy(t.get("offerDeadline") or ""))}</td>'
                f'<td><a href="{BASE}/{LANG}/auftrag/{e(t.get("projectId"))}/">{e(de(t, "title")[:120])}</a>'
                + (f'<span class="sub" style="display:block;margin-top:2px">'
                   f'{e((de(t, "cpvLabel") or t.get("cpvLabel") or "")[:60])}</span>'
                   if (t.get("cpvLabel") or de(t, "cpvLabel")) else "")
                + f'</td><td>{e(t.get("buyerName"))}</td><td>{e(t.get("canton"))}</td></tr>')
        out.append("</tbody></table></div>")
        return "\n".join(out)

    by_cant = collections.defaultdict(list)
    for t in opens:
        if t.get("canton"):
            by_cant[t["canton"]].append(t)
    nav = ('<div class="tags" style="margin-top:26px;padding-top:22px;'
           'border-top:1px solid var(--rule)">'
           + "".join(f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/{e(c)}/">{e(c)} {len(r)}</a>'
                     for c, r in sorted(by_cant.items(), key=lambda kv: -len(kv[1])))
           + "</div>")

    b = [f'<div class="title"><div><p class="eyebrow">Laufend</p>'
         f"<h1>{e(_p.open_tenders_h1)}</h1>"
         f'<p class="sum">' + e(_m("open_lead", n=len(opens))) + "</p></div>"
         f'<dl class="rail"><dt>{_.as_of}</dt><dd class="mono">{TODAY}</dd>'
         f"<dt>{_.cantons}</dt><dd>{len(by_cant)}</dd></dl></div>",
         '<div class="sec">' + table(opens[:400]) + "</div>",
         (f'<p class="sub" style="margin:12px 0 0">'
          + e(_m("open_truncated", shown=400, total=len(opens))) + "</p>"
          if len(opens) > 400 else ""),
         nav]
    write(f"/{LANG}/ausschreibungen/index.html", page(
        _m("open_title"), _m("open_desc", n=len(opens)),
        "\n".join(b), f"/{LANG}/ausschreibungen/", _.tenders))

    for code, rows in by_cant.items():
        name = CANTONS.get(code, code)
        b = [f'<div class="title"><div><p class="eyebrow">Laufend · Kanton</p>'
             f'<h1>{e(_m("open_canton_title", name=name))}</h1>'
             f'<p class="sum">'
             + e(_m("open_canton_desc", n=len(rows), name=name)) + "</p></div>"
             f'<dl class="rail"><dt>{_.as_of}</dt><dd class="mono">{TODAY}</dd>'
             f'<dt>{_.canton}</dt><dd class="mono">{e(code)}</dd></dl></div>',
             '<div class="sec">' + table(rows) + "</div>",
             f'<div class="tags" style="margin-top:22px">'
             f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(code)}/">{e(_if("awarded_in", c=code))}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/">{e(_i.all_open)}</a></div>']
        write(f"/{LANG}/ausschreibungen/{code}/index.html", page(
            fit_title(_m("open_canton_title", name=name), " — simap"),
            _m("open_canton_desc", n=len(rows), name=name),
            "\n".join(b), f"/{LANG}/ausschreibungen/{code}/", _.tenders))
    return 1 + len(by_cant)


# --------------------------------------------------------------- section index

def build_index(path: str, kicker: str, h1: str, lead: str, items: list,
                title: str, desc: str) -> None:
    """The root of each section. Without one the URL is a 404 in production (the local
    server's directory listing hides this), and the leaves lose their nearest hub."""
    groups = collections.defaultdict(list)
    for sl, name, n in items:
        first = (name.strip()[:1] or "#").upper()
        groups["0–9" if first.isdigit() else (first if first.isalpha() else "#")].append(
            (sl, name, n))
    b = [f'<div class="title"><div><p class="eyebrow">{e(kicker)}</p><h1>{e(h1)}</h1>'
         f'<p class="sum">{e(lead)}</p></div>'
         f'<dl class="rail"><dt>{_.entries}</dt><dd class="num">{len(items)}</dd></dl></div>']
    letters = sorted(groups)
    b.append('<div class="tags" style="margin:22px 0 0">'
             + "".join(f'<a class="tag" href="#{e(g)}">{e(g)}</a>' for g in letters) + "</div>")
    for g in letters:
        rows = sorted(groups[g], key=lambda x: x[1].lower())
        b.append(f'<div class="sec" id="{e(g)}"><div class="runhead"><span>{e(g)}</span>'
                 f'<span>{len(rows)}</span></div><ul class="plain">')
        for sl, name, n in rows:
            b.append(f'<li><div class="row"><a href="/{LANG}{path}{e(sl)}/">{e(name)}</a>'
                     f'<span class="sub num">{zuschlag(n)}</span></div></li>')
        b.append("</ul></div>")
    write(f"/{LANG}{path}index.html", page(title, desc, "\n".join(b), f"/{LANG}{path}", kicker))


# ------------------------------------------------------------- home & sitemap

def build_home(pages: dict, comp: dict, awards: list, opens: list, cant_list, cpv_list) -> None:
    total = sum(a.get("winnerPrice") or 0 for a in awards
                if isinstance(a.get("winnerPrice"), (int, float)))
    months = sorted({(a.get("publicationDate") or "")[:7] for a in awards if a.get("publicationDate")})
    span = ""
    if months:
        fmt = lambda m: f"{m[5:7]}/{m[:4]}"
        span = fmt(months[0]) if len(months) == 1 else f"{fmt(months[0])} – {fmt(months[-1])}"
    firms = collections.Counter(slug(w) for a in awards for w in winners(a))
    soon = sorted((t for t in opens if t.get("offerDeadline")),
                  key=lambda t: t["offerDeadline"])[:8]

    b = [f'<div class="title"><div><h1>Wer gewinnt die öffentlichen Aufträge der Schweiz.</h1>'
         '<p class="sum">Jeder auf simap.ch publizierte Zuschlag, nach Unternehmen '
         "aufbereitet: Auftraggeber, Betrag, Verfahren — und welche Ausschreibungen "
         "gerade offen sind.</p></div>"
         f'<dl class="rail"><dt>{_.source}</dt><dd>Amtliche Publikationen von Bund, Kantonen '
         "und Gemeinden</dd>" + (f"<dt>{_.period}</dt><dd>{e(span)}</dd>" if span else "")
         + f"<dt>{_.updated}</dt><dd>{e(TODAY)}</dd></dl></div>",
         '<div class="figures">',
         f'<div class="fig"><b>{chf(len(awards))}</b><span>{_.awards}</span></div>',
         f'<div class="fig"><b>{chf(len(firms))}</b><span>{_.companies}</span></div>']
    if total:
        b.append(f'<div class="fig"><b>{chf_big(total)}</b><span>{_.sum_published}</span></div>')
    b.append(f'<div class="fig"><b>{chf(len(opens))}</b><span>{_.tenders}</span></div>'
             "</div>")

    b.append('<div class="cols"><div>'
             f'<div class="runhead"><span>{_.companies}</span>'
             f'<span>{e(span)}</span></div>'
             '<div class="scroll"><table><thead><tr><th style="width:34px"></th>'
             f'<th>{_.companies}</th><th style="width:46px">Kt.</th>'
             f'<th class="r">{_.awards}</th><th class="r">{_.sum}</th></tr></thead><tbody>')
    rank = [(s, p) for s, p in sorted(pages.items(), key=lambda kv: (-kv[1]["n"], -kv[1]["value"]))][:25]
    for i, (s, p) in enumerate(rank, 1):
        b.append(f'<tr><td class="sub num">{i:02d}</td><td>'
                 f'<a href="{BASE}/{LANG}/unternehmen/{e(s)}/">{e(p["name"])}</a>'
                 + (f'<span class="sub" style="display:block;margin-top:2px">'
                    f'{e(p["sector"][:46])}</span>' if p["sector"] else "")
                 + f'</td><td>{e(p["cant"])}</td><td class="r num">{p["n"]}</td>'
                 f'<td class="r num">{e(chf(p["value"]))}</td></tr>')
    b.append("</tbody></table></div></div><div>")

    if soon:
        b.append(f'<div class="runhead"><span>{_i.next_deadlines}</span>'
                 f'<span>{_if("open_count", n=len(opens))}</span></div><ul class="plain">')
        for t in soon:
            b.append(f'<li><div class="row"><a href="{BASE}/{LANG}/auftrag/{e(t.get("projectId"))}/">'
                     f'{e(de(t, "title")[:66])}</a>'
                     f'<span class="when">{e(dmy(t["offerDeadline"]))}</span>'
                     "</div></li>")
        b.append("</ul>")
    b.append(f'<div class="runhead" style="margin-top:28px"><span>{_i.by_canton}</span>'
             f'<span>{len(cant_list)}</span></div><div class="tags">'
             + "".join(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(c)}/">{e(c)} {len(r)}</a>'
                       for c, r in cant_list[:16]) + "</div>")
    b.append(f'<div class="runhead" style="margin-top:28px"><span>{_i.by_sector}</span>'
             f'<span>{len(cpv_list)}</span></div><ul class="plain">')
    for code, rows in cpv_list[:8]:
        label = next((de(a, "cpvLabel") or a.get("cpvLabel") for a in rows
                      if de(a, "cpvLabel") or a.get("cpvLabel")), code)
        b.append(f'<li><div class="row"><a href="{BASE}/{LANG}/bereich/{e(code)}/">{e(label[:40])}</a>'
                 f'<span class="sub num">{len(rows)}</span></div></li>')
    b.append("</ul></div></div>")

    b.append('<div class="tags" style="margin-top:32px;padding-top:22px;'
             'border-top:1px solid var(--rule)">'
             f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/">{e(_p.open_tenders_h1)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/unternehmen/">{e(_i.all_companies)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/auftraggeber/">{e(_i.all_buyers)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/kanton/">{e(_i.all_cantons)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/bereich/">{e(_i.all_sectors)}</a></div>')
    col = grafici.columns(per_month(awards), _p.chart_months, _p.chart_months_cap)
    if col:
        b.append(f'<div class="sec"><div class="runhead"><span>{_p.chart_months}</span>'
                 f'<span>{chf(len(awards))}</span></div>{col}</div>')

    b.append('<div class="official" style="margin-top:36px">Diese Website bereitet '
             "öffentlich publizierte Daten auf und ist kein Ersatz für simap.ch. "
             "Massgebend sind ausschliesslich die dort veröffentlichten Publikationen.</div>")

    write(f"/{LANG}/index.html", page(
        _m("home_title"), _m("home_desc", n=chf(len(awards))),
        "\n".join(b), f"/{LANG}/"))




def build_root() -> None:
    """The root is a real page, not a redirect: it is what x-default points at, and a
    visitor who does not read German should not be guessed at."""
    rows = "".join(
        f'<li><div class="row"><a href="/{l}/"><b style="font-size:17px">{e(NAMES[l])}</b>'
        f'<span class="sub" style="display:block;margin-top:2px">'
        f'{e(lingue.p("tagline", l))}</span></a></div></li>' for l in LANGS)
    alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{ORIGIN}/{l}/">'
                     for l in LANGS) + f'\n<link rel="alternate" hreflang="x-default" href="{ORIGIN}/">'
    body = (f'<div class="masthead"><span class="name">{e(lingue.t("site", "de"))}</span>'
            f'<span class="eyebrow">Sprache · Langue · Lingua · Language</span></div>'
            f'<div class="sec"><ul class="plain">{rows}</ul></div>')
    html = (f'<!doctype html>\n<html lang="de"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(lingue.t("site", "de"))} — Marchés publics · Appalti · Contracts</title>'
            f'<meta name="description" content="'
            f'{e(lingue.m("home_desc", "de", n=""))}">'
            f'<link rel="canonical" href="{ORIGIN}/">\n{alts}\n'
            f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
            f'family=IBM+Plex+Sans:wght@400;500;600&amp;'
            f'family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&amp;display=swap">'
            f'<link rel="stylesheet" href="{BASE}/style.css">{VERIFY}</head><body><div class="wrap">'
            f'{body}</div></body></html>')
    write("/index.html", html)




def build_language(awards: list, opens: list) -> tuple[int, int, int, int, int, int]:
    comp = profile(awards)
    open_for = matches(comp, opens)
    sectors = sector_pages(awards)
    buyer_counts = collections.Counter(a["buyerName"] for a in awards if a.get("buyerName"))
    buyer_slugs = {slug(b) for b, k in buyer_counts.items() if k >= 3}
    keep = {n for n, c in comp.items() if len(c["awards"]) >= MIN_AWARDS}
    peer_map = peers(comp, keep)
    pages = build_companies(comp, open_for, sectors, buyer_slugs, peer_map)
    n_aw = build_awards(awards, opens, pages, sectors, buyer_slugs)
    buyers = build_buyers(awards, comp, pages, sectors)
    cant_list, cpv_list = build_hubs(awards, comp, pages, sectors)
    n_open = build_open(opens, sectors, buyer_slugs)
    build_index("/unternehmen/", _.companies, _i.companies_h1, _i.companies_lead,
                [(sl, p["name"], p["n"]) for sl, p in pages.items()],
                _i.companies_title, _if("companies_desc", n=len(pages)))
    build_index("/auftraggeber/", _.buyers, _i.buyers_h1, _i.buyers_lead,
                [(sl, n, k) for sl, n, k in buyers],
                _i.buyers_title, _if("buyers_desc", n=len(buyers)))
    build_index("/kanton/", _.cantons, _.cantons, _i.cantons_lead,
                [(c, CANTONS.get(c, c), len(r)) for c, r in cant_list],
                _i.cantons_title, _i.cantons_desc)
    build_index("/bereich/", _.sectors, _i.sectors_h1, _i.sectors_lead,
                [(c, next((de(a, "cpvLabel") or a.get("cpvLabel") or c for a in r
                           if de(a, "cpvLabel") or a.get("cpvLabel")), c), len(r))
                 for c, r in cpv_list],
                _i.sectors_title, _i.sectors_desc)
    build_home(pages, comp, awards, opens, cant_list, cpv_list)
    return (len(pages), n_aw, len(buyers), len(cant_list), len(cpv_list), n_open)


def main() -> None:
    global LANG
    # docs/ is wiped every build, so the IndexNow key file — proof of ownership,
    # served at the site root — is put back afterwards rather than lost each night.
    keyfile = ROOT / "indexnow.key"
    if OUT.exists():
        shutil.rmtree(OUT)
    awards, opens = load()
    print(f"  dati    : {len(awards)} aggiudicazioni · {len(opens)} bandi aperti")
    for lang in LANGS:
        LANG = lang
        n = build_language(awards, opens)
        print(f"  {lang}      : {n[0]} imprese · {n[1]} appalti · {n[2]} committenti "
              f"· {n[3]} cantoni · {n[4]} settori · {n[5]} bandi")
    LANG = "de"
    build_root()
    write("/style.css", CSS)
    if keyfile.exists():
        k = keyfile.read_text().strip()
        write(f"/{k}.txt", k)
    print(f"  sitemap : {build_sitemap()} URL in {len(LANGS)} lingue")


def build_sitemap() -> int:
    """One sitemap per language plus an index.

    Two limits force the split. The protocol caps a sitemap file at 50,000 URLs and
    75,141 in one file makes Search Console reject it — a third of the register would
    never be submitted. And every <loc> has to carry the base path: without it the
    submission comes back "not found" for every URL, which is the whole point of the
    site failing silently.
    """
    def url_of(f: pathlib.Path) -> str:
        rel = f.relative_to(OUT).parent.as_posix()
        return "/" if rel == "." else f"/{rel}/"

    by_lang: dict[str, list[str]] = {l: [] for l in LANGS}
    root: list[str] = []
    for f in OUT.rglob("index.html"):
        u = url_of(f)
        seg = u.strip("/").split("/")[0]
        (by_lang[seg] if seg in by_lang else root).append(u)

    def doc(urls: list[str]) -> str:
        head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        body = "".join(f"<url><loc>{ORIGIN}{u}</loc><lastmod>{TODAY}</lastmod></url>"
                       for u in sorted(urls))
        return head + body + "</urlset>"

    files, total = [], 0
    for lang in LANGS:
        urls = by_lang[lang] + (root if lang == LANGS[0] else [])
        assert len(urls) <= 50_000, f"sitemap-{lang}: {len(urls)} URL, il limite e' 50 000"
        write(f"/sitemap-{lang}.xml", doc(urls))
        files.append(f"sitemap-{lang}.xml")
        total += len(urls)

    idx = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           + "".join(f"<sitemap><loc>{ORIGIN}/{f}</loc><lastmod>{TODAY}</lastmod></sitemap>"
                     for f in files)
           + "</sitemapindex>")
    write("/sitemap.xml", idx)
    # robots.txt sits at /auftragsregister/robots.txt on a project Pages site, where no
    # crawler looks for it — the origin root is not ours to write. It is emitted for
    # correctness; discovery happens through the Search Console submission.
    write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n")
    return total


if __name__ == "__main__":
    main()
