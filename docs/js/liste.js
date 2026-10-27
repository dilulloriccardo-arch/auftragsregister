(function () {
var A = window.AR; if (!A || A.liste) return; A.liste = 1;
var d = document, LL = {"de":{"f_count":"{n} von {m} offenen Ausschreibungen","f_first":"Die {k}, deren Frist zuerst abläuft, von {m} offenen Ausschreibungen","f_none":"Für diese Auswahl gibt es keine offene Ausschreibung.","f_active":"({n} aktiv)","f_active_1":"(1 aktiv)","multi":"mehrere Kantone","z_near":"{c}: {n}","f_abo_kwb":"Per E-Mail: die Branche «{b}», ohne Stichwörter."},"fr":{"f_count":"{n} sur {m} appels d’offres en cours","f_first":"Les {k} qui expirent en premier, sur {m} appels d’offres en cours","f_none":"Aucun appel d’offres en cours pour cette sélection.","f_active":"({n} actifs)","f_active_1":"(1 actif)","multi":"plusieurs cantons","z_near":"{c} : {n}","f_abo_kwb":"Par e-mail : le secteur « {b} », sans mots-clés."},"it":{"f_count":"{n} di {m} bandi aperti","f_first":"I {k} che scadono prima, su {m} bandi aperti","f_none":"Nessun bando aperto per questa selezione.","f_active":"({n} attivi)","f_active_1":"(1 attivo)","multi":"più cantoni","z_near":"{c}: {n}","f_abo_kwb":"Via e-mail ricevi tutto il settore «{b}»: le parole chiave valgono solo qui."},"en":{"f_count":"{n} of {m} open tenders","f_first":"The {k} that close first, of {m} open tenders","f_none":"No open tenders for this selection.","f_active":"({n} active)","f_active_1":"(1 active)","multi":"several cantons","z_near":"{c}: {n}","f_abo_kwb":"By email: the “{b}” sector, without keywords."}}, L = LL[A.l] || LL.de, S = A.L, l = A.l, B = A.B, fmt = A.fmt, esc = A.esc, fold = A.fold;
var LI = A.li, title = A.title;
var sec = d.querySelector('[data-liste]'); if (!sec) return;
var scope = sec.getAttribute('data-liste') || '', sk = scope.indexOf('k:') === 0 ? scope.slice(2) : '',
sb = scope.indexOf('b:') === 0 ? scope.slice(2) : '';
var tbl = sec.querySelector('table.tl'), tb = tbl && tbl.tBodies[0]; if (!tb) return;
var bar = sec.querySelector('.flt'); if (!bar) return;
var wrap = tbl.closest('.scroll') || tbl, orig = tb.innerHTML, allA = sec.querySelector('a[data-all]'), allB = null;
var abRow = tb.querySelector('tr.ab');
var P = new URLSearchParams(location.search);
var st = { q: P.get('q') || '', k: (P.get('k') || '').toUpperCase(), b: P.get('b') || '', s: P.get('soon') === '1',
n: P.get('neu') === '1', o: P.get('sort') === 'neu' ? 'neu' : '', all: false };
var O = null, none, zs, tm = 0, wait = null, first = true;
var fq = bar.querySelector('input[name=q]'), fk = bar.querySelector('select[name=k]'), fb = bar.querySelector('select[name=b]'),
fo = bar.querySelector('select[name=sort]'), fn = bar.querySelector('input[name=neu]'), fs = bar.querySelector('input[name=soon]'),
cnt = bar.querySelector('.cnt'), abo = bar.querySelector('a.fa'), fan = bar.querySelector('.fan'), fd = bar.querySelector('details'),
act = bar.querySelector('.fn0'), clr = bar.querySelector('button.clr'), fan0 = fan ? fan.textContent : '';
var NB = { AG: 'ZH LU ZG SO BL BE', AI: 'AR SG', AR: 'AI SG', BE: 'JU SO AG LU OW NW UR VS VD FR NE', BL: 'BS AG SO JU', BS: 'BL',
FR: 'BE VD NE', GE: 'VD', GL: 'SZ UR GR SG', GR: 'TI UR GL SG', JU: 'BE SO BL', LU: 'AG BE OW NW SZ ZG', NE: 'VD FR BE',
NW: 'OW LU BE UR', OW: 'NW LU BE UR', SG: 'AR AI TG ZH SZ GL GR', SH: 'ZH TG', SO: 'BE JU BL AG', SZ: 'ZG LU UR GL SG ZH',
TG: 'SH ZH SG', TI: 'VS UR GR', UR: 'SZ NW OW BE VS TI GR GL', VD: 'GE FR NE BE VS', VS: 'VD BE UR TI', ZG: 'ZH AG LU SZ',
ZH: 'SH TG SG SZ ZG AG' };
function cants(r) { return r[3].replace(/\*/g, '').split(' ').filter(function (x) { return x; }); }
function cut(s, n) { if (s.length <= n) return s; s = s.slice(0, n); var i = s.lastIndexOf(' '); return (i > n - 20 ? s.slice(0, i) : s).replace(/[\s,;:.\-–]+$/, '') + '…'; }
function query() {
var p = !sk && O ? A.qparse(st.q, O.k) : { q: st.q.trim(), k: '' };
return { k: p.k, t: A.sw(A.words(p.q)), q: p.q };
}
function ek(qp) { return sk || qp.k || st.k; }
function active() { return !!(st.q.trim() || st.k || st.b || st.s || st.n || st.o); }
function scoped() {
return O.t.filter(function (r) {
if (A.when(r[6]) <= A.now) return false;
if (sk && cants(r).indexOf(sk) < 0) return false;
return !(sb && r[4].slice(0, 2) !== sb);
});
}
function pass(r, qp, skip) {
var k = ek(qp);
if (skip !== 'k' && k && cants(r).indexOf(k) < 0) return false;
if (skip !== 'b' && st.b && r[4].slice(0, 2) !== st.b) return false;
if (st.s && (A.rel(r[6]) || { n: 99 }).n > 7) return false;
if (st.n && r[7] !== O.nd) return false;
if (qp.t.length && !A.tscore(A.twords(r, O), qp.t)) return false;
return true;
}
function row(r) {
var t = title(r), dl = r[6], cs = cants(r), fbk = r[3].indexOf('*') >= 0, lab = (O.c[r[4]] || [])[LI] || '';
var sub = (cs.length > 1 ? L.multi + ' · ' : '') + cut(lab, 60);
return '<tr data-deadline="' + esc(dl) + '"><td class="when mono d"><time datetime="' + dl.slice(0, 10) + '">' + A.date(dl) + '</time></td>' +
'<td><a href="' + B + '/' + l + '/auftrag/' + r[0] + '/"' + (t.l !== l && t.l !== '--' ? ' lang="' + t.l + '"' : '') + '>' + esc(t.t) + '</a>' +
(sub ? '<span class="sub sb2">' + esc(sub) + '</span>' : '') + '</td><td>' + esc(O.b[r[5]]) + '</td><td>' +
cs.map(function (k) { return '<abbr' + (fbk ? ' class="fb"' : '') + ' title="' + esc(O.k[k] ? O.k[k][LI] : k) + '">' + k + '</abbr>'; }).join(' ') + '</td></tr>';
}
function byName(tab) { return function (a, b) { var x = fold(tab[a][LI]), y = fold(tab[b][LI]); return x < y ? -1 : x > y ? 1 : 0; }; }
function options(sc, qp) {
var kc = {}, bc = {};
sc.forEach(function (r) {
if (pass(r, qp, 'k')) cants(r).forEach(function (k) { kc[k] = (kc[k] || 0) + 1; });
if (pass(r, qp, 'b')) { var v = r[4].slice(0, 2); if (v) bc[v] = (bc[v] || 0) + 1; }
});
function fill(sel, tab, c, cur, all) {
if (!sel) return;
var keys = Object.keys(tab).filter(function (v) { return c[v] || v === cur || all; }).sort(byName(tab));
sel.innerHTML = sel.options[0].outerHTML + keys.map(function (v) {
return '<option value="' + v + '">' + esc(tab[v][LI]) + ' (' + A.count(c[v] || 0) + ')</option>'; }).join('');
sel.value = cur || '';
}
fill(fk, O.k, kc, ek(qp), true);
fill(fb, O.d, bc, st.b, false);
}
function suggest(sc, qp, k) {
var out = [], y = qp.t.length && A.dym(st.q, O);
if (y) out.push('<a href="#" data-q="' + esc(y) + '">' + esc(fmt(S.z_dym, { q: y })) + '</a>');
if (qp.t.length > 1) qp.t.forEach(function (w, i) {
var t2 = qp.t.filter(function (x, j) { return j !== i; }), n = sc.filter(function (r) { return pass(r, { k: qp.k, t: t2 }); }).length;
if (n) out.push('<a href="#" data-q="' + esc(qp.q.split(/\s+/).filter(function (x) { return fold(x).replace(/[^0-9a-z]/g, '') !== w; }).join(' ')) + '">' + esc(fmt(S.z_drop, { t: w, n: A.count(n) })) + '</a>');
});
if (k && !sk && NB[k]) NB[k].split(' ').forEach(function (c) {
var n = sc.filter(function (r) { return cants(r).indexOf(c) >= 0 && pass(r, qp, 'k'); }).length;
if (n && out.length < 6) out.push('<a href="#" data-k="' + c + '">' + esc(fmt(L.z_near, { c: O.k[c][LI], n: A.count(n) })) + '</a>');
});
out.push('<a href="' + esc(abo.href) + '">' + esc(S.z_abo) + '</a>');
zs.innerHTML = '<strong>' + esc(S.z_h) + '</strong> ' + out.join(' · ');
}
function aboLink(k, b, qp, rows) {
var a = [], c = {}, v = '', x;
function most(rs) {
rs.forEach(function (r) {
var f = A.twords(r, O), w = A.tscore(f, qp.t) && (A.tier(f, qp.t) ? .1 : 1);
if (w && O.d[x = r[4].slice(0, 2)] && A.topic(f, qp.t))
c[x] = (c[x] || 0) + w + (qp.t.some(function (q) { return !(A.syn[q] || '').indexOf(x); }) ? .01 : 0);
});
for (x in c) if (!v || c[x] > c[v]) v = x;
}
if (!b && qp.q) {
most(rows); if (!v) most(scoped());
qp.t.forEach(function (q) { x = (A.syn[q] || '').slice(0, 2); if (!v && O.d[x]) v = x; });
}
if (k) a.push('k=' + k); if (b || v) a.push('b=' + (b || v));
abo.href = B + '/' + l + '/ausschreibungen/abo/' + (a.length ? '?' + a.join('&') : '');
if (fan) { fan.hidden = !qp.q; fan.textContent = v ? fmt(L.f_abo_kwb, { b: O.d[v][LI] }) : fan0; }
}
function render() {
var qp = query(), sc = scoped(), n, k = ek(qp), on = active() || st.all, rows = [];
if (on) {
rows = sc.filter(function (r) { return pass(r, qp); });
var neu = st.o === 'neu', html = '', w = -1;
rows.forEach(function (r) { r.ti = qp.t.length && A.tier(A.twords(r, O), qp.t); });
rows.sort(function (a, b) {
return a.ti - b.ti || (neu ? (a[7] < b[7] ? 1 : a[7] > b[7] ? -1 : 0) : 0) || (A.when(a[6]) - A.when(b[6]));
});
rows.forEach(function (r, i) { if (w < 0 && r.ti) w = i; });
rows.forEach(function (r, i) {
if (i === w) html += '<tr class="tier"><td colspan="4">' + esc(i ? S.tier_w : S.tier_a) + '</td></tr>';
html += row(r);
});
tb.innerHTML = html;
n = rows.length;
} else {
tb.innerHTML = orig;
n = tb.querySelectorAll('tr[data-deadline]').length;
}
if (abRow) {
var dr = tb.querySelectorAll('tr[data-deadline]:not([hidden])');
if (on && dr.length) { var at = dr[Math.min(10, dr.length) - 1]; at.parentNode.insertBefore(abRow, at.nextSibling); }
}
A.deco(tb);
if (!on) n = tb.querySelectorAll('tr[data-deadline]:not([hidden])').length;
A.roles(tbl);
aboLink(k, st.b || sb, qp, rows);
none.hidden = n > 0; wrap.hidden = !n; zs.hidden = n > 0;
if (!n) suggest(sc, qp, k);
[].forEach.call(sec.querySelectorAll('p.xh,p.fn'), function (x) { x.hidden = on; });
cnt.textContent = !on && n < sc.length ? fmt(L.f_first, { k: A.count(n), m: A.count(sc.length) })
: fmt(L.f_count, { n: A.count(n), m: A.count(sc.length) });
A.cut(tbl, on ? n : sc.length, on || !(allA || allB) ? null : function () { showAll(); });
var more = (allA && allA.closest('p')) || allB;
if (more) {
more.hidden = on || n >= sc.length || !!tbl._cb;
(allA || allB.firstChild).textContent = fmt(S.all_n, { n: A.count(sc.length) });
}
var nx = !scope && d.querySelector('a.fig.date time');
if (nx && sc.length) {
var m = sc.reduce(function (a, r) { return A.when(r[6]) < A.when(a) ? r[6] : a; }, sc[0][6]);
nx.setAttribute('datetime', m.slice(0, 10)); nx.textContent = A.date(m);
}
options(sc, qp);
var na = (qp.q ? 1 : 0) + (k && !sk ? 1 : 0) + (st.b ? 1 : 0) + (st.s ? 1 : 0) + (st.n ? 1 : 0) + (st.o ? 1 : 0);
if (act) act.textContent = na ? ' ' + (na === 1 ? L.f_active_1 : fmt(L.f_active, { n: na })) : '';
clr.hidden = !na;
var p = [];
if (qp.q) p.push('q=' + encodeURIComponent(qp.q));
if (k && !sk) p.push('k=' + k); if (st.b) p.push('b=' + st.b); if (st.o) p.push('sort=' + st.o);
if (st.n) p.push('neu=1'); if (st.s) p.push('soon=1');
try { history.replaceState(null, '', location.pathname + (p.length ? '?' + p.join('&') : '') + location.hash); } catch (e) { }
A.totop();
if (first) {
first = false;
if (active()) {
if (fd && !fd.open) fd.open = true;
try { bar.scrollIntoView({ block: 'start' }); } catch (e) { }
cnt.focus({ preventScroll: true });
cnt.classList.remove('hl'); void cnt.offsetWidth; cnt.classList.add('hl');
}
}
}
function bind() {
none = d.createElement('p'); none.className = 'flt-none'; none.hidden = true; none.textContent = L.f_none;
zs = d.createElement('p'); zs.className = 'zs'; zs.hidden = true;
wrap.parentNode.insertBefore(none, wrap); wrap.parentNode.insertBefore(zs, wrap);
if (fq.value) st.q = fq.value;
if (fs.checked) st.s = true; if (fn && fn.checked) st.n = true; if (fo && fo.value) st.o = fo.value;
var qp = A.qparse(st.q, O.k);
if (!sk && qp.k) { st.q = qp.q; st.k = qp.k; }
fq.value = st.q; fs.checked = st.s; if (fn) fn.checked = st.n; if (fo) fo.value = st.o;
if (sk) st.k = ''; if (sb) st.b = '';
if (st.k && !O.k[st.k]) st.k = '';
if (st.b && !O.d[st.b]) st.b = '';
fq.addEventListener('input', function () { clearTimeout(tm); tm = setTimeout(function () { st.q = fq.value; render(); }, 200); });
if (fk) fk.addEventListener('change', function () { st.k = fk.value; var p = A.qparse(st.q, O.k); if (p.k) { st.q = p.q; fq.value = p.q; } render(); });
if (fb) fb.addEventListener('change', function () { st.b = fb.value; render(); });
if (fo) fo.addEventListener('change', function () { st.o = fo.value; render(); });
if (fn) fn.addEventListener('change', function () { st.n = fn.checked; render(); });
fs.addEventListener('change', function () { st.s = fs.checked; render(); });
clr.addEventListener('click', function () {
st.q = st.k = st.b = st.o = ''; st.s = st.n = false; fq.value = ''; fs.checked = false; if (fn) fn.checked = false;
if (fo) fo.value = ''; render(); fq.focus();
});
zs.addEventListener('click', function (ev) {
var a = ev.target.closest('a[data-q],a[data-k]'); if (!a) return;
ev.preventDefault();
if (a.hasAttribute('data-q')) { st.q = a.getAttribute('data-q'); fq.value = st.q; }
else st.k = a.getAttribute('data-k');
render();
});
if (A.ph.addEventListener) A.ph.addEventListener('change', function () { if (!A.ph.matches && fd) fd.open = true; });
}
function ready() {
if (!wait) wait = A.json('/daten/offen.json').then(function (o) { O = o; bind(); render(); }, function () { wait = null; });
return wait;
}
function showAll(ev) {
if (ev) ev.preventDefault();
var k = tb.querySelectorAll('tr[data-deadline]').length;
ready().then(function () {
if (!O) { if (allA) location.href = allA.href; return; }
st.all = true; tbl.setAttribute('data-all', '1'); render();
var r = tb.querySelectorAll('tr[data-deadline]')[k], a = r && r.querySelector('a');
if (a) a.focus();
});
}
if (allA) allA.addEventListener('click', showAll);
var total = +sec.getAttribute('data-n') || 0;
if (!allA && total > tb.querySelectorAll('tr[data-deadline]').length) {
allB = d.createElement('p');
allB.innerHTML = '<button type="button" class="all">' + esc(fmt(S.all_n, { n: A.count(total) })) + '</button>';
wrap.parentNode.insertBefore(allB, wrap.nextSibling);
allB.firstChild.addEventListener('click', showAll);
}
if (tbl._cb && (allA || allB)) { A.cut(tbl, total, showAll); ((allA && allA.closest('p')) || allB).hidden = true; }
var live = 'tr[data-deadline]:not([hidden]):not(.off)';
function pre(c) {
var n = tb.querySelectorAll(live).length,
m = c ? (scope ? (c[scope.charAt(0)] || {})[scope.slice(2)] || 0 : c.a) : total;
m = Math.max(m, n);
if (O) return;
cnt.textContent = n < m ? fmt(L.f_first, { k: A.count(n), m: A.count(m) }) : fmt(L.f_count, { n: A.count(n), m: A.count(m) });
[allA, allB && allB.firstChild, tbl._cb && tbl._cb.firstChild].forEach(function (b) { if (b) b.textContent = fmt(S.all_n, { n: A.count(m) }); });
var nx = !scope && d.querySelector('a.fig.date time'), r0 = tb.querySelector(live);
if (nx && r0) { var t = r0.getAttribute('data-deadline'); nx.setAttribute('datetime', t.slice(0, 10)); nx.textContent = A.date(t); }
}
A.lx = function () { (A.oc || Promise.resolve(null)).then(pre, function () { }); };
if (active()) ready();
else {
pre(null);
A.lx();
var go = function () { bar.removeEventListener('pointerover', go); bar.removeEventListener('focusin', go); ready(); };
bar.addEventListener('pointerover', go); bar.addEventListener('focusin', go);
}
})();
