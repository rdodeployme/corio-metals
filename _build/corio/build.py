#!/usr/bin/env python3
"""Build Corio Metals (concept 1): src/pages/*.html -> repo root.

Public drop-off at Recycle North Geelong, 116 Furner Avenue (clean scrap metal is no charge),
and commercial collections from one tonne (one service fee, quoted first).
"""
import json, os, re, shutil, datetime, hashlib, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "common"))
import common as C  # noqa: E402

SRC = os.path.join(ROOT, "src")
SITE = C.REPO                      # Corio is the root of the repo
DEPTH = 0
NAME = "Corio Metals"
SITE_URL = C.SITE_BASE

NAV = [("drop", "drop-off.html", "Drop off"), ("collect", "collections.html", "Collections"),
       ("take", "what-we-take.html", "What we take"), ("load", "load-check.html", "Load check"),
       ("contact", "contact.html", "Contact")]
PAGE_KEY = {"index.html": "home", "drop-off.html": "dropoff", "collections.html": "collect",
            "what-we-take.html": "take", "load-check.html": "load", "contact.html": "contact"}

PHONE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.6a1 1 0 0 1-.25 1z"/></svg>'
PIN_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>'

MAP_IFRAME = (f'<iframe title="Map: {C.ADDRESS}" loading="lazy" referrerpolicy="no-referrer" src="{C.MAP_EMBED}"></iframe>'
              f'<a class="map-open btn btn-amber" href="{C.MAPS_DIR}" target="_blank" rel="noopener">Open in Google Maps</a>')


def _ver():
    h = hashlib.sha1()
    for f in (os.path.join(SRC, "css", "main.css"), os.path.join(SRC, "js", "main.js")):
        h.update(open(f, "rb").read())
    return h.hexdigest()[:8]


VER = _ver()

# ---------------------------------------------------------------- components
GROUP_TABS = [g for g in C.GROUPS if g[0] != "cant"]
TAG = {"ok": ("ok", "No charge"), "prep": ("prep", "Prep first"), "fee": ("fee", "Fee"), "call": ("call", "Call first")}


def load_check():
    tabs = "".join(
        f'<button type="button" role="tab" id="lt-{k}" aria-controls="lp-{k}" aria-selected="{"true" if i == 0 else "false"}">{n}</button>'
        for i, (k, n) in enumerate(GROUP_TABS))
    panes = ""
    for i, (k, n) in enumerate(GROUP_TABS):
        rows, n = "", 0
        for iid, name, grp, kg, st, note, icon in C.ITEMS:
            if grp != k:
                continue
            n += 1
            cls, lab = TAG[st]
            tag = f'<span class="tag t-{cls}">{lab}</span>' if st != "ok" else '<span class="tag-gap"></span>'
            small = f"about {kg:,}&nbsp;kg" + (f" · {note}" if note and st != "ok" else "")
            rows += (f'<div class="lrow{" more" if n > 8 else ""}" data-id="{iid}" data-kg="{kg}" data-st="{st}" data-name="{C.esc(name)}" data-note="{C.esc(note)}">'
                     f'<div class="lrow-main"><b>{name}</b><small>{small}</small></div>{tag}'
                     f'<div class="kg"><button type="button" class="lc-minus" aria-label="One less {C.esc(name.lower())}">−</button>'
                     f'<input class="lc-n" type="number" inputmode="numeric" min="0" step="1" value="0" aria-label="How many: {C.esc(name)}">'
                     f'<button type="button" class="lc-plus" aria-label="One more {C.esc(name.lower())}">+</button></div></div>')
        more = f'<button type="button" class="lc-more">Show {n - 8} more</button>' if n > 8 else ""
        panes += f'<div class="lrows" role="tabpanel" id="lp-{k}" aria-labelledby="lt-{k}"{"" if i == 0 else " hidden"}>{rows}{more}</div>'
    return f'''<div class="lc" id="lc">
  <div class="lc-in">
    <div class="lbl-row"><span class="lc-h">What have you got?</span><button type="button" class="est-clear" id="lc-clear">Clear all</button></div>
    <div class="ltabs" role="tablist" aria-label="Item type">{tabs}</div>
    {panes}
    <p class="small lc-foot">Everything here is no charge unless it's tagged. Weights are a rough guide for typical items. Asbestos, chemicals and full or hired gas cylinders can't come in at&nbsp;all.</p>
  </div>
  <div class="lc-out" aria-live="polite"><div class="lc-out-in">
    <p class="eyebrow">Your load</p>
    <div class="lc-val" id="lc-val">0&nbsp;kg</div>
    <div class="lc-cap" id="lc-cap">Add a few items to get started</div>
    <div class="meter" id="lc-meter" aria-hidden="true"><div class="meter-bar"><i></i></div><div class="meter-lab"><span>Drop off</span><span class="mid">1 tonne</span><span>We collect</span></div></div>
    <p class="lc-verdict" id="lc-verdict">Under a tonne, drop it off. A tonne or more, we collect.</p>
    <ul class="lc-lines" id="lc-lines"></ul>
    <div class="lc-gate" id="lc-gate"><span>At the gate</span><b id="lc-cost">No charge</b></div>
    <div class="btns lc-cta" id="lc-cta"></div>
  </div></div>
</div>'''


