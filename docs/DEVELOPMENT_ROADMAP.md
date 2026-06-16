# Dungeon Crawl Development Roadmap

*Updated: June 2026*

This roadmap tracks the remaining work for Dungeon Crawl after the recent stabilization and coverage passes. Completed work is summarized briefly so the active backlog stays readable.

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
- Data-driven ability migration is substantially complete with `179` YAML ability definitions.
- Pygame dungeon, town, combat, popup, and menu flows are functional, with remaining polish work concentrated in UX consistency and visual presentation.
- Visual character creation now includes the selected portrait and sex/race/class identity on the naming screen.
- Large item-render artwork is integrated for selected-item presentation contexts while compact lists continue to use small icons.
- Large item artwork now uses approved transparent individual PNGs organized under `src/ui_pygame/assets/item_art/` for regular, key, and special inventory selected-item views.
- Combat simulator, battle logger, save diagnostics, renderer diagnostics, audio diagnostics, and gameplay-stat summaries are implemented.
- Sound/music runtime integration is active, but final content assets are still incomplete.

### Verified Repo Metrics

- Test files under `tests/`: `81`
- YAML ability definitions under `src/core/data/abilities/`: `179`
- Event types in `EventType`: `38`
- Latest full-suite result recorded in prior roadmap notes: `1398` passing tests with `81%` total coverage across `src/`

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
- The P2 renderer/exploration presentation pass added Rotator, active FunhouseTeleporter, and visited-only FakeWall/Fake Path floor-bound presentation, smoothed the pygame load progress popup, and expanded structural-depth side-opening smoke coverage.
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

Next active priority: `P3 - Core Refactoring And Test Confidence`.

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
   - Added visited-only FakeWall/Fake Path presentation so revealed fake paths get a subtle floor marker while hidden fake walls remain visually indistinguishable from ordinary walls.
4. Keep asset fallback diagnostics visible during renderer changes.
   - Use existing grouped fallback and panel-slot diagnostics before adding new debug helpers.
5. Gameplay element refinement.
   - The load bar when loading a game is jumpy instead of a smooth progression.
   - Smoothed the pygame load progress popup with time-based 60 FPS interpolation while preserving the existing load-game flow and debug/test compatibility.

### P3 - Core Refactoring And Test Confidence

Status: `Active`

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
   - 2026-06-16: Removed the stale `random_enemy()` debug override that forced all random encounters to the
     `Test` enemy after catalog selection.
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
     - 2026-06-16: Re-enabled real random enemy catalog selection and validated catalog edge coverage.
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
   - 2026-06-16: Added typed signatures to `DataDrivenHealSpell` cast, hybrid heal, HoT, and out-of-combat
     heal helpers after consolidating instant-heal behavior.
   - 2026-06-16: Added typed signatures to data-driven support/status spell `cast()` methods and pinned
     Cleanse's default-target presentation.
   - 2026-06-16: Added typed signatures to data-driven weapon/custom spell constructors and `cast()` methods
     after the shield-helper cleanup, keeping Smite and Turn Undead wrapper contracts explicit.
   - 2026-06-16: Extended typed signatures across the remaining data-driven charging, magic-missile, Jump,
     and movement wrapper entry points.
4. Remove easy skips or placeholder tests where missing functionality is now small enough to implement.

### P4 - Content And Systems Expansion

Status: `Planned`

1. Quest and realm expansion.
   - Finish or expand Playhouse/Jester content.
   - Add the class-specific Class Ring questline if still desired.
   - Add post-fight NPC dialogue changes.
   - Expand Realm of Cambion follow-up content.
   - Add missing special tiles such as Portal, Rotator, Teleporter, and Fake Path where still needed.
   - Implement concept of Psychopomp, a creature or spirit that escorts the newly deceased to the afterlife and often resembles self
      - if player dies outside of starter area, instead of being resurrected in town, require passage of trial to return
      - possibly defeat scaled-up version of self; difficulty based on where character dies
   - Greater immersive gameplay details
      - Scientist(s) manning the Warp Point
      - Artistic renderings for NPCs
         - Sergeant in Barracks
         - Patrons in Inn
         - Shop purveyors
         - Guards at Old Warehouse
         - Priest at Church
         - Little boy lost in dungeon (Bring Him Home quest)
