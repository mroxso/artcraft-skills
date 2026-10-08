---
name: lightcraft
description: Organize, rate, develop, crop, render, and export photos in the LightCraft application through its desktop control protocol, MCP server, or headless CLI. Use when the user asks to work in LightCraft.
---

# LightCraft

Operate LightCraft through its structured automation interface, using the user's intended photo library and session.

## References

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing desktop calls. This is an unmodified upstream snapshot downloaded on 2026-10-08.

Source: [LightCraft control protocol](https://raw.githubusercontent.com/storytold/lightcraft/refs/heads/main/docs/control-protocol.md). The upstream MIT license is included in [references/LICENSE-MIT](references/LICENSE-MIT).

Search for `Methods`, `When the library can't be saved`, `When the library can't be opened`, and `Headless rendering` as needed. Relative links resolve against `https://github.com/storytold/lightcraft/blob/main/docs/`.

For MCP tool schemas, import modes, develop controls, export options, and one-shot CLI syntax, consult the [upstream MCP documentation](https://github.com/storytold/lightcraft/blob/main/docs/mcp.md) when needed. Discover installed command and tool schemas if behavior differs; do not reuse parameters from other ArtCraft applications.

## Choose the session

Discover available LightCraft tools, installed executables, and existing sessions. Prefer an available MCP connection that targets the intended session.

- For the user's running app, use desktop control or `lightcraft-cli mcp --connect 127.0.0.1:7980`. A needed desktop session can be started with `lightcraft --control 7980` or `LIGHTCRAFT_CONTROL_PORT=7980`; adapt executable paths and port to the environment.
- For independent photo processing, use `lightcraft-cli mcp [FILES/FOLDERS…]`. Headless is the default and runs a separate in-process session.
- For persistent headless edits, add `--library /absolute/path/library`. A library can be open in only one program at a time; if the app holds its catalog lock, connect to the app instead of opening that folder headlessly. Do not remove the lock to bypass this restriction.

Without `--library`, do not assume headless catalog edits persist between sessions. Use `--demo` only for requested demonstrations or isolated examples. Reuse an appropriate session; report a missing executable or connection when unavailable. This skill does not install LightCraft or configure MCP servers.

## Desktop transport

The control channel is raw loopback TCP, not HTTP or MCP JSON-RPC, and has no authentication; enable it only while needed. Send UTF-8 JSON objects, one per newline, with a string `method`, optional `params`, and distinct request IDs. Read one reply per request, match IDs, and check `ok` before dependent actions:

```json
{"id":1,"method":"ui.inspect","params":{}}
{"id":2,"method":"engine.commands","params":{}}
```

Discover engine and UI command IDs, parameter documentation, and enablement with `engine.commands`. Invoke them with `engine.execute {command, params}` (alias `ui.menu.invoke`). MCP uses `list_commands` and `run_command {command, params}`, helper tools, or `cmd_` tools named after command IDs with dots replaced by underscores.

Requests run on the UI thread between frames with a 60-second timeout. Invalid JSON objects, invalid UTF-8, and lines over 4 MiB close the connection; at most 16 connections are served. Reconnect after an error reply. After a timeout or lost mutation reply, inspect state before replaying; stop and report uncertainty if the outcome cannot be established safely.

## Inspect and edit photos

Inspect the library, current view/filter, active photo, selection, and background work before editing. Desktop uses `ui.inspect` plus discovered library/photo commands; MCP exposes `query_photos`, `get_develop`, and resources such as `lightcraft://library` and `lightcraft://photo/active`.

Obtain real photo IDs from queries and set selection explicitly with `select_photos {ids, active?, mode?}` or a discovered library selection command. Tools taking `id` make that photo active first; tools without it act on the active photo. For batch operations, use documented `ids` parameters or explicitly select the intended photos and verify scope before applying changes.

Discover develop control IDs, ranges, defaults, and current values with `list_controls` or the installed command registry. Use `set_develop` with `values` for individual controls or `settings` for a partial deep merge. Read current settings first and preserve unrelated edits. Query available presets instead of inventing preset IDs. MCP `crop` uses normalized `[x0,y0,x1,y1]` coordinates and a straighten angle; read its schema before combining crop and rotation.

For imports, preserve the user's intended source-file handling. Read import schemas before choosing reference, copy, or move behavior. Move mode removes verified, catalogued sources and their XMP sidecars; undo does not move them back. Inspect returned moved/kept results and failures before reporting completion.

Prefer commands and helper tools for precise edits. For desktop interactions, get stable widget IDs from `ui.widgets`; screen rectangles are in points, while `ui.pointer` gestures use normalized image coordinates in Detail view. Refresh widgets after layout changes. Text input depends on focus. Position the pointer before scroll or pinch zoom. `view.navigate` supports fit/fill or percentage zoom and a normalized image-centre pan; consult the reference for limits.

## Persistence, export, and verification

A persistent library journals mutations before replying. The error `saved in memory but not written to disk` means the edit already happened and is queued for persistence. Do not repeat it as though nothing changed. Inspect `ui.inspect` → `unsaved` or `library.info` → `unsavedOps` / `unsavedError`, resolve the storage problem within scope, and verify the queue clears. Do not quit or claim the edits are safely saved while unsaved operations remain.

If the library cannot open, inspect `libraryProblem`. A temporary session writes nothing; do not choose Continue Without Saving when the task requires durable edits. Retry, choose the intended accessible library, or report the blocking issue without discarding work.

Read the export schema before selecting format, dimensions, color space, quality, bit depth, or original/DNG output. MCP export defaults to a 3000-pixel long edge; use `longEdge: 0` for cropped native resolution when requested. Confirm explicit IDs and destinations. Rendering a preview does not constitute exporting a deliverable.

Desktop `app.export` with `background: true` acknowledges queued work. Poll `ui.inspect` → `export` until the relevant batch finishes, inspect its result, and verify returned files exist and are readable. Likewise, check import/task progress before treating asynchronous work as complete. Inspect state and outputs before retrying an uncertain export.

Verify develop settings and selection scope, then view a rendered photo or screenshot to assess exposure, color, crop, and the requested look. Desktop `ui.render` renders a photo; `ui.screenshot` waits for finished renders and supports CPU capture with `headless: true`, including when the window is occluded.

For independent UI snapshots, `lightcraft-cli snapshot --library DIR --script tour.jsonl -o shot.png` accepts control requests. This opens its own session and must respect the library lock. Failed script requests do not stop subsequent requests, but make the exit status non-zero; inspect all replies and exit status before reporting success. `ui.settle {timeoutMs?}` waits for renders to finish in snapshot scripts. Report actual exported paths and any remaining persistence errors or unfinished work.
