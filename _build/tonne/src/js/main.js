/* By The Tonne site behaviour. Settings from window.BTT; estimator data from window.BTT_ITEMS and BTT_EG. */
(function () {
  "use strict";
  var S = window.BTT || { phone: "0427888222", minKg: 1000, contact: "Nigel" };

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

  function fmt(n, d) { return Number(n).toLocaleString("en-AU", { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }); }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  /* ---- estimator: build a list of what's on site, total it against the one-tonne minimum ---- */
  var mf = document.getElementById("mf"), ITEMS = window.BTT_ITEMS || {}, EG = window.BTT_EG || {};
  if (mf) {
    var $ = function (id) { return document.getElementById(id); };
    var form = $("mf-add"), sel = $("mf-item"), qty = $("mf-qty"), table = $("mf-table"), body = $("mf-body"), empty = $("mf-empty");
    var list = []; // [{id, q}]
    var DEL = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 5l10 10M15 5L5 15" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>';

    var addLine = function (id, q) {
      q = Math.max(1, Math.min(9999, parseInt(q, 10) || 1));
      var hit = list.filter(function (l) { return l.id === id; })[0];
      if (hit) hit.q = Math.min(9999, hit.q + q); else list.push({ id: id, q: q });
    };
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      addLine(sel.value, qty.value);
      qty.value = 1;
      render(sel.value);
    });
    mf.querySelectorAll("[data-eg]").forEach(function (b) {
      b.addEventListener("click", function () {
        var eg = EG[b.getAttribute("data-eg")] || {};
        list = [];
        Object.keys(eg).forEach(function (id) { addLine(id, eg[id]); });
        render();
      });
    });
    body.addEventListener("input", function (e) {
      var inp = e.target.closest("input"); if (!inp) return;
      var id = inp.closest("tr").getAttribute("data-id"), v = parseInt(inp.value, 10);
      list.forEach(function (l) { if (l.id === id) l.q = isFinite(v) && v > 0 ? Math.min(9999, v) : 0; });
      totals();
    });
    body.addEventListener("change", function (e) {
      if (!e.target.closest("input")) return;
      list = list.filter(function (l) { return l.q > 0; });
      render();
    });
    body.addEventListener("click", function (e) {
      var b = e.target.closest(".mf-del"); if (!b) return;
      var id = b.closest("tr").getAttribute("data-id");
      list = list.filter(function (l) { return l.id !== id; });
      render();
      (sel || form).focus();
    });

    var render = function (flashId) {
      body.innerHTML = list.map(function (l) {
        var it = ITEMS[l.id];
        return '<tr data-id="' + l.id + '"' + (l.id === flashId ? ' class="new"' : "") + '>' +
          '<td class="nm">' + esc(it.n) + (it.note ? "<small>" + esc(it.note) + "</small>" : "") + "</td>" +
          '<td class="n q"><label class="sr" for="q-' + l.id + '">Quantity of ' + esc(it.n) + '</label><input id="q-' + l.id + '" type="number" min="0" max="9999" inputmode="numeric" value="' + l.q + '"></td>' +
          '<td class="n e">' + fmt(it.kg) + '&nbsp;kg<span class="m-each"> each</span></td>' +
          '<td class="n l"></td>' +
          '<td class="d"><button type="button" class="mf-del" aria-label="Remove ' + esc(it.n) + '">' + DEL + "</button></td></tr>";
      }).join("");
      table.hidden = list.length === 0;
      empty.hidden = list.length > 0;
      totals();
    };

    var totals = function () {
      var kg = 0, lines = 0, notes = [], what = [];
      list.forEach(function (l) {
        var it = ITEMS[l.id], k = it.kg * l.q;
        kg += k; if (l.q > 0) lines++;
        var cell = body.querySelector('tr[data-id="' + l.id + '"] .l');
        if (cell) cell.innerHTML = fmt(k) + "&nbsp;kg";
        if (l.q > 0) {
          what.push(it.n + " x " + l.q);
          if (it.note) notes.push("<li><b>" + esc(it.n) + ":</b> " + esc(it.note.charAt(0).toLowerCase() + it.note.slice(1)) + "</li>");
        }
      });
      var big = kg >= S.minKg;
      $("mf-t").textContent = kg >= 1000 ? fmt(kg / 1000, 1) : fmt(kg);
      $("mf-u").textContent = kg >= 1000 ? "tonnes" : "kg";
      $("mf-sub").innerHTML = lines ? fmt(kg) + "&nbsp;kg · " + lines + (lines === 1 ? " line" : " lines") : "No lines yet";
      var bar = $("mf-bar");
      bar.style.setProperty("--p", Math.min(100, kg / (3 * S.minKg) * 100) + "%");
      bar.parentNode.classList.toggle("over", big);
      var v = $("mf-verdict"), cta = $("mf-cta"), nl = $("mf-notes");
      nl.innerHTML = notes.join(""); nl.hidden = notes.length === 0;
      if (!lines) {
        v.innerHTML = "Collections start at one tonne. Add your items to see where you&nbsp;land.";
        cta.innerHTML = "";
      } else if (big) {
        v.innerHTML = "<b>Over the one-tonne minimum.</b>Send this list for a quote. One service fee, quoted before we&nbsp;come.";
        cta.innerHTML = '<a class="btn btn-white" href="quote.html?kg=' + Math.round(kg) + "&what=" + encodeURIComponent(what.join(", ")) + '#quote">Request a quote with this list</a>' +
          '<a class="btn btn-ghost" href="tel:' + S.phone + '">Call ' + esc(S.contact) + "</a>";
      } else {
        v.innerHTML = "<b>Under a tonne, for now.</b>Add anything else on site, or drop it off at 116 Furner Avenue. Clean scrap metal is no charge at the&nbsp;gate.";
        cta.innerHTML = '<a class="btn btn-white" href="drop-off.html">Drop-off details</a>';
      }
    };
    render();
  }

  /* ---- quote form: prefill from the estimator ---- */
  (function () {
    var f = document.querySelector('form.enq[data-subject="Collection quote request"]'); if (!f) return;
    try {
      var q = new URLSearchParams(location.search);
      if (q.get("what") && f.elements.what && !f.elements.what.value) f.elements.what.value = q.get("what").slice(0, 800);
      var kg = parseInt(q.get("kg"), 10);
      if (kg && f.elements.size) {
        var t = kg / 1000;
        f.elements.size.value = t < 1 ? "Not sure, photos attached" : t < 3 ? "1 to 3 tonnes" : t < 10 ? "3 to 10 tonnes" : "More than 10 tonnes";
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
