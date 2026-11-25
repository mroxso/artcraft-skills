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
`layer.select {layers: [id], layer?}` selects several layers of one texture set at once (`layer`
is the active one), and `{layer, range: true}` / `{layer, toggle: true}` do what Shift+click and
Ctrl+click do in the Layers panel. `layer.select {all: true}` (Ctrl+A with the pointer over the
Layers panel) selects every shown row of the active texture set: the folder rows and the layers
of open folders, not the layers of collapsed ones. `{layer, toggle: true}` on the only selected
layer leaves nothing selected. `layer.visible {layers, layer}` gives every listed layer the
opposite of `layer`'s visibility (the Layers panel's eye uses `{layer}` and acts on that layer
only). `layer.group` puts the new folder at the place and in the folder of the topmost selected
layer, the others in stack order; `layer.duplicate` puts the copies in one block above the
topmost selected layer. Without `layer`, `layer.remove`, `layer.duplicate`,
`layer.group` and `layer.visible` act on every selected layer; each of them and `layer.move
{layers, above | index}` also take an explicit `layers` list. `session.inspect` lists the
selection as `selectedLayers` (top row first).

`mask.export {layer?, path}` writes the layer's evaluated mask as a 16-bit grayscale PNG at the
texture set's resolution: black where the mesh does not cover the texture, with the orientation
of the exported textures (top row first). A UV-tiled set writes one file per tile, each at its
tile's size, with the tile number before the extension (`mask.1001.png`, `mask.1002.png`). The
result is `{files}`. A layer without an enabled mask is an error. The layer menu's Export mask to
file runs it; Copy mask to clipboard puts the same mask on the system clipboard as an 8-bit
grayscale image (the whole tile atlas for a UV-tiled set).

`file.exportTextures`, `export.plan`, the automation `textures.export` method and the MCP
`textures_export` tool accept `maps: [{map, enabled?, format?, bitDepth?, dithering?}]`.
Each entry overrides that map's export settings. The `map` field is its index in the selected
template. `enabled: false` suppresses that file while reserving its name. When several texture
sets produce the same name (ignoring case), programmatic and browser exports keep the first file
and warn about later duplicates. The desktop export window reports the collision before writing.

`file.exportTextures` with `usdAsset` also writes `<mesh>.usd` (binary USD, Crate) next to the textures: the whole mesh
(every texture set, whatever `ts` selects) with one UsdPreviewSurface material per texture set. A
material's inputs read the texture files the export planned for that set with its output template
(`usdAsset: true`: the sets, options and `reservedNames` of this command; a list of export params such as
`[{"ts": 0, "preset": "..."}, {"ts": 1}]`, not empty, every entry an object: each entry's sets, options and `reservedNames`, the way the export window,
which runs one command per texture set, passes the params of all its commands with the last one).
Bound inputs: `diffuseColor`, `roughness`, `metallic`, `normal`, `emissiveColor`, `opacity`,
`clearcoat` and `clearcoatRoughness`, each reading the `rgb`, `r`, `g`, `b` or `a` output of the
file that holds it; other maps (ambient occlusion, height, specular...) are not bound, a UDIM map that lost a tile to an earlier
set's file name or to an entry's `reservedNames` is not bound, a mesh with no materials gets one implicit `default` material bound to the Default set, and a texture set outside the export has
no textures. A file name is relative to the file (`./<file>`, with `<UDIM>` for UV tiles). A failure
to build or write it is named in `warnings` and the command still succeeds. The file is in `files`.

`file.exportTextures` with `materialX: true` also writes an OpenPBR `.mtlx` beside each texture
set's maps. It reuses compatible maps with OpenPBR names and writes dedicated maps for remaining
inputs with data. A named OpenPBR map explicitly disabled in `maps` stays disabled. Dedicated maps
use the effective size, padding and color space. A dedicated replacement for a named map keeps
its file settings where supported. PSD, JNG, PGM and WebP fall back to the OpenPBR template's PNG
format and bit depth. MaterialX uses OpenGL normals.

`reservedNames: [file names]` takes the basenames and `materialUdimPatterns` returned by earlier
`file.exportTextures` calls in the same export. The desktop window passes both when exporting
one set at a time. Comparisons ignore case. If a name is reserved, the command skips the file
and names it in `warnings`. Materials omit any map with incomplete tiles or a UDIM pattern
shared by different sets.

`format` accepts the export window's names (`bmp`, `jpeg`, `jng`, `pgm`, `png`, `targa`, `tiff`,
`hdr`, `exr`, `webp`, `psd`) and their extensions. `bitDepth: 32` selects floating point for
TIFF, EXR and HDR. `dithering: true` dithers 8-bit integer output with an ordered pattern, and
`export.plan` reports the effective setting and per-file dimensions (`size` and `sourceSize`, both in pixels). `padding: "diffusion"` dilates by
`dilation` texels and fills the remaining space with a smooth blend of the island colours.

`effect.set {effect, filter: "blur", radius: 5}` replaces a filter in place, preserving its
stack position, blend, opacity and visibility. Replacement filters start from defaults plus
the supplied parameters; naming the current filter instead edits it without resetting omitted
parameters. Default effect names follow the new filter, custom names remain, and an explicit
`name` overrides either. Only filter effects can be replaced this way, and masks reject
content-only filters. `filter.list` lists the available IDs; levels and material finishes
must be added separately with `effect.add.filter`. A successful replacement is one undo step;
a rejected replacement changes nothing.

