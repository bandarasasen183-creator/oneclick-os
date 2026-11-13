// OneClick start menu. Laid out like the Windows 11 one: search at the top, pinned apps
// in a grid, an "All apps" list one click away, and the account and power buttons at the bottom.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PC3
import org.kde.plasma.plasma5support as P5Support
import org.kde.plasma.private.kicker as Kicker
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    property bool showAll: false
    readonly property string query: search.text.trim()
    readonly property color accent: "#2dd4bf"

    preferredRepresentation: compactRepresentation
    switchWidth: 0
    switchHeight: 0

    onExpandedChanged: {
        if (expanded) {
            search.text = ""
            showAll = false
            search.forceActiveFocus()
        }
    }

    // ---- data -------------------------------------------------------------
    Kicker.RootModel {
        id: appsRoot
        autoPopulate: true
        appNameFormat: 0
        flat: true
        sorted: true
        showSeparators: false
        showAllApps: true
        showAllAppsCategorized: false
        showRecentApps: false
        showRecentDocs: false
        showPowerSession: false
        showFavoritesPlaceholder: false
        Component.onCompleted: {
            favoritesModel.initForClient("org.oneclick.startmenu.pinned.instance-" + Plasmoid.id)
            if (favoritesModel.favorites.length === 0) {
                favoritesModel.favorites = Plasmoid.configuration.pinned
            }
        }
    }

    Kicker.RunnerModel {
        id: runner
        appletInterface: root
        mergeResults: true
        favoritesModel: appsRoot.favoritesModel
        runners: ["krunner_services", "krunner_systemsettings", "calculator", "krunner_sessions", "krunner_powerdevil"]
        query: root.query
    }

    P5Support.DataSource {
        id: shell
        engine: "executable"
        connectedSources: []
        onNewData: (source) => disconnectSource(source)
        function run(cmd) { connectSource(cmd) }
    }

    function launch(model, row) {
        model.trigger(row, "", null)
        root.expanded = false
    }

    // ---- taskbar button ---------------------------------------------------
    compactRepresentation: MouseArea {
        id: button
        hoverEnabled: true
        onClicked: root.expanded = !root.expanded
        Layout.minimumWidth: height * 1.25
        Rectangle {
            anchors.fill: parent
            anchors.margins: 3
            radius: 6
            color: "#ffffff"
            opacity: root.expanded ? 0.14 : (button.containsMouse ? 0.08 : 0)
            Behavior on opacity { NumberAnimation { duration: 120 } }
        }
        Kirigami.Icon {
            anchors.centerIn: parent
            width: Math.min(parent.width, parent.height) * 0.62
            height: width
            source: "start-here"
            scale: button.pressed ? 0.88 : 1
            Behavior on scale { NumberAnimation { duration: 90 } }
        }
    }

    // ---- the menu ---------------------------------------------------------
    fullRepresentation: Item {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 34
        Layout.preferredHeight: Kirigami.Units.gridUnit * 38
        Layout.minimumWidth: Layout.preferredWidth
        Layout.minimumHeight: Layout.preferredHeight

        Keys.onEscapePressed: root.expanded = false

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Kirigami.Units.gridUnit
            spacing: Kirigami.Units.gridUnit

            // Search
            QQC2.TextField {
                id: search
                Layout.fillWidth: true
                placeholderText: "Search apps, settings and files"
                leftPadding: Kirigami.Units.gridUnit * 2
                font.pixelSize: Kirigami.Units.gridUnit * 0.85
                background: Rectangle {
                    radius: height / 2
                    color: Qt.rgba(1, 1, 1, 0.06)
                    border.width: search.activeFocus ? 2 : 1
                    border.color: search.activeFocus ? root.accent : Qt.rgba(1, 1, 1, 0.12)
                }
                Kirigami.Icon {
                    source: "search"
                    width: Kirigami.Units.iconSizes.small
                    height: width
                    anchors.left: parent.left
                    anchors.leftMargin: Kirigami.Units.gridUnit * 0.7
                    anchors.verticalCenter: parent.verticalCenter
                }
                Keys.onReturnPressed: {
                    if (root.query.length > 0 && runner.count > 0 && runner.modelForRow(0).count > 0) {
                        root.launch(runner.modelForRow(0), 0)
                    }
                }
                Keys.onDownPressed: results.forceActiveFocus()
            }

            // Section heading and the button to switch between pinned and all apps
            RowLayout {
                Layout.fillWidth: true
                visible: root.query.length === 0
                PC3.Label {
                    text: root.showAll ? "All apps" : "Pinned"
                    font.bold: true
                    font.pixelSize: Kirigami.Units.gridUnit * 0.8
                    Layout.fillWidth: true
                }
                PC3.Button {
                    text: root.showAll ? "Back" : "All apps"
                    icon.name: root.showAll ? "go-previous" : "go-next"
                    onClicked: root.showAll = !root.showAll
                }
            }

            // Pinned grid
            GridView {
                id: pinned
                visible: root.query.length === 0 && !root.showAll
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                cellWidth: width / 6
                cellHeight: Kirigami.Units.gridUnit * 5.4
                model: appsRoot.favoritesModel
                delegate: Tile {
                    width: pinned.cellWidth
                    height: pinned.cellHeight
                    onActivated: root.launch(appsRoot.favoritesModel, index)
                }
                populate: Transition {
                    NumberAnimation { properties: "opacity"; from: 0; to: 1; duration: 180 }
                    NumberAnimation { properties: "y"; from: 30; duration: 220; easing.type: Easing.OutCubic }
                }
            }

            // All apps, A to Z
            ListView {
                id: allApps
                visible: root.query.length === 0 && root.showAll
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                model: appsRoot.count > 0 ? appsRoot.modelForRow(0) : null
                delegate: Row_ {
                    width: allApps.width
                    onActivated: root.launch(allApps.model, index)
                }
                QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
            }

            // Search results
            ListView {
                id: results
                visible: root.query.length > 0
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                model: runner.count > 0 ? runner.modelForRow(0) : null
                delegate: Row_ {
                    width: results.width
                    highlighted: index === 0 || ListView.isCurrentItem
                    onActivated: root.launch(results.model, index)
                }
                Keys.onReturnPressed: root.launch(model, currentIndex)
                PC3.Label {
                    anchors.centerIn: parent
                    visible: root.query.length > 0 && (results.count === 0)
                    text: "Nothing found for “" + root.query + "”"
                    opacity: 0.6
                }
            }

            // Account and power
            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: -Kirigami.Units.gridUnit
                Layout.rightMargin: -Kirigami.Units.gridUnit
                Layout.bottomMargin: -Kirigami.Units.gridUnit
                implicitHeight: Kirigami.Units.gridUnit * 3.2
                color: Qt.rgba(0, 0, 0, 0.18)
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Kirigami.Units.gridUnit * 1.5
                    anchors.rightMargin: Kirigami.Units.gridUnit
                    Kirigami.Icon {
                        source: "user-identity"
                        Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                        Layout.preferredHeight: Layout.preferredWidth
                    }
                    PC3.Label {
                        text: Qt.application.arguments.length >= 0 ? (shellUser.name) : ""
                        Layout.fillWidth: true
                    }
                    PowerButton { icon: "system-lock-screen"; tip: "Lock"; command: "loginctl lock-session" }
                    PowerButton { icon: "system-log-out"; tip: "Sign out"; command: "qdbus-qt6 org.kde.LogoutPrompt /LogoutPrompt promptLogout" }
                    PowerButton { icon: "system-reboot"; tip: "Restart"; command: "qdbus-qt6 org.kde.LogoutPrompt /LogoutPrompt promptReboot" }
                    PowerButton { icon: "system-shutdown"; tip: "Shut down"; command: "qdbus-qt6 org.kde.LogoutPrompt /LogoutPrompt promptShutDown" }
                }
            }
        }
    }

    QtObject {
        id: shellUser
        property string name: ""
    }
    P5Support.DataSource {
        engine: "executable"
        connectedSources: ["getent passwd $USER | cut -d: -f5 | cut -d, -f1; echo; whoami"]
        onNewData: (source, data) => {
            const lines = data["stdout"].split("\n").map(s => s.trim()).filter(s => s.length)
            shellUser.name = lines.length ? lines[0] : ""
            disconnectSource(source)
        }
    }

    // ---- small parts ------------------------------------------------------
    component Tile: MouseArea {
        id: tile
        signal activated()
        hoverEnabled: true
        onClicked: activated()
        Rectangle {
            anchors.fill: parent
            anchors.margins: 4
            radius: 8
            color: "#ffffff"
            opacity: tile.pressed ? 0.12 : (tile.containsMouse ? 0.07 : 0)
            Behavior on opacity { NumberAnimation { duration: 100 } }
        }
        ColumnLayout {
            anchors.centerIn: parent
            width: parent.width - 8
            spacing: 6
            Kirigami.Icon {
                source: model.decoration
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: Kirigami.Units.iconSizes.large
                Layout.preferredHeight: Layout.preferredWidth
                scale: tile.pressed ? 0.9 : 1
                Behavior on scale { NumberAnimation { duration: 90 } }
            }
            PC3.Label {
                text: model.display
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                font.pixelSize: Kirigami.Units.gridUnit * 0.62
            }
        }
    }

    component Row_: MouseArea {
        id: row
        signal activated()
        property bool highlighted: false
        height: Kirigami.Units.gridUnit * 2.4
        hoverEnabled: true
        onClicked: activated()
        Rectangle {
            anchors.fill: parent
            radius: 6
            color: "#ffffff"
            opacity: row.pressed ? 0.12 : ((row.containsMouse || row.highlighted) ? 0.07 : 0)
        }
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Kirigami.Units.gridUnit * 0.6
            spacing: Kirigami.Units.gridUnit * 0.6
            Kirigami.Icon {
                source: model.decoration
                Layout.preferredWidth: Kirigami.Units.iconSizes.smallMedium
                Layout.preferredHeight: Layout.preferredWidth
            }
            PC3.Label {
                text: model.display
                Layout.fillWidth: true
                elide: Text.ElideRight
            }
        }
    }

    component PowerButton: PC3.ToolButton {
        property string icon: ""
        property string tip: ""
        property string command: ""
        icon.name: icon
        display: QQC2.AbstractButton.IconOnly
        PC3.ToolTip.text: tip
        PC3.ToolTip.visible: hovered
        onClicked: { root.expanded = false; shell.run(command) }
    }
}
