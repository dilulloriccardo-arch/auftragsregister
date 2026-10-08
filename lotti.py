#!/usr/bin/env python3
"""The lot awards the nightly pull cannot see.

simap publishes a project split into lots with one award publication PER LOT (28439-02 for
lot 1, 28439-03 for lot 2), but its project-search answers with one row per project, that
project's newest publication, and the Apify actor turns each row into one record. On
08.10.2026 that had left 2'684 lot awards of 856 projects out of dati/: 6965 has 15 on simap
and had 1 here, and 22300-04 (Sword Services, Geneva) was nowhere.

For every project with lots in dati/ this asks simap's project-header which publication each
lot carries, fetches the award publications not on disk yet and appends them, in the actor's
record format, to the month of their publicationDate. Append-only, deduplicated on
publicationId. dati/lotti_checked.json keeps each project's newest publication date, so a
project is asked again only once a newer publication of it reaches dati/.

    python3 lotti.py              # one polite run: sequential, at most 400 + 400 requests
    python3 lotti.py --dry-run    # fetch and convert, write nothing
"""
from __future__ import annotations

import argparse
import collections
import html
import http.client
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

import lingue

ROOT = pathlib.Path(__file__).resolve().parent
DATI = ROOT / "dati"
CHECKED = DATI / "lotti_checked.json"

BASE_URL = "https://www.simap.ch"
HEADER_PATH = "/api/publications/v2/project/{pid}/project-header"
DETAILS_PATH = "/api/publications/v1/project/{pid}/publication-details/{pubid}"
PUBLIC_URL = "https://www.simap.ch/{lang}/project-detail/{pid}"
LANG = "de"         # aggiorna.py asks the actor for German records
UA = "auftragsregister.ch (+https://auftragsregister.ch)"

# Polite by construction: one request at a time, at most ~3 a second, and a ceiling per run.
# The backfill of 08.10.2026 took 1'081 headers and 3'547 details in 9 runs (29 minutes); a
# normal night asks for a handful.
MAX_HEADERS = 400
MAX_DETAILS = 400
PAUSE = 0.35                # seconds between two requests
TIMEOUT = 30
BACKOFF = (2, 5, 15, 40)    # waits before the retries of a 429/5xx or a network error
MAX_FAILS_IN_ROW = 5        # simap down: stop instead of retrying through the night
DEADLINE = 25 * 60          # aggiorna.py kills the run at 30 minutes: stop cleanly before
FLUSH_EVERY = 25            # projects between two writes: an interrupted run keeps its work


# ------------------------------------------------------------------ the actor's transform
# Copied from the simap Apify actor (apify-actors/simap-tenders/src/transform.py, 21.08.2026)
# so these records cannot be told from the ones aggiorna.py pulls: same keys, same order, same
# cleaning. Only the part the actor takes from the search row is rebuilt, from the header.

LANG_ORDER = ("it", "de", "fr", "en")
DISCLAIMER = ("Dies ist keine amtliche Veröffentlichung. Massgebend sind die auf der "
              "Plattform www.simap.ch veröffentlichten Daten.")

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t ]+")
_NL_RE = re.compile(r"\n{3,}")


def strip_html(text):
    if not text:
        return text
    t = re.sub(r"(?i)<\s*br\s*/?>", "\n", text)
    t = re.sub(r"(?i)</\s*(p|div|li|h\d|tr)\s*>", "\n", t)
    t = re.sub(r"(?i)<\s*li[^>]*>", "- ", t)
    t = _TAG_RE.sub("", t)
    t = html.unescape(t)
    t = _WS_RE.sub(" ", t)
    t = "\n".join(line.strip() for line in t.split("\n"))
    t = _NL_RE.sub("\n\n", t).strip()
    return t or None


def pick_lang(translation, lang):
    """The preferred language's text, else it -> de -> fr -> en."""
    return _pick(translation, lang)[0]


def _pick(translation, lang):
    if not translation or not isinstance(translation, dict):
        return None, None
    if translation.get(lang):
        return translation[lang], lang
    for alt in LANG_ORDER:
        if translation.get(alt):
            return translation[alt], alt
    return None, None


def _translations(translation, strip: bool) -> dict:
    if not translation or not isinstance(translation, dict):
        return {}
    return {k: (strip_html(v) if strip else v) for k, v in translation.items() if v}


