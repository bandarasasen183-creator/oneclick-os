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
    # Character map: a tile with a letter and an accent mark.
    "characters": """
  <rect x="8" y="8" width="48" height="48" rx="8" fill="#7c3aed"/>
  <path d="M22 46l10-26 10 26M26 37h12" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M29 13l6-3" stroke="#ddd6fe" stroke-width="3.5" stroke-linecap="round"/>""",

    # Disk usage: a pie chart.
    "diskusage": """
  <circle cx="32" cy="32" r="25" fill="#f59e0b"/>
  <path d="M32 32V7a25 25 0 0 1 23.5 33.5z" fill="#2563eb"/>
  <path d="M32 32l23.5 8.5A25 25 0 0 1 20 54z" fill="#10b981"/>
  <circle cx="32" cy="32" r="8" fill="#0a1020"/>""",

    # Firewall: a brick wall with a shield.
    "firewall": """
  <rect x="6" y="12" width="52" height="40" rx="3" fill="#c2410c"/>
  <path d="M6 25h52M6 38h52M22 12v13M42 12v13M14 25v13M32 25v13M50 25v13M22 38v14M42 38v14" stroke="#7c2d12" stroke-width="2.5"/>
  <path d="M32 22l12 4v9c0 8-5 13-12 16-7-3-12-8-12-16v-9z" fill="#f8fafc"/>
  <path d="M26.5 35.5l4 4 7-8" fill="none" stroke="#16a34a" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>""",

    # Help: a round badge with a question mark.
    "help": """
  <circle cx="32" cy="32" r="26" fill="#0284c7"/>
  <path d="M24 25a8 8 0 1 1 12 7c-3 2-4 3-4 7" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/>
  <circle cx="32" cy="47" r="3.2" fill="#fff"/>""",

    # About this PC: a computer chip.
    "info": """
  <path d="M20 4v8M32 4v8M44 4v8M20 52v8M32 52v8M44 52v8M4 20h8M4 32h8M4 44h8M52 20h8M52 32h8M52 44h8" stroke="#64748b" stroke-width="4" stroke-linecap="round"/>
  <rect x="10" y="10" width="44" height="44" rx="6" fill="#334155"/>
  <rect x="20" y="20" width="24" height="24" rx="3" fill="#2dd4bf"/>""",

    # Phone link: a phone beside a laptop.
    "phone": """
  <rect x="4" y="14" width="40" height="28" rx="3" fill="#475569"/>
  <rect x="8" y="18" width="32" height="20" rx="1" fill="#93c5fd"/>
  <path d="M2 46h44v2a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3z" fill="#64748b"/>
  <rect x="38" y="22" width="22" height="36" rx="4" fill="#0f172a"/>
  <rect x="41" y="26" width="16" height="26" rx="1" fill="#2dd4bf"/>""",

    # Search: a magnifying glass.
    "search": """
  <path d="M40 40l16 16" stroke="#475569" stroke-width="8" stroke-linecap="round"/>
  <circle cx="27" cy="27" r="19" fill="#475569"/>
  <circle cx="27" cy="27" r="13" fill="#bae6fd"/>
  <path d="M19 26a8 8 0 0 1 8-8" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>""",

    # Menu editor: a list with a pencil.
    "menuedit": """
  <rect x="6" y="8" width="40" height="48" rx="5" fill="#e2e8f0"/>
  <path d="M14 20h24M14 30h24M14 40h14" stroke="#64748b" stroke-width="4" stroke-linecap="round"/>
  <path d="M34 50l3-11 16-16 8 8-16 16z" fill="#f59e0b"/>
  <path d="M34 50l3-11 8 8z" fill="#fde68a"/>
  <path d="M49 27l8 8 3-3a3 3 0 0 0 0-4l-4-4a3 3 0 0 0-4 0z" fill="#ef4444"/>""",

    # Remote desktop: two screens, one inside the other.
    "remote": """
  <rect x="4" y="8" width="56" height="38" rx="4" fill="#1d4ed8"/>
  <rect x="8" y="12" width="48" height="30" rx="2" fill="#60a5fa"/>
  <rect x="26" y="22" width="26" height="17" rx="2" fill="#1e3a8a"/>
  <rect x="28" y="24" width="22" height="13" rx="1" fill="#dbeafe"/>
  <path d="M22 56h20M32 46v10" stroke="#1d4ed8" stroke-width="4" stroke-linecap="round"/>""",

    # Passwords: a key.
    "passwords": """
  <rect x="6" y="6" width="52" height="52" rx="10" fill="#065f46"/>
  <circle cx="24" cy="32" r="9" fill="none" stroke="#fde047" stroke-width="5"/>
  <path d="M33 32h18M44 32v8M51 32v6" fill="none" stroke="#fde047" stroke-width="5" stroke-linecap="round"/>""",

    # Logs: a scroll of lines with a clock.
    "logs": """
  <rect x="8" y="6" width="38" height="52" rx="4" fill="#f1f5f9"/>
  <path d="M15 17h24M15 26h24M15 35h14" stroke="#94a3b8" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="44" cy="44" r="14" fill="#4f46e5"/>
  <path d="M44 36v8l6 4" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>""",

    # Disks: a hard drive.
    "disks": """
  <rect x="6" y="12" width="52" height="40" rx="6" fill="#64748b"/>
  <rect x="6" y="36" width="52" height="16" rx="6" fill="#475569"/>
  <rect x="6" y="36" width="52" height="6" fill="#475569"/>
  <circle cx="47" cy="44" r="3" fill="#2dd4bf"/>
  <path d="M14 44h18" stroke="#94a3b8" stroke-width="3" stroke-linecap="round"/>
  <circle cx="32" cy="24" r="7" fill="#94a3b8"/>
  <circle cx="32" cy="24" r="2.5" fill="#475569"/>""",

    # Emoji picker: a plain smiling face.
    "emoji": """
  <circle cx="32" cy="32" r="26" fill="#facc15"/>
  <circle cx="23" cy="26" r="3.5" fill="#422006"/>
  <circle cx="41" cy="26" r="3.5" fill="#422006"/>
  <path d="M20 37a13 13 0 0 0 24 0" fill="none" stroke="#422006" stroke-width="4" stroke-linecap="round"/>""",

    # Problem reports: a window with a warning triangle.
    "problems": """
  <rect x="6" y="10" width="52" height="44" rx="5" fill="#e2e8f0"/>
  <path d="M6 15a5 5 0 0 1 5-5h42a5 5 0 0 1 5 5v5H6z" fill="#94a3b8"/>
  <path d="M32 25l13 23H19z" fill="#f59e0b" stroke="#f59e0b" stroke-width="3" stroke-linejoin="round"/>
  <path d="M32 33v7" stroke="#422006" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="32" cy="44.5" r="2" fill="#422006"/>""",

    # Developer settings: brackets and a slash.
    "developer": """
  <rect x="6" y="8" width="52" height="48" rx="6" fill="#1e293b"/>
  <path d="M24 22l-10 10 10 10M40 22l10 10-10 10" fill="none" stroke="#2dd4bf" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M35 19l-6 26" stroke="#f8fafc" stroke-width="4" stroke-linecap="round"/>""",

    # Welcome: a waving flag on a pole.
    "welcome": """
  <path d="M14 8v50" stroke="#64748b" stroke-width="5" stroke-linecap="round"/>
  <path d="M16 10c10-5 16 5 26 0 4-2 8-2 12 0v24c-4-2-8-2-12 0-10 5-16-5-26 0z" fill="#2dd4bf"/>
  <path d="M16 22c10-5 16 5 26 0 4-2 8-2 12 0v12c-4-2-8-2-12 0-10 5-16-5-26 0z" fill="#14b8a6"/>""",

    # All apps: a grid of nine squares.
    "allapps": """
  <g fill="#94a3b8"><rect x="8" y="8" width="13" height="13" rx="3"/><rect x="25.5" y="8" width="13" height="13" rx="3"/><rect x="43" y="8" width="13" height="13" rx="3"/>
  <rect x="8" y="25.5" width="13" height="13" rx="3"/><rect x="25.5" y="25.5" width="13" height="13" rx="3" fill="#2dd4bf"/><rect x="43" y="25.5" width="13" height="13" rx="3"/>
  <rect x="8" y="43" width="13" height="13" rx="3"/><rect x="25.5" y="43" width="13" height="13" rx="3"/><rect x="43" y="43" width="13" height="13" rx="3"/></g>""",

    # Favourites: a star.
    "favourites": """
  <path d="M32 6l7.8 16.6 18.2 2.400-13.3 12.700 3.3 18.1L32 47l-16 8.8 3.3-18.1L6 25l18.2-2.400z" fill="#facc15" stroke="#facc15" stroke-width="3" stroke-linejoin="round"/>""",

    # Internet: a globe.
    "internet": """
  <circle cx="32" cy="32" r="26" fill="#0ea5e9"/>
  <path d="M6 32h52M32 6c-9 7-9 45 0 52M32 6c9 7 9 45 0 52M10 19h44M10 45h44" fill="none" stroke="#e0f2fe" stroke-width="3"/>""",

    # Utilities: a toolbox.
    "utilities": """
  <path d="M24 18v-4a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v4" fill="none" stroke="#7f1d1d" stroke-width="4"/>
  <rect x="6" y="18" width="52" height="36" rx="5" fill="#dc2626"/>
  <rect x="6" y="30" width="52" height="5" fill="#7f1d1d"/>
  <rect x="27" y="27" width="10" height="11" rx="2" fill="#fde047"/>""",
}

