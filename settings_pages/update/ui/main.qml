// The Update page. One card that changes with the state, then the channel choice,
// then previous versions and "go back".
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.kcmutils as KCM

KCM.SimpleKCM {
    id: page

    Component.onCompleted: {
        kcm.check()
        kcm.loadVersions()
    }

    ColumnLayout {
        spacing: Kirigami.Units.largeSpacing * 2

        // ---- status card --------------------------------------------------
        Kirigami.AbstractCard {
            Layout.fillWidth: true
            contentItem: ColumnLayout {
                spacing: Kirigami.Units.largeSpacing

                RowLayout {
                    spacing: Kirigami.Units.largeSpacing
                    Kirigami.Icon {
                        source: kcm.state === "error" ? "dialog-error"
                              : kcm.state === "uptodate" ? "checkmark" : "oneclick-update"
                        Layout.preferredWidth: Kirigami.Units.iconSizes.huge
                        Layout.preferredHeight: Kirigami.Units.iconSizes.huge
                        RotationAnimator on rotation {
                            running: kcm.state === "checking"
                            from: 0; to: 360; duration: 1400; loops: Animation.Infinite
                            onRunningChanged: if (!running) target.rotation = 0
                        }
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Kirigami.Heading {
                            level: 2
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            text: ({
                                idle: "Check for updates",
                                checking: "Checking for updates...",
                                available: kcm.channel === "security" ? "Security fixes are available" : "A new version is available",
                                uptodate: "You're up to date",
                                downloading: "Downloading...",
                                ready: "Ready. Restart to finish",
                                error: "Something went wrong"
                            })[kcm.state]
                        }
                        QQC2.Label {
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            opacity: 0.7
                            text: kcm.state === "error" ? ("Check your internet connection and try again.\n" + kcm.message)
                                : kcm.state === "downloading" ? "You can keep using your PC. Nothing changes until you restart."
                                : kcm.state === "ready" ? "Your open apps will close when you restart."
                                : "You have OneClick OS " + (kcm.currentVersion || "(development build)")
                        }
                    }
                }

                // Download progress: bar, megabytes, time left
                ColumnLayout {
                    visible: kcm.state === "downloading"
                    Layout.fillWidth: true
                    spacing: Kirigami.Units.smallSpacing
                    QQC2.ProgressBar {
                        Layout.fillWidth: true
                        indeterminate: kcm.totalMb <= 0
                        from: 0
                        to: Math.max(1, kcm.totalMb)
                        value: kcm.doneMb
                        Behavior on value { NumberAnimation { duration: 900 } }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        QQC2.Label {
                            text: kcm.totalMb > 0
                                ? Math.round(kcm.doneMb) + " MB of " + Math.round(kcm.totalMb) + " MB"
                                : "Working out the size..."
                        }
                        Item { Layout.fillWidth: true }
                        QQC2.Label { text: kcm.eta; opacity: 0.7 }
                    }
                }

                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    spacing: Kirigami.Units.smallSpacing
                    QQC2.Button {
                        visible: ["idle", "uptodate", "error"].includes(kcm.state)
                        text: "Check now"
                        icon.name: "view-refresh"
                        onClicked: kcm.check()
                    }
                    QQC2.Button {
                        visible: kcm.state === "available"
                        text: "Download"
                        icon.name: "download"
                        onClicked: kcm.download(false)
                    }
                    QQC2.Button {
                        visible: kcm.state === "available"
                        text: "Download and restart"
                        icon.name: "system-reboot"
                        highlighted: true
                        onClicked: kcm.download(true)
                    }
                    QQC2.Button {
                        visible: kcm.state === "ready"
                        text: "Restart now"
                        icon.name: "system-reboot"
                        highlighted: true
                        onClicked: kcm.restart()
                    }
                }
            }
        }

        // ---- what to receive ---------------------------------------------
        Kirigami.FormLayout {
            Layout.fillWidth: true
            enabled: kcm.state !== "downloading" && kcm.state !== "checking"
            QQC2.ButtonGroup { id: channels }
            QQC2.RadioButton {
                Kirigami.FormData.label: "Updates to receive:"
                text: "Full: new features and security fixes"
                checked: kcm.channel === "full"
                QQC2.ButtonGroup.group: channels
                onToggled: if (checked) { kcm.setChannel("full"); kcm.check() }
            }
            QQC2.RadioButton {
                text: "Security only: keep this version, receive security fixes"
                checked: kcm.channel === "security"
                QQC2.ButtonGroup.group: channels
                onToggled: if (checked) { kcm.setChannel("security"); kcm.check() }
            }
            QQC2.Label {
                text: "Updates are never installed without you choosing to."
                opacity: 0.7
            }
        }

        // ---- previous versions -------------------------------------------
        Kirigami.Heading { level: 3; text: "Previous versions" }
        QQC2.Label {
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            opacity: 0.7
            text: "Each version below keeps its own features and includes the latest security fixes. Your files and apps are not affected."
        }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing
            enabled: kcm.state !== "downloading" && kcm.state !== "checking"

            Repeater {
                model: kcm.versions
                delegate: Kirigami.AbstractCard {
                    id: card
                    required property string modelData
                    property bool open: false
                    Layout.fillWidth: true
                    contentItem: ColumnLayout {
                        RowLayout {
                            Kirigami.Icon { source: "oneclick-update"; Layout.preferredWidth: Kirigami.Units.iconSizes.medium; Layout.preferredHeight: Kirigami.Units.iconSizes.medium }
                            QQC2.Label {
                                Layout.fillWidth: true
                                font.bold: true
                                text: "OneClick OS " + card.modelData + (card.modelData === kcm.currentVersion ? "  (this PC)" : "")
                            }
                            QQC2.ToolButton {
                                icon.name: card.open ? "arrow-up" : "arrow-down"
                                onClicked: card.open = !card.open
                            }
                        }
                        RowLayout {
                            visible: card.open
                            Layout.alignment: Qt.AlignRight
                            QQC2.Button { text: "Download"; onClicked: kcm.installVersion(card.modelData, false) }
                            QQC2.Button { text: "Download and restart"; onClicked: kcm.installVersion(card.modelData, true) }
                        }
                    }
                }
            }
            QQC2.Label {
                visible: kcm.versions.length === 0
                opacity: 0.7
                text: "No earlier versions have been published yet."
            }
        }

        QQC2.Button {
            text: "Undo the last update"
            icon.name: "edit-undo"
            enabled: kcm.state !== "downloading" && kcm.state !== "checking"
            onClicked: kcm.rollback()
            QQC2.ToolTip.text: "Go back to exactly what this PC ran before the last update"
            QQC2.ToolTip.visible: hovered
        }
    }
}
