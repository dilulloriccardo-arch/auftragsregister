/* /js/kb.js (step 3b, 15.10.2026): a canton's awards in one industry, on /xx/kanton/XX/. The canton page
   ranks its industries; each row links to the industry's national page, which is what it does without
   JavaScript. With it the row opens, in place and as ?b=72 (an address that can be shared), the canton's
   awards in that industry: the companies with the most of them (count and CHF sum, as the site's own
   tables count them) and the newest awards, from /daten/kb/XX.json (one small file per canton, shared
   by the four languages; titles as published, the CSV files' rule). Who won the most IT contracts in
   Bern is one click.
   Fix round 1 (20.10.2026): the address is #kb-72 (the Branche pages link to it; without JavaScript it leads to the
   Branche's row), the panel scrolls into view before it takes the focus, its tables use the page's money scale,
   and it says how many of its awards count here only as the authority's seat, with a toggle that leaves them out. */
(function () {
  var A = window.AR; if (!A || A.kb) return; A.kb = 1;
  var d = document, LL = __L__, L = LL[A.l] || LL.de, l = A.l, B = A.B, fmt = A.fmt, esc = A.esc;
  var LI = { de: 0, fr: 1, it: 2, en: 3 }[l];
  var m = location.pathname.match(/\/kanton\/([A-Z]{2})\/$/); if (!m) return;
  var K = m[1], fig = d.querySelector('figure.rk[aria-labelledby="chart-sectors"]'); if (!fig) return;
  var links = [].slice.call(fig.querySelectorAll('a[href*="/branche/"]')), panel = null, from = null, PU = fig.getAttribute('data-u') || '', xo = false;
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
  // a money column in one unit, as formato.unit_for()/scaled(): thousands, or millions from a median of a million
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
    // without the awards placed here only as the authority's seat (the toggle): their own lists
    var ex = xo && x.x, fs = ex ? x.fx : x.f, rs = ex ? x.r.filter(function (r) { return !r[6]; }).concat(x.rx || []) : x.r,
      na = ex ? x.a - x.x : x.a, nk = ex ? x.kx : x.k;
    var cn = o.c[l] || o.c.de, name = x.n[LI], uf = PU || unit(fs.map(function (r) { return r[3]; })), ur = PU || unit(rs.map(function (r) { return r[5]; }));
    var h = '<button type="button" class="tag kbx">' + esc(L.kb_close) + '</button>' +
      '<h2 id="kb-h">' + esc(fmt(L.kb_h, { div: name, name: cn[0], of: cn[1] })) + '</h2>' +
      '<p class="sub m10">' + esc(fmt(L.kb_lead, { n: na === 1 ? L.aw_1 : fmt(L.aw_n, { n: A.count(na) }), f: nk === 1 ? L.kb_f1 : fmt(L.kb_fn, { n: A.count(nk) }) })) + '</p>' +
      (x.x ? '<p class="sub m10">' + esc(fmt(L.kb_fb, { k: A.count(x.x), p: Math.round(100 * x.x / x.a) + (l === 'de' ? '\u00a0%' : l === 'fr' ? '\u202f%' : '%') })) + '</p>' +
        '<label class="fbx"><input type="checkbox"' + (ex ? ' checked' : '') + '> ' + esc(L.kb_fbx) + '</label>' : '') +
      '<h3>' + esc(L.kb_top) + '</h3><div class="scroll"><table><caption class="sr">' + esc(L.kb_top) + '</caption><thead><tr><th scope="col">' + esc(L.company) + '</th>' +
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
      var at = fig.closest('.half') || fig; at.parentNode.insertBefore(panel, at.nextSibling);
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
  function show(v, push, scroll) {
    A.json('/daten/kb/' + K + '.json').then(function (o) {
      if (!render(o, v)) return;
      try { history[push ? 'pushState' : 'replaceState'](null, '', location.pathname + '#kb-' + v); } catch (e) { }
      // into view first, then the focus without a second jump (fix round 1: focus() scrolled it half out of view)
      if (scroll) { try { panel.scrollIntoView({ block: 'start' }); } catch (e) { } panel.focus({ preventScroll: true }); }
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
  var hint = d.createElement('p'); hint.className = 'sub m10'; hint.textContent = L.kb_hint;
  var lede = fig.querySelector('.lede'); if (lede) lede.parentNode.insertBefore(hint, lede.nextSibling);
  // #kb-72 (and the older ?b=72)
  function fromUrl(scroll) {
    var v = (location.hash.match(/^#kb-(\d\d)$/) || [])[1] || new URLSearchParams(location.search).get('b');
    if (v && /^\d\d$/.test(v)) show(v, false, scroll); else if (panel) { panel.remove(); panel = null; }
  }
  addEventListener('popstate', function () { fromUrl(false); });
  addEventListener('hashchange', function () { fromUrl(true); });
  fromUrl(true);
})();
