# The Forsaken Tenet Development Roadmap

*Updated: June 2026*

This roadmap tracks the remaining work for **The Forsaken Tenet** after the recent stabilization and coverage passes. Completed work is summarized briefly so the active backlog stays readable. Code, scripts, and legacy docs may still refer to the project as Dungeon Crawl until the rename is implemented as a separate cleanup pass.

## Status Legend

- `Done`: Implemented and covered well enough for current planning.
- `Active`: High-priority work for the next stabilization or polish pass.
- `Planned`: Valuable future work, but not the next thing to tackle.
- `Deferred`: Intentionally postponed until a dependency or design decision is clearer.

## Current Snapshot

### Foundation Status

- Core project structure is split across `src/core/`, `src/ui_curses/`, and `src/ui_pygame/`.
- EventBus infrastructure is in place and used by combat, presentation, audio, and diagnostics.
- Shared battle-engine extraction is complete enough that UI layers are thinner, though UI-specific orchestration remains.
- Data-driven ability migration is substantially complete with `180` YAML ability definitions.
- Pygame dungeon, town, combat, popup, and menu flows are functional, with remaining polish work concentrated in UX consistency and visual presentation.
- Visual character creation now includes the selected portrait and sex/race/class identity on the naming screen.
- Large item-render artwork is integrated for selected-item presentation contexts while compact lists continue to use small icons.
- Large item artwork now uses approved transparent individual PNGs organized under `src/ui_pygame/assets/item_art/` for regular, key, and special inventory selected-item views.
- Combat simulator, battle logger, save diagnostics, renderer diagnostics, audio diagnostics, and gameplay-stat summaries are implemented.
- Sound/music runtime integration is active, but final content assets are still incomplete.

### Verified Repo Metrics

- Test files under `tests/`: `102`
- YAML ability definitions under `src/core/data/abilities/`: `180`
- Event types in `EventType`: `38`
- Latest full-suite result recorded in prior roadmap notes: `1398` passing tests with `81%` total coverage across `src/`

## Narrative Direction

Current title: **The Forsaken Tenet**

The title points to the central mystery without revealing it early. The forsaken tenet is **Voluntas**, the forgotten seventh principle of reality: Choice and Free Will. Vesperion forsook his duty as its Guardian, history forgot it, the world lost it, and the player rediscovers it late in the story.

### Core Mythology

Before time and before the mortal races, there was only **Elysia**, the First Light and source of all creation. To give structure to reality, Elysia established Seven Principles, each embodied by a Guardian:

1. `Triangulus`: Self, expressed through Mind, Body, and Spirit.
2. `Quadrata`: Order.
3. `Hexagonum`: Nature.
4. `Luna`: Love.
5. `Polaris`: Guidance.
6. `Infinitas`: Eternity and endless struggle.
7. `Voluntas`: Choice and Free Will.

From the Seven Principles came all life and all races. No mortal people are favored or chosen above another; humans, elves, dwarves, halflings, gnomes, and all other peoples are equally children of Elysia and equally shaped by the Seven Principles.

The missing seventh Principle is `Voluntas`. Voluntas gives moral meaning to the other six. Without it, Self becomes programming, Order becomes tyranny, Nature becomes instinct, Love becomes obligation, Guidance becomes control, and Eternity becomes imprisonment.

### Antagonist And The Hollowing

The Great Evil is **Vesperion**, the former Guardian of Voluntas, a celestial being associated with wisdom, light, and the Evening Star. Vesperion is not driven by simple conquest. After witnessing war, betrayal, cruelty, greed, grief, and loss, he came to believe Voluntas was Elysia's mistake. To him, free will is not a gift but a disease that produces endless suffering.

Believing he was acting mercifully, Vesperion attempted to remove Voluntas from existence. This event became known as **The Hollowing**. The world was not destroyed, but something fundamental was lost. The Seventh Principle disappeared from memory, and history slowly rewrote itself until most of creation believed there had only ever been six principles.

### Story Roles

- The six relics are real and powerful, but incomplete. The surviving Guardians left them as safeguards designed to guide a future champion toward the forgotten truth. Over centuries, their original purpose was forgotten and they became objects of legend.
- The hero begins as an ordinary adventurer tasked with recovering the Six Relics to stop the Great Evil. The expected story is simple: gather the relics, defeat the Great Evil, save the world. The late-game turn reveals that this understanding is incomplete.
- The Hooded Figure should ultimately be a hidden servant or witness of Voluntas, guiding the hero toward forgotten truth rather than toward raw power.
- The Acolyte should embody Vesperion's argument instead of serving as a simple villain. Their belief should come from suffering and the sincere conviction that removing free will would prevent more pain.

### The Liminal Gap And Voluntas Reveal

After the first confrontation with Vesperion, the hero is defeated or killed. The player's soul awakens in **The Liminal Gap**, a surreal realm between existence and oblivion. It should feel abandoned, dreamlike, distorted, familiar, and wrong, with fragments of memory, forgotten truths, and remnants of ancient souls drifting through it.

The Liminal Gap is one of the few places untouched by the Hollowing, so traces of the Seventh Principle remain there. The Six Relics awaken and guide the player toward surviving echoes of the Six Guardians. These should not become a repetitive sequence of boss fights; each Guardian presents a unique trial reflecting its principle. Some trials may involve combat, while others involve understanding, sacrifice, exploration, or difficult decisions.

Completing the trials reveals hidden lore about Elysia, the Seven Principles, the Hollowing, and Vesperion's fall. After the six trials, the player discovers there should be a Seventh Guardian. The seat of Voluntas stands empty because Vesperion himself was once its Guardian, and the principle was deliberately removed from history.

The player eventually discovers that Voluntas was never truly destroyed. Unlike the other principles, Voluntas cannot exist as a relic, artifact, or monument. It exists wherever a soul chooses.

The path to Voluntas culminates in a Reflection Battle against a self-copy representing every path not taken and every possible version of the hero. The player must prove they possess Voluntas by affirming their identity and exercising true choice. Defeating the reflection symbolizes embracing the path the player has chosen through class, promotion, equipment, and playstyle.

Class progression should therefore become part of the story's argument. Promotions and build choices are not only mechanics; they are evidence that the hero is shaped by will rather than destiny.

### Final Conflict

The final confrontation is not framed as simple good versus evil. It asks whether free will is worth the suffering it creates.

Armed with the truth, the hero returns from The Liminal Gap and confronts Vesperion once more. Vesperion argues that removing Voluntas will end suffering. The hero answers that without Voluntas, love, sacrifice, courage, redemption, and growth cannot exist. The fate of creation rests on whether the Seventh Principle should survive.

## Completed Summary

### Core Combat And Ability Work

Status: `Done`

- Critical combat bugs are resolved, including Charge stun behavior, Arcane Blast mana guarding, Mana Shield cleanup, Jump forced-action cleanup, Berserk/Jump ordering, and duration-1 incapacitation turn consumption.
- Core battle logic is extracted into the shared battle engine.
- Ability execution is standardized around structured combat-result style outputs.
- The YAML/data-driven ability migration covers the major planned batches, including offensive spells, healing/buffs/debuffs, multi-hit and conditional abilities, weapon/status skills, death/composite/stat-reduction effects, toggles, enemy skills, equipment skills, Maelstrom, Disintegrate, Inspect, Purity Body, Resurrection, and Resist All.
- Status interactions, immunity handling, and multi-turn combat behavior have been improved.
- Enemy AI now has status-aware ability selection, Copycat support, charging telegraph support, Cambion acolyte support behavior, and selected-action metadata for priority/delay/telegraph inspection.

### Balance And Progression Foundations

Status: `Done`

- Initial balance pass is complete for the original stabilization scope: Clannfear buff, Laser2 redesign, weapon crit rebalance, Disarm total-output handling, Mimic scaling, Half Giant drawback tuning, and Old Key reward increases.
- Combat simulator tooling supports deterministic seeding, generated player baselines, promotion-tier progression modeling, structured JSON exports, and compact balance summaries.
- Race identity has an initial always-on trait pass that preserves broad race strengths and weaknesses.

### Save, Logging, Diagnostics, And Statistics

Status: `Done`

- Save/load robustness has been significantly hardened: atomic writes, filename confinement, deterministic save listing, temp/directory filtering, corrupt JSON handling, visible-save metadata, save-directory diagnostics, tile-state restoration diagnostics, and collect-quest compatibility.
- Gameplay statistics are tracked, saved, normalized, grouped, and visible from the pygame town Statistics entry.
- BattleLogger supports structured payloads, JSON file export, compact summaries, event/flag counts, actor/target counts, and positive damage attribution.
- EventBus diagnostics expose history/subscriber summaries, retained capacity, full state, and sorted event-type lists.
- Renderer diagnostics expose texture fallbacks, projected-surface cache state, surface-slot overrides, panel summaries, and grouped fallback keys.

