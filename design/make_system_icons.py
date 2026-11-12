#!/usr/bin/env python3
"""Draws two icon families for the OneClick theme. Run from the repo root.

1. Settings pages: a coloured rounded tile with a white symbol, one per Settings page or category.
2. Tray: thin white line icons for the corner of the taskbar (sound, network, notifications...).
   They use the desktop's text colour, so they stay readable on light and dark taskbars."""
import os

ROOT = "system_files/usr/share/icons/OneClick/scalable"
W = 'fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"'
F = 'fill="#fff"'

def tile(color, glyph):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            f'<rect x="4" y="4" width="56" height="56" rx="14" fill="{color}"/>{glyph}</svg>\n')

# name of drawing -> (tile colour, symbol, icon names it answers to)
SETTINGS = {
    "bluetooth": ("#2563eb", f'<path d="M22 23l20 18-10 9V14l10 9-20 18" {W}/>',
                  ["preferences-system-bluetooth", "bluetooth", "preferences-system-bluetooth-activated"]),
    "network": ("#0ea5e9", f'<path d="M13 27a27 27 0 0 1 38 0M21 36a16 16 0 0 1 22 0" {W}/><circle cx="32" cy="45" r="3.5" {F}/>',
                ["preferences-system-network", "preferences-system-network-connection", "network-wireless"]),
    "power": ("#16a34a", f'<rect x="12" y="23" width="34" height="18" rx="4" {W}/><path d="M51 29v6" {W}/><path d="M31 26l-6 7h8l-6 7" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
              ["preferences-system-power-management", "preferences-system-power"]),
    "users": ("#7c3aed", f'<circle cx="32" cy="25" r="8" {W}/><path d="M17 49a15 15 0 0 1 30 0" {W}/>',
              ["preferences-system-users", "preferences-desktop-user", "system-users"]),
    "session": ("#64748b", f'<path d="M29 17H19v30h10M28 32h19M40 24l8 8-8 8" {W}/>',
                ["preferences-system-login", "system-log-out", "preferences-system-session-services"]),
    "sound": ("#db2777", f'<path d="M14 27h8l10-9v28l-10-9h-8z" {F} stroke="#fff" stroke-width="2" stroke-linejoin="round"/><path d="M40 25a10 10 0 0 1 0 14M46 19a18 18 0 0 1 0 26" {W}/>',
              ["preferences-desktop-sound", "preferences-desktop-multimedia", "emblem-music-symbolic"]),
    "display": ("#0284c7", f'<rect x="12" y="15" width="40" height="26" rx="3" {W}/><path d="M24 50h16M32 41v9" {W}/>',
                ["preferences-desktop-display", "preferences-desktop-display-randr", "preferences-desktop-display-color"]),
    "keyboard": ("#475569", f'<rect x="10" y="19" width="44" height="26" rx="4" {W}/><path d="M18 28h1M27 28h1M36 28h1M45 28h1M22 37h20" {W}/>',
                 ["preferences-desktop-keyboard", "input-keyboard", "input-keyboard-virtual", "preferences-desktop-keyboard-shortcut"]),
    "mouse": ("#525f7a", f'<rect x="21" y="12" width="22" height="40" rx="11" {W}/><path d="M32 20v8" {W}/>',
              ["preferences-desktop-mouse", "preferences-desktop-peripherals", "preferences-desktop-touchpad", "input-mouse"]),
    "printer": ("#57534e", f'<path d="M20 24V13h24v11M20 44h-6V26a2 2 0 0 1 2-2h32a2 2 0 0 1 2 2v18h-6" {W}/><rect x="20" y="37" width="24" height="14" rx="1" {W}/>',
                ["preferences-devices-printer", "printer"]),
    "wallpaper": ("#0d9488", f'<rect x="11" y="15" width="42" height="34" rx="4" {W}/><path d="M12 43l11-11 9 9 6-6 14 13" {W}/><circle cx="42" cy="25" r="3" {F}/>',
                  ["preferences-desktop-wallpaper"]),
    "notifications": ("#ea580c", f'<path d="M19 43V30a13 13 0 0 1 26 0v13l4 4H15z" {W}/><path d="M28 51a4 4 0 0 0 8 0" {W}/>',
                      ["preferences-desktop-notification-bell", "preferences-desktop-notification"]),
    "time": ("#4f46e5", f'<circle cx="32" cy="32" r="18" {W}/><path d="M32 21v11l7 5" {W}/>',
             ["preferences-system-time"]),
    "language": ("#0891b2", f'<circle cx="32" cy="32" r="18" {W}/><path d="M14 32h36M32 14c-8 6-8 30 0 36M32 14c8 6 8 30 0 36" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>',
                 ["preferences-desktop-locale"]),
    "accessibility": ("#1d4ed8", f'<circle cx="32" cy="15" r="4" {F}/><path d="M17 24h30M32 24v14M32 38l-8 13M32 38l8 13" {W}/>',
                      ["preferences-desktop-accessibility"]),
    "colours": ("#1e293b", '<circle cx="32" cy="24" r="11" fill="#f43f5e"/><circle cx="24" cy="38" r="11" fill="#22c55e" fill-opacity="0.9"/><circle cx="40" cy="38" r="11" fill="#3b82f6" fill-opacity="0.9"/>',
                ["preferences-desktop-color", "preferences-desktop-theme-global", "preferences-desktop-theme"]),
    "fonts": ("#b45309", f'<path d="M14 46l10-27 10 27M18 37h12M37 46l6-16 6 16M39.500 41h7" {W}/>',
              ["preferences-desktop-font", "preferences-desktop-font-installer"]),
    "quick": ("#0f766e", f'<path d="M14 22h36M14 32h36M14 42h36" {W}/><circle cx="24" cy="22" r="5" fill="#0f766e" stroke="#fff" stroke-width="4"/><circle cx="40" cy="32" r="5" fill="#0f766e" stroke="#fff" stroke-width="4"/><circle cx="28" cy="42" r="5" fill="#0f766e" stroke="#fff" stroke-width="4"/>',
              ["preferences-desktop"]),
    "lock": ("#ca8a04", f'<rect x="16" y="29" width="32" height="22" rx="4" {W}/><path d="M23 29v-6a9 9 0 0 1 18 0v6" {W}/><circle cx="32" cy="40" r="2.500" {F}/>',
             ["preferences-desktop-user-password", "system-lock-screen"]),
    "security": ("#15803d", f'<path d="M32 12l17 6v12c0 11-7 18-17 22-10-4-17-11-17-22V18z" {W}/><path d="M24 32l6 6 10-11" {W}/>',
                 ["preferences-security"]),
    "autostart": ("#e11d48", f'<path d="M24 18l22 14-22 14z" {F} stroke="#fff" stroke-width="4" stroke-linejoin="round"/>',
                  ["system-run"]),
    "disks": ("#44546f", f'<rect x="12" y="17" width="40" height="30" rx="5" {W}/><path d="M12 36h40M20 42h10" {W}/><circle cx="44" cy="42" r="1.500" {F}/>',
              ["preferences-system-disks", "camera-photo", "preferences-smart-status"]),
    "windows": ("#3b5bdb", f'<rect x="12" y="15" width="30" height="24" rx="3" {W}/><path d="M22 39v7a3 3 0 0 0 3 3h24a3 3 0 0 0 3-3V28a3 3 0 0 0-3-3h-7" {W}/>',
                ["preferences-system-windows", "preferences-system-windows-actions", "preferences-system-tabbox", "preferences-desktop-virtual"]),
    "search": ("#9333ea", f'<circle cx="28" cy="28" r="12" {W}/><path d="M37 37l12 12" {W}/>',
               ["preferences-desktop-search", "preferences-desktop-baloo", "plasma-search", "krunner"]),
    "defaultapps": ("#0369a1", f'<rect x="13" y="13" width="15" height="15" rx="3" {W}/><rect x="36" y="13" width="15" height="15" rx="3" {W}/><rect x="13" y="36" width="15" height="15" rx="3" {W}/><path d="M37 44l5 5 9-11" {W}/>',
                    ["preferences-desktop-default-applications", "preferences-desktop-filetype-association"]),
    "touch": ("#be185d", f'<path d="M26 34V18a4 4 0 0 1 8 0v12l10 2a5 5 0 0 1 4 6l-2 10a5 5 0 0 1-5 4H31a5 5 0 0 1-4-2l-9-12a3.500 3.500 0 0 1 5-5z" {W}/>',
              ["preferences-desktop-touchscreen", "preferences-desktop-tablet", "preferences-desktop-gaming"]),
    "nightlight": ("#b45309", f'<path d="M44 37a15 15 0 0 1-18-18 15 15 0 1 0 18 18z" {W}/>',
                   ["redshift-status-on", "lighttable", "preferences-desktop-effects", "preferences-desktop-animations"]),
    "about": ("#0e7490", f'<circle cx="32" cy="32" r="19" {W}/><path d="M32 30v13" {W}/><circle cx="32" cy="22" r="2.800" {F}/>',
              ["ktip", "help-about", "preferences-desktop-feedback"]),
    "trash": ("#6b7280", f'<path d="M15 20h34M26 20v-5h12v5M19 20l2 28a3 3 0 0 0 3 3h16a3 3 0 0 0 3-3l2-28M28 28v15M36 28v15" {W}/>',
              ["user-trash", "user-trash-full", "trash-empty"]),
}

