#!/bin/bash
# Runs the OneClick OS preview in a window on an Apple Silicon Mac.
# This is the real operating system in a virtual machine, not a mock-up.
#
#   mac/run-preview.sh            start the preview
#   mac/run-preview.sh --reset    throw away changes and start from the clean disk
#
# The virtual disk lives in ~/OneClickVM, outside iCloud, because it is several GB.
set -euo pipefail

VM_DIR="${HOME}/OneClickVM"
BASE="${VM_DIR}/disk.qcow2"        # clean disk from the build, never written to
WORK="${VM_DIR}/work.qcow2"        # your session's changes
VARS="${VM_DIR}/efi-vars.fd"
CODE="/opt/homebrew/share/qemu/edk2-aarch64-code.fd"

if [[ ! -f "${BASE}" ]]; then
    echo "No preview disk yet. Expected it at ${BASE}" >&2
    exit 1
fi

if [[ "${1:-}" == "--reset" ]]; then
    rm -f "${WORK}" "${VARS}"
fi

if [[ ! -f "${WORK}" ]]; then
    qemu-img create -q -f qcow2 -b "${BASE}" -F qcow2 "${WORK}"
fi
if [[ ! -f "${VARS}" ]]; then
    dd if=/dev/zero of="${VARS}" bs=1m count=64 status=none
fi

exec qemu-system-aarch64 \
    -name "OneClick OS preview" \
    -machine virt -accel hvf -cpu host \
    -smp 4 -m 3584 \
    -drive if=pflash,format=raw,readonly=on,file="${CODE}" \
    -drive if=pflash,format=raw,file="${VARS}" \
    -drive if=virtio,format=qcow2,file="${WORK}" \
    -device virtio-gpu-pci -display cocoa,show-cursor=on \
    -device qemu-xhci -device usb-kbd -device usb-tablet \
    -nic user,model=virtio-net-pci \
    -monitor unix:"${VM_DIR}/monitor.sock",server,nowait \
    -qmp unix:"${VM_DIR}/qmp.sock",server,nowait \
    -serial file:"${VM_DIR}/boot.log" \
    -audiodev coreaudio,id=snd -device ich9-intel-hda -device hda-output,audiodev=snd
