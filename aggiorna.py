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
import http.client
import json
import os
import pathlib
import shutil
import socket
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


_RETRY_WAIT = (15, 45, 120)
_TRANSIENT = (urllib.error.URLError, ConnectionError, TimeoutError, socket.timeout,
              http.client.HTTPException)


def _pre_send(exc: BaseException) -> bool:
    """True when the request certainly never reached the server (refused, no DNS)."""
    reason = getattr(exc, "reason", exc)
    return isinstance(reason, (ConnectionRefusedError, socket.gaierror))


def _open(url: str, timeout: int, method: str = "GET", data=None, headers=None) -> bytes:
    """urlopen with retries for transient network errors.

    On 24.09.2026 one "connection reset by peer" while polling a run's status killed the
    whole nightly: the awards were fetched, the tenders never, and nothing was published.
    GETs are retried on any transient error. A POST is retried only when the connection
    was never established, so a retry can never start a second paid Actor run.
    """
    for attempt in range(len(_RETRY_WAIT) + 1):
        req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if method == "GET" and e.code in (429, 500, 502, 503, 504) and attempt < len(_RETRY_WAIT):
                say(f"  rete: HTTP {e.code}, nuovo tentativo fra {_RETRY_WAIT[attempt]} s")
                time.sleep(_RETRY_WAIT[attempt]); continue
            raise
        except _TRANSIENT as e:
            if (method == "GET" or _pre_send(e)) and attempt < len(_RETRY_WAIT):
                say(f"  rete: {type(e).__name__}, nuovo tentativo fra {_RETRY_WAIT[attempt]} s")
                time.sleep(_RETRY_WAIT[attempt]); continue
            raise
    raise RuntimeError("unreachable")


def api(method: str, path: str, body=None):
    url = f"https://api.apify.com/v2{path}{'&' if '?' in path else '?'}token={TOKEN}"
    raw = _open(url, 180, method, json.dumps(body).encode() if body is not None else None,
                {"Content-Type": "application/json"})
    return json.loads(raw.decode()).get("data", {})


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
    items = json.loads(_open(
        f"https://api.apify.com/v2/datasets/{r['defaultDatasetId']}/items"
        f"?token={TOKEN}&clean=true&limit=50000", 300))
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


def wait_online(attempts: int = 12, wait: int = 150) -> bool:
    """Alle 05:40 la rete del Mac puo' non esserci (3/9/2026: DNS giu').
    Aspetta fino a ~30 minuti prima di arrendersi, invece di morire subito."""
    import socket, time
    for i in range(attempts):
        try:
            socket.gethostbyname("api.apify.com")
            return True
        except OSError:
            say(f"rete assente (tentativo {i + 1}/{attempts}), riprovo tra {wait}s")
            time.sleep(wait)
    say("rete assente per 30 minuti: rinuncio, si riprova domani")
    return False


# simap AGB API Ziff. 5 (letta 2026-09-04 su simap.ch/de/about/legal):
# «Die simap-Daten dürfen Dritten ab 8:00 Uhr des Erscheinungstages bekannt
# gegeben werden.» Le pubblicazioni del giorno stesso entrano nella finestra di
# fetch, quindi pubblicare il sito prima delle 08:00 (ora di Zurigo) viola il
# contratto. Il job è schedulato alle 08:20; questo blocco impedisce che una
# modifica futura dello schedule, o un lancio manuale, ripubblichi troppo presto.
EMBARGO_ORA = 8


def embargo_ok() -> bool:
    now = datetime.datetime.now()
    if now.hour >= EMBARGO_ORA:
        return True
    say(f"prima delle {EMBARGO_ORA}:00: i dati simap del giorno non possono "
        f"ancora essere pubblicati (AGB API Ziff. 5) — non faccio nulla")
    return False


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def unpushed() -> str:
    """How many local commits GitHub does not have yet ("" when git cannot tell: treated as unsafe)."""
    r = git("rev-list", "--count", "@{u}..HEAD")
    return r.stdout.strip() if r.returncode == 0 else ""


