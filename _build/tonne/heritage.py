"""Where it started: the Robert Hyde & Co. tokens, drawn as line art for the heritage page and the home strip.

The 1857 token is redrawn from the legend recorded by Museums Victoria (NU 11310 and related), not traced from a photo.
The second token is a concept only: a Recycled Metals token that could be struck from copper dropped off at the gate.
"""
import math


def _beads(r, n, rad):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        out.append(f'<circle cx="{100 + r * math.cos(a):.2f}" cy="{100 + r * math.sin(a):.2f}" r="{rad}"/>')
    return "".join(out)


def token(kind, uid):
    """kind 'hyde' (1857) or 'rm' (concept). uid keeps the textPath ids unique on a page."""
    if kind == "hyde":
        top, bottom = "ROBERT HYDE &amp; Co", "MELBOURNE"
        centre = ('<text class="tk-c1" x="100" y="80">GENERAL</text>'
                  '<text class="tk-c2" x="100" y="94">MARINE STORE</text>'
                  '<path class="tk-rule" d="M76 101.5h48"/>'
                  '<text class="tk-c3" x="100" y="113">SHIPPERS OF</text>'
                  '<text class="tk-c3" x="100" y="124">RAGS GLASS</text>'
                  '<text class="tk-c3" x="100" y="135">METALS &amp;c.</text>')
        label = "Robert Hyde &amp; Co. token, 1857, redrawn"
    else:
        top, bottom = "RECYCLED METALS", "NORTH GEELONG"
        centre = ('<text class="tk-c1" x="100" y="82">ANY METAL</text>'
                  '<text class="tk-c1" x="100" y="96">ANY VOLUME</text>'
                  '<path class="tk-rule" d="M76 104h48"/>'
                  '<text class="tk-c3" x="100" y="117">BACK INTO USE</text>'
                  '<text class="tk-yr" x="100" y="133">2026</text>')
        label = "Recycled Metals token, a concept"
    return f'''<svg class="tok tok-{kind}" viewBox="0 0 200 200" role="img" aria-label="{label}">
<defs><path id="tt-{uid}" d="M31 100a69 69 0 0 1 138 0"/><path id="tb-{uid}" d="M22 100a78 78 0 0 0 156 0"/></defs>
<circle class="tk-face" cx="100" cy="100" r="96"/>
<circle class="tk-edge" cx="100" cy="100" r="96"/>
<g class="tk-beads">{_beads(89.5, 72, 1.15)}</g>
<circle class="tk-ring" cx="100" cy="100" r="83"/>
<circle class="tk-ring" cx="100" cy="100" r="57"/>
<text class="tk-leg"><textPath href="#tt-{uid}" startOffset="50%">{top}</textPath></text>
<text class="tk-leg"><textPath href="#tb-{uid}" startOffset="50%">{bottom}</textPath></text>
<path class="tk-dot" d="M26 96l4 4-4 4-4-4zM174 96l4 4-4 4-4-4z"/>
{centre}
</svg>'''


def pair():
    return f'''<div class="tokens">
  <figure class="tk-fig">{token("hyde", "h1")}<figcaption><b>1857</b>Robert Hyde &amp;&nbsp;Co., Melbourne</figcaption></figure>
  <span class="tk-arrow" aria-hidden="true"></span>
  <figure class="tk-fig">{token("rm", "r1")}<figcaption><b>Today</b>Recycled Metals, North&nbsp;Geelong</figcaption></figure>
</div>'''
