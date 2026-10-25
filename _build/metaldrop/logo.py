"""The Metal Drop logo: a red hex nut + "the metal / drop" set in Rubik, as pure paths."""
import os, math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "the-metal-drop", "assets", "brand")
os.makedirs(OUT, exist_ok=True)
INK, RED, WHITE = "#1B1D20", "#D52B1E", "#FFFFFF"
_f = {}


def text_path(fname, text, size, x=0, y=0, tracking=0.0):
    if fname not in _f:
        _f[fname] = TTFont(os.path.join(FONTS, fname))
    f = _f[fname]
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    s = size / upm
    pen, bp, cx = SVGPathPen(gs), BoundsPen(gs), 0.0
    for ch in text:
        g = cmap[ord(ch)]
        t = (s, 0, 0, -s, x + cx, y)
        gs[g].draw(TransformPen(pen, t)); gs[g].draw(TransformPen(bp, t))
        cx += gs[g].width * s + tracking * size
    return pen.getCommands(), cx - tracking * size, bp.bounds


def nut(cx, cy, r, col):
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    hexp = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"
    h = r * 0.46
    hole = f"M{cx - h:.2f} {cy:.2f} a{h:.2f} {h:.2f} 0 1 0 {2 * h:.2f} 0 a{h:.2f} {h:.2f} 0 1 0 {-2 * h:.2f} 0 Z"
    # small chamfer ring for a machined look
    return f'<path d="{hexp} {hole}" fill="{col}" fill-rule="evenodd"/>'


def lockup(theme="light"):
    word = INK if theme == "light" else WHITE
    R = 40
    mark = nut(R + 2, R + 4, R, RED)
    tx = 2 * R + 22
    d1, w1, b1 = text_path("rubik-latin-600-normal.woff2", "the metal", 34, 0, 0, tracking=-0.01)
    y1 = 6 - b1[1]
    d1, w1, b1 = text_path("rubik-latin-600-normal.woff2", "the metal", 34, tx, y1, tracking=-0.01)
    d2, w2, b2 = text_path("rubik-latin-800-normal.woff2", "drop", 64, 0, 0, tracking=-0.03)
    y2 = b1[3] + 2 - b2[1]
    d2, w2, b2 = text_path("rubik-latin-800-normal.woff2", "drop", 64, tx - 2, y2, tracking=-0.03)
    W = max(tx + w1, tx + w2) + 6
    H = max(b2[3] + 6, 2 * R + 10)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="The Metal Drop">'
           f'{mark}<path d="{d1}" fill="{word}"/><path d="{d2}" fill="{RED}"/></svg>')
    open(os.path.join(OUT, f"logo-{theme}.svg"), "w").write(svg)
    return W, H


def icons():
    sq = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect width="96" height="96" rx="22" fill="{WHITE}"/>'
          f'{nut(48, 48, 36, RED)}</svg>')
    open(os.path.join(OUT, "icon.svg"), "w").write(sq)
    for name, w in [("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512)]:
        cairosvg.svg2png(bytestring=sq.encode(), write_to=os.path.join(OUT, name), output_width=w)


if __name__ == "__main__":
    print(lockup("light"), lockup("dark"))
    icons()
    cairosvg.svg2png(url=os.path.join(OUT, "logo-light.svg"), write_to="/tmp/claude-0/-home-claude/dd8bbb2f-c6b4-5eca-8d91-f5c9cf325536/scratchpad/md-logo.png", output_width=700, background_color="#F6F5F1")