2. Racial passive follow-up.
   - Decide whether the original "7 sins / 7 virtues" ideas should become deeper passives or remain design flavor.
   - Avoid weakening the already-implemented always-on race identity pass.
3. Gameplay statistics expansion.
   - Decide whether persistent history, run summaries, or account-style stats are worth adding beyond the current grouped run popup.
4. Equipment and progression expansion.
   - Helmet slot support and the initial Cloth/Light/Medium/Heavy helmet catalog are now done.
      - Add quest/process for obtaining ultimate helmets.
   - Most originally listed item-system improvements are now done.
   - Future equipment work should focus on clearly scoped new mechanics, class kits, or content rewards.
   - Equipment durability; continuing to use a broken item without fixing can make it shatter, losing it forever.
   - Add way to inspect currently equipped items.
   - Equipment details when equipping should include whether the weapon is a one-handed or two-handed weapon.
5. Deeper balance tuning.
   - Revisit stat-dump tradeoffs.
   - Re-run race-baseline comparisons once class kits are stable.
   - Revisit progression scaling outliers.
   - Use simulator-backed reports for PvE tuning.
6. Item improvement and expansion.
   - Item identification tied to intelligence; low intelligence characters will find more unidentified items, requiring either a scroll or shop to identify.
   - Item usage for buffs or special attacks; using it too much can cause it to break/shatter.
7. Bestiary implementation.
   - Allow the player to view information about previously defeated enemies.
   - Use enemy artwork with details gleaned from combat encounters; higher perception characters (including when wearing Pendant of Vision) will uncover more information.
   - Add achievements and/or rewards for completion.
8. Combat Improvements
   - Add multi-enemy combat support; may require rebalancing
   - Create combat stack based on speed; greater speed diff can result in multiple turns in a row
   - Combat logging improvements
      - Add logging for item special effects (e.g. when an attack disarms an enemy)
      - Change the player log color to match the icon colors (player blue, enemy red)
   - Add visual representation of abilities
      - Mana Shield creates a blue force field glow around the user
      - Mirror Image duplicates the user
      - Smoke Screen should obscure the user and then have them disappear while it fades
