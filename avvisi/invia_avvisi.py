#!/usr/bin/env python3
"""Avvisi bandi: dopo ogni pubblicazione del sito manda a ogni iscritto i nuovi bandi che corrispondono
al suo cantone e settore. Iscrizione, conferma (double opt-in) e disiscrizione sono di Brevo; qui si legge
la lista iscritti (API), si inviano le e-mail (API transazionale) e si cancellano i dati di chi se ne va.

Quando gira: chiamato da aggiorna.py subito dopo una pubblicazione verificata, piu' un giro di riserva via
launchd (ch.auftragsregister.avvisi, 12:30). Legge SOLO dati/gare_pubblicate.json, la copia che aggiorna.py
scrive quando le pagine sono davvero su GitHub, e prima di inviare aspetta che GitHub Pages le serva: un link
in una e-mail non punta mai a una pagina che non esiste ancora. Due giri lo stesso giorno sono innocui.

Prerequisiti (una volta, dall'utente): account Brevo gratuito; attributi contatto KANTON / BRANCHE / SPRACHE;
lista "Avvisi bandi" (id 3) con double opt-in; API key in ~/.brevo_api_key (contacts + transactional).

Stato: avvisi/stato.json (MAI nel repo pubblico: contiene indirizzi; .gitignore copre avvisi/stato.json*) =
per contatto {"floor", "last", "sent": {id pubblicazione | "P:"+id progetto: data}, "gone"}. Un bando e' nuovo
se ne' la pubblicazione ne' il progetto sono gia' stati inviati a quel contatto, e' pubblicato da non piu' di
LOOKBACK_DAYS rispetto al dato piu' recente, non e' scaduto, ha la sua pagina sul sito e corrisponde ai
filtri. Giorni saltati, nightly falliti, bandi indicizzati in ritardo e invii falliti non fanno perdere nulla,
e nulla parte due volte (una rettifica di simap con un nuovo id pubblicazione non viene riannunciata).

Disiscrizioni: chi usa il link {{ unsubscribe }} finisce nella lista dei bloccati di Brevo. Qui lo si toglie
dalla lista 3 e se ne svuotano le scelte, ma il contatto e il blocco RESTANO: Brevo sconsiglia di cancellare i
contatti bloccati (la cancellazione fa perdere il blocco) e sbloccare chi si e' disiscritto esplicitamente e'
illecito. Nessuno sblocco automatico, mai. Rimbalzi e blocchi amministrativi: nessun invio, niente altro.

Storia: fino al 24.09.2026 lo stato era "la data di oggi" e il giro fisso delle 08:50 partiva di solito prima
che il nightly (08:20 -> fra le 09:00 e le 12:00) scrivesse i bandi del giorno; il giorno dopo il filtro "piu'
nuovo di ieri" scartava proprio quelli, quindi quasi nessun bando sarebbe mai arrivato. Trovato prima del primo
iscritto vero.
"""
from __future__ import annotations
import datetime, fcntl, html, json, os, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEYFILE = pathlib.Path.home() / ".brevo_api_key"
STATE = ROOT / "avvisi" / "stato.json"
LOG = ROOT / "avvisi" / "avvisi.log"
LOCK = ROOT / "avvisi" / "avvisi.lock"
DATA = ROOT / "dati" / "gare_pubblicate.json"   # scritto da aggiorna.py solo dopo una pubblicazione verificata
DOCS = ROOT / "docs"
SITE = "https://auftragsregister.ch"
SENDER = {"name": "auftragsregister.ch", "email": "abo@auftragsregister.ch"}
MAX_PER_MAIL = 100   # righe per e-mail; oltre si mandano piu' e-mail (100 righe ~45 KB, sotto il taglio di Gmail)
LOOKBACK_DAYS = 14   # un bando pubblicato fino a 14 giorni prima del dato piu' recente conta ancora come nuovo
KEEP_SENT_DAYS = 45  # gli id inviati si ricordano 45 giorni
LIVE_WAIT_S = 480    # attesa massima perche' GitHub Pages serva le pagine appena pubblicate
LOCK_WAIT_S = 900    # se un altro giro sta inviando, aspettarlo invece di saltare il giorno
GONE_GRACE_DAYS = 7 # chi sparisce dalla lista senza blocco (intoppo di Brevo?) viene purgato dopo 7 giorni
HOLD_DAYS = 7       # un disiscritto modificato dopo il blocco (forse reiscritto) resta in attesa 7 giorni dalla modifica
RESUB_MARGIN_MIN = 10  # una modifica fino a 10 minuti dopo il blocco e' la disiscrizione stessa
LEAVE = {"unsubscribedViaEmail", "unsubscribedViaMA", "unsubscribedViaApi", "contactFlaggedAsSpam", "adminBlocked"}
_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_PID = re.compile(r"^[A-Za-z0-9-]{1,80}$")


