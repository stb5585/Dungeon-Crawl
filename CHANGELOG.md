# The Forsaken Tenet - Changelog

## [Unreleased] - 2026-06-26

### Design Gate Spec Maps

- Added durable Presentation/Asset, Dungeon/World/Encounter, and
  Equipment/Items/Economy design-gate docs, then converted the matching roadmap
  sections into compact status summaries.
- Moved Class/Ability/Combat, Story/Endgame, and Systems/Audio/Meta gates into
  their existing owner docs while keeping the roadmap as the index of next
  implementation slices.
- Updated documentation indexes so current gate docs are discoverable from the
  project README and docs README.

### Presentation And Asset Gates

- Added `docs/PRESENTATION_ASSET_DESIGN_GATES.md` as the durable spec map for
  presentation, generated bitmap, visual-cue, and screen-polish gates.
- Replaced the plain pygame Character Created popup with a visual summary screen
  and moved New Game intro text into reusable story-card pages.
- Added reusable combat impact cues for reflected damage, hard-control hits,
  and elemental weapon strikes.

### Roadmap Polish And Bugfixes

- Fixed pygame character naming so printable `m` and `f` key presses enter the
  name field instead of being swallowed by sex-selection shortcuts.
- Fixed the stairs-up ceiling-void placement so the missing ceiling tile stays
  above the current stairs rather than the space in front of the player.
- Added tiered minimum floors to health potion healing before percent scaling,
  preserving combat caps while making low-HP pools receive useful healing.
- Added selected equipment artwork to the pygame Equip popup details pane.
- Suppressed unchanged resistance rows in equipment diffs and moved the
  teleport-to-town popup before the return loading screen.
- Cleaned up shop quantity confirmation, keyboard Cancel selection, Equip Now
  prompt wrapping, and the final dungeon-frame flash on return to town.
- Improved minimap readability with outlined special-tile indicators and a
  blinking player-position marker.
- Fixed data-driven stealth-skill regressions so Kidney Punch costs exactly
  18 MP, mana/resource pools cannot underflow, and Backstab only works against
  incapacitated targets.
- Surfaced Footpad Evasive Guard stacks in pygame status icons and Combat Focus,
  and changed undetailed boss Bestiary entries so they no longer suggest Vision
  can reveal boss details.
- Fixed roadmap bugfix queue items for Smoke Screen flee visuals, promoted
  highest-level statistics, long character-screen locations, and status
  consumables missing from pygame shops.
- Improved contained pygame flows for bounty acceptance, incapacitated turn
  indicators, flying enemy placement, minimap adjacent visibility, enemy
  Shapeshift follow-up actions, and dual-wield shop comparison text.
- Fixed additional playtest polish around state-gated skill menu visibility,
  fake-wall wall overlays, non-enterable minimap review tiles, Evasive Guard
  dodge falloff, dead-body dungeon placement, and the Bad Dream Lucky Locket
  turn-in handoff.
- Fixed Demon Claw Doom feedback, PyGame bounty abandonment parity, softer
  quest encounter bias including enemy-drop collection quests, movement log
  coordinate spam, and Thief/Rogue Fortune/Misfortune combat focus behavior.
- Fixed flying target Earth interactions so flying no longer grants blanket
  Earth immunity; only ground-contact spells such as `Tremor`, `Mudslide`, and
  `Earthquake` fail to damage flying targets, while `Sandstorm` and Earth
  elemental damage can still connect.
- Implemented remaining contained roadmap improvements for PyGame death parity,
  Rookie Mistake body drop/recovery, promotion equipment cleanup, menu cursor
  policy coverage, save-preview portraits, Mad Waitress dungeon cue/SFX hooks,
  and the Minotaur approach bone pile; added measurement targets for deferred
  Footpad, drop-rate, multi-strike, and Enfeeble tuning.
- Finished the Mouse Support V1 shared-layer pass for pygame NPC/quest text,
  bounty/content selection lists, read-only item boxes, and reusable popup-menu
  row hover/click/wheel behavior.
- Shipped pygame Shop Polish V1 buy/equip clarity with replacement previews,
  stat/no-stat comparison lines, dual-wield copy guidance, and inventory-safe
  cancel/failure handling.
- Closed Dungeon Quick Wins V1 with regression coverage for one-and-done
  chests, relic-specific discovery text, soft active-quest encounter bias, and
  the persistent pygame low-health dungeon cue.
- Expanded relic discovery text into shared core handling so pygame and
  core/curses relic-room interactions use the same relic-specific copy and
  generic fallback.
- Shipped Enemy Identity Presentation V1 with Sight-gated invisible target
  notes, Mad Waitress form-change readability, and construct-facing `Oil Leak`
  wording while keeping canonical `Bleed` mechanics unchanged.
- Added the remaining-improvement balance baseline wrapper, dry-run summary
  coverage, and ignored timestamped report outputs so Footpad, drop-rate,
  multi-strike, and Enfeeble tuning remain evidence-gated.
- Remade the Quasit combat sprite and added active/inactive Warp Point dungeon
  art with review sheets and fallback-preserving renderer coverage.
