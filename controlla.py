#!/usr/bin/env python3
"""Check the built site before it is published.

A broken internal link costs twice: the reader hits nothing, and the crawler spends
its budget on a 404 instead of a page. These are the checks that catch what the
generator cannot see about itself.
"""
from __future__ import annotations

import collections
import csv
import html as htmlmod
import io
import json
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "docs"
# The site can be served from a subdirectory (GitHub Pages project sites are), in
# which case every internal link carries that prefix while the files do not. Without
# stripping it, every link on the site reads as broken.
_d = ROOT / "dominio.txt"
_l = _d.read_text().strip().splitlines() if _d.exists() else []
SITE = _l[0].strip().rstrip("/") if _l else ""
BASE = _l[1].strip().rstrip("/") if len(_l) > 1 else ""



def check_absolute(pages: set, site: str, base: str) -> list[str]:
    """The URLs a page declares about ITSELF — canonical, hreflang, breadcrumb item,
    sitemap <loc>. These were never checked, and that is how 75,141 canonicals and
    375,705 hreflang alternates shipped pointing at 404s while this script reported
    zero broken links: it only ever looked at root-relative hrefs in the body.
    """
    import json as _json
    origin = site + base
    errs = []
    sample = sorted(OUT.rglob("index.html"))
    step = max(1, len(sample) // 400)          # a spread sample, not the first 400
    for f in sample[::step]:
        html = f.read_text(errors="replace")
        urls = re.findall(r'<link rel="canonical" href="([^"]+)"', html)
        urls += re.findall(r'<link rel="alternate" hreflang="[^"]+" href="([^"]+)"', html)
        urls += re.findall(r'"item": "([^"]+)"', html)
        for u in urls:
            if not u.startswith(origin + "/") and u != origin + "/":
                errs.append(f"{f.relative_to(OUT)}: URL assoluto senza prefisso — {u}")
                break
            rest = u[len(origin):] or "/"
            if rest not in pages:
                errs.append(f"{f.relative_to(OUT)}: URL assoluto verso una pagina "
                            f"inesistente — {u}")
                break
    for sm in OUT.glob("sitemap*.xml"):
        body = sm.read_text(errors="replace")
        locs = re.findall(r"<loc>([^<]+)</loc>", body)
        if len(locs) > 50_000:
            errs.append(f"{sm.name}: {len(locs)} URL, il limite del protocollo e' 50 000")
        bad = [u for u in locs if not u.startswith(origin + "/") and u != origin + "/"]
        if bad:
            errs.append(f"{sm.name}: {len(bad)} <loc> senza il prefisso, es. {bad[0]}")
        if sm.name != "sitemap.xml":
            missing = [u for u in locs
                       if (u[len(origin):] or "/") not in pages and not u.endswith(".xml")]
            if missing:
                errs.append(f"{sm.name}: {len(missing)} <loc> verso pagine inesistenti, "
                            f"es. {missing[0]}")
    return errs


_TENDER_LISTS = re.compile(r'<(table|ul) class="[^"]*\btl\b[^"]*"[^>]*>.*?</\1>', re.S)
_LISTS = re.compile(r'<tbody>.*?</tbody>|<ul class="plain[^"]*"[^>]*>.*?</ul>', re.S)
_ROWS = re.compile(r'<tr\b.*?</tr>|<li\b.*?</li>', re.S)


# ------------------------------------------------------------- step 3a (14.10.2026)
# Restated here rather than imported from genera: a check that reads the generator's own constant
# could not catch it changing.
RATE_FLOOR = 1000          # an award under CHF 1'000 is a unit rate: in no sum, no median
RATE_CUE_MAX = 5000        # fix round 1: so is one up to CHF 5'000 whose publication speaks of a day or hour rate
_RATE_CUE = re.compile(
    r"(?<![\w-])(?:(?-i:LSE)|location\s+de\s+(?:services|personnel)|Personal(?:verleih|ausleihe)\w*|Temporärpersonal"
    r"|Tagess[aä]tz\w*|Stundens[aä]tz\w*|Tagespauschal\w*|Regie(?!rung)\w*|pro\s+(?:Tag|Stunde|Arbeitstag)|Ans[aä]tz\w*"
    r"|tarifs?\s+(?:journalier|horaire)s?|taux\s+(?:journalier|horaire)s?|prix\s+(?:journalier|horaire)s?"
    r"|tariff[ae]\s+(?:giornalier|orari)[ae]|prestito\s+di\s+personale|(?:day|daily|hourly)\s+rates?"
    r"|postes?\s+externes?)(?![\w-])|délégation\s+d['’]activités(?![\w-])", re.I)


def rate_cue(a: dict) -> bool:
    aw = a.get("award") or {}
    parts = [a.get("title"), a.get("description"), aw.get("justification")]
    for f in ("title", "description"):
        parts += list(((a.get("translations") or {}).get(f) or {}).values())
    parts += [v.get("note") for v in (aw.get("vendors") or []) if isinstance(v, dict)]
    return bool(_RATE_CUE.search(" ".join(str(x) for x in parts if x)))


SIMAP_TERMS = "https://www.simap.ch/de/about/legal"
N_DIVISIONS = 45
_TOTAL = re.compile(r'<data value="(\d+)" id="total">')
_SRN = re.compile(r'<em class="sr">([\d’\u202f,\u00a0 ]+?)\s+\D')


def sum_ok(got: float, want: float) -> bool:
    """A page's CHF total equals the one recomputed from the records (expected_sums: one firm, francs,
    no unit rate): a total that counts a rate, a foreign amount or a joint award fails."""
    return abs(got - round(want, 2)) <= 0.05


def total_of(html: str):
    """The awards total a home, a canton page or the about page states (<data id="total">), or None."""
    m = _TOTAL.search(html)
    return int(m.group(1)) if m else None


def chart_sum(html: str):
    """The sum of the first monthly chart's columns (each says '781 Zuschläge' to screen readers), or
    None when the page draws no chart."""
    m = re.search(r'<figure class="mc"[^>]*>(.*?)</figure>', html, re.S)
    if not m or "<table" not in m.group(1):
        return None
    return sum(int(re.sub(r"\D", "", x)) for x in _SRN.findall(m.group(1)))


def nocant_of(html: str) -> int:
    """The awards without a canton the canton index lists (0 when it has no such section)."""
    m = re.search(r'<div class="sec" id="ohne-kanton"><div class="runhead"><h2>[^<]*</h2><span>([^<]*)</span>', html)
    return int(re.sub(r"\D", "", m.group(1))) if m else 0


def reconcile_totals(home: dict, about: dict, cantons: dict, nocant: dict, csv_rows: dict, nocant_csv: int,
                     chart: dict, canton_chart: dict) -> list:
    """The national total is the same everywhere (step 3a: the home said 18'552, the cantons and their
    CSVs 18'443): per language, the home's and the about page's figure, the sum of the 26 canton pages
    plus the awards without a canton, the home's monthly chart; and, for the files the four languages
    share, the rows of the canton CSVs plus the one without a canton. Each canton page's own chart and
    CSV agree with its figure."""
    errs = []
    for lang, total in sorted(home.items()):
        if total is None:
            errs.append(f"{lang}: la home non dichiara il totale")
            continue
        if about.get(lang) != total:
            errs.append(f"{lang}: Über {about.get(lang)} / home {total}")
        sc = sum(v for v in cantons.get(lang, {}).values() if v) + nocant.get(lang, 0)
        if sc != total:
            errs.append(f"{lang}: cantoni + senza cantone {sc} / home {total}")
        if chart.get(lang) is not None and chart[lang] != total:
            errs.append(f"{lang}: grafico mensile {chart[lang]} / home {total}")
        sv = sum(csv_rows.values()) + nocant_csv
        if sv != total:
            errs.append(f"{lang}: righe CSV dei cantoni + senza cantone {sv} / home {total}")
        for code, n in sorted(cantons.get(lang, {}).items()):
            if csv_rows.get(code) is not None and csv_rows[code] != n:
                errs.append(f"{lang}/kanton/{code}: CSV {csv_rows[code]} / pagina {n}")
            c = canton_chart.get(lang, {}).get(code)
            if c is not None and c != n:
                errs.append(f"{lang}/kanton/{code}: grafico {c} / pagina {n}")
    return errs


def company_buyer_errors(html: str, expected: int):
    """None when a company page lists every one of its contracting authorities (step 3a: 'Auftraggeber 71'
    showed 12), else 'shown / expected'."""
    m = re.search(r'<div class="sec" id="auftraggeber">.*?<ul class="plain">(.*?)</ul>', html, re.S)
    n = len(re.findall(r"<li\b", m.group(1))) if m else 0
    return None if n == expected else f"{n} / {expected}"


def form_branch_errors(html: str, divisions) -> list:
    """The alert form offers every Branche once (step 3a: 41 of 45; 14, 37, 73, 76 only by prefill)."""
    vals = re.findall(r'<input type="checkbox" name="b" value="(\d{2})"', html)
    errs = []
    if len(vals) != len(set(vals)):
        errs.append("branche doppie")
    miss, extra = sorted(set(divisions) - set(vals)), sorted(set(vals) - set(divisions))
    if miss:
        errs.append(f"mancano {', '.join(miss)}")
    if extra:
        errs.append(f"in piu' {', '.join(extra)}")
    if len(set(vals)) != N_DIVISIONS:
        errs.append(f"{len(set(vals))} branche invece di {N_DIVISIONS}")
    return errs


def atom_errors(xml_text: str) -> list:
    """An Atom feed RFC 4287 accepts: well-formed, a feed with id, title, updated and an author (none
    of the 288 had one; step 3a), each entry with id, title, updated and a link."""
    import xml.etree.ElementTree as ET
    A = "{http://www.w3.org/2005/Atom}"
    try:
        root = ET.fromstring(xml_text.encode("utf-8"))
    except ET.ParseError as ex:
        return [f"XML: {ex}"]
    if root.tag != A + "feed":
        return ["non e' un feed Atom"]
    errs = [f"feed senza <{x}>" for x in ("id", "title", "updated") if root.find(A + x) is None]
    if root.find(f"{A}author/{A}name") is None:
        errs.append("feed senza <author><name>")
    for ent in root.findall(A + "entry"):
        miss = [x for x in ("id", "title", "updated", "link") if ent.find(A + x) is None]
        if miss:
            errs.append(f"voce senza {', '.join(miss)}")
            break
    return errs


def jsonld_errors(html: str) -> list:
    """Every JSON-LD block of a page parses."""
    out = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(m.group(1))
        except ValueError as ex:
            out.append(str(ex)[:80])
    return out


def expected_sums(G, awards: list) -> dict:
    """'<lang>/<section>/<key>/' (and '<lang>/' for the home) -> the CHF sum the money tile of that
    home, canton, buyer or company page must state: the francs published for awards that name ONE
    firm, recomputed here from the records rather than taken from the generator; 0 means the page
    shows no money tile at all."""
    def single(rows):
        out = 0.0
        for a in rows:
            p = a.get("winnerPrice")
            if (len(G.winners(a)) == 1 and isinstance(p, (int, float)) and not isinstance(p, bool) and p
                    and not a.get("_price_repeat")
                    and (a.get("winnerCurrency") or "CHF").strip().upper() == "CHF"
                    # step 3a: an amount under CHF 1'000 is a unit rate and in no sum; fix round 1: up to
                    # CHF 5'000 with a rate cue too
                    and p >= RATE_FLOOR and not (p <= RATE_CUE_MAX and rate_cue(a))):
                out += p
        return out
    groups = collections.defaultdict(list)
    bmap = G.buyer_map(awards)
    for a in awards:
        groups[""].append(a)
        if a.get("canton"):
            groups["kanton/" + a["canton"]].append(a)
        hit = bmap.get(G.norm_buyer(a.get("buyerName") or "")) if a.get("buyerName") else None
        if hit:
            groups["auftraggeber/" + hit[0]].append(a)
        ws = G.winners(a)
        for w in dict.fromkeys(G.slug(x) for x in ws):
            groups["unternehmen/" + w].append(a)
    out = {}
    for k, rows in groups.items():
        if k.startswith("unternehmen/") and len(rows) < G.MIN_AWARDS:
            continue
        for lang in ("de", "fr", "it", "en"):
            out[f"{lang}/{k}/" if k else f"{lang}/"] = single(rows)
    return out


def _text(row: str) -> str:
    return " ".join(htmlmod.unescape(re.sub(r"<[^>]+>", " ", row)).split())


# ------------------------------------------------------------- step 3b (15.10.2026)
# The interactive layer: the data the scripts read, the words that depend on the reader's clock, the search
# that must work without JavaScript. Limits restated here, not imported (see above).
SHARD_MAX = 320_000           # bytes of one search shard
DATA_MAX = 6_000_000          # /daten/offen.json, /daten/suche/, /daten/kb/, /daten/abo-rate.json together
JS_MAX_GZ = 30_000            # /stand.js and /js/*.js together but the home's, gzip -9 (fix round 1: 25 -> 30 KB)
HOME_JS_MAX_GZ = 12_000       # /js/home.js alone, gzip -9 (step 4: the home's motion and its map)
FONTS_MAX = 120_000           # every woff2 in /fonts/ together (step 4)
FONTS_NEED = ("is.woff2", "is7.woff2", "lg.woff2", "is-ext.woff2", "is7-ext.woff2", "lg-ext.woff2",
              "InstrumentSans-OFL.txt", "LeagueGothic-OFL.txt")
MIN_REM = 0.8125              # the smallest font size the stylesheet may set: 13 px (step 4)
HOMES = ("/", "/de/", "/fr/", "/it/", "/en/")
LANGS4 = ("de", "fr", "it", "en")


def relative_patterns(lingue) -> list:
    """Regular expressions of the day-relative wording, in the four languages, from the scripts' templates
    ('noch {n} Tage' -> 'noch \d+ Tage'); no-break spaces match any space. The unmistakable ones ('läuft
    heute ab', 'expire demain', 'neu seit gestern' …) count anywhere; the ones prose also uses ('noch 90 Tage
    abrufbar' on the about page, 'seit gestern') only as a label: the whole text of an element, give or take
    a count before it. 'abgelaufen' alone is left out: it is also the static state 'Eingabefrist abgelaufen'
    of an expired tender, which is a fact."""
    out = []
    strong = [lingue.JS[k][l] for k in ("due_tomorrow", "new_today", "new_today_1", "new_yday", "new_yday_1")
              for l in LANGS4]
    strong += [lingue.META[k][l] for k in ("due_today", "due_today_bare") for l in LANGS4]
    weak = [lingue.JS[k][l] for k in ("due_days", "hidden_1", "hidden_n") for l in LANGS4]
    weak += ["seit gestern", "depuis hier", "da ieri", "since yesterday"]
    for t in strong + weak:
        rx = re.escape(t)
        rx = re.sub(r"\\\{[a-z]+\\\}", r"[\\d’ ,]+", rx)
        rx = rx.replace(" ", "[\\s  ]").replace("\\ ", "[\\s  ]")
        if t in weak:
            rx = r">[^<>]{0,30}" + rx + r"[^<>]{0,12}<"
        out.append(re.compile(rx, re.I))
    return out


_SCRIPT = re.compile(r"<script\b[^>]*>.*?</script>", re.S)
# a class the build used to set by its own date (14.10.2026): .today/.soon are the script's since step 3b
_REL_CLASS = re.compile(r'class="[^"]*\b(?:when|state|fig|dnew)\b[^"]*\b(?:today|soon)\b[^"]*"')


def relative_errors(html: str, patterns: list) -> list:
    """Day-relative wording or classes in a static page (they changed with the build's date and were wrong
    by evening; the reader's clock writes them now, through /stand.js)."""
    text = _SCRIPT.sub("", html)
    errs = [m.group(0) for m in _REL_CLASS.finditer(text)][:1]
    for rx in patterns:
        m = rx.search(text)
        if m:
            errs.append(m.group(0).strip("<>"))
    return errs


def json_errors(files: dict) -> list:
    """Every data file of the scripts parses (name -> bytes)."""
    errs = []
    for name, raw in sorted(files.items()):
        try:
            json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as ex:
            errs.append(f"{name}: {str(ex)[:80]}")
    return errs


def size_errors(sizes: dict, js_gz: int) -> list:
    """The byte limits: each search shard, the data all together, the scripts all together (gzip)."""
    errs = [f"{n}: {v} byte, oltre {SHARD_MAX}" for n, v in sorted(sizes.items())
            if n.startswith("/daten/suche/") and n != "/daten/suche/themen.json" and v > SHARD_MAX]
    tot = sum(sizes.values())
    if tot > DATA_MAX:
        errs.append(f"dati degli script {tot} byte, oltre {DATA_MAX}")
    if js_gz > JS_MAX_GZ:
        errs.append(f"script {js_gz} byte gzip, oltre {JS_MAX_GZ}")
    return errs


def search_index_errors(shards: dict, companies: dict, buyers: dict, pages: set) -> list:
    """Every company and every contracting authority is in the search index exactly once — one entry, the
    same in every shard it sits in, none missing, none extra — and links where it should: a company or an
    authority with a page to that page, one without to an award page that exists (companies: name ->
    (slug, awards, has page); buyers: name -> (slug, awards, has page))."""
    errs, seen = [], {"u": {}, "b": {}}
    for k, sh in sorted(shards.items()):
        for kind in ("u", "f", "b", "g"):
            names = [x[0] for x in sh.get(kind, [])]
            if len(names) != len(set(names)):
                errs.append(f"shard {k}: {kind} doppio")
            for x in sh.get(kind, []):
                grp = "u" if kind in "uf" else "b"
                prev = seen[grp].get(x[0])
                if prev is not None and prev != (kind, x):
                    errs.append(f"{x[0]}: voci diverse fra gli shard")
                seen[grp][x[0]] = (kind, x)
    for grp, want, kind_page, sec in (("u", companies, "u", "unternehmen"), ("b", buyers, "b", "auftraggeber")):
        got = seen[grp]
        miss, extra = sorted(set(want) - set(got)), sorted(set(got) - set(want))
        if miss:
            errs.append(f"{sec}: {len(miss)} mancanti, es. {miss[0]}")
        if extra:
            errs.append(f"{sec}: {len(extra)} in piu', es. {extra[0]}")
        for name, (kind, x) in got.items():
            if name not in want:
                continue
            sl, n, has_page = want[name]
            if has_page != (kind == kind_page):
                errs.append(f"{sec}/{name}: pagina {'mancante' if has_page else 'inesistente'} nell'indice")
            elif kind == kind_page:
                if (x[1] or sl) != sl or f"/de/{sec}/{sl}/" not in pages or x[2] != n:
                    errs.append(f"{sec}/{name}: link o conteggio sbagliato")
            elif f"/de/auftrag/{x[1].split('#')[0]}" not in pages:
                errs.append(f"{sec}/{name}: pagina del zuschlag inesistente {x[1]}")
    return errs[:20] if len(errs) > 20 else errs


def open_index_errors(offen: dict, open_ids: set) -> list:
    """/daten/offen.json holds every open tender exactly once: the tenders whose page is open."""
    ids = [r[0] for r in offen.get("t", [])]
    errs = []
    if len(ids) != len(set(ids)):
        errs.append(f"{len(ids) - len(set(ids))} bandi doppi")
    miss, extra = open_ids - set(ids), set(ids) - open_ids
    if miss:
        errs.append(f"{len(miss)} bandi aperti mancanti, es. {sorted(miss)[0]}")
    if extra:
        errs.append(f"{len(extra)} bandi che non sono aperti, es. {sorted(extra)[0]}")
    for r in offen.get("t", []):
        if not (isinstance(r, list) and len(r) == 8 and r[1] and 0 <= r[5] < len(offen.get("b", []))):
            errs.append(f"riga malformata {str(r)[:60]}")
            break
    return errs


def open_count_errors(offen: dict, counts: dict) -> list:
    """/daten/offen-n.json (the pills' counts on the award pages) says what /daten/offen.json holds: the open
    tenders per canton (each canton a tender is listed under) and per Branche."""
    k, b = collections.Counter(), collections.Counter()
    for r in offen.get("t", []):
        for c in r[3].replace("*", "").split():
            k[c] += 1
        if r[4][:2] in offen.get("d", {}):
            b[r[4][:2]] += 1
    errs = [f"cantone {c}: {counts.get('k', {}).get(c)} / {n}" for c, n in sorted(k.items()) if counts.get("k", {}).get(c) != n]
    errs += [f"branca {c}: {counts.get('b', {}).get(c)} / {n}" for c, n in sorted(b.items()) if counts.get("b", {}).get(c) != n]
    if sum(counts.get("k", {}).values()) != sum(k.values()) or sum(counts.get("b", {}).values()) != sum(b.values()):
        errs.append("totali diversi")
    return errs


def search_page_errors(pages: set) -> list:
    """The header's search works without JavaScript: it submits to /xx/suche/, which exists in each language."""
    return [f"/{l}/suche/ mancante" for l in LANGS4 if f"/{l}/suche/" not in pages]


_SEARCH_FORM = re.compile(r'<header class="masthead">.*?<form role="search" action="([^"]+)"><input name="q" '
                          r'aria-label="[^"]+"><button>[^<]+</button></form>.*?</header>', re.S)


# ------------------------------------------------------------- step 5 (15.10.2026): one name per concept
# The copy pass gave each concept one name per language, the open tender (never a "contract") and «ohne Konto».
# The words it retired must not come back in the site's own text. Restated here, not imported from lingue (see above).
# Publications are quoted as published and may say anything ('Gratis-WLAN', 'Login-Prozess', 'Submissionen'
# in titles, 'E-mail system' as an EU CPV label): the lint reads only what the site writes itself, the chrome,
# with every quoted text masked inside it, so a title can never stop the nightly.
# Plain-language pass (22.10.2026, owner): the procurement office's words out of the chrome. The e-mail service is
# «Ausschreibungen per E-Mail» / «Appels d’offres par e-mail» / «Bandi via e-mail» / «Tenders by email» (no more
# E-Mail-Abo / alerte e-mail / avviso e-mail / email alert), the date «Aktualisiert am» / «Mis à jour le» /
# «Aggiornato al» / «Updated» (no more Daten vom / État des données / Stato dei dati / Data as of), the about page
# «So funktioniert’s» / «Comment ça marche» / «Come funziona» / «How it works», «gratis» in German (the owner's
# «Gratis abonnieren»; «kostenlos» retired), Settori / Secteurs / Sectors for the 45 CPV divisions, Kategorie for
# the 8-digit codes, Aziende, Enti pubblici / Acheteurs publics / Public buyers, and the old headings. Italian: the
# controls in the familiar imperative as the owner approved them («Ricevi», «Cerca», «Mostra tutti»), so the
# Lei-form controls are the retired ones now. The about page explains each official term once, in the singular
# («Zuschlag», «adjudicateur», «committente», «contracting authority»): those stay allowed.
# Natural-voice pass (owner, 23.10.2026): the office phrasing the owner named goes too, as the site's own words
# (never a publication's): «a scelta», «per lo più», «in mattinata», «qualora», «suddetto» …; «erfolgt», «mittels»,
# «gemäss», «zwecks»; «s’effectue», «afin de procéder»; «in order to», «utilise», «commence».
# A term matches as a whole word; one ending in '*' matches as the start of a word ('E-Mail-Abo*': E-Mail-Abos).
BANNED_TERMS = {
    "de": ("offene Aufträge", "Submissionen", "E-Mail-Alarm", "Benachrichtigung einrichten", "Login",
           "E-Mail-Abo*", "Daten vom", "Über das Register", "Methodik", "kostenlos*", "Bereiche", "verwandten Bereichen",
           "Unternehmen mit den meisten Zuschlägen", "Zuschläge pro Monat", "Zuschläge nach", "Zuschläge pro Jahr",
           "Unternehmen finden", "Unternehmen im Register",
           "erfolgt", "mittels", "bzgl.", "gemäss", "zwecks"),
    "fr": ("marchés ouverts", "marchés publics en cours", "alerte e-mail", "alertes e-mail", "État des données",
           "Méthodologie", "À propos du registre", "adjudicateurs", "Adjudications par", "Adjudications du",
           "le plus d’adjudications", "par branche", "Toutes les branches",
           "s’effectue", "afin de procéder"),
    "it": ("appalti aperti", "Vai al contenuto", "Vai all’avviso",
           # the Lei form of a control (the owner: «Ricevi», «Cerca», «Mostra tutti», «Iscriviti gratis»)
           "Si iscriva", "Mostri tutti", "Mostri gli altri", "Cerchi un", "Torni all*", "Azzeri i filtri",
           "Segnali un errore", "Apra questo bando", "Apra il bando", "Aggiunga la scadenza", "Attivi l’avviso",
           "Clicchi", "Tocchi", "Scelga", "Inserisca", "Riceva gratuitamente", "Cercare",
           "avviso e-mail", "avvisi e-mail", "Stato dei dati", "rami", "ramo", "committenti", "Metodologia",
           "Informazioni sul registro", "Imprese con più aggiudicazioni", "Aggiudicazioni al mese",
           "Aggiudicazioni per", "Ricevere automaticamente",
           "a scelta", "per lo più", "in mattinata", "suddett*", "qualora", "in merito a", "vigenti", "effettuare",
           "procedere a"),
    # fix round 3 (item 40): the term table's 'Open tender'
    "en": ("open contracts", "e-mail*", "Open for bids", "email alert*", "Data as of", "Methodology",
           "contracting authorities", "industries", "Awards by", "Awards per month", "Companies with the most awards",
           "in order to", "utilise*", "commence*"),
}


def _term_pat(t: str) -> str:
    """A banned term as a pattern: whole words, or the start of a word when it ends in '*'; any run of white
    space (the no-break spaces of the typography too) between its words."""
    body = re.escape(t.rstrip("*")).replace("\\ ", " ").replace(" ", r"\s+")
    return r"(?<![\w-])" + body + ("" if t.endswith("*") else r"(?![\w’'-])")


_TERM_RX = {l: re.compile("|".join(_term_pat(t) for t in ts), re.I) for l, ts in BANNED_TERMS.items()}
# Inside the chrome, the quoted texts: code, anything in another language (lang=), the links to a record, a
# company, an authority or a CPV category (their text is a title, a name or an EU label), the last breadcrumb,
# the sub-lines under a row (CPV labels, co-winners), table data cells (but the comparison table's), values.
_TERM_MASK = re.compile(
    r"<script\b.*?</script>|<style\b.*?</style>"
    r'|<(a|abbr|div|em|h[1-6]|li|nav|p|span|strong|td|ul)\b[^>]*\slang="[a-z]{2}"[^>]*>.*?</\1>'
    r'|<a\b[^>]*\shref="[^"]*/(?:auftrag|unternehmen|auftraggeber|bereich)/[^"/#?]+/[^"]*"[^>]*>.*?</a>'
    r'|<span aria-current="page"[^>]*>.*?</span>|<span class="sub[^"]*">.*?</span>'
    r'|<td\b(?![^>]*\bclass="c[ "])[^>]*>.*?</td>|<dd\b[^>]*>.*?</dd>|<div class="row">.*?</div>', re.S)
# The chrome of a page that also shows publications: the header, the breadcrumbs, the footer, the alert boxes,
# a record's buttons and state, the eyebrows, headings, leads and notes, the labels of rails, tables and forms.
_TERM_CHROME = re.compile(
    r'<header class="masthead">.*?</header>|<nav class="crumbs".*?</nav>|<footer>.*?</footer>'
    r'|<div class="glass alert".*?</p></div></div>|<div class="acts">.*?</div>|<span class="state">.*?</span>'
    r'|<p class="(?:eyebrow|sum|sub|lead|lede|note|aside|empty|dl|src|unit|act|s|aud)\b[^"]*">.*?</p>'
    r"|<h([1-6])\b[^>]*>.*?</h\1>|<dt>.*?</dt>|<th\b[^>]*>.*?</th>|<caption\b[^>]*>.*?</caption>"
    r"|<label\b[^>]*>.*?</label>|<legend\b[^>]*>.*?</legend>|<summary>.*?</summary>|<button\b[^>]*>.*?</button>"
    r'|<a class="(?:tag|btn|more|rep)\b[^"]*"[^>]*>.*?</a>|<td class="c[ "][^>]*>.*?</td>', re.S)
_TAG = re.compile(r"<[^>]+>")
# pages whose main shows no publication: the whole of it is the site's own text
_TERM_OWN = re.compile(r"^/(?:(?:de|fr|it|en)/(?:ueber|impressum|datenschutz|suche|ausschreibungen/abo)/|(?:de|fr|it|en)/)?$")
# pages about one record, firm, authority or CPV category: their H1, <title> and description quote it
_TERM_DATA = re.compile(r"^/(?:de|fr|it|en)/(?:auftrag|unternehmen|auftraggeber|bereich)/"
                        r"(?!(?:[a-z]|0-9|andere)(?:-az)?/$)[^/]+/$")
_TERM_HEAD = re.compile(r'<title>(.*?)</title>|<meta name="description" content="([^"]*)"', re.S)


def _term_text(fragment: str) -> str:
    return " ".join(htmlmod.unescape(_TAG.sub(" ", fragment)).replace("\u00ad", "").split())


def term_hits(text: str, lang: str) -> list:
    """The retired words of `lang` in a text, each with a little of its context."""
    return [text[max(0, m.start() - 30):m.end() + 30] for m in _TERM_RX[lang].finditer(text)]


def term_errors(here: str, html: str) -> list:
    """[(lang, context)] of every retired word in a page's own text. The two pages Brevo sends people to and the
    404 page carry the four languages side by side, each block with its lang=: each is read in its language."""
    if here in ("/abo/check/", "/abo/ok/", "/404.html"):
        out = []
        for m in re.finditer(r'<(div|nav|span|p)\b[^>]*\slang="([a-z]{2})"[^>]*>(.*?)</\1>', _SCRIPT.sub("", html), re.S):
            if m.group(2) in _TERM_RX:
                out += [(m.group(2), c) for c in term_hits(_term_text(m.group(3)), m.group(2))]
        return out
    p = here.strip("/").split("/")
    lang = p[0] if p and p[0] in LANGS4 else "de"
    head, _sep, body = html.partition("</head>")
    data_page = bool(_TERM_DATA.match(here))
    if data_page:
        # its own name or title, wherever the chrome repeats it ('Wie hoch sind die Zuschläge an X?')
        h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", body, re.S)
        if h1 and _TAG.sub("", h1.group(1)).strip():
            body = body.replace(h1.group(1), " ")
        if p[1] == "unternehmen":
            body = re.sub(r'<p class="eyebrow">.*?</p>', " ", body, flags=re.S)   # its main CPV label
        if p[1] == "bereich":
            body = re.sub(r'<p class="sum">.*?</p>', " ", body, flags=re.S)       # names without a page of their own
    if _TERM_OWN.match(here):
        parts = [body]
    else:
        parts = [m.group(0) for m in _TERM_CHROME.finditer(body)]
    if not data_page:
        parts += [x for m in _TERM_HEAD.finditer(head) for x in m.groups() if x]
    text = _term_text(_TERM_MASK.sub(" ", " ".join(parts)))
    return [(lang, c) for c in term_hits(text, lang)]


# The new names must be there, not only the old ones gone (plain-language pass, 22.10.2026): the menu's seven labels
# in order on every page (the four menus of the 404 page and of the two pages Brevo sends people to, each in its
# language), the e-mail service's page (its heading the service's name, its button the short call), the home's two
# calls to action, the date line of the footer and its template in /stand.js. Restated here, not imported from lingue.
NAV_WANT = {
    "de": ("Ausschreibungen", "Firmen", "Auftraggeber", "Kantone", "Branchen", "So funktioniert’s",
           "Ausschreibungen per E-Mail"),
    "fr": ("Appels d’offres", "Entreprises", "Acheteurs publics", "Cantons", "Secteurs", "Comment ça marche",
           "Appels d’offres par e-mail"),
    "it": ("Bandi", "Aziende", "Enti pubblici", "Cantoni", "Settori", "Come funziona", "Bandi via e-mail"),
    "en": ("Tenders", "Companies", "Public buyers", "Cantons", "Sectors", "How it works", "Tenders by email"),
}
CTA_MAIN = {"de": "Neue Ausschreibungen gratis per E-Mail",
            "fr": "Recevoir gratuitement les nouveaux appels d’offres par e-mail",
            "it": "Ricevi gratis i nuovi bandi via e-mail", "en": "Get new tenders by email – free"}
CTA_SHORT = {"de": "Gratis abonnieren", "fr": "S’abonner gratuitement", "it": "Iscriviti gratis",
             "en": "Subscribe free"}
# Italian elides before the 8th and the 11th ('Aggiornato all’08.10.2026')
DATE_LABEL = {"de": ("Aktualisiert am ",), "fr": ("Mis à jour le ",), "it": ("Aggiornato al ", "Aggiornato all’"),
              "en": ("Updated ",)}
_NAV = re.compile(r'<nav class="sitenav[^"]*"(?: data-nf)?(?: lang="([a-z]{2})")?[^>]*><ul>(.*?)</ul></nav>', re.S)
_NAV_A = re.compile(r"<a\b[^>]*>(.*?)</a>", re.S)


def _plain(fragment: str) -> str:
    return " ".join(htmlmod.unescape(_TAG.sub("", fragment)).split())


def required_errors(here: str, html: str) -> list:
    """[(what, what the page says)] wherever a page lacks the new name it must carry."""
    p = here.strip("/").split("/")
    lang = p[0] if p and p[0] in LANGS4 else "de"
    out = []
    for m in _NAV.finditer(html):
        lm = m.group(1) or lang
        got = tuple(_plain(a) for a in _NAV_A.findall(m.group(2)))
        if got != NAV_WANT.get(lm):
            out.append((f"menu {lm}", " · ".join(got)[:140]))
    body = html.partition('<main id="inhalt">')[2]
    if len(p) == 3 and p[1:] == ["ausschreibungen", "abo"]:
        h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", body, re.S)
        if not h1 or _plain(h1.group(1)) != NAV_WANT[lang][-1]:
            out.append(("titolo della pagina del servizio", _plain(h1.group(1)) if h1 else ""))
        btn = re.search(r'<button type="submit">(.*?)</button>', body, re.S)
        if not btn or _plain(btn.group(1)) != CTA_SHORT[lang]:
            out.append(("bottone del modulo", _plain(btn.group(1)) if btn else ""))
    if here in HOMES:
        ctas = [_plain(x) for x in re.findall(r'<p class="ctas"><a class="btn"[^>]*>(.*?)</a>', body, re.S)]
        if ctas[:1] != [CTA_MAIN[lang]] or ctas[1:2] != [CTA_SHORT[lang]]:
            out.append(("inviti della home", " | ".join(ctas)))
    st = re.search(r'<p class="stand">(.*?)</p>', html, re.S)
    if st and "<time" in st.group(1) and not _plain(st.group(1)).startswith(DATE_LABEL[lang]):
        out.append(("riga della data", _plain(st.group(1))[:60]))
    return out


def stand_template_errors(js: str) -> list:
    """/stand.js writes the footer's date line on every page that does not state it: its template per language."""
    i = js.find("var D = ")
    if i < 0:
        return ["/stand.js: dati non trovati"]
    try:
        data, _end = json.JSONDecoder().raw_decode(js, i + len("var D = "))
    except ValueError as ex:
        return [f"/stand.js: {ex}"]
    t = data.get("t") or {}
    return [f"/stand.js {l}: {t.get(l)!r}" for l in LANGS4
            if not (isinstance(t.get(l), str) and "{d}" in t[l] and t[l].startswith(DATE_LABEL[l]))]


# ------------------------------------------------------------- fix round 3 (21.10.2026)
# The H1 never repeats its eyebrow ('OFFENE AUSSCHREIBUNGEN · KANTON' over 'Offene Ausschreibungen im Kanton Zug' on
# 581 pages): no segment of the eyebrow whose words all stand in the H1. A record's own name (h1.rec: a company, an
# authority, a publication) may share a word with its sector by chance ('Fenster' over 'Fenster-Keller AG').
_EYEBROW = re.compile(r'<p class="eyebrow">(.*?)</p>', re.S)
_H1 = re.compile(r"<h1\b([^>]*)>(.*?)</h1>", re.S)


def _fold_words(s: str) -> list:
    import unicodedata
    s = unicodedata.normalize("NFKD", htmlmod.unescape(_TAG.sub(" ", s))).encode("ascii", "ignore").decode().lower()
    return [w for w in re.split(r"[^a-z0-9]+", s) if w]


def eyebrow_errors(html: str) -> list:
    main = html.partition('<main id="inhalt">')[2]
    eb, h1 = _EYEBROW.search(main), _H1.search(main)
    if not eb or not h1 or 'class="rec' in h1.group(1):
        return []
    hw = set(_fold_words(h1.group(2)))
    out = []
    for seg in htmlmod.unescape(_TAG.sub("", eb.group(1))).split("·"):
        ws = _fold_words(seg)
        if ws and not re.fullmatch(r"(cpv )?[\d ]+", " ".join(ws)) and all(w in hw for w in ws):
            out.append(f"«{seg.strip()}» nel titolo «{htmlmod.unescape(_TAG.sub('', h1.group(2)))[:60]}»")
    return out


# A name that ends in a full stop gets no second one from the sentence around it ('Coopérative T.B.R.C..'): the
# site's own sentences (leads, notes, sub-lines, the tiles' notes), never a quoted publication.
_OWN_SENTENCE = re.compile(r'<p class="(?:sum|sub|lede|note|empty)\b[^"]*">(.*?)</p>|<em class="approx">(.*?)</em>', re.S)
_DOUBLE_STOP = re.compile(r"(?<![.\d])\.\.(?![.\d/])")


def double_stop_errors(html: str) -> list:
    out = []
    for m in _OWN_SENTENCE.finditer(html.partition('<main id="inhalt">')[2]):
        frag = m.group(1) or m.group(2) or ""
        frag = re.sub(r'<(\w+)\b[^>]*\slang="[a-z]{2}"[^>]*>.*?</\1>', " ", frag, flags=re.S)   # a quoted text
        t = htmlmod.unescape(_TAG.sub("", frag))
        for x in _DOUBLE_STOP.finditer(t):
            out.append(t[max(0, x.start() - 40):x.end() + 5])
    return out


# French elides 'de', 'le', 'que' before a vowel, before an inserted name too ('Adjudications de Abteilung
# Tiefbau (CSV)' on 234 pages): every French template that inserts a value after them, filled with a name that
# starts with a vowel and one with an h, and the pages' own places where names are inserted (the CSV links, the notes).
# Fix round 4: before an h only a mute one ('d’Hôpital'): 'd’Haute école', 'd’Hochbauamt', 'd’HOLINGER' are wrong too.
# The mute-h starts restated from lingue._MUTE_H, not imported (see above).
_MUTE_H = r"(?i:h(?:ôpita|ôtel|ospi|abita|ygièn|éberg|orlog))"
_ELISION_SLOT = re.compile(r"(?<![\w’'])(?:de|De|le|Le|que|Que) \{(\w+)\}")
_NO_ELISION = re.compile(r"(?<![\w’'-])(?:de|De|le|Le|que|Que) (?=[AEIOUYÀÂÄÉÈÊËÎÏÔÖÛÜaeiouyàâäéèêëîïôöûü]|" + _MUTE_H + ")")
_BAD_ELISION = re.compile(r"(?<![\w’'-])(?:[dDlL]|[qQ]u)’(?=[Hh])(?!" + _MUTE_H + ")")


def elision_template_errors(lingue_mod) -> list:
    out = []
    for name, fn, tbl in (("META", lingue_mod.m, lingue_mod.META), ("IDX", lingue_mod.i, lingue_mod.IDX)):
        for key, d in tbl.items():
            tpl = d.get("fr") if isinstance(d, dict) else None
            if not isinstance(tpl, str) or not _ELISION_SLOT.search(tpl):
                continue
            fields = set(re.findall(r"\{(\w+)\}", tpl))
            for probe in ("Abteilung Tiefbau", "Hochbauamt", "Office fédéral des routes", "Hôpital du Valais", "HOLINGER AG"):
                kw = {f: "12" for f in fields}
                kw.update({m.group(1): probe for m in _ELISION_SLOT.finditer(tpl)})
                try:
                    txt = fn(key, "fr", **kw)
                except (KeyError, IndexError, ValueError):
                    continue
                if _NO_ELISION.search(txt) or _BAD_ELISION.search(txt):
                    out.append(f"{name}[{key!r}]: {txt[:90]}")
                    break
    return out


_FR_SLOTS = re.compile(r'<a [^>]*type="text/csv"[^>]*>(.*?)</a>|<p class="note">(.*?)</p>', re.S)


def elision_page_errors(html: str) -> list:
    out = []
    for m in _FR_SLOTS.finditer(html):
        t = htmlmod.unescape(_TAG.sub("", m.group(1) or m.group(2) or ""))
        for rx in (_NO_ELISION, _BAD_ELISION):
            for x in rx.finditer(t):
                out.append(t[max(0, x.start() - 25):x.end() + 25])
    return out


# ------------------------------------------------------------- structure (14.10.2026)
# The menu, the breadcrumbs, the headings, the prefilled alert links and the files the pages offer
# (calendar .ics, CSV): each page is read once, in the main loop, and the files after it.
_CRUMB_LD = re.compile(r'<script type="application/ld\+json">(\{"@context": "https://schema.org", '
                       r'"@type": "BreadcrumbList".*?)</script>', re.S)
_CRUMB_NAV = re.compile(r'<nav class="crumbs"[^>]*><ol>(.*?)</ol></nav>', re.S)
_CRUMB_LI = re.compile(r'<li>(?:<a href="([^"]*)">(.*?)</a>|<span aria-current="page"[^>]*>(.*?)</span>)</li>', re.S)
_HEADING = re.compile(r"<h([1-6])\b")
_ALERT = re.compile(r'href="([^"]*/ausschreibungen/abo/\?[^"]*)"')
_FILE_LINK = re.compile(r'<a [^>]*?href="(/[^"#?]*\.(?:ics|csv))"([^>]*)>')
_TH_NOSCOPE = re.compile(r"<th(?![^>]*\bscope=)(?=[\s>])")
_TABLE_NAME = re.compile(r"<table\b([^>]*)>(\s*<caption)?")
_REC_H1 = re.compile(r'<h1 class="rec([^"]*)"[^>]*>(.*?)</h1>', re.S)
_CANTONS = {"AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU", "LU", "NE", "NW", "OW", "SG",
            "SH", "SO", "SZ", "TG", "TI", "UR", "VD", "VS", "ZG", "ZH"}


class Structure:
    def __init__(self, origin: str, base: str, csv_cols: tuple, agg: dict | None = None):
        self.origin, self.base, self.csv_cols = origin, base, csv_cols
        self.agg = agg or {}
        self.errs = collections.defaultdict(list)          # kind -> [(page, detail)]
        self.files = {}                                     # docs path -> (page, link attributes)
        self.noindex = set()
        self.ics_pages = 0
        self.scripts = set()
        self.names = {}
        for l in ("de", "fr", "it", "en"):
            f = OUT / l / "ausschreibungen" / "abo" / "index.html"
            m = re.search(r'<script type="application/json" id="abo-names">(.*?)</script>',
                          f.read_text(encoding="utf-8") if f.exists() else "", re.S)
            self.names[l] = json.loads(m.group(1)) if m else {"k": {}, "b": {}}

    def err(self, kind: str, here: str, detail: str = "") -> None:
        self.errs[kind].append((here, detail))

    def page(self, here: str, html: str) -> None:
        lang = here.strip("/").split("/")[0] if here != "/" else "de"
        if lang not in self.names:
            lang = "de"
        # the menu, the skip link and the landmarks on every page
        for kind, needle in (("menu", '<nav class="sitenav"'), ("menu del telefono", '<details><summary>'),
                             ("salta al contenuto", 'class="skip" href="#inhalt"'),
                             ("<main id=inhalt>", '<main id="inhalt">'), ("<header>", '<header class="masthead">'),
                             ("<footer>", "<footer>"), ("riga dati nel piede", '<p class="stand">')):
            if needle not in html:
                self.err(kind, here)
        nav = re.search(r'<nav class="sitenav"[^>]*>(.*?)</nav>', html, re.S)
        if nav and nav.group(1).count("aria-current=") > 1:
            self.err("menu: piu' voci correnti", here)
        langs = re.search(r'<nav class="langs"[^>]*>(.*?)</nav>', html, re.S)
        if langs and any("lang=" not in a or "hreflang=" not in a for a in re.findall(r"<a [^>]*>", langs.group(1))):
            self.err("lingue senza lang/hreflang", here)
        # breadcrumbs: the visible trail is the BreadcrumbList, item by item
        ld = _CRUMB_LD.search(html)
        vis = _CRUMB_NAV.search(html)
        noindex = re.search(r'<meta name="robots" content="[^"]*noindex', html)
        home = here in ("/", "/de/", "/fr/", "/it/", "/en/")
        if not ld:
            # a noindex page carries no BreadcrumbList (14.10.2026): its visible trail must be there,
            # every level but the last a link, the last the page itself; the home carries none at all
            # (a one-item trail, step 3a)
            if home:
                if vis:
                    self.err("briciole visibili sulla home", here)
            elif not noindex:
                self.err("briciole: manca il BreadcrumbList", here)
            elif here not in ("/",) and not vis:
                self.err("briciole: mancano quelle visibili", here)
            elif vis:
                lis = _CRUMB_LI.findall(vis.group(1))
                if len(lis) < 2 or any(not h for h, _n, _c in lis[:-1]) or lis[-1][0]:
                    self.err("briciole: forma sbagliata", here)
        else:
            items = [(x["name"], x["item"]) for x in json.loads(ld.group(1))["itemListElement"]]
            if len(items) == 1:
                if vis:
                    self.err("briciole visibili sulla home", here)
            elif not vis:
                self.err("briciole: mancano quelle visibili", here)
            else:
                shown = []
                for href, name, cur in _CRUMB_LI.findall(vis.group(1)):
                    shown.append((htmlmod.unescape(name or cur), href))
                if len(shown) != len(items):
                    self.err("briciole: numero di livelli diverso", here, f"{len(shown)} / {len(items)}")
                else:
                    for (vn, vh), (ln, lu) in zip(shown, items):
                        if vn != ln:
                            self.err("briciole: nome diverso", here, f"{vn!r} / {ln!r}")
                            break
                        if vh and self.origin + (vh[len(self.base):] if self.base and vh.startswith(self.base) else vh) != lu:
                            self.err("briciole: link diverso", here, f"{vh} / {lu}")
                            break
                    if shown[-1][1]:
                        self.err("briciole: l'ultima e' un link", here)
        # headings: one h1, first; never a level skipped going down
        levels = [int(x) for x in _HEADING.findall(html)]
        if not levels or levels[0] != 1 or levels.count(1) != 1:
            self.err("titoli: h1 mancante, doppio o non primo", here, str(levels[:6]))
        else:
            for a, b in zip(levels, levels[1:]):
                if b > a + 1:
                    self.err("titoli: salto di livello", here, f"h{a} -> h{b}")
                    break
        # tables: a caption each, or the visible heading that names them (aria-labelledby, fix round 2), and every
        # header cell with its scope
        for attrs, capt in _TABLE_NAME.findall(html):
            ref = re.search(r'aria-labelledby="([^"]+)"', attrs)
            if not capt and not (ref and all(f'id="{x}"' in html for x in ref.group(1).split())):
                self.err("tabelle senza didascalia", here)
                break
        if _TH_NOSCOPE.search(html):
            self.err("celle d'intestazione senza scope", here)
        # the prefilled alert links: only canton codes and CPV divisions the form can name
        for href in _ALERT.findall(html):
            q = urllib.parse.parse_qs(urllib.parse.urlsplit(htmlmod.unescape(href)).query)
            bad = set(q) - {"k", "b"}
            ks = [v for x in q.get("k", []) for v in x.split(",")]
            bs = [v for x in q.get("b", []) for v in x.split(",")]
            if (bad or len(ks) > 5 or len(bs) > 5 or any(k not in _CANTONS for k in ks)
                    or any(not re.fullmatch(r"\d{2}", v) or v not in self.names[lang]["b"] for v in bs)):
                self.err("avviso precompilato non valido", here, href)
        parts = here.strip("/").split("/")
        want = None
        if len(parts) == 3 and parts[1] == "ausschreibungen" and parts[2] in _CANTONS:
            want = ("k", parts[2])
        elif len(parts) == 4 and parts[1:3] == ["ausschreibungen", "bereich"]:
            want = ("b", parts[3]) if parts[3] in self.names[lang]["b"] else None
        elif len(parts) == 3 and parts[1] == "kanton":
            want = ("k", parts[2])
        elif len(parts) == 3 and parts[1] == "bereich" and parts[2][:2] in self.names[lang]["b"]:
            want = ("b", parts[2][:2])
        elif len(parts) == 3 and parts[1] == "branche" and parts[2] in self.names[lang]["b"]:
            want = ("b", parts[2])
        if want:
            ok = any(want[1] in urllib.parse.parse_qs(urllib.parse.urlsplit(htmlmod.unescape(h)).query).get(want[0], [])
                     for h in _ALERT.findall(html))
            if not ok:
                self.err("avviso: manca il precompilato della pagina", here, f"{want[0]}={want[1]}")
        elif len(parts) == 3 and parts[1] in ("auftraggeber", "auftrag") and "/ausschreibungen/abo/" not in html:
            self.err("avviso: manca", here)
        # an open tender offers its deadline as a calendar file
        if '<div class="fig wide" data-deadline="' in html:
            self.ics_pages += 1
            if "/frist.ics" not in html:
                self.err("bando aperto senza .ics", here)
        for href, attrs in _FILE_LINK.findall(html):
            path = href[len(self.base):] if self.base and href.startswith(self.base) else href
            self.files[path] = (here, attrs)
        if re.search(r'<meta name="robots" content="[^"]*noindex', html):
            self.noindex.add(here)
        self.scripts.update(re.findall(r'<script src="([^"]+)"', html))

    def check_files(self) -> None:
        for path, (here, attrs) in self.files.items():
            f = OUT / path.lstrip("/")
            if not f.is_file():
                self.err("file mancante", here, path)
                continue
            raw = f.read_bytes()
            if path.endswith(".ics"):
                txt = raw.decode("utf-8")
                lines = txt.split("\r\n")
                pl = path.strip("/").split("/")[0]
                if pl in LANGS4 and simap_lang_errors(pl, txt.replace("\r\n ", "")):
                    self.err(".ics: simap.ch in un'altra lingua", here, path)
                if (not txt.startswith("BEGIN:VCALENDAR\r\n") or not txt.endswith("END:VCALENDAR\r\n")
                        or "\n" in txt.replace("\r\n", "")
                        or any(len(x.encode("utf-8")) > 75 for x in lines)
                        or not all(k in txt for k in ("BEGIN:VEVENT", "\r\nUID:", "\r\nDTSTAMP:",
                                                      "\r\nDTSTART", "\r\nSUMMARY:", "END:VEVENT"))):
                    self.err(".ics non valido", here, path)
            else:
                if not raw.startswith(b"\xef\xbb\xbf"):
                    self.err("CSV senza BOM", here, path)
                    continue
                rows = list(csv.reader(io.StringIO(raw[3:].decode("utf-8"), newline=""), delimiter=";"))
                head = tuple(rows[0]) if rows else ()
                if head != tuple(self.agg.get(path, self.csv_cols)):
                    self.err("CSV: intestazione sbagliata", here, path)
                elif any(len(r) != len(head) for r in rows[1:]):
                    self.err("CSV: righe con colonne diverse", here, path)
                m = re.search(r'data-rows="(\d+)"', attrs)
                if m and int(m.group(1)) != len(rows) - 1:
                    self.err("CSV: numero di righe diverso dal link", here, f"{path} {len(rows) - 1}/{m.group(1)}")
        n_ics = sum(1 for p in self.files if p.endswith(".ics"))
        if n_ics != self.ics_pages:
            self.err(".ics: file e bandi aperti non coincidono", "", f"{n_ics} / {self.ics_pages}")
        if not (OUT / "stand.js").is_file():
            self.err("stand.js mancante", "/")
        for js in re.findall(r"/js/(\w+)\.js", " ".join(self.scripts)):
            if not (OUT / "js" / f"{js}.js").is_file():
                self.err("script mancante", "/", js)
        for sm in OUT.glob("sitemap-*.xml"):
            origin = self.origin
            for u in re.findall(r"<loc>([^<]+)</loc>", sm.read_text(errors="replace")):
                rest = u[len(origin):] or "/"
                if rest in self.noindex:
                    self.err("sitemap con pagine noindex", sm.name, rest)

    def report(self) -> int:
        n = sum(len(v) for v in self.errs.values())
        print(f"  struttura (menu, briciole, titoli, avvisi, .ics, CSV)  {n} problemi"
              f" · {sum(1 for p in self.files if p.endswith('.ics'))} .ics"
              f" · {sum(1 for p in self.files if p.endswith('.csv'))} CSV")
        for kind, v in sorted(self.errs.items(), key=lambda kv: -len(kv[1])):
            print(f"    {len(v):>6}  {kind}" + (f"  es. {v[0][0]} {v[0][1]}"[:200] if v else ""))
        return n


# ------------------------------------------------------------- design (14.10.2026; A2 "Brass", step 4)
# The look as data: the colour tokens of the one dark theme against WCAG 2.2 AA (genera.CONTRAST), every
# font size in rem and none under 13 px (the shared sheet and the home's own), the fonts and their licences,
# the home's script on the home pages only, one unit per money column, and the head of each page — JSON-LD
# that parses, the share card where it belongs (and only there), feeds and icons that exist, and nothing
# fetched from another host.
_TOKEN = re.compile(r"--([\w-]+):\s*([^;]+?)\s*(?:;|$)")


def css_tokens(css: str) -> dict:
    """{'dark': {...}}: the custom properties of the stylesheet's first :root block. Design A2 (step 4) has
    one theme for everyone; a light theme coming back is an error (check_contrast)."""
    m = re.search(r":root\{(.*?)\}", css, re.S)
    return {"dark": dict(_TOKEN.findall(m.group(1))) if m else {}}


def _rgba(v: str):
    v = v.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", v)
    if m:
        h = m.group(1)
        h = "".join(c * 2 for c in h) if len(h) == 3 else h
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    m = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)", v)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4) or 1))
    return None


