#!/usr/bin/env python3
"""Drive the preview VM over QMP.  vm.py click X Y | key NAME[+NAME] | type TEXT | shot FILE
X and Y are fractions (0-1) of the screen."""
import json, os, socket, sys, time

s = socket.socket(socket.AF_UNIX); s.connect(os.path.expanduser("~/OneClickVM/qmp.sock"))
f = s.makefile("rw")
def cmd(name, **args):
    f.write(json.dumps({"execute": name, "arguments": args}) + "\n"); f.flush()
    while True:
        r = json.loads(f.readline())
        if "return" in r or "error" in r:
            return r
f.readline(); cmd("qmp_capabilities")

def ev(events): cmd("input-send-event", events=events)
def key(q, down): return {"type": "key", "data": {"down": down, "key": {"type": "qcode", "data": q}}}
def press(names):
    ev([key(n, True) for n in names]); time.sleep(0.05); ev([key(n, False) for n in reversed(names)])

SHIFT = {"_": "minus", "!": "1", "@": "2", ":": "semicolon", "?": "slash"}
PLAIN = {" ": "spc", "-": "minus", ".": "dot", "/": "slash", ",": "comma", "\n": "ret", ";": "semicolon"}

a = sys.argv
if a[1] == "click":
    x, y = int(float(a[2]) * 32767), int(float(a[3]) * 32767)
    ev([{"type": "abs", "data": {"axis": "x", "value": x}}, {"type": "abs", "data": {"axis": "y", "value": y}}])
    time.sleep(0.2)
    ev([{"type": "btn", "data": {"down": True, "button": "left"}}]); time.sleep(0.08)
    ev([{"type": "btn", "data": {"down": False, "button": "left"}}])
elif a[1] == "key":
    press(a[2].split("+"))
elif a[1] == "type":
    for c in a[2]:
        if c in PLAIN: press([PLAIN[c]])
        elif c in SHIFT: press(["shift", SHIFT[c]])
        elif c.isupper(): press(["shift", c.lower()])
        else: press([c])
        time.sleep(0.03)
elif a[1] == "shot":
    print(cmd("screendump", filename=a[2], format="png"))
