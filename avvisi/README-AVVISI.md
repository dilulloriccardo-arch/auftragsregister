# Avvisi bandi — come funziona (attivo dal 18.9.2026)

Tutto automatico, gratis (Brevo piano Free: 300 e-mail/giorno). Nessun passo manuale per le iscrizioni.

## Flusso
1. **Iscrizione**: modulo su `/{de,fr,it,en}/ausschreibungen/abo/` (e-mail + cantoni + settori, lingua = lingua della pagina).
   Il modulo posta direttamente a Brevo (form "Avvisi bandi", id 6aacf0ec31d42a059fbbc677, campi EMAIL/KANTON/BRANCHE/SPRACHE).
   Con JavaScript la risposta appare nella pagina; senza JavaScript Brevo rimanda a `https://auftragsregister.ch/abo/check/`.
2. **Double opt-in**: Brevo manda l'e-mail "Bitte bestätigen · Merci de confirmer · Confermi · Please confirm" (modello id 1,
   mittente abo@auftragsregister.ch, testo in 4 lingue). Solo dopo il clic il contatto entra nella lista **"Avvisi bandi" (id 3)**
   con gli attributi KANTON ("ZH,BE" o "ALLE"), BRANCHE (prime 2 cifre CPV, "45,72" o "ALLE"), SPRACHE (de/fr/it/en).
   Dopo il clic Brevo rimanda a `https://auftragsregister.ch/abo/ok/`.
3. **Invio giornaliero**: launchd `ch.auftragsregister.avvisi` alle 08:50 (dopo la pubblicazione delle 08:20) esegue
   `invia_avvisi.py`: per ogni contatto della lista 3 prende i bandi in `dati/gare_aperte.json` pubblicati dopo l'ultimo
   invio (`stato.json`, per contatto) che corrispondono a cantone/settore, e manda UNA e-mail transazionale nella sua lingua
   (max 40 bandi, link alle schede del sito). Nessuna novità = nessuna e-mail.
4. **Disiscrizione**: link "Abmelden" in fondo a ogni e-mail (tag Brevo `{{ unsubscribe }}` → il contatto viene messo in
   blacklist e lo script lo salta). In più: chi scrive "Stop" a abo@ va tolto a mano dalla lista (controlli periodici).

## Dove guardare
- Iscritti: Brevo → Contatti → Liste → "Avvisi bandi" (oppure API: `GET /v3/contacts/lists/3/contacts`).
- Invii: Brevo → Transazionale → Log; log locale `avvisi/avvisi.log` (launchd) e `stato.json`.
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
- Il Mac deve essere acceso alle 08:50; se dorme, il job parte al risveglio (launchd) e il catch-up delle 2 ore lo copre.
