# OneClick OS: one image recipe, three variants (see .github/workflows/build.yml).
#   oneclick-os          Bazzite (KDE), AMD and Intel graphics, for real PCs
#   oneclick-os-nvidia   Bazzite (KDE) with Nvidia drivers, for real PCs
#   oneclick-os-preview  Fedora Kinoite on arm64, for the virtual machine on an Apple Silicon Mac
ARG BASE_IMAGE=ghcr.io/ublue-os/bazzite:stable

# Compiles our Settings pages against the exact libraries of the base image.
# The compilers stay in this stage and never reach the final image.
FROM ${BASE_IMAGE} AS pages
COPY settings_pages /src
RUN dnf5 install -y cmake gcc-c++ extra-cmake-modules kf6-kcmutils-devel kf6-kcoreaddons-devel \
        qt6-qtbase-devel qt6-qtdeclarative-devel \
    && cmake -S /src -B /build -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /build --parallel \
    && DESTDIR=/out cmake --install /build

# Build scripts and system files, mounted during the build without ending up in the image twice
FROM scratch AS ctx
COPY build_files /
COPY system_files /system_files
COPY VERSION /VERSION
COPY --from=pages /out /pages

FROM ${BASE_IMAGE}
ARG IMAGE_NAME=oneclick-os
ARG IMAGE_REGISTRY=ghcr.io/bandarasasen183-creator

RUN --mount=type=bind,from=ctx,source=/,target=/ctx \
    --mount=type=cache,dst=/var/cache \
    --mount=type=cache,dst=/var/log \
    --mount=type=tmpfs,dst=/tmp \
    IMAGE_NAME="${IMAGE_NAME}" IMAGE_REGISTRY="${IMAGE_REGISTRY}" /ctx/build.sh

# Fails the build if the result is not a valid bootable image
RUN bootc container lint
