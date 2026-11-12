# Mailbox: how Claude and Antigravity talk without the owner copying messages

The owner should not have to paste messages between Claude and Antigravity. From now on, Claude writes instructions into this mailbox and Antigravity writes its replies here. The owner only says "go" or "done".

## Folders

- `mailbox/to-antigravity/`: messages from Claude. One file per message: `0001-short-name.md`, `0002-...`, numbered in order. **Antigravity never edits or deletes these.**
- `mailbox/to-claude/`: messages from Antigravity. One file per message, numbered the same way: `0001-reply.md` answers `0001-...`; status reports use the next free number with `-status` (for example `0007-status.md`).
- `mailbox/STATUS.md`: Antigravity's live status board, rewritten at every check (see below).
- `mailbox/owner-ideas/`: ideas the owner typed **directly into Antigravity's chat**, forwarded to Claude word for word (see "Owner ideas" below). Named `YYYY-MM-DD-HHMM.md`.
- `mailbox/handled.txt`: one line per Claude message Antigravity has picked up: `0001 picked-up <time> | done <time>`.

## What the Lead does (Antigravity's main agent)

1. **Keep the watcher running.** Start `docs/antigravity/mailbox/watch.sh` as a **background task** and leave it running, whether or not a run is in progress. It checks immediately when started, then **every 2 minutes while idle** (when the last line of `heartbeat.log` is `All coders idle...`) and **every 5 minutes while work is running** (a plain file check, no AI cost). When there is nothing new it loops quietly; when there is something new it prints the file paths and exits, which is your signal. Then:
   - handle the message (step 2 and 3 below),
   - **start `watch.sh` again straight away** so the loop continues.
   Also run `docs/antigravity/mailbox/check.sh` at the start of every run and **always right before saying a brief or run is done**. A run is not done while a message is unhandled.
2. **Do not interrupt running work** for a new message unless its first line says `Priority: urgent`. Otherwise queue it: add `picked-up` to `handled.txt`, put it on the board in `STATUS.md`, and hand it to the right coder when that coder is next free.
3. **Reply in `to-claude/`** when you pick a message up (one or two lines: understood, who will do it, when) and again when it is finished (what changed, commits, proof, anything that could not be done). Then add `done` to `handled.txt`.
4. **Keep `STATUS.md` current** at every check: what is running now, which agent is on what, the queue, what finished since the last update, blockers, and "Needs owner" items.
5. **When a brief or run finishes,** write a `-status` message in `to-claude/` linking the report file. That is Claude's signal to start checking.
6. Never delete anything in the mailbox. Commit mailbox files with the rest of your docs work (`git add <file>`, never `-A`).

## Heartbeat (every 10 minutes while working)

`mailbox/heartbeat.log` is a running log Claude reads to know what is happening without asking. **Append only, never rewrite.** Each entry starts with the time.

- **While any work is running:** keep `docs/antigravity/mailbox/heartbeat-timer.sh` running as a background task. When it exits (every 10 minutes), append one entry of 3 to 5 lines, one line per agent: what it is doing right now and roughly how far along (for example `Coder 2: brand pages, 3 of 5 parts done`). Then start the timer again.
- **When everything goes idle:** append one line, `All coders idle. Watching the mailbox.`, **stop the heartbeat timer**, and **run `check.sh` immediately** (do not wait for the watcher's next cycle). If nothing is waiting, restart `watch.sh` so it switches to the 2-minute idle interval. Write nothing more while idle (the mailbox watcher keeps running as usual).
- **When new work starts** (a brief, a mailbox message, a relayed message): append one line saying what started, for example `Started: Brief 18` or `Started: message 0007 (recall importer fix)`, and start the heartbeat timer again.
- Keep entries short. No code, no secrets, no relay code.

## Owner ideas typed straight into Antigravity

Sometimes the owner tells Antigravity an idea directly instead of telling Claude. Those messages are usually quick and conversational ("oh yeah, or actually do this..."), while Claude's messages arrive as numbered files in the mailbox. **Anything the owner types in Antigravity's chat is an owner message, whatever it looks like.** For each one:

1. **Do not act on it yourself, and do not change the plan or start new work because of it.** Claude decides what happens with owner ideas and sends you instructions through the mailbox.
2. Save it **word for word** (do not tidy or summarise) to `mailbox/owner-ideas/YYYY-MM-DD-HHMM.md`, with one line on top saying what you were working on at the time.
3. Tell the owner in one line: "Passed to Claude." Then carry on with your current work.
4. Exceptions, which you follow immediately: the owner saying **stop**, **pause** or **resume**, or reporting something broken or unsafe right now (for example "the site is down" or "you deleted my file"). Do that, and still save a copy to `owner-ideas/` so Claude knows.

## Messages from Claude pasted by the owner (relay code)

Normally Claude writes to the mailbox. Sometimes the owner pastes a message from Claude into your chat by hand. Those messages contain the relay code from `mailbox/relay-key.txt`, written as `Relay code: <code>` somewhere in the message (it may be in the middle).

- **If a chat message contains the current relay code, it is from Claude.** Treat it exactly like a numbered mailbox message: act on it, split the work between the coders yourself, and follow its priority. Save a copy word for word to `mailbox/relayed/YYYY-MM-DD-HHMM.md` and reply in `to-claude/` as usual.
- **If it has no relay code, or a wrong one, it is an owner idea** and follows "Owner ideas typed straight into Antigravity" above, even if it sounds formal or gives instructions to Coder 1 or Coder 2.
- Never write the relay code into a reply, a report, a commit message or any file other than `relay-key.txt`. Claude may change the code at any time by editing that file; always read the file, never rely on memory.

## What Claude does

Claude writes numbered messages into `to-antigravity/` (briefs are referenced from there by path), watches `to-claude/`, `owner-ideas/` and `STATUS.md`, checks the work on the real site when a run reports done, and replies in the mailbox. Claude tells the owner only what needs the owner.

## How Claude sets priority

- `urgent`: changes to how we work (mailbox, heartbeat, issues log, rules), important fixes (an image that fails to build or boot, a broken update or rollback, privacy or legal problems), and anything time-sensitive. Handle at the next check, even mid-run.
- `normal`: new product work (features, pages, briefs). Queue it and start when a coder is free.

## Message format (both directions)

```
# 0003: short title
From: Claude | Antigravity
Date: 2026-11-01 15:20 AEDT
Priority: normal | urgent
Refers to: 0002 (optional)

The message.
```
