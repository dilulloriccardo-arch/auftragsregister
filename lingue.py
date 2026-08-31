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
                    "it": "Bando aperto", "en": "Tender open"},
    "sum": {"de": "Summe CHF", "fr": "Total CHF", "it": "Totale CHF", "en": "Total CHF"},
    "sum_published": {"de": "publizierte Summe CHF", "fr": "montant publié CHF",
                      "it": "importo pubblicato CHF", "en": "published value CHF"},
    "median": {"de": "Median CHF", "fr": "Médiane CHF", "it": "Mediana CHF",
               "en": "Median CHF"},
    "amount": {"de": "Betrag CHF", "fr": "Montant CHF", "it": "Importo CHF",
               "en": "Amount CHF"},
    "date": {"de": "Datum", "fr": "Date", "it": "Data", "en": "Date"},
    "contract": {"de": "Auftrag", "fr": "Marché", "it": "Appalto", "en": "Contract"},
    "buyer": {"de": "Auftraggeber", "fr": "Adjudicateur", "it": "Committente",
              "en": "Contracting authority"},
    "canton": {"de": "Kanton", "fr": "Canton", "it": "Cantone", "en": "Canton"},
    "canton_abbr": {"de": "Kt.", "fr": "Ct.", "it": "Cant.", "en": "Cant."},
    "deadline": {"de": "Eingabefrist", "fr": "Délai de remise", "it": "Termine",
                 "en": "Submission deadline"},
    "procedure": {"de": "Verfahren", "fr": "Procédure", "it": "Procedura",
                  "en": "Procedure"},
    "publication": {"de": "Publikation", "fr": "Publication", "it": "Pubblicazione",
                    "en": "Publication"},
    "published_on": {"de": "Publiziert", "fr": "Publié le", "it": "Pubblicato",
                     "en": "Published"},
    "offers": {"de": "eingegangene Angebote", "fr": "offres reçues",
               "it": "offerte ricevute", "en": "bids received"},
    "chronological": {"de": "chronologisch", "fr": "chronologique",
                      "it": "cronologico", "en": "chronological"},
    "by_awards": {"de": "nach Zuschlägen", "fr": "par adjudications",
                  "it": "per aggiudicazioni", "en": "by awards"},
    "main_sector": {"de": "Hauptbereich", "fr": "Domaine principal",
                    "it": "Settore principale", "en": "Main sector"},
    "activities": {"de": "Tätigkeitsbereiche", "fr": "Domaines d'activité",
                   "it": "Settori di attività", "en": "Activity sectors"},
    "reason": {"de": "Begründung des Auftraggebers", "fr": "Motivation de l'adjudicateur",
               "it": "Motivazione del committente", "en": "Contracting authority's reasons"},
    "description": {"de": "Beschreibung", "fr": "Description", "it": "Descrizione",
                    "en": "Description"},
    "details": {"de": "Angaben", "fr": "Détails", "it": "Dettagli", "en": "Details"},
    "type": {"de": "Auftragsart", "fr": "Type de marché", "it": "Tipo di appalto",
             "en": "Contract type"},
    "treaty": {"de": "Staatsvertrag", "fr": "Accord international",
               "it": "Trattato internazionale", "en": "International treaty"},
    "place": {"de": "Ort", "fr": "Lieu", "it": "Luogo", "en": "Place"},
    "source": {"de": "Quelle", "fr": "Source", "it": "Fonte", "en": "Source"},
    "updated": {"de": "Aktualisiert", "fr": "Mis à jour", "it": "Aggiornato",
                "en": "Updated"},
    "period": {"de": "Zeitraum", "fr": "Période", "it": "Periodo", "en": "Period"},
    "as_of": {"de": "Stand", "fr": "État au", "it": "Stato al", "en": "As of"},
    "entries": {"de": "Einträge", "fr": "Entrées", "it": "Voci", "en": "Entries"},
    "suppliers": {"de": "Anbieter", "fr": "Soumissionnaires", "it": "Offerenti",
                  "en": "Bidders"},
    "until": {"de": "bis", "fr": "jusqu'au", "it": "entro", "en": "until"},
    "running": {"de": "Laufend", "fr": "En cours", "it": "In corso", "en": "Current"},
    "language": {"de": "Sprache", "fr": "Langue", "it": "Lingua", "en": "Language"},
}


def t(key: str, lang: str) -> str:
    return T[key][lang]