def _address(addr, lang):
    if not addr:
        return None
    return {
        "name": pick_lang(addr.get("name"), lang),
        "street": pick_lang(addr.get("street"), lang),
        "postalCode": (addr.get("postalCode") or "").strip() or None,
        "city": pick_lang(addr.get("city"), lang),
        "canton": addr.get("cantonId"),
        "country": addr.get("countryId"),
        "email": addr.get("email"),
        "phone": addr.get("phone"),
        "url": pick_lang(addr.get("url"), lang),
        "contactPerson": pick_lang(addr.get("contactPerson"), lang),
    }


def merge_details(rec: dict, details: dict, lang: str, strip: bool = True,
                  referenced_details: dict | None = None) -> dict:
    """The actor's merge_details, unchanged: award payloads carry no criteria or dates, so
    those come from the tender the award refers to (criteriaSource 'referencedTender')."""
    info = details.get("project-info") or {}
    proc = details.get("procurement") or {}
    base = details.get("base") or {}

    criteria_source = None
    if details.get("criteria") is not None or details.get("dates") is not None:
        criteria_source = "publication"
        crit_src = details
    elif referenced_details:
        criteria_source = "referencedTender"
        crit_src = referenced_details
    else:
        crit_src = details
    dates = crit_src.get("dates") or {}
    crit = crit_src.get("criteria") or {}

    def txt(t):
        return strip_html(pick_lang(t, lang)) if strip else pick_lang(t, lang)

    cpv = proc.get("cpvCode") or base.get("cpvCode") or {}
    additional_cpv = proc.get("additionalCpvCodes") or base.get("additionalCpvCodes") or []
    desc_raw = pick_lang(proc.get("orderDescription"), lang)
    qnas = dates.get("qnas") or []
    rec.update({
        "cpvCode": cpv.get("code"),
        "cpvLabel": pick_lang(cpv.get("label"), lang),
        "additionalCpvCodes": [
            {"code": a.get("code"), "label": pick_lang(a.get("label"), lang)}
            for a in additional_cpv if isinstance(a, dict) and a.get("code")
        ],
        "description": strip_html(desc_raw) if strip else desc_raw,
        "orderType": crit.get("orderType") or proc.get("orderType"),
        "offerDeadline": dates.get("offerDeadline"),
        "offerOpening": (dates.get("offerOpening") or {}).get("dateTime"),
        "offerValidityUntil": dates.get("offerValidityDeadlineDate"),
        "qnaDeadline": next((q.get("date") for q in qnas if q.get("date")), None),
        "qnaNote": txt(next((q.get("note") for q in qnas), None)),
        "documentsAvailableFrom": next(iter(((dates.get("documentsAvailable") or {}).get("dateRange") or [])), None),
        "specificDeadlinesAndFormalRequirements": txt(dates.get("specificDeadlinesAndFormalRequirements")),
        "stateContractArea": info.get("stateContractArea"),
        "publicationTed": info.get("publicationTed"),
        "documentsWithCosts": info.get("documentsWithCosts"),
        "documentsSourceType": info.get("documentsSourceType"),
        "buyer": _address(info.get("procOfficeAddress"), lang),
        "recipient": _address(info.get("procurementRecipientAddress"), lang),
        "awardCriteria": [
            {
                "title": pick_lang(c.get("title"), lang),
                "weighting": c.get("weighting"),
                "maxPoints": c.get("maxPoints"),
                "isPriceCriterion": c.get("isPriceCriterion"),
                "description": txt(c.get("description")),
            }
            for c in (crit.get("awardCriteria") or [])
        ],
        "awardCriteriaSelection": crit.get("awardCriteriaSelection"),
        "criteriaSource": criteria_source,
        "qualificationCriteria": [
            {"title": pick_lang(c.get("title"), lang), "description": txt(c.get("description"))}
            for c in (crit.get("qualificationCriteria") or [])
        ],
        "lotsDetailed": [
            {
                "lotNumber": lot.get("lotNumber"),
                "title": pick_lang(lot.get("title"), lang),
                "cpvCode": (lot.get("cpvCode") or {}).get("code"),
                "additionalCpvCodes": [a.get("code") for a in (lot.get("additionalCpvCodes") or [])
                                       if isinstance(a, dict) and a.get("code")],
                "description": txt(lot.get("orderDescription")),
            }
            for lot in (details.get("lots") or [])
        ],
    })
    rec["translations"]["description"] = _translations(proc.get("orderDescription"), strip)

    decision = details.get("decision") or {}
    if decision:
        price_range = decision.get("totalPriceRange") or {}
        # the bounds live one level down: {"currency": "chf", "range": {"from": .., "to": ..}}
        price_bounds = price_range.get("range") or {}
        rec["award"] = {
            "awardDecisionDate": decision.get("awardDecisionDate"),
            "numberOfSubmissions": decision.get("numberOfSubmissions"),
            "totalPriceSelection": decision.get("totalPriceSelection"),
            "totalPriceRange": {
                "min": price_bounds.get("from"),
                "max": price_bounds.get("to"),
                "currency": price_range.get("currency"),
            } if price_range else None,
            "justification": txt(decision.get("awardDecisionJustification")),
            "note": txt(decision.get("awardDecisionNote")),
            "vendors": [
                {
                    "rank": v.get("rank"),
                    "name": v.get("vendorName"),
                    "street": (v.get("vendorAddress") or {}).get("street"),
                    "postalCode": (v.get("vendorAddress") or {}).get("postalCode"),
                    "city": (v.get("vendorAddress") or {}).get("city"),
                    "canton": (v.get("vendorAddress") or {}).get("cantonId"),
                    "country": (v.get("vendorAddress") or {}).get("countryId"),
                    "price": (v.get("price") or {}).get("price"),
                    "currency": ((v.get("price") or {}).get("currency") or "").upper() or None,
                    "vatType": (v.get("price") or {}).get("vatType"),
                    "note": txt(v.get("note")),
                }
                for v in (decision.get("vendors") or [])
            ],
        }
        vendors = rec["award"]["vendors"]
        rec["winnerName"] = vendors[0]["name"] if vendors else None
        rec["winnerPrice"] = vendors[0]["price"] if vendors else None
        rec["winnerCurrency"] = vendors[0]["currency"] if vendors else None
        ref = details.get("referencingPub") or {}
        if ref:
            rec["referencedTender"] = {
                "publicationId": ref.get("publicationId"),
                "publicationNumber": ref.get("publicationNumber"),
                "publicationDate": ref.get("publicationDate"),
                "pubType": ref.get("pubType"),
            }
    if not rec.get("buyerName") and rec.get("buyer"):
        rec["buyerName"] = rec["buyer"].get("name")
    if not rec.get("canton") and rec.get("buyer"):
        rec["canton"] = rec["buyer"].get("canton")
    return rec


