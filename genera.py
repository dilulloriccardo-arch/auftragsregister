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
import hashlib
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
# Data mostrata nelle pagine = data dell'ultimo dato pubblicato (non del giorno di build): cosi'
# le pagine i cui dati non cambiano restano identiche da una notte all'altra (git, IndexNow, Google).
DATA_DATE = TODAY

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
    """Headline sums only, abbreviated in the READER's units: Mrd. and Mio. are the
    German abbreviations and read foreign on the French and Italian pages."""
    if not isinstance(v, (int, float)) or not v:
        return ""
    bn, mn, dec = lingue.BIG_UNITS[LANG]
    if v >= 1_000_000_000:
        return f"{v / 1_000_000_000:.2f}".replace(".", dec) + f" {bn}"
    if v >= 10_000_000:
        return f"{v / 1_000_000:.0f} {mn}"
    return chf(v)


def plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def dmy(iso: str) -> str:
    """Short German date: 28.08 — day before month, unlike the ISO the source uses."""
    return f"{iso[8:10]}.{iso[5:7]}" if iso and len(iso) >= 10 else ""


def dmyy(iso: str) -> str:
    """A date as the reader writes it: dd.mm.yyyy in the three national languages,
    ISO on the English pages, where it reads international rather than foreign."""
    if not iso or len(iso) < 10:
        return ""
    if LANG == "en":
        return iso[:10]
    return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}"


def fit_title(text: str, suffix: str, limit: int = 64) -> str:
    """A title Google will not truncate, cut so it still identifies the page.

    Cutting only the tail produced 747 titles shared by 3,036 pages: awards from one
    big project share a long prefix and differ only in the part that gets thrown away —
    28 pages all reading "Flumenthal; Zentralgefängnis Kanton Solothurn (ZGSO)…" where
    the real subject was Brandschutzbekleidung, Innentüren, Gärtnerarbeiten. Identical
    titles are what tells a search engine a set of pages carries nothing of its own.

    So the ellipsis goes in the MIDDLE: the head keeps the project, the tail keeps the
    trade, and both are cut on a word boundary.
    """
    room = limit - len(suffix)
    text = " ".join(text.split())
    if len(text) <= room:
        return text + suffix

    def cut_end(t: str, n: int) -> str:
        c = t[:n]
        if " " in c[max(0, n - 22):]:
            c = c[:c.rfind(" ")]
        return c.rstrip(" ,.;:-–—/")

    def cut_start(t: str, n: int) -> str:
        """Whole words from the end. A tail that begins mid-word ("dschutzbekleidung")
        is worse than a shorter one: it reads as damage, not as an abbreviation."""
        words, out = t.split(" "), []
        for w in reversed(words):
            if len(" ".join([w] + out)) > n:
                break
            out.insert(0, w)
        return " ".join(out).lstrip(" ,.;:-–—/")

    tail_room = max(0, room * 2 // 5)
    head = cut_end(text, room - tail_room - 1)
    tail = cut_start(text, tail_room) if tail_room >= 8 else ""
    if not tail or tail in head:
        return head + "…" + suffix
    return f"{head}…{tail}{suffix}"


def zuschlag(n: int) -> str:
    one, many = lingue.PLURALS[LANG]
    return plural(n, one, many)


def de(row: dict, field: str) -> str:
    """The publication's own text, in the page's language where it exists.

    simap translates 74% of titles into German and 51% into French, so hardcoding
    German threw away roughly 3,700 French titles the source had already published —
    on the French site, which serves a quarter of the market. Italian sits at 3% and
    English at nothing, so those fall back rather than pretend.

    The fallback order is deliberate: the page's language, then German as the register's
    majority language, then the field as published. It never paraphrases, and it never
    labels one language's text as another's.
    """
    t = ((row.get("translations") or {}).get(field) or {})
    order = (LANG, "de", "fr", "it")
    for lang in order:
        if t.get(lang):
            return t[lang].strip()
    return (row.get(field) or "").strip()


def chf_amount(row: dict) -> float | None:
    """The awarded amount, but only when the register published it IN FRANCS.

    98 awards are published in euros and 11 in dollars. Adding them to a CHF total
    silently overstated it by roughly half a billion, and each page printed a foreign
    figure under a "CHF" label — a converted or mislabelled amount is a number the
    source never published, and this is a register. Foreign amounts are shown on their
    own page with their own currency and left out of every total.
    """
    p = row.get("winnerPrice")
    if not isinstance(p, (int, float)) or not p:
        return None
    cur = (row.get("winnerCurrency") or "CHF").strip().upper()
    return float(p) if cur == "CHF" else None


def _e(kind: str, value) -> str:
    return lingue.enum(kind, value, LANG)


def money(row: dict) -> str:
    """The awarded amount as the register published it, currency and all.

    Never relabelled: 109 awards are in euros or dollars, and printing them under a
    CHF heading states something the publication does not.
    """
    p = row.get("winnerPrice")
    if not isinstance(p, (int, float)) or not p:
        return ""
    cur = (row.get("winnerCurrency") or "CHF").strip().upper()
    return f"{chf(p)}" + ("" if cur == "CHF" else f" {cur}")


def winners(row: dict) -> list[str]:
    """Every firm the award names, from the structured list where the source has one.

    simap publishes `award.vendors` as a list and `winnerName` as a flat string that
    holds only the FIRST of them. Parsing the string dropped 1,162 firm-award rows
    across 473 awards — one framework contract names 36 suppliers and the page showed
    a single "1 Anbieter", contradicting the publication it links to.

    Names only. `vendors[i].price` is not money per firm: on many of these rows every
    vendor carries the identical figure, a framework ceiling repeated line by line, so
    attributing it per name would invent billions the register never published. The
    money rule elsewhere is unchanged — an amount is only ever credited to a firm when
    the award names exactly one.
    """
    vend = (row.get("award") or {}).get("vendors") or []
    names = [str(v.get("name") or "").strip() for v in vend if isinstance(v, dict)]
    names = [n for n in names if len(n) > 2]
    if names:
        return list(dict.fromkeys(names))
    w = (row.get("winnerName") or "").strip()
    if not w:
        return []
    return [p.strip() for p in re.split(r"\s*;\s*|\s+/\s+|\n", w) if len(p.strip()) > 2]


_CPV = json.loads((ROOT / "cpv_labels.json").read_text()) if (ROOT / "cpv_labels.json").exists() else {}
_CPV_COL = {"de": 0, "fr": 1, "it": 2, "en": 3}


def cpv_label(code, fallback: str = "") -> str:
    """The official EU label for a CPV code, in the page's language.

    The register's own labels come back only in the language of the request, which
    left every sector name German on three of the four language versions — the
    reviewers' single most repeated finding. The EU publishes the whole vocabulary
    in every official language; unknown codes fall back to whatever simap sent.
    """
    row = _CPV.get(str(code or "").strip())
    return row[_CPV_COL[LANG]] if row else fallback


def canton_name_or(code, fallback=None):
    """Drop-in for the old CANTONS.get(code, fallback) call sites."""
    if not code:
        return fallback if fallback is not None else ""
    n = canton_name(code)
    return n if n else (fallback if fallback is not None else code)


def canton_name(code: str) -> str:
    """The canton's name as the reader calls it — 'Tessin' on the Italian page named
    the reader's own canton in German."""
    if LANG != "de":
        n = lingue.CANTON_NAMES.get(LANG, {}).get(code)
        if n:
            return n
    return CANTONS.get(code, code or "")


def wcut(t: str, n: int) -> str:
    """Cut on a word boundary: a label ending mid-word reads as damage."""
    t = (t or "").strip()
    if len(t) <= n:
        return t
    c = t[:n]
    if " " in c[max(0, n - 18):]:
        c = c[:c.rfind(" ")]
    return c.rstrip(" ,.;:-–—/") + "…"


def norm_buyer(name: str) -> str:
    """The key that decides whether two spellings are the same authority.

    The register writes one office several ways — a trailing space, a leading tab,
    "BBL" against "(BBL)". Keyed on the raw string, each variant became its own page
    writing to the same file, and the last write won: the Bundesamt für Bauten und
    Logistik page stated 3 awards where the office has 156, and Basel-Stadt 3 where it
    has 351. Figures that wrong about a named public body are the worst thing a
    register can publish.

    Normalising the NAME, not the slug: slug() truncates at 70 characters, and grouping
    on that would merge genuinely separate SBB purchasing units into one page.
    """
    n = (name or "")
    # Typographic variants of the same character: the register writes both l'environnement
    # and l’environnement for one office, and separates a department from its parent with a
    # comma here and a dash there.
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'),
                 ("\u2013", "-"), ("\u2014", "-"), (",", " "), ("/", " "), ("-", " ")):
        n = n.replace(a, b)
    n = n.replace("(", " ").replace(")", " ")
    # Genuine typos are left alone on purpose: "Bundebahnen" for "Bundesbahnen" and
    # "Resourcen" for "Ressourcen" are real spellings in the source, and the fuzzy match
    # that would merge them would also merge authorities that are actually different.
    return " ".join(n.split()).casefold().rstrip(" .:;'")


def sig(code) -> str:
    """Significant digits of a CPV code: 45000000 -> '45' (a bucket, not a category)."""
    return str(code).rstrip("0") or str(code)[:2]


def load() -> tuple[list, list]:
    """Awards and open tenders.

    `abandonment` publications ride in the same feed: a procurement the authority
    called off. Presenting one as an award says a contract was granted that was not,
    so they are dropped here rather than counted.
    """
    awards, seen = [], set()
    for f in sorted(DATI.glob("aggiudicazioni_*.json")):
        for a in json.loads(f.read_text()):
            k = a.get("publicationId") or a.get("publicationNumber")
            if k and k in seen:
                continue
            seen.add(k)
            if a.get("pubType") == "abandonment":
                continue
            awards.append(a)
    p = DATI / "gare_aperte.json"
    opens = [t for t in json.loads(p.read_text())
             if (t.get("offerDeadline") or "")[:10] >= TODAY] if p.exists() else []
    return awards, opens


# ------------------------------------------------------------------ the chrome