### Pygame Stabilization

Status: `Done`

- Pygame stale-input protection is implemented across high-traffic menu, popup, combat, shop, town, character, dungeon, inventory, equipment, quest, save/quit, and unlock-key flows.
- Shared popup background fallback behavior is hardened for empty/live-screen/broken providers.
- Combat UI now has status-icon priority, overflow, urgent coloring, label fitting, counted duplicate labels, Maelstrom stack visibility, Blind Rage labeling, telegraph-colored log lines, a dedicated telegraph banner, and long-name fitting.
- Dungeon renderer coverage and fixes now cover defeated-boss visuals, minimap door/chest state, side-door behavior, Ore Vault door rendering, side-corridor floor/ceiling/wall slot routing, side-view chest orientation, soft vignette framing, and texture override diagnostics.
- The P2 renderer/exploration presentation pass added Rotator, active FunhouseTeleporter, and visited-only FakeWall/Fake Path translucent wall presentation without revealing hidden fake walls, smoothed the pygame load progress popup, and expanded structural-depth side-opening smoke coverage.
- Shop item lists support long-list paging, Home/End navigation, preserved-scroll clamping, item ranges, stat-themed names, and elemental metadata display.
- Pygame Character Menu now reports weapon-adjusted Attack and armor-adjusted Defense through the same core modifier paths used by combat/equipment previews.
- The modern Pygame Character Menu is the default town and dungeon character menu. It includes tabbed character/equipment views, race/sex portraits, grouped weaknesses/resistances, a paper-doll equipment layout with Helmet support, dual-wield attack display, item artwork, in-slot equipment details/buffs, and styled inventory equip-failure notices.
- Helmet equipment is now implemented across core equipment, save/load compatibility, curses and pygame shops, inventory/equipment popups, icon/artwork fallback, and Defense/resistance/invisibility modifiers. The current catalog includes Cloth, Light, Medium, and Heavy helmet progressions plus restricted and special-effect helmets.
- The medium ultimate armor reward is now Klivanion; its retaliation effect, shop flows, item maps, and tests use the renamed item and effect text.
- Character creation uses a visual naming screen with portrait preview plus selected sex, race, and class details.
- Selected-item contexts now use individual large item artwork in inventory, equipment, shop, loot/reward, and modern Character Menu equipment views.

### Audio Runtime And Staged Content

Status: `Done` for runtime integration, `Planned` for final content completion

- SoundManager supports default audio diagnostics, checked-path reporting, `.wav` music assets, nested `sounds/new_sounds/` staged SFX, and location/context music themes.
- Pygame top-level locations request music themes for menu, town, shops, church, inn, dungeon, combat, boss combat, and final combat.
- Repeated music-theme requests do not restart the active track unless forced.
- Combat music restores the previous non-combat location theme after combat ends.
- Main-menu transitions and dungeon exits stop or replace stale music so dungeon music does not linger into menus/town.
- Staged SFX are wired for ice/frost spell and skill events, scream/howl/nightmare skills, Mortal Strike, shield blocks, underground spring interactions, and successful dungeon door opens.

## Ranked Remaining Backlog

### P0 - Current Playtest Regressions And Trust

Status: `Done`

Completed in the June 2026 P0 pass:

1. Fixed and covered the reported first-key-blocking issue after combat turn start.
   - Guarded input now pumps pygame events before reading physical key state.
   - Regression coverage verifies the combat action grid accepts the first fresh movement/confirm key once no key is held.
2. Re-ran focused playtest regression coverage for recently fixed areas.
   - Main-menu/dungeon music transitions.
   - Character Menu Attack and Defense stat display.
   - Enfeeble zero-value reporting.
   - Half Giant Warrior early-game balance.
   - Old Key locked-door prompt behavior.
   - Audio diagnostics and location/combat music routing.
3. Updated roadmap and playtest checklist entries for the completed P0 pass.

Next active priority: `P4 - Content And Systems Expansion`.

### P1 - Pygame UX Polish

Status: `Done`

1. Complete modern Character Menu acceptance and iteration.
   - Status: `Done` for the current UX pass.
   - Implemented: sex-first character creation, race/sex portrait assets, base portrait atlas loading with individual PNG fallback support, reusable portrait composition/caching for future overlays, native-ratio portrait frame sizing, generic Character/Equipment tabs, wider 60/40 Character and Combat Stats panels, wider right-column level-progress bar using current-level XP progress, dual-wield main/offhand Attack display, larger right-aligned Name/Race/Class/Level text, Core Attributes positioned below the experience bar, larger character/combat/resistance text, right-aligned core/combat values, static side-by-side weaknesses/resistances block for all 10 resistance keys, panel dividers, spread-out paper-doll Equipment tab with an active Helmet equipment slot, larger equipment blocks with optional icon boxes and right-aligned subtype/base weapon/armor/block/weight/resistance details, in-slot equipment-buff reporting, popup quick-scroll and wrapped item descriptions, and town/dungeon opt-in routing.
   - Portrait implementation note: runtime prefers `base_portrait_atlas.png`/`.json`; the loader supports both the current `assets/portraits/` drop location and the suggested future `assets/portraits/base/` plus `fallback_individuals/` layout.
   - Item artwork implementation note: selected-item views use individual transparent artwork from organized `assets/item_art/` subdirectories through exact mappings in `assets/item_render_map.json`; dense rows and compact slot summaries still use the small icon system.
2. Replace current shop mode-selection flow with shop tabs.
   - Status: `Done`.
   - Type selection remains in place for shop categories, while item sub-types are now browsed with tabs in the buy list.
   - Implemented for town shops and secret-shop grouped categories, with left/right tab navigation and filtered empty tabs.
3. Revisit combat visual polish.
   - Current status/telegraph readability is strong enough for baseline play.
   - Status: `Done`.
   - Lightweight hit/spell/skill effects are implemented as transient procedural overlays on confirmed damage events, using muted impact strokes, rings, sparks, and elemental glows that sit over the current enemy renderings without changing combat mechanics.
   - Confirmed damage also produces compact floating damage text at the target, confirmed healing produces compact floating healing text, and enemy hits add a brief recoil nudge so successful impacts read immediately without changing combat timing.
   - Low player HP now adds a restrained combat-area danger vignette so near-death state is visible while preserving the dungeon-backed combat scene.
   - Spell, skill, item, and totem selection now use an in-combat bottom command panel instead of a full combat-area modal, and confirmed selections redraw the battlefield before damage effects play.
   - The combat action menu now compacts up to three rows of actions and truncates long labels so debug/expanded action sets do not overflow the bottom command panel.
   - Combat log rendering now pages over wrapped visible lines so long messages stay inside the log panel, keep source-message colors across wrapped continuations, and use subtle category ticks for faster scanning.
   - Enemy telegraphs now render as a compact `Incoming` warning strip near the combat target area.
   - The bottom action panel has an initial darker stone/parchment treatment with clearer selected-action framing.
   - Defend status presentation now treats `DEF` as a positive icon and the base Defend action expires after one turn unless selected again.
   - Vision and reveal-based enemy details are now suppressed in boss fights, preserving boss mystery while keeping ordinary encounter inspection intact.
4. Modify the character naming screen.
   - Status: `Done`.
   - Added a visual naming screen with selected portrait, sex, race, and class panels.
   - Replaced the basic text-entry flow in pygame character creation with the guarded visual naming screen.
5. Update enemy presentation around approved transparent sprites.
   - Status: `Done`.
   - Retired the broad-archetype `enemy_renders/` atlas and `enemy_combat_art/` presentation layer to `old_assets/retired_enemy_art/`.
   - `EnemyCombatSpriteManager` now owns enemy display-name lookup, boss/category fallbacks, combat target-panel presentation, and dungeon boss navigation figures.
   - Added `EnemyTokenManager` as a compact middle layer derived from combat sprites for initiative/turn UI and future target-list or encounter-summary use.
   - Added `EnemyCombatSpriteManager` and `assets/enemy_combat_sprites/` as transparent full-body battlefield enemy sprites for the center combat renderer, with legacy 32x32 sprites retained only as fallback assets.
   - Production enemy combat sprites now cover every concrete enemy display name in `src/core/enemies.py`, excluding the development `Test` enemy and the base `Myrmidon` template.
   - Added `enemy_combat_sprite_scale.json` so large creatures can use per-enemy combat scale multipliers without changing every shared-canvas sprite.
   - Combat sprite review sheets can be rebuilt from approved transparent PNGs with `./.venv/bin/python tools/build_enemy_combat_sprites.py`.
