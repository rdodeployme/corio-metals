#!/usr/bin/env python3
"""Build BTT By The Tonne (concept 3): commercial first. Collections from one tonne, every tonne on the record.

Output: by-the-tonne/ in the repo.
"""
import json, os, re, shutil, datetime, hashlib, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "common"))
import common as C  # noqa: E402

SRC = os.path.join(ROOT, "src")
SITE = os.path.join(C.REPO, "by-the-tonne")
DEPTH = 1
NAME = "BTT By The Tonne"
SHORT = "BTT"
SITE_URL = C.SITE_BASE + "by-the-tonne/"

NAV = [("collect", "services.html", "Services"), ("take", "what-we-collect.html", "What we collect"),
       ("report", "reporting.html", "Reporting"), ("dropoff", "drop-off.html", "Drop-off")]
PAGE_KEY = {"index.html": "home", "services.html": "collect", "what-we-collect.html": "take",
            "reporting.html": "report", "drop-off.html": "dropoff", "quote.html": "contact"}

ITEMS = {it[0]: it for it in C.ITEMS}
# The estimator lists what businesses, sites and depots usually have (guide weights from common.py)
MANIFEST = [
    ("Office and fit-out", ["filing", "locker", "desk", "shelving", "server"]),
    ("Warehouse and logistics", ["racking", "cage"]),
    ("Building and demolition", ["offcuts", "mesh", "roofing", "pickets", "fence", "gutter", "window"]),
    ("Workshop and plant", ["motor", "bench", "cable", "copper"]),
    ("Vehicles and machinery", ["engine", "rims", "radiator", "car"]),
    ("Whitegoods in bulk", ["fridge", "washer", "oven", "hws"]),
]
NOTES = {"server": "Drives removed or wiped first.", "engine": "Fuel and oil drained.", "car": "Call first.",
         "hws": "Drained.", "window": "Glass out if you can.", "solar": "Quoted separately."}
EXAMPLES = {
    "office": ("Office strip-out", {"filing": 12, "locker": 8, "desk": 20, "shelving": 10, "server": 2}),
    "warehouse": ("Warehouse refit", {"racking": 40, "cage": 12}),
    "site": ("Site clean-up", {"offcuts": 10, "mesh": 8, "roofing": 40, "pickets": 5}),
}

ARROW = '<svg class="arr" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 10h13M11 5l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
CHECK = '<svg class="tk" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
CROSS = '<svg class="tk" viewBox="0 0 20 20" aria-hidden="true"><path d="M5 5l10 10M15 5L5 15" fill="none" stroke="currentColor" stroke-width="2"/></svg>'


def _ver():
    h = hashlib.sha1()
    for f in (os.path.join(SRC, "css", "main.css"), os.path.join(SRC, "js", "main.js")):
        h.update(open(f, "rb").read())
    return h.hexdigest()[:8]


VER = _ver()


# ---------------------------------------------------------------- components
def manifest():
    groups = ""
    data = {}
    for g, ids in MANIFEST:
        opts = ""
        for i in ids:
            iid, name, grp, kg, st, note, ic = ITEMS[i]
            data[iid] = {"n": name, "kg": kg, "note": NOTES.get(iid, "")}
            opts += f'<option value="{iid}">{C.esc(name)} · {kg:,}&nbsp;kg</option>'
        groups += f'<optgroup label="{C.esc(g)}">{opts}</optgroup>'
    eg = "".join(f'<button type="button" data-eg="{k}">{v[0]}</button>' for k, v in EXAMPLES.items())
    egdata = {k: v[1] for k, v in EXAMPLES.items()}
    return f'''<div class="mf" id="mf">
  <div class="mf-main">
    <form class="mf-add" id="mf-add">
      <div class="mf-f mf-item"><label for="mf-item">Item</label><select id="mf-item">{groups}</select></div>
      <div class="mf-f mf-qty"><label for="mf-qty">Quantity</label><input id="mf-qty" type="number" min="1" max="9999" value="1" inputmode="numeric"></div>
      <button class="btn btn-black mf-go" type="submit">Add to list</button>
    </form>
    <div class="mf-eg"><span class="label">Or load an example</span>{eg}</div>
    <table class="mf-table" id="mf-table" hidden>
      <thead><tr><th scope="col">Item</th><th scope="col" class="n">Qty</th><th scope="col" class="n">Guide each</th><th scope="col" class="n">Line total</th><th scope="col"><span class="sr">Remove</span></th></tr></thead>
      <tbody id="mf-body"></tbody>
    </table>
    <p class="mf-empty" id="mf-empty">Your list is empty. Add what's on site, line by line, and the total builds as you&nbsp;go.</p>
  </div>
  <aside class="mf-out" aria-label="Estimate">
    <div class="mf-out-in" id="mf-out" aria-live="polite">
      <p class="label">Estimated total</p>
      <div class="mf-total"><span id="mf-t">0</span><small id="mf-u">kg</small></div>
      <p class="mf-sub mono" id="mf-sub">No lines yet</p>
      <div class="mf-scale" aria-hidden="true"><i id="mf-bar"></i><span class="mk">1&nbsp;t minimum</span></div>
      <div class="mf-scale-l mono" aria-hidden="true"><span>0</span><span>1&nbsp;t</span><span>3&nbsp;t+</span></div>
      <p class="mf-verdict" id="mf-verdict">Collections start at one tonne. Add your items to see where you&nbsp;land.</p>
      <ul class="mf-notes" id="mf-notes" hidden></ul>
      <div class="mf-cta" id="mf-cta"></div>
      <p class="mf-fine">Guide weights only. Your docket shows the weighed&nbsp;tonnage.</p>
    </div>
  </aside>
</div>
<script>window.BTT_ITEMS={json.dumps(data, separators=(",", ":"))};window.BTT_EG={json.dumps(egdata, separators=(",", ":"))};</script>'''


