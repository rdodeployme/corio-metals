#!/usr/bin/env python3
"""Build The Metal Drop (concept 2): public first, an item checker, business collections second.

Output: the-metal-drop/ in the repo.
"""
import json, os, re, shutil, datetime, hashlib, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "common"))
sys.path.insert(0, ROOT)
import common as C  # noqa: E402
from icons import svg as icon  # noqa: E402

SRC = os.path.join(ROOT, "src")
SITE = os.path.join(C.REPO, "the-metal-drop")
DEPTH = 1
NAME = "The Metal Drop"
SITE_URL = C.SITE_BASE + "the-metal-drop/"

NAV = [("dropoff", "drop-off.html", "Plan your visit"), ("take", "what-we-take.html", "What we take"),
       ("collect", "business.html", "Business collections"), ("contact", "faq.html", "FAQ &amp; contact")]
PAGE_KEY = {"index.html": "home", "drop-off.html": "dropoff", "what-we-take.html": "take",
            "business.html": "collect", "faq.html": "contact"}

# ---------------------------------------------------------------- checker data
FEE_SHORT = {"gas": "$15 to $25", "ext": "$10 to $15", "solar": "$39 each"}
CHIP = {"ok": ("c-ok", "No charge"), "prep": ("c-prep", "Prep first"), "call": ("c-call", "Call first"),
        "no": ("c-no", "Can't take")}
# What to do before you come, per item (shown in the checker's "before you come" list)
PREP = {
    "bbq": "Take the gas bottle off.", "hws": "Drain it first.", "mower": "Drain the fuel and oil.",
    "gas": "Empty, and your own (not hired).", "battery": "Tape the terminals.",
    "tramp": "Take the mat, net and padding off.", "setting": "Timber and cushions off.",
    "filing": "Empty it first.", "bedframe": "Mattress off.", "ext": "Discharged.",
    "window": "Glass out if you can.", "server": "Drives removed or wiped first.",
    "engine": "Drain the fuel and oil.", "car": f"Call {C.CONTACT_NAME} before you bring it.",
}
KEYWORDS = {
    "fridge": "fridge freezer refrigerator whitegoods white goods", "washer": "washing machine washer laundry whitegoods",
    "dryer": "dryer clothes dryer whitegoods", "oven": "oven stove cooktop range whitegoods",
    "hws": "hot water unit heater cylinder system", "bbq": "bbq barbecue barbeque grill",
    "bike": "bike bicycle push bike", "tramp": "trampoline frame", "mower": "lawn mower lawnmower mower",
    "setting": "outdoor setting table chairs furniture", "filing": "filing cabinet drawers office",
    "bedframe": "bed frame bed base metal bed", "shelving": "shelving shelves shelf steel shelf",
    "pots": "pots pans cutlery kitchen saucepan", "gas": "gas bottle lpg cylinder bbq bottle",
    "ext": "fire extinguisher extinguisher", "battery": "car battery batteries lead acid",
    "roofing": "roofing iron corrugated iron roof sheet", "fence": "fence panel fencing steel fence",
    "pickets": "star pickets posts fencing", "mesh": "reo mesh reinforcing mesh steel mesh",
    "offcuts": "steel offcuts rhs angle plate beams scrap steel", "copper": "copper pipe plumbing copper",
    "cable": "cable wire electrical copper wire", "window": "aluminium window frame door frame sliding door",
    "gutter": "gutter downpipe spouting", "racking": "pallet racking racking warehouse",
    "locker": "locker lockers", "desk": "desk office desk frame", "cage": "roll cage trolley cage",
    "bench": "stainless bench sink kitchen bench", "server": "server rack computer it cabinet",
    "motor": "electric motor pump", "solar": "solar panel panels", "rims": "wheel rim rims alloy wheels",
    "radiator": "radiator car radiator", "engine": "engine block motor gearbox", "car": "car body vehicle car",
    "asbestos": "asbestos fibro", "chem": "chemicals chemical poison", "fullgas": "full gas cylinder hired cylinder",
}
NO_MSG = {
    "asbestos": "We can't take asbestos or anything that might contain it. It needs a licensed asbestos removalist.",
    "chem": "We can't take chemicals or hazardous waste with your metal.",
    "fullgas": "We can't take full or hired gas cylinders. Hired cylinders go back to the supplier.",
}
# The twelve items people bring most, shown first; the rest sit behind "Show more"
POPULAR = ["fridge", "washer", "bbq", "bike", "hws", "gas", "battery", "mower", "roofing", "copper", "racking", "rims"]
GROUP_NAMES = dict(C.GROUPS)
FILTER_LABEL = {"home": "Household", "trade": "Trade", "biz": "Business", "vehicle": "Vehicles", "cant": "Can't take"}

