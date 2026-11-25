# AniCraft for AI assistants (MCP)

`anicraft-cli mcp` is a [Model Context Protocol](https://modelcontextprotocol.io) server. Any
MCP client (an AI assistant, an editor, a script) can then open a document, draw, animate,
look at frames and export through the same commands the app uses.

```sh
ROOTS="--automation-read-root /work/project --automation-write-root /work/project/renders"
anicraft-cli mcp $ROOTS                   # a new, empty document
anicraft-cli mcp scene.anicraft $ROOTS    # open a document
anicraft-cli mcp --sample $ROOTS          # the sample animation
anicraft-cli mcp --bridge 9878 $ROOTS     # the AniCraft window you have open (below)
```

## The two folders an assistant may use

`mcp` does not start without both of these (it prints why and exits with code 2):

| Flag | The assistant's commands may |
|---|---|
| `--automation-read-root <folder>` | read files inside this folder: open, import, saved commands, presets, swatches, data tables, plug-ins. Give it again for more folders. |
| `--automation-write-root <folder>` | create, replace and delete files inside this folder: save, export, publish, templates. Given once. |

They may be the same folder. Each must exist when the server starts. Use absolute paths in a
client's configuration: a relative one starts at the folder the client launches the server in.

* Reading and writing are separate. The write root can't be read from and the read roots can't
  be written to, unless you give a folder as both. (A command may still ask whether a file in
  the write root exists, so replacing one asks for `"confirm": true` as always.)
* A path is checked as the file it really names: made absolute, `..` removed, symbolic links
  and Windows junctions followed, and on Windows letter case ignored. A link inside a root to a
  file outside it is outside. A root itself counts as inside.
* The check covers every file a command touches, not only the path it is given: a plain
  `file.save` of a document opened from elsewhere, Publish's outputs, the steps of a saved
  command, a video a document links to.
* A refused command comes back as a tool error that names the root, before any file is touched:
  `file.export_png: param 'path': C:\Users\me\a.png is outside the folder automation may write
  to: the automation write root is C:\work\project\renders`.
* The document and `--plugins` folder on the command line are your own choice and open as
  before; the roots apply to what the assistant asks for after that.
* Temporary files AniCraft makes for itself (the soundtrack it hands to ffmpeg) are not affected.

`serve` takes the same two flags, optionally: with them it is limited in the same way. The app
and the other subcommands (`exec`, `run`, `render`, …), which you run yourself, are not limited.
The design is ADR 0124.

## Headless or live

Without `--bridge` the server edits a document of its own, with no window: good for pipelines and
batch work. Save it (`file.save`) to keep the result.

With `--bridge <port>` the same tools act on the AniCraft window you have open, started with
`anicraft --control <port>`: every edit appears there at once, and Ctrl+Z undoes it
(`docs/control-protocol.md`, ADR 0104). The server starts even when AniCraft isn't open (an
assistant starts its servers when it starts) and connects on the first tool call; until AniCraft is
open with remote control, the tools answer with how to start it. Close and reopen AniCraft whenever
you like: the next call reconnects, with no need to restart the assistant. It finds the run's token
in `control.json` in AniCraft's settings folder, so there is nothing to copy.

The two roots apply live too: the bridge sends them with each call and the window keeps that
call's commands inside them, while your own work in the window is not limited. The window must
be an AniCraft that applies roots (control protocol 2); the bridge refuses to send commands to an
older one, which would ignore them.

The server talks MCP's stdio transport: JSON-RPC 2.0, one message per line on stdin and stdout.
It speaks protocol revisions 2025-06-18, 2025-03-26 and 2024-11-05.

## Connecting a client

Most clients take a server entry like this one (use the full path to `anicraft-cli`):

```json
{
  "mcpServers": {
    "anicraft": {
      "command": "/path/to/anicraft-cli",
      "args": ["mcp", "/path/to/project/scene.anicraft",
               "--automation-read-root", "/path/to/project",
               "--automation-write-root", "/path/to/project"]
    }
  }
}
```

For live editing, start AniCraft with `--control 9878` (a desktop shortcut is handy) and use:

```json
{
  "mcpServers": {
    "anicraft": {
      "command": "C:\\path\\to\\anicraft-cli.exe",
      "args": ["mcp", "--bridge", "9878",
               "--automation-read-root", "C:\\path\\to\\project",
               "--automation-write-root", "C:\\path\\to\\project"]
    }
  }
}
```

## Tools

| Tool | What it does |
|---|---|
| `anicraft_commands` | Lists the commands (id, label, menu, shortcut, params), optionally filtered by words such as `tween` or `export`. |
| `anicraft_run` | Runs one command with its params. |
| `anicraft_run_script` | Runs several commands in order; stops at the first error and says which step failed. |
| `anicraft_document` | Describes the document: stage, scenes, layers and keyframes, library, and the current scene, frame, layer and selection. |
| `anicraft_render` | Returns a frame of the current scene as a PNG picture, exactly as exported. |

The assistant sees one tool per job, not one per command: the command list is long and grows
with every release, and `anicraft_commands` lets it find what it needs. Frames in params are
0-based, as everywhere in the engine (the CLI's own `--frame` flags are 1-based, as in the
timeline).

Saved commands (ADR 0097) run through `anicraft_run` too: `macro.run` with `{"path": …}` (a
saved command's file) or `{"steps": [{"cmd", "params"}]}` runs the steps as one undo step, and
unlike `anicraft_run_script` a failing step leaves the document as it was. `macro.history` and
`macro.save` turn the session's undo steps into a saved command.

## A frame with artwork left out

A document can hold more than AniCraft draws in one frame (symbols nested many times over, as
in a damaged file): the frame is then drawn in part
([ADR 0128](adr/0128-one-work-allowance-and-frames-that-say-what-they-left-out.md)). The commands
that write frames still write it, and their result has `"left_out": true` and a `"warning"`;
`anicraft_render` says so in the picture's caption, and the document's state has the two keys
for the frame shown. A result without them is a whole frame.

## Safety

* Everything runs through the engine's commands, so params are checked and every edit can be
  undone with `edit.undo`.
* Commands that would lose unsaved work or replace a file refuse until their params include
  `"confirm": true` (ADR 0004). The server's instructions ask the assistant to check with you
  before confirming.
* Commands read files only inside the automation read roots and write only inside the automation
  write root (above). Inside them the assistant has your permissions: it can read any file below
  a read root and create or replace files anywhere below the write root, so give it a project
  folder, not your home folder. The roots limit AniCraft's commands, not the assistant's other
  tools. A program running as you that swaps a folder for a link at the right moment could still
  redirect one operation, and hard links can't be told from files (ADR 0124).
* An assistant can't choose the program that makes or reads video: over `mcp` and `serve`, every
  command refuses an `ffmpeg` param (Export Video, Import Video and the rest). Set `ANICRAFT_FFMPEG` yourself, or have ffmpeg on the PATH. (`exec`
  and `run`, which you type, keep the param.)
* A failing command comes back as a tool result marked as an error, so the assistant can read
  the message and try again; it never stops the server.
* Live (`--bridge`): an edit whose answer was lost (AniCraft closed mid-call) is never sent again,
  since it may have been made; the assistant is told to check with `anicraft_document`. While you
  are dragging, the assistant's edits wait until you let go, so the two stay separate undo steps.
