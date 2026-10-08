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
    "sectors": {"de": "Bereiche", "fr": "Domaines", "it": "Settori", "en": "Sectors"},
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
    "sum_published": {"de": "Summe der publizierten Beträge", "fr": "Total des montants publiés",
                      "it": "Totale degli importi pubblicati", "en": "Total of published amounts"},
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
    "deadline": {"de": "Eingabefrist", "fr": "Délai de remise", "it": "Scadenza",
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
    "by_awards": {"de": "nach Anzahl Zuschläge", "fr": "par nombre d’adjudications",
                  "it": "per numero di aggiudicazioni", "en": "by number of awards"},
    "main_sector": {"de": "Hauptbereich", "fr": "Domaine principal",
                    "it": "Settore principale", "en": "Main sector"},
    "activities": {"de": "Tätigkeitsbereiche", "fr": "Domaines d'activité",
                   "it": "Settori di attività", "en": "Sectors"},
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
    # no "Aggiornato al" before a date: it reads "al 08.10.2026" on the 8th (all'8)
    "updated": {"de": "Aktualisiert", "fr": "Mis à jour", "it": "Ultimo aggiornamento",
                "en": "Updated"},
    "period": {"de": "Zeitraum", "fr": "Période", "it": "Periodo", "en": "Period"},
    # one label for the same date on the home and the tenders pages
    "as_of": {"de": "Aktualisiert", "fr": "Mis à jour", "it": "Ultimo aggiornamento", "en": "Updated"},
    "entries": {"de": "Einträge", "fr": "Entrées", "it": "Voci", "en": "Entries"},
    "until": {"de": "bis", "fr": "jusqu'au", "it": "entro il", "en": "due"},
    "running": {"de": "Offene Ausschreibungen", "fr": "Appels d’offres en cours", "it": "Bandi aperti", "en": "Open now"},
    "language": {"de": "Sprache", "fr": "Langue", "it": "Lingua", "en": "Language"},
    "company": {"de": "Unternehmen", "fr": "Entreprise", "it": "Impresa", "en": "Company"},
    "tender": {"de": "Ausschreibung", "fr": "Appel d’offres", "it": "Bando", "en": "Tender"},
    "winner": {"de": "Zuschlag an", "fr": "Adjudicataire", "it": "Aggiudicatario", "en": "Winner"},
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
        "fr": "La moitié des adjudications dotées d’un montant attribuable porte sur un montant "
              "supérieur, l’autre moitié sur un montant inférieur.",
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
              "Unternehmen – mit Auftraggeber, Betrag und Verfahren. Dazu alle Ausschreibungen, "
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
              "Only the publications there are authoritative.",
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
              "Only the publications there are authoritative.",
    },
    "official_link": {
        "de": "Amtliche Publikation: {link} — massgebend ist ausschliesslich die dortige "
              "Veröffentlichung.",
        "fr": "Publication officielle : {link} – seule cette publication fait foi.",
        "it": "Pubblicazione ufficiale: {link}. Fa fede esclusivamente quella pubblicazione.",
        "en": "Official publication: {link}. Only the version published there is authoritative.",
    },
    "view_on_simap": {
        "de": "Projekt {n} auf simap.ch ansehen", "fr": "projet {n} sur simap.ch",
        "it": "progetto n. {n} su simap.ch", "en": "project {n} on simap.ch",
    },
    # genera.matches() needs four significant CPV digits in common: the same code or a
    # closely related one, never "the same sector" (the list shows other exact codes)
    "matched_tenders": {
        "de": "Offene Ausschreibungen in verwandten Bereichen",
        "fr": "Appels d’offres en cours dans des domaines apparentés",
        "it": "Bandi aperti in settori affini",
        "en": "Open tenders in related sectors",
    },
    "matched_note": {
        "de": "Offene Ausschreibungen mit demselben oder einem eng verwandten CPV-Code (der "
              "EU-weit einheitlichen Einteilung der Leistungen) wie die bisherigen Zuschläge "
              "dieses Unternehmens.",
        "fr": "Appels d’offres en cours dont le code CPV (le vocabulaire commun pour les marchés "
              "publics de l’UE) est identique ou étroitement apparenté à celui d’adjudications déjà "
              "obtenues par cette entreprise.",
        "it": "Bandi aperti con un codice CPV (la classificazione europea degli appalti) uguale o "
              "affine a quello delle aggiudicazioni già ottenute da questa impresa.",
        "en": "Tenders still open whose CPV code (the EU’s standard classification of works, "
              "supplies and services) is the same as, or closely related to, that of this "
              "company’s past awards.",
    },
    # grouped on the first four significant CPV digits of the main code: related sectors,
    # not one exact code (the same wording as the matched tenders above it)
    "peers": {
        "de": "Weitere Unternehmen in verwandten Bereichen", "fr": "Autres entreprises dans des domaines apparentés",
        "it": "Altre imprese in settori affini", "en": "Other companies in related sectors",
    },
    "analysis": {
        "de": "Zuschläge pro Jahr", "fr": "Adjudications par année", "it": "Aggiudicazioni per anno", "en": "Awards per year",
    },
    "derived": {
        "de": "eigene Auswertung der Publikationen", "fr": "analyse établie à partir des "
                                                        "publications",
        "it": "elaborazione propria dei dati pubblicati", "en": "own analysis of the publications",
    },
    "open_tenders_h1": {
        "de": "Aktuelle Ausschreibungen in der Schweiz finden",
        "fr": "Trouver les appels d'offres en cours en Suisse",
        "it": "Bandi di gara aperti in Svizzera",
        "en": "Find open public tenders in Switzerland",
    },
    "translation_note": {
        "de": "Titel und Beschreibungen erscheinen in der Sprache, in der sie publiziert "
              "wurden. Nicht jede Publikation liegt in allen Landessprachen vor.",
        "fr": "Les titres et descriptions apparaissent dans la langue de publication. "
              "Toutes les publications ne sont pas disponibles dans toutes les langues.",
        "it": "Titoli e descrizioni compaiono nella lingua in cui sono stati pubblicati. Non "
              "tutte le pubblicazioni sono disponibili in tutte le lingue.",
        "en": "Titles and descriptions appear in the language they were published in. Not every "
              "publication is available in every language.",
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
    "canton_title": {"de": "Öffentliche Aufträge Kanton {name}",
                     "fr": "Marchés publics du canton {of}",
                     "it": "Appalti pubblici nel Canton {name}",
                     "en": "Public contracts, canton of {name}"},
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
        "it": "{n} a favore di {f} nel settore «{label}», pubblicate su simap.ch.",
        "en": "{n} to {f} in the “{label}” sector, published on simap.ch.",
    },
    "sector_lead": {"de": "{n} an {f} in diesem Bereich.",
                    "fr": "{n} en faveur de {f} dans ce domaine.",
                    "it": "{n} a favore di {f} in questo settore.",
                    "en": "{n} to {f} in this sector."},
    "home_title": {"de": "Öffentliche Aufträge Schweiz — Zuschläge nach Unternehmen",
                   "fr": "Marchés publics suisses — adjudications par entreprise",
                   "it": "Appalti pubblici svizzeri — aggiudicazioni per impresa",
                   "en": "Swiss public contracts — awards by company"},
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
    "open_title": {"de": "Ausschreibungen Schweiz: {n} offene Aufträge – täglich neu",
                   "fr": "Appels d’offres en Suisse : {n} marchés publics en cours",
                   "it": "Bandi di gara in Svizzera: {n} appalti pubblici aperti",
                   "en": "Public tenders in Switzerland: {n} open now"},
    "open_desc": {
        "de": "Alle offenen Ausschreibungen von Bund, Kantonen und Gemeinden (simap.ch) an einem Ort: "
              "nach Frist, Kanton und Branche. Ohne Login, mit Gratis-E-Mail-Alarm.",
        "fr": "Tous les appels d’offres publics en cours de la Confédération, des cantons et des communes "
              "(simap.ch), par délai, canton et branche. Sans compte, alerte e-mail gratuite.",
        "it": "Tutti i bandi aperti di Confederazione, Cantoni e Comuni (simap.ch) in un unico posto: per "
              "scadenza, cantone e ramo. Senza account, con avviso e-mail gratuito.",
        "en": "All open public tenders from the Confederation, cantons and municipalities (simap.ch) in one "
              "place, by deadline, canton and industry. No account, free e-mail alerts.",
    },
    "open_lead": {
        "de": "{n} öffentliche Ausschreibungen mit noch offener Eingabefrist, publiziert von "
              "Bund, Kantonen und Gemeinden auf simap.ch – nach Frist geordnet, nach Kanton und "
              "Branche gegliedert, jeden Morgen aktualisiert.",
        "fr": "{n} appels d’offres publics dont le délai de remise court encore, publiés sur "
              "simap.ch par la Confédération, les cantons et les communes – par ordre d’échéance, "
              "consultables par canton et par branche, mis à jour chaque matin.",
        "it": "{n} bandi di gara ancora aperti, pubblicati da Confederazione, Cantoni e Comuni "
              "su simap.ch: ordinati per scadenza, suddivisi per cantone e ramo, aggiornati ogni "
              "mattina.",
        "en": "{n} public tenders with a deadline still open, published by the Confederation, "
              "cantons and communes on simap.ch – sorted by deadline, grouped by canton and "
              "industry, updated every morning.",
    },
    "open_howto_h2": {
        "de": "Ausschreibungen suchen: So funktioniert es",
        "fr": "Chercher un appel d'offres : mode d'emploi",
        "it": "Cercare un bando: come funziona",
        "en": "How to find tenders",
    },
    "open_howto": {
        "de": "Die Tabelle zeigt die Ausschreibungen mit der nächsten Eingabefrist zuerst. Jede "
              "Zeile führt zur Ausschreibung mit Auftraggeber, Frist, Bereich (CPV-Code nach der "
              "EU-weit einheitlichen Einteilung der Leistungen) und dem Link zur amtlichen "
              "Publikation. Über die Kantonsseiten finden Sie Ausschreibungen in Ihrer Region, "
              "über die Branchenseiten Ausschreibungen für Ihr Gewerbe: Bauarbeiten, Planung, "
              "IT, Versicherungen, Fahrzeuge und mehr. Die Daten stammen von der amtlichen "
              "Plattform simap.ch und werden jeden Morgen aktualisiert, sobald simap.ch die "
              "Publikationen des Tages freigibt.",
        "fr": "Le tableau présente d’abord les appels d’offres dont le délai est le plus proche. "
              "Chaque ligne ouvre la fiche de l’appel d’offres : adjudicateur, délai, domaine "
              "(code CPV) et lien vers la publication officielle. Les pages cantonales regroupent les "
              "appels d’offres de votre région, les pages par branche ceux de votre métier : "
              "construction, études, informatique, assurances, véhicules, etc. Les données "
              "proviennent de la plateforme officielle simap.ch et sont mises à jour chaque "
              "matin, dès que simap.ch met en ligne les publications du jour.",
        "it": "La tabella mostra per primi i bandi con la scadenza più vicina. Ogni riga rimanda "
              "alla scheda del bando, con committente, scadenza, settore (codice CPV) e link alla "
              "pubblicazione ufficiale. Nelle pagine cantonali trova i bandi della sua "
              "regione, in quelle per ramo i bandi del suo settore: edilizia, progettazione, "
              "informatica, assicurazioni, veicoli e altro. I dati provengono dalla piattaforma "
              "ufficiale simap.ch e sono aggiornati ogni mattina, non appena simap.ch rende "
              "disponibili le pubblicazioni del giorno.",
        "en": "The table lists the tenders with the nearest deadline first. Each row leads to "
              "the tender, with the contracting authority, the deadline, the sector (CPV code) and "
              "a link to the official publication. Canton pages list the tenders in your region; "
              "industry pages list those in your line of work: construction, engineering, IT, "
              "insurance, vehicles and more. The data comes from simap.ch, the official "
              "platform, and is refreshed every morning once simap.ch releases the day’s "
              "publications.",
    },
    "open_by_canton_h2": {
        "de": "Offene Ausschreibungen pro Kanton", "fr": "Appels d’offres en cours par canton",
        "it": "Bandi aperti per cantone", "en": "Open tenders by canton",
    },
    "open_canton_lede": {
        "de": "Stand {date}. Klicken Sie auf einen Kanton, um dessen offene Ausschreibungen nach "
              "Eingabefrist geordnet zu sehen.",
        "fr": "État au {date}. Cliquez sur un canton pour voir tous ses appels d’offres en "
              "cours, par ordre d’échéance.",
        "it": "Ultimo aggiornamento: {date}. Clicchi su un cantone per vedere i bandi aperti di quel "
              "cantone, ordinati per scadenza.",
        "en": "As of {date}. Click a canton to see all its open tenders, sorted by deadline.",
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
    "feed_title": {"de": "Neue Ausschreibungen: {scope} – auftragsregister.ch",
                   "fr": "Nouveaux appels d’offres : {scope} – auftragsregister.ch",
                   "it": "Nuovi bandi: {scope} – auftragsregister.ch",
                   "en": "New tenders: {scope} – auftragsregister.ch"},
    "feed_all": {"de": "Schweiz", "fr": "Suisse", "it": "Svizzera", "en": "Switzerland"},
    "feed_link": {"de": "RSS-Feed", "fr": "Flux RSS", "it": "Feed RSS", "en": "RSS feed"},
    "abo_cta": {"de": "Neue Ausschreibungen automatisch erhalten (kostenlos)",
                "fr": "Recevoir automatiquement les nouveaux appels d’offres (gratuit)",
                "it": "Ricevere i nuovi bandi automaticamente (gratis)",
                "en": "Get new tenders automatically (free)"},
    # No "every day" / "täglich" about the e-mail: the sender writes only on days with new matching
    # tenders (08.10.2026)
    "abo_title": {"de": "Ausschreibungen abonnieren (E-Mail, RSS)",
                  "fr": "Nouveaux appels d’offres par e-mail ou RSS",
                  "it": "Nuovi bandi via e-mail o RSS",
                  "en": "Subscribe to tender alerts by email or RSS"},
    "abo_desc": {"de": "Kostenlose Benachrichtigung über neue öffentliche Ausschreibungen in der "
                       "Schweiz, nach Kanton und Branche: per E-Mail oder als RSS-Feed. "
                       "Quelle: simap.ch.",
                 "fr": "Alerte gratuite sur les nouveaux appels d’offres publics en Suisse, par "
                       "canton et par branche : par e-mail ou par flux RSS. Source : "
                       "simap.ch.",
                 "it": "Avviso gratuito sui nuovi bandi pubblici in Svizzera, per cantone e "
                       "ramo: via e-mail o feed RSS. Fonte: simap.ch.",
                 "en": "Free alerts for new public tenders in Switzerland, by canton and "
                       "industry: by email or as an RSS feed. Source: simap.ch."},
    "abo_h1": {"de": "Neue Ausschreibungen automatisch erhalten",
               "fr": "Recevoir automatiquement les nouveaux appels d’offres",
               "it": "Ricevere i nuovi bandi automaticamente",
               "en": "Get new tenders automatically"},
    "abo_lead": {"de": "Jeden Morgen erscheinen auf simap.ch neue Ausschreibungen. Wählen Sie Kanton und "
                       "Branche und lassen Sie sich die neuen Ausschreibungen zuschicken — kostenlos, ohne Konto.",
                 "fr": "Chaque matin, de nouveaux appels d'offres paraissent sur simap.ch. Choisissez le canton "
                       "et la branche et recevez les nouveautés — gratuitement, sans compte.",
                 "it": "Ogni mattina su simap.ch vengono pubblicati nuovi bandi. Scelga cantone "
                       "e ramo e riceverà le novità – gratis, senza account.",
                 "en": "New tenders appear on simap.ch every morning. Choose your cantons and "
                       "industries, and we will send you the new ones – free, no account needed."},
    "abo_email_text": {"de": "Schreiben Sie eine E-Mail an {mail} mit dem Betreff «Abo» und "
                             "nennen Sie im Text Kanton (z. B. ZH) und Branche (z. B. "
                             "Bauarbeiten oder CPV 45). Sie erhalten eine Bestätigung und danach "
                             "eine E-Mail, wenn neue Ausschreibungen erscheinen, die zu Ihrer "
                             "Auswahl passen. Abmelden: E-Mail mit Betreff «Stop». Ihre Adresse "
                             "wird nur dafür verwendet und nicht weitergegeben.",
                       "fr": "Envoyez un e-mail à {mail} avec l’objet « Abo » en indiquant le "
                             "canton (p. ex. GE) et la branche (p. ex. construction ou CPV 45). "
                             "Vous recevrez une confirmation, puis un e-mail les jours où "
                             "paraissent de nouveaux appels d’offres correspondants. Pour vous "
                             "désabonner, envoyez un e-mail avec l’objet « Stop ». Votre adresse "
                             "ne sert qu’à cet envoi et n’est transmise à personne.",
                       "it": "Scriva un’e-mail ad {mail} con oggetto «Abo», indicando il cantone "
                             "(p. es. TI) e il ramo (p. es. edilizia o CPV 45). Riceverà una "
                             "conferma e poi un’e-mail nei giorni in cui escono nuovi bandi "
                             "corrispondenti. Per cancellarsi basta un’e-mail con oggetto «Stop». "
                             "Il suo indirizzo serve solo a questo e non viene ceduto a terzi.",
                       "en": "Send an email to {mail} with the subject “Abo”, stating the canton "
                             "(e.g. ZH) and the industry (e.g. construction or CPV 45). You will "
                             "receive a confirmation and then an email on days when new matching "
                             "tenders appear. To stop, send an email with the subject "
                             "“Stop”. Your address is used only for this and is never shared."},
    "abo_rss_h2": {"de": "Per RSS-Feed (sofort, ohne Anmeldung)", "fr": "Par flux RSS (immédiat, sans inscription)",
                   "it": "Via feed RSS (subito, senza iscrizione)", "en": "By RSS feed (instant, no sign-up)"},
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
    "abo_check_title": {"de": "Fast geschafft: bitte E-Mail bestätigen", "fr": "Plus qu’une "
                                                                               "étape : "
                                                                               "confirmez votre "
                                                                               "adresse e-mail",
                        "it": "Quasi fatto: confermi il suo indirizzo e-mail", "en": "Almost done: please "
                                                                      "confirm your email address"},
    "abo_check": {"de": "Wir haben Ihnen eine E-Mail geschickt. Klicken Sie auf den Bestätigungslink, dann ist das Abo aktiv. "
                        "Keine E-Mail erhalten? Bitte prüfen Sie Ihren Spam-Ordner.",
                  "fr": "Nous vous avons envoyé un e-mail. Cliquez sur le lien de confirmation "
                        "pour activer l’abonnement. Rien reçu ? Vérifiez votre dossier de "
                        "courrier indésirable.",
                  "it": "Le abbiamo inviato un'e-mail. Clicchi sul link di conferma per attivare l'abbonamento. "
                        "Nessuna e-mail? Controlli la cartella spam.",
                  "en": "We have sent you an email. Click the confirmation link in it to "
                        "activate your subscription. No email? Check your spam folder."},
    "abo_ok_title": {"de": "Abo bestätigt", "fr": "Abonnement confirmé", "it": "Abbonamento confermato",
                     "en": "Subscription confirmed"},
    "abo_ok": {"de": "Ab jetzt erhalten Sie eine E-Mail, wenn neue Ausschreibungen erscheinen, die zu "
                     "Ihrer Auswahl passen. Abmelden: Link am Ende jeder E-Mail.",
               "fr": "Dès à présent, vous recevrez un e-mail les jours où paraissent de nouveaux "
                     "appels d’offres correspondant à votre sélection. Pour vous désabonner : lien "
                     "au bas de chaque e-mail.",
               "it": "D’ora in poi riceverà un’e-mail nei giorni in cui escono nuovi bandi "
                     "corrispondenti alla sua scelta. Per cancellarsi: link in fondo a ogni e-mail.",
               "en": "From now on, you will receive an email on days when new tenders matching "
                     "your selection appear. To unsubscribe, use the link at the bottom of any "
                     "email."},
    "abo_back": {"de": "Zur Abo-Seite", "fr": "Retour à la page d’abonnement", "it": "Torna alla pagina di abbonamento",
                 "en": "Back to the subscription page"},
    "abo_form_h2": {"de": "Anmelden (kostenlos)", "fr": "S'inscrire (gratuit)", "it": "Iscriversi (gratis)", "en": "Sign up (free)"},
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
    "abo_form_submit": {"de": "Abonnieren", "fr": "S'abonner", "it": "Iscriversi", "en": "Subscribe"},
    # an e-mail only on a day with new matching tenders: "an jedem Werktag eine E-Mail" promised one
    # every working day, and none goes out without a match (08.10.2026)
    "abo_form_consent": {"de": "Sie erhalten zuerst eine E-Mail mit einem Bestätigungslink; erst "
                               "danach ist das Abo aktiv. Von da an erhalten Sie eine E-Mail, wenn "
                               "neue Ausschreibungen erscheinen, die zu Ihrer Auswahl passen – an "
                               "Tagen ohne solche Ausschreibungen keine. Abmelden können Sie sich "
                               "jederzeit über den Link in jeder E-Mail. Anmeldung und Versand "
                               "über Brevo (EU).",
                         "fr": "Vous recevrez d’abord un e-mail contenant un lien de "
                               "confirmation : l’abonnement ne sera actif qu’après votre clic. "
                               "Ensuite, un e-mail vous présentera les nouveaux appels d’offres "
                               "correspondant à votre sélection, les jours où il en paraît ; les "
                               "autres jours, vous n’en recevrez pas. Vous "
                               "pouvez vous désabonner à tout moment grâce au lien présent dans "
                               "chaque e-mail. L’inscription et l’envoi passent par Brevo (UE).",
                         "it": "Riceverà prima un’e-mail con un link di conferma: l’abbonamento "
                               "si attiva solo dopo il clic su quel link. In seguito riceverà "
                               "un’e-mail nei giorni in cui escono nuovi bandi corrispondenti alla "
                               "sua scelta; negli altri giorni nessuna. Può cancellarsi in "
                               "qualsiasi momento con il link presente in ogni e-mail. Iscrizione "
                               "e invio tramite Brevo (UE).",
                         "en": "You will first receive an email with a confirmation link; the "
                               "subscription starts only once you click it. After that, you will "
                               "receive an email on days when new tenders matching your selection "
                               "appear, and none on other days. "
                               "You can unsubscribe at any time via the link in every email. "
                               "Sign-up and sending are handled by Brevo (EU)."},
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
                     "en": "That didn’t work. Please check the email address or write to {mail}."},
    "abo_email_alt_h2": {"de": "Ohne Formular: per E-Mail", "fr": "Sans formulaire : par e-mail",
                         "it": "Senza modulo: via e-mail", "en": "Or sign up by email"},
    "open_kpi_open": {"de": "offene Ausschreibungen", "fr": "appels d’offres en cours",
                      "it": "bandi aperti", "en": "open tenders"},
    "open_kpi_cantons": {"de": "Kantone mit offenen Ausschreibungen", "fr": "cantons avec appels d’offres en cours",
                         "it": "cantoni con bandi aperti", "en": "cantons with open tenders"},
    "open_kpi_sectors": {"de": "Branchen (CPV)", "fr": "branches (CPV)", "it": "rami (CPV)",
                         "en": "industries (CPV)"},
    "open_kpi_next": {"de": "nächste Eingabefrist", "fr": "prochain délai",
                      "it": "prossima scadenza", "en": "next deadline"},
    "cmp_h2": {"de": "simap.ch und dieses Register",
               "fr": "simap.ch et ce registre",
               "it": "simap.ch e questo registro",
               "en": "simap.ch and this register"},
    "cmp_lead": {"de": "simap.ch ist die amtliche Plattform und bleibt die massgebende Quelle. "
                       "Dieses Register liest sie täglich aus und beantwortet zusätzlich Fragen, "
                       "die sich dort nicht stellen lassen.",
                 "fr": "simap.ch est la plateforme officielle et reste la source déterminante. "
                       "Ce registre la consulte chaque jour et répond en outre à des questions "
                       "que l’on ne peut pas y poser.",
                 "it": "simap.ch è la piattaforma ufficiale e resta la fonte che fa fede. Questo "
                       "registro ne riprende i dati ogni giorno e risponde anche a domande che "
                       "su simap.ch non si possono porre.",
                 "en": "simap.ch is the official platform and remains the authoritative source. "
                       "This register reads it daily and additionally answers questions that "
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
    "cmp_r2": {"de": "Alle offenen Ausschreibungen",
               "fr": "Tous les appels d’offres en cours",
               "it": "Tutti i bandi aperti", "en": "All open tenders"},
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
    "cmp_r7": {"de": "E-Mail-Benachrichtigung nach eigenem Filter",
               "fr": "Alerte e-mail selon vos propres critères",
               "it": "Avviso e-mail secondo il proprio filtro",
               "en": "Email alerts matching your own filters"},
    "cmp_r8": {"de": "Nutzung ohne Konto", "fr": "Utilisation sans compte",
               "it": "Uso senza account", "en": "Use without an account"},
    "open_sector_desc": {
        "de": "{n} in der Branche «{name}» (CPV {code}) aus der ganzen Schweiz, nach "
              "Eingabefrist geordnet.",
        "fr": "{n} en Suisse dans la branche « {name} » (CPV {code}), par ordre d’échéance, avec "
              "mise à jour quotidienne.",
        "it": "{n} nel ramo «{name}» (CPV {code}) in tutta la Svizzera, in ordine di scadenza, "
              "con aggiornamento quotidiano.",
        "en": "{n} across Switzerland in the “{name}” industry (CPV {code}), sorted by deadline "
              "and updated daily.",
    },
    "open_canton_title": {"de": "Aktuelle Ausschreibungen Kanton {name}",
                          "fr": "Appels d’offres dans le canton {of}",
                          "it": "Bandi aperti nel Canton {name}",
                          "en": "Open tenders in the canton of {name}"},
    "open_canton_t1": {"de": "Ausschreibungen Kanton {name}: {c} – täglich neu",
                       "fr": "Appels d’offres dans le canton {of} : {c}",
                       "it": "Bandi di gara nel Canton {name}: {c}",
                       "en": "Public tenders in the canton of {name}: {c}"},
    "open_canton_t2": {"de": "Ausschreibungen Kanton {name}: {c}",
                       "fr": "Appels d’offres canton {of} : {c}",
                       "it": "Bandi Canton {name}: {c}",
                       "en": "Tenders in the canton of {name}: {c}"},
    "open_canton_t3": {"de": "Ausschreibungen {name}: {c}", "fr": "Appels d’offres {name} : {c}",
                       "it": "Bandi {name}: {c}", "en": "Tenders in {name}: {c}"},
    "open_sector_t1": {"de": "{word} Schweiz: {k} offene Submissionen – täglich neu",
                       "fr": "{word} en Suisse : {k} en cours",
                       "it": "{word} in Svizzera: {k} aperti – aggiornati ogni giorno",
                       "en": "{word} in Switzerland: {k} open – updated daily"},
    "open_sector_t2": {"de": "{word} Schweiz: {k} offene Submissionen", "fr": "{word} en Suisse : {k} en cours",
                       "it": "{word} in Svizzera: {k} aperti", "en": "{word} in Switzerland: {k} open"},
    "open_sector_desc_word": {
        "de": "Alle {k} offenen {w} der Schweiz aus simap.ch, nach Eingabefrist und Kanton geordnet. "
              "Gratis, ohne Login, mit E-Mail-Alarm.",
        "fr": "Les {k} {w} en cours en Suisse (simap.ch), classés par délai et par canton. Gratuit, "
              "sans compte, avec alerte e-mail.",
        "it": "I {k} {w} aperti in Svizzera (simap.ch), in ordine di scadenza e per cantone. Gratis, "
              "senza account, con avviso e-mail.",
        "en": "All {k} open {w} in Switzerland from simap.ch, sorted by deadline and canton. Free, no "
              "account, with e-mail alerts.",
    },
    "open_canton_h1": {
        "de": "Aktuelle Ausschreibungen im Kanton {name}",
        "fr": "Appels d’offres en cours dans le canton {of}",
        "it": "Bandi aperti nel Canton {name}",
        "en": "Open public tenders in the canton of {name}",
    },
    "open_canton_desc": {
        "de": "{n} im Kanton {name}: nach Frist geordnet, täglich aktualisiert, mit Gratis-E-Mail-Alarm und "
              "ohne Login.",
        "fr": "{n} dans le canton {of} : classés par délai, mis à jour chaque jour, alerte e-mail gratuite, "
              "sans compte.",
        "it": "{n} nel Canton {name}: in ordine di scadenza, aggiornati ogni giorno, con avviso e-mail "
              "gratuito e senza account.",
        "en": "{n} in the canton of {name}: sorted by deadline, updated daily, with a free e-mail alert and "
              "no account needed.",
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
        "de": "Auftraggeber von Bund, Kantonen und Gemeinden, alphabetisch geordnet.",
        "fr": "Adjudicateurs (services acheteurs) de la Confédération, des cantons et des "
              "communes, par ordre alphabétique.",
        "it": "Committenti pubblici della Confederazione, dei Cantoni e dei Comuni, in ordine "
              "alfabetico.",
        "en": "Federal, cantonal and communal contracting authorities, listed alphabetically."},
    "buyers_title": {"de": "Auftraggeber im öffentlichen Beschaffungswesen — Verzeichnis",
                     "fr": "Adjudicateurs des marchés publics — répertoire",
                     "it": "Committenti degli appalti pubblici — elenco",
                     "en": "Contracting authorities in public procurement — directory"},
    "buyers_desc": {
        "de": "Verzeichnis von {n} Auftraggebern und den Aufträgen, die sie auf simap.ch "
              "publiziert haben.",
        "fr": "Répertoire de {n} adjudicateurs et des adjudications qu’ils ont publiées sur "
              "simap.ch.",
        "it": "Elenco dei {n} committenti pubblici, con le aggiudicazioni che hanno pubblicato "
              "su simap.ch.",
        "en": "Directory of {n} contracting authorities and the awards they published on "
              "simap.ch."},
    "cantons_lead": {"de": "Publizierte Zuschläge nach Kanton der Auftragsausführung.",
                     "fr": "Adjudications publiées par canton d'exécution.",
                     "it": "Aggiudicazioni pubblicate per cantone di esecuzione.",
                     "en": "Published awards, by the canton where the contract is carried out."},
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
                   "it": "Appalti pubblici per settore", "en": "Public contracts by sector"},
    "sectors_lead": {"de": "Publizierte Zuschläge nach Bereich. Die Bereiche folgen dem CPV, der "
                           "EU-weit einheitlichen Einteilung der Leistungen.",
                     "fr": "Adjudications publiées par domaine. Les domaines suivent le CPV, le "
                           "vocabulaire commun pour les marchés publics de l’UE.",
                     "it": "Aggiudicazioni pubblicate per settore. I settori seguono il CPV, la "
                           "classificazione europea comune degli appalti.",
                     "en": "Published awards by sector. Sectors follow the CPV, the EU’s "
                           "standard codes for types of works, supplies and services."},
    "sectors_title": {"de": "Öffentliche Aufträge nach Bereich — CPV-Übersicht",
                      "fr": "Marchés publics par domaine — aperçu CPV",
                      "it": "Appalti pubblici per settore — panoramica CPV",
                      "en": "Public contracts by sector — CPV overview"},
    "sectors_desc": {
        "de": "Publizierte Zuschläge nach Bereich (CPV), mit den Unternehmen, die sie erhalten "
              "haben.",
        "fr": "Adjudications publiées par domaine (CPV), avec les entreprises qui les ont obtenues.",
        "it": "Aggiudicazioni pubblicate per settore (CPV), con le imprese che le hanno ottenute.",
        "en": "Published awards by sector (CPV), with the companies that won them."},
    "all_companies": {"de": "Alle Unternehmen", "fr": "Toutes les entreprises",
                      "it": "Tutte le imprese", "en": "All companies"},
    "all_buyers": {"de": "Alle Auftraggeber", "fr": "Tous les adjudicateurs",
                   "it": "Tutti i committenti", "en": "All contracting authorities"},
    "all_cantons": {"de": "Alle Kantone", "fr": "Tous les cantons",
                    "it": "Tutti i cantoni", "en": "All cantons"},
    "all_sectors": {"de": "Alle Bereiche", "fr": "Tous les domaines",
                    "it": "Tutti i settori", "en": "All sectors"},
    "next_deadlines": {"de": "Nächste Eingabefristen", "fr": "Prochains délais",
                       "it": "Prossime scadenze", "en": "Next deadlines"},
    "open_count": {"de": "{n} offen", "fr": "{n} en cours", "it": "{n} bandi aperti",
                   "en": "{n} open"},
    "by_canton": {"de": "Nach Kanton", "fr": "Par canton", "it": "Per cantone",
                  "en": "By canton"},
    "by_sector": {"de": "Nach Bereich", "fr": "Par domaine", "it": "Per settore",
                  "en": "By sector"},
    "awarded_in": {"de": "Vergebene Aufträge im Kanton {c}", "fr": "Marchés adjugés dans le canton {of}",
                   "it": "Appalti aggiudicati nel Canton {c}", "en": "Contracts awarded in the canton of {c}"},
    "all_open": {"de": "Alle offenen Ausschreibungen", "fr": "Tous les appels d’offres en cours",
                 "it": "Tutti i bandi aperti", "en": "All open tenders"},
    "same_sector": {"de": "Aufträge im selben Bereich", "fr": "Marchés du même domaine",
                    "it": "Appalti dello stesso settore", "en": "Awards in the same sector"},
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
        "it": "Aggiudicazioni al mese in questo settore",
        "en": "Awards per month in this sector",
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
        "de": "Schraffierte letzte Säule: laufender Monat, erfasst bis {date}.",
        "fr": "Dernière colonne hachurée : mois en cours, données au {date}.",
        "it": "Ultima colonna tratteggiata: mese in corso (ultimo aggiornamento: {date}).",
        "en": "Striped last column: current month, data up to {date}.",
    },
    # the running month with no award yet: no column is drawn, so no "last column" to point at
    "mc_note_end_zero": {
        "de": "Laufender Monat ({m}): bisher kein Zuschlag, erfasst bis {date}.",
        "fr": "Mois en cours ({m}) : aucune adjudication pour l’instant, données au {date}.",
        "it": "Mese in corso ({m}): finora nessuna aggiudicazione (ultimo aggiornamento: {date}).",
        "en": "Current month ({m}): no awards so far, data up to {date}.",
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
        "it": "Numero di aggiudicazioni per ramo. I rami sono le divisioni del CPV, la "
              "classificazione europea degli appalti; ognuno comprende molti settori specifici.",
        "en": "Number of awards per industry. Industries are the top-level groups of the CPV, "
              "the EU’s standard classification of works, supplies and services; each covers "
              "many specific sectors.",
    },
    "div_lede_top": {
        "de": "Anzahl Zuschläge je Branche. Branchen sind die Abteilungen des CPV (erste zwei "
              "Ziffern), der EU-weit einheitlichen Einteilung der Leistungen; jede umfasst viele "
              "einzelne Bereiche. Hier die {k} häufigsten von {total}.",
        "fr": "Nombre d’adjudications par branche. Les branches sont les divisions du CPV, le "
              "vocabulaire commun pour les marchés publics de l’UE ; chacune regroupe de "
              "nombreux domaines détaillés. Voici les {k} plus fréquentes sur {total}.",
        "it": "Numero di aggiudicazioni per ramo. I rami sono le divisioni del CPV, la "
              "classificazione europea degli appalti; ognuno comprende molti settori specifici. "
              "Qui i rami più frequenti: {k} su {total}.",
        "en": "Number of awards per industry. Industries are the top-level groups of the CPV, "
              "the EU’s standard classification of works, supplies and services; each covers "
              "many specific sectors. Shown: the {k} most frequent of {total}.",
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
        "it": "Settori specifici (codice CPV esatto)",
        "en": "Specific sectors (exact CPV code)",
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
              "attribuable porte sur un montant supérieur, l’autre moitié sur un montant inférieur.",
        "it": "Importo tipico (mediana): {m} – metà delle aggiudicazioni con un importo "
              "attribuibile supera questo valore, l’altra metà resta al di sotto.",
        "en": "Typical amount (median): {m} – half of the awards with an attributable amount are "
              "above this figure, half below.",
    },
    # quotes the last label of lingue.BANDS word for word
    "bands_noown": {
        "de": "«Ohne zurechenbaren Betrag»: kein Betrag publiziert, Betrag in Fremdwährung oder "
              "Zuschlag an mehrere Unternehmen.",
        "fr": "« Sans montant attribuable » : montant non publié, montant en devise étrangère ou "
              "adjudication attribuée à plusieurs entreprises.",
        "it": "«Importo non attribuibile»: importo non pubblicato, in valuta estera o riferito a "
              "un’aggiudicazione attribuita a più imprese.",
        "en": "“No attributable CHF amount”: no amount published, an amount in a foreign "
              "currency, or an award made to several companies.",
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
    # Italian without an article before the figure: "vale 33%" lacked one, and the right one
    # changes with the number ("il 33%", "l’80%")
    "largest_share": {
        "de": "Allein der grösste Zuschlag macht {share} der Summe aus.",
        "fr": "À elle seule, la plus importante représente {share} du total.",
        "it": "Quota dell’aggiudicazione maggiore sul totale: {share}.",
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
             "E-Mail-Benachrichtigungen (siehe unten). "
             "Die Website wird über GitHub Pages ausgeliefert; der Hosting-Anbieter kann "
             "im Rahmen des Betriebs technische Verbindungsdaten wie IP-Adressen in "
             "eigenen Server-Logs erfassen."),
            ("Abonnement neuer Ausschreibungen (E-Mail und RSS)",
             "Wer neue Ausschreibungen per E-Mail erhalten möchte, meldet sich über das Formular "
             "auf der Abo-Seite an oder schreibt an abo@auftragsregister.ch. Das Abo wird erst "
             "aktiv, wenn der Bestätigungslink in der zugestellten E-Mail angeklickt wird "
             "(Double-Opt-in). Bearbeitet werden die E-Mail-Adresse, die gewählten Kantone und "
             "Branchen, die Sprache, der Zeitpunkt und die IP-Adresse der Bestätigung sowie während "
             "höchstens 45 Tagen die Liste der bereits zugestellten Ausschreibungen, damit keine "
             "Ausschreibung doppelt verschickt wird. Alle diese Daten werden ausschliesslich für "
             "den Versand der Benachrichtigungen bearbeitet; Grundlage ist Ihre eigene "
             "Anmeldung. Die E-Mails enthalten ein Zählpixel und Links, die über einen Server "
             "von Brevo laufen; Brevo kann dabei Öffnungen und Klicks erfassen. Sie können das "
             "verhindern, indem Sie das automatische Laden von Bildern ausschalten und die "
             "Ausschreibungen direkt auf auftragsregister.ch aufrufen. Abmelden können Sie sich "
             "jederzeit über den Link in jeder E-Mail oder per E-Mail mit dem Betreff «Stop»; "
             "danach entfernen wir Sie innert 30 Tagen aus der Verteilerliste und löschen die "
             "Liste der zugestellten Ausschreibungen. Bei Brevo bleiben Ihr Kontakteintrag "
             "(unter anderem E-Mail-Adresse und Zeitpunkt von Anmeldung und Bestätigung), der "
             "Vermerk der Abmeldung und die Versandprotokolle der bereits zugestellten E-Mails "
             "bestehen, damit Sie sicher keine weiteren E-Mails erhalten. Die Daten werden weder "
             "weitergegeben noch für andere Zwecke verwendet. Anmeldung und Versand laufen über "
             "Brevo (Sendinblue SAS, Paris, EU), das die Adressen nur in unserem Auftrag "
             "bearbeitet; eingehende E-Mails werden über ImprovMX Inc. (USA, Weiterleitung) an "
             "ein Postfach bei Google LLC (Gmail) zugestellt. Die RSS-Feeds erfordern keine "
             "Anmeldung und übermitteln uns keine Personendaten."),
            ("Archiv und Aufbewahrung",
             "Der Datenbestand wird täglich mit den Daten von simap.ch aktualisiert. Ältere "
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
             "compte utilisateur ; le seul formulaire est l’inscription facultative aux alertes "
             "par e-mail (voir ci-dessous). Le site est diffusé via GitHub Pages ; l’hébergeur "
             "peut enregistrer dans ses propres journaux des données techniques de connexion "
             "telles que les adresses IP."),
            ("Abonnement aux nouveaux appels d'offres (e-mail et RSS)",
             "Pour recevoir les nouveaux appels d'offres par e-mail, il suffit de remplir le "
             "formulaire de la page d’abonnement ou d’écrire à abo@auftragsregister.ch. "
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
             "Les données ne sont ni transmises ni utilisées à d'autres fins. L'inscription et "
             "l'envoi passent par Brevo (Sendinblue SAS, Paris, UE), qui traite les adresses "
             "uniquement pour notre compte ; les e-mails entrants sont acheminés par ImprovMX "
             "Inc. (États-Unis, service de redirection) vers une boîte aux lettres chez Google "
             "LLC (Gmail). Les flux RSS ne demandent aucune inscription et ne nous transmettent "
             "aucune donnée personnelle."),
            ("Archive et conservation",
             "Les données sont mises à jour chaque jour depuis simap.ch. Les "
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
             "l'iscrizione facoltativa agli avvisi via e-mail (vedi sotto). Il sito è "
             "distribuito tramite GitHub Pages; il fornitore di hosting può registrare nei "
             "propri log dati tecnici di connessione come gli indirizzi IP."),
            ("Abbonamento ai nuovi bandi (e-mail e RSS)",
             "Per ricevere i nuovi bandi via e-mail ci si iscrive con il modulo della pagina "
             "di abbonamento oppure si scrive ad abo@auftragsregister.ch. L’iscrizione diventa "
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
             "vengono ceduti a terzi né usati per altri scopi. Iscrizione e invio passano da "
             "Brevo (Sendinblue SAS, Parigi, UE), che tratta gli indirizzi solo per nostro "
             "conto; le e-mail in arrivo sono inoltrate da ImprovMX Inc. (USA) a una casella di "
             "posta presso Google LLC (Gmail). I feed RSS non richiedono iscrizione e non ci "
             "trasmettono dati personali."),
            ("Archivio e conservazione",
             "I dati vengono ripresi ogni giorno da simap.ch. Le pubblicazioni più "
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
             "optional sign-up for email alerts (see below). The site is served through GitHub "
             "Pages; the hosting provider may record technical connection data such as IP "
             "addresses in its own server logs."),
            ("Subscription to new tenders (email and RSS)",
             "To receive new tenders by email, sign up with the form on the subscription page or "
             "write to abo@auftragsregister.ch. The subscription only becomes active once you "
             "click the confirmation link sent to you by email (double opt-in). We process your "
             "email address, the cantons and industries you choose, your language, the time and "
             "IP address of your confirmation and, for no more than 45 days, the list of tenders "
             "already sent to you, so that none is sent twice; all of this solely to send these "
             "alerts, on the basis of your own sign-up. The emails contain a tracking pixel and "
             "links that pass through a Brevo server, so Brevo may record opens and clicks. You "
             "can prevent this by turning off automatic image loading and opening the tenders "
             "directly on auftragsregister.ch. You can unsubscribe at any time via the link in "
             "every email or by sending an email with the subject “Stop”; we then remove you "
             "from the mailing list within 30 days and delete the list of tenders sent. Brevo "
             "keeps your contact record (including your email address and the time of sign-up "
             "and confirmation), a record that you unsubscribed and the logs of the emails "
             "already sent, to make sure you receive no further emails. The data is neither "
             "shared nor used for any other purpose. Sign-up and sending are handled by Brevo "
             "(Sendinblue SAS, Paris, EU), which processes the addresses only on our behalf; "
             "incoming emails are forwarded by ImprovMX Inc. (USA) to a mailbox at Google LLC "
             "(Gmail). The RSS feeds need no sign-up and send us no personal data."),
            ("Archive and retention",
             "The data is refreshed daily from simap.ch. Older publications are kept as "
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


T["sector"] = {"de": "Bereich", "fr": "Domaine", "it": "Settore", "en": "Sector"}
T["year"] = {"de": "Jahr", "fr": "Année", "it": "Anno", "en": "Year"}
T["running_canton"] = {"de": "Offene Ausschreibungen · Kanton", "fr": "Appels d’offres en cours · Canton",
                       "it": "Bandi aperti · Cantone", "en": "Open now · Canton"}


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
    "it": "Nuovi bandi nel ramo «{sector}» {where} – via e-mail, gratis.",
    "en": "New tenders in the “{sector}” industry {where}: by email, free.",
}
META["alert_sector"] = {
    "de": "Neue Ausschreibungen der Branche «{sector}» aus der ganzen Schweiz — per E-Mail, "
          "kostenlos.",
    "fr": "Recevez gratuitement par e-mail les nouveaux appels d’offres de la branche « {sector} » "
          "de toute la Suisse.",
    "it": "Nuovi bandi nel ramo «{sector}» in tutta la Svizzera – via e-mail, gratis.",
    "en": "New tenders in the “{sector}” industry from all over Switzerland: by email, free.",
}
META["alert_canton"] = {
    "de": "Neue öffentliche Ausschreibungen {where} — per E-Mail, kostenlos.",
    "fr": "Recevez gratuitement par e-mail les nouveaux appels d’offres publics {where}.",
    "it": "Nuovi bandi pubblici {where} — via e-mail, gratis.",
    "en": "New public tenders {where}: by email, free.",
}
META["alert_none"] = {
    "de": "Neue öffentliche Ausschreibungen — per E-Mail, kostenlos.",
    "fr": "Recevez gratuitement par e-mail les nouveaux appels d’offres publics.",
    "it": "Nuovi bandi pubblici — via e-mail, gratis.",
    "en": "New public tenders: by email, free.",
}
META["alert_link"] = {"de": "Benachrichtigung einrichten", "fr": "Créer l'alerte",
                      "it": "Attivare l'avviso", "en": "Set up the alert"}
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
OPEN_CONTRACTS = {"de": ("offener Auftrag", "offene Aufträge"), "fr": ("marché ouvert", "marchés ouverts"),
                  "it": ("appalto aperto", "appalti aperti"), "en": ("open contract", "open contracts")}
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
T["activity"] = {"de": "Tätigkeitsbereich", "fr": "Domaine d'activité", "it": "Settore di attività",
                 "en": "Sector"}
PROSE["matched_tenders_one"] = {
    "de": "Offene Ausschreibung in verwandten Bereichen",
    "fr": "Appel d’offres en cours dans un domaine apparenté",
    "it": "Bando aperto in settori affini",
    "en": "Open tender in related sectors",
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
    "it": "{n} a favore di {f} nel settore «{label}».",
    "en": "{n} to {f} in the “{label}” sector.",
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
    "de": "{n} in der Branche «{name}» (CPV {code}) aus der ganzen Schweiz, täglich aktualisiert.",
    "fr": "{n} en Suisse dans la branche « {name} » (CPV {code}), avec mise à jour quotidienne.",
    "it": "{n} nel ramo «{name}» (CPV {code}) in tutta la Svizzera, con aggiornamento quotidiano.",
    "en": "{n} across Switzerland in the “{name}” industry (CPV {code}), updated daily.",
}
META["open_canton_desc_one"] = {
    "de": "{n} im Kanton {name}, täglich aktualisiert (Quelle: simap.ch).",
    "fr": "{n} dans le canton {of}, avec mise à jour quotidienne (source : simap.ch).",
    "it": "{n} nel Canton {name}, con aggiornamento quotidiano (fonte: simap.ch).",
    "en": "{n} in the canton of {name}, updated daily (source: simap.ch).",
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
    "de": "Die Eingabefrist ist am {when} abgelaufen. Wird der Zuschlag auf simap.ch publiziert, "
          "erscheint er unter dieser Adresse.",
    "fr": "Le délai de remise a expiré le {when}. Si l’adjudication est publiée sur simap.ch, elle "
          "apparaîtra à cette adresse.",
    "it": "Termine d’inoltro scaduto ({when}). Se l’aggiudicazione verrà pubblicata su simap.ch, "
          "comparirà a questo indirizzo.",
    "en": "The submission deadline passed on {when}. If the award is published on simap.ch, it "
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
META["nf_home"] = {"de": "Startseite", "fr": "Page d’accueil", "it": "Pagina iniziale",
                   "en": "Home page"}
# shown by the page's script when the missing URL was a tender's (/de/auftrag/<id>/)
META["nf_simap"] = {"de": "Diese Ausschreibung auf simap.ch öffnen",
                    "fr": "Ouvrir cet appel d’offres sur simap.ch",
                    "it": "Aprire questo bando su simap.ch",
                    "en": "Open this tender on simap.ch"}


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
    if lang in ("fr", "it", "en"):
        s = s.replace(" \u2026", "\u2026")
    return s


for _tbl in (T, PROSE, META, IDX):
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
for _tbl in (T, PROSE, META, IDX):
    for _k, _d in _tbl.items():
        for _l, _v in _d.items():
            assert " \u2014 " not in _v, (_k, _l, _v)
            if _l == "fr":
                assert not _re.search(r" [:;?!]", _v), (_k, _v)