def mask(email: str) -> str:
    """Le righe di log sopravvivono a ogni disiscrizione: niente indirizzi interi."""
    local, _, dom = (email or "").partition("@")
    if not dom:
        return "***"
    name, _, tld = dom.rpartition(".")
    return f"{local[:1]}***@{name[:1]}***.{tld}" if name else f"{local[:1]}***@***"


def say(msg: str) -> None:
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {msg}"
    print(line)
    with LOG.open("a") as f:
        f.write(line + "\n")


def api(method: str, path: str, body=None):
    key = KEYFILE.read_text().strip()
    req = urllib.request.Request("https://api.brevo.com/v3" + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"api-key": key, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "auftragsregister-avvisi/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "{}")

LIST_ID = 3   # lista Brevo "Avvisi bandi" (solo chi ha confermato il double opt-in ci entra)


def contacts() -> list:
    """Tutti i contatti della lista avvisi, compresi quelli in blacklist (li smista main())."""
    out, offset = [], 0
    while True:
        d = api("GET", f"/contacts/lists/{LIST_ID}/contacts?limit=500&offset={offset}")
        page = d.get("contacts", []) or []
        out += page
        if len(page) < 500:
            return out
        offset += 500


_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


def blocked() -> dict:
    """email -> (blockedAt, motivo) degli indirizzi che Brevo blocca per le e-mail transazionali.

    Il link {{ unsubscribe }} dei nostri avvisi finisce QUI (motivo unsubscribedViaEmail): di norma non
    toglie il contatto dalla lista 3 e non imposta emailBlacklisted, quindi senza questo controllo il
    mittente teneva i dati di chi se n'era andato e continuava a provare a scrivergli. Qui finiscono anche
    rimbalzi definitivi e segnalazioni di spam.
    """
    out, offset = {}, 0
    snd = urllib.parse.quote(SENDER["email"], safe="")
    while True:
        d = api("GET", f"/smtp/blockedContacts?limit=100&offset={offset}&senders={snd}")
        page = d.get("contacts", []) or []
        for c in page:
            e = (c.get("email") or "").strip().lower()
            if not e or (c.get("senderEmail") or SENDER["email"]).lower() != SENDER["email"]:
                continue
            row = (str(c.get("blockedAt") or ""), str((c.get("reason") or {}).get("code") or ""))
            old = out.get(e)
            if old is None or (when(row[0]) or _EPOCH) > (when(old[0]) or _EPOCH):
                out[e] = row
        if len(page) < 100:
            return out
        offset += 100


def when(ts):
    """Un timestamp di Brevo come datetime con fuso, oppure None."""
    t = str(ts or "").strip().replace("Z", "+00:00")
    if not t:
        return None
    t = re.sub(r"\.(\d+)", lambda m: "." + (m.group(1) + "000000")[:6], t)  # 3.9 vuole 6 cifre
    try:
        d = datetime.datetime.fromisoformat(t)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)


