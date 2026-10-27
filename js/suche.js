/* /js/suche.js (step 3b, 15.10.2026): the register's search, loaded by /stand.js at the first focus on a
   search field, and by the search page itself. One engine for the header field (every page), the home's
   company finder and the full results on /xx/suche/?q=.
   Data, all static (genera.py):
   - /daten/suche/<c>.json: companies and authorities, sharded by the first letter of their words
     (an entry sits in the shard of every letter its significant words start with): u companies with a
     page [name, slug|0, awards], f companies without one [name, award page], b authorities with a page
     [name, slug|0, awards], g without one [name, newest award page, awards]; slug 0 = slug(name);
   - /daten/suche/themen.json: cantons, Branchen, Bereiche (their CPV labels in the four languages) and
     the key pages;
   - /daten/offen.json: the open tenders, every translation of their titles, their CPV labels in the four
     languages (the same file the tender lists filter).
   Matching folds case, accents, ß/ss and ä/ae; a company or an authority is found by the beginning of
   any of its words, a tender or a topic by any part of its text in any language ('reinigung',
   'nettoyage', 'pulizia' and 'cleaning' find the cleaning tenders and CPV 909…). Results come in groups:
   open tenders, companies, authorities, industries and sectors, cantons, pages. ARIA: the field is a
   combobox, its results a listbox of grouped options (links); the arrow keys choose, Enter opens.
   Fix round 1 (20.10.2026): a canton named in the query becomes the tenders' canton ('Reinigung Zürich': the cleaning
   tenders in Zurich, and the hub's list filtered so, scrolled to); tenders are ranked (the topic and the start of a
   title's words before a word inside another: 'Vereinigung' after the cleaning tenders); an exact canton, Branche or
   company name leads; Escape first lets go of the chosen option; no result offers a word less and the alert;
   t=b searches the authorities only (their index's finder).
   Fix round 3 (21.10.2026): no open tender for a query still says so, 'Offene Ausschreibungen (0)', with the link to
   the tender list (its own zero state names the neighbouring cantons and the alert); a word of two letters only as a
   whole word or a word's start; the topics' synonyms (IT -> Informatikdienstleistungen); the results page says its
   count in one live region that stays.
   Fix round 4 (21.10.2026): the stop words (A.sw, one list with the tender lists') off the query while another word
   remains, and out of the shard's choice; 'IT' names the software and the computers too (CPV 48, 302).
   Fix round 5 (21.10.2026): the tenders in the tender lists' order (A.tier): the whole matches first, the matches of a
   word part after them under a divider, and in the field's list only when nothing matches whole ('Gebäudereinigung':
   the laboratory buildings came first); 'Treffer als Wortteil' when every match is one.
   Fix round 6 (21.10.2026): a group whose best match is a word part after the groups with whole matches ('Marchese': the
   firm before three 'Marché…'); a town's word in any language the same ('City of Zurich' = 'Stadt Zürich', its shard the
   town's name); no result offers the query with a word one letter away ('Reinigng': 'Meinten Sie «Reinigung»?'). */
