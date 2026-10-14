/* /stand.js, on every page (step 3b, 15.10.2026). genera.py writes its data (D): the date of the newest
   publication, the words below in the four languages, the base path and the scripts' version.
   It does what depends on the reader's clock and nothing else, so the pages themselves never change
   because a day has passed:
   - the footer's data line (data-stand), as before;
   - every deadline (data-deadline): 'läuft heute ab, 14.00 Uhr', 'läuft morgen ab', 'noch 5 Tage',
     the classes .today and .soon; a list row whose deadline has passed since the build is hidden, with
     a note under its list and its section's count lowered; a tender page past its deadline shows the
     'Eingabefrist abgelaufen' state;
   - the home's 'neu' badge reads 'heute' or 'seit gestern' only when that is true; else its date stays;
   - the search fields: their placeholder, and /js/suche.js at the first focus;
   - a 'Nach oben' link on long pages.
   Its helpers are window.AR, for the page type's own script (liste.js, suche.js, abo.js, kb.js). */
(function () {
  var D = __DATA__, d = document, h = d.documentElement, l = D.L[h.lang] ? h.lang : 'de', L = D.L[l], B = D.B;
  function fmt(s, o) { return String(s).replace(/\{(\w+)\}/g, function (m, k) { return k in o ? o[k] : m; }); }
  function p2(n) { n = +n; return (n < 10 ? '0' : '') + n; }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  var GR = { de: '’', it: '’', fr: ' ', en: ',' };
  function count(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, GR[l]); }
  function date(iso) {
    var y = iso.slice(0, 4), m = +iso.slice(5, 7), x = +iso.slice(8, 10);
    return l === 'en' ? x + ' ' + D.mo[m - 1] + ' ' + y : p2(x) + '.' + p2(m) + '.' + y;
  }
  var MK; try { MK = new RegExp('\\p{M}', 'gu'); } catch (e) { MK = /[̀-ͯ]/g; }
  // the search's and the filters' folding, the same as genera.sfold(): case, accents, ß/ss, ä/ae
  function fold(s) {
    s = String(s || '').toLowerCase().replace(/ß/g, 'ss').replace(/æ/g, 'ae').replace(/œ/g, 'oe').replace(/ø/g, 'o');
    if (s.normalize) s = s.normalize('NFD');
    return s.replace(MK, '').replace(/ae/g, 'a').replace(/oe/g, 'o').replace(/ue/g, 'u');
  }

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
    return l === 'de' ? hh + '.' + mm + ' Uhr' : l === 'fr' ? hh + ' h ' + mm : p2(hh) + ':' + mm;
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
    var x = d.createElement('em'); x.className = 'rel'; x.textContent = L.due_over; e.appendChild(x);
    var st = d.querySelector('.title .state'), h1 = d.querySelector('.title h1'), b = e.querySelector('b');
    if (st && !st.classList.contains('off')) { st.className = 'state off'; st.lastChild.textContent = L.tender_expired; }
    if (h1 && b && !h1.parentNode.querySelector('.sum')) {
      var p = d.createElement('p'); p.className = 'sum'; p.textContent = fmt(L.expired_lead, { when: b.textContent });
      h1.parentNode.insertBefore(p, h1.nextSibling);
    }
    [].forEach.call(d.querySelectorAll('.acts a[href$="frist.ics"]'), function (a) { a.hidden = true; });
  }
  // every data-deadline in root: the label and the class; a list row past its deadline hidden, with a
  // note under its list and the section's own count lowered. Returns the rows hidden.
  function deco(root) {
    var hid = [];
    [].forEach.call((root || d).querySelectorAll('[data-deadline]'), function (e) {
      if (e.getAttribute('data-r')) return;
      e.setAttribute('data-r', '1');
      var r = rel(e.getAttribute('data-deadline'));
      if (!r) return;
      if (r.c === 'over') {
        if (e.tagName === 'TR' || e.tagName === 'LI') { e.hidden = true; e.setAttribute('data-gone', ''); hid.push(e); } else expire(e);
        return;
      }
      var w = e.classList.contains('when') ? e : (e.querySelector('.when') || e);
      if (r.c) { w.classList.add(r.c); e.classList.add(r.c); }
      if (r.x) { var s = d.createElement(e.tagName === 'DIV' ? 'em' : 'span'); s.className = 'rel'; s.textContent = r.x; w.appendChild(s); }
      if (r.c === 'today' && e.tagName === 'DIV') {
        var st = d.querySelector('.title .state');
        if (st && !st.classList.contains('off')) { st.className = 'state today'; st.lastChild.textContent = r.x; }
      }
    });
    var lists = [];
    hid.forEach(function (e) { var c = e.closest('table') || e.parentNode; if (lists.indexOf(c) < 0) lists.push(c); });
    lists.forEach(function (c) {
      var n = c.querySelectorAll('[data-gone]').length;
      var a = c.tagName === 'TABLE' ? (c.closest('.scroll') || c) : c, nx = a.nextElementSibling, note;
      if (nx && nx.classList.contains('xh')) note = nx;
      else { note = d.createElement('p'); note.className = 'xh'; a.parentNode.insertBefore(note, a.nextSibling); }
      note.textContent = n === 1 ? L.hidden_1 : fmt(L.hidden_n, { n: count(n) });
      var sec = c.closest('.sec'), k = sec && sec.querySelector('.runhead>span');
      if (k && /^[\d’ ,]+$/.test(k.textContent)) {
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

  // the open tenders' count on the pills of the award pages (a Bereich, a Branche, a canton): one small
  // file changes each night instead of 1'700 pages
  var op = d.querySelectorAll('[data-open]');
  if (op.length) json('/daten/offen-n.json').then(function (c) {
    [].forEach.call(op, function (e) {
      var s = e.getAttribute('data-open').split(':'), n = (c[s[0]] || {})[s[1]];
      if (n) e.appendChild(d.createTextNode(L.colon + ' ' + count(n)));
    });
  }, function () { });

  // the search fields: the search script at the first focus or keystroke
  [].forEach.call(d.querySelectorAll('form[role=search]'), function (f) {
    var i = f.querySelector('input[name=q]');
    if (!i) return;
    i.type = 'search'; i.setAttribute('autocomplete', 'off'); i.setAttribute('spellcheck', 'false');
    if (!i.placeholder) i.placeholder = L.ph;
    function go() { load('suche'); }
    i.addEventListener('focus', go); i.addEventListener('input', go);
  });

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

  window.AR = { l: l, B: B, v: D.v, iso: D.iso, L: L, fmt: fmt, esc: esc, count: count, date: date, fold: fold,
    deco: deco, rel: rel, when: when, now: now, today: today, dnum: dnum, zday: zday, load: load, json: json, totop: totop };
})();