PHONE_ICON = icon("phone", "ic ic-sm")


def _ver():
    h = hashlib.sha1()
    for f in (os.path.join(SRC, "css", "main.css"), os.path.join(SRC, "js", "main.js")):
        h.update(open(f, "rb").read())
    return h.hexdigest()[:8]


VER = _ver()


# ---------------------------------------------------------------- components
def chip(iid, st):
    if st == "fee":
        return f'<span class="chip c-fee">{FEE_SHORT.get(iid, "Fee")}</span>'
    cls, lab = CHIP[st]
    return f'<span class="chip {cls}">{lab}</span>'


def checker(limit=True):
    filters = [("all", "All")] + [(k, FILTER_LABEL[k]) for k, _ in C.GROUPS]
    fbtns = "".join(f'<button type="button" class="fbtn" data-f="{k}" aria-pressed="{"true" if k == "all" else "false"}">{n}</button>'
                    for k, n in filters)
    items = {it[0]: it for it in C.ITEMS}
    ordered = [items[i] for i in POPULAR] + [it for it in C.ITEMS if it[0] not in POPULAR]
    tiles = ""
    for iid, name, grp, kg, st, note, ic in ordered:
        more = " more" if limit and iid not in POPULAR else ""
        q = f"{KEYWORDS.get(iid, '')} {name} {GROUP_NAMES[grp]}".lower()
        tiles += (f'<button type="button" class="tile t-{st}{more}" data-id="{iid}" data-g="{grp}" data-st="{st}" data-kg="{kg}" '
                  f'data-name="{C.esc(name)}" data-prep="{C.esc(PREP.get(iid, ""))}" data-q="{C.esc(q)}" '
                  f'data-msg="{C.esc(NO_MSG.get(iid, ""))}">'
                  f'<span class="tile-ic">{icon(ic)}</span><span class="tile-name">{name}</span>{chip(iid, st)}'
                  f'<span class="tile-n" aria-hidden="true"></span></button>')
    n_more = len(C.ITEMS) - len(POPULAR)
    more_btn = (f'<button type="button" class="btn btn-line btn-sm ck-more"><span>Show <b>{n_more}</b> more items</span></button>'
                if limit else "")
    return f'''<div class="ck" id="ck">
  <div class="ck-main">
    <div class="ck-search">{icon("search", "ic ic-sm")}<label class="sr" for="ck-q">Search items</label>
      <input id="ck-q" type="search" placeholder="Search: fridge, BBQ, copper pipe..." autocomplete="off" enterkeyhint="search"></div>
    <div class="ck-filters" role="group" aria-label="Show items">{fbtns}</div>
    <div class="ck-grid">{tiles}</div>
    <p class="ck-empty" hidden>Nothing by that name. If it's mostly metal we can probably take it. Call {C.CONTACT_NAME} on <a href="tel:{C.PHONE_TEL}">{C.PHONE.replace(" ", "&nbsp;")}</a> to&nbsp;check.</p>
    {more_btn}
  </div>
  <aside class="ck-load" aria-label="Your drop-off">
    <div class="ck-load-in" id="ck-load">
      <div class="ck-head"><h3>Your drop-off</h3><button type="button" class="ck-clear" id="ck-clear" hidden>Clear</button></div>
      <p class="ck-msg" id="ck-msg" role="status" hidden></p>
      <p class="ck-hint" id="ck-hint">Tap the items you've got. We'll show you what it costs, what to do first, and whether to bring it in or book a&nbsp;collection.</p>
      <ul class="ck-lines" id="ck-lines"></ul>
      <div class="ck-out" id="ck-out" hidden aria-live="polite">
        <div class="ck-weight"><span>Rough weight</span><b id="ck-kg">0&nbsp;kg</b><small id="ck-cap"></small></div>
        <div class="ck-meter" id="ck-meter" aria-hidden="true"><i></i><span class="m-1t">1 tonne</span></div>
        <div class="ck-meter-l" aria-hidden="true"><span>Drop it off</span><span>We collect</span></div>
        <div class="ck-cost"><span id="ck-cost-l">At the gate</span><b id="ck-cost">No charge</b></div>
        <div class="ck-verdict" id="ck-verdict"></div>
        <div class="ck-prep" id="ck-prep" hidden><h4 id="ck-prep-h">Before you come</h4><ul id="ck-prep-l"></ul></div>
        <div class="ck-cta" id="ck-cta"></div>
      </div>
    </div>
  </aside>
</div>
<div class="ck-bar" id="ck-bar" hidden><span id="ck-bar-t"></span><a href="#ck-load" class="btn btn-red btn-sm">View</a></div>'''


