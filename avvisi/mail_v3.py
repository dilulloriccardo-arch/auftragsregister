#!/usr/bin/env python3
"""The e-mail alert of auftragsregister.ch, version 3: design A2 "Brass" (20.10.2026).

Template only. Nothing here sends, calls Brevo or touches the network.

    render(lang, rows, since, contact=None, today=None, *, cap=CAP, pro=False) -> (subject, html)
    render_text(...same arguments...) -> the plain-text part (Brevo's "textContent")
    fit(lang, rows, since, contact=None, today=None, *, cap=CAP) -> how many cards the e-mail shows

One e-mail per subscriber per day, never several (owner's decision, 21.10.2026). rows are ALL the
subscriber's new tenders, most urgent first (invia_avvisi.message() orders them); the e-mail shows the
first cap of them (40) as cards and counts the others in a line above the button to the site's list
("+ 23 weitere neue Ausschreibungen auf der Website"). Subject and band count them all.
contact (the Brevo contact, for its KANTON / BRANCHE) and today (ISO date, for "noch 3 Tage") are
optional; pro=True shows the slot for a future paid plan, off unless asked (the sender keeps it off).
It reads the site's own modules, which invia_avvisi.py already puts on sys.path: kantone.cantons_of
(the cantons a tender is listed and matched under) and lingue (site name, canton names, the short
names of the CPV divisions, the deadline words of the pages), so the e-mail names things as the pages do.

Why it holds in the clients that matter
- Structure: one black band (wordmark, count, selection), then white cards on the brand's ivory.
  Light is what the dark modes know how to handle: Outlook.com, the Outlook apps and Gmail for Android
  darken the light body and leave the black band alone; Apple Mail and Outlook.com get the A2 dark
  look itself from the prefers-color-scheme and [data-ogsc]/[data-ogsb] rules; Gmail for iOS and
  Outlook for Windows invert every colour, which keeps each text on a contrasting ground.
- Tables, inline styles and bgcolor on every coloured cell, at most 600 px (a ghost table for
  Outlook). The <style> blocks only add things (phones, dark mode, fonts) and are four, so a client
  that drops one (Gmail drops a block it cannot parse) keeps the others; without any of them the
  e-mail still reads right (labels lose their capitals, nothing else).
- Buttons: a brass cell and a link with its own padding (mso-padding-alt for Outlook); the A2 cut
  corner is drawn with borders in a cell Outlook never sees.
- Fonts: inline stacks start with a font Windows has (Arial; Impact for the display type), because
  Outlook for Windows falls back to Times New Roman when the first family is missing. Phones and Macs
  get Helvetica Neue Condensed Bold from an @media screen rule; Apple Mail loads AR Gothic and
  Instrument Sans from the site (@font-face inside @media screen, which Outlook never reads).
- Urgency is said three ways: the words ("noch 3 Tage"), a ▲, and a filled red block where the other
  deadlines have an outline.
- Size: about 1.7 KB per tender (40 real tenders: 78-82 KB). The e-mail is never split: fit() shows
  fewer than 40 cards (and counts the rest) only when 40 would take the HTML past 100 KB (owner's rule),
  i.e. with pathological titles. Gmail clips at 102 KB, hiding the footer with the unsubscribe link; on
  Brevo's click-tracking links see fits().
- No "{" or "}" from the data reaches Brevo's template engine (written as entities in the HTML, split
  by a zero-width space in the subject and the text part): only {{ unsubscribe }} is a tag.
"""
from __future__ import annotations

import datetime
import html as _html
import re
import urllib.parse

import lingue as L                    # the site's words (repo root on sys.path, as for kantone)
from kantone import cantons_of

SITE = "https://auftragsregister.ch"
FONTS = SITE + "/fonts/"              # AR Gothic and Instrument Sans, as the pages load them
URGENT_DAYS = 7
CAP = 40              # cards in the one e-mail of the day; the others are counted above the button to the list
BUDGET = 100_000      # bytes of HTML at most (owner's rule, 21.10.2026); 40 real cards are 78-82 KB
PER_LINK = 0          # bytes reserved per link for Brevo's click-tracking rewrite: none for now (see fits())
NBSP, NNBSP = "\u00a0", "\u202f"
WILDCARD = {"ALLE", "ALL", "TOUS", "TUTTI", "*", ""}
_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DMY = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})")
_PID = re.compile(r"^[A-Za-z0-9-]{1,80}$")
MON_EN = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# the German canton names live in genera.CANTONS (lingue.CANTON_NAMES["de"] is empty on purpose)
CANTONS_DE = {
    "AG": "Aargau", "AI": "Appenzell Innerrhoden", "AR": "Appenzell Ausserrhoden", "BE": "Bern",
    "BL": "Basel-Landschaft", "BS": "Basel-Stadt", "FR": "Freiburg", "GE": "Genf", "GL": "Glarus",
    "GR": "Graubünden", "JU": "Jura", "LU": "Luzern", "NE": "Neuenburg", "NW": "Nidwalden",
    "OW": "Obwalden", "SG": "St. Gallen", "SH": "Schaffhausen", "SO": "Solothurn", "SZ": "Schwyz",
    "TG": "Thurgau", "TI": "Tessin", "UR": "Uri", "VD": "Waadt", "VS": "Wallis", "ZG": "Zug", "ZH": "Zürich",
}

# ---------------------------------------------------------------- colours (A2 "Brass")
BLACK, IVORY, BODY, MUTED_D, GOLD, LINK_D = "#000000", "#f4f1ea", "#e2ddd1", "#a6a39b", "#d8b66a", "#f3dc9a"
BRASS, BRASS_LO, FIELD = "#c9a24e", "#9c7633", "#8a6a2d"
PAPER, CARD, LINE, CHIP = "#f4f1ea", "#ffffff", "#e2ddd1", "#fbf8f1"     # the light body
INK, MUTED, BRASS_TX = "#16130e", "#5c564c", "#7a5a1e"                  # text on the light body
RED, HOT = "#b3261e", "#ff9a8a"                                        # deadline within 7 days

# inline font stacks: a font Windows has comes first (Outlook uses only the first one)
FT = "font-family:Arial,sans-serif"
FD = "font-family:Impact,'Arial Narrow',sans-serif"