def leave(email: str) -> bool:
    """Chi se n'e' andato: fuori dalla lista 3 e scelte svuotate. Il contatto e il blocco restano a Brevo,
    che serve proprio a garantire che non riceva piu' nulla (cancellarlo farebbe perdere il blocco)."""
    try:
        api("PUT", "/contacts/" + urllib.parse.quote(email, safe=""),
            {"unlinkListIds": [LIST_ID], "attributes": {"KANTON": "", "BRANCHE": "", "SPRACHE": ""}})
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return True
        say(f"ATTENZIONE uscita dalla lista di {mask(email)} fallita: HTTP {e.code}")
    except (urllib.error.URLError, OSError) as e:
        say(f"ATTENZIONE uscita dalla lista di {mask(email)} fallita: {type(e).__name__}")
    return False


WILDCARD = {"ALLE", "ALL", "TOUS", "TUTTI", "*", ""}


def _picks(raw, trim: int = 0) -> set:
    """Chosen values, upper case, with the wildcard recognised BEFORE any trimming.

    The sector list used to be built as x.strip()[:2], which turned the wildcard "ALLE"
    into "AL": the test for "ALLE" could then never be true, so every contact who left
    the sectors unchosen — the default on the form — matched nothing and would have got
    no e-mail, ever. Found 22.09.2026, before anyone but the test address had signed up.
    """
    out = set()
    for part in str(raw or "ALLE").split(","):
        v = part.strip().upper()
        if not v:
            continue
        out.add(v if v in WILDCARD else (v[:trim] if trim else v))
    return out or {"ALLE"}


def wants(contact: dict, tender: dict) -> bool:
    a = contact.get("attributes", {}) or {}
    kant = _picks(a.get("KANTON"))
    bran = _picks(a.get("BRANCHE"), trim=2)
    ok_k = bool(kant & WILDCARD) or str(tender.get("canton") or "").upper() in kant
    ok_b = bool(bran & WILDCARD) or str(tender.get("cpvCode") or "")[:2] in bran
    return ok_k and ok_b

def lang_of(contact: dict) -> str:
    l = str((contact.get("attributes", {}) or {}).get("SPRACHE") or "de").lower()[:2]
    return l if l in ("de", "fr", "it", "en") else "de"

CORR = {"de": "Berichtigung", "fr": "rectificatif", "it": "rettifica", "en": "correction"}
T = {
    "de": ("Neue Ausschreibungen für Sie", "{n} neue Ausschreibungen seit {since}", "Eingabefrist", "Abmelden", "Keine neuen Ausschreibungen — es gibt heute nichts zu tun."),
    "fr": ("Nouveaux appels d'offres pour vous", "{n} nouveaux appels d'offres depuis le {since}", "Délai", "Se désabonner", "Pas de nouvel appel d'offres — rien à faire aujourd'hui."),
    "it": ("Nuovi bandi per voi", "{n} nuovi bandi dal {since}", "Termine", "Cancellarsi", "Nessun nuovo bando — oggi niente da fare."),
    "en": ("New tenders for you", "{n} new tenders since {since}", "Deadline", "Unsubscribe", "No new tenders — nothing to do today."),
}
FOOT = {"de": ("Quelle", "Datenschutz"), "fr": ("Source", "Protection des données"),
        "it": ("Fonte", "Protezione dei dati"), "en": ("Source", "Privacy")}



def mail_html(lang: str, rows: list, since: str, total: int = 0, part: int = 1, parts: int = 1):
    """Mostra TUTTE le righe ricevute: e' il chiamante che divide in parti da MAX_PER_MAIL."""
    subj, head, dl, foot, _ = T[lang]
    total = total or len(rows)
    items = []
    for t in rows:
        url = f"{SITE}/{lang}/auftrag/{t.get('projectId')}/"
        items.append(f'<li style="margin:0 0 10px"><a href="{url}">{html.escape(str(t.get("title") or ""))}</a><br>'
                     f'<span style="color:#555">{html.escape(str(t.get("buyerName") or ""))} · '
                     f'{html.escape(str(t.get("canton") or ""))} · '
                     f'{dl} {html.escape(str(t.get("offerDeadline") or "")[:10])}'
                     + (f' · {CORR[lang]}' if t.get("corrected") else "") + '</span></li>')
    tag = f" ({part}/{parts})" if parts > 1 else ""
    body = (f'<p>{head.format(n=total, since=since)}{tag}</p><ul style="padding-left:18px">{"".join(items)}</ul>'
            f'<p style="color:#777;font-size:12px">auftragsregister.ch — {FOOT[lang][0]}: simap.ch · '
            f'<a href="{{{{ unsubscribe }}}}" style="color:#777">{foot}</a> · '
            f'<a href="{SITE}/{lang}/datenschutz/" style="color:#777">{FOOT[lang][1]}</a></p>')
    return f"{subj} ({total}){tag}", body


