/* /js/liste.js (step 3b, 15.10.2026; fix round 1, 20.10.2026): the filters of a tender list — the hub, the 26 canton
   lists, the industry lists and their full-list pages. The section holding the list says its scope (data-liste="",
   "k:ZH" or "b:45") and its size at build time (data-n); its filter bar is in the page (genera.flt_bar), shown
   only with JavaScript, so nothing moves when this script arrives.
   On the first interaction with the bar (at once when the address carries a selection), /daten/offen.json is read —
   every open tender, not only the rows the page shows — and the bar works: free text over the titles in every
   language, the authority and the CPV labels, ranked (a word of the topic or the start of a title's word before a word
   merely inside another: 'Reinigung' finds 'Gebäudereinigung' before 'Vereinigung'), a canton named in it becoming the
   canton filter ('Reinigung Zürich'); canton and industry, each option with its count for the rest of the
   selection; the order (nearest deadline or newest); new ones only (first published on the latest day); deadline
   within 7 days. The list shows 'N von M', said by a live region; the selection lives in the address
   (?q=&k=&b=&sort=&neu=1&soon=1) so it can be shared; with a selection in the address the list is scrolled to and
   its count focused. No result: what would give some (a word less, a neighbouring canton) and the alert. One
   button clears it all, one link opens the alert form with the same canton and industry. A list cut to its first
   100 rows gets them all in place ('Alle N anzeigen'); on a phone it shows 25 rows first.
   Fix round 3 (21.10.2026): the order chosen is the order shown: the matches of a word part come after a divider
   ('Weitere Treffer (Wortteil)'), each group in that order; the suggestions of an empty result are separated; the
   count takes the focus with a short highlight, not an input's ring; a keyword that names a Branche ('Reinigung')
   carries it to the alert form; /daten/offen.json (150 KB) waits for the first touch of the bar, and until then the
   count line and the next deadline come from the page and /stand.js's live count.
   Fix round 4 (21.10.2026): the stop words of the four languages off the query while another word remains ('Reinigung an
   Schulen' = 'Reinigung Schulen'); the divider above the first match of a word part, also when no row matches whole;
   a deadline passing while the page is open leaves its row in place (/stand.js) and the count line follows (A.lx). */
