#!/usr/bin/env python3
"""Talk to a running SolidCraft desktop app over its control channel.

The channel is line-delimited JSON over loopback TCP; this script is a thin
convenience wrapper, not a requirement. Every method in
references/control-protocol.md is reachable with `call`.

usage:
  sc.py [--port N] raw '<full request json>'
  sc.py [--port N] call <method> ['<params json>']
  sc.py [--port N] exec <command> ['<params json>']        engine.execute
  sc.py [--port N] batch '<[{"command":..,"params":..}]>'  engine.batch
  sc.py [--port N] inspect [--no-measure]                  document.inspect
  sc.py [--port N] ui                                      ui.inspect
  sc.py [--port N] measure ['<params json>']              engine.execute inspect.measure
  sc.py [--port N] cmds [filter]                           command registry
  sc.py [--port N] shot [view] [path]                      ui.render (model, no window needed)
  sc.py [--port N] shotwin [path]                          ui.screenshot (needs a presented window)
  sc.py [--port N] new | open <path> | save [path]
  sc.py [--port N] export <path> [format]
  sc.py [--port N] undo | redo | running | pending | wake

Exit code is non-zero and the reply is printed when the app answers ok:false.
"""
import json
import os
import platform
import socket
import subprocess
import sys

PORT = int(os.environ.get("SOLIDCRAFT_CONTROL_PORT", "7878"))
HOST = "127.0.0.1"
VIEWS = ("iso", "front", "back", "top", "bottom", "left", "right", "home", "fit")


def token_path(port):
    system = platform.system()
    if system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support/SolidCraft/control")
    elif system == "Windows":
        base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "SolidCraft", "control")
    else:
        data = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        base = os.path.join(data, "solidcraft", "control")
    return os.path.join(base, f"{port}.token")


def read_token(port):
    env = os.environ.get("SOLIDCRAFT_CONTROL_TOKEN")
    if env:
        return env.strip()
    with open(token_path(port)) as fh:
        return fh.read().strip()


class Conn:
    """One control connection; the token authenticates the first request."""

    def __init__(self, port=PORT):
        self.sock = socket.create_connection((HOST, port), timeout=600)
        self.buf = b""
        self.n = 0
        self.tok = read_token(port)

    def request(self, method, params=None):
        self.n += 1
        req = {"id": self.n, "method": method}
        if params is not None:
            req["params"] = params
        if self.n == 1:
            req["token"] = self.tok
        self.sock.sendall((json.dumps(req) + "\n").encode())
        while b"\n" not in self.buf:
            chunk = self.sock.recv(1 << 20)
            if not chunk:
                raise SystemExit("connection closed by the app (did it quit?)")
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        reply = json.loads(line)
        if not reply.get("ok", False):
            raise SystemExit("error: " + json.dumps(
                {k: v for k, v in reply.items() if k != "id"}, indent=2))
        return reply.get("result")


def out(value):
    print(value if isinstance(value, str) else json.dumps(value, indent=2))


def jarg(text, default=None):
    return default if text is None else json.loads(text)


def main(argv):
    port = PORT
    if argv[:1] == ["--port"]:
        port = int(argv[1])
        argv = argv[2:]
    cmd = argv[0] if argv else "help"
    a = argv[1:]
    need = {"raw": 1, "call": 1, "exec": 1, "batch": 1, "open": 1, "export": 1}
    if cmd in need and len(a) < need[cmd]:
        raise SystemExit(f"{cmd}: missing argument\n{__doc__}")
    if cmd == "help":
        print(__doc__)
        return
    c = Conn(port)

    if cmd == "raw":
        req = json.loads(a[0])
        req.setdefault("token", c.tok)
        c.sock.sendall((json.dumps(req) + "\n").encode())
        out(json.loads(c.sock.recv(1 << 20)))
    elif cmd == "call":
        out(c.request(a[0], jarg(a[1]) if len(a) > 1 else None))
    elif cmd == "exec":
        out(c.request("engine.execute", {"command": a[0], "params": jarg(a[1], {})}))
    elif cmd == "batch":
        out(c.request("engine.batch", {"commands": json.loads(a[0])}))
    elif cmd == "inspect":
        out(c.request("document.inspect", {"measure": "--no-measure" not in a}))
    elif cmd == "ui":
        out(c.request("ui.inspect"))
    elif cmd == "measure":
        out(c.request("engine.execute",
                      {"command": "inspect.measure",
                       "params": jarg(a[0], {}) if a else {}}))
    elif cmd == "cmds":
        regs = c.request("engine.commands")
        items = regs if isinstance(regs, list) else regs.get("commands", regs)
        for it in items:
            if not a or a[0].lower() in json.dumps(it).lower():
                out(it)
    elif cmd == "shot":
        view = a[0] if a else "iso"
        path = a[1] if len(a) > 1 else os.path.join(os.getcwd(), "solidcraft-shot.png")
        if view in VIEWS:
            c.request("ui.view", {"view": view, "animate": False})
        else:
            path = view
        out(c.request("ui.render", {"path": path}))
    elif cmd == "shotwin":
        path = a[0] if a else os.path.join(os.getcwd(), "solidcraft-window.png")
        out(c.request("ui.screenshot", {"path": path}))
    elif cmd == "new":
        out(c.request("engine.execute", {"command": "file.new", "params": {}}))
    elif cmd == "open":
        out(c.request("engine.execute", {"command": "doc.open", "params": {"path": a[0]}}))
    elif cmd == "save":
        out(c.request("engine.execute",
                      {"command": "file.save", "params": {"path": a[0]} if a else {}}))
    elif cmd == "export":
        params = {"path": a[0]}
        if len(a) > 1:
            params["format"] = a[1]
        out(c.request("engine.execute", {"command": "file.export", "params": params}))
    elif cmd in ("undo", "redo"):
        out(c.request("engine.execute", {"command": f"edit.{cmd}", "params": {}}))
    elif cmd == "running":
        out(c.request("control.running"))
    elif cmd == "pending":
        out(c.request("control.pending"))
    elif cmd == "wake":  # front the window so ui.screenshot has a frame (macOS)
        pid = os.environ.get("SOLIDCRAFT_PID")
        if platform.system() != "Darwin" or not pid:
            raise SystemExit("set SOLIDCRAFT_PID=<pid>; macOS only. "
                             "Otherwise use `shot` (ui.render), which needs no window.")
        subprocess.run(["osascript", "-e",
                        f'tell application "System Events" to set frontmost of '
                        f'(first process whose unix id is {pid}) to true'], check=True)
        out({"awoke": pid})
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
