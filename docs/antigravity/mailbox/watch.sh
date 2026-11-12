#!/bin/sh
# Cheap mailbox watcher for Antigravity's Lead. Run it as a background task, always.
# It checks immediately when started, then every 2 minutes while idle (last heartbeat line is
# "All coders idle...") or every 5 minutes while work is running. A plain file check, no AI cost.
# Something new: it prints the paths and exits, which wakes the Lead. The Lead handles the
# message, replies in to-claude/, then starts watch.sh again (which checks again at once).
cd "$(dirname "$0")" || exit 1
touch handled.txt heartbeat.log
while true; do
  new=""
  for f in to-antigravity/[0-9][0-9][0-9][0-9]-*.md; do
    [ -e "$f" ] || continue
    n=$(basename "$f" | cut -c1-4)
    grep -q "^$n picked-up" handled.txt || new="$new docs/antigravity/mailbox/$f"
  done
  if [ -n "$new" ]; then
    echo "NEW MESSAGE(S) FROM CLAUDE:$new"
    exit 0
  fi
  if grep -v '^[[:space:]]*$' heartbeat.log | tail -1 | grep -q "All coders idle"; then
    sleep 120
  else
    sleep 300
  fi
done
