"""Recycle Group Metals lockup: the official Recycle Group wordmark, unchanged, with a copper
METALS tag set beside it on the GROUP baseline. Proposed lockup, for sign-off.

The tag text is Archivo (the Recycle Group site's display face), converted to paths.
Favicon: the Recycle Group site's own favicon (copper R on a dark tile).
"""
import os, re
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.join(os.path.dirname(HERE), "common", "brand")
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "recycle-group-metals", "assets", "brand")
os.makedirs(OUT, exist_ok=True)
COPPER, INK = "#C2804F", "#0E1114"
GROUP_BASELINE, GROUP_CAP, LOGO_RIGHT = 63.0, 20.9, 632.69


def archivo(wght=650):
    f = TTFont(os.path.join(HERE, "fonts", "archivo-latin-wght-normal.woff2"))
    f.flavor = None
    return instancer.instantiateVariableFont(f, {"wght": wght})


def text_path(font, s, size, x, y, track=0.0):
    gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
    sc, pen, bp, cx = size / upm, SVGPathPen(font.getGlyphSet()), BoundsPen(font.getGlyphSet()), 0.0
    for ch in s:
        g = cmap[ord(ch)]
        t = (sc, 0, 0, -sc, x + cx, y)
        gs[g].draw(TransformPen(pen, t))
        gs[g].draw(TransformPen(bp, t))
        cx += gs[g].width * sc + track * size
    return pen.getCommands(), cx - track * size, bp.bounds


def logo_inner(dark_bg):
    s = open(os.path.join(BRAND, "recycle-logo.svg" if dark_bg else "recycle-logo-dark.svg")).read()
    s = re.sub(r"<\?xml[^>]*>", "", s).strip()
    s = re.sub(r"^<svg[^>]*>|</svg>$", "", s).strip()
    return re.sub(r"<title[^>]*>.*?</title>", "", s, flags=re.S)


def lockup(dark_bg=True):
    A = archivo()
    d, tw, b = text_path(A, "METALS", 20, 0, 0, track=0.22)
    size = GROUP_CAP / (b[3] - b[1]) * 20
    d, tw, b = text_path(A, "METALS", size, 0, 0, track=0.22)
    padx, pady, x0 = 12, 9, LOGO_RIGHT + 18
    cap = b[3] - b[1]
    w, h, y0 = tw + 2 * padx, cap + 2 * pady, GROUP_BASELINE - cap - pady
    d, tw, b = text_path(A, "METALS", size, x0 + padx, GROUP_BASELINE, track=0.22)
    W = x0 + w + 2 - 114
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="114 8.97 {W:.2f} 82" width="{W:.2f}" height="82" role="img" aria-label="Recycle Group Metals">'
           f'{logo_inner(dark_bg)}<rect x="{x0:.2f}" y="{y0:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{COPPER}"/>'
           f'<path d="{d}" fill="{INK}"/></svg>')
    name = "lockup-dark-bg.svg" if dark_bg else "lockup-light-bg.svg"
    open(os.path.join(OUT, name), "w").write(svg)
    return round(W, 2), 82


ICON = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='101.8 13.97 72 72'><rect x='101.8' y='13.97' width='72' height='72' rx='10' fill='#0E1114'/>"
        "<g transform='translate(137.8 49.97) scale(1.12) translate(-137.8 -49.97)'><path fill='#C2804F' d='M116 73V26.93H142.76Q147.85 26.93 151.27 28.84Q154.69 30.76 156.4 34.07Q158.11 37.39 158.11 41.48Q158.11 45.91 156.07 49.36Q154.02 52.82 150.33 54.76L159.59 73H146.17L138.53 56.77H128V73ZM128 47.85H140.41Q142.89 47.85 144.4 46.21Q145.91 44.57 145.91 41.82Q145.91 40.01 145.24 38.73Q144.57 37.46 143.36 36.76Q142.15 36.05 140.41 36.05H128Z'/></g></svg>")


def icons():
    open(os.path.join(OUT, "icon.svg"), "w").write(ICON)
    for name, w in [("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512)]:
        cairosvg.svg2png(bytestring=ICON.encode(), write_to=os.path.join(OUT, name), output_width=w, output_height=w)


if __name__ == "__main__":
    print(lockup(True), lockup(False))
    icons()
    sp = "/tmp/claude-0/-home-claude/dd8bbb2f-c6b4-5eca-8d91-f5c9cf325536/scratchpad/"
    cairosvg.svg2png(url=os.path.join(OUT, "lockup-dark-bg.svg"), write_to=sp + "rgm-l1.png", output_height=80, background_color="#0E1114")
    cairosvg.svg2png(url=os.path.join(OUT, "lockup-light-bg.svg"), write_to=sp + "rgm-l2.png", output_height=80, background_color="#ECEFF1")
