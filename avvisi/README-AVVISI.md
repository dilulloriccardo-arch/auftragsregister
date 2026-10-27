# Avvisi bandi — come funziona (attivo dal 18.9.2026, riscritto il 24.9.2026, e-mail v3 dal 21.10.2026)

Tutto automatico, gratis (Brevo piano Free: 300 e-mail/giorno). Nessun passo manuale per le iscrizioni.

## Flusso
1. **Iscrizione**: modulo su `/{de,fr,it,en}/ausschreibungen/abo/` (e-mail + cantoni + settori, lingua = lingua della pagina).
   Il modulo posta direttamente a Brevo (form "Avvisi bandi", id 6aacf0ec31d42a059fbbc677, campi EMAIL/KANTON/BRANCHE/SPRACHE).
   Con JavaScript la risposta appare nella pagina; senza JavaScript Brevo rimanda a `https://auftragsregister.ch/abo/check/`.
2. **Double opt-in**: Brevo manda l'e-mail "Bitte bestätigen · Merci de confirmer · Confermi · Please confirm" (modello id 1,
   mittente abo@auftragsregister.ch, testo in 4 lingue). Solo dopo il clic il contatto entra nella lista **"Avvisi bandi" (id 3)**
   con gli attributi KANTON ("ZH,BE" o "ALLE"), BRANCHE (prime 2 cifre CPV, "45,72" o "ALLE"), SPRACHE (de/fr/it/en).
   Dopo il clic Brevo rimanda a `https://auftragsregister.ch/abo/ok/`.
3. **Invio**: `aggiorna.py` chiama `invia_avvisi.py` subito dopo una pubblicazione verificata (push riuscito, nessun
   commit in sospeso); in piu' un giro di riserva launchd `ch.auftragsregister.avvisi` alle 12:30. Lo script legge SOLO
   `dati/gare_pubblicate.json` (la copia che il nightly scrive quando le pagine sono su GitHub), aspetta che GitHub Pages
   serva le pagine e manda a ogni contatto della lista 3 i bandi che non ha ancora ricevuto (per pubblicazione e per
   progetto: le rettifiche non si riannunciano), pubblicati da non piu' di 14 giorni, non scaduti, con la loro pagina sul
   sito, che corrispondono a cantone/settore. **Una sola e-mail al giorno per iscritto**, mai divisa in parti (vedi
   «L'e-mail» qui sotto). Nessuna novita' = nessuna e-mail. Due giri lo stesso giorno sono innocui: chi ha gia' ricevuto
   l'e-mail del giorno (giorno svizzero) non ne riceve una seconda; i bandi trovati dopo (pagine arrivate tardi, nightly
   rilanciato) restano non segnati e partono con l'e-mail del giorno dopo. Un invio fallito non conta: si riprova al giro
   dopo, anche lo stesso giorno. Stato per contatto in `avvisi/stato.json` (mai nel repo: `.gitignore`), con `mailed` =
   giorno dell'ultima e-mail (gli stati scritti prima del 21.10.2026 non ce l'hanno e valgono "nessuna e-mail oggi").
