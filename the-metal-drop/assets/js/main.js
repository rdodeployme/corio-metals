/* The Metal Drop site behaviour. Site settings from window.MD. */
(function () {
  "use strict";
  var MD = window.MD || { phone: "0433115500", minKg: 1000, maps: "#", contact: "Rory" };
  // Handling fees at the gate (Recycle North Geelong price list): low and high per item
  var FEE = { gas: [15, 25], ext: [10, 15], solar: [39, 39] };

  /* ---- menu ---- */
  var btn = document.querySelector(".menu-btn"), nav = document.getElementById("nav");
  if (btn && nav) {
    var setMenu = function (open) {
      nav.classList.toggle("open", open);
      document.body.classList.toggle("menu-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.textContent = open ? "Close" : "Menu";
    };
    btn.addEventListener("click", function () { setMenu(!nav.classList.contains("open")); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && nav.classList.contains("open")) { setMenu(false); btn.focus(); } });
    window.addEventListener("resize", function () { if (window.innerWidth > 1080 && nav.classList.contains("open")) setMenu(false); });
  }

  function fmt(n) { return Number(n).toLocaleString("en-AU", { maximumFractionDigits: 0 }); }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function money(a, b) { return a === b ? "$" + fmt(a) : "$" + fmt(a) + " to $" + fmt(b); }
  function words(s) {
    return String(s || "").toLowerCase().replace(/[^a-z0-9 ]+/g, " ").split(/\s+/).filter(Boolean).map(function (w) {
      return w.length > 3 ? w.replace(/ies$/, "y").replace(/(es|s)$/, "") : w;
    });
  }

  /* ---- item checker ---- */
  var api = null, root = document.getElementById("ck");
  if (root) api = checker(root);

  function checker(root) {
    var tiles = [].slice.call(root.querySelectorAll(".tile"));
    var input = document.getElementById("ck-q");
    var fbtns = [].slice.call(root.querySelectorAll(".fbtn"));
    var more = root.querySelector(".ck-more");
    var empty = root.querySelector(".ck-empty");
    var $ = function (id) { return document.getElementById(id); };
    var el = { hint: $("ck-hint"), msg: $("ck-msg"), lines: $("ck-lines"), out: $("ck-out"), kg: $("ck-kg"), cap: $("ck-cap"),
      meter: $("ck-meter"), costL: $("ck-cost-l"), cost: $("ck-cost"), verdict: $("ck-verdict"), prep: $("ck-prep"),
      prepH: $("ck-prep-h"), prepL: $("ck-prep-l"), cta: $("ck-cta"), clear: $("ck-clear"), bar: $("ck-bar"), barT: $("ck-bar-t"), panel: $("ck-load") };
    var filter = "all", expanded = !more, counts = {}, order = [], byId = {}, msgTimer = null;
    tiles.forEach(function (t) { byId[t.getAttribute("data-id")] = t; });

    function apply() {
      var ws = words(input.value);
      var shown = 0, hid = 0;
      tiles.forEach(function (t) {
        var okF = filter === "all" || t.getAttribute("data-g") === filter;
        var hay = t.getAttribute("data-q");
        var okQ = ws.every(function (w) { return hay.indexOf(w) >= 0; });
        var limited = !expanded && !ws.length && filter === "all" && t.classList.contains("more");
        var vis = okF && okQ && !limited;
        if (okF && okQ && limited) hid++;
        t.hidden = !vis;
        if (vis) shown++;
      });
      empty.hidden = shown > 0;
      if (more) { more.hidden = hid === 0; more.querySelector("b").textContent = hid; }
    }

    function setFilter(f) {
      filter = f;
      fbtns.forEach(function (x) { x.setAttribute("aria-pressed", x.getAttribute("data-f") === f ? "true" : "false"); });
      apply();
    }
    fbtns.forEach(function (b) { b.addEventListener("click", function () { setFilter(b.getAttribute("data-f")); }); });
    input.addEventListener("input", apply);
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); input.blur(); } });
    if (more) more.addEventListener("click", function () { expanded = true; apply(); });

    function showMsg(text) {
      el.msg.textContent = text; el.msg.hidden = false;
      if (window.innerWidth <= 900) {
        el.barT.textContent = text; el.bar.hidden = false; el.bar.classList.add("is-msg");
        clearTimeout(msgTimer);
        msgTimer = setTimeout(function () { el.bar.classList.remove("is-msg"); render(); }, 5000);
      }
    }

    tiles.forEach(function (t) {
      t.addEventListener("click", function () {
        if (t.getAttribute("data-st") === "no") { showMsg(t.getAttribute("data-msg")); return; }
        add(t.getAttribute("data-id"), 1);
        t.classList.remove("flash"); void t.offsetWidth; t.classList.add("flash");
      });
    });

    function add(id, d) {
      var c = (counts[id] || 0) + d;
      if (c <= 0) { delete counts[id]; order = order.filter(function (x) { return x !== id; }); }
      else { if (!counts[id]) order.push(id); counts[id] = Math.min(99, c); }
      el.msg.hidden = true;
      render();
    }

    el.lines.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      var id = b.closest("li").getAttribute("data-id");
      add(id, b.classList.contains("ln-p") ? 1 : -1);
      var again = el.lines.querySelector('li[data-id="' + id + '"] .' + (b.classList.contains("ln-p") ? "ln-p" : "ln-m"));
      if (again) again.focus();
    });
    el.clear.addEventListener("click", function () { counts = {}; order = []; el.msg.hidden = true; render(); });

    function render() {
      var kg = 0, n = 0, fa = 0, fb = 0, preps = [], what = [], lines = "";
      order.forEach(function (id) {
        var t = byId[id], c = counts[id];
        var name = t.getAttribute("data-name"), k = +t.getAttribute("data-kg") * c, prep = t.getAttribute("data-prep");
        kg += k; n += c;
        if (FEE[id]) { fa += FEE[id][0] * c; fb += FEE[id][1] * c; }
        if (prep) preps.push("<li><span><b>" + esc(name) + ":</b> " + esc(prep.charAt(0).toLowerCase() + prep.slice(1)) + "</span></li>");
        what.push(name + (c > 1 ? " x " + c : ""));
        lines += '<li data-id="' + id + '"><span class="ln-name">' + esc(name) + "</span>" +
          '<span class="ln-step"><button type="button" class="ln-m" aria-label="One less: ' + esc(name) + '">&minus;</button><b>' + c + "</b>" +
          '<button type="button" class="ln-p" aria-label="One more: ' + esc(name) + '">+</button></span>' +
          '<span class="ln-kg">' + fmt(k) + "&nbsp;kg</span></li>";
      });
      tiles.forEach(function (t) {
        var c = counts[t.getAttribute("data-id")] || 0;
        t.classList.toggle("on", c > 0);
        t.querySelector(".tile-n").textContent = c ? c : "";
      });
      el.lines.innerHTML = lines;
      el.hint.hidden = n > 0;
      el.clear.hidden = n === 0;
      el.out.hidden = n === 0;
      var big = kg >= MD.minKg;
      el.kg.innerHTML = fmt(kg) + "&nbsp;kg";
      el.cap.textContent = n + (n === 1 ? " item" : " items") + ", using rough guide weights";
      el.meter.style.setProperty("--p", Math.min(100, kg / (2 * MD.minKg) * 100) + "%");
      el.meter.classList.toggle("over", big);
      el.costL.textContent = big ? "Collection" : "At the gate";
      el.cost.textContent = big ? "Quoted first" : fb ? money(fa, fb) : "No charge";
      el.cost.parentNode.classList.toggle("fee", !big && fb > 0);
      if (big) {
        el.verdict.className = "ck-verdict big";
        el.verdict.innerHTML = "<b>That's over a tonne, so we'll come to you.</b>One service fee, quoted before we come.<small>Or bring it in over a few trips.</small>";
        el.cta.innerHTML = '<a class="btn btn-red" href="business.html?kg=' + Math.round(kg) + "&what=" + encodeURIComponent(what.join(", ")) + '#quote">Get a collection quote</a>' +
          '<a class="btn btn-line" href="tel:' + MD.phone + '">Call ' + esc(MD.contact) + "</a>";
      } else {
        el.verdict.className = "ck-verdict";
        el.verdict.innerHTML = "<b>Bring it in.</b>No booking needed for a car, ute or trailer.";
        el.cta.innerHTML = '<a class="btn btn-red" href="' + MD.maps + '" target="_blank" rel="noopener">Get directions</a>' +
          '<a class="btn btn-line" href="drop-off.html">Plan your visit</a>';
      }
      el.prep.hidden = preps.length === 0;
      el.prepH.textContent = big ? "Before we come" : "Before you come";
      el.prepL.innerHTML = preps.join("");
      if (!el.bar.classList.contains("is-msg")) {
        el.barT.innerHTML = n + (n === 1 ? " item" : " items") + " · " + fmt(kg) + "&nbsp;kg · " + (big ? "Over a tonne" : fb ? money(fa, fb) + " in fees" : "No charge");
      }
      bar();
    }

    /* the summary bar on phones: shows while the item grid is on screen and the panel isn't */
    var gridOn = false, panelOn = false;
    function bar() {
      var n = order.length;
      el.bar.hidden = !(el.bar.classList.contains("is-msg") || (n > 0 && gridOn && !panelOn));
    }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { es.forEach(function (e) { gridOn = e.isIntersecting; }); bar(); }, { threshold: 0 }).observe(root.querySelector(".ck-grid"));
      new IntersectionObserver(function (es) { es.forEach(function (e) { panelOn = e.isIntersecting; }); bar(); }, { threshold: 0.25 }).observe(el.panel);
    }

    apply();
    render();

    return {
      search: function (q, jump) {
        input.value = q;
        setFilter("all");
        var target = document.getElementById("check") || root;
        if (jump !== false) target.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
      }
    };
  }

  /* hero search and quick picks send their words into the checker on the same page */
  document.querySelectorAll("form.hs").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      if (!api) return;
      e.preventDefault();
      api.search(f.elements.q.value);
    });
  });
  document.querySelectorAll(".quick a[data-q]").forEach(function (a) {
    a.addEventListener("click", function (e) { if (!api) return; e.preventDefault(); api.search(a.getAttribute("data-q")); });
  });
  if (api) {
    try { var q0 = new URLSearchParams(location.search).get("q"); if (q0) api.search(q0.slice(0, 60)); } catch (e) {}
  }

  /* ---- collection form: prefill from the checker ---- */
  (function () {
    var f = document.querySelector('form.enq[data-subject="Collection quote request"]'); if (!f) return;
    try {
      var q = new URLSearchParams(location.search);
      if (q.get("what") && f.elements.what && !f.elements.what.value) f.elements.what.value = q.get("what").slice(0, 600);
      var kg = parseInt(q.get("kg"), 10);
      if (kg && f.elements.size) {
        var t = kg / 1000;
        f.elements.size.value = t < 3 ? "1 to 3 tonnes" : t < 10 ? "3 to 10 tonnes" : "More than 10 tonnes";
      }
    } catch (e) {}
  })();

  /* ---- enquiry forms open a pre-filled email ---- */
  document.querySelectorAll("form.enq").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var get = function (n) { var x = f.elements[n]; return x ? x.value.trim() : ""; };
      var subject = (f.getAttribute("data-subject") || "Enquiry") + (get("org") ? " · " + get("org") : get("site") ? " · " + get("site") : "");
      var lines = [];
      Array.prototype.forEach.call(f.elements, function (x) {
        if (!x.name || !x.value || !x.value.trim() || x.type === "submit") return;
        if ((x.type === "radio" || x.type === "checkbox") && !x.checked) return;
        lines.push((x.getAttribute("data-label") || x.name) + ": " + x.value.trim());
      });
      var done = f.querySelector(".form-done"); if (done) done.hidden = false;
      window.location.href = "mailto:" + f.getAttribute("data-to") + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
    });
  });
})();
