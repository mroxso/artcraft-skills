---
name: pdfcraft
description: Create, edit, combine, split, annotate, fill forms, sign, OCR, and export PDF documents or automate workflows in the PdfCraft application using its desktop control channel, MCP server, or headless CLI. Use when the user asks to work in PdfCraft.
---

# PdfCraft

Operate PdfCraft through its structured automation interfaces. Preserve the user's requested document and editing workflow.

## References

PdfCraft documents automation in two bundled snapshots, captured from upstream on 2026-11-09:

- [references/mcp.md](references/mcp.md) — the MCP server: startup flags, tool surface, and file-access confinement. Source: [PdfCraft MCP conventions](https://raw.githubusercontent.com/storytold/pdfcraft/refs/heads/main/docs/mcp.md).
- [references/cli-batch.md](references/cli-batch.md) — `pdfcraft-cli batch` for convert, OCR, and optimize over files and folders. Source: [PdfCraft batch docs](https://raw.githubusercontent.com/storytold/pdfcraft/refs/heads/main/docs/cli-batch.md).

Both are distributed under the [bundled MIT license](references/LICENSE-MIT). Relative links inside the snapshots resolve against `https://github.com/storytold/pdfcraft/blob/main/docs/`. The desktop control channel is described in the [upstream README](https://github.com/storytold/pdfcraft#readme); discover installed commands and flags rather than borrowing schemas from other ArtCraft applications.

## Select the surface

- **MCP (headless, opt-in):** `pdfcraft-cli mcp [--root DIR] [--compact] [--automation-read-root DIR] [--automation-write-root DIR]` runs over stdin/stdout JSON lines, opens no port, and stops on EOF. It always runs in its own process; it never attaches to the desktop app.
- **Desktop control (live window):** start `pdfcraft --control ~/.pdfcraft-control.json` to let an agent see and operate the real interface — widget tree, clicks, typing, keys, commands, screenshots. Off by default, loopback only, and every connection must present the random token in that file. Keep the control file in a folder only you can write (never `/tmp`); `pdfcraft-cli ui` refuses symlinked or world-readable control files. Drive it with `pdfcraft-cli ui --control <file> inspect|click|key|command|drag|screenshot|resize|focus|quit`.
- **One-off file processing:** `pdfcraft-cli batch` (see the batch reference) and the CLI's other subcommands.

Discover available executables and sessions first and reuse a running session when possible. If the required connection or executable is missing, report the concrete prerequisite; this skill does not install PdfCraft or register MCP servers.

## Tools and discovery

The MCP surface maps document work to five common tools: `command_list {doc?, filter?, enabled_only?}`, `command_run {id, params?}`, `command_batch {steps, stop_on_error?}`, `doc_inspect {doc?}`, and `render_preview {doc?, page?, max_side?}`; existing task tools (`doc_open`, `doc_save`, `page_*`, `form_*`, `sign_*`, `ocr_*`, …) remain available. `pdfcraft://document` and `pdfcraft://commands` resources mirror `doc_inspect` and `command_list`. Discover command ids and mapped tool schemas before running commands; unknown top-level MCP arguments are refused with JSON-RPC `-32602`, and a failed batch reports per-step errors. Inspect the returned `doc` id after `file.open` and pass it to dependent commands.

## File access and output

Read and write roots are separate launch-time capabilities: every file a tool reads must lie inside the read root and every file it writes inside the write root; a root left out grants none of that access. Paths are resolved (links followed) and compared by whole folder names; a refused path is an ordinary, correctable tool error — do not bypass it with ambient filesystem commands. `--root` confines everything and can be combined with the automation roots (both must accept the path). Keychain or certificate-store signing identities and printer jobs are not file access and are not covered.

Exports complete synchronously; there is no background progress or cancellation. Save the requested deliverable (edited PDF in place or to a new path) and verify outputs exist and render: re-open or `doc_inspect` the saved file and `render_preview` the pages that matter, checking text, annotations, form fields, and page order. For batches, read the JSON report and surface skipped files and per-file errors.
