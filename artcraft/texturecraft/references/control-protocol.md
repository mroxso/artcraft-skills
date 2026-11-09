# Control protocol, MCP and CLI

Everything TextureCraft does is an engine command with a stable id (`layer.add.fill`,
`bake.run`, `edit.undo`, …). Agents and scripts reach the same commands four ways:

| Surface | Start it with | Use it for |
|---|---|---|
| Control channel | `texturecraft --control <port>` | Drive the running desktop app: commands, inspect, menus, screenshots |
| MCP server | `texturecraft-cli mcp` | AI agents (Claude Code, Claude Desktop, any MCP client), headless or bridged to the app |
| JSON-lines server | `texturecraft-cli serve [--port <port>]` | Scripts that keep one headless session open |
| CLI subcommands | `texturecraft-cli info/run/batch/bake/export/render/new` | One-shot jobs in shells and pipelines |

Programmatic calls never open dialogs: a command runs with its defaults. Only `ui.menu.invoke`
behaves like a menu click. `session.inspect` shows every layer, mask, effect, fill source and
painted tile count, so an agent can verify its work without a screenshot.
`effect.histogram {effect, channel?, bins?}` counts the values an effect reads (a levels
effect's input), so an agent can pick its input range from the data. `effect.move {effect,
index}` reorders an effect within its stack (0 = bottom) and `effect.duplicate {effect}` copies
one just above itself. `effect.copy {effect?}` and `effect.cut {effect?}` put an effect on the
layer clipboard, and `effect.paste {layer?, target?}` adds it to another layer's content or mask.

`effect.set {effect, filter: "blur", radius: 5}` replaces a filter in place, preserving its
stack position, blend, opacity and visibility. Replacement filters start from defaults plus
the supplied parameters; naming the current filter instead edits it without resetting omitted
parameters. Default effect names follow the new filter, custom names remain, and an explicit
`name` overrides either. Only filter effects can be replaced this way, and masks reject
content-only filters. `filter.list` lists the available IDs; levels and material finishes
must be added separately with `effect.add.filter`. A successful replacement is one undo step;
a rejected replacement changes nothing.

`edit.undo {steps?}` and `edit.redo {steps?}` go back or forward several steps at once (as far
as the history reaches); `edit.history` lists the steps done and the undone ones, next first.
Any command takes `merge: true` to fold its edit into the previous undo step when that step has
the same label: a drag that applies a value on every frame stays one step.

Bake mode applies edits in Common Settings and Mesh Map Settings to every texture set. Each
set keeps its own enabled mesh-map checkboxes and Include in Bake flag. Edits update only the
changed fields; Restore Defaults resets the whole parameter section across all sets.

`bake.settings {ts: "all", patch: {maps: {ao: {parameters: {rays: {rays: 128}}}}}}` changes
only AO secondary rays. A `patch` uses the nested `BakeSettings` field names and named enum
values returned in the command's `model` result; omitted fields retain each set's values, and
`null` clears optional fields such as `common.resolution_height`. All targeted sets are validated
before the edit is applied as one undo step. `model` still replaces the complete settings;
when combined, `patch` follows `model`, then the flat command parameters apply. Omitting `ts`
still targets the active set for scripts that need individual control.

The bake texture-set list shows visibility eyes and expandable UV tile rows. Visibility affects
the viewport independently of bake inclusion. Its resolution menus edit the texture-set size
(`textureSet.resolution`) and individual tile overrides (`textureSet.tile.resolution`), independently
of Common Settings' bake Output Size. Overridden tiles display a resolution marked with an asterisk;
inherited tile resolutions appear only on hover or while their menu is open. Remove resolution
override hides the number and restores inheritance from the set, including when their current
sizes happen to match.

Baked maps use a uniform UV tile atlas: every selected tile receives the full bake Output Size,
including rectangular output sizes. Changing a texture-set or tile working resolution preserves
the stored bake pixels. Materials, mesh-map previews, and exports sample those pixels through
the working tile layout. Older project files load their baked pixels as-is without layout
conversion; rebaking restores correct mapping and detail.

`bake.tile.set {ts?, tile: 1002, enabled: false}`
excludes one UV tile; `textureSet.inspect` / `session.inspect` expose each tile's `bakeEnabled`.
Tile choices are saved and undoable. Unchecked tiles retain their previous baked pixels, resampled
if output size changes, or neutral values when no previous map exists. A running bake uses the
tile selection captured when its worker started. Sets with no checked tiles are skipped; their
geometry still contributes to occlusion when baking other tiles.

## Control channel (desktop app)

```sh
texturecraft --control 7878
# stderr: texturecraft: control token written to <temp>/texturecraft-control-7878.token
```

Loopback TCP (`127.0.0.1` only), one JSON object per line each way. Requests are
`{"id", "method", "params"}`; replies are `{"id", "ok": true, "result"}` or
`{"id", "ok": false, "error"}`. Requests are limited to 8 MiB.

**Authentication.** The first request on every connection must be

```json
{"id": 0, "method": "auth", "params": {"token": "<token>"}}
```

The token is `TEXTURECRAFT_CONTROL_TOKEN` when that is set (16 to 1024 printable ASCII
characters; surrounding whitespace is ignored), otherwise a fresh random 256-bit token the app
writes to `<temp>/texturecraft-control-<port>.token` (`<temp>` is `%TEMP%` on Windows, `$TMPDIR`
or `/tmp` elsewhere). On Unix the file is created new and readable by its owner only; when an
existing file there cannot be replaced (another user's, in a shared `/tmp`), the control server
stays off: set `TEXTURECRAFT_CONTROL_TOKEN` instead. Clients (`texturecraft-cli mcp --bridge`)
only read a token file that is a regular file owned by them with no group or other permissions.

A connection must authenticate within 10 seconds. Any other first request, or a wrong token, is
refused and the connection closed. At most 16 connections are served at once.

Scripted runs (agents, recordings, tests) can set `TEXTURECRAFT_NO_PREFS` (any value) so the app
neither reads nor overwrites the user's saved layout and settings: it starts from the defaults and
keeps its state in a throwaway file.

| Method | Params | Result |
|---|---|---|
| `ping` | | `"pong"` |
| `command.run` | `{id, params?}` | the command's JSON result |
| `command.list` | `{filter?}` | `[{id, label, menu, shortcut, params, enabled}]` |
| `session.inspect` | | project, mesh, texture sets, layer stack, tool, camera, display, history |
| `ui.inspect` | | UI state, viewport rect, fps, bake progress, toasts, `titleBar` (who draws the title bar this run: `app`, `integrated` on macOS, or `system`) |
| `ui.menu.list` | | the menu catalog: `{menu, submenu, label, id, shortcut, implemented, enabled}` |
| `ui.menu.invoke` | `{id}` | behaves like a menu click (may open a window) |
| `ui.set` | fields of the UI state, e.g. `{"layout": "Only3D"}`; `dock` is the panel layout, a craft-ui docking `Workspace` (`{version, layout: {root, floating}, hidden}`; `root` is a tree of `Split`, `Tabs` and `Stack` nodes over the panels `Viewport`, `Assets`, `TextureSetList`, `Layers`, `TextureSetSettings`, `Properties`, `Display`, `Shader`, `History` and `Log`; `hidden` lists where each closed panel was, so reopening it puts it back; a layout that does not read or has no docked `Viewport` becomes the default), `prefs` the settings (`{"language": "ja", "viewport_texture": 1, "brightness": "light", "accent": "blue"}`; missing fields take their defaults; `brightness` is `dark`, `mediumDark` (default), `mediumLight` or `light`, `accent` `copper` (default), `coral`, `blue`, `violet`, `green`, `amber` or `pink`, applied on the next frame; `system_title_bar` `true` has the system draw the title bar from the next start), `keymap` the custom shortcuts (`{"file.save": "F5"}`, `""` unbinds) | `null` |
| `viewport.screenshot` | `{view?: "3d" \| "2d"}` | `{width, height, png}` (PNG, base64) |
| `ui.screenshot` | | `{width, height, png}` of the whole window, after the next frame |
| `ui.resize` | `{width, height}` | Sets the window's inner size in points (640–7680), leaving maximized state; for recordings and screenshots at a fixed size |
| `debug.paintTest` | `{from: [x, y], to: [x, y], frames?: 120}` | Paints a straight stroke through the real frame loop (viewport pixels, one point per frame) for performance work |
| `debug.frames` | | Frame timing since the last call (then cleared): `{frames, intervalMs, uiMs, syncMs, logicMs}` each `{avg, p95, max}`; `syncMs` is compositing plus display tile conversion, `logicMs` input, control requests and scripted strokes before the UI is built; `worst` breaks down the slowest frame; `strokeEnd` lists the frame that committed a `debug.paintTest` stroke and the one after it (null without one) |

Example session:

```text
> {"id":0,"method":"auth","params":{"token":"3f9c…"}}
< {"id":0,"ok":true}
> {"id":1,"method":"command.run","params":{"id":"layer.add.fill","params":{"color":"#336699","roughness":0.2}}}
< {"id":1,"ok":true,"result":{"layer":7}}
> {"id":2,"method":"command.run","params":{"id":"mask.add.black"}}
< {"id":2,"ok":true,"result":null}
> {"id":3,"method":"viewport.screenshot","params":{"view":"3d"}}
< {"id":3,"ok":true,"result":{"width":1210,"height":788,"png":"iVBORw0KGgo…"}}
```

A minimal client (Python, for illustration):

```python
import json, os, socket, tempfile
port = 7878
token = os.environ.get("TEXTURECRAFT_CONTROL_TOKEN") or open(
    os.path.join(tempfile.gettempdir(), f"texturecraft-control-{port}.token")).read().strip()
