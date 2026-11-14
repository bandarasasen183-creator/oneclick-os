# Brief 02: the system features that are still missing

Project: **OneClick OS**, a Linux desktop for people leaving Windows. Folder: this repo (`~/Library/Mobile Documents/com~apple~CloudDocs/OneClickOS`). GitHub: `Codecraft-Solutions-Team/oneclick-os`.

The owner wants this worked through overnight without supervision. Work the tasks in order, commit often, keep the build green, and write the report at the end. Do not stop to ask questions: where this brief leaves a choice open, choose the simplest thing that meets the rule, and list the choice in the report.

## Read first

- `Containerfile`, `build_files/build.sh`, `system_files/`: how the image is made. Everything we change on top of the base lives here.
- `settings_pages/update/`: an existing compiled Settings page (C++ KCM with a QML UI). Copy its pattern for new pages.
- `system_files/usr/share/plasma/plasmoids/org.oneclick.startmenu/`: the start menu, written but never run.
- `design/*.py`: generators for icons, wordmark and boot animation. They need macOS (`qlmanage`, `sips`).
- `website/`: the public site. **Do not change it in this brief.**

## How the system is built and tested

- One recipe, three images: `oneclick-os` and `oneclick-os-nvidia` (Bazzite base, x86_64, real PCs) and `oneclick-os-preview` (Fedora Kinoite, arm64, runs in a QEMU virtual machine on this Mac).
- **Nothing builds on this Mac.** Pushing to `main` starts `.github/workflows/build.yml`. Check it with `gh run list --workflow build.yml` and `gh run view <id> --log-failed`. A build takes 10 to 20 minutes. Changes under `website/`, `design/`, `mac/` and `*.md` do not start a build.
- **The preview VM** is the only place to see things. Start it with `mac/run-preview.sh`. Tools in `tools/preview/`:
  - `vmssh '<command>'` runs a command as the `tester` user with the desktop session's environment (needs the VM up and sshd on; key at `~/OneClickVM/id`).
  - `vmcp <local> <remote>` copies files in.
  - `vm.py shot <file.png>`, `vm.py click <x 0-1> <y 0-1>`, `vm.py type <text>`, `vm.py key <name>` drive the screen over QMP.
  - `ser.py` talks to the serial console.
  - The tester password is in `disk_config/disk.toml`.
- **Fast loop for desktop files:** copy QML, icons, themes and plasmoids into `~/.local/share/...` inside the VM with `vmcp` and reload (`systemctl --user restart plasma-plasmashell`, or `qdbus-qt6 org.kde.KWin /KWin reconfigure`). Only compiled pages and image-level changes need a full build.
- **Getting a build into the VM:** `vmssh 'echo <password> | sudo -S bootc switch ghcr.io/codecraft-solutions-team/oneclick-os-preview:latest'`, then reboot. **This is blocked until the owner makes the GitHub packages public** (they are private since the repo moved). If the pull fails with 403, do not try to work around it: test with the fast loop, and say in the report which items were only checked that way.
- GUI commands over ssh need `WAYLAND_DISPLAY=wayland-1 QT_QPA_PLATFORM=wayland` (the helper sets them). Without them the tool aborts and leaves a crash report on the desktop.
- The VM has 3.5 GB of memory and no graphics acceleration. Slow is normal. The preview image never suspends; do not re-enable sleep.

## Rules that are not negotiable