def gate_guide(dark=True):
    free = "".join(f'<li><b>{a}</b><span>{b}</span><em class="t-ok">No charge</em></li>' for a, b in C.GATE_NO_CHARGE)
    fees = "".join(f'<li><b>{a}</b><span>{c}</span><em class="t-fee">{b}</em></li>' for a, b, c in C.GATE_FEES)
    return (f'<div class="gate{" gate-dark" if dark else ""}"><ul class="gate-list">{free}{fees}</ul>'
            f'<p class="small gate-note">{C.FEES_NOTE} <a href="{C.PRICE_LIST_URL}" target="_blank" rel="noopener">Recycle North Geelong price&nbsp;list</a></p></div>')


def cant_take():
    return "".join(f"<li>{x}</li>" for x in C.CANT_TAKE)


# ---------------------------------------------------------------- layout
def header(nav_key):
    links = (f'<a class="m-only" href="./"{" aria-current=page" if nav_key == "home" else ""}>Home</a>' + "".join(
        f'<a href="{href}"{" aria-current=page" if key == nav_key else ""}>{label}</a>' for key, href, label in NAV
    ) + f'<div class="nav-extra"><a class="btn btn-amber" href="tel:{C.PHONE_TEL}">{PHONE_SVG}Call {C.CONTACT_NAME} {C.PHONE}</a>'
        f'<a class="btn btn-line" style="color:#F2EFE9" href="collections.html#quote">Book a collection</a>'
        f'<p>{C.FACILITY}, {C.STREET}</p></div>')
    return f'''<a class="sr" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
  <a class="brand" href="./" aria-label="{NAME} home"><img src="assets/brand/logo-dark.svg" alt="{NAME}" width="186" height="80"></a>
  <nav class="nav" id="nav" aria-label="Main">{links}</nav>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
  <div class="top-call"><a class="btn btn-amber" href="tel:{C.PHONE_TEL}">{PHONE_SVG}<span>Call<span class="long"> {C.PHONE}</span></span></a></div>
</div></header>'''