def _over(fg, bg):
    a = fg[3]
    return tuple(round(fg[i] * a + bg[i] * (1 - a)) for i in range(3)) + (1.0,)


def _lum(c) -> float:
    def ch(x):
        x /= 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(a, b) -> float:
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check_contrast(css: str, pairs) -> tuple[list, list]:
    """(errors, rows): every pair of genera.CONTRAST measured in both themes; a translucent colour is
    laid over --paper. rows: (theme, fg, bg, ratio, minimum) for the report."""
    errs, rows = [], []
    toks = css_tokens(css)
    if "prefers-color-scheme" in css:
        errs.append("un tema chiaro nel foglio: A2 ha un solo tema, scuro (passo 4)")
    for theme, t in toks.items():
        if not t:
            continue
        paper = _rgba(t.get("paper", ""))
        for fg, bg, need in pairs:
            a, b = _rgba(t.get(fg, "")), _rgba(t.get(bg, ""))
            if not (a and b and paper):
                errs.append(f"{theme}: token --{fg} o --{bg} mancante o non leggibile")
                continue
            b = _over(b, paper) if b[3] < 1 else b
            a = _over(a, b) if a[3] < 1 else a
            r = ratio(a, b)
            rows.append((theme, fg, bg, r, need))
            if r + 1e-9 < need:
                errs.append(f"{theme}: --{fg} su --{bg} {r:.2f}:1, ne servono {need}:1")
    return errs, rows