def docket(big=False):
    return f'''<figure class="docket{" big" if big else ""}">
  <div class="dk" role="img" aria-label="Sample weighbridge docket: date, customer, site, material, then gross, tare and net weight">
    <div class="dk-head"><img src="assets/brand/logo-light.svg" alt="" width="173" height="34"><span>Weighbridge docket</span></div>
    <dl class="dk-rows">
      <div><dt>Docket</dt><dd>No. 000000</dd></div>
      <div><dt>Date</dt><dd>DD / MM / YYYY</dd></div>
      <div><dt>Customer</dt><dd>Your business</dd></div>
      <div><dt>Site</dt><dd>Your site, VIC</dd></div>
      <div><dt>Material</dt><dd>Mixed steel</dd></div>
    </dl>
    <dl class="dk-w">
      <div><dt>Gross</dt><dd>16,240&nbsp;kg</dd></div>
      <div><dt>Tare</dt><dd>10,980&nbsp;kg</dd></div>
      <div class="net"><dt>Net</dt><dd>5,260&nbsp;kg</dd></div>
    </dl>
    <p class="dk-foot">Environmental reporting through YARTA</p>
    <span class="dk-stamp" aria-hidden="true">Sample</span>
  </div>
  <figcaption>Sample layout, for illustration only. Your docket shows your load's weighed&nbsp;figures.</figcaption>
</figure>'''


def gate_guide():
    free = "".join(f'<tr><td class="it"><b>{a}</b><small>{b}</small></td><td class="v">No charge</td></tr>' for a, b in C.GATE_NO_CHARGE)
    fees = "".join(f'<tr><td class="it"><b>{a}</b>{f"<small>{c}</small>" if c else ""}</td><td class="v">{b}</td></tr>' for a, b, c in C.GATE_FEES)
    return (f'<table class="gate"><thead><tr><th scope="col">Item</th><th scope="col">At the gate</th></tr></thead><tbody>{free}{fees}</tbody></table>'
            f'<p class="fine">{C.FEES_NOTE} <a href="{C.PRICE_LIST_URL}" target="_blank" rel="noopener">Recycle North Geelong price&nbsp;list</a></p>')


def cant_take():
    return "".join(f'<li>{CROSS}<span>{x}</span></li>' for x in C.CANT_TAKE)


def weights_table():
    rows = ""
    for g, gname in C.GROUPS:
        if g == "cant":
            continue
        rows += f'<tr class="grp"><th colspan="3" scope="colgroup">{gname}</th></tr>'
        for iid, name, grp, kg, st, note, ic in C.ITEMS:
            if grp != g:
                continue
            n = NOTES.get(iid) or (note if st in ("prep", "call") else "")
            rows += f'<tr><td class="it">{name}</td><td class="n">{kg:,}&nbsp;kg</td><td class="nt">{n}</td></tr>'
    return (f'<table class="wt"><thead><tr><th scope="col">Item</th><th scope="col" class="n">Guide weight</th><th scope="col">Note</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')


# ---------------------------------------------------------------- layout
def topbar():
    return (f'<div class="tb"><div class="wrap tb-in">'
            f'<span class="tb-rg">A Recycle Group business <img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="96" height="15"></span>'
            f'<span class="tb-r"><span class="tb-hide">Collections from 1 tonne · Geelong, Melbourne and regional Victoria</span>'
            f'<a href="tel:{C.PHONE_TEL}">{C.PHONE}</a></span>'
            f'</div></div>')


