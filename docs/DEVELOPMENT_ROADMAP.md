# Dungeon Crawl — Development Roadmap

*Updated: May 2026*

This roadmap is organized by implementation status instead of historical planning order. It is intended to answer three questions quickly:

1. What is already complete?
2. What is partially complete or still actively needed?
3. What is deferred until later phases?

### Status Legend

- `Confirmed`: Repo inspection clearly supports that the item is implemented and active
- `Partial`: Significant implementation exists, but the item is incomplete, uneven, or still needs follow-up work
- `Planned`: Still primarily future work, deferred work, or work not yet clearly implemented
- `Active`: Immediate execution work currently in progress or intended as the next stabilization pass

---

## Snapshot

### Completed Foundations

- Core project architecture is reorganized into `src/core/`, `src/ui_curses/`, and `src/ui_pygame/`
- EventBus infrastructure is in place
- Core battle logic has been extracted into a shared engine
- Combat simulator and balance tooling are functional
- Large portions of the abilities system have been migrated to YAML / data-driven definitions
- Pygame dungeon/town/combat flows are functional, though still incomplete in polish
- Pygame combat status icons and telegraph UI are implemented in a baseline form
- Sound and music systems are implemented at the engine/integration level, but content assets are still incomplete

### Active Gaps

- Pygame UI polish and consistency
- Remaining effects-system integration across older hand-written ability logic
- Broader automated test coverage
- Further post-migration balance tuning
- Content systems such as quest expansion, item expansion, racial-passive follow-up, and sound/music content

### Verified Repo Metrics

- Test files under `tests/` (all buckets): `81`
- YAML ability definitions under `src/core/data/abilities/`: `179`
- Event types in `EventType`: `38`

---

## Completed

### 1. Critical Combat Bug Fixes

Status: `Confirmed`

These roadmap items are considered complete:

- Charge stun logic fix
- Arcane Blast mana guard
- Mana Shield method mismatch cleanup

### 2. Core Battle Engine Extraction

Status: `Confirmed`

This roadmap item is considered complete.

Completed outcomes:

- Shared battle logic extracted into `src/core/battle_engine.py`
- UI battle layers are thinner than before
- Combat mechanics are no longer primarily duplicated between curses and pygame

Clarification:

- This is materially complete, but not absolute. The UI layers still contain orchestration and presentation-specific combat flow, so “zero combat logic in UI layers” should not be treated as fully achieved.

### 3. Ability Output Standardization

Status: `Confirmed`

This roadmap item is considered complete.

Completed outcomes:

- Ability execution is aligned around structured combat-result style outputs
- The combat engine and simulator can operate on more consistent ability results

### 4. YAML / Data-Driven Ability Migration

Status: `Partial`

This roadmap area is substantially complete for the batches listed in the original roadmap.

Completed migration batches:

- Batch 1: Simple offensive spells
- Batch 2: Healing and buff/debuff spells
- Batch 3: Complex offensive / multi-hit / conditional abilities
- Batch 4: Weapon+status skills and StatusSkill extensions
- Batch 5: High-damage weapon skills, Doom, Tunnel/Surface
- Batch 6: Death spells, composite debuffs, stat-reduction
- Batch 7: Power-up, chain, drain, and toggle abilities
- Batch 8: Enemy skills, Hex, Vulcanize, Smite family, Turn Undead
- Batch 9: Equipment skills, enemy skills, Gold Toss, Dim Mak
- Batch 10: Maelstrom, Disintegrate, Inspect, Purity Body, Resurrection, Resist All

Completed supporting work:

- New effect types added to support migrated abilities
- Expanded data-driven base types
- Save-system and serialization fixes related to migrated abilities

Clarification:

- Repo inspection strongly supports the migration claims, but this section should still be treated as “substantially complete” rather than “finished forever.” Some legacy hand-written ability logic still exists outside the data-driven path.
- The current repo contains `179` YAML ability definition files, which strongly supports the “substantially complete” label.

### 5. Status Effect Improvements

Status: `Confirmed`

This roadmap item is considered complete for the originally scoped work.

Completed outcomes:

- Status interactions improved
- More status-aware combat behavior implemented
- Better support for multi-turn and immunity-related combat logic

### 6. Enemy AI Improvements

Status: `Confirmed`

The originally listed roadmap items in this category are complete.

Completed outcomes:

- Status-aware enemy ability selection
- Funhouse `Copycat` enemy that mirrors a subset of player abilities
- Charging telegraph support
- Cambion acolyte support behavior for the Devil encounter

Note:

- YAML `telegraph_message` is currently the canonical telegraph source
- `Enemy.action_stack["telegraph"]` and `Enemy.action_stack["delay"]` remain future-integration hooks rather than fully consumed scheduling inputs
- Enemy priority selection now records the chosen `action_stack` entry as metadata, so delay and telegraph hooks can be inspected by UI/tooling before deeper scheduler integration.

### 7. Initial Balance / Tuning Pass

Status: `Partial`

This roadmap area has meaningful completed work, but is not fully “finished.”

Completed initial-pass items:

- Clannfear buff
- Laser2 nerf / redesign away from excessive permanent stat loss
- Weapon crit rebalance
- Disarm updated to affect total weapon output
- Mimic scaling adjustments
- Half Giant early-game tuning now preserves strength/constitution identity while sharpening agility, magic-defense, and resistance drawbacks.

Completed tooling items:

- Deterministic simulator seeding
- Better generated test-player baselines
- Promotion-tier level-cap correctness
- Support for promoted-class progression modeling

Clarification:

- The initial balance pass is confirmed, but deeper numerical tuning is still deferred until class kits are fully complete.

### 8. Race Identity Pass

Status: `Confirmed`

This roadmap item is marked as done in the original plan.

Completed outcomes:

- Simple, always-on race identity traits were defined and implemented as an initial pass
- The work is intended to preserve race strengths/weaknesses instead of flattening race identity

### 9. Type Hinting and Early Quality Work

Status: `Partial`

Partially completed from the original roadmap’s earlier phases:

- Type-hint cleanup has begun
- `character.py` and `combat_result.py` were explicitly called out as completed in the earlier execution phases
- `CombatResult` now uses a more precise typed effects mapping and snapshots mutable payloads when converted to dictionaries
- Combat basics coverage was expanded enough to mark earlier stabilization phases complete

Clarification:

- This area is not broadly complete. Large legacy modules still need further type-hinting and cleanup.

### 10. Combat Simulator / Analytics

Status: `Confirmed`

This roadmap item is functionally complete enough to support balancing work.

Completed outcomes:

- BattleEngine-backed combat simulator is functional
- Usable for regression checks and balance comparisons
- Supports the balance workflow described in the roadmap
- Balance reports can now export structured JSON payloads and files for debug/tooling workflows
- Balance reports can now export compact summary payloads for lightweight dashboards without raw per-battle results

Metric note:

- Older roadmap wording that described analytics as a “stub” is no longer accurate.

---

## In Progress Or Remaining

### 1. Effects System Integration Beyond Migration

Status: `Partial`

While the YAML migration batches listed above are complete, this area is not fully done.

Remaining work:

- Continue replacing older inline combat logic in legacy ability code with composable effects
- Reduce remaining hand-written special-case logic where practical
- Keep output formats and effect composition consistent across old and new abilities

### 2. Pygame UI Completion

Status: `Partial`

This is still an active focus area.

### Combat UI Polish

Status: `Partial`

Remaining work:

- Continue polishing status effect icon presentation beyond the completed overflow handling
- Add spell effect animations / particle systems
- Continue telegraph presentation polish beyond the completed combat-log highlight treatment and new banner strip

Verification note:

- Repo inspection confirms that baseline status icons, telegraph UI, and a dedicated turn-indicator banner exist in pygame combat.
- Combat status icons now cap visible rows and collapse excess effects into a `+N` marker.
- Combat status icons now sort urgent negative effects ahead of positive buffs before overflow compaction, so control/status hazards stay visible when many effects are active.
- Urgent negative combat status icons now use a stronger alert color after prioritization, improving readability when many effects are active.
- Combat status icon labels now trim to fit inside their compact pills instead of spilling over when future labels run long.
- Combat and combat-mode dungeon HUD status icons now share the same priority, overflow, and color helper logic to avoid future presentation drift.
- Main combat status icons now include the Maelstrom Weapon stack marker already shown in the dungeon combat HUD, keeping stacked passive state visible across combat presentations.
- Repeated same-label combat status icons now collapse into counted pills such as `ATK2` / `PSN2`, reducing crowding before overflow compaction.
- Dense dungeon-combat HUD status rows now have regression coverage proving urgent counted effects stay visible ahead of overflow.
- Dungeon-combat HUD status pills are now slightly wider so counted labels such as `STN2` remain readable before overflow compaction.
- Charging / telegraph-style combat log lines now render with a warning color in both combat overlay modes.
- Charging / telegraph-style combat log lines now wrap against the narrower dungeon-combat overlay pane as well as the main combat pane.
- Telegraph messages now also surface in a dedicated warning banner, and the turn indicator now uses fixed player/enemy turn labels for cleaner readability.
- Telegraph banners now keep the full latest unwrapped telegraph message for truncation instead of depending on combat-log wrap fragments.
- Telegraph banners now clear when later non-telegraph combat messages arrive, avoiding stale charge warnings after the charged action resolves.
- Combat selection overlays now fit long item, spell, skill, and Totem labels by rendered pixel width instead of raw character count, preserving readable compact menus.
- Combat turn-indicator subtitles now trim long player/enemy names to the banner width so unusual names do not spill into neighboring UI.
- Blind Rage now has a distinct urgent `BRG` status icon label in both main combat and dungeon-combat HUD status rows.
- Zero-value stat debuffs are now suppressed at effect/reporting time, and stale zero-value stat effects no longer render as green combat status icons.

