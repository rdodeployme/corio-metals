#!/usr/bin/env python3
"""Build Recycled Metals (concept 3, was BTT By The Tonne). By the tonne.

Richard's notes, 26 Oct 2026: free drop-off at any volume; four ways to move metal (drop it off,
a bin dropped off, an operator with excavator and grapple, containers and boats taken away);
collections by enquiry; Crux's 766-item directory as "Find out what you can drop off" with a
drop-off column; panels for a shed load, a farm or property, industry or business; grey photo
tiles for every sector; a map of the towns covered. No "we", no tonne thresholds, no YARTA.

Keeps the BTT look: black, white and safety yellow, Saira headings, black-and-white photos,
the riveted yellow nameplate (now reading RECYCLED METALS). Output: recycled-metals/ in the
repo, plus redirect pages left at by-the-tonne/.
"""
import json, os, re, shutil, datetime, hashlib, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "common"))
sys.path.insert(0, ROOT)
import common as C  # noqa: E402
import map as MAP  # noqa: E402

SRC = os.path.join(ROOT, "src")
SLUG = "recycled-metals"
SITE = os.path.join(C.REPO, SLUG)
OLD = os.path.join(C.REPO, "by-the-tonne")
DEPTH = 1
NAME = "Recycled Metals"
SITE_URL = C.SITE_BASE + SLUG + "/"

NAV = [("dropoff", "drop-off.html", "Drop-off"), ("collect", "bins-and-collections.html", "Bins and collections"),
       ("take", "items.html", "What you can drop off"), ("area", "./#area", "Service area")]
PAGE_KEY = {"index.html": "home", "drop-off.html": "dropoff", "bins-and-collections.html": "collect",
            "items.html": "take", "enquire.html": "contact"}
# old BTT pages -> new pages (redirects stay at by-the-tonne/)
REDIRECTS = {"index.html": "", "drop-off.html": "drop-off.html", "services.html": "bins-and-collections.html",
             "what-we-collect.html": "items.html", "quote.html": "enquire.html", "reporting.html": "bins-and-collections.html"}

ARROW = '<svg class="arr" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 10h13M11 5l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
CHECK = '<svg class="tk" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
CROSS = '<svg class="tk" viewBox="0 0 20 20" aria-hidden="true"><path d="M5 5l10 10M15 5L5 15" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
SEARCH = '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.75" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M13 13l4.5 4.5" stroke="currentColor" stroke-width="1.8"/></svg>'

FEE_SHORT = {"gas": "$15 or $25", "ext": "$10 or $15", "n2o": "$20", "solar": "$39"}
BIN_SIZES = [15, 32, 42]

# Copy rules for this site (Richard's notes, 26 Oct 2026). The build stops if any of these show up.
RULES = [
    (r"\b(we|we'?re|we'?ll|we'?ve|we'?d|our|ours|ourselves|us)\b", "first person (no \"we\")"),
    (r"under a tonne|tonne or more|a tonne or|one tonne|1\s?(tonne|t)\b|from a tonne|minimum", "tonne thresholds"),
    (r"yarta", "YARTA"),
    (r"free (collection|pick-?up|bin)|collections? (is|are) free|bins? (is|are) free", "free collections"),
]