(function () {
  var A = window.AR; if (!A || A.liste) return; A.liste = 1;
  var d = document, LL = __L__, L = LL[A.l] || LL.de, l = A.l, B = A.B, fmt = A.fmt, esc = A.esc, fold = A.fold;
  var LI = { de: 0, fr: 1, it: 2, en: 3 }[l];
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
  var O = null, none, zs, tm = 0, wait = null, first = true, aboQ = '';
  var fq = bar.querySelector('input[name=q]'), fk = bar.querySelector('select[name=k]'), fb = bar.querySelector('select[name=b]'),
    fo = bar.querySelector('select[name=sort]'), fn = bar.querySelector('input[name=neu]'), fs = bar.querySelector('input[name=soon]'),
    cnt = bar.querySelector('.cnt'), abo = bar.querySelector('a.fa'), fan = bar.querySelector('.fan'), fd = bar.querySelector('details'),
    act = bar.querySelector('.fn0'), clr = bar.querySelector('button.clr'), fan0 = fan ? fan.textContent : '';
  // the neighbours of each canton, for 'nothing here — in Bern 3'
  var NB = { AG: 'ZH LU ZG SO BL BE', AI: 'AR SG', AR: 'AI SG', BE: 'JU SO AG LU OW NW UR VS VD FR NE', BL: 'BS AG SO JU', BS: 'BL',
    FR: 'BE VD NE', GE: 'VD', GL: 'SZ UR GR SG', GR: 'TI UR GL SG', JU: 'BE SO BL', LU: 'AG BE OW NW SZ ZG', NE: 'VD FR BE',
    NW: 'OW LU BE UR', OW: 'NW LU BE UR', SG: 'AR AI TG ZH SZ GL GR', SH: 'ZH TG', SO: 'BE JU BL AG', SZ: 'ZG LU UR GL SG ZH',
    TG: 'SH ZH SG', TI: 'VS UR GR', UR: 'SZ NW OW BE VS TI GR GL', VD: 'GE FR NE BE VS', VS: 'VD BE UR TI', ZG: 'ZH AG LU SZ',
    ZH: 'SH TG SG SZ ZG AG' };
  function cants(r) { return r[3].replace(/\*/g, '').split(' ').filter(function (x) { return x; }); }
  function title(r) { var v = r[1][r[2] ? +r[2].charAt(LI) : 0] || r[1][0]; return { t: v.slice(3), l: v.slice(0, 2) }; }
  function cut(s, n) { if (s.length <= n) return s; s = s.slice(0, n); var i = s.lastIndexOf(' '); return (i > n - 20 ? s.slice(0, i) : s).replace(/[\s,;:.\-–]+$/, '') + '…'; }
  // the query as typed, its canton (when the list has no canton of its own) and its words, the stop words off while
  // another word remains (fix round 4: 'Reinigung an Schulen' = 'Reinigung Schulen')
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
  // every filter but the ones named in skip ('k', 'b'): the options' counts are those of the rest of the selection
  function pass(r, qp, skip) {
    var k = ek(qp);
    if (skip !== 'k' && k && cants(r).indexOf(k) < 0) return false;
    if (skip !== 'b' && st.b && r[4].slice(0, 2) !== st.b) return false;
    if (st.s && (A.rel(r[6]) || { n: 99 }).n > 7) return false;
    if (st.n && r[7] !== O.nd) return false;
    if (qp.t.length && !A.tscore(A.twords(r, O), qp.t)) return false;
    return true;
  }
  // strong: every word of the query in the topic, a title's word start or a compound's end; weak ones after them
  function tier(r, qp) {
    var f = A.twords(r, O);
    for (var i = 0; i < qp.t.length; i++) if (A.tscore(f, [qp.t[i]]) < 2) return 1;
    return 0;
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
  // the options of the two selects, with their counts for the rest of the selection (fix round 1: they were the
  // list's totals whatever was typed)
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
  // nothing found: a word less, a neighbouring canton, the alert (fix round 1); separated by ' · ' (fix round 3)
  function suggest(sc, qp, k) {
    var out = [];
    if (qp.t.length > 1) qp.t.forEach(function (w, i) {
      var t2 = qp.t.filter(function (x, j) { return j !== i; }), n = sc.filter(function (r) { return pass(r, { k: qp.k, t: t2 }); }).length;
      if (n) out.push('<a href="#" data-q="' + esc(qp.q.split(/\s+/).filter(function (x) { return fold(x).replace(/[^0-9a-z]/g, '') !== w; }).join(' ')) + '">' + esc(fmt(L.z_drop, { t: w, n: A.count(n) })) + '</a>');
    });
    if (k && !sk && NB[k]) NB[k].split(' ').forEach(function (c) {
      var n = sc.filter(function (r) { return cants(r).indexOf(c) >= 0 && pass(r, qp, 'k'); }).length;
      if (n && out.length < 6) out.push('<a href="#" data-k="' + c + '">' + esc(fmt(L.z_near, { c: O.k[c][LI], n: A.count(n) })) + '</a>');
    });
    out.push('<a href="' + esc(abo.href) + '">' + esc(L.z_abo) + '</a>');
    zs.innerHTML = '<strong>' + esc(L.z_h) + '</strong> ' + out.join(' · ');
  }
  // the Branche a keyword names, for the alert (fix round 3: 'Reinigung' -> 90): its synonym, else the Branche or the
  // Bereiche whose names start with it, when one Branche holds most of them
  function kwdiv(qt, th) {
    var s = {}, tot = 0, best = '', i, v;
    for (i = 0; i < qt.length; i++) if (A.syn[qt[i]]) return A.syn[qt[i]].slice(0, 2);
    function hit(ns) {
      var ws = A.words(ns.join(' '));
      return qt.some(function (q) { return q.length > 2 && ws.some(function (w) { return w.indexOf(q) === 0; }); });
    }
    (th.d || []).forEach(function (e) { if (hit(e[1])) s[e[0]] = (s[e[0]] || 0) + 1e6; });
    (th.s || []).forEach(function (e) { if (hit(e[1])) { v = e[0].slice(0, 2); s[v] = (s[v] || 0) + (e[2] || 1); } });
    for (v in s) { tot += s[v]; if (!best || s[v] > s[best]) best = v; }
    return best && O.d[best] && s[best] * 2 >= tot ? best : '';
  }
  function aboLink(k, b, qp) {
    var a = [];
    if (k) a.push('k=' + k); if (b) a.push('b=' + b);
    abo.href = B + '/' + l + '/ausschreibungen/abo/' + (a.length ? '?' + a.join('&') : '');
    if (fan) { fan.hidden = !qp.q; fan.textContent = fan0; }
    if (b || !qp.q) return;
    // a keyword's Branche, once the topics are in (the alert itself filters by canton and Branche only)
    var my = aboQ = qp.q;
    A.json('/daten/suche/themen.json').then(function (th) {
      if (my !== aboQ) return;
      var v = kwdiv(qp.t, th); if (!v) return;
      a.push('b=' + v);
      abo.href = B + '/' + l + '/ausschreibungen/abo/?' + a.join('&');
      if (fan) fan.textContent = fmt(L.f_abo_kwb, { b: O.d[v][LI] });
    }, function () { });
  }
  function render() {
    var qp = query(), sc = scoped(), n, k = ek(qp), on = active() || st.all;
    if (on) {
      var rows = sc.filter(function (r) { return pass(r, qp); });
      var neu = st.o === 'neu', html = '', w = -1;
      rows.forEach(function (r) { r.ti = qp.t.length ? tier(r, qp) : 0; });
      rows.sort(function (a, b) {
        return a.ti - b.ti || (neu ? (a[7] < b[7] ? 1 : a[7] > b[7] ? -1 : 0) : 0) || (A.when(a[6]) - A.when(b[6]));
      });
      // the order chosen holds within each group; the matches of a word part after a divider of their own
      // (fix round 4: above the first match of a word part even when it is the first row, or the only one)
      rows.forEach(function (r, i) { if (w < 0 && r.ti) w = i; });
      rows.forEach(function (r, i) {
        if (i === w) html += '<tr class="tier"><td colspan="4">' + esc(L.tier_w) + '</td></tr>';
        html += row(r);
      });
      tb.innerHTML = html;
      n = rows.length;
    } else {
      tb.innerHTML = orig;
      n = tb.querySelectorAll('tr[data-deadline]').length;
    }
    // the alert after the first ten rows, on a phone
    if (abRow) {
      var dr = tb.querySelectorAll('tr[data-deadline]:not([hidden])');
      if (on && dr.length) { var at = dr[Math.min(10, dr.length) - 1]; at.parentNode.insertBefore(abRow, at.nextSibling); }
    }
    A.deco(tb);
    if (!on) n = tb.querySelectorAll('tr[data-deadline]:not([hidden])').length;
    A.roles(tbl);
    // the alert with the list's canton and industry; a keyword that names a Branche brings it (fix round 3)
    aboLink(k, st.b || sb, qp);
    none.hidden = n > 0; wrap.hidden = !n; zs.hidden = n > 0;
    if (!n) suggest(sc, qp, k);
    // the notes on the page's own rows (hidden since the build; 'the 100 nearest of …') belong to those rows
    [].forEach.call(sec.querySelectorAll('p.xh,p.fn'), function (x) { x.hidden = on; });
    cnt.textContent = !on && n < sc.length ? fmt(L.f_first, { k: A.count(n), m: A.count(sc.length) })
      : fmt(L.f_count, { n: A.count(n), m: A.count(sc.length) });
    // on a phone, 25 rows and 'Alle N anzeigen' (the whole list when the page shows only its first rows)
    A.cut(tbl, on ? n : sc.length, on || !(allA || allB) ? null : function () { showAll(); });
    var more = (allA && allA.closest('p')) || allB;
    if (more) {
      more.hidden = on || n >= sc.length || !!tbl._cb;
      (allA || allB.firstChild).textContent = fmt(L.all_n, { n: A.count(sc.length) });
    }
    // the hub's 'next deadline' tile: the next one still ahead, not the build's
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
      // a selection in the address (the search's hand-off, a shared link): the list in view, its count said and
      // briefly lit (fix round 3: no 3-px ring on a line of text)
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
    // what the reader did before the data came stands (the field typed in, a box ticked)
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
    // a phone turned wide: the controls in view
    if (A.ph.addEventListener) A.ph.addEventListener('change', function () { if (!A.ph.matches && fd) fd.open = true; });
  }
  function ready() {
    if (!wait) wait = A.json('/daten/offen.json').then(function (o) { O = o; bind(); render(); }, function () { wait = null; });
    return wait;
  }
  // all rows in place: the cut list's link (to its full page) or, on the hub, a button
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
    allB.innerHTML = '<button type="button" class="all">' + esc(fmt(L.all_n, { n: A.count(total) })) + '</button>';
    wrap.parentNode.insertBefore(allB, wrap.nextSibling);
    allB.firstChild.addEventListener('click', showAll);
  }
  // a phone's cut table (stand.js): one button, with the whole count, for the whole list
  if (tbl._cb && (allA || allB)) { A.cut(tbl, total, showAll); ((allA && allA.closest('p')) || allB).hidden = true; }
  // until the data comes: the count line from the page's rows and the live count of /stand.js (offen-dl.json, 30 KB:
  // read only once a deadline has passed since the build), the next deadline from the first row still shown
  // (fix round 4: a row muted since its deadline passed while the page is open no longer counts, A.lx)
  var live = 'tr[data-deadline]:not([hidden]):not(.off)';
  function pre(c) {
    var n = tb.querySelectorAll(live).length,
      m = c ? (scope ? (c[scope.charAt(0)] || {})[scope.slice(2)] || 0 : c.a) : total;
    m = Math.max(m, n);
    if (!O) cnt.textContent = n < m ? fmt(L.f_first, { k: A.count(n), m: A.count(m) }) : fmt(L.f_count, { n: A.count(n), m: A.count(m) });
    var nx = !scope && d.querySelector('a.fig.date time'), r0 = tb.querySelector(live);
    if (!O && nx && r0) { var t = r0.getAttribute('data-deadline'); nx.setAttribute('datetime', t.slice(0, 10)); nx.textContent = A.date(t); }
  }
  A.lx = function () { (A.oc || Promise.resolve(null)).then(pre, function () { }); };
  if (active()) ready();
  else {
    pre(null);
    A.lx();
    // the first touch of the bar (a pointer over it, the focus in it) fetches the data
    var go = function () { bar.removeEventListener('pointerover', go); bar.removeEventListener('focusin', go); ready(); };
    bar.addEventListener('pointerover', go); bar.addEventListener('focusin', go);
  }
})();
