#!/usr/bin/env python3
"""Build the comparison page: concepts/index.html, with fresh screenshots of each concept.

Neutral on purpose: this page belongs to the review, not to any of the five concepts.
"""
import os, sys, json, html, datetime, threading, functools, http.server

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "common"))
import common as C  # noqa: E402

OUT = os.path.join(C.REPO, "concepts")
IMG = os.path.join(OUT, "img")

CONCEPTS = [
    {"id": "corio", "name": "Corio Metals", "dir": "", "dots": ["#111417", "#E38A45", "#F2EFE9"],
     "line": "Balanced. Drop-off and collections side by side, as two equal paths.",
     "look": "Industrial and dark, with Recycle Group copper. Condensed headlines, real yard photos.",
     "tool": "Load check: pick items by category for a rough weight, gate fees, and drop off or collect.",
     "best": "Both paths matter equally, and the brand should feel like a working yard.",
     "watch": "A Geelong place name. It may feel local when we collect in Melbourne and regional Victoria."},
    {"id": "drop", "name": "The Metal Drop", "dir": "the-metal-drop/", "dots": ["#FFFFFF", "#D52B1E", "#1B1D20"],
     "line": "Public first. The easiest place in Geelong to get rid of scrap metal, with business collections second.",
     "look": "Light and friendly, signal red, rounded type and a full set of item pictograms.",
     "tool": "Item checker: tap what you've got to see no charge, a fee or prep first, and whether to drop off or book a collection.",
     "best": "The order of the brief: a clear public drop-off, then a clear commercial path. The name says what it does.",
     "watch": "The name says drop, so business buyers rely on the Business collections page."},
    {"id": "tonne", "name": "Recycled Metals", "dir": "recycled-metals/", "dots": ["#0E0E0E", "#FFD200", "#FFFFFF"], "flag": "Richard's notes",
     "line": "Recycling metals since 1955. BTT, renamed and rebuilt on Richard's notes: free drop-off at any volume, four ways to move metal, and everything else by enquiry.",
     "look": "Black and white with safety yellow: the riveted yellow nameplate now reads RECYCLED METALS, with grey photos for every sector and a map from Werribee to Portland.",
     "tool": "Find out what you can drop off: 865 items across 20 categories with a drop-off column (free, or the gate fee), plus bin, boot, back of the ute or B-double.",
     "best": "Richard's direction. Drop-off free and clear for everyone, bins, an operator with excavator and grapple, and containers and boats taken away for the big jobs.",
     "watch": "Free drop-off sits beside five gate fees from the price list. Werribee already has a council tip that takes metal free, so the west and the coast are the stronger markets for bins."},
    {"id": "shed", "name": "Shedload", "dir": "shedload/", "dots": ["#2C2D2F", "#7C9177", "#EAE3D2"],
     "line": "Brand first. Shedload? Drop it off. Truckload? We'll collect.",
     "look": "Colorbond shed colours, stencil capitals, poster photos and labels like rubber stamps.",
     "tool": "Load scale: slide from a bucket to a full site and it tells you which way to go.",
     "best": "A memorable local brand for ads, signage and radio. The tagline explains the one-tonne line by itself.",
     "watch": "Shedload Pty Ltd is registered in Victoria (not in metal or waste). Casual tone for some council buyers."},
    {"id": "crux", "name": "Crux Metals", "dir": "crux-metals/", "dots": ["#1E1B19", "#8E3B26", "#EDE6DA"], "flag": "New",
     "line": "Richard's focus. His own lines and his directory of 766 items, under a new name with national reach: Crux is the Southern Cross.",
     "look": "Raw steel and red oxide primer: charcoal, red oxide and bone, heavy slab headings, an X made of two steel bars bolted like cross-bracing, and big real photos from Furner Avenue.",
     "tool": "Directory finder: search 766 items across 15 sectors, with Specialist items and gate fees flagged, beside how to get it to us.",
     "best": "Councils, institutions and big sites. It leads with credibility: the group's EPA registration, ISO certifications and YARTA reporting, and his three-beat lines.",
     "watch": "Crux needs a word of explanation for some people. A Castlemaine business already trades as Crux Forge (a forge, not scrap metal). No Crux on the NSW scrap metal register."},
]