6. Expand realistic item artworks to include images for all items.
   - Status: `Done` for regular inventory, key inventory, and special inventory selected-item artwork.
   - Approved individual transparent PNGs cover weapons, armor, helmets, offhands, accessories, potions, scrolls, keys, quest materials, status remedies, story items, Unobtainium, Dead Soldier, and the relic item-art variants.
   - Natural/enemy-only equipment, empty equipment slots, summon-only natural objects, and compact row icons remain intentionally outside the large item-art set.
   - The retired generic item render atlas has been removed; selected-item views resolve exact item artwork from `src/ui_pygame/assets/item_art/`.
7. Update dungeon renderings to match new aesthetic.
   - Status: `Done`.
   - Implemented: manifest-driven dungeon texture loading, painterly replacement wall/floor/ceiling/door textures, approved 256x256 roots/fungus tile art, decorative render hooks for rubble/roots/fungus/crystals/bones/broken gear, deterministic torch/sconce wall overlays, richer Tiled JSON gameplay-layer selection, chunked/infinite map support, funhouse boundary-wall rendering, and stable appended authoring tiles for future flexible maps.
   - Art usage note: new dungeon tile art is documented in `docs/DUNGEON_TILE_ART.md`; maps should use the decorative tile classes for gameplay/world placement and the manifest keys for renderer-only texture variants.
   - Gameplay note: decorative tiles are currently traversable visual/message hooks only; harvesting, debris destruction, crystal mana interactions, poison/fungus effects, and salvage remain future gameplay work.
   - Generate new floor, ceiling, and wall tiles
      - dungeon becomes more weathered as you go deeper
      - upper levels have torches/sconces but they may be broken/unlit further down
   - Expand tileset to add dynamic gameplay
      - crumbling rocks, dead ends (stalagmite/stalactites)
         - gameplay elements can be added to remove debris/destroy obstructions to reveal paths
      - roots, fungus, lichen
         - can be farmed/gathered for use
         - can affect abilites or enemy strength
         - can poison or cause other status effects
      - crystal formations
         - can be gathered or used to regen mana or power class mechanics
         - can effect spells or become projectiles in combat
      - bones, sinew, fur
      - broken equipment, random items (usable and unusable)

### P2 - Renderer And Exploration Presentation

Status: `Done`

1. Continue renderer smoke-test work around structural-depth and side-corridor behavior.
   - Preserve center-wall stopping behavior.
   - Preserve valid depth-2/depth-3 side floor, ceiling, wall, and door routing.
   - Added structural-depth smoke coverage for blocking center walls with visible side openings, preserving side-corridor wall presentation and the depth-2 center floor/ceiling slots reused for side-lane routing.
2. Continue door and side-opening presentation validation.
   - Keep hidden/detected/open Ore Vault behavior stable.
   - Preserve single-side-door visibility unless playtesting says it is confusing.
3. Finish special-tile placement polish for future floor-bound props.
   - Existing defeated-boss, spring, chest, door, and side-special coverage is useful; extend it only for concrete new props or regressions.
   - Started P2 polish by rendering Rotator and active FunhouseTeleporter tiles as floor-bound special sprites, with repo-relative asset resolution and smoke coverage for inactive teleporter fallback behavior.
   - Added visited-only FakeWall/Fake Path presentation so revealed fake paths show a translucent normal wall panel while hidden fake walls remain visually indistinguishable from ordinary walls.
   - Replaced the revealed FakeWall/Fake Path wall-texture sprite marker with full-panel translucent wall presentation and added side-corridor smoke coverage.
4. Keep asset fallback diagnostics visible during renderer changes.
   - Use existing grouped fallback and panel-slot diagnostics before adding new debug helpers.
5. Gameplay element refinement.
   - The load bar when loading a game is jumpy instead of a smooth progression.
   - Smoothed the pygame load progress popup with time-based 60 FPS interpolation while preserving the existing load-game flow and debug/test compatibility.

### P3 - Core Refactoring And Test Confidence

Status: `Done`

P3 closure note: the remaining work after the final audit is future content or
opportunistic refactoring. There are no explicit `pytest.mark.skip` or `xfail`
tests left in the focused test tree search, and passive Power Up placeholders
remain P4 content work rather than P3 blockers.

1. Continue effects-system integration beyond the migration.
   - Replace older inline combat logic in legacy ability code with composable effects where practical.
   - Keep output formats consistent between legacy and YAML abilities.
   - 2026-06-16: Started the P3 effects audit and cleaned up stale primitive effect contracts. See
     `docs/P3_EFFECTS_AUDIT.md`; next work is result-shape contract coverage before deeper combat-pipeline extraction.
   - 2026-06-16: Added result-shape contract coverage for data-driven damage spells and weapon skills; weapon
     skills now populate `CombatResult.damage` from actual hit damage.
   - 2026-06-16: Aligned composed Stun application with `Character.apply_stun` so YAML effects respect the
     post-stun immunity window.
   - 2026-06-16: Reused the shared result reset helper for legacy base `Spell.cast()` and `Skill.use()` paths so
     old-style reusable ability instances do not leak stale messages, effect buckets, or damage fields.
   - 2026-06-16: Audited primitive `DamageEffect` registration: it remains available for custom `EffectFactory`
     definitions, while built-in YAML abilities are now covered to ensure they do not use `type: damage`.
   - 2026-06-16: Aligned reflected data-driven damage spell results with the actual damaged target and record
     the original reflector in `CombatResult.extra["reflected_by"]`.
   - 2026-06-16: Aligned legacy `ElectricSpell` stun messaging with `Character.apply_stun()` so post-stun
     immunity does not produce false “stunned” text.
   - 2026-06-16: Added a representative concrete legacy-vs-YAML burn contract comparing legacy `FireSpell`
     and data-driven `Fireball` DOT behavior.
   - 2026-06-16: Fixed data-driven spell effect-message detection by snapshotting effect buckets by value
     instead of sharing the mutable bucket lists.
   - 2026-06-16: Added a legacy `IceSpell` vs YAML `Ice Lance` extra-damage contract and routed
     `DynamicExtraDamageEffect` message templates through data-driven spell presentation.
   - 2026-06-16: Tightened the shared instant `HealSpell.cast()` path so legacy and YAML heals report and emit
     actual applied healing after caps and healing-received modifiers.
   - 2026-06-16: Extracted shared instant-heal application into `HealSpell._apply_instant_healing()` and routed
     YAML hybrid and out-of-combat heals through the same actual-healing helper.
   - 2026-06-16: Corrected composite Mana Shield/Crusader shield helper calls for weapon-spell follow-ups and
     related custom effects so they use the shared attacker/defender absorption helpers consistently.
   - 2026-06-16: Routed passive placeholder power-up hooks through the shared result reset helper so their
     interim `CombatResult` contracts do not leak stale reusable state.
   - 2026-06-16: Replaced the hidden `random_enemy()` debug override with explicit
     `set_random_enemy_override()` / `clear_random_enemy_override()` helpers for ability playtesting.
   - 2026-06-16: Wired `DUNGEON_FORCE_ENEMY` into the random enemy override path so debug launchers can force
     ability-test encounters without code edits.
   - 2026-06-16: Clarified `Character.handle_defenses()` / `damage_reduction()` as active shared spell/effect
     defense contracts rather than stale stubs.
2. Expand high-value automated coverage.
   - Ability effects across the full ability set.
     - 2026-06-16: Added a combat-ready YAML catalog smoke test covering all 179 ability files and removed an
       obsolete file-missing skip from fixed Batch 1 spell coverage.
     - 2026-06-16: Added legacy base `Spell`/`Skill` result lifecycle regressions to complement the YAML
       result-shape contracts.
     - 2026-06-16: Added a catalog audit test proving built-in YAML abilities avoid primitive `DamageEffect`
       entries.
     - 2026-06-16: Added legacy/YAML burn comparison coverage for fire spell DOT presentation and state.
     - 2026-06-16: Added legacy/YAML ice comparison coverage for extra-damage presentation and state.
     - 2026-06-16: Added legacy/YAML heal coverage for capped healing and healing-received modifiers.
     - 2026-06-16: Added YAML `cast_out()` heal coverage for capped actual-healing reporting.
     - 2026-06-16: Added result lifecycle coverage for passive placeholder power-up hooks while their final
       gameplay effects remain future content work.
   - Status-effect interaction scenarios.
     - 2026-06-16: Added focused coverage for effect-driven Stun versus post-stun immunity.
     - 2026-06-16: Added turn-tick ordering coverage for Poison, burn DOT, Bleed, and Regen cleanup.
     - 2026-06-16: Fixed and covered finite Silence expiry while preserving `duration=-1` indefinite Silence.
     - 2026-06-16: Reused the shared Mana Shield absorption helper from `handle_defenses()` and covered
       shield depletion with leftover damage and depletion events.
     - 2026-06-16: Added reflected damage-spell result coverage so presentation/result consumers see the
       redirected target.
     - 2026-06-16: Added Smite follow-up coverage for Mana Shield absorption messages and mana consumption.
     - 2026-06-16: Added Sleep/Prone interaction coverage proving Prone recovery waits until the tick after
       Sleep expires.
     - 2026-06-16: Added legacy electric-stun coverage against the post-stun immunity path.
   - Enemy AI behavior where tactical choices are meaningful.
     - 2026-06-16: Added priority-stack coverage for redundant target-status skips and target-positive-effect
       Dispel selection; refreshed Attack fallback assertions to match the engine's `("Attack", None)` contract.
     - 2026-06-16: Re-enabled real random enemy catalog selection by default and validated explicit debug
       enemy overrides for targeted ability playtesting.
     - 2026-06-16: Added environment-variable coverage for forced random encounters, including explicit helper
       precedence and reset behavior.
     - 2026-06-16: Fixed enemy consumable selection so Elixir/Megalixir count as mixed health/mana recovery
       items instead of looking only for an unused `Both` subtype.
   - Quest completion/reward flows.
     - 2026-06-16: Added item-collection quest coverage for partial progress, item-instance matching, and
       no duplicate completion messages after completion.
   - Save/load round trips only when new persistence risks appear.
