"""Shared facts, data and checks for the four metal-site concepts.

One source of truth for the offer, contact, gate fees, can't-take list and item weights,
so every concept says the same thing. Concept builds import this module.
"""
import json, os, re, html as _html

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)            # _build/
REPO = os.path.dirname(BUILD)            # repo root (Corio lives here)
SITE_BASE = "https://rdodeployme.github.io/corio-metals/"

# ---------------------------------------------------------------- contact
CONTACT_NAME = "Nigel"
CONTACT_FULL = "Nigel Taylor"
PHONE, PHONE_TEL, EMAIL = "0427 888 222", "0427888222", "nigel@recycle.net.au"
PHONE_INTL = "+61427888222"

# ---------------------------------------------------------------- the drop-off
FACILITY = "Recycle North Geelong"
STREET, SUBURB, STATE, POSTCODE = "116 Furner Avenue", "North Geelong", "VIC", "3215"
ADDRESS = f"{STREET}, {SUBURB} {STATE} {POSTCODE}"
LAT, LON = -38.1012, 144.3426
# Group fact: open six days a week. Exact gate times not confirmed (sources differ).
HOURS_DAYS = "Monday to Saturday"
HOURS_SHORT = "Mon to Sat"
HOURS_NOTE = "Call for gate times"
MAPS_DIR = "https://www.google.com/maps/dir/?api=1&destination=116+Furner+Avenue%2C+North+Geelong+VIC+3215"
MAP_EMBED = ("https://www.openstreetmap.org/export/embed.html?bbox=144.322%2C-38.112%2C144.364%2C-38.090"
             "&amp;layer=mapnik&amp;marker=-38.1012%2C144.3426")
PRICE_LIST_URL = "https://recycle.net.au/price-list/"

MIN_TONNES = 1
MIN_KG = 1000

RG_LINE = "Responsible recovery. Sustainable outcomes."
YARTA_LINE = "Environmental reporting through YARTA Environmental Sustainability, a Recycle Group initiative."


def rg_business(brand):
    return f"{brand} is a Recycle Group business"


# What costs nothing at the gate (Recycle North Geelong price list, verified Jun 2026)
GATE_NO_CHARGE = [
    ("Clean scrap metal", "Every type of metal, sorted from your rubbish"),
    ("Whitegoods", "Fridges, freezers, washers, dryers and ovens"),
    ("Car batteries", "Tape the terminals"),
    ("Steel bikes", "Whole or in pieces"),
]
# Items with a handling fee (same price list)
GATE_FEES = [
    ("Gas bottles", "$15 under 9 kg, $25 over 9 kg", "Empty and customer-owned"),
    ("Fire extinguishers", "$10 under 3 kg, $15 over 3 kg", "Fully discharged"),
    ("Nitrous canisters", "$20 each", "Over 0.5 kg or 2 L"),
    ("Solar panels", "$39 each", ""),
    ("Tyres on rims", "$25 each", "Rims with the tyre off are scrap metal"),
]
FEES_NOTE = ("Fees as listed on Recycle North Geelong's price list. Anything in your load that "
             "isn't metal goes through the transfer station at its usual rate.")

CANT_TAKE = [
    "Asbestos, or anything that might contain it",
    "Chemicals, prescribed and hazardous waste",
    "Full, charged or hired gas cylinders",
    "Firearms, ammunition and explosives",
    "Clinical waste, sharps and radioactive material",
    "Anything still holding fuel, oil or liquid",
]
CANT_TAKE_SHORT = "Asbestos, chemicals and hazardous waste, full or hired gas cylinders, firearms and explosives, clinical waste, and anything still holding fuel or oil."

# ---------------------------------------------------------------- items (rough guide weights)
# status: ok = no charge; prep = no charge once prepared; fee = handling fee; call = call first; no = can't take
GROUPS = [("home", "Household"), ("trade", "Trade & building"), ("biz", "Business & bulk"),
          ("vehicle", "Vehicles & machinery"), ("cant", "Can't take")]
