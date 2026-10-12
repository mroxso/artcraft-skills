---
name: cadcraft
description: Create and edit CAD drawings, entities, layers, and layouts or automate workflows in the CADCraft application using its control protocol, MCP bridge, or headless CLI. Use when the user asks to work in CADCraft.
---

# CADCraft

Operate CADCraft through its structured automation interface. Preserve the user's requested drafting workflow and target drawing.

## Protocol reference

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing calls. This is the downloaded upstream protocol, captured on 2026-10-12.

Source: [CADCraft control protocol](https://raw.githubusercontent.com/storytold/cadcraft/refs/heads/main/docs/control-protocol.md).

Useful sections: the **method table** (top of the document), **Panel docking**, **Command-line replies**, and **Interface language**. Relative links inside the downloaded document (e.g. `localization.md`) refer to upstream documentation; resolve them against `https://github.com/storytold/cadcraft/blob/main/docs/` when needed. The document is short and does not list individual drawing commands: discover them at runtime with `engine.commands` instead of inventing command IDs or parameters.

## Locate the executables

`cadcraft` and `cadcraft-cli` may not be on `PATH` even when CADCraft is installed. Discover them before assuming anything is missing, and never invent a path — search for it:

1. **PATH:** `command -v cadcraft cadcraft-cli` (POSIX) or `where cadcraft cadcraft-cli` (Windows).
2. **macOS:** look for `CADCraft.app` in `/Applications` and `~/Applications`, or run `mdfind -name CADCraft.app`; the binary inside `Contents/MacOS/` is the desktop app.
3. **Linux / Windows:** check the usual install locations and the target of any desktop or Start-Menu shortcut.
4. **`cadcraft-cli` missing is not a blocker.** The control port speaks plain line-delimited JSON over loopback TCP and needs no bridge: send one request per line, e.g. `{"id":1,"method":"cmdline.input","params":{"text":"circle 0,0 5"}}`, and match replies by `id` and `ok`. A short script in any language covers every method.

## Select the session

- For a user's open drawing or visible application, use an existing CADCraft MCP bridge or control session. A headless session has its own in-process drawings and cannot edit the user's live window.
- For unattended processing of files, use headless MCP (`cadcraft-cli mcp`).
- Discover available CADCraft tools and installed executables first. If the required connection or executable is missing, report the concrete prerequisite; creating this skill does not install CADCraft or register an MCP server.

Start a desktop session with `--control PORT` (or `CADCRAFT_CONTROL_PORT=PORT`); it listens on `127.0.0.1:PORT`. Bridge it with:

```sh
cadcraft-cli mcp --connect 127.0.0.1:PORT
```

Reuse a running session when possible and keep TCP on loopback. The upstream protocol documents no authentication handshake or file-access roots; if the installed version requires a token or roots, follow its `--help` output rather than guessing.

Use `CADCRAFT_CONFIG_DIR` to point the app at a private, isolated profile for automation (an explicitly empty value disables workspace reads and writes). Do not edit the user's `workspace.json` directly.

## Inspect, edit, and verify

Inspect before editing: `drawing.inspect` for counts, extents, layers, styles, blocks, layouts, selection, and undo state; `ui.inspect` for the UI state, active view, and any pending "Save changes?" prompt (`closePrompt`); `cmdline.state` for the current prompt. The app may restore or already hold drawings you did not create.

Two ways to edit:

- **Command line** — `cmdline.input {text}` behaves exactly like a user typing: it starts commands by name or alias and answers prompts (points `x,y`, relative `@dx,dy`, polar `@d<a`, distances, keywords, empty = Enter). Spaces act as Enter except at text prompts. `cmdline.script {text}` runs a multi-line script; `cmdline.key` sends Enter or Escape. Always return the command line to the idle `Command:` prompt (Escape) before the next unrelated operation.
- **Engine commands** — `engine.execute {command, params}` runs any command with JSON parameters and never opens a dialog. Look up IDs, parameter docs, and enablement via `engine.commands`.

A refused command-line entry (unknown command, invalid input) still replies `"ok": true`; **always check the `error` field** and `output` of the reply. `app.open` without a string `path` fails with `"missing path"`.

Use `ui.menu.invoke` only when interactive menu behavior is intended. `ui.pointer` defaults to world coordinates; `ui.click`, `ui.move`, and `ui.drag` use screen points and reach every widget. `ui.key` only queues key events — poll `ui.inspect` or `ui.elements` for the resulting focus or state before the next action. Use `ui.elements` (exact-match filters on `label`, `role`, `focused`) to find controls instead of guessing coordinates.

Panel layout (`ui.dock`, `ui.dock.reset`, panel IDs `toolSets`, `layers`, `properties`, `externalReferences`; the `canvas` is protected) is invoked through `engine.execute` and does not edit document contents. Change layout, theme, or interface language only when the task requires it.

Verify visually and structurally: re-run `drawing.inspect` (entities carry handles and geometry) and render with `ui.render` — a headless render that frames the whole drawing by default (`fit: false` keeps the current view) and returns `pngBase64`, or pass `path`. `ui.screenshot` captures the app window and needs a presented frame.

## File access and output

- Desktop control: `app.open {path}` / `app.save {path}` / `app.quit`.
- Save output as DXF or DWG: `ui.set` with `saveFormat: "dxf"|"dwg"` and `saveVersion: "2000"`…`"2018"` set what Save As suggests for new drawings; `SAVEAS` also accepts `version` and `binary` directly.
- Report successful saves and the exact output path and format/version. Do not overwrite the user's source drawing unless asked; save a copy under a new name.

## Timeouts and uncertain outcomes

The server waits up to 60 s for the app to answer. A timeout reply carries `state`:

- `"not-run"` — the request was cancelled and will never run; resending is safe.
- `"may-have-run"` — the app had already started it and may still change the drawing (its late result is discarded). **Inspect with `drawing.inspect` before resending any mutation.**

After a disconnect or any other unclear failure, inspect drawing and undo state before retrying. Stop and report unresolved state if inspection cannot determine whether replay is safe.
