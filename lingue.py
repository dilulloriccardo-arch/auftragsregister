#!/usr/bin/env python3
"""Chrome strings for the four site languages.

Only the site's own words are translated. The publications themselves are shown as
the register published them: simap carries German for 73% of titles and French for
59%, but Italian for 3% and no English at all, so a translated-looking title would
often be a German one wearing an Italian label. An official publication is quoted,
not paraphrased — so where the language asked for is missing, the original stands.
"""
from __future__ import annotations

LANGS = ("de", "fr", "it", "en")

NAMES = {"de": "Deutsch", "fr": "Français", "it": "Italiano", "en": "English"}

T: dict[str, dict[str, str]] = {
    "site": {
        "de": "Öffentliche Aufträge Schweiz", "fr": "Marchés publics suisses",
        "it": "Appalti pubblici svizzeri", "en": "Swiss Public Contracts",
    },
    "register": {"de": "Register", "fr": "Registre", "it": "Registro", "en": "Register"},
    "companies": {"de": "Unternehmen", "fr": "Entreprises", "it": "Imprese",
                  "en": "Companies"},
    "buyers": {"de": "Auftraggeber", "fr": "Adjudicateurs", "it": "Committenti",
               "en": "Contracting authorities"},
    "cantons": {"de": "Kantone", "fr": "Cantons", "it": "Cantoni", "en": "Cantons"},
    "sectors": {"de": "Bereiche", "fr": "Domaines", "it": "Categorie", "en": "Categories"},
    "contracts": {"de": "Aufträge", "fr": "Marchés", "it": "Appalti", "en": "Contracts"},
    "tenders": {"de": "Ausschreibungen", "fr": "Appels d'offres", "it": "Bandi",
                "en": "Tenders"},
    "award": {"de": "Zuschlag", "fr": "Adjudication", "it": "Aggiudicazione",
              "en": "Award"},
    "awards": {"de": "Zuschläge", "fr": "Adjudications", "it": "Aggiudicazioni",
               "en": "Awards"},
    "award_granted": {"de": "Zuschlag erteilt", "fr": "Marché adjugé",
                      "it": "Appalto aggiudicato", "en": "Contract awarded"},
    "tender_open": {"de": "Ausschreibung offen", "fr": "Appel d'offres en cours",
                    "it": "Bando aperto", "en": "Open for bids"},
    "sum": {"de": "Summe (CHF)", "fr": "Total (CHF)", "it": "Totale (CHF)", "en": "Total (CHF)"},
    "sum_published": {"de": "Summe der Beträge in CHF", "fr": "Total des montants en CHF",
                      "it": "Totale degli importi in CHF", "en": "Total of amounts in CHF"},
    "median": {"de": "Typischer Betrag (Median)", "fr": "Montant typique (médiane)", "it": "Importo tipico (mediana)",
               "en": "Typical amount (median)"},
    # the award lists (company, buyer, a project's lots): no currency in the header, which stood over
    # euro and dollar amounts; a foreign amount names its currency in its cell (08.10.2026)
    "amount": {"de": "Betrag", "fr": "Montant", "it": "Importo", "en": "Amount"},
    "date": {"de": "Datum", "fr": "Date", "it": "Data", "en": "Date"},
    "contract": {"de": "Auftrag", "fr": "Marché", "it": "Appalto", "en": "Contract"},
    "buyer": {"de": "Auftraggeber", "fr": "Adjudicateur", "it": "Committente",
              "en": "Contracting authority"},
    "canton": {"de": "Kanton", "fr": "Canton", "it": "Cantone", "en": "Canton"},
    "canton_abbr": {"de": "Kt.", "fr": "Cant.", "it": "Cant.", "en": "Canton"},
    # the home's company table: the canton where most of the firm's awards fall, not its seat
    "canton_most": {"de": "Kanton mit den meisten Zuschlägen", "fr": "Canton comptant le plus d’adjudications",
                    "it": "Cantone con più aggiudicazioni", "en": "Canton with the most awards"},
    "deadline": {"de": "Eingabefrist", "fr": "Délai de remise", "it": "Termine d'inoltro",
                 "en": "Submission deadline"},
    "procedure": {"de": "Verfahren", "fr": "Procédure", "it": "Procedura",
                  "en": "Procedure"},
    "publication": {"de": "Publikationsnummer", "fr": "N° de publication", "it": "N. di pubblicazione",
                    "en": "Publication no."},
    "published_on": {"de": "Publiziert am", "fr": "Publié le", "it": "Data di pubblicazione",
                     "en": "Published on"},
    "offers": {"de": "eingegangene Angebote", "fr": "offres reçues",
               "it": "offerte ricevute", "en": "bids received"},
    "chronological": {"de": "neueste zuerst", "fr": "les plus récentes d’abord",
                      "it": "dalla più recente", "en": "newest first"},
    "by_awards": {"de": "nach Anzahl der Zuschläge", "fr": "par nombre d’adjudications",
                  "it": "per numero di aggiudicazioni", "en": "by number of awards"},
    "main_sector": {"de": "Hauptbereich", "fr": "Domaine principal",
                    "it": "Categoria principale", "en": "Main category"},
    "activities": {"de": "Tätigkeitsbereiche", "fr": "Domaines d'activité",
                   "it": "Categorie di attività", "en": "Categories"},
    "reason": {"de": "Begründung des Auftraggebers", "fr": "Motivation de l'adjudicateur",
               "it": "Motivazione del committente", "en": "Reasons given by the contracting "
                                                          "authority"},
    "description": {"de": "Beschreibung", "fr": "Description", "it": "Descrizione",
                    "en": "Description"},
    "details": {"de": "Angaben", "fr": "Détails", "it": "Dettagli", "en": "Details"},
    "type": {"de": "Auftragsart", "fr": "Type de marché", "it": "Tipo di appalto",
             "en": "Contract type"},
    # a soft hyphen: the Details column breaks the compound there rather than mid-syllable
    "treaty": {"de": "Staatsvertrags\u00adbereich", "fr": "Accord international",
               "it": "Trattato internazionale", "en": "International treaty"},
    "place": {"de": "Ort", "fr": "Lieu", "it": "Luogo", "en": "Location"},
    "source": {"de": "Quelle", "fr": "Source", "it": "Fonte", "en": "Source"},
    # no "Aggiornato al" before a date: it reads "al 08.10.2026" on the 8th (all'8). The date is the newest
    # publication's (DATA_DATE), named as the footer names it (META["stand"]; step 5, copy pass)
    "updated": {"de": "Daten vom", "fr": "État des données", "it": "Stato dei dati",
                "en": "Data as of"},
    "period": {"de": "Zeitraum", "fr": "Période", "it": "Periodo", "en": "Period"},
    # one label for the same date on the home and the tenders pages
    "as_of": {"de": "Daten vom", "fr": "État des données", "it": "Stato dei dati", "en": "Data as of"},
    "entries": {"de": "Einträge", "fr": "Entrées", "it": "Voci", "en": "Entries"},
    "until": {"de": "bis", "fr": "jusqu'au", "it": "entro il", "en": "due"},
    "running": {"de": "Offene Ausschreibungen", "fr": "Appels d’offres en cours", "it": "Bandi aperti", "en": "Open tenders"},
    "language": {"de": "Sprache", "fr": "Langue", "it": "Lingua", "en": "Language"},
    "company": {"de": "Unternehmen", "fr": "Entreprise", "it": "Impresa", "en": "Company"},
    "tender": {"de": "Ausschreibung", "fr": "Appel d’offres", "it": "Bando", "en": "Tender"},
    "winner": {"de": "Zuschlag an", "fr": "Adjudicataire", "it": "Aggiudicatario", "en": "Awarded to"},
    "award_to": {"de": "Zuschlag an", "fr": "Adjugé à", "it": "Aggiudicato a", "en": "Awarded to"},
    "award_amount": {
        "de": "Zuschlagsbetrag",
        "fr": "Montant adjugé",
        "it": "Importo aggiudicato",
        "en": "Awarded amount",
    },
    "approx": {"de": "rund {v}", "fr": "environ {v}", "it": "circa {v}", "en": "about {v}"},
    "median_help": {
        "de": "Die Hälfte der Zuschläge mit zurechenbarem Betrag liegt darüber, die andere Hälfte "
              "darunter.",
        "fr": "La moitié des adjudications dotées d’un montant attribuable se situe au-dessus de ce "
              "montant, l’autre moitié en dessous.",
        "it": "Metà delle aggiudicazioni con un importo attribuibile supera questo valore, l’altra "
              "metà resta al di sotto.",
        "en": "Half of the awards with an attributable amount are above this figure, half below.",
    },
    "not_published": {
        "de": "nicht publiziert",
        "fr": "non publié",
        "it": "non pubblicato",
        "en": "not published",
    },
    # an amount that cannot be credited to this firm alone: none published, a foreign
    # currency, or a joint award ("kein eigener Betrag" / "no own amount" was opaque)
    "no_own_amount": {
        "de": "kein zurechenbarer Betrag",
        "fr": "pas de montant attribuable",
        "it": "nessun importo attribuibile",
        "en": "no attributable amount",
    },
    "main_cantons": {
        "de": "Häufigste Kantone",
        "fr": "Principaux cantons",
        "it": "Cantoni principali",
        "en": "Main cantons",
    },
    # an award naming several firms: often separate awards per lot, section or framework
    # contract, so "gemeinsam" / "conjointement" said more than the publication does
    "joint": {"de": "an mehrere Unternehmen", "fr": "à plusieurs entreprises", "it": "a più imprese",
              "en": "to several companies"},
    "main_canton": {
        "de": "Häufigster Kanton",
        "fr": "Canton principal",
        "it": "Cantone principale",
        "en": "Main canton",
    },
    "offers_one": {
        "de": "eingegangenes Angebot",
        "fr": "offre reçue",
        "it": "offerta ricevuta",
        "en": "bid received",
    },
}


def t(key: str, lang: str) -> str:
    return T[key][lang]


# Longer strings that carry the register's own voice, kept apart from the labels.
PROSE: dict[str, dict[str, str]] = {
    "tagline": {
        "de": "Wer gewinnt die öffentlichen Aufträge in der Schweiz?",
        "fr": "Qui remporte les marchés publics en Suisse ?",
        "it": "Chi vince gli appalti pubblici in Svizzera?",
        "en": "Who wins public contracts in Switzerland?",
    },
    "lead": {
        # "all awards" promised more than the archive holds: it starts in August 2024, and its
        # first months are incomplete (the chart below says so)
        "de": "Die seit August 2024 auf simap.ch publizierten Zuschläge, geordnet nach "
              "Unternehmen – mit Auftraggeber, Betrag und Verfahren. Dazu die Ausschreibungen, "
              "die gerade offen sind.",
        "fr": "Les adjudications publiées sur simap.ch depuis août 2024, présentées par "
              "entreprise : adjudicateur, montant, procédure — et les appels d'offres en cours.",
        "it": "Le aggiudicazioni pubblicate su simap.ch da agosto 2024, raggruppate per impresa: "
              "committente, importo, procedura – e i bandi attualmente aperti.",
        "en": "The awards published on simap.ch since August 2024, arranged by company: "
              "contracting authority, amount, procedure — and which tenders are currently open.",
    },
    "source_note": {
        "de": "Amtliche Publikationen von Bund, Kantonen und Gemeinden",
        "fr": "Publications officielles de la Confédération, des cantons et des communes",
        "it": "Pubblicazioni ufficiali della Confederazione, dei Cantoni e dei Comuni",
        "en": "Official publications of the Confederation, cantons and communes",
    },
    "source_inline": {
        "de": "amtliche Publikationen von Bund, Kantonen und Gemeinden",
        "fr": "publications officielles de la Confédération, des cantons et des communes",
        "it": "pubblicazioni ufficiali della Confederazione, dei Cantoni e dei Comuni",
        "en": "official publications of the Confederation, cantons and communes",
    },
    "not_official": {
        "de": "Diese Website bereitet öffentlich publizierte Daten auf und ist kein Ersatz für "
              "simap.ch. Massgebend sind ausschliesslich die Publikationen auf simap.ch.",
        "fr": "Ce site présente des données publiées officiellement et ne remplace pas "
              "simap.ch. Seules les publications qui y figurent font foi.",
        "it": "Questo sito rielabora dati pubblicati ufficialmente e non sostituisce "
              "simap.ch. Fanno fede esclusivamente le pubblicazioni che vi figurano.",
        "en": "This site presents officially published data and does not replace simap.ch. "
              "Only the publications on simap.ch are authoritative.",
    },
    # the footer's first line. In German it stops after the first sentence: the verbatim
    # simap notice right below it already says "Massgebend sind …", and the footer printed
    # two consecutive "Massgebend" sentences on every German page
    "footer_note": {
        "de": "Diese Website bereitet öffentlich publizierte Daten auf und ist kein Ersatz für "
              "simap.ch.",
        "fr": "Ce site présente des données publiées officiellement et ne remplace pas "
              "simap.ch. Seules les publications qui y figurent font foi.",
        "it": "Questo sito rielabora dati pubblicati ufficialmente e non sostituisce "
              "simap.ch. Fanno fede esclusivamente le pubblicazioni che vi figurano.",
        "en": "This site presents officially published data and does not replace simap.ch. "
              "Only the publications on simap.ch are authoritative.",
    },
    "official_link": {
        "de": "Amtliche Publikation: {link} — massgebend ist ausschliesslich diese Veröffentlichung.",
        "fr": "Publication officielle : {link} – seule cette publication fait foi.",
        "it": "Pubblicazione ufficiale: {link}. Fa fede esclusivamente quella pubblicazione.",
        "en": "Official publication: {link}. Only that publication is authoritative.",
    },
    "view_on_simap": {
        "de": "Projekt {n} auf simap.ch", "fr": "projet {n} sur simap.ch",
        "it": "progetto n. {n} su simap.ch", "en": "project {n} on simap.ch",
    },
    # genera.matches() needs four significant CPV digits in common: the same code or a
    # closely related one, never "the same sector" (the list shows other exact codes)
    "matched_tenders": {
        "de": "Offene Ausschreibungen in verwandten Bereichen",
        "fr": "Appels d’offres en cours dans des domaines apparentés",
        "it": "Bandi aperti in categorie affini",
        "en": "Open tenders in related categories",
    },
    "matched_note": {
        "de": "Offene Ausschreibungen mit demselben oder einem eng verwandten CPV-Code (der "
              "EU-weit einheitlichen Einteilung der Leistungen) wie die bisherigen Zuschläge "
              "dieses Unternehmens.",
        "fr": "Appels d’offres en cours dont le code CPV (le vocabulaire commun pour les marchés "
              "publics de l’UE) est identique ou étroitement apparenté à celui d’adjudications déjà "
              "obtenues par cette entreprise.",
        "it": "Bandi aperti con un codice CPV (il vocabolario comune per gli appalti pubblici dell’UE) "
              "uguale o affine a quello delle aggiudicazioni già ottenute da questa impresa.",
        "en": "Tenders still open whose CPV code (the EU’s Common Procurement Vocabulary) is the same "
              "as, or closely related to, that of this company’s past awards.",
    },
    # grouped on the first four significant CPV digits of the main code: related sectors,
    # not one exact code (the same wording as the matched tenders above it)
    "peers": {
        "de": "Weitere Unternehmen in verwandten Bereichen", "fr": "Autres entreprises dans des domaines apparentés",
        "it": "Altre imprese in categorie affini", "en": "Other companies in related categories",
    },
    "analysis": {
        "de": "Zuschläge pro Jahr", "fr": "Adjudications par année", "it": "Aggiudicazioni per anno", "en": "Awards per year",
    },
    "derived": {
        "de": "eigene Auswertung der Publikationen", "fr": "analyse établie à partir des "
                                                        "publications",
        "it": "elaborazione propria dei dati pubblicati", "en": "our analysis of the published data",
    },
    "open_tenders_h1": {
        "de": "Offene Ausschreibungen in der Schweiz",
        "fr": "Appels d’offres en cours en Suisse",
        "it": "Bandi aperti in Svizzera",
        "en": "Open public tenders in Switzerland",
    },
    "translation_note": {
        "de": "Titel und Beschreibungen erscheinen in der Sprache, in der sie publiziert "
              "wurden. Nicht jede Publikation liegt in allen Landessprachen vor.",
        "fr": "Les titres et descriptions apparaissent dans la langue de publication. "
              "Toutes les publications ne sont pas disponibles dans toutes les langues.",
        "it": "Titoli e descrizioni compaiono nella lingua in cui sono stati pubblicati. Non "
              "tutte le pubblicazioni sono disponibili in tutte le lingue.",
        "en": "Titles and descriptions are shown in the language in which they were published; only "
              "some are available in English.",
    },
    "disclaimer": {
        # simap requires this notice verbatim, in the language of the publication; the
        # German wording is the one their terms prescribe and is never translated away.
        "de": "Dies ist keine amtliche Veröffentlichung. Massgebend sind die auf der "
              "Plattform www.simap.ch veröffentlichten Daten.",
    },
}


def p(key: str, lang: str) -> str:
    d = PROSE[key]
    return d.get(lang, d["de"])


