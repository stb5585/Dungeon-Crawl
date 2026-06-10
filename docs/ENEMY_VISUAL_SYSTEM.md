# Enemy Visual System

Enemy visuals are split into three presentation layers. Each layer solves a different readability problem and should remain separate.

## Layer 1: Combat Sprite

Combat sprites remain the tactical battlefield representation. They are used for dungeon-facing combat, movement, enemy positioning, target selection, damage flashes, death animation, and tactical readability.

Do not replace combat sprites with large enemy renders.

## Layer 2: Enemy Token

Enemy tokens are compact circular portraits generated automatically from the broad-archetype enemy renders. They are used for compact combat UI such as turn/initiative banners, future target lists, future encounter summaries, and other status-heavy layouts.

Player turn banners use the same compact-token presentation, but derive the face token from the player's portrait via `PlayerTokenManager`.

Token generation uses:

1. `EnemyRenderManager` render-key lookup.
2. `enemy_token_crop.json` crop override when available.
3. A default centered head-and-shoulders crop when no override exists.
4. Circular framing and token-size caching in `EnemyTokenManager`.

Token crops should be tuned for 64x64 and 96x96 readability.

## Layer 3: Enemy Render

Large enemy renders remain presentation artwork. They are used for selected target panels, inspection screens, bestiary screens, boss introductions, and encounter artwork.

Large renders should not be used as battlefield sprites or compact initiative art.

## Asset Validation

Run this after changing enemy render source images, the runtime atlas, or token crops:

```bash
./.venv/bin/python tools/validate_enemy_render_atlas.py
```

The validator checks atlas dimensions, manifest coverage, frame bounds, frame overlap, source PNG coverage, and token crop bounds. The current atlas passes these automated integrity checks.

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