### Dungeon Rendering / Presentation Polish

Status: `Partial`

Remaining work:

- Continue any remaining presentation cleanup if later playtesting shows it is still needed

Verification note:

- Current active stabilization work is concentrated in `src/ui_pygame/gui/dungeon/renderer.py` and `tests/test_dungeon_renderer_smoke.py`.
- Defeated boss rooms now render a replacement burial-site style visual.
- Minimap door and chest icons now distinguish open and closed state.
- Side-door smoke coverage now preserves the intentional rule that a single side door can remain visible behind a depth-1 center wall while the opposite side special still renders.
- The dungeon viewport now gets a soft edge vignette so the rendered scene feels less abruptly cut off.
- The viewport edge treatment now uses layered bands and a subtle separator so the dungeon frame reads more cleanly against the HUD.
- Side floor sprites now advance to the visible next-zone depth when the corridor extends forward, and floor-sprite clip regions expand accordingly.
- Depth-2 side floor-special geometry now has regression coverage to keep left/right props in the outer lanes as they advance to depth-3 placement.
- Side-view chest sprites now render upright instead of being perspective-skewed like floor decals.
- Left-side side-corridor floor-special routing now has outer depth-3 floor regression coverage to match the existing right-side checks.
- Combat-mode dungeon HUD status icons now share the priority/overflow behavior used by the main combat view.
- Outer side-corridor door regression coverage now checks left-side open and closed doors as well as the existing right-side cases.
- Detected but closed Ore Vault doors now render as closed door wall planes while still leaving undetected Ore Vault doors visually hidden as normal walls.
- Side-opening Ore Vault door rendering now has matching detected/hidden regression coverage, preserving hidden-wall presentation until the door is revealed.
- Open Ore Vault doors now have renderer coverage that preserves their current open-passage presentation.
- Left-side outer corridor floor, ceiling, and wall slot IDs now have parity regression coverage alongside the existing right-side checks.
- Left depth-3 outer side-corridor wall continuation now has smoke coverage so deeper side-wall routing stays stable.
- Depth-3 outer side-corridor floor and ceiling slot IDs now have left/right regression coverage, keeping deeper corridor surface routing stable.
- Right-side outer depth-3 floor-special routing now has matching smoke coverage with the existing left-side case.
- Texture-library surface-slot override state now has a public debug/test helper with manual and scene override coverage.

### Character / Shop UX

Status: `Partial`

Remaining work:

- Redesign the character menu
- Replace shop submenus with tabs where appropriate

Verification note:

- Repo inspection still points to shop tabs and character-menu redesign as unfinished work.

### Input / Redraw Behavior

Status: `Partial`

Remaining work:

- Continue broad stale-input protection when entering new areas and popups
- Continue standardizing background drawing
- Continue using cached views where helpful for cheaper redraws

Verification note:

- Stale-input protection is already present in multiple popup and dungeon flows (`flush_events`, `require_key_release`, and targeted `pygame.event.clear()` usage), but it is not yet uniform enough to mark this area complete.
- Quantity and code-entry popups now support the same `flush_events` / `require_key_release` protections as confirmation popups, with shop, barracks, and anti-magic terminal flows using them.
- Level-up info, stat selection, and inventory confirm/drop popups now use the same stale-input guard so buffered key presses do not skip modal choices.
- Level-up info, stat selection, loot, empty-chest, and unlock-key prompts now use the shared current-key-state guard behavior.
- Remaining shop, barracks, and combat-end confirmation popups now use the same stale-input guard too, so the modal behavior is consistent across the main pygame menu flows.
- The shared `confirm_yes_no()` helper now opts into `flush_events` and `require_key_release`, extending the stale-input guard to simple yes/no confirmations that use the helper.
- Inn, church, and quest-manager fallback popups now consistently use stale-input guards, and town-manager popups share a common background redraw helper.
- Reward-selection popups now support the same stale-input guard used by confirmation, quantity, and code-entry popups.
- Shared confirmation, reward-selection, quantity, and code-entry popups now use one guarded-input release helper so stale-input audits check the same arming rule.
- Shared modal popup guards now live in a reusable input helper that can arm from current keyboard state as well as release events.
- Top-level pygame game-flow confirmations now use shared stale-input guards, including debug-mode notices, race/class confirmation, town-menu confirmations, and warp-point prompts.
- Dungeon save/quit menu confirmations, Golden Chalice pickup confirmation, and the character-screen empty-key-items notice now use the same guarded modal input behavior.
- Shared pygame popup menus can now wait for key release before accepting selection input, and nested inventory action menus opt into that guard.
- Shared inventory/equipment/quest popup menus now use the current-key-state guard, so fresh keys are accepted even if no KEYUP event is delivered.
- Nested equipment action menus now opt into the same popup-menu stale-input guard as inventory action menus.
- Shared pygame popup menus now restore the previous background provider even if a popup exits through an exception.
- The barracks leave popup now redraws over the barracks menu background while using the shared stale-input guard.
- Promotion confirmation popups now use the shared town popup guard/background behavior.
- Nested inventory action menus now restore their temporary background override even if a nested popup exits through an exception.
- Loot and locked-door/chest key-use popups now support stale-input guards and use cached dungeon backgrounds when invoked from dungeon interactions.
- The in-dungeon escape menu now uses the same stale-input guard so the key press that opens it cannot immediately choose an option.
- Load-game, shop-selection, and reusable town location menus now support guarded navigation input, with main entry flows opting into stale-input protection.
- Main-menu, race-selection, class-selection, and town-hub navigation loops now support the same guarded input behavior, and the top-level game flow opts into it.
- Main-menu, town-menu, load-game, shop-selection, location, race-selection, and class-selection guards now arm from current keyboard state to avoid first-key stalls after transitions.
- Combat action-grid and combat submenu selectors now clear buffered input and wait for key release before accepting selection input.
- Reusable shop-screen option and item navigation loops now clear buffered input and wait for key release before accepting selection input.
- Top-level character-screen navigation now clears buffered input and waits for key release before accepting menu choices.
- Combat action-grid/submenu, shop-screen, and character-screen guards now also arm from current keyboard state so a fresh first key press is not blocked when no KEYUP event is pending.

### 3. Broader Test Coverage

Status: `Partial`

Testing work remains ongoing.

Current state note:

- The old roadmap metric of “13 test files” is outdated. The repo now contains substantially more test modules, but coverage gaps still remain in the areas below.
- The current tracked `test_*.py` module count is `81`, with active work now organized across `tests/core`, `tests/integration`, `tests/ui_pygame`, and `tests/ui_curses`.
- The latest full-suite run confirmed by the user is `1398` passing tests with `81%` total coverage across `src/`.
- The `ui_pygame` bucket is now broadly stabilized for Phase 1 coverage work; every currently measured module there is at or above `70%`.
- The test buckets now use package markers (`__init__.py`) so identically named files like `test_battle.py` and `test_town.py` collect cleanly across domains.

High-priority remaining coverage:

- Ability effects across the full ability set
- Status-effect interaction scenarios
- Combat-result consistency checks
  - focused `CombatResult` / `CombatResultGroup` snapshot and ordering coverage now exists

Medium-priority remaining coverage:

- Save/load round trips
  - foundation coverage now exists for inventory/storage, quest serialization, mutable tile state, SaveManager file IO, and gameplay-stat persistence
- Quest completion flows
  - pygame quest-manager diagnostics now summarize completed, turned-in, ready-to-turn-in, active, and total quest counts by category
- Enemy AI behavior

Lower-priority remaining coverage:

- Event bus emissions / infrastructure-level checks
  - focused event-bus diagnostics and unsubscribe-during-emit regression coverage now exists

### 4. Broader Type Hinting And Docstrings

Status: `Partial`