- Added saved, progress-gated bounty-board restocks so completed boards refill
  intermittently after enough steps, enemy defeats, or a level gain instead of
  refreshing immediately.
- Fixed empty pygame bounty-board prompts so the “No new bounties” popup redraws
  over the Bounty Board submenu instead of the main tavern menu.
- Fixed Invisible Stalker combat presentation so it does not draw the generic
  fallback body when the player lacks Vision or another sight source.
- Added compact combat indicators for Vision/sight and Weapon Art states such
  as Reaver's Mark, Brace, and Riposte Line.
- Improved Weapon Discipline presentation with required-weapon text in Weapon
  Art descriptions, selectable/clickable discipline rows, detail popups, and
  cleaner class-tab rows that no longer duplicate art names under weapon types.
- Expanded pygame promotion-preview mechanic tabs for Pathfinder branches so
  Diviner, Shaman, and Ranger previews announce their Runes, Totems, and
  Companion class tabs.
- Wired Warrior-line promotion mechanic tabs so Paladin/Crusader, Lancer/Dragoon,
  and Sentinel/Stalwart Defender previews and Character Menu tabs announce Oath
  Conviction, Aerial Tempo, and Resolve.
- Replaced the pygame Paladin vow picker with a styled selection popup that
  previews each vow's signature skill, aura, mark, and broad playstyle identity
  before a terse final oath confirmation without exposing tuning details.
- Moved pygame Lancer/Dragoon Jump Mods management inline into the `Aerial
  Tempo` Character Menu tab, expanded `Oath Conviction` vow details, and rebuilt
  Sentinel/Stalwart `Resolve` around a large red meter with ability boxes.
- Added Sentinel/Stalwart `Resolve` class-tab spend and Surge listings and
  captured future Paladin vow drift/oathless recovery as a design gate instead
  of loose roadmap notes.
- Rendered Sentinel/Stalwart `Resolve` in Combat Focus as a red value bar and
  kept active Defend from displaying as a Defense-down combat status icon.
- Implemented the Sentinel/Stalwart Resolve direction so Sentinel owns normal
  Resolve spending, Stalwart Defender inherits those shield actions, and
  Stalwart adds full-bar `Resolve Surges`.
- Split Sentinel/Stalwart Resolve actions into their own pygame combat menu
  with Resolve-cost labels, and reworked the low-cost shield control action as
  `Shield Check` so it no longer overlaps `Shield Slam`.
- Wired Mage-tree promotion mechanic tabs so Sorcerer/Wizard, Warlock,
  Shadowcaster, Demonologist, Spellblade/Knight Enchanter, and Summoner/Grand
  Summoner previews and Character Menu tabs announce School Affinity, Familiar,
  Umbral Debt, Contracts, Blade Charge, Arcane Tempo, and Summons.
- Wired Footpad-tree promotion mechanic tabs so Thief/Rogue, Inquisitor/Seeker,
  Assassin/Ninja, and Spell Stealer/Arcane Trickster previews and Character
  Menu tabs announce Fortune, Case Journal, Death Mark, and Stolen Charge.
- Wired Healer-tree promotion mechanic tabs so Cleric/Templar, Monk/Master
  Monk, Priest/Archbishop, and Bard/Troubadour previews and Character Menu tabs
  announce Devotion, Ki, Prayer, and Crescendo.

### Promotion Class Kits

- Implemented the V1 promotion class-kit track pass, including shared
  promotion-kit state/hooks, combat-only meters, persistent track state,
  representative active/passive abilities, class-ring identity updates, and
  save/load normalization for the second-promotion class loops.
- Added regression coverage for promotion-kit state, representative actives,
  Demonologist corruption/patron mood, Shadowcaster Eclipse, summon and
  companion bond state, Footpad-track meters, Lycan control, and ring display
  compatibility.
- Added the Master Monk-only `Ruyi Jingu Bang` ultimate staff, class-specific
  ultimate-staff selection, and curses/pygame blacksmith coverage for the
  `Unobtainium` crafting flow.
- Expanded Weapon Master/Berserker/Grandmaster Weapon Discipline into a
  player-facing progression loop with weapon-type ranks, active Weapon Arts,
  whole-XP insight rolls, INT-scaled insight chance, enemy-promotion difficulty
  gating, combat/victory/rank-up messaging, and pygame Character Menu progress
  bars with weapon icons and equipped highlighting.
- Redesigned the pygame promotion preview to show class transitions,
  promotion stat deltas, and post-promotion Character Menu mechanic tabs;
  pygame promotion now applies class stat/resource/combat bonuses, increases
  current HP/MP alongside max HP/MP bonuses, and shows one concise
  congratulations popup without extra tutorial popups.
- Tuned Weapon Master and Grandmaster of Arms promotion stat bonuses to include
  `+1 INT`, reinforcing Intelligence as martial study and Weapon Discipline
  insight rather than only spellcasting.
- Completed additional promotion-kit smoothing hooks for `Loaded Dice`,
  `Ordered Blessings`, `Divine Intervention`, `Encore`, and bond-scaling
  `Shared Recovery`, including representative Rogue Fortune/Misfortune payoff,
  `Cheat Death`, and Bard/Troubadour Crescendo coda coverage.