def _rem(v: str):
    """A font size in rem, or None when it is not a rem value."""
    m = re.fullmatch(r"([\d.]+)rem", v.strip().lower())
    return float(m.group(1)) if m else None


def _no_print(css: str) -> str:
    """The stylesheet without its @media print block: paper is set in points."""
    i = css.find("@media print{")
    if i < 0:
        return css
    depth, j = 0, i + len("@media print")
    while j < len(css):
        depth += {"{": 1, "}": -1}.get(css[j], 0)
        j += 1
        if depth == 0:
            break
    return css[:i] + css[j:]


def check_font_sizes(css: str) -> list:
    """Every font size in rem (step 4: none in px, em or %, so the reader's own text size scales them all) and
    none under MIN_REM (13 px): plain values, the smallest end of a clamp() (which must be rem; its middle may
    add vw), each term of a min() and the largest of a max(). The print sheet is left out (points)."""
    errs = []
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", _no_print(css)):
        sel, body = m.group(1).strip(), m.group(2)
        if sel == ".sr" or sel.startswith("@font-face"):
            continue
        for d in re.finditer(r"(?<![\w-])font(-size)?\s*:\s*([^;]+)", body):
            val = d.group(2).strip()
            if d.group(1) is None:
                # the shorthand: its size is the token before an optional /line-height
                sz = re.search(r"(?:^|\s)((?:max|min|clamp)\([^)]*\)+|[\d.]+(?:px|pt|rem|em|%))(?:/|\s)", val + " ")
                if not sz:
                    continue
                val = sz.group(1)
            if val in ("inherit", "initial", "unset", "100%"):
                continue
            if val.startswith(("max(", "min(", "clamp(")):
                inner = val[val.index("(") + 1:-1]
                terms = re.split(r",(?![^(]*\))", inner)
                if val.startswith("clamp("):
                    lo = _rem(terms[0])
                    ok = (lo is not None and lo >= MIN_REM
                          and not re.search(r"\d(?:px|pt|em|%)", inner.replace("rem", "")))
                elif val.startswith("min("):
                    ok = all(_rem(t) is not None and _rem(t) >= MIN_REM for t in terms if not re.search(r"v[wh]|svh", t))
                else:
                    ok = any(_rem(t) is not None and _rem(t) >= MIN_REM for t in terms)
            else:
                x = _rem(val)
                ok = x is not None and x >= MIN_REM
            if not ok:
                errs.append(f"{sel[:60]} {{font-size:{val}}}")
    return errs