This remains unfinished.

High-value remaining targets:

- `abilities.py`
- `items.py`
- `enemies.py`
- `character.py` follow-up work beyond the initial pass

### 5. Further Balance Tuning

Status: `Planned`

The roadmap explicitly defers deeper numerical tuning until class kits are fully complete.

Remaining work:

- Revisit stat-dump tradeoffs
- Re-run race-baseline comparisons once class implementations are stable
- Revisit progression scaling outliers
- Tune remaining PvE outliers with simulator-backed reports

---

## Planned / Deferred

### 1. Gameplay Statistics

Status: `Confirmed`

Completed foundation work:

- Persistent player-side gameplay statistics are now tracked and saved
- Current tracked values include steps, stairs, enemies defeated, deaths, flees
- High-water marks now include highest level reached and peak damage dealt / taken
- Targeted tests cover statistics defaults, persistence, and core combat hooks
- A player-facing Statistics entry is available from the pygame town menu
- The pygame statistics popup now includes a derived encounters-survived line and defensive formatting for missing legacy values
- The pygame statistics popup now includes derived exploration-action and combat-survival-rate lines without adding save-format fields
- The pygame statistics popup now groups current counters into Exploration, Combat, and Records sections using a shared core summary helper

Remaining work:

- Decide whether richer history, run summaries, or permanent account-style statistics beyond the current grouped popup are worth adding later

Verification note:

- The current scoped statistics work is complete: tracked values are persisted and visible in the pygame UI.

### 2. Quest And Realm Expansion

Status: `Planned`

Planned work:

- Expand / finish realm content such as the Playhouse / Jester content
- Class-specific Class Ring questline
- Post-fight NPC dialogue changes
- Additional realm maps such as the Realm of Cambion follow-up content
- Additional special tiles such as Portal, Rotator, Teleporter, Fake Path where still missing

### 3. Equipment And Item Systems

Status: `Planned`

Planned work:

- Elemental armor options or modification system
- Special effects on ultimate armor
- Spell modifiers on cloth armor
  - completed: cloth armor now contributes to `check_mod("magic")` through a shared armor spell-modifier helper, with explicit `spell_mod` support for future item definitions
- Weapon efficiency stat
- Stat-themed item naming
- Enemy item use / stolen consumables
- Continue `crit` parameter cleanup to `crit_chance`
  - a backward-compatible `Weapon.crit_chance` alias now exists, and character critical-hit math prefers it when present
  - new weapon definitions can now use the `crit_chance` constructor keyword while legacy `crit` callers continue to work
  - curses shop item descriptions now show elemental metadata for any item type that exposes an `element`, including future elemental armor.

### 4. Racial Passives

Status: `Planned`

This remains a planned / follow-up gameplay feature area in the roadmap, even though an initial race identity pass has been completed.

Potential remaining work:

- Reconcile original “7 sins / 7 virtues” design ideas with the implemented race identity pass
- Decide whether additional racial passive depth is still desirable beyond the current always-on traits

### 5. Sound And Music

Status: `Partial`

Still planned:

- Replace placeholder sound effects with final assets
- Add background music assets

Clarification:

- The runtime sound/music system exists already; what remains is mostly content completion and polish.
- Repo inspection confirms that the music runtime exists, but the `src/ui_pygame/assets/music/` directory still lacks real music assets beyond documentation.
- Audio asset diagnostics now include every candidate path checked for each SFX/music name, which should make missing-content audits easier while final assets are still incomplete.
- SoundManager now has location/context music routing for town, shops, church, inn, dungeon, normal combat, boss combat, and final combat; actual music assets are still incomplete.
- Pygame top-level town/shop/church/inn/barracks/dungeon flows now request location music through that routing, and repeated requests for the active theme do not restart the track.
- Combat-start events now route normal, boss, and final combat music through the same theme helper, with pre-combat location music restored after combat ends when available.

---

## Recommended Near-Term Execution Order

### Phase 1: Verify And Stabilize

Status: `Active`

Goal:

- Bring the roadmap, test suite, and active pygame systems back into alignment so future work starts from a reliable baseline.

Remaining tasks:

- Review the remaining roadmap claims that were only marked `Partial` and confirm whether they should stay `Partial`, move to `Confirmed`, or move back to `Planned`
- Update stale roadmap metrics when they can be measured directly
  - current top-level test file count
  - current YAML ability count
  - current event type count
- Record measured metrics directly in the roadmap snapshot once verified
- Audit the pygame dungeon renderer transition for active regressions
  - remaining smoke-test failures
  - side-wall / door / depth-slot edge cases
  - boss-aftermath visual regressions after the completed replacement-visual pass
- Verify the current state of pygame combat presentation
  - status icon behavior
  - telegraph UI behavior
  - whether the current turn-indicator treatment needs further visual refinement
- Verify whether stale-input handling is broad enough across popups, area transitions, and menus
- Confirm whether shop tabs remain unimplemented or whether a partial replacement already exists in the current shop flow
- Decide whether gameplay statistics need richer history/run-summary UI beyond the current town-menu display
- Confirm whether sound/music should remain `Partial`
  - sound runtime/integration is implemented
  - final sound asset replacement is incomplete
  - music asset directory still needs real content
- Reconcile disabled, skipped, or recently flaky tests in the active renderer / pygame areas
- Document the outcome of the verification pass directly in the roadmap so Phase 2 starts from an accurate status file

Current progress:

- Verified and recorded current repo metrics
- Confirmed that baseline status icons and telegraph UI exist in pygame combat
- Confirmed that shop tabs and character-menu redesign still appear to be open roadmap items
- Confirmed that sound/music remains `Partial`: system code exists, final asset content is still incomplete
- Completed the gameplay-statistics tracking and persistence foundation plus a player-facing pygame town-menu statistics popup
- Closed the legacy collect-quest `What` deserialization gap and added focused compatibility coverage
- Added broader save/load round-trip coverage for mutable player inventories, quest data, and tile state restoration
- Added atomic SaveManager writes so a failed save does not corrupt the previous file
- Added save/tmp filename confinement and deterministic save-list ordering
- Save listing now ignores atomic-write leftovers and `.save` directories, keeping load-game choices limited to real save files
- Tile-state restoration now skips malformed per-tile state payloads while preserving valid neighboring tile state.
- Upgraded the battle logger from raw event capture only to structured payload and JSON export support
- Confirmed that stale-input protection is present in key flows but still not broad enough to mark complete
- Added a dedicated pygame combat turn-indicator treatment
- Added combat status-icon overflow handling and telegraph-colored combat log lines
- Added a dedicated telegraph banner and cleaner fixed-label turn indicator in pygame combat
- Prioritized combat status icons before overflow compaction so stun/sleep/silence/prone-style hazards remain visible ahead of buffs
- Confirmed that the active pygame stabilization hotspot is the dungeon renderer / smoke-test surface
- Added defeated-boss replacement visuals and open/closed minimap icon states for doors and chests
- Added dungeon texture-library fallback diagnostics for missing wall, special-tile, and enemy sprite assets
- Added renderer regression coverage for mixed single-side-door / opposite-side-special center-wall layouts
- Added a dungeon viewport vignette cleanup pass with regression coverage
- Refined the dungeon viewport edge vignette into layered bands plus a subtle HUD separator
- Tightened side-corridor floor-sprite depth and clip behavior so opening sprites follow the deeper corridor geometry
- Extended stale-input protection to quantity, code-entry, level-up, inventory, shop, barracks, and combat-end modal flows
- Extended the same status-icon priority/overflow behavior to the combat-mode dungeon HUD
- Added stable enemy action metadata for selected weighted `action_stack` entries, including ability, priority, delay, and telegraph fields.
- Added checked-path details to audio asset diagnostics for missing SFX/music follow-up work.
- Added SoundManager location/context music-theme routing for future music integration.
- Wired pygame top-level location transitions into SoundManager music-theme routing.
- Added a repeat-theme guard so location music requests do not restart the currently active track unless forced.
- Routed combat-start events to normal/boss/final combat music themes and restored the previous location theme after combat end.
- Extended weapon construction to accept the clearer `crit_chance` keyword without breaking existing item definitions.
- Added quest status summary diagnostics for completion/turn-in flow audits.
- Added left-side outer-corridor door-state smoke coverage to match the existing right-side checks
- Extended stale-input protection to shared `confirm_yes_no()` prompts
- Standardized inn/church town-manager popups on shared guarded popup kwargs with background redraw support
- Extended guarded popup behavior through quest-manager fallback messages, accept/decline prompts, reward selection, and Busboy event fallbacks
- Extended guarded popup behavior to top-level game confirmations, dungeon save/quit and chalice prompts, and the character-menu empty-key-items notice
- Extracted shared pygame status-icon priority, overflow, and color helpers for combat view and combat-mode dungeon HUD
- Added depth-2 side floor-special geometry coverage so side props stay aligned with depth-3 outer-lane placement
- Added high-alert coloring for urgent negative combat status icons in both combat view and combat-mode dungeon HUD
- Added compact status-label fitting so long labels cannot overflow their icon pills
- Tightened combat-log wrapping for the narrower dungeon-combat overlay pane so charge/telegraph lines stay inside both log surfaces
- Extended stale-input protection into reusable popup-menu selection loops and the nested inventory action menu
- Extended stale-input protection to nested equipment action menus
- Hardened reusable popup-menu background-provider restoration with a `finally` guard
- Kept the barracks leave popup on its local background while preserving guarded modal input
- Fixed side-view chest sprite rendering so chests stay upright instead of skewing through the lateral floor projection path
- Added left-side outer depth-3 floor-special smoke coverage for side-corridor presentation parity
- Fixed detected closed Ore Vault door rendering so the dungeon scene treats it as a visible blocking door instead of an open corridor
- Added Maelstrom Weapon stack visibility to the main combat status-icon row
- Extended guarded popup/background behavior to promotion confirmations and hardened nested inventory action-menu restoration on exceptional exits
- Collapsed duplicate combat status icons into counted compact pills before overflow handling
- Added side-opening Ore Vault door regression coverage for detected versus hidden presentation
- Extended stale-input protection and cached-background rendering to loot and key-use dungeon popups
- Kept telegraph banners tied to the full latest unwrapped warning line so long charge messages do not degrade into partial fragments
- Added open Ore Vault door renderer coverage for the current open-passage behavior
- Extended stale-input protection to the in-dungeon escape menu
- Switched the in-dungeon popup menu to the shared physical-key-state input guard so fresh keys are accepted without a KEYUP event.
- Switched reusable inventory/equipment/quest popup menus to the shared physical-key-state input guard.
- Cleared active telegraph banners after non-telegraph combat messages so resolved charge warnings do not linger
- Extended guarded navigation input to load-game, shop-selection, and reusable town location menus
- Added left-side outer corridor floor/ceiling/wall slot-ID parity coverage for future renderer edits
- Extended guarded navigation input to main-menu, race-selection, class-selection, and town-hub selection loops
- Added dense dungeon-combat HUD status-icon coverage for urgent counted effects plus overflow behavior
- Widened dungeon-combat HUD status pills enough to preserve counted four-character labels before fitting/truncation
- Extended guarded input to the combat action grid plus item, spell, skill, and Totem aspect selection overlays
- Added left depth-3 outer side-corridor wall continuation smoke coverage
- Extended guarded input to reusable shop-screen option and item selection loops
- Tightened combat selection overlay label fitting for long item/spell/skill/Totem names
- Added depth-3 outer side-corridor floor/ceiling slot-ID parity coverage
- Extended guarded input to top-level character-screen navigation
- Tightened combat turn-indicator name fitting for long player/enemy names
- Added right-side outer depth-3 floor-special smoke coverage
- Increased Old Key quest rewards for early/main quest turn-ins and added loader-level regression coverage for the new reward counts
- Added pygame quest-manager turn-in regression coverage for the Old Key rewards and their turned-in state
- Added SaveManager round-trip regression coverage for Old Key inventory counts
- Tightened the analytics quick-balance helper so it returns an explicit empty `BalanceReport` instead of falling through as `None`
- Added BattleLogger JSON file export support for debugger/tooling workflows
- Hardened EventBus bounded history so `max_history=0` disables history storage without disabling subscribers
- Hardened action-queue helper scheduling by clamping negative delays/cast times and tagging helper-created actions with debug metadata
- Switched the pygame Settings placeholder to the shared guarded modal popup path so buffered menu input cannot skip it
- Added distinct Blind Rage status-icon labeling and urgent prioritization for combat readability
- Suppressed zero-value Enfeeble/stat-effect reporting and stale zero-value combat status icons so no-change debuffs do not read as positive buffs.
- Centralized zero-value stat-effect icon filtering so combat view and dungeon HUD share the same no-op suppression rule.
- Added stat-effect icon filtering diagnostics so zero-value suppressed status effects can be audited without rendering combat.
- Tuned Half Giant drawbacks so Giant Warrior-style starts keep their physical identity but carry clearer low-agility and magic-vulnerability costs.
- Hardened SaveManager listing to hide temporary save leftovers and directory entries
- Added a derived encounters-survived line plus defensive legacy-value handling to the pygame statistics popup
- Gameplay-stat normalization now clamps negative legacy/manual counter values before derived statistics are displayed.
- SaveManager now exposes compact save-directory diagnostics for visible saves, temporary leftovers, directory-like save entries, and ignored files.
- SaveManager save-file metadata now flags empty files, and save-directory diagnostics include total hidden entries.
- Added structured JSON payload/file export support to combat simulator balance reports
- Added renderer texture-library helper coverage for manual and scene surface-slot override state
- Extended panel surface-slot state diagnostics to label each slot as default, scene-overridden, or manually overridden
- Added compact per-panel surface-slot source summaries for side-corridor and door diagnostics.
- Hardened tile-state restore against malformed per-tile payloads
- Hardened top-level pygame cleanup so presenter background providers are cleared and pygame quits even if presenter cleanup raises
- Added compact combat simulator balance summary payloads with limited top-ability and top-status lists
- Hardened renderer surface-slot overrides so invalid debug/test entries are ignored while valid neighboring floor, ceiling, and wall overrides still apply
- Improved combat status-icon ordering so counted labels use count-aware stable tie-breaks without overriding urgent-status priority
- Hardened pygame presenter popup-background fallback so broken or empty providers are cleared after falling back to the screen copy
- Pygame presenter popup-background diagnostics now expose provider presence and fallback counts for stale-provider audits.
- Extracted a core gameplay-stat summary helper so pygame statistics and tests share normalized derived counters
- Added panel-scoped renderer surface-slot override diagnostics for focused side-corridor and door debugging
- Hardened SaveManager filename handling for blank names and made save deletion explicitly file-only
- Hardened combat status-icon label fitting for zero-width and overflow marker edge cases
- Added compact BattleLogger summary payloads for debug views that do not need raw per-event rows
- Extended renderer panel diagnostics to report default and effective texture keys per surface slot
- Hardened SaveManager loading so directory-like save entries are treated as missing files
- Hardened level-up and stat-selection popup background fallback when providers return the live screen or no surface
- Added compact EventBus history counts for debug/test checks without walking raw event lists
- Added projected-surface cache diagnostics for renderer smoke tests and debugging
- Added save/load regression coverage for corrupt normal and temporary JSON save files
- Hardened confirmation popup background fallback when providers return the live screen or no surface
- Added compact EventBus subscriber counts for debug/test diagnostics
- Added compact texture-library fallback counts so missing wall, special-tile, and enemy assets can be checked without scanning raw paths
- Standardized shared confirmation, choice, reward, quantity, and code-entry popup background fallback so empty or live-screen providers fall back to copied surfaces
- Exposed SaveManager save-filename validation for UI/debug checks while preserving existing path-confinement behavior
- Added compact EventBus diagnostics combining enabled state, history bounds, history counts, and subscriber counts
- EventBus diagnostics now also report whether bounded history is full and the compact subscriber total.

Latest focused phase:

- Completed a compact diagnostics pass across save metadata, EventBus state summaries, and renderer asset fallback reporting.
- Added regression coverage for expected save extensions and empty-save counts, EventBus retained/subscriber event-type lists, and grouped renderer fallback keys.
- Deferred first-key input-loop behavior and larger visual/UX changes so this pass could stay focused on safe debug/test helpers.

Previous focused phase:

- Completed a compact debug-summary pass across combat status layout diagnostics, audio asset summaries, and battle-log damage summaries.
- Added regression coverage for visible/hidden status polarity counts, audio available/missing name lists, and battle-log damage-row counts.
- Deferred input-loop behavior changes for the first-key issue and larger renderer/shop/character UX work because this pass focused on deterministic helper diagnostics.

Earlier focused phase:

- Completed a diagnostic-focused stabilization pass across renderer texture diagnostics, popup background providers, and save tile-state payload inspection.
- Added regression coverage for renderer cache capacity/fullness, popup background fallback counts, and malformed tile-state payload summaries.
- Deferred larger renderer geometry changes, shop-tab UX, character-menu redesign, and content/balance expansion to later phases because this pass stayed on small, low-risk debug and regression helpers.

Earlier compact phase:

- Completed a compact stabilization pass across combat status readability, save/stat diagnostics, and EventBus debug payloads.
- Added regression coverage for zero-value stat debuffs, stale zero-value status icons, negative legacy gameplay counters, save-directory entry counting, and extended EventBus diagnostics.
- Deferred larger renderer, shop-tab, character-menu, and content-expansion work to later phases because they exceed the intended small-task scope of this pass.
- Added aggregate texture-library diagnostics for loaded state, fallback counts, projected cache state, and surface-slot override state
- Added derived combat-outcome and total-activity counters to gameplay-stat summaries without adding new save fields
- Added SaveManager save-file metadata diagnostics for menu/debug checks without reading save payloads
- Added BattleLogger event-type and flag-count diagnostics to compact battle summaries
- Added compact combat status-icon layout diagnostics for visible, hidden, overflow, and urgent-visible counts
- Added renderer surface-slot override diagnostics that split manual and scene override counts while tracking revision changes
- Added sound/music asset availability diagnostics for checking expected SFX and music content without loading or playing assets
- Added SaveManager visible-save metadata listing that mirrors load-menu filtering without parsing save contents
- Added BattleLogger actor and target count diagnostics to compact battle summaries without raw event rows
- Extended combat status-icon layout diagnostics with capacity and rendered row counts for dense status rows
- Added default sound/music asset diagnostics for the runtime's expected SFX and music names
- Added visible-save metadata summaries for count, total size, and largest player-visible save diagnostics
- Added BattleLogger positive damage attribution by actor and target to compact battle summaries
- Extended combat status-icon layout diagnostics with overflow state and hidden urgent-status counts
- Added sound/music availability summary counts for expected audio asset diagnostics
- Extended save metadata diagnostics with loadability flags and visible filename summaries

Current stabilization priorities:

- Renderer structural-depth and side-corridor behavior
  - keep center-wall stopping behavior correct without breaking legitimate depth-2/depth-3 side-slot routing
  - preserve outer-corridor wall/floor/ceiling rendering where the smoke tests expect it
- Door and side-opening presentation
  - continue validating side-door hiding rules versus center-wall depth
  - keep slot-based door rendering aligned with wall-layer expectations
  - preserve the current single-side-door visibility behavior unless playtesting proves it is confusing
- Special-tile rendering consistency
  - keep quest-gated visuals from leaking into generic renderer tests
  - preserve migrated special-tile sprite coverage in smoke tests
  - continue floor-bound placement polish for future props beyond the completed defeated-boss replacement visual
- Asset fallback visibility
  - use the texture-library fallback diagnostics when renderer tests or manual play hit missing assets
  - invalid renderer surface-slot override entries are filtered before they can affect panel composition
  - panel-scoped surface-slot override diagnostics are available for focused renderer smoke tests
  - panel diagnostics now include default and effective texture keys for each surface slot
- projected-surface cache diagnostics expose current size and configured limit
- projected-surface cache diagnostics now also expose remaining capacity and full/not-full state
- asset fallback diagnostics now expose compact counts by asset category for quick renderer/debug checks
- asset fallback diagnostics now expose grouped fallback texture keys by category for quick missing-asset identification
- aggregate texture diagnostics now include total fallback count alongside per-category counts
  - aggregate texture-library diagnostics now combine fallback/cache/override state for quick debug assertions
  - surface-slot override diagnostics now distinguish manual overrides from scene-driven overrides during renderer smoke checks
  - per-panel surface-slot summaries now count default, scene, and manual sources for focused side-corridor checks

Current non-visual Phase 1 track:

- Gameplay-statistics foundation
  - completed: persistent player-side counters for steps, stairs, deaths, flees, defeats, and high-water combat stats
  - completed: expose the tracked data through a player-facing pygame statistics popup
  - completed: show derived encounters survived and tolerate malformed legacy stat values in the popup formatter
  - completed: share derived gameplay-stat summary counters through a core helper for UI/tooling reuse
  - completed: gameplay-stat summaries now include derived combat-outcome and total-activity counters from existing save data
  - completed: gameplay-stat summaries now include exploration-action and combat-survival-rate counters for the pygame Statistics popup
  - completed: gameplay-stat summaries now provide grouped Exploration, Combat, and Records payloads for UI/tooling displays
  - remaining: decide whether persistent history or run-summary views beyond the grouped current-run display are worth adding later
- Save/load robustness
  - completed: collect-quest item deserialization now resolves both serialized items and legacy string saves
  - completed: added round-trip coverage for mutable quest, inventory, storage, and tile-state persistence
  - completed: SaveManager writes are atomic and reject path-bearing save names
  - completed: SaveManager lists only real `.save` files, ignoring temp leftovers and directories
  - completed: tile-state restore ignores malformed per-tile state payloads without aborting valid restores
  - completed: tile-state payload diagnostics count valid entries, malformed position keys, malformed state payloads, and positions absent from the current world
  - completed: tile-state payload diagnostics now expose restorable attribute counts plus unknown legacy/custom attribute keys
  - completed: blank save names are rejected and delete operations refuse directories
  - completed: load operations treat directory-like save entries as missing files
  - completed: corrupt save JSON loads return `None` without deleting the original file
  - completed: save-filename validation is now available as a public helper for menu/debug callers before file operations
  - completed: save-file metadata diagnostics can report validity, path type, existence, and file size without parsing JSON
  - completed: save-file metadata diagnostics now report the expected extension and whether the filename matches it
  - completed: visible-save metadata can now be listed in load-menu order while excluding temp leftovers and directories
  - completed: visible-save metadata summaries now expose count, total size, and largest save without parsing save payloads
  - completed: visible-save metadata summaries now include loadable and empty-save counts for menu/debug checks
  - completed: save metadata diagnostics now expose loadability and visible filenames for load-menu sanity checks
  - completed: save-directory diagnostics now include grouped hidden-entry filename lists for temp leftovers, directory-like saves, and ignored files
  - remaining: broaden only if new persistence failures appear in specific systems
  - completed: pygame load-game navigation can delete selected save files through the hardened SaveManager delete path
- Combat/logging infrastructure
  - completed: battle logger now supports structured payload and JSON export for debugging/tooling
- completed: battle logger can persist structured JSON logs directly to disk for local analysis
  - completed: battle logger can export compact metadata + summary payloads without raw event rows
  - completed: quick-balance helper now returns an explicit empty report while full class factory wiring remains deferred
  - completed: action-queue helper actions now carry lightweight metadata for debugging/analytics
  - completed: simulator balance reports now export structured JSON payloads and files for local analysis
  - completed: battle logger compact summaries now expose event-type and flag counts without raw event rows
  - completed: battle logger compact summaries now split numeric damage-event count from positive-damage-event count
  - completed: battle logger compact summaries now expose actor and target counts for quick turn-flow sanity checks
  - completed: battle logger compact summaries now expose positive damage totals by actor and target
  - completed: pygame debug-mode combat endings automatically persist structured battle logs under `debug_logs/battles/`
- Combat status presentation
  - completed: compact status-icon layout diagnostics expose visible/hidden/overflow counts for focused readability checks
  - completed: status-icon layout diagnostics now split visible and hidden icons into positive, negative, and neutral counts
  - completed: status-icon layout diagnostics now report capacity and row count for dense overlay validation
  - completed: status-icon layout diagnostics now report whether overflow is active and whether urgent statuses were hidden
  - completed: status-icon layout diagnostics now expose visible/hidden label lists plus urgent visible/hidden label lists for focused readability audits
- Sound/music content visibility
  - completed: sound manager diagnostics can report expected sound-effect and music asset availability without requiring final content
  - completed: default audio diagnostics now use the runtime's expected SFX and music name lists for content checks
  - completed: audio diagnostics now summarize available and missing SFX/music counts for quick content audits
  - completed: audio diagnostics now include available and missing SFX/music name lists alongside summary counts
- Test debt that removes skips or weak assertions
  - replace skipped or placeholder-oriented tests with real assertions where the missing functionality is now small enough to implement
  - strengthen agent-friendly regression coverage in core systems before Phase 2 polish work continues
  - current high-leverage coverage targets have shifted away from `ui_pygame` and now primarily live in the remaining medium-coverage `core` and `ui_curses` modules
  - prefer medium-sized deterministic helper modules and shared UI/menu layers over sprawling end-to-end screen loops when the goal is near-term percentage lift plus regression value
  - compact EventBus history counts are now available for focused debug/test assertions
  - compact EventBus subscriber counts are now available for duplicate-subscription diagnostics
  - compact EventBus diagnostics now summarize enabled/history/subscriber state without requiring raw event inspection
  - compact EventBus diagnostics now include retained-history remaining capacity plus sorted history/subscriber event-type lists
- Small core-quality tasks
  - resolve narrow TODOs that are self-contained, non-visual, and low-risk in `save_system.py`, `battle_logger.py`, `character.py`, and related core modules

Current targeted coverage lift:

- Expanded analytics-focused test work around `combat_simulator.py`
  - cover report aggregation, summary rendering, helper metrics, deterministic seeding, and draw outcomes