def header(nav_key):
    links = (f'<a class="m-only" href="./"{" aria-current=page" if nav_key == "home" else ""}>Home</a>' +
             "".join(f'<a href="{h}"{" aria-current=page" if k == nav_key else ""}>{l}</a>' for k, h, l in NAV))
    return f'''<a class="sr skip" href="#main">Skip to content</a>
{topbar()}
<header class="hd"><div class="wrap hd-in">
  <a class="brand" href="./" aria-label="{NAME} home"><picture><source media="(max-width:620px)" srcset="assets/brand/plate.svg"><img src="assets/brand/logo-dark.svg" alt="{NAME}" width="306" height="60"></picture></a>
  <nav class="nav" id="nav" aria-label="Main">{links}<a class="m-only m-call" href="tel:{C.PHONE_TEL}">Call {C.CONTACT_NAME} {C.PHONE}</a></nav>
  <a class="btn btn-yellow hd-cta" href="quote.html"{" aria-current=page" if nav_key == "contact" else ""}><span><span class="long">Get a </span>quote</span></a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
</div></header>'''


def footer():
    year = datetime.date.today().year
    pages = "".join(f'<li><a href="{h}">{l}</a></li>' for _, h, l in NAV)
    return f'''<footer class="ft"><div class="wrap">
  <div class="ft-top">
    <img class="ft-logo" src="assets/brand/logo-dark.svg" alt="{NAME}" width="306" height="60">
    <p class="ft-line">Scrap metal collections from one tonne. Every tonne on the&nbsp;record.</p>
  </div>
  <div class="ft-grid">
    <div><p class="label">Collections</p><ul><li>{C.CONTACT_FULL}</li><li><a href="tel:{C.PHONE_TEL}">{C.PHONE}</a></li><li><a href="mailto:{C.EMAIL}">{C.EMAIL}</a></li><li><a href="quote.html">Get a quote</a></li></ul></div>
    <div><p class="label">Drop-off under a tonne</p><ul><li>{C.FACILITY}</li><li>{C.STREET}, {C.SUBURB}</li><li>{C.HOURS_DAYS}</li><li><a href="drop-off.html">Drop-off details</a></li></ul></div>
    <div><p class="label">Pages</p><ul><li><a href="./">Home</a></li>{pages}<li><a href="quote.html">Quote</a></li></ul></div>
  </div>
  <div class="ft-rg"><img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="124" height="19"><p>{C.rg_business(NAME)} · {C.RG_LINE}</p><p class="ft-c">&copy; {year} {NAME}</p></div>
</div></footer>'''


def page(fname):
    raw = open(os.path.join(SRC, "pages", fname)).read()
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", raw[: raw.index("-->")], re.M))
    body = raw[raw.index("-->") + 3:].strip()
    map_iframe = f'<iframe title="Map: {C.ADDRESS}" loading="lazy" referrerpolicy="no-referrer" src="{C.MAP_EMBED}"></iframe>'
    for key, val in {
        "{{MANIFEST}}": manifest(), "{{DOCKET}}": docket(), "{{DOCKET_BIG}}": docket(True),
        "{{GATE_GUIDE}}": gate_guide(), "{{CANT_TAKE}}": cant_take(), "{{WEIGHTS}}": weights_table(),
        "{{ARROW}}": ARROW, "{{CHECK}}": CHECK,
        "{{PHONE}}": C.PHONE.replace(" ", "&nbsp;"), "{{PHONE_TEL}}": C.PHONE_TEL, "{{EMAIL}}": C.EMAIL,
        "{{CONTACT}}": C.CONTACT_NAME, "{{CONTACT_FULL}}": C.CONTACT_FULL, "{{FACILITY}}": C.FACILITY,
        "{{STREET}}": C.STREET, "{{SUBURB}}": C.SUBURB, "{{ADDRESS}}": C.ADDRESS.replace("VIC 3215", "VIC&nbsp;3215"),
        "{{HOURS}}": C.HOURS_DAYS, "{{HOURS_NOTE}}": C.HOURS_NOTE, "{{MAPS_DIR}}": C.MAPS_DIR,
        "{{MAP}}": map_iframe, "{{YARTA}}": C.YARTA_LINE, "{{PRICE_LIST_URL}}": C.PRICE_LIST_URL,
        "{{CANT_SHORT}}": C.CANT_TAKE_SHORT,
    }.items():
        body = body.replace(key, val)
    assert "{{" not in body, f"unfilled placeholder in {fname}: {re.findall(r'{{[A-Z_:a-z]+}}', body)}"
    body = C.glue(body)
    url = SITE_URL + ("" if fname == "index.html" else fname)
    schema = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": NAME, "alternateName": SHORT,
              "description": "Scrap metal collections from one tonne for businesses, sites, farms and councils. One service fee, quoted before we come. A weighbridge docket for every load.",
              "url": SITE_URL, "telephone": C.PHONE_INTL, "email": C.EMAIL,
              "areaServed": ["Geelong", "Melbourne", "Regional Victoria"],
              "address": {"@type": "PostalAddress", "streetAddress": C.STREET, "addressLocality": C.SUBURB,
                          "addressRegion": C.STATE, "postalCode": C.POSTCODE, "addressCountry": "AU"}}
    html = f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta["title"]}</title>
