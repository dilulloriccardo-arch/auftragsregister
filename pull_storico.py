#!/usr/bin/env python3
"""Fetch the award history month by month, four months at a time.

Two constraints shape this:

  * simap answers a WIDE date window with only its most recent weeks — a twelve-month
    query came back with 906 rows that all fell in the last two months, which reads
    exactly like a year of data and is not. So one request per month, always.
  * that makes the run long, and the runs are independent, so they go in parallel.
    The account allows five concurrent jobs at 16 GB; four at 2 GB leaves headroom
    for the nightly refresh if it fires mid-run.

Already-downloaded months are skipped, so the script resumes after any interruption.
"""
from __future__ import annotations

import json
import pathlib
import time
import urllib.error
import urllib.request

TOKEN = (pathlib.Path.home() / ".apify_publish_token").read_text().strip()
SIMAP = "nm2hQBphfU8wWlFa2"
OUT = pathlib.Path(__file__).resolve().parent / "dati"
# One at a time. Four concurrent runs each took 483 minutes instead of ten: the
# account's compute is shared across them, so parallelism bought nothing and cost a
# whole night. Measured 2026-08-29.
LANES = 1


def api(method: str, path: str, body=None):
    url = f"https://api.apify.com/v2{path}{'&' if '?' in path else '?'}token={TOKEN}"
    req = urllib.request.Request(
        url, data=json.dumps(body).encode() if body is not None else None,
        method=method, headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode()).get("data", {})
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
            print(f"    (riprovo dopo {type(exc).__name__})", flush=True)


def months(first: str, last: str):
    y, m = int(first[:4]), int(first[5:7])
    ly, lm = int(last[:4]), int(last[5:7])
    out = []
    while (y, m) <= (ly, lm):
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        out.append((f"{y:04d}-{m:02d}-01", f"{ny:04d}-{nm:02d}-01", f"{y:04d}-{m:02d}"))
        y, m = ny, nm
    return out


def start(frm: str, to: str) -> str:
    return api("POST", f"/acts/{SIMAP}/runs?memory=2048&timeout=7200",
               {"publicationTypes": ["award_tender", "direct_award"],
                "publishedFrom": frm, "publishedUntil": to, "onlySwitzerland": True,
                "includeDetails": True, "stripHtml": True, "language": "de",
                "maxItems": 0})["id"]


def collect(rid: str, dest: pathlib.Path) -> int:
    r = api("GET", f"/actor-runs/{rid}")
    if r["status"] != "SUCCEEDED":
        print(f"  {dest.stem}: {r['status']} — non scritto", flush=True)
        return -1
    items = json.loads(urllib.request.urlopen(
        f"https://api.apify.com/v2/datasets/{r['defaultDatasetId']}/items"
        f"?token={TOKEN}&clean=true&limit=50000", timeout=300).read())
    dest.write_text(json.dumps(items, ensure_ascii=False))
    return len(items)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    todo = [(f, t, n) for f, t, n in reversed(months("2023-09", "2026-08"))
            if not (OUT / f"aggiudicazioni_{n}.json").exists()]
    print(f"  {len(todo)} mesi da scaricare, {LANES} in parallelo", flush=True)
    running: dict[str, tuple[str, pathlib.Path]] = {}
    done = 0
    while todo or running:
        while todo and len(running) < LANES:
            frm, to, name = todo.pop(0)
            running[start(frm, to)] = (name, OUT / f"aggiudicazioni_{name}.json")
            print(f"  avvio {name}", flush=True)
        time.sleep(20)
        for rid in list(running):
            st = api("GET", f"/actor-runs/{rid}")["status"]
            if st in ("RUNNING", "READY"):
                continue
            name, dest = running.pop(rid)
            n = collect(rid, dest)
            done += 1
            print(f"  ok {name}: {n} righe  ({done} fatti, {len(todo)} in coda)", flush=True)
    print("  storico completo", flush=True)


if __name__ == "__main__":
    main()
