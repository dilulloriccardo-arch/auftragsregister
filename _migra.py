import pathlib, re
p = pathlib.Path("genera.py"); s = p.read_text()
R = []

R.append(('''def zuschlag(n: int) -> str:
    return plural(n, "Zuschlag", "Zuschläge")''',
'''def zuschlag(n: int) -> str:
    one, many = lingue.PLURALS[LANG]
    return plural(n, one, many)'''))

R.append(('''class _Prose:
    def __getattr__(self, key: str) -> str:
        return lingue.p(key, LANG)''',
'''class _Prose:
    def __getattr__(self, key: str) -> str:
        return lingue.p(key, LANG)


def _m(key: str, **kw) -> str:
    return lingue.m(key, LANG, **kw)'''))

# --- scheda azienda ---
R.append(('''f'<p class="sum">{zuschlag(len(rows))} auf simap.ch publiziert'
             + (f", {e(span)}" if span else "") + ", "
             + f'{plural(len(c["buyers"]), "Auftraggeber", "verschiedene Auftraggeber")}.</p></div>'
             '<dl class="rail">\'''',
'''f'<p class="sum">' + e(_m("company_lead", n=zuschlag(len(rows)),
                                       span=(f", {span}" if span else ""),
                                       b=_m("buyers_count", k=len(c["buyers"]))))
             + '</p></div><dl class="rail">\''''))
R.append(('''        desc = (f"{name}: {zuschlag(len(rows))} auf simap.ch"
                + (f", {chf(c['value'])} CHF" if c["value"] else "")
                + (f", {span}" if span else "") + ". Auftraggeber, Beträge, Kantone.")''',
'''        desc = _m("company_desc", name=name, n=zuschlag(len(rows)),
                  val=(f", {chf(c['value'])} CHF" if c["value"] else ""),
                  span=(f", {span}" if span else ""))'''))
R.append(('page(fit_title(name, " — öffentliche Aufträge"), desc[:180],',
          'page(fit_title(name, _m("company_title")), desc[:180],'))
R.append(('''<div class="runhead"><span>Zuschläge</span>'
                 '<span>chronologisch</span></div>''',
          '''<div class="runhead"><span>{_.awards}</span>'
                 f'<span>{_.chronological}</span></div>'''))

# --- appalto ---
R.append(('page(fit_title(title, " — Ausschreibung" if is_open else " — Zuschlag"),',
          'page(fit_title(title, _m("tender_suffix") if is_open else _m("award_suffix")),'))

# --- committente ---
R.append(('''f'<p class="sum">{zuschlag(len(rows))} an {nfirms} Unternehmen vergeben und auf '
             "simap.ch publiziert.</p></div><dl class=\\"rail\\">"''',
'''f'<p class="sum">' + e(_m("buyer_lead", n=zuschlag(len(rows)), f=nfirms))
             + '</p></div><dl class="rail">\''''))
R.append(('''              page(fit_title(name, " — vergebene Aufträge"),
                   f"{name}: {zuschlag(len(rows))} an {nfirms} Unternehmen, publiziert auf "
                   f"simap.ch. Wer welchen Auftrag erhielt und für welchen Betrag.",''',
'''              page(fit_title(name, _m("buyer_title")),
                   _m("buyer_desc", name=name, n=zuschlag(len(rows)), f=nfirms),'''))
R.append(('''<div class="runhead"><span>Beauftragte Unternehmen'
                 "</span><span>nach Zuschlägen</span></div>"''',
          '''<div class="runhead"><span>{_.companies}</span>'
                 f'<span>{_.by_awards}</span></div>\''''))

# --- cantone ---
R.append(('''f'<p class="sum">{zuschlag(len(rows))} an {nfirms} Unternehmen, publiziert von '
             f'kantonalen Ämtern, Gemeinden und Bundesstellen.</p></div>\'''',
'''f'<p class="sum">' + e(_m("canton_lead", n=zuschlag(len(rows)), f=nfirms))
             + "</p></div>"'''))
R.append(('''              page(fit_title(f"Öffentliche Aufträge Kanton {name}", " — Zuschläge"),
                   f"{zuschlag(len(rows))} im Kanton {name} auf simap.ch, {nfirms} Unternehmen, "
                   f"mit Auftraggebern und Beträgen.", "\\n".join(b), f"/{LANG}/kanton/{code}/", _.canton))''',
'''              page(fit_title(_m("canton_title", name=name), _m("canton_suffix")),
                   _m("canton_desc", n=zuschlag(len(rows)), name=name, f=nfirms),
                   "\\n".join(b), f"/{LANG}/kanton/{code}/", _.canton))'''))
R.append(('''<div class="half"><div><div class="runhead"><span>Unternehmen</span>'
                 "<span>nach Zuschlägen</span></div>"''',
          '''<div class="half"><div><div class="runhead"><span>{_.companies}</span>'
                 f'<span>{_.by_awards}</span></div>\''''))

# --- settore ---
R.append(('''f'<h1>{e(label)}</h1><p class="sum">{zuschlag(len(rows))} an {nfirms} Unternehmen '
             "in diesem Beschaffungsbereich.</p></div>"''',
'''f'<h1>{e(label)}</h1><p class="sum">'
             + e(_m("sector_lead", n=zuschlag(len(rows)), f=nfirms)) + "</p></div>"'''))
R.append(('''              page(fit_title(label, f" — Aufträge CH · CPV {code}"),
                   f"{zuschlag(len(rows))} im Bereich {label} auf simap.ch, {nfirms} Unternehmen.",''',
'''              page(fit_title(label, _m("sector_suffix", code=code)),
                   _m("sector_desc", n=zuschlag(len(rows)), label=label, f=nfirms),'''))
R.append(('''<div class="sec"><div class="runhead"><span>Unternehmen</span>'
             "<span>nach Zuschlägen</span></div>"''',
          '''<div class="sec"><div class="runhead"><span>{_.companies}</span>'
             f'<span>{_.by_awards}</span></div>\''''))

n = 0
for old, new in R:
    if old in s:
        s = s.replace(old, new); n += 1
    else:
        print(f"    NON TROVATO: {old.splitlines()[0][:64]}")
p.write_text(s)
print(f"  {n}/{len(R)} sostituzioni applicate")
