"""Recycled Metals logo (3 Nov 2026): back to the original Recycled | METALS stacked-steel cube,
with the stripe in the cube (and the d, divider and METALS) in safety yellow instead of copper.
"Since 1955" removed.

Sources are the official Recycled | METALS SVGs from rdodeployme/global-steel, copied into
brand-src/ (text is already outlined as paths). This file recolours them:
  on dark backgrounds (header, footer, og image): yellow stripe, yellow d / divider / METALS, white text
  on light backgrounds (the white weighbridge docket): yellow stripe, all text black (yellow type
  does not read on white)
The Saira helpers stay: build.py uses static_ttf() for the og image.
"""
import os, re
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
VF = os.path.join(HERE, "fonts", "saira-latin-wdth-normal.woff2")
SRC = os.path.join(HERE, "brand-src")
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "recycled-metals-site" if os.environ.get("RM_STANDALONE") == "1" else "recycled-metals", "assets", "brand")
os.makedirs(OUT, exist_ok=True)
YELLOW, YELLOW_SHADE, BLACK, WHITE = "#FFD200", "#C9A400", "#0E0E0E", "#FFFFFF"
COPPER, COPPER_SHADE = "#C2804F", "#8A5A38"
_inst = {}


def font(wght, wdth):
    k = (wght, wdth)
    if k not in _inst:
        f = TTFont(VF)
        f.flavor = None
        _inst[k] = instancer.instantiateVariableFont(f, {"wght": wght, "wdth": wdth})
    return _inst[k]


def static_ttf(wght, wdth):
    """Write a static Saira instance (used by the og image) and return its path."""
    p = f"/tmp/saira-{wght}-{wdth}.ttf"
    if not os.path.exists(p):
        font(wght, wdth).save(p)
    return p


def recolour(svg, text_accent):
    """Cube stripe to yellow (front face) and a darker yellow (side face); other copper to text_accent."""
    svg = svg.replace(f'<polygon fill="{COPPER}"', f'<polygon fill="{YELLOW}"')
    svg = svg.replace(COPPER_SHADE, YELLOW_SHADE)
    svg = svg.replace(COPPER, text_accent)
    assert COPPER not in svg and COPPER_SHADE not in svg
    return svg


def fade_wordmark(svg, white="#F2F4F5"):
    """8 Nov 2026 (Andy): a very slow gradient across "Recycled", the R white and the d full yellow.
    The glyphs each carry their own translate, so a userSpaceOnUse gradient on them would restart per
    letter. Instead the glyphs become a clipPath and one gradient-filled rect, in the root coordinates,
    is clipped to them. Glyph units: R starts at 0 and is about 628 wide; the d starts at about 4036."""
    i = svg.find("<g transform=")
    j = svg.find("</g>", i) + 4
    g = svg[i:j]
    tx, ty, s = map(float, re.match(r'<g transform="translate\(([\d.]+),([\d.]+)\) scale\(([\d.]+),', g).groups())
    x_white = tx + 314 * s      # middle of the R
    x_yellow = tx + 4036 * s    # left edge of the d
    left, right = tx - 10, tx + 4800 * s
    top, bottom = ty - 760 * s, ty + 220 * s   # cap height down to the g's descender
    # Browsers ignore a <g> inside a clipPath, so the group's transform moves onto the clipPath itself.
    gt = re.match(r'<g (transform="[^"]+")>', g).group(1)
    glyphs = re.sub(r' fill="#[0-9A-Fa-f]{6}"', "", g[g.find(">") + 1:-4])
    new = (f'<defs><linearGradient id="rm-fade" gradientUnits="userSpaceOnUse" x1="{x_white:.1f}" y1="0" x2="{x_yellow:.1f}" y2="0">'
           f'<stop offset="0" stop-color="{white}"/><stop offset="1" stop-color="{YELLOW}"/></linearGradient>'
           f'<clipPath id="rm-word" {gt}>{glyphs}</clipPath></defs>'
           f'<rect x="{left:.1f}" y="{top:.1f}" width="{right - left:.1f}" height="{bottom - top:.1f}" fill="url(#rm-fade)" clip-path="url(#rm-word)"/>')
    return svg[:i] + new + svg[j:]


def label(svg, text="Recycled Metals"):
    return svg.replace("<svg ", f'<svg role="img" aria-label="{text}" ', 1)


def read(name):
    return open(os.path.join(SRC, name)).read()


def size(svg):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    return float(m.group(1)), float(m.group(2))


def lockup(theme="light"):
    """logo-dark.svg: for dark backgrounds. logo-light.svg: for light backgrounds."""
    if theme == "dark":
        svg = fade_wordmark(recolour(read("recycled-logo-on-dark.svg"), YELLOW))
    else:
        svg = recolour(read("recycled-logo-on-light.svg"), BLACK).replace("#0F1214", BLACK)
    open(os.path.join(OUT, f"logo-{theme}.svg"), "w").write(label(svg))
    return size(svg)


def plate_only():
    """Compact logo for narrow screens (kept as plate.svg so build.py's paths don't change):
    the stacked lockup on dark."""
    svg = fade_wordmark(recolour(read("recycled-logo-stacked-on-dark.svg"), YELLOW))
    open(os.path.join(OUT, "plate.svg"), "w").write(label(svg))
    open(os.path.join(OUT, "mark.svg"), "w").write(label(recolour(read("recycled-mark-on-dark.svg"), YELLOW)))
    return size(svg)


def icons():
    """Square icon: the yellow-striped cube on a black tile."""
    mark = recolour(read("recycled-mark-on-dark.svg"), YELLOW)
    inner = re.sub(r"^<svg[^>]*>|</svg>$", "", mark.strip())
    mw, mh = size(mark)
    s = 72 / mh
    sq = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96">'
          f'<rect width="96" height="96" rx="14" fill="{BLACK}"/>'
          f'<g transform="translate({48 - mw * s / 2:.2f},12) scale({s:.5f})">{inner}</g></svg>')
    open(os.path.join(OUT, "icon.svg"), "w").write(sq)
    for name, w in [("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512)]:
        cairosvg.svg2png(bytestring=sq.encode(), write_to=os.path.join(OUT, name), output_width=w, output_height=w)


if __name__ == "__main__":
    print(lockup("light"), lockup("dark"), plate_only())
    icons()