# Titles and meta descriptions, as format templates. These are the strings a search
# engine shows, so each language gets its own phrasing rather than a word swap.
META: dict[str, dict[str, str]] = {
    "company_title": {"de": " — öffentliche Aufträge", "fr": " — marchés publics",
                      "it": " — appalti pubblici", "en": " — public contracts"},
    # for a long company name: the awards it won (a buyer page's short suffix is ' — Aufträge')
    "company_title_short": {"de": " — Zuschläge", "fr": " — marchés", "it": " — appalti",
                            "en": " — awards"},
    "company_desc": {
        "de": "{name}: {n} auf simap.ch{span}{val} – mit Auftraggebern, Beträgen und Kantonen.",
        "fr": "{name} : {n} publiées sur simap.ch{span}{val}. Adjudicateurs, montants, cantons.",
        "it": "{name}: {n} pubblicate su simap.ch{span}{val}. Committenti, importi e cantoni.",
        "en": "{name}: {n} published on simap.ch{span}{val}, with contracting authorities, "
              "amounts and cantons.",
    },
    "company_val": {
        "de": ", zusammen {v}",
        "fr": ", au total {v}",
        "it": ", per un totale di {v}",
        "en": ", {v} in total",
    },
    "top_buyer_share": {
        "de": "Häufigster Auftraggeber: {buyer} ({share} der Zuschläge).",
        "fr": "Principal adjudicateur : {buyer} ({share} de ses adjudications).",
        "it": "Committente principale: {buyer} ({share} delle aggiudicazioni).",
        "en": "Most frequent contracting authority: {buyer} ({share} of awards).",
    },
    "top_buyer_only": {
        "de": "Einziger Auftraggeber: {buyer}.",
        "fr": "Seul adjudicateur : {buyer}.",
        "it": "Unico committente: {buyer}.",
        "en": "Sole contracting authority: {buyer}.",
    },
    "company_lead": {
        "de": "{n} auf simap.ch publiziert{span}, erteilt von {b}.",
        "fr": "{n} publiées sur simap.ch par {b}{span}.",
        "it": "{n} pubblicate su simap.ch{span}, da {b}.",
        "en": "{n} published on simap.ch{span}, from {b}.",
    },
    "buyers_count": {"de": "{k} verschiedenen Auftraggebern", "fr": "{k} adjudicateurs différents",
                     "it": "{k} committenti diversi", "en": "{k} different contracting "
                                                            "authorities"},
    "award_suffix": {"de": " — Zuschlag", "fr": " — adjudication", "it": " — aggiudicazione",
                     "en": " — award"},
    "tender_suffix": {"de": " — Ausschreibung", "fr": " — appel d'offres",
                      "it": " — bando", "en": " — tender"},
    "buyer_title": {"de": " — vergebene Aufträge", "fr": " — marchés adjugés",
                    "it": " — appalti aggiudicati", "en": " — contracts awarded"},
    # a shorter suffix, for the few authorities whose long names differ only in the middle
    "buyer_title_short": {"de": " — Aufträge", "fr": " — marchés", "it": " — appalti",
                          "en": " — contracts"},
    "buyer_desc": {
        "de": "{name}: {n} an {f}, publiziert auf simap.ch.",
        "fr": "{name} : {n} en faveur de {f}, publiées sur simap.ch.",
        "it": "{name}: {n} a favore di {f}, pubblicate su simap.ch.",
        "en": "{name}: {n} to {f}, published on simap.ch.",
    },
    "buyer_lead": {
        "de": "Dieser Auftraggeber hat {n} an {f} vergeben und auf simap.ch publiziert.",
        "fr": "{n} attribuées à {f} et publiées sur simap.ch.",
        "it": "{n} a favore di {f}, pubblicate su simap.ch.",
        "en": "{n} made to {f} and published on simap.ch.",
    },
    "buyer_joint_note": {
        "de": "{k} Zuschläge gingen an mehrere Unternehmen.",
        "fr": "{k} adjudications ont été attribuées à plusieurs entreprises.",
        "it": "{k} aggiudicazioni sono andate a più imprese.",
        "en": "{k} awards went to several companies.",
    },
    "canton_title": {"de": "Öffentliche Aufträge im Kanton {name}",
                     "fr": "Marchés publics du canton {of}",
                     "it": "Appalti pubblici nel Canton {name}",
                     "en": "Public contracts in the canton of {name}"},
    "canton_suffix": {"de": " — Zuschläge", "fr": " — adjudications",
                      "it": " — aggiudicazioni", "en": " — awards"},
    "canton_desc": {
        "de": "{n} im Kanton {name} an {f}, publiziert auf simap.ch – mit Beträgen, Branchen und "
              "Monatsverlauf.",
        "fr": "{n} dans le canton {of} en faveur de {f} (simap.ch) : montants, branches et "
              "évolution mensuelle.",
        "it": "{n} nel Canton {name} pubblicate su simap.ch, a favore di {f}: importi, rami e "
              "andamento mensile.",
        "en": "{n} to {f} in the canton of {name}, published on simap.ch, with amounts, "
              "industries and monthly trend.",
    },
    # the canton pages count awards by the canton where the contract is carried out; many
    # were published by companies owned by the state (airport, utilities), not by offices
    "canton_lead": {
        "de": "Für Aufträge im Kanton {name} wurden auf simap.ch {n} publiziert; sie gingen an {f}.",
        "fr": "Dans le canton {of}, {n} en faveur de {f} ont été publiées sur simap.ch.",
        "it": "Per gli appalti eseguiti nel Canton {name} sono state pubblicate su simap.ch {n}, "
              "a favore di {f}.",
        "en": "For contracts in the canton of {name}, {n} were published on simap.ch; they went to {f}.",
    },
    "canton_lead_one": {
        "de": "Für Aufträge im Kanton {name} wurde auf simap.ch {n} publiziert; er ging an {f}.",
        "fr": "Dans le canton {of}, {n} en faveur de {f} a été publiée sur simap.ch.",
        "it": "Per gli appalti eseguiti nel Canton {name} è stata pubblicata su simap.ch {n}, a "
              "favore di {f}.",
        "en": "For contracts in the canton of {name}, {n} was published on simap.ch; it went to {f}.",
    },
    "sector_suffix": {"de": " – CPV {code}", "fr": " – CPV {code}",
                      "it": " – CPV {code}", "en": " – CPV {code}"},
    # with the keyword a searcher types, where the sector's name leaves room for it
    "sector_suffix_long": {"de": " – Aufträge · CPV {code}", "fr": " – marchés · CPV {code}",
                           "it": " – appalti · CPV {code}", "en": " – contracts · CPV {code}"},
    # the project number at the end of an award or tender <title>, where two pages share a title
    "title_no": {"de": "Nr. {n}", "fr": "n°\u00a0{n}", "it": "n. {n}", "en": "no. {n}"},
    "sector_desc": {
        "de": "{n} an {f} im Bereich «{label}», publiziert auf simap.ch.",
        "fr": "{n} en faveur de {f} dans le domaine « {label} », publiées sur simap.ch.",
        "it": "{n} a favore di {f} nella categoria «{label}», pubblicate su simap.ch.",
        "en": "{n} to {f} in the “{label}” category, published on simap.ch.",
    },
    "sector_lead": {"de": "{n} an {f} in diesem Bereich.",
                    "fr": "{n} en faveur de {f} dans ce domaine.",
                    "it": "{n} a favore di {f} in questa categoria.",
                    "en": "{n} to {f} in this category."},
    "home_title": {"de": "Öffentliche Aufträge Schweiz — Zuschläge nach Unternehmen",
                   "fr": "Marchés publics suisses — adjudications par entreprise",
                   "it": "Appalti pubblici svizzeri — aggiudicazioni per impresa",
                   "en": "Swiss Public Contracts — awards by company"},
    "home_desc": {
        "de": "{n} auf simap.ch publizierte Zuschläge, nach Unternehmen geordnet: wer in der "
              "Schweiz welche öffentlichen Aufträge gewinnt und zu welchem Betrag.",
        "fr": "{n} adjudications publiées sur simap.ch, présentées par entreprise : qui "
              "remporte quels marchés publics en Suisse et pour quel montant.",
        "it": "{n} aggiudicazioni pubblicate su simap.ch, raggruppate per impresa: chi vince "
              "quali appalti pubblici in Svizzera e per quale importo.",
        "en": "{n} awards published on simap.ch, arranged by company: who wins which "
              "public contracts in Switzerland and for what amount.",
    },
    "open_title": {"de": "Öffentliche Ausschreibungen Schweiz: {n} offen",
                   "fr": "Appels d’offres publics en Suisse : {n} en cours",
                   "it": "Bandi di gara in Svizzera: {n} aperti",
                   "en": "Public tenders in Switzerland: {n} open"},
    "open_desc": {
        "de": "Offene Ausschreibungen von Bund, Kantonen und Gemeinden auf simap.ch an einem Ort: "
              "nach Frist, Kanton und Branche. Ohne Konto, mit kostenlosem E-Mail-Abo.",
        "fr": "Appels d’offres publics en cours de la Confédération, des cantons et des communes publiés "
              "sur simap.ch, par délai, canton et branche. Sans compte, alerte e-mail gratuite.",
        "it": "Bandi aperti di Confederazione, Cantoni e Comuni pubblicati su simap.ch, in un unico posto: per "
              "scadenza, cantone e ramo. Senza account, con avviso e-mail gratuito.",
        "en": "Open public tenders from the Confederation, cantons and communes published on simap.ch, in one "
              "place, by deadline, canton and industry. No account, free email alerts.",
    },
    "open_lead": {
        "de": "{n} öffentliche Ausschreibungen mit noch offener Eingabefrist, publiziert von "
              "Bund, Kantonen und Gemeinden auf simap.ch – nach Frist geordnet, nach Kanton und "
              "Branche gegliedert, in der Regel werktags aktualisiert.",
        "fr": "{n} appels d’offres publics dont le délai de remise court encore, publiés sur "
              "simap.ch par la Confédération, les cantons et les communes – par ordre d’échéance, "
              "consultables par canton et par branche, mis à jour en règle générale les jours ouvrables.",
        "it": "{n} bandi di gara ancora aperti, pubblicati da Confederazione, Cantoni e Comuni "
              "su simap.ch: ordinati per scadenza, suddivisi per cantone e ramo, aggiornati di norma "
              "nei giorni feriali.",
        "en": "{n} public tenders with a deadline still open, published by the Confederation, "
              "cantons and communes on simap.ch – sorted by deadline, grouped by canton and "
              "industry, usually updated on working days.",
    },
    # no heading may promise a search the page does not have ("Ausschreibungen suchen: So
    # funktioniert es"; audit 13.10.2026)
    "open_howto_h2": {
        "de": "So ist die Liste aufgebaut",
        "fr": "Comment cette liste est organisée",
        "it": "Come è organizzato l’elenco",
        "en": "How this list is organised",
    },
    "open_howto": {
        "de": "Die Tabelle zeigt die Ausschreibungen mit der nächsten Eingabefrist zuerst. Jede "
              "Zeile führt zur Ausschreibung mit Auftraggeber, Frist, Bereich (CPV-Code nach der "
              "EU-weit einheitlichen Einteilung der Leistungen) und dem Link zur amtlichen "
              "Publikation. Über die Kantonsseiten finden Sie Ausschreibungen in Ihrer Region, "
              "über die Branchenseiten Ausschreibungen für Ihr Gewerbe: Bauarbeiten, Planung, "
              "IT, Versicherungen, Fahrzeuge und mehr. Die Daten stammen von der amtlichen "
              "Plattform simap.ch und werden in der Regel werktags aktualisiert, nachdem simap.ch die "
              "Publikationen des Tages freigegeben hat.",
        "fr": "Le tableau présente d’abord les appels d’offres dont le délai est le plus proche. "
              "Chaque ligne ouvre la fiche de l’appel d’offres : adjudicateur, délai, domaine "
              "(code CPV) et lien vers la publication officielle. Les pages cantonales regroupent les "
              "appels d’offres de votre région, les pages par branche ceux de votre métier : "
              "construction, études, informatique, assurances, véhicules, etc. Les données "
              "proviennent de la plateforme officielle simap.ch et sont mises à jour en règle "
              "générale les jours ouvrables, après que simap.ch a mis en ligne les publications du jour.",
        "it": "La tabella mostra per primi i bandi con la scadenza più vicina. Ogni riga rimanda "
              "alla scheda del bando, con committente, scadenza, categoria (codice CPV) e link alla "
              "pubblicazione ufficiale. Nelle pagine cantonali trova i bandi della sua "
              "regione, in quelle per ramo i bandi della sua attività: edilizia, progettazione, "
              "informatica, assicurazioni, veicoli e altro. I dati provengono dalla piattaforma "
              "ufficiale simap.ch e sono aggiornati di norma nei giorni feriali, dopo che simap.ch ha "
              "reso disponibili le pubblicazioni del giorno.",
        "en": "The table lists the tenders with the nearest deadline first. Each row leads to "
              "the tender, with the contracting authority, the deadline, the category (CPV code) and "
              "a link to the official publication. Canton pages list the tenders in your region; "
              "industry pages list those in your line of work: construction, engineering, IT, "
              "insurance, vehicles and more. The data comes from simap.ch, the official "
              "platform, and is usually refreshed on working days, after simap.ch releases the day’s "
              "publications.",
    },
    "open_by_canton_h2": {
        "de": "Offene Ausschreibungen nach Kanton", "fr": "Appels d’offres en cours par canton",
        "it": "Bandi aperti per cantone", "en": "Open tenders by canton",
    },
    "open_canton_lede": {
        "de": "Klicken Sie auf einen Kanton, um seine offenen Ausschreibungen nach Eingabefrist geordnet "
              "zu sehen.",
        "fr": "Cliquez sur un canton pour voir ses appels d’offres en cours, par ordre d’échéance.",
        "it": "Clicchi su un cantone per vederne i bandi aperti, ordinati per scadenza.",
        "en": "Click a canton to see its open tenders, sorted by deadline.",
    },
    "open_by_sector_h2": {
        "de": "Ausschreibungen nach Branche", "fr": "Appels d'offres par branche",
        "it": "Bandi per ramo", "en": "Tenders by industry",
    },
    "open_sector_title": {
        "de": "{name}: {n}",
        "fr": "{name} : {n}",
        "it": "{name}: {n}",
        "en": "{name}: {n}",
    },
    # an industry with nothing open (audit 7.3: "Bergbau und Metalle: 0 offene Ausschreibungen")
    "open_sector_title_none": {
        "de": "{name}: zurzeit keine offene Ausschreibung",
        "fr": "{name} : aucun appel d’offres en cours",
        "it": "{name}: nessun bando aperto",
        "en": "{name}: no open tenders",
    },
    "feed_title": {"de": "Neue Ausschreibungen: {scope} – Öffentliche Aufträge Schweiz",
                   "fr": "Nouveaux appels d’offres : {scope} – Marchés publics suisses",
                   "it": "Nuovi bandi: {scope} – Appalti pubblici svizzeri",
                   "en": "New tenders: {scope} – Swiss Public Contracts"},
    "feed_all": {"de": "Schweiz", "fr": "Suisse", "it": "Svizzera", "en": "Switzerland"},
    "feed_link": {"de": "RSS-Feed", "fr": "Flux RSS", "it": "Feed RSS", "en": "RSS feed"},
    "abo_cta": {"de": "Kostenloses E-Mail-Abo einrichten",
                "fr": "Créer une alerte e-mail gratuite",
                "it": "Attiva l’avviso e-mail gratuito",
                "en": "Set up a free email alert"},
    # No "every day" / "täglich" about the e-mail: the sender writes only on days with new matching
    # tenders (08.10.2026)
    "abo_title": {"de": "Ausschreibungen per E-Mail-Abo oder RSS",
                  "fr": "Appels d’offres par alerte e-mail ou RSS",
                  "it": "Bandi via avviso e-mail o feed RSS",
                  "en": "Tenders by email alert or RSS feed"},
    "abo_desc": {"de": "Kostenloses E-Mail-Abo für neue öffentliche Ausschreibungen in der Schweiz, nach Kanton "
                       "und Branche – oder als RSS-Feed. Quelle: simap.ch.",
                 "fr": "Alerte e-mail gratuite pour les nouveaux appels d’offres publics en Suisse, par canton "
                       "et par branche – ou par flux RSS. Source : simap.ch.",
                 "it": "Avviso e-mail gratuito per i nuovi bandi pubblici in Svizzera, per cantone e ramo – "
                       "oppure via feed RSS. Fonte: simap.ch.",
                 "en": "Free email alerts for new public tenders in Switzerland, by canton and industry – or "
                       "an RSS feed. Source: simap.ch."},
    "abo_h1": {"de": "E-Mail-Abo für neue Ausschreibungen",
               "fr": "Alerte e-mail pour les nouveaux appels d’offres",
               "it": "Avviso e-mail per i nuovi bandi",
               "en": "Email alerts for new tenders"},
    "abo_lead": {"de": "An jedem Werktag erscheinen auf simap.ch neue Ausschreibungen. Wählen Sie Kantone und "
                       "Branchen und lassen Sie sich die passenden zuschicken — kostenlos, ohne Konto.",
                 "fr": "Chaque jour ouvrable, de nouveaux appels d'offres paraissent sur simap.ch. Choisissez les "
                       "cantons et les branches qui vous intéressent : nous vous envoyons les nouveaux appels "
                       "d’offres correspondants — gratuitement, sans compte.",
                 "it": "Ogni giorno feriale su simap.ch vengono pubblicati nuovi bandi. Scelga i cantoni "
                       "e i rami che le interessano: le invieremo i nuovi bandi corrispondenti – gratuitamente, "
                       "senza account.",
                 "en": "New tenders appear on simap.ch on every working day. Choose your cantons and "
                       "industries, and we will send you the new ones – free, no account needed."},
    "abo_rss_h2": {"de": "Per RSS-Feed (bei jeder Aktualisierung, ohne Anmeldung)",
                   "fr": "Par flux RSS (à chaque mise à jour, sans inscription)",
                   "it": "Via feed RSS (a ogni aggiornamento, senza iscrizione)",
                   "en": "By RSS feed (at every update, no sign-up)"},
    "abo_rss_text": {"de": "Jede Kantons- und Branchenseite hat einen Feed. Fügen Sie die Adresse in Ihren "
                           "Feed-Reader, in Outlook (RSS-Abonnements) oder in einen RSS-zu-E-Mail-Dienst ein.",
                     "fr": "Chaque page de canton et de branche a son propre flux. Ajoutez son "
                           "adresse à votre lecteur de flux, à Outlook (abonnements RSS) ou à un "
                           "service qui transforme les flux RSS en e-mails.",
                     "it": "Ogni pagina cantonale e di ramo ha il proprio feed. Aggiunga "
                           "l’indirizzo al suo lettore di feed, a Outlook (abbonamenti RSS) o a "
                           "un servizio che inoltra i feed RSS via e-mail.",
                     "en": "Every canton and industry page has its own feed. Add its address to "
                           "your feed reader, to Outlook (RSS subscriptions) or to an "
                           "RSS-to-email service."},
    "abo_rss_all": {"de": "Alle neuen Ausschreibungen der Schweiz", "fr": "Tous les nouveaux appels d'offres suisses",
                    "it": "Tutti i nuovi bandi svizzeri", "en": "All new Swiss tenders"},
    "abo_by_canton": {"de": "Feeds nach Kanton", "fr": "Flux par canton", "it": "Feed per cantone", "en": "Feeds by canton"},
    "abo_by_sector": {"de": "Feeds nach Branche", "fr": "Flux par branche", "it": "Feed per ramo", "en": "Feeds "
                                                                                                            "by "
                                                                                                            "industry"},
    "abo_check_title": {"de": "Fast geschafft: Bitte bestätigen Sie Ihre E-Mail-Adresse", "fr": "Plus qu’une "
                                                                               "étape : "
                                                                               "confirmez votre "
                                                                               "adresse e-mail",
                        "it": "Quasi fatto: confermi il suo indirizzo e-mail", "en": "Almost done: please "
                                                                      "confirm your email address"},
    "abo_check": {"de": "Wir haben Ihnen eine E-Mail geschickt. Klicken Sie auf den Bestätigungslink darin – erst "
                        "dann ist Ihr E-Mail-Abo aktiv.",
                  "fr": "Nous vous avons envoyé un e-mail. Cliquez sur le lien de confirmation qu’il contient – "
                        "votre alerte e-mail ne sera active qu’après ce clic.",
                  "it": "Le abbiamo inviato un’e-mail. Clicchi sul link di conferma che contiene: solo allora "
                        "l’avviso e-mail sarà attivo.",
                  "en": "We have sent you an email. Click the confirmation link in it – your email alert starts "
                        "only after that."},
    "abo_ok_title": {"de": "Abo bestätigt", "fr": "Abonnement confirmé", "it": "Iscrizione confermata",
                     "en": "Subscription confirmed"},
    "abo_ok": {"de": "Ihr E-Mail-Abo ist aktiv. Abmelden können Sie sich jederzeit über den Link am Ende "
                     "jeder E-Mail.",
               "fr": "Votre alerte e-mail est active. Vous pouvez vous désabonner à tout moment par le lien au "
                     "bas de chaque e-mail.",
               "it": "Il suo avviso e-mail è attivo. Può cancellarsi in qualsiasi momento con il link in fondo "
                     "a ogni e-mail.",
               "en": "Your email alert is active. You can unsubscribe at any time with the link at the bottom "
                     "of any email."},
    "abo_back": {"de": "Zurück zum E-Mail-Abo", "fr": "Retour à l’alerte e-mail", "it": "Torna all’avviso e-mail",
                 "en": "Back to email alerts"},
    # the form's heading names the alert as the links to it do; the button says the verb (abonnieren /
    # s'abonner / iscriversi / subscribe) and that it is free (step 5, owner's terminology)
    "abo_form_h2": {"de": "E-Mail-Abo einrichten", "fr": "Créer une alerte e-mail", "it": "Attivare l’avviso e-mail",
                    "en": "Set up an email alert"},
    "abo_form_email": {"de": "E-Mail-Adresse", "fr": "Adresse e-mail", "it": "Indirizzo e-mail", "en": "Email "
                                                                                                       "address"},
    "abo_form_cantons": {"de": "Kantone (keine Auswahl = ganze Schweiz)", "fr": "Cantons (aucun choix = toute la Suisse)",
                         "it": "Cantoni (nessuna scelta = tutta la Svizzera)", "en": "Cantons "
                                                                                     "(none "
                                                                                     "selected = "
                                                                                     "all of "
                                                                                     "Switzerland)"},
    "abo_form_sectors": {"de": "Branchen (keine Auswahl = alle)", "fr": "Branches (aucun choix = toutes)",
                         "it": "Rami (nessuna scelta = tutti)", "en": "Industries (none "
                                                                         "selected = all)"},
    "abo_form_submit": {"de": "Kostenlos abonnieren", "fr": "S'abonner gratuitement", "it": "Iscriviti gratuitamente",
                        "en": "Subscribe free"},
    # an e-mail only on a day with new matching tenders: "an jedem Werktag eine E-Mail" promised one
    # every working day, and none goes out without a match (08.10.2026)
    "abo_form_consent": {"de": "Sie erhalten zuerst eine E-Mail mit einem Bestätigungslink; erst "
                               "danach ist das Abo aktiv. Von da an erhalten Sie eine E-Mail, wenn "
                               "neue Ausschreibungen erscheinen, die zu Ihrer Auswahl passen – an "
                               "Tagen ohne solche Ausschreibungen keine. Abmelden können Sie sich "
                               "jederzeit über den Link in jeder E-Mail. Anmeldung und Versand "
                               "über Brevo (EU).",
                         "fr": "Vous recevrez d’abord un e-mail contenant un lien de "
                               "confirmation : l’alerte ne sera active qu’après votre clic. "
                               "Ensuite, un e-mail vous présentera les nouveaux appels d’offres "
                               "correspondant à votre sélection, les jours où il en paraît ; les "
                               "autres jours, vous n’en recevrez pas. Vous "
                               "pouvez vous désabonner à tout moment grâce au lien présent dans "
                               "chaque e-mail. L’inscription et l’envoi passent par Brevo (UE).",
                         "it": "Riceverà prima un’e-mail con un link di conferma: l’avviso "
                               "si attiva solo dopo il clic su quel link. In seguito riceverà "
                               "un’e-mail nei giorni in cui escono nuovi bandi corrispondenti alla "
                               "sua scelta; negli altri giorni nessuna. Può cancellarsi in "
                               "qualsiasi momento con il link presente in ogni e-mail. Iscrizione "
                               "e invio tramite Brevo (UE).",
                         "en": "You will first receive an email with a confirmation link; your "
                               "email alert starts only once you click it. After that, you will "
                               "receive an email on days when new tenders matching your selection "
                               "appear, and none on other days. "
                               "You can unsubscribe at any time via the link in every email. "
                               "Subscriptions and sending are handled by Brevo (EU)."},
    "abo_form_sending": {"de": "Wird gesendet …", "fr": "Envoi en cours…", "it": "Invio in "
                                                                                  "corso…", "en": "Sending…"},
    "abo_form_ok": {"de": "Fast geschafft: Bitte klicken Sie auf den Link in der E-Mail, die wir Ihnen gerade geschickt haben.",
                    "fr": "Plus qu’une étape : cliquez sur le lien contenu dans l’e-mail que "
                          "nous venons de vous envoyer.",
                    "it": "Quasi fatto: clicchi sul link nell’e-mail che le abbiamo appena "
                          "inviato.",
                    "en": "Almost done: please click the link in the email we have just sent you."},
    "abo_form_err": {"de": "Die Anmeldung ist fehlgeschlagen. Bitte prüfen Sie die E-Mail-Adresse oder "
                           "schreiben Sie an {mail}.",
                     "fr": "L’inscription n’a pas abouti. Vérifiez l’adresse e-mail ou écrivez à "
                           "{mail}.",
                     "it": "Iscrizione non riuscita. Controlli l’indirizzo e-mail o scriva ad "
                           "{mail}.",
                     "en": "Subscription failed. Please check the email address or write to {mail}."},
    "open_kpi_open": {"de": "offene Ausschreibungen", "fr": "appels d’offres en cours",
                      "it": "bandi aperti", "en": "open tenders"},
    "open_kpi_cantons": {"de": "Kantone mit offenen Ausschreibungen", "fr": "cantons avec des appels d’offres en cours",
                         "it": "cantoni con bandi aperti", "en": "cantons with open tenders"},
    # the industries that HAVE an open tender (41 of the 45 on 14.10.2026), like the canton tile beside it
    "open_kpi_sectors": {"de": "Branchen mit offenen Ausschreibungen", "fr": "branches avec des appels d’offres en cours",
                         "it": "rami con bandi aperti", "en": "industries with open tenders"},
    "open_kpi_next": {"de": "nächste Eingabefrist", "fr": "prochain délai",
                      "it": "prossima scadenza", "en": "next deadline"},
    "cmp_h2": {"de": "simap.ch und dieses Register",
               "fr": "simap.ch et ce registre",
               "it": "simap.ch e questo registro",
               "en": "simap.ch and this register"},
    "cmp_lead": {"de": "simap.ch ist die amtliche Plattform und bleibt die massgebende Quelle. "
                       "Dieses Register liest sie regelmässig aus und beantwortet zusätzlich Fragen, "
                       "die sich dort nicht stellen lassen.",
                 "fr": "simap.ch est la plateforme officielle et reste la source déterminante. "
                       "Ce registre la consulte régulièrement et répond en outre à des questions "
                       "que l’on ne peut pas y poser.",
                 "it": "simap.ch è la piattaforma ufficiale e resta la fonte che fa fede. Questo "
                       "registro ne riprende regolarmente i dati e risponde anche a domande che "
                       "su simap.ch non si possono porre.",
                 "en": "simap.ch is the official platform and remains the authoritative source. "
                       "This register reads it regularly and additionally answers questions that "
                       "cannot be asked there."},
    "cmp_us": {"de": "auftragsregister.ch", "fr": "auftragsregister.ch", "it": "auftragsregister.ch",
               "en": "auftragsregister.ch"},
    "cmp_yes": {"de": "ja", "fr": "oui", "it": "sì", "en": "yes"},
    "cmp_no": {"de": "nein", "fr": "non", "it": "no", "en": "no"},
    "cmp_link": {"de": "verweist darauf", "fr": "y renvoie", "it": "vi rimanda",
                 "en": "links to it"},
    "cmp_acct": {"de": "mit Konto", "fr": "avec un compte", "it": "con un account",
                 "en": "with an account"},
    "cmp_partly": {"de": "teilweise", "fr": "en partie", "it": "in parte", "en": "partly"},
    "cmp_r1": {"de": "Amtliche, rechtlich massgebende Publikation",
               "fr": "Publication officielle et juridiquement déterminante",
               "it": "Pubblicazione ufficiale, con valore giuridico",
               "en": "Official, legally authoritative publication"},
    "cmp_r2": {"de": "Offene Ausschreibungen auf simap.ch",
               "fr": "Appels d’offres en cours publiés sur simap.ch",
               "it": "Bandi aperti pubblicati su simap.ch", "en": "Open tenders published on simap.ch"},
    "cmp_r3": {"de": "Zuschläge pro Unternehmen zusammengeführt",
               "fr": "Adjudications regroupées par entreprise",
               "it": "Aggiudicazioni raggruppate per impresa",
               "en": "Awards grouped by company"},
    "cmp_r4": {"de": "Wer hat vergleichbare Aufträge gewonnen – und zu welchem Betrag?",
               "fr": "Qui a remporté des marchés comparables, et pour quel montant ?",
               "it": "Chi ha vinto appalti simili e per quale importo?",
               "en": "Who won similar contracts, and for how much?"},
    "cmp_r5": {"de": "Auswertungen nach Kanton, Branche und Monat",
               "fr": "Analyses par canton, par branche et dans le temps",
               "it": "Analisi per cantone, ramo e andamento nel tempo",
               "en": "Analysis by canton, industry and over time"},
    "cmp_r6": {"de": "RSS-Feed pro Kanton und Branche",
               "fr": "Flux RSS par canton et par branche",
               "it": "Feed RSS per cantone e ramo",
               "en": "RSS feed for each canton and industry"},
    "cmp_r7": {"de": "E-Mail-Abo nach eigener Auswahl",
               "fr": "Alerte e-mail selon vos propres critères",
               "it": "Avviso e-mail secondo i propri criteri",
               "en": "Email alerts matching your own filters"},
    "cmp_r8": {"de": "Nutzung ohne Konto", "fr": "Utilisation sans compte",
               "it": "Uso senza account", "en": "Use without an account"},
    "open_sector_desc": {
        "de": "{n} in der Branche «{name}» (CPV {code}) aus der ganzen Schweiz, nach "
              "Eingabefrist geordnet.",
        "fr": "{n} en Suisse dans la branche « {name} » (CPV {code}), par ordre d’échéance.",
        "it": "{n} nel ramo «{name}» (CPV {code}) in tutta la Svizzera, in ordine di scadenza.",
        "en": "{n} across Switzerland in the “{name}” industry (CPV {code}), sorted by deadline.",
    },
    "open_canton_title": {"de": "Offene Ausschreibungen im Kanton {name}",
                          "fr": "Appels d’offres dans le canton {of}",
                          "it": "Bandi aperti nel Canton {name}",
                          "en": "Open tenders in the canton of {name}"},
    "open_canton_t1": {"de": "Ausschreibungen im Kanton {name}: {c}",
                       "fr": "Appels d’offres dans le canton {of} : {c}",
                       "it": "Bandi di gara nel Canton {name}: {c}",
                       "en": "Public tenders in the canton of {name}: {c}"},
    "open_canton_t2": {"de": "Ausschreibungen Kanton {name}: {c}",
                       "fr": "Appels d’offres du canton {of} : {c}",
                       "it": "Bandi nel Canton {name}: {c}",
                       "en": "Tenders in the canton of {name}: {c}"},
    "open_canton_t3": {"de": "Ausschreibungen {name}: {c}", "fr": "Appels d’offres {name} : {c}",
                       "it": "Bandi {name}: {c}", "en": "Tenders in {name}: {c}"},
    "open_sector_t1": {"de": "{word} in der Schweiz: {k} offen",
                       "fr": "{word} en Suisse : {k} en cours",
                       "it": "{word} in Svizzera: {k} aperti",
                       "en": "{word} in Switzerland: {k} open"},
    "open_sector_t2": {"de": "{word} in der Schweiz: {k} offen", "fr": "{word} en Suisse : {k} en cours",
                       "it": "{word} in Svizzera: {k} aperti", "en": "{word} in Switzerland: {k} open"},
    "open_sector_desc_word": {
        "de": "Die {k} offenen {w} der Schweiz auf simap.ch, nach Eingabefrist und Kanton geordnet. "
              "Kostenlos, ohne Konto, mit E-Mail-Abo.",
        "fr": "Les {k} {w} en cours en Suisse (simap.ch), classés par délai et par canton. Gratuit, "
              "sans compte, avec alerte e-mail.",
        "it": "I {k} {w} aperti in Svizzera (simap.ch), in ordine di scadenza e per cantone. Gratuito, "
              "senza account, con avviso e-mail.",
        "en": "The {k} open {w} in Switzerland on simap.ch, sorted by deadline and canton. Free, no "
              "account, with email alerts.",
    },
    "open_canton_h1": {
        "de": "Offene Ausschreibungen im Kanton {name}",
        "fr": "Appels d’offres en cours dans le canton {of}",
        "it": "Bandi aperti nel Canton {name}",
        "en": "Open public tenders in the canton of {name}",
    },
    "open_canton_desc": {
        "de": "{n} im Kanton {name}: nach Eingabefrist geordnet, werktags aktualisiert, mit kostenlosem "
              "E-Mail-Abo, ohne Konto.",
        "fr": "{n} dans le canton {of} : classés par délai, mis à jour les jours ouvrables, alerte e-mail "
              "gratuite, sans compte.",
        "it": "{n} nel Canton {name}: in ordine di scadenza, aggiornati nei giorni feriali, con avviso "
              "e-mail gratuito e senza account.",
        "en": "{n} in the canton of {name}: sorted by deadline, updated on working days, with a free email "
              "alert and no account needed.",
    },
    "desc_deadline": {
        "de": ", Eingabefrist {date}",
        "fr": ", délai de remise : {date}",
        "it": ", scadenza {date}",
        "en": ", submission deadline {date}",
    },
    "desc_won": {
        "de": ", Zuschlag an {who}",
        "fr": ", adjugé à {who}",
        "it": ", aggiudicato a {who}",
        "en": ", awarded to {who}",
    },
    "desc_amount": {
        "de": " für {amount}",
        "fr": " pour {amount}",
        "it": " per {amount}",
        "en": " for {amount}",
    },
    # (", Zuschlag über {amount}" for an award to several firms is gone: it gave the first
    # firm's price as the award's; desc_won_n names how many firms instead, 08.10.2026)
}

# Plural of the central noun, per language.
PLURALS: dict[str, tuple[str, str]] = {
    "de": ("Zuschlag", "Zuschläge"), "fr": ("adjudication", "adjudications"),
    "it": ("aggiudicazione", "aggiudicazioni"), "en": ("award", "awards"),
}


def m(key: str, lang: str, **kw) -> str:
    return META[key][lang].format(**kw)


IDX: dict[str, dict[str, str]] = {
    "companies_h1": {"de": "Unternehmen im Register", "fr": "Entreprises du registre",
                     "it": "Imprese nel registro", "en": "Companies in the register"},
    "companies_lead": {
        "de": "Alle Unternehmen mit mindestens zwei publizierten Zuschlägen, alphabetisch.",
        "fr": "Toutes les entreprises ayant obtenu au moins deux adjudications publiées, par "
              "ordre alphabétique.",
        "it": "Tutte le imprese con almeno due aggiudicazioni pubblicate, in ordine alfabetico.",
        "en": "Every company with at least two published awards, listed alphabetically."},
    "companies_title": {"de": "Unternehmen mit öffentlichen Aufträgen — Verzeichnis",
                        "fr": "Entreprises titulaires de marchés publics — répertoire",
                        "it": "Imprese con appalti pubblici — elenco",
                        "en": "Companies holding public contracts — directory"},
    # the same population as the lead: companies with at least two awards (the home counts
    # every company, 6,278, and a bare "2574 Unternehmen" contradicted it)
    "companies_desc": {
        "de": "Alphabetisches Verzeichnis der {n} Unternehmen mit mindestens zwei auf simap.ch "
              "publizierten Zuschlägen.",
        "fr": "Répertoire alphabétique des {n} entreprises ayant obtenu au moins deux "
              "adjudications publiées sur simap.ch.",
        "it": "Elenco alfabetico delle {n} imprese con almeno due aggiudicazioni pubblicate su "
              "simap.ch.",
        "en": "Alphabetical directory of the {n} companies with at least two awards published "
              "on simap.ch."},
    "buyers_h1": {"de": "Auftraggeber", "fr": "Adjudicateurs", "it": "Committenti",
                  "en": "Contracting authorities"},
    "buyers_lead": {
        "de": "Alle Auftraggeber mit mindestens drei publizierten Zuschlägen, alphabetisch.",
        "fr": "Tous les adjudicateurs ayant publié au moins trois adjudications, par ordre "
              "alphabétique.",
        "it": "Tutti i committenti con almeno tre aggiudicazioni pubblicate, in ordine alfabetico.",
        "en": "Every contracting authority with at least three published awards, listed "
              "alphabetically."},
    "buyers_title": {"de": "Auftraggeber im öffentlichen Beschaffungswesen — Verzeichnis",
                     "fr": "Adjudicateurs des marchés publics — répertoire",
                     "it": "Committenti degli appalti pubblici — elenco",
                     "en": "Contracting authorities in public procurement — directory"},
    "buyers_desc": {
        "de": "Verzeichnis der {n} Auftraggeber mit mindestens drei Zuschlägen, die sie auf simap.ch "
              "publiziert haben.",
        "fr": "Répertoire des {n} adjudicateurs ayant publié au moins trois adjudications sur "
              "simap.ch.",
        "it": "Elenco dei {n} committenti con almeno tre aggiudicazioni pubblicate su simap.ch.",
        "en": "Directory of the {n} contracting authorities with at least three awards published on "
              "simap.ch."},
    "cantons_lead": {"de": "Publizierte Zuschläge nach dem Kanton, den die Publikation als Ort der Leistung "
                           "nennt; ohne Angabe nach dem Kanton des Auftraggebers.",
                     "fr": "Adjudications publiées, par canton du lieu d’exécution indiqué dans la "
                           "publication ; à défaut, par canton de l’adjudicateur.",
                     "it": "Aggiudicazioni pubblicate per il cantone che la pubblicazione indica come luogo "
                           "di esecuzione; in mancanza, per il cantone del committente.",
                     "en": "Published awards, by the canton the publication gives as the place of "
                           "performance; where it gives none, by the contracting authority’s canton."},
    "cantons_title": {"de": "Öffentliche Aufträge nach Kanton — Übersicht",
                      "fr": "Marchés publics par canton — aperçu",
                      "it": "Appalti pubblici per cantone — panoramica",
                      "en": "Public contracts by canton — overview"},
    "cantons_desc": {
        "de": "Publizierte Zuschläge aus dem öffentlichen Beschaffungswesen der Schweiz, nach Kanton geordnet.",
        "fr": "Adjudications publiées dans les marchés publics suisses, classées par canton.",
        "it": "Aggiudicazioni pubblicate negli appalti pubblici svizzeri, ordinate per cantone.",
        "en": "Published awards from Swiss public procurement, ordered by canton."},
    "sectors_h1": {"de": "Öffentliche Aufträge nach Bereich", "fr": "Marchés publics par domaine",
                   "it": "Appalti pubblici per categoria", "en": "Public contracts by category"},
    "sectors_lead": {"de": "Publizierte Zuschläge nach Bereich. Die Bereiche folgen dem CPV, der "
                           "EU-weit einheitlichen Einteilung der Leistungen.",
                     "fr": "Adjudications publiées par domaine. Les domaines suivent le CPV, le "
                           "vocabulaire commun pour les marchés publics de l’UE.",
                     "it": "Aggiudicazioni pubblicate per categoria. Le categorie seguono il CPV, il "
                           "vocabolario comune per gli appalti pubblici dell’UE.",
                     "en": "Published awards by category. Categories follow the CPV, the EU’s "
                           "Common Procurement Vocabulary."},
    "sectors_title": {"de": "Öffentliche Aufträge nach Bereich — CPV-Übersicht",
                      "fr": "Marchés publics par domaine — aperçu CPV",
                      "it": "Appalti pubblici per categoria — panoramica CPV",
                      "en": "Public contracts by category — CPV overview"},
    "sectors_desc": {
        "de": "Publizierte Zuschläge nach Bereich (CPV), mit den Unternehmen, die sie erhalten "
              "haben.",
        "fr": "Adjudications publiées par domaine (CPV), avec les entreprises qui les ont obtenues.",
        "it": "Aggiudicazioni pubblicate per categoria (CPV), con le imprese che le hanno ottenute.",
        "en": "Published awards by category (CPV), with the companies that won them."},
    "all_companies": {"de": "Alle Unternehmen", "fr": "Toutes les entreprises",
                      "it": "Tutte le imprese", "en": "All companies"},
    "all_buyers": {"de": "Alle Auftraggeber", "fr": "Tous les adjudicateurs",
                   "it": "Tutti i committenti", "en": "All contracting authorities"},
    "all_cantons": {"de": "Alle Kantone", "fr": "Tous les cantons",
                    "it": "Tutti i cantoni", "en": "All cantons"},
    "all_sectors": {"de": "Alle Bereiche", "fr": "Tous les domaines",
                    "it": "Tutte le categorie", "en": "All categories"},
    "next_deadlines": {"de": "Nächste Eingabefristen", "fr": "Prochains délais",
                       "it": "Prossime scadenze", "en": "Next deadlines"},
    "open_count": {"de": "{n} offen", "fr": "{n} en cours", "it": "{n} bandi aperti",
                   "en": "{n} open"},
    "by_canton": {"de": "Nach Kanton", "fr": "Par canton", "it": "Per cantone",
                  "en": "By canton"},
    "by_sector": {"de": "Nach Bereich", "fr": "Par domaine", "it": "Per categoria",
                  "en": "By category"},
    "awarded_in": {"de": "Vergebene Aufträge im Kanton {c}", "fr": "Marchés adjugés dans le canton {of}",
                   "it": "Appalti aggiudicati nel Canton {c}", "en": "Contracts awarded in the canton of {c}"},
    "all_open": {"de": "Alle offenen Ausschreibungen", "fr": "Tous les appels d’offres en cours",
                 "it": "Tutti i bandi aperti", "en": "All open tenders"},
    "same_sector": {"de": "Aufträge im selben Bereich", "fr": "Marchés du même domaine",
                    "it": "Appalti della stessa categoria", "en": "Awards in the same category"},
    "contracts_in": {"de": "Aufträge im Kanton {c}", "fr": "Marchés du canton {of}",
                     "it": "Altri appalti nel Canton {c}", "en": "Awards in the canton of {c}"},
    "mc_title_home": {
        "de": "Zuschläge pro Monat in der ganzen Schweiz",
        "fr": "Adjudications par mois dans toute la Suisse",
        "it": "Aggiudicazioni al mese in tutta la Svizzera",
        "en": "Awards per month across Switzerland",
    },
    "mc_title_canton": {
        "de": "Zuschläge pro Monat im Kanton {name}",
        "fr": "Adjudications par mois dans le canton {of}",
        "it": "Aggiudicazioni al mese nel Canton {name}",
        "en": "Awards per month in the canton of {name}",
    },
    "mc_title_buyer": {
        "de": "Zuschläge dieses Auftraggebers pro Monat",
        "fr": "Adjudications de cet adjudicateur par mois",
        "it": "Aggiudicazioni di questo committente al mese",
        "en": "This contracting authority’s awards per month",
    },
    "mc_title_sector": {
        "de": "Zuschläge pro Monat in diesem Bereich",
        "fr": "Adjudications par mois dans ce domaine",
        "it": "Aggiudicazioni al mese in questa categoria",
        "en": "Awards per month in this category",
    },
    # computed from complete months only, and it says so: the running month can already be
    # taller than the peak named here (20 chart pages per language on 28.09.2026)
    "mc_takeaway": {
        "de": "Seit {start} im Schnitt {avg} pro Monat; vollständiger Monat mit den meisten "
              "Zuschlägen: {peak_month} ({peak}).",
        "fr": "Depuis {start}, {avg} par mois en moyenne ; mois complet avec le plus "
              "d’adjudications : {peak_month} ({peak}).",
        "it": "Da {start} in media {avg} al mese; mese completo con più aggiudicazioni: "
              "{peak_month} ({peak}).",
        "en": "Since {start}, an average of {avg} a month; busiest complete month: "
              "{peak_month} ({peak}).",
    },
    # two complete months tie for the most awards: both are named
    "mc_takeaway_two": {
        "de": "Seit {start} im Schnitt {avg} pro Monat; vollständige Monate mit den meisten "
              "Zuschlägen: {months} (je {peak}).",
        "fr": "Depuis {start}, {avg} par mois en moyenne ; mois complets avec le plus "
              "d’adjudications : {months} ({peak} chacun).",
        "it": "Da {start} in media {avg} al mese; mesi completi con più aggiudicazioni: "
              "{months} ({peak} ciascuno).",
        "en": "Since {start}, an average of {avg} a month; busiest complete months: "
              "{months} ({peak} each).",
    },
    # three or more tie: the value, and how often it was reached
    "mc_takeaway_many": {
        "de": "Seit {start} im Schnitt {avg} pro Monat; Höchstwert eines vollständigen Monats: "
              "{peak}, erreicht in {k} Monaten.",
        "fr": "Depuis {start}, {avg} par mois en moyenne ; maximum sur un mois complet : "
              "{peak}, atteint à {k} reprises.",
        "it": "Da {start} in media {avg} al mese; massimo di un mese completo: {peak}, "
              "raggiunto in {k} mesi.",
        "en": "Since {start}, an average of {avg} a month; most awards in a complete month: "
              "{peak}, reached in {k} months.",
    },
    "mc_unit": {
        "de": "Anzahl Zuschläge",
        "fr": "Nombre d’adjudications",
        "it": "Numero di aggiudicazioni",
        "en": "Number of awards",
    },
    # Incomplete months are drawn STRIPED. The notes used to call them "lighter", but on the
    # site's dark panel a paler column renders darker: the note named a colour nobody saw.
    # The striped build-up months are the ARCHIVE's coverage, not a market trend: the archive
    # starts in August 2024 and its first months were not collected in full (owner,
    # 28.09.2026). Past tense; {span}/{m} are this chart's own striped months, {start} the
    # archive's first month; one striped column takes the singular.
    # The striped months come first, so "dieser Monat" / "that month" cannot be read as the
    # archive's first month named after it (verifier, 28.09.2026: the Uri chart has no August)
    # "because the archive starts in August" did not explain a striped September or October
    # (verifier, 28.09.2026): the reason is that its first months were incomplete
    "mc_note_start": {
        "de": "Schraffierte Säulen ({span}): Diese Monate sind nur teilweise erfasst – das "
              "Archiv beginnt im {start} und war in den ersten Monaten noch unvollständig.",
        "fr": "Colonnes hachurées ({span}) : mois relevés partiellement ; les données commencent "
              "en {start} et étaient encore incomplètes les premiers mois.",
        "it": "Colonne tratteggiate ({span}): mesi rilevati solo in parte; l’archivio parte da "
              "{start} e nei primi mesi era ancora incompleto.",
        "en": "Striped columns ({span}): these months are only partly covered; the archive "
              "begins in {start} and was still incomplete in its first months.",
    },
    "mc_note_start_one": {
        "de": "Schraffierte Säule ({m}): Dieser Monat ist nur teilweise erfasst – das Archiv "
              "beginnt im {start} und war in den ersten Monaten noch unvollständig.",
        "fr": "Colonne hachurée ({m}) : mois relevé partiellement ; les données commencent en "
              "{start} et étaient encore incomplètes les premiers mois.",
        "it": "Colonna tratteggiata ({m}): mese rilevato solo in parte; l’archivio parte da "
              "{start} e nei primi mesi era ancora incompleto.",
        "en": "Striped column ({m}): this month is only partly covered; the archive begins in "
              "{start} and was still incomplete in its first months.",
    },
    # Italian without "al" before the date: "al 08.10.2026" would need "all’8"
    "mc_note_end": {
        "de": "Schraffierte letzte Säule: laufender Monat (Daten vom {date}).",
        "fr": "Dernière colonne hachurée : mois en cours (état des données : {date}).",
        "it": "Ultima colonna tratteggiata: mese in corso (stato dei dati: {date}).",
        "en": "Striped last column: current month (data as of {date}).",
    },
    # the running month with no award yet: no column is drawn, so no "last column" to point at
    "mc_note_end_zero": {
        "de": "Laufender Monat ({m}): bisher kein Zuschlag (Daten vom {date}).",
        "fr": "Mois en cours ({m}) : aucune adjudication pour l’instant (état des données : {date}).",
        "it": "Mese in corso ({m}): finora nessuna aggiudicazione (stato dei dati: {date}).",
        "en": "Current month ({m}): no awards so far (data as of {date}).",
    },
    # too few data for a chart: one sentence. Several months: the count of months, then the
    # months, each with its count; one month: no list and no repeated count
    "mc_few": {
        "de": "{n} in {k} Monaten: {months}.",
        "fr": "{n} sur {k} mois : {months}.",
        "it": "{n} in {k} mesi: {months}.",
        "en": "{n} in {k} months: {months}.",
    },
    "mc_few_one": {
        "de": "{n}, alle publiziert im {month}.",
        "fr": "{n}, toutes publiées en {month}.",
        "it": "{n}, tutte pubblicate nel mese di {month}.",
        "en": "{n}, all published in {month}.",
    },
    "mc_few_single": {
        "de": "{n}, publiziert im {month}.",
        "fr": "{n}, publiée en {month}.",
        "it": "{n}, pubblicata nel mese di {month}.",
        "en": "{n}, published in {month}.",
    },
    "div_title": {
        "de": "Zuschläge nach Branche",
        "fr": "Adjudications par branche",
        "it": "Aggiudicazioni per ramo",
        "en": "Awards by industry",
    },
    # A Branche (division, 2 digits) groups many Bereiche (exact 8-digit codes); both appear on
    # canton and buyer pages, one above the other, so the lede says how they relate.
    "div_lede_all": {
        "de": "Anzahl Zuschläge je Branche. Branchen sind die Abteilungen des CPV (erste zwei "
              "Ziffern), der EU-weit einheitlichen Einteilung der Leistungen; jede umfasst viele "
              "einzelne Bereiche.",
        "fr": "Nombre d’adjudications par branche. Les branches sont les divisions du CPV, le "
              "vocabulaire commun pour les marchés publics de l’UE ; chacune regroupe de "
              "nombreux domaines détaillés.",
        "it": "Numero di aggiudicazioni per ramo. I rami sono le divisioni del CPV, il vocabolario "
              "comune per gli appalti pubblici dell’UE; ognuno comprende molte categorie specifiche.",
        "en": "Number of awards per industry. Industries are the top-level groups of the CPV, "
              "the EU’s Common Procurement Vocabulary; each covers many specific categories.",
    },
    "div_lede_top": {
        "de": "Anzahl Zuschläge je Branche. Branchen sind die Abteilungen des CPV (erste zwei "
              "Ziffern), der EU-weit einheitlichen Einteilung der Leistungen; jede umfasst viele "
              "einzelne Bereiche. Hier die {k} häufigsten von {total}.",
        "fr": "Nombre d’adjudications par branche. Les branches sont les divisions du CPV, le "
              "vocabulaire commun pour les marchés publics de l’UE ; chacune regroupe de "
              "nombreux domaines détaillés. Voici les {k} plus fréquentes sur {total}.",
        "it": "Numero di aggiudicazioni per ramo. I rami sono le divisioni del CPV, il vocabolario "
              "comune per gli appalti pubblici dell’UE; ognuno comprende molte categorie specifiche. "
              "Qui i rami più frequenti: {k} su {total}.",
        "en": "Number of awards per industry. Industries are the top-level groups of the CPV, "
              "the EU’s Common Procurement Vocabulary; each covers many specific categories. "
              "Shown: the {k} most frequent of {total}.",
    },
    "div_other": {
        "de": "{k} weitere Branchen",
        "fr": "Autres branches ({k})",
        "it": "Altri {k} rami",
        "en": "Other industries ({k})",
    },
    # one industry only: a sentence instead of a single bar at 100 %
    "div_single": {
        "de": "Alle {n} gehören zur Branche «{label}».",
        "fr": "Les {n} relèvent toutes de la branche « {label} ».",
        "it": "Le {n} appartengono tutte al ramo «{label}».",
        "en": "All {n} are in the “{label}” industry.",
    },
    "div_single_one": {
        "de": "Der einzige Zuschlag gehört zur Branche «{label}».",
        "fr": "L’unique adjudication relève de la branche « {label} ».",
        "it": "L’unica aggiudicazione appartiene al ramo «{label}».",
        "en": "The only award is in the “{label}” industry.",
    },
    "detail_sectors": {
        "de": "Einzelne Bereiche (genauer CPV-Code)",
        "fr": "Domaines détaillés (code CPV exact)",
        "it": "Categorie specifiche (codice CPV esatto)",
        "en": "Specific categories (exact CPV code)",
    },
    # the pill for a division's own general code (45000000), under the list that counts the
    # whole division: "Bauarbeiten 2’148" above, "Bauarbeiten (allgemeiner Code) · 758" below
    "tag_general": {
        "de": "{label} (allgemeiner Code)",
        "fr": "{label} (code général)",
        "it": "{label} (codice generico)",
        "en": "{label} (general code)",
    },
    "bands_title": {
        "de": "Wie hoch sind die Zuschläge an {name}?",
        "fr": "Quels sont les montants des adjudications obtenues par {name} ?",
        "it": "Quanto valgono le aggiudicazioni di {name}?",
        "en": "How large are the awards won by {name}?",
    },
    "bands_lede": {
        "de": "Anzahl Zuschläge je Betragsklasse.",
        "fr": "Nombre d’adjudications par tranche de montant.",
        "it": "Numero di aggiudicazioni per fascia d’importo.",
        "en": "Number of awards by amount band.",
    },
    "bands_median": {
        "de": "Typischer Betrag (Median): {m} – die Hälfte der Zuschläge mit zurechenbarem Betrag "
              "liegt darüber, die andere Hälfte darunter.",
        "fr": "Montant typique (médiane) : {m} – la moitié des adjudications dotées d’un montant "
              "attribuable se situe au-dessus de ce montant, l’autre moitié en dessous.",
        "it": "Importo tipico (mediana): {m} – metà delle aggiudicazioni con un importo "
              "attribuibile supera questo valore, l’altra metà resta al di sotto.",
        "en": "Typical amount (median): {m} – half of the awards with an attributable amount are "
              "above this figure, half below.",
    },
    # quotes the last label of lingue.BANDS word for word
    "bands_noown": {
        "de": "«Ohne zurechenbaren Betrag»: kein Betrag publiziert, Betrag in Fremdwährung, "
              "Zuschlag an mehrere Unternehmen oder vermutlicher Einheitspreis.",
        "fr": "« Sans montant attribuable » : montant non publié, montant en devise étrangère, "
              "adjudication attribuée à plusieurs entreprises ou prix probablement unitaire.",
        "it": "«Importo non attribuibile»: importo non pubblicato o in valuta estera, aggiudicazione "
              "attribuita a più imprese oppure probabile prezzo unitario.",
        "en": "“No attributable CHF amount”: no amount published, an amount in a foreign "
              "currency, an award made to several companies, or a probable unit rate.",
    },
    # every award without a CHF amount of its own: a sentence, not five empty bars
    "bands_none": {
        "de": "Keiner der {n} Zuschläge hat einen zurechenbaren Betrag in CHF.",
        "fr": "Aucune des {n} adjudications n’a de montant attribuable en CHF.",
        "it": "Nessuna delle {n} aggiudicazioni ha un importo in CHF attribuibile.",
        "en": "None of the {n} awards has an attributable CHF amount.",
    },
    "largest_h": {
        "de": "Die grössten Zuschläge",
        "fr": "Les adjudications les plus importantes",
        "it": "Le aggiudicazioni maggiori",
        "en": "Largest awards",
    },
    # Italian: genera puts the article before the figure ("il 33%", "l’80%"; step 5); none before "oltre il 99%"
    "largest_share": {
        "de": "Allein der grösste Zuschlag macht {share} der Summe aus.",
        "fr": "À elle seule, la plus importante représente {share} du total.",
        "it": "Da sola, l’aggiudicazione maggiore rappresenta {share} del totale.",
        "en": "The largest award alone accounts for {share} of the total.",
    },
    # a share between 99.5 and 100 %, in prose ("macht mehr als 99 % der Summe aus")
    "over_pct": {
        "de": "mehr als {p}",
        "fr": "plus de {p}",
        "it": "oltre il {p}",
        "en": "more than {p}",
    },
    # an award that names several firms is often a set of separate awards (one per lot,
    # section or framework contract): the notes say "an mehrere Unternehmen", never "gemeinsam".
    # Such an award has no amount to split: simap publishes one price per firm, which the rows
    # below now show ("Betrag nicht aufteilbar" assumed a single amount; 08.10.2026)
    "joint_note": {
        "de": "Nicht in den Summen enthalten sind {k} Zuschläge, die an mehrere Unternehmen "
              "gingen (publiziert ist ein Preis je Unternehmen).",
        "fr": "Les totaux n’incluent pas {k} adjudications attribuées à plusieurs entreprises "
              "(la publication indique un prix par entreprise).",
        "it": "I totali non comprendono {k} aggiudicazioni attribuite a più imprese (la "
              "pubblicazione indica un prezzo per impresa).",
        "en": "Totals exclude {k} awards made to several companies (the publication gives one "
              "price per company).",
    },
    "joint_note_one": {
        "de": "Nicht in den Summen enthalten ist ein Zuschlag, der an mehrere Unternehmen ging "
              "(publiziert ist ein Preis je Unternehmen).",
        "fr": "Une adjudication attribuée à plusieurs entreprises n’est pas comprise dans les "
              "totaux (la publication indique un prix par entreprise).",
        "it": "I totali non comprendono un’aggiudicazione attribuita a più imprese (la "
              "pubblicazione indica un prezzo per impresa).",
        "en": "Totals exclude one award made to several companies (the publication gives one "
              "price per company).",
    },
    "joint_n": {
        "de": "{n} Unternehmen",
        "fr": "{n} entreprises",
        "it": "{n} imprese",
        "en": "{n} companies",
    },
    "open_in": {
        "de": "Im Kanton {c} sind zurzeit {k} Ausschreibungen offen",
        "fr": "Appels d’offres en cours dans le canton {of} : {k}",
        "it": "Bandi aperti nel Canton {c}: {k}",
        "en": "Open tenders in the canton of {c}: {k}",
    },
    "open_in_one": {
        "de": "Im Kanton {c} ist zurzeit 1 Ausschreibung offen",
        "fr": "Appels d’offres en cours dans le canton {of} : 1",
        "it": "Bandi aperti nel Canton {c}: 1",
        "en": "Open tenders in the canton of {c}: 1",
    },
    # what still tells apart lots published under one identical title
    "project_no": {
        "de": "Projekt {n}",
        "fr": "projet {n}",
        "it": "progetto n. {n}",
        "en": "project {n}",
    },
    # the lots of one project on one line of the home's deadline list
    "lots_n": {
        "de": "{n} Lose",
        "fr": "{n} lots",
        "it": "{n} lotti",
        "en": "{n} lots",
    },
}