Warp (`warp`) and Blur Slope (`blurSlope`) work on layer content or masks. Use these IDs with
`effect.add.filter` and `effect.set`, including when replacing a saved filter. They share
normalized `intensity` (0..1), `divider` (1, 10, 100, 1000), and `seed`.

- Warp accepts `warpMode: "warp" | "directional" | "multiDirectional"`. The directional
  modes take `angle` in degrees. Multidirectional Warp also takes `directions` (1, 2, 4)
  and `blendingMode: "average" | "min" | "max" | "chain"`.
- Blur Slope accepts `blendingMode: "blur" | "min" | "max"` and normalized `quality` (0..1).
- Both take `sourceMode: "defaultNoise" | "previousInput" | "customNoise"`, normalized
  `sourceBlur`, `sourceBalance` and `sourceContrast`, and `sourceTiling` (0.01..16).
  Source Tiling sets the noise frequency or repeats a sampled source within each UV tile.
  In Custom Noise mode, set the grayscale source through `layer.fill.set
  {effect, input: "customNoise", ...}`. Blur Slope can read an anchor through that slot.

For directional Warp, use `effect.add.filter {target: "content", filter: "warp",
warpMode: "directional", angle: 45, intensity: 0.05, divider: 1}`. To replace that effect,
use `effect.set {effect, filter: "blurSlope", quality: 0.5}`.

This changes the automation contract. `warp` uses normalized intensity, and the
`warpDirectional` and `slopeBlur` selectors return an unknown-filter error. Saved filter
settings still load as stored. Restore Defaults applies to the current catalog entries.

`edit.undo {steps?}` and `edit.redo {steps?}` go back or forward several steps at once (as far
as the history reaches); `edit.history` lists the steps done and the undone ones, next first. Step names are English; a stroke is named by tool and layer (`Paint on Rust`,
`Clone on Rust`, `Erase mask of Rust`).
Any command takes `merge: true` to fold its edit into the previous undo step when that step has
the same label: a drag that applies a value on every frame stays one step.

A colour param is `[r, g, b]` in linear 0..1, or `"#rrggbb"` in sRGB, which is converted to
linear. The same digits are two different colours: `"#c8102e"` is `[0.578, 0.005, 0.027]`, while
`[0.784, 0.063, 0.180]` (its hex digits over 255) paints the lighter `#e54776`. Pass a colour from
a design tool or a brand guide as hex. A single number is a linear grey.
For a colour selection, `effect.set` accepts only linear `[r, g, b]` arrays in its `colors` list.

`tool.cloneSource {uv: [u, v]}` (or `{x, y}` for a point on the mesh, or `{clear: true}`) sets the
Clone tool's source. The source belongs to the active texture set: selecting another texture set
(`textureSet.select`, or `layer.select` of a layer in another set) clears it. `tool.brush
{cloneAligned}` (default `true`) chooses how later strokes use it: aligned keeps the offset the
first stroke fixed, so the source moves along with the brush; `false` makes every stroke start
sampling at the source point. Changing `cloneAligned` forgets the offset of earlier strokes.
`tool.brush` takes the alpha's shared parameters next to `alpha`: `alphaSizeX` and `alphaSizeY`
(5..100, percent of the stamp the alpha fills, default 100), `alphaRoundness` (0..100, only for the
procedural Round alpha: 100 is a circle, 0 a square), `alphaContrast` (1..8, 1 leaves the values
alone) and `alphaInvert` (swaps paint and no paint inside the stamp square). They apply to
procedural, library and imported alphas alike and are returned by `tool.brush` with the other
values. The alpha's rotation is the brush `angle`.

Bake mode applies an edit in Common Settings or Mesh Map Settings to the texture sets sharing that
group's settings: Common Settings, and each map's settings, are shared by any set of texture sets
(at first every set shares them). Each set keeps its own enabled mesh-map checkboxes and Include in
Bake flag. An edit reaches the sets sharing its group with only the fields it changed, so values
that differ elsewhere stay; Restore Defaults resets the whole parameter section across those sets.

