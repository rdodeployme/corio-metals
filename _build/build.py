#!/usr/bin/env python3
"""Build the Corio Metals static site: src/pages/*.html -> repo root.

Corio Metals: public scrap metal drop-off at 116 Furner Avenue, North Geelong,
and commercial collections from one tonne.
"""
import json, os, re, shutil, datetime, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC, SITE = os.path.join(ROOT, "src"), os.path.dirname(ROOT)  # _build/ -> repo root
SITE_URL = "https://rdodeployme.github.io/corio-metals/"

# ---- contact and site details (change here, then rebuild) ----
NAME = "Corio Metals"
CONTACT = "Nigel"
CONTACT_FULL = "Nigel Taylor"
PHONE, PHONE_TEL, EMAIL = "0427 888 222", "0427888222", "nigel@recycle.net.au"
STREET, SUBURB, POSTCODE = "116 Furner Avenue", "North Geelong", "3215"
ADDRESS = f"{STREET}, {SUBURB} VIC {POSTCODE}"
LAT, LON = -38.1012, 144.3426  # Furner Avenue (street, from OpenStreetMap)
# Gate hours are not confirmed yet. When they are, set HOURS (e.g. "7am to 4pm, Monday to Friday").
HOURS = None
HOURS_SHORT = HOURS or "Call ahead for gate hours"
MIN_TONNES = 1  # commercial collections start at this many tonnes

MAPS_DIR = "https://www.google.com/maps/dir/?api=1&destination=116+Furner+Avenue%2C+North+Geelong+VIC+3215"
MAP_IFRAME = (
    '<iframe title="Map: 116 Furner Avenue, North Geelong" loading="lazy" referrerpolicy="no-referrer" '
    'src="https://www.openstreetmap.org/export/embed.html?bbox=144.322%2C-38.112%2C144.364%2C-38.090&amp;layer=mapnik&amp;marker=-38.1012%2C144.3426"></iframe>'
    f'<a class="map-open btn btn-amber" href="{MAPS_DIR}" target="_blank" rel="noopener">Open in Google Maps</a>'
)

NAV = [("drop", "drop-off.html", "Drop off"), ("prices", "prices.html", "Prices"), ("collect", "collections.html", "Collections"),
       ("take", "what-we-take.html", "What we take"), ("contact", "contact.html", "Contact")]

PHONE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.6a1 1 0 0 1-.25 1z"/></svg>'
PIN_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>'


def _ver():
    h = hashlib.sha1()
    for f in (os.path.join(SRC, "css", "main.css"), os.path.join(SRC, "js", "main.js")):
        h.update(open(f, "rb").read())
    return h.hexdigest()[:8]


VER = _ver()
PRICES = json.load(open(os.path.join(ROOT, "data", "prices.json")))


def price_board():
    fams = PRICES["families"]
    tabs = "".join(
        f'<button type="button" role="tab" id="pt-{f["key"]}" aria-controls="pp-{f["key"]}" aria-selected="{"true" if i == 0 else "false"}">'
        f'<i style="background:{f["colour"]}"></i>{f["name"]}</button>' for i, f in enumerate(fams)
    ) + '<button type="button" role="tab" id="pt-fees" aria-controls="pp-fees" aria-selected="false"><i class="fee-dot"></i>Handling fees</button>'
    panes = ""
    for i, f in enumerate(fams):
        rows = "".join(
            f'<div class="grade"><div><b>{n}</b><small>{d}</small></div>'
            f'<div class="price" data-rate="{gid}"><a class="call-rate" href="tel:{PHONE_TEL}">Call</a></div></div>'
            for gid, n, d in f["grades"]
        )
        panes += f'<div class="grades" role="tabpanel" id="pp-{f["key"]}" aria-labelledby="pt-{f["key"]}"{"" if i == 0 else " hidden"}>{rows}</div>'
    rows = "".join(
        f'<div class="grade"><div><b>{n}</b><small>{d}</small></div>'
        f'<div class="price" data-fee="{fid}"><span class="quoted">Quoted</span></div></div>'
        for fid, n, d in PRICES["fees"]
    )
    panes += f'<div class="grades" role="tabpanel" id="pp-fees" aria-labelledby="pt-fees" hidden>{rows}</div>'
    return (
        '<div class="board">'
        '<div class="board-top"><div class="live" id="rates-stamp"><i></i><span>Rates per kg for clean, sorted metal</span></div>'
        f'<div class="mtabs" role="tablist" aria-label="Metal">{tabs}</div></div>'
        f'{panes}'
        '<div class="board-foot"><p>Clean, sorted metal gets the best rate. Mixed or dirty loads are graded on the scale, '
        'and the final price is set when it\'s weighed.</p>'
        '<a class="btn btn-amber" href="prices.html#estimate">Estimate my load</a></div>'
        "</div>"
    )