def check_fonts(css: str, pages_head: str) -> list:
    """The fonts of design A2 (step 4): the six woff2 files and the two licences in /fonts/, together at most
    FONTS_MAX bytes; no file of the fonts it replaced; every url() of the sheet's @font-face there; the font a
    page preloads is one of them."""
    errs, fdir = [], OUT / "fonts"
    for name in FONTS_NEED:
        if not (fdir / name).is_file():
            errs.append(f"/fonts/{name} mancante")
    for old in ("lf.woff2", "lf-ext.woff2", "bg.woff2", "bg-ext.woff2"):
        if (fdir / old).exists():
            errs.append(f"/fonts/{old}: font sostituito ancora presente")
    tot = sum(f.stat().st_size for f in fdir.glob("*.woff2")) if fdir.is_dir() else 0
    if tot > FONTS_MAX:
        errs.append(f"font {tot} byte, oltre {FONTS_MAX}")
    for u in re.findall(r"@font-face\{[^}]*?url\(([^)]+)\)", css):
        if not (OUT / u.strip("'\"").split("?")[0].lstrip("/")[len(BASE.lstrip("/")):].lstrip("/")).is_file():
            errs.append(f"@font-face: {u} mancante")
    for u in re.findall(r'<link rel="preload" href="([^"]+)" as="font"', pages_head):
        if not (OUT / u[len(BASE):].lstrip("/")).is_file():
            errs.append(f"preload di un font che non esiste: {u}")
    return errs