- Expanded companion coverage around `companions.py`
  - cover familiar progression, summon constructors, summon action menus, and summon-level ability unlocks
- Expanded town-system coverage around `town.py`
  - cover bounty generation, quest-dict caching, and Holy Grail hint rotation behavior
- Expanded combat-core coverage around `battle_engine.py` and `action_queue.py`
  - cover forced actions, spell/skill/item/summon branches, post-turn cleanup, end-of-battle outcomes, queue helpers, and turn-manager flow
- Expanded a narrow utility/state slice of `player.py`
  - cover gameplay-stat helpers, race EXP modifiers, level/town/location helpers, item/ability usability checks, weight helpers, death penalties, and deterministic familiar support behavior
- Expanded a second `player.py` slice around combat-adjacent state transitions
  - cover transform forward/back behavior, Soulcatcher/Lycan class-upgrade branches, end-of-combat victory/defeat bookkeeping, and additional familiar Arcane/Luck behavior
- Expanded `save_system.py` coverage around serializers and SaveManager file IO
  - cover item/ability/enemy serializer helper branches, jump/totem skill-state detection, save/load/list/delete flows, error handling, JSON payload writing, and legacy defeated-boss restoration fallback
- Expanded a third `player.py` slice around quest/menu helper logic and combat modifiers
  - cover quest progression branches, UI-agnostic character/quest/summon menu behavior, `special_power`, status/combat/equipment/resistance string helpers, and broader `check_mod` branches for shield/magic/heal/luck/speed/armor/resistance handling
- Expanded `character.py` coverage around low-risk combat helpers and status processing
  - cover silence/anti-magic suppression, defensive stance helpers, healing/shop multipliers, disarm helpers, hit/dodge/crit helper branches, duplicate handling, shield/defense/flee/inventory helpers, and several duration-based effect-processing paths
- Expanded tiny core helper-module coverage
  - cover `tutorial.py` exit behavior plus low-level `effects` helper modules for direct damage/healing/regeneration/status application
- Expanded `items.py` coverage around consumables, scrolls, and class-accessory rules
  - cover health/mana/elixir behavior, Dwarf hangover side effects, stat potions, status cures, scroll charge consumption, and representative `ClassRing` description/modifier branches
- Expanded a second `items.py` slice around accessory rules, status helpers, and metadata-heavy item constructors
  - cover the remaining `ClassRing` class branches, out-of-combat Dwarf hangover-step clamping, additional status-item early returns, non-final scroll charges, and key/pendant metadata constructors
- Expanded a third `items.py` slice around item-catalog breadth and shared helper utilities
  - cover broad no-arg item instantiation/rendering across weapons, armor, off-hands, accessories, potions, and misc items, plus loot-table caching, rarity clamping, `remove_equipment()`, and base item helper constructors
- Expanded `enemies.py` coverage around constructor catalog breadth and legacy enemy behavior helpers
  - cover broad no-arg enemy instantiation/rendering, deterministic `random_enemy` / `funhouse_enemy` selection, berserk/turtle/ice-block short-circuit behavior, legacy pickup/surface/flee action paths, and required-argument constructors like `Mimic` and `FunhouseMinion`
- Expanded `ui_pygame` coverage around presentation interfaces and sound-management helpers
  - cover `GamePresenter` / `NullPresenter` / `EventDrivenPresenter` / `ConsolePresenter` behavior, plus `SoundManager` mixer init, event routing, sound/music loading, volume control, cleanup, and singleton access
- Expanded `ui_pygame` coverage around shared town-screen helpers
  - cover town background loading/fallbacks, centered background drawing, semi-transparent panels, and debug/non-debug quest-text rendering flow in `town_base.py`
- Expanded `ui_pygame` coverage around reusable shop-manager helpers
  - cover blacksmith/alchemist/jeweler visit flow, buy/sell/shop-screen branching, quantity/confirmation popup paths, item-info formatting, item-availability filtering, and secret-shop submenu delegation in `shops.py`
- Expanded `ui_pygame` coverage around shared shop-screen layout and navigation helpers
  - cover background scaling, window-rect calculation, buy/sell list construction and filtering, description/list/gold rendering, cached equipment-diff display, and option/item navigation/scroll behavior in `shop_screen.py`
- Expanded `ui_pygame` coverage around shared popup helpers and modal input flows
  - cover confirmation wrapping/reveal gating/background restoration, choice-popup navigation, reward-selection confirmation, quantity adjustment/confirmation, code-entry digit editing, and the `confirm_yes_no()` helper in `confirmation_popup.py`
- Expanded `ui_pygame` coverage around quest-offer and turn-in flow helpers
  - cover renderer formatting, chalice-hint progression, eligible/help-hint selection, prerequisite checks, accept/decline quest offers, reward handling and collect cleanup on turn-in, Busboy post-quest events, and `check_and_offer()` turn-in/help/no-quest branches in `quest_manager.py`
- Expanded `ui_pygame` coverage around dungeon-manager navigation and shared helper flow
  - cover enemy resolution, message-log wrapping/scroll/reset behavior, random cry hints, dungeon background/loading-screen helpers, popup-background caching, spawn-tile selection after stairs, movement blockers/success cases, turning, stair usage, secret-shop interaction, and dungeon dialogue/choice/event helper wiring in `dungeon_manager.py`
- Expanded a second `ui_pygame` `dungeon_manager.py` slice around object interactions and room-state transitions
  - cover chest unlock/mimic/loot paths, door unlock flows, relic-room rewards and restore behavior, warp-point return logic, anti-magic terminal code-entry handling, unobtainium pickup, and dead-body quest-item acquisition
- Expanded a third `ui_pygame` `dungeon_manager.py` slice around spring/Nimue flow, tile intros/effects, and exploration-loop behavior
  - cover underground-spring quest/item/summon/realm interactions, additional tile-intro branches, fire/town-teleport/enemy-combat tile effects, final-room/incubus/chalice interactions, and the main explore/render loop wiring
- Expanded a fourth `ui_pygame` `dungeon_manager.py` slice around remaining menu/popup control flow and render fallbacks
  - cover character-menu quit/unimplemented branches, dungeon-menu character/save paths, popup navigation/cancel handling, and render cache/error bookkeeping paths
- Expanded `ui_pygame` coverage around reusable inventory/equipment/quest popup-menu helpers
  - cover shared base popup navigation/drawing behavior, inventory sorting/equip/use/drop flows, equipment selection and unequip helpers, quest list/detail rendering, simple-list inspect flow, and jump/totem/selection popup helper behavior in `popup_menus.py`
- Expanded a second `ui_pygame` `popup_menus.py` slice around secondary sort/detail and nested-selection branches
  - cover base-popup default helper paths, additional inventory sort modes and canceled-drop behavior, equipment unequip nested selection, no-quest and callable reward collection branches, fallback detail rendering, “not learned” jump/totem selection paths, extended selection-popup details, and concrete equipment-diff preview behavior
- Expanded `ui_pygame` coverage around `pygame_presenter.py` event flow and presenter helpers
  - cover floating-text animation, event subscriptions and combat-event reactions, combat-log/telegraph rendering, list/grid/split-layout menus, message dialogs, progress popup flow, background-provider fallback handling, player-input helpers, confirmation/dialogue wrappers, and lightweight map/character-sheet rendering
- Expanded `ui_pygame` coverage around level-up progression helpers and overlays
  - cover level-up gain calculation and application, spell/skill upgrade handling, familiar/jump/totem unlock side effects, stat-selection flow, popup-background fallback behavior, confirmation messaging, and level-up info rendering in `level_up.py`
- Expanded `ui_pygame` coverage around loot popup rendering and key-use prompts
  - cover loot normalization and empty-chest flow, animated loot popup rendering, rarity/description/stat rendering, default background fallback handling, unlock prompt navigation, and prompt rendering helpers in `loot_popup.py`
- Expanded `ui_pygame` coverage around top-level game bootstrap and menu-routing helpers
  - cover signal handling, presenter/bootstrap wiring, default character creation, debug level-up flow, manager initialization, bounty refresh, intro/load/save/menu routing, warp-point handling, character-menu quit flow, and cleanup in `game.py`
- Expanded `ui_pygame` coverage around location and shop-selection menu helpers
  - cover location menu header/options/content rendering, item-list display, content-list navigation and wraparound behavior, plus shop-selection panel rendering, navigation wraparound, selection, cancel, and quit-event handling in `location_menu.py` and `shop_selection.py`
- Expanded `ui_pygame` coverage around town-hub menu and inn/church manager helpers
  - cover town-menu panel rendering, debug-level-up hook, selection/cancel/quit handling, plus inn patron routing, bounty acceptance/turn-in/view flow, and church visit routing, save behavior, and promotion guard/success branches in `town_menu.py`, `inn.py`, and `church.py`