# ---------------------------------------------------------------- words
# The terms (one per concept), as the site names them since the plain-language pass (owner, 22.10.2026): the
# service «Ausschreibungen per E-Mail» / «Appels d’offres par e-mail» / «Bandi via e-mail» / «Tenders by email»;
# Eingabefrist / délai de remise des offres / termine d'inoltro / submission deadline next to a date;
# Auftraggeber / acheteur public / ente pubblico / public buyer; Branche / secteur / settore / sector.
# Italian: controls in the familiar imperative, the rest impersonal.
S = {
    "de": {
        "alert": "Ausschreibungen per E-Mail", "since": "Neu seit {d}",
        "n1": "1 neue Ausschreibung", "nn": "{n} neue Ausschreibungen",
        "h1": "Neue Ausschreibung", "hn": "Neue Ausschreibungen",
        "k1": "Kanton", "kn": "Kantone", "b1": "Branche", "bn": "Branchen",
        "all_k": "ganze Schweiz", "all_b": "alle Branchen",
        "urgent": "{u} mit Eingabefrist in den nächsten 7 Tagen", "next": "Nächste Eingabefrist: {d}",
        "web": "Alle neuen Ausschreibungen auf der Website",
        "more1": "{p} weitere neue Ausschreibung auf der Website",
        "moren": "{p} weitere neue Ausschreibungen auf der Website",
        "dl": "Eingabefrist", "buyer": "Auftraggeber", "corr": "Berichtigung", "open": "Zur Ausschreibung",
        "why": "Sie erhalten diese E-Mail, weil Sie «Ausschreibungen per E-Mail» von auftragsregister.ch gratis für "
               "diese Auswahl abonniert und bestätigt haben: {sel}.",
        "why0": "Sie erhalten diese E-Mail, weil Sie «Ausschreibungen per E-Mail» von auftragsregister.ch gratis "
                "abonniert und bestätigt haben.",
        "change": "Auswahl ändern: Melden Sie sich über «Abmelden» ab und abonnieren Sie dann auf der {a}Seite "
                  "«Ausschreibungen per E-Mail»{z} mit der neuen Auswahl erneut.",
        "unsub": "Abmelden", "privacy": "Datenschutz", "imprint": "Impressum",
        "source": "Quelle: simap.ch (amtliche Publikationen von Bund, Kantonen und Gemeinden)",
        "titles": "Titel erscheinen in der Sprache, in der sie publiziert wurden.", "asof": "Aktualisiert am {d}",
        "pro_tag": "CHF 29 pro Monat", "pro_h": "Mehr Kantone, mehr Branchen – und wer gewinnt",
        "pro_1": "Mehr Kantone und Branchen im selben Abo",
        "pro_2": "Jede Woche ein Bericht: wer in Ihren Kantonen und Branchen die Aufträge erhalten hat",
        "pro_cta": "Pro ansehen",
    },
    "fr": {
        "alert": "Appels d’offres par e-mail", "since": "Depuis le {d}",
        "n1": "1 nouvel appel d’offres", "nn": "{n} nouveaux appels d’offres",
        "h1": "Nouvel appel d’offres", "hn": "Nouveaux appels d’offres",
        "k1": "Canton", "kn": "Cantons", "b1": "Secteur", "bn": "Secteurs",
        "all_k": "toute la Suisse", "all_b": "tous les secteurs",
        "urgent": "{u} dont le délai expire dans les 7 prochains jours",
        "next": "Prochain délai\u202f: {d}",
        "web": "Tous les nouveaux appels d’offres sur le site",
        "more1": "{p} autre nouvel appel d’offres sur le site",
        "moren": "{p} autres nouveaux appels d’offres sur le site",
        "dl": "Délai de remise", "buyer": "Acheteur public", "corr": "Rectificatif",
        "open": "Voir l’appel d’offres",
        "why": "Vous recevez cet e-mail parce que vous avez confirmé votre abonnement gratuit à «\u202fAppels "
               "d’offres par e-mail\u202f» d’auftragsregister.ch pour cette sélection\u202f: {sel}.",
        "why0": "Vous recevez cet e-mail parce que vous avez confirmé votre abonnement gratuit à «\u202fAppels "
                "d’offres par e-mail\u202f» d’auftragsregister.ch.",
        "change": "Pour modifier votre sélection\u202f: désabonnez-vous par «\u202fSe désabonner\u202f», puis "
                  "abonnez-vous à nouveau avec la nouvelle sélection sur la {a}page «\u202fAppels d’offres par "
                  "e-mail\u202f»{z}.",
        "unsub": "Se désabonner", "privacy": "Protection des données", "imprint": "Mentions légales",
        "source": "Source\u202f: simap.ch (publications officielles de la Confédération, des cantons et des communes)",
        "titles": "Les titres apparaissent dans la langue de publication.", "asof": "Mis à jour le {d}",
        "pro_tag": "CHF 29 par mois", "pro_h": "Plus de cantons, plus de secteurs – et qui remporte les marchés",
        "pro_1": "Plus de cantons et de secteurs dans le même abonnement",
        "pro_2": "Chaque semaine, un rapport\u202f: qui a remporté les marchés dans vos cantons et vos secteurs",
        "pro_cta": "Découvrir Pro",
    },
    "it": {
        "alert": "Bandi via e-mail", "since": "Dal {d}", "since_v": "Dall’{d}",
        "n1": "1 nuovo bando", "nn": "{n} nuovi bandi", "h1": "Nuovo bando", "hn": "Nuovi bandi",
        "k1": "Cantone", "kn": "Cantoni", "b1": "Settore", "bn": "Settori",
        "all_k": "tutta la Svizzera", "all_b": "tutti i settori",
        "urgent": "{u} in scadenza nei prossimi 7 giorni", "next": "Prossima scadenza: {d}",
        "web": "Tutti i nuovi bandi sul sito",
        "more1": "{p} altro nuovo bando sul sito", "moren": "{p} altri nuovi bandi sul sito",
        "dl": "Termine d’inoltro", "buyer": "Ente pubblico", "corr": "Rettifica", "open": "Apri il bando",
        "why": "Questa e-mail arriva perché è stata confermata l’iscrizione gratuita a «Bandi via e-mail» di "
               "auftragsregister.ch per questa scelta: {sel}.",
        "why0": "Questa e-mail arriva perché è stata confermata l’iscrizione gratuita a «Bandi via e-mail» di "
                "auftragsregister.ch.",
        "change": "Per cambiare la scelta: annullare l’iscrizione con «Annulla l’iscrizione» e iscriversi di nuovo "
                  "con la nuova scelta nella {a}pagina «Bandi via e-mail»{z}.",
        "unsub": "Annulla l’iscrizione", "privacy": "Protezione dei dati", "imprint": "Note legali",
        "source": "Fonte: simap.ch (pubblicazioni ufficiali della Confederazione, dei Cantoni e dei Comuni)",
        "titles": "I titoli compaiono nella lingua in cui sono stati pubblicati.", "asof": "Aggiornato al {d}",
        "pro_tag": "CHF 29 al mese", "pro_h": "Più cantoni, più settori – e chi vince gli appalti",
        "pro_1": "Più cantoni e settori nella stessa iscrizione",
        "pro_2": "Ogni settimana un rapporto: chi ha vinto gli appalti nei cantoni e nei settori scelti",
        "pro_cta": "Scopri Pro",
    },
    "en": {
        "alert": "Tenders by email", "since": "Since {d}",
        "n1": "1 new tender", "nn": "{n} new tenders", "h1": "New tender", "hn": "New tenders",
        "k1": "Canton", "kn": "Cantons", "b1": "Sector", "bn": "Sectors",
        "all_k": "all of Switzerland", "all_b": "all sectors",
        "urgent": "{u} closing in the next 7 days", "next": "Next deadline: {d}",
        "web": "All new tenders on the website",
        "more1": "{p} more new tender on the website", "moren": "{p} more new tenders on the website",
        "dl": "Submission deadline", "buyer": "Public buyer", "corr": "Correction", "open": "View tender",
        "why": "You are receiving this email because you confirmed your free subscription to Tenders by email "
               "from auftragsregister.ch for this selection: {sel}.",
        "why0": "You are receiving this email because you confirmed your free subscription to Tenders by email "
                "from auftragsregister.ch.",
        "change": "To change your selection, unsubscribe with “Unsubscribe” below and subscribe again with the "
                  "new selection on the {a}Tenders by email page{z}.",
        "unsub": "Unsubscribe", "privacy": "Privacy", "imprint": "Legal notice",
        "source": "Source: simap.ch (official publications of the Confederation, cantons and communes)",
        "titles": "Titles are shown in the language in which they were published.", "asof": "Updated {d}",
        "pro_tag": "CHF 29 a month", "pro_h": "More cantons, more sectors – and who wins",
        "pro_1": "More cantons and sectors in the same subscription",
        "pro_2": "A weekly report: who won the contracts in your cantons and sectors",
        "pro_cta": "See Pro",
    },
}
# simap's API terms (§5) require this sentence, verbatim and in German, wherever its data is passed on: the
# site's footer always carried it, the e-mails since 13.10.2026. The only copy (invia_avvisi.py has none).
SIMAP_NOTICE = ("Dies ist keine amtliche Veröffentlichung. Massgebend sind die auf der Plattform "
                "www.simap.ch veröffentlichten Daten.")


