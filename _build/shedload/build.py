#!/usr/bin/env python3
"""Build Shedload (concept 4): brand first. Shedload? Drop it off. Truckload? We'll collect.

Output: shedload/ in the repo.
"""
import json, os, re, shutil, datetime, hashlib, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "common"))
import common as C  # noqa: E402

SRC = os.path.join(ROOT, "src")
SITE = os.path.join(C.REPO, "shedload")
DEPTH = 1
NAME = "Shedload"
SITE_URL = C.SITE_BASE + "shedload/"

NAV = [("dropoff", "drop-off.html", "Drop it off"), ("collect", "collect.html", "We collect"),
       ("take", "what-we-take.html", "What we take"), ("contact", "find-us.html", "Find us")]
PAGE_KEY = {"index.html": "home", "drop-off.html": "dropoff", "collect.html": "collect",
            "what-we-take.html": "take", "find-us.html": "contact"}

STAMP = {"ok": ("s-ok", "No charge"), "prep": ("s-prep", "Prep first"), "fee": ("s-fee", "Fee"),
         "call": ("s-call", "Call first"), "no": ("s-no", "Can't take")}
FEE_SHORT = {"gas": "$15 to $25", "ext": "$10 to $15", "solar": "$39 each"}
FEE_NOTE = {"gas": "Empty, and your own (not hired).", "ext": "Fully discharged."}
HOME_ITEMS = ["fridge", "washer", "bbq", "bike", "tramp", "mower", "gas", "battery", "roofing", "copper", "offcuts", "racking"]

ARROW = '<svg class="arr" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 10h13M11 5l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2.4"/></svg>'


def _ver():
    h = hashlib.sha1()
    for f in (os.path.join(SRC, "css", "main.css"), os.path.join(SRC, "js", "main.js")):
        h.update(open(f, "rb").read())
    return h.hexdigest()[:8]


VER = _ver()


def kg_label(kg):
    if kg >= 10000:
        return "10 tonnes plus"
    if kg >= 1000:
        return f"About {kg / 1000:g} tonnes"
    return f"About {kg:,} kg"


# ---------------------------------------------------------------- components
SHORT = {"bucket": "Bucket", "boot": "Boot", "ute": "Ute", "trailer": "Trailer", "shed": "Shedload", "truck": "Truckload", "site": "Site"}


def scale():
    last = len(C.LOADS) - 1
    stops = "".join(
        f'<li style="--f:{i / last:.4f}"><button type="button" data-i="{i}" aria-label="{n}, {kg_label(kg).lower()}"><b>{SHORT.get(k, n)}</b><span>{kg_label(kg).replace("About ", "").replace(" tonnes plus", " t+").replace(" tonnes", " t")}</span></button></li>'
        for i, (k, n, kg, eg) in enumerate(C.LOADS))
    data = [{"k": k, "n": n, "kg": kg, "eg": eg, "lab": kg_label(kg)} for k, n, kg, eg in C.LOADS]
    start = 3
    k, n, kg, eg = C.LOADS[start]
    return f'''<div class="scale" id="scale-ui">
  <div class="sc-in">
    <label class="sc-q" for="sc-r">Slide to the size of your load</label>
    <div class="sc-track">
      <input type="range" id="sc-r" min="0" max="{len(C.LOADS) - 1}" step="1" value="{start}" aria-valuetext="{n}, {kg_label(kg).lower()}">
      <span class="sc-line" aria-hidden="true"><i class="sc-1t">1 tonne</i></span>
    </div>
    <ol class="sc-stops">{stops}</ol>
    <div class="sc-tonne"><span class="t-big" aria-hidden="true">1&nbsp;t</span><p><b>Where's the line?</b> One tonne: 1,000&nbsp;kg. That's about twenty steel filing cabinets, and more than a trailer without brakes is allowed to weigh fully loaded (750&nbsp;kg).</p></div>
  </div>
  <div class="sc-out">
    <div class="sc-card" id="sc-out" aria-live="polite">
      <p class="sc-label">Your load</p>
      <div class="sc-name" id="sc-name">{n}</div>
      <p class="sc-kg" id="sc-kg">{kg_label(kg)}</p>
      <p class="sc-eg" id="sc-eg">{eg}</p>
      <div class="sc-verdict" id="sc-verdict"></div>
      <div class="btns" id="sc-cta"></div>
    </div>
  </div>
</div>
<script>window.SL_LOADS={json.dumps(data, separators=(",", ":"))};</script>'''