_UNIT_RE = {"k": re.compile(r"(?:< )?\d{1,3}(?:[’ ,]\d{3})*"),
            "m": re.compile(r"(?:< )?\d{1,3}(?:[’ ,]\d{3})*[,.]\d"),
            "chf": re.compile(r"\d{1,3}(?:[’ ,]\d{3})*(?:\.\d{2})?")}
_SR = re.compile(r'<span class="(?:sr|sub[^"]*)">.*?</span>', re.S)


# a currency other than the franc, by its ISO code (the data has EUR and USD)
_FX = re.compile(r"\b(?:EUR|USD|GBP|JPY|CNY|SEK|NOK|DKK|PLN|CZK|HUF|CAD|AUD|RUB|INR|TRY)\b")


def money_column_errors(html: str, units: dict, seen: list | None = None) -> tuple[int, list]:
    """(money columns seen, [(kind, detail)]): every money column (th class amt) states its unit in its
    header, every figure under it is in that unit, and no amount in another currency stands in a CHF
    column at all — not even with its code (step 3a, 14.10.2026: 1'436 EUR cells sat under 'Betrag
    (Tsd. CHF)'); such an amount belongs in the row's title cell. seen: the units of the page's columns are
    appended to it (one_scale_errors)."""
    n, errs = 0, []
    for t in re.finditer(r"<table\b[^>]*>(.*?)</table>", html, re.S):
        body = t.group(1)
        head = re.search(r"<thead>(.*?)</thead>", body, re.S)
        if not head or 'class="r amt"' not in head.group(1):
            continue
        cells = re.findall(r"<t[hd]\b([^>]*)>(.*?)</t[hd]>", head.group(1), re.S)
        idx = next(i for i, (attrs, _x) in enumerate(cells) if "amt" in attrs)
        label = htmlmod.unescape(re.sub(r"<[^>]+>", "", cells[idx][1]))
        unit = next((u for txt, u in units.items() if f"({txt})" in label), None)
        n += 1
        if seen is not None and unit:
            seen.append(unit)
        if not unit:
            errs.append(("colonna importi: unità mancante nell'intestazione", label))
            continue
        tb = re.search(r"<tbody>(.*?)</tbody>", body, re.S)
        for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", tb.group(1) if tb else "", re.S):
            tds = re.findall(r"<td\b[^>]*>(.*?)</td>", row, re.S)
            if len(tds) <= idx:
                continue
            whole = htmlmod.unescape(re.sub(r"<[^>]+>", " ", tds[idx]))
            if _FX.search(whole):
                errs.append(("colonna importi CHF con una valuta estera", f"{label}: «{' '.join(whole.split())}»"))
                break
            txt = htmlmod.unescape(re.sub(r"<[^>]+>", "", _SR.sub("", tds[idx]))).strip()
            if txt in ("–", ""):
                continue          # not published, or not in francs (the dash's hidden text says why)
            if not _UNIT_RE[unit].fullmatch(txt):
                errs.append(("colonna importi: cifra fuori dall'unità della colonna", f"{label}: «{txt}»"))
                break
    return n, errs


# ------------------------------------------------------------- fix round 1 (20.10.2026)
# What the third audit found and must not come back: an element the scripts hide that stays visible, a page that
# prints one money table in thousands and another in millions, simap.ch opened in German from a French page, the
# total's note counting fewer awards than it leaves out, a sole trader's name in the sitemap.
def hidden_rule_errors(css: str) -> list:
    """The stylesheet keeps [hidden] hidden whatever display a component sets (.tl li, the stacked rows)."""
    return [] if re.search(r"\[hidden\]\{display:none!important\}", css) else ["[hidden]{display:none!important} manca in style.css"]


def one_scale_errors(units: list) -> list:
    """One scale per page: its money columns all in 'Tsd. CHF', all in 'Mio. CHF' or all exact."""
    return [("piu' scale nella stessa pagina", " / ".join(sorted(set(units))))] if len(set(units)) > 1 else []


_SIMAP_LINK = re.compile(r"https://www\.simap\.ch/([a-z]{2})/project-detail/")


