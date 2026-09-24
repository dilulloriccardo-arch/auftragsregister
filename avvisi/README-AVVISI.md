# Avvisi bandi — come funziona (attivo dal 18.9.2026, riscritto il 24.9.2026)

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
   sito, che corrispondono a cantone/settore. Piu' di 100 bandi = piu' e-mail da 100. Nessuna novita' = nessuna e-mail.
   Due giri lo stesso giorno sono innocui. Stato per contatto in `avvisi/stato.json` (mai nel repo: `.gitignore`).
4. **Disiscrizione**: link in fondo a ogni e-mail (tag Brevo `{{ unsubscribe }}` → blocco transazionale di Brevo). Al giro
   dopo lo script toglie il contatto dalla lista 3, ne svuota KANTON/BRANCHE/SPRACHE e cancella il suo stato locale.
   **Il contatto e il blocco restano a Brevo**: cancellarlo farebbe perdere il blocco, e sbloccare chi si e' disiscritto
   e' illecito. Lo script non cancella e non sblocca MAI nessuno.
   Chi scrive "Stop" a abo@: in Brevo → Transazionale → contatti bloccati, bloccarlo a mano (motivo adminBlocked); al giro
   dopo lo script fa il resto. Rimbalzi definitivi: nessun invio, contatto tenuto.
   Se un disiscritto risulta modificato dopo il blocco (forse si e' reiscritto) il log lo segnala: decidere a mano entro 7
   giorni se sbloccarlo in Brevo (solo se la nuova iscrizione e' confermata).

## Dove guardare
- Iscritti: Brevo → Contatti → Liste → "Avvisi bandi" (oppure API: `GET /v3/contacts/lists/3/contacts`).
- Invii: Brevo → Transazionale → Log; log locale `avvisi/avvisi.log` (indirizzi mascherati) e in `aggiorna.log` la riga `avvisi:`.
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
