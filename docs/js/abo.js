(function () {
var d = document, f = d.getElementById('abo'); if (!f) return;
var LL = {"de":{"email_missing":"Bitte geben Sie Ihre E-Mail-Adresse ein.","email_bad":"Diese E-Mail-Adresse ist nicht gültig. Beispiel: name@firma.ch","sel":"({n} ausgewählt)","pv":"≈ {w} neue Ausschreibungen pro Woche","pv_lt":"weniger als eine neue Ausschreibung pro Woche","sum_sel":"Sie abonnieren: {s}","all_ch":"ganze Schweiz","all_b":"alle Branchen","bf_none":"Keine Branche passt zu «{q}»."},"fr":{"email_missing":"Indiquez votre adresse e-mail.","email_bad":"Cette adresse e-mail n’est pas valable. Exemple : nom@entreprise.ch","sel":"(sélection : {n})","pv":"≈ {w} nouveaux appels d’offres par semaine","pv_lt":"moins d’un nouvel appel d’offres par semaine","sum_sel":"Vous vous abonnez à : {s}","all_ch":"toute la Suisse","all_b":"tous les secteurs","bf_none":"Aucun secteur ne correspond à « {q} »."},"it":{"email_missing":"Inserisci il tuo indirizzo e-mail.","email_bad":"Questo indirizzo e-mail non è valido. Esempio: nome@azienda.ch","sel":"(selezionati: {n})","pv":"≈ {w} nuovi bandi alla settimana","pv_lt":"meno di un nuovo bando alla settimana","sum_sel":"Ti iscrivi a: {s}","all_ch":"tutta la Svizzera","all_b":"tutti i settori","bf_none":"Nessun settore trovato per «{q}»."},"en":{"email_missing":"Please enter your email address.","email_bad":"This email address is not valid. Example: name@company.ch","sel":"({n} selected)","pv":"≈ {w} new tenders a week","pv_lt":"fewer than one new tender a week","sum_sel":"You’re subscribing to: {s}","all_ch":"all of Switzerland","all_b":"all sectors","bf_none":"No sector matches “{q}”."}}, A = window.AR, l = d.documentElement.lang, L = LL[l] || LL.de;
var m = f.querySelector('.msg'), b = f.querySelector('button[type=submit]'), em = f.elements.EMAIL, er = d.getElementById('abo-email-err'), busy = false;
function fmt(s, o) { return String(s).replace(/\{(\w+)\}/g, function (x, k) { return k in o ? o[k] : x; }); }
function vals(n) { return [].map.call(f.querySelectorAll('input[name=' + n + ']:checked'), function (x) { return x.value; }); }
function j(n) { var v = vals(n); return v.length ? v.join(',') : 'ALLE'; }
function fill() { f.elements.KANTON.value = j('k'); f.elements.BRANCHE.value = j('b'); }
f.setAttribute('novalidate', '');
m.setAttribute('tabindex', '-1');
function check() {
var v = em.value.trim(), bad = !v ? L.email_missing : !/^[^\s@]+@[^\s@.]+(\.[^\s@.]+)*\.[^\s@.]{2,}$/.test(v) ? L.email_bad : '';
if (bad) { em.setAttribute('aria-invalid', 'true'); er.textContent = bad; er.hidden = false; }
else { em.removeAttribute('aria-invalid'); er.textContent = ''; er.hidden = true; }
return !bad;
}
em.addEventListener('blur', function () { if (em.value.trim()) check(); });
em.addEventListener('input', function () { if (em.getAttribute('aria-invalid')) check(); });
f.addEventListener('submit', function (ev) {
ev.preventDefault();
if (busy) return;
fill();
if (!check()) { em.focus(); return; }
busy = true; b.setAttribute('aria-disabled', 'true'); m.className = 'msg'; m.textContent = f.dataset.sending;
fetch(f.action + '?isAjax=1', { method: 'POST', body: new FormData(f) }).then(function (r) { return r.json(); }).then(function (r) {
if (r.success) m.textContent = f.dataset.ok;
else { busy = false; b.removeAttribute('aria-disabled'); m.className = 'msg err'; m.textContent = f.dataset.err; }
m.focus();
}).catch(function () { busy = false; b.removeAttribute('aria-disabled'); f.submit(); });
});
function counts() {
[].forEach.call(f.querySelectorAll('details.grp'), function (g) {
var s = g.querySelector('summary .sr');
if (!s) { s = d.createElement('span'); s.className = 'sr'; g.querySelector('summary').appendChild(s); }
s.textContent = ' ' + fmt(L.sel, { n: g.querySelectorAll('input:checked').length });
});
}
var pv = f.querySelector('.pv'), sm = f.querySelector('.sumry'), R = null;
function week(w) {
var s = w >= 10 ? String(Math.round(w)) : (Math.round(w * 10) / 10).toFixed(1).replace(/\.0$/, '');
return l === 'en' ? s : s.replace('.', ',');
}
function preview() {
if (!R) return;
var ks = vals('k'), bs = vals('b'), w = 0;
(ks.length ? ks : ['*']).forEach(function (k) {
(bs.length ? bs : ['*']).forEach(function (v) { w += ((R[k] || {})[v] || 0) / 8; });
});
pv.textContent = w > 0 && w < 1 ? L.pv_lt : fmt(L.pv, { w: week(w) });
}
function names(n) {
return [].map.call(f.querySelectorAll('input[name=' + n + ']:checked'), function (x) {
var t = x.nextElementSibling, b = t && t.querySelector('b');
return t ? (b ? t.textContent.slice(b.textContent.length) : t.textContent).trim() : x.value;
});
}
function summary() {
if (!sm) return;
var k = names('k'), b = names('b');
sm.textContent = fmt(L.sum_sel, { s: (k.length ? k.join(', ') : L.all_ch) + ' · ' + (b.length ? b.join(', ') : L.all_b) });
}
function changed() { fill(); counts(); preview(); summary(); }
var bq = d.getElementById('abo-bq'), bqn = f.querySelector('.bqn');
if (bq && A) bq.addEventListener('input', function () {
var q = A.fold(bq.value.trim()), hit = 0;
[].forEach.call(f.querySelectorAll('details.grp'), function (g) {
var n = 0;
[].forEach.call(g.querySelectorAll('label'), function (lb) {
var ok = !q || A.fold(lb.textContent).indexOf(q) >= 0;
lb.hidden = !ok; if (ok) n++;
});
g.hidden = !n; if (q) g.open = n > 0; hit += n;
});
if (bqn) { bqn.hidden = !!hit || !q; bqn.textContent = hit || !q ? '' : fmt(L.bf_none, { q: bq.value.trim() }); }
});
if (bq) bq.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') ev.preventDefault(); });
f.addEventListener('change', changed);
var K = 'AG AI AR BE BL BS FR GE GL GR JU LU NE NW OW SG SH SO SZ TG TI UR VD VS ZG ZH'.split(' ');
function pre() {
var q, nm = {}, hit = 0;
try { q = new URLSearchParams(location.search); } catch (x) { return; }
if (!q.has('k') && !q.has('b')) return;
try { nm = JSON.parse(d.getElementById('abo-names').textContent) || {}; } catch (x) { nm = {}; }
[['k', function (v) { return K.indexOf(v) >= 0; }], ['b', function (v) { return /^[0-9]{2}$/.test(v); }]].forEach(function (g) {
var n = g[0], ok = g[1], names = nm[n] || {}, box = f.querySelector('.pills[data-g="' + n + '"]'), seen = {}, c = 0;
q.getAll(n).join(',').split(',').forEach(function (v) {
v = v.trim().toUpperCase();
if (c >= 5 || !v || !ok(v) || seen[v]) return;
seen[v] = 1;
var i = null, all = f.querySelectorAll('input[name="' + n + '"]'), z;
for (z = 0; z < all.length; z++) if (all[z].value === v) { i = all[z]; break; }
if (!i) {
var t = Object.prototype.hasOwnProperty.call(names, v) ? String(names[v]) : '';
if (!t || !box) return;
var lb = d.createElement('label'), s = d.createElement('span'), ref = null, bx = box;
i = d.createElement('input'); i.type = 'checkbox'; i.name = n; i.value = v; s.className = 'tag'; s.textContent = t;
lb.appendChild(i); lb.appendChild(s);
if (n === 'k') { for (z = 0; z < all.length; z++) if (all[z].value > v) { ref = all[z].parentNode; break; } }
else {
[].forEach.call(f.querySelectorAll('details[data-c]'), function (dd) {
if ((' ' + dd.getAttribute('data-c') + ' ').indexOf(' ' + v + ' ') >= 0) bx = dd.querySelector('.pills') || bx;
});
ref = bx.firstChild;
}
bx.insertBefore(lb, ref);
}
i.checked = true; c++; hit++;
var gr = i.closest ? i.closest('details') : null; if (gr) gr.open = true;
});
});
if (!hit) return;
fill();
var sec = f.parentNode || f;
try { sec.scrollIntoView({ block: 'start' }); } catch (x) { }
try { if (window.matchMedia && matchMedia('(pointer:fine)').matches) em.focus({ preventScroll: true }); } catch (x) { }
}
pre(); fill(); counts(); summary();
if (A) {
var go = function () {
A.json('/daten/abo-rate.json').then(function (x) { R = x; preview(); }, function () { });
};
if (window.requestIdleCallback) requestIdleCallback(go, { timeout: 2000 }); else setTimeout(go, 800);
}
})();
