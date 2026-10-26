"""Service map for Recycled Metals: south-west Victoria, the drop-off at North Geelong and the
towns it covers, drawn as an inline SVG from Natural Earth 10m land and roads (public domain,
clipped into data/sw-vic.json).
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = json.load(open(os.path.join(HERE, "data", "sw-vic.json")))

BASE = ("North Geelong", -38.1012, 144.3426)
# name, lat, lon, label anchor (dx, dy, text-anchor), group
TOWNS = [
    ("Werribee", -37.900, 144.663, (14, 6, "start"), "north"),
    ("Bacchus Marsh", -37.675, 144.438, (14, 6, "start"), "north"),
    ("Ballarat", -37.562, 143.850, (0, -16, "middle"), "north"),
    ("Hamilton", -37.744, 142.022, (0, -16, "middle"), "west"),
    ("Lismore", -37.953, 143.340, (0, -16, "middle"), "west"),
    ("Portland", -38.342, 141.605, (0, 30, "middle"), "west"),
    ("Warrnambool", -38.383, 142.485, (0, 30, "middle"), "west"),
    ("Colac", -38.340, 143.585, (0, -16, "middle"), "west"),
    ("Apollo Bay", -38.759, 143.670, (-14, 6, "end"), "coast"),
    ("Lorne", -38.542, 143.975, (-14, 6, "end"), "coast"),
    ("Torquay", -38.331, 144.326, (-14, 8, "end"), "coast"),
    ("Ocean Grove", -38.264, 144.524, (14, 10, "start"), "coast"),
]
GROUPS = [("north", "North and east"), ("west", "The west"), ("coast", "The coast")]

LON0, LON1, LAT0, LAT1 = 141.35, 145.20, -37.40, -38.95
K = math.cos(math.radians(38.1))
W = 1200
H = round(W * (LAT0 - LAT1) / ((LON1 - LON0) * K))


def xy(lat, lon):
    return ((lon - LON0) / (LON1 - LON0) * W, (LAT0 - lat) / (LAT0 - LAT1) * H)


def ring(coords):
    pts = [xy(lat, lon) for lon, lat in coords]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def line(coords):
    pts = [xy(lat, lon) for lon, lat in coords]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def land_path():
    g = GEO["land"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    return "".join(ring(r) for p in polys for r in p)


def road_paths():
    out = []
    for r in GEO["roads"]:
        if r["type"] not in ("Major Highway", "Secondary Highway"):
            continue
        g = r["g"]
        parts = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]] if g["type"] == "LineString" else []
        d = "".join(line(p) for p in parts)
        if d:
            out.append(f'<path class="rd{" maj" if r["type"] == "Major Highway" else ""}" d="{d}"/>')
    return "".join(out)


def km(a, b):
    R = 6371
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def svg():
    bx, by = xy(BASE[1], BASE[2])
    spokes, dots, labels = [], [], []
    for name, lat, lon, (dx, dy, anc), grp in TOWNS:
        x, y = xy(lat, lon)
        spokes.append(f'<path class="sp" d="M{bx:.1f} {by:.1f}L{x:.1f} {y:.1f}"/>')
        dots.append(f'<circle class="tn" cx="{x:.1f}" cy="{y:.1f}" r="7"/>')
        hide = " sm-hide" if name in ("Torquay", "Ocean Grove", "Lorne", "Bacchus Marsh", "Lismore", "Portland", "Werribee") else ""
        labels.append(f'<text class="lb{hide}" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anc}">{name}</text>')
    # 50 km scale bar, bottom left
    px50 = 50 / (111.32 * K) / (LON1 - LON0) * W
    sx, sy = 40, H - 40
    scale = (f'<g class="scale"><path d="M{sx} {sy}h{px50:.1f}M{sx} {sy - 7}v14M{sx + px50:.1f} {sy - 7}v14"/>'
             f'<text x="{sx}" y="{sy - 16}">50&nbsp;km</text></g>')
    tx, ty = bx - 40, by + 196
    base = (f'<g class="base"><path class="lead" d="M{bx:.1f} {by:.1f}V{ty:.1f}"/><circle cx="{bx:.1f}" cy="{by:.1f}" r="26" class="halo"/>'
            f'<rect x="{bx - 11:.1f}" y="{by - 11:.1f}" width="22" height="22" class="pin"/>'
            f'<g class="btag" transform="translate({tx:.1f} {ty:.1f})"><path d="M0 0h224v62H0z"/>'
            f'<text x="16" y="27" class="t1">Recycled Metals</text><text x="16" y="49" class="t2">Free drop-off · North Geelong</text></g></g>')
    pp = xy(-38.12, 144.87)
    sea = ('<text class="sea" x="330" y="%d">Bass Strait</text><text class="sea" x="%.1f" y="%.1f" text-anchor="middle">Port Phillip</text>'
           % (H - 70, pp[0], pp[1]))
    return (f'<svg class="svmap" viewBox="0 0 {W} {H}" role="img" aria-labelledby="map-t map-d" preserveAspectRatio="xMidYMid meet">'
            f'<title id="map-t">Service map</title>'
            f'<desc id="map-d">A map of south-west Victoria. The free drop-off is at North Geelong, with lines out to '
            + ", ".join(t[0] for t in TOWNS) + '.</desc>'
            f'<rect class="bg" width="{W}" height="{H}"/><path class="land" d="{land_path()}"/>{road_paths()}{sea}'
            + "".join(spokes) + "".join(dots) + "".join(labels) + base + scale + "</svg>")


def town_list():
    out = []
    for g, title in GROUPS:
        names = [t[0] for t in TOWNS if t[4] == g]
        out.append(f'<div><p class="label">{title}</p><ul>' + "".join(f"<li>{n}</li>" for n in names) + "</ul></div>")
    return '<div class="towns">' + "".join(out) + "</div>"


if __name__ == "__main__":
    s = svg()
    print(W, H, len(s))