# ---------------------------------------------------------------- small helpers
def esc(s) -> str:
    """HTML-escaped, and no brace left for Brevo's template engine to read as a tag."""
    return _html.escape(str(s if s is not None else ""), quote=True).replace("{", "&#123;").replace("}", "&#125;")


def plain(s: str) -> str:
    """For what leaves as plain text (subject, text part): no tag for Brevo's template engine, as esc() does for
    the HTML. A zero-width space splits {{ {% {# and their closers; the text reads the same."""
    return re.sub(r"(?<=[}%#])\}", "\u200b}", re.sub(r"\{(?=[{%#])", "{\u200b", str(s)))


def clip(s, n: int) -> str:
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def iso_day(raw) -> str:
    """'2026-10-23' from '2026-10-23T12:00:00+02:00' or '23.10.2026'; '' when it is not a date."""
    s = str(raw or "").strip()
    if _DAY.match(s[:10]):
        return s[:10]
    m = _DMY.match(s)
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else ""


def fdate(raw, lang: str) -> str:
    """23.10.2026 (de/fr/it) · 23 Oct 2026 (en), as formato.date() writes it."""
    d = iso_day(raw)
    if not d:
        return ""
    y, m, g = d.split("-")
    return f"{int(g)}{NBSP}{MON_EN[int(m) - 1]}{NBSP}{y}" if lang == "en" else f"{g}.{m}.{y}"


def fclock(raw, lang: str) -> str:
    """'12.00 Uhr' / '12 h 00' / '12:00', as formato.clock(); '' without a time or at 00:00."""
    s = str(raw or "")
    t = s[11:16] if len(s) >= 16 and s[10] == "T" else ""
    if len(t) != 5 or t[2] != ":" or t == "00:00":
        return ""
    if lang == "de":
        return f"{int(t[:2])}.{t[3:]}{NBSP}Uhr"
    if lang == "fr":
        return f"{int(t[:2])}{NNBSP}h{NNBSP}{t[3:]}"
    return t


def fdeadline(raw, lang: str) -> str:
    d, c = fdate(raw, lang), fclock(raw, lang)
    return f"{d}, {c}" if d and c else d


def days_left(raw, today: str):
    d = iso_day(raw)
    if not d or not today:
        return None
    return (datetime.date.fromisoformat(d) - datetime.date.fromisoformat(today)).days


def due(raw, today: str, lang: str):
    """The site's words for a deadline within 7 days ('läuft heute ab', 'läuft morgen ab', 'noch 3 Tage'),
    None for a later or unreadable one."""
    n = days_left(raw, today)
    if n is None or n > URGENT_DAYS or n < 0:
        return None
    if n == 0:
        return L.META["due_today_bare"][lang]
    if n == 1:
        return L.JS["due_tomorrow"][lang]
    return L.JS["due_days"][lang].format(n=n)


def picks(raw, trim: int = 0) -> list:
    """The chosen codes in their order; [] = all (the wildcard, as invia_avvisi._picks reads it)."""
    out = []
    for part in str(raw if raw is not None else "ALLE").split(","):
        v = part.strip().upper()
        if v in WILDCARD:
            if v:
                return []
            continue
        v = v[:trim] if trim else v
        if v not in out:
            out.append(v)
    return out


def selection(contact) -> tuple:
    """(cantons, divisions) of a Brevo contact; (None, None) without one."""
    if not contact:
        return None, None
    a = contact.get("attributes", {}) or {}
    return picks(a.get("KANTON")), picks(a.get("BRANCHE"), trim=2)


def kname(code: str, lang: str) -> str:
    return (CANTONS_DE if lang == "de" else L.CANTON_NAMES.get(lang, {})).get(code, code)