1. **Fully custom, not a rename.** The owner rejected an earlier build as "Fedora with our name on it". Nothing a user sees should say KDE, Plasma, Fedora or Bazzite, or use their logos, where we can reasonably change it.
2. **Flat design. No glow, no gradients, no neon.** The owner calls those "AI looking". Colours: navy `#0a1020`, panel `#0b1224`, line `#22304d`, teal accent `#2dd4bf`, white. Look at `design/make_system_icons.py` and the wallpaper for the style.
3. **No emoji anywhere.** Icons are SVG.
4. **Windows-familiar.** Taskbar at the bottom, start menu bottom-left, min/max/close top-right, Windows wording ("Settings", "Files", "Task Manager").
5. **One of everything.** Never add a second tool for a job that already has one, and never ask the user to choose between alternatives.
6. **No telemetry, no accounts, no AI features in the OS.**
7. **Nothing is installed or updated without the user choosing it.**
8. **Privileged work goes through a helper in `/usr/libexec/` called with `pkexec`**, with a polkit action file, as `oneclick-update-helper` does.
9. **Do not claim something works unless you saw it work.** The report must separate "seen on screen" from "written, not seen".
10. **Keep `bootc container lint` passing and all three images building.** If a change breaks the Bazzite images but not the preview (or the reverse), fix it or guard it with `IMAGE_NAME`; do not leave a red build.
11. Do not touch: `website/`, `firebase.json`, `functions/`, the GitHub repo settings, the domain, or anything outside this repo. Do not publish, deploy, tag a release, or change package visibility.
12. Stage per file (`git add <file>`, never `-A`). Commit messages in plain English.

## Tasks, in order

For each task: research how the best systems do it (Windows 11, macOS, Zorin OS, Linux Mint), write two or three lines on what you copied into the report, then build it.

### 1. Start menu on the taskbar

`org.oneclick.startmenu` exists but has never been loaded. Get it working and make it the default launcher.

- Load it in the VM first (`plasmawindowed org.oneclick.startmenu`, then on the panel). Fix whatever fails; the Kicker model property names were written from memory and may be wrong.
- Layout like Windows 11: search field at the top, "Pinned" grid, "All apps" list A to Z one click away, and at the bottom the user's name with Lock, Sign out, Restart, Shut down.
- **Search must find Settings pages** and open Settings at that page (the `krunner_systemsettings` runner does this), as well as apps and files.
- Pinned by default: browser, Files, App Store, Settings, Text Editor, Terminal, Screenshot, Update, Task Manager, Claude, ChatGPT, GeForce NOW, Xbox Cloud Gaming.
- Right-click an app: Pin / Unpin, Add to taskbar.
- Opening animation: rises and fades in, about 180 ms. Tiles appear with a slight stagger.
- Replace `org.kde.plasma.kickoff` with it in `.../look-and-feel/org.oneclick.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`. The Meta key must open it.

### 2. Our apps as Settings pages

The owner wants our tools inside Settings, not as separate windows, and their shortcuts should open Settings at that page.

- **Taskbar** page (`kcm_oneclick_taskbar`): the options now in `system_files/usr/bin/oneclick-taskbar` (hide while an app covers it, always hidden until the pointer reaches the edge, floating, top or bottom, small/medium/large), with a small live preview drawing of the taskbar. Applies at once through the `org.kde.plasmashell` `evaluateScript` D-Bus call. Category `workspace`.
- **Windows apps** page: whether double-clicking a `.exe` is handled, and a button to install Bottles from the App Store.
- **About this PC** page text and logo: our name, version from `/usr/share/oneclick/version`, our logo. Remove or override the stock "About this System" page branding.
- Change `oneclick-taskbar.desktop` to `Exec=systemsettings kcm_oneclick_taskbar`, and delete the kdialog script.
- Verify the existing **Update** page (`kcm_oneclick_update`) on screen: check, download with megabytes and time left, Full and Security only, previous versions, undo. Fix what does not work. It has compiled but has never been opened.

### 3. Login screen

The login manager is `plasma-login-manager` (not SDDM). The wallpaper setting in `system_files/etc/plasmalogin.conf.d/10-oneclick.conf` had no effect.

- Find how its wallpaper and look are really configured (read its source and the files under `/var/lib/plasmalogin/.config`), then give it: our wallpaper unblurred, the clock, the user's name and password field, and our wordmark small at the bottom (`/usr/share/oneclick/wordmark.svg`).
- If its QML can be replaced cleanly, restyle it flat in our colours. If not, set what can be set and say so.
- Same wallpaper on the lock screen.

### 4. First-run setup and welcome

