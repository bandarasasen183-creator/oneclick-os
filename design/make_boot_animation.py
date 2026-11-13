#!/usr/bin/env python3
"""Renders the start-up animation frames. Run from the repo root on a Mac.

The word OneClick is drawn stroke by stroke, like handwriting. The logo's white dot pops in
when the ring closes. The dot of the i is not drawn: it falls from above, bounces off the top
of the k, arcs across to the i, bounces there, and settles in its place."""
import math, os, shutil, subprocess, tempfile

FPS = 30
W, H = 1060, 330                    # extra head-room above the letters for the falling dot
TOP = 76                            # the letters sit this far down inside the frame
TEAL, WHITE = "#2dd4bf", "#ffffff"

# (path, colour, width, relative time it takes to draw)
STROKES = [
    ("M74 72.5 A76 76 0 1 0 166 72.5", TEAL, 26, 3.0),            # O
    ("M250 116 V209", WHITE, 24, 0.7), ("M250 163 A38 38 0 0 1 326 163 V209", WHITE, 24, 1.1),   # n
    ("M368 163 H460 A46 46 0 1 0 446.5 195.5", WHITE, 24, 2.0),   # e
    ("M648.2 84.1 A76 76 0 1 0 648.2 181.9", WHITE, 24, 2.3),     # C
    ("M712 57 V209", WHITE, 24, 0.9),                             # l
    ("M766 116 V209", WHITE, 24, 0.7),                            # i (stem only)
    ("M895.2 133.4 A46 46 0 1 0 895.2 192.6", WHITE, 24, 1.5),    # c
    ("M958 57 V209", WHITE, 24, 0.9), ("M1012 116 L958 168", WHITE, 24, 0.5), ("M979 148 L1016 209", WHITE, 24, 0.5),  # k
]
WRITE_TIME = 1.75                   # seconds to write the whole word
total = sum(s[3] for s in STROKES)
starts, acc = [], 0.0
for s in STROKES:
    starts.append(acc / total * WRITE_TIME); acc += s[3]
ends = starts[1:] + [WRITE_TIME]

def ease(p): return p * p * (3 - 2 * p)

# ---- the i-dot's flight -------------------------------------------------------------
G = 1555.0                          # gravity, px/s^2
K_X, K_Y = 958.0, 30.0              # resting on top of the k
I_X, I_Y, I_REST = 766.0, 89.0, 72.0   # touching the top of the i, and its final place
T_FALL, T_ARC, T_HOP, T_SETTLE = 0.30, 0.42, 0.424, 0.70
T0 = WRITE_TIME + 0.10

def dot_position(t):
    """Returns (x, y, squash) of the i-dot at time t, or None before it appears."""
    t -= T0
    if t < 0:
        return None
    if t < T_FALL:                                    # falls onto the k
        return K_X, K_Y - 0.5 * G * T_FALL ** 2 + 0.5 * G * t ** 2, 0
    t -= T_FALL
    if t < T_ARC:                                     # bounces off the k, arcs over to the i
        vy = (I_Y - K_Y - 0.5 * G * T_ARC ** 2) / T_ARC
        return K_X + (I_X - K_X) * t / T_ARC, K_Y + vy * t + 0.5 * G * t * t, 0
    t -= T_ARC
    if t < T_HOP:                                     # bounces on the i
        vy = -0.5 * G * T_HOP
        return I_X, I_Y + vy * t + 0.5 * G * t * t, 0
    t -= T_HOP
    t = min(t, T_SETTLE)                              # one last small hop, then it floats to rest
    return I_X, I_REST + (I_Y - I_REST) * math.exp(-6.5 * t) * math.cos(17 * t), 0

DURATION = T0 + T_FALL + T_ARC + T_HOP + T_SETTLE + 0.15
N = math.ceil(DURATION * FPS)

def frame(t):
    parts = []
    for (d, colour, width, _), a, b in zip(STROKES, starts, ends):
        if t <= a:
            continue
        p = ease(min(1, (t - a) / (b - a)))
        parts.append(f'<path d="{d}" pathLength="1" fill="none" stroke="{colour}" stroke-width="{width}" '
                     f'stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{p:.4f} 2"/>')
    ring_done = ends[0]
    if t > ring_done:                                 # the logo's own dot pops in
        q = min(1, (t - ring_done) / 0.16)
        parts.append(f'<circle cx="120" cy="58.5" r="{17 * q * (1.3 - 0.3 * q):.2f}" fill="{WHITE}"/>')
    pos = dot_position(t)
    if pos:
        parts.append(f'<circle cx="{pos[0]:.1f}" cy="{pos[1]:.1f}" r="15" fill="{TEAL}"/>')
    return "".join(parts)

tmp = tempfile.mkdtemp()
out_w = 620; out_h = round(out_w * H / W)
for i in range(N):
    body = frame(i / FPS)
    open(f"{tmp}/frame-{i:03d}.svg", "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}"><rect x="-20" y="-20" width="{W+40}" height="{W+40}" fill="#000"/>'
        f'<g transform="translate(0,{(W - H) / 2 + TOP})">{body}</g></svg>')
subprocess.run(f'qlmanage -t -s {out_w} -o {tmp} {tmp}/*.svg >/dev/null 2>&1', shell=True)
dest = "build_files/boot/plymouth"
for old in os.listdir(dest):
    if old.endswith(".png"):
        os.remove(f"{dest}/{old}")
for i in range(N):
    subprocess.run(["sips", "-c", str(out_h), str(out_w), f"{tmp}/frame-{i:03d}.svg.png", "--out", f"{dest}/frame-{i:03d}.png"],
                   stdout=subprocess.DEVNULL)
shutil.rmtree(tmp)
print(f"{N} frames at {FPS} fps, {out_w}x{out_h}")
