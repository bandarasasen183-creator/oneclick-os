#!/bin/bash
# Runs once, inside the image, while it is being built. Everything OneClick OS
# changes on top of the base image happens here or in system_files/.
set -ouex pipefail

source /ctx/brand.env

# Sets a system-wide default for a desktop setting. kwriteconfig6 merges into the
# file, so the base image's other settings survive. Fedora keeps its own defaults
# in a second folder that wins over /etc/xdg, so write there too when it has the file.
FEDORA_XDG=/usr/share/kde-settings/kde-profile/default/xdg
setcfg() {
    local file=$1 group=$2 key=$3 value=$4
    kwriteconfig6 --file "/etc/xdg/${file}" --group "${group}" --key "${key}" "${value}"
    if [[ -f "${FEDORA_XDG}/${file}" ]]; then
        kwriteconfig6 --file "${FEDORA_XDG}/${file}" --group "${group}" --key "${key}" "${value}"
    fi
}

### System files (handlers, default app associations, icons, boot settings)
cp -avf /ctx/system_files/. /
chmod 755 /usr/bin/oneclick-open-windows-app /usr/bin/oneclick-update /usr/bin/oneclick-taskbar /usr/libexec/oneclick-update-helper

### Branding
# Only the display name and links change. ID and ID_LIKE stay as the base image set
# them, because the base image's own tools and third-party software check those.
sed -i \
    -e "s|^NAME=.*|NAME=\"${BRAND_NAME}\"|" \
    -e "s|^PRETTY_NAME=.*|PRETTY_NAME=\"${BRAND_NAME}\"|" \
    -e "s|^DEFAULT_HOSTNAME=.*|DEFAULT_HOSTNAME=\"${BRAND_HOSTNAME}\"|" \
    -e "s|^HOME_URL=.*|HOME_URL=\"${BRAND_URL}\"|" \
    -e "s|^DOCUMENTATION_URL=.*|DOCUMENTATION_URL=\"${BRAND_URL}\"|" \
    -e "s|^SUPPORT_URL=.*|SUPPORT_URL=\"${BRAND_URL}/issues\"|" \
    -e "s|^BUG_REPORT_URL=.*|BUG_REPORT_URL=\"${BRAND_URL}/issues\"|" \
    /usr/lib/os-release
echo "${IMAGE_NAME}" > /usr/share/oneclick-variant
mkdir -p /usr/share/oneclick
cp /ctx/VERSION /usr/share/oneclick/version
echo "${IMAGE_REGISTRY}/${IMAGE_NAME}" > /usr/share/oneclick/image

### Our own Settings pages (compiled in the first stage of the Containerfile)
cp -a /ctx/pages/. /
install -Dm644 /usr/share/icons/OneClick/scalable/places/start-here.svg /usr/share/pixmaps/oneclick-logo.svg

### Welcome window (shown once after first login)
setcfg plasma-welcomerc General IntroText "Welcome to ${BRAND_NAME}. Everything is already set up: your drivers, your apps and your games library are ready to go. This short tour shows you where things are."
setcfg plasma-welcomerc General IntroIcon "file:///usr/share/pixmaps/oneclick-logo.svg"
setcfg plasma-welcomerc General IntroIconLink "${BRAND_URL}"
setcfg plasma-welcomerc General IntroIconCaption "${BRAND_NAME}"

### Desktop defaults (system-wide, so they apply to every new user)
# Double-click opens, single-click selects, like Windows Explorer.
setcfg kdeglobals KDE SingleClick false

### Icons
# Papirus is the base icon set; the OneClick theme sits on top with our own icons.
dnf5 install -y papirus-icon-theme
PLACES=/usr/share/icons/OneClick/scalable/places
for name in start-here-kde start-here-kde-symbolic start-here-kde-plasma start-here-symbolic; do
    cp "${PLACES}/start-here.svg" "${PLACES}/${name}.svg"
done
python3 /ctx/fill_icon_gaps.py /usr/share/icons/OneClick /usr/share/icons/Papirus
gtk-update-icon-cache -f /usr/share/icons/OneClick || true
setcfg kdeglobals Icons Theme OneClick

### Animations
# Lively window effects on by default. Each is a normal switch in Settings, so anyone can turn it off.
setcfg kwinrc Plugins wobblywindowsEnabled true
setcfg kwinrc Plugins magiclampEnabled true
setcfg kwinrc Plugins squashEnabled false
setcfg kwinrc Plugins sheetEnabled true
setcfg kwinrc Plugins dimscreenEnabled true
setcfg kwinrc Plugins glideEnabled true
setcfg kwinrc Plugins scaleEnabled false
setcfg kwinrc Plugins fadeEnabled false

