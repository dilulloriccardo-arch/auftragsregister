/* /js/home.js (step 4, 15.10.2026): the motion of the home in design A2 "Brass", on the four home pages (and
   the root) only, after /stand.js. Own code, no library. Everything here is an enhancement: without it the
   home is complete (the map's SVG and the canton list stand in for the canvas), and under
   prefers-reduced-motion it stays still. It adds:
   - one rAF ticker and damped springs (mass 1, sub-stepped at 1 ms);
   - the hero: a brass glow under the cursor and a soft parallax of its layers (pointer: fine only), and,
     where the CSS pins the hero (sticky), its recede under the next band (scale 1 - 0.1p, a shade 0.55p);
   - below the fold only: the section headings revealed word by word (a plain copy stays for screen
     readers), blocks that rise into place (data-up), the key figures counting up;
   - the halftone map of the open tenders per canton (official 2026 boundaries, reticolo.json): the dots
     lit by rank as the pinned stage scrolls (or on a timer), a reticle and a read-out under the cursor, the
     canton list as the keyboard's path to the same read-out; a click on a canton opens its tenders;
   - the chequered seam where the brass alarm band ends (a decision falls).
   Its words are those of the page's language (__L__, written by genera.py).
   Fix round 2: the reveal starts as soon as a block is a tenth into the screen, the horizon moves with the pillars,
   the seam continues the band's own gradient, the map shows a pointer over a canton and keeps its read-out while a
   canton is hovered or focused. */
