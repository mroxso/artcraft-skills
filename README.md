# ArtCraft Skills

AI agent skills for the ArtCraft software suite. Each skill teaches a coding agent — Codex, Claude Code, Cursor, and others — to drive a desktop creative application through its desktop control protocol, MCP bridge, or headless CLI.

[![skills.sh](https://img.shields.io/endpoint?url=https://skills.sh/api/badge/mroxso/artcraft-skills)](https://skills.sh/mroxso/artcraft-skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Skills](https://img.shields.io/badge/skills-16-blue)
[![Last commit](https://img.shields.io/github/last-commit/mroxso/artcraft-skills)](https://github.com/mroxso/artcraft-skills/commits)

## Available skills

| Skill | Application | What the skill covers |
| --- | --- | --- |
| [photocraft](artcraft/photocraft/SKILL.md) | [PhotoCraft](https://github.com/storytold/photocraft) | Session selection, command discovery, layers and selections, file access, background jobs, previews, and export verification. |
| [filmcraft](artcraft/filmcraft/SKILL.md) | [FilmCraft](https://github.com/storytold/filmcraft) | Session selection, command discovery, linked timeline edits, audio and color workflows, project saving, and export verification. |
| [vectorcraft](artcraft/vectorcraft/SKILL.md) | [VectorCraft](https://github.com/storytold/vectorcraft) | Live and headless sessions, command discovery, object targeting, editable artwork, previews, and save/export verification. |
| [lightcraft](artcraft/lightcraft/SKILL.md) | [LightCraft](https://github.com/storytold/lightcraft) | Live and headless sessions, library locks, photo targeting, develop controls, durable edits, previews, and export verification. |
| [effectcraft](artcraft/effectcraft/SKILL.md) | [EffectCraft](https://github.com/storytold/effectcraft) | Session selection, command discovery, composition and property targeting, animation, UI interaction, project saving, and export verification. |
| [designcraft](artcraft/designcraft/SKILL.md) | [DesignCraft](https://github.com/storytold/designcraft) | Live and headless sessions, command discovery, spread coordinates, story targeting, data merge, previews, and save/export verification. |
| [cadcraft](artcraft/cadcraft/SKILL.md) | [CADCraft](https://github.com/storytold/cadcraft) | Executable discovery, session selection, command discovery, drawing entities, layers, layouts, and command-line input. |
| [deckcraft](artcraft/deckcraft/SKILL.md) | [DeckCraft](https://github.com/storytold/deckcraft) | Live and headless sessions, command discovery, slide and shape targeting, slide shows, previews, and save/export verification. |
| [figcraft](artcraft/figcraft/SKILL.md) | [FigCraft](https://github.com/storytold/figcraft) | Session and window selection, command discovery, node and document inspection, batches with step references, synthetic input, previews, and confined file access. |
| [gridcraft](artcraft/gridcraft/SKILL.md) | [GridCraft](https://github.com/storytold/gridcraft) | Token authentication, command discovery, cell and range editing, dialogs, workbook windows, printing, and screenshot verification. |
| [pdfcraft](artcraft/pdfcraft/SKILL.md) | [PdfCraft](https://github.com/storytold/pdfcraft) | The headless MCP server, the opt-in desktop control channel, command discovery, read/write roots, batch conversion and OCR, and output verification. |
| [solidcraft](artcraft/solidcraft/SKILL.md) | [SolidCraft](https://github.com/tangency-labs/solidcraft) | Executable discovery, watchable and headless sessions, token authentication, command discovery, sketch and feature editing, numerical verification, rendering, and export. |
| [soundcraft](artcraft/soundcraft/SKILL.md) | [SoundCraft](https://github.com/storytold/soundcraft) | The control channel, CLI, and MCP surfaces, session inspection, track and clip targeting, time references, synthetic input ordering, and screenshot verification. |
| [wordcraft](artcraft/wordcraft/SKILL.md) | [WordCraft](https://github.com/storytold/wordcraft) | Key authentication, multiple open documents, command discovery, text and style targeting, queued input, native printing, and page render verification. |
| [materialcraft](artcraft/materialcraft/SKILL.md) | [MaterialCraft](https://github.com/storytold/materialcraft) | Live and headless sessions, command discovery, node graph editing, function graphs, view verification, texture export, and portable `.mcmat` materials. |
| [texturecraft](artcraft/texturecraft/SKILL.md) | [TextureCraft](https://github.com/storytold/texturecraft) | Live and headless sessions, command discovery, texture sets and layer stacks, painting strokes, mesh-map baking, previews, texture export, and `.tcmat`/`.mcmat` materials. |

## Install

Install with the [skills CLI](https://github.com/vercel-labs/skills):

```sh
# all 16 skills
npx skills add mroxso/artcraft-skills

# a single skill
npx skills add mroxso/artcraft-skills --skill photocraft

# a single skill, globally, for Codex
npx skills add mroxso/artcraft-skills --skill photocraft --agent codex --global
```

Replace `photocraft` with any skill name from the table.

## Usage

In Codex, invoke a skill by name — for example `$photocraft`. In other agents, simply ask it to work in the application ("open this FilmCraft project and export the timeline") and the skill instructions will be picked up.

> [!NOTE]
> The skills provide instructions only. They do not install the applications or configure MCP servers. Each skill needs a running application with an automation session (desktop control or MCP bridge), or an installed executable for headless use.

## Repository layout

```text
artcraft/
└── <skill>/
    ├── SKILL.md            # skill instructions (front matter: name, description)
    ├── agents/openai.yaml  # Codex agent configuration
    └── references/         # upstream documentation snapshots + LICENSE-MIT
```

A few skills ship extras: `solidcraft` includes a helper script (`scripts/sc.py`), and `pdfcraft` bundles MCP and CLI-batch references instead of a control protocol.

## Contributing

- **New skills** should follow the layout above: a `SKILL.md` with `name` and `description` front matter, an `agents/openai.yaml`, and any upstream references under `references/` with their license.
- **Refreshing snapshots**: keep reference files unmodified copies of the upstream docs, and update the download date in the affected `SKILL.md` files and in [Attribution](#attribution).
- **Docs fixes** to `SKILL.md` instructions are welcome — open an issue first for larger changes.

## Attribution

Every bundled reference is an unmodified snapshot of upstream documentation, downloaded on 2026-11-11 (`cadcraft`, `effectcraft`, `figcraft`, `filmcraft`, `gridcraft`, `lightcraft`, and `pdfcraft` on 2026-11-09, `deckcraft`, `designcraft`, and `soundcraft` on 2026-11-02, unchanged upstream since those dates). Snapshots are copyright © 2026 ArtCraft Team and the respective contributors, distributed under the upstream MIT license reproduced in each skill's `references/LICENSE-MIT`. Relative documentation links inside a snapshot resolve against the upstream repository's `docs/` directory.

| Skill | Upstream source | Snapshotted files |
| --- | --- | --- |
| photocraft | [storytold/photocraft](https://github.com/storytold/photocraft) | `control-protocol.md` |
| filmcraft | [storytold/filmcraft](https://github.com/storytold/filmcraft) | `control-protocol.md` |
| vectorcraft | [storytold/vectorcraft](https://github.com/storytold/vectorcraft) | `control-protocol.md` |
| lightcraft | [storytold/lightcraft](https://github.com/storytold/lightcraft) | `control-protocol.md` |
| effectcraft | [storytold/effectcraft](https://github.com/storytold/effectcraft) | `control-protocol.md` |
| designcraft | [storytold/designcraft](https://github.com/storytold/designcraft) | `control-protocol.md` |
| cadcraft | [storytold/cadcraft](https://github.com/storytold/cadcraft) | `control-protocol.md` |
| deckcraft | [storytold/deckcraft](https://github.com/storytold/deckcraft) | `control-protocol.md` |
| figcraft | [storytold/figcraft](https://github.com/storytold/figcraft) | `control-protocol.md` |
| gridcraft | [storytold/gridcraft](https://github.com/storytold/gridcraft) | `control-protocol.md` |
| pdfcraft | [storytold/pdfcraft](https://github.com/storytold/pdfcraft) | `mcp.md`, `cli-batch.md` |
| solidcraft | [tangency-labs/solidcraft](https://github.com/tangency-labs/solidcraft) | `control-protocol.md`, `mcp.md`, `scripts.md`, `render-jobs.md` |
| soundcraft | [storytold/soundcraft](https://github.com/storytold/soundcraft) | `control-protocol.md` |
| wordcraft | [storytold/wordcraft](https://github.com/storytold/wordcraft) | `control-protocol.md` |
| materialcraft | [storytold/materialcraft](https://github.com/storytold/materialcraft) | `control-protocol.md` |
| texturecraft | [storytold/texturecraft](https://github.com/storytold/texturecraft) | `control-protocol.md` |

SolidCraft snapshots are copyright © 2026 SolidCraft contributors.

## License

The skill instructions and repository documentation are available under the [MIT license](LICENSE). Bundled upstream references remain under their respective upstream MIT licenses (see [Attribution](#attribution)).
