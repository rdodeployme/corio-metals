#!/usr/bin/env python3
"""Build Crux Metals (concept 5): a new brand built around Richard's focus.

His own lines, his 766-item collection directory as the home page tool, the group's real
facility photos, credentials and YARTA reporting. Raw steel and red oxide: charcoal, red oxide
and bone, Roboto Slab headings, Source Sans 3 text. Output: crux-metals/ in the repo.
"""
import json, os, re, shutil, datetime, hashlib, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "common"))
import common as C  # noqa: E402

SRC = os.path.join(ROOT, "src")
SITE = os.path.join(C.REPO, "crux-metals")
DEPTH = 1
NAME = "Crux Metals"
SITE_URL = C.SITE_BASE + "crux-metals/"

NAV = [("dropoff", "drop-off.html", "Drop-off"), ("collect", "collections.html", "Collections"),
       ("take", "what-we-collect.html", "What we collect"), ("report", "reporting.html", "Reporting"),
       ("contact", "contact.html", "Contact")]
PAGE_KEY = {"index.html": "home", "drop-off.html": "dropoff", "collections.html": "collect",
            "what-we-collect.html": "take", "reporting.html": "report", "contact.html": "contact"}

CHECK = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2.5 8.5l3.5 3.5 7.5-8" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
CROSS = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 3.5l9 9M12.5 3.5l-9 9" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
SEARCH = '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.75" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M13 13l4.5 4.5" stroke="currentColor" stroke-width="1.6"/></svg>'

# Gate fees that match directory items (Recycle North Geelong price list, via common.py)
FEE_SHORT = {"gas": "Gate fee $15 or $25", "ext": "Gate fee $10 or $15", "n2o": "Gate fee $20", "solar": "Gate fee $39"}


def _ver():
    h = hashlib.sha1()
    for f in (os.path.join(SRC, "css", "main.css"), os.path.join(SRC, "js", "main.js")):
        h.update(open(f, "rb").read())
    return h.hexdigest()[:8]


VER = _ver()


# ---------------------------------------------------------------- directory data (Richard's list)
def clean_note(s):
    s = re.sub(r"(\w+) asbestos-free", r"\1 with no asbestos", s)
    s = s.replace("asbestos-free", "no asbestos").replace("PCB-free", "no PCBs")
    return s


def fee_for(name):
    n = name.lower()
    if re.search(r"\blpg\b|barbecue gas bottle", n):
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
        c["title"] = c["title"].replace(" ", " ")
        c["note"] = clean_note(c.get("note", ""))
        for it in c["items"]:
            it["note"] = clean_note(it["note"])
            it["fee"] = fee_for(it["n"])
            it["spec"] = "Specialist" in it["tags"]
    return cats


DIR = load_directory()
TOTAL = sum(len(c["items"]) for c in DIR)
assert TOTAL == 766, TOTAL


def dir_json():
    cats = [{"id": c["id"], "n": c["num"], "t": c["title"], "c": len(c["items"])} for c in DIR]
    items = [[i, it["n"], it["note"], 1 if it["spec"] else 0, it["fee"]] for i, c in enumerate(DIR) for it in c["items"]]
    return json.dumps({"cats": cats, "items": items, "fees": FEE_SHORT}, separators=(",", ":"), ensure_ascii=False)


def nb_last(t):
    """Glue the last two words so a short word never sits alone on a line."""
    i = t.rfind(" ")
    return t if i < 0 else t[:i] + "&nbsp;" + t[i + 1:]


def item_li(it):
    """One directory item. The last word travels with the first tag, so a tag never sits alone on a line."""
    tags = (['<span class="tag">Specialist</span>'] if it["spec"] else []) + \
           ([f'<span class="fee">{FEE_SHORT[it["fee"]]}</span>'] if it["fee"] else [])
    rest = "".join(" " + t for t in tags[1:])
    name = C.esc(it["n"])
    if it["note"]:
        note = C.esc(it["note"])
        k = note.rfind(" ")
        head, last = (note[:k + 1], note[k + 1:]) if k > -1 else ("", note)
        tail = f'<span class="nw">{last})' + (f"&nbsp;{tags[0]}" if tags else "") + "</span>" + rest
        return f'<li>{name} <small>({head}</small><small>{tail}</small></li>'
    k = name.rfind(" ")
    head, last = (name[:k + 1], name[k + 1:]) if k > -1 else ("", name)
    if tags:
        return f'<li>{head}<span class="nw">{last}&nbsp;{tags[0]}</span>{rest}</li>'
    return f'<li>{head}<span class="nw">{last}</span></li>' if head else f'<li>{name}</li>'


