(function () {
var A = window.AR; if (!A || A.alle) return; A.alle = 1;
var d = document, LL = {"de":{"rate_flag":"vermutlich Einheitspreis","per_firm":"Preise je Firma","fx_amount":"Betrag in Fremdwährung: {a}","not_published":"nicht publiziert"},"fr":{"rate_flag":"probablement un prix unitaire","per_firm":"prix par entreprise","fx_amount":"Montant en devise étrangère : {a}","not_published":"non publié"},"it":{"rate_flag":"probabilmente un prezzo unitario","per_firm":"prezzi per azienda","fx_amount":"Importo in valuta estera: {a}","not_published":"non pubblicato"},"en":{"rate_flag":"probably a unit rate","per_firm":"prices per company","fx_amount":"Amount in a foreign currency: {a}","not_published":"not published"}}, L = LL[A.l] || LL.de, l = A.l, B = A.B, fmt = A.fmt, esc = A.esc, firm = A.firm;
var LI = { de: 0, fr: 1, it: 2, en: 3 }[l], DEC = l === 'en' ? '.' : ',', NB = l === 'en' ? '' : ' ';
function exact(v) {
var s = v.toFixed(2).split('.'), i = A.count(+s[0]) + (s[1] === '00' ? '' : '.' + s[1]);
return l === 'en' ? 'CHF ' + i : i + ' CHF';
}
function cell(v, u) {
if (!v) return '–<span class="sr"> ' + esc(L.not_published) + '</span>';
var t;
if (u === 'm') { var x = Math.round(v / 1e5) / 10; t = x === 0 ? '<' + NB + '0' + DEC + '1' : A.count(Math.floor(x)) + DEC + Math.round((x % 1) * 10); }
else { var k = Math.round(v / 1e3); t = k === 0 ? '<' + NB + '1' : A.count(k); }
return '<data value="' + v.toFixed(2) + '" title="' + esc(exact(v)) + '">' + t + '</data>';
}
function arow(r, u) {
var v = r[2][r[3] ? +r[3].charAt(LI) : 0] || r[2][0], tl = v.slice(0, 2), t = v.slice(3), amt, fx = '';
if (r[6] === 'f') amt = '–<span class="sub sb2">' + esc(L.per_firm) + '</span>';
else if (r[6] === 'x') {
amt = '–';
fx = '<span class="sub sb2">' + esc(fmt(L.fx_amount, { a: A.count(r[5][0]) + ' ' + r[5][1] })) + '</span>';
} else amt = cell(r[5], u) + (r[6] === 'r' ? '<span class="sub sb2 rt">' + esc(L.rate_flag) + '</span>' : '');
return '<tr><td class="mono d"><time datetime="' + r[0] + '">' + A.date(r[0]) + '</time></td><td><a href="' + B + '/' + l + '/auftrag/' + r[1] + '"' +
(tl !== l && tl !== '--' ? ' lang="' + tl + '"' : '') + '>' + esc(t) + '</a>' + fx + '</td><td>' + (r[4].map(firm).join(' · ') || '–') +
'</td><td class="r num">' + amt + '</td></tr>';
}
function frow(r, u) {
return '<tr><td>' + firm(r) + '</td><td class="r num">' + A.count(r[2]) + '</td><td class="r num">' + cell(r[3], u) + '</td></tr>';
}
[].forEach.call(d.querySelectorAll('[data-alle]'), function (el) {
var p = el.closest('p'), box = p && p.previousElementSibling;
if (box && box.classList.contains('cutb')) box = box.previousElementSibling;      // stand.js's phone button
var t = box && (box.tagName === 'TABLE' ? box : box.querySelector('table'));
if (!t || !t.tBodies[0]) return;
var kf = el.getAttribute('data-alle').indexOf('/kf/') >= 0, u = t.getAttribute('data-u') || (/\bum\b/.test(t.className) ? 'm' : 'k');
if (el.hasAttribute('data-t')) el.textContent = el.getAttribute('data-t');
el.hidden = false;
function load(focus) {
A.json(el.getAttribute('data-alle')).then(function (rows) {
t.tBodies[0].insertAdjacentHTML('beforeend', rows.map(function (r) { return kf ? frow(r, u) : arow(r, u); }).join(''));
t.setAttribute('data-all', '1');
A.roles(t); A.cut(t);
p.remove();
var r = focus >= 0 && t.tBodies[0].rows[focus], a = r && r.querySelector('a'); if (a) a.focus();
A.totop();
}, function () { if (!kf) location.href = el.href; else { p.hidden = false; el.textContent = A.L.failed; } });
}
el.addEventListener('click', function (ev) {
if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button) return;
ev.preventDefault();
load(t.tBodies[0].rows.length);
});
if (t._cb) { A.cut(t, +el.textContent.replace(/\D/g, '') || 0, function () { load(-1); }); p.hidden = true; }
});
})();
