#!/usr/bin/env python3
"""Draws the OneClick app icons: flat objects with simple two-tone shading, no glow.
Run from the repo root. Writes SVGs into the OneClick icon theme and copies each one
under every name the app might ask for, so the icon shows wherever the app appears."""
import os

OUT = "system_files/usr/share/icons/OneClick/scalable/apps"
HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'

ICONS = {
    # Files: a folder, back flap darker than the front.
    "files": """
  <path d="M6 16a4 4 0 0 1 4-4h14l5 5h25a4 4 0 0 1 4 4v29a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4z" fill="#e8a317"/>
  <path d="M6 24a4 4 0 0 1 4-4h44a4 4 0 0 1 4 4v26a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4z" fill="#ffc83d"/>
  <rect x="6" y="20" width="52" height="3" fill="#ffd96a"/>""",

    # Settings: a gear, with a lighter inner ring.
    "settings": """
  <path d="M28 6h8l1.3 6.2a20 20 0 0 1 5.1 2.1l5.3-3.5 5.6 5.6-3.5 5.3a20 20 0 0 1 2.1 5.1L58 28v8l-6.2 1.3a20 20 0 0 1-2.1 5.1l3.5 5.3-5.6 5.6-5.3-3.5a20 20 0 0 1-5.1 2.1L36 58h-8l-1.3-6.2a20 20 0 0 1-5.1-2.1l-5.3 3.5-5.6-5.6 3.5-5.3a20 20 0 0 1-2.1-5.1L6 36v-8l6.2-1.3a20 20 0 0 1 2.1-5.1l-3.5-5.3 5.6-5.6 5.3 3.5a20 20 0 0 1 5.1-2.1z" fill="#5b6b86"/>
  <circle cx="32" cy="32" r="13" fill="#8a9ab5"/>
  <circle cx="32" cy="32" r="6" fill="#2b3550"/>""",

    # App store: a shopping bag with the OneClick ring on it.
    "store": """
  <path d="M22 20v-4a10 10 0 0 1 20 0v4" fill="none" stroke="#1e3a8a" stroke-width="4" stroke-linecap="round"/>
  <path d="M10 22a3 3 0 0 1 3-3h38a3 3 0 0 1 3 3l-2 30a4 4 0 0 1-4 4H16a4 4 0 0 1-4-4z" fill="#3b82f6"/>
  <path d="M10 22a3 3 0 0 1 3-3h38a3 3 0 0 1 3 3l-0.3 4H10.3z" fill="#60a5fa"/>
  <path d="M27.5 32.5a8 8 0 1 0 9 0" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>
  <circle cx="32" cy="30.5" r="2.3" fill="#fff"/>""",

    # Terminal: a dark window with a prompt.
    "terminal": """
  <rect x="6" y="10" width="52" height="44" rx="5" fill="#1f2937"/>
  <path d="M6 15a5 5 0 0 1 5-5h42a5 5 0 0 1 5 5v4H6z" fill="#374151"/>
  <path d="M15 30l7 6-7 6" fill="none" stroke="#2dd4bf" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M27 43h12" stroke="#e5e7eb" stroke-width="3.5" stroke-linecap="round"/>""",

    # Text editor: a page with a folded corner and lines.
    "editor": """
  <path d="M14 6h26l12 12v36a4 4 0 0 1-4 4H14a4 4 0 0 1-4-4V10a4 4 0 0 1 4-4z" fill="#f1f5f9"/>
  <path d="M40 6l12 12H44a4 4 0 0 1-4-4z" fill="#cbd5e1"/>
  <path d="M18 28h28M18 36h28M18 44h18" stroke="#3b82f6" stroke-width="3" stroke-linecap="round"/>""",

    # System monitor: a screen with a pulse line.
    "monitor": """
  <rect x="6" y="10" width="52" height="36" rx="4" fill="#0f766e"/>
  <rect x="10" y="14" width="44" height="28" rx="2" fill="#134e4a"/>
  <path d="M13 30h9l4-9 6 17 5-12 3 4h11" fill="none" stroke="#5eead4" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M24 54h16" stroke="#0f766e" stroke-width="4" stroke-linecap="round"/>
  <path d="M32 46v8" stroke="#0f766e" stroke-width="4"/>""",

    # Screenshot: a frame with corner marks around a small picture.
    "screenshot": """
  <path d="M8 20V12a4 4 0 0 1 4-4h8M44 8h8a4 4 0 0 1 4 4v8M56 44v8a4 4 0 0 1-4 4h-8M20 56h-8a4 4 0 0 1-4-4v-8" fill="none" stroke="#e11d48" stroke-width="4" stroke-linecap="round"/>
  <rect x="17" y="19" width="30" height="26" rx="3" fill="#fda4af"/>
  <path d="M17 39l9-9 7 7 4-4 10 10v2a3 3 0 0 1-3 3H20a3 3 0 0 1-3-3z" fill="#be123c"/>
  <circle cx="39" cy="26" r="3" fill="#fff"/>""",

    # Image viewer: a landscape photo.
    "photos": """
  <rect x="6" y="12" width="52" height="40" rx="5" fill="#0ea5e9"/>
  <circle cx="44" cy="24" r="5" fill="#fde047"/>
  <path d="M6 44l14-14 12 12 8-8 18 18v0a5 5 0 0 1-5 5H11a5 5 0 0 1-5-5z" fill="#16a34a"/>
  <path d="M6 47l14-14 12 12 8-8 18 18" fill="none" stroke="#22c55e" stroke-width="0"/>""",

    # Archive: a box with a zip strip.
    "archive": """
  <path d="M8 18l6-10h36l6 10z" fill="#a16207"/>
  <rect x="8" y="18" width="48" height="38" rx="3" fill="#ca8a04"/>
  <rect x="29" y="18" width="6" height="38" fill="#fde68a"/>
  <path d="M29 24h6M29 30h6M29 36h6M29 42h6" stroke="#a16207" stroke-width="2"/>""",

    # Documents/PDF reader: a page with a red band.
    "reader": """
  <path d="M14 6h26l12 12v36a4 4 0 0 1-4 4H14a4 4 0 0 1-4-4V10a4 4 0 0 1 4-4z" fill="#f8fafc"/>
  <path d="M40 6l12 12H44a4 4 0 0 1-4-4z" fill="#cbd5e1"/>
  <rect x="10" y="34" width="34" height="14" rx="2" fill="#dc2626"/>
  <path d="M15 41h24" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
  <path d="M18 20h16M18 27h22" stroke="#94a3b8" stroke-width="3" stroke-linecap="round"/>""",

    # Updates: a circular arrow around a down arrow.
    "update": """
  <circle cx="32" cy="32" r="26" fill="#2dd4bf"/>
  <path d="M32 18v22M23 32l9 9 9-9" fill="none" stroke="#042f2e" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M21 47h22" stroke="#042f2e" stroke-width="5" stroke-linecap="round"/>""",
}