def simap_lang_errors(lang: str, text: str) -> list:
    """Every link to a publication on simap.ch in the page's (or the calendar file's) language."""
    return sorted({x for x in _SIMAP_LINK.findall(text) if x != lang})


def sum_note_errors(html: str, joint: int) -> list:
    """The note under the home's total names every award to several firms it leaves out (fix round 1: 966 of
    1'140): the first figure of the first note of the money tile is that count."""
    m = re.search(r'<div class="fig money">.*?<em class="approx">([^<]*)</em>', html, re.S)
    if not joint:
        return []
    if not m:
        return ["nota della somma mancante"]
    k = re.search(r"\d[\d’'\u202f\u00a0 ,]*", m.group(1))
    n = int(re.sub(r"\D", "", k.group(0))) if k else None
    return [] if n == joint else [f"nota: {n} / {joint} zuschläge a piu' imprese"]


# a company page named after a natural person (genera.natural_person, restated): no legal form, no business
# word, two or three name-shaped words, one of them a common first name
_P_LEGAL = re.compile(r"(?i)(?<![\w])(?:ag|gmbh|sa|sàrl|sarl|sagl|kg|gen|genossenschaft|verein|stiftung|fondation|"
                      r"fondazione|ltd|inc|srl|spa|snc|co|cie|holding|aktiengesellschaft|gesellschaft|partner\w*)\.?(?![\w])")
_P_FIRM = re.compile(r"(?i)(?:technik|bau|werk|betrieb|dienst|service|consult|studio|atelier|büro|office|praxis|"
                     r"traduc|traduz|übersetz|schaft|handel|transport|reinigung|garten|ingenieur|architekt|design|"
                     r"solution|system|energie|immobil|treuhand|stadt|gemeinde|swiss|schweiz)")
_P_FIRST = frozenset("adelheid agata angelika anna barbara christian claudio concetta corina daniel isabelle karin "
                     "laurence maria matteo michael rodolfo sara stefan tatjana thomas valérie valerie viviana".split())


