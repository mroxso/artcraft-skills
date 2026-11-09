---
name: texturecraft
description: Create and edit 3D texture painting projects, texture sets, layer stacks, baking, and texture exports or automate the TextureCraft application using its control protocol, MCP bridge, or headless CLI. Use when the user asks to work in TextureCraft.
---

# TextureCraft

Operate TextureCraft through its structured automation interface. Preserve the user's requested texturing workflow and target texture set.

## Protocol reference

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing calls. This is the downloaded upstream protocol, captured on 2026-11-09.

Source: [TextureCraft control protocol](https://raw.githubusercontent.com/storytold/texturecraft/refs/heads/main/docs/control-protocol.md).

Useful sections: the **Control channel** method table, the **MCP server** tool table, **MaterialCraft materials**, and **CLI**. Relative links inside the downloaded document refer to upstream documentation; resolve them against `https://github.com/storytold/texturecraft/blob/main/docs/` when needed. The document lists example commands, not the full command library: discover command ids, labels, parameter docs and current enabled state at runtime with `command.list {filter?}` (MCP: `command_list`) instead of inventing ids.

## Locate the executables

`texturecraft` and `texturecraft-cli` may not be on `PATH` even when TextureCraft is installed. Discover them before assuming anything is missing, and never invent a path — search for it:

1. **PATH:** `command -v texturecraft texturecraft-cli` (POSIX) or `where texturecraft texturecraft-cli` (Windows).
2. **macOS:** look for `TextureCraft.app` in `/Applications` and `~/Applications`, or run `mdfind -name TextureCraft.app`; the binary inside `Contents/MacOS/` is the desktop app.
3. **Linux:** AppImage, Flatpak, deb/rpm, or tarball installs; the CLI may be a separate download.
4. **Built from source:** `cargo run --release -p texturecraft` and `cargo run --release -p texturecraft-cli -- …`.

## Select the session

- For a user's open project or visible application, use a TextureCraft MCP bridge (`texturecraft-cli mcp --bridge <port>`) or the app's control channel (`texturecraft --control <port>`). A headless session has its own in-process project and cannot edit the user's live window.
- For unattended file processing, use headless MCP (`texturecraft-cli mcp --read-root DIR --write-root DIR`), the JSON-lines server (`texturecraft-cli serve [--port <port>]`), or one-shot CLI subcommands (`new`, `run`, `batch`, `bake`, `export`, `render`, `info`).

The control channel requires an `auth` request first on every connection: token from `TEXTURECRAFT_CONTROL_TOKEN` or the file `<temp>/texturecraft-control-<port>.token`. Then one JSON object per line, `{"id", "method", "params"}`; match replies by `id` and check `ok`. Set `TEXTURECRAFT_NO_PREFS` (any value) for scripted runs so the user's layout and settings are left alone. Keep TCP on loopback and credentials in a private token file; do not print, commit, or expose tokens in command arguments.

## Inspect, edit, and verify

Inspect before editing: `session.inspect` returns the project, mesh, texture sets, the layer stack with every layer, mask, effect and fill source, painted tile counts, the tool, camera, display and history — an agent can verify most work without a screenshot. `project.inspect` shows a `.mcmat` fill layer's `link` (the MaterialCraft graph's exposed inputs, presets and image inputs).

Edit through engine commands via `command.run`: `project.new {mesh?, resolution?, name?, template?}` (built-in meshes: `material_ball`, `sphere`, `cube`, `rounded_cube`, `cylinder`, `torus`, `plane`, `crate`), `layer.add.fill {color?, roughness?, metallic?, …}`, `layer.add.image`, `mask.add.black`, `effect.add.generator {generator: "edgeWear"|…}`, `textureSet.meshMap.set` / `textureSet.meshMap.clear` for imported mesh maps, `bake.run {resolution?, maps?}` (exclude single UV tiles with `bake.tile.set`, patch bake settings field-wise with `bake.settings {ts?, patch}`), `material.apply {material}`, and painting through `tool.stroke` (or the MCP `paint_stroke` tool, whose points are viewport pixels). `edit.undo {steps?}` / `edit.redo {steps?}` move through history; any command accepts `merge: true` to fold its edit into the previous undo step.

Commands run programmatically and never open dialogs. Use `ui.menu.invoke` only when interactive menu behavior is intended. In the app, `ui.set` can change layout, dock, preferences (language, brightness, accent) and keymap; `debug.paintTest` and `debug.frames` exist for performance work.

Verify visually and structurally: re-run `session.inspect`, then render — `viewport.screenshot {view: "3d"|"2d"}` (app), `viewport_render` (MCP; `samples` up to 4096 path-traces the 3D view), `render` (JSON-lines), or `texturecraft-cli render project.tcraft out.png --size 1280x800 --yaw 30 --pitch 15` (CLI). Saved camera bookmarks (`camera.add` / `camera.list` / `camera.select`) pin repeatable views. Stroke points and render sizes share one space: the default render size is the session viewport (1280×800), so `paint_stroke` points can be read straight off a `viewport_render` image.

## File access and output

Headless file access is workspace-scoped by launch-time roots (`--read-root` / `--write-root`); use task-scoped roots and forward-slash relative paths within them. `..`, absolute paths, drive letters and symlink escapes are refused. Do not bypass rejected paths by switching to ambient filesystem commands. Through `command_run`, path-carrying commands (`file.*` except `file.close` / `file.removeUnused`, `resource.import`, `material.save`, …) are refused in both MCP modes: use the dedicated tools.

- Projects: `project_open {path}` (`.tcraft` or a mesh file) / `project_save {path?}`; in bridge mode `project_save` without a path invokes File › Save. Meshes: `mesh_import {path, resolution?}` (glTF/GLB, FBX, COLLADA, USD, Alembic, OBJ, PLY, STL), `mesh_reimport`, `mesh_export {path, format?}` (textured obj, glb, usd).
- Resources and baking: `resource_import {path}` embeds an image (for `layer.add.image` or `tool.stencil`, or as a mesh map via `textureSet.meshMap.set`); `bake_mesh_add {path, cage?}` adds a high-poly mesh; `bake {resolution?, maps?, cpu?}` bakes mesh maps, on the GPU when there is one.
- Materials: `material_save {path, layer?, name?}` writes a `.tcmat` smart material; `material_load {path}` reads `.tcmat`, a MaterialCraft `.mcmat` or `.mcraft` package; drive `.mcmat` inputs with `material.link.set` / `material.link.preset` / `material.link.cook` (re-cooks call `materialcraft-cli`, found via `$MATERIALCRAFT_CLI` or next to the executable).
- Textures: `textures_export {dir, preset?, ts?, format?, padding?, size?}` writes engine-ready maps (PNG, JPEG, TGA, TIFF, BMP, WEBP, EXR, HDR at 8, 16 or 32 bits); CLI: `texturecraft-cli export model.tcraft out/ --preset "Unreal Engine (Packed)"`.
- Report successful saves and exports with the exact output path and format. Do not overwrite the user's source project unless asked; save a copy under a new name.

## Batches and uncertain outcomes

Use `command_batch {steps}` (MCP, JSON-lines `command.batch`, or `texturecraft-cli batch script.json`) for known sequences; it stops at the first error and reports `{completed, results, failed}`. Batches are not transactions: earlier steps persist on failure, so inspect per-step results. Replies are capped (8 MiB of JSON, 5 MiB per PNG, 256 batch steps).

After a disconnect or any other unclear failure, run `session.inspect` before retrying a mutation — the command may already have completed. Stop and report unresolved state if inspection cannot determine whether replay is safe.