ITEMS = [
    # id, name, group, kg, status, note, icon
    ("fridge", "Fridge or freezer", "home", 70, "ok", "Whitegoods are no charge.", "fridge"),
    ("washer", "Washing machine", "home", 65, "ok", "Whitegoods are no charge.", "washer"),
    ("bbq", "BBQ", "home", 45, "prep", "Take the gas bottle off.", "bbq"),
    ("bike", "Bike", "home", 13, "ok", "Steel bikes are no charge.", "bike"),
    ("hws", "Hot water unit", "home", 60, "prep", "Drain it first.", "hws"),
    ("mower", "Lawn mower", "home", 30, "prep", "Fuel and oil drained.", "mower"),
    ("gas", "Gas bottle", "home", 10, "fee", "$15 under 9 kg, $25 over. Empty, customer-owned.", "gas"),
    ("battery", "Car battery", "home", 15, "ok", "Tape the terminals.", "battery"),
    ("dryer", "Clothes dryer", "home", 35, "ok", "Whitegoods are no charge.", "dryer"),
    ("oven", "Oven or stove", "home", 50, "ok", "Whitegoods are no charge.", "oven"),
    ("tramp", "Trampoline frame", "home", 50, "prep", "Mat, net and padding off.", "tramp"),
    ("setting", "Outdoor setting", "home", 25, "ok", "Metal frames. Timber and cushions off.", "setting"),
    ("filing", "Filing cabinet", "home", 50, "ok", "Empty it first.", "filing"),
    ("bedframe", "Metal bed frame", "home", 25, "ok", "Mattress off.", "bed"),
    ("shelving", "Steel shelving", "home", 25, "ok", "", "shelving"),
    ("pots", "Box of pots, pans and cutlery", "home", 10, "ok", "", "pots"),
    ("ext", "Fire extinguisher", "home", 5, "fee", "$10 under 3 kg, $15 over. Discharged.", "ext"),
    ("roofing", "Roofing iron (sheet)", "trade", 7, "ok", "", "roofing"),
    ("offcuts", "Steel offcuts (barrow)", "trade", 80, "ok", "", "offcuts"),
    ("copper", "Copper pipe (bag)", "trade", 10, "ok", "", "pipe"),
    ("cable", "Cable (bag)", "trade", 15, "ok", "", "cable"),
    ("gutter", "Gutter and downpipe", "trade", 15, "ok", "", "gutter"),
    ("fence", "Steel fence panel", "trade", 25, "ok", "", "fence"),
    ("pickets", "Star pickets (10)", "trade", 35, "ok", "", "pickets"),
    ("mesh", "Reo mesh sheet", "trade", 60, "ok", "", "mesh"),
    ("window", "Aluminium window frame", "trade", 8, "ok", "Glass out if you can.", "window"),
    ("racking", "Pallet racking (one bay)", "biz", 80, "ok", "", "racking"),
    ("locker", "Steel locker", "biz", 35, "ok", "", "locker"),
    ("desk", "Steel desk frame", "biz", 25, "ok", "", "desk"),
    ("cage", "Roll cage", "biz", 45, "ok", "", "cage"),
    ("bench", "Stainless bench", "biz", 40, "ok", "", "bench"),
    ("server", "Server rack", "biz", 90, "prep", "Drives removed or wiped first.", "server"),
    ("motor", "Electric motor", "biz", 30, "ok", "", "motor"),
    ("solar", "Solar panel", "biz", 20, "fee", "$39 each.", "solar"),
    ("rims", "Wheel rim, tyre off", "vehicle", 10, "ok", "With the tyre on it's $25.", "rim"),
    ("radiator", "Car radiator", "vehicle", 8, "ok", "", "radiator"),
    ("engine", "Engine block", "vehicle", 150, "prep", "Fuel and oil drained.", "engine"),
    ("car", "Car body", "vehicle", 1000, "call", "Call first.", "car"),
    ("asbestos", "Asbestos", "cant", 0, "no", "We can't take it.", "asbestos"),
    ("chem", "Chemicals", "cant", 0, "no", "We can't take them.", "chem"),
    ("fullgas", "Full or hired gas cylinder", "cant", 0, "no", "Return hired cylinders to the supplier.", "fullgas"),
]
STATUS_LABEL = {"ok": "No charge", "prep": "No charge, prep first", "fee": "Fee", "call": "Call first", "no": "Can't take"}

# Loads for the load scale (rough guide)
LOADS = [
    ("bucket", "Bucket", 10, "A few offcuts, a box of pots and cutlery"),
    ("boot", "Car boot", 60, "A BBQ, a bike, a mower"),
    ("ute", "Ute tray", 400, "Gutter, fence posts, a hot water unit"),
    ("trailer", "Trailer", 600, "A garage clean-out: whitegoods, frames, roofing iron"),
    ("shed", "Shedload", 900, "The whole back shed, sorted from the rubbish"),
    ("truck", "Truckload", 3000, "A strip-out, a farm clean-up, a site's offcuts"),
    ("site", "Site full", 10000, "Racking from a warehouse, a demolition, a depot clear-out"),
]


def items_json():
    keys = ("id", "name", "group", "kg", "status", "note", "icon")
    return json.dumps([dict(zip(keys, it)) for it in ITEMS], separators=(",", ":"))


# ---------------------------------------------------------------- page helpers
def esc(s):
    return _html.escape(s, quote=True)


def glue(html):
    """Keep the last two words of short text blocks together (clean-line-breaks)."""
    return re.sub(r"(?<=[^\s>])[ ]+([^\s<>]{1,12}</(?:p|h3|li|dd|figcaption|summary)>)", " \\1", html)


BANNED = [
    (r"—|&mdash;", "em dash"),
    (r"\bfree\b", "the word 'free'"),
    (r"get paid|we pay you|bank transfer|photo ID|price board|/kg\b|per kg|per kilo", "payment wording"),
]


def check(html, fname):
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    for pat, what in BANNED:
        m = re.search(pat, text if what != "em dash" else html, re.I)
        if m:
            ctx = text[max(0, m.start() - 60): m.end() + 60] if what != "em dash" else ""
            raise SystemExit(f"BUILD FAILED: {what} in {fname}: ...{ctx}...")


def review_script(depth):
    """The concept switcher, shared by every page. depth = folders below the repo root."""
    up = "../" * depth
    return (f'<link rel="stylesheet" href="{up}review/switcher.css?v={asset_ver("review/switcher.css")}">'
            f'<script src="{up}review/switcher.js?v={asset_ver("review/switcher.js")}" defer></script>')


def asset_ver(rel):
    import hashlib
    p = os.path.join(HERE, rel)
    return hashlib.sha1(open(p, "rb").read()).hexdigest()[:8] if os.path.exists(p) else "0"


def rg_logo_svg(dark_bg=True):
    """Official Recycle Group wordmark (from the Recycle Group site)."""
    f = "recycle-logo.svg" if dark_bg else "recycle-logo-dark.svg"
    s = open(os.path.join(HERE, "brand", f)).read()
    s = re.sub(r"<\?xml[^>]*>", "", s)
    return s.strip()


def copy_rg_logos(dest_dir):
    import shutil
    os.makedirs(dest_dir, exist_ok=True)
    for f in ("recycle-logo.svg", "recycle-logo-dark.svg"):
        shutil.copy(os.path.join(HERE, "brand", f), os.path.join(dest_dir, f))
