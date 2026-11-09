---
name: gridcraft
description: Create and edit spreadsheets, cells, formulas, charts, tables, and pivots or automate workflows in the GridCraft application using its control protocol, MCP bridge, or headless CLI. Use when the user asks to work in GridCraft.
---

# GridCraft

Operate GridCraft through its structured automation interface. Preserve the user's requested workbook, formulas, and editable content.

## Protocol reference

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing calls. This is the downloaded upstream protocol, captured on 2026-11-09.

Source: [GridCraft control protocol](https://raw.githubusercontent.com/storytold/gridcraft/refs/heads/main/docs/control-protocol.md). The documentation is distributed under the [bundled MIT license](references/LICENSE-MIT). Relative links inside the snapshot (e.g. `mcp.md`, `cli.md`) resolve against `https://github.com/storytold/gridcraft/blob/main/docs/`. Discover installed command parameters through `engine.commands` rather than inventing them.

## Select the session and authenticate

Start the desktop app with a control port: `gridcraft --control 7979` (or `GRIDCRAFT_CONTROL_PORT=7979`). The port always requires a token; there is no way to turn this off. The app writes its token to `$XDG_RUNTIME_DIR/gridcraft/control-<port>.token` (else `~/.cache/gridcraft/…`; Windows `%USERPROFILE%\.gridcraft\…`), or you can pin one with `GRIDCRAFT_CONTROL_TOKEN` (preferred over the visible `--control-token`). The first line of every connection must be `{"id":0,"method":"auth","params":{"token":"…"}}`; anything else closes the connection. `gridcraft-cli send` and `gridcraft-cli mcp --connect` handle auth themselves.

For headless work with no window, use `gridcraft-cli mcp` or `gridcraft-cli run`; that session is separate from the user's live app. Discover executables and running sessions first and reuse one when possible; this skill does not install GridCraft or configure MCP servers.

## Transport

After auth, send newline-delimited JSON to `127.0.0.1:<port>`; one request line, one reply line, matched by `id`, check `ok`. A line that is not a JSON object with a string `method` (over 64 MiB, non-UTF-8, an HTTP request) gets one error reply and closes the connection. Any method name that is a command id (e.g. `home.bold`) runs that command directly.

## Inspect, edit, and verify

Inspect before editing: `document.inspect` (sheets, used ranges, tables, charts, names, selection, undo labels), `sheet.read {range?, sheet?, formulas?, formatted?}`, `cell.get {cell?}`, `ui.inspect` (ribbon tab, editor state, open dialog, selected object, grid rect, windows), and `engine.commands {search?}` for command ids, parameter docs, and enablement. `engine.journal` lists replayable commands (passwords omitted).

Edit through `engine.execute {command, params}` with optional `window` (window id) or `doc` (workbook id) to target a specific window; the active window stays in front. Use real cell references and ranges (`cell.set` with `input: "=SUM(A1:A9)"`, `selection.set`, `edit.goTo`). Prefer structured commands over synthetic input; `ui.click`, `ui.cell.click`, `ui.key`, and the `ui.edit.*` methods drive the grid when interaction is intended, under a shared synthetic-input budget. Dialogs are opened, filled, and confirmed with `ui.dialog`, `ui.dialog.set`, `ui.dialog.confirm`, `ui.dialog.cancel`; a Goal Seek dialog is driven with its own `data.goalSeek` command after reading and cancelling.

Multiple windows per workbook are normal: `window.list` shows `{window, doc, index, title, dirty, active, hidden}`; `window.activate`, `window.close {force?}`, and `file.close` manage them. Floating objects (chart, image, shape, equation, slicer) are selected with `ui.object.select` and arranged with `object.*` and `arrange.*` commands.

Verify with `ui.screenshot` (settles animations first; bounded budgets — prefer a `path` for large captures) and by re-reading `sheet.read`/`cell.get` after edits.

## Files, printing, and settings

`app.open {path, password?}` / `app.save {path?}` handle files; a password-protected workbook needs the `password` parameter and never prompts, and opens without a save path so Save asks where to write. Native printing: `ui.printSettings` inspects and configures printers (`refresh` starts discovery; set `printer`, `copies`, `duplex`, `grayscale`), and `ui.printSubmit` spools the print-ready PDF without a dialog; poll until `busy` is false and check `status`. PDF export is separate. Use `view.theme {mode}` for light/dark/system, `view.animations {on}` to steady motion before captures, and `app.language.set {language}` for interface language. Report saved paths and any material warnings.
