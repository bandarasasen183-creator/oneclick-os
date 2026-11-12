// The OneClick desktop: one taskbar along the bottom, laid out like Windows.
// Start menu at the left, pinned apps, then the tray, clock and show-desktop corner.
var panel = new Panel
panel.location = "bottom"
panel.height = Math.round(gridUnit * 2.6)
panel.floating = false

panel.addWidget("org.kde.plasma.kickoff")

var tasks = panel.addWidget("org.kde.plasma.icontasks")
tasks.currentConfigGroup = ["General"]
tasks.writeConfig("launchers", [
    "preferred://browser",
    "preferred://filemanager",
    "applications:org.kde.discover.desktop",
    "applications:systemsettings.desktop",
    "applications:oneclick-update.desktop"
])

panel.addWidget("org.kde.plasma.marginsseparator")
panel.addWidget("org.kde.plasma.systemtray")
panel.addWidget("org.kde.plasma.digitalclock")
panel.addWidget("org.kde.plasma.showdesktop")

var allDesktops = desktops()
for (var i = 0; i < allDesktops.length; i++) {
    var d = allDesktops[i]
    d.wallpaperPlugin = "org.kde.image"
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"]
    d.writeConfig("Image", "file:///usr/share/wallpapers/OneClick/")
}
