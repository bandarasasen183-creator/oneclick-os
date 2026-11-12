// Shown between logging in and the desktop appearing.
import QtQuick

Rectangle {
    id: root
    color: "#040816"
    property int stage

    onStageChanged: {
        if (stage >= 1) {
            fadeIn.running = true
        }
    }

    Item {
        id: content
        anchors.fill: parent
        opacity: 0

        // Soft glow that breathes behind the logo
        Rectangle {
            id: glow
            anchors.centerIn: logo
            width: 420
            height: 420
            radius: 210
            color: "#2dd4bf"
            opacity: 0.06
            SequentialAnimation on scale {
                loops: Animation.Infinite
                NumberAnimation { from: 0.8; to: 1.15; duration: 1600; easing.type: Easing.InOutSine }
                NumberAnimation { from: 1.15; to: 0.8; duration: 1600; easing.type: Easing.InOutSine }
            }
        }

        Image {
            id: logo
            anchors.centerIn: parent
            source: "images/logo.svg"
            sourceSize.width: 180
            sourceSize.height: 180
            SequentialAnimation on scale {
                loops: Animation.Infinite
                NumberAnimation { from: 1.0; to: 1.05; duration: 1600; easing.type: Easing.InOutSine }
                NumberAnimation { from: 1.05; to: 1.0; duration: 1600; easing.type: Easing.InOutSine }
            }
        }

        // Three dots that light up in turn
        Row {
            anchors.top: logo.bottom
            anchors.topMargin: 56
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 14
            Repeater {
                model: 3
                Rectangle {
                    id: dot
                    required property int index
                    width: 10
                    height: 10
                    radius: 5
                    color: "#34d399"
                    opacity: 0.2
                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        PauseAnimation { duration: dot.index * 220 }
                        NumberAnimation { to: 1.0; duration: 380; easing.type: Easing.OutQuad }
                        NumberAnimation { to: 0.2; duration: 380; easing.type: Easing.InQuad }
                        PauseAnimation { duration: (2 - dot.index) * 220 }
                    }
                }
            }
        }
    }

    OpacityAnimator {
        id: fadeIn
        running: false
        target: content
        from: 0
        to: 1
        duration: 700
        easing.type: Easing.InOutQuad
    }
}
