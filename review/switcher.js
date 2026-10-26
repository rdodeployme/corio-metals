/* Version switcher: a bar of big buttons at the top of every page of every concept.
   One button per version. Tapping one opens the matching page in that version
   (drop-off to drop-off, collections to collections). Not part of any brand. */
(function () {
  "use strict";
  var me = document.currentScript;
  var base = me ? me.src.replace(/review\/switcher\.js.*$/, "") : "/";
  var C = [
    { id: "corio", name: "Corio Metals", short: "Corio", dir: "", line: "Balanced: drop-off and collections side by side",
      dots: ["#111417", "#E38A45", "#F2EFE9"],
      pages: { home: "index.html", dropoff: "drop-off.html", collect: "collections.html", take: "what-we-take.html", contact: "contact.html", load: "load-check.html" } },
    { id: "drop", name: "The Metal Drop", short: "Metal Drop", dir: "the-metal-drop/", line: "Public first: an item checker and a dead-easy drop-off",
      dots: ["#FFFFFF", "#D52B1E", "#1B1D20"],
      pages: { home: "index.html", dropoff: "drop-off.html", collect: "business.html", take: "what-we-take.html", contact: "faq.html", load: "what-we-take.html" } },
    { id: "tonne", name: "Recycled Metals", short: "Recycled", dir: "recycled-metals/", line: "By the tonne: drop-off at any volume, bins and big jobs by enquiry",
      dots: ["#0E0E0E", "#FFD200", "#FFFFFF"],
      pages: { home: "index.html", dropoff: "drop-off.html", collect: "bins-and-collections.html", take: "items.html", contact: "enquire.html", load: "index.html#sizes", report: "bins-and-collections.html" } },
    { id: "shed", name: "Shedload", short: "Shedload", dir: "shedload/", line: "Brand first: Shedload? Drop it off. Truckload? We'll collect.",
      dots: ["#2C2D2F", "#7C9177", "#EAE3D2"],
      pages: { home: "index.html", dropoff: "drop-off.html", collect: "collect.html", take: "what-we-take.html", contact: "find-us.html", load: "index.html#scale" } },
    { id: "crux", name: "Crux Metals", short: "Crux", dir: "crux-metals/", line: "Richard's focus: his lines, his 766-item directory, the group's credentials",
      dots: ["#1E1B19", "#8E3B26", "#EDE6DA"],
      pages: { home: "index.html", dropoff: "drop-off.html", collect: "collections.html", take: "what-we-collect.html", contact: "contact.html", load: "index.html#finder", report: "reporting.html" } }
  ];
  var body = document.body;
  var cur = body.getAttribute("data-concept") || "corio";
  var page = body.getAttribute("data-page") || "home";
  var onCompare = cur === "compare";
  function hrefFor(c) {
    var p = c.pages[page] || c.pages.home;
    return base + c.dir + (p === "index.html" ? "" : p);
  }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (ch) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]; }); }
  var hidden = false;
  try { hidden = sessionStorage.getItem("rv-hidden") === "1"; } catch (e) {}

  var bar = document.createElement("div");
  bar.className = "rv-bar";
  bar.setAttribute("role", "navigation");
  bar.setAttribute("aria-label", "Versions for approval");
  var dots = function (c) { return '<span class="rv-dots" aria-hidden="true">' + c.dots.map(function (d) { return '<i style="background:' + d + '"></i>'; }).join("") + "</span>"; };
  bar.innerHTML =
    '<div class="rv-in">' +
      '<span class="rv-label">Versions<br><small>for approval</small></span>' +
      '<div class="rv-row">' +
        C.map(function (c, i) {
          var on = c.id === cur;
          return '<a class="rv-v' + (on ? " on" : "") + '" href="' + hrefFor(c) + '"' + (on ? ' aria-current="page"' : "") +
            ' title="' + esc(c.name + ": " + c.line) + '">' +
            '<span class="rv-n">' + (i + 1) + '</span>' + dots(c) +
            '<span class="rv-name"><span class="rv-long">' + esc(c.name) + '</span><span class="rv-short">' + esc(c.short) + '</span></span></a>';
        }).join("") +
        '<a class="rv-v rv-cmp' + (onCompare ? " on" : "") + '" href="' + base + 'concepts/"' + (onCompare ? ' aria-current="page"' : "") + '>' +
          '<span class="rv-name"><span class="rv-long">Compare all</span><span class="rv-short">Compare</span></span></a>' +
      '</div>' +
      '<button class="rv-hide" type="button" aria-label="Hide the version buttons"><span aria-hidden="true">&times;</span></button>' +
    '</div>';
  var tab = document.createElement("button");
  tab.className = "rv-tab"; tab.type = "button";
  tab.textContent = "Show versions";
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

  /* on phones the row scrolls sideways: bring the current version into view */
  var row = bar.querySelector(".rv-row"), on = bar.querySelector(".rv-v.on");
  function edges() {
    var max = row.scrollWidth - row.clientWidth;
    row.classList.toggle("fl", max > 2 && row.scrollLeft > 2);
    row.classList.toggle("fr", max > 2 && row.scrollLeft < max - 2);
  }
  if (row) {
    if (on && row.scrollWidth > row.clientWidth) {
      row.scrollLeft = Math.max(0, on.offsetLeft - (row.clientWidth - on.offsetWidth) / 2);
    }
    edges();
    row.addEventListener("scroll", edges, { passive: true });
    window.addEventListener("resize", edges);
  }
  bar.querySelector(".rv-hide").addEventListener("click", function () { setHidden(true); });
  tab.addEventListener("click", function () { setHidden(false); });
})();