# Longer strings that carry the register's own voice, kept apart from the labels.
PROSE: dict[str, dict[str, str]] = {
    "tagline": {
        "de": "Wer gewinnt die öffentlichen Aufträge der Schweiz.",
        "fr": "Qui remporte les marchés publics suisses.",
        "it": "Chi vince gli appalti pubblici svizzeri.",
        "en": "Who wins Switzerland's public contracts.",
    },
    "lead": {
        "de": "Jeder auf simap.ch publizierte Zuschlag, nach Unternehmen aufbereitet: "
              "Auftraggeber, Betrag, Verfahren — und welche Ausschreibungen gerade offen sind.",
        "fr": "Chaque adjudication publiée sur simap.ch, présentée par entreprise : "
              "adjudicateur, montant, procédure — et les appels d'offres en cours.",
        "it": "Ogni aggiudicazione pubblicata su simap.ch, riorganizzata per impresa: "
              "committente, importo, procedura — e i bandi attualmente aperti.",
        "en": "Every award published on simap.ch, arranged by company: contracting "
              "authority, amount, procedure — and which tenders are currently open.",
    },
    "source_note": {
        "de": "Amtliche Publikationen von Bund, Kantonen und Gemeinden",
        "fr": "Publications officielles de la Confédération, des cantons et des communes",
        "it": "Pubblicazioni ufficiali di Confederazione, cantoni e comuni",
        "en": "Official publications of the Confederation, cantons and communes",
    },
    "not_official": {
        "de": "Diese Website bereitet öffentlich publizierte Daten auf und ist kein Ersatz "
              "für simap.ch. Massgebend sind ausschliesslich die dort veröffentlichten "
              "Publikationen.",
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
        "fr": "Publication officielle : {link} — seule la publication qui y figure fait foi.",
        "it": "Pubblicazione ufficiale: {link} — fa fede esclusivamente quella pubblicazione.",
        "en": "Official publication: {link} — only the publication there is authoritative.",
    },
    "view_on_simap": {
        "de": "Projekt {n} auf simap.ch ansehen", "fr": "Voir le projet {n} sur simap.ch",
        "it": "Vedi il progetto {n} su simap.ch", "en": "View project {n} on simap.ch",
    },
    "matched_tenders": {
        "de": "Offene Ausschreibungen im selben Bereich",
        "fr": "Appels d'offres en cours dans le même domaine",
        "it": "Bandi aperti nello stesso settore",
        "en": "Open tenders in the same sector",
    },
    "matched_note": {
        "de": "Laufende Ausschreibungen, deren CPV-Code den bisherigen Zuschlägen dieses "
              "Unternehmens entspricht.",
        "fr": "Appels d'offres en cours dont le code CPV correspond aux adjudications "
              "obtenues par cette entreprise.",
        "it": "Bandi aperti il cui codice CPV corrisponde alle aggiudicazioni già ottenute "
              "da questa impresa.",
        "en": "Open tenders whose CPV code matches this company's previous awards.",
    },
    "peers": {
        "de": "Weitere Anbieter im selben Bereich", "fr": "Autres soumissionnaires du domaine",
        "it": "Altri offerenti nello stesso settore", "en": "Other bidders in the sector",
    },
    "open_tenders_h1": {
        "de": "Offene Ausschreibungen", "fr": "Appels d'offres en cours",
        "it": "Bandi aperti", "en": "Open tenders",
    },
    "chart_timeline": {
        "de": "Zuschläge im Zeitverlauf", "fr": "Adjudications dans le temps",
        "it": "Aggiudicazioni nel tempo", "en": "Awards over time"},
    "chart_timeline_cap": {
        "de": "Ein Punkt pro Zuschlag, waagrecht nach Datum, die Fläche im Verhältnis "
              "zum publizierten Betrag. Zuschläge ohne publizierten Betrag stehen offen "
              "auf der Grundlinie.",
        "fr": "Un point par adjudication, en abscisse la date, la surface proportionnelle "
              "au montant publié. Les adjudications sans montant publié restent ouvertes "
              "sur la ligne de base.",
        "it": "Un punto per aggiudicazione, in ascissa la data, l'area proporzionale "
              "all'importo pubblicato. Le aggiudicazioni senza importo restano vuote "
              "sulla linea di base.",
        "en": "One dot per award, date across, area proportional to the published amount. "
              "Awards with no published amount sit open on the baseline."},
    "chart_sectors": {
        "de": "Zuschläge nach Bereich", "fr": "Adjudications par domaine",
        "it": "Aggiudicazioni per settore", "en": "Awards by sector"},
    "chart_sectors_cap": {
        "de": "Die zehn häufigsten CPV-Bereiche, nach Anzahl publizierter Zuschläge.",
        "fr": "Les dix domaines CPV les plus fréquents, par nombre d'adjudications publiées.",
        "it": "I dieci settori CPV più frequenti, per numero di aggiudicazioni pubblicate.",
        "en": "The ten most frequent CPV sectors, by number of published awards."},
    "chart_firms": {
        "de": "Unternehmen nach Anzahl Zuschläge", "fr": "Entreprises par adjudications",
        "it": "Imprese per aggiudicazioni", "en": "Companies by awards"},
    "chart_firms_cap": {
        "de": "Die zehn Unternehmen mit den meisten publizierten Zuschlägen in diesem Bereich.",
        "fr": "Les dix entreprises comptant le plus d'adjudications publiées dans ce domaine.",
        "it": "Le dieci imprese con più aggiudicazioni pubblicate in questo ambito.",
        "en": "The ten companies with the most published awards in this area."},
    "chart_months": {
        "de": "Publizierte Zuschläge pro Monat", "fr": "Adjudications publiées par mois",
        "it": "Aggiudicazioni pubblicate per mese", "en": "Awards published per month"},
    "chart_months_cap": {
        "de": "Anzahl der auf simap.ch publizierten Zuschläge je Publikationsmonat.",
        "fr": "Nombre d'adjudications publiées sur simap.ch par mois de publication.",
        "it": "Numero di aggiudicazioni pubblicate su simap.ch per mese di pubblicazione.",
        "en": "Number of awards published on simap.ch by month of publication."},
    "translation_note": {
        "de": "Titel und Beschreibungen erscheinen in der Sprache, in der sie publiziert "
              "wurden. Nicht jede Publikation liegt in allen Landessprachen vor.",
        "fr": "Les titres et descriptions apparaissent dans la langue de publication. "
              "Toutes les publications ne sont pas disponibles dans toutes les langues.",
        "it": "Titoli e descrizioni compaiono nella lingua in cui sono stati pubblicati. "
              "Non tutte le pubblicazioni esistono in tutte le lingue.",
        "en": "Titles and descriptions appear in the language they were published in. Not "
              "every publication exists in every language.",
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
    "company_desc": {
        "de": "{name}: {n} auf simap.ch{val}{span}. Auftraggeber, Beträge, Kantone.",
        "fr": "{name} : {n} sur simap.ch{val}{span}. Adjudicateurs, montants, cantons.",
        "it": "{name}: {n} su simap.ch{val}{span}. Committenti, importi, cantoni.",
        "en": "{name}: {n} on simap.ch{val}{span}. Authorities, amounts, cantons.",
    },
    "company_lead": {
        "de": "{n} auf simap.ch publiziert{span}, {b}.",
        "fr": "{n} publiées sur simap.ch{span}, {b}.",
        "it": "{n} pubblicate su simap.ch{span}, {b}.",
        "en": "{n} published on simap.ch{span}, {b}.",
    },
    "buyers_count": {"de": "{k} verschiedene Auftraggeber", "fr": "{k} adjudicateurs différents",
                     "it": "{k} committenti diversi", "en": "{k} different authorities"},
    "award_suffix": {"de": " — Zuschlag", "fr": " — adjudication", "it": " — aggiudicazione",
                     "en": " — award"},
    "tender_suffix": {"de": " — Ausschreibung", "fr": " — appel d'offres",
                      "it": " — bando", "en": " — tender"},
    "buyer_title": {"de": " — vergebene Aufträge", "fr": " — marchés adjugés",
                    "it": " — appalti aggiudicati", "en": " — contracts awarded"},
    "buyer_desc": {
        "de": "{name}: {n} an {f} Unternehmen, publiziert auf simap.ch.",
        "fr": "{name} : {n} à {f} entreprises, publiées sur simap.ch.",
        "it": "{name}: {n} a {f} imprese, pubblicate su simap.ch.",
        "en": "{name}: {n} to {f} companies, published on simap.ch.",
    },
    "buyer_lead": {
        "de": "{n} an {f} Unternehmen vergeben und auf simap.ch publiziert.",
        "fr": "{n} attribuées à {f} entreprises et publiées sur simap.ch.",
        "it": "{n} assegnate a {f} imprese e pubblicate su simap.ch.",
        "en": "{n} awarded to {f} companies and published on simap.ch.",
    },
    "canton_title": {"de": "Öffentliche Aufträge Kanton {name}",
                     "fr": "Marchés publics canton de {name}",
                     "it": "Appalti pubblici cantone {name}",
                     "en": "Public contracts canton of {name}"},
    "canton_suffix": {"de": " — Zuschläge", "fr": " — adjudications",
                      "it": " — aggiudicazioni", "en": " — awards"},
    "canton_desc": {
        "de": "{n} im Kanton {name} auf simap.ch, {f} Unternehmen, mit Auftraggebern und Beträgen.",
        "fr": "{n} dans le canton de {name} sur simap.ch, {f} entreprises, avec adjudicateurs et montants.",
        "it": "{n} nel cantone {name} su simap.ch, {f} imprese, con committenti e importi.",
        "en": "{n} in the canton of {name} on simap.ch, {f} companies, with authorities and amounts.",
    },
    "canton_lead": {
        "de": "{n} an {f} Unternehmen, publiziert von kantonalen Ämtern, Gemeinden und Bundesstellen.",
        "fr": "{n} à {f} entreprises, publiées par les services cantonaux, communaux et fédéraux.",
        "it": "{n} a {f} imprese, pubblicate da uffici cantonali, comunali e federali.",
        "en": "{n} to {f} companies, published by cantonal, communal and federal bodies.",
    },
    "sector_suffix": {"de": " — Aufträge CH · CPV {code}", "fr": " — marchés CH · CPV {code}",
                      "it": " — appalti CH · CPV {code}", "en": " — contracts CH · CPV {code}"},
    "sector_desc": {
        "de": "{n} im Bereich {label} auf simap.ch, {f} Unternehmen.",
        "fr": "{n} dans le domaine {label} sur simap.ch, {f} entreprises.",
        "it": "{n} nel settore {label} su simap.ch, {f} imprese.",
        "en": "{n} in the {label} sector on simap.ch, {f} companies.",
    },
    "sector_lead": {"de": "{n} an {f} Unternehmen in diesem Beschaffungsbereich.",
                    "fr": "{n} à {f} entreprises dans ce domaine.",
                    "it": "{n} a {f} imprese in questo settore.",
                    "en": "{n} to {f} companies in this procurement sector."},
    "home_title": {"de": "Öffentliche Aufträge Schweiz — Zuschläge nach Unternehmen",
                   "fr": "Marchés publics suisses — adjudications par entreprise",
                   "it": "Appalti pubblici svizzeri — aggiudicazioni per impresa",
                   "en": "Swiss public contracts — awards by company"},
    "home_desc": {
        "de": "{n} auf simap.ch publizierte Zuschläge, nach Unternehmen aufbereitet: wer "
              "gewinnt welche öffentlichen Aufträge in der Schweiz und für welchen Betrag.",
        "fr": "{n} adjudications publiées sur simap.ch, présentées par entreprise : qui "
              "remporte quels marchés publics en Suisse et pour quel montant.",
        "it": "{n} aggiudicazioni pubblicate su simap.ch, riorganizzate per impresa: chi "
              "vince quali appalti pubblici in Svizzera e per quale importo.",
        "en": "{n} awards published on simap.ch, arranged by company: who wins which "
              "public contracts in Switzerland and for what amount.",
    },
    "open_title": {"de": "Offene Ausschreibungen Schweiz — laufende öffentliche Aufträge",
                   "fr": "Appels d'offres en cours en Suisse — marchés publics",
                   "it": "Bandi aperti in Svizzera — appalti pubblici in corso",
                   "en": "Open tenders in Switzerland — current public contracts"},
    "open_desc": {
        "de": "{n} laufende Ausschreibungen mit offener Eingabefrist aus dem öffentlichen "
              "Beschaffungswesen der Schweiz, nach Frist geordnet.",
        "fr": "{n} appels d'offres en cours avec délai ouvert dans les marchés publics "
              "suisses, classés par délai.",
        "it": "{n} bandi aperti con termine ancora valido negli appalti pubblici svizzeri, "
              "ordinati per scadenza.",
        "en": "{n} current tenders with an open deadline in Swiss public procurement, "
              "ordered by deadline.",
    },
    "open_lead": {
        "de": "{n} Ausschreibungen mit noch offener Eingabefrist, publiziert von Bund, "
              "Kantonen und Gemeinden auf simap.ch.",
        "fr": "{n} appels d'offres dont le délai est encore ouvert, publiés par la "
              "Confédération, les cantons et les communes sur simap.ch.",
        "it": "{n} bandi con termine ancora aperto, pubblicati da Confederazione, cantoni "
              "e comuni su simap.ch.",
        "en": "{n} tenders with a deadline still open, published by the Confederation, "
              "cantons and communes on simap.ch.",
    },
    "open_canton_title": {"de": "Offene Ausschreibungen {name}",
                          "fr": "Appels d'offres en cours {name}",
                          "it": "Bandi aperti {name}", "en": "Open tenders {name}"},
    "open_truncated": {
        "de": "Diese Seite zeigt die {shown} Ausschreibungen mit der nächsten Frist von "
              "insgesamt {total}. Die übrigen stehen auf den Kantonsseiten unten.",
        "fr": "Cette page montre les {shown} appels d'offres dont le délai est le plus "
              "proche, sur {total} au total. Les autres figurent sur les pages cantonales "
              "ci-dessous.",
        "it": "Questa pagina mostra i {shown} bandi con la scadenza più vicina su {total} "
              "totali. Gli altri sono nelle pagine cantonali qui sotto.",
        "en": "This page shows the {shown} tenders with the nearest deadline out of "
              "{total}. The rest are on the canton pages below."},
    "open_canton_desc": {
        "de": "{n} laufende Ausschreibungen im Kanton {name} mit offener Eingabefrist.",
        "fr": "{n} appels d'offres en cours dans le canton de {name}, délai ouvert.",
        "it": "{n} bandi aperti nel cantone {name}, termine ancora valido.",
        "en": "{n} current tenders in the canton of {name} with an open deadline.",
    },
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
        "fr": "Toutes les entreprises avec au moins deux adjudications publiées, par ordre alphabétique.",
        "it": "Tutte le imprese con almeno due aggiudicazioni pubblicate, in ordine alfabetico.",
        "en": "Every company with at least two published awards, alphabetically."},
    "companies_title": {"de": "Unternehmen mit öffentlichen Aufträgen — Verzeichnis",
                        "fr": "Entreprises titulaires de marchés publics — répertoire",
                        "it": "Imprese con appalti pubblici — elenco",
                        "en": "Companies holding public contracts — directory"},
    "companies_desc": {
        "de": "Verzeichnis von {n} Unternehmen mit publizierten Zuschlägen aus dem "
              "öffentlichen Beschaffungswesen der Schweiz.",
        "fr": "Répertoire de {n} entreprises titulaires d'adjudications publiées dans les "
              "marchés publics suisses.",
        "it": "Elenco di {n} imprese con aggiudicazioni pubblicate negli appalti pubblici svizzeri.",
        "en": "Directory of {n} companies with published awards from Swiss public procurement."},
    "buyers_h1": {"de": "Auftraggeber", "fr": "Adjudicateurs", "it": "Committenti",
                  "en": "Contracting authorities"},
    "buyers_lead": {
        "de": "Beschaffungsstellen von Bund, Kantonen und Gemeinden, alphabetisch.",
        "fr": "Services acheteurs de la Confédération, des cantons et des communes, par ordre alphabétique.",
        "it": "Stazioni appaltanti di Confederazione, cantoni e comuni, in ordine alfabetico.",
        "en": "Purchasing bodies of the Confederation, cantons and communes, alphabetically."},
    "buyers_title": {"de": "Auftraggeber im öffentlichen Beschaffungswesen — Verzeichnis",
                     "fr": "Adjudicateurs des marchés publics — répertoire",
                     "it": "Committenti degli appalti pubblici — elenco",
                     "en": "Contracting authorities in public procurement — directory"},
    "buyers_desc": {
        "de": "Verzeichnis von {n} Beschaffungsstellen und den Aufträgen, die sie auf simap.ch publiziert haben.",
        "fr": "Répertoire de {n} services acheteurs et des marchés qu'ils ont publiés sur simap.ch.",
        "it": "Elenco di {n} stazioni appaltanti e degli appalti pubblicati su simap.ch.",
        "en": "Directory of {n} purchasing bodies and the contracts they published on simap.ch."},
    "cantons_lead": {"de": "Publizierte Zuschläge nach Kanton der Auftragsausführung.",
                     "fr": "Adjudications publiées par canton d'exécution.",
                     "it": "Aggiudicazioni pubblicate per cantone di esecuzione.",
                     "en": "Published awards by canton of performance."},
    "cantons_title": {"de": "Öffentliche Aufträge nach Kanton — Übersicht",
                      "fr": "Marchés publics par canton — aperçu",
                      "it": "Appalti pubblici per cantone — panoramica",
                      "en": "Public contracts by canton — overview"},
    "cantons_desc": {
        "de": "Publizierte Zuschläge aus dem öffentlichen Beschaffungswesen der Schweiz, nach Kanton geordnet.",
        "fr": "Adjudications publiées dans les marchés publics suisses, classées par canton.",
        "it": "Aggiudicazioni pubblicate negli appalti pubblici svizzeri, ordinate per cantone.",
        "en": "Published awards from Swiss public procurement, ordered by canton."},
    "sectors_h1": {"de": "Beschaffungsbereiche", "fr": "Domaines de marchés",
                   "it": "Settori di appalto", "en": "Procurement sectors"},
    "sectors_lead": {"de": "Publizierte Zuschläge nach CPV-Bereich.",
                     "fr": "Adjudications publiées par domaine CPV.",
                     "it": "Aggiudicazioni pubblicate per settore CPV.",
                     "en": "Published awards by CPV sector."},
    "sectors_title": {"de": "Öffentliche Aufträge nach Bereich — CPV-Übersicht",
                      "fr": "Marchés publics par domaine — aperçu CPV",
                      "it": "Appalti pubblici per settore — panoramica CPV",
                      "en": "Public contracts by sector — CPV overview"},
    "sectors_desc": {
        "de": "Publizierte Zuschläge nach Beschaffungsbereich (CPV), mit den Unternehmen, die sie erhalten haben.",
        "fr": "Adjudications publiées par domaine (CPV), avec les entreprises qui les ont obtenues.",
        "it": "Aggiudicazioni pubblicate per settore (CPV), con le imprese che le hanno ottenute.",
        "en": "Published awards by procurement sector (CPV), with the companies that won them."},
    "all_companies": {"de": "Alle Unternehmen", "fr": "Toutes les entreprises",
                      "it": "Tutte le imprese", "en": "All companies"},
    "all_buyers": {"de": "Alle Auftraggeber", "fr": "Tous les adjudicateurs",
                   "it": "Tutti i committenti", "en": "All authorities"},
    "all_cantons": {"de": "Alle Kantone", "fr": "Tous les cantons",
                    "it": "Tutti i cantoni", "en": "All cantons"},
    "all_sectors": {"de": "Alle Bereiche", "fr": "Tous les domaines",
                    "it": "Tutti i settori", "en": "All sectors"},
    "next_deadlines": {"de": "Nächste Eingabefristen", "fr": "Prochains délais",
                       "it": "Prossime scadenze", "en": "Next deadlines"},
    "open_count": {"de": "{n} offen", "fr": "{n} en cours", "it": "{n} aperti",
                   "en": "{n} open"},
    "by_canton": {"de": "Nach Kanton", "fr": "Par canton", "it": "Per cantone",
                  "en": "By canton"},
    "by_sector": {"de": "Nach Bereich", "fr": "Par domaine", "it": "Per settore",
                  "en": "By sector"},
    "awarded_in": {"de": "Vergebene Aufträge {c}", "fr": "Marchés adjugés {c}",
                   "it": "Appalti aggiudicati {c}", "en": "Contracts awarded {c}"},
    "all_open": {"de": "Alle offenen Ausschreibungen", "fr": "Tous les appels d'offres",
                 "it": "Tutti i bandi aperti", "en": "All open tenders"},
    "same_sector": {"de": "Gleicher Bereich", "fr": "Même domaine",
                    "it": "Stesso settore", "en": "Same sector"},
    "contracts_in": {"de": "Aufträge im Kanton {c}", "fr": "Marchés dans le canton {c}",
                     "it": "Appalti nel cantone {c}", "en": "Contracts in canton {c}"},
}


def i(key: str, lang: str, **kw) -> str:
    return IDX[key][lang].format(**kw) if kw else IDX[key][lang]
