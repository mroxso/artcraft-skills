---
name: solidcraft
description: Create and edit parametric 3D CAD designs, sketches, features, parameters, assemblies, and drawings or automate workflows in the SolidCraft application using its control protocol, MCP bridge, or headless CLI. Use when the user asks to work in SolidCraft.
---

# SolidCraft

Operate SolidCraft (an open-source parametric CAD app in Rust: desktop, web, headless CLI, MCP) through its structured automation interface. Preserve the user's requested modelling workflow and target design.

## Protocol reference

Read the relevant sections of [references/control-protocol.md](references/control-protocol.md) before constructing calls, and [references/mcp.md](references/mcp.md) for the MCP tool surface. These are downloaded upstream docs, captured from upstream `main` on 2026-11-28 for SolidCraft 0.51.x (`render-jobs.md` and `scripts.md` were re-checked the same day and are unchanged since 2026-11-11); upstream lives at [github.com/tangency-labs/solidcraft](https://github.com/tangency-labs/solidcraft) (`docs/`). Relative links inside them (e.g. `render-jobs.md`, `scripts.md`) resolve against `https://github.com/tangency-labs/solidcraft/blob/main/docs/`; `render-jobs.md` and `scripts.md` are also in `references/`. The protocol lists methods, not individual modelling commands: discover those at runtime instead of inventing command IDs or parameters.

## Locate the executables

`solidcraft` and `solidcraft-cli` are usually **not** on `PATH` even when the app is installed. Discover them, never guess a path:

1. **PATH:** `command -v solidcraft solidcraft-cli` (POSIX) or `where solidcraft solidcraft-cli` (Windows).
2. **macOS:** `mdfind -name SolidCraft.app`; the binaries are `/Applications/SolidCraft.app/Contents/MacOS/SolidCraft` and `.../solidcraft-cli` (both ship in the same bundle).
3. **Linux:** the AppImage, `/snap/bin/solidcraft`, or the shortcut's target.
4. **Nothing to install to drive it.** The control port is plain line-delimited JSON over loopback TCP; `scripts/sc.py` is a small dependency-free wrapper, and any language that opens a socket works. `solidcraft-cli` is only needed for the MCP bridge and headless runs.

## Start and select a session

- **Watchable session (default choice):** start the desktop app with a control port, then drive that live window so the user sees the model appear.

  ```sh
  SOLIDCRAFT_CONTROL_PORT=7878 /Applications/SolidCraft.app/Contents/MacOS/SolidCraft >/tmp/solidcraft.log 2>&1 &
  ```

  A plain launch keeps the control channel **off** by default; `--control PORT` or `SOLIDCRAFT_CONTROL_PORT` opens it for that run, or turn it on under Preferences › Assistant › Agents through MCP › "Let AI agents connect" (takes effect at once).

- **Bridged MCP** for an MCP-capable client: `solidcraft-cli mcp --connect 127.0.0.1:7878` (add `--compact` or `SOLIDCRAFT_MCP_COMPACT=1` for byte-lean summaries when the design is large) (tools: `execute`, `batch`, `inspect_design`, `measure`, `body_topology`, `set_parameter`, `check_parameters`, `screenshot`, `compare_picture`, `export`, `open`, `save`, `new_design`, `undo`, `redo`, `list_commands`, `describe_command`, `pending`, `running`, `cancel`, `crash_reports`, `skill_reference`).
- **Headless** (`solidcraft-cli mcp --headless`, or `solidcraft-cli run script.json`) has its own in-process design and cannot touch the user's open window. Plain `solidcraft-cli mcp` with no flag finds the running app first and is headless only when none runs (then it upgrades to the app on the next call while no design work has happened). Use headless for unattended file processing; note `view.pick` needs a connection to the app and is unavailable headless. Add `--structured` for programmatic clients (every tool result also carries `structuredContent`), and `--render-gpu` when headless GPU render jobs are needed.
- **Streamable HTTP** (`solidcraft-cli mcp --http 127.0.0.1:8765 --http-info-file ~/.cache/solidcraft-mcp.json --in assembly.sc`) serves the MCP HTTP transport on `/mcp` so several local clients share one warm headless session in RAM; loopback addresses only, bearer-token authenticated (generated tokens go to the info file, never to stderr), requests dispatched serially. Wrap multi-step edits in one atomic `batch` so clients cannot interleave.

Reuse a running instance when one exists (`pgrep -lf SolidCraft`) and keep the channel on loopback. Beyond the tools, the MCP server exposes read-only resources (`solidcraft://design`, `solidcraft://commands`, `solidcraft://body/{name}`, `solidcraft://sketch/{name}`, `solidcraft://feature/{id}`, `solidcraft://command/{id}`, `solidcraft://skill/{skill}/{file}`), resource subscriptions, workflow prompts (`model-part`, `edit-design`, `check-parameters`, `diagnose-feature`, `assembly-clearance`) and argument completions.

**Authentication:** each launch mints a random token and writes it, hex, to a `0600` file the app removes on exit — macOS `~/Library/Application Support/SolidCraft/control/PORT.token`, Linux `$XDG_DATA_HOME/solidcraft/control/PORT.token`, Windows `%LOCALAPPDATA%\SolidCraft\control\PORT.token`. Send it as a top-level `"token"` on the first request of a connection; later requests may omit it. A wrong or missing token answers `unauthorized` and closes. Set `SOLIDCRAFT_CONTROL_TOKEN` (≥32 hex chars) to pin one; prefer the variable over `--token`, which other users can see in the process list.

## Discover commands before using them

`engine.commands` (or `solidcraft-cli commands`, or MCP `list_commands`) gives every command's id, label, tab, panel, shortcut, parameter docs and whether it is enabled right now; `describe_command` / `engine.describe {command}` gives one command's parameter doc and JSON Schemas when it has a typed contract. The command families:

- **`sketch.*`** — `create`, `line`, `circle.center`, `rectangle.two_point`, `arc.three_point`, `spline.fit_point`, `slot.center_point`, `polygon.*`, `text`, `point`, `construction`, `dimension`, `constraint.concentric` (and the other `constraint.*` relations), `trim`, `fillet`, `chamfer.*`, `mirror`, `pattern.rectangular`, `pattern.circular`, `solve`, `inspect`, `finish`.
- **`solid.*`** — features `extrude`, `revolve`, `sweep`, `loft`, `fillet`, `chamfer`, `shell`, `draft`, `hole`, `thread`, `coil`, `rib`, `web`, `press_pull`, `pipe`, `emboss`, `boundary_fill`, `offset_face`, `replace_face`, `split_body`, `split_face`, `combine`, `remove`, `move`, `scale`, `mirror`, `align`; patterns `pattern.rectangular`, `pattern.circular`, `pattern.path`; direct primitives `box`, `cylinder`, `sphere`, `torus`, `bounding_solid` (each takes an `operation` of `new`/`cut`/`join`).
- **`face.*`**, **`body.*`**, **`sheet.*`** (flange, hem, fold, unfold, flat pattern, `convert`), **`assembly.*`** / **`joint.*`** / **`contact.*`** / **`motion.*`** / **`explode.*`**, **`parameters.*`**, **`config.*`**, **`timeline.*`**, **`construct.*`** (planes, axes), **`surface.*`**, **`mesh.*`**, **`material.*`** / **`appearance.*`**, **`document.*`** / **`doc.*`** / **`file.*`**, **`view.*`**, **`browser.*`**, **`select.*`** / **`selection.*`**, **`inspect.*`** (`measure`, `section`, `interference`, `clearance`, `draft`, `curvature_map`, `center_of_mass`, `minimum_radius`), **`render.*`**, **`edit.*`** (`undo`, `redo`, `checkpoint`, `restore_checkpoint`), **`diagnostics.*`**.

## Inspect, edit, and verify

Inspect first: `document.inspect` for parameters, timeline (errors, warnings, timings), bodies, sketches, selection and undo depth; `ui.inspect` for the camera, active tool or dialog, status line, hover, and a pending file picker (`file_picker_busy`). The app may already hold a design you did not create.

Edit with `engine.execute {command, params}` (one command, never opens a dialog) or `engine.batch {commands, rollback}` — a batch runs in one frame, stops at the first failure, and restores an engine checkpoint, reporting `failed.index`/`failed.command`/`failed.error`. MCP's `batch` tool also takes `dry_run: true`: every step runs and is checked (`measure`, `expect`) against the simulated result, then everything is restored with zero undo entries left — refuse it for steps that write to disk or talk outside the design. Batch refuses any step that loads a file (`doc.open`, `file.insert_step`, `file.insert_mesh`) and any step while the agent cursor is shown: send those one at a time.

Verify numerically, not by eye alone: `engine.execute inspect.measure {bodies?}` (volume mm³, area mm², centre of mass, bbox, face/edge/vertex counts, totals; MCP exposes the same as its `measure` tool), `body_topology` for the faces and edge midpoints to pick for fillets and chamfers, and `inspect.measure` with `items` for picked geometry (a cylindrical face reports `diameter`, `radius`, `center`, `axis`; 3 to 64 round edges or cylinder faces with parallel axes reply `spacing` — centre-to-centre distances for a hole row or bolt circle). Check a result against an analytic value before telling the user a part is correct.

To change an existing feature, read it with `engine.execute timeline.inspect {feature}` and write it back with `timeline.edit {feature, set}` (e.g. `{"extent": {"distance": "30"}}`) rather than rebuilding the part.

Sketch notes: every mutating `sketch.*` reply carries `created: {points, curves, constraints, dimensions}` with stable ids (`l1`, `c1`, `k1`) that go straight into later commands. A bare numeric `sketch.dimension` `value` is read in the **design's units**, exactly as typed in the dimension box; pass `"50 mm"` or `"0.5 in"` to pin units. Point coordinates are always millimetres. Angles are degrees unless an expression says otherwise — except camera `yaw`/`pitch`/`roll`, which are **radians**, unlike `solid.move`'s `angle`.

## Watch the user's window, and take pictures

`ui.render {path, width?, height?, grid?, axes?}` draws the model with the app's GPU and needs no presented window — this is the reliable way to see the design. `ui.screenshot {path}` captures the window chrome and fails with `no frame was presented (window hidden?)` when the window is minimised, fully covered, or on another macOS Space; front it first (macOS: `osascript -e 'tell application "System Events" to set frontmost of (first process whose unix id is PID) to true'`) or just use `ui.render`. `ui.view {view, animate}` and `ui.camera {target, yaw, pitch, distance, fit}` move the viewport; `ui.worldToScreen` maps world points to pixels.

For real UI work (a dialog the engine cannot reach, or showing the user a workflow): `ui.handles` names toolbar buttons (`toolbar:<command id>`), tabs (`tab:Model`), panels and browser rows (`row:<label>`); `ui.click`/`ui.move`/`ui.drag` inject pointer input in screen points, `ui.key`/`ui.text` keyboard input, `ui.start {command, params}` opens a command's dialog, `ui.menuPick`, `ui.selection`, `ui.editFeature` and `ui.confirm` handle menus, dialog inputs, rollback-to-feature and delete confirmations. One pointer event per frame. `ui.agent_cursor {show: true}` makes `engine.execute` glide the pointer to each pick so the run reads like a person modelling.

## Files, export, and access rules

`file.new`, `doc.open {path}`, `file.save [path]`, `file.export {path, format}` (step, stp, iges, igs, 3mf, 3mf-tagged, stl, stla, obj, glb, usd, usda, usdc, usdz, 3dm, urdf, mjcf, sdf); STEP opens as an Import base feature, 3MF/STL as mesh bodies, and `up: "y"` stands a Y-up file upright. Mesh exports take `quality` (`standard`/`fine`/`finest`) or a `chord` tolerance in mm (not both). `doc.open` also reads a KiCad board (`.kicad_pcb`/`.kicad_pro`) with its copper, silkscreen and component models. Report the exact path and format written. Do not overwrite the user's source design unless asked — save a copy under a new name.

The MCP server restricts file paths to the open design's folder (only when strictly inside your home folder and not in a hidden folder), SolidCraft's recovery folder, and its scratch folder; widen with `--allow-path DIR` (repeatable) or lift with `--allow-any-path`. Raw control requests are unlimited for a token holder; a request may pass `allow_paths` to confine itself.

## Slow commands, timeouts, and uncertain outcomes

A request unanswered for 60 s (3600 s for `engine.batch`) replies `timeout: … is still running`. **That is not a failure** — the command may still apply, so never blindly resend a mutation. Ask `control.running` (whole app, never blocks) and `control.pending` (this connection's outstanding request, then its reply once, exactly once); while one is pending every other request on that connection replies `busy`. A request that outlived its wait can be cancelled from its own connection with `control.cancel {id?}` (MCP `cancel`): one still queued is removed and never runs, one computing off the window thread stops with nothing applied; one running on the window thread cannot be cancelled. `solidcraft-cli mcp` and `scripts/sc.py` wait far longer than 60 s on the socket, so bridged calls usually just answer late. Render jobs (`render.start`/`status`/`cancel`/`export`) are the non-blocking path for product images.

## Headless and scripts

`solidcraft-cli run <script.json|design.sc|part.step> [--in F] [--out F]... [--results] [--timings] [--profile]` replays a JSON list of the same commands (`references/scripts.md`); `eval`/`script` inspect and export a design's history; `snapshot --in design --out shot.png [--view iso|--camera JSON] [--section z=27] [--body Name:color=#rrggbb]` renders without a window; `recipe`, `oracle`, `fuzz`, `gpu` and `crashes` cover the rest (`solidcraft-cli --help`).

## Optional deeper guidance

Upstream ships six agent skills for the modelling workflow itself — `solidcraft-modeling`, `solidcraft-editing`, `solidcraft-checking`, `solidcraft-mechanisms`, `solidcraft-sheetmetal`, `solidcraft-reporting` — under [`skills/`](https://github.com/tangency-labs/solidcraft/tree/main/skills). Fetch the relevant one when a task is a full part build, an edit to an existing design, regression checking, an assembly with joints and motion studies, a sheet-metal flat pattern, or a design report. The MCP `skill_reference` tool returns all six from the copies built into SolidCraft.