<meta name="description" content="{meta["description"]}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0E0E0E">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{meta["title"]}"><meta property="og:description" content="{meta["description"]}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="assets/brand/icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/saira-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/inter-tight-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/main.css?v={VER}">
{C.review_script(DEPTH)}
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body data-concept="tonne" data-page="{PAGE_KEY.get(fname, "home")}">
{header(meta.get("nav", ""))}
<main id="main">
{body}
</main>
{footer()}
<script>window.BTT={{phone:"{C.PHONE_TEL}",minKg:{C.MIN_KG},contact:"{C.CONTACT_NAME}"}};</script>
<script src="assets/js/main.js?v={VER}" defer></script>
</body>
</html>
'''
    C.check(html, "by-the-tonne/" + fname)
    open(os.path.join(SITE, fname), "w").write(html)
    return fname


def _ttf(woff2):
    from fontTools.ttLib import TTFont
    out = os.path.join("/tmp", os.path.basename(woff2).replace(".woff2", ".ttf"))
    if not os.path.exists(out):
        f = TTFont(woff2)
        f.flavor = None
        f.save(out)
    return out


def og_image():
    from PIL import Image, ImageDraw, ImageFont
    import cairosvg, io
    sys.path.insert(0, ROOT)
    import logo as L
    W, H = 1200, 630
    ph = Image.open(os.path.join(SITE, "assets/img/hero.webp")).convert("RGB")
    s = max(W / ph.width, H / ph.height)
    ph = ph.resize((int(ph.width * s), int(ph.height * s)))
    left = int((ph.width - W) * 0.7)
    ph = ph.crop((left, (ph.height - H) // 2, left + W, (ph.height - H) // 2 + H))
    shade = Image.new("L", (W, H))
    shade.putdata([int(max(0, 232 - x * 0.3)) for x in range(W)] * H)
    black = Image.new("RGB", (W, H), (14, 14, 14))
    bg = Image.composite(black, ph, shade)
    logo = cairosvg.svg2png(url=os.path.join(SITE, "assets/brand/logo-dark.svg"), output_width=330)
    lg = Image.open(io.BytesIO(logo)).convert("RGBA")
    bg.paste(lg, (56, 54), lg)
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(L.static_ttf(800, 125), 70)
    f2 = ImageFont.truetype(_ttf(os.path.join(ROOT, "fonts", "ibm-plex-mono-latin-500-normal.woff2")), 23)
    d.text((56, 268), "Metal collections,", font=f1, fill=(255, 255, 255))
    d.text((56, 350), "by the tonne.", font=f1, fill=(255, 255, 255))
    d.rectangle((56, 470, 104, 480), fill=(255, 210, 0))
    d.text((56, 506), "FROM 1 TONNE · ONE FEE, QUOTED FIRST · A DOCKET FOR EVERY LOAD", font=f2, fill=(205, 205, 205))
    bg.save(os.path.join(SITE, "og.jpg"), quality=86)


def main():
    for d in ("css", "js", "fonts", "brand"):
        os.makedirs(os.path.join(SITE, "assets", d), exist_ok=True)
    shutil.copy(os.path.join(SRC, "css", "main.css"), os.path.join(SITE, "assets", "css", "main.css"))
    shutil.copy(os.path.join(SRC, "js", "main.js"), os.path.join(SITE, "assets", "js", "main.js"))
    for f in os.listdir(os.path.join(ROOT, "fonts")):
        if f.endswith(".woff2"):
            shutil.copy(os.path.join(ROOT, "fonts", f), os.path.join(SITE, "assets", "fonts", f))
    C.copy_rg_logos(os.path.join(SITE, "assets", "brand"))
    built = [page(f) for f in sorted(os.listdir(os.path.join(SRC, "pages"))) if f.endswith(".html")]
    og_image()
    print("by the tonne built", built)


if __name__ == "__main__":
    main()
