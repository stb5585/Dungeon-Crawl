# Dungeon Tile Art

Dungeon rendering art is loaded through `src/ui_pygame/assets/dungeon_tiles/dungeon_texture_manifest.json`.
Prefer adding new renderer assets to that manifest instead of hard-coding new paths in the renderer.

## Asset Layout

- Complete projected floor textures live under `src/ui_pygame/assets/dungeon_tiles/floors/`.
- Complete projected ceiling textures live under `src/ui_pygame/assets/dungeon_tiles/ceilings/`.
- Wall textures live under `src/ui_pygame/assets/dungeon_tiles/walls/`.
- Transparent floor and wall decorations live under `src/ui_pygame/assets/dungeon_tiles/special_tiles/`.
- Approved organic source atlases live under `src/ui_pygame/assets/dungeon_tiles/source/ai/`.

The organic root/fungus production assets are `256x256` RGBA PNGs. They are intentionally smaller than the older projected-plane assets; the texture library scales them for projected dungeon surfaces.

## Current Organic Texture Keys

Use these manifest texture keys for renderer-only surface overrides:

- `floor_roots`: sparse embedded roots, current default for `RootGrowthTile`.
- `floor_roots_sparse`: named sparse roots variant.
- `floor_roots_dense`: dense embedded roots variant.
- `floor_fungus`: sparse embedded fungus, current default for `FungusPatchTile`.
- `floor_fungus_sparse`: named sparse fungus variant.
- `floor_fungus_dense`: dense embedded fungus variant.
- `floor_root_fungus_mixed`: mixed roots and fungus variant.
- `ceiling_fungus`: upper-wall/ceiling fungus, current default for `FungusPatchTile` ceilings.
- `ceiling_fungus_upper`: named upper-wall/ceiling fungus variant.

Use these manifest special texture keys for transparent overlay sprites:

- `root_growth`: dense root overlay, current default sprite for `RootGrowthTile`.
- `root_growth_sparse`
- `root_growth_dense`
- `fungus_patch`: dense fungus overlay, current default sprite for `FungusPatchTile`.
- `fungus_patch_sparse`
- `fungus_patch_dense`
- `ceiling_fungus_overlay`
- `root_fungus_patch`

## Map Authoring

Use map tile classes for gameplay/world placement:

- `RubbleTile`
- `RootGrowthTile`
- `FungusPatchTile`
- `CrystalClusterTile`
- `BonePileTile`
- `BrokenGearTile`
- `FunhouseBoundaryWall`

Decorative cave-path tiles are traversable in this P1 pass. They provide rendering and message hooks only; harvesting, rubble destruction, poison/fungus effects, crystal mana behavior, and salvage mechanics are future gameplay work.

Tiled JSON maps should put gameplay tiles on a layer named `Tiles`, or mark the gameplay tile layer with a `gameplay=true` property. Decorative/object-only layers should be marked `decorative=true` when they are not intended to create gameplay tiles.

## Regeneration

Rebuild dungeon render assets with:

```bash
./.venv/bin/python tools/build_dungeon_render_assets.py
```

When `source/ai/roots_fungus_floor_atlas.png` and `source/ai/roots_fungus_overlay_chromakey_atlas.png` are present, the builder regenerates the approved organic `256x256` variants and aliases them to the existing in-game keys.

Rebuild the Tiled tileset after adding or changing authoring icons:

```bash
./.venv/bin/python tools/generate_tiled_tileset.py
```

Then convert maps if needed:

```bash
./.venv/bin/python tools/convert_maps_to_tiled_json.py
```
