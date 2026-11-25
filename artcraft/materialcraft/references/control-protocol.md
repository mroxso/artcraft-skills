# Control protocol and MCP

> **Last reviewed:** 2026-11-02 · **Last updated:** 2026-11-03 · **Change:** minor (`material_export` MCP tool) · **Target:** the professional node-based material workflow

Agents drive MaterialCraft three ways, all dispatching the same engine commands:

1. **MCP** (`materialcraft-cli mcp`): headless (an in-process session, files only below
   `--read-root` / `--write-root`, also spelled `--automation-read-root` /
   `--automation-write-root` as in the other crafting apps; `serve` takes them too) or bridged to the running app (`--bridge <port>`).
2. **JSON lines** (`materialcraft-cli serve`): the same methods on stdio, or on `127.0.0.1:<port>`
   behind a token.
3. **The app's control channel** (`materialcraft --control <port>`): one JSON request per line,
   `{"id", "method", "params"}` → `{"id", "ok": true, "result"}` or `{"id", "ok": false, "error"}`.
   The first request must be `{"method":"auth","params":{"token":"…"}}` with the token from
   `MATERIALCRAFT_CONTROL_TOKEN` (16 to 1024 printable ASCII characters) or the file
   `<temp>/materialcraft-control-<port>.token`, a fresh random 256-bit token written after the port
   is bound. On Unix the file is created new with mode 0600 (owner only); if an existing file there
   cannot be replaced, the control server stays off and `MATERIALCRAFT_CONTROL_TOKEN` is the
   alternative. Clients (`materialcraft-cli mcp --bridge`) refuse a token file that is a symlink,
   not a regular file, not owned by them, or accessible to group or others. A connection gets one
   authentication attempt, within 10 s; a wrong token, any other first request or malformed JSON
   closes it. At most 16 connections are served at once. Whoever holds the token has full
   engine-command authority, including host file access.
   Set `MATERIALCRAFT_NO_PREFS=1` for scripted runs so the user's layout is left alone.

The first SBS save sets `formatVersion` and `updaterVersion` to MaterialCraft's workspace release
version. Later saves preserve the document's original `formatVersion` and refresh `updaterVersion`
to the saving application's release version. Save As and archive packaging retain that baseline too.

## Methods

| Method | Where | What |
|---|---|---|
| `ping` | all | `"pong"` |
| `command.list {filter?}` | all | every command: id, label, menu, shortcut, params doc, enabled |
| `command.run {id, params?}` | all | run one command (programmatic: never opens a dialog) |
| `command.batch {steps}` | headless | run `[{id, params}]` in order, stop at the first error |
| `session.inspect` | all | package, graphs, the open graph's nodes (def, params, bindings, base, ports, cook error/size/mean/ms), wires, frames, comments, pins, exposed inputs, views, history |
| `package.open {path}` / `package.save {path?}` | headless | workspace-scoped package I/O |
| `bitmap.import {path, name?}` | headless | embed an image as a resource |
| `outputs.export {dir, format?, pattern?, depth?, size?, graph?, outputs?, colorSpaces?, profile?, preset?, values?, inputs?, normalFormat?, displacementScale?}` | headless | cook at full size and write the outputs: `size` is the larger side or `[width, height]`, `outputs` lists identifiers (default all), `colorSpaces` maps identifiers to `srgb`, `linear` or `raw` (default by usage) |
| `material.export {path, graph?}` | headless | write a portable `.mcmat` below the write root |
| `render {view?, width?, height?, yaw?, pitch?, scene?, node?, port?, full?, tiling?, hq?, displacement?}` | headless | PNG (base64) of the 3D view or of one node; `hq` is the beauty render (displaced mesh, ray-traced AO, shadowed key light, 3×3 supersampling), `displacement` its depth in scene radii |
| `ui.inspect` | app | UI state, the graph view rectangle, every node's screen rectangle, every port's identifier, display label and screen position, fps, toasts |
| `ui.menu.list` / `ui.menu.invoke {id}` | app | the menu catalog; behave like a click. While a dialog or prompt is open (an app dialog, the unsaved-changes prompt, a file dialog, or the update prompt or result window; not Home, the Shortcuts list or the notice that an update installed), an item lists as disabled and `ui.menu.invoke` returns an error. When a file dialog is the only one open, the items that show a file dialog stay enabled and bring it forward |
| `ui.set {...}` | app | recursively merge fields into the UI state |
| `ui.input {events}` | app | synthetic input, below |
| `view.screenshot {view?: "3d"\|"2d"}` | app | PNG of the 3D or 2D view |
| `ui.screenshot` | app | PNG of the whole window |
| `ui.resize {width, height}` | app | window size in points |

### Undo preferences and document history

`session.history {undoLimit?}` reads or sets the number of retained undo steps per package
(1–10,000; default 200). This is an app preference, independent of SBS contents. The desktop and
web app expose it under **Edit → Preferences → Undo history (steps)** and persist it with UI
preferences (`prefs.history.undoLimit`). Changing it applies to every open package and future
edits; lowering it drops the oldest excess states from the undo and redo stacks.