def estimator_rows():
    out = ""
    for f in PRICES["families"]:
        opts = "".join(f'<option value="{gid}">{n}</option>' for gid, n, d in f["grades"])
        out += (
            f'<div class="mrow" data-family="{f["key"]}">'
            f'<span class="sw" style="background:{f["colour"]}"></span>'
            f'<div class="mrow-main"><b>{f["name"]}</b>'
            f'<label class="sr" for="g-{f["key"]}">{f["name"]} grade</label><select id="g-{f["key"]}" class="mgrade">{opts}</select></div>'
            f'<div class="kg"><button type="button" class="kg-minus" aria-label="10 kg less {f["name"].lower()}">−</button>'
            f'<label class="sr" for="kg-{f["key"]}">{f["name"]} kilos</label>'
            f'<input id="kg-{f["key"]}" class="kg-in" type="number" inputmode="numeric" min="0" step="10" value="0">'
            f'<span class="kg-u">kg</span>'
            f'<button type="button" class="kg-plus" aria-label="10 kg more {f["name"].lower()}">+</button></div>'
            "</div>"
        )
    return out


# ---------------------------------------------------------------- layout
def header(nav_key):
    links = (f'<a class="m-only" href="./"{" aria-current=page" if nav_key == "home" else ""}>Home</a>' + "".join(
        f'<a href="{href}"{" aria-current=page" if key == nav_key else ""}>{label}</a>' for key, href, label in NAV
    ) + f'<div class="nav-extra"><a class="btn btn-amber" href="tel:{PHONE_TEL}">{PHONE_SVG}Call {CONTACT} {PHONE}</a>'
        f'<a class="btn btn-line" style="color:#F2EFE9" href="collections.html#quote">Book a collection</a>'
        f'<p>{STREET}, {SUBURB}</p></div>')
    return f'''<a class="sr" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
  <a class="brand" href="./" aria-label="{NAME} home"><img src="assets/brand/logo-dark.svg" alt="{NAME}" width="186" height="80"></a>
  <nav class="nav" id="nav" aria-label="Main">{links}</nav>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
  <div class="top-call"><a class="btn btn-amber" href="tel:{PHONE_TEL}">{PHONE_SVG}<span>Call<span class="long"> {PHONE}</span></span></a></div>
</div></header>'''


def footer():
    year = datetime.date.today().year
    pages = "".join(f'<li><a href="{h}">{l}</a></li>' for _, h, l in NAV)
    return f'''<div class="hazard thin"></div>
<footer class="foot"><div class="wrap">
  <div class="foot-grid">
    <div><img src="assets/brand/logo-dark.svg" alt="{NAME}" width="186" height="80"><p style="margin:0;max-width:34ch">Scrap metal recycling in Geelong. Drop it off at Furner Avenue, or book a collection for a tonne or&nbsp;more.</p></div>
    <div><h4>Drop off</h4><ul><li>{STREET}</li><li>{SUBURB} VIC&nbsp;{POSTCODE}</li><li>{HOURS_SHORT}</li><li><a href="{MAPS_DIR}" target="_blank" rel="noopener">Directions</a></li></ul></div>
    <div><h4>Talk to us</h4><ul><li>{CONTACT_FULL}</li><li><a href="tel:{PHONE_TEL}">{PHONE}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="collections.html#quote">Book a collection</a></li></ul></div>
    <div><h4>Pages</h4><ul><li><a href="./">Home</a></li>{pages}</ul></div>
  </div>
  <div class="legal"><p>Victorian law bans cash for scrap metal. Any payment is by bank transfer and we record your name, address and&nbsp;ID.</p><p>&copy; {year} {NAME}</p></div>
</div></footer>
<div class="callbar"><a class="btn btn-amber" href="tel:{PHONE_TEL}">{PHONE_SVG}Call</a><a class="btn btn-line" style="color:#F2EFE9" href="{MAPS_DIR}" target="_blank" rel="noopener">{PIN_SVG}Directions</a></div>'''