s = socket.create_connection(("127.0.0.1", port)); f = s.makefile("rw")
def call(method, params=None, _id=[0]):
    _id[0] += 1
    f.write(json.dumps({"id": _id[0], "method": method, "params": params or {}}) + "\n"); f.flush()
    reply = json.loads(f.readline())
    if not reply["ok"]: raise RuntimeError(reply["error"])
    return reply.get("result")
call("auth", {"token": token})
print(call("command.run", {"id": "layer.add.fill", "params": {"color": [0.8, 0.1, 0.1]}}))
```

## MCP server

`texturecraft-cli mcp` speaks MCP on stdin/stdout (stdout carries only protocol messages).

- **Headless** (default): an in-process session that starts on the material ball (1024).
  Files are reachable only below the roots given at launch, as forward-slash paths relative to
  them: `--read-root <dir>` for `project_open` / `mesh_import` / `mesh_reimport` / `bake_mesh_add`,
  `--write-root <dir>` for `project_save` / `material_save` / `textures_export` / `mesh_export`
  (`--automation-read-root` / `--automation-write-root`, as in the other crafting apps, are the
  same flags). Without roots there is no file access. `..`, absolute
  paths, drive letters, device names and symlink or junction escapes are refused.
- **Bridge**: `--bridge <port>` forwards to a running `texturecraft --control <port>` (token from
  `--token`, `TEXTURECRAFT_CONTROL_TOKEN` or the app's token file). The app reads and writes its
  own files, so the path tools are unavailable there; `project_save` without a path invokes
  File › Save.

Through `command_run`, every `file.*` command but `file.close` and `file.removeUnused` (and
`file.reimportMesh` without a `path`) is refused, and so is any command given a `path` or `dir`, at the top level or in
a `files` entry (`resource.import`, `material.save`, `material.load`, `textureSet.meshMap.import`, …), in both modes: use the workspace tools below. `resource.text`
takes a font family, not a path: it reads only the system's font folders.

| Tool | Params | Notes |
|---|---|---|
| `session_inspect` | | The whole session as JSON |
| `command_list` | `{filter?}` | Command ids, labels, params docs, enabled now |
| `command_run` | `{id, params?}` | Any command by id |
| `command_batch` | `{steps: [{id, params?}]}` | Stops at the first error: `{completed, results, failed: {index, id, error}}` (a tool error) |
| `project_new` | `{mesh?, resolution?, name?, template?}` | Built-in mesh: material_ball, sphere, cube, rounded_cube, cylinder, torus, plane, crate; `template` names a project template (`project.templates`) |
| `project_open` | `{path}` | `.tcraft` or a mesh file, relative to the read root |
| `project_save` | `{path?}` | `.tcraft` (appended if missing), relative to the write root |
| `mesh_import` | `{path, resolution?}` | New project from .glb/.gltf/.fbx/.dae/.usd/.usda/.usdc/.usdz/.abc/.obj/.ply/.stl; a .gltf's buffers and images and a loose USD layer's textures are read from its folder |
| `mesh_reimport` | `{path?, preserveStrokes?}` | Reimport the mesh from a file, or (no path) from the project's own copy; bridge mode supports only the latter |
| `mesh_export` | `{path, format?}` | The mesh as obj, glb, usda, usdc or usdz below the write root (obj: its .mtl and textures, usda / usdc: textures next to it) → `{path, textures?}` |
| `bake_mesh_add` | `{path, cage?}` | Add a high-definition mesh for baking, or set the cage → `{name, meshes}` |
| `resource_import` | `{path}` | Image resource (png, jpg, tga, tif, bmp, webp, exr, hdr) → its name, for `layer.add.image` / `tool.stencil`, or as a mesh map instead of baking it: `textureSet.meshMap.set {ts?, map, image}` (`textureSet.meshMap.clear {ts?, map}` empties the slot); call it once per baked map file (the desktop app's `textureSet.meshMap.import`, which takes host paths, is refused through `command_run`) |
| `material_save` | `{path, layer?, name?}` | A layer or folder as a `.tcmat` smart material below the write root |
| `material_load` | `{path}` | Add a `.tcmat` smart material, a MaterialCraft `.mcmat` material or a `.mcraft` package above the selection |
| `textures_export` | `{dir, preset?, ts?, format?, padding?, size?}` | Writes files below the write root |
| `bake` | `{ts?, resolution?, maps?, cpu?}` | Mesh maps for generators and smart materials; rays on the GPU when there is one (`cpu: true`: on the CPU). Per-map ray settings (`ao`, `thickness`, `bentNormal`: rays, maxDistance, spread, distribution; AO ignoreBackface, selfOcclusion) are `bake.settings` parameters |
| `paint_stroke` | `{points, viewport?, color?, roughness?, metallic?, height?, size?, hardness?}` | Paint tool + brush material + `tool.stroke`; points in viewport pixels |
| `viewport_render` | `{view?: "3d" \| "2d", width?, height?, yaw?, pitch?, samples?, bounces?, cpu?}` | Headless: PNG image (≤ 2048 px a side); yaw/pitch in degrees for this render only; `samples` (1–4096) path traces the 3D view instead, on the GPU when it has compute shaders, else (or with `cpu: true`) on the CPU (no GPU needed) |
| `viewport_screenshot` | `{view?}` | Bridge: the app's 3D or 2D view |
| `ui_screenshot` | | Bridge: the whole window (downscaled to 2048 px) |
| `ui_inspect` | | Bridge: UI state |
| `ui_menu_invoke` | `{id}` | Bridge: a menu click |

Replies are capped: 8 MiB of JSON, 5 MiB per PNG, 256 batch steps. Stroke points and render
sizes share one space: the default render size is the session viewport (1280×800), so
`paint_stroke` points can be read straight off a `viewport_render` image.

A typical agent run: `project_new {"mesh": "sphere"}` → `command_run layer.add.fill
{"color": "#336699", "roughness": 0.2}` → `bake {"resolution": 512}` → `command_run
mask.add.black` → `command_run effect.add.generator {"generator": "edgeWear"}` →
`session_inspect` → `viewport_render` → `project_save {"path": "ball.tcraft"}` →
`textures_export {"dir": "textures", "preset": "glTF PBR Metal Roughness"}`.

### Claude Code

```sh
claude mcp add texturecraft -- texturecraft-cli mcp --read-root . --write-root .
# bridged to the running app:
claude mcp add texturecraft-app -- texturecraft-cli mcp --bridge 7878
```

or a project `.mcp.json`:

```json
{
  "mcpServers": {
    "texturecraft": { "command": "texturecraft-cli", "args": ["mcp", "--read-root", ".", "--write-root", "."] }
  }
}
```

### Claude Desktop

In `claude_desktop_config.json` (Settings › Developer › Edit Config), with absolute paths:

```json
{
  "mcpServers": {
    "texturecraft": {
      "command": "C:\\Program Files\\TextureCraft\\texturecraft-cli.exe",
      "args": ["mcp", "--read-root", "C:\\Users\\me\\Texturing", "--write-root", "C:\\Users\\me\\Texturing"]
    }
  }
}
```

## Headless JSON-lines server

`texturecraft-cli serve` keeps one headless session open and answers the control channel's
envelope on stdin/stdout (no authentication: the caller started the process). With
`--port <port>` it listens on `127.0.0.1:<port>` instead, with the same `auth` handshake and
token rules as the app (a generated token goes to `<temp>/texturecraft-control-<port>.token`).
File access follows `--read-root` / `--write-root` as for MCP.

| Method | Params |
|---|---|
| `ping`, `methods`, `session.inspect` | |
| `command.run` | `{id, params?}` |
| `command.list` | `{filter?}` |
| `command.batch` | `{steps: [{id, params?}]}` |
| `project.open` | `{path}` |
| `project.save` | `{path?}` |
| `mesh.import` | `{path, resolution?, name?}` |
| `mesh.reimport` | `{path?, preserveStrokes?}` |
| `mesh.export` | `{path, format?}` |
| `bake.mesh.add` | `{path, cage?}` |
| `resource.import` | `{path}` |
| `material.save` | `{path, layer?, name?}` |
| `material.load` | `{path}` |
| `textures.export` | `{dir, preset?, ts?, format?, padding?, size?, bitDepth?, dilation?, normalFormat?}` |
| `render` | `{view?, width?, height?, yaw?, pitch?}` → `{width, height, png}` |

```sh
printf '%s\n' '{"id":1,"method":"command.run","params":{"id":"project.new","params":{"mesh":"torus"}}}' \
              '{"id":2,"method":"render","params":{"width":512,"height":512}}' | texturecraft-cli serve