- Updated class-kit, class-ring, roadmap, and docs-index references to mark the
  V1 implementation as shipped while keeping deeper ability-specific riders,
  richer UI/log surfacing, and balance/playtest tuning as follow-up work.

### P7 Additional Improvements

- Added mouse hover/click support for selector-style pygame screens: main menu,
  town menu, shop selection, generic location menus, race/class selection,
  Character Menu tabs/actions, and equipment paper-doll slots.
- Improved Equipment tab selected-slot visibility with a fixed-size high-contrast
  highlight that does not resize or shift the paper-doll layout.
- Added live dungeon HUD location labels for Town, ordinary dungeon levels,
  Realm of Cambion, and Liminal Gap.
- Added an enlarged dungeon minimap modal opened with `M` or by clicking the
  existing minimap; it reuses current minimap discovery/reveal rules and closes
  with `M`, `Esc`, or outside click.
- Added an optional first-person-style `Explore Town` prototype that navigates a
  small Silvana node graph and routes interactions back through the existing
  Barracks, Shops, Tavern, Church, Old Warehouse, Warp Point, and dungeon-entry
  flows.
- Revised the `Explore Town` prototype from a menu-like selector into a
  directional town walk: arrow keys/WASD move between venues and Enter/Space
  interacts with the current venue.
- Updated the enlarged dungeon minimap modal to frame all currently revealed
  tiles on the active level instead of enlarging only the local HUD viewport.
- Added numbered portrait-atlas variant support for character creation. The
  creation screen starts on a random portrait variant, lets players browse with
  arrows/clickable portrait buttons, and persists the chosen variant for later
  Character Menu and player-token rendering.
- Hardened save loading so missing core equipment slots are backfilled with
  empty equipment, preventing legacy or synthetic saves without `OffHand` from
  crashing Character Menu resistance calculations.
- Replaced the base racial portrait source with per-race portrait sheets,
  providing five male and five female selectable base portraits per race.
- Folded sex selection into the character naming screen so character creation
  skips the old standalone sex page; Male/Female buttons below the portrait now
  switch the race-specific portrait set before confirmation.
- Extended mouse support to load-game save rows, promotion choices, the
  level-up stat picker, the main combat action grid, and core in-combat
  item/spell/skill/totem picker panels.
- Replaced the dungeon special-tile artwork for stairs up, stairs down, and the
  secret shop with new painterly RGBA sprites matched to the current dungeon
  wall/floor/ceiling treatment.
- Added generated companion/familiar artwork for Homunculus, Fairy, Mephit, and
  Jinkin, plus a companion art manager that uses those assets first and falls
  back to existing enemy sprites for tamed beasts and summons.
- Added bespoke transparent companion-art sprites for all 11 summon creatures
  and a summon companion-art review sheet; summon mappings now resolve to those
  assets before enemy fallback lookup.
- Moved companion/summon artwork out of Class tab tiles and into a
  Character-tab-style companion details popup with identity, attributes, combat
  stats, abilities, weaknesses, and resistances.
- Changed the Class tab companion/summon overview from a square grid to stacked
  full-width rows that fit the complete 11-summon roster.
- Moved active-summon HP, MP, level, and XP presentation into the pygame Combat
  Focus panel.
- Added active-summon `Support`, level-span-based summon bond rolls, explicit
  summon starting combat stats, Dilong `Surface`, Class-tab summon selection via
  `C`, Combat Focus summon-bond cleanup, and faster pygame combat entry pacing;
  `C` no longer jumps to the Class tab from other Character Menu tabs.
- Removed passive `Class` and known-`Summons` summary rows from pygame Combat
  Focus; the panel now shows active focus content, active summon resources, or a
  quiet no-focus message.
- Changed dungeon special-location text in pygame from a scrolling combat/log
  line into a popup message so one-off location events remain visible.
- Fixed Dragon Breath damage so it routes through Mana Shield before applying
  elemental reduction and HP loss.
- Kept summon level-up combat stat gains as integers so details popups no
  longer show fractional Attack/Defense/Magic/Magic Defense values.
- Cached bestiary location/drop hint rows inside the pygame Bestiary popup to
  reduce repeated redraw work while browsing enemy entries.
- Fixed the pygame equipment replacement popup so slot selection no longer
  flashes the full equipment-slot list before the filtered replacement list.
- Added summon calling costs, including MP for summon creatures and an
  additional gold fee for Kobalos.
- Added active-summon combat log coloring, active summon status icons in Combat
  Focus, boss-victory guaranteed/doubled summon bond gain, and a Dilong starting
  Attack bump for better low/mid-level hit payoff.
- Removed the deferred `Explore Town` prototype entry from the normal town menu
  while keeping the direct prototype launcher available for later work.
- Reworked the stairs-down dungeon tile as a floor-bound stairwell overlay
  instead of a wall-filling shaft, with renderer placement that sits it on the
  projected floor tile and sizes it from floor-slot width rather than shallow
  floor-slot height, plus a flatter, tapered perspective so it reads as
  descending into the floor without rising up the back wall.
