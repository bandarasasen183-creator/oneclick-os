#!/usr/bin/env python3
"""Stops our icons from swallowing more specific ones.

When an app asks for "preferences-system-bluetooth" and the theme lacks it, the desktop falls
back to "preferences-system". Because our theme is searched first, our general icon would win
over the base set's specific one. For every icon we ship, this links the base set's more
specific variants ("name-something") into our theme, unless we drew that one ourselves.

usage: fill_icon_gaps.py <our theme dir> <base theme dir>"""
import os, sys

ours, base = sys.argv[1], sys.argv[2]
mine = {}
for sub in ("apps", "panel", "places"):
    d = os.path.join(ours, "scalable", sub)
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.endswith(".svg"):
                mine[f[:-4]] = sub

# Every icon in the base set, preferring the largest size.
available = {}
for size in ("64x64", "48x48", "32x32", "24x24", "22x22", "16x16"):
    top = os.path.join(base, size)
    for root, _, files in os.walk(top):
        for f in files:
            if f.endswith(".svg"):
                available.setdefault(f[:-4], os.path.join(root, f))

linked = 0
for name, path in available.items():
    if name in mine:
        continue
    parts = name.split("-")
    for i in range(len(parts) - 1, 0, -1):
        parent = "-".join(parts[:i])
        if parent in mine:
            target = os.path.join(ours, "scalable", mine[parent], name + ".svg")
            os.symlink(os.path.realpath(path), target)
            linked += 1
            break
print(f"linked {linked} specific icons from {os.path.basename(base)}")
