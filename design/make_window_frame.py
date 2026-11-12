#!/usr/bin/env python3
"""Draws the OneClick window frame: flat title bar with classic minimise / maximise / close buttons.
Run from the repo root; writes into system_files/usr/share/aurorae/themes/OneClick/."""
import os
OUT = "system_files/usr/share/aurorae/themes/OneClick"
W, H = 46, 32                      # button size
BAR, BAR_INACTIVE, EDGE = "#0b1224", "#0d1528", "#22304d"
FG, FG_DIM = "#ffffff", "#7c8aa5"

def glyph(kind, color):
    cx, cy, s = W / 2, H / 2, 5    # s = half the glyph size
    a = f'stroke="{color}" stroke-width="1.1" fill="none" stroke-linecap="square"'
    if kind == "minimize":
        return f'<path d="M{cx-s} {cy+0.5} H{cx+s}" {a}/>'
    if kind == "maximize":
        return f'<rect x="{cx-s+0.5}" y="{cy-s+0.5}" width="{2*s-1}" height="{2*s-1}" {a}/>'
    if kind == "restore":
        return (f'<rect x="{cx-s+0.5}" y="{cy-s+2.5}" width="{2*s-3}" height="{2*s-3}" {a}/>'
                f'<path d="M{cx-s+2.5} {cy-s+2.5} V{cy-s+0.5} H{cx+s-0.5} V{cy+s-2.5} H{cx+s-2.5}" {a}/>')
    if kind == "close":
        return f'<path d="M{cx-s} {cy-s} L{cx+s} {cy+s} M{cx+s} {cy-s} L{cx-s} {cy+s}" stroke="{color}" stroke-width="1.1" fill="none"/>'

def button(kind):
    red = kind == "close"
    states = [  # id, background, background opacity, glyph colour
        ("active", "#ffffff", 0, FG), ("inactive", "#ffffff", 0, FG_DIM),
        ("hover", "#e81123" if red else "#ffffff", 1 if red else 0.10, FG),
        ("hover-inactive", "#e81123" if red else "#ffffff", 1 if red else 0.10, FG),
        ("pressed", "#f1707a" if red else "#ffffff", 1 if red else 0.18, FG),
        ("pressed-inactive", "#f1707a" if red else "#ffffff", 1 if red else 0.18, FG),
        ("deactivated", "#ffffff", 0, "#4a5670"), ("deactivated-inactive", "#ffffff", 0, "#4a5670"),
    ]
    parts = []
    for i, (sid, bg, op, fg) in enumerate(states):
        parts.append(f'<g id="{sid}-center" transform="translate({i*(W+4)},0)">'
                     f'<rect width="{W}" height="{H}" fill="{bg}" fill-opacity="{op}"/>{glyph(kind, fg)}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{len(states)*(W+4)}" height="{H}">'
            + "".join(parts) + "</svg>")

def frame():
    def nine(prefix, fill, x0):
        b, c = 1, 20  # border thickness, centre size
        el = lambda name, x, y, w, h, col: f'<rect id="{prefix}-{name}" x="{x0+x}" y="{y}" width="{w}" height="{h}" fill="{col}"/>'
        return "".join([
            el("topleft", 0, 0, b, b, EDGE), el("top", b, 0, c, b, EDGE), el("topright", b+c, 0, b, b, EDGE),
            el("left", 0, b, b, c, EDGE), el("center", b, b, c, c, fill), el("right", b+c, b, b, c, EDGE),
            el("bottomleft", 0, b+c, b, b, EDGE), el("bottom", b, b+c, c, b, EDGE), el("bottomright", b+c, b+c, b, b, EDGE)])
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="120" height="30">'
            + nine("decoration", BAR, 0) + nine("decoration-inactive", BAR_INACTIVE, 30)
            + nine("decoration-maximized", BAR, 60) + nine("decoration-maximized-inactive", BAR_INACTIVE, 90) + "</svg>")

os.makedirs(OUT, exist_ok=True)
for k in ("minimize", "maximize", "restore", "close"):
    open(f"{OUT}/{k}.svg", "w").write(button(k))
open(f"{OUT}/decoration.svg", "w").write(frame())
open(f"{OUT}/OneClickrc", "w").write(f"""[General]
ActiveTextColor=255,255,255,255
InactiveTextColor=124,138,165,255
UseTextShadow=false
TitleAlignment=Left
TitleVerticalAlignment=Center
Animation=100
ActiveFontBold=false
Shadow=true

[Layout]
BorderLeft=1
BorderRight=1
BorderBottom=1
TitleEdgeTop=1
TitleEdgeBottom=0
TitleEdgeLeft=10
TitleEdgeRight=0
TitleEdgeTopMaximized=0
TitleEdgeBottomMaximized=0
TitleEdgeLeftMaximized=10
TitleEdgeRightMaximized=0
TitleBorderLeft=6
TitleBorderRight=6
TitleHeight={H}
ButtonWidth={W}
ButtonHeight={H}
ButtonSpacing=0
ButtonMarginTop=0
ExplicitButtonSpacer=8
PaddingTop=0
PaddingBottom=0
PaddingLeft=0
PaddingRight=0
""")
open(f"{OUT}/metadata.desktop", "w").write("""[Desktop Entry]
Name=OneClick
Comment=Flat title bar with classic minimise, maximise and close buttons
X-KDE-PluginInfo-Name=OneClick
X-KDE-PluginInfo-Version=0.1
X-KDE-PluginInfo-License=Apache-2.0
X-KDE-PluginInfo-EnabledByDefault=true
""")
print("wrote", os.listdir(OUT))