def dname(code2: str, lang: str, fallback="") -> str:
    return L.CPV_SHORT.get(lang, {}).get(code2) or str(fallback or "") or (f"CPV {code2}" if code2 else "")


def row_cantons(t: dict) -> list:
    try:
        ks = list(cantons_of(t)[0])
    except Exception:          # a strange record must not stop the e-mail
        ks = []
    return ks or ([str(t["canton"])] if t.get("canton") else [])


def where(lang: str, codes: list) -> str:
    """Where the tenders are, for the subject: 'im Kanton Zürich', 'in Zürich, Bern und 4 weiteren Kantonen'."""
    n = len(codes)
    if not n:
        return ""
    nm = [kname(c, lang) for c in codes[:3]]
    if lang == "fr":
        of = [L.canton_of(c, kname(c, "fr"), "fr") for c in codes[:3]]
        return ("dans le canton " + of[0] if n == 1 else
                f"dans les cantons {of[0]} et {of[1]}" if n == 2 else
                f"dans les cantons {of[0]}, {of[1]} et {of[2]}" if n == 3 else
                f"dans les cantons {of[0]}, {of[1]} et {n - 2} autres")
    if lang == "it":
        return (f"nel Canton {nm[0]}" if n == 1 else f"nei Cantoni {nm[0]} e {nm[1]}" if n == 2 else
                f"nei Cantoni {nm[0]}, {nm[1]} e {nm[2]}" if n == 3 else f"nei Cantoni {nm[0]}, {nm[1]} e altri {n - 2}")
    if lang == "en":
        return (f"in the canton of {nm[0]}" if n == 1 else f"in {nm[0]} and {nm[1]}" if n == 2 else
                f"in {nm[0]}, {nm[1]} and {nm[2]}" if n == 3 else f"in {nm[0]}, {nm[1]} and {n - 2} other cantons")
    return (f"im Kanton {nm[0]}" if n == 1 else f"in {nm[0]} und {nm[1]}" if n == 2 else
            f"in {nm[0]}, {nm[1]} und {nm[2]}" if n == 3 else f"in {nm[0]}, {nm[1]} und {n - 2} weiteren Kantonen")


def where_codes(rows: list, ks) -> list:
    """The cantons the rows were sent for (those of the selection, else each tender's first), most first."""
    cnt = {}
    for t in rows:
        rc = row_cantons(t)
        for k in ([k for k in rc if k in ks] if ks else []) or rc[:1]:
            cnt[k] = cnt.get(k, 0) + 1
    return sorted(cnt, key=lambda k: (-cnt[k], k))


def tender_url(lang: str, t: dict) -> str:
    pid = str(t.get("projectId") or "")
    return f"{SITE}/{lang}/auftrag/{pid if _PID.match(pid) else urllib.parse.quote(pid, safe='')}/"


def list_url(lang: str, ks, bs) -> str:
    """The site's list of open tenders, newest first; one canton or one Branche goes in as its filter
    (the list takes one of each: ?k=ZH&b=45&sort=neu)."""
    q = ([f"k={ks[0]}"] if ks and len(ks) == 1 else []) + ([f"b={bs[0]}"] if bs and len(bs) == 1 else [])
    return f"{SITE}/{lang}/ausschreibungen/?" + "&".join(q + ["sort=neu"])


def abo_url(lang: str, ks, bs) -> str:
    """The alert form, prefilled with the current selection (abo.js reads ?k=&b=, five of each)."""
    q = (["k=" + ",".join(ks[:5])] if ks else []) + (["b=" + ",".join(bs[:5])] if bs else [])
    return f"{SITE}/{lang}/ausschreibungen/abo/" + ("?" + "&".join(q) if q else "")


def _today(today) -> str:
    if isinstance(today, datetime.date):
        return today.isoformat()
    return iso_day(today) or datetime.date.today().isoformat()


def since_label(s: dict, since, lang: str) -> str:
    """'Neu seit 08.10.2026'; Italian elides before a day read with a vowel: 'Dall’08.10.2026', 'Dall’11…' (fix round
    3), in the band and, since 22.10.2026, in the text part too."""
    d = fdate(since, lang)
    return (s["since_v"] if "since_v" in s and d[:2] in ("08", "11") else s["since"]).format(d=d)


def asof(s: dict, today, lang: str) -> str:
    """'Aktualisiert am 23.10.2026'; Italian elides before a day read with a vowel ('Aggiornato all’08.10.2026')."""
    t = s["asof"].format(d=fdate(today, lang))
    return L.it_dates(t) if lang == "it" else t


def _list(names: list, more: int = 0) -> str:
    return " · ".join(names) + (f" +{more}" if more else "")


