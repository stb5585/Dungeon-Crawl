# Large Item Artwork System

Dungeon Crawl now has a broad-archetype item render system for selected-item presentation panels.

This system is parallel to the small item icon system:

- Small item icons remain for compact rows, equipment slots, and dense inventory lists.
- Large item renders are for detail contexts where the selected item has room to breathe.

## Runtime Assets

The runtime artwork lives in:

```text
src/ui_pygame/assets/item_renders/
  item_render_atlas.png
  item_render_atlas.json
  item_render_map.json
```

The current atlas is generated dark-fantasy item artwork based on the provided reference sheet: dramatic lighting, weathered metal/leather/parchment tones, and painterly inventory objects rather than enlarged symbolic icons.

The runtime atlas is normalized to an 8-column grid with `120x336` frames. The border-connected dark card backgrounds have been converted to alpha so the item art can sit directly on top of Dungeon Crawl's UI panels and scene backgrounds.

It is intentionally archetype-based rather than item-specific so it can be swapped for a higher fidelity generated or hand-painted sheet later without changing game logic.

## Archetype Decisions

The render system starts from `item_icon_map.json`, then converts small icon archetypes to larger presentation archetypes.

Important conversions:

- `sword` -> `longsword`
- `longsword` -> `greatsword`
- `hammer` -> `warhammer`
- `tome` and `spellbook` -> `spellbook`
- Missing weapon-like items -> `weapon`
- Missing armor-like items -> `armor`
- Missing offhand-like items -> `offhand`
- Missing accessory-like items -> `accessory`
- Missing consumable-like items -> `consumable`
- Final fallback -> `generic_item`

Large two-handed swords currently mapped to `greatsword`:

- Bastard Sword
- Claymore
- Zweihander
- Changdao
- Flamberge
- Executioner's Blade

Katana currently maps through the concrete render map generated from the item icon map. It can be moved to a dedicated `katana` or `greatsword` render archetype later if the art direction calls for that extra distinction.

## UI Usage

Large renders are used only in selected-item contexts:

- Inventory detail panel
- Equipment detail panel
- Shop selected item artwork panel, reusing the left option box while buy/sell items are being browsed
- Loot/reward popup item entries
- Modern Character Menu Equipment tab slot cards

Large renders are not used in compact inventory rows, compact equipment rows, or equipment slot summaries.

## Future Work

The manager caches both atlas crops and scaled renders, so later artwork replacement only needs matching render keys and manifest entries. Future layers such as rarity borders, elemental overlays, equipped/new/locked badges, or quest marks should be separate overlay assets rather than new item render variants.
