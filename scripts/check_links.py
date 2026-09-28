#!/usr/bin/env python3
"""Check every relative link in the repo's markdown resolves.

Checks [text](path) links relative to the file's real location (symlinked docs resolve from their
target), and backticked repo paths such as `styles/x/starter/` or `references/qa.md` relative to the
repo root. Exits 1 and lists every broken link.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
TICK = re.compile(r"`((?:styles|references|profiles|scripts)/[^`\s*<>]*)`")
SKIP_DIRS = {"node_modules", ".git"}

def md_files():
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(d, f)

broken = []
checked = 0
for path in md_files():
    real = os.path.realpath(path)
    if real != path and real.startswith(ROOT):
        continue  # a compatibility symlink; its target is checked at its real path
    base = os.path.dirname(real)
    rel = os.path.relpath(path, ROOT)
    text = open(real, encoding="utf-8").read()
    for n, line in enumerate(text.splitlines(), 1):
        for target in LINK.findall(line):
            if re.match(r"^[a-z]+:|^#|^mailto:", target):
                continue
            t = target.split("#")[0]
            if not t:
                continue
            checked += 1
            if not os.path.exists(os.path.join(base, t)):
                broken.append(f"{rel}:{n}: {target}")
        for target in TICK.findall(line):
            t = target.rstrip(".,;:")
            if "<" in t or "*" in t:
                continue
            checked += 1
            if not (os.path.exists(os.path.join(ROOT, t)) or os.path.exists(os.path.join(base, t))):
                broken.append(f"{rel}:{n}: `{target}`")

print(f"{checked} links checked, {len(broken)} broken")
for b in broken:
    print("  " + b)
sys.exit(1 if broken else 0)