# --- Tray icons: 22px grid, drawn in the taskbar's text colour ---------------------------
T = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
TF = 'fill="currentColor"'
DIM = 'opacity="0.35"'

def tray(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 22">'
            '<style type="text/css" id="current-color-scheme">.ColorScheme-Text{color:#fcfcfc;}</style>'
            f'<g class="ColorScheme-Text">{body}</g></svg>\n')

SPEAKER = f'<path d="M3 8.500h3l4-3.500v12l-4-3.500H3z" {TF} stroke="currentColor" stroke-width="1.200" stroke-linejoin="round"/>'
WAVE1 = f'<path d="M13 8.800a3.200 3.200 0 0 1 0 4.400" {T}/>'
WAVE2 = f'<path d="M15.300 6.500a6.400 6.400 0 0 1 0 9" {T}/>'
WAVE3 = f'<path d="M17.600 4.300a9.500 9.500 0 0 1 0 13.400" {T}/>'
BELL = f'<path d="M6 15V10a5 5 0 0 1 10 0v5l1.500 1.800h-13z" {T}/><path d="M9.300 19a1.800 1.800 0 0 0 3.400 0" {T}/>'
PLUG = f'<rect x="3" y="5" width="16" height="10" rx="1.500" {T}/><path d="M7 15v3h8v-3M8 8.500v2.500M11 8.500v2.500M14 8.500v2.500" {T}/>'
SLASH = f'<path d="M3.500 3.500l15 15" {T}/>'