(function () {
  "use strict";
  var A = window.AR; if (!A || A.home) return; A.home = 1;
  var LL = __L__, L = LL[A.l] || LL.de, D = document, H = D.documentElement, W = window;
  var RM = W.matchMedia("(prefers-reduced-motion: reduce)").matches, FINE = W.matchMedia("(pointer: fine)").matches;
  H.classList.add("js");
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function fmt(s, o) { return A.fmt(s, o); }

  /* ticker: subscribers with a minimum interval; runs only while someone listens */
  var subs = [], raf = 0;
  function frame(now) {
    raf = 0;
    for (var i = subs.length - 1; i >= 0; i--) {
      var s = subs[i];
      if (now - s.l < s.i) continue;
      var dt = s.p ? Math.min(64, now - s.p) : 16;
      s.p = now; s.l = now;
      if (s.f(dt, now) === false) subs.splice(i, 1);
    }
    if (subs.length) raf = requestAnimationFrame(frame);
  }
  function tick(f, iv) {
    var s = { f: f, i: iv || 0, l: -1e9, p: 0 };
    subs.push(s);
    if (!raf) raf = requestAnimationFrame(frame);
    return function () { var k = subs.indexOf(s); if (k >= 0) subs.splice(k, 1); };
  }
  function Spring(c, x) { this.k = c[0]; this.c = c[1]; this.x = x || 0; this.t = this.x; this.v = 0; }
  Spring.prototype.step = function (dt) {
    for (var n = Math.max(1, Math.round(dt)); n--;) {
      this.v += (-this.k * (this.x - this.t) - this.c * this.v) * 0.001;
      this.x += this.v * 0.001;
    }
    if (Math.abs(this.v) < 0.01 && Math.abs(this.t - this.x) < 0.01) { this.x = this.t; this.v = 0; return false; }
    return true;
  };
  var REVEAL = [90, 26], ROW = [170, 24], SETTLE = [32, 26];
  function io(el, cb, opt) {
    if (!("IntersectionObserver" in W)) { cb(true); return null; }
    var o = new IntersectionObserver(function (es) { es.forEach(function (e) { cb(e.isIntersecting, e); }); }, opt || { threshold: 0 });
    o.observe(el);
    return o;
  }
  function below(el) { return el.getBoundingClientRect().top > (W.innerHeight || 800) * 0.92; }
  function once(el, th, go) {
    var done = false, o = io(el, function (v) { if (v && !done) { done = true; if (o) o.disconnect(); go(); } }, { threshold: th });
  }

  /* headings below the fold, word by word; the plain copy stays for screen readers */
  function split(el) {
    var sr = D.createElement("span"), vis = D.createElement("span"), units = [], last = null;
    sr.className = "sr"; sr.textContent = el.textContent.replace(/\s+/g, " ").trim();
    vis.className = "split"; vis.setAttribute("aria-hidden", "true");
    [].forEach.call(el.childNodes, function (n) {
      if (n.nodeType === 3) n.textContent.split(/(\s+)/).forEach(function (p) {
        if (!p) return;
        if (/^\s+$/.test(p)) { vis.appendChild(D.createTextNode(" ")); last = null; return; }
        var w = D.createElement("span"); w.className = "w"; w.textContent = p; vis.appendChild(w); units.push(w); last = w;
      });
      else if (n.nodeType === 1) {
        var s = D.createElement("span"); s.className = n.className; s.textContent = n.textContent;
        (last || vis).appendChild(s);
      }
    });
    el.textContent = ""; el.appendChild(sr); el.appendChild(vis);
    return units;
  }
  function reveal(el) {
    if (RM || !below(el)) return;
    var units = split(el);
    units.forEach(function (u) { u.style.opacity = "0"; u.style.transform = "translateY(.35em)"; });
    once(el, 0.2, function () {
      var sp = units.map(function () { return new Spring(REVEAL, 0); }), t0 = -1;
      tick(function (dt, now) {
        if (t0 < 0) t0 = now;
        var busy = false;
        for (var i = 0; i < units.length; i++) {
          if (now - t0 >= i * 110) sp[i].t = 1;
          var m = sp[i].step(dt) || sp[i].t !== 1, x = sp[i].x;
          busy = busy || m;
          units[i].style.opacity = Math.min(1, x).toFixed(3);
          units[i].style.transform = x >= 1 && !m ? "" : "translateY(" + ((1 - x) * 0.35).toFixed(3) + "em)";
        }
        return busy;
      });
    });
  }

  /* the key figures count up when they come into view (Swiss formats: 18’445, 32,1) */
  function countUp(el) {
    var raw = el.textContent.trim(), m = raw.match(/^([\d’'  ,.]*\d)(.*)$/);
    if (!m || RM || !below(el)) return;
    var g = m[1], dec = /[,.]\d{1,2}$/.test(g) && !/[’'  ]\d{3}$/.test(g) ? g.match(/[,.](\d+)$/)[1].length : 0;
    var sep = (g.match(/[’'  ,.](?=\d{3}(?!\d))/) || [""])[0], dch = dec ? g.charAt(g.length - dec - 1) : "";
    var target = parseFloat(g.replace(/[^\d,.]/g, "").replace(dch ? new RegExp("[^\\d" + dch + "]", "g") : /[,.]/g, "").replace(",", ".")), tail = m[2];
    if (!isFinite(target)) return;
    function f(v) {
      var s = v.toFixed(dec).split("."), i = sep ? s[0].replace(/\B(?=(\d{3})+(?!\d))/g, sep) : s[0];
      return dec ? i + dch + s[1] : i;
    }
    var sr = D.createElement("span"), vis = D.createElement("span");
    sr.className = "sr"; sr.textContent = raw; vis.setAttribute("aria-hidden", "true"); vis.className = "cnt";
    vis.style.setProperty("--w", raw.length + "ch"); vis.textContent = f(0) + tail;
    el.textContent = ""; el.appendChild(sr); el.appendChild(vis);
    once(el, 0.4, function () {
      var t0 = -1, dur = 1300 + Math.min(700, target / 40);
      tick(function (dt, now) {
        if (t0 < 0) t0 = now;
        var p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 4);
        vis.textContent = f(target * e) + tail;
        if (p >= 1) { vis.textContent = raw; vis.style.removeProperty("--w"); return false; }
      });
    });
  }

  /* blocks rise into place, only those that start below the fold (data-up: stand.js marks its deadlines data-r).
     Fix round 2: from the moment their top is a tenth of the screen above its bottom edge (threshold 0; the margin
     counts the 1.625rem they rise from), not once 12 % of a tall block is in view: a band of 270-450 px stayed black */
  var LIFT = 1.625 * (parseFloat(getComputedStyle(H).fontSize) || 16);
  function rise(el) {
    if (RM || !below(el)) return;
    el.classList.add("up0");
    var m = Math.max(0, Math.round((W.innerHeight || 800) * 0.1 - LIFT));
    var o = io(el, function (v) { if (v) { el.classList.remove("up0"); if (o) o.disconnect(); } }, { threshold: 0, rootMargin: "0px 0px -" + m + "px 0px" });
  }

  /* the hero: glow under the cursor, a soft parallax of its layers; its recede under the next band */
  function hero(h) {
    if (!h || RM || !FINE) return;
    var rest = (h.getAttribute("data-rest") || ".7,.35").split(",").map(Number);
    var gx = new Spring(ROW, rest[0]), gy = new Spring(ROW, rest[1]), px = new Spring(SETTLE, 0), py = new Spring(SETTLE, 0);
    var layers = [].slice.call(h.querySelectorAll("[data-depth]")), par = W.innerWidth >= 900, stop = null;
    function paint() {
      h.style.setProperty("--mx", (gx.x * 100).toFixed(2) + "%"); h.style.setProperty("--my", (gy.x * 100).toFixed(2) + "%");
      if (par) layers.forEach(function (l) {
        var d = +l.getAttribute("data-depth");
        l.style.transform = "translate3d(" + (-px.x * d * 34).toFixed(2) + "px," + (-py.x * d * 22).toFixed(2) + "px,0)";
      });
    }
    function run() {
      if (stop) return;
      stop = tick(function (dt) {
        var a = gx.step(dt), b = gy.step(dt), c = px.step(dt), d = py.step(dt);
        paint();
        if (!(a || b || c || d)) { stop = null; return false; }
      });
    }
    paint(); h.classList.add("glow-on");
    h.addEventListener("pointermove", function (e) {
      var r = h.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      gx.t = x; gy.t = y; if (par) { px.t = x - 0.5; py.t = y - 0.5; }
      run();
    }, { passive: true });
    h.addEventListener("pointerleave", function () { gx.t = rest[0]; gy.t = rest[1]; px.t = 0; py.t = 0; run(); });
  }
  function stack(h, next) {
    if (!h || !next || RM) return;
    var inner = h.querySelector(".recede"), shade = h.querySelector(".shade"), q = 0;
    // pinned only while the hero fits the screen (fix round 1): taller, its doors would never come into view
    function fit() { h.classList.toggle("pin", h.offsetHeight <= W.innerHeight); }
    fit();
    W.addEventListener("resize", fit);
    function upd() {
      q = 0;
      if (getComputedStyle(h).position !== "sticky") { shade.style.opacity = 0; inner.style.transform = ""; h.style.visibility = ""; return; }
      var p = clamp(1 - next.getBoundingClientRect().top / h.offsetHeight, 0, 1);
      inner.style.transform = W.innerWidth < 900 || p === 0 ? "" : "scale(" + (1 - 0.1 * p).toFixed(4) + ")";
      shade.style.opacity = (0.55 * p).toFixed(3);
      h.style.visibility = p >= 1 ? "hidden" : "";
    }
    W.addEventListener("scroll", function () { if (!q) q = requestAnimationFrame(upd); }, { passive: true });
    W.addEventListener("resize", upd);
    upd();
  }

  /* the chequered seam: brass cells falling into the black, lifted by the scroll */
  function hash(x, y) {
    var h = Math.imul(x, 374761393) + Math.imul(y, 668265263);
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    return ((h ^ (h >>> 16)) >>> 0) / 4294967295;
  }
  /* fix round 2: its solid rows and its cells are the alarm band's own gradient (100deg, its five stops), laid over the
     band's box and continued below it; the seam had its own, horizontal one, a colour step at the joint */
  function seam(cv, al) {
    var ctx = cv.getContext("2d"), stops = [[0, "#b78f43"], [0.3, "#d9b867"], [0.52, "#f3dc9a"], [0.74, "#d6b262"], [1, "#c09848"]],
      acc = "#fff6dc", cell = 24, last = -1, q = 0, live = false;
    function draw(prog) {
      var w = cv.clientWidth, h = cv.clientHeight, dpr = Math.min(2, W.devicePixelRatio || 1);
      if (!w || !h) return;
      if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); last = -1; }
      var lift = prog * 2 * h, off = Math.floor(lift / cell), sub = lift - off * cell;
      if (Math.abs(lift - last) < 0.5) return;
      last = lift;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, w, h);
      // CSS linear-gradient(100deg) over the band (w x ah, its bottom edge at y 0): the line through its centre, as long as
      // the box's projection on it
      var ah = al.offsetHeight || 0, a = 100 * Math.PI / 180, dx = Math.sin(a), dy = -Math.cos(a),
        len = Math.abs(w * dx) + Math.abs(ah * dy), cx = w / 2, cy = -ah / 2;
      var fill = ctx.createLinearGradient(cx - dx * len / 2, cy - dy * len / 2, cx + dx * len / 2, cy + dy * len / 2);
      stops.forEach(function (s) { fill.addColorStop(s[0], s[1]); });
      var rows = Math.ceil(h / cell) + 1, cols = Math.ceil(w / cell), solid = Math.round(rows * 0.16);
      ctx.fillStyle = fill; ctx.fillRect(0, 0, w, solid * cell - sub);
      for (var r = solid; r < rows; r++) {
        var y = r * cell - sub, fade = 1 - (y + cell / 2) / h;
        if (fade <= 0) break;
        var rr = r + off;
        for (var c = 0; c < cols; c++) {
          if ((c + rr) & 1 || hash(c, rr) >= fade) continue;
          ctx.fillStyle = hash(c + 911, rr + 37) < 0.06 ? acc : fill;
          ctx.fillRect(c * cell, y, cell, cell);
        }
      }
    }
    function upd() { q = 0; draw(RM ? 0.25 : clamp(1 - cv.getBoundingClientRect().top / Math.min(W.innerHeight, 1100), 0, 1) * 0.5); }
    upd();
    if (RM) return;
    io(cv, function (v) { live = v; if (v) upd(); });
    W.addEventListener("scroll", function () { if (live && !q) q = requestAnimationFrame(upd); }, { passive: true });
    W.addEventListener("resize", function () { last = -1; upd(); });
  }

  /* the halftone map: canton dots lit by rank, a reticle and a read-out under the cursor */
  var T = { rest: "rgba(244,241,234,.13)", ramp: ["#4a3a1d", "#8a6a2d", "#c9a24e", "#f2d892", "#fff4d8"], a0: 0.42,
    hover: "#fff2c8", glow: "#c9a24e", bg: "#050403", lo: "#c9a24e", mid: "#f2d892", hot: "#fff8e6" };
  function mix(a, b, t) {
    var pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16), o = [];
    for (var s = 16; s >= 0; s -= 8) o.push(Math.round(((pa >> s) & 255) * (1 - t) + ((pb >> s) & 255) * t));
    return o;
  }
  function map(box, M) {
    var sec = box.closest(".mapsec"), ro = sec.querySelector(".ro"), tip = box.querySelector(".tip");
    var cv = D.createElement("canvas"), base = D.createElement("canvas"), ctx = cv.getContext("2d"), bx = base.getContext("2d");
    cv.setAttribute("aria-hidden", "true"); box.insertBefore(cv, tip);
    var cols = M.cols, rows = M.rows, N = cols * rows, grid = new Uint8Array(N), AL = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_";
    M.packed.split("|").forEach(function (s, r) {
      for (var i = 0; i < s.length; i += 5) {
        var c = AL.indexOf(s[i]) * 64 + AL.indexOf(s[i + 1]), n = AL.indexOf(s[i + 2]) * 64 + AL.indexOf(s[i + 3]), k = AL.indexOf(s[i + 4]);
        for (var j = 0; j < n; j++) grid[r * cols + c + j] = k + 1;
      }
    });
    var K = M.order.map(function (k) { var c = M.k[k]; return { k: k, n: c[0], name: c[1], href: c[2], ax: M.anchors[k][0], ay: M.anchors[k][1] }; });
    var maxN = 1, total = M.total || 0, order = [], rankOf = [];
    function ranks() {
      maxN = 1;
      K.forEach(function (c) { maxN = Math.max(maxN, c.n); });
      K.forEach(function (c) { c.t = Math.sqrt(c.n / maxN); });
      order = K.map(function (c, i) { return i; }).sort(function (a, b) { return K[b].n - K[a].n; });
      order.forEach(function (ci, r) { rankOf[ci] = r; });
    }
    ranks();
    var lit = new Float32Array(N), act = [], inAct = new Uint8Array(N), ign = 26, hov = -1, P = 0, Wd = 0, Ht = 0, dpr = 1;
    var px = -1, py = -1, lx = 0, ly = 0, lt = 0, inside = false, arm = new Spring(ROW, 0), stop = null, settle = 0;
    // fix round 2: the canton under the pointer on the map (mk), under the pointer in the list (lk), focused in the list
    // (fk); the read-out shows the first of them, and the cantons lighting up leave it alone
    var mk = -1, lk = -1, fk = -1;
    var links = [].slice.call(sec.querySelectorAll(".kl a[data-k]"));
    var rk = ro.querySelector(".rk"), nm = ro.querySelector(".nm"), vl = ro.querySelector(".vl b"), cum = ro.querySelector(".cum"), bar = ro.querySelector(".bar i");
    var r0 = [rk.textContent, nm.textContent, vl.textContent, cum.textContent];
    function pct(v) { return (v * 100).toFixed(1).replace(".", L.dec); }
    function size() {
      Wd = box.clientWidth; if (!Wd) return;
      P = Wd / cols; Ht = P * rows; dpr = Math.min(2, W.devicePixelRatio || 1);
      [cv, base].forEach(function (c) { c.width = Math.round(Wd * dpr); c.height = Math.round(Ht * dpr); });
      cv.style.height = Ht + "px";
      paintBase(); draw();
    }
    function tone(ci) {
      if (rankOf[ci] >= ign) return T.rest;
      var t = K[ci].t, r = T.ramp, x = t * (r.length - 1), i = Math.min(r.length - 2, Math.floor(x)), c = mix(r[i], r[i + 1], x - i);
      return "rgba(" + c[0] + "," + c[1] + "," + c[2] + "," + (T.a0 + (1 - T.a0) * t).toFixed(3) + ")";
    }
    function paintBase() {
      bx.setTransform(dpr, 0, 0, dpr, 0, 0); bx.clearRect(0, 0, Wd, Ht);
      var r = Math.max(1.05, P * 0.27), paths = K.map(function () { return new Path2D(); }), sq = new Path2D(), s = P * 0.66, o = (P - s) / 2;
      for (var j = 0; j < rows; j++) for (var i = 0; i < cols; i++) {
        var k = grid[j * cols + i]; if (!k) continue;
        if (k - 1 === hov) { sq.rect(i * P + o, j * P + o, s, s); continue; }
        var x = (i + 0.5) * P, y = (j + 0.5) * P, p = paths[k - 1];
        p.moveTo(x + r, y); p.arc(x, y, r, 0, 6.2832);
      }
      paths.forEach(function (p, ci) { bx.fillStyle = tone(ci); bx.fill(p); });
      if (hov >= 0) { bx.shadowColor = T.glow; bx.shadowBlur = 10; bx.fillStyle = T.hover; bx.fill(sq); bx.shadowBlur = 0; }
    }
    function light(i, j, l) {
      if (i < 0 || j < 0 || i >= cols || j >= rows) return;
      var idx = j * cols + i;
      if (!grid[idx] || l <= lit[idx]) return;
      lit[idx] = l;
      if (!inAct[idx]) { inAct[idx] = 1; act.push(idx); }
    }
    function draw() {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, Wd, Ht); ctx.drawImage(base, 0, 0, Wd, Ht);
      for (var a = 0; a < act.length; a++) {
        var idx = act[a], l = lit[idx], i = idx % cols, j = (idx / cols) | 0, x = i * P, y = j * P;
        if ((i + j) & 1) { ctx.globalAlpha = Math.min(1, l * 1.3); ctx.fillStyle = T.bg; ctx.fillRect(x, y, P, P); }
        else { var s = P * (0.7 + 0.3 * l), o = (P - s) / 2; ctx.globalAlpha = Math.min(1, 0.25 + l); ctx.fillStyle = l > 0.86 ? T.hot : l > 0.5 ? T.mid : T.lo; ctx.fillRect(x + o, y + o, s, s); }
      }
      ctx.globalAlpha = 1;
    }
    function frame(dt) {
      var moving = arm.step(dt), R = arm.x * (420 / P), dec = Math.exp(-dt / 170);
      for (var a = act.length - 1; a >= 0; a--) { var idx = act[a]; lit[idx] *= dec; if (lit[idx] < 0.02) { lit[idx] = 0; inAct[idx] = 0; act.splice(a, 1); } }
      if (inside && px >= 0) {
        var ci = Math.floor(px / P), cj = Math.floor(py / P), Ri = Math.ceil(R);
        for (var d = -Ri; d <= Ri; d++) { var l = 1 - Math.abs(d) / Math.max(R, 1); if (l > 0) { light(ci + d, cj, l); light(ci, cj + d, l); } }
        for (var dj = -4; dj <= 4; dj++) for (var di = -4; di <= 4; di++) { var dd = Math.sqrt(di * di + dj * dj); if (dd <= 4.2) light(ci + di, cj + dj, 1 - dd / 5.2); }
      }
      draw();
      if (!(act.length || moving || inside)) { stop = null; return false; }
    }
    function run() { if (!stop) stop = tick(frame); }
    function at(x, y) {
      var i = Math.floor(x / P), j = Math.floor(y / P);
      for (var r = 0; r <= 1; r++) for (var dj = -r; dj <= r; dj++) for (var di = -r; di <= r; di++) {
        var ii = i + di, jj = j + dj;
        if (ii >= 0 && jj >= 0 && ii < cols && jj < rows && grid[jj * cols + ii]) return grid[jj * cols + ii] - 1;
      }
      return -1;
    }
    function readout(ci) {
      var c, w;
      if (ci < 0 && (ign >= 26 || ign < 1)) {
        rk.textContent = r0[0]; nm.textContent = r0[1]; vl.textContent = r0[2]; cum.textContent = r0[3]; w = 100;
      } else if (ci < 0) {
        c = K[order[ign - 1]];
        rk.textContent = fmt(L.map_rank, { r: ign }); nm.textContent = c.name; vl.textContent = A.count(c.n);
        cum.textContent = fmt(L.map_lit, { n: ign }); w = ign / 26 * 100;
      } else {
        c = K[ci];
        rk.textContent = fmt(L.map_rank, { r: rankOf[ci] + 1 }); nm.textContent = c.name; vl.textContent = A.count(c.n);
        cum.textContent = fmt(L.map_share, { p: pct(total ? c.n / total : 0) }); w = total ? c.n / total * 100 : 0;
      }
      bar.style.setProperty("--w", w.toFixed(1) + "%");
    }
    function hover(ci, x, y) {
      if (ci !== hov) {
        hov = ci; paintBase(); draw();
        links.forEach(function (a) { a.classList.toggle("on", ci >= 0 && a.getAttribute("data-k") === K[ci].k); });
        readout(ci);
        if (ci >= 0) { tip.firstChild.textContent = K[ci].k + " · " + K[ci].name; tip.lastChild.textContent = A.count(K[ci].n) + " " + (K[ci].n === 1 ? L.open_1 : L.open_n).replace(/^1 |\{n\} /, ""); }
      }
      tip.classList.toggle("on", ci >= 0);
      if (ci >= 0) {
        var tw = tip.offsetWidth, th = tip.offsetHeight, lx2 = Math.min(Wd - tw, x + 18), ly2 = y + 18 + th > Ht ? y - th - 14 : y + 18;
        tip.style.transform = "translate(" + Math.max(0, lx2).toFixed(1) + "px," + Math.max(0, ly2).toFixed(1) + "px)";
      }
    }
    function held() {
      var ci = lk >= 0 ? lk : fk;
      if (ci >= 0) hover(ci, (K[ci].ax + 0.5) * P, (K[ci].ay + 0.5) * P); else hover(-1);
    }
    function move(x, y, now) {
      var sp = Math.hypot(x - lx, y - ly) / Math.max(8, now - lt);
      lx = x; ly = y; lt = now; px = x; py = y; inside = true;
      arm.t = sp > 0.9 ? 0.12 : 1;
      clearTimeout(settle); settle = setTimeout(function () { arm.t = 1; run(); }, 110);
      mk = at(x, y);
      cv.style.cursor = mk >= 0 ? "pointer" : "";
      if (mk >= 0) hover(mk, x, y); else held();
      run();
    }
    if (!RM) {
      cv.addEventListener("pointermove", function (e) {
        if (e.pointerType !== "mouse" && !FINE) return;
        var r = cv.getBoundingClientRect(); move(e.clientX - r.left, e.clientY - r.top, performance.now());
      }, { passive: true });
      cv.addEventListener("pointerleave", function () { inside = false; arm.t = 0; mk = -1; cv.style.cursor = ""; held(); run(); });
    }
    cv.addEventListener("pointerdown", function (e) {
      var r = cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top, ci = at(x, y);
      if (e.pointerType === "mouse" && ci >= 0) { location.href = K[ci].href; return; }
      hover(ci, x, y);
    });
    links.forEach(function (a) {
      var ci = M.order.indexOf(a.getAttribute("data-k"));
      if (ci < 0) return;
      a.addEventListener("mouseenter", function () { lk = ci; if (mk < 0) held(); });
      a.addEventListener("focus", function () { fk = ci; if (mk < 0) held(); });
      a.addEventListener("mouseleave", function () { lk = -1; if (mk < 0) held(); });
      a.addEventListener("blur", function () { fk = -1; if (mk < 0) held(); });
    });
    /* the cantons light up in rank order: with the scroll on a pinned stage, else on a timer */
    var q = 0;
    function pinned() { var st = sec.querySelector(".stage"); return st && getComputedStyle(st).position === "sticky"; }
    function byScroll() {
      q = 0;
      var n = 26;
      if (pinned()) {
        var r = sec.getBoundingClientRect(), span = sec.offsetHeight - W.innerHeight, p = span > 0 ? clamp(-r.top / span, 0, 1) : 1;
        n = Math.max(1, Math.min(26, Math.ceil(p / 0.78 * 26)));
      }
      if (n !== ign) { ign = n; paintBase(); draw(); if (hov < 0) readout(-1); }
    }
    box.classList.add("ready");
    size();
    W.addEventListener("resize", function () { size(); byScroll(); });
    if (!RM) {
      if (pinned()) { ign = 1; W.addEventListener("scroll", function () { if (!q) q = requestAnimationFrame(byScroll); }, { passive: true }); byScroll(); }
      else {
        ign = 0; paintBase(); draw();
        once(box, 0, function () {
          var t0 = -1;
          tick(function (dt, now) { if (t0 < 0) t0 = now; var n = Math.min(26, Math.floor((now - t0) / 95) + 1); if (n !== ign) { ign = n; paintBase(); draw(); if (hov < 0) readout(-1); } return n < 26; });
        });
      }
    }
    readout(-1);
    // the counts of the reader's moment, once a deadline has passed since the build (/stand.js, fix round 1)
    if (A.oc) A.oc.then(function (c) {
      if (!c) return;
      K.forEach(function (k) { k.n = c.k[k.k] || 0; });
      total = c.a; r0[2] = A.count(total); ranks(); paintBase(); draw(); if (hov < 0) readout(-1);
    });
  }

  var mj = D.getElementById("karte"), mb = D.querySelector(".mapbox");
  if (mj && mb && W.Path2D) { try { map(mb, JSON.parse(mj.textContent)); } catch (x) { } }
  [].forEach.call(D.querySelectorAll("h2[data-split]"), reveal);
  [].forEach.call(D.querySelectorAll(".stats .fig b"), function (b) { countUp(b.querySelector(".n") || b.querySelector("#total") || b); });
  [].forEach.call(D.querySelectorAll("[data-up]"), rise);
  var h = D.querySelector(".hero");
  hero(h); stack(h, h && h.nextElementSibling);
  var al = D.querySelector(".alarm"), nx = al && al.nextElementSibling;
  if (nx && W.HTMLCanvasElement) { var cv = D.createElement("canvas"); cv.className = "seam"; cv.setAttribute("aria-hidden", "true"); nx.insertBefore(cv, nx.firstChild); seam(cv, al); }
})();