def person_name(name: str) -> bool:
    n = " ".join((name or "").split())
    if not n or _P_LEGAL.search(n) or _P_FIRM.search(n) or re.search(r"[\d&/+@()]", n):
        return False
    toks = [t for t in re.split(r"[\s,]+", n) if t]
    return 2 <= len(toks) <= 3 and all(re.fullmatch(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*", t) for t in toks) \
        and any(t.casefold() in _P_FIRST for t in toks)


# an e-mail address as the name of an entity (fix round 1: 'valentin.berclaz@eraneos.com' as a contracting
# authority): in a link to a company or an authority, a page's H1 or <title> or description, a table cell, a winner's
# card, the search index, the open tenders' file, the CSV files' name columns
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_ENT_LINK = re.compile(r'<a href="[^"]*/(?:unternehmen|auftraggeber)/[^"]*"[^>]*>(.*?)</a>|<span class="who">(.*?)</span>', re.S)
# a table cell, or a rail's value: a record's contracting authority stands in its rail since 23.10.2026
_ENT_TD = re.compile(r"<(?:td|dd)\b[^>]*>(.*?)</(?:td|dd)>", re.S)
# inside a cell: a record's title (a publication's text), the notes under a name, a mailto: link
_ENT_NOT = re.compile(r'<a href="[^"]*/auftrag/[^"]*"[^>]*>.*?</a>|<(span|div) class="sub[^"]*"[^>]*>.*?</\1>'
                      r'|<a href="mailto:[^"]*">.*?</a>', re.S)
_ENT_PAGE = re.compile(r"^/(?:de|fr|it|en)/(?:unternehmen|auftraggeber)/[^/]+/$")
_ENT_HEAD = re.compile(r'<h1\b[^>]*>(.*?)</h1>|<title>(.*?)</title>|<meta name="description" content="([^"]*)"', re.S)


def email_entity_errors(here: str, html: str) -> list:
    """E-mail addresses where a page names a company or an authority: a link to its page, a winner's card, a
    table's name cells (not a title, not a note), and on a company's or an authority's own page its H1, <title> and
    description. Publication texts may quote an address; a name may not."""
    parts = [g for m in _ENT_LINK.finditer(html) for g in m.groups() if g]
    parts += [_ENT_NOT.sub(" ", m.group(1)) for m in _ENT_TD.finditer(html)]
    if _ENT_PAGE.match(here):
        parts += [next((g for g in m.groups() if g), "") for m in _ENT_HEAD.finditer(html)]
    out = []
    for x in parts:
        hit = _EMAIL.search(htmlmod.unescape(_TAG.sub(" ", x)))
        if hit:
            out.append(hit.group(0))
    return out


def email_data_errors(shards: dict, offen: dict, csv_texts: dict) -> list:
    """E-mail addresses as names in the search index, the open tenders' authorities and the CSV name columns."""
    out = []
    for k, sh in shards.items():
        for kind, rows in sh.items():
            out += [f"suche/{k}.json {kind}: {r[0]}" for r in rows if _EMAIL.search(str(r[0]))]
    out += [f"offen.json: {b}" for b in offen.get("b", []) if _EMAIL.search(str(b))]
    for name, txt in csv_texts.items():
        for r in csv.reader(io.StringIO(txt, newline=""), delimiter=";"):
            if len(r) > 3 and (_EMAIL.search(r[2]) or _EMAIL.search(r[3])):
                out.append(f"{name}: {r[2] or r[3]}")
                break
    return out


def person_sitemap_errors(pages: dict, sitemap_urls: set) -> list:
    """No company page named after a natural person in the sitemap, and none indexable (pages: path -> (name,
    noindex))."""
    out = []
    for here, (name, noindex) in sorted(pages.items()):
        if person_name(name) and (here in sitemap_urls or not noindex):
            out.append(f"{here} ({name})")
    return out


class Design:
    """What every page's head and money columns must say (14.10.2026)."""

    def __init__(self, origin: str, base: str, units: dict):
        self.origin, self.base = origin, base
        # header text -> unit key, in the four languages ('Tsd. CHF' -> 'k')
        self.units = units
        self.errs = collections.defaultdict(list)
        self.columns = 0
        self.og = 0
        self.ld = 0

    def err(self, kind: str, here: str, detail: str = "") -> None:
        self.errs[kind].append((here, detail))

    def money_columns(self, here: str, html: str) -> None:
        seen: list = []
        n, errs = money_column_errors(html, self.units, seen)
        self.columns += n
        for kind, detail in errs + one_scale_errors(seen):
            self.err(kind, here, detail)

    def head(self, here: str, html: str, open_tender: bool) -> None:
        headpart = html.split("</head>", 1)[0]
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            self.ld += 1
            try:
                data = json.loads(m.group(1))
            except ValueError as ex:
                self.err("JSON-LD che non si legge", here, str(ex)[:80])
                continue
            graph = data.get("@graph", [data]) if isinstance(data, dict) else []
            for x in graph:
                if x.get("@type") == "Dataset" and (x.get("license") != SIMAP_TERMS or not x.get("@id")):
                    self.err("Dataset senza licenza (condizioni simap) o senza @id", here)
                if x.get("@type") == "Organization" and "address" in x:
                    self.err("Organization con indirizzo postale", here)
        parts = here.strip("/").split("/")
        if len(parts) == 1 and parts[0] in ("de", "fr", "it", "en"):
            if '"@type": "WebSite"' not in headpart or '"@type": "Organization"' not in headpart:
                self.err("home senza WebSite/Organization", here)
        if len(parts) == 2 and parts[1] == "ueber" and '"@type": "Dataset"' not in headpart:
            self.err("pagina Über senza Dataset", here)
        noindex = re.search(r'<meta name="robots" content="[^"]*noindex', headpart)
        og = dict(re.findall(r'<meta (?:property|name)="((?:og|twitter):[\w:]+)" content="([^"]*)"', headpart))
        if not noindex or open_tender:
            self.og += 1
            need = ("og:type", "og:title", "og:description", "og:url", "og:image", "og:locale", "twitter:card")
            miss = [k for k in need if not og.get(k)]
            if miss:
                self.err("Open Graph mancante", here, ", ".join(miss))
            else:
                canon = re.search(r'<link rel="canonical" href="([^"]+)"', headpart)
                if canon and og["og:url"] != canon.group(1):
                    self.err("og:url diverso dal canonical", here, og["og:url"])
                img = og["og:image"]
                if not img.startswith(self.origin + "/") or not (OUT / img[len(self.origin) + 1:]).is_file():
                    self.err("og:image inesistente", here, img)
        elif og:
            self.err("Open Graph su una pagina noindex (byte)", here)
        for href in re.findall(r'<link rel="alternate" type="application/(?:atom|rss)\+xml"[^>]*href="([^"]+)"', headpart):
            rest = href[len(self.origin):] if href.startswith(self.origin) else href
            if not rest.startswith("/") or not (OUT / rest.lstrip("/")).is_file():
                self.err("feed annunciato che non esiste", here, href)
        # nothing loaded from another host: scripts, stylesheets, fonts, icons, images, frames
        for _tag, url in re.findall(r'<(script|link|img|iframe|source|video|audio)\b[^>]*?\b(?:src|href)="(https?://[^"]+)"', html):
            if not url.startswith(self.origin + "/"):
                self.err("risorsa da un altro host", here, url[:80])

    def report(self) -> int:
        n = sum(len(v) for v in self.errs.values())
        print(f"  design (importi, JSON-LD, Open Graph, feed, host esterni)  {n} problemi"
              f" · {self.columns} colonne importi · {self.ld} blocchi JSON-LD · {self.og} pagine con Open Graph")
        for kind, v in sorted(self.errs.items(), key=lambda kv: -len(kv[1])):
            print(f"    {len(v):>6}  {kind}" + (f"  es. {v[0][0]} {v[0][1]}"[:200] if v else ""))
        return n


def _png_size(f: pathlib.Path):
    b = f.read_bytes()[:24]
    return (int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")) if b[:8] == b"\x89PNG\r\n\x1a\n" else None


def check_assets(css: str) -> list:
    """The icons and share cards, their sizes, and a stylesheet that loads nothing from elsewhere."""
    errs = []
    want = {"favicon.svg": None, "favicon.ico": None, "apple-touch-icon.png": (180, 180), "icon-512.png": (512, 512)}
    want.update({f"og-{l}.png": (1200, 630) for l in ("de", "fr", "it", "en")})
    for name, dim in want.items():
        f = OUT / name
        if not f.is_file():
            errs.append(f"{name} mancante")
            continue
        if dim and _png_size(f) != dim:
            errs.append(f"{name}: {_png_size(f)} invece di {dim}")
        if name.startswith("og-") and f.stat().st_size > 100_000:
            errs.append(f"{name}: {f.stat().st_size} byte, oltre 100 KB")
    for u in re.findall(r"url\(\s*['\"]?([^'\")]+)", css):
        if re.match(r"(?:https?:)?//", u):
            errs.append(f"style.css carica {u}")
        elif not u.startswith("data:") and not (OUT / u.split("?")[0].lstrip("/")[len(BASE.lstrip("/")):].lstrip("/")).is_file():
            errs.append(f"style.css: file mancante {u}")
    return errs


def main() -> int:
    def url_of(f: pathlib.Path) -> str:
        rel = f.relative_to(OUT).parent.as_posix()
        return "/" if rel == "." else f"/{rel}/"

    pages = {url_of(f) for f in OUT.rglob("index.html")}
    counts = collections.Counter()
    empty_titles, long_titles, no_desc = [], [], []
    broken = collections.Counter()
    same_tender, twin_rows = [], []
    # what the money figures and the award pages must say, from the data itself
    import sys as _sys
    _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import genera as G
    import lingue
    awards, *_ = G.load()
    expected = expected_sums(G, awards)
    projects = G.project_awards(awards)
    bad_sums, single_amount = [], []
    anchors_to: list = []                 # (page, target, fragment)
    anchors_at: dict = {}                 # award page -> the line ids it carries
    listed: list = []                     # (page, project id) of every row in a tender list
    closed: set = set()                   # project ids whose page says the deadline has passed
    st = Structure(SITE + BASE, BASE, G.CSV_COLS, getattr(G, "AGG_CSV", {}))
    # step 3a: what the totals, the company pages and the alert form must say, from the data
    home_t, about_t, cant_t, nocant_t, chart_t, cchart_t = {}, {}, collections.defaultdict(dict), {}, {}, \
        collections.defaultdict(dict)
    want_buyers = collections.defaultdict(set)
    for a in awards:
        if a.get("buyerName"):
            for w in G.winners(a):
                want_buyers[G.slug(w)].add(G.norm_buyer(a["buyerName"]))
    bad_buyers, bad_form, bad_ld = [], [], []
    units = {lingue.t(f"unit_{u}", l): u for u in ("k", "m", "chf") for l in ("de", "fr", "it", "en")}
    ds = Design(SITE + BASE, BASE, units)
    # step 3b: day-relative wording, the header's search, the open tenders as the pages show them
    rel_pat = relative_patterns(lingue)
    rel_bad, form_bad, open_ids = [], [], set()
    home_js_bad, first_head = [], ""
    # step 5: the retired words, page by page; meta descriptions over 155 characters; the new names (22.10.2026)
    term_bad, long_desc, req_bad = [], [], []
    # fix round 1: simap.ch in the page's language, the total's note, the company pages named after a person
    simap_bad, note_bad, person_pages, email_bad = [], [], {}, []
    joint_n = sum(1 for a in awards if len(G.winners(a)) > 1)
    # fix round 2: one gold button (the flat 'tag on' chip is gone), the A–Z component on the Bereich and canton
    # indexes, an official title over 110 characters a size smaller
    gold_bad, az_bad, lt_bad = [], [], []
    # fix round 3: H1 against its eyebrow, double full stops, French elision
    eb_bad, stop_bad, elide_bad = [], [], []

    for f in OUT.rglob("index.html"):
        html = f.read_text(encoding="utf-8")
        here = url_of(f)
        counts["pagine"] += 1
        st.page(here, html)
        ds.money_columns(here, html)
        ds.head(here, html, '<div class="fig wide" data-deadline="' in html)
        # step 3a: the totals, every buyer of a company, the 45 Branchen of the form
        hp = here.strip("/").split("/")
        if len(hp) == 1 and hp[0] in ("de", "fr", "it", "en"):
            home_t[hp[0]], chart_t[hp[0]] = total_of(html), chart_sum(html)
        elif len(hp) == 2 and hp[1] == "ueber":
            about_t[hp[0]] = total_of(html)
        elif len(hp) == 2 and hp[1] == "kanton":
            nocant_t[hp[0]] = nocant_of(html)
        elif len(hp) == 3 and hp[1] == "kanton":
            cant_t[hp[0]][hp[2]], cchart_t[hp[0]][hp[2]] = total_of(html), chart_sum(html)
        elif len(hp) == 3 and hp[1] == "unternehmen":
            x = company_buyer_errors(html, len(want_buyers.get(hp[2], ())))
            if x:
                bad_buyers.append((here, x))
        elif len(hp) == 3 and hp[1:] == ["ausschreibungen", "abo"]:
            bad_form += [(here, x) for x in form_branch_errors(html, lingue.CPV_SHORT["de"])]

        x = relative_errors(html, rel_pat)
        if x:
            rel_bad.append((here, x[0]))
        if hp and hp[0] in LANGS4:
            x = simap_lang_errors(hp[0], html)
            if x:
                simap_bad.append((here, x[0]))
        x = email_entity_errors(here, html)
        if x:
            email_bad.append((here, x[0]))
        if len(hp) == 1 and hp[0] in LANGS4:
            note_bad += [(here, x) for x in sum_note_errors(html, joint_n)]
        if len(hp) == 3 and hp[1] == "unternehmen":
            h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.S)
            person_pages[here] = (htmlmod.unescape(_TAG.sub("", h1.group(1))) if h1 else "",
                                  bool(re.search(r'<meta name="robots" content="[^"]*noindex', html)))
        x = term_errors(here, html)
        if x:
            term_bad.append((here, x))
        x = required_errors(here, html)
        if x:
            req_bad.append((here, x))
        if 'class="tag on"' in html:
            gold_bad.append(here)
        eb_bad += [(here, x) for x in eyebrow_errors(html)]
        stop_bad += [(here, x) for x in double_stop_errors(html)]
        if hp and hp[0] == "fr":
            elide_bad += [(here, x) for x in elision_page_errors(html)]
        if len(hp) == 2 and hp[1] in ("bereich", "kanton") and '<ul class="az' not in html:
            az_bad.append(here)
        h1r = _REC_H1.search(html)
        if h1r and len(htmlmod.unescape(_TAG.sub("", h1r.group(2)))) > G.LONG_TITLE and " lt" not in h1r.group(1):
            lt_bad.append(here)
        # step 4: the home's script on the five home pages, and on no other
        has_home = f'src="{BASE}/js/home.js' in html
        if has_home != (here in HOMES):
            home_js_bad.append((here, "home.js su una pagina che non è la home" if has_home else "home senza home.js"))
        if not first_head:
            first_head = html.split("</head>", 1)[0]
        fm = _SEARCH_FORM.search(html)
        lang_here = hp[0] if hp and hp[0] in LANGS4 else "de"
        if not fm:
            form_bad.append((here, "manca la ricerca nell'intestazione"))
        elif fm.group(1) != f"{BASE}/{lang_here}/suche/":
            form_bad.append((here, fm.group(1)))
        if (len(hp) == 3 and hp[0] == "de" and hp[1] == "auftrag" and '<div class="fig wide" data-deadline="' in html
                and '<span class="state off">' not in html):
            open_ids.add(hp[2])

        t = re.search(r"<title>(.*?)</title>", html, re.S)
        # measure what a reader sees: an apostrophe is one character, not the six
        # of its &#x27; entity, and the entity form made 149 correct titles look long
        title = htmlmod.unescape(t.group(1).strip()) if t else ""
        if not title:
            empty_titles.append(here)
        elif len(title) > 65:
            long_titles.append((here, len(title)))
        d = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
        if not d or not d.group(1).strip():
            no_desc.append(here)
        elif len(htmlmod.unescape(d.group(1).strip())) > 155:
            long_desc.append((here, len(htmlmod.unescape(d.group(1).strip()))))

        # A tender list names each tender once: simap republishes a tender for every
        # correction, and each copy was listed as a tender of its own (the same line two or
        # three times, a superseded deadline beside the current one; 28.09.2026).
        for m in _TENDER_LISTS.finditer(html):
            ids = [re.search(r'href="[^"]*/auftrag/([^/"]+)/"', r) for r in _ROWS.findall(m.group(0))]
            seen = collections.Counter(x.group(1) for x in ids if x)
            dup = [k for k, n in seen.items() if n > 1]
            if dup:
                same_tender.append((here, dup[0]))
            listed.extend((here, k) for k in seen)
        # a tender past its deadline keeps its page, marked so (08.10.2026), and is listed nowhere
        # as open: read from the pages themselves, so a deadline passing between the build and
        # this check is not an error
        if '<span class="state off">' in html and "/auftrag/" in here:
            closed.add(here.rstrip("/").rsplit("/", 1)[-1])
        # No list shows two rows a reader cannot tell apart.
        for lst in _LISTS.findall(html):
            rows = [_text(r) for r in _ROWS.findall(lst)]
            n = collections.Counter(r for r in rows if r)
            twin = [r for r, k in n.items() if k > 1]
            if twin:
                twin_rows.append((here, twin[0][:90]))

        for href in re.findall(r'href="(/[^"#?]*)"', html):
            if BASE and href.startswith(BASE + "/"):
                href = href[len(BASE):]
            elif BASE and href == BASE:
                href = "/"
            if href.startswith(("/style.css", "/sitemap.xml", "/robots.txt", "/fonts/")):
                continue
            if re.search(r"\.(?:ics|csv|xml|js|svg)$", href):    # a file, not a page (14.10.2026)
                if not (OUT / href.lstrip("/")).is_file():
                    broken[href] += 1
                    counts["link rotti"] += 1
                continue
            target = href if href.endswith("/") else href + "/"
            if target not in pages:
                broken[target] += 1
                counts["link rotti"] += 1
        # a row that links to its own lot on a project's page (#lot-2): the line must be there
        for href, frag in re.findall(r'href="(/[^"#?]*)#((?:lot|pub)-[^"]*)"', html):
            if BASE and href.startswith(BASE + "/"):
                href = href[len(BASE):]
            target = href if href.endswith("/") else href + "/"
            anchors_to.append((here, target, frag))
            if target not in pages:          # the pattern above skips links with a fragment
                broken[target] += 1
                counts["link rotti"] += 1

        # The money figures. The invariant that matters on a transparency register: a page's
        # headline sum must equal the sum of the rows it shows, and a figure that states more
        # than the source published is worse than no figure. Since 08.10.2026 a CHF total counts
        # awards to ONE firm only: an award to several firms has a price per firm and no amount
        # of its own, so a total that counts one states a figure nobody published.
        tile = re.search(r'<div class="fig money"><b><data value="([0-9.]+)"', html)
        key = here.lstrip("/") or "de/"          # the root carries the German home
        if key in expected:
            want = expected[key]
            got = float(tile.group(1)) if tile else 0.0
            if not sum_ok(got, want):
                bad_sums.append((here, got, want))
        # An award page never shows a single amount for an award naming several firms: not as
        # its 'Zuschlagsbetrag' tile, and not on the award's line in a project's list of lots.
        parts = here.strip("/").split("/")
        if len(parts) == 3 and parts[1] == "auftrag" and parts[2] in projects:
            rows = projects[parts[2]]
            label = re.escape(htmlmod.escape(lingue.t("award_amount", parts[0]), quote=True))
            has_tile = re.search(r'<div class="fig[^"]*"><b>.*?</b><span>' + label + "</span>", html)
            if has_tile and (len(rows) > 1 or len(G.winners(rows[0])) > 1):
                single_amount.append((here, "Zuschlagsbetrag"))
            lines = dict(re.findall(r'<tr id="((?:lot|pub)-[^"]*)">(.*?)</tr>', html, re.S))
            anchors_at[here] = set(lines)
            for a in rows:
                if len(rows) == 1:
                    break
                line = lines.get(a.get("_anchor") or "")
                if line is None:
                    single_amount.append((here, f"riga mancante {a.get('publicationNumber')}"))
                elif len(G.winners(a)) > 1 and "<data" in line.rsplit('<td class="r num">', 1)[-1]:
                    single_amount.append((here, f"importo unico {a.get('publicationNumber')}"))

    # the national total everywhere (home, about, cantons + no canton, CSV, monthly chart)
    csv_rows, nocant_csv = {}, 0
    for f in sorted((OUT / "daten" / "kanton").glob("*.csv")):
        n = sum(1 for _r in csv.reader(io.StringIO(f.read_bytes()[3:].decode("utf-8"), newline=""), delimiter=";")) - 1
        if f.stem == "ohne-kanton":
            nocant_csv = n
        else:
            csv_rows[f.stem] = n
    tot_errs = reconcile_totals(home_t, about_t, cant_t, nocant_t, csv_rows, nocant_csv, chart_t, cchart_t)
    nat = next(iter(home_t.values()), None)
    print(f"  totale che non quadra   {len(tot_errs)} (totale {nat}, cantoni {sum(v or 0 for v in cant_t.get('de', {}).values())}"
          f" + senza cantone {nocant_t.get('de', 0)}, CSV {sum(csv_rows.values())} + {nocant_csv})")
    for m in tot_errs[:6]:
        print(f"    {m}")
    print(f"  imprese senza tutti i committenti {len(bad_buyers)} pagine")
    for h, x in bad_buyers[:4]:
        print(f"    {h}  {x}")
    print(f"  modulo avvisi: branche  {len(bad_form)} problemi")
    for h, x in bad_form[:4]:
        print(f"    {h}  {x}")
    # every Atom feed valid (RFC 4287), every JSON-LD block of the 404 page too
    bad_feeds = []
    feeds = sorted(OUT.rglob("feed.xml"))
    for f in feeds:
        for x in atom_errors(f.read_text(encoding="utf-8")):
            bad_feeds.append((f.relative_to(OUT).as_posix(), x))
    print(f"  feed Atom non validi    {len(bad_feeds)} su {len(feeds)}")
    for h, x in bad_feeds[:4]:
        print(f"    {h}  {x}")
    if (OUT / "404.html").exists():
        bad_ld += [("404.html", x) for x in jsonld_errors((OUT / "404.html").read_text(encoding="utf-8"))]
    print(f"  somme che non quadrano  {len(bad_sums)} pagine (home, cantoni, committenti, imprese)")
    for h, got, want in bad_sums[:4]:
        print(f"    {h}  pagina {got:,.2f} · righe con una sola impresa {want:,.2f}")
    print(f"  un importo per più ditte {len(single_amount)} pagine appalto")
    for h, what in single_amount[:4]:
        print(f"    {h}  {what}")
    lost = [(h, t, fr) for h, t, fr in anchors_to if t in anchors_at and fr not in anchors_at[t]]
    print(f"  ancore di lotto rotte   {len(lost)} su {len(anchors_to)}")
    for h, t, fr in lost[:4]:
        print(f"    {h} -> {t}#{fr}")

    # step 3b: the scripts' data, the search index, the byte limits, the day-relative wording
    import gzip
    data_files = {"/" + f.relative_to(OUT).as_posix(): f.read_bytes()
                  for f in [OUT / "daten" / "offen.json", OUT / "daten" / "offen-n.json", OUT / "daten" / "abo-rate.json",
                            OUT / "daten" / "offen-dl.json",
                            *sorted((OUT / "daten" / "suche").glob("*.json")), *sorted((OUT / "daten" / "kb").glob("*.json")),
                            *sorted((OUT / "daten" / "ab").glob("*.json")), *sorted((OUT / "daten" / "kf").glob("*.json"))]
                  if f.is_file()}
    j_errs = json_errors(data_files)
    for need in ("/daten/offen.json", "/daten/offen-n.json", "/daten/abo-rate.json", "/daten/suche/themen.json",
                 "/daten/offen-dl.json"):
        if need not in data_files:
            j_errs.append(f"{need} mancante")
    js_gz = sum(len(gzip.compress(f.read_bytes(), 9)) for f in [OUT / "stand.js", *sorted((OUT / "js").glob("*.js"))]
                if f.is_file() and f.name != "home.js")
    sz_errs = size_errors({k: len(v) for k, v in data_files.items()}, js_gz)
    # the home's motion and map (step 4): a file of its own, on the home pages only, at most HOME_JS_MAX_GZ
    home_gz = len(gzip.compress((OUT / "js" / "home.js").read_bytes(), 9)) if (OUT / "js" / "home.js").is_file() else 0
    if not home_gz:
        sz_errs.append("/js/home.js mancante")
    elif home_gz > HOME_JS_MAX_GZ:
        sz_errs.append(f"/js/home.js {home_gz} byte gzip, oltre {HOME_JS_MAX_GZ}")
    sz_errs += [f"{h}: {x}" for h, x in home_js_bad[:6]]
    idx_errs, open_errs = [], []
    if not j_errs:
        comp = G.profile(awards)
        companies = {c["name"]: (sl, len(c["awards"]), len(c["awards"]) >= G.MIN_AWARDS) for sl, c in comp.items()}
        bmap = G.buyer_map(awards)
        bk = collections.defaultdict(collections.Counter)
        for a in awards:
            if a.get("buyerName"):
                bk[G.norm_buyer(a["buyerName"])][" ".join(a["buyerName"].split())] += 1
        buyers = {(bmap[k][1] if k in bmap else c.most_common(1)[0][0]): (bmap[k][0] if k in bmap else "", sum(c.values()), k in bmap)
                  for k, c in bk.items()}
        shards = {k[len("/daten/suche/"):-5]: json.loads(v) for k, v in data_files.items()
                  if k.startswith("/daten/suche/") and not k.endswith("/themen.json")}
        idx_errs = search_index_errors(shards, companies, buyers, pages)
        open_errs = open_index_errors(json.loads(data_files["/daten/offen.json"]), open_ids)
        open_errs += open_count_errors(json.loads(data_files["/daten/offen.json"]), json.loads(data_files["/daten/offen-n.json"]))
    sp_errs = search_page_errors(pages)
    n_entries = sum(len(v) for sh in (json.loads(x) for k, x in data_files.items() if k.startswith("/daten/suche/")
                                      and not k.endswith("themen.json")) for v in sh.values())
    print(f"  dati degli script       {len(j_errs)} illeggibili su {len(data_files)} file · "
          f"{sum(len(v) for v in data_files.values()) / 1e6:.2f} MB · script {js_gz / 1e3:.1f} KB gzip"
          f" · home.js {home_gz / 1e3:.1f} KB gzip ({len(home_js_bad)} pagine fuori posto)")
    for m in (j_errs + sz_errs)[:6]:
        print(f"    {m}")
    print(f"  indice di ricerca       {len(idx_errs)} problemi ({n_entries} voci negli shard) · "
          f"bandi aperti {len(open_errs)} problemi ({len(open_ids)} pagine aperte)")
    for m in (idx_errs + open_errs)[:6]:
        print(f"    {m}")
    print(f"  ricerca senza JS        {len(sp_errs) + len(form_bad)} problemi (/xx/suche/ e il modulo in ogni intestazione)")
    for m in (sp_errs + [f"{h} {x}" for h, x in form_bad])[:4]:
        print(f"    {m}")
    sm_urls = set()
    for sm in OUT.glob("sitemap-*.xml"):
        sm_urls |= {u[len(SITE + BASE):] for u in re.findall(r"<loc>([^<]+)</loc>", sm.read_text(errors="replace"))}
    person_bad = person_sitemap_errors(person_pages, sm_urls)
    css0 = (OUT / "style.css").read_text(encoding="utf-8") if (OUT / "style.css").is_file() else ""
    hid_errs = hidden_rule_errors(css0)
    csv_texts = {f.relative_to(OUT).as_posix(): f.read_bytes()[3:].decode("utf-8")
                 for f in (OUT / "daten").glob("*/*.csv")}
    shards0 = {k[len("/daten/suche/"):-5]: json.loads(v) for k, v in data_files.items()
               if k.startswith("/daten/suche/") and not k.endswith("/themen.json")} if not j_errs else {}
    email_bad += [("daten", x) for x in email_data_errors(
        shards0, json.loads(data_files["/daten/offen.json"]) if "/daten/offen.json" in data_files and not j_errs else {},
        csv_texts)]
    print(f"  giro 1: [hidden] {'ok' if not hid_errs else hid_errs[0]} · simap in un'altra lingua {len(simap_bad)} pagine"
          f" · nota della somma {len(note_bad)} problemi ({joint_n} zuschläge a piu' imprese)"
          f" · persone fisiche indicizzabili o in sitemap {len(person_bad)}"
          f" (su {sum(1 for n, _x in person_pages.values() if person_name(n))} pagine di persone)"
          f" · indirizzi e-mail come nome {len(email_bad)}")
    for m in ([f"{h} {x}" for h, x in simap_bad[:3]] + [f"{h} {x}" for h, x in note_bad[:3]] + person_bad[:3]
              + [f"{h} {x}" for h, x in email_bad[:3]]):
        print(f"    {m}")
    print(f"  giro 2: bottoni d'oro piatti {len(gold_bad)} pagine · indici senza A–Z {len(az_bad)}"
          f" · titoli lunghi senza la misura minore {len(lt_bad)}")
    for m in (gold_bad[:3] + az_bad[:3] + lt_bad[:3]):
        print(f"    {m}")
    elide_bad = [("lingue", x) for x in elision_template_errors(lingue)] + elide_bad
    print(f"  giro 3: H1 che ripete l'occhiello {len(eb_bad)} pagine · doppio punto {len(stop_bad)}"
          f" · elisione francese {len(elide_bad)}")
    for h, x in (eb_bad[:3] + stop_bad[:3] + elide_bad[:3]):
        print(f"    {h}  {x}")
    print(f"  parole relative al giorno {len(rel_bad)} pagine")
    for h, x in rel_bad[:4]:
        print(f"    {h}  «{x}»")
    if (OUT / "404.html").exists():
        x = term_errors("/404.html", (OUT / "404.html").read_text(encoding="utf-8"))
        if x:
            term_bad.append(("/404.html", x))
        x = required_errors("/404.html", (OUT / "404.html").read_text(encoding="utf-8"))
        if x:
            req_bad.append(("/404.html", x))
    if (OUT / "stand.js").is_file():
        req_bad += [("/stand.js", [("modello della riga della data", x)])
                    for x in stand_template_errors((OUT / "stand.js").read_text(encoding="utf-8"))]
    # which word, how often (each hit's context names it)
    n_terms = collections.Counter(t for _h, xs in term_bad for l, c in xs for t in BANNED_TERMS[l]
                                  if re.search(_term_pat(t), c, re.I))
    print(f"  parole ritirate (una per concetto) {len(term_bad)} pagine"
          + (f" · {', '.join(f'«{t}» {k}' for t, k in n_terms.most_common())}" if n_terms else ""))
    for h, xs in term_bad[:6]:
        print(f"    {h}  [{xs[0][0]}] …{xs[0][1]}…")
    print(f"  nomi nuovi mancanti (menu, servizio e-mail, inviti, data) {len(req_bad)} pagine")
    for h, xs in req_bad[:6]:
        print(f"    {h}  {xs[0][0]}: «{xs[0][1]}»")
    print(f"  pagine controllate      {counts['pagine']}")
    print(f"  titoli vuoti            {len(empty_titles)}")
    print(f"  titoli oltre 65 char    {len(long_titles)}")
    print(f"  senza description       {len(no_desc)}")
    print(f"  description oltre 155   {len(long_desc)}")
    for h, n in long_desc[:4]:
        print(f"    {n} char  {h}")
    print(f"  link interni rotti      {counts['link rotti']} verso {len(broken)} destinazioni")
    print(f"  bandi ripetuti in lista {len(same_tender)} pagine")
    for h, k in same_tender[:4]:
        print(f"    {h}  /auftrag/{k}/")
    stale = [(h, k) for h, k in listed if k in closed]
    print(f"  scaduti fra gli aperti  {len(stale)} righe ({len(closed)} pagine di bandi scaduti)")
    for h, k in stale[:4]:
        print(f"    {h}  /auftrag/{k}/")
    # docs/404.html, served by GitHub Pages for every missing URL: it must exist, and its links —
    # root-relative, since it is served at any depth — must lead to pages (08.10.2026)
    nf, nf_bad = OUT / "404.html", []
    if not nf.exists():
        nf_bad.append("docs/404.html manca")
    else:
        for href in re.findall(r'href="(/[^"#?]*)"', nf.read_text(encoding="utf-8")):
            if BASE and href.startswith(BASE + "/"):
                href = href[len(BASE):]
            if href.startswith(("/style.css", "/fonts/")):
                continue
            if re.search(r"\.(?:ics|csv|xml|js|svg)$", href):
                if not (OUT / href.lstrip("/")).is_file():
                    nf_bad.append(href)
                continue
            if (href if href.endswith("/") else href + "/") not in pages:
                nf_bad.append(href)
    if nf.exists():
        nft = nf.read_text(encoding="utf-8")
        for needle in ('<nav class="sitenav', 'class="skip" href="#inhalt"', '<main id="inhalt">', "<header"):
            if needle not in nft:
                nf_bad.append(f"manca {needle}")
    print(f"  pagina 404              {'ok' if not nf_bad else 'link rotti: ' + ', '.join(nf_bad[:4])}")
    st.check_files()
    n_struct = st.report()
    n_design = ds.report()
    css = (OUT / "style.css").read_text(encoding="utf-8") if (OUT / "style.css").is_file() else ""
    c_errs, c_rows = check_contrast(css, G.CONTRAST)
    print(f"  contrasto dei token      {len(c_errs)} coppie sotto WCAG AA su {len(c_rows)} (un tema, scuro)")
    for m in c_errs[:8]:
        print(f"    {m}")
    f_errs = check_font_sizes(css) + [f"home: {x}" for x in check_font_sizes(G.css_min(G.HOME_CSS))]
    print(f"  corpi non in rem o sotto 13 px  {len(f_errs)} dichiarazioni (foglio e home)")
    for m in f_errs[:8]:
        print(f"    {m}")
    fo_errs = check_fonts(css, first_head)
    fo_tot = sum(f.stat().st_size for f in (OUT / "fonts").glob("*.woff2")) if (OUT / "fonts").is_dir() else 0
    print(f"  font                    {len(fo_errs)} problemi · {fo_tot / 1e3:.1f} KB woff2 (max {FONTS_MAX / 1e3:.0f})")
    for m in fo_errs[:6]:
        print(f"    {m}")
    a_errs = check_assets(css)
    print(f"  icone e immagini        {'ok' if not a_errs else '; '.join(a_errs[:4])}")
    print(f"  righe identiche         {len(twin_rows)} pagine")
    for h, k in twin_rows[:4]:
        print(f"    {h}  «{k}»")
    abs_errs = check_absolute(pages, SITE, BASE)
    print(f"  URL assoluti sbagliati  {len(abs_errs)}")
    if abs_errs:
        print("\n  URL che il sito dichiara su se stesso e che non risolvono:")
        for m in abs_errs[:6]:
            print(f"    {m}")
    if broken:
        print("\n  destinazioni mancanti più citate:")
        for tgt, k in broken.most_common(8):
            print(f"    {k:>4}×  {tgt}")
    if long_titles:
        print("\n  titoli troppo lunghi (Google li tronca):")
        for h, n in long_titles[:5]:
            print(f"    {n} char  {h}")
    return 1 if (broken or empty_titles or no_desc or abs_errs or same_tender or twin_rows
                 or bad_sums or single_amount or lost or stale or nf_bad or n_struct
                 or n_design or c_errs or f_errs or fo_errs or a_errs or tot_errs or bad_buyers or bad_form
                 or bad_feeds or bad_ld or j_errs or sz_errs or idx_errs or open_errs or sp_errs or form_bad
                 or rel_bad or term_bad or req_bad or long_desc or hid_errs or simap_bad or note_bad or person_bad
                 or email_bad or gold_bad or az_bad or lt_bad or eb_bad or stop_bad or elide_bad) else 0


if __name__ == "__main__":
    sys.exit(main())
