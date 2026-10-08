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

import calendar
import collections
import hashlib
import html
import json
import pathlib
import re
import shutil
import unicodedata
from datetime import date, datetime, timedelta

import formato
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
TODAY = date.today().isoformat()
# The moment of the build: a tender whose deadline is behind it is no longer open, even on the
# deadline's own day (a deadline of today 00:00 was listed as open all day; 08.10.2026)
NOW = datetime.now().astimezone()
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


def plural(n: int, one: str, many: str) -> str:
    """'1 Unternehmen / 27 Unternehmen', '1 impresa / 22 imprese': every 'number + noun'
    goes through here, so the count is grouped and the noun agrees."""
    return f"{formato.count(n)} {one if n == 1 else many}"


_ONE = {"awards": "award", "companies": "company", "buyers": "buyer", "cantons": "canton"}


def lab_n(n: int, many: str) -> str:
    """A tile or rail label that agrees with the figure above it: '1 Committente', not
    '1 Committenti' (193 company pages, 34 sector pages, 7 buyer pages; verifier 28.09.2026)."""
    return lingue.t(_ONE[many] if n == 1 else many, LANG)


def firms(n: int) -> str:
    """'27 Unternehmen'; one is 'ein einziges Unternehmen' / 'une seule entreprise': '3
    adjudications en faveur de 1 entreprise' read like a form letter (verifier, 28.09.2026)."""
    return lingue.COMPANY_ONE[LANG] if n == 1 else plural(n, *lingue.COMPANY[LANG])


def open_n(n: int) -> str:
    return plural(n, *lingue.OPEN_TENDERS[LANG])


def open_contracts(n: int) -> str:
    return plural(n, *lingue.OPEN_CONTRACTS[LANG])


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


def due_today(iso: str) -> str:
    """'läuft heute ab, 16.00 Uhr' for a deadline on the day of the build, '' on any other day: the
    site is built once each morning, and a tender due at 16.00 stood under the bare date all day
    (08.10.2026). Only open tenders reach this; one due earlier today is already over (load)."""
    if not iso or iso[:10] != TODAY:
        return ""
    t = formato.clock(iso)
    return _m("due_today", t=t) if t else _m("due_today_bare")


def due_cell(iso: str, text: str, until: bool = False) -> tuple[str, str]:
    """(extra class, content) of a deadline in a tender list: the date as before ('bis 25.09.2026'),
    or on its own day 'läuft heute ab, 16.00 Uhr', which the class sets in the signal colour."""
    today = due_today(iso)
    if today:
        return " today", f'<time datetime="{e(iso)}">{e(today)}</time>'
    return "", (f"{_.until} " if until else "") + tt(iso, text)


def fold(s: str) -> str:
    """Sort key that files É under E and Ö under O, instead of after Z."""
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().casefold()


def abbr_canton(code: str) -> str:
    return f'<abbr title="{e(canton_name_or(code, code))}">{e(code)}</abbr>' if code else ""


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
    orig = (row.get(field) or "").strip()
    order = (LANG, "de", "fr", "it")
    for lang in order:
        v = (t.get(lang) or "").strip()
        if not v:
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
        return _INVISIBLE.sub("", v)
    return _INVISIBLE.sub("", orig)


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
    return float(p) if cur == "CHF" else None


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
    k = sum(1 for a in rows if joint_priced(a))
    note = (f'<em class="approx">{e(_if("sum_no_joint_one" if k == 1 else "sum_no_joint", k=formato.count(k)))}</em>'
            if k else "")
    return f'<div class="fig money"><b>{formato.tile(total)}</b><span>{_.sum_published}</span>{note}</div>'


def award_cell(a: dict) -> str:
    """An award's amount in a list of awards: its amount when it names one firm; for several firms
    no figure — each has its own price, on the award's page."""
    firms = firm_prices(a)
    if len(firms) > 1:
        if any(p for _w, p, _c, _n in firms):
            return f'–<span class="sub" style="display:block">{e(_.per_firm)}</span>'
        return formato.cell(None, empty_sr=_.not_published)
    return formato.cell(price_of(a), cur_of(a), empty_sr=_.not_published)


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
    for f in sorted(DATI.glob("aggiudicazioni_*.json")):
        for a in json.loads(f.read_text()):
            k = a.get("publicationId") or a.get("publicationNumber")
            if k and k in seen:
                continue
            seen.add(k)
            if a.get("pubType") == "abandonment":
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
    for t in rows:
        k = t.get("projectId") or t.get("publicationId") or t.get("publicationNumber")
        if k not in newest or _pub_order(t) > _pub_order(newest[k]):
            newest[k] = t
    # Open = the deadline is still ahead at the moment of the build, not merely on or after today's
    # date (08.10.2026). A tender past its deadline keeps its page for EXPIRED_DAYS, marked as such;
    # once the project has an award, the award's page holds that address instead.
    no_page = {a["projectId"] for a in awards if a.get("projectId")} | {None, ""}
    floor = (date.fromisoformat(TODAY) - timedelta(days=EXPIRED_DAYS)).isoformat()
    opens, expired = [], []
    for t in newest.values():
        dl = deadline_at(t)
        if dl is None:
            continue
        if dl > NOW:
            opens.append(t)
        elif (t.get("offerDeadline") or "")[:10] >= floor and t.get("projectId") not in no_page:
            expired.append(t)
    return awards, opens, expired


def _clean_names(r: dict) -> None:
    """Zero-width characters out of the names ('\u200bGesundheitsnetz Küsnacht AG'): invisible,
    they changed nothing a reader sees but split sort order and counted in cut lengths."""
    for k in ("buyerName", "winnerName"):
        if isinstance(r.get(k), str):
            r[k] = _INVISIBLE.sub("", r[k])
    for v in ((r.get("award") or {}).get("vendors") or []):
        if isinstance(v, dict) and isinstance(v.get("name"), str):
            v["name"] = _INVISIBLE.sub("", v["name"])


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
  font-variant-numeric:normal;line-height:1;overflow-wrap:break-word}
/* a figure never breaks inside its digits or its unit ("827’782.5|5", "C|HF"); only the
   currency may move to the next line, as a whole word */
.fig b .n{white-space:nowrap}
.fig b small{font-size:.42em;font-weight:600;letter-spacing:0;color:var(--muted)}
/* phones: the exact amount and the deadline on the award page take the whole row */
@media(max-width:599px){.figures .fig.wide{grid-column:1/-1}
  /* two tiles per row: the currency on its own line in every tile, not only in the
     ones whose figure happens to be wide ('30,2 mia.' / 'CHF' beside '2,2 mio. CHF') */
  .fig b small{display:block;margin-top:.4em}
  html:lang(en) .fig b small{margin:0 0 .4em}}
.fig .approx{display:block;margin-top:8px;font-size:13px;font-style:normal;color:var(--muted)}
.fig.money b{color:var(--accent)}
/* a date tile keeps its date on one line ('08.10.20|26' on phones, and in four tiles a row up
   to ~1000 px): never larger than the other tiles' figures, smaller where 17 % of the tile's own
   width, which fits the longest date ('30 May 2026'), asks for it; the media query is for
   browsers without container units (08.10.2026) */
.fig.date{container-type:inline-size}
.fig.date b{white-space:nowrap}
@media(max-width:419px){.fig.date b{font-size:clamp(17px,5.2vw,26px)}}
.fig.date b{font-size:max(17px,min(17cqi,clamp(26px,3.6vw,38px)))}
.fig.off b{color:var(--muted)}
.fig>span{display:block;margin-top:11px;font-size:10px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--muted-2);font-weight:600;
  font-family:ui-monospace,Menlo,monospace}
.sec{margin-top:10px}
.scroll{overflow-x:auto;max-width:100%;position:relative}
/* position: the visually hidden cell text (.sr) is absolutely positioned; without a
   positioned scroll box it escaped the clipping and widened the page on phones */
/* A table wider than the screen fades out at the edge it continues past, so the sideways scroll
   shows (08.10.2026). Driven by the box's own scroll position: no fade while the table fits (the
   timeline is inactive then) and none at the end reached; without scroll timelines, as before. */