3. Continue targeted type hints and docstrings.
   - Highest-value modules: `abilities.py`, `items.py`, `enemies.py`, and follow-up `character.py` cleanup.
   - Keep type-hint work scoped to clear behavior boundaries rather than broad rewrites.
   - 2026-06-16: Added a typed signature and behavior docstring to `Player.quests()` to clarify enemy, item,
     and relic completion paths.
   - 2026-06-16: Added typed signatures around class promotion rule application and `Job` equipment checks,
     with focused coverage for spellbook transitions, helmet defaults, and accessory slot rules.
   - 2026-06-16: Tightened base legacy `Ability`, `Skill`, `Spell`, `Attack`, and `HealSpell` entry-point
     signatures to reflect optional targets and flexible kwargs without changing runtime behavior.
   - 2026-06-16: Added typed `use()` signatures to remaining consumable/stat/status potion and Sanctuary
     scroll overrides so they match the base item call contract.
   - 2026-06-16: Corrected loot helper type contracts so `random_item()` and the rarity cache are typed as
     item-class factories, matching existing inventory and loot-table usage.
   - 2026-06-16: Tightened enemy catalog helper types around random encounter selection, debug enemy
     overrides, fixed resistance maps, and spellbook construction.
   - 2026-06-16: Added typed signatures to `DataDrivenHealSpell` cast, hybrid heal, HoT, and out-of-combat
     heal helpers after consolidating instant-heal behavior.
   - 2026-06-16: Added typed signatures to data-driven support/status spell `cast()` methods and pinned
     Cleanse's default-target presentation.
   - 2026-06-16: Added typed signatures to data-driven weapon/custom spell constructors and `cast()` methods
     after the shield-helper cleanup, keeping Smite and Turn Undead wrapper contracts explicit.
   - 2026-06-16: Extended typed signatures across the remaining data-driven charging, magic-missile, Jump,
     and movement wrapper entry points.
   - 2026-06-16: Added focused `character.py` type aliases and attribute annotations for effect maps,
     inventories, ability books, weapon-damage results, and defense-resolution tuples.
4. Remove easy skips or placeholder tests where missing functionality is now small enough to implement.
   - 2026-06-16: Audited the test tree for explicit `pytest.mark.skip` / `xfail` usage; no actionable skipped
     tests remain in the focused search.
   - 2026-06-16: Deferred passive Power Up final gameplay effects and item/content TODOs to P4 because they are
     feature/content work rather than missing P3 refactoring coverage.

### P4 - Content And Systems Expansion

Status: `Active`

P4 is split into smaller tracks so low-risk content and polish can move while larger systems remain explicitly decision-gated. Status labels:

- `Ready`: scoped enough to implement after normal code/data inspection.
- `Needs Exploration`: inspect current data, UI, save, or engine shape before implementation.
- `Needs Design Decision`: product/design choice required before implementation.
- `Deferred`: intentionally postponed until a design spec or prerequisite exists.

#### P4a - Immediate Content And UX Wins

Status: `Complete`

Implemented:

- Added post-fight/tavern comments, Sergeant relic and Warp Point hints, and staffed Warp Point scientist flavor.
- Added one-handed/two-handed weapon details to equipment previews and equipped-slot inspection details.
  - Equipment slots show `(1H)` or `(2H)` for weapons; equip popups use the weapon name suffix without a separate Hands row.
  - Equipment replacement popup detail titles show `(1H)` for one-handed weapons and `(2H)` for two-handed weapons.
- Preserved inventory sort selection when reopening the Character Menu inventory popup.
- Aligned ordinary player/enemy combat log lines with player blue/enemy red while preserving outcome colors for damage, healing, misses, and resists.
- Expanded combat-log color classification for item special-effect style messages.
- Rebalanced Smoke Screen to cost 0 MP.
- Tuned Bandit post-steal AI so Smoke Screen is strongly favored across a longer `Steal Success` retry window, but not guaranteed.
- Replaced status-effect initials with larger standalone effect artwork where current assets exist, with text fallback for missing icons.
- Removed the duplicate Hands row from equipment replacement popups.
- Moved save loading and manager initialization into the pygame progress popup lifecycle so the load bar does not complete before the expensive restore work runs.
- Bosses and the Waitress suppress Vision enemy-detail reveals in the pygame combat view.
- Added enemy HP/MP labels when Vision-style enemy details are visible and the enemy has mana.
- Added limited ability-specific visuals:
  - Mana Shield creates a blue force field glow around the user.
  - Mirror Image uses duplicated sprite shimmer only.
  - Smoke Screen creates a foot-level smoke burst that rises to obscure the target; the enemy fades out and stays hidden through the flee transition.

#### P4b - Quest And Realm Content

Status: `Closed` for Class Ring activation, current quest/realm additions, Realm of Cambion current scope, Vesperion first-confrontation false-final path, Liminal Gap hub shell, six lightweight Guardian trial story shells, Liminal guide clue review, Guardian trial consequences, Voluntas clue aggregation, Seventh Seat reveal, Acolyte tragic mirror scene, Reflection/Psychopomp Liminal combat shell, Reflection path mirroring, Reflection retry tracking, Liminal return, true-final re-entry, Vesperion `Choose Fate` Guardian counters, Vesperion phase-pressure Guardian counters, true-final victory resolution, ending sequence, tavern epilogue, and main storyline/Vesperion/endgame plot direction. Deferred/future polish now tracks bespoke Guardian trial rooms or mini-bosses, deeper Reflection behavior, final Vesperion balance/presentation polish, broader Waitress/Joffrey/busboy rewrites, and deeper Realm of Cambion expansion.

Implemented:

- Quest: Rookie Mistake
   - Removed the second generic town-entry completion popup after the event popup.
   - Added a floor marker at the Rookie location using the Dead Soldier item artwork.
   - Changed the post-Rookie encounter to Zombie instead of a random enemy.
- Realm of Cambion current scope:
   - Completed the current P4b Realm flow: Underground Spring entry/return, configured portal pairs and fallback exit, rotator movement, anti-magic terminal code `2749`, Merzhin victory collapse/exit/tile cleanup, and Merzhin defeat return without normal town death.
   - Confirmed existing renderer coverage for portal, rotator, active FunhouseTeleporter, and visited FakeWall/Fake Path presentation; no new Cambion special tile class is required until a concrete content beat needs one.
   - Added pygame regression coverage for Merzhin victory and defeat return handling.
- Realm of Cambion content expansion:
   - Added non-modal flavor messages for portal travel, rotator movement, and anti-magic terminal state.
   - Added Nimue follow-up dialogue after `The Wizard's Folly` is turned in.
   - Added small post-Merzhin Barkeep, Soldier, and Busboy town reactions using existing late-game patron dialogue.
- P4b town response content:
   - Added post-fight tavern dialogue variants for Jester and Realm of Cambion progress.
   - Added subtle Busboy and Soldier hints for portal/Cambion aftermath.
   - Added one-time milestone supply deposits to the Barracks storage locker for selected turned-in quests.
- P4b town presentation hooks:
   - Added contextual town-menu location details for the Sergeant/Barracks, tavern patrons, shop purveyors, Church priest, Old Warehouse guards, and staffed Warp Point scientists.
- Bring Him Home presentation hook:
   - Added a post-turn-in Timmy/family scene after the Sergeant receives the completed quest.