def directory():
    out = []
    for c in DIR:
        note = f'<p class="note">{C.esc(c["note"])}</p>' if c["note"] else ""
        lis = "".join(item_li(it) for it in c["items"])
        out.append(f'<details id="{c["id"]}"><summary><span class="n">{c["num"]}</span>'
                   f'<span class="t"><b>{C.esc(c["title"])}</b><span>{C.esc(c["desc"])}</span></span>'
                   f'<span class="c">{len(c["items"])} items</span></summary>{note}<ul>{lis}</ul></details>')
    return '<div class="dir" id="dir">' + "".join(out) + "</div>"


def dir_chips():
    return "".join(f'<a href="#{c["id"]}">{C.esc(short_title(c["title"]))}</a>' for c in DIR)


SHORT = {"councils": "Councils", "transfer-stations": "Transfer stations", "residential": "Residential", "roads": "State roads",
         "health": "Health and aged care", "education": "Education", "offices": "Offices", "whitegoods": "Retail and whitegoods",
         "warehousing": "Warehousing", "industry": "Industry", "trades": "Trades", "rural": "Rural and farming",
         "hospitality": "Hospitality", "solar": "Solar", "ports": "Airports and ports"}


def short_title(t):
    for c in DIR:
        if c["title"] == t:
            return SHORT.get(c["id"], t)
    return t


def sectors():
    return '<div class="secs">' + "".join(
        f'<a href="what-we-collect.html#{c["id"]}"><i>{c["num"]}</i><b>{C.esc(c["title"]).replace(" &amp; ", "&nbsp;&amp; ")}</b><em>{len(c["items"])}</em></a>'
        for c in DIR) + "</div>"


def finder():
    chips = "".join(f'<button type="button" data-cat="{i}" aria-pressed="false">{SHORT[c["id"]]}</button>' for i, c in enumerate(DIR))
    fees = "".join(f"<li><span>{a}</span><span>{short_fee(b)}</span></li>" for a, b, _ in C.GATE_FEES)
    return f'''<div class="finder" id="finder-ui">
  <div>
    <div class="f-search">{SEARCH}<label class="sr" for="f-q">Search what we collect</label>
      <input id="f-q" type="search" placeholder="Search {TOTAL} items, e.g. fridge, racking, guardrail" data-short="Search {TOTAL} items, e.g. racking" autocomplete="off" enterkeyhint="search"></div>
    <div class="f-meta"><span id="f-count" aria-live="polite">{TOTAL} items across {len(DIR)} categories</span><button type="button" id="f-clear" hidden>Clear</button></div>
    <div class="chips" role="group" aria-label="Categories">{chips}</div>
    <div class="f-out" id="f-out"></div>
  </div>
  <aside class="route" aria-label="Getting it to us">
    <p class="eyebrow">Getting it to us</p>
    <dl>
      <div><dt>Under a tonne</dt><dd>Drop it off at {C.STREET}, North&nbsp;Geelong. Clean scrap metal is no charge at the&nbsp;gate.</dd></div>
      <div><dt>A tonne or more</dt><dd>We collect it. One service fee, quoted before we&nbsp;come.</dd></div>
      <div><dt>Handling fees at the gate</dt><dd><ul class="fees">{fees}</ul></dd></div>
    </dl>
    <div class="actions"><a class="btn btn-solid" href="collections.html#book">Book a collection</a><a class="btn btn-line" href="drop-off.html">Drop-off</a></div>
  </aside>
</div>
<noscript><p class="fine" style="margin-top:20px">Search needs JavaScript. <a href="what-we-collect.html">See the full list of {TOTAL} items</a>.</p></noscript>
<script>window.CRUX_DIR={dir_json()};</script>'''


def short_fee(b):
    return {"$15 under 9 kg, $25 over 9 kg": "$15 / $25", "$10 under 3 kg, $15 over 3 kg": "$10 / $15"}.get(b, b.replace(" each", ""))


def gate_guide():
    free = "".join(f'<tr class="nc"><td class="it"><b>{a}</b><small>{b}</small></td><td class="v">No charge</td></tr>' for a, b in C.GATE_NO_CHARGE)
    fees = "".join(f'<tr><td class="it"><b>{a}</b>{f"<small>{c}</small>" if c else ""}</td><td class="v">{b}</td></tr>' for a, b, c in C.GATE_FEES)
    return (f'<table class="gate"><thead><tr><th scope="col">Item</th><th scope="col">At the gate</th></tr></thead><tbody>{free}{fees}</tbody></table>'
            f'<p class="fine" style="margin-top:14px">{C.FEES_NOTE} <a href="{C.PRICE_LIST_URL}" target="_blank" rel="noopener">Recycle North Geelong price&nbsp;list</a></p>')