def pub_day(t) -> str:
    d = str((t or {}).get("publicationDate") or "")[:10]
    return d if _DAY.match(d) else ""


def keys_of(t: dict) -> list:
    """Le identita' di un bando: la pubblicazione e il progetto (una rettifica ha un nuovo id pubblicazione)."""
    ks = []
    if t.get("publicationId"):
        ks.append(str(t["publicationId"]))
    if t.get("projectId"):
        ks.append("P:" + str(t["projectId"]))
    return ks


def expired(t: dict, today: str) -> bool:
    raw = str(t.get("offerDeadline") or "").strip()
    d = raw[:10]
    if not _DAY.match(d):
        m = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})", raw)   # 15.12.2026
        if not m:
            return False          # scadenza illeggibile: meglio annunciarlo che perderlo
        d = f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return d < today


def has_page(pid, lang: str) -> bool:
    pid = str(pid or "")
    return bool(_PID.match(pid)) and (DOCS / lang / "auftrag" / pid / "index.html").exists()


def day(iso: str, delta: int = 0) -> str:
    return (datetime.date.fromisoformat(iso) + datetime.timedelta(days=delta)).isoformat()


def contact_state(raw, hw: str) -> dict:
    """Lo stato di un contatto, anche dal vecchio formato (una data) o da una voce rovinata."""
    try:
        if isinstance(raw, dict) and raw.get("floor"):
            floor = str(raw["floor"])[:10]; day(floor)
            sent = raw.get("sent") if isinstance(raw.get("sent"), dict) else {}
            sent = {str(k): str(v)[:10] for k, v in sent.items() if _DAY.match(str(v)[:10])}
            last = str(raw.get("last"))[:10] if raw.get("last") else None
            return {"floor": floor, "last": last if last and _DAY.match(last) else None,
                    "sent": sent, "gone": raw.get("gone")}
        if isinstance(raw, str) and _DAY.match(raw[:10]):
            d = day(raw[:10], -1)   # il vecchio formato salvava "oggi" su dati di ieri
            return {"floor": d, "last": d, "sent": {}, "gone": None}
    except (ValueError, TypeError):
        pass
    return {"floor": hw, "last": None, "sent": {}, "gone": None}   # nuovo: parte dal giorno piu' recente


def select(contact: dict, rows_all: list, st: dict, hw: str, today: str, lang: str) -> list:
    floor = max(st["floor"], day(hw, -LOOKBACK_DAYS))
    out, seen = [], set()
    for t in rows_all:
        ks = keys_of(t); d = pub_day(t)
        if (not ks or not d or d < floor or d > today or any(k in st["sent"] or k in seen for k in ks)
                or expired(t, today) or not has_page(t.get("projectId"), lang) or not wants(contact, t)):
            continue
        seen.update(ks); out.append(t)
    out.sort(key=lambda x: (str(x.get("offerDeadline") or "9999"), pub_day(x)))
    return out


def load_state() -> dict:
    if not STATE.exists():
        return {}
    try:
        s = json.loads(STATE.read_text())
        if isinstance(s, dict):
            return s
        raise ValueError("non e' un dizionario")
    except (ValueError, OSError) as e:
        # uno stato rovinato non deve zittire gli avvisi per sempre, ne' restare in giro con indirizzi dentro
        STATE.unlink()
        say(f"ATTENZIONE stato illeggibile ({type(e).__name__}): cancellato, si riparte da zero")
        return {}