def stamp(iid, st):
    cls, lab = STAMP[st]
    if st == "fee":
        lab = FEE_SHORT.get(iid, "Fee")
    return f'<span class="stamp {cls}">{lab}</span>'


def stamp_grid(ids=None):
    items = [it for it in C.ITEMS if it[2] != "cant"] if ids is None else [next(i for i in C.ITEMS if i[0] == x) for x in ids]
    out = ""
    for iid, name, grp, kg, st, note, ic in items:
        n = FEE_NOTE.get(iid, "") if st == "fee" else note if st != "ok" or iid in ("battery", "filing", "bedframe", "setting", "window", "rims") else ""
        out += (f'<li class="it"><span class="it-n">{name}</span>{stamp(iid, st)}'
                f'{f"<small>{n}</small>" if n else ""}</li>')
    return f'<ul class="items">{out}</ul>'


def stamp_groups():
    out = ""
    for g, gname in C.GROUPS:
        if g == "cant":
            continue
        ids = [it[0] for it in C.ITEMS if it[2] == g]
        out += f'<section class="grp" id="{g}"><h3>{gname}</h3>{stamp_grid(ids)}</section>'
    return out


def ticket():
    return f'''<div class="ticket" aria-label="Clean scrap metal is no charge to drop off at 116 Furner Avenue, North Geelong, {C.HOURS_DAYS}">
  <div class="tk-l"><span>Admit one</span><b>Shedload</b></div>
  <div class="tk-r"><span>Clean scrap metal</span><b>No charge</b><span><span class="nw">116 Furner Ave</span> · <span class="nw">{C.HOURS_SHORT}</span></span></div>
</div>'''


def gate_guide():
    free = "".join(f'<li><span class="g-n"><b>{a}</b><small>{b}</small></span><span class="stamp s-ok">No charge</span></li>' for a, b in C.GATE_NO_CHARGE)
    fees = "".join(f'<li><span class="g-n"><b>{a}</b>{f"<small>{c}</small>" if c else ""}</span><span class="stamp s-fee">{b}</span></li>' for a, b, c in C.GATE_FEES)
    return (f'<ul class="gate">{free}{fees}</ul><p class="fine">{C.FEES_NOTE} '
            f'<a href="{C.PRICE_LIST_URL}" target="_blank" rel="noopener">Recycle North Geelong price&nbsp;list</a></p>')


def cant_take():
    return "".join(f'<li><span class="x" aria-hidden="true">&times;</span><span>{x}</span></li>' for x in C.CANT_TAKE)


# ---------------------------------------------------------------- layout
def topbar():
    return (f'<div class="tb"><div class="wrap tb-in">'
            f'<span class="tb-rg">A Recycle Group business <img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="92" height="15"></span>'
            f'<span class="tb-r"><span class="tb-hide">Drop-off {C.HOURS_SHORT} · {C.STREET}, {C.SUBURB}</span>'
            f'<a href="tel:{C.PHONE_TEL}">{C.PHONE}</a></span></div></div>')


def header(nav_key):
    links = (f'<a class="m-only" href="./"{" aria-current=page" if nav_key == "home" else ""}>Home</a>' +
             "".join(f'<a href="{h}"{" aria-current=page" if k == nav_key else ""}>{l}</a>' for k, h, l in NAV))
    return f'''<a class="sr skip" href="#main">Skip to content</a>
{topbar()}
<header class="hd"><div class="wrap hd-in">
  <a class="brand" href="./" aria-label="{NAME} home"><img src="assets/brand/logo-light.svg" alt="{NAME}" width="267" height="45"></a>
  <nav class="nav" id="nav" aria-label="Main">{links}<a class="m-only m-call" href="tel:{C.PHONE_TEL}">Call {C.CONTACT_NAME} {C.PHONE}</a></nav>
  <a class="btn btn-euc hd-cta" href="collect.html#quote"><span class="long">Get a quote</span><span class="short">Quote</span></a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
</div></header>'''


