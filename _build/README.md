# Scrap metal site: five concepts for approval

One repo, five versions of the same offer, with a review bar at the top of every page to swap between them.

| Concept | Folder | Lead path |
|---|---|---|
| Corio Metals | repo root | Balanced: drop-off and collections side by side |
| The Metal Drop | `the-metal-drop/` | Public drop-off first, business collections second |
| BTT By The Tonne | `by-the-tonne/` | Commercial collections first, drop-off second |
| Shedload | `shedload/` | Brand first: "Shedload? Drop it off. Truckload? We'll collect." |
| Recycle Group Metals | `recycle-group-metals/` | Master brand: the offer under Recycle Group, with Richard's 766-item directory as the home page tool |

Comparison page: `concepts/` (not part of any brand, noindex).

## The offer (same in all five)
- Public drop-off at Recycle North Geelong, 116 Furner Avenue, North Geelong VIC 3215. Clean scrap metal is no charge. We don't pay for metal.
- Handling fees on a few items (gas bottles, extinguishers, nitrous canisters, solar panels, tyres on rims), per Recycle North Geelong's price list.
- Collections from one tonne: one service fee, quoted before we come; weighbridge docket for every load; reporting through YARTA.
- Contact: Nigel Taylor, 0427 888 222, nigel@recycle.net.au.

## Where things live
- `common/common.py` is the single source of truth: contact, address, hours, fees, can't-take list, item list with guide weights, load sizes, and the banned-word checks. Change a fact here and rebuild; every concept picks it up.
- `common/review/` is the review bar (switcher). `common/brand/` holds the official Recycle Group marks.
- Each concept has `build.py`, `src/pages/*.html`, `src/css/main.css`, `src/js/main.js`, `fonts/` and a `logo.py` (logos are drawn from fonts as paths).
- Recycle Group Metals (`rgm/`) uses the official Recycle Group logo with a METALS tag (proposed lockup), the group's real facility photos, and `rgm/data/directory-source.json`: Richard's 766-item directory, parsed from the Recycle Group site's metals section. Notes are cleaned at build time (no "free" wording).
- BTT (`tonne/`) uses Saira (variable, expanded) for display type, Inter Tight for text and IBM Plex Mono for figures. No serif, no italics.

## Build
```
python3 _build/build_all.py                # everything
python3 _build/build_all.py drop tonne     # some: corio, drop, tonne, shed, rgm, concepts
```
Needs Python 3 with Pillow, cairosvg and fontTools (plus Playwright for the comparison page screenshots).

## Guards (the build stops on any of these)
- Em dashes, anywhere.
- The word "free".
- Payment wording: "get paid", "we pay you", "bank transfer", "photo ID", "price board", per kg rates.