- Dragoon Dragon Quest:
   - Implemented the Lancer/Dragoon-only Recover Jump alternate Red Dragon resolution: active `Recover` restores Kaelenon's lost humanoid transformation ability, has no low-HP requirement, does not heal the Red Dragon's HP, and resolves the encounter for existing Red Dragon progression.
   - Added saved Dragoon dragon quest state for Kaelenon restoration, Cambion portal key, Kaelenon's return home, Draconite, and Draconite Pendant crafting.
   - Extended the Realm of Cambion anti-magic terminal with Kaelenon's portal-key and return-home scenes.
   - Added `Kaelenon's Portal Key`, `Draconite`, and `Draconite Pendant`; the Jeweler crafts the pendant from Draconite, and the pendant strengthens Jump `Recover` HP/MP restoration.
- Class Ring activation and new class mechanics:
   - Added `docs/CLASS_RING_ACTIVATION_SPEC.md` covering Grandmaster of Arms, Demonologist, Archdruid, and legacy second-promotion ring directions.
   - Replaced the old monolithic `src/core/classes.py` with the `src/core/classes/` package while preserving public class imports.
   - Implemented Grandmaster of Arms weapon disciplines, Class Ring binding/rebinding, Secret Master Barracks hall, trial combat handling, weapon techniques, save state, and regression coverage.
   - Implemented Demonologist crypt access, fiend contracts, active patron binding, `Call Contract`, familiar imprisonment, empowered contracts, new fiend patrons/enemies, save state, and regression coverage.
   - Implemented Archdruid fourfold attunement, Ancient Grove town option, deterministic catalysts, aspect rituals, mastery caps, Harmony Bonus, save state, and regression coverage.
   - Implemented Berserker No Healing Duel activation through the Barracks, including visible-ring gating, no-normal-reward trial combat, no-healing failure handling, ring awakening, and regression coverage.
   - Implemented Dragoon Guard The Fall and Stalwart Defender Siege Trial activations through the Barracks, including visible-ring gating, no-normal-reward trial combat, ring awakening, and regression coverage.
   - Implemented Wizard Four Formulae, Shadowcaster Debt Cap Trial, Knight Enchanter Arcane Duel, and Grand Summoner Conduit Ritual activations through the Church, including visible-ring gating, ring awakening, Grand Summoner HP sacrifice, and regression coverage.
   - Implemented Rogue Loaded Game, Seeker Cartographer's Proof, Ninja No-Trace Contract, and Arcane Trickster Impossible Theft activations through the Old Warehouse, including visible-ring gating, late-game Old Warehouse access alongside Warp Point, ring awakening, and regression coverage.
   - Implemented Templar Relic Defense, Master Monk Purity Rite, Archbishop Miracle Vigil, Troubadour Lost Ballad, Lycan Control Rite, Astromancer Star Chart, Soulcatcher Ancestral Totem Rite, and Beast Master Pack Trial activations through the Church, including visible-ring gating, ring awakening, and regression coverage.
   - Added legacy second-promotion Class Ring awakening state, dormant/awakened descriptions, activation helpers, and live hooks for the legacy class-kit effects.
   - Implemented the full legacy class-kit pass for the ring-backed classes: Berserker Battle Scars, Spell Stealer/Arcane Trickster scroll-based spell theft, Bard/Troubadour songs and Encore, Wizard six-school affinity text/status, Lycan Moon Cycle and Frenzy Lock, Stalwart Defender Resolve, Grand Summoner future summon scaling, and status descriptions for the remaining legacy helpers.

Specified:

- Main Storyline Plot and Vesperion boss concept:
   - Added `docs/MAIN_STORYLINE_PLOT_SPEC.md`.
   - Replaced the old Devil-centered final reveal direction with Vesperion, the former Guardian of `Voluntas`.
   - Locked the Hooded Figure as a hidden Voluntas guide rather than Vesperion.
   - Locked the busboy as Vesperion in disguise, manipulating the Waitress/Joffrey tragedy to observe the hero.
   - Locked the Acolyte as a former failed hero who voices Vesperion's mercy-through-control argument narratively without joining the final fight mechanically.
   - Added an initial distinct Vesperion enemy concept and Vesperion-specific `Choose Fate` path; Balor remains separate and does not use `Choose Fate`.
- Vesperion false-final to Liminal Gap stub:
   - Added persistent `main_story` state for Vesperion/Liminal progression and legacy-save defaults.
   - Added the first Vesperion confrontation scripted transition at 70% HP, after three Vesperion turns, or on player death before that threshold.
   - Added Liminal Gap recovery that clears temporary combat effects, restores HP/MP to 50%, and preserves spent consumables.
   - Added a final-room re-entry blocker while `vesperion_false_final_triggered` is true and `true_final_unlocked` is false.
- Liminal Gap hub shell:
   - Added a real navigable hub map on the new Liminal Gap level.
   - Revealed the Hooded Figure as the wounded Liminal guide while reserving the fuller angelic reveal for later.
   - Added guide-only save access, no-exit blocker messaging, and six named sealed Guardian gates.
   - Added `main_story` state for guide reveal/save and Guardian trial completion placeholders.
- Lightweight Guardian trial story shells:
   - Activated all six Guardian gates as non-combat story-choice trials: Triangulus, Quadrata, Hexagonum, Luna, Polaris, and Infinitas.
   - Records trial started/completed state, the selected Guardian answer, and a Guardian-specific Voluntas clue placeholder.
   - Added Hooded Figure clue review for awakened Guardian clues and current Liminal progress.
   - Added small one-time principle consequences for completed Guardian trials, including resource recovery, defensive order, and clearing misdirection.
   - Keeps bespoke trial rooms, puzzles, combat variants, and mini-boss encounters reserved for later slices.
- Main storyline endgame plot chain:
   - Locked the post-trial route as six Guardian clues, empty Seventh Seat, Voluntas reveal, Acolyte tragic mirror, Reflection/Psychopomp, return from The Liminal Gap, and true Vesperion final.
   - Defined the six Guardian clue meanings and the Seventh Seat reveal: Voluntas is not a relic or external power, but the act of choosing itself.
   - Locked the Hooded Figure reveal cadence from wounded Liminal guide to surviving Witness of Voluntas, with fuller angelic nature reserved for a later reveal.
   - Locked the Acolyte as a non-combat tragic mirror who remains convinced by Vesperion's mercy-through-control argument.
   - Defined the Reflection/Psychopomp as affirmation of the player's chosen build, class, promotion, relic journey, and Guardian answers rather than a single correct build test.
   - Defined the true-final busboy/Waitress/Joffrey reframing without erasing the human grief of that tragedy.
- Main storyline endgame route implementation:
   - Added route flags for Seventh Seat reveal, Acolyte Liminal scene, Hooded Figure Witness reveal, Liminal return, Reflection defeat, Voluntas reveal, and true-final unlock.
   - Added Liminal hub story tiles for the empty Seventh Seat, Acolyte tragic mirror, and Reflection/Psychopomp.
   - Implemented clue aggregation so six completed Guardian clues open the Seventh Seat reveal.
   - Implemented Voluntas reveal, Hooded Figure Witness reveal, non-combat Acolyte scene, Reflection/Psychopomp route gating, return from The Liminal Gap, and true-final Vesperion prelude.
   - Replaced the Reflection/Psychopomp story resolution with a no-normal-reward Liminal combat shell that unlocks the true final on victory and returns the player to the Liminal hub on defeat.
   - Added Reflection path mirroring so the combat shell records the player's class/path profile and shifts martial, mystic, or hybrid action priorities.
   - Added Reflection attempt/failure tracking in `main_story` for retry-safe presentation and future tuning.
   - Added Vesperion `Choose Fate` Guardian-counter behavior so completed Guardian trials mitigate or cancel matching Vesperion consequences.
   - Added Vesperion once-per-phase battlefield pressure answered by all six Guardian trials across the three true-final phases.
   - Added true-final completion flags for Vesperion's defeat and main story completion.
   - Added true-final victory handling that bypasses ordinary XP, loot, quest completion, boss-tile defeat, town resurrection, and death-cost routing.
   - Added ending events for Vesperion's defeat and `The Forsaken Tenet` Voluntas ending.
   - Added a minimal post-ending tavern epilogue preserving the Waitress/Joffrey grief and acknowledging the Busboy/Vesperion absence without creating a postgame mode.
   - Added a completed-story final-room guard so the finale cannot restart after `main_story_complete`.

Deferred/Future Polish:

