/* Corio Metals site behaviour. Site settings from window.CM; item data from window.CM_ITEMS. */
(function () {
  "use strict";
  var CM = window.CM || { phone: "0433115500", minKg: 1000, maps: "#" };

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
    window.addEventListener("resize", function () { if (window.innerWidth > 1060 && nav.classList.contains("open")) setMenu(false); });
  }

  function fmt(n) { return Number(n).toLocaleString("en-AU", { maximumFractionDigits: 0 }); }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  /* ---- load check ---- */
  var lc = document.getElementById("lc");
  if (lc) {
    var tabs = lc.querySelectorAll('[role="tab"]');
    var pick = function (t) {
      tabs.forEach(function (x) {
        var on = x === t; x.setAttribute("aria-selected", on ? "true" : "false"); x.tabIndex = on ? 0 : -1;
        document.getElementById(x.getAttribute("aria-controls")).hidden = !on;
      });
    };
    tabs.forEach(function (t, i) {
      t.tabIndex = i === 0 ? 0 : -1;
      t.addEventListener("click", function () { pick(t); });
      t.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0; if (!d) return;
        e.preventDefault(); var n = tabs[(i + d + tabs.length) % tabs.length]; pick(n); n.focus();
      });
    });
    var rows = lc.querySelectorAll(".lrow");
    var countOf = function (row) { var v = parseInt(row.querySelector(".lc-n").value, 10); return isFinite(v) && v > 0 ? v : 0; };
    var setCount = function (row, v) { row.querySelector(".lc-n").value = Math.max(0, Math.min(999, v)); calc(); };
    rows.forEach(function (row) {
      row.querySelector(".lc-minus").addEventListener("click", function () { setCount(row, countOf(row) - 1); });
      row.querySelector(".lc-plus").addEventListener("click", function () { setCount(row, countOf(row) + 1); });
      var inp = row.querySelector(".lc-n");
      inp.addEventListener("input", calc);
      inp.addEventListener("focus", function () { if (this.value === "0") this.select(); });
    });
    lc.querySelectorAll(".lc-more").forEach(function (b) {
      b.addEventListener("click", function () { b.parentNode.classList.add("show-all"); });
    });
    document.getElementById("lc-clear").addEventListener("click", function () { rows.forEach(function (r) { r.querySelector(".lc-n").value = 0; }); calc(); });
    calc();
  }

  function calc() {
    var kg = 0, n = 0, lines = [], fees = [], preps = [], calls = [], what = [];
    lc.querySelectorAll(".lrow").forEach(function (row) {
      var c = parseInt(row.querySelector(".lc-n").value, 10); c = isFinite(c) && c > 0 ? c : 0;
      row.classList.toggle("has", c > 0);
      if (!c) return;
      var k = +row.getAttribute("data-kg") * c, st = row.getAttribute("data-st"), name = row.getAttribute("data-name"), note = row.getAttribute("data-note");
      kg += k; n += c;
      lines.push("<li><span>" + esc(name) + (c > 1 ? " &times; " + c : "") + "</span><b>" + fmt(k) + "&nbsp;kg</b></li>");
      what.push(name + (c > 1 ? " x " + c : ""));
      if (st === "fee") fees.push(name + (c > 1 ? " &times; " + c : "") + ": " + esc(note.split(". ")[0].replace(/\.$/, "")));
      if (st === "prep" && note) preps.push(esc(note.charAt(0).toLowerCase() + note.slice(1).replace(/\.$/, "")));
      if (st === "call") calls.push(esc(name));
    });
    var val = document.getElementById("lc-val"), cap = document.getElementById("lc-cap"), verdict = document.getElementById("lc-verdict");
    var big = kg >= CM.minKg;
    val.innerHTML = fmt(kg) + "&nbsp;kg";
    cap.textContent = n ? "Rough estimate for " + n + (n === 1 ? " item" : " items") : "Add a few items to get started";
    var meter = document.getElementById("lc-meter");
    meter.style.setProperty("--p", Math.min(100, kg / (2 * CM.minKg) * 100) + "%");
    meter.classList.toggle("over", big);
    document.getElementById("lc-lines").innerHTML = lines.join("");
    var cost = document.getElementById("lc-cost"), gate = document.getElementById("lc-gate");
    gate.querySelector("span").textContent = big ? "Collection" : "At the gate";
    gate.classList.toggle("has-fee", !big && fees.length > 0);
    cost.innerHTML = big ? "Quoted first" : fees.length ? "Handling fee on " + fees.length + (fees.length === 1 ? " item" : " items") : "No charge";
    var extra = "";
    if (fees.length && !big) extra += '<p class="lc-note">' + fees.join("<br>") + "</p>";
    if (preps.length) extra += '<p class="lc-note">Before ' + (big ? "we come" : "you come") + ": " + preps.join("; ") + ".</p>";
    if (calls.length) extra += '<p class="lc-note">Call first for: ' + calls.join(", ") + ".</p>";
    gate.querySelectorAll(".lc-note").forEach(function (x) { x.remove(); });
    gate.insertAdjacentHTML("beforeend", extra);
    var cta = document.getElementById("lc-cta");
    if (!n) {
      verdict.innerHTML = "Under a tonne, drop it off. A tonne or more, we collect.";
      cta.innerHTML = "";
    } else if (big) {
      verdict.innerHTML = "<b>That's over a tonne.</b> We can collect it from your site. One service fee, quoted before we come.";
      cta.innerHTML = '<a class="btn btn-amber" href="collections.html?kg=' + Math.round(kg) + "&what=" + encodeURIComponent(what.join(", ")) + '#quote">Book a collection</a>' +
        '<a class="btn btn-line" href="tel:' + CM.phone + '">Call Rory</a>';
    } else {
      verdict.innerHTML = "<b>Drop it off.</b> " + fmt(CM.minKg - kg) + "&nbsp;kg under a tonne, so bring it to 116 Furner Avenue.";
      cta.innerHTML = '<a class="btn btn-amber" href="' + CM.maps + '" target="_blank" rel="noopener">Directions</a>' +
        '<a class="btn btn-line" href="drop-off.html">Drop-off details</a>';
    }
  }

  /* ---- collection form: prefill from the load check ---- */
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

  /* ---- enquiry forms -> pre-filled email ---- */
  document.querySelectorAll("form.enq").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var get = function (n) { var el = f.elements[n]; return el ? el.value.trim() : ""; };
      var subject = (f.getAttribute("data-subject") || "Enquiry") + (get("org") ? " · " + get("org") : get("site") ? " · " + get("site") : "");
      var lines = [];
      Array.prototype.forEach.call(f.elements, function (el) {
        if (!el.name || !el.value || !el.value.trim() || el.type === "submit") return;
        if ((el.type === "radio" || el.type === "checkbox") && !el.checked) return;
        lines.push((el.getAttribute("data-label") || el.name) + ": " + el.value.trim());
      });
      var done = f.querySelector(".form-done"); if (done) done.hidden = false;
      window.location.href = "mailto:" + f.getAttribute("data-to") + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
    });
  });
})();
