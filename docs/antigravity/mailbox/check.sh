#!/bin/sh
# Prints Claude's messages in to-antigravity/ that are not yet listed in handled.txt.
cd "$(dirname "$0")" || exit 1
touch handled.txt
found=0
for f in to-antigravity/[0-9][0-9][0-9][0-9]-*.md; do
  [ -e "$f" ] || continue
  n=$(basename "$f" | cut -c1-4)
  if ! grep -q "^$n picked-up" handled.txt; then
    echo "NEW MESSAGE: docs/antigravity/mailbox/$f"
    found=1
  fi
done
[ "$found" = 0 ] && echo "No new messages from Claude."
exit 0
