"""By The Tonne logo: a cast-iron counterweight stamped 1T, with a stacked wordmark.

"BY THE" in IBM Plex Mono over "Tonne" in Instrument Serif. Everything is converted to paths
so the logo renders the same everywhere.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "by-the-tonne", "assets", "brand")
os.makedirs(OUT, exist_ok=True)
BLACK, WHITE = "#0E0E0E", "#FFFFFF"
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


def weight(x, y, h, fill, knock):
    """A counterweight: ring handle on a tapered body, '1T' knocked out of the body."""
    w_top, w_bot = h * 0.52, h * 0.92
    top, bot = y + h * 0.30, y + h
    cx = x + w_bot / 2
    r = h * 0.035  # corner rounding
    body = (f"M{cx - w_top / 2 + r:.2f} {top:.2f} L{cx + w_top / 2 - r:.2f} {top:.2f} "
            f"Q{cx + w_top / 2:.2f} {top:.2f} {cx + w_top / 2 + r * .4:.2f} {top + r:.2f} "
            f"L{cx + w_bot / 2:.2f} {bot - r:.2f} Q{cx + w_bot / 2:.2f} {bot:.2f} {cx + w_bot / 2 - r:.2f} {bot:.2f} "
            f"L{cx - w_bot / 2 + r:.2f} {bot:.2f} Q{cx - w_bot / 2:.2f} {bot:.2f} {cx - w_bot / 2:.2f} {bot - r:.2f} "
            f"L{cx - w_top / 2 - r * .4:.2f} {top + r:.2f} Q{cx - w_top / 2:.2f} {top:.2f} {cx - w_top / 2 + r:.2f} {top:.2f} Z")
    # ring handle
    ro, ri = h * 0.15, h * 0.085
    hy = y + ro
    ring = (f"M{cx - ro:.2f} {hy:.2f} a{ro:.2f} {ro:.2f} 0 1 0 {2 * ro:.2f} 0 a{ro:.2f} {ro:.2f} 0 1 0 {-2 * ro:.2f} 0 Z "
            f"M{cx - ri:.2f} {hy:.2f} a{ri:.2f} {ri:.2f} 0 1 1 {2 * ri:.2f} 0 a{ri:.2f} {ri:.2f} 0 1 1 {-2 * ri:.2f} 0 Z")
    neck = f"M{cx - h * .06:.2f} {hy + ro * .7:.2f} h{h * .12:.2f} V{top + 1:.2f} h{-h * .12:.2f} Z"
    # 1T label
    d, tw, b = text_path("ibm-plex-mono-latin-600-normal.woff2", "1T", h * 0.30, 0, 0, tracking=-0.04)
    tx = cx - tw / 2
    ty = top + (bot - top) * 0.62 - (b[1] + b[3]) / 2 + (b[3] - b[1]) / 2 * 0  # baseline guess, centred below
    d, tw, b = text_path("ibm-plex-mono-latin-600-normal.woff2", "1T", h * 0.30, tx, 0, tracking=-0.04)
    mid = top + (bot - top) * 0.56
    ty = mid - (b[1] + b[3]) / 2
    d, tw, b = text_path("ibm-plex-mono-latin-600-normal.woff2", "1T", h * 0.30, tx, ty, tracking=-0.04)
    return (f'<path d="{ring}" fill="{fill}" fill-rule="evenodd"/><path d="{neck}" fill="{fill}"/>'
            f'<path d="{body}" fill="{fill}"/><path d="{d}" fill="{knock}"/>'), w_bot


def lockup(theme="light"):
    ink = BLACK if theme == "light" else WHITE
    knock = WHITE if theme == "light" else BLACK
    H = 60
    mark, mw = weight(0, 0, H, ink, knock)
    tx = mw + 14
    # BY THE (mono, tracked) over Tonne (serif)
    d1, w1, b1 = text_path("ibm-plex-mono-latin-500-normal.woff2", "BY THE", 12.5, 0, 0, tracking=0.22)
    d2, w2, b2 = text_path("instrument-serif-latin-400-normal.woff2", "Tonne", 50, 0, 0, tracking=-0.01)
    y1 = 6 - b1[1]
    d1, w1, b1 = text_path("ibm-plex-mono-latin-500-normal.woff2", "BY THE", 12.5, tx + 2, y1, tracking=0.22)
    y2 = H - b2[3] + 0
    d2, w2, b2 = text_path("instrument-serif-latin-400-normal.woff2", "Tonne", 50, tx - 1, H, tracking=-0.01)
    W = max(tx + 2 + w1, tx - 1 + w2) + 4
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H + 1:.0f}" role="img" aria-label="By The Tonne">'
           f'{mark}<path d="{d1}" fill="{ink}"/><path d="{d2}" fill="{ink}"/></svg>')
    open(os.path.join(OUT, f"logo-{theme}.svg"), "w").write(svg)
    return W, H


def icons():
    mark, mw = weight(13, 9, 78, BLACK, WHITE)
    sq = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect width="96" height="96" rx="14" fill="{WHITE}"/>'
          f'{mark}</svg>')
    open(os.path.join(OUT, "icon.svg"), "w").write(sq)
    for name, w in [("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512)]:
        cairosvg.svg2png(bytestring=sq.encode(), write_to=os.path.join(OUT, name), output_width=w, output_height=w)


if __name__ == "__main__":
    print(lockup("light"), lockup("dark"))
    icons()
    sp = "/tmp/claude-0/-home-claude/dd8bbb2f-c6b4-5eca-8d91-f5c9cf325536/scratchpad/"
    cairosvg.svg2png(url=os.path.join(OUT, "logo-light.svg"), write_to=sp + "btt-logo.png", output_width=640, background_color="#FFFFFF")
    cairosvg.svg2png(url=os.path.join(OUT, "logo-dark.svg"), write_to=sp + "btt-logo-d.png", output_width=640, background_color="#0E0E0E")
    cairosvg.svg2png(url=os.path.join(OUT, "icon.svg"), write_to=sp + "btt-icon.png", output_width=128, output_height=128)
