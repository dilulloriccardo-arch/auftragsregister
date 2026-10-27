"""The canton(s) of a simap publication, and where they come from (step 3a, 14.10.2026).

genera.py (the pages) and avvisi/invia_avvisi.py (the e-mail alerts) both read this module, so a
tender is listed and announced under the same cantons.

What the records carry. The Apify actor (apify-actors/simap-tenders/src/transform.py) writes `canton`
from the publication's order address, orderAddress.cantonId — the field simap.ch's own canton filter
uses — and, when the order address names no canton, silently from the buyer's seat (merge_details).
lotti.py's lot records have no order address at all, so their `canton` is always the buyer's. Each lot
carries the canton of its own order address in `lots[].canton`.

How the fallback is recognised. An order address that names a place has a city or a postal code. In
the archive of 14.10.2026, none of the 8'914 records without either carries a canton other than the
buyer's, while 706 of the 12'116 with one do: without a place, `canton` is the buyer's seat.

The source of a record's canton(s), one of SOURCES:
    "ort"           the order address (the place of performance the publication gives)
    "lose"          the order addresses of its lots
    "auftraggeber"  none given: the canton of the buyer's seat, marked as such on the pages
    ""              no canton at all
"""
from __future__ import annotations

CANTONS = frozenset(("AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU", "LU", "NE",
                     "NW", "OW", "SG", "SH", "SO", "SZ", "TG", "TI", "UR", "VD", "VS", "ZG", "ZH"))
SOURCES = ("ort", "lose", "auftraggeber", "")


def _code(v) -> str:
    v = str(v or "").strip().upper()
    return v if v in CANTONS else ""


def buyer_canton(r: dict) -> str:
    """The canton of the buyer's seat (procOfficeAddress), '' when it has none."""
    return _code((r.get("buyer") or {}).get("canton") if isinstance(r.get("buyer"), dict) else "")


def order_canton(r: dict) -> str:
    """The canton of the record's own order address, '' when the publication gives none.

    `canton` is the order address's when the order address names a place (a city or a postal code),
    or when it differs from the buyer's seat (the fallback copies the buyer's canton, so a different
    one can only be the order address's)."""
    k = _code(r.get("canton"))
    if not k:
        return ""
    if str(r.get("city") or "").strip() or str(r.get("postalCode") or "").strip():
        return k
    b = buyer_canton(r)
    return k if b and k != b else ""


def lot_cantons(r: dict) -> dict:
    """lot number -> the canton of that lot's order address, for the lots that name one."""
    out = {}
    for x in r.get("lots") or []:
        if isinstance(x, dict):
            k = _code(x.get("canton"))
            if k:
                out[x.get("lotNumber")] = k
    return out


def fallback_canton(r: dict) -> str:
    """The buyer's canton the actor put into `canton` when the order address named none."""
    return buyer_canton(r) or _code(r.get("canton"))


def cantons_of(r: dict) -> tuple[list, str]:
    """(cantons, source) of a tender: the order address's canton together with its lots' cantons; with
    neither, the buyer's seat. A tender is listed, and announced by e-mail, under each of them."""
    o = order_canton(r)
    lots = sorted(set(lot_cantons(r).values()))
    if o:
        return [o] + [k for k in lots if k != o], "ort"
    if lots:
        first = primary(r)
        return [first] + [k for k in lots if k != first], "lose"
    fb = fallback_canton(r)
    return ([fb], "auftraggeber") if fb else ([], "")


def primary(r: dict) -> str:
    """The first canton of cantons_of(): the order address's, else the most frequent lot canton
    (ties to the lower code), else the buyer's seat."""
    o = order_canton(r)
    if o:
        return o
    lots = list(lot_cantons(r).values())
    if lots:
        return min(set(lots), key=lambda k: (-lots.count(k), k))
    return fallback_canton(r)


def award_canton(r: dict, lot=None) -> tuple[str, str]:
    """(canton, source) of an award: ONE canton, so that a sum over cantons never counts an award
    twice. The award of a lot keeps its own lot's canton; else the order address's; else the lots'
    when they all name the same one; else the buyer's seat."""
    lots = lot_cantons(r)
    if lot is not None and lots.get(lot):
        return lots[lot], "lose"
    o = order_canton(r)
    if o:
        return o, "ort"
    if len(set(lots.values())) == 1:
        return next(iter(lots.values())), "lose"
    fb = fallback_canton(r)
    return (fb, "auftraggeber") if fb else ("", "")