def i(key: str, lang: str, **kw) -> str:
    return IDX[key][lang].format(**kw) if kw else IDX[key][lang]


# The API's own enum values, as a reader should see them. Printing "open" and "True"
# to a German reader is not a register, it is a database dump.
ENUM: dict[str, dict[str, dict[str, str]]] = {
    "processType": {
        "open": {"de": "Offenes Verfahren", "fr": "Procédure ouverte",
                 "it": "Procedura aperta", "en": "Open procedure"},
        "selective": {"de": "Selektives Verfahren", "fr": "Procédure sélective",
                      "it": "Procedura selettiva", "en": "Selective procedure"},
        "invitation": {"de": "Einladungsverfahren", "fr": "Procédure sur invitation",
                       "it": "Procedura su invito", "en": "Invitation procedure"},
        "direct": {"de": "Freihändiges Verfahren", "fr": "Procédure de gré à gré",
                   "it": "Trattativa privata", "en": "Direct award"},
    },
    "orderType": {
        "construction": {"de": "Bauauftrag", "fr": "Marché de travaux",
                         "it": "Appalto di lavori", "en": "Works contract"},
        "service": {"de": "Dienstleistungsauftrag", "fr": "Marché de services",
                    "it": "Appalto di servizi", "en": "Services contract"},
        "supply": {"de": "Lieferauftrag", "fr": "Marché de fournitures",
                   "it": "Appalto di forniture", "en": "Supply contract"},
    },
    "bool": {
        "True": {"de": "Ja", "fr": "Oui", "it": "Sì", "en": "Yes"},
        "False": {"de": "Nein", "fr": "Non", "it": "No", "en": "No"},
    },
}


def enum(kind: str, value, lang: str) -> str:
    """A reader-facing label, or the raw value when the source used one we do not know
    — showing an unknown code is honest; inventing a translation for it is not."""
    if value is None or value == "":
        return ""
    key = str(value)
    return ENUM.get(kind, {}).get(key, {}).get(lang, key)


IDX["showing_n"] = {
    "de": "Angezeigt werden die {n} Ausschreibungen mit der nächsten Eingabefrist (von insgesamt "
          "{total} offenen); alle übrigen finden Sie auf den Kantonsseiten.",
    "fr": "Cette liste affiche les {n} appels d’offres dont le délai est le plus proche, sur "
          "{total} en cours ; les autres figurent sur les pages cantonales.",
    "it": "Sono elencati i {n} bandi con la scadenza più vicina, su {total} bandi aperti; gli "
          "altri si trovano nelle pagine cantonali.",
    "en": "Showing the {n} tenders with the nearest deadlines, out of {total} open; the others "
          "are on the canton pages.",
}


IDX["firms_cap"] = {
    "de": "Unternehmen mit den meisten Zuschlägen", "fr": "Entreprises ayant obtenu le plus "
                                                          "d’adjudications",
    "it": "Imprese con più aggiudicazioni", "en": "Companies with the most awards",
}


T["imprint"] = {"de": "Impressum", "fr": "Mentions légales", "it": "Note legali",
                "en": "Legal notice"}

T["privacy"] = {"de": "Datenschutz", "fr": "Protection des données",
                "it": "Protezione dei dati", "en": "Privacy"}

# The Impressum, per language. The operator's name and address of contact are injected
# by the generator so they live in one place.
IMP: dict[str, dict] = {
    "de": {
        "title": "Impressum",
        "operator_h": "Betreiber",
        "operator_note": "Privatperson, Schweiz",
        "contact_h": "Kontakt",
        "paras": [
            ("Unabhängiges Projekt",
             "Öffentliche Aufträge Schweiz ist ein privates, unabhängiges Projekt. Es "
             "ist kein amtliches Register und steht in keiner Verbindung zu simap.ch "
             "oder zu einer Behörde von Bund, Kantonen oder Gemeinden."),
            ("Datengrundlage",
             "Alle Inhalte beruhen auf amtlichen Publikationen der Plattform simap.ch "
             "und werden gemäss deren API-Nutzungsbedingungen inhaltlich unverändert "
             "wiedergegeben. Massgebend sind ausschliesslich die dort veröffentlichten "
             "Daten."),
            ("Keine Gewähr",
             "Für die Vollständigkeit und Richtigkeit der Aufbereitung wird keine Gewähr "
             "übernommen. Hinweise auf Fehler sind per E-Mail willkommen."),
        ],
    },
    "fr": {
        "title": "Mentions légales",
        "operator_h": "Exploitant",
        "operator_note": "Particulier, Suisse",
        "contact_h": "Contact",
        "paras": [
            ("Projet indépendant",
             "« Marchés publics suisses » est un projet privé et indépendant. Il ne s’agit pas "
             "d’un registre officiel, et le projet n’a aucun lien avec simap.ch ni avec aucune "
             "autorité fédérale, cantonale ou communale."),
            ("Source des données",
             "Toutes les informations reposent sur les publications officielles de la plateforme "
             "simap.ch et sont restituées sans modification de leur contenu, conformément aux "
             "conditions d’utilisation de l’API de simap.ch. Seules les données qui y sont "
             "publiées font foi."),
            ("Absence de garantie",
             "L’exhaustivité et l’exactitude de la présentation ne sont pas garanties. Les "
             "erreurs peuvent être signalées par e-mail."),
        ],
    },
    "it": {
        "title": "Note legali",
        "operator_h": "Gestore",
        "operator_note": "Privato, Svizzera",
        "contact_h": "Contatto",
        "paras": [
            ("Progetto indipendente",
             "Appalti pubblici svizzeri è un progetto privato e indipendente. Non è un "
             "registro ufficiale e non ha alcun legame con simap.ch né con autorità "
             "federali, cantonali o comunali."),
            ("Fonte dei dati",
             "Tutti i contenuti si basano sulle pubblicazioni ufficiali della piattaforma "
             "simap.ch e sono riprodotti senza modificarne il contenuto, conformemente alle "
             "condizioni d’uso dell’API di simap.ch. Fanno fede esclusivamente i dati ivi "
             "pubblicati."),
            ("Nessuna garanzia",
             "Non si garantiscono né la completezza né l’esattezza della rielaborazione. "
             "Eventuali errori possono essere segnalati via e-mail."),
        ],
    },
    "en": {
        "title": "Legal notice",
        "operator_h": "Operator",
        "operator_note": "Private individual, Switzerland",
        "contact_h": "Contact",
        "paras": [
            ("Independent project",
             "Swiss Public Contracts is a private, independent project. It is not an "
             "official register and has no connection to simap.ch or to any federal, "
             "cantonal or communal authority."),
            ("Data source",
             "All content is based on the official publications of the simap.ch platform and is "
             "reproduced without any change to its content, in accordance with simap.ch’s API "
             "terms of use. Only the data published there is authoritative."),
            ("No guarantee",
             "No guarantee is given that this presentation is complete or correct. Please report "
             "any errors by email."),
        ],
    },
}


# The site reproduces official award publications. Most awardees are companies, but a
# measured 3.3% of the 10,547 names are natural persons (sole traders), so the site
# does process personal data and owes a notice under the revised Swiss DSG.
PRIV: dict[str, dict] = {
    "de": {
        "title": "Datenschutz",
        "operator_h": "Verantwortliche Person",
        "operator_note": "Privatperson, Schweiz",
        "contact_h": "Kontakt",
        "paras": [
            ("Welche Personendaten enthält diese Website?",
             "Diese Website gibt amtliche Publikationen von simap.ch wieder. Die meisten "
             "genannten Anbieterinnen und Anbieter sind Unternehmen. Ein Teil der "
             "Zuschlagsempfängerinnen und -empfänger sind jedoch Einzelfirmen und "
             "Selbständigerwerbende: In diesen Fällen erscheint der Name einer natürlichen Person "
             "zusammen mit dem Auftrag, dem Betrag und dem Auftraggeber. Kontaktpersonen, E-Mail-Adressen und Telefonnummern "
             "werden nicht gesondert erfasst; stehen solche Angaben im Text einer Ausschreibung, "
             "werden sie unverändert von simap.ch übernommen."),
            ("Zweck und Rechtfertigung",
             "Zweck ist es, bereits amtlich veröffentlichte Vergabeentscheide auffindbar "
             "und vergleichbar zu machen. Die Daten wurden von Behörden des Bundes, der "
             "Kantone und der Gemeinden im Rahmen des öffentlichen Beschaffungsrechts "
             "publiziert, sind allgemein zugänglich und werden gemäss den "
             "API-Nutzungsbedingungen von simap.ch inhaltlich unverändert wiedergegeben. "
             "Die Bearbeitung stützt sich auf das überwiegende Interesse an der "
             "Transparenz öffentlicher Beschaffungen."),
            ("Daten über Besucherinnen und Besucher",
             "Diese Website setzt keine Cookies, verwendet keine Analyse- oder "
             "Tracking-Dienste und bindet keine Skripte oder Schriften von Dritten ein. "
             "Es bestehen keine Benutzerkonten. Das einzige Formular ist die freiwillige Anmeldung für "
             "das E-Mail-Abo (siehe unten). "
             "Die Website wird über GitHub Pages ausgeliefert; der Hosting-Anbieter kann "
             "im Rahmen des Betriebs technische Verbindungsdaten wie IP-Adressen in "
             "eigenen Server-Logs erfassen."),
            ("E-Mail-Abo und RSS-Feeds",
             "Wer neue Ausschreibungen per E-Mail erhalten möchte, abonniert sie über das Formular "
             "auf der Seite des E-Mail-Abos. Das Abo wird erst "
             "aktiv, wenn der Bestätigungslink in der zugestellten E-Mail angeklickt wird "
             "(Double-Opt-in). Bearbeitet werden die E-Mail-Adresse, die gewählten Kantone und "
             "Branchen, die Sprache, der Zeitpunkt und die IP-Adresse der Bestätigung sowie während "
             "höchstens 45 Tagen die Liste der bereits zugestellten Ausschreibungen, damit keine "
             "Ausschreibung doppelt verschickt wird. Alle diese Daten werden ausschliesslich für "
             "den Versand der Abo-E-Mails bearbeitet; Grundlage ist Ihre eigene "
             "Anmeldung. Die E-Mails enthalten ein Zählpixel und Links, die über einen Server "
             "von Brevo laufen; Brevo kann dabei Öffnungen und Klicks erfassen. Sie können das "
             "verhindern, indem Sie das automatische Laden von Bildern ausschalten und die "
             "Ausschreibungen direkt auf auftragsregister.ch aufrufen. Abmelden können Sie sich "
             "jederzeit über den Link in jeder E-Mail oder per E-Mail mit dem Betreff «Stop»; "
             "danach entfernen wir Sie innert 30 Tagen aus der Verteilerliste und löschen die "
             "Liste der zugestellten Ausschreibungen. Bei Brevo bleiben Ihr Kontakteintrag "
             "(unter anderem E-Mail-Adresse und Zeitpunkt von Anmeldung und Bestätigung), der "
             "Vermerk der Abmeldung und die Versandprotokolle der bereits zugestellten E-Mails "
             "bestehen, damit Sie sicher keine weiteren E-Mails erhalten. Die Daten werden nicht "
             "verkauft, nicht an Dritte zu deren eigenen Zwecken weitergegeben und nicht für andere "
             "Zwecke verwendet. In unserem Auftrag bearbeiten sie: Brevo (Sendinblue SAS, Paris, EU) "
             "für Anmeldung und Versand sowie, für E-Mails an abo@auftragsregister.ch (auch "
             "Fehlermeldungen), ImprovMX Inc. (USA), das sie weiterleitet, und Google LLC, bei dem "
             "das Postfach liegt (Gmail). Die RSS-Feeds erfordern keine Anmeldung und übermitteln "
             "uns keine Personendaten."),
            ("Archiv und Aufbewahrung",
             "Der Datenbestand wird in der Regel werktags mit den Daten von simap.ch aktualisiert. Ältere "
             "Publikationen bleiben als Archiv erhalten, auch wenn sie über die Schnittstelle "
             "von simap.ch nicht mehr abgefragt werden können."),
            ("Ihre Rechte",
             "Sie können jederzeit Auskunft über die zu Ihrer Person bearbeiteten Daten "
             "verlangen sowie deren Berichtigung oder Löschung beantragen und der Bearbeitung "
             "widersprechen. Eine kurze E-Mail an die oben genannte Adresse genügt; Anliegen "
             "werden ohne Kostenfolge behandelt. Massgebend bleibt die Publikation auf simap.ch: "
             "Eine Berichtigung dort sollte zusätzlich bei der publizierenden Behörde verlangt "
             "werden."),
        ],
    },
    "fr": {
        "title": "Protection des données",
        "operator_h": "Responsable du traitement",
        "operator_note": "Particulier, Suisse",
        "contact_h": "Contact",
        "paras": [
            ("Quelles données personnelles figurent sur ce site ?",
             "Ce site reproduit des publications officielles de simap.ch. La plupart des "
             "adjudicataires sont des entreprises. Certains sont toutefois des raisons "
             "individuelles ou des indépendants : dans ces cas, le nom d'une personne physique "
             "apparaît avec le marché, le montant et l'adjudicateur. Les personnes de contact, "
             "adresses e-mail et numéros de téléphone ne sont pas collectés séparément ; lorsque "
             "le texte d'un appel d'offres en contient, ils sont repris tels quels de simap.ch."),
            ("Finalité et justification",
             "La finalité est de rendre repérables et comparables des décisions "
             "d'adjudication déjà publiées officiellement. Les données ont été publiées "
             "par des autorités fédérales, cantonales et communales dans le cadre du "
             "droit des marchés publics ; elles sont accessibles au public et sont "
             "restituées sans modification de contenu conformément aux conditions "
             "d'utilisation de l'API de simap.ch. Le traitement repose sur l'intérêt "
             "prépondérant à la transparence des marchés publics."),
            ("Données sur les visiteurs",
             "Ce site ne dépose aucun cookie, n’utilise aucun service d’analyse ou de suivi et "
             "n’intègre aucun script ni aucune police de caractères de tiers. Il n’y a pas de "
             "compte utilisateur ; le seul formulaire est l’inscription facultative à l’alerte "
             "e-mail (voir ci-dessous). Le site est diffusé via GitHub Pages ; l’hébergeur "
             "peut enregistrer dans ses propres journaux des données techniques de connexion "
             "telles que les adresses IP."),
            ("Alerte e-mail et flux RSS",
             "Pour recevoir les nouveaux appels d'offres par e-mail, il suffit de remplir le "
             "formulaire de la page de l’alerte e-mail. "
             "L'inscription n'est active qu'après un clic sur le lien de confirmation envoyé par "
             "e-mail (double opt-in). Sont traités l'adresse e-mail, les cantons et branches "
             "choisis, la langue, la date et l'adresse IP de la confirmation ainsi que, pendant "
             "45 jours au plus, la liste des appels d'offres déjà envoyés, afin qu’aucun ne soit "
             "envoyé deux fois ; le tout uniquement pour l'envoi de ces alertes, sur la base de "
             "votre propre inscription. Les e-mails contiennent un pixel de suivi et des liens "
             "qui passent par un serveur de Brevo ; Brevo peut ainsi enregistrer les ouvertures "
             "et les clics. Vous pouvez l'empêcher en désactivant le chargement automatique des "
             "images et en consultant les appels d'offres directement sur auftragsregister.ch. "
             "Vous pouvez vous désabonner à tout moment par le lien présent dans chaque e-mail "
             "ou par un e-mail avec l'objet « Stop » ; nous vous retirons ensuite de la liste de "
             "diffusion dans les 30 jours et effaçons la liste des appels d'offres envoyés. "
             "Brevo conserve votre fiche de contact (notamment l'adresse e-mail et la date de "
             "l'inscription et de la confirmation), la mention de votre désabonnement et les "
             "journaux des e-mails déjà envoyés, afin que vous ne receviez plus aucun e-mail. "
             "Les données ne sont ni vendues, ni cédées à des tiers pour leurs propres fins, ni "
             "utilisées à d'autres fins. Les traitent pour notre compte : Brevo (Sendinblue SAS, "
             "Paris, UE) pour l’inscription et l’envoi et, pour les e-mails adressés à "
             "abo@auftragsregister.ch (y compris les signalements d’erreur), ImprovMX Inc. "
             "(États-Unis), qui les redirige, et Google LLC, qui héberge la boîte aux lettres "
             "(Gmail). Les flux RSS ne demandent aucune inscription et ne nous transmettent "
             "aucune donnée personnelle."),
            ("Archive et conservation",
             "Les données sont mises à jour depuis simap.ch, en règle générale les jours ouvrables. Les "
             "publications plus anciennes sont conservées sous forme d'archive, même "
             "lorsqu'elles ne peuvent plus être interrogées via l'interface de simap.ch."),
            ("Vos droits",
             "Vous pouvez en tout temps demander l'accès aux données vous concernant, leur "
             "rectification ou leur effacement, et vous opposer au traitement. Un simple e-mail "
             "à l'adresse ci-dessus suffit ; les demandes sont traitées sans frais. Seule la "
             "publication sur simap.ch fait foi : pour la faire rectifier, il convient en outre "
             "de s’adresser à l’autorité qui l’a publiée."),
        ],
    },
    "it": {
        "title": "Protezione dei dati",
        "operator_h": "Titolare del trattamento",
        "operator_note": "Privato, Svizzera",
        "contact_h": "Contatto",
        "paras": [
            ("Quali dati personali contiene questo sito?",
             "Questo sito riproduce pubblicazioni ufficiali di simap.ch. La maggior parte "
             "degli aggiudicatari sono imprese. Alcuni sono però ditte individuali e "
             "lavoratori indipendenti: in questi casi il nome di una persona fisica "
             "compare insieme all'appalto, all'importo e al committente. Persone di "
             "contatto, indirizzi e-mail e numeri di telefono non vengono raccolti a "
             "parte; se il testo di un bando li contiene, sono ripresi invariati da "
             "simap.ch."),
            ("Finalità e giustificazione",
             "La finalità è rendere reperibili e confrontabili decisioni di aggiudicazione già "
             "pubblicate ufficialmente. I dati sono stati pubblicati da autorità federali, "
             "cantonali e comunali nell'ambito del diritto degli appalti pubblici, sono "
             "accessibili a chiunque e vengono riprodotti senza modificarne il contenuto, "
             "conformemente alle condizioni d’uso dell’API di simap.ch. Il trattamento si fonda "
             "sull'interesse preponderante alla trasparenza degli appalti pubblici."),
            ("Dati sui visitatori",
             "Questo sito non usa cookie, non impiega servizi di analisi o tracciamento e non "
             "incorpora script o font di terzi. Non esistono account utente; l'unico modulo è "
             "l'iscrizione facoltativa all’avviso e-mail (vedi sotto). Il sito è "
             "distribuito tramite GitHub Pages; il fornitore di hosting può registrare nei "
             "propri log dati tecnici di connessione come gli indirizzi IP."),
            ("Avviso e-mail e feed RSS",
             "Per ricevere i nuovi bandi via e-mail ci si iscrive con il modulo della pagina "
             "dell’avviso e-mail. L’iscrizione diventa "
             "attiva solo dopo il clic sul link di conferma inviato via e-mail (double opt-in). "
             "Vengono trattati l’indirizzo e-mail, i cantoni e i rami scelti, la lingua, la "
             "data, l’ora e l’indirizzo IP della conferma e, per 45 giorni al massimo, l’elenco "
             "dei bandi già inviati, affinché nessun bando venga inviato due volte; il tutto "
             "esclusivamente per l’invio di questi avvisi e sulla base della sua iscrizione. Le "
             "e-mail contengono un pixel di tracciamento e link che passano da un server di "
             "Brevo; Brevo può così registrare aperture e clic. Può impedirlo disattivando il "
             "caricamento automatico delle immagini e aprendo i bandi direttamente su "
             "auftragsregister.ch. Può cancellarsi in qualsiasi momento con il link presente in "
             "ogni e-mail o inviando un’e-mail con oggetto «Stop»; entro 30 giorni la togliamo "
             "dalla lista d’invio e cancelliamo l’elenco dei bandi inviati. Presso Brevo "
             "restano la sua scheda di contatto (tra l’altro l’indirizzo e-mail, la data e l’ora "
             "dell’iscrizione e della conferma), l’annotazione della cancellazione e i registri "
             "delle e-mail già inviate, affinché non riceva più alcuna e-mail. I dati non "
             "vengono venduti, non vengono ceduti a terzi per i loro scopi e non sono usati per "
             "altri scopi. Li trattano per nostro conto: Brevo (Sendinblue SAS, Parigi, UE) per "
             "iscrizione e invio e, per le e-mail inviate ad abo@auftragsregister.ch (anche le "
             "segnalazioni di errori), ImprovMX Inc. (USA), che le inoltra, e Google LLC, presso cui "
             "si trova la casella di posta (Gmail). I feed RSS non richiedono iscrizione e non ci "
             "trasmettono dati personali."),
            ("Archivio e conservazione",
             "I dati vengono ripresi da simap.ch, di norma nei giorni feriali. Le pubblicazioni più "
             "vecchie restano conservate come archivio, anche quando non sono più "
             "interrogabili tramite l'interfaccia di simap.ch."),
            ("I suoi diritti",
             "Può in ogni momento chiedere l'accesso ai dati che la riguardano, la loro "
             "rettifica o cancellazione e opporsi al trattamento. È sufficiente una breve e-mail "
             "all'indirizzo indicato sopra; le richieste sono trattate senza spese. Fa fede la "
             "pubblicazione su simap.ch: una rettifica andrebbe richiesta anche all’autorità che "
             "l’ha pubblicata."),
        ],
    },
    "en": {
        "title": "Privacy",
        "operator_h": "Controller",
        "operator_note": "Private individual, Switzerland",
        "contact_h": "Contact",
        "paras": [
            ("What personal data does this site contain?",
             "This site reproduces official publications from simap.ch. Most contract winners are "
             "companies. Some, however, are sole proprietorships and self-employed individuals: "
             "in those cases the name of a natural person appears together with the contract, "
             "the amount and the contracting authority. Contact persons, email addresses and "
             "telephone numbers are not collected separately; where the text of a tender "
             "contains them, they are reproduced unchanged from simap.ch."),
            ("Purpose and justification",
             "The purpose is to make already officially published award decisions "
             "findable and comparable. The data was published by federal, cantonal and "
             "communal authorities under public-procurement law, is publicly accessible, "
             "and is reproduced without changes to its content under the simap.ch API "
             "terms of use. The processing rests on the overriding interest in the "
             "transparency of public procurement."),
            ("Data about visitors",
             "This site sets no cookies, uses no analytics or tracking services, and embeds no "
             "third-party scripts or fonts. There are no user accounts; the only form is the "
             "optional subscription to email alerts (see below). The site is served through GitHub "
             "Pages; the hosting provider may record technical connection data such as IP "
             "addresses in its own server logs."),
            ("Email alerts and RSS feeds",
             "To receive new tenders by email, subscribe with the form on the email alerts page. "
             "Your email alert only becomes active once you "
             "click the confirmation link sent to you by email (double opt-in). We process your "
             "email address, the cantons and industries you choose, your language, the time and "
             "IP address of your confirmation and, for no more than 45 days, the list of tenders "
             "already sent to you, so that none is sent twice; all of this solely to send these "
             "alerts, on the basis of your own subscription. The emails contain a tracking pixel and "
             "links that pass through a Brevo server, so Brevo may record opens and clicks. You "
             "can prevent this by turning off automatic image loading and opening the tenders "
             "directly on auftragsregister.ch. You can unsubscribe at any time via the link in "
             "every email or by sending an email with the subject “Stop”; we then remove you "
             "from the mailing list within 30 days and delete the list of tenders sent. Brevo "
             "keeps your contact record (including your email address and the time of subscription "
             "and confirmation), a record that you unsubscribed and the logs of the emails "
             "already sent, to make sure you receive no further emails. The data is not sold, not "
             "passed on to third parties for their own use, and not used for any other purpose. It "
             "is processed on our behalf by Brevo (Sendinblue SAS, Paris, EU) for subscriptions and "
             "sending and, for emails sent to abo@auftragsregister.ch (error reports included), by "
             "ImprovMX Inc. (USA), which forwards them, and Google LLC, which hosts the mailbox "
             "(Gmail). The RSS feeds require no registration and send us no personal data."),
            ("Archive and retention",
             "The data is refreshed from simap.ch, usually on working days. Older publications are kept as "
             "an archive, even once they can no longer be queried through the simap.ch "
             "interface."),
            ("Your rights",
             "You may at any time request access to the data concerning you, ask for it to be "
             "corrected or deleted, and object to the processing. A short email to the address "
             "above is enough; requests are handled free of charge. The publication on simap.ch "
             "remains authoritative: a correction should also be requested from the authority "
             "that published it."),
        ],
    },
}


