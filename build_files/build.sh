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
