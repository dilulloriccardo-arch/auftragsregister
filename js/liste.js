/* /js/liste.js (step 3b, 15.10.2026): the filters of a tender list — the hub, the 26 canton lists, the
   industry lists and their full-list pages. The section holding the list says its scope
   (data-liste="", "k:ZH" or "b:45") and its size at build time (data-n).
   Without JavaScript the list is whole as built. With it, once the browser is idle (at once when the
   address carries a selection), /daten/offen.json is read — every open tender, not only the rows the
   page shows — and a filter bar appears above the list: free text over the titles in every language,
   the authority and the CPV labels; canton; industry; deadline within 7 days. The list shows
   'N von M', said by a live region; the selection lives in the address (?q=&k=&b=&soon=1) so it can be
   shared; one button clears it, one link opens the alert form with the same canton and industry.
   A list cut to its first 100 rows gets them all in place ('Alle N anzeigen'). */
(function () {
  var A = window.AR; if (!A || A.liste) return; A.liste = 1;
  var d = document, LL = __L__, L = LL[A.l] || LL.de, l = A.l, B = A.B, fmt = A.fmt, esc = A.esc, fold = A.fold;
  var LI = { de: 0, fr: 1, it: 2, en: 3 }[l];
  var sec = d.querySelector('[data-liste]'); if (!sec) return;
  var scope = sec.getAttribute('data-liste') || '', sk = scope.indexOf('k:') === 0 ? scope.slice(2) : '',
    sb = scope.indexOf('b:') === 0 ? scope.slice(2) : '';
  var tbl = sec.querySelector('table.tl'), tb = tbl && tbl.tBodies[0]; if (!tb) return;
  var wrap = tbl.closest('.scroll') || tbl, orig = tb.innerHTML, allA = sec.querySelector('a[data-all]'), allB = null;
  var P = new URLSearchParams(location.search), st = { q: P.get('q') || '', k: (P.get('k') || '').toUpperCase(), b: P.get('b') || '', s: P.get('soon') === '1', all: false };
  var O = null, bar, cnt, abo, none, fq, fk, fb, fs, tm = 0, wait = null;
  function active() { return !!(st.q.trim() || st.k || st.b || st.s); }
  function title(r) { var v = r[1][r[2] ? +r[2].charAt(LI) : 0] || r[1][0]; return { t: v.slice(3), l: v.slice(0, 2) }; }
  function cants(r) { return r[3].replace(/\*/g, '').split(' ').filter(function (x) { return x; }); }
  function hay(r) { return fold(r[1].map(function (v) { return v.slice(3); }).join(' ') + ' ' + O.b[r[5]] + ' ' + (O.c[r[4]] || []).join(' ')); }
  function cut(s, n) { if (s.length <= n) return s; s = s.slice(0, n); var i = s.lastIndexOf(' '); return (i > n - 20 ? s.slice(0, i) : s).replace(/[\s,;:.\-–]+$/, '') + '…'; }
  function scoped() {
    return O.t.filter(function (r) {
      if (A.when(r[6]) <= A.now) return false;
      if (sk && cants(r).indexOf(sk) < 0) return false;
      return !(sb && r[4].slice(0, 2) !== sb);
    });
  }
  function match(r, qt) {
    if (st.k && cants(r).indexOf(st.k) < 0) return false;
    if (st.b && r[4].slice(0, 2) !== st.b) return false;
    if (st.s && (A.rel(r[6]) || { n: 99 }).n > 7) return false;
    if (qt.length) {
      if (!r.f) r.f = hay(r);
      for (var i = 0; i < qt.length; i++) if (r.f.indexOf(qt[i]) < 0) return false;
    }
    return true;
  }
  // a row as genera.tender_table() writes it
  function row(r) {
    var t = title(r), dl = r[6], cs = cants(r), fbk = r[3].indexOf('*') >= 0, lab = (O.c[r[4]] || [])[LI] || '';
    var sub = (cs.length > 1 ? L.multi + ' · ' : '') + cut(lab, 60);
    return '<tr data-deadline="' + esc(dl) + '"><td class="when mono d"><time datetime="' + dl.slice(0, 10) + '">' + A.date(dl) + '</time></td>' +
      '<td><a href="' + B + '/' + l + '/auftrag/' + r[0] + '/"' + (t.l !== l && t.l !== '--' ? ' lang="' + t.l + '"' : '') + '>' + esc(t.t) + '</a>' +
      (sub ? '<span class="sub sb2">' + esc(sub) + '</span>' : '') + '</td><td>' + esc(O.b[r[5]]) + '</td><td>' +
      cs.map(function (k) { return '<abbr' + (fbk ? ' class="fb"' : '') + ' title="' + esc(O.k[k] ? O.k[k][LI] : k) + '">' + k + '</abbr>'; }).join(' ') + '</td></tr>';
  }
  function byName(tab) { return function (a, b) { var x = fold(tab[a][LI]), y = fold(tab[b][LI]); return x < y ? -1 : x > y ? 1 : 0; }; }
  function build() {
    var sc = scoped(), kc = {}, bc = {}, h;
    sc.forEach(function (r) { cants(r).forEach(function (k) { kc[k] = (kc[k] || 0) + 1; }); var v = r[4].slice(0, 2); if (v) bc[v] = (bc[v] || 0) + 1; });
    bar = d.createElement('div'); bar.className = 'flt'; bar.setAttribute('role', 'group'); bar.setAttribute('aria-label', L.f_label);
    h = '<label class="fq">' + esc(L.f_q) + '<input type="search" autocomplete="off" spellcheck="false"></label>';
    if (!sk) h += '<label class="fk">' + esc(L.k_canton) + '<select><option value="">' + esc(L.f_k_all) + '</option>' +
      Object.keys(O.k).sort(byName(O.k)).map(function (k) { return '<option value="' + k + '">' + esc(O.k[k][LI]) + ' (' + A.count(kc[k] || 0) + ')</option>'; }).join('') + '</select></label>';
    if (!sb) h += '<label class="fb">' + esc(L.k_div) + '<select><option value="">' + esc(L.f_b_all) + '</option>' +
      Object.keys(O.d).filter(function (v) { return bc[v] || v === st.b; }).sort(byName(O.d)).map(function (v) {
        return '<option value="' + v + '">' + esc(O.d[v][LI]) + ' (' + A.count(bc[v] || 0) + ')</option>'; }).join('') + '</select></label>';
    h += '<label class="chk"><input type="checkbox"> ' + esc(L.f_soon) + '</label><button type="button">' + esc(L.f_clear) + '</button>' +
      '<a class="tag fa" href="">' + esc(L.f_abo) + '</a><p class="cnt" role="status" aria-live="polite"></p>';
    bar.innerHTML = h;
    wrap.parentNode.insertBefore(bar, wrap);
    none = d.createElement('p'); none.className = 'flt-none'; none.hidden = true; none.textContent = L.f_none;
    wrap.parentNode.insertBefore(none, wrap);
    fq = bar.querySelector('input[type=search]'); fk = bar.querySelector('.fk select'); fb = bar.querySelector('.fb select');
    fs = bar.querySelector('input[type=checkbox]'); cnt = bar.querySelector('.cnt'); abo = bar.querySelector('a.fa');
    fq.value = st.q; fs.checked = st.s;
    if (fk) { fk.value = st.k; if (fk.value !== st.k) st.k = ''; }
    if (fb) { fb.value = st.b; if (fb.value !== st.b) st.b = ''; }
    if (sk) st.k = ''; if (sb) st.b = '';
    fq.addEventListener('input', function () { clearTimeout(tm); tm = setTimeout(function () { st.q = fq.value; render(); }, 200); });
    if (fk) fk.addEventListener('change', function () { st.k = fk.value; render(); });
    if (fb) fb.addEventListener('change', function () { st.b = fb.value; render(); });
    fs.addEventListener('change', function () { st.s = fs.checked; render(); });
    bar.querySelector('button').addEventListener('click', function () {
      st.q = st.k = st.b = ''; st.s = false; fq.value = ''; fs.checked = false; if (fk) fk.value = ''; if (fb) fb.value = '';
      render(); fq.focus();
    });
  }
  function render() {
    var qt = fold(st.q).split(/[^0-9a-z]+/).filter(function (x) { return x; }), sc = scoped(), n;
    if (active() || st.all) {
      var rows = sc.filter(function (r) { return match(r, qt); });
      tb.innerHTML = rows.map(row).join(''); A.deco(tb); n = rows.length;
    } else {
      tb.innerHTML = orig; n = tb.querySelectorAll('tr:not([hidden])').length;
    }
    none.hidden = n > 0; wrap.hidden = !n;
    // the note on the page's own rows hidden since the build belongs to those rows only
    // the notes on the page's own rows (hidden since the build; 'the 100 nearest of …') belong to those rows
    [].forEach.call(sec.querySelectorAll('p.xh,p.fn'), function (x) { x.hidden = active() || st.all; });
    cnt.textContent = fmt(L.f_count, { n: A.count(n), m: A.count(sc.length) });
    var more = (allA && allA.closest('p')) || allB;
    if (more) {
      more.hidden = active() || st.all || n >= sc.length;
      (allA || allB.firstChild).textContent = fmt(L.all_n, { n: A.count(sc.length) });
    }
    // the hub's 'next deadline' tile: the next one still ahead, not the build's
    var nx = !scope && d.querySelector('a.fig.date time');
    if (nx && sc.length) {
      var m = sc.reduce(function (a, r) { return A.when(r[6]) < A.when(a) ? r[6] : a; }, sc[0][6]);
      nx.setAttribute('datetime', m.slice(0, 10)); nx.textContent = A.date(m);
    }
    var p = [], k = st.k || sk, b = st.b || sb, a = [];
    if (st.q.trim()) p.push('q=' + encodeURIComponent(st.q.trim()));
    if (st.k) p.push('k=' + st.k); if (st.b) p.push('b=' + st.b); if (st.s) p.push('soon=1');
    try { history.replaceState(null, '', location.pathname + (p.length ? '?' + p.join('&') : '') + location.hash); } catch (e) { }
    if (k) a.push('k=' + k); if (b) a.push('b=' + b);
    abo.href = B + '/' + l + '/ausschreibungen/abo/' + (a.length ? '?' + a.join('&') : '');
    A.totop();
  }
  function ready() {
    if (!wait) wait = A.json('/daten/offen.json').then(function (o) { O = o; build(); render(); }, function () { wait = null; });
    return wait;
  }
  // all rows in place: the cut list's link (to its full page) or, on the hub, a button
  function showAll(ev) {
    if (ev) ev.preventDefault();
    var k = tb.rows.length;
    ready().then(function () {
      if (!O) { if (allA) location.href = allA.href; return; }
      st.all = true; render();
      var r = tb.rows[k], a = r && r.querySelector('a');
      if (a) a.focus();
    });
  }
  if (allA) allA.addEventListener('click', showAll);
  var total = +sec.getAttribute('data-n') || 0;
  if (!allA && total > tb.rows.length) {
    allB = d.createElement('p');
    allB.innerHTML = '<button type="button" class="all">' + esc(fmt(L.all_n, { n: A.count(total) })) + '</button>';
    wrap.parentNode.insertBefore(allB, wrap.nextSibling);
    allB.firstChild.addEventListener('click', showAll);
  }
  if (active()) ready();
  else if (window.requestIdleCallback) requestIdleCallback(ready, { timeout: 2500 });
  else setTimeout(ready, 1200);
})();
