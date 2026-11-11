---
name: anicraft
description: Create and edit 2D vector animations, stages, timelines, keyframes, tweens, symbols, and exports or automate workflows in the AniCraft application using its MCP server or headless CLI. Use when the user asks to work in AniCraft.
---

# AniCraft

Operate AniCraft (an early-alpha open-source 2D vector animation studio in Rust: desktop app, headless CLI, MCP server) through its structured automation interfaces. Preserve the user's requested animation workflow and target document.

## Protocol reference

Read [references/mcp.md](references/mcp.md) before connecting an MCP client or scripting calls. This is the downloaded upstream MCP documentation, captured on 2026-11-11. Source: [AniCraft MCP docs](https://raw.githubusercontent.com/storytold/anicraft/refs/heads/main/docs/mcp.md), distributed under the [bundled MIT license](references/LICENSE-MIT). Relative links inside the snapshot resolve against `https://github.com/storytold/anicraft/blob/main/docs/`. AniCraft has no desktop control channel: the live window is driven by the user, and agents work on documents through the headless engine. If installed behavior differs, discover the installed command registry (`anicraft-cli commands`) rather than inventing command IDs or parameters.

## Select the surface

- **MCP server:** `anicraft-cli mcp [file.anicraft|--sample]` speaks MCP over stdio (JSON-RPC 2.0, one message per line; protocol revisions 2025-06-18, 2025-03-26, 2024-11-05). It runs its own in-process document and cannot touch the user's open window. Register the full path to `anicraft-cli`.
- **One-off file processing:** `anicraft-cli exec <file|--sample> <command.id> ['<json-params>'] [--save out.anicraft]` runs one command; `anicraft-cli run <file|--sample> <script.json> [--save]` replays a JSON list of commands; `info`, `render`, `render-seq`, `gif`, and `new --out <file> [--width W] [--height H] [--fps F]` cover inspection, exports, and creating documents without scripting.
- **Persistent JSON-lines session:** `anicraft-cli serve [file|--sample]` takes one request per line, `{"id":1,"cmd":"draw.rect","params":{"x":10,"y":10,"w":50,"h":50}}`, and answers `{"id":1,"ok":true,"result":{},"revision":7,"frame":0}`; send `{"cmd":"quit"}` to exit.
- **Desktop app:** `AniCraft [file] [--screenshot out.png] [--open <panel>]` opens the window for the user; `--screenshot` draws, saves the window image, and exits (a visual check; `--open` can preselect a panel). Other flags: `--renderer wgpu|gl`, `--theme`, `--scale`, `--lang`.

Discover executables first: on macOS the CLI ships inside the app bundle (`/Applications/AniCraft.app/Contents/MacOS/anicraft-cli`); elsewhere try `command -v anicraft-cli`. Reuse a running session when one fits. If the executable is missing, report the concrete prerequisite; this skill does not install AniCraft or register MCP servers.

## Discover commands before using them

`anicraft_commands` (MCP, filter by words such as `tween` or `export`) and `anicraft-cli commands` list every command with `id`, `label`, `menu`, `shortcut`, `mutates`, and its `params` shape — 225 commands in 0.2.0 across families like `draw.*`, `paint.*`, `path.*`, `raw.*`, `stroke.*`, `text.*`, `element.*`, `modify.*`, `align.*`, `arrange.*`, `layer.*`, `frames.*`, `timeline.*`, `tween.*`, `motion.*`, `bone.*`, `camera.*`, `scene.*`, `symbol.*`, `library.*`, `sound.*`, `script.*`, `actions.*`, `file.*`, `doc.*`, `edit.*`, `control.*`, and `plugin.*`. Read the parameter docs from the registry instead of guessing fields.

## Inspect, edit, and verify

Inspect first: `anicraft_document` (MCP) or `anicraft-cli info <file|--sample>` describes the stage, scenes, layers and keyframes, library, and the current scene, frame, layer, and selection.

Edit through `anicraft_run {command, params}` (MCP), `anicraft_run_script` for a sequence that stops at the first failing step and names it, `exec`/`run` on the CLI, or `serve` lines. A typical build: `file.new` (or open a document), `layer.new` / `scene.new` for structure, `draw.rect` / `draw.ellipse` / `draw.path` / `draw.freehand` / `text.create` for artwork, `timeline.insert_keyframe` and `timeline.create_tween` / `create_shape_tween` / `create_motion_tween` with `timeline.set_easing` for animation, and `library.*` / `symbol.*` for reusable assets.

Frame numbering: engine frames (MCP params, `serve`, command params) are 0-based; the CLI's own `--frame`, `--from`, and `--to` flags are 1-based, as in the timeline UI. Know which surface you are on before setting a frame.

Verify by rendering, not by assumption: `anicraft_render` (MCP) returns a frame of the current scene as a PNG picture, exactly as exported; `anicraft-cli render --frame N --out f.png`, `render-seq`, and `gif` write files. View the returned image or the written frames and check composition, tween easing, and layer order before telling the user the animation is right.

## Safety and files

Every edit goes through the engine's commands, so params are checked and any change can be undone with `edit.undo`. Commands that would lose unsaved work or replace an existing file refuse until their params include `"confirm": true` — ask the user before confirming, and never set it by default. Commands read and write files with your permissions at the paths given (open, save, import, export); connect only clients you trust with those files.

The native format is `.anicraft` (documented JSON). `file.open` also accepts Adobe Animate documents (`.fla`, `.xfl`, XFL folders); `file.import` brings SVG to the stage and `file.import_to_library` into the library. Export through `file.export_png`, `file.export_png_sequence`, `file.export_gif`, `file.export_svg`, `file.export_sprite_sheet`, `file.export_lottie`, `file.export_html`, `file.export_audio`, and `file.export_video` (WebM/MP4 through the user's own ffmpeg). Save the user's document (`file.save`, or `--save` on the CLI), report the exact paths written, and do not overwrite the user's source file unless asked.

AniCraft is early alpha: audio layers, ActionScript beyond the timeline subset (frame scripts are kept and those controlling the timeline run), motion tweens from XFL, and a GPU stage renderer are still missing. Say so when a task needs a missing feature instead of faking it.
