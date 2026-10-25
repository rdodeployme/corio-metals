/* Shedload site behaviour. Settings from window.SL; the load scale from window.SL_LOADS. */
(function () {
  "use strict";
  var S = window.SL || { phone: "0427888222", minKg: 1000, maps: "#", contact: "Nigel" };

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
    window.addEventListener("resize", function () { if (window.innerWidth > 1100 && nav.classList.contains("open")) setMenu(false); });
  }

  /* ---- load scale: slide from a bucket to a full site, see which way to go ---- */
  var ui = document.getElementById("scale-ui"), L = window.SL_LOADS || [];
  if (ui && L.length) {
    var r = document.getElementById("sc-r");
    var stops = [].slice.call(ui.querySelectorAll(".sc-stops button"));
    var $ = function (id) { return document.getElementById(id); };
    // the 1 tonne marker sits between the last drop-off load and the first collection load
    var first = 0; while (first < L.length && L[first].kg < S.minKg) first++;
    var mark = ui.querySelector(".sc-1t");
    if (mark) mark.style.setProperty("--t1", ((first - 0.5) / (L.length - 1)).toFixed(4));

    var show = function (i) {
      var d = L[i], big = d.kg >= S.minKg;
      r.value = i;
      r.setAttribute("aria-valuetext", d.n + ", " + d.lab.toLowerCase());
      stops.forEach(function (b, j) { b.setAttribute("aria-pressed", j === i ? "true" : "false"); });
      $("sc-name").textContent = d.n;
      $("sc-kg").textContent = d.lab;
      $("sc-eg").textContent = d.eg;
      if (big) {
        $("sc-verdict").innerHTML = '<span class="stamp">We’ll collect</span><p>A tonne or more. We bring the truck and the crew, quote one service fee before we come, and weigh every load on our weighbridge.</p>';
        $("sc-cta").innerHTML = '<a class="btn btn-euc" href="collect.html#quote">Get a quote</a><a class="btn btn-mon" href="tel:' + S.phone + '">Call ' + S.contact + "</a>";
      } else {
        $("sc-verdict").innerHTML = '<span class="stamp">Drop it off</span><p>Under a tonne. Bring it to 116 Furner Avenue, North Geelong. Clean scrap metal is no charge, and you unload under cover.</p>';
        $("sc-cta").innerHTML = '<a class="btn btn-euc" href="' + S.maps + '" target="_blank" rel="noopener">Directions</a><a class="btn btn-mon" href="drop-off.html">Drop-off details</a>';
      }
    };
    r.addEventListener("input", function () { show(parseInt(r.value, 10) || 0); });
    stops.forEach(function (b) { b.addEventListener("click", function () { show(parseInt(b.getAttribute("data-i"), 10)); }); });
    show(parseInt(r.value, 10) || 0);
  }

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
