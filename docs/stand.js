(function () {
var D = {"iso":"2026-10-30","t":{"de":"Aktualisiert am {d}","fr":"Mis à jour le {d}","it":"Aggiornato al {d}","en":"Updated {d}"},"B":"","v":"aa5a09da","mo":["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],"nx":29889120,"sw":"ag sa gmbh sarl sagl ltd kg co cie inc llc ug se sas srl spa de du des la le les der die das dem den und et ed di del della dei von fur and of the en au aux im in an zu zur zum par pour per mit bei auf a d l e al con delle degli dello dell alla alle nel nella for at to with","L":{"de":{"due_today":"läuft heute ab, {t}","due_today_bare":"läuft heute ab","due_tomorrow":"läuft morgen ab","due_days":"noch {n} Tage","due_over":"abgelaufen","hidden_1":"1 Ausschreibung ist inzwischen abgelaufen und ausgeblendet","hidden_n":"{n} Ausschreibungen sind inzwischen abgelaufen und ausgeblendet","tender_expired":"Eingabefrist abgelaufen","expired_lead":"Die Eingabefrist ist abgelaufen ({when}). Wenn der Auftrag vergeben und auf simap.ch publiziert wird, sehen Sie hier, wer ihn erhält.","top":"Nach oben","ph":"Firma, Auftraggeber, Thema …|Firma, Auftraggeber …|Firma, Thema …","colon":":","all_n":"Alle {n} anzeigen","z_h":"Vorschläge:","z_drop":"ohne «{t}»: {n}","z_abo":"Neue Ausschreibungen dieser Auswahl gratis per E-Mail","z_dym":"Meinten Sie «{q}»?","tier_w":"Weitere Treffer (Wortteil)","tier_a":"Treffer als Wortteil","aw_1":"1 Auftrag","aw_n":"{n} Aufträge","failed":"Wir konnten die Daten nicht laden."},"fr":{"due_today":"expire aujourd’hui à {t}","due_today_bare":"expire aujourd’hui","due_tomorrow":"expire demain","due_days":"encore {n} jours","due_over":"expiré","hidden_1":"1 appel d’offres expiré entre-temps n’est plus affiché","hidden_n":"{n} appels d’offres expirés entre-temps ne sont plus affichés","tender_expired":"Délai de remise expiré","expired_lead":"Le délai de remise des offres a expiré ({when}). Si le marché est attribué et publié sur simap.ch, vous verrez ici qui l’a remporté.","top":"Retour en haut","ph":"Entreprise, acheteur, thème…|Entreprise, acheteur…|Entreprise, thème…","colon":" :","all_n":"Afficher les {n}","z_h":"Suggestions :","z_drop":"sans « {t} » : {n}","z_abo":"Recevoir gratuitement par e-mail les nouveaux appels d’offres de cette sélection","z_dym":"Vouliez-vous dire « {q} » ?","tier_w":"Autres résultats (partie de mot)","tier_a":"Résultats par partie de mot","aw_1":"1 marché","aw_n":"{n} marchés","failed":"Impossible de charger les données."},"it":{"due_today":"scade oggi, ore {t}","due_today_bare":"scade oggi","due_tomorrow":"scade domani","due_days":"ancora {n} giorni","due_over":"scaduto","hidden_1":"1 bando scaduto nel frattempo è nascosto","hidden_n":"{n} bandi scaduti nel frattempo sono nascosti","tender_expired":"Termine scaduto","expired_lead":"La scadenza è passata ({when}). Se l’appalto viene aggiudicato e pubblicato su simap.ch, qui vedrai chi l’ha vinto.","top":"Torna su","ph":"Azienda, ente pubblico, tema…|Azienda, ente…|Azienda, tema…","colon":":","all_n":"Mostra tutti i {n}","z_h":"Suggerimenti:","z_drop":"senza «{t}»: {n}","z_abo":"Ricevi gratis via e-mail i nuovi bandi di questa selezione","z_dym":"Forse cercavi «{q}»?","tier_w":"Altri risultati (parte di parola)","tier_a":"Risultati per parte di parola","aw_1":"1 appalto","aw_n":"{n} appalti","failed":"Non siamo riusciti a caricare i dati."},"en":{"due_today":"closes today at {t}","due_today_bare":"closes today","due_tomorrow":"closes tomorrow","due_days":"{n} days left","due_over":"closed","hidden_1":"1 tender has closed since and is hidden","hidden_n":"{n} tenders have closed since and are hidden","tender_expired":"Deadline passed","expired_lead":"The submission deadline has passed ({when}). If the contract is awarded and published on simap.ch, you’ll see here who won it.","top":"Back to top","ph":"Company, buyer, topic…|Company, buyer…|Company, topic…","colon":":","all_n":"Show all {n}","z_h":"Suggestions:","z_drop":"without “{t}”: {n}","z_abo":"Get new tenders for this selection by email – free","z_dym":"Did you mean “{q}”?","tier_w":"More matches (part of a word)","tier_a":"Matches on part of a word","aw_1":"1 contract","aw_n":"{n} contracts","failed":"We couldn’t load the data."}},"de":"30.10.2026","fr":"30.10.2026","it":"30.10.2026","en":"30 Oct 2026"}, d = document, h = d.documentElement, l = D.L[h.lang] ? h.lang : 'de', L = D.L[l], B = D.B, A = null;
var IE = { al: 'all’', dal: 'dall’', del: 'dell’', nel: 'nell’', il: 'l’' };
function fmt(s, o) {
s = String(s);
if (l == 'it') s = s.replace(/(^|[^\w’'])(al|dal|del|nel|il) \{(\w+)\}/gi, function (m, a, w, k) {
var x = IE[w.toLowerCase()];
return /^(0?8|11)\.\d/.test(o[k]) ? a + (w[0] == w[0].toLowerCase() ? x : x[0].toUpperCase() + x.slice(1)) + '{' + k + '}' : m;
});
return s.replace(/\{(\w+)\}/g, function (m, k) { return k in o ? o[k] : m; });
}
function p2(n) { n = +n; return (n < 10 ? '0' : '') + n; }
function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
var GR = { de: '’', it: '’', fr: '\u202f', en: ',' };
function count(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, GR[l]); }
function date(iso) {
var y = iso.slice(0, 4), m = +iso.slice(5, 7), x = +iso.slice(8, 10);
return l === 'en' ? x + ' ' + D.mo[m - 1] + ' ' + y : p2(x) + '.' + p2(m) + '.' + y;
}
var MK; try { MK = new RegExp('\\p{M}', 'gu'); } catch (e) { MK = /[̀-ͯ]/g; }
function fold(s) {
s = String(s || '').toLowerCase().replace(/ß/g, 'ss').replace(/æ/g, 'ae').replace(/œ/g, 'oe').replace(/ø/g, 'o');
if (s.normalize) s = s.normalize('NFD');
return s.replace(MK, '').replace(/ae/g, 'a').replace(/oe/g, 'o').replace(/ue/g, 'u');
}
function words(s) { return fold(s).split(/[^0-9a-z]+/).filter(function (x) { return x; }); }
function slug(s) {
s = String(s).toLowerCase().replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss');
if (s.normalize) s = s.normalize('NFKD');
return s.replace(MK, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70) || 'x';
}
function firm(x) {
var p = x[1], n = esc(x[0]);
return p ? '<a href="' + B + '/' + l + '/unternehmen/' + (p === 1 ? slug(x[0]) : p) + '/">' + n + '</a>' : n;
}
var sd = D[l], sp = (D.t[l] || '').split('{d}');
if (sd && sp.length === 2) [].forEach.call(d.querySelectorAll('[data-stand]'), function (e) {
var t = d.createElement('time'); t.setAttribute('datetime', D.iso); t.textContent = sd;
e.textContent = sp[0]; e.appendChild(t); e.appendChild(d.createTextNode(sp[1] + (e.nextElementSibling ? ' · ' : '')));
e.removeAttribute('data-stand');
});
var ZF = null;
try { ZF = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Zurich', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }); } catch (e) { ZF = null; }
function parts(t) {
var o = {};
if (ZF && ZF.formatToParts) { ZF.formatToParts(new Date(t)).forEach(function (x) { o[x.type] = x.value; }); return o; }
var x = new Date(t);
return { year: '' + x.getFullYear(), month: p2(x.getMonth() + 1), day: p2(x.getDate()), hour: p2(x.getHours()), minute: p2(x.getMinutes()) };
}
function zday(t) { var o = parts(t); return o.year + '-' + o.month + '-' + o.day; }
function dnum(s) { return Math.round(Date.UTC(+s.slice(0, 4), +s.slice(5, 7) - 1, +s.slice(8, 10)) / 864e5); }
var now = Date.now(), today = dnum(zday(now));
function when(iso) { if (!iso) return null; var t = Date.parse(iso.length <= 10 ? iso + 'T23:59:59' : iso); return isNaN(t) ? null : t; }
function clock(t) {
var o = parts(t), hh = +o.hour, mm = o.minute;
if (!hh && mm === '00') return '';
return l === 'de' ? hh + '.' + mm + '\u00a0Uhr' : l === 'fr' ? hh + '\u202fh\u202f' + mm : p2(hh) + ':' + mm;
}
function rel(iso) {
var t = when(iso);
if (t === null) return null;
if (t <= now) return { c: 'over', x: L.due_over, n: -1 };
var n = dnum(zday(t)) - today, c;
if (n <= 0) { c = clock(t); return { c: 'today', x: c ? fmt(L.due_today, { t: c }) : L.due_today_bare, n: 0 }; }
if (n === 1) return { c: 'soon', x: L.due_tomorrow, n: 1 };
if (n <= 7) return { c: 'soon', x: fmt(L.due_days, { n: n }), n: n };
return { c: '', x: '', n: n };
}
function over(x) {
var w = x.parentNode;
if (w.tagName === 'SPAN') w.style.minWidth = w.getBoundingClientRect().width + 'px';
x.style.minHeight = x.getBoundingClientRect().height + 'px'; x.textContent = L.due_over;
}
function expire(e, live) {
e.classList.add('off');
var x = e.querySelector('.rel');
if (!x) { x = d.createElement('em'); x.className = 'rel'; e.appendChild(x); }
over(x);
var st = d.querySelector('.title .state'), h1 = d.querySelector('.title h1'), b = e.querySelector('b');
if (st && !st.classList.contains('off')) { st.className = 'state off'; st.lastChild.textContent = L.tender_expired; }
if (!live) h.classList.add('xp');
if (!live && h1 && b && !h1.parentNode.querySelector('.sum')) {
var p = d.createElement('p'); p.className = 'sum'; p.textContent = fmt(L.expired_lead, { when: b.textContent });
h1.parentNode.insertBefore(p, h1.nextSibling);
}
[].forEach.call(d.querySelectorAll('.acts a[href$="frist.ics"]'), function (a) { if (live) a.style.visibility = 'hidden'; else a.hidden = true; });
}
function one(e, hid, live, pt) {
var r = rel(e.getAttribute('data-deadline')), x;
if (!r) return;
if (r.c === 'over') {
if (e.tagName !== 'TR' && e.tagName !== 'LI') { if (!e.classList.contains('off')) expire(e, live); return; }
if (!live && !(pt && e.tagName === 'LI' && !e.closest('[data-show]'))) {
if (!e.hasAttribute('data-gone')) { e.hidden = true; e.setAttribute('data-gone', ''); hid.push(e); }
return;
}
if (e.classList.contains('off')) return;
e.classList.add('off'); hid.push(e);
if ((x = e.querySelector('.rel'))) return over(x);
r.c = '';
}
if (e.getAttribute('data-r')) return;
e.setAttribute('data-r', '1');
var w = e.classList.contains('when') ? e : (e.querySelector('.when') || e);
if (r.c) { w.classList.add(r.c); e.classList.add(r.c); }
if (r.x) {
var s = w.querySelector('.rel');
if (!s) { s = d.createElement(e.tagName === 'DIV' ? 'em' : 'span'); s.className = 'rel'; w.appendChild(s); }
s.textContent = r.x;
}
if (r.c === 'today' && e.tagName === 'DIV') {
var st = d.querySelector('.title .state');
if (st && !st.classList.contains('off')) { st.className = 'state today'; st.lastChild.textContent = r.x; }
}
}
function deco(root, live) {
var hid = [], pt = !live && (d.timeline && d.timeline.currentTime || performance.getEntriesByType('paint').length);
[].forEach.call((root || d).querySelectorAll('[data-deadline]'), function (e) { one(e, hid, live, pt); });
var lists = [];
hid.forEach(function (e) { var c = e.closest('table') || e.parentNode; if (lists.indexOf(c) < 0) lists.push(c); });
lists.forEach(function (c) {
var sec = c.closest('.sec'), k = sec && sec.querySelector('.runhead>span');
if (k && /^[\d’ ,]+$/.test(k.textContent)) {
if (!k.hasAttribute('data-n0')) k.setAttribute('data-n0', k.textContent.replace(/\D/g, ''));
k.textContent = count(Math.max(0, +k.getAttribute('data-n0') - sec.querySelectorAll('[data-gone],[data-deadline].off').length));
}
var n = c.querySelectorAll('[data-gone]').length;
if (live || !n) return;
var a = c.tagName === 'TABLE' ? (c.closest('.scroll') || c) : c, nx = a.nextElementSibling, note;
if (nx && nx.classList.contains('xh')) note = nx;
else { note = d.createElement('p'); note.className = 'xh'; a.parentNode.insertBefore(note, a.nextSibling); }
note.textContent = n === 1 ? L.hidden_1 : fmt(L.hidden_n, { n: count(n) });
var want = +c.getAttribute('data-show') || 0;
if (want) [].forEach.call(c.querySelectorAll('[data-more]:not([data-gone])'), function (x) {
if (c.querySelectorAll('[data-deadline]:not([hidden])').length < want) x.hidden = false;
});
});
if (!live) [].forEach.call((root || d).querySelectorAll('table.tl tr.ab'), function (ab) {
var rs = [].filter.call(ab.parentNode.rows, function (r) { return !r.hidden && r.hasAttribute('data-deadline'); }),
at = rs[Math.min(10, rs.length) - 1];
if (at && at.nextElementSibling !== ab) at.parentNode.insertBefore(ab, at.nextSibling);
ab.setAttribute('data-p', '');
});
return hid;
}
deco(d);
var got = {}, J = {};
function load(n) {
if (got[n]) return; got[n] = 1;
var s = d.createElement('script'); s.src = B + '/js/' + n + '.js?v=' + D.v; d.head.appendChild(s);
}
function json(u) {
if (!J[u]) J[u] = fetch(B + u + '?d=' + D.iso).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
.catch(function (e) { delete J[u]; throw e; });
return J[u];
}
function oc() {
var t = Date.now();
if (!D.nx || t < D.nx * 6e4) return Promise.resolve(null);
return json('/daten/offen-dl.json').then(function (o) {
var c = { a: 0, k: {}, b: {} };
o.t.forEach(function (r) {
if (r[0] * 6e4 <= t) return;
c.a++;
r[1].split(' ').forEach(function (k) { if (k) c.k[k] = (c.k[k] || 0) + 1; });
if (r[2]) c.b[r[2]] = (c.b[r[2]] || 0) + 1;
});
return c;
}, function () { return null; });
}
function ocv(c, k) {
if (k === '*') return c.a;
var o, n = 0, x;
if (k === 'nk' || k === 'nb') { o = c[k.charAt(1)]; for (x in o) if (o[x]) n++; return n; }
if (k === 'mx') { for (x in c.k) n = Math.max(n, c.k[x]); return n; }
return (c[k.charAt(0)] || {})[k.slice(2)] || 0;
}
function counts() {
var oe = d.querySelectorAll('[data-oc]'), op = d.querySelectorAll('[data-open]');
if (!oe.length && !op.length) return null;
var pr = oc();
pr.then(function (c) {
var tt = 0;
if (c) [].forEach.call(oe, function (e) {
var s = count(ocv(c, e.getAttribute('data-oc'))), old = e.textContent;
if (s === old) return;
e.textContent = s;
var m = !tt && new RegExp('(^|[^\\d’\'.,\\u00a0\\u202f]|\\D[\\u00a0\\u202f])' + old.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') +
'(?![\\d’\']|[\\u00a0\\u202f]\\d)').exec(d.title);
if (m) { tt = 1; d.title = d.title.slice(0, m.index + m[1].length) + s + d.title.slice(m.index + m[0].length); }
});
if (op.length) (c ? Promise.resolve(c) : json('/daten/offen-n.json')).then(function (n) {
[].forEach.call(op, function (e) {
var s = e.getAttribute('data-open').split(':'), v = (n[s[0]] || {})[s[1]], x = e.querySelector('.ocn');
if (!x) { x = d.createElement('span'); x.className = 'ocn'; e.appendChild(x); }
x.innerHTML = v ? '<span class="sr">' + esc(L.colon) + ' </span>' + count(v) : '';
});
}, function () { });
});
return pr;
}
function later() {
var t = Date.now(), nx = 0;
[].forEach.call(d.querySelectorAll('[data-deadline]:not([data-gone]):not(.off)'), function (e) {
var w = when(e.getAttribute('data-deadline')); if (w > t && (!nx || w < nx)) nx = w;
});
if (nx && nx - t < 864e5) setTimeout(function () {
now = Date.now(); A.now = now; today = dnum(zday(now)); A.today = today;
deco(d, 1); A.oc = counts(); if (A.lx) A.lx(); later();
}, nx - t + 1000);
}
function roles(t) {
if (!t) return;
t.setAttribute('role', 'table');
[].forEach.call(t.querySelectorAll('thead,tbody'), function (g) { g.setAttribute('role', 'rowgroup'); });
[].forEach.call(t.querySelectorAll('tr'), function (r) { r.setAttribute('role', 'row'); });
[].forEach.call(t.querySelectorAll('th'), function (c) { c.setAttribute('role', c.closest('thead') ? 'columnheader' : 'rowheader'); });
[].forEach.call(t.querySelectorAll('td'), function (c) { c.setAttribute('role', 'cell'); });
}
[].forEach.call(d.querySelectorAll('table.ls,table.top,table.kv'), roles);
var PH = window.matchMedia ? matchMedia('(max-width:37.5rem)') : { matches: false };
function cut(t, total, more) {
var tb = t && t.tBodies[0]; if (!tb) return;
var wrap = t.closest('.scroll') || t, b = t._cb || null;
var rows = [].filter.call(tb.rows, function (r) { return !r.hidden && !r.classList.contains('ab'); });
[].forEach.call(tb.querySelectorAll('tr.cut'), function (r) { r.classList.remove('cut'); });
if (!PH.matches || t.hasAttribute('data-all') || rows.length <= 30) { if (b) b.remove(); t._cb = null; return; }
rows.slice(25).forEach(function (r) { r.classList.add('cut'); });
if (!b) {
b = t._cb = d.createElement('p'); b.className = 'cutb';
b.innerHTML = '<button type="button" class="all"></button>';
wrap.parentNode.insertBefore(b, wrap.nextSibling);
}
var btn = b.firstChild;
btn.textContent = fmt(L.all_n, { n: count(Math.max(total || 0, rows.length - !!tb.querySelector('tr.tier'))) });
btn.onclick = function () {
var r26 = rows[25];
t.setAttribute('data-all', '1');
[].forEach.call(tb.querySelectorAll('tr.cut'), function (r) { r.classList.remove('cut'); });
b.remove(); t._cb = null;
if (more) more();
var a = r26 && r26.querySelector('a'); if (a) a.focus();
};
}
[].forEach.call(d.querySelectorAll('table.ls:not(.tl)'), function (t) { cut(t); });
[].forEach.call(d.querySelectorAll('table.tl'), function (t) { cut(t); });
d.addEventListener('keydown', function (ev) {
if (ev.key !== 'Escape' || ev.defaultPrevented) return;
var m = d.querySelector('.masthead details[open]') || (ev.target.closest && ev.target.closest('details[open]'));
if (!m) return;
m.open = false;
var s = m.querySelector('summary'); if (s) s.focus();
});
[].forEach.call(d.querySelectorAll('figure.mc'), function (f) {
var t = f.querySelector('.cc table'), rd = f.querySelector('.rd');
if (!t || !rd) return;
var rows = [].slice.call(t.tBodies[0] ? t.tBodies[0].rows : []), cur = -1, lv = d.createElement('span');
lv.className = 'sr'; lv.setAttribute('aria-live', 'polite'); f.appendChild(lv);
function show(i, say) {
if (cur >= 0 && rows[cur]) rows[cur].classList.remove('on');
cur = i;
if (i < 0 || !rows[i]) { rd.textContent = ''; cur = -1; return; }
var r = rows[i], v = r.querySelector('em'), x = r.cells[0].textContent + L.colon + ' ' + (v ? v.textContent : '');
r.classList.add('on');
rd.textContent = '· ' + x;
if (say) lv.textContent = x;
}
t.tabIndex = 0;
t.addEventListener('pointerover', function (ev) { var r = ev.target.closest('tr'); if (r) show(rows.indexOf(r)); });
t.addEventListener('pointerleave', function (ev) { if (ev.pointerType !== 'touch' && d.activeElement !== t) show(-1); });
t.addEventListener('focus', function () { if (cur < 0) show(rows.length - 1); });
t.addEventListener('blur', function () { show(-1); });
t.addEventListener('keydown', function (ev) {
var k = ev.key, i = cur < 0 ? rows.length - 1 : cur;
if (k === 'ArrowLeft' || k === 'ArrowRight') i += k === 'ArrowRight' ? 1 : -1;
else if (k === 'Home') i = 0;
else if (k === 'End') i = rows.length - 1;
else return;
ev.preventDefault(); show(Math.max(0, Math.min(rows.length - 1, i)), 1);
});
});
var phs = [], cvx = null;
function fitph() {
var o = L.ph.split('|');
cvx = cvx || d.createElement('canvas').getContext('2d');
phs.forEach(function (i) {
var cs = getComputedStyle(i), w = i.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
cvx.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
for (var k = 0; k < o.length; k++) if (k === o.length - 1 || cvx.measureText(o[k]).width <= w) { i.placeholder = o[k]; break; }
});
}
[].forEach.call(d.querySelectorAll('form[role=search]'), function (f) {
var i = f.querySelector('input[name=q]');
if (!i) return;
i.type = 'search'; i.setAttribute('autocomplete', 'off'); i.setAttribute('spellcheck', 'false');
if (!i.placeholder) phs.push(i);
function go() { load('suche'); }
i.addEventListener('focus', go); i.addEventListener('input', go);
});
if (phs.length) {
fitph();
if (d.fonts && d.fonts.ready) d.fonts.ready.then(fitph);
var phq = 0;
addEventListener('resize', function () { if (!phq) phq = requestAnimationFrame(function () { phq = 0; fitph(); }); });
}
var tp = null, tq = 0;
function totop() {
if (tp || h.scrollHeight < 3 * innerHeight) return;
tp = d.createElement('a'); tp.href = '#top'; tp.className = 'totop'; tp.hidden = true;
tp.innerHTML = '<span aria-hidden="true">↑ </span>' + esc(L.top);
d.body.appendChild(tp);
var ly = scrollY;
addEventListener('scroll', function () {
if (!tq) tq = setTimeout(function () {
tq = 0; var y = scrollY;
if (y < 1.5 * innerHeight || y > ly + 2) tp.hidden = true; else if (y < ly - 2) tp.hidden = false;
ly = y;
}, 120);
}, { passive: true });
tp.addEventListener('click', function (ev) {
ev.preventDefault(); scrollTo(0, 0);
var n = d.querySelector('.masthead a.name'); if (n) n.focus();
});
}
totop();
var PW = /(^| )(stadt|ville|citta|city|gemeinde|commune|comune)( de| di| of)?$/;
function qparse(q, names) {
var ow = String(q || '').trim().split(/[\s\-]+/).filter(function (x) { return x; }), t = ow.map(function (w) { return words(w).join(''); }), best = null;
Object.keys(names || {}).forEach(function (k) {
var ns = (names[k] || []).slice();
if (k !== 'AG' && new RegExp('(^|[^A-Za-z])' + k + '([^A-Za-z]|$)').test(q)) ns.push(k);
ns.forEach(function (n) {
var nt = String(n).split(/[\s\-]+/).map(function (w) { return words(w).join(''); }).filter(function (x) { return x; });
if (!nt.length) return;
for (var i = 0; i + nt.length <= t.length; i++) {
var ok = true;
for (var x = 0; x < nt.length; x++) if (t[i + x] !== nt[x]) { ok = false; break; }
if (ok && !PW.test(t.slice(i < 2 ? 0 : i - 2, i).join(' ')) && (!best || nt.length > best.n)) best = { k: k, i: i, n: nt.length };
}
});
});
if (!best) return { q: String(q || '').trim(), k: '' };
var rest = ow.filter(function (w, i) {
return (i < best.i || i >= best.i + best.n) && !/^(kanton|canton|cantone|kt|ct)\.?$/i.test(w);
}).join(' ');
return { q: words(rest).every(stop) ? '' : rest, k: best.k };
}
var IT = '72 48 302', CL = '909', SYN = Object.create(null), S0 = { it: IT, ict: IT, edv: IT, informatik: IT,
informatique: IT, informatica: IT, bau: '45', construction: '45', costruzione: '45', reinigung: CL, nettoyage: CL,
pulizia: CL, cleaning: CL, personalverleih: '796', 'gebäudereinigung': CL, unterhaltsreinigung: CL,
strassenreinigung: '906 3414443', gartenpflege: '773', strada: '45233', strade: '45233', 'übersetzung': '7953',
traduction: '7953', traduzione: '7953', translation: '7953', 'déneigement': '9062' }, s0;
for (s0 in S0) SYN[fold(s0)] = S0[s0];
function syn(q, v) { return v && (SYN[q] || '').split(' ').some(function (p) { return p && !v.indexOf(p); }); }
var SW = ' ' + D.sw + ' ';
function stop(x) { return SW.indexOf(' ' + x + ' ') >= 0; }
function sw(t) { var u = t.filter(function (x) { return !stop(x); }); return u.length ? u : t; }
function cw(x) { return /^(city|ville|citta)$/.test(x) ? 'stadt' : x; }
function wscore(ws, q, top) {
if (q.length < 3) return ws.indexOf(q) < 0 ? 0 : top;
var b = 0, j, w, x, n = q.length;
for (j = 0; j < ws.length; j++) {
w = ws[j];
if (w === q) return top;
x = w.indexOf(q);
if (x < 0 || (top === 5 && n < 5)) continue;
b = Math.max(b, top === 5 ? (!x || (x > 2 && (n > 5 || x + n === w.length)) ? 5 : 1) : !x ? 3 : x > 2 && x + n === w.length ? 2 : 1);
}
return b;
}
var GW = ' dienstleistungen leistungen leistung arbeiten dienste dienst lieferungen lieferung anlagen systeme system projekte projekt planungen planung igung isierung ierung isation ation ',
GX = RegExp('s?(' + GW.trim().split(' ').join('|') + ')$'), PC = Object.create(null);
function gen(t) {
for (var n = t.length, u; GW.indexOf(t + ' ') < 0; t = u) if ((u = t.replace(GX, '')) === t) return t.length < n && t.length < 4;
return 1;
}
function part(ws, q) {
var c = PC[q], k, j, w, x, h, s, e;
if (!c) for (c = PC[q] = [], k = q.length - 1; k > 5; k--) {
if (k >= q.length - 2 && !gen(x = q.slice(0, k))) c.push('=' + x);
if (!gen(x = q.slice(-k))) c.push((k > 7 ? '^' : ' ') + x);
}
for (k = 0; k < c.length; k++) for (h = c[k][0], x = c[k].slice(1), j = 0; j < ws.length; j++) {
w = ws[j]; s = !w.indexOf(x); e = w.length > x.length + 2 && w.slice(-x.length) === x;
if (h === '=' ? w === x || e : h === '^' ? s || e : s && w !== x) return 1;
}
return 0;
}
function tscore(f, qt) {
var s = 0, i, best, q, a = qt.length > 1;
for (i = 0; i < qt.length; i++) {
q = cw(qt[i]);
best = syn(q, f.v) ? 5 : wscore(f.c, q, 5);
if (best < 5) best = Math.max(best, wscore(f.t, q, 4));
if (best < 4 && q.length < 5 && f.b.indexOf(q) >= 0) best = 4;
if (best < 2) best = Math.max(best, Math.min(2, wscore(f.b, q, 3)));
if (!best && q.length > 6) best = part(f.t, q) || part(f.c, q);
if (!best) return 0;
if (f.b.indexOf(q) < 0) a = false;
s += best;
}
return s + (a ? 4 : 0);
}
function topic(f, qt) { return qt.some(function (q) { q = cw(q); return !stop(q) && !PW.test(q) && (syn(q, f.v) || wscore(f.c, q, 5) > 4); }); }
function tier(f, qt) {
for (var i = 0; i < qt.length; i++) if (tscore(f, [qt[i]]) < 2) return 1;
return 0;
}
var VO = null;
function ed1(a, b) {
var i = 0, m = a.length, n = b.length;
if (m - n > 1 || n - m > 1) return 0;
while (i < m && a[i] === b[i]) i++;
return m < n ? a.slice(i) === b.slice(i + 1) : m > n ? a.slice(i + 1) === b.slice(i) :
a.slice(i + 1) === b.slice(i + 1) || (a[i] === b[i + 1] && a[i + 1] === b[i] && a.slice(i + 2) === b.slice(i + 2));
}
function dym(q, o) {
var hit = 0, c, add = function (s) {
s.split(/[^A-Za-zÀ-ÿ]+/).forEach(function (w) {
var f = fold(w), e;
if (f.length < 4) return;
e = VO[f] || (VO[f] = { n: 0, w: w });
e.n++; if (e.w === e.w.toUpperCase()) e.w = w;
});
};
if (!VO) {
VO = Object.create(null);
o.t.forEach(function (r) { r[1].forEach(function (v) { add(v.slice(3)); }); });
for (c in o.c) add(o.c[c].join(' '));
for (c in o.k) add(o.k[c].join(' '));
}
q = String(q).trim().split(/\s+/).map(function (w) {
var f = words(w).join(''), b = null, x;
if (f.length > 3 && !VO[f]) for (x in VO) if (ed1(f, x) && (!b || VO[x].n > b.n)) b = VO[x];
hit = b ? hit || 1 : f.length > 3 && !VO[f] ? -1 : hit;
return b ? b.w : w;
}).join(' ');
return hit > 0 ? q : '';
}
var LI = { de: 0, fr: 1, it: 2, en: 3 }[l];
function title(r) { var v = r[1][r[2] ? +r[2].charAt(LI) : 0] || r[1][0]; return { t: v.slice(3), l: v.slice(0, 2) }; }
function twords(r, o) {
if (!r.fw) r.fw = { t: words(r[1].map(function (v) { return v.slice(3); }).join(' ')).map(cw), c: words((o.c[r[4]] || []).join(' ')), b: words(o.b[r[5]]).map(cw), v: r[4] || '' };
return r.fw;
}
window.AR = { l: l, B: B, v: D.v, iso: D.iso, L: L, fmt: fmt, esc: esc, count: count, date: date, fold: fold, words: words, slug: slug, firm: firm,
deco: deco, rel: rel, when: when, now: now, today: today, dnum: dnum, zday: zday, load: load, json: json, totop: totop,
roles: roles, cut: cut, ph: PH, qparse: qparse, tscore: tscore, tier: tier, twords: twords, syn: SYN, sw: sw, oc: null,
cw: cw, dym: dym, li: LI, title: title, topic: topic };
A = window.AR;
A.oc = counts();
later();
})();
