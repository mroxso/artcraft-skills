---
name: designcraft
description: Create and edit page layouts, text frames, styles, images, and data-merged documents in the DesignCraft application through its control protocol, MCP server, or CLI. Use when the user asks to work in DesignCraft.
---

# DesignCraft

Operate DesignCraft through its structured automation interfaces, preserving editable layouts and the user's chosen document.

## References

Read [references/control-protocol.md](references/control-protocol.md) before constructing desktop requests. It is an unmodified upstream snapshot downloaded on 2026-10-08.

Source: [DesignCraft control protocol](https://raw.githubusercontent.com/storytold/designcraft/refs/heads/main/docs/control-protocol.md). The documentation is distributed under the [bundled MIT license](references/LICENSE-MIT). Relative links in the snapshot resolve against `https://github.com/storytold/designcraft/blob/main/docs/`.

For tool schemas, session modes, and coordinates, consult the [upstream MCP documentation](https://github.com/storytold/designcraft/blob/main/docs/mcp.md). For CLI script syntax, result references, and data merge, consult the [agent guide](https://github.com/storytold/designcraft/blob/main/docs/agents.md). Discover installed command parameters when they differ from the snapshot; do not borrow flags or schemas from other ArtCraft applications.

## Choose the session

Discover available DesignCraft tools, executables, and existing sessions first. Prefer a connected MCP server when available.

- To edit the user's running app, use desktop control or `designcraft-cli mcp --connect PORT` (also accepts `HOST:PORT`).
- For independent file processing, `designcraft-cli mcp` starts an in-process headless engine with an empty Letter document. Open the intended file before editing it. This mode does not change the user's live window.
- CLI scripts can process files or connect to the running app. Inspect `designcraft-cli --help` and the relevant subcommand before choosing arguments.

Start a needed desktop control session with `designcraft --control <port>` or `DESIGNCRAFT_CONTROL_PORT`; 7979 is an upstream example, not a required port. Reuse existing sessions where possible. The server binds to loopback and has no authentication; enable it only while using it. If the application or connection is unavailable, report the missing prerequisite. This skill does not install DesignCraft or configure MCP servers.

## Control transport and discovery

The desktop control channel is raw TCP with UTF-8 JSON lines, not HTTP or MCP JSON-RPC. Send one request per newline, read one reply per request, use unique IDs, and check `ok` before dependent actions:

```json
{"id":1,"method":"document.inspect"}
{"id":2,"method":"ui.inspect"}
{"id":3,"method":"engine.commands"}
```

`engine.execute` takes `{command, params}`; discover command IDs, parameters, and enabled state through `engine.commands`. With MCP, use `list_commands` and `execute`, or dedicated tools after inspecting their schemas. MCP failures may be tool results with `isError: true`.

Malformed lines close the TCP connection, requests must not exceed 4 MiB, and the server allows at most 16 simultaneous connections. Reconnect after an error reply. If a mutation loses its reply or times out, inspect the resulting document before replaying it. Stop and report uncertainty when you cannot determine whether it ran; repeated creation or merge can duplicate work.

## Layout and text editing

Inspect pages, spreads, item IDs and bounds, stories, overset, styles, swatches, layers, and selection before targeting edits. MCP provides `inspect_document` and `get_story`; desktop provides `document.inspect`. Inspect UI state separately when focus, tools, or dialogs matter.

Prefer engine commands or dedicated MCP tools for precise frames, text, styles, and image placement. Use actual returned item and story IDs for subsequent edits, and establish selection or text range when a command depends on it. `set_story_text` replaces the story's text; use it for replacement, not a partial insertion unless the complete resulting text is intended. Preserve text threading and editable styles when they suit the requested layout.

Coordinates are points (1/72 inch), y increases downward, in spread space. On facing spreads the right page begins at x = page width; inspect page bounds instead of assuming each page starts at zero. MCP `render_page` and `export_png` use zero-based page indices. Inspect command parameters before interpreting a frame's `rect` or other geometry arrays.

For tool gestures, select the active tool deliberately. Desktop `ui.pointer` supports explicit `space: "canvas"` or `"screen"`; inspect zoom, origin, and canvas rect before screen interaction. MCP connected `pointer` supports screen space too. Keyboard and text input depend on the insertion point or focused field; prefer story or engine edits when deterministic targeting matters.

Use `ui.menu.list` and `ui.menu.invoke` for menus. Invoking a parameterized menu command without params can open its dialog rather than perform the edit. Inspect the dialog, fill documented fields with `ui.dialog.set`, and confirm or cancel it. Do not assume a menu invocation completed the document change.

## Scripts and data merge

For multi-command CLI jobs, read the agent guide first. Scripts accept command lines, JSON lines, or a JSON array of `{command, params}`. Result references such as `"$0.story"` and `"$last.id"` let later steps target earlier results. MCP `batch` supports commands or script text and stops at the first error. Inspect `failedIndex` and partial results before continuing; do not replay a whole partially completed batch blindly.

For data merge, discover `data.source.select`, `data.fields`, `data.placeholder.add`, `data.options`, `data.preview`, `data.preview.stop`, and `data.merge`. Inspect source fields before adding placeholders and preview representative records for text overflow and image fitting. `data.merge` creates and activates a new document while leaving the template unchanged; save the merged document to its intended output path. The obsolete `spread` merge parameter is an error.

## Save, export, and verify

Use desktop `app.open`, `app.save`, and `app.export`, or MCP `open_document` / `save_document` for native `.designcraft` files and the installed export commands. Discover format-specific parameters rather than guessing file operation schemas. Save an editable native document when appropriate and export the requested delivery format separately.

Check resulting document structure and overset text, then render the relevant pages with `ui.render` or MCP `render_page` and view the images. Check margins, bleed, text flow, clipping, and image placement. Window screenshots show UI state; page renders show artwork and are available without a presented window. MCP window tools require connected mode. The reference also documents the source-tree `ui_shot` example for offscreen whole-window captures when needed.

Verify that saves and exports succeeded and that the actual output files exist and are readable before reporting completion. Return the saved paths and any material layout or export issues.