CSS = grafici.CSS + """
/* Direction: dark instrument panel. One visual world, deliberately dark — the record is
   the light in the room. Bricolage Grotesque sets the display, Libre Franklin reads, and
   every figure is monospaced so columns of numbers line up the way a ledger does.

   Adapted 21.09.2026 from a design study, with three things deliberately NOT carried over:
   no web fonts from a third party (the privacy page promises none, and the Google Fonts
   link would send every visitor's IP abroad), no client-side view switching (the whole
   value of this site is 81'891 pages a crawler can read), and no pricing. */
:root{
  --paper:#07090c; --paper-2:#0a0d12;
  --ink:#f3f6f9; --muted:#9db0c2; --muted-2:#6d8093;
  --rule:rgba(255,255,255,.085); --rule-strong:rgba(255,255,255,.17);
  --accent:#ff4356; --accent-soft:#ff8a96; --signal:#ffb454;
  --wash:rgba(255,255,255,.045); --panel:#0d1117;
  --hero:transparent; --hero-ink:#f3f6f9; --hero-muted:#9db0c2;
  --mark:#38b5dd;
  --glass:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.017));
  --d1:#10303f; --d2:#15485f; --d3:#1b6484; --d4:#2288ae; --d5:#38b5dd; --d6:#7fe3ff;
  --ease:cubic-bezier(.22,.68,.24,1);
  color-scheme:dark;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Libre Franklin",system-ui,-apple-system,sans-serif;font-size:15px;
  line-height:1.6;-webkit-font-smoothing:antialiased;position:relative}
/* Background, painted with pseudo-elements so no page needs extra markup. */
body::before{content:"";position:fixed;inset:0;z-index:-2;pointer-events:none;
  background:
    radial-gradient(48vw 40vw at 6% -8%,rgba(56,181,221,.30),transparent 64%),
    radial-gradient(42vw 36vw at 96% -4%,rgba(124,92,255,.22),transparent 64%),
    radial-gradient(40vw 34vw at 58% 22%,rgba(255,67,86,.14),transparent 66%),
    var(--paper)}
body::after{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;
  background-image:
    repeating-linear-gradient(90deg,rgba(255,255,255,.032) 0 1px,transparent 1px 72px),
    repeating-linear-gradient(0deg,rgba(255,255,255,.032) 0 1px,transparent 1px 72px);
  -webkit-mask-image:radial-gradient(130% 88% at 50% 0%,#000 26%,transparent 74%);
  mask-image:radial-gradient(130% 88% at 50% 0%,#000 26%,transparent 74%)}
.wrap{max-width:1180px;margin:0 auto;padding:0 30px 60px}
a{color:var(--ink);text-decoration:none;
  background-image:linear-gradient(var(--accent),var(--accent));
  background-size:100% 1px;background-repeat:no-repeat;background-position:0 100%;
  padding-bottom:1px;transition:color .15s}
a:hover{background-size:100% 2px;color:#fff}
a:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:5px}
.disp,h1,h2,h3,.fig b,.masthead a.name{font-family:"Bricolage Grotesque","Libre Franklin",
  system-ui,sans-serif;font-variation-settings:"wdth" 92}
.mono,.num,.when,.tag,.amount{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,
  Consolas,monospace;font-variant-numeric:tabular-nums;font-feature-settings:"tnum"}
.eyebrow{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10.5px;
  letter-spacing:.2em;text-transform:uppercase;color:var(--muted-2);font-weight:500;margin:0}
.masthead{display:flex;justify-content:space-between;align-items:baseline;gap:16px;
  padding:18px 0 14px;border-bottom:1px solid var(--rule);flex-wrap:wrap}
.masthead a.name{font-weight:800;font-size:18px;letter-spacing:-.03em;color:var(--ink);
  background:none;padding:0}
.masthead a.name:hover{color:var(--accent)}
.langs{display:flex;gap:16px;padding:10px 0 0;font-size:12.5px;font-weight:600;
  justify-content:flex-end}
.langs a{color:var(--muted-2);background:none;padding:0}
.langs a:hover{color:var(--ink)}
.langs .on{color:var(--accent)}
/* The hero no longer needs its own dark block: the whole page is dark. It keeps the
   same class name and grid so every existing page renders unchanged. */
.title{background:var(--hero);color:var(--hero-ink);margin:0;padding:44px 0 34px;
  display:grid;grid-template-columns:1fr 280px;gap:48px;align-items:start;
  border-bottom:1px solid var(--rule)}
.title .eyebrow{color:var(--accent-soft)}
.title h1{color:var(--hero-ink)}
.title p.sum{margin:16px 0 0;color:var(--hero-muted);font-size:16px;max-width:52ch}
h1{font-weight:800;letter-spacing:-.045em;line-height:1;margin:12px 0 0;
  text-wrap:balance;font-size:clamp(32px,5.4vw,54px)}
h2{font-weight:700;font-size:23px;margin:0 0 3px;letter-spacing:-.032em}
h3{font-weight:700;font-size:16px;margin:0;letter-spacing:-.02em}
.runhead{display:flex;justify-content:space-between;gap:16px;padding:0 0 9px;
  margin-top:40px;border-bottom:1px solid var(--rule-strong);font-size:10.5px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--muted-2);font-weight:600;
  font-family:ui-monospace,Menlo,monospace}
.rail{border-left:0;padding-left:0;font-size:13px;color:var(--hero-muted)}
.rail dt{font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--accent-soft);margin-top:15px;font-weight:600;
  font-family:ui-monospace,Menlo,monospace}
.rail dt:first-child{margin-top:0}
.rail dd{margin:4px 0 0;font-size:14px;color:var(--hero-ink)}
/* ── figures / KPI ─────────────────────────────────────────────────────── */
.figures{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;
  padding:26px 0 6px;border-bottom:0}
.fig{border:1px solid var(--rule);border-radius:16px;padding:20px 22px;background:var(--glass);
  position:relative;overflow:hidden}
.fig::after{content:"";position:absolute;left:0;right:0;top:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.26),transparent)}
.fig b{display:block;font-weight:700;font-size:clamp(26px,3.6vw,38px);letter-spacing:-.045em;
  font-variant-numeric:tabular-nums;line-height:1;overflow-wrap:anywhere}
.fig.money b{color:var(--accent)}
.fig span{display:block;margin-top:11px;font-size:10px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--muted-2);font-weight:600;
  font-family:ui-monospace,Menlo,monospace}
.sec{margin-top:10px}
.scroll{overflow-x:auto;max-width:100%}
/* ── tables ────────────────────────────────────────────────────────────── */
table{width:100%;border-collapse:collapse}
th{text-align:left;font-size:9.5px;letter-spacing:.15em;text-transform:uppercase;
  color:var(--muted-2);font-weight:600;padding:0 14px 11px 0;
  border-bottom:1px solid var(--rule-strong);white-space:nowrap;
  font-family:ui-monospace,Menlo,monospace}
td{padding:13px 14px 13px 0;border-bottom:1px solid var(--rule);vertical-align:top;
  font-size:14.5px}
tbody tr{transition:background .15s}
tbody tr:hover{background:rgba(255,255,255,.032)}
td.r,th.r{text-align:right;padding-right:0}
td.sub,.sub{color:var(--muted);font-size:13px}
ul.plain{list-style:none;margin:0;padding:0}
ul.plain li{padding:13px 0;border-bottom:1px solid var(--rule)}
ul.plain li:last-child{border-bottom:0}
.row{display:flex;justify-content:space-between;gap:16px;align-items:baseline}
.when{color:var(--accent);font-size:12px;white-space:nowrap;font-weight:600}
/* ── tags / chips ──────────────────────────────────────────────────────── */
.tags{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}
.tag{border:1px solid var(--rule);background:var(--wash);border-radius:100px;
  padding:6px 14px;font-size:12px;color:var(--muted);
  transition:border-color .16s,color .16s,transform .16s var(--ease)}
a.tag{background-image:none;padding-bottom:6px}
a.tag:hover{background:var(--wash);border-color:var(--rule-strong);color:var(--ink);
  transform:translateY(-1px)}
.tag.on{background:var(--ink);border-color:var(--ink);color:var(--paper);font-weight:600}
/* ── glass panel, the one new primitive ────────────────────────────────── */
.glass{position:relative;border:1px solid var(--rule);border-radius:18px;overflow:hidden;
  background:var(--glass);margin-top:16px}
.glass::after{content:"";position:absolute;left:0;right:0;top:0;height:1px;
  pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.26),transparent)}
.glass .ch{display:flex;justify-content:space-between;align-items:baseline;gap:14px;
  padding:18px 24px 14px}
.glass .ch .side{font-family:ui-monospace,Menlo,monospace;font-size:10px;
  letter-spacing:.15em;text-transform:uppercase;color:var(--muted-2)}
.glass .pad{padding:0 24px 22px}
.glass .pad.top{padding-top:20px}
/* ── canton map: 26 links, works with JavaScript switched off ──────────── */
.gmap{display:grid;grid-template-columns:repeat(8,1fr);gap:6px;padding:4px 24px 20px}
.gmap a{border-radius:11px;aspect-ratio:1;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:3px;line-height:1;background-image:none;
  padding-bottom:0;transition:transform .2s var(--ease),box-shadow .2s}
.gmap a:hover{transform:scale(1.11);z-index:2;box-shadow:0 10px 28px -8px rgba(0,0,0,.85)}
.gmap .c{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;font-weight:600}
.gmap .v{font-family:ui-monospace,Menlo,monospace;font-size:8.5px;opacity:.72}
.s1{background:var(--d1);color:#cfe6f2} .s2{background:var(--d2);color:#e4f2f9}
.s3{background:var(--d3);color:#eaf6fb} .s4{background:var(--d4);color:#04141c}
.s5{background:var(--d5);color:#04141c} .s6{background:var(--d6);color:#04141c}
.mleg{display:flex;align-items:center;gap:9px;padding:0 24px 20px;font-size:10px;
  color:var(--muted-2);font-family:ui-monospace,Menlo,monospace;letter-spacing:.08em}
.mleg .sw{display:flex;gap:3px}
.mleg i{width:20px;height:8px;border-radius:3px;display:block}
/* ── comparison table ──────────────────────────────────────────────────── */
.cmp th{padding:16px 18px;font-size:12px;letter-spacing:.03em;text-transform:none;
  color:var(--muted);font-weight:600;font-family:"Libre Franklin",sans-serif;
  border-bottom:1px solid var(--rule)}
.cmp th.us{color:var(--accent-soft)}
.cmp td{padding:15px 18px;font-size:14px}
.cmp td.c{text-align:center;width:180px;font-family:ui-monospace,Menlo,monospace;
  font-size:12.5px;color:var(--muted-2)}
.cmp td.c.y{color:#3ddc97}
/* ── FAQ ───────────────────────────────────────────────────────────────── */
.faq details{border-bottom:1px solid var(--rule);padding:16px 0}
.faq details:last-child{border-bottom:0}
.faq summary{cursor:pointer;font-weight:600;font-size:15.5px;list-style:none;display:flex;
  justify-content:space-between;gap:14px;align-items:baseline}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";color:var(--accent);
  font-family:ui-monospace,Menlo,monospace;flex:0 0 auto}
.faq details[open] summary::after{content:"\2212"}
.faq p{margin:12px 0 0;font-size:14.5px;color:var(--muted);max-width:74ch}
/* ── subscribe form ────────────────────────────────────────────────────── */
.form{margin-top:18px;max-width:620px;position:relative}
.form .f{display:block;font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--muted-2);font-weight:600;margin:20px 0 8px;
  font-family:ui-monospace,Menlo,monospace}
.form input[type=email]{width:100%;box-sizing:border-box;border:1px solid var(--rule-strong);
  border-radius:12px;padding:13px 15px;font-size:15.5px;background:rgba(255,255,255,.05);
  color:var(--ink);font-family:inherit;transition:border-color .2s,background .2s}
.form input[type=email]::placeholder{color:var(--muted-2)}
.form input[type=email]:focus{background:rgba(255,255,255,.085);border-color:var(--accent);
  outline:none}
.form .pills{display:flex;flex-wrap:wrap;gap:7px}
.form .pills label{cursor:pointer;position:relative}
.form .pills input{position:absolute;opacity:0;width:1px;height:1px;left:0;top:0}
.form .pills input:checked+.tag{background:var(--ink);border-color:var(--ink);
  color:var(--paper);font-weight:600}
.form .pills input:focus-visible+.tag{outline:2px solid var(--accent);outline-offset:2px}
.form button{margin-top:22px;border:1px solid #ff6b7a;
  background:linear-gradient(180deg,#ff5b6b,#e8283c);color:#fff;border-radius:100px;
  padding:13px 26px;font-size:14.5px;font-weight:600;cursor:pointer;
  box-shadow:0 8px 26px -10px rgba(255,67,86,.8);
  transition:transform .18s var(--ease),box-shadow .25s}
.form button:hover{transform:translateY(-2px);
  box-shadow:0 14px 36px -10px rgba(255,67,86,.95)}
.form button:disabled{opacity:.55;transform:none;cursor:default}
.form .hp{position:absolute;left:-9999px;opacity:0}
.form .msg{margin-top:14px;font-size:14px;min-height:1.4em}
.form .msg.err{color:var(--accent-soft)}
/* ── misc ──────────────────────────────────────────────────────────────── */
.state{display:inline-flex;align-items:center;gap:8px;font-size:10px;letter-spacing:.16em;
  text-transform:uppercase;font-weight:600;color:#3ddc97;padding:5px 12px;border-radius:100px;
  background:rgba(61,220,151,.12);font-family:ui-monospace,Menlo,monospace}
.state i{width:6px;height:6px;background:currentColor;border-radius:50%;display:block}
.winner{border:1px solid var(--rule);border-radius:16px;background:var(--glass);
  padding:20px 22px;margin:10px 0 0}
.winner .who{font-family:"Bricolage Grotesque",sans-serif;font-size:22px;font-weight:700;
  letter-spacing:-.03em}
.official{margin-top:26px;padding:15px 18px;background:rgba(255,67,86,.09);
  border-left:2px solid var(--accent);border-radius:0 10px 10px 0;font-size:12.5px;
  color:var(--muted)}
.prose p{margin:0 0 15px;font-size:15.5px;line-height:1.7;max-width:66ch;color:var(--muted)}
.prose p strong{color:var(--ink)}
.bar{display:block;height:4px;border-radius:2px;
  background:linear-gradient(90deg,var(--d3),var(--d6));margin-top:6px}
.cols{display:grid;grid-template-columns:1fr 320px;gap:48px;padding-top:6px;
  align-items:start}
.half{display:grid;grid-template-columns:1fr 1fr;gap:48px;padding-top:6px;align-items:start}
.cols>*,.half>*{min-width:0}
figure{margin:16px 0 4px;background:var(--panel);border:1px solid var(--rule);
  border-radius:16px;padding:20px 22px}
figcaption{color:var(--muted-2);font-size:12px;margin-top:10px}
svg.chart{margin:0}
footer{border-top:1px solid var(--rule);margin-top:56px;padding-top:22px;
  color:var(--muted-2);font-size:12.5px}
footer p{margin:0 0 6px;max-width:80ch}
@media(prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;
  transition-duration:.01ms!important}}
@media(max-width:860px){
  .wrap{padding:0 20px 44px}
  .title{padding:30px 0 24px;grid-template-columns:1fr;gap:24px}
  .cols,.half{grid-template-columns:1fr;gap:30px}
  .gmap{grid-template-columns:repeat(5,1fr);padding-inline:16px}
  .gmap .v{display:none}
  .glass .ch,.glass .pad,.mleg{padding-inline:16px}
  .cmp td.c{width:96px;font-size:11.5px}
  .cmp th,.cmp td{padding:12px 10px}
}
"""