def wifi(level):  # level 0-4 arcs lit
    arcs = ['<circle cx="11" cy="16.500" r="1.300" %s %s/>',
            '<path d="M7.600 13.200a4.800 4.800 0 0 1 6.800 0" %s %s/>',
            '<path d="M5 10.400a8.500 8.500 0 0 1 12 0" %s %s/>',
            '<path d="M2.400 7.600a12.200 12.200 0 0 1 17.200 0" %s %s/>']
    out = ""
    for i, a in enumerate(arcs):
        style = TF if i == 0 else T
        out += a % (style, "" if level > i or (i == 0 and level > 0) else DIM)
    return out

SUN = (f'<circle cx="11" cy="11" r="3.400" {T}/>'
       f'<path d="M11 2.500v2M11 17.500v2M2.500 11h2M17.500 11h2M5 5l1.400 1.400M15.600 15.600L17 17M5 17l1.400-1.400M15.600 6.400L17 5" {T}/>')

TRAY = {
    "audio-high": (SPEAKER + WAVE1 + WAVE2 + WAVE3, ["audio-volume-high", "audio-volume-high-panel", "audio-volume-high-symbolic", "audio-volume-high-warning", "audio-volume-high-danger"]),
    "audio-medium": (SPEAKER + WAVE1 + WAVE2, ["audio-volume-medium", "audio-volume-medium-panel", "audio-volume-medium-symbolic"]),
    "audio-low": (SPEAKER + WAVE1, ["audio-volume-low", "audio-volume-low-panel", "audio-volume-low-symbolic", "audio-volume-low-zero-panel"]),
    "audio-muted": (SPEAKER + f'<path d="M14 8.500l5 5M19 8.500l-5 5" {T}/>', ["audio-volume-muted", "audio-volume-muted-panel", "audio-volume-muted-symbolic", "audio-volume-off", "audio-volume-muted-blocking", "audio-volume-muted-blocking-panel", "audio-volume-muted-blocked-panel"]),
    "bell": (BELL, ["notifications", "notification-inactive", "notification-symbolic", "preferences-desktop-notification-symbolic"]),
    "bell-new": (BELL + f'<circle cx="16.500" cy="5.500" r="2.600" fill="#2dd4bf"/>', ["notification-active", "notification-new"]),
    "bell-off": (BELL + SLASH, ["notifications-disabled", "notification-disabled"]),
    "wired": (PLUG, ["network-wired", "network-wired-activated", "network-wired-secure", "network-wired-activated-locked", "network-wired-symbolic"]),
    "wired-off": (f'<g {DIM}>{PLUG}</g>' + SLASH, ["network-wired-unavailable", "network-wired-disconnected", "network-wired-offline", "network-wired-no-route", "network-wired-available", "network-offline-symbolic"]),
    "wired-busy": (f'<g opacity="0.6">{PLUG}</g>', ["network-wired-acquiring"]),
    "wifi-4": (wifi(4), ["network-wireless-connected-100", "network-wireless-signal-excellent", "network-wireless-connected", "network-wireless-symbolic", "network-wireless-signal-excellent-symbolic"]),
    "wifi-3": (wifi(3), ["network-wireless-connected-75", "network-wireless-signal-good", "network-wireless-signal-good-symbolic"]),
    "wifi-2": (wifi(2), ["network-wireless-connected-50", "network-wireless-signal-ok", "network-wireless-signal-ok-symbolic"]),
    "wifi-1": (wifi(1), ["network-wireless-connected-25", "network-wireless-signal-low", "network-wireless-signal-weak", "network-wireless-signal-weak-symbolic"]),
    "wifi-0": (wifi(0), ["network-wireless-connected-00", "network-wireless-signal-none", "network-wireless-signal-none-symbolic", "network-wireless-disconnected"]),
    "brightness": (SUN, ["brightness-systray", "brightness", "brightness-high", "brightness-high-symbolic", "brightness-medium-symbolic", "brightness-low-symbolic", "brightness-symbolic", "display-brightness", "display-brightness-symbolic", "display-brightness-high-symbolic", "display-brightness-medium-symbolic", "display-brightness-low-symbolic", "video-display-brightness", "brightnesssettings"]),
    "desktop": (f'<rect x="3" y="4.500" width="16" height="11" rx="1.500" {T}/><path d="M8 18.500h6" {T}/>', ["user-desktop", "user-desktop-symbolic", "desktop", "desktop-symbolic"]),
    "bluetooth": (f'<path d="M7 7.500l8 7-4 3.500V4l4 3.500-8 7" {T}/>', ["bluetooth-active", "bluetooth-active-symbolic", "preferences-system-bluetooth-symbolic"]),
    "clipboard": (f'<rect x="5" y="4.500" width="12" height="14.500" rx="1.500" {T}/><path d="M8.500 4.500v-1.500h5v1.500M8.500 10h5M8.500 13.500h3" {T}/>', ["klipper", "klipper-symbolic", "edit-paste-symbolic"]),
}

def clean(s):  # tidy the number formatting used above
    for a, b in ((".500", ".5"), (".200", ".2"), (".300", ".3"), (".400", ".4"), (".600", ".6"), (".800", ".8")):
        s = s.replace(a, b)
    return s

os.makedirs(f"{ROOT}/apps", exist_ok=True); os.makedirs(f"{ROOT}/panel", exist_ok=True)
n = 0
for key, (color, glyph, names) in SETTINGS.items():
    for name in [f"oneclick-settings-{key}"] + names:
        open(f"{ROOT}/apps/{name}.svg", "w").write(clean(tile(color, glyph))); n += 1
for key, (body, names) in TRAY.items():
    for name in [f"oneclick-tray-{key}"] + names:
        open(f"{ROOT}/panel/{name}.svg", "w").write(clean(tray(body))); n += 1
print(len(SETTINGS), "settings icons,", len(TRAY), "tray icons,", n, "files")
