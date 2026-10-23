# Corio Metals site source

Static site for Corio Metals: public scrap metal drop-off at 116 Furner Avenue, North Geelong, and commercial collections from one tonne.

- Edit pages in `src/pages/*.html`, styles in `src/css/main.css`, behaviour in `src/js/main.js`.
- Contact, address, gate hours and the collection minimum are set at the top of `build.py` (`HOURS = None` shows "Call ahead for gate hours" until hours are confirmed).
- Rebuild into the repo root: `python3 _build/build.py` (needs Python 3, Pillow and cairosvg). Logo: `python3 _build/brand/logo.py`.
- Rules: no em dashes, no "free", Australian English. The build fails if either slips in.

## Updating prices
- Edit `assets/js/rates.js` in the repo root (you can do it straight on GitHub: open the file, click the pencil, save).
- Rates are $ per kg; handling fees are $ per item. `null` shows "Call" / "Quoted". Set `updated` to when they were set.
- The build never overwrites `assets/js/rates.js`; grade names and descriptions live in `_build/data/prices.json`.
