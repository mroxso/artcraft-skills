---
name: figcraft
description: Create and edit vector designs, frames, layers, components, styles, and prototypes in the FigCraft application using its control protocol, MCP bridge, or headless CLI. Use when the user asks to work in FigCraft.
---

# FigCraft

Operate FigCraft through its structured automation interface. Preserve the user's requested design workflow and target file.

## Protocol reference

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing calls. This is the downloaded upstream protocol, captured on 2026-11-09.

Source: [FigCraft control protocol](https://raw.githubusercontent.com/storytold/figcraft/refs/heads/main/docs/control-protocol.md). The documentation is distributed under the [bundled MIT license](references/LICENSE-MIT). Relative links inside the snapshot (e.g. `mcp.md`) refer to upstream documentation; resolve those against `https://github.com/storytold/figcraft/blob/main/docs/` when needed. If installed behavior differs, inspect the installed command registry through `engine.commands` rather than inventing parameters.

## Select the session

- The desktop app serves the control channel on `127.0.0.1` only: `figcraft --control 7979 [file.figcraft|file.svg|image]`. For the user's open file, drive that live window, directly or through the attached MCP server (`figcraft-cli mcp --attach 7979`, see upstream `docs/mcp.md`).
- The app can show files in several windows. Every method takes an optional `window` id from `window.list` (`0` is the main window); without it, requests go to the window last in front. `engine.execute`, `document.inspect`, `node.get`, and `ui.render` also take an optional `document` (open file id from `doc.list`, or a path) to act on a background tab.
- The web build exposes the same methods as promises on `window.figcraft` when the page URL carries a `control` query entry.
- Discover available executables and sessions first. If the required connection or executable is missing, report the concrete prerequisite; this skill does not install FigCraft or register an MCP server.

## Transport and limits

Requests are newline-delimited JSON, one per line, replies matched by `id`; check `ok`. Requests run on the UI thread at the start of the next frame. A 60 s timeout reply distinguishes a dropped request (never applied) from one already running (will take effect; inspect the document before retrying). A long request such as a big `command.batch` can raise its own wait with `timeoutMs` (up to 600000). A request line is limited to 32 MiB; at most 8 connections and 8 queued requests per queue are accepted. A minimised or covered window still answers state methods but cannot take `ui.screenshot` or `ui.input` until it paints.

## Inspect, edit, and verify

Inspect before editing: `document.inspect` (pages, layer tree, selection, styles, undo history; use `depth`, `fields`, or `outline: true` to bound output) and `node.get {id}` for one layer. Discover command ids, parameters, and menus through `engine.commands`.

Edit through `engine.execute {command, params}`; programmatic calls never open dialogs. Creation commands return `{"id": N}`; use real returned ids. Unknown parameters are errors, never ignored. Prefer editable nodes: `frame.create`, `node.create`, `node.set`, `shape.*`, `text.*`, `tool.set` plus `ui.pointer` gestures. Use `command.batch` for known sequences; with `onError: "continue"` only failed steps roll back, and steps can reference earlier results with `{"$ref": "name"}` or `{"$step": n}`. Pass `agent` beside `command` so comment activity is signed as an AI agent.

Coordinates are page units, y down; `x`/`y` in `node.set`/`node.create` are relative to the parent frame. `ui.pointer` takes page coordinates or screen pixels (`sx`, `sy`); `ui.input` sends raw window input (separate calls for press and release); `ui.key` sends canvas shortcuts; `ui.type` goes to the text being edited (begin with `text.edit.begin {id}` or a double-click). `ui.menu.invoke` clicks a menu item and may open a dialog; `ui.set` switches panels, tabs, and pickers.

Verify with `ui.render` (document PNG without chrome, works without a window) or `ui.screenshot` (whole window). Report material import warnings; `file.open` and `file.import` return a `summary`.

## File access and output

`--automation-read-root` and `--automation-write-root` (FigCraft 0.7.0+) confine control and injected input to task folders; writes go only inside a write root, reads only inside a read or write root, and networked collaboration is refused while confined. Use forward-slash paths inside the roots; a rejected path is an ordinary error (`automation path rejected: …`) — do not bypass it with ambient filesystem commands. Save native editable files as `.figcraft`; export SVG, PNG, or PDF as requested. `events.poll` watches comment activity; keep the returned `cursor` and re-read comments when `reset` is true.