- Main Storyline Plot and The Liminal Gap:
   - Locked creation premise: Elysia established Seven Principles, each embodied by a Guardian, and all mortal races are equally children of Elysia.
   - Locked story beat: the first confrontation with Vesperion defeats or kills the hero and sends them to The Liminal Gap instead of normal town resurrection.
   - Locked objective: explore The Liminal Gap, complete the Six Guardian trials, gather clues, discover Voluntas, identify the secret to defeating a boss-like self-copy Psychopomp, then return to life.
   - Locked trial structure: Guardian trials should vary by principle and may use combat, understanding, sacrifice, exploration, or difficult decisions instead of repeating one boss-battle template.
   - Locked Reflection Battle: the self-copy represents every possible version of the hero and tests whether the player can prove Voluntas through a chosen path.
   - Locked NPC beat: a disfigured being guides and allows saving, then is revealed as an angelic guide who helps the player ultimately oppose Vesperion.
   - Implemented: clue aggregation/reveal thresholds, guide clue review, Guardian trial consequences, Seventh Seat scene, Acolyte Liminal scene, Reflection/Psychopomp combat shell, Reflection victory/defeat routing, Reflection path mirroring, Reflection retry tracking, return-from-Liminal placement, Vesperion re-entry, Vesperion `Choose Fate` Guardian counters, Vesperion phase-pressure counters, true-final victory resolution, ending events, UI messaging, migration behavior, and regression tests.
   - Deferred: bespoke Guardian trial rooms or mini-boss roster where appropriate, deeper Reflection self-copy behavior, richer final Vesperion phase/audio/visual presentation, balance tuning, and broader Waitress/Joffrey/busboy town-route rewrites.
- Realm of Cambion:
   - Current portal, rotator, anti-magic terminal, Merzhin win/loss, Nimue follow-up, movement flavor, and small post-Merzhin town reactions are implemented for P4b.
   - Defer deeper Realm of Cambion rooms, events, rewards, and special tiles until a concrete content beat is chosen.

Deferred Asset Pass:

- Artistic renderings for town NPCs/venues are deferred until art direction and target list are selected.
- Deferred targets include Sergeant/Barracks, inn patrons, shop purveyors, Church priest, Old Warehouse guards, staffed Warp Point scientists, and Bring Him Home family/child scenes.
- Do not generate or add new artistic assets until the desired visual style, asset dimensions, and target list are chosen.

#### P4c - Knowledge And Collection Systems

Status: `Closed` for the current per-save informational Bestiary scope. Account-style rewards/history remain deferred.

Implemented:

- Bestiary MVP:
  - Uses per-save defeated enemy records from `kill_dict`, which already round-trips through save/load.
  - Adds a read-only Bestiary popup to the Character Menu.
  - Displays defeated enemy names, categories, and defeated counts.
  - Displays enemy artwork when the combat sprite manager has art for that enemy.
  - Reveals stable enemy details only when the player had detail visibility while fighting that enemy.
  - Displays stable level/type, defeated count, one-row-per-resistance details, observed abilities, immunities, and special features without volatile enemy stat rolls.
- Bestiary Plus:
  - Records seen enemies per save at shared battle start without revealing details.
  - Keeps detail unlocks tied to combat detail visibility, so current Vision does not retroactively reveal old encounters.
  - Merges seen-only, defeated-only legacy, and detailed entries in the Character Menu Bestiary.
  - Adds compact Seen/Defeated/Detailed completion counts and per-entry Seen, Defeated, and Status rows.
- Bestiary closure polish:
  - Adds defeated-gated practical information without new save keys.
  - Shows coarse encounter locations for defeated enemies, including dungeon-level random encounter hints, Funhouse, chest Mimics, fixed boss rooms, Realm of Cambion, Liminal Gap, and final-room encounters.
  - Shows possible drops using broad labels such as `Guaranteed`, `Common`, `Uncommon`, `Rare`, and `Very Rare`, without exact percentage claims.
  - Preserves layered reveal rules: seen entries show identity only, defeated entries add practical info, and detail-visible entries add mechanics/abilities/resistances.

Current Scope Complete:

- Boss lore and hand-authored encounter notes are not part of this closure slice and can become a later narrative/content pass if desired.

Deferred:

- Account-style persistent history remains out of scope until profile storage and migration rules are specified.
- Completion rewards, achievements, titles, and gameplay bonuses remain deferred; current Bestiary progress is informational only.
- Persistent gameplay history, run summaries, or account-style stats remain decision-gated beyond the current grouped run popup.

#### P4d - Equipment And Item Systems

Status: `Done` for the lightweight foundation/UX-validation slice. Heavier item-state systems remain deferred.

Implemented:

- Added shared equipment eligibility helpers for slot resolution and non-mutating equip checks.
- Added equip-after-buy prompts to pygame and curses shop purchase flows for blacksmith, jeweler, and secret-shop equipment categories.
- Multi-copy weapon purchases can equip one copy or dual-wield two eligible copies while leaving remaining purchased copies in inventory.
- Validated current equipment/item foundations, including cloth armor spell modifiers, elemental and resistance metadata, Tome/offhand details, ultimate armor effects, and enemy consumable-use behavior.
- Confirmed generated stat-themed equipment names remain display-only and do not replace canonical item names used by inventory, quests, saves, or drops.

Ultimate Helmet Outline:

- Cloth path: knowledge/ritual-focused acquisition, likely tied to Church or arcane research content.
- Light path: mobility/precision-focused acquisition, likely tied to Old Warehouse, scouting, or trickster content.
- Medium path: balanced martial proof, likely tied to Barracks or dungeon challenge content.
- Heavy path: endurance/guard-focused acquisition, likely tied to fortress, armor forge, or deep-dungeon survival content.

Deferred:

- Ultimate helmet acquisition remains outline-only; implementation is deferred until a dedicated Ultimate Helmet spec defines quest triggers, reward selection, UI text, save flags, class/armor eligibility, and tests.
- Durability, repair, broken-item, and shatter/loss rules remain deferred until a dedicated spec covers save compatibility, economy, combat, UI, and tests.
- Item identification remains deferred, including intelligence-based unidentified drop chance, identify scroll/shop access, inventory/shop/save behavior, and loot-display rules.
- Usable equipment/accessory active abilities remain deferred; equipped items do not gain active-use actions or durability costs in this slice.
- Armor speed and mobility penalties remain deferred; current weight and encumbrance behavior is unchanged.
- Equipment naming themes such as "Rapier of the Wolf" remain undecided and deferred.
- Random healing/mana refresher spots are deferred until dungeon interaction design is clearer.

#### P4e - Class Mechanics And Progression Kits

Status: `Partially Implemented`, `Needs Playtest` for full legacy class-kit balance and remaining non-legacy class specs

- Re-design Astromancer ultimate ability `TetraDisaster` after a reference audit across abilities, data, tests, saves, and UI text.
   - Astromancer is a prophet/time mage mix

Implemented:

- Grandmaster of Arms:
  - Implemented as a second-promotion class in the class package.
  - Added Weapon Discipline storage, XP gain, rank curve, accuracy/proc scaling, bound Class Ring weapon, weapon techniques, and save migration.
  - Added Barracks Secret Hall activation/rebinding gauntlets and trial reward/death handling.
- Demonologist:
  - Implemented as a second-promotion class in the class package.
  - Added Church Crypt unlock, fiend contract acquisition from kill history, active patron binding, contract quote/pay/resolve flow, familiar imprisonment, empowered contracts, and save migration.
  - Added Succubus, Maelephant, and Balor as supported fiend contract enemies.
- Archdruid:
  - Implemented as a second-promotion class in the class package.
  - Added Venom, Stone, Growth, and Storm attunement; Ancient Grove unlock; deterministic catalysts; aspect rituals; mastery caps; Harmony Bonus; and save migration.
- Class Ring foundation:
   - Existing second-promotion rings now have dormant/awakened descriptions, saved awakening state, activation helpers, and live class-kit mechanics hooks.
  - Berserker, Dragoon, and Stalwart Defender now have playable Barracks activation flows.
  - Wizard, Shadowcaster, Knight Enchanter, and Grand Summoner now have playable Church activation rites.
  - Rogue, Seeker, Ninja, and Arcane Trickster now have playable Old Warehouse activation jobs.
  - Templar, Master Monk, Archbishop, Troubadour, Lycan, Astromancer, Soulcatcher, Beast Master, and Crusader now have playable Church activation rites.
  - Paladin vow selection now persists from promotion, grants vow-specific skills, and feeds Crusader `Vow Trial` / `Vow Affirmation`.
- Legacy full class-kit pass:
  - Berserker Battle Scars now roll after non-trial low-HP victories, cap at 20, raise max HP, and add bloodied weapon damage.
  - Spell Stealer/Arcane Trickster `Steal Spell` now requires `Blank Scroll`, consumes it, and creates usable stolen-spell scrolls; Class Ring trial enemies are immune.
  - Bard/Troubadour now have active `Valor`, `Shelter`, and `Renewal` songs requiring a musical instrument; Troubadour strengthens songs and awakened `Encore` adds the final weaker beat.
  - Wizard now tracks a six-school affinity hex with `Fire`/`Ice`, `Water`/`Electric`, and `Earth`/`Wind` opposites, including status text.
  - Lycan now tracks dungeon-step Moon Cycle and Frenzy Lock state with Controlled Frenzy healing support.
  - Stalwart Defender `Resolve` / `Guard Meter`, Grand Summoner future summon scaling, Soulcatcher harvest tracking, Beast Master shared recovery, and class status text are wired through existing runtime hooks.
