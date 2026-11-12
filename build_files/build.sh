#!/bin/bash
# Runs once, inside the image, while it is being built. Everything OneClick OS
# changes on top of the base image happens here or in system_files/.
set -ouex pipefail

source /ctx/brand.env

### System files (handlers, default app associations)
cp -avf /ctx/system_files/. /
chmod 755 /usr/bin/oneclick-open-windows-app

### Branding
# Only the display name changes. ID and ID_LIKE stay as the base image set them,
# because the base image's own tools and third-party software check those.
sed -i \
    -e "s|^NAME=.*|NAME=\"${BRAND_NAME}\"|" \
    -e "s|^PRETTY_NAME=.*|PRETTY_NAME=\"${BRAND_NAME}\"|" \
    -e "s|^DEFAULT_HOSTNAME=.*|DEFAULT_HOSTNAME=\"${BRAND_HOSTNAME}\"|" \
    /usr/lib/os-release
echo "${IMAGE_NAME}" > /usr/share/oneclick-variant

### Desktop defaults (system-wide, so they apply to every new user)
# Double-click opens, single-click selects, like Windows Explorer.
# kwriteconfig6 merges into the file, so the base image's own settings survive.
kwriteconfig6 --file /etc/xdg/kdeglobals --group KDE --key SingleClick false

### Icons
# Papirus is the base icon set; the OneClick theme sits on top with our own icons.
dnf5 install -y papirus-icon-theme
PLACES=/usr/share/icons/OneClick/scalable/places
for name in start-here-kde start-here-kde-symbolic start-here-kde-plasma start-here-symbolic; do
    cp "${PLACES}/start-here.svg" "${PLACES}/${name}.svg"
done
gtk-update-icon-cache -f /usr/share/icons/OneClick || true
kwriteconfig6 --file /etc/xdg/kdeglobals --group Icons --key Theme OneClick

### Animations
# Lively window effects on by default. Each is a normal switch in Settings, so anyone can turn it off.
kwriteconfig6 --file /etc/xdg/kwinrc --group Plugins --key wobblywindowsEnabled true
kwriteconfig6 --file /etc/xdg/kwinrc --group Plugins --key magiclampEnabled true
kwriteconfig6 --file /etc/xdg/kwinrc --group Plugins --key squashEnabled false
kwriteconfig6 --file /etc/xdg/kwinrc --group Plugins --key sheetEnabled true
kwriteconfig6 --file /etc/xdg/kwinrc --group Plugins --key dimscreenEnabled true
kwriteconfig6 --file /etc/xdg/kwinrc --group Plugins --key glideEnabled true
kwriteconfig6 --file /etc/xdg/kwinrc --group Plugins --key scaleEnabled false
kwriteconfig6 --file /etc/xdg/kwinrc --group Plugins --key fadeEnabled false

### Start-up screen
# Replace the scrolling text with a graphical splash: our logo with a spinner.
# (system_files adds the "quiet rhgb" kernel options and the unit that hides the text boot menu.)
cp /ctx/boot/watermark.png /usr/share/plymouth/themes/spinner/watermark.png
systemctl enable oneclick-hide-boot-menu.service
# The splash lives in the early-boot image, so rebuild that image to pick up the logo.
KVER="$(ls /usr/lib/modules | sort -V | tail -1)"
DRACUT_NO_XATTR=1 dracut --no-hostonly --kver "${KVER}" --reproducible --add ostree \
    -f "/usr/lib/modules/${KVER}/initramfs.img"
chmod 0600 "/usr/lib/modules/${KVER}/initramfs.img"
