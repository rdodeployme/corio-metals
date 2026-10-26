"""Recycled Metals logo: a safety-yellow steel nameplate with four rivets reading RECYCLED / METALS
in heavy expanded type, locked up with SINCE / 1955 (the BTT plate, renamed; "By the tonne" dropped 26 Oct).

Type is Saira (variable, wdth 125 / wght 900 and 800), converted to paths so the logo renders
the same everywhere.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
VF = os.path.join(HERE, "fonts", "saira-latin-wdth-normal.woff2")
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "recycled-metals-site" if os.environ.get("RM_STANDALONE") == "1" else "recycled-metals", "assets", "brand")
os.makedirs(OUT, exist_ok=True)
YELLOW, BLACK, WHITE = "#FFD200", "#0E0E0E", "#FFFFFF"
_inst = {}


def font(wght, wdth):
    """A static instance of the variable font (cached)."""
    k = (wght, wdth)
    if k not in _inst:
        f = TTFont(VF)
        f.flavor = None
        _inst[k] = instancer.instantiateVariableFont(f, {"wght": wght, "wdth": wdth})
    return _inst[k]


def static_ttf(wght, wdth):
    """Write a static TTF instance (used by the og image) and return its path."""
    p = f"/tmp/saira-{wght}-{wdth}.ttf"
    if not os.path.exists(p):
        font(wght, wdth).save(p)
    return p


def text_path(f, text, size, x=0.0, y=0.0, tracking=0.0):
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    s = size / upm
    pen, bp, cx = SVGPathPen(gs), BoundsPen(gs), 0.0
    for ch in text:
        g = cmap[ord(ch)]
        t = (s, 0, 0, -s, x + cx, y)
        gs[g].draw(TransformPen(pen, t))
        gs[g].draw(TransformPen(bp, t))
        cx += gs[g].width * s + tracking * size
    return pen.getCommands(), cx - tracking * size, bp.bounds


def plate_path(x, y, w, h, c):
    """A rectangle with 45 degree cut corners, like a stamped steel plate."""
    return (f"M{x + c:.2f} {y:.2f}H{x + w - c:.2f}L{x + w:.2f} {y + c:.2f}V{y + h - c:.2f}"
            f"L{x + w - c:.2f} {y + h:.2f}H{x + c:.2f}L{x:.2f} {y + h - c:.2f}V{y + c:.2f}Z")


def plate(x, y, h, rivets=True, label="BTT", wdth=125, cap=0.62):
    """The nameplate: yellow plate, black letters, optional rivets. Returns (svg, width)."""
    f = font(900, wdth)
    size = h * cap / 0.688                      # Saira cap height is 0.688 em
    d, tw, b = text_path(f, label, size, 0, 0, tracking=0.025)
    padx = h * 0.42 if rivets else h * 0.24
    w = tw + 2 * padx - b[0]
    caph = b[3] - b[1]
    d, tw, b = text_path(f, label, size, x + padx - b[0], y + h / 2 + caph / 2, tracking=0.025)
    s = f'<path d="{plate_path(x, y, w, h, h * 0.16)}" fill="{YELLOW}"/><path d="{d}" fill="{BLACK}"/>'
    if rivets:
        r = h * 0.065
        for cx in (x + padx * 0.47, x + w - padx * 0.47):
            s += f'<circle cx="{cx:.2f}" cy="{y + h / 2:.2f}" r="{r:.2f}" fill="{BLACK}"/>'
    return s, w


def plate2(x, y, h, wdth=125):
    """Two-line nameplate: RECYCLED over METALS, rivets in the four corners. Returns (svg, width)."""
    f = font(900, wdth)
    cap = h * 0.27
    size = cap / 0.688
    d1, w1, b1 = text_path(f, "RECYCLED", size, 0, 0, tracking=0.02)
    d2, w2, b2 = text_path(f, "METALS", size, 0, 0, tracking=0.02)
    tw = max(w1, w2)
    track2 = (tw - w2) / size / 5 + 0.02            # spread METALS to the width of RECYCLED
    padx = h * 0.30
    w = tw + 2 * padx
    gap = h * 0.12
    y1 = y + (h - 2 * cap - gap) / 2 + cap
    y2 = y1 + gap + cap
    d1, _, _ = text_path(f, "RECYCLED", size, x + padx - b1[0], y1, tracking=0.02)
    d2, _, _ = text_path(f, "METALS", size, x + padx - b2[0], y2, tracking=track2)
    s = f'<path d="{plate_path(x, y, w, h, h * 0.13)}" fill="{YELLOW}"/><path d="{d1}" fill="{BLACK}"/><path d="{d2}" fill="{BLACK}"/>'
    r, inset = h * 0.045, h * 0.13
    for cx, cy in ((x + inset, y + inset), (x + w - inset, y + inset), (x + inset, y + h - inset), (x + w - inset, y + h - inset)):
        s += f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{BLACK}"/>'
    return s, w


def lockup(theme="light"):
    ink = BLACK if theme == "light" else WHITE
    H = 60
    mark, mw = plate2(0, 0, H)
    f2 = font(800, 125)
    size = 15.5 / 0.688
    gap_x = 14
    d1, w1, b1 = text_path(f2, "SINCE", size, 0, 0, tracking=0.08)
    caph = b1[3] - b1[1]
    lead = 9
    top = (H - 2 * caph - lead) / 2
    d1, w1, b1 = text_path(f2, "SINCE", size, mw + gap_x, top + caph, tracking=0.08)
    d2, w2, b2 = text_path(f2, "1955", size, mw + gap_x, top + 2 * caph + lead, tracking=0.08)
    W = mw + gap_x + max(w1, w2) + 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H}" width="{W:.0f}" height="{H}" role="img" aria-label="Recycled Metals, since 1955">'
           f'{mark}<path d="{d1}" fill="{ink}"/><path d="{d2}" fill="{ink}"/></svg>')
    open(os.path.join(OUT, f"logo-{theme}.svg"), "w").write(svg)
    return round(W), H


def plate_only():
    mark, mw = plate2(0, 0, 60)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {mw:.0f} 60" width="{mw:.0f}" height="60" role="img" aria-label="Recycled Metals">{mark}</svg>')
    open(os.path.join(OUT, "plate.svg"), "w").write(svg)
    return round(mw), 60


def icons():
    """Square icon: the yellow cut-corner plate with RM, no rivets (they blur at 32 px)."""
    f = font(900, 100)
    size = 40 / 0.688
    d, tw, b = text_path(f, "RM", size, 0, 0, tracking=0.0)
    caph = b[3] - b[1]
    d, tw, b = text_path(f, "RM", size, 48 - tw / 2 - b[0] / 2, 48 + caph / 2, tracking=0.0)
    sq = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96">'
          f'<path d="{plate_path(0, 0, 96, 96, 14)}" fill="{YELLOW}"/><path d="{d}" fill="{BLACK}"/></svg>')
    open(os.path.join(OUT, "icon.svg"), "w").write(sq)
    for name, w in [("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512)]:
        cairosvg.svg2png(bytestring=sq.encode(), write_to=os.path.join(OUT, name), output_width=w, output_height=w)


if __name__ == "__main__":
    print(lockup("light"), lockup("dark"), plate_only())
    icons()
    sp = "/tmp/claude-0/-home-claude/dd8bbb2f-c6b4-5eca-8d91-f5c9cf325536/scratchpad/"
    cairosvg.svg2png(url=os.path.join(OUT, "logo-light.svg"), write_to=sp + "rm-logo.png", output_width=640, background_color="#FFFFFF")
    cairosvg.svg2png(url=os.path.join(OUT, "logo-dark.svg"), write_to=sp + "rm-logo-d.png", output_width=640, background_color="#0E0E0E")
    cairosvg.svg2png(url=os.path.join(OUT, "icon.svg"), write_to=sp + "rm-icon.png", output_width=128, output_height=128)
    cairosvg.svg2png(url=os.path.join(OUT, "icon.svg"), write_to=sp + "rm-icon32.png", output_width=32, output_height=32)
