---
name: vectorcraft
description: Create and edit vector artwork, paths, text, artboards, and live effects in the VectorCraft application using its control protocol, MCP server, or headless CLI. Use when the user asks to work in VectorCraft.
---

# VectorCraft

Operate VectorCraft through its structured automation interface, keeping the user's chosen document and intended editability.

## References

Read the relevant parts of [references/control-protocol.md](references/control-protocol.md) before constructing desktop calls. This is an unmodified upstream snapshot downloaded on 2026-10-08.

Source: [VectorCraft control protocol](https://raw.githubusercontent.com/storytold/vectorcraft/refs/heads/main/docs/control-protocol.md). The upstream documentation is distributed under the [bundled MIT license](references/LICENSE-MIT).

The reference begins with the method table; search for the particular tool, dialog, or format when needed. Useful terms include `Background Save / Export`, `SVG Options`, `Import PDF`, `gradientStop`, `Effect dialogs`, `Native save options`, and `Modifiers on synthetic input`. Relative links resolve against `https://github.com/storytold/vectorcraft/blob/main/docs/`.

For MCP tool schemas, headless batch syntax, and engine command examples, consult the [upstream MCP documentation](https://github.com/storytold/vectorcraft/blob/main/docs/mcp.md) when needed. Discover the installed command registry and tool schemas if behavior differs; do not borrow parameters or authentication flags from other ArtCraft applications.

## Choose the session

Discover available VectorCraft tools, installed executables, and existing sessions first. Prefer a connected MCP server when available.

- To edit the user's live app document, use desktop control or MCP explicitly connected to that app: `vectorcraft-cli mcp --connect 127.0.0.1:7979`.
- For independent file processing, use `vectorcraft-cli mcp --headless`, or the batch CLI after reading its syntax in the MCP documentation.
- With no mode flag, `vectorcraft-cli mcp` tries port 7979 and falls back to headless. Pin the mode when the target matters: a headless session does not edit the user's open app window.

A needed desktop session can be started with `vectorcraft --control 7979`; adapt the executable and available port to the environment. Reuse an existing session where possible. The port is loopback-only and has no authentication; enable it only while using it. If the executable or connection is unavailable, report the missing prerequisite. This skill does not install VectorCraft or configure MCP servers.

## Desktop transport

The control port is raw TCP, not HTTP or MCP JSON-RPC. Send UTF-8 JSON objects, one per newline, and read one reply per request. Use unique request IDs, match replies, and check `ok` before dependent actions:

```json
{"id":1,"method":"ui.inspect","params":{}}
{"id":2,"method":"document.inspect","params":{"depth":1,"childLimit":20}}
{"id":3,"method":"engine.commands","params":{}}
```

`engine.execute` takes `{command, params}`. Its `command` is an engine command ID discovered from `engine.commands`; it is separate from the transport `method`. For MCP, use `list_commands` and `run_command {command, params}` or the appropriate dedicated tool.

Malformed request lines close the connection; request lines must not exceed 4 MiB. The server supports at most 16 concurrent connections. Reconnect after an error reply. If a mutation times out or loses its reply, inspect document state and history before replaying it; stop and report uncertainty if its outcome cannot be determined safely.

## Inspect and edit

Inspect the active document, artboards, selection, paint target, active tool, and any open dialog before editing. Desktop uses `document.inspect` and `ui.inspect`; MCP uses `inspect_document` and, in remote mode, `inspect_ui`.

On large documents, use `depth` and `childLimit` to bound inspection. Discover or use `document.find` to locate relevant objects and `document.node {id, summary: true, depth?, childLimit?}` to drill into them. Obtain actual object IDs before targeting edits; new objects become the selection and many commands act on it. Set selection explicitly with `select.set {ids}` or use command-specific `ids` where supported.

Use engine commands or dedicated MCP tools for precise shapes, paths, text, paint, transforms, and effects. MCP exposes `draw_path`, `draw_shape`, `add_text`, `set_paint`, `transform`, `pathfinder`, and `apply_effect`; inspect their schemas before calling. Preserve editable type, live effects, blends, and envelopes when they suit the requested result; expand, outline, or rasterize only when needed for that result.

For gestures, document coordinates are points, y increases downward, and the origin is the first artboard's top-left. Desktop `ui.pointer` events support explicit `space: "doc"` or `space: "screen"`; choose the space deliberately and inspect the view and canvas rectangle before interacting with screen widgets. MCP `pointer_gesture` uses document coordinates. Set the active tool and inspect snapping and tool options before drawing. `ui.text` and remote MCP `type_text` depend on focus; use text commands for deterministic content edits.

Use `ui.menu.list` / `ui.menu.invoke` when working through application menus. Calls may return `pending` or open a dialog rather than complete the action. Inspect the dialog, set its documented fields with `ui.dialog.set {field, value}`, and confirm or cancel as appropriate. Previewing dialogs can modify the canvas temporarily; confirmation keeps the edit and cancellation rolls the preview back. Do not discard unsaved work in `saveChanges` or recovery dialogs without authorization.

## Save, export, and verify

Desktop file operations are `app.open`, `app.save`, and `app.export`; MCP provides `open_file`, `save_file`, and `export`. Query `document.formats` for installed format support and options. Inspect import/export `warnings`, including fallback raster previews and lost format features.

Save editable deliverables as `.vectorcraft` when appropriate and export the requested delivery format separately. Save uses the document's own format: an opened or saved SVG/PDF can save as that format again. Use an explicit native path when a native copy is wanted. Export does not change the document's path. SVG save operations can open `svgOptions` unless explicit SVG options are provided.

Check artboard scope and indexing: MCP export's `artboard` is zero-based, while its `range` uses one-based values such as `"1-3, 5"`. Desktop `useArtboards` can produce several files; inspect returned `files` instead of assuming only the requested path exists. Without a path, exports can return `dataBase64` rather than write a file. Read the format-specific options before setting resolution, text outlining, color models, transparency, or linked assets.

Desktop saves and exports run in the background by default. A reply containing `background: true` acknowledges a queued snapshot write, not completion. Inspect `ui.inspect`'s `background` jobs until the relevant write finishes, then verify the output exists and is readable before reporting success. Later edits are not part of an earlier snapshot. Inspect state before retrying a failed or uncertain write.

Verify the resulting object structure and visual output. Desktop `ui.render` renders the artboard without requiring a presented window; `ui.screenshot` captures the window and needs a visible presented frame. MCP `screenshot` renders artwork by default, while `window: true` captures the remote window and is unavailable headlessly. View the returned image or local preview and check composition, clipping, text, and effects. Report actual saved/exported paths and material warnings.