- Shortened and darkened the stairs-up dungeon tile so the arch sits lower and
  the stone color better matches the surrounding dungeon walls.
- Reworked the stairs-up tile experiment to remove the custom dark upper
  opening, lower the top of the visible staircase below the ceiling plane, and
  color-match the stone more closely to the stairs-down tile while preserving
  normal wall/ceiling rendering.
- Adjusted center stairs-up rendering so the visible staircase spans from the
  floor edge into the ceiling opening at its projected depth, with a wider
  centered target, upward darkening gradient, and a generated `ceiling_void`
  slot that removes the center ceiling tile while leaving void visible above
  the stair top.
- Expanded pygame mouse support across reusable presenter menus and shared popup
  flows, including list/grid/split menus, confirmations, choice lists, reward
  selection, quantity selection, and code entry.
- Added mouse hover/click support for remaining named combat pickers: Runic
  Boost, Steal As Well, and Demonologist Ask Fiend contract intent selection.
- Wired companion/familiar artwork into the Character Menu combat-stats panel,
  preferring the active familiar and falling back to the first living summon
  without changing companion mechanics or save data.

### Roadmap Completion Consolidation

This entry consolidates completed roadmap work from `docs/DEVELOPMENT_ROADMAP.md`
and completed roadmap-sidecar notes, including the retired
`docs/P3_EFFECTS_AUDIT.md`. The active roadmap now tracks only current,
deferred, or decision-gated work.

#### P0 - Current Playtest Regressions And Trust
- Fixed the first-key combat input regression by pumping pygame events before
  guarded physical-key reads.
- Re-ran focused playtest coverage for main-menu/dungeon music transitions,
  Character Menu Attack/Defense display, Enfeeble zero-value reporting,
  Half Giant early balance, Old Key prompts, audio diagnostics, and
  location/combat music routing.
- Recorded the P0 verification pass in roadmap and playtest docs.

#### P1 - Pygame UX Polish
- Completed the modern Character Menu acceptance pass: tabbed character and
  equipment views, portrait/identity presentation, wider stat panels,
  resistance/weakness grouping, paper-doll equipment layout, Helmet support,
  dual-wield Attack display, selected-item artwork, item detail popups, and
  town/dungeon default routing.
- Replaced shop sub-type selection with tabbed buy-list browsing for town shops
  and secret-shop grouped categories.
- Added combat visual polish: procedural hit/spell/skill overlays, floating
  damage/healing text, enemy recoil, low-HP danger vignette, compact bottom
  command panels, paged wrapped combat logs, compact enemy telegraph warnings,
  boss-detail suppression, and improved Defend presentation.
- Replaced the basic pygame naming prompt with a visual naming screen showing
  portrait, sex, race, and class.
- Reworked enemy presentation around approved transparent combat sprites,
  compact tokens, per-enemy scale data, target-panel rendering, and boss
  navigation figures.
- Completed large selected-item artwork coverage for regular, key, and special
  inventory presentation contexts.
- Completed the dungeon rendering art pass: manifest-driven texture loading,
  painterly projected dungeon textures, decorative tile hooks, deterministic
  torch/sconce overlays, richer Tiled JSON layer handling, chunked/infinite map
  support, funhouse boundary-wall rendering, and authoring-tile stability.

#### P2 - Renderer And Exploration Presentation
- Preserved and expanded structural-depth renderer coverage for center walls,
  side corridors, floor/ceiling/wall slot routing, side doors, Ore Vault door
  states, defeated-boss visuals, springs, chests, and side-special placement.
- Added floor-bound presentation for Rotator and active FunhouseTeleporter
  tiles.
- Added visited-only FakeWall/Fake Path translucent wall presentation without
  revealing hidden fake walls.
- Smoothed the pygame load progress popup with time-based interpolation while
  preserving the existing load flow and test hooks.

#### P3 - Core Refactoring And Test Confidence
- Completed the effects audit previously tracked in `docs/P3_EFFECTS_AUDIT.md`.
- Updated stale primitive effect contracts, including `DamageEffect`,
  `HealEffect`, result bucket writes, and type-only imports.
- Added result-shape and lifecycle coverage for data-driven spells, weapon
  skills, legacy `Spell`/`Skill` instances, passive placeholder power-ups, and
  all built-in YAML ability files.
- Aligned Stun, Silence, Poison, burn DOT, Bleed, Regen, Mana Shield,
  Crusader shield, reflected spell, Fire/Ice legacy-vs-YAML, healing, Smite,
  Sleep/Prone, enemy priority, enemy item, random enemy override, forced enemy
  debug, quest completion, class progression, loot helper, enemy catalog, and
  character defense contracts with current runtime behavior.
- Added targeted typed signatures/docstrings around player quests, class
  promotion rules, legacy ability entry points, item use overrides,
  data-driven spell wrappers, enemy helpers, loot helpers, and core character
  state aliases.
- Audited explicit `pytest.mark.skip` / `xfail` usage in the focused test tree
  and found no remaining P3 blockers.
- Deferred final passive Power Up gameplay effects, item TODOs, content
  expansion placeholders, and future helper extraction to later evidence-backed
  specs.