HEAD = """<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{site}{path}">
{alts}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 100 100%27%3E%3Crect width=%27100%27 height=%27100%27 rx=%2718%27 fill=%27%23c4472a%27/%3E%3Ctext x=%2750%27 y=%2773%27 font-size=%2762%27 font-family=%27Arial,sans-serif%27 font-weight=%27800%27 fill=%27%23fbfaf7%27 text-anchor=%27middle%27%3EA%3C/text%3E%3C/svg%3E">
<link rel="preload" href="{base}/fonts/LibreFranklin-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{base}/fonts/BricolageGrotesque-800-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}/style.css">
{verify}</head><body>
<div class="wrap">
<div class="masthead"><a class="name" href="{base}/{lang}/">{sitename}</a>
<span class="eyebrow">{kicker}</span></div>
<nav class="langs" aria-label="{langlabel}">{langnav}</nav>
<main>
"""

# The first footer line says "not official" in the READER's language. simap's §5
# notice must stay verbatim — which means German — so on its own it protected nobody
# who reads only French, Italian or English: the audit found the byte-identical German
# string on all four language versions, making the "it plainly says so" defence false
# on three of them. The verbatim notice keeps its lang="de" so screen readers switch.
FOOT = """</main><footer><p>{notoff}</p>
<p lang="de">{disc}</p>
<p>{srcnote}</p>
<p>{source}: <a href="https://www.simap.ch">simap.ch</a> — {official} ·
<a href="{imphref}">{implabel}</a> · <a href="{privhref}">{privlabel}</a></p>
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


def fit_desc(text: str, limit: int = 155) -> str:
    """A description Google shows whole.

    The snippet is cut at roughly 155 characters, and 28 % of the pages were over it —
    the worst at 224 — so a third of the site advertised itself with a sentence that
    stopped mid-word. Cut at the last sentence that fits; if none does, at the last
    word, and only then add an ellipsis. Measured 22.09.2026.
    """
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    head = text[:limit]
    # a full sentence is better than a trimmed one, but not if it throws away half
    cut = max(head.rfind(". "), head.rfind("? "), head.rfind("! "))
    if cut >= limit * 0.6:
        return head[:cut + 1]
    cut = head.rfind(" ")
    return (head[:cut] if cut > 0 else head).rstrip(" ,;:—-") + "\u2026"


def page(title: str, desc: str, body: str, path: str, kicker: str = "",
         leaf: str = "", robots: str = "", head_extra: str = "") -> str:
    # hreflang tells the search engine these are one page in four languages, not four
    # pages competing with each other for the same query.
    alts = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{ORIGIN}{lang_path(path, l)}">'
        for l in LANGS) + f'\n<link rel="alternate" hreflang="x-default" href="{ORIGIN}/">'
    nav = "".join(
        (f'<span class="on">{e(NAMES[l])}</span>' if l == LANG
         else f'<a href="{BASE}{lang_path(path, l)}">{e(NAMES[l])}</a>') for l in LANGS)
    return (HEAD.format(title=e(title), desc=e(fit_desc(desc)), site=ORIGIN, base=BASE, path=path,
                        kicker=e(kicker or _.register), lang=LANG, alts=alts,
                        verify=VERIFY + (f'<meta name="robots" content="{robots}">\n' if robots else "") + head_extra,
                        sitename=e(_.site), langnav=nav, langlabel=e(_.language))
            + breadcrumbs(path, leaf or title.split(" — ")[0])
            + body + FOOT.format(disc=e(DISCLAIMER),
                                 notoff=e(_p.not_official),
                                 imphref=f"{BASE}/{LANG}/impressum/",
                                 implabel=e(_.imprint),
                                 privhref=f"{BASE}/{LANG}/datenschutz/",
                                 privlabel=e(_.privacy),
                                 srcnote=e(_p.translation_note), source=e(_.source),
                                 official=e(_p.source_note)))


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
            p = chf_amount(a)
            # a joint award names several firms for one price; splitting it would
            # invent a figure the register never published
            if p is not None and len(ws) == 1:
                c["value"] += p
                c["amounts"].append(p)
            if a.get("cpvCode"):
                c["cpv"][(str(a["cpvCode"]), cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") or "")] += 1
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
                    buyer_slugs: dict, peer_map: dict) -> dict:
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
             + " · ".join(x for x in (wcut(sector, 44), canton_name_or(cants[0], cants[0]) if cants else "") if x)
             + f'</p><h1>{e(name)}</h1>'
             f'<p class="sum">' + e(_m("company_lead", n=zuschlag(len(rows)),
                                       span=(f", {span}" if span else ""),
                                       b=(_m("buyers_count_one") if len(c["buyers"]) == 1
                                          else _m("buyers_count", k=len(c["buyers"])))))
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
            b.append(f'<div class="fig money"><b>{chf(c["value"])}</b><span>{_.sum}</span></div>')
        b.append(f'<div class="fig"><b>{len(c["buyers"])}</b><span>{_.buyers}</span></div>')
        if len(c["amounts"]) > 1:
            b.append(f'<div class="fig"><b>{chf(median(c["amounts"]))}</b><span>{_.median}</span></div>')
        b.append("</div>")

        # Derived analysis (2026-09-07): what simap does not say — per-year rhythm and
        # how concentrated the client base is. Aggregation, not alteration (AGB §5).
        per_year: dict[str, list] = {}
        for a in rows:
            y = (a.get("publicationDate") or "")[:4]
            if y:
                per_year.setdefault(y, [0, 0.0])
                per_year[y][0] += 1
                per_year[y][1] += chf_amount(a) or 0
        if len(per_year) >= 1:
            top_b = c["buyers"].most_common(1)[0] if c["buyers"] else None
            share = round(100 * top_b[1] / len(rows)) if top_b else 0
            b.append(f'<div class="sec"><div class="runhead"><span>{e(_p.analysis)}</span>'
                     f'<span>{e(_p.derived)}</span></div><div class="scroll"><table><thead><tr>'
                     f'<th>{_.year}</th><th class="r">{_.awards}</th><th class="r">{_.sum}</th>'
                     "</tr></thead><tbody>")
            for y in sorted(per_year, reverse=True):
                n_y, v_y = per_year[y]
                b.append(f'<tr><td class="mono">{e(y)}</td><td class="r num">{n_y}</td>'
                         f'<td class="r num">{e(chf(v_y)) if v_y else "–"}</td></tr>')
            b.append("</tbody></table></div>")
            if top_b:
                b.append(f'<p class="sub" style="margin:10px 0 0">'
                         + e(_m("top_buyer_share", buyer=top_b[0][:60], share=share)) + "</p>")
            b.append("</div>")

        tl = grafici.timeline([(a.get("publicationDate") or "", chf_amount(a) or 0)
                               for a in rows], title=f"{name}: {zuschlag(len(rows))}")
        if tl:
            b.append(f'<figure>{tl}<figcaption>{e(_i.timeline_cap)}</figcaption></figure>')
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
                f'<td class="r num">{e(money(a))}</td></tr>')
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
                         f'{e(cpv_label(t.get("cpvCode"), de(t, "cpvLabel") or t.get("cpvLabel") or "") or "")[:44]}</span></div>'
                         f'<span class="when">{_.until} {e(dmyy(t.get("offerDeadline") or ""))}</span>'
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
                hit = buyer_slugs.get(norm_buyer(bu))
                b.append(f'<a class="tag" href="{BASE}/{LANG}/auftraggeber/{e(hit[0])}/">'
                         f'{e(hit[1][:52])} · {k}</a>' if hit
                         else f'<span class="tag">{e(bu[:52])} · {k}</span>')
            b.append("</div></div>")

        pr = peer_map.get(s)
        if pr:
            others, cant = pr
            b.append(f'<div class="sec"><div class="runhead"><span>{e(_p.peers)}'
                     f'</span><span>{e(canton_name_or(cant, cant))}</span></div>'
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
                 buyer_slugs: dict) -> int:
    by_project = {}
    for a in awards:
        by_project.setdefault(a.get("projectId"), {})["award"] = a
    for t in opens:
        by_project.setdefault(t.get("projectId"), {})["open"] = t
    # A first pass over the titles, because uniqueness is not a property any single
    # page can see. Truncation alone got the duplicates from 3,036 pages down to 712,
    # and the rest genuinely share a title — twelve awards read only "BKP 211
    # Baumeisterarbeiten". Knowing which ones collide is what lets the distinguisher
    # be added only where it earns its space.
    heads: dict[str, str] = {}
    for pid, rec in by_project.items():
        if not pid:
            continue
        src = rec.get("open") or rec.get("award")
        t = de(src, "title")
        if t:
            heads[pid] = fit_title(t, "")
    clash = {h for h, k in collections.Counter(heads.values()).items() if k > 1}

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
            b.append(f"<dt>{_.procedure}</dt><dd>{e(_e('processType', src['processType']))}</dd>")
        b.append("</dl></div>")

        figs = []
        if is_open and src.get("offerDeadline"):
            figs.append(f'<div class="fig"><b>{e(src["offerDeadline"][:10])}</b>'
                        f"<span>{_.deadline}</span></div>")
        if aw and aw.get("winnerPrice"):
            figs.append(f'<div class="fig"><b>{money(aw)}</b>'
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
                     f'<span>{plural(len(ws), *lingue.WINNER[LANG])}</span></div>')
            for w in ws:
                s = slug(w)
                known = pages.get(s)
                link = (f'<a href="{BASE}/{LANG}/unternehmen/{e(s)}/" class="who">{e(w)}</a>'
                        if known else f'<span class="who">{e(w)}</span>')
                extra = []
                if aw.get("winnerPrice") and len(ws) == 1:
                    extra.append(money(aw) + (" CHF" if not (aw.get("winnerCurrency")
                                  or "CHF").strip().upper() != "CHF" else ""))
                if known:
                    extra.append(f'{zuschlag(known["n"])} {_.in_register}')
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
            link = (f'<a href="{e(src["simapUrl"])}">'
                    + e(lingue.p("view_on_simap", LANG).format(n=src.get("projectNumber") or ""))
                    + "</a>")
            b.append('<div class="official">'
                     + e(_p.official_link).replace("{link}", link) + "</div>")
        b.append("</div><div>")

        b.append(f'<div class="runhead"><span>{_.details}</span><span></span></div>'
                 '<div class="scroll"><table><tbody>')
        cpv = f'<span class="mono">{e(src.get("cpvCode") or "")}</span>' + (
            "<br>" + e(cpv_label(src.get("cpvCode"), de(src, "cpvLabel") or src.get("cpvLabel") or "") or "")
            if (src.get("cpvLabel") or de(src, "cpvLabel")) else "")
        hit = buyer_slugs.get(norm_buyer(src.get("buyerName") or ""))
        buyer_cell = (f'<a href="{BASE}/{LANG}/auftraggeber/{e(hit[0])}/">{e(hit[1])}</a>'
                      if hit else e(src.get("buyerName")))
        for label, val in [(_.buyer, buyer_cell if src.get("buyerName") else ""),
                           (_.place, e(src.get("city"))),
                           (_.canton, e(canton_name_or(src.get("canton"), src.get("canton") or ""))),
                           (_.type, e(_e("orderType", src.get("orderType")))),
                           ("CPV", cpv if src.get("cpvCode") else ""),
                           (_.treaty, e(_e("bool", src.get("stateContractArea"))))]:
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
            desc += f", {_.award} {money(aw)}" + (f" — {ws[0]}" if ws else "")
        # Some award titles are genuinely identical — twelve read only "BKP 211
        # Baumeisterarbeiten". No amount of clever truncation separates those, so the
        # title carries who won: it is what distinguishes the page and what a reader
        # searching for a firm's public work would type.
        who = ws[0] if ws else (src.get("buyerName") or "")
        if heads.get(pid) in clash:
            # this one would otherwise be indistinguishable: trade the title's tail for
            # the name, and fall back to the publication number when even that repeats
            head = f"{who} · {title}" if who else f"{title} · {src.get('publicationNumber') or pid[:8]}"
        else:
            head = f"{title} · {who}" if who and len(title) < 46 else title
        write(f"/{LANG}/auftrag/{pid}/index.html",
              page(fit_title(head, _m("tender_suffix") if is_open else _m("award_suffix")),
                   desc[:180], "\n".join(b), f"/{LANG}/auftrag/{pid}/",
                   _.tenders if is_open else _.award,
                   # 2026-09-07: 77.8k schede "rilevate ma non indicizzate" (Search Console).
                   # Sono quasi identiche fra loro e il testo simap non e' modificabile (AGB
                   # §5): tolte dall'indice per concentrare il budget di scansione sulle
                   # pagine azienda e sugli indici, che hanno contenuto proprio.
                   robots="noindex,follow"))
        n += 1
    return n


# ------------------------------------------------------------------ buyer page

def buyer_map(awards: list, floor: int = 3) -> dict:
    """key -> (slug, display name), decided once so every link agrees with the page.

    Computed before anything is written: a company page, an award page and the buyer
    page itself all have to resolve the same authority to the same URL, and deriving
    the slug separately in each builder is how they drifted apart.
    """
    counts: dict[str, int] = collections.Counter()
    spell: dict[str, collections.Counter] = {}
    for a in awards:
        b = a.get("buyerName")
        if not b:
            continue
        k = norm_buyer(b)
        counts[k] += 1
        spell.setdefault(k, collections.Counter())[" ".join(b.split())] += 1
    taken: dict[str, str] = {}
    out: dict[str, tuple] = {}
    for k in sorted(counts, key=lambda x: (-counts[x], x)):
        name = spell[k].most_common(1)[0][0]
        base_sl = slug(name)
        sl = base_sl
        if taken.get(sl, k) != k:
            # hash() is randomized per process (PYTHONHASHSEED), so this suffix used to
            # change on EVERY build: the 9 colliding buyer URLs 404ed each night and
            # could never stay indexed (Search Console 404, 19.09.2026). blake2s is stable.
            digest = hashlib.blake2s(k.encode("utf-8"), digest_size=8).hexdigest()
            sl = f"{base_sl[:62]}-{int(digest, 16) % 9973:04d}"
        taken[sl] = k
        out[k] = (sl, name, counts[k])
    return {k: v for k, v in out.items() if v[2] >= floor}


def build_buyers(awards: list, comp: dict, pages: dict, sectors: set[str],
                 bmap: dict, floor: int = 3) -> list:
    """A page per contracting authority. "Welche Aufträge hat die Gemeinde X
    vergeben" is a proper-name search with a real reader behind it — a resident, a
    journalist, a competitor — and no site answers it today."""
    by = collections.defaultdict(list)
    for a in awards:
        if a.get("buyerName"):
            by[norm_buyer(a["buyerName"])].append(a)
    out = []
    for key, rows in sorted(by.items(), key=lambda kv: -len(kv[1])):
        if key not in bmap:
            continue
        # never unpack into _ here: `_` is the translation accessor, and shadowing it
        # replaces every label on the page with an integer
        sl, name, _n = bmap[key]
        total = sum(chf_amount(a) or 0 for a in rows)
        table, nfirms = firm_table(rows, comp, pages, limit=40)
        cants = collections.Counter(a["canton"] for a in rows if a.get("canton"))
        sect = collections.Counter(
            (de(a, "cpvLabel") or a.get("cpvLabel") or "", str(a.get("cpvCode") or ""))
            for a in rows if a.get("cpvCode"))
        cant = cants.most_common(1)[0][0] if cants else ""
        b = [f'<div class="title"><div><p class="eyebrow">{_.buyer}'
             + (f" · {e(canton_name_or(cant, cant))}" if cant else "") + f'</p><h1>{e(name)}</h1>'
             f'<p class="sum">' + e(_m("buyer_lead", n=zuschlag(len(rows)), f=nfirms))
             + '</p></div><dl class="rail">'
             + (f"<dt>{_.canton}</dt><dd>{e(cant)}</dd>" if cant else "")
             + f"<dt>{_.companies}</dt><dd>{nfirms}</dd></dl></div>",
             '<div class="figures">',
             f'<div class="fig"><b>{len(rows)}</b><span>{_.awards}</span></div>',
             f'<div class="fig"><b>{nfirms}</b><span>{_.companies}</span></div>']
        if total:
            b.append(f'<div class="fig money"><b>{chf_big(total)}</b><span>{_.sum}</span></div>')
        b.append("</div>")
        b.append(f'<div class="half"><div><div class="runhead"><span>{_.companies}</span>'
                 f'<span>{_.by_awards}</span></div>' + table + "</div><div>")
        b.append(f'<div class="runhead"><span>{_.sectors}</span><span>CPV</span></div>'
                 + grafici.bars([(lab, k) for (lab, _c), k in sect.most_common(8)],
                                unit=_.awards, title=_i.sectors_cap)
                 + '<ul class="plain">')
        for (label, code), k in sect.most_common(8):
            cell = (f'<a href="{BASE}/{LANG}/bereich/{e(code)}/">{e(label[:48])}</a>' if code in sectors
                    else e(label[:48]))
            b.append(f'<li><div class="row">{cell}<span class="sub num">{k}</span></div></li>')
        b.append("</ul></div></div>")
        col = grafici.columns(sorted(per_month(rows).items()), title=_i.volume_cap)
        if col:
            b.append(f'<figure>{col}<figcaption>{e(_i.volume_cap)}</figcaption></figure>')
        b.append(f'<div class="sec"><div class="runhead"><span>{_.awards}</span>'
                 f"<span>{_.chronological}</span></div><div class=\"scroll\"><table><thead><tr>"
                 f'<th style="width:96px">{_.date}</th><th>{_.contract}</th><th>{_.award}</th>'
                 f'<th class="r">{_.amount}</th></tr></thead><tbody>')
        for a in sorted(rows, key=lambda x: x.get("publicationDate") or "", reverse=True)[:60]:
            ws = winners(a)
            who = " · ".join(
                (f'<a href="{BASE}/{LANG}/unternehmen/{e(slug(w))}/">{e(w)}</a>'
                 if slug(w) in pages else e(w)) for w in ws) or "—"
            b.append(f'<tr><td class="mono" style="font-size:12.5px">'
                     f'{e((a.get("publicationDate") or "")[:10])}</td>'
                     f'<td><a href="{BASE}/{LANG}/auftrag/{e(a.get("projectId"))}/">{e(de(a, "title")[:110])}</a></td>'
                     f"<td>{who}</td><td class=\"r num\">{e(money(a))}</td></tr>")
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
            p = chf_amount(r)
            if p is not None and len(ws) == 1:
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
        name = canton_name_or(code, code)
        table, nfirms = firm_table(rows, comp, pages)
        total = sum(chf_amount(a) or 0 for a in rows)
        sect = collections.Counter(
            (cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") or "", str(a.get("cpvCode") or ""))
            for a in rows if a.get("cpvCode"))
        top = sect.most_common(1)[0][1] if sect else 1
        b = [f'<div class="title"><div><p class="eyebrow">{_.canton}</p><h1>{e(name)}</h1>'
             f'<p class="sum">' + e(_m("canton_lead", n=zuschlag(len(rows)), f=nfirms))
             + "</p></div>"
             f'<dl class="rail"><dt>{_.abbr}</dt><dd class="mono">{e(code)}</dd>'
             f'<dt>{_.buyers}</dt><dd>{len({a.get("buyerName") for a in rows})}</dd></dl></div>',
             '<div class="figures">',
             f'<div class="fig"><b>{len(rows)}</b><span>{_.awards}</span></div>',
             f'<div class="fig"><b>{nfirms}</b><span>{_.companies}</span></div>']
        if total:
            b.append(f'<div class="fig money"><b>{chf_big(total)}</b><span>{_.sum}</span></div>')
        b.append("</div>")
        b.append(f'<div class="half"><div><div class="runhead"><span>{_.companies}</span>'
                 f"<span>{_.by_awards}</span></div>" + table + "</div>")
        b.append(f'<div><div class="runhead"><span>{_.sectors}</span><span>CPV</span></div>'
                 + grafici.bars([(lab, k) for (lab, _c), k in sect.most_common(8)],
                                unit=_.awards, title=_i.sectors_cap)
                 + '<ul class="plain">')
        for (label, code2), k in sect.most_common(10):
            cell = (f'<a href="{BASE}/{LANG}/bereich/{e(code2)}/">{e(label[:52])}</a>' if code2 in sectors
                    else e(label[:52]))
            b.append(f'<li><div class="row">{cell}<span class="sub num">{k}</span></div>'
                     f'<span class="bar" style="width:{max(4, round(k / top * 100))}%"></span></li>')
        b.append("</ul></div></div>")
        col = grafici.columns(sorted(per_month(rows).items()),
                              title=_i.volume_cap)
        if col:
            b.append(f'<figure>{col}<figcaption>{e(_i.volume_cap)}</figcaption></figure>')
        b.append(nav)
        write(f"/{LANG}/kanton/{code}/index.html",
              page(fit_title(_m("canton_title", name=name), _m("canton_suffix")),
                   _m("canton_desc", n=zuschlag(len(rows)), name=name, f=nfirms),
                   "\n".join(b), f"/{LANG}/kanton/{code}/", _.canton))

    cpv_list = [(c, r) for c, r in sorted(by_cpv.items(), key=lambda kv: -len(kv[1]))
                if c in sectors]
    for code, rows in cpv_list:
        label = next((cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") for a in rows
                      if cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "")), code)
        table, nfirms = firm_table(rows, comp, pages)
        cants = collections.Counter(a["canton"] for a in rows if a.get("canton"))
        b = [f'<div class="title"><div><p class="eyebrow">{_.sector} · CPV {e(code)}</p>'
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
             (lambda g: f'<figure>{g}<figcaption>{e(_i.volume_cap)}</figcaption></figure>'
              if g else "")(grafici.columns(sorted(per_month(rows).items()),
                                            title=_i.volume_cap)),
             '<div class="tags" style="margin-top:24px">'
             + "".join(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(c)}/">{e(c)} {k}</a>'
                       for c, k in cants.most_common(14)) + "</div>"]
        write(f"/{LANG}/bereich/{code}/index.html",
              page(fit_title(label, _m("sector_suffix", code=code)),
                   _m("sector_desc", n=zuschlag(len(rows)), label=label, f=nfirms),
                   "\n".join(b), f"/{LANG}/bereich/{code}/", _.sectors))
    return cant_list, cpv_list


# ------------------------------------------------------------- open tenders

SHOWN = 400            # rows on the all-tenders index; the rest live on the canton pages


ABO_MAIL = "abo@auftragsregister.ch"


def feed_xml(scope: str, self_path: str, rows: list) -> str:
    """Atom feed of the newest publications (max 100), newest first."""
    rows = sorted(rows, key=lambda t: t.get("publicationDate") or "", reverse=True)[:100]
    upd = (rows[0].get("publicationDate") if rows else DATA_DATE) or DATA_DATE
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<feed xmlns="http://www.w3.org/2005/Atom">',
           f"<title>{e(_m('feed_title', scope=scope))}</title>",
           f'<link href="{ORIGIN}{self_path}" rel="self"/>',
           f'<link href="{ORIGIN}{self_path.rsplit("/", 1)[0]}/"/>',
           f"<id>{ORIGIN}{self_path}</id>",
           f"<updated>{upd[:10]}T06:20:00Z</updated>"]
    for t in rows:
        d = (t.get("publicationDate") or DATA_DATE)[:10]
        label = cpv_label(t.get("cpvCode"), de(t, "cpvLabel") or t.get("cpvLabel") or "")
        summary = " · ".join(x for x in (t.get("buyerName") or "", f"{_.deadline}: {dmyy(t.get('offerDeadline') or '')}",
                                         t.get("canton") or "", label) if x)
        out.append("<entry>"
                   f"<title>{e(de(t, 'title'))}</title>"
                   f'<link href="{ORIGIN}/{LANG}/auftrag/{e(t.get("projectId"))}/"/>'
                   f'<id>{ORIGIN}/{LANG}/auftrag/{e(t.get("projectId"))}/</id>'
                   f"<updated>{d}T06:20:00Z</updated>"
                   f"<summary>{e(summary)}</summary></entry>")
    out.append("</feed>")
    return "\n".join(out)


def feed_head(path: str, scope: str) -> str:
    return (f'<link rel="alternate" type="application/atom+xml" '
            f'title="{e(_m("feed_title", scope=scope))}" href="{ORIGIN}{path}">\n')


def abo_block(feed_path: str) -> str:
    """The subscribe call-out shown on every tenders page."""
    return (f'<div class="sec"><p><a class="tag" href="{BASE}/{LANG}/ausschreibungen/abo/">'
            f'{e(_m("abo_cta"))}</a> <a class="tag" href="{ORIGIN}{feed_path}">{e(_m("feed_link"))}</a></p></div>')


BREVO_FORM = ("https://127f7d6f.sibforms.com/serve/MUIFAMYhHZXtCOd46O8Uq0H9DqIvbKjonCrMyCDZwBkCaUnmAUo6jz94s1wMVgHNKqluVahz4Xv"
              "QKlERvQhB9gdn9vtuebLrP6KdDdG-3VnrsJ2y6Ex6qU_Zcqp-Wv-dehKLXyYafqlL6rKK8lfXo4avjXTlNc7fPriLfxDj82TdfHK5WP8LSbpWo5N"
              "AVMf2FdpJXb1me5DNcx-xaQ==")

# The form posts straight to Brevo (double opt-in, list "Avvisi bandi"). Without JS the
# browser submits it normally and Brevo redirects to /abo/check/; with JS the answer is
# shown in place, in the page's language. Canton and sector pills are folded into the two
# text attributes the daily sender reads (KANTON, BRANCHE: codes joined by commas, or ALLE).
ABO_JS = """(function(){var f=document.getElementById('abo');if(!f)return;var m=f.querySelector('.msg'),b=f.querySelector('button');
function j(n){var v=[].map.call(f.querySelectorAll('input[name='+n+']:checked'),function(x){return x.value});return v.length?v.join(','):'ALLE'}
function fill(){f.elements.KANTON.value=j('k');f.elements.BRANCHE.value=j('b')}
f.addEventListener('change',fill);
f.addEventListener('submit',function(ev){ev.preventDefault();fill();b.disabled=true;m.className='msg';m.textContent=f.dataset.sending;
fetch(f.action+'?isAjax=1',{method:'POST',body:new FormData(f)}).then(function(r){return r.json()}).then(function(r){
if(r.success){m.textContent=f.dataset.ok;}else{b.disabled=false;m.className='msg err';m.textContent=f.dataset.err;}
}).catch(function(){b.disabled=false;f.submit();});});})();"""


def build_abo(by_cant: dict, by_sect: dict, sect_name) -> None:
    mail = ABO_MAIL
    cant_pills = "".join(
        f'<label><input type="checkbox" name="k" value="{e(c)}"><span class="tag">{e(canton_name_or(c, c))}</span></label>'
        for c in sorted(by_cant))
    top_sect = sorted(by_sect.items(), key=lambda kv: -len(kv[1]))[:24]
    sect_pills = "".join(
        f'<label><input type="checkbox" name="b" value="{e(c)}"><span class="tag">{e(sect_name(c)[:40])}</span></label>'
        for c, r in top_sect)
    form = (f'<div class="sec"><h2>{e(_m("abo_form_h2"))}</h2>'
            f'<form id="abo" class="form" method="post" action="{BREVO_FORM}" data-sending="{e(_m("abo_form_sending"))}" '
            f'data-ok="{e(_m("abo_form_ok"))}" data-err="{e(_m("abo_form_err", mail=mail))}">'
            f'<label class="f" for="abo-email">{e(_m("abo_form_email"))}</label>'
            f'<input id="abo-email" type="email" name="EMAIL" required autocomplete="email" placeholder="name@firma.ch">'
            f'<span class="f">{e(_m("abo_form_cantons"))}</span><div class="pills">{cant_pills}</div>'
            f'<span class="f">{e(_m("abo_form_sectors"))}</span><div class="pills">{sect_pills}</div>'
            f'<input type="hidden" name="KANTON" value="ALLE"><input type="hidden" name="BRANCHE" value="ALLE">'
            f'<input type="hidden" name="SPRACHE" value="{LANG}"><input type="hidden" name="locale" value="{LANG}">'
            f'<input type="text" name="email_address_check" value="" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">'
            f'<button type="submit">{e(_m("abo_form_submit"))}</button>'
            f'<p class="msg" aria-live="polite"></p>'
            f'<p class="sub">{e(_m("abo_form_consent"))} <a href="{BASE}/{LANG}/datenschutz/">{e(_.privacy)}</a></p>'
            f'</form><script>{ABO_JS}</script></div>')
    b = [f'<div class="title"><div><p class="eyebrow">{_.running}</p><h1>{e(_m("abo_h1"))}</h1>'
         f'<p class="sum">{e(_m("abo_lead"))}</p></div></div>',
         form,
         f'<div class="sec"><h2>{e(_m("abo_email_alt_h2"))}</h2><p>'
         + e(_m("abo_email_text", mail=mail)).replace(e(mail), f'<a href="mailto:{mail}?subject=Abo">{e(mail)}</a>')
         + "</p></div>",
         f'<div class="sec"><h2>{e(_m("abo_rss_h2"))}</h2><p>{e(_m("abo_rss_text"))}</p>'
         f'<p><a class="tag" href="{ORIGIN}/{LANG}/ausschreibungen/feed.xml">{e(_m("abo_rss_all"))}</a></p>'
         f'<h3>{e(_m("abo_by_canton"))}</h3><div class="tags">'
         + "".join(f'<a class="tag" href="{ORIGIN}/{LANG}/ausschreibungen/{e(c)}/feed.xml">{e(c)}</a>'
                   for c in sorted(by_cant))
         + f'</div><h3>{e(_m("abo_by_sector"))}</h3><div class="tags">'
         + "".join(f'<a class="tag" href="{ORIGIN}/{LANG}/ausschreibungen/bereich/{e(c)}/feed.xml">'
                   f'{e(sect_name(c)[:40])}</a>'
                   for c, r in top_sect)
         + "</div></div>"]
    write(f"/{LANG}/ausschreibungen/abo/index.html", page(
        fit_title(_m("abo_title"), " — auftragsregister.ch"), _m("abo_desc"),
        "\n".join(b), f"/{LANG}/ausschreibungen/abo/", _.tenders))

def canton_map(by_cant: dict) -> str:
    """The 26 cantons as a heat grid. Every tile is a plain link to a page that already
    exists, so it works with JavaScript switched off and a crawler follows all 26."""
    if not by_cant:
        return ""
    counts = {c: len(r) for c, r in by_cant.items()}
    hi, lo = max(counts.values()), min(counts.values())
    # Rank, not raw count: tender volume follows a power law (Zurich alone carries a
    # sixth of them), so a linear scale painted 13 of 26 cantons the same darkest shade
    # and the map said nothing. Ranking spreads the six steps evenly across the field.
    order = sorted(counts, key=lambda c: (-counts[c], c))
    rank = {c: i for i, c in enumerate(order)}
    tiles = []
    for c, rows in sorted(by_cant.items()):
        step = 6 - min(5, rank[c] * 6 // max(len(order), 1))
        tiles.append(
            f'<a class="s{step}" href="{BASE}/{LANG}/ausschreibungen/{e(c)}/" '
            f'title="{e(canton_name_or(c, c))}: {len(rows)}">'
            f'<span class="c">{e(c)}</span><span class="v">{len(rows)}</span></a>')
    legend = "".join(f'<i style="background:var(--d{i})"></i>' for i in range(1, 7))
    return (f'<div class="glass"><div class="gmap" style="padding-top:20px">'
            f'{"".join(tiles)}</div>'
            f'<div class="mleg"><span>{e(_m("open_map_few"))}</span>'
            f'<span class="sw">{legend}</span><span>{e(_m("open_map_many"))}</span>'
            f'<span style="margin-left:auto">{e(_m("open_map_note"))} '
            f'({lo}\u2009\u2013\u2009{hi})</span></div></div>')


def simap_compare() -> str:
    """What simap.ch is, and what this register adds. Stated as fact, without claiming
    simap lacks anything it actually offers: its alerts exist, they need an account."""
    yes, no_, link = _m("cmp_yes"), _m("cmp_no"), _m("cmp_link")
    rows = [("cmp_r1", yes, link), ("cmp_r2", yes, yes), ("cmp_r3", no_, yes),
            ("cmp_r4", no_, yes), ("cmp_r5", no_, yes), ("cmp_r6", no_, yes),
            ("cmp_r7", _m("cmp_acct"), yes), ("cmp_r8", _m("cmp_partly"), yes)]
    body = "".join(
        f'<tr><td>{e(_m(k))}</td>'
        f'<td class="c{" y" if a == yes else ""}">{e(a)}</td>'
        f'<td class="c{" y" if b == yes else ""}">{e(b)}</td></tr>' for k, a, b in rows)
    return (f'<div class="sec"><h2>{e(_m("cmp_h2"))}</h2>'
            f'<p class="sub" style="max-width:66ch;margin:10px 0 0">{e(_m("cmp_lead"))}</p>'
            f'<div class="glass"><div class="scroll"><table class="cmp">'
            f'<thead><tr><th>&nbsp;</th><th class="c" style="text-align:center">simap.ch</th>'
            f'<th class="c us" style="text-align:center">{e(_m("cmp_us"))}</th></tr></thead>'
            f"<tbody>{body}</tbody></table></div></div></div>")


def build_open(opens: list, sectors: set[str], buyer_slugs: dict) -> int:
    """The open tenders, whole and by canton.

    This is the part with intent behind it: someone searching for current tenders is
    looking to bid, not to browse. The pages carry the deadline first, because that is
    the fact that decides whether the rest matters.
    """
    def table(rows: list) -> str:
        out = [f'<div class="scroll"><table><thead><tr><th style="width:104px">{_.deadline}</th>'
               f'<th>{_.tenders}</th><th>{_.buyer}</th><th style="width:44px">{_.canton_abbr}</th>'
               "</tr></thead><tbody>"]
        for t in sorted(rows, key=lambda x: x.get("offerDeadline") or "9999"):
            out.append(
                f'<tr><td class="when mono" style="font-size:12.5px">'
                f'{e(dmyy(t.get("offerDeadline") or ""))}</td>'
                f'<td><a href="{BASE}/{LANG}/auftrag/{e(t.get("projectId"))}/">{e(de(t, "title")[:120])}</a>'
                + (f'<span class="sub" style="display:block;margin-top:2px">'
                   f'{e((cpv_label(t.get("cpvCode"), de(t, "cpvLabel") or t.get("cpvLabel") or "") or "")[:60])}</span>'
                   if (t.get("cpvLabel") or de(t, "cpvLabel")) else "")
                + f'</td><td>{e(t.get("buyerName"))}</td><td>{e(t.get("canton"))}</td></tr>')
        out.append("</tbody></table></div>")
        return "\n".join(out)

    by_cant = collections.defaultdict(list)
    for t in opens:
        if t.get("canton"):
            by_cant[t["canton"]].append(t)
    # Branche = CPV-Abteilung (erste zwei Ziffern): "45" Bauarbeiten, "71" Planung, "72" IT …
    by_sect = collections.defaultdict(list)
    for t in opens:
        code2 = str(t.get("cpvCode") or "")[:2]
        if code2.isdigit():
            by_sect[code2].append(t)
    def sect_name(code2: str) -> str:
        return cpv_label(code2 + "000000", "") or e(next((de(t, "cpvLabel") or t.get("cpvLabel") or "")
                                                          for t in by_sect[code2]) or code2)
    sect_nav = ('<div class="tags">'
                + "".join(f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/bereich/{e(c)}/">'
                          f'{e(sect_name(c)[:40])} {len(r)}</a>'
                          for c, r in sorted(by_sect.items(), key=lambda kv: -len(kv[1]))[:24])
                + "</div>")

    b = [f'<div class="title"><div><p class="eyebrow">{_.running}</p>'
         f"<h1>{e(_p.open_tenders_h1)}</h1>"
         f'<p class="sum">' + e(_m("open_lead", n=len(opens))) + "</p></div>"
         f'<dl class="rail"><dt>{_.as_of}</dt><dd class="mono">{DATA_DATE}</dd>'
         f"<dt>{_.cantons}</dt><dd>{len(by_cant)}</dd></dl></div>",
         f'<div class="figures">'
         f'<div class="fig money"><b class="num">{len(opens)}</b>'
         f'<span>{e(_m("open_kpi_open"))}</span></div>'
         f'<div class="fig"><b class="num">{len(by_cant)}</b>'
         f'<span>{e(_m("open_kpi_cantons"))}</span></div>'
         f'<div class="fig"><b class="num">{len(by_sect)}</b>'
         f'<span>{e(_m("open_kpi_sectors"))}</span></div>'
         f'<div class="fig"><b class="num">{e(dmyy(next(iter(sorted((t.get("offerDeadline") or "" for t in opens if t.get("offerDeadline")))), "")))}</b>'
         f'<span>{e(_m("open_kpi_next"))}</span></div></div>',
         f'<div class="sec"><h2>{e(_m("open_by_canton_h2"))}</h2>' + canton_map(by_cant) + "</div>",
         # sorted BEFORE slicing: taking 400 in file order and then sorting those
         # states "the nearest deadlines" about an arbitrary subset of the 588.
         '<div class="sec">' + table(sorted(
             opens, key=lambda x: x.get("offerDeadline") or "9999")[:SHOWN]) + "</div>",
         (f'<p class="sub" style="margin:12px 0 0">'
          + e(_if("showing_n", n=SHOWN, total=len(opens))) + "</p>"
          if len(opens) > SHOWN else ""),
         abo_block(f"/{LANG}/ausschreibungen/feed.xml"),
         f'<div class="sec"><h2>{e(_m("open_by_sector_h2"))}</h2>' + sect_nav + "</div>",
         f'<div class="sec"><h2>{e(_m("open_howto_h2"))}</h2><p>{e(_m("open_howto"))}</p></div>',
         simap_compare()]
    write(f"/{LANG}/ausschreibungen/index.html", page(
        _m("open_title", n=len(opens)), _m("open_desc", n=len(opens)),
        "\n".join(b), f"/{LANG}/ausschreibungen/", _.tenders,
        head_extra=feed_head(f"/{LANG}/ausschreibungen/feed.xml", _m("feed_all"))))
    write(f"/{LANG}/ausschreibungen/feed.xml", feed_xml(_m("feed_all"), f"/{LANG}/ausschreibungen/feed.xml", opens))
    build_abo(by_cant, by_sect, sect_name)

    for code2, rows in by_sect.items():
        name = sect_name(code2)
        b = [f'<div class="title"><div><p class="eyebrow">{_.running}</p>'
             f'<h1>{e(_m("open_sector_title", name=name, n=len(rows)))}</h1>'
             f'<p class="sum">' + e(_m("open_sector_desc", n=len(rows), name=name, code=code2)) + "</p></div>"
             f'<dl class="rail"><dt>{_.as_of}</dt><dd class="mono">{DATA_DATE}</dd>'
             f'<dt>CPV</dt><dd class="mono">{e(code2)}</dd></dl></div>',
             '<div class="sec">' + table(rows) + "</div>",
             f'<div class="tags" style="margin-top:22px">'
             f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/">{e(_i.all_open)}</a></div>']
        fp = f"/{LANG}/ausschreibungen/bereich/{code2}/feed.xml"
        b.insert(1, abo_block(fp))
        write(f"/{LANG}/ausschreibungen/bereich/{code2}/index.html", page(
            fit_title(_m("open_sector_title", name=name, n=len(rows)), " — simap"),
            _m("open_sector_desc", n=len(rows), name=name, code=code2),
            "\n".join(b), f"/{LANG}/ausschreibungen/bereich/{code2}/", _.tenders,
            head_extra=feed_head(fp, name)))
        write(f"/{LANG}/ausschreibungen/bereich/{code2}/feed.xml", feed_xml(name, fp, rows))

    for code, rows in by_cant.items():
        name = canton_name_or(code, code)
        b = [f'<div class="title"><div><p class="eyebrow">{_.running_canton}</p>'
             f'<h1>{e(_m("open_canton_title", name=name))}</h1>'
             f'<p class="sum">'
             + e(_m("open_canton_desc", n=len(rows), name=name)) + "</p></div>"
             f'<dl class="rail"><dt>{_.as_of}</dt><dd class="mono">{DATA_DATE}</dd>'
             f'<dt>{_.canton}</dt><dd class="mono">{e(code)}</dd></dl></div>',
             '<div class="sec">' + table(rows) + "</div>",
             f'<div class="tags" style="margin-top:22px">'
             f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(code)}/">{e(_if("awarded_in", c=code))}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/">{e(_i.all_open)}</a></div>']
        fp = f"/{LANG}/ausschreibungen/{code}/feed.xml"
        b.insert(1, abo_block(fp))
        write(f"/{LANG}/ausschreibungen/{code}/index.html", page(
            fit_title(_m("open_canton_title", name=name), " — simap"),
            _m("open_canton_desc", n=len(rows), name=name),
            "\n".join(b), f"/{LANG}/ausschreibungen/{code}/", _.tenders,
            head_extra=feed_head(fp, name)))
        write(f"/{LANG}/ausschreibungen/{code}/feed.xml", feed_xml(name, fp, rows))
    return 1 + len(by_cant) + len(by_sect)


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
    total = sum(chf_amount(a) or 0 for a in awards)
    months = sorted({(a.get("publicationDate") or "")[:7] for a in awards if a.get("publicationDate")})
    span = ""
    if months:
        fmt = lambda m: f"{m[5:7]}/{m[:4]}"
        span = fmt(months[0]) if len(months) == 1 else f"{fmt(months[0])} – {fmt(months[-1])}"
    firms = collections.Counter(slug(w) for a in awards for w in winners(a))
    soon = sorted((t for t in opens if t.get("offerDeadline")),
                  key=lambda t: t["offerDeadline"])[:8]

    b = [f'<div class="title"><div><h1>{e(_p.tagline)}</h1>'
         f'<p class="sum">{e(_p.lead)}</p></div>'
         f'<dl class="rail"><dt>{_.source}</dt><dd>{e(_p.source_note)}</dd>'
         + (f"<dt>{_.period}</dt><dd>{e(span)}</dd>" if span else "")
         + f"<dt>{_.updated}</dt><dd>{e(DATA_DATE)}</dd></dl></div>",
         '<div class="figures">',
         f'<div class="fig"><b>{chf(len(awards))}</b><span>{_.awards}</span></div>',
         f'<div class="fig"><b>{chf(len(firms))}</b><span>{_.companies}</span></div>']
    if total:
        b.append(f'<div class="fig money"><b>{chf_big(total)}</b><span>{_.sum_published}</span></div>')
    b.append(f'<div class="fig"><b>{chf(len(opens))}</b><span>{_.tenders}</span></div>'
             "</div>")

    b.append('<div class="cols"><div>'
             f'<div class="runhead"><span>{_.companies}</span>'
             f'<span>{e(span)}</span></div>'
             '<div class="scroll"><table><thead><tr><th style="width:34px"></th>'
             f'<th>{_.companies}</th><th style="width:46px">{_.canton_abbr}</th>'
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
        label = next((cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") for a in rows
                      if cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "")), code)
        b.append(f'<li><div class="row"><a href="{BASE}/{LANG}/bereich/{e(code)}/">{e(label[:40])}</a>'
                 f'<span class="sub num">{len(rows)}</span></div></li>')
    b.append("</ul></div></div>")

    b.append('<div class="tags" style="margin-top:32px;padding-top:22px;'
             'border-top:1px solid var(--rule)">'
             f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/">{e(_p.open_tenders_h1)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/unternehmen/">{e(_i.all_companies)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/auftraggeber/">{e(_i.all_buyers)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/kanton/">{e(_i.all_cantons)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/bereich/">{e(_i.all_sectors)}</a>'
             # l'iscrizione agli avvisi era raggiungibile solo dalle pagine bandi e
             # cantonali: dalla home, che e' la pagina piu' linkata del sito, non lo era
             f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/abo/">'
             f'{e(_m("abo_cta"))}</a></div>')
    col = grafici.columns(sorted(per_month(awards).items()), title=_i.volume_cap,
                          width=900, height=150)
    if col:
        b.append(f'<div class="sec"><div class="runhead"><span>{_i.volume_cap}</span>'
                 f'<span>{chf(len(awards))}</span></div>{col}</div>')

    # the one prominent notice on the home — in the reader's language, like the footer
    b.append(f'<div class="official" style="margin-top:36px">{e(_p.not_official)}</div>')

    write(f"/{LANG}/index.html", page(
        _m("home_title"), _m("home_desc", n=chf(len(awards))),
        "\n".join(b), f"/{LANG}/"))




OPERATOR_NAME = "Riccardo Di Lullo"
OPERATOR_EMAIL = "dilulloriccardo@gmail.com"     # already public in the repo history


def build_impressum() -> None:
    """The operator, named. Until now the only identity signal on the whole site was
    the username inside the canonical URLs — and on a custom domain even that goes
    away, making the site MORE anonymous exactly when it starts looking serious."""
    imp = lingue.IMP[LANG]
    b = [f'<div class="title"><div><p class="eyebrow">{e(_.register)}</p>'
         f'<h1>{e(imp["title"])}</h1></div><dl class="rail">'
         f'<dt>{e(imp["operator_h"])}</dt><dd>{e(OPERATOR_NAME)}<br>'
         f'{e(imp["operator_note"])}</dd>'
         f'<dt>{e(imp["contact_h"])}</dt><dd><a href="mailto:{e(OPERATOR_EMAIL)}">'
         f'{e(OPERATOR_EMAIL)}</a></dd></dl></div>',
         '<div class="sec prose" style="padding-top:24px">']
    for h, t in imp["paras"]:
        b.append(f"<h2 style=\"margin:22px 0 8px\">{e(h)}</h2><p>{e(t)}</p>")
    b.append("</div>")
    write(f"/{LANG}/impressum/index.html", page(
        f"{imp['title']} — {_.site}", imp["paras"][0][1][:170],
        "\n".join(b), f"/{LANG}/impressum/", _.register, imp["title"]))


def build_privacy() -> None:
    """A privacy notice is owed because ~3.3% of the 10,547 awardee names are natural
    persons (sole traders), so the site processes personal data even though every field
    it shows was already officially published. The page is one URL per language under
    /datenschutz/ regardless of language, so the footer link needs no per-language path."""
    pr = lingue.PRIV[LANG]
    b = [f'<div class="title"><div><p class="eyebrow">{e(_.register)}</p>'
         f'<h1>{e(pr["title"])}</h1></div><dl class="rail">'
         f'<dt>{e(pr["operator_h"])}</dt><dd>{e(OPERATOR_NAME)}<br>'
         f'{e(pr["operator_note"])}</dd>'
         f'<dt>{e(pr["contact_h"])}</dt><dd><a href="mailto:{e(OPERATOR_EMAIL)}">'
         f'{e(OPERATOR_EMAIL)}</a></dd></dl></div>',
         '<div class="sec prose" style="padding-top:24px">']
    for h, t in pr["paras"]:
        b.append(f"<h2 style=\"margin:22px 0 8px\">{e(h)}</h2><p>{e(t)}</p>")
    b.append("</div>")
    write(f"/{LANG}/datenschutz/index.html", page(
        f"{pr['title']} — {_.site}", pr["paras"][0][1][:170],
        "\n".join(b), f"/{LANG}/datenschutz/", _.register, pr["title"]))


def build_abo_status() -> None:
    """The two pages Brevo sends people to: after the form (check your mail) and after
    the opt-in click (done). The redirect target is one fixed URL per form, so these
    live outside the language tree, carry all four languages and stay out of the index."""
    for slug, key in (("check", "abo_check"), ("ok", "abo_ok")):
        blocks = "".join(
            f'<p><b>{e(NAMES[l])}</b> — {e(lingue.m(key, l))} '
            f'<a href="{BASE}/{l}/ausschreibungen/abo/">{e(lingue.m("abo_back", l))}</a></p>' for l in LANGS)
        title = lingue.m(key + "_title", "de")
        html = page(title, lingue.m(key, "de"),
                    f'<div class="title"><div><p class="eyebrow">{e(_.tenders)}</p><h1>{e(title)}</h1></div></div>'
                    f'<div class="sec">{blocks}</div>', f"/abo/{slug}/", _.tenders, robots="noindex,nofollow")
        html = re.sub(r'<link rel="alternate"[^>]*>\n?', "", html)
        for l in LANGS:      # the masthead language switch: point it at the real abo pages
            html = html.replace(f'href="{BASE}/{l}/abo/{slug}/"', f'href="{BASE}/{l}/ausschreibungen/abo/"')
        write(f"/abo/{slug}/index.html", html)


def build_root() -> None:
    """The root used to be a language picker. Search Console (2026-09-07) showed it
    was the ONLY page Google indexed, ranking at position 61 for "ausschreibungen
    schweiz" with nothing on it, and every observed query was German. So the root now
    carries the German homepage itself; the language switch stays in the masthead.
    Canonical points at /de/ so the two copies consolidate instead of competing;
    x-default keeps pointing at / (hreflang alternates are copied along)."""
    de_home = OUT / "de" / "index.html"
    html = de_home.read_text(encoding="utf-8")
    html = html.replace(f'<link rel="canonical" href="{ORIGIN}/de/">',
                        f'<link rel="canonical" href="{ORIGIN}/de/">', 1)
    write("/index.html", html)




def build_language(awards: list, opens: list) -> tuple[int, int, int, int, int, int]:
    comp = profile(awards)
    open_for = matches(comp, opens)
    sectors = sector_pages(awards)
    buyer_slugs = buyer_map(awards)
    keep = {n for n, c in comp.items() if len(c["awards"]) >= MIN_AWARDS}
    peer_map = peers(comp, keep)
    pages = build_companies(comp, open_for, sectors, buyer_slugs, peer_map)
    n_aw = build_awards(awards, opens, pages, sectors, buyer_slugs)
    buyers = build_buyers(awards, comp, pages, sectors, buyer_slugs)
    cant_list, cpv_list = build_hubs(awards, comp, pages, sectors)
    n_open = build_open(opens, sectors, buyer_slugs)
    build_index("/unternehmen/", _.companies, _i.companies_h1, _i.companies_lead,
                [(sl, p["name"], p["n"]) for sl, p in pages.items()],
                _i.companies_title, _if("companies_desc", n=len(pages)))
    build_index("/auftraggeber/", _.buyers, _i.buyers_h1, _i.buyers_lead,
                [(sl, n, k) for sl, n, k in buyers],
                _i.buyers_title, _if("buyers_desc", n=len(buyers)))
    build_index("/kanton/", _.cantons, _.cantons, _i.cantons_lead,
                [(c, canton_name_or(c, c), len(r)) for c, r in cant_list],
                _i.cantons_title, _i.cantons_desc)
    build_index("/bereich/", _.sectors, _i.sectors_h1, _i.sectors_lead,
                [(c, next((cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") or c for a in r
                           if cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "")), c), len(r))
                 for c, r in cpv_list],
                _i.sectors_title, _i.sectors_desc)
    build_home(pages, comp, awards, opens, cant_list, cpv_list)
    build_impressum()
    build_privacy()
    return (len(pages), n_aw, len(buyers), len(cant_list), len(cpv_list), n_open)


def main() -> None:
    global LANG
    # docs/ is wiped every build, so the IndexNow key file — proof of ownership,
    # served at the site root — is put back afterwards rather than lost each night.
    keyfile = ROOT / "indexnow.key"
    if OUT.exists():
        shutil.rmtree(OUT)
    awards, opens = load()
    global DATA_DATE
    DATA_DATE = max(((a.get("publicationDate") or "")[:10] for a in awards), default=TODAY) or TODAY
    print(f"  dati    : {len(awards)} aggiudicazioni · {len(opens)} bandi aperti · dati al {DATA_DATE}")
    for lang in LANGS:
        LANG = lang
        grafici.BILLION, grafici.MILLION, grafici.DEC = lingue.BIG_UNITS[lang]
        n = build_language(awards, opens)
        print(f"  {lang}      : {n[0]} imprese · {n[1]} appalti · {n[2]} committenti "
              f"· {n[3]} cantoni · {n[4]} settori · {n[5]} bandi")
    LANG = "de"
    build_root()
    build_abo_status()
    # Fonts are served from our own origin: the Google Fonts link both blocked first
    # paint for ~2 seconds on mobile and sent every visitor's IP to Google — the same
    # embedding European courts have already sanctioned. docs/ is wiped every build,
    # so the woff2 files are copied in each time, like the CNAME and the IndexNow key.
    fdir = ROOT / "fonts"
    fontcss = ""
    if fdir.exists():
        (OUT / "fonts").mkdir(parents=True, exist_ok=True)
        for f in fdir.glob("*.woff2"):
            shutil.copy(f, OUT / "fonts" / f.name)
        fontcss = (fdir / "fonts.css").read_text().replace("/fonts/", f"{BASE}/fonts/")
    write("/style.css", fontcss + "\n" + CSS)
    if keyfile.exists():
        k = keyfile.read_text().strip()
        write(f"/{k}.txt", k)
    # Pages reads the custom domain from a CNAME file in the publish directory, and
    # this directory is wiped on every build — so the file is emitted here, like the
    # IndexNow key, or the nightly rebuild would silently detach the domain.
    host = SITE.split("//", 1)[-1]
    if not host.endswith("github.io"):
        write("/CNAME", host + "\n")
    # 76k files do not need a Jekyll pass; skipping it makes Pages builds faster
    write("/.nojekyll", "")
    print(f"  sitemap : {build_sitemap()} URL in {len(LANGS)} lingue")



def page_dates() -> dict[str, str]:
    """URL -> data dell'ultima modifica reale (vedi build_sitemap). Vuoto se git non risponde."""
    import subprocess
    try:
        rel = OUT.relative_to(ROOT).as_posix()
        def url_of_rel(path: str) -> str | None:
            if not path.startswith(rel + "/") or not path.endswith("index.html"):
                return None
            return "/" + path[len(rel) + 1:-len("index.html")]
        out: dict[str, str] = {}
        st = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=ROOT,
                            capture_output=True, text=True, timeout=600).stdout
        for line in st.splitlines():
            u = url_of_rel(line[3:].strip().strip('"'))
            if u:
                out[u] = DATA_DATE            # cambiata in questo build
        log = subprocess.run(["git", "log", "-n", "10", "--format=%x01%cs", "--name-only", "--", rel],
                             cwd=ROOT, capture_output=True, text=True, timeout=600).stdout
        cur = DATA_DATE
        for line in log.splitlines():
            if line.startswith("\x01"):
                cur = line[1:].strip() or cur
                continue
            u = url_of_rel(line.strip())
            if u and u not in out:
                out[u] = cur                 # primo (= piu' recente) commit che l'ha toccata
        return out
    except Exception as exc:                 # mai bloccare la pubblicazione per la sitemap
        print(f"  sitemap : lastmod da git non disponibile ({type(exc).__name__}), uso {DATA_DATE}")
        return {}

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
        if "/auftrag/" in u or u.startswith("/abo/"):   # noindex: fuori dalla sitemap (schede: vedi build_awards; /abo/: pagine di ritorno Brevo)
            continue
        seg = u.strip("/").split("/")[0]
        (by_lang[seg] if seg in by_lang else root).append(u)

    # <lastmod> = data dell'ultima modifica REALE della pagina, non del build: Google ignora le
    # sitemap in cui tutte le date cambiano ogni giorno. Pagine cambiate in questo build (non ancora
    # committate) -> DATA_DATE; le altre -> data dell'ultimo commit che le ha toccate; fallback DATA_DATE.
    dates = page_dates()

    def doc(urls: list[str]) -> str:
        head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        body = "".join(f"<url><loc>{ORIGIN}{u}</loc><lastmod>{dates.get(u, DATA_DATE)}</lastmod></url>"
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
           + "".join(f"<sitemap><loc>{ORIGIN}/{f}</loc><lastmod>{DATA_DATE}</lastmod></sitemap>"
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
