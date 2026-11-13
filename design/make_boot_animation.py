#!/usr/bin/env python3
"""Renders the start-up animation frames. Run from the repo root on a Mac.

The word OneClick is drawn stroke by stroke, like handwriting. The logo's white dot pops in
when the ring closes. The dot of the i is not drawn: it drops straight onto the i, squashes
as it lands, bounces twice, each time lower, and settles."""
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

# ---- the i-dot: drops straight onto the i, bounces twice (each lower), squashes as it lands ---
G = 2600.0                          # gravity, px/s^2
REST_Y, START_Y, X = 72.0, -40.0, 766.0   # starts inside the frame, out of the dark
BOUNCE = 0.42                       # each bounce keeps 42% of the speed
T0 = WRITE_TIME + 0.12

def _simulate():
    """Steps the fall once and returns a list of (t, y, squash) samples at 240 per second."""
    out, t, y, v, dt, hits = [], 0.0, START_Y, 0.0, 1 / 240, 0
    while t < 1.6:
        v += G * dt; y += v * dt
        squash = 0.0
        if y >= REST_Y and v > 0:
            y = REST_Y; hits += 1
            squash = min(0.32, v / 2600)            # harder landing, flatter dot
            v = -v * BOUNCE if hits < 3 else 0.0
        out.append((t, y, squash)); t += dt
    return out
_SAMPLES = _simulate()

def dot_position(t):
    t -= T0
    if t < 0:
        return None
    i = min(int(t * 240), len(_SAMPLES) - 1)
    # squash lingers for 0.08s after an impact
    sq = max((s for (tt, _, s) in _SAMPLES[max(0, i - 19):i + 1]), default=0)
    return X, _SAMPLES[i][1], sq

DURATION = T0 + 1.25
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
        appear = min(1, (t - T0) / 0.14)            # fades in out of the black as it starts to fall
        sq = pos[2]   # flatten against the i: wider, shorter, bottom stays on the line
        rx, ry = 15 * (1 + sq), 15 * (1 - sq)
        parts.append(f'<ellipse cx="{pos[0]:.1f}" cy="{pos[1] + 15 - ry:.1f}" rx="{rx * (0.6 + 0.4 * appear):.2f}" ry="{ry * (0.6 + 0.4 * appear):.2f}" fill="{TEAL}" opacity="{appear:.3f}"/>')
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
