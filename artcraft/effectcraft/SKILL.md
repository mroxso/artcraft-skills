---
name: effectcraft
description: Create and edit compositions, layers, animation, masks, and visual effects in the EffectCraft application through desktop control, MCP, or headless CLI. Use when the user asks to work in EffectCraft.
---

# EffectCraft

Operate EffectCraft through its structured automation interfaces, using the user's intended project and session.

## References

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing desktop calls. This is an unmodified snapshot downloaded on 2026-10-08 from the [upstream control protocol](https://raw.githubusercontent.com/storytold/effectcraft/refs/heads/main/docs/control-protocol.md). The upstream MIT license is included in [references/LICENSE-MIT](references/LICENSE-MIT).

Search the reference for `Engine`, `UI state`, `Input`, `Locating things`, or `Screenshots`. Relative documentation links resolve against `https://github.com/storytold/effectcraft/blob/main/docs/`.

For MCP tool schemas, CLI syntax, scripting, tracking, rotoscoping, and export workflows, consult the [upstream agent guide](https://github.com/storytold/effectcraft/blob/main/docs/agents.md) when needed. Discover schemas from the installed application if behavior differs; do not reuse parameters from other ArtCraft applications or assume complete After Effects compatibility.

## Choose the session

Discover available EffectCraft tools, installed executables, and existing sessions. Prefer an available MCP connection targeting the intended session.

- For a running desktop project, use its control channel or `effectcraft-cli mcp --bridge 9877`. A needed desktop session can be started with `effectcraft --control 9877` or `EFFECTCRAFT_CONTROL_PORT=9877`; adapt executable paths and port to the environment.
- For independent work, `effectcraft-cli mcp --project /absolute/path/project.ecproj` opens a headless session; `effectcraft-cli mcp` starts without content, while `--demo` loads demonstration content. Headless rendering defaults to CPU; `--gpu` requests a separate GPU compositor and fails if no adapter is usable.
- One-shot CLI invocations use separate headless engines and default to the demo project. Supply the intended project or `--empty`, and use `--save` or `--save-as` to persist edits. A CLI call supports `--bridge 9877` when it should act on the live app instead.

Reuse an appropriate session. Do not open a separate headless project expecting edits to appear in the desktop app. Report a missing executable or connection when unavailable; this skill does not install EffectCraft or configure MCP servers.

## Discover commands and transport

The desktop channel is raw TCP on `127.0.0.1`, not HTTP or MCP JSON-RPC. Send UTF-8 JSON objects with a string `method`, optional `params`, and distinct request IDs, one per newline. Read one reply per request, match IDs, and check `ok` before dependent actions:

```json
{"id":1,"method":"ui.inspect","params":{}}
{"id":2,"method":"engine.execute","params":{"command":"project.summary"}}
{"id":3,"method":"engine.execute","params":{"command":"command.describe","params":{"command":"comp.new"}}}
```

Connections are persistent and replies are ordered. Requests run between UI frames with a 60-second timeout. Invalid request lines, invalid UTF-8, or lines over 4 MiB close the connection; at most 16 connections are served. The port has no authentication, so enable it only while needed. After a timeout or lost mutation reply, inspect state before replaying; stop and report uncertainty if the result cannot be established safely.

Use `engine.commands`, or engine commands `command.list` and `command.describe`, for IDs, schemas, enablement, and disabled reasons. Execute edits with `engine.execute {command, params}`. It runs engine commands without opening dialogs; `ui.menu.invoke {id, params}` behaves like a menu click and may open a dialog when params are empty.

MCP uses `list_commands`, `describe_command`, and `execute_command {command, params}`, plus helper tools such as `get_comp`, `get_layer`, and `set_property`. Use the actual connected tool schemas; MCP helpers and desktop methods have different names and parameter casing. For CLI discovery, use `effectcraft-cli commands` or `effectcraft-cli exec --list --schemas --json`.

## Inspect and edit compositions

Inspect project items, active comp, selection, time, dirty state, and background jobs before editing. Desktop queries include `project.summary`, `comp.info`, `editor.state`, `app.capabilities`, and `jobs.list` through `engine.execute`; MCP exposes `get_state`, `get_project`, and `get_comp`.

Obtain actual comp and layer IDs from queries. Layers can also be addressed by name or `#n` (1-based from the top), but indices can change after reordering. Pass an explicit comp where supported, and set selection deliberately for commands acting on selected objects. Do not unlock or edit locked layers incidentally.

Read property trees with `layer.tree` / MCP `get_layer` and use returned paths or UIDs. Read values with `prop.get` / `get_property`; discover effect IDs and parameters before applying them. Returned effect and shape paths identify the newly created instances, avoiding accidental edits to another effect of the same type.

MCP `set_property` without `time` sets a static value; with `time` it creates a keyframe; with `expression` it sets an expression. Times are seconds. Keyframe times use layer time, which differs from comp time for offset or stretched layers. Inspect interpolation and values at relevant times. Expression replies distinguish `value` from `evaluated` and report `expressionError`; a syntax error can leave the expression stored but disabled.

For related multi-step edits, consider MCP `batch` or `engine.batch` after reading its schema: steps can reference prior results with `$N.key`, and failed batches roll back. For procedural construction, `run_script` supports the application's After Effects-style object model. Inspect script errors and any `waiting` result; ScriptUI dialogs require interaction before a script finishes. Preserve the application's scripting file/network restrictions.

Opening, replacing, reverting, or closing a project through engine/MCP commands does not ask to save. Inspect dirty state and save the user's work before such a transition when needed. Do not use `app.quit {force: true}` to bypass unsaved work.

## Operate the UI when needed

Use `ui.inspect` and `ui.elements {prefix?}` to discover drawn widgets and stable IDs. Refresh elements after layout changes. Coordinates and widget rectangles are logical window points; `ui.viewer.locate` converts comp pixels to window points, and `ui.timeline.locate` locates a layer at a time. Prefer discovered IDs over guessed coordinates. `ui.type` acts on the focused field.

Use `ui.set` for documented viewer/timeline state or `ui.panel.show` to expose the needed panel. Avoid stealing focus with `ui.focus` unless interaction requires it. UI gestures reply after synthetic input is processed; inspect their result before dependent edits.

## Save, render, and verify

Save the editable `.ecproj` separately from exported media. MCP provides `save_project {path?}`; discover the corresponding engine save command and CLI flags for the chosen interface. Verify the save result and resulting file, and check dirty state where available.

Use `render.frame` (desktop) or `render_frame` (MCP) to inspect frames at representative times, including animation boundaries and transitions. Desktop frames are independent of viewer zoom/resolution; `max_side: 0` gives full size. MCP `transparent: true` preserves alpha for inspection. Use `ui.screenshot` for panel or UI evidence. A frame preview is not a finished video export.

Discover render queue/export schemas and supported formats with command discovery and capabilities. Set the intended comp, output path, time range, dimensions, and alpha requirements explicitly. Wait for `renderQueue.render {wait: true}` where supported, or poll the relevant job/status until completion; likewise inspect status for tracking or roto jobs before saving or applying results. Check background footage validation after opening a project and report missing media affecting the result.

Verify exported files exist, are readable, and match the requested format and duration; inspect representative frames and alpha when relevant. Review warnings for Lottie or timeline interchange rather than treating an existing file as proof of fidelity. Report actual saved/exported paths and any unfinished jobs, missing media, or unsupported features.