def gate_guide():
    free = "".join(f'<li class="g-ok">{icon("check", "ic ic-sm")}<div><b>{a}</b><span>{b}</span></div><em class="chip c-ok">No charge</em></li>'
                   for a, b in C.GATE_NO_CHARGE)
    fees = "".join(f'<li class="g-fee">{icon("tag", "ic ic-sm")}<div><b>{a}</b>{f"<span>{c}</span>" if c else ""}</div><em class="chip c-fee">{b}</em></li>'
                   for a, b, c in C.GATE_FEES)
    return (f'<div class="gate"><ul>{free}{fees}</ul><p class="small">{C.FEES_NOTE} '
            f'<a href="{C.PRICE_LIST_URL}" target="_blank" rel="noopener">Recycle North Geelong price&nbsp;list</a></p></div>')


def cant_take():
    return "".join(f'<li>{icon("cross", "ic ic-sm")}<span>{x}</span></li>' for x in C.CANT_TAKE)


def az_list():
    out = ""
    for g, gname in C.GROUPS:
        if g == "cant":
            continue
        lis = "".join(f'<li><span>{name}</span>{chip(iid, st)}</li>'
                      for iid, name, grp, kg, st, note, ic in C.ITEMS if grp == g)
        out += f'<div class="az-col"><h3>{gname}</h3><ul>{lis}</ul></div>'
    return out


# ---------------------------------------------------------------- layout
def strip():
    return (f'<div class="strip"><div class="wrap strip-in">'
            f'<span class="s-hide">{icon("clock", "ic ic-xs")}Open {C.HOURS_DAYS}</span>'
            f'<span class="s-hide">{icon("pin", "ic ic-xs")}{C.STREET}, {C.SUBURB}</span>'
            f'<span class="strip-rg">A Recycle Group business <img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="88" height="14"></span>'
            f'</div></div>')


def header(nav_key):
    links = (f'<a class="m-only" href="./"{" aria-current=page" if nav_key == "home" else ""}>Home</a>' +
             "".join(f'<a href="{h}"{" aria-current=page" if k == nav_key else ""}>{l}</a>' for k, h, l in NAV))
    return f'''<a class="sr skip" href="#main">Skip to content</a>
{strip()}
<header class="hd"><div class="wrap hd-in">
  <a class="brand" href="./" aria-label="{NAME} home"><img src="assets/brand/logo-light.svg" alt="{NAME}" width="152" height="55"></a>
  <nav class="nav" id="nav" aria-label="Main">{links}<a class="btn btn-red m-only m-call" href="tel:{C.PHONE_TEL}">{PHONE_ICON}Call {C.CONTACT_NAME} {C.PHONE}</a></nav>
  <a class="btn btn-red hd-call" href="tel:{C.PHONE_TEL}" aria-label="Call {C.CONTACT_NAME} on {C.PHONE}">{PHONE_ICON}<span class="long">{C.PHONE}</span><span class="short">Call</span></a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
</div></header>'''


def footer():
    year = datetime.date.today().year
    pages = "".join(f'<li><a href="{h}">{l}</a></li>' for _, h, l in NAV)
    return f'''<footer class="ft"><div class="wrap">
  <div class="ft-grid">
    <div class="ft-about"><img class="ft-logo" src="assets/brand/logo-dark.svg" alt="{NAME}" width="152" height="55"><p>The easy way to get rid of scrap metal in Geelong. Clean metal is no charge to drop off, and a tonne or more gets a&nbsp;collection.</p></div>
    <div><h4>Drop off</h4><ul><li>{C.FACILITY}</li><li>{C.STREET}</li><li>{C.SUBURB} {C.STATE}&nbsp;{C.POSTCODE}</li><li>{C.HOURS_DAYS}</li><li><a href="{C.MAPS_DIR}" target="_blank" rel="noopener">Get directions</a></li></ul></div>
    <div><h4>Business</h4><ul><li><a href="business.html">Collections from 1&nbsp;tonne</a></li><li><a href="business.html#quote">Get a quote</a></li><li>{C.CONTACT_FULL}</li><li><a href="tel:{C.PHONE_TEL}">{C.PHONE}</a></li><li><a href="mailto:{C.EMAIL}">{C.EMAIL}</a></li></ul></div>
    <div><h4>Pages</h4><ul><li><a href="./">Home</a></li>{pages}</ul></div>
  </div>
  <div class="ft-rg"><img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="120" height="19"><p>{C.rg_business(NAME)} · {C.RG_LINE}</p><p class="ft-c">&copy; {year} {NAME}</p></div>
</div></footer>'''