def cant_take():
    return '<ul class="cant">' + "".join(f"<li>{CROSS}<span>{x}</span></li>" for x in C.CANT_TAKE) + "</ul>"


def docket():
    return f'''<figure class="docket">
  <div class="dk" role="img" aria-label="Sample weighbridge docket: date, customer, site, material, then gross, tare and net weight">
    <div class="dk-head"><img src="assets/brand/logo-light.svg" alt="" width="85" height="34"><span>Weighbridge docket</span></div>
    <dl class="dk-rows">
      <div><dt>Docket</dt><dd>No. 000000</dd></div>
      <div><dt>Date</dt><dd>DD / MM / YYYY</dd></div>
      <div><dt>Customer</dt><dd>Your organisation</dd></div>
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


# ---------------------------------------------------------------- layout
def header(nav_key):
    links = (f'<a class="m-only" href="./"{" aria-current=page" if nav_key == "home" else ""}>Home</a>' +
             "".join(f'<a href="{h}"{" aria-current=page" if k == nav_key else ""}>{l}</a>' for k, h, l in NAV) +
             f'<a class="m-only m-cta" href="tel:{C.PHONE_TEL}">Call {C.CONTACT_NAME} {C.PHONE}</a>')
    return f'''<a class="sr skip" href="#main">Skip to content</a>
<div class="rg"><div class="wrap"><span>A Recycle Group business <img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="91" height="14"></span><span class="r">{C.HOURS_SHORT} at 116 Furner Avenue · <a href="tel:{C.PHONE_TEL}">{C.PHONE}</a></span></div></div>
<header class="hdr"><div class="wrap">
  <a class="brand" href="./" aria-label="{NAME} home"><img src="assets/brand/logo-dark.svg" alt="{NAME}" width="241" height="96"></a>
  <nav class="nav" id="nav" aria-label="Main">{links}</nav>
  <a class="btn btn-solid nav-cta" href="collections.html#book">Book a collection</a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav" aria-label="Menu"><span></span></button>
</div></header>'''


def footer():
    year = datetime.date.today().year
    pages = "".join(f'<li><a href="{h}">{l}</a></li>' for _, h, l in NAV)
    return f'''<footer class="ft"><div class="wrap">
  <div class="ft-top">
    <img class="ft-logo" src="assets/brand/logo-dark.svg" alt="{NAME}" width="241" height="96">
    <p class="ft-line"><span class="nw">All metals collected.</span> <span class="nw">Every resource valued.</span></p>
  </div>
  <div class="ft-grid">
    <div><h2>Drop-off</h2><ul><li>{C.FACILITY}</li><li>{C.STREET}</li><li>North Geelong VIC&nbsp;3215</li><li>{C.HOURS_DAYS}</li></ul></div>
    <div><h2>Collections</h2><ul><li>From one tonne</li><li>{C.CONTACT_FULL}</li><li><a href="tel:{C.PHONE_TEL}">{C.PHONE}</a></li><li><a href="mailto:{C.EMAIL}">{C.EMAIL}</a></li></ul></div>
    <div><h2>Pages</h2><ul><li><a href="./">Home</a></li>{pages}</ul></div>
    <div><h2>Backed by Recycle Group</h2><ul><li>EPA Victoria R000312600</li><li>ISO 9001, 14001 and 45001</li><li>Reporting through YARTA</li></ul></div>
  </div>
  <div class="ft-base"><img src="assets/brand/recycle-logo.svg" alt="Recycle Group" width="124" height="19"><p>{C.rg_business(NAME)} · {C.RG_LINE}</p><p>&copy; {year} {NAME}</p></div>
