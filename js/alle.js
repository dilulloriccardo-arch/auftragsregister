/* /js/alle.js (fix round 1, 20.10.2026): the rest of a cut table, in place. A buyer page shows its 60 newest
   awards and says so ('die 60 neuesten von 438'); its link to the authority's CSV file becomes 'Alle 438 anzeigen'
   and adds the others from /daten/ab/<slug>.json, as the page's table writes them (title in the page's language
   where the publication has one, the winners, the amount in the page's scale, a unit rate or prices per firm
   flagged). A canton page shows the 60 companies with the most awards; 'Alle N anzeigen' adds the others from
   /daten/kf/<canton>.json. Shared by the four languages; without JavaScript the CSV file is the way to all. */
(function () {
  var A = window.AR; if (!A || A.alle) return; A.alle = 1;
  var d = document, LL = __L__, L = LL[A.l] || LL.de, l = A.l, B = A.B, fmt = A.fmt, esc = A.esc;
  var LI = { de: 0, fr: 1, it: 2, en: 3 }[l], DEC = l === 'en' ? '.' : ',', NB = l === 'en' ? '' : ' ';
  function slug(s) {
    s = String(s).toLowerCase().replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss');
    if (s.normalize) s = s.normalize('NFKD');
    try { s = s.replace(new RegExp('\\p{M}', 'gu'), ''); } catch (e) { s = s.replace(/[̀-ͯ]/g, ''); }
    return s.replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70) || 'x';
  }
  function firm(x) {
    var p = x[1], name = esc(x[0]);
    return p ? '<a href="' + B + '/' + l + '/unternehmen/' + (p === 1 ? slug(x[0]) : p) + '/">' + name + '</a>' : name;
  }
  // an amount in the table's scale, the exact one on hover (formato.column_cell)
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
  // a buyer's award: [date, page, titles, map, winners, amount, kind]
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
  // a canton's company: [name, page, awards, CHF sum]
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
    // focus: the row to focus once the rest is in (-1: none, the phone's button has focused its own)
    function load(focus) {
      A.json(el.getAttribute('data-alle')).then(function (rows) {
        t.tBodies[0].insertAdjacentHTML('beforeend', rows.map(function (r) { return kf ? frow(r, u) : arow(r, u); }).join(''));
        t.setAttribute('data-all', '1');
        A.roles(t); A.cut(t);
        p.remove();
        var r = focus >= 0 && t.tBodies[0].rows[focus], a = r && r.querySelector('a'); if (a) a.focus();
        A.totop();
      }, function () { if (!kf) location.href = el.href; else { p.hidden = false; el.textContent = L.failed; } });
    }
    el.addEventListener('click', function (ev) {
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button) return;
      ev.preventDefault();
      load(t.tBodies[0].rows.length);
    });
    // a phone's cut table (stand.js, its first 25 rows): one button, 'Alle 438 anzeigen', for all of them
    if (t._cb) { A.cut(t, +el.textContent.replace(/\D/g, '') || 0, function () { load(-1); }); p.hidden = true; }
  });
})();