def glue(html):
    """Keep the last two words of short text blocks together (clean-line-breaks)."""
    return re.sub(r"(?<=[^\s>])[ ]+([^\s<>]{1,12}</(?:p|h3|li|dd|figcaption|summary)>)", " \\1", html)


def page(fname):
    raw = open(os.path.join(SRC, "pages", fname)).read()
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", raw[: raw.index("-->")], re.M))
    body = raw[raw.index("-->") + 3 :].strip()
    for key, val in {
        "{{PRICE_BOARD}}": price_board(), "{{EST_ROWS}}": estimator_rows(),
        "{{PHONE}}": PHONE.replace(" ", "&nbsp;"), "{{PHONE_TEL}}": PHONE_TEL, "{{EMAIL}}": EMAIL,
        "{{CONTACT}}": CONTACT, "{{CONTACT_FULL}}": CONTACT_FULL,
        "{{STREET}}": STREET, "{{SUBURB}}": SUBURB, "{{ADDRESS}}": ADDRESS.replace("VIC 3215", "VIC&nbsp;3215"),
        "{{HOURS}}": HOURS_SHORT,
        "{{MAPS_DIR}}": MAPS_DIR, "{{MAP_IFRAME}}": MAP_IFRAME,
    }.items():
        body = body.replace(key, val)
    assert "{{" not in body, f"unfilled placeholder in {fname}"
    body = glue(body)
    url = SITE_URL + ("" if fname == "index.html" else fname)
    schema = {
        "@context": "https://schema.org", "@type": "RecyclingCenter", "name": NAME,
        "description": "Scrap metal drop-off in North Geelong and commercial scrap metal collections from one tonne.",
        "url": SITE_URL, "telephone": "+61" + PHONE_TEL[1:], "email": EMAIL,
        "address": {"@type": "PostalAddress", "streetAddress": STREET, "addressLocality": SUBURB,
                    "addressRegion": "VIC", "postalCode": POSTCODE, "addressCountry": "AU"},
        "geo": {"@type": "GeoCoordinates", "latitude": LAT, "longitude": LON},
        "areaServed": "Geelong and Victoria", "image": SITE_URL + "og.jpg",
    }
    scripts = '<script src="assets/js/rates.js" defer></script>\n' if fname in ("prices.html", "index.html") else ""
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
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body>
{header(meta.get("nav", ""))}
<main id="main">
{body}
</main>
{footer()}
{scripts}<script>window.CM={{phone:"{PHONE_TEL}",minKg:{MIN_TONNES*1000},maps:"{MAPS_DIR}"}};</script>
<script src="assets/js/main.js?v={VER}" defer></script>
</body>
</html>
'''
    assert "—" not in html and "&mdash;" not in html, f"em dash in {fname}"
    assert not re.search(r"\bfree\b", re.sub(r"<[^>]+>", " ", html), re.I), f"'free' in {fname}"
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
    # rates.js is edited by hand on the live site: only seed it, never overwrite
    rates_out = os.path.join(SITE, "assets", "js", "rates.js")
    if not os.path.exists(rates_out):
        shutil.copy(os.path.join(SRC, "js", "rates.js"), rates_out)
    built = [page(f) for f in sorted(os.listdir(os.path.join(SRC, "pages"))) if f.endswith(".html")]
    today = datetime.date.today().isoformat()
    open(os.path.join(SITE, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE_URL}{'' if f == 'index.html' else f}</loc><lastmod>{today}</lastmod></url>\n" for f in built if f != "404.html")
        + "</urlset>\n")
    open(os.path.join(SITE, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n")
    open(os.path.join(SITE, ".nojekyll"), "w").write("")
    og_image()
    print("built", built)


if __name__ == "__main__":
    main()
