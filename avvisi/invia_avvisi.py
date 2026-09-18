#!/usr/bin/env python3
"""Avvisi bandi: ogni mattina, dopo la pubblicazione del sito, manda a ogni iscritto i nuovi bandi
che corrispondono al suo cantone e settore. Tutto automatico: iscrizione, conferma (double opt-in) e
disiscrizione sono di Brevo; qui si legge la lista iscritti (API) e si inviano le e-mail (API transazionale).

Prerequisiti (una volta, dall'utente): account Brevo gratuito; attributi contatto KANTON (testo, es. "ZH,BE" o "ALLE")
e BRANCHE (testo, es. "45,71" = prime due cifre CPV, o "ALLE"); lista "Avvisi bandi" con double opt-in;
API key in ~/.brevo_api_key (solo permessi contacts + transactional). Nessun server: gira sul Mac via launchd
(ch.auftragsregister.avvisi, 08:50) dopo aggiorna.py (08:20).

Stato: ~/auftragsregister/avvisi/stato.json = ultima data di pubblicazione inviata per contatto, cosi' un giorno
saltato (Mac spento) non perde bandi: al prossimo giro manda tutto cio' che e' uscito dall'ultimo invio.
"""
from __future__ import annotations
import json, pathlib, sys, datetime, urllib.request, urllib.error, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEYFILE = pathlib.Path.home() / ".brevo_api_key"
STATE = ROOT / "avvisi" / "stato.json"
LOG = ROOT / "avvisi" / "avvisi.log"
SITE = "https://auftragsregister.ch"
SENDER = {"name": "auftragsregister.ch", "email": "abo@auftragsregister.ch"}
MAX_PER_MAIL = 40

def say(msg: str) -> None:
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {msg}"
    print(line); LOG.open("a").write(line + "\n")

def api(method: str, path: str, body=None):
    key = KEYFILE.read_text().strip()
    req = urllib.request.Request("https://api.brevo.com/v3" + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"api-key": key, "Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "{}")

def contacts() -> list[dict]:
    """Tutti i contatti confermati (double opt-in fatto = presenti nella lista) con i loro attributi."""
    out, offset = [], 0
    while True:
        d = api("GET", f"/contacts?limit=500&offset={offset}")
        page = d.get("contacts", [])
        out += [c for c in page if not c.get("emailBlacklisted")]
        if len(page) < 500: return out
        offset += 500

def wants(contact: dict, tender: dict) -> bool:
    a = contact.get("attributes", {}) or {}
    kant = [x.strip().upper() for x in str(a.get("KANTON") or "ALLE").split(",") if x.strip()]
    bran = [x.strip()[:2] for x in str(a.get("BRANCHE") or "ALLE").split(",") if x.strip()]
    ok_k = "ALLE" in kant or (tender.get("canton") or "").upper() in kant
    ok_b = "ALLE" in bran or str(tender.get("cpvCode") or "")[:2] in bran
    return ok_k and ok_b

def lang_of(contact: dict) -> str:
    l = str((contact.get("attributes", {}) or {}).get("SPRACHE") or "de").lower()[:2]
    return l if l in ("de", "fr", "it", "en") else "de"

T = {
    "de": ("Neue Ausschreibungen für Sie", "{n} neue Ausschreibungen seit {since}", "Eingabefrist", "Abmelden: Link am Ende der E-Mail.", "Keine neuen Ausschreibungen — es gibt heute nichts zu tun."),
    "fr": ("Nouveaux appels d'offres pour vous", "{n} nouveaux appels d'offres depuis le {since}", "Délai", "Désabonnement : lien en bas de l'e-mail.", "Pas de nouvel appel d'offres — rien à faire aujourd'hui."),
    "it": ("Nuovi bandi per voi", "{n} nuovi bandi dal {since}", "Termine", "Disiscrizione: link in fondo all'e-mail.", "Nessun nuovo bando — oggi niente da fare."),
    "en": ("New tenders for you", "{n} new tenders since {since}", "Deadline", "Unsubscribe: link at the bottom.", "No new tenders — nothing to do today."),
}

def mail_html(lang: str, rows: list[dict], since: str) -> tuple[str, str]:
    subj, head, dl, foot, _ = T[lang]
    items = []
    for t in sorted(rows, key=lambda x: x.get("offerDeadline") or "9999")[:MAX_PER_MAIL]:
        url = f"{SITE}/{lang}/auftrag/{t.get('projectId')}/"
        items.append(f'<li style="margin:0 0 10px"><a href="{url}">{html.escape(t.get("title") or "")}</a><br>'
                     f'<span style="color:#555">{html.escape(t.get("buyerName") or "")} · {html.escape(t.get("canton") or "")} · '
                     f'{dl} {html.escape((t.get("offerDeadline") or "")[:10])}</span></li>')
    more = f'<p><a href="{SITE}/{lang}/ausschreibungen/">…</a></p>' if len(rows) > MAX_PER_MAIL else ""
    body = (f'<p>{head.format(n=len(rows), since=since)}</p><ul style="padding-left:18px">{"".join(items)}</ul>{more}'
            f'<p style="color:#777;font-size:12px">auftragsregister.ch — Quelle: simap.ch. {foot}</p>')
    return f"{subj} ({len(rows)})", body

def main() -> int:
    if not KEYFILE.exists():
        say("nessuna API key Brevo (~/.brevo_api_key): invio saltato"); return 0
    opens = json.loads((ROOT / "dati" / "gare_aperte.json").read_text())
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    today = datetime.date.today().isoformat()
    sent = skipped = 0
    for c in contacts():
        email = c.get("email");
        if not email: continue
        since = state.get(email) or (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        rows = [t for t in opens if (t.get("publicationDate") or "")[:10] > since and wants(c, t)]
        if not rows:
            skipped += 1; state[email] = today; continue
        subj, body = mail_html(lang_of(c), rows, since)
        try:
            api("POST", "/smtp/email", {"sender": SENDER, "to": [{"email": email}], "subject": subj, "htmlContent": body})
            sent += 1; state[email] = today
        except urllib.error.HTTPError as e:
            say(f"errore invio a {email}: HTTP {e.code} {e.read().decode()[:200]}")
    STATE.write_text(json.dumps(state, indent=1))
    say(f"inviati {sent}, senza novita' {skipped}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
