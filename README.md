# ArtCraft Skills

AI agent skills for ArtCraft software.

## Install

Install a skill with the [skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add mroxso/artcraft-skills --skill photocraft
npx skills add mroxso/artcraft-skills --skill filmcraft
npx skills add mroxso/artcraft-skills --skill vectorcraft
npx skills add mroxso/artcraft-skills --skill lightcraft
npx skills add mroxso/artcraft-skills --skill effectcraft
npx skills add mroxso/artcraft-skills --skill designcraft
npx skills add mroxso/artcraft-skills --skill cadcraft
npx skills add mroxso/artcraft-skills --skill deckcraft
npx skills add mroxso/artcraft-skills --skill figcraft
npx skills add mroxso/artcraft-skills --skill gridcraft
npx skills add mroxso/artcraft-skills --skill pdfcraft
npx skills add mroxso/artcraft-skills --skill solidcraft
npx skills add mroxso/artcraft-skills --skill soundcraft
npx skills add mroxso/artcraft-skills --skill wordcraft
```

For a global Codex installation:

```sh
npx skills add mroxso/artcraft-skills --skill photocraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill filmcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill vectorcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill lightcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill effectcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill designcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill cadcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill deckcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill figcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill gridcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill pdfcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill solidcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill soundcraft --agent codex --global
npx skills add mroxso/artcraft-skills --skill wordcraft --agent codex --global
```

## Available skills

| Skill | Application | Capabilities |
| --- | --- | --- |
| [photocraft](artcraft/photocraft/SKILL.md) | [PhotoCraft](https://github.com/storytold/photocraft) | Image editing and application automation through desktop control, MCP bridge, or headless CLI. |
| [filmcraft](artcraft/filmcraft/SKILL.md) | [FilmCraft](https://github.com/storytold/filmcraft) | Video project, timeline, audio, and color editing through desktop control, MCP bridge, or headless CLI. |
| [vectorcraft](artcraft/vectorcraft/SKILL.md) | [VectorCraft](https://github.com/storytold/vectorcraft) | Vector artwork, paths, text, artboards, and live effects through desktop control, MCP, or headless CLI. |
| [lightcraft](artcraft/lightcraft/SKILL.md) | [LightCraft](https://github.com/storytold/lightcraft) | Photo organization, development, cropping, rendering, and export through desktop control, MCP, or headless CLI. |
| [effectcraft](artcraft/effectcraft/SKILL.md) | [EffectCraft](https://github.com/storytold/effectcraft) | Compositing, animation, layers, masks, effects, and rendering through desktop control, MCP, or headless CLI. |
| [designcraft](artcraft/designcraft/SKILL.md) | [DesignCraft](https://github.com/storytold/designcraft) | Page layouts, text frames, styles, image placement, and data merge through desktop control, MCP, or CLI. |
| [cadcraft](artcraft/cadcraft/SKILL.md) | [CADCraft](https://github.com/storytold/cadcraft) | CAD drawing, entity, layer, and layout editing through command-line input, desktop control, MCP, or headless CLI. |
| [deckcraft](artcraft/deckcraft/SKILL.md) | [DeckCraft](https://github.com/storytold/deckcraft) | Presentations, slides, shapes, text, charts, and slide shows through desktop control, MCP, or headless CLI. |
| [figcraft](artcraft/figcraft/SKILL.md) | [FigCraft](https://github.com/storytold/figcraft) | Vector designs, frames, layers, components, styles, and prototypes through desktop control, MCP bridge, or headless CLI. |
| [gridcraft](artcraft/gridcraft/SKILL.md) | [GridCraft](https://github.com/storytold/gridcraft) | Spreadsheets, cells, formulas, charts, tables, and pivots through desktop control, MCP bridge, or headless CLI. |
| [pdfcraft](artcraft/pdfcraft/SKILL.md) | [PdfCraft](https://github.com/storytold/pdfcraft) | PDF creation, editing, forms, signing, OCR, and export through desktop control, the MCP server, or headless CLI. |
| [solidcraft](artcraft/solidcraft/SKILL.md) | [SolidCraft](https://github.com/tangency-labs/solidcraft) | Parametric 3D CAD designs, sketches, features, parameters, assemblies, and drawings through desktop control, MCP bridge, or headless CLI. |
| [soundcraft](artcraft/soundcraft/SKILL.md) | [SoundCraft](https://github.com/storytold/soundcraft) | Audio sessions, tracks, clips, mixes, automation, and bounces through desktop control, MCP bridge, or headless CLI. |
| [wordcraft](artcraft/wordcraft/SKILL.md) | [WordCraft](https://github.com/storytold/wordcraft) | Documents, text, styles, tables, comments, and print jobs through desktop control, MCP bridge, or headless CLI. |

Use `$photocraft` in Codex, or ask your agent to work in PhotoCraft. The skill covers session selection, command discovery, layers and selections, file access, background jobs, previews, and export verification.

Use `$filmcraft` in Codex, or ask your agent to work in FilmCraft. The skill covers session selection, command discovery, linked timeline edits, audio and color workflows, project saving, and export verification.

Use `$vectorcraft` in Codex, or ask your agent to work in VectorCraft. The skill covers live and headless sessions, command discovery, object targeting, editable artwork, previews, and save/export verification.

Use `$lightcraft` in Codex, or ask your agent to work in LightCraft. The skill covers live and headless sessions, library locks, photo targeting, develop controls, durable edits, previews, and export verification.

Use `$effectcraft` in Codex, or ask your agent to work in EffectCraft. The skill covers session selection, command discovery, composition and property targeting, animation, UI interaction, project saving, and export verification.

Use `$designcraft` in Codex, or ask your agent to work in DesignCraft. The skill covers live and headless sessions, command discovery, spread coordinates, story targeting, data merge, previews, and save/export verification.

Use `$deckcraft` in Codex, or ask your agent to work in DeckCraft. The skill covers live and headless sessions, command discovery, slide and shape targeting, slide shows, previews, and save/export verification.

Use `$figcraft` in Codex, or ask your agent to work in FigCraft. The skill covers session and window selection, command discovery, node and document inspection, batches with step references, synthetic input, previews, and confined file access.

Use `$gridcraft` in Codex, or ask your agent to work in GridCraft. The skill covers token authentication, command discovery, cell and range editing, dialogs, workbook windows, printing, and screenshot verification.

Use `$pdfcraft` in Codex, or ask your agent to work in PdfCraft. The skill covers the headless MCP server, the opt-in desktop control channel, command discovery, read/write roots, batch conversion and OCR, and output verification.

Use `$solidcraft` in Codex, or ask your agent to work in SolidCraft. The skill covers executable discovery, watchable and headless sessions, token authentication, command discovery, sketch and feature editing, numerical verification, rendering, and export.

Use `$soundcraft` in Codex, or ask your agent to work in SoundCraft. The skill covers the control channel, CLI, and MCP surfaces, session inspection, track and clip targeting, time references, synthetic input ordering, and screenshot verification.

Use `$wordcraft` in Codex, or ask your agent to work in WordCraft. The skill covers key authentication, multiple open documents, command discovery, text and style targeting, queued input, native printing, and page render verification.

The skills provide instructions; they do not install the applications or configure MCP servers. An executable or connected automation session for the chosen application is required.

## Repository layout

```text
artcraft/
├── cadcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
├── deckcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
├── designcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
├── effectcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
├── figcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
├── filmcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
├── gridcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
├── lightcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
├── pdfcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── cli-batch.md
│       ├── LICENSE-MIT
│       └── mcp.md
├── photocraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
├── solidcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   │   ├── control-protocol.md
│   │   ├── LICENSE-MIT
│   │   ├── mcp.md
│   │   ├── render-jobs.md
│   │   └── scripts.md
│   └── scripts/
│       └── sc.py
├── soundcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
├── vectorcraft/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── control-protocol.md
│       └── LICENSE-MIT
└── wordcraft/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
        ├── control-protocol.md
        └── LICENSE-MIT
```

## Reference and attribution

The bundled [control protocol](artcraft/photocraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-10-08 from the [upstream source](https://raw.githubusercontent.com/storytold/photocraft/refs/heads/main/docs/control-protocol.md).

That reference is copyright © 2026 ArtCraft Team and the PhotoCraft contributors, distributed under the upstream MIT license reproduced in [references/LICENSE-MIT](artcraft/photocraft/references/LICENSE-MIT). Relative documentation links in the reference resolve against the [upstream docs directory](https://github.com/storytold/photocraft/tree/main/docs).

The bundled [FilmCraft control protocol](artcraft/filmcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-10-08 from its [upstream source](https://raw.githubusercontent.com/storytold/filmcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the FilmCraft contributors, distributed under the upstream MIT license reproduced in [FilmCraft references/LICENSE-MIT](artcraft/filmcraft/references/LICENSE-MIT). Relative documentation links resolve against the [FilmCraft upstream docs directory](https://github.com/storytold/filmcraft/tree/main/docs).

The bundled [VectorCraft control protocol](artcraft/vectorcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-10-08 from its [upstream source](https://raw.githubusercontent.com/storytold/vectorcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the VectorCraft contributors, distributed under the upstream MIT license reproduced in [VectorCraft references/LICENSE-MIT](artcraft/vectorcraft/references/LICENSE-MIT). Relative documentation links resolve against the [VectorCraft upstream docs directory](https://github.com/storytold/vectorcraft/tree/main/docs).

The bundled [LightCraft control protocol](artcraft/lightcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-10-08 from its [upstream source](https://raw.githubusercontent.com/storytold/lightcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the LightCraft contributors, distributed under the upstream MIT license reproduced in [LightCraft references/LICENSE-MIT](artcraft/lightcraft/references/LICENSE-MIT). Relative documentation links resolve against the [LightCraft upstream docs directory](https://github.com/storytold/lightcraft/tree/main/docs).

The bundled [EffectCraft control protocol](artcraft/effectcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-10-08 from its [upstream source](https://raw.githubusercontent.com/storytold/effectcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the EffectCraft contributors, distributed under the upstream MIT license reproduced in [EffectCraft references/LICENSE-MIT](artcraft/effectcraft/references/LICENSE-MIT). Relative documentation links resolve against the [EffectCraft upstream docs directory](https://github.com/storytold/effectcraft/tree/main/docs).

The bundled [DesignCraft control protocol](artcraft/designcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-10-08 from its [upstream source](https://raw.githubusercontent.com/storytold/designcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the DesignCraft contributors, distributed under the upstream MIT license reproduced in [DesignCraft references/LICENSE-MIT](artcraft/designcraft/references/LICENSE-MIT). Relative documentation links resolve against the [DesignCraft upstream docs directory](https://github.com/storytold/designcraft/tree/main/docs).

The bundled [CADCraft control protocol](artcraft/cadcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-10-12 from its [upstream source](https://raw.githubusercontent.com/storytold/cadcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the CADCraft contributors, distributed under the upstream MIT license reproduced in [CADCraft references/LICENSE-MIT](artcraft/cadcraft/references/LICENSE-MIT). Relative documentation links resolve against the [CADCraft upstream docs directory](https://github.com/storytold/cadcraft/tree/main/docs).

The bundled [DeckCraft control protocol](artcraft/deckcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-10-14 from its [upstream source](https://raw.githubusercontent.com/storytold/deckcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the DeckCraft contributors, distributed under the upstream MIT license reproduced in [DeckCraft references/LICENSE-MIT](artcraft/deckcraft/references/LICENSE-MIT). Relative documentation links resolve against the [DeckCraft upstream docs directory](https://github.com/storytold/deckcraft/tree/main/docs).

The bundled [FigCraft control protocol](artcraft/figcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-11-02 from its [upstream source](https://raw.githubusercontent.com/storytold/figcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the FigCraft contributors, distributed under the upstream MIT license reproduced in [FigCraft references/LICENSE-MIT](artcraft/figcraft/references/LICENSE-MIT). Relative documentation links resolve against the [FigCraft upstream docs directory](https://github.com/storytold/figcraft/tree/main/docs).

The bundled [GridCraft control protocol](artcraft/gridcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-11-02 from its [upstream source](https://raw.githubusercontent.com/storytold/gridcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the GridCraft contributors, distributed under the upstream MIT license reproduced in [GridCraft references/LICENSE-MIT](artcraft/gridcraft/references/LICENSE-MIT). Relative documentation links resolve against the [GridCraft upstream docs directory](https://github.com/storytold/gridcraft/tree/main/docs).

The bundled [PdfCraft MCP conventions](artcraft/pdfcraft/references/mcp.md) and [batch documentation](artcraft/pdfcraft/references/cli-batch.md) are unmodified snapshots downloaded on 2026-11-02 from their [upstream sources](https://github.com/storytold/pdfcraft/tree/main/docs). They are copyright © 2026 ArtCraft Team and the PdfCraft contributors, distributed under the upstream MIT license reproduced in [PdfCraft references/LICENSE-MIT](artcraft/pdfcraft/references/LICENSE-MIT). Relative documentation links resolve against the [PdfCraft upstream docs directory](https://github.com/storytold/pdfcraft/tree/main/docs).

The bundled [SolidCraft control protocol](artcraft/solidcraft/references/control-protocol.md), [MCP documentation](artcraft/solidcraft/references/mcp.md), [scripts documentation](artcraft/solidcraft/references/scripts.md), and [render jobs documentation](artcraft/solidcraft/references/render-jobs.md) are unmodified snapshots downloaded on 2026-11-02 from their [upstream sources](https://github.com/tangency-labs/solidcraft/tree/main/docs). They are copyright © 2026 SolidCraft contributors, distributed under the upstream MIT license reproduced in [SolidCraft references/LICENSE-MIT](artcraft/solidcraft/references/LICENSE-MIT). Relative documentation links resolve against the [SolidCraft upstream docs directory](https://github.com/tangency-labs/solidcraft/tree/main/docs).

The bundled [SoundCraft control protocol](artcraft/soundcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-11-02 from its [upstream source](https://raw.githubusercontent.com/storytold/soundcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the SoundCraft contributors, distributed under the upstream MIT license reproduced in [SoundCraft references/LICENSE-MIT](artcraft/soundcraft/references/LICENSE-MIT). Relative documentation links resolve against the [SoundCraft upstream docs directory](https://github.com/storytold/soundcraft/tree/main/docs).

The bundled [WordCraft control protocol](artcraft/wordcraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-11-02 from its [upstream source](https://raw.githubusercontent.com/storytold/wordcraft/refs/heads/main/docs/control-protocol.md). It is copyright © 2026 ArtCraft Team and the WordCraft contributors, distributed under the upstream MIT license reproduced in [WordCraft references/LICENSE-MIT](artcraft/wordcraft/references/LICENSE-MIT). Relative documentation links resolve against the [WordCraft upstream docs directory](https://github.com/storytold/wordcraft/tree/main/docs).

The original skill instructions and repository documentation are available under the [MIT license](LICENSE).