# ---------------------------------------------------------------- the parts of the e-mail
# No "}}", "%}" or "{%" anywhere: Brevo's template engine reads its own tags in htmlContent.
CSS_CORE = (  # Gmail-safe: classes, elements and @media only
    "body{margin:0!important;padding:0!important;width:100%!important;-webkit-text-size-adjust:100%;"
    "-ms-text-size-adjust:100%;}\ntable,td{border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt}\n"
    "h1,h2,p{mso-line-height-rule:exactly}\n.e{font-weight:700;letter-spacing:1.3px;text-transform:uppercase}\n"
    f".gl{{background-image:linear-gradient(100deg,{BRASS_LO} 0%,{BRASS} 22%,#f2d892 48%,#d4ae5c 74%,{BRASS} 100%)}}\n"
    f".rl{{background-image:linear-gradient(90deg,{BRASS_LO} 0%,#f2d892 45%,{BRASS} 70%,{BRASS_LO} 100%)}}\n"
    "@media (max-width:620px){.px{padding-left:16px!important;padding-right:16px!important}\n"
    ".cp{padding:14px 16px 16px!important}\n.hn{font-size:48px!important;line-height:50px!important}\n"
    ".hl{font-size:26px!important;line-height:30px!important}\n"
    ".go{clear:both;margin-top:0!important;padding-top:12px!important;text-align:left!important}\n"
    ".wm{font-size:17px!important;letter-spacing:.5px!important}\n}"
)
CSS_DARK = (  # Apple Mail (prefers-color-scheme), Outlook.com ([data-ogsc]/[data-ogsb]), iOS data detectors
    ":root{color-scheme:light dark;supported-color-schemes:light dark}\n"
    "a[x-apple-data-detectors]{color:inherit!important;text-decoration:none!important;font-size:inherit!important;"
    "font-family:inherit!important;font-weight:inherit!important;line-height:inherit!important}\n"
    "@media (prefers-color-scheme:dark){"
    f".bp{{background-color:{BLACK}!important}}\n"
    f".bc{{background-color:#0d0b08!important;border-color:#2f2c27!important;border-top-color:{BRASS}!important}}\n"
    f".ch{{background-color:#15110a!important}}\n.tx{{color:{IVORY}!important}}\n.tm{{color:{MUTED_D}!important}}\n"
    f".tb{{color:{GOLD}!important}}\n.ln{{color:{LINK_D}!important}}\n.cut{{border-right-color:{BLACK}!important}}\n"
    f".ob{{border-color:{GOLD}!important}}\n.rk{{background-color:#2f2c27!important}}\n"
    f".bk{{background-color:#0d0b08!important}}\n.pt{{background-color:{BRASS}!important;color:#0b0905!important}}\n}}\n"
    + "".join(f"[data-ogsb] .{c},[data-ogab] .{c},.{c}[data-ogsb],.{c}[data-ogab]{{background-color:{v}!important}}\n"
              for c, v in (("bp", BLACK), ("bc", "#0d0b08"), ("bk", "#0d0b08"), ("ch", "#15110a")))
    + "".join(f"[data-ogsc] .{c},.{c}[data-ogsc]{{color:{v}!important}}\n"
              for c, v in (("tx", IVORY), ("tm", MUTED_D), ("tb", GOLD), ("ln", LINK_D)))
)
CSS_SYS = (  # system fonts for the clients that read @media (not Outlook for Windows): Helvetica on Apple devices,
    # a condensed face where Impact is missing (iPhone: Helvetica Neue Condensed Bold; Android: Roboto Condensed)
    "@media screen{.ft td,.ft p,.ft a,.ft span,.ft h1,.ft h2{font-family:Helvetica,Arial,sans-serif!important}\n"
    ".ft .fd,.ft .fd a,.ft .fd span{font-family:'HelveticaNeue-CondensedBold',Impact,'Arial Narrow',"
    "'sans-serif-condensed',sans-serif!important}\n}"
)
CSS_FONTS = (  # Apple Mail and the WebKit clients; Gmail drops @font-face, Outlook never reads @media
    "@media screen{"
    f"@font-face{{font-family:'AR Gothic';font-weight:400;src:url({FONTS}lg.woff2) format('woff2');size-adjust:112%;}}\n"
    f"@font-face{{font-family:'Instrument Sans';font-weight:400;src:url({FONTS}is.woff2) format('woff2')}}\n"
    f"@font-face{{font-family:'Instrument Sans';font-weight:700;src:url({FONTS}is7.woff2) format('woff2')}}\n"
    ".ft td,.ft p,.ft a,.ft span,.ft h1,.ft h2{font-family:'Instrument Sans',Helvetica,Arial,sans-serif!important}\n"
    ".ft .fd,.ft .fd a,.ft .fd span{font-family:'AR Gothic','League Gothic','HelveticaNeue-CondensedBold',Impact,"
    "sans-serif!important}\n}"
)
TABLE = 'role="presentation" cellpadding="0" cellspacing="0" border="0"'


def _ghost(inner: str) -> str:
    """A 600-px column: fluid everywhere, fixed for Outlook for Windows (which ignores max-width)."""
    return (f'<!--[if mso]><table {TABLE} width="600" align="center"><tr><td><![endif]-->'
            f'<table {TABLE} width="100%" style="max-width:600px;margin:0 auto">{inner}</table>'
            '<!--[if mso]></td></tr></table><![endif]-->')


def _band(lang, s, total, since, ks, bs, rows, today, web) -> str:
    home = esc(f"{SITE}/{lang}/")
    eyebrow = [s["alert"]] + ([since_label(s, since, lang)] if fdate(since, lang) else [])
    sel = ""
    if ks is not None:
        kn = [kname(k, lang) for k in ks[:4]] or [s["all_k"]]
        bn = [dname(b, lang) for b in bs[:3]] or [s["all_b"]]
        lab = (f'<td valign="top" style="padding:3px 14px 6px 0;{FT};font-size:10px;line-height:16px;font-weight:700;'
               f'letter-spacing:1.4px;text-transform:uppercase;color:{GOLD};white-space:nowrap">')
        val = f'<td valign="top" style="padding:0 0 6px;{FT};font-size:14px;line-height:20px;color:{IVORY}">'
        sel = (f'<table {TABLE} style="margin:0 0 10px">'
               f'<tr>{lab}{s["k1"] if len(ks) == 1 else s["kn"]}</td>{val}{esc(_list(kn, max(0, len(ks) - 4)))}</td></tr>'
               f'<tr>{lab}{s["b1"] if len(bs) == 1 else s["bn"]}</td>{val}{esc(_list(bn, max(0, len(bs) - 3)))}</td></tr>'
               '</table>')
    u = sum(1 for t in rows if due(t.get("offerDeadline"), today, lang))
    if u:
        alert = (f'<p style="margin:0 0 10px;{FT};font-size:14px;line-height:20px;font-weight:700;color:{HOT}">'
                 f'▲{NBSP}{esc(s["urgent"].format(u=u))}</p>')
    else:
        nxt = min((iso_day(t.get("offerDeadline")) for t in rows if iso_day(t.get("offerDeadline"))), default="")
        alert = (f'<p style="margin:0 0 10px;{FT};font-size:14px;line-height:20px;color:{MUTED_D}">'
                 f'{esc(s["next"].format(d=fdate(nxt, lang)))}</p>') if nxt else ""
    inner = (
        f'<tr><td class="px" style="padding:24px 32px 26px;{FT};color:{BODY}">'
        f'<table {TABLE}><tr>'
        f'<td width="34" height="34" align="center" valign="middle" class="fd" style="width:34px;height:34px;'
        f'border:1px solid {FIELD};border-bottom:3px solid {BRASS};{FD};font-size:24px;line-height:32px;'
        f'mso-line-height-rule:exactly"><a href="{home}" style="color:{IVORY};text-decoration:none">A</a></td>'
        f'<td class="fd wm" style="padding-left:12px;{FD};font-size:20px;line-height:24px;letter-spacing:1px;'
        f'text-transform:uppercase"><a href="{home}" style="color:{IVORY};text-decoration:none">'
        f'{esc(L.T["site"][lang])}</a></td></tr></table>'
        f'<p style="margin:22px 0 8px;{FT};font-size:11px;line-height:16px;font-weight:700;letter-spacing:1.8px;'
        f'text-transform:uppercase;color:{GOLD}">{esc(" · ".join(eyebrow))}</p>'
        f'<h1 class="fd hl" style="margin:0 0 16px;{FD};font-size:30px;line-height:34px;font-weight:400;'
        f'mso-line-height-rule:at-least;text-transform:uppercase;color:{IVORY}">'
        f'<span class="hn" style="font-size:60px;line-height:62px;color:{GOLD}">{total}</span><br>'
        f'{esc(s["h1"] if total == 1 else s["hn"])}</h1>'
        f'{sel}{alert}'
        f'<p style="margin:0;{FT};font-size:14px;line-height:20px"><a href="{esc(web)}" style="color:{LINK_D};'
        f'text-decoration:underline">{esc(s["web"])}{NBSP}→</a></p>'
        '</td></tr>')
    return (f'<tr><td align="center" bgcolor="{BLACK}" style="background-color:{BLACK}">{_ghost(inner)}</td></tr>'
            f'<tr><td class="rl" height="3" bgcolor="{BRASS}" style="height:3px;font-size:0;line-height:3px;'
            f'mso-line-height-rule:exactly;background-color:{BRASS}">&nbsp;</td></tr>')