### Start-up screen
# Replace the scrolling text with a graphical splash: our animated logo.
# (system_files adds the "quiet rhgb" kernel options and the unit that hides the text boot menu.)
# Our own animated theme: the word OneClick is written by hand and the dot of the i bounces
# into place. It uses Plymouth's script engine, which is a separate small package.
dnf5 install -y plymouth-plugin-script
PLY=/usr/share/plymouth/themes
mkdir -p "${PLY}/oneclick"
cp /ctx/boot/plymouth/* "${PLY}/oneclick/"
plymouth-set-default-theme oneclick
systemctl enable oneclick-hide-boot-menu.service
# The splash lives in the early-boot image, so rebuild that image to pick up the logo.
KVER="$(ls /usr/lib/modules | sort -V | tail -1)"
DRACUT_NO_XATTR=1 dracut --no-hostonly --kver "${KVER}" --reproducible --add ostree \
    -f "/usr/lib/modules/${KVER}/initramfs.img"
chmod 0600 "/usr/lib/modules/${KVER}/initramfs.img"

### The OneClick look (colours, wallpaper, taskbar layout, login-to-desktop splash)
# Colour scheme: Breeze Dark's structure with our deep navy and teal.
SCHEMES=/usr/share/color-schemes
sed -e 's/^Name=.*/Name=OneClick Dark/' \
    -e '/^Name\[/d' \
    -e 's/^ColorScheme=.*/ColorScheme=OneClickDark/' \
    -e 's/61,174,233/45,212,191/g' \
    -e 's/29,153,243/34,211,238/g' \
    -e 's/32,35,38/11,18,36/g' \
    -e 's/20,22,24/6,11,24/g' \
    -e 's/41,44,48/20,30,52/g' \
    -e 's/49,54,59/20,30,52/g' \
    -e 's/35,38,41/11,18,36/g' \
    -e 's/42,46,50/14,22,42/g' \
    -e 's/27,30,32/8,14,30/g' \
    "${SCHEMES}/BreezeDark.colors" > "${SCHEMES}/OneClickDark.colors"
# Make it the default look for every new user, and use our wallpaper on the lock screen.
setcfg kdeglobals KDE LookAndFeelPackage org.oneclick.desktop
# Plasma swaps the look to follow light/dark mode by default, which is what switched
# testers back to stock Breeze Dark. Point both modes at ours and turn the swap off.
setcfg kdeglobals KDE DefaultLightLookAndFeel org.oneclick.desktop
setcfg kdeglobals KDE DefaultDarkLookAndFeel org.oneclick.desktop
setcfg kdeglobals KDE AutomaticLookAndFeel false
setcfg kdeglobals General ColorScheme OneClickDark
setcfg kdeglobals General AccentColor 45,212,191
setcfg ksplashrc KSplash Theme org.oneclick.desktop
kwriteconfig6 --file /etc/xdg/kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image \
    --group General --key Image "file:///usr/share/wallpapers/OneClick/"
# Window title bars: bigger buttons, title on the left, like Windows.
setcfg breezerc Windeco ButtonSize ButtonLarge
setcfg breezerc Windeco TitleAlignment AlignLeft

### Plain names instead of project names
# Menus, search and the taskbar show these. Only the visible names change; the programs are the same.
rename() {  # rename <file in /usr/share/applications> <new name> [new generic name]
    local f="/usr/share/applications/$1"
    [[ -f "$f" ]] || return 0
    sed -i -e "s|^Name=.*|Name=$2|" -e '/^Name\[/d' "$f"
    if [[ -n "${3:-}" ]]; then sed -i -e "s|^GenericName=.*|GenericName=$3|" -e '/^GenericName\[/d' "$f"; fi
}
rename org.kde.dolphin.desktop          "Files"            "File manager"
rename org.kde.konsole.desktop          "Terminal"         "Command line"
rename org.kde.discover.desktop         "App Store"        "Install apps"
rename org.kde.kwrite.desktop           "Text Editor"      "Text editor"
rename org.kde.spectacle.desktop        "Screenshot"       "Take a screenshot"
rename org.kde.ark.desktop              "Archives"         "Open and make zip files"
rename org.kde.filelight.desktop        "Disk Usage"       "See what is using space"
rename org.kde.kcharselect.desktop      "Characters"       "Special characters"
rename org.kde.kfind.desktop            "Find Files"       "Search for files"
rename org.kde.krfb.desktop             "Share My Screen"  "Let someone see your screen"
rename org.kde.kwalletmanager.desktop   "Passwords"        "Saved passwords"
rename org.kde.partitionmanager.desktop "Disks"            "Manage disks"
rename org.kde.kdeconnect.app.desktop   "Phone Link"       "Connect your phone"
rename org.kde.kdeconnect.sms.desktop   "Phone Messages"   "Text from your PC"
rename org.kde.plasma-systemmonitor.desktop "Task Manager" "See what is running"
rename org.kde.kjournaldbrowser.desktop "System Logs"      "System logs"
rename org.kde.kmenuedit.desktop        "Edit Start Menu"  "Change the start menu"
rename org.kde.drkonqi.coredump.gui.desktop "Problem Reports" "Apps that closed unexpectedly"
rename org.kde.plasma-welcome.desktop   "Welcome"          "Welcome tour"
rename kdesystemsettings.desktop        "Settings"         "Settings"
rename systemsettings.desktop           "Settings"         "Settings"
rename org.kde.kinfocenter.desktop      "About This PC"    "Hardware and system details"
rename org.kde.khelpcenter.desktop      "Help"             "Help"
# Settings pages that name the project behind them
rename kcm_kwallet5.desktop             "Saved Passwords"
rename kcm_desktoptheme.desktop         "Taskbar Style"
rename kcm_krunnersettings.desktop      "Search Bar"
rename kcm_kwin_scripts.desktop         "Window Scripts"
rename kcm_plasmasearch.desktop         "Search"
rename kcm_qtquicksettings.desktop      "Graphics Renderer"

### No KDE feedback page
# The User Feedback page sends usage data to KDE. OneClick collects nothing, so the page and the
# feedback prompts are removed and the setting is pinned off.
rm -f /usr/share/applications/kcm_feedback.desktop \
      /usr/lib64/qt6/plugins/plasma/kcms/systemsettings/kcm_feedback.so
setcfg PlasmaUserFeedback Global FeedbackLevel 0
kwriteconfig6 --file /etc/xdg/PlasmaUserFeedback --group UserFeedback --key Enabled false

### Terminal: our colours
mkdir -p /usr/share/konsole
cat > /usr/share/konsole/OneClick.colorscheme <<'COLORS'
[General]
Description=OneClick
Opacity=1
Wallpaper=

[Background]
Color=10,16,32
[BackgroundIntense]
Color=14,24,48
[Foreground]
Color=226,232,240
[ForegroundIntense]
Color=255,255,255
[Color0]
Color=30,41,59
[Color0Intense]
Color=71,85,105
[Color1]
Color=248,113,113
[Color1Intense]
Color=252,165,165
[Color2]
Color=45,212,191
[Color2Intense]
Color=94,234,212
[Color3]
Color=250,204,21
[Color3Intense]
Color=253,224,71
[Color4]
Color=96,165,250
[Color4Intense]
Color=147,197,253
[Color5]
Color=192,132,252
[Color5Intense]
Color=216,180,254
[Color6]
Color=34,211,238
[Color6Intense]
Color=103,232,249
[Color7]
Color=203,213,225
[Color7Intense]
Color=248,250,252
COLORS
cat > /usr/share/konsole/OneClick.profile <<'PROFILE'
[Appearance]
ColorScheme=OneClick
Font=Monospace,11,-1,5,400,0,0,0,0,0,0,0,0,0,0,1

[General]
Name=OneClick
Parent=FALLBACK/

[Scrolling]
HistoryMode=2
PROFILE
setcfg konsolerc "Desktop Entry" DefaultProfile OneClick.profile
# Our own welcome line instead of the base system's.
echo "Welcome to ${BRAND_NAME}." > /etc/motd

### Cloud gaming shortcuts (for games whose anti-cheat blocks Linux)
mkdir -p /usr/share/oneclick
for game in "GeForce NOW|https://play.geforcenow.com|nvidia" "Xbox Cloud Gaming|https://www.xbox.com/play|xbox"; do
    IFS='|' read -r name url key <<< "${game}"
    cat > "/usr/share/applications/oneclick-cloud-${key}.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=${name}
Comment=Play games in the cloud, including ones that do not run on Linux
Exec=xdg-open ${url}
Icon=oneclick-cloud-gaming
Categories=Game;
Keywords=fortnite;cloud;stream;games;
DESKTOP
done

### Boot menu: hidden on a PC with only OneClick, shown when another system is installed
cat > /usr/libexec/oneclick-boot-menu <<'BOOTMENU'
#!/usr/bin/bash
# Hides the start-up menu only when OneClick is the only system on the PC.
# On a dual-boot PC the menu stays so the person can pick Windows or OneClick.
if os-prober 2>/dev/null | grep -q . || efibootmgr 2>/dev/null | grep -qi -E "windows|ubuntu|mint|debian|opensuse|arch"; then
    grub2-editenv - unset menu_auto_hide
else
    grub2-editenv - set menu_auto_hide=1
fi
BOOTMENU
chmod 755 /usr/libexec/oneclick-boot-menu
sed -i 's|^ExecStart=.*|ExecStart=/usr/libexec/oneclick-boot-menu|' /usr/lib/systemd/system/oneclick-hide-boot-menu.service

### Preview only: never sleep
# The Mac preview runs in a virtual machine, which freezes for good if the system suspends.
# Real PCs keep normal sleep.
if [[ "${IMAGE_NAME}" == "oneclick-os-preview" ]]; then
    systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target suspend-then-hibernate.target
fi

### One updater only
# The App Store also tried to update the system, and clashed with our Update app
# ("System transaction in progress"). The App Store now only handles apps; system updates
# are ours alone.
dnf5 remove -y plasma-discover-rpm-ostree || true
# The stock "Software Update" page goes too; ours replaces it.
rm -f /usr/share/applications/kcm_updates.desktop /usr/lib64/qt6/plugins/plasma/kcms/systemsettings/kcm_updates.so

### Home-screen corner
# Resting the pointer in the bottom-right corner for a second shows the home screen (desktop),
# where the taskbar is always visible. A safety net for when the taskbar is hidden.
setcfg kwinrc ElectricBorders BottomRight ShowDesktop
setcfg kwinrc Windows ElectricBorderDelay 1000
setcfg kwinrc Windows ElectricBorderCooldown 800