def footer():
    year = datetime.date.today().year
    pages = "".join(f'<li><a href="{h}">{l}</a></li>' for _, h, l in NAV)
    return f'''<footer class="ft"><div class="wrap">
  <div class="ft-top">
    <img class="ft-logo" src="assets/brand/logo-dark.svg" alt="{NAME}" width="267" height="45">
    <p class="ft-line">Shedload? Drop it off. Truckload? We'll&nbsp;collect.</p>
  </div>
  <div class="ft-grid">
    <div><h4>Drop it off</h4><ul><li>{C.FACILITY}</li><li>{C.STREET}, {C.SUBURB}</li><li>{C.HOURS_DAYS}</li><li><a href="{C.MAPS_DIR}" target="_blank" rel="noopener">Get directions</a></li></ul></div>
    <div><h4>We collect</h4><ul><li>From 1 tonne</li><li>{C.CONTACT_FULL}</li><li><a href="tel:{C.PHONE_TEL}">{C.PHONE}</a></li><li><a href="mailto:{C.EMAIL}">{C.EMAIL}</a></li></ul></div>
    <div><h4>Pages</h4><ul><li><a href="./">Home</a></li>{pages}</ul></div>
  </div>
  <div class="ft-rg"><img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="122" height="19"><p>{C.rg_business(NAME)} · {C.RG_LINE}</p><p class="ft-c">&copy; {year} {NAME}</p></div>
</div></footer>'''


def page(fname):
    raw = open(os.path.join(SRC, "pages", fname)).read()
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", raw[: raw.index("-->")], re.M))
    body = raw[raw.index("-->") + 3:].strip()
    map_iframe = f'<iframe title="Map: {C.ADDRESS}" loading="lazy" referrerpolicy="no-referrer" src="{C.MAP_EMBED}"></iframe>'
    for key, val in {
        "{{SCALE}}": scale(), "{{TICKET}}": ticket(), "{{STAMPS_HOME}}": stamp_grid(HOME_ITEMS),
        "{{STAMP_GROUPS}}": stamp_groups(), "{{GATE_GUIDE}}": gate_guide(), "{{CANT_TAKE}}": cant_take(),
        "{{ARROW}}": ARROW,
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
              "description": "Scrap metal drop-off at Recycle North Geelong, 116 Furner Avenue: clean metal is no charge. Collections from one tonne.",
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
<meta name="theme-color" content="#2C2D2F">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{meta["title"]}"><meta property="og:description" content="{meta["description"]}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="assets/brand/icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/big-shoulders-stencil-display-latin-900-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/public-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/main.css?v={VER}">
{C.review_script(DEPTH)}
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body data-concept="shed" data-page="{PAGE_KEY.get(fname, "home")}">
{header(meta.get("nav", ""))}
<main id="main">
{body}
</main>
{footer()}
<script>window.SL={{phone:"{C.PHONE_TEL}",minKg:{C.MIN_KG},maps:"{C.MAPS_DIR}",contact:"{C.CONTACT_NAME}"}};</script>
<script src="assets/js/main.js?v={VER}" defer></script>
</body>
</html>
'''
    C.check(html, "shedload/" + fname)
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
    W, H = 1200, 630
    bg = Image.new("RGB", (W, H), (234, 227, 210))
    ph = Image.open(os.path.join(SITE, "assets/img/hero.webp")).convert("RGB")
    pw = 520
    s = max(pw / ph.width, H / ph.height)
    ph = ph.resize((int(ph.width * s), int(ph.height * s)))
    left = int((ph.width - pw) * 0.55)
    ph = ph.crop((left, (ph.height - H) // 2, left + pw, (ph.height - H) // 2 + H))
    bg.paste(ph, (W - pw, 0))
    logo = cairosvg.svg2png(url=os.path.join(SITE, "assets/brand/logo-light.svg"), output_width=330)
    lg = Image.open(io.BytesIO(logo)).convert("RGBA")
    bg.paste(lg, (56, 56), lg)
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(_ttf(os.path.join(ROOT, "fonts", "big-shoulders-stencil-display-latin-900-normal.woff2")), 96)
    d.text((56, 170), "SHEDLOAD?", font=f1, fill=(44, 45, 47))
    d.text((56, 262), "DROP IT OFF.", font=f1, fill=(94, 115, 89))
    d.text((56, 372), "TRUCKLOAD?", font=f1, fill=(44, 45, 47))
    d.text((56, 464), "WE'LL COLLECT.", font=f1, fill=(94, 115, 89))
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
    print("shedload built", built)


if __name__ == "__main__":
    main()
