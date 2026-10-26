/* Recycled Metals site behaviour: menu, the home page finder ("Find out what you can drop off",
   window.RM_DIR), the directory search on items.html, and the enquiry form that opens a pre-filled email. */
(function () {
  "use strict";
  var S = window.RM || { phone: "0427888222", contact: "Nigel" };

  /* shorter search placeholders on phones, so they aren't cut off */
  if (window.matchMedia && window.matchMedia("(max-width: 560px)").matches) {
    [].forEach.call(document.querySelectorAll("input[data-short]"), function (el) { el.placeholder = el.getAttribute("data-short"); });
  }

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

  /* ---- search helpers (same matching as the Recycle Group directory) ---- */
  function norm(s) { return (s || "").toLowerCase().replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim(); }
  var SYN = { "fridge": ["refrigerat", "fridge"], "fridges": ["refrigerat", "fridge"], "aircon": ["air condition"], "air con": ["air condition"], "ac": ["air condition"],
    "washer": ["washing machine", "dishwasher", "glasswasher"], "xray": ["x ray"], "guard rail": ["guardrail"], "computer": ["computer", "laptop"], "laptop": ["computer", "laptop"],
    "cable": ["cable", "wire", "wiring"], "wire": ["wire", "cable"], "stove": ["stove", "oven", "cooktop"], "oven": ["oven", "stove"], "trolley": ["trolley", "cart"],
    "car": ["car ", "cars", "vehicle"], "ute": ["utility vehicle"], "heater": ["hot water", "heater"], "bbq": ["bbq", "barbecue"], "barbeque": ["bbq", "barbecue"],
    "gas bottle": ["gas bottle", "lpg"], "battery": ["batter"], "batteries": ["batter"], "tv": ["television", "tv "], "bike": ["bicycle", "bike"], "bicycle": ["bicycle", "bike"],
    "fence": ["fenc"], "fencing": ["fenc"], "shelf": ["shelv"], "shelves": ["shelv"], "racks": ["rack"], "container": ["container"], "boat": ["boat", "trailer"] };
  function terms(q) { var t = [q]; if (SYN[q]) t = t.concat(SYN[q]); if (q.length > 3 && q.slice(-1) === "s") t.push(q.slice(0, -1)); return t; }
  function hit(tx, w) { return w.length < 5 ? (" " + tx).indexOf(" " + w) > -1 : tx.indexOf(w) > -1; }
  /* a phrase matches if the whole phrase (or a synonym) is there, or failing that, every word is */
  function matcher(q) {
    var whole = terms(q), words = q.split(" ").filter(function (w) { return w.length > 1; }).map(terms);
    return function (tx) {
      if (whole.some(function (w) { return hit(tx, w); })) return true;
      return words.length > 1 && words.every(function (ts) { return ts.some(function (w) { return hit(tx, w); }); });
    };
  }
  var CANT = /(^| )(asbestos|chemicals?|hazardous|firearms?|guns?|ammunition|ammo|explosives?|clinical|sharps|needles?|syringes?|radioactive|pesticides?|poisons?)( |$)/;
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var phone = S.phone.replace(/(\d{4})(\d{3})(\d{3})/, "$1&nbsp;$2&nbsp;$3");

  /* ---- home page finder ---- */
  var ui = document.getElementById("finder-ui"), D = window.RM_DIR;
  if (ui && D) {
    var qEl = document.getElementById("f-q"), out = document.getElementById("f-out"), count = document.getElementById("f-count"), clear = document.getElementById("f-clear");
    var chips = [].slice.call(ui.querySelectorAll("[data-cat]"));
    var cat = -1, LIMIT = 10;
    var SHORTS = chips.map(function (c) { return c.textContent; });
    var norms = D.items.map(function (it) { return norm(it[1] + " " + it[2]); });
    var row = function (it, q) {
      var name = esc(it[1]);
      if (q) { var i = it[1].toLowerCase().indexOf(q); if (i > -1) name = esc(it[1].slice(0, i)) + "<mark>" + esc(it[1].slice(i, i + q.length)) + "</mark>" + esc(it[1].slice(i + q.length)); }
      return "<li><div class=\"nm\">" + name + (it[2] ? "<small>" + esc(it[2].charAt(0).toUpperCase() + it[2].slice(1)) + "</small>" : "") +
        "<span class=\"meta\"><span class=\"cat\">" + esc(SHORTS[it[0]]) + "</span>" + (it[3] ? "<span class=\"tag\">Specialist</span>" : "") + "</span></div>" +
        (it[4] ? "<span class=\"pr paid\">" + esc(D.fees[it[4]]) + "</span>" : "<span class=\"pr\">Free</span>") + "</li>";
    };
    var render = function () {
      var q = norm(qEl.value);
      chips.forEach(function (c, i) { c.setAttribute("aria-pressed", i === cat ? "true" : "false"); });
      clear.hidden = !q && cat < 0;
      if (q && CANT.test(q)) {
        count.textContent = "Not accepted";
        out.innerHTML = "<div class=\"f-none no\"><b>Not accepted.</b><p>Asbestos, chemicals and hazardous waste, full or hired gas cylinders, firearms and explosives, clinical waste and radioactive material can't come in. " +
          "<a href=\"items.html#cant\">See the full list</a>.</p></div>";
        return;
      }
      if (!q && cat < 0) {
        count.textContent = D.items.length + " items across " + D.cats.length + " categories";
        out.innerHTML = "<div class=\"cats\">" + D.cats.map(function (c, i) {
          return "<a href=\"items.html#" + c.id + "\" data-pick=\"" + i + "\"><i>" + c.n + "</i><b>" + esc(c.t) + "</b><em>" + c.c + "</em></a>";
        }).join("") + "</div>";
        return;
      }
      var mt = matcher(q), m = [];
      D.items.forEach(function (it, i) {
        if (cat > -1 && it[0] !== cat) return;
        if (!q || mt(norms[i])) m.push(it);
      });
      var where = cat > -1 ? " in " + SHORTS[cat] : "";
      count.textContent = q ? m.length + (m.length === 1 ? " match" : " matches") + where : m.length + " items" + where;
      if (!m.length) {
        out.innerHTML = "<div class=\"f-none\"><b>Not on the list yet.</b><p>If it's mostly metal, it can most likely come in. Call " + esc(S.contact) +
          " on <a href=\"tel:" + S.phone + "\">" + phone + "</a> or <a href=\"enquire.html\">send an enquiry</a>.</p></div>";
        return;
      }
      var more = "";
      if (m.length > LIMIT) {
        var href = q ? "items.html?q=" + encodeURIComponent(qEl.value.trim()) + "#list" : "items.html#" + D.cats[cat].id;
        more = "<p class=\"f-more\"><a class=\"tlink\" href=\"" + href + "\">See all " + m.length + "</a></p>";
      }
      out.innerHTML = "<div class=\"f-head\" aria-hidden=\"true\"><span>Item</span><span>Drop-off</span></div><ul class=\"f-list\">" +
        m.slice(0, LIMIT).map(function (it) { return row(it, q); }).join("") + "</ul>" + more;
    };
    qEl.addEventListener("input", render);
    chips.forEach(function (c, i) { c.addEventListener("click", function () { cat = cat === i ? -1 : i; render(); }); });
    out.addEventListener("click", function (e) {
      var b = e.target.closest("[data-pick]"); if (!b) return;
      e.preventDefault();
      cat = parseInt(b.getAttribute("data-pick"), 10); render();
      chips[cat].focus();
    });
    clear.addEventListener("click", function () { qEl.value = ""; cat = -1; render(); qEl.focus(); });
    render();
  }

  /* ---- directory page search ---- */
  var dq = document.getElementById("dir-q");
  if (dq) {
    var cats = [].slice.call(document.querySelectorAll("#dir details"));
    var dcount = document.getElementById("dir-count"), dempty = document.getElementById("dir-empty"), dcant = document.getElementById("dir-cant");
    var total = document.querySelectorAll("#dir li").length;
    var run = function () {
      var q = norm(dq.value), hits = 0, mt = matcher(q), isCant = !!q && CANT.test(q);
      cats.forEach(function (c) {
        var title = norm(c.querySelector(".t b").textContent), n = 0;
        [].forEach.call(c.querySelectorAll("li"), function (li) {
          var tx = norm(li.querySelector(".nm").textContent);
          var on = !q || (!isCant && (title.indexOf(q) > -1 || mt(tx)));
          li.hidden = !on; li.classList.toggle("hit", !!q && on); if (on) n++;
        });
        c.hidden = !!q && n === 0; if (q) c.open = n > 0; hits += n;
      });
      dcount.textContent = q ? (isCant ? "Not accepted" : hits + " of " + total + " items match") : total + " items across " + cats.length + " categories";
      dempty.hidden = !(q && hits === 0 && !isCant);
      dcant.hidden = !isCant;
    };
    dq.addEventListener("input", run);
    var openHash = function () {
      var id = (location.hash || "").slice(1); if (!id) return;
      var el = document.getElementById(id);
      if (el && el.tagName === "DETAILS") { el.open = true; setTimeout(function () { el.scrollIntoView({ block: "start" }); }, 60); }
    };
    window.addEventListener("hashchange", openHash);
    try { var q0 = new URLSearchParams(location.search).get("q"); if (q0) dq.value = q0; } catch (e) {}
    openHash(); run();
  }

  /* ---- enquiry form opens a pre-filled email ---- */
  document.querySelectorAll("form.enq").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var get = function (n) { var x = f.elements[n]; return x ? x.value.trim() : ""; };
      var subject = (f.getAttribute("data-subject") || "Enquiry") + (get("org") ? " · " + get("org") : get("site") ? " · " + get("site") : "");
      var lines = [];
      Array.prototype.forEach.call(f.elements, function (x) {
        if (!x.name || !x.value || !x.value.trim() || x.type === "submit") return;
        lines.push((x.getAttribute("data-label") || x.name) + ": " + x.value.trim());
      });
      var done = f.querySelector(".form-done"); if (done) done.hidden = false;
      window.location.href = "mailto:" + f.getAttribute("data-to") + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
    });
  });
})();