# ------------------------------------------------------------------ one lot, one record

# a lot whose own name already says which lot it is: 'Los 3 Zone C', 'Lotto 1 - Medicamenti'
_NAMED = re.compile(r"(?:teil)?(?:los|lose|lot|lots|lotto|lotti)\b", re.I)


def _same(a: str, b: str) -> bool:
    return " ".join(a.split()).casefold() == " ".join(b.split()).casefold()


def lot_title(title, lot, n, lang) -> str | None:
    """The project's title with the lot named after it, in the language of `title`.

    simap gives every lot award the project's title only: 15 awards of 6965 read
    'Consultants Informatiques - Référencement' and nothing said which was which.
    """
    title, lot = (title or "").strip(), (lot or "").strip()
    if not title or n is None:
        return title or lot or None
    lang = lang if lang in ("de", "fr", "it", "en") else "de"
    if not re.search(r"[^\W\d_]", lot) or _same(lot, title):
        return lingue.i("lot_award_title_bare", lang, title=title, n=n)
    if " ".join(lot.split()).casefold().startswith(" ".join(title.split()).casefold()):
        return lot      # 'Pose de compteurs SMART - secteur Nord' names project and lot
    key = "lot_award_title_named" if _NAMED.match(lot) else "lot_award_title"
    return lingue.i(key, lang, title=title, n=n, lot=lot)