9. Unique class mechanics
   - Warrior
      - Weapon Master/Grandmaster of Arms/Berserker
         - Implement second promotion class Grandmaster of Arms
         - Weapon Master/Grandmaster of Arms: Weapon Discipline
            - gain proficiency with a weapon type as it's used
            - each weapon type levels from 0-100 and has 10 levels
            - experience is gained by attacking; critical hits double experience
            - can no longer be leveled once promoted to Berserker; player must either max out weapon of choice or select Grandmaster of Arms promotion
         - Grandmaster of Arms: Weapon Specialty
            - weapon types that gain max level now trigger certain abilities/buffs
               - Fist: Hundred Hand Slap -
               - Dagger:
               - Sword:
               - Club:
               - Longsword:
               - Battle Axe:
               - Hammer:
         - Berserker: Battle Scars
            - surviving combat with less than 10% health gives chance of permanent scar
            - scars provide permanent stat bonuses (e.g. +1 to stat, +5 health or mana, +1% crit chance, +1% life steal, etc.)
      - Paladin/Crusader
         - Oathbringer: choose an path to follow
            - Redemption: the path of the pacifist
               - gain Redeem ability; success affected by charisma and inversely related to enemy HP percentage (bosses are immune and won't trigger Mark of Perdition)
               - successful redeem trigger Redemption aura
                  - lowers encounter rate but increases experience and gold and chance to redeem enemies
                  - persists until an enemy is killed instead of Redeem
               - killing a non-boss enemy has a chance to trigger Mark of Perdition based on charisma (lower charisma = higher chance)
                  - increases encounter rate and lowers experience and gold
                  - persists until next successful Redeem
            - Conquest: the path of the warmonger
               - killing enemies that you currently have a bounty on triggers Conquest aura
                  - increases initiative and offensive combat stats (attack, crit, hit)
                  - lasts 5 minutes and stacks up to 3 times
               - running away from any enemy drops Conquest aura and triggers Mark of the Craven
                  - decreases initiative and offensive combat stats (attack, crit, hit)
                  - persists until killing a bounty target
            - Retribution: the path of the punitive
               - successful counterattacks (Parry) trigger Retribution aura
                  - increases dodge chance and critical damage
                  - lasts 5 minutes (killing blow doubles duration)
               - unequipping, breaking, or being disarmed triggers Mark of Mercy
                  - if HP drops below 10%, enemy can mercy-kill player
                  - persists until weapon is equipped or picked up
            - Protection: the path of the defender
               - blocking an attack can trigger Protection aura
                  - increases block amount and regens health every turn active
                  - lasts 2 turns but can stack up to 5 times, resetting the duration each time
               - if a shield is not equipped (unequipped or broken), player will be affected by Mark of Vulnerability
                  - increases melee damage taken and lowers healing from any source
                  - persists until a shield is equipped
      - Lancer/Dragoon
         - Jump: `implemented`
         - Dragoon: Dragon Quest - following the defeat of the Red Dragon, the Dragoon can embark on a
            quest to collect the 
      - Sentinel/Stalwart Defender
         - Sentinel: Resolve - taking damage generates resolve that fills up a gauge
            - the percentage of resolve affects certain abilities, culminating in an ultimate ability
               - Shield Slam: increases damage dealt by the percentage filled
               - Retaliate: blocked attacks have chance equal to the percentage filled to retaliate
               - Shield Block: successful blocks trigger a concussive shock from the shield, stunning the attacker
               - Last Stand: lowers the attack penalty by the percentage filled
	- Mage
      - Sorcerer/Wizard
         - Elemental Affinity Wheel - casting spells of a particular element increases affinity with that element but at the detriment of the inverse element (fire/ice, electric/water, earth/wind)
            - once affinity reaches a certain level, unlocks 2nd level spell of that element
            - for level 3 spells, must be Wizard class with even higher affinity; if affinity level reached before becoming Wizard, spell will be learned on promotion
            - represented visually with a hex radar chart
            - affinity grows/shrinks based on intelligence level
               - 15 intel is baseline; equal gain and loss
               - every point above or below changes the affinity gained/lost by 5%
      - Warlock/Shadowcaster
      - Spellblade/Knight Enchanter
      - Summoner/Grand Summoner
	- Footpad
      - Thief/Rogue
      - Inquisitor/Seeker
      - Assassin/Ninja
      - Spell Stealer/Arcane Trickster
	- Healer
      - Cleric/Templar
      - Priest/Archbishop
      - Monk/Master Monk
         - Sound Body and Mind - Arms, legs, head, body
      - Bard/Troubadour
	- Pathfinder
      - Druid/Lycan
      - Diviner/Astromancer
         - Geomancer has been renamed to Astromancer in runtime class, item, race, ability, and test references.
            - change TetraDisaster to GrandDesign
         - Astromancer: Runic Alterations - defeating enemies with elemental spells gives chance to drop runes
            - runes match the spell used when gained
            - combine rune(s) and gear to increase power
               - modifying weapons add elemental damage and/or attack stats
               - modifying armor/helmets adds elemental resistance and/or defensive stats
               - modifying accessories adds buffs and/or spell damage/defense
               - modifying spells increases damage and/or hit chance and/or crit chance
            - runes can be replaced but they are lost
      - Shaman/Soulcatcher
      - Ranger/Beast Master

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

### P6 - Removal of UI Curses Game Edition

Status: `Planned`

1. Remove parallel `curses` UI implementation of the Dungeon Crawl game
2. Confirm all dependencies and plugin code is removed.

## Deferred Or Decision-Gated Items

- Shop tab UX is decision-gated behind whether the current shop mode flow remains too slow after paging/navigation improvements.
- Spell/hit particle effects are deferred until the team chooses where animation adds clarity instead of visual noise.
- Persistent statistics history is deferred until current-run stats feel insufficient in play.
- Deep race-passive expansion is deferred until the current always-on identity pass has enough playtest feedback.
- Laser/bird staged SFX routing is deferred until event payloads or creature-specific hooks are clear enough to avoid brittle name guesses.

## Found Bugfixes

- Log messages are still not being fully flushed to the logger before proceeding to the next turn or end of combat.
- DOT status from Slot Machine does not apply a debuff to the statuses.
- Lick should not be able to apply Hangover status.

## Resolved Archive

### Recent Improvements

- Increased Old Key quest rewards for early/main quest turn-ins.
- Added staged SFX routing for ice/frost, scream/howl/nightmare, Mortal Strike, shield block, underground spring, and door-open interactions.
- Added dungeon music aliasing and location/context music routing.
- Improved long shop list paging and selection visibility.

### Recent Bug Fixes

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