T["sector"] = {"de": "Bereich", "fr": "Domaine", "it": "Categoria", "en": "Category"}
T["year"] = {"de": "Jahr", "fr": "Année", "it": "Anno", "en": "Year"}
T["running_canton"] = {"de": "Offene Ausschreibungen · Kanton", "fr": "Appels d’offres en cours · Canton",
                       "it": "Bandi aperti · Cantone", "en": "Open tenders · Canton"}


T["abbr"] = {"de": "Kürzel", "fr": "Abréviation", "it": "Sigla", "en": "Code"}
T["in_register"] = {"de": "in diesem Register", "fr": "dans ce registre",
                    "it": "in questo registro", "en": "in this register"}
T["reason"]["fr"] = "Motifs de l'adjudication"
T["reason"]["it"] = "Motivazione dell'aggiudicazione"
T["treaty"]["fr"] = "Soumis aux accords internationaux"
T["treaty"]["it"] = "Soggetto ai trattati internazionali"
T["treaty"]["en"] = "Covered by international treaties"
META["buyers_count_one"] = {"de": "einem einzigen Auftraggeber", "fr": "un seul adjudicateur",
                            "it": "un solo committente", "en": "a single contracting authority"}

# Canton names in the reader's language — "Tessin" on the Italian page named the
# reader's own canton in German.
CANTON_NAMES: dict[str, dict[str, str]] = {
    "de": {}, # the German names live in genera.CANTONS and stay authoritative for /de/
    "fr": {"AG": "Argovie", "AI": "Appenzell Rhodes-Intérieures",
           "AR": "Appenzell Rhodes-Extérieures", "BE": "Berne", "BL": "Bâle-Campagne",
           "BS": "Bâle-Ville", "FR": "Fribourg", "GE": "Genève", "GL": "Glaris",
           "GR": "Grisons", "JU": "Jura", "LU": "Lucerne", "NE": "Neuchâtel",
           "NW": "Nidwald", "OW": "Obwald", "SG": "Saint-Gall", "SH": "Schaffhouse",
           "SO": "Soleure", "SZ": "Schwytz", "TG": "Thurgovie", "TI": "Tessin",
           "UR": "Uri", "VD": "Vaud", "VS": "Valais", "ZG": "Zoug", "ZH": "Zurich"},
    "it": {"AG": "Argovia", "AI": "Appenzello Interno", "AR": "Appenzello Esterno",
           "BE": "Berna", "BL": "Basilea Campagna", "BS": "Basilea Città",
           "FR": "Friburgo", "GE": "Ginevra", "GL": "Glarona", "GR": "Grigioni",
           "JU": "Giura", "LU": "Lucerna", "NE": "Neuchâtel", "NW": "Nidvaldo",
           "OW": "Obvaldo", "SG": "San Gallo", "SH": "Sciaffusa", "SO": "Soletta",
           "SZ": "Svitto", "TG": "Turgovia", "TI": "Ticino", "UR": "Uri",
           "VD": "Vaud", "VS": "Vallese", "ZG": "Zugo", "ZH": "Zurigo"},
    "en": {"AG": "Aargau", "AI": "Appenzell Innerrhoden", "AR": "Appenzell Ausserrhoden",
           "BE": "Bern", "BL": "Basel-Landschaft", "BS": "Basel-Stadt", "FR": "Fribourg",
           "GE": "Geneva", "GL": "Glarus", "GR": "Graubünden", "JU": "Jura",
           "LU": "Lucerne", "NE": "Neuchâtel", "NW": "Nidwalden", "OW": "Obwalden",
           "SG": "St. Gallen", "SH": "Schaffhausen", "SO": "Solothurn", "SZ": "Schwyz",
           "TG": "Thurgau", "TI": "Ticino", "UR": "Uri", "VD": "Vaud", "VS": "Valais",
           "ZG": "Zug", "ZH": "Zurich"},
}

# The alert call-out on every company page (23.09.2026). Search Console: 8 of the 10
# queries with the most impressions are company names, so visitors land on company
# pages — and the free e-mail alert was offered only on the tenders pages.
# {sector} is the company's main CPV division, {where} the phrase from alert_where.
# No "an Werktagen" / "chaque jour ouvrable": an e-mail goes out only on a day with new matching
# tenders (08.10.2026, as on the subscription page)
META["alert_both"] = {
    "de": "Neue Ausschreibungen der Branche «{sector}» {where} — per E-Mail, kostenlos.",
    "fr": "Recevez gratuitement par e-mail les nouveaux appels d’offres de la branche « {sector} » "
          "{where}.",
    "it": "Nuovi bandi nel ramo «{sector}» {where} – via e-mail, gratuitamente.",
    "en": "Get new tenders in the “{sector}” industry {where} by email – free.",
}
META["alert_sector"] = {
    "de": "Neue Ausschreibungen der Branche «{sector}» aus der ganzen Schweiz — per E-Mail, "
          "kostenlos.",
    "fr": "Recevez gratuitement par e-mail les nouveaux appels d’offres de la branche « {sector} » "
          "de toute la Suisse.",
    "it": "Nuovi bandi nel ramo «{sector}» in tutta la Svizzera – via e-mail, gratuitamente.",
    "en": "Get new tenders in the “{sector}” industry from all over Switzerland by email – free.",
}
META["alert_canton"] = {
    "de": "Neue öffentliche Ausschreibungen {where} — per E-Mail, kostenlos.",
    "fr": "Recevez gratuitement par e-mail les nouveaux appels d’offres publics {where}.",
    "it": "Nuovi bandi pubblici {where} — via e-mail, gratuitamente.",
    "en": "Get new public tenders {where} by email – free.",
}
META["alert_none"] = {
    "de": "Neue öffentliche Ausschreibungen — per E-Mail, kostenlos.",
    "fr": "Recevez gratuitement par e-mail les nouveaux appels d’offres publics.",
    "it": "Nuovi bandi pubblici — via e-mail, gratuitamente.",
    "en": "Get new public tenders by email – free.",
}
META["alert_link"] = {"de": "E-Mail-Abo einrichten", "fr": "Créer une alerte e-mail",
                      "it": "Attiva l’avviso e-mail", "en": "Set up an email alert"}
META["alert_where"] = {"de": "im Kanton {name}", "fr": "dans le canton {of}",
                       "it": "nel Canton {name}", "en": "in the canton of {name}"}
# The e-mail field's example address: "name@firma.ch" read German on every other page.
META["abo_form_placeholder"] = {"de": "name@firma.ch", "fr": "nom@entreprise.ch",
                                "it": "nome@azienda.ch", "en": "name@company.ch"}

# "canton de …" / "cantone di …" take the article the name carries: du Valais, des
# Grisons, d'Argovie; del Vallese, dei Grigioni, and Cantone Ticino with none at all.
CANTON_OF: dict[str, dict[str, str]] = {
    "fr": {"AG": "d'Argovie", "AI": "d'Appenzell Rhodes-Intérieures",
           "AR": "d'Appenzell Rhodes-Extérieures", "GR": "des Grisons", "JU": "du Jura",
           "OW": "d'Obwald", "TI": "du Tessin", "UR": "d'Uri", "VS": "du Valais"},
}


def canton_of(code: str, name: str, lang: str) -> str:
    """The canton's name with the preposition it takes: 'de Vaud', 'du Valais'."""
    if code in CANTON_OF.get(lang, {}):
        return CANTON_OF[lang][code]
    return {"fr": "de ", "it": "di "}.get(lang, "") + name


# Short names for the 45 CPV divisions (the first two digits of a code). The EU names run
# to 138 characters and were cut mid-word in pills, list rows and titles; these fit every
# place a division is named: the division lists, the tender pages and the alert pills.
CPV_SHORT = {
 "de": {"03": "Agrar- und Forstprodukte", "09": "Energie und Brennstoffe", "14": "Bergbau und Metalle",
        "15": "Nahrungsmittel und Getränke", "16": "Landwirtschaftsmaschinen", "18": "Kleidung und Schuhe",
        "19": "Leder, Textilien, Kunststoff, Gummi", "22": "Drucksachen", "24": "Chemische Erzeugnisse",
        "30": "Büromaschinen und Computer", "31": "Elektrotechnik und Beleuchtung", "32": "Funk, Fernsehen, Telekommunikation",
        "33": "Medizinprodukte und Arzneimittel", "34": "Fahrzeuge und Verkehrstechnik", "35": "Sicherheit, Polizei, Verteidigung",
        "37": "Musikinstrumente, Sport, Spielwaren", "38": "Labor- und Präzisionsgeräte", "39": "Möbel, Einrichtung, Haushaltsgeräte",
        "41": "Wasser", "42": "Industriemaschinen", "43": "Bau- und Bergbaumaschinen", "44": "Baustoffe und Baukonstruktionen",
        "45": "Bauarbeiten", "48": "Software und Informationssysteme", "50": "Reparatur und Wartung",
        "51": "Installation (ohne Software)", "55": "Gastgewerbe und Detailhandel", "60": "Transportdienstleistungen",
        "63": "Verkehrshilfsdienste, Reisebüros", "64": "Post und Telekommunikation", "65": "Energie- und Wasserversorgung",
        "66": "Finanzen und Versicherungen", "70": "Immobiliendienstleistungen", "71": "Architektur- und Ingenieurleistungen",
        "72": "Informatikdienstleistungen", "73": "Forschung und Entwicklung", "75": "Verwaltung und Sozialversicherung",
        "76": "Erdöl- und Erdgasdienstleistungen", "77": "Land-, Forstwirtschaft, Gartenbau", "79": "Dienstleistungen für Unternehmen",
        "80": "Aus- und Weiterbildung", "85": "Gesundheits- und Sozialwesen", "90": "Abwasser, Abfall, Reinigung, Umwelt",
        "92": "Kultur, Sport, Freizeit", "98": "Sonstige Dienstleistungen"},
 "fr": {"03": "Produits agricoles et forestiers", "09": "Énergie et combustibles", "14": "Mines et métaux",
        "15": "Alimentation et boissons", "16": "Machines agricoles", "18": "Vêtements et chaussures",
        "19": "Cuir, textiles, plastique, caoutchouc", "22": "Imprimés", "24": "Produits chimiques",
        "30": "Informatique et bureautique", "31": "Matériel électrique et éclairage", "32": "Radio, TV, télécommunications",
        "33": "Matériel médical et médicaments", "34": "Matériel de transport", "35": "Sécurité, police, défense",
        "37": "Musique, sport, jeux et jouets", "38": "Instruments de laboratoire et de précision", "39": "Mobilier et électroménager",
        "41": "Eau", "42": "Machines industrielles", "43": "Engins de chantier et d’exploitation minière", "44": "Matériaux de construction",
        "45": "Travaux de construction", "48": "Logiciels", "50": "Réparation et entretien",
        "51": "Installation (hors logiciels)", "55": "Hôtellerie, restauration et commerce de détail", "60": "Transports",
        "63": "Services liés aux transports, agences de voyage", "64": "Poste et télécommunications", "65": "Distribution d’énergie et d’eau",
        "66": "Finance et assurances", "70": "Services immobiliers", "71": "Architecture et ingénierie",
        "72": "Services informatiques", "73": "Recherche et développement", "75": "Administration et sécurité sociale",
        "76": "Services pétroliers et gaziers", "77": "Agriculture, forêts, horticulture", "79": "Services aux entreprises",
        "80": "Enseignement et formation", "85": "Santé et action sociale", "90": "Eaux usées, déchets, nettoyage, environnement",
        "92": "Culture, sport, loisirs", "98": "Autres services"},
 "it": {"03": "Prodotti agricoli e forestali", "09": "Energia e combustibili", "14": "Minerali e metalli",
        "15": "Alimenti e bevande", "16": "Macchinari agricoli", "18": "Abbigliamento e calzature",
        "19": "Cuoio, tessuti, plastica, gomma", "22": "Stampati", "24": "Prodotti chimici",
        "30": "Computer e macchine per ufficio", "31": "Materiale elettrico e illuminazione", "32": "Radio, televisione, telecomunicazioni",
        "33": "Apparecchi medici e farmaci", "34": "Veicoli e mezzi di trasporto", "35": "Sicurezza, polizia, difesa",
        "37": "Strumenti musicali, sport, giochi", "38": "Strumenti di laboratorio e di precisione", "39": "Mobili ed elettrodomestici",
        "41": "Acqua", "42": "Macchinari industriali", "43": "Macchine edili e per cave", "44": "Materiali da costruzione",
        "45": "Lavori di costruzione", "48": "Software e sistemi informativi", "50": "Riparazione e manutenzione",
        "51": "Installazione (escluso software)", "55": "Alberghi, ristorazione, commercio", "60": "Trasporti",
        "63": "Servizi ausiliari ai trasporti", "64": "Poste e telecomunicazioni", "65": "Distribuzione di energia e acqua",
        "66": "Finanza e assicurazioni", "70": "Servizi immobiliari", "71": "Architettura e ingegneria",
        "72": "Servizi informatici", "73": "Ricerca e sviluppo", "75": "Amministrazione pubblica e previdenza sociale",
        "76": "Servizi per petrolio e gas", "77": "Agricoltura, selvicoltura, giardinaggio", "79": "Servizi alle imprese",
        "80": "Istruzione e formazione", "85": "Sanità e assistenza sociale", "90": "Acque reflue, rifiuti, pulizia",
        "92": "Cultura, sport, tempo libero", "98": "Altri servizi"},
 "en": {"03": "Agricultural and forestry products", "09": "Energy and fuels", "14": "Mining and metals",
        "15": "Food and beverages", "16": "Agricultural machinery", "18": "Clothing and footwear",
        "19": "Leather, textiles, plastic, rubber", "22": "Printed matter", "24": "Chemical products",
        "30": "Computers and office equipment", "31": "Electrical equipment and lighting", "32": "Radio, TV and telecoms equipment",
        "33": "Medical equipment and medicines", "34": "Vehicles and transport equipment", "35": "Security, police, defence",
        "37": "Musical instruments, sport, toys", "38": "Laboratory and precision equipment", "39": "Furniture and appliances",
        "41": "Water", "42": "Industrial machinery", "43": "Construction and mining machinery", "44": "Construction materials",
        "45": "Construction work", "48": "Software and information systems", "50": "Repair and maintenance",
        "51": "Installation (except software)", "55": "Hotels, catering and retail", "60": "Transport services",
        "63": "Transport support services", "64": "Post and telecommunications", "65": "Energy and water supply",
        "66": "Finance and insurance", "70": "Real estate services", "71": "Architecture and engineering",
        "72": "IT services", "73": "Research and development", "75": "Public administration and social security",
        "76": "Oil and gas services", "77": "Agriculture, forestry, gardening", "79": "Business services",
        "80": "Education and training", "85": "Health and social work", "90": "Sewage, waste, cleaning",
        "92": "Culture, sport, recreation", "98": "Other services"},
}
# Company size bands, top to bottom: >=100m, >=10m, >=1m, >=100k, <100k, no attributable
# amount. Edges are exclusive ("1–10 Mio." and "100’000 – 1 Mio." both claimed 1 Mio.), and
# genera bands an award on the ROUNDED figure it prints (formato.shown), so an award shown as
# "1 Mio." is never counted "unter 1 Mio.".
BANDS = {
 "de": ("100 Mio. CHF und mehr", "10 bis unter 100 Mio. CHF", "1 bis unter 10 Mio. CHF",
        "100’000 CHF bis unter 1 Mio. CHF", "unter 100’000 CHF", "ohne zurechenbaren Betrag"),
 "fr": ("100 mio CHF et plus", "de 10 à moins de 100 mio CHF", "de 1 à moins de 10 mio CHF",
        "de 100\u202f000 CHF à moins de 1 mio CHF", "moins de 100\u202f000 CHF", "sans montant attribuable"),
 "it": ("100 mio. CHF e oltre", "da 10 a meno di 100 mio. CHF", "da 1 a meno di 10 mio. CHF",
        "da 100’000 CHF a meno di 1 mio. CHF", "meno di 100’000 CHF", "importo non attribuibile"),
 "en": ("CHF 100m and over", "CHF 10m to under 100m", "CHF 1m to under 10m",
        "CHF 100,000 to under 1m", "under CHF 100,000", "no attributable CHF amount"),
}
COMPANY = {"de": ("Unternehmen", "Unternehmen"), "fr": ("entreprise", "entreprises"),
           "it": ("impresa", "imprese"), "en": ("company", "companies")}
# "an 1 Unternehmen" / "en faveur de 1 entreprise" read like a form letter
COMPANY_ONE = {"de": "ein einziges Unternehmen", "fr": "une seule entreprise",
               "it": "un’unica impresa", "en": "a single company"}
OPEN_CONTRACTS = {"de": ("offen", "offen"), "fr": ("en cours", "en cours"),
                  "it": ("aperto", "aperti"), "en": ("open", "open")}
# the same titles for a canton with none open ("Ausschreibungen im Kanton Uri: 0 offen" read like a counter)
OPEN_NONE = {"de": "zurzeit keine offen", "fr": "aucun en cours", "it": "nessuno aperto", "en": "none open"}
# The words people search with, instead of the CPV label (SERP audit 28.09.2026). (title form, in-sentence form)
SECTOR_WORD = {
    "de": {"45": ("Bauausschreibungen", "Bauausschreibungen"), "72": ("IT-Ausschreibungen", "IT-Ausschreibungen"),
           "48": ("Software-Ausschreibungen", "Software-Ausschreibungen")},
    "fr": {"45": ("Appels d’offres de construction", "appels d’offres de construction"),
           "72": ("Appels d’offres informatiques", "appels d’offres informatiques"),
           "48": ("Appels d’offres de logiciels", "appels d’offres de logiciels")},
    "it": {"45": ("Bandi edili", "bandi edili"), "72": ("Bandi informatici", "bandi informatici"),
           "48": ("Bandi per software", "bandi per software")},
    "en": {"45": ("Construction tenders", "construction tenders"), "72": ("IT tenders", "IT tenders"),
           "48": ("Software tenders", "software tenders")},
}
OPEN_TENDERS = {"de": ("offene Ausschreibung", "offene Ausschreibungen"), "fr": ("appel d’offres en cours", "appels d’offres en cours"),
                "it": ("bando aperto", "bandi aperti"), "en": ("open tender", "open tenders")}