def footer():
    year = datetime.date.today().year
    pages = "".join(f'<li><a href="{h}">{l}</a></li>' for _, h, l in NAV)
    return f'''<div class="hazard thin"></div>
<footer class="foot"><div class="wrap">
  <div class="foot-grid">
    <div><img src="assets/brand/logo-dark.svg" alt="{NAME}" width="186" height="80"><p style="margin:0;max-width:34ch">Scrap metal in Geelong. Drop it off at Furner Avenue, or book a collection for a tonne or&nbsp;more.</p></div>
    <div><h4>Drop off</h4><ul><li>{C.FACILITY}</li><li>{C.STREET}</li><li>{C.SUBURB} {C.STATE}&nbsp;{C.POSTCODE}</li><li>{C.HOURS_DAYS}</li><li><a href="{C.MAPS_DIR}" target="_blank" rel="noopener">Directions</a></li></ul></div>
    <div><h4>Talk to us</h4><ul><li>{C.CONTACT_FULL}</li><li><a href="tel:{C.PHONE_TEL}">{C.PHONE}</a></li><li><a href="mailto:{C.EMAIL}">{C.EMAIL}</a></li><li><a href="collections.html#quote">Book a collection</a></li></ul></div>
    <div><h4>Pages</h4><ul><li><a href="./">Home</a></li>{pages}</ul></div>
  </div>
  <div class="legal rg-legal"><span class="rg-mark"><img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="130" height="21"></span><p>{C.rg_business(NAME)} · {C.RG_LINE}</p><p>&copy; {year} {NAME}</p></div>
</div></footer>
<div class="callbar"><a class="btn btn-amber" href="tel:{C.PHONE_TEL}">{PHONE_SVG}Call</a><a class="btn btn-line" style="color:#F2EFE9" href="{C.MAPS_DIR}" target="_blank" rel="noopener">{PIN_SVG}Directions</a></div>'''


def page(fname):
    raw = open(os.path.join(SRC, "pages", fname)).read()
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", raw[: raw.index("-->")], re.M))
    body = raw[raw.index("-->") + 3:].strip()
    for key, val in {
        "{{LOAD_CHECK}}": load_check(), "{{GATE_GUIDE}}": gate_guide(True), "{{GATE_GUIDE_LIGHT}}": gate_guide(False),
        "{{CANT_TAKE}}": cant_take(), "{{CANT_SHORT}}": C.CANT_TAKE_SHORT,
        "{{PHONE}}": C.PHONE.replace(" ", "&nbsp;"), "{{PHONE_TEL}}": C.PHONE_TEL, "{{EMAIL}}": C.EMAIL,
        "{{CONTACT}}": C.CONTACT_NAME, "{{CONTACT_FULL}}": C.CONTACT_FULL, "{{FACILITY}}": C.FACILITY,
        "{{STREET}}": C.STREET, "{{SUBURB}}": C.SUBURB, "{{ADDRESS}}": C.ADDRESS.replace("VIC 3215", "VIC&nbsp;3215"),
        "{{HOURS}}": C.HOURS_DAYS, "{{HOURS_NOTE}}": C.HOURS_NOTE,
        "{{MAPS_DIR}}": C.MAPS_DIR, "{{MAP_IFRAME}}": MAP_IFRAME, "{{YARTA}}": C.YARTA_LINE,
        "{{PRICE_LIST_URL}}": C.PRICE_LIST_URL,
    }.items():
        body = body.replace(key, val)
    assert "{{" not in body, f"unfilled placeholder in {fname}: {re.findall(r'{{[A-Z_]+}}', body)}"
    body = C.glue(body)
    url = SITE_URL + ("" if fname == "index.html" else fname)
    schema = {
        "@context": "https://schema.org", "@type": "RecyclingCenter", "name": NAME,
        "description": "Scrap metal drop-off at Recycle North Geelong and commercial scrap metal collections from one tonne.",
        "url": SITE_URL, "telephone": C.PHONE_INTL, "email": C.EMAIL,
        "address": {"@type": "PostalAddress", "streetAddress": C.STREET, "addressLocality": C.SUBURB,
                    "addressRegion": C.STATE, "postalCode": C.POSTCODE, "addressCountry": "AU"},
        "geo": {"@type": "GeoCoordinates", "latitude": C.LAT, "longitude": C.LON},
        "areaServed": "Geelong and Victoria", "image": SITE_URL + "og.jpg",
    }
    items = f'<script>window.CM_ITEMS={C.items_json()};</script>\n' if "{{" not in body and 'id="lc"' in body else ""
    html = f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta["title"]}</title>
