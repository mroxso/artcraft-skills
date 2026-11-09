---
name: materialcraft
description: Build and edit node-based procedural PBR materials, graphs, and texture exports or automate the MaterialCraft application using its control protocol, MCP bridge, or headless CLI. Use when the user asks to work in MaterialCraft.
---

# MaterialCraft

Operate MaterialCraft through its structured automation interface. Preserve the user's requested material workflow and target graph.

## Protocol reference

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing calls. This is the downloaded upstream protocol, captured on 2026-11-09.

Source: [MaterialCraft control protocol](https://raw.githubusercontent.com/storytold/materialcraft/refs/heads/main/docs/control-protocol.md).

Useful sections: the **Methods** table (which methods are headless-only vs app-only), **Key commands**, **Function graphs**, **Linked packages**, **3D material assignment**, and **Portable materials (TextureCraft)**. Relative links inside the downloaded document refer to upstream documentation; resolve them against `https://github.com/storytold/materialcraft/blob/main/docs/` when needed. The document lists key commands, not the full library of 227 nodes: discover node definitions and parameters at runtime with `library.list` / `command.list` instead of inventing IDs.

## Locate the executables

`materialcraft` and `materialcraft-cli` may not be on `PATH` even when MaterialCraft is installed. Discover them before assuming anything is missing, and never invent a path — search for it:

1. **PATH:** `command -v materialcraft materialcraft-cli` (POSIX) or `where materialcraft materialcraft-cli` (Windows).
2. **macOS:** look for `MaterialCraft.app` in `/Applications` and `~/Applications`, or run `mdfind -name MaterialCraft.app`; the binary inside `Contents/MacOS/` is the desktop app.
3. **Linux:** AppImage, Flatpak, deb/rpm, or tarball installs; the CLI may be a separate download.
4. **Built from source:** `cargo run --release -p materialcraft` and `cargo run --release -p materialcraft-cli -- …`.

## Select the session

- For a user's open package or visible application, use a MaterialCraft MCP bridge (`materialcraft-cli mcp --bridge <port>`) or the app's control channel (`materialcraft --control <port>`). A headless session has its own in-process workspace and cannot edit the user's live window.
- For unattended file processing, use headless MCP (`materialcraft-cli mcp --read-root DIR --write-root DIR`) or the JSON-lines server (`materialcraft-cli serve`), on stdio or `127.0.0.1:<port>` behind a token.
- Discover available MaterialCraft tools and installed executables first. If the required connection or executable is missing, report the concrete prerequisite; creating this skill does not install MaterialCraft or register an MCP server.

The control channel requires an `auth` request first on every connection: token from `MATERIALCRAFT_CONTROL_TOKEN` or the file `<temp>/materialcraft-control-<port>.token`. Then one JSON object per line, `{"id", "method", "params"}`; match replies by `id` and check `ok`. Set `MATERIALCRAFT_NO_PREFS=1` for scripted runs so the user's layout is left alone. Keep TCP on loopback and credentials in a private token file; do not print, commit, or expose tokens in command arguments.

## Inspect, edit, and verify

Inspect before editing: `session.inspect` returns the package, graphs, the open graph's nodes (def, params, bindings, base, ports, cook error/size/mean/ms), wires, frames, exposed inputs, views, and history. In the app, `ui.inspect` adds the graph view rectangle, per-node screen rectangles, and per-port screen positions. Discover command and node IDs with `command.list {filter?}` and `library.list {filter?, category?}`.

Build graphs with `file.new {template?, name?, size?}` (templates: `empty`, `pbr`, `bricks`, `stone_tiles`, `wood`, `rusty_metal`, `fabric`, `ground`), `graph.node.add {def, at?, params?, connectFrom?, label?}`, `graph.connect` / `graph.disconnect`, and `graph.node.param {id?, param, value}`. Parameter values are typed: numbers, `[x, y]`, `"#rrggbb"`, enum index, curve `[[x, y], …]`, gradient `[[pos, color], …]`, or `{"t": "function", "v": {...}}` for a function graph driving a parameter (dynamic parameter; remove with `{param, remove: true}`). Set per-node cook settings with `graph.node.base {sizeMode?, size?, format?, seed?, tiling?}`.

Commands run programmatically and never open dialogs. Use `ui.menu.invoke` only when interactive menu behavior is intended. For UI gestures, `ui.input {events}` applies synthetic events one frame at a time using **window points** taken from `ui.inspect` (`nodes`, `ports`): `move`, `down`, `up`, `click`, `doubleClick`, `drag`, `scroll`, `key` (egui key names), `text`.

Verify visually and structurally: re-run `session.inspect` and check each node's cook error and mean output; render with `view.screenshot {view: "3d"|"2d"}` (app) or `render {…}` (headless, PNG base64 — `hq: true` gives the beauty render with displacement, ray-traced AO and a shadowed key light). Use `view.2d` / `view.3d` commands to point the views at a specific node, channel, or scene; `view.3d.loadMesh {path}` shows an OBJ/glTF/GLB mesh (scene `custom`).

## File access and output

Headless file access is workspace-scoped by launch-time roots (`--read-root` / `--write-root`); use task-scoped roots and forward-slash relative paths within them. Do not bypass rejected paths by switching to ambient filesystem commands.

- Packages: `package.open {path}` / `package.save {path?}` (headless); the app saves through its own menus. `.mcmat` files open too (their source package, on its graph).
- Bitmaps: `bitmap.import {path, name?}` embeds an image as a resource.
- Texture maps: `outputs.export {dir, format?, pattern?, depth?, graph?}` cooks at full size and writes every output — PNG, JPEG, TGA, TIFF, BMP, WEBP, EXR or HDR at 8, 16 or 32 bits.
- Portable materials: `file.exportMaterial {path, graph?, size?, values?, inputs?}` writes a `.mcmat` for TextureCraft; `file.sendToTextureCraft {graph?}` exports into TextureCraft's library folder. In the workspace sandbox, exporting a `.mcmat` is CLI-only: `materialcraft-cli run package.mcraft file.exportMaterial '{"path": "out.mcmat", "size": 2048}'`.
- Report successful saves and exports with the exact output path and format. Do not overwrite the user's source package unless asked; save a copy under a new name.

## Batches and uncertain outcomes

Use `command.batch {steps}` (headless) for known sequences; it stops at the first error. Batches are not transactions: earlier steps persist on failure, so inspect per-step results.

After a disconnect or any other unclear failure, run `session.inspect` before retrying a mutation — the command may already have completed. Stop and report unresolved state if inspection cannot determine whether replay is safe.
