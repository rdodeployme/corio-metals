/* Concept switcher: a review bar at the top of every page of every concept.
   Swaps to the matching page in another concept. Not part of any brand. */
(function () {
  "use strict";
  var me = document.currentScript;
  var base = me ? me.src.replace(/review\/switcher\.js.*$/, "") : "/";
  var C = [
    { id: "corio", name: "Corio Metals", dir: "", line: "Balanced: drop-off and collections side by side",
      dots: ["#111417", "#E38A45", "#F2EFE9"],
      pages: { home: "index.html", dropoff: "drop-off.html", collect: "collections.html", take: "what-we-take.html", contact: "contact.html", load: "load-check.html" } },
    { id: "drop", name: "The Metal Drop", dir: "the-metal-drop/", line: "Public first: an item checker and a dead-easy drop-off",
      dots: ["#FFFFFF", "#D52B1E", "#1B1D20"],
      pages: { home: "index.html", dropoff: "drop-off.html", collect: "business.html", take: "what-we-take.html", contact: "faq.html", load: "what-we-take.html" } },
    { id: "tonne", name: "BTT By The Tonne", dir: "by-the-tonne/", line: "Commercial first: collections from one tonne, every tonne on the record",
      dots: ["#0E0E0E", "#FFD200", "#FFFFFF"],
      pages: { home: "index.html", dropoff: "drop-off.html", collect: "services.html", take: "what-we-collect.html", contact: "quote.html", load: "index.html#estimate", report: "reporting.html" } },
    { id: "shed", name: "Shedload", dir: "shedload/", line: "Brand first: Shedload? Drop it off. Truckload? We'll collect.",
      dots: ["#2C2D2F", "#7C9177", "#EAE3D2"],
      pages: { home: "index.html", dropoff: "drop-off.html", collect: "collect.html", take: "what-we-take.html", contact: "find-us.html", load: "index.html#scale" } },
    { id: "rgm", name: "Recycle Group Metals", dir: "recycle-group-metals/", line: "Master brand: the group's own name, facility and credentials, with Richard's directory",
      dots: ["#0E1114", "#C2804F", "#ECEFF1"],
      pages: { home: "index.html", dropoff: "drop-off.html", collect: "collections.html", take: "what-we-collect.html", contact: "contact.html", load: "index.html#finder", report: "reporting.html" } }
  ];
  var body = document.body;
  var cur = body.getAttribute("data-concept") || "corio";
  var page = body.getAttribute("data-page") || "home";
  var idx = -1;
  C.forEach(function (c, i) { if (c.id === cur) idx = i; });
  var onCompare = idx < 0;
  function hrefFor(c) {
    var p = c.pages[page] || c.pages.home;
    return base + c.dir + (p === "index.html" ? "" : p);
  }
  var hidden = false;
  try { hidden = sessionStorage.getItem("rv-hidden") === "1"; } catch (e) {}

  var bar = document.createElement("div");
  bar.className = "rv-bar";
  bar.setAttribute("role", "region");
  bar.setAttribute("aria-label", "Concept switcher");
  var prev = onCompare ? C[C.length - 1] : C[(idx + C.length - 1) % C.length], next = onCompare ? C[0] : C[(idx + 1) % C.length];
  var dots = function (c) { return '<span class="rv-dots" aria-hidden="true">' + c.dots.map(function (d) { return '<i style="background:' + d + '"></i>'; }).join("") + "</span>"; };
  bar.innerHTML =
    '<div class="rv-in">' +
      '<span class="rv-label">Concepts for approval</span>' +
      '<a class="rv-arrow" href="' + hrefFor(prev) + '" aria-label="Previous concept: ' + prev.name + '">&#8592;</a>' +
      '<button class="rv-btn" type="button" aria-expanded="false" aria-controls="rv-menu">' +
        (onCompare ? '<b>Compare all five</b>' :
        '<span class="rv-n">' + (idx + 1) + ' of ' + C.length + '</span>' + dots(C[idx]) + '<b>' + C[idx].name + '</b>') +
        '<span class="rv-caret" aria-hidden="true">&#9662;</span>' +
      '</button>' +
      '<a class="rv-arrow" href="' + hrefFor(next) + '" aria-label="Next concept: ' + next.name + '">&#8594;</a>' +
      (onCompare ? '<span class="rv-all"></span>' : '<a class="rv-all" href="' + base + 'concepts/">Compare all 5</a>') +
      '<button class="rv-hide" type="button" aria-label="Hide the concept bar">Hide</button>' +
    '</div>' +
    '<div class="rv-menu" id="rv-menu" hidden><ol>' +
      C.map(function (c, i) {
        return '<li><a href="' + hrefFor(c) + '"' + (i === idx ? ' aria-current="true"' : "") + '>' +
          '<span class="rv-num">' + (i + 1) + '</span>' + dots(c) +
          '<span class="rv-txt"><b>' + c.name + '</b><small>' + c.line + '</small></span></a></li>';
      }).join("") +
      '<li class="rv-cmp"><a href="' + base + 'concepts/"' + (onCompare ? ' aria-current="true"' : '') + '><span class="rv-txt"><b>Compare all five side by side</b><small>What each one is for, and what is the same in all of them</small></span></a></li>' +
    '</ol></div>';
  var tab = document.createElement("button");
  tab.className = "rv-tab"; tab.type = "button";
  tab.innerHTML = "Concepts &#9662;";
  tab.setAttribute("aria-label", "Show the concept bar");
  var spacer = document.createElement("div");
  spacer.className = "rv-space";
  body.insertBefore(spacer, body.firstChild);
  body.insertBefore(bar, body.firstChild);
  body.appendChild(tab);

  function setHidden(h) {
    hidden = h;
    document.documentElement.classList.toggle("rv-hidden", h);
    try { sessionStorage.setItem("rv-hidden", h ? "1" : "0"); } catch (e) {}
  }
  setHidden(hidden);
  document.documentElement.classList.add("rv-on");

  var btn = bar.querySelector(".rv-btn"), menu = bar.querySelector(".rv-menu");
  function open(o) { menu.hidden = !o; btn.setAttribute("aria-expanded", o ? "true" : "false"); }
  btn.addEventListener("click", function () { open(menu.hidden); });
  document.addEventListener("click", function (e) { if (!bar.contains(e.target)) open(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") open(false); });
  bar.querySelector(".rv-hide").addEventListener("click", function () { open(false); setHidden(true); });
  tab.addEventListener("click", function () { setHidden(false); });
})();
