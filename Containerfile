# OneClick OS: one image recipe, three variants (see .github/workflows/build.yml).
#   oneclick-os          Bazzite (KDE), AMD and Intel graphics, for real PCs
#   oneclick-os-nvidia   Bazzite (KDE) with Nvidia drivers, for real PCs
#   oneclick-os-preview  Fedora Kinoite on arm64, for the virtual machine on an Apple Silicon Mac
ARG BASE_IMAGE=ghcr.io/ublue-os/bazzite:stable

# Build scripts and system files, mounted during the build without ending up in the image twice
FROM scratch AS ctx
COPY build_files /
COPY system_files /system_files

FROM ${BASE_IMAGE}
ARG IMAGE_NAME=oneclick-os

RUN --mount=type=bind,from=ctx,source=/,target=/ctx \
    --mount=type=cache,dst=/var/cache \
    --mount=type=cache,dst=/var/log \
    --mount=type=tmpfs,dst=/tmp \
    IMAGE_NAME="${IMAGE_NAME}" /ctx/build.sh

# Fails the build if the result is not a valid bootable image
RUN bootc container lint