```

## Camera bookmarks

Saved cameras (`Project.cameras`, stored in the `.tcraft` file) are the camera bookmarks.
`camera.add {name?}` saves the current view, `camera.list` lists them (`current` is the one the view
is at), `camera.select {index? | name?}` restores one, `camera.rename {index? | name?, to}` and
`camera.remove {index? | name?}` edit them. `camera.bookmark1` … `camera.bookmark9` (Ctrl+1 … Ctrl+9)
go to the first nine. Commands jump straight to the view; the desktop UI glides there over about a third
of a second.

## MaterialCraft materials

A `.mcmat` portable material (MaterialCraft's format, read here by `formats::mcmat`; the manifest is
documented in MaterialCraft's `docs/control-protocol.md` § Portable materials) becomes a fill layer
whose channel sources are its cooked maps and whose `link` (shown by `project.inspect`) holds the
graph's exposed inputs, presets and image inputs. The apps share the format and the command line,
not code.

| Command | Params |
|---|---|
| `material.load` | `{path, above?, inside?, index?}`: `.tcmat`, `.mcmat` or `.mcraft` (cooked first) |
| `material.link.set` | `{layer?, id, value, cook?: true}`: a number, `[..]`, a bool, `"#rrggbb"` or a typed `{"t", "v"}`; re-cooks unless `cook: false` |
| `material.link.preset` | `{layer?, name, cook?: true}` |
| `material.link.cook` | `{layer?}`: re-cook at the texture set's resolution with its baked mesh maps (after a bake or a resize) |
| `material.link.saveSource` | `{layer?, path}`: the `.mcraft` package, to open in MaterialCraft |

Re-cooks run `materialcraft-cli run <package> file.exportMaterial {path, size, values, inputs}`:
`$MATERIALCRAFT_CLI`, else `materialcraft-cli` next to the TextureCraft executable, else on `PATH`
(the app is `$MATERIALCRAFT` / `materialcraft`). Baked maps feed graph input nodes whose identifier
matches the map's shared id (`ambientOcclusion`, `curvature`, `thickness`, `position`,
`worldNormal`, `normal`, `height`, `id`, `bentNormal`, `opacity`, `colorMap`, `worldDirection`;
case and underscores ignored). Usages map to channels of the same id (`baseColor`, `normal` in
OpenGL convention, `roughness`, `metallic`, `height`, `ambientOcclusion`, `emissive`, `opacity`,
`specular`); missing channels join the texture set.

## CLI

```sh
texturecraft-cli --version                                   # TextureCraft 0.1.0 (abc1234 2026-10-14)
texturecraft-cli info model.glb                              # triangles, materials, UV report
texturecraft-cli info project.tcraft                         # texture sets, layers, baked maps
texturecraft-cli commands --filter mask
texturecraft-cli new builtin:material_ball ball.tcraft --resolution 1024 --sample   # mesh maps baked at ≤ 1024 px
texturecraft-cli new model.glb model.tcraft --resolution 2048
texturecraft-cli run ball.tcraft layer.add.fill '{"color":"#c08040","metallic":1}' -o ball.tcraft
texturecraft-cli batch script.json
texturecraft-cli bake model.tcraft --resolution 2048 --maps ambientOcclusion,curvature,thickness
texturecraft-cli export model.tcraft out/ --preset "Unreal Engine (Packed)" --format png --size 2048
texturecraft-cli render ball.tcraft ball.png --size 1280x800 --view 3d --yaw 30 --pitch 15
texturecraft-cli render scene.tcraft hero.png --size 1200x900 --camera Hero --samples 2048   # a saved camera (camera.add), path traced
```

`<input>` is a `.tcraft` project, a mesh file or `builtin:<id>`. A batch script is a list of
steps or an object with an optional input and output (paths relative to the current directory):

```json
{
  "open": "builtin:sphere",
  "steps": [
    {"id": "layer.add.fill", "params": {"color": [0.6, 0.6, 0.62], "metallic": 1, "roughness": 0.3}},
    {"id": "bake.run", "params": {"resolution": 512}},
    {"id": "material.apply", "params": {"material": "iron_rusted"}}
  ],
  "save": "rusty.tcraft"
}
```

Errors print `texturecraft-cli <command>: error: …` and exit 1; usage errors exit 2. The CLI is a
console program and never opens a window; `render` needs a GPU or software adapter.
