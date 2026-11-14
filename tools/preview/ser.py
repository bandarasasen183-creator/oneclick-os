#!/usr/bin/env python3
"""Talk to the VM's serial console. ser.py [wait_seconds] line1 line2 ...  (sends each line, prints what comes back)"""
import os, socket, sys, time, re
s = socket.socket(socket.AF_UNIX); s.connect(os.path.expanduser("~/OneClickVM/serial.sock")); s.settimeout(0.5)
def read(t):
    end = time.time() + t; out = b""
    while time.time() < end:
        try:
            d = s.recv(65536)
            if d: out += d
        except socket.timeout:
            pass
    return re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07\x1b]*(\x07|\x1b\\)", "", out.decode("utf-8", "replace"))
args = sys.argv[1:]; wait = 3.0
if args and re.fullmatch(r"[0-9.]+", args[0]): wait = float(args.pop(0))
for line in args:
    s.sendall(line.encode() + b"\r"); sys.stdout.write(read(wait))
if not args: sys.stdout.write(read(wait))
