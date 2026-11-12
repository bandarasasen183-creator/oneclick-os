# Brief 01: first bootable image

Working title: **OneClick OS** (the owner has not picked a final name; keep the name in one place so it is a one-line change later).

## What we are making

A Linux distro for people leaving Windows. It should install and run with no terminal, no choices to make, and no setup after first boot. The owner's words: "one click and ready to go", "literally just like Windows, but without the features people hate".

This brief covers only the first milestone: **an image that builds in GitHub Actions, produces an installable ISO, boots to a Windows-style desktop, and already has drivers, codecs and gaming tools in it.** No custom apps yet.

## How others do it (and what we copy)

| Distro | What we copy | What we avoid |
|---|---|---|
| Bazzite | Image-based updates with rollback; Steam, Proton, codecs and Nvidia drivers preinstalled | Its many image variants (users pick the wrong one); console mode on desktop PCs |
| Zorin OS, Linux Mint | Windows-style layout from first boot: bottom taskbar, start menu bottom-left, system tray and clock bottom-right | Mint's old display stack (no HDR or variable refresh) |
| Pop!_OS | Nvidia works with no user action | A separate download per GPU that the user must understand |
| Ubuntu | Nothing | Snaps, and swapping package formats behind the user's back |
| CachyOS, Nobara | Later: tuned kernel and gaming patches (Bazzite already carries most of these) | Rolling updates that can break |

The biggest complaint about desktop Linux is fragmentation: too many distros, desktops and package formats. So the rule for every decision in this project is **one of everything and never ask the user to choose**: one desktop (KDE Plasma), one app store (Flathub through the built-in store), one update mechanism (image updates).

## Technical approach

Do not build a distro from scratch. Use the Universal Blue custom-image pattern:

- Start from the official template: https://github.com/ublue-os/image-template (Containerfile, `build_files/build.sh`, `system_files/`, `disk_config/`, Justfile, and the `build.yml` and `build-disk.yml` workflows). Read its README first and follow its current instructions; they change, and they win over anything in this brief that disagrees.
- Base image: `ghcr.io/ublue-os/bazzite` (KDE Plasma, AMD and Intel graphics) and `ghcr.io/ublue-os/bazzite-nvidia-open` or the current Nvidia equivalent. Check the ublue-os packages page for the right current names and tags. Use the `stable` tag.
- Images are x86_64 only. The owner's Mac is Apple Silicon, so **do not try to build the image locally**; all builds run in GitHub Actions. Claude will boot-test the ISO in QEMU.

The project folder is `/Users/sasenb/oneclick-os` (git already initialised, no remote yet). Claude creates the GitHub repo, the cosign signing key and the repo secrets once the owner approves; write the code so it works when those exist. Do not create the repo, push, or generate keys yourself.

## Tasks

Split between two coders with strict file ownership. Stage per file (`git add <file>`, never `-A`).

### Coder 1: image build (owns `Containerfile`, `build_files/`, `.github/`, `Justfile`, `disk_config/`, `image-template.env`)

1. Bring in the template files and rename everything from the template's placeholder to the image name `oneclick-os`. Keep the name in one variable or file where the template allows.
2. Build **two images from one Containerfile** using a build argument for the base: `oneclick-os` (AMD and Intel) and `oneclick-os-nvidia`. Update `build.yml` to build both as a matrix.
3. Make `build-disk.yml` produce an **installable ISO** for each image (the template uses bootc-image-builder; use whichever installer type its README currently recommends) and upload it as a workflow artifact. S3 upload stays off.
4. The ISO installer must need as few decisions as possible: language, keyboard, disk, user name and password. Nothing else. Configure this through `disk_config/`.
5. Keep `bootc container lint` passing.
6. Remove Bazzite's first-run "portal" or welcome screens that ask the user to pick optional extras, if they can be turned off cleanly from the image. If that is not clean, leave them and report it.

### Coder 2: desktop defaults (owns `system_files/` and `build_files/desktop/`)

1. **Windows-style Plasma layout as the default for every new user:** one bottom panel with the application launcher at the left, pinned apps, task manager, system tray and clock at the right; "show desktop" at the far right corner. Ship it as system defaults (for example a Plasma look-and-feel package or files under `/etc/xdg` and `/etc/skel`), not as a script the user runs.
2. **Windows keyboard shortcuts** that Plasma does not already have by default: Super+E opens the file manager, Super+L locks, Super+D shows the desktop, Ctrl+Shift+Esc opens the system monitor, Super+V opens clipboard history, Super+Shift+S takes a region screenshot. Check which are already defaults and only add the missing ones.
3. **File manager behaves like Explorer:** double-click to open, single-click to select.
4. **Branding in one place:** `/usr/lib/os-release` fields (NAME, PRETTY_NAME, ID=oneclick-os, keeping `ID_LIKE` so software still recognises it as Fedora), and a plain default wallpaper. No logo work yet. No emoji anywhere in the UI; icons only.
5. **Double-clicking a `.exe` or `.msi` does something sensible.** Research first how Bazzite, Zorin OS ("Windows App Support") and Bottles handle this. Pick the simplest approach that works from the image with no user setup, set the file association, and report what you chose and what its limits are. If no approach is solid, ship a clear dialog that explains instead of a silent failure.

### Both

- Write `docs/WHAT-IS-IN-THE-IMAGE.md`: a plain-language list of everything we change on top of Bazzite, kept up to date. This is how Claude reviews the work.
- Do not add anything not listed here. No telemetry, no accounts, no AI features.
- Do not claim hardware or game support we have not tested.

## Out of scope for this brief

The Windows migration tool, the "will my games and apps work" first-run check, a custom app store front end, a website, a custom kernel, and the final name and logo. These come in later briefs.

## Done means

1. `build.yml` and `build-disk.yml` are ready to run for both images as soon as the repo and signing secret exist (Claude will run them and send back any failures through the mailbox).
2. `docs/WHAT-IS-IN-THE-IMAGE.md` exists and matches the code.
3. A report at `docs/antigravity/reports/BRIEF-01-report.md` listing: what was done, what was not and why, every choice you made where this brief left it open, and anything that needs the owner.
4. The mailbox was checked (`docs/antigravity/mailbox/check.sh`) right before saying done.

## Mailbox

All communication with Claude goes through `docs/antigravity/mailbox/` following `docs/antigravity/MAILBOX.md`. Start `mailbox/watch.sh` as a background task before starting work.
