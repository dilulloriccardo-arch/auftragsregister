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
    # Plain-language pass (22.10.2026, owner): Firmen / aziende, enti pubblici / acheteurs publics /
    # public buyers, the 8-digit CPV level a Kategorie / catégorie / categoria / category
    "companies": {"de": "Firmen", "fr": "Entreprises", "it": "Aziende",
                  "en": "Companies"},
    "buyers": {"de": "Auftraggeber", "fr": "Acheteurs publics", "it": "Enti pubblici",
               "en": "Public buyers"},
    "cantons": {"de": "Kantone", "fr": "Cantons", "it": "Cantoni", "en": "Cantons"},
    "sectors": {"de": "Kategorien", "fr": "Catégories", "it": "Categorie", "en": "Categories"},
    "contracts": {"de": "Aufträge", "fr": "Marchés", "it": "Appalti", "en": "Contracts"},
    "tenders": {"de": "Ausschreibungen", "fr": "Appels d'offres", "it": "Bandi",
                "en": "Tenders"},
    # the awards under a figure, over a list, in a heading: «Zuschläge» / «aggiudicazioni» were the
    # procurement office's word (owner, 22.10.2026); awards_col is the short form a table column takes
    "award": {"de": "Vergebener Auftrag", "fr": "Marché attribué", "it": "Appalto aggiudicato",
              "en": "Contract awarded"},
    "awards": {"de": "Vergebene Aufträge", "fr": "Marchés attribués", "it": "Appalti aggiudicati",
               "en": "Contracts awarded"},
    "awards_col": {"de": "Aufträge", "fr": "Marchés", "it": "Appalti", "en": "Contracts"},
    "award_granted": {"de": "Auftrag vergeben", "fr": "Marché attribué",
                      "it": "Appalto aggiudicato", "en": "Contract awarded"},
    "tender_open": {"de": "Ausschreibung offen", "fr": "Appel d'offres en cours",
                    "it": "Bando aperto", "en": "Open tender"},
    "sum": {"de": "Summe (CHF)", "fr": "Total (CHF)", "it": "Totale (CHF)", "en": "Total (CHF)"},
    "sum_published": {"de": "Summe in CHF", "fr": "Total en CHF",
                      "it": "Totale in CHF", "en": "Total awarded (CHF)"},
    "median": {"de": "Typischer Betrag (Median)", "fr": "Montant typique (médiane)", "it": "Importo tipico (mediana)",
               "en": "Typical amount (median)"},
    # the award lists (company, buyer, a project's lots): no currency in the header, which stood over
    # euro and dollar amounts; a foreign amount names its currency in its cell (08.10.2026)
    "amount": {"de": "Betrag", "fr": "Montant", "it": "Importo", "en": "Amount"},
    "date": {"de": "Datum", "fr": "Date", "it": "Data", "en": "Date"},
    "contract": {"de": "Auftrag", "fr": "Marché", "it": "Appalto", "en": "Contract"},
    "buyer": {"de": "Auftraggeber", "fr": "Acheteur public", "it": "Ente pubblico",
              "en": "Public buyer"},
    "canton": {"de": "Kanton", "fr": "Canton", "it": "Cantone", "en": "Canton"},
    "canton_abbr": {"de": "Kt.", "fr": "Cant.", "it": "Cant.", "en": "Canton"},
    # the home's company table: the canton where most of the firm's awards fall, not its seat
    "canton_most": {"de": "Kanton mit den meisten Aufträgen", "fr": "Canton comptant le plus de marchés",
                    "it": "Cantone con più appalti", "en": "Canton with the most contracts"},
    # Italian: «Scadenza», the word the lists already used ('Prossime scadenze'); the official «termine
    # d'inoltro» is explained once on the about page (natural-voice pass, 23.10.2026)
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
    "chronological": {"de": "neueste zuerst", "fr": "les plus récents d’abord",
                      "it": "dal più recente", "en": "newest first"},
    "by_awards": {"de": "nach Anzahl Aufträge", "fr": "par nombre de marchés",
                  "it": "per numero di appalti", "en": "by number of contracts"},
    "main_sector": {"de": "Hauptkategorie", "fr": "Catégorie principale",
                    "it": "Categoria principale", "en": "Main category"},
    "activities": {"de": "Kategorien", "fr": "Catégories",
                   "it": "Categorie", "en": "Categories"},
    "reason": {"de": "Begründung des Auftraggebers", "fr": "Motivation de l'acheteur public",
               "it": "Motivazione dell'ente pubblico", "en": "Reasons given by the public buyer"},
    "description": {"de": "Beschreibung", "fr": "Description", "it": "Descrizione",
                    "en": "Description"},
    "details": {"de": "Angaben", "fr": "Détails", "it": "Dettagli", "en": "Details"},
    "type": {"de": "Art des Auftrags", "fr": "Type de marché", "it": "Tipo di appalto",
             "en": "Contract type"},
    # a soft hyphen: the Details column breaks the compound there rather than mid-syllable
    "treaty": {"de": "Staatsvertrags\u00adbereich", "fr": "Accord international",
               "it": "Trattato internazionale", "en": "International treaty"},
    "place": {"de": "Ort", "fr": "Lieu", "it": "Luogo", "en": "Location"},
    "source": {"de": "Quelle", "fr": "Source", "it": "Fonte", "en": "Source"},
    # The date is the newest publication's (DATA_DATE), named as the footer names it (META["stand"]).
    # «aggiornato al 22.10.2026» as the owner approved it (22.10.2026); in running text it_dates() elides
    # 'al 08.' / 'al 11.' to 'all’08.' / 'all’11.', a label over its date stays 'Aggiornato al'
    "updated": {"de": "Aktualisiert am", "fr": "Mis à jour le", "it": "Aggiornato al",
                "en": "Updated"},
    "period": {"de": "Zeitraum", "fr": "Période", "it": "Periodo", "en": "Period"},
    # one label for the same date on the home and the tenders pages
    "as_of": {"de": "Aktualisiert am", "fr": "Mis à jour le", "it": "Aggiornato al", "en": "Updated"},
    "entries": {"de": "Einträge", "fr": "Nombre", "it": "Voci", "en": "Entries"},
    "until": {"de": "bis", "fr": "jusqu'au", "it": "entro il", "en": "due"},
    "running": {"de": "Offene Ausschreibungen", "fr": "Appels d’offres en cours", "it": "Bandi aperti", "en": "Open tenders"},
    "language": {"de": "Sprache", "fr": "Langue", "it": "Lingua", "en": "Language"},
    "company": {"de": "Firma", "fr": "Entreprise", "it": "Azienda", "en": "Company"},
    "tender": {"de": "Ausschreibung", "fr": "Appel d’offres", "it": "Bando", "en": "Tender"},
    "winner": {"de": "Vergeben an", "fr": "Attribué à", "it": "Aggiudicato a", "en": "Awarded to"},
    "award_to": {"de": "Vergeben an", "fr": "Attribué à", "it": "Aggiudicato a", "en": "Awarded to"},
    "award_amount": {
        "de": "Betrag des Auftrags",
        "fr": "Montant attribué",
        "it": "Importo aggiudicato",
        "en": "Amount awarded",
    },
    "approx": {"de": "rund {v}", "fr": "environ {v}", "it": "circa {v}", "en": "about {v}"},
    "median_help": {
        "de": "Die Hälfte der Aufträge mit zurechenbarem Betrag liegt darüber, die andere Hälfte "
              "darunter.",
        "fr": "La moitié des marchés avec un montant attribuable est au-dessus, l’autre moitié en dessous.",
        "it": "Metà degli appalti con un importo attribuibile sta sopra questo valore, metà sotto.",
        "en": "Half of the contracts with an attributable amount are above this figure, half below.",
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
        "it": "importo non attribuibile",
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
    "joint": {"de": "an mehrere Firmen", "fr": "à plusieurs entreprises", "it": "a più aziende",
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
    # (the home's "lead" is at the end of the file, in the 'strictly necessary' pass)
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
    # the same meaning in plainer words (natural-voice pass, 23.10.2026)
    "footer_note": {
        "de": "Diese Website bereitet öffentlich publizierte Daten auf und ersetzt simap.ch nicht.",
        "fr": "Ce site présente des données publiées officiellement et ne remplace pas "
              "simap.ch. Seules les publications de simap.ch font foi.",
        "it": "Questo sito rielabora dati pubblicati ufficialmente e non sostituisce "
              "simap.ch. Fanno fede solo le pubblicazioni su simap.ch.",
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
        "de": "Offene Ausschreibungen in verwandten Kategorien",
        "fr": "Appels d’offres en cours dans des catégories proches",
        "it": "Bandi aperti in categorie simili",
        "en": "Open tenders in related categories",
    },
    # (the note under it, "matched_note", is at the end of the file, in the 'strictly necessary' pass)
    # grouped on the first four significant CPV digits of the main code: related sectors,
    # not one exact code (the same wording as the matched tenders above it)
    "peers": {
        "de": "Weitere Firmen in verwandten Kategorien", "fr": "Autres entreprises dans des catégories proches",
        "it": "Altre aziende in categorie simili", "en": "Other companies in related categories",
    },
    "analysis": {
        "de": "Aufträge pro Jahr", "fr": "Marchés par année", "it": "Appalti per anno", "en": "Contracts per year",
    },
    # our own figures, marked as such (simap's terms §5): said by the one who worked them out
    "derived": {
        "de": "von uns aus den Publikationen berechnet", "fr": "calculé par nous à partir des publications",
        "it": "calcolato da noi sui dati pubblicati", "en": "worked out by us from the published data",
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
    "company_title_short": {"de": " — Aufträge", "fr": " — marchés", "it": " — appalti",
                            "en": " — contracts"},
    # natural-voice pass (owner, 23.10.2026): who did what, with a verb ('Implenia Schweiz AG hat 102 Aufträge
    # gewonnen'); {n} is the count with its noun, {span} ' (Okt. 2024 – Okt. 2026)', {val} ', zusammen …'
    "company_desc": {
        "de": "{name} hat {n} gewonnen{span}{val} – laut simap.ch. Mit Auftraggebern, Beträgen und Kantonen.",
        "fr": "{name} a remporté {n}{span}{val}, selon simap.ch. Acheteurs publics, montants et cantons.",
        "it": "{name} ha vinto {n}{span}{val}, secondo simap.ch. Qui trovi enti pubblici, importi e cantoni.",
        "en": "{name} has won {n}{span}{val}, according to simap.ch. With public buyers, amounts and cantons.",
    },
    "company_val": {
        "de": ", zusammen {v}",
        "fr": ", au total {v}",
        "it": ", per un totale di {v}",
        "en": ", {v} in total",
    },
    "top_buyer_share": {
        "de": "Häufigster Auftraggeber: {buyer} ({share} der Aufträge).",
        "fr": "Acheteur public le plus fréquent : {buyer} ({share} des marchés).",
        "it": "Ente pubblico più frequente: {buyer} ({share} degli appalti).",
        "en": "Most frequent public buyer: {buyer} ({share} of contracts).",
    },
    "top_buyer_only": {
        "de": "Alle Aufträge stammen von {buyer}.",
        "fr": "Tous les marchés viennent de {buyer}.",
        "it": "Tutti gli appalti vengono da {buyer}.",
        "en": "All contracts come from {buyer}.",
    },
    # (the company page's lead, "company_lead", is at the end of the file, in the 'strictly necessary' pass)
    "buyers_count": {"de": "{k} verschiedenen Auftraggebern", "fr": "{k} acheteurs publics différents",
                     "it": "{k} enti pubblici diversi", "en": "{k} different public buyers"},
    "award_suffix": {"de": " — vergeben", "fr": " — attribué", "it": " — aggiudicato",
                     "en": " — awarded"},
    "tender_suffix": {"de": " — Ausschreibung", "fr": " — appel d'offres",
                      "it": " — bando", "en": " — tender"},
    "buyer_title": {"de": " — vergebene Aufträge", "fr": " — marchés attribués",
                    "it": " — appalti aggiudicati", "en": " — contracts awarded"},
    # a shorter suffix, for the few authorities whose long names differ only in the middle
    "buyer_title_short": {"de": " — Aufträge", "fr": " — marchés", "it": " — appalti",
                          "en": " — contracts"},
    "buyer_desc": {
        "de": "{name} hat {n} an {f} vergeben, laut simap.ch.",
        "fr": "{name} a attribué {n} à {f}, selon simap.ch.",
        "it": "{name} ha aggiudicato {n} a {f}, secondo simap.ch.",
        "en": "{name} has awarded {n} to {f}, according to simap.ch.",
    },
    # (the buyer page's lead, "buyer_lead", is at the end of the file)
    "buyer_joint_note": {
        "de": "{k} Aufträge gingen an mehrere Firmen.",
        "fr": "{k} marchés ont été attribués à plusieurs entreprises.",
        "it": "{k} appalti sono andati a più aziende.",
        "en": "{k} contracts went to several companies.",
    },
    "canton_title": {"de": "Öffentliche Aufträge im Kanton {name}",
                     "fr": "Marchés publics du canton {of}",
                     "it": "Appalti pubblici nel Canton {name}",
                     "en": "Public contracts in the canton of {name}"},
    "canton_suffix": {"de": " — wer sie gewinnt", "fr": " — qui les remporte",
                      "it": " — chi li vince", "en": " — who wins them"},
    "canton_desc": {
        "de": "Im Kanton {name} gingen {n} an {f}: Beträge, Branchen und Verlauf Monat für Monat, laut simap.ch.",
        "fr": "Dans le canton {of}, {n} ont été attribués à {f} : montants, secteurs et évolution mois par mois, "
              "selon simap.ch.",
        "it": "Nel Canton {name} {n} sono andati a {f}: importi, settori e andamento mese per mese, secondo "
              "simap.ch.",
        "en": "In the canton of {name}, {n} went to {f}: amounts, sectors and the month-by-month trend, according "
              "to simap.ch.",
    },
    # (the canton page's lead, "canton_lead", is at the end of the file: the canton pages count awards by the
    # canton where the contract is carried out; many were published by companies owned by the state)
    "sector_suffix": {"de": " – CPV {code}", "fr": " – CPV {code}",
                      "it": " – CPV {code}", "en": " – CPV {code}"},
    # with the keyword a searcher types, where the sector's name leaves room for it
    "sector_suffix_long": {"de": " – Aufträge · CPV {code}", "fr": " – marchés · CPV {code}",
                           "it": " – appalti · CPV {code}", "en": " – contracts · CPV {code}"},
    # the project number at the end of an award or tender <title>, where two pages share a title
    "title_no": {"de": "Nr. {n}", "fr": "n°\u00a0{n}", "it": "n. {n}", "en": "no. {n}"},
    "sector_desc": {
        "de": "In der Kategorie «{label}» gingen {n} an {f}, laut simap.ch.",
        "fr": "Dans la catégorie « {label} », {n} ont été attribués à {f}, selon simap.ch.",
        "it": "Nella categoria «{label}» {n} sono andati a {f}, secondo simap.ch.",
        "en": "In the “{label}” category, {n} went to {f}, according to simap.ch.",
    },
    "sector_lead": {"de": "In dieser Kategorie gingen {n} an {f}.",
                    "fr": "Dans cette catégorie, {n} ont été attribués à {f}.",
                    "it": "In questa categoria {n} sono andati a {f}.",
                    "en": "In this category, {n} went to {f}."},
    "home_title": {"de": "Öffentliche Aufträge Schweiz — wer welche Aufträge gewinnt",
                   "fr": "Marchés publics suisses — qui remporte quels marchés",
                   "it": "Appalti pubblici svizzeri — chi vince quali appalti",
                   "en": "Swiss Public Contracts — who wins which contracts"},
    "home_desc": {
        "de": "Wer gewinnt die öffentlichen Aufträge in der Schweiz – und zu welchem Betrag? {n} vergebene "
              "Aufträge von simap.ch, nach Firma geordnet.",
        "fr": "Qui remporte les marchés publics en Suisse, et pour quel montant ? {n} marchés attribués, publiés "
              "sur simap.ch et classés par entreprise.",
        "it": "Chi vince gli appalti pubblici in Svizzera, e per quanto? {n} appalti aggiudicati, pubblicati su "
              "simap.ch e ordinati per azienda.",
        "en": "Who wins public contracts in Switzerland, and for how much? {n} contracts awarded, published on "
              "simap.ch and sorted by company.",
    },
    "open_title": {"de": "Öffentliche Ausschreibungen Schweiz: {n} offen",
                   "fr": "Appels d’offres publics en Suisse : {n} en cours",
                   "it": "Bandi di gara in Svizzera: {n} aperti",
                   "en": "Public tenders in Switzerland: {n} open"},
    "open_desc": {
        "de": "Offene Ausschreibungen von Bund, Kantonen und Gemeinden an einem Ort. Nach Frist, Kanton und "
              "Branche filtern – oder gratis per E-Mail erhalten.",
        "fr": "Les appels d’offres en cours de la Confédération, des cantons et des communes, réunis ici. Par "
              "délai, canton et secteur – aussi par e-mail, gratuitement.",
        "it": "I bandi aperti di Confederazione, Cantoni e Comuni in un unico posto. Filtra per scadenza, "
              "cantone e settore, o ricevili gratis via e-mail.",
        "en": "Open tenders from the Confederation, cantons and communes in one place. Filter by deadline, "
              "canton and sector – or get them by email, free.",
    },
    # the hub's 'how to read this list', behind a <details>: what is listed and in which order; when it is updated
    # the paragraph under it says
    "open_lead": {
        "de": "{n} Ausschreibungen von Bund, Kantonen und Gemeinden, deren Eingabefrist noch läuft – publiziert "
              "auf simap.ch. Wir ordnen sie nach Frist und gliedern sie nach Kanton und Branche.",
        "fr": "{n} appels d’offres de la Confédération, des cantons et des communes dont le délai court encore, "
              "publiés sur simap.ch. Nous les classons par délai, par canton et par secteur.",
        "it": "{n} bandi ancora aperti di Confederazione, Cantoni e Comuni, pubblicati su simap.ch. Li "
              "ordiniamo per scadenza e li raggruppiamo per cantone e settore.",
        "en": "{n} tenders from the Confederation, cantons and communes whose deadline is still open, published "
              "on simap.ch. We sort them by deadline and group them by canton and sector.",
    },
    # no heading may promise a search the page does not have ("Ausschreibungen suchen: So
    # funktioniert es"; audit 13.10.2026)
    "open_howto_h2": {
        "de": "So ist die Liste aufgebaut",
        "fr": "Comment lire cette liste",
        "it": "Come leggere l’elenco",
        "en": "How to read this list",
    },
    "open_howto": {
        "de": "Oben stehen die Ausschreibungen, deren Frist zuerst abläuft. Jede Zeile führt zur Ausschreibung: "
              "Auftraggeber, Frist, Kategorie (CPV-Code) und Link zur amtlichen Publikation. Auf den "
              "Kantonsseiten finden Sie die Ausschreibungen Ihrer Region, auf den Branchenseiten die für Ihr "
              "Gewerbe: Bau, Planung, IT, Versicherungen, Fahrzeuge und mehr. Die Daten stammen von simap.ch, der "
              "amtlichen Plattform. Wir aktualisieren sie in der Regel werktags, sobald simap.ch die Publikationen "
              "des Tages freigegeben hat.",
        "fr": "En haut, les appels d’offres dont le délai expire en premier. Chaque ligne ouvre la fiche de "
              "l’appel d’offres : acheteur public, délai, catégorie (code CPV) et lien vers la publication "
              "officielle. Les pages des cantons montrent les appels d’offres de votre région, celles des secteurs "
              "ceux de votre métier : construction, études, informatique, assurances, véhicules, etc. Les données "
              "viennent de simap.ch, la plateforme officielle. Nous les mettons à jour en règle générale les jours "
              "ouvrables, dès que simap.ch a mis en ligne les publications du jour.",
        "it": "In cima trovi i bandi che scadono prima. Ogni riga apre la scheda del bando: ente pubblico, "
              "scadenza, categoria (codice CPV) e link alla pubblicazione ufficiale. Nelle pagine dei cantoni "
              "trovi i bandi della tua regione, in quelle dei settori i bandi del tuo mestiere: edilizia, "
              "progettazione, informatica, assicurazioni, veicoli e altro. I dati vengono da simap.ch, la "
              "piattaforma ufficiale. Li aggiorniamo di solito nei giorni feriali, dopo che simap.ch ha messo a "
              "disposizione le pubblicazioni del giorno.",
        "en": "The tenders that close first are at the top. Each row opens the tender: public buyer, deadline, "
              "category (CPV code) and a link to the official publication. Canton pages show the tenders in "
              "your region, sector pages those in your line of work: construction, engineering, IT, insurance, "
              "vehicles and more. The data comes from simap.ch, the official platform. We usually update it "
              "Monday to Saturday, once simap.ch has released the day’s publications.",
    },
    "open_by_canton_h2": {
        "de": "Offene Ausschreibungen nach Kanton", "fr": "Appels d’offres en cours par canton",
        "it": "Bandi aperti per cantone", "en": "Open tenders by canton",
    },
    "open_canton_lede": {
        "de": "Klicken Sie auf einen Kanton, um seine offenen Ausschreibungen zu sehen – nach Frist geordnet.",
        "fr": "Cliquez sur un canton pour voir ses appels d’offres en cours, par ordre d’échéance.",
        "it": "Clicca su un cantone per vedere i suoi bandi aperti, in ordine di scadenza.",
        "en": "Click a canton to see its open tenders, sorted by deadline.",
    },
    # fix round 3: on a touch screen the map is tapped
    "open_canton_lede_tap": {
        "de": "Tippen Sie auf einen Kanton, um seine offenen Ausschreibungen zu sehen – nach Frist geordnet.",
        "fr": "Touchez un canton pour voir ses appels d’offres en cours, par ordre d’échéance.",
        "it": "Tocca un cantone per vedere i suoi bandi aperti, in ordine di scadenza.",
        "en": "Tap a canton to see its open tenders, sorted by deadline.",
    },
    "open_by_sector_h2": {
        "de": "Ausschreibungen nach Branche", "fr": "Appels d'offres par secteur",
        "it": "Bandi per settore", "en": "Tenders by sector",
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
    "feed_all": {"de": "ganze Schweiz", "fr": "toute la Suisse", "it": "tutta la Svizzera", "en": "all of Switzerland"},
    "feed_link": {"de": "RSS-Feed", "fr": "Flux RSS", "it": "Feed RSS", "en": "RSS feed"},
    # The free e-mail service under its one name per language (owner, 22.10.2026): «Ausschreibungen per
    # E-Mail» / «Appels d’offres par e-mail» / «Bandi via e-mail» / «Tenders by email»; the call to action
    # says what one gets, the short button «Gratis abonnieren» / «S’abonner gratuitement» / «Iscriviti
    # gratis» / «Subscribe free». Italian: the controls in the familiar imperative, the prose impersonal.
    "abo_cta": {"de": "Neue Ausschreibungen gratis per E-Mail",
                "fr": "Recevoir gratuitement les nouveaux appels d’offres par e-mail",
                "it": "Ricevi gratis i nuovi bandi via e-mail",
                "en": "Get new tenders by email – free"},
    # No "every day" / "täglich" about the e-mail: the sender writes only on days with new matching
    # tenders (08.10.2026)
    "abo_title": {"de": "Ausschreibungen per E-Mail oder RSS-Feed – gratis",
                  "fr": "Appels d’offres par e-mail ou flux RSS – gratuit",
                  "it": "Bandi via e-mail o feed RSS – gratis",
                  "en": "Tenders by email or RSS feed – free"},
    "abo_desc": {"de": "Erhalten Sie neue öffentliche Ausschreibungen der Schweiz gratis per E-Mail, nach Kanton "
                       "und Branche – oder als RSS-Feed. Quelle: simap.ch.",
                 "fr": "Recevez gratuitement par e-mail les nouveaux appels d’offres publics en Suisse, par canton "
                       "et par secteur – ou suivez-les par flux RSS. Source : simap.ch.",
                 "it": "Ricevi gratis via e-mail i nuovi bandi pubblici in Svizzera, per cantone e settore, oppure "
                       "seguili con un feed RSS. Fonte: simap.ch.",
                 "en": "Get new Swiss public tenders by email, free, by canton and sector – or follow them by RSS "
                       "feed. Source: simap.ch."},
    "abo_h1": {"de": "Ausschreibungen per E-Mail",
               "fr": "Appels d’offres par e-mail",
               "it": "Bandi via e-mail",
               "en": "Tenders by email"},
    # (the page's lead, "abo_lead", and the RSS heading, "abo_rss_h2", are at the end of the file)
    "abo_rss_text": {"de": "Jede Kantons- und Branchenseite hat einen Feed. Fügen Sie die Adresse in Ihren "
                           "Feed-Reader, in Outlook (RSS-Abonnements) oder in einen RSS-zu-E-Mail-Dienst ein.",
                     "fr": "Chaque page de canton et de secteur a son propre flux. Ajoutez son "
                           "adresse à votre lecteur de flux, à Outlook (abonnements RSS) ou à un "
                           "service qui transforme les flux RSS en e-mails.",
                     "it": "Ogni pagina di cantone e di settore ha il suo feed. Aggiungi l’indirizzo al tuo "
                           "lettore di feed, a Outlook (abbonamenti RSS) o a un servizio che ti inoltra i feed "
                           "via e-mail.",
                     "en": "Every canton and sector page has its own feed. Add its address to "
                           "your feed reader, to Outlook (RSS subscriptions) or to an "
                           "RSS-to-email service."},
    "abo_rss_all": {"de": "Alle neuen Ausschreibungen der Schweiz", "fr": "Tous les nouveaux appels d'offres suisses",
                    "it": "Tutti i nuovi bandi svizzeri", "en": "All new Swiss tenders"},
    "abo_by_canton": {"de": "Feeds nach Kanton", "fr": "Flux par canton", "it": "Feed per cantone", "en": "Feeds by canton"},
    "abo_by_sector": {"de": "Feeds nach Branche", "fr": "Flux par secteur", "it": "Feed per settore",
                      "en": "Feeds by sector"},
    "abo_check_title": {"de": "Fast geschafft: Bitte bestätigen Sie Ihre E-Mail-Adresse",
                        "fr": "Plus qu’une étape : confirmez votre adresse e-mail",
                        "it": "Quasi fatto: conferma il tuo indirizzo e-mail",
                        "en": "Almost done: please confirm your email address"},
    # the click on the link is what starts the subscription (double opt-in)
    "abo_check": {"de": "Wir haben Ihnen eine E-Mail geschickt. Klicken Sie auf den Link darin, um Ihr Abo zu "
                        "aktivieren.",
                  "fr": "Nous vous avons envoyé un e-mail. Cliquez sur le lien qu’il contient pour activer votre "
                        "abonnement.",
                  "it": "Ti abbiamo mandato un’e-mail. Clicca sul link che trovi dentro per attivare l’iscrizione.",
                  "en": "We’ve sent you an email. Click the link in it to start your subscription."},
    "abo_ok_title": {"de": "Anmeldung bestätigt", "fr": "Abonnement confirmé", "it": "Iscrizione confermata",
                     "en": "Subscription confirmed"},
    # (the done page's first line, "abo_ok", is at the end of the file)
    "abo_back": {"de": "Zurück zur Anmeldung", "fr": "Retour à l’inscription", "it": "Torna all’iscrizione",
                 "en": "Back to sign-up"},
    # the form's heading says what to do; its button the short call (owner, 22.10.2026)
    "abo_form_h2": {"de": "Kantone und Branchen wählen", "fr": "Choisir cantons et secteurs",
                    "it": "Scegli cantoni e settori", "en": "Choose cantons and sectors"},
    "abo_form_email": {"de": "E-Mail-Adresse", "fr": "Adresse e-mail", "it": "Indirizzo e-mail",
                       "en": "Email address"},
    # what an empty choice means, said as one would say it
    "abo_form_cantons": {"de": "Kantone (ohne Auswahl: ganze Schweiz)", "fr": "Cantons (sans choix : toute la Suisse)",
                         "it": "Cantoni (se non ne scegli nessuno: tutta la Svizzera)",
                         "en": "Cantons (none chosen: all of Switzerland)"},
    "abo_form_sectors": {"de": "Branchen (ohne Auswahl: alle)", "fr": "Secteurs (sans choix : tous)",
                         "it": "Settori (se non ne scegli nessuno: tutti)", "en": "Sectors (none chosen: all)"},
    "abo_form_submit": {"de": "Gratis abonnieren", "fr": "S'abonner gratuitement", "it": "Iscriviti gratis",
                        "en": "Subscribe free"},
    # (the consent under the button, "abo_form_consent", is at the end of the file: an e-mail only on a day with
    # new matching tenders, none without a match, 08.10.2026)
    "abo_form_sending": {"de": "Wird gesendet\u00a0…", "fr": "Envoi en cours…", "it": "Invio in corso…",
                         "en": "Sending…"},
    "abo_form_ok": {"de": "Fast geschafft: Bitte klicken Sie auf den Link in der E-Mail, die wir Ihnen gerade geschickt haben.",
                    "fr": "Plus qu’une étape : cliquez sur le lien de l’e-mail que nous venons de vous envoyer.",
                    "it": "Quasi fatto: clicca sul link nell’e-mail che ti abbiamo appena mandato.",
                    "en": "Almost done: please click the link in the email we’ve just sent you."},
    "abo_form_err": {"de": "Das hat nicht geklappt. Prüfen Sie bitte die E-Mail-Adresse oder schreiben Sie uns an "
                           "{mail}.",
                     "fr": "L’inscription n’a pas fonctionné. Vérifiez l’adresse e-mail ou écrivez-nous à {mail}.",
                     "it": "L’iscrizione non è riuscita. Controlla l’indirizzo e-mail o scrivici ad {mail}.",
                     "en": "That didn’t work. Please check the email address or write to us at {mail}."},
    "open_kpi_open": {"de": "offene Ausschreibungen", "fr": "appels d’offres en cours",
                      "it": "bandi aperti", "en": "open tenders"},
    "open_kpi_cantons": {"de": "Kantone mit offenen Ausschreibungen", "fr": "cantons avec des appels d’offres en cours",
                         "it": "cantoni con bandi aperti", "en": "cantons with open tenders"},
    # the industries that HAVE an open tender (41 of the 45 on 14.10.2026), like the canton tile beside it
    "open_kpi_sectors": {"de": "Branchen mit offenen Ausschreibungen", "fr": "secteurs avec des appels d’offres en cours",
                         "it": "settori con bandi aperti", "en": "sectors with open tenders"},
    "open_kpi_next": {"de": "nächste Eingabefrist", "fr": "prochain délai",
                      "it": "prossima scadenza", "en": "next deadline"},
    "cmp_h2": {"de": "simap.ch und dieses Register",
               "fr": "simap.ch et ce registre",
               "it": "simap.ch e questo registro",
               "en": "simap.ch and this register"},
    "cmp_lead": {"de": "simap.ch ist die amtliche Plattform und bleibt die massgebende Quelle. Wir übernehmen "
                       "ihre Daten regelmässig und beantworten zusätzlich Fragen, die Sie dort nicht stellen "
                       "können.",
                 "fr": "simap.ch est la plateforme officielle et reste la source qui fait foi. Nous reprenons "
                       "régulièrement ses données et répondons aussi à des questions que vous ne pouvez pas y "
                       "poser.",
                 "it": "simap.ch è la piattaforma ufficiale e resta la fonte che fa fede. Noi ne riprendiamo "
                       "regolarmente i dati e rispondiamo anche a domande che su simap.ch non puoi fare.",
                 "en": "simap.ch is the official platform and remains the authoritative source. We take its data "
                       "regularly and also answer questions you can’t ask there."},
    "cmp_us": {"de": "auftragsregister.ch", "fr": "auftragsregister.ch", "it": "auftragsregister.ch",
               "en": "auftragsregister.ch"},
    "cmp_yes": {"de": "ja", "fr": "oui", "it": "sì", "en": "yes"},
    "cmp_no": {"de": "nein", "fr": "non", "it": "no", "en": "no"},
    "cmp_link": {"de": "verweist darauf", "fr": "y renvoie", "it": "con il link",
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
    "cmp_r3": {"de": "Vergebene Aufträge nach Firma zusammengefasst",
               "fr": "Marchés attribués regroupés par entreprise",
               "it": "Appalti aggiudicati raggruppati per azienda",
               "en": "Contracts awarded, grouped by company"},
    "cmp_r4": {"de": "Wer hat vergleichbare Aufträge gewonnen – und zu welchem Betrag?",
               "fr": "Qui a remporté des marchés comparables, et pour quel montant ?",
               "it": "Chi ha vinto appalti simili e per quale importo?",
               "en": "Who won similar contracts, and for how much?"},
    "cmp_r5": {"de": "Auswertungen nach Kanton, Branche und Monat",
               "fr": "Analyses par canton, par secteur et dans le temps",
               "it": "Analisi per cantone, settore e andamento nel tempo",
               "en": "Analysis by canton, sector and over time"},
    "cmp_r6": {"de": "RSS-Feed pro Kanton und Branche",
               "fr": "Flux RSS par canton et par secteur",
               "it": "Feed RSS per cantone e settore",
               "en": "RSS feed for each canton and sector"},
    "cmp_r7": {"de": "Neue Ausschreibungen per E-Mail, nach Ihrer Auswahl",
               "fr": "Nouveaux appels d’offres par e-mail, selon vos critères",
               "it": "Nuovi bandi via e-mail, solo quelli che ti interessano",
               "en": "New tenders by email, matching your own filters"},
    "cmp_r8": {"de": "Ohne Konto nutzbar", "fr": "Sans compte",
               "it": "Si usa senza account", "en": "No account needed"},
    "open_sector_desc": {
        "de": "{n} in der Branche «{name}» (CPV {code}) aus der ganzen Schweiz, nach "
              "Eingabefrist geordnet.",
        "fr": "{n} en Suisse dans le secteur « {name} » (CPV {code}), par ordre d’échéance.",
        "it": "{n} nel settore «{name}» (CPV {code}) in tutta la Svizzera, in ordine di scadenza.",
        "en": "{n} across Switzerland in the “{name}” sector (CPV {code}), sorted by deadline.",
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
    "open_canton_t3": {"de": "{name}: {o}", "fr": "{name} : {o}", "it": "{name}: {o}", "en": "{name}: {o}"},
    "open_sector_t1": {"de": "{word} in der Schweiz: {k} offen",
                       "fr": "{word} en Suisse : {k} en cours",
                       "it": "{word} in Svizzera: {k} aperti",
                       "en": "{word} in Switzerland: {k} open"},
    "open_sector_t2": {"de": "{word} in der Schweiz: {k} offen", "fr": "{word} en Suisse : {k} en cours",
                       "it": "{word} in Svizzera: {k} aperti", "en": "{word} in Switzerland: {k} open"},
    "open_sector_desc_word": {
        "de": "Die {k} offenen {w} der Schweiz auf simap.ch, nach Frist und Kanton geordnet. Auch gratis "
              "per E-Mail, ohne Konto.",
        "fr": "Les {k} {w} en cours en Suisse (simap.ch), par délai et par canton. Aussi par e-mail, "
              "gratuitement et sans compte.",
        "it": "I {k} {w} aperti in Svizzera (simap.ch), in ordine di scadenza e per cantone. Ricevili gratis "
              "anche via e-mail.",
        "en": "The {k} open {w} in Switzerland on simap.ch, by deadline and canton. Also by email – free, no "
              "account needed.",
    },
    "open_canton_h1": {
        "de": "Offene Ausschreibungen im Kanton {name}",
        "fr": "Appels d’offres en cours dans le canton {of}",
        "it": "Bandi aperti nel Canton {name}",
        "en": "Open public tenders in the canton of {name}",
    },
    "open_canton_desc": {
        "de": "{n} im Kanton {name}, nach Frist geordnet und werktags aktualisiert. Auch gratis per E-Mail, "
              "ohne Konto.",
        "fr": "{n} dans le canton {of}, par délai, mis à jour les jours ouvrables. Aussi par e-mail, "
              "gratuitement et sans compte.",
        "it": "{n} nel Canton {name}, in ordine di scadenza e aggiornati nei giorni feriali. Ricevili gratis "
              "anche via e-mail.",
        "en": "{n} in the canton of {name}, sorted by deadline and updated Monday to Saturday. Also by email – "
              "free, no account needed.",
    },
    "desc_deadline": {
        "de": ", Eingabefrist {date}",
        "fr": ", délai de remise : {date}",
        "it": ", scadenza {date}",
        "en": ", submission deadline {date}",
    },
    "desc_won": {
        "de": ", vergeben an {who}",
        "fr": ", attribué à {who}",
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

# Plural of the central noun, per language: a count of awards in prose ('345 Aufträge an 210 Firmen').
# «Zuschläge» / «adjudications» / «aggiudicazioni» / «awards» were the procurement office's words; the
# templates around the count say 'vergeben' / 'attribués' / 'aggiudicati' / 'awarded' where it matters
# (plain-language pass, 22.10.2026). French and Italian templates agree with the masculine noun.
PLURALS: dict[str, tuple[str, str]] = {
    "de": ("Auftrag", "Aufträge"), "fr": ("marché", "marchés"),
    "it": ("appalto", "appalti"), "en": ("contract", "contracts"),
}


# Italian elides the article before a day read with a vowel: 'aggiornato all’08.10.2026', 'dall’11.10.',
# 'entro l’08.10.2026' (the owner's «aggiornato al 22.10.2026», 22.10.2026). A date may sit in a <time>.
_IT_DAY = __import__("re").compile(r"(?<![\w’'])(al|dal|del|nel|il|Al|Dal|Del|Nel|Il)[  ](?=(?:<[^>]+>)?(?:08|8|11)\.\d)")
_IT_ELIDED = {"al": "all’", "dal": "dall’", "del": "dell’", "nel": "nell’", "il": "l’"}


def it_dates(s: str) -> str:
    """'al 08.10.2026' -> 'all’08.10.2026', 'il 11.10.' -> 'l’11.10.' (Italian; other text unchanged)."""
    def one(mo):
        w = mo.group(1)
        out = _IT_ELIDED[w.lower()]
        return out[0].upper() + out[1:] if w[0].isupper() else out
    return _IT_DAY.sub(one, s)


def m(key: str, lang: str, **kw) -> str:
    if not kw:
        return META[key][lang]
    s = _DOTS.sub(".", elide(META[key][lang], lang, kw).format(**kw))
    return it_dates(s) if lang == "it" else s


IDX: dict[str, dict[str, str]] = {
    "companies_h1": {"de": "Firmen im Register", "fr": "Entreprises du registre",
                     "it": "Aziende nel registro", "en": "Companies in the register"},
    "companies_lead": {
        "de": "Alle Firmen, die mindestens zwei Aufträge gewonnen haben, von A bis Z.",
        "fr": "Toutes les entreprises qui ont remporté au moins deux marchés, de A à Z.",
        "it": "Tutte le aziende che hanno vinto almeno due appalti, dalla A alla Z.",
        "en": "Every company that has won at least two contracts, from A to Z."},
    "companies_title": {"de": "Firmen mit öffentlichen Aufträgen — Verzeichnis",
                        "fr": "Entreprises qui remportent des marchés publics — répertoire",
                        "it": "Aziende con appalti pubblici — elenco",
                        "en": "Companies winning public contracts — directory"},
    # the same population as the lead: companies with at least two awards (the home counts
    # every company, 6,278, and a bare "2574 Unternehmen" contradicted it)
    "companies_desc": {
        "de": "Die {n} Firmen, die mindestens zwei öffentliche Aufträge gewonnen haben, von A bis Z. Daten von "
              "simap.ch.",
        "fr": "Les {n} entreprises qui ont remporté au moins deux marchés publics, de A à Z. Données de "
              "simap.ch.",
        "it": "Le {n} aziende che hanno vinto almeno due appalti pubblici, dalla A alla Z. Dati di simap.ch.",
        "en": "The {n} companies that have won at least two public contracts, from A to Z. Data from "
              "simap.ch."},
    "buyers_h1": {"de": "Auftraggeber im Register", "fr": "Acheteurs publics du registre", "it": "Enti pubblici nel registro",
                  "en": "Public buyers in the register"},
    "cantons_h1": {"de": "Öffentliche Aufträge nach Kanton", "fr": "Marchés publics par canton",
                   "it": "Appalti pubblici per cantone", "en": "Public contracts by canton"},
    "buyers_lead": {
        "de": "Alle Auftraggeber, die mindestens drei Aufträge vergeben haben, von A bis Z.",
        "fr": "Tous les acheteurs publics qui ont attribué au moins trois marchés, de A à Z.",
        "it": "Tutti gli enti pubblici che hanno aggiudicato almeno tre appalti, dalla A alla Z.",
        "en": "Every public buyer that has awarded at least three contracts, from A to Z."},
    "buyers_title": {"de": "Öffentliche Auftraggeber — Verzeichnis",
                     "fr": "Acheteurs publics en Suisse — répertoire",
                     "it": "Enti pubblici che aggiudicano appalti — elenco",
                     "en": "Public buyers awarding contracts — directory"},
    "buyers_desc": {
        "de": "Die {n} Auftraggeber, die mindestens drei Aufträge vergeben haben, von A bis Z. Daten von "
              "simap.ch.",
        "fr": "Les {n} acheteurs publics qui ont attribué au moins trois marchés, de A à Z. Données de "
              "simap.ch.",
        "it": "I {n} enti pubblici che hanno aggiudicato almeno tre appalti, dalla A alla Z. Dati di simap.ch.",
        "en": "The {n} public buyers that have awarded at least three contracts, from A to Z. Data from "
              "simap.ch."},
    "cantons_lead": {"de": "Wir zählen jeden Auftrag im Kanton, den die Publikation als Ort der Leistung nennt. "
                           "Fehlt diese Angabe, zählt der Kanton des Auftraggebers.",
                     "fr": "Nous comptons chaque marché dans le canton du lieu d’exécution indiqué dans la "
                           "publication. S’il manque, dans celui de l’acheteur public.",
                     "it": "Contiamo ogni appalto nel cantone che la pubblicazione indica come luogo di "
                           "esecuzione. Se manca, in quello dell’ente pubblico.",
                     "en": "We count each contract in the canton the publication gives as the place of "
                           "performance. If it gives none, we use the public buyer’s canton."},
    "cantons_title": {"de": "Öffentliche Aufträge nach Kanton — Übersicht",
                      "fr": "Marchés publics par canton — aperçu",
                      "it": "Appalti pubblici per cantone — panoramica",
                      "en": "Public contracts by canton — overview"},
    "cantons_desc": {
        "de": "Die vergebenen öffentlichen Aufträge der Schweiz, Kanton für Kanton.",
        "fr": "Les marchés publics attribués en Suisse, canton par canton.",
        "it": "Gli appalti pubblici aggiudicati in Svizzera, cantone per cantone.",
        "en": "Public contracts awarded in Switzerland, canton by canton."},
    "sectors_h1": {"de": "Öffentliche Aufträge nach Kategorie", "fr": "Marchés publics par catégorie",
                   "it": "Appalti pubblici per categoria", "en": "Public contracts by category"},
    "sectors_lead": {"de": "Die vergebenen Aufträge, Kategorie für Kategorie. Die Kategorien stammen aus dem CPV, "
                           "der EU-weit einheitlichen Einteilung der Leistungen.",
                     "fr": "Les marchés attribués, catégorie par catégorie. Les catégories sont celles du CPV, "
                           "le vocabulaire commun de l’UE pour les marchés publics.",
                     "it": "Gli appalti aggiudicati, categoria per categoria. Le categorie sono quelle del CPV, "
                           "il vocabolario comune dell’UE per gli appalti pubblici.",
                     "en": "Contracts awarded, category by category. The categories are those of the CPV, the "
                           "EU’s Common Procurement Vocabulary."},
    "sectors_title": {"de": "Öffentliche Aufträge nach Kategorie — CPV-Übersicht",
                      "fr": "Marchés publics par catégorie — aperçu CPV",
                      "it": "Appalti pubblici per categoria — panoramica CPV",
                      "en": "Public contracts by category — CPV overview"},
    "sectors_desc": {
        "de": "Vergebene Aufträge nach Kategorie (CPV), mit den Firmen, die sie erhalten "
              "haben.",
        "fr": "Marchés attribués par catégorie (CPV), avec les entreprises qui les ont remportés.",
        "it": "Appalti aggiudicati per categoria (CPV), con le aziende che li hanno vinti.",
        "en": "Contracts awarded by category (CPV), with the companies that won them."},
    "all_companies": {"de": "Alle Firmen", "fr": "Toutes les entreprises",
                      "it": "Tutte le aziende", "en": "All companies"},
    "all_buyers": {"de": "Alle Auftraggeber", "fr": "Tous les acheteurs publics",
                   "it": "Tutti gli enti pubblici", "en": "All public buyers"},
    "all_cantons": {"de": "Alle Kantone", "fr": "Tous les cantons",
                    "it": "Tutti i cantoni", "en": "All cantons"},
    "all_sectors": {"de": "Alle Kategorien", "fr": "Toutes les catégories",
                    "it": "Tutte le categorie", "en": "All categories"},
    "next_deadlines": {"de": "Nächste Eingabefristen", "fr": "Prochains délais",
                       "it": "Prossime scadenze", "en": "Next deadlines"},
    "open_count": {"de": "{n} offen", "fr": "{n} en cours", "it": "{n} bandi aperti",
                   "en": "{n} open"},
    "by_canton": {"de": "Nach Kanton", "fr": "Par canton", "it": "Per cantone",
                  "en": "By canton"},
    "by_sector": {"de": "Nach Kategorie", "fr": "Par catégorie", "it": "Per categoria",
                  "en": "By category"},
    "awarded_in": {"de": "Vergebene Aufträge im Kanton {c}", "fr": "Marchés attribués dans le canton {of}",
                   "it": "Appalti aggiudicati nel Canton {c}", "en": "Contracts awarded in the canton of {c}"},
    "all_open": {"de": "Alle offenen Ausschreibungen", "fr": "Tous les appels d’offres en cours",
                 "it": "Tutti i bandi aperti", "en": "All open tenders"},
    "same_sector": {"de": "Aufträge in derselben Kategorie", "fr": "Marchés de la même catégorie",
                    "it": "Appalti della stessa categoria", "en": "Contracts in the same category"},
    "contracts_in": {"de": "Aufträge im Kanton {c}", "fr": "Marchés du canton {of}",
                     "it": "Appalti nel Canton {c}", "en": "Contracts in the canton of {c}"},
    # the monthly charts (owner, 22.10.2026: «Appalti aggiudicati ogni mese»)
    "mc_title_home": {
        "de": "Vergebene Aufträge pro Monat in der ganzen Schweiz",
        "fr": "Marchés attribués chaque mois dans toute la Suisse",
        "it": "Appalti aggiudicati ogni mese in tutta la Svizzera",
        "en": "Contracts awarded each month across Switzerland",
    },
    "mc_title_canton": {
        "de": "Vergebene Aufträge pro Monat im Kanton {name}",
        "fr": "Marchés attribués chaque mois dans le canton {of}",
        "it": "Appalti aggiudicati ogni mese nel Canton {name}",
        "en": "Contracts awarded each month in the canton of {name}",
    },
    "mc_title_buyer": {
        "de": "Vergebene Aufträge dieses Auftraggebers pro Monat",
        "fr": "Marchés attribués par cet acheteur public, chaque mois",
        "it": "Appalti aggiudicati da questo ente pubblico ogni mese",
        "en": "Contracts awarded by this public buyer each month",
    },
    "mc_title_sector": {
        "de": "Vergebene Aufträge pro Monat in dieser Kategorie",
        "fr": "Marchés attribués chaque mois dans cette catégorie",
        "it": "Appalti aggiudicati ogni mese in questa categoria",
        "en": "Contracts awarded each month in this category",
    },
    # computed from complete months only, and it says so: the running month can already be
    # taller than the peak named here (20 chart pages per language on 28.09.2026)
    "mc_takeaway": {
        "de": "Seit {start} im Schnitt {avg} pro Monat. Stärkster vollständiger Monat: {peak_month} ({peak}).",
        "fr": "Depuis {start}, {avg} par mois en moyenne. Le mois complet le plus chargé a été {peak_month} "
              "({peak}).",
        "it": "Da {start} in media {avg} al mese. Il mese completo con più appalti è stato {peak_month} ({peak}).",
        "en": "Since {start}, an average of {avg} a month. The busiest complete month was {peak_month} ({peak}).",
    },
    # two complete months tie for the most awards: both are named
    "mc_takeaway_two": {
        "de": "Seit {start} im Schnitt {avg} pro Monat. Stärkste vollständige Monate: {months} (je {peak}).",
        "fr": "Depuis {start}, {avg} par mois en moyenne. Les mois complets les plus chargés ont été {months} "
              "({peak} chacun).",
        "it": "Da {start} in media {avg} al mese. I mesi completi con più appalti sono stati {months} "
              "({peak} ciascuno).",
        "en": "Since {start}, an average of {avg} a month. The busiest complete months were {months} "
              "({peak} each).",
    },
    # three or more tie: the value, and how often it was reached
    "mc_takeaway_many": {
        "de": "Seit {start} im Schnitt {avg} pro Monat. Höchstens {peak} in einem vollständigen Monat, erreicht "
              "in {k} Monaten.",
        "fr": "Depuis {start}, {avg} par mois en moyenne. Au plus {peak} sur un mois complet, atteint {k} fois.",
        "it": "Da {start} in media {avg} al mese. Il massimo in un mese completo è {peak}, raggiunto {k} volte.",
        "en": "Since {start}, an average of {avg} a month. At most {peak} in a complete month, reached in "
              "{k} months.",
    },
    "mc_unit": {
        "de": "Anzahl Aufträge",
        "fr": "Nombre de marchés",
        "it": "Numero di appalti",
        "en": "Number of contracts",
    },
    # Incomplete months are drawn STRIPED (the notes once called them "lighter", a colour nobody saw on the dark
    # panel); the striped build-up months are the archive's coverage, not a market trend. The notes themselves,
    # "mc_note_start" … "mc_note_end_zero", are at the end of the file, in the 'strictly necessary' pass.
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
        "fr": "{n}, tous publiés en {month}.",
        "it": "{n}, tutti pubblicati a {month}.",
        "en": "{n}, all published in {month}.",
    },
    "mc_few_single": {
        "de": "{n}, publiziert im {month}.",
        "fr": "{n}, publié en {month}.",
        "it": "{n}, pubblicato a {month}.",
        "en": "{n}, published in {month}.",
    },
    # «Appalti aggiudicati per settore» (owner, 22.10.2026)
    "div_title": {
        "de": "Vergebene Aufträge nach Branche",
        "fr": "Marchés attribués par secteur",
        "it": "Appalti aggiudicati per settore",
        "en": "Contracts awarded by sector",
    },
    # A Branche (division, 2 digits) groups many Kategorien (exact 8-digit codes); what they are, the about page
    # says ("div_lede_all" and "div_lede_top" are at the end of the file, in the 'strictly necessary' pass)
    "div_other": {
        "de": "{k} weitere Branchen",
        "fr": "Autres secteurs ({k})",
        "it": "Altri {k} settori",
        "en": "Other sectors ({k})",
    },
    # one industry only: a sentence instead of a single bar at 100 %
    "div_single": {
        "de": "Alle {n} gehören zur Branche «{label}».",
        "fr": "Les {n} sont tous du secteur « {label} ».",
        "it": "Tutti i {n} sono del settore «{label}».",
        "en": "All {n} are in the “{label}” sector.",
    },
    "div_single_one": {
        "de": "Der einzige Auftrag gehört zur Branche «{label}».",
        "fr": "Le seul marché est du secteur « {label} ».",
        "it": "L’unico appalto è del settore «{label}».",
        "en": "The only contract is in the “{label}” sector.",
    },
    "detail_sectors": {
        "de": "Einzelne Kategorien (genauer CPV-Code)",
        "fr": "Catégories détaillées (code CPV exact)",
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
        "de": "Wie gross sind die Aufträge von {name}?",
        "fr": "Combien valent les marchés remportés par {name} ?",
        "it": "Quanto valgono gli appalti vinti da {name}?",
        "en": "How large are the contracts won by {name}?",
    },
    "bands_lede": {
        "de": "Anzahl Aufträge je Betragsklasse.",
        "fr": "Nombre de marchés par tranche de montant.",
        "it": "Numero di appalti per fascia d’importo.",
        "en": "Number of contracts by amount band.",
    },
    "bands_median": {
        "de": "Typischer Betrag (Median): {m} – die Hälfte der Aufträge mit zurechenbarem Betrag "
              "liegt darüber, die andere Hälfte darunter.",
        "fr": "Montant typique (médiane) : {m} – la moitié des marchés dotés d’un montant "
              "attribuable se situe au-dessus de ce montant, l’autre moitié en dessous.",
        "it": "Importo tipico (mediana): {m} – metà degli appalti con un importo "
              "attribuibile supera questo valore, l’altra metà resta al di sotto.",
        "en": "Typical amount (median): {m} – half of the contracts with an attributable amount are "
              "above this figure, half below.",
    },
    # quotes the last label of lingue.BANDS word for word
    "bands_noown": {
        "de": "«Ohne zurechenbaren Betrag» heisst: kein Betrag publiziert, Betrag in Fremdwährung, Auftrag an "
              "mehrere Firmen oder vermutlich ein Einheitspreis.",
        "fr": "« Sans montant attribuable » signifie : aucun montant publié, un montant en devise étrangère, un "
              "marché attribué à plusieurs entreprises ou probablement un prix unitaire.",
        "it": "«Importo non attribuibile» vuol dire: nessun importo pubblicato, importo in valuta estera, "
              "appalto andato a più aziende o probabile prezzo unitario.",
        "en": "“No attributable CHF amount” means: no amount published, an amount in a foreign currency, a "
              "contract awarded to several companies, or probably a unit rate.",
    },
    # every award without a CHF amount of its own: a sentence, not five empty bars
    "bands_none": {
        "de": "Keiner der {n} Aufträge hat einen zurechenbaren Betrag in CHF.",
        "fr": "Aucun des {n} marchés n’a de montant attribuable en CHF.",
        "it": "Nessuno dei {n} appalti ha un importo in CHF attribuibile.",
        "en": "None of the {n} contracts has an attributable CHF amount.",
    },
    "largest_h": {
        "de": "Die grössten Aufträge",
        "fr": "Les marchés les plus importants",
        "it": "Gli appalti più grandi",
        "en": "The largest contracts",
    },
    # Italian: genera puts the article before the figure ("il 33%", "l’80%"; step 5); none before "oltre il 99%"
    "largest_share": {
        "de": "Allein der grösste Auftrag macht {share} der Summe aus.",
        "fr": "À lui seul, le plus important représente {share} du total.",
        "it": "Il più grande vale da solo {share} del totale.",
        "en": "The largest contract alone accounts for {share} of the total.",
    },
    # a share between 99.5 and 100 %, in prose ("macht mehr als 99 % der Summe aus")
    "over_pct": {
        "de": "mehr als {p}",
        "fr": "plus de {p}",
        "it": "oltre il {p}",
        "en": "more than {p}",
    },
    # an award that names several firms is often a set of separate awards (one per lot,
    # section or framework contract): the notes say "an mehrere Firmen", never "gemeinsam".
    # Such an award has no amount to split: simap publishes one price per firm, which the rows
    # below now show ("Betrag nicht aufteilbar" assumed a single amount; 08.10.2026). The notes, "joint_note" and
    # "joint_note_one", are at the end of the file, in the 'strictly necessary' pass.
    "joint_n": {
        "de": "{n} Firmen",
        "fr": "{n} entreprises",
        "it": "{n} aziende",
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


# Fix round 3 (item 36): French elides 'de', 'le' and 'que' before a vowel, also before a name the template inserts:
# 'Adjudications de Abteilung Tiefbau (CSV)' (234 pages), 'd’un seul projet de Office…' (23). The template's
# 'de {name}' becomes 'd’{name}' when the value starts so; a figure ('de 12 projets') or a consonant keeps it.
# Fix round 4: before an h only where it is mute ('d’Hôpital du Valais'): an aspirated or a foreign one keeps 'de'
# ('d’Haute école', 'd’Hochbauamt', 'd’HOLINGER' were wrong). _MUTE_H: the starts of the mute-h words names begin with.
_ELIDE = __import__("re").compile(r"(?<![\w’'])(de|De|le|Le|que|Que) \{(\w+)\}")
_ELIDE_START = "aeiouyàâäéèêëîïôöûüœæAEIOUYÀÂÄÉÈÊËÎÏÔÖÛÜŒÆ"
_MUTE_H = ("hôpita", "hôtel", "hospi", "habita", "hygièn", "héberg", "horlog")


def elides(v: str) -> bool:
    """French elides before v: a vowel, or a mute h (_MUTE_H)."""
    return bool(v) and (v[0] in _ELIDE_START or v.lower().startswith(_MUTE_H))


def elide(tpl: str, lang: str, kw: dict) -> str:
    """tpl with every 'de {x}' / 'le {x}' / 'que {x}' elided where kw's x starts with a vowel or a mute h (French only)."""
    if lang != "fr" or not kw:
        return tpl

    def one(m):
        v = str(kw.get(m.group(2), ""))
        if not elides(v):
            return m.group(0)
        w = m.group(1)
        return (w[:2] if w.lower() == "que" else w[0]) + "’{" + m.group(2) + "}"
    return _ELIDE.sub(one, tpl)


# Fix round 3 (item 41): a name that ends in a full stop before the template's own ('Coopérative T.B.R.C..') keeps one
_DOTS = __import__("re").compile(r"(?<!\.)\.\.(?!\.)")


def i(key: str, lang: str, **kw) -> str:
    if not kw:
        return IDX[key][lang]
    s = _DOTS.sub(".", elide(IDX[key][lang], lang, kw).format(**kw))
    return it_dates(s) if lang == "it" else s


# The API's own enum values, as a reader should see them. Printing "open" and "True"
# to a German reader is not a register, it is a database dump.
ENUM: dict[str, dict[str, dict[str, str]]] = {
    "processType": {
        "open": {"de": "Offenes Verfahren", "fr": "Procédure ouverte",
                 "it": "Procedura di pubblico concorso", "en": "Open procedure"},
        "selective": {"de": "Selektives Verfahren", "fr": "Procédure sélective",
                      "it": "Procedura selettiva", "en": "Selective procedure"},
        "invitation": {"de": "Einladungsverfahren", "fr": "Procédure sur invitation",
                       "it": "Procedura mediante invito", "en": "Invitation procedure"},
        "direct": {"de": "Freihändiges Verfahren", "fr": "Procédure de gré à gré",
                   "it": "Procedura per incarico diretto", "en": "Direct award"},
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
    "de": "Hier sehen Sie die {n} Ausschreibungen, deren Frist zuerst abläuft – von {total} offenen. Die "
          "übrigen finden Sie auf den Kantonsseiten.",
    "fr": "Voici les {n} appels d’offres dont le délai expire en premier, sur {total} en cours. Les autres "
          "sont sur les pages des cantons.",
    "it": "Qui vedi i {n} bandi che scadono prima, su {total} aperti. Gli altri sono nelle pagine dei "
          "cantoni.",
    "en": "Here are the {n} tenders that close first, out of {total} open. The others are on the canton "
          "pages.",
}


# «Aziende che hanno vinto più appalti» / «Firmen mit den meisten Aufträgen» (owner, 22.10.2026)
IDX["firms_cap"] = {
    "de": "Firmen mit den meisten Aufträgen", "fr": "Entreprises qui ont remporté le plus de marchés",
    "it": "Aziende che hanno vinto più appalti", "en": "Companies that won the most contracts",
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
             "Alle Inhalte beruhen auf amtlichen Publikationen der Plattform simap.ch. Wir geben sie nach "
             "den API-Nutzungsbedingungen von simap.ch inhaltlich unverändert wieder. Massgebend sind "
             "ausschliesslich die dort veröffentlichten Daten."),
            ("Keine Gewähr",
             "Wir übernehmen keine Gewähr für die Vollständigkeit und Richtigkeit der Aufbereitung. "
             "Hinweise auf Fehler nehmen wir gern per E-Mail entgegen."),
        ],
    },
    "fr": {
        "title": "Mentions légales",
        "operator_h": "Exploitant",
        "operator_note": "Particulier, Suisse",
        "contact_h": "Contact",
        "paras": [
            ("Projet indépendant",
             "« Marchés publics suisses » est un projet privé et indépendant. Ce n’est pas un registre "
             "officiel, et le projet n’a aucun lien avec simap.ch ni avec aucune autorité fédérale, "
             "cantonale ou communale."),
            ("Source des données",
             "Toutes les informations reposent sur les publications officielles de la plateforme simap.ch. "
             "Nous les reproduisons sans en modifier le contenu, conformément aux conditions d’utilisation "
             "de l’API de simap.ch. Seules les données publiées sur simap.ch font foi."),
            ("Absence de garantie",
             "Nous ne garantissons ni l’exhaustivité ni l’exactitude de cette présentation. Vous pouvez "
             "nous signaler les erreurs par e-mail."),
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
             "Tutti i contenuti si basano sulle pubblicazioni ufficiali della piattaforma simap.ch. Li "
             "riproduciamo senza modificarne il contenuto, nel rispetto delle condizioni d’uso dell’API di "
             "simap.ch. Fanno fede solo i dati pubblicati su simap.ch."),
            ("Nessuna garanzia",
             "Non garantiamo né la completezza né l’esattezza della rielaborazione. Se trovi un errore, "
             "segnalacelo via e-mail."),
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
             "All content is based on the official publications of the simap.ch platform. We reproduce it "
             "without changing its content, in accordance with simap.ch’s API terms of use. Only the data "
             "published on simap.ch is authoritative."),
            ("No guarantee",
             "We give no guarantee that this presentation is complete or correct. Please report any errors "
             "by email."),
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
             "Diese Website gibt amtliche Publikationen von simap.ch wieder. Die meisten genannten "
             "Anbieterinnen und Anbieter sind Unternehmen. Einige, die einen Zuschlag erhalten, sind jedoch "
             "Einzelfirmen oder Selbständigerwerbende: Dann erscheint der Name einer natürlichen Person zusammen "
             "mit dem Auftrag, dem Betrag und dem Auftraggeber. Kontaktpersonen, E-Mail-Adressen und "
             "Telefonnummern erfassen wir nicht gesondert. Stehen solche Angaben im Text einer Ausschreibung, "
             "übernehmen wir sie unverändert von simap.ch."),
            ("Zweck und Rechtfertigung",
             "Der Zweck ist, bereits amtlich veröffentlichte Vergabeentscheide auffindbar und vergleichbar zu "
             "machen. Behörden von Bund, Kantonen und Gemeinden haben diese Daten nach dem öffentlichen "
             "Beschaffungsrecht publiziert; sie sind allgemein zugänglich. Wir geben sie nach den "
             "API-Nutzungsbedingungen von simap.ch inhaltlich unverändert wieder. Die Bearbeitung stützt sich "
             "auf das überwiegende Interesse an der Transparenz öffentlicher Beschaffungen."),
            ("Daten über Besucherinnen und Besucher",
             "Diese Website setzt keine Cookies, nutzt keine Analyse- oder Tracking-Dienste und bindet keine "
             "Skripte oder Schriften von Dritten ein. Es gibt keine Benutzerkonten. Das einzige Formular ist "
             "die freiwillige Anmeldung für «Ausschreibungen per E-Mail» (siehe unten). Die Website wird über "
             "GitHub Pages ausgeliefert. Der Hosting-Anbieter kann im Betrieb technische Verbindungsdaten wie "
             "IP-Adressen in eigenen Server-Logs erfassen."),
            ("Ausschreibungen per E-Mail und RSS-Feeds",
             "Wer neue Ausschreibungen per E-Mail erhalten möchte, abonniert sie über das Formular auf der "
             "Seite «Ausschreibungen per E-Mail». Das Abo wird erst aktiv, wenn Sie auf den Bestätigungslink in "
             "der E-Mail klicken, die wir Ihnen schicken (Double-Opt-in). Wir bearbeiten Ihre E-Mail-Adresse, "
             "die gewählten Kantone und Branchen, die Sprache, Zeitpunkt und IP-Adresse der Bestätigung sowie "
             "während höchstens 45 Tagen die Liste der bereits zugestellten Ausschreibungen, damit keine "
             "Ausschreibung doppelt verschickt wird. Alle diese Daten bearbeiten wir ausschliesslich für den "
             "Versand der Abo-E-Mails; Grundlage ist Ihre eigene Anmeldung. Die E-Mails enthalten ein "
             "Zählpixel und Links, die über einen Server von Brevo laufen; Brevo kann so Öffnungen und Klicks "
             "erfassen. Das können Sie verhindern, indem Sie das automatische Laden von Bildern ausschalten und "
             "die Ausschreibungen direkt auf auftragsregister.ch aufrufen. Abmelden können Sie sich jederzeit "
             "über den Link in jeder E-Mail oder per E-Mail mit dem Betreff «Stop». Danach entfernen wir Sie "
             "innert 30 Tagen aus der Verteilerliste und löschen die Liste der zugestellten Ausschreibungen. "
             "Bei Brevo bleiben Ihr Kontakteintrag (unter anderem E-Mail-Adresse und Zeitpunkt von Anmeldung "
             "und Bestätigung), der Vermerk der Abmeldung und die Versandprotokolle der bereits zugestellten "
             "E-Mails bestehen, damit Sie sicher keine weiteren E-Mails erhalten. Wir verkaufen die Daten "
             "nicht, geben sie nicht an Dritte zu deren eigenen Zwecken weiter und verwenden sie nicht für "
             "andere Zwecke. In unserem Auftrag bearbeiten sie: Brevo (Sendinblue SAS, Paris, EU) für Anmeldung "
             "und Versand sowie, für E-Mails an abo@auftragsregister.ch (auch Fehlermeldungen), ImprovMX Inc. "
             "(USA), das sie weiterleitet, und Google LLC, bei dem das Postfach liegt (Gmail). Die RSS-Feeds "
             "erfordern keine Anmeldung und übermitteln uns keine Personendaten."),
            ("Archiv und Aufbewahrung",
             "Wir aktualisieren den Datenbestand in der Regel werktags mit den Daten von simap.ch. Ältere "
             "Publikationen bleiben im Archiv erhalten, auch wenn man sie über die Schnittstelle von simap.ch "
             "nicht mehr abfragen kann."),
            ("Ihre Rechte",
             "Sie können jederzeit Auskunft über die Daten verlangen, die wir zu Ihrer Person bearbeiten. Sie "
             "können auch verlangen, dass wir sie berichtigen oder löschen, und der Bearbeitung widersprechen. Eine "
             "kurze E-Mail an die oben genannte Adresse genügt; wir bearbeiten Ihr Anliegen ohne Kosten für "
             "Sie. Massgebend bleibt die Publikation auf simap.ch: Eine Berichtigung dort sollten Sie "
             "zusätzlich bei der Behörde verlangen, die sie publiziert hat."),
        ],
    },
    "fr": {
        "title": "Protection des données",
        "operator_h": "Responsable du traitement",
        "operator_note": "Particulier, Suisse",
        "contact_h": "Contact",
        "paras": [
            ("Quelles données personnelles figurent sur ce site ?",
             "Ce site reproduit des publications officielles de simap.ch. La plupart des adjudicataires sont "
             "des entreprises. Certains sont toutefois des raisons individuelles ou des indépendants : dans ces "
             "cas, le nom d'une personne physique apparaît avec le marché, le montant et l'acheteur public. "
             "Nous ne collectons pas séparément les personnes de contact, les adresses e-mail ni les numéros "
             "de téléphone. Si le texte d'un appel d'offres en contient, nous les reprenons tels quels de "
             "simap.ch."),
            ("Finalité et justification",
             "La finalité est de rendre repérables et comparables des décisions d'adjudication déjà publiées "
             "officiellement. Des autorités fédérales, cantonales et communales ont publié ces données dans le "
             "cadre du droit des marchés publics ; elles sont accessibles au public. Nous les reproduisons sans "
             "modification de contenu, conformément aux conditions d'utilisation de l'API de simap.ch. Le "
             "traitement repose sur l'intérêt prépondérant à la transparence des marchés publics."),
            ("Données sur les visiteurs",
             "Ce site ne dépose aucun cookie, n’utilise aucun service d’analyse ou de suivi et n’intègre aucun "
             "script ni aucune police de caractères de tiers. Il n’y a pas de compte utilisateur. Le seul "
             "formulaire est l’inscription facultative à « Appels d’offres par e-mail » (voir ci-dessous). Le "
             "site est diffusé via GitHub Pages ; l’hébergeur peut enregistrer dans ses propres journaux des "
             "données techniques de connexion, comme les adresses IP."),
            ("Appels d’offres par e-mail et flux RSS",
             "Pour recevoir les nouveaux appels d'offres par e-mail, il suffit de remplir le formulaire de la "
             "page « Appels d’offres par e-mail ». L'inscription n'est active qu'après un clic sur le lien de "
             "confirmation que nous vous envoyons par e-mail (double opt-in). Nous traitons votre adresse "
             "e-mail, les cantons et secteurs choisis, la langue, la date et l'adresse IP de la confirmation "
             "ainsi que, pendant 45 jours au plus, la liste des appels d'offres déjà envoyés, afin qu’aucun ne "
             "soit envoyé deux fois. Nous utilisons ces données uniquement pour l'envoi de ces e-mails, sur la "
             "base de votre propre inscription. Les e-mails contiennent un pixel de suivi et des liens qui "
             "passent par un serveur de Brevo ; Brevo peut ainsi enregistrer les ouvertures et les clics. Vous "
             "pouvez l'empêcher en désactivant le chargement automatique des images et en consultant les appels "
             "d'offres directement sur auftragsregister.ch. Vous pouvez vous désabonner à tout moment par le "
             "lien présent dans chaque e-mail ou par un e-mail avec l'objet « Stop ». Nous vous retirons alors "
             "de la liste de diffusion dans les 30 jours et effaçons la liste des appels d'offres envoyés. "
             "Brevo conserve votre fiche de contact (notamment l'adresse e-mail et la date de l'inscription et "
             "de la confirmation), la mention de votre désabonnement et les journaux des e-mails déjà envoyés, "
             "afin que vous ne receviez plus aucun e-mail. Nous ne vendons pas les données, ne les cédons pas à "
             "des tiers pour leurs propres fins et ne les utilisons pas à d'autres fins. Elles sont traitées "
             "pour notre compte par Brevo (Sendinblue SAS, Paris, UE) pour l’inscription et l’envoi et, pour "
             "les e-mails adressés à abo@auftragsregister.ch (y compris les signalements d’erreur), par "
             "ImprovMX Inc. (États-Unis), qui les redirige, et par Google LLC, qui héberge la boîte aux lettres "
             "(Gmail). Les flux RSS ne demandent aucune inscription et ne nous transmettent aucune donnée "
             "personnelle."),
            ("Archive et conservation",
             "Nous mettons les données à jour depuis simap.ch, en règle générale les jours ouvrables. Les "
             "publications plus anciennes restent dans les archives, même lorsqu'on ne peut plus les interroger "
             "via l'interface de simap.ch."),
            ("Vos droits",
             "Vous pouvez en tout temps demander l'accès aux données vous concernant, leur rectification ou "
             "leur effacement, et vous opposer au traitement. Un simple e-mail à l'adresse ci-dessus suffit ; "
             "nous traitons les demandes sans frais. Seule la publication sur simap.ch fait foi : pour la faire "
             "rectifier, vous devriez aussi vous adresser à l’autorité qui l’a publiée."),
        ],
    },
    # Italian: «tu», as on the rest of the site (natural-voice pass, owner, 23.10.2026); the meaning unchanged
    "it": {
        "title": "Protezione dei dati",
        "operator_h": "Titolare del trattamento",
        "operator_note": "Privato, Svizzera",
        "contact_h": "Contatto",
        "paras": [
            ("Quali dati personali contiene questo sito?",
             "Questo sito riproduce pubblicazioni ufficiali di simap.ch. La maggior parte dei vincitori sono "
             "imprese. Alcuni però sono ditte individuali o lavoratori indipendenti: in questi casi compare il "
             "nome di una persona fisica, insieme all'appalto, all'importo e all'ente pubblico. Non raccogliamo "
             "a parte persone di contatto, indirizzi e-mail e numeri di telefono. Se il testo di un bando li "
             "contiene, li riprendiamo invariati da simap.ch."),
            ("Scopo e giustificazione",
             "Lo scopo è rendere reperibili e confrontabili decisioni di aggiudicazione già pubblicate "
             "ufficialmente. Sono dati pubblicati da autorità federali, cantonali e comunali in base al diritto "
             "degli appalti pubblici e accessibili a tutti. Li riproduciamo senza modificarne il "
             "contenuto, nel rispetto delle condizioni d’uso dell’API di simap.ch. Il trattamento si fonda "
             "sull'interesse preponderante alla trasparenza degli appalti pubblici."),
            ("Dati di chi visita il sito",
             "Questo sito non usa cookie, né servizi di analisi o di tracciamento, e non incorpora script o "
             "font di terzi. Non ci sono account utente. L'unico modulo è l'iscrizione facoltativa a «Bandi via "
             "e-mail» (vedi sotto). Il sito è distribuito tramite GitHub Pages: il fornitore di hosting può "
             "registrare nei suoi log dati tecnici di connessione, come gli indirizzi IP."),
            ("Bandi via e-mail e feed RSS",
             "Per ricevere i nuovi bandi via e-mail ti iscrivi con il modulo della pagina «Bandi via e-mail». "
             "L’iscrizione diventa attiva solo dopo il clic sul link di conferma che ti mandiamo via e-mail "
             "(double opt-in). Trattiamo il tuo indirizzo e-mail, i cantoni e i settori che scegli, la lingua, "
             "la data, l’ora e l’indirizzo IP della conferma e, per 45 giorni al massimo, l’elenco dei bandi "
             "già inviati, così nessun bando ti arriva due volte. Usiamo tutti questi dati solo per inviarti "
             "queste e-mail, sulla base della tua iscrizione. Le e-mail contengono un pixel di tracciamento e "
             "link che passano da un server di Brevo: Brevo può così registrare aperture e clic. Puoi evitarlo "
             "disattivando il caricamento automatico delle immagini e aprendo i bandi direttamente su "
             "auftragsregister.ch. Puoi annullare l’iscrizione in qualsiasi momento con il link presente in "
             "ogni e-mail o mandando un’e-mail con oggetto «Stop». Entro 30 giorni ti togliamo dalla lista "
             "d’invio e cancelliamo l’elenco dei bandi inviati. Presso Brevo restano la tua scheda di contatto "
             "(tra l’altro l’indirizzo e-mail, la data e l’ora dell’iscrizione e della conferma), l’annotazione "
             "della disiscrizione e i registri delle e-mail già inviate, perché tu non riceva più nessuna "
             "e-mail. Non vendiamo i dati, non li cediamo a terzi per i loro scopi e non li usiamo per altri "
             "scopi. Trattano i dati per nostro conto: Brevo (Sendinblue SAS, Parigi, UE), per iscrizione e invio; "
             "ImprovMX Inc. (USA), che inoltra le e-mail inviate ad abo@auftragsregister.ch (anche le segnalazioni "
             "di errori); Google LLC, che ospita la casella di posta (Gmail). I feed RSS "
             "non richiedono iscrizione e non ci trasmettono dati personali."),
            ("Archivio e conservazione",
             "Riprendiamo i dati da simap.ch, di norma nei giorni feriali. Le pubblicazioni più vecchie restano "
             "nell’archivio, anche quando non si possono più consultare tramite l'interfaccia di simap.ch."),
            ("I tuoi diritti",
             "Puoi chiedere in ogni momento l'accesso ai dati che ti riguardano, la loro rettifica o la loro "
             "cancellazione, e puoi opporti al trattamento. Basta una breve e-mail all'indirizzo indicato "
             "sopra; trattiamo le richieste senza spese. Fa fede la pubblicazione su simap.ch: una rettifica "
             "dovresti chiederla anche all’autorità che l’ha pubblicata."),
        ],
    },
    "en": {
        "title": "Privacy",
        "operator_h": "Controller",
        "operator_note": "Private individual, Switzerland",
        "contact_h": "Contact",
        "paras": [
            ("What personal data does this site contain?",
             "This site reproduces official publications from simap.ch. Most contract winners are companies. "
             "Some, however, are sole proprietorships or self-employed individuals: in those cases the name of "
             "a natural person appears together with the contract, the amount and the public buyer. We do not "
             "collect contact persons, email addresses or telephone numbers separately. Where the text of a "
             "tender contains them, we reproduce them unchanged from simap.ch."),
            ("Purpose and justification",
             "The purpose is to make award decisions that have already been officially published findable and "
             "comparable. Federal, cantonal and communal authorities published this data under "
             "public-procurement law, and it is publicly accessible. We reproduce it without changes to its "
             "content, under the simap.ch API terms of use. The processing rests on the overriding interest in "
             "the transparency of public procurement."),
            ("Data about visitors",
             "This site sets no cookies, uses no analytics or tracking services, and embeds no third-party "
             "scripts or fonts. There are no user accounts. The only form is the optional subscription to "
             "Tenders by email (see below). The site is served through GitHub Pages; the hosting provider may "
             "record technical connection data such as IP addresses in its own server logs."),
            ("Tenders by email and RSS feeds",
             "To receive new tenders by email, subscribe with the form on the Tenders by email page. Your "
             "subscription only becomes active once you click the confirmation link we email you (double "
             "opt-in). We process your email address, the cantons and sectors you choose, your language, the "
             "time and IP address of your confirmation and, for no more than 45 days, the list of tenders "
             "already sent to you, so that none is sent twice. We use all of this solely to send these emails, "
             "on the basis of your own subscription. The emails contain a tracking pixel and links that pass "
             "through a Brevo server, so Brevo may record opens and clicks. You can prevent this by turning off "
             "automatic image loading and opening the tenders directly on auftragsregister.ch. You can "
             "unsubscribe at any time via the link in every email or by sending an email with the subject "
             "“Stop”. We then remove you from the mailing list within 30 days and delete the list of tenders "
             "sent. Brevo keeps your contact record (including your email address and the time of subscription "
             "and confirmation), a record that you unsubscribed and the logs of the emails already sent, to "
             "make sure you receive no further emails. We do not sell the data, pass it on to third parties for "
             "their own use, or use it for any other purpose. It is processed on our behalf by Brevo "
             "(Sendinblue SAS, Paris, EU) for subscriptions and sending and, for emails sent to "
             "abo@auftragsregister.ch (error reports included), by ImprovMX Inc. (USA), which forwards them, "
             "and Google LLC, which hosts the mailbox (Gmail). The RSS feeds require no registration and send "
             "us no personal data."),
            ("Archive and retention",
             "We refresh the data from simap.ch, usually Monday to Saturday. Older publications stay in the "
             "archive, even once they can no longer be queried through the simap.ch interface."),
            ("Your rights",
             "You may at any time request access to the data concerning you, ask for it to be corrected or "
             "deleted, and object to the processing. A short email to the address above is enough; we handle "
             "requests free of charge. The publication on simap.ch remains authoritative: you should also ask "
             "the authority that published it for a correction."),
        ],
    },
}


T["sector"] = {"de": "Kategorie", "fr": "Catégorie", "it": "Categoria", "en": "Category"}
T["year"] = {"de": "Jahr", "fr": "Année", "it": "Anno", "en": "Year"}
T["running_canton"] = {"de": "Offene Ausschreibungen · Kanton", "fr": "Appels d’offres en cours · Canton",
                       "it": "Bandi aperti · Cantone", "en": "Open tenders · Canton"}


T["abbr"] = {"de": "Kürzel", "fr": "Abréviation", "it": "Sigla", "en": "Code"}
T["in_register"] = {"de": "in diesem Register", "fr": "dans ce registre",
                    "it": "in questo registro", "en": "in this register"}
T["reason"]["fr"] = "Motifs du choix"
T["reason"]["it"] = "Motivazione della scelta"
T["treaty"]["fr"] = "Soumis aux accords internationaux"
T["treaty"]["it"] = "Soggetto ai trattati internazionali"
T["treaty"]["en"] = "Covered by international treaties"
META["buyers_count_one"] = {"de": "einem einzigen Auftraggeber", "fr": "un seul acheteur public",
                            "it": "un solo ente pubblico", "en": "a single public buyer"}

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
# The box says what comes by e-mail; its button is the short call, «Gratis abonnieren» / «S’abonner
# gratuitement» / «Iscriviti gratis» / «Subscribe free» (owner, 22.10.2026)
# Natural-voice pass (owner, 23.10.2026): the service speaks («Ti mandiamo …», «Wir schicken Ihnen …»).
META["alert_both"] = {
    "de": "Wir schicken Ihnen neue Ausschreibungen der Branche «{sector}» {where} per E-Mail.",
    "fr": "Nous vous envoyons par e-mail les nouveaux appels d’offres du secteur « {sector} » {where}.",
    "it": "Ti mandiamo via e-mail i nuovi bandi del settore «{sector}» {where}.",
    "en": "We email you new tenders in the “{sector}” sector {where}.",
}
META["alert_sector"] = {
    "de": "Wir schicken Ihnen neue Ausschreibungen der Branche «{sector}» aus der ganzen Schweiz per E-Mail.",
    "fr": "Nous vous envoyons par e-mail les nouveaux appels d’offres du secteur « {sector} » de toute la Suisse.",
    "it": "Ti mandiamo via e-mail i nuovi bandi del settore «{sector}» in tutta la Svizzera.",
    "en": "We email you new tenders in the “{sector}” sector from all over Switzerland.",
}
META["alert_canton"] = {
    "de": "Wir schicken Ihnen neue öffentliche Ausschreibungen {where} per E-Mail.",
    "fr": "Nous vous envoyons par e-mail les nouveaux appels d’offres publics {where}.",
    "it": "Ti mandiamo via e-mail i nuovi bandi pubblici {where}.",
    "en": "We email you new public tenders {where}.",
}
META["alert_none"] = {
    "de": "Wir schicken Ihnen neue öffentliche Ausschreibungen per E-Mail.",
    "fr": "Nous vous envoyons par e-mail les nouveaux appels d’offres publics.",
    "it": "Ti mandiamo via e-mail i nuovi bandi pubblici.",
    "en": "We email you new public tenders.",
}
META["alert_link"] = {"de": "Gratis abonnieren", "fr": "S’abonner gratuitement",
                      "it": "Iscriviti gratis", "en": "Subscribe free"}
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
        "45": "Travaux de construction", "48": "Logiciels et systèmes d’information", "50": "Réparation et entretien",
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
        "63": "Servizi ausiliari ai trasporti, agenzie di viaggio", "64": "Poste e telecomunicazioni", "65": "Distribuzione di energia e acqua",
        "66": "Finanza e assicurazioni", "70": "Servizi immobiliari", "71": "Architettura e ingegneria",
        "72": "Servizi informatici", "73": "Ricerca e sviluppo", "75": "Amministrazione pubblica e previdenza sociale",
        "76": "Servizi per petrolio e gas", "77": "Agricoltura, selvicoltura, giardinaggio", "79": "Servizi alle imprese",
        "80": "Istruzione e formazione", "85": "Sanità e assistenza sociale", "90": "Acque reflue, rifiuti, pulizia, ambiente",
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
        "63": "Transport support services, travel agencies", "64": "Post and telecommunications", "65": "Energy and water supply",
        "66": "Finance and insurance", "70": "Real estate services", "71": "Architecture and engineering",
        "72": "IT services", "73": "Research and development", "75": "Public administration and social security",
        "76": "Oil and gas services", "77": "Agriculture, forestry, gardening", "79": "Business services",
        "80": "Education and training", "85": "Health and social work", "90": "Sewage, waste, cleaning, environment",
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
COMPANY = {"de": ("Firma", "Firmen"), "fr": ("entreprise", "entreprises"),
           "it": ("azienda", "aziende"), "en": ("company", "companies")}
# "an 1 Firma" / "en faveur de 1 entreprise" read like a form letter
COMPANY_ONE = {"de": "eine einzige Firma", "fr": "une seule entreprise",
               "it": "un’unica azienda", "en": "a single company"}
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
T["activity"] = {"de": "Kategorie", "fr": "Catégorie", "it": "Categoria",
                 "en": "Category"}
PROSE["matched_tenders_one"] = {
    "de": "Offene Ausschreibung in einer verwandten Kategorie",
    "fr": "Appel d’offres en cours dans une catégorie proche",
    "it": "Bando aperto in una categoria simile",
    "en": "Open tender in a related category",
}
# Meta descriptions without their closing clause, used when the full one would be cut
# ("… – mit Auftraggebern, Beträgen und…", "… », publiées sur…"; verifier 28.09.2026)
META["company_desc_short"] = {
    "de": "{name} hat {n} gewonnen{span}{val} – laut simap.ch.",
    "fr": "{name} a remporté {n}{span}{val}, selon simap.ch.",
    "it": "{name} ha vinto {n}{span}{val}, secondo simap.ch.",
    "en": "{name} has won {n}{span}{val}, according to simap.ch.",
}
META["buyer_desc_short"] = {
    "de": "{name} hat {n} an {f} vergeben.",
    "fr": "{name} a attribué {n} à {f}.",
    "it": "{name} ha aggiudicato {n} a {f}.",
    "en": "{name} has awarded {n} to {f}.",
}
META["sector_desc_short"] = {
    "de": "In der Kategorie «{label}» gingen {n} an {f}.",
    "fr": "Dans la catégorie « {label} », {n} ont été attribués à {f}.",
    "it": "Nella categoria «{label}» {n} sono andati a {f}.",
    "en": "In the “{label}” category, {n} went to {f}.",
}
META["canton_desc_short"] = {
    "de": "Im Kanton {name} gingen {n} an {f}, laut simap.ch.",
    "fr": "Dans le canton {of}, {n} ont été attribués à {f}, selon simap.ch.",
    "it": "Nel Canton {name} {n} sono andati a {f}, secondo simap.ch.",
    "en": "In the canton of {name}, {n} went to {f}, according to simap.ch.",
}
# one open tender: "classés par délai" / "nach Eingabefrist geordnet" said nothing about one
# item, and the French plural participle disagreed with "1 appel d’offres"
META["open_sector_desc_one"] = {
    "de": "{n} in der Branche «{name}» aus der ganzen Schweiz (CPV {code}), Quelle: simap.ch.",
    "fr": "{n} en Suisse dans le secteur « {name} » (CPV {code}), source : simap.ch.",
    "it": "{n} nel settore «{name}» in tutta la Svizzera (CPV {code}), fonte: simap.ch.",
    "en": "{n} across Switzerland in the “{name}” sector (CPV {code}); source: simap.ch.",
}
META["open_canton_desc_one"] = {
    "de": "{n} im Kanton {name}, werktags aktualisiert (Quelle: simap.ch).",
    "fr": "{n} dans le canton {of}, mis à jour les jours ouvrables (source : simap.ch).",
    "it": "{n} nel Canton {name}, aggiornato nei giorni feriali (fonte: simap.ch).",
    "en": "{n} in the canton of {name}, updated Monday to Saturday (source: simap.ch).",
}
# the note on buyer pages, counted: 72 of 128 German pages had exactly one such award
META["buyer_joint_note_one"] = {
    "de": "Ein Auftrag ging an mehrere Firmen.",
    "fr": "Un marché a été attribué à plusieurs entreprises.",
    "it": "Un appalto è andato a più aziende.",
    "en": "One contract went to several companies.",
}
META["open_sector_desc_short"] = {
    "de": "{n} in der Branche «{name}» (CPV {code}) aus der ganzen Schweiz.",
    "fr": "{n} en Suisse dans le secteur « {name} » (CPV {code}), par ordre d’échéance.",
    "it": "{n} nel settore «{name}» (CPV {code}) in tutta la Svizzera, in ordine di scadenza.",
    "en": "{n} across Switzerland in the “{name}” sector (CPV {code}), sorted by deadline.",
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
    "fr": "Code général du secteur « {label} »",
    "it": "Codice generico del settore «{label}»",
    "en": "General code of the “{label}” sector",
}
# A project's page lists every lot awarded, one line per lot ('Lose'), and each line is what a
# company or buyer row links to (#lot-2): the page used to show one lot, the last one read
# (6965: lot 15 of 15; 08.10.2026)
T["lots"] = {"de": "Lose", "fr": "Lots", "it": "Lotti", "en": "Lots"}
T["lot"] = {"de": "Los", "fr": "Lot", "it": "Lotto", "en": "Lot"}
T["lot_name"] = {"de": "Bezeichnung", "fr": "Intitulé", "it": "Titolo", "en": "Title"}
T["project_number"] = {"de": "Projektnummer", "fr": "N° de projet", "it": "N. di progetto",
                       "en": "Project no."}
# the texts that differ from lot to lot, each under the lots it belongs to
IDX["lot_n"] = {"de": "Los\u00a0{n}", "fr": "Lot\u00a0{n}", "it": "Lotto\u00a0{n}", "en": "Lot\u00a0{n}"}
IDX["lots_list"] = {"de": "Lose\u00a0{n}", "fr": "Lots\u00a0{n}", "it": "Lotti\u00a0{n}", "en": "Lots\u00a0{n}"}
META["desc_lots"] = {
    "de": ", {n} Lose vergeben",
    "fr": ", {n} lots attribués",
    "it": ", {n} lotti aggiudicati",
    "en": ", {n} lots awarded",
}
# a project without lots whose later award names other firms (4 on 08.10.2026)
META["desc_awards_n"] = {
    "de": ", {n} Aufträge vergeben",
    "fr": ", {n} marchés attribués",
    "it": ", {n} appalti aggiudicati",
    "en": ", {n} contracts awarded",
}
# An award to several firms has no amount of its own: simap publishes a price beside each name,
# the price of that firm's successful offer, and the page printed the first firm's as the
# 'Zuschlagsbetrag' (15349-02: 313'744.35 of five BKP packages worth 5.87 Mio.). Narrowed
# (owner, 08.10.2026): each firm with its own price, no figure for the award, and on a company
# page the firm's own price marked as its offer — not a "share", which it is not: in a
# framework the same ceiling stands beside every name.
T["offer_price"] = {"de": "Angebotspreis", "fr": "Prix de l'offre", "it": "Prezzo dell'offerta",
                    "en": "Offer price"}
T["per_firm"] = {"de": "Preise je Firma", "fr": "prix par entreprise", "it": "prezzi per azienda",
                 "en": "prices per company"}
IDX["own_offer"] = {
    "de": "Angebotspreis · vergeben an {n} Firmen",
    "fr": "prix de l'offre · attribué à {n} entreprises",
    "it": "prezzo dell'offerta · aggiudicato a {n} aziende",
    "en": "offer price · awarded to {n} companies",
}
IDX["same_price"] = {
    "de": "Die Publikation nennt für alle {n} Firmen denselben Preis.",
    "fr": "La publication indique le même prix pour les {n} entreprises.",
    "it": "La pubblicazione indica lo stesso prezzo per tutte e {n} le aziende.",
    "en": "The publication gives the same price for all {n} companies.",
}
# two firms, the most common case: 'für alle 2 Unternehmen' reads wrong (verifier, 08.10.2026)
IDX["same_price_two"] = {
    "de": "Die Publikation nennt für beide Firmen denselben Preis.",
    "fr": "La publication indique le même prix pour les deux entreprises.",
    "it": "La pubblicazione indica lo stesso prezzo per entrambe le aziende.",
    "en": "The publication gives the same price for both companies.",
}
META["desc_won_n"] = {
    "de": ", vergeben an {n} Firmen",
    "fr": ", attribué à {n} entreprises",
    "it": ", aggiudicato a {n} aziende",
    "en": ", awarded to {n} companies",
}
# under the CHF total of the home, a canton or a buyer, which leaves those awards out like the
# company pages always did (the home counted 5.1 Mrd. of first firms' prices; 08.10.2026)
IDX["sum_no_joint"] = {
    "de": "ohne die {k} Aufträge an mehrere Firmen",
    "fr": "sans les {k} marchés attribués à plusieurs entreprises",
    "it": "senza i {k} appalti andati a più aziende",
    "en": "excluding the {k} contracts awarded to several companies",
}
IDX["sum_no_joint_one"] = {
    "de": "ohne den Auftrag an mehrere Firmen",
    "fr": "sans le marché attribué à plusieurs entreprises",
    "it": "senza l’appalto andato a più aziende",
    "en": "excluding the contract awarded to several companies",
}
# A tender keeps its page for a while after its deadline: the links in alert e-mails and feeds
# led to a missing page the day after (08.10.2026). The status says so, with the date and time.
T["tender_expired"] = {"de": "Eingabefrist abgelaufen", "fr": "Délai de remise expiré",
                       "it": "Termine scaduto", "en": "Deadline passed"}
# {when}: formato.deadline(); Italian without an article before the date ("il 08.10.2026" needs
# "l’8"), as in mc_note_end
META["expired_lead"] = {
    "de": "Die Eingabefrist ist abgelaufen ({when}). Wenn der Auftrag vergeben und auf simap.ch publiziert "
          "wird, sehen Sie hier, wer ihn erhält.",
    "fr": "Le délai de remise des offres a expiré ({when}). Si le marché est attribué et publié sur "
          "simap.ch, vous verrez ici qui l’a remporté.",
    "it": "La scadenza è passata ({when}). Se l’appalto viene aggiudicato e pubblicato su simap.ch, qui "
          "vedrai chi l’ha vinto.",
    "en": "The submission deadline has passed ({when}). If the contract is awarded and published on "
          "simap.ch, you’ll see here who won it.",
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
# (META["abo_form_nojs"]: without JavaScript the pills are not copied into KANTON/BRANCHE, which stay
# ALLE; its words are in fix round 1 below)
# The page GitHub Pages serves for any missing URL (docs/404.html), all four languages on one page.
# {days}: genera.EXPIRED_DAYS
META["nf_title"] = {"de": "Seite nicht gefunden", "fr": "Page introuvable",
                    "it": "Pagina non trovata", "en": "Page not found"}
# (its text, "nf_text", is at the end of the file, in the 'strictly necessary' pass)
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
# 'Branchen' in German as the owner named it. Plain-language pass (owner, 22.10.2026): the e-mail service
# «Ausschreibungen per E-Mail» / «Appels d’offres par e-mail» / «Bandi via e-mail» / «Tenders by email»,
# Firmen / Aziende, Acheteurs publics / Enti pubblici / Public buyers, Secteurs / Settori / Sectors
# (nav_sectors below), and the about page «So funktioniert’s» / «Comment ça marche» / «Come funziona» /
# «How it works».
T["nav_tenders"] = {"de": "Ausschreibungen", "fr": "Appels d’offres", "it": "Bandi", "en": "Tenders"}
T["nav_alert"] = {"de": "Ausschreibungen per E-Mail", "fr": "Appels d’offres par e-mail", "it": "Bandi via e-mail",
                  "en": "Tenders by email"}
T["nav_companies"] = {"de": "Firmen", "fr": "Entreprises", "it": "Aziende", "en": "Companies"}
T["nav_buyers"] = {"de": "Auftraggeber", "fr": "Acheteurs publics", "it": "Enti pubblici",
                   "en": "Public buyers"}
T["nav_cantons"] = {"de": "Kantone", "fr": "Cantons", "it": "Cantoni", "en": "Cantons"}
T["nav_about"] = {"de": "So funktioniert’s", "fr": "Comment ça marche", "it": "Come funziona", "en": "How it works"}
T["nav_label"] = {"de": "Hauptnavigation", "fr": "Navigation principale", "it": "Navigazione principale",
                  "en": "Main navigation"}
T["home"] = {"de": "Startseite", "fr": "Accueil", "it": "Home", "en": "Home"}
T["crumbs_label"] = {"de": "Sie sind hier", "fr": "Fil d’Ariane", "it": "Percorso di navigazione",
                     "en": "Breadcrumb"}
T["skip"] = {"de": "Zum Inhalt springen", "fr": "Aller au contenu", "it": "Al contenuto principale",
             "en": "Skip to main content"}
# the footer's data line: the date is the newest publication (DATA_DATE). Pages whose content does
# not change from one day to the next carry it through /stand.js, so they stay byte-identical
# overnight (git, IndexNow and the sitemap's lastmod read every changed page as news).
# «aggiornato al 22.10.2026» (owner, 22.10.2026); it_dates() elides 'al 08.' to 'all’08.' (and genera does it
# for the footer's <time> and for /stand.js)
META["stand"] = {"de": "Aktualisiert am {d}", "fr": "Mis à jour le {d}",
                 "it": "Aggiornato al {d}", "en": "Updated {d}"}
# the footer's link beside the date: where it leads, in plain words («Methodik» was the office's)
META["methodik"] = {"de": "Woher die Daten kommen", "fr": "D’où viennent les données", "it": "Da dove vengono i dati",
                    "en": "Where the data comes from"}

# The home's two doors: open tenders (with the ones first published on the day of the build) and
# the company index. {m}: tenders whose first publication (-01) is dated the build day.
META["door_new"] = {"de": "{m} neue am {d}", "fr": "{m} nouveaux le {d}",
                    "it": "{m} nuovi il {d}", "en": "{m} new on {d}"}
META["door_new_one"] = {"de": "1 neue am {d}", "fr": "1 nouveau le {d}",
                        "it": "1 nuovo il {d}", "en": "1 new on {d}"}
# (the open tenders' door line, "door_open_sub", is at the end of the file, in the 'strictly necessary' pass)
META["door_companies_h"] = {"de": "Firma finden", "fr": "Trouver une entreprise",
                            "it": "Trova un’azienda", "en": "Find a company"}
META["door_companies_sub"] = {
    "de": "{n} Firmen mit mindestens zwei Aufträgen – von A bis Z.",
    "fr": "{n} entreprises ayant remporté au moins deux marchés, de A à Z.",
    "it": "{n} aziende con almeno due appalti vinti, dalla A alla Z.",
    "en": "{n} companies with at least two contracts, from A to Z.",
}
# the home's lower half counts awards: the headings say so (the chips read like open tenders)
IDX["by_canton_awards"] = {"de": "Vergebene Aufträge nach Kanton", "fr": "Marchés attribués par canton",
                           "it": "Appalti aggiudicati per cantone", "en": "Contracts awarded by canton"}
IDX["by_sector_awards"] = {"de": "Vergebene Aufträge nach Kategorie", "fr": "Marchés attribués par catégorie",
                           "it": "Appalti aggiudicati per categoria", "en": "Contracts awarded by category"}

# The hub's table gets a heading of its own (it had none, under the canton list)
META["open_table_h2"] = {"de": "Offene Ausschreibungen nach Frist",
                         "fr": "Appels d’offres en cours par délai",
                         "it": "Bandi aperti per scadenza", "en": "Open tenders by deadline"}
# a canton or industry without an open tender keeps its page and its feed, and offers the alert
META["empty_canton"] = {
    "de": "Zurzeit ist im Kanton {name} keine Ausschreibung offen.",
    "fr": "Il n’y a pas d’appel d’offres en cours dans le canton {of} pour le moment.",
    "it": "Al momento nel Canton {name} non ci sono bandi aperti.",
    "en": "There are no open tenders in the canton of {name} at the moment.",
}
META["empty_sector"] = {
    "de": "Zurzeit ist in der Branche «{name}» keine Ausschreibung offen.",
    "fr": "Il n’y a pas d’appel d’offres en cours dans le secteur « {name} » pour le moment.",
    "it": "Al momento nel settore «{name}» non ci sono bandi aperti.",
    "en": "There are no open tenders in the “{name}” sector at the moment.",
}
META["empty_buyer"] = {
    "de": "Zurzeit hat dieser Auftraggeber keine offene Ausschreibung.",
    "fr": "Cet acheteur public n’a pas d’appel d’offres en cours pour le moment.",
    "it": "Al momento questo ente pubblico non ha bandi aperti.",
    "en": "This public buyer has no open tenders at the moment.",
}
# a tender page past its deadline: the hook above the alert
META["alert_missed"] = {
    "de": "Frist verpasst? Wir schicken Ihnen die nächsten Ausschreibungen dieser Art gratis per E-Mail.",
    "fr": "Vous avez manqué le délai ? Nous vous envoyons gratuitement par e-mail les prochains appels "
          "d’offres de ce type.",
    "it": "Hai perso la scadenza? Ti mandiamo gratis via e-mail i prossimi bandi come questo.",
    "en": "Missed the deadline? We’ll email you the next tenders like this – free.",
}
# the open tenders of the division a sector page belongs to
IDX["open_in_sector"] = {
    "de": "Offene Ausschreibungen der Branche «{name}»: {k}",
    "fr": "Appels d’offres en cours dans le secteur « {name} » : {k}",
    "it": "Bandi aperti nel settore «{name}»: {k}",
    "en": "Open tenders in the “{name}” sector: {k}",
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
                              "fr": "Autres appels d’offres en cours du même acheteur public",
                              "it": "Altri bandi aperti dello stesso ente pubblico",
                              "en": "Other open tenders from this public buyer"}
IDX["tender_buyer_awards_h"] = {"de": "Bisher vergebene Aufträge dieses Auftraggebers",
                                "fr": "Marchés déjà attribués par cet acheteur public",
                                "it": "Appalti già aggiudicati dallo stesso ente pubblico",
                                "en": "Contracts already awarded by this public buyer"}
IDX["tender_buyer_awards_all"] = {"de": "Alle {n} dieses Auftraggebers",
                                  "fr": "Les {n} de cet acheteur public",
                                  "it": "Tutti i {n} dell’ente pubblico",
                                  "en": "All {n} by this public buyer"}
IDX["buyer_open_all"] = {"de": "Alle {n} offenen Ausschreibungen dieses Auftraggebers",
                         "fr": "Les {n} appels d’offres en cours de cet acheteur public",
                         "it": "Tutti i {n} bandi aperti dell’ente pubblico",
                         "en": "All {n} open tenders from this public buyer"}
# a long list of open tenders on a buyer page: the first ones, the rest behind a disclosure
IDX["show_more"] = {"de": "{n} weitere anzeigen", "fr": "Afficher les {n} autres", "it": "Mostra gli altri {n}",
                    "en": "Show {n} more"}
IDX["similar_h"] = {"de": "Ähnliche vergebene Aufträge", "fr": "Marchés similaires déjà attribués",
                    "it": "Appalti simili già aggiudicati", "en": "Similar contracts awarded"}
# (the note under it, "similar_note", is at the end of the file, in the 'strictly necessary' pass)
# CSV downloads (canton, buyer and company pages): one file per page, its awards newest first
IDX["csv_link"] = {"de": "Daten als CSV", "fr": "Données en CSV", "it": "Dati in CSV", "en": "Data as CSV"}
IDX["csv_meta"] = {"de": "{n} Zeilen, {size}", "fr": "{n} lignes, {size}", "it": "{n} righe, {size}",
                   "en": "{n} rows, {size}"}
# file names: the URL keeps one German name per language like every other path segment; the
# download attribute names the saved file in the reader's language (plain words since 22.10.2026)
CSV_STEM = {"de": "auftraege", "fr": "marches", "it": "appalti", "en": "contracts"}
ICS_STEM = {"de": "eingabefrist", "fr": "delai", "it": "scadenza", "en": "deadline"}
# visually hidden table captions
IDX["cap_company_awards"] = {"de": "Aufträge an {name}, neueste zuerst",
                             "fr": "Marchés remportés par {name}, les plus récents d’abord",
                             "it": "Appalti vinti da {name}, dal più recente",
                             "en": "Contracts won by {name}, newest first"}

# The about and methodology page (/xx/ueber/). Facts only, each checked against the generator:
# MIN_AWARDS, buyer_map(floor=3), sector_pages(floor=3), EXPIRED_DAYS, load() (abandonments,
# corrections, deadlines), chf_total(), firm_prices(), the 08:00 release in simap's API terms
# (aggiorna.embargo_ok) and the commit times of the nightly (mostly 08:40-09:00, 14.10.2026).
# Blocks: a string is a paragraph, a list a bulleted list. Placeholders are filled by genera.
UEBER: dict[str, dict] = {
    "de": {
        "title": "So funktioniert’s",
        "h1": "So funktioniert’s",
        "lead": "Woher die Daten kommen, wie wir sie ordnen und was sie nicht zeigen. Dazu die wichtigsten Begriffe, "
                "kurz erklärt.",
        "sections": [
            ("register", "Was dieses Register ist", [
                "Öffentliche Aufträge Schweiz sammelt die vergebenen Aufträge und die Ausschreibungen, die Bund, "
                "Kantone und Gemeinden auf simap.ch publizieren, und ordnet sie nach Firmen, Auftraggebern, "
                "Kantonen und Branchen. So sehen Sie, wer welche öffentlichen Aufträge gewonnen hat – eine Frage, "
                "die simap.ch selbst nicht beantwortet.",
                "Das Register ist ein privates, unabhängiges Projekt. Es ist keine amtliche Veröffentlichung "
                "und steht in keiner Verbindung zu simap.ch oder zu einer Behörde. Massgebend sind "
                "ausschliesslich die Publikationen auf simap.ch; jede Seite eines Auftrags und jede "
                "Ausschreibung verlinkt die amtliche Publikation.",
            ]),
            # the official words the site keeps where they say something precise, each explained once
            # (plain-language pass, owner, 22.10.2026)
            ("begriffe", "Die wichtigsten Begriffe", [[
                "Ausschreibung: Ein Auftraggeber sucht Angebote für einen Auftrag. Bis zur Eingabefrist können "
                "Firmen ein Angebot einreichen.",
                "Eingabefrist: Bis zu diesem Datum, oft mit Uhrzeit, muss das Angebot eingereicht sein. "
                "Massgebend sind die Angaben auf simap.ch und in den Unterlagen.",
                "Zuschlag: der Entscheid, welche Firma den Auftrag erhält. Wir sprechen hier von «vergebenen "
                "Aufträgen».",
                "Auftraggeber: wer den Auftrag vergibt – Bund, Kanton, Gemeinde oder eine öffentliche "
                "Einrichtung, etwa ein Spital oder ein Unternehmen der öffentlichen Hand.",
                "Verfahren: wie ein Auftrag vergeben wird. Offenes Verfahren: Jede Firma kann ein Angebot "
                "einreichen. Selektives Verfahren: Zuerst bewerben sich die Firmen, dann reichen die "
                "ausgewählten ein Angebot ein. Einladungsverfahren: Der Auftraggeber lädt ausgewählte Firmen "
                "direkt ein, ein Angebot einzureichen. Freihändiges Verfahren: Der Auftraggeber vergibt den "
                "Auftrag direkt, ohne Ausschreibung.",
                "Los: ein Teil eines grösseren Auftrags, der einzeln vergeben wird – oft an verschiedene "
                "Firmen.",
                "CPV-Code: die EU-weit einheitliche Nummer für die Art der Leistung. Die ersten zwei Ziffern "
                "ergeben die Branche (z. B. 45, Bauarbeiten), der ganze achtstellige Code die Kategorie "
                "(z. B. 45233000).",
                "Art des Auftrags: Bauauftrag (Bauarbeiten), Lieferauftrag (Waren) oder "
                "Dienstleistungsauftrag (Dienstleistungen).",
                "Staatsvertragsbereich: Der Auftrag fällt unter internationale Abkommen über das öffentliche "
                "Beschaffungswesen, etwa jenes der WTO.",
                "Angebotspreis: der Preis, den eine Firma in ihrem Angebot genannt hat. Bei einem Auftrag an "
                "mehrere Firmen nennt simap.ch einen Preis je Firma.",
                "Hinweis von simap.ch: Den Satz «Dies ist keine amtliche Veröffentlichung …» in der Fusszeile "
                "schreibt simap.ch vor. Deshalb steht er auf jeder Seite wörtlich und auf Deutsch.",
            ]]),
            ("quelle", "Quelle und Nutzungsbedingungen", [
                "Alle Daten stammen aus der Programmierschnittstelle (API) von simap.ch, der amtlichen "
                "Plattform für öffentliche Aufträge in der Schweiz. Ihre Nutzungsbedingungen erlauben die "
                "Weiterverwendung, auch gewerblich, wenn die Daten inhaltlich unverändert bleiben, getrennt von "
                "eigenen Auswertungen stehen und den vorgeschriebenen Hinweis tragen. Dieser Hinweis steht in "
                "der Fusszeile jeder Seite; unsere eigenen Auswertungen sind als solche gekennzeichnet.",
                "Titel und Beschreibungen erscheinen so, wie sie publiziert wurden, in der Sprache der "
                "Publikation. Wir übersetzen sie nicht und formulieren sie nicht um.",
                "Lizenz: Das Register vergibt an den Daten keine eigene Lizenz. Für ihre Weiterverwendung "
                "gelten die Nutzungsbedingungen von simap.ch ({terms}). Auf diese Bedingungen verweist auch "
                "die Lizenzangabe in den strukturierten Daten dieser Seite (schema.org/Dataset).",
            ]),
            ("aktualisierung", "Wann wir die Daten aktualisieren", [
                "simap.ch gibt die Publikationen eines Tages ab 8 Uhr zur Weiterverbreitung frei. Wir holen sie "
                "in der Regel an jedem Werktag danach ab. Meist ist das Register am Vormittag aktuell, an "
                "einzelnen Tagen später oder erst am Folgetag. Jedes Mal holen wir die vergebenen Aufträge des "
                "laufenden und des vorangehenden Monats – dort treffen auch nachträgliche Berichtigungen ein – "
                "sowie die Ausschreibungen der letzten 75 Tage.",
                "Das Datum in der Fusszeile jeder Seite («{stand}») ist das Datum der neuesten Publikation im "
                "Register. Aktualisiert am {date}: {awards} vergebene Aufträge und {open} offene Ausschreibungen.",
            ]),
            ("abdeckung", "Was erfasst ist", [
                "Das Archiv beginnt im {start}.{ramp}{incomplete}",
                "Erfasst sind die vergebenen Aufträge, die simap.ch nach einem offenen Verfahren, einem "
                "selektiven Verfahren oder einem Einladungsverfahren publiziert, sowie die Ausschreibungen mit "
                "noch offener Eingabefrist. Freihändig vergebene Aufträge, die simap.ch in einzelnen Fällen "
                "ebenfalls publiziert, sind nicht enthalten. Aufträge, die nicht auf simap.ch publiziert werden "
                "– etwa kleinere Aufträge, die ohne Ausschreibung direkt vergeben werden dürfen –, fehlen hier "
                "wie dort.",
            ]),
            ("kantone", "Wie wir Aufträge den Kantonen zuordnen", [
                "Massgebend ist der Kanton, den die Publikation als Ort der Leistung angibt, also die Adresse des "
                "Auftrags – dieselbe Angabe, nach der simap.ch selbst filtert. Bei einem Projekt mit Losen gilt "
                "der Kanton jedes Loses: Eine Ausschreibung mit Losen in mehreren Kantonen steht in der Liste "
                "jedes dieser Kantone, mit dem Vermerk «{multi}». Ein vergebener Auftrag zählt nur im Kanton "
                "seines Loses, damit keine Summe ihn doppelt zählt.",
                "Nennt die Publikation weder für den Auftrag noch für die Lose einen Ort, nehmen wir den Kanton "
                "des Auftraggebers und markieren ihn mit «{fallback}». So erscheinen etwa Arbeiten an "
                "Nationalstrassen im Thurgau oder in St. Gallen, die die ASTRA-Filiale Winterthur ohne Ort "
                "ausschreibt, unter Zürich. Andere Auftraggeber geben ihre eigene Adresse als Ort der Leistung "
                "an. Dann steht der Kanton ihres Sitzes, auch wenn die Arbeiten anderswo stattfinden – das lässt "
                "sich aus den Daten nicht erkennen.",
                "{nocant} Alle Kantone zusammen und diese Aufträge ergeben die Gesamtzahl auf der Startseite. "
                "«Ausschreibungen per E-Mail» ordnet gleich zu: Für Ihre Auswahl zählt jeder Kanton einer "
                "Ausschreibung.",
            ]),
            ("zusammenfuehrung", "Wie wir Firmen und Auftraggeber zusammenfassen", [
                "Der Name einer Firma ist in den Publikationen nicht immer gleich geschrieben. Schreibweisen, "
                "die sich nur in Gross- und Kleinschreibung, Umlauten, Akzenten oder Satzzeichen unterscheiden "
                "(«CSD INGENIEURE AG» und «CSD Ingenieure AG», «Bolliger & Co. AG» und «Bolliger + Co. AG»), "
                "behandeln wir als dieselbe Firma und zeigen die häufigste Schreibweise. Unterschiedlich "
                "benannte Einheiten, etwa Zweigniederlassungen, bleiben getrennt. Mit dem Handelsregister "
                "gleichen wir die Namen nicht ab.",
                "Eine eigene Seite erhält eine Firma ab {min_c} Aufträgen, ein Auftraggeber ab {min_b} und eine "
                "Kategorie (CPV-Code) ab {min_s}. Auch Auftraggeber fassen wir über ihren Namen zusammen, "
                "unabhängig von Leerzeichen, Bindestrichen, Anführungszeichen und Klammern.",
                "Ein Auftrag an mehrere Firmen erscheint auf der Seite jeder genannten Firma.",
            ]),
            ("betraege", "Beträge, Lose und Summen", [
                "Wir geben Beträge so wieder, wie sie publiziert wurden. Die Seite eines Auftrags nennt den "
                "genauen Betrag. Listen zeigen einen gerundeten Betrag; den genauen sehen Sie, wenn Sie mit der "
                "Maus darüberfahren, und Screenreader lesen ihn vor.",
                "Summen enthalten nur Aufträge in Franken an eine einzige Firma. Bei einem Auftrag an mehrere "
                "Firmen nennt die Publikation einen Preis je Firma. Diese Preise zeigen wir einzeln, aber wir "
                "addieren sie nicht und schreiben sie keinem Gesamtauftrag zu – bei Rahmenverträgen steht oft "
                "bei jeder Firma dieselbe Obergrenze. Beträge in Euro oder anderen Währungen erscheinen mit "
                "ihrer Währung, nie in einer Spalte in Franken, und zählen in keiner Summe.",
                "Ein Betrag unter 1’000 CHF ist bei einem vergebenen Auftrag fast nie dessen Wert, sondern ein "
                "Einheitspreis (etwa pro Stunde, Stück oder Kilometer). Wir markieren ihn mit «{rate}» und "
                "zählen ihn in keiner Summe und keinem Median. Dasselbe gilt für einen Betrag bis 5’000 CHF, "
                "wenn die Publikation auf Personalverleih oder einen Tages- oder Stundensatz hinweist («LSE», "
                "«Personalverleih», «Tagessatz», «Regie» und Ähnliches).",
                "simap.ch publiziert bei einem Projekt mit Losen jedes Los einzeln. Die Seite des Projekts "
                "listet alle Lose. Nennt simap für mehrere Lose derselben Firma denselben Projektpreis, zählt "
                "er in Summen nur einmal.",
            ]),
            ("ausgeschlossen", "Was nicht enthalten ist", [[
                "Abgebrochene Verfahren: simap.ch publiziert sie im selben Datenstrom wie die vergebenen "
                "Aufträge; hier erscheinen sie nicht als vergebene Aufträge.",
                "Berichtigungen: Wird eine Ausschreibung oder ein vergebener Auftrag berichtigt, gilt die "
                "zuletzt publizierte Fassung. Frühere Fassungen zeigen wir nicht zusätzlich.",
                "Abgelaufene Ausschreibungen: Nach Ablauf der Eingabefrist bleibt die Seite einer Ausschreibung "
                "noch {days} Tage online, mit dem Vermerk «{expired}». Wird der Auftrag vorher vergeben und "
                "publiziert, sehen Sie unter derselben Adresse, wer ihn erhält. Erfasst sind die "
                "Ausschreibungen seit dem {since}.",
                "Ausschreibungen ohne lesbare Eingabefrist führen wir nicht als offen auf.",
            ]]),
            ("cpv", "Branchen und Kategorien (CPV)", [
                "Die Einteilung folgt dem CPV, dem EU-weit einheitlichen Vokabular für öffentliche Aufträge. "
                "Eine Branche entspricht den ersten zwei Ziffern des Codes (z. B. 45, Bauarbeiten), eine "
                "Kategorie dem genauen achtstelligen Code (z. B. 45233000). Die Bezeichnungen der Kategorien "
                "stammen aus der amtlichen Fassung des CPV in der jeweiligen Sprache, auf Deutsch in Schweizer "
                "Schreibweise (ss). Die Namen der 45 Branchen sind eigene Kurzformen des Registers.",
                "«{matched}» auf den Firmenseiten und «{similar}» auf den Ausschreibungsseiten beruhen "
                "auf den gemeinsamen Ziffern der CPV-Codes: Ein allgemeiner Code wie 45000000 (Bauarbeiten) "
                "allein genügt nicht. Für Firmen müssen mindestens die ersten vier Ziffern (ohne Füllnullen) "
                "übereinstimmen. Ähnliche vergebene Aufträge stammen aus derselben Branche und demselben "
                "Kanton, die mit dem ähnlichsten Code zuerst.",
            ]),
            ("daten", "Daten herunterladen und abonnieren", [[
                "CSV: {csv_pages} bieten ihre vergebenen Aufträge als CSV-Datei an – UTF-8 mit BOM, Semikolon "
                "als Trennzeichen, Beträge mit Punkt als Dezimalzeichen. Eine Datei gilt für alle vier "
                "Sprachversionen, mit englischen Spaltennamen ({cols}) und den Titeln in der Sprache der "
                "Publikation. Bei Aufträgen an mehrere Firmen bleibt die Spalte «Amount» leer. Zellen, die mit "
                "=, +, - oder @ beginnen, erhalten einen vorangestellten Apostroph, damit Tabellenprogramme sie "
                "nicht als Formel ausführen. «Canton source» nennt die Herkunft des Kantons (place: Ort der "
                "Leistung, lot: Los, buyer: Sitz des Auftraggebers), «Amount note» markiert vermutliche "
                "Einheitspreise (probable unit rate).",
                "Grafiken: Jede Grafik nennt ihre Quelle und verlinkt ihre Daten als CSV-Datei.",
                "Kalender: Jede offene Ausschreibung bietet ihre Eingabefrist als Kalenderdatei (.ics) an.",
                "RSS und E-Mail: Für jeden Kanton und jede Branche gibt es einen RSS-Feed. Mit «Ausschreibungen "
                "per E-Mail» schicken wir Ihnen neue Ausschreibungen nach Kanton und Branche, gratis und ohne "
                "Konto.",
            ]]),
            ("kontakt", "Kontakt und Fehlermeldungen", [
                "Fehler, Fragen und Hinweise schicken Sie an {mail}. Auf jeder Seite eines Auftrags und jeder "
                "Ausschreibung öffnet «{report}» eine E-Mail mit der Publikationsnummer im Betreff. Das Register "
                "wird von einer Privatperson in der Schweiz betrieben; die Angaben zum Betreiber stehen im "
                "Impressum.",
            ]),
        ],
        "csv_pages": "Die Kantons-, Auftraggeber- und Firmenseiten",
        "csv_pages_nocomp": "Die Kantons- und Auftraggeberseiten",
        "ramp": " Von {a} bis {b} ist nur ein Teil der vergebenen Aufträge erfasst; in den Monatsgrafiken sind "
                "diese Monate schraffiert. Ab {full} enthält das Register die vergebenen Aufträge, die die "
                "Schnittstelle von simap.ch beim Abruf für den jeweiligen Monat geliefert hat. Mit amtlichen "
                "Gesamtzahlen gleichen wir sie nicht ab.",
        "incomplete": " Bei {n} Publikationen vergebener Aufträge ({months}) fehlten in den Daten der Schnittstelle "
                      "der Titel und die Firma, die den Auftrag erhielt. Sie sind in keiner Zahl und keiner Liste "
                      "enthalten.",
        "nocant": "{n} nennen weder einen Ort noch einen Auftraggeber mit Kanton. Sie zählen zu keinem Kanton; "
                  "die Kantonsübersicht führt sie gesondert auf.",
        "nocant_zero": "Zurzeit hat jeder vergebene Auftrag einen Kanton.",
        "alert_link": "Gratis abonnieren",
    },
    "fr": {
        "title": "Comment ça marche",
        "h1": "Comment ça marche",
        "lead": "D’où viennent les données, comment nous les classons et ce qu’elles ne montrent pas. Avec les "
                "principaux termes, expliqués en bref.",
        "sections": [
            ("register", "Ce qu’est ce registre", [
                "« Marchés publics suisses » rassemble les marchés attribués et les appels d’offres que la "
                "Confédération, les cantons et les communes publient sur simap.ch, et les classe par entreprise, "
                "par acheteur public, par canton et par secteur. Vous voyez ainsi qui a remporté quels marchés "
                "publics – une question à laquelle simap.ch ne répond pas lui-même.",
                "Le registre est un projet privé et indépendant. Ce n’est pas une publication officielle, et il "
                "n’a aucun lien avec simap.ch ni avec aucune autorité. Seules les publications de simap.ch font "
                "foi ; chaque page de marché attribué et d’appel d’offres renvoie à la publication officielle.",
            ]),
            ("begriffe", "Les termes principaux", [[
                "Appel d’offres : un acheteur public demande des offres pour un marché. Les entreprises peuvent "
                "remettre une offre jusqu’au délai de remise.",
                "Délai de remise des offres : la date, souvent avec l’heure, à laquelle l’offre doit être "
                "remise. Font foi les indications de simap.ch et des documents d’appel d’offres.",
                "Adjudication : la décision qui désigne l’entreprise qui obtient le marché. Ici, nous parlons "
                "de « marchés attribués ».",
                "Acheteur public (adjudicateur) : l’entité qui attribue le marché – Confédération, canton, "
                "commune ou établissement public, comme un hôpital ou une entreprise publique.",
                "Procédure : la manière dont le marché est attribué. Procédure ouverte : toute entreprise peut "
                "remettre une offre. Procédure sélective : les entreprises se portent d’abord candidates, puis "
                "celles qui sont retenues remettent une offre. Procédure sur invitation : l’acheteur public invite "
                "directement certaines entreprises à remettre une offre. Procédure de gré à gré : l’acheteur "
                "public attribue le marché directement, sans appel d’offres.",
                "Lot : une partie d’un marché plus important, attribuée séparément – souvent à des entreprises "
                "différentes.",
                "Code CPV : le code commun de l’UE pour le type de prestation. Les deux premiers chiffres donnent "
                "le secteur (p. ex. 45, travaux de construction), le code complet à huit chiffres la catégorie "
                "(p. ex. 45233000).",
                "Type de marché : marché de travaux, de fournitures ou de services.",
                "Soumis aux accords internationaux : le marché relève des accords internationaux sur les marchés "
                "publics, comme celui de l’OMC.",
                "Prix de l’offre : le prix indiqué par une entreprise dans son offre. Pour un marché attribué à "
                "plusieurs entreprises, simap.ch indique un prix par entreprise.",
                "Mention de simap.ch : la phrase « Dies ist keine amtliche Veröffentlichung … » au bas de chaque "
                "page est imposée par simap.ch. C’est pourquoi elle y figure telle quelle, en allemand.",
            ]]),
            ("quelle", "Source et conditions d’utilisation", [
                "Toutes les données proviennent de l’interface de programmation (API) de simap.ch, la "
                "plateforme officielle des marchés publics en Suisse. Ses conditions d’utilisation autorisent "
                "la réutilisation, y compris à des fins commerciales, si les données restent inchangées dans "
                "leur contenu, séparées de nos propres analyses et accompagnées de la mention prescrite. Cette "
                "mention figure au bas de chaque page ; nos propres analyses sont signalées comme telles.",
                "Les titres et les descriptions apparaissent tels qu’ils ont été publiés, dans la langue de "
                "la publication. Nous ne les traduisons pas et ne les reformulons pas.",
                "Licence : le registre n’accorde aucune licence propre sur les données. Leur réutilisation est "
                "régie par les conditions d’utilisation de simap.ch ({terms}). L’indication de licence dans les "
                "données structurées de cette page (schema.org/Dataset) renvoie aussi à ces conditions.",
            ]),
            ("aktualisierung", "Quand nous mettons les données à jour", [
                "simap.ch autorise la diffusion des publications du jour à partir de 8 h. Nous les récupérons en "
                "règle générale chaque jour ouvrable après cette heure. Le registre est le plus souvent à jour "
                "dans la matinée, certains jours plus tard ou le lendemain. Chaque mise à jour reprend les "
                "marchés attribués du mois en cours et du mois précédent – c’est là qu’arrivent aussi les "
                "rectifications – ainsi que les appels d’offres des 75 derniers jours.",
                "La date au bas de chaque page (« {stand} ») est celle de la publication la plus récente du "
                "registre. Mis à jour le {date} : {awards} marchés attribués et {open} appels d’offres en cours.",
            ]),
            ("abdeckung", "Ce que contient le registre", [
                "Les données commencent en {start}.{ramp}{incomplete}",
                "Le registre contient les marchés attribués que simap.ch publie à l’issue d’une procédure "
                "ouverte, sélective ou sur invitation, ainsi que les appels d’offres dont le délai de remise des "
                "offres court encore. Les marchés attribués de gré à gré, que simap.ch publie aussi dans certains "
                "cas, n’y figurent pas. Les marchés qui ne sont pas publiés sur simap.ch – par exemple les petits "
                "marchés qui peuvent être attribués directement, sans appel d’offres – ne figurent ni ici ni sur "
                "simap.ch.",
            ]),
            ("kantone", "Comment nous attribuons les marchés aux cantons", [
                "Ce qui compte, c’est le canton que la publication indique comme lieu d’exécution, c’est-à-dire "
                "l’adresse du marché – la même indication que celle sur laquelle simap.ch filtre lui-même. Pour "
                "un projet divisé en lots, c’est le canton de chaque lot qui compte : un appel d’offres dont les "
                "lots se situent dans plusieurs cantons figure dans la liste de chacun d’eux, avec la mention "
                "« {multi} ». Un marché attribué n’est compté que dans le canton de son lot, afin qu’aucun total "
                "ne le compte deux fois.",
                "Si la publication n’indique de lieu ni pour le marché ni pour les lots, nous prenons le canton "
                "de l’acheteur public, avec la mention « {fallback} ». Ainsi, des travaux sur les routes "
                "nationales en Thurgovie ou à Saint-Gall que la filiale de l’OFROU à Winterthour met en "
                "soumission sans lieu apparaissent sous Zurich. D’autres acheteurs publics indiquent leur propre "
                "adresse comme lieu d’exécution ; c’est alors le canton de leur siège qui figure, même si les "
                "travaux ont lieu ailleurs – les données ne permettent pas de le voir.",
                "{nocant} Tous les cantons et ces marchés donnent ensemble le total de la page d’accueil. "
                "« Appels d’offres par e-mail » attribue de la même manière : pour votre sélection, chaque "
                "canton d’un appel d’offres compte.",
            ]),
            ("zusammenfuehrung", "Comment nous regroupons les entreprises et les acheteurs publics", [
                "Une entreprise n’apparaît pas toujours sous la même graphie dans les publications. Les "
                "graphies qui ne diffèrent que par les majuscules, les trémas, les accents ou la ponctuation "
                "(« CSD INGENIEURE AG » et « CSD Ingenieure AG », « Bolliger & Co. AG » et « Bolliger + Co. "
                "AG ») comptent pour une seule entreprise, affichée sous sa graphie la plus fréquente. Les unités "
                "portant des noms différents, comme les succursales, restent distinctes. Nous ne faisons aucun "
                "rapprochement avec le registre du commerce.",
                "Une entreprise a sa propre page à partir de {min_c} marchés, un acheteur public à partir "
                "de {min_b} et une catégorie (code CPV) à partir de {min_s}. Les acheteurs publics sont eux aussi "
                "regroupés par leur nom, sans tenir compte des espaces, des traits d’union, des guillemets et "
                "des parenthèses.",
                "Un marché attribué à plusieurs entreprises figure sur la page de chacune d’elles.",
            ]),
            ("betraege", "Montants, lots et totaux", [
                "Nous reprenons les montants tels qu’ils ont été publiés. La page d’un marché indique le montant "
                "exact. Les listes affichent un montant arrondi ; le montant exact apparaît au survol de la "
                "souris et pour les lecteurs d’écran.",
                "Les totaux ne comprennent que les marchés en francs attribués à une seule entreprise. Pour un "
                "marché attribué à plusieurs entreprises, la publication indique un prix par entreprise : nous "
                "affichons ces prix séparément, mais nous ne les additionnons pas et ne les attribuons pas à un "
                "marché global – dans les contrats-cadres, le même plafond figure souvent à côté de chaque "
                "entreprise. Les montants en euros ou dans d’autres monnaies sont affichés avec leur devise, "
                "jamais dans une colonne en francs, et n’entrent dans aucun total.",
                "Un montant inférieur à 1 000 CHF n’est presque jamais la valeur d’un marché mais un prix "
                "unitaire (par heure, par pièce ou par kilomètre, par exemple). Nous le signalons par « {rate} » "
                "et il n’entre dans aucun total ni aucune médiane. Il en va de même d’un montant jusqu’à "
                "5 000 CHF lorsque la publication parle de location de services ou d’un tarif journalier ou "
                "horaire (« LSE », « location de services », « tarif journalier », etc.).",
                "Pour un projet divisé en lots, simap.ch publie chaque lot séparément. La page du projet liste "
                "tous les lots. Lorsque simap indique le même prix de projet pour plusieurs lots attribués à la "
                "même entreprise, ce prix n’est compté qu’une fois dans les totaux.",
            ]),
            ("ausgeschlossen", "Ce que le registre ne contient pas", [[
                "Procédures interrompues : simap.ch les publie dans le même flux que les marchés attribués ; "
                "elles ne sont pas présentées ici comme des marchés attribués.",
                "Rectifications : lorsqu’un appel d’offres ou un marché attribué est rectifié, seule la "
                "dernière version publiée compte. Nous n’affichons pas en plus les versions antérieures.",
                "Appels d’offres échus : après l’expiration du délai de remise des offres, la page d’un appel "
                "d’offres reste en ligne pendant {days} jours, avec la mention « {expired} ». Si le marché est "
                "attribué et publié entre-temps, vous voyez à la même adresse qui l’a remporté. Le registre "
                "recense les appels d’offres depuis le {since}.",
                "Les appels d’offres sans délai de remise lisible ne sont pas listés comme étant en cours.",
            ]]),
            ("cpv", "Secteurs et catégories (CPV)", [
                "La classification suit le CPV, le vocabulaire commun pour les marchés publics de l’UE. Un "
                "secteur correspond aux deux premiers chiffres du code (p. ex. 45, travaux de construction), "
                "une catégorie au code exact à huit chiffres (p. ex. 45233000). Les intitulés des catégories "
                "viennent de la version officielle du CPV dans chaque langue ; les noms des 45 secteurs sont "
                "des formes abrégées propres au registre.",
                "Les « {matched} » des pages d’entreprise et les « {similar} » des pages d’appel d’offres "
                "reposent sur les chiffres communs des codes CPV : un code général comme 45000000 (travaux "
                "de construction) ne suffit pas à lui seul. Pour les entreprises, au moins les quatre premiers "
                "chiffres significatifs doivent coïncider. Les marchés similaires appartiennent au même secteur "
                "et au même canton, les codes les plus proches d’abord.",
            ]),
            ("daten", "Télécharger et s’abonner", [[
                "CSV : {csv_pages} proposent leurs marchés attribués sous forme de fichier CSV – UTF-8 avec BOM, "
                "point-virgule comme séparateur, montants avec un point décimal. Un seul fichier sert aux quatre "
                "versions linguistiques, avec des noms de colonnes en anglais ({cols}) et les titres dans la "
                "langue de la publication. Pour les marchés attribués à plusieurs entreprises, la colonne "
                "« Amount » reste vide. Les cellules qui commencent par =, +, - ou @ sont précédées d’une "
                "apostrophe, pour que les tableurs ne les exécutent pas comme des formules. « Canton source » "
                "indique l’origine du canton (place : lieu d’exécution, lot : lot, buyer : siège de l’acheteur "
                "public), « Amount note » signale les prix probablement unitaires (probable unit rate).",
                "Graphiques : chaque graphique indique sa source et renvoie à ses données en CSV.",
                "Agenda : chaque appel d’offres en cours propose son délai de remise sous forme de fichier "
                "d’agenda (.ics).",
                "RSS et e-mail : chaque canton et chaque secteur a son flux RSS. Avec « Appels d’offres par "
                "e-mail », nous vous envoyons les nouveaux appels d’offres par canton et par secteur, "
                "gratuitement et sans compte.",
            ]]),
            ("kontakt", "Contact et signalement d’erreurs", [
                "Erreurs, questions et remarques : écrivez à {mail}. Sur chaque page de marché et d’appel "
                "d’offres, « {report} » ouvre un e-mail avec le numéro de publication en objet. Le registre "
                "est exploité par un particulier en Suisse ; les informations sur l’exploitant figurent dans "
                "les mentions légales.",
            ]),
        ],
        "csv_pages": "les pages des cantons, des acheteurs publics et des entreprises",
        "csv_pages_nocomp": "les pages des cantons et des acheteurs publics",
        "ramp": " Entre {a} et {b}, seule une partie des marchés attribués a été relevée ; ces mois sont "
                "hachurés dans les graphiques mensuels. À partir de {full}, le registre contient les marchés "
                "attribués que l’interface de simap.ch a fournis pour chaque mois lors de leur relevé. Nous ne "
                "les comparons pas à des totaux officiels.",
        "incomplete": " {n} publications de marchés attribués de {months} sont arrivées par l’interface sans titre "
                      "ni entreprise retenue : elles ne figurent dans aucun chiffre ni aucune liste.",
        "nocant": "{n} n’indiquent ni lieu ni acheteur public avec canton : ils ne comptent dans aucun "
                  "canton, et l’aperçu des cantons les présente à part.",
        "nocant_zero": "Actuellement, chaque marché attribué a un canton.",
        "alert_link": "S’abonner gratuitement",
    },
    "it": {
        "title": "Come funziona",
        "h1": "Come funziona",
        "lead": "Da dove vengono i dati, come li ordiniamo e cosa non mostrano. E i termini principali, spiegati in "
                "breve.",
        "sections": [
            ("register", "Che cos’è questo registro", [
                "Appalti pubblici svizzeri raccoglie gli appalti aggiudicati e i bandi che Confederazione, Cantoni "
                "e Comuni pubblicano su simap.ch. Li ordiniamo per azienda, ente pubblico, cantone e settore. "
                "Così puoi vedere chi ha vinto quali appalti pubblici: una domanda a cui simap.ch stesso non "
                "risponde.",
                "Il registro è un progetto privato e indipendente. Non è una pubblicazione ufficiale e non ha "
                "legami né con simap.ch né con alcuna autorità. Fanno fede solo le pubblicazioni su simap.ch: "
                "ogni pagina di appalto e di bando ha il link alla pubblicazione ufficiale.",
            ]),
            ("begriffe", "I termini principali", [[
                "Bando: un ente pubblico chiede offerte per un appalto. Le aziende possono presentare un’offerta "
                "fino alla scadenza.",
                "Scadenza (termine d’inoltro): la data, spesso con l’ora, entro cui va presentata l’offerta. Fanno "
                "fede le indicazioni su simap.ch e nei documenti del bando.",
                "Aggiudicazione: la decisione su quale azienda ottiene l’appalto. Qui parliamo di «appalti "
                "aggiudicati».",
                "Ente pubblico (committente): chi assegna l’appalto – Confederazione, Cantone, Comune o un ente "
                "o un’azienda pubblica, per esempio un ospedale.",
                "Procedura: come viene assegnato l’appalto. Procedura di pubblico concorso: ogni azienda può "
                "presentare un’offerta. Procedura selettiva: prima le aziende si candidano, poi quelle scelte "
                "presentano un’offerta. Procedura mediante invito: l’ente pubblico invita direttamente alcune "
                "aziende a presentare un’offerta. Procedura per incarico diretto: l’ente pubblico assegna "
                "l’appalto direttamente, senza bando.",
                "Lotto: una parte di un appalto più grande, aggiudicata separatamente – spesso ad aziende "
                "diverse.",
                "Codice CPV: il codice comune europeo per il tipo di prestazione. Le prime due cifre danno il "
                "settore (p. es. 45, lavori di costruzione), il codice completo di otto cifre la categoria "
                "(p. es. 45233000).",
                "Tipo di appalto: appalto di lavori, di forniture o di servizi.",
                "Soggetto ai trattati internazionali: l’appalto rientra negli accordi internazionali sugli "
                "appalti pubblici, come quello dell’OMC.",
                "Prezzo dell’offerta: il prezzo che un’azienda indica nella sua offerta. Per un appalto "
                "aggiudicato a più aziende, simap.ch indica un prezzo per azienda.",
                "Avvertenza di simap.ch: la frase «Dies ist keine amtliche Veröffentlichung …» in fondo a ogni "
                "pagina la richiede simap.ch. Per questo la riportiamo alla lettera, in tedesco.",
            ]]),
            ("quelle", "Fonte e condizioni d’uso", [
                "Tutti i dati vengono dall’interfaccia di programmazione (API) di simap.ch, la piattaforma "
                "ufficiale degli appalti pubblici in Svizzera. Le sue condizioni d’uso permettono di riutilizzarli, "
                "anche a fini commerciali, se i dati restano invariati nel contenuto, separati dalle nostre "
                "analisi e accompagnati dall’avvertenza prescritta. L’avvertenza è in fondo a ogni pagina; le "
                "nostre analisi sono indicate come tali.",
                "Titoli e descrizioni compaiono come sono stati pubblicati, nella lingua della pubblicazione. "
                "Non li traduciamo e non li riformuliamo.",
                "Licenza: non concediamo nessuna licenza propria sui dati. Il loro riutilizzo è regolato dalle "
                "condizioni d’uso di simap.ch ({terms}). A queste condizioni rimanda anche l’indicazione di "
                "licenza nei dati strutturati di questa pagina (schema.org/Dataset).",
            ]),
            ("aktualisierung", "Quando aggiorniamo i dati", [
                "simap.ch permette di diffondere le pubblicazioni del giorno dalle 8. Noi le riprendiamo di norma "
                "ogni giorno feriale, dopo quell’ora. Il registro è aggiornato di solito al mattino, certi giorni "
                "più tardi o il giorno dopo. A ogni aggiornamento riprendiamo gli appalti aggiudicati del mese "
                "corrente e di quello precedente – dove arrivano anche le rettifiche – e i bandi degli ultimi "
                "75 giorni.",
                "La data in fondo a ogni pagina («{stand}») è quella della pubblicazione più recente nel "
                "registro. Aggiornato al {date}: {awards} appalti aggiudicati e {open} bandi aperti.",
            ]),
            ("abdeckung", "Cosa contiene il registro", [
                "L’archivio parte da {start}.{ramp}{incomplete}",
                "Il registro contiene gli appalti aggiudicati che simap.ch pubblica dopo una procedura di "
                "pubblico concorso, una procedura selettiva o una procedura mediante invito, e i bandi con la "
                "scadenza ancora aperta. Non contiene gli appalti assegnati per incarico diretto, che simap.ch "
                "pubblica in alcuni casi. Gli appalti che non vengono pubblicati su simap.ch – per esempio i "
                "piccoli appalti che si possono assegnare direttamente, senza bando – mancano qui come su "
                "simap.ch.",
            ]),
            ("kantone", "Come attribuiamo gli appalti ai cantoni", [
                "Conta il cantone che la pubblicazione indica come luogo di esecuzione, cioè l’indirizzo "
                "dell’appalto: la stessa indicazione che simap.ch usa per filtrare. In un progetto diviso in "
                "lotti conta il cantone di ogni lotto. Un bando con lotti in più cantoni compare nell’elenco di "
                "ognuno, con la nota «{multi}». Un appalto aggiudicato invece conta solo nel cantone del suo "
                "lotto, così nessun totale lo conta due volte.",
                "Se la pubblicazione non indica un luogo né per l’appalto né per i lotti, usiamo il cantone "
                "dell’ente pubblico, con la nota «{fallback}». Per esempio, i lavori sulle strade nazionali in "
                "Turgovia o a San Gallo che la filiale USTRA di Winterthur mette a concorso senza indicare il "
                "luogo compaiono sotto Zurigo. Altri enti pubblici indicano come luogo di esecuzione il proprio "
                "indirizzo: allora compare il cantone della loro sede, anche se i lavori si svolgono altrove: "
                "dai dati non lo possiamo sapere.",
                "{nocant} Con questi, la somma dei cantoni dà il totale della home. «Bandi via e-mail» usa la "
                "stessa regola: per la tua scelta conta ogni cantone del bando.",
            ]),
            ("zusammenfuehrung", "Come raggruppiamo aziende ed enti pubblici", [
                "Nelle pubblicazioni il nome di un’azienda non è sempre scritto allo stesso modo. Se due grafie "
                "differiscono solo per maiuscole, dieresi, accenti o punteggiatura («CSD INGENIEURE AG» e "
                "«CSD Ingenieure AG», «Bolliger & Co. AG» e «Bolliger + Co. AG»), le trattiamo come la stessa "
                "azienda e mostriamo la grafia più frequente. Le unità con nomi diversi, per esempio le "
                "succursali, restano separate. Non facciamo confronti con il registro di commercio.",
                "Un’azienda ha una pagina sua da {min_c} appalti in su, un ente pubblico da {min_b} e una categoria "
                "(codice CPV) da {min_s}. Anche gli enti pubblici li raggruppiamo per nome, senza badare a spazi, "
                "trattini, virgolette e parentesi.",
                "Un appalto aggiudicato a più aziende compare sulla pagina di ognuna.",
            ]),
            ("betraege", "Importi, lotti e totali", [
                "Riportiamo gli importi come sono stati pubblicati. La pagina di un appalto mostra l’importo "
                "esatto. Gli elenchi mostrano un importo arrotondato: quello esatto lo vedi passando col mouse, "
                "e lo leggono anche i lettori di schermo.",
                "Nei totali contiamo solo gli appalti in franchi aggiudicati a una sola azienda. Per un appalto "
                "aggiudicato a più aziende la pubblicazione indica un prezzo per azienda: mostriamo questi prezzi "
                "uno per uno, ma non li sommiamo e non li attribuiamo a un appalto complessivo – nei contratti "
                "quadro accanto a ogni azienda compare spesso lo stesso tetto massimo. Gli importi in euro o in "
                "altre valute compaiono con la loro valuta, mai in una colonna in franchi, e non entrano in "
                "nessun totale.",
                "Un importo sotto i 1’000 CHF non è quasi mai il valore di un appalto, ma un prezzo unitario (per "
                "ora, per pezzo o per chilometro, per esempio). Lo segnaliamo con «{rate}» e non lo contiamo in "
                "nessun totale né in nessuna mediana. Lo stesso vale per un importo fino a 5’000 CHF, se la "
                "pubblicazione parla di prestito di personale o di una tariffa giornaliera od oraria («LSE», "
                "«tariffa giornaliera», «Regie» e simili).",
                "Per un progetto diviso in lotti, simap.ch pubblica ogni lotto separatamente. La pagina del "
                "progetto elenca tutti i lotti. Se simap indica lo stesso prezzo di progetto per più lotti della "
                "stessa azienda, nei totali lo contiamo una volta sola.",
            ]),
            ("ausgeschlossen", "Cosa non trovi qui", [[
                "Procedure interrotte: simap.ch le pubblica nello stesso flusso di dati degli appalti aggiudicati; "
                "qui non compaiono come appalti aggiudicati.",
                "Rettifiche: se un bando o un appalto aggiudicato viene rettificato, vale l’ultima versione "
                "pubblicata. Le versioni precedenti non le mostriamo.",
                "Bandi scaduti: dopo la scadenza la pagina di un bando resta online per {days} giorni, con la "
                "scritta «{expired}». Se nel frattempo l’appalto viene aggiudicato e pubblicato, allo stesso "
                "indirizzo vedi chi l’ha vinto. Raccogliamo i bandi dal {since}.",
                "I bandi senza una scadenza chiara non li elenchiamo tra quelli aperti.",
            ]]),
            ("cpv", "Settori e categorie (CPV)", [
                "La classificazione segue il CPV, il vocabolario comune europeo per gli appalti pubblici. "
                "Un settore corrisponde alle prime due cifre del codice (p. es. 45, lavori di costruzione), una "
                "categoria al codice esatto di otto cifre (p. es. 45233000). I nomi delle categorie vengono dalla "
                "versione ufficiale del CPV in ogni lingua; i nomi dei 45 settori sono forme brevi scelte da noi.",
                "I «{matched}» delle pagine delle aziende e gli «{similar}» delle pagine dei bandi si basano "
                "sulle cifre che i codici CPV hanno in comune: un codice generico come 45000000 (lavori di "
                "costruzione) da solo non basta. Per le aziende devono coincidere almeno le prime quattro cifre "
                "significative. Gli appalti simili sono dello stesso settore e dello stesso cantone, prima quelli "
                "con il codice più vicino.",
            ]),
            ("daten", "Scarica i dati e iscriviti", [[
                "CSV: {csv_pages} offrono i loro appalti aggiudicati come file CSV – UTF-8 con BOM, punto e "
                "virgola come separatore, importi con il punto come separatore decimale. C’è un solo file per le "
                "quattro lingue, con i nomi delle colonne in inglese ({cols}) e i titoli nella lingua della "
                "pubblicazione. Per gli appalti aggiudicati a più aziende la colonna «Amount» resta vuota. Le "
                "celle che iniziano con =, +, - o @ hanno davanti un apostrofo, così i fogli di calcolo non le "
                "eseguono come formule. «Canton source» dice da dove viene il cantone (place: luogo di "
                "esecuzione, lot: lotto, buyer: sede dell’ente pubblico), «Amount note» segnala i probabili "
                "prezzi unitari (probable unit rate).",
                "Grafici: ogni grafico indica la sua fonte e ha il link ai suoi dati in CSV.",
                "Calendario: per ogni bando aperto puoi scaricare la scadenza come file di calendario (.ics).",
                "RSS ed e-mail: ogni cantone e ogni settore ha il suo feed RSS. Con «Bandi via e-mail» ti "
                "mandiamo i nuovi bandi per cantone e settore, gratis e senza account.",
            ]]),
            ("kontakt", "Contatto e segnalazioni", [
                "Per errori, domande e segnalazioni scrivi ad {mail}. Su ogni pagina di appalto e di bando, "
                "«{report}» apre un’e-mail con il numero di pubblicazione nell’oggetto. Il registro è "
                "gestito da un privato in Svizzera; i dati del gestore si trovano nelle note legali.",
            ]),
        ],
        "csv_pages": "le pagine dei cantoni, degli enti pubblici e delle aziende",
        "csv_pages_nocomp": "le pagine dei cantoni e degli enti pubblici",
        "ramp": " Tra {a} e {b} abbiamo raccolto solo una parte degli appalti aggiudicati: nei grafici mensili "
                "questi mesi sono tratteggiati. Da {full} il registro contiene gli appalti aggiudicati che "
                "l’interfaccia di simap.ch ha fornito per ogni mese al momento della raccolta. Non li "
                "confrontiamo con i totali ufficiali.",
        "incomplete": " {n} pubblicazioni di appalti aggiudicati di {months} sono arrivate dall’interfaccia senza "
                      "titolo e senza azienda vincitrice: non compaiono in nessun numero e in nessun elenco.",
        "nocant": "{n} non indicano né un luogo né un ente pubblico con cantone: non contano in nessun cantone e "
                  "la pagina dei cantoni li elenca a parte.",
        "nocant_zero": "Al momento ogni appalto aggiudicato ha un cantone.",
        # the familiar imperative on buttons and controls (owner, 22.10.2026)
        "alert_link": "Iscriviti gratis",
    },
    "en": {
        "title": "How it works",
        "h1": "How it works",
        "lead": "Where the data comes from, how we arrange it and what it does not show – plus the key terms, "
                "explained briefly.",
        "sections": [
            ("register", "What this register is", [
                "Swiss Public Contracts collects the contracts awarded and the tenders that the Confederation, the "
                "cantons and the communes publish on simap.ch, and arranges them by company, public buyer, canton "
                "and sector. That way you can see who has won which public contracts – a question simap.ch "
                "itself does not answer.",
                "The register is a private, independent project. It is not an official publication and has "
                "no connection to simap.ch or to any authority. Only the publications on simap.ch are "
                "authoritative; every contract and tender page links to the official publication.",
            ]),
            ("begriffe", "Key terms", [[
                "Tender: a public buyer asks for offers for a contract. Companies can submit an offer until the "
                "submission deadline.",
                "Submission deadline: the date, often with a time, by which the offer must be submitted. What "
                "counts is the date on simap.ch and in the tender documents.",
                "Award: the decision on which company gets the contract. Here we speak of “contracts awarded”.",
                "Public buyer (contracting authority): whoever awards the contract – the Confederation, a canton, "
                "a commune or a public body such as a hospital or a publicly owned company.",
                "Procedure: how the contract is awarded. Open procedure: any company can submit an offer. "
                "Selective procedure: companies first apply, then the ones selected submit an offer. Invitation "
                "procedure: the public buyer invites selected companies directly to submit an offer. Direct "
                "award: the public buyer awards the contract directly, without a tender.",
                "Lot: part of a larger contract, awarded separately – often to different companies.",
                "CPV code: the EU’s common code for the type of work, goods or services. The first two digits "
                "give the sector (e.g. 45, construction work), the full eight-digit code the category "
                "(e.g. 45233000).",
                "Contract type: works, supply or services contract.",
                "Covered by international treaties: the contract falls under the international agreements on "
                "public procurement, such as the WTO’s.",
                "Offer price: the price a company stated in its offer. For a contract awarded to several "
                "companies, simap.ch gives one price per company.",
                "simap.ch notice: simap.ch requires the sentence “Dies ist keine amtliche Veröffentlichung …” at "
                "the foot of every page, so it appears word for word, in German.",
            ]]),
            ("quelle", "Source and terms of use", [
                "All data comes from the application programming interface (API) of simap.ch, the official "
                "platform for public procurement in Switzerland. Its terms of use allow the data to be reused, "
                "including commercially, provided it stays unchanged in content, is kept separate from our own "
                "analysis and carries the prescribed notice. That notice is in the footer of every page; our "
                "own analysis is marked as such.",
                "Titles and descriptions appear as they were published, in the language of the publication. "
                "We neither translate nor reword them.",
                "Licence: the register grants no licence of its own for the data; its reuse is governed by "
                "simap.ch’s terms of use ({terms}). The licence field in this page’s structured data "
                "(schema.org/Dataset) points to those terms.",
            ]),
            ("aktualisierung", "When we update the data", [
                "simap.ch releases each day’s publications for redistribution from 8 am. We usually fetch them "
                "every day from Monday to Saturday after that, and the register is mostly up to date by late "
                "morning; on some days later, or the next day. Each run fetches the contracts awarded in the "
                "current and the previous month – where corrections also arrive – and the tenders of the last "
                "75 days.",
                "The date in the footer of every page (“{stand}”) is the date of the newest publication in "
                "the register. Updated {date}: {awards} contracts awarded and {open} open tenders.",
            ]),
            ("abdeckung", "What is covered", [
                "The archive begins in {start}.{ramp}{incomplete}",
                "The register covers the contracts awarded and published on simap.ch after an open, a selective "
                "or an invitation procedure, and the tenders whose submission deadline is still open. Direct "
                "awards, which simap.ch also publishes in some cases, are not included. Contracts that are not "
                "published on simap.ch – small contracts that may be awarded directly, without a tender, for "
                "example – are missing here, just as they are on simap.ch.",
            ]),
            ("kantone", "How we assign contracts to cantons", [
                "What counts is the canton the publication gives as the place of performance (the "
                "contract’s address) – the same field simap.ch itself filters on. For a project divided into "
                "lots, each lot’s canton counts: a tender whose lots lie in several cantons is listed under "
                "each of them, marked “{multi}”. A contract awarded counts only in the canton of its lot, so "
                "that no total counts it twice.",
                "Where the publication gives no place for the contract or its lots, we use the public buyer’s "
                "canton, marked “{fallback}”. Works on national roads in Thurgau or St. Gallen that FEDRO’s "
                "Winterthur branch puts out to tender without a place, for example, appear under Zurich. Other "
                "public buyers give their own address as the place of performance; their own canton is then "
                "shown even when the work takes place elsewhere – the data does not reveal it.",
                "{nocant} All cantons together plus these contracts add up to the total on the home page. "
                "Tenders by email assigns them the same way: each of a tender’s cantons counts for your "
                "selection.",
            ]),
            ("zusammenfuehrung", "How we match companies and public buyers", [
                "A company is not always spelled the same way in the publications. Spellings that differ "
                "only in capitalisation, umlauts, accents or punctuation (“CSD INGENIEURE AG” and “CSD "
                "Ingenieure AG”, “Bolliger & Co. AG” and “Bolliger + Co. AG”) count as one company, shown under "
                "its most frequent spelling. Units with different names, such as branches, stay separate. We "
                "don’t match names against the commercial register.",
                "A company gets its own page once it has {min_c} contracts, a public buyer once it has "
                "{min_b}, and a category (CPV code) once it has {min_s}. We match public buyers by name too, "
                "regardless of spaces, hyphens, quotation marks and brackets.",
                "A contract awarded to several companies appears on the page of each of them.",
            ]),
            ("betraege", "Amounts, lots and totals", [
                "We show amounts as published. A contract’s page gives the exact amount; lists show a "
                "rounded figure, with the exact amount on hover and for screen readers.",
                "Totals include only contracts in Swiss francs awarded to a single company. For a contract "
                "awarded to several companies the publication gives a price per company: we show these prices "
                "one by one, but never add them up or attribute them to an overall contract – in framework "
                "agreements the same ceiling often appears next to every company. Amounts in euros or other "
                "currencies are shown with their currency, never in a column of francs, and left out of "
                "every total.",
                "An amount under CHF 1,000 is almost never the value of a contract but a unit rate (per "
                "hour, item or kilometre, for example). We mark it “{rate}” and leave it out of every total "
                "and median. The same goes for an amount of up to CHF 5,000 when the publication speaks of staff "
                "leasing or a day or hourly rate (“LSE”, “Personalverleih”, “Tagessatz”, “tarif journalier” and "
                "the like).",
                "For a project divided into lots, simap.ch publishes each lot separately. The project’s page "
                "lists every lot; where simap gives the same project price for several lots won by the same "
                "company, totals count it once.",
            ]),
            ("ausgeschlossen", "What is not included", [[
                "Cancelled procedures: simap.ch publishes them in the same feed as the contracts awarded; they "
                "are not shown here as contracts awarded.",
                "Corrections: when a tender or a contract awarded is corrected, the version published last "
                "applies. We don’t show earlier versions as well.",
                "Expired tenders: after the submission deadline, a tender’s page stays online for {days} "
                "days, marked “{expired}”. If the contract is awarded and published in the meantime, the same "
                "address shows who won it. We have collected tenders since {since}.",
                "We don’t list tenders without a readable submission deadline as open.",
            ]]),
            ("cpv", "Sectors and categories (CPV)", [
                "The classification follows the CPV, the EU’s Common Procurement Vocabulary. A sector is "
                "the first two digits of the code (e.g. 45, construction work), a category the exact "
                "eight-digit code (e.g. 45233000). Category labels come from the official CPV in each "
                "language; the names of the 45 sectors are the register’s own short forms.",
                "“{matched}” on company pages and “{similar}” on tender pages are based on the digits that "
                "CPV codes have in common: a general code such as 45000000 (construction work) is not enough "
                "on its own. For companies at least the first four significant digits must match. Similar "
                "contracts are in the same sector and the same canton, closest codes first.",
            ]),
            ("daten", "Downloads and subscriptions", [[
                "CSV: {csv_pages} offer their contracts awarded as a CSV file – UTF-8 with a BOM, semicolon as "
                "the separator, amounts with a decimal point. One file serves all four language versions, with "
                "English column names ({cols}) and the titles in the language of the publication. For "
                "contracts awarded to several companies the “Amount” column is left empty. Cells that begin with "
                "=, +, - or @ get a leading apostrophe, so that spreadsheet programs do not run them as "
                "formulas. “Canton source” says where the canton comes from (place: place of performance, "
                "lot: the lot, buyer: the public buyer’s seat); “Amount note” marks probable unit "
                "rates.",
                "Charts: every chart names its source and links to its data as a CSV file.",
                "Calendar: every open tender offers its submission deadline as a calendar file (.ics).",
                "RSS and email: every canton and every sector has its own RSS feed. With Tenders by email we "
                "send you new tenders by canton and sector, free and without an account.",
            ]]),
            ("kontakt", "Contact and error reports", [
                "Errors, questions and suggestions: write to {mail}. On every contract and tender page, "
                "“{report}” opens an email with the publication number in the subject line. The register is run "
                "by a private individual in Switzerland; details of the operator are in the legal notice.",
            ]),
        ],
        "csv_pages": "Canton, public buyer and company pages",
        "csv_pages_nocomp": "Canton and public buyer pages",
        "ramp": " From {a} to {b} only part of the contracts awarded were captured; these months are striped in "
                "the monthly charts. From {full} on, the register holds the contracts awarded that the simap.ch "
                "interface returned for each month when we fetched them. We don’t check them against official "
                "totals.",
        "incomplete": " {n} publications of contracts awarded from {months} came through the interface without "
                      "a title or a winner; they are left out of every figure and list.",
        "nocant": "{n} name neither a place nor a public buyer with a canton; they count in no "
                  "canton, and the canton overview lists them separately.",
        "nocant_zero": "At present every contract awarded has a canton.",
        "alert_link": "Subscribe free",
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
META["abo_grp_other"] = {"de": "Weitere Branchen", "fr": "Autres secteurs", "it": "Altri settori",
                         "en": "Other sectors"}
# structured data: the country a Dataset covers (schema.org spatialCoverage), and og:locale
COUNTRY = {"de": "Schweiz", "fr": "Suisse", "it": "Svizzera", "en": "Switzerland"}
OG_LOCALE = {"de": "de_CH", "fr": "fr_CH", "it": "it_CH", "en": "en_GB"}


# ------------------------------------------------- step 3a: data, trust, structure (14.10.2026)
# The menu's 'Branchen' opens the 45 CPV divisions (/xx/branche/); the 8-digit categories (Kategorien,
# formerly 'Bereiche') are their second level and keep their URLs (/xx/bereich/). «Rami» -> «Settori»,
# Branches -> Secteurs, Industries -> Sectors (owner, 22.10.2026).
T["nav_sectors"] = {"de": "Branchen", "fr": "Secteurs", "it": "Settori", "en": "Sectors"}
T["division"] = {"de": "Branche", "fr": "Secteur", "it": "Settore", "en": "Sector"}
T["divisions"] = {"de": "Branchen", "fr": "Secteurs", "it": "Settori", "en": "Sectors"}
# after a count, the noun in lower case ('45 Secteurs', '45 Settori' reused the menu's label; audit 7.2)
T["divisions_n"] = {"de": "Branchen", "fr": "secteurs", "it": "settori", "en": "sectors"}
# The canton of a record whose publication names no place: the buyer's seat (kantone.py), marked on
# every row and record page that shows it
T["fb_note"] = {"de": "Ort nicht angegeben – Kanton des Auftraggebers",
                "fr": "Lieu non indiqué – canton de l’acheteur public",
                "it": "Luogo non indicato – cantone dell’ente pubblico",
                "en": "Location not given – canton of the public buyer"}
T["multi_cantons"] = {"de": "mehrere Kantone", "fr": "plusieurs cantons", "it": "più cantoni",
                      "en": "several cantons"}
T["lot_cantons"] = {"de": "nach den Losen", "fr": "selon les lots", "it": "secondo i lotti", "en": "from the lots"}
T["no_canton"] = {"de": "Ohne Kanton", "fr": "Sans canton", "it": "Senza cantone", "en": "No canton"}
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
                       "it": "senza {k} probabili prezzi unitari", "en": "excluding {k} probable unit rates"}
IDX["sum_no_rates_one"] = {"de": "ohne einen vermutlichen Einheitspreis", "fr": "sans un prix probablement unitaire",
                           "it": "senza un probabile prezzo unitario", "en": "excluding one probable unit rate"}
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
IDX["chart_src"] = {"de": "Quelle: simap.ch, eigene Auswertung", "fr": "Source : simap.ch, nos calculs",
                    "it": "Fonte: simap.ch, calcoli nostri", "en": "Source: simap.ch, our analysis"}
# (the link to its data, "chart_csv", is in fix round 1 below)
# the open tenders hub
IDX["multi_note"] = {
    "de": "Eine Ausschreibung mit Losen in mehreren Kantonen zählt in jedem dieser Kantone.",
    "fr": "Un appel d’offres dont les lots se situent dans plusieurs cantons compte dans chacun d’eux.",
    "it": "Un bando con lotti in più cantoni conta in tutti quei cantoni.",
    "en": "A tender with lots in several cantons counts in each of them.",
}
IDX["nodl_note"] = {
    "de": "{n} Ausschreibungen ohne lesbare Eingabefrist führen wir nicht auf.",
    "fr": "Nous ne listons pas {n} appels d’offres dont le délai de remise est illisible.",
    "it": "Non elenchiamo {n} bandi senza una scadenza chiara.",
    "en": "We don’t list {n} tenders without a readable submission deadline.",
}
# the canton overview: the awards that count in no canton, so that the cantons add up to the total
IDX["nocant_lead"] = {
    "de": "{n} nennen weder einen Ort noch einen Auftraggeber mit Kanton. Alle Kantone zusammen und diese "
          "Aufträge ergeben die {total} der Startseite.",
    "fr": "{n} n’indiquent ni lieu ni acheteur public avec canton. Tous les cantons et ces marchés donnent "
          "ensemble les {total} de la page d’accueil.",
    "it": "{n} non indicano né un luogo né un ente pubblico con cantone. Con questi, la somma dei cantoni dà i "
          "{total} della home.",
    "en": "{n} name neither a place nor a public buyer with a canton. All cantons together and "
          "these contracts make up the {total} on the home page.",
}
# the home: who the site is for, and the two company counts
META["audience"] = {
    "de": "Für Firmen, die öffentliche Ausschreibungen suchen, und für alle, die wissen wollen, wer "
          "die Aufträge gewinnt.",
    "fr": "Pour les entreprises qui cherchent des appels d’offres publics, et pour tous ceux qui veulent "
          "savoir qui remporte les marchés.",
    "it": "Per le aziende che cercano bandi pubblici e per chi vuole sapere chi vince gli appalti.",
    "en": "For companies looking for public tenders, and for anyone who wants to know who wins the "
          "contracts.",
}
META["home_firms_tile"] = {"de": "Firmen, davon {k} mit eigener Seite",
                           "fr": "entreprises, dont {k} avec leur propre page",
                           "it": "aziende, di cui {k} con una pagina propria",
                           "en": "companies, {k} with a page of their own"}
META["home_firms_tile_one"] = {"de": "Firma", "fr": "entreprise", "it": "azienda", "en": "company"}
# the 45 divisions: an index and one award page each
IDX["div_index_h1"] = {"de": "Öffentliche Aufträge nach Branche", "fr": "Marchés publics par secteur",
                       "it": "Appalti pubblici per settore", "en": "Public contracts by sector"}
IDX["div_index_lead"] = {
    "de": "Die {n} Branchen des CPV (die ersten zwei Ziffern des Codes) mit ihren offenen Ausschreibungen "
          "und vergebenen Aufträgen. Jede Branche umfasst viele einzelne Kategorien (genauer "
          "achtstelliger Code).",
    "fr": "Les {n} secteurs du CPV (les deux premiers chiffres du code) avec leurs appels d’offres en "
          "cours et leurs marchés attribués. Chaque secteur regroupe de nombreuses catégories détaillées "
          "(code exact à huit chiffres).",
    "it": "I {n} settori del CPV, cioè le prime due cifre del codice, con i loro bandi aperti e gli appalti "
          "aggiudicati. Ogni settore raccoglie molte categorie (il codice esatto di otto cifre).",
    "en": "The {n} sectors of the CPV (the first two digits of the code) with their open tenders and "
          "contracts awarded. Each sector covers many specific categories (the exact eight-digit code).",
}
IDX["div_index_title"] = {"de": "Öffentliche Aufträge nach Branche — CPV-Übersicht",
                          "fr": "Marchés publics par secteur — aperçu CPV",
                          "it": "Appalti pubblici per settore — panoramica CPV",
                          "en": "Public contracts by sector — CPV overview"}
IDX["div_index_desc"] = {
    "de": "Die {n} Branchen der öffentlichen Aufträge in der Schweiz: offene Ausschreibungen und "
          "vergebene Aufträge je Branche, mit Firmen und Auftraggebern.",
    "fr": "Les {n} secteurs des marchés publics en Suisse : appels d’offres en cours et marchés attribués par "
          "secteur, avec entreprises et acheteurs publics.",
    "it": "I {n} settori degli appalti pubblici in Svizzera: bandi aperti e appalti aggiudicati per settore, con "
          "aziende ed enti pubblici.",
    "en": "The {n} sectors of Swiss public procurement: open tenders and contracts awarded per sector, with "
          "companies and public buyers.",
}
# the division index's two count columns say what they count (22.10.2026: «Open | Contracts» read as «open contracts»)
IDX["col_open"] = {"de": "Offene Ausschreibungen", "fr": "Appels d’offres en cours", "it": "Bandi aperti",
                   "en": "Open tenders"}
IDX["all_bereiche"] = {"de": "Alle {n} Kategorien von A bis Z (genauer CPV-Code)",
                       "fr": "Les {n} catégories de A à Z (code CPV exact)",
                       "it": "Tutte le {n} categorie dalla A alla Z (codice CPV esatto)",
                       "en": "All {n} categories from A to Z (exact CPV code)"}
META["div_suffix"] = {"de": " — öffentliche Aufträge", "fr": " — marchés publics",
                      "it": " — appalti pubblici", "en": " — public contracts"}
META["div_suffix_short"] = {"de": " — Aufträge", "fr": " — marchés", "it": " — appalti",
                            "en": " — contracts"}
META["div_lead"] = {
    "de": "{n} an {f} in der Branche «{name}», publiziert auf simap.ch.",
    "fr": "{n} attribués à {f} dans le secteur « {name} », publiés sur simap.ch.",
    "it": "{n} aggiudicati a {f} nel settore «{name}», pubblicati su simap.ch.",
    "en": "{n} awarded to {f} in the “{name}” sector, published on simap.ch.",
}
META["div_desc"] = {
    "de": "Branche «{name}» (CPV {code}): {n} an {f}. Die Firmen und Auftraggeber mit den meisten Aufträgen, "
          "nach Kanton.",
    "fr": "Secteur « {name} » (CPV {code}) : {n} attribués à {f}. Les entreprises et les acheteurs publics les "
          "plus actifs, par canton.",
    "it": "Settore «{name}» (CPV {code}): {n} andati a {f}. Le aziende e gli enti pubblici più attivi, per "
          "cantone.",
    "en": "The “{name}” sector (CPV {code}): {n} awarded to {f}. The companies and public buyers with the most "
          "contracts, by canton.",
}
META["div_desc_short"] = {
    "de": "Branche «{name}» (CPV {code}): {n} an {f}.",
    "fr": "Secteur « {name} » (CPV {code}) : {n} attribués à {f}.",
    "it": "Settore «{name}» (CPV {code}): {n} andati a {f}.",
    "en": "The “{name}” sector (CPV {code}): {n} awarded to {f}.",
}
IDX["div_none"] = {
    "de": "In dieser Branche wurde noch kein vergebener Auftrag publiziert.",
    "fr": "Aucun marché attribué n’a encore été publié dans ce secteur.",
    "it": "In questo settore non è ancora stato pubblicato nessun appalto aggiudicato.",
    "en": "No contract awarded in this sector has been published yet.",
}
IDX["div_buyers_h"] = {"de": "Auftraggeber", "fr": "Acheteurs publics", "it": "Enti pubblici",
                       "en": "Public buyers"}
IDX["div_sectors_h"] = {"de": "Kategorien dieser Branche (genauer CPV-Code)",
                        "fr": "Catégories de ce secteur (code CPV exact)",
                        "it": "Categorie di questo settore (codice CPV esatto)",
                        "en": "Categories in this sector (exact CPV code)"}
IDX["mc_title_div"] = {"de": "Vergebene Aufträge pro Monat in dieser Branche",
                       "fr": "Marchés attribués chaque mois dans ce secteur",
                       "it": "Appalti aggiudicati ogni mese in questo settore",
                       "en": "Contracts awarded each month in this sector"}
IDX["top_n"] = {"de": "die {k} mit den meisten Aufträgen", "fr": "les {k} qui ont remporté le plus de marchés",
                "it": "le {k} che hanno vinto più appalti", "en": "the {k} that won the most contracts"}
IDX["top_n_b"] = {"de": "die {k} mit den meisten vergebenen Aufträgen", "fr": "les {k} qui ont attribué le plus de marchés",
                  "it": "i {k} che hanno aggiudicato più appalti", "en": "the {k} that awarded the most contracts"}
IDX["of_division"] = {"de": "Branche «{name}»", "fr": "Secteur « {name} »", "it": "Settore «{name}»",
                      "en": "The “{name}” sector"}
# a sector page's own numbers, in one sentence (the thin CPV pages, technical audit 14.10.2026)
IDX["stats_sum"] = {"de": "Summe der publizierten Beträge: {v}.", "fr": "Total des montants publiés : {v}.",
                    "it": "Totale degli importi pubblicati: {v}.", "en": "Total of published amounts: {v}."}
IDX["stats_buyer"] = {"de": "Häufigster Auftraggeber: {b} ({n}).", "fr": "Acheteur public le plus fréquent : {b} ({n}).",
                      "it": "Ente pubblico più frequente: {b} ({n}).", "en": "Most frequent public buyer: {b} ({n})."}
IDX["stats_firm"] = {"de": "Häufigste Firma: {c} ({n}).", "fr": "Entreprise la plus fréquente : {c} ({n}).",
                     "it": "Azienda più frequente: {c} ({n}).", "en": "Most frequent company: {c} ({n})."}
IDX["stats_div"] = {"de": "Die Kategorie gehört zur Branche {d}.", "fr": "Cette catégorie fait partie du secteur {d}.",
                    "it": "Questa categoria fa parte del settore {d}.", "en": "This category belongs to the {d} sector."}
T["by_amount"] = {"de": "nach Betrag", "fr": "par montant", "it": "per importo", "en": "by amount"}
# «Appalti aggiudicati per settore» (owner, 22.10.2026)
IDX["by_division_awards"] = {"de": "Vergebene Aufträge nach Branche", "fr": "Marchés attribués par secteur",
                             "it": "Appalti aggiudicati per settore", "en": "Contracts awarded by sector"}
IDX["all_divisions"] = {"de": "Alle Branchen", "fr": "Tous les secteurs", "it": "Tutti i settori",
                        "en": "All sectors"}
IDX["to_divisions"] = {"de": "Die {n} Branchen im Überblick", "fr": "Les {n} secteurs en un coup d’œil",
                       "it": "I {n} settori a colpo d’occhio", "en": "The {n} sectors at a glance"}
# the two pages Brevo sends people to: one language each (from the path, ?lang or the browser)
META["abo_from"] = {
    "de": "Absender: auftragsregister.ch <{mail}>.",
    "fr": "Expéditeur : auftragsregister.ch <{mail}>.",
    "it": "Mittente: auftragsregister.ch <{mail}>.",
    "en": "Sender: auftragsregister.ch <{mail}>.",
}
# (when the e-mails come, "abo_when", is at the end of the file, in the 'strictly necessary' pass)
META["abo_spam"] = {
    "de": "Keine E-Mail erhalten? Bitte prüfen Sie Ihren Spam-Ordner.",
    "fr": "Rien reçu ? Vérifiez votre dossier de courrier indésirable.",
    "it": "E-mail non arrivata? Conviene controllare la cartella dello spam.",
    "en": "Nothing arrived? Please check your spam folder.",
}
# (how to change the selection, "abo_change", is at the end of the file)
META["abo_lang_label"] = {"de": "Diese Seite in", "fr": "Cette page en", "it": "Questa pagina in",
                          "en": "This page in"}


# ------------------------------------------- step 3b (15.10.2026): the interactive layer
# The search in the header of every page (its field's name and button), the search page, the A–Z
# letter pages, the long lists cut to their first rows, the company finder on the home.
T["search"] = {"de": "Suche", "fr": "Recherche", "it": "Ricerca", "en": "Search"}
T["search_go"] = {"de": "Suchen", "fr": "Rechercher", "it": "Cerca", "en": "Search"}
META["search_title"] = {"de": "Im Register suchen", "fr": "Rechercher dans le registre",
                        "it": "Cerca nel registro", "en": "Search the register"}
META["search_desc"] = {
    "de": "Suchen Sie Firmen, Auftraggeber, offene Ausschreibungen, Branchen und Kantone im Register der "
          "öffentlichen Aufträge der Schweiz.",
    "fr": "Cherchez des entreprises, des acheteurs publics, des appels d’offres en cours, des secteurs et des "
          "cantons dans le registre des marchés publics suisses.",
    "it": "Cerca aziende, enti pubblici, bandi aperti, settori e cantoni nel registro degli appalti pubblici "
          "svizzeri.",
    "en": "Search companies, public buyers, open tenders, sectors and cantons in the register "
          "of Swiss public contracts.",
}
# (the search page's lead, "search_lead", is at the end of the file, in the 'strictly necessary' pass)
# the field's label as a question, as one would ask it
META["search_label"] = {"de": "Wonach suchen Sie?", "fr": "Que cherchez-vous ?", "it": "Cosa cerchi?",
                        "en": "What are you looking for?"}
META["search_nojs"] = {
    "de": "Die Suche braucht JavaScript. Ohne JavaScript führen diese Verzeichnisse zu jedem Eintrag "
          "des Registers:",
    "fr": "La recherche a besoin de JavaScript. Sans lui, ces répertoires vous mènent à chaque entrée du "
          "registre :",
    "it": "La ricerca ha bisogno di JavaScript. Senza, questi elenchi ti portano a ogni voce del registro:",
    "en": "Search needs JavaScript. Without it, these directories lead to every entry in the register:",
}
# (the directories' heading, "search_dirs", is at the end of the file)
META["az_companies"] = {"de": "Firmen von A bis Z", "fr": "Entreprises de A à Z",
                        "it": "Aziende dalla A alla Z", "en": "Companies from A to Z"}
META["az_buyers"] = {"de": "Auftraggeber von A bis Z", "fr": "Acheteurs publics de A à Z",
                     "it": "Enti pubblici dalla A alla Z", "en": "Public buyers from A to Z"}
# a letter page of the company and buyer indexes: '{l}' is the letter ('A', '0–9')
META["letter_companies_title"] = {"de": "Firmen mit Anfangsbuchstabe {l} – öffentliche Aufträge",
                                  "fr": "Entreprises commençant par {l} – marchés publics",
                                  "it": "Aziende con iniziale {l} – appalti pubblici",
                                  "en": "Companies starting with {l} – public contracts"}
META["letter_companies_h1"] = {"de": "Firmen: {l}", "fr": "Entreprises : {l}", "it": "Aziende: {l}",
                               "en": "Companies: {l}"}
META["letter_companies_desc"] = {
    "de": "{n} Firmen mit dem Anfangsbuchstaben {l}, jede mit ihren öffentlichen Aufträgen in der "
          "Schweiz.",
    "fr": "{n} entreprises commençant par {l}, chacune avec ses marchés publics en Suisse.",
    "it": "{n} aziende con iniziale {l}, ognuna con i suoi appalti pubblici in Svizzera.",
    "en": "{n} companies starting with {l}, each with its public contracts in Switzerland.",
}
META["letter_buyers_title"] = {"de": "Auftraggeber mit Anfangsbuchstabe {l} – öffentliche Aufträge",
                               "fr": "Acheteurs publics commençant par {l} – marchés publics",
                               "it": "Enti pubblici con iniziale {l} – appalti pubblici",
                               "en": "Public buyers starting with {l} – public contracts"}
META["letter_buyers_h1"] = {"de": "Auftraggeber: {l}", "fr": "Acheteurs publics : {l}", "it": "Enti pubblici: {l}",
                            "en": "Public buyers: {l}"}
META["letter_buyers_desc"] = {
    "de": "{n} Auftraggeber mit dem Anfangsbuchstaben {l}, jeder mit den Aufträgen, die er vergeben und auf "
          "simap.ch publiziert hat.",
    "fr": "{n} acheteurs publics commençant par {l}, chacun avec les marchés attribués publiés sur simap.ch.",
    "it": "{n} enti pubblici con iniziale {l}, ognuno con gli appalti aggiudicati pubblicati su simap.ch.",
    "en": "{n} public buyers starting with {l}, each with the contracts it awarded and published on simap.ch.",
}
# fix round 3 (item 39): the bucket of names that start with neither a letter nor a figure
META["letter_companies_h1_other"] = {"de": "Firmen: Namen mit Ziffern oder Zeichen",
                                     "fr": "Entreprises : noms commençant par un chiffre ou un signe",
                                     "it": "Aziende: nomi che iniziano con una cifra o un segno",
                                     "en": "Companies: names starting with a figure or a sign"}
META["letter_buyers_h1_other"] = {"de": "Auftraggeber: Namen mit Ziffern oder Zeichen",
                                  "fr": "Acheteurs publics : noms commençant par un chiffre ou un signe",
                                  "it": "Enti pubblici: nomi che iniziano con una cifra o un segno",
                                  "en": "Public buyers: names starting with a figure or a sign"}
META["letter_companies_desc_other"] = {
    "de": "{n} Firmen, deren Name mit einer Ziffer oder einem Zeichen beginnt, jede mit ihren öffentlichen Aufträgen.",
    "fr": "{n} entreprises dont le nom commence par un chiffre ou un signe, chacune avec ses marchés publics.",
    "it": "{n} aziende il cui nome inizia con una cifra o un segno, ognuna con i suoi appalti pubblici.",
    "en": "{n} companies whose name starts with a figure or a sign, each with its public contracts.",
}
META["letter_buyers_desc_other"] = {
    "de": "{n} Auftraggeber, deren Name mit einer Ziffer oder einem Zeichen beginnt, jeder mit seinen vergebenen Aufträgen.",
    "fr": "{n} acheteurs publics dont le nom commence par un chiffre ou un signe, chacun avec ses marchés attribués.",
    "it": "{n} enti pubblici il cui nome inizia con una cifra o un segno, ognuno con i suoi appalti aggiudicati.",
    "en": "{n} public buyers whose name starts with a figure or a sign, each with the contracts it awarded.",
}
META["letters_lead"] = {
    "de": "Wählen Sie einen Buchstaben – jeder hat eine eigene Seite.",
    "fr": "Choisissez une lettre : chacune a sa propre page.",
    "it": "Scegli una lettera: ognuna ha la sua pagina.",
    "en": "Pick a letter – each one has a page of its own.",
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
    "de": "Die {n} Ausschreibungen, deren Frist zuerst abläuft – von {total}.",
    "fr": "Les {n} appels d’offres qui expirent en premier, sur {total}.",
    "it": "I {n} bandi che scadono prima, su {total}.",
    "en": "The {n} tenders that close first, out of {total}.",
}
IDX["rest_note"] = {
    "de": "Die übrigen {n} stehen in den Listen der Kantone und Branchen.",
    "fr": "Les {n} autres figurent dans les listes des cantons et des secteurs.",
    "it": "Gli altri {n} si trovano negli elenchi dei cantoni e dei settori.",
    "en": "The other {n} are in the canton and sector lists.",
}
META["all_list_title"] = {"de": "{h} – vollständige Liste", "fr": "{h} – liste complète",
                          "it": "{h} – elenco completo", "en": "{h} – full list"}
META["all_list_lead"] = {
    "de": "Alle {n} offenen Ausschreibungen dieser Liste auf einer Seite – die nächste Frist zuerst.",
    "fr": "Les {n} appels d’offres en cours de cette liste sur une seule page, le délai le plus proche "
          "d’abord.",
    "it": "Tutti i {n} bandi aperti di questo elenco in una sola pagina, dal più urgente.",
    "en": "All {n} open tenders in this list on one page, nearest deadline first.",
}
META["all_list_back"] = {"de": "Zur kurzen Liste", "fr": "Retour à la liste courte", "it": "Torna all’elenco breve",
                         "en": "Back to the short list"}
# the home's company finder (the door 'Unternehmen finden' becomes a search box)
META["finder_label"] = {"de": "Name der Firma", "fr": "Nom de l’entreprise", "it": "Nome dell’azienda",
                        "en": "Company name"}
META["finder_ph"] = {"de": "z. B. Implenia", "fr": "p. ex. Implenia", "it": "ad es. Implenia",
                     "en": "e.g. Implenia"}
META["finder_sub"] = {
    "de": "{n} Firmen haben mindestens einen Auftrag gewonnen; {k} davon haben eine eigene Seite.",
    "fr": "{n} entreprises ont remporté au moins un marché ; {k} ont leur propre page.",
    "it": "{n} aziende hanno vinto almeno un appalto; {k} hanno una pagina propria.",
    "en": "{n} companies have won at least one contract; {k} of them have a page of their own.",
}
META["finder_az"] = {"de": "Von A bis Z", "fr": "De A à Z", "it": "Dalla A alla Z", "en": "From A to Z"}
# the alert form: the e-mail field's error, tied to the field (aria-describedby)
META["abo_email_missing"] = {"de": "Bitte geben Sie Ihre E-Mail-Adresse ein.",
                             "fr": "Indiquez votre adresse e-mail.",
                             "it": "Inserisci il tuo indirizzo e-mail.",
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
                           "fr": "Appels d’offres en cours dans le secteur « {name} »",
                           "it": "Bandi aperti nel settore «{name}»", "en": "Open tenders in the “{name}” sector"}
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
    "hidden_1": {"de": "1 Ausschreibung ist inzwischen abgelaufen und ausgeblendet",
                 "fr": "1 appel d’offres expiré entre-temps n’est plus affiché",
                 "it": "1 bando scaduto nel frattempo è nascosto",
                 "en": "1 tender has closed since and is hidden"},
    "hidden_n": {"de": "{n} Ausschreibungen sind inzwischen abgelaufen und ausgeblendet",
                 "fr": "{n} appels d’offres expirés entre-temps ne sont plus affichés",
                 "it": "{n} bandi scaduti nel frattempo sono nascosti",
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
    "top": {"de": "Nach oben", "fr": "Retour en haut", "it": "Torna su", "en": "Back to top"},
    # fix round 2: short enough for the field (the longer list was cut mid-word at 1280 and 390 px); '|' separates
    # shorter forms, and /stand.js shows the first that fits the field as the reader sees it
    "ph": {"de": "Firma, Auftraggeber, Thema\u00a0…|Firma, Auftraggeber\u00a0…|Firma, Thema\u00a0…",
           "fr": "Entreprise, acheteur, thème…|Entreprise, acheteur…|Entreprise, thème…",
           "it": "Azienda, ente pubblico, tema…|Azienda, ente…|Azienda, tema…",
           "en": "Company, buyer, topic…|Company, buyer…|Company, topic…"},
    # the search (suche.js), its groups in this order
    "g_t": {"de": "Offene Ausschreibungen", "fr": "Appels d’offres en cours", "it": "Bandi aperti",
            "en": "Open tenders"},
    "g_u": {"de": "Firmen", "fr": "Entreprises", "it": "Aziende", "en": "Companies"},
    "g_b": {"de": "Auftraggeber", "fr": "Acheteurs publics", "it": "Enti pubblici", "en": "Public buyers"},
    "g_s": {"de": "Branchen und Kategorien", "fr": "Secteurs et catégories", "it": "Settori e categorie",
            "en": "Sectors and categories"},
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
                  "it": "Prova con un’altra parola, una parte del nome o gli elenchi qui sotto.",
                  "en": "Try another word, part of the name, or the directories below."},
    "n_res": {"de": "{n} Treffer", "fr": "{n} résultats", "it": "{n} risultati", "en": "{n} results"},
    "n_res_1": {"de": "1 Treffer", "fr": "1 résultat", "it": "1 risultato", "en": "1 result"},
    "n_sug": {"de": "{n} Vorschläge, mit den Pfeiltasten wählen", "fr": "{n} suggestions ; choisissez avec les flèches",
              "it": "{n} suggerimenti: scegli con i tasti freccia", "en": "{n} suggestions; use the arrow keys to choose"},
    "more": {"de": "{n} weitere anzeigen", "fr": "Afficher les {n} autres", "it": "Mostra gli altri {n}",
             "en": "Show {n} more"},
    "aw_1": {"de": "1 Auftrag", "fr": "1 marché", "it": "1 appalto", "en": "1 contract"},
    "aw_n": {"de": "{n} Aufträge", "fr": "{n} marchés", "it": "{n} appalti", "en": "{n} contracts"},
    "open_1": {"de": "1 offen", "fr": "1 en cours", "it": "1 aperto", "en": "1 open"},
    "open_n": {"de": "{n} offen", "fr": "{n} en cours", "it": "{n} aperti", "en": "{n} open"},
    "to_award": {"de": "Seite des Auftrags", "fr": "page du marché", "it": "pagina dell’appalto",
                 "en": "contract page"},
    "k_canton": {"de": "Kanton", "fr": "Canton", "it": "Cantone", "en": "Canton"},
    "k_div": {"de": "Branche", "fr": "Secteur", "it": "Settore", "en": "Sector"},
    "k_sec": {"de": "Kategorie", "fr": "Catégorie", "it": "Categoria", "en": "Category"},
    "until": {"de": "bis {d}", "fr": "jusqu’au {d}", "it": "entro il {d}", "en": "due {d}"},
    "loading": {"de": "Wird geladen\u00a0…", "fr": "Chargement …", "it": "Caricamento …", "en": "Loading …"},
    "failed": {"de": "Wir konnten die Daten nicht laden.", "fr": "Impossible de charger les données.",
               "it": "Non siamo riusciti a caricare i dati.", "en": "We couldn’t load the data."},
    # the filters of the tender lists (liste.js)
    "f_label": {"de": "Ausschreibungen filtern", "fr": "Filtrer les appels d’offres", "it": "Filtra i bandi",
                "en": "Filter tenders"},
    "f_q": {"de": "Titel oder Auftraggeber", "fr": "Titre ou acheteur public", "it": "Titolo o ente pubblico",
            "en": "Title or public buyer"},
    "f_k_all": {"de": "Alle Kantone", "fr": "Tous les cantons", "it": "Tutti i cantoni", "en": "All cantons"},
    "f_b_all": {"de": "Alle Branchen", "fr": "Tous les secteurs", "it": "Tutti i settori", "en": "All sectors"},
    "f_soon": {"de": "Frist in den nächsten 7 Tagen", "fr": "Délai dans les 7 prochains jours",
               "it": "Scadenza entro 7 giorni", "en": "Deadline within 7 days"},
    "f_clear": {"de": "Filter zurücksetzen", "fr": "Réinitialiser les filtres", "it": "Azzera i filtri",
                "en": "Clear filters"},
    # the e-mail service, prefilled with the selection: what one gets (owner, 22.10.2026)
    "f_abo": {"de": "Diese Auswahl per E-Mail", "fr": "Cette sélection par e-mail",
              "it": "Questa selezione via e-mail", "en": "This selection by email"},
    "f_count": {"de": "{n} von {m} offenen Ausschreibungen", "fr": "{n} sur {m} appels d’offres en cours",
                "it": "{n} di {m} bandi aperti", "en": "{n} of {m} open tenders"},
    "f_none": {"de": "Für diese Auswahl gibt es keine offene Ausschreibung.",
               "fr": "Aucun appel d’offres en cours pour cette sélection.",
               "it": "Nessun bando aperto per questa selezione.",
               "en": "No open tenders for this selection."},
    "multi": {"de": "mehrere Kantone", "fr": "plusieurs cantons", "it": "più cantoni", "en": "several cantons"},
    # the alert form (abo.js)
    "sel": {"de": "({n} ausgewählt)", "fr": "(sélection : {n})", "it": "(selezionati: {n})", "en": "({n} selected)"},
    # (the weekly estimate, "pv" and "pv_lt", is at the end of the file, in the 'strictly necessary' pass)
    "pv_note": {"de": "für die gewählten Kantone und Branchen, berechnet aus den letzten 8 Wochen",
                "fr": "pour les cantons et secteurs choisis, d’après les 8 dernières semaines",
                "it": "per i cantoni e i settori scelti, in base alle ultime 8 settimane",
                "en": "for the chosen cantons and sectors, based on the last 8 weeks"},
    # a canton's awards in one industry (kb.js)
    "kb_h": {"de": "{div} im Kanton {name}", "fr": "{div} dans le canton {of}", "it": "{div} nel Canton {name}",
             "en": "{div} in the canton of {name}"},
    "kb_lead": {"de": "{n} an {f} (Daten dieses Registers).",
                "fr": "{n} pour {f} (données de ce registre).",
                "it": "{n} a {f} (dati di questo registro).",
                "en": "{n} to {f} (data from this register)."},
    "kb_f1": {"de": "1 Firma", "fr": "1 entreprise", "it": "1 azienda", "en": "1 company"},
    "kb_fn": {"de": "{n} Firmen", "fr": "{n} entreprises", "it": "{n} aziende", "en": "{n} companies"},
    "kb_top": {"de": "Firmen mit den meisten Aufträgen", "fr": "Entreprises qui ont remporté le plus de marchés",
               "it": "Aziende che hanno vinto più appalti", "en": "Companies that won the most contracts"},
    "kb_recent": {"de": "Die {k} neuesten von {n}", "fr": "Les {k} plus récents sur {n}",
                  "it": "I {k} più recenti su {n}", "en": "The {k} most recent of {n}"},
    "kb_all": {"de": "Die Branche in der ganzen Schweiz", "fr": "Le secteur dans toute la Suisse",
               "it": "Il settore in tutta la Svizzera", "en": "The sector across Switzerland"},
    "kb_csv": {"de": "Alle Aufträge des Kantons als CSV", "fr": "Tous les marchés du canton en CSV",
               "it": "Tutti gli appalti del cantone in CSV", "en": "All the canton’s contracts as CSV"},
    "kb_close": {"de": "Schliessen", "fr": "Fermer", "it": "Chiudi", "en": "Close"},
    # fix round 3: why '268 Aufträge an 264 Firmen' is no error, as the Branche pages say it
    "kb_once": {"de": "{k} der {f} Firmen haben hier genau einen Auftrag erhalten.",
                "fr": "{k} des {f} entreprises ont remporté ici un seul marché.",
                "it": "{k} delle {f} aziende hanno vinto qui un solo appalto.",
                "en": "{k} of the {f} companies won exactly one contract here."},
    "kb_hint": {"de": "Wählen Sie eine Branche: Sie sehen die Aufträge dieses Kantons und die Firmen mit den "
                      "meisten davon.",
                "fr": "Choisissez un secteur pour voir les marchés de ce canton et les entreprises qui en ont "
                      "remporté le plus.",
                "it": "Scegli un settore: vedi gli appalti di questo cantone e le aziende che ne hanno vinti di più.",
                "en": "Pick a sector to see this canton’s contracts and the companies that won the most of them."},
}

# ---------------------------------------------------------------- step 4: design A2 "Brass"
# The phone menu (a <details> in the header of every page) and the home in the A2 design (15.10.2026):
# the hero's eyebrow and its brass pillars, the map of the open tenders per canton (legend, attribution,
# read-out), the section eyebrows and the alarm band. The map's read-out words for the script are in JS.
T["menu"] = {"de": "Menü", "fr": "Menu", "it": "Menu", "en": "Menu"}
# fix round 3 (item 38): eyebrows that say what the H1 does not
META["list_eyebrow"] = {"de": "Nächste Frist zuerst", "fr": "Délai le plus proche d’abord",
                        "it": "Prima le scadenze più vicine", "en": "Nearest deadline first"}
META["az_eyebrow"] = {"de": "Verzeichnis A–Z", "fr": "Répertoire A–Z", "it": "Elenco A–Z", "en": "A–Z directory"}
META["abo_eyebrow"] = {"de": "Gratis · ohne Konto", "fr": "Gratuit · sans compte", "it": "Gratis · senza account",
                       "en": "Free · no account"}
META["about_eyebrow"] = {"de": "Daten · Quellen · Begriffe", "fr": "Données · sources · termes",
                         "it": "Dati · fonti · termini", "en": "Data · sources · terms"}
META["home_eyebrow"] = {"de": "{span} · aktualisiert am {d}", "fr": "{span} · mis à jour le {d}",
                        "it": "{span} · aggiornato al {d}", "en": "{span} · updated {d}"}
META["sky_peak"] = {"de": "{m} · die meisten Aufträge", "fr": "{m} · record de marchés",
                    "it": "{m} · record di appalti", "en": "{m} · most contracts"}
META["map_eyebrow"] = {"de": "01 · Karte · aktualisiert am {d}", "fr": "01 · Carte · mise à jour le {d}",
                       "it": "01 · Mappa · aggiornata al {d}", "en": "01 · Map · updated {d}"}
META["map_legend"] = {"de": "Je heller ein Kanton, desto mehr offene Ausschreibungen.",
                      "fr": "Plus un canton est clair, plus il compte d’appels d’offres en cours.",
                      "it": "Più un cantone è chiaro, più bandi aperti ha.",
                      "en": "The brighter a canton, the more open tenders it has."}
META["map_hint"] = {"de": "Oder wählen Sie den Kanton in der Liste.", "fr": "Ou choisissez-le dans la liste.",
                    "it": "Oppure si sceglie il cantone dall’elenco.", "en": "Or pick it from the list."}
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
META["sec_awards"] = {"de": "02 · Vergebene Aufträge", "fr": "02 · Marchés attribués", "it": "02 · Appalti aggiudicati",
                      "en": "02 · Contracts awarded"}
META["sec_companies"] = {"de": "03 · Firmen", "fr": "03 · Entreprises", "it": "03 · Aziende",
                         "en": "03 · Companies"}
META["sec_divisions"] = {"de": "04 · Branchen", "fr": "04 · Secteurs", "it": "04 · Settori", "en": "04 · Sectors"}
# the e-mail service's band at the foot of the home (owner, 22.10.2026: «Ricevi i nuovi bandi via e-mail»)
META["alarm_eyebrow"] = {"de": "Ausschreibungen per E-Mail · gratis", "fr": "Appels d’offres par e-mail · gratuit",
                         "it": "Bandi via e-mail · gratis", "en": "Tenders by email · free"}
META["alarm_h2"] = {"de": "Neue Ausschreibungen per E-Mail erhalten",
                    "fr": "Recevez les nouveaux appels d’offres par e-mail",
                    "it": "Ricevi i nuovi bandi via e-mail", "en": "Get new tenders by email"}
META["map_about"] = {
    "de": "Kartengrundlage der Startseite: swiss-maps © Interactive Things (BSD-3-Clause), Daten BFS/swisstopo.",
    "fr": "Fond de carte de la page d’accueil : swiss-maps © Interactive Things (BSD-3-Clause), données OFS/swisstopo.",
    "it": "Base cartografica della home: swiss-maps © Interactive Things (BSD-3-Clause), dati UST/swisstopo.",
    "en": "Base map of the home page: swiss-maps © Interactive Things (BSD-3-Clause), data FSO/swisstopo.",
}
JS["map_rank"] = {"de": "Rang {r} von 26", "fr": "Rang {r} sur 26", "it": "Posizione {r} su 26",
                  "en": "Rank {r} of 26"}
JS["map_share"] = {"de": "{p}\u00a0% aller offenen Ausschreibungen", "fr": "{p} % des appels d’offres en cours",
                   "it": "{p}% dei bandi aperti", "en": "{p}% of all open tenders"}
# fix round 3: the read-out's link to the canton chosen on the map
JS["map_go"] = {"de": "Ausschreibungen in {c}", "fr": "Appels d’offres en cours : {c}", "it": "Bandi aperti: {c}",
                "en": "Tenders in {c}"}
JS["map_lit"] = {"de": "{n} von 26 Kantonen", "fr": "{n} cantons sur 26", "it": "{n} cantoni su 26",
                 "en": "{n} of 26 cantons"}


# ---------------------------------------------------------------- fix round 1 (20.10.2026)
# After the third audit: the masthead's 'independent, not official', the short phone units of the stacked tables,
# the chart as a table, the lists' filter bar and leads, the cut tables, the buyer's-seat share, the outlier notes,
# the CSV links that say what they download, the authorities' finder, the alert form and its two return pages.
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
                         "fr": "{n} dans le secteur « {name} », dans toute la Suisse, le délai le plus proche en premier.",
                         "it": "{n} del settore «{name}» in tutta la Svizzera, la scadenza più vicina per prima.",
                         "en": "{n} in the “{name}” sector across Switzerland, the nearest deadline first."}
META["all_list_crumb"] = {"de": "Vollständige Liste", "fr": "Liste complète", "it": "Elenco completo",
                          "en": "Full list"}
META["desc_amount_approx"] = {"de": " für rund {amount}", "fr": " pour environ {amount}", "it": " per circa {amount}",
                              "en": " for about {amount}"}
META["company_val_approx"] = {"de": ", zusammen rund {v}", "fr": ", au total environ {v}",
                              "it": ", per un totale di circa {v}", "en": ", about {v} in total"}
META["door_buyers_h"] = {"de": "Auftraggeber finden", "fr": "Trouver un acheteur public", "it": "Trova un ente pubblico",
                         "en": "Find a public buyer"}
META["finder_ph_b"] = {"de": "z. B. Stadt Zürich", "fr": "p. ex. Ville de Genève", "it": "ad es. Città di Lugano",
                       "en": "e.g. City of Zurich"}
META["finder_sub_b"] = {
    "de": "{n} Auftraggeber haben mindestens einen Auftrag vergeben; {k} davon haben eine eigene Seite.",
    "fr": "{n} acheteurs publics ont attribué au moins un marché ; {k} ont leur propre page.",
    "it": "{n} enti pubblici hanno aggiudicato almeno un appalto; {k} hanno una pagina propria.",
    "en": "{n} public buyers have awarded at least one contract; {k} of them have a page of their own.",
}
META["az_other"] = {"de": "Andere", "fr": "Autres", "it": "Altri", "en": "Other"}
META["nf_eyebrow"] = {"de": "Fehler 404", "fr": "Erreur 404", "it": "Errore 404", "en": "Error 404"}
# (the check page's 'no e-mail?' line, "abo_resend", is at the end of the file, in the 'strictly necessary' pass)
META["abo_recap_h"] = {"de": "So geht es weiter", "fr": "La suite", "it": "I prossimi passi", "en": "What happens next"}
META["abo_step1"] = {"de": "Den Bestätigungslink in der E-Mail anklicken.",
                     "fr": "Cliquer sur le lien de confirmation de l’e-mail.",
                     "it": "Cliccare sul link di conferma nell’e-mail.",
                     "en": "Click the confirmation link in the email."}
META["abo_step2"] = {
    "de": "An jedem Werktag, an dem neue Ausschreibungen zu Ihrer Auswahl erscheinen, erhalten Sie eine E-Mail.",
    "fr": "Chaque jour ouvrable où de nouveaux appels d’offres correspondent à votre sélection, vous recevez un "
          "e-mail.",
    "it": "Nei giorni feriali in cui escono nuovi bandi adatti alla scelta fatta arriva un’e-mail.",
    "en": "On every day from Monday to Saturday when new tenders matching your selection appear, you get an "
          "email.",
}
META["abo_step3"] = {"de": "Abmelden können Sie sich jederzeit über den Link am Ende jeder E-Mail.",
                     "fr": "Vous pouvez vous désabonner à tout moment par le lien au bas de chaque e-mail.",
                     "it": "Per cancellarsi basta il link in fondo a ogni e-mail, in qualsiasi momento.",
                     "en": "You can unsubscribe at any time with the link at the bottom of every email."}
META["abo_form_nojs"] = {
    "de": "Die Auswahl nach Kanton und Branche braucht JavaScript. Ohne JavaScript gilt das Abo für die ganze "
          "Schweiz und alle Branchen.",
    "fr": "Pour choisir des cantons et des secteurs, il faut JavaScript. Sans lui, l’abonnement couvre toute la "
          "Suisse et tous les secteurs.",
    "it": "Per scegliere cantoni e settori serve JavaScript. Senza, ricevi i bandi di tutta la Svizzera e di tutti "
          "i settori.",
    "en": "Choosing cantons and sectors needs JavaScript. Without it, the subscription covers all of Switzerland and "
          "every sector.",
}
META["abo_bfilter"] = {"de": "Branche suchen", "fr": "Chercher un secteur", "it": "Cerca un settore",
                       "en": "Find a sector"}
META["abo_bfilter_ph"] = {"de": "z. B. Reinigung", "fr": "p. ex. nettoyage", "it": "ad es. pulizia",
                          "en": "e.g. cleaning"}
IDX["cut_firms"] = {"de": "die {k} mit den meisten Aufträgen, von {n}",
                    "fr": "les {k} qui ont remporté le plus de marchés, sur {n}",
                    "it": "le {k} che hanno vinto più appalti, su {n}", "en": "the {k} that won the most contracts, of {n}"}
IDX["cut_buyers"] = {"de": "die {k} mit den meisten vergebenen Aufträgen, von {n}",
                     "fr": "les {k} qui ont attribué le plus de marchés, sur {n}",
                     "it": "i {k} che hanno aggiudicato più appalti, su {n}",
                     "en": "the {k} that awarded the most contracts, of {n}"}
IDX["cut_newest"] = {"de": "die {k} neuesten von {n}", "fr": "les {k} plus récents sur {n}",
                     "it": "i {k} più recenti su {n}", "en": "the {k} most recent of {n}"}
# the CSV links say what they download (fix round 1), in plain words since 22.10.2026
IDX["csv_all_n"] = {"de": "Alle {n} Aufträge als CSV-Datei", "fr": "Les {n} marchés en fichier CSV",
                    "it": "Tutti i {n} appalti in un file CSV", "en": "All {n} contracts as a CSV file"}
IDX["csv_canton"] = {"de": "Vergebene Aufträge im Kanton {name} (CSV)", "fr": "Marchés attribués du canton {of} (CSV)",
                     "it": "Appalti aggiudicati del Canton {name} (CSV)",
                     "en": "Contracts awarded in the canton of {name} (CSV)"}
IDX["csv_buyer"] = {"de": "Vergebene Aufträge von {name} (CSV)", "fr": "Marchés attribués par {name} (CSV)",
                    "it": "Appalti aggiudicati da {name} (CSV)", "en": "Contracts awarded by {name} (CSV)"}
IDX["csv_company"] = {"de": "Aufträge an {name} (CSV)", "fr": "Marchés remportés par {name} (CSV)",
                      "it": "Appalti vinti da {name} (CSV)", "en": "Contracts won by {name} (CSV)"}
IDX["csv_nocant"] = {"de": "Aufträge ohne Kanton (CSV)", "fr": "Marchés sans canton (CSV)",
                     "it": "Appalti senza cantone (CSV)", "en": "Contracts without a canton (CSV)"}
IDX["chart_csv"] = {"de": "Daten der Grafik (CSV)", "fr": "Données du graphique (CSV)", "it": "Dati del grafico (CSV)",
                    "en": "Chart data (CSV)"}
# (the canton page's buyer's-seat share, "fb_share" and "fb_share_one", is at the end of the file)
IDX["div_once"] = {"de": "{k} der {f} Firmen haben in dieser Branche genau einen Auftrag erhalten.",
                   "fr": "{k} des {f} entreprises ont remporté un seul marché dans ce secteur.",
                   "it": "{k} delle {f} aziende hanno vinto un solo appalto in questo settore.",
                   "en": "{k} of the {f} companies won exactly one contract in this sector."}
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
OUTLIER_WHAT = {"de": ("Lose", "Aufträge"), "fr": ("lots", "marchés"), "it": ("lotti", "appalti"),
                "en": ("lots", "contracts")}
# the lists' filter bar (liste.js), the zero-result suggestions (liste.js, suche.js), the panel's toggle (kb.js),
# the alert form's summary and Branche filter (abo.js)
JS["f_toggle"] = {"de": "Filter", "fr": "Filtres", "it": "Filtri", "en": "Filters"}
JS["f_active"] = {"de": "({n} aktiv)", "fr": "({n} actifs)", "it": "({n} attivi)", "en": "({n} active)"}
JS["f_active_1"] = {"de": "(1 aktiv)", "fr": "(1 actif)", "it": "(1 attivo)", "en": "(1 active)"}
JS["f_sort"] = {"de": "Reihenfolge", "fr": "Ordre", "it": "Ordine", "en": "Order"}
JS["f_sort_dl"] = {"de": "Nächste Frist zuerst", "fr": "Délai le plus proche d’abord",
                   "it": "Scadenza più vicina prima", "en": "Nearest deadline first"}
JS["f_sort_new"] = {"de": "Neueste zuerst", "fr": "Les plus récents d’abord", "it": "Più recenti prima",
                    "en": "Newest first"}
JS["f_new"] = {"de": "Nur neue vom {d}", "fr": "Seulement les nouveaux du {d}", "it": "Solo i nuovi del {d}",
               "en": "Only new on {d}"}
JS["f_abo_kw"] = {"de": "Per E-Mail schicken wir Ausschreibungen nach Kanton und Branche – Stichwörter gelten nur hier.",
                  "fr": "Par e-mail, nous envoyons les appels d’offres par canton et par secteur : les mots-clés ne "
                        "servent qu’ici.",
                  "it": "Via e-mail ti mandiamo i bandi per cantone e settore: le parole chiave valgono solo qui.",
                  "en": "By email we send tenders by canton and sector – keywords only work here."}
JS["f_first"] = {"de": "Die {k}, deren Frist zuerst abläuft, von {m} offenen Ausschreibungen",
                 "fr": "Les {k} qui expirent en premier, sur {m} appels d’offres en cours",
                 "it": "I {k} che scadono prima, su {m} bandi aperti",
                 "en": "The {k} that close first, of {m} open tenders"}
JS["z_h"] = {"de": "Vorschläge:", "fr": "Suggestions :", "it": "Suggerimenti:", "en": "Suggestions:"}
# fix round 3: the divider before the matches of a part of a word, and the alert link's note when a keyword names a Branche
JS["tier_w"] = {"de": "Weitere Treffer (Wortteil)", "fr": "Autres résultats (partie de mot)",
                "it": "Altri risultati (parte di parola)", "en": "More matches (part of a word)"}
# fix round 5: the same divider when no match is whole ('Weitere' with nothing above it), in the lists and the search
JS["tier_a"] = {"de": "Treffer als Wortteil", "fr": "Résultats par partie de mot", "it": "Risultati per parte di parola",
                "en": "Matches on part of a word"}
JS["f_abo_kwb"] = {"de": "Per E-Mail: die Branche «{b}», ohne Stichwörter.",
                   "fr": "Par e-mail : le secteur « {b} », sans mots-clés.",
                   "it": "Via e-mail ricevi tutto il settore «{b}»: le parole chiave valgono solo qui.",
                   "en": "By email: the “{b}” sector, without keywords."}
JS["z_drop"] = {"de": "ohne «{t}»: {n}", "fr": "sans « {t} » : {n}", "it": "senza «{t}»: {n}",
                "en": "without “{t}”: {n}"}
JS["z_near"] = {"de": "{c}: {n}", "fr": "{c} : {n}", "it": "{c}: {n}", "en": "{c}: {n}"}
# fix round 6: no result, the query with a word one letter away (the open tenders' words)
JS["z_dym"] = {"de": "Meinten Sie «{q}»?", "fr": "Vouliez-vous dire « {q} » ?", "it": "Forse cercavi «{q}»?",
               "en": "Did you mean “{q}”?"}
JS["z_abo"] = {"de": "Neue Ausschreibungen dieser Auswahl gratis per E-Mail",
               "fr": "Recevoir gratuitement par e-mail les nouveaux appels d’offres de cette sélection",
               "it": "Ricevi gratis via e-mail i nuovi bandi di questa selezione",
               "en": "Get new tenders for this selection by email – free"}
JS["kb_fb"] = {"de": "{k} dieser Aufträge ({p}) nennen keinen Ort und zählen hier, weil der Auftraggeber hier seinen "
                     "Sitz hat.",
               "fr": "{k} de ces marchés ({p}) n’indiquent aucun lieu et comptent ici, où l’acheteur public a son "
                     "siège.",
               "it": "{k} di questi appalti ({p}) non indicano il luogo e contano qui, dove ha sede l’ente "
                     "pubblico.",
               "en": "{k} of these contracts ({p}) name no place and count here, where the public buyer is based."}
JS["kb_fbx"] = {"de": "Ohne diese Aufträge", "fr": "Sans ces marchés", "it": "Senza questi appalti",
                "en": "Without these contracts"}
JS["sum_sel"] = {"de": "Sie abonnieren: {s}", "fr": "Vous vous abonnez à : {s}", "it": "Ti iscrivi a: {s}",
                 "en": "You’re subscribing to: {s}"}
JS["all_ch"] = {"de": "ganze Schweiz", "fr": "toute la Suisse", "it": "tutta la Svizzera", "en": "all of Switzerland"}
JS["all_b"] = {"de": "alle Branchen", "fr": "tous les secteurs", "it": "tutti i settori", "en": "all sectors"}
JS["bf_none"] = {"de": "Keine Branche passt zu «{q}».", "fr": "Aucun secteur ne correspond à « {q} ».",
                 "it": "Nessun settore trovato per «{q}».", "en": "No sector matches “{q}”."}


# ---------------------------------------------------------------- fix round 2 (20.10.2026)
# The copy audit of 15.10 (audit3/copy/fixes.md): the home's alarm band said the same thing three times and printed
# its number twice; an expired tender's alert box made its promise twice; a company page without a CHF sum said
# nothing about why; small counts at the start of a sentence, and the thresholds on the Über page, in words.
# The Italian answers the owner's example of a stilted line (23.10.2026, «Cantoni e settori a scelta: … per lo più in
# mattinata. Senza account.»); under the heading «Ricevi i nuovi bandi via e-mail» it does not repeat «via e-mail».
# The e-mail goes out only on a day with matching new tenders.
META["alarm_sub"] = {
    "de": "Wählen Sie Kantone und Branchen: Wir schicken Ihnen die neuen Ausschreibungen per E-Mail, meist am "
          "Vormittag. Ein Konto brauchen Sie nicht.",
    "fr": "Choisissez vos cantons et vos secteurs : nous vous envoyons les nouveaux appels d’offres par e-mail, "
          "en général le matin. Pas besoin de compte.",
    "it": "Scegli cantoni e settori: ti scriviamo quando escono bandi nuovi, di solito al mattino. Non serve "
          "registrarsi.",
    "en": "Choose your cantons and sectors, and we’ll email you the new tenders, usually in the morning. "
          "No account needed.",
}
# under the big number of the alarm band: the number is not said twice
META["alarm_since"] = {"de": "neue Ausschreibungen am {d}", "fr": "nouveaux appels d’offres le {d}",
                       "it": "nuovi bandi il {d}", "en": "new tenders on {d}"}
META["alarm_since_one"] = {"de": "neue Ausschreibung am {d}", "fr": "nouvel appel d’offres le {d}",
                           "it": "nuovo bando il {d}", "en": "new tender on {d}"}
# an expired tender's alert box: after 'Frist verpasst? …' only what the alert would cover
META["alert_scope_div"] = {"de": "Branche «{sector}»", "fr": "Secteur « {sector} »", "it": "Settore «{sector}»",
                           "en": "“{sector}” sector"}
META["alert_scope_alldiv"] = {"de": "Alle Branchen", "fr": "Tous les secteurs", "it": "Tutti i settori",
                              "en": "All sectors"}
META["alert_scope_k"] = {"de": "Kanton {name}", "fr": "canton {of}", "it": "Canton {name}", "en": "canton of {name}"}
META["alert_scope_ch"] = {"de": "ganze Schweiz", "fr": "toute la Suisse", "it": "tutta la Svizzera",
                          "en": "all of Switzerland"}
# a company page whose awards give no CHF sum (all unit rates, awards to several firms …): the tile says why
IDX["nosum"] = {"de": "Keine Summe in CHF: {why}.", "fr": "Pas de total en CHF : {why}.",
                "it": "Nessun totale in CHF: {why}.", "en": "No CHF total: {why}."}
IDX["nosum_rates"] = {"de": "{k} vermutliche Einheitspreise", "fr": "{k} prix probablement unitaires",
                      "it": "{k} probabili prezzi unitari", "en": "{k} probable unit rates"}
IDX["nosum_rates_one"] = {"de": "ein vermutlicher Einheitspreis", "fr": "un prix probablement unitaire",
                          "it": "un probabile prezzo unitario", "en": "one probable unit rate"}
IDX["nosum_joint"] = {"de": "{k} Aufträge an mehrere Firmen", "fr": "{k} marchés à plusieurs entreprises",
                      "it": "{k} appalti a più aziende", "en": "{k} contracts to several companies"}
IDX["nosum_joint_one"] = {"de": "ein Auftrag an mehrere Firmen", "fr": "un marché à plusieurs entreprises",
                          "it": "un appalto a più aziende", "en": "one contract to several companies"}
IDX["nosum_fx"] = {"de": "{k} Beträge in Fremdwährung", "fr": "{k} montants en devise étrangère",
                   "it": "{k} importi in valuta estera", "en": "{k} amounts in a foreign currency"}
IDX["nosum_fx_one"] = {"de": "ein Betrag in Fremdwährung", "fr": "un montant en devise étrangère",
                       "it": "un importo in valuta estera", "en": "one amount in a foreign currency"}
IDX["nosum_none"] = {"de": "{k} Aufträge ohne publizierten Betrag", "fr": "{k} marchés sans montant publié",
                     "it": "{k} appalti senza importo pubblicato", "en": "{k} contracts without a published amount"}
IDX["nosum_none_one"] = {"de": "ein Auftrag ohne publizierten Betrag", "fr": "un marché sans montant publié",
                         "it": "un appalto senza importo pubblicato", "en": "one contract without a published amount"}
AND = {"de": " und ", "fr": " et ", "it": " e ", "en": " and "}
# the canton overview's awards without a canton, one of them
IDX["nocant_lead_one"] = {
    "de": "Ein Auftrag nennt weder einen Ort noch einen Auftraggeber mit Kanton. Alle Kantone zusammen und dieser "
          "Auftrag ergeben die {total} der Startseite.",
    "fr": "Un marché n’indique ni lieu ni acheteur public avec canton. Tous les cantons et ce marché donnent "
          "ensemble les {total} de la page d’accueil.",
    "it": "Un appalto non indica né un luogo né un ente pubblico con cantone. Con questo, la somma dei cantoni dà "
          "i {total} della home.",
    "en": "One contract names neither a place nor a public buyer with a canton. All cantons together and this "
          "contract make up the {total} on the home page.",
}
for _l, _x in (("de", "Ein Auftrag nennt weder einen Ort noch einen Auftraggeber mit Kanton. Er zählt zu keinem Kanton; "
                      "die Kantonsübersicht führt ihn gesondert auf."),
               ("fr", "Un marché n’indique ni lieu ni acheteur public avec canton : il ne compte dans aucun canton, "
                      "et l’aperçu des cantons le présente à part."),
               ("it", "Un appalto non indica né un luogo né un ente pubblico con cantone: non conta in nessun "
                      "cantone e la pagina dei cantoni lo elenca a parte."),
               ("en", "One contract names neither a place nor a public buyer with a canton; it counts in no "
                      "canton, and the canton overview lists it separately.")):
    UEBER[_l]["nocant_one"] = _x
# small numbers in words (a count that opens a sentence, the thresholds on the Über page; British house style
# spells out numbers under ten): genera.spelled()
NUM_WORDS = {
    "de": ("null", "ein", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf"),
    "fr": ("zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze"),
    "it": ("zero", "uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto", "nove", "dieci", "undici", "dodici"),
    "en": ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"),
}


# ------------------------------------------------- strictly necessary (owner, 23.10.2026)
# Every page asked: is each element needed, would a reader with ADHD take it in at a glance? Short sentences (20 words at
# most), one or two lines of lead, no number said twice, the explanations on the about page or behind a 'more'. The
# masthead's 'Unabhängig · nicht amtlich' is gone (its T["indep"] with it); the simap notice and its translation stay in
# the footer.
# the footer's last link (the minimal footer: the notice, the source, one date, the about and legal pages, the contact)
T["contact"] = {"de": "Kontakt", "fr": "Contact", "it": "Contatto", "en": "Contact"}
# the home's one line of trust over the question: the source and the page's one date (it elides like the footer's line)
META["home_source"] = {"de": "Daten von simap.ch · aktualisiert am {d}", "fr": "Données de simap.ch · mis à jour le {d}",
                       "it": "Dati di simap.ch · aggiornato al {d}", "en": "Data from simap.ch · updated {d}"}
# the home's lead, one line (it was two paragraphs: who the site is for, then what it holds). Natural-voice pass
# (owner, 23.10.2026): it answers the question of the H1 right above it ('li' / 'sie' / 'les' / 'them' are its contracts)
PROSE["lead"] = {
    "de": "Hier sehen Sie, wer sie seit August 2024 gewonnen hat – Firma für Firma. Dazu die offenen Ausschreibungen.",
    "fr": "Découvrez qui les a remportés depuis août 2024, entreprise par entreprise – et trouvez les appels d'offres "
          "en cours.",
    "it": "Qui trovi tutti gli appalti aggiudicati da agosto 2024, azienda per azienda, e i bandi ancora aperti.",
    "en": "See who has won them since August 2024, company by company – and find the tenders open now.",
}
META["door_open_sub"] = {"de": "Nach Frist, Kanton und Branche.", "fr": "Par délai, canton et secteur.",
                         "it": "In ordine di scadenza, per cantone e settore.", "en": "By deadline, canton and sector."}
# the leads of the company, buyer, canton and Branche pages say what the page holds; their numbers are the figures'
META["company_lead"] = {"de": "Hier finden Sie die öffentlichen Aufträge, die diese Firma gewonnen hat{span} – laut "
                              "simap.ch.",
                        "fr": "Voici les marchés publics remportés par cette entreprise{span}, selon simap.ch.",
                        "it": "Qui trovi gli appalti pubblici vinti da questa azienda{span}, secondo simap.ch.",
                        "en": "Here are the public contracts this company has won{span}, according to simap.ch."}
META["buyer_lead"] = {"de": "Hier finden Sie die Aufträge, die dieser Auftraggeber vergeben hat – laut simap.ch.",
                      "fr": "Voici les marchés attribués par cet acheteur public, selon simap.ch.",
                      "it": "Qui trovi gli appalti aggiudicati da questo ente pubblico, secondo simap.ch.",
                      "en": "Here are the contracts this public buyer has awarded, according to simap.ch."}
META["canton_lead"] = {
    "de": "Hier sehen Sie, wer im Kanton {name} öffentliche Aufträge gewonnen hat{span} – laut simap.ch.",
    "fr": "Voici qui a remporté les marchés publics dans le canton {of}{span}, selon simap.ch.",
    "it": "Qui vedi chi ha vinto gli appalti pubblici nel Canton {name}{span}, secondo simap.ch.",
    "en": "Here you can see who won public contracts in the canton of {name}{span}, according to simap.ch.",
}
META["canton_lead_one"] = dict(META["canton_lead"])
IDX["fb_share"] = {
    "de": "{k} Aufträge ({p}) nennen keinen Ort und zählen hier, weil der Auftraggeber hier seinen Sitz hat.",
    "fr": "{k} marchés ({p}) n'indiquent aucun lieu et comptent ici, où l'acheteur public a son siège.",
    "it": "{k} appalti ({p}) non indicano il luogo e contano qui, dove l'ente pubblico ha sede.",
    "en": "{k} contracts ({p}) name no place and count here, where the public buyer is based.",
}
IDX["fb_share_one"] = {
    "de": "Ein Auftrag ({p}) nennt keinen Ort und zählt hier, weil der Auftraggeber hier seinen Sitz hat.",
    "fr": "Un marché ({p}) n'indique aucun lieu et compte ici, où l'acheteur public a son siège.",
    "it": "Un appalto ({p}) non indica il luogo e conta qui, dove l'ente pubblico ha sede.",
    "en": "One contract ({p}) names no place and counts here, where the public buyer is based.",
}
META["div_lead"] = {"de": "Hier finden Sie die vergebenen Aufträge dieser Branche – laut simap.ch.",
                    "fr": "Voici les marchés attribués dans ce secteur, selon simap.ch.",
                    "it": "Qui trovi gli appalti aggiudicati in questo settore, secondo simap.ch.",
                    "en": "Here are the contracts awarded in this sector, according to simap.ch."}
# the sectors panel: what a sector is, the about page says ('Branchen und Kategorien (CPV)')
IDX["div_lede_top"] = {"de": "Die häufigsten Branchen: {k} von {total}.", "fr": "Les secteurs les plus fréquents : {k} sur {total}.",
                       "it": "I settori più frequenti: {k} su {total}.", "en": "The most frequent sectors: {k} of {total}."}
IDX["div_lede_all"] = {"de": "", "fr": "", "it": "", "en": ""}
# the notes under the charts: what changes how they read, nothing more (the archive's start is the about page's, the
# date the page's one date)
IDX["mc_note_start"] = {"de": "Schraffierte Säulen ({span}): unvollständig erfasste Monate am Anfang des Archivs.",
                        "fr": "Colonnes hachurées ({span}) : mois incomplets du début des archives.",
                        "it": "Colonne tratteggiate ({span}): mesi incompleti all'inizio dell'archivio.",
                        "en": "Striped columns ({span}): incomplete months at the start of the archive."}
IDX["mc_note_start_one"] = {"de": "Schraffierte Säule ({m}): unvollständig erfasster Monat am Anfang des Archivs.",
                            "fr": "Colonne hachurée ({m}) : mois incomplet du début des archives.",
                            "it": "Colonna tratteggiata ({m}): mese incompleto all'inizio dell'archivio.",
                            "en": "Striped column ({m}): incomplete month at the start of the archive."}
IDX["mc_note_end"] = {"de": "Schraffierte letzte Säule: laufender Monat.", "fr": "Dernière colonne hachurée : mois en cours.",
                      "it": "Ultima colonna tratteggiata: mese in corso.", "en": "Striped last column: current month."}
IDX["mc_note_end_zero"] = {"de": "Laufender Monat ({m}): bisher kein vergebener Auftrag.",
                           "fr": "Mois en cours ({m}) : aucun marché attribué pour l'instant.",
                           "it": "Mese in corso ({m}): finora nessun appalto aggiudicato.",
                           "en": "Current month ({m}): no contracts awarded so far."}
# the notes that change how a list or a total reads, short (what a CPV code or a unit rate is: the about page); said by
# the one who picked or counted (natural-voice pass, 23.10.2026)
PROSE["matched_note"] = {
    "de": "Wir wählen sie nach dem CPV-Code der bisherigen Aufträge aus: derselbe oder ein ähnlicher.",
    "fr": "Nous les choisissons d'après le code CPV des marchés déjà remportés : le même ou un code proche.",
    "it": "Li scegliamo in base al codice CPV degli appalti già vinti: lo stesso o uno simile.",
    "en": "We pick them by the CPV code of the contracts already won: the same one or a related one.",
}
IDX["similar_note"] = {"de": "Branche «{sector}», Kanton {name}: die ähnlichsten zuerst.",
                       "fr": "Secteur « {sector} », canton {of} : les plus proches d'abord.",
                       "it": "Settore «{sector}», Canton {name}: prima i più simili.",
                       "en": "“{sector}” sector, canton of {name}: closest first."}
IDX["joint_note"] = {"de": "Die {k} Aufträge an mehrere Firmen rechnen wir nicht in die Summen ein.",
                     "fr": "Nous ne comptons pas dans les totaux les {k} marchés attribués à plusieurs entreprises.",
                     "it": "Nei totali non contiamo i {k} appalti andati a più aziende.",
                     "en": "Totals exclude the {k} contracts awarded to several companies."}
IDX["joint_note_one"] = {"de": "Den Auftrag an mehrere Firmen rechnen wir nicht in die Summen ein.",
                         "fr": "Nous ne comptons pas dans les totaux le marché attribué à plusieurs entreprises.",
                         "it": "Nei totali non contiamo l'appalto andato a più aziende.",
                         "en": "Totals exclude the contract awarded to several companies."}
IDX["rates_note"] = {"de": "{k} vermutliche Einheitspreise rechnen wir weder in die Summen noch in den Median ein.",
                     "fr": "Nous ne comptons pas {k} prix probablement unitaires dans les totaux ni dans la médiane.",
                     "it": "Nei totali e nella mediana non contiamo {k} probabili prezzi unitari.",
                     "en": "Totals and the median exclude {k} probable unit rates."}
IDX["rates_note_one"] = {"de": "Einen vermutlichen Einheitspreis rechnen wir weder in die Summen noch in den Median ein.",
                         "fr": "Nous ne comptons pas un prix probablement unitaire dans les totaux ni dans la médiane.",
                         "it": "Nei totali e nella mediana non contiamo un probabile prezzo unitario.",
                         "en": "Totals and the median exclude one probable unit rate."}
# the search page's directories, behind a 'more': its summary says what opens
META["search_dirs"] = {"de": "Verzeichnisse von A bis Z", "fr": "Répertoires de A à Z", "it": "Elenchi dalla A alla Z",
                       "en": "Directories from A to Z"}
META["search_lead"] = {
    "de": "Firmen, Auftraggeber, Ausschreibungen, Branchen und Kantone: Mit «Reinigung» finden Sie auch «nettoyage».",
    "fr": "Entreprises, acheteurs publics, appels d'offres, secteurs et cantons : avec « nettoyage », vous trouvez aussi "
          "« Reinigung ».",
    "it": "Aziende, enti pubblici, bandi, settori e cantoni: se scrivi «pulizia», trovi anche «Reinigung».",
    "en": "Companies, public buyers, tenders, sectors and cantons: type “cleaning” and you also find “Reinigung”.",
}
# the e-mail service: one line and a link over the form, two short lines of consent under the button. The Italian
# is the natural-voice line agreed in the review of 23.10.2026: «Scegli cantoni e settori: ti mandiamo i nuovi bandi
# via e-mail.»
META["abo_lead"] = {
    "de": "Wählen Sie Kantone und Branchen: Wir schicken Ihnen die neuen Ausschreibungen per E-Mail. Gratis und ohne "
          "Konto.",
    "fr": "Choisissez vos cantons et vos secteurs : nous vous envoyons les nouveaux appels d'offres par e-mail. C'est "
          "gratuit, sans compte.",
    "it": "Scegli cantoni e settori: ti mandiamo i nuovi bandi via e-mail. È gratis e non serve registrarsi.",
    "en": "Choose your cantons and sectors, and we’ll email you the new tenders. Free, no account needed.",
}
META["abo_form_consent"] = {
    "de": "Zuerst schicken wir Ihnen eine E-Mail mit einem Bestätigungslink. Jede E-Mail enthält einen Link zum Abmelden. "
          "Der Versand läuft über Brevo (EU).",
    "fr": "Nous vous envoyons d'abord un e-mail avec un lien de confirmation. Chaque e-mail contient un lien pour vous "
          "désabonner. L'envoi passe par Brevo (UE).",
    "it": "Prima ti mandiamo un'e-mail con un link di conferma. In ogni e-mail trovi il link per annullare l'iscrizione. "
          "L'invio passa da Brevo (UE).",
    "en": "First we send you an email with a confirmation link. Every email has an unsubscribe link. We send through "
          "Brevo (EU).",
}
META["abo_rss_h2"] = {"de": "RSS-Feeds (ohne Anmeldung)", "fr": "Flux RSS (sans inscription)",
                      "it": "Feed RSS (senza iscrizione)", "en": "RSS feeds (no sign-up)"}
JS["pv"] = {"de": "≈ {w} neue Ausschreibungen pro Woche", "fr": "≈ {w} nouveaux appels d'offres par semaine",
            "it": "≈ {w} nuovi bandi alla settimana", "en": "≈ {w} new tenders a week"}
JS["pv_lt"] = {"de": "weniger als eine neue Ausschreibung pro Woche", "fr": "moins d'un nouvel appel d'offres par semaine",
               "it": "meno di un nuovo bando alla settimana", "en": "fewer than one new tender a week"}
# the two pages Brevo sends people to
META["abo_resend"] = {
    "de": "Keine E-Mail nach 15 Minuten? Prüfen Sie den Spam-Ordner oder melden Sie sich noch einmal an.",
    "fr": "Pas d'e-mail après 15 minutes ? Vérifiez vos courriers indésirables ou inscrivez-vous à nouveau.",
    "it": "Nessuna e-mail dopo 15 minuti? Controlla lo spam o iscriviti di nuovo.",
    "en": "No email after 15 minutes? Check your spam folder or sign up again.",
}
META["abo_ok"] = {"de": "Ihr Abo ist aktiv.", "fr": "Votre abonnement est actif.", "it": "La tua iscrizione è attiva.",
                  "en": "Your subscription is active."}
# only on a day with matching new tenders, usually in the morning (the sender's facts)
META["abo_when"] = {
    "de": "Wir schreiben Ihnen an Werktagen, an denen passende neue Ausschreibungen erscheinen – meist am Vormittag.",
    "fr": "Nous vous écrivons les jours ouvrables où paraissent de nouveaux appels d'offres pour vous, en général le "
          "matin.",
    "it": "Ti scriviamo nei giorni feriali in cui escono nuovi bandi per te, di solito al mattino.",
    "en": "We email you on days with new matching tenders, usually in the morning.",
}
META["abo_change"] = {
    "de": "Auswahl ändern? Melden Sie sich über den Link am Ende einer E-Mail ab und abonnieren Sie dann neu.",
    "fr": "Pour changer de sélection, désabonnez-vous avec le lien au bas d'un e-mail, puis abonnez-vous à nouveau.",
    "it": "Vuoi cambiare cantoni o settori? Annulla l'iscrizione con il link in fondo a un'e-mail, poi iscriviti di "
          "nuovo.",
    "en": "To change your selection, unsubscribe with the link at the bottom of an email, then subscribe again.",
}
META["nf_text"] = {
    "de": "Diese Seite gibt es nicht oder nicht mehr. Abgelaufene Ausschreibungen bleiben {days} Tage online.",
    "fr": "Cette page n'existe pas, ou n'existe plus. Les appels d'offres expirés restent en ligne pendant {days} jours.",
    "it": "Questa pagina non esiste, o non esiste più. I bandi scaduti restano online per {days} giorni.",
    "en": "This page does not exist, or no longer does. Expired tenders stay online for {days} days.",
}
# the footer's line on the language of the titles, moved to the about page (its source section already said the first
# half: titles appear as published, in the publication's language)
for _l, _x in (("de", " Nicht jede Publikation liegt in allen Landessprachen vor."),
               ("fr", " Toutes les publications ne sont pas disponibles dans toutes les langues."),
               ("it", " Non tutte le pubblicazioni sono disponibili in tutte le lingue."),
               ("en", " Only some are available in English.")):
    for _sec in UEBER[_l]["sections"]:
        if _sec[0] == "quelle":
            _sec[2][1] += _x


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
               "nocant", "nocant_zero", "nocant_one"):
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