#### P4 - Content And Systems Expansion
- Completed P4a immediate content and UX polish: town/tavern/Sergeant/Warp
  Point hints, equipment hand details, inventory sort persistence, combat-log
  color improvements, Smoke Screen tuning and visuals, status icon artwork,
  load popup lifecycle fixes, Vision suppression for bosses/Waitress, enemy
  HP/MP labels when details are visible, and limited ability-specific visuals.
- Completed P4b quest and realm scope: Rookie Mistake polish, Realm of Cambion
  portal/rotator/anti-magic/Merzhin flow, Cambion flavor and reactions, town
  presentation hooks, Bring Him Home follow-up, Dragoon dragon route, class
  ring activation systems, legacy class-kit hooks, Vesperion/Voluntas plot
  direction, Liminal Gap hub and Guardian trial shells, clue aggregation,
  Seventh Seat/Voluntas/Acolyte/Reflection route, true-final re-entry,
  Guardian counters, true-final victory resolution, ending, and tavern
  epilogue.
- Completed P4c Bestiary scope: per-save seen/defeated/detailed records,
  Character Menu Bestiary UI, detail visibility rules, stable practical enemy
  details, completion counts, coarse encounter locations, and broad drop
  labels.
- Completed P4d lightweight equipment foundation: shared slot/eligibility
  helpers, buy-to-equip flows for pygame and curses shops, multi-copy/dual-wield
  handling, current item foundation validation, and stat-themed display-name
  confirmation.
- Completed P4e class-mechanics foundation: Grandmaster disciplines, Demonologist
  contracts, Archdruid attunement, legacy Class Ring awakening flows, Paladin
  vows and Crusader affirmation, Dragoon dragon quest route, Astromancer rune
  foundation, Shaman/Soulcatcher Totem foundation, and related save/UI/test
  coverage.
- Completed P4f combat architecture and balance design-gate slice. No gameplay rules
  changed in that slice; future combat and tuning changes are gated by
  `docs/COMBAT_BALANCE_DESIGN_GATES.md`.

#### P5 - Audio Content Completion
- Completed the non-asset audio-routing and event-payload readiness slice:
  weapon/action metadata, `laser_beam.wav`, `bird_attack_sound.wav`, scroll cast
  routing, and potion/elixir recovery cues.
- Deferred final SFX and music replacement to the later asset-content pass.

#### P6 - Expand Enemies, Items, And Abilities
- Added `Giant` and `Owlbear` to the level 3/4 encounter catalog.
- Added `Helm of Rostam`, reshuffled the medium helmet progression, retained
  `Visored Sallet` for legacy compatibility, and added reagent items `Acorn`,
  `Vine Seed`, `Fungus Spore`, and `Hemlock Root`.
- Added approved combat/item artwork and sprite/icon/render mappings for the
  new enemies, helmet, and reagents.
- Added passive entries and first-pass hooks for `Zephyrstrike`, `Retaliate`,
  `Defensive Regen`, `Posturing`, `Third Eye`, and `Pious Bounty`.
- Added Druid/Archdruid nature spells and straightforward data-driven spell
  entries for poison, lightning, stone, wind, growth, nature shield, and haste
  effects.
- Completed the current ability mechanics slice: Berserker and Dragoon martial
  abilities, Stalwart Defender and Monk/Master Monk strikes, Ranger `Tame` and
  `Favored Enemy`, Spell Stealer/Arcane Trickster theft follow-ups,
  Archdruid reagent/Growth abilities, Astromancer time spells,
  Seeker/Wizard movement and illusion spells, summon support, elemental
  resistance spells, advanced one-use sheet music, dark spells, enemy-only
  `Bad Breath`, and current second-promotion power-up hooks.

#### Resolved Roadmap Archive Cleanup
- Consolidated recent completed UI improvements that were previously parked in
  the roadmap archive: combat HUD class-focus panel, Totem combat presentation,
  additional PNG status icons, equipment resistance previews, Bestiary detail
  reveal and completion summaries, compact charge telegraphs, danger vignette,
  enlarged/re-anchored minimap, Alchemist/Jeweler tabbed buy flows, enemy combat
  sprite warmup, Old Key reward tuning, staged SFX routing, dungeon music
  aliasing, location/context music routing, and long shop-list paging.
- Consolidated recent completed bug fixes that were previously parked in the
  roadmap archive: torch/sconce overlay restoration, resistance preview context,
  Magic Pendant buff reporting, Bestiary lazy detail loading and Mimic artwork,
  Mirror Image duplicate interception, Mana Shield nonpositive-damage handling,
  Slot Machine logging, Regen Dispel, combat post-turn log flushing, combat-log
  wrapping cache, side-opening decorative prop grounding, Hex log coloring,
  action-menu refresh after Silence expiry, charged-skill resolution through
  Silence, Health Potion combat heal caps, Jester AI/storage/event ordering,
  Slot Machine DOT metadata/icons, generic DOT icons, Lick status filtering,
  town-return background cleanup, stale music cleanup, first-key guarded input,
  Jump forced-action cleanup, Berserk/Jump ordering, duration-1 incapacitation,
  equipment submenu input guards, unstoppable Jump behavior, side-door textures,
  two-handed shield unequip, initiative-hidden turn indicator, side-view chest
  orientation, charge log wrapping, enemy sprite fallback paths, Character Menu
  stat display, and zero-value Enfeeble filtering.