- Paladin/Crusader:
  - Implemented permanent Paladin vow selection for Redemption, Conquest, Protection, and Retribution.
  - Added `Redeem`, `Challenge`, `Interpose`, and `Judgment Riposte`, with saved aura/mark state, deterministic counters, save/load migration, pygame/curses promotion prompts, Church legacy vow selection, and Crusader Vow Trial affirmation.
- Lancer/Dragoon:
  - Jump remains implemented.
  - Dragoon Dragon Quest is implemented through the Recover Jump Red Dragon route, Realm of Cambion terminal follow-up, Jeweler crafting, and Draconite Pendant reward.

Needs Design Decision And Playtest Follow-Up:

- Legacy class-kit balance:
  - Playtest Berserker Battle Scars gain rate, low-HP risk/reward, and late-game HP/damage scaling.
  - Playtest scroll economy for `Blank Scroll`, stolen scroll charge/value behavior, and boss spell-steal limits.
  - Playtest Bard/Troubadour song strength, Renewal sustain, and Encore usefulness.
  - Playtest Wizard affinity gain/pull rates and whether radar visualization is worth adding beyond text status.
  - Playtest Lycan Moon Cycle cadence, Frenzy Lock risk/duration, and Controlled Frenzy healing balance.
  - Playtest Stalwart Resolve gain/spend rate and how Shield Slam, Retaliate, Shield Block, and Last Stand should deepen the meter later.
- Balance follow-up:
  - Continue playtesting Paladin vow balance, Dragoon Dragon Quest reward balance, mercy victory reward expectations, encounter-rate modifiers, and mark severity.
- Narrative integration:
  - Tie second-promotion identity, Class Ring activation, and major class-kit choices back to Voluntas as expressions of chosen selfhood.
  - Avoid implementing class-progression story beats until the associated quest/spec defines trigger timing, player-facing text, save flags, and whether the beat is optional or required.
- Mage:
  - Define any remaining Demonologist corruption/bargain presentation and Shadowcaster overlap beyond the implemented contract system.
  - Define deeper Spellblade/Knight Enchanter and Summoner/Grand Summoner mechanics beyond the ring hooks.
- Pathfinder:
  - Define deeper Druid/Lycan and Ranger/Beast Master mechanics beyond the ring hooks.
  - Define Astromancer Runic Alterations drop rules, rune inventory, gear/spell modification, replacement/loss rules, UI, and save behavior.
  - Define Shaman/Soulcatcher rank-1 elemental spell unlock quests, Staff incentives, and Magic Defense/absorption Totem behavior.

Deferred:

- Do not implement major class kits until each has a one-page spec covering triggers, storage, UI, save migration, tests, and balance assumptions.
- Keep deep race-passive expansion deferred until the current always-on race identity pass has enough playtest feedback; the "7 sins / 7 virtues" ideas remain design flavor unless promoted by spec.

#### P4f - Combat Architecture And Balance

Status: `Needs Exploration`

- Use simulator-backed reports for stat-dump tradeoffs, poison/stun/crit scaling, progression outliers, and PvE tuning.
- Re-run race-baseline comparisons once class kits are stable.
- Validate enemy item usage after stealing consumables.
- Explore ability/menu improvements:
  - spell/skill ordering by mana cost;
  - Diviner/Astromancer specialty-first spell casting;
  - Wind eject effects and reward handling;
  - Absorb Essence rework;
  - mana-percentage damage abilities;
  - Prismatic Rays;
  - Throw inventory-item ability;
  - magic-stat success scaling;
  - status-gated skills;
  - out-of-combat timed buffs/debuffs;
  - Monk/Master Monk bare-handed skill support and attack bonuses.

Needs Design Decision:

- Decide whether class/race-specific level scaling belongs in P4.
- Decide whether to convert random rolls to DnD-style dice rolls.
- Decide whether charisma or another stat should affect experience.
- Decide whether Silence should affect summons.
- Decide Nightmare/flying creature land/takeoff behavior.
- Decide whether status ticks continue after enemy defeat.
- Decide ignore-vs-defense semantics and shield/reflect resolution order.
- Decide unlockable races/classes/levels and difficulty-level strategy.

Deferred:

- Defer multi-enemy combat until battle-engine targeting, encounter generation, UI layout, loot/XP allocation, AI, and balance implications are designed.
- Defer speed-based combat stacks until initiative/action-queue rules, multiple-turn caps, UI messaging, and simulator impact are designed.

### P5 - Audio Content Completion

Status: `Planned`

1. Replace remaining placeholder SFX with final assets.
2. Add final music assets for menu, town, shops, church, inn, dungeon, normal combat, boss combat, and final combat.
3. Route remaining staged assets only when the runtime hook is clear.
   - `laser_beam.wav`: needs weapon/damage event payloads that expose weapon identity before it can be routed safely.
   - bird-call asset: decide whether it should replace or supplement the current scream/howl/nightmare routing for Screech/lightning-bird content.
4. Add event-payload enrichment for future audio routing.
   - Weapon name or attack source on weapon-damage events.
   - Ability/item/source metadata where UI and audio layers need presentation-specific behavior.

### P6 - Expand Enemies, Items, and Abilities

1. Enemies
  - Giant: humanoid
  - Owlbear: monster
2. Items
  - Helm of Rostam: replaces Tarnhelm as ultimate medium helmet; Tarnhelm and Tolga "pushed down" and Visored Sallet removed from medium helmets
  - Acorn, Vine Seed, Fungus Spore, Hemlock Root: reagents for Druid/Archdruid abilities
3. Abilities
  - Skills
    - Offensive
      - Zephyrstrike: passive; gain speed on a critical attack (Ranger, Rogue)
    - Defensive
      - Retaliate: passive; chance to counter attack following a blocked attack (Sentinel)
      - Defensive Regen: passive; increase effect of Regen heal when in defensive stance (Priest)
      - Posturing: passive; increases chance to Parry when in defensive stance (Crusader)
      - Last Stand: increases defense and block amount at the expense of attack (Stalwart Defender)
    - Stealth
      - Steal As Well: passive; damaging spells have a chance to steal when hit (Spell Stealer)
      - Steal Spell: steal a random spell from the target to use against them or save for later (Spell Stealer)
      - Steal Spell 2: chance to learn spells permanently when stolen (Arcane Trickster)
      - Poison Dart: fire a poisoned dart at the enemy, dealing damage and infecting the enemy (Archdruid)
    - Enhance
      - Third Eye: passive; add intelligence into critical and dodge chance calculations (Arcane Trickster)
    - Class
      - Monkey Grip: passive; allows Berserker to equip a 2-handed weapon in the main hand at the expense of accuracy (Berserker)
      - Monkey Grip 2: passive; allows Berserker to equip a 2-handed weapon in the offhand at the expense of accuracy (Berserker)
      - Final Assault: upon lethal damage from a melee attack, retaliate against the target with a counterattack; if the target is felled, you stabilize at 1 HP (Berserker)
      - Paladin - Redemption Path
        - Implemented: `Redeem` attempts a boss-immune mercy victory using Charisma/Wisdom, enemy missing HP, and aura bonus.
        - Implemented: `Redemption Aura` lasts 3 encounters, lowers encounter rate, increases experience/gold, and improves Redeem chance.
        - Implemented: `Mark of Perdition` lasts 3 encounters, increasing encounter rate and reducing experience/gold after Redemption vow-breaking kills.
      - Paladin - Conquest Path
        - Implemented: `Challenge` marks one foe for 3 turns and grants bonus accuracy/damage against that foe.
        - Implemented: `Conquest Aura` lasts 3 encounters, stacks up to 3, and grants initiative plus weapon/magic damage.
        - Implemented: `Mark of the Craven` persists until killing a bounty target and reduces initiative plus weapon/magic damage.
      - Paladin - Protection Path
        - Implemented: `Interpose` enters a 2-turn guarded stance, improving the next weapon-hit block.
        - Implemented: `Protection Aura` lasts 2 combat turns, stacks up to 5, and improves block chance/mitigation.
        - Implemented: `Mark of Vulnerability` lasts until incapacitation ends and increases physical/melee damage taken.
      - Paladin - Retribution Path
        - Implemented: `Judgment Riposte` enters a 2-turn retaliatory stance that counters an enemy attack with weapon/Holy damage.
        - Implemented: `Retribution Aura` lasts 3 encounters, or 6 if the riposte kills, and improves dodge plus critical damage.
        - Implemented: `Mark of Mercy` persists until a weapon is equipped/picked up; Vow Affirmation lowers its lethal threshold from 10% HP to 5%.
      - Transform (1-4): change Transform abilities to add each iteration instead of overwriting the previous one (Druid/Lycan)
      - Nature Attunement follow-up abilities: the core Archdruid attunement/ring system is implemented; future Druid/Archdruid abilities can consume or reference the existing Venom, Stone, Growth, and Storm state.
  - Spells