def save_state(state: dict) -> None:
    tmp = STATE.with_suffix(".json.tmp")
    try:
        tmp.write_text(json.dumps(state, indent=1, sort_keys=True))
        os.replace(tmp, STATE)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


def live(url: str) -> bool:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "auftragsregister-avvisi/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


def wait_live(plan: list) -> bool:
    """Aspetta che GitHub Pages serva la pagina del bando piu' recente da inviare (deploy 1-3 minuti)."""
    rows = [(pub_day(t), lang, str(t.get("projectId"))) for _e, _c, _s, lang, rs in plan for t in rs]
    if not rows:
        return True
    _d, lang, pid = max(rows)
    url = f"{SITE}/{lang}/auftrag/{pid}/"
    deadline = time.time() + LIVE_WAIT_S
    while True:
        if live(url):
            return True
        if time.time() >= deadline:
            return False
        time.sleep(20)


def only_live(plan: list) -> list:
    """Una passata su ogni pagina da linkare: una riga la cui pagina non e' ancora online resta non
    inviata e non segnata, e parte al giro successivo (un bando indicizzato tardi e' in un altro deploy)."""
    ok = {}
    out = []
    for email, c, st, lang, rows in plan:
        keep = []
        for t in rows:
            url = f"{SITE}/{lang}/auftrag/{t.get('projectId')}/"
            if url not in ok:
                ok[url] = live(url)
            if ok[url]:
                keep.append(t)
        out.append((email, c, st, lang, keep))
    return out


