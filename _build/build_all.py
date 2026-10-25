#!/usr/bin/env python3
"""Build every concept, the review switcher and the comparison page.

python3 _build/build_all.py            # all
python3 _build/build_all.py corio drop # some
"""
import os, sys, shutil, subprocess, re, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "common"))
import common as C  # noqa: E402

CONCEPTS = [("corio", "corio/build.py"), ("drop", "metaldrop/build.py"), ("tonne", "tonne/build.py"),
            ("shed", "shedload/build.py"), ("concepts", "concepts/build.py")]


def run(which):
    for key, script in CONCEPTS:
        if which and key not in which:
            continue
        p = os.path.join(HERE, script)
        if not os.path.exists(p):
            print("skip (not built yet):", key)
            continue
        r = subprocess.run([sys.executable, p], cwd=REPO)
        if r.returncode:
            raise SystemExit(f"{key} build failed")
    # review switcher
    dst = os.path.join(REPO, "review")
    os.makedirs(dst, exist_ok=True)
    for f in ("switcher.js", "switcher.css"):
        shutil.copy(os.path.join(HERE, "common", "review", f), os.path.join(dst, f))
    # JS text checks (copy shown to visitors lives in JS too)
    for js in glob.glob(os.path.join(REPO, "**", "assets", "js", "*.js"), recursive=True) + [os.path.join(dst, "switcher.js")]:
        if "/_build/" in js:
            continue
        s = open(js, encoding="utf-8").read()
        for pat, what in C.BANNED:
            if what == "em dash":
                if re.search(pat, s):
                    raise SystemExit(f"em dash in {js}")
            elif re.search(pat, s, re.I):
                raise SystemExit(f"{what} in {js}: {re.search(pat, s, re.I).group(0)}")
    # sitemap + robots for the whole repo
    pages = []
    for f in sorted(glob.glob(os.path.join(REPO, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(f, REPO)
        if rel.startswith("_build") or rel.startswith("concepts/") or rel.endswith("404.html") or rel in ("prices.html",):
            continue
        pages.append(rel)
    today = datetime.date.today().isoformat()
    with open(os.path.join(REPO, "sitemap.xml"), "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for rel in pages:
            loc = C.SITE_BASE + re.sub(r"(^|/)index\.html$", r"\1", rel)
            fh.write(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod></url>\n")
        fh.write("</urlset>\n")
    open(os.path.join(REPO, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {C.SITE_BASE}sitemap.xml\n")
    open(os.path.join(REPO, ".nojekyll"), "w").write("")
    print("done:", len(pages), "pages in sitemap")


if __name__ == "__main__":
    run(set(sys.argv[1:]))
