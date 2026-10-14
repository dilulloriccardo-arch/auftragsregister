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
                    and (a.get("winnerCurrency") or "CHF").strip().upper() == "CHF"):
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
_CANTONS = {"AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU", "LU", "NE", "NW", "OW", "SG",
            "SH", "SO", "SZ", "TG", "TI", "UR", "VD", "VS", "ZG", "ZH"}


class Structure:
    def __init__(self, origin: str, base: str, csv_cols: tuple):
        self.origin, self.base, self.csv_cols = origin, base, csv_cols
        self.errs = collections.defaultdict(list)          # kind -> [(page, detail)]
        self.files = {}                                     # docs path -> (page, link attributes)
        self.noindex = set()
        self.ics_pages = 0
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
        for kind, needle in (("menu", '<nav class="sitenav"'), ("salta al contenuto", 'class="skip" href="#inhalt"'),
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
        if not ld:
            # a noindex page carries no BreadcrumbList (14.10.2026): its visible trail must be there,
            # every level but the last a link, the last the page itself
            if not noindex:
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
        # tables: a caption each, and every header cell with its scope
        if html.count("<table") != html.count("<caption"):
            self.err("tabelle senza didascalia", here)
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
                if head != tuple(self.csv_cols):
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
    st = Structure(SITE + BASE, BASE, G.CSV_COLS)

    for f in OUT.rglob("index.html"):
        html = f.read_text(encoding="utf-8")
        here = url_of(f)
        counts["pagine"] += 1
        st.page(here, html)

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
            if abs(got - round(want, 2)) > 0.05:
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

    print(f"  pagine controllate      {counts['pagine']}")
    print(f"  titoli vuoti            {len(empty_titles)}")
    print(f"  titoli oltre 65 char    {len(long_titles)}")
    print(f"  senza description       {len(no_desc)}")
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
                 or bad_sums or single_amount or lost or stale or nf_bad or n_struct) else 0


if __name__ == "__main__":
    sys.exit(main())
