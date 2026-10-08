---
name: photocraft
description: Edit images, layers, selections, and text or automate workflows in the PhotoCraft application using its control protocol, MCP bridge, or headless CLI. Use when the user asks to work in PhotoCraft.
---

# PhotoCraft

Operate PhotoCraft through its structured automation interface. Preserve the user's requested editing workflow and target document.

## Protocol reference

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing calls. This is the downloaded upstream protocol, captured on 2026-10-08.

Source: [PhotoCraft control protocol](https://raw.githubusercontent.com/storytold/photocraft/refs/heads/main/docs/control-protocol.md).

Useful sections: **Methods**, **Engine commands**, **Background jobs**, **MCP bridge**, **Headless server**, **Transport limits**, **Preferences**, **Snapping**, and **Camera Raw dialog**. Relative links inside the downloaded document refer to upstream documentation; resolve those against `https://github.com/storytold/photocraft/blob/main/docs/` when needed. If installed behavior differs, inspect the installed command registry and consult the source rather than inventing parameters.

## Select the session

- For a user's open document or visible application, use an existing PhotoCraft MCP bridge or authenticated desktop control session. A headless session has separate documents and cannot edit the user's live window.
- For unattended processing of files, use headless MCP (`photocraft-cli mcp`) or the persistent JSON-lines server (`photocraft-cli serve`).
- Discover available PhotoCraft tools and installed executables first. If the required connection or executable is missing, report the concrete prerequisite; creating this skill does not install PhotoCraft or register an MCP server.

When launching a needed desktop session, adapt this example to the actual executable, available port, private token file, and task directories:

```sh
photocraft --control 7878 --control-token-file /private/path/photocraft-control.token \
  --automation-read-root /work/input --automation-write-root /work/output
```

Bridge that session with:

```sh
photocraft-cli mcp --bridge 127.0.0.1:7878 \
  --control-token-file /private/path/photocraft-control.token
```

Reuse a running session when possible. Keep TCP on loopback and credentials in a private token file; do not print, commit, or expose tokens in command arguments. Raw TCP requires an `auth` request first on every connection, then one JSON object per line with a unique `id`; match replies by ID and check `ok`. Stdio `serve` does not need the TCP authentication handshake.

## Inspect, edit, and verify

Inspect the active document, selected layers, selection, channel/mask target, and pending dialogs before editing. Discover command IDs, parameter documentation, and enablement through `engine.commands` or MCP `command_list`; use `ui.menu.list` for the menu tree.

Use `engine.execute {command, params}` or MCP `command_run {id, params}` for explicit edits. Command params must be an object, omitted, or null. Direct execution uses defaults without opening a dialog. Use `ui.menu.invoke` when dialog interaction is intended, then inspect and change its fields before confirming.

For UI gestures, `ui.pointer` uses **document coordinates**, not screen coordinates. Inspect the active tool and snapping options first. `ui.type` goes to the focused widget or active Type editing session. A pixel gesture on a type, shape, Smart Object, or fill layer can open a rasterization prompt; confirm only when rasterization fits the intended edit.

Prefer editable layers, adjustments, and masks when they suit the user's requested result. Inspect the resulting document and render a preview or capture a screenshot to check the visual outcome. Report successful saves and material import/export warnings.

## File access and output

Read and write roots are separate launch-time capabilities. Use task-scoped roots and forward-slash relative paths within them; the output parent directory must exist. Do not bypass rejected paths by switching to ambient filesystem commands.

- Desktop control: `app.open` / `app.save`.
- MCP: `doc_open` / `doc_save` / `doc_export` (bridge maps these to desktop methods).
- Headless JSON-lines: `doc.open` / `doc.save` / `doc.render`.

Automation refuses `file.open`, `file.save`, `file.saveAs`, `file.saveACopy`, and other commands using ambient paths. Save native editable output as `.pcraft` when appropriate; use the requested export extension. Saving without a path writes back only to an existing PSD, PSB, or `.pcraft` source. Use an explicit output path when creating a copy or exporting another format.

## Jobs, batches, and uncertain outcomes

Long commands wait by default. With `wait: false`, retain the returned job ID and check `jobs.list` / MCP `jobs_list` until done, failed, or cancelled before dependent edits or final verification. Cancel a specific job when needed; edits to its locked document fail while it runs.

Use batches for known sequences, with stop-on-error enabled unless continuing is intentional. Batches are not transactions: earlier edits persist on failure. Inspect per-step results; `actions.play` may report a failed step despite an overall successful reply.

After a timeout, disconnect, or reply-budget error, inspect document/history/job state before retrying a mutation. An operation may already have completed. Stop and report unresolved state if inspection cannot determine whether replay is safe.

Read **Transport limits** for large batches or previews: batches allow at most 256 steps, and headless previews have a 2048-pixel edge limit even for full-size requests. In bridge mode previews capture the app window; headless previews render the document. `doc_select` and `doc_close` are headless-only; `ui_*` tools and `control_call` are bridge-only.

For preferences and Camera Raw, read their protocol sections before editing. Change only settings relevant to the task. Camera Raw analysis can use a bounded proxy; preserve reserved `__cameraRawPsd` metadata when editing imported filter parameters, and verify whether detail refinement finished before assessing full-resolution results.