`bake.sync {group: "common" | <map id>, ts: [indices] | "all"}` makes exactly these sets share the
group from now on; sets joining take the settings the group shares. `bake.copy {what: "settings" |
"checked" | "check", map?, from?, ts}` copies once: every setting with which maps are checked (or
one map's settings), which maps are checked, or checks one map; settings also reach the sets sharing a group with a target, while
checkboxes stay per set. Each is one undo step. `bake.settings` with `model` keeps each set's sync
membership. A `patch` containing `sync` is rejected. Use `bake.sync` to change membership.
For `bake.copy`, `from` takes a texture set index and `map` takes a mesh map ID. Omit either field
or pass `null` to use its default.

`bake.settings {ts: "all", patch: {maps: {ao: {parameters: {rays: {rays: 128}}}}}}` changes
only AO secondary rays. A `patch` uses the nested `BakeSettings` field names and named enum
values returned in the command's `model` result; omitted fields retain each set's values, and
`null` clears optional fields such as `common.resolution_height`. All targeted sets are validated
before the edit is applied as one undo step. `model` still replaces the complete settings;
when combined, `patch` follows `model`, then the flat command parameters apply. Omitting `ts`
still targets the active set. Settings passed to `bake.run` follow the same sync rules, while only
the requested texture sets bake. The settings and baked maps share one undo step.

Bake presets are saved settings in the UI state (Mesh Map Bakers > Presets). Loading one is
`bake.settings {ts: <index>, model: <the preset's settings>, preserveEnabled: true, preset: true}`; Apply to All
Texture Sets is the same with `ts: "all"` and the active set's `model`. Both are one undo step.
When a bake started in the app ends, a toast counts the new maps and failed sets, and shows the
elapsed time. On failure, the toast can open the Log. The session log gets `Bake finished: N maps in T` and `Bake of texture set N failed: <error>`.

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

`view.solo {layer?, ignoreMask?}` shows one layer alone in the viewport, as if the other layers
of its texture set were hidden (`layer` defaults to the selected layer, `layer: null` ends the
solo; `ignoreMask: true` draws the layer, and the folders around it, at full coverage; other
texture sets are unchanged). It changes only the view: nothing enters the undo history, the
project file or an export (`file.exportTextures` and the CLI export the whole stack, then the solo comes
back), and removing the soloed layer ends it. `session.inspect` reports it as `solo`
(`{layer, ignoreMask}` or `null`).

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
| `ui.inspect` | | UI state, viewport rect, fps, bake progress (`baking`, 0..1), the running bake's stage (`bakeStatus`, e.g. "Baking Ambient Occlusion (2/4)") and live preview (`bakePreview`, see *Live bake preview*), toasts, `titleBar` (who draws the title bar this run: `app`, `integrated` on macOS, or `system`) |
| `ui.menu.list` | | the menu catalog: `{menu, submenu, label, id, shortcut, implemented, enabled, checked}` |
| `ui.menu.invoke` | `{id}` | behaves like a menu click (may open a window; `ui.resetUi` opens its question; `file.exportMesh` opens the Mesh Export Options prompt, whose Export asks for the file; `ui.view.export` opens the right bar's Export panel). `{"id": "ui.layout.apply", "name": "<layout>"}` switches to a legacy named panel layout (still accessible through assigned shortcuts) (panels only; mode, zoom and wireframes stay) and errors when no layout has that name. `ui.layout.save` still saves the active mode; `ui.layout.save.painting`, `ui.layout.save.rendering` and `ui.layout.save.baking` ask where to save only that mode's panels and view arrangement as a JSON file (without preferences or recent projects); loading preserves the other modes, `ui.layout.load` asks for one to load ("Load UI Layout"); `ui.toolbar.docks` and `ui.toolbar.tools` show or hide the right bar and the painting tools; the disabled Snooze Autosave and Resources Updater buttons stay visible when Tools is off; `ui.view.renderer` toggles the Renderer Settings panel (Rendering Mode only). `{"id": "ui.layout.swap"}` swaps the 3D and 2D views of the split layout (F4) |
| `ui.menu.invoke` id `project.sample` | `{id}` | File > Open Sample Project opens a file picker for a `.tcraft` project. The direct `project.sample` engine command still creates the generated sample for automation. |
| `ui.menu.invoke` id `ui.saveAsTemplate` | `{id}` | File > More Save Options > Save As Template opens a save dialog in the user templates folder. The choice supplies the file path and template name to `project.template.save`. `ui.saveReduced` (Save and Reduce File Size) is listed as not implemented and not enabled |
| `ui.menu.invoke` ids `ui.help.releaseNotes`, `ui.help.showLog`, `ui.help.exportLog` | `{id}` | Help > Release Notes opens the releases page in the browser; Help > Show Log opens the current desktop run's rolling `log.txt` in the system text-file handler; Help > Export Log exports the session log with each entry’s recorded UTC time, severity and source (a save dialog on desktop with a `Log_TextureCraft_<version>_<date>_<os>_<gpuMode>.txt` name, a download on the web) |
| `ui.menu.invoke` id `ui.wireframe` | `{id}` | Show mesh wireframe: shows or hides the mesh wireframe in the 3D and 2D views (the Display Settings check box). It has no menu entry and no default key; bind it in Settings > Shortcuts. The key bindings `camera.next` and `camera.previous` (Select next camera `>`, Select previous camera `<`) and `ui.mode.bake` (F8) run the same commands as before |
| `ui.reset` | | resets the panels, view layout, zoom and every other view setting at once, without the question the Reset UI menu item asks; settings and shortcuts stay |
| `ui.bake.start` | `{ts?: index \| [indices]}` (default: the sets ticked in Bake mode) | Opens Bake mode and bakes in the background like the Bake button: the 3D view shows the maps landing on the model as they finish (see *Live bake preview*). → the `bake.preview` state. Errors when a bake is already running |
| `ui.bake.cancel` | | Stops the running bake; the set being baked keeps the maps it had, sets already finished stay applied, and the previous view mode comes back |
| `ui.set` | fields of the UI state, e.g. `{"layout": "Only3D"}`; `dock` is the panel layout, a craft-ui docking `Workspace` (`{version, layout: {root, floating}, hidden}`; `root` is a tree of `Split`, `Tabs` and `Stack` nodes over the panels `Viewport`, `Assets`, `TextureSetList`, `Layers`, `TextureSetSettings`, `Properties`, `Display`, `Shader`, `History`, `Log`, `BakingLog`, `MeshMapBakers`, `BakeMaps`, `BakeSettings`, `Export` and `Renderer` (a floating window holding one right-bar panel is that panel undocked); `hidden` lists where each closed panel was, so reopening it puts it back; a layout that does not read or has no docked `Viewport` becomes the default), `prefs` the settings (`{"language": "ja", "viewport_texture": 1, "brightness": "light", "accent": "blue"}`; missing fields take their defaults; `brightness` is `dark`, `mediumDark` (default), `mediumLight` or `light`, `accent` `copper` (default), `coral`, `blue`, `violet`, `green`, `amber` or `pink`, applied on the next frame; `system_title_bar` `true` has the system draw the title bar from the next start), `keymap` the custom shortcuts (`{"file.save": "F5"}`, `""` unbinds), `log_channel` the Log panel's tab (`General` or `Assets`) | `null` |
| `viewport.screenshot` | `{view?: "3d" \| "2d"}` | `{width, height, png}` (PNG, base64) |
| `ui.screenshot` | | `{width, height, png}` of the whole window, after the next frame |
| `ui.resize` | `{width, height}` | Sets the window's inner size in points (640–7680), leaving maximized state; for recordings and screenshots at a fixed size |
| `debug.paintTest` | `{from: [x, y], to: [x, y], frames?: 120}` | Paints a straight stroke through the real frame loop (viewport pixels, one point per frame) for performance work |
| `debug.frames` | | Frame timing since the last call (then cleared): `{frames, intervalMs, uiMs, syncMs, logicMs}` each `{avg, p95, max}`; `syncMs` is compositing plus display tile conversion, `logicMs` input, control requests and scripted strokes before the UI is built; `worst` breaks down the slowest frame; `strokeEnd` lists the frame that committed a `debug.paintTest` stroke and the one after it (null without one) |

The empty-project menus keep Recent Projects openable with Clear disabled when the list is empty.
`ui.recent.clear` clears that list. More Save Options is disabled until a project is open.
Help > Shortcuts list opens Settings on its Shortcuts page. Window > Reset UI restores the
Assets, Layers, Properties, Texture Set List and Texture Set Settings panels and both toolbars.
Baking Log and the bake/render settings views are disabled without a project. Import resources
can open its dialog on desktop without a project; importing still requires an open project,
and the dialog explains that asset-library import is not available yet.

Settings > General > Recent Projects limit controls the retained history (default 10, range 0–100; 0 disables history). Automation uses `ui.set {"prefs":{"recent_projects_limit":10}}`. A lower limit trims the oldest paths immediately.

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

### Live bake preview

A bake started in the app (`ui.bake.start`, or the Bake button) makes the mesh maps one after
another, in the `BakedMap` order of the set's enabled maps, and shows each one on the model as
soon as it is finished and padded: the 3D view displays the newest finished map raw (normals as
RGB, scalar maps as gray, ID maps as their colors), maps and texture sets not baked yet show their
neutral value, and the bake bar names the stage (`Baking Ambient Occlusion (2/4)`). Each map is a
bake of its own, so with a high poly the transfer rays are cast once per map; the pixels are the
same as a single bake's. `bake.run` and the CLI bake all maps at once and never show a preview.

The streamed maps are held by the session, not the document: nothing enters the undo history
until a texture set's bake is applied (one undo step); a cancelled bake leaves the set it was baking
as it was, while sets that finished before the cancel stay applied. When
the bake ends, is cancelled or Bake mode is left, the view mode that was in use comes back.
Bake setup overlays are hidden during the preview so they cannot cover the maps; their visibility
settings take effect again when the preview ends.
**Painting is paused while a bake is shown**: strokes and polygon fills fail with "Painting is paused while a bake
is shown. Cancel the bake or wait for it to finish."

`bake.preview` `{show?: "follow" \| "material" \| "map:<id>"}` reads and sets what the view shows
(also the control in the bake bar): `follow` (default) the newest finished map, `material` the lit
material, `map:<id>` one map pinned (neutral until it is baked). Picking a mesh map with
`viewport.view` during a bake pins it; any other view mode is kept for when the bake ends. Result,
also `session.inspect`'s `bakePreview`:

```json
{"active": true, "show": "follow", "shown": "ambientOcclusion", "newest": "ambientOcclusion",
 "restore": "Material", "stage": {"set": 0, "map": "curvature", "n": 3, "total": 4},
 "sets": [{"set": 0, "order": ["id", "ambientOcclusion", "curvature", "height"], "done": ["id", "ambientOcclusion"]}]}
```

`{"active": false}` when no bake is shown; setting `show` then is an error. Drive a bake with
`ui.bake.start` and poll `ui.inspect`'s `bakeStatus` / `bakePreview` (and `viewport.screenshot`)
until `baking` is `null`.

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

The UI's `prefs.project_open_limit_gib` sets the maximum decompressed project data accepted on open
(default 8 GiB, minimum 1 GiB). Set it with `ui.set {"prefs":{"project_open_limit_gib":16}}`;
it takes effect before the next control request, without waiting for a frame, and persists with
the UI preferences. Individual entry limits still apply. This controls opening only, independently
of `prefs.reserved_cores` and `prefs.save_ram_percent` for saving.
Settings bounds the reserved-core input to the available logical CPU count and shows the estimated
save budget in GiB beside the RAM percentage. The readout refreshes once a second from currently
available RAM; a save calculates its budget when it starts.

Other preferences set through `ui.set {"prefs": {...}}`: `language` (`""` follows the system
language), `work_threads` (worker threads for painting, baking and export; 0 uses every logical
CPU; read at startup), `rotation_speed` (default 2), `zoom_speed` and `wheel_speed` (default 1,
each from 0.1 to 10) with `zoom_inverse` and `wheel_inverse`, `gpu_raytracing` (false keeps bake
rays on the CPU) and `libraries` (the folders the shelf scans for saved smart materials and masks).
For example, the `libraries` field can contain `[{"name": "Studio", "path": "/assets/studio"}]`.
Use an absolute path on the host running TextureCraft. To change one preference, read `state.prefs`
with `ui.inspect`, update that field and send the full `prefs` object to `ui.set`.

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

`file.close` leaves no project open: `session.inspect` then reports `projectOpen: false`, `command.list` marks every command but the project-independent ones as not enabled: the ones that open or create a project (`file.open`, `file.new`, `project.new`, `project.sample`), `project.inspect`, `viewport.frame`, `project.templates`, the `export.preset*` commands (`export.presets`, `export.preset.get`, `export.preset.save`, `export.preset.remove`) and the library and preset listings (`brush.preset.list`, `alpha.list`, `filter.list`, `material.list`, `mask.smart.list`, `text.fonts`), each still subject to its own enabled check. The rest are refused with "no project is open" until a project is opened or created. A `texturecraft --control` run starts with the sample project (an empty material ball with `--empty`); the app without `--control` starts with no project.

| Tool | Params | Notes |
|---|---|---|
| `session_inspect` | | The whole session as JSON |
| `command_list` | `{filter?}` | Command ids, labels, params docs, enabled now |
| `command_run` | `{id, params?}` | Any command by id |
| `command_batch` | `{steps: [{id, params?}]}` | Stops at the first error: `{completed, results, failed: {index, id, error}}` (a tool error) |
| `project_new` | `{mesh?, resolution?, name?, template?}` | Built-in mesh: material_ball, sphere, cube, rounded_cube, cylinder, torus, plane, crate; `template` names a project template (`project.templates`, listed as `{name, label, builtin, ...}`; the label the New project list shows is "Default (OpenPBR)", "<name> (starter_assets)" or "<name> (your_assets)", and `template` takes the name or the label) |
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
| `textures.export` | `{dir, preset?, ts?, format?, padding?, size?, bitDepth?, dithering?, dilation?, normalFormat?, maps?}` |
| `render` | `{view?, width?, height?, yaw?, pitch?}` → `{width, height, png}` |

Brush preset operations are engine commands. Send each through `command.run` with the shown
`id` and `params`, for example `{"id":1,"method":"command.run","params":{"id":"brush.preset.list","params":{}}}`.

| `command.run` id | `params` and result |
|---|---|
| `brush.preset.list` | `{}` → `[{id, label, category, builtin}]`: the built-in brush presets, then the user's |
| `brush.preset.apply` | `{preset}`: a built-in sets the stroke and keeps the size; a user preset sets the whole brush (size too) and the painted channels |
| `brush.preset.store` | `{name, overwrite?}`: saves the current brush and painted channels as a user preset (desktop and trusted local CLI: a `.tcbrush` file in the data folder's `brushes` folder; browser and untrusted headless MCP/RPC: current session only); an existing name needs `overwrite: true`, built-in names are read-only |
| `brush.preset.rename` | `{name, to}` |
| `brush.preset.delete` | `{name}` |
| `brush.preset.save` / `brush.preset.load` | `{path}`: save the brush as a loose `.tcbrush` file; load a loose or named preset's stroke, keeping the current size and painted channels |

```sh
printf '%s\n' '{"id":1,"method":"command.run","params":{"id":"project.new","params":{"mesh":"torus"}}}' \
              '{"id":2,"method":"render","params":{"width":512,"height":512}}' | texturecraft-cli serve
```

## PBR texture folders

`file.importPbrFolder` turns a folder, a `.zip` or a list of image files of PBR maps into one fill layer
(one undo step), the way `file.importMaterialX` does for a `.mtlx`. `file.scanPbrFolder` takes the same
`path` / `files` and reports what would be used without changing anything. Both are `file.*` commands, so
they run over the control channel and the CLI, not through MCP `command_run` (which refuses `file.*`
commands and host paths).

| Command | Params |
|---|---|
| `file.importPbrFolder` | `{path \| files, name?, normalFormat?: auto\|openGl\|directX, projection?: uv\|triplanar\|planar..., scale?, choose?: {map: file}}` → `{layer, name, maps, candidates, normalFormat, channels, resources, ignored, warnings}` |
| `file.scanPbrFolder` | `{path \| files, name?, normalFormat?, choose?, projection?, scale?}` → `{name, maps, candidates, normalFormat, ignored, channelsAvailable}` |

Maps are found by file name, case-insensitively, from the last known word in the name; resolution
(`2k`, `4096`), bit depth and other tokens are skipped:

| Map (`maps` key) | Words |
|---|---|
| `baseColor` | `basecolor`, `base_color`, `albedo`, `diffuse`, `diff`, `col`, `color`, `bc`, `basemap`, `maintex` |
| `roughness` | `roughness`, `rough`, `rgh` |
| `glossiness` (inverted into roughness; a roughness file wins) | `gloss`, `glossiness`, `smoothness` |
| `metallic` | `metallic`, `metalness`, `metal`, `mtl` |
| `normal` | `normal`, `nrm`, `nor`, `norm`, `normalmap`, `bumpmap`, a trailing `n` |
| `height` | `height`, `disp`, `displacement`, `hgt`, `bump` (weakest) |
| `ambientOcclusion` | `ao`, `ambientocclusion`, `ambient_occlusion`, `occlusion`, `occ` |
| `emissive` | `emissive`, `emission`, `emit`, `glow` |
| `opacity` | `opacity`, `alpha`, `transparency` |
| `orm` (split: R occlusion, G roughness, B metallic; separate files win) | `orm`, `arm`, `ao_rough_metal` |

- **Normal convention.** `gl` / `opengl` in the name is OpenGL, `dx` / `directx` is DirectX (the layer's
  normal source is flagged DirectX, so its green is flipped where it is sampled). With neither the map is
  OpenGL. `normalFormat: openGl|directX` forces every normal map; `auto` (the default) reads the name.
- **Ignored**: other files, dot files and `__MACOSX`, preview images (`preview`, `thumb`, `thumbnail`,
  `sphere`, `render`, `swatch`, `icon`), and maps with no channel here (cavity, curvature, specular...).
  Each is listed in `ignored` with the reason.
- **Several files for one map** (resolutions, formats, GL and DX): the OpenGL normal, then the highest
  resolution token, then the largest file wins. A programmatic call never asks; `candidates` lists the
  alternatives and `choose: {"baseColor": "file.png"}` picks one (the app's dialog shows a drop-down).
- **Where.** A folder's own files if they hold maps; otherwise the one sub-folder that does (several are
  an error that names them). The layer is named after the folder, archive or shared file-name prefix.
  The import reply's `name` is the created layer's unique name, including its numeric suffix.
  A blank `name` uses the same source-derived default as an omitted name.
- **Channels** the texture set doesn't have are skipped with a warning. Projection defaults to UV
  (`scale` 1); `projection: triplanar` is the option for models without good UVs.
- **Hostile input.** Links, pipes and devices are rejected as sources. A scan admits at most 4096
  directory entries (including subdirectories), selected files, or ZIP entries. Folder traversal is
  limited to four levels below the root; exceeding a scan limit returns an error instead of a partial list.
  A file or ZIP entry is at most 256 MiB, an archive 512 MiB, an image 64 Mi texels (320 Mi per import).
  Actual reads are capped even if a file grows. Decoded sources and outputs also share an estimated
  memory budget: one quarter of available memory, capped at 4 GiB (1 GiB for the byte API on the web).
  Compressed inputs already held by the caller and existing project/GPU memory are outside that estimate.
  An image that exceeds the budget or cannot decode is skipped with a warning; if none decodes the
  import is an error that changes nothing. `maps` describes detection; `channels` and `resources`
  describe the successful import. Scan validates import options without decoding pixels.

In the app: drop a folder, a `.zip` or several map files on the window. The dialog shows the maps found,
lets you pick between candidates, set the normal convention and projection, and keep the material in the
library (shelf › Materials). A `.mtlx` added in File › Import Resources is imported as `file.importMaterialX`
does it.

## Smart masks

`mask.smart.list` lists the built-in smart masks and `mask.smart.apply {name, layer?}` replaces a
layer's mask with one. A user smart mask is a layer's mask saved as a `.tcmask` file (the `.tcraft`
container holding one layer with the mask): all effects with their parameters, painted pixels and the
images they read.

| Command | Params |
|---|---|
| `mask.smart.create` | `{layer?, path, name?}`: save the layer's mask (an instance without its own mask saves its source's) to `path` (`.tcmask` is appended if missing, folders are made); `name` defaults to the layer's name. Returns `{path}` |
| `mask.smart.apply` | `{path, layer?}`: replace the layer's mask with the one in a `.tcmask` file (one undo step; images it needs are added to the project, painted pixels are fitted to the texture set) |

In the app: right-click a layer > *Create smart mask* saves into the library folder next to the smart
materials (never over an earlier file), and the shelf lists it under *My smart masks* (Smart masks tab,
*Your assets*): click it or drop it on a layer. Like `material.save`, both forms with `path` are not
available through `command_run` on the MCP server, which rejects host paths.

## Geometry decals

`layer.add.decal {image, ...}` places an image as a decal and `layer.decal.set {layer? | effect?, ...}` edits
one (`command.list` shows every param). Three of them keep the image's look:

- `keepProportions: true` keeps the image's aspect (the decal's current ratio when it shows no image). A
  height (`size: 0.2`) sets the width; a `[w, h]` pair or no `size` sets the height from the width. It acts
  in that call only and is not saved: the desktop Properties panel's "Keep proportions" box (on for every
  decal) sends it with each Width or Height edit.
