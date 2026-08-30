import pathlib
p = pathlib.Path("genera.py"); s = p.read_text()

s = s.replace('''def _m(key: str, **kw) -> str:
    return lingue.m(key, LANG, **kw)''',
'''def _m(key: str, **kw) -> str:
    return lingue.m(key, LANG, **kw)


class _Idx:
    def __getattr__(self, key: str) -> str:
        return lingue.i(key, LANG)


_i = _Idx()


def _if(key: str, **kw) -> str:
    return lingue.i(key, LANG, **kw)''')

R = [
 # --- gare aperte ---
 ('"<h1>Offene Ausschreibungen</h1>"', 'f"<h1>{e(_p.open_tenders_h1)}</h1>"'),
 ('''f'<p class="sum">{len(opens)} Ausschreibungen mit noch offener Eingabefrist, '
         "publiziert von Bund, Kantonen und Gemeinden auf simap.ch.</p></div>"''',
  '''f'<p class="sum">' + e(_m("open_lead", n=len(opens))) + "</p></div>"'''),
 ('''        "Offene Ausschreibungen Schweiz — laufende öffentliche Aufträge",
        f"{len(opens)} laufende Ausschreibungen mit offener Eingabefrist aus dem "
        "öffentlichen Beschaffungswesen der Schweiz, nach Frist geordnet.",''',
  '''        _m("open_title"), _m("open_desc", n=len(opens)),'''),
 ('''f"<h1>Offene Ausschreibungen {e(name)}</h1>"''',
  '''f'<h1>{e(_m("open_canton_title", name=name))}</h1>\''''),
 ('''f'<p class="sum">{len(rows)} Ausschreibungen mit offener Eingabefrist im '
             f"Kanton {e(name)}.</p></div>"''',
  '''f'<p class="sum">'
             + e(_m("open_canton_desc", n=len(rows), name=name)) + "</p></div>"'''),
 ('''            fit_title(f"Offene Ausschreibungen {name}", " — simap"),
            f"{len(rows)} laufende Ausschreibungen im Kanton {name} mit offener "
            "Eingabefrist, nach Frist geordnet.",''',
  '''            fit_title(_m("open_canton_title", name=name), " — simap"),
            _m("open_canton_desc", n=len(rows), name=name),'''),
 ('''f'<a class="tag" href="/{LANG}/kanton/{e(code)}/">Vergebene Aufträge {e(code)}</a>'
             f'<a class="tag" href="/{LANG}/ausschreibungen/">Alle offenen Ausschreibungen</a></div>\'''',
  '''f'<a class="tag" href="/{LANG}/kanton/{e(code)}/">{e(_if("awarded_in", c=code))}</a>'
             f'<a class="tag" href="/{LANG}/ausschreibungen/">{e(_i.all_open)}</a></div>\''''),
 # --- indici ---
 ('''    build_index("/unternehmen/", "Unternehmen", "Unternehmen im Register",
                "Alle Unternehmen mit mindestens zwei publizierten Zuschlägen, alphabetisch.",
                [(sl, p["name"], p["n"]) for sl, p in pages.items()],
                "Unternehmen mit öffentlichen Aufträgen — Verzeichnis",
                f"Verzeichnis von {len(pages)} Unternehmen mit publizierten Zuschlägen "
                "aus dem öffentlichen Beschaffungswesen der Schweiz.")''',
  '''    build_index("/unternehmen/", _.companies, _i.companies_h1, _i.companies_lead,
                [(sl, p["name"], p["n"]) for sl, p in pages.items()],
                _i.companies_title, _if("companies_desc", n=len(pages)))'''),
 ('''    build_index("/auftraggeber/", "Auftraggeber", "Auftraggeber",
                "Beschaffungsstellen von Bund, Kantonen und Gemeinden, alphabetisch.",
                [(sl, n, k) for sl, n, k in buyers],
                "Auftraggeber im öffentlichen Beschaffungswesen — Verzeichnis",
                f"Verzeichnis von {len(buyers)} Beschaffungsstellen und den Aufträgen, "
                "die sie auf simap.ch publiziert haben.")''',
  '''    build_index("/auftraggeber/", _.buyers, _i.buyers_h1, _i.buyers_lead,
                [(sl, n, k) for sl, n, k in buyers],
                _i.buyers_title, _if("buyers_desc", n=len(buyers)))'''),
 ('''    build_index("/kanton/", "Kantone", "Kantone",
                "Publizierte Zuschläge nach Kanton der Auftragsausführung.",
                [(c, CANTONS.get(c, c), len(r)) for c, r in cant_list],
                "Öffentliche Aufträge nach Kanton — Übersicht",
                "Publizierte Zuschläge aus dem öffentlichen Beschaffungswesen der Schweiz, "
                "nach Kanton geordnet.")''',
  '''    build_index("/kanton/", _.cantons, _.cantons, _i.cantons_lead,
                [(c, CANTONS.get(c, c), len(r)) for c, r in cant_list],
                _i.cantons_title, _i.cantons_desc)'''),
 ('''    build_index("/bereich/", "Bereiche", "Beschaffungsbereiche",
                "Publizierte Zuschläge nach CPV-Bereich.",
                [(c, next((de(a, "cpvLabel") or a.get("cpvLabel") or c for a in r
                           if de(a, "cpvLabel") or a.get("cpvLabel")), c), len(r))
                 for c, r in cpv_list],
                "Öffentliche Aufträge nach Bereich — CPV-Übersicht",
                "Publizierte Zuschläge nach Beschaffungsbereich (CPV), mit den Unternehmen, "
                "die sie erhalten haben.")''',
  '''    build_index("/bereich/", _.sectors, _i.sectors_h1, _i.sectors_lead,
                [(c, next((de(a, "cpvLabel") or a.get("cpvLabel") or c for a in r
                           if de(a, "cpvLabel") or a.get("cpvLabel")), c), len(r))
                 for c, r in cpv_list],
                _i.sectors_title, _i.sectors_desc)'''),
 # --- home ---
 ('''    write(f"/{LANG}/index.html", page(
        "Öffentliche Aufträge Schweiz — Zuschläge nach Unternehmen",
        f"{chf(len(awards))} auf simap.ch publizierte Zuschläge, nach Unternehmen "
        f"aufbereitet: wer gewinnt welche öffentlichen Aufträge in der Schweiz, "
        f"für welchen Betrag und bei welchem Auftraggeber.", "\\n".join(b), f"/{LANG}/"))''',
  '''    write(f"/{LANG}/index.html", page(
        _m("home_title"), _m("home_desc", n=chf(len(awards))), "\\n".join(b), f"/{LANG}/"))'''),
 ('''             '<a class="tag" href="/{LANG}/ausschreibungen/">Offene Ausschreibungen</a>'
             '<a class="tag" href="/{LANG}/unternehmen/">Alle Unternehmen</a>'
             '<a class="tag" href="/{LANG}/auftraggeber/">Alle Auftraggeber</a>'
             '<a class="tag" href="/{LANG}/kanton/">Alle Kantone</a>'
             '<a class="tag" href="/{LANG}/bereich/">Alle Bereiche</a></div>')''',
  '''             f'<a class="tag" href="/{LANG}/ausschreibungen/">{e(_p.open_tenders_h1)}</a>'
             f'<a class="tag" href="/{LANG}/unternehmen/">{e(_i.all_companies)}</a>'
             f'<a class="tag" href="/{LANG}/auftraggeber/">{e(_i.all_buyers)}</a>'
             f'<a class="tag" href="/{LANG}/kanton/">{e(_i.all_cantons)}</a>'
             f'<a class="tag" href="/{LANG}/bereich/">{e(_i.all_sectors)}</a></div>')'''),
 ('''<span>Nächste Eingabefristen</span>'
                 f'<span>{len(opens)} offen</span></div>''',
  '''<span>{_i.next_deadlines}</span>'
                 f'<span>{_if("open_count", n=len(opens))}</span></div>'''),
 ('''<div class="runhead" style="margin-top:28px"><span>Nach Kanton</span>''',
  '''<div class="runhead" style="margin-top:28px"><span>{_i.by_canton}</span>'''),
 ('''<div class="runhead" style="margin-top:28px"><span>Nach Bereich</span>''',
  '''<div class="runhead" style="margin-top:28px"><span>{_i.by_sector}</span>'''),
 ('''"Gleicher Bereich</a>')''', '''{e(_i.same_sector)}</a>')'''),
 ('''Aufträge im Kanton {e(src["canton"])}</a>\'''', '''{e(_if("contracts_in", c=src["canton"]))}</a>\''''),
]
n = 0
for old, new in R:
    if old in s:
        s = s.replace(old, new); n += 1
    else:
        print(f"    NON TROVATO: {old.splitlines()[0][:66]}")
p.write_text(s)
print(f"  {n}/{len(R)} applicate")
