#!/bin/sh
# 10-minute heartbeat timer for Antigravity's Lead. Run as a background task ONLY while work is in progress.
# It just waits 10 minutes and exits; the exit is the Lead's cue to append a heartbeat to heartbeat.log.
sleep 600
echo "HEARTBEAT DUE: append a heartbeat to docs/antigravity/mailbox/heartbeat.log, then start heartbeat-timer.sh again if any coder is still busy."
