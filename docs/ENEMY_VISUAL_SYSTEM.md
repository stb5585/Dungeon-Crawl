# Enemy Visual System

Enemy visuals are split into four presentation layers. Each layer solves a different readability problem and should remain separate.

## Layer 1: Combat Sprite

Combat sprites are the active battlefield representation. They are used for the visible enemy body in combat and dungeon-facing combat overlays.

Do not replace combat sprites with portrait-style enemy renders, token crops, item-card art, or rectangular encounter artwork.

Combat sprite loading uses:

1. `EnemyCombatSpriteManager` for transparent PNG loading from `enemy_combat_sprites/`.
2. Exact enemy display-name mappings in `enemy_combat_sprite_map.json`.
3. Boss and generic fallback sprites when a specific combat-sprite file is missing.
4. Legacy `sprites/enemies/` PNGs only as a runtime fallback if the new combat-sprite path fails.

Combat sprites must be transparent, full-body creature images with no frame, no label, no rectangular background, and no UI decoration.

Current combat-sprite coverage is complete for concrete enemy display names in `src/core/enemies.py`, excluding the development `Test` enemy and the base `Myrmidon` template. Upgraded variants that share a display name use the same sprite mapping.

## Layer 2: Enemy Token

Enemy tokens are compact circular portraits generated automatically from the broad-archetype enemy renders. They are used for compact combat UI such as turn/initiative banners, future target lists, future encounter summaries, and other status-heavy layouts.

Player turn banners use the same compact-token presentation, but derive the face token from the player's portrait via `PlayerTokenManager`.

Token generation uses:

1. `EnemyRenderManager` render-key lookup.
2. `enemy_token_crop.json` crop override when available.
3. A default centered head-and-shoulders crop when no override exists.
4. Circular framing and token-size caching in `EnemyTokenManager`.

Token crops should be tuned for 64x64 and 96x96 readability.

## Layer 3: Enemy Combat Artwork

Enemy combat artwork is full-body encounter presentation art. It is used for combat display panels, selected target display, combat action display, boss-introduction-style panels, and inspection panels.

Combat artwork answers "what is standing in front of me right now?" It should preserve weapons, armor, body shape, and silhouette readability at combat-panel scale.

Combat artwork uses:

1. `EnemyCombatArtManager` for individual PNG loading from `enemy_combat_art/`.
2. `EnemyRenderManager` render-key lookup so name, boss, category, and fallback behavior stays consistent.
3. Boss and generic fallback artwork when a specific combat-art file is missing.
4. Per-key and per-size caching for combat panels.

Combat artwork should not replace the visible center combat enemy body. Use `enemy_combat_sprites/` for that.

## Layer 4: Enemy Render

Large enemy renders remain presentation artwork. They are used for selected target panels, inspection screens, bestiary screens, boss introductions, and encounter artwork.

Large renders should not be used as battlefield sprites or compact initiative art. Prefer combat artwork for active combat panels and use large renders as source/review artwork for portrait-like or bestiary contexts.

## Asset Validation

Run this after changing enemy render source images, the runtime atlas, or token crops:

```bash
./.venv/bin/python tools/validate_enemy_render_atlas.py
```

The validator checks atlas dimensions, manifest coverage, frame bounds, frame overlap, source PNG coverage, and token crop bounds. The current atlas passes these automated integrity checks.

Run this after changing combat artwork or token crops to rebuild the visual comparison sheet:

```bash
./.venv/bin/python tools/build_enemy_combat_art_review_sheet.py
```

Run this after changing combat sprites to rebuild the review sheet from approved transparent PNGs:

```bash
./.venv/bin/python tools/build_enemy_combat_sprites.py
```

This tool does not generate replacement artwork. Production combat sprites are approved transparent PNG assets stored individually under `src/ui_pygame/assets/enemy_combat_sprites/`.

## Future Render Generation Requirements

Future enemy artwork prompts must preserve archetype distinctions at token size, not only at full render size.

- Goblin: green skin, large ears, yellow eyes, hunched raider silhouette.
- Kobold: reptilian, scaled skin, narrow snout, smaller tunnel-creature profile.
- Bandit: human, leather hood or outlaw gear, visible face.
- Cultist: robes, mask, ritual elements, occult silhouette.
- Orc: larger than goblin, tusks, heavier jaw and armor.
- Skeleton Warrior: helmet, armor, weapon silhouette distinct from basic skeleton.
- Dire Wolf: larger, darker, more scarred and aggressive than wolf.
- Ooze: darker and more corrosive than slime.
- Greater Demon: larger horns and more imposing facial structure than demon.
- Wyrm: serpentine profile distinct from broader dragon head.