def _chip(lang, s, t, today) -> str:
    """The deadline: an outlined chip, or within 7 days a filled red one with ▲ and the site's words."""
    raw = t.get("offerDeadline")
    when = esc(fdeadline(raw, lang)) or "–"
    rel = due(raw, today, lang)
    big = f'margin:0;{FD};font-size:19px;line-height:23px'
    if rel:
        return (f'<table {TABLE} align="left"><tr><td bgcolor="{RED}" style="padding:7px 12px 8px;{FT}">'
                f'<p class="e" style="margin:0;font-size:10px;line-height:14px;color:#ffffff">▲{NBSP}{esc(rel)}</p>'
                f'<p class="fd" style="{big};color:#ffffff">{when}</p></td></tr></table>')
    return (f'<table {TABLE} align="left"><tr><td class="ch" bgcolor="{CHIP}" style="border:1px solid {BRASS};'
            f'padding:6px 11px 7px;{FT}"><p class="e tb" style="margin:0;font-size:10px;'
            f'line-height:14px;color:{BRASS_TX}">{esc(s["dl"])}</p><p class="fd tx" style="{big};color:{INK}">{when}</p>'
            '</td></tr></table>')


def _card(lang, s, t, today) -> str:
    """One tender: where and what (eyebrow), the title, the contracting authority, the deadline, the link."""
    url = esc(tender_url(lang, t))
    ks = row_cantons(t)
    place = kname(ks[0], lang) if len(ks) == 1 else ", ".join(ks[:4]) + (f" +{len(ks) - 4}" if len(ks) > 4 else "")
    div = dname(str(t.get("cpvCode") or "")[:2], lang, t.get("cpvLabel"))
    eyebrow = esc(" · ".join(x for x in (place, div) if x))
    if t.get("corrected"):
        eyebrow += (f'{NBSP} <span class="rk tx" style="background-color:{LINE};color:{INK};padding:1px 5px">'
                    f'{esc(s["corr"])}</span>')
    buyer = esc(clip(t.get("buyerName"), 140))
    who = (f'<p class="tm" style="margin:0 0 14px;font-size:14px;line-height:20px;color:{MUTED}"><span class="e tb" '
           f'style="font-size:10px;color:{BRASS_TX}">{esc(s["buyer"])}</span>{NBSP} {buyer}</p>') if buyer else ""
    return (
        f'<table {TABLE} width="100%" class="bc" bgcolor="{CARD}" style="border:1px solid {LINE};'
        f'border-top:3px solid {BRASS}"><tr><td class="cp" style="padding:16px 20px 18px;{FT}">'
        f'<p class="e tb" style="margin:0 0 6px;font-size:11px;line-height:16px;color:{BRASS_TX}">{eyebrow}</p>'
        f'<h2 style="margin:0 0 {6 if who else 14}px;{FT};font-size:17px;line-height:23px"><a class="tx" href="{url}" '
        f'style="color:{INK};text-decoration:none">{esc(clip(t.get("title"), 220))}</a></h2>{who}'
        f'{_chip(lang, s, t, today)}'
        f'<p class="e go" style="margin:26px 0 0;font-size:11px;line-height:16px;text-align:right"><a class="tb" '
        f'href="{url}" style="color:{BRASS_TX};text-decoration:none">{esc(s["open"])}{NBSP}→</a></p>'
        '</td></tr></table>')


def _button(label: str, href: str) -> str:
    """Brass, with the A2 cut corner where borders draw it (WebKit, Blink); Outlook gets the plain block."""
    return (f'<table {TABLE}><tr><td class="gl" bgcolor="{BRASS}" style="background-color:{BRASS};'
            f'mso-padding-alt:15px 20px 15px 24px">'
            f'<a href="{esc(href)}" style="display:block;padding:15px 20px 15px 24px;{FT};font-size:13px;'
            f'line-height:18px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;color:#0b0905;'
            f'text-decoration:none">{esc(label)}{NBSP}→</a></td>'
            f'<!--[if !mso]><!--><td width="12" valign="bottom" bgcolor="{BRASS}" style="width:12px;'
            f'background-color:{BRASS};vertical-align:bottom;font-size:0;line-height:0"><div class="cut" '
            f'style="width:0;height:0;border-top:12px solid {BRASS};border-right:12px solid {PAPER};font-size:0;'
            f'line-height:0"></div></td><!--<![endif]--></tr></table>')


def _more(s, more: int) -> str:
    """The tenders over the cap, counted in one line above the button to the site's list (never a 2nd e-mail)."""
    if more <= 0:
        return ""
    pre, post = s["more1" if more == 1 else "moren"].split("{p}")
    return (f'<p class="fd tx" style="margin:0 0 16px;{FD};font-size:24px;line-height:28px;text-transform:uppercase;'
            f'color:{INK}">{esc(pre)}<span class="tb" style="color:{BRASS_TX}">+{NBSP}{more}</span>{esc(post)}</p>')