def mark_published(complete: bool = True) -> None:
    """Called only when every commit is on GitHub. The alert sender reads nothing but this copy, so an
    e-mail never links to a page a failed push or failed checks kept offline; ultimo_ok.txt tells the
    catch-up job the day is done. dati/ is gitignored: neither file ever reaches the public repo."""
    src = DATI / "gare_aperte.json"
    if src.exists():
        tmp = DATI / "gare_pubblicate.json.tmp"
        shutil.copyfile(src, tmp)
        os.replace(tmp, DATI / "gare_pubblicate.json")
    if complete:   # a failed Apify pull leaves the day open, so the catch-up tries again
        (DATI / "ultimo_ok.txt").write_text(datetime.date.today().isoformat() + "\n")
    else:
        say("  un download Apify e' fallito: giornata NON segnata come fatta, il recupero riprovera'")


def send_alerts() -> None:
    """E-mail alerts on the data just published. Never turns a good nightly red."""
    try:
        r = subprocess.run([sys.executable, str(ROOT / "avvisi" / "invia_avvisi.py")],
                           capture_output=True, text=True, cwd=ROOT, timeout=1500)
    except Exception as exc:   # hung or missing sender: the 12:30 fallback run tries again
        say(f"  ATTENZIONE avvisi non eseguiti: {type(exc).__name__}")
        return
    out = (r.stdout.strip().splitlines() or [""])[-1]
    if r.returncode == 0:
        say(f"  avvisi: {out}")
    else:
        say(f"  ATTENZIONE avvisi exit {r.returncode}: {out} {r.stderr.strip()[-400:]}")


def main() -> int:
    if not embargo_ok():
        return 0
    if not wait_online():
        return 2
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
    add = git("add", "-A")
    if add.returncode != 0:
        say(f"  ATTENZIONE git add fallito — NON pubblicato: {add.stderr.strip()[:300]}")
        return 1
    st = git("status", "--porcelain").stdout.strip()
    if not st:
        # a clean tree only means nothing changed since the last COMMIT: after a failed push that
        # commit is still local, so push it before telling anyone the pages exist
        ahead = unpushed()
        if ahead != "0":
            push = git("push", "-q")
            if push.returncode != 0 or unpushed() != "0":
                say(f"  ATTENZIONE push dei commit in sospeso fallito — NON pubblicato: {push.stderr.strip()[:300]}")
                return 1
            say(f"pubblicato: {ahead or '?'} commit in sospeso, nessuna pagina nuova")
        else:
            say(f"nessun cambiamento — {pages} pagine invariate")
        mark_published(-1 not in (n_now, n_prev, n_open))
        send_alerts()
        return 0
    changed = len(st.splitlines())
    commit = git("-c", "user.email=dilulloriccardo@gmail.com", "-c", "user.name=Riccardo Di Lullo",
                 "commit", "-q", "-m", f"Aggiornamento {datetime.date.today():%Y-%m-%d}: "
                                       f"{changed} pagine cambiate")
    if commit.returncode != 0:
        say(f"  ATTENZIONE commit fallito — NON pubblicato: {(commit.stderr or commit.stdout).strip()[:300]}")
        return 1
    push = git("push", "-q")
    if push.returncode != 0:
        say(f"  ATTENZIONE push fallito: {push.stderr.strip()[:300]}")
        return 1
    if unpushed() != "0":
        say("  ATTENZIONE dopo il push GitHub non ha ancora tutti i commit — NON pubblicato")
        return 1
    say(f"pubblicato: {changed} pagine cambiate su {pages}")
    mark_published(-1 not in (n_now, n_prev, n_open))

    # Only the pages that changed: submitting the whole site nightly is what gets a
    # host throttled, and IndexNow exists precisely to avoid that.
    site, base = "", ""
    try:
        lines = (ROOT / "dominio.txt").read_text().strip().splitlines()
        site = lines[0].strip().rstrip("/")
        base = lines[1].strip().rstrip("/") if len(lines) > 1 else ""
        urls = []
        for line in st.splitlines():
            f = line[3:].strip().strip('"')
            if f.startswith("docs/") and f.endswith("index.html"):
                rel = f[len("docs"):-len("index.html")]
                urls.append(f"{site}{base}{rel}")
        if urls:
            r = subprocess.run([sys.executable, str(ROOT / "indexnow.py")],
                               input="\n".join(urls[:10000]), text=True,
                               capture_output=True, cwd=ROOT)
            say("  " + (r.stdout.strip() or r.stderr.strip()[:200]))
    except Exception as exc:
        say(f"  IndexNow saltato: {type(exc).__name__}")
    say(f"dati: {n_now} questo mese, {n_prev} il mese scorso, {n_open} bandi aperti")
    send_alerts()
    return 0


if __name__ == "__main__":
    sys.exit(main())
