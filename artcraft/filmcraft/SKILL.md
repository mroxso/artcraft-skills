---
name: filmcraft
description: Edit video projects, timelines, audio, and color or automate imports and exports in the FilmCraft application through its desktop control protocol, MCP bridge, or headless CLI. Use when the user asks to work in FilmCraft.
---

# FilmCraft

Operate FilmCraft through its structured automation interface, using the user's intended project and sequence.

## Protocol reference

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing calls. This is an unmodified upstream snapshot downloaded on 2026-10-08.

Source: [FilmCraft control protocol](https://raw.githubusercontent.com/storytold/filmcraft/refs/heads/main/docs/control-protocol.md). The upstream MIT license is included in [references/LICENSE-MIT](references/LICENSE-MIT).

Search the reference for **Desktop control channel**, **Selection or explicit targets**, **Moving clips**, **Trim mode**, **Replace With Clip**, **Audio mixing**, **Essential Sound**, **Colour**, **Keyboard shortcuts**, and **MCP** as relevant. Relative links resolve against `https://github.com/storytold/filmcraft/blob/main/docs/`. For MCP argument schemas, CLI persistence, and export progress/cancellation, consult [upstream agent documentation, Part 1](https://github.com/storytold/filmcraft/blob/main/docs/agents.md). For save, recovery, relinking, and proxy commands, consult [project-files.md](https://github.com/storytold/filmcraft/blob/main/docs/project-files.md) when needed. If installed behavior differs, inspect the installed command registry and tool schemas rather than inventing parameters.

## Choose the session

Discover available FilmCraft tools and executables, and reuse an appropriate existing session. A user's open project requires the desktop bridge; a headless session is a separate in-process project and cannot edit the live window. For file-based unattended work, use headless MCP or CLI.

Desktop control and bridge examples (adapt executable paths and port):

```sh
filmcraft --control 9876
filmcraft-cli mcp --bridge 127.0.0.1:9876
```

Headless MCP:

```sh
filmcraft-cli mcp --project /absolute/path/project.fcproj
```

Without `--project` or `--demo`, headless MCP starts with an empty project. UI tools require bridge mode. Creating or using this skill does not install FilmCraft or register an MCP server; report the missing executable or connection if unavailable.

The desktop TCP channel is loopback-only and unauthenticated; enable it only while using it. Send UTF-8 JSON objects, one per line, with a string `method`, optional `params`, and distinct request IDs. Read the reply and check `ok`. This is raw TCP, not HTTP. Invalid requests, lines over 4 MiB, or excess connections can close the connection; reconnect after an error before further calls. Do not replay an uncertain mutation merely because the connection closed.

## Inspect and edit

Use MCP `doc_inspect` or `project_inspect` plus `sequence_inspect` to identify project items, the active sequence, tracks, clips, playhead, selection, and effects. In desktop control, discover the inspection commands through `engine.commands`; inspect UI state with `ui.inspect`.

Discover command IDs, parameter documentation, and current enablement through MCP `command_list` or desktop `engine.commands`. Execute with MCP `command_run {id, params}` or desktop `engine.execute {command, params}`. Prefer documented explicit `clips` / `clip` or `items` / `item` targets when they express the task accurately. The command registry reports selection-based enablement: a command shown as disabled may still accept explicit targets, but other preconditions still apply.

Time uses integer ticks: **254,016,000,000 ticks per second**. Use documented `seconds`, `frame`, or `timecode` alternatives when available; never substitute seconds for a tick-valued `time` field. Inspect sequence frame rate before interpreting frame counts. Use actual track IDs or existing names such as `V1` or `A2`; nonexistent tracks are errors.

Before moving clips, inspect linked partners, locked tracks, and destination overlaps. `timeline.move` can overwrite destination material or insert with `insert`; linked partners move by the same offset by default. Use `linked: false` only when moving exactly the named clips is intended. Check the returned `moved` IDs and resulting timing, including audio sync and any shift away from negative sequence time.

For replacement edits, inspect `short` and `sourceInClamped` results: successful replacement may hold the last frame past available media or clamp a retained source In. For dynamic trim operations, provide the documented clock in seconds and finish or cancel the trim gesture before continuing. Read the audio or color sections for mixer automation, ducking, LUTs, or HDR work; preserve unrelated sequence settings.

For dialogs and gestures, inspect `ui.elements` and prefer returned stable element IDs. Use `ui.set` for documented dialog and view fields, and `ui.timeline.locate` / `ui.timeline.hit` for timeline positioning. Refresh inspection after layout changes. `ui.type` targets the focused field. Only `ui.focus` explicitly takes the user's keyboard focus; invoke it when the task needs activation.

## Save, export, and verify

Discover the installed file commands and their parameters before opening, saving, or exporting. Save editable projects as `.fcproj` when appropriate, and honor the requested output path and format. For one-shot CLI edits, persistence requires `--save` with `--project` or `--save-as <path>`; do not report an in-memory edit as a saved project.

Use batches for known command sequences with `stop_on_error: true` unless continuing after failure is intentional. Inspect per-step results and the resulting project after a failed batch before deciding what remains.

For `file.exportMedia`, `wait: true` waits for completion; without it, retain the returned job ID and poll `jobs.list` until completion or failure. Cancel the specific job with `jobs.cancel` when needed. MCP cancellation of a waiting export deletes partial output. Discover installed progress and cancellation support before relying on it. After a timeout or lost reply, inspect project/job state and output before retrying; stop and report the uncertain outcome if a safe retry cannot be established.

Verify resulting sequence state and inspect representative rendered frames or screenshots. MCP `render_frame` / `render_preview` renders headlessly or captures the Program monitor in bridge mode without changing playhead or selection. A desktop screenshot can fail after 10 seconds without a presented frame; distinguish a capture failure from an edit failure. For audio edits, also check playback or an exported audio sample when available. Report saved paths, export completion, and material warnings such as missing media, clamped source ranges, or unfinished jobs.