def main() -> int:
    if not KEYFILE.exists():
        say("nessuna API key Brevo (~/.brevo_api_key): invio saltato"); return 0
    lock = LOCK.open("w")
    waited = time.time() + LOCK_WAIT_S
    while True:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except OSError:
            if time.time() >= waited:
                say("ATTENZIONE un altro invio e' in corso da oltre 15 minuti: salto"); return 0
            time.sleep(15)
    if not DATA.exists():
        say("nessun dato pubblicato (dati/gare_pubblicate.json): invio saltato"); return 0
    try:
        rows_all = json.loads(DATA.read_text())
    except (ValueError, OSError):
        say("ATTENZIONE dati pubblicati illeggibili: invio saltato"); return 0
    rows_all = [t for t in (rows_all if isinstance(rows_all, list) else []) if isinstance(t, dict)]
    today = datetime.date.today().isoformat()
    days = [d for d in (pub_day(t) for t in rows_all) if d and d <= today]
    if not days:
        say("nessun bando nei dati: invio saltato"); return 0
    hw = max(days)                     # il giorno piu' recente nei dati (futuri esclusi)
    age_h = (time.time() - DATA.stat().st_mtime) / 3600
    if age_h > 36:
        say(f"ATTENZIONE dati pubblicati fermi da {age_h:.0f} ore (dati fino al {hw}): il nightly ha pubblicato?")

    state = load_state()
    people = contacts()                # se Brevo non risponde si ferma qui, stato intatto
    blk = blocked()
    work = dict(state)

    now = datetime.datetime.now(datetime.timezone.utc)
    active, leaving, held, seen = [], [], [], set()
    for c in people:
        email = (c.get("email") or "").strip().lower()
        if not email or email in seen:
            continue
        seen.add(email)
        if c.get("emailBlacklisted"):
            leaving.append(email)
            continue
        b = blk.get(email)
        if b is None:
            active.append((email, c))
            continue
        bt, reason = when(b[0]), b[1]
        mod = when(c.get("modifiedAt"))
        if reason in LEAVE:
            resub = bool(bt and mod and mod > bt + datetime.timedelta(minutes=RESUB_MARGIN_MIN))
            if resub and now - mod < datetime.timedelta(days=HOLD_DAYS):
                left = HOLD_DAYS - (now - mod).days
                say(f"ATTENZIONE {mask(email)} disiscritto ma modificato dopo il blocco: forse si e' reiscritto. "
                    f"Nessun invio; se confermato, sbloccarlo a mano in Brevo entro {left} giorni")
                held.append(email)
            else:
                if resub:
                    say(f"ATTENZIONE {mask(email)}: reiscrizione non sbloccata entro {HOLD_DAYS} giorni, tolto dalla lista")
                leaving.append(email)
        else:
            say(f"{mask(email)} bloccato da Brevo ({reason or '?'}): nessun invio, contatto tenuto")
            held.append(email)

    keep_from = day(hw, -KEEP_SENT_DAYS)   # la promessa dei 45 giorni vale anche per i contatti in attesa
    for email in held:
        if email in work:
            st = contact_state(work[email], hw)
            st["sent"] = {k: d for k, d in st["sent"].items() if d >= keep_from}
            work[email] = st

    # chi se n'e' andato: fuori dalla lista, scelte svuotate, via i nostri dati (il blocco resta a Brevo)
    gone_now = 0
    for email in leaving:
        if leave(email):
            work.pop(email, None); gone_now += 1
    # chi manca dalla lista senza blocco (disiscritto altrove, o un intoppo di Brevo): via dopo GONE_GRACE_DAYS
    present = {e for e, _c in active} | set(leaving) | set(held)
    for email in list(work):
        if email in present:
            continue
        st = contact_state(work[email], hw)
        if st.get("gone") and day(st["gone"], GONE_GRACE_DAYS) <= today:
            work.pop(email); gone_now += 1
        else:
            st["gone"] = st.get("gone") or today
            work[email] = st

    plan = []
    for email, c in active:
        st = contact_state(work.get(email), hw)
        st["gone"] = None
        lang = lang_of(c)
        # una rettifica tardiva tiene viva la memoria del progetto: non si riannuncia dopo 45 giorni
        for t in rows_all:
            pk = "P:" + str(t.get("projectId") or "")
            if pk in st["sent"] and pub_day(t) > st["sent"][pk]:
                st["sent"][pk] = pub_day(t)
        try:
            rows = select(c, rows_all, st, hw, today, lang)
        except Exception as e:     # una riga strana non deve fermare tutti
            say(f"ATTENZIONE selezione per {mask(email)}: {type(e).__name__}"); rows = []
        work[email] = st
        plan.append((email, c, st, lang, rows))

    if not wait_live(plan):
        save_state(work)
        say("il sito non serve ancora le pagine nuove: invio rimandato al prossimo giro"); return 0
    plan = only_live(plan)

    sent = skipped = failed = 0
    for email, c, st, lang, rows in plan:
        try:
            if rows:
                since = st["last"] or day(st["floor"], -1)
                parts = [rows[i:i + MAX_PER_MAIL] for i in range(0, len(rows), MAX_PER_MAIL)]
                for n, part in enumerate(parts, 1):
                    subj, body = mail_html(lang, part, since, len(rows), n, len(parts))
                    api("POST", "/smtp/email", {"sender": SENDER,
                                                "to": [{"email": email, "contactPixelTrackingConsent": False}],
                                                "subject": subj, "htmlContent": body})
                    for t in part:           # segnato solo cio' che e' davvero partito
                        for k in keys_of(t):
                            st["sent"][k] = pub_day(t)
                    save_state(work)
                sent += 1
            else:
                skipped += 1
            st["last"] = hw
        except Exception as e:
            failed += 1
            detail = e.read().decode(errors="replace")[:160] if isinstance(e, urllib.error.HTTPError) else str(e)[:160]
            say(f"errore invio a {mask(email)}: {type(e).__name__} {detail}")   # riprovato al prossimo giro
        keep = day(hw, -KEEP_SENT_DAYS)
        st["sent"] = {k: d for k, d in st["sent"].items() if d >= keep}
    save_state(work)
    say(f"inviati {sent}, senza novita' {skipped}, errori {failed}, dati fino al {hw}"
        + (f", dati cancellati per {gone_now} disiscritti" if gone_now else ""))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:
        import traceback
        say(f"ATTENZIONE errore imprevisto: {type(exc).__name__}: {str(exc)[:200]}")
        say("  " + traceback.format_exc().strip().replace("\n", "\n  ")[-1500:])
        sys.exit(1)