SAME = [
    "Public drop-off at Recycle North Geelong, 116 Furner Avenue. Clean scrap metal is no charge: we don't pay for it, and you don't pay to leave it.",
    "Handling fees on a few items only: gas bottles, fire extinguishers, nitrous canisters, solar panels and tyres on rims, as on Recycle North Geelong's price list.",
    "A commercial path in every version: collections from one tonne in four of them, and bins and big jobs by enquiry in Recycled Metals.",
    "A weighbridge docket for every collected load. YARTA reporting in four versions; Richard's notes took it out of Recycled Metals.",
    "Rory Tonkin as the only contact: 0433 115 500. Enquiry forms open an email.",
    "The same can't-take list: asbestos, chemicals and hazardous waste, full or hired gas cylinders, firearms and explosives, clinical waste, anything holding fuel or oil.",
    "“A Recycle Group business” with the official Recycle mark near the logo and in every footer.",
    "The same address, hours, fees, can't-take list and contact from one shared source file, so the facts can't drift between versions.",
]

FEEDBACK = [
    ("No payment for metal", "Nothing about buying metal in any version: no rates, no payment details, no ID checks."),
    ("Two clear paths", "A public drop-off and commercial collections from one tonne."),
    ("One service fee, quoted first", "Every collection carries one service fee, quoted before we come. Checked automatically on every build."),
    ("Rory only", "One contact on every page, form and footer."),
    ("No em dashes", "Checked automatically on every build."),
    ("Easy, Aussie names", "Checked on the ABN register on 25 Oct."),
    ("Logos that say scrap metal", "A hook-lift bin, a hex nut, a riveted steel nameplate, a corrugated shed and two bolted steel bars. No sleek app marks."),
    ("Not pigeonholed", "Households, trades, business, farms, government and industry in every version."),
    ("Uniform images", "One photo treatment per site, captions that match the shot, nothing cropped awkwardly."),
    ("The tool on the home page", "Inputs above results on phones, results level with the inputs on desktop."),
    ("Real scale for one tonne", "Twenty steel filing cabinets, and more than an unbraked trailer may weigh."),
    ("Mobile and line breaks", "Every page checked at phone, tablet and desktop widths."),
    ("Recycle Group credit", "Near the logo and in every footer."),
    ("YARTA reporting", "On the commercial side of every version."),
    ("Batteries and data", "Batteries taken; drives removed or wiped before IT collections."),
    ("No pink, orange or blue", "Corio keeps the Recycle Group copper. Recycled Metals uses safety yellow, Crux uses red oxide."),
    ("Richard's notes, 26 Oct", "Recycled Metals: free drop-off at any volume, four ways to move metal, bin sizes, panels for a shed, a farm and a business, grey photo tiles, the town map. No \"we\", no tonne thresholds, no YARTA, checked on every build."),
    ("One link, big buttons", "All five live on the one link. Big buttons at the top of every page swap between them."),
]

CONFIRM = [
    "Gate times for the drop-off (sites say Monday to Saturday, call for gate times).",
    "That the metal drop-off runs through Recycle North Geelong's gate, and what the signage says.",
    "That no booking is needed to drop off from a car, ute or trailer.",
    "The fee items and amounts (taken from the price list as captured in June 2026).",
    "How non-metal parts of a load are charged (sites say the transfer station's usual rate).",
    "The collection minimum fee, the service area, and bin sizes.",
    "Whether a collection statement goes with each docket.",
    "The final name, domain and email address.",
    "For Recycled Metals: that drop-off stays free at any volume with the five gate fees still applying; bin sizes and pick-ups across every town on the map; how containers, boats and operator jobs are priced.",
    "For Crux Metals: showing the group's EPA registration and ISO certifications as its backing (both are on the Recycle Group site now).",
]