</div></footer>'''


def page(fname):
    raw = open(os.path.join(SRC, "pages", fname)).read()
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", raw[: raw.index("-->")], re.M))
    body = raw[raw.index("-->") + 3:].strip()
    map_iframe = f'<iframe title="Map: {C.ADDRESS}" loading="lazy" referrerpolicy="no-referrer" src="{C.MAP_EMBED}"></iframe>'
    for key, val in {
        "{{FINDER}}": finder() if "{{FINDER}}" in body else "", "{{DIRECTORY}}": directory() if "{{DIRECTORY}}" in body else "",
        "{{DIR_CHIPS}}": dir_chips(), "{{SECTORS}}": sectors(), "{{DOCKET}}": docket(),
        "{{GATE_GUIDE}}": gate_guide(), "{{CANT_TAKE}}": cant_take(), "{{CHECK}}": CHECK, "{{SEARCH}}": SEARCH,
        "{{TOTAL}}": str(TOTAL), "{{CATS}}": str(len(DIR)),
        "{{PHONE}}": C.PHONE.replace(" ", "&nbsp;"), "{{PHONE_TEL}}": C.PHONE_TEL, "{{EMAIL}}": C.EMAIL,
        "{{CONTACT}}": C.CONTACT_NAME, "{{CONTACT_FULL}}": C.CONTACT_FULL, "{{FACILITY}}": C.FACILITY,
        "{{STREET}}": C.STREET, "{{SUBURB}}": C.SUBURB, "{{ADDRESS}}": C.ADDRESS.replace("VIC 3215", "VIC&nbsp;3215"),
        "{{HOURS}}": C.HOURS_DAYS, "{{HOURS_NOTE}}": C.HOURS_NOTE, "{{MAPS_DIR}}": C.MAPS_DIR,
        "{{MAP}}": map_iframe, "{{YARTA}}": C.YARTA_LINE, "{{CANT_SHORT}}": C.CANT_TAKE_SHORT,
    }.items():
        body = body.replace(key, val)
    assert "{{" not in body, f"unfilled placeholder in {fname}: {re.findall(r'{{[A-Z_:a-z]+}}', body)}"
    body = C.glue(body)
    url = SITE_URL + ("" if fname == "index.html" else fname)
    schema = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": NAME,
              "parentOrganization": {"@type": "Organization", "name": "Recycle Group"}, "slogan": "All metals collected. Every resource valued.",
              "description": "Scrap metal drop-off at Recycle North Geelong, 116 Furner Avenue, and collections from one tonne. One service fee, quoted before we come. A weighbridge docket for every load.",
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
<meta name="theme-color" content="#1E1B19">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{meta["title"]}"><meta property="og:description" content="{meta["description"]}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="assets/brand/icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/roboto-slab-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/source-sans-3-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/main.css?v={VER}">
{C.review_script(DEPTH)}
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body data-concept="crux" data-page="{PAGE_KEY.get(fname, "home")}">
{header(meta.get("nav", ""))}
<main id="main">
{body}
</main>
{footer()}
<script>window.CRUX={{phone:"{C.PHONE_TEL}",contact:"{C.CONTACT_NAME}"}};</script>
<script src="assets/js/main.js?v={VER}" defer></script>
</body>
</html>
'''
    C.check(html, "crux-metals/" + fname)
    open(os.path.join(SITE, fname), "w").write(html)
    return fname


def _ttf(woff2, wght=None):
    from fontTools.ttLib import TTFont
    out = os.path.join("/tmp", os.path.basename(woff2).replace(".woff2", f"-{wght or 0}.ttf"))
    if not os.path.exists(out):
        f = TTFont(woff2)
        f.flavor = None
        if wght:
            from fontTools.varLib import instancer
            f = instancer.instantiateVariableFont(f, {"wght": wght})
        f.save(out)
    return out


def og_image():
    from PIL import Image, ImageDraw, ImageFont
    import cairosvg, io
    sys.path.insert(0, ROOT)
    import logo as L
    W, H = 1200, 630
    ph = Image.open(os.path.join(SITE, "assets/img/bales-forklift.webp")).convert("RGB")
    s = max(W / ph.width, H / ph.height)
    ph = ph.resize((int(ph.width * s), int(ph.height * s)))
    left = int((ph.width - W) * 0.65)
    ph = ph.crop((left, (ph.height - H) // 2, left + W, (ph.height - H) // 2 + H))
    shade = Image.new("L", (W, H))
    shade.putdata([int(max(30, 240 - x * 0.26)) for x in range(W)] * H)
    char = Image.new("RGB", (W, H), (30, 27, 25))
    bg = Image.composite(char, ph, shade)
    logo = cairosvg.svg2png(url=os.path.join(SITE, "assets/brand/logo-dark.svg"), output_height=92)
    lg = Image.open(io.BytesIO(logo)).convert("RGBA")
    bg.paste(lg, (56, 50), lg)
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(L.static_ttf("slab", 800), 66)
    f2 = ImageFont.truetype(L.static_ttf("sans", 700), 22)
    d.text((56, 250), "All metals collected.", font=f1, fill=(237, 230, 218))
    tb = d.textbbox((56, 336), "Every resource valued.", font=f1)
    d.rectangle((tb[0] - 12, tb[1] - 12, tb[2] + 12, tb[3] + 14), fill=(142, 59, 38))
    d.text((56, 336), "Every resource valued.", font=f1, fill=(237, 230, 218))
    d.rectangle((0, H - 10, W, H), fill=(142, 59, 38))
    d.text((56, 486), "DROP-OFF AT 116 FURNER AVENUE · COLLECTIONS FROM ONE TONNE", font=f2, fill=(220, 212, 200))
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
    print("crux metals built", built)


if __name__ == "__main__":
    main()