@property --fl{syntax:"<length>";inherits:false;initial-value:0px}
@property --fr{syntax:"<length>";inherits:false;initial-value:0px}
@keyframes scroll-hint{0%{--fl:0px;--fr:28px}6%,94%{--fl:28px;--fr:28px}100%{--fl:28px;--fr:0px}}
@supports (animation-timeline:scroll(self inline)){
  .scroll{-webkit-mask-image:linear-gradient(90deg,transparent,#000 var(--fl),#000 calc(100% - var(--fr)),transparent);
    mask-image:linear-gradient(90deg,transparent,#000 var(--fl),#000 calc(100% - var(--fr)),transparent);
    animation:scroll-hint linear both;animation-timeline:scroll(self inline)}}
/* ── tables ────────────────────────────────────────────────────────────── */
table{width:100%;border-collapse:collapse}
/* the Details box sits in a 320px column: long names and CPV labels wrap in place instead
   of pushing the value column past the edge (verifier, 29.09.2026) */
.kv{table-layout:fixed}
.kv td{padding-right:0;overflow-wrap:break-word;hyphens:auto;vertical-align:baseline}
/* the label column takes 42 % and its labels wrap: at a fixed 112 px 'Staatsvertragsbereich',
   'Contracting authority' and the French and Italian labels ran into the value (08.10.2026);
   42 % of the 320 px column fits 'Staatsvertrags-' on one line. Hyphens only where lingue.py puts
   a soft one: automatic hyphenation split 'ac-cords' though the line breaks at spaces */
.kv th{width:42%;white-space:normal;overflow-wrap:break-word;hyphens:manual;-webkit-hyphens:manual;
  text-transform:none;letter-spacing:0;font-size:13px;font-weight:500;line-height:1.45;
  border-bottom:1px solid var(--rule);padding:13px 12px 13px 0;vertical-align:baseline}
th{text-align:left;font-size:9.5px;letter-spacing:.15em;text-transform:uppercase;
  color:var(--muted-2);font-weight:600;padding:0 14px 11px 0;
  border-bottom:1px solid var(--rule-strong);white-space:nowrap;
  font-family:ui-monospace,Menlo,monospace}
td{padding:13px 14px 13px 0;border-bottom:1px solid var(--rule);vertical-align:top;
  font-size:14.5px}
tbody tr{transition:background .15s}
tbody tr:hover{background:rgba(255,255,255,.032)}
td.r,th.r{text-align:right;padding-right:0;padding-left:18px}
abbr[title]{text-decoration:none;cursor:help}
td.sub,.sub{color:var(--muted);font-size:13px}
ul.plain{list-style:none;margin:0;padding:0}
ul.plain li{padding:13px 0;border-bottom:1px solid var(--rule)}
ul.plain li:last-child{border-bottom:0}
.row{display:flex;justify-content:space-between;gap:16px;align-items:baseline}
/* a long unbroken name ('PricewaterhouseCoopers', 'Infrastrukturunterhaltsgesellschaft')
   wraps instead of widening the page on phones; the count beside it never wraps */
.row>*{min-width:0;overflow-wrap:anywhere}
.row>.sub,.row>.when,.row>.num{flex:none;overflow-wrap:normal}
h1,.eyebrow{overflow-wrap:anywhere}
.when{color:var(--accent);font-size:12px;white-space:nowrap;font-weight:600}
/* due today: 'läuft heute ab, 16.00 Uhr' in the signal colour, free to wrap before the time (its
   other spaces are no-break) instead of widening the column or squeezing the title (08.10.2026) */
.when.today{color:var(--signal);white-space:normal}
.row>.when.today{flex:0 1 auto;min-width:min-content;text-align:right}
/* ── tags / chips ──────────────────────────────────────────────────────── */
.tags{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}
.tag{border:1px solid var(--rule);background:var(--wash);border-radius:100px;
  padding:6px 14px;font-size:12px;color:var(--muted);
  transition:border-color .16s,color .16s,transform .16s var(--ease)}
a.tag{background-image:none;padding-bottom:6px;display:inline-block;max-width:100%;line-height:1.45}
/* inline-block: a pill whose text wraps on a phone stays one rounded box */
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
/* a tender due today, and one past its deadline (08.10.2026) */
.state.today{color:var(--signal);background:rgba(255,180,84,.13)}
.state.off{color:var(--muted);background:rgba(255,255,255,.07)}
.winner{border:1px solid var(--rule);border-radius:16px;background:var(--glass);
  padding:20px 22px;margin:10px 0 0}
.winner .who{font-family:"Bricolage Grotesque",sans-serif;font-size:22px;font-weight:700;
  letter-spacing:-.03em}
.official{margin-top:26px;padding:15px 18px;background:rgba(255,67,86,.09);
  border-left:2px solid var(--accent);border-radius:0 10px 10px 0;font-size:12.5px;
  color:var(--muted)}
.prose p{margin:0 0 15px;font-size:15.5px;line-height:1.7;max-width:66ch;color:var(--muted);overflow-wrap:break-word}
.prose p strong{color:var(--ink)}
.cols{display:grid;grid-template-columns:1fr 320px;gap:48px;padding-top:6px;
  align-items:start}
.half{display:grid;grid-template-columns:1fr 1fr;gap:48px;padding-top:6px;align-items:start}
.cols>*,.half>*{min-width:0}
figure{margin:16px 0 4px;background:var(--panel);border:1px solid var(--rule);
  border-radius:16px;padding:20px 22px}
footer{border-top:1px solid var(--rule);margin-top:56px;padding-top:22px;
  color:var(--muted-2);font-size:12.5px}
footer p{margin:0 0 6px;max-width:80ch}
@media(prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;
  transition-duration:.01ms!important}}
@media(max-width:860px){
  .wrap{padding:0 20px 44px}
  .title{padding:30px 0 24px;grid-template-columns:1fr;gap:24px}
  .cols,.half{grid-template-columns:1fr;gap:30px}
  .glass .ch,.glass .pad{padding-inline:16px}
  /* phones: headers such as "Totale (CHF)" may wrap and the numeric gutter narrows, so
     the half-width firm tables fit 390px again instead of scrolling by 7-21px */
  th{white-space:normal;vertical-align:bottom;letter-spacing:.08em}
  td.r,th.r{padding-left:12px}
  .cmp td.c{width:96px;font-size:11.5px}
  /* the home ranking fits a phone without scrolling: rank and canton step aside */
  table.top .n0,table.top .kt{display:none}
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
<p>{source}{colon} <a href="https://www.simap.ch">simap.ch</a> ({official}) ·
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


def page(title: str, desc: str, body: str, path: str, kicker: str = "",
         leaf: str = "", robots: str = "", head_extra: str = "") -> str:
    # hreflang tells the search engine these are one page in four languages, not four
    # pages competing with each other for the same query.
    # x-default is the page's own German version: it named the root for every page, a URL that
    # is no page's canonical (08.10.2026)
    alts = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{ORIGIN}{lang_path(path, l)}">'
        for l in LANGS) + f'\n<link rel="alternate" hreflang="x-default" href="{ORIGIN}{lang_path(path, "de")}">'
    nav = "".join(
        (f'<span class="on">{e(NAMES[l])}</span>' if l == LANG
         else f'<a href="{BASE}{lang_path(path, l)}">{e(NAMES[l])}</a>') for l in LANGS)
    return (HEAD.format(title=e(title), desc=e(fit_desc(desc)), site=ORIGIN, base=BASE, path=path,
                        kicker=e(kicker or _.register), lang=LANG, alts=alts,
                        verify=VERIFY + (f'<meta name="robots" content="{robots}">\n' if robots else "") + head_extra,
                        sitename=e(_.site), langnav=nav, langlabel=e(_.language))
            + breadcrumbs(path, leaf or re.split(r"\s[—–]\s", title)[0])
            + body + FOOT.format(disc=e(DISCLAIMER),
                                 notoff=e(_p.footer_note),
                                 imphref=f"{BASE}/{LANG}/impressum/",
                                 implabel=e(_.imprint),
                                 privhref=f"{BASE}/{LANG}/datenschutz/",
                                 privlabel=e(_.privacy),
                                 srcnote=e(_p.translation_note), source=e(_.source),
                                 colon=lingue.COLON[LANG],
                                 official=e(_p.source_inline)))


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


def month_chart(rows: list, title: str, fig_id: str = "chart-months") -> str:
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
        return (f'<figure class="mc"><h3>{e(title)}</h3>'
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
    return grafici.month_columns(ser, fig_id=fig_id, title=title, takeaway=tk,
                                 unit_label=_i.mc_unit, units=lingue.PLURALS[LANG],
                                 partial=part, notes=notes)


def division_figure(rows: list, sect_counter: collections.Counter, sectors: set[str]) -> str:
    """Awards by CPV division (first two digits) as a ranked list with bars: the top 8 and
    one row for the rest, each with its share. Parent and sub-classes no longer compete
    for the same eight slots, so the list covers most awards instead of half. The links
    to the eight-digit sector pages stay, as a tag row under it."""
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

    if len(ranked) == 1:
        # a single bar at 100 % says nothing a sentence does not (368 buyer pages per language)
        n = ranked[0][1]
        out = (f'<figure class="rk" aria-labelledby="chart-sectors"><h3 id="chart-sectors">{e(_i.div_title)}</h3>'
               f'<p class="lede">{e(_if("div_single" if n > 1 else "div_single_one", n=zuschlag(n), label=label(ranked[0][0])))}</p></figure>')
    else:
        items = [(label(d), None, k, formato.count(k)) for d, k in top]
        other = None
        if rest:
            s = sum(k for _d, k in rest)
            other = (_if("div_other", k=formato.count(len(rest))), None, s, formato.count(s))
        lede = _if("div_lede_top", k=len(top), total=len(ranked)) if rest else _i.div_lede_all
        out = grafici.rank_list(items, fig_id="chart-sectors", title=_i.div_title, lede=lede,
                                other=other, total=sum(div.values()))
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
        out += (f'<p class="sub" style="margin:14px 0 0">{e(_i.detail_sectors)}</p><div class="tags">'
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
    div = top_division(c["cpv"])
    sector = (lingue.CPV_SHORT[LANG].get(div) or short_sector(cpv_label(div + "000000", ""), 60)
              if div else "")
    if not sector:
        div = ""
    where = ""
    if cant:
        cname = canton_name_or(cant, cant)
        where = _m("alert_where", name=cname, of=lingue.canton_of(cant, cname, LANG))
    if cant and div:
        text = _m("alert_both", sector=sector, where=where)
    elif cant:
        text = _m("alert_canton", where=where)
    elif div:
        text = _m("alert_sector", sector=sector)
    else:
        text = _m("alert_none")
    query = "&".join(f"{k}={v}" for k, v in (("k", cant), ("b", div)) if v)
    href = f"{BASE}/{LANG}/ausschreibungen/abo/" + (f"?{query}" if query else "")
    return (f'<div class="glass"><div class="pad top">'
            f'<p style="margin:0;font-size:15.5px">{e(text)}</p>'
            f'<p style="margin:14px 0 0"><a class="tag on" href="{e(href)}" rel="nofollow">'
            f'{e(_m("alert_link"))}</a></p></div></div>')


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

        b = [f'<div class="title"><div><p class="eyebrow">'
             # the sector only: a canton here read as the firm's seat ('Swisscom … · Genf'),
             # while it is where most of its awards fall — the rail says so ('Häufigste Kantone')
             + e(short_sector(sector, 44) if sector else _.company)
             + f'</p><h1>{e(name)}</h1>'
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
            b.append(f'<div class="fig money"><b>{formato.tile(c["value"])}</b><span>{_.sum_published}</span></div>')
        b.append(f'<div class="fig"><b>{formato.count(len(c["buyers"]))}</b>'
                 f'<span>{lab_n(len(c["buyers"]), "buyers")}</span></div>')
        if len(c["amounts"]) >= 3:
            b.append(f'<div class="fig" title="{e(_.median_help)}"><b>{formato.tile(median(c["amounts"]))}</b>'
                     f'<span>{_.median}</span></div>')
        b.append("</div>")
        b.append(alert_callout(c))

        # Derived analysis (2026-09-07): what simap does not say — per-year rhythm and
        # how concentrated the client base is. Aggregation, not alteration (AGB §5).
        # One money rule for every figure on the page: an amount is credited to the firm
        # only when the award names exactly one firm — the same rule as the headline total,
        # which 595 company pages used to contradict in this table.
        per_year: dict[str, list] = {}
        joint = 0
        for a in rows:
            y = (a.get("publicationDate") or "")[:4]
            if y:
                per_year.setdefault(y, [0, 0.0])
                per_year[y][0] += 1
                p = chf_amount(a)
                if p is not None and len(winners(a)) == 1:
                    per_year[y][1] += p
                elif joint_priced(a):
                    joint += 1
        if per_year:
            b.append(f'<div class="sec"><div class="runhead"><span>{e(_p.analysis)}</span>'
                     f'<span>{e(_p.derived)}</span></div><div class="scroll"><table><thead><tr>'
                     f'<th>{_.year}</th><th class="r">{_.awards}</th><th class="r">{_.sum}</th>'
                     "</tr></thead><tbody>")
            for y in sorted(per_year, reverse=True):
                n_y, v_y = per_year[y]
                b.append(f'<tr><td class="mono">{e(y)}</td><td class="r num">{formato.count(n_y)}</td>'
                         f'<td class="r num">{formato.cell(v_y or None, empty_sr=_.no_own_amount)}</td></tr>')
            b.append("</tbody></table></div>")
            if joint:
                b.append(f'<p class="sub" style="margin:10px 0 0">'
                         f'{e(_if("joint_note_one" if joint == 1 else "joint_note", k=formato.count(joint)))}</p>')
            line = ""
            if len(c["buyers"]) == 1:
                line = _m("top_buyer_only", buyer=name_cut(next(iter(c["buyers"])), 90))
            elif len(c["buyers"]) > 1:
                # "most frequent" only when there is one: a tie, or a single award, is not a pattern
                (b1, k1), (_b2, k2) = c["buyers"].most_common(2)
                if k1 >= 2 and k1 > k2:
                    line = _m("top_buyer_share", buyer=name_cut(b1, 90), share=formato.pct(100 * k1 / len(rows)))
            if line:
                b.append(f'<p class="sub" style="margin:10px 0 0">{e(line)}</p>')
            b.append("</div>")

        # How large the awards are: counts per amount band, read without a legend. It
        # replaces the bubble timeline (overlapping dots, ISO ends, contrast 1.68:1).
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
                b.append(f'<figure class="rk" aria-labelledby="chart-sizes"><h3 id="chart-sizes">'
                         f'{e(_if("bands_title", name=name))}</h3><p class="lede">'
                         f'{e(_if("bands_none", n=formato.count(len(rows))))}</p></figure>')
            else:
                band_rows = [(lingue.BANDS[LANG][i], None, bands[i], formato.count(bands[i])) for i in range(6)]
                note = ((_if("bands_median", m=formato.money(median(c["amounts"])))
                         if len(c["amounts"]) >= 3 else "")
                        + (" " + _i.bands_noown if bands[5] else ""))
                b.append(grafici.rank_list(band_rows[:5], other=band_rows[5], fig_id="chart-sizes",
                                           title=_if("bands_title", name=name), lede=_i.bands_lede,
                                           note=note.strip()))
        # ... and which ones they are: a 331 Mio. total is often one award
        own = sorted(((chf_amount(a), a) for a in rows
                      if chf_amount(a) is not None and len(winners(a)) == 1),
                     key=lambda x: -x[0])
        if len(own) >= 3:
            b.append(f'<div class="sec"><div class="runhead"><span>{_i.largest_h}</span><span></span></div>'
                     '<ul class="plain">')
            top3 = own[:3]
            heads3 = distinct_titles([de(a, "title") for _p, a in top3], 110)
            tw3 = twin_notes([a for _p, a in top3],
                             [(h, a.get("buyerName"), a.get("publicationDate"), formato.money(p))
                              for (p, a), h in zip(top3, heads3)])
            for i, ((p, a), head) in enumerate(zip(top3, heads3)):
                d = a.get("publicationDate") or ""
                meta = " · ".join(x for x in (e(a.get("buyerName") or ""), tt(d, formato.date(d)),
                                              e(tw3.get(i, ""))) if x)
                b.append(f'<li><div class="row"><div><a href="{award_href(a)}">'
                         f'{e(head)}</a>'
                         f'<span class="sub" style="display:block;margin-top:3px">{meta}</span></div>'
                         f'<span class="num" style="white-space:nowrap">{formato.money_data(p)}</span></div></li>')
            b.append("</ul>")
            top1 = own[0][0]
            if c["value"] and top1 / c["value"] >= .25:
                share = formato.pct(100 * top1 / c["value"])
                if share.startswith(">"):          # 99.6 % is not "100 %" when other amounts exist
                    share = _if("over_pct", p=share[1:])
                b.append(f'<p class="sub" style="margin:10px 0 0">'
                         f'{e(_if("largest_share", share=share))}</p>')
            b.append("</div>")

        b.append(f'<div class="sec"><div class="runhead"><span>{_.awards}</span>'
                 f'<span>{_.chronological}</span></div><div class="scroll"><table><thead><tr>'
                 f'<th style="width:96px">{_.date}</th><th>{_.contract}</th><th>{_.buyer}</th>'
                 f'<th style="width:44px">{_.canton_abbr}</th><th class="r">{_.amount}</th>'
                 "</tr></thead><tbody>")
        heads = distinct_titles([de(a, "title") for a in rows], 130)
        # An award to several firms: this firm's own price, marked as the price of its offer — the
        # column showed the FIRST firm's price under 'an mehrere Unternehmen' (08.10.2026). It
        # stays out of every sum on the page, like before.
        amts = []
        for a in rows:
            firms = firm_prices(a)
            if len(firms) > 1:
                p, cur = next(((fp, fc) for fw, fp, fc, _n in firms if slug(fw) == s), (None, cur_of(a)))
                amts.append(formato.cell(p, cur, empty_sr=_.not_published)
                            + f'<span class="sub" style="display:block">'
                            f'{e(_if("own_offer", n=formato.count(len(firms))) if p else _.joint)}</span>')
            else:
                amts.append(formato.cell(price_of(a), cur_of(a), empty_sr=_.not_published))
        twn = twin_notes(rows, [(a.get("publicationDate"), h, a.get("buyerName"), a.get("canton"), amt)
                                for a, h, amt in zip(rows, heads, amts)])
        for i, (a, head, amt) in enumerate(zip(rows, heads, amts)):
            d = a.get("publicationDate") or ""
            tn = twn.get(i)
            twin = f'<span class="sub" style="display:block;margin-top:2px">{e(tn)}</span>' if tn else ""
            b.append(
                f'<tr><td class="mono" style="font-size:12.5px">{tt(d, formato.date(d))}</td>'
                f'<td><a href="{award_href(a)}">{e(head)}</a>{twin}</td>'
                f'<td>{e(a.get("buyerName"))}</td><td>{abbr_canton(a.get("canton") or "")}</td>'
                f'<td class="r num">{amt}</td></tr>')
        b.append("</tbody></table></div></div>")

        m = open_for.get(s, [])
        if m:
            # was hardcoded German, shipped on 1,938 company pages in each of fr/it/en
            b.append(f'<div class="sec"><div class="runhead"><span>'
                     f'{e(_p.matched_tenders_one if len(m) == 1 else _p.matched_tenders)}'
                     f'</span><span>{formato.count(len(m))}</span></div>'
                     f'<p class="sub" style="margin:10px 0 0">{e(_p.matched_note)}</p>'
                     '<ul class="plain tl" style="margin-top:10px">')
            heads = distinct_titles([de(t, "title") for t in m], 120)
            labels = [short_sector(cpv_label(t.get("cpvCode"), de(t, "cpvLabel") or t.get("cpvLabel") or "") or "", 44)
                      for t in m]
            twins = twin_rows(list(zip(heads, labels)))
            for i, (t, head, label) in enumerate(zip(m, heads, labels)):
                dl = t.get("offerDeadline") or ""
                cls, when = due_cell(dl, formato.date(dl), until=True)
                b.append(f'<li><div class="row"><div><a href="{BASE}/{LANG}/auftrag/{e(t.get("projectId"))}/">'
                         f'{e(head)}</a><span class="sub" style="display:block;'
                         f'margin-top:3px">{e(t.get("buyerName"))} · {abbr_canton(t.get("canton") or "")} · '
                         f'{e(label)}{e(project_no(t)) if i in twins else ""}</span></div>'
                         f'<span class="when{cls}">{when}</span>'
                         "</div></li>")
            b.append("</ul></div>")

        if c["cpv"]:
            b.append(f'<div class="sec"><div class="runhead"><span>'
                     f'{_.activity if len(c["cpv"]) == 1 else _.activities}</span>'
                     f'<span>{formato.count(len(c["cpv"]))}</span></div><ul class="plain">')
            for (code, label), k in c["cpv"].most_common(8):
                cell = (f'<a href="{BASE}/{LANG}/bereich/{e(code)}/">{e(label)}</a>' if code in sectors
                        else e(label))
                b.append(f'<li><div class="row">{cell}'
                         f'<span class="sub num">{zuschlag(k)}</span></div></li>')
            b.append("</ul></div>")

        if c["buyers"]:
            b.append(f'<div class="sec"><div class="runhead"><span>'
                     f'{_.buyer if len(c["buyers"]) == 1 else _.buyers}</span>'
                     f'<span>{formato.count(len(c["buyers"]))}</span></div><div class="tags">')
            for bu, k in c["buyers"].most_common(12):
                hit = buyer_slugs.get(norm_buyer(bu))
                b.append(f'<a class="tag" href="{BASE}/{LANG}/auftraggeber/{e(hit[0])}/" title="{e(hit[1])}">'
                         f'{e(name_cut(hit[1], 60))} · {formato.count(k)}</a>' if hit
                         else f'<span class="tag" title="{e(bu)}">{e(name_cut(bu, 60))} · {formato.count(k)}</span>')
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

        kw = dict(n=zuschlag(len(rows)),
                  val=(_m("company_val", v=formato.money(c["value"])) if c["value"] else ""),
                  span=(f" ({span})" if span else ""))
        desc = desc_pick(_m("company_desc", name=name, **kw), _m("company_desc_short", name=name, **kw),
                         _m("company_desc_short", name=name, **{**kw, "span": ""}),
                         _m("company_desc_short", name=name_cut(name, 70), **{**kw, "span": ""}))
        pages[s] = {"name": name, "n": len(rows), "value": c["value"],
                    "cant": cants[0] if cants else "", "sector": sector}
        write(f"/{LANG}/unternehmen/{s}/index.html",
              page(ctitle[s], desc,
                   "\n".join(b), f"/{LANG}/unternehmen/{s}/", _.companies,
                   leaf=fit_title(name, "", tail_share=0)))
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
        if lines:
            out.append("<p>" + "<br>".join(e(x) for x in lines) + "</p>")
    return "".join(out)


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
            tail = _m("desc_won", who=ws[0]) + (
                _m("desc_amount", amount=formato.money(price, cur_of(aw))) if price else "")
        elif ws:
            tail = _m("desc_won_n", n=formato.count(len(ws)))
    return rec_title(rec), (src.get("buyerName") or "").strip(), tail


def award_descs(by_project: dict) -> dict:
    """projectId -> meta description. Pages whose simap titles are identical ('SGS Erweiterung
    Schulanlage Gutenbrunnen Schübelbach', projects 42676 and 42684) shared one description
    although their <title>s differ: those get the project number (verifier, 28.09.2026)."""
    parts = {pid: award_desc_parts(rec) for pid, rec in by_project.items()
             if pid and rec_title(rec)}
    out = {pid: award_desc(*p) for pid, p in parts.items()}
    seen = collections.Counter(out.values())
    for pid, (t, b, tail) in parts.items():
        if seen[out[pid]] > 1:
            src = rec_src(by_project[pid])
            num = src.get("projectNumber") or src.get("publicationNumber")
            if num:
                out[pid] = award_desc(t, b, tail + " · " + _if("project_no", n=num))
    return out


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
    if shared:
        out.append(note_html(shared))
    if block:
        return "".join(f'<div class="sub" style="margin-top:10px">{x}</div>' for x in out)
    return "".join(f'<span class="sub" style="display:block;margin-top:6px">{x}</span>' for x in out)


STYLE_GAP = ' style="margin-top:4px"'


def lot_table(rows: list, pages: dict, h1: str) -> str:
    """The awards of one project, a line each: the lot, who won it and for how much — the amount of
    an award to one firm, else each firm's own price beside its name and no figure for the lot.
    Each line is the anchor a company or buyer row links to (#lot-2). The page used to show one
    of them, the last one read: lot 15 of 6965, lot 2 of 28439 (08.10.2026)."""
    has_lots = any(a.get("_lot") is not None for a in rows)
    days = {(a.get("publicationDate") or "")[:10] for a in rows}
    out = [f'<div class="sec"><div class="runhead"><span>{_.lots if has_lots else _.awards}</span>'
           f'<span>{formato.count(len(rows))}</span></div><div class="scroll"><table><thead><tr>'
           + (f'<th style="width:52px">{_.lot}</th><th>{_.lot_name}</th>' if has_lots
              else f'<th style="width:96px">{_.date}</th>')
           + f'<th>{_.winner}</th><th class="r">{_.amount}</th></tr></thead><tbody>']
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
        subline = ('<span class="sub" style="display:block;margin-top:2px">'
                   + " · ".join(x for x in sub if x) + "</span>")
        if has_lots:
            name = lot_name(a)
            if _lot_key(name) == _lot_key(h1):
                name = ""          # a lot that only repeats the project's name
            n = a.get("_lot")
            first = (f'<td class="mono">{e(n) if n is not None else "–"}</td>'
                     f'<td>{e(name)}{subline}</td>')
        else:
            first = f'<td class="mono" style="font-size:12.5px">{tt(d, formato.date(d))}{subline}</td>'
        firms = firm_prices(a)
        if len(firms) > 1:
            each, _shared = firm_notes(firms)
            priced = any(p for _w, p, _c, _n in firms)
            # no price beside any name (4377: ten firms per lot): the names alone
            who = "".join(
                f'<div{STYLE_GAP if i else ""}>{firm_link(w, pages)}'
                + (f' <span class="sub num" style="white-space:nowrap">'
                   f'{formato.exact(p, c) if p else e(_.not_published)}</span>' if priced else "")
                + (f'<span class="sub" style="display:block">{note_html(nt)}</span>' if nt else "")
                + "</div>" for i, ((w, p, c, _n), nt) in enumerate(zip(firms, each))) + price_notes(firms)
            amt = (f'–<span class="sub" style="display:block">{e(_.per_firm)}</span>'
                   if priced else formato.cell(None, empty_sr=_.not_published))
        else:
            who = firm_link(firms[0][0], pages) if firms else "–"
            amt = formato.exact_cell(price_of(a), cur_of(a), empty_sr=_.not_published)
        out.append(f'<tr id="{e(a.get("_anchor") or "")}">{first}<td>{who}</td>'
                   f'<td class="r num">{amt}</td></tr>')
    out.append("</tbody></table></div></div>")
    return "\n".join(out)


def grouped_texts(rows: list, texts: list) -> str:
    """One text field of a project's awards: once when every lot has the same, else each text under
    the lots it belongs to ('Lose 2, 3'); the reason given for lot 2 is not lot 15's."""
    groups: dict = {}
    for a, t in zip(rows, texts):
        t = (t or "").strip()
        if t:
            groups.setdefault(_ws(t), (t, []))[1].append(a)
    if not groups:
        return ""
    if len(groups) == 1 and len(next(iter(groups.values()))[1]) == len(rows):
        return paras(next(iter(groups.values()))[0])
    out = []
    for t, members in groups.values():
        nums = [a["_lot"] for a in members if a.get("_lot") is not None]
        if len(nums) == len(members):
            label = (_if("lot_n", n=nums[0]) if len(nums) == 1
                     else _if("lots_list", n=", ".join(str(x) for x in nums)))
        else:
            label = ", ".join(_if("publication_no", n=a.get("publicationNumber") or "") for a in members)
        out.append(f'<p style="margin:0 0 4px"><strong>{e(label)}</strong></p>' + paras(t))
    return "".join(out)


def build_awards(awards: list, opens: list, expired: list, pages: dict, sectors: set[str],
                 buyer_slugs: dict, lot_sib: dict | None = None) -> int:
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
        # one award: its own record, as before; several (a project's lots): a line each
        aw = rows[0] if len(rows) == 1 else None
        many = len(rows) > 1
        award = (aw or {}).get("award") or {}

        # the status: open; due today with its time (the page is built in the morning, 08.10.2026);
        # past its deadline; or awarded
        today = due_today(dl) if is_tender and not gone else ""
        state = (f'<span class="state off"><i></i>{_.tender_expired}</span>' if gone
                 else f'<span class="state today"><i></i>{e(today)}</span>' if today
                 else f'<span class="state"><i></i>{_.tender_open if is_tender else _.award_granted}</span>')
        b = [f'<div class="title"><div>{state}'
             f'<h1 style="margin-top:12px;font-size:clamp(24px,3.4vw,34px)">{e(title)}</h1>'
             + (f'<p class="sum">{e(_m("expired_lead", when=formato.deadline(dl)))}</p>' if gone and dl else "")
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
            figs.append(f'<div class="fig wide{" off" if gone else ""}"><b>{tt(dl, formato.deadline(dl))}</b>'
                        f"<span>{_.deadline}</span></div>")
        ws = winners(aw) if aw else []
        firms = firm_prices(aw) if aw else []
        # The award page is the official record: the amount exactly as published, Rappen
        # included, with a rounded reading under it from one million up. Only for an award to
        # one firm: several firms have a price each, shown beside their names, and the award
        # has none (08.10.2026)
        price = price_of(aw) if aw and len(ws) == 1 else None
        if price:
            cur = cur_of(aw)
            approx = (f'<em class="approx">{e(_.approx.format(v=formato.money(price, cur)))}</em>'
                      if price >= 999_500 else "")
            figs.append(f'<div class="fig wide"><b>{formato.exact_tile(price, cur)}</b>'
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
        if many:
            b.append(lot_table(rows, pages, title))

        b.append('<div class="cols"><div class="prose">')
        if ws:
            b.append(f'<div class="runhead"><span>{_.award_to}</span>'
                     f'<span>{e(_if("joint_n", n=formato.count(len(ws)))) if len(ws) > 1 else ""}</span></div>')
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
                                 + (e(formato.exact(p, cur)) if p else e(_.not_published)))
                if known:
                    extra.append(f'{zuschlag(known["n"])} {_.in_register}')
                b.append(f'<div class="winner">{link}'
                         + (f'<div class="sub" style="margin-top:5px">' + " · ".join(extra)
                            + "</div>" if extra else "")
                         + (f'<div class="sub" style="margin-top:3px">{note_html(nt)}</div>' if nt else "")
                         + "</div>")
            if len(firms) > 1:
                b.append(price_notes(firms, block=True))
        if many:
            just = grouped_texts(rows, [(a.get("award") or {}).get("justification") for a in rows])
            body = grouped_texts(rows, [de(a, "description") for a in rows])
            if just:
                b.append(f'<h2 style="margin:34px 0 12px">{_.reason}</h2>' + just)
            if body:
                b.append(f'<h2 style="margin:30px 0 12px">{_.description}</h2>' + body)
        else:
            if award.get("justification"):
                b.append(f'<h2 style="margin:34px 0 12px">{_.reason}</h2>'
                         + paras(award["justification"]))
            body_txt = de(src, "description")
            if body_txt:
                b.append(f'<h2 style="margin:30px 0 12px">{_.description}</h2>'
                         + paras(body_txt))
        if src.get("simapUrl"):
            link = (f'<a href="{e(src["simapUrl"])}">'
                    + e(lingue.p("view_on_simap", LANG).format(n=src.get("projectNumber") or ""))
                    + "</a>")
            b.append('<div class="official">'
                     + e(_p.official_link).replace("{link}", link) + "</div>")
        sib = (lot_sib or {}).get(pid) if is_tender else None
        if sib:
            # the home shows these lots as one line ('… · 6 Lose') linking here
            b.append(f'<h2 id="lose" style="margin:30px 0 8px">{e(_i.other_lots)}</h2><ul class="plain tl">')
            for x, head in zip(sib, distinct_titles([de(x, "title") for x in sib], 100)):
                xd = x.get("offerDeadline") or ""
                cls, when = due_cell(xd, formato.date(xd), until=True)
                b.append(f'<li><div class="row"><a href="{BASE}/{LANG}/auftrag/{e(x.get("projectId"))}/">'
                         f'{e(head + project_no(x))}</a><span class="when{cls}">{when}</span></div></li>')
            b.append("</ul>")
        b.append("</div><div>")

        b.append(f'<div class="runhead"><span>{_.details}</span><span></span></div>'
                 '<div class="scroll"><table class="kv"><tbody>')
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
                   leaf=fit_title(title, "", tail_share=0),
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
    out = [(name + x, name) for x in (sfx, short, "") if len(name + x) <= 64]
    for x in (sfx, short):
        out.append(_ft(name, x, tail_share=0))
        if head:
            out.append(_ft(name, x, head_min=head))
        out += [_ft(name, x), _ft(name, x, tail_share=.7)]
    out.append(_ft(name, ""))
    return rank_titles(out, most=True)


def build_buyers(awards: list, comp: dict, pages: dict, sectors: set[str],
                 bmap: dict, floor: int = 3) -> list:
    """A page per contracting authority. "Welche Aufträge hat die Gemeinde X
    vergeben" is a proper-name search with a real reader behind it — a resident, a
    journalist, a competitor — and no site answers it today."""
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
        table, nfirms = firm_table(rows, comp, pages, limit=40)
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
        b = [f'<div class="title"><div><p class="eyebrow">{_.buyer}</p><h1>{e(name)}</h1>'
             f'<p class="sum">{lead}</p></div><dl class="rail">'
             + (f"<dt>{_.main_canton}</dt><dd>{e(canton_name_or(cant, cant))}</dd>" if cant else "")
             # one firm: its name, not "Impresa: 1" (which reads as a firm called 1)
             + (f"<dt>{_.company}</dt><dd>{e(only_firm(rows, comp))}</dd></dl></div>" if nfirms == 1
                else f"<dt>{lab_n(nfirms, 'companies')}</dt><dd>{formato.count(nfirms)}</dd></dl></div>"),
             '<div class="figures">',
             f'<div class="fig"><b>{formato.count(len(rows))}</b><span>{lab_n(len(rows), "awards")}</span></div>',
             f'<div class="fig"><b>{formato.count(nfirms)}</b><span>{lab_n(nfirms, "companies")}</span></div>',
             sum_tile(rows), "</div>"]
        b.append(month_chart(rows, _i.mc_title_buyer))
        b.append(f'<div class="half"><div><div class="runhead"><span>{_.companies}</span>'
                 f'<span>{_.by_awards}</span></div>' + table + "</div><div>"
                 + division_figure(rows, sect, sectors) + "</div></div>")
        b.append(f'<div class="sec"><div class="runhead"><span>{_.awards}</span>'
                 f"<span>{_.chronological}</span></div><div class=\"scroll\"><table><thead><tr>"
                 f'<th style="width:96px">{_.date}</th><th>{_.contract}</th><th>{_.winner}</th>'
                 f'<th class="r">{_.amount}</th></tr></thead><tbody>')
        recent = sorted(rows, key=lambda x: x.get("publicationDate") or "", reverse=True)[:60]
        heads = distinct_titles([de(a, "title") for a in recent], 110)
        # rows that still read the same (two projects under one title, or one project's lots
        # awarded separately) get the number that tells them apart
        amts = [award_cell(a) for a in recent]
        twn = twin_notes(recent, [(a.get("publicationDate"), h, tuple(winners(a)), amt)
                                  for a, h, amt in zip(recent, heads, amts)])
        for i, (a, head, amt) in enumerate(zip(recent, heads, amts)):
            ws = winners(a)
            who = " · ".join(
                (f'<a href="{BASE}/{LANG}/unternehmen/{e(slug(w))}/">{e(w)}</a>'
                 if slug(w) in pages else e(w)) for w in ws) or "–"
            d = a.get("publicationDate") or ""
            tn = twn.get(i)
            twin = f'<span class="sub" style="display:block;margin-top:2px">{e(tn)}</span>' if tn else ""
            b.append(f'<tr><td class="mono" style="font-size:12.5px">{tt(d, formato.date(d))}</td>'
                     f'<td><a href="{award_href(a)}">{e(head)}</a>{twin}</td>'
                     f'<td>{who}</td><td class="r num">{amt}</td></tr>')
        b.append("</tbody></table></div></div>")
        write(f"/{LANG}/auftraggeber/{sl}/index.html",
              page(btitle[key],
                   desc_pick(_m("buyer_desc", name=name, n=zuschlag(len(rows)), f=firms(nfirms)),
                             _m("buyer_desc_short", name=name, n=zuschlag(len(rows)), f=firms(nfirms)),
                             _m("buyer_desc_short", name=name_cut(name, 100), n=zuschlag(len(rows)),
                                f=firms(nfirms))),
                   "\n".join(b), f"/{LANG}/auftraggeber/{sl}/", _.buyers,
                   leaf=fit_title(name, "", tail_share=0)))
        out.append((sl, name, len(rows)))
    return out


# ------------------------------------------------------------------- the hubs

def only_firm(rows: list, comp: dict) -> str:
    """The single firm named across these rows, spelled as on its company page."""
    w = next((w for r in rows for w in winners(r)), "")
    return (comp.get(slug(w)) or {}).get("name") or w


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
    out = [f'<div class="scroll"><table><thead><tr><th>{_.company}</th>'
           f'<th class="r">{_.awards}</th><th class="r">{_.sum}</th></tr></thead><tbody>']
    # ties: the larger sum first, then the name — the same order on every build
    order = sorted(firms.items(), key=lambda kv: (-kv[1], -sums.get(kv[0], 0),
                                                  fold(seen_name.get(kv[0], ""))))[:limit]
    for sl, k in order:
        label = (comp.get(sl) or {}).get("name") or seen_name.get(sl, sl)
        cell = (f'<a href="{BASE}/{LANG}/unternehmen/{e(sl)}/">{e(label)}</a>'
                if sl in pages else e(label))
        out.append(f'<tr><td>{cell}</td><td class="r num">{formato.count(k)}</td>'
                   f'<td class="r num">{formato.cell(sums.get(sl) or None, empty_sr=_.no_own_amount)}</td></tr>')
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
    cut = _ft(short_sector(label, 63 - len(sfx)), sfx)
    # the name alone, whole, rather than 'Elektrizitätsverteilungs-… – CPV 31200000'
    bare = [(whole, whole)] if len(whole) <= 64 and _poor(cut[1]) else []
    return rank_titles([cut] + bare + [_ft(whole, sfx), _ft(whole, sfx, tail_share=.7, gap1=True)])[0]


def build_hubs(awards: list, comp: dict, pages: dict, sectors: set[str],
               open_cants: collections.Counter) -> tuple[list, list]:
    by_cant, by_cpv = collections.defaultdict(list), collections.defaultdict(list)
    for a in awards:
        if a.get("canton"):
            by_cant[a["canton"]].append(a)
        if a.get("cpvCode"):
            by_cpv[str(a["cpvCode"])].append(a)

    cant_list = sorted(by_cant.items(), key=lambda kv: -len(kv[1]))
    nav = (f'<div class="runhead" style="margin-top:26px"><span>{_i.all_cantons}</span>'
           f'<span>{_.awards}</span></div><div class="tags">'
           + "".join(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(c)}/">'
                     f'{e(canton_name_or(c, c))} · {formato.count(len(r))}</a>'
                     for c, r in cant_list) + "</div>")

    for code, rows in cant_list:
        name = canton_name_or(code, code)
        of = cant_of(code, name)
        table, nfirms = firm_table(rows, comp, pages)
        sect = collections.Counter(
            (cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") or "", str(a.get("cpvCode") or ""))
            for a in rows if a.get("cpvCode"))
        # the canton's open tenders, when it has any (only then does that page exist)
        open_link = ""
        if open_cants.get(code):
            k_open = open_cants[code]
            open_link = (f'<p style="margin:14px 0 0"><a class="tag on" href="{BASE}/{LANG}/ausschreibungen/{code}/">'
                         f'{e(_if("open_in_one" if k_open == 1 else "open_in", c=name, of=of, k=formato.count(k_open)))}</a></p>')
        nbuyers = len({a.get("buyerName") for a in rows})
        b = [f'<div class="title"><div><p class="eyebrow">{_.canton}</p><h1>{e(_m("canton_title", name=name, of=of))}</h1>'
             f'<p class="sum">' + e(_m("canton_lead_one" if len(rows) == 1 else "canton_lead",
                                       n=zuschlag(len(rows)), f=firms(nfirms), name=name, of=of))
             + "</p>" + open_link + "</div>"
             f'<dl class="rail"><dt>{_.abbr}</dt><dd class="mono">{e(code)}</dd>'
             f'<dt>{lab_n(nbuyers, "buyers")}</dt><dd>{formato.count(nbuyers)}</dd></dl></div>',
             '<div class="figures">',
             f'<div class="fig"><b>{formato.count(len(rows))}</b><span>{lab_n(len(rows), "awards")}</span></div>',
             f'<div class="fig"><b>{formato.count(nfirms)}</b><span>{lab_n(nfirms, "companies")}</span></div>',
             sum_tile(rows), "</div>"]
        b.append(month_chart(rows, _if("mc_title_canton", name=name, of=of)))
        b.append(f'<div class="half"><div><div class="runhead"><span>{_.companies}</span>'
                 f"<span>{_.by_awards}</span></div>" + table + "</div><div>"
                 + division_figure(rows, sect, sectors) + "</div></div>")
        b.append(nav)
        write(f"/{LANG}/kanton/{code}/index.html",
              page(canton_title(_m("canton_title", name=name, of=of), _m("canton_suffix")),
                   desc_pick(_m("canton_desc", n=zuschlag(len(rows)), name=name, of=of, f=firms(nfirms)),
                             _m("canton_desc_short", n=zuschlag(len(rows)), name=name, of=of, f=firms(nfirms))),
                   "\n".join(b), f"/{LANG}/kanton/{code}/", _.canton))

    cpv_list = [(c, r) for c, r in sorted(by_cpv.items(), key=lambda kv: -len(kv[1]))
                if c in sectors]
    for code, rows in cpv_list:
        label = next((cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") for a in rows
                      if cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "")), code)
        table, nfirms = firm_table(rows, comp, pages)
        cants = collections.Counter(a["canton"] for a in rows if a.get("canton"))
        # a division's own general code (72000000) names its division: the pills that link here
        # call it "Informatikdienstleistungen (allgemeiner Code)", the EU label reads otherwise
        general = code[2:] == "000000" and code[:2] in lingue.CPV_SHORT[LANG]
        eyebrow = (_if("sector_general", label=lingue.CPV_SHORT[LANG][code[:2]]) + f" · CPV {code}"
                   if general else f"{_.sector} · CPV {code}")
        # one canton: its name ("Kanton: 1" read as a canton called 1)
        rail_cant = (f'<dt>{_.canton}</dt><dd>{e(canton_name_or(next(iter(cants)), ""))}</dd>'
                     if len(cants) == 1 else
                     f'<dt>{lab_n(len(cants), "cantons")}</dt><dd>{formato.count(len(cants))}</dd>')
        b = [f'<div class="title"><div><p class="eyebrow">{e(eyebrow)}</p>'
             f'<h1>{e(label)}</h1><p class="sum">'
             + e(_m("sector_lead", n=zuschlag(len(rows)), f=firms(nfirms))) + "</p></div>"
             f'<dl class="rail"><dt>CPV</dt><dd class="mono">{e(code)}</dd>'
             f'{rail_cant}</dl></div>',
             '<div class="figures">',
             f'<div class="fig"><b>{formato.count(len(rows))}</b><span>{lab_n(len(rows), "awards")}</span></div>',
             f'<div class="fig"><b>{formato.count(nfirms)}</b><span>{lab_n(nfirms, "companies")}</span></div>',
             f'<div class="fig"><b>{formato.count(len(cants))}</b><span>{lab_n(len(cants), "cantons")}</span></div></div>',
             month_chart(rows, _i.mc_title_sector),
             f'<div class="sec"><div class="runhead"><span>{_.companies}</span>'
             f"<span>{_.by_awards}</span></div>" + table + "</div>",
             f'<div class="runhead" style="margin-top:26px"><span>{lab_n(len(cants), "cantons")}</span>'
             f'<span>{lab_n(len(rows), "awards")}</span></div><div class="tags">'
             + "".join(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(c)}/">'
                       f'{e(canton_name_or(c, c))} · {formato.count(k)}</a>'
                       # every canton: the tile above counts them all, and 14 of 18 read as
                       # the whole list (verifier 28.09.2026); there are at most 26
                       for c, k in cants.most_common()) + "</div>"]
        write(f"/{LANG}/bereich/{code}/index.html",
              page(sector_title(label, code),
                   # the counts first and the name shortened, so the snippet never ends mid-number
                   desc_pick(_m("sector_desc", n=zuschlag(len(rows)), label=short_sector(label, 70), f=firms(nfirms)),
                             _m("sector_desc_short", n=zuschlag(len(rows)), label=short_sector(label, 70),
                                f=firms(nfirms)),
                             _m("sector_desc_short", n=zuschlag(len(rows)), label=short_sector(label, 44),
                                f=firms(nfirms))),
                   "\n".join(b), f"/{LANG}/bereich/{code}/", _.sectors, leaf=short_sector(label, 64)))
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
}).catch(function(){b.disabled=false;f.submit();});});
var K='AG AI AR BE BL BS FR GE GL GR JU LU NE NW OW SG SH SO SZ TG TI UR VD VS ZG ZH'.split(' ');
function pre(){var q,d={},hit=0;try{q=new URLSearchParams(location.search)}catch(x){return}
if(!q.has('k')&&!q.has('b'))return;
try{d=JSON.parse(document.getElementById('abo-names').textContent)||{}}catch(x){d={}}
[['k',function(v){return K.indexOf(v)>=0}],['b',function(v){return /^[0-9]{2}$/.test(v)}]].forEach(function(g){
var n=g[0],ok=g[1],nm=d[n]||{},box=f.querySelector('.pills[data-g="'+n+'"]'),seen={},c=0,last=null;
q.getAll(n).join(',').split(',').forEach(function(v){v=v.trim().toUpperCase();
if(c>=5||!v||!ok(v)||seen[v])return;seen[v]=1;
var i=null,all=f.querySelectorAll('input[name="'+n+'"]'),z;
for(z=0;z<all.length;z++){if(all[z].value===v){i=all[z];break}}
if(!i){var t=Object.prototype.hasOwnProperty.call(nm,v)?String(nm[v]):'';if(!t||!box)return;
var l=document.createElement('label'),s=document.createElement('span'),ref=null;i=document.createElement('input');
i.type='checkbox';i.name=n;i.value=v;s.className='tag';s.textContent=t;l.appendChild(i);l.appendChild(s);
if(n==='k'){for(z=0;z<all.length;z++){if(all[z].value>v){ref=all[z].parentNode;break}}}else{ref=last?last.nextSibling:box.firstChild;last=l}
box.insertBefore(l,ref)}
i.checked=true;c++;hit++})});
if(!hit)return;fill();
var em=f.elements.EMAIL,sec=f.parentNode||f;try{sec.scrollIntoView({block:'start'})}catch(x){}
try{if(window.matchMedia&&matchMedia('(pointer:fine)').matches)em.focus({preventScroll:true})}catch(x){}}
pre();})();"""
# The prefill above reads ?k=ZH&b=45 (the links on the company pages): only the 26
# canton codes and two-digit CPV divisions are accepted, at most five of each. A value
# without a pill gets one, labelled from the build-time name map, never from the URL.


def build_abo(by_cant: dict, by_sect: dict, sect_name) -> None:
    mail = ABO_MAIL
    # all 26 cantons, in the reader's alphabetical order (AI was missing whenever it had
    # no open tender, and the Italian list was sorted by code)
    cant_pills = "".join(
        f'<label><input type="checkbox" name="k" value="{e(c)}"><span class="tag">{e(canton_name_or(c, c))}</span></label>'
        for c in sorted(CANTONS, key=lambda c: fold(canton_name_or(c, c))))
    # every industry with an open tender, like the tenders page (it listed 40 industries, each
    # with a feed, while this page offered 24 and said "every industry page has a feed")
    top_sect = sorted(by_sect.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    def pill(code2: str) -> str:
        return lingue.CPV_SHORT[LANG].get(code2) or short_sector(sect_name(code2), 40)

    sect_pills = "".join(
        f'<label><input type="checkbox" name="b" value="{e(c)}"><span class="tag">{e(pill(c))}</span></label>'
        for c, r in top_sect)
    # Names for pills the prefill may have to create: every canton, every CPV division,
    # in the page's language. Escaped so no label can close the script element.
    names = {"k": {c: canton_name_or(c, c) for c in sorted(CANTONS)},
             "b": {k[:2]: lingue.CPV_SHORT[LANG].get(k[:2]) or short_sector(cpv_label(k, ""), 40)
                   for k in sorted(_CPV) if re.fullmatch(r"\d{2}000000", k) and cpv_label(k, "")}}
    names_json = (json.dumps(names, ensure_ascii=False, sort_keys=True)
                  .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))
    form = (f'<div class="sec"><h2>{e(_m("abo_form_h2"))}</h2>'
            f'<form id="abo" class="form" method="post" action="{BREVO_FORM}" data-sending="{e(_m("abo_form_sending"))}" '
            f'data-ok="{e(_m("abo_form_ok"))}" data-err="{e(_m("abo_form_err", mail=mail))}">'
            f'<label class="f" for="abo-email">{e(_m("abo_form_email"))}</label>'
            f'<input id="abo-email" type="email" name="EMAIL" required autocomplete="email" '
            f'placeholder="{e(_m("abo_form_placeholder"))}">'
            f'<span class="f">{e(_m("abo_form_cantons"))}</span><div class="pills" data-g="k">{cant_pills}</div>'
            f'<span class="f">{e(_m("abo_form_sectors"))}</span><div class="pills" data-g="b">{sect_pills}</div>'
            # the pills reach KANTON/BRANCHE only through the script; without it both stay ALLE
            f'<noscript><p class="sub" style="margin:14px 0 0">{e(_m("abo_form_nojs"))}</p></noscript>'
            f'<input type="hidden" name="KANTON" value="ALLE"><input type="hidden" name="BRANCHE" value="ALLE">'
            f'<input type="hidden" name="SPRACHE" value="{LANG}"><input type="hidden" name="locale" value="{LANG}">'
            f'<input type="text" name="email_address_check" value="" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">'
            f'<button type="submit">{e(_m("abo_form_submit"))}</button>'
            f'<p class="msg" aria-live="polite"></p>'
            f'<p class="sub">{e(_m("abo_form_consent"))} <a href="{BASE}/{LANG}/datenschutz/">{e(_.privacy)}</a></p>'
            f'</form><script type="application/json" id="abo-names">{names_json}</script>'
            f'<script>{ABO_JS}</script></div>')
    b = [f'<div class="title"><div><p class="eyebrow">{_.tenders}</p><h1>{e(_m("abo_h1"))}</h1>'
         f'<p class="sum">{e(_m("abo_lead"))}</p></div></div>',
         form,
         f'<div class="sec"><h2>{e(_m("abo_email_alt_h2"))}</h2><p>'
         + e(_m("abo_email_text", mail=mail)).replace(e(mail), f'<a href="mailto:{mail}?subject=Abo">{e(mail)}</a>')
         + "</p></div>",
         f'<div class="sec"><h2>{e(_m("abo_rss_h2"))}</h2><p>{e(_m("abo_rss_text"))}</p>'
         f'<p><a class="tag" href="{ORIGIN}/{LANG}/ausschreibungen/feed.xml">{e(_m("abo_rss_all"))}</a></p>'
         f'<h3>{e(_m("abo_by_canton"))}</h3><div class="tags">'
         + "".join(f'<a class="tag" href="{ORIGIN}/{LANG}/ausschreibungen/{e(c)}/feed.xml">{e(canton_name_or(c, c))}</a>'
                   for c in sorted(by_cant, key=lambda c: fold(canton_name_or(c, c))))
         + f'</div><h3>{e(_m("abo_by_sector"))}</h3><div class="tags">'
         + "".join(f'<a class="tag" href="{ORIGIN}/{LANG}/ausschreibungen/bereich/{e(c)}/feed.xml">'
                   f'{e(pill(c))}</a>'
                   for c, r in top_sect)
         + "</div></div>"]
    write(f"/{LANG}/ausschreibungen/abo/index.html", page(
        fit_title(_m("abo_title"), "\u00a0– auftragsregister.ch"), _m("abo_desc"),
        "\n".join(b), f"/{LANG}/ausschreibungen/abo/", _.tenders))

def canton_list(by_cant: dict) -> str:
    """Open tenders per canton: all 26 by name, with the count and a bar, sorted by count.

    It replaces a heat grid whose legend said only "few … many", which hid the counts on
    phones and left Appenzell Innerrhoden out whenever it had nothing open. A canton with
    no open tender shows 0 and no link, because its tenders page is not written."""
    n = {c: len(by_cant.get(c, [])) for c in CANTONS}
    order = sorted(CANTONS, key=lambda c: (-n[c], fold(canton_name_or(c, c))))
    items = [(canton_name_or(c, c), f"{BASE}/{LANG}/ausschreibungen/{c}/" if n[c] else None,
              n[c], formato.count(n[c])) for c in order]
    return grafici.rank_list(items, fig_id="open-cantons-list", labelledby="open-cantons",
                             lede=_m("open_canton_lede", date=formato.date(DATA_DATE)), two_cols=True)


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


def open_sector_title(name: str, k: int) -> str:
    """'{branch}: 12 offene Ausschreibungen' within 64 characters: the branch name is cut, never
    the count ('Eaux usées, déchets, nettoyage … appels d’offres en cours' had lost it)."""
    h = _m("open_sector_title", name=name, n=open_n(k))
    if len(h) <= 64:
        return h
    room = 64 - (len(h) - len(name)) - 1
    t = _m("open_sector_title", name=cut_end(name, room) + "…", n=open_n(k)) if room >= 12 else ""
    return t if t and len(t) <= 64 else fit_title(h, "", tail_share=0)


def build_open(opens: list, sectors: set[str], buyer_slugs: dict) -> int:
    """The open tenders, whole and by canton.

    This is the part with intent behind it: someone searching for current tenders is
    looking to bid, not to browse. The pages carry the deadline first, because that is
    the fact that decides whether the rest matters.
    """
    def table(rows: list) -> str:
        out = [f'<div class="scroll"><table class="tl"><thead><tr><th style="width:104px">{_.deadline}</th>'
               f'<th>{_.tender}</th><th>{_.buyer}</th><th style="width:44px">{_.canton_abbr}</th>'
               "</tr></thead><tbody>"]
        rows = sorted(rows, key=lambda x: x.get("offerDeadline") or "9999")
        heads = distinct_titles([de(t, "title") for t in rows], 120)
        labels = [short_sector(cpv_label(t.get("cpvCode"), de(t, "cpvLabel") or t.get("cpvLabel") or "") or "", 60)
                  if (t.get("cpvLabel") or de(t, "cpvLabel")) else "" for t in rows]
        twins = twin_rows(list(zip(heads, labels)))
        for i, (t, head, label) in enumerate(zip(rows, heads, labels)):
            dl = t.get("offerDeadline") or ""
            sub = label + (project_no(t) if i in twins else "")
            cls, when = due_cell(dl, formato.date(dl))
            out.append(
                f'<tr><td class="when mono{cls}" style="font-size:12.5px">{when}</td>'
                f'<td><a href="{BASE}/{LANG}/auftrag/{e(t.get("projectId"))}/">{e(head)}</a>'
                + (f'<span class="sub" style="display:block;margin-top:2px">{e(sub.lstrip(" ·"))}</span>'
                   if sub else "")
                + f'</td><td>{e(t.get("buyerName"))}</td><td>{abbr_canton(t.get("canton") or "")}</td></tr>')
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
        return (lingue.CPV_SHORT[LANG].get(code2) or cpv_label(code2 + "000000", "")
                or next((de(t, "cpvLabel") or t.get("cpvLabel") or "" for t in by_sect[code2]), "")
                or code2)

    sect_nav = ('<div class="tags">'
                + "".join(f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/bereich/{e(c)}/">'
                          f'{e(sect_name(c))} · {formato.count(len(r))}</a>'
                          # all of them: the tile above counts every industry (40), and 24 pills
                          # under it left 16 unexplained
                          for c, r in sorted(by_sect.items(), key=lambda kv: (-len(kv[1]), kv[0])))
                + "</div>")
    nxt = next(iter(sorted(t.get("offerDeadline") for t in opens if t.get("offerDeadline"))), "")
    today = tt(DATA_DATE, formato.date(DATA_DATE))

    b = [f'<div class="title"><div><p class="eyebrow">{_.running}</p>'
         f"<h1>{e(_p.open_tenders_h1)}</h1>"
         f'<p class="sum">' + e(_m("open_lead", n=formato.count(len(opens)))) + "</p></div>"
         f'<dl class="rail"><dt>{_.as_of}</dt><dd>{today}</dd>'
         f"<dt>{lab_n(len(by_cant), 'cantons')}</dt><dd>{formato.count(len(by_cant))}</dd></dl></div>",
         f'<div class="figures">'
         f'<div class="fig money"><b class="num">{formato.count(len(opens))}</b>'
         f'<span>{e(_m("open_kpi_open"))}</span></div>'
         f'<div class="fig"><b class="num">{formato.count(len(by_cant))}</b>'
         f'<span>{e(_m("open_kpi_cantons"))}</span></div>'
         f'<div class="fig"><b class="num">{formato.count(len(by_sect))}</b>'
         f'<span>{e(_m("open_kpi_sectors"))}</span></div>'
         # .date: the date stays on one line ('08.10.20|26' on phones, 08.10.2026)
         f'<div class="fig date"><b class="num">{tt(nxt, formato.date(nxt))}</b>'
         f'<span>{e(_m("open_kpi_next"))}</span></div></div>',
         f'<div class="sec"><h2 id="open-cantons">{e(_m("open_by_canton_h2"))}</h2>' + canton_list(by_cant) + "</div>",
         # sorted BEFORE slicing: taking 400 in file order and then sorting those
         # states "the nearest deadlines" about an arbitrary subset of the 588.
         '<div class="sec">' + table(sorted(
             opens, key=lambda x: x.get("offerDeadline") or "9999")[:SHOWN]) + "</div>",
         (f'<p class="sub" style="margin:12px 0 0">'
          + e(_if("showing_n", n=formato.count(SHOWN), total=formato.count(len(opens)))) + "</p>"
          if len(opens) > SHOWN else ""),
         abo_block(f"/{LANG}/ausschreibungen/feed.xml"),
         f'<div class="sec"><h2>{e(_m("open_by_sector_h2"))}</h2>' + sect_nav + "</div>",
         f'<div class="sec"><h2>{e(_m("open_howto_h2"))}</h2><p>{e(_m("open_howto"))}</p></div>',
         simap_compare()]
    write(f"/{LANG}/ausschreibungen/index.html", page(
        _m("open_title", n=formato.count(len(opens))), _m("open_desc", n=formato.count(len(opens))),
        "\n".join(b), f"/{LANG}/ausschreibungen/", _.tenders,
        head_extra=feed_head(f"/{LANG}/ausschreibungen/feed.xml", _m("feed_all"))))
    write(f"/{LANG}/ausschreibungen/feed.xml", feed_xml(_m("feed_all"), f"/{LANG}/ausschreibungen/feed.xml", opens))
    build_abo(by_cant, by_sect, sect_name)

    for code2, rows in by_sect.items():
        name = sect_name(code2)
        # one template for title and H1: "{name}: 762 offene Ausschreibungen"
        h = _m("open_sector_title", name=name, n=open_n(len(rows)))
        desc = _m("open_sector_desc_one" if len(rows) == 1 else "open_sector_desc",
                  n=open_n(len(rows)), name=name, code=code2)
        word = lingue.SECTOR_WORD[LANG].get(code2)
        seo_title = ""
        if word and len(rows) > 1:
            k = formato.count(len(rows))
            seo_title = first_fit(_m("open_sector_t1", word=word[0], k=k), _m("open_sector_t2", word=word[0], k=k))
            h = _m("open_sector_t2", word=word[0], k=k)
            desc = _m("open_sector_desc_word", k=k, w=word[1])
        b = [f'<div class="title"><div><p class="eyebrow">{_.running}</p>'
             f'<h1>{e(h)}</h1>'
             f'<p class="sum">' + e(desc) + "</p></div>"
             f'<dl class="rail"><dt>{_.as_of}</dt><dd>{today}</dd>'
             f'<dt>CPV</dt><dd class="mono">{e(code2)}</dd></dl></div>',
             '<div class="sec">' + table(rows) + "</div>",
             f'<div class="tags" style="margin-top:22px">'
             f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/">{e(_i.all_open)}</a></div>']
        fp = f"/{LANG}/ausschreibungen/bereich/{code2}/feed.xml"
        b.insert(1, abo_block(fp))
        write(f"/{LANG}/ausschreibungen/bereich/{code2}/index.html", page(
            seo_title or open_sector_title(name, len(rows)),
            desc if seo_title else desc_pick(desc, _m("open_sector_desc_one" if len(rows) == 1
                                                      else "open_sector_desc_short",
                                                      n=open_n(len(rows)), name=name, code=code2)),
            "\n".join(b), f"/{LANG}/ausschreibungen/bereich/{code2}/", _.tenders,
            head_extra=feed_head(fp, name)))
        write(f"/{LANG}/ausschreibungen/bereich/{code2}/feed.xml", feed_xml(name, fp, rows))

    for code, rows in by_cant.items():
        name = canton_name_or(code, code)
        of = cant_of(code, name)
        desc = _m("open_canton_desc_one" if len(rows) == 1 else "open_canton_desc",
                  n=open_n(len(rows)), name=name, of=of)
        b = [f'<div class="title"><div><p class="eyebrow">{_.running_canton}</p>'
             f'<h1>{e(_m("open_canton_h1", name=name, of=of))}</h1>'
             f'<p class="sum">' + e(desc) + "</p></div>"
             f'<dl class="rail"><dt>{_.as_of}</dt><dd>{today}</dd>'
             f'<dt>{_.canton}</dt><dd>{e(name)}</dd></dl></div>',
             '<div class="sec">' + table(rows) + "</div>",
             f'<div class="tags" style="margin-top:22px">'
             f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(code)}/">{e(_if("awarded_in", c=name, of=of))}</a>'
             f'<a class="tag" href="{BASE}/{LANG}/ausschreibungen/">{e(_i.all_open)}</a></div>']
        fp = f"/{LANG}/ausschreibungen/{code}/feed.xml"
        b.insert(1, abo_block(fp))
        write(f"/{LANG}/ausschreibungen/{code}/index.html", page(
            first_fit(*(_m(t, name=name, of=of, c=open_contracts(len(rows)))
                         for t in ("open_canton_t1", "open_canton_t2", "open_canton_t3"))), desc,
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
        # folded, so É files under E and Ö under O instead of after Z
        first = (fold(name.strip())[:1] or "#").upper()
        groups["0–9" if first.isdigit() else (first if first.isalpha() else "#")].append(
            (sl, name, n))
    b = [f'<div class="title"><div><p class="eyebrow">{e(kicker)}</p><h1>{e(h1)}</h1>'
         f'<p class="sum">{e(lead)}</p></div>'
         f'<dl class="rail"><dt>{_.entries}</dt><dd class="num">{formato.count(len(items))}</dd></dl></div>']
    letters = sorted(groups)
    b.append('<div class="tags" style="margin:22px 0 0">'
             + "".join(f'<a class="tag" href="#{e(g)}">{e(g)}</a>' for g in letters) + "</div>")
    for g in letters:
        rows = sorted(groups[g], key=lambda x: fold(x[1]))
        b.append(f'<div class="sec" id="{e(g)}"><div class="runhead"><span>{e(g)}</span>'
                 f'<span>{formato.count(len(rows))}</span></div><ul class="plain">')
        for sl, name, n in rows:
            b.append(f'<li><div class="row"><a href="/{LANG}{path}{e(sl)}/">{e(name)}</a>'
                     f'<span class="sub num">{zuschlag(n)}</span></div></li>')
        b.append("</ul></div>")
    write(f"/{LANG}{path}index.html", page(title, desc, "\n".join(b), f"/{LANG}{path}", kicker))


# ------------------------------------------------------------- home & sitemap

def build_home(pages: dict, comp: dict, awards: list, opens: list, cant_list, cpv_list) -> None:
    months = sorted({(a.get("publicationDate") or "")[:7] for a in awards if a.get("publicationDate")})
    span = formato.period(months[0], months[-1]) if months else ""
    winners_all = collections.Counter(slug(w) for a in awards for w in winners(a))
    soon = lot_groups(sorted((t for t in opens if t.get("offerDeadline")),
                             key=lambda t: t["offerDeadline"]))[:8]

    b = [f'<div class="title"><div><h1>{e(_p.tagline)}</h1>'
         f'<p class="sum">{e(_p.lead)}</p></div>'
         f'<dl class="rail"><dt>{_.source}</dt><dd>{e(_p.source_note)}</dd>'
         + (f"<dt>{_.period}</dt><dd>{e(span)}</dd>" if span else "")
         + f"<dt>{_.updated}</dt><dd>{tt(DATA_DATE, formato.date(DATA_DATE))}</dd></dl></div>",
         '<div class="figures">',
         f'<div class="fig"><b>{formato.count(len(awards))}</b><span>{lab_n(len(awards), "awards")}</span></div>',
         f'<div class="fig"><b>{formato.count(len(winners_all))}</b>'
         f'<span>{lab_n(len(winners_all), "companies")}</span></div>', sum_tile(awards)]
    b.append(f'<div class="fig"><b>{formato.count(len(opens))}</b><span>{e(_m("open_kpi_open"))}</span></div>'
             "</div>")
    # the monthly chart sits right under the key figures, with its own title and takeaway
    b.append(month_chart(awards, _i.mc_title_home))

    b.append('<div class="cols"><div>'
             f'<div class="runhead"><span>{_i.firms_cap}</span>'
             f'<span>{e(span)}</span></div>'
             '<div class="scroll"><table class="top"><thead><tr><th class="n0" style="width:34px"></th>'
             f'<th>{_.company}</th><th class="kt" style="width:46px">'
             f'<abbr title="{e(_.canton_most)}">{_.canton_abbr}</abbr></th>'
             f'<th class="r">{_.awards}</th><th class="r">{_.sum}</th></tr></thead><tbody>')
    rank = [(s, p) for s, p in sorted(pages.items(), key=lambda kv: (-kv[1]["n"], -kv[1]["value"]))][:25]
    for i, (s, p) in enumerate(rank, 1):
        b.append(f'<tr><td class="sub num n0">{i:02d}</td><td>'
                 f'<a href="{BASE}/{LANG}/unternehmen/{e(s)}/">{e(p["name"])}</a>'
                 + (f'<span class="sub" style="display:block;margin-top:2px">'
                    f'{e(short_sector(p["sector"], 46))}</span>' if p["sector"] else "")
                 + f'</td><td class="kt">{abbr_canton(p["cant"])}</td><td class="r num">{formato.count(p["n"])}</td>'
                 f'<td class="r num">{formato.cell(p["value"] or None, empty_sr=_.no_own_amount)}</td></tr>')
    b.append("</tbody></table></div></div><div>")

    if soon:
        b.append(f'<div class="runhead"><span>{_i.next_deadlines}</span>'
                 f'<span>{e(_if("open_count", n=formato.count(len(opens))))}</span></div><ul class="plain tl">')
        single = distinct_titles([de(g[0], "title") for _stem, g in soon], 66)
        for (stem, g), one in zip(soon, single):
            t = g[0]
            dl = t["offerDeadline"]
            if len(g) > 1:
                # the shared project name, cut at its end if at all: the lots' own names are
                # what the count replaces, so there is no tail worth keeping
                # no-break spaces around the dot: '· 6 lots' never starts a line of its own; the
                # link opens the first lot, whose page lists the others ("Weitere Lose")
                text = (name_cut(stem, 70) + "\u00a0·\u00a0"
                        + _if("lots_n", n=formato.count(len(g))).replace(" ", "\u00a0"))
            else:
                text = one
            cls, when = due_cell(dl, formato.date_short(dl))
            b.append(f'<li><div class="row"><a href="{BASE}/{LANG}/auftrag/{e(t.get("projectId"))}/">'
                     f'{e(text)}</a>'
                     f'<span class="when{cls}">{when}</span>'
                     "</div></li>")
        b.append("</ul>")
    b.append(f'<div class="runhead" style="margin-top:28px"><span>{_i.by_canton}</span>'
             f'<span>{formato.count(len(cant_list))} {_.cantons}</span></div><div class="tags">'
             + "".join(f'<a class="tag" href="{BASE}/{LANG}/kanton/{e(c)}/">'
                       f'{e(canton_name_or(c, c))} · {formato.count(len(r))}</a>'
                       for c, r in cant_list[:16]) + "</div>")
    b.append(f'<div class="runhead" style="margin-top:28px"><span>{_i.by_sector}</span>'
             f'<span>{formato.count(len(cpv_list))} {_.sectors}</span></div><ul class="plain">')
    for code, rows in cpv_list[:8]:
        label = next((cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "") for a in rows
                      if cpv_label(a.get("cpvCode"), de(a, "cpvLabel") or a.get("cpvLabel") or "")), code)
        b.append(f'<li><div class="row"><a href="{BASE}/{LANG}/bereich/{e(code)}/">{e(label)}</a>'
                 f'<span class="sub num">{formato.count(len(rows))}</span></div></li>')
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

    # no separate notice box on the home: it repeated, word for word, the footer's first
    # paragraph right below it (verifier, 28.09.2026)

    write(f"/{LANG}/index.html", page(
        _m("home_title"), _m("home_desc", n=formato.count(len(awards))),
        "\n".join(b), f"/{LANG}/"))




OPERATOR_NAME = "Riccardo Di Lullo"
OPERATOR_EMAIL = "dilulloriccardo@gmail.com"     # already public in the repo history


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


def build_abo_status() -> None:
    """The two pages Brevo sends people to: after the form (check your mail) and after
    the opt-in click (done). The redirect target is one fixed URL per form, so these
    live outside the language tree, carry all four languages and stay out of the index."""
    for slug, key in (("check", "abo_check"), ("ok", "abo_ok")):
        blocks = "".join(
            f'<p{"" if l == "de" else f" lang={chr(34)}{l}{chr(34)}"}><b>{e(NAMES[l])}</b>{lingue.COLON[l]} {e(lingue.m(key, l))} '
            f'<a href="{BASE}/{l}/ausschreibungen/abo/">{e(lingue.m("abo_back", l))}</a></p>' for l in LANGS)
        title = lingue.m(key + "_title", "de")
        html = page(title, lingue.m(key, "de"),
                    f'<div class="title"><div><p class="eyebrow">{e(_.tenders)}</p><h1>{e(title)}</h1></div></div>'
                    f'<div class="sec">{blocks}</div>', f"/abo/{slug}/", _.tenders, robots="noindex,nofollow")
        html = re.sub(r'<link rel="alternate"[^>]*>\n?', "", html)
        for l in LANGS:      # the masthead language switch: point it at the real abo pages
            html = html.replace(f'href="{BASE}/{l}/abo/{slug}/"', f'href="{BASE}/{l}/ausschreibungen/abo/"')
        write(f"/abo/{slug}/index.html", html)


# The 404 page's script: the language from the path (/fr/… -> French only, its title), and for a
# tender's address (/fr/auftrag/<id>/) the link to that project on simap.ch. Without it the page
# shows all four languages.
NF_JS = """(function(){var d=document.documentElement,p=location.pathname,b=%s,t=%s;
if(b&&p.indexOf(b)===0)p=p.slice(b.length);
var m=p.match(/^\\/(de|fr|it|en)(\\/|$)/),id=p.match(/^\\/(?:de|fr|it|en)\\/auftrag\\/([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})\\/?$/);
if(m){d.lang=m[1];d.setAttribute('data-l',m[1]);document.title=t[m[1]];
document.querySelector('.masthead a.name').href=b+'/'+m[1]+'/';document.querySelector('.langs a[lang='+m[1]+']').className='on'}
if(id)[].forEach.call(document.querySelectorAll('a[data-simap]'),function(a){
a.href='https://www.simap.ch/'+a.getAttribute('data-simap')+'/project-detail/'+id[1];a.hidden=false})})();"""
NF_CSS = ("[hidden]{display:none!important}html[data-l] .nf{display:none}"
          + ",".join(f"html[data-l={l}] .nf[lang={l}]" for l in LANGS) + "{display:block}"
          ".nf{margin-top:34px}.nf h2{margin:0 0 10px}.nf p{margin:0;color:var(--muted);max-width:62ch}")


def build_404() -> None:
    """GitHub Pages answers every missing URL with /404.html, and without one it served its own
    English 'Page not found' (08.10.2026). One page for the four languages, readable as it stands;
    the script shows the reader's language only, taken from the path. The links are root-relative,
    because the page is served at whatever depth the missing URL had; noindex, no canonical."""
    titles = {l: f"{lingue.m('nf_title', l)}\u00a0– {lingue.t('site', l)}" for l in LANGS}
    blocks = "".join(
        f'<div class="nf" lang="{l}"><h2>{e(lingue.m("nf_title", l))}</h2>'
        f'<p>{e(lingue.m("nf_text", l, days=EXPIRED_DAYS))}</p><div class="tags">'
        f'<a class="tag on" href="{BASE}/{l}/ausschreibungen/">{e(lingue.i("all_open", l))}</a>'
        f'<a class="tag" href="{BASE}/{l}/">{e(lingue.m("nf_home", l))}</a>'
        f'<a class="tag" href="https://www.simap.ch/{l}/" data-simap="{l}" hidden>{e(lingue.m("nf_simap", l))}</a>'
        "</div></div>" for l in LANGS)
    js = NF_JS % (json.dumps(BASE), json.dumps(titles, ensure_ascii=False).replace("<", "\\u003c"))
    html = ('<!doctype html>\n<html lang="de"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>404 · {" · ".join(e(lingue.m("nf_title", l)) for l in LANGS)}</title>\n'
            '<meta name="robots" content="noindex">\n'
            + re.search(r'<link rel="icon"[^>]*>\n', HEAD).group(0) +
            f'<link rel="preload" href="{BASE}/fonts/LibreFranklin-400-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
            f'<link rel="preload" href="{BASE}/fonts/BricolageGrotesque-800-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
            f'<link rel="stylesheet" href="{BASE}/style.css">\n<style>{NF_CSS}</style>\n</head><body>\n'
            f'<div class="wrap">\n<div class="masthead"><a class="name" href="{BASE}/">auftragsregister.ch</a>\n'
            '<span class="eyebrow">404</span></div>\n'
            f'<nav class="langs" aria-label="{e(" · ".join(lingue.t("language", l) for l in LANGS))}">'
            + "".join(f'<a href="{BASE}/{l}/" lang="{l}">{e(NAMES[l])}</a>' for l in LANGS) + "</nav>\n<main>\n"
            '<div class="title"><div><h1>404</h1></div></div>\n'
            + blocks + f"\n<script>{js}</script>\n</main><footer><p>"
            + " · ".join(f'<a href="{BASE}/{l}/impressum/" lang="{l}">{e(lingue.t("imprint", l))}</a>' for l in LANGS)
            + "</p></footer></div></body></html>")
    write("/404.html", html)


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




def build_language(awards: list, opens: list, expired: list) -> tuple[int, int, int, int, int, int]:
    comp = profile(awards)
    open_for = matches(comp, opens)
    sectors = sector_pages(awards)
    buyer_slugs = buyer_map(awards)
    keep = {n for n, c in comp.items() if len(c["awards"]) >= MIN_AWARDS}
    peer_map = peers(comp, keep)
    pages = build_companies(comp, open_for, sectors, buyer_slugs, peer_map)
    lot_sib = {}
    for _stem, g in lot_groups(sorted((t for t in opens if t.get("offerDeadline")),
                                      key=lambda t: t["offerDeadline"])):
        if len(g) > 1:
            for t in g:
                lot_sib[t.get("projectId")] = [x for x in g if x is not t]
    n_aw = build_awards(awards, opens, expired, pages, sectors, buyer_slugs, lot_sib)
    buyers = build_buyers(awards, comp, pages, sectors, buyer_slugs)
    open_cants = collections.Counter(t["canton"] for t in opens if t.get("canton"))
    cant_list, cpv_list = build_hubs(awards, comp, pages, sectors, open_cants)
    n_open = build_open(opens, sectors, buyer_slugs)
    build_index("/unternehmen/", _.companies, _i.companies_h1, _i.companies_lead,
                [(sl, p["name"], p["n"]) for sl, p in pages.items()],
                _i.companies_title, _if("companies_desc", n=formato.count(len(pages))))
    build_index("/auftraggeber/", _.buyers, _i.buyers_h1, _i.buyers_lead,
                [(sl, n, k) for sl, n, k in buyers],
                _i.buyers_title, _if("buyers_desc", n=formato.count(len(buyers))))
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
    awards, opens, expired = load()
    _SHARED.update(find_shared(awards + opens + expired))
    global DATA_DATE
    DATA_DATE = max(((a.get("publicationDate") or "")[:10] for a in awards), default=TODAY) or TODAY
    print(f"  dati    : {len(awards)} aggiudicazioni · {len(opens)} bandi aperti · "
          f"{len(expired)} scaduti con pagina (fino a {EXPIRED_DAYS} giorni) · dati al {DATA_DATE}")
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
    build_root()
    build_abo_status()
    build_404()
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
        # The French pages space digit groups and ':' ';' '?' '!' '%' with U+202F. Google's
        # subsets have no glyph for it, so the browser fell back to a system font that draws it
        # 1.3-1.8 px wide: '888 382 352.95' read as one run of digits (verifier, 28.09.2026).
        # The *-latin.woff2 files in fonts/ were patched once (U+202F -> the space glyph);
        # warn if a font update ever brings the unpatched files back.
        try:
            from fontTools.ttLib import TTFont
            bad = [f.name for f in fdir.glob("*-latin.woff2") if 0x202F not in TTFont(f).getBestCmap()]
            if bad:
                print(f"  ATTENZIONE: font senza U+202F (spazio fine francese): {', '.join(bad)}")
        except Exception:
            pass
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
        if u == "/":       # la radice e' una copia di /de/ con canonical /de/ (build_root): resta raggiungibile, non va in sitemap
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
