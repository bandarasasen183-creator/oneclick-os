// Shown between logging in and the desktop appearing. Flat: the mark, and three dots that light up in turn.
import QtQuick

Rectangle {
    id: root
    color: "#000000"
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

        Image {
            id: logo
            anchors.centerIn: parent
            source: "images/wordmark.svg"
            sourceSize.width: 520
            sourceSize.height: 130
        }

        Row {
            anchors.top: logo.bottom
            anchors.topMargin: 64
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 14
            Repeater {
                model: 3
                Rectangle {
                    id: dot
                    required property int index
                    width: 8
                    height: 8
                    radius: 4
                    color: "#ffffff"
                    opacity: 0.25
                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        PauseAnimation { duration: dot.index * 220 }
                        NumberAnimation { to: 1.0; duration: 380; easing.type: Easing.OutQuad }
                        NumberAnimation { to: 0.25; duration: 380; easing.type: Easing.InQuad }
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
        duration: 500
        easing.type: Easing.InOutQuad
    }
}
