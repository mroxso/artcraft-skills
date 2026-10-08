# ArtCraft Skills

AI agent skills for ArtCraft software.

## Install

Install the PhotoCraft skill with the [skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add mroxso/artcraft-skills --skill photocraft
```

For a global Codex installation:

```sh
npx skills add mroxso/artcraft-skills --skill photocraft --agent codex --global
```

## Available skills

| Skill | Application | Capabilities |
| --- | --- | --- |
| [photocraft](artcraft/photocraft/SKILL.md) | [PhotoCraft](https://github.com/storytold/photocraft) | Image editing and application automation through desktop control, MCP bridge, or headless CLI. |

Use `$photocraft` in Codex, or ask your agent to work in PhotoCraft. The skill covers session selection, command discovery, layers and selections, file access, background jobs, previews, and export verification.

The skill provides instructions; it does not install PhotoCraft or configure an MCP server. A PhotoCraft executable or connected automation session is required to operate the application.

## Repository layout

```text
artcraft/
└── photocraft/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
        ├── control-protocol.md
        └── LICENSE-MIT
```

## Reference and attribution

The bundled [control protocol](artcraft/photocraft/references/control-protocol.md) is an unmodified snapshot downloaded on 2026-10-08 from the [upstream source](https://raw.githubusercontent.com/storytold/photocraft/refs/heads/main/docs/control-protocol.md).

That reference is copyright © 2026 ArtCraft Team and the PhotoCraft contributors, distributed under the upstream MIT license reproduced in [references/LICENSE-MIT](artcraft/photocraft/references/LICENSE-MIT). Relative documentation links in the reference resolve against the [upstream docs directory](https://github.com/storytold/photocraft/tree/main/docs).

The original skill instructions and repository documentation are available under the [MIT license](LICENSE).
