# Avvisi bandi — come si accende l'invio automatico (5 minuti, solo l'utente)

Oggi (18.9.2026): feed RSS attivi; iscrizione via e-mail a abo@auftragsregister.ch (arriva su Gmail) gestita a mano
nei controlli. Per renderla completamente automatica (iscrizione con conferma, invio giornaliero, disiscrizione):

1. Crea un account gratuito su https://www.brevo.com (piano Free: 300 e-mail/giorno) con dilulloriccardo@gmail.com.
2. Contatti → Impostazioni → Attributi: crea 3 attributi testo: KANTON, BRANCHE, SPRACHE.
3. Contatti → Liste: crea la lista "Avvisi bandi".
4. Contatti → Moduli: crea un modulo con i campi E-mail, KANTON (es. "ZH,BE" oppure ALLE), BRANCHE (prime 2 cifre CPV,
   es. "45,71" oppure ALLE), SPRACHE (de/fr/it/en); attiva il **double opt-in**; copia il codice HTML del modulo.
5. Profilo → SMTP & API → API keys → crea una chiave "avvisi" → incollala nel file `~/.brevo_api_key` (una riga).
6. Mittente: aggiungi e verifica abo@auftragsregister.ch (Brevo manda un'e-mail di verifica: arriva su Gmail via ImprovMX).
Poi dimmi "brevo ok": inserisco il modulo nella pagina /ausschreibungen/abo/, carico il job launchd delle 08:50 e faccio un invio di prova.
Passaggio a pagamento: solo dopo il 1.11 o l'ok scritto di EFG.
