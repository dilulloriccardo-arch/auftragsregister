(function () {
var A = window.AR; if (!A || A.kb) return; A.kb = 1;
var d = document, LL = {"de":{"kb_close":"Schliessen","kb_h":"{div} im Kanton {name}","kb_lead":"{n} an {f} (Daten dieses Registers).","kb_f1":"1 Firma","kb_fn":"{n} Firmen","kb_top":"Firmen mit den meisten Aufträgen","company":"Firma","awards":"Aufträge","sum_l":"Summe","unit_k":"Tsd. CHF","unit_m":"Mio. CHF","amount":"Betrag","kb_recent":"Die {k} neuesten von {n}","date":"Datum","contract":"Auftrag","winner":"Vergeben an","kb_all":"Die Branche in der ganzen Schweiz","kb_csv":"Alle Aufträge des Kantons als CSV","kb_fb":"{k} dieser Aufträge ({p}) nennen keinen Ort und zählen hier, weil der Auftraggeber hier seinen Sitz hat.","kb_fbx":"Ohne diese Aufträge","kb_once":"{k} der {f} Firmen haben hier genau einen Auftrag erhalten."},"fr":{"kb_close":"Fermer","kb_h":"{div} dans le canton {of}","kb_lead":"{n} pour {f} (données de ce registre).","kb_f1":"1 entreprise","kb_fn":"{n} entreprises","kb_top":"Entreprises qui ont remporté le plus de marchés","company":"Entreprise","awards":"Marchés","sum_l":"Total","unit_k":"milliers de CHF","unit_m":"millions de CHF","amount":"Montant","kb_recent":"Les {k} plus récents sur {n}","date":"Date","contract":"Marché","winner":"Attribué à","kb_all":"Le secteur dans toute la Suisse","kb_csv":"Tous les marchés du canton en CSV","kb_fb":"{k} de ces marchés ({p}) n’indiquent aucun lieu et comptent ici, où l’acheteur public a son siège.","kb_fbx":"Sans ces marchés","kb_once":"{k} des {f} entreprises ont remporté ici un seul marché."},"it":{"kb_close":"Chiudi","kb_h":"{div} nel Canton {name}","kb_lead":"{n} a {f} (dati di questo registro).","kb_f1":"1 azienda","kb_fn":"{n} aziende","kb_top":"Aziende che hanno vinto più appalti","company":"Azienda","awards":"Appalti","sum_l":"Totale","unit_k":"migliaia di CHF","unit_m":"milioni di CHF","amount":"Importo","kb_recent":"I {k} più recenti su {n}","date":"Data","contract":"Appalto","winner":"Aggiudicato a","kb_all":"Il settore in tutta la Svizzera","kb_csv":"Tutti gli appalti del cantone in CSV","kb_fb":"{k} di questi appalti ({p}) non indicano il luogo e contano qui, dove ha sede l’ente pubblico.","kb_fbx":"Senza questi appalti","kb_once":"{k} delle {f} aziende hanno vinto qui un solo appalto."},"en":{"kb_close":"Close","kb_h":"{div} in the canton of {name}","kb_lead":"{n} to {f} (data from this register).","kb_f1":"1 company","kb_fn":"{n} companies","kb_top":"Companies that won the most contracts","company":"Company","awards":"Contracts","sum_l":"Total","unit_k":"CHF thousand","unit_m":"CHF million","amount":"Amount","kb_recent":"The {k} most recent of {n}","date":"Date","contract":"Contract","winner":"Awarded to","kb_all":"The sector across Switzerland","kb_csv":"All the canton’s contracts as CSV","kb_fb":"{k} of these contracts ({p}) name no place and count here, where the public buyer is based.","kb_fbx":"Without these contracts","kb_once":"{k} of the {f} companies won exactly one contract here."}}, L = LL[A.l] || LL.de, l = A.l, B = A.B, fmt = A.fmt, esc = A.esc, firm = A.firm;
var LI = { de: 0, fr: 1, it: 2, en: 3 }[l];
var m = location.pathname.match(/\/kanton\/([A-Z]{2})\/$/); if (!m) return;
var K = m[1], fig = d.querySelector('figure.rk[aria-labelledby="chart-sectors"]'); if (!fig) return;
var links = [].slice.call(fig.querySelectorAll('a[href*="/branche/"]')), panel = null, from = null, PU = fig.getAttribute('data-u') || '', xo = false;
var DEC = l === 'en' ? '.' : ',';
function unit(vs) {
vs = vs.filter(function (v) { return v; }).sort(function (a, b) { return a - b; });
if (!vs.length) return 'k';
var h = vs.length >> 1, mid = vs.length % 2 ? vs[h] : (vs[h - 1] + vs[h]) / 2;
return mid >= 1e6 ? 'm' : 'k';
}
function scaled(v, u) {
if (!v) return '–';
if (u === 'm') { var x = Math.round(v / 1e5) / 10; return x === 0 ? '< 0' + DEC + '1' : A.count(Math.floor(x)) + DEC + Math.round((x % 1) * 10); }
var k = Math.round(v / 1e3); return k === 0 ? '< 1' : A.count(k);
}
function money_th(u, k) { return '<th class="r amt">' + esc(L[k || 'sum_l']) + ' (' + esc(u === 'm' ? L.unit_m : L.unit_k) + ')</th>'; }
function render(o, v) {
var x = o.d[v]; if (!x) return false;
var ex = xo && x.x, fs = ex ? x.fx : x.f, rs = ex ? x.r.filter(function (r) { return !r[6]; }).concat(x.rx || []) : x.r,
na = ex ? x.a - x.x : x.a, nk = ex ? x.kx : x.k, no = ex ? x.ox : x.o;
var cn = o.c[l] || o.c.de, name = x.n[LI], uf = PU || unit(fs.map(function (r) { return r[3]; })), ur = PU || unit(rs.map(function (r) { return r[5]; }));
var h = '<button type="button" class="tag kbx">' + esc(L.kb_close) + '</button>' +
'<h2 id="kb-h">' + esc(fmt(L.kb_h, { div: name, name: cn[0], of: cn[1] })) + '</h2>' +
'<p class="sub m10">' + esc(fmt(L.kb_lead, { n: na === 1 ? A.L.aw_1 : fmt(A.L.aw_n, { n: A.count(na) }), f: nk === 1 ? L.kb_f1 : fmt(L.kb_fn, { n: A.count(nk) }) }) +
(no && nk >= 10 && no * 2 > nk ? ' ' + fmt(L.kb_once, { k: A.count(no), f: A.count(nk) }) : '')) + '</p>' +
(x.x ? '<p class="sub m10">' + esc(fmt(L.kb_fb, { k: A.count(x.x), p: Math.round(100 * x.x / x.a) + (l === 'de' ? '\u00a0%' : l === 'fr' ? '\u202f%' : '%') })) + '</p>' +
'<label class="fbx"><input type="checkbox"' + (ex ? ' checked' : '') + '> ' + esc(L.kb_fbx) + '</label>' : '') +
'<h3>' + esc(L.kb_top) + '</h3><div class="scroll"><table class="ls fk u' + uf + '"><caption class="sr">' + esc(L.kb_top) + '</caption><thead><tr><th scope="col">' + esc(L.company) + '</th>' +
'<th scope="col" class="r">' + esc(L.awards) + '</th>' + money_th(uf).replace('<th', '<th scope="col"') + '</tr></thead><tbody>' +
fs.map(function (r) { return '<tr><td>' + firm(r) + '</td><td class="r num">' + A.count(r[2]) + '</td><td class="r num">' + scaled(r[3], uf) + '</td></tr>'; }).join('') +
'</tbody></table></div>' +
'<h3>' + esc(fmt(L.kb_recent, { k: A.count(rs.length), n: A.count(na) })) + '</h3><div class="scroll"><table class="ls awb u' + ur + '"><caption class="sr">' +
esc(fmt(L.kb_recent, { k: rs.length, n: na })) + '</caption><thead><tr><th scope="col" class="w96">' + esc(L.date) + '</th><th scope="col">' + esc(L.contract) +
'</th><th scope="col">' + esc(L.winner) + '</th>' + money_th(ur, 'amount').replace('<th', '<th scope="col"') + '</tr></thead><tbody>' +
rs.map(function (r) {
return '<tr><td class="mono d"><time datetime="' + r[0] + '">' + A.date(r[0]) + '</time></td><td><a href="' + B + '/' + l + '/auftrag/' + r[1] + '"' +
(r[3] && r[3] !== l ? ' lang="' + r[3] + '"' : '') + '>' + esc(r[2]) + '</a></td><td>' + (r[4].map(firm).join(' · ') || '–') +
'</td><td class="r num">' + scaled(r[5], ur) + '</td></tr>';
}).join('') + '</tbody></table></div>' +
'<p class="dl"><a href="' + B + '/' + l + '/branche/' + v + '/">' + esc(L.kb_all) + '</a> · <a href="' + B + '/daten/kanton/' + K + '.csv" type="text/csv" download>' +
esc(L.kb_csv) + '</a></p>';
if (!panel) {
panel = d.createElement('section'); panel.className = 'kb'; panel.id = 'kb'; panel.tabIndex = -1;
panel.setAttribute('aria-labelledby', 'kb-h');
fig.parentNode.insertBefore(panel, fig.nextSibling);
}
panel.innerHTML = h;
panel.querySelector('.kbx').addEventListener('click', close);
var tg = panel.querySelector('.fbx input');
if (tg) tg.addEventListener('change', function () { xo = tg.checked; render(o, v); var t2 = panel.querySelector('.fbx input'); if (t2) t2.focus(); });
[].forEach.call(panel.querySelectorAll('table.ls'), function (t) { A.roles(t); A.cut(t); });
links.forEach(function (a) { if (a.getAttribute('data-b') === v) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
return true;
}
function close() {
if (panel) { panel.remove(); panel = null; }
links.forEach(function (a) { a.removeAttribute('aria-current'); });
try { history.replaceState(null, '', location.pathname); } catch (e) { }
if (from) from.focus();
}
function show(v, push, scroll, first) {
A.json('/daten/kb/' + K + '.json').then(function (o) {
if (first && !panel) { var y = fig.getBoundingClientRect().bottom + scrollY - innerHeight; if (y < scrollY) scrollTo(0, Math.max(0, y)); }
if (!render(o, v)) return;
try { history[push ? 'pushState' : 'replaceState'](null, '', location.pathname + '#kb-' + v); } catch (e) { }
if (scroll) requestAnimationFrame(function () {
requestAnimationFrame(function () { try { panel.scrollIntoView({ block: 'start' }); } catch (e) { } panel.focus({ preventScroll: true }); });
});
A.totop();
}, function () { var a = links.filter(function (x) { return x.getAttribute('data-b') === v; })[0]; if (a && push) location.href = a.getAttribute('data-href'); });
}
links.forEach(function (a) {
var v = (a.getAttribute('href').match(/\/branche\/(\d\d)\//) || [])[1]; if (!v) return;
a.setAttribute('data-b', v); a.setAttribute('data-href', a.getAttribute('href'));
a.setAttribute('href', '#kb-' + v); a.classList.add('kbs');
a.addEventListener('click', function (ev) {
if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button) return;
ev.preventDefault(); from = a; show(v, true, true);
});
});
function fromUrl(scroll, first) {
var v = (location.hash.match(/^#kb-(\d\d)$/) || [])[1] || new URLSearchParams(location.search).get('b');
if (v && /^\d\d$/.test(v)) show(v, false, scroll, first); else if (panel) { panel.remove(); panel = null; }
}
addEventListener('popstate', function () { fromUrl(false); });
addEventListener('hashchange', function () { fromUrl(true); });
fromUrl(true, true);
})();