<meta name="description" content="{meta["description"]}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#111417">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{meta["title"]}"><meta property="og:description" content="{meta["description"]}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="assets/brand/icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/anton-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/main.css?v={VER}">
{C.review_script(DEPTH)}
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body data-concept="corio" data-page="{PAGE_KEY.get(fname, "home")}">
{header(meta.get("nav", ""))}
<main id="main">
{body}
</main>
{footer()}
{items}<script>window.CM={{phone:"{C.PHONE_TEL}",minKg:{C.MIN_KG},maps:"{C.MAPS_DIR}"}};</script>
<script src="assets/js/main.js?v={VER}" defer></script>
</body>
</html>
'''
    C.check(html, fname)
    open(os.path.join(SITE, fname), "w").write(html)
    return fname


def og_image():
    from PIL import Image, ImageDraw, ImageFont
    import cairosvg, io
    W, H = 1200, 630
    bg = Image.open(os.path.join(SITE, "assets/img/hero-dropoff.webp")).convert("RGB")
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s), int(bg.height * s)))
    x0 = bg.width - W
    bg = bg.crop((x0, (bg.height - H) // 2, x0 + W, (bg.height - H) // 2 + H))
    grad = Image.linear_gradient("L").rotate(90).resize((W, H)).point(lambda v: int(v * 0.93))
    bg = Image.composite(Image.new("RGB", (W, H), (17, 20, 23)), bg, grad)
    logo = cairosvg.svg2png(url=os.path.join(SITE, "assets/brand/logo-dark.svg"), output_width=420)
    lg = Image.open(io.BytesIO(logo)).convert("RGBA")
    bg.paste(lg, (60, 56), lg)
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(os.path.join(ROOT, "fonts", "Anton-Regular.ttf"), 76)
    f2 = ImageFont.truetype(os.path.join(ROOT, "fonts", "BarlowCondensed-Bold.ttf"), 38)
    d.text((60, 300), "DROP IT OFF.", font=f1, fill=(242, 239, 233))
    d.text((60, 390), "OR WE'LL COLLECT IT.", font=f1, fill=(227, 138, 69))
    d.text((60, 500), "SCRAP METAL · 116 FURNER AVE, NORTH GEELONG", font=f2, fill=(242, 239, 233))
    d.rectangle([0, H - 14, W, H], fill=(227, 138, 69))
    bg.save(os.path.join(SITE, "og.jpg"), quality=86)


def main():
    os.makedirs(os.path.join(SITE, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "assets", "js"), exist_ok=True)
    shutil.copy(os.path.join(SRC, "css", "main.css"), os.path.join(SITE, "assets", "css", "main.css"))
    shutil.copy(os.path.join(SRC, "js", "main.js"), os.path.join(SITE, "assets", "js", "main.js"))
    C.copy_rg_logos(os.path.join(SITE, "assets", "brand"))
    for old in ("assets/js/rates.js", "assets/js/towns.js"):
        p = os.path.join(SITE, old)
        if os.path.exists(p):
            os.remove(p)
    built = [page(f) for f in sorted(os.listdir(os.path.join(SRC, "pages"))) if f.endswith(".html")]
    # the old prices page now points at the load check
    open(os.path.join(SITE, "prices.html"), "w").write(
        '<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>Load check | Corio Metals</title>'
        '<meta http-equiv="refresh" content="0; url=load-check.html"><link rel="canonical" href="' + SITE_URL + 'load-check.html">'
        '</head><body><p><a href="load-check.html">Load check</a></p></body></html>\n')
    og_image()
    print("corio built", built)
    return built


if __name__ == "__main__":
    main()
