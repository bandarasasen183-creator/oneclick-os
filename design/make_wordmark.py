#!/usr/bin/env python3
"""Draws the OneClick wordmark: the logo ring is the O, followed by "neClick" in letters drawn
with the same rounded line as the ring. Also renders the 60 boot-animation frames.
Run from the repo root on a Mac (uses qlmanage and sips to turn SVG into PNG)."""
import math, os, subprocess, sys, tempfile, shutil

RING = 'M74 72.500 A76 76 0 1 0 166 72.500'          # the O (open at the top)
RING_LEN = 2 * math.pi * 76 * (1 - 2 * math.degrees(math.atan2(46, 60.500)) / 360)
LETTERS = [                                        # n e C l i c k, as centre lines
    'M250 116 V209', 'M250 163 A38 38 0 0 1 326 163 V209',
    'M368 163 H460 A46 46 0 1 0 446.500 195.500',
    'M648.200 84.100 A76 76 0 1 0 648.200 181.900',
    'M712 57 V209',
    'M766 116 V209',
    'M895.200 133.400 A46 46 0 1 0 895.200 192.600',
    'M958 57 V209', 'M1012 116 L958 168', 'M979 148 L1016 209',
]
W, H = 1060, 266
TEAL, WHITE = "#2dd4bf", "#ffffff"

def mark(draw=1.0, dot=1.0, letters=1.0, fade=1.0, background=None):
    r = 17 * (dot * (1.25 - 0.25 * dot))
    out = [f'<g opacity="{fade:.3f}" fill="none" stroke-linecap="round" stroke-linejoin="round">']
    if draw > 0.01:
        out.append(f'<path d="{RING}" stroke="{TEAL}" stroke-width="26" stroke-dasharray="{draw * RING_LEN:.1f} 2000"/>')
    out.append(f'<circle cx="120" cy="58.500" r="{r:.1f}" fill="{WHITE}" stroke="none"/>')
    out.append(f'<g opacity="{letters:.3f}" stroke="{WHITE}" stroke-width="24">')
    out += [f'<path d="{d}"/>' for d in LETTERS]
    out.append(f'<circle cx="766" cy="72" r="15" fill="{TEAL}" stroke="none"/></g></g>')
    body = "".join(out).replace(".500", ".5").replace(".200", ".2").replace(".100", ".1")
    return body

def svg(body, background=None):
    bg = f'<rect width="{W}" height="{H}" fill="{background}"/>' if background else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{bg}<g transform="translate(0,12)">{body}</g></svg>\n'

# 1. The wordmark itself, for dark backgrounds
os.makedirs("system_files/usr/share/oneclick", exist_ok=True)
open("system_files/usr/share/oneclick/wordmark.svg", "w").write(svg(mark()))

# 2. Boot animation: ring draws, dot pops, letters fade in, hold, fade out
if "--frames" in sys.argv:
    tmp = tempfile.mkdtemp(); N = 60; out_w = 560; out_h = round(out_w * H / W)
    for i in range(N):
        t = i / N
        draw = min(1, t / 0.35); draw = draw * draw * (3 - 2 * draw)
        dot = 0 if t < 0.35 else min(1, (t - 0.35) / 0.08)
        letters = 0 if t < 0.40 else min(1, (t - 0.40) / 0.15)
        fade = 1 if t < 0.88 else 1 - (t - 0.88) / 0.12
        square = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}"><rect x="-20" y="-20" width="{W+40}" height="{W+40}" fill="#000"/>'
                  f'<g transform="translate(0,{(W - H) / 2 + 12})">{mark(draw, dot, letters, fade)}</g></svg>')
        open(f"{tmp}/throbber-{i+1:04d}.svg", "w").write(square)
    subprocess.run(f'qlmanage -t -s {out_w} -o {tmp} {tmp}/*.svg >/dev/null 2>&1', shell=True)
    dest = "build_files/boot/plymouth"
    for i in range(N):
        name = f"throbber-{i+1:04d}"
        subprocess.run(["sips", "-c", str(out_h), str(out_w), f"{tmp}/{name}.svg.png", "--out", f"{dest}/{name}.png"],
                       stdout=subprocess.DEVNULL)
    shutil.rmtree(tmp)
    print("frames:", N, f"{out_w}x{out_h}")