`edit.undo {document?}` and `edit.redo {document?}` default to the active package. An explicit
document id operates on that package without switching the canvas. UI Undo/Redo target the
package whose graph is being inspected in Explorer, or the canvas package when no graph is
being inspected.

### Synthetic input (`ui.input`)

Events are applied one frame at a time, so egui sees real presses, drags and releases. Positions are
window points (take them from `ui.inspect`'s `nodes` and `ports`).

```json
{"method": "ui.input", "params": {"events": [
  {"type": "drag", "from": [512, 140], "to": [600, 220], "steps": 12},
  {"type": "click", "pos": [700, 300], "button": "left", "modifiers": ["ctrl"]},
  {"type": "doubleClick", "pos": [640, 180]},
  {"type": "scroll", "pos": [640, 300], "delta": [0, -120]},
  {"type": "key", "key": "Space"},
  {"type": "text", "text": "perlin"},
  {"type": "key", "key": "Enter"}
]}}
```

Types: `move`, `down`, `up`, `click`, `doubleClick`, `drag`, `scroll`, `key` (egui key names:
`A`, `Enter`, `Space`, `Delete`, `F5`, …), `text`. Buttons: `left`, `right`, `middle`.

## Key commands

| Command | Params |
|---|---|
| `graph.function.variables` | `{id, target?: FunctionGraphTarget}` returns ordered suggestions matching a Get node's type and caller scope; typed custom names remain supported |
| `session.environment` | `{timeSeconds?, uvTile?: [int, int], normalFormat?: int}` updates host evaluation values without modifying the package; `{}` reads them; defaults are zero and the normal-format code is passed through |
| `graph.context` | `{physicalSize?: [x, y, z], pixelRatio?: 0\|1, tiling?: [horizontal, vertical]}` edits material-graph metadata with undo; `{}` reads it; reusable functions receive their caller's context |
| `file.new` | `{template?, name?, folder?, kind?, size?, height?, document?, newPackage?}`. Use `graph.templates` for the supported material templates. `size` is the width in pixels and `height` defaults to it (powers of two, 16 to 8192). `document` selects an open package. `newPackage: true` creates a new untitled package and cannot be combined with `document` or a nonempty `folder` |
| `graph.node.edit` | `{}` resolves the selected FX-Map, processor or graph instance to `{kind, node, parameter?, graph?, document?, path?}`; use `ui.menu.invoke` to open its reference in the graph panel |
| `graph.node.info` | `{id}` returns `{text}` describing a main-graph node without changing the document or node clipboard |
| `graph.instance.add` | `{document, graph, function?: FunctionGraphTarget, at?, snapToGrid?}` adds a linked graph instance from an open package; requires a source output and rejects dependency cycles |
| `package.activate` | `{document}` activates an open package while retaining each package's selection, views and undo history |
| `package.close` / `package.closeAll` | `{document?, discard?}` / `{discard?}` closes one/all packages; modified packages require explicit discard |
| `folder.create` / `folder.rename` / `folder.remove` | `{parent?, name?}` / `{folder, name}` / `{folder}` edits SBS folders, including empty folders; removal includes descendants and supports undo |
| `explorer.copy` / `explorer.paste` | `{graph? index, folder?}` / `{folder?}` copies a graph, folder subtree, or package contents and pastes into a folder or the package root; internal references follow the copies |
| `explorer.move` | `{graph? index, folder?, parent?}` moves a graph or folder within the active package and updates local graph references |
| `file.reload` | `{discard?}` reloads the active document in place; unsaved changes require explicit discard |
| `file.saveCopyAs` | `{path}` writes a copy without changing the active document's path, modified flag, or history |
| `graph.pattern.set` | `{id, pattern}` replaces an FX-Map subgraph with cycle validation and undo |
| `graph.node.add` | `{def, at?, params?, connectFrom?: {node, port?}, label?}` |
| `graph.connect` / `graph.disconnect` | `{from, fromPort?, to, toPort?}` / `{to, toPort}` |
| `graph.wire.insertDot` | `{to, toPort, at?}`: split the wire feeding `to.toPort` with a reroute Dot node at `at` (graph point, default midway), selected |
| `graph.wire.swap` / `graph.wire.delete` | `{wires: [{to, toPort}, ...]}`: exchange the sources of exactly two wires / delete any listed wires, one undo step each |
| `graph.node.param` | `{id?, param, value}`: numbers, `[x, y]`, `"#rrggbb"`, enum index, curve `[[x, y], …]`, gradient `[[pos, color], …]`, or a typed value `{"t": "function", "v": {...}}` |
| `graph.node.base` | `{id?, param, value?, inheritance?}` edits one base parameter; legacy `{sizeMode?, size?, format?, seed?, tiling?}` fields remain supported |
| `graph.exposed.prepare` | `{bind: {node, param}, default?}` returns editable input settings without changing the graph; only Specific Parameters can be exposed |
| `graph.exposed.add` / `graph.exposed.set` | `{id?, label?, group?, description?, default?, min?, max?, editor?, clamp?, step?, bind?: {node, param}}` (with `bind`, `id` may be omitted: `opacity`, `opacity_1`…) / `{id, value}`; `editor` is `slider`, `input`, `color`, `dropdown`, `toggle` or `text`, subject to the parameter type |
| `graph.node.function` | `{id?, param, base?, mode?: empty\|constant, value?, function?, remove?}` attaches an owned parameter function; constant creation captures its current value, or uses the supplied `value`; empty creation has no output |
| `graph.node.bind` | `{id?, param, base?, input}` attaches a typed input function; `input: null` clears the driver |
| `graph.node.function.edit` | `{id?, param, base?}` resolves the function target and opens it when dispatched by the UI |
| `graph.node.parameterInfo` | `{id?, param, base?}` returns the expected type, current value or error, function, input link, inheritance and warnings |
| `graph.node.reset` | `{id?, param?, base?}` removes the driver and restores defaults; omit `param` to reset the selected parameter section |
| `graph.preset.save` / `.apply` / `.delete` | `{name}`: store, restore or remove the current input values |
| `graph.createFromSelection` | `{name?, ids?}`: move nodes into a sub-graph and replace them with an instance |
| `view.2d` | `{node?, port?}` picks what the 2D view shows. Display: `channel` (`rgba`\|`r`\|`g`\|`b`\|`a`), `tiled` (repeat the image across the view), `checkerboard` (behind transparent pixels, else black), `premultiplied` (colors already multiplied by alpha), `srgb` (values are sRGB encoded, the default; false shows them as linear light), `physicalSize` (proportions of the graph's physical size), `maintainZoom` (keep the zoom when the image size changes, the default; false keeps the image's size on screen), `uv` (overlay the UV layout of the 3D view's mesh), `background` (an image file drawn behind transparent pixels, or null). Information panel: `information`, `sampler` (`[x, y]` in 0..1 from the top-left corner, or null). Histogram panel: `histogram`, `histogramChannel` (`luminance`\|`red`\|`green`\|`blue`\|`rgb`\|`alpha`), `histogramBits` (8\|16\|32; 0 follows the image), `histogramSqrt`, `histogramSelection` (`[low, high]` in 0..1, or null). A rejected parameter changes nothing; the result and `session.inspect` (`view2d`) hold every setting. Pan and zoom are UI state: `ui.set {imageCamera: {zoom, offset, fit}}` |
| `view.3d` | Every setting of the 3D view, each optional; the reply is the whole view. See [3D view settings](#3d-view-settings) |
| `view.3d.viewpoint` | `{name}`: `default`, `front`, `right`, `back`, `left`, `top` or `bottom` turns the camera to look from there, at the same distance |
| `view.3d.frame` | `{}` centers the mesh and moves the camera to where all of it is in view |
| `view.3d.resetCamera` | `{properties?}` puts the camera back where a new view has it; with `properties` also the lens, projection, background, resolution and clip planes |
| `view.3d.resetLights`, `view.3d.resetEnvironment` | `{}` the lights, or the environment, of a new view |
| `view.3d.resetMaterial` | `{common?}` puts the material model back to its defaults; with `common` only the parameters several shaders share, and the shader stays. The assigned images stay |
| `view.3d.saveDefault` | `{}` makes the current view the one `view.3d.reset` and a new package start from. The app keeps it in its preferences |
| `view.3d.saveState`, `view.3d.loadState` | `{path}` writes the view's settings to a `.mcview` file (JSON); `{path, mesh?}` applies one, switching to its mesh only with `mesh`. Numbers out of range are clamped; a file that is not a state changes nothing |
| `view.3d.reset` | `{}` back to the saved default view, or the built-in one |
| `view.3d.loadMesh` | `{path}` shows an OBJ, glTF or GLB mesh (scene `custom`) |
| `library.list` | `{filter?, category?}`: every node with ports and parameters |
| `library.tree` | `{filter?, category? (Top or Top/Sub), canvas? (material\|function\|pattern)}`: the Library panel's category tree and its entries. Each entry has `id`, `label`, `category`, `type` (`node`, `comment`, `frame`, `pin`, `instance`, `operation`, `functionInstance`, `pattern`, `bitmap`), the `canvas` that takes it (`any` for shared graph items), `missing` when MaterialCraft lacks the library package it needs, and `warning` when it can be added but is incomplete |
| `library.add` | `{entry, at?, snapToGrid?, function?: FunctionGraphTarget, pattern?: owner node id}`: add a `library.tree` entry to the open graph (function entries to a Function canvas; FX-Map nodes use `graph.pattern.edit`). Entries with `missing` refuse with the reason |
| `library.reload` | `{}`: read the SBS library folder again |
| `graph.cook` | `{full?, graph?: index}`: cook now and return per-node timings and errors; another material graph of the package cooks at full size into the cache |

## Node library

Every `.sbs` file in the library folder (`assets/sbs`, or `MATERIALCRAFT_SBS_DIR`; installed and
browser builds embed all library packages and shared resources) loads once per process, and its graphs join every
session's dependencies. Function graphs are listed under Functions using recognized Tags, then
Category or package-path fallbacks (`Functions/colorValues` → Color, `Functions/easings` → Easings).
Other graphs use the category in their attributes. A package whose graphs group nodes in titled frames lays the library
out instead: a frame titled `Top - Sub` (or `Top`) is a Library category, and every node inside it
becomes an entry there, `missing` until its package is in the folder. Function frames name only the
sub-category. The older category name "SDF functions" reads as MCF functions.

## Linked packages

Opening an SBS file or creating a package retains the other open packages. `session.inspect`
includes `documents` with each package's document id, path, active state, modified state and graphs.
Explorer graph drags use that document id and graph name with `graph.instance.add`.

A single click on an Explorer graph inspects its properties without changing the open canvas.
Regular graphs currently show Identifier and Label in Attributes; function graphs show the full
attribute form.
`graph.properties`, `graph.attributes`, and `graph.rename` accept optional `document` and `graph`
targets, including graphs in inactive packages. Attribute edits use `label`, `description`,
`category`, `author`, `authorUrl`, `tags`, `group`, and `userData`; the identifier uses
`graph.rename` with `name`. Labels are display text, while identifiers remain the SBS reference
names. Graph metadata is saved in native SBS attributes for both material and function graphs.
Edits belong to the target package's undo history. Size, format, and seed commands accept the same
optional targets.

Main graphs with outputs can be instanced in other main graphs. Cross-file sources must be saved
first; the target stores a file reference and connector metadata, not a copy of the source nodes.
Unsaved source edits update open instances and mark dependent packages modified, including
transitive dependencies. Each package keeps its own undo history. Native reopening resolves saved
file references even when the sources are not open in Explorer. Missing source files retain their
cached connectors and wires and report a cook error.

Function Graphs with designated outputs can be instanced in Function canvases, including Pixel
Processor, Value Processor and parameter functions. Pass `function` for embedded canvases; the
active standalone Function Graph is inferred when it is omitted. FX-Map canvases reject instances.
The source's exposed inputs become typed connectors; missing connections warn when the instance
feeds the designated output. An instance can itself be designated as the output. Function calls
retain separate variable scopes and share the evaluator's execution budget.

`graph.instance.reference {id, function?: FunctionGraphTarget}` resolves the source document, path
and graph index without changing the package. The UI's Open reference action uses this command
and retains the parent Function/processor canvas for return navigation. Double-clicking an instance
has no additional action, and Ctrl+E does not open its source. Ctrl+E still opens the embedded canvas
of a Pixel Processor, Value Processor or FX-Map node.

Source-file watching is not implemented yet. The global Function Library reads `sbs://functions.sbs`.
References currently identify graphs by name; renaming an external source graph requires recreating
its instances. Save As creates a separate file and does not redirect references to the original.

## 3D view settings

`view.3d` takes any of the settings below and leaves the rest as they are. A number out of range
is held at the nearest limit; an unknown name (a scene, a shader, a material parameter) is an error
and changes nothing. One mesh unit is 50 scene units; a built-in mesh is 100 across, one meter.

| Group | Parameters |
|---|---|
| Scene | `scene` (`cube`, `cylinder`, `hollow_box`, `inner_box`, `plane`, `plane_hi_res`, `sphere`, `cloth`, `material_ball`, `rounded_cube`, `rounded_cylinder`, `sphere_2_tiles`, `torus`, or `custom` after `view.3d.loadMesh`) |
| Camera | `yaw`, `pitch` (degrees), `distance` (mesh radii), `target` (`[x, y, z]` in mesh radii from the center, within the pan limit preference), `focalLength` (mm on a 36 × 24 frame, 0.01 to 100), `projection` (`perspective`, `orthographic`), `background` (`studio`: a gray backdrop that darkens toward the corners, the default; `color`; `environment`), `backgroundColor` (linear `[r, g, b]`, for `color`), `autoClip`, `nearClip`, `farClip` (scene units) |
| Render resolution | `overrideResolution`, `viewportResolution` (start from the view's size), `renderResolution` (`[width, height]`, 16 to 4096), `renderScale` (25, 50, 100 or 200 percent). A resolution of its own is shown fitted in the view, with bars around it |
| Environment | `environment` (`studio`, `sunset`, `overcast`, `night`), `envEnabled` (it lights the scene), `envRotation` (degrees), `exposure` (stops, -10 to 10) |
| Lights | `ambient` (`{enabled?, color?}`), `light1`, `light2` (`{enabled?, color?, intensity?, yaw?, pitch?, distance?}`: a point light that orbits the scene's center), `shadows` (the point lights cast them) |
| Display | `wireframe`, `backfaceCulling`, `axis` (the world axes with a scale), `grid`, `boundingBox`, `lightHelpers`, `vertexTangentSpace`, `sceneStats`, `resolution`, `fps` |
| Material model | `shader` (`openPbr`, `blinn`, `lambert`, `meshInfo`, `metallicRoughness`, `metallicRoughnessCoated`, `metallicRoughnessSss`, `specularGlossiness`, `unlit`), `technique` (`tessellation`, `parallax`: how the height output shows), `meshInfo` (`normal`, `tangent`, `binormal`, `uv`, `uvTile`, `vertexColor`, `position`) |
| Material values | `material` (`{parameter: number, [r, g, b] or bool}`; `null` puts a parameter back to its default), `channels` (`{parameter: bool}` switches a parameter, and the image a graph output gives it, on or off) |
| UVs | `tiling`, `uvScale` (`[u, v]`), `physicalSize` (size the material by the physical size of its graph: a graph a meter wide covers a built-in mesh once) |
| Height | `displacement` (raise the mesh), `heightScale` (mesh radii, 0 to 0.5), `heightLevel` (the height that stays on the surface; 0 = the relief rises out of it), `tessellation` (1 to 8), `normalYFlip` (DirectX normal maps; default false, OpenGL) |
| Renderer | `samples` (rays per pixel side of a resting frame, 1 to 4), `ambientOcclusion` (rays, 0 to 32), `transparency` (see through where the alpha is below one), `alphaView` (show the alpha channel), `viewChannels` (`rgb`, `r`, `g`, `b`), `colorSpace` (`aces`, `srgb`) |

The material parameters follow the public OpenPBR Surface model: `baseWeight`, `baseColor`,
`baseMetalness`, `baseDiffuseRoughness`, `specularWeight`, `specularColor`, `specularRoughness`,
`specularAnisotropy`, `specularIor`, `transmissionWeight`, `transmissionColor`, `subsurfaceWeight`,
`subsurfaceColor`, `subsurfaceRadiusScale`, `coatWeight`, `coatColor`, `coatRoughness`, `coatIor`,
`coatDarkening`, `fuzzWeight`, `fuzzColor`, `fuzzRoughness`, `emissionLuminance`, `emissionColor`,
`thinFilmWeight`, `thinFilmThickness`, `thinFilmIor`, `geometryOpacity`, `geometryNormal`,
`ambientOcclusion` and `height`; the glossy shaders add `specular` and `glossiness`. Each shader
lists the parameters it shades with. `transmissionDepth`, the dispersion values, `subsurfaceRadius`,
`subsurfaceAnisotropy`, `coatAnisotropy`, `geometryThinWalled` and the Phong tessellation values are
kept with the state, but the CPU renderer does not show them.

In the app the view's menus (Scene, Materials, Lights, Camera, Environment, Display, Renderer) and
its tool strip run these commands, and Edit properties shows the material, the lights, the camera,
the environment or the renderer in the Properties panel. Over the view: drag orbits, the middle
button (or Alt+drag, or Ctrl with the right button) pans, the wheel and the right button zoom,
Shift+drag turns the environment, Ctrl+Shift+drag (or the Light tool) moves the first point light,
Shift+click (or the Select tool) selects the mesh; F frames, R puts the camera back, Shift+R also
puts its properties back (with the Light tool: the light's position), Alt+S saves the render, Alt+C
copies it, C and L pick the Camera and Light tools.

## 3D material assignment

`view.3d.outputs {graph?, reset?}` applies a material graph's image outputs by their usage.
`graph` accepts an index or name and defaults to the open graph. Ordinary application preserves
unmatched channel assignments; `reset: true` clears them while preserving the scene, camera and lighting.
Outputs with unsupported usages or scalar/vector results cannot supply material textures.

`view.3d.assign {graph?, node?, port?, channel, reset?}` assigns an individual image to `baseColor`,
`normal`, `roughness`, `metallic`, `height`, `ambientOcclusion`, `emissive` or `opacity`.
The node defaults to the selection only in the open graph. The port accepts an identifier or index;
terminal Output nodes use `output` or index 0. Assignments refer to their source graph and named port,
update when that source changes, and remain active while editing a Function Graph.
`view.3d.clear {}` removes assignments without resetting the scene.

Opening a material graph automatically previews its output usages. Selecting or previewing a node
in 2D does not reassign the 3D material. Dragging a graph from Explorer onto the 3D view applies its outputs without opening the graph.
Canvas and Explorer context menus use the same assignment
commands; the 3D view's material properties mark each parameter a graph output feeds. A Height-only output affects height
sampling, not Base Color; assign that image to `baseColor` to inspect its grayscale pattern on the mesh.

`session.inspect.material3d` reports assignments and resolved channels, including source graph/node/port,
image dimensions and mean values. Assignment commands leave the package and document undo history
unchanged. Document undo restores the associated source references; replacing a package clears them.

## Function graphs

`file.new {"kind": "function", "name": "Calculation"}` creates a standalone Function Graph.
Omit `kind`, or use `"material"`, for a Graph. `graph.function.set {"function": {...}}` replaces
the active standalone function through one validated, undoable command.
Both `graph.function.set` and `graph.function.edit` accept an optional `target`: `{"kind":"graph"}`
(the default), `{"kind":"parameter","node":12,"parameter":"function"}`,
`{"kind":"dynamic","node":12,"parameter":"opacity"}`,
`{"kind":"base","node":12,"parameter":"outputsize"}`, or
`{"kind":"pattern","owner":12,"node":3,"parameter":"patternrotation"}`.

Base function identifiers are `outputsize` (Integer2), `pixelsize` (Float2), and `format`,
`pixelratio`, `tiling`, `randomseed` (Integer). Their inheritance is independent of the driver.
`graph.node.base {id, param, inheritance}` changes inheritance while keeping its function;
add `value` to replace the function with a literal. Output size uses log2 dimensions in absolute
mode and log2 offsets in relative modes. Its relative-mode function reads the inherited nominal
`$size` and `$sizelog2`, before preview limits. Instances pass their resolved size to their child graph.
Exposing or binding a parameter creates an editable, typed Get-node function. Literal edits and
reset remove the old driver. Native parameters and instance inputs require their declared output
type; color parameters use Float4 and enum parameters use Integer. Invalid functions remain editable
and cook with a diagnostic. `session.inspect` includes evaluated `base`, `baseValues` and `parameters`
in each node's `cooked` result; `parameters` contains scalar and vector values, while authoring
graphs and curves remain in `params`. `baseValues` is populated for nodes with base functions.

`graph.function.edit` accepts `edit: {action: add|move|connect|value|output, ...}`.
Explicit output selection rejects a type incompatible with the target parameter. Existing
functions with mismatched output types remain editable and report the mismatch in
`graph.functionWarnings`; this includes a Pixel Processor whose color mode has changed.
For example, `{"edit":{"action":"add","operation":"mul","at":[256,0],"snap":true}}`
creates and returns a node ID using the same defaults as library and context-menu insertion.
Adding an operation leaves the function's output unchanged. Use
`{"edit":{"action":"output","id":12}}` to designate its single output node; deleting that
node clears the designation. These edits support undo for every Function target.
Dot nodes cannot be designated as outputs, including through commands.
`session.inspect` reports incomplete functions in `graph.functionWarnings`, with a `target` and
`messages` for each affected function. It warns when no output is defined or no input path from
the output reaches a value source such as a constant or variable input. One such path is enough;
unused nodes and other unconnected pins do not warn. A constant output needs no input connection.
Warnings do not prevent editing or saving, including inside Pixel Processor and Value Processor nodes.
`graph.function.node.info {id, target?}` returns a `text` field with the node's operation, values,
connections and output designation. The node context menu copies this text to the system clipboard;
the document, undo history and node clipboard remain unchanged.
`graph.wire.swap {function?, pattern?, wires: [{to, toPort}, {to, toPort}]}` exchanges the
sources feeding any two selected links across all graph canvases. For functions, pass a
`FunctionGraphTarget` in `function` and a zero-based input index string in `toPort`. For FX-Map,
pass the owner node ID in `pattern`; `to` is the internal parent and `toPort` its child port
(`output0`, `output1`, or `output` for a Dot). The command preserves other connections, rejects
cycles atomically and supports undo. `graph.wire.delete` uses the same target and wire addresses.
Click a link and Shift-click another, then use **Swap links** or **X**. The menu action appears
only when exactly two links from different output pins are selected, independently of node selection.
Two links from the same output pin are rejected without changing the document or undo history.
Main-graph swaps also apply the normal input type checks to both replacement connections.
Equal values from different output pins remain eligible. `ui.inspect` exposes
embedded selections as `subgraph.selectedWires`.
`graph.pattern.edit` accepts the FX-Map owner `id` and
`edit: {action: add|move|connect|disconnect|root|value, ...}`.
Use `command.list` for command descriptions and the serialized `FunctionEdit`/`PatternEdit` types
in `crates/engine/src/` for the action fields. Value edits are individual undo steps by default;
`merge: true` groups repeated updates to the same target and value until `edit.finish` or another
edit ends the group. Idle UI frames preserve explicitly requested automation groups.

`ui.menu.invoke` sends selection actions to the focused editor, including embedded Function
windows. `ui.inspect.subgraph.target` identifies that Function target; its canvas rectangles and
ports correspond to the same editor. Raw `command.run` calls retain their explicit command targets.


Selection and clipboard commands (`graph.select`, `edit.selectAll`, `edit.copy`, `edit.cut`,
`edit.paste`, `edit.duplicate`, `edit.delete`, their without-link/relink variants and upstream/downstream
selection) also work without a UI. They infer the active standalone Function Graph. To address an
embedded graph, pass `function: <FunctionGraphTarget>` or `pattern: <owner node id>` and explicit
`ids` for selection-dependent operations. `edit.selectAll` returns those IDs. An optional numeric
`graph` guards against the owning graph no longer being active. `graph.align` accepts the same
Function and FX-Map targets with explicit IDs.

Results include `ids` and `selected`; copy/cut also return `copied` and a typed `clip` accepted by
paste. In the app, Copy and Cut from a menu, a shortcut or `ui.menu.invoke` also put that `clip` on
the system clipboard, because the desktop sends no Paste event while it is empty; `command.run`
leaves the system clipboard alone. The session retains the most recent embedded clipboard. Cross-target paste keeps internal
links and drops external links. Standalone commands update the session selection; embedded commands
return their selection without changing the parent selection. Invalid operations preserve the
document, clipboard, selection and undo history. Creation and all function/pattern setters share
cycle, capacity, ID and position validation.


A function has `nodes` and an optional `output` node id. Each node has `id`, native `op`,
`inputs` (source ids or null for unwired ports), optional `value`, `type_code` and `pos`. Function instances use `op: "instance"` and
`instance: {package, graph, inputs, outputs}`; resolved call bodies are runtime-only.
For example, `const_float1` supplies a scalar and `mul` multiplies its `a` and `b` inputs.
The catalog in `crates/nodes/src/function/catalog.rs` defines all native operation and port ids.
Processors and dynamic parameters use the same function representation. Graph validation and
execution use bounded iterative traversal and reject cycles.

`graph.annotation.select {"kind": "frame"|"comment"|"pin", "id": ...}` selects an annotation.
`graph.frame.edit` accepts `title`, `titleVisible`, `description`, `color` and `rect`.
`graph.frame.move {"id": ..., "by": [dx, dy], "snapToGrid": true}` moves enclosed nodes,
comments, nested frames and pins together. `graph.comment.edit` accepts `text`, `at` and `size`.
`session.inspect` includes annotation selection and the standalone function; `ui.inspect`
includes frame, comment and pin rectangles for synthetic input.

## Portable materials (TextureCraft)

A v3 `.mcmat` publishes a single material graph for procedural cooking. Choose **Export material… → MCMAT → Root graph** or give the graph's full SBS path to the CLI.

The commands below assume `surfaces.sbs` has a connected material graph at `Materials/Oak`, a scalar control named `wear`, a preset named `Worn`, and an image input named `curvature`. Supply a mesh map at `mesh/curvature.exr`.

```sh
materialcraft-cli publish surfaces.sbs Oak.mcmat --graph Materials/Oak
materialcraft-cli info Oak.mcmat
materialcraft-cli cook Oak.mcmat --size 1024 --set wear=0.2
materialcraft-cli export Oak.mcmat build/oak --profile materialx --size 2048 \
  --preset Worn --set wear=0.7 --input curvature=mesh/curvature.exr
```

The ZIP contains a version marker (`material.json` with `{"version":3}`), a DEFLATE-compressed `source.sbs`, and the source assets its graphs reference under `resources/`. The sole graph at the root of the SBS document is the entry. Reachable helper graphs and functions have local paths under `Dependencies/`. Republish v1 and v2 archives from the original authoring project.

`info` reads the entry's path, dimensions, supported resolutions, typed defaults, saved values, presets, image inputs and output usages. A cook starts from the saved values, applies the named preset, then applies each explicit override. `--set` accepts numbers, booleans, JSON vectors, colors and typed values such as `{"t":"float","v":0.7}`. The size is the longer side in pixels. The graph retains its aspect ratio within the supported powers of two from 16 to 8192. Use `--size 1024x512` to choose both sides. An omitted size uses the authored dimensions. An explicit size also sets the final dimensions of outputs fed by fixed-size nodes.

TextureCraft requests `--profile maps` at its texture set's resolution and supplies mesh maps through repeated `--input identifier=path`. Common identifiers include `ambientOcclusion`, `curvature`, `thickness`, `position`, `worldNormal`, `normal`, `height`, `id`, `bentNormal`, `opacity`, `colorMap` and `worldDirection`. An image override uses the published preview binding’s color space when present. Otherwise the input’s declared usage determines the transfer, with the identifier as a fallback for untagged inputs. The JSON report lists each map's identifier, usage, filename, color space and actual dimensions.

The CLI's `--graph-path` selects a literal SBS path, including a numeric name, while `--graph` retains numeric-index shorthand.

The `materialx` profile writes `material.mtlx` with relative texture paths and an OpenPBR surface. Color textures default to sRGB PNG, data textures to linear 16-bit PNG, and out-of-range values to floating-point EXR. Both bake profiles write tangent-space Y+ normals. A directly connected Normal node supplies its evaluated convention, including through routing dots. Other normal sources default to Y+. Use `--normal-format directx` for a Y− source or `--normal-format opengl` for Y+. OpenPBR scalar and normal inputs require linear data. Height becomes signed EXR displacement in scene units using `(height - 0.5) × displacementScale`. The CLI accepts `--displacement-scale`. MaterialX texture filenames include a hash of the output name and bytes. Re-export writes the document last and keeps earlier texture versions, so a failed export leaves the previous material usable. Outputs without an OpenPBR connection are written alongside the document and listed in `unmapped`.

The named profiles choose their own file names and formats. Use `--format` and `--pattern` with plain image export. `--normal-format` applies to both named profiles, and `--displacement-scale` applies to MaterialX. Profile EXR files are linear. Leave the color space automatic, or choose linear or raw explicitly.

| Command | Params |
|---|---|
| `file.exportMaterial` | `{path, graph?}` publishes the chosen source graph by SBS path or index. The default is the open graph. |
| `material.info` | `{graph?}` reads the material interface. |
| `material.cook` | `{graph?, size?, preset?, values?, inputs?}` returns output dimensions and mean values. |
| `file.export` | `{dir, graph?, profile?, size?, preset?, values?, inputs?, normalFormat?, displacementScale?}` bakes images using the selected profile. |
| `file.sendToTextureCraft` | `{graph?}`: export into TextureCraft's library folder (`Documents/TextureCraft/library`), where its shelf lists it |
| `graph.input.bind` / `graph.input.unbind` | `{identifier, resource? \| path?, linear?}` / `{identifier}`: a preview image for an input node (a mesh map exported from TextureCraft), saved in the package |
| `file.open` | `{path}` opens `.sbs` XML or an independent `.mcraft` ZIP. Also opens a `.mcmat`'s source without a save path. Returns `warnings` for unsupported content; also in `session.inspect` as `package.warnings` |
| `file.save` / `file.saveAs` / `file.saveCopyAs` | `{path?}` / `{path}` / `{path}`: `.sbs` writes XML and adjacent `resources/`; `.mcraft` writes a ZIP containing `package.sbs` and `resources/`. Unrecognized extensions get `.sbs` appended. Save Copy preserves the active path and modified state |
| `file.saveAll` | Native only. `{}` saves every modified package that has a local file and returns `{saved, withoutFile, failed}`. `saved` lists paths, `withoutFile` lists packages that need `file.saveAs`, and `failed` lists `{package, error}` entries. The original package stays active |
| `file.importBitmap` / `file.importVector` | `{path, name?, folder?}` imports a supported bitmap / SVG into Resources or a subfolder without adding a node. Unsaved imports and their original bytes participate in undo. `session.inspect` reports resource name, folder, file, byte count and missing status |
| `graph.resource.add` | `{resource, document?, at?}` places a resource from the source document on the active material graph. Cross-document drops copy the asset; resource and node creation undo together |
| `folder.properties` / `folder.attributes` | `{folder, document?}` reads Identifier/Description; add `identifier?` and/or `description?` to edit. Folder attributes persist as native SBS group identifiers and descriptions. The reserved root Resources identifier cannot change |
| `library.functions` | `{filter?}`: list reusable SBS functions with package URI, full graph path, typed ports and missing status |
| `library.function.add` | `{graph, package? (default: sbs://functions.sbs), function?: FunctionGraphTarget, at?, snapToGrid?}`: insert a reference into the active Function or processor canvas |

## MCP tools

`session_inspect`, `command_list`, `command_run`, `command_batch`, `library_list`, `graph_new`,
`node_add`, `node_connect`, `node_param`, `package_open`, `package_save`, `bitmap_import`,
`outputs_export`, `material_export`, `view_render` (headless) and, bridged to the app, `view_screenshot`,
`ui_screenshot`, `ui_inspect`, `ui_menu_invoke`, `ui_input`. Bridged to the app, `package_save`
without a path runs File > Save through `ui.menu.invoke`, so it returns that call's error when a
dialog or prompt blocks it. `package_open` opens `.mcmat` files
too. `material_export` accepts `{path, graph?}` and publishes below the write root. Use
`outputs_export` to bake variations with `profile`, `size`, `preset`, `values` and `inputs`.
Image paths are relative to the read root and the destination is relative to the write root.
Workspace publication limits both the combined uncompressed assets and the final archive to 256 MiB.

While an FX-Map subgraph is open, `ui.inspect.subgraph` identifies its owner and selection. Canvas
node IDs and ports refer to that embedded graph. `ui.menu.invoke` with `ui.graph.parent` returns
to the parent canvas.

Automation command requests each form a separate undo step. Embedded graph edits may explicitly
pass `merge: true` to continue one gesture; an ordinary request ends that merge. UI slider gestures
still coalesce until release. `material_export` uses the headless write-root capability and does not
expose unrestricted engine file paths.

Bitmap Color space selects sRGB or Linear. `graph.input.bind` accepts `linear: true` for normal,
height and other data maps. Input preview bindings persist in native SBS graph options with the
`materialcraft.previewImage.` and `materialcraft.previewLinear.` prefixes; these options describe
MaterialCraft editor previews and do not establish external application interoperability.

### Shared graph items and classification metadata

The Library sorts previews by their displayed names. Graph items (Comment, Dot node, Frame and
Pin) are available in material, standalone Function, embedded Function and FX-Map canvases.
Dot node appears only in Graph items. To address an embedded canvas, annotation commands and
`library.add` accept `function: FunctionGraphTarget` or `pattern: owner node id`.
`graph.pin.edit {id, description?, at?}` edits a pin's description or position. Selecting a pin
shows its Description field; creating one focuses that field. Delete and undo apply to the
selected pin. `session.inspect` reports `annotationTarget`; `ui.inspect` also reports pin bounds.
Frames, comments and pins are saved in the owning canvas's SBS `GUIObjects` section.

Function-library conversion preserves Category and Tags, including empty values. Recognized
function tags select Library filters before category-path and package-path fallbacks; multiple
recognized tags can place the function in multiple filters. The tag `Easing` maps to the
`Functions/Easings` filter. This does not implement project-configurable Library filters.