# Every icon name an app might use, mapped to our drawing.
NAMES = {
    "files": ["org.kde.dolphin", "system-file-manager", "file-manager", "folder-open"],
    "settings": ["systemsettings", "preferences-system", "configure", "org.kde.systemsettings"],
    "store": ["org.kde.discover", "plasmadiscover", "system-software-install", "software-store"],
    "terminal": ["org.kde.konsole", "utilities-terminal", "terminal"],
    "editor": ["org.kde.kwrite", "org.kde.kate", "accessories-text-editor", "text-editor"],
    "monitor": ["org.kde.plasma-systemmonitor", "utilities-system-monitor", "ksysguard"],
    "screenshot": ["org.kde.spectacle", "applets-screenshooter", "spectacle"],
    "photos": ["org.kde.gwenview", "image-viewer", "multimedia-photo-viewer"],
    "archive": ["org.kde.ark", "utilities-file-archiver", "ark"],
    "reader": ["org.kde.okular", "okular", "application-pdf", "x-office-document-viewer"],
    "update": ["oneclick-update", "system-software-update", "software-update-available"],
}

os.makedirs(OUT, exist_ok=True)
for key, body in ICONS.items():
    svg = HEAD + body + "\n</svg>\n"
    for name in [f"oneclick-{key}"] + NAMES[key]:
        open(f"{OUT}/{name}.svg", "w").write(svg)
print(len(ICONS), "icons,", sum(len(v) + 1 for v in NAMES.values()), "files")
