/* Corio Metals site behaviour. Rates come from rates.js (window.WM_RATES); site settings from window.CM. */
(function () {
  "use strict";
  var CM = window.CM || { phone: "0427888222", minKg: 1000, maps: "#" };

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

  function fmt(n, d) { return Number(n).toLocaleString("en-AU", { maximumFractionDigits: d || 0, minimumFractionDigits: d || 0 }); }
  var R = window.WM_RATES || { rates: {}, fees: {} };
  var rates = R.rates || {}, fees = R.fees || {};
  var money = function (n, dp) { return "$" + Number(n).toLocaleString("en-AU", { minimumFractionDigits: dp, maximumFractionDigits: dp }); };
  var has = function (v) { return typeof v === "number" && isFinite(v) && v >= 0; };

  /* ---- any price on the page (board, home strip) ---- */
  document.querySelectorAll("[data-rate]").forEach(function (el) {
    var v = rates[el.getAttribute("data-rate")];
    if (has(v)) el.innerHTML = '<span class="amt">' + money(v, 2) + '</span><span class="per">/kg</span>';
  });
  document.querySelectorAll("[data-fee]").forEach(function (el) {
    var v = fees[el.getAttribute("data-fee")];
    if (has(v)) el.innerHTML = '<span class="amt">' + money(v, 0) + '</span><span class="per">each</span>';
  });
  document.querySelectorAll("[data-rates-updated]").forEach(function (el) {
    if (R.updated) el.textContent = String(R.updated);
  });

  /* ---- price board ---- */
  var board = document.querySelector(".board");
  if (board) {
    var anyRate = Object.keys(rates).some(function (k) { return has(rates[k]); });
    var stamp = document.getElementById("rates-stamp");
    if (stamp && R.updated) {
      stamp.classList.add("is-live");
      stamp.querySelector("span").innerHTML = "Rates per kg · <b>" + String(R.updated).replace(/[<>&]/g, "") + "</b>";
    } else if (stamp && !anyRate) {
      stamp.querySelector("span").textContent = "Call for today's rates · per kg, clean and sorted";
    }
    var tabs = board.querySelectorAll('[role="tab"]');
    var pick = function (t) {
      tabs.forEach(function (x) {
        var on = x === t; x.setAttribute("aria-selected", on ? "true" : "false"); x.tabIndex = on ? 0 : -1;
        document.getElementById(x.getAttribute("aria-controls")).hidden = !on;
      });
    };
    tabs.forEach(function (t, i) {
      t.tabIndex = i === 0 ? 0 : -1;
      t.addEventListener("click", function () { pick(t); t.scrollIntoView({ block: "nearest", inline: "nearest" }); });
      t.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0; if (!d) return;
        e.preventDefault(); var n = tabs[(i + d + tabs.length) % tabs.length]; pick(n); n.focus();
      });
    });
  }

  /* ---- load estimate: drop off under a tonne, collection from a tonne ---- */
  var est = document.getElementById("est");
  if (est) {
    var rows = est.querySelectorAll(".mrow");
    var kgOf = function (row) { var v = parseFloat(row.querySelector(".kg-in").value); return isFinite(v) && v > 0 ? Math.round(v) : 0; };
    var setKg = function (row, v) { row.querySelector(".kg-in").value = Math.max(0, Math.round(v)); calcEst(); };
    rows.forEach(function (row) {
      row.querySelector(".kg-minus").addEventListener("click", function () { setKg(row, kgOf(row) - 10); });
      row.querySelector(".kg-plus").addEventListener("click", function () { setKg(row, kgOf(row) + 10); });
      row.querySelector(".kg-in").addEventListener("input", calcEst);
      row.querySelector(".kg-in").addEventListener("focus", function () { if (this.value === "0") this.select(); });
      row.querySelector(".mgrade").addEventListener("change", calcEst);
    });
    document.getElementById("est-clear").addEventListener("click", function () { rows.forEach(function (r) { r.querySelector(".kg-in").value = 0; }); calcEst(); });
    calcEst();
  }

  function calcEst() {
    var money0 = function (n) { return "$" + Math.round(n).toLocaleString("en-AU"); };
    var lines = [], kg = 0, value = 0, priced = true;
    est.querySelectorAll(".mrow").forEach(function (row) {
      var v = parseFloat(row.querySelector(".kg-in").value); v = isFinite(v) && v > 0 ? Math.round(v) : 0;
      row.classList.toggle("has", v > 0);
      if (!v) return;
      var sel = row.querySelector(".mgrade"), gid = sel.value, gname = sel.options[sel.selectedIndex].text;
      var r = rates[gid];
      kg += v;
      if (has(r)) { value += v * r; lines.push([gname, fmt(v) + " kg · " + money0(v * r)]); }
      else { priced = false; lines.push([gname, fmt(v) + " kg"]); }
    });
    var val = document.getElementById("est-val"), cap = document.getElementById("est-cap"), lbl = document.getElementById("est-lbl");
    document.getElementById("est-lines").innerHTML = lines.map(function (l) { return "<li><span>" + l[0] + "</span><b>" + l[1] + "</b></li>"; }).join("");
    document.getElementById("est-kg").textContent = fmt(kg) + " kg";
    val.classList.remove("is-call");
    var big = kg >= CM.minKg;
    if (!kg) {
      lbl.textContent = "Your estimate"; val.textContent = "$0"; cap.textContent = "Add some kilos to get started";
    } else if (priced) {
      lbl.textContent = "Your estimate";
      val.textContent = value < 20 ? money0(value) : money0(value * 0.9) + "–" + money0(value);
      cap.textContent = "For about " + fmt(kg) + " kg at our listed rates";
    } else {
      lbl.textContent = "Your load"; val.classList.add("is-call"); val.textContent = fmt(kg) + " kg";
      cap.textContent = "Call for today's rate on this load";
    }
    // which way in: the tonne line
    var path = document.getElementById("est-path"), cta = document.getElementById("est-cta"), note = document.getElementById("est-note");
    var meter = document.getElementById("est-meter");
    if (meter) {
      var pct = Math.min(100, kg / (2 * CM.minKg) * 100);
      meter.style.setProperty("--p", pct + "%");
      meter.classList.toggle("over", big);
    }
    var what = lines.map(function (l) { return l[0] + " (" + l[1].split(" · ")[0] + ")"; }).join(", ");
    if (big) {
      path.innerHTML = "<b>That's over a tonne.</b> We can collect it from your site. Collections are quoted before we come.";
      cta.innerHTML = '<a class="btn btn-amber" href="collections.html?kg=' + kg + (what ? "&what=" + encodeURIComponent(what) : "") + '#quote">Book a collection</a>' +
        '<a class="btn btn-line" href="tel:' + CM.phone + '">Call for today\'s rate</a>';
      note.innerHTML = "Metal value at our listed rates, set on our weighbridge. The collection itself is quoted&nbsp;separately.";
    } else {
      path.innerHTML = kg ? "Under a tonne: <b>drop it off</b> at 116 Furner Avenue. " + fmt(CM.minKg - kg) + " kg more and we can collect it." : "Under a tonne: drop it off. A tonne or more: we can collect it.";
      cta.innerHTML = (kg && !priced ? '<a class="btn btn-amber" href="tel:' + CM.phone + '">Call for today\'s rate</a>' : "") +
        '<a class="btn btn-line" href="' + CM.maps + '" target="_blank" rel="noopener">Get directions</a>';
      note.innerHTML = "Final price set on the scale at the yard. Paid by bank transfer, so bring photo&nbsp;ID.";
    }
  }

  /* ---- collection form: prefill from the load estimate ---- */
  (function () {
    var f = document.querySelector('form.enq[data-subject="Collection quote request"]'); if (!f) return;
    try {
      var q = new URLSearchParams(location.search);
      if (q.get("what") && f.elements.what && !f.elements.what.value) f.elements.what.value = q.get("what").slice(0, 600);
      var kg = parseInt(q.get("kg"), 10);
      if (kg && f.elements.size) {
        var t = kg / 1000, opt = t < 3 ? "1 to 3 tonnes" : t < 10 ? "3 to 10 tonnes" : "More than 10 tonnes";
        f.elements.size.value = opt;
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