def rules(html, fname):
    text = re.sub(r"<script.*?</script>|<style.*?</style>|<svg.*?</svg>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text).replace("&nbsp;", " ").replace("&#x27;", "'").replace("&rsquo;", "'")
    for pat, what in RULES:
        m = re.search(pat, text, re.I)
        if m:
            raise SystemExit(f"BUILD FAILED: {what} in {fname}: ...{text[max(0, m.start() - 70): m.end() + 70]}...")


def _ver():
    h = hashlib.sha1()
    for f in (os.path.join(SRC, "css", "main.css"), os.path.join(SRC, "js", "main.js")):
        h.update(open(f, "rb").read())
    return h.hexdigest()[:8]


VER = _ver()


# ---------------------------------------------------------------- directory data (Richard's list, via Crux)
def clean_note(s):
    s = re.sub(r"(\w+) asbestos-free", r"\1 with no asbestos", s)
    return s.replace("asbestos-free", "no asbestos").replace("PCB-free", "no PCBs")


def fee_for(name):
    n = name.lower()
    if re.search(r"\blpg\b|gas bottle", n):
        return "gas"
    if "fire extinguisher" in n:
        return "ext"
    if "nitrous" in n or "cream charger" in n:
        return "n2o"
    if re.search(r"solar panels?$", n) and "frame" not in n:
        return "solar"
    return ""


def load_directory():
    cats = json.load(open(os.path.join(ROOT, "data", "directory-source.json")))
    for c in cats:
        c["title"] = c["title"].replace(" ", " ")
        c["note"] = clean_note(c.get("note", ""))
        if c["id"] == "ports":   # Richard's note, without "we" and YARTA (26 Oct notes)
            c["note"] = ("Aircraft components, marine equipment, electrical infrastructure and anything that may be contaminated "
                         "need ownership verification, decommissioning and the right handling first. Secure or safety-critical "
                         "equipment may need controlled disposal, arranged by enquiry.")
        for it in c["items"]:
            it["note"] = clean_note(it["note"])
            it["fee"] = fee_for(it["n"])
            it["spec"] = "Specialist" in it["tags"]
    return cats


DIR = load_directory()
TOTAL = sum(len(c["items"]) for c in DIR)
assert TOTAL == 766, TOTAL

SHORT = {"councils": "Councils", "transfer-stations": "Transfer stations", "residential": "Residential", "roads": "State roads",
         "health": "Health and aged care", "education": "Education", "offices": "Offices", "whitegoods": "Retail and whitegoods",
         "warehousing": "Warehousing", "industry": "Industry", "trades": "Trades", "rural": "Rural and farming",
         "hospitality": "Hospitality", "solar": "Solar", "ports": "Airports and ports"}
# grey photo for each sector tile
TILE_IMG = {"councils": ("councils", "A council depot skip bin of old street signs and bench frames beside a works ute"),
            "transfer-stations": ("transfer", "A metal bay at a transfer station piled with whitegoods and steel, a car and trailer backed up"),
            "residential": ("residential", "Bikes, a barbecue frame, a mower and roofing iron sorted on a suburban driveway"),
            "roads": ("roads", "Stacks of bent guardrail, sign posts and old sign plates in a roadworks depot"),
            "health": ("health", "Old hospital bed frames and steel trolleys lined up on a loading dock"),
            "education": ("education", "Old steel lockers, chair frames and computer towers in a school storeroom"),
            "offices": ("offices", "Filing cabinets and desk frames gathered on an emptied office floor"),
            "whitegoods": ("whitegoods", "Old fridges, washing machines and ovens lined up at a store's loading dock"),
            "warehousing": ("warehousing", "Dismantled pallet racking stacked on a warehouse floor beside a forklift"),
            "industry": ("industry", "A steel bin of offcuts in an engineering workshop, with a lathe and steel racks behind"),
            "trades": ("trades", "A ute tray loaded with copper pipe, cable, window frames and an old hot water unit"),
            "rural": ("rural", "Old farm machinery, fencing wire and star pickets beside a hay shed"),
            "hospitality": ("hospitality", "Stainless benches and old commercial ovens in a kitchen being stripped out"),
            "solar": ("solar", "Old solar panels on pallets with aluminium rails and a cage of inverters"),
            "ports": ("ports", "An old shipping container and scrap steel at a port, cranes behind")}


def dir_json():
    cats = [{"id": c["id"], "n": c["num"], "t": c["title"], "c": len(c["items"])} for c in DIR]
    items = [[i, it["n"], it["note"], 1 if it["spec"] else 0, it["fee"]] for i, c in enumerate(DIR) for it in c["items"]]
    return json.dumps({"cats": cats, "items": items, "fees": FEE_SHORT}, separators=(",", ":"), ensure_ascii=False)


def item_li(it):
    """One directory row: the item (with its note and Specialist tag) and the drop-off column."""
    name = C.esc(it["n"])
    note = f' <small>({C.esc(it["note"])})</small>' if it["note"] else ""
    tag = ' <span class="tag">Specialist</span>' if it["spec"] else ""
    price = f'<span class="pr paid">{FEE_SHORT[it["fee"]]}</span>' if it["fee"] else '<span class="pr">Free</span>'
    return f'<li><span class="nm">{name}{note}{tag}</span>{price}</li>'


def directory():
    out = []
    for c in DIR:
        note = f'<p class="note">{C.esc(c["note"])}</p>' if c["note"] else ""
        lis = "".join(item_li(it) for it in c["items"])
        out.append(f'<details id="{c["id"]}"><summary><span class="n">{c["num"]}</span>'
                   f'<span class="t"><b>{C.esc(c["title"])}</b><span>{C.esc(c["desc"])}</span></span>'
                   f'<span class="c">{len(c["items"])} items</span></summary>'
                   f'<div class="dir-terms"><span><b>Drop-off</b> Free, unless a fee is shown</span><span><b>Collection</b> By enquiry</span></div>{note}'
                   f'<div class="dir-head" aria-hidden="true"><span>Item</span><span>Drop-off</span><span>Item</span><span>Drop-off</span></div><ul>{lis}</ul></details>')
    return '<div class="dir" id="dir">' + "".join(out) + "</div>"


def dir_chips():
    return "".join(f'<a href="#{c["id"]}">{C.esc(SHORT[c["id"]])}</a>' for c in DIR)


def tiles():
    out = []
    for c in DIR:
        img, alt = TILE_IMG[c["id"]]
        title = C.esc(c["title"]).replace(" &amp; ", "&nbsp;&amp; ")
        out.append(f'<a class="tile" href="items.html#{c["id"]}"><img src="assets/img/{img}-sm.webp" width="700" height="523" alt="{C.esc(alt)}" loading="lazy">'
                   f'<span class="tile-t"><i>{c["num"]}</i><b>{title}</b><em>{len(c["items"])} items</em></span></a>')
    return '<div class="tiles">' + "".join(out) + "</div>"


def short_fee(b):
    return {"$15 under 9 kg, $25 over 9 kg": "$15 / $25", "$10 under 3 kg, $15 over 3 kg": "$10 / $15"}.get(b, b.replace(" each", ""))


def finder():
    chips = "".join(f'<button type="button" data-cat="{i}" aria-pressed="false">{SHORT[c["id"]]}</button>' for i, c in enumerate(DIR))
    fees = "".join(f"<li><span>{a}</span><span>{short_fee(b)}</span></li>" for a, b, _ in C.GATE_FEES)
    enq = "Councils, state roads, schools, offices, hospitals, industry and&nbsp;farms"
    return f'''<div class="finder" id="finder-ui">
  <div class="f-main">
    <div class="f-search">{SEARCH}<label class="sr" for="f-q">Search what you can drop off</label>
      <input id="f-q" type="search" placeholder="Search {TOTAL} items, e.g. fridge, racking, guardrail" data-short="Search {TOTAL} items, e.g. racking" autocomplete="off" enterkeyhint="search"></div>
    <div class="f-meta"><span id="f-count" aria-live="polite">{TOTAL} items across {len(DIR)} categories</span><button type="button" id="f-clear" hidden>Clear</button></div>
    <div class="chips" role="group" aria-label="Categories">{chips}</div>
    <div class="f-out" id="f-out"></div>
  </div>
  <aside class="ways" aria-label="Two ways in">
    <p class="label">Two ways in</p>
    <dl>
      <div><dt>Drop it off</dt><dd><b class="big-free">Free</b>Any volume, at {C.STREET}, North&nbsp;Geelong. {C.HOURS_DAYS}, no&nbsp;booking.</dd></div>
      <div><dt>Collection</dt><dd><b class="big-enq">By enquiry</b>{enq}.</dd></div>
      <div><dt>Handling fees at the gate</dt><dd><ul class="fees">{fees}</ul></dd></div>
    </dl>
    <div class="btns"><a class="btn btn-yellow" href="enquire.html">Enquire {ARROW}</a><a class="btn btn-ghost" href="drop-off.html">Drop-off</a></div>
  </aside>
</div>
<noscript><p class="fine" style="margin-top:20px">Search needs JavaScript. <a href="items.html">See the full list of {TOTAL} items</a>.</p></noscript>
<script>window.RM_DIR={dir_json()};</script>'''


SIZES = [("Bucket", "A few offcuts, old taps and fittings, a box of bolts.", 1),
         ("Boot", "A BBQ frame, a bike, a mower with the fuel drained.", 2),
         ("Back of the ute", "Roofing iron, fence panels, an old hot water unit.", 3),
         ("B-double", "Truckloads from a factory, a farm or a demolition job.", 4)]


def sizes():
    out = "".join(f'<li><span class="sz-bar" style="--s:{s}" aria-hidden="true"></span><b>{n}</b><p>{d}</p><span class="pr">Free</span></li>'
                  for n, d, s in SIZES)
    return f'<ol class="sizes">{out}</ol>'


def bin_sizes():
    """Skip bins drawn to scale: side of each square = cube root of the volume."""
    mx = max(BIN_SIZES) ** (1 / 3)
    out = "".join(f'<li><span class="cube" style="--k:{(v ** (1 / 3)) / mx:.3f}" aria-hidden="true"></span><b>{v}&nbsp;m³</b></li>' for v in BIN_SIZES)
    return f'<ul class="bins" aria-label="Skip bin sizes: 15, 32 and 42 cubic metres">{out}</ul>'


def gate_guide():
    free = "".join(f'<tr class="nc"><td class="it"><b>{a}</b><small>{b}</small></td><td class="v">Free</td></tr>' for a, b in C.GATE_NO_CHARGE)
    fees = "".join(f'<tr><td class="it"><b>{a}</b>{f"<small>{c}</small>" if c else ""}</td><td class="v">{b}</td></tr>' for a, b, c in C.GATE_FEES)
    return (f'<table class="gate"><thead><tr><th scope="col">Item</th><th scope="col">At the gate</th></tr></thead><tbody>{free}{fees}</tbody></table>'
            f'<p class="fine" style="margin-top:14px">Fees as listed on Recycle North Geelong\'s price list. Anything in a load that isn\'t metal goes through the transfer station at its usual rate. <a href="{C.PRICE_LIST_URL}" target="_blank" rel="noopener">Recycle North Geelong price&nbsp;list</a></p>')


def cant_take():
    return "".join(f'<li>{CROSS}<span>{x}</span></li>' for x in C.CANT_TAKE)


def creds():
    return '''<div class="creds">
  <div><p class="cr-big">90+</p><p>Streams separated on site at Furner Avenue, under&nbsp;cover</p></div>
  <div><p class="cr-big">EPA</p><p>Victoria registered site, R000312600, North&nbsp;Geelong</p></div>
  <div><p class="cr-big">ISO</p><p>9001, 14001 and 45001: Recycle Group's certified&nbsp;systems</p></div>
  <div><p class="cr-big">6&nbsp;days</p><p>Monday to Saturday for drop-off, no&nbsp;booking</p></div>
</div>'''


def area():
    return f'<div class="area"><figure class="area-map">{MAP.svg()}</figure>{MAP.town_list()}</div>'


# ---------------------------------------------------------------- layout
def topbar():
    return (f'<div class="tb"><div class="wrap tb-in">'
            f'<span class="tb-rg">A Recycle Group business <img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="96" height="15"></span>'
            f'<span class="tb-r"><span class="tb-hide">Free drop-off · {C.HOURS_SHORT} · {C.STREET}, North Geelong</span>'
            f'<a href="tel:{C.PHONE_TEL}">{C.PHONE}</a></span>'
            f'</div></div>')


def header(nav_key):
    links = (f'<a class="m-only" href="./"{" aria-current=page" if nav_key == "home" else ""}>Home</a>' +
             "".join(f'<a href="{h}"{" aria-current=page" if k == nav_key else ""}>{l}</a>' for k, h, l in NAV))
    return f'''<a class="sr skip" href="#main">Skip to content</a>
{topbar()}
<header class="hd"><div class="wrap hd-in">
  <a class="brand" href="./" aria-label="{NAME} home"><picture><source media="(max-width:620px)" srcset="assets/brand/plate.svg"><img src="assets/brand/logo-dark.svg" alt="{NAME}, by the tonne" width="289" height="60"></picture></a>
  <nav class="nav" id="nav" aria-label="Main">{links}<a class="m-only m-call" href="tel:{C.PHONE_TEL}">Call {C.CONTACT_NAME} {C.PHONE}</a></nav>
  <a class="btn btn-yellow hd-cta" href="enquire.html"{" aria-current=page" if nav_key == "contact" else ""}><span>Enquire</span></a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
</div></header>'''


def footer():
    year = datetime.date.today().year
    pages = "".join(f'<li><a href="{h}">{l}</a></li>' for _, h, l in NAV)
    return f'''<footer class="ft"><div class="wrap">
  <div class="ft-top">
    <img class="ft-logo" src="assets/brand/logo-dark.svg" alt="{NAME}, by the tonne" width="289" height="60">
    <p class="ft-line"><span class="nw">Free drop-off.</span> <span class="nw">Any volume.</span> <span class="nw">By the tonne.</span></p>
  </div>
  <div class="ft-grid">
    <div><p class="label">Drop-off</p><ul><li>{C.FACILITY}</li><li>{C.STREET}, {C.SUBURB}</li><li>{C.HOURS_DAYS}</li><li><a href="drop-off.html">Drop-off details</a></li></ul></div>
    <div><p class="label">Bins and collections</p><ul><li>By enquiry</li><li>{C.CONTACT_FULL}</li><li><a href="tel:{C.PHONE_TEL}">{C.PHONE}</a></li><li><a href="mailto:{C.EMAIL}">{C.EMAIL}</a></li></ul></div>
    <div><p class="label">Pages</p><ul><li><a href="./">Home</a></li>{pages}<li><a href="enquire.html">Enquire</a></li></ul></div>
    <div><p class="label">Backed by Recycle Group</p><ul><li>EPA Victoria R000312600</li><li>ISO 9001, 14001 and 45001</li></ul></div>
  </div>
  <div class="ft-rg"><img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="124" height="19"><p>{C.rg_business(NAME)} · {C.RG_LINE}</p><p class="ft-c">&copy; {year} {NAME}</p></div>
</div></footer>'''


def page(fname):
    raw = open(os.path.join(SRC, "pages", fname)).read()
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", raw[: raw.index("-->")], re.M))
    body = raw[raw.index("-->") + 3:].strip()
    map_iframe = f'<iframe title="Map: {C.ADDRESS}" loading="lazy" referrerpolicy="no-referrer" src="{C.MAP_EMBED}"></iframe>'
    lazy = {"{{FINDER}}": finder, "{{DIRECTORY}}": directory, "{{AREA}}": area, "{{TILES}}": tiles}
    for key, fn in lazy.items():
        if key in body:
            body = body.replace(key, fn())
    for key, val in {
        "{{DIR_CHIPS}}": dir_chips(), "{{SIZES}}": sizes(), "{{BIN_SIZES}}": bin_sizes(), "{{CREDS}}": creds(),
        "{{GATE_GUIDE}}": gate_guide(), "{{CANT_TAKE}}": cant_take(), "{{ARROW}}": ARROW, "{{CHECK}}": CHECK, "{{SEARCH}}": SEARCH,
        "{{TOTAL}}": str(TOTAL), "{{CATS}}": str(len(DIR)),
        "{{PHONE}}": C.PHONE.replace(" ", "&nbsp;"), "{{PHONE_TEL}}": C.PHONE_TEL, "{{EMAIL}}": C.EMAIL,
        "{{CONTACT}}": C.CONTACT_NAME, "{{CONTACT_FULL}}": C.CONTACT_FULL, "{{FACILITY}}": C.FACILITY,
        "{{STREET}}": C.STREET, "{{SUBURB}}": C.SUBURB, "{{ADDRESS}}": C.ADDRESS.replace("VIC 3215", "VIC&nbsp;3215"),
        "{{HOURS}}": C.HOURS_DAYS, "{{HOURS_NOTE}}": C.HOURS_NOTE, "{{MAPS_DIR}}": C.MAPS_DIR,
        "{{MAP}}": map_iframe, "{{CANT_SHORT}}": C.CANT_TAKE_SHORT,
    }.items():
        body = body.replace(key, val)
    assert "{{" not in body, f"unfilled placeholder in {fname}: {re.findall(r'{{[A-Z_:a-z]+}}', body)}"
    body = C.glue(body)
    url = SITE_URL + ("" if fname == "index.html" else fname)
    schema = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": NAME, "slogan": "By the tonne",
              "parentOrganization": {"@type": "Organization", "name": "Recycle Group"},
              "description": "Free scrap metal drop-off at any volume at Recycle North Geelong, 116 Furner Avenue. Bins, operators with excavator and grapple, and container and boat removal by enquiry.",
              "url": SITE_URL, "telephone": C.PHONE_INTL, "email": C.EMAIL,
              "areaServed": [t[0] for t in MAP.TOWNS] + ["Geelong"],
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
<script>window.RM={{phone:"{C.PHONE_TEL}",contact:"{C.CONTACT_NAME}"}};</script>
<script src="assets/js/main.js?v={VER}" defer></script>
</body>
</html>
'''
    C.check(html, f"{SLUG}/{fname}", allow_free=True)
    rules(html, f"{SLUG}/{fname}")
    open(os.path.join(SITE, fname), "w").write(html)
    return fname


def redirects():
    """Leave small pages at the old BTT address that send people to the new one."""
    if os.path.isdir(OLD):
        shutil.rmtree(OLD)
    os.makedirs(OLD)
    for old, new in REDIRECTS.items():
        to = f"../{SLUG}/{new}"
        open(os.path.join(OLD, old), "w").write(
            f'<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>{NAME}</title>'
            f'<meta name="robots" content="noindex"><link rel="canonical" href="{SITE_URL}{new}">'
            f'<meta http-equiv="refresh" content="0; url={to}"><script>location.replace("{to}"+location.hash)</script></head>'
            f'<body><p>BTT By The Tonne is now {NAME}. <a href="{to}">Go to {NAME}</a>.</p></body></html>\n')


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
    import logo as L
    W, H = 1200, 630
    ph = Image.open(os.path.join(SITE, "assets/img/bales-forklift.webp")).convert("RGB")
    s = max(W / ph.width, H / ph.height)
    ph = ph.resize((int(ph.width * s), int(ph.height * s)))
    left = int((ph.width - W) * 0.7)
    ph = ph.crop((left, (ph.height - H) // 2, left + W, (ph.height - H) // 2 + H))
    shade = Image.new("L", (W, H))
    shade.putdata([int(max(0, 236 - x * 0.28)) for x in range(W)] * H)
    black = Image.new("RGB", (W, H), (14, 14, 14))
    bg = Image.composite(black, ph, shade)
    logo = cairosvg.svg2png(url=os.path.join(SITE, "assets/brand/logo-dark.svg"), output_width=380)
    lg = Image.open(io.BytesIO(logo)).convert("RGBA")
    bg.paste(lg, (56, 54), lg)
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(L.static_ttf(800, 125), 66)
    f2 = ImageFont.truetype(_ttf(os.path.join(ROOT, "fonts", "ibm-plex-mono-latin-500-normal.woff2")), 23)
    d.text((56, 262), "Free metal drop-off.", font=f1, fill=(255, 255, 255))
    d.text((56, 340), "Any volume.", font=f1, fill=(255, 210, 0))
    d.rectangle((56, 462, 104, 472), fill=(255, 210, 0))
    d.text((56, 498), "BUCKET, BOOT, BACK OF THE UTE OR B-DOUBLE · 116 FURNER AVENUE", font=f2, fill=(205, 205, 205))
    bg.save(os.path.join(SITE, "og.jpg"), quality=86)


def main():
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    for d in ("css", "js", "fonts", "brand", "img"):
        os.makedirs(os.path.join(SITE, "assets", d), exist_ok=True)
    import logo as L
    L.lockup("light"), L.lockup("dark"), L.plate_only(), L.icons()
    shutil.copy(os.path.join(SRC, "css", "main.css"), os.path.join(SITE, "assets", "css", "main.css"))
    shutil.copy(os.path.join(SRC, "js", "main.js"), os.path.join(SITE, "assets", "js", "main.js"))
    for f in os.listdir(os.path.join(ROOT, "fonts")):
        if f.endswith(".woff2"):
            shutil.copy(os.path.join(ROOT, "fonts", f), os.path.join(SITE, "assets", "fonts", f))
    for f in os.listdir(os.path.join(ROOT, "img")):
        shutil.copy(os.path.join(ROOT, "img", f), os.path.join(SITE, "assets", "img", f))
    C.copy_rg_logos(os.path.join(SITE, "assets", "brand"))
    built = [page(f) for f in sorted(os.listdir(os.path.join(SRC, "pages"))) if f.endswith(".html")]
    og_image()
    redirects()
    print("recycled metals built", built)


if __name__ == "__main__":
    main()
