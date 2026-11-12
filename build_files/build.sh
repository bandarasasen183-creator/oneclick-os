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
chmod 755 /usr/bin/oneclick-open-windows-app

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
# Our own animated theme: 60 frames of the logo drawing itself. The password-prompt
# images come from the stock theme so encrypted disks still get a proper prompt.
PLY=/usr/share/plymouth/themes
mkdir -p "${PLY}/oneclick"
cp /ctx/boot/plymouth/* "${PLY}/oneclick/"
for img in lock entry bullet capslock keyboard keymap-render; do
    cp "${PLY}/spinner/${img}.png" "${PLY}/oneclick/" || true
done
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
setcfg kdeglobals General ColorScheme OneClickDark
setcfg kdeglobals General AccentColor 45,212,191
setcfg ksplashrc KSplash Theme org.oneclick.desktop
kwriteconfig6 --file /etc/xdg/kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image \
    --group General --key Image "file:///usr/share/wallpapers/OneClick/"
# Window title bars: bigger buttons, title on the left, like Windows.
setcfg breezerc Windeco ButtonSize ButtonLarge
setcfg breezerc Windeco TitleAlignment AlignLeft
