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

Every SBS save writes MaterialCraft's workspace release version to `updaterVersion`, including
when resaving a file from an older release. `formatVersion` identifies the SBS schema separately.

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
| `outputs.export {dir, format?, pattern?, depth?, size?, graph?}` | headless | cook at full size and write every output |
| `material.export {path, graph?, size?, values?}` | headless | write a portable `.mcmat` below the write root |
| `render {view?, width?, height?, yaw?, pitch?, scene?, node?, port?, full?, tiling?, hq?, displacement?}` | headless | PNG (base64) of the 3D view or of one node; `hq` is the beauty render (displaced mesh, ray-traced AO, shadowed key light, 3×3 supersampling), `displacement` its depth in scene radii |
| `ui.inspect` | app | UI state, the graph view rectangle, every node's screen rectangle, every port's identifier, display label and screen position, fps, toasts |
| `ui.menu.list` / `ui.menu.invoke {id}` | app | the menu catalog; behave like a click |
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
| `file.new` | `{template?, name?, size?}`; templates from `graph.templates` (`empty`, `pbr`, `bricks`, `stone_tiles`, `wood`, `rusty_metal`, `fabric`, `ground`) |
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
| `graph.node.base` | `{id?, sizeMode?, size?, format?, seed?, tiling?}` |
| `graph.exposed.add` / `graph.exposed.set` | `{id, label?, default?, bind?: {node, param}}` (with `bind`, `id` may be omitted: the input is named after the parameter, `opacity`, `opacity_1`…) / `{id, value}` |
| `graph.node.function` | `{id?, param, function}` drives a parameter by a function graph of the graph's inputs (dynamic parameter); `{id?, param, remove: true}` removes it |
| `graph.preset.save` / `.apply` / `.delete` | `{name}`: store, restore or remove the current input values |
| `graph.createFromSelection` | `{name?, ids?}`: move nodes into a sub-graph and replace them with an instance |
| `view.2d` / `view.3d` | which node the 2D view shows, channel, tiling, histogram; scene, environment, camera, tiling, `heightScale` (how far the height output raises the mesh, in mesh radii) and `heightLevel` (the height that stays on the surface; 0 = the relief rises out of it), `normalYFlip` (interpret DirectX normal maps; default false/OpenGL), `transparency` (see through where the alpha is below one: the opacity output, else the base color's alpha), `alphaView` (show the alpha channel) |
| `view.3d.loadMesh` | `{path}` shows an OBJ, glTF or GLB mesh (scene `custom`) |
| `library.list` | `{filter?, category?}`: every node with ports and parameters |

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
commands; the 3D View's Material menu lists its channel sources. A Height-only output affects height
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
`{"kind":"dynamic","node":12,"parameter":"opacity"}`, or
`{"kind":"pattern","owner":12,"node":3,"parameter":"patternrotation"}`.

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
paste. The session retains the most recent embedded clipboard. Cross-target paste keeps internal
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

`graph.annotation.select {"kind": "frame"|"comment", "id": ...}` selects an annotation.
`graph.frame.edit` accepts `title`, `titleVisible`, `description`, `color` and `rect`.
`graph.frame.move {"id": ..., "by": [dx, dy], "snapToGrid": true}` moves enclosed nodes,
comments, nested frames and pins together. `graph.comment.edit` accepts `text`, `at` and `size`.
`session.inspect` includes annotation selection and the standalone function; `ui.inspect`
includes frame and comment rectangles for synthetic input.

## Portable materials (TextureCraft)

A `.mcmat` portable material is a zip: `material.json` (manifest), `maps/<usage>.png` and
`source.sbs` (the package). TextureCraft applies it as a fill layer and keeps the exposed inputs
editable, re-cooking through `materialcraft-cli`. The format is a convention the two apps share;
each has its own reader and writer (`crates/formats/src/material.rs` here), so keep them in step.

```json
{ "format": "craft-material", "version": 2, "name": "Brick wall", "graph": "Brick_wall", "size": [2048, 2048],
  "maps": [{"usage": "baseColor", "file": "maps/baseColor.png", "colorSpace": "srgb"}],
  "parameters": [{"id": "wear", "label": "Wear", "default": {"t": "float", "v": 0.5}, "min": 0, "max": 1,
                  "value": {"t": "float", "v": 0.8}}],
  "inputs": [{"identifier": "curvature", "kind": "gray"}],
  "presets": [{"name": "Worn", "values": {"wear": {"t": "float", "v": 1.0}}}],
  "source": "source.sbs" }
```

- Usages come from the shared `ComponentUsage` catalog (the first output of each, excluding
  `any`). The catalog includes PBR, diffuse/specular, coat, sheen, scattering and user channels.
  Color maps are 8-bit sRGB PNGs; data maps are 16-bit linear. Each map records its color space.
  Additional usage identifiers do not change the manifest version; consumers may ignore usages
  they do not support. Normals are tangent space, OpenGL (Y+); height is 0..1 with 0.5 at the surface.
  The 3D preview supports base color (including `diffuse`), normal, roughness, metallic, height,
  ambient occlusion, emissive and opacity; other usages remain available for SBS and exports.
- Parameters are the exposed inputs other apps can set (float, float2-4, int, int2, bool, color,
  enum), values in the typed form `{"t", "v"}`; colors are linear RGBA.
- Inputs are the graph's input nodes. Mesh maps feed them by identifier: `ambientOcclusion`,
  `curvature`, `thickness`, `position`, `worldNormal`, `normal`, `height`, `id`, `bentNormal`,
  `opacity`, `colorMap`, `worldDirection`.
- Readers ignore unknown fields and require manifest `version` 2.

| Command | Params |
|---|---|
| `file.exportMaterial` | `{path, graph?, size? (px), values? {input: value}, inputs? {identifier: image path}}`: cook and write a `.mcmat`. TextureCraft runs `materialcraft-cli run source.sbs file.exportMaterial {...}` to re-cook at its texture set's resolution with its own values and baked mesh maps |
| `file.sendToTextureCraft` | `{graph?}`: export into TextureCraft's library folder (`Documents/TextureCraft/library`), where its shelf lists it |
| `graph.input.bind` / `graph.input.unbind` | `{identifier, resource? \| path?, linear?}` / `{identifier}`: a preview image for an input node (a mesh map exported from TextureCraft), saved in the package |
| `file.open` | `{path}` opens `.sbs` XML or an independent `.mcraft` ZIP. Also opens a `.mcmat`'s source without a save path. Returns `warnings` for unsupported content; also in `session.inspect` as `package.warnings` |
| `file.save` / `file.saveAs` / `file.saveCopyAs` | `{path?}` / `{path}` / `{path}`: `.sbs` writes XML and adjacent `resources/`; `.mcraft` writes a ZIP containing `package.sbs` and `resources/`. Unrecognized extensions get `.sbs` appended. Save Copy preserves the active path and modified state |
| `file.importBitmap` / `file.importVector` | `{path, name?, folder?}` imports a supported bitmap / SVG into Resources or a subfolder without adding a node. Unsaved imports and their original bytes participate in undo. `session.inspect` reports resource name, folder, file, byte count and missing status |
| `graph.resource.add` | `{resource, document?, at?}` places a resource from the source document on the active material graph. Cross-document drops copy the asset; resource and node creation undo together |
| `folder.properties` / `folder.attributes` | `{folder, document?}` reads Identifier/Description; add `identifier?` and/or `description?` to edit. Folder attributes persist as native SBS group identifiers and descriptions. The reserved root Resources identifier cannot change |
| `library.functions` | `{filter?}`: list reusable SBS functions with package URI, full graph path, typed ports and missing status |
| `library.function.add` | `{graph, package? (default: sbs://functions.sbs), function?: FunctionGraphTarget, at?, snapToGrid?}`: insert a reference into the active Function or processor canvas |

## MCP tools

`session_inspect`, `command_list`, `command_run`, `command_batch`, `library_list`, `graph_new`,
`node_add`, `node_connect`, `node_param`, `package_open`, `package_save`, `bitmap_import`,
`outputs_export`, `material_export`, `view_render` (headless) and, bridged to the app, `view_screenshot`,
`ui_screenshot`, `ui_inspect`, `ui_menu_invoke`, `ui_input`. `package_open` opens `.mcmat` files
too, and `material_export` `{path, graph?, size?, values?}` writes one below `--write-root` (`path` is
relative, the parent folder must exist, `values` are exposed input values). The workspace sandbox
still refuses `file.*` commands, so a sandboxed agent exports through the tool, not `file.exportMaterial`;
mesh-map `inputs` stay a CLI feature.

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