def _pro(lang, s, pro) -> str:
    url = pro.get("url") if isinstance(pro, dict) else None
    url = url or f"{SITE}/{lang}/pro/"
    dot = f'<span style="color:{BRASS}">◆</span>{NBSP}{NBSP}'
    return (
        f'<tr><td class="px bp" bgcolor="{PAPER}" style="padding:0 32px 30px;background-color:{PAPER}">'
        f'<table {TABLE} width="100%" class="bk" bgcolor="{CARD}" style="border:1px solid {BRASS}"><tr>'
        f'<td class="cp tx" style="padding:20px 22px 22px;{FT};color:{INK}">'
        f'<p style="margin:0 0 10px;font-size:11px;line-height:18px;font-weight:700;letter-spacing:1.4px;'
        f'text-transform:uppercase"><span class="pt" style="background-color:{BLACK};color:{GOLD};padding:2px 7px">Pro</span>'
        f'{NBSP} <span class="tb" style="color:{BRASS_TX}">{esc(s["pro_tag"])}</span></p>'
        f'<p class="fd tx" style="margin:0 0 12px;{FD};font-size:24px;line-height:28px;text-transform:uppercase;'
        f'color:{INK}">{esc(s["pro_h"])}</p>'
        f'<p style="margin:0 0 6px 18px;text-indent:-18px;font-size:14px;line-height:20px">{dot}{esc(s["pro_1"])}</p>'
        f'<p style="margin:0 0 16px 18px;text-indent:-18px;font-size:14px;line-height:20px">{dot}{esc(s["pro_2"])}</p>'
        f'<table {TABLE}><tr><td class="ob" style="border:1px solid {INK};mso-padding-alt:10px 16px"><a class="tx" '
        f'href="{esc(url)}" '
        f'style="display:block;padding:10px 16px;font-size:12px;line-height:16px;font-weight:700;letter-spacing:1.4px;'
        f'text-transform:uppercase;color:{INK};text-decoration:none">{esc(s["pro_cta"])}{NBSP}→</a></td></tr></table>'
        '</td></tr></table></td></tr>')


def _footer(lang, s, ks, bs, today) -> str:
    if ks is not None:
        sel = (", ".join(kname(k, lang) for k in ks) or s["all_k"]) + " · " + (
            ", ".join(dname(b, lang) for b in bs) or s["all_b"])
        why = esc(s["why"].format(sel=sel))
    else:
        why = esc(s["why0"])
    a = (f'<a class="ln" href="{esc(abo_url(lang, ks or [], bs or []))}" style="color:{INK};'
         'text-decoration:underline">')
    pre, rest = s["change"].split("{a}")
    mid, post = rest.split("{z}")
    change = f"{esc(pre)}{a}{esc(mid)}</a>{esc(post)}"
    link = f'class="ln" style="color:{INK};text-decoration:underline"'
    simap = f'<a href="https://www.simap.ch" class="tm" style="color:{MUTED};text-decoration:underline">{{}}</a>'
    de = ' lang="de"' if lang != "de" else ""
    return (
        f'<tr><td class="px bp tm" bgcolor="{PAPER}" style="padding:4px 32px 40px;background-color:{PAPER};{FT};'
        f'font-size:12px;line-height:18px;color:{MUTED}">'
        f'<table {TABLE} width="100%"><tr><td class="rl" height="1" bgcolor="{BRASS}" style="height:1px;font-size:0;'
        f'line-height:1px;mso-line-height-rule:exactly;background-color:{BRASS}">&nbsp;</td></tr></table>'
        f'<p style="margin:16px 0 8px">{why}</p>'
        f'<p style="margin:0 0 12px">{change}</p>'
        f'<p style="margin:0 0 14px;font-size:13px;line-height:20px;font-weight:700">'
        f'<a href="{{{{ unsubscribe }}}}" {link}>{esc(s["unsub"])}</a> &nbsp;·&nbsp; '
        f'<a href="{esc(f"{SITE}/{lang}/datenschutz/")}" {link}>{esc(s["privacy"])}</a> &nbsp;·&nbsp; '
        f'<a href="{esc(f"{SITE}/{lang}/impressum/")}" {link}>{esc(s["imprint"])}</a></p>'
        f'<p style="margin:0 0 6px">{esc(s["source"]).replace("simap.ch", simap.format("simap.ch"), 1)}</p>'
        f'<p{de} style="margin:0 0 6px;font-size:11px;line-height:16px">'
        f'{esc(SIMAP_NOTICE).replace("www.simap.ch", simap.format("www.simap.ch"))}</p>'
        f'<p style="margin:0;font-size:11px;line-height:16px">{esc(s["titles"])} {esc(asof(s, today, lang))}'
        f' · <a href="{esc(f"{SITE}/{lang}/")}" {link}>auftragsregister.ch</a></p>'
        '</td></tr>')


def _preheader(lang, s, rows, today) -> str:
    u = sum(1 for t in rows if due(t.get("offerDeadline"), today, lang))
    if u:
        head = s["urgent"].format(u=u)
    else:
        nxt = min((iso_day(t.get("offerDeadline")) for t in rows if iso_day(t.get("offerDeadline"))), default="")
        head = s["next"].format(d=fdate(nxt, lang)) if nxt else ""
    titles = [clip(t.get("title"), 70) for t in rows[:2] if t.get("title")]
    return " · ".join([x for x in [head] if x] + titles)


def subject_of(lang: str, rows: list, ks) -> str:
    """'63 neue Ausschreibungen im Kanton Zürich': all the new tenders, also those counted and not shown."""
    s = S[lang]
    head = s["n1"] if len(rows) == 1 else s["nn"].format(n=len(rows))
    w = where(lang, where_codes(rows, ks))
    return plain(f"{head} {w}" if w else head)


def _shown(rows: list, cap) -> list:
    return rows if cap is None else rows[:max(0, int(cap))]


# ---------------------------------------------------------------- the e-mail
def fits(doc: str, budget: int = BUDGET, per_link: int = PER_LINK) -> bool:
    """The owner's budget: the HTML under 100 KB. Gmail clips at 102 KB and then hides the footer with the
    unsubscribe link; per_link reserves room for Brevo lengthening each link (click tracking). v3's split()
    reserved 200 B, which cut real French e-mails to 39 cards; 0 until a real e-mail shows how long Brevo's
    links are (with 200 B each, the real 40-card e-mails would be 96-100 KB: still under the clip)."""
    return len(doc.encode("utf-8")) + per_link * doc.count('href="') <= budget