### P7 - Additional Improvements

1. Add mouse/cursor support; make menu options clickable
2. Additional artistic renderings
   - Create additional portrait options for greater customization (i.e. different skin colors, facial features, etc.)
   - Replace certain dungeon sprite renderings: stairs up/down, secret shop
   - Companions: familiars, beasts (reuse enemy art?), summons, etc.
3. Increase the border size in the Equipment tab so the selected equipment slot stands out more
4. Change town from menu-based to dungeon-style first-person navigation

## Deferred Or Decision-Gated Items

- Remaining status-effect artwork beyond the wired combat-state/stat-effect set is deferred to a later asset pass; current fallback initials remain valid where no PNG exists.
- Broader ability visuals are deferred until a future batch is selected; candidates include Reflect/Magic reflection flashes, Stun/Prone hit accents, elemental strike overlays, and other approved combat reads.
- Jump and Charge wind-up/impact visuals are deferred until enemy sprite stance adjustments are planned.
- Warp Point artistic renderings are deferred to a later presentation/art pass.
- Ultimate helmet acquisition, durability, item identification, usable equipment/accessory actions, armor mobility penalties, equipment naming themes, and random refresher spots are deferred until design specs cover save compatibility, economy, combat, UI, and tests.
- Persistent statistics history and account-style Bestiary collection remain deferred until profile storage, migration, and privacy/scope rules are specified.
- Deep race-passive expansion is deferred until the current always-on identity pass has enough playtest feedback.
- Major class kits are deferred until each kit has a one-page spec covering triggers, storage, UI, save migration, tests, and balance assumptions.
- Multi-enemy combat and speed-based combat stacks are deferred until battle-engine, UI, encounter-generation, and balance designs are complete.
- Laser/bird staged SFX routing is deferred until event payloads or creature-specific hooks are clear enough to avoid brittle name guesses.

## Found Bugfixes

None currently listed.

## Additional UX Improvements

None currently listed.

## Resolved Archive

### Recent Improvements

- Combat HUD replaces the minimap with a class-focused panel for familiar, summon, Totem, and active class-effect state.
- Shaman/Soulcatcher Totem presentation now has stronger aspect-colored combat-focus glyph rendering.
- Active Totem now shows its combat benefits as status icons instead of `TOT`, with combat-view marker rendering removed now that Totem lives in the HUD panel.
- Status icons now use the Astral Shift, Ice Block, Mana Shield, Mirror Image, magic Reflect, Totem melee reflect, and Speed up/down PNG assets.
- Equipment previews now include resistance changes, color-code stat deltas, and equipment slots surface resistance/immunity bonuses.
- Bestiary detail reveal is recorded during combat when enemy details are visible; current Vision no longer retroactively unlocks old kills, random enemy combat stats are hidden, and entries show stable level/type/defeat count/resistance/ability/feature details.
- Bestiary now records seen enemies at battle start, summarizes Seen/Defeated/Detailed progress, and shows defeated-gated coarse locations plus broad possible-drop labels without adding account history or exact odds.
- Status icons now use the Blind Rage, Burn, Regen, and Maelstrom Weapon PNG assets; counted labels such as `MW5` render stack-count badges over the base artwork.
- Visible charge telegraphs now use a compact "is charging" combat-log/banner indicator while detailed telegraph text remains available to the combat engine/logger.
- Bestiary entries are alphabetized by monster name, render resistances one per row under a `Resistances` header, and list immunities separately from features.
- Added a pulsing radial danger vignette for low-health pygame combat.
- Moved the dungeon minimap lower in the HUD, enlarged it, and anchored it so combat status effects do not shift the map.
- Wired PNG status artwork for Doom, Disarm, and Attack/Defense/Magic/Magic Defense up/down effects.
- Alchemist and Jeweler Buy flows now open tabbed item browsers.
- Combat startup warms enemy combat sprites before the first combat frame.
- Increased Old Key quest rewards for early/main quest turn-ins.
- Added staged SFX routing for ice/frost, scream/howl/nightmare, Mortal Strike, shield block, underground spring, and door-open interactions.
- Added dungeon music aliasing and location/context music routing.
- Improved long shop list paging and selection visibility.

### Recent Bug Fixes

- Gameplay dungeon rendering now enables the deterministic torch/sconce wall overlays so sconces can appear on eligible wall tiles again.
- Equipment resistance previews compare against pre-existing effective resistance values, preserve non-zero current resistance context while stats stay delta-only, and Character screen weakness/resistance groups include equipped resistance items.
- Magic Pendant now reports its `Magic Dodge` buff in character buff summaries.
- Bestiary entries load enemy details lazily so the Character Menu opens faster, and Mimic resolves to its combat artwork/details.
- Mirror Image duplicate handling now keeps remaining images interceptable after one vanishes, including multi-hit spells, and stale zero-duration duplicate state no longer renders visual copies.
- Mana Shield no longer absorbs negative damage or activates against nonpositive mana, and Amber Jester skips Mana Shield below 20% mana.
- Slot Machine card-hand outcome logging no longer repeats the outcome label around the card list.
- Verified Dispel removes Regen through the shared full-dispel effect.
- Combat post-turn log messages flush to the visible combat log before turn swaps or end-of-combat flow.
- Combat log wrapping is cached between message changes so long battles do not spend more time rewrapping old log history every frame.
- Decorative floor props, including BonePileTile, stay grounded when viewed through side openings instead of projecting onto the wall plane.
- Blinded and silence Hex log messages use damage/debuff coloring instead of player-blue coloring.
- Combat action menus refresh immediately after silence expires on the player's pre-turn tick.
- Already-started charged skills, including Jump, resolve their forced follow-up even if silence lands during the charge.
- Regular Health Potions no longer exceed their advertised combat heal tier through high luck modifiers.
- Crimson Jester Dispel targets positive `Character.stat_effects`, Amber Jester Mana Shield is treated as a skill, and barracks milestone storage rewards deposit without storage-key crashes.
- The Jester post-fight event waits until the battle victory and loot popups have run.
- Slot Machine DOT now applies tick damage metadata and appears in status icons.
- Generic DOT status effects appear in the pygame HUD/status icon row.
- Lick no longer selects Hangover as a random status.
- Town-return loading clears stale dungeon background providers to avoid a dungeon-view blink before the town menu.
- Dungeon music no longer keeps playing when exiting the dungeon or returning to the main menu.
- Combat and menu input guards pump pygame events before reading physical key state, so the first fresh combat action key after turn start is accepted once no key is held.
- Jump clears forced-action state after landing.
- Active Jump resolves before Berserk can force a basic attack, preserving `Unstoppable` Jump behavior.
- Duration-1 stun/sleep/incapacitation consumes the current combat turn before expiring.
- Character-screen submenu popups use stale-input/key-release guards.
- Jump no longer cancels when stun lands during charge if the skill has `Unstoppable`.
- Side-corridor outer wall doors keep door textures instead of collapsing into plain wall art.
- Shields unequip correctly when equipping two-handed weapons through pygame equipment and core equip paths.
- Combat turn indicator stays hidden until initiative is known.
- Side-view chest sprites render upright and stay behind blocking corners in the covered side-view case.
- Charge/telegraph messages wrap in both main combat and dungeon-combat overlay logs.
- Combat enemy sprites fall back from legacy `.txt` picture values to enemy-name PNG assets using cwd-independent paths.
- Pygame Character Menu Attack and Defense now match core equipment/combat modifier paths.
- Zero-value Enfeeble/stat-effect changes no longer report as positive status changes.

### Watch Items

- Keep an eye on enemies with explicit `.png` form swaps so palette/form changes continue to invalidate the correct cached sprite.
- Keep checking guarded input after unusual transitions, especially paths that clear events before entering a selection loop.

## Working Principles

1. Fix before expanding. Resolve regressions and inconsistent behavior before adding more systems on top.
2. Keep UI thin. Game logic belongs in `src/core/`; UI layers should present, not own mechanics.
3. Prefer data-driven content. New abilities and content rules should go through the YAML/effect pipeline where practical.
4. Test what changes. Renderer, combat, quest, save, and input changes should have direct focused coverage.
5. Keep this roadmap current. Completed work should be summarized or archived, not left in the active backlog.
