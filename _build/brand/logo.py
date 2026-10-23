"""Corio Metals logo set: scrap-bin mark + CORIO / METALS wordmark with hazard stripes.

Pure-path SVGs (no font dependency) written to ../../assets/brand/, plus PNG favicons.
Run: python3 _build/brand/logo.py
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "..", "..", "assets", "brand")
os.makedirs(OUT, exist_ok=True)

INK, BONE, COPPER, STEEL = "#111417", "#F2EFE9", "#E38A45", "#5B656E"
ANTON = "Anton-Regular.ttf"
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


def bin_icon(col=COPPER, scrap=BONE):
    """Open hook-lift scrap bin, loaded, side on. viewBox 0 0 140 120."""
    # scrap standing out of the top: two I-beams and a length of pipe
    def ibeam(x, y, L, ang):
        return (f'<g transform="translate({x} {y}) rotate({ang})">'
                f'<rect x="0" y="-7" width="{L}" height="14" fill="{scrap}"/>'
                f'<rect x="3" y="-2.5" width="{L-6}" height="5" fill="{INK}" opacity=".55"/></g>')
    load = (
        ibeam(18, 60, 62, -38)
        + ibeam(54, 60, 58, -62)
        + f'<path d="M78 58 L104 22" stroke="{scrap}" stroke-width="10" stroke-linecap="round"/>'
        + f'<circle cx="104" cy="22" r="5" fill="{INK}"/>'
    )
    body = (
        f'<path d="M4 54 L112 54 L112 104 L22 104 L4 86 Z" fill="{col}"/>'      # bin body, sloped tail
        f'<rect x="0" y="50" width="116" height="8" rx="2" fill="{col}"/>'      # top rail
        + "".join(f'<rect x="{x}" y="62" width="6" height="36" fill="{INK}" opacity=".3"/>' for x in (30, 52, 74, 96))
        + f'<path d="M112 104 L112 40 L122 40 L136 104 Z" fill="{col}"/>'        # hook A-frame
        f'<circle cx="117" cy="32" r="8" fill="none" stroke="{scrap}" stroke-width="5"/>'  # lifting hook ring
        f'<rect x="10" y="104" width="122" height="6" fill="{scrap}"/>'          # long rail
        f'<circle cx="18" cy="112" r="5" fill="{scrap}"/>'                       # rear roller
    )
    return load + body


def lockup(theme="dark"):
    word = BONE if theme == "dark" else INK
    icon = bin_icon(COPPER, word)
    tx = 162
    d1, w1, b1 = text_path(ANTON, "CORIO", 104, 0, 0, tracking=0.03)
    y1 = 16 - b1[1]
    d1, w1, b1 = text_path(ANTON, "CORIO", 104, tx, y1, tracking=0.03)
    d2, w2, b2 = text_path(ANTON, "METALS", 46, 0, 0, tracking=0.16)
    y2 = b1[3] + 14 - b2[1]
    d2, w2, b2 = text_path(ANTON, "METALS", 46, tx, y2, tracking=0.16)
    right = max(tx + w1, tx + w2 + 70)
    hx0, hx1, hy0, hy1 = tx + w2 + 14, right, b2[1] + 5, b2[3] - 5
    hh = hy1 - hy0
    haz = (f'<clipPath id="hz-{theme}"><rect x="{hx0:.1f}" y="{hy0:.1f}" width="{hx1-hx0:.1f}" height="{hh:.1f}"/></clipPath>'
           f'<rect x="{hx0:.1f}" y="{hy0:.1f}" width="{hx1-hx0:.1f}" height="{hh:.1f}" fill="{COPPER}"/><g clip-path="url(#hz-{theme})">')
    x = hx0 - hh
    while x < hx1:
        haz += f'<path d="M{x:.1f} {hy1:.1f} L{x+hh:.1f} {hy0:.1f} L{x+hh+10:.1f} {hy0:.1f} L{x+10:.1f} {hy1:.1f} Z" fill="{INK}"/>'
        x += 20
    haz += "</g>"
    H = b2[3] + 16
    W = right + 10
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Corio Metals">'
           f'<g transform="translate(8 {(H-120)/2:.1f})">{icon}</g>'
           f'<path d="{d1}" fill="{word}"/><path d="{d2}" fill="{COPPER}"/>{haz}</svg>')
    open(os.path.join(OUT, f"logo-{theme}.svg"), "w").write(svg)
    return W, H


def icons():
    sq = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-14 -14 168 148"><rect x="-14" y="-14" width="168" height="148" rx="26" fill="{INK}"/>'
          f'{bin_icon(COPPER, BONE)}</svg>')
    open(os.path.join(OUT, "icon.svg"), "w").write(sq)
    for name, w in [("favicon-32.png", 32), ("favicon-64.png", 64), ("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)]:
        cairosvg.svg2png(bytestring=sq.encode(), write_to=os.path.join(OUT, name), output_width=w)


if __name__ == "__main__":
    print(lockup("dark"), lockup("light"))
    icons()
    for t in ("dark", "light"):
        cairosvg.svg2png(url=os.path.join(OUT, f"logo-{t}.svg"), write_to=f"/tmp/claude-0/-home-claude/dd8bbb2f-c6b4-5eca-8d91-f5c9cf325536/scratchpad/logo-{t}.png",
                         output_width=900, background_color=INK if t == "dark" else BONE)
