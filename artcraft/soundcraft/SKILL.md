---
name: soundcraft
description: Create and edit audio sessions, tracks, clips, mixes, automation, and bounces or automate workflows in the SoundCraft application using its control protocol, MCP bridge, or headless CLI. Use when the user asks to work in SoundCraft.
---

# SoundCraft

Operate SoundCraft through its structured automation interface. Preserve the user's requested session, routing, and audio content.

## Protocol reference

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing calls. This is the downloaded upstream protocol, captured on 2026-11-02.

Source: [SoundCraft control protocol](https://raw.githubusercontent.com/storytold/soundcraft/refs/heads/main/docs/control-protocol.md). The documentation is distributed under the [bundled MIT license](references/LICENSE-MIT). Relative links inside the snapshot (e.g. `cli.md`) resolve against `https://github.com/storytold/soundcraft/blob/main/docs/`. Discover command ids and parameter docs at runtime through `engine.commands` instead of inventing them.

## Select the surface

Every command is reachable from several surfaces; pick by task:

- Desktop control channel: `soundcraft --control <port>` (`0` picks a free port, printed as `SOUNDCRAFT_CONTROL_PORT=…`), driven over loopback TCP.
- CLI against a running app: `soundcraft-cli app --port <port> <method or command id> [JSON]`.
- Headless CLI: `soundcraft-cli run --demo --cmd 'mix.volume={"track":"Kick","db":-6}' --bounce out.wav`.
- MCP: `soundcraft-cli mcp [--demo]` (headless) or `soundcraft-cli mcp --connect <port>` (bridged to the live app).

Discover executables and running sessions first and reuse one when possible; this skill does not install SoundCraft or configure MCP servers. For automated tests, isolate state with `SOUNDCRAFT_CONFIG_DIR` and run UI acceptance with `--no-audio`; never arm a track, enable input monitoring, or start recording in a smoke run.

## Transport

Newline-delimited JSON over TCP on `127.0.0.1`: one request per line, one reply per line, matched by `id`; check `ok`. `engine.execute` (alias `command`) never opens a dialog; empty params use defaults or the current selection. `ui.menu.invoke {path|id}` clicks a real menu item and may open its dialog. Scripted input (`ui.click`, `ui.drag`, `ui.scroll`, `ui.zoom`, `ui.key`, `ui.text`, `ui.move`) uses window points, queues at most 4096 events, and its reply arrives only after a UI pass applied the gesture — inspect state before dependent actions instead of replaying.

## Inspect, edit, and verify

Inspect first: `session.inspect {detail}` for tracks, clips with times, inserts and params, sends, routing, automation, markers, groups, busses, sources, selection, zoom, and transport; `ui.inspect` for panels, dialogs, audio device, and `edit_layout` (timeline and track-row rects for clicking); `engine.commands {filter?}` for the catalog with enablement reasons.

Reference tracks by id or name, clips by id from `session.inspect`, and positions as samples, `{"seconds": 2.5}`, or prefixed time strings (`"bars_beats:5|1|000"`, `"timecode:00:00:10:00"`). Ranges are `start` + `end` (or `length`); omitted means the current edit selection. Prefer structured commands (`track.new`, `mix.volume`, `mix.solo`, `transport.play`, `view.scroll_into_view`) over synthetic input. Panel docking is driven with `ui.dock` (`open`, `close`, `activate`, `float`, `move` with zones) and `ui.dock.reset`; these change layout only, never document contents.

Verify with `ui.screenshot {path?}` (one reply per request; stale or focus-changed captures fail rather than misreport) and by re-reading `session.inspect` after edits. Report bounce/export results and material errors.