def page(fname):
    raw = open(os.path.join(SRC, "pages", fname)).read()
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", raw[: raw.index("-->")], re.M))
    body = raw[raw.index("-->") + 3:].strip()
    body = re.sub(r"\{\{ICON:([a-z]+)(?::([a-z\- ]+))?\}\}",
                  lambda m: icon(m.group(1), ("ic " + m.group(2)) if m.group(2) else "ic"), body)
    map_iframe = f'<iframe title="Map: {C.ADDRESS}" loading="lazy" referrerpolicy="no-referrer" src="{C.MAP_EMBED}"></iframe>'
    for key, val in {
        "{{CHECKER}}": checker(True), "{{CHECKER_ALL}}": checker(False), "{{GATE_GUIDE}}": gate_guide(),
        "{{CANT_TAKE}}": cant_take(), "{{AZ}}": az_list(),
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
    schema = {"@context": "https://schema.org", "@type": "RecyclingCenter", "name": NAME,
              "description": "Scrap metal drop-off at Recycle North Geelong, 116 Furner Avenue. Clean metal is no charge. Business collections from one tonne.",
              "url": SITE_URL, "telephone": C.PHONE_INTL, "email": C.EMAIL,
              "address": {"@type": "PostalAddress", "streetAddress": C.STREET, "addressLocality": C.SUBURB,
                          "addressRegion": C.STATE, "postalCode": C.POSTCODE, "addressCountry": "AU"},
              "geo": {"@type": "GeoCoordinates", "latitude": C.LAT, "longitude": C.LON}}
    html = f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta["title"]}</title>
<meta name="description" content="{meta["description"]}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#FFFFFF">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{meta["title"]}"><meta property="og:description" content="{meta["description"]}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="assets/brand/icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/rubik-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/rubik-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/main.css?v={VER}">
{C.review_script(DEPTH)}
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body data-concept="drop" data-page="{PAGE_KEY.get(fname, "home")}">
{header(meta.get("nav", ""))}
<main id="main">
{body}
</main>
{footer()}
<script>window.MD={{phone:"{C.PHONE_TEL}",minKg:{C.MIN_KG},maps:"{C.MAPS_DIR}",contact:"{C.CONTACT_NAME}"}};</script>
<script src="assets/js/main.js?v={VER}" defer></script>
</body>
</html>
'''
    C.check(html, "the-metal-drop/" + fname)
    open(os.path.join(SITE, fname), "w").write(html)
    return fname


def _ttf(woff2):
    """PIL can't always read woff2; decompress to a temporary ttf."""
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
    W, H = 1200, 630
    bg = Image.new("RGB", (W, H), (246, 245, 241))
    ph = Image.open(os.path.join(SITE, "assets/img/hero.webp")).convert("RGB")
    pw = 540
    s = max(pw / ph.width, H / ph.height)
    ph = ph.resize((int(ph.width * s), int(ph.height * s)))
    left = int((ph.width - pw) * 0.42)
    ph = ph.crop((left, (ph.height - H) // 2, left + pw, (ph.height - H) // 2 + H))
    bg.paste(ph, (W - pw, 0))
    logo = cairosvg.svg2png(url=os.path.join(SITE, "assets/brand/logo-light.svg"), output_width=300)
    lg = Image.open(io.BytesIO(logo)).convert("RGBA")
    bg.paste(lg, (56, 52), lg)
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(_ttf(os.path.join(ROOT, "fonts", "rubik-latin-800-normal.woff2")), 66)
    f2 = ImageFont.truetype(_ttf(os.path.join(ROOT, "fonts", "rubik-latin-500-normal.woff2")), 28)
    d.text((56, 236), "Got scrap metal?", font=f1, fill=(27, 29, 32))
    d.text((56, 314), "Drop it here.", font=f1, fill=(213, 43, 30))
    d.text((56, 440), "Clean scrap metal is no charge to drop off.", font=f2, fill=(27, 29, 32))
    d.text((56, 482), "116 Furner Avenue, North Geelong", font=f2, fill=(95, 100, 107))
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
    print("metal drop built", built)


if __name__ == "__main__":
    main()
