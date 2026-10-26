# Scrap metal site: five concepts for approval

One repo, five versions of the same offer, with a bar of big buttons at the top of every page to swap between them.

| Concept | Folder | Lead path |
|---|---|---|
| Corio Metals | repo root | Balanced: drop-off and collections side by side |
| The Metal Drop | `the-metal-drop/` | Public drop-off first, business collections second |
| Recycled Metals (was BTT By The Tonne) | `recycled-metals/` | Richard's notes, 26 Oct: free drop-off at any volume, four ways to move metal, bins and big jobs by enquiry. Old `by-the-tonne/` URLs redirect here |
| Shedload | `shedload/` | Brand first: "Shedload? Drop it off. Truckload? We'll collect." |
| Crux Metals | `crux-metals/` | Richard's focus: his lines and 766-item directory as the home page tool, the group's credentials, YARTA reporting |

Comparison page: `concepts/` (not part of any brand, noindex).

## The offer (same in all five)
- Public drop-off at Recycle North Geelong, 116 Furner Avenue, North Geelong VIC 3215. Clean scrap metal is no charge. We don't pay for metal.
- Handling fees on a few items (gas bottles, extinguishers, nitrous canisters, solar panels, tyres on rims), per Recycle North Geelong's price list.
- Collections from one tonne: one service fee, quoted before we come; weighbridge docket for every load; reporting through YARTA (four versions; Recycled Metals has bins and big jobs by enquiry, no YARTA).
- Contact: Nigel Taylor, 0427 888 222, nigel@recycle.net.au.

## Where things live
- `common/common.py` is the single source of truth: contact, address, hours, fees, can't-take list, item list with guide weights, load sizes, and the banned-word checks. Change a fact here and rebuild; every concept picks it up.
- `common/review/` is the version bar (switcher): big buttons, one per version, plus Compare. `common/brand/` holds the official Recycle Group marks.
- Each concept has `build.py`, `src/pages/*.html`, `src/css/main.css`, `src/js/main.js`, `fonts/` and a `logo.py` (logos are drawn from fonts as paths).
- Crux Metals (`crux/`): Roboto Slab and Source Sans 3; charcoal, red oxide and bone; the CRUX logo's X is two bolted steel bars (`crux/logo.py`). Real facility photos from the Recycle Group site plus three generated collection shots. `crux/data/directory-source.json` is Richard's 766-item directory, parsed from the Recycle Group site's metals section; notes are cleaned at build time (no "free" wording) and gate-fee items are matched in `crux/build.py` (`fee_for`).
- Recycled Metals (`tonne/`) uses Saira (variable, expanded) for display type, Inter Tight for text and IBM Plex Mono for figures; black, white and safety yellow; the riveted yellow nameplate reads RECYCLED / METALS (`tonne/logo.py`). Crux's 766-item directory is in `tonne/data/directory-source.json`, with a drop-off column (free, or the gate fee). Grey photos in `tonne/img/` (Higgsfield, plus the real Furner Avenue photos in greyscale). The service map is drawn by `tonne/map.py` from Natural Earth 10m land and roads clipped into `tonne/data/sw-vic.json`. Its build stops on "we/our/us", tonne thresholds, YARTA or free collections; "free" is allowed for drop-off on this site only.

## Build
```
python3 _build/build_all.py                # everything
python3 _build/build_all.py drop tonne     # some: corio, drop, tonne, shed, crux, concepts
```
Needs Python 3 with Pillow, cairosvg and fontTools (plus Playwright for the comparison page screenshots).

## Guards (the build stops on any of these)
- Em dashes, anywhere.
- The word "free".
- Payment wording: "get paid", "we pay you", "bank transfer", "photo ID", "price board", per kg rates.
