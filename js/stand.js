/* /stand.js, on every page (step 3b, 15.10.2026). genera.py writes its data (D): the date of the newest
   publication, the words below in the four languages, the base path, the scripts' version and the nearest
   deadline of the open tenders.
   It does what depends on the reader's clock and nothing else, so the pages themselves never change
   because a day has passed:
   - the footer's data line (data-stand), as before;
   - every deadline (data-deadline): 'läuft heute ab, 14.00 Uhr', 'läuft morgen ab', 'noch 5 Tage',
     the classes .today and .soon; a list row whose deadline has passed since the build is hidden, with
     a note under its list and its section's count lowered; a tender page past its deadline shows the
     'Eingabefrist abgelaufen' state and loses its calendar link — at load, and again when the next deadline
     on the page passes while it is open (fix round 1);
   - every count of open tenders (data-oc) and the pills' counts (data-open): once a deadline has passed since
     the build, recounted from /daten/offen-dl.json, so a page never says 1'477 beside '92 von 1'469' (fix
     round 1);
   - the home's 'neu' badge reads 'heute' or 'seit gestern' only when that is true; else its date stays;
   - the search fields: their placeholder, and /js/suche.js at the first focus;
   - a 'Nach oben' link on long pages; on a phone, a long table shows 25 rows and 'Alle N anzeigen';
   - the stacked tables keep their table roles for screen readers (VoiceOver drops them with the CSS display);
   - Escape closes the open menu; the month under the pointer or the keyboard in a chart's unit line.
   Its helpers are window.AR, for the page type's own script (liste.js, suche.js, abo.js, kb.js, alle.js). */