- The setup wizard is `plasma-setup`. Rebrand its pages (it has a distro customisation mechanism): our wordmark, our wording, as few steps as possible. **Keep the final "Completed!" page as it is; the owner likes it.**
- Replace the `plasma-welcome` tour pages with ours: Welcome; Where things are (taskbar, start menu, Settings); Your apps; Updates are your choice; Coming from Windows (what does not work: anti-cheat games, Adobe, desktop Office, and what to use instead). The intro text is already overridden in `build.sh`; finish the rest.
- **App choices:** on first login, if `/etc/oneclick/apps.list` or `~/.config/oneclick/apps.list` exists (one Flathub ID per line), install those apps with a progress window, then remove the file. Also add an "Apps" page to the welcome tour offering the same starter sets as the website (Everyday, Gamer, Work, Creator) with tick boxes.

### 5. Office, cloud drives, everyday gaps

- Preinstall LibreOffice (Flatpak from Flathub, installed on first boot so the image stays small, or as RPMs if that is cleaner on both bases). Set it as the default for `.docx`, `.xlsx`, `.pptx`, `.odt`.
- OneDrive as a folder in Files: research the options (`onedriver`, `rclone mount`, the `abraunegg/onedrive` client) and choose one that needs no terminal. Add a "Cloud drives" Settings page or reuse Online Accounts. Google Drive already works through Online Accounts; verify it and say so.
- Start-menu shortcuts for Office on the web (Word, Excel, PowerPoint) with our own icons.

### 6. Crash window and shutdown

- When an app crashes, show one plain window: "<App> closed unexpectedly" with **Reopen** and **Close**. Hide the developer and gdb route behind a small "Details for developers" link. Mask or replace DrKonqi's dialog.
- Shutdown and restart must show our graphical screen, not scrolling text (`plymouth.ignore-serial-consoles` is already in `kargs.d`; check `plymouth-poweroff`/`plymouth-reboot` and the theme's shutdown behaviour). The start-up theme is a Plymouth script theme in `build_files/boot/plymouth/`; on shutdown show the finished wordmark, not the writing animation.

### 7. Animations

The owner asked for "a lot more animations", tasteful ones.

- Windows: open and close scale-and-fade, minimise to the taskbar icon, maximise snap. Tune KWin effect durations; keep wobbly windows subtle or off if it looks cheap.
- Taskbar: icons bounce slightly on launch; the open-app indicator slides in.
- Our pages and the start menu: hover and press states, list items easing in.
- Notifications slide in from the right.
- Respect the system "animation speed" setting and reduced motion.

### 8. macOS mode (a full switch, not a theme tweak)

A second complete look the user can switch on and off from Settings. Everything changes together:

- A top menu bar with the app's menu (global menu), clock and tray on the right, our logo at the left.
- A dock at the bottom: centred, floating, icons magnify on hover.
- Window buttons on the **left** as three coloured circles (close, minimise, maximise), in a second Aurorae theme. Generate it the way `design/make_window_frame.py` does.
- Translucent "glass" panels and menus with background blur.
- macOS-style window open, close and minimise ("genie") animations.
- A Settings page **Look** with two large previews: "Windows style" and "Mac style". One click applies everything; one click goes back.
- Build it as a second look-and-feel package (`org.oneclick.mac`) plus a helper that swaps layout, decoration, effects and panel settings. Draw our own artwork. Do not copy Apple's icons, wallpapers or logos.

### 9. Leave for later (do not start)

Our own Settings app, a restyled App Store, the Windows migration tool, the "will my games work" check. Note any thoughts on them in the report.

## Done means

1. `main` builds green for all three images after your last commit.
2. `docs/WHAT-IS-IN-THE-IMAGE.md` exists: a plain-language list of everything we change on top of the base, kept in step with the code.
3. `docs/antigravity/reports/BRIEF-02-report.md` exists, with, per task: **seen on screen** / **written, not seen** / **not done and why**; every choice you made where this brief left one open; how others do it (two or three lines); and screenshots saved under `docs/antigravity/reports/shots/`.
4. A short list at the top of the report titled **Needs the owner**.
5. The mailbox was checked (`docs/antigravity/mailbox/check.sh`) right before saying done.

## Mailbox

All communication with Claude goes through `docs/antigravity/mailbox/`, following `docs/antigravity/MAILBOX.md`. Start `mailbox/watch.sh` as a background task before starting work, and keep the heartbeat log going.