def shots():
    """Desktop and phone screenshots of each concept's home page, without the review bar."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    os.makedirs(IMG, exist_ok=True)

    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=C.REPO))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for c in CONCEPTS:
            for kind, vw, vh in (("desk", 1440, 900), ("phone", 390, 844)):
                ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2 if kind == "phone" else 1)
                ctx.add_init_script("try{sessionStorage.setItem('rv-hidden','1')}catch(e){}")
                pg = ctx.new_page()
                pg.goto(base + c["dir"], wait_until="networkidle")
                pg.add_style_tag(content=".rv-bar,.rv-tab,.rv-space{display:none!important}html{--rv:0px!important}")
                pg.wait_for_timeout(400)
                tmp = os.path.join(IMG, f"{c['id']}-{kind}.png")
                pg.screenshot(path=tmp)
                im = Image.open(tmp).convert("RGB")
                w = 1200 if kind == "desk" else 600
                im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
                im.save(tmp.replace(".png", ".webp"), quality=82)
                os.remove(tmp)
                ctx.close()
        b.close()
    srv.shutdown()


def page():
    esc = html.escape
    cards = ""
    for i, c in enumerate(CONCEPTS, 1):
        dots = "".join(f'<i style="background:{d}"></i>' for d in c["dots"])
        cards += f'''<article class="card" id="{c["id"]}">
  <div class="shots">
    <a class="desk" href="../{c["dir"]}" aria-label="Open {esc(c["name"])}"><img src="img/{c["id"]}-desk.webp" width="1200" height="750" alt="{esc(c["name"])} home page on a desktop screen" loading="lazy"></a>
    <a class="phone" href="../{c["dir"]}" tabindex="-1" aria-hidden="true"><img src="img/{c["id"]}-phone.webp" width="600" height="1298" alt="" loading="lazy"></a>
  </div>
  <div class="txt">
    <p class="num"><span>{i}</span><span class="dots" aria-hidden="true">{dots}</span>{f'<span class="flag">{esc(c["flag"])}</span>' if c.get("flag") else ""}</p>
    <h2>{esc(c["name"])}</h2>
    <p class="line">{esc(c["line"])}</p>
    <dl>
      <div><dt>Look</dt><dd>{esc(c["look"])}</dd></div>
      <div><dt>Home page tool</dt><dd>{esc(c["tool"])}</dd></div>
      <div><dt>Best if</dt><dd>{esc(c["best"])}</dd></div>
      <div><dt>Watch</dt><dd>{esc(c["watch"])}</dd></div>
    </dl>
    <a class="open" href="../{c["dir"]}">Open {esc(c["name"])} <span aria-hidden="true">&rarr;</span></a>
  </div>
</article>'''
    same = "".join(f"<li>{esc(x)}</li>" for x in SAME)
    fb = "".join(f"<li><b>{esc(a)}.</b> {esc(b)}</li>" for a, b in FEEDBACK)
    conf = "".join(f"<li>{esc(x)}</li>" for x in CONFIRM)
    today = datetime.date.today().strftime("%-d %B %Y")
    doc = f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Five concepts for approval | Scrap metal drop-off and collections</title>
<meta name="description" content="Five versions of the scrap metal site for 116 Furner Avenue, North Geelong: Corio Metals, The Metal Drop, Recycled Metals, Shedload and Crux Metals. Same offer, five different brands.">
<meta name="robots" content="noindex">
<link rel="icon" href="data:,">
{C.review_script(1)}
<style>
:root{{--ink:#16181B;--mute:#5C6066;--line:#DDDCD8;--bg:#F6F6F4;--card:#FFFFFF}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}}
img{{display:block;max-width:100%;height:auto}}
a{{color:inherit;text-underline-offset:3px}}
.wrap{{max-width:1240px;margin:0 auto;padding:0 28px}}
h1,h2,h3{{text-wrap:balance;letter-spacing:-.015em}}
p,li,dd{{text-wrap:pretty}}
header.top{{padding:56px 0 28px}}
.kick{{margin:0 0 10px;font-size:14px;font-weight:600;color:var(--mute);letter-spacing:.04em;text-transform:uppercase}}
h1{{margin:0 0 14px;font-size:clamp(34px,4.6vw,56px);line-height:1.05}}
.intro{{max-width:46em;font-size:19px;color:#33363A;margin:0}}
.pick{{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0 0;padding:0;list-style:none}}
.pick a{{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 14px;border:1px solid var(--line);border-radius:999px;background:#fff;text-decoration:none;font-weight:600;font-size:15px;white-space:nowrap}}
.pick a:hover{{border-color:var(--ink)}}
.pick i,.dots i{{display:inline-block;width:12px;height:12px;border-radius:50%;border:1px solid rgba(0,0,0,.25);margin-left:-3px}}
.pick i:first-child,.dots i:first-child{{margin-left:0}}
.rec{{margin:30px 0 0;padding:22px 24px;background:#fff;border:1px solid var(--line);border-left:5px solid var(--ink);border-radius:10px;max-width:60em}}
.rec h2{{margin:0 0 8px;font-size:20px}}
.rec p{{margin:0 0 8px}}
.rec p:last-child{{margin:0;color:var(--mute);font-size:15px}}
.rec b{{font-weight:700}}
.cards{{display:grid;gap:28px;padding:28px 0 20px}}
.card{{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:28px;align-items:start;padding:24px;background:var(--card);border:1px solid var(--line);border-radius:14px}}
.shots{{position:relative;padding:0 46px 40px 0}}
.shots .desk img{{border-radius:8px;border:1px solid var(--line);box-shadow:0 8px 24px rgba(0,0,0,.08)}}
.shots .phone{{position:absolute;right:0;bottom:0;width:26%;}}
.shots .phone img{{border-radius:16px;border:5px solid #1B1C1F;box-shadow:0 10px 26px rgba(0,0,0,.22);aspect-ratio:390/700;object-fit:cover;object-position:top}}
.txt{{min-width:0}}
.num{{display:flex;align-items:center;gap:10px;margin:0 0 6px;color:var(--mute);font-weight:700}}
.num span:first-child{{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--ink);color:#fff;font-size:14px}}
.flag{{margin-left:4px;padding:3px 9px;border-radius:999px;background:#EDEDEA;color:var(--ink);font-size:12px;font-weight:700;letter-spacing:.02em}}
.card h2{{margin:0 0 6px;font-size:clamp(26px,2.6vw,34px);line-height:1.1}}
.line{{margin:0 0 14px;font-size:18px;color:#33363A}}
dl{{margin:0 0 16px;border-top:1px solid var(--line)}}
dl > div{{display:grid;grid-template-columns:120px minmax(0,1fr);gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}}
dt{{font-weight:700;font-size:14px;color:var(--mute);padding-top:2px}}
dd{{margin:0;font-size:15.5px}}
.open{{display:inline-flex;align-items:center;gap:8px;height:46px;padding:0 18px;border-radius:8px;background:var(--ink);color:#fff;text-decoration:none;font-weight:700;white-space:nowrap}}
.open:hover{{background:#000}}
.cols{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;padding:20px 0 64px}}
.box{{padding:22px 22px 10px;background:#fff;border:1px solid var(--line);border-radius:14px}}
.box h3{{margin:0 0 10px;font-size:20px}}
.box ul{{margin:0;padding:0 0 0 18px}}
.box li{{margin:0 0 10px;font-size:15.5px}}
footer{{padding:28px 0 48px;color:var(--mute);font-size:14px;border-top:1px solid var(--line)}}
@media (max-width:980px){{.card{{grid-template-columns:1fr}}.cols{{grid-template-columns:1fr}}}}
@media (max-width:560px){{.wrap{{padding:0 16px}}.card{{padding:16px}}.shots{{padding:0 30px 34px 0}}dl > div{{grid-template-columns:1fr;gap:2px}}}}
</style>
</head>
<body data-concept="compare" data-page="home">
<header class="top"><div class="wrap">
  <p class="kick">For approval · {today}</p>
  <h1>One offer, five versions.</h1>
  <p class="intro">Five versions of the scrap metal site for 116 Furner Avenue, North Geelong. Each one has a clear public drop-off and a commercial path, and none of them pays for metal. They differ in name, look, which path leads, and the tool on the home page. Tap the big buttons at the top of any page to swap between them; you stay on the matching&nbsp;page.</p>
  <ul class="pick">{"".join(f'<li><a href="#{c["id"]}"><span class="dots">{"".join(f"<i style=background:{d}></i>" for d in c["dots"])}</span>{esc(c["name"])}</a></li>' for c in CONCEPTS)}</ul>
  <div class="rec">
    <h2>The lead: Recycled Metals</h2>
    <p><b>Richard's notes, built: Recycled Metals, recycling metals since 1955.</b> Free drop-off at any volume, four ways to move metal, the 865-item list with a drop-off column, and a map of the towns&nbsp;covered.</p>
    <p><b>For the public first: The Metal Drop.</b> The name says exactly what it does for signage and Google, and its item checker answers the question people ask before they load&nbsp;up.</p>
    <p>Crux Metals for a new national name. Shedload for the most memorable ads and signs, after a check on Shedload Pty&nbsp;Ltd.</p>
  </div>
</div></header>
<main class="wrap">
  <section class="cards" aria-label="The five concepts">{cards}</section>
  <section class="cols">
    <div class="box"><h3>The same in all five</h3><ul>{same}</ul></div>
    <div class="box"><h3>Your feedback, applied</h3><ul>{fb}</ul></div>
    <div class="box"><h3>Needs confirming before launch</h3><ul>{conf}</ul></div>
  </section>
</main>
<footer><div class="wrap">Review page for the five concepts. Not part of any brand. Contact for all five: {C.CONTACT_FULL}, {C.PHONE}.</div></footer>
</body>
</html>
'''
    C.check(doc, "concepts/index.html", allow_free=True)
    open(os.path.join(OUT, "index.html"), "w").write(C.glue(doc))


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--no-shots" not in sys.argv:
        shots()
    page()
    print("concepts page built")


if __name__ == "__main__":
    main()
