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
- Shop item lists support long-list paging, Home/End navigation, preserved-scroll clamping, item ranges, weapon efficiency display, stat-themed names, and elemental metadata display.
- Pygame Character Menu now reports weapon-adjusted Attack and armor-adjusted Defense through the same core modifier paths used by combat/equipment previews.

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

Status: `Active`

These should be handled before larger feature work because they directly affect confidence in moment-to-moment play.

1. Verify and close the reported first-key-blocking issue after turn starts.
   - Confirm whether any combat or menu input guard still blocks the first fresh key press.
   - Add a regression test around the affected input loop once reproduced.
2. Re-run focused playtest checks for recently fixed areas.
   - Main-menu/dungeon music transitions.
   - Character Menu Attack and Defense stat display.
   - Enfeeble zero-value reporting.
   - Half Giant Warrior early-game balance.
   - Old Key locked-door prompt behavior.
3. Keep the roadmap and playtest checklist aligned after each implementation pass.
   - Move resolved bug lines into the resolved archive instead of leaving them as active bugs.
   - Keep checklist items for newly wired SFX and music transitions.

### P1 - Pygame UX Polish

Status: `Active`

1. Decide the character menu direction.
   - Option A: focused cleanup of existing panels and equipment comparisons.
   - Option B: full redesign of character/inventory/equipment presentation.
   - The next pass should choose one path instead of leaving this as an open-ended item.
2. Decide whether shop tabs should replace the current shop mode-selection flow.
   - The current shop flow has improved paging and comparison support, but true tabs remain unimplemented.
3. Continue popup/background consistency work only where playtesting shows visible issues.
   - Most stale-input and background-provider paths are now guarded.
   - Remaining work should be bug-driven rather than broad speculative rewrites.
4. Revisit combat visual polish.
   - Current status/telegraph readability is strong enough for baseline play.
   - Lightweight hit/spell effects or particles are still planned, but should be added only where they improve clarity.

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
2. Racial passive follow-up.
   - Decide whether the original "7 sins / 7 virtues" ideas should become deeper passives or remain design flavor.
   - Avoid weakening the already-implemented always-on race identity pass.
3. Gameplay statistics expansion.
   - Decide whether persistent history, run summaries, or account-style stats are worth adding beyond the current grouped run popup.
4. Equipment and progression expansion.
   - Most originally listed item-system improvements are now done.
   - Future equipment work should focus on clearly scoped new mechanics, class kits, or content rewards.
5. Deeper balance tuning.
   - Revisit stat-dump tradeoffs.
   - Re-run race-baseline comparisons once class kits are stable.
   - Revisit progression scaling outliers.
   - Use simulator-backed reports for PvE tuning.

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

## Deferred Or Decision-Gated Items

- Full character menu redesign is decision-gated behind whether focused cleanup is sufficient.
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
- Keep checking first-key behavior after guarded input transitions, especially combat-turn and menu-entry paths.

## Working Principles

1. Fix before expanding. Resolve regressions and inconsistent behavior before adding more systems on top.
2. Keep UI thin. Game logic belongs in `src/core/`; UI layers should present, not own mechanics.
3. Prefer data-driven content. New abilities and content rules should go through the YAML/effect pipeline where practical.
4. Test what changes. Renderer, combat, quest, save, and input changes should have direct focused coverage.
5. Keep this roadmap current. Completed work should be summarized or archived, not left in the active backlog.