- Expanded a second `ui_pygame` combat/quest manager pass around turn-flow and popup-only branches
  - cover combat start/initiation flow, sanctuary escape handling, pre-turn skip/forced-action player branches, enemy-turn skip/forced/nothing/damage paths, plus popup-based quest offer/turn-in branches, warp/gold rewards, relic auto-complete handling, and Busboy event popup fallbacks in `combat_manager.py` and `quest_manager.py`
- Expanded `ui_pygame` coverage around low-coverage town and character-selection screens
  - cover promotion-screen detail rendering and confirm/cancel navigation, barracks special-event/storage/store/retrieve flows, and class-selection class filtering, stat/detail rendering, selection, cancel, and quit handling in `promotion_screen.py`, `barracks.py`, and `class_selection.py`
- Expanded a second low-coverage `ui_pygame` sweep around race-selection and deeper church promotion branches
  - cover race filtering/detail rendering, resistance/virtue/sin display, selection/cancel/quit flow, plus church promotion option-unavailable handling, level-1 spell/skill grant branches, Warlock familiar binding, Summoner pet setup, nested promotion flow, and guarded promotion-failure behavior in `race_selection.py` and `church.py`
- Expanded initial `ui_curses` coverage around battle wrappers, queue helpers, and class/promotion UI helpers
  - cover battle-screen rendering, status-text filtering, player input routing, forced/inactive turn flow, summon/flee/boss end-battle cleanup, familiar selection, curses promotion go-back/success behavior, and enhanced action-queue telegraph/scheduling/execution helpers in `battle.py`, `classes.py`, and `enhanced_manager.py`
- Expanded initial `ui_curses` game-controller coverage around bootstrap, menu routing, creation/load flows, and bounty/event helpers
  - cover constructor/main-menu setup, debug level-up flow, new-game character creation, save-load cleanup, run-loop town routing, bounty refresh/delete helpers, and special-event popup display in `game.py`
- Expanded second-pass `ui_curses` coverage around promotion edge cases and queue-turn orchestration
  - cover second-tier promotion flow, duplicate spell/skill gains, Warlock/Shaman/Summoner/Wizard special branches, promotion decline behavior, plus enhanced-manager turn-start/end events, queue scheduling/execution orchestration, and additional summon/flee after-turn paths in `classes.py` and `enhanced_manager.py`
- Expanded initial `ui_curses` town-manager coverage around quest, storage, church, warp-point, and town-hub helpers
  - cover ultimate-weapon crafting flow, quest turn-in/acceptance helpers, prerequisite-aware quest checks, Holy Grail hint dialogue, barracks key/storage handling, church promotion-save-quit routing, warp-point travel, and town-menu character/warehouse/dungeon branches in `town.py`
- Expanded a second `ui_curses` `town.py` slice around tavern board flow, Sergeant hints, armor crafting, and shop wrappers
  - cover bounty accept/abandon/turn-in branches, Chalice Map Sergeant guidance, storage retrieval, alchemist/jeweler quest wrappers, unavailable church promotion messaging, warp decline, and ultimate-armor repository selection/crafting in `town.py`
- Expanded initial `ui_curses` shared-menu coverage around input helpers, base navigation, and popup infrastructure
  - cover typed input, ascii-art loading, save/load popup progress display, main-menu debug/navigation flow, new-game and load-game menu selection helpers, town/location menu navigation, generic popup/selection/shop/confirm popup behavior, combat popup option filtering, quest-list summaries, and textbox rendering helpers in `menus.py`
- Expanded a second `ui_curses` `menus.py` slice around inventory, equipment, ability, and modifier popup families
  - cover inventory sort modes, paging, combat-usable filtering, key-item inspection, equip-popup option generation and diff confirmation, ability inspection/use-out flow, empty-ability fallback, plus Jump and Totem modifier/aspect popup toggling and descriptions in `menus.py`
- Expanded a third `ui_curses` `menus.py` slice around promotion, combat, quest, and mini-game popups
  - cover promotion-popup class/familiar render branches, deeper combat-popup filtering and item selection, slot-machine and blackjack helper flows, confirm-selection reward popup behavior, quest-popup text rendering, and quest-list navigation through active/completed/turned-in sections in `menus.py`
- Expanded a fourth `ui_curses` `menus.py` slice around the remaining screen-style shared menu classes
  - cover dungeon-screen map/room/control rendering, shop-screen item/config/mod/gold/navigation helpers, and character-screen panel rendering plus grid navigation in `menus.py`
- Expanded `map_tiles.py` coverage around quest helpers, movement tiles, and special-room interactions
  - cover Chalice quest reveal flow, Cambion realm state/message helpers, stairs/ladders, combat-path action menus, fire/funhouse tiles, spring/boulder interactions, traps/doors/chests, relic/warp/funhouse transport, and several story/shop tile branches
- Expanded a fourth `player.py` slice around progression, save/equip wrappers, and map-loading helpers
  - cover gameplay-stat normalization, tmp-load cleanup, tiled-map parsing/loading helpers, level-up spell/skill/jump/totem unlock flows, inventory/key-item/menu wrappers, save wrapper branches, equip/two-handed conflict handling, open-chest/open-door helpers, and remaining movement/action helper branches
- Expanded a fifth `player.py` slice around loot logic and equipment-preview helpers
  - cover gnome gold bonus handling, quest/ability/special/summon drop rules, jump unlocks from items and boss defeats, duplicate summon-item suppression, equip-diff preview branches, promotion unequip helpers, and unknown open-target assertions

Recommended immediate fix order:

1. Remove easy test skips / placeholders in core systems
2. Continue `player.py` as a sequence of narrow behavior slices rather than treating it as a single coverage target
3. Continue medium-sized `ui_curses` and remaining core slices before attempting any giant legacy screen/controller loops
4. Build on the new `save_system.py` coverage with broader end-to-end SaveManager round-trip scenarios if persistence still feels under-tested
5. Return to the remaining core combat/content clusters only if they offer better leverage than the next shared `ui_curses` helper module
6. Decide whether structured battle logs need file persistence or simulator integration next
7. Continue renderer presentation cleanup around wall, door, side-corridor, and vignette edge cases
8. Revisit statistics only if persistent history/run-summary behavior becomes a clear gameplay need

Definition of done for Phase 1:

- Roadmap status labels match the repo well enough to be trusted
- Known renderer/UI regressions are either fixed or explicitly called out as current blockers
- The active test surface for the new dungeon renderer is stable enough to support continued UI polish work
- A parallel non-visual task lane is identified and scoped tightly enough to be executed safely by agents

### Phase 2: Finish Pygame Polish

Status: `Planned`

Goal:

- Turn the currently functional pygame experience into a stable, coherent, and visually consistent primary UI layer.

Primary workstreams:

- Combat UI polish
  - completed: status icons cap visible rows and show a `+N` overflow marker under many simultaneous effects
  - completed: status icons prioritize urgent negative effects before positive buffs so overflow preserves the most actionable states
  - completed: combat view and combat-mode dungeon HUD now share status-icon priority/overflow/color helpers
  - completed: urgent negative status icons now receive a stronger alert color in both combat status displays
  - completed: compact status-icon labels now trim to fit their pills
  - completed: counted status-icon labels now use stable count-aware ordering inside the existing priority buckets
  - completed: status-icon fitting now handles zero-width pills and overflow markers without returning oversized labels
  - completed: combat selection overlays now fit long labels by rendered pixel width
  - completed: combat turn-indicator subtitles now fit long names inside the banner
  - completed: telegraph-like combat log lines use warning coloring in both combat render modes
  - completed: telegraph-like combat log lines wrap to the active combat-log pane width in both render modes
  - completed: telegraph messages also surface in a dedicated warning banner
  - refine the current turn-indicator treatment if playtesting shows it is not sufficient
  - evaluate where lightweight spell or hit effects add clarity rather than noise
- Dungeon renderer and exploration polish
  - resolve remaining wall, door, and side-corridor edge cases in the scene renderer
  - completed: left and right outer side-corridor door-state smoke tests cover open/closed texture preservation
  - completed: depth-2 side floor-special placement is covered for left/right outer-lane parity
  - completed: side-view chest sprites now render upright rather than using skewed floor projection
  - completed: left-side side-corridor floor-special routing is covered for outer depth-3 placement
  - completed: depth-3 outer side-corridor floor and ceiling slot IDs are covered on both sides
  - completed: right-side side-corridor floor-special routing is covered for outer depth-3 placement
  - finish special-tile placement polish for floor-bound sprites and future migrated props
  - remove or rewrite any outdated rendering assumptions left over from the legacy dungeon renderer
  - make smoke-test expectations and renderer behavior converge so regressions are caught early
  - keep the new soft vignette honest if future playtesting suggests it needs tuning
  - continue tuning the remaining edge framing if the viewport/HUD boundary still feels abrupt in play