def to_record(head: dict, lot: dict, det: dict, ref_det: dict | None, proj: dict) -> dict:
    """One lot's award publication in the record format of the actor's search rows.

    The search row of a lot project carries no order address (country, city and postal code
    were empty on all 1'114 lot records of 08.10.2026, the canton is the buyer's), and its
    title and buyer name are the project's: both are taken from the record already here, so
    all lots of one project land on the same buyer page. The award publication alone would
    give fewer titles: 9002-08 has German only, its project also French and English.
    """
    lp = lot.get("latestPublication") or {}
    base = det.get("base") or {}
    pid = head.get("id") or base.get("projectId")
    own = det.get("lot") or {}
    n = own.get("lotNumber") if own.get("lotNumber") is not None else lot.get("lotNumber")
    lot_tr = own.get("title") or lot.get("title") or {}
    sib = proj.get("sib") or {}
    titles = {k: v for k, v in ((sib.get("translations") or {}).get("title") or {}).items() if v}
    if titles:
        raw, raw_lang = sib.get("title"), _pick(titles, LANG)[1]
    else:
        pub_tr = lp.get("title") or base.get("title") or (det.get("project-info") or {}).get("title")
        titles = {k: v for k, v in _translations(pub_tr, True).items() if v}
        raw, raw_lang = _pick(pub_tr, LANG)
    number = lp.get("publicationNumber") or base.get("publicationNumber")
    if isinstance(number, dict):
        number = number.get("number")
    rec = {
        "projectId": pid,
        "publicationId": lp.get("id"),
        "projectNumber": head.get("projectNumber") or base.get("projectNumber"),
        "publicationNumber": number,
        "pubType": lp.get("pubType"),
        "projectType": head.get("projectType") or lp.get("projectType"),
        "projectSubType": head.get("projectSubType") or lp.get("projectSubType"),
        "processType": head.get("processType") or lp.get("processType"),
        "lotsType": head.get("lotsType"),
        "corrected": lp.get("corrected"),
        "publicationDate": (lp.get("dates") or {}).get("publicationDate") or base.get("publicationDate"),
        "title": lot_title(raw, lot_tr.get(raw_lang) or pick_lang(lot_tr, raw_lang or LANG),
                           n, raw_lang),
        "buyerName": sib.get("buyerName"),
        "canton": None,
        "country": None,
        "city": None,
        "postalCode": None,
        "lots": [
            {
                "lotNumber": x.get("lotNumber"),
                "lotTitle": pick_lang(x.get("title"), LANG),
                "publicationDate": ((x.get("latestPublication") or {}).get("dates") or {}).get("publicationDate"),
                "pubType": (x.get("latestPublication") or {}).get("pubType"),
                # the header has no address: the lot's canton as the search row gave it
                "canton": proj.get("cantons", {}).get(x.get("lotNumber")),
            }
            for x in (head.get("lots") or [])
        ],
        "simapUrl": PUBLIC_URL.format(lang=LANG, pid=pid),
        "translations": {"title": {
            lang: lot_title(t, strip_html(lot_tr.get(lang) or pick_lang(lot_tr, lang)), n, lang)
            for lang, t in titles.items()
        }},
        "source": "simap.ch",
        "disclaimer": DISCLAIMER,
    }
    return merge_details(rec, det, LANG, True, referenced_details=ref_det)


# ------------------------------------------------------------------ simap, politely

class Budget(Exception):
    """This run's share of simap is used up: the next run carries on."""


class SimapError(Exception):
    """A request that still failed after its retries."""