def fit(lang, rows, since, contact=None, today=None, *, cap=CAP, budget=BUDGET, per_link=PER_LINK, pro=False) -> int:
    """How many cards the one e-mail of the day shows: cap, or fewer when cap cards would not fit() (very long
    titles). Never a second e-mail: the tenders left out are counted above the button to the site's list."""
    rows = [t for t in (rows or []) if isinstance(t, dict)]
    n = min(cap, len(rows))
    while n > 1:
        _s, doc = render(lang, rows, since, contact, today, cap=n, pro=pro)
        if fits(doc, budget, per_link):
            break
        n -= 1
    return n


def render(lang, rows, since, contact=None, today=None, *, cap=CAP, pro=False):
    """(subject, html) of the one e-mail of the day. rows: ALL the subscriber's new tenders, most urgent first;
    the first cap are shown as cards, the others counted above the button (fit() gives the cap that fits)."""
    lang = lang if lang in S else "de"
    s = S[lang]
    rows = [t for t in (rows or []) if isinstance(t, dict)]
    shown = _shown(rows, cap)
    total = len(rows)
    today = _today(today)
    ks, bs = selection(contact)
    subject = subject_of(lang, rows, ks)
    web = list_url(lang, ks, bs)
    pre = esc(_preheader(lang, s, rows, today)) + "&#847;&zwnj;&nbsp;" * 40
    gap = f'<p style="margin:0;font-size:14px;line-height:14px">&nbsp;</p>'
    cards = gap.join(_card(lang, s, t, today) for t in shown)
    body = (
        f'<tr><td class="px bp" bgcolor="{PAPER}" style="padding:22px 32px 6px;background-color:{PAPER}">{cards}</td></tr>'
        f'<tr><td class="px bp" bgcolor="{PAPER}" style="padding:20px 32px 30px;background-color:{PAPER}">'
        f'{_more(s, total - len(shown))}{_button(s["web"], web)}</td></tr>'
        + (_pro(lang, s, pro) if pro else "")
        + _footer(lang, s, ks, bs, today))
    doc = (
        '<!DOCTYPE html>'
        f'<html lang="{lang}" dir="ltr" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" '
        'xmlns:o="urn:schemas-microsoft-com:office:office"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="x-apple-disable-message-reformatting">'
        '<meta name="format-detection" content="telephone=no,date=no,address=no,email=no,url=no">'
        '<meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark">'
        f'<title>{esc(subject)}</title>'
        '<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch>'
        '</o:OfficeDocumentSettings></xml></noscript><![endif]-->'
        f'<style>{CSS_CORE}</style><style>{CSS_DARK}</style><style>{CSS_SYS}</style><style>{CSS_FONTS}</style></head>'
        f'<body class="bp" bgcolor="{PAPER}" style="margin:0;padding:0;background-color:{PAPER}">'
        f'<div style="display:none;font-size:1px;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;'
        f'mso-hide:all">{pre}</div>'
        f'<table {TABLE} width="100%" class="bp ft" bgcolor="{PAPER}" style="background-color:{PAPER}">'
        + _band(lang, s, total, since, ks, bs, rows, today, web)
        + f'<tr><td align="center" class="bp" bgcolor="{PAPER}" style="background-color:{PAPER}">{_ghost(body)}</td></tr>'
        '</table></body></html>')
    return subject, doc


def render_text(lang, rows, since, contact=None, today=None, *, cap=CAP, pro=False) -> str:
    """The plain-text part: what Outlook's "read as plain text" and the text-only readers show. Same rows and
    cap as render(); nothing from the data can be read as a Brevo tag, only {{ unsubscribe }} is one."""
    lang = lang if lang in S else "de"
    s = S[lang]
    rows = [t for t in (rows or []) if isinstance(t, dict)]
    shown = _shown(rows, cap)
    today = _today(today)
    ks, bs = selection(contact)
    out = [subject_of(lang, rows, ks), ""]
    head = [s["alert"]] + ([since_label(s, since, lang)] if fdate(since, lang) else [])
    out.append(" · ".join(head))
    if ks is not None:
        out.append(f'{s["k1"] if len(ks) == 1 else s["kn"]}: ' + (", ".join(kname(k, lang) for k in ks) or s["all_k"]))
        out.append(f'{s["b1"] if len(bs) == 1 else s["bn"]}: ' + ("; ".join(dname(b, lang) for b in bs) or s["all_b"]))
    out.append("")
    for t in shown:
        ks_t = row_cantons(t)
        place = kname(ks_t[0], lang) if len(ks_t) == 1 else ", ".join(ks_t)
        rel = due(t.get("offerDeadline"), today, lang)
        dl = fdeadline(t.get("offerDeadline"), lang)
        out += [clip(t.get("title"), 220),
                f'{s["buyer"]}: {clip(t.get("buyerName"), 140)}',
                " · ".join(x for x in (place, dname(str(t.get("cpvCode") or "")[:2], lang, t.get("cpvLabel")),
                                       s["corr"] if t.get("corrected") else "") if x),
                (f"▲ {rel} – " if rel else "") + f'{s["dl"]}: {dl}',
                tender_url(lang, t), ""]
    more = len(rows) - len(shown)
    if more > 0:
        out.append(s["more1" if more == 1 else "moren"].replace("{p}", f"+ {more}"))
    out += [f'{s["web"]}: {list_url(lang, ks, bs)}', ""]
    if pro:
        url = (pro.get("url") if isinstance(pro, dict) else None) or f"{SITE}/{lang}/pro/"
        out += [f'PRO · {s["pro_tag"]}: {s["pro_h"]}', f'- {s["pro_1"]}', f'- {s["pro_2"]}', url, ""]
    sel = ((", ".join(kname(k, lang) for k in ks) or s["all_k"]) + " · " + (
        ", ".join(dname(b, lang) for b in bs) or s["all_b"])) if ks is not None else None
    out += ["—", s["why"].format(sel=sel) if sel else s["why0"],
            s["change"].replace("{a}", "").replace("{z}", "") + " " + abo_url(lang, ks or [], bs or []),
            f'{s["unsub"]}: ']
    tail = [f'{s["privacy"]}: {SITE}/{lang}/datenschutz/', f'{s["imprint"]}: {SITE}/{lang}/impressum/',
            s["source"], SIMAP_NOTICE, asof(s, today, lang)]
    text = plain("\n".join(out)) + "{{ unsubscribe }}\n" + plain("\n".join(tail))
    return text.replace(NBSP, " ").replace(NNBSP, " ")