(function () {
  var D = __DATA__, d = document, h = d.documentElement, l = D.L[h.lang] ? h.lang : 'de', L = D.L[l], B = D.B, A = null;
  function fmt(s, o) { return String(s).replace(/\{(\w+)\}/g, function (m, k) { return k in o ? o[k] : m; }); }
  function p2(n) { n = +n; return (n < 10 ? '0' : '') + n; }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  var GR = { de: '’', it: '’', fr: ' ', en: ',' };
  function count(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, GR[l]); }
  function date(iso) {
    var y = iso.slice(0, 4), m = +iso.slice(5, 7), x = +iso.slice(8, 10);
    return l === 'en' ? x + ' ' + D.mo[m - 1] + ' ' + y : p2(x) + '.' + p2(m) + '.' + y;
  }
  var MK; try { MK = new RegExp('\\p{M}', 'gu'); } catch (e) { MK = /[̀-ͯ]/g; }
  // the search's and the filters' folding, the same as genera.sfold(): case, accents, ß/ss, ä/ae
  function fold(s) {
    s = String(s || '').toLowerCase().replace(/ß/g, 'ss').replace(/æ/g, 'ae').replace(/œ/g, 'oe').replace(/ø/g, 'o');
    if (s.normalize) s = s.normalize('NFD');
    return s.replace(MK, '').replace(/ae/g, 'a').replace(/oe/g, 'o').replace(/ue/g, 'u');
  }
  function words(s) { return fold(s).split(/[^0-9a-z]+/).filter(function (x) { return x; }); }

  // the footer's data line
  var sd = D[l], sp = (D.t[l] || '').split('{d}');
  if (sd && sp.length === 2) [].forEach.call(d.querySelectorAll('[data-stand]'), function (e) {
    var t = d.createElement('time'); t.setAttribute('datetime', D.iso); t.textContent = sd;
    e.textContent = sp[0]; e.appendChild(t); e.appendChild(d.createTextNode(sp[1] + (e.nextElementSibling ? ' · ' : '')));
    e.removeAttribute('data-stand');
  });

  // the reader's day, in Swiss time: deadlines are published in Swiss time
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
  // the published local time, as formato.clock() writes it
  function clock(t) {
    var o = parts(t), hh = +o.hour, mm = o.minute;
    if (!hh && mm === '00') return '';
    return l === 'de' ? hh + '.' + mm + ' Uhr' : l === 'fr' ? hh + ' h ' + mm : p2(hh) + ':' + mm;
  }
  // {c: '' | 'soon' | 'today' | 'over', x: the label, n: days to go}
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
  function expire(e) {
    e.classList.add('off');
    var x = d.createElement('em'); x.className = 'rel'; x.textContent = L.due_over;
    var old = e.querySelector('.rel'); if (old) old.remove();
    e.appendChild(x);
    var st = d.querySelector('.title .state'), h1 = d.querySelector('.title h1'), b = e.querySelector('b');
    if (st && !st.classList.contains('off')) { st.className = 'state off'; st.lastChild.textContent = L.tender_expired; }
    if (h1 && b && !h1.parentNode.querySelector('.sum')) {
      var p = d.createElement('p'); p.className = 'sum'; p.textContent = fmt(L.expired_lead, { when: b.textContent });
      h1.parentNode.insertBefore(p, h1.nextSibling);
    }
    [].forEach.call(d.querySelectorAll('.acts a[href$="frist.ics"]'), function (a) { a.hidden = true; });
  }
  // one element with a deadline: its label and class once; a list row whose deadline has passed hidden, a
  // record's deadline tile expired (also when it passes while the page is open)
  function one(e, hid) {
    var r = rel(e.getAttribute('data-deadline'));
    if (!r) return;
    if (r.c === 'over') {
      if (e.tagName === 'TR' || e.tagName === 'LI') {
        if (!e.hasAttribute('data-gone')) { e.hidden = true; e.setAttribute('data-gone', ''); hid.push(e); }
      } else if (!e.classList.contains('off')) expire(e);
      return;
    }
    if (e.getAttribute('data-r')) return;
    e.setAttribute('data-r', '1');
    var w = e.classList.contains('when') ? e : (e.querySelector('.when') || e);
    if (r.c) { w.classList.add(r.c); e.classList.add(r.c); }
    if (r.x) { var s = d.createElement(e.tagName === 'DIV' ? 'em' : 'span'); s.className = 'rel'; s.textContent = r.x; w.appendChild(s); }
    if (r.c === 'today' && e.tagName === 'DIV') {
      var st = d.querySelector('.title .state');
      if (st && !st.classList.contains('off')) { st.className = 'state today'; st.lastChild.textContent = r.x; }
    }
  }
  // every data-deadline in root; under each list that lost rows, a note, and its section's own count lowered.
  // Returns the rows hidden.
  function deco(root) {
    var hid = [];
    [].forEach.call((root || d).querySelectorAll('[data-deadline]'), function (e) { one(e, hid); });
    var lists = [];
    hid.forEach(function (e) { var c = e.closest('table') || e.parentNode; if (lists.indexOf(c) < 0) lists.push(c); });
    lists.forEach(function (c) {
      var n = c.querySelectorAll('[data-gone]').length;
      var a = c.tagName === 'TABLE' ? (c.closest('.scroll') || c) : c, nx = a.nextElementSibling, note;
      if (nx && nx.classList.contains('xh')) note = nx;
      else { note = d.createElement('p'); note.className = 'xh'; a.parentNode.insertBefore(note, a.nextSibling); }
      note.textContent = n === 1 ? L.hidden_1 : fmt(L.hidden_n, { n: count(n) });
      var sec = c.closest('.sec'), k = sec && sec.querySelector('.runhead>span');
      if (k && /^[\d’ ,]+$/.test(k.textContent)) {
        if (!k.hasAttribute('data-n0')) k.setAttribute('data-n0', k.textContent.replace(/\D/g, ''));
        k.textContent = count(Math.max(0, +k.getAttribute('data-n0') - sec.querySelectorAll('[data-gone]').length));
      }
      // a list that keeps a reserve (the home's next deadlines, data-show="8"): its next rows step in
      var want = +c.getAttribute('data-show') || 0;
      if (want) [].forEach.call(c.querySelectorAll('[data-more]:not([data-gone])'), function (x) {
        if (c.querySelectorAll('[data-deadline]:not([hidden])').length < want) x.hidden = false;
      });
    });
    return hid;
  }
  deco(d);

  // the home's 'neu': 'heute' or 'seit gestern' only while true; otherwise the date the page states
  var nb = d.querySelector('.dnew[data-day]');
  if (nb) {
    var m = +nb.getAttribute('data-n'), dd = today - dnum(nb.getAttribute('data-day'));
    if (dd === 0) nb.textContent = m === 1 ? L.new_today_1 : fmt(L.new_today, { m: count(m) });
    else if (dd === 1) nb.textContent = m === 1 ? L.new_yday_1 : fmt(L.new_yday, { m: count(m) });
  }

  // the page type's scripts, once each; JSON once each, by the day of the data
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

  // the open tenders now, by canton and Branche: null while no deadline has passed since the build (the page's
  // counts are still true), else counted from /daten/offen-dl.json [deadline in minutes, cantons, Branche]
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
        // the tab's title says the page's count too ('… : 344 offen'): the first one on the page, as a whole
        // number (a canton's '5' is not the 5 in '1’405')
        var m = !tt && new RegExp('(^|[^\\d’\'.,\\u00a0\\u202f]|\\D[\\u00a0\\u202f])' + old.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') +
          '(?![\\d’\']|[\\u00a0\\u202f]\\d)').exec(d.title);
        if (m) { tt = 1; d.title = d.title.slice(0, m.index + m[1].length) + s + d.title.slice(m.index + m[0].length); }
      });
      if (op.length) (c ? Promise.resolve(c) : json('/daten/offen-n.json')).then(function (n) {
        [].forEach.call(op, function (e) {
          var s = e.getAttribute('data-open').split(':'), v = (n[s[0]] || {})[s[1]], x = e.querySelector('.ocn');
          if (!x) { x = d.createElement('span'); x.className = 'ocn'; e.appendChild(x); }
          x.textContent = v ? L.colon + ' ' + count(v) : '';
        });
      }, function () { });
    });
    return pr;
  }

  // the next deadline on the page that is still ahead: when it passes while the page is open, its row goes, its
  // calendar link goes, and the counts follow
  function later() {
    var t = Date.now(), nx = 0;
    [].forEach.call(d.querySelectorAll('[data-deadline]:not([data-gone]):not(.off)'), function (e) {
      var w = when(e.getAttribute('data-deadline')); if (w > t && (!nx || w < nx)) nx = w;
    });
    if (nx && nx - t < 864e5) setTimeout(function () {
      now = Date.now(); A.now = now; today = dnum(zday(now)); A.today = today;
      deco(d); A.oc = counts(); later();
    }, nx - t + 1000);
  }

  // the stacked tables keep their table semantics (fix round 1): VoiceOver on iOS drops them with display:grid
  function roles(t) {
    if (!t) return;
    t.setAttribute('role', 'table');
    [].forEach.call(t.querySelectorAll('thead,tbody'), function (g) { g.setAttribute('role', 'rowgroup'); });
    [].forEach.call(t.querySelectorAll('tr'), function (r) { r.setAttribute('role', 'row'); });
    [].forEach.call(t.querySelectorAll('th'), function (c) { c.setAttribute('role', c.closest('thead') ? 'columnheader' : 'rowheader'); });
    [].forEach.call(t.querySelectorAll('td'), function (c) { c.setAttribute('role', 'cell'); });
  }
  [].forEach.call(d.querySelectorAll('table.ls,table.top'), roles);

  // on a phone a long table shows its first 25 rows and 'Alle N anzeigen' (fix round 1); more: what the button
  // does instead of showing the rows already there (liste.js: the whole list)
  var PH = window.matchMedia ? matchMedia('(max-width:37.5rem)') : { matches: false };
  function cut(t, total, more) {
    var tb = t && t.tBodies[0]; if (!tb) return;
    // the table keeps its button (t._cb): liste.js puts its own 'Alle N' after the table too
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
    btn.textContent = fmt(L.all_n, { n: count(Math.max(total || 0, rows.length)) });
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

  // Escape closes the open menu (the header's <details>), and any other open <details> around the focus
  d.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Escape' || ev.defaultPrevented) return;
    var m = d.querySelector('.masthead details[open]') || (ev.target.closest && ev.target.closest('details[open]'));
    if (!m) return;
    m.open = false;
    var s = m.querySelector('summary'); if (s) s.focus();
  });

  // a monthly chart: the month under the pointer (a tap too) or the keyboard (the chart takes the focus, the arrow
  // keys move) in its unit line; the table itself stays the screen readers' (fix round 1: no native title)
  [].forEach.call(d.querySelectorAll('figure.mc'), function (f) {
    var t = f.querySelector('.cc table'), rd = f.querySelector('.rd');
    if (!t || !rd) return;
    var rows = [].slice.call(t.tBodies[0] ? t.tBodies[0].rows : []), cur = -1;
    function show(i) {
      if (cur >= 0 && rows[cur]) rows[cur].classList.remove('on');
      cur = i;
      if (i < 0 || !rows[i]) { rd.textContent = ''; cur = -1; return; }
      var r = rows[i], v = r.querySelector('em');
      r.classList.add('on');
      rd.textContent = '· ' + r.cells[0].textContent + L.colon + ' ' + (v ? v.textContent : '');
    }
    t.tabIndex = 0;
    t.addEventListener('pointerover', function (ev) { var r = ev.target.closest('tr'); if (r) show(rows.indexOf(r)); });
    t.addEventListener('pointerleave', function () { if (d.activeElement !== t) show(-1); });
    t.addEventListener('focus', function () { if (cur < 0) show(rows.length - 1); });
    t.addEventListener('blur', function () { show(-1); });
    t.addEventListener('keydown', function (ev) {
      var k = ev.key, i = cur < 0 ? rows.length - 1 : cur;
      if (k === 'ArrowLeft' || k === 'ArrowRight') i += k === 'ArrowRight' ? 1 : -1;
      else if (k === 'Home') i = 0;
      else if (k === 'End') i = rows.length - 1;
      else return;
      ev.preventDefault(); show(Math.max(0, Math.min(rows.length - 1, i)));
    });
  });

  // the search fields: the search script at the first focus or keystroke; the placeholder's longest form that fits the
  // field as the reader sees it (fix round 2: 'Unternehmen, Auftraggeber, Ausschre' was cut at 1280 and 390 px)
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

  // 'Nach oben' on a page longer than three screens
  var tp = null, tq = 0;
  function totop() {
    if (tp || h.scrollHeight < 3 * innerHeight) return;
    tp = d.createElement('a'); tp.href = '#top'; tp.className = 'totop'; tp.hidden = true;
    tp.innerHTML = '<span aria-hidden="true">↑ </span>' + esc(L.top);
    d.body.appendChild(tp);
    addEventListener('scroll', function () {
      if (!tq) tq = setTimeout(function () { tq = 0; tp.hidden = scrollY < 1.5 * innerHeight; }, 120);
    }, { passive: true });
    tp.addEventListener('click', function (ev) {
      ev.preventDefault(); scrollTo(0, 0);
      var n = d.querySelector('.masthead a.name'); if (n) n.focus();
    });
  }
  totop();

  // a query's canton (fix round 1): 'Reinigung Zürich', 'nettoyage Genève', 'pulizia Ticino' -> the words without
  // the canton's name (in any of the four languages, or its code in capitals) and the canton. names: {ZH: [names]}
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
          if (ok && (!best || nt.length > best.n)) best = { k: k, i: i, n: nt.length };
        }
      });
    });
    if (!best) return { q: String(q || '').trim(), k: '' };
    var rest = ow.filter(function (w, i) {
      return (i < best.i || i >= best.i + best.n) && !/^(kanton|canton|cantone|kt|ct)\.?$/i.test(w);
    });
    return { q: rest.join(' '), k: best.k };
  }
  // a tender's relevance to a query's words (fix round 1): a word in its CPV labels — its topic — 5; in its title a
  // whole word 4, the start of a word 3, the end of a compound ('Gebäudereinigung') 2, inside a word
  // ('Vereinigung') 1; in its authority 2 at most. A word found nowhere: 0, no match. f: {c, t, b} folded words
  function wscore(ws, q, top) {
    var b = 0, j, w, x;
    for (j = 0; j < ws.length; j++) {
      w = ws[j];
      if (w === q) return top;
      x = w.indexOf(q);
      if (x === 0) b = Math.max(b, top === 5 ? 5 : 3);
      else if (x > 0) b = Math.max(b, top === 5 ? (x >= 3 ? 5 : 1) : (x >= 3 && x + q.length === w.length ? 2 : 1));
    }
    return b;
  }
  function tscore(f, qt) {
    var s = 0, i, best;
    for (i = 0; i < qt.length; i++) {
      best = wscore(f.c, qt[i], 5);
      if (best < 5) best = Math.max(best, wscore(f.t, qt[i], 4));
      if (best < 2) best = Math.max(best, Math.min(2, wscore(f.b, qt[i], 3)));
      if (!best) return 0;
      s += best;
    }
    return s;
  }
  // the words of an open tender of /daten/offen.json for tscore(): its titles, its CPV labels, its authority
  function twords(r, o) {
    if (!r.fw) r.fw = { t: words(r[1].map(function (v) { return v.slice(3); }).join(' ')), c: words((o.c[r[4]] || []).join(' ')), b: words(o.b[r[5]]) };
    return r.fw;
  }

  window.AR = { l: l, B: B, v: D.v, iso: D.iso, L: L, fmt: fmt, esc: esc, count: count, date: date, fold: fold, words: words,
    deco: deco, rel: rel, when: when, now: now, today: today, dnum: dnum, zday: zday, load: load, json: json, totop: totop,
    roles: roles, cut: cut, ph: PH, qparse: qparse, tscore: tscore, twords: twords, oc: null };
  A = window.AR;
  A.oc = counts();
  later();
})();
