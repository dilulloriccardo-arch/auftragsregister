#!/usr/bin/env python3
"""Check the built site before it is published.

A broken internal link costs twice: the reader hits nothing, and the crawler spends
its budget on a 404 instead of a page. These are the checks that catch what the
generator cannot see about itself.
"""
from __future__ import annotations

import collections
import html as htmlmod
import pathlib
import re
import sys

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


def main() -> int:
    def url_of(f: pathlib.Path) -> str:
        rel = f.relative_to(OUT).parent.as_posix()
        return "/" if rel == "." else f"/{rel}/"

    pages = {url_of(f) for f in OUT.rglob("index.html")}
    problems: list[str] = []
    counts = collections.Counter()
    empty_titles, long_titles, no_desc = [], [], []
    broken = collections.Counter()

    for f in OUT.rglob("index.html"):
        html = f.read_text(encoding="utf-8")
        here = url_of(f)
        counts["pagine"] += 1

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

        for href in re.findall(r'href="(/[^"#?]*)"', html):
            if BASE and href.startswith(BASE + "/"):
                href = href[len(BASE):]
            elif BASE and href == BASE:
                href = "/"
            if href.startswith(("/style.css", "/sitemap.xml", "/robots.txt", "/fonts/")):
                continue
            target = href if href.endswith("/") else href + "/"
            if target not in pages:
                broken[target] += 1
                counts["link rotti"] += 1

    # The invariant that matters on a transparency register: a page's headline sum
    # must equal the sum of the rows it shows. A figure that states more than the
    # source published is worse than no figure.
    import sys as _sys
    _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import genera as G
    awards, _ = G.load()
    by_buyer = collections.defaultdict(list)
    for a in awards:
        if a.get("buyerName"):
            by_buyer[a["buyerName"]].append(a)
    mismatch = 0
    for name, rows in by_buyer.items():
        if len(rows) < 3:
            continue
        head = sum(a.get("winnerPrice") or 0 for a in rows
                   if isinstance(a.get("winnerPrice"), (int, float)))
        per, joint = 0.0, 0.0
        for r in rows:
            ws, pr = G.winners(r), r.get("winnerPrice")
            if isinstance(pr, (int, float)) and pr:
                if len(ws) == 1:
                    per += pr
                else:
                    joint += pr
        if abs(head - per - joint) > 1:
            mismatch += 1
    print(f"  somme che non quadrano  {mismatch} pagine committente")
    if mismatch:
        problems.append("somme incoerenti")

    print(f"  pagine controllate      {counts['pagine']}")
    print(f"  titoli vuoti            {len(empty_titles)}")
    print(f"  titoli oltre 65 char    {len(long_titles)}")
    print(f"  senza description       {len(no_desc)}")
    print(f"  link interni rotti      {counts['link rotti']} verso {len(broken)} destinazioni")
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
    return 1 if (broken or empty_titles or no_desc or abs_errs) else 0


if __name__ == "__main__":
    sys.exit(main())