#### Consolidated Commit Messages
- `b086723` - Fix guarded input first-key handling
- `6194924` - Document completed P0 verification
- `51bba63` - Complete pygame character and item presentation pass
- `d46ceba` - Implement helmet equipment and standard character screen
- `e486c9a` - Complete combat polish pass
- `a08425e` - Finalize P1 dungeon rendering art
- `6d16c17` - Advance P2 renderer presentation polish
- `66fa9f1` - Close P2 renderer presentation pass
- `1bf7414` - Start P3 effects primitive cleanup
- `3f3af3a` - Add P3 ability result contracts
- `477d65d` - Expand P3 ability catalog coverage
- `6483f1e` - Cover status tick ordering
- `fc31792` - Share mana shield defense handling
- `18967e3` - Share instant heal application helper
- `348d681` - Close P3 roadmap work
- `a77fce6` - Organize P4 roadmap tracks
- `61180bc` - Complete P4a and polish Rookie Mistake
- `3d1895b` - Audit Realm of Cambion flow
- `08898aa` - Add P4b town presentation hooks
- `96edc4f` - Add Bring Him Home follow-up scene
- `22ff50e` - Add Bestiary MVP
- `424d33c` - Document Forsaken Tenet story direction
- `5778ea0` - Implement class ring activation systems
- `cb943c4` - Implement Paladin vows and Crusader ring affirmation
- `e20d843` - Implement Dragoon dragon quest route
- `3b36188` - Implement legacy class ring kits
- `8e8d1cf` - Close P4b quest and finale route
- `bcd17fd` - Close P4c bestiary scope
- `1f0172d` - Add P4d equipment foundation
- `f886726` - Implement P4e class mechanic foundations
- `7184a61` - Clean up roadmap and class kit docs
- `bd6f4d5` - Add P4f combat balance spec
- `3eaedf5` - Complete P5 non-asset audio routing
- `1487b5e` - Complete P6 content and ability mechanics

### Changed

#### Item Artwork Organization
- Organized large selected-item artwork into category subdirectories under `src/ui_pygame/assets/item_art/`.
- Replaced the old flat item-art render keys with nested `item_render_map.json` entries and kept optional legacy atlas fallback support.
- Preserved the Chalice Map split: selected-item art uses `item_art/special/story/chalice_map.png`, while the dungeon/location reveal uses `assets/key_items/chalice_map.png`.

#### Pygame Renderer and Combat UI Polish
- Improved combat status icon readability with urgent-effect prioritization, duplicate compaction, counted labels, Maelstrom Weapon stack visibility, stronger alert coloring, and shared helper behavior across the main combat view and dungeon-combat HUD.
- Tightened combat telegraph presentation with warning-colored wrapped log lines, a dedicated banner that tracks the full latest telegraph message, and clearing behavior after non-telegraph follow-up messages.
- Fit long combat selection labels and turn-indicator subtitles by rendered width so dense item/spell/skill names and long player/enemy names stay inside their UI surfaces.
- Hardened stale-input handling across Pygame popups and navigation loops, including town menus, class/race/load/shop selection, shared popup menus, dungeon escape/loot/key-use prompts, combat action/submenu selectors, shop screens, and the character screen.
- Expanded dungeon renderer smoke coverage around side-corridor walls, open/closed and hidden Ore Vault doors, side-door state preservation, depth-3 outer floor/ceiling slot routing, and left/right floor-special placement parity.

### Documentation
- Updated `docs/DEVELOPMENT_ROADMAP.md` with the completed Pygame polish items and current follow-up notes.

## [Unreleased] - 2026-02-22

### Added

#### Sound System (2026-02-22) 🔊
- **Complete sound manager with event-driven audio**
  - SoundManager class with pygame.mixer integration
  - Automatic pygame.mixer initialization (44.1kHz, 16-bit, stereo)
  - 16 simultaneous sound channels
  - Sound effect caching for performance
  - Graceful handling of missing audio files

- **Event-driven sound effects**
  - Combat sounds: hit, heavy_hit, critical_hit, victory, defeat, flee
  - Spell sounds: cast, fire, ice, lightning, heal, buff, debuff
  - Status effects: poison, stun, burn
  - Character events: heal, level_up, player_death, enemy_death
  - UI sounds: menu_select, menu_confirm, menu_cancel

- **Background music support**
  - Looping music with fade in/out transitions
  - Separate music directory structure
  - Designed for location-based and combat music

- **Volume controls**
  - Independent master, SFX, and music volume
  - Enable/disable sound system
  - Volume ranges from 0.0 to 1.0

- **Development tools**
  - `tools/generate_placeholder_sounds.py` - Creates simple beep sounds for testing
  - Generates 30+ sound effects as sine wave tones
  - Requires numpy and scipy for tone generation

