"""Crux Metals logo: CRU in heavy slab capitals, with the X made from two steel flat bars
crossed and bolted like cross-bracing, and METALS spaced out underneath.

Crux is the formal name of the Southern Cross. Type is Roboto Slab (variable, 900) and
Source Sans 3 (700), converted to paths so the logo renders the same everywhere.
"""
import math, os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "crux-metals", "assets", "brand")
os.makedirs(OUT, exist_ok=True)

CHAR, BONE, OXIDE, OXIDE_D = "#1E1B19", "#EDE6DA", "#8E3B26", "#A9452E"
_cache = {}


def font(file, wght):
    k = (file, wght)
    if k not in _cache:
        f = TTFont(os.path.join(FONTS, file))
        f.flavor = None
        _cache[k] = instancer.instantiateVariableFont(f, {"wght": wght})
    return _cache[k]


def slab(w=900):
    return font("roboto-slab-latin-wght-normal.woff2", w)


def sans(w=700):
    return font("source-sans-3-latin-wght-normal.woff2", w)


def static_ttf(which, wght):
    """A static TTF instance on disk, for Pillow (og image)."""
    p = f"/tmp/crux-{which}-{wght}.ttf"
    if not os.path.exists(p):
        (slab(wght) if which == "slab" else sans(wght)).save(p)
    return p


def text_path(f, s, size, x=0.0, y=0.0, track=0.0):
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    sc, pen, bp, cx = size / upm, SVGPathPen(f.getGlyphSet()), BoundsPen(f.getGlyphSet()), 0.0
    for ch in s:
        g = cmap[ord(ch)]
        t = (sc, 0, 0, -sc, x + cx, y)
        gs[g].draw(TransformPen(pen, t))
        gs[g].draw(TransformPen(bp, t))
        cx += gs[g].width * sc + track * size
    return pen.getCommands(), cx - track * size, bp.bounds


def cross(x0, yb, w, h, t, bar, bolt, bg):
    """Two flat bars crossed and bolted. x0: left, yb: baseline, w/h: box, t: bar thickness."""
    yt = yb - h
    theta = math.atan2(h, w - t)
    wh = t / math.sin(theta)                      # horizontal width of a bar where it is cut flat
    back = f"M{x0:.2f} {yt:.2f}H{x0 + wh:.2f}L{x0 + w:.2f} {yb:.2f}H{x0 + w - wh:.2f}Z"
    front = f"M{x0:.2f} {yb:.2f}H{x0 + wh:.2f}L{x0 + w:.2f} {yt:.2f}H{x0 + w - wh:.2f}Z"
    cx, cy, r = x0 + w / 2, yb - h / 2, t * 0.36
    return (f'<path d="{back}" fill="{bar}"/>'
            f'<path d="{front}" fill="{bar}" stroke="{bg}" stroke-width="{t * 0.14:.2f}" stroke-linejoin="miter" paint-order="stroke"/>'
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{bolt}" stroke="{bg}" stroke-width="{t * 0.1:.2f}"/>')


def lockup(theme="dark"):
    ink, bar, bg = (BONE, OXIDE_D, CHAR) if theme == "dark" else (CHAR, OXIDE, BONE)
    H = 60.0                                       # cap height of CRU
    f = slab(900)
    d, tw, b = text_path(f, "CRU", 100, 0, 0, track=0.02)
    size = 100 * H / (b[3] - b[1])
    base = H + 2
    d, tw, b = text_path(f, "CRU", size, 0 - 0, base, track=0.02)
    x0 = b[2] + H * 0.08
    xw, t = H * 0.96, H * 0.25
    mark = cross(x0, base, xw, H, t, bar, ink, bg)
    W1 = x0 + xw
    # METALS, spaced to the full width of CRUX
    s = sans(700)
    _, mw, mb = text_path(s, "METALS", 100, 0, 0)
    cap2 = H * 0.3
    msize = 100 * cap2 / (mb[3] - mb[1])
    track = 0.42
    _, mw, mb = text_path(s, "METALS", msize, 0, 0, track=track)
    y2 = base + H * 0.24 + cap2
    mx = b[0] + (W1 - b[0] - mw) / 2
    d2, w2, b2 = text_path(s, "METALS", msize, mx, y2, track=track)
    Wd, Hd = W1 + 2, y2 + 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd:.0f} {Hd:.0f}" width="{Wd:.0f}" height="{Hd:.0f}" role="img" aria-label="Crux Metals">'
           f'<path d="{d}" fill="{ink}"/>{mark}<path d="{d2}" fill="{ink}"/></svg>')
    open(os.path.join(OUT, f"logo-{theme}.svg"), "w").write(svg)
    return round(Wd), round(Hd)


def icons():
    """Square icon: the bolted cross on a charcoal tile."""
    sq = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96">'
          f'<rect width="96" height="96" rx="14" fill="{CHAR}"/>{cross(20, 76, 56, 56, 15, OXIDE_D, BONE, CHAR)}</svg>')
    open(os.path.join(OUT, "icon.svg"), "w").write(sq)
    for name, w in [("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512)]:
        cairosvg.svg2png(bytestring=sq.encode(), write_to=os.path.join(OUT, name), output_width=w, output_height=w)


if __name__ == "__main__":
    print(lockup("dark"), lockup("light"))
    icons()
    sp = "/tmp/claude-0/-home-claude/dd8bbb2f-c6b4-5eca-8d91-f5c9cf325536/scratchpad/"
    cairosvg.svg2png(url=os.path.join(OUT, "logo-dark.svg"), write_to=sp + "crux-d.png", output_height=150, background_color=CHAR)
    cairosvg.svg2png(url=os.path.join(OUT, "logo-light.svg"), write_to=sp + "crux-l.png", output_height=150, background_color=BONE)
    cairosvg.svg2png(url=os.path.join(OUT, "icon.svg"), write_to=sp + "crux-i.png", output_width=128, output_height=128)
    cairosvg.svg2png(url=os.path.join(OUT, "icon.svg"), write_to=sp + "crux-i32.png", output_width=32, output_height=32)