- `flipU` / `flipV`: mirror the image left to right / top to bottom inside the frame. They are saved with
  the decal (`flip: [u, v]`, left out while both are false, so older projects load and save unchanged).

`layer.add.decal {image, position?, normal?, up?, size?, rotation?, depth?, symmetry?, symmetryFlip?}`
places an image on the surface; `layer.decal.set` moves, resizes or turns it later. `symmetry`
(`x`, `y`, `z` or `off`) adds a mirrored copy on the other side of the mesh: the decal reflected
through the plane across the mesh center, perpendicular to that axis. The copy is part of the
decal, not a second layer, so it follows every later edit and is saved with the project.
`symmetryFlip` (`none`, `u`, `v`) additionally flips the copy's image (U swaps left and right,
V swaps top and bottom). `symmetryOffset` moves the mirror plane along the axis, in world units from the mesh center (default 0, kept within the mesh, as the brush symmetry's offset). With a copy on, each of the three params may be sent alone and keeps the others.
`session.inspect` shows the setting as `decal.symmetry` (`{axis: 0|1|2, flip, offset?}`, absent without
a copy).

## Camera bookmarks

Saved cameras (`Project.cameras`, stored in the `.tcraft` file) are the camera bookmarks.
`camera.add {name?}` saves the current view, `camera.list` lists them (`current` is the one the view
is at), `camera.select {index? | name?}` restores one, `camera.rename {index? | name?, to}` and
`camera.remove {index? | name?}` edit them. `camera.bookmark1` … `camera.bookmark9` (Ctrl+1 … Ctrl+9)
go to the first nine. Commands jump straight to the view; the desktop UI glides there over about a third
of a second.

## Framing the view

`viewport.frame {target?: "all" | "selection"}` points the camera at the bounding box of the whole mesh
(`"all"`, the default, F) or of the active texture set's geometry only (`"selection"`), keeping the
current angles. The orbit pivot (`camera.get` `target`) is the framed center, so `camera.orbit` and the
Alt+drag orbit turn around the object being painted even with a floor plane or other helper geometry in
the mesh. `viewport.frameSelection` (Shift+F) is the same as `target: "selection"`; a set with no triangles
frames the whole mesh. Both return the camera like `camera.get`.
In the app, `viewport.frame` also resets the 2D view (pan, zoom and rotation), as F does, on the next 2D draw. This happens only when the layout is not `Only3D` and the mode is not `Rendering`; otherwise the previous pan, zoom and rotation stay. In a UV tile set the reset frames tile 1001, or the lowest tile when tile 1001 is absent. The engine alone has no 2D view state.

## Camera views and projection

`camera.view {view}` looks at the mesh from one side (`front` from +Z, `back`, `left` from -X,
`right`, `top` and `bottom` at the orbit's ±89° pitch limit) and frames it; the projection stays.
`camera.view.front` … `camera.view.bottom` do the same without params (no default
shortcut, bindable in Settings ▸ Shortcuts). `camera.perspective` (F5) and `camera.orthographic` (F6)
change only the projection; position and rotation stay. None of them is an undo step. In the 3D
view, Alt+Shift+left drag orbits in 90° steps.

`camera.rotation {mode: constrained|free}` (or `camera.rotation.constrained` / `camera.rotation.free`,
the rotation dropdown of the top bar) picks the orbit: constrained (the default) keeps
the horizon level and stops at the poles; free is a trackball that turns the camera about its own axes,
so the model can be turned over and rolled. `camera.get` shows it as `rotation`; `camera.set` takes
`rotation` too. Switching keeps the direction of view; going back to constrained drops the roll.
Views saved in free mode restore their roll while free rotation is active. Older cameras and cameras
saved in constrained mode restore from yaw and pitch. Fixed views and `camera.set` yaw/pitch put a
free camera level. `camera.snapRotate {yaw?, pitch?}`
(whole 90° steps; the angles first go to the nearest step) is the command behind the Alt+Shift+left drag
("Camera snap rotate"); `camera.snapRotate.left|right|up|down` are its menu forms. `camera.next` and
`camera.previous` go to the next or previous saved camera (wrapping; from a view that is no saved
camera, the first or the last). The commands have no default keys and are bindable in Settings ▸ Shortcuts.
None is an undo step.

`display.set` also takes `alignment` (`world` or `camera`: the environment, and the key light with it,
turns with the camera about the vertical axis), `shadowMode` (`intensive`, `average` or `lightweight`, the
default: the shadow map's resolution) and `shadowOpacity` (0 to 1, default 1: how dark the shadows are).

`viewport.view {mode: "image", image: <image resource>}` shows a project image as it is, stretched over
the UV square, on the mesh and in the 2D view (the view picker's "Other..."). `display.set {soloUnlit}`
(default true) says whether a single-channel view is flat; off, Base color, Metallic, Roughness, Normal
and Height are shaded on a lit neutral material in the 3D view. `viewport.nextChannel` and
`viewport.previousChannel` (C, Shift+C) visit the set's channels, then "Normal+height+mesh", and wrap.

`viewport.view {mode: "normalHeightMesh"}` is the combined "Normal+height+mesh" view: the surface normal
the shading uses (mesh normal, Height channel slope and Normal channel), unlit; the 2D view shows its
tangent-space form.

## Colour swatches

The project's swatches (`Project.swatches`, linear RGB, stored in the `.tcraft` file; projects without any
save none) are the Swatches row under the colour picker. `swatch.list` lists them, `swatch.add {color}`
(`[r, g, b]` linear or `"#rrggbb"`, clamped to 0..1, at most 64) adds one at the end and
`swatch.remove {index}` removes one; `project.inspect` shows them as `swatches`. Applying a swatch is an
ordinary colour edit (`layer.fill.set {color}`).

## A fill's whole material

A fill layer or content fill effect can hold one built-in plain material whole (the Material side of
its Material section). `layer.fill.material {layer? | effect?, material}` sets every channel the
material writes from it, turns those channels on and the others off, and keeps the fill's projection;
`material: null` returns the channels to their defaults (a content fill effect keeps the channels it
changes, at their defaults); setting what the fill already holds adds no undo step. Smart materials (folders of layers) are added
with `material.apply` instead. The command rejects linked MaterialCraft fills. The fill remembers the material (`Fill.material`, saved only when set;
`project.inspect` shows it as `material`) until a channel's source is set on its own with
`layer.fill.set`. A plain material added from the shelf names its fill the same way.

## Folders, effect blending and masks

- `folder.contents.set {layer?, scale?, rotation?}` lays a Scale (multiplying every fill's tiling inside)
  and a Rotation (degrees added to every fill's angle) on a folder's contents, never written into the fills;
  `folder.contents.reset {layer?}` drops them and puts back the seeds `folder.randomizeSeeds {layer?}` changed.
  `folder.randomizeSeeds` gives every pattern, generator and noise filter inside a new seed (seeds that were
  equal stay equal) and returns `{seeds}`, how many changed.
- `effect.blending.modeToEveryChannel`, `opacityToEveryChannel` and `bothToEveryChannel {effect?, channel?}`
  give every channel of a content effect one channel's blend mode, opacity or both; `effect.blending.copy`
  and `effect.blending.paste {effect?}` carry every channel's blending between effects (a mask effect takes
  the shared one). `effect.set {effect, channel, blend?, opacity?}` sets one channel's blending and
  `effect.set {effect, channels: {roughness: false}}` switches a content effect's channels on or off.
- `mask.add.bitmap {layer?, image | alpha, projection?}` adds a mask fill reading an image's gray;
  `effect.set {effect, idMap: image resource | null}` gives a colour selection its own ID map in place of
  the baked one; `tool.material {maskImage: image resource | null}` paints an image's gray into masks.
- `effect.add.colorSelection {layer?, color?, tolerance?}` and `mask.add.heightCombination {layer?}` add a
  colour selection or a compare mask (this layer's height against the layers below) to a layer's mask,
  making the mask first when it has none; both return `{effect}`.
- `effect.filter.restoreDefaults {effect?}` puts a filter's parameters back to its defaults (name,
  channels and blending stay) and returns `{changed}`.
- `layer.fill.resetProjection {layer? | effect?}` puts the Fill section back to a new fill's (same
  projection kind; a placed frame, the symmetry and the sources stay); `layer.fill.resetFrame` puts a
  warp's frame back around the mesh with its corners unpulled. Each is one undo step, or none when
  nothing changes.

## MaterialCraft materials

A v3 `.mcmat` holds a published SBS graph and its source assets. TextureCraft uses the shared `craft-mcmat` reader and cooks the archive through `materialcraft-cli`. The resulting fill stores its channel textures and the original archive in the project. Linked cooks use the Settings percentage of available RAM. A cook that exceeds the estimated budget reports the required and configured byte counts without replacing the current fill. Its exposed values, presets and mesh-map inputs appear in `project.inspect`. Republish older MCMAT files from their original authoring project. Procedural imports and re-cooks require the desktop CLI. Saved projects retain their baked maps for use in the browser.

Saving and linked cooks share one reservation for the configured RAM allowance. Autosave waits
until a cook releases the reservation. An explicit save or cook that conflicts with the other
operation returns a busy error and can be retried.

| Command | Params |
|---|---|
| `material.load` | `{path, above?, inside?, index?}`: `.tcmat`, `.mcmat` or `.mcraft` (cooked first) |
| `material.link.set` | `{layer?, id, value, cook?: true}`: a number, `[..]`, a bool, `"#rrggbb"` or a typed `{"t", "v"}`; re-cooks unless `cook: false` |
| `material.link.preset` | `{layer?, name, cook?: true}` |
| `material.link.map` | `{layer?, channel, output}`: the channel reads another output of the material |
| `material.link.resolution` | `{layer?, relative: -3..3 \| fixed: 128..8192, cook?: true}`: the size the material cooks at |
| `material.link.cook` | `{layer?}`: re-cook at its picked resolution (default: the texture set's) with its baked mesh maps (after a bake or a resize) |
| `material.link.saveSource` | `{layer?, path}`: the original linked source with its `.mcmat`, `.mcraft` or `.sbs` extension |

For a 1024-pixel texture set, TextureCraft requests `materialcraft-cli export source.mcmat maps --profile maps --size 1024x1024` with repeated `--set` and `--input` arguments. It discovers the published image inputs through `info` when the texture set supplies mesh maps. The desktop worker decodes the returned maps before installing the fill at its original drop target. The executable is resolved from
`$MATERIALCRAFT_CLI`, else `materialcraft-cli` next to the TextureCraft executable, else on `PATH`
(the app is `$MATERIALCRAFT` / `materialcraft`). Baked maps feed graph input nodes whose identifier
matches the map's shared id (`ambientOcclusion`, `curvature`, `thickness`, `position`,
`worldNormal`, `normal`, `height`, `id`, `bentNormal`, `opacity`, `colorMap`, `worldDirection`;
case and underscores ignored; `normal` and `bentNormal` are tangent space, OpenGL green). Usages
map to channels of the same id (`baseColor`, `normal` in OpenGL convention, `roughness`, `metallic`,
`height`, `ambientOcclusion`, `emissive`, `opacity`, `specular`); missing channels join the texture
set.

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