- **Documentation**
  - `docs/SOUND_SYSTEM.md` - Comprehensive sound system guide
  - `assets/sounds/README.md` - Sound effects catalog
  - `assets/music/README.md` - Music tracks guide

#### Map and Sprite Tooling (2026-02-22)
- **Enemy sprites**: 42 new 32x32 enemy sprites for pygame UI
- **Tiled integration tools**
  - `tools/generate_tiled_tileset.py` - Creates Tiled .tsx tilesets
  - `tools/convert_maps_to_tiled_json.py` - Converts text maps to Tiled JSON
  - `tools/sprite_sheet_extractor.py` - Extracts sprites from sheets
  - `tools/sprite_merger.py` - Combines sprites into composite images

## [Unreleased] - 2026-01-28

### Major Reorganization - Code Structure Overhaul ✅

#### Codebase Reorganization
**Complete restructuring into modular architecture**:
- **src/core/** - All game logic modules (UI-agnostic)
  - Moved: abilities.py, battle.py, character.py, classes.py, combat_result.py
  - Moved: companions.py, enemies.py, items.py, map_tiles.py, player.py
  - Moved: races.py, save_system.py, town.py, tutorial.py
  - Kept: combat/ and events/ subdirectories

- **src/ui_curses/** - Terminal UI implementation
  - Moved: game.py, menus.py, town.py from root
  - Clean separation from game logic

- **src/ui_pygame/** - GUI implementation (Pygame)
  - Organized: gui/ directory with all pygame components
  - Created: presentation/pygame_presenter.py for event-driven UI

- **_old_code_archive/** - Archived original files
  - Git-ignored for safety during reorganization
  - Original file structure preserved

#### Import System Overhaul
**Fixed 20+ import errors across reorganized codebase**:
- **Core Modules**: Updated all imports to use relative imports (`from . import`, `from .. import`)
- **UI Modules**: Fixed cross-boundary imports (`from ..core import`, `from ...core import`)
- **Pygame GUI**: Corrected all relative import paths in gui/ subdirectories
- **Module-Level Imports**: Moved all local function imports to module level
- **Circular Dependencies**: Resolved with proper import structure

**Files Fixed** (20+ files):
- src/core/abilities.py (8 import fixes + 3 bugfixes for missing code)
- src/core/town.py (added enemies import)
- src/core/player.py (removed invalid utils import, fixed Mimic instantiation)
- src/core/classes.py (removed try/except fallbacks, added module imports)
- src/core/save_system.py (added enemies import, fixed indentation)
- src/ui_curses/town.py (added enemies import)
- src/ui_pygame/gui/combat_manager.py (fixed TYPE_CHECKING imports)
- src/ui_pygame/gui/enhanced_dungeon_renderer.py (added DIRECTIONS import)
- src/ui_pygame/gui/popup_menus.py (added module-level items import)
- And 10+ more files with import corrections

#### Code Quality Improvements
- **Syntax Errors Fixed**: 3 syntax errors from incomplete edits (abilities.py, save_system.py)
- **Indentation Fixed**: Corrected indentation errors in save_system.py
- **Missing Code Restored**: Added missing popup/result assignments in abilities.py
- **Dead Code Removed**: Eliminated unreachable pygame code in curses menus.py

#### Verification
- ✅ **Both UIs Working**: Terminal (curses) and GUI (pygame) both import successfully
- ✅ **Zero Import Errors**: Comprehensive grep search confirms no bad imports remain
- ✅ **All Tests Passing**: Import verification test passes for all critical modules
- ✅ **Entry Points Functional**: Both game_curses.py and game_pygame.py launch correctly

#### Developer Experience
- **Clearer Structure**: Logical separation of concerns (core vs UI)
- **Easier Navigation**: Files organized by purpose
- **Better Imports**: Consistent relative import patterns
- **Future-Proof**: Ready for additional UI implementations (web, mobile)

---

## [Phase 3 Started] - 2025-12-14

### Phase 3 Started - GUI Development with Pygame 🎮

#### Pygame Integration
- **Pygame 2.6.1 Installed**: Modern 2D graphics library for Python
- **PygamePresenter**: Complete presenter implementation with event subscriptions
- **Combat UI**: Character sprites, health/mana bars, status effects, turn display

#### Visual Features
- **Floating Damage Numbers**: Animated text showing damage/healing with color-coded types
- **Screen Shake**: Dynamic camera shake for critical hits and big damage
- **Combat Log**: Scrolling text log at bottom of screen
- **Telegraph Display**: Warning messages for charging abilities (Seeker/Inquisitor)
- **Status Icons**: Visual indicators for active status effects

#### Event Integration
- **COMBAT_START/END**: Initialize combat UI, display victory/defeat
- **DAMAGE_DEALT**: Create floating damage text with type-specific colors
- **HEALING_DONE**: Green floating text for healing
- **CRITICAL_HIT**: Enhanced visual feedback with extra screen shake
- **STATUS_APPLIED**: Add status to character display
- **TURN_START**: Update turn counter

#### Damage Type Colors
- Physical (White), Fire (Red), Ice (Light Blue), Lightning (Yellow)
- Poison (Green), Holy (Gold), Shadow/Arcane (Purple), Drain (Dark Red)

#### Next Steps
- Create sprite assets for characters and enemies
- Add spell effect animations
- Implement particle systems
- Create main menu and game over screens
- Add sound effects and music

---

### Phase 2 Complete - Enhanced Combat System ✅

#### Major Features Added
- **Action Queue System**: Turn-based combat with priority system (IMMEDIATE, HIGH, NORMAL, LOW, DELAYED)
- **Charging Abilities**: 18 abilities with charge times and telegraph messages for tactical gameplay
- **Event System**: 38 status effect events + combat events (damage, healing, dodge, block, critical hit)
- **YAML Ability System**: Externalized ability definitions for easier balance and modding

#### Combat Enhancements
- **Telegraph Messages**: Seeker/Inquisitor classes get foresight warnings about charging enemy abilities
- **Enhanced Battle Manager**: Full action queue integration with 117 enemy ability stacks
- **Status Effect Events**: All 38 status effects emit events with proper duration/source tracking
- **Damage/Healing Events**: Combat actions emit events for future GUI animations

#### Critical Fixes

##### Weapon Special Effects Re-enabled (Dec 14, 2025)
**Issue**: All weapon and armor special effects were disabled during CombatResultGroup API refactor
- 43 special effect methods completely non-functional
- Life steal, instant death, elemental damage, stun effects broken
- Leer/Gaze petrification attacks not working
- Armor thorns/reflection inactive

**Resolution**:
- **character.py** (lines 325-335, 508-540): Re-enabled special_effect calls with CombatResultGroup integration
- **combat_result.py** (lines 50-62): Made CombatResultGroup subscriptable (added `__getitem__`, `__len__`)
- **items.py** (line 1657): Fixed Gaze weapon missing result assignment
- **tests/test_weapon_special_effects.py**: Created comprehensive test suite (5/5 passing)

**Impact**: All weapon/armor special effects now operational - life steal, instant death, stun, elemental damage, petrification, thorns/reflection all working.

#### Project Configuration
- **pyproject.toml**: Modern Python packaging with PEP 621 standard
  - Dependencies: numpy, pyyaml
  - Dev dependencies: pytest, pytest-cov
  - GUI dependencies: pygame (for Phase 3)
  - Tool configs: pytest, black, mypy, isort, coverage
  - Entry point: `dungeon-crawl` command

#### YAML Ability Files Created (18 total)
**2-turn charge abilities**:
- meteor.yaml, dragon_breath.yaml, detonate.yaml

**1-turn charge abilities**:
- jump.yaml, charge.yaml, true_strike.yaml, true_piercing_strike.yaml
- ultima.yaml, disintegrate.yaml, dim_mak.yaml, arcane_blast.yaml
- shadow_strike.yaml, crushing_blow.yaml
- blessing.yaml, fireball.yaml

**Features**:
- Telegraph messages for foresight mechanics
- Special mechanics: prone_while_charging, unblockable, guaranteed_hit, ignore_defense
- Future: Cooldown system documented for Phase 3 implementation

#### Code Quality
- Removed unused imports (abilities.py - 4 effect imports)
- Fixed module conflicts (combat.py → battle.py)
- Added type hints with `from __future__ import annotations`
- Fixed mutable default arguments in dataclasses

#### Documentation
- **docs/PHASE_2.md**: Complete Phase 2 status and features
- **docs/ARCHITECTURE.md**: System architecture and design decisions
- **docs/PRE_PHASE_3_CLEANUP.md**: Pre-Phase 3 analysis and recommendations
- **data/abilities/README.md**: YAML ability system documentation
- **tests/**: Integration tests (6/6 passing), weapon special effects tests (5/5 passing)

#### Testing
- ✅ All modules import cleanly
- ✅ Enhanced combat manager integration (117/117 enemy stacks)
- ✅ Event system (38/38 status events + combat events)
- ✅ Weapon special effects (5/5 test suite passing)
- ✅ Action queue system functional
- ✅ YAML ability loader working

### Phase 3 Readiness 🟢

**Status**: Ready to proceed with GUI development

**What's Complete**:
- ✅ Event system for animations (38 status + 6 combat event types)
- ✅ Action queue for turn order display
- ✅ Combat mechanics fully functional
- ✅ Presentation interface ready for Pygame implementation
- ✅ Telegraph messages for UI display
- ✅ All special effects working

**Next Steps**:
1. Install Pygame: `pip install -e '.[gui]'`
2. Implement Pygame presenter in `presentation/pygame_presenter.py`
3. Create combat UI: sprites, health/mana bars, status icons
4. Add animations using event system
5. Implement telegraph message UI for Seeker/Inquisitor foresight

### Deferred to Phase 4+
- **Architecture Restructuring**: Current structure is functional, defer until after GUI stable
- **Companion Ultimate Attacks**: 9 missing (Carbuncle, Cait Sith, Chocobo, Imp, Moogle, Shiva, Sprite, Sylph, Tonberry)
- **Full YAML Migration**: 18/215 abilities done, complete remaining 197 in Phase 4
- **Quest System Expansion**: Basic system works, add more content later

---

## Format
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Types of changes
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities
