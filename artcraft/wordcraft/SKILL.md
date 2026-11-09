---
name: wordcraft
description: Create and edit documents, text, styles, tables, comments, and print jobs or automate workflows in the WordCraft application using its control protocol, MCP bridge, or headless CLI. Use when the user asks to work in WordCraft.
---

# WordCraft

Operate WordCraft through its structured automation interface. Preserve the user's requested document, styles, and editable content.

## Protocol reference

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing calls. This is the downloaded upstream protocol, captured on 2026-11-09.

Source: [WordCraft control protocol](https://raw.githubusercontent.com/storytold/wordcraft/refs/heads/main/docs/control-protocol.md). The documentation is distributed under the [bundled MIT license](references/LICENSE-MIT). Relative links inside the snapshot (e.g. `mcp.md`, `recovery.md`) resolve against `https://github.com/storytold/wordcraft/blob/main/docs/`. Discover command ids and parameter docs through `engine.commands` instead of inventing them.

## Select the session and authenticate

Start the app with a control port: `wordcraft --control 7981` (or `WORDCRAFT_CONTROL_PORT=7981`); it listens on `127.0.0.1` only. Every request needs the window's key: a random hex value the app writes to `<settings>/control-key.local-<port>` (macOS `~/Library/Application Support/WordCraft`, Linux `$XDG_CONFIG_HOME/wordcraft`, Windows `%APPDATA%\WordCraft`; `WORDCRAFT_PROFILE_DIR` isolates the profile). Send it as top-level `"key"` on every request, or once per connection with `{"method": "auth", "key": "…"}`. A missing or wrong key answers `unauthorized` and closes the connection; an unauthenticated connection is dropped after 30 s. `wordcraft-cli mcp --connect` reads the key itself (or `WORDCRAFT_CONTROL_KEY`) and only sends it to `127.0.0.1`; to drive a remote app, forward the port and set the key explicitly. Discover executables and running sessions first; this skill does not install WordCraft or configure MCP servers.

## Transport

Send one JSON object per line; each gets one reply line, matched by `id`; check `ok`. A failed command leaves the document unchanged. A non-JSON line gets one error reply and closes the connection; lines over 1 MiB are refused the same way. Any method name that is a command id works directly (`{"method": "format.bold"}`).

## Documents and targeting

Several documents can be open, each with a stable id. `ui.inspect` reports `document` and `documents` (`id`, `title`, `path`, `dirty`, `active`). `file.new` and `file.open` open a document in its own window and make it active (`file.open` on an already-open file returns `alreadyOpen: true`); `view.switchWindows {id}` activates one; `file.closeDocument {id?, force?}` closes one. `engine.execute`, `document.inspect`, and `ui.render` take `doc` to work on a background document without changing the active window; window and input methods act on the active window only. `file.close` never shows a Save prompt: with unsaved changes it errors — save first or pass `{"force": true}` deliberately.

## Inspect, edit, and verify

Inspect before editing: `document.inspect {text?, doc?}` for blocks, styles, runs, lists, tables, parts, sections, selection, and pages; `engine.commands` for the catalog with enablement. Edit through `engine.execute {command, params}` — `text.insert`, `format.*`, `para.*`, `styles.modify`, table and comment commands. Positions are `{"story": "body" | {"part": n}, "path": [block, row, cell, …], "off": byteOffset}`; `CharProps`/`ParaProps` shapes are documented in upstream `mcp.md`. UI commands such as `ui.dialog`, `ui.backstage`, `ui.theme`, `ui.language`, and `ui.fileBrowser` drive chrome; dialogs and protection still apply to input.

Input methods (`ui.click`, `ui.clickText` with 0-based page and page-point coordinates, `ui.press`/`ui.release`, `ui.wheel`, `ui.key`, `ui.text`) go to the active window's focused widget and reply `{"queued": true}` when queued, not when applied — inspect the resulting state before dependent edits and never replay an edit just because its effect was not immediate.

Verify with `ui.render {page?, scale?, doc?}` (engine-rendered page PNG, no window needed) or `ui.screenshot` (window state, dialogs, balloons). Report saved and exported paths and material warnings.

## Printing and export

Native printing: `ui.printSettings` inspects and configures the printer (`refresh` starts discovery; set `printer`, `copies`, `duplex`, `grayscale`), and `ui.printSubmit` submits the print-ready PDF without a dialog, accepting `range`, `pages`, `parity`, `copies`, `collate`, and `paper` (Scale to Paper Size; the document's page size is unchanged). Poll `ui.printSettings` until `busy` is false and check `status`/`detail`. `file.printPdf` exports PDF; invalid ranges submit no job.
