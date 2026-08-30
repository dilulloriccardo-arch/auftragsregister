#!/usr/bin/env python3
"""Nightly refresh: pull what changed, rebuild the register, report in one line.

Only the current and previous month of awards are re-fetched — a publication can be
corrected after the fact, and those two months are where corrections land — plus the
open tenders, which turn over constantly. Everything older is already on disk and is
never re-fetched: it is the archive, and it is the part no one else can rebuild,
because simap's API answers a wide date window with only its most recent weeks.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
DATI = ROOT / "dati"
TOKEN = (pathlib.Path.home() / ".apify_publish_token").read_text().strip()
SIMAP = "nm2hQBphfU8wWlFa2"
LOG = ROOT / "aggiorna.log"


def say(msg: str) -> None:
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def api(method: str, path: str, body=None):
    url = f"https://api.apify.com/v2{path}{'&' if '?' in path else '?'}token={TOKEN}"
    req = urllib.request.Request(
        url, data=json.dumps(body).encode() if body is not None else None,
        method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode()).get("data", {})


def run(kinds, frm, to, dest: pathlib.Path) -> int:
    r = api("POST", f"/acts/{SIMAP}/runs?memory=2048&timeout=7200",
            {"publicationTypes": kinds, "publishedFrom": frm, "publishedUntil": to,
             "onlySwitzerland": True, "includeDetails": True, "stripHtml": True,
             "language": "de", "maxItems": 0})
    rid = r["id"]
    for _ in range(720):
        time.sleep(15)
        r = api("GET", f"/actor-runs/{rid}")
        if r["status"] not in ("RUNNING", "READY"):
            break
    if r["status"] != "SUCCEEDED":
        say(f"  ATTENZIONE run {rid} finito {r['status']} — {dest.name} non aggiornato")
        return -1
    items = json.loads(urllib.request.urlopen(
        f"https://api.apify.com/v2/datasets/{r['defaultDatasetId']}/items"
        f"?token={TOKEN}&clean=true&limit=50000", timeout=300).read())
    # MERGE, never replace. simap matches a date window against each project's NEWEST
    # publication, so an award from July that gets a correction in August stops
    # matching July — refetching a month and overwriting it silently drops those rows.
    # It cost 220 rows on 2026-08-30 before this was fixed. An archive only grows.
    old = json.loads(dest.read_text()) if dest.exists() else []
    by_id = {(r.get("publicationId") or r.get("publicationNumber")): r for r in old}
    added = updated = 0
    for r in items:
        k = r.get("publicationId") or r.get("publicationNumber")
        if not k:
            continue
        if k not in by_id:
            added += 1
        elif by_id[k] != r:
            updated += 1
        by_id[k] = r
    merged = list(by_id.values())
    if len(merged) < len(old):
        say(f"  {dest.name}: la fusione ridurrebbe da {len(old)} a {len(merged)} — non scrivo")
        return len(old)
    dest.write_text(json.dumps(merged, ensure_ascii=False))
    if added or updated:
        say(f"  {dest.name}: +{added} nuove, {updated} aggiornate, {len(merged)} totali")
    return len(merged)


def main() -> int:
    today = datetime.date.today()
    first = today.replace(day=1)
    prev_end = first
    prev = (first - datetime.timedelta(days=1)).replace(day=1)
    nxt = (first + datetime.timedelta(days=32)).replace(day=1)

    n_now = run(["award_tender", "direct_award"], first.isoformat(), nxt.isoformat(),
                DATI / f"aggiudicazioni_{first:%Y-%m}.json")
    n_prev = run(["award_tender", "direct_award"], prev.isoformat(), prev_end.isoformat(),
                 DATI / f"aggiudicazioni_{prev:%Y-%m}.json")
    since = (today - datetime.timedelta(days=75)).isoformat()
    n_open = run(["tender"], since, nxt.isoformat(), DATI / "gare_aperte.json")

    out = subprocess.run([sys.executable, str(ROOT / "genera.py")],
                         capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        say(f"  ERRORE nella generazione:\n{out.stderr[-800:]}")
        return 1
    check = subprocess.run([sys.executable, str(ROOT / "controlla.py")],
                           capture_output=True, text=True, cwd=ROOT)
    if check.returncode != 0:
        say("  controlli falliti — sito rigenerato ma NON pubblicato")
        say("  " + check.stdout.strip().replace("\n", "\n  ")[-600:])
        return 1

    pages = sum(1 for _ in (ROOT / "docs").rglob("index.html"))
    # Publishing is a plain commit: unchanged pages cost nothing in git, so a daily
    # push of 76k files only carries the ones the day actually changed.
    subprocess.run(["git", "add", "-A"], cwd=ROOT, capture_output=True)
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                        capture_output=True, text=True).stdout.strip()
    if not st:
        say(f"nessun cambiamento — {pages} pagine invariate")
        return 0
    changed = len(st.splitlines())
    subprocess.run(["git", "-c", "user.email=dilulloriccardo@gmail.com",
                    "-c", "user.name=Riccardo Di Lullo", "commit", "-q",
                    "-m", f"Aggiornamento {datetime.date.today():%Y-%m-%d}: "
                          f"{changed} pagine cambiate"], cwd=ROOT, capture_output=True)
    push = subprocess.run(["git", "push", "-q"], cwd=ROOT, capture_output=True, text=True)
    if push.returncode != 0:
        say(f"  ATTENZIONE push fallito: {push.stderr.strip()[:300]}")
        return 1
    say(f"pubblicato: {changed} pagine cambiate su {pages}")
    say(f"dati: {n_now} questo mese, {n_prev} il mese scorso, {n_open} bandi aperti")
    return 0


if __name__ == "__main__":
    sys.exit(main())