# Every icon name an app might use, mapped to our drawing.
NAMES = {
    "files": ["org.kde.dolphin", "system-file-manager", "file-manager"],
    "settings": ["systemsettings", "preferences-system", "applications-system", "applications-system-symbolic", "configure", "org.kde.systemsettings"],
    "store": ["org.kde.discover", "plasmadiscover", "system-software-install", "software-store"],
    "terminal": ["org.kde.konsole", "utilities-terminal", "terminal"],
    "editor": ["org.kde.kwrite", "kwrite", "kate", "org.kde.kate", "accessories-text-editor", "text-editor"],
    "monitor": ["org.kde.plasma-systemmonitor", "utilities-system-monitor", "ksysguard"],
    "screenshot": ["org.kde.spectacle", "applets-screenshooter", "spectacle"],
    "photos": ["org.kde.gwenview", "image-viewer", "multimedia-photo-viewer"],
    "archive": ["org.kde.ark", "utilities-file-archiver", "ark"],
    "reader": ["org.kde.okular", "okular", "application-pdf", "x-office-document-viewer"],
    "update": ["oneclick-update", "system-software-update", "software-update-available"],
    "characters": ["accessories-character-map", "org.kde.kcharselect"],
    "diskusage": ["filelight", "org.kde.filelight", "baobab"],
    "firewall": ["firewall-config", "preferences-security-firewall"],
    "help": ["help-browser", "system-help", "org.kde.khelpcenter", "help-contents"],
    "info": ["hwinfo", "org.kde.kinfocenter", "kinfocenter", "computer"],
    "phone": ["kdeconnect", "org.kde.kdeconnect", "kdeconnectindicator"],
    "search": ["kfind", "org.kde.kfind", "system-search"],
    "menuedit": ["kmenuedit", "org.kde.kmenuedit"],
    "remote": ["krfb", "org.kde.krfb", "preferences-desktop-remote-desktop", "krdc"],
    "passwords": ["kwalletmanager", "kwalletmanager5", "org.kde.kwalletmanager", "dialog-password"],
    "logs": ["org.kde.kjournaldbrowser", "utilities-log-viewer"],
    "disks": ["partitionmanager", "org.kde.partitionmanager", "drive-harddisk"],
    "emoji": ["preferences-desktop-emoticons", "org.kde.plasma.emojier"],
    "problems": ["tools-report-bug", "org.kde.drkonqi", "drkonqi"],
    "developer": ["debug-run", "applications-development", "applications-development-symbolic", "applications-engineering"],
    "welcome": ["org.kde.plasma-welcome", "start-here-kde-plasma-welcome"],
    "allapps": ["applications-all", "applications-all-symbolic", "applications-other", "view-grid", "view-list-icons"],
    "favourites": ["bookmarks", "bookmarks-symbolic", "favorites", "favorite", "starred"],
    "internet": ["applications-internet", "applications-internet-symbolic", "applications-network"],
    "utilities": ["applications-utilities", "applications-utilities-symbolic", "applications-accessories"],
}

os.makedirs(OUT, exist_ok=True)
for key, body in ICONS.items():
    svg = HEAD + body + "\n</svg>\n"
    for name in [f"oneclick-{key}"] + NAMES[key]:
        open(f"{OUT}/{name}.svg", "w").write(svg)
print(len(ICONS), "icons,", sum(len(v) + 1 for v in NAMES.values()), "files")
