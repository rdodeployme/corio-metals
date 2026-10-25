"""Shedload logo: a corrugated-iron shed with its doors open, and SHEDLOAD in stencil capitals.

Colours are Colorbond-style: Monument (charcoal), Pale Eucalypt (green) and Paperbark (cream).
Text is converted to paths so the logo renders the same everywhere.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "shedload", "assets", "brand")
os.makedirs(OUT, exist_ok=True)
MONUMENT, EUC, PAPER = "#2C2D2F", "#7C9177", "#EAE3D2"
_f = {}


def text_path(fname, text, size, x=0.0, y=0.0, tracking=0.0):
    if fname not in _f:
        _f[fname] = TTFont(os.path.join(FONTS, fname))
    f = _f[fname]
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


def shed(x, y, w, h, body, door, ribs):
    """Gable shed, corrugated (vertical ribs), double doors open showing a dark interior."""
    eave = y + h * 0.36
    roof = f"M{x:.2f} {eave:.2f} L{x + w / 2:.2f} {y:.2f} L{x + w:.2f} {eave:.2f} V{y + h:.2f} H{x:.2f} Z"
    # ribs: thin vertical knock-out lines across the front
    rib_paths = ""
    n = 9
    for i in range(1, n):
        rx = x + w * i / n
        # top of the rib follows the gable line
        top = y + (h * 0.36) * abs(rx - (x + w / 2)) / (w / 2) + 3.5
        rib_paths += f"M{rx - .7:.2f} {top:.2f} h1.4 V{y + h:.2f} h-1.4 Z "
    dw, dh = w * 0.42, h * 0.5
    dx, dy = x + (w - dw) / 2, y + h - dh
    door_p = f"M{dx:.2f} {dy:.2f} h{dw:.2f} v{dh:.2f} h{-dw:.2f} Z"
    return (f'<path d="{roof}" fill="{body}"/>'
            f'<path d="{rib_paths}" fill="{ribs}" opacity=".55"/>'
            f'<path d="{door_p}" fill="{door}"/>')


def lockup(theme="light"):
    ink = MONUMENT if theme == "light" else PAPER
    door = EUC
    ribs = PAPER if theme == "light" else MONUMENT
    H = 56
    mark = shed(0, 2, 64, H - 2, ink, door, ribs)
    d, w, b = text_path("big-shoulders-stencil-display-latin-900-normal.woff2", "SHEDLOAD", 64, 0, 0, tracking=0.015)
    # sit the caps on the shed's base line, cap height equal to the shed height
    capH = b[3] - b[1]
    scale = (H - 2) / capH
    size = 64 * scale
    d, w, b = text_path("big-shoulders-stencil-display-latin-900-normal.woff2", "SHEDLOAD", size, 0, 0, tracking=0.015)
    tx = 64 + 14
    ty = H - b[3]
    d, w, b = text_path("big-shoulders-stencil-display-latin-900-normal.woff2", "SHEDLOAD", size, tx, ty, tracking=0.015)
    W = tx + w + 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H}" role="img" aria-label="Shedload">'
           f'{mark}<path d="{d}" fill="{ink}"/></svg>')
    open(os.path.join(OUT, f"logo-{theme}.svg"), "w").write(svg)
    return W, H


def icons():
    sq = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect width="96" height="96" rx="16" fill="{PAPER}"/>'
          f'{shed(14, 16, 68, 62, MONUMENT, EUC, PAPER)}</svg>')
    open(os.path.join(OUT, "icon.svg"), "w").write(sq)
    for name, w in [("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512)]:
        cairosvg.svg2png(bytestring=sq.encode(), write_to=os.path.join(OUT, name), output_width=w, output_height=w)


if __name__ == "__main__":
    print(lockup("light"), lockup("dark"))
    icons()
    sp = "/tmp/claude-0/-home-claude/dd8bbb2f-c6b4-5eca-8d91-f5c9cf325536/scratchpad/"
    cairosvg.svg2png(url=os.path.join(OUT, "logo-light.svg"), write_to=sp + "shed-logo.png", output_width=600, background_color=PAPER)
    cairosvg.svg2png(url=os.path.join(OUT, "logo-dark.svg"), write_to=sp + "shed-logo-d.png", output_width=600, background_color=MONUMENT)
    cairosvg.svg2png(url=os.path.join(OUT, "icon.svg"), write_to=sp + "shed-icon.png", output_width=128, output_height=128)