class Simap:
    def __init__(self, max_headers: int, max_details: int, deadline: float) -> None:
        self.cap = {"header": max_headers, "details": max_details}
        self.used = collections.Counter()
        self.deadline = deadline
        self.fails_in_row = 0
        self._last = 0.0

    def header(self, pid: str):
        return self._get("header", HEADER_PATH.format(pid=pid))

    def details(self, pid: str, pubid: str):
        return self._get("details", DETAILS_PATH.format(pid=pid, pubid=pubid))

    def _get(self, kind: str, path: str):
        """JSON, or None for a 404 (withdrawn from simap)."""
        if self.used[kind] >= self.cap[kind]:
            raise Budget(f"limite di {self.cap[kind]} richieste {kind}")
        if time.monotonic() > self.deadline:
            raise Budget(f"limite di {DEADLINE // 60} minuti")
        self.used[kind] += 1
        err = ""
        for attempt in range(len(BACKOFF) + 1):
            wait = PAUSE - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            req = urllib.request.Request(BASE_URL + path,
                                         headers={"Accept": "application/json", "User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                    data = json.loads(r.read().decode("utf-8"))
                self.fails_in_row = 0
                return data
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    self.fails_in_row = 0
                    return None
                err = f"HTTP {e.code}"
                if e.code in (429, 500, 502, 503, 504) and attempt < len(BACKOFF):
                    time.sleep(_retry_after(e, BACKOFF[attempt]))
                    continue
            # ValueError: a maintenance page in place of the JSON
            except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as e:
                err = type(e).__name__
                if attempt < len(BACKOFF):
                    time.sleep(BACKOFF[attempt])
                    continue
            break
        self.fails_in_row += 1
        raise SimapError(f"{err} su {path}")


def _retry_after(e: urllib.error.HTTPError, default: float) -> float:
    try:
        return min(120.0, max(default, float(e.headers.get("Retry-After") or 0)))
    except (TypeError, ValueError):
        return default


# ------------------------------------------------------------------ dati/

_LOT_MARK = re.compile(r" – (?:Los|lot|lotto|Lot) \d+")


def load_dati() -> tuple:
    """publicationIds on disk, and per lot project: its newest publication date, the record
    its buyer name comes from and each lot's canton."""
    have, projects = set(), {}
    for f in sorted(DATI.glob("aggiudicazioni_*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            if r.get("publicationId"):
                have.add(r["publicationId"])
            pid = r.get("projectId")
            if not pid or r.get("lotsType") != "with":
                continue
            p = projects.setdefault(pid, {"newest": "", "sib": None, "cantons": {}})
            day = (r.get("publicationDate") or "")[:10]
            p["newest"] = max(p["newest"], day)
            # the project's title and buyer come from a record simap titled itself: one this module
            # wrote already names its lot, and reusing it gave '… – lot 4 : … – lot 5 : …' (08.10.2026)
            if r.get("buyerName"):
                cur = p["sib"]
                mine, theirs = bool(_LOT_MARK.search(r.get("title") or "")), bool(cur and _LOT_MARK.search(cur.get("title") or ""))
                if cur is None or (theirs and not mine) or (
                        mine == theirs and day >= (cur.get("publicationDate") or "")[:10]):
                    p["sib"] = r
            for x in r.get("lots") or []:
                if x.get("canton"):
                    p["cantons"][x.get("lotNumber")] = x["canton"]
    return have, projects


def load_checked() -> dict:
    try:
        return json.loads(CHECKED.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def _write(path: pathlib.Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def append(recs: list) -> collections.Counter:
    """New records at the end of their month's file. Never rewrites what is there: the
    file is read back before it replaces the old one, and a write that would leave fewer
    records than before is refused (the archive only grows)."""
    by_month = collections.defaultdict(list)
    for r in recs:
        by_month[r["publicationDate"][:7]].append(r)
    added = collections.Counter()
    for month, rows in sorted(by_month.items()):
        path = DATI / f"aggiudicazioni_{month}.json"
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        ids = {r.get("publicationId") for r in old}
        new = [r for r in rows if r["publicationId"] not in ids]
        if not new:
            continue
        # in publication order: 6965-03 … -16, not the order the requests happened to run
        new.sort(key=lambda r: (r["publicationDate"], r["projectNumber"] or "",
                                _suffix(r["publicationNumber"])))
        merged = old + new
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
        back = json.loads(tmp.read_text(encoding="utf-8"))
        if len(back) != len(old) + len(new) or back[:len(old)] != old:
            tmp.unlink()
            raise RuntimeError(f"{path.name}: rilettura diversa da quanto scritto, non sostituito")
        os.replace(tmp, path)
        added[month] += len(new)
    return added


def _suffix(number) -> int:
    tail = str(number or "").rsplit("-", 1)[-1]
    return int(tail) if tail.isdigit() else -1


def _n(k: int, one: str, many: str) -> str:
    return f"{k} {one if k == 1 else many}"


# ------------------------------------------------------------------ the run

def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description="Aggiudicazioni dei lotti mancanti da simap.")
    ap.add_argument("--dry-run", action="store_true", help="scarica e converte, non scrive")
    ap.add_argument("--max-headers", type=int, default=MAX_HEADERS)
    ap.add_argument("--max-details", type=int, default=MAX_DETAILS)
    args = ap.parse_args(argv)

    t0 = time.monotonic()
    have, projects = load_dati()
    checked = load_checked()
    # newest first: the projects a reader is most likely to look up
    todo = sorted((pid for pid, p in projects.items()
                   if pid not in checked or p["newest"] > checked[pid]),
                  key=lambda pid: (projects[pid]["newest"], pid), reverse=True)
    simap = Simap(args.max_headers, args.max_details, t0 + DEADLINE)
    pending, done, refs = [], {}, {}
    added = collections.Counter()
    n_checked = n_gone = n_err = 0
    stop = ""

    def flush() -> None:
        # records first, then the projects they complete: a project is never remembered as
        # done while its awards are only in memory
        if not args.dry_run:
            added.update(append(pending))
            checked.update(done)
            _write(CHECKED, json.dumps(checked, indent=0, sort_keys=True))
        else:
            added.update(collections.Counter(r["publicationDate"][:7] for r in pending))
        pending.clear()
        done.clear()

    for i, pid in enumerate(todo):
        try:
            head = simap.header(pid)
        except Budget as exc:
            stop = str(exc)
            break
        except SimapError:
            n_err += 1
            if simap.fails_in_row >= MAX_FAILS_IN_ROW:
                stop = "simap non risponde"
                break
            continue
        n_checked += 1
        newest = projects[pid]["newest"]
        if head is None:            # withdrawn from simap: nothing left to fetch
            n_gone += 1
            done[pid] = newest
            continue
        complete, here = True, set()
        for lot in head.get("lots") or []:
            lp = lot.get("latestPublication") or {}
            newest = max(newest, ((lp.get("dates") or {}).get("publicationDate") or "")[:10])
            pub = lp.get("id")
            if not pub or pub in have or pub in here or lp.get("pubType") != "award":
                continue
            here.add(pub)
            try:
                det = simap.details(pid, pub)
                if det is None:
                    continue
                ref = None
                if det.get("criteria") is None and det.get("dates") is None:
                    ref_pub = (det.get("referencingPub") or {}).get("publicationId")
                    if ref_pub and ref_pub != pub:
                        if ref_pub not in refs:
                            refs[ref_pub] = simap.details(pid, ref_pub)
                        ref = refs[ref_pub]
            except Budget as exc:
                stop, complete = str(exc), False
                break
            except SimapError:
                n_err += 1
                complete = False
                if simap.fails_in_row >= MAX_FAILS_IN_ROW:
                    stop = "simap non risponde"
                    break
                continue
            try:
                rec = to_record(head, lot, det, ref, projects[pid])
            except Exception as exc:  # one odd payload must not block the projects behind it
                print(f"lotti: {pid}/{pub} non convertibile ({type(exc).__name__}), riprovo al prossimo giro")
                n_err += 1
                complete = False
                continue
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(rec.get("publicationDate") or "")[:10]):
                n_err += 1          # cannot be filed under a month: asked again next run
                complete = False
                continue
            pending.append(rec)
            have.add(pub)
        if complete:
            done[pid] = newest
        if stop:
            break
        if (i + 1) % FLUSH_EVERY == 0:
            flush()
    flush()

    left = sum(1 for pid, p in projects.items() if pid not in checked or p["newest"] > checked[pid])
    secs = int(time.monotonic() - t0)
    total = sum(added.values())
    print(f"lotti: {_n(n_checked, 'progetto controllato', 'progetti controllati')}, "
          f"+{_n(total, 'aggiudicazione', 'aggiudicazioni')} di lotti"
          + (f" in {_n(len(added), 'mese', 'mesi')}" if added else "")
          + f", {_n(left, 'progetto', 'progetti')} ancora da controllare"
          + (f", {_n(n_err, 'errore', 'errori')}" if n_err else "")
          + (f", {n_gone} non piu' su simap" if n_gone else "")
          + f"; {simap.used['header']}+{simap.used['details']} richieste in {secs // 60}:{secs % 60:02d}"
          + (f" (fermato: {stop})" if stop else "")
          + (" [prova, nulla scritto]" if args.dry_run else ""), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
