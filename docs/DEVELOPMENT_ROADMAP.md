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
- Shop item lists support long-list paging, Home/End navigation, preserved-scroll clamping, item ranges, stat-themed names, and elemental metadata display.
- Pygame Character Menu now reports weapon-adjusted Attack and armor-adjusted Defense through the same core modifier paths used by combat/equipment previews.
- The modern Pygame Character Menu is the default town and dungeon character menu. It includes tabbed character/equipment views, race/sex portraits, grouped weaknesses/resistances, a paper-doll equipment layout with Helmet support, dual-wield attack display, item artwork, in-slot equipment details/buffs, and styled inventory equip-failure notices.
- Helmet equipment is now implemented across core equipment, save/load compatibility, curses and pygame shops, inventory/equipment popups, icon/artwork fallback, and Defense/resistance/invisibility modifiers. The current catalog includes Cloth, Light, Medium, and Heavy helmet progressions plus restricted and special-effect helmets.
- The medium ultimate armor reward is now Klivanion; its retaliation effect, shop flows, item maps, and tests use the renamed item and effect text.
- Character creation uses a visual naming screen with portrait preview plus selected sex, race, and class details.
- Selected-item contexts now use the large item artwork atlas in inventory, equipment, shop, loot/reward, and modern Character Menu equipment views.

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

Next active priority: `P1 - Pygame UX Polish`.

### P1 - Pygame UX Polish

Status: `Active`

1. Complete modern Character Menu acceptance and iteration.
   - Status: `Done` for the current UX pass.
   - Implemented: sex-first character creation, race/sex portrait assets, base portrait atlas loading with individual PNG fallback support, reusable portrait composition/caching for future overlays, native-ratio portrait frame sizing, generic Character/Equipment tabs, wider 60/40 Character and Combat Stats panels, wider right-column level-progress bar using current-level XP progress, dual-wield main/offhand Attack display, larger right-aligned Name/Race/Class/Level text, Core Attributes positioned below the experience bar, larger character/combat/resistance text, right-aligned core/combat values, static side-by-side weaknesses/resistances block for all 10 resistance keys, panel dividers, spread-out paper-doll Equipment tab with an active Helmet equipment slot, larger equipment blocks with optional icon boxes and right-aligned subtype/base weapon/armor/block/weight/resistance details, in-slot equipment-buff reporting, popup quick-scroll and wrapped item descriptions, and town/dungeon opt-in routing.
   - Portrait implementation note: runtime prefers `base_portrait_atlas.png`/`.json`; the loader supports both the current `assets/portraits/` drop location and the suggested future `assets/portraits/base/` plus `fallback_individuals/` layout.
   - Item artwork implementation note: selected-item views use large archetype artwork from `assets/item_renders/`; dense rows and compact slot summaries still use the small icon system.
2. Replace current shop mode-selection flow with shop tabs.
   - Status: `Done`.
   - Type selection remains in place for shop categories, while item sub-types are now browsed with tabs in the buy list.
   - Implemented for town shops and secret-shop grouped categories, with left/right tab navigation and filtered empty tabs.
3. Revisit combat visual polish.
   - Current status/telegraph readability is strong enough for baseline play.
   - Lightweight hit/spell effects or particles are still planned, but should be added only where they improve clarity.
   - Current "Choose Action" menu can overflow if more than 6 options are available.
   - Combat view UI is fairly rudimentary, could use an update to match game aesthetics.
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
6. Update dungeon renderings to match new aesthetic.
   - Generate new floor, ceiling, and wall tiles
7. Expand realistic item artworks to include images for all items.
   - build on renderings in `src/ui_pygame/assets/item_renders/item_render_atlas.png` to produce images for each item
   - either create independent images or create atlases for each item type or sub-type

### P2 - Renderer And Exploration Presentation

Status: `Active`

1. Continue renderer smoke-test work around structural-depth and side-corridor behavior.
   - Preserve center-wall stopping behavior.
   - Preserve valid depth-2/depth-3 side floor, ceiling, wall, and door routing.
2. Continue door and side-opening presentation validation.
   - Keep hidden/detected/open Ore Vault behavior stable.
   - Preserve single-side-door visibility unless playtesting says it is confusing.
3. Finish special-tile placement polish for future floor-bound props.
   - Existing defeated-boss, spring, chest, door, and side-special coverage is useful; extend it only for concrete new props or regressions.
4. Keep asset fallback diagnostics visible during renderer changes.
   - Use existing grouped fallback and panel-slot diagnostics before adding new debug helpers.

### P3 - Core Refactoring And Test Confidence

Status: `Planned`

1. Continue effects-system integration beyond the migration.
   - Replace older inline combat logic in legacy ability code with composable effects where practical.
   - Keep output formats consistent between legacy and YAML abilities.
2. Expand high-value automated coverage.
   - Ability effects across the full ability set.
   - Status-effect interaction scenarios.
   - Enemy AI behavior where tactical choices are meaningful.
   - Quest completion/reward flows.
   - Save/load round trips only when new persistence risks appear.
3. Continue targeted type hints and docstrings.
   - Highest-value modules: `abilities.py`, `items.py`, `enemies.py`, and follow-up `character.py` cleanup.
   - Keep type-hint work scoped to clear behavior boundaries rather than broad rewrites.
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