(function () {
  var A = window.AR; if (!A || A.suche) return; A.suche = 1;
  var d = document, LL = __L__, L = LL[A.l] || LL.de, S = A.L, l = A.l, B = A.B, fmt = A.fmt, esc = A.esc, fold = A.fold, toks = A.words, slug = A.slug;
  var LI = A.li, cw = A.cw;
  // the word that picks the shard: the first of two letters or more once the stop words are off (A.sw: articles,
  // prepositions, legal forms; fix round 4: one list with the tender lists', in /stand.js), a town's word only alone
  // (fix round 6: 'Ville de Genève' and 'City of Zurich' are in the shards of 'Genève' and 'Zurich', not 'Stadt')
  function kw(qt) {
    var f = A.sw(qt).filter(function (x) { return x.length > 1; });
    return f.filter(function (x) { return cw(x) !== 'stadt'; })[0] || f[0] || A.sw(qt)[0] || '';
  }
  function words(e, s) { if (!e.w) { e.f = fold(s); e.w = e.f.split(/[^0-9a-z]+/).map(cw); } return e.w; }
  function n_aw(n) { return n === 1 ? S.aw_1 : fmt(S.aw_n, { n: A.count(n) }); }
  function n_open(n) { return n === 1 ? L.open_1 : fmt(L.open_n, { n: A.count(n) }); }
  // a word-prefix (key) and part-of-text (the others) test; score: whole word 4, word start 3, inside 1; the stop words
  // only in the bonus of a name that starts with the query (fix round 4: 'Reinigung an Schulen')
  function score(e, text, qt, key) {
    var w = words(e, text), s = 0, i, j, t, best, f = A.sw(qt).map(cw);
    for (i = 0; i < f.length; i++) {
      t = f[i]; best = 0;
      for (j = 0; j < w.length && best < 4; j++) {
        if (w[j] === t) best = 4; else if (best < 3 && w[j].indexOf(t) === 0) best = 3;
      }
      // the shard's own word must start a word (that is why the entry is in this shard); the rest may be inside one
      if (!best && t !== key && t.length > 2 && e.f.indexOf(t) >= 0) best = 1;
      if (!best) return 0;
      s += best;
    }
    return s + (e.f.indexOf(qt.join(' ')) === 0 ? 3 : 0);
  }
  // every result as {g: group, s: score, n: weight, h: href, x: text, xl: its language, u: sub-line}
  // the canton a query names (A.qparse) and the rest of its words; the names from the tenders' file (fix round 6: not
  // from the topics' when that file failed: no tender to filter then, and the hub's list reads the canton itself)
  function parse(q, op) { return op && op.k ? A.qparse(q, op.k) : { q: q, k: '' }; }
  function search(q, only, shard, th, op) {
    var qt = toks(q), out = [], key = kw(qt), qp = parse(q, op), qr = A.sw(toks(qp.q)), fq = fold(q).replace(/[^0-9a-z]+/g, ' ').trim();
    if (!qt.length) return out;
    // ex: the entry's name is the query itself (an exact canton, Branche or company leads, fix round 1)
    function add(g, s, n, h, x, u, xl, ex) { if (s) out.push({ g: g, s: s + (ex ? 50 : 0) + Math.log(n + 1) / Math.LN10, n: n, h: h, x: x, u: u, xl: xl || '', ex: !!ex }); }
    function same(name) { return fold(name).replace(/[^0-9a-z]+/g, ' ').trim() === fq; }
    var base = B + '/' + l + '/';
    if (shard) {
      if (only !== 'b') {
        (shard.u || []).forEach(function (e) { add('u', score(e, e[0], qt, key), e[2], base + 'unternehmen/' + (e[1] || slug(e[0])) + '/', e[0], n_aw(e[2]), '', same(e[0])); });
        (shard.f || []).forEach(function (e) { add('u', score(e, e[0], qt, key), 1, base + 'auftrag/' + e[1], e[0], n_aw(1) + ' · ' + L.to_award, '', same(e[0])); });
      }
      if (only !== 'u') {
        (shard.b || []).forEach(function (e) { add('b', score(e, e[0], qt, key), e[2], base + 'auftraggeber/' + (e[1] || slug(e[0])) + '/', e[0], n_aw(e[2]), '', same(e[0])); });
        (shard.g || []).forEach(function (e) { add('b', score(e, e[0], qt, key), e[2], base + 'auftrag/' + e[1], e[0], n_aw(e[2]) + ' · ' + L.to_award, '', same(e[0])); });
      }
    }
    if (only) return out;
    if (op && op.t) {
      // the tenders: in the canton the query names, ranked by A.tscore (the topic, then the title's words)
      op.t.forEach(function (r) {
        if (A.when(r[6]) <= A.now) return;
        if (qp.k && r[3].replace(/\*/g, '').split(' ').indexOf(qp.k) < 0) return;
        var s = qr.length ? A.tscore(A.twords(r, op), qr) : (qp.k ? 1 : 0), t = A.title(r), x;
        // the nearest deadline first among equals (n: the minus of its time, scaled)
        add('t', s, 0, base + 'auftrag/' + r[0] + '/', t.t,
          fmt(L.until, { d: A.date(r[6]) }) + ' · ' + op.b[r[5]] + ' · ' + r[3].replace(/\*/g, ''), t.l);
        // w: a word part's match (A.tier), after the whole ones
        if (s) { x = out[out.length - 1]; x.d = A.when(r[6]); x.w = A.tier(A.twords(r, op), qr); }
      });
    }
    if (th) {
      var tq = qr.length ? qr : qt;
      var syn = tq.map(function (w) { return A.syn[w] || ''; }).join(' ').split(' ');
      (th.s || []).concat(th.d || []).forEach(function (e) {
        var div = e[0].length === 2, sc = score(e, e[1].join(' ') + ' ' + e[0], tq, null);
        // the Branche a synonym names leads its group ('IT' -> Informatikdienstleistungen), when the synonym is that broad
        // (fix round 6: 'Übersetzung' -> 7953 put the Branche of all business services before the translations)
        if (syn.some(function (v) { return v && (e[0].indexOf(v) === 0 || (div && v.length < 4 && v.indexOf(e[0]) === 0)); })) sc = Math.max(sc, 4) + (div ? 4 : 0);
        // a Branche before its own Bereiche when both match as well
        add('s', sc && sc + (div ? 1 : 0), e[2], base + (div ? 'branche/' : 'bereich/') + e[0] + '/', e[1][LI],
          (div ? L.k_div : L.k_sec) + ' · CPV ' + e[0] + ' · ' + n_aw(e[2]) + (e[3] ? ' · ' + n_open(e[3]) : ''), '',
          div && e[1].some(same));
      });
      (th.k || []).forEach(function (e) {
        var sc = qp.k === e[0] ? 12 : score(e, e[1].join(' ') + ' ' + e[0], qt, null);
        add('k', sc, e[2], base + 'kanton/' + e[0] + '/', L.k_canton + ' ' + e[1][LI],
          n_aw(e[2]) + (e[3] ? ' · ' + n_open(e[3]) : ''), '', e[1].some(same) || e[0] === q.trim());
      });
      (th.p || []).forEach(function (e) {
        add('p', score(e, e[1].join(' ') + ' ' + e[3], qt, null), 0, base + e[2], e[1][LI], '');
      });
    }
    return out;
  }
  var ORDER = ['t', 'u', 'b', 's', 'k', 'p'];
  function rank(x) { return x.ex ? 0 : x.w ? 2 : 1; }
  function groups(res) {
    var g = {};
    res.forEach(function (r) { (g[r.g] = g[r.g] || []).push(r); });
    ORDER.forEach(function (k) {
      if (g[k]) g[k].sort(function (a, b) { return (a.w | 0) - (b.w | 0) || b.s - a.s || (a.d && b.d ? a.d - b.d : 0) || b.n - a.n || (a.x < b.x ? -1 : a.x > b.x ? 1 : 0); });
    });
    // the groups holding an exact name first (fix round 1: 'Zürich' showed tenders before the canton), the ones whose best
    // match is a word part last (fix round 6: 'Marchese' showed three 'Marché…' before the firm)
    g.order = ORDER.filter(function (k) { return g[k]; }).sort(function (a, b) { return rank(g[a][0]) - rank(g[b][0]); });
    return g;
  }
  function data(q) {
    var key = kw(toks(q)), c = /[0-9]/.test(key.charAt(0)) ? '0' : key.charAt(0);
    function soft(p) { return p.catch(function () { return null; }); }
    return Promise.all([c ? soft(A.json('/daten/suche/' + c + '.json')) : null, soft(A.json('/daten/suche/themen.json')),
      soft(A.json('/daten/offen.json'))]);
  }
  // the hub's list for a query: its canton as the canton filter, scrolled to the list (fix round 1)
  function hubq(q, r) {
    var p = parse(q, r && r[2]), a = [];
    if (p.q) a.push('q=' + encodeURIComponent(p.q)); if (p.k) a.push('k=' + p.k);
    return B + '/' + l + '/ausschreibungen/' + (a.length ? '?' + a.join('&') : '') + '#fristen';
  }
  // no result: the query with a word one letter away (fix round 6), a word less (when the query has several), the alert,
  // and on the page the directories (fix round 1)
  function sugg(q, only, op) {
    var ws = q.trim().split(/\s+/), out = [], y = op && A.dym(q, op);
    if (y) out.push({ h: resq(y, only), x: fmt(S.z_dym, { q: y }) });
    if (ws.length > 1) ws.forEach(function (w, i) {
      var rest = ws.filter(function (x, j) { return j !== i; }).join(' ');
      out.push({ h: resq(rest, only), x: fmt(S.z_drop, { t: w, n: '' }).replace(/[:\s]+$/, '') });
    });
    out.push({ h: B + '/' + l + '/ausschreibungen/abo/', x: S.z_abo });
    return out;
  }
  function resq(q, only) { return B + '/' + l + '/suche/?q=' + encodeURIComponent(q) + (only ? '&t=' + only : ''); }

  // the combobox under a field
  var uid = 0;
  function setup(f) {
    if (f.getAttribute('data-s')) return; f.setAttribute('data-s', '1');
    var i = f.querySelector('input[name=q]'), oi = f.querySelector('input[name=t]'), only = oi ? oi.value : '';
    var page = f.classList.contains('search-page');
    var pop = d.createElement('div'), st = d.createElement('span'), id = 'sp' + (++uid), act = -1, opts = [], tm = 0, seq = 0;
    pop.className = 'search-pop'; pop.id = id; pop.setAttribute('role', 'listbox'); pop.hidden = true;
    pop.setAttribute('aria-label', i.getAttribute('aria-label') || L.g_u);
    st.className = 'sr'; st.setAttribute('role', 'status');
    f.appendChild(pop); f.appendChild(st);
    i.setAttribute('role', 'combobox'); i.setAttribute('aria-autocomplete', 'list');
    i.setAttribute('aria-expanded', 'false'); i.setAttribute('aria-controls', id);
    function close() { pop.hidden = true; i.setAttribute('aria-expanded', 'false'); i.removeAttribute('aria-activedescendant'); act = -1; }
    function pick(k) {
      if (!opts.length) return;
      if (act >= 0) opts[act].setAttribute('aria-selected', 'false');
      act = (k + opts.length) % opts.length;
      opts[act].setAttribute('aria-selected', 'true'); i.setAttribute('aria-activedescendant', opts[act].id);
      opts[act].scrollIntoView({ block: 'nearest' });
    }
    function opt(h, x, u, cls, xl) {
      var o = '<a role="option" aria-selected="false" class="search-opt' + (cls ? ' ' + cls : '') + '" href="' + esc(h) + '" id="' + id + '-' + (opts.length + 1) + '">' +
        '<span' + (xl && xl !== l ? ' lang="' + xl + '"' : '') + '>' + esc(x) + '</span>' + (u ? '<span class="sub">' + esc(u) + '</span>' : '') + '</a>';
      opts.length++;
      return o;
    }
    function run() {
      var q = i.value.trim(), my = ++seq;
      if (q.length < 2) { close(); st.textContent = ''; return; }
      data(q).then(function (r) {
        if (my !== seq) return;
        var g = groups(search(q, only, r[0], r[1], r[2])), html = '', n = 0, cap = { t: 3, u: only ? 8 : 4, b: only ? 8 : 3, s: 3, k: 2, p: 2 };
        opts = []; act = -1;
        g.order.forEach(function (k) {
          // tw: every tender found as a word part, said under the group's name; else only the whole matches here
          var rs = g[k], gi = ORDER.indexOf(k), tw = rs[0].w;
          var gid = id + '-g' + gi;
          html += '<div role="group" aria-labelledby="' + gid + '"><span class="search-grp" id="' + gid + '" role="presentation">' + esc(L['g_' + k]) + ' (' + A.count(rs.length) + ')' +
            (tw ? '<span class="tw">' + esc(S.tier_a) + '</span>' : '') + '</span>';
          rs.filter(function (x) { return tw || !x.w; }).slice(0, cap[k]).forEach(function (x) { html += opt(x.h, x.x, x.u, '', x.xl); n++; });
          if (k === 't') html += opt(hubq(q, r), fmt(L.all_t, { q: q }), '', 'all');
          html += '</div>';
        });
        var t0 = !only && r[2] && !g.t ? '<div role="group" aria-labelledby="' + id + '-g0"><span class="search-grp" id="' + id +
          '-g0" role="presentation">' + esc(L.g_t) + ' (0)</span>' + opt(hubq(q, r), fmt(L.all_t, { q: q }), '', 'all') + '</div>' : '';
        if (n) html += t0 + opt(resq(q, only), fmt(L.all_r, { q: q }), '', 'all');
        else {
          html = '<span class="search-msg">' + esc(fmt(L.none, { q: q })) + ' ' + esc(S.z_h) + '</span>';
          sugg(q, only, r[2]).forEach(function (x) { html += opt(x.h, x.x, '', 'all'); });
          html += t0;
        }
        pop.innerHTML = html;
        opts = [].slice.call(pop.querySelectorAll('[role=option]'));
        pop.hidden = false; i.setAttribute('aria-expanded', 'true');
        st.textContent = n ? fmt(L.n_sug, { n: opts.length }) : fmt(L.none, { q: q });
      });
    }
    i.addEventListener('input', function () { clearTimeout(tm); tm = setTimeout(page ? function () { full(i.value); } : run, 160); });
    if (page) return;
    i.addEventListener('keydown', function (ev) {
      var k = ev.key;
      if (k === 'ArrowDown' || k === 'ArrowUp') {
        ev.preventDefault();
        if (pop.hidden) { run(); return; }
        pick(act < 0 ? (k === 'ArrowDown' ? 0 : -1) : act + (k === 'ArrowDown' ? 1 : -1));
      } else if (k === 'Enter' && act >= 0 && !pop.hidden) {
        ev.preventDefault(); location.href = opts[act].href;
      } else if (k === 'Escape') {
        // first the chosen option is let go, then the list closes, then the field empties (fix round 1)
        if (!pop.hidden && act >= 0) { ev.preventDefault(); opts[act].setAttribute('aria-selected', 'false'); act = -1; i.removeAttribute('aria-activedescendant'); }
        else if (!pop.hidden) { ev.preventDefault(); close(); } else if (i.value) { ev.preventDefault(); i.value = ''; }
      } else if (k === 'Tab') close();
    });
    pop.addEventListener('mousedown', function (ev) { ev.preventDefault(); });
    f.addEventListener('focusout', function (ev) { if (!f.contains(ev.relatedTarget)) setTimeout(close, 120); });
    i.addEventListener('focus', function () { if (i.value.trim().length >= 2 && pop.hidden) run(); });
    if (d.activeElement === i && i.value.trim().length >= 2) run();
  }

  // the results page, /xx/suche/?q=…&t=u
  var res = d.getElementById('treffer'), fseq = 0, live = null;
  if (res) { live = d.createElement('p'); live.className = 'sr'; live.setAttribute('role', 'status'); res.parentNode.insertBefore(live, res); }
  function full(q) {
    if (!res) return;
    var my = ++fseq, sp = new URLSearchParams(location.search), only = /^[ub]$/.test(sp.get('t') || '') ? sp.get('t') : '';
    q = (q || '').trim();
    try { history.replaceState(null, '', q ? resq(q, only) : location.pathname); } catch (e) { }
    if (q.length < 2) { res.innerHTML = ''; live.textContent = ''; return; }
    res.innerHTML = '<p class="cnt">' + esc(L.loading) + '</p>';
    data(q).then(function (r) {
      if (my !== fseq) return;
      if (!r[0] && !r[1] && !r[2]) { res.innerHTML = '<p class="cnt">' + esc(S.failed) + '</p>'; return; }
      var all = search(q, only, r[0], r[1], r[2]), g = groups(all), html = '', nt = all.length === 1 ? L.n_res_1 : fmt(L.n_res, { n: A.count(all.length) });
      html += '<p class="cnt">' + esc(nt) + '</p>';
      live.textContent = nt;
      if (!all.length) html += '<p class="empty">' + esc(fmt(L.none, { q: q })) + ' ' + esc(L.none_hint) + '</p>' +
        '<p class="zs"><strong>' + esc(S.z_h) + '</strong> ' + sugg(q, only, r[2]).map(function (x) { return '<a href="' + esc(x.h) + '">' + esc(x.x) + '</a>'; }).join(' · ') + '</p>';
      html += '<div class="search-res">';
      g.order.forEach(function (k) {
        var rs = g[k];
        html += '<h2>' + esc(L['g_' + k]) + ' <span class="sub">(' + A.count(rs.length) + ')</span></h2><ul class="plain">';
        rs.forEach(function (x, j) {
          // the matches of a word part after a divider, as in the tender lists
          if (x.w && !(rs[j - 1] || {}).w) html += '<li class="tier"' + (j >= 50 ? ' hidden' : '') + '>' + esc(j ? S.tier_w : S.tier_a) + '</li>';
          html += '<li' + (j >= 50 ? ' hidden' : '') + '><a href="' + esc(x.h) + '"' + (x.xl && x.xl !== l ? ' lang="' + x.xl + '"' : '') + '>' + esc(x.x) + '</a>' +
            (x.u ? '<span class="sub sb2">' + esc(x.u) + '</span>' : '') + '</li>';
        });
        html += '</ul>';
        if (rs.length > 50) html += '<button type="button" class="all" data-more>' + esc(fmt(L.more, { n: A.count(rs.length - 50) })) + '</button>';
        if (k === 't') html += '<p class="dl"><a href="' + esc(hubq(q, r)) + '">' + esc(fmt(L.all_t, { q: q })) + '</a></p>';
      });
      // no open tender for the query: said, and the list's own zero state one click away (fix round 3)
      if (!only && r[2] && !g.t) html += '<h2>' + esc(L.g_t) + ' <span class="sub">(0)</span></h2><p class="dl"><a href="' +
        esc(hubq(q, r)) + '">' + esc(fmt(L.all_t, { q: q })) + '</a></p>';
      res.innerHTML = html + '</div>';
      [].forEach.call(res.querySelectorAll('[data-more]'), function (b) {
        b.addEventListener('click', function () {
          var ul = b.previousElementSibling, a = ul.querySelector('li[hidden] a');
          [].forEach.call(ul.querySelectorAll('li[hidden]'), function (x) { x.hidden = false; });
          b.remove(); if (a) a.focus();
        });
      });
    });
  }

  [].forEach.call(d.querySelectorAll('form[role=search]'), setup);
  if (res) {
    var q0 = new URLSearchParams(location.search).get('q') || '', pf = d.querySelector('form.search-page input[name=q]');
    if (pf && q0) pf.value = q0;
    full(q0);
  }
})();
