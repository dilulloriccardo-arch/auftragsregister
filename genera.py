#!/usr/bin/env python3
"""Build the static register from simap award and tender data.

The look is design A2 "Brass" (step 4, 15.10.2026): black, warm off-white and metallic
brass; League Gothic in capitals for the site's and the sections' headings, Instrument Sans
for everything read, tabular figures in every column of numbers, an asymmetric grid with
the metadata on a rail, running heads. The home carries the halftone map of the open
tenders per canton and the motion of js/home.js; the data pages are a calm instrument.

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

import calendar
import collections
import csv
import hashlib
import html
import io
import json
import os
import pathlib
import re
import shutil
import unicodedata
import urllib.parse
from datetime import date, datetime, timedelta, timezone

import formato
import grafici
import kantone
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
    s = lingue.m(key, LANG, **kw)
    # French elision where a filled-in phrase meets a preposition: "de une seule entreprise"
    return s.replace("de une ", "d’une ") if LANG == "fr" else s


class _Idx:
    def __getattr__(self, key: str) -> str:
        return lingue.i(key, LANG)


_i = _Idx()


def _if(key: str, **kw) -> str:
    return lingue.i(key, LANG, **kw)


_ = _Words()
_p = _Prose()
MIN_AWARDS = 2          # below this a company page is thin; the record still shows in hubs
JUMP_MIN = 8            # from this many awards a company page links its lists under its figures (fix round 3)
# The moment of the build: a tender whose deadline is behind it is no longer open, even on the
# deadline's own day (a deadline of today 00:00 was listed as open all day; 08.10.2026).
# GENERA_TODAY (step 3b, 15.10.2026) sets it for a test: '2026-10-16' (that day at 08:20, the nightly's
# hour) or '2026-10-16T14:00'. Two builds of the same data a day apart then differ only where something
# really changed: a tender passed its deadline, an expired one left the 90 days. No page states 'heute',
# 'morgen' or 'noch 5 Tage' any more; the reader's own clock does, through /stand.js.
def _build_now() -> datetime:
    raw = os.environ.get("GENERA_TODAY", "").strip()
    if not raw:
        return datetime.now().astimezone()
    d = datetime.fromisoformat(raw if "T" in raw else raw + "T08:20")
    return d if d.tzinfo else d.astimezone()


NOW = _build_now()
TODAY = NOW.date().isoformat()
# A tender keeps its page this many days after its deadline: the links in alert e-mails and feeds
# pointed at a page deleted the next morning (08.10.2026). The 404 page states the same figure.
EXPIRED_DAYS = 90
# Data mostrata nelle pagine = data dell'ultimo dato pubblicato (non del giorno di build): cosi'
# le pagine i cui dati non cambiano restano identiche da una notte all'altra (git, IndexNow, Google).
DATA_DATE = TODAY
# Monthly charts (set once in main() from the national series): FULL_FROM is the first
# month the data covers fully, RAMP_START..RAMP_END the build-up months before it (drawn
# striped, with a note), CUR_MONTH the month of DATA_DATE and CUR_PARTIAL whether it is
# still running.
FULL_FROM = RAMP_START = RAMP_END = CUR_MONTH = ""
CUR_PARTIAL = False
# award publications without a title and without a winner, left out of every figure (load), and the
# tenders without a readable deadline, not listed as open (load); the about page and the hub say so
INCOMPLETE: list = []
NO_DEADLINE = [0]
# the latest day simap published a tender on (load): the home's 'N neu am …' counts the tenders first
# published that day
LATEST_TENDER_DAY = [""]
# the first publication day of the tenders the archive holds (load): the 90 days are counted from there (fix round 3)
TENDERS_SINCE = [""]
# path -> the newest publication date among the records the page shows: the sitemap's <lastmod>
# (step 3a, 14.10.2026; it was the date of the last git commit that touched the file, and in a build
# whose docs/ is not committed, the build date for every URL)
LASTMOD: dict = {}
# (day of the first publication, cantons, CPV division) of every tender project the data holds (load): the
# alert form's preview of how many new tenders a week a selection brings (step 3b)
FIRSTS: list = []
# the open tenders of this build (main): /stand.js gets their nearest deadline
OPENS: list = []

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
    """Text for HTML, and for an attribute in double quotes — every attribute the site writes is: the
    apostrophe stays itself (step 3a: 143'000 '&#x27;' over the site, 0.7 MB)."""
    return html.escape(str(v), quote=False).replace('"', "&quot;") if v is not None else ""


def plural(n: int, one: str, many: str) -> str:
    """'1 Unternehmen / 27 Unternehmen', '1 impresa / 22 imprese': every 'number + noun'
    goes through here, so the count is grouped and the noun agrees. French takes the singular for
    zero too ('0 adjudication'; fix round 2)."""
    return f"{formato.count(n)} {one if singular(n) else many}"


def singular(n) -> bool:
    """The count takes the singular: one, and in French zero as well."""
    return n == 1 or (n == 0 and LANG == "fr")


_ONE = {"awards": "award", "companies": "company", "buyers": "buyer", "cantons": "canton"}


def lab_n(n: int, many: str) -> str:
    """A tile or rail label that agrees with the figure above it: '1 Committente', not
    '1 Committenti' (193 company pages, 34 sector pages, 7 buyer pages; verifier 28.09.2026)."""
    return lingue.t(_ONE[many] if singular(n) else many, LANG)


def firms(n: int) -> str:
    """'27 Unternehmen'; one is 'ein einziges Unternehmen' / 'une seule entreprise': '3
    adjudications en faveur de 1 entreprise' read like a form letter (verifier, 28.09.2026)."""
    return lingue.COMPANY_ONE[LANG] if n == 1 else plural(n, *lingue.COMPANY[LANG])


def open_n(n: int) -> str:
    return plural(n, *lingue.OPEN_TENDERS[LANG])


def open_contracts(n: int) -> str:
    """The count in a canton's tender title: '341 offen', '1 aperto'; none: 'zurzeit keine offen' (step 5)."""
    return plural(n, *lingue.OPEN_CONTRACTS[LANG]) if n else lingue.OPEN_NONE[LANG]


def first_fit(*cands: str, limit: int = 64) -> str:
    """The first candidate that fits, never an ellipsis on a title template (SEO audit 28.09.2026)."""
    for c in cands:
        if c and len(c) <= limit:
            return c
    return fit_title(cands[-1], "")


def cur_of(row: dict) -> str:
    return (row.get("winnerCurrency") or "CHF").strip().upper()


def cant_of(code: str, name: str | None = None) -> str:
    """The canton with the preposition French needs: 'de Vaud', 'du Valais'."""
    return lingue.canton_of(code, name or canton_name_or(code, code), LANG)


def tt(iso: str, text: str) -> str:
    return formato.time_tag(iso, text)


def deadline_at(t: dict) -> datetime | None:
    """The submission deadline as a moment: simap gives the local time with its offset
    ('2026-10-08T16:00:00+02:00'); a date alone runs to the end of that day."""
    raw = str(t.get("offerDeadline") or "").strip()
    if raw.endswith("Z"):
        # the nightly's Python 3.9 cannot read 'Z': the tender would vanish from the site and the e-mails
        raw = raw[:-1] + "+00:00"
    try:
        d = datetime.fromisoformat(raw)
    except ValueError:
        try:
            raw = raw[:10]
            d = datetime.fromisoformat(raw)
        except ValueError:
            return None
    if len(raw) <= 10:
        d = d.replace(hour=23, minute=59, second=59)
    return d if d.tzinfo else d.astimezone()


def due_cell(iso: str, text: str, until: bool = False, soon: bool = False) -> tuple[str, str]:
    """(extra class, content) of a deadline in a tender list: the date, absolute ('bis 25.09.2026').
    Step 3b (15.10.2026): no 'läuft heute ab, 16.00 Uhr' and no .today/.soon in the page any more: they
    changed with the build's date, rewrote thousands of pages every night for no new fact, and were wrong
    by the evening. /stand.js reads data-deadline on the row and writes them from the reader's clock;
    without JavaScript the date stands, which is always true. The class slot stays for the callers."""
    return "", (f"{_.until} " if until else "") + tt(iso, text)


def fold(s: str) -> str:
    """Sort key that files É under E and Ö under O, instead of after Z."""
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().casefold()


def abbr_canton(code: str, src: str = "") -> str:
    """A canton code in a row, its name on hover. src "auftraggeber" (kantone.py): the publication names
    no place and the canton is the buyer's seat; class fb marks it with an asterisk that the note under
    the list (fb_note) explains (step 3a, 14.10.2026)."""
    if not code:
        return ""
    fb = ' class="fb"' if src == "auftraggeber" else ""
    return f'<abbr{fb} title="{e(canton_name_or(code, code))}">{e(code)}</abbr>'


def cantons_cell(t: dict) -> str:
    """The canton cell of a tender row: every canton the tender is listed under (kantone.cantons_of),
    the buyer's seat marked."""
    ks = t.get("_cants") or ([t["canton"]] if t.get("canton") else [])
    return " ".join(abbr_canton(k, t.get("_ksrc", "")) for k in ks)


def multi_mark(t: dict) -> str:
    """'mehrere Kantone · ' before a tender row's sub-line when its lots lie in several cantons."""
    return f"{_.multi_cantons} · " if len(t.get("_cants") or []) > 1 else ""


def fb_foot(rows: list, cls: str = "") -> str:
    """The note under a list whose rows show a buyer's-seat canton (abbr.fb): what the asterisk means."""
    if not any(r.get("_ksrc") == "auftraggeber" and r.get("canton") for r in rows):
        return ""
    return f'<p class="sub fbn{cls}">* {e(_.fb_note)}</p>'


_INVISIBLE = re.compile("[​-‍﻿]")


def _ws(s: str) -> str:
    """Collapse ASCII whitespace only. str.split() also splits on U+00A0 and U+202F, and
    re-joining with a plain space undid the French typography in every meta description,
    title and short label that passed through it (verifier, 28.09.2026). Zero-width spaces
    from the source go too: invisible, but they counted against the title's 64 characters."""
    return re.sub(r"[ \t\r\n\f\v]+", " ", _INVISIBLE.sub("", s or "")).strip()


_LEAD_STOP = {"und", "oder", "sowie", "et", "ou", "e", "o", "ed", "and", "or"}

_PAIRS = {"(": ")", "[": "]", "«": "»", "‹": "›", "„": "“", "“": "”"}
_CLOSERS = {")", "]", "»", "›", "”"}


def _brackets(t: str) -> tuple[list[int], int]:
    """(positions of the openers left unclosed, position of the first closer without an
    opener or -1). Straight double quotes count by parity; '“' closes a German '„' and
    otherwise opens an English quote."""
    stack: list[int] = []
    stray = -1
    quote = -1
    for i, ch in enumerate(t):
        if ch == '"':
            quote = -1 if quote >= 0 else i
        elif ch == "“" and stack and t[stack[-1]] == "„":
            stack.pop()
        elif ch in _PAIRS:
            stack.append(i)
        elif ch in _CLOSERS:
            if stack and _PAIRS[t[stack[-1]]] == ch:
                stack.pop()
            elif stray < 0:
                stray = i
    if quote >= 0:
        stack.append(quote)
    return sorted(stack), stray


def _balanced(t: str) -> bool:
    op, stray = _brackets(t)
    return not op and stray < 0


def _suspended(w: str) -> bool:
    """'Turn-', 'Alters-', 'Wohn-': the first half of a German suspended compound, which
    reads as a whole word once its hyphen is stripped ('Sanierung Turn … Bedachungsarbeiten')."""
    return len(w) > 1 and w.endswith("-") and w[-2].isalpha()


def _susp(w: str) -> str:
    """'Heizungs-,', 'Hellfeld-/', 'Nutzer-', 'Natur-' -> the same word ending on its hyphen;
    '' for any other word. Whatever follows ('und', a comma, a slash, the next half 'Sicherheits-'
    or 'in'), a word written with a trailing hyphen is the first half of a compound."""
    w = w.rstrip(",/;")
    return w if _suspended(w) else ""


# a lone separator left at the end of a cut ('Sanierung Wohnheim West |…')
_SEPS = {"·", "-", "–", "—", "/", "&", "+", "|"}


def cut_end(t: str, n: int, safe: bool = True, back: bool = True) -> str:
    """The first n characters of t cut back to a whole word, without a trailing 'und', 'de',
    'per', 'aus', 'sur' …, a lone separator, or an abbreviation cut from its word ('St.' of
    'St. Bernhardstrasse'), and never inside a bracket or quote it opened (safe=True, and only
    when t itself is balanced).

    The first half of a suspended compound keeps its hyphen: 'Installation von Heizungs-,
    Lüftungs-…'. Dropping it with the words before it cut 'Heizungs-, Lüftungs- und
    Klimaanlagen' down to 'Installation…', and stripping only the hyphen turned 'Lift-,
    Brandschutz- und Erdbebensanierung' into 'Lift' (verifier, 28.09.2026)."""
    t = _ws(t)
    if n >= len(t):
        return t
    c = t[:n]
    if t[n] != " ":
        if " " in c:
            c = c[:c.rfind(" ")]      # never inside a word, however long the word
        else:
            # one long token ('596-GyEchallens_Lot6_SciageSechage…'): back to its last joint
            j = max(c.rfind("_"), c.rfind("/"), c.rfind("-"))
            if j >= 8:
                c = c[:j]
    check = safe and _balanced(t)
    while True:
        c = c.rstrip(" ,;:–—/·|")
        hw = c.split(" ")
        while len(hw) > 1 and (hw[-1].lower().strip(",;:(«„“\"") in _TAIL_STOP
                               # half a name: 'Lycée Denis-de…' of 'Denis-de Rougemont'
                               or ("-" in hw[-1][1:] and hw[-1].rsplit("-", 1)[1].lower() in _TAIL_STOP)
                               or hw[-1] in _SEPS
                               or (hw[-1].endswith(".") and len(hw[-1]) <= 4)):
            hw.pop()
        # a stop word glued on by a no-break space in the source ('Adobe\u202fpour')
        m = re.search(r"[\u00a0\u202f]([^\u00a0\u202f]*)$", hw[-1])
        if m and m.start() and m.group(1).lower().strip(",;:") in _TAIL_STOP:
            hw[-1] = hw[-1][:m.start()]
            c = " ".join(hw)
            continue
        s = _susp(hw[-1])
        if s:
            hw[-1] = s
            c = " ".join(hw)
        else:
            c = " ".join(hw).rstrip(" ,.;:-–—/·|")
        if check:
            op, _stray = _brackets(c)
            pre = c[:op[0]].rstrip(" ,;:-–—/·|") if op else ""
            # back to before the bracket when that still leaves a name ('Neubau Kindergarten
            # (inkl. Umgebung…' -> 'Neubau Kindergarten…'); otherwise the caller closes it
            if back and op and len(pre.split()) >= 2 and len(pre) >= 0.4 * n:
                c = pre
                continue
        return c


def _shown(core: str) -> tuple[int, int]:
    """(words, characters) a cut title still shows of its name; the parts of a hyphenated
    compound count as words ('Structured-Illumination-Mikroskop' says as much as three)."""
    s = core.replace("…", " ")
    return (sum(1 for w in re.split(r"[\s\-_/]+", s) if re.search(r"[^\W\d_]", w)),
            len(s.replace(" ", "")))


def _poor(core: str) -> bool:
    """A cut that no longer says what the page is about: one word, under twenty characters,
    or two short words before the ellipsis ('Installation…', 'Eidgenössisches…', 'Lift-…',
    'Aufwertung Gennersbrunner-…'). Two long German compounds ('Ingenieurleistungen
    Siedlungsentwässerung…') still say it."""
    if "…" not in core:
        return False
    w, n = _shown(core)
    return w < 2 or n < 20 or (w < 3 and n < 30)


def rank_titles(cands: list, most: bool = False) -> list[str]:
    """[(title, the part of it taken from the name)] in order of preference -> the titles,
    those whose cut still says something first, in their order (most=True: the one showing
    the most words of the name first — a buyer's or a company's name is what its page is
    searched by); the poor ones after them, the one showing the most first. 22 indexed pages
    and 438 award pages per language had come down to one word and an ellipsis (verifier,
    28.09.2026)."""
    good = [x for x in cands if not _poor(x[1])]
    if most:
        good.sort(key=lambda x: -_shown(x[1])[0])
    good = [t for t, _core in good]
    poor = sorted((x for x in cands if _poor(x[1])), key=lambda x: (-_shown(x[1])[0], -_shown(x[1])[1]))
    return list(dict.fromkeys(good + [t for t, _core in poor]))


def _ft(text: str, suffix: str, **kw) -> tuple[str, str]:
    """fit_title, with the part of the title that comes from the text."""
    t = fit_title(text, suffix, **kw)
    return t, (t[:-len(suffix)] if suffix else t)


def fit_title(text: str, suffix: str, limit: int = 64, tail_share: float = 0.4,
              head_min: int = 0, gap1: bool = False) -> str:
    """A title Google will not truncate, cut so it still identifies the page.

    Cutting only the tail produced 747 titles shared by 3,036 pages: awards from one
    big project share a long prefix and differ only in the part that gets thrown away —
    28 pages all reading "Flumenthal; Zentralgefängnis Kanton Solothurn (ZGSO)…" where
    the real subject was Brandschutzbekleidung, Innentüren, Gärtnerarbeiten. So with
    tail_share > 0 the ellipsis may go in the MIDDLE: the head keeps the project, the tail
    keeps the trade.

    Both halves are cut on whole words and never split a bracket or a quote: a tail never
    starts inside '(…)' or '«…»' (it moves past the closing mark, or widens to the opening
    one), a head never ends inside one, a tail is never a bare number ('Lose 340 … 3599'
    read as a range) and the suspended compound 'Turn-' keeps its hyphen. A middle cut that
    would drop a single word is not worth its ellipsis: the end is cut instead — unless that
    end cut leaves a poor title ('Eidgenössisches…', 'Gesundheitsinformationssystem…'), where
    the middle cut may keep a one-word head or skip a one-word gap ('Eidgenössisches … ENSI').
    tail_share=0 cuts at the end only; head_min keeps at least that many leading characters
    in the head (a buyer's name up to its first comma: the town); gap1=True allows the
    one-word gap where it is what tells two pages apart ('Hälg & Co. AG, … Zürich').
    """
    room = limit - len(suffix)
    text = _ws(text)
    if len(text) <= room:
        return text + suffix
    check = _balanced(text)

    def end_only(back: bool = True) -> str:
        # a bracket or quote the cut could not avoid is closed after the ellipsis: '(Etappe 2…)'
        n = room - 1
        while n > 0:
            h = cut_end(text, n, back=back)
            op = _brackets(h)[0] if check else []
            close = "".join('"' if h[i] == '"' else _PAIRS[h[i]] for i in reversed(op))
            if len(h) + 1 + len(close) <= room:
                out = h + "…" + close
                if back and _poor(out):
                    # 'Volkswirtschaftliche Studien…' -> '… Studien zu "Impulse für Wachstum…"'
                    alt = end_only(False)
                    alt = alt[:len(alt) - len(suffix)]
                    if _shown(alt) > _shown(out):
                        out = alt
                return out + suffix
            n -= 1
        return text[:room - 1] + "…" + suffix

    end = end_only()
    if tail_share <= 0 or room < 20:
        return end
    end_core = end[:len(end) - len(suffix)]
    poor_end = _poor(end_core)
    # tail candidates: every whole-word ending of the text, the preferred length first
    starts = [0] + [i + 1 for i, ch in enumerate(text) if ch == " "]
    tail_room = (room - head_min - 3) if head_min else int(room * tail_share)
    if tail_room < 8:
        return end
    cands = [text[i:] for i in starts[1:]]
    fits = sorted((c for c in cands if len(c) <= tail_room), key=len, reverse=True)
    wider = sorted((c for c in cands if tail_room < len(c) <= room - 12), key=len)

    def tail_ok(tail: str) -> bool:
        first = tail.split(" ")[0]
        if (not tail or first.lower() in _LEAD_STOP or first in _SEPS
                or first.startswith(("-", ",", ";", ":", ".", ")", "]", "»", "”", "|"))):
            return False
        if not re.search(r"[^\W\d_]", tail):          # a bare number reads as a range
            return False
        if check and not _balanced(tail):
            return False
        return True

    for tail in fits + wider:
        tail = tail.strip()
        if not tail_ok(tail):
            continue
        head = cut_end(text, room - len(tail) - 3)
        if (len(head.split(" ")) < 2 and not poor_end) or (head_min and len(head) < head_min - 1):
            continue
        if head.split(" ")[-1].lower() in _TAIL_STOP:        # 'Ein … die BioImaging Platform'
            continue
        # a head is whole words: never the front of one long word or of a hyphenated one
        # ('Unterstützungsdienstleist …', 'Breitband … ' of 'Breitband-Frequenzvervielfacher')
        if text[len(head):len(head) + 1] not in ("", " ", ",", ";", ":", "/", "|") and not head.endswith("-"):
            continue
        if check and not _balanced(head):
            continue
        t0 = len(text) - len(tail)
        if len(head) >= t0:
            continue
        gap = text[len(head):t0].strip(" ,.;:-–—/·|")
        if len(gap.split()) <= 1 and not gap1 and not poor_end:
            return end                   # a one-word gap is not worth the ellipsis
        if head[-1:].isdigit() and tail[:1].isdigit():
            continue
        mid = f"{head} … {tail}"
        if poor_end and _shown(mid) <= _shown(end_core):
            continue
        return mid + suffix
    return end


# where a project name ends and a lot's own name begins: " / BKP 240", " - BKP 281.0",
# ": BKP 250", ", Los 3", " (Los 2)"
_LOT_SEP = re.compile(r"\s+[-–—/|:]\s+|[,;:]\s+|\s+\(")


def _stem(a: str, b: str) -> str:
    """The project name two lot titles share, cut at a separator; '' when they share none
    worth a line of its own (at least two words and twenty characters)."""
    if a == b:
        return a
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    for x, y in ((a, b), (b, a)):
        if n == len(x) and _LOT_SEP.match(y, n):
            return x
    cut = [m.start() for m in _LOT_SEP.finditer(a[:n])]
    stem = a[:cut[-1]].rstrip(" ,;:-–—/|(") if cut else ""
    return stem if len(stem) >= 20 and len(stem.split()) >= 2 else ""


def lot_groups(tenders: list) -> list:
    """Tenders in deadline order -> [(project name, [tenders])]: the lots one authority
    published under one project name, due the same day, become one line ('… · 6 Lose')
    instead of six identical ones (owner, 28.09.2026)."""
    groups: list = []
    for t in tenders:
        title = _ws(de(t, "title"))
        key = (norm_buyer(t.get("buyerName") or ""), (t.get("offerDeadline") or "")[:10])
        for g in groups:
            if g[0] == key and (st := _stem(g[1], title)):
                g[1] = st
                g[2].append(t)
                break
        else:
            groups.append([key, title, [t]])
    return [(stem, lst) for _k, stem, lst in groups]


def pick_unique(cands: dict) -> dict:
    """key -> the first of its candidate titles that no other page shares: pages in a
    collision move to their next candidate, round by round, until none collides or the
    candidates run out."""
    pick = {k: 0 for k in cands}
    for _round in range(max((len(v) for v in cands.values()), default=0)):
        n = collections.Counter(cands[k][pick[k]] for k in cands)
        moved = False
        for k in cands:
            if n[cands[k][pick[k]]] > 1 and pick[k] < len(cands[k]) - 1:
                pick[k] += 1
                moved = True
        if not moved:
            break
    out = {k: cands[k][pick[k]] for k in cands}
    # the pages still sharing a title take any candidate of theirs nobody else holds
    n = collections.Counter(out.values())
    for k in cands:
        if n[out[k]] > 1:
            free = next((c for c in cands[k] if not n[c]), None)
            if free:
                n[out[k]] -= 1
                out[k] = free
                n[free] += 1
    return out


def twin_rows(keys: list) -> set[int]:
    """Positions whose visible text repeats in the same list."""
    n = collections.Counter(keys)
    return {i for i, k in enumerate(keys) if n[k] > 1}


def project_no(row: dict) -> str:
    """' · Projekt 42676': what still tells apart lots published under one identical title
    (3× 'SGS Erweiterung Schulanlage Gutenbrunnen Schübelbach', same code, same deadline)."""
    n = row.get("projectNumber") or row.get("publicationNumber") or ""
    return f" · {_if('project_no', n=n)}".replace(f" {n}", f"\u00a0{n}") if n else ""


def distinct_titles(texts: list[str], limit: int) -> list[str]:
    """Titles for one list, each cut to `limit` and told apart from its neighbours.

    A plain end cut printed six identical lines on every home page ('Modernisierung
    "Kirchzelg", St. Bernhardstrasse 38, 5430…': the lots differ only after the cut) and 14
    on one buyer page (owner and verifier, 28.09.2026). Every line is cut at its end, the way
    a reader expects; only the lines that then read the same as another line get a middle
    cut that keeps their own tail, with more room for the tail if they still clash, and as a
    last resort the whole title."""
    out = [fit_title(t, "", limit, 0) for t in texts]
    for share in (0.4, 0.55, 0.7, None):
        seen = collections.defaultdict(set)
        for t, o in zip(texts, out):
            seen[o].add(_ws(t))
        clash = {o for o, full in seen.items() if len(full) > 1}
        if not clash:
            break
        # the difference sits in the middle (two refuse lorries that differ only in their
        # width): those lines are printed whole
        out = [(_ws(t) if share is None else fit_title(t, "", limit, share)) if o in clash else o
               for t, o in zip(texts, out)]
    return out


def zuschlag(n: int) -> str:
    one, many = lingue.PLURALS[LANG]
    return plural(n, one, many)


def spelled(n: int, cap: bool = False) -> str:
    """A small number in words, in prose (fix round 2): a count that opens a sentence ('Zwei Zuschläge nennen …'),
    the Über page's thresholds ('ab zwei Zuschlägen'; British style spells out numbers under ten)."""
    w = lingue.NUM_WORDS[LANG]
    if not 0 <= n < len(w):
        return formato.count(n)
    return w[n][:1].upper() + w[n][1:] if cap else w[n]


def awards_start(n: int) -> str:
    """'Zwei Zuschläge' / 'Deux adjudications' at the start of a sentence; a large count stays in figures."""
    one, many = lingue.PLURALS[LANG]
    return f"{spelled(n, cap=True)} {one if n == 1 else many}" if n <= 12 else zuschlag(n)


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
    return de_lang(row, field)[0]


def text_la(text: str) -> str:
    """' lang="fr"' for a publication text without a language of its own (a justification, a firm's note, a lot's
    name) when its words say it is not the page's language (fix round 1)."""
    lang = detect_lang(_ws(text or ""))
    return f' lang="{lang}"' if lang and lang != LANG else ""


def la(row: dict, field: str = "title") -> str:
    """' lang="fr"' for a publication text de() takes from another language than the page's, so a
    screen reader switches voice ('' when it is the page's language or not known; audit 13.10.2026)."""
    lang = de_lang(row, field)[1]
    return f' lang="{lang}"' if lang and lang != LANG else ""


_NULLS = ("null", "none", "undefined")


def de_lang(row: dict, field: str) -> tuple[str, str]:
    """(text de() shows, its language): the translation it took, or for the publication's own text
    the translation that carries the same words ('' when none or several languages do)."""
    t = ((row.get("translations") or {}).get(field) or {})
    orig = (row.get(field) or "").strip()
    # a text that is a literal 'null' is no text (fix round 2: 9 descriptions, /en/auftrag/296c9108…/)
    if orig.lower() in _NULLS:
        orig = ""
    order = (LANG, "de", "fr", "it")
    for lang in order:
        v = (t.get(lang) or "").strip()
        if not v or v.lower() in _NULLS:
            continue
        # simap's own translation is sometimes one text pasted onto several lots ('Extension
        # de l'École de la Champagne - CFC' for 18 different lots; the ventilation lot of
        # Kalktarren reads 'maçonnerie' in French) or cut at 100 characters ('…Heizungs- und
        # Kühlwasse'): then the publication's own title is the true one
        if (field, lang, _ws(v)) in _SHARED or (orig and len(v) < len(orig) and orig.startswith(v)):
            continue
        # a template simap never filled in: 'Erneuerung der amtlichen Vermessung, Nom
        # entreprise, los x' for the Tafers lot whose French title names 'Rue, lot 4'
        if _PLACEHOLDER.search(v):
            continue
        # a translation left over from the publication it was copied from ('Copie de …',
        # 'Kopie von …'): several name another lot or project than the award (verifier,
        # 29.09.2026), so the publication's own text is the true one
        if _COPY.match(v) and not _COPY.match(orig):
            continue
        v = _INVISIBLE.sub("", v)
        # one text filed under several languages ('Software Development Services …' as both 'de' and 'en') says
        # nothing about its language: then only its own words do (fix round 1)
        dup = sum(1 for x in t.values() if x and _ws(x) == _ws(v)) > 1
        return v, detect_lang(v) or ("" if dup else lang)
    o = _ws(orig)
    same = [k for k, v in t.items() if v and _ws(v) == o and o]
    lang = LANG if LANG in same else (same[0] if len(same) == 1 else "")
    orig = _INVISIBLE.sub("", orig)
    return orig, detect_lang(orig) or lang


# The language of a title or a description, read from its own words (step 3a, 14.10.2026): simap's
# declared language was wrong or missing on about 175 records (an Italian title under 'fr', a French
# one under none), and the pages gave screen readers the wrong voice. Only words that belong to one
# of the four languages count; a language is taken when it has at least two of them and twice as many
# as any other, else the declared language stands.
_LANG_WORDS = {
    "de": frozenset("und der die das dem den für von vom im mit zur zum auf bei nach aus über sowie ein eine einer "
                    "eines einem neubau sanierung erneuerung umbau ersatz lieferung beschaffung arbeiten "
                    "unterhalt dienstleistungen gemeinde stadt kanton schulhaus strasse planung ausführung "
                    "bauarbeiten baumeisterarbeiten instandsetzung erweiterung leistungen".split()),
    "fr": frozenset("et du les pour au aux sur une dans avec par de travaux fourniture rénovation réfection "
                    "entretien assainissement prestations nouvelle nouveau commune ville remplacement "
                    "réaménagement aménagement bâtiment école rue chemin lieu marché d’ d' "
                    "ouvrages équipements à en collège mise conformité".split()),
    "it": frozenset("e di del della delle dei degli dello per il con nel nella nei nelle sul sulla dal dalla ed "
                    "lavori fornitura servizi manutenzione risanamento nuovo nuova sostituzione progettazione "
                    "rifacimento comune città scuola strada dell’ dell' nell’ nell' all’ all' sull’ sull' "
                    "edificio opere impianti".split()),
    # English by its function words only: 'Maintenance licences', 'SAP Support', 'Software' and
    # 'Management' are French or German titles too
    # (fix round 1: 'development', 'planning', 'outage', 'platform' for 'Software Development Services for Outage
    # Planning Platform', filed by simap as German)
    "en": frozenset("and the of for with from to supply framework agreement development planning "
                    "outage platform".split()),
}
# a hyphenated compound is one word ('state-of-the-art' is not three English ones in a German title)
_LANG_TOK = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*(?:['’][^\W\d_]+)?", re.UNICODE)
_LANG_CACHE: dict = {}


def detect_lang(text: str) -> str:
    """'de', 'fr', 'it', 'en' when the text's own words say so clearly, else ''."""
    if not text:
        return ""
    hit = _LANG_CACHE.get(text)
    if hit is not None:
        return hit
    score = collections.Counter()
    for m in _LANG_TOK.finditer(text.casefold()):
        w = m.group(0)
        # an elided article counts by its own form: 'dell’' Italian, 'd’' French
        if "'" in w or "’" in w:
            w = re.split(r"['’]", w)[0] + "’"
        for lang, words in _LANG_WORDS.items():
            if w in words or w.replace("’", "'") in words:
                score[lang] += 1
    top = score.most_common(2)
    out = ""
    if top and top[0][1] >= 2 and (len(top) == 1 or top[0][1] >= 2 * top[1][1]):
        out = top[0][0]
    _LANG_CACHE[text] = out
    return out


_COPY = re.compile(r"\s*(?:copie|copy|kopie|copia)\b", re.I)
_PLACEHOLDER = re.compile(r"\bnom (?:de l['’])?entreprise\b|\bfirmenname\b|\b(?:los|lot|lotto) x\b"
                          r"|\bx{3,}\b", re.I)


# (field, language, text) of translations that simap attached to publications whose own
# texts differ: filled once by main(), before any page is written
_SHARED: set = set()


def find_shared(rows: list) -> set:
    seen = collections.defaultdict(set)
    for r in rows:
        for field in ("title",):
            tr = ((r.get("translations") or {}).get(field) or {})
            o = _ws(r.get(field) or "").casefold()
            for lang, v in tr.items():
                if v and o:
                    seen[(field, lang, _ws(v))].add(o)
    return {k for k, v in seen.items() if len(v) > 1}


def chf_amount(row: dict) -> float | None:
    """The awarded amount, but only when the register published it IN FRANCS.

    98 awards are published in euros and 11 in dollars. Adding them to a CHF total
    silently overstated it by roughly half a billion, and each page printed a foreign
    figure under a "CHF" label — a converted or mislabelled amount is a number the
    source never published, and this is a register. Foreign amounts are shown on their
    own page with their own currency and left out of every total.
    """
    p = row.get("winnerPrice")
    if not isinstance(p, (int, float)) or not p or row.get("_price_repeat"):
        return None
    cur = (row.get("winnerCurrency") or "CHF").strip().upper()
    if cur != "CHF" or rate_price(p, cur, row):
        # under CHF 1'000 an award states a unit rate, not a contract value (rate_price): it is shown,
        # flagged, and never enters a sum or a median (step 3a, 14.10.2026); up to CHF 5'000 when its text
        # speaks of a day or hour rate (fix round 1)
        return None
    return float(p)


# An award of less than CHF 1'000 is a unit rate (per hour, item or kilometre), not the value of a
# contract: 168 awards to one firm on 14.10.2026, Antaès' twelve summed to 'CHF 1'250'. Flagged on rows
# and pages ('vermutlich Einheitspreis'), left out of every sum and median, with a note where they are.
# Fix round 1 (20.10.2026): so is an amount of CHF 1'000 to 5'000 whose publication speaks of staff leasing or
# a day or hour rate (LSE, Personalverleih, postes externes, Tagessatz, Regie …): such awards, Antaès' 1'250 and 1'000 and
# Sword Services' 1'054, 1'090, 1'368 among them, were still summed and listed among the 'largest'.
RATE_MAX = 1000.0
RATE_CUE_MAX = 5000.0
_RATE_CUE = re.compile(
    r"(?<![\w-])(?:(?-i:LSE)|location\s+de\s+(?:services|personnel)|Personal(?:verleih|ausleihe)\w*|Temporärpersonal"
    r"|Tagess[aä]tz\w*|Stundens[aä]tz\w*|Tagespauschal\w*|Regie(?!rung)\w*|pro\s+(?:Tag|Stunde|Arbeitstag)|Ans[aä]tz\w*"
    r"|tarifs?\s+(?:journalier|horaire)s?|taux\s+(?:journalier|horaire)s?|prix\s+(?:journalier|horaire)s?"
    r"|tariff[ae]\s+(?:giornalier|orari)[ae]|prestito\s+di\s+personale|(?:day|daily|hourly)\s+rates?"
    r"|postes?\s+externes?)(?![\w-])|délégation\s+d['’]activités(?![\w-])", re.I)


def rate_cue(row: dict) -> bool:
    """The publication speaks of staff leasing or of a day or hour rate (its titles, descriptions, the
    justification, the firms' notes)."""
    hit = row.get("_rcue")
    if hit is None:
        aw = row.get("award") or {}
        parts = [row.get("title"), row.get("description"), aw.get("justification")]
        for f in ("title", "description"):
            parts += list(((row.get("translations") or {}).get(f) or {}).values())
        parts += [v.get("note") for v in (aw.get("vendors") or []) if isinstance(v, dict)]
        hit = row["_rcue"] = bool(_RATE_CUE.search(" ".join(str(x) for x in parts if x)))
    return hit


def rate_price(p, cur: str, row: dict | None = None) -> bool:
    """A CHF amount that is a unit rate: under 1'000, or up to 5'000 with a rate cue in its publication."""
    if p is None or cur != "CHF" or not 0 < p:
        return False
    return p < RATE_MAX or (p <= RATE_CUE_MAX and row is not None and rate_cue(row))


def is_rate(row: dict) -> bool:
    """An award to ONE firm whose CHF amount is a unit rate (rate_price)."""
    return len(winners(row)) == 1 and rate_price(price_of(row), cur_of(row), row)


def rate_sub(p, cur: str, row: dict | None = None) -> str:
    """The flag under a unit rate in a cell: a chip (.rt, fix round 2), the cell's figure muted by the CSS."""
    return f'<span class="sub sb2 rt">{e(_.rate_flag)}</span>' if rate_price(p, cur, row) else ""


def fx_sub(p, cur: str, exact: bool = False) -> str:
    """A foreign-currency amount, outside every CHF column: the sub-line of the row's title (or firm)
    cell says it with its currency, and the CHF column shows a dash (step 3a: 1'436 EUR cells stood
    under 'Betrag (Tsd. CHF)')."""
    if not p or cur == "CHF":
        return ""
    a = formato.exact(p, cur) if exact else formato.money(p, cur)
    return f'<span class="sub sb2">{e(_if("fx_amount", a=a))}</span>'


def not_chf_cell() -> str:
    return f'–<span class="sr"> {e(_.not_chf)}</span>'


def price_of(row: dict) -> float | None:
    """The published amount in whatever currency it was published, or None."""
    p = row.get("winnerPrice")
    return float(p) if isinstance(p, (int, float)) and not isinstance(p, bool) and p else None


def _e(kind: str, value) -> str:
    return lingue.enum(kind, value, LANG)


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


def firm_prices(row: dict) -> list[tuple[str, float | None, str, str]]:
    """(name, price, currency, note) of every firm winners() names, in the same order.

    An award to several firms has no amount of its own. simap publishes a price beside each
    name — the price of that firm's offer — and winnerPrice is only the first of them: the page
    of 15349-02 printed 313’744.35, the first of five BKP packages worth 5.87 Mio. together, as
    the 'Zuschlagsbetrag' (owner, 08.10.2026). Each firm's price is shown beside its name and
    never summed: in a framework the same ceiling stands beside every name (winners())."""
    vend = [v for v in ((row.get("award") or {}).get("vendors") or []) if isinstance(v, dict)]
    out, seen = [], set()
    for v in vend:
        name = str(v.get("name") or "").strip()
        if len(name) <= 2 or name in seen:
            continue
        seen.add(name)
        p = v.get("price")
        p = float(p) if isinstance(p, (int, float)) and not isinstance(p, bool) and p else None
        cur = (v.get("currency") or row.get("winnerCurrency") or "CHF").strip().upper()
        out.append((name, p, cur, (v.get("note") or "").strip()))
    if out:
        return out
    ws = winners(row)
    return [(w, price_of(row) if len(ws) == 1 else None, cur_of(row), "") for w in ws]


def joint_priced(row: dict) -> bool:
    """An award to several firms with a price in francs: one a CHF total leaves out."""
    return len(winners(row)) > 1 and any(p and cur == "CHF" for _w, p, cur, _n in firm_prices(row))


def rounded(v) -> bool:
    """The figure formato.money() prints for v is rounded (it then reads 'rund 1,2 Mio. CHF')."""
    return bool(v) and abs(formato.shown(v) - float(v)) > 0.005


def chf_total(rows: list) -> float:
    """The CHF sum the home, a canton or a buyer states: awards to ONE firm only, the rule the
    company pages always followed. Adding winnerPrice of an award to several firms counted the
    first firm's offer as the award (5.1 Mrd. on the home; 08.10.2026)."""
    return sum(chf_amount(a) or 0 for a in rows if len(winners(a)) == 1)


def sum_tile(rows: list) -> str:
    """The 'Summe der publizierten Beträge' tile of the home, a canton or a buyer (chf_total), with a
    line under it naming the awards to several firms it leaves out."""
    total = chf_total(rows)
    if not total:
        return ""
    return (f'<div class="fig money"><b>{formato.tile(total)}</b><span>{_.sum_published}</span>'
            f'{sum_notes(rows)}</div>')


def sum_notes(rows: list) -> str:
    """The lines under a CHF total: the awards to several firms and the unit rates it leaves out. Every award to
    several firms counts, with a price per firm or none (fix round 1: the home said 966 where the total leaves
    out 1'140)."""
    k = sum(1 for a in rows if len(winners(a)) > 1)
    r = sum(1 for a in rows if is_rate(a))
    out = []
    if k:
        out.append(_if("sum_no_joint_one" if k == 1 else "sum_no_joint", k=formato.count(k)))
    if r:
        out.append(_if("sum_no_rates_one" if r == 1 else "sum_no_rates", k=formato.count(r)))
    return "".join(f'<em class="approx">{e(x)}</em>' for x in out)


def nosum_tile(rows: list) -> str:
    """The sum's tile of a company page whose awards give no CHF sum (fix round 2: Antaès showed no tile, and nothing
    said why): a dash, and the reasons counted ('Keine Summe in CHF: 12 vermutliche Einheitspreise und 4 Zuschläge an
    mehrere Unternehmen.'), by the rule of chf_total()."""
    rates = joint = fx = none = 0
    for a in rows:
        p, cur = price_of(a), cur_of(a)
        if len(winners(a)) > 1:
            joint += 1
        elif not p or a.get("_price_repeat"):
            none += 1
        elif cur != "CHF":
            fx += 1
        elif rate_price(p, cur, a):
            rates += 1
    why = [_if(k + "_one") if n == 1 else _if(k, k=formato.count(n))
           for n, k in ((rates, "nosum_rates"), (joint, "nosum_joint"), (fx, "nosum_fx"), (none, "nosum_none")) if n]
    if not why:
        return ""
    text = why[0] if len(why) == 1 else ", ".join(why[:-1]) + lingue.AND[LANG] + why[-1]
    return (f'<div class="fig off"><b>–</b><span>{_.sum_published}</span>'
            f'<em class="approx">{e(_if("nosum", why=text))}</em></div>')


def award_cell(a: dict, unit: str) -> str:
    """An award's amount in a list of awards, in the column's unit: its amount when it names one firm;
    for several firms no figure — each has its own price, on the award's page. A foreign currency
    is never in the CHF column (fx_sub in the title cell); a unit rate is flagged."""
    firms = firm_prices(a)
    if len(firms) > 1:
        if any(p for _w, p, _c, _n in firms):
            return f'–<span class="sub sb2">{e(_.per_firm)}</span>'
        return formato.cell(None, empty_sr=_.not_published)
    p, cur = price_of(a), cur_of(a)
    if p and cur != "CHF":
        return not_chf_cell()
    return formato.column_cell(p, unit, cur, empty_sr=_.not_published) + rate_sub(p, cur, a)


def award_fx(a: dict) -> str:
    """The foreign-currency amount of an award to one firm, for its row's title cell."""
    return fx_sub(price_of(a), cur_of(a)) if len(firm_prices(a)) <= 1 else ""


def award_unit(rows: list) -> str:
    """The unit of a column of award amounts (formato.unit_for), from the CHF figures it prints: the
    amounts of awards to one firm (14.10.2026)."""
    return formato.unit_for(price_of(a) for a in rows if len(firm_prices(a)) == 1 and cur_of(a) == "CHF")


def money_th(key: str, unit: str) -> str:
    """A money column's header: its name and, once, the unit of every figure under it ('Betrag
    (Tsd. CHF)', 'Summe (Mio. CHF)'); class amt marks the column for controlla.py (14.10.2026)."""
    return f'<th class="r amt">{e(lingue.t(key, LANG))} ({e(lingue.t("unit_" + unit, LANG))})</th>'


# a vendor's note shown beside its price when it is short ('1710 Pfählungen', '2. Rang', 'Hinweis:
# Die publizierte Summe versteht sich als Kostendach …'), never one carrying an address: some name
# a subcontractor's contact person with street and postcode
_NOTE_MAX = 120
_ADDRESS = re.compile(r"(?i:strasse|straße|str\.|gasse|weg|platz|allee|rain|halde|ring)\s*\d+[a-z]?\b"
                      r"|\b(?i:rue|ch\.|chemin|avenue|av\.|route|quai|boulevard|via|viale|piazza|corso)\b[^\n,]{0,40}?\d"
                      r"|\b(?:CH|D|F|I|A|FL)-\d{4,5}\b|\b(?i:postfach|case postale|casella postale)\b")


def short_note(note: str) -> str:
    note = _INVISIBLE.sub("", note or "").strip()
    if not note or len(note) > _NOTE_MAX or note.count("\n") > 2 or _ADDRESS.search(note):
        return ""
    return note


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
    if not row:
        # simap's own label, as sent; on /fr/ with the French narrow space before ':' and ';'
        # like every other label (it kept a plain one in the tender tables)
        return lingue._typo(_ws(fallback), "fr") if LANG == "fr" and fallback else fallback
    # the EU chrome only, never simap's own text: Swiss German writes ss, and the EU file
    # carries a few typos, French colons without their space and one Italian label left in
    # English (32400000 'Network')
    lab = _CPV_FIX.get((LANG, str(code).strip())) or row[_CPV_COL[LANG]]
    if LANG == "de":
        lab = (lab.replace("ß", "ss").replace("Veschiedene", "Verschiedene")
               .replace("Forstwirtschft", "Forstwirtschaft"))
    else:
        lab = lab.replace("'", "’")
    if LANG == "fr":
        lab = (re.sub(r"\s*([:;])\s*", " \\1 ", lab).strip().replace("theâtres", "théâtres")
               .replace("personnnels", "personnels"))
        lab = lingue._typo(lab, "fr")
    return lab


_CPV_FIX = {("it", "32400000"): "Reti"}


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


def name_cut(t: str, n: int) -> str:
    """A name cut for a pill or a line: on a word boundary, never after 'des', 'de la',
    'und' …, never inside '(…' ('Unité soumissions - Département de l'aménagement, des…',
    'Gemeinde Kölliken, Abteilung Hochbau (müller verdan…': 507 pills per language)."""
    t = _ws(t)
    if len(t) <= n:
        return t
    cut = t[:n + 1]
    cut = cut[:cut.rfind(" ")] if " " in cut else t[:n]
    if cut.count("(") > cut.count(")"):
        cut = cut[:cut.rfind("(")]
    words = cut.rstrip(" ,;:–—/|").split(" ")
    while len(words) > 1 and (words[-1].lower().strip(",;:") in _TAIL_STOP
                              or words[-1] in _SEPS):
        words.pop()
    sp = _susp(words[-1])
    # the first half of a suspended compound keeps its hyphen ('Bau- und Umwelt-…')
    s = " ".join(words[:-1] + [sp]) if sp else " ".join(words).rstrip(" ,;:–—-/|")
    return (s if len(s) >= min(20, n // 2) else cut_end(t, n)) + "…"


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


def load() -> tuple[list, list, list]:
    """Awards, open tenders, and the tenders whose deadline passed in the last EXPIRED_DAYS days.

    `abandonment` publications ride in the same feed: a procurement the authority
    called off. Presenting one as an award says a contract was granted that was not,
    so they are dropped here rather than counted.
    """
    awards, seen = [], set()
    INCOMPLETE.clear()
    for f in sorted(DATI.glob("aggiudicazioni_*.json")):
        for a in json.loads(f.read_text()):
            k = a.get("publicationId") or a.get("publicationNumber")
            if k and k in seen:
                continue
            seen.add(k)
            if a.get("pubType") == "abandonment":
                continue
            # A publication that arrived without a title in any language and without a winner cannot be
            # shown: no page, no row, no canton. 107 of July 2026 (dati/aggiudicazioni_2026-07.json, the
            # details without the search row) were counted in the national total and the monthly chart
            # all the same, so the cantons summed to 107 less than the home (step 3a, 14.10.2026). They
            # are left out of every figure, and the about page says how many.
            if not _titles_of(a) and not winners(a):
                INCOMPLETE.append(a)
                continue
            _clean_names(a)
            _one_lot_title(a)
            awards.append(a)
    # A corrected award is published again under the same project (38433-02, -03, -04: the
    # same winner, the same amount): each copy counted as an award of its own, so the line
    # repeated on the company and buyer pages and the sums counted it twice or three times
    # (verifier, 29.09.2026). A correction is the same LOT published again (08.10.2026: with
    # every lot in dati/, keying on the firms alone merged lots 1 and 2 of 28439, which name
    # the same three firms); an award whose lot is not known keeps the old rule, the same
    # project naming the same companies.
    _infer_lots(awards)
    newest_aw: dict = {}
    for a in awards:
        k = _award_key(a)
        if k and (k not in newest_aw or _aw_order(a) > _aw_order(newest_aw[k])):
            newest_aw[k] = a
    awards = [a for a in awards if not (k := _award_key(a)) or newest_aw[k] is a]
    # simap often repeats the project's price on every lot an award covers (38433: 607’881.60 on each
    # of lots 1-3, the same firm): with the lots kept apart the totals counted it once per lot. The
    # same firms at the identical price within one project count once; every lot still shows it.
    seen_price: set = set()
    for a in sorted(awards, key=lambda r: (str(r.get("projectId") or ""), _aw_order(r))):
        p, cur = price_of(a), cur_of(a)
        if not a.get("projectId") or p is None:
            continue
        k = (a["projectId"], frozenset(winners(a)), round(p, 2), cur)
        if k in seen_price:
            a["_price_repeat"] = True
        seen_price.add(k)
    # One canton per award, and where it comes from (kantone.py): the award of a lot keeps its lot's
    # canton, so a sum over the cantons counts every award once; '_ksrc' says whether it is the order
    # address's ('ort'), the lot's ('lose') or the buyer's seat ('auftraggeber', marked on the pages).
    for a in awards:
        a["_canton_raw"] = a.get("canton")
        a["canton"], a["_ksrc"] = kantone.award_canton(a, a.get("_lot"))
    # a project whose page lists several awards: each row that links there from a company or a
    # buyer page points at its own line (#lot-2)
    for rows in project_awards(awards).values():
        for a in rows:
            a["_anchor"] = "" if len(rows) == 1 else (
                f"lot-{a['_lot']}" if a.get("_lot") is not None
                else "pub-" + slug(str(a.get("publicationNumber") or a.get("publicationId") or "")))
    # gare_aperte.json is the nightly's merge of every tender pulled (it only grows); the copy the
    # alert sender reads, gare_pubblicate.json, is added for any publication the first lacks, so a
    # tender an e-mail linked to keeps its page whichever file is on disk
    rows, seen_t = [], set()
    for name in ("gare_aperte.json", "gare_pubblicate.json"):
        p = DATI / name
        for t in (json.loads(p.read_text()) if p.exists() else []):
            k = t.get("publicationId") or t.get("publicationNumber")
            if k and k in seen_t:
                continue
            seen_t.add(k)
            _clean_names(t)
            rows.append(t)
    # One row per project: simap republishes a tender for every correction (-02, -03 …),
    # and each copy used to be listed as a tender of its own — the same line two or three
    # times, the superseded deadline beside the current one, 1’458 "open tenders" that were
    # 1’394 projects (verifier, 28.09.2026). The newest publication is the one in force:
    # highest publication suffix, then the latest publication date.
    newest: dict = {}
    first: dict = {}
    LATEST_TENDER_DAY[0] = max((d for d in ((t.get("publicationDate") or "")[:10] for t in rows) if d <= TODAY),
                               default="")
    TENDERS_SINCE[0] = min((d for d in ((t.get("publicationDate") or "")[:10] for t in rows) if d), default=TODAY)
    for t in rows:
        k = t.get("projectId") or t.get("publicationId") or t.get("publicationNumber")
        if k not in newest or _pub_order(t) > _pub_order(newest[k]):
            newest[k] = t
        # the day the tender first appeared: its -01 publication (a correction is not new; the
        # home counts the tenders first published on the day of the build, 14.10.2026)
        num, day = str(t.get("publicationNumber") or ""), (t.get("publicationDate") or "")[:10]
        if day and (num.endswith("-01") or "-" not in num) and (k not in first or day < first[k]):
            first[k] = day
    FIRSTS.clear()
    for k, t in newest.items():
        t["_first"] = first.get(k, "")
        # every canton the tender is listed (and announced by e-mail) under: its order address's with its
        # lots', else the buyer's seat (kantone.cantons_of, shared with avvisi/invia_avvisi.py); 'canton'
        # becomes the first of them
        t["_canton_raw"] = t.get("canton")
        t["_cants"], t["_ksrc"] = kantone.cantons_of(t)
        t["canton"] = t["_cants"][0] if t["_cants"] else ""
        # every project's first publication, open or not by now: the alert form's 'new a week' (step 3b)
        if t["_first"]:
            FIRSTS.append((t["_first"], tuple(t["_cants"]), str(t.get("cpvCode") or "")[:2]))
    NO_DEADLINE[0] = 0
    # Open = the deadline is still ahead at the moment of the build, not merely on or after today's
    # date (08.10.2026). A tender past its deadline keeps its page for EXPIRED_DAYS, marked as such;
    # once the project has an award, the award's page holds that address instead.
    no_page = {a["projectId"] for a in awards if a.get("projectId")} | {None, ""}
    floor = (date.fromisoformat(TODAY) - timedelta(days=EXPIRED_DAYS)).isoformat()
    opens, expired = [], []
    for t in newest.values():
        dl = deadline_at(t)
        if dl is None:
            # not listed as open: the hub says how many (nodl_note)
            NO_DEADLINE[0] += 1
            continue
        if dl > NOW:
            opens.append(t)
        elif (t.get("offerDeadline") or "")[:10] >= floor and t.get("projectId") not in no_page:
            expired.append(t)
    return awards, opens, expired


# A name that is an e-mail address (fix round 1: 'valentin.berclaz@eraneos.com' as the contracting authority of
# 37165-02, on cablex-ag's page and in the search index): a data error, never an entity of the register
_EMAIL_NAME = re.compile(r"^\s*[\w.+-]+@[\w-]+(?:\.[\w-]+)+\s*$")


def email_name(s) -> bool:
    return bool(s) and bool(_EMAIL_NAME.match(str(s)))


def _clean_names(r: dict) -> None:
    """Zero-width characters out of the names ('\u200bGesundheitsnetz Küsnacht AG'): invisible,
    they changed nothing a reader sees but split sort order and counted in cut lengths.
    A name that is an e-mail address is blanked (fix round 1): the record keeps the fact in '_buyer_nn' /
    '_win_nn' — the publication's other name for the authority (the recipient of the offers) when it has one, else
    True — and the pages say 'Name nicht angegeben' (buyer_label); it is in no index, CSV, list or description."""
    for k in ("buyerName", "winnerName"):
        if isinstance(r.get(k), str):
            r[k] = _INVISIBLE.sub("", r[k])
    for v in ((r.get("award") or {}).get("vendors") or []):
        if isinstance(v, dict) and isinstance(v.get("name"), str):
            v["name"] = _INVISIBLE.sub("", v["name"])
            if email_name(v["name"]):
                v["name"] = ""
                r["_win_nn"] = True
    if email_name(r.get("winnerName")):
        r["winnerName"] = ""
        r["_win_nn"] = True
    if email_name(r.get("buyerName")):
        rec = r.get("recipient") if isinstance(r.get("recipient"), dict) else {}
        alt = _ws(str(rec.get("name") or ""))
        r["_buyer_nn"] = alt if alt and not email_name(alt) else True
        r["buyerName"] = ""


def buyer_label(r: dict) -> str:
    """The authority as a row shows it: its name, or 'Name nicht angegeben' for a name that was an e-mail address."""
    return _ws(r.get("buyerName") or "") or (_.noname if r.get("_buyer_nn") else "")


def _vendor_set(a: dict) -> tuple:
    names = [(v.get("name") or "").strip().casefold()
             for v in ((a.get("award") or {}).get("vendors") or []) if isinstance(v, dict)]
    if not any(names) and a.get("winnerName"):
        names = [a["winnerName"].strip().casefold()]
    return tuple(sorted(n for n in names if n))


def _aw_order(a: dict) -> tuple:
    """The correction in force is the one published last (34279-02 came a day after -04)."""
    return (a.get("publicationDate") or "", _pub_order(a)[0])


def _pub_order(t: dict) -> tuple:
    num = str(t.get("publicationNumber") or "")
    suf = num.rsplit("-", 1)[-1] if "-" in num else ""
    return (int(suf) if suf.isdigit() else -1, t.get("publicationDate") or "")


# ------------------------------------------------------------------- the lots
# simap publishes a project in lots with one award per lot (28439-02 for lot 1, -03 for lot 2),
# and no record says which lot it is. lotti.py writes the lot into the title of the awards it
# adds, after a no-break space and an en dash: '… – Los 2: Grossaufträge Baumeister'.
_LOT_MARK = re.compile(r"\u00a0– (?:Los|lot|lotto)\u00a0(\d+)(?=\u202f?:|$)")


def _lot_key(s) -> str:
    return " ".join(str(s or "").split()).casefold()


def _one_lot_title(a: dict) -> None:
    """A title lotti.py named two lots in keeps the last, the award's own: 7 lot awards of
    08.10.2026 took their project title from a lot award an earlier run had written, and a row
    of 13551-06 read '… – lot 4 : Périodiques BGE zone UE Nord – lot 5 : …' for lot 5. Only the
    part lotti.py added is touched, in memory; simap's own text stays as published."""
    def one(t):
        m = list(_LOT_MARK.finditer(t)) if isinstance(t, str) else []
        return t[:m[0].start()] + t[m[-1].start():] if len(m) > 1 else t
    if isinstance(a.get("title"), str):
        a["title"] = one(a["title"])
    tr = (a.get("translations") or {}).get("title")
    if isinstance(tr, dict):
        for k in list(tr):
            tr[k] = one(tr[k])


def _titles_of(a: dict) -> list[str]:
    return [t for t in [a.get("title"), *((a.get("translations") or {}).get("title") or {}).values()] if t]


def _named_lot(a: dict):
    """The lot lotti.py named in the title, or None; the last one named, as _one_lot_title keeps
    it. A lot whose own name says it ('… – Los 3 Zone C') is found by that name in the project's
    list of lots."""
    nums = set()
    for t in _titles_of(a):
        m = _LOT_MARK.findall(t)
        if m:
            nums.add(int(m[-1]))
    if nums:
        return nums.pop() if len(nums) == 1 else None
    tails = {_lot_key(t.rsplit("\u00a0– ", 1)[1]) for t in _titles_of(a) if "\u00a0– " in t}
    hit = {x.get("lotNumber") for x in a.get("lots") or []
           if isinstance(x.get("lotNumber"), int) and _lot_key(x.get("lotTitle")) in tails}
    return hit.pop() if len(hit) == 1 else None


def _infer_lots(awards: list) -> None:
    """a['_lot'] = the number of the lot an award belongs to, or None where nothing says it.

    The nightly pull brings in a project's newest publication with the project's list of lots,
    each dated by its own newest publication: the award is the lot dated to its publication day
    when that is one lot, or one once the lots the project's other awards hold are set aside
    (6965-02 is lot 1: lots 2-15 are -03 … -16, all of 24.09.2025). Read against simap's
    project-header of 11 projects (08.10.2026): 39 awards placed right, none wrong, one left
    unknown; on the whole archive one award (29436-03) stays without a lot."""
    by_p = collections.defaultdict(list)
    for a in awards:
        a["_lot"] = None
        if a.get("projectId") and a.get("lots"):
            by_p[a["projectId"]].append(a)
    for rows in by_p.values():
        for a in rows:
            a["_lot"] = _named_lot(a)
        todo = [a for a in rows if a["_lot"] is None]
        while todo:
            taken = {a["_lot"] for a in rows if a["_lot"] is not None}
            left = []
            for a in todo:
                day = (a.get("publicationDate") or "")[:10]
                lots = [x for x in a["lots"] if isinstance(x.get("lotNumber"), int)]
                same = {x["lotNumber"] for x in lots if (x.get("publicationDate") or "")[:10] == day
                        and x.get("pubType") == a.get("pubType")}
                free = same - taken
                # a title lotti.py could not mark: the lot's own name, which starts with the
                # project's ('Pose de compteurs SMART - secteur Nord')
                named = {x["lotNumber"] for x in lots
                         if _lot_key(x.get("lotTitle")) in {_lot_key(t) for t in _titles_of(a)}}
                for pick in (same, free, named & (free or same)):
                    if len(pick) == 1:
                        a["_lot"] = next(iter(pick))
                        taken.add(a["_lot"])
                        break
                else:
                    left.append(a)
            if len(left) == len(todo):
                break
            todo = left


def _award_key(a: dict):
    """What makes publications one award, of which the one published last is in force: the
    same lot of the same project, whatever firms it names (36719-05 corrects the nursery
    36719-02 had named for lot 2); without a lot, the same project naming the same firms."""
    pid = a.get("projectId")
    if not pid:
        return None
    if a.get("_lot") is not None:
        return (pid, "lot", a["_lot"])
    vs = _vendor_set(a)
    return (pid, "firms", vs) if vs else None


def _lot_order(a: dict) -> tuple:
    n = a.get("_lot")
    return (n is None, n if n is not None else 0, _pub_order(a))


def project_awards(awards: list) -> dict:
    """projectId -> its awards, lots in order: what the project's page lists."""
    out = collections.defaultdict(list)
    for a in awards:
        if a.get("projectId"):
            out[a["projectId"]].append(a)
    for rows in out.values():
        rows.sort(key=_lot_order)
    return out


def award_href(a: dict) -> str:
    """The award's page, at the award's own line when the page lists several (#lot-2)."""
    anchor = a.get("_anchor") or ""
    return f"{BASE}/{LANG}/auftrag/{e(a.get('projectId'))}/" + (f"#{e(anchor)}" if anchor else "")


def _lot_tail(a: dict, t: str):
    """(project part, lot part) of a title lotti.py wrote, else (t, None)."""
    m = list(_LOT_MARK.finditer(t))
    if m:
        return t[:m[0].start()].rstrip(), t[m[-1].end():].lstrip("\u202f:").strip()
    if "\u00a0– " in t:
        head, tail = t.rsplit("\u00a0– ", 1)
        if _lot_key(tail) in {_lot_key(x.get("lotTitle")) for x in a.get("lots") or []}:
            return head.rstrip(), tail.strip()
    return t, None


def lot_name(a: dict) -> str:
    """The lot's own name, in the page's language where the record has it: what follows 'Los 2:'
    in a title lotti.py wrote, else the name in the project's list of lots ('' for a lot named
    only by its number)."""
    _head, tail = _lot_tail(a, de(a, "title"))
    if tail is not None:
        return tail
    return next((_ws(x.get("lotTitle") or "") for x in a.get("lots") or []
                 if x.get("lotNumber") == a.get("_lot")), "")


def project_title(rows: list) -> str:
    """The title of a project whose page lists several awards: the publications' title without
    the lot lotti.py named after it — the one most of the others start with, else the name their
    titles share ('Consultants Informatiques - Référencement', where the page used to show '… –
    lot 15 : Expert sécurité de l’information', the last lot read)."""
    heads = [h for h in (_lot_tail(a, de(a, "title"))[0] for a in rows) if h]
    if not heads:
        return ""
    best = max(dict.fromkeys(heads), key=lambda t: sum(h.startswith(t) for h in heads))
    if sum(h.startswith(best) for h in heads) == 1 and len(heads) > 1:
        stem = heads[0]
        for h in heads[1:]:
            stem = _stem(stem, h) if stem else ""
        best = stem or best
    return best


# ------------------------------------------------------------------ the chrome

CSS = grafici.CSS + r"""
/* Step 4 (15.10.2026): design A2 "Brass" on every page, in the owner's chosen look: black, warm off-white
   and metallic brass; League Gothic (as "AR Gothic") for the site's and the sections' headings, set in
   capitals, and Instrument Sans for everything that is read, with tabular figures in every column of
   numbers. One dark theme for everyone (the owner's choice), a print sheet and a forced-colours mode. Every
   colour is a token defined once below, and controlla.py measures each pair in genera.CONTRAST against
   WCAG 2.2 AA. Font sizes in rem only, none under 0.8125 rem (13 px); body text 17 px, prose 18 px and
   never wider than about 70 characters; targets of at least 24 px; the brass focus ring on everything that
   takes focus. The official titles of tenders and awards, and the names of companies and authorities, stay
   in Instrument Sans as published (h1.rec): long official titles in condensed capitals would not read.
   The data pages are an instrument: subtle hover and focus transitions only. The home alone moves
   (js/home.js), and is complete and still without it. Hooks are the pages' existing classes, so the look
   costs no byte on the 92,000 pages: the header's search is `.masthead [role=search]`, the phone menu the
   header's <details>, the stacked tables' labels come from the table's class and the column's position,
   keyed by :lang() (generated in genera.css_labels). */
:root{
  --paper:#000;--band:#050403;--card:#0d0b08;--panel:#090806;--sticky:#000;--alert-bg:#15110a;
  --ink:#f4f1ea;--text:#e2ddd1;--muted:#a6a39b;
  --brass:#c9a24e;--brass-lo:#9c7633;--gold:#d8b66a;--gold-hi:#f3dc9a;--on-brass:#0b0905;
  --link:#f3dc9a;--link-hover:#fff6dc;--focus:#f3dc9a;
  --field:#8a6a2d;--line:#2f2c27;--line2:#565046;
  --warm:#ffc46b;--hot:#ff9a8a;--ok:#9fdcb7;--ok-bg:#0d1a12;--off-bg:#16140f;
  --hover:rgba(201,162,78,.08);--mark:#c9a24e;
  --grad:linear-gradient(100deg,#9c7633 0%,#c9a24e 20%,#f2d892 44%,#d4ae5c 62%,#a17a35 100%);
  --grad-v:linear-gradient(180deg,#f6e2a6 0%,#d7b263 32%,#a8803a 100%);
  --bar:linear-gradient(180deg,#f2d892,#c9a24e 34%,#8f6c2c);
  --display:"AR Gothic","AR Gothic fb","AR Gothic fb2","AR Gothic fr","Arial Narrow",sans-serif;
  --sans:"Instrument Sans","IS fb","IS fr",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --max:77.5rem;--gut:2rem;
  --cut:polygon(0 0,100% 0,100% calc(100% - .625rem),calc(100% - .625rem) 100%,0 100%);
  --cut0:polygon(100% 0,100% 0,100% calc(100% - .625rem),100% 100%,100% 100%);
  --mk:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cpath fill='%23f4f1ea' fill-rule='evenodd' d='M12 54 27 10h10l15 44h-9.5l-3.1-9H24.6l-3.1 9zM32 23.2 36.7 37h-9.4z'/%3E%3Cpath fill='%23c9a24e' d='M27.3 37h9.4l2.7 8H24.6z'/%3E%3C/svg%3E");
  color-scheme:dark}
@media(max-width:40rem){:root{--gut:1rem}}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%;background:var(--paper)}
body{margin:0;background:var(--paper);color:var(--text);font:400 1.0625rem/1.6 var(--sans);
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;font-synthesis-weight:none;overflow-wrap:break-word}
::selection{background:var(--brass);color:#000}
img,svg,canvas{max-width:100%}
/* one link style: brass-underlined, thicker on hover; chips, menu items and buttons carry their own frame */
a{color:var(--link);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.22em;
  text-decoration-color:rgba(201,162,78,.65)}
a:hover{color:var(--link-hover);text-decoration-thickness:2px;text-decoration-color:currentColor}
:focus-visible{outline:3px solid var(--focus);outline-offset:3px}
.sr{position:absolute!important;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden;
  clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
/* fix round 1 (20.10.2026): an element the scripts hide stays hidden whatever display a component gives it
   (.tl li, the stacked rows and the chips set one; expired rows and the calendar link stayed visible) */
[hidden]{display:none!important}
.skip{position:absolute;left:1rem;top:-6rem;z-index:100;padding:.625rem 1rem;background:var(--ink);
  color:var(--paper);font-weight:700;text-decoration:none}
.skip:focus{top:.75rem;color:var(--paper)}
/* ── type ───────────────────────────────────────────────────────────────── */
h1,h2,h3,.disp{font-family:var(--display);font-weight:400;text-transform:uppercase;letter-spacing:.015em;
  color:var(--ink);text-wrap:balance}
h1{margin:.875rem 0 0;font-size:clamp(2.5rem,1.5rem + 3.6vw,4.5rem);line-height:.94}
h2{margin:0 0 .25rem;font-size:clamp(1.75rem,1.4rem + 1.2vw,2.375rem);line-height:1}
h3{margin:0;font-size:1.375rem;line-height:1.1;letter-spacing:.03em}
/* the official title of a tender or an award, the name of a company or an authority: as published. Its measure in em,
   not ch (fix round 4): a ch is the width of the font's '0', 0.68 em in Instrument Sans bold and 0.56 em in its fallback,
   so until the bold face arrived the title was 158 px narrower, took a line more and the page moved by up to 0.48 on a
   slow first visit; 25.9 em and 32.7 em are the 38 ch and 48 ch of Instrument Sans bold */
h1.rec{margin:.875rem 0 0;font:700 clamp(1.5rem,1.15rem + 1.4vw,2.25rem)/1.18 var(--sans);letter-spacing:-.01em;
  text-transform:none;max-width:25.9em;text-wrap:pretty;overflow-wrap:break-word;hyphens:auto;-webkit-hyphens:auto;
  hyphenate-limit-chars:6 3 3}
/* fix round 2: an official title over 110 characters a size smaller (it ran 6 lines at 1280 and 10 at 390), broken
   at a hyphen or after a slash or an ampersand (genera puts a <wbr> there), never in the middle of a word */
h1.rec.lt{font-size:clamp(1.25rem,1rem + 1vw,1.75rem);line-height:1.25;max-width:32.7em}
.eyebrow{display:flex;align-items:center;gap:.875rem;margin:0;max-width:none;font:700 .8125rem/1.35 var(--sans);
  letter-spacing:.2em;text-transform:uppercase;color:var(--gold);overflow-wrap:anywhere}
.eyebrow::before{content:"";flex:none;width:2.75rem;height:1px;background:linear-gradient(90deg,transparent,var(--brass))}
.dot{color:var(--brass)}
.num,.mono,.when,.amount,td.r{font-variant-numeric:tabular-nums}
.mono{letter-spacing:.02em}
.sub{color:var(--muted);font-size:.875rem;line-height:1.45}
abbr[title]{text-decoration:none;cursor:help}
/* fix round 2: the measure in em, about 70 characters a line (70ch of Instrument Sans, whose zero is wide, gave
   96 to 104) */
p{max-width:33em}
/* ── header: the A, the name and the search on the first row; the menu, the alert and the languages on the
   second; on a phone the search under the name, the rest behind "Menü" (a <details>: no script) ───── */
.masthead{position:relative;z-index:30;display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;column-gap:1.5rem;
  padding:0 max(var(--gut),(100% - var(--max))/2);background:#000;border-bottom:1px solid rgba(201,162,78,.34)}
.masthead a.name{grid-row:1;grid-column:1;display:flex;align-items:center;gap:.75rem;min-height:4.25rem;
  font:400 1.375rem/1 var(--display);letter-spacing:.05em;text-transform:uppercase;color:var(--ink);text-decoration:none}
.masthead a.name::before{content:"";flex:none;width:1.875rem;height:1.875rem;background:var(--mk) center/contain no-repeat}
.masthead a.name:hover{color:var(--gold-hi)}
/* 'unabhängig · nicht amtlich' under the name, from the stylesheet (css_labels, by :lang): no byte on the pages */
.masthead a.name{flex-wrap:wrap;align-content:center;row-gap:.25rem}
.masthead a.name::after{flex-basis:100%;padding-left:2.625rem;font:600 .8125rem/1.2 var(--sans);
  letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.masthead details{grid-row:1;grid-column:2;justify-self:end;display:none}
.masthead summary{display:flex;align-items:center;gap:.625rem;min-height:2.75rem;padding:0 .875rem;
  border:1px solid var(--line2);cursor:pointer;list-style:none;font:700 .8125rem/1 var(--sans);
  letter-spacing:.16em;text-transform:uppercase;color:var(--ink)}
.masthead summary::-webkit-details-marker{display:none}
.masthead summary::before{content:"";width:1.125rem;height:.75rem;
  background:linear-gradient(currentColor,currentColor) 0 0/100% 2px no-repeat,
    linear-gradient(currentColor,currentColor) 0 50%/100% 2px no-repeat,
    linear-gradient(currentColor,currentColor) 0 100%/100% 2px no-repeat}
.masthead details[open] summary{border-color:var(--brass);color:var(--gold-hi)}
.masthead summary:hover{border-color:var(--brass)}
.masthead [role=search]{grid-row:1;grid-column:2/4;justify-self:end;display:flex;position:relative;width:min(100%,28rem);margin:0}
[role=search] input{flex:1 1 auto;min-width:0;min-height:2.75rem;margin:0;font:inherit;font-size:1rem;line-height:1.3;
  padding:.5rem .75rem .5rem 2.375rem;border:1px solid var(--field);border-right:0;border-radius:0;color:var(--ink);
  background:#0b0a08 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='6.5' cy='6.5' r='4.75' fill='none' stroke='%23c9a24e' stroke-width='1.6'/%3E%3Cpath d='M10 10l4.25 4.25' stroke='%23c9a24e' stroke-width='1.8' stroke-linecap='round'/%3E%3C/svg%3E") no-repeat .75rem 50%/1rem 1rem}
[role=search] input::placeholder{color:var(--muted);opacity:1}
[role=search] input::-webkit-search-decoration{-webkit-appearance:none}
/* the clear button in brass, and none while the placeholder shows (fix round 2: the native grey one was off the
   palette, and the room it kept even when hidden cut the placeholder) */
input[type=search]::-webkit-search-cancel-button{-webkit-appearance:none;appearance:none;flex:none;width:1rem;height:1rem;
  margin-left:.375rem;cursor:pointer;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3.5 3.5l9 9M12.5 3.5l-9 9' stroke='%23c9a24e' stroke-width='1.8' stroke-linecap='round'/%3E%3C/svg%3E") 50%/.875rem no-repeat}
input[type=search]:placeholder-shown::-webkit-search-cancel-button{display:none}
[role=search] input:focus{outline:3px solid var(--focus);outline-offset:1px;border-color:var(--brass)}
[role=search] button{flex:none;min-height:2.75rem;margin:0;padding:0 1rem;border:1px solid var(--field);border-radius:0;
  background:#0b0a08;color:var(--gold-hi);font:700 .8125rem/1 var(--sans);letter-spacing:.12em;text-transform:uppercase;
  cursor:pointer;transition:background-color .2s,color .2s}
[role=search] button:hover{background:var(--brass);border-color:var(--brass);color:var(--on-brass)}
.sitenav{grid-column:1/3;min-width:0}
.sitenav ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;align-items:center;column-gap:1.375rem}
.sitenav a{position:relative;display:block;padding:.6875rem 0 .8125rem;font-size:.9375rem;line-height:1.4;
  color:var(--text);text-decoration:none}
.sitenav li:not(:last-child) a::after{content:"";position:absolute;left:0;right:0;bottom:.375rem;height:2px;background:var(--brass);
  transform:scaleX(0);transform-origin:left;transition:transform .3s cubic-bezier(.33,0,0,1)}
.sitenav a:hover,.sitenav a[aria-current]{color:var(--ink)}
.sitenav li:not(:last-child) a:hover::after,.sitenav li:not(:last-child) a[aria-current]::after{transform:scaleX(1)}
/* the alert, last in the menu: a brass, chamfered button that floods on hover */
.sitenav li:last-child{margin-left:auto}
.sitenav li:last-child a,a.btn,.form button{position:relative;isolation:isolate;display:inline-flex;
  align-items:center;justify-content:center;gap:.75rem;min-height:2.75rem;padding:.625rem 1.375rem .625rem 1.25rem;
  border:0;background:none;font:700 .8125rem/1.25 var(--sans);letter-spacing:.12em;text-transform:uppercase;
  text-decoration:none;color:var(--on-brass);cursor:pointer;transition:color .25s}
.sitenav li:last-child a::before,a.btn::before,.form button::before{content:"";position:absolute;inset:0;z-index:-2;
  background:linear-gradient(100deg,#fff6dc,#f6e2a6 60%,#e6c77e);clip-path:var(--cut)}
.sitenav li:last-child a::after,a.btn::after,.form button::after{content:"";position:absolute;inset:0;z-index:-1;
  background:var(--grad);clip-path:var(--cut);transition:clip-path .3s cubic-bezier(.33,0,0,1)}
.sitenav li:last-child a:hover::after,a.btn:hover::after,.form button:hover::after,
a.btn:focus-visible::after{clip-path:var(--cut0)}
a.btn:hover,.form button:hover{color:var(--on-brass)}
/* the ghost variant in the header: a 1-px brass edge, the brass floods in on hover */
.sitenav li:last-child a{color:var(--gold-hi);padding-block:.5rem;min-height:2.5rem}
.sitenav li:last-child a::before{background:var(--grad)}
.sitenav li:last-child a::after{inset:1px;background:#0b0a08;clip-path:polygon(0 0,100% 0,100% calc(100% - .5625rem),calc(100% - .5625rem) 100%,0 100%)}
.sitenav li:last-child a:hover::after,.sitenav li:last-child a[aria-current]::after{clip-path:polygon(100% 0,100% 0,100% calc(100% - .5625rem),100% 100%,100% 100%)}
.sitenav li:last-child a:hover,.sitenav li:last-child a[aria-current]{color:var(--on-brass)}
.sitenav li:last-child a[aria-current]{box-shadow:0 2px 0 var(--brass)}
/* the languages: chips with the code (from the lang attribute) and the language's name for screen readers */
.langs{grid-row:2;grid-column:3;display:flex;gap:.25rem;margin-left:1rem}
.langs a,.langs .on{position:relative;display:block;width:2.375rem;height:1.875rem;overflow:hidden;white-space:nowrap;
  text-indent:4rem;border:1px solid var(--line2);color:var(--muted);text-decoration:none;transition:border-color .2s,color .2s}
.langs a::before,.langs .on::before{content:attr(lang);content:attr(lang)/"";position:absolute;inset:0;display:grid;
  place-items:center;text-indent:0;font:700 .8125rem/1 var(--sans);letter-spacing:.12em;text-transform:uppercase}
.langs a:hover{border-color:var(--brass);color:var(--ink)}
.langs .on{background:var(--grad);border-color:transparent;color:var(--on-brass)}
@media(max-width:72rem){
  .masthead{grid-template-columns:minmax(0,1fr) auto;padding-bottom:.875rem}
  .masthead a.name{min-height:4rem}
  .masthead details{display:block}
  .masthead [role=search]{grid-row:2;grid-column:1/-1;justify-self:stretch;width:100%}
  .masthead>details:not([open])~nav.sitenav,.masthead>details:not([open])~nav.langs{display:none}
  .sitenav{grid-column:1/-1;margin-top:.5rem}
  .sitenav ul{flex-direction:column;align-items:stretch}
  .sitenav li{border-bottom:1px solid var(--line)}
  .sitenav a{padding:.8125rem 0;font-size:1.0625rem}
  .sitenav li:not(:last-child) a::after{bottom:.5rem;right:auto;width:2.5rem}
  .sitenav li:last-child{margin:1.125rem 0 .25rem;border:0}
  .sitenav li:last-child a{display:flex;width:100%;min-height:3rem}
  .langs{grid-row:auto;grid-column:1/-1;margin:.75rem 0 0}
  .langs a,.langs .on{width:3rem;height:2.5rem}
}
@media(max-width:26.25rem){.masthead a.name{font-size:1.1875rem;letter-spacing:.04em;column-gap:.625rem}
  .masthead a.name::before{width:1.625rem;height:1.625rem}
  .masthead a.name::after{padding-left:2.25rem;letter-spacing:.02em;text-transform:none;font-weight:500}
  .masthead summary{padding:0 .625rem}}
/* ── the page: header and footer full width, the content centred ───────────────────────────── */
/* the content column: a grid, so no component's own margins can pull a block out of line */
main{display:grid;grid-template-columns:minmax(var(--gut),1fr) min(var(--max),100% - 2*var(--gut)) minmax(var(--gut),1fr)}
main>*{grid-column:2;min-width:0}
.crumbs{width:min(var(--max),100% - 2*var(--gut));margin-inline:auto}
.crumbs ol{list-style:none;margin:0;padding:1.25rem 0 0;display:flex;flex-wrap:wrap;font-size:.875rem;line-height:1.5rem;color:var(--muted)}
.crumbs li{min-width:0;overflow-wrap:anywhere}
.crumbs li:last-child{max-width:100%;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.crumbs li+li::before{content:"/";content:"/"/"";margin:0 .625rem;color:var(--brass)}
.crumbs a{color:var(--gold-hi);text-decoration-color:rgba(201,162,78,.45)}
.crumbs [aria-current]{color:var(--text)}
.title{display:grid;grid-template-columns:minmax(0,1fr) 17.5rem;gap:1.75rem 3.5rem;align-items:end;
  padding:2.75rem 0 2.25rem;border-bottom:1px solid rgba(201,162,78,.34)}
.title>div:only-child{grid-column:1/-1}
.title p.sum{margin:1.125rem 0 0;max-width:33em;font-size:1.125rem;line-height:1.6;color:var(--text)}
.title p.aud{margin:1rem 0 0;max-width:30em;font-size:1.1875rem;line-height:1.5;color:var(--ink)}
.title .m14{margin-top:1.25rem}
.rail{margin:0;padding:0 0 .25rem 1.5rem;border-left:1px solid rgba(201,162,78,.38);font-size:.9375rem;color:var(--text)}
.rail dt{margin:1rem 0 0;font:700 .8125rem/1.35 var(--sans);letter-spacing:.18em;text-transform:uppercase;color:var(--gold)}
.rail dt:first-child{margin-top:0}
.rail dd{margin:.25rem 0 0;color:var(--ink);overflow-wrap:break-word}
.state{display:inline-flex;align-items:center;gap:.5rem;padding:.3125rem .75rem;border:1px solid rgba(201,162,78,.55);
  font:700 .8125rem/1.3 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--gold-hi)}
.state i{width:.4375rem;height:.4375rem;background:currentColor;transform:rotate(45deg);display:block;flex:none}
.state.today{color:var(--hot);border-color:var(--hot)}
.state.off{color:var(--muted);border-color:var(--line2);background:var(--off-bg)}
/* fix round 3 (item 31): a tender page near its deadline (genera.XP_JS): the expired lead shown by html.xp before the first
   paint, the deadline muted and the calendar link gone with it; the line of 'noch 5 Tage' kept free (html.s7) */
html:not(.xp) .title p.xl{display:none}
.fig .rel:empty{display:none}
.s7 .fig.wide .rel:empty,.xp .fig.wide .rel:empty{display:block}
.fig.wide .rel:empty::before{content:"\a0"}
.xp .fig.wide[data-deadline] b{background:none;-webkit-text-fill-color:currentColor;color:var(--muted)}
.xp .fig.wide[data-deadline]::before{opacity:.45}
.xp .fig.wide[data-deadline] .rel{color:var(--muted)}
.xp .acts a[href$="frist.ics"]{display:none}
.xp .title .state{color:var(--muted);border-color:var(--line2);background:var(--off-bg)}
/* ── figures: big brass numbers, small capitals under them ────────────────────────────────── */
.figures{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,11.5rem),1fr));gap:1.5rem 0;padding:2rem 0 .5rem}
.fig{position:relative;display:block;padding:.25rem 1.5rem .25rem;border-left:1px solid var(--line);min-width:0}
.figures>.fig:first-child{border-left:0;padding-left:0}
.fig b{display:block;font:400 clamp(2.75rem,2rem + 2.4vw,4rem)/.92 var(--display);letter-spacing:.01em;color:var(--gold-hi);
  background:var(--grad-v);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;overflow-wrap:break-word}
.fig b .n{white-space:nowrap}
.fig b small{font-size:1.125rem;letter-spacing:.06em;margin-left:.15em;white-space:nowrap}
.fig>span{display:block;margin-top:.75rem;font:700 .8125rem/1.4 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.fig .approx{display:block;margin-top:.5rem;font-size:.875rem;font-style:normal;line-height:1.45;color:var(--muted)}
a.fig{color:var(--ink);text-decoration:none}
a.fig>span::after{content:"\00a0\2192";content:"\00a0\2192"/"";color:var(--brass)}
a.fig[href^="#"]>span::after{content:"\00a0\2193";content:"\00a0\2193"/""}
.jl{margin:1rem 0 0;font-size:.9375rem;color:var(--muted)}
.jl a{white-space:nowrap}
a.fig:hover b{filter:brightness(1.18)}
a.fig:hover>span{color:var(--ink)}
.fig.date b{font-size:clamp(2rem,1.6rem + 1.4vw,2.75rem);white-space:nowrap}
.fig.off b{background:none;-webkit-text-fill-color:currentColor;color:var(--muted)}
.fig .rel{display:block;margin-top:.5rem;font:700 .9375rem/1.35 var(--sans);font-style:normal;letter-spacing:.02em;color:var(--gold-hi)}
.fig.soon .rel{color:var(--warm)}
.fig.today b{background:none;-webkit-text-fill-color:currentColor;color:var(--hot)}
.fig.today .rel{color:var(--hot)}
/* a record's deadline (or amount): the tile in brass brackets */
.fig.wide{grid-column:span 2;max-width:42rem;padding:1.25rem 1.5rem 1.125rem;border:0;background:linear-gradient(180deg,rgba(201,162,78,.09),rgba(201,162,78,.02))}
.figures>.fig.wide:first-child{padding-left:1.5rem}
.fig.wide::before,.cols>.prose+div::before,.kb::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(var(--brass),var(--brass)) 0 0/.75rem 1px,linear-gradient(var(--brass),var(--brass)) 0 0/1px .75rem,
    linear-gradient(var(--brass),var(--brass)) 100% 0/.75rem 1px,linear-gradient(var(--brass),var(--brass)) 100% 0/1px .75rem,
    linear-gradient(var(--brass),var(--brass)) 0 100%/.75rem 1px,linear-gradient(var(--brass),var(--brass)) 0 100%/1px .75rem,
    linear-gradient(var(--brass),var(--brass)) 100% 100%/.75rem 1px,linear-gradient(var(--brass),var(--brass)) 100% 100%/1px .75rem;
  background-repeat:no-repeat}
.fig.wide b{font-size:clamp(2.25rem,1.7rem + 2vw,3.5rem)}
.fig.wide.off::before{opacity:.45}
/* a unit rate (fix round 2: a full-gold '130 CHF' over a 14 px footnote): the figure muted like a past deadline, beside
   it a chip that says what it probably is; in a list the cell's figure muted and its flag the same chip */
.fig.rate{display:flex;flex-wrap:wrap;align-items:center;column-gap:1.125rem}
.fig.rate b{background:none;-webkit-text-fill-color:currentColor;color:var(--muted)}
.fig.rate>span{order:2;flex-basis:100%}
.fig.rate .approx{order:1;display:inline-flex;margin:0;padding:.3125rem .75rem;border:1px solid rgba(255,196,107,.6);
  background:rgba(255,196,107,.07);font:700 .8125rem/1.3 var(--sans);letter-spacing:.06em;text-transform:uppercase;color:var(--ink)}
.sub.rt{display:table;margin:.25rem 0 0 auto;padding:.0625rem .4375rem;border:1px solid rgba(255,196,107,.55);font-size:.8125rem;
  line-height:1.45;color:var(--text)}
.fig.rate .approx::before,.sub.rt::before{content:"\2248\00a0";content:"\2248\00a0"/"";color:var(--warm)}
td:has(>.rt)>data{color:var(--muted)}
@media(max-width:37.5rem){.fig{padding:.25rem 0 .25rem 1rem}.figures>.fig:nth-child(odd):not(.wide){border-left:0;padding-left:0}
  .fig.wide{grid-column:1/-1}.figures{grid-template-columns:repeat(2,minmax(0,1fr))}
  .fig.wide+.fig{border-left:0;padding-left:0}}
@media(max-width:23.75rem){.figures{grid-template-columns:minmax(0,1fr);gap:1rem 0}
  .figures>.fig{border-left:0;padding:0}.figures>.fig+.fig{border-top:1px solid var(--line);padding-top:1rem}
  .figures>.fig.wide{padding:1.125rem 1.25rem 1rem;border:0}}
/* ── sections and running heads ───────────────────────────────────────────────────────────── */
.sec{margin-top:.75rem}
.sec>h2:first-child,.sec>h2.pr30:first-child{margin:3.25rem 0 .75rem}
.runhead{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:.25rem 1.5rem;
  margin-top:3.25rem;padding:0 0 .75rem;border-bottom:1px solid rgba(201,162,78,.42)}
.runhead h2{margin:0;font-size:clamp(1.5rem,1.25rem + .9vw,2rem)}
.runhead>span{font:700 .8125rem/1.4 var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.runhead.mt26{margin-top:1.75rem}
.lede,figure .lede{margin:.75rem 0 0;max-width:33em;color:var(--muted);font-size:1rem;line-height:1.6}
.prose p{margin:0 0 1rem;font-size:1.125rem;line-height:1.7;max-width:33em;color:var(--text)}
.prose ul{max-width:33em}
.prose p strong{color:var(--ink)}
.prose h2,h2.pr34,h2.pr30{margin:2.25rem 0 .75rem;font-size:1.625rem}
.prose>h2:first-child{margin-top:2.75rem}
.cols{display:grid;grid-template-columns:minmax(0,1fr) 25rem;gap:3.5rem;align-items:start;padding-top:.5rem}
.half{display:grid;grid-template-columns:1fr 1fr;gap:3.5rem;align-items:start;padding-top:.5rem}
.cols>*,.half>*{min-width:0}
/* a record's "Angaben": the details in a brass-bracketed panel */
.cols>.prose+div{position:relative;margin-top:2.75rem;padding:.25rem 1.5rem 1.5rem;background:var(--card)}
.cols>.prose+div .runhead{margin-top:1.25rem}
.cols>.prose+div .tags{margin-top:1.25rem}
/* ── tables ───────────────────────────────────────────────────────────────────────────────── */
table{width:100%;border-collapse:collapse}
th{text-align:left;font:700 .8125rem/1.35 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);
  padding:0 .875rem .75rem 0;border-bottom:1px solid var(--line2);vertical-align:bottom}
td{padding:.875rem .875rem .875rem 0;border-bottom:1px solid var(--line);vertical-align:top;font-size:1rem;line-height:1.5}
thead td{border-bottom:1px solid var(--line2);padding:0 .875rem .75rem 0}
td.r,th.r{text-align:right;padding-right:0;padding-left:1rem}
td.num{white-space:nowrap}
td.num .sub{white-space:normal;font-variant-numeric:normal}
td a,ul.plain a,.bl a,.ber a{color:var(--ink);text-decoration-color:rgba(201,162,78,.5)}
td a:hover,ul.plain a:hover,.bl a:hover,.ber a:hover{color:var(--gold-hi)}
td.d,td.when{white-space:nowrap}
td.sub,.sub{color:var(--muted)}
td .sub{display:block;margin-top:.25rem}
td.when{font-weight:700;color:var(--ink)}
th.w96{width:7.5rem}
th.w44{width:3.5rem}
th.w52{width:4rem}
tbody tr{position:relative;transition:background-color .2s}
tbody tr:hover{background:var(--hover)}
tbody tr:hover>:first-child{box-shadow:inset 2px 0 0 var(--brass)}
/* a row with one primary link is tappable as a whole: the first linked cell's link covers the row */
tbody td a::after{content:"";position:absolute;inset:0}
tbody td:has(a)~td a{position:relative;z-index:1}
tbody td:has(a)~td a::after,.kv a::after,.lots a::after,.cmp a::after,td .sub a::after,.kb a::after{content:none}
.kv a,.cmp a{position:static}
.kv tbody tr:hover,.cmp tbody tr:hover,.cc tbody tr:hover{background:none}
.kv tbody tr:hover>:first-child,.cmp tbody tr:hover>:first-child,.cc tbody tr:hover>:first-child{box-shadow:none}
.scroll{overflow-x:auto;max-width:100%;position:relative}
.scroll:has(>table td.num>.sr:only-child)::after{display:block;margin:.5rem 0 0;font-size:.875rem;line-height:1.45;color:var(--muted)}
/* the details of a record: label and value */
.kv{table-layout:fixed}
.kv th{width:max(33%,9.5em);padding:.75rem .875rem .75rem 0;font:400 1rem/1.45 var(--sans);letter-spacing:0;text-transform:none;
  color:var(--muted);border-bottom:1px solid var(--line);vertical-align:baseline;white-space:normal;overflow-wrap:normal;
  hyphens:auto;-webkit-hyphens:auto}
.kv td{padding:.75rem 0;vertical-align:baseline;color:var(--ink);overflow-wrap:break-word;hyphens:auto;-webkit-hyphens:auto;
  hyphenate-limit-chars:12 5 5}
.kv tr:last-child>*{border-bottom:0}
/* simap.ch and the register side by side (the hub) */
.cmp th{padding:.875rem 1rem;border-bottom:1px solid var(--line)}
.cmp thead td{padding:.875rem 1rem}
.cmp th.us{color:var(--gold-hi)}
.cmp tbody th{font:400 1rem/1.5 var(--sans);letter-spacing:0;text-transform:none;color:var(--text);white-space:normal;vertical-align:top}
.cmp td{padding:.875rem 1rem}
.cmp td.c{text-align:center;width:11rem;font-weight:700;color:var(--muted)}
.cmp td.c.y{color:var(--gold-hi)}
.top td.n0,.top .n0{width:3rem;font:400 1.625rem/1 var(--display);color:var(--gold);padding-top:1rem}
.top td.r.num{font-weight:700;color:var(--ink)}
.top td.r.num:last-child{font-weight:400;color:var(--text)}
@media(min-width:53.8125rem){
  th{white-space:nowrap}
  .scroll>table:not(.kv):not(.cmp) tr>:first-child{padding-left:.75rem}
  html{scroll-padding-top:4rem}
  .scroll:has(>table.ls){overflow:visible}
  table.ls thead :is(th,td){position:sticky;top:0;z-index:2;padding-top:.75rem;background:var(--sticky);
    border-bottom:0;box-shadow:inset 0 -1px var(--line2)}
}
/* ── lists ────────────────────────────────────────────────────────────────────────────────── */
ul.plain{list-style:none;margin:0;padding:0}
ul.plain li{position:relative;padding:.875rem 0;border-bottom:1px solid var(--line)}
ul.plain li:last-child{border-bottom:0}
/* fix round 4: a name without a page of its own is the row's bare text, which kept its longest word whole and pushed the
   figures out (320 px with WCAG text spacing: 'Einwohnergemeinde Biberstein', 47 px sideways); it may break like a link */
.row{display:flex;justify-content:space-between;gap:1rem;align-items:baseline;overflow-wrap:anywhere}
.row>*{min-width:0;overflow-wrap:anywhere}
.row>.when,.row>.nw{flex:none}
.row>.sub,.row>.num:not(.nw){flex:0 1 auto;min-width:auto;text-align:right;overflow-wrap:normal}
ul.plain .row>a:first-child::after,ul.plain .row>div:first-child>a:first-child::after{content:"";position:absolute;inset:0}
ul.plain li a~a,ul.plain .row>:not(:first-child) a,ul.plain .sub a{position:relative;z-index:1}
ul.plain li:hover{background:var(--hover)}
ul.plain.cols2{columns:2;column-gap:3.5rem}
ul.plain.cols2 li{break-inside:avoid}
.when{color:var(--ink);font-size:.875rem;white-space:nowrap;font-weight:700}
.when.soon,td.when.soon{color:var(--warm)}
.when.today,td.when.today{color:var(--hot);white-space:normal}
.row>.when.today{flex:none;max-width:45%;text-align:right}
.when time{white-space:nowrap}
.when .rel{display:block;font-weight:400;font-size:.875rem;white-space:normal;overflow-wrap:normal}
td.when.today,td.when.soon{white-space:normal}
p.xh{margin:.625rem 0 0;font-size:.875rem;color:var(--muted)}
/* fix round 4: a row whose deadline passes while the page is open stays in its place (it went, and the list moved by
   0.04-0.38), muted, 'abgelaufen' as its label (/stand.js); the next page view leaves it out (J_LIST) */
[data-deadline].off .when,[data-deadline].off a,[data-deadline].off>b,[data-deadline].off .rel{color:var(--muted)}
/* ── chips ────────────────────────────────────────────────────────────────────────────────── */
.tags{display:flex;flex-wrap:wrap;gap:.625rem;margin-top:1rem}
.tag{display:inline-block;max-width:100%;padding:.5rem .875rem;border:1px solid var(--field);font-size:.9375rem;line-height:1.4;
  color:var(--ink);background:transparent;text-decoration:none;transition:border-color .2s,background-color .2s,color .2s}
a.tag:hover{border-color:var(--gold-hi);background:var(--hover);color:var(--ink)}
/* a link to a list of open tenders under a page's title (fix round 2: a flat gold chip, a second button style beside
   the alert's): an outlined chip with the arrow of the home's links */
a.tag[data-open]::after{content:"\00a0\2192";content:"\00a0\2192"/"";color:var(--brass)}
a.tag[data-open]{position:relative}
a.tag[data-open] .ocn{position:absolute;top:-.6875rem;right:-.5rem;min-width:1.625rem;padding:.0625rem .4375rem;border-radius:.8125rem;
  background:var(--grad);color:var(--on-brass);font:700 .8125rem/1.35 var(--sans);text-align:center;font-variant-numeric:tabular-nums}
a.tag[data-open] .ocn:empty{display:none}
/* ── panels: the alert in brass, the others dark ──────────────────────────────────────────── */
.glass{position:relative;margin-top:1.5rem;border:1px solid var(--line);background:var(--card)}
.glass .pad{padding:0 1.5rem 1.375rem}
.glass .pad.top{padding-top:1.25rem}
.glass.alert{margin-top:2.75rem;border:0;border-top:1px solid var(--brass);
  background:linear-gradient(100deg,rgba(201,162,78,.16),rgba(201,162,78,.05) 55%,rgba(201,162,78,.02)),var(--alert-bg)}
/* a grid, not a wrapping flex row (fix round 1): with the fallback font the button wrapped under the text and
   with the web font it did not, and the box changed height by 28 px when the font arrived (CLS 0.24-0.36) */
.alert .pad{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:1rem 2rem;padding:1.5rem 1.75rem}
.alert .pad>p{margin:0;font-size:1.0625rem;color:var(--ink)}
.alert .pad>p.lead{grid-column:1/-1;font-weight:700}
.alert .pad>p.act{grid-column:2;display:flex;flex-wrap:wrap;gap:.75rem;align-items:center;justify-content:flex-end}
.alert .tag{border-color:var(--field)}
a.btn.gh{color:var(--gold-hi)}
a.btn.gh::before{background:var(--grad)}
a.btn.gh::after{inset:1px;background:#0b0a08;clip-path:polygon(0 0,100% 0,100% calc(100% - .5625rem),calc(100% - .5625rem) 100%,0 100%)}
a.btn.gh:hover::after,a.btn.gh:focus-visible::after{clip-path:polygon(100% 0,100% 0,100% calc(100% - .5625rem),100% 100%,100% 100%)}
a.btn.gh:hover,a.btn.gh:focus-visible{color:var(--on-brass)}
/* the scope under 'Frist verpasst? …' (fix round 2): what the alert would cover, not the promise again */
.alert .pad>p.sc{color:var(--gold-hi)}
.winner{margin:.75rem 0 0;padding:1.125rem 1.25rem;border-left:2px solid var(--brass);background:var(--card)}
.winner .who{font:700 1.375rem/1.3 var(--sans);color:var(--ink)}
.official{margin-top:1.75rem;padding:.875rem 1.125rem;border-left:2px solid var(--line2);background:var(--card);font-size:.9375rem;color:var(--muted)}
.acts{display:flex;flex-wrap:wrap;align-items:center;gap:.75rem 1rem;margin-top:1.5rem}
.acts .rep{font-size:.9375rem}
a.btn{min-height:3.25rem;padding-inline:1.5rem 1.625rem;font-size:.875rem}
a.btn::after{transition:clip-path .3s cubic-bezier(.33,0,0,1)}
.dl{margin:1rem 0 0;font-size:.9375rem}
.empty{margin:1.5rem 0 0;font-size:1.125rem;color:var(--ink)}
details.more summary{cursor:pointer;margin:.75rem 0 0;padding:.25rem 0;font-size:.9375rem;font-weight:700;color:var(--link)}
abbr.fb::after{content:"*"}
p.fbn{margin:.5rem 0 0}
.lead{font-weight:700;color:var(--ink)}
/* the most repeated spacing, as classes (on 92,000 pages) */
.sub.sb2{display:block;margin-top:.125rem}
.sub.sb3{display:block;margin-top:.1875rem}
.sub.sb6{display:block;margin-top:.375rem}
.sub.sb0{display:block}
.sub.mt5{margin-top:.3125rem}
.mt3{margin-top:.1875rem}
.mt4{margin-top:.25rem}
.mt10,ul.plain.mt10{margin-top:.625rem}
ul.plain.mt6{margin-top:.375rem}
.m10{margin:.625rem 0 0}
.m106{margin:.625rem 0 .375rem}
.m14{margin:.875rem 0 0}
.m18{margin:1.125rem 0 0}
.prose p.p4{margin:0 0 .25rem}
.nw{white-space:nowrap}
/* ── the A–Z, the pager, the finder, the search ───────────────────────────────────────────── */
.az{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.25rem 0 0;padding:0;list-style:none}
.az a,.az span{display:inline-block;min-width:2.75rem;padding:.375rem .625rem;border:1px solid var(--field);text-align:center;
  font:400 1.375rem/1.1 var(--display);letter-spacing:.04em;color:var(--ink);text-decoration:none;transition:background-color .2s,color .2s}
.az a:hover{background:var(--hover);border-color:var(--gold-hi)}
.az [aria-current]{background:var(--grad);border-color:transparent;color:var(--on-brass)}
.az [aria-current] small{opacity:1}
.az small{display:block;font:400 .8125rem/1.3 var(--sans);letter-spacing:0;color:inherit;opacity:.85}
@media(min-width:62.5rem){ul.azl{columns:2;column-gap:3.5rem}ul.azl li{break-inside:avoid}ul.azl .row>.sub{white-space:nowrap}}
/* the canton index (fix round 2): the 26 cantons in a grid, each with its awards and a bar, the most first */
.az.kg{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,11.5rem),1fr));gap:.625rem;margin-top:1.5rem}
@media(max-width:37.5rem){.az.kg{grid-template-columns:repeat(2,minmax(0,1fr));gap:.5rem}.az.kg a{padding:.625rem .75rem .75rem}}
.az.kg a{display:grid;grid-template-columns:auto minmax(0,1fr);align-items:baseline;gap:.25rem .75rem;width:100%;height:100%;
  min-width:0;padding:.75rem .875rem .875rem;text-align:left;font:400 1rem/1.3 var(--sans);letter-spacing:0}
.az.kg b{grid-row:1;grid-column:1;font:400 1.875rem/1 var(--display);letter-spacing:.04em;color:var(--gold-hi)}
.az.kg small{grid-row:1;grid-column:2;justify-self:end;font:700 .9375rem/1.3 var(--sans);opacity:1;color:var(--ink);
  font-variant-numeric:tabular-nums}
.az.kg .nm{grid-row:2;grid-column:1/-1;font-style:normal;color:var(--text);overflow-wrap:break-word;hyphens:auto;-webkit-hyphens:auto}
.az.kg a:hover .nm{color:var(--ink)}
.az.kg i{grid-row:3;grid-column:1/-1;align-self:end;height:3px;margin-top:.375rem;
  background:linear-gradient(90deg,#8f6c2c,#f2d892) 0 0/var(--w,0) 100% no-repeat,rgba(244,241,234,.08)}
.pn{display:flex;justify-content:space-between;gap:.75rem;flex-wrap:wrap;margin-top:1.5rem}
form.finder{position:relative;padding:1.375rem 1.5rem;border:1px solid var(--line);background:linear-gradient(180deg,rgba(244,241,234,.06),rgba(244,241,234,.02))}
form.finder .dh{display:block;margin-bottom:.875rem;font:400 clamp(1.75rem,1.4rem + 1.2vw,2.5rem)/1 var(--display);
  letter-spacing:.02em;text-transform:uppercase;color:var(--ink)}
form.finder .row2{display:flex;position:relative}
form.finder .dsub{display:block;margin-top:.75rem;color:var(--muted);font-size:.9375rem;line-height:1.5}
form.search-page{display:flex;max-width:40rem;margin:1.75rem 0 0;position:relative}
form.search-page label{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
form.search-page input{font-size:1.125rem;padding:.75rem .875rem .75rem 2.5rem;min-height:3.25rem}
form.search-page button{font-size:.875rem;padding:0 1.25rem;min-height:3.25rem}
.search-res{margin-top:1.5rem}
#treffer.wait{min-height:85vh}
.search-res h2{margin:2rem 0 .375rem}
.search-res ul.plain li{padding:.625rem 0}
.search-res .kind{color:var(--muted);font-size:.875rem}
.search-dirs h3{margin:1.75rem 0 0}
.search-dirs .az{display:grid;grid-template-columns:repeat(auto-fill,minmax(3.25rem,1fr))}
.search-dirs .az a{display:block}
/* the live results under a search field (js/suche.js) */
.search-pop{position:absolute;left:0;right:0;top:calc(100% + .375rem);z-index:40;min-width:min(100%,20rem);max-height:min(72vh,37.5rem);
  overflow:auto;padding:.25rem 0 .375rem;background:#0b0a08;border:1px solid rgba(201,162,78,.6);box-shadow:0 1.25rem 2.5rem rgba(0,0,0,.6);text-align:left}
.search-pop[hidden]{display:none}
.search-grp{display:block;padding:.75rem 1rem .25rem;font:700 .8125rem/1.4 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}
/* fix round 5: 'Treffer als Wortteil' under the tenders' name when no tender matches whole (js/suche.js) */
.search-grp .tw{display:block;margin-top:.375rem;padding-top:.375rem;border-top:1px solid var(--line2);color:var(--muted);letter-spacing:.1em}
.search-opt{display:block;padding:.5rem 1rem;color:var(--ink);text-decoration:none;line-height:1.35;font-size:1rem}
.search-opt:hover{color:var(--ink);background:var(--hover)}
.search-opt[aria-selected=true]{background:var(--hover);box-shadow:inset 3px 0 var(--brass)}
.search-opt .sub{display:block;margin-top:.125rem;font-size:.875rem}
.search-opt.all{font-weight:700;color:var(--gold-hi)}
.search-msg{display:block;padding:.75rem 1rem;color:var(--muted);font-size:.9375rem}
/* ── forms: the alert and the filters ─────────────────────────────────────────────────────── */
.form{margin-top:1.25rem;max-width:40rem;position:relative}
.form .f{display:block;font:700 .9375rem/1.4 var(--sans);color:var(--ink);margin:1.5rem 0 .5rem}
.form input[type=email]{width:100%;min-height:3rem;border:1px solid var(--field);border-radius:0;padding:.75rem .875rem;font:inherit;font-size:1rem;
  line-height:1.4;background:#0b0a08;color:var(--ink)}
.form input[type=email]::placeholder{color:var(--muted)}
.form input[type=email]:focus{outline:3px solid var(--focus);outline-offset:1px;border-color:var(--brass)}
.form fieldset{border:0;margin:0;padding:0;min-width:0}
.form legend.f{padding:0;float:left;width:100%}
.form legend.f+*{clear:both}
.form .pills{display:flex;flex-wrap:wrap;gap:.5rem}
.form .pills label{cursor:pointer;position:relative;display:inline-block}
.form .pills input{position:absolute;opacity:0;width:1px;height:1px;left:0;top:0}
.form .pills input:checked+.tag{background:var(--grad);border-color:transparent;color:var(--on-brass);font-weight:700}
.form .pills input:checked+.tag::before{content:"\2713\00a0";content:"\2713\00a0"/""}
.form .pills input:focus-visible+.tag{outline:3px solid var(--focus);outline-offset:2px}
.form .pills.k{gap:.375rem}
.form .pills.k .tag{padding:.375rem .625rem;font-size:.875rem}
.form .pills.k .tag b{font-weight:700}
.form details.grp{margin-top:.5rem;border:1px solid var(--line);background:var(--card)}
.form details.grp>summary{display:flex;align-items:center;gap:.625rem;min-height:3rem;padding:.625rem .875rem;cursor:pointer;
  font-weight:700;font-size:1rem;line-height:1.35;color:var(--ink);list-style:none}
.form details.grp>summary::-webkit-details-marker{display:none}
.form details.grp>summary::after{content:"+";content:"+"/"";margin-left:auto;font:700 1.25rem/1 var(--sans);color:var(--brass)}
.form details.grp[open]>summary::after{content:"\2212";content:"\2212"/""}
.form details.grp:has(input:checked)>summary::before{content:"";width:.5rem;height:.5rem;flex:none;background:var(--brass);transform:rotate(45deg)}
.form details.grp .pills{padding:.125rem .875rem .875rem}
.form button{margin-top:1.5rem;min-height:3.25rem;padding-inline:1.75rem 1.875rem;font-size:.875rem}
.form button:disabled,.form button[aria-disabled=true]{opacity:.6;cursor:progress}
.form .hp{position:absolute;left:-9999px;opacity:0}
.form .msg{margin-top:.875rem;font-size:1rem;min-height:1.4em}
.form .msg.err,.form .ferr{color:var(--hot)}
.form .ferr{margin:.5rem 0 0;font-size:.9375rem}
.form input[aria-invalid=true]{border-color:var(--hot)}
.form .pv{margin:1.125rem 0 0;padding:.75rem .875rem;border-left:2px solid var(--brass);background:var(--card);font-size:1rem;color:var(--ink);
  min-height:4.75rem}
.form .pv small{display:block;margin-top:.125rem;font-size:.875rem;color:var(--muted)}
/* fix round 1: without a script no selection (it would not reach Brevo), the summary of the selection beside the
   button, the Branchen filter, and two columns from 1000 px (the selection left, the address and the button right) */
html:not(.j) #abo fieldset,html:not(.j) #abo .pv,html:not(.j) #abo .sumry{display:none}
.form .sumry{margin:1rem 0 0;min-height:1.6em;font-size:1rem;font-weight:700;color:var(--ink)}
.form .bq{display:flex;flex-direction:column;gap:.3125rem;margin:0 0 .625rem;font:700 .8125rem/1.35 var(--sans);letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted)}
.form .bq input{width:100%;max-width:22rem;min-height:2.75rem;margin:0;font:inherit;font-size:1rem;font-weight:400;letter-spacing:0;
  text-transform:none;line-height:1.3;padding:.5rem .625rem;border:1px solid var(--field);border-radius:0;background:#0b0a08;color:var(--ink)}
.form .bqn{margin:.25rem 0 .5rem;font-size:.9375rem;color:var(--muted)}
@media(min-width:62.5rem){
  .form.two{max-width:none;display:grid;grid-template-columns:minmax(0,1fr) minmax(18rem,24rem);grid-template-areas:"sel em" "sel side";
    grid-template-rows:auto 1fr;column-gap:3.5rem;align-items:start}
  .form.two .fe{grid-area:em}
  .form.two .fsel{grid-area:sel}
  .form.two .fside{grid-area:side;position:sticky;top:1rem}
}
/* the filter bar of the tender lists (fix round 1): in the page from the start, so nothing moves when the
   script arrives; shown only with JavaScript (the class j, set in the page's head), its controls behind
   'Filter' on a phone */
html:not(.j) .flt{display:none}
.j p.fn{display:none}
.flt{margin:1rem 0 .5rem;padding:1rem 1.125rem;border:1px solid var(--line);border-top-color:rgba(201,162,78,.5);background:var(--card)}
.flt .fd>summary{display:none}
.flt .fc{display:flex;flex-wrap:wrap;gap:.75rem .875rem;align-items:flex-end}
.flt label{display:flex;flex-direction:column;gap:.3125rem;font:700 .8125rem/1.35 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);min-width:0}
.flt .fq{flex:2 1 14rem}
.flt .fk,.flt .fb{flex:1 1 9.5rem}
.flt .fs{flex:1 1 13.5rem}
.flt .chks{display:flex;flex-direction:column;gap:.25rem}
.flt .chks .chk{min-height:1.75rem}
.flt .fl2{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem 1rem;margin-top:.75rem}
.flt .fl2 .cnt{flex:1 1 18rem;margin:0}
.flt .fl2 .fa,.flt .fl2 .clr{min-height:2.25rem;padding-block:.25rem}
.flt .fl2 .fa{margin-left:auto}
.flt .fan{margin:.5rem 0 0;font-size:.875rem;color:var(--muted)}
.zs{margin:.75rem 0 0;font-size:.9375rem;color:var(--ink)}
table.tl tr.ab{display:none}
table.tl tr.tier td,.search-res .plain li.tier{padding:.75rem 0 .5rem;border-bottom:1px solid var(--line2);font:700 .8125rem/1.35 var(--sans);letter-spacing:.14em;
  text-transform:uppercase;color:var(--gold)}
table.tl tbody tr.tier:hover,.search-res li.tier:hover{background:none}
table.tl tbody tr.tier:hover>:first-child{box-shadow:none}
table.tl.ls tr.tier>td::before{content:none}
table.tl.ls tr.tier>td{grid-column:1/-1;grid-row:1;text-align:left}
table.tl.ls tr.ab>td{grid-column:1/-1;grid-row:1;text-align:left}
table.tl.ls tr.ab>td::before{content:none}
tr.ab .glass.alert{margin:0}
table.ls tbody tr.cut{display:none}
.title.lst{padding:1.5rem 0 1rem}
/* a list's heading on one line where it can, a long one a size smaller (genera.lst_h1), a short lead: the first
   tender at y <= 600 at 1280 (fix round 1) */
.title.lst h1{margin-top:.625rem;font-size:clamp(2.25rem,1.25rem + 2.6vw,3.25rem)}
.title.lst h1.lg{font-size:clamp(2rem,1rem + 2vw,2.625rem)}
.title.lst p.sum{max-width:none;margin-top:.75rem;font-size:1.0625rem;line-height:1.5}
@media(min-width:53.8125rem){.title.lst{grid-template-columns:minmax(0,1fr) auto}}
@media(max-width:37.5rem){
  .flt{padding:.625rem .875rem .75rem}
  .flt .fd>summary{display:flex;align-items:center;gap:.5rem;min-height:2.75rem;cursor:pointer;list-style:none;
    font:700 .8125rem/1.3 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--gold-hi)}
  .flt .fd>summary::-webkit-details-marker{display:none}
  .flt .fd>summary::after{content:"+";content:"+"/"";margin-left:auto;font:700 1.25rem/1 var(--sans);color:var(--brass)}
  .flt .fd[open]>summary::after{content:"\2212";content:"\2212"/""}
  .flt .fd[open]>.fc{margin:.375rem 0 .25rem}
  table.tl tr.ab{display:block}
  .ab-out,.title.lst .rail{display:none}
}
.flt input[type=search],.flt select{width:100%;min-height:2.75rem;font:inherit;font-size:1rem;font-weight:400;letter-spacing:0;text-transform:none;line-height:1.3;
  padding:.5rem .625rem;border:1px solid var(--field);border-radius:0;background:#0b0a08;color:var(--ink)}
.flt .chk{flex-direction:row;align-items:center;gap:.5rem;font:400 1rem/1.3 var(--sans);letter-spacing:0;text-transform:none;color:var(--ink);min-height:2.75rem}
.flt .chk input,.kb .fbx input{-webkit-appearance:none;appearance:none;flex:none;width:1.375rem;height:1.375rem;margin:0;
  border:1px solid var(--field);border-radius:0;background:#0b0a08 50%/.875rem no-repeat;cursor:pointer;
  transition:background-color .15s,border-color .15s}
.flt .chk input:hover,.kb .fbx input:hover{border-color:var(--gold-hi)}
.flt .chk input:checked,.kb .fbx input:checked{border-color:var(--brass);background-color:var(--brass);
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3 8.4 6.4 11.8 13 4.6' fill='none' stroke='%230b0905' stroke-width='2.2'/%3E%3C/svg%3E")}
.flt .chk input:focus-visible,.kb .fbx input:focus-visible{outline:3px solid var(--focus);outline-offset:2px}
.flt button,button.all{min-height:2.75rem;padding:.5rem 1rem;border:1px solid var(--field);background:transparent;color:var(--gold-hi);
  font:700 .8125rem/1.3 var(--sans);letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:background-color .2s,color .2s}
.flt button:hover,button.all:hover{background:var(--brass);border-color:var(--brass);color:var(--on-brass)}
button.all{margin:.875rem 0 0}
.flt .fa{min-height:2.75rem;display:inline-flex;align-items:center}
.flt .cnt{margin:.75rem 0 0;min-height:1.45em;font-size:.9375rem;font-weight:700;color:var(--ink)}
.flt .cnt:focus{outline:none}
.flt .cnt.hl{animation:hl 1.8s ease-out}
@keyframes hl{0%,30%{background:rgba(201,162,78,.3);box-shadow:0 0 0 .3125rem rgba(201,162,78,.3)}
  100%{background:rgba(201,162,78,0);box-shadow:0 0 0 .3125rem rgba(201,162,78,0)}}
.flt-none{margin:1rem 0 0;font-size:1rem;color:var(--ink)}
.totop{position:fixed;right:1rem;bottom:1rem;z-index:35;padding:.625rem 1rem;border:1px solid var(--brass);background:#0b0a08;
  color:var(--gold-hi);font:700 .8125rem/1.2 var(--sans);letter-spacing:.12em;text-transform:uppercase;text-decoration:none}
.totop:hover{background:var(--brass);color:var(--on-brass)}
.totop[hidden]{display:none}
/* a canton's awards in one industry (js/kb.js) */
.kb{position:relative;margin-top:2rem;padding:1.25rem 1.5rem 1.5rem;background:var(--card)}
.kb h2{margin:0}
.kb h3{margin:1.5rem 0 .5rem}
.kb .kbx{float:right;margin:0 0 .5rem .75rem}
/* fix round 5: beside its list (1024-1440 px) the panel is half the page, and the newest awards' table, a list table
   that does not scroll on a wide screen (its headers stick), stood out of it and the page scrolled sideways by 67-195 px:
   here its headers wrap, its words break at their hyphens, and what still does not fit scrolls in the panel */
.kb th{white-space:normal}
.kb td{-webkit-hyphens:auto;hyphens:auto}
.kb .scroll:has(>table.ls){overflow-x:auto}
.rk a.kbs[aria-current]{font-weight:700;color:var(--gold-hi)}
html:not(.j) .kbh{display:none}
/* the panel's share of awards placed at the authority's seat, and the toggle that leaves them out (fix round 1) */
.kb .fbx{display:flex;align-items:center;gap:.5rem;margin:.5rem 0 0;font-size:.9375rem;color:var(--ink);cursor:pointer}
/* the check-your-mail and done pages, the 404 */
.blk{margin-top:1.75rem}
.blk p{margin:0 0 .75rem}
.nf h2{margin:0 0 .625rem}
/* ── footer: the A and the name, the data line, the simap notice, the links ─────────────────── */
footer{margin-top:5.5rem;padding:3.25rem max(var(--gut),(100% - var(--max))/2) 3.5rem;border-top:1px solid rgba(201,162,78,.34);
  background:#000;color:var(--muted);font-size:.9375rem;line-height:1.65}
footer::before{display:flex;align-items:center;min-height:1.875rem;padding-left:2.625rem;margin-bottom:1.5rem;
  background:var(--mk) 0 50%/1.875rem no-repeat;font:400 1.625rem/1 var(--display);letter-spacing:.05em;text-transform:uppercase;color:var(--ink)}
footer p{margin:.625rem 0 0;max-width:33em}
footer .stand{color:var(--text)}
footer a{color:var(--gold-hi)}
/* ── narrow screens ──────────────────────────────────────────────────────────────────────── */
@media(max-width:53.75rem){
  .title{padding:2rem 0 1.75rem;grid-template-columns:minmax(0,1fr);gap:1.5rem}
  .rail{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:.5rem 1rem;align-items:baseline;padding-left:1rem}
  .rail dt,.rail dd{margin:0}
  .cols,.half{grid-template-columns:minmax(0,1fr);gap:2rem}
  .glass .pad,.alert .pad{padding-inline:1.125rem}
  .alert .pad{grid-template-columns:minmax(0,1fr)}
  .alert .pad>p.act{grid-column:1;justify-content:flex-start}
  .cmp td.c{width:6rem}
  .cmp th,.cmp td,.cmp thead td{padding:.75rem .5rem}
  ul.plain.cols2{columns:1}
  .top .n0{display:none}
  td.r,th.r{padding-left:.75rem}
  /* the list tables as stacked rows, labels and units from the CSS (genera.css_labels) */
  table.ls,table.ls thead,table.ls tbody{display:block}
  table.ls thead{position:absolute;width:1px;height:1px;margin:-1px;overflow:hidden;clip-path:inset(50%)}
  table.ls tbody{border-top:1px solid var(--line2)}
  /* a card per row (fix round 1): the right column never wider than 42 %, so a date or a deadline keeps its
     line; words break at a hyphenation point, not anywhere ('17.09.202|6', 'Ingenieurleistung|en') */
  table.ls tbody tr{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,42%);column-gap:1rem;row-gap:.375rem;padding:1rem 0;border-bottom:1px solid var(--line)}
  table.ls td{display:block;grid-column:1/-1;min-width:0;padding:0;border:0;overflow-wrap:break-word;hyphens:auto;-webkit-hyphens:auto;white-space:normal}
  table.ls td:first-child{grid-column:1;grid-row:1}
  table.ls td:last-child{grid-column:2;grid-row:1;text-align:right;padding-left:0}
  table.ls td::before{display:block;font:700 .8125rem/1.4 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);white-space:nowrap}
  table.ls time,table.ls .num data,table.ls td.num{white-space:nowrap}
  /* fix round 3: a deadline's label and date keep their line when it turns 'today' or 'soon' (the class let them wrap and
     the card grew a line under the reader; its 'läuft heute ab' line below is kept free by the list's head script) */
  table.ls td.when,table.ls td.when.today,table.ls td.when.soon{white-space:nowrap}
  table.ls td:first-child::before{display:inline;margin-right:.5rem}
  table.ls tbody tr:hover>:first-child{box-shadow:none}
  /* the note under an amount ('vermutlich Einheitspreis', 'Preise je Unternehmen') runs the card's whole width */
  table.awb td:last-child .sub,table.awc td:last-child .sub{width:238.1%;margin-left:-138.1%}
  table.ls td:last-child .sub.rt{width:auto;margin-left:auto}
  table.awc td:nth-child(3){grid-column:1;grid-row:3}
  table.awc td:nth-child(4){grid-column:2;grid-row:3;text-align:right}
  table.tl td:nth-child(3){grid-column:1/-1}
  table.tl td:last-child::before,table.awc td:nth-child(4)::before,table.tl td:nth-child(3)::before{display:inline;margin-right:.375rem}
  table.tl tbody tr{row-gap:.25rem;padding:.75rem 0}
  /* fix round 4: the divider row keeps its own rule only (the card's under it drew a second one) */
  table.tl tbody tr.tier{padding:0;border-bottom:0}
  table.tl td:nth-child(2){font-size:.9375rem;line-height:1.38}
  table.tl td:nth-child(3){font-size:.875rem;line-height:1.45}
  /* item 14: on a canton's page (and a buyer's) its awards by Branche before the long table of companies */
  .half:has(figure.rk[aria-labelledby="chart-sectors"])>div:last-child{order:-1}
  /* item 20: the Branchen index's labels unspaced, so 'ADJUDICATIONS' and 'AGGIUDICAZIONI' fit their third */
  table.dv td::before{letter-spacing:.02em}
  /* the Branchen index as cards: the name, then the code, the open tenders and the awards side by side */
  table.dv tbody tr{grid-template-columns:repeat(3,minmax(0,1fr))}
  table.dv td:first-child{grid-column:1/-1;grid-row:1;font-weight:700}
  table.dv td:first-child::before{content:none}
  table.dv td:nth-child(n+2){grid-row:2;grid-column:auto;text-align:left;padding-left:0}
  /* the companies and authorities ranked on a page as cards (fix round 2): the name on a row of its own, the awards
     and the sum under it ('Eraneos Switz-erland AG' in a 150 px column of the canton x Branche panel) */
  table.fk tbody tr{grid-template-columns:repeat(2,minmax(0,1fr))}
  table.fk td:first-child{grid-column:1/-1;grid-row:1}
  table.fk td:first-child::before{content:none}
  table.fk td:nth-child(2){grid-column:1;grid-row:2;text-align:left}
  table.fk td:last-child{grid-row:2}
  table.fk td:nth-child(2)::before,table.fk td:last-child::before{display:inline;margin-right:.375rem}
}
@media(max-width:37.5rem){
  .kv,.kv tbody,.kv tr,.kv th,.kv td{display:block;width:auto}
  .kv th{padding:.75rem 0 .125rem;border-bottom:0}
  .kv td{padding:0 0 .75rem;border-bottom:1px solid var(--line)}
  .flt .cnt{min-height:3.2em}
  th{letter-spacing:.04em;white-space:normal;overflow-wrap:anywhere;hyphens:auto;-webkit-hyphens:auto}
  th.r{overflow-wrap:normal;hyphens:manual;-webkit-hyphens:manual}
  th.r:not(.amt){white-space:nowrap}
  td{overflow-wrap:break-word;hyphens:auto;-webkit-hyphens:auto}
  td.r,th.r{padding-left:.625rem}
  .masthead [role=search] button{padding:0 .625rem;letter-spacing:.06em}
  .alert .pad>p.act{flex-basis:100%}
  a.btn{width:100%;justify-content:space-between}
  .acts{gap:.625rem}
  .cmp td.c{width:4.75rem}
  .cmp thead th{overflow-wrap:anywhere}
  .runhead>span{letter-spacing:.1em}
}
/* the rail on a narrow phone: the label above its value (fix round 2: Datenschutz broke 'Privatperso/n' and
   'abo@auftra/gsregister.c/h' in a column beside 'VERANTWORTLICHE PERSON') */
@media(max-width:26.25rem){.rail{display:block}.rail dt{margin:.875rem 0 0}.rail dt:first-child{margin-top:0}
  .rail dd{margin:.125rem 0 0}
  h1,h2{hyphens:auto;-webkit-hyphens:auto;hyphenate-limit-chars:12 5 5}}
@media(max-width:30rem){table.fk td.num::before{display:block;margin-right:0}}
/* ── forced colours: frames instead of fills ─────────────────────────────────────────────── */
@media(forced-colors:active){
  .fig b,.fig.today b,.fig.off b{background:none;-webkit-text-fill-color:CanvasText;color:CanvasText}
  .sitenav li:last-child a,a.btn,.form button,.langs .on,.az [aria-current]{border:2px solid ButtonText}
  .sitenav li:last-child a::before,.sitenav li:last-child a::after,a.btn::before,a.btn::after,
  .form button::before,.form button::after{display:none}
  .flt .chk input,.kb .fbx input{appearance:auto;-webkit-appearance:auto}
  .fig.rate .approx,.sub.rt{border-color:CanvasText}
  .cc td>span,.bl .trk i,.ber .t i{forced-color-adjust:none;background:CanvasText}
  .langs .on{outline:2px solid Highlight}
  .masthead summary::before{background:none;border-block:2px solid CanvasText}
}
/* ── print: the record on paper, black on white; the links to simap.ch printed out ────────────── */
@media print{
  :root{--paper:#fff;--card:#fff;--panel:#fff;--sticky:#fff;--band:#fff;--alert-bg:#fff;--ink:#000;--text:#000;--muted:#333;
    --line:#bbb;--line2:#555;--link:#000;--link-hover:#000;--gold:#000;--gold-hi:#000;--hot:#000;--warm:#000;--ok:#000;
    --hover:transparent;--brass:#555;color-scheme:light}
  @page{margin:16mm 14mm}
  html,body{background:#fff;color:#000}
  body{font-size:10.5pt;line-height:1.45}
  .skip,.masthead details,.masthead [role=search],.langs,.sitenav,.crumbs,.alert,.tags,.dl,.form,details.more>summary,noscript,
  a.fig>span::after,.acts,p.src,.search-pop,.flt,.totop,button.all,.kb .kbx,footer::before,.tg,.ab-out,tr.ab,
  .masthead a.name::after{display:none!important}
  .masthead{display:block;padding:0 0 6pt;border-bottom:1px solid #999;background:#fff}
  .fig.wide,.glass,.winner,.official,.state{background:#fff!important}
  .masthead a.name{min-height:0;font-size:12pt;color:#000}
  .masthead a.name::before{display:none}
  main{display:block}
  .crumbs{width:auto}
  .title{display:block;padding:6pt 0 10pt}
  .title .rail{margin-top:8pt;border-left:0;padding-left:0}
  h1{font-size:20pt}
  h1.rec{font-size:16pt}
  .runhead{margin-top:16pt;border-color:#999}
  .figures{display:flex;flex-wrap:wrap;gap:6pt;padding:10pt 0 0}
  .fig{flex:1 1 30%;border:1px solid #999;padding:6pt 8pt}
  .fig b{font-size:15pt;background:none;-webkit-text-fill-color:#000;color:#000}
  .fig.wide::before,.cols>.prose+div::before{display:none}
  .cols,.half{display:block}
  .cols>.prose+div{background:#fff;padding:0}
  .scroll{overflow:visible!important}
  table{font-size:9.5pt}
  thead{display:table-header-group}
  tr,li,.fig,figure,.winner,.official,.glass{break-inside:avoid}
  h1,h2,h3,.runhead{break-after:avoid}
  a{color:#000;text-decoration:underline}
  tbody td a::after{content:none}
  a[href^="https://www.simap.ch"]::after{content:" <" attr(href) ">";font-size:9pt;word-break:break-all}
  figure,.winner,.official{border:1px solid #999;background:#fff}
  .cc td>span,.bl .trk i,figure .note .key{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  footer{margin-top:16pt;padding:8pt 0 0;color:#000;border-color:#999}
}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;
  transition-duration:.01ms!important;scroll-behavior:auto!important}}
"""
# The home's own rules (step 4): in the <head> of the four home pages (and the root), not in the sheet
# the 92,000 other pages load. They extend the classes above; js/home.js moves what they describe.
HOME_CSS = r"""
/* ── the home (A2 as approved, 14.10.2026): full-bleed bands, each with its content centred ───────── */
main>.band{grid-column:1/-1}
.band .in{width:min(var(--max),100% - 2*var(--gut));margin-inline:auto}
.band h2{font-size:clamp(2.5rem,1.6rem + 3.6vw,4.75rem);line-height:.9}
.sh{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:end;gap:1.125rem 2.5rem;margin-bottom:2.75rem}
.sh .eyebrow,.sh .lede{grid-column:1/-1}
.sh .lede{margin-top:0}
.sh .aside{font:700 .8125rem/1.4 var(--sans);letter-spacing:.18em;text-transform:uppercase;color:var(--muted);padding-bottom:.5rem;margin:0}
.more{display:inline-flex;align-items:center;gap:.625rem;margin-top:1rem;min-height:2.75rem;color:var(--gold-hi);
  font:700 .8125rem/1.3 var(--sans);letter-spacing:.16em;text-transform:uppercase;text-decoration:none}
.more:hover{color:var(--link-hover)}
.ar{flex:none;width:1.25rem;height:.75rem;transition:transform .25s cubic-bezier(.33,0,0,1)}
.more:hover .ar,a.btn:hover .ar,a.btn:focus-visible .ar,.door:hover .ar,.door:focus-within .ar{transform:translateX(.3rem)}
/* the hero: the question, the brass pillars of the awards per month, the doors */
/* fix round 1: at least the screen's height, as tall as its content needs (a fixed height with overflow:hidden
   cut the doors off at 1280×800, 1366×768, 1280×720, 1024×768 and 1536×864, and 13 elements with WCAG text
   spacing); clipped sideways only (overflow-x:clip is no scroll container, so a focused door cannot scroll it) */
.hero{position:relative;isolation:isolate;z-index:0;display:grid;min-height:clamp(40rem,100svh - 6.5rem,60rem);background:#000;overflow-x:clip}
.hero .recede{position:relative;display:grid;transform-origin:50% 0}
.hero .shade{position:absolute;inset:0;background:#000;opacity:0;pointer-events:none;z-index:5}
.hero .bg{position:absolute;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.vign{position:absolute;inset:0;background:radial-gradient(120% 90% at 78% 70%,rgba(201,162,78,.16),transparent 55%),
  radial-gradient(70% 60% at 10% 0%,rgba(244,241,234,.05),transparent 60%),linear-gradient(180deg,rgba(0,0,0,0) 60%,#000 100%)}
.ghost{position:absolute;right:-1.5vw;top:8%;font:400 clamp(15rem,31vw,29.5rem)/.78 var(--display);color:transparent;
  -webkit-text-stroke:1px rgba(201,162,78,.26);white-space:nowrap;user-select:none}
.hero .glow{position:absolute;inset:0;z-index:1;pointer-events:none;opacity:0;transition:opacity .6s;
  background:radial-gradient(27.5rem circle at var(--mx,70%) var(--my,35%),rgba(201,162,78,.16),transparent 62%)}
.hero.glow-on .glow{opacity:1}
.hero-in{position:relative;z-index:3;display:grid;container-type:inline-size;grid-template-columns:minmax(0,1fr) minmax(0,31.25rem);
  grid-template-rows:1fr auto;column-gap:2.5rem;padding-top:2rem}
.hero .copy{grid-column:1/-1;grid-row:1;max-width:56rem;align-self:center;padding-bottom:1.5rem;position:relative;z-index:2}
.hero h1{margin-top:1.125rem;font-size:clamp(3.5rem,min(7.6vw,10.6svh),7.75rem);line-height:.9;text-shadow:0 2px 30px rgba(0,0,0,.6)}
.hero .aud{margin:1.25rem 0 0;max-width:min(58ch,100cqw - 33.5rem);font-size:clamp(1.125rem,1rem + .4vw,1.25rem);line-height:1.45;color:var(--ink)}
.hero .lead{margin:.625rem 0 0;max-width:min(62ch,100cqw - 33.5rem);font-size:clamp(1.0625rem,1rem + .2vw,1.15625rem);font-weight:400;color:var(--text)}
.ctas{margin:1.625rem 0 0;display:flex;flex-wrap:wrap;gap:1.125rem 1.625rem;align-items:center}
.ctas a.btn{min-height:3.625rem;padding-inline:1.5rem 1.625rem;font-size:.875rem}
.sky{grid-column:2;grid-row:1;align-self:end;justify-self:end;width:min(31.25rem,100%);height:min(44svh,21.875rem);position:relative;z-index:1;
  display:flex;align-items:flex-end;gap:5px;pointer-events:none}
.sky i{position:relative;flex:1;height:var(--h);min-height:3px;border-radius:2px 2px 0 0;
  background:linear-gradient(180deg,rgba(246,226,166,.95) 0,rgba(215,178,99,.75) 18%,rgba(168,128,58,.32) 62%,rgba(140,104,44,.05) 100%);
  box-shadow:0 -10px 24px -14px rgba(242,216,146,.55)}
.sky i.p{background:repeating-linear-gradient(-45deg,rgba(201,162,78,.75) 0 2px,transparent 2px 6px);box-shadow:inset 0 0 0 1px rgba(201,162,78,.6)}
.sky i.pk{background:linear-gradient(180deg,#fff2c8 0,#f2d892 14%,rgba(201,162,78,.55) 60%,rgba(140,104,44,.08) 100%);box-shadow:0 0 36px -6px rgba(242,216,146,.6)}
.sky .pkl{position:absolute;bottom:calc(100% + .875rem);right:-.25rem;font:400 .8125rem/1.35 var(--sans);letter-spacing:.14em;
  text-transform:uppercase;color:var(--gold-hi);white-space:nowrap;text-align:right}
.sky .pkl b{display:block;font:400 2.125rem/1 var(--display);letter-spacing:.02em}
.horizon{position:absolute;left:-50vw;right:-50vw;top:0;height:1px;pointer-events:none;
  background:linear-gradient(90deg,transparent 0,rgba(201,162,78,.5) 35%,rgba(242,216,146,.95) 72%,rgba(201,162,78,.35) 100%)}
.doors{grid-column:1/-1;grid-row:2;position:relative;display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr) minmax(0,.55fr);
  gap:1.375rem;padding:1.375rem 0 1.75rem}
.door{position:relative;display:grid;grid-template-columns:minmax(0,1fr) auto;align-content:start;gap:.125rem 1.125rem;padding:1.125rem 1.375rem;
  color:var(--ink);text-decoration:none;isolation:isolate;margin:0}
.door::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,rgba(244,241,234,.07),rgba(244,241,234,.025));
  border:1px solid rgba(244,241,234,.1);transition:inset .35s cubic-bezier(.33,0,0,1),background .35s}
div.door:hover::after,div.door:focus-within::after{inset:.375rem;background:linear-gradient(180deg,rgba(201,162,78,.14),rgba(201,162,78,.04))}
/* the door of the open tenders (fix round 1): its count is the link and covers the door; the 'N neue' badge is a
   link of its own above it (to the list's 'Neu' filter) */
.door a.big{color:var(--ink);text-decoration:none}
.door a.big::after{content:"";position:absolute;inset:0;z-index:1}
.door a.dnew{position:relative;z-index:3;text-decoration:none}
.door a.dnew:hover{border-color:var(--gold-hi);background:var(--hover)}
.door::before{content:"";position:absolute;inset:0;pointer-events:none;z-index:2;transition:inset .35s cubic-bezier(.33,0,0,1);
  background:linear-gradient(var(--brass),var(--brass)) 0 0/.75rem 1px,linear-gradient(var(--brass),var(--brass)) 0 0/1px .75rem,
    linear-gradient(var(--brass),var(--brass)) 100% 0/.75rem 1px,linear-gradient(var(--brass),var(--brass)) 100% 0/1px .75rem,
    linear-gradient(var(--brass),var(--brass)) 0 100%/.75rem 1px,linear-gradient(var(--brass),var(--brass)) 0 100%/1px .75rem,
    linear-gradient(var(--brass),var(--brass)) 100% 100%/.75rem 1px,linear-gradient(var(--brass),var(--brass)) 100% 100%/1px .75rem;
  background-repeat:no-repeat}
div.door:hover::before,div.door:focus-within::before{inset:-.375rem}
.door .k{grid-column:1/-1;font:700 .8125rem/1.35 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--gold)}
.door .big{grid-column:1;display:flex;align-items:baseline;flex-wrap:wrap;gap:.25rem .75rem}
.door .big b{font:400 4rem/.9 var(--display);letter-spacing:.01em;background:var(--grad-v);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:var(--gold-hi)}
.door .big .lbl{font:400 1.875rem/1 var(--display);text-transform:uppercase;letter-spacing:.03em}
.door .dnew{grid-column:1/-1;display:inline-flex;align-items:center;gap:.5625rem;justify-self:start;margin-top:.375rem;padding:.25rem .625rem;
  font:700 .8125rem/1.35 var(--sans);letter-spacing:.06em;color:var(--gold-hi);border:1px solid rgba(201,162,78,.5)}
.door .dnew::before{content:"";width:.4375rem;height:.4375rem;border-radius:50%;background:var(--gold-hi);flex:none;box-shadow:0 0 0 0 rgba(243,220,154,.6);animation:ping 1.6s cubic-bezier(.2,.6,.3,1) 3}
@keyframes ping{0%{box-shadow:0 0 0 0 rgba(243,220,154,.7)}80%,100%{box-shadow:0 0 0 .5rem rgba(243,220,154,0)}}
.door .sub{grid-column:1/-1;margin-top:.5rem;font-size:.9375rem;line-height:1.45;color:var(--muted)}
.door .ar{grid-column:2;grid-row:2;align-self:center;color:var(--brass)}
form.finder.door{padding:1.125rem 1.375rem;border:0;background:none;display:block}
form.finder.door .dh{font-size:2.875rem;line-height:.95;margin:.25rem 0 .875rem}
.hmeta{align-self:end;justify-self:end;text-align:right;font:400 .8125rem/1.7 var(--sans);letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin:0}
.hmeta b{color:var(--gold-hi)}
/* pinned only while it fits the screen (js/home.js sets .pin): pinned taller than the screen, its doors would
   never come into view */
@media(min-width:56.25rem) and (min-height:43.75rem) and (max-height:87.5rem) and (prefers-reduced-motion:no-preference){.hero.pin{position:sticky;top:0}}
.hero~*{position:relative;z-index:3}
/* 01 · the map of the open tenders per canton (official 2026 boundaries; js/home.js draws and reads it) */
.mapsec{background:radial-gradient(60% 55% at 32% 58%,rgba(201,162,78,.09),transparent 70%),var(--band);border-top:1px solid rgba(201,162,78,.38);
  padding:7.5rem 0 6.25rem;box-shadow:0 -2.5rem 5rem rgba(0,0,0,.7)}
.mapsec .stage{position:relative}
@media(min-width:56.25rem) and (min-height:53.75rem) and (max-height:87.5rem) and (prefers-reduced-motion:no-preference){
  .js .mapsec.pin{height:205svh;padding:0}
  .js .mapsec.pin .stage{position:sticky;top:0;height:100svh;display:flex;flex-direction:column;justify-content:flex-start;padding:5.5rem 0 1.25rem}
  .js .mapsec.pin .sh{margin-bottom:.875rem}
}
.mapgrid{display:grid;grid-template-columns:minmax(0,1fr) 20.625rem;gap:2.75rem;align-items:center}
.mapbox{position:relative}
.mapbox canvas{width:100%;display:block}
.mapbox .mapfb{width:100%;height:auto;display:block}
.mapbox.ready .mapfb{display:none}
.mapbox .tip{position:absolute;left:0;top:0;z-index:4;pointer-events:none;padding:.5625rem .75rem .625rem;background:rgba(5,4,3,.94);
  border:1px solid var(--brass);color:var(--ink);white-space:nowrap;opacity:0;transform:translate(-9999px,0);transition:opacity .15s}
.mapbox .tip.on{opacity:1}
.mapbox .tip b{display:block;font:400 1.625rem/1 var(--display);letter-spacing:.03em;color:var(--gold-hi)}
.mapbox .tip span{display:block;margin-top:.25rem;font-size:.8125rem;color:var(--text)}
.maplegend{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem 1.125rem;margin:.875rem 0 0;font-size:.875rem;color:var(--muted);max-width:none}
.maplegend .ramp{width:7.5rem;height:.5rem;background:linear-gradient(90deg,#3a2f1a,#8a6a2d 35%,#c9a24e 60%,#f2d892 85%,#fff4d8)}
.maplegend .sc{display:inline-flex;align-items:center;gap:.5rem}
.maplegend .sc b{font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums}
.mapsrc{margin:.375rem 0 0;font-size:.8125rem;color:var(--muted)}
html:not(.js) .maplegend span:last-child{display:none}
.ro{border-left:1px solid rgba(201,162,78,.3);padding-left:1.75rem}
.ro .rk{margin:0;font:700 .8125rem/1.35 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--gold)}
/* the name's box one line high exactly (fix round 4: 2.925 rem, not 2.9; js/home.js sets a long name a size smaller in
   it, and the box kept 0.4 px less than a line) */
.ro .nm{display:block;margin-top:.5rem;font:400 3.25rem/.9 var(--display);text-transform:uppercase;letter-spacing:.02em;color:var(--ink);min-height:2.925rem}
/* fix round 4: beside the map, the count and its words on one row whatever the count (French 'appels d’offres en cours'
   went under '1 492' and back beside a canton's '264', and the map moved by 12 px as the cantons lit up); the words may
   break rather than push out (WCAG text spacing); a phone's full-width read-out wraps as before */
.ro .vl{display:flex;flex-wrap:nowrap;align-items:baseline;gap:.25rem .75rem;margin:.625rem 0 0}
.ro .vl b{font:400 7rem/.8 var(--display);background:var(--grad-v);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:var(--gold-hi)}
.ro .vl span{font-size:.875rem;color:var(--text);max-width:9em;line-height:1.3;min-width:0;overflow-wrap:anywhere}
.ro .cum{margin:.75rem 0 0;font-size:.875rem;color:var(--muted)}
.ro .cum b{color:var(--ink)}
.ro .bar{height:3px;margin-top:.5rem;background:rgba(244,241,234,.08)}
.ro .bar i{display:block;height:100%;width:var(--w,100%);background:linear-gradient(90deg,#8f6c2c,#f2d892);transition:width .4s cubic-bezier(.2,.7,.2,1)}
.ro .go{margin:.875rem 0 0;font:700 .875rem/1.35 var(--sans)}
.ro .go a{color:var(--gold-hi)}
.ro .go a::after{content:"\00a0\2192";content:"\00a0\2192"/"";color:var(--brass)}
.lede .hc{display:none}
@media(pointer:coarse){.lede .hc{display:inline}.lede .hf{display:none}}
.kl{list-style:none;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 .875rem;margin:1.25rem 0 0;border-top:1px solid var(--line)}
.kl li{border-bottom:1px solid var(--line)}
.kl a{display:flex;justify-content:space-between;gap:.375rem;min-height:2rem;align-items:center;padding:.25rem .25rem;font-size:.875rem;color:var(--text);text-decoration:none;transition:background-color .15s,color .15s}
.kl a b{font-weight:700;color:var(--gold-hi);font-variant-numeric:tabular-nums}
.kl a:hover,.kl a.on{background:rgba(201,162,78,.16);color:var(--ink)}
.kl abbr{font-weight:700;letter-spacing:.06em}
/* the key figures, sliding over the hero */
.stats{background:var(--band);border-top:1px solid rgba(201,162,78,.38);padding:5.25rem 0 4.375rem;box-shadow:0 -2.5rem 5rem rgba(0,0,0,.7)}
.stats .figures{padding:0;gap:2.125rem 0;grid-template-columns:repeat(4,minmax(0,1fr))}
.stats .fig{padding:.375rem 1.625rem .25rem}
.stats .fig b{font-size:clamp(4rem,7vw,6.75rem);line-height:.86}
.stats .fig b small{font-size:2.25rem}
.stats .fig.money b{white-space:nowrap;font-size:clamp(3.25rem,5.4vw,5.5rem)}
.stats .fig.money b small{font-size:1.375rem;letter-spacing:.04em;margin-left:.1em}
.stats .rail{display:flex;flex-wrap:wrap;gap:.625rem 2.75rem;margin-top:3.5rem;padding:1.375rem 0 0;border:0;border-top:1px solid var(--line)}
.stats .rail div,.stats .rail{align-items:baseline}
.stats .rail dt{margin:0 .75rem 0 0;display:inline}
.stats .rail dd{margin:0 2.75rem 0 0;display:inline;font-size:.9375rem;color:var(--text)}
/* 02–04: the chart, the companies and the next deadlines, the industries */
.hsec{padding:7.5rem 0 2.5rem;background:#000}
.hsec figure.mc{margin:0;padding:0;background:none;border:0}
.hsec figure.mc>h2{font-size:clamp(2.5rem,1.6rem + 3.6vw,4.75rem);line-height:.9;margin:1.125rem 0 0}
.hsec figure.mc>.lede{margin:1rem 0 2.75rem;font-size:1.0625rem}
.mcp{--ch:17.5rem;--gap:5px;padding:2.125rem 2.125rem 1.625rem;background:linear-gradient(180deg,rgba(201,162,78,.05),rgba(201,162,78,0) 70%);border-top:1px solid rgba(201,162,78,.3)}
.mcp .unit{margin-top:0}
.two{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);gap:3.5rem;align-items:start}
.aside-col{position:sticky;top:1.5rem}
.sub-h{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;padding-bottom:.875rem;border-bottom:1px solid rgba(201,162,78,.4);margin-bottom:.375rem}
.sub-h h3{font-size:1.875rem;letter-spacing:.03em;margin:0}
.sub-h span{font:700 .8125rem/1.35 var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}
.top thead th,.top thead td{padding:0 .75rem .875rem}
.top td{padding:.75rem;vertical-align:baseline}
.top td.n0{padding-left:.25rem}
.top td:nth-child(2) a{font-weight:700}
.tl li{display:block}
.tl .row{flex-direction:column;gap:.375rem;align-items:flex-start}
.tl .when{display:flex;align-items:center;gap:.5625rem;font:700 .8125rem/1.35 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);white-space:normal}
.tl .when::before{content:"";width:.4375rem;height:.4375rem;border:1px solid currentColor;transform:rotate(45deg);flex:none}
.tl .when.soon{color:var(--warm)}
.tl .when.today{color:var(--hot)}
.tl .when.today::before{background:currentColor}
.tl .when .rel{display:inline;margin-left:.25rem;font-size:.8125rem}
.ber{list-style:none;margin:0;padding:0;columns:2;column-gap:3.5rem}
.ber li{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.375rem 1.125rem;padding:.8125rem 0;border-bottom:1px solid var(--line);break-inside:avoid;position:relative}
.ber a{font-size:1rem}
.ber a::after{content:"";position:absolute;inset:0}
.ber li:hover{background:var(--hover)}
.ber .v{font-weight:700;color:var(--gold-hi);font-variant-numeric:tabular-nums}
.ber .t{grid-column:1/-1;height:3px;background:rgba(244,241,234,.06)}
.ber .t i{display:block;height:100%;background:linear-gradient(90deg,#8f6c2c,#f2d892)}
/* the alarm band in brass, the closing links */
.alarm{position:relative;background:linear-gradient(100deg,#b78f43 0%,#d9b867 30%,#f3dc9a 52%,#d6b262 74%,#c09848 100%);color:var(--on-brass);
  padding:7.5rem 0 6.875rem;overflow:hidden}
.alarm::before{content:"";position:absolute;inset:0;background:radial-gradient(60% 120% at 80% 0%,rgba(255,255,255,.35),transparent 60%);pointer-events:none}
.alarm .in{position:relative;display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:2.5rem}
.alarm .in>*{grid-column:1}
.alarm .eyebrow{color:#2a2009}
.alarm .eyebrow::before{background:linear-gradient(90deg,transparent,#2a2009)}
.alarm h2{color:var(--on-brass);font-size:clamp(3.5rem,6.6vw,6.75rem);margin-top:1.25rem;max-width:21ch}
.alarm h2 .dot{color:#fff}
.alarm .s{margin:1.375rem 0 0;font-size:1.1875rem;max-width:44ch;color:#1d1608}
.alarm .ctas{margin-top:2.25rem}
.alarm a.btn{color:var(--gold-hi)}
.alarm a.btn::before{background:#1c1710}
.alarm a.btn::after{background:#0b0905}
.alarm a.btn:hover,.alarm a.btn:focus-visible{color:var(--gold-hi)}
.alarm a.btn:focus-visible{outline-color:#0b0905}
.alarm .since{grid-column:2;grid-row:1/span 4;align-self:center;text-align:right;color:var(--on-brass);margin:0}
.alarm .since b{display:block;font:400 clamp(11.25rem,22vw,20.625rem)/.8 var(--display);color:transparent;-webkit-text-stroke:2px #0b0905}
.alarm .since span{display:block;margin-top:.875rem;font:700 .875rem/1.35 var(--sans);letter-spacing:.2em;text-transform:uppercase}
.endband{position:relative;background:#000;padding-top:3.5rem}
.endband .tags{margin:0}
.js .endband{padding-top:13.125rem}
canvas.seam{position:absolute;left:0;right:0;top:0;width:100%;height:13.125rem;pointer-events:none;z-index:0}
.endband .in{position:relative;z-index:1}
main:has(>.endband){padding-bottom:0}
main:has(>.endband)+footer{margin-top:0;border-top:0;padding-top:2.5rem}
/* the motion of js/home.js: word reveals and block reveals only for what starts below the fold */
.split{display:inline}
.split .w{display:inline-block;max-width:100%}
.cnt{display:inline-block;white-space:nowrap}
.js [data-up]{transition:opacity .9s cubic-bezier(.2,.7,.2,1),transform 1s cubic-bezier(.2,.7,.2,1);transition-delay:var(--d,0s)}
.js [data-up].up0{opacity:0;transform:translate3d(0,1.625rem,0)}
@media(max-width:56.1875rem){
  .hero{min-height:0}
  .hero-in{padding-top:2.75rem;padding-bottom:2.25rem;grid-template-columns:minmax(0,1fr);grid-template-rows:auto auto auto}
  .hero h1{font-size:clamp(3.125rem,14.5vw,4.75rem)}
  .hero .aud,.hero .lead{max-width:62ch}
  .ghost{display:none}
  .sky{grid-column:1;grid-row:2;justify-self:stretch;width:100%;height:7.5rem;margin-top:4rem;gap:3px}
  .doors{grid-row:3;grid-template-columns:minmax(0,1fr);gap:.875rem;padding-top:1.375rem}
  .hmeta{justify-self:start;text-align:left}
  .stats .figures{grid-template-columns:repeat(2,minmax(0,1fr))}
  .stats .fig:nth-child(3){border-left:0;padding-left:0}
  .stats .fig b{font-size:clamp(3.375rem,15vw,4.5rem)}
  .stats .fig b small{font-size:1.375rem}
  .stats .fig.money b{font-size:clamp(2.75rem,12vw,3.75rem)}
  .stats .fig.money b small{font-size:1.125rem}
  .two{grid-template-columns:minmax(0,1fr);gap:4rem}
  .aside-col{position:static}
  .hsec{padding-top:5.5rem}
  .sh{grid-template-columns:minmax(0,1fr)}
  .mcp{padding:1.375rem 0 1.125rem;--ch:12.5rem;--gap:2px;background:none}
  .mapgrid{grid-template-columns:minmax(0,1fr);gap:1.625rem}
  .ro{border-left:0;padding-left:0;border-top:1px solid var(--line);padding-top:1.375rem}
  .ro .vl b{font-size:5.375rem}
  .ro .vl{flex-wrap:wrap}
  .mapsec{padding:6rem 0 4.375rem}
  .ber{columns:1}
  .alarm{padding:6rem 0 5.25rem}
}
@media(max-width:40rem){
  .ctas a.btn{width:100%;justify-content:space-between;letter-spacing:.06em;font-size:.8125rem}
  /* fix round 4: the read-out's canton keeps two lines while the map lights the cantons one by one ('Appenzell
     Ausserrhoden' took a second line and moved the page by 47 px, CLS 0.06-0.17); a size smaller on a narrow phone, so
     'Appenzell Rhodes-Extérieures' keeps to two lines (it took three at 320 px) */
  .ro .nm{font-size:min(3.25rem,13.6vw);min-height:1.8em}
  .door .big b{font-size:3.5rem}
  .door .big .lbl{font-size:1.625rem}
  form.finder.door .dh{font-size:2.25rem}
  .stats{padding:4rem 0 3.375rem}
  .stats .fig{padding:.25rem 0 0 1rem}
  .stats .fig:first-child,.stats .fig:nth-child(3){padding-left:0}
  .stats .fig>span{letter-spacing:.12em}
  .stats .rail{flex-direction:column;gap:.75rem}
  .alarm h2{font-size:clamp(3.125rem,14vw,4.5rem);hyphens:auto;-webkit-hyphens:auto}
  .alarm .in{grid-template-columns:minmax(0,1fr)}
  .alarm .since{grid-column:1;grid-row:auto;text-align:left;margin-top:2.5rem}
  .alarm .since b{font-size:9.375rem}
  .kl a{font-size:.875rem}
  .top td{padding:.75rem .375rem}
  .top thead th,.top thead td{padding:0 .375rem .625rem;letter-spacing:.06em;white-space:normal}
  .js .endband{padding-top:9.375rem}
  canvas.seam{height:9.375rem}
}
@media(max-width:23.75rem){.stats .figures{grid-template-columns:minmax(0,1fr)}.stats .fig,.stats .fig:nth-child(3){padding:1rem 0 0}}
/* the companies with the most awards as cards on a phone (fix round 2: names in a 150 px column, 'KIBAG Bauleistun-gen
   AG'): the name and its Branche on a row of their own, the awards and the sum under them; labels from css_labels */
@media(max-width:53.75rem){
  table.top,table.top tbody{display:block}
  table.top thead{position:absolute;width:1px;height:1px;margin:-1px;overflow:hidden;clip-path:inset(50%)}
  table.top tbody{border-top:1px solid var(--line2)}
  table.top tbody tr{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:1rem;row-gap:.375rem;padding:.875rem 0;
    border-bottom:1px solid var(--line)}
  table.top td{display:block;padding:0;border:0}
  table.top td:nth-child(2){grid-column:1/-1;grid-row:1}
  table.top td:nth-child(3){grid-column:1;grid-row:2;text-align:left}
  table.top td:nth-child(4){grid-column:2;grid-row:2}
  table.top td:nth-child(3)::before,table.top td:nth-child(4)::before{display:inline;margin-right:.375rem;
    font:700 .8125rem/1.4 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);white-space:nowrap}
  table.top tbody tr:hover>:first-child{box-shadow:none}
}
"""


def css_min(css: str) -> str:
    """The stylesheet as served: comments, line breaks, indentation and the spaces around { } ; , out, and the
    last ';' of each block. Nothing else is touched: the sheets are written so that this is safe (no '/*', no run
    of spaces and no space before or after a comma inside a string or a url()), and calc()'s spaces stay."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def css_labels() -> str:
    """The labels of the stacked list tables on a narrow screen (step 4, 15.10.2026): each cell says what it
    holds, a money cell its unit too, from the table's class (tl, awb, awc, lots; uk, um, uchf: the unit of its
    money column) and the column's place, in each language through :lang(). No attribute on any cell (byte
    budget). The labels are hidden from screen readers ('/""'), which read the column headers."""
    out, sig = [], []
    for l in LANGS:
        def t(k: str) -> str:
            return lingue.t(k, l)
        q = json.dumps(t("site"), ensure_ascii=False)
        sig.append(f':lang({l}) footer::before{{content:{q};content:{q}/""}}')
        # fix round 3 (item 24): '– nicht publiziert' under a list of awards, '– kein zurechenbarer Betrag' under a ranking
        for sel, k in (("table:is(.awb,.awc,.lots)", "not_published"), ("table:not(.awb,.awc,.lots)", "no_own_amount")):
            q = json.dumps("– " + t(k), ensure_ascii=False)
            sig.append(f':lang({l}) .scroll:has(>{sel} td.num>.sr:only-child)::after{{content:{q};content:{q}/""}}')
        # under the name in the header, on every page (fix round 1): 'unabhängig · nicht amtlich'
        q = json.dumps(t("indep"), ensure_ascii=False)
        sig.append(f':lang({l}) .masthead a.name::after{{content:{q};content:{q}/""}}')
        rules = [("table.tl td.when", t("deadline")), ("table.tl td:nth-child(3)", t("buyer")),
                 ("table.tl td:last-child", t("canton_abbr")), ("table.awb td.d", t("date")),
                 ("table.awb td:nth-child(3)", t("winner")), ("table.awc td.d", t("date")),
                 ("table.awc td:nth-child(3)", t("buyer")), ("table.awc td:nth-child(4)", t("canton_abbr")),
                 ("table.lots td.mono:first-child:not(.d)", t("lot")), ("table.lots td.d", t("date")),
                 ("table.lots td:nth-last-child(2)", t("winner")),
                 ("table.dv td:nth-child(2)", "CPV"), ("table.dv td:nth-child(3)", lingue.i("col_open", l)),
                 ("table.dv td:nth-child(4)", t("awards")), ("table.fk td:nth-child(2)", t("awards")),
                 ("table.top td:nth-child(3)", t("awards"))]
        # a money cell's label on a phone is its unit alone, short ('Tsd. CHF', 'k CHF'; fix round 1): the long
        # 'Betrag (milliers de CHF)' made the amount column the widest and squeezed the dates
        for u in ("k", "m", "chf"):
            rules.append((f"table.u{u} td:last-child", t("unit_" + u + "_ph")))
        for sel, txt in rules:
            q = json.dumps(txt, ensure_ascii=False)
            out.append(f':lang({l}) {sel}::before{{content:{q};content:{q}/""}}')
    return "".join(sig) + "@media(max-width:53.75rem){" + "".join(out) + "}"


# What the colour tokens of the CSS must satisfy (WCAG 2.2 AA). Design A2 (step 4, 15.10.2026) has one theme, dark,
# for everyone: text 4.5:1 against every background it is set on, and 3:1 for what identifies a control (the edge
# of a field or a chip, the brass of a button against the page), the focus ring and the chart marks. (foreground
# token, background token, minimum); a translucent colour is laid over --paper first. controlla.py reads the
# tokens from docs/style.css and measures each pair.
CONTRAST = (
    ("ink", "paper", 4.5), ("ink", "band", 4.5), ("ink", "card", 4.5), ("ink", "panel", 4.5), ("ink", "sticky", 4.5),
    ("ink", "alert-bg", 4.5), ("text", "paper", 4.5), ("text", "band", 4.5), ("text", "card", 4.5), ("text", "panel", 4.5),
    ("muted", "paper", 4.5), ("muted", "band", 4.5), ("muted", "card", 4.5), ("muted", "panel", 4.5),
    ("muted", "sticky", 4.5), ("muted", "off-bg", 4.5), ("muted", "alert-bg", 4.5),
    ("gold", "paper", 4.5), ("gold", "band", 4.5), ("gold", "card", 4.5), ("gold-hi", "paper", 4.5),
    ("gold-hi", "card", 4.5), ("gold-hi", "alert-bg", 4.5), ("link", "paper", 4.5), ("link", "card", 4.5),
    ("link-hover", "paper", 4.5), ("warm", "paper", 4.5), ("warm", "card", 4.5), ("hot", "paper", 4.5),
    ("hot", "card", 4.5), ("hot", "off-bg", 4.5), ("ok", "ok-bg", 4.5), ("ok", "paper", 4.5),
    ("on-brass", "brass", 4.5), ("on-brass", "brass-lo", 4.5), ("on-brass", "gold-hi", 4.5), ("paper", "ink", 4.5),
    ("brass", "paper", 3), ("brass", "card", 3), ("field", "paper", 3), ("field", "card", 3), ("focus", "paper", 3),
    ("focus", "card", 3), ("focus", "alert-bg", 3), ("mark", "panel", 3), ("mark", "paper", 3),
)
# The one font the first screen reads, preloaded: Instrument Sans 400, Latin (step 4). The display face is not
# preloaded (63 bytes on each of 92,000 pages); its fallback carries its metrics (fonts/fonts.css), so the swap
# moves no line. No type="font/woff2": every browser that preloads reads woff2.
PRELOAD = '<link rel="preload" href="{base}/fonts/is.woff2" as="font" crossorigin>\n'
# fix round 3 (item 32): the home's hero is set in the display face and its doors in the bold, both late without this
# (the hero's heading re-wrapped when they came); on the five home pages only (bytes)
HOME_PRELOAD = ('<link rel="preload" href="{base}/fonts/lg.woff2" as="font" crossorigin>\n'
                '<link rel="preload" href="{base}/fonts/is7.woff2" as="font" crossorigin>\n')
# Fix round 4: a tender's page (open or past its deadline) loads the bold face at once (17.7 KB): its row of buttons
# ('UNTERLAGEN … AUF SIMAP.CH', the calendar, the canton's list, 'Fehler melden') fits a 1440-px line in Instrument Sans
# bold and not in its fallback, and on a slow first visit the page moved by 0.20 when the face arrived. 67 bytes on the
# 9,408 tender pages (0.63 MB); the 63,316 award pages, whose row is short, go without (on all 72,724 detail pages the
# bold and the display face would cost 9.7 MB, the bold alone 4.9 MB, over the round's 3 MB). Every title's measure is
# in em (h1.rec), so the fallback no longer changes it.
BOLD_PRELOAD = '<link rel="preload" href="{base}/fonts/is7.woff2" as="font" crossorigin>\n'
# The icon: the SVG for browsers that take one; /favicon.ico and /apple-touch-icon.png sit at the root,
# where browsers and iOS look for them without a tag (two tags would cost 9 MB over the site).
# The header (step 4): the name and the search, then the menu and the languages; on a phone the menu sits behind
# the <details> ("Menü"), which needs no script and shows the menu right under it when opened. No wrapper
# around the page: the header and the footer run full width, the content is centred by the CSS.
HEAD = """<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{canon}{alts}
<link rel="icon" href="{base}/favicon.svg" type="image/svg+xml">
""" + PRELOAD + """<link rel="stylesheet" href="{base}/style.css">
{verify}</head><body>
<a class="skip" href="#inhalt">{skip}</a>
<header class="masthead"><a class="name" href="{base}/{lang}/">{sitename}</a>
<details><summary>{menu}</summary></details>{search}
<nav class="sitenav" aria-label="{navlabel}"><ul>{sitenav}</ul></nav><nav class="langs" aria-label="{langlabel}">{langnav}</nav></header>
"""


# The search (step 3b, 15.10.2026; the owner: "companies need to find whatever they want"): a field in
# the header of every page, phone included. A plain GET form: without JavaScript it opens /xx/suche/,
# whose A–Z directories lead to every entry; with it, /stand.js loads /js/suche.js at the first focus and
# the field becomes a combobox with live results. As few bytes as a working form takes, on 92,000 pages:
# its hook is role="search" (no class), type="search" and the placeholder are set by the script, the
# button carries the visible word. The redesign styles it as `.masthead [role=search]`.
SEARCH_WORDS = {l: [lingue.t("search", l), lingue.t("search_go", l)] for l in LANGS}


def search_form(lang: str, base: str = "") -> str:
    return (f'<form role="search" action="{base}/{lang}/suche/"><input name="q" aria-label="{e(lingue.t("search", lang))}">'
            f'<button>{e(lingue.t("search_go", lang))}</button></form>')

# The first footer line says "not official" in the READER's language. simap's §5
# notice must stay verbatim — which means German — so on its own it protected nobody
# who reads only French, Italian or English: the audit found the byte-identical German
# string on all four language versions, making the "it plainly says so" defence false
# on three of them. The verbatim notice keeps its lang="de" so screen readers switch.
# The data line opens the footer (14.10.2026): the date of the newest publication, how often the
# register is refreshed, and the methodology behind it.
FOOT = """</main><footer><p class="stand">{stand}<a href="{base}/{lang}/ueber/#methodik">{methodik}</a></p>
<p>{notoff}</p>
<p lang="de">{disc}</p>
<p>{srcnote}</p>
<p>{source}{colon} <a href="https://www.simap.ch">simap.ch</a> ({official}) ·
<a href="{abouthref}">{aboutlabel}</a> · <a href="{imphref}">{implabel}</a> · <a href="{privhref}">{privlabel}</a></p>
</footer><script src="{base}/stand.js" defer></script>{scripts}</body></html>"""


# The menu (14.10.2026; audit of 13.10.2026: there was none, and the tenders were linked only at
# the foot of the home). The five sections people look for, the about page, and the alert last: the CSS
# makes the last item the brass button at the end of the row (step 4), in the order a keyboard reaches it.
NAV = (("nav_tenders", "ausschreibungen/"), ("nav_companies", "unternehmen/"), ("nav_buyers", "auftraggeber/"),
       ("nav_cantons", "kanton/"), ("nav_sectors", "branche/"), ("nav_about", "ueber/"),
       ("nav_alert", "ausschreibungen/abo/"))
# The sections that have an index page, by the name the menu gives them. /auftrag/ deliberately has
# none — 18,000 awards do not belong in one alphabetical list — so no breadcrumb claims that level:
# it would point at a 404, and Google reads breadcrumbs as a promise about the site's shape.
# 'Branchen' (the 45 CPV divisions, /branche/) holds the 8-digit Bereiche (/bereich/) as its second
# level since step 3a (14.10.2026): their URLs stay, their breadcrumbs run through the division.
SECTION_KEY = {"ausschreibungen": "nav_tenders", "unternehmen": "nav_companies",
               "auftraggeber": "nav_buyers", "kanton": "nav_cantons", "branche": "nav_sectors",
               "bereich": "nav_sectors"}
SECTION_HOME = {"bereich": "branche"}
# paths written with robots noindex: the sitemap leaves them out (an empty canton list, 14.10.2026)
NOINDEX: set = set()


def trail(path: str, leaf: str, mid=None) -> list:
    """[(name, path)] from the register's home to this page. The BreadcrumbList and the visible
    breadcrumbs are both written from this one list, so they cannot disagree (14.10.2026). mid: the
    levels between home and the page that its URL does not show — a tender sits under its canton's
    open tenders, an award under its contracting authority."""
    parts = [x for x in path.strip("/").split("/") if x]
    if parts and parts[0] in LANGS:
        parts = parts[1:]
    out = [(_.home, f"/{LANG}/")]
    if not parts:
        return out
    sec = parts[0]
    if mid:
        out += list(mid)
    elif sec in SECTION_KEY:
        out.append((lingue.t(SECTION_KEY[sec], LANG), f"/{LANG}/{SECTION_HOME.get(sec, sec)}/"))
    if len(parts) > 1 or sec not in SECTION_KEY or sec in SECTION_HOME:
        out.append((leaf, path))
    return out


def crumbs_html(tr: list, leaf_lang: str = "", ld: bool = True) -> str:
    """Schema.org trail, so a result shows Startseite > Unternehmen > HOLINGER AG rather than a bare
    URL (ld: indexable pages only), and the same trail on the page above the title (none on the
    home itself, which carries no one-item BreadcrumbList either: step 3a, 14.10.2026)."""
    out = ""
    if ld and len(tr) > 1:
        items = [{"@type": "ListItem", "position": i, "name": n, "item": ORIGIN + p}
                 for i, (n, p) in enumerate(tr, 1)]
        js = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                         "itemListElement": items}, ensure_ascii=False).replace("<", "\\u003c")
        out = f'<script type="application/ld+json">{js}</script>\n'
    if len(tr) < 2:
        return out
    lis = [f'<li><a href="{BASE}{p}">{e(n)}</a></li>' for n, p in tr[:-1]]
    lis.append(f'<li><span aria-current="page"{leaf_lang}>{e(tr[-1][0])}</span></li>')
    return out + f'<nav class="crumbs" aria-label="{e(_.crumbs_label)}"><ol>{"".join(lis)}</ol></nav>\n'


def site_nav(path: str, tr: list) -> str:
    """The menu's items; the one for this page aria-current="page", else the section the breadcrumbs
    place the page in aria-current="true"."""
    sec = tr[1][1] if len(tr) > 1 else ""
    own = path in {f"/{LANG}/{h}" for _k, h in NAV}
    out = []
    for key, h in NAV:
        full = f"/{LANG}/{h}"
        cur = (' aria-current="page"' if full == path
               else ' aria-current="true"' if not own and full == sec else "")
        out.append(f'<li><a href="{BASE}{full}"{cur}>{e(lingue.t(key, LANG))}</a></li>')
    return "".join(out)


def stand_line(fresh: bool) -> str:
    """The footer's data line. A page that changes every day anyway (home, tender lists, about) states
    the date itself; every other page carries it through /stand.js, so it stays byte-identical from
    one night to the next — a date on all 92,000 pages would have rewritten every one of them daily
    for git and IndexNow. Without JavaScript those pages say nothing about it (step 3a: 'täglich
    aktualisiert' was a promise the nightly does not keep)."""
    if fresh:
        return e(_m("stand", d="\x00")).replace("\x00", tt(DATA_DATE, formato.date(DATA_DATE))) + " · "
    # without JavaScript nothing: the date is not on the page, and 'täglich aktualisiert' was a claim
    return '<span data-stand></span>'


def cap(text: str) -> str:
    """A table's caption, visually hidden: the running head above it names the section for a sighted
    reader, a screen reader announces the table by this one (audit 13.10.2026)."""
    return f'<caption class="sr">{e(text)}</caption>'


_TH = re.compile(r"<th(?![^>]*\bscope=)(?=[\s>])")


def scoped(body: str) -> str:
    """Every header cell says what it heads: scope="col" in a table's head, scope="row" in its body
    (audit 13.10.2026). One pass over the page, so no table written later can miss it."""
    def head(m):
        return _TH.sub('<th scope="col"', m.group(0))

    def rows(m):
        return _TH.sub('<th scope="row"', m.group(0))
    body = re.sub(r"<thead>.*?</thead>", head, body, flags=re.S)
    return re.sub(r"<tbody>.*?</tbody>", rows, body, flags=re.S)


def lang_path(path: str, lang: str) -> str:
    """The same page in another language: only the language segment changes."""
    parts = [x for x in path.strip("/").split("/") if x]
    if parts and parts[0] in LANGS:
        parts[0] = lang
    else:
        parts = [lang] + parts
    return "/" + "/".join(parts) + "/"


# words a cut description must not end on: articles, conjunctions, prepositions
_DESC_STOP = {"an", "auf", "aus", "bei", "über", "nach", "bis", "zwischen", "sur", "dans", "par",
              "avec", "entre", "chez", "su", "tra", "fra", "nel", "nella", "nei", "nelle", "sul",
              "sulla", "dal", "dalla", "on", "at", "by", "from", "in", "into", "a", "an"}


def fit_desc(text: str, limit: int = 155) -> str:
    """A description Google shows whole.

    The snippet is cut at roughly 155 characters, and 28 % of the pages were over it —
    the worst at 224 — so a third of the site advertised itself with a sentence that
    stopped mid-word. Cut at the last sentence that fits; if none worth keeping does, at
    the last clause boundary (comma, semicolon, dash) and only then at the last word,
    never after 'zu', 'avec', 'Zuschlag an' … (2,432 German descriptions ended '… an…',
    '… und…'; verifier 28.09.2026). Only ASCII whitespace is collapsed: the French
    U+00A0/U+202F stay (10,371 French descriptions had lost them).
    Builders drop their optional closing clause first (desc_pick); this is the last resort.
    """
    text = _ws(text)
    if len(text) <= limit:
        return text
    head = text[:limit + 1]

    def sentence_end(h: str) -> int:
        return max(h.rfind(". "), h.rfind("? "), h.rfind("! "), h.rfind(" ? "),
                   h.rfind(" ! "))

    cut = sentence_end(head)
    if cut >= limit * 0.6:
        return text[:cut + 1].rstrip()
    body = text[:limit - 1]
    clause = max(body.rfind(", "), body.rfind("; "), body.rfind(" ; "), body.rfind(" – "),
                 body.rfind(" – "))
    if clause >= limit * 0.6:
        c = body[:clause].rstrip(" ,;:  –—")
        # 'Lift-, Brandschutz- und …' cut at its first comma keeps 'Lift-', not 'Lift'
        return (c if _susp(c.split(" ")[-1]) else c.rstrip("-")) + "…"
    if cut >= limit * 0.35:
        return text[:cut + 1].rstrip()
    c = body[:body.rfind(" ")] if " " in body else body
    words = c.rstrip(" ,;:—–  /|").split(" ")
    stop = _TAIL_STOP | _DESC_STOP
    while len(words) > 1 and (words[-1].lower().strip(",;:  ") in stop
                              or words[-1] in _SEPS):
        words.pop()
    sp = _susp(words[-1])
    if sp:
        # the first half of a suspended compound keeps its hyphen: 'Umbau Natur-…'
        return " ".join(words[:-1] + [sp]) + "…"
    return " ".join(words).rstrip(" ,;:—–-  /|") + "…"


def desc_pick(*cands: str, limit: int = 155) -> str:
    """The first description that fits whole, else the last one cut by fit_desc: a template
    drops its optional closing clause ('– mit Auftraggebern, Beträgen und Kantonen', ',
    publiées sur simap.ch') before anything is cut."""
    for c in cands:
        if c and len(_ws(c)) <= limit:
            return _ws(c)
    return fit_desc(cands[-1], limit)


def og_tags(title: str, desc: str, path: str) -> str:
    """Open Graph and the Twitter card (14.10.2026), for a link shared in a chat or a social network:
    title, description, address, type, the card image of the page's language (1200×630) and the
    locale. X reads the og: tags for everything but the card type. title and desc come escaped."""
    # site name, image size and alt text since step 3a (14.10.2026); the card shows the register's name
    # and its domain, which is what the alt text says
    return (f'<meta property="og:type" content="website">\n'
            f'<meta property="og:site_name" content="{e(_.site)}">\n'
            f'<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="{desc}">\n'
            f'<meta property="og:url" content="{ORIGIN}{path}">\n'
            f'<meta property="og:image" content="{ORIGIN}/og-{LANG}.png">\n'
            '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{e(_.site)}">\n'
            f'<meta property="og:locale" content="{lingue.OG_LOCALE[LANG]}">\n'
            '<meta name="twitter:card" content="summary_large_image">\n')


def ld_script(data: dict) -> str:
    """A JSON-LD block; '<' escaped so no value can close the script element."""
    js = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{js}</script>\n'


def page(title: str, desc: str, body: str, path: str, kicker: str = "",
         leaf: str = "", robots: str = "", head_extra: str = "", fresh: bool = False,
         mid=None, leaf_lang: str = "", og=None, lastmod: str = "", scripts: tuple = ()) -> str:
    """One page in the site's shell. kicker is no longer shown (the menu marks the section since
    14.10.2026); fresh: the page changes every day anyway and states the data date itself
    (stand_line); mid, leaf_lang: the breadcrumb levels its URL does not show (trail) and the
    language of its last crumb when that is a publication's title in another language.
    og: the Open Graph tags, by default on every indexable page; an open tender's page (noindex)
    asks for them, the 66,000 award pages do not carry them (600 bytes a page; 14.10.2026)."""
    # hreflang tells the search engine these are one page in four languages, not four
    # pages competing with each other for the same query.
    # x-default is the page's own German version: it named the root for every page, a URL that
    # is no page's canonical (08.10.2026)
    # Only on indexable pages since 14.10.2026, like the BreadcrumbList: a noindex page leaves the
    # index with both, and the two cost 77 MB over the 71,000 award and tender pages.
    # robots 'noindex' alone since step 3b: following the links is every crawler's default ('noindex,follow'
    # said it in 7 more bytes on 75,000 pages)
    noindex = "noindex" in robots
    alts = "" if noindex else ("\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{ORIGIN}{lang_path(path, l)}">'
        for l in LANGS) + f'\n<link rel="alternate" hreflang="x-default" href="{ORIGIN}{lang_path(path, "de")}">')
    # each language named in its own language, and said so (lang, hreflang; audit 13.10.2026)
    nav = "".join(
        (f'<span class="on" lang="{l}" aria-current="true">{e(NAMES[l])}</span>' if l == LANG
         else f'<a href="{BASE}{lang_path(path, l)}" lang="{l}" hreflang="{l}">{e(NAMES[l])}</a>')
        for l in LANGS)
    tr = trail(path, leaf or re.split(r"\s[—–]\s", title)[0], mid)
    if noindex:
        NOINDEX.add(path)
    if lastmod:
        LASTMOD[path] = lastmod[:10]
    og_html = og_tags(e(title), e(fit_desc(desc)), path) if (not noindex if og is None else og) else ""
    # A noindex page names no canonical either (step 3a, 14.10.2026): it asks to stay out of the index,
    # so a URL for the index to keep says nothing — and it cost 7 MB over the 71,000 award and tender
    # pages, the room the step's own additions needed under GitHub Pages' 1 GB
    canon = "" if noindex else f'<link rel="canonical" href="{ORIGIN}{path}">\n'
    return (HEAD.format(title=e(title), desc=e(fit_desc(desc)), site=ORIGIN, base=BASE, path=path,
                        lang=LANG, alts=alts, canon=canon,
                        verify=VERIFY + (f'<meta name="robots" content="{robots}">\n' if robots else "")
                        + og_html + head_extra,
                        sitename=e(_.site), langnav=nav, langlabel=e(_.language), skip=e(_.skip),
                        navlabel=e(_.nav_label), sitenav=site_nav(path, tr), search=search_form(LANG, BASE),
                        menu=e(_.menu))
            + crumbs_html(tr, leaf_lang, ld=not noindex) + '<main id="inhalt">\n'
            + scoped(body) + FOOT.format(disc=e(DISCLAIMER), base=BASE, lang=LANG,
                                 stand=stand_line(fresh), methodik=e(_m("methodik")),
                                 notoff=e(_p.footer_note),
                                 abouthref=f"{BASE}/{LANG}/ueber/", aboutlabel=e(_.nav_about),
                                 imphref=f"{BASE}/{LANG}/impressum/",
                                 implabel=e(_.imprint),
                                 privhref=f"{BASE}/{LANG}/datenschutz/",
                                 privlabel=e(_.privacy),
                                 srcnote=e(_p.translation_note), source=e(_.source),
                                 colon=lingue.COLON[LANG],
                                 official=e(_p.source_inline),
                                 # the page type's script (step 3b): after /stand.js, whose helpers it uses
                                 scripts="".join(f'<script src="{BASE}/js/{x}.js?v={JS_VER[0]}" defer></script>'
                                                 for x in scripts)))


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
                                    "buyers": collections.Counter(), "sig": set(),
                                    "bsum": collections.Counter(), "bname": {}})
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
                # one authority however the publications spell it (norm_buyer, as the buyer pages do):
                # keyed by the raw name, 'Auftraggeber 71' counted spellings, not authorities
                bk = norm_buyer(a["buyerName"])
                c["buyers"][bk] += 1
                c["bname"].setdefault(bk, collections.Counter())[" ".join(a["buyerName"].split())] += 1
                if p is not None and len(ws) == 1:
                    c["bsum"][bk] += p
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
            # the six closest matches, shown by deadline: in score order the dates read as
            # unsorted (07.10., 19.10., 06.10. …; verifier 28.09.2026)
            top = [t for _, t in sorted(scored, key=lambda x: -x[0])[:6]]
            out[name] = sorted(top, key=lambda t: t.get("offerDeadline") or "9999")
    return out


def per_month(rows: list, until: str = "") -> dict:
    """Publication counts by month — the dimension the tables do not carry.

    until='YYYY-MM' extends the series with zero months up to that month, so a buyer
    that has gone quiet shows its silence instead of ending on its last award."""
    c = collections.Counter((r.get("publicationDate") or "")[:7] for r in rows
                            if (r.get("publicationDate") or "")[:7])
    if not c:
        return {}
    keys = sorted(c)
    # fill the gaps: a month with no awards is a fact, and leaving it out would
    # squeeze the axis and quietly imply activity that was not there
    out, y, m = {}, int(keys[0][:4]), int(keys[0][5:7])
    ly, lm = int(keys[-1][:4]), int(keys[-1][5:7])
    if until and until > keys[-1]:
        ly, lm = int(until[:4]), int(until[5:7])
    while (y, m) <= (ly, lm):
        out[f"{y:04d}-{m:02d}"] = c.get(f"{y:04d}-{m:02d}", 0)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def outlier_notes(rows: list, ser: list, own_buyer: bool = False) -> list:
    """A month swollen by one project (fix round 1): when one project gives more than a quarter of a month's
    awards (lots, mostly), the note under the chart says so — 'Sept. 2025: davon 142 Lose aus 3 Projekten von
    SBB …' — with the projects of a similar size beside it. own_buyer: the page is the authority's own (no name)."""
    by_m: dict = collections.defaultdict(collections.Counter)
    first: dict = {}
    for a in rows:
        m, pid = (a.get("publicationDate") or "")[:7], a.get("projectId")
        if m and pid:
            by_m[m][pid] += 1
            first.setdefault(pid, a)
    out = []
    for m, tot in ser:
        c = by_m.get(m)
        if not c or tot < 12:
            continue
        (_p1, k1), = c.most_common(1)
        if k1 < 5 or k1 <= 0.25 * tot:
            continue
        big = [pid for pid, k in c.most_common() if k >= max(5, 0.5 * k1)]
        n = sum(c[pid] for pid in big)
        lots = all(a.get("_lot") is not None for a in rows
                   if a.get("projectId") in big and (a.get("publicationDate") or "")[:7] == m)
        what = lingue.OUTLIER_WHAT[LANG][0 if lots else 1]
        bs = {norm_buyer(first[pid].get("buyerName") or "") for pid in big}
        who = "" if own_buyer or len(bs) != 1 else name_cut(_ws(first[big[0]].get("buyerName") or ""), 60)
        key = "mc_outlier" + ("_one" if len(big) == 1 else "") + ("_by" if who else "")
        out.append(_if(key, m=formato.month(m), k=formato.count(n), what=what, p=formato.count(len(big)), b=who))
    return out[-3:]


def month_chart(rows: list, title: str, fig_id: str = "chart-months", csv: str = "", own_buyer: bool = False) -> str:
    """Awards per month as a chart a reader understands without help (owner, 28.09.2026:
    "I don't understand the data in the charts"): a title that says what is counted, a
    one-line takeaway from complete months only (and saying so: a running month can be taller
    than the peak it names), a scale, readable month ticks, and the incomplete months drawn
    striped with a note saying why. Below the minimum data it is one sentence instead of a chart."""
    ser = sorted(per_month(rows, until=CUR_MONTH).items())
    if not ser:
        return ""
    tot = sum(v for _k, v in ser)
    part = {k for k, _v in ser if k < FULL_FROM or (k == CUR_MONTH and CUR_PARTIAL)}
    if tot < 12 or len(ser) < 6:
        # one sentence instead of a chart: "5 Zuschläge, alle im Juli 2026." — the plural
        # "Publikationsmonate: Juli 2026 (5)" named one month and repeated the count
        used = [(k, v) for k, v in ser if v]
        if len(used) == 1:
            lede = _if("mc_few_single" if tot == 1 else "mc_few_one", n=zuschlag(tot),
                       month=formato.month(used[0][0], full=True))
        else:
            # every month with its count: 'Mai 2026 (7), Aug. 2026 (1)', not '…, Aug. 2026.'
            months = ", ".join(formato.month(k) + f" ({formato.count(v)})" for k, v in used)
            lede = _if("mc_few", n=zuschlag(tot), k=formato.count(len(used)), months=months)
        return (f'<figure class="mc"><h2>{e(title)}</h2>'
                f'<p class="lede">{e(lede)}</p></figure>')
    comp = [(k, v) for k, v in ser if k not in part]
    tk = ""
    if comp:
        avg = sum(v for _k, v in comp) / len(comp)
        # a tie is named in full (122 charts per language named one month of a tie)
        peaks = grafici.peak_months(ser, part)
        top = dict(ser)[peaks[0]] if peaks else 0
        start, avg_s = formato.month(comp[0][0]), formato.num1(avg)
        if len(peaks) == 1:
            tk = _if("mc_takeaway", start=start, avg=avg_s,
                     peak_month=formato.month(peaks[0]), peak=formato.count(top))
        elif len(peaks) == 2:
            tk = _if("mc_takeaway_two", start=start, avg=avg_s, months=formato.month_list(peaks),
                     peak=formato.count(top))
        elif peaks:
            tk = _if("mc_takeaway_many", start=start, avg=avg_s, peak=zuschlag(top),
                     k=formato.count(len(peaks)))
    notes = []
    # a note describes only columns the reader can see: the build-up months when at least one
    # of them has an award, the running month as a striped column only when it has one — with
    # none so far, "striped last column" pointed at the last complete month instead.
    # The build-up is the archive's coverage (it starts in August 2024; owner, 28.09.2026):
    # said in the past tense, naming this chart's own striped months, singular for one column.
    ramp = [k for k, v in ser if k < FULL_FROM and v]
    if ramp:
        if len(ramp) == 1:
            notes.append(_if("mc_note_start_one", m=formato.month(ramp[0]),
                             start=formato.month(RAMP_START, full=True)))
        else:
            notes.append(_if("mc_note_start", span=formato.month_range(ramp[0], ramp[-1]),
                             start=formato.month(RAMP_START, full=True)))
    if CUR_PARTIAL and ser[-1][0] == CUR_MONTH:
        notes.append(_if("mc_note_end" if ser[-1][1] else "mc_note_end_zero",
                         m=formato.month(CUR_MONTH), date=formato.date(DATA_DATE)))
    notes += outlier_notes(rows, ser, own_buyer)
    return grafici.month_columns(ser, fig_id=fig_id, title=title, takeaway=tk,
                                 unit_label=_i.mc_unit, units=lingue.PLURALS[LANG],
                                 partial=part, notes=notes, src=chart_src(csv))


def division_figure(rows: list, sect_counter: collections.Counter, sectors: set[str], csv: str = "",
                    anchors: bool = False, unit: str = "") -> str:
    """Awards by CPV division (first two digits) as a ranked list with bars: the top 8 and
    one row for the rest, each with its share. Parent and sub-classes no longer compete
    for the same eight slots, so the list covers most awards instead of half. The links
    to the eight-digit sector pages stay, as a tag row under it. Each division row links to the
    division's page (step 3a, 14.10.2026: the canton pages' 'Informatikdienstleistungen 270' led
    nowhere); a canton × division view is step 3b."""
    div = collections.Counter(str(a.get("cpvCode") or "")[:2] for a in rows
                              if re.fullmatch(r"\d{2}", str(a.get("cpvCode") or "")[:2]))
    if not div:
        return ""
    ranked = sorted(div.items(), key=lambda kv: (-kv[1], kv[0]))
    # one industry left over is shown as a ninth row: "Übrige 1 Branchen" / "Altri 1 rami"
    # grouped a single row under a plural (6 buyer pages per language)
    top, rest = (ranked, []) if len(ranked) <= 9 else (ranked[:8], ranked[8:])

    def label(d: str) -> str:
        return lingue.CPV_SHORT[LANG].get(d) or cpv_label(d + "000000", d)

    def href(d: str):
        return f"{BASE}/{LANG}/branche/{d}/" if d in lingue.CPV_SHORT[LANG] else None

    if len(ranked) == 1:
        # a single bar at 100 % says nothing a sentence does not (368 buyer pages per language)
        n = ranked[0][1]
        out = (f'<figure class="rk" aria-labelledby="chart-sectors"><h2 id="chart-sectors">{e(_i.div_title)}</h2>'
               f'<p class="lede">{e(_if("div_single" if n > 1 else "div_single_one", n=zuschlag(n), label=label(ranked[0][0])))}</p></figure>')
    else:
        items = [(label(d), href(d), k, formato.count(k)) for d, k in top]
        other = None
        if rest:
            s = sum(k for _d, k in rest)
            other = (_if("div_other", k=formato.count(len(rest))), None, s, formato.count(s))
        lede = _if("div_lede_top", k=len(top), total=len(ranked)) if rest else _i.div_lede_all
        # a canton page: each row an anchor (#kb-72), the target of the Branche pages' canton rows, and the page's
        # money scale for the canton × Branche panel (js/kb.js; fix round 1)
        out = grafici.rank_list(items, fig_id="chart-sectors", title=_i.div_title, lede=lede,
                                other=other, total=sum(div.values()), src=chart_src(csv),
                                ids=[f"kb-{d}" if href(d) else "" for d, _k in top] if anchors else None)
        if unit:
            out = out.replace('<figure class="rk"', f'<figure class="rk" data-u="{unit}"', 1)
        if anchors:
            # the canton x Branche panel's hint in the page, shown with JavaScript only (fix round 3: js/kb.js inserted it
            # after the first paint and moved the rows, the deep link's target among them)
            out = re.sub(r'(<p class="lede"[^>]*>.*?</p>)', lambda m: m.group(1) + f'<p class="sub m10 kbh">{e(lingue.JS["kb_hint"][LANG])}</p>',
                         out, count=1, flags=re.S)
    tops = [(lab, code, k) for (lab, code), k in sect_counter.most_common(20) if code in sectors][:8]

    def tag_label(lab: str, code: str) -> str:
        # A division's own general code (45000000) carries the division's name: the list read
        # "Bauarbeiten 2’148" and the pill right under it "Bauarbeiten · 758" (462 /de/ pages).
        # The pill now names it for what it counts — the awards filed under the general code.
        if code[2:] == "000000" and code[:2] in lingue.CPV_SHORT[LANG]:
            return _if("tag_general", label=label(code[:2]))
        s = short_sector(lab, 48)
        # a few sub-codes carry their division's name word for word (fr/it 72500000
        # "Services informatiques"): the code itself tells them apart
        return f"{s} ({code})" if s.casefold() == label(code[:2]).casefold() else s

    if tops:
        out += (f'<p class="sub m14">{e(_i.detail_sectors)}</p><div class="tags">'
                + "".join(f'<a class="tag" href="{BASE}/{LANG}/bereich/{e(code)}/">'
                          f'{e(tag_label(lab, code))} · {formato.count(k)}</a>' for lab, code, k in tops)
                + "</div>")
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
        code = sig(main_cpv(c)[0])[:4]
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


_TAIL_STOP = {"und", "oder", "sowie", "bis", "der", "die", "das", "des", "den", "dem", "für", "von", "vom",
              "in", "im", "mit", "zu", "zur", "zum", "außer", "ausser", "ausgenommen",
              "einschließlich", "einschliesslich", "et", "ou", "de", "des", "du", "la", "le", "les",
              "pour", "en", "à", "au", "aux", "sauf", "y", "compris", "e", "o", "ed", "di", "del",
              "della", "dei", "degli", "delle", "per", "con", "a", "al", "da", "and", "or", "of",
              "the", "for", "with", "except", "including", "to",
              # prepositions and articles a cut stopped on ('Bodenbeläge aus…', 'sur la RC no 61,
              # sur…', 'Wettswil am…', 'per il…'; verifier 28.09.2026)
              "aus", "auf", "bei", "beim", "am", "an", "ans", "nach", "über", "unter", "gegen", "ohne",
              "durch", "gemäss", "gemäß", "zwischen", "als", "ein", "eine", "einer", "eines", "einem",
              "einen", "inkl.", "bzw.", "resp.", "evtl.", "sur", "avec", "par", "dans", "chez", "sous",
              "vers", "entre", "jusqu'à", "jusqu’à", "un", "une", "su", "sul", "sullo", "sulla", "sui",
              "sugli", "sulle", "alla", "allo", "alle", "ai", "agli", "nel", "nello", "nella", "nei",
              "negli", "nelle", "dal", "dallo", "dalla", "dai", "dagli", "dalle", "col", "tra", "fra",
              "il", "lo", "gli", "uno", "una", "at", "from", "on", "into", "by", "a", "an"}


def short_sector(name: str, limit: int) -> str:
    """A division name short enough for a call-out or a pill, cut so it still reads.

    The EU names run to 138 characters. A plain cut left "…und der Tierhaltung sowie"
    or an open parenthesis; this ends on the last whole word, drops a trailing
    conjunction, article or preposition and never stops inside "(…". On /de/ it
    writes Swiss spelling (ss), as the rest of the German site does.
    """
    name = _ws(name)
    if LANG == "de":
        name = name.replace("ß", "ss")
    if len(name) <= limit:
        return name

    def cut_at(room: int) -> str:
        # cut_end: whole words, no dangling 'und'/'des', no bracket left open, and the first
        # half of a suspended compound dropped with its hyphen ('…von Architektur-,
        # Konstruktions- und …' printed 'Dienstleistungen von Architektur…')
        c = cut_end(name, room)
        return c if _balanced(c) else ""

    # German suspended compounds ("Elektrizitätsverteilungs- und -schalteinrichtungen",
    # "Architektur- und Ingenieurbüros") put the cut between the two halves; dropping the
    # dangling half and the "und" before it left "Dienstleistungen…" or a bare "…" on 62
    # /de/ pills (verifier, 28.09.2026). A cut that keeps less than two words or twenty
    # characters is not a name: allow 16 more characters, then the full name.
    for room in (limit, limit + 16, limit + 24):
        if len(name) <= room:
            return name
        s = cut_at(room)
        if len(s.split()) >= 2 and len(s) >= min(20, limit // 2):
            return s + "…"
    m = re.fullmatch(r"(.+?)\s*\([^()]*\)", name)       # "RAID (Redundant Array …)" -> "RAID…"
    if m and len(m.group(1)) <= limit + 16:
        return m.group(1).rstrip(" ,;:–—-") + "…"
    return name if len(name) <= limit + 24 else cut_end(name, limit + 16) + "…"


def top_division(cpv: collections.Counter) -> str:
    """The company's main CPV division (first two digits), summed over ALL its awards.

    Taking [:2] of the single most common 8-digit code misreads a firm whose work is
    spread over many codes of one division (four awards under 71000000 would beat
    twelve spread over different 45… codes): measured 23.09.2026, the two readings
    disagree for 203 of the 2,558 company pages. Ties go to the lower code, so the page
    is the same from one build to the next.
    """
    div: collections.Counter = collections.Counter()
    for (code, _label), k in cpv.items():
        d = str(code)[:2]
        if len(d) == 2 and d.isdigit():
            div[d] += k
    return min(div.items(), key=lambda kv: (-kv[1], kv[0]))[0] if div else ""


def main_cpv(c: dict) -> tuple:
    """The company's main (code, label): the most frequent 8-digit code INSIDE its main
    division, ties to the lower code. The header took the first of Counter.most_common while
    the alert took top_division, so a firm with one award in 45210000 and one in 31500000
    read 'Lavori generali di costruzione di edifici' above an alert for «Materiale elettrico e
    illuminazione» (verifier, 28.09.2026)."""
    div = top_division(c["cpv"])
    keys = [(k, n) for k, n in c["cpv"].items() if str(k[0])[:2] == div] or list(c["cpv"].items())
    return min(keys, key=lambda kv: (-kv[1], str(kv[0][0]), kv[0][1]))[0] if keys else ("", "")


def twin_notes(rows: list, keys: list) -> dict[int, str]:
    """Rows whose visible text repeats in one table -> the sub-line that tells them apart:
    the project number when the twins belong to different projects ('Umbau und Erweiterung
    Jurastrasse 16' twice for the Integra foundation, projects 34265 and 34307), else the
    publication number (three awards of project 38433, one per lot, identical on the page)."""
    groups = collections.defaultdict(list)
    for i, k in enumerate(keys):
        groups[k].append(i)
    out: dict[int, str] = {}
    for idx in groups.values():
        if len(idx) < 2:
            continue
        projs = [str(rows[i].get("projectNumber") or "") for i in idx]
        by_proj = len(set(projs)) == len(projs) and all(projs)
        for i in idx:
            r = rows[i]
            out[i] = (_if("project_no", n=r.get("projectNumber")) if by_proj
                      else _if("publication_no", n=r.get("publicationNumber") or r.get("projectNumber") or ""))
    return out


def alert_callout(c: dict) -> str:
    """The free e-mail alert, offered where most visitors actually land.

    8 of the 10 queries with the most impressions in Search Console are company names,
    and the alert was offered only on the tenders pages. The link carries the
    company's main canton and division so the form opens already filled in; it is
    nofollow because thousands of parameter URLs are not pages worth crawling.
    """
    cant = next((k for k, _n in c["cant"].most_common() if k in CANTONS), "")
    return alert_box(cant, top_division(c["cpv"]))


def div_name(div: str) -> str:
    """A CPV division's short name in the page's language ('' when the vocabulary has none)."""
    return (lingue.CPV_SHORT[LANG].get(div) or short_sector(cpv_label(div + "000000", ""), 60)
            if div else "")


def alert_href(cant: str = "", div: str = "") -> str:
    """The alert form, prefilled through ?k=ZH&b=45 (ABO_JS): only a canton code and a two-digit
    division the form can name; '' parts are left out."""
    cant = cant if cant in CANTONS else ""
    div = div if re.fullmatch(r"\d{2}", div or "") and div_name(div) else ""
    query = "&".join(f"{k}={v}" for k, v in (("k", cant), ("b", div)) if v)
    return f"{BASE}/{LANG}/ausschreibungen/abo/" + (f"?{query}" if query else "")


def alert_box(cant: str = "", div: str = "", lead: str = "", feed: str = "", missed: bool = False, ghost: bool = False) -> str:
    """The company pages' alert box, on every page that has a canton or an industry (14.10.2026: the
    canton, industry, buyer and tender pages led to the empty form). The same wording, the form
    prefilled with the page's canton and CPV division; lead: a sentence before it (a missed deadline,
    an empty list). data-k/data-b: the selection, for a later script. missed (fix round 2): after the
    missed-deadline lead only the alert's scope ('Branche «…», Kanton Bern'), not its promise a second time."""
    cant = cant if cant in CANTONS else ""
    sector = div_name(div) if re.fullmatch(r"\d{2}", div or "") else ""
    div = div if sector else ""
    where = ""
    if cant:
        cname = canton_name_or(cant, cant)
        where = _m("alert_where", name=cname, of=lingue.canton_of(cant, cname, LANG))
    if missed:
        text = ((_m("alert_scope_div", sector=sector) if div else _m("alert_scope_alldiv")) + ", "
                + (_m("alert_scope_k", name=cname, of=lingue.canton_of(cant, cname, LANG)) if cant else _m("alert_scope_ch")))
    elif cant and div:
        text = _m("alert_both", sector=sector, where=where)
    elif cant:
        text = _m("alert_canton", where=where)
    elif div:
        text = _m("alert_sector", sector=sector)
    else:
        text = _m("alert_none")
    href = alert_href(cant, div)
    # a parameter URL per canton and industry is not a page worth crawling; the plain form is
    rel = ' rel="nofollow"' if "?" in href else ""
    lead_p = f'<p class="lead">{e(lead)}</p>' if lead else ""
    # its look in the CSS (.alert): the box sits on 92,000 pages; its button the site's one gold button (fix round 2:
    # 'tag on' was a second style)
    return (f'<div class="glass alert" data-k="{cant}" data-b="{div}"><div class="pad top">{lead_p}'
            f'<p{" class=" + chr(34) + "sc" + chr(34) if missed else ""}>{e(text)}</p><p class="act"><a class="btn{" gh" if ghost else ""}" href="{e(href)}"{rel}>'
            f'{e(_m("alert_link"))}</a>'
            + (f' <a class="tag" href="{ORIGIN}{feed}">{e(_m("feed_link"))}</a>' if feed else "")
            + '</p></div></div>')


def chart_src(csv_path: str = "") -> str:
    """The source line under a chart (step 3a, 14.10.2026; Our World in Data gives one for every chart):
    simap.ch and our own analysis, with the CSV the chart is computed from."""
    link = (f' · <a href="{BASE}{csv_path}" type="text/csv" rel="nofollow">{e(_i.chart_csv)}</a>'
            if csv_path else "")
    return f'<p class="src">{e(_i.chart_src)}{link}</p>'


def co_firms(a: dict, own: str) -> str:
    """'mit AP Automobile Schweiz AG, TOYOTA AG' under an award to several firms on a company page: the
    other firms of the same award. Without it the partners of one framework read as one company listed
    twice (ao-/ap-automobile-schweiz-ag: separate vendors of armasuisse's project 16152)."""
    others = [w for w in winners(a) if slug(w) != own]
    if len(winners(a)) < 2 or not others:
        return ""
    shown = others[:2]
    names = ", ".join(name_cut(w, 40) for w in shown)
    if len(others) > 2:
        names += f" +{formato.count(len(others) - 2)}"
    return _if("with_firms", names=names)


def newest(*groups) -> str:
    """The latest publication date among the given lists of records ('' for none): a page's lastmod."""
    return max(((r.get("publicationDate") or "")[:10] for g in groups for r in g), default="")


# bytes of CSV written, for the build's report line
CSV_BYTES: collections.Counter = collections.Counter()
# CSV for company pages too: 5.1 MB on 14.10.2026, the three kinds together 14.3 MB
CSV_COMPANIES = True
# One file per canton, authority and company, shared by the four languages (14.10.2026): written per
# language they came to 58 MB, a quarter of the room left under GitHub Pages' 1 GB. Column names in
# English, the titles as the publication gives them (the site's rule for every title), so nothing in
# the file depends on the page that links it. path -> (rows, bytes), filled by the first pass.
CSV_COLS = ("Date", "Title", "Contracting authority", "Winners", "Amount", "Currency", "Canton", "CPV",
            "Publication number", "simap link", "Canton source", "Amount note")
# step 3a (14.10.2026): where the Canton comes from (kantone.py) and the amounts under CHF 1'000 that are
# almost certainly unit rates, appended so the earlier columns keep their place
CSV_KSRC = {"ort": "place", "lose": "lot", "auftraggeber": "buyer", "": ""}
CSV_RATE = "probable unit rate"
_CSV_DONE: dict = {}


def _csv_cell(v) -> str:
    """A text cell: whitespace as the page shows it; a leading =, +, - or @ gets an apostrophe so a
    spreadsheet does not run it as a formula ('+Calore SA', 14.10.2026; the about page says so)."""
    t = _ws(str(v or ""))
    return "'" + t if t[:1] in ("=", "+", "-", "@") else t


def _csv_amount(p) -> str:
    if not p:
        return ""
    d = formato._q(p, "0.01")
    return str(int(d)) if d == int(d) else f"{d:.2f}"


def csv_download(rows: list, kind: str, key: str, label: str = "") -> str:
    """The awards of a canton, a contracting authority or a company as a CSV file, and the link to it
    (audit 13.10.2026). /daten/<kind>/<key>.csv, newest first; UTF-8 with BOM and semicolons, which
    Excel opens as columns in Swiss settings; an amount only for an award to one firm, as published,
    with its currency; nothing in it changes unless its awards do (no date)."""
    path = f"/daten/{kind}/{key}.csv"
    if path not in _CSV_DONE:
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=";", lineterminator="\r\n")
        w.writerow(CSV_COLS)
        for a in sorted(rows, key=lambda r: ((r.get("publicationDate") or "")[:10],
                                             str(r.get("publicationNumber") or ""), str(r.get("publicationId") or "")),
                        reverse=True):
            ws = winners(a)
            p = price_of(a) if len(ws) == 1 else None
            w.writerow([(a.get("publicationDate") or "")[:10], _csv_cell(a.get("title")),
                        _csv_cell(a.get("buyerName")), _csv_cell(" | ".join(ws)), _csv_amount(p),
                        cur_of(a) if p else "", a.get("canton") or "", str(a.get("cpvCode") or ""),
                        _csv_cell(a.get("publicationNumber")), a.get("simapUrl") or "",
                        CSV_KSRC.get(a.get("_ksrc", ""), ""), CSV_RATE if is_rate(a) else ""])
        data = ("\ufeff" + buf.getvalue()).encode("utf-8")
        f = OUT / path.lstrip("/")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
        CSV_BYTES[kind] += len(data)
        _CSV_DONE[path] = (len(rows), len(data))
    n, size = _CSV_DONE[path]
    meta = _if("csv_meta", n=formato.count(n), size=formato.size(size))
    # the saved file is named in the reader's language
    save_as = f"{lingue.CSV_STEM[LANG]}-{key.lower()}.csv"
    # nofollow, and /daten/ is closed to crawlers in robots.txt: 4,000 data files are not pages
    # the link says what it downloads (fix round 1): 'Zuschläge Kanton Bern (CSV)', not 'Daten als CSV'
    return (f'<p class="dl"><a href="{BASE}{path}" download="{e(save_as)}" type="text/csv" rel="nofollow" '
            f'data-rows="{n}">{e(label or _i.csv_link)}</a> <span class="sub">({e(meta)})</span></p>')


# The data of the charts that no page's own CSV holds (step 3a, 14.10.2026): one small file each, shared
# by the four languages and linked from the chart's source line; controlla.py checks their headers.
AGG_CSV = {
    "/daten/monate.csv": ("Month", "Awards"),
    "/daten/branchen-monate.csv": ("Division", "Month", "Awards"),
    "/daten/branchen-kantone.csv": ("Division", "Canton", "Awards", "CHF total"),
    "/daten/bereiche-monate.csv": ("CPV", "Month", "Awards"),
    "/daten/offen-kantone.csv": ("Canton", "Open tenders"),
}


def write_agg(path: str, rows) -> None:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", lineterminator="\r\n")
    w.writerow(AGG_CSV[path])
    w.writerows(rows)
    data = ("\ufeff" + buf.getvalue()).encode("utf-8")
    f = OUT / path.lstrip("/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(data)
    CSV_BYTES["grafici"] += len(data)


def write_aggregates(awards: list, opens: list) -> None:
    """The home's monthly chart (every month of the series, zeros included), the Branchen's months and
    cantons, the Bereiche's months and the open tenders per canton (each canton of a tender)."""
    write_agg("/daten/monate.csv", sorted(per_month(awards, until=CUR_MONTH).items()))
    dm = collections.Counter((str(a.get("cpvCode") or "")[:2], (a.get("publicationDate") or "")[:7])
                             for a in awards if str(a.get("cpvCode") or "")[:2] in lingue.CPV_SHORT["de"]
                             and a.get("publicationDate"))
    write_agg("/daten/branchen-monate.csv", [(d, m, k) for (d, m), k in sorted(dm.items())])
    dk = collections.Counter()
    dsum: dict = collections.defaultdict(float)
    for a in awards:
        d = str(a.get("cpvCode") or "")[:2]
        if d in lingue.CPV_SHORT["de"]:
            key = (d, a.get("canton") or "")
            dk[key] += 1
            p = chf_amount(a)
            if p is not None and len(winners(a)) == 1:
                dsum[key] += p
    write_agg("/daten/branchen-kantone.csv",
              [(d, c, k, _csv_amount(dsum.get((d, c)))) for (d, c), k in sorted(dk.items())])
    cm = collections.Counter((str(a["cpvCode"]), (a.get("publicationDate") or "")[:7])
                             for a in awards if a.get("cpvCode") and a.get("publicationDate"))
    write_agg("/daten/bereiche-monate.csv", [(c, m, k) for (c, m), k in sorted(cm.items())])
    oc = collections.Counter(k for t in opens for k in (t.get("_cants") or []))
    write_agg("/daten/offen-kantone.csv", [(c, oc.get(c, 0)) for c in sorted(CANTONS)])


# Company pages named after a natural person (fix round 1): a sole trader's register entry is a person's name
# ('Valérie Rollinet'). Such a page stays readable and is linked as before, but asks to stay out of the search
# engines' index and out of the sitemap. Conservative: no legal-form or business word anywhere, two or three
# words that are all names, at least one of them a first name from the list below.
_LEGAL_FORM = re.compile(
    r"(?i)(?<![\w])(?:ag|gmbh|sa|sàrl|sarl|sagl|kg|kig|gen|genossenschaft|verein|stiftung|fondation|fondazione|"
    r"association|associazione|coop\w*|ltd|llc|inc|plc|sas|srl|spa|snc|se|bv|nv|ab|oy|oü|as|co|cie|holding|"
    r"aktiengesellschaft|gesellschaft|corporation|corp|group|groupe|gruppe|gruppo|partner\w*|consortium|"
    r"konsortium|arge|bietergemeinschaft|ig|eg|gbr|ev|kollektivgesellschaft|einzelfirma)\.?(?![\w])")
_FIRM_WORD = re.compile(
    r"(?i)(?:technik|tech|bau|werk|betrieb|unternehmung|dienst|service|consult|studio|atelier|büro|buero|"
    r"bureau|office|praxis|practice|traduc|traduz|übersetz|uebersetz|transl|schaft|handel|verlag|druck|"
    r"transport|reinigung|garten|garage|elektr|sanit|maler|schrein|holz|metall|ingenieur|architekt|design|"
    r"media|solution|system|energie|energy|immobil|treuhand|logist|consulting|management|gastro|hotel|"
    r"restaurant|café|cafe|shop|store|center|centre|zentrum|schule|école|ecole|scuola|institut|stadt|gemeinde|"
    r"kanton|region|swiss|schweiz|suisse|svizzera|helvet|international|national|electric|nutrex|renotec|"
    r"stromag|cogifer|winterthur)")
_FIRST_NAMES = frozenset("""
adelheid adrian adriana agata agnes alain alessandra alessandro alessia alexander alexandra alfred alice alina
andrea andreas andré andrin angela angelika anita anna anne annette antoine antonio arnaud astrid audrey barbara
beat beatrice beatrix benjamin benoît bernard bernhard bettina bruno camille carla carlo carmen caroline catherine
cécile chantal charlotte christian christiane christina christine christoph christophe claudia claudio claude
concetta corina cornelia damien daniel daniela daniele david denis didier dominik dominique doris edith elena
elisabeth emanuel emma eric erich erika erwin esther eva fabian fabienne fabio federica federico felix florian
francesca francesco franz françoise frédéric gabriel gabriela gabriele georg george gérard gianluca giorgio
giovanni giulia giuseppe gregor guido hans hanspeter heidi heinz helen hélène helena helmut hugo isabel isabelle
jacqueline jacques jakob jan jana janine jean jeanne jérôme johann johanna johannes jonas josef judith julia
julien jürg jürgen karin karl katharina katrin kevin klaus lara laura laurence laurent lea lena leonardo lisa
lorenzo luca lucas lucia luigi lukas luzia manuel manuela marc marcel marco margrit maria marianne marie mario
marion marius markus marta martin martina mathias matteo matthias maurice max michael michel michèle michela
monika nadia nadine natalie nathalie nicolas nicole nina noah olivier oliver pascal pascale patricia patrick
paul paola paolo peter petra philipp philippe pierre pietro raffaele ralph raphael regina regula reto robert
roberto rodolfo roger roland roman rosa ruth sabine sabrina samuel sandra sara sarah sebastian sébastien silvia
simon simone sonja sophie stefan stefanie stefano stephan stéphane susanne sylvie tatjana thomas tobias ueli urs
ursula valentina valérie valerie verena véronique viviana walter werner yann yves yvonne
""".split())
NATURAL: list = []


def natural_person(name: str) -> bool:
    """A company name that is a person's name ('Valérie Rollinet', 'Andreoli Rodolfo'): see _FIRST_NAMES."""
    n = _ws(name)
    if not n or _LEGAL_FORM.search(n) or _FIRM_WORD.search(n) or re.search(r"[\d&/+@()]", n):
        return False
    toks = [t for t in re.split(r"[\s,]+", n) if t]
    if not 2 <= len(toks) <= 3 or any(not re.fullmatch(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*", t) for t in toks):
        return False
    return any(t.casefold() in _FIRST_NAMES or t.split("-")[0].casefold() in _FIRST_NAMES for t in toks)


def company_titles(comp: dict, taken: set = frozenset()) -> dict:
    """slug -> the company page's <title>, unique across the site; `taken`: the buyers' names,
    which their own pages may carry bare."""
    sfx, short = _m("company_title"), _m("company_title_short")

    def cands(name: str) -> list[str]:
        name = _ws(name)
        # the whole name with the short suffix before a cut name with the long one
        # ('AS Aufzüge AG, Zweigniederlassung Wettswil am… – marchés publics'); the bare name
        # and the short suffix only where no authority of that name has a page (Transports
        # publics fribourgeois Trafic is both, and its buyer page may carry either)
        both = name in taken
        out = [(name + x, name) for x in (sfx, short) if len(name + x) <= 64 and not (both and x == short)]
        out += [_ft(name, sfx), _ft(name, sfx, gap1=True), _ft(name, sfx, tail_share=.7, gap1=True)]
        if not both:
            out += [_ft(name, short, gap1=True), _ft(name, short, tail_share=.7, gap1=True)]
            if len(name) <= 64:
                out.append((name, name))
        return rank_titles(out, most=True)
    return pick_unique({s: cands(c["name"]) for s, c in comp.items() if len(c["awards"]) >= MIN_AWARDS})


def build_companies(comp: dict, open_for: dict, sectors: set[str],
                    buyer_slugs: dict, peer_map: dict) -> dict:
    pages = {}
    # one <title> per company page: branches of one firm differ only at the end of the name
    # ('Hälg & Co. AG, Zweigniederlassung Zürich' / '… Basel')
    ctitle = company_titles(comp, {_ws(v[1]) for v in buyer_slugs.values()})
    for s, c in comp.items():
        rows = sorted(c["awards"], key=lambda a: a.get("publicationDate") or "", reverse=True)
        if len(rows) < MIN_AWARDS:
            continue
        name = c["name"]
        years = sorted({(a.get("publicationDate") or "")[:7] for a in rows if a.get("publicationDate")})
        span = formato.period(years[0], years[-1]) if years else ""
        main_code, sector = main_cpv(c) if c["cpv"] else ("", "")
        cants = [k for k, _ in c["cant"].most_common(4)]
        # each authority under one name: its page's, else the spelling the publications use most
        bnames = {k: (buyer_slugs[k][1] if k in buyer_slugs else c["bname"][k].most_common(1)[0][0])
                  for k in c["buyers"]}

        b = [f'<div class="title"><div><p class="eyebrow">'
             # the sector only: a canton here read as the firm's seat ('Swisscom … · Genf'),
             # while it is where most of its awards fall — the rail says so ('Häufigste Kantone')
             + e(short_sector(sector, 44) if sector else _.company)
             + f'</p>{rec_h1(name)}'
             f'<p class="sum">' + e(_m("company_lead", n=zuschlag(len(rows)),
                                       span=(f" ({span})" if span else ""),
                                       b=(_m("buyers_count_one") if len(c["buyers"]) == 1
                                          else _m("buyers_count", k=formato.count(len(c["buyers"]))))))
             + '</p></div><dl class="rail">']
        if sector:
            b.append(f"<dt>{_.main_sector}</dt><dd>{e(sector)}</dd>")
        if main_code:
            b.append(f'<dt>CPV</dt><dd class="mono">{e(main_code)}</dd>')
        if cants:
            # up to four, the most frequent first: "Kantone" over a list cut at four read as all
            b.append(f"<dt>{_.canton if len(c['cant']) == 1 else _.main_cantons}</dt><dd>"
                     + " · ".join(e(canton_name_or(x, x)) for x in cants) + "</dd>")
        b.append("</dl></div>")

        b.append('<div class="figures">')
        b.append(f'<div class="fig"><b>{formato.count(len(rows))}</b><span>{lab_n(len(rows), "awards")}</span></div>')
        if c["value"]:
            b.append(f'<div class="fig money"><b>{formato.tile(c["value"])}</b><span>{_.sum_published}</span>'
                     f'{sum_notes(rows)}</div>')
        else:
            b.append(nosum_tile(rows))
        b.append(f'<a class="fig" href="#auftraggeber"><b>{formato.count(len(c["buyers"]))}</b>'
                 f'<span>{lab_n(len(c["buyers"]), "buyers")}</span></a>')
        if len(c["amounts"]) >= 3:
            b.append(f'<div class="fig" title="{e(_.median_help)}"><b>{formato.tile(median(c["amounts"]))}</b>'
                     f'<span>{_.median}</span></div>')
        b.append("</div>")
        # fix round 3 (item 14): on a long page, the way to its lists (in their order on the page)
        jump = len(rows) >= JUMP_MIN
        if jump:
            jl = [("zuschlaege", _.awards)] + ([("offen", _.running)] if open_for.get(s) else []) + (
                [("bereiche", _.activity if len(c["cpv"]) == 1 else _.activities)] if c["cpv"] else []) + (
                [("auftraggeber", _.buyer if len(c["buyers"]) == 1 else _.buyers)] if c["buyers"] else [])
            b.append('<p class="jl">' + " · ".join(f'<a href="#{i}">{t}</a>' for i, t in jl) + "</p>")
        if CSV_COMPANIES:
            b.append(csv_download(rows, "unternehmen", s, _if("csv_company", name=name_cut(name, 60))))
        b.append(alert_callout(c))

        # Derived analysis (2026-09-07): what simap does not say — per-year rhythm and
        # how concentrated the client base is. Aggregation, not alteration (AGB §5).
        # One money rule for every figure on the page: an amount is credited to the firm
        # only when the award names exactly one firm — the same rule as the headline total,
        # which 595 company pages used to contradict in this table.
        # An award to several firms: this firm's own price (see the award table below); computed first, as the
        # page's one money scale (page_unit, fix round 1) needs the award table's and the yearly table's values
        firm_amt = []
        for a in rows:
            firms = firm_prices(a)
            if len(firms) > 1:
                firm_amt.append(next(((fp, fc) for fw, fp, fc, _n in firms if slug(fw) == s), (None, cur_of(a))))
            else:
                firm_amt.append((price_of(a), cur_of(a)))
        per_year: dict[str, list] = {}
        joint = rates = 0
        for a in rows:
            y = (a.get("publicationDate") or "")[:4]
            if y:
                per_year.setdefault(y, [0, 0.0])
                per_year[y][0] += 1
                p = chf_amount(a)
                if p is not None and len(winners(a)) == 1:
                    per_year[y][1] += p
                elif len(winners(a)) > 1:
                    # every award to several firms, as the tile counts them (fix round 3: Equans said 6 there, 5 here)
                    joint += 1
                elif is_rate(a):
                    rates += 1
        pu = page_unit(unit_of(v for _n, v in per_year.values()),
                       unit_of(p for p, cur in firm_amt if p and cur == "CHF"))
        if per_year:
            yu = pu
            b.append(f'<div class="sec"><div class="runhead"><h2>{e(_p.analysis)}</h2>'
                     f'<span>{e(_p.derived)}</span></div><div class="scroll"><table>{cap(_p.analysis)}<thead><tr>'
                     f'<th>{_.year}</th><th class="r">{_.awards}</th>{money_th("sum_l", yu)}'
                     "</tr></thead><tbody>")
            for y in sorted(per_year, reverse=True):
                n_y, v_y = per_year[y]
                b.append(f'<tr><td class="mono">{e(y)}</td><td class="r num">{formato.count(n_y)}</td>'
                         f'<td class="r num">{formato.column_cell(v_y or None, yu, empty_sr=_.no_own_amount)}</td></tr>')
            b.append("</tbody></table></div>")
            if joint:
                b.append(f'<p class="sub m10">'
                         f'{e(_if("joint_note_one" if joint == 1 else "joint_note", k=formato.count(joint)))}</p>')
            if rates:
                b.append(f'<p class="sub m10">'
                         f'{e(_if("rates_note_one" if rates == 1 else "rates_note", k=formato.count(rates)))}</p>')
            line = ""
            if len(c["buyers"]) == 1:
                line = _m("top_buyer_only", buyer=name_cut(bnames[next(iter(c["buyers"]))], 90))
            elif len(c["buyers"]) > 1:
                # "most frequent" only when there is one: a tie, or a single award, is not a pattern
                (b1, k1), (_b2, k2) = c["buyers"].most_common(2)
                if k1 >= 2 and k1 > k2:
                    line = _m("top_buyer_share", buyer=name_cut(bnames[b1], 90), share=formato.pct(100 * k1 / len(rows)))
            if line:
                b.append(f'<p class="sub m10">{e(line)}</p>')
            b.append("</div>")

        # How large the awards are: counts per amount band, read without a legend. It
        # replaces the bubble timeline (overlapping dots, ISO ends, contrast 1.68:1).
        csv_path = f"/daten/unternehmen/{s}.csv" if CSV_COMPANIES else ""
        if len(rows) >= 5:
            bands = [0] * 6
            for a in rows:
                p = chf_amount(a)
                if p is not None and len(winners(a)) == 1:
                    # banded on the figure the page prints: 999’696 shows as "1 Mio." and so
                    # belongs to "1 bis unter 10 Mio.", not to the band below it
                    q = formato.shown(p)
                    bands[0 if q >= 1e8 else 1 if q >= 1e7 else 2 if q >= 1e6 else 3 if q >= 1e5 else 4] += 1
                else:
                    bands[5] += 1
            if not sum(bands[:5]):
                # five empty bars and nothing to read (all amounts in euros, or none published)
                b.append(f'<figure class="rk" aria-labelledby="chart-sizes"><h2 id="chart-sizes">'
                         f'{e(_if("bands_title", name=name))}</h2><p class="lede">'
                         f'{e(_if("bands_none", n=formato.count(len(rows))))}</p></figure>')
            else:
                band_rows = [(lingue.BANDS[LANG][i], None, bands[i], formato.count(bands[i])) for i in range(6)]
                note = ((_if("bands_median", m=formato.money(median(c["amounts"])))
                         if len(c["amounts"]) >= 3 else "")
                        + (" " + _i.bands_noown if bands[5] else ""))
                b.append(grafici.rank_list(band_rows[:5], other=band_rows[5], fig_id="chart-sizes",
                                           title=_if("bands_title", name=name), lede=_i.bands_lede,
                                           note=note.strip(), src=chart_src(csv_path)))
        # ... and which ones they are: a 331 Mio. total is often one award
        own = sorted(((chf_amount(a), a) for a in rows
                      if chf_amount(a) is not None and len(winners(a)) == 1),
                     key=lambda x: -x[0])
        if len(own) >= 3:
            b.append(f'<div class="sec"><div class="runhead"><h2>{_i.largest_h}</h2></div>'
                     '<ul class="plain">')
            top3 = own[:3]
            heads3 = distinct_titles([de(a, "title") for _p, a in top3], 110)
            tw3 = twin_notes([a for _p, a in top3],
                             [(h, a.get("buyerName"), a.get("publicationDate"), formato.money(p))
                              for (p, a), h in zip(top3, heads3)])
            for i, ((p, a), head) in enumerate(zip(top3, heads3)):
                d = a.get("publicationDate") or ""
                meta = " · ".join(x for x in (e(buyer_label(a)), tt(d, formato.date(d)),
                                              e(tw3.get(i, ""))) if x)
                b.append(f'<li><div class="row"><div><a href="{award_href(a)}"{la(a)}>'
                         f'{e(head)}</a>'
                         f'<span class="sub sb3">{meta}</span></div>'
                         f'<span class="num nw">{formato.money_data(p)}</span></div></li>')
            b.append("</ul>")
            top1 = own[0][0]
            if c["value"] and top1 / c["value"] >= .25:
                share = formato.pct(100 * top1 / c["value"])
                if share.startswith(">"):          # 99.6 % is not "100 %" when other amounts exist
                    share = _if("over_pct", p=share[1:])
                elif LANG == "it":
                    share = ("l’" if share.startswith("8") else "il ") + share
                b.append(f'<p class="sub m10">'
                         f'{e(_if("largest_share", share=share))}</p>')
            b.append("</div>")

        # An award to several firms: this firm's own price, marked as the price of its offer — the
        # column showed the FIRST firm's price under 'an mehrere Unternehmen' (08.10.2026). It
        # stays out of every sum on the page, like before. A price in another currency stands in the
        # title cell, never in the CHF column; a unit rate is flagged (step 3a, 14.10.2026).
        unit = pu
        b.append(f'<div class="sec"{" id=" + chr(34) + "zuschlaege" + chr(34) if jump else ""}><div class="runhead"><h2>{_.awards}</h2>'
                 f'<span>{_.chronological}</span></div><div class="scroll"><table class="ls awc u{unit}">'
                 f'{cap(_if("cap_company_awards", name=name))}<thead><tr>'
                 f'<th class="w96">{_.date}</th><th>{_.contract}</th><th>{_.buyer}</th>'
                 f'<th class="w44">{_.canton_abbr}</th>{money_th("amount", unit)}'
                 "</tr></thead><tbody>")
        heads = distinct_titles([de(a, "title") for a in rows], 130)
        amts = []
        for a, (p, cur) in zip(rows, firm_amt):
            n_f = len(firm_prices(a))
            cell = (not_chf_cell() if p and cur != "CHF"
                    else formato.column_cell(p, unit, cur, empty_sr=_.not_published) + rate_sub(p, cur, a))
            amts.append(cell + (f'<span class="sub sb2">{e(_if("own_offer", n=formato.count(n_f)) if p else _.joint)}</span>'
                                if n_f > 1 else ""))
        twn = twin_notes(rows, [(a.get("publicationDate"), h, a.get("buyerName"), a.get("canton"), amt)
                                for a, h, amt in zip(rows, heads, amts)])
        for i, (a, head, amt, (p, cur)) in enumerate(zip(rows, heads, amts, firm_amt)):
            d = a.get("publicationDate") or ""
            subs = [x for x in (twn.get(i), co_firms(a, s)) if x]
            twin = "".join(f'<span class="sub sb2">{e(x)}</span>' for x in subs) + fx_sub(p, cur)
            b.append(
                f'<tr><td class="mono d">{tt(d, formato.date(d))}</td>'
                f'<td><a href="{award_href(a)}"{la(a)}>{e(head)}</a>{twin}</td>'
                f'<td>{e(buyer_label(a))}</td><td>{abbr_canton(a.get("canton") or "", a.get("_ksrc", ""))}</td>'
                f'<td class="r num">{amt}</td></tr>')
        b.append("</tbody></table></div>" + fb_foot(rows) + "</div>")

        m = open_for.get(s, [])
        if m:
            # was hardcoded German, shipped on 1,938 company pages in each of fr/it/en
            b.append(f'<div class="sec"{" id=" + chr(34) + "offen" + chr(34) if jump else ""}><div class="runhead"><h2>'
                     f'{e(_p.matched_tenders_one if len(m) == 1 else _p.matched_tenders)}'
                     f'</h2><span>{formato.count(len(m))}</span></div>'
                     f'<p class="sub m10">{e(_p.matched_note)}</p>'
                     '<ul class="plain tl mt10">')
            heads = distinct_titles([de(t, "title") for t in m], 120)
            labels = [short_sector(cpv_label(t.get("cpvCode"), de(t, "cpvLabel") or t.get("cpvLabel") or "") or "", 44)
                      for t in m]
            twins = twin_rows(list(zip(heads, labels)))
            for i, (t, head, label) in enumerate(zip(m, heads, labels)):
                dl = t.get("offerDeadline") or ""
                cls, when = due_cell(dl, formato.date(dl), until=True)
                b.append(f'<li data-deadline="{e(dl)}"><div class="row"><div><a href="{BASE}/{LANG}/auftrag/{e(t.get("projectId"))}/"{la(t)}>'
                         f'{e(head)}</a><span class="sub sb3">{e(buyer_label(t))} · {e(multi_mark(t))}{cantons_cell(t)} · '
                         f'{e(label)}{e(project_no(t)) if i in twins else ""}</span></div>'
                         f'<span class="when{cls}">{when}</span>'
                         "</div></li>")
            b.append("</ul>" + fb_foot(m) + "</div>")

        if c["cpv"]:
            # every exact code, the most frequent first (it listed 8 of 21 under 'Tätigkeitsbereiche 21')
            b.append(f'<div class="sec"{" id=" + chr(34) + "bereiche" + chr(34) if jump else ""}><div class="runhead"><h2>'
                     f'{_.activity if len(c["cpv"]) == 1 else _.activities}</h2>'
                     f'<span>{formato.count(len(c["cpv"]))}</span></div><ul class="plain">')
            for (code, label), k in sorted(c["cpv"].items(), key=lambda kv: (-kv[1], kv[0][0])):
                cell = (f'<a href="{BASE}/{LANG}/bereich/{e(code)}/">{e(label)}</a>' if code in sectors
                        else e(label))
                b.append(f'<li><div class="row">{cell}'
                         f'<span class="sub num">{zuschlag(k)}</span></div></li>')
            b.append("</ul></div>")

        if c["buyers"]:
            # every authority (it showed 12 of 71 as pills, by count: SBB Region Ost's CHF 536 Mio. read
            # '2'), the largest CHF sum to this firm first, with the count beside it (step 3a)
            order = sorted(c["buyers"], key=lambda k: (-c["bsum"].get(k, 0), -c["buyers"][k], fold(bnames[k])))
            b.append(f'<div class="sec" id="auftraggeber"><div class="runhead"><h2>'
                     f'{_.buyer if len(c["buyers"]) == 1 else _.buyers}</h2>'
                     f'<span>{e(_.by_amount)}</span></div><ul class="plain">')
            for k in order:
                hit = buyer_slugs.get(k)
                nm = bnames[k]
                cell = (f'<a href="{BASE}/{LANG}/auftraggeber/{e(hit[0])}/">{e(nm)}</a>' if hit else e(nm))
                money = c["bsum"].get(k, 0)
                val = zuschlag(c["buyers"][k]) + (f" · {formato.money(money)}" if money else "")
                b.append(f'<li><div class="row">{cell}<span class="sub num">{e(val)}</span></div></li>')
            b.append("</ul></div>")

        pr = peer_map.get(s)
        if pr:
            others, cant = pr
            b.append(f'<div class="sec"><div class="runhead"><h2>{e(_p.peers)}'
                     f'</h2><span>{e(canton_name_or(cant, cant))}</span></div>'
                     '<ul class="plain">')
            for o in others:
                oc = comp[o]
                b.append(f'<li><div class="row"><a href="{BASE}/{LANG}/unternehmen/{e(o)}/">{e(oc["name"])}</a>'
                         f'<span class="sub num">{zuschlag(len(oc["awards"]))}</span></div></li>')
            b.append("</ul></div>")

        kw = dict(n=zuschlag(len(rows)),
                  val=(_m("company_val_approx" if rounded(c["value"]) else "company_val", v=formato.money(c["value"]))
                       if c["value"] else ""),
                  span=(f" ({span})" if span else ""))
        desc = desc_pick(_m("company_desc", name=name, **kw), _m("company_desc_short", name=name, **kw),
                         _m("company_desc_short", name=name, **{**kw, "span": ""}),
                         _m("company_desc_short", name=name_cut(name, 70), **{**kw, "span": ""}))
        pages[s] = {"name": name, "n": len(rows), "value": c["value"],
                    "cant": cants[0] if cants else "", "sector": sector, "date": newest(rows)}
        # a person's name: readable, linked, but not for the search engines' index (fix round 1)
        person = natural_person(name)
        if person and LANG == "de":
            NATURAL.append(s)
        write(f"/{LANG}/unternehmen/{s}/index.html",
              page(ctitle[s], desc,
                   "\n".join(b), f"/{LANG}/unternehmen/{s}/", _.companies,
                   leaf=fit_title(name, "", tail_share=0), lastmod=newest(rows, m),
                   robots="noindex" if person else ""))
    return pages


# ----------------------------------------------------------------- award page

def _drop_echo(t: str) -> str:
    """t without a bracket that only repeats, translated, the name before it: 'MehrSpur Zürich –
    Winterthur (VoiePlus Zurich - Winterthur), Lots 140 et 141, …'. Kept in a cut, it pushed
    out the lot numbers that tell the French pages apart (verifier 28.09.2026)."""
    for m in re.finditer(r"\s*\(([^()]{3,90})\)", t):
        inner = set(re.findall(r"\w{3,}", fold(m.group(1))))
        before = set(re.findall(r"\w{3,}", fold(t[:m.start()]))[-8:])
        common = inner & before
        if len(common) >= 2 and len(common) * 2 >= len(inner):
            return _ws(t[:m.start()] + t[m.end():])
    return t


def title_cands(t: str, who: str, num: str, sfx: str) -> list[str]:
    """Candidate <title>s for one award or tender page, in order of preference.

    Each is cut inside the publication's title only: a middle cut across the boundary
    between the title and the buyer read 'Fenstersanierung Schulhaus … Abteilung Hochbau'
    (297 German tender titles; verifier 28.09.2026). The winner or buyer is added only when
    it fits whole, and the project number is appended, never cut ('Lose 340 … 3599' read
    as a range of lots). A title that fits the 64 characters only without its suffix is
    shown whole rather than cut ('Gesundheitsinformationssystem für Vollzugseinrichtungen'
    had become 'Gesundheitsinformationssystem… – Zuschlag'), and a cut that leaves one or two
    words comes after every cut that still says something (rank_titles)."""
    t, who = _ws(t), _ws(who)
    room = 64 - len(sfx)
    out = []
    if who and len(t) < 46 and len(t) + 3 + len(who) <= room:
        out.append((f"{t} · {who}{sfx}", t))
    if len(t) <= room:
        out.append((t + sfx, t))
    else:
        if len(t) <= 64:
            out.append((t, t))
        t = _drop_echo(t)
        out += [_ft(t, sfx, tail_share=0), _ft(t, sfx), _ft(t, sfx, tail_share=.7)]
    if who and room - len(who) - 3 >= 24:
        part, core = _ft(t, sfx, limit=64 - len(who) - 3)
        out.append((f"{who} · {part}", core))
    if num:
        # labelled where the title still fits whole with it ('· Nr. 42546'), bare otherwise
        nums = [f" · {_m('title_no', n=num)}{sfx}", f" · {num}{sfx}"]
        fit = [x for x in nums if len(t + x) <= 64]
        out += [(t + x, t) for x in fit[:1]]
        for x in nums:
            if x not in fit:
                out += [_ft(t, x), _ft(t, x, tail_share=0)]
        # without the suffix: the whole title and its number
        out += [(t + x, t) for x in (f" · {_m('title_no', n=num)}", f" · {num}") if len(t + x) <= 64][:1]
    # the last resort before a one-word title: a longer cut without the suffix
    out.append(_ft(t, ""))
    return rank_titles(out)


def paras(text: str) -> str:
    """A publication's text, whole, with its own paragraphs and line breaks. It used to be
    cut at 1,500/1,600 characters in the middle of a word with no ellipsis ('…führt
    westlich, paralle'; 662 German award pages): the longest text is 9 KB, and the source
    is quoted, not trimmed."""
    text = _INVISIBLE.sub("", text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    out = []
    for block in re.split(r"\n\s*\n", text):
        lines = [x.strip() for x in block.split("\n") if x.strip()]
        # fix round 2: a run of lines is a paragraph per sentence (a line that ends one starts a new paragraph, and
        # so does the first line after a list), the lines of a list stay together: «…(5 Jahre).<br>Die Transporte…»
        # read as one wall of text
        paras_, cur = [], []
        for i, x in enumerate(lines):
            if cur and (sent_end(lines[i - 1]) or (_LIST_ITEM.match(lines[i - 1]) and not _LIST_ITEM.match(x))):
                paras_.append(cur)
                cur = []
            cur.append(x)
        if cur:
            paras_.append(cur)
        out.extend("<p>" + "<br>".join(e(x) for x in p) + "</p>" for p in paras_)
    return "".join(out)


# the end of a sentence at the end of a line: . ! ? (and a closing bracket or quote after them), not an abbreviation
# ('z. B.', 'ca.', 'Nr.', 'inkl.', 'Lot A.') nor an item's number ('Phase 1.')
_SENT_END = re.compile(r"[.!?][)»”\"']?$")
_ABBR_END = re.compile(r"(?:\b(?:ca|nr|inkl|bzw|usw|etc|vgl|evtl|ggf|abs|art|ziff|lit|st|fr|mio|mrd|max|min|resp|ev|"
                       r"z\.\s?b|u\.\s?a|d\.\s?h|p\.\s?ex|p\.\s?es|ad\s?es|e\.\s?g|i\.\s?e)|\b\w|\b\d{1,3})\.$", re.I)


def sent_end(line: str) -> bool:
    return bool(_SENT_END.search(line)) and not _ABBR_END.search(line)
# a line that is an item of a list: a bullet, a dash, a number or a letter with its mark
_LIST_ITEM = re.compile(r"^(?:[-–—•·*▪◦●○■□➢►>]|\d{1,2}[.)]|[a-zA-Z][.)]|\(\w{1,2}\))\s")


def award_desc(title: str, buyer: str, tail: str, limit: int = 155) -> str:
    """'Title – Buyer, Zuschlag an X für 1,2 Mio. CHF' made to fit: the title gives way
    first, then the buyer; the winner and the amount are never the part that is cut off
    ('…Hochbauamt Thurgau, Zuschlag an…' dropped the winner on 7,018 German pages)."""
    title, buyer = _ws(title), _ws(buyer)
    for b in (buyer, name_cut(buyer, 60) if len(buyer) > 60 else None,
              name_cut(buyer, 36) if len(buyer) > 36 else None, ""):
        if b is None:
            continue
        rest = (f"\u00a0– {b}" if b else "") + tail
        room = limit - len(rest)
        if room >= 40 or (not b and room >= 24):
            t = title if len(title) <= room else fit_title(_drop_echo(title), "", room)
            return t + rest
    return fit_desc(f"{title}\u00a0– {buyer}{tail}", limit)


def rec_src(rec: dict) -> dict:
    """The publication a project's page is headed by: the tender (open, or past its deadline
    with rec['expired']), else its first award."""
    rows = rec.get("awards") or []
    return rec.get("tender") or (rows[0] if rows else {})


def rec_title(rec: dict) -> str:
    """The page's title: the tender's, the award's own, or the project's for several awards."""
    rows = rec.get("awards") or []
    if rec.get("tender") or len(rows) == 1:
        return de(rec_src(rec), "title")
    return project_title(rows)


def award_titles(by_project: dict) -> dict:
    """projectId -> the page's <title>, unique across the site (see build_awards)."""
    heads: dict[str, list] = {}
    for pid, rec in by_project.items():
        if not pid:
            continue
        t = rec_title(rec)
        if not t:
            continue
        src = rec_src(rec)
        rows = rec.get("awards") or []
        ws = winners(rows[0]) if len(rows) == 1 else []
        # a winner only when there is exactly one: 'B + S AG · Rahmenvertrag …' named one of
        # five winners as if it were the only one (verifier 28.09.2026); the page of a
        # project's lots names its buyer
        who = ws[0] if len(ws) == 1 else (src.get("buyerName") or "")
        sfx = _m("tender_suffix") if "tender" in rec else _m("award_suffix")
        num = src.get("projectNumber") or src.get("publicationNumber") or pid[:8]
        heads[pid] = title_cands(t, who, str(num), sfx)
    return pick_unique(heads)


def award_desc_parts(rec: dict) -> tuple[str, str, str]:
    """(title, buyer, closing clause) of an award or tender page's meta description."""
    src = rec_src(rec)
    rows = rec.get("awards") or []
    tail = ""
    if "tender" in rec and src.get("offerDeadline"):
        tail = _m("desc_deadline_passed" if rec.get("expired") else "desc_deadline",
                  date=formato.date(src["offerDeadline"]))
    elif len(rows) > 1:
        # the lots of a project: how many, never a sum of them — none was published
        tail = (_m("desc_lots", n=formato.count(len(rows))) if any(a.get("_lot") is not None for a in rows)
                else _m("desc_awards_n", n=formato.count(len(rows))))
    elif rows:
        aw = rows[0]
        ws, price = winners(aw), price_of(aw)
        # one money rule: an amount only for an award to one firm. Several firms have a price
        # each and the award none: ', Zuschlag über 313’744 CHF' gave the first firm's price as
        # the whole award's (08.10.2026)
        if len(ws) == 1:
            # no unit rate in a description, and 'rund' where the figure is rounded (fix round 1)
            tail = _m("desc_won", who=ws[0]) + (
                _m("desc_amount_approx" if rounded(price) else "desc_amount", amount=formato.money(price, cur_of(aw)))
                if price and not is_rate(aw) else "")
        elif ws:
            tail = _m("desc_won_n", n=formato.count(len(ws)))
    return rec_title(rec), (src.get("buyerName") or "").strip(), tail


def award_descs(by_project: dict) -> dict:
    """projectId -> meta description. Pages whose simap titles are identical ('SGS Erweiterung
    Schulanlage Gutenbrunnen Schübelbach', projects 42676 and 42684) shared one description
    although their <title>s differ: those get the project number (verifier, 28.09.2026)."""
    parts = {pid: award_desc_parts(rec) for pid, rec in by_project.items()
             if pid and rec_title(rec)}
    out = {pid: award_desc(*p, limit=154) for pid, p in parts.items()}
    seen = collections.Counter(out.values())
    for pid, (t, b, tail) in parts.items():
        if seen[out[pid]] > 1:
            src = rec_src(by_project[pid])
            num = src.get("projectNumber") or src.get("publicationNumber")
            if num:
                out[pid] = award_desc(t, b, tail + " · " + _if("project_no", n=num), limit=154)
    return {pid: d if d.endswith((".", "!", "?", "…")) else d + "." for pid, d in out.items()}


def firm_link(name: str, pages: dict) -> str:
    s = slug(name)
    return (f'<a href="{BASE}/{LANG}/unternehmen/{e(s)}/">{e(name)}</a>' if s in pages else e(name))


def note_html(note: str) -> str:
    return "<br>".join(e(x.strip()) for x in note.split("\n") if x.strip())


def firm_notes(firms: list) -> tuple[list[str], str]:
    """(each firm's short note, or the one note every firm carries): 'Hinweis: Die publizierte
    Summe versteht sich als Kostendach … für alle Zuschlagsempfänger' once, not under each name."""
    notes = [short_note(n) for _w, _p, _c, n in firms]
    if len(firms) > 1 and notes[0] and len(set(notes)) == 1:
        return [""] * len(firms), notes[0]
    return notes, ""


def price_notes(firms: list, block: bool = False) -> str:
    """The notes under the firms of an award to several: the same price beside every name is said
    so (a framework ceiling repeated per firm reads like each firm's own otherwise), and a note
    every firm carries is given once. block=True: as blocks of their own, under the firms' cards."""
    out = []
    prices = {(p, c) for _w, p, c, _n in firms}
    if len(firms) > 1 and len(prices) == 1 and next(iter(prices))[0]:
        out.append(e(_i.same_price_two if len(firms) == 2 else _if("same_price", n=formato.count(len(firms)))))
    _each, shared = firm_notes(firms)
    attrs = [""] * len(out)
    if shared:
        out.append(note_html(shared))
        attrs.append(text_la(shared))
    if block:
        return "".join(f'<div class="sub mt10"{a}>{x}</div>' for x, a in zip(out, attrs))
    return "".join(f'<span class="sub sb6"{a}>{x}</span>' for x, a in zip(out, attrs))


STYLE_GAP = ' class="mt4"'


def lot_table(rows: list, pages: dict, h1: str) -> str:
    """The awards of one project, a line each: the lot, who won it and for how much — the amount of
    an award to one firm, else each firm's own price beside its name and no figure for the lot.
    Each line is the anchor a company or buyer row links to (#lot-2). The page used to show one
    of them, the last one read: lot 15 of 6965, lot 2 of 28439 (08.10.2026)."""
    has_lots = any(a.get("_lot") is not None for a in rows)
    days = {(a.get("publicationDate") or "")[:10] for a in rows}
    # the official record: each amount exactly as published, in francs, the unit in the header
    out = [f'<div class="sec"><div class="runhead"><h2 id="h-lots">{_.lots if has_lots else _.awards}</h2>'
           f'<span>{formato.count(len(rows))}</span></div><div class="scroll"><table class="ls lots uchf" aria-labelledby="h-lots">'
           f'<thead><tr>'
           + (f'<th class="w52">{_.lot}</th><th>{_.lot_name}</th>' if has_lots
              else f'<th class="w96">{_.date}</th>')
           + f'<th>{_.winner}</th>{money_th("amount", "chf")}</tr></thead><tbody>']
    for a in rows:
        d = (a.get("publicationDate") or "")[:10]
        sub = [e(a.get("publicationNumber") or "")]
        if has_lots and len(days) > 1 and d:
            sub.append(tt(d, formato.date(d)))
        try:
            ns = int((a.get("award") or {}).get("numberOfSubmissions"))
        except (TypeError, ValueError):
            ns = 0
        if ns > 0:
            sub.append(f"{formato.count(ns)} {_.offers_one if ns == 1 else _.offers}")
        subline = ('<span class="sub sb2">'
                   + " · ".join(x for x in sub if x) + "</span>")
        if has_lots:
            name = lot_name(a)
            if _lot_key(name) == _lot_key(h1):
                name = ""          # a lot that only repeats the project's name
            n = a.get("_lot")
            # a lot named in the title is in the title's language
            nl = ((la(a) if _lot_tail(a, de(a, "title"))[1] is not None else text_la(name)) if name else "")
            first = (f'<td class="mono">{e(n) if n is not None else "–"}</td>'
                     f'<td>{f"<span{nl}>{e(name)}</span>" if nl else e(name)}{subline}</td>')
        else:
            first = f'<td class="mono d">{tt(d, formato.date(d))}{subline}</td>'
        firms = firm_prices(a)
        if len(firms) > 1:
            each, _shared = firm_notes(firms)
            priced = any(p for _w, p, _c, _n in firms)
            # no price beside any name (4377: ten firms per lot): the names alone
            who = "".join(
                f'<div{STYLE_GAP if i else ""}>{firm_link(w, pages)}'
                + (f' <span class="sub num nw">'
                   f'{formato.exact(p, c) if p else e(_.not_published)}</span>' if priced else "")
                + (f' <span class="sub">· {e(_.rate_flag)}</span>' if rate_price(p, c, a) else "")
                + (f'<span class="sub sb0"{text_la(nt)}>{note_html(nt)}</span>' if nt else "")
                + "</div>" for i, ((w, p, c, _n), nt) in enumerate(zip(firms, each))) + price_notes(firms)
            amt = (f'–<span class="sub sb2">{e(_.per_firm)}</span>'
                   if priced else formato.cell(None, empty_sr=_.not_published))
        else:
            # the amount as published, in the CHF column only when it is in francs (a foreign one
            # stands under the firm with its currency); a unit rate is flagged (step 3a)
            p, cur = price_of(a), cur_of(a)
            who = (firm_link(firms[0][0], pages) if firms else "–") + fx_sub(p, cur, exact=True)
            amt = (not_chf_cell() if p and cur != "CHF"
                   else formato.exact_cell(p, cur, empty_sr=_.not_published) + rate_sub(p, cur, a))
        out.append(f'<tr id="{e(a.get("_anchor") or "")}">{first}<td>{who}</td>'
                   f'<td class="r num">{amt}</td></tr>')
    out.append("</tbody></table></div></div>")
    return "\n".join(out)


# a break opportunity after a slash or an ampersand inside a word ('Mettmenstetten/Fabrication&livraison')
_WBR = re.compile(r"(?<=\S)(/|&amp;)(?=\S)")
LONG_TITLE = 110


def rec_h1(text: str, attr: str = "") -> str:
    """The H1 of a record, a company or an authority, as published (fix round 2): over LONG_TITLE characters a size
    smaller (.lt), and a <wbr> after '/' and '&' inside a word, so the browser breaks there or at a hyphen
    (hyphens:auto), never in the middle of a word ('Fabrication&li|vraison' at 390 px)."""
    t = _WBR.sub(r"\1<wbr>", e(text))
    return f'<h1 class="rec{" lt" if len(text or "") > LONG_TITLE else ""}"{attr}>{t}</h1>'


def lang_div(html_: str, attr: str) -> str:
    """A block of publication text in another language than the page: wrapped, lang= on it."""
    return f"<div{attr}>{html_}</div>" if attr and html_ else html_


def grouped_texts(rows: list, texts: list, field: str = "") -> str:
    """One text field of a project's awards: once when every lot has the same, else each text under
    the lots it belongs to ('Lose 2, 3'); the reason given for lot 2 is not lot 15's. field: the
    publication field the texts come from (their language marked, 14.10.2026)."""
    groups: dict = {}
    for a, t in zip(rows, texts):
        t = (t or "").strip()
        if t:
            groups.setdefault(_ws(t), (t, []))[1].append(a)
    if not groups:
        return ""
    if len(groups) == 1 and len(next(iter(groups.values()))[1]) == len(rows):
        t, members = next(iter(groups.values()))
        return lang_div(paras(t), la(members[0], field) if field else text_la(t))
    out = []
    for t, members in groups.values():
        nums = [a["_lot"] for a in members if a.get("_lot") is not None]
        if len(nums) == len(members):
            label = (_if("lot_n", n=nums[0]) if len(nums) == 1
                     else _if("lots_list", n=", ".join(str(x) for x in nums)))
        else:
            label = ", ".join(_if("publication_no", n=a.get("publicationNumber") or "") for a in members)
        out.append(f'<p class="p4"><strong>{e(label)}</strong></p>'
                   + lang_div(paras(t), la(members[0], field) if field else text_la(t)))
    return "".join(out)


_SIMAP_PD = re.compile(r"https://www\.simap\.ch/[a-z]{2}/project-detail/")


def simap_href(t: dict) -> str:
    """The publication on simap.ch in the page's language (fix round 1: every link opened the German one): simap's
    project page, https://www.simap.ch/{lang}/project-detail/{id}, the address the simap actor writes."""
    u = str(t.get("simapUrl") or "")
    pid = str(t.get("projectId") or "")
    return f"https://www.simap.ch/{LANG}/project-detail/{pid}" if pid and _SIMAP_PD.match(u) else u


def _ics_text(v: str) -> str:
    return v.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _ics_fold(line: str) -> str:
    """RFC 5545 lines of at most 75 octets, continued on a line that starts with a space; never
    inside a UTF-8 character."""
    out, cur, size = [], "", 0
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > 75:
            out.append(cur)
            cur, size = " ", 1
        cur += ch
        size += n
    out.append(cur)
    return "\r\n".join(out)


def ics_file(t: dict) -> str:
    """The deadline of an open tender as a calendar event (audit 13.10.2026, 'scadenza da aggiungere
    al calendario'). At the published time, in UTC; a deadline without a time (or at 00:00, which
    the page shows as the date alone) as an all-day event on that date. A reminder the day before.
    Nothing in it changes unless the tender does: the stamp is its publication day, the sequence
    its correction number, so the file stays the same from one night to the next."""
    raw = str(t.get("offerDeadline") or "")
    pid = t.get("projectId")
    url = f"{ORIGIN}/{LANG}/auftrag/{pid}/"
    num = str(t.get("publicationNumber") or "")
    suf = num.rsplit("-", 1)[-1] if "-" in num else ""
    seq = max(0, int(suf) - 1) if suf.isdigit() else 0
    stamp = (t.get("publicationDate") or DATA_DATE)[:10].replace("-", "") + "T000000Z"
    summary = _if("ics_summary", title=_ws(de(t, "title")))
    colon = lingue.COLON[LANG]
    desc = [x for x in (
        f"{_.buyer}{colon} {_ws(t.get('buyerName'))}" if t.get("buyerName") else "",
        f"{_.deadline}{colon} {formato.deadline(raw)}",
        f"{_i.ics_page}{colon} {url}",
        f"{_i.ics_official}{colon} {simap_href(t)}" if t.get("simapUrl") else "") if x]
    if len(raw) <= 10 or raw[11:16] == "00:00":
        day = date.fromisoformat(raw[:10])
        when = [f"DTSTART;VALUE=DATE:{day:%Y%m%d}", f"DTEND;VALUE=DATE:{day + timedelta(days=1):%Y%m%d}"]
        trigger = "-PT15H"          # 09:00 the day before
    else:
        when = [f"DTSTART:{deadline_at(t).astimezone(timezone.utc):%Y%m%dT%H%M%SZ}"]
        trigger = "-P1D"
    lines = (["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//auftragsregister.ch//{LANG.upper()}",
              "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "BEGIN:VEVENT",
              f"UID:{pid}-frist@auftragsregister.ch", f"DTSTAMP:{stamp}", f"SEQUENCE:{seq}"] + when
             + ["SUMMARY:" + _ics_text(summary), "DESCRIPTION:" + _ics_text("\n".join(desc)), "URL:" + url]
             + (["LOCATION:" + _ics_text(_ws(t.get("city")))] if t.get("city") else [])
             + ["TRANSP:TRANSPARENT", "BEGIN:VALARM", "ACTION:DISPLAY",
                "DESCRIPTION:" + _ics_text(summary), f"TRIGGER:{trigger}", "END:VALARM",
                "END:VEVENT", "END:VCALENDAR"])
    return "\r\n".join(_ics_fold(x) for x in lines) + "\r\n"


def award_mini_table(rows: list, pages: dict, caption: str, with_buyer: bool, unit: str = "") -> str:
    """A few awards in a table: date, title (and the authority when it is not the page's own), who
    won, the amount by the site's rule (award_cell: one firm's amount, none for several). unit: the
    page's scale (page_unit)."""
    heads = distinct_titles([de(a, "title") for a in rows], 100)
    unit = unit or award_unit(rows)
    amts = [award_cell(a, unit) for a in rows]
    twn = twin_notes(rows, [(a.get("publicationDate"), h, a.get("buyerName") if with_buyer else "",
                             tuple(winners(a)), amt) for a, h, amt in zip(rows, heads, amts)])
    out = [f'<div class="scroll"><table class="ls awb u{unit}">{cap(caption)}<thead><tr><th class="w96">{_.date}</th>'
           f'<th>{_.contract}</th><th>{_.winner}</th>{money_th("amount", unit)}</tr></thead><tbody>']
    for i, (a, head, amt) in enumerate(zip(rows, heads, amts)):
        d = a.get("publicationDate") or ""
        who = " · ".join(firm_link(w, pages) for w in winners(a)) or "–"
        subs = [e(buyer_label(a))] if with_buyer and buyer_label(a) else []
        if twn.get(i):
            subs.append(e(twn[i]))
        sub = (f'<span class="sub sb2">{" · ".join(subs)}</span>'
               if subs else "") + award_fx(a)
        out.append(f'<tr><td class="mono d">{tt(d, formato.date(d))}</td>'
                   f'<td><a href="{award_href(a)}"{la(a)}>{e(head)}</a>{sub}</td><td>{who}</td>'
                   f'<td class="r num">{amt}</td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


def one_per_project(rows: list, k: int) -> list:
    """The first k rows, one per project: five lots of one project are one line of history."""
    out, seen = [], set()
    for a in rows:
        key = a.get("projectId") or id(a)
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
        if len(out) == k:
            break
    return out


def bid_context(t: dict, ctx: dict, pages: dict, buyer_slugs: dict, skip: set, history: bool = True) -> str:
    """What a bidder wants to know beside the tender (audit 13.10.2026, Pacchetto 2 #14): what else
    the authority has open, whom it awarded its last contracts to and for how much, and who won
    similar work in the same canton. skip: the tender itself and the lots listed beside it."""
    out = []
    key = norm_buyer(t.get("buyerName") or "")
    hit = buyer_slugs.get(key)
    now = [x for x in ctx["open_by_buyer"].get(key, []) if x.get("projectId") not in skip]
    if now:
        more = (f'<p class="dl"><a href="{BASE}/{LANG}/auftraggeber/{e(hit[0])}/#offen">'
                f'{e(_if("buyer_open_all", n=formato.count(len(ctx["open_by_buyer"].get(key, [])))))}</a></p>'
                if hit and len(now) > 8 else "")
        out.append(f'<div class="sec"><div class="runhead"><h2>{e(_i.tender_buyer_open_h)}</h2>'
                   f'<span>{formato.count(len(now))}</span></div>{open_items(now, 8)}{more}</div>')
    if not history:
        return "".join(out)
    past_all = ctx["awards_by_buyer"].get(key, [])
    past = one_per_project(past_all, 5)
    sim = []
    div, cant = str(t.get("cpvCode") or "")[:2], t.get("canton") or ""
    if div.isdigit() and cant in CANTONS and div_name(div):
        shown = {id(a) for a in past}
        ts = sig(t.get("cpvCode"))

        def close(a) -> int:
            s2, k = a["_sig"], 0
            while k < min(len(s2), len(ts)) and s2[k] == ts[k]:
                k += 1
            return k
        cands = [a for a in ctx["awards_by_dc"].get((div, cant), []) if id(a) not in shown
                 and a.get("_bk") != key]
        # the closest CPV codes first, the newest among equals (the list is newest first and the sort
        # stable), one per project, and shown in that order — as the about page and the note above the
        # list say. They used to be re-sorted newest first: a cleaning tender listed four snow-clearing
        # awards before the only cleaning award (audit 14.10.2026)
        sim = one_per_project(sorted(cands, key=lambda a: -close(a)), 5)
    # the two tables in one scale (fix round 1)
    pu = page_unit(*(unit_of(price_of(a) for a in x if len(firm_prices(a)) == 1 and cur_of(a) == "CHF")
                     for x in (past, sim)))
    if past:
        more = (f'<p class="dl"><a href="{BASE}/{LANG}/auftraggeber/{e(hit[0])}/">'
                f'{e(_if("tender_buyer_awards_all", n=zuschlag(len(past_all))))}</a></p>' if hit else "")
        out.append(f'<div class="sec"><div class="runhead"><h2>{e(_i.tender_buyer_awards_h)}</h2>'
                   f'<span>{formato.count(len(past_all))}</span></div>'
                   + award_mini_table(past, pages, _i.tender_buyer_awards_h, False, pu) + more + "</div>")
    if sim:
        name = canton_name_or(cant, cant)
        out.append(f'<div class="sec"><div class="runhead"><h2>{e(_i.similar_h)}</h2></div>'
                   f'<p class="sub m106">'
                   f'{e(_if("similar_note", sector=div_name(div), name=name, of=cant_of(cant, name)))}</p>'
                   + award_mini_table(sim, pages, _i.similar_h, True, pu) + "</div>")
    return "".join(out)


def canton_detail(t: dict | None, rows: list) -> str:
    """The 'Kanton' line of a record page: every canton the record counts in (a tender's, else its
    awards'), and, when the publication names no place, that it is the buyer's seat (step 3a)."""
    if t is not None:
        ks, src = list(t.get("_cants") or []), t.get("_ksrc", "")
    else:
        cnt = collections.Counter(a.get("canton") for a in rows if a.get("canton"))
        ks = [k for k, _n in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))]
        srcs = {a.get("_ksrc", "") for a in rows if a.get("canton")}
        src = srcs.pop() if len(srcs) == 1 else ""
    if not ks:
        return ""
    notes = [_.multi_cantons] if len(ks) > 1 else []
    if src == "auftraggeber":
        notes.append(_.fb_note)
    return (e(", ".join(canton_name_or(k, k) for k in ks))
            + "".join(f'<span class="sub sb2">{e(x)}</span>' for x in notes))


def build_awards(awards: list, opens: list, expired: list, pages: dict, sectors: set[str],
                 buyer_slugs: dict, lot_sib: dict | None = None, ctx: dict | None = None,
                 award_cants: set = frozenset()) -> int:
    ctx = ctx or {"open_by_buyer": {}, "awards_by_buyer": {}, "awards_by_dc": {}}
    # every award of a project on its page, the lots in order: keyed by project, the last award
    # read used to overwrite the others (08.10.2026)
    by_project = {pid: {"awards": rows} for pid, rows in project_awards(awards).items()}
    for t in opens:
        by_project.setdefault(t.get("projectId"), {})["tender"] = t
    # a tender past its deadline keeps its page, marked as such (load() leaves out the projects
    # with an award: their award page holds the address)
    for t in expired:
        if t.get("projectId") not in by_project:
            by_project[t["projectId"]] = {"tender": t, "expired": True}
    # A first pass over the titles, because uniqueness is not a property any single
    # page can see. Truncation alone got the duplicates from 3,036 pages down to 712,
    # and the rest genuinely share a title — twelve awards read only "BKP 211
    # Baumeisterarbeiten". Knowing which ones collide is what lets the distinguisher
    # be added only where it earns its space.
    # The collision test runs on the FINAL titles, suffix included: testing a longer
    # suffix-free cut missed 243 pages that the real, shorter cut made identical. Up to three
    # rounds: the title as is (with the winner when it is short), then the winner in front,
    # then the project number at the end, where the middle cut keeps it.
    final_title = award_titles(by_project)
    final_desc = award_descs(by_project)

    n = 0
    for pid, rec in by_project.items():
        if not pid:
            continue
        rows = rec.get("awards") or []
        src = rec_src(rec)
        title = rec_title(rec)
        if not title:
            continue
        is_tender = "tender" in rec        # a tender's page: open, or past its deadline
        gone = bool(rec.get("expired"))
        dl = (src.get("offerDeadline") or "") if is_tender else ""
        # fix round 3 (item 31): open, and its deadline within NEAR_DAYS of the build
        dl_at = deadline_at(src) if dl and not gone else None
        near = bool(dl_at) and (dl_at - NOW).total_seconds() < NEAR_DAYS * 86400
        # one award: its own record, as before; several (a project's lots): a line each
        aw = rows[0] if len(rows) == 1 else None
        many = len(rows) > 1
        award = (aw or {}).get("award") or {}

        # the status: open, past its deadline, or awarded. 'Läuft heute ab, 16.00 Uhr' and a deadline
        # passed since the build are the script's (stand.js, from the reader's clock; step 3b)
        state = (f'<span class="state off"><i></i>{_.tender_expired}</span>' if gone
                 else f'<span class="state"><i></i>{_.tender_open if is_tender else _.award_granted}</span>')
        # the title's language: the tender's or the award's own, the first lot's for a project
        tl = la(src) if (is_tender or len(rows) == 1) else (la(rows[0]) if rows else "")
        cant = src.get("canton") if src.get("canton") in CANTONS else ""
        div = str(src.get("cpvCode") or "")[:2]
        b = [f'<div class="title"><div>{state}'
             + rec_h1(title, tl)
             + (f'<p class="sum">{e(_m("expired_lead", when=formato.deadline(dl)))}</p>' if gone and dl else "")
             + (f'<p class="sum xl">{e(_m("expired_lead", when=formato.deadline(dl)))}</p>' if near else "")
             + '</div><dl class="rail">']
        if many and not is_tender:
            # several publications: the project's number, and the day or the span they came out
            if src.get("projectNumber"):
                b.append(f'<dt>{_.project_number}</dt><dd class="mono">{e(src["projectNumber"])}</dd>')
            days = sorted({(a.get("publicationDate") or "")[:10] for a in rows} - {""})
            if len(days) == 1:
                b.append(f'<dt>{_.published_on}</dt><dd>{tt(days[0], formato.date(days[0]))}</dd>')
            elif days:
                b.append(f'<dt>{_.period}</dt><dd>{tt(days[0], formato.date(days[0]))}\u00a0– '
                         f'{tt(days[-1], formato.date(days[-1]))}</dd>')
        else:
            if src.get("publicationNumber"):
                b.append(f'<dt>{_.publication}</dt><dd class="mono">{e(src["publicationNumber"])}</dd>')
            if src.get("publicationDate"):
                pd = src["publicationDate"]
                b.append(f'<dt>{_.published_on}</dt><dd>{tt(pd, formato.date(pd))}</dd>')
        if aw and aw.get("_lot") is not None and not is_tender:
            b.append(f'<dt>{_.lot}</dt><dd class="mono">{e(aw["_lot"])}</dd>')
        if src.get("processType"):
            b.append(f"<dt>{_.procedure}</dt><dd>{e(_e('processType', src['processType']))}</dd>")
        b.append("</dl></div>")

        figs = []
        if dl:
            figs.append(f'<div class="fig wide{" off" if gone else ""}" data-deadline="{e(dl)}"><b>{tt(dl, formato.deadline(dl))}</b>'
                        f"<span>{_.deadline}</span>" + ('<em class="rel"></em>' if near else "") + "</div>")
        ws = winners(aw) if aw else []
        firms = firm_prices(aw) if aw else []
        # The award page is the official record: the amount exactly as published, Rappen
        # included, with a rounded reading under it from one million up. Only for an award to
        # one firm: several firms have a price each, shown beside their names, and the award
        # has none (08.10.2026)
        price = price_of(aw) if aw and len(ws) == 1 else None
        if price:
            cur = cur_of(aw)
            # a unit rate: shown as published, left out of every sum, the figure muted and a chip beside it (fix
            # round 2: a full-gold '130 CHF' over a footnote)
            rate = price < 999_500 and rate_price(price, cur, aw)
            approx = (f'<em class="approx">{e(_.approx.format(v=formato.money(price, cur)))}</em>'
                      if price >= 999_500 else f'<em class="approx">{e(_.rate_flag)}</em>' if rate else "")
            figs.append(f'<div class="fig wide{" rate" if rate else ""}"><b>{formato.exact_tile(price, cur)}</b>'
                        f"<span>{_.award_amount}</span>{approx}</div>")
        if award.get("numberOfSubmissions"):
            ns = award["numberOfSubmissions"]
            try:
                one = int(ns) == 1
                shown = formato.count(int(ns))
            except (TypeError, ValueError):
                one, shown = False, e(ns)
            figs.append(f'<div class="fig"><b>{shown}</b>'
                        f"<span>{_.offers_one if one else _.offers}</span></div>")
        if many:
            k = len(rows)
            lots = any(a.get("_lot") is not None for a in rows)
            figs.append(f'<div class="fig"><b>{formato.count(k)}</b>'
                        f'<span>{_.lots if lots else lab_n(k, "awards")}</span></div>')
            nf = len({slug(w) for a in rows for w in winners(a)})
            if nf:
                figs.append(f'<div class="fig"><b>{formato.count(nf)}</b>'
                            f'<span>{lab_n(nf, "companies")}</span></div>')
        if figs:
            b.append('<div class="figures">' + "".join(figs) + "</div>")
        # The publication on simap.ch is the primary action, above any long description (it sat at
        # 11'241 px on a phone under one award's 15 lots); the calendar file and the way back to the
        # canton's open tenders are secondary; 'Fehler melden' opens an e-mail with the publication
        # number in its subject (step 3a, 14.10.2026)
        acts = []
        if src.get("simapUrl"):
            acts.append(f'<a class="btn" href="{e(simap_href(src))}">{e(_.simap_btn)}</a>')
        if is_tender and not gone:
            acts.append(f'<a class="tag" href="{BASE}/{LANG}/auftrag/{e(pid)}/frist.ics" type="text/calendar" rel="nofollow">'
                        f'{e(_i.ics_link)}</a>')
        if is_tender and cant:
            cn = canton_name_or(cant, cant)
            acts.append(f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/{cant}/">'
                        f'<span aria-hidden="true">← </span>{e(_if("back_canton", name=cn, of=cant_of(cant, cn)))}</a>')
        ref = (src.get("projectNumber") if many and not is_tender else src.get("publicationNumber")) or pid[:8]
        acts.append(f'<a class="rep" href="mailto:{ABO_MAIL}?subject={urllib.parse.quote(f"{_.report_subj} {ref}")}">'
                    f'{e(_.report_error)}</a>')
        b.append('<div class="acts">' + "".join(acts) + "</div>")
        if is_tender and gone:
            b.append(alert_box(cant, div, lead=_m("alert_missed"), missed=True, ghost=bool(src.get("simapUrl"))))
        if many:
            b.append(lot_table(rows, pages, title))

        b.append('<div class="cols"><div class="prose">')
        if not ws and aw and aw.get("_win_nn"):
            b.append(f'<div class="runhead"><h2>{_.award_to}</h2></div>'
                     f'<div class="winner"><span class="who">{e(_.noname)}</span></div>')
        if ws:
            b.append(f'<div class="runhead"><h2>{_.award_to}</h2>'
                     + (f'<span>{e(_if("joint_n", n=formato.count(len(ws))))}</span>' if len(ws) > 1 else "")
                     + "</div>")
            each, _shared = firm_notes(firms)
            for (w, p, cur, _note), nt in zip(firms, each):
                s = slug(w)
                known = pages.get(s)
                link = (f'<a href="{BASE}/{LANG}/unternehmen/{e(s)}/" class="who">{e(w)}</a>'
                        if known else f'<span class="who">{e(w)}</span>')
                extra = []
                if len(firms) > 1 and any(fp for _w, fp, _c, _n in firms):
                    # the firm's own price, as the publication gives it beside its name
                    extra.append(f'{e(_.offer_price)}{lingue.COLON[LANG]} '
                                 + (e(formato.exact(p, cur)) if p else e(_.not_published))
                                 + (f" ({e(_.rate_flag)})" if rate_price(p, cur, aw) else ""))
                if known:
                    extra.append(f'{zuschlag(known["n"])} {_.in_register}')
                b.append(f'<div class="winner">{link}'
                         + (f'<div class="sub mt5">' + " · ".join(extra)
                            + "</div>" if extra else "")
                         + (f'<div class="sub mt3"{text_la(nt)}>{note_html(nt)}</div>' if nt else "")
                         + "</div>")
            if len(firms) > 1:
                b.append(price_notes(firms, block=True))
        if many:
            just = grouped_texts(rows, [(a.get("award") or {}).get("justification") for a in rows])
            body = grouped_texts(rows, [de(a, "description") for a in rows], "description")
            if just:
                b.append(f'<h2 class="pr34">{_.reason}</h2>' + just)
            if body:
                b.append(f'<h2 class="pr30">{_.description}</h2>' + body)
        else:
            if award.get("justification"):
                b.append(f'<h2 class="pr34">{_.reason}</h2>'
                         + lang_div(paras(award["justification"]), text_la(award["justification"])))
            body_txt = de(src, "description")
            if body_txt:
                b.append(f'<h2 class="pr30">{_.description}</h2>'
                         + lang_div(paras(body_txt), la(src, "description")))
        sib = (lot_sib or {}).get(pid) if is_tender else None
        if sib:
            # the home shows these lots as one line ('… · 6 Lose') linking here
            b.append(f'<h2 id="lose" style="margin:30px 0 8px">{e(_i.other_lots)}</h2><ul class="plain tl">')
            for x, head in zip(sib, distinct_titles([de(x, "title") for x in sib], 100)):
                xd = x.get("offerDeadline") or ""
                cls, when = due_cell(xd, formato.date(xd), until=True)
                b.append(f'<li data-deadline="{e(xd)}"><div class="row"><a href="{BASE}/{LANG}/auftrag/{e(x.get("projectId"))}/">'
                         f'<span{la(x)}>{e(head)}</span>{e(project_no(x))}</a><span class="when{cls}">{when}</span></div></li>')
            b.append("</ul>")
        b.append("</div><div>")

        # no empty <span> beside a runhead's heading (step 3a: 141'000 of them, 1.8 MB)
        # the table named by its visible heading (fix round 2: a hidden caption repeated it, 'Angaben, Angaben')
        b.append(f'<div class="runhead"><h2 id="h-det">{_.details}</h2></div>'
                 f'<div class="scroll"><table class="kv" aria-labelledby="h-det"><tbody>')
        cpv = f'<span class="mono">{e(src.get("cpvCode") or "")}</span>' + (
            "<br>" + e(cpv_label(src.get("cpvCode"), de(src, "cpvLabel") or src.get("cpvLabel") or "") or "")
            if (src.get("cpvLabel") or de(src, "cpvLabel")) else "")
        hit = buyer_slugs.get(norm_buyer(src.get("buyerName") or ""))
        # the authority as this publication names it, linked to its page (fix round 1: 41 names showed the
        # spelling the buyer page uses instead)
        buyer_cell = (f'<a href="{BASE}/{LANG}/auftraggeber/{e(hit[0])}/">{e(_ws(src.get("buyerName")))}</a>'
                      if hit else e(src.get("buyerName")))
        if src.get("_buyer_nn"):
            # a name that was an e-mail address: 'Name nicht angegeben', linked only to the page of the publication's
            # other name for the authority, when it has one (fix round 1)
            alt = buyer_slugs.get(norm_buyer(src["_buyer_nn"])) if isinstance(src["_buyer_nn"], str) else None
            buyer_cell = (f'<a href="{BASE}/{LANG}/auftraggeber/{e(alt[0])}/">{e(_.noname)}</a>' if alt
                          else e(_.noname))
        for label, val in [(_.buyer, buyer_cell if src.get("buyerName") or src.get("_buyer_nn") else ""),
                           (_.place, e(src.get("city"))),
                           (_.canton, canton_detail(src if is_tender else None, rows)),
                           (_.type, e(_e("orderType", src.get("orderType")))),
                           ("CPV", cpv if src.get("cpvCode") else ""),
                           (_.treaty, e(_e("bool", src.get("stateContractArea"))))]:
            if val:
                # the label's look lives in the CSS (.kv th): a fixed 112 px let 'Staatsvertrags-
                # bereich' and 'Contracting authority' run into the value (08.10.2026)
                b.append(f'<tr><th>{label}</th><td>{val}</td></tr>')
        b.append("</tbody></table></div>")
        links = []
        if src.get("canton"):
            links.append(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(src["canton"])}/">'
                         f'{e(_if("contracts_in", c=canton_name_or(src["canton"], src["canton"]), of=cant_of(src["canton"])))}</a>')
        if str(src.get("cpvCode") or "") in sectors:
            links.append(f'<a class="tag" href="{BASE}/{LANG}/bereich/{e(src["cpvCode"])}/">{e(_i.same_sector)}</a>')
        if links:
            b.append('<div class="tags">' + "".join(links) + "</div>")
        b.append("</div></div>")
        if not gone:
            b.append(alert_box(cant, div, ghost=bool(src.get("simapUrl"))))
        if is_tender:
            b.append(bid_context(src, ctx, pages, buyer_slugs,
                                 {pid} | {x.get("projectId") for x in (sib or [])}, history=not gone))
            if not gone:
                write(f"/{LANG}/auftrag/{pid}/frist.ics", ics_file(src))
        # the breadcrumbs: a tender under its canton's open tenders, an award under its authority (or
        # its canton); the menu marks that section
        if is_tender:
            mid = [(_.nav_tenders, f"/{LANG}/ausschreibungen/")] + (
                [(canton_name_or(cant, cant), f"/{LANG}/ausschreibungen/{cant}/")] if cant else [])
        else:
            hit = buyer_slugs.get(norm_buyer(src.get("buyerName") or ""))
            mid = ([(_.nav_buyers, f"/{LANG}/auftraggeber/"),
                    (fit_title(hit[1], "", tail_share=0), f"/{LANG}/auftraggeber/{hit[0]}/")] if hit
                   else [(_.nav_cantons, f"/{LANG}/kanton/"),
                         (canton_name_or(cant, cant), f"/{LANG}/kanton/{cant}/")] if cant in award_cants
                   else None)

        desc = final_desc[pid]
        # Some award titles are genuinely identical — twelve read only "BKP 211
        # Baumeisterarbeiten". No amount of clever truncation separates those, so the
        # title carries who won: it is what distinguishes the page and what a reader
        # searching for a firm's public work would type (chosen above, per collision).
        write(f"/{LANG}/auftrag/{pid}/index.html",
              page(final_title[pid],
                   desc, "\n".join(b), f"/{LANG}/auftrag/{pid}/",
                   _.tenders if is_tender else _.award,
                   # the breadcrumb names the publication, not the part of it before its
                   # first dash ('Chavornay' for 'Chavornay – Raccordement de la boucle TRAVYS')
                   leaf=fit_title(title, "", tail_share=0), mid=mid, leaf_lang=tl,
                   # 2026-09-07: 77.8k schede "rilevate ma non indicizzate" (Search Console).
                   # Sono quasi identiche fra loro e il testo simap non e' modificabile (AGB
                   # §5): tolte dall'indice per concentrare il budget di scansione sulle
                   # pagine azienda e sugli indici, che hanno contenuto proprio.
                   # An open tender's page is the one link people pass on: it carries the share
                   # card (og:*), the award pages do not (14.10.2026).
                   robots="noindex", og=is_tender and not gone,
                   head_extra=(BOLD_PRELOAD.format(base=BASE) if is_tender else "")
                   + (XP_JS.format(t=int(dl_at.timestamp() * 1000)) if near else "")))
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


def buyer_title_cands(name: str, sfx: str, short: str) -> list[str]:
    """A buyer's <title>: the whole name, with the long suffix, the short one or none; only
    then cut, at its end first ('Politische Gemeinde Turbenthal…'), and where two authorities
    then read the same, a middle cut that keeps the name up to its first comma — the town —
    before the part that tells them apart. The generic middle cut dropped the town
    ('Politische Gemeinde … Tiefbau und Werke'), and the long suffix left 'Eidgenössisches…
    – vergebene Aufträge' where 'Eidgenössisches Nuklearsicherheitsinspektorat ENSI –
    Aufträge' fits (verifier 28.09.2026)."""
    name = _ws(name)
    m = re.search(r",\s|\s[-–—]\s", name)
    head = m.start() if m and m.start() >= 12 else 0
    whole = [(name + x, name) for x in (sfx, short, "") if len(name + x) <= 64]
    cut = []
    for x in (sfx, short):
        cut.append(_ft(name, x, tail_share=0))
        if head:
            cut.append(_ft(name, x, head_min=head))
        cut += [_ft(name, x), _ft(name, x, tail_share=.7)]
    bare = [_ft(name, "")]
    # A cut title keeps a suffix where it fits (step 3a, 14.10.2026): ranked only by the words it shows,
    # the bare cut won on 274 authorities ('Etat de Genève, Département du Territoire … - OCBA'). The
    # whole name first; then the cuts with a suffix that still say something; the bare cut after them;
    # the poor cuts last.
    def by_words(c):
        return [t for t, core in sorted(c, key=lambda x: -_shown(x[1])[0])]
    good_cut = by_words([x for x in cut if not _poor(x[1])])
    good_bare = [t for t, core in bare if not _poor(core)]
    poor = by_words([x for x in cut + bare if _poor(x[1])])
    return list(dict.fromkeys([t for t, _c in whole] + good_cut + good_bare + poor))


def open_items(rows: list, limit: int = 0) -> str:
    """Open tenders of one authority, the nearest deadline first: the title (lang= when it is in
    another language), canton and sector under it, the deadline on the right."""
    rows = sorted(rows, key=lambda t: (t.get("offerDeadline") or "9999", str(t.get("projectId") or "")))
    if limit:
        rows = rows[:limit]
    heads = distinct_titles([de(t, "title") for t in rows], 120)
    labels = [short_sector(cpv_label(t.get("cpvCode"), de(t, "cpvLabel") or t.get("cpvLabel") or "") or "", 44)
              for t in rows]
    twins = twin_rows(list(zip(heads, labels, [(t.get("offerDeadline") or "")[:10] for t in rows])))
    out = ['<ul class="plain tl mt6">']
    for i, (t, head, label) in enumerate(zip(rows, heads, labels)):
        dl = t.get("offerDeadline") or ""
        cls, when = due_cell(dl, formato.date(dl), until=True)
        sub = " · ".join(x for x in (e(multi_mark(t)) + cantons_cell(t), e(label)) if x)
        out.append(f'<li data-deadline="{e(dl)}"><div class="row"><div><a href="{BASE}/{LANG}/auftrag/{e(t.get("projectId"))}/"{la(t)}>'
                   f'{e(head)}</a><span class="sub sb3">{sub}'
                   f'{e(project_no(t)) if i in twins else ""}</span></div>'
                   f'<span class="when{cls}">{when}</span></div></li>')
    out.append("</ul>" + fb_foot(rows))
    return "".join(out)


def main_div(rows: list) -> str:
    """The CPV division most of these rows fall in, ties to the lower code ('' for none)."""
    div = collections.Counter(str(a.get("cpvCode") or "")[:2] for a in rows
                              if re.fullmatch(r"\d{2}", str(a.get("cpvCode") or "")[:2]))
    return min(div.items(), key=lambda kv: (-kv[1], kv[0]))[0] if div else ""


def build_buyers(awards: list, comp: dict, pages: dict, sectors: set[str],
                 bmap: dict, open_by_buyer: dict, floor: int = 3) -> list:
    """A page per contracting authority. "Welche Aufträge hat die Gemeinde X
    vergeben" is a proper-name search with a real reader behind it — a resident, a
    journalist, a competitor — and no site answers it today. Since 14.10.2026 it opens with
    what the authority has open now, offers its tenders by e-mail and its awards as CSV."""
    by = collections.defaultdict(list)
    for a in awards:
        if a.get("buyerName"):
            by[norm_buyer(a["buyerName"])].append(a)
    # names that differ only in the middle ("Bundesamt für Strassen ASTRA, Filiale Zofingen" /
    # "… Abteilung Strasseninfrastruktur Ost Filiale Zofingen") would share a middle-cut title
    sfx, short = _m("buyer_title"), _m("buyer_title_short")
    btitle = pick_unique({k: buyer_title_cands(v[1], sfx, short) for k, v in bmap.items()})
    out = []
    for key, rows in sorted(by.items(), key=lambda kv: -len(kv[1])):
        if key not in bmap:
            continue
        # never unpack into _ here: `_` is the translation accessor, and shadowing it
        # replaces every label on the page with an integer
        sl, name, _n = bmap[key]
        recent_all = sorted(rows, key=lambda x: (x.get("publicationDate") or "", str(x.get("publicationNumber") or "")),
                            reverse=True)
        recent = recent_all[:BUYER_SHOWN]
        # one money scale for the page: the companies' sums and the awards (fix round 1)
        pu = page_unit(firm_unit(rows, 40),
                       unit_of(price_of(a) for a in recent if len(firm_prices(a)) == 1 and cur_of(a) == "CHF"))
        table, nfirms = firm_table(rows, comp, pages, limit=40, unit=pu)
        cants = collections.Counter(a["canton"] for a in rows if a.get("canton"))
        # fr/it/en: the EU label in the page's language — the publication's own label left
        # the sector list German there. /de/ keeps simap's label: it is Swiss German
        # ("Strasse"), where the EU vocabulary writes "Straße".
        sect = collections.Counter(
            (((de(a, "cpvLabel") or a.get("cpvLabel") or "") if LANG == "de" else
              (cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") or "")),
             str(a.get("cpvCode") or ""))
            for a in rows if a.get("cpvCode"))
        cant = cants.most_common(1)[0][0] if cants else ""
        lead = e(_m("buyer_lead", n=zuschlag(len(rows)), f=firms(nfirms)))
        if nfirms > len(rows):
            # "83 Zuschläge an 90 Unternehmen" reads as an error without this
            k_joint = sum(1 for a in rows if len(winners(a)) > 1)
            lead += " " + e(_m("buyer_joint_note_one") if k_joint == 1
                            else _m("buyer_joint_note", k=formato.count(k_joint)))
        # The eyebrow no longer names a canton: a federal office is not "Kanton TG" because
        # most of its awards are carried out there. The rail says what the canton is.
        b = [f'<div class="title"><div><p class="eyebrow">{_.buyer}</p>{rec_h1(name)}'
             f'<p class="sum">{lead}</p></div><dl class="rail">'
             + (f"<dt>{_.main_canton}</dt><dd>{e(canton_name_or(cant, cant))}</dd>" if cant else "")
             # one firm: its name, not "Impresa: 1" (which reads as a firm called 1)
             + (f"<dt>{_.company}</dt><dd>{e(only_firm(rows, comp))}</dd></dl></div>" if nfirms == 1
                else f"<dt>{lab_n(nfirms, 'companies')}</dt><dd>{formato.count(nfirms)}</dd></dl></div>"),
             ]
        # what it has open now, first: the reason most visitors come (audit 13.10.2026); with nothing
        # open, one sentence in the alert box
        now = sorted(open_by_buyer.get(key, []), key=lambda t: (t.get("offerDeadline") or "9999",
                                                                str(t.get("projectId") or "")))
        if now:
            # the eight nearest deadlines, the rest behind a disclosure (31 rows pushed the page's
            # figures two screens down)
            more = (f'<details class="more"><summary>{e(_if("show_more", n=formato.count(len(now) - 8)))}</summary>'
                    f'{open_items(now[8:])}</details>' if len(now) > 10 else "")
            b.append(f'<div class="sec" id="offen"><div class="runhead"><h2>{e(_i.buyer_open_h)}</h2>'
                     f'<span>{formato.count(len(now))}</span></div>{open_items(now if not more else now[:8])}'
                     f'{more}</div>')
        b.append(alert_box(cant, main_div(rows), lead="" if now else _m("empty_buyer")))
        b += ['<div class="figures">',
              f'<div class="fig"><b>{formato.count(len(rows))}</b><span>{lab_n(len(rows), "awards")}</span></div>',
              f'<div class="fig"><b>{formato.count(nfirms)}</b><span>{lab_n(nfirms, "companies")}</span></div>',
              sum_tile(rows), "</div>",
              csv_download(rows, "auftraggeber", sl, _if("csv_buyer", name=name_cut(name, 60)))]
        bcsv = f"/daten/auftraggeber/{sl}.csv"
        b.append(month_chart(rows, _i.mc_title_buyer, csv=bcsv, own_buyer=True))
        # a table cut to its first rows says so (fix round 1): 'die 40 mit den meisten Zuschlägen von 263'
        f_head = (e(_if("cut_firms", k=formato.count(40), n=formato.count(nfirms))) if nfirms > 40 else _.by_awards)
        b.append(f'<div class="half"><div><div class="runhead"><h2>{_.companies}</h2>'
                 f'<span>{f_head}</span></div>' + table + "</div><div>"
                 + division_figure(rows, sect, sectors, csv=bcsv) + "</div></div>")
        unit = pu
        cut = len(rows) > BUYER_SHOWN
        # the newest BUYER_SHOWN; the others from /daten/ab/<slug>.json in place (js/alle.js), or the CSV file
        a_head = (e(_if("cut_newest", k=formato.count(BUYER_SHOWN), n=formato.count(len(rows)))) if cut
                  else _.chronological)
        b.append(f'<div class="sec"><div class="runhead"><h2>{_.awards}</h2>'
                 f"<span>{a_head}</span></div><div class=\"scroll\"><table class=\"ls awb u{unit}\">"
                 f'{cap(_.awards + ", " + _.chronological)}<thead><tr>'
                 f'<th class="w96">{_.date}</th><th>{_.contract}</th><th>{_.winner}</th>'
                 f'{money_th("amount", unit)}</tr></thead><tbody>')
        heads = distinct_titles([de(a, "title") for a in recent], 110)
        # rows that still read the same (two projects under one title, or one project's lots
        # awarded separately) get the number that tells them apart
        amts = [award_cell(a, unit) for a in recent]
        twn = twin_notes(recent, [(a.get("publicationDate"), h, tuple(winners(a)), amt)
                                  for a, h, amt in zip(recent, heads, amts)])
        for i, (a, head, amt) in enumerate(zip(recent, heads, amts)):
            ws = winners(a)
            who = " · ".join(
                (f'<a href="{BASE}/{LANG}/unternehmen/{e(slug(w))}/">{e(w)}</a>'
                 if slug(w) in pages else e(w)) for w in ws) or "–"
            d = a.get("publicationDate") or ""
            tn = twn.get(i)
            twin = f'<span class="sub sb2">{e(tn)}</span>' if tn else ""
            b.append(f'<tr><td class="mono d">{tt(d, formato.date(d))}</td>'
                     f'<td><a href="{award_href(a)}"{la(a)}>{e(head)}</a>{twin}{award_fx(a)}</td>'
                     f'<td>{who}</td><td class="r num">{amt}</td></tr>')
        b.append("</tbody></table></div>")
        if cut:
            AB_JSON[sl] = recent_all[BUYER_SHOWN:]
            b.append(f'<p class="dl"><a href="{BASE}/daten/auftraggeber/{e(sl)}.csv" type="text/csv" rel="nofollow" '
                     f'download="{e(lingue.CSV_STEM[LANG])}-{e(sl)}.csv" data-alle="/daten/ab/{e(sl)}.json" '
                     f'data-t="{e(_if("show_all_n", n=formato.count(len(rows))))}">'
                     f'{e(_if("csv_all_n", n=formato.count(len(rows))))}</a></p>')
        b.append("</div>")
        write(f"/{LANG}/auftraggeber/{sl}/index.html",
              page(btitle[key],
                   desc_pick(_m("buyer_desc", name=name, n=zuschlag(len(rows)), f=firms(nfirms)),
                             _m("buyer_desc_short", name=name, n=zuschlag(len(rows)), f=firms(nfirms)),
                             _m("buyer_desc_short", name=name_cut(name, 100), n=zuschlag(len(rows)),
                                f=firms(nfirms))),
                   "\n".join(b), f"/{LANG}/auftraggeber/{sl}/", _.buyers,
                   leaf=fit_title(name, "", tail_share=0), lastmod=newest(rows, now),
                   scripts=("alle",) if cut else ()))
        out.append((sl, name, len(rows)))
    return out


# ------------------------------------------------------------------- the hubs

def only_firm(rows: list, comp: dict) -> str:
    """The single firm named across these rows, spelled as on its company page."""
    w = next((w for r in rows for w in winners(r)), "")
    return (comp.get(slug(w)) or {}).get("name") or w


def unit_of(values) -> str:
    """formato.unit_for() of the values a column prints, '' when it prints none (it then sets no scale)."""
    vs = [v for v in values if v]
    return formato.unit_for(vs) if vs else ""


def page_unit(*units: str) -> str:
    """One scale for every money column of a page (fix round 1: 1,579 pages printed one table in 'Tsd. CHF' and
    another in 'Mio. CHF'): millions only when every column would use them, else thousands, which never turn
    an amount into '< 0,1'."""
    us = [u for u in units if u]
    return "m" if us and all(u == "m" for u in us) else "k"


def firm_rank(rows: list, limit: int = 60):
    """(the firms' award counts, their CHF sums, their names, the first `limit` in table order)."""
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
    # ties: the larger sum first, then the name — the same order on every build
    order = sorted(firms.items(), key=lambda kv: (-kv[1], -sums.get(kv[0], 0),
                                                  fold(seen_name.get(kv[0], ""))))[:limit]
    return firms, sums, seen_name, order


def firm_unit(rows: list, limit: int = 60) -> str:
    """The unit firm_table() would choose for these rows on its own ('' when it prints no amount)."""
    _f, sums, _n, order = firm_rank(rows, limit)
    return unit_of(sums.get(sl) for sl, _k in order)


def buyer_unit(rows: list, limit: int = 25) -> str:
    _c, sums, _s, order = buyer_rank(rows, limit)
    return unit_of(sums.get(k) for k, _n in order)


def firm_table(rows: list, comp: dict, pages: dict, limit: int = 60, unit: str = "", cut: str = "") -> str:
    """Companies ranked within THESE rows.

    The sum is computed from the rows passed in, never from the company's global
    total: on a buyer's page the column reads as "what this authority awarded them",
    and a global figure there states something the register never published.
    unit: the page's scale (page_unit); cut: the note above a table that shows the first `limit` only.
    """
    firms, sums, seen_name, order = firm_rank(rows, limit)
    unit = unit or formato.unit_for(sums.get(sl) for sl, _k in order)
    # a card per company on a phone (fix round 2): the name on a row of its own, the awards and the sum under it
    out = [cut + f'<div class="scroll"><table class="ls fk u{unit}">{cap(_.companies + " – " + _.by_awards)}<thead><tr>'
           f'<th>{_.company}</th><th class="r">{_.awards}</th>{money_th("sum_l", unit)}</tr></thead><tbody>']
    for sl, k in order:
        label = (comp.get(sl) or {}).get("name") or seen_name.get(sl, sl)
        cell = (f'<a href="{BASE}/{LANG}/unternehmen/{e(sl)}/">{e(label)}</a>'
                if sl in pages else e(label))
        out.append(f'<tr><td>{cell}</td><td class="r num">{formato.count(k)}</td>'
                   f'<td class="r num">{formato.column_cell(sums.get(sl) or None, unit, empty_sr=_.no_own_amount)}</td></tr>')
    out.append("</tbody></table></div>")
    return "\n".join(out), len(firms)


def canton_title(t: str, sfx: str) -> str:
    """The canton's <title>: with its suffix when it fits, else without it — a cut left both
    Appenzell cantons as 'Marchés publics du canton d’Appenzell… – adjudications'."""
    return t + sfx if len(t + sfx) <= 64 else t if len(t) <= 64 else fit_title(t, sfx, gap1=True)


def sector_title(label: str, code: str) -> str:
    """A sector's <title>: the name whole with 'Aufträge' when it fits, else whole with the
    code only; a division's own general code (71000000) by the division's short name; only
    then a cut. 'Installation… – CPV 45331000' and 'Dienstleistungen… – CPV 71000000' named
    nothing, and 'Bauarbeiten – CPV 45000000' had lost the keyword (verifier 28.09.2026)."""
    long_, sfx = _m("sector_suffix_long", code=code), _m("sector_suffix", code=code)
    whole = short_sector(label, 999)
    for x in (long_, sfx):
        if len(whole + x) <= 64:
            return whole + x
    div = lingue.CPV_SHORT[LANG].get(code[:2]) if code[2:] == "000000" else None
    if div:
        for x in (long_, sfx):
            if len(div + x) <= 64:
                return div + x
    # the name alone, whole, rather than 'Elektrizitätsverteilungs-… – CPV 31200000' (fix round 3: whenever it fits)
    if len(whole) <= 64:
        return whole
    cut = _ft(short_sector(label, 63 - len(sfx)), sfx)
    bare = []
    return rank_titles([cut] + bare + [_ft(whole, sfx), _ft(whole, sfx, tail_share=.7, gap1=True)])[0]


def build_hubs(awards: list, comp: dict, pages: dict, sectors: set[str],
               open_cants: collections.Counter, open_divs: collections.Counter,
               buyer_slugs: dict | None = None) -> tuple[list, list]:
    buyer_slugs = buyer_slugs or {}
    by_cant, by_cpv = collections.defaultdict(list), collections.defaultdict(list)
    for a in awards:
        if a.get("canton"):
            by_cant[a["canton"]].append(a)
        if a.get("cpvCode"):
            by_cpv[str(a["cpvCode"])].append(a)

    cant_list = sorted(by_cant.items(), key=lambda kv: -len(kv[1]))
    nav = (f'<div class="runhead mt26"><h2>{_i.all_cantons}</h2>'
           f'<span>{_.awards}</span></div><div class="tags">'
           + "".join(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(c)}/">'
                     f'{e(canton_name_or(c, c))} · {formato.count(len(r))}</a>'
                     for c, r in cant_list) + "</div>")

    for code, rows in cant_list:
        name = canton_name_or(code, code)
        of = cant_of(code, name)
        # the page's one money scale, shared by the canton × Branche panel (js/kb.js; fix round 1)
        pu = page_unit(firm_unit(rows, CANTON_FIRMS))
        table, nfirms = firm_table(rows, comp, pages, limit=CANTON_FIRMS, unit=pu)
        sect = collections.Counter(
            (cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") or "", str(a.get("cpvCode") or ""))
            for a in rows if a.get("cpvCode"))
        # the canton's open tenders; with none, a sentence (the alert box below offers the rest)
        k_open = open_cants.get(code, 0)
        if k_open:
            # the count is /stand.js's (data-open; step 3b): it rewrote the page every night
            open_link = (f'<p class="m14"><a class="tag" href="{BASE}/{LANG}/ausschreibungen/{code}/" data-open="k:{code}">'
                         f'{e(_if("open_in_x", c=name, of=of))}</a></p>')
        else:
            open_link = f'<p class="sum" style="margin-top:14px">{e(_m("empty_canton", name=name, of=of))}</p>'
        nbuyers = len({a.get("buyerName") for a in rows})
        # how many of them count here only because the authority sits in the canton (fix round 1: 34 % over the
        # whole register, 78 % of Bern's IT awards)
        k_fb = sum(1 for a in rows if a.get("_ksrc") == "auftraggeber")
        fb_line = (f'<p class="sub m10">{e(_if("fb_share_one" if k_fb == 1 else "fb_share", k=formato.count(k_fb), n=zuschlag(len(rows)), p=formato.pct(100 * k_fb / len(rows)), name=name, of=of))}</p>'
                   if k_fb else "")
        cm = sorted({(a.get("publicationDate") or "")[:7] for a in rows if a.get("publicationDate")})
        b = [f'<div class="title"><div><p class="eyebrow">{e(formato.period(cm[0], cm[-1]) if cm else _.canton)}</p>'
             f'<h1>{e(_m("canton_title", name=name, of=of))}</h1>'
             f'<p class="sum">' + e(_m("canton_lead_one" if len(rows) == 1 else "canton_lead",
                                       n=zuschlag(len(rows)), f=firms(nfirms), name=name, of=of))
             + "</p>" + fb_line + open_link + "</div>"
             f'<dl class="rail"><dt>{_.abbr}</dt><dd class="mono">{e(code)}</dd>'
             f'<dt>{lab_n(nbuyers, "buyers")}</dt><dd>{formato.count(nbuyers)}</dd></dl></div>',
             '<div class="figures">',
             f'<div class="fig"><b><data value="{len(rows)}" id="total">{formato.count(len(rows))}</data></b>'
             f'<span>{lab_n(len(rows), "awards")}</span></div>',
             f'<div class="fig"><b>{formato.count(nfirms)}</b><span>{lab_n(nfirms, "companies")}</span></div>',
             sum_tile(rows), "</div>",
             # the canton's awards as a file, and its new tenders by e-mail (14.10.2026)
             csv_download(rows, "kanton", code, _if("csv_canton", name=name, of=of)),
             alert_box(code)]
        ccsv = f"/daten/kanton/{code}.csv"
        b.append(month_chart(rows, _if("mc_title_canton", name=name, of=of), csv=ccsv))
        # the CANTON_FIRMS with the most awards, said so, and the others from /daten/kf/<canton>.json (js/alle.js)
        cut = nfirms > CANTON_FIRMS
        f_head = (e(_if("cut_firms", k=formato.count(CANTON_FIRMS), n=formato.count(nfirms))) if cut else _.by_awards)
        if cut:
            KF_JSON[code] = rows
        more = (f'<p class="dl"><button type="button" class="all" data-alle="/daten/kf/{code}.json" hidden>'
                f'{e(_if("show_all_n", n=formato.count(nfirms)))}</button></p>' if cut else "")
        b.append(f'<div class="half"><div><div class="runhead"><h2>{_.companies}</h2>'
                 f"<span>{f_head}</span></div>" + table.replace("<table ", f'<table data-u="{pu}" ', 1) + more
                 + "</div><div>" + division_figure(rows, sect, sectors, csv=ccsv, anchors=True, unit=pu) + "</div></div>")
        b.append(nav)
        write(f"/{LANG}/kanton/{code}/index.html",
              page(canton_title(_m("canton_title", name=name, of=of), _m("canton_suffix")),
                   desc_pick(_m("canton_desc", n=zuschlag(len(rows)), name=name, of=of, f=firms(nfirms)),
                             _m("canton_desc_short", n=zuschlag(len(rows)), name=name, of=of, f=firms(nfirms))),
                   "\n".join(b), f"/{LANG}/kanton/{code}/", _.canton, leaf=name, lastmod=newest(rows),
                   scripts=("kb", "alle") if cut else ("kb",), head_extra=J_HEAD))

    cpv_list = [(c, r) for c, r in sorted(by_cpv.items(), key=lambda kv: -len(kv[1]))
                if c in sectors]
    for code, rows in cpv_list:
        label = next((cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") for a in rows
                      if cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "")), code)
        table, nfirms = firm_table(rows, comp, pages)
        f_head = (e(_if("cut_firms", k=formato.count(60), n=formato.count(nfirms))) if nfirms > 60 else _.by_awards)
        cants = collections.Counter(a["canton"] for a in rows if a.get("canton"))
        # a division's own general code (72000000) names its division: the pills that link here
        # call it "Informatikdienstleistungen (allgemeiner Code)", the EU label reads otherwise
        general = code[2:] == "000000" and code[:2] in lingue.CPV_SHORT[LANG]
        eyebrow = (_if("sector_general", label=lingue.CPV_SHORT[LANG][code[:2]]) + f" · CPV {code}"
                   if general else f"{_.sector} · CPV {code}")
        # the label itself names the word ('Dienstleistungen im Bereich Rechnungslegung'): the code alone
        if not general and fold(_.sector) in fold(label).split():
            eyebrow = f"CPV {code}"
        # one canton: its name ("Kanton: 1" read as a canton called 1)
        rail_cant = (f'<dt>{_.canton}</dt><dd>{e(canton_name_or(next(iter(cants)), ""))}</dd>'
                     if len(cants) == 1 else
                     f'<dt>{lab_n(len(cants), "cantons")}</dt><dd>{formato.count(len(cants))}</dd>')
        b = [f'<div class="title"><div><p class="eyebrow">{e(eyebrow)}</p>'
             f'<h1>{e(label)}</h1><p class="sum">'
             + e(_m("sector_lead", n=zuschlag(len(rows)), f=firms(nfirms))) + " "
             + sector_stats(rows, comp, pages, buyer_slugs, code[:2]) + "</p></div>"
             f'<dl class="rail"><dt>CPV</dt><dd class="mono">{e(code)}</dd>'
             f'{rail_cant}</dl></div>',
             '<div class="figures">',
             f'<div class="fig"><b>{formato.count(len(rows))}</b><span>{lab_n(len(rows), "awards")}</span></div>',
             f'<div class="fig"><b>{formato.count(nfirms)}</b><span>{lab_n(nfirms, "companies")}</span></div>',
             f'<div class="fig"><b>{formato.count(len(cants))}</b><span>{lab_n(len(cants), "cantons")}</span></div></div>',
             # the open tenders of the industry this sector belongs to, and the alert for it (14.10.2026)
             (f'<p class="m18"><a class="tag" href="{BASE}/{LANG}/ausschreibungen/bereich/{code[:2]}/" data-open="b:{code[:2]}">'
              f'{e(_if("open_in_sector_x", name=div_name(code[:2])))}</a></p>'
              if open_divs.get(code[:2]) and div_name(code[:2]) else ""),
             alert_box("", code[:2]),
             month_chart(rows, _i.mc_title_sector, csv="/daten/bereiche-monate.csv"),
             f'<div class="sec"><div class="runhead"><h2>{_.companies}</h2>'
             f"<span>{f_head}</span></div>" + table + "</div>",
             THIN_MARK,
             f'<div class="runhead mt26"><h2>{lab_n(len(cants), "cantons")}</h2>'
             f'<span>{lab_n(len(rows), "awards")}</span></div><div class="tags">'
             + "".join(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(c)}/">'
                       f'{e(canton_name_or(c, c))} · {formato.count(k)}</a>'
                       # every canton: the tile above counts them all, and 14 of 18 read as
                       # the whole list (verifier 28.09.2026); there are at most 26
                       for c, k in cants.most_common()) + "</div>"]
        # fix round 3 (item 46): under 150 words, the authorities that awarded them as well (the page stays indexable)
        i_thin = b.index(THIN_MARK)
        b[i_thin] = (thin_buyers(rows, buyer_slugs) if page_words("".join(b)) < THIN_WORDS else "")
        write(f"/{LANG}/bereich/{code}/index.html",
              page(sector_title(label, code),
                   # the counts first and the name shortened, so the snippet never ends mid-number
                   desc_pick(_m("sector_desc", n=zuschlag(len(rows)), label=short_sector(label, 70), f=firms(nfirms)),
                             _m("sector_desc_short", n=zuschlag(len(rows)), label=short_sector(label, 70),
                                f=firms(nfirms)),
                             _m("sector_desc_short", n=zuschlag(len(rows)), label=short_sector(label, 44),
                                f=firms(nfirms))),
                   "\n".join(b), f"/{LANG}/bereich/{code}/", _.sectors, leaf=short_sector(label, 64),
                   mid=division_crumbs(code[:2]), lastmod=newest(rows)))
    return cant_list, cpv_list


THIN_MARK, THIN_WORDS = "\x00thin\x00", 150


def page_words(body: str) -> int:
    """The words of a page's body as a reader or a crawler counts them: its text without the tags and the scripts."""
    t = re.sub(r"<script\b.*?</script>", " ", body, flags=re.S)
    return len(re.findall(r"\w+", html.unescape(re.sub(r"<[^>]+>", " ", t))))


def thin_buyers(rows: list, buyer_slugs: dict, limit: int = 8) -> str:
    """The contracting authorities of a thin page's awards, the most first (fix round 3, item 46)."""
    cnt, _sums, spell, order = buyer_rank(rows, limit)
    if not order:
        return ""
    li = []
    for k, n in order:
        hit = buyer_slugs.get(k)
        nm = hit[1] if hit else spell[k].most_common(1)[0][0]
        cell = f'<a href="{BASE}/{LANG}/auftraggeber/{e(hit[0])}/">{e(nm)}</a>' if hit else e(nm)
        li.append(f'<li><div class="row">{cell}<span class="sub num">{zuschlag(n)}</span></div></li>')
    return (f'<div class="sec"><div class="runhead"><h2>{_.buyer if len(cnt) == 1 else _.buyers}</h2>'
            f'<span>{e(_.by_awards)}</span></div><ul class="plain">{"".join(li)}</ul></div>')


def division_crumbs(div: str) -> list:
    """The levels above an 8-digit Bereich: the Branchen, then its own Branche (step 3a)."""
    out = [(_.nav_sectors, f"/{LANG}/branche/")]
    if div in lingue.CPV_SHORT[LANG]:
        out.append((div_name(div), f"/{LANG}/branche/{div}/"))
    return out


def sector_stats(rows: list, comp: dict, pages: dict, buyer_slugs: dict, div: str) -> str:
    """One sentence of a sector page's own figures (step 3a: 1,761 of 2,872 CPV pages had under 150
    words): the CHF total, the authority and the company with the most awards there — named only when
    one leads alone — and the Branche the sector belongs to. HTML."""
    out = []
    total = chf_total(rows)
    if total:
        out.append(e(_if("stats_sum", v=formato.money(total))))
    bc = collections.Counter(norm_buyer(a["buyerName"]) for a in rows if a.get("buyerName"))
    top = bc.most_common(2)
    if top and top[0][1] >= 2 and (len(top) == 1 or top[0][1] > top[1][1]):
        k, n = top[0]
        hit = buyer_slugs.get(k)
        nm = hit[1] if hit else next(" ".join(a["buyerName"].split()) for a in rows
                                     if a.get("buyerName") and norm_buyer(a["buyerName"]) == k)
        cell = f'<a href="{BASE}/{LANG}/auftraggeber/{e(hit[0])}/">{e(nm)}</a>' if hit else e(nm)
        out.append(e(_if("stats_buyer", b="\x00", n=zuschlag(n))).replace("\x00", cell))
    fc = collections.Counter(slug(w) for a in rows for w in winners(a))
    top = fc.most_common(2)
    if top and top[0][1] >= 2 and (len(top) == 1 or top[0][1] > top[1][1]):
        k, n = top[0]
        nm = (comp.get(k) or {}).get("name") or k
        cell = f'<a href="{BASE}/{LANG}/unternehmen/{e(k)}/">{e(nm)}</a>' if k in pages else e(nm)
        out.append(e(_if("stats_firm", c="\x00", n=zuschlag(n))).replace("\x00", cell))
    if div in lingue.CPV_SHORT[LANG]:
        link = f'<a href="{BASE}/{LANG}/branche/{div}/">{e(div_name(div))}</a>'
        q = ("«", "»") if LANG in ("de", "it") else ("«\u202f", "\u202f»") if LANG == "fr" else ("“", "”")
        out.append(e(_if("stats_div", d="\x00")).replace("\x00", q[0] + link + q[1]))
    return " ".join(out)


# ------------------------------------------------------------- open tenders

# rows on the all-tenders index; the rest live on the canton pages, and with JavaScript the hub shows them all
# in place (step 3b: 400 rows were 70'319 px on a phone)
SHOWN = 100
# A cut table says so and offers the rest (fix round 1): a buyer page's newest awards (the others from
# /daten/ab/<slug>.json, filled by build_buyers) and a canton page's companies with the most awards (the others from
# /daten/kf/<canton>.json, filled by build_hubs); js/alle.js shows them in place
BUYER_SHOWN = 60
CANTON_FIRMS = 60
AB_JSON: dict = {}
KF_JSON: dict = {}


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
           f"<updated>{upd[:10]}T06:20:00Z</updated>",
           # RFC 4287 4.1.1: a feed whose entries name no author names one itself (all 288 feeds were
           # invalid without it; step 3a, 14.10.2026)
           f"<author><name>{e(_.site)}</name><uri>{ORIGIN}/{LANG}/</uri></author>"]
    for t in rows:
        d = (t.get("publicationDate") or DATA_DATE)[:10]
        label = cpv_label(t.get("cpvCode"), de(t, "cpvLabel") or t.get("cpvLabel") or "")
        dl = formato.date(t.get("offerDeadline") or "")
        summary = " · ".join(x for x in (_ws(t.get("buyerName")),
                                         f"{_.deadline}{lingue.COLON[LANG]} {dl}" if dl else "",
                                         canton_name_or(t.get("canton"), t.get("canton") or ""), label) if x)
        out.append("<entry>"
                   f"<title>{e(_ws(de(t, 'title')))}</title>"
                   f'<link href="{ORIGIN}/{LANG}/auftrag/{e(t.get("projectId"))}/"/>'
                   f'<id>{ORIGIN}/{LANG}/auftrag/{e(t.get("projectId"))}/</id>'
                   f"<updated>{d}T06:20:00Z</updated>"
                   f"<summary>{e(summary)}</summary></entry>")
    out.append("</feed>")
    return "\n".join(out)


def feed_head(path: str, scope: str) -> str:
    return (f'<link rel="alternate" type="application/atom+xml" '
            f'title="{e(_m("feed_title", scope=scope))}" href="{ORIGIN}{path}">\n')


BREVO_FORM = ("https://127f7d6f.sibforms.com/serve/MUIFAMYhHZXtCOd46O8Uq0H9DqIvbKjonCrMyCDZwBkCaUnmAUo6jz94s1wMVgHNKqluVahz4Xv"
              "QKlERvQhB9gdn9vtuebLrP6KdDdG-3VnrsJ2y6Ex6qU_Zcqp-Wv-dehKLXyYafqlL6rKK8lfXo4avjXTlNc7fPriLfxDj82TdfHK5WP8LSbpWo5N"
              "AVMf2FdpJXb1me5DNcx-xaQ==")

# The form posts straight to Brevo (double opt-in, list "Avvisi bandi"). Without JS the
# browser submits it normally and Brevo redirects to /abo/check/; with JS the answer is
# shown in place, in the page's language. Canton and sector pills are folded into the two
# text attributes the daily sender reads (KANTON, BRANCHE: codes joined by commas, or ALLE).
# The form's script is js/abo.js since step 3b (it was inline here).
# The prefill (js/abo.js) reads ?k=ZH&b=45 (the links on the company pages): only the 26
# canton codes and two-digit CPV divisions are accepted, at most five of each. A value
# without a pill gets one, labelled from the build-time name map, never from the URL, in the
# group of its division; the group holding a prefilled choice is opened (14.10.2026).

# The industries of the form in groups (14.10.2026): forty pills one under the other put the button
# 1,600 px below the e-mail field on a phone. Every CPV division of lingue.CPV_SHORT is in one group;
# a division the vocabulary lacks lands in 'Weitere Branchen'. Names: META["abo_grp_<key>"].
ABO_GROUPS = (("bau", ("45", "71", "44", "43", "70")),
              ("it", ("72", "48", "30", "32", "64")),
              ("tech", ("31", "38", "42", "50", "51", "65", "09", "41", "76", "90", "77")),
              ("verkehr", ("34", "35", "60", "63")),
              ("dienst", ("79", "73", "75", "66", "80", "85", "33", "92", "98", "55")),
              ("waren", ("03", "14", "15", "16", "18", "19", "22", "24", "37", "39")))
assert sorted(c for _g, cs in ABO_GROUPS for c in cs) == sorted(lingue.CPV_SHORT["de"])


def build_abo(by_cant: dict, by_sect: dict, sect_name) -> None:
    mail = ABO_MAIL
    # all 26 cantons (AI was missing whenever it had no open tender), each with its code AND its name
    # since step 3a (14.10.2026): a reader who does not know AI, AR, NW or OW had to hover; in the
    # order of the codes, compact so the form stays short on a phone
    cant_pills = "".join(
        f'<label><input type="checkbox" name="k" value="{e(c)}">'
        f'<span class="tag"><b>{e(c)}</b> {e(canton_name_or(c, c))}</span></label>'
        for c in sorted(CANTONS))
    # all 45 industries, open tenders or not (it offered the 41 with an open tender: 14, 37, 73 and 76
    # were reachable only through a prefilled link; step 3a), the most frequent first in each group
    top_sect = sorted(((c, by_sect.get(c, [])) for c in set(lingue.CPV_SHORT[LANG]) | set(by_sect)),
                      key=lambda kv: (-len(kv[1]), kv[0]))

    def pill(code2: str) -> str:
        return lingue.CPV_SHORT[LANG].get(code2) or short_sector(sect_name(code2), 40)

    def pills(codes: list) -> str:
        return "".join(f'<label><input type="checkbox" name="b" value="{e(c)}"><span class="tag">{e(pill(c))}</span></label>'
                       for c in codes)
    grouped = {c for _g, cs in ABO_GROUPS for c in cs}
    groups = [(g, " ".join(cs), [c for c, _r in top_sect if c in cs]) for g, cs in ABO_GROUPS]
    groups.append(("other", "", [c for c, _r in top_sect if c not in grouped]))
    # each group closed until opened, the most frequent industry first inside it (as before)
    sect_groups = "".join(
        f'<details class="grp"{f" data-c={chr(34)}{dc}{chr(34)}" if dc else ""}><summary>{e(_m("abo_grp_" + g))}</summary>'
        f'<div class="pills" data-g="b">{pills(cs)}</div></details>' for g, dc, cs in groups if cs)
    # Names for pills the prefill may have to create: every canton, every CPV division,
    # in the page's language. Escaped so no label can close the script element.
    names = {"k": {c: canton_name_or(c, c) for c in sorted(CANTONS)},
             "b": {k[:2]: lingue.CPV_SHORT[LANG].get(k[:2]) or short_sector(cpv_label(k, ""), 40)
                   for k in sorted(_CPV) if re.fullmatch(r"\d{2}000000", k) and cpv_label(k, "")}}
    names_json = (json.dumps(names, ensure_ascii=False, sort_keys=True)
                  .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))
    # Fix round 1 (20.10.2026): from 1000 px two columns, the selection on the left, the e-mail address, a summary
    # of the selection, the preview and the button on the right ('Sie abonnieren: Zürich · Bauarbeiten'); a box that
    # filters the 45 Branchen as one types; without JavaScript no selection at all (it would not reach Brevo, which
    # would subscribe the reader to the whole country), and a note that says so; the e-mail field's error is
    # announced (role=alert).
    form = (f'<div class="sec"><h2>{e(_m("abo_form_h2"))}</h2>'
            f'<form id="abo" class="form two" method="post" action="{BREVO_FORM}" data-sending="{e(_m("abo_form_sending"))}" '
            f'data-ok="{e(_m("abo_form_ok"))}" data-err="{e(_m("abo_form_err", mail=mail))}">'
            # fix round 3 (item 28): the selection first, then the address and the button, so Tab goes from the field to the
            # button (it went back to the 26 canton pills); from 1000 px the grid still sets the address beside the selection
            # each group of pills is a fieldset: a screen reader names the group with every checkbox
            # in it (audit 13.10.2026)
            f'<div class="fsel"><fieldset><legend class="f">{e(_m("abo_form_cantons"))}</legend>'
            f'<div class="pills k" data-g="k">{cant_pills}</div></fieldset>'
            f'<fieldset><legend class="f">{e(_m("abo_form_sectors"))}</legend>'
            f'<label class="bq"><span>{e(_m("abo_bfilter"))}</span><input id="abo-bq" type="search" autocomplete="off" '
            f'spellcheck="false" placeholder="{e(_m("abo_bfilter_ph"))}"></label>'
            f'<p class="bqn" role="status" hidden></p>{sect_groups}</fieldset></div>'
            f'<div class="fe"><label class="f" for="abo-email">{e(_m("abo_form_email"))}</label>'
            f'<input id="abo-email" type="email" name="EMAIL" required autocomplete="email" '
            f'placeholder="{e(_m("abo_form_placeholder"))}" aria-describedby="abo-email-err">'
            # the field's error, which js/abo.js fills and ties to it (aria-invalid; step 3b)
            f'<p id="abo-email-err" class="ferr" role="alert" hidden></p></div>'
            f'<div class="fside"><p class="pv" role="status" aria-live="polite"></p>'
            f'<p class="sumry" aria-live="polite"></p>'
            # the pills reach KANTON/BRANCHE only through the script; without it both stay ALLE
            f'<noscript><p class="sub m14">{e(_m("abo_form_nojs"))}</p></noscript>'
            f'<input type="hidden" name="KANTON" value="ALLE"><input type="hidden" name="BRANCHE" value="ALLE">'
            f'<input type="hidden" name="SPRACHE" value="{LANG}"><input type="hidden" name="locale" value="{LANG}">'
            f'<input type="text" name="email_address_check" value="" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">'
            f'<button type="submit">{e(_m("abo_form_submit"))}</button>'
            f'<p class="msg" aria-live="polite"></p>'
            f'<p class="sub">{e(_m("abo_form_consent"))} <a href="{BASE}/{LANG}/datenschutz/">{e(_.privacy)}</a></p></div>'
            f'</form><script type="application/json" id="abo-names">{names_json}</script></div>')
    # no 'Ohne Formular: per E-Mail' any more (step 3a): nobody processes those e-mails
    b = [f'<div class="title"><div><p class="eyebrow">{e(_m("abo_eyebrow"))}</p><h1>{e(_m("abo_h1"))}</h1>'
         f'<p class="sum">{e(_m("abo_lead"))}</p></div></div>',
         form,
         f'<div class="sec"><h2>{e(_m("abo_rss_h2"))}</h2><p>{e(_m("abo_rss_text"))}</p>'
         f'<p><a class="tag" href="{ORIGIN}/{LANG}/ausschreibungen/feed.xml">{e(_m("abo_rss_all"))}</a></p>'
         f'<h3>{e(_m("abo_by_canton"))}</h3><div class="tags">'
         # all 26: every canton keeps its list and its feed, with or without open tenders (14.10.2026)
         + "".join(f'<a class="tag" href="{ORIGIN}/{LANG}/ausschreibungen/{e(c)}/feed.xml">{e(canton_name_or(c, c))}</a>'
                   for c in sorted(CANTONS, key=lambda c: fold(canton_name_or(c, c))))
         + f'</div><h3>{e(_m("abo_by_sector"))}</h3><div class="tags">'
         + "".join(f'<a class="tag" href="{ORIGIN}/{LANG}/ausschreibungen/bereich/{e(c)}/feed.xml">'
                   f'{e(pill(c))}</a>'
                   for c, r in top_sect)
         + "</div></div>"]
    # the title without the site's name in every language (fix round 2: it fitted in IT and EN only, so two of the four
    # carried it)
    write(f"/{LANG}/ausschreibungen/abo/index.html", page(
        _m("abo_title"), _m("abo_desc"),
        "\n".join(b), f"/{LANG}/ausschreibungen/abo/", _.tenders, leaf=_.nav_alert,
        head_extra=J_HEAD + feed_head(f"/{LANG}/ausschreibungen/feed.xml", _m("feed_all")), scripts=("abo",)))


def canton_list(by_cant: dict) -> str:
    """Open tenders per canton: all 26 by name, with the count and a bar, sorted by count.

    It replaces a heat grid whose legend said only "few … many", which hid the counts on
    phones and left Appenzell Innerrhoden out whenever it had nothing open. A canton with
    no open tender shows 0 and links its list all the same: the page is written for all 26 and
    offers the alert when it is empty (14.10.2026)."""
    n = {c: len(by_cant.get(c, [])) for c in CANTONS}
    order = sorted(CANTONS, key=lambda c: (-n[c], fold(canton_name_or(c, c))))
    items = [(canton_name_or(c, c), f"{BASE}/{LANG}/ausschreibungen/{c}/",
              n[c], formato.count(n[c])) for c in order]
    multi = any(len(t.get("_cants") or []) > 1 for rows in by_cant.values() for t in rows)
    # each count recounted by /stand.js from the reader's clock (data-oc, fix round 1)
    return grafici.rank_list(items, fig_id="open-cantons-list", labelledby="open-cantons",
                             lede=_m("open_canton_lede", date=formato.date(DATA_DATE)), two_cols=True,
                             note=_i.multi_note if multi else "", src=chart_src("/daten/offen-kantone.csv"),
                             vattrs=[f' data-oc="k:{c}"' for c in order])


def simap_compare() -> str:
    """What simap.ch is, and what this register adds. Stated as fact, without claiming
    simap lacks anything it actually offers: its alerts exist, they need an account."""
    yes, no_, link = _m("cmp_yes"), _m("cmp_no"), _m("cmp_link")
    rows = [("cmp_r1", yes, link), ("cmp_r2", yes, yes), ("cmp_r3", no_, yes),
            ("cmp_r4", _m("cmp_partly"), yes), ("cmp_r5", no_, yes), ("cmp_r6", no_, yes),
            ("cmp_r7", _m("cmp_acct"), yes), ("cmp_r8", _m("cmp_partly"), yes)]
    body = "".join(
        f'<tr><th scope="row">{e(_m(k))}</th>'
        f'<td class="c{" y" if a == yes else ""}">{e(a)}</td>'
        f'<td class="c{" y" if b == yes else ""}">{e(b)}</td></tr>' for k, a, b in rows)
    return (f'<div class="sec"><h2>{e(_m("cmp_h2"))}</h2>'
            f'<p class="sub" style="max-width:66ch;margin:10px 0 0">{e(_m("cmp_lead"))}</p>'
            f'<div class="glass"><div class="scroll"><table class="cmp">{cap(_m("cmp_h2"))}'
            f'<thead><tr><td></td><th class="c" style="text-align:center">simap.ch</th>'
            f'<th class="c us" style="text-align:center">{e(_m("cmp_us"))}</th></tr></thead>'
            f"<tbody>{body}</tbody></table></div></div></div>")


def open_sector_title(name: str, k: int) -> str:
    """'{branch}: 12 offene Ausschreibungen' within 64 characters: the branch name is cut, never
    the count ('Eaux usées, déchets, nettoyage … appels d’offres en cours' had lost it). None open:
    '{branch}: zurzeit keine offene Ausschreibung' (step 5: '0 offene Ausschreibungen')."""
    key, kw = ("open_sector_title", {"n": open_n(k)}) if k else ("open_sector_title_none", {})
    h = _m(key, name=name, **kw)
    if len(h) <= 64:
        return h
    # fix round 3: the short count, whole, before the name is cut
    one, many = lingue.OPEN_CONTRACTS[LANG]
    short = _m("open_sector_title", name=name, n=f"{formato.count(k)} {one if k == 1 else many}" if k else lingue.OPEN_NONE[LANG])
    if len(short) <= 64:
        return short
    room = 64 - (len(h) - len(name)) - 1
    t = _m(key, name=cut_end(name, room) + "…", **kw) if room >= 12 else ""
    return t if t and len(t) <= 64 else fit_title(h, "", tail_share=0)


# the place of a count in a template, filled in after escaping (an f-string may not hold a backslash in 3.9)
NUL = "\x00"


def oc_span(n: int, key: str) -> str:
    """A count of open tenders that /stand.js recounts from the reader's clock once a deadline has passed since
    the build (fix round 1: the hub said 1'477 beside '92 von 1'469', St. Gallen 62 beside '56 von 56'). key:
    '*' all, 'k:ZH' a canton, 'b:45' a Branche, 'nk'/'nb' the cantons/Branchen with any, 'mx' the largest canton."""
    return f'<span data-oc="{key}">{formato.count(n)}</span>'


def oc_text(text: str, n: int, key: str) -> str:
    """text (with \x00 where the count goes), escaped, the count marked (oc_span)."""
    return e(text).replace("\x00", oc_span(n, key))


def open_n_oc(n: int) -> str:
    """'\x00 offene Ausschreibungen': open_n() with the count's place kept for oc_text()."""
    one, many = lingue.OPEN_TENDERS[LANG]
    return f"\x00 {one if n == 1 else many}"


# the head of every page with a filter bar: the class j says JavaScript runs, before the first paint, so the bar
# (in the page from the start, hidden without a script) moves nothing when liste.js arrives (fix round 1)
J_HEAD = '<script>document.documentElement.classList.add("j")</script>\n'
# Fix round 3 (item 31): a tender list hid its rows past their deadline once /stand.js ran, after the first paint, and
# the list jumped (CLS 0.17-0.36 on a phone for most of the day). Its head now writes, before anything is painted, a
# rule that hides every row whose deadline the reader's clock (Swiss time) has passed: the rows' data-deadline is
# local Swiss time, so 'before now' is a lexical comparison, written as the prefixes of every string below now
# ('2026-10-2' + 0, '2026-10-21T0' …, '2026-10-21T14:3' + 0-6, and now's own minute). The phone's alert row stays
# hidden while expired rows stand before it, until /stand.js puts it after the tenth visible row (data-p); the rows
# due within 7 days keep the line /stand.js writes their 'noch 5 Tage' on. 0.6 KB on the ~400 list pages only. The rule is
# !important: the phone's cards (table.ls tbody tr, display:grid) outrank an attribute selector.
J_LIST = ('<script>(function(h,D){h.classList.add("j");try{var z=function(t){return new D(t).toLocaleString("sv",'
          '{timeZone:"Europe/Zurich"}).replace(" ","T")},v=z(D.now()).slice(0,16),w=new D(D.parse(v.slice(0,10))+6912e5)'
          '.toISOString().slice(0,10),c=function(v,q){for(var s=[],i=0,k;i<v.length;i++)for(k=0;k<+v[i];k++)'
          's.push(\'tr[data-deadline^="\'+v.slice(0,i)+k+\'"]\'+q);return s.join()},x=c(v,"")+\',tr[data-deadline^="\'+v+\'"]\','
          'e=document.createElement("style");if(v[10]!="T")return;e.textContent=x+"{display:none!important}:is("+x+")~tr.ab:not('
          '[data-p],:last-child){display:none!important}@media(max-width:53.75rem){"+c(w," td.when")+"{min-height:3em}}";document.head.appendChild(e)}'
          'catch(e){}})(document.documentElement,Date)</script>\n')
# Fix round 3 (item 31): an open tender's page whose deadline falls within 8 days of the build: its head sets, before the
# first paint, html.xp once the deadline has passed (the expired state: its lead under the title, already in the page,
# the deadline muted, no calendar link) and html.s7 within the last 8 days (the line of 'noch 5 Tage' kept free).
# Opened after its deadline, the page moved by 0.28-0.31; 0.1 KB on those pages only (the nightly rebuilds the rest).
XP_JS = '<script>{{let t={t}-Date.now(),c=document.documentElement.classList;t>0||c.add("xp");t<6912e5&&c.add("s7")}}</script>\n'
NEAR_DAYS = 8
# the filter bar's controls on a phone (<= 600 px) behind 'Filter', unless the address carries a selection
FLT_JS = ('<script>(function(d){if(matchMedia("(max-width:37.5rem)").matches&&!/[?&](?:q|k|b|neu|soon|sort)=/'
          '.test(location.search))d.open=false})(document.currentScript.previousElementSibling)</script>')


def flt_bar(scope: str) -> str:
    """The filter bar of a tender list (js/liste.js binds and fills it): free text, canton, Branche, the order
    (deadline or newest), new ones only, deadline within 7 days, reset, and the alert for the selection."""
    sk = scope[2:] if scope.startswith("k:") else ""
    sb = scope[2:] if scope.startswith("b:") else ""

    def j(k: str) -> str:
        return e(lingue.JS[k][LANG])
    day = LATEST_TENDER_DAY[0]
    return (f'<div class="flt" role="group" aria-label="{j("f_label")}"><details class="fd" open>'
            f'<summary>{j("f_toggle")}<span class="fn0"></span></summary><div class="fc">'
            f'<label class="fq">{j("f_q")}<input type="search" name="q" autocomplete="off" spellcheck="false"></label>'
            + ("" if sk else f'<label class="fk">{j("k_canton")}<select name="k"><option value="">{j("f_k_all")}</option></select></label>')
            + ("" if sb else f'<label class="fb">{j("k_div")}<select name="b"><option value="">{j("f_b_all")}</option></select></label>')
            + f'<label class="fs">{j("f_sort")}<select name="sort"><option value="">{j("f_sort_dl")}</option>'
            f'<option value="neu">{j("f_sort_new")}</option></select></label>'
            + '<div class="chks">'
            + (f'<label class="chk"><input type="checkbox" name="neu"> '
               f'{e(lingue.JS["f_new"][LANG].format(d=formato.date_short(day)))}</label>' if day else "")
            + f'<label class="chk"><input type="checkbox" name="soon"> {j("f_soon")}</label></div>'
            f'</div></details>{FLT_JS}'
            # the count, and beside it the reset (while a filter is set) and the alert for the selection
            f'<div class="fl2"><p class="cnt" role="status" aria-live="polite" tabindex="-1"></p>'
            f'<button type="button" class="clr" hidden>{j("f_clear")}</button>'
            f'<a class="tag fa" href="{e(alert_href(sk, sb))}" rel="nofollow">{j("f_abo")}</a></div>'
            f'<p class="fan" hidden>{j("f_abo_kw")}</p></div>')


def tender_table(rows: list, ab: str = "") -> str:
    """Open tenders, the nearest deadline first: deadline, title (in its own language, lang=),
    authority, canton. ab: the alert box, as a row after the first ten (shown on a phone only, fix round 1)."""
    out = [f'<div class="scroll"><table class="tl ls">{cap(_m("open_table_h2"))}<thead><tr>'
           f'<th style="width:104px">{_.deadline}</th>'
           f'<th>{_.tender}</th><th>{_.buyer}</th><th class="w44">{_.canton_abbr}</th>'
           "</tr></thead><tbody>"]
    rows = sorted(rows, key=lambda x: x.get("offerDeadline") or "9999")
    heads = distinct_titles([de(t, "title") for t in rows], 120)
    labels = [short_sector(cpv_label(t.get("cpvCode"), de(t, "cpvLabel") or t.get("cpvLabel") or "") or "", 60)
              if (t.get("cpvLabel") or de(t, "cpvLabel")) else "" for t in rows]
    twins = twin_rows(list(zip(heads, labels)))
    at = min(10, len(rows))
    for i, (t, head, label) in enumerate(zip(rows, heads, labels)):
        dl = t.get("offerDeadline") or ""
        sub = multi_mark(t) + label + (project_no(t) if i in twins else "")
        cls, when = due_cell(dl, formato.date(dl), soon=True)
        out.append(
            f'<tr data-deadline="{e(dl)}"><td class="when mono d{cls}">{when}</td>'
            f'<td><a href="{BASE}/{LANG}/auftrag/{e(t.get("projectId"))}/"{la(t)}>{e(head)}</a>'
            + (f'<span class="sub sb2">{e(sub.strip(" ·"))}</span>'
               if sub.strip(" ·") else "")
            + f'</td><td>{e(buyer_label(t))}</td><td>{cantons_cell(t)}</td></tr>')
        if ab and i + 1 == at:
            out.append(f'<tr class="ab"><td colspan="4">{ab}</td></tr>')
    out.append("</tbody></table></div>" + fb_foot(rows))
    return "\n".join(out)


def list_section(rows: list, scope: str, path: str, ab: str = "") -> str:
    """A canton's or an industry's open tenders, in the section liste.js reads (data-liste: its scope,
    data-n: its size), its filter bar first. Over LIST_CUT rows (Zurich 342, Bauarbeiten 792: 336 KB, 54'000 px
    on a phone) the page shows the LIST_FIRST nearest deadlines and links the whole list, a page of its own that
    works without JavaScript (alle/); with JavaScript the link loads the rest in place (step 3b)."""
    cut = len(rows) > LIST_CUT
    key = "k:" + scope[2:] if scope.startswith("k:") else "b:" + scope[2:] if scope.startswith("b:") else "*"
    shown = sorted(rows, key=lambda x: (x.get("offerDeadline") or "9999", str(x.get("projectId") or "")))[:LIST_FIRST] if cut else rows
    return (f'<div class="sec" id="fristen" data-liste="{scope}" data-n="{len(rows)}">'
            + flt_bar(scope)
            + (f'<p class="sub m10 fn">'
               + oc_text(_if("first_n_note", n=formato.count(LIST_FIRST), total="\x00"), len(rows), key) + "</p>"
               if cut else "")
            + tender_table(shown, ab)
            + (f'<p class="dl"><a href="{BASE}{path}alle/" data-all>'
               + oc_text(_if("show_all_n", n="\x00"), len(rows), key) + "</a></p>" if cut else "") + "</div>")


def lst_h1(h: str) -> str:
    """A tender list's long heading ('Offene Ausschreibungen im Kanton Appenzell Ausserrhoden') a size smaller, so it
    keeps to one or two lines and the first tender stays within the first screen (fix round 1)."""
    return ' class="lg"' if len(re.sub(r"<[^>]+>", "", h)) > 48 else ""


def write_all_list(rows: list, path: str, name: str, scope: str, mid: list, alert: str) -> None:
    """The whole of a cut list (list_section) on its own page, noindex: the short list is the one to index.
    Titled '{name} – vollständige Liste', its last breadcrumb 'Vollständige Liste' (fix round 1)."""
    key = "k:" + scope[2:] if scope.startswith("k:") else "b:" + scope[2:]
    h1 = _m("all_list_title", h=name)
    b = [f'<div class="title lst"><div><p class="eyebrow">{e(_m("list_eyebrow"))}</p><h1{lst_h1(h1)}>{e(h1)}</h1>'
         f'<p class="sum">{oc_text(_m("all_list_lead", n=NUL), len(rows), key)}</p></div>'
         f'<dl class="rail"><dt>{_.as_of}</dt><dd>{tt(DATA_DATE, formato.date(DATA_DATE))}</dd></dl></div>',
         f'<div class="sec" id="fristen" data-liste="{scope}" data-n="{len(rows)}">' + flt_bar(scope)
         + tender_table(rows, alert) + "</div>",
         f'<div class="ab-out">{alert}</div>',
         f'<div class="tags" style="margin-top:22px"><a class="tag" href="{BASE}{path}">'
         f'<span aria-hidden="true">← </span>{e(_m("all_list_back"))}</a></div>']
    write(f"{path}alle/index.html", page(
        first_fit(h1, _m("all_list_title", h=name_cut(name, 40))), _m("all_list_lead", n=formato.count(len(rows))),
        "\n".join(b), f"{path}alle/", _.tenders, leaf=_m("all_list_crumb"), mid=mid, fresh=True,
        robots="noindex", scripts=("liste",), lastmod=newest(rows), head_extra=J_LIST))


def build_open(opens: list, sectors: set[str], buyer_slugs: dict, award_cants: set) -> int:
    """The open tenders, whole and by canton.

    This is the part with intent behind it: someone searching for current tenders is
    looking to bid, not to browse. The pages carry the deadline first, because that is
    the fact that decides whether the rest matters.

    Since 14.10.2026 the alert sits at the top of every list, prefilled with its canton or
    industry, instead of under 400 rows; every canton and every CPV division keeps its list and
    its feed even with nothing open (an empty list says so and offers the alert, noindex).
    """
    by_cant = collections.defaultdict(list)
    for t in opens:
        # in the list of every canton it has (a tender with lots in GE, NE, VD and VS is in all four;
        # step 3a, 14.10.2026)
        for k in t.get("_cants") or ([t["canton"]] if t.get("canton") else []):
            by_cant[k].append(t)
    # Branche = CPV-Abteilung (erste zwei Ziffern): "45" Bauarbeiten, "71" Planung, "72" IT …
    by_sect = collections.defaultdict(list)
    for t in opens:
        code2 = str(t.get("cpvCode") or "")[:2]
        if code2.isdigit():
            by_sect[code2].append(t)

    def sect_name(code2: str) -> str:
        return (lingue.CPV_SHORT[LANG].get(code2) or cpv_label(code2 + "000000", "")
                or next((de(t, "cpvLabel") or t.get("cpvLabel") or "" for t in by_sect[code2]), "")
                or code2)

    sect_nav = ('<div class="tags">'
                + "".join(f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/bereich/{e(c)}/">'
                          f'{e(sect_name(c))} · {oc_span(len(r), "b:" + c)}</a>'
                          # all of them: the tile above counts every industry (40), and 24 pills
                          # under it left 16 unexplained
                          for c, r in sorted(by_sect.items(), key=lambda kv: (-len(kv[1]), kv[0])))
                + "</div>")
    nxt = next(iter(sorted(t.get("offerDeadline") for t in opens if t.get("offerDeadline"))), "")
    today = tt(DATA_DATE, formato.date(DATA_DATE))

    # The hub (fix round 1): the list first — its filter, the nearest deadlines, the alert after ten rows on a
    # phone — and only then the figures, the ways in by canton and by industry, and the explanations. Every count
    # of open tenders is recounted from the reader's clock by /stand.js (oc_span).
    hub_rows = sorted(opens, key=lambda x: (x.get("offerDeadline") or "9999", str(x.get("projectId") or "")))[:SHOWN]
    abx = alert_box(feed=f"/{LANG}/ausschreibungen/feed.xml")
    b = [f'<div class="title lst"><div><p class="eyebrow">{e(_m("list_eyebrow"))}</p>'
         f"<h1>{e(_p.open_tenders_h1)}</h1>"
         f'<p class="sum">' + oc_text(_m("open_lead_short", n="\x00"), len(opens), "*") + "</p></div>"
         f'<dl class="rail"><dt>{_.as_of}</dt><dd>{today}</dd>'
         f"<dt>{lab_n(len(by_cant), 'cantons')}</dt><dd>{oc_span(len(by_cant), 'nk')}</dd></dl></div>",
         f'<div class="sec" id="fristen" data-liste="" data-n="{len(opens)}"><h2 class="sr">{e(_m("open_table_h2"))}</h2>'
         + flt_bar("")
         + (f'<p class="sub m10 fn">'
            + oc_text(_if("showing_n", n=formato.count(SHOWN), total="\x00"), len(opens), "*") + "</p>"
            if len(opens) > SHOWN else "")
         # sorted BEFORE slicing: taking 400 in file order and then sorting those
         # states "the nearest deadlines" about an arbitrary subset of the 588.
         + tender_table(hub_rows, abx)
         + (f'<p class="sub m10">{e(_if("nodl_note", n=formato.count(NO_DEADLINE[0])))}</p>' if NO_DEADLINE[0] else "")
         + "</div>",
         f'<div class="ab-out">{abx}</div>',
         f'<div class="figures">'
         f'<a class="fig money" href="#fristen"><b class="num" data-oc="*">{formato.count(len(opens))}</b>'
         f'<span>{e(_m("open_kpi_open"))}</span></a>'
         f'<a class="fig" href="#open-cantons"><b class="num" data-oc="nk">{formato.count(len(by_cant))}</b>'
         f'<span>{e(_m("open_kpi_cantons"))}</span></a>'
         f'<a class="fig" href="#branchen"><b class="num" data-oc="nb">{formato.count(len(by_sect))}</b>'
         f'<span>{e(_m("open_kpi_sectors"))}</span></a>'
         # .date: the date stays on one line ('08.10.20|26' on phones, 08.10.2026)
         f'<a class="fig date" href="#fristen"><b class="num">{tt(nxt, formato.date(nxt))}</b>'
         f'<span>{e(_m("open_kpi_next"))}</span></a></div>',
         f'<div class="sec"><h2 id="open-cantons">{e(_m("open_by_canton_h2"))}</h2>' + canton_list(by_cant) + "</div>",
         f'<div class="sec"><h2 id="branchen">{e(_m("open_by_sector_h2"))}</h2>' + sect_nav + "</div>",
         f'<div class="sec"><h2>{e(_m("open_howto_h2"))}</h2>'
         f'<p>{oc_text(_m("open_lead", n=NUL), len(opens), "*")}</p><p>{e(_m("open_howto"))}</p></div>',
         simap_compare()]
    write(f"/{LANG}/ausschreibungen/index.html", page(
        _m("open_title", n=formato.count(len(opens))), _m("open_desc", n=formato.count(len(opens))),
        "\n".join(b), f"/{LANG}/ausschreibungen/", _.tenders, fresh=True,
        head_extra=J_LIST + feed_head(f"/{LANG}/ausschreibungen/feed.xml", _m("feed_all")), lastmod=newest(opens),
        scripts=("liste",)))
    write(f"/{LANG}/ausschreibungen/feed.xml", feed_xml(_m("feed_all"), f"/{LANG}/ausschreibungen/feed.xml", opens))
    build_abo(by_cant, by_sect, sect_name)

    # every division the vocabulary names, and any other the data has
    for code2 in sorted(set(lingue.CPV_SHORT[LANG]) | set(by_sect)):
        rows = by_sect.get(code2, [])
        name = sect_name(code2)
        key = f"b:{code2}"
        # one template for title and H1: "{name}: 762 offene Ausschreibungen" ('zurzeit keine' when none)
        h = (_m("open_sector_title", name=name, n=open_n(len(rows))) if rows
             else _m("open_sector_title_none", name=name))
        h_html = (oc_text(_m("open_sector_title", name=name, n=open_n_oc(len(rows))), len(rows), key) if rows
                  else e(h))
        desc = _m("open_sector_desc_one" if len(rows) == 1 else "open_sector_desc",
                  n=open_n(len(rows)), name=name, code=code2)
        word = lingue.SECTOR_WORD[LANG].get(code2)
        seo_title = ""
        if word and len(rows) > 1:
            k = formato.count(len(rows))
            seo_title = first_fit(_m("open_sector_t1", word=word[0], k=k), _m("open_sector_t2", word=word[0], k=k))
            h = _m("open_sector_t2", word=word[0], k=k)
            h_html = oc_text(_m("open_sector_t2", word=word[0], k="\x00"), len(rows), key)
            desc = _m("open_sector_desc_word", k=k, w=word[1])
        if not rows:
            desc = _m("empty_sector", name=name)
        fp = f"/{LANG}/ausschreibungen/bereich/{code2}/feed.xml"
        path = f"/{LANG}/ausschreibungen/bereich/{code2}/"
        # a short lead: the page's description was written for search engines (five lines on a phone)
        b = [f'<div class="title lst"><div><p class="eyebrow">{e(_m("list_eyebrow"))}</p>'
             f'<h1{lst_h1(h_html)}>{h_html}</h1>'
             + (f'<p class="sum">' + oc_text(_m("list_lead_div", n=open_n_oc(len(rows)), name=name), len(rows), key)
                + "</p>" if rows else "") + "</div>"
             f'<dl class="rail"><dt>{_.as_of}</dt><dd>{today}</dd>'
             f'<dt>CPV</dt><dd class="mono">{e(code2)}</dd></dl></div>']
        if rows:
            abx = alert_box("", code2, feed=fp)
            b += [list_section(rows, key, path, abx), f'<div class="ab-out">{abx}</div>']
            if len(rows) > LIST_CUT:
                write_all_list(rows, path, word[0] if word else name, key,
                               [(_.nav_tenders, f"/{LANG}/ausschreibungen/"), (name, path)], abx)
        else:
            b += [f'<p class="empty">{e(desc)}</p>', alert_box("", code2, feed=fp)]
        b.append(f'<div class="tags" style="margin-top:22px">'
                 f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/">{e(_i.all_open)}</a></div>')
        write(f"{path}index.html", page(
            seo_title or open_sector_title(name, len(rows)),
            desc if seo_title or not rows else desc_pick(desc, _m("open_sector_desc_one" if len(rows) == 1
                                                                  else "open_sector_desc_short",
                                                                  n=open_n(len(rows)), name=name, code=code2)),
            "\n".join(b), path, _.tenders, leaf=name,
            fresh=True, robots="" if rows else "noindex", head_extra=(J_LIST if rows else "") + feed_head(fp, name),
            lastmod=newest(rows), scripts=("liste",) if rows else ()))
        write(f"{path}feed.xml", feed_xml(name, fp, rows))

    for code in sorted(CANTONS):
        rows = by_cant.get(code, [])
        name = canton_name_or(code, code)
        of = cant_of(code, name)
        key = f"k:{code}"
        desc = (_m("empty_canton", name=name, of=of) if not rows else
                _m("open_canton_desc_one" if len(rows) == 1 else "open_canton_desc",
                   n=open_n(len(rows)), name=name, of=of))
        fp = f"/{LANG}/ausschreibungen/{code}/feed.xml"
        path = f"/{LANG}/ausschreibungen/{code}/"
        b = [f'<div class="title lst"><div><p class="eyebrow">{e(_m("list_eyebrow"))}</p>'
             f'<h1{lst_h1(_m("open_canton_h1", name=name, of=of))}>{e(_m("open_canton_h1", name=name, of=of))}</h1>'
             + (f'<p class="sum">'
                + oc_text(_m("list_lead_canton", n=open_n_oc(len(rows)), name=name, of=of), len(rows), key)
                + "</p>" if rows else "") + "</div>"
             f'<dl class="rail"><dt>{_.as_of}</dt><dd>{today}</dd>'
             f'<dt>{_.canton}</dt><dd>{e(name)}</dd></dl></div>']
        if rows:
            abx = alert_box(code, feed=fp)
            b += [list_section(rows, key, path, abx), f'<div class="ab-out">{abx}</div>']
            if len(rows) > LIST_CUT:
                write_all_list(rows, path, _m("open_canton_title", name=name, of=of), key,
                               [(_.nav_tenders, f"/{LANG}/ausschreibungen/"), (name, path)], abx)
        else:
            b += [f'<p class="empty">{e(desc)}</p>', alert_box(code, feed=fp)]
        b.append(f'<div class="tags" style="margin-top:22px">'
                 + (f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(code)}/">{e(_if("awarded_in", c=name, of=of))}</a>'
                    if code in award_cants else "")
                 + f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/">{e(_i.all_open)}</a></div>')
        write(f"{path}index.html", page(
            # t3, the shortest, names the tenders after the count (fix round 2: 'Appels d'offres Appenzell
            # Rhodes-Extérieures : 4 en cours' had no preposition)
            first_fit(*(_m(t, name=name, of=of, c=open_contracts(len(rows)),
                           o=open_n(len(rows)) if rows else open_contracts(0))
                         for t in ("open_canton_t1", "open_canton_t2", "open_canton_t3"))), desc,
            "\n".join(b), path, _.tenders, leaf=name, fresh=True,
            robots="" if rows else "noindex", head_extra=(J_LIST if rows else "") + feed_head(fp, name),
            lastmod=newest(rows), scripts=("liste",) if rows else ()))
        write(f"{path}feed.xml", feed_xml(name, fp, rows))
    return 1 + len(CANTONS) + len(set(lingue.CPV_SHORT[LANG]) | set(by_sect))


def buyer_rank(rows: list, limit: int = 25):
    cnt: collections.Counter = collections.Counter()
    sums: dict = collections.defaultdict(float)
    spell: dict = {}
    for a in rows:
        if not a.get("buyerName"):
            continue
        k = norm_buyer(a["buyerName"])
        cnt[k] += 1
        spell.setdefault(k, collections.Counter())[" ".join(a["buyerName"].split())] += 1
        p = chf_amount(a)
        if p is not None and len(winners(a)) == 1:
            sums[k] += p
    order = sorted(cnt.items(), key=lambda kv: (-kv[1], -sums.get(kv[0], 0),
                                                 fold(spell[kv[0]].most_common(1)[0][0])))[:limit]
    return cnt, sums, spell, order


def buyer_table(rows: list, buyer_slugs: dict, limit: int = 25, unit: str = "") -> str:
    """Contracting authorities ranked within THESE rows, as firm_table ranks companies: the count, and
    the CHF sum of their awards to one firm (no unit rates, no foreign currency). unit: the page's scale."""
    cnt, sums, spell, order = buyer_rank(rows, limit)
    unit = unit or formato.unit_for(sums.get(k) for k, _n in order)
    out = [f'<div class="scroll"><table class="ls fk u{unit}">{cap(_.buyers + " – " + _.by_awards)}<thead><tr>'
           f'<th>{_.buyer}</th><th class="r">{_.awards}</th>{money_th("sum_l", unit)}</tr></thead><tbody>']
    for k, n in order:
        hit = buyer_slugs.get(k)
        nm = hit[1] if hit else spell[k].most_common(1)[0][0]
        cell = f'<a href="{BASE}/{LANG}/auftraggeber/{e(hit[0])}/">{e(nm)}</a>' if hit else e(nm)
        out.append(f'<tr><td>{cell}</td><td class="r num">{formato.count(n)}</td>'
                   f'<td class="r num">{formato.column_cell(sums.get(k) or None, unit, empty_sr=_.no_own_amount)}</td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out), len(cnt)


def div_title(name: str) -> str:
    """A Branche's <title>: its short name with the long suffix, else the short one, else alone."""
    for x in (_m("div_suffix"), _m("div_suffix_short"), ""):
        if len(name + x) <= 64:
            return name + x
    return fit_title(name, "")


# rows of a Branche page's two rankings, and of its list of Bereiche (the A–Z index has them all):
# the 45 pages × 4 languages came to 5 MB with 25 and every Bereich (step 3a byte budget)
TOP_DIV, TOP_SUB = 20, 30


def build_divisions(awards: list, opens: list, comp: dict, pages: dict, sectors: set[str],
                    buyer_slugs: dict, by_cpv: dict) -> int:
    """The 45 Branchen (CPV divisions, the first two digits of the code): an index with their open
    tenders and awards, and a page of awards for each (step 3a, 14.10.2026). The menu's 'Branchen'
    opened the 718 eight-digit Bereiche; those are now the second level, linked from their Branche,
    and keep their URLs. Each page: the companies and the authorities with the most awards (count and
    CHF sum), the awards by canton (linking to the canton), the month chart, the Bereiche of the
    division, and the way to its open tenders."""
    by_div = collections.defaultdict(list)
    for a in awards:
        d = str(a.get("cpvCode") or "")[:2]
        if d in lingue.CPV_SHORT[LANG]:
            by_div[d].append(a)
    open_div = collections.defaultdict(list)
    for t in opens:
        d = str(t.get("cpvCode") or "")[:2]
        if d in lingue.CPV_SHORT[LANG]:
            open_div[d].append(t)
    divs = sorted(lingue.CPV_SHORT[LANG], key=lambda d: (-len(by_div.get(d, [])), d))
    n_all = len(divs)
    # the index: every Branche, its open tenders and its awards
    rows_html = []
    for d in divs:
        k_open, k_aw = len(open_div.get(d, [])), len(by_div.get(d, []))
        open_cell = (f'<a href="{BASE}/{LANG}/ausschreibungen/bereich/{d}/">{oc_span(k_open, "b:" + d)}</a>'
                     if k_open else "0")
        rows_html.append(f'<tr><td><a href="{BASE}/{LANG}/branche/{d}/">{e(div_name(d))}</a></td>'
                         f'<td class="mono">{d}</td><td class="r num">{open_cell}</td>'
                         f'<td class="r num">{formato.count(k_aw)}</td></tr>')
    b = [f'<div class="title"><div><p class="eyebrow">{e(_.divisions)}</p><h1>{e(_i.div_index_h1)}</h1>'
         f'<p class="sum">{e(_if("div_index_lead", n=n_all))}</p></div>'
         f'<dl class="rail"><dt>{_.entries}</dt><dd class="num">{formato.count(n_all)}</dd></dl></div>',
         # a card per Branche on a phone (table.ls.dv, fix round 1: four columns at 390 px broke 47 words)
         f'<div class="sec"><div class="scroll"><table class="ls dv">{cap(_i.div_index_h1)}<thead><tr>'
         f'<th>{_.division}</th><th style="width:60px">CPV</th><th class="r">{_i.col_open}</th>'
         f'<th class="r">{_.awards}</th></tr></thead><tbody>' + "".join(rows_html) + "</tbody></table></div>"
         f'<p class="dl"><a href="{BASE}/{LANG}/bereich/">{e(_if("all_bereiche", n=formato.count(len(sectors))))}</a></p></div>']
    write(f"/{LANG}/branche/index.html", page(
        _i.div_index_title, _if("div_index_desc", n=n_all), "\n".join(b), f"/{LANG}/branche/", _.divisions,
        lastmod=newest(awards, opens)))

    for d in divs:
        rows, now = by_div.get(d, []), open_div.get(d, [])
        name = div_name(d)
        # one money scale for the two rankings (fix round 1)
        pu = page_unit(firm_unit(rows, TOP_DIV), buyer_unit(rows, TOP_DIV))
        table, nfirms = firm_table(rows, comp, pages, limit=TOP_DIV, unit=pu)
        btable, nbuyers = buyer_table(rows, buyer_slugs, limit=TOP_DIV, unit=pu)
        cants = collections.Counter(a.get("canton") or "" for a in rows)
        # '267 Zuschläge an 263 Unternehmen' needed saying why (fix round 1): most firms won once here
        fk = collections.Counter(slug(w) for a in rows for w in winners(a))
        once = sum(1 for k in fk.values() if k == 1)
        why = (" " + _if("div_once", k=formato.count(once), f=formato.count(nfirms))
               if rows and nfirms >= 10 and once * 2 > nfirms else "")
        b = [f'<div class="title"><div><p class="eyebrow">{e(_.division)} · CPV {d}</p><h1>{e(name)}</h1>'
             + (f'<p class="sum">{e(_m("div_lead", n=zuschlag(len(rows)), f=firms(nfirms), name=name) + why)}</p>'
                if rows else f'<p class="sum">{e(_i.div_none)}</p>')
             + f'</div><dl class="rail"><dt>CPV</dt><dd class="mono">{d}</dd>'
             f'<dt>{lab_n(len([c for c in cants if c]), "cantons")}</dt>'
             f'<dd>{formato.count(len([c for c in cants if c]))}</dd></dl></div>']
        if rows:
            b += ['<div class="figures">',
                  f'<div class="fig"><b>{formato.count(len(rows))}</b><span>{lab_n(len(rows), "awards")}</span></div>',
                  f'<div class="fig"><b>{formato.count(nfirms)}</b><span>{lab_n(nfirms, "companies")}</span></div>',
                  sum_tile(rows), '</div>']
        # the open tenders' count is /stand.js's (data-open; step 3b): the tile and the pill rewrote the page
        # every night for that number
        b.append(f'<p class="m18"><a class="tag" href="{BASE}/{LANG}/ausschreibungen/bereich/{d}/" data-open="b:{d}">'
                 f'{e(_if("open_in_sector_x", name=name))}</a></p>' if now
                 else f'<p class="sum" style="margin-top:14px">{e(_m("empty_sector", name=name))}</p>')
        b.append(alert_box("", d))
        if rows:
            b.append(month_chart(rows, _i.mc_title_div, csv="/daten/branchen-monate.csv"))
            fh = (_if("cut_firms", k=formato.count(TOP_DIV), n=formato.count(nfirms)) if nfirms > TOP_DIV
                  else _if("top_n", k=min(TOP_DIV, nfirms)))
            bh = (_if("cut_buyers", k=formato.count(TOP_DIV), n=formato.count(nbuyers)) if nbuyers > TOP_DIV
                  else _if("top_n_b", k=min(TOP_DIV, nbuyers)))
            b.append(f'<div class="half"><div><div class="runhead"><h2>{_.companies}</h2>'
                     f'<span>{e(fh)}</span></div>' + table + "</div><div>"
                     f'<div class="runhead"><h2>{_i.div_buyers_h}</h2>'
                     f'<span>{e(bh)}</span></div>' + btable + "</div></div>")
            # the awards by canton, each row to the canton's awards in this Branche (#kb-45 opens the canton ×
            # Branche panel, and without a script leads to the Branche's row on the canton page; fix round 1)
            items = [(canton_name_or(c, c), f"{BASE}/{LANG}/kanton/{c}/#kb-{d}", k, formato.count(k))
                     for c, k in sorted(((c, k) for c, k in cants.items() if c), key=lambda kv: (-kv[1], kv[0]))]
            other = ((_.no_canton, None, cants[""], formato.count(cants[""])) if cants.get("") else None)
            b.append(grafici.rank_list(items, fig_id="chart-cantons", title=_i.by_canton_awards,
                                       other=other, total=len(rows), two_cols=True,
                                       src=chart_src("/daten/branchen-kantone.csv")))
            # the second level: the Bereiche of this Branche that have a page, the most awards first
            sub = sorted(((c, r) for c, r in by_cpv.items() if c[:2] == d and c in sectors),
                         key=lambda kv: (-len(kv[1]), kv[0]))
            if sub:
                b.append(f'<div class="sec"><div class="runhead"><h2>{e(_i.div_sectors_h)}</h2>'
                         f'<span>{formato.count(len(sub))}</span></div><ul class="plain cols2">')
                for code, r in sub[:TOP_SUB]:
                    label = next((cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") for a in r
                                  if cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "")), code)
                    b.append(f'<li><div class="row"><a href="{BASE}/{LANG}/bereich/{code}/">{e(label)}</a>'
                             f'<span class="sub num">{formato.count(len(r))}</span></div></li>')
                b.append("</ul>" + (f'<p class="dl"><a href="{BASE}/{LANG}/bereich/">'
                                    f'{e(_if("all_bereiche", n=formato.count(len(sectors))))}</a></p>'
                                    if len(sub) > TOP_SUB else "") + "</div>")
        kw = dict(name=name, code=d, n=zuschlag(len(rows)), f=firms(nfirms))
        write(f"/{LANG}/branche/{d}/index.html", page(
            div_title(name),
            desc_pick(_m("div_desc", **kw), _m("div_desc_short", **kw)) if rows else _i.div_none + " " + _m("empty_sector", name=name),
            "\n".join(b), f"/{LANG}/branche/{d}/", _.divisions, leaf=name,
            # a Branche without a single award is not worth an index entry (its tenders list is)
            robots="" if rows else "noindex", lastmod=newest(rows, now)))
    return n_all


# --------------------------------------------------------------- section index

# A letter page with fewer entries than this is thin: noindex (out of the sitemap), its links still followed
LETTER_MIN = 30
# the letter pages of each split index, for the search page's A–Z: path -> [(letter, its page)]
LETTERS: dict = {}


def letter_groups(items: list) -> dict:
    groups = collections.defaultdict(list)
    for sl, name, n in items:
        # folded, so É files under E and Ö under O instead of after Z
        first = (re.sub(r"^[^0-9a-z]+", "", fold(name.strip()))[:1] or "#").upper()
        groups["0–9" if first.isdigit() else (first if first.isalpha() else "#")].append((sl, name, n))
    return groups


def letter_slug(g: str, taken: set) -> str:
    """'a' … 'z', '0-9', 'andere' ('#'): the letter's page under the index; never the slug of an entry
    of the same section (none has one or two characters; if one ever had, the letter gives way)."""
    sl = {"0–9": "0-9", "#": "andere"}.get(g, g.lower())
    return sl if sl not in taken else sl + "-az"


def az_label(g: str) -> str:
    """A letter group as the reader sees it: 'Andere' / 'Autres' for the names that start with no letter or digit
    (fix round 1: it read '#')."""
    return _m("az_other") if g == "#" else g


def az_grid(path: str, letters: list, groups: dict, slugs: dict, here: str = "") -> str:
    return ('<ul class="az">' + "".join(
        f'<li><a href="{BASE}/{LANG}{path}{slugs[g]}/"{" aria-current=" + chr(34) + "page" + chr(34) if g == here else ""}>'
        f'{e(az_label(g))}<small>{formato.count(len(groups[g]))}</small></a></li>' for g in letters) + "</ul>")


def build_index(path: str, kicker: str, h1: str, lead: str, items: list,
                title: str, desc: str, top: str = "", extra: str = "", lastmod: str = "", split: str = "",
                cells: str = "") -> None:
    """The root of each section. Without one the URL is a 404 in production (the local
    server's directory listing hides this), and the leaves lose their nearest hub. top: HTML under
    the title (the way to the Branchen on the Bereiche index); extra: HTML after the list (the awards
    without a canton on the canton index).
    split ('companies', 'buyers'; step 3b, 15.10.2026): the index becomes the grid of letters and each
    letter a page of its own — the company index was 479 KB and 179'000 px on a phone. Stable URLs
    (/de/unternehmen/a/), no JavaScript; a letter with fewer than LETTER_MIN entries is noindex.
    Fix round 2: one A–Z component (.az, with each letter's count) on every index, the letter lists in two columns
    from 1000 px (.azl); cells: the whole index as a grid instead of the letters (the 26 cantons)."""
    groups = letter_groups(items)
    letters = sorted(groups)

    def row(sl, name, n):
        return (f'<li><div class="row"><a href="{BASE}/{LANG}{path}{e(sl)}/">{e(name)}</a>'
                f'<span class="sub num">{zuschlag(n)}</span></div></li>')
    eyebrow = _m("az_eyebrow") if split else kicker
    head = (f'<div class="title"><div><p class="eyebrow">{e(eyebrow)}</p><h1>{e(h1)}</h1>'
            f'<p class="sum">{e(lead)}</p></div>'
            f'<dl class="rail"><dt>{_.entries}</dt><dd class="num">{formato.count(len(items))}</dd></dl></div>')
    if split:
        taken = {sl for sl, _n, _k in items}
        slugs = {g: letter_slug(g, taken) for g in letters}
        LETTERS[path] = [(g, slugs[g]) for g in letters]
        b = [head, top, f'<div class="sec"><h2 class="sr">{e(_m("az_" + split))}</h2>'
             f'<p class="sub m14">{e(_m("letters_lead"))}</p>{az_grid(path, letters, groups, slugs)}</div>']
        if extra:
            b.append(extra)
        write(f"/{LANG}{path}index.html", page(title, desc, "\n".join(x for x in b if x), f"/{LANG}{path}", kicker,
                                               lastmod=lastmod))
        for i, g in enumerate(letters):
            rows = sorted(groups[g], key=lambda x: fold(x[1]))
            here = f"/{LANG}{path}{slugs[g]}/"
            gl = az_label(g)
            pn = []
            if i:
                pn.append(f'<a class="tag" href="{BASE}/{LANG}{path}{slugs[letters[i - 1]]}/" rel="prev">'
                          f'<span aria-hidden="true">← </span>{e(_m("letter_prev"))}{lingue.COLON[LANG]} {e(az_label(letters[i - 1]))}</a>')
            if i + 1 < len(letters):
                pn.append(f'<a class="tag" href="{BASE}/{LANG}{path}{slugs[letters[i + 1]]}/" rel="next">'
                          f'{e(_m("letter_next"))}{lingue.COLON[LANG]} {e(az_label(letters[i + 1]))}<span aria-hidden="true"> →</span></a>')
            body = [f'<div class="title"><div><p class="eyebrow">{e(eyebrow)}</p>'
                    f'<h1>{e(_m("letter_" + split + "_h1", l=gl) if g != "#" else _m("letter_" + split + "_h1_other"))}</h1></div>'
                    f'<dl class="rail"><dt>{_.entries}</dt><dd class="num">{formato.count(len(rows))}</dd></dl></div>',
                    f'<nav aria-label="{e(_m("az_" + split))}">{az_grid(path, letters, groups, slugs, g)}</nav>',
                    f'<div class="sec"><div class="runhead"><h2>{e(gl)}</h2><span>{formato.count(len(rows))}</span></div>'
                    f'<ul class="plain azl">' + "".join(row(*r) for r in rows) + "</ul></div>",
                    f'<div class="pn">{"".join(pn)}</div>']
            other = g == "#"
            write(f"{here}index.html", page(
                first_fit(_m("letter_" + split + "_h1_other") if other else _m("letter_" + split + "_title", l=gl),
                          _m("letter_" + split + "_h1", l=gl)),
                _m("letter_" + split + "_desc_other", n=formato.count(len(rows))) if other
                else _m("letter_" + split + "_desc", n=formato.count(len(rows)), l=gl), "\n".join(body), here, kicker, leaf=gl,
                robots="" if len(rows) >= LETTER_MIN else "noindex", lastmod=lastmod))
        return
    b = [head]
    if top:
        b.append(top)
    if cells:
        b.append(cells)
    else:
        b.append('<ul class="az">' + "".join(f'<li><a href="#{e(g)}">{e(az_label(g))}<small>{formato.count(len(groups[g]))}</small></a></li>'
                                             for g in letters) + "</ul>")
        for g in letters:
            rows = sorted(groups[g], key=lambda x: fold(x[1]))
            b.append(f'<div class="sec" id="{e(g)}"><div class="runhead"><h2>{e(az_label(g))}</h2>'
                     f'<span>{formato.count(len(rows))}</span></div><ul class="plain azl">')
            for sl, name, n in rows:
                b.append(row(sl, name, n))
            b.append("</ul></div>")
    if extra:
        b.append(extra)
    write(f"/{LANG}{path}index.html", page(title, desc, "\n".join(b), f"/{LANG}{path}", kicker,
                                           lastmod=lastmod))


# ------------------------------------------------------------- home & sitemap

def finder(n_all: int, n_pages: int, cls: str = "", az: bool = True, kind: str = "u") -> str:
    """The company finder (step 3b, 15.10.2026; the home's door 'Unternehmen finden' was a link to the A–Z):
    the search, limited to companies (t=u), with the header's engine. Without JavaScript it opens the
    search page, whose A–Z directories lead to every company. kind 'b': the authorities' finder, on their index
    (fix round 1)."""
    sfx = "" if kind == "u" else "_b"
    return (f'<form class="finder{" " + cls if cls else ""}" role="search" action="{BASE}/{LANG}/suche/">'
            f'<label class="dh" for="finder">{e(_m("door_companies_h" if kind == "u" else "door_buyers_h"))}</label>'
            f'<div class="row2"><input id="finder" name="q" placeholder="{e(_m("finder_ph" + sfx))}" aria-describedby="finder-sub">'
            f'<input type="hidden" name="t" value="{kind}"><button>{e(_.search_go)}</button></div>'
            f'<span class="dsub" id="finder-sub">{e(_m("finder_sub" + sfx, n=formato.count(n_all), k=formato.count(n_pages)))}'
            + (f' <a href="{BASE}/{LANG}/unternehmen/">{e(_m("finder_az"))}</a>' if az else "") + "</span></form>")


def build_search_page() -> None:
    """/xx/suche/ (step 3b): where the header's search leads without JavaScript, and the full results with
    it (?q=, live). Its directories reach every entry of the register without a script: companies and
    authorities from A to Z (their letter pages), the cantons, the Branchen, the Bereiche, the open
    tenders. noindex: a search page is no answer of its own."""
    def grid(path: str) -> str:
        return '<ul class="az">' + "".join(f'<li><a href="{BASE}/{LANG}{path}{sl}/">{e(az_label(g))}</a></li>'
                                           for g, sl in LETTERS.get(path, [])) + "</ul>"
    links = [(f"/{LANG}/ausschreibungen/", _p.open_tenders_h1), (f"/{LANG}/kanton/", _i.all_cantons),
             (f"/{LANG}/branche/", _i.all_divisions), (f"/{LANG}/bereich/", _i.all_sectors),
             (f"/{LANG}/ausschreibungen/abo/", _m("abo_cta")), (f"/{LANG}/ueber/", _.nav_about)]
    b = [f'<div class="title"><div><h1>{e(_m("search_title"))}</h1><p class="sum">{e(_m("search_lead"))}</p></div></div>',
         f'<form class="search-page" role="search" action="{BASE}/{LANG}/suche/"><label for="sq">{e(_m("search_label"))}</label>'
         f'<input id="sq" type="search" name="q"><button>{e(_.search_go)}</button></form>',
         # with a query in the address the results' place is kept from the first paint (fix round 1: the
         # directories below jumped down when the results arrived, CLS 0.21-0.44)
         '<div id="treffer"></div><script>if(/[?&]q=[^&]/.test(location.search))'
         'document.getElementById("treffer").className="wait"</script>',
         f'<div class="sec search-dirs" id="verzeichnisse"><h2 class="pr30">{e(_m("search_dirs"))}</h2>'
         f'<noscript><p>{e(_m("search_nojs"))}</p></noscript>'
         f'<h3>{e(_m("az_companies"))}</h3>{grid("/unternehmen/")}'
         f'<h3>{e(_m("az_buyers"))}</h3>{grid("/auftraggeber/")}'
         '<ul class="plain mt10">' + "".join(f'<li><a href="{BASE}{h}">{e(t)}</a></li>' for h, t in links) + "</ul></div>"]
    write(f"/{LANG}/suche/index.html", page(
        first_fit(f"{_m('search_title')}\u00a0– {_.site}", _m("search_title")), _m("search_desc"), "\n".join(b),
        f"/{LANG}/suche/", leaf=_.search, robots="noindex", scripts=("suche",)))


# The arrow of the home's buttons and links (step 4); the data pages' buttons carry none (bytes)
ARROW = ('<svg class="ar" viewBox="0 0 20 12" aria-hidden="true"><path d="M0 6h17M12.5 1.2 17.6 6l-5.1 4.8" fill="none" '
         'stroke="currentColor" stroke-width="1.6"/></svg>')
# the halftone lattice of Switzerland, rasterised once from the official 2026 boundaries (reticolo.py)
LATTICE = json.loads((ROOT / "reticolo.json").read_text(encoding="utf-8")) if (ROOT / "reticolo.json").exists() else None


def home_map(opens: list) -> str:
    """01 · the open tenders per canton on the halftone map (step 4, design A2). Without JavaScript the map is
    an SVG of the dotted outline, and the 26 cantons are a list of links with their counts: the keyboard's path
    and the screen reader's, the same as the hub's list. With it, js/home.js draws the lattice from the JSON
    below (the dots of each canton, from reticolo.json; the counts, names and links of this build)."""
    oc = collections.Counter(k for t in opens for k in (t.get("_cants") or []))
    order = sorted(CANTONS, key=lambda c: (-oc.get(c, 0), fold(canton_name_or(c, c))))
    noun = lingue.OPEN_TENDERS[LANG]
    kl = "".join(f'<li><a href="{BASE}/{LANG}/ausschreibungen/{c}/" data-k="{c}"><span><abbr title="{e(canton_name_or(c, c))}">{c}</abbr>'
                 f'<span class="sr"> {e(canton_name_or(c, c))}</span></span><b data-oc="k:{c}">{formato.count(oc.get(c, 0))}</b></a></li>'
                 for c in order)
    fb, data = "", ""
    if LATTICE:
        L_ = LATTICE
        cols, rows = L_["cols"], L_["rows"]
        fb = (f'<svg class="mapfb" viewBox="0 0 {cols} {rows}"><defs><pattern id="dotA" width="1" height="1" patternUnits="userSpaceOnUse">'
              '<circle cx=".5" cy=".5" r=".27" fill="#c9a24e" fill-opacity=".55"/></pattern>'
              f'<mask id="lkA" maskUnits="userSpaceOnUse" x="0" y="0" width="{cols}" height="{rows}"><rect width="{cols}" height="{rows}" fill="#fff"/>'
              f'<path d="{L_["lakes"]}" fill="#000"/></mask></defs>'
              f'<path d="{L_["outline"]}" fill="url(#dotA)" fill-rule="evenodd" mask="url(#lkA)"/></svg>')
        d = {"cols": cols, "rows": rows, "order": L_["order"], "packed": L_["packed"], "anchors": L_["anchors"],
             "k": {c: [oc.get(c, 0), canton_name_or(c, c), f"{BASE}/{LANG}/ausschreibungen/{c}/"] for c in L_["order"]},
             "total": len(opens)}
        data = ('<script type="application/json" id="karte">'
                + json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c") + "</script>")
    return (f'<section class="band mapsec pin" aria-labelledby="open-cantons"><div class="stage"><div class="in">'
            f'<header class="sh"><p class="eyebrow">{e(_m("map_eyebrow", d=formato.date(DATA_DATE)))}</p>'
            f'<h2 id="open-cantons" data-split>{e(_m("open_by_canton_h2"))}<span class="dot" aria-hidden="true">.</span></h2>'
            f'<p class="lede"><span class="hf">{e(_m("open_canton_lede", date=formato.date(DATA_DATE)))}</span>'
            f'<span class="hc">{e(_m("open_canton_lede_tap"))}</span></p></header>'
            '<div class="mapgrid"><div>'
            f'<div class="mapbox" aria-hidden="true">{fb}<div class="tip"><b></b><span></span></div></div>'
            # the legend's scale, from none to the canton with the most (fix round 1)
            f'<p class="maplegend"><span class="sc"><b>0</b><span class="ramp" aria-hidden="true"></span>'
            f'<b data-oc="mx">{formato.count(max(oc.values(), default=0))}</b></span><span>{e(_m("map_legend"))}</span>'
            f'<span>{e(_m("map_hint"))}</span></p><p class="mapsrc">{e(_m("map_src"))}</p></div>'
            f'<div class="ro"><p class="rk">{e(_m("map_ch"))}</p><b class="nm">{e(_m("map_all"))}</b>'
            f'<p class="vl"><b data-oc="*">{formato.count(len(opens))}</b><span>{e(noun[0 if len(opens) == 1 else 1])}</span></p>'
            f'<p class="cum">{e(_m("stand", d=formato.date(DATA_DATE)))}</p><div class="bar" aria-hidden="true"><i></i></div>'
            f'<p class="go"><a href="{BASE}/{LANG}/ausschreibungen/">{e(lingue.i("all_open", LANG))}</a></p>'
            f'<ol class="kl" aria-label="{e(_m("map_list"))}">{kl}</ol></div></div></div></div>{data}</section>')


def home_sky(awards: list) -> str:
    """The hero's brass pillars: the awards per month, the incomplete months hatched, the busiest complete
    month brightest and named (decoration: the chart of section 02 says the same in full)."""
    ser = sorted(per_month(awards, until=CUR_MONTH).items())
    if not ser:
        return ""
    part = {k for k, _v in ser if k < FULL_FROM or (k == CUR_MONTH and CUR_PARTIAL)}
    peaks = grafici.peak_months(ser, part)
    top = max(v for _k, v in ser) * 1.04 or 1
    out = []
    for k, v in ser:
        cls = "p" if k in part else ("pk" if peaks and k == peaks[0] else "")
        lab = (f'<span class="pkl"><b>{formato.count(v)}</b>{e(_m("sky_peak", m=formato.month(k)))}</span>'
               if peaks and k == peaks[0] else "")
        out.append(f'<i{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} style="--h:{100 * v / top:.1f}%">{lab}</i>')
    return "".join(out)


def build_home(pages: dict, comp: dict, awards: list, opens: list, cant_list, cpv_list) -> None:
    """The home in design A2 "Brass" (step 4, 15.10.2026, as the owner approved it): the question and its two
    doors (the open tenders, the company finder) over the brass pillars of the awards per month; 01 the open
    tenders per canton on the halftone map; the key figures; 02 the awards per month; 03 the companies with the
    most awards beside the next deadlines; 04 the awards by industry; the alarm band. The H1 is there at first
    paint; js/home.js adds the motion and the map's canvas, the content is complete without it."""
    months = sorted({(a.get("publicationDate") or "")[:7] for a in awards if a.get("publicationDate")})
    span = formato.period(months[0], months[-1]) if months else ""
    winners_all = collections.Counter(slug(w) for a in awards for w in winners(a))
    # the 8 nearest deadlines, and 16 more in reserve, hidden: by the evening the 8 of the morning's build
    # may all have passed, and /stand.js shows the next ones in their place (step 3b)
    soon = lot_groups(sorted((t for t in opens if t.get("offerDeadline")),
                             key=lambda t: t["offerDeadline"]))[:24]
    # 'Neu' (step 3a, 14.10.2026) = first published (-01, a correction is not new) on the latest day simap
    # published tenders, and the label names that day: 'seit gestern' was wrong after a missed run
    day = LATEST_TENDER_DAY[0]
    fresh_n = sum(1 for t in opens if day and t.get("_first") == day)
    d_short = formato.date_short(day) if day else ""
    new_txt = ((_m("door_new_one", d=d_short) if fresh_n == 1 else _m("door_new", m=formato.count(fresh_n), d=d_short))
               if fresh_n else "")
    noun = lingue.OPEN_TENDERS[LANG][0 if len(opens) == 1 else 1]
    abo = f"{BASE}/{LANG}/ausschreibungen/abo/"
    dot = '<span class="dot" aria-hidden="true">.</span>'

    # the hero: the question (its last sign in brass), who the site is for, the alert; the pillars; the doors
    tag = _p.tagline
    h1 = (e(tag[:-1]) + f'<span class="dot">{e(tag[-1])}</span>') if tag[-1:] in ("?", ".") else e(tag)
    # the door of the open tenders (fix round 1): the count is the link and covers the door; 'N neue' links to the
    # list's 'Neu' filter
    door1 = (f'<div class="door d1"><span class="k" aria-hidden="true">{e(_.nav_tenders)}</span>'
             f'<a class="big" href="{BASE}/{LANG}/ausschreibungen/"><b data-oc="*">{formato.count(len(opens))}</b> '
             f'<span class="lbl">{e(noun)}</span></a>'
             + (f'<a class="dnew" href="{BASE}/{LANG}/ausschreibungen/?neu=1#fristen" rel="nofollow" data-day="{day}" '
                f'data-n="{fresh_n}">{e(new_txt)}</a>' if new_txt else "")
             + f'<span class="sub">{e(_m("door_open_sub"))}</span>{ARROW}</div>')
    # 'Unternehmen finden' is the company finder since step 3b: the search, limited to companies
    door2 = finder(len(winners_all), len(pages), "door d2").replace(
        ">", f'><span class="k" aria-hidden="true">{e(_.search)}</span>', 1)
    b = [f'<section class="band hero" data-rest=".72,.36" aria-labelledby="h1"><div class="recede">'
         f'<div class="bg" aria-hidden="true"><div class="vign"></div><div class="ghost" data-depth=".22">{formato.count(len(awards))}</div></div>'
         '<div class="glow" aria-hidden="true"></div><div class="in hero-in"><div class="copy">'
         f'<p class="eyebrow">{e(_m("home_eyebrow", span=span, d=formato.date(DATA_DATE)))}</p>'
         f'<h1 id="h1">{h1}</h1><p class="aud">{e(_m("audience"))}</p><p class="lead">{e(_p.lead)}</p>'
         f'<p class="ctas"><a class="btn" href="{abo}">{e(_m("abo_cta"))}{ARROW}</a></p></div>'
         f'<div class="sky" data-depth=".55" aria-hidden="true">{home_sky(awards)}</div>'
         # the horizon moves with the pillars it underlines (fix round 2: .85 against their .55 drifted 3-5 px apart)
         f'<div class="doors"><span class="horizon" data-depth=".55" aria-hidden="true"></span>{door1}{door2}'
         f'<p class="hmeta">{e(_.source)}<br><b>simap.ch</b></p></div></div></div><div class="shade"></div></section>']
    b.append(home_map(opens))

    # the key figures; the tiles that have a page behind them lead there (the companies tile says how many of
    # them have a page, the number the finder and the index give)
    nfirms = len(winners_all)
    firms_lab = (_m("home_firms_tile", k=formato.count(len(pages))) if nfirms != 1 else _m("home_firms_tile_one"))
    b.append(f'<section class="band stats" aria-label="{e(_m("key_figures"))}"><div class="in"><div class="figures">'
             f'<div class="fig" data-up><b><data value="{len(awards)}" id="total">{formato.count(len(awards))}</data></b>'
             f'<span>{lab_n(len(awards), "awards")}</span></div>'
             f'<a class="fig" href="{BASE}/{LANG}/unternehmen/" data-up style="--d:.08s"><b>{formato.count(nfirms)}</b>'
             f'<span>{e(firms_lab)}</span></a>'
             + sum_tile(awards)
             + f'<a class="fig" href="{BASE}/{LANG}/ausschreibungen/" data-up style="--d:.24s"><b data-oc="*">{formato.count(len(opens))}</b>'
             f'<span>{e(_m("open_kpi_open"))}</span></a></div>'
             f'<dl class="rail"><div><dt>{_.source}</dt><dd>{e(_p.source_note)}</dd></div>'
             + (f"<div><dt>{_.period}</dt><dd>{e(span)}</dd></div>" if span else "")
             + f"<div><dt>{_.updated}</dt><dd>{tt(DATA_DATE, formato.date(DATA_DATE))}</dd></div></dl></div></section>")

    # 02 · the awards per month: the chart as everywhere, its panel set apart under the heading
    fig = month_chart(awards, _i.mc_title_home, csv="/daten/monate.csv")
    if '<p class="unit"' in fig:
        fig = (fig.replace('<h2 id="chart-months">', '<h2 id="chart-months" data-split>', 1)
                  .replace("</h2>", f"{dot}</h2>", 1)
                  .replace('<div class="mch">', '<div class="mcp" data-up><div class="mch">', 1)
                  .replace("</figure>", "</div></figure>", 1))
    b.append(f'<section class="band hsec" id="monate" aria-labelledby="chart-months"><div class="in">'
             f'<p class="eyebrow">{e(_m("sec_awards"))}</p>{fig}</div></section>')

    # 03 · the companies with the most awards (no canton column since step 3a: it read as the firm's seat),
    # beside the next deadlines
    rank = [(s, p) for s, p in sorted(pages.items(), key=lambda kv: (-kv[1]["n"], -kv[1]["value"]))][:25]
    unit = formato.unit_for(p["value"] for _s, p in rank)
    t = [f'<div class="scroll"><table class="top u{unit}">{cap(_i.firms_cap)}<thead><tr><td class="n0"></td>'
         f'<th>{_.company}</th><th class="r">{_.awards}</th>{money_th("sum_l", unit)}</tr></thead><tbody>']
    for i, (s, p) in enumerate(rank, 1):
        t.append(f'<tr><td class="n0">{i:02d}</td><td><a href="{BASE}/{LANG}/unternehmen/{e(s)}/">{e(p["name"])}</a>'
                 + (f'<span class="sub sb2">{e(short_sector(p["sector"], 46))}</span>' if p["sector"] else "")
                 + f'</td><td class="r num">{formato.count(p["n"])}</td>'
                 f'<td class="r num">{formato.column_cell(p["value"] or None, unit, empty_sr=_.no_own_amount)}</td></tr>')
    t.append("</tbody></table></div>")
    dl = []
    if soon:
        dl.append('<ul class="plain tl" data-show="8">')
        single = distinct_titles([de(g[0], "title") for _stem, g in soon], 66)
        for k_, ((stem, g), one) in enumerate(zip(soon, single)):
            t0 = g[0]
            dln = t0["offerDeadline"]
            if len(g) > 1:
                # the shared project name; '· 6 Lose' never starts a line of its own; the link opens the
                # first lot, whose page lists the others
                text = (name_cut(stem, 70) + " · " + _if("lots_n", n=formato.count(len(g))).replace(" ", " "))
            else:
                text = one
            cls, when = due_cell(dln, formato.date_short(dln), soon=True)
            more = " data-more hidden" if k_ >= 8 else ""
            dl.append(f'<li data-deadline="{e(dln)}"{more}><div class="row"><a href="{BASE}/{LANG}/auftrag/{e(t0.get("projectId"))}/"{la(t0)}>'
                      f'{e(text)}</a><span class="when{cls}">{when}</span></div></li>')
        dl.append("</ul>")
    b.append(f'<section class="band hsec" id="unternehmen" aria-labelledby="h-top"><div class="in">'
             f'<header class="sh"><p class="eyebrow">{e(_m("sec_companies"))}</p>'
             f'<h2 id="h-top" data-split>{e(_i.firms_cap)}{dot}</h2><p class="aside">{e(span)}</p></header>'
             f'<div class="two"><div data-up>{"".join(t)}'
             f'<a class="more" href="{BASE}/{LANG}/unternehmen/">{e(_i.all_companies)}{ARROW}</a></div>'
             f'<aside class="aside-col" aria-labelledby="h-dl" data-up style="--d:.1s"><div class="sub-h"><h3 id="h-dl">{e(_i.next_deadlines)}</h3>'
             f'<span>{oc_text(_if("open_count", n=NUL), len(opens), "*")}</span></div>{"".join(dl)}'
             f'<a class="more" href="{BASE}/{LANG}/ausschreibungen/">{e(lingue.i("all_open", LANG))}{ARROW}</a></aside></div></div></section>')

    # 04 · the awards by Branche (division), each linking to its page
    divs = collections.Counter(str(a.get("cpvCode") or "")[:2] for a in awards
                               if str(a.get("cpvCode") or "")[:2] in lingue.CPV_SHORT[LANG])
    top8 = sorted(divs.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
    mx = top8[0][1] if top8 else 1
    ber = "".join(f'<li><a href="{BASE}/{LANG}/branche/{d}/">{e(div_name(d))}</a><span class="v num">{formato.count(k)}</span>'
                  f'<span class="t" aria-hidden="true"><i style="width:{100 * k / mx:.1f}%"></i></span></li>' for d, k in top8)
    b.append(f'<section class="band hsec" id="branchen" aria-labelledby="h-br"><div class="in">'
             f'<header class="sh"><p class="eyebrow">{e(_m("sec_divisions"))}</p>'
             f'<h2 id="h-br" data-split>{e(_i.by_division_awards)}{dot}</h2>'
             f'<p class="aside">{formato.count(len(lingue.CPV_SHORT[LANG]))} {_.divisions_n}</p></header>'
             f'<ul class="ber" data-up>{ber}</ul><a class="more" href="{BASE}/{LANG}/branche/">{e(_i.all_divisions)}{ARROW}</a>'
             '</div></section>')

    # the alarm band in brass, then every section of the register
    b.append(f'<section class="band alarm" aria-labelledby="h-alarm"><div class="in">'
             f'<p class="eyebrow">{e(_m("alarm_eyebrow"))}</p><h2 id="h-alarm" data-split>{e(_m("alarm_h2"))}{dot}</h2>'
             # how it works, not the promise a third time (fix round 2: eyebrow, heading and this line all said 'free, by
             # e-mail'); the number once, its caption without it
             f'<p class="s">{e(_m("alarm_sub"))}</p><p class="ctas"><a class="btn" href="{abo}">{e(_m("alert_link"))}{ARROW}</a></p>'
             + (f'<p class="since" data-up><b aria-hidden="true">{formato.count(fresh_n)}</b><span><em class="sr">'
                f'{formato.count(fresh_n)} </em>{e(_m("alarm_since_one" if fresh_n == 1 else "alarm_since", d=d_short))}</span></p>'
                if fresh_n else "")
             + "</div></section>")
    b.append('<div class="band endband"><div class="in"><div class="tags">'
             f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/">{e(_p.open_tenders_h1)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/unternehmen/">{e(_i.all_companies)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/auftraggeber/">{e(_i.all_buyers)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/kanton/">{e(_i.all_cantons)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/branche/">{e(_i.all_divisions)}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/bereich/">{e(_i.all_sectors)}</a>'
             f'<a class="tag" href="{abo}">{e(_m("abo_cta"))}</a></div></div></div>')

    write(f"/{LANG}/index.html", page(
        _m("home_title"), _m("home_desc", n=formato.count(len(awards))),
        "\n".join(b), f"/{LANG}/", fresh=True,
        head_extra=(HOME_PRELOAD.format(base=BASE) + site_ld() + feed_head(f"/{LANG}/ausschreibungen/feed.xml", _m("feed_all"))
                    + f"<style>{css_min(HOME_CSS)}</style>\n"),
        lastmod=newest(awards, opens), scripts=("home",)))




OPERATOR_NAME = "Riccardo Di Lullo"
# the register's own address, which forwards to the operator: the personal Gmail address stood in
# the legal notice (audit 13.10.2026)
OPERATOR_EMAIL = ABO_MAIL


def sentences(text: str, limit: int = 155) -> str:
    """As many whole sentences from the start as fit: a legal page's description ended
    '…steht in keiner Verbindung zu simap.ch oder zu…' (verifier, 28.09.2026)."""
    text = _ws(text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = ""
    for x in parts:
        nxt = f"{out} {x}".strip()
        if len(nxt) > limit:
            break
        out = nxt
    return out or fit_desc(text, limit)


# The register as an organisation and a website, for search engines (14.10.2026): name, address on
# the web, logo, e-mail — no postal address. No SearchAction until the site has a search.
ORG_NAME = "auftragsregister.ch"


def org_ld() -> dict:
    return {"@type": "Organization", "@id": f"{ORIGIN}/#org", "name": ORG_NAME, "url": f"{ORIGIN}/",
            "logo": f"{ORIGIN}/icon-512.png", "email": ABO_MAIL}


def site_ld() -> str:
    """WebSite and Organization, on the home pages. One WebSite for the four languages: its address is
    the domain's root, its other names the register's in the other languages and the domain (step 3a)."""
    names = [lingue.t("site", l) for l in LANGS]
    return ld_script({"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": f"{ORIGIN}/#website", "name": _.site, "url": f"{ORIGIN}/",
         "alternateName": [ORG_NAME] + [n for n in dict.fromkeys(names) if n != _.site],
         "inLanguage": LANG, "publisher": {"@id": f"{ORIGIN}/#org"},
         # the site's search (step 3b): /xx/suche/?q=
         "potentialAction": {"@type": "SearchAction",
                             "target": {"@type": "EntryPoint", "urlTemplate": f"{ORIGIN}/{LANG}/suche/?q={{search_term_string}}"},
                             "query-input": "required name=search_term_string"}},
        org_ld()]})


# The licence the Dataset names (step 3a, 14.10.2026): the register grants none of its own; reuse is
# governed by simap.ch's terms of use for its API (read 04.09.2026 at this address), which the about
# page explains
SIMAP_TERMS = "https://www.simap.ch/de/about/legal"


def dataset_ld(u: dict) -> str:
    """The register as a Dataset, on the about pages: what it covers (since the archive's first
    month, Switzerland), what it is built from (simap.ch), the terms that govern its reuse (simap's:
    SIMAP_TERMS, the about page says so) and the CSV files it offers, one per canton and one for the
    awards without a canton. One @id for the four language versions."""
    files = sorted(k for k in _CSV_DONE if k.startswith("/daten/kanton/"))
    return ld_script({
        "@context": "https://schema.org", "@type": "Dataset", "@id": f"{ORIGIN}/#dataset",
        "name": f"{_.site} – {_.awards}",
        "description": _ws(u["lead"] + " " + u["sections"][0][2][0]),
        "url": f"{ORIGIN}/{LANG}/ueber/", "inLanguage": LANG, "license": SIMAP_TERMS,
        "creator": org_ld(), "isAccessibleForFree": True,
        "temporalCoverage": f"{RAMP_START or CUR_MONTH}/{DATA_DATE}",
        "spatialCoverage": {"@type": "Country", "name": lingue.COUNTRY[LANG]},
        "isBasedOn": "https://www.simap.ch", "dateModified": DATA_DATE,
        "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv",
                          "name": (canton_name_or(k.rsplit("/", 1)[-1][:-4], "") if not k.endswith("ohne-kanton.csv")
                                   else _.no_canton),
                          "contentUrl": f"{ORIGIN}{k}"} for k in files]})


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
        f"{imp['title']}\u00a0– {_.site}", sentences(imp["paras"][0][1]),
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
        f"{pr['title']}\u00a0– {_.site}", sentences(pr["paras"][0][1]),
        "\n".join(b), f"/{LANG}/datenschutz/", _.register, pr["title"]))


def incomplete_note(u: dict) -> str:
    """' 107 Zuschlagspublikationen aus Juli 2026 kamen … ohne Titel und ohne Zuschlagsempfänger an …'
    (load(): left out of every figure), '' when there are none."""
    if not INCOMPLETE:
        return ""
    months = sorted({(a.get("publicationDate") or "")[:7] for a in INCOMPLETE if a.get("publicationDate")})
    return u["incomplete"].format(n=formato.count(len(INCOMPLETE)),
                                  months=formato.month_list(months) if len(months) > 1
                                  else formato.month(months[0], full=True) if months else "")


def nocant_sentence(u: dict, k: int) -> str:
    """The Über page's sentence on the awards without a canton: none, one, or a count that opens the sentence in
    words (fix round 2: '2 Zuschläge nennen …')."""
    return u["nocant_zero"] if not k else u["nocant_one"] if k == 1 else u["nocant"].format(n=awards_start(k))


def build_about(awards: list, opens: list) -> None:
    """About the register and its methodology (/xx/ueber/; audit 13.10.2026: "Über/Methodik" was
    missing). Every figure on it comes from the build: the archive's span and its incomplete first
    months (the charts' FULL_FROM), the page thresholds, the days an expired tender stays online."""
    u = lingue.UEBER[LANG]
    ramp = ""
    if RAMP_START and FULL_FROM and RAMP_START < FULL_FROM:
        ramp = u["ramp"].format(a=formato.month(RAMP_START, full=True), b=formato.month(RAMP_END, full=True),
                                full=formato.month(FULL_FROM, full=True))
    cols = ", ".join(CSV_COLS)
    kw = dict(stand=_m("stand", d="…").split("…")[0].strip(" :\u202f"), date=formato.date(DATA_DATE),
              awards=formato.count(len(awards)), open=formato.count(len(opens)),
              start=formato.month(RAMP_START or CUR_MONTH, full=True), ramp=ramp,
              min_c=spelled(MIN_AWARDS), min_b=spelled(3), min_s=spelled(3),
              days=formato.count(EXPIRED_DAYS), expired=_.tender_expired, since=formato.date(TENDERS_SINCE[0]),
              matched=_p.matched_tenders, similar=_i.similar_h, mail=ABO_MAIL, cols=cols,
              csv_pages=u["csv_pages"] if CSV_COMPANIES else u["csv_pages_nocomp"],
              # step 3a: the licence, the incomplete publications, the canton rule and the unit rates
              terms=SIMAP_TERMS.split("//", 1)[1].replace("www.", ""),
              incomplete=incomplete_note(u), multi=_.multi_cantons, fallback=_.fb_note,
              nocant=nocant_sentence(u, sum(1 for a in awards if not a.get("canton"))),
              rate=_.rate_flag, report=_.report_error)
    b = [f'<div class="title"><div><p class="eyebrow">{e(_m("about_eyebrow"))}</p><h1>{e(u["h1"])}</h1>'
         f'<p class="sum">{e(u["lead"])}</p></div>'
         f'<dl class="rail"><dt>{e(_.source)}</dt><dd><a href="https://www.simap.ch">simap.ch</a></dd>'
         f'<dt>{_.updated}</dt><dd>{tt(DATA_DATE, formato.date(DATA_DATE))}</dd>'
         # 'Kontakt und Fehlermeldungen' (fix round 1): what the address is for
         f'<dt>{e(_.contact_errors)}</dt><dd><a href="mailto:{ABO_MAIL}">{ABO_MAIL}</a></dd></dl></div>',
         # the sections at a glance, for a page this long: where the footer's 'Methodik' leads (fix round 1: it led
         # to the section on how names are merged)
         '<div class="tags" id="methodik" style="margin:22px 0 0">'
         + "".join(f'<a class="tag" href="#{sid}">{e(h)}</a>' for sid, h, _b in u["sections"]) + "</div>",
         '<div class="sec prose" style="padding-top:8px">']
    for sid, h, blocks in u["sections"]:
        b.append(f'<h2 id="{sid}" style="margin:34px 0 10px">{e(h)}</h2>')
        for blk in blocks:
            if isinstance(blk, list):
                b.append('<ul style="margin:0 0 15px;padding-left:20px;color:var(--muted)">'
                         + "".join(f'<li style="margin:0 0 8px">{e(x.format(**kw))}</li>' for x in blk) + "</ul>")
            else:
                # the terms of use as a link (the licence the Dataset names); the national total as a
                # value controlla.py reconciles with the home and the cantons
                para = f"<p>{e(blk.format(**kw))}</p>".replace(
                    e(kw["terms"]), f'<a href="{SIMAP_TERMS}">{e(kw["terms"])}</a>', 1)
                if sid == "aktualisierung" and "{awards}" in blk:
                    para = para.replace(e(kw["awards"]), f'<data value="{len(awards)}" id="total">{e(kw["awards"])}</data>', 1)
                b.append(para)
        if sid == "quelle":
            # the home's map: its base and its licence (step 4)
            b.append(f'<p>{e(_m("map_about"))}</p>')
        if sid == "daten":
            b.append(f'<p><a class="btn" href="{BASE}/{LANG}/ausschreibungen/abo/">{e(u["alert_link"])}</a></p>')
        if sid == "kontakt":
            b.append(f'<p><a href="mailto:{ABO_MAIL}">{ABO_MAIL}</a> · '
                     f'<a href="{BASE}/{LANG}/impressum/">{e(_.imprint)}</a> · '
                     f'<a href="{BASE}/{LANG}/datenschutz/">{e(_.privacy)}</a></p>')
    b.append("</div>")
    write(f"/{LANG}/ueber/index.html", page(
        f"{u['title']}\u00a0– {_.site}" if len(f"{u['title']}\u00a0– {_.site}") <= 64 else u["title"],
        sentences(u["lead"] + " " + u["sections"][0][2][0]),
        "\n".join(b), f"/{LANG}/ueber/", _.register, leaf=_.nav_about, fresh=True,
        head_extra=dataset_ld(u), lastmod=newest(awards, opens)))


# The two pages Brevo sends people to show ONE language (step 3a, 14.10.2026; every FR/IT/EN subscriber
# read German first): the one named by ?lang= (or Brevo's locale / SPRACHE), else the first of the
# browser's languages the site has, else German. Without JavaScript all four, as before.
# Fix round 1 (20.10.2026): the header carries the register's name in that language (it read
# 'AUFTRAGSREGISTER.CH'), the page an eyebrow and a display H1 like every other page.
ABO_STATUS_JS = """(function(){var d=document.documentElement,t=%s,s=%s,b=%s,L=['de','fr','it','en'],l='',
m=location.search.match(/[?&](?:lang|locale|sprache)=(de|fr|it|en)/i);if(m)l=m[1].toLowerCase();
if(!l){var n=navigator.languages||[navigator.language||''];for(var i=0;i<n.length&&!l;i++){var c=String(n[i]).slice(0,2).toLowerCase();if(L.indexOf(c)>=0)l=c}}
if(!l)l='de';d.lang=l;d.setAttribute('data-l',l);document.title=t[l];var k=document.querySelector('.skip');if(k)k.textContent=s[l][0];
var u=document.querySelector('.masthead summary');if(u)u.textContent=s[l][1];
var w=document.querySelector('.masthead a.name');w.href=b+'/'+l+'/';w.textContent=s[l][2];var a=document.querySelector('.langs a[lang='+l+']');if(a)a.className='on';
var c=document.querySelector('.crumbs [aria-current]');if(c)c.textContent=t[l];var r=document.querySelector('.crumbs a');if(r){r.textContent=s[l][3];r.href=b+'/'+l+'/'}
var f=document.querySelector('.masthead [role=search]'),q=%s;if(f){f.action=b+'/'+l+'/suche/';f.q.setAttribute('aria-label',q[l][0]);f.querySelector('button').textContent=q[l][1]}})();"""
ABO_STATUS_CSS = ("html[data-l] [data-nf]{display:none}"
                  + ",".join(f"html[data-l={l}] [data-nf][lang={l}]" for l in LANGS) + "{display:block}"
                  + ",".join(f"html[data-l={l}] span[data-nf][lang={l}]" for l in LANGS) + "{display:inline}"
                  ".blk{margin-top:26px}.blk p{margin:0 0 12px;max-width:33em}.blk .tags{margin-top:18px}"
                  ".blk h2{margin:1.75rem 0 .5rem;font-size:1.5rem}.blk ol{margin:0 0 12px;padding-left:1.25rem;max-width:33em}"
                  ".blk li{margin:0 0 .375rem}"
                  "span[data-nf]+span[data-nf]::before{content:' · ';content:' · '/''}"
                  "html[data-l] span[data-nf]+span[data-nf]::before{content:none}"
                  # one menu without a script: the German one (the language links lead to the others)
                  "html:not([data-l]) nav.sitenav[data-nf]:not([lang=de]){display:none}")


def build_abo_status() -> None:
    """The two pages Brevo sends people to: after the form without JavaScript (check your mail) and
    after the opt-in click (done). The redirect target is one fixed URL per form, so these live
    outside the language tree and stay out of the index. Each says, in the reader's language
    (ABO_STATUS_JS): the sender address and when the e-mails come; the check page what to do when no e-mail
    arrives and the steps ahead, the done page how to change the selection (fix round 1: the done page asked
    'Keine E-Mail erhalten?'). Without JavaScript all four."""
    mail = ABO_MAIL
    for slug_, key in (("check", "abo_check"), ("ok", "abo_ok")):
        titles = {l: lingue.m(key + "_title", l) for l in LANGS}
        spans = "".join(f'<span data-nf lang="{l}">{e(titles[l])}</span>' for l in LANGS)
        brows = "".join(f'<span data-nf lang="{l}">{e(lingue.t("nav_alert", l))}</span>' for l in LANGS)

        def body(l: str) -> str:
            frm = e(lingue.m("abo_from", l, mail=NUL)).replace(NUL, f'<a href="mailto:{mail}">{mail}</a>')
            if slug_ == "check":
                steps = "".join(f"<li>{e(lingue.m(k, l))}</li>" for k in ("abo_step1", "abo_step2", "abo_step3"))
                return (f"<p>{e(lingue.m(key, l))}</p><p>{e(lingue.m('abo_resend', l))}</p><p>{frm}</p>"
                        f"<h2>{e(lingue.m('abo_recap_h', l))}</h2><ol>{steps}</ol>")
            return (f"<p>{e(lingue.m(key, l))}</p><p>{frm}</p><p>{e(lingue.m('abo_when', l))}</p>"
                    f"<p>{e(lingue.m('abo_change', l))}</p>")
        blocks = "".join(
            f'<div class="blk" data-nf lang="{l}">' + body(l)
            + f'<div class="acts"><a class="btn" href="{BASE}/{l}/ausschreibungen/abo/">{e(lingue.m("abo_back", l))}</a>'
            f'<a class="tag" href="{BASE}/{l}/ausschreibungen/">{e(lingue.i("all_open", l))}</a></div></div>'
            for l in LANGS)
        skips = {l: [lingue.t("skip", l), lingue.t("menu", l), lingue.t("site", l), lingue.t("home", l)] for l in LANGS}
        js = ABO_STATUS_JS % (json.dumps(titles, ensure_ascii=False).replace("<", "\\u003c"),
                              json.dumps(skips, ensure_ascii=False).replace("<", "\\u003c"), json.dumps(BASE),
                              json.dumps(SEARCH_WORDS, ensure_ascii=False))
        html = ('<!doctype html>\n<html lang="de"><head><meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
                # German until the script names the reader's language (the four did not fit 65 characters)
                f'<title>{e(titles["de"])}</title>\n'
                f'<meta name="description" content="{e(lingue.m(key, "de"))}">\n'
                '<meta name="robots" content="noindex,nofollow">\n'
                + re.search(r'<link rel="icon"[^>]*>\n', HEAD).group(0).replace("{base}", BASE)
                + PRELOAD.replace("{base}", BASE)
                + f'<link rel="stylesheet" href="{BASE}/style.css">\n<style>{ABO_STATUS_CSS}</style>\n</head><body>\n'
                f'<a class="skip" href="#inhalt">{e(lingue.t("skip", "de"))}</a>\n'
                f'<header class="masthead"><a class="name" href="{BASE}/de/">{e(lingue.t("site", "de"))}</a>\n'
                f'<details><summary>{e(lingue.t("menu", "de"))}</summary></details>' + search_form("de", BASE) + "\n"
                # the menu in each language, the reader's own with the script, the German one without it
                + "".join(f'<nav class="sitenav" data-nf lang="{l}" aria-label="{e(lingue.t("nav_label", l))}"><ul>'
                          + "".join(f'<li><a href="{BASE}/{l}/{h}">{e(lingue.t(k, l))}</a></li>' for k, h in NAV)
                          + "</ul></nav>" for l in LANGS)
                + f'<nav class="langs" aria-label="{e(" · ".join(lingue.t("language", l) for l in LANGS))}">'
                + "".join(f'<a href="{BASE}/{l}/ausschreibungen/abo/" lang="{l}" hreflang="{l}">{e(NAMES[l])}</a>'
                          for l in LANGS) + "</nav>"
                + f'</header>\n<nav class="crumbs" aria-label="{e(lingue.t("crumbs_label", "de"))}"><ol>'
                f'<li><a href="{BASE}/de/">{e(lingue.t("home", "de"))}</a></li>'
                f'<li><span aria-current="page">{" · ".join(e(titles[l]) for l in LANGS)}</span></li></ol></nav>\n'
                '<main id="inhalt">\n'
                f'<div class="title"><div><p class="eyebrow">{brows}</p><h1>{spans}</h1></div></div>\n'
                + blocks + f"\n<script>{js}</script>\n</main><footer>"
                '<p class="stand"><span data-stand></span></p><p>'
                + " · ".join(f'<a href="{BASE}/{l}/datenschutz/" lang="{l}">{e(lingue.t("privacy", l))}</a>' for l in LANGS)
                + "</p><p>"
                + " · ".join(f'<a href="{BASE}/{l}/impressum/" lang="{l}">{e(lingue.t("imprint", l))}</a>' for l in LANGS)
                + f'</p></footer><script src="{BASE}/stand.js" defer></script></body></html>')
        write(f"/abo/{slug_}/index.html", html)


# The 404 page's script: the language from the path (/fr/… -> French only, its title), else the first of the
# browser's languages the site has, else German (fix round 1: at a path without a language the four menus stood
# one under the other); for a tender's address (/fr/auftrag/<id>/) the link to that project on simap.ch. Without
# it the page shows all four texts and the German menu.
NF_JS = """(function(){var d=document.documentElement,p=location.pathname,b=%s,t=%s,s=%s,L=['de','fr','it','en'];
if(b&&p.indexOf(b)===0)p=p.slice(b.length);
var m=p.match(/^\\/(de|fr|it|en)(\\/|$)/),id=p.match(/^\\/(?:de|fr|it|en)\\/auftrag\\/([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})\\/?$/),l=m?m[1]:'';
if(!l){var n=navigator.languages||[navigator.language||''];for(var i=0;i<n.length&&!l;i++){var c=String(n[i]).slice(0,2).toLowerCase();if(L.indexOf(c)>=0)l=c}}
if(!l)l='de';
d.lang=l;d.setAttribute('data-l',l);document.title=t[l];var k=document.querySelector('.skip');if(k&&s[l])k.textContent=s[l][0];
var u=document.querySelector('.masthead summary');if(u&&s[l])u.textContent=s[l][1];
var w=document.querySelector('.masthead a.name');w.href=b+'/'+l+'/';w.textContent=s[l][2];document.querySelector('.langs a[lang='+l+']').className='on';
var f=document.querySelector('.masthead [role=search]'),q=%s;if(f){f.action=b+'/'+l+'/suche/';f.q.setAttribute('aria-label',q[l][0]);f.querySelector('button').textContent=q[l][1]}
if(id)[].forEach.call(document.querySelectorAll('a[data-simap]'),function(a){
a.href='https://www.simap.ch/'+a.getAttribute('data-simap')+'/project-detail/'+id[1];a.hidden=false})})();"""
NF_CSS = ("html[data-l] .nf{display:none}"
          + ",".join(f"html[data-l={l}] .nf[lang={l}]" for l in LANGS) + "{display:block}"
          + ",".join(f"html[data-l={l}] span.nf[lang={l}]" for l in LANGS) + "{display:inline}"
          "span.nf+span.nf::before{content:' · ';content:' · '/''}html[data-l] span.nf+span.nf::before{content:none}"
          "div.nf{margin-top:26px}div.nf p{margin:0;color:var(--muted);max-width:33em}"
          ".sitenav.nf{margin-top:0}html:not([data-l]) .sitenav.nf:not([lang=de]){display:none}")


def build_404() -> None:
    """GitHub Pages answers every missing URL with /404.html, and without one it served its own
    English 'Page not found' (08.10.2026). One page for the four languages, readable as it stands;
    the script shows the reader's language only. The links are root-relative, because the page is
    served at whatever depth the missing URL had; noindex, no canonical. Fix round 1: the register's name in
    the header, an eyebrow and a display H1, one menu."""
    titles = {l: f"{lingue.m('nf_title', l)} – {lingue.t('site', l)}" for l in LANGS}
    eyebrow = "".join(f'<span class="nf" lang="{l}">{e(lingue.m("nf_eyebrow", l))}</span>' for l in LANGS)
    h1 = "".join(f'<span class="nf" lang="{l}">{e(lingue.m("nf_title", l))}</span>' for l in LANGS)
    blocks = "".join(
        f'<div class="nf" lang="{l}"><p>{e(lingue.m("nf_text", l, days=EXPIRED_DAYS, since=in_lang(l, lambda: formato.date(TENDERS_SINCE[0]))))}</p><div class="acts">'
        f'<a class="btn" href="{BASE}/{l}/ausschreibungen/">{e(lingue.i("all_open", l))}</a>'
        f'<a class="tag" href="{BASE}/{l}/">{e(lingue.m("nf_home", l))}</a>'
        f'<a class="tag" href="https://www.simap.ch/{l}/" data-simap="{l}" hidden>{e(lingue.m("nf_simap", l))}</a>'
        "</div></div>" for l in LANGS)
    skips = {l: [lingue.t("skip", l), lingue.t("menu", l), lingue.t("site", l)] for l in LANGS}
    js = NF_JS % (json.dumps(BASE), json.dumps(titles, ensure_ascii=False).replace("<", "\\u003c"),
                  json.dumps(skips, ensure_ascii=False).replace("<", "\\u003c"), json.dumps(SEARCH_WORDS, ensure_ascii=False))
    html = ('<!doctype html>\n<html lang="de"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>404 · {" · ".join(e(lingue.m("nf_title", l)) for l in LANGS)}</title>\n'
            '<meta name="robots" content="noindex">\n'
            + re.search(r'<link rel="icon"[^>]*>\n', HEAD).group(0).replace("{base}", BASE)
            + PRELOAD.replace("{base}", BASE) +
            f'<link rel="stylesheet" href="{BASE}/style.css">\n<style>{NF_CSS}</style>\n</head><body>\n'
            f'<a class="skip" href="#inhalt">{e(lingue.t("skip", "de"))}</a>\n'
            f'<header class="masthead"><a class="name" href="{BASE}/de/">{e(lingue.t("site", "de"))}</a>\n'
            f'<details><summary>{e(lingue.t("menu", "de"))}</summary></details>' + search_form("de", BASE) + "\n"
            # the menu in each language, shown like the text blocks below: the reader's own with the script, the
            # German one without it
            + "".join(f'<nav class="sitenav nf" lang="{l}" aria-label="{e(lingue.t("nav_label", l))}"><ul>'
                      + "".join(f'<li><a href="{BASE}/{l}/{h}">{e(lingue.t(k, l))}</a></li>' for k, h in NAV)
                      + "</ul></nav>" for l in LANGS)
            + f'<nav class="langs" aria-label="{e(" · ".join(lingue.t("language", l) for l in LANGS))}">'
            + "".join(f'<a href="{BASE}/{l}/" lang="{l}" hreflang="{l}">{e(NAMES[l])}</a>' for l in LANGS) + "</nav>"
            + '</header>\n<main id="inhalt">\n'
            f'<div class="title"><div><p class="eyebrow">{eyebrow}</p><h1>{h1}</h1></div></div>\n'
            + blocks + f"\n<script>{js}</script>\n</main><footer><p>"
            + " · ".join(f'<a href="{BASE}/{l}/ueber/" lang="{l}">{e(lingue.t("nav_about", l))}</a>' for l in LANGS)
            + "</p><p>"
            + " · ".join(f'<a href="{BASE}/{l}/impressum/" lang="{l}">{e(lingue.t("imprint", l))}</a>' for l in LANGS)
            # the core script: the header's search finds the page that was looked for (step 3b)
            + f'</p></footer><script src="{BASE}/stand.js" defer></script></body></html>')
    write("/404.html", html)


# ------------------------------------------------- the scripts and their data (step 3b)
# Everything a script needs that the page does not carry: one copy for the four languages wherever the
# content allows (names of firms and authorities, CPV labels in all four languages, titles as published),
# under /daten/ (closed to crawlers by robots.txt). controlla.py checks that every file parses, that every
# company, authority and open tender is in it exactly once, and the byte limits below.
DATA_BYTES: collections.Counter = collections.Counter()
# words that never choose a search shard (a firm is not found under 'A' for its 'AG'): legal forms,
# articles, prepositions
SEARCH_STOP = ("ag", "sa", "gmbh", "sarl", "sagl", "ltd", "kg", "co", "cie", "inc", "llc", "ug", "se", "sas", "srl",
               "spa", "de", "du", "des", "la", "le", "les", "der", "die", "das", "dem", "den", "und", "et", "ed",
               "di", "del", "della", "dei", "von", "fur", "and", "of", "the", "en", "au", "aux", "im", "in", "an",
               "zu", "zur", "zum", "par", "pour", "per")
# Fix round 4: the words a query drops while another word remains, folded ('für' fur, 'à' a, 'd’' d), on the tender
# lists (js/liste.js) and in the search (js/suche.js), through /stand.js (D.sw: these and SEARCH_STOP, one list):
# 'Reinigung an Schulen' found nothing where 'Reinigung Schulen' found 2. The articles and prepositions of the four
# languages (the brief's lists, and the Italian articulated forms and the French elided ones); a superset of
# SEARCH_STOP, so the shard a query picks (its first word not in the list) still holds what it finds.
QUERY_STOP = ("an", "fur", "der", "die", "das", "und", "im", "in", "von", "zu", "mit", "bei", "auf",
              "de", "du", "des", "la", "le", "les", "et", "a", "au", "aux", "pour", "en", "d", "l",
              "di", "del", "della", "dei", "e", "al", "per", "con", "delle", "degli", "dello", "dell", "alla", "alle",
              "nel", "nella",
              "of", "the", "and", "for", "at", "to", "with")
SHARD_MAX = 320_000            # bytes of one search shard (the largest, 's', is fetched for 'Stadt', 'SBB' …)
DATA_MAX = 6_000_000           # every file of /daten/suche/, /daten/offen.json, /daten/kb/, /daten/abo-rate.json
JS_MAX_GZ = 30_000             # all the scripts together but the home's, gzip (fix round 1: 25 -> 30 KB, the brief's budget)
HOME_JS_MAX_GZ = 12_000        # /js/home.js alone, gzip (step 4): the home's motion and its map
LIST_CUT = 300                 # a tender list longer than this shows its first LIST_FIRST rows…
LIST_FIRST = 100               # …and the whole list on a page of its own (alle/), or in place with JavaScript
# shared by the four language passes (build_language, first pass): what the search index is built from
SHARED: dict = {}


def sfold(s: str) -> str:
    """The search's folding, the same as js/stand.js fold(): case, accents and umlauts away, ß -> ss,
    ae/oe/ue -> a/o/u, so 'Zürich', 'Zuerich' and 'zurich' are one word."""
    s = (s or "").lower().replace("ß", "ss").replace("æ", "ae").replace("œ", "oe").replace("ø", "o")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.category(c).startswith("M"))
    return s.replace("ae", "a").replace("oe", "o").replace("ue", "u")


def stoks(s: str) -> list:
    return [t for t in re.split(r"[^0-9a-z]+", sfold(s)) if t]


def shard_keys(name: str) -> set:
    """The shards an entry sits in: the first letter (digits: '0') of each of its words, the stop words and
    single letters aside unless nothing else is left."""
    toks = stoks(name)
    sig_ = [t for t in toks if t not in SEARCH_STOP and len(t) > 1]
    return {("0" if t[0].isdigit() else t[0]) for t in (sig_ or toks)}


def js_slug(s: str) -> str:
    """slug() as js/suche.js computes it from a name: an entry stores 0 instead of its page's slug when
    the two agree (all 3'205 companies do), so the index carries every name once and no slug."""
    s = (s or "").lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.category(c).startswith("M"))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:70] or "x"


def write_json(path: str, obj, kind: str) -> None:
    data = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    f = OUT / path.lstrip("/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(data)
    DATA_BYTES[kind] += len(data)


def in_lang(lang: str, fn):
    """fn() computed as the pass of another language would (cpv_label, canton_name, de() read LANG)."""
    global LANG
    old, oldf = LANG, formato.LANG
    LANG, formato.LANG = lang, lang
    try:
        return fn()
    finally:
        LANG, formato.LANG = old, oldf


def award_target(a: dict) -> str:
    """An award page's address after /<lang>/auftrag/, at the award's own line when the page lists several."""
    return f"{a['projectId']}/" + (f"#{a['_anchor']}" if a.get("_anchor") else "")


def open_data(opens: list) -> dict:
    """/daten/offen.json: every open tender, for the lists' filters, the search and the alert's preview.
    t: [projectId, titles, map, cantons, CPV code, authority, deadline]; titles: each distinct title the
    four language versions show, as 'de|…' (its language, '--' unknown; cut as the hub cuts it), map: which
    of them each language shows (de fr it en, '' = the first for all); cantons: as listed, '*' first when
    they are the authority's seat; c: CPV labels in the four languages, b: the authorities, k and d: the
    names of the cantons and the Branchen in the four languages."""
    rows = sorted(opens, key=lambda t: (t.get("offerDeadline") or "9999", str(t.get("projectId") or "")))
    heads = {l: in_lang(l, lambda: list(zip(distinct_titles([de(t, "title") for t in rows], 120),
                                            [de_lang(t, "title")[1] for t in rows]))) for l in LANGS}
    buyers, bix, cpv, out = [], {}, {}, []
    for i, t in enumerate(rows):
        vs, mp = [], ""
        for l in LANGS:
            h, tl = heads[l][i]
            v = f"{tl or '--'}|{h}"
            if v not in vs:
                vs.append(v)
            mp += str(vs.index(v))
        b = _ws(t.get("buyerName") or "")
        if b not in bix:
            bix[b] = len(buyers)
            buyers.append(b)
        code = str(t.get("cpvCode") or "")
        if code and code not in cpv:
            cpv[code] = [in_lang(l, lambda: cpv_label(code, de(t, "cpvLabel") or t.get("cpvLabel") or "")) for l in LANGS]
        ks = list(t.get("_cants") or ([t["canton"]] if t.get("canton") else []))
        # r[7]: the day the tender was first published, for the lists' 'Neueste zuerst' and 'Neu' (fix round 1)
        out.append([t.get("projectId"), vs, "" if mp == "0000" else mp,
                    ("*" if ks and t.get("_ksrc") == "auftraggeber" else "") + " ".join(ks), code, bix[b],
                    t.get("offerDeadline") or "", t.get("_first") or ""])
    return {"v": DATA_DATE, "nd": LATEST_TENDER_DAY[0],
            "k": {c: [in_lang(l, lambda: canton_name_or(c, c)) for l in LANGS] for c in sorted(CANTONS)},
            "d": {d: [lingue.CPV_SHORT[l][d] for l in LANGS] for d in sorted(lingue.CPV_SHORT["de"])},
            "c": cpv, "b": buyers, "t": out}


def deadline_min(t: dict) -> int:
    """A tender's deadline in minutes since 1970 (UTC), 0 when it has none."""
    d = deadline_at(t)
    return int(d.timestamp() // 60) if d else 0


def offen_dl(opens: list) -> dict:
    """/daten/offen-dl.json: every open tender's deadline (minutes since 1970), cantons and Branche, the nearest
    first: what /stand.js needs to recount the open tenders on a page once a deadline has passed since the build
    (fix round 1)."""
    rows = sorted(opens, key=lambda t: (deadline_min(t), str(t.get("projectId") or "")))
    return {"t": [[deadline_min(t), " ".join(t.get("_cants") or []), str(t.get("cpvCode") or "")[:2]]
                  for t in rows if deadline_min(t)]}


def ab_rows(rows: list, comp: dict, pages: dict) -> list:
    """/daten/ab/<slug>.json: a buyer's awards after the newest BUYER_SHOWN, as its page's table shows them:
    [date, award page, titles, title map, winners, amount, kind] — titles as offen.json writes them (each distinct
    title the four languages show, 'de|…'; the map says which each language shows), winners [name, page] (1: the
    slug of the name, a slug, 0: none), kind: '' an amount (or none), 'r' a unit rate, 'f' prices per firm, 'x' a
    foreign currency (the amount and its code)."""
    out = []
    for a in rows:
        vs, mp = [], ""
        for l in LANGS:
            h = in_lang(l, lambda: fit_title(de(a, "title"), "", 110, 0))
            v = f"{in_lang(l, lambda: de_lang(a, 'title')[1]) or '--'}|{h}"
            if v not in vs:
                vs.append(v)
            mp += str(vs.index(v))
        ws = winners(a)
        who = [[w, (1 if js_slug(w) == slug(w) else slug(w)) if slug(w) in pages else 0] for w in ws]
        firms_ = firm_prices(a)
        p, cur = price_of(a), cur_of(a)
        if len(firms_) > 1:
            amt, kind = None, "f" if any(fp for _w, fp, _c, _n in firms_) else ""
        elif p and cur != "CHF":
            amt, kind = [round(p, 2), cur], "x"
        else:
            amt, kind = (round(p, 2) if p else None), ("r" if rate_price(p, cur, a) else "")
        out.append([(a.get("publicationDate") or "")[:10], award_target(a), vs, "" if mp == "0000" else mp, who, amt, kind])
    return out


def kf_rows(rows: list, comp: dict, pages: dict) -> list:
    """/daten/kf/<canton>.json: every company of a canton after the first CANTON_FIRMS, as firm_table() ranks them:
    [name, page (1, a slug or 0), awards, CHF sum]."""
    firms_, sums, seen, order = firm_rank(rows, 10 ** 9)
    out = []
    for sl, n in order[CANTON_FIRMS:]:
        name = (comp.get(sl) or {}).get("name") or seen.get(sl, sl)
        out.append([name, (1 if js_slug(name) == sl else sl) if sl in pages else 0, n, round(sums.get(sl, 0.0), 2)])
    return out


# the key pages, for the search: path under /<lang>/, the label key, and words in any language that find it
SEARCH_PAGES = (("ueber/", "nav_about", "uber register methodik quelle daten about methodology source a propos "
                 "informazioni metodologia fonte simap kontakt contact"),
                ("ausschreibungen/abo/", "nav_alert", "abo abonnement alarm alert alerte avviso benachrichtigung "
                 "newsletter e-mail email mail rss feed"),
                ("ausschreibungen/", "nav_tenders", "ausschreibungen offen appels offres bandi aperti tenders open"),
                ("unternehmen/", "nav_companies", "firmen verzeichnis a-z entreprises imprese companies"),
                ("auftraggeber/", "nav_buyers", "verzeichnis a-z adjudicateurs committenti authorities"),
                ("kanton/", "nav_cantons", "kantone cantons cantoni"),
                ("branche/", "divisions", "branchen branches rami industries cpv"),
                ("bereich/", "sectors", "bereiche domaines settori sectors cpv"),
                ("impressum/", "imprint", "impressum mentions legales note legali imprint betreiber"),
                ("datenschutz/", "privacy", "datenschutz confidentialite privacy cookies"))


def themen_data(awards: list, opens: list, sectors: set) -> dict:
    """/daten/suche/themen.json: the cantons, the 45 Branchen and the Bereiche with a page, by their names
    and CPV labels in the four languages (so 'nettoyage' finds the cleaning sector on the German pages),
    with their counts; and the key pages."""
    nk = collections.Counter(a["canton"] for a in awards if a.get("canton"))
    ok = collections.Counter(k for t in opens for k in (t.get("_cants") or []))
    nd = collections.Counter(str(a.get("cpvCode") or "")[:2] for a in awards)
    od = collections.Counter(str(t.get("cpvCode") or "")[:2] for t in opens)
    nc = collections.Counter(str(a.get("cpvCode") or "") for a in awards if a.get("cpvCode"))
    fb: dict = {}
    for a in awards:
        if a.get("cpvCode") and str(a["cpvCode"]) in sectors and str(a["cpvCode"]) not in fb:
            fb[str(a["cpvCode"])] = a
    sec = []
    for code in sorted(sectors):
        a = fb[code]
        labs = [in_lang(l, lambda: cpv_label(code, de(a, "cpvLabel") or a.get("cpvLabel") or "") or code) for l in LANGS]
        sec.append([code, labs, nc[code]])
    return {"k": [[c, [in_lang(l, lambda: canton_name_or(c, c)) for l in LANGS], nk[c], ok[c]] for c in sorted(CANTONS)],
            "d": [[d, [lingue.CPV_SHORT[l][d] for l in LANGS], nd[d], od[d]] for d in sorted(lingue.CPV_SHORT["de"])],
            "s": sec,
            "p": [[path, [lingue.t(key, l) if key in lingue.T else lingue.m(key, l) for l in LANGS], path, words]
                  for path, key, words in SEARCH_PAGES]}


def search_shards(awards: list, comp: dict, pages: dict, bmap: dict) -> dict:
    """The companies and the authorities, by shard (shard_keys). u: [name, slug or 0, awards] for a company
    with a page; f: [name, award page] for one without (its single award); b: [name, slug or 0, awards] for
    an authority with a page, g: [name, its newest award's page, awards] for one without."""
    sh = collections.defaultdict(lambda: {"u": [], "f": [], "b": [], "g": []})

    def put(name, kind, entry):
        for k in sorted(shard_keys(name)):
            sh[k][kind].append(entry)
    for sl, c in sorted(comp.items(), key=lambda kv: (fold(kv[1]["name"]), kv[0])):
        if sl in pages:
            put(c["name"], "u", [c["name"], 0 if js_slug(c["name"]) == sl else sl, len(c["awards"])])
        else:
            a = max((x for x in c["awards"] if x.get("projectId")), key=lambda x: (x.get("publicationDate") or ""), default=None)
            if a is not None:
                put(c["name"], "f", [c["name"], award_target(a)])
    by = collections.defaultdict(list)
    for a in awards:
        if a.get("buyerName"):
            by[norm_buyer(a["buyerName"])].append(a)
    for k, rows in sorted(by.items()):
        if k in bmap:
            sl, name = bmap[k][0], bmap[k][1]
            put(name, "b", [name, 0 if js_slug(name) == sl else sl, len(rows)])
        else:
            name = collections.Counter(" ".join(a["buyerName"].split()) for a in rows).most_common(1)[0][0]
            a = max((x for x in rows if x.get("projectId")), key=lambda x: (x.get("publicationDate") or "",
                                                                            str(x.get("publicationNumber") or "")), default=None)
            if a is not None:
                put(name, "g", [name, award_target(a), len(rows)])
    return {k: {t: v for t, v in d.items() if v} for k, d in sh.items()}


KB_FIRMS, KB_RECENT = 15, 20


def kb_data(awards: list, comp: dict, pages: dict) -> dict:
    """/daten/kb/<canton>.json: a canton's awards by Branche — the companies with the most of them (count and
    CHF sum, as firm_table() counts: one firm's award in francs, no unit rate) and the newest ones (titles as
    published, the CSV files' rule) — and the canton's name in the four languages."""
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for a in awards:
        d = str(a.get("cpvCode") or "")[:2]
        if a.get("canton") and d in lingue.CPV_SHORT["de"]:
            by[a["canton"]][d].append(a)

    def flag(sl: str, name: str):
        return (1 if js_slug(name) == sl else sl) if sl in pages else 0

    def rank(rows: list):
        cnt, sums, seen = collections.Counter(), collections.defaultdict(float), {}
        for r in rows:
            ws = winners(r)
            for w in ws:
                sl = slug(w)
                cnt[sl] += 1
                seen.setdefault(sl, w)
                p = chf_amount(r)
                if p is not None and len(ws) == 1:
                    sums[sl] += p
        order = sorted(cnt.items(), key=lambda kv: (-kv[1], -sums.get(kv[0], 0), fold(seen[kv[0]])))[:KB_FIRMS]
        firms_ = []
        for sl, n in order:
            name = (comp.get(sl) or {}).get("name") or seen[sl]
            firms_.append([name, flag(sl, name), n, round(sums.get(sl, 0.0), 2)])
        # fix round 3: how many won exactly one ('268 Zuschläge an 264 Unternehmen' read as an error)
        return firms_, len(cnt), sum(1 for v in cnt.values() if v == 1)

    def recent(rows: list, k: int = KB_RECENT):
        out_ = []
        for r in sorted((r for r in rows if r.get("projectId")),
                        key=lambda r: ((r.get("publicationDate") or "")[:10], str(r.get("publicationNumber") or "")),
                        reverse=True)[:k]:
            ws = winners(r)
            p = chf_amount(r) if len(ws) == 1 else None
            t = _ws(_INVISIBLE.sub("", r.get("title") or "")) or _ws(de(r, "title"))
            # [7]: 1 when the award counts in the canton only as the authority's seat (fix round 1)
            out_.append([(r.get("publicationDate") or "")[:10], award_target(r), t, detect_lang(t),
                         [[w, flag(slug(w), (comp.get(slug(w)) or {}).get("name") or w)] for w in ws],
                         round(p, 2) if p else None, 1 if r.get("_ksrc") == "auftraggeber" else 0])
        return out_
    out = {}
    for k, divs in by.items():
        dd = {}
        for d, rows in sorted(divs.items()):
            firms_, nk, no = rank(rows)
            dd[d] = {"n": [lingue.CPV_SHORT[l][d] for l in LANGS], "a": len(rows), "k": nk, "o": no, "f": firms_,
                     "r": recent(rows)}
            # the awards that name no place and count here as the authority's seat, and the panel without them
            # (its toggle; fix round 1: 78 % of Bern's IT awards)
            own = [r for r in rows if r.get("_ksrc") != "auftraggeber"]
            if len(own) < len(rows):
                fx, kx, ox = rank(own)
                shown = {x[1] for x in dd[d]["r"]}
                rx = [x for x in recent(own) if x[1] not in shown]
                dd[d].update({"x": len(rows) - len(own), "kx": kx, "ox": ox, "fx": fx,
                              "rx": rx[:max(0, KB_RECENT - sum(1 for x in dd[d]["r"] if not x[6]))]})
        out[k] = {"c": {l: [in_lang(l, lambda: canton_name_or(k, k)), in_lang(l, lambda: lingue.canton_of(k, canton_name_or(k, k), l))]
                        for l in LANGS}, "d": dd}
    return out


def abo_rate() -> dict:
    """/daten/abo-rate.json: tenders first published in the last 8 weeks of the data, by canton and Branche
    ('*' = all), each canton a tender is listed under; the alert form divides by 8 for 'new a week'."""
    end = LATEST_TENDER_DAY[0] or DATA_DATE
    start = (date.fromisoformat(end) - timedelta(days=55)).isoformat()
    r: dict = collections.defaultdict(collections.Counter)
    for day, ks, d in FIRSTS:
        if not start <= day <= end:
            continue
        d = d if re.fullmatch(r"\d{2}", d) else ""
        for k in ks or ():
            r[k]["*"] += 1
            if d:
                r[k][d] += 1
        r["*"]["*"] += 1
        if d:
            r["*"][d] += 1
    return {"from": start, "to": end, **{k: dict(sorted(v.items())) for k, v in sorted(r.items())}}


def write_script_data(awards: list, opens: list) -> None:
    comp, pages, bmap, sectors = SHARED["comp"], SHARED["pages"], SHARED["bmap"], SHARED["sectors"]
    write_json("/daten/offen.json", open_data(opens), "offen")
    write_json("/daten/offen-dl.json", offen_dl(opens), "offen")
    for sl, rows in sorted(AB_JSON.items()):
        write_json(f"/daten/ab/{sl}.json", ab_rows(rows, comp, pages), "alle")
    for k, rows in sorted(KF_JSON.items()):
        write_json(f"/daten/kf/{k}.json", kf_rows(rows, comp, pages), "alle")
    write_json("/daten/suche/themen.json", themen_data(awards, opens, sectors), "suche")
    for k, v in sorted(search_shards(awards, comp, pages, bmap).items()):
        write_json(f"/daten/suche/{k}.json", v, "suche")
    for k, v in sorted(kb_data(awards, comp, pages).items()):
        write_json(f"/daten/kb/{k}.json", v, "kb")
    write_json("/daten/abo-rate.json", abo_rate(), "abo")
    # the open tenders per canton and per Branche, for the pills of the award pages (data-open)
    write_json("/daten/offen-n.json", {
        "k": dict(sorted(collections.Counter(k for t in opens for k in (t.get("_cants") or [])).items())),
        "b": dict(sorted(collections.Counter(str(t.get("cpvCode") or "")[:2] for t in opens
                                             if str(t.get("cpvCode") or "")[:2] in lingue.CPV_SHORT["de"]).items()))}, "offen")


# The scripts (js/ in the repository): /stand.js on every page, with the day's data; the page types' own
# under /js/, each with its words in the four languages. Their version (?v=) is a hash of what they say,
# so a page names a new one only when a script changed, never because a night passed.
JS_DIR = ROOT / "js"
JS_WORDS = {
    # fix round 6: with the words two scripts share (the search's and the tender lists' suggestions and dividers, the
    # awards' count, the failure), read as A.L: one copy instead of two, for the room the search's fixes needed
    "stand": ("due_today", "due_today_bare", "due_tomorrow", "due_days", "due_over", "hidden_1", "hidden_n",
              "tender_expired", "expired_lead", "top", "ph", "colon", "all_n", "z_h", "z_drop", "z_abo", "z_dym",
              "tier_w", "tier_a", "aw_1", "aw_n", "failed"),
    # fix round 4: the words no script reads any more out (suche res_h, liste k_canton and k_div, kb rate_flag, alle all_n)
    "suche": ("g_t", "g_u", "g_b", "g_s", "g_k", "g_p", "all_t", "all_r", "none", "none_hint", "n_res",
              "n_res_1", "n_sug", "more", "open_1", "open_n", "to_award", "k_canton", "k_div", "k_sec", "until",
              "loading"),
    "liste": ("f_count", "f_first", "f_none", "f_active", "f_active_1", "multi", "z_near", "f_abo_kwb"),
    "abo": ("email_missing", "email_bad", "sel", "pv", "pv_lt", "pv_note", "open_1", "open_n", "sum_sel", "all_ch",
            "all_b", "bf_none"),
    "kb": ("kb_close", "kb_h", "kb_lead", "kb_f1", "kb_fn", "kb_top", "company", "awards", "sum_l",
           "unit_k", "unit_m", "amount", "kb_recent", "date", "contract", "winner", "kb_all", "kb_csv",
           "kb_fb", "kb_fbx", "kb_once"),
    # the rest of a cut table, in place (fix round 1)
    "alle": ("rate_flag", "per_firm", "fx_amount", "not_published"),
    # the home's map read-out (step 4); dec: the decimal sign of the language; the 'neu' badge's words (fix round 6:
    # from /stand.js, the home is the only page that has the badge)
    "home": ("map_rank", "map_share", "map_lit", "open_1", "open_n", "dec", "map_go", "new_today", "new_today_1",
             "new_yday", "new_yday_1"),
}


def _word(mod: str, key: str, l: str) -> str:
    if key == "dec":
        return "." if l == "en" else ","
    if mod in ("abo", "home") and key in ("open_1", "open_n"):
        one, many = lingue.OPEN_TENDERS[l]
        return f"1 {one}" if key == "open_1" else f"{{n}} {many}"
    if mod == "abo" and key.startswith("email_"):
        return lingue.m("abo_" + key, l)
    if key == "all_n":
        return lingue.IDX["show_all_n"][l]
    if key == "colon":
        return lingue.COLON[l]
    for tbl in (lingue.JS, lingue.META, lingue.T, lingue.IDX):
        if key in tbl:
            return tbl[key][l]
    raise KeyError(key)


def js_min(src: str) -> str:
    """A script as shipped: block comments, comment lines and indentation out (js/ keeps them); the scripts
    are written so that this is safe (no '/*' or a line starting '//' inside a string)."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return "\n".join(x for x in (y.strip() for y in src.splitlines()) if x and not x.startswith("//")) + "\n"


def js_module(name: str) -> str:
    src = js_min((JS_DIR / f"{name}.js").read_text(encoding="utf-8"))
    assert src.count("__L__") == 1, name
    words = {l: {k: _word(name, k, l) for k in JS_WORDS[name]} for l in LANGS}
    return src.replace("__L__", json.dumps(words, ensure_ascii=False, separators=(",", ":")), 1)


JS_MODULES = ("suche", "liste", "abo", "kb", "home", "alle")
JS_VER = [hashlib.sha1("".join(js_module(m) for m in JS_MODULES).encode("utf-8")
                       + (JS_DIR / "stand.js").read_bytes()).hexdigest()[:8]
          if (JS_DIR / "stand.js").exists() else "0"]


def write_scripts() -> None:
    """/stand.js (the day's data and the core) and /js/<module>.js."""
    data = {"iso": DATA_DATE, "t": {l: lingue.m("stand", l, d="{d}") for l in LANGS}, "B": BASE, "v": JS_VER[0],
            "mo": list(lingue.MONTHS["en"][0]),
            # the nearest deadline of the open tenders (minutes since 1970): until it passes, every count of open
            # tenders on a page is still the build's and /stand.js recounts nothing (fix round 1)
            "nx": min((m for m in (deadline_min(t) for t in OPENS) if m), default=0),
            # the words a query drops (fix round 4): one list for the tender lists and the search, the shards' too
            "sw": " ".join(dict.fromkeys(SEARCH_STOP + QUERY_STOP)),
            "L": {l: {k: _word("stand", k, l) for k in JS_WORDS["stand"]} for l in LANGS}}
    for l in LANGS:
        formato.LANG = l
        data[l] = formato.date(DATA_DATE)
    formato.LANG = LANG
    src = js_min((JS_DIR / "stand.js").read_text(encoding="utf-8"))
    assert src.count("__DATA__") == 1
    write("/stand.js", src.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")), 1))
    for m in JS_MODULES:
        write(f"/js/{m}.js", js_module(m))


def build_root() -> None:
    """The root used to be a language picker. Search Console (2026-09-07) showed it
    was the ONLY page Google indexed, ranking at position 61 for "ausschreibungen
    schweiz" with nothing on it, and every observed query was German. So the root now
    carries the German homepage itself; the language switch stays in the masthead.
    Canonical points at /de/ so the two copies consolidate instead of competing, and so does
    x-default (08.10.2026; it pointed every page at /, a URL that is no page's canonical);
    the hreflang alternates are copied along. The sitemap leaves / out."""
    de_home = OUT / "de" / "index.html"
    html = de_home.read_text(encoding="utf-8")
    html = html.replace(f'<link rel="canonical" href="{ORIGIN}/de/">',
                        f'<link rel="canonical" href="{ORIGIN}/de/">', 1)
    write("/index.html", html)




def canton_grid(cant_list: list) -> str:
    """The canton index (fix round 2: an A–Z directory of 26 names): the 26 cantons in a grid of the A–Z component,
    the most awards first, each with its code, its name, its awards and a bar against the canton with the most."""
    mx = max((len(r) for _c, r in cant_list), default=0) or 1
    return (f'<div class="sec"><div class="runhead"><h2>{e(_i.by_canton_awards)}</h2><span>{e(_.by_awards)}</span></div>'
            '<ul class="az kg">' + "".join(
                f'<li><a href="{BASE}/{LANG}/kanton/{c}/"><b>{c}</b><em class="nm">{e(canton_name_or(c, c))}</em>'
                f'<small>{formato.count(len(r))}<em class="sr"> {e(_.awards)}</em></small>'
                f'<i style="--w:{100 * len(r) / mx:.1f}%" aria-hidden="true"></i></a></li>' for c, r in cant_list)
            + "</ul></div>")


def nocant_section(rows: list, total: int) -> str:
    """The awards that count in no canton (kantone.py: neither a place, nor a lot's, nor a buyer with a
    canton), listed on the canton index: with them the 26 cantons add up to the national total (step 3a,
    14.10.2026: the cantons summed to 18'443, the home said 18'552). '' when there are none."""
    if not rows:
        return ""
    rows = sorted(rows, key=lambda a: (a.get("publicationDate") or "", str(a.get("publicationNumber") or "")),
                  reverse=True)
    heads = distinct_titles([de(a, "title") for a in rows], 110)
    lis = []
    for a, h in zip(rows, heads):
        d = a.get("publicationDate") or ""
        link = f'<a href="{award_href(a)}"{la(a)}>{e(h)}</a>' if h else e(a.get("publicationNumber") or "")
        lis.append(f'<li><div class="row">{link}<span class="sub num">{tt(d, formato.date(d))}</span></div></li>')
    return (f'<div class="sec" id="ohne-kanton"><div class="runhead"><h2>{e(_.no_canton)}</h2>'
            f'<span>{formato.count(len(rows))}</span></div>'
            f'<p class="sub m10">{e(_if("nocant_lead_one", total=zuschlag(total)) if len(rows) == 1 else _if("nocant_lead", n=awards_start(len(rows)), total=zuschlag(total)))}</p>'
            f'<ul class="plain">{"".join(lis)}</ul>{csv_download(rows, "kanton", "ohne-kanton", _i.csv_nocant)}</div>')


# matches() reads only CPV digits and cantons: the same for the four language passes (14.10.2026:
# it was a minute of the build, computed four times)
_OPEN_FOR: dict = {}


def build_language(awards: list, opens: list, expired: list) -> tuple[int, int, int, int, int, int]:
    comp = profile(awards)
    if not _OPEN_FOR:
        _OPEN_FOR.update(matches(comp, opens))
    open_for = _OPEN_FOR
    sectors = sector_pages(awards)
    buyer_slugs = buyer_map(awards)
    keep = {n for n, c in comp.items() if len(c["awards"]) >= MIN_AWARDS}
    peer_map = peers(comp, keep)
    pages = build_companies(comp, open_for, sectors, buyer_slugs, peer_map)
    if not SHARED:
        # the search index is language-neutral: built once, from the first pass (step 3b)
        SHARED.update(comp=comp, pages=pages, bmap=buyer_slugs, sectors=sectors)
    lot_sib = {}
    for _stem, g in lot_groups(sorted((t for t in opens if t.get("offerDeadline")),
                                      key=lambda t: t["offerDeadline"])):
        if len(g) > 1:
            for t in g:
                lot_sib[t.get("projectId")] = [x for x in g if x is not t]
    # who has what open, and the awards by authority and by industry and canton, newest first: what
    # the tender and buyer pages show beside their own record (14.10.2026)
    ctx = {"open_by_buyer": collections.defaultdict(list), "awards_by_buyer": collections.defaultdict(list),
           "awards_by_dc": collections.defaultdict(list)}
    for t in opens:
        if t.get("buyerName"):
            ctx["open_by_buyer"][norm_buyer(t["buyerName"])].append(t)
    for a in sorted(awards, key=lambda a: ((a.get("publicationDate") or "")[:10],
                                           str(a.get("publicationNumber") or "")), reverse=True):
        # the authority's key and the CPV code's significant digits, once (bid_context reads them
        # for every tender of a canton and industry)
        a["_bk"] = norm_buyer(a.get("buyerName") or "")
        a["_sig"] = sig(a.get("cpvCode") or "")
        if a.get("buyerName"):
            ctx["awards_by_buyer"][a["_bk"]].append(a)
        d = str(a.get("cpvCode") or "")[:2]
        if d.isdigit() and a.get("canton"):
            ctx["awards_by_dc"][(d, a["canton"])].append(a)
    award_cants = {a["canton"] for a in awards if a.get("canton")}
    n_aw = build_awards(awards, opens, expired, pages, sectors, buyer_slugs, lot_sib, ctx, award_cants)
    buyers = build_buyers(awards, comp, pages, sectors, buyer_slugs, ctx["open_by_buyer"])
    # every canton a tender is listed under (kantone.cantons_of), as on the tender lists
    open_cants = collections.Counter(k for t in opens for k in (t.get("_cants") or []))
    open_divs = collections.Counter(str(t.get("cpvCode") or "")[:2] for t in opens
                                    if str(t.get("cpvCode") or "")[:2].isdigit())
    cant_list, cpv_list = build_hubs(awards, comp, pages, sectors, open_cants, open_divs, buyer_slugs)
    n_open = build_open(opens, sectors, buyer_slugs, award_cants)
    by_cpv = collections.defaultdict(list)
    for a in awards:
        if a.get("cpvCode"):
            by_cpv[str(a["cpvCode"])].append(a)
    build_divisions(awards, opens, comp, pages, sectors, buyer_slugs, by_cpv)
    build_index("/unternehmen/", _.companies, _i.companies_h1, _i.companies_lead,
                [(sl, p["name"], p["n"]) for sl, p in pages.items()],
                _i.companies_title, _if("companies_desc", n=formato.count(len(pages))),
                lastmod=max((p["date"] for p in pages.values()), default=""), split="companies",
                top=finder(len(comp), len(pages), "m18", az=False))
    build_index("/auftraggeber/", _.buyers, _i.buyers_h1, _i.buyers_lead,
                [(sl, n, k) for sl, n, k in buyers],
                _i.buyers_title, _if("buyers_desc", n=formato.count(len(buyers))), lastmod=newest(awards),
                split="buyers", top=finder(len({norm_buyer(a["buyerName"]) for a in awards if a.get("buyerName")}),
                                           len(buyers), "m18", az=False, kind="b"))
    build_search_page()
    # the awards without a canton, after the 26: with them the cantons add up to the national total
    nocant = [a for a in awards if not a.get("canton")]
    build_index("/kanton/", _.cantons, _i.cantons_h1, _i.cantons_lead,
                [(c, canton_name_or(c, c), len(r)) for c, r in cant_list],
                _i.cantons_title, _i.cantons_desc, extra=nocant_section(nocant, len(awards)),
                lastmod=newest(awards), cells=canton_grid(cant_list))
    build_index("/bereich/", _.sectors, _i.sectors_h1, _i.sectors_lead,
                [(c, next((cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") or c for a in r
                           if cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "")), c), len(r))
                 for c, r in cpv_list],
                _i.sectors_title, _i.sectors_desc,
                top=(f'<p class="dl"><a href="{BASE}/{LANG}/branche/">{e(_if("to_divisions", n=len(lingue.CPV_SHORT[LANG])))}</a></p>'),
                lastmod=newest(*(r for _c, r in cpv_list)))
    build_home(pages, comp, awards, opens, cant_list, cpv_list)
    build_impressum()
    build_privacy()
    build_about(awards, opens)
    return (len(pages), n_aw, len(buyers), len(cant_list), len(cpv_list), n_open)


def main() -> None:
    global LANG
    # docs/ is wiped every build, so the IndexNow key file — proof of ownership,
    # served at the site root — is put back afterwards rather than lost each night.
    keyfile = ROOT / "indexnow.key"
    if OUT.exists():
        shutil.rmtree(OUT)
    awards, opens, expired = load()
    OPENS[:] = opens
    _SHARED.update(find_shared(awards + opens + expired))
    global DATA_DATE
    DATA_DATE = max(((a.get("publicationDate") or "")[:10] for a in awards), default=TODAY) or TODAY
    print(f"  dati    : {len(awards)} aggiudicazioni · {len(opens)} bandi aperti · "
          f"{len(expired)} scaduti con pagina (fino a {EXPIRED_DAYS} giorni) · dati al {DATA_DATE}")
    print(f"  esclusi : {len(INCOMPLETE)} aggiudicazioni senza titolo né vincitore · "
          f"{NO_DEADLINE[0]} bandi senza scadenza leggibile · "
          f"{sum(1 for a in awards if not a.get('canton'))} aggiudicazioni senza cantone · "
          f"{sum(1 for a in awards if is_rate(a))} probabili prezzi unitari")
    formato.MONTHS = lingue.MONTHS
    # Monthly charts: which months are complete. FULL_FROM is the first month whose count
    # reaches half the median of it and every later complete month — on 28.09.2026 that is
    # 2024-11 (Aug 13, Sep 96, Oct 198, Nov 446): the months before are the series
    # building up and are drawn striped with a note, not read as a market trend.
    global FULL_FROM, RAMP_START, RAMP_END, CUR_MONTH, CUR_PARTIAL
    nat = per_month(awards)
    keys = sorted(nat)
    CUR_MONTH = DATA_DATE[:7]
    CUR_PARTIAL = int(DATA_DATE[8:10]) < calendar.monthrange(int(DATA_DATE[:4]), int(DATA_DATE[5:7]))[1]
    RAMP_START = FULL_FROM = keys[0] if keys else CUR_MONTH
    done = [k for k in keys if k < CUR_MONTH]
    for i, k in enumerate(done):
        rest = sorted(nat[x] for x in done[i:])
        if nat[k] >= 0.5 * rest[len(rest) // 2]:
            FULL_FROM = k
            break
    y, m = int(FULL_FROM[:4]), int(FULL_FROM[5:7])
    RAMP_END = f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"
    print(f"  mesi    : serie completa da {FULL_FROM} (rampa {RAMP_START}..{RAMP_END}), "
          f"mese corrente {CUR_MONTH}{' parziale' if CUR_PARTIAL else ''}")
    for lang in LANGS:
        LANG = lang
        formato.LANG = lang
        n = build_language(awards, opens, expired)
        print(f"  {lang}      : {n[0]} imprese · {n[1]} appalti · {n[2]} committenti "
              f"· {n[3]} cantoni · {n[4]} settori · {n[5]} bandi")
    LANG = "de"
    print(f"  persone : {len(NATURAL)} pagine di imprese col nome di una persona fisica (noindex, fuori dalla sitemap)")
    write_aggregates(awards, opens)
    build_root()
    build_abo_status()
    build_404()
    write_scripts()
    write_script_data(awards, opens)
    # The icons and the share cards (immagini/, 14.10.2026): favicon.svg, which every page names (it
    # was a 600-byte data URI inside each of 92,000 pages); favicon.ico and apple-touch-icon.png at the
    # root, where browsers and iOS look for them without a tag; icon-512.png, the logo of the
    # structured data; og-<lang>.png, the 1200×630 card of a shared link.
    for f in sorted((ROOT / "immagini").glob("*")):
        if f.suffix in (".svg", ".png", ".ico"):
            shutil.copy(f, OUT / f.name)
    if CSV_BYTES:
        print(f"  csv     : {len(_CSV_DONE)} file, "
              + " · ".join(f"{k} {v / 1e6:.1f} MB" for k, v in sorted(CSV_BYTES.items())))
    # Fonts are served from our own origin: the Google Fonts link both blocked first
    # paint for ~2 seconds on mobile and sent every visitor's IP to Google — the same
    # embedding European courts have already sanctioned. docs/ is wiped every build,
    # so the woff2 files are copied in each time, like the CNAME and the IndexNow key.
    fdir = ROOT / "fonts"
    fontcss = ""
    if fdir.exists():
        (OUT / "fonts").mkdir(parents=True, exist_ok=True)
        # the fonts and, beside them, their licences (SIL OFL 1.1 asks for the licence with the fonts)
        for f in [*fdir.glob("*.woff2"), *fdir.glob("*-OFL.txt")]:
            shutil.copy(f, OUT / "fonts" / f.name)
        # The French pages space digit groups and ':' ';' '?' '!' '%' with U+202F. Google's
        # subsets have no glyph for it, so the browser fell back to a system font that draws it
        # 1.3-1.8 px wide: '888 382 352.95' read as one run of digits (verifier, 28.09.2026).
        # The Latin files in fonts/ map it (step 4: Instrument Sans got a narrow space glyph of its own,
        # League Gothic has one); warn if a font update ever brings files without it back.
        try:
            from fontTools.ttLib import TTFont
            bad = [f.name for f in (fdir / "is.woff2", fdir / "is7.woff2", fdir / "lg.woff2")
                   if 0x202F not in TTFont(f).getBestCmap()]
            if bad:
                print(f"  ATTENZIONE: font senza U+202F (spazio fine francese): {', '.join(bad)}")
        except Exception:
            pass
        fontcss = (fdir / "fonts.css").read_text().replace("/fonts/", f"{BASE}/fonts/")
    # one minified sheet: the fonts, the look, the stacked tables' labels (the home's own rules are in its head)
    write("/style.css", css_min(fontcss + "\n" + CSS + "\n" + css_labels()) + "\n")
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
    noindex = {u.rstrip("/") + "/" for u in NOINDEX}
    for f in OUT.rglob("index.html"):
        u = url_of(f)
        if "/auftrag/" in u or u.startswith("/abo/"):   # noindex: fuori dalla sitemap (schede: vedi build_awards; /abo/: pagine di ritorno Brevo)
            continue
        if u in noindex:                                # liste vuote di bandi (noindex, 14.10.2026)
            continue
        if u == "/":       # la radice e' una copia di /de/ con canonical /de/ (build_root): resta raggiungibile, non va in sitemap
            continue
        seg = u.strip("/").split("/")[0]
        (by_lang[seg] if seg in by_lang else root).append(u)

    # <lastmod> = the newest publication among the records the page shows (LASTMOD, set by page();
    # step 3a, 14.10.2026), not a git date: the worktree's docs/ is not committed, and every URL read
    # as changed on the day of the build. A page that shows no record (the legal pages) has none.
    def doc(urls: list[str]) -> str:
        head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        body = "".join(f"<url><loc>{ORIGIN}{u}</loc>"
                       + (f"<lastmod>{LASTMOD[u]}</lastmod>" if LASTMOD.get(u) else "") + "</url>"
                       for u in sorted(urls))
        return head + body + "</urlset>"

    files, total = [], 0
    for lang in LANGS:
        urls = by_lang[lang] + (root if lang == LANGS[0] else [])
        assert len(urls) <= 50_000, f"sitemap-{lang}: {len(urls)} URL, il limite e' 50 000"
        write(f"/sitemap-{lang}.xml", doc(urls))
        files.append((f"sitemap-{lang}.xml", max((LASTMOD.get(u, "") for u in urls), default="") or DATA_DATE))
        total += len(urls)

    idx = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           + "".join(f"<sitemap><loc>{ORIGIN}/{f}</loc><lastmod>{d}</lastmod></sitemap>"
                     for f, d in files)
           + "</sitemapindex>")
    write("/sitemap.xml", idx)
    # robots.txt sits at /auftragsregister/robots.txt on a project Pages site, where no
    # crawler looks for it — the origin root is not ours to write. It is emitted for
    # correctness; discovery happens through the Search Console submission.
    # the CSV files are data, not pages (14.10.2026)
    # the 26 canton files (and the one for the awards without a canton) are what the about page's Dataset
    # offers for download: crawlable, the rest of /daten/ not (step 3a, 14.10.2026)
    write("/robots.txt", f"User-agent: *\nAllow: /\nAllow: {BASE}/daten/kanton/\nDisallow: {BASE}/daten/\n\n"
                         f"Sitemap: {ORIGIN}/sitemap.xml\n")
    return total


if __name__ == "__main__":
    main()
