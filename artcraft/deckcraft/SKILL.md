---
name: deckcraft
description: Create and edit presentations, slides, shapes, text, charts, and slide shows in the DeckCraft application through its control protocol, MCP server, or CLI. Use when the user asks to work in DeckCraft.
---

# DeckCraft

Operate DeckCraft through its structured automation interfaces, preserving editable slides and the user's chosen presentation.

## References

Read [references/control-protocol.md](references/control-protocol.md) before constructing desktop requests. It is an unmodified upstream snapshot downloaded on 2026-10-14.

Source: [DeckCraft control protocol](https://raw.githubusercontent.com/storytold/deckcraft/refs/heads/main/docs/control-protocol.md). The documentation is distributed under the [bundled MIT license](references/LICENSE-MIT). Relative links in the snapshot resolve against `https://github.com/storytold/deckcraft/blob/main/docs/`.

For MCP tools and session modes, consult the [upstream MCP documentation](https://github.com/storytold/deckcraft/blob/main/docs/mcp.md). The [repository](https://github.com/storytold/deckcraft) documents installation and supported workflows. Discover installed command parameters when they differ from the snapshot; do not borrow flags or schemas from other ArtCraft applications.

## Locate the executables and choose the session

Discover available DeckCraft tools, executables, and existing sessions first. Prefer a connected MCP server when available.

- For the user's open presentation, use desktop control or `deckcraft-cli mcp --connect PORT`. This operates the same deck as the visible app.
- For independent file processing, `deckcraft-cli mcp` starts its own headless engine. Open the intended presentation before editing it; this session does not change the user's live window.
- For one-off file operations, use `deckcraft-cli info`, `run`, `render`, or `convert`. Each invocation has its own session. Use `run --in FILE` to continue work on a saved deck; `--sample` loads the built-in sample, not the user's presentation.

Check `command -v deckcraft deckcraft-cli` on POSIX or `where deckcraft deckcraft-cli` on Windows. If absent from PATH, inspect application install locations. On macOS, look for `DeckCraft.app` in `/Applications` and `~/Applications` or use `mdfind -name DeckCraft.app`, then inspect `Contents/MacOS/`. Do not invent an executable path.

Start a needed desktop session with `deckcraft --control PORT`; 7990 is an upstream example. Reuse an existing session where possible. A missing CLI does not prevent direct TCP control of the desktop app. If neither an executable nor a usable connection is available, report the missing prerequisite. This skill does not install DeckCraft or configure MCP servers.

## Control transport and discovery

Desktop control uses loopback TCP with newline-delimited JSON, not HTTP or MCP JSON-RPC. Send one request per line, match replies by `id`, and check `ok` before dependent actions:

```json
{"id":1,"method":"document.inspect"}
{"id":2,"method":"ui.inspect"}
{"id":3,"method":"engine.commands"}
```

Use `engine.commands` for command IDs, parameter documentation, and enabled or disabled reasons. Execute a command through `engine.execute` with `{command, params}`. With MCP, discover tool schemas and use `list_commands`, `run_command`, or the dedicated tools. Inspect tool errors as well as transport success.

The CLI distinguishes engine commands from control methods. The protocol snapshot's final shorthand omits this distinction; the upstream CLI uses `--method` for control methods:

```sh
deckcraft-cli commands format.
deckcraft-cli describe shape.insert
deckcraft-cli app --port 7990 --method document.inspect
deckcraft-cli app --port 7990 shape.insert '{"preset":"roundRect","rect":[100,100,240,120],"text":"Hello"}'
```

Check the installed CLI usage if it differs. If a mutation times out or loses its reply, inspect the resulting presentation before retrying; repeated insertion can duplicate slides or shapes. MCP `batch` stops at the first error, so inspect partial results before continuing.

## Slides and editable content

Inspect the deck, active slide, layouts, sections, shapes, and selection before targeting edits. MCP provides `inspect_document` and `inspect_slide`; desktop provides `document.inspect`. Use actual returned IDs, and distinguish shape IDs from slide indices. Establish the active slide and selection when a command depends on them.

Prefer structured commands or dedicated MCP tools for precise edits. Discover `slide.new`, `shape.insert`, `shape.connect`, `format.*`, `design.theme`, `table.*`, and `chart.*` as needed. MCP also offers `add_slide`, `go_to_slide`, `add_shape`, `add_text_box`, `set_text`, `insert_picture`, `insert_table`, and `insert_chart`. Inspect each schema before using it. Preserve themes, layouts, placeholders, notes, and editable content when they suit the request; check the replacement scope before setting text.

Geometry is in slide points (1/72 inch); the documented 16:9 slide is 960 × 540. Inspect the actual slide size for custom decks, and confirm rectangle parameter semantics before positioning content. CLI `render --slide N` uses zero-based indices; check other tools' schemas rather than assuming a displayed slide number is their index.

For gestures, select the tool with `ui.tool.select` and send slide-space events through `ui.pointer`. In contrast, `ui.move`, `ui.click`, and `ui.drag` use screen points. Inspect window, canvas, and slide rectangles before screen interaction. Keyboard, text, and IME input act on the current focus and can also drive a slide show; use structured text editing when deterministic targeting matters.

## Presentations and previews

Discover `transition.set` and `animation.set` before adding effects. Use `show.start` and `show.end` for a requested live slide show, inspecting the current show state first. Test timing, builds, navigation, and media playback in the show when those are part of the task; a static render cannot verify them.

Use `ui.render` or MCP `render_slide` to inspect slide artwork. Use `ui.screenshot` or connected MCP `screenshot` for window and dialog state. MCP `call_app` exposes control methods only in connected mode.

For saved decks, render all slides for review:

```sh
deckcraft-cli info presentation.deckcraft
deckcraft-cli render presentation.deckcraft --all --scale 1 previews/
```

View the generated images and check text overflow, clipping, alignment, contrast, image crops, chart labels, and consistency across layouts. Rendering is available headlessly and does not require a visible application window.

## Save, export, and verify

Use desktop `app.open`, `app.save`, and `app.export`, or MCP `open_presentation`, `save_presentation`, and `export`. Discover format-specific parameters instead of guessing schemas. Keep an editable `.deckcraft` or requested `.pptx` deliverable and export PDF, images, or outlines separately as needed.

CLI `run` accepts repeated `--cmd 'ID=JSON'` arguments, then `--save OUT` and/or `--export OUT`. Save between separate CLI invocations; their in-memory edits are not shared. Image conversion through `convert` exports only the first slide; use `render --all` for a complete set of slide previews. PDF export can distinguish slides, notes pages, and handouts through `file.export` parameters; confirm the requested layout and scope.

Verify save/export results and that output files exist and are readable. Reopen or inspect the saved presentation when checking persistence, and review the exported artifact when format fidelity matters, especially after PowerPoint exchange. Return output paths and any material rendering or compatibility issues.