4. **Disiscrizione**: link in fondo a ogni e-mail (tag Brevo `{{ unsubscribe }}` → blocco transazionale di Brevo). Al giro
   dopo lo script toglie il contatto dalla lista 3, ne svuota KANTON/BRANCHE/SPRACHE e cancella il suo stato locale.
   **Il contatto e il blocco restano a Brevo**: cancellarlo farebbe perdere il blocco, e sbloccare chi si e' disiscritto
   e' illecito. Lo script non cancella e non sblocca MAI nessuno.
   Chi scrive "Stop" a abo@: in Brevo → Transazionale → contatti bloccati, bloccarlo a mano (motivo adminBlocked); al giro
   dopo lo script fa il resto. Rimbalzi definitivi: nessun invio, contatto tenuto.
   Se un disiscritto risulta modificato dopo il blocco (forse si e' reiscritto) il log lo segnala: decidere a mano entro 7
   giorni se sbloccarlo in Brevo (solo se la nuova iscrizione e' confermata).

## L'e-mail (modello v3, dal 21.10.2026)
- Modello: `avvisi/mail_v3.py`, design A2 «Brass» approvato il 20.10.2026 (banda nera con il numero dei nuovi bandi e la
  scelta, schede bianche, pulsante ottone), nella lingua dell'iscritto (SPRACHE). HTML e testo semplice (`textContent`).
- **Al massimo 40 schede**: i bandi con la Eingabefrist piu' vicina, a parita' i piu' nuovi. Oggetto e banda contano tutti
  i nuovi bandi, anche quelli senza scheda ("63 neue Ausschreibungen im Kanton Zürich").
- **Oltre 40**: sotto le schede la riga «+ 23 weitere neue Ausschreibungen auf der Website» (fr «+ 23 autres nouveaux
  appels d’offres sur le site», it «+ 23 altri nuovi bandi sul sito», en «+ 23 more new tenders on the website») e il
  pulsante verso la lista del sito filtrata per la scelta: `/{lingua}/ausschreibungen/?k=ZH&b=45&sort=neu` (piu' nuovi
  prima). La lista filtra un solo cantone e una sola branca: con piu' cantoni o piu' branche resta il filtro possibile.
  Anche i bandi contati nel «+ N» sono segnati come inviati: annunciati e sul sito, il giorno dopo non tornano.
- Peso: sotto i 100 KB (40 schede reali: 78-82 KB). Solo con titoli lunghissimi l'e-mail mostra meno schede e conta il
  resto nel «+ N». Gmail taglia oltre i 102 KB (e nasconde il link di disiscrizione): se Brevo allunga i link per il
  conteggio dei clic, impostare `PER_LINK` in `mail_v3.py` (byte in piu' per link).
- Pro: spazio spento (`pro=False`), nessun link a `/pro/`.
- In fondo: «Abmelden» (`{{ unsubscribe }}`, l'unico tag Brevo), Datenschutz, Impressum, fonte simap.ch e la nota di
  simap obbligatoria, testuale e in tedesco.

## Dove guardare
- Iscritti: Brevo → Contatti → Liste → "Avvisi bandi" (oppure API: `GET /v3/contacts/lists/3/contacts`).
- Invii: Brevo → Transazionale → Log; log locale `avvisi/avvisi.log` (indirizzi mascherati) e in `aggiorna.log` la riga `avvisi:`.
  La riga finale di ogni giro: `inviati N, senza novita' N, errori N, dati fino al …`, piu' `rinviati a domani N` se
  qualcuno aveva gia' ricevuto l'e-mail del giorno.
- Chiave API: `~/.brevo_api_key` (600). Se manca, lo script salta l'invio senza errori.
- Modelli e-mail (id 1 double opt-in, 3 conferma finale, 4 disiscrizione): modificabili via API `PUT /v3/smtp/templates/{id}`.

## Test fatto il 18.9.2026
Iscrizione via endpoint con attributi → e-mail DOI ricevuta (via ImprovMX su Gmail) → clic → contatto in lista 3 con
KANTON/BRANCHE/SPRACHE corretti → `invia_avvisi.py` ha mandato 2 e-mail (DE 6 bandi ZH/BE cpv 72, FR 19 bandi TI/GE cpv 45)
con link di disiscrizione funzionante. Contatto di prova rimasto: abo@auftragsregister.ch (ZH,BE / 72 / de).

## Limiti
- Piano Free: 300 e-mail/giorno → fino a ~250 iscritti attivi al giorno; oltre, passare al piano a pagamento
  (solo dopo il 1.11.2026 o l'ok scritto di EFG).
- Il modulo Brevo mostra un avviso "consigliato reCAPTCHA": non attivo (il modulo del sito ha un campo honeypot).
- Il Mac deve essere acceso: se il nightly salta, il recupero automatico (ogni 2 ore, 08-18, max 2 rilanci) lo rilancia
  finche' `dati/ultimo_ok.txt` non ha la data di oggi.
- Fino al 24.9.2026 gli avvisi non potevano funzionare: il giro fisso delle 08:50 partiva prima che il nightly
  scrivesse i bandi del giorno e lo stato salvava "oggi". Riscritto con tre giri di revisione indipendente.