MONTHS = {  # (abbr, full); abbr used in axes, spans and short prose, full in tooltips and screen-reader row headers
 "de": (("Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sept.", "Okt.", "Nov.", "Dez."),
        ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember")),
 "fr": (("janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."),
        ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre")),
 "it": (("gen.", "feb.", "mar.", "apr.", "mag.", "giu.", "lug.", "ago.", "set.", "ott.", "nov.", "dic."),
        ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre")),
 "en": (("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
        ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")),
}
COLON = {"de": ":", "fr": "\u202f:", "it": ":", "en": ":"}


# Singular headers over a count of one ("Tätigkeitsbereiche 1" on 383 pages per language)
T["activity"] = {"de": "Tätigkeitsbereich", "fr": "Domaine d'activité", "it": "Categoria di attività",
                 "en": "Category"}
PROSE["matched_tenders_one"] = {
    "de": "Offene Ausschreibung in einem verwandten Bereich",
    "fr": "Appel d’offres en cours dans un domaine apparenté",
    "it": "Bando aperto in una categoria affine",
    "en": "Open tender in a related category",
}
# Meta descriptions without their closing clause, used when the full one would be cut
# ("… – mit Auftraggebern, Beträgen und…", "… », publiées sur…"; verifier 28.09.2026)
META["company_desc_short"] = {
    "de": "{name}: {n} auf simap.ch{span}{val}.",
    "fr": "{name} : {n} publiées sur simap.ch{span}{val}.",
    "it": "{name}: {n} pubblicate su simap.ch{span}{val}.",
    "en": "{name}: {n} published on simap.ch{span}{val}.",
}
META["buyer_desc_short"] = {
    "de": "{name}: {n} an {f}.",
    "fr": "{name} : {n} en faveur de {f}.",
    "it": "{name}: {n} a favore di {f}.",
    "en": "{name}: {n} to {f}.",
}
META["sector_desc_short"] = {
    "de": "{n} an {f} im Bereich «{label}».",
    "fr": "{n} en faveur de {f} dans le domaine « {label} ».",
    "it": "{n} a favore di {f} nella categoria «{label}».",
    "en": "{n} to {f} in the “{label}” category.",
}
META["canton_desc_short"] = {
    "de": "{n} im Kanton {name} an {f}, publiziert auf simap.ch.",
    "fr": "{n} dans le canton {of} en faveur de {f}, publiées sur simap.ch.",
    "it": "{n} nel Canton {name} a favore di {f}, pubblicate su simap.ch.",
    "en": "{n} to {f} in the canton of {name}, published on simap.ch.",
}
# one open tender: "classés par délai" / "nach Eingabefrist geordnet" said nothing about one
# item, and the French plural participle disagreed with "1 appel d’offres"
META["open_sector_desc_one"] = {
    "de": "{n} in der Branche «{name}» (CPV {code}) aus der ganzen Schweiz (Quelle: simap.ch).",
    "fr": "{n} en Suisse dans la branche « {name} » (CPV {code}) (source : simap.ch).",
    "it": "{n} nel ramo «{name}» (CPV {code}) in tutta la Svizzera (fonte: simap.ch).",
    "en": "{n} across Switzerland in the “{name}” industry (CPV {code}) (source: simap.ch).",
}
META["open_canton_desc_one"] = {
    "de": "{n} im Kanton {name}, werktags aktualisiert (Quelle: simap.ch).",
    "fr": "{n} dans le canton {of}, mis à jour les jours ouvrables (source : simap.ch).",
    "it": "{n} nel Canton {name}, aggiornato nei giorni feriali (fonte: simap.ch).",
    "en": "{n} in the canton of {name}, updated on working days (source: simap.ch).",
}
# the note on buyer pages, counted: 72 of 128 German pages had exactly one such award
META["buyer_joint_note_one"] = {
    "de": "Ein Zuschlag ging an mehrere Unternehmen.",
    "fr": "Une adjudication a été attribuée à plusieurs entreprises.",
    "it": "Un’aggiudicazione è andata a più imprese.",
    "en": "One award went to several companies.",
}
META["open_sector_desc_short"] = {
    "de": "{n} in der Branche «{name}» (CPV {code}) aus der ganzen Schweiz.",
    "fr": "{n} en Suisse dans la branche « {name} » (CPV {code}), par ordre d’échéance.",
    "it": "{n} nel ramo «{name}» (CPV {code}) in tutta la Svizzera, in ordine di scadenza.",
    "en": "{n} across Switzerland in the “{name}” industry (CPV {code}), sorted by deadline.",
}
# What tells apart two award rows that read the same when they belong to one project:
# the publication number ("38433-02", "38433-03" are awards for different lots)
IDX["publication_no"] = {
    "de": "Publikation {n}",
    "fr": "publication {n}",
    "it": "pubblicazione n. {n}",
    "en": "publication {n}",
}
# the other lots of a project on each lot's page: the home groups them into one line
# ("… · 6 Lose") that links to the first lot (verifier, 28.09.2026)
# They are separate simap projects (same authority, same deadline, one project name): the
# heading must not say "of this project" right under this page's own project number
IDX["other_lots"] = {
    "de": "Weitere Lose mit derselben Eingabefrist",
    "fr": "Autres lots avec le même délai",
    "it": "Altri lotti con la stessa scadenza",
    "en": "Other lots with the same deadline",
}
# The title of a lot's own award, which simap publishes apart from the other lots (28439-02
# for lot 1, -03 for lot 2) under the project's title alone: lotti.py names the lot after it
# (08.10.2026). Written into the record in the language of {title}, not of the page; {title}
# and {lot} are simap's own texts.
IDX["lot_award_title"] = {
    "de": "{title} – Los\u00a0{n}: {lot}",
    "fr": "{title} – lot\u00a0{n} : {lot}",
    "it": "{title} – lotto\u00a0{n}: {lot}",
    "en": "{title} – lot\u00a0{n}: {lot}",
}
# the lot's own name already says which lot it is ('Los 3 Zone C', 'Lotto 1 - Medicamenti')
IDX["lot_award_title_named"] = {
    "de": "{title} – {lot}",
    "fr": "{title} – {lot}",
    "it": "{title} – {lot}",
    "en": "{title} – {lot}",
}
# the lot has no name of its own beyond the project's (2018-02: both lots repeat it)
IDX["lot_award_title_bare"] = {
    "de": "{title} – Los\u00a0{n}",
    "fr": "{title} – lot\u00a0{n}",
    "it": "{title} – lotto\u00a0{n}",
    "en": "{title} – lot\u00a0{n}",
}
# the page of a division's own general code (72000000) says which division it belongs to:
# the pills name it "Informatikdienstleistungen (allgemeiner Code)", the EU label reads
# "IT-Dienste: Beratung, Software-Entwicklung, …"
IDX["sector_general"] = {
    "de": "Allgemeiner Code der Branche «{label}»",
    "fr": "Code général de la branche « {label} »",
    "it": "Codice generico del ramo «{label}»",
    "en": "General code of the “{label}” industry",
}
# A project's page lists every lot awarded, one line per lot ('Lose'), and each line is what a
# company or buyer row links to (#lot-2): the page used to show one lot, the last one read
# (6965: lot 15 of 15; 08.10.2026)
T["lots"] = {"de": "Lose", "fr": "Lots", "it": "Lotti", "en": "Lots"}
T["lot"] = {"de": "Los", "fr": "Lot", "it": "Lotto", "en": "Lot"}
T["lot_name"] = {"de": "Bezeichnung", "fr": "Intitulé", "it": "Denominazione", "en": "Title"}
T["project_number"] = {"de": "Projektnummer", "fr": "N° de projet", "it": "N. di progetto",
                       "en": "Project no."}
# the texts that differ from lot to lot, each under the lots it belongs to
IDX["lot_n"] = {"de": "Los\u00a0{n}", "fr": "Lot\u00a0{n}", "it": "Lotto\u00a0{n}", "en": "Lot\u00a0{n}"}
IDX["lots_list"] = {"de": "Lose\u00a0{n}", "fr": "Lots\u00a0{n}", "it": "Lotti\u00a0{n}", "en": "Lots\u00a0{n}"}
META["desc_lots"] = {
    "de": ", {n} Lose vergeben",
    "fr": ", {n} lots adjugés",
    "it": ", {n} lotti aggiudicati",
    "en": ", {n} lots awarded",
}
# a project without lots whose later award names other firms (4 on 08.10.2026)
META["desc_awards_n"] = {
    "de": ", {n} Zuschläge",
    "fr": ", {n} adjudications",
    "it": ", {n} aggiudicazioni",
    "en": ", {n} awards",
}
# An award to several firms has no amount of its own: simap publishes a price beside each name,
# the price of that firm's successful offer, and the page printed the first firm's as the
# 'Zuschlagsbetrag' (15349-02: 313'744.35 of five BKP packages worth 5.87 Mio.). Narrowed
# (owner, 08.10.2026): each firm with its own price, no figure for the award, and on a company
# page the firm's own price marked as its offer — not a "share", which it is not: in a
# framework the same ceiling stands beside every name.
T["offer_price"] = {"de": "Angebotspreis", "fr": "Prix de l'offre", "it": "Prezzo dell'offerta",
                    "en": "Offer price"}
T["per_firm"] = {"de": "Preise je Unternehmen", "fr": "prix par entreprise", "it": "prezzi per impresa",
                 "en": "prices per company"}
IDX["own_offer"] = {
    "de": "Angebotspreis · Zuschlag an {n} Unternehmen",
    "fr": "prix de l'offre · adjugé à {n} entreprises",
    "it": "prezzo dell'offerta · aggiudicato a {n} imprese",
    "en": "offer price · awarded to {n} companies",
}
IDX["same_price"] = {
    "de": "Die Publikation nennt für alle {n} Unternehmen denselben Preis.",
    "fr": "La publication indique le même prix pour les {n} entreprises.",
    "it": "La pubblicazione indica lo stesso prezzo per tutte le {n} imprese.",
    "en": "The publication gives the same price for all {n} companies.",
}
# two firms, the most common case: 'für alle 2 Unternehmen' reads wrong (verifier, 08.10.2026)
IDX["same_price_two"] = {
    "de": "Die Publikation nennt für beide Unternehmen denselben Preis.",
    "fr": "La publication indique le même prix pour les deux entreprises.",
    "it": "La pubblicazione indica lo stesso prezzo per entrambe le imprese.",
    "en": "The publication gives the same price for both companies.",
}
META["desc_won_n"] = {
    "de": ", Zuschlag an {n} Unternehmen",
    "fr": ", adjugé à {n} entreprises",
    "it": ", aggiudicato a {n} imprese",
    "en": ", awarded to {n} companies",
}
# under the CHF total of the home, a canton or a buyer, which leaves those awards out like the
# company pages always did (the home counted 5.1 Mrd. of first firms' prices; 08.10.2026)
IDX["sum_no_joint"] = {
    "de": "ohne die {k} Zuschläge an mehrere Unternehmen",
    "fr": "sans les {k} adjudications attribuées à plusieurs entreprises",
    "it": "escluse le {k} aggiudicazioni attribuite a più imprese",
    "en": "excluding the {k} awards made to several companies",
}
IDX["sum_no_joint_one"] = {
    "de": "ohne den Zuschlag an mehrere Unternehmen",
    "fr": "sans l'adjudication attribuée à plusieurs entreprises",
    "it": "esclusa l'aggiudicazione attribuita a più imprese",
    "en": "excluding the award made to several companies",
}
# A tender keeps its page for a while after its deadline: the links in alert e-mails and feeds
# led to a missing page the day after (08.10.2026). The status says so, with the date and time.
T["tender_expired"] = {"de": "Eingabefrist abgelaufen", "fr": "Délai de remise expiré",
                       "it": "Termine scaduto", "en": "Deadline passed"}
# {when}: formato.deadline(); Italian without an article before the date ("il 08.10.2026" needs
# "l’8"), as in mc_note_end
META["expired_lead"] = {
    "de": "Die Eingabefrist ist abgelaufen ({when}). Wird der Zuschlag auf simap.ch publiziert, "
          "erscheint er unter dieser Adresse.",
    "fr": "Le délai de remise a expiré ({when}). Si l’adjudication est publiée sur simap.ch, elle "
          "apparaîtra à cette adresse.",
    "it": "Termine d’inoltro scaduto ({when}). Se l’aggiudicazione verrà pubblicata su simap.ch, "
          "comparirà a questo indirizzo.",
    "en": "The submission deadline has passed ({when}). If the award is published on simap.ch, it "
          "will appear at this address.",
}
META["desc_deadline_passed"] = {
    "de": ", Eingabefrist abgelaufen ({date})",
    "fr": ", délai de remise expiré ({date})",
    "it": ", termine scaduto ({date})",
    "en": ", submission deadline passed ({date})",
}
# A deadline on the day of the build: the site is built once each morning, and a tender due at
# 16.00 stood under the bare date all day (08.10.2026). {t} is formato.clock(); the no-break spaces
# leave one place to wrap, before the time.
META["due_today"] = {
    "de": "läuft\u00a0heute\u00a0ab, {t}",
    "fr": "expire\u00a0aujourd’hui à\u00a0{t}",
    "it": "scade\u00a0oggi, ore\u00a0{t}",
    "en": "closes\u00a0today at\u00a0{t}",
}
META["due_today_bare"] = {"de": "läuft\u00a0heute\u00a0ab", "fr": "expire\u00a0aujourd’hui",
                          "it": "scade\u00a0oggi", "en": "closes\u00a0today"}
# Without JavaScript the pills are not copied into KANTON/BRANCHE, which stay ALLE (08.10.2026)
META["abo_form_nojs"] = {
    "de": "Ohne JavaScript wird die Auswahl oben nicht übernommen: Das Abo gilt dann für die ganze "
          "Schweiz und alle Branchen.",
    "fr": "Sans JavaScript, la sélection ci-dessus n’est pas transmise : l’alerte couvre alors toute "
          "la Suisse et toutes les branches.",
    "it": "Senza JavaScript la scelta qui sopra non viene trasmessa: l’avviso vale allora per tutta "
          "la Svizzera e per tutti i rami.",
    "en": "Without JavaScript, the selection above is not sent: the alert then covers all of "
          "Switzerland and every industry.",
}
# The page GitHub Pages serves for any missing URL (docs/404.html), all four languages on one page.
# {days}: genera.EXPIRED_DAYS
META["nf_title"] = {"de": "Seite nicht gefunden", "fr": "Page introuvable",
                    "it": "Pagina non trovata", "en": "Page not found"}
META["nf_text"] = {
    "de": "Diese Seite gibt es nicht oder nicht mehr. Ausschreibungen bleiben nach Ablauf der "
          "Eingabefrist noch {days} Tage abrufbar.",
    "fr": "Cette page n’existe pas ou n’existe plus. Les appels d’offres restent consultables "
          "{days} jours après l’expiration du délai de remise.",
    "it": "Questa pagina non esiste o non esiste più. I bandi restano consultabili per {days} "
          "giorni dopo la scadenza del termine d’inoltro.",
    "en": "This page does not exist, or no longer does. Tenders stay online for {days} days after "
          "their submission deadline.",
}
# the breadcrumbs' first level, in the same words (T["home"], step 5)
META["nf_home"] = {"de": "Startseite", "fr": "Accueil", "it": "Home", "en": "Home"}
# shown by the page's script when the missing URL was a tender's (/de/auftrag/<id>/)
META["nf_simap"] = {"de": "Diese Ausschreibung auf simap.ch öffnen",
                    "fr": "Ouvrir cet appel d’offres sur simap.ch",
                    "it": "Apri questo bando su simap.ch",
                    "en": "Open this tender on simap.ch"}


# ------------------------------------------------- navigation, doors, alerts (14.10.2026)
# The audit of 13.10.2026: no menu, no visible breadcrumbs, no skip link, the alert offered
# prefilled only on company pages. One label per section, shared by the menu and the breadcrumbs.
# 'Branchen' in German as the owner named it (the /bereich/ pages still say 'Bereich': copy pass).
T["nav_tenders"] = {"de": "Ausschreibungen", "fr": "Appels d’offres", "it": "Bandi", "en": "Tenders"}
T["nav_alert"] = {"de": "E-Mail-Abo", "fr": "Alerte e-mail", "it": "Avviso e-mail", "en": "Email alerts"}
T["nav_companies"] = {"de": "Unternehmen", "fr": "Entreprises", "it": "Imprese", "en": "Companies"}
T["nav_buyers"] = {"de": "Auftraggeber", "fr": "Adjudicateurs", "it": "Committenti",
                   "en": "Contracting authorities"}
T["nav_cantons"] = {"de": "Kantone", "fr": "Cantons", "it": "Cantoni", "en": "Cantons"}
T["nav_sectors"] = {"de": "Branchen", "fr": "Domaines", "it": "Settori", "en": "Sectors"}
T["nav_about"] = {"de": "Über das Register", "fr": "À propos", "it": "Informazioni", "en": "About"}
T["nav_label"] = {"de": "Hauptnavigation", "fr": "Navigation principale", "it": "Navigazione principale",
                  "en": "Main navigation"}
T["home"] = {"de": "Startseite", "fr": "Accueil", "it": "Home", "en": "Home"}
T["crumbs_label"] = {"de": "Sie sind hier", "fr": "Fil d’Ariane", "it": "Percorso di navigazione",
                     "en": "Breadcrumb"}
T["skip"] = {"de": "Zum Inhalt springen", "fr": "Aller au contenu", "it": "Vai al contenuto",
             "en": "Skip to main content"}
# the footer's data line: the date is the newest publication (DATA_DATE). Pages whose content does
# not change from one day to the next carry it through /stand.js, so they stay byte-identical
# overnight (git, IndexNow and the sitemap's lastmod read every changed page as news).
# Italian without a preposition before the date ("del 08.10.2026" needs "dell’8").
META["stand"] = {"de": "Daten vom {d}", "fr": "État des données : {d}",
                 "it": "Stato dei dati: {d}", "en": "Data as of {d}"}
META["methodik"] = {"de": "Methodik", "fr": "Méthodologie", "it": "Metodologia", "en": "Methodology"}

# The home's two doors: open tenders (with the ones first published on the day of the build) and
# the company index. {m}: tenders whose first publication (-01) is dated the build day.
META["door_new"] = {"de": "{m} neue am {d}", "fr": "{m} nouveaux le {d}",
                    "it": "{m} nuovi ({d})", "en": "{m} new on {d}"}
META["door_new_one"] = {"de": "1 neue am {d}", "fr": "1 nouveau le {d}",
                        "it": "1 nuovo ({d})", "en": "1 new on {d}"}
META["door_open_sub"] = {
    "de": "Nach Eingabefrist, Kanton und Branche – jede mit dem Link zur amtlichen Publikation.",
    "fr": "Par délai, par canton et par branche – chacun avec le lien vers la publication officielle.",
    "it": "Per scadenza, cantone e ramo – ognuno con il link alla pubblicazione ufficiale.",
    "en": "By deadline, canton and industry – each with a link to the official publication.",
}
META["door_companies_h"] = {"de": "Unternehmen finden", "fr": "Trouver une entreprise",
                            "it": "Trova un’impresa", "en": "Find a company"}
META["door_companies_sub"] = {
    "de": "{n} Unternehmen mit mindestens zwei Zuschlägen – von A bis Z.",
    "fr": "{n} entreprises ayant obtenu au moins deux adjudications, de A à Z.",
    "it": "{n} imprese con almeno due aggiudicazioni, dalla A alla Z.",
    "en": "{n} companies with at least two awards, from A to Z.",
}
# the home's lower half counts awards: the headings say so (the chips read like open tenders)
IDX["by_canton_awards"] = {"de": "Zuschläge nach Kanton", "fr": "Adjudications par canton",
                           "it": "Aggiudicazioni per cantone", "en": "Awards by canton"}
IDX["by_sector_awards"] = {"de": "Zuschläge nach Bereich", "fr": "Adjudications par domaine",
                           "it": "Aggiudicazioni per categoria", "en": "Awards by category"}

# The hub's table gets a heading of its own (it had none, under the canton list)
META["open_table_h2"] = {"de": "Offene Ausschreibungen nach Eingabefrist",
                         "fr": "Appels d’offres en cours par délai",
                         "it": "Bandi aperti per scadenza", "en": "Open tenders by deadline"}
# a canton or industry without an open tender keeps its page and its feed, and offers the alert
META["empty_canton"] = {
    "de": "Zurzeit ist im Kanton {name} keine Ausschreibung offen.",
    "fr": "Aucun appel d’offres n’est actuellement en cours dans le canton {of}.",
    "it": "Al momento nel Canton {name} non ci sono bandi aperti.",
    "en": "There are no open tenders in the canton of {name} at the moment.",
}
META["empty_sector"] = {
    "de": "Zurzeit ist in der Branche «{name}» keine Ausschreibung offen.",
    "fr": "Aucun appel d’offres n’est actuellement en cours dans la branche « {name} ».",
    "it": "Al momento nel ramo «{name}» non ci sono bandi aperti.",
    "en": "There are no open tenders in the “{name}” industry at the moment.",
}
META["empty_buyer"] = {
    "de": "Zurzeit hat dieser Auftraggeber keine offene Ausschreibung.",
    "fr": "Cet adjudicateur n’a actuellement aucun appel d’offres en cours.",
    "it": "Al momento questo committente non ha bandi aperti.",
    "en": "This contracting authority has no open tenders at the moment.",
}
# a tender page past its deadline: the hook above the alert
META["alert_missed"] = {
    "de": "Frist verpasst? Die nächsten Ausschreibungen dieser Art erhalten Sie kostenlos per E-Mail.",
    "fr": "Délai manqué ? Recevez gratuitement par e-mail les prochains appels d’offres de ce type.",
    "it": "Ha mancato la scadenza? Riceva gratuitamente via e-mail i prossimi bandi di questo tipo.",
    "en": "Missed the deadline? Get the next tenders like this by email – free.",
}
# the open tenders of the division a sector page belongs to
IDX["open_in_sector"] = {
    "de": "Offene Ausschreibungen der Branche «{name}»: {k}",
    "fr": "Appels d’offres en cours dans la branche « {name} » : {k}",
    "it": "Bandi aperti nel ramo «{name}»: {k}",
    "en": "Open tenders in the “{name}” industry: {k}",
}

# The tender page as a bid/no-bid page (audit 13.10.2026, Pacchetto 2 #14)
IDX["back_canton"] = {
    "de": "Alle offenen Ausschreibungen im Kanton {name}",
    "fr": "Tous les appels d’offres en cours dans le canton {of}",
    "it": "Tutti i bandi aperti nel Canton {name}",
    "en": "All open tenders in the canton of {name}",
}
IDX["ics_link"] = {"de": "Frist in den Kalender eintragen", "fr": "Ajouter le délai à l’agenda",
                   "it": "Aggiungi la scadenza al calendario", "en": "Add the deadline to your calendar"}
IDX["ics_summary"] = {"de": "Eingabefrist: {title}", "fr": "Délai de remise : {title}",
                      "it": "Scadenza: {title}", "en": "Submission deadline: {title}"}
IDX["ics_official"] = {"de": "Amtliche Publikation", "fr": "Publication officielle",
                       "it": "Pubblicazione ufficiale", "en": "Official publication"}
IDX["ics_page"] = {"de": "Im Register", "fr": "Dans le registre", "it": "Nel registro", "en": "In the register"}
IDX["buyer_open_h"] = {"de": "Zurzeit offene Ausschreibungen", "fr": "Appels d’offres en cours",
                       "it": "Bandi aperti", "en": "Open tenders"}
IDX["tender_buyer_open_h"] = {"de": "Weitere offene Ausschreibungen dieses Auftraggebers",
                              "fr": "Autres appels d’offres en cours du même adjudicateur",
                              "it": "Altri bandi aperti dello stesso committente",
                              "en": "Other open tenders from this contracting authority"}
IDX["tender_buyer_awards_h"] = {"de": "Frühere Zuschläge dieses Auftraggebers",
                                "fr": "Adjudications précédentes de cet adjudicateur",
                                "it": "Aggiudicazioni precedenti dello stesso committente",
                                "en": "Previous awards by this contracting authority"}
IDX["tender_buyer_awards_all"] = {"de": "Alle {n} dieses Auftraggebers",
                                  "fr": "Les {n} de cet adjudicateur",
                                  "it": "Tutte le {n} del committente",
                                  "en": "All {n} by this contracting authority"}
IDX["buyer_open_all"] = {"de": "Alle {n} offenen Ausschreibungen dieses Auftraggebers",
                         "fr": "Les {n} appels d’offres en cours de cet adjudicateur",
                         "it": "Tutti i {n} bandi aperti del committente",
                         "en": "All {n} open tenders from this contracting authority"}
# a long list of open tenders on a buyer page: the first ones, the rest behind a disclosure
IDX["show_more"] = {"de": "{n} weitere anzeigen", "fr": "Afficher les {n} autres", "it": "Mostra gli altri {n}",
                    "en": "Show {n} more"}
IDX["similar_h"] = {"de": "Ähnliche Zuschläge", "fr": "Adjudications similaires",
                    "it": "Aggiudicazioni simili", "en": "Similar awards"}
IDX["similar_note"] = {
    "de": "Zuschläge der Branche «{sector}» im Kanton {name}: die mit dem ähnlichsten CPV-Code "
          "zuerst, bei gleicher Ähnlichkeit die neuesten.",
    "fr": "Adjudications de la branche « {sector} » dans le canton {of} : les codes CPV les plus "
          "proches d’abord, puis les plus récentes à proximité égale.",
    "it": "Aggiudicazioni del ramo «{sector}» nel Canton {name}: prima i codici CPV più simili, a "
          "parità di somiglianza le più recenti.",
    "en": "Awards in the “{sector}” industry in the canton of {name}: closest CPV codes first, "
          "and the newest first among equally close ones.",
}
# CSV downloads (canton, buyer and company pages): one file per page, its awards newest first
IDX["csv_link"] = {"de": "Daten als CSV", "fr": "Données en CSV", "it": "Dati in CSV", "en": "Data as CSV"}
IDX["csv_meta"] = {"de": "{n} Zeilen, {size}", "fr": "{n} lignes, {size}", "it": "{n} righe, {size}",
                   "en": "{n} rows, {size}"}
# file names: the URL keeps one German name per language like every other path segment; the
# download attribute names the saved file in the reader's language
CSV_STEM = {"de": "zuschlaege", "fr": "adjudications", "it": "aggiudicazioni", "en": "awards"}
ICS_STEM = {"de": "eingabefrist", "fr": "delai", "it": "scadenza", "en": "deadline"}
# visually hidden table captions
IDX["cap_company_awards"] = {"de": "Zuschläge an {name}, neueste zuerst",
                             "fr": "Adjudications obtenues par {name}, les plus récentes d’abord",
                             "it": "Aggiudicazioni a {name}, dalla più recente",
                             "en": "Awards to {name}, newest first"}

# The about and methodology page (/xx/ueber/). Facts only, each checked against the generator:
# MIN_AWARDS, buyer_map(floor=3), sector_pages(floor=3), EXPIRED_DAYS, load() (abandonments,
# corrections, deadlines), chf_total(), firm_prices(), the 08:00 release in simap's API terms
# (aggiorna.embargo_ok) and the commit times of the nightly (mostly 08:40-09:00, 14.10.2026).
# Blocks: a string is a paragraph, a list a bulleted list. Placeholders are filled by genera.
UEBER: dict[str, dict] = {
    "de": {
        "title": "Über das Register und seine Methodik",
        "h1": "Über das Register",
        "lead": "Woher die Daten kommen, wie sie zusammengeführt werden und was sie nicht zeigen.",
        "sections": [
            ("register", "Was dieses Register ist", [
                "Öffentliche Aufträge Schweiz ordnet die Zuschläge und Ausschreibungen, die Bund, Kantone "
                "und Gemeinden auf simap.ch publizieren, nach Unternehmen, Auftraggebern, Kantonen und "
                "Branchen. So lässt sich nachlesen, wer welche öffentlichen Aufträge gewonnen hat – eine "
                "Frage, die simap.ch selbst nicht beantwortet.",
                "Das Register ist ein privates, unabhängiges Projekt. Es ist keine amtliche Veröffentlichung "
                "und steht in keiner Verbindung zu simap.ch oder zu einer Behörde. Massgebend sind "
                "ausschliesslich die Publikationen auf simap.ch; jede Zuschlags- und Ausschreibungsseite "
                "verlinkt die amtliche Publikation.",
            ]),
            ("quelle", "Quelle und Nutzungsbedingungen", [
                "Alle Daten stammen aus der Programmierschnittstelle (API) von simap.ch, der amtlichen "
                "Plattform für das öffentliche Beschaffungswesen der Schweiz. Deren Nutzungsbedingungen "
                "erlauben die Weiterverwendung, auch zu gewerblichen Zwecken, sofern die Daten inhaltlich "
                "unverändert, getrennt von eigenen Auswertungen und mit dem vorgeschriebenen Hinweis "
                "wiedergegeben werden. Dieser Hinweis steht im Fuss jeder Seite; eigene Auswertungen sind "
                "als solche gekennzeichnet.",
                "Titel und Beschreibungen erscheinen so, wie sie publiziert wurden, in der Sprache der "
                "Publikation. Sie werden weder übersetzt noch umformuliert.",
                "Lizenz: Das Register vergibt an den Daten keine eigene Lizenz; für ihre Weiterverwendung "
                "gelten die Nutzungsbedingungen von simap.ch ({terms}). Auf diese Bedingungen verweist auch "
                "die Lizenzangabe in den strukturierten Daten dieser Seite (schema.org/Dataset).",
            ]),
            ("aktualisierung", "Aktualisierung", [
                "simap.ch gibt die Publikationen eines Tages ab 8 Uhr zur Weiterverbreitung frei. Das "
                "Register holt sie in der Regel an jedem Werktag danach ab und ist meist am Vormittag "
                "aktualisiert; an einzelnen Tagen später oder erst am Folgetag. Abgerufen werden jeweils die "
                "Zuschläge des laufenden und des vorangehenden Monats – dort treffen auch nachträgliche "
                "Berichtigungen ein – sowie die Ausschreibungen der letzten 75 Tage.",
                "Das Datum im Fuss jeder Seite («{stand}») ist das Datum der neuesten Publikation im "
                "Register. Daten vom {date}: {awards} Zuschläge und {open} offene Ausschreibungen.",
            ]),
            ("abdeckung", "Abdeckung", [
                "Das Archiv beginnt im {start}.{ramp}{incomplete}",
                "Erfasst sind die Zuschläge, die auf simap.ch nach einem offenen Verfahren, einem selektiven "
                "Verfahren oder einem Einladungsverfahren publiziert werden, sowie die Ausschreibungen mit noch "
                "offener Eingabefrist. Freihändige Vergaben, die simap.ch in einzelnen Fällen ebenfalls "
                "publiziert, sind nicht enthalten. Aufträge, die nicht auf simap.ch publiziert werden müssen – "
                "etwa unterhalb der Schwellenwerte –, fehlen hier wie auf simap.ch.",
            ]),
            ("kantone", "Wie Aufträge den Kantonen zugeordnet werden", [
                "Massgebend ist der Kanton, den die Publikation als Ort der Leistung angibt (die Adresse des "
                "Auftrags) – dieselbe Angabe, nach der simap.ch selbst filtert. Bei einem Projekt mit Losen "
                "gilt der Kanton jedes Loses: Eine Ausschreibung mit Losen in mehreren Kantonen steht in der "
                "Liste jedes dieser Kantone und trägt den Vermerk «{multi}»; ein Zuschlag zählt nur im Kanton "
                "seines Loses, damit keine Summe einen Zuschlag doppelt zählt.",
                "Nennt die Publikation weder für den Auftrag noch für die Lose einen Ort, steht der Kanton "
                "des Auftraggebers, markiert mit «{fallback}». So erscheinen etwa Arbeiten an "
                "Nationalstrassen im Thurgau oder in St. Gallen, die die ASTRA-Filiale Winterthur ohne Ort "
                "ausschreibt, unter Zürich. Andere Auftraggeber geben ihre eigene Adresse als Ort der "
                "Leistung an; dann steht der Kanton ihres Sitzes, auch wenn die Arbeiten anderswo "
                "stattfinden – das lässt sich aus den Daten nicht erkennen.",
                "{nocant} Die Summe über alle Kantone und diese Zuschläge ergibt die Gesamtzahl auf der "
                "Startseite. Das E-Mail-Abo verwendet dieselbe Zuordnung: Eine Ausschreibung wird für jeden "
                "ihrer Kantone verschickt.",
            ]),
            ("zusammenfuehrung", "Wie Unternehmen und Auftraggeber zusammengeführt werden", [
                "Der Name eines Unternehmens ist in den Publikationen nicht immer gleich geschrieben. "
                "Schreibweisen, die sich nur in Gross- und Kleinschreibung, Umlauten, Akzenten oder "
                "Satzzeichen unterscheiden («CSD INGENIEURE AG» und «CSD Ingenieure AG», «Bolliger & Co. AG» "
                "und «Bolliger + Co. AG»), gelten als dasselbe Unternehmen; angezeigt wird die häufigste "
                "Schreibweise. Unterschiedlich benannte Einheiten, etwa Zweigniederlassungen, bleiben "
                "getrennt. Ein Abgleich mit dem Handelsregister findet nicht statt.",
                "Eine eigene Seite erhält ein Unternehmen ab {min_c} Zuschlägen, ein Auftraggeber ab "
                "{min_b} und ein Bereich (CPV-Code) ab {min_s}. Auftraggeber werden ebenfalls über ihren "
                "Namen zusammengeführt, unabhängig von Leerzeichen, Bindestrichen, Anführungszeichen und "
                "Klammern.",
                "Ein Zuschlag an mehrere Unternehmen erscheint auf der Seite jedes genannten Unternehmens.",
            ]),
            ("betraege", "Beträge, Lose und Summen", [
                "Beträge werden so wiedergegeben, wie sie publiziert wurden. Die Seite eines Zuschlags nennt "
                "den genauen Betrag; Listen zeigen einen gerundeten Betrag, den genauen beim Darüberfahren "
                "mit der Maus und für Screenreader.",
                "Summen enthalten nur Zuschläge in Franken an ein einziges Unternehmen. Bei einem Zuschlag "
                "an mehrere Unternehmen nennt die Publikation einen Preis je Unternehmen: Diese Preise "
                "werden einzeln gezeigt, aber weder addiert noch einem Gesamtauftrag zugeschrieben – bei "
                "Rahmenverträgen steht oft bei jedem Unternehmen dieselbe Obergrenze. Beträge in Euro oder "
                "anderen Währungen erscheinen mit ihrer Währung, nie in einer Spalte in Franken, und zählen "
                "in keiner Summe.",
                "Ein Betrag unter 1’000 CHF ist bei einem Zuschlag fast nie der Wert des Auftrags, sondern "
                "ein Einheitspreis (etwa pro Stunde, Stück oder Kilometer): Er ist mit «{rate}» markiert "
                "und zählt in keiner Summe und keinem Median. Dasselbe gilt für einen Betrag bis 5’000 CHF, "
                "wenn die Publikation auf Personalverleih oder einen Tages- oder Stundensatz hinweist "
                "(«LSE», «Personalverleih», «Tagessatz», «Regie» und Ähnliches).",
                "simap.ch publiziert ein Projekt mit Losen als einen Zuschlag pro Los. Die Seite des "
                "Projekts listet alle Lose; nennt simap für mehrere Lose desselben Unternehmens denselben "
                "Projektpreis, zählt er in Summen nur einmal.",
            ]),
            ("ausgeschlossen", "Was nicht enthalten ist", [[
                "Abgebrochene Verfahren: simap.ch publiziert sie im selben Datenstrom wie die Zuschläge; "
                "hier erscheinen sie nicht als Zuschlag.",
                "Berichtigungen: Wird eine Ausschreibung oder ein Zuschlag berichtigt, gilt die zuletzt "
                "publizierte Fassung; frühere Fassungen erscheinen nicht zusätzlich.",
                "Abgelaufene Ausschreibungen: Nach Ablauf der Eingabefrist bleibt die Seite einer "
                "Ausschreibung noch {days} Tage abrufbar, gekennzeichnet mit «{expired}». Wird der "
                "Zuschlag vorher publiziert, erscheint er unter derselben Adresse.",
                "Ausschreibungen ohne lesbare Eingabefrist werden nicht als offen aufgeführt.",
            ]]),
            ("cpv", "Branchen und Bereiche (CPV)", [
                "Die Einteilung folgt dem CPV, dem EU-weit einheitlichen Vokabular für öffentliche Aufträge. "
                "Eine Branche entspricht den ersten zwei Ziffern des Codes (z. B. 45, Bauarbeiten), ein Bereich "
                "dem genauen achtstelligen Code (z. B. 45233000). Die Bezeichnungen der Bereiche stammen aus "
                "der amtlichen Fassung des CPV in der jeweiligen Sprache, auf Deutsch in Schweizer Schreibweise "
                "(ss); die Namen der 45 Branchen sind eigene Kurzformen des Registers.",
                "«{matched}» auf den Unternehmensseiten und «{similar}» auf den Ausschreibungsseiten beruhen "
                "auf den gemeinsamen Ziffern der CPV-Codes: Ein allgemeiner Code wie 45000000 (Bauarbeiten) "
                "allein genügt nicht. Für Unternehmen müssen mindestens die ersten vier Ziffern (ohne "
                "Füllnullen) übereinstimmen; ähnliche Zuschläge stammen aus derselben Branche und demselben "
                "Kanton, die mit dem ähnlichsten Code zuerst.",
            ]),
            ("daten", "Daten herunterladen und abonnieren", [[
                "CSV: {csv_pages} bieten ihre Zuschläge als CSV-Datei an – UTF-8 mit BOM, Semikolon als "
                "Trennzeichen, Beträge mit Punkt als Dezimalzeichen; eine Datei für alle vier "
                "Sprachversionen, mit englischen Spaltennamen ({cols}) und den Titeln in der Sprache der "
                "Publikation. Bei Zuschlägen an mehrere Unternehmen bleibt die Spalte «Amount» leer. "
                "Zellen, die mit =, +, - oder @ beginnen, erhalten einen vorangestellten Apostroph, damit "
                "Tabellenprogramme sie nicht als Formel ausführen. «Canton source» nennt die Herkunft des "
                "Kantons (place: Ort der Leistung, lot: Los, buyer: Sitz des Auftraggebers), «Amount note» "
                "markiert vermutliche Einheitspreise (probable unit rate).",
                "Grafiken: Jede Grafik nennt ihre Quelle und verlinkt ihre Daten als CSV-Datei.",
                "Kalender: Jede offene Ausschreibung bietet ihre Eingabefrist als Kalenderdatei (.ics) an.",
                "RSS und E-Mail: Für jeden Kanton und jede Branche gibt es einen RSS-Feed; das E-Mail-Abo "
                "schickt neue Ausschreibungen nach Kanton und Branche, kostenlos und ohne Konto.",
            ]]),
            ("kontakt", "Kontakt und Fehlermeldungen", [
                "Fehler, Fragen und Hinweise an {mail}; auf jeder Zuschlags- und Ausschreibungsseite öffnet "
                "«{report}» eine E-Mail mit der Publikationsnummer im Betreff. Das Register wird von einer "
                "Privatperson in der Schweiz betrieben; die Angaben zum Betreiber stehen im Impressum.",
            ]),
        ],
        "csv_pages": "Die Kantons-, Auftraggeber- und Unternehmensseiten",
        "csv_pages_nocomp": "Die Kantons- und Auftraggeberseiten",
        "ramp": " Von {a} bis {b} ist nur ein Teil der Zuschläge erfasst; in den Monatsgrafiken sind diese "
                "Monate schraffiert. Ab {full} enthält das Register die Zuschläge, die die Schnittstelle von "
                "simap.ch beim Abruf für den jeweiligen Monat geliefert hat; ein Abgleich mit amtlichen "
                "Gesamtzahlen findet nicht statt.",
        "incomplete": " {n} Zuschlagspublikationen ({months}) kamen über die Schnittstelle ohne Titel und "
                      "ohne Zuschlagsempfänger an; sie fehlen in allen Zahlen und Listen.",
        "nocant": "{n} nennen weder einen Ort noch einen Auftraggeber mit Kanton; sie zählen zu keinem "
                  "Kanton, und die Kantonsübersicht führt sie gesondert auf.",
        "nocant_zero": "Zurzeit hat jeder Zuschlag einen Kanton.",
        "alert_link": "Zum E-Mail-Abo",
    },
    "fr": {
        "title": "À propos du registre et de sa méthodologie",
        "h1": "À propos du registre",
        "lead": "D’où viennent les données, comment elles sont regroupées et ce qu’elles ne montrent pas.",
        "sections": [
            ("register", "Ce qu’est ce registre", [
                "Marchés publics suisses classe par entreprise, par adjudicateur, par canton et par branche "
                "les adjudications et les appels d’offres que la Confédération, les cantons et les communes "
                "publient sur simap.ch. On peut ainsi savoir qui a remporté quels marchés publics – une "
                "question à laquelle simap.ch ne répond pas lui-même.",
                "Le registre est un projet privé et indépendant. Il ne s’agit pas d’une publication "
                "officielle, et il n’a aucun lien avec simap.ch ni avec aucune autorité. Seules les "
                "publications de simap.ch font foi ; chaque page d’adjudication et d’appel d’offres renvoie "
                "à la publication officielle.",
            ]),
            ("quelle", "Source et conditions d’utilisation", [
                "Toutes les données proviennent de l’interface de programmation (API) de simap.ch, la "
                "plateforme officielle des marchés publics en Suisse. Ses conditions d’utilisation autorisent "
                "la réutilisation, y compris à des fins commerciales, à condition que les données soient "
                "reproduites sans modification de leur contenu, séparées de nos propres analyses et "
                "accompagnées de la mention prescrite. Cette mention figure au bas de chaque page ; nos "
                "propres analyses sont signalées comme telles.",
                "Les titres et les descriptions apparaissent tels qu’ils ont été publiés, dans la langue de "
                "la publication. Ils ne sont ni traduits ni reformulés.",
                "Licence : le registre n’accorde aucune licence propre sur les données ; leur réutilisation "
                "est régie par les conditions d’utilisation de simap.ch ({terms}). C’est aussi à ces "
                "conditions que renvoie l’indication de licence dans les données structurées de cette page "
                "(schema.org/Dataset).",
            ]),
            ("aktualisierung", "Mise à jour", [
                "simap.ch autorise la diffusion des publications du jour à partir de 8 h. Le registre les "
                "récupère en règle générale chaque jour ouvrable après cette heure et il est le plus souvent "
                "à jour dans la matinée ; certains jours plus tard, ou le lendemain. Chaque mise à jour "
                "reprend les adjudications du mois en cours et du mois précédent – c’est là qu’arrivent aussi "
                "les rectifications – ainsi que les appels d’offres des 75 derniers jours.",
                "La date indiquée au bas de chaque page (« {stand} ») est celle de la publication la plus "
                "récente du registre. État des données : {date}, avec {awards} adjudications et {open} "
                "appels d’offres en cours.",
            ]),
            ("abdeckung", "Couverture", [
                "Les données commencent en {start}.{ramp}{incomplete}",
                "Le registre reprend les adjudications publiées sur simap.ch à l’issue d’une procédure "
                "ouverte, d’une procédure sélective ou d’une procédure sur invitation, ainsi que tous les "
                "appels d’offres dont le délai de remise court encore. Les adjudications de gré à gré, que "
                "simap.ch publie aussi dans certains cas, n’y figurent pas. Les marchés qui ne doivent pas être "
                "publiés sur simap.ch – par exemple en dessous des valeurs seuils – ne figurent ni ici ni sur "
                "simap.ch.",
            ]),
            ("kantone", "Comment les marchés sont attribués aux cantons", [
                "Ce qui compte est le canton que la publication indique comme lieu d’exécution (l’adresse "
                "du marché) – la même indication que celle sur laquelle simap.ch filtre lui-même. Pour un "
                "projet divisé en lots, c’est le canton de chaque lot qui compte : un appel d’offres dont les "
                "lots se situent dans plusieurs cantons figure dans la liste de chacun d’eux, avec la mention "
                "« {multi} » ; une adjudication n’est comptée que dans le canton de son lot, afin qu’aucun "
                "total ne la compte deux fois.",
                "Si la publication n’indique de lieu ni pour le marché ni pour les lots, c’est le canton de "
                "l’adjudicateur qui figure, avec la mention « {fallback} ». Ainsi, des travaux sur les routes "
                "nationales en Thurgovie ou à Saint-Gall que la filiale de l’OFROU à Winterthour met en "
                "soumission sans lieu apparaissent sous Zurich. D’autres adjudicateurs indiquent leur propre "
                "adresse comme lieu d’exécution ; c’est alors le canton de leur siège qui figure, même si les "
                "travaux ont lieu ailleurs – les données ne permettent pas de le déceler.",
                "{nocant} Le total de tous les cantons et de ces adjudications correspond au nombre total "
                "indiqué sur la page d’accueil. L’alerte e-mail utilise la même attribution : un appel "
                "d’offres est envoyé pour chacun de ses cantons.",
            ]),
            ("zusammenfuehrung", "Comment les entreprises et les adjudicateurs sont regroupés", [
                "Une entreprise n’apparaît pas toujours sous la même graphie dans les publications. Les "
                "graphies qui ne diffèrent que par les majuscules, les trémas, les accents ou la ponctuation "
                "(« CSD INGENIEURE AG » et « CSD Ingenieure AG », « Bolliger & Co. AG » et « Bolliger + Co. "
                "AG ») sont considérées comme une seule entreprise ; la graphie la plus fréquente est "
                "affichée. Les unités portant des noms différents, comme les succursales, restent "
                "distinctes. Aucune comparaison avec le registre du commerce n’est effectuée.",
                "Une entreprise a sa propre page à partir de {min_c} adjudications, un adjudicateur à partir "
                "de {min_b} et un domaine (code CPV) à partir de {min_s}. Les adjudicateurs sont eux aussi "
                "regroupés par leur nom, indépendamment des espaces, des traits d’union, des guillemets et "
                "des parenthèses.",
                "Une adjudication attribuée à plusieurs entreprises figure sur la page de chacune d’elles.",
            ]),
            ("betraege", "Montants, lots et totaux", [
                "Les montants sont repris tels qu’ils ont été publiés. La page d’une adjudication indique le "
                "montant exact ; les listes affichent un montant arrondi, et le montant exact au survol de "
                "la souris ainsi que pour les lecteurs d’écran.",
                "Les totaux ne comprennent que les adjudications en francs attribuées à une seule "
                "entreprise. Pour une adjudication à plusieurs entreprises, la publication indique un prix "
                "par entreprise : ces prix sont affichés séparément, mais ne sont ni additionnés ni "
                "attribués à un marché global – dans les contrats-cadres, le même plafond figure souvent à "
                "côté de chaque entreprise. Les montants en euros ou dans d’autres monnaies sont affichés "
                "avec leur devise, jamais dans une colonne en francs, et n’entrent dans aucun total.",
                "Un montant inférieur à 1 000 CHF n’est presque jamais la valeur d’un marché mais un prix "
                "unitaire (par heure, par pièce ou par kilomètre, par exemple) : il est signalé par « {rate} » "
                "et n’entre dans aucun total ni aucune médiane. Il en va de même d’un montant jusqu’à "
                "5 000 CHF lorsque la publication parle de location de services ou d’un tarif journalier ou "
                "horaire (« LSE », « location de services », « tarif journalier », etc.).",
                "simap.ch publie un projet divisé en lots sous la forme d’une adjudication par lot. La page "
                "du projet liste tous les lots ; lorsque simap indique le même prix de projet pour plusieurs "
                "lots attribués à la même entreprise, ce prix n’est compté qu’une fois dans les totaux.",
            ]),
            ("ausgeschlossen", "Ce qui n’est pas repris", [[
                "Procédures interrompues : simap.ch les publie dans le même flux que les adjudications ; "
                "elles ne sont pas présentées ici comme des adjudications.",
                "Rectifications : lorsqu’un appel d’offres ou une adjudication est rectifié, seule la "
                "dernière version publiée compte ; les versions antérieures n’apparaissent pas en plus.",
                "Appels d’offres échus : après l’expiration du délai de remise, la page d’un appel d’offres "
                "reste consultable pendant {days} jours, avec la mention « {expired} ». Si l’adjudication "
                "est publiée entre-temps, elle apparaît à la même adresse.",
                "Les appels d’offres sans délai de remise lisible ne sont pas listés comme étant en cours.",
            ]]),
            ("cpv", "Branches et domaines (CPV)", [
                "La classification suit le CPV, le vocabulaire commun pour les marchés publics de l’UE. Une "
                "branche correspond aux deux premiers chiffres du code (p. ex. 45, travaux de construction), "
                "un domaine au code exact à huit chiffres (p. ex. 45233000). Les intitulés des domaines "
                "proviennent de la version officielle du CPV dans chaque langue ; les noms des 45 branches "
                "sont des formes abrégées propres au registre.",
                "Les « {matched} » des pages d’entreprise et les « {similar} » des pages d’appel d’offres "
                "reposent sur les chiffres communs des codes CPV : un code général comme 45000000 (travaux "
                "de construction) ne suffit pas à lui seul. Pour les entreprises, au moins les quatre premiers "
                "chiffres significatifs doivent coïncider ; les adjudications similaires appartiennent à la même "
                "branche et au même canton, les codes les plus proches d’abord.",
            ]),
            ("daten", "Télécharger et s’abonner", [[
                "CSV : {csv_pages} proposent leurs adjudications sous forme de fichier CSV – UTF-8 avec BOM, "
                "point-virgule comme séparateur, montants avec un point décimal ; un seul fichier pour les "
                "quatre versions linguistiques, avec des noms de colonnes en anglais ({cols}) et les titres "
                "dans la langue de la publication. Pour les adjudications à plusieurs entreprises, la "
                "colonne « Amount » reste vide. Les cellules qui commencent par =, +, - ou @ sont précédées "
                "d’une apostrophe, afin que les tableurs ne les exécutent pas comme des formules. "
                "« Canton source » indique l’origine du canton (place : lieu d’exécution, lot : lot, buyer : "
                "siège de l’adjudicateur), « Amount note » signale les prix probablement unitaires "
                "(probable unit rate).",
                "Graphiques : chaque graphique indique sa source et renvoie à ses données en CSV.",
                "Agenda : chaque appel d’offres en cours propose son délai de remise sous forme de fichier "
                "d’agenda (.ics).",
                "RSS et e-mail : chaque canton et chaque branche a son flux RSS ; l’alerte e-mail envoie "
                "les nouveaux appels d’offres par canton et par branche, gratuitement et sans compte.",
            ]]),
            ("kontakt", "Contact et signalement d’erreurs", [
                "Erreurs, questions et remarques : {mail} ; sur chaque page d’adjudication et d’appel "
                "d’offres, « {report} » ouvre un e-mail avec le numéro de publication en objet. Le registre "
                "est exploité par un particulier en Suisse ; les informations sur l’exploitant figurent dans "
                "les mentions légales.",
            ]),
        ],
        "csv_pages": "les pages des cantons, des adjudicateurs et des entreprises",
        "csv_pages_nocomp": "les pages des cantons et des adjudicateurs",
        "ramp": " Entre {a} et {b}, seule une partie des adjudications a été relevée ; ces mois sont "
                "hachurés dans les graphiques mensuels. À partir de {full}, le registre contient les "
                "adjudications que l’interface de simap.ch a fournies pour chaque mois lors de leur relevé ; "
                "aucune comparaison avec des totaux officiels n’est effectuée.",
        "incomplete": " {n} publications d’adjudication de {months} sont arrivées par l’interface sans titre "
                      "ni adjudicataire ; elles ne figurent dans aucun chiffre ni aucune liste.",
        "nocant": "{n} n’indiquent ni lieu ni adjudicateur avec canton ; elles ne comptent dans aucun "
                  "canton, et l’aperçu des cantons les présente à part.",
        "nocant_zero": "Actuellement, chaque adjudication a un canton.",
        "alert_link": "Vers l’alerte e-mail",
    },
    "it": {
        "title": "Informazioni sul registro e sulla metodologia",
        "h1": "Informazioni sul registro",
        "lead": "Da dove vengono i dati, come vengono raggruppati e che cosa non mostrano.",
        "sections": [
            ("register", "Che cos’è questo registro", [
                "Appalti pubblici svizzeri ordina per impresa, committente, cantone e ramo le aggiudicazioni "
                "e i bandi che Confederazione, Cantoni e Comuni pubblicano su simap.ch. Così si può sapere "
                "chi ha vinto quali appalti pubblici – una domanda a cui simap.ch stesso non risponde.",
                "Il registro è un progetto privato e indipendente. Non è una pubblicazione ufficiale e non "
                "ha alcun legame con simap.ch né con alcuna autorità. Fanno fede esclusivamente le "
                "pubblicazioni su simap.ch; ogni pagina di aggiudicazione e di bando rimanda alla "
                "pubblicazione ufficiale.",
            ]),
            ("quelle", "Fonte e condizioni d’uso", [
                "Tutti i dati provengono dall’interfaccia di programmazione (API) di simap.ch, la piattaforma "
                "ufficiale degli appalti pubblici in Svizzera. Le sue condizioni d’uso consentono il "
                "riutilizzo, anche a fini commerciali, a condizione che i dati siano riprodotti senza "
                "modificarne il contenuto, separati dalle nostre analisi e accompagnati dall’avvertenza "
                "prescritta. L’avvertenza figura in fondo a ogni pagina; le nostre analisi sono indicate "
                "come tali.",
                "Titoli e descrizioni compaiono così come sono stati pubblicati, nella lingua della "
                "pubblicazione. Non vengono né tradotti né riformulati.",
                "Licenza: il registro non concede alcuna licenza propria sui dati; il loro riutilizzo è "
                "disciplinato dalle condizioni d’uso di simap.ch ({terms}). A queste condizioni rimanda "
                "anche l’indicazione di licenza nei dati strutturati di questa pagina (schema.org/Dataset).",
            ]),
            ("aktualisierung", "Aggiornamento", [
                "simap.ch rende disponibili per la diffusione le pubblicazioni del giorno a partire dalle 8. "
                "Il registro le riprende di norma ogni giorno feriale dopo quell’ora ed è per lo più "
                "aggiornato in mattinata; alcuni giorni più tardi o il giorno dopo. A ogni aggiornamento il "
                "registro riprende le aggiudicazioni del mese corrente e del mese precedente – dove arrivano "
                "anche le rettifiche – e i bandi degli ultimi 75 giorni.",
                "La data indicata in fondo a ogni pagina («{stand}») è quella della pubblicazione più recente "
                "del registro. Stato dei dati: {date}; {awards} aggiudicazioni e {open} bandi aperti.",
            ]),
            ("abdeckung", "Copertura", [
                "L’archivio parte da {start}.{ramp}{incomplete}",
                "Il registro riprende le aggiudicazioni pubblicate su simap.ch al termine di una procedura di "
                "pubblico concorso, di una procedura selettiva o di una procedura mediante invito, e tutti i "
                "bandi con il termine d’inoltro ancora aperto. Le aggiudicazioni per incarico diretto, che "
                "simap.ch pubblica in alcuni casi, non vi figurano. Gli appalti che non devono essere "
                "pubblicati su simap.ch – per esempio sotto i valori soglia – non figurano né qui né su "
                "simap.ch.",
            ]),
            ("kantone", "Come gli appalti vengono attribuiti ai cantoni", [
                "Conta il cantone che la pubblicazione indica come luogo di esecuzione (l’indirizzo "
                "dell’appalto) – la stessa indicazione su cui filtra simap.ch. Per un progetto suddiviso in "
                "lotti conta il cantone di ciascun lotto: un bando con lotti in più cantoni figura "
                "nell’elenco di ciascuno di essi, con l’indicazione «{multi}»; un’aggiudicazione conta solo "
                "nel cantone del suo lotto, affinché nessun totale la conti due volte.",
                "Se la pubblicazione non indica un luogo né per l’appalto né per i lotti, figura il cantone "
                "del committente, con l’indicazione «{fallback}». Così, per esempio, i lavori sulle strade "
                "nazionali in Turgovia o a San Gallo che la filiale USTRA di Winterthur mette a concorso "
                "senza indicare il luogo compaiono sotto Zurigo. Altri committenti indicano il proprio "
                "indirizzo come luogo di esecuzione; figura allora il cantone della loro sede, anche se i "
                "lavori si svolgono altrove – dai dati non è possibile accorgersene.",
                "{nocant} La somma di tutti i cantoni e di queste aggiudicazioni dà il numero totale della "
                "pagina iniziale. L’avviso e-mail usa la stessa attribuzione: un bando viene inviato per "
                "ciascuno dei suoi cantoni.",
            ]),
            ("zusammenfuehrung", "Come vengono raggruppati imprese e committenti", [
                "Nelle pubblicazioni il nome di un’impresa non è sempre scritto allo stesso modo. Le grafie che "
                "differiscono solo per maiuscole, dieresi, accenti o punteggiatura («CSD INGENIEURE AG» e "
                "«CSD Ingenieure AG», «Bolliger & Co. AG» e «Bolliger + Co. AG») sono considerate la stessa "
                "impresa; viene mostrata la grafia più frequente. Le unità con nomi diversi, per esempio le "
                "succursali, restano separate. Non avviene alcun confronto con il registro di commercio.",
                "Un’impresa ha una pagina propria a partire da {min_c} aggiudicazioni, un committente da "
                "{min_b} e una categoria (codice CPV) da {min_s}. Anche i committenti sono raggruppati per "
                "nome, indipendentemente da spazi, trattini, virgolette e parentesi.",
                "Un’aggiudicazione a più imprese compare sulla pagina di ciascuna di esse.",
            ]),
            ("betraege", "Importi, lotti e totali", [
                "Gli importi sono riportati come sono stati pubblicati. La pagina di un’aggiudicazione "
                "indica l’importo esatto; gli elenchi mostrano un importo arrotondato, quello esatto "
                "passando il mouse e per i lettori di schermo.",
                "I totali comprendono solo le aggiudicazioni in franchi a una sola impresa. Per "
                "un’aggiudicazione a più imprese la pubblicazione indica un prezzo per impresa: questi "
                "prezzi sono mostrati singolarmente, ma non vengono sommati né attribuiti a un appalto "
                "complessivo – nei contratti quadro accanto a ogni impresa compare spesso lo stesso tetto "
                "massimo. Gli importi in euro o in altre valute sono mostrati con la loro valuta, mai in "
                "una colonna in franchi, e non rientrano in alcun totale.",
                "Un importo inferiore a 1’000 CHF non è quasi mai il valore di un appalto ma un prezzo "
                "unitario (per ora, per pezzo o per chilometro, per esempio): è contrassegnato con «{rate}» "
                "e non rientra in alcun totale né in alcuna mediana. Lo stesso vale per un importo fino a "
                "5’000 CHF quando la pubblicazione parla di prestito di personale o di una tariffa giornaliera "
                "od oraria («LSE», «tariffa giornaliera», «Regie» e simili).",
                "simap.ch pubblica un progetto suddiviso in lotti come un’aggiudicazione per lotto. La "
                "pagina del progetto elenca tutti i lotti; se simap indica lo stesso prezzo di progetto per "
                "più lotti della stessa impresa, nei totali conta una volta sola.",
            ]),
            ("ausgeschlossen", "Che cosa non è incluso", [[
                "Procedure interrotte: simap.ch le pubblica nello stesso flusso delle aggiudicazioni; qui non "
                "compaiono come aggiudicazioni.",
                "Rettifiche: se un bando o un’aggiudicazione viene rettificato, vale l’ultima versione "
                "pubblicata; le versioni precedenti non compaiono in aggiunta.",
                "Bandi scaduti: dopo la scadenza del termine d’inoltro la pagina di un bando resta "
                "consultabile per {days} giorni, con la dicitura «{expired}». Se nel frattempo viene "
                "pubblicata l’aggiudicazione, compare allo stesso indirizzo.",
                "I bandi senza un termine d’inoltro leggibile non sono elencati come aperti.",
            ]]),
            ("cpv", "Rami e categorie (CPV)", [
                "La classificazione segue il CPV, il vocabolario comune europeo per gli appalti pubblici. "
                "Un ramo corrisponde alle prime due cifre del codice (p. es. 45, lavori di costruzione), una "
                "categoria al codice esatto di otto cifre (p. es. 45233000). Le denominazioni delle categorie "
                "provengono dalla versione ufficiale del CPV in ciascuna lingua; i nomi dei 45 rami sono "
                "abbreviazioni proprie del registro.",
                "I «{matched}» delle pagine delle imprese e le «{similar}» delle pagine dei bandi si basano "
                "sulle cifre in comune dei codici CPV: un codice generico come 45000000 (lavori di "
                "costruzione) da solo non basta. Per le imprese devono coincidere almeno le prime quattro cifre "
                "significative; le aggiudicazioni simili appartengono allo stesso ramo e allo stesso "
                "cantone, a partire dai codici più vicini.",
            ]),
            ("daten", "Scaricare i dati e iscriversi", [[
                "CSV: {csv_pages} offrono le loro aggiudicazioni come file CSV – UTF-8 con BOM, punto e "
                "virgola come separatore, importi con il punto come separatore decimale; un solo file per "
                "le quattro versioni linguistiche, con i nomi delle colonne in inglese ({cols}) e i titoli "
                "nella lingua della pubblicazione. Per le aggiudicazioni a più imprese la colonna «Amount» "
                "resta vuota. Le celle che iniziano con =, +, - o @ sono precedute da un apostrofo, "
                "affinché i fogli di calcolo non le eseguano come formule. «Canton source» indica l’origine "
                "del cantone (place: luogo di esecuzione, lot: lotto, buyer: sede del committente), «Amount "
                "note» segnala i probabili prezzi unitari (probable unit rate).",
                "Grafici: ogni grafico indica la sua fonte e rimanda ai suoi dati in CSV.",
                "Calendario: ogni bando aperto offre la sua scadenza come file di calendario (.ics).",
                "RSS ed e-mail: ogni cantone e ogni ramo ha il suo feed RSS; l’avviso e-mail invia i nuovi "
                "bandi per cantone e ramo, gratuitamente e senza account.",
            ]]),
            ("kontakt", "Contatto e segnalazione di errori", [
                "Errori, domande e segnalazioni: {mail}; su ogni pagina di aggiudicazione e di bando "
                "«{report}» apre un’e-mail con il numero di pubblicazione nell’oggetto. Il registro è "
                "gestito da un privato in Svizzera; i dati del gestore si trovano nelle note legali.",
            ]),
        ],
        "csv_pages": "Le pagine dei cantoni, dei committenti e delle imprese",
        "csv_pages_nocomp": "Le pagine dei cantoni e dei committenti",
        "ramp": " Tra {a} e {b} è stata rilevata solo una parte delle aggiudicazioni; nei grafici mensili "
                "questi mesi sono tratteggiati. Da {full} il registro contiene le aggiudicazioni che "
                "l’interfaccia di simap.ch ha fornito per ciascun mese al momento del rilevamento; non avviene "
                "alcun confronto con totali ufficiali.",
        "incomplete": " {n} pubblicazioni di aggiudicazione di {months} sono arrivate dall’interfaccia senza "
                      "titolo né aggiudicatario; mancano da tutti i numeri e da tutti gli elenchi.",
        "nocant": "{n} non indicano né un luogo né un committente con cantone; non contano in alcun "
                  "cantone, e la panoramica dei cantoni le elenca a parte.",
        "nocant_zero": "Al momento ogni aggiudicazione ha un cantone.",
        "alert_link": "Vai all’avviso e-mail",
    },
    "en": {
        "title": "About the register and its methodology",
        "h1": "About the register",
        "lead": "Where the data comes from, how it is matched and what it does not show.",
        "sections": [
            ("register", "What this register is", [
                "Swiss Public Contracts takes the awards and tenders that the Confederation, the cantons and "
                "the communes publish on simap.ch and arranges them by company, contracting authority, canton "
                "and industry. That makes it possible to see who has won which public contracts – a question "
                "simap.ch itself does not answer.",
                "The register is a private, independent project. It is not an official publication and has "
                "no connection to simap.ch or to any authority. Only the publications on simap.ch are "
                "authoritative; every award and tender page links to the official publication.",
            ]),
            ("quelle", "Source and terms of use", [
                "All data comes from the application programming interface (API) of simap.ch, the official "
                "platform for public procurement in Switzerland. Its terms of use allow the data to be "
                "reused, including commercially, provided it is reproduced without changes to its content, "
                "kept separate from our own analysis and accompanied by the prescribed notice. That notice "
                "is in the footer of every page; our own analysis is marked as such.",
                "Titles and descriptions appear as they were published, in the language of the publication. "
                "They are neither translated nor reworded.",
                "Licence: the register grants no licence of its own on the data; their reuse is governed by "
                "simap.ch’s terms of use ({terms}). The licence field in this page’s structured data "
                "(schema.org/Dataset) points to those terms.",
            ]),
            ("aktualisierung", "Updates", [
                "simap.ch releases each day’s publications for redistribution from 8 am. The register "
                "usually fetches them every working day after that and is mostly up to date by late morning; "
                "on some days later, or the next day. Each run fetches the awards of the current and the "
                "previous month – where corrections also arrive – and the tenders of the last 75 days.",
                "The date in the footer of every page (“{stand}”) is the date of the newest publication in "
                "the register. Data as of {date}: {awards} awards and {open} open tenders.",
            ]),
            ("abdeckung", "Coverage", [
                "The archive begins in {start}.{ramp}{incomplete}",
                "The register covers the awards published on simap.ch after an open, a selective or an "
                "invitation procedure, and the tenders whose submission deadline is still open. Direct awards, "
                "which simap.ch also publishes in some cases, are not included. Contracts that do not have to "
                "be published on simap.ch – below the thresholds, for example – are missing here, just as they "
                "are on simap.ch.",
            ]),
            ("kantone", "How contracts are assigned to cantons", [
                "What counts is the canton the publication gives as the place of performance (the "
                "contract’s address) – the same field simap.ch itself filters on. For a project divided into "
                "lots, each lot’s canton counts: a tender whose lots lie in several cantons is listed under "
                "each of them, marked “{multi}”; an award counts only in the canton of its lot, so that no "
                "total counts it twice.",
                "Where the publication gives no place for the contract or its lots, the contracting "
                "authority’s canton is shown, marked “{fallback}”. Works on national roads in Thurgau or "
                "St. Gallen that FEDRO’s Winterthur branch puts out to tender without a place, for example, "
                "appear under Zurich. Other authorities give their own address as the place of performance; "
                "their own canton is then shown even when the work takes place elsewhere – the data does "
                "not reveal it.",
                "{nocant} All cantons together plus these awards add up to the total on the home page. The "
                "email alert uses the same assignment: a tender is sent for each of its cantons.",
            ]),
            ("zusammenfuehrung", "How companies and contracting authorities are matched", [
                "A company is not always spelled the same way in the publications. Spellings that differ "
                "only in capitalisation, umlauts, accents or punctuation (“CSD INGENIEURE AG” and “CSD "
                "Ingenieure AG”, “Bolliger & Co. AG” and “Bolliger + Co. AG”) are treated as one company, "
                "shown under its most frequent spelling. Units with different names, such as branches, stay "
                "separate. There is no matching against the commercial register.",
                "A company gets its own page once it has {min_c} awards, a contracting authority once it has "
                "{min_b}, and a category (CPV code) once it has {min_s}. Contracting authorities are also "
                "matched by name, "
                "regardless of spaces, hyphens, quotation marks and brackets.",
                "An award to several companies appears on the page of each of them.",
            ]),
            ("betraege", "Amounts, lots and totals", [
                "Amounts are shown as published. An award’s page gives the exact amount; lists show a "
                "rounded figure, with the exact amount on hover and for screen readers.",
                "Totals include only awards in Swiss francs made to a single company. For an award to "
                "several companies the publication gives a price per company: these prices are shown "
                "individually, but are never added up or attributed to an overall contract – in framework "
                "agreements the same ceiling often appears next to every company. Amounts in euros or other "
                "currencies are shown with their currency, never in a column of francs, and left out of "
                "every total.",
                "An amount under CHF 1,000 is almost never the value of a contract but a unit rate (per "
                "hour, item or kilometre, for example): it is marked “{rate}” and left out of every total "
                "and median. So is an amount of up to CHF 5,000 when the publication speaks of staff leasing "
                "or a day or hourly rate (“LSE”, “Personalverleih”, “Tagessatz”, “tarif journalier” and the "
                "like).",
                "simap.ch publishes a project divided into lots as one award per lot. The project’s page "
                "lists every lot; where simap gives the same project price for several lots won by the same "
                "company, totals count it once.",
            ]),
            ("ausgeschlossen", "What is not included", [[
                "Cancelled procedures: simap.ch publishes them in the same feed as awards; they are not shown "
                "here as awards.",
                "Corrections: when a tender or an award is corrected, the version published last applies; "
                "earlier versions are not shown in addition.",
                "Expired tenders: after the submission deadline, a tender’s page stays online for {days} "
                "days, marked “{expired}”. If the award is published in the meantime, it appears at the "
                "same address.",
                "Tenders without a readable submission deadline are not listed as open.",
            ]]),
            ("cpv", "Industries and categories (CPV)", [
                "The classification follows the CPV, the EU’s Common Procurement Vocabulary. An industry is "
                "the first two digits of the code (e.g. 45, construction work), a category the exact "
                "eight-digit code (e.g. 45233000). Category labels come from the official CPV in each "
                "language; the names of the 45 industries are the register’s own short forms.",
                "“{matched}” on company pages and “{similar}” on tender pages are based on the digits that "
                "CPV codes have in common: a general code such as 45000000 (construction work) is not enough "
                "on its own. For companies at least the first four significant digits must match; similar "
                "awards are in "
                "the same industry and the same canton, closest codes first.",
            ]),
            ("daten", "Downloads and subscriptions", [[
                "CSV: {csv_pages} offer their awards as a CSV file – UTF-8 with a BOM, semicolon as the "
                "separator, amounts with a decimal point; one file for all four language versions, with "
                "English column names ({cols}) and the titles in the language of the publication. For "
                "awards to several companies the “Amount” column is left empty. Cells that begin with =, "
                "+, - or @ get a leading apostrophe, so that spreadsheet programs do not run them as "
                "formulas. “Canton source” says where the canton comes from (place: place of performance, "
                "lot: the lot, buyer: the contracting authority’s seat); “Amount note” marks probable unit "
                "rates.",
                "Charts: every chart names its source and links to its data as a CSV file.",
                "Calendar: every open tender offers its submission deadline as a calendar file (.ics).",
                "RSS and email: every canton and every industry has its own RSS feed; the email alert sends "
                "new tenders by canton and industry, free and without an account.",
            ]]),
            ("kontakt", "Contact and error reports", [
                "Errors, questions and suggestions: {mail}; on every award and tender page, “{report}” "
                "opens an email with the publication number in the subject line. The register is run by a "
                "private individual in Switzerland; details of the operator are in the legal notice.",
            ]),
        ],
        "csv_pages": "Canton, contracting authority and company pages",
        "csv_pages_nocomp": "Canton and contracting authority pages",
        "ramp": " From {a} to {b} only part of the awards were captured; these months are striped in the "
                "monthly charts. From {full} on, the register holds the awards the simap.ch interface "
                "returned for each month when they were fetched; there is no check against official totals.",
        "incomplete": " {n} award publications from {months} came through the interface without a title or "
                      "a winner; they are left out of every figure and list.",
        "nocant": "{n} name neither a place nor a contracting authority with a canton; they count in no "
                  "canton, and the canton overview lists them separately.",
        "nocant_zero": "At present every award has a canton.",
        "alert_link": "Go to email alerts",
    },
}


# ------------------------------------------------- design step 2: units, form groups (14.10.2026)
# A money column states its unit once, in its header: 'Betrag (Tsd. CHF)', 'Summe (Mio. CHF)'
# (formato.unit_for / column_cell). The award page's lots keep the exact amount: 'Betrag (CHF)'.
T["sum_l"] = {"de": "Summe", "fr": "Total", "it": "Totale", "en": "Total"}
T["unit_k"] = {"de": "Tsd. CHF", "fr": "milliers de CHF", "it": "migliaia di CHF", "en": "CHF thousand"}
T["unit_m"] = {"de": "Mio. CHF", "fr": "millions de CHF", "it": "milioni di CHF", "en": "CHF million"}
T["unit_chf"] = {"de": "CHF", "fr": "CHF", "it": "CHF", "en": "CHF"}
# The alert form's industries in groups, each one a <details> (genera.ABO_GROUPS): forty pills one
# under the other put the button 1,600 px below the e-mail field on a phone.
META["abo_grp_bau"] = {"de": "Bau und Planung", "fr": "Construction et planification",
                       "it": "Costruzione e progettazione", "en": "Construction and planning"}
META["abo_grp_it"] = {"de": "Informatik und Telekommunikation", "fr": "Informatique et télécommunications",
                      "it": "Informatica e telecomunicazioni", "en": "IT and telecoms"}
META["abo_grp_tech"] = {"de": "Technik, Energie und Umwelt", "fr": "Technique, énergie et environnement",
                        "it": "Tecnica, energia e ambiente", "en": "Engineering, energy and environment"}
META["abo_grp_verkehr"] = {"de": "Verkehr und Sicherheit", "fr": "Transports et sécurité",
                           "it": "Trasporti e sicurezza", "en": "Transport and security"}
META["abo_grp_dienst"] = {"de": "Dienstleistungen, Gesundheit, Bildung", "fr": "Services, santé, formation",
                          "it": "Servizi, sanità, formazione", "en": "Services, health, education"}
META["abo_grp_waren"] = {"de": "Waren und Material", "fr": "Biens et fournitures",
                         "it": "Beni e forniture", "en": "Goods and supplies"}
META["abo_grp_other"] = {"de": "Weitere Branchen", "fr": "Autres branches", "it": "Altri rami",
                         "en": "Other industries"}
# structured data: the country a Dataset covers (schema.org spatialCoverage), and og:locale
COUNTRY = {"de": "Schweiz", "fr": "Suisse", "it": "Svizzera", "en": "Switzerland"}
OG_LOCALE = {"de": "de_CH", "fr": "fr_CH", "it": "it_CH", "en": "en_GB"}


# ------------------------------------------------- step 3a: data, trust, structure (14.10.2026)
# The menu's 'Branchen' opens the 45 CPV divisions (/xx/branche/); the 8-digit Bereiche are their
# second level and keep their URLs (/xx/bereich/).
T["nav_sectors"] = {"de": "Branchen", "fr": "Branches", "it": "Rami", "en": "Industries"}
T["division"] = {"de": "Branche", "fr": "Branche", "it": "Ramo", "en": "Industry"}
T["divisions"] = {"de": "Branchen", "fr": "Branches", "it": "Rami", "en": "Industries"}
# after a count, the noun in lower case ('45 Branches', '45 Rami' reused the menu's label; audit 7.2)
T["divisions_n"] = {"de": "Branchen", "fr": "branches", "it": "rami", "en": "industries"}
# The canton of a record whose publication names no place: the buyer's seat (kantone.py), marked on
# every row and record page that shows it
T["fb_note"] = {"de": "Ort nicht angegeben – Kanton des Auftraggebers",
                "fr": "Lieu non indiqué – canton de l’adjudicateur",
                "it": "Luogo non indicato – cantone del committente",
                "en": "Place not given – canton of the contracting authority"}
T["multi_cantons"] = {"de": "mehrere Kantone", "fr": "plusieurs cantons", "it": "più cantoni",
                      "en": "several cantons"}
T["lot_cantons"] = {"de": "nach den Losen", "fr": "selon les lots", "it": "secondo i lotti", "en": "from the lots"}
T["no_canton"] = {"de": "Ohne Kanton", "fr": "Sans canton", "it": "Senza cantone", "en": "Without a canton"}
# An award amount under CHF 1'000: almost always a unit rate (per hour, item, km), never in a sum
T["rate_flag"] = {"de": "vermutlich Einheitspreis", "fr": "probablement un prix unitaire",
                  "it": "probabilmente un prezzo unitario", "en": "probably a unit rate"}
T["not_chf"] = {"de": "Betrag in Fremdwährung", "fr": "montant en devise étrangère", "it": "importo in valuta estera",
                "en": "amount in a foreign currency"}
T["report_error"] = {"de": "Fehler melden", "fr": "Signaler une erreur", "it": "Segnala un errore",
                     "en": "Report an error"}
T["report_subj"] = {"de": "Fehler", "fr": "Erreur", "it": "Errore", "en": "Error"}
T["simap_btn"] = {"de": "Unterlagen und amtliche Publikation auf simap.ch",
                  "fr": "Documents et publication officielle sur simap.ch",
                  "it": "Documenti e pubblicazione ufficiale su simap.ch",
                  "en": "Documents and official publication on simap.ch"}
IDX["fx_amount"] = {"de": "Betrag in Fremdwährung: {a}", "fr": "Montant en devise étrangère : {a}",
                    "it": "Importo in valuta estera: {a}", "en": "Amount in a foreign currency: {a}"}
# under a CHF total: the unit rates it leaves out (like the awards to several firms)
IDX["sum_no_rates"] = {"de": "ohne {k} vermutliche Einheitspreise", "fr": "sans {k} prix probablement unitaires",
                       "it": "esclusi {k} probabili prezzi unitari", "en": "excluding {k} probable unit rates"}
IDX["sum_no_rates_one"] = {"de": "ohne einen vermutlichen Einheitspreis", "fr": "sans un prix probablement unitaire",
                           "it": "escluso un probabile prezzo unitario", "en": "excluding one probable unit rate"}
IDX["rates_note"] = {
    "de": "Nicht in den Summen und im Median enthalten sind {k} Beträge, die vermutlich Einheitspreise sind (unter "
          "1'000 CHF, oder bis 5'000 CHF mit einem Hinweis auf Personalverleih oder einen Tages- oder Stundensatz).",
    "fr": "Les totaux et la médiane n’incluent pas {k} montants qui sont probablement des prix unitaires (moins de "
          "1\u202f000 CHF, ou jusqu’à 5\u202f000 CHF quand la publication parle de location de services ou d’un "
          "tarif journalier ou horaire).",
    "it": "I totali e la mediana non comprendono {k} importi che sono probabilmente prezzi unitari (sotto i 1'000 "
          "CHF, o fino a 5'000 CHF quando la pubblicazione parla di prestito di personale o di una tariffa "
          "giornaliera od oraria).",
    "en": "Totals and the median exclude {k} amounts that are probably unit rates (under CHF 1,000, or up to CHF "
          "5,000 where the publication speaks of staff leasing or a day or hourly rate).",
}
IDX["rates_note_one"] = {
    "de": "Nicht in den Summen und im Median enthalten ist ein Betrag, der vermutlich ein Einheitspreis ist (unter "
          "1'000 CHF, oder bis 5'000 CHF mit einem Hinweis auf Personalverleih oder einen Tages- oder Stundensatz).",
    "fr": "Les totaux et la médiane n’incluent pas un montant qui est probablement un prix unitaire (moins de "
          "1\u202f000 CHF, ou jusqu’à 5\u202f000 CHF quand la publication parle de location de services ou d’un "
          "tarif journalier ou horaire).",
    "it": "I totali e la mediana non comprendono un importo che è probabilmente un prezzo unitario (sotto i 1'000 "
          "CHF, o fino a 5'000 CHF quando la pubblicazione parla di prestito di personale o di una tariffa "
          "giornaliera od oraria).",
    "en": "Totals and the median exclude one amount that is probably a unit rate (under CHF 1,000, or up to CHF "
          "5,000 where the publication speaks of staff leasing or a day or hourly rate).",
}
# the other firms of an award to several, on a company page's row: partners in one framework read as
# the same award twice (ao-/ap-automobile-schweiz-ag, audit 14.10.2026)
IDX["with_firms"] = {"de": "mit {names}", "fr": "avec {names}", "it": "con {names}", "en": "with {names}"}
IDX["and_more"] = {"de": "{k} weiteren", "fr": "{k} autres", "it": "altre {k}", "en": "{k} others"}
# a chart's source and its data, under every chart
IDX["chart_src"] = {"de": "Quelle: simap.ch, eigene Auswertung", "fr": "Source : simap.ch, analyse propre",
                    "it": "Fonte: simap.ch, elaborazione propria", "en": "Source: simap.ch, our analysis"}
IDX["chart_csv"] = {"de": "Daten als CSV", "fr": "Données en CSV", "it": "Dati in CSV", "en": "Data as CSV"}
# the open tenders hub
IDX["multi_note"] = {
    "de": "Eine Ausschreibung mit Losen in mehreren Kantonen zählt in jedem dieser Kantone.",
    "fr": "Un appel d’offres dont les lots se situent dans plusieurs cantons compte dans chacun d’eux.",
    "it": "Un bando con lotti in più cantoni conta in ciascuno di essi.",
    "en": "A tender with lots in several cantons counts in each of them.",
}
IDX["nodl_note"] = {
    "de": "{n} Ausschreibungen ohne lesbare Eingabefrist sind nicht aufgeführt.",
    "fr": "{n} appels d’offres sans délai de remise lisible ne sont pas listés.",
    "it": "{n} bandi senza un termine d’inoltro leggibile non sono elencati.",
    "en": "{n} tenders without a readable submission deadline are not listed.",
}
# the canton overview: the awards that count in no canton, so that the cantons add up to the total
IDX["nocant_lead"] = {
    "de": "{n} nennen weder einen Ort noch einen Auftraggeber mit Kanton. Alle Kantone zusammen und diese "
          "Zuschläge ergeben die {total} der Startseite.",
    "fr": "{n} n’indiquent ni lieu ni adjudicateur avec canton. Avec ces adjudications, la somme de tous les "
          "cantons correspond aux {total} de la page d’accueil.",
    "it": "{n} non indicano né un luogo né un committente con cantone. Sommando tutti i cantoni e queste "
          "aggiudicazioni si ottengono le {total} della pagina iniziale.",
    "en": "{n} name neither a place nor a contracting authority with a canton. All cantons together and "
          "these awards make up the {total} on the home page.",
}
# the home: who the site is for, and the two company counts
META["audience"] = {
    "de": "Für Unternehmen, die öffentliche Ausschreibungen suchen, und für alle, die wissen wollen, wer "
          "die Aufträge gewinnt.",
    "fr": "Pour les entreprises qui cherchent des appels d’offres publics, et pour tous ceux qui veulent "
          "savoir qui remporte les marchés.",
    "it": "Per le imprese che cercano bandi pubblici e per chi vuole sapere chi si aggiudica gli appalti.",
    "en": "For companies looking for public tenders, and for anyone who wants to know who wins the "
          "contracts.",
}
META["home_firms_tile"] = {"de": "Unternehmen, davon {k} mit eigener Seite",
                           "fr": "entreprises, dont {k} avec leur propre page",
                           "it": "imprese, di cui {k} con una pagina propria",
                           "en": "companies, {k} with a page of their own"}
META["home_firms_tile_one"] = {"de": "Unternehmen", "fr": "entreprise", "it": "impresa", "en": "company"}
# the 45 divisions: an index and one award page each
IDX["div_index_h1"] = {"de": "Öffentliche Aufträge nach Branche", "fr": "Marchés publics par branche",
                       "it": "Appalti pubblici per ramo", "en": "Public contracts by industry"}
IDX["div_index_lead"] = {
    "de": "Die {n} Branchen des CPV (die ersten zwei Ziffern des Codes) mit ihren offenen Ausschreibungen "
          "und publizierten Zuschlägen. Jede Branche umfasst viele einzelne Bereiche (genauer "
          "achtstelliger Code).",
    "fr": "Les {n} branches du CPV (les deux premiers chiffres du code) avec leurs appels d’offres en "
          "cours et leurs adjudications publiées. Chaque branche regroupe de nombreux domaines détaillés "
          "(code exact à huit chiffres).",
    "it": "I {n} rami del CPV (le prime due cifre del codice) con i loro bandi aperti e le aggiudicazioni "
          "pubblicate. Ogni ramo comprende molte categorie specifiche (codice esatto di otto cifre).",
    "en": "The {n} industries of the CPV (the first two digits of the code) with their open tenders and "
          "published awards. Each industry covers many specific categories (the exact eight-digit code).",
}
IDX["div_index_title"] = {"de": "Öffentliche Aufträge nach Branche — CPV-Übersicht",
                          "fr": "Marchés publics par branche — aperçu CPV",
                          "it": "Appalti pubblici per ramo — panoramica CPV",
                          "en": "Public contracts by industry — CPV overview"}
IDX["div_index_desc"] = {
    "de": "Die {n} Branchen der öffentlichen Beschaffung in der Schweiz: offene Ausschreibungen und "
          "Zuschläge je Branche, mit Unternehmen und Auftraggebern.",
    "fr": "Les {n} branches des marchés publics en Suisse : appels d’offres en cours et adjudications par "
          "branche, avec entreprises et adjudicateurs.",
    "it": "I {n} rami degli appalti pubblici in Svizzera: bandi aperti e aggiudicazioni per ramo, con "
          "imprese e committenti.",
    "en": "The {n} industries of Swiss public procurement: open tenders and awards per industry, with "
          "companies and contracting authorities.",
}
IDX["col_open"] = {"de": "Offen", "fr": "En cours", "it": "Aperti", "en": "Open"}
IDX["all_bereiche"] = {"de": "Alle {n} Bereiche von A bis Z (genauer CPV-Code)",
                       "fr": "Les {n} domaines de A à Z (code CPV exact)",
                       "it": "Tutte le {n} categorie dalla A alla Z (codice CPV esatto)",
                       "en": "All {n} categories from A to Z (exact CPV code)"}
META["div_suffix"] = {"de": " — öffentliche Aufträge", "fr": " — marchés publics",
                      "it": " — appalti pubblici", "en": " — public contracts"}
META["div_suffix_short"] = {"de": " — Zuschläge", "fr": " — adjudications", "it": " — aggiudicazioni",
                            "en": " — awards"}
META["div_lead"] = {
    "de": "{n} an {f} in der Branche «{name}», publiziert auf simap.ch.",
    "fr": "{n} en faveur de {f} dans la branche « {name} », publiées sur simap.ch.",
    "it": "{n} a favore di {f} nel ramo «{name}», pubblicate su simap.ch.",
    "en": "{n} to {f} in the “{name}” industry, published on simap.ch.",
}
META["div_desc"] = {
    "de": "Branche «{name}» (CPV {code}): {n} an {f} – die Unternehmen und Auftraggeber mit den meisten "
          "Zuschlägen, nach Kanton.",
    "fr": "Branche « {name} » (CPV {code}) : {n} en faveur de {f} – entreprises et adjudicateurs les plus "
          "actifs, par canton.",
    "it": "Ramo «{name}» (CPV {code}): {n} a favore di {f} – le imprese e i committenti più attivi, per "
          "cantone.",
    "en": "The “{name}” industry (CPV {code}): {n} to {f} – the companies and contracting authorities "
          "with the most awards, by canton.",
}
META["div_desc_short"] = {
    "de": "Branche «{name}» (CPV {code}): {n} an {f}.",
    "fr": "Branche « {name} » (CPV {code}) : {n} en faveur de {f}.",
    "it": "Ramo «{name}» (CPV {code}): {n} a favore di {f}.",
    "en": "The “{name}” industry (CPV {code}): {n} to {f}.",
}
IDX["div_none"] = {
    "de": "In dieser Branche ist noch kein Zuschlag publiziert.",
    "fr": "Aucune adjudication n’a encore été publiée dans cette branche.",
    "it": "In questo ramo non è ancora stata pubblicata alcuna aggiudicazione.",
    "en": "No award has been published in this industry yet.",
}
IDX["div_buyers_h"] = {"de": "Auftraggeber", "fr": "Adjudicateurs", "it": "Committenti",
                       "en": "Contracting authorities"}
IDX["div_sectors_h"] = {"de": "Bereiche dieser Branche (genauer CPV-Code)",
                        "fr": "Domaines de cette branche (code CPV exact)",
                        "it": "Categorie di questo ramo (codice CPV esatto)",
                        "en": "Categories in this industry (exact CPV code)"}
IDX["mc_title_div"] = {"de": "Zuschläge pro Monat in dieser Branche", "fr": "Adjudications par mois dans cette branche",
                       "it": "Aggiudicazioni al mese in questo ramo", "en": "Awards per month in this industry"}
IDX["top_n"] = {"de": "die {k} mit den meisten Zuschlägen", "fr": "les {k} ayant obtenu le plus d’adjudications",
                "it": "le {k} con più aggiudicazioni", "en": "the {k} with the most awards"}
IDX["top_n_b"] = {"de": "die {k} mit den meisten Zuschlägen", "fr": "les {k} ayant attribué le plus d’adjudications",
                  "it": "i {k} con più aggiudicazioni", "en": "the {k} with the most awards"}
IDX["of_division"] = {"de": "Branche «{name}»", "fr": "Branche « {name} »", "it": "Ramo «{name}»",
                      "en": "The “{name}” industry"}
# a sector page's own numbers, in one sentence (the thin CPV pages, technical audit 14.10.2026)
IDX["stats_sum"] = {"de": "Summe der publizierten Beträge: {v}.", "fr": "Total des montants publiés : {v}.",
                    "it": "Totale degli importi pubblicati: {v}.", "en": "Total of published amounts: {v}."}
IDX["stats_buyer"] = {"de": "Häufigster Auftraggeber: {b} ({n}).", "fr": "Adjudicateur le plus fréquent : {b} ({n}).",
                      "it": "Committente più frequente: {b} ({n}).", "en": "Most frequent contracting authority: {b} ({n})."}
IDX["stats_firm"] = {"de": "Häufigstes Unternehmen: {c} ({n}).", "fr": "Entreprise la plus fréquente : {c} ({n}).",
                     "it": "Impresa più frequente: {c} ({n}).", "en": "Most frequent company: {c} ({n})."}
IDX["stats_div"] = {"de": "Der Bereich gehört zur Branche {d}.", "fr": "Ce domaine fait partie de la branche {d}.",
                    "it": "Questa categoria fa parte del ramo {d}.", "en": "This category belongs to the {d} industry."}
T["by_amount"] = {"de": "nach Betrag", "fr": "par montant", "it": "per importo", "en": "by amount"}
IDX["by_division_awards"] = {"de": "Zuschläge nach Branche", "fr": "Adjudications par branche",
                             "it": "Aggiudicazioni per ramo", "en": "Awards by industry"}
IDX["all_divisions"] = {"de": "Alle Branchen", "fr": "Toutes les branches", "it": "Tutti i rami",
                        "en": "All industries"}
IDX["to_divisions"] = {"de": "Die {n} Branchen im Überblick", "fr": "Les {n} branches en un coup d’œil",
                       "it": "I {n} rami in sintesi", "en": "The {n} industries at a glance"}
# the two pages Brevo sends people to: one language each (from the path, ?lang or the browser)
META["abo_from"] = {
    "de": "Absender: auftragsregister.ch <{mail}>.",
    "fr": "Expéditeur : auftragsregister.ch <{mail}>.",
    "it": "Mittente: auftragsregister.ch <{mail}>.",
    "en": "Sender: auftragsregister.ch <{mail}>.",
}
META["abo_when"] = {
    "de": "Die Abo-E-Mails kommen an Werktagen, an denen neue Ausschreibungen zu Ihrer Auswahl erschienen sind, "
          "meist am Vormittag; an Tagen ohne solche Ausschreibungen kommt keine.",
    "fr": "Les e-mails d’alerte arrivent les jours ouvrables où de nouveaux appels d’offres correspondant à votre "
          "sélection ont paru, le plus souvent dans la matinée ; les autres jours, aucun.",
    "it": "Le e-mail dell’avviso arrivano nei giorni feriali in cui sono usciti nuovi bandi corrispondenti alla "
          "sua scelta, per lo più in mattinata; negli altri giorni nessuna.",
    "en": "Alert emails arrive on working days when new tenders matching your selection have appeared, usually "
          "in the morning; on other days, none is sent.",
}
META["abo_spam"] = {
    "de": "Keine E-Mail erhalten? Bitte prüfen Sie Ihren Spam-Ordner.",
    "fr": "Rien reçu ? Vérifiez votre dossier de courrier indésirable.",
    "it": "Non ha ricevuto l’e-mail? Controlli la cartella dello spam.",
    "en": "Nothing arrived? Please check your spam folder.",
}
META["abo_change"] = {
    "de": "Auswahl ändern: Melden Sie sich über den Link am Ende jeder E-Mail ab und abonnieren Sie dann mit "
          "der neuen Auswahl erneut.",
    "fr": "Pour modifier votre sélection : désabonnez-vous par le lien au bas de chaque e-mail, puis "
          "abonnez-vous à nouveau avec la nouvelle sélection.",
    "it": "Per cambiare la scelta: si cancelli con il link in fondo a ogni e-mail e si iscriva di nuovo con "
          "la nuova scelta.",
    "en": "To change your selection, unsubscribe with the link at the bottom of any email and subscribe again "
          "with the new selection.",
}
META["abo_lang_label"] = {"de": "Diese Seite in", "fr": "Cette page en", "it": "Questa pagina in",
                          "en": "This page in"}


# ------------------------------------------- step 3b (15.10.2026): the interactive layer
# The search in the header of every page (its field's name and button), the search page, the A–Z
# letter pages, the long lists cut to their first rows, the company finder on the home.
T["search"] = {"de": "Suche", "fr": "Recherche", "it": "Ricerca", "en": "Search"}
T["search_go"] = {"de": "Suchen", "fr": "Rechercher", "it": "Cerca", "en": "Search"}
META["search_title"] = {"de": "Suche im Register", "fr": "Recherche dans le registre",
                        "it": "Ricerca nel registro", "en": "Search the register"}
META["search_desc"] = {
    "de": "Unternehmen, Auftraggeber, offene Ausschreibungen, Branchen und Kantone im Register der "
          "öffentlichen Aufträge der Schweiz suchen.",
    "fr": "Rechercher entreprises, adjudicateurs, appels d’offres en cours, branches et cantons dans le "
          "registre des marchés publics suisses.",
    "it": "Cercare imprese, committenti, bandi aperti, rami e cantoni nel registro degli appalti pubblici "
          "svizzeri.",
    "en": "Search companies, contracting authorities, open tenders, industries and cantons in the register "
          "of Swiss public contracts.",
}
META["search_lead"] = {
    "de": "Unternehmen, Auftraggeber, offene Ausschreibungen, Branchen und Kantone – nach Name oder Thema, "
          "in jeder Landessprache: «Reinigung» findet auch «nettoyage».",
    "fr": "Entreprises, adjudicateurs, appels d’offres en cours, branches et cantons – par nom ou par thème, "
          "dans chaque langue nationale : « nettoyage » trouve aussi « Reinigung ».",
    "it": "Imprese, committenti, bandi aperti, rami e cantoni – per nome o per tema, in ogni lingua "
          "nazionale: «pulizia» trova anche «Reinigung».",
    "en": "Companies, contracting authorities, open tenders, industries and cantons – by name or by topic, "
          "in any national language: “cleaning” also finds “Reinigung”.",
}
META["search_label"] = {"de": "Suchbegriff", "fr": "Terme recherché", "it": "Termine di ricerca",
                        "en": "Search term"}
META["search_nojs"] = {
    "de": "Die Suche braucht JavaScript. Ohne JavaScript führen diese Verzeichnisse zu jedem Eintrag "
          "des Registers:",
    "fr": "La recherche nécessite JavaScript. Sans JavaScript, ces répertoires mènent à chaque entrée "
          "du registre :",
    "it": "La ricerca richiede JavaScript. Senza JavaScript, questi elenchi portano a ogni voce del "
          "registro:",
    "en": "Search needs JavaScript. Without it, these directories lead to every entry in the register:",
}
META["search_dirs"] = {"de": "Verzeichnisse", "fr": "Répertoires", "it": "Elenchi", "en": "Directories"}
META["az_companies"] = {"de": "Unternehmen von A bis Z", "fr": "Entreprises de A à Z",
                        "it": "Imprese dalla A alla Z", "en": "Companies from A to Z"}
META["az_buyers"] = {"de": "Auftraggeber von A bis Z", "fr": "Adjudicateurs de A à Z",
                     "it": "Committenti dalla A alla Z", "en": "Contracting authorities from A to Z"}
# a letter page of the company and buyer indexes: '{l}' is the letter ('A', '0–9')
META["letter_companies_title"] = {"de": "Unternehmen mit Anfangsbuchstabe {l} – öffentliche Aufträge",
                                  "fr": "Entreprises commençant par {l} – marchés publics",
                                  "it": "Imprese con iniziale {l} – appalti pubblici",
                                  "en": "Companies starting with {l} – public contracts"}
META["letter_companies_h1"] = {"de": "Unternehmen: {l}", "fr": "Entreprises : {l}", "it": "Imprese: {l}",
                               "en": "Companies: {l}"}
META["letter_companies_desc"] = {
    "de": "{n} Unternehmen mit dem Anfangsbuchstaben {l}, jedes mit seinen öffentlichen Aufträgen in der "
          "Schweiz.",
    "fr": "{n} entreprises commençant par {l}, chacune avec ses marchés publics en Suisse.",
    "it": "{n} imprese con iniziale {l}, ognuna con i suoi appalti pubblici in Svizzera.",
    "en": "{n} companies starting with {l}, each with its public contracts in Switzerland.",
}
META["letter_buyers_title"] = {"de": "Auftraggeber mit Anfangsbuchstabe {l} – öffentliche Aufträge",
                               "fr": "Adjudicateurs commençant par {l} – marchés publics",
                               "it": "Committenti con iniziale {l} – appalti pubblici",
                               "en": "Contracting authorities starting with {l} – public contracts"}
META["letter_buyers_h1"] = {"de": "Auftraggeber: {l}", "fr": "Adjudicateurs : {l}", "it": "Committenti: {l}",
                            "en": "Contracting authorities: {l}"}
META["letter_buyers_desc"] = {
    "de": "{n} Auftraggeber mit dem Anfangsbuchstaben {l}, jeder mit den Zuschlägen, die er auf simap.ch "
          "publiziert hat.",
    "fr": "{n} adjudicateurs commençant par {l}, chacun avec les adjudications publiées sur simap.ch.",
    "it": "{n} committenti con iniziale {l}, ognuno con le aggiudicazioni pubblicate su simap.ch.",
    "en": "{n} contracting authorities starting with {l}, each with the awards it published on simap.ch.",
}
META["letters_lead"] = {
    "de": "Nach Anfangsbuchstabe; jeder Buchstabe hat seine eigene Seite.",
    "fr": "Par initiale ; chaque lettre a sa propre page.",
    "it": "Per iniziale; ogni lettera ha la sua pagina.",
    "en": "By first letter; each letter has a page of its own.",
}
META["letter_prev"] = {"de": "Vorheriger Buchstabe", "fr": "Lettre précédente", "it": "Lettera precedente",
                       "en": "Previous letter"}
META["letter_next"] = {"de": "Nächster Buchstabe", "fr": "Lettre suivante", "it": "Lettera successiva",
                       "en": "Next letter"}
# a list over 300 rows shows its first 100; the whole list is a page of its own (without JavaScript)
# or loaded in place (with it)
IDX["show_all_n"] = {"de": "Alle {n} anzeigen", "fr": "Afficher les {n}", "it": "Mostra tutti i {n}",
                     "en": "Show all {n}"}
IDX["first_n_note"] = {
    "de": "Die {n} Ausschreibungen mit der nächsten Eingabefrist, von {total}.",
    "fr": "Les {n} appels d’offres dont le délai est le plus proche, sur {total}.",
    "it": "I {n} bandi con la scadenza più vicina, su {total}.",
    "en": "The {n} tenders with the nearest deadlines, out of {total}.",
}
IDX["rest_note"] = {
    "de": "Die übrigen {n} stehen in den Listen der Kantone und Branchen.",
    "fr": "Les {n} autres figurent dans les listes des cantons et des branches.",
    "it": "Gli altri {n} si trovano negli elenchi dei cantoni e dei rami.",
    "en": "The other {n} are in the canton and industry lists.",
}
META["all_list_title"] = {"de": "{h} – vollständige Liste", "fr": "{h} – liste complète",
                          "it": "{h} – elenco completo", "en": "{h} – full list"}
META["all_list_lead"] = {
    "de": "Alle {n} offenen Ausschreibungen dieser Liste auf einer Seite, die nächste Eingabefrist zuerst.",
    "fr": "Les {n} appels d’offres en cours de cette liste sur une seule page, le délai le plus proche "
          "en premier.",
    "it": "Tutti i {n} bandi aperti di questo elenco su una sola pagina, la scadenza più vicina per prima.",
    "en": "All {n} open tenders of this list on one page, the nearest deadline first.",
}
META["all_list_back"] = {"de": "Zur kurzen Liste", "fr": "Retour à la liste courte", "it": "Torna all’elenco breve",
                         "en": "Back to the short list"}
# the home's company finder (the door 'Unternehmen finden' becomes a search box)
META["finder_label"] = {"de": "Name des Unternehmens", "fr": "Nom de l’entreprise", "it": "Nome dell’impresa",
                        "en": "Company name"}
META["finder_ph"] = {"de": "z. B. Implenia", "fr": "p. ex. Implenia", "it": "ad es. Implenia",
                     "en": "e.g. Implenia"}
META["finder_sub"] = {
    "de": "{n} Unternehmen mit mindestens einem Zuschlag, {k} davon mit eigener Seite.",
    "fr": "{n} entreprises ayant obtenu au moins une adjudication, dont {k} avec leur propre page.",
    "it": "{n} imprese con almeno un’aggiudicazione, di cui {k} con una pagina propria.",
    "en": "{n} companies with at least one award, {k} of them with a page of their own.",
}
META["finder_az"] = {"de": "Von A bis Z", "fr": "De A à Z", "it": "Dalla A alla Z", "en": "From A to Z"}
# the alert form: the e-mail field's error, tied to the field (aria-describedby)
META["abo_email_missing"] = {"de": "Bitte geben Sie Ihre E-Mail-Adresse ein.",
                             "fr": "Veuillez saisir votre adresse e-mail.",
                             "it": "Inserisca il suo indirizzo e-mail.",
                             "en": "Please enter your email address."}
META["abo_email_bad"] = {
    "de": "Diese E-Mail-Adresse ist nicht gültig. Beispiel: name@firma.ch",
    "fr": "Cette adresse e-mail n’est pas valable. Exemple : nom@entreprise.ch",
    "it": "Questo indirizzo e-mail non è valido. Esempio: nome@azienda.ch",
    "en": "This email address is not valid. Example: name@company.ch",
}

# The pill to a list of open tenders on the award pages of a Bereich, a Branche and a canton, without its
# count: the count changed every night and rewrote 1'700 pages for that one number; /stand.js adds it from
# /daten/offen-n.json (step 3b)
IDX["open_in_sector_x"] = {"de": "Offene Ausschreibungen der Branche «{name}»",
                           "fr": "Appels d’offres en cours dans la branche « {name} »",
                           "it": "Bandi aperti nel ramo «{name}»", "en": "Open tenders in the “{name}” industry"}
IDX["open_in_x"] = {"de": "Offene Ausschreibungen im Kanton {c}", "fr": "Appels d’offres en cours dans le canton {of}",
                    "it": "Bandi aperti nel Canton {c}", "en": "Open tenders in the canton of {c}"}

# The scripts' words (js/*.js read them from the data genera.py writes into each script): every label
# that depends on the reader's clock lives here and nowhere in the static pages, which carry absolute
# dates only (the static HTML must not say 'heute', 'morgen', 'noch 5 Tage' or 'seit gestern').
JS: dict[str, dict[str, str]] = {
    # the deadlines, from the reader's clock (stand.js)
    "due_tomorrow": {"de": "läuft morgen ab", "fr": "expire demain", "it": "scade domani",
                     "en": "closes tomorrow"},
    "due_days": {"de": "noch {n} Tage", "fr": "encore {n} jours", "it": "ancora {n} giorni",
                 "en": "{n} days left"},
    "due_over": {"de": "abgelaufen", "fr": "expiré", "it": "scaduto", "en": "closed"},
    "hidden_1": {"de": "1 inzwischen abgelaufene Ausschreibung ausgeblendet",
                 "fr": "1 appel d’offres expiré entre-temps n’est plus affiché",
                 "it": "1 bando scaduto nel frattempo non è più mostrato",
                 "en": "1 tender has closed since and is hidden"},
    "hidden_n": {"de": "{n} inzwischen abgelaufene Ausschreibungen ausgeblendet",
                 "fr": "{n} appels d’offres expirés entre-temps ne sont plus affichés",
                 "it": "{n} bandi scaduti nel frattempo non sono più mostrati",
                 "en": "{n} tenders have closed since and are hidden"},
    # the home's 'neu' badge while its day is today or yesterday on the reader's clock
    "new_today": {"de": "{m} neue heute", "fr": "{m} nouveaux aujourd’hui", "it": "{m} nuovi oggi",
                  "en": "{m} new today"},
    "new_today_1": {"de": "1 neue heute", "fr": "1 nouveau aujourd’hui", "it": "1 nuovo oggi",
                    "en": "1 new today"},
    "new_yday": {"de": "{m} neue seit gestern", "fr": "{m} nouveaux depuis hier", "it": "{m} nuovi da ieri",
                 "en": "{m} new since yesterday"},
    "new_yday_1": {"de": "1 neue seit gestern", "fr": "1 nouveau depuis hier", "it": "1 nuovo da ieri",
                   "en": "1 new since yesterday"},
    "top": {"de": "Nach oben", "fr": "Haut de page", "it": "Torna su", "en": "Back to top"},
    "ph": {"de": "Unternehmen, Auftraggeber, Ausschreibung, Branche …",
           "fr": "Entreprise, adjudicateur, appel d’offres, branche …",
           "it": "Impresa, committente, bando, ramo …",
           "en": "Company, contracting authority, tender, industry …"},
    # the search (suche.js), its groups in this order
    "g_t": {"de": "Offene Ausschreibungen", "fr": "Appels d’offres en cours", "it": "Bandi aperti",
            "en": "Open tenders"},
    "g_u": {"de": "Unternehmen", "fr": "Entreprises", "it": "Imprese", "en": "Companies"},
    "g_b": {"de": "Auftraggeber", "fr": "Adjudicateurs", "it": "Committenti", "en": "Contracting authorities"},
    "g_s": {"de": "Branchen und Bereiche", "fr": "Branches et domaines", "it": "Rami e categorie",
            "en": "Industries and categories"},
    "g_k": {"de": "Kantone", "fr": "Cantons", "it": "Cantoni", "en": "Cantons"},
    "g_p": {"de": "Seiten", "fr": "Pages", "it": "Pagine", "en": "Pages"},
    "all_t": {"de": "Alle offenen Ausschreibungen zu «{q}»", "fr": "Tous les appels d’offres en cours pour « {q} »",
              "it": "Tutti i bandi aperti per «{q}»", "en": "All open tenders matching “{q}”"},
    "all_r": {"de": "Alle Ergebnisse für «{q}»", "fr": "Tous les résultats pour « {q} »",
              "it": "Tutti i risultati per «{q}»", "en": "All results for “{q}”"},
    "res_h": {"de": "Ergebnisse für «{q}»", "fr": "Résultats pour « {q} »", "it": "Risultati per «{q}»",
              "en": "Results for “{q}”"},
    "none": {"de": "Keine Treffer für «{q}».", "fr": "Aucun résultat pour « {q} ».",
             "it": "Nessun risultato per «{q}».", "en": "No results for “{q}”."},
    "none_hint": {"de": "Versuchen Sie ein anderes Wort, einen Teil des Namens oder die Verzeichnisse unten.",
                  "fr": "Essayez un autre mot, une partie du nom ou les répertoires ci-dessous.",
                  "it": "Provi un’altra parola, una parte del nome o gli elenchi qui sotto.",
                  "en": "Try another word, part of the name, or the directories below."},
    "n_res": {"de": "{n} Treffer", "fr": "{n} résultats", "it": "{n} risultati", "en": "{n} results"},
    "n_res_1": {"de": "1 Treffer", "fr": "1 résultat", "it": "1 risultato", "en": "1 result"},
    "n_sug": {"de": "{n} Vorschläge, mit den Pfeiltasten wählen", "fr": "{n} suggestions ; choisissez avec les flèches",
              "it": "{n} suggerimenti; scelga con i tasti freccia", "en": "{n} suggestions; use the arrow keys to choose"},
    "more": {"de": "{n} weitere anzeigen", "fr": "Afficher les {n} autres", "it": "Mostra gli altri {n}",
             "en": "Show {n} more"},
    "aw_1": {"de": "1 Zuschlag", "fr": "1 adjudication", "it": "1 aggiudicazione", "en": "1 award"},
    "aw_n": {"de": "{n} Zuschläge", "fr": "{n} adjudications", "it": "{n} aggiudicazioni", "en": "{n} awards"},
    "open_1": {"de": "1 offen", "fr": "1 en cours", "it": "1 aperto", "en": "1 open"},
    "open_n": {"de": "{n} offen", "fr": "{n} en cours", "it": "{n} aperti", "en": "{n} open"},
    "to_award": {"de": "Seite des Zuschlags", "fr": "page de l’adjudication", "it": "pagina dell’aggiudicazione",
                 "en": "award page"},
    "k_canton": {"de": "Kanton", "fr": "Canton", "it": "Cantone", "en": "Canton"},
    "k_div": {"de": "Branche", "fr": "Branche", "it": "Ramo", "en": "Industry"},
    "k_sec": {"de": "Bereich", "fr": "Domaine", "it": "Categoria", "en": "Category"},
    "until": {"de": "bis {d}", "fr": "jusqu’au {d}", "it": "entro il {d}", "en": "due {d}"},
    "loading": {"de": "Wird geladen …", "fr": "Chargement …", "it": "Caricamento …", "en": "Loading …"},
    "failed": {"de": "Die Daten konnten nicht geladen werden.", "fr": "Les données n’ont pas pu être chargées.",
               "it": "Non è stato possibile caricare i dati.", "en": "The data could not be loaded."},
    # the filters of the tender lists (liste.js)
    "f_label": {"de": "Ausschreibungen filtern", "fr": "Filtrer les appels d’offres", "it": "Filtra i bandi",
                "en": "Filter tenders"},
    "f_q": {"de": "Titel oder Auftraggeber", "fr": "Titre ou adjudicateur", "it": "Titolo o committente",
            "en": "Title or contracting authority"},
    "f_k_all": {"de": "Alle Kantone", "fr": "Tous les cantons", "it": "Tutti i cantoni", "en": "All cantons"},
    "f_b_all": {"de": "Alle Branchen", "fr": "Toutes les branches", "it": "Tutti i rami", "en": "All industries"},
    "f_soon": {"de": "Frist in den nächsten 7 Tagen", "fr": "Délai dans les 7 prochains jours",
               "it": "Scadenza entro 7 giorni", "en": "Deadline within 7 days"},
    "f_clear": {"de": "Filter zurücksetzen", "fr": "Réinitialiser les filtres", "it": "Azzera i filtri",
                "en": "Clear filters"},
    # the alert under its one name per language, prefilled with the selection
    "f_abo": {"de": "E-Mail-Abo für diese Auswahl", "fr": "Alerte e-mail pour cette sélection",
              "it": "Avviso e-mail per questa selezione", "en": "Email alert for this selection"},
    "f_count": {"de": "{n} von {m} offenen Ausschreibungen", "fr": "{n} sur {m} appels d’offres en cours",
                "it": "{n} di {m} bandi aperti", "en": "{n} of {m} open tenders"},
    "f_none": {"de": "Keine offene Ausschreibung entspricht dieser Auswahl.",
               "fr": "Aucun appel d’offres en cours ne correspond à cette sélection.",
               "it": "Nessun bando aperto corrisponde a questa selezione.",
               "en": "No open tender matches this selection."},
    "multi": {"de": "mehrere Kantone", "fr": "plusieurs cantons", "it": "più cantoni", "en": "several cantons"},
    # the alert form (abo.js)
    "sel": {"de": "({n} ausgewählt)", "fr": "(sélection : {n})", "it": "(selezionati: {n})", "en": "({n} selected)"},
    "pv": {"de": "Zurzeit {open} · ≈ {w} neue pro Woche", "fr": "Actuellement {open} · ≈ {w} nouveaux par semaine",
           "it": "Attualmente {open} · ≈ {w} nuovi alla settimana", "en": "Currently {open} · ≈ {w} new a week"},
    "pv_lt": {"de": "Zurzeit {open} · weniger als eine neue pro Woche",
              "fr": "Actuellement {open} · moins d’un nouveau par semaine",
              "it": "Attualmente {open} · meno di un nuovo bando alla settimana",
              "en": "Currently {open} · fewer than one new a week"},
    "pv_note": {"de": "für die gewählten Kantone und Branchen, berechnet aus den letzten 8 Wochen",
                "fr": "pour les cantons et branches choisis, d’après les 8 dernières semaines",
                "it": "per i cantoni e i rami scelti, in base alle ultime 8 settimane",
                "en": "for the chosen cantons and industries, based on the last 8 weeks"},
    # a canton's awards in one industry (kb.js)
    "kb_h": {"de": "{div} im Kanton {name}", "fr": "{div} dans le canton {of}", "it": "{div} nel Canton {name}",
             "en": "{div} in the canton of {name}"},
    "kb_lead": {"de": "{n} an {f} (Daten dieses Registers).",
                "fr": "{n} en faveur de {f} (données de ce registre).",
                "it": "{n} a favore di {f} (dati di questo registro).",
                "en": "{n} to {f} (data from this register)."},
    "kb_f1": {"de": "1 Unternehmen", "fr": "1 entreprise", "it": "1 impresa", "en": "1 company"},
    "kb_fn": {"de": "{n} Unternehmen", "fr": "{n} entreprises", "it": "{n} imprese", "en": "{n} companies"},
    "kb_top": {"de": "Unternehmen mit den meisten Zuschlägen", "fr": "Entreprises avec le plus d’adjudications",
               "it": "Imprese con più aggiudicazioni", "en": "Companies with the most awards"},
    "kb_recent": {"de": "Die {k} neuesten von {n}", "fr": "Les {k} plus récentes sur {n}",
                  "it": "Le {k} più recenti su {n}", "en": "The {k} most recent of {n}"},
    "kb_all": {"de": "Die Branche in der ganzen Schweiz", "fr": "La branche dans toute la Suisse",
               "it": "Il ramo in tutta la Svizzera", "en": "The industry across Switzerland"},
    "kb_csv": {"de": "Alle Zuschläge des Kantons als CSV", "fr": "Toutes les adjudications du canton en CSV",
               "it": "Tutte le aggiudicazioni del cantone in CSV", "en": "All the canton’s awards as CSV"},
    "kb_close": {"de": "Schliessen", "fr": "Fermer", "it": "Chiudi", "en": "Close"},
    "kb_hint": {"de": "Branche wählen: die Zuschläge dieses Kantons und die Unternehmen mit den meisten davon.",
                "fr": "Choisir une branche : les adjudications de ce canton et les entreprises qui en ont le plus.",
                "it": "Scelga un ramo: le aggiudicazioni di questo cantone e le imprese che ne hanno ottenute di più.",
                "en": "Pick an industry: this canton’s awards and the companies with the most of them."},
}

# ---------------------------------------------------------------- step 4: design A2 "Brass"
# The phone menu (a <details> in the header of every page) and the home in the A2 design (15.10.2026):
# the hero's eyebrow and its brass pillars, the map of the open tenders per canton (legend, attribution,
# read-out), the section eyebrows and the alarm band. The map's read-out words for the script are in JS.
T["menu"] = {"de": "Menü", "fr": "Menu", "it": "Menu", "en": "Menu"}
META["home_eyebrow"] = {"de": "{span} · Daten vom {d}", "fr": "{span} · état des données : {d}",
                        "it": "{span} · stato dei dati: {d}", "en": "{span} · data as of {d}"}
META["sky_peak"] = {"de": "{m} · meiste Zuschläge", "fr": "{m} · record d’adjudications",
                    "it": "{m} · record di aggiudicazioni", "en": "{m} · most awards"}
META["map_eyebrow"] = {"de": "01 · Karte · Daten vom {d}", "fr": "01 · Carte · état des données : {d}",
                       "it": "01 · Mappa · stato dei dati: {d}", "en": "01 · Map · data as of {d}"}
META["map_legend"] = {"de": "Je heller ein Kanton, desto mehr offene Ausschreibungen.",
                      "fr": "Plus un canton est clair, plus il compte d’appels d’offres en cours.",
                      "it": "Più un cantone è chiaro, più bandi aperti conta.",
                      "en": "The brighter a canton, the more open tenders it has."}
META["map_hint"] = {"de": "Zeigen Sie auf einen Kanton oder wählen Sie ihn in der Liste.",
                    "fr": "Survolez un canton ou choisissez-le dans la liste.",
                    "it": "Passi il puntatore su un cantone o lo scelga nell’elenco.",
                    "en": "Point at a canton or pick it from the list."}
META["map_src"] = {"de": "Kartengrundlage: BFS, swisstopo (swiss-maps © Interactive Things)",
                   "fr": "Fond de carte : OFS, swisstopo (swiss-maps © Interactive Things)",
                   "it": "Base cartografica: UST, swisstopo (swiss-maps © Interactive Things)",
                   "en": "Base map: FSO, swisstopo (swiss-maps © Interactive Things)"}
META["map_ch"] = {"de": "Schweiz · 26 Kantone", "fr": "Suisse · 26 cantons", "it": "Svizzera · 26 cantoni",
                  "en": "Switzerland · 26 cantons"}
META["map_all"] = {"de": "Alle Kantone", "fr": "Tous les cantons", "it": "Tutti i cantoni", "en": "All cantons"}
META["map_list"] = {"de": "Offene Ausschreibungen der 26 Kantone", "fr": "Appels d’offres en cours des 26 cantons",
                    "it": "Bandi aperti dei 26 cantoni", "en": "Open tenders in the 26 cantons"}
META["key_figures"] = {"de": "Kennzahlen", "fr": "Chiffres clés", "it": "Cifre chiave", "en": "Key figures"}
META["sec_awards"] = {"de": "02 · Zuschläge", "fr": "02 · Adjudications", "it": "02 · Aggiudicazioni",
                      "en": "02 · Awards"}
META["sec_companies"] = {"de": "03 · Unternehmen", "fr": "03 · Entreprises", "it": "03 · Imprese",
                         "en": "03 · Companies"}
META["sec_divisions"] = {"de": "04 · Branchen", "fr": "04 · Branches", "it": "04 · Rami", "en": "04 · Industries"}
META["alarm_eyebrow"] = {"de": "E-Mail-Abo · kostenlos", "fr": "Alerte e-mail · gratuite",
                         "it": "Avviso e-mail · gratuito", "en": "Email alerts · free"}
META["alarm_h2"] = {"de": "Neue Ausschreibungen automatisch erhalten",
                    "fr": "Recevoir automatiquement les nouveaux appels d’offres",
                    "it": "Ricevere automaticamente i nuovi bandi", "en": "Get new tenders automatically"}
META["map_about"] = {
    "de": "Kartengrundlage der Startseite: swiss-maps © Interactive Things (BSD-3-Clause), Daten BFS/swisstopo.",
    "fr": "Fond de carte de la page d’accueil : swiss-maps © Interactive Things (BSD-3-Clause), données OFS/swisstopo.",
    "it": "Base cartografica della pagina iniziale: swiss-maps © Interactive Things (BSD-3-Clause), dati UST/swisstopo.",
    "en": "Base map of the home page: swiss-maps © Interactive Things (BSD-3-Clause), data FSO/swisstopo.",
}
JS["map_rank"] = {"de": "Rang {r} von 26", "fr": "Rang {r} sur 26", "it": "Posizione {r} su 26",
                  "en": "Rank {r} of 26"}
JS["map_share"] = {"de": "{p}\u00a0% aller offenen Ausschreibungen", "fr": "{p} % des appels d’offres en cours",
                   "it": "{p}% dei bandi aperti", "en": "{p}% of all open tenders"}
JS["map_lit"] = {"de": "{n} von 26 Kantonen", "fr": "{n} cantons sur 26", "it": "{n} cantoni su 26",
                 "en": "{n} of 26 cantons"}


# ---------------------------------------------------------------- fix round 1 (20.10.2026)
# After the third audit: the masthead's 'independent, not official', the short phone units of the stacked tables,
# the chart as a table, the lists' filter bar and leads, the cut tables, the buyer's-seat share, the outlier notes,
# the CSV links that say what they download, the authorities' finder, the alert form and its two return pages.
T["indep"] = {"de": "Unabhängig · nicht amtlich", "fr": "Indépendant · non officiel",
              "it": "Indipendente · non ufficiale", "en": "Independent · not official"}
T["chart_table"] = {"de": "Tabelle", "fr": "Tableau", "it": "Tabella", "en": "Table"}
T["unit_k_ph"] = {"de": "Tsd. CHF", "fr": "k CHF", "it": "k CHF", "en": "CHF k"}
T["unit_m_ph"] = {"de": "Mio. CHF", "fr": "mio CHF", "it": "mio. CHF", "en": "CHF m"}
T["unit_chf_ph"] = {"de": "CHF", "fr": "CHF", "it": "CHF", "en": "CHF"}
# a name that is an e-mail address in the publication (fix round 1): shown as this, never as an entity
T["noname"] = {"de": "Name nicht angegeben", "fr": "Nom non indiqué", "it": "Nome non indicato", "en": "Name not given"}
T["contact_errors"] = {"de": "Kontakt und Fehlermeldungen", "fr": "Contact et erreurs", "it": "Contatto ed errori",
                       "en": "Contact and errors"}
META["open_lead_short"] = {
    "de": "{n} offene Ausschreibungen von Bund, Kantonen und Gemeinden, die nächste Eingabefrist zuerst.",
    "fr": "{n} appels d’offres en cours de la Confédération, des cantons et des communes, le délai le plus proche "
          "en premier.",
    "it": "{n} bandi aperti di Confederazione, Cantoni e Comuni, la scadenza più vicina per prima.",
    "en": "{n} open tenders from the Confederation, cantons and communes, the nearest deadline first.",
}
META["list_lead_canton"] = {"de": "{n} im Kanton {name}, die nächste Eingabefrist zuerst.",
                            "fr": "{n} dans le canton {of}, le délai le plus proche en premier.",
                            "it": "{n} nel Canton {name}, la scadenza più vicina per prima.",
                            "en": "{n} in the canton of {name}, the nearest deadline first."}
META["list_lead_div"] = {"de": "{n} der Branche «{name}» aus der ganzen Schweiz, die nächste Eingabefrist zuerst.",
                         "fr": "{n} dans la branche « {name} », dans toute la Suisse, le délai le plus proche en premier.",
                         "it": "{n} del ramo «{name}» in tutta la Svizzera, la scadenza più vicina per prima.",
                         "en": "{n} in the “{name}” industry across Switzerland, the nearest deadline first."}
META["all_list_crumb"] = {"de": "Vollständige Liste", "fr": "Liste complète", "it": "Elenco completo",
                          "en": "Full list"}
META["desc_amount_approx"] = {"de": " für rund {amount}", "fr": " pour environ {amount}", "it": " per circa {amount}",
                              "en": " for about {amount}"}
META["company_val_approx"] = {"de": ", zusammen rund {v}", "fr": ", au total environ {v}",
                              "it": ", per un totale di circa {v}", "en": ", about {v} in total"}
META["door_buyers_h"] = {"de": "Auftraggeber finden", "fr": "Trouver un adjudicateur", "it": "Trova un committente",
                         "en": "Find a contracting authority"}
META["finder_ph_b"] = {"de": "z. B. Stadt Zürich", "fr": "p. ex. Ville de Genève", "it": "ad es. Città di Lugano",
                       "en": "e.g. City of Zurich"}
META["finder_sub_b"] = {
    "de": "{n} Auftraggeber mit mindestens einem Zuschlag, {k} davon mit eigener Seite.",
    "fr": "{n} adjudicateurs ayant attribué au moins un marché, dont {k} avec leur propre page.",
    "it": "{n} committenti con almeno un’aggiudicazione, di cui {k} con una pagina propria.",
    "en": "{n} contracting authorities with at least one award, {k} of them with a page of their own.",
}
META["az_other"] = {"de": "Andere", "fr": "Autres", "it": "Altri", "en": "Other"}
META["nf_eyebrow"] = {"de": "Fehler 404", "fr": "Erreur 404", "it": "Errore 404", "en": "Error 404"}
META["abo_resend"] = {
    "de": "Keine E-Mail nach 15 Minuten? Prüfen Sie den Spam-Ordner. Ist sie auch dort nicht, melden Sie sich mit "
          "derselben Adresse noch einmal an: Sie erhalten einen neuen Bestätigungslink.",
    "fr": "Pas d’e-mail après 15 minutes ? Vérifiez votre dossier de courrier indésirable. S’il n’y est pas non "
          "plus, inscrivez-vous à nouveau avec la même adresse : vous recevrez un nouveau lien de confirmation.",
    "it": "Nessuna e-mail dopo 15 minuti? Controlli la cartella dello spam. Se non c’è nemmeno lì, si iscriva di "
          "nuovo con lo stesso indirizzo: riceverà un nuovo link di conferma.",
    "en": "No email after 15 minutes? Check your spam folder. If it is not there either, sign up again with the "
          "same address: you will get a new confirmation link.",
}
META["abo_recap_h"] = {"de": "So geht es weiter", "fr": "La suite", "it": "I prossimi passi", "en": "What happens next"}
META["abo_step1"] = {"de": "Den Bestätigungslink in der E-Mail anklicken.",
                     "fr": "Cliquer sur le lien de confirmation de l’e-mail.",
                     "it": "Cliccare sul link di conferma nell’e-mail.",
                     "en": "Click the confirmation link in the email."}
META["abo_step2"] = {
    "de": "An jedem Werktag, an dem neue Ausschreibungen zu Ihrer Auswahl erscheinen, erhalten Sie eine E-Mail.",
    "fr": "Chaque jour ouvrable où de nouveaux appels d’offres correspondent à votre sélection, vous recevez un "
          "e-mail.",
    "it": "In ogni giorno feriale in cui escono nuovi bandi corrispondenti alla sua scelta riceverà un’e-mail.",
    "en": "On every working day when new tenders matching your selection appear, you get an email.",
}
META["abo_step3"] = {"de": "Abmelden können Sie sich jederzeit über den Link am Ende jeder E-Mail.",
                     "fr": "Vous pouvez vous désabonner à tout moment par le lien au bas de chaque e-mail.",
                     "it": "Può cancellarsi in qualsiasi momento con il link in fondo a ogni e-mail.",
                     "en": "You can unsubscribe at any time with the link at the bottom of every email."}
META["abo_form_nojs"] = {
    "de": "Die Auswahl nach Kanton und Branche braucht JavaScript. Ohne JavaScript gilt das Abo für die ganze "
          "Schweiz und alle Branchen.",
    "fr": "Le choix par canton et par branche nécessite JavaScript. Sans JavaScript, l’alerte couvre toute la "
          "Suisse et toutes les branches.",
    "it": "La scelta per cantone e ramo richiede JavaScript. Senza JavaScript l’avviso vale per tutta la Svizzera "
          "e per tutti i rami.",
    "en": "Choosing cantons and industries needs JavaScript. Without it, the alert covers all of Switzerland and "
          "every industry.",
}
META["abo_bfilter"] = {"de": "Branche suchen", "fr": "Chercher une branche", "it": "Cerca un ramo",
                       "en": "Find an industry"}
META["abo_bfilter_ph"] = {"de": "z. B. Reinigung", "fr": "p. ex. nettoyage", "it": "ad es. pulizia",
                          "en": "e.g. cleaning"}
IDX["cut_firms"] = {"de": "die {k} mit den meisten Zuschlägen, von {n}",
                    "fr": "les {k} ayant obtenu le plus d’adjudications, sur {n}",
                    "it": "le {k} con più aggiudicazioni, su {n}", "en": "the {k} with the most awards, of {n}"}
IDX["cut_buyers"] = {"de": "die {k} mit den meisten Zuschlägen, von {n}",
                     "fr": "les {k} ayant attribué le plus d’adjudications, sur {n}",
                     "it": "i {k} con più aggiudicazioni, su {n}", "en": "the {k} with the most awards, of {n}"}
IDX["cut_newest"] = {"de": "die {k} neuesten von {n}", "fr": "les {k} plus récentes sur {n}",
                     "it": "le {k} più recenti su {n}", "en": "the {k} most recent of {n}"}
IDX["csv_all_n"] = {"de": "Alle {n} Zuschläge als CSV-Datei", "fr": "Les {n} adjudications en fichier CSV",
                    "it": "Tutte le {n} aggiudicazioni in un file CSV", "en": "All {n} awards as a CSV file"}
IDX["csv_canton"] = {"de": "Zuschläge Kanton {name} (CSV)", "fr": "Adjudications du canton {of} (CSV)",
                     "it": "Aggiudicazioni del Canton {name} (CSV)", "en": "Awards in the canton of {name} (CSV)"}
IDX["csv_buyer"] = {"de": "Zuschläge von {name} (CSV)", "fr": "Adjudications de {name} (CSV)",
                    "it": "Aggiudicazioni di {name} (CSV)", "en": "Awards by {name} (CSV)"}
IDX["csv_company"] = {"de": "Zuschläge an {name} (CSV)", "fr": "Adjudications à {name} (CSV)",
                      "it": "Aggiudicazioni a {name} (CSV)", "en": "Awards to {name} (CSV)"}
IDX["csv_nocant"] = {"de": "Zuschläge ohne Kanton (CSV)", "fr": "Adjudications sans canton (CSV)",
                     "it": "Aggiudicazioni senza cantone (CSV)", "en": "Awards without a canton (CSV)"}
IDX["chart_csv"] = {"de": "Daten der Grafik (CSV)", "fr": "Données du graphique (CSV)", "it": "Dati del grafico (CSV)",
                    "en": "Chart data (CSV)"}
IDX["fb_share"] = {
    "de": "{k} der {n} ({p}) nennen keinen Ort; sie zählen hier, weil der Auftraggeber seinen Sitz im Kanton "
          "{name} hat.",
    "fr": "{k} des {n} ({p}) n’indiquent aucun lieu ; elles comptent ici parce que l’adjudicateur a son siège "
          "dans le canton {of}.",
    "it": "{k} delle {n} ({p}) non indicano alcun luogo; contano qui perché il committente ha sede nel Canton "
          "{name}.",
    "en": "{k} of the {n} ({p}) name no place; they count here because the contracting authority is based in the "
          "canton of {name}.",
}
IDX["fb_share_one"] = {
    "de": "Ein Zuschlag ({p}) nennt keinen Ort; er zählt hier, weil der Auftraggeber seinen Sitz im Kanton {name} "
          "hat.",
    "fr": "Une adjudication ({p}) n’indique aucun lieu ; elle compte ici parce que l’adjudicateur a son siège dans "
          "le canton {of}.",
    "it": "Un’aggiudicazione ({p}) non indica alcun luogo; conta qui perché il committente ha sede nel Canton "
          "{name}.",
    "en": "One award ({p}) names no place; it counts here because the contracting authority is based in the canton "
          "of {name}.",
}
IDX["div_once"] = {"de": "{k} der {f} Unternehmen haben in dieser Branche genau einen Zuschlag erhalten.",
                   "fr": "{k} des {f} entreprises ont obtenu exactement une adjudication dans cette branche.",
                   "it": "{k} delle {f} imprese hanno ottenuto esattamente un’aggiudicazione in questo ramo.",
                   "en": "{k} of the {f} companies won exactly one award in this industry."}
IDX["mc_outlier"] = {"de": "{m}: davon {k} {what} aus {p} Projekten.",
                     "fr": "{m} : dont {k} {what} provenant de {p} projets.",
                     "it": "{m}: di cui {k} {what} da {p} progetti.",
                     "en": "{m}: including {k} {what} from {p} projects."}
IDX["mc_outlier_one"] = {"de": "{m}: davon {k} {what} aus einem einzigen Projekt.",
                         "fr": "{m} : dont {k} {what} provenant d’un seul projet.",
                         "it": "{m}: di cui {k} {what} da un solo progetto.",
                         "en": "{m}: including {k} {what} from a single project."}
IDX["mc_outlier_by"] = {"de": "{m}: davon {k} {what} aus {p} Projekten von {b}.",
                        "fr": "{m} : dont {k} {what} provenant de {p} projets de {b}.",
                        "it": "{m}: di cui {k} {what} da {p} progetti di {b}.",
                        "en": "{m}: including {k} {what} from {p} projects by {b}."}
IDX["mc_outlier_one_by"] = {"de": "{m}: davon {k} {what} aus einem einzigen Projekt von {b}.",
                            "fr": "{m} : dont {k} {what} provenant d’un seul projet de {b}.",
                            "it": "{m}: di cui {k} {what} da un solo progetto di {b}.",
                            "en": "{m}: including {k} {what} from a single project by {b}."}
OUTLIER_WHAT = {"de": ("Lose", "Zuschläge"), "fr": ("lots", "adjudications"), "it": ("lotti", "aggiudicazioni"),
                "en": ("lots", "awards")}
# the lists' filter bar (liste.js), the zero-result suggestions (liste.js, suche.js), the panel's toggle (kb.js),
# the alert form's summary and Branche filter (abo.js)
JS["f_toggle"] = {"de": "Filter", "fr": "Filtres", "it": "Filtri", "en": "Filters"}
JS["f_active"] = {"de": "({n} aktiv)", "fr": "({n} actifs)", "it": "({n} attivi)", "en": "({n} active)"}
JS["f_active_1"] = {"de": "(1 aktiv)", "fr": "(1 actif)", "it": "(1 attivo)", "en": "(1 active)"}
JS["f_sort"] = {"de": "Reihenfolge", "fr": "Ordre", "it": "Ordine", "en": "Order"}
JS["f_sort_dl"] = {"de": "Nächste Eingabefrist zuerst", "fr": "Délai le plus proche d’abord",
                   "it": "Scadenza più vicina prima", "en": "Nearest deadline first"}
JS["f_sort_new"] = {"de": "Neueste zuerst", "fr": "Les plus récents d’abord", "it": "Più recenti prima",
                    "en": "Newest first"}
JS["f_new"] = {"de": "Nur neue vom {d}", "fr": "Seulement les nouveaux du {d}", "it": "Solo i nuovi del {d}",
               "en": "Only new on {d}"}
JS["f_abo_kw"] = {"de": "Das E-Mail-Abo filtert nach Kanton und Branche; Stichwörter werden nicht übernommen.",
                  "fr": "L’alerte e-mail filtre par canton et par branche ; les mots-clés ne sont pas repris.",
                  "it": "L’avviso e-mail filtra per cantone e ramo; le parole chiave non vengono riprese.",
                  "en": "Email alerts filter by canton and industry; keywords are not carried over."}
JS["f_first"] = {"de": "Die {k} mit der nächsten Eingabefrist, von {m} offenen Ausschreibungen",
                 "fr": "Les {k} dont le délai est le plus proche, sur {m} appels d’offres en cours",
                 "it": "I {k} con la scadenza più vicina, su {m} bandi aperti",
                 "en": "The {k} with the nearest deadlines, of {m} open tenders"}
JS["z_h"] = {"de": "Vorschläge:", "fr": "Suggestions :", "it": "Suggerimenti:", "en": "Suggestions:"}
JS["z_drop"] = {"de": "ohne «{t}»: {n}", "fr": "sans « {t} » : {n}", "it": "senza «{t}»: {n}",
                "en": "without “{t}”: {n}"}
JS["z_near"] = {"de": "{c}: {n}", "fr": "{c} : {n}", "it": "{c}: {n}", "en": "{c}: {n}"}
JS["z_abo"] = {"de": "E-Mail-Abo: neue Ausschreibungen dieser Auswahl automatisch erhalten",
               "fr": "Alerte e-mail : recevoir automatiquement les nouveaux appels d’offres de cette sélection",
               "it": "Avviso e-mail: ricevere automaticamente i nuovi bandi di questa selezione",
               "en": "Email alert: get new tenders for this selection automatically"}
JS["kb_fb"] = {"de": "{k} dieser Zuschläge ({p}) nennen keinen Ort und zählen hier als Sitz des Auftraggebers.",
               "fr": "{k} de ces adjudications ({p}) n’indiquent aucun lieu et comptent ici comme siège de "
                     "l’adjudicateur.",
               "it": "{k} di queste aggiudicazioni ({p}) non indicano alcun luogo e contano qui come sede del "
                     "committente.",
               "en": "{k} of these awards ({p}) name no place and count here as the authority’s seat."}
JS["kb_fbx"] = {"de": "Ohne diese Zuschläge", "fr": "Sans ces adjudications", "it": "Senza queste aggiudicazioni",
                "en": "Without these awards"}
JS["sum_sel"] = {"de": "Sie abonnieren: {s}", "fr": "Vous vous abonnez à : {s}", "it": "Si iscrive a: {s}",
                 "en": "You are subscribing to: {s}"}
JS["all_ch"] = {"de": "ganze Schweiz", "fr": "toute la Suisse", "it": "tutta la Svizzera", "en": "all of Switzerland"}
JS["all_b"] = {"de": "alle Branchen", "fr": "toutes les branches", "it": "tutti i rami", "en": "all industries"}
JS["bf_none"] = {"de": "Keine Branche passt zu «{q}».", "fr": "Aucune branche ne correspond à « {q} ».",
                 "it": "Nessun ramo corrisponde a «{q}».", "en": "No industry matches “{q}”."}


# ---------------------------------------------------------------- typography
# One rule set per language, applied once at import to the site's own templates and never
# to simap data. Strings above are written with plain spaces and straight apostrophes;
# this pass gives them the typography each language expects, so a new string cannot
# drift from it: typographic apostrophe everywhere, a spaced en dash tied to the word
# before it, the French narrow no-break space before : ; ? ! % and inside « », the German
# narrow space in "z. B.", and no space before an ellipsis in French, Italian and English.
# The simap notice (PROSE["disclaimer"]) is prescribed verbatim and stays untouched.
import re as _re


def _typo(s, lang):
    if not isinstance(s, str):
        return s
    s = s.replace("'", "\u2019")
    s = _re.sub(r" [\u2014\u2013] ", "\u00a0\u2013 ", s)
    if lang == "fr":
        s = _re.sub(r" ([:;?!%\u00bb])", "\u202f\\1", s)
        s = s.replace("\u00ab ", "\u00ab\u202f").replace("p. ex.", "p.\u202fex.")
    elif lang == "de":
        s = s.replace("z. B.", "z.\u202fB.").replace("u. a.", "u.\u202fa.")
    elif lang == "it":
        s = s.replace("p. es.", "p.\u202fes.").replace("ad es.", "ad\u00a0es.")
    if lang in ("fr", "it", "en"):
        s = s.replace(" \u2026", "\u2026")
    return s


for _tbl in (T, PROSE, META, IDX, JS):
    for _k, _d in _tbl.items():
        if _tbl is PROSE and _k == "disclaimer":
            continue
        for _l in list(_d):
            _d[_l] = _typo(_d[_l], _l)
for _kind in ENUM.values():
    for _d in _kind.values():
        for _l in list(_d):
            _d[_l] = _typo(_d[_l], _l)
for _doc in (IMP, PRIV):
    for _l, _v in _doc.items():
        for _f in ("title", "operator_h", "operator_note", "contact_h"):
            _v[_f] = _typo(_v[_f], _l)
        _v["paras"] = [(_typo(h, _l), _typo(t, _l)) for h, t in _v["paras"]]
for _l, _v in UEBER.items():
    for _f in ("title", "h1", "lead", "csv_pages", "csv_pages_nocomp", "ramp", "alert_link", "incomplete",
               "nocant", "nocant_zero"):
        _v[_f] = _typo(_v[_f], _l)
    _v["sections"] = [(_id, _typo(h, _l), [[_typo(x, _l) for x in blk] if isinstance(blk, list)
                                           else _typo(blk, _l) for blk in blocks])
                      for _id, h, blocks in _v["sections"]]
for _l, _d in SECTOR_WORD.items():
    for _c in list(_d):
        _d[_c] = tuple(_typo(x, _l) for x in _d[_c])
for _l, _d in list(CANTON_NAMES.items()) + [("fr", CANTON_OF["fr"]), *CPV_SHORT.items()]:
    for _c in list(_d):
        _d[_c] = _typo(_d[_c], _l)
for _tbl in (BANDS, COMPANY, OPEN_TENDERS, OPEN_CONTRACTS):
    for _l in list(_tbl):
        _tbl[_l] = tuple(_typo(x, _l) for x in _tbl[_l])


def _tie(s):
    """A number and its unit on one line: '1 mio CHF' broke as '1 | mio' at 320 px."""
    s = _re.sub(r"(?<=\d) (?=Mio\.|mio\b|CHF\b)", "\u00a0", s)
    s = _re.sub(r"(?<=[Mm]io) (?=CHF\b)|(?<=[Mm]io\.) (?=CHF\b)|(?<=CHF) (?=\d)", "\u00a0", s)
    return s


for _l in list(BANDS):
    BANDS[_l] = tuple(_tie(x) for x in BANDS[_l])

# Drift fails the build: a French template with a plain space before : ; ? !, or an
# unconverted spaced em dash anywhere.
for _tbl in (T, PROSE, META, IDX, JS):
    for _k, _d in _tbl.items():
        for _l, _v in _d.items():
            assert " \u2014 " not in _v, (_k, _l, _v)
            if _l == "fr":
                assert not _re.search(r" [:;?!]", _v), (_k, _v)
for _l, _v in UEBER.items():
    for _id, _h, _blocks in _v["sections"]:
        for _x in [_h] + [y for b in _blocks for y in (b if isinstance(b, list) else [b])]:
            assert " — " not in _x, (_id, _l, _x)
            if _l == "fr":
                assert not _re.search(r" [:;?!]", _x), (_id, _x)
