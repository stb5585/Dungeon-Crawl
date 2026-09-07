# Asset Provenance And Distribution Inventory

Status: `Stabilization baseline — owner attribution required for audio`

This inventory separates files required by the game from review and source
material. The repository's MIT license covers project code and documentation;
it does not establish rights for third-party media whose original terms are
not recorded.

## Runtime Visual Assets

The owner reports that the current visual assets were generated with GPT image
generation through the Codex plugin in VS Code. No third-party artist or stock
library is currently recorded for these categories.

| Runtime directory | Purpose | Distribution |
| --- | --- | --- |
| `ability_icons/`, `effects/`, `item_icons/`, `ui/` | Ability, effect, item, and interface atlases/icons | Required |
| `backgrounds/` | Menu, town, shop, and dungeon backgrounds | Required |
| `companion_art/`, `enemy_combat_sprites/`, `npc_art/` | Combat and dialogue character artwork | Required |
| `dungeon_tiles/` | First-person dungeon surfaces and special-tile art | Required |
| `item_art/`, `key_items/` | Equipment, consumable, material, and story-item renders | Required |
| `portraits/`, `sprites/` | Player portraits, tokens, and NPC sprites | Required |

The packaged map definitions and their 32-pixel editor tiles live under
`src/core/data/maps/`. Map JSON/TMX metadata is project-authored runtime data;
the tile images follow the same reported GPT-generated provenance as the other
visual assets.

## Audio

`src/ui_pygame/assets/sounds/` and `src/ui_pygame/assets/music/` are required
runtime audio. The owner reports that these files came from free asset sites,
but the exact source pages, authors, license names, modification terms, and
attribution text are not yet known.

Every audio entry therefore has status **OWNER ATTRIBUTION REQUIRED**. Do not
invent a source or license. Before a public release, the owner must supply or
verify an attribution ledger for each file and confirm that redistribution is
permitted. The two largest runtime files are currently:

- `music/eerie_dungeon_background.wav` (about 21 MB);
- `sounds/new_sounds/underground_spring.wav` (about 19 MB).

WAV-to-OGG conversion is deferred until the source/license audit is complete.
Pygame 2 supports OGG playback, but source-quality originals must first be
placed in an owner-controlled archive or their disposition documented. A
format conversion would reduce distribution size but would not resolve the
missing attribution.

## Generated Review And Source Material

- `docs/assets/review-sheets/` contains generated visual contact sheets. They
  are documentation-only and excluded from the PyInstaller artifact.
- `docs/spreadsheets/` contains generated catalog CSVs. They are review data,
  not runtime resources, and are excluded from the artifact.
- `docs/ability_trees/` contains generated diagrams used for design review,
  not runtime resources.
- Local `old_assets/`, `ascii_files/`, and `map_files/text_files/` directories
  are source/reference workspaces ignored by Git and excluded from builds.
  Their contents are not covered by this tracked inventory.

The repository should eventually use Git LFS for large binary assets if clone
size becomes a maintenance problem. This stabilization pass intentionally does
not rewrite Git history; any LFS migration must be separately planned and
coordinated.
