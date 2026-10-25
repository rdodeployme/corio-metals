"""Pictograms for The Metal Drop item checker. 48x48, 2.5 px strokes, round joins.

One consistent set: every item in the checker has its own drawing, so the grid reads as a
system rather than a collection of random icons.
"""

ICONS = {
    "fridge": '<rect x="13" y="5" width="22" height="38" rx="3"/><path d="M13 18h22M17 10v4M17 22v8"/>',
    "washer": '<rect x="9" y="6" width="30" height="36" rx="3"/><path d="M9 13h30"/><circle cx="24" cy="28" r="9"/><circle cx="24" cy="28" r="4"/><circle cx="15" cy="9.5" r=".8" class="f"/><circle cx="19" cy="9.5" r=".8" class="f"/>',
    "dryer": '<rect x="9" y="6" width="30" height="36" rx="3"/><path d="M9 13h30M18 28q3-3 6 0t6 0"/><circle cx="24" cy="28" r="9"/>',
    "oven": '<rect x="8" y="6" width="32" height="36" rx="3"/><path d="M8 14h32M14 18h20"/><rect x="13" y="21" width="22" height="15" rx="2"/><circle cx="14" cy="10" r=".8" class="f"/><circle cx="20" cy="10" r=".8" class="f"/><circle cx="28" cy="10" r=".8" class="f"/><circle cx="34" cy="10" r=".8" class="f"/>',
    "hws": '<rect x="14" y="4" width="20" height="36" rx="9"/><path d="M19 40v5M29 40v5"/><circle cx="24" cy="14" r="3"/>',
    "bbq": '<path d="M9 20Q9 9 24 9t15 11z"/><rect x="7" y="20" width="34" height="7" rx="1.5"/><path d="M11 27v14M37 27v14M11 35h26"/><circle cx="11" cy="42" r="2"/><circle cx="37" cy="42" r="2"/>',
    "bike": '<circle cx="12" cy="32" r="8"/><circle cx="36" cy="32" r="8"/><path d="M12 32l7-14h14l3 14M19 18l5 14 9-14M24 32H12M15 16h7M31 14h5"/>',
    "tramp": '<ellipse cx="24" cy="19" rx="19" ry="6"/><path d="M7 21l3 18 4-15M41 21l-3 18-4-15"/>',
    "mower": '<path d="M8 30h26a4 4 0 0 1 4 4v1H6v-1a2 2 0 0 1 2-2"/><path d="M14 30a6 6 0 0 1 12 0M33 30l9-22M40 8h5"/><circle cx="12" cy="38" r="4"/><circle cx="32" cy="38" r="4"/>',
    "setting": '<path d="M5 22h22M9 22v18M23 22v18M34 8v32M34 26h10M44 26v14"/>',
    "filing": '<rect x="13" y="4" width="22" height="40" rx="2"/><path d="M13 14h22M13 24h22M13 34h22M21 9h6M21 19h6M21 29h6M21 39h6"/>',
    "bed": '<path d="M7 14v28M41 22v20M7 30h34M7 24h34"/><path d="M7 42h3M38 42h3"/>',
    "shelving": '<path d="M11 4v40M37 4v40M11 12h26M11 22h26M11 32h26M11 42h26"/>',
    "pots": '<path d="M8 22h24v11a7 7 0 0 1-7 7H15a7 7 0 0 1-7-7z"/><path d="M32 26l9-3M10 22a10 5 0 0 1 20 0"/><circle cx="20" cy="15" r="1.2" class="f"/>',
    "gas": '<rect x="14" y="13" width="20" height="30" rx="8"/><path d="M18 13V8h12v5M24 4v4M14 26h20"/>',
    "ext": '<rect x="17" y="15" width="14" height="29" rx="5"/><path d="M20 15v-5h8v5M28 10h8M21 12q-9 2-9 12v6"/>',
    "battery": '<rect x="6" y="14" width="36" height="24" rx="2"/><path d="M11 14v-4h6v4M31 14v-4h6v4M12 26h6M15 23v6M30 26h6"/>',
    "roofing": '<path d="M4 36l10-22h30L34 36zM10 36l10-22M16 36l10-22M22 36l10-22M28 36l10-22"/>',
    "fence": '<path d="M8 6v38M40 6v38M8 11h32M8 39h32M14 11v28M20 11v28M26 11v28M34 11v28"/>',
    "pickets": '<path d="M12 44l3-36 3 36M22 44l2-36 2 36M32 44l2-36 3 36M10 8h7M21 8h6M31 8h7"/>',
    "mesh": '<rect x="6" y="8" width="36" height="32"/><path d="M15 8v32M24 8v32M33 8v32M6 16h36M6 24h36M6 32h36"/>',
    "offcuts": '<path d="M8 21h28l-5 11H14zM3 15l5 6M31 32l7 5M16 32l-2 7M13 21l7-13M19 21l9-12M25 21l5-14"/><circle cx="39" cy="38" r="4"/>',
    "pipe": '<path d="M5 14h23a12 12 0 0 1 12 12v18M5 22h23a4 4 0 0 1 4 4v18"/>',
    "cable": '<circle cx="22" cy="24" r="15"/><circle cx="22" cy="24" r="9.5"/><circle cx="22" cy="24" r="4"/><path d="M37 24l7 8"/>',
    "window": '<rect x="8" y="6" width="32" height="36" rx="1"/><path d="M24 6v36M8 24h32"/>',
    "gutter": '<path d="M5 12v9a7 7 0 0 0 7 7h24a7 7 0 0 0 7-7v-9M28 28v16M36 28v16"/>',
    "racking": '<path d="M8 4v40M24 4v40M40 4v40M8 14h32M8 28h32M8 42h32M8 16l16 10M24 16l16 10"/>',
    "locker": '<rect x="7" y="4" width="34" height="40" rx="1.5"/><path d="M18.3 4v40M29.6 4v40M10.5 10h4.5M21.8 10h4.5M33 10h4.5M15 24v4M26.3 24v4M37.6 24v4"/>',
    "desk": '<path d="M4 16h40M9 16v26M39 16v26M9 30h30"/>',
    "cage": '<rect x="10" y="5" width="28" height="33" rx="1"/><path d="M17 5v33M24 5v33M31 5v33M10 14h28M10 22h28M10 30h28"/><circle cx="14" cy="42" r="2.5"/><circle cx="34" cy="42" r="2.5"/>',
    "bench": '<path d="M4 18h40M4 18v-6M8 18v24M40 18v24M8 34h32"/>',
    "server": '<rect x="12" y="4" width="24" height="40" rx="2"/><path d="M12 12h24M12 20h24M12 28h24M12 36h24"/><circle cx="31" cy="8" r=".9" class="f"/><circle cx="31" cy="16" r=".9" class="f"/><circle cx="31" cy="24" r=".9" class="f"/>',
    "motor": '<rect x="8" y="14" width="24" height="20" rx="4"/><path d="M14 14v20M20 14v20M26 14v20M32 24h10M11 34l-2 6M29 34l2 6"/><rect x="14" y="8" width="10" height="6" rx="1"/>',
    "solar": '<path d="M10 8h28l4 24H6z"/><path d="M19 8l-2 24M29 8l2 24M8 16h32M7 24h34M24 32v10M16 42h16"/>',
    "rim": '<circle cx="24" cy="24" r="18"/><circle cx="24" cy="24" r="5"/><path d="M24 19V7M28.8 22.5l11.4-3.7M27 28.1l7 9.7M21 28.1l-7 9.7M19.2 22.5L7.8 18.8"/>',
    "radiator": '<rect x="8" y="9" width="32" height="30" rx="1"/><path d="M8 14h32M8 34h32M14 14v20M19 14v20M24 14v20M29 14v20M34 14v20M34 9V5"/>',
    "engine": '<path d="M8 20h26l6 6v12H8z"/><rect x="12" y="11" width="6" height="9"/><rect x="21" y="11" width="6" height="9"/><path d="M40 30h4M4 28h4"/>',
    "car": '<path d="M4 31v-6l6-2 6-8h16l6 8 6 2v6z"/><path d="M17 15v8M10 23h28"/><circle cx="14" cy="33" r="4"/><circle cx="34" cy="33" r="4"/>',
    "asbestos": '<path d="M24 6l20 34H4z"/><path d="M24 18v11"/><circle cx="24" cy="34.5" r="1.4" class="f"/>',
    "chem": '<rect x="13" y="6" width="22" height="36" rx="2"/><path d="M13 16h22M13 32h22M20 6V3h8v3"/>',
    "fullgas": '<rect x="14" y="13" width="20" height="30" rx="8"/><path d="M18 13V8h12v5M24 4v4M19 22l10 12M29 22L19 34"/>',
    # UI pictograms
    "roof": '<path d="M4 20L24 7l20 13M9 17v25M39 17v25M4 42h40"/>',
    "staff": '<circle cx="24" cy="13" r="7"/><path d="M10 43v-6a14 14 0 0 1 28 0v6M18 31l6 6 6-6"/>',
    "tag": '<path d="M6 24V8h16l20 20-14 14z"/><circle cx="14" cy="16" r="3"/>',
    "check": '<path d="M9 25l9 9L39 13"/>',
    "cross": '<path d="M12 12l24 24M36 12L12 36"/>',
    "pin": '<path d="M24 44S10 30 10 19a14 14 0 0 1 28 0c0 11-14 25-14 25z"/><circle cx="24" cy="19" r="5"/>',
    "clock": '<circle cx="24" cy="24" r="18"/><path d="M24 13v11l7 5"/>',
    "phone": '<path d="M13 6h7l3 9-5 3a24 24 0 0 0 12 12l3-5 9 3v7a4 4 0 0 1-4 4A36 36 0 0 1 9 10a4 4 0 0 1 4-4z"/>',
    "truck": '<path d="M4 12h24v22H4zM28 20h9l7 8v6H28z"/><circle cx="12" cy="36" r="4"/><circle cx="36" cy="36" r="4"/>',
    "search": '<circle cx="21" cy="21" r="13"/><path d="M31 31l11 11"/>',
    "spanner": '<path d="M29 6a10 10 0 0 0-9 14L6 34a4 4 0 0 0 6 6l14-14A10 10 0 0 0 40 17l-6 6-6-1-1-6 6-6a10 10 0 0 0-4-4z"/>',
}


def svg(name, cls="ic", title=None):
    inner = ICONS[name]
    t = f"<title>{title}</title>" if title else ""
    aria = 'role="img"' if title else 'aria-hidden="true"'
    return (f'<svg class="{cls}" viewBox="0 0 48 48" {aria} fill="none" stroke="currentColor" stroke-width="2.5" '
            f'stroke-linecap="round" stroke-linejoin="round">{t}{inner}</svg>')
