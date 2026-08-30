# Öffentliche Aufträge Schweiz — il registro

Sito statico che pubblica ogni aggiudicazione di appalto pubblico svizzero
apparsa su simap.ch, riorganizzata **per azienda** invece che per bando.
Quell'informazione è pubblica ma non esiste in forma consultabile sul web:
cercando il nome di un'impresa non si trova da nessuna parte quali appalti
abbia vinto.

## Perché esiste

Non per vendere qualcosa. Serve a **misurare la domanda senza contattare
nessuno**: quando le pagine sono indicizzate, Search Console dice esattamente
quali frasi la gente digita per arrivarci. Quelle frasi sono il primo dato reale
sulla domanda che questo progetto abbia mai avuto — tutto il resto, in otto mesi,
è stato misurare l'offerta e dedurre.

Se le ricerche dicono che qualcuno cerca qualcosa che vale, si costruisce quella.
A 50-150 €/mese bastano 20-40 clienti per CHF 2.000 al mese.

## Come si usa

    python3 genera.py       # ricostruisce www/ dai dati in dati/
    python3 controlla.py    # link rotti, titoli, description — esce 1 se trova qualcosa
    python3 aggiorna.py     # scarica il nuovo e ricostruisce (è il lavoro notturno)
    ./pubblica.sh           # pubblica su Netlify (i controlli bloccano se falliscono)
    ./installa.sh           # sposta fuori dal Desktop e installa il lavoro notturno

Guardare il sito in locale:

    python3 -m http.server 8791 --directory www

## I file

    genera.py      il generatore: legge dati/, scrive www/
    controlla.py   controllo qualità prima della pubblicazione
    aggiorna.py    aggiornamento notturno (mese corrente + precedente + gare aperte)
    pull_storico.py raccolta iniziale dello storico, un mese per volta
    dati/          le aggiudicazioni scaricate, un file per mese — l'archivio
    www/           il sito generato (si rigenera da zero ogni volta)
    dominio.txt    l'origine canonica, es. https://auftragsregister.ch
    design/        le quattro schermate del progetto grafico

## Stato al 29 agosto 2026

Installato in `~/auftragsregister` (fuori dal Desktop, vedi sotto), con symlink dal
vecchio percorso. Aggiornamento notturno **attivo**, ogni giorno alle 05:40.

    10 mesi di storico · 7.385 aggiudicazioni · 10.467 pagine
    controlli: 0 link rotti, 0 titoli lunghi, 0 somme incoerenti

Lo **storico non è completo**: ne mancano 26 mesi (settembre 2023 – ottobre 2025).
Si riprende quando vuoi, salta i mesi già scaricati:

    cd ~/auftragsregister && python3 pull_storico.py > pull.log 2>&1 &

Serve circa un'ora ogni sei mesi. Non è urgente: il sito funziona già, e ogni mese
aggiunto migliora le schede senza rompere niente.

## Quattro cose imparate a caro prezzo, da non rifare

**1. simap va interrogato un mese per volta.** Una finestra di dodici mesi
risponde con **solo le ultime settimane**: sembrano dodici mesi di dati, sono due.
`pull_storico.py` va per mesi singoli proprio per questo, e `aggiorna.py` non
riscarica mai lo storico.

**2. L'archivio è il fossato.** Poiché una query larga non raggiunge il passato,
chi partisse oggi non potrebbe ricostruire lo storico. `dati/` cresce ogni notte
e nessuno può rifarlo a ritroso. **Non cancellarlo mai.**

**3. Non scaricare mesi in parallelo.** Quattro run simultanei hanno impiegato
**483 minuti ciascuno** invece di dieci: la capacità di calcolo dell'account si
divide fra loro, quindi il parallelo costa una notte e non guadagna niente.
`LANES = 1` è deliberato.

**4. Il codice CPV di primo livello non è una categoria.** `45000000`
"Bauarbeiten" contiene mezzo settore edile: incrociare su quello proponeva a
un'azienda di cablaggi un campo da calcio. Il matching pesa le cifre
significative e pretende quattro cifre in comune.

## Limite noto: le etichette di settore restano in tedesco

I titoli degli appalti compaiono nella lingua in cui sono stati pubblicati (simap ne
fornisce 73% in tedesco, 59% in francese, 3% in italiano, 0% in inglese) — ed è
corretto così: una pubblicazione ufficiale si cita, non si parafrasa. Il piede di
ogni pagina lo dice.

Ma **l'etichetta del codice CPV** ("Dienstleistungen von Ingenieurbüros") è
classificazione, non pubblicazione, e resta in tedesco su tutte e quattro le lingue
perché simap la restituisce nella lingua della richiesta e noi scarichiamo in
tedesco. Si sistema in due modi:

  a) scaricare ogni mese quattro volte, una per lingua — quadruplica i tempi
  b) incorporare il vocabolario CPV ufficiale UE, che esiste in tutte le lingue
     europee ed è una tabella fissa — è la strada giusta, non ancora fatta

## Legale

I dati vengono da simap.ch. Le loro condizioni API **§4 permettono l'uso
commerciale e la trasmissione a terzi**; **§5 impone** di non alterarli, di
tenerli distinti dal commento e di riportare il disclaimer alla lettera — che sta
nel piede di ogni pagina. Il commento nostro sta nel riquadro marcato, separato
dai dati.

Nessun dato personale: le aziende del registro sono persone giuridiche, e dal
1° settembre 2023 la legge svizzera protegge solo le persone fisiche.

## Cosa manca, in ordine

1. **Un dominio.** Sembrano liberi (indizio DNS, da confermare):
   `auftragsregister.ch`, `zuschlagsregister.ch`, `vergaberegister.ch`,
   `oeffentliche-auftraege.ch`. ~15 CHF/anno, si registra come persona fisica.
2. **Un account Netlify** (gratuito) e `npm install -g netlify-cli && netlify login`.
   Netlify e non Cloudflare: con quattro lingue il sito fa ~41.000 file e il piano
   gratuito di Cloudflare Pages si ferma a 20.000. Netlify non ha limite totale.
3. `echo "https://iltuodominio.ch" > dominio.txt`, poi `./pubblica.sh`.
4. **Search Console**: aggiungere il sito, inviare `sitemap.xml`. È il passo che
   trasforma il sito nello strumento di misura per cui esiste.
5. Aspettare. L'indicizzazione richiede mesi; il sito nel frattempo si aggiorna
   da solo e non chiede niente a nessuno.
