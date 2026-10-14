/* /js/abo.js (step 3b, 15.10.2026; it was the inline ABO_JS): the alert form on /xx/ausschreibungen/abo/.
   The form posts to Brevo (double opt-in). Without JavaScript the browser submits it and Brevo redirects
   to /abo/check/; with it the answer shows in place, in the page's language, and the canton and
   industry pills are folded into the two text attributes the daily sender reads (KANTON, BRANCHE:
   codes joined by commas, or ALLE).
   Step 3b: the button is never disabled while sending (aria-disabled: the focus stays on it), and the
   focus moves to the answer; the e-mail field says aria-invalid and points at its error
   (aria-describedby); each industry group's summary says how many it has chosen, in visually hidden
   text; and a preview counts what the selection would bring: the tenders open now (/daten/offen.json)
   and the new ones a week, from the last 8 weeks of first publications (/daten/abo-rate.json).
   The prefill reads ?k=ZH&b=45 (the links of the pages' alert boxes): only the 26 canton codes and
   two-digit CPV divisions, at most five of each; a value without a pill gets one, labelled from the
   build-time name map (never from the address), in the group of its division, which opens. */
(function () {
  var d = document, f = d.getElementById('abo'); if (!f) return;
  var LL = __L__, A = window.AR, l = d.documentElement.lang, L = LL[l] || LL.de;
  var m = f.querySelector('.msg'), b = f.querySelector('button[type=submit]'), em = f.elements.EMAIL, er = d.getElementById('abo-email-err'), busy = false;
  function fmt(s, o) { return String(s).replace(/\{(\w+)\}/g, function (x, k) { return k in o ? o[k] : x; }); }
  function vals(n) { return [].map.call(f.querySelectorAll('input[name=' + n + ']:checked'), function (x) { return x.value; }); }
  function j(n) { var v = vals(n); return v.length ? v.join(',') : 'ALLE'; }
  function fill() { f.elements.KANTON.value = j('k'); f.elements.BRANCHE.value = j('b'); }
  // the e-mail field and its error, tied together
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
      // a success keeps the button inert: one confirmation e-mail is enough
      if (r.success) m.textContent = f.dataset.ok;
      else { busy = false; b.removeAttribute('aria-disabled'); m.className = 'msg err'; m.textContent = f.dataset.err; }
      m.focus();
    }).catch(function () { busy = false; b.removeAttribute('aria-disabled'); f.submit(); });
  });
  // how many each industry group has chosen, for a screen reader (the dot says it to the eye)
  function counts() {
    [].forEach.call(f.querySelectorAll('details.grp'), function (g) {
      var s = g.querySelector('summary .sr');
      if (!s) { s = d.createElement('span'); s.className = 'sr'; g.querySelector('summary').appendChild(s); }
      s.textContent = ' ' + fmt(L.sel, { n: g.querySelectorAll('input:checked').length });
    });
  }
  // the preview: open now, and new ones a week
  var pv = d.createElement('p'), O = null, R = null;
  pv.className = 'pv'; pv.setAttribute('role', 'status'); pv.setAttribute('aria-live', 'polite'); pv.hidden = true;
  var fs = f.querySelectorAll('fieldset'), last = fs[fs.length - 1];
  if (last) last.parentNode.insertBefore(pv, last.nextSibling);
  function week(w) {
    var s = w >= 10 ? String(Math.round(w)) : (Math.round(w * 10) / 10).toFixed(1).replace(/\.0$/, '');
    return l === 'en' ? s : s.replace('.', ',');
  }
  function preview() {
    if (!O || !R || !A) return;
    var ks = vals('k'), bs = vals('b'), n = 0, w = 0;
    O.t.forEach(function (r) {
      if (A.when(r[6]) <= A.now) return;
      if (bs.length && bs.indexOf(r[4].slice(0, 2)) < 0) return;
      if (ks.length && !r[3].replace(/\*/g, '').split(' ').some(function (k) { return ks.indexOf(k) >= 0; })) return;
      n++;
    });
    (ks.length ? ks : ['*']).forEach(function (k) {
      (bs.length ? bs : ['*']).forEach(function (v) { w += ((R[k] || {})[v] || 0) / 8; });
    });
    var open = n === 1 ? L.open_1 : fmt(L.open_n, { n: A.count(n) });
    pv.innerHTML = '';
    pv.appendChild(d.createTextNode(w > 0 && w < 1 ? fmt(L.pv_lt, { open: open }) : fmt(L.pv, { open: open, w: week(w) })));
    var sm = d.createElement('small'); sm.textContent = L.pv_note; pv.appendChild(sm);
    pv.hidden = false;
  }
  function changed() { fill(); counts(); preview(); }
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
  pre(); fill(); counts();
  if (A) {
    var go = function () {
      Promise.all([A.json('/daten/offen.json'), A.json('/daten/abo-rate.json')]).then(function (x) { O = x[0]; R = x[1]; preview(); }, function () { });
    };
    if (window.requestIdleCallback) requestIdleCallback(go, { timeout: 2000 }); else setTimeout(go, 800);
  }
})();