- Character / shop UX cleanup
  - decide whether the character menu needs a full redesign or a focused cleanup pass
  - reduce friction in inventory, equipment, and comparison flows
  - decide whether shop tabs should replace the current shop mode selection flow
  - completed: reusable pygame shop item lists now support PageUp/PageDown plus Home/End navigation for long inventories
  - standardize popup behavior across town, shop, dungeon, and combat interactions
- Input, redraw, and presentation consistency
  - extend stale-input protections anywhere buffered input can still skip a prompt or transition
  - completed: simple yes/no helper confirmations now use the same stale-input guard as direct confirmation popups
  - completed: inn/church town popups and quest-manager fallback popups now use guarded modal input consistently
  - completed: reward-selection popups now support stale-input guards
  - completed: shared modal popup release checks now route through one helper for confirmation, reward, quantity, and code-entry popups
  - completed: modal popup stale-input guards now use a reusable helper that supports both current-key-state and release-event arming
  - completed: level-up, stat-selection, loot, empty-chest, and unlock-key popups now share current-key-state guarded input behavior
  - completed: high-traffic top-level game, dungeon-menu, and character-menu notice popups now use guarded modal input
  - completed: reusable popup-menu selection loops and nested inventory action menus can wait for key release before accepting input
  - completed: nested equipment action menus can wait for key release before accepting input
  - completed: reusable popup-menu background providers are restored through a `finally` guard
  - completed: barracks leave messaging preserves its local background redraw while using guarded input
  - completed: reusable shop-screen option and item selectors now use the same stale-input guard
  - completed: top-level character-screen navigation now uses the same stale-input guard
  - completed: combat, shop, and character selectors now arm from current keyboard state as well as release events
  - completed: top-level menu/navigation screens now use current-key-state arming in addition to release events
  - completed: pygame main-menu Settings placeholder now uses the guarded modal popup path
  - completed: top-level pygame cleanup clears presenter background providers during shutdown
  - completed: presenter popup-background fallback clears broken or empty providers after fallback
  - completed: level-up popup helpers fall back to screen copies when providers return empty or live-screen surfaces
  - completed: confirmation popups fall back to screen copies when providers return empty or live-screen surfaces
  - completed: shared pygame confirmation/choice/reward/quantity/code-entry popups now use the same copied-surface fallback rule
  - standardize background-provider usage so popups inherit the correct view consistently
  - keep cached-view logic correct across resolution changes, area transitions, and combat entry/exit
  - remove duplicated or per-screen redraw logic where a shared approach is sufficient

Supporting tasks:

- add or update focused renderer / UI tests for each bug fixed during the polish pass
- remove or retire legacy pygame rendering code paths that are no longer intended to be used
- keep the roadmap statuses updated as items move from `Partial` to `Confirmed`

Definition of done for Phase 2:

- The pygame dungeon/town/combat loop is stable enough that Phase 1 is no longer dominated by UI regressions
- Known renderer edge cases have either been fixed or isolated with clear, limited follow-up scope
- Core UI interactions feel visually consistent across popups, menus, combat overlays, and dungeon exploration
- The remaining pygame work is mostly additive polish or feature expansion, not baseline stabilization

### Phase 3: Expand Confidence

Status: `Planned`

Goal:

- Improve confidence in correctness, maintainability, and future refactoring safety across combat, quests, saves, and UI-adjacent gameplay systems.

Primary workstreams:

- Broaden automated test coverage
  - expand ability-effect coverage across data-driven and remaining legacy abilities
  - add more status-interaction tests for multi-turn and edge-case behavior
  - improve save/load coverage, especially around mutable tile state, YAML abilities, and quest progress
  - add targeted quest-flow tests for reveal, completion, and reward transitions
  - add enemy-AI behavior tests where tactical decisions are important enough to regress
- Strengthen quality scaffolding
  - continue targeted type-hinting in large legacy files
  - add docstrings where behavior is subtle, stateful, or easy to misuse
  - reduce brittle test setup by leaning on shared harnesses where possible
  - improve serialization and fixture stability for systems that frequently change
- Use tooling for validation
  - use the combat simulator as a regression check before and after balance-sensitive changes
  - use smoke and scenario tests to guard the pygame dungeon renderer as it evolves
  - improve the developer workflow for targeted test runs and balance comparisons where helpful

Supporting tasks:

- update roadmap labels when areas move from “partially implemented” to “well covered”
- document persistent testing gaps that remain intentionally deferred
- keep flaky tests visible and tracked rather than silently skipped

Definition of done for Phase 3:

- The most failure-prone gameplay systems have direct automated coverage
- Major combat and quest regressions are more likely to be caught by tests than by manual play
- The codebase is easier to navigate and change because critical modules have better type information and clearer interfaces
- Future feature work can build on a more trustworthy regression safety net

### Phase 4: Resume Feature Expansion

Status: `Planned`

Goal:

- Resume content and system expansion from a stable foundation, using the improved core engine, test surface, and pygame UI as the default platform for new work.

Primary workstreams:

- Gameplay statistics
  - decide which stats are worth persisting permanently versus showing only for the current run
  - decide whether the current town-menu statistics popup needs history views beyond its current grouped sections
  - reuse existing tracked state where possible before adding new persistence fields
- Quest and realm expansion
  - prioritize unfinished or lightly implemented questlines and realm content
  - add or complete special-tile behaviors required by those questlines
  - ensure new quest content uses the stabilized popup, renderer, and save-state systems
- Equipment and progression systems
  - implement the next meaningful item/equipment upgrades only after their combat hooks are well defined
  - keep naming, modifiers, and item rules aligned with the data-driven direction of the project
  - use simulator-assisted validation for balance-sensitive equipment changes
- Audio and presentation content
  - replace placeholder sound assets with real effects
  - add actual music assets and map them to locations or encounter types
  - ensure audio integration remains graceful when content is missing or partially installed

Supporting tasks:

- keep new content accompanied by focused tests where the rules are stateful or easy to break
- document content dependencies clearly so quest/map/tile changes stay synchronized
- revisit roadmap priorities periodically as content work uncovers new systemic gaps

Definition of done for Phase 4:

- New content work is no longer blocked by foundational instability in combat, rendering, or save systems
- Statistics, quest expansion, equipment work, and audio content can progress in parallel without heavy rework
- The roadmap has shifted from recovery/stabilization mode into sustained feature development

---

## Working Principles

1. Fix before expanding. Resolve regressions and inconsistent behavior before adding more systems on top.
2. Keep UI thin. Game logic belongs in `src/core/`; UI layers should present, not own mechanics.
3. Prefer data-driven content. New abilities and content rules should go through the YAML / effect pipeline where possible.
4. Test what changes. New renderer, combat, and quest work should come with direct test coverage.
5. Treat this document as a living status file. If a section is complete, move it rather than leaving it buried in planned work.

---

## Improvements

Resolved:

- Increased the number of Old Keys given out for quest rewards

---

## Bug Fixes

Resolved:

- Jump now clears its forced-action state after the landing resolves, returning control instead of repeating the skill.
- Active Jump now resolves before Berserk can force a basic attack, preserving `Unstoppable` Jump behavior.
- Duration-1 incapacitation now still consumes the current combat turn before expiring, so stun/sleep no longer clear before skipping action.
- Character-screen submenu popups now use the stale-input/key-release guard used by other pygame modal overlays.
- Left-side side-corridor ladder ceilings now have mirrored renderer regression coverage for center ceiling slot routing.
- Jump no longer cancels when stun lands during the charge if the skill has `Unstoppable` active.
- Side-corridor outer wall doors now keep their door textures instead of collapsing into plain wall art, for both open and closed states.
- Shields unequip correctly when equipping a two-handed weapon through the pygame equipment popup and the core equip path.
- The combat turn indicator now stays hidden until initiative is known, instead of defaulting to the player's turn.
- Chest sprites now stay behind the blocking corner in the side-view depth=2 corridor case.
- Side-view chest sprites now render upright instead of being distorted by lateral floor projection.
- Charge/telegraph messages now wrap against both the main combat log and the narrower dungeon-combat overlay log pane.
- Combat enemy sprites failed to render for legacy `.txt` `enemy.picture` values. Sprite lookup now falls back to enemy-name PNG assets, uses cwd-independent asset paths, and has regression coverage for the dungeon-combat render path.
- The pygame Character Menu now displays weapon-adjusted attack via the same `check_mod("weapon")` path used by equipment previews and melee damage.
- The pygame Character Menu now displays armor-adjusted Defense via `check_mod("armor")`, matching equipment previews and damage reduction.

New follow-up items:

- Keep an eye on enemies with explicit `.png` form swaps so palette/form changes continue to invalidate the correct cached sprite.
