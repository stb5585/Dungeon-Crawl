# The Forsaken Tenet Development Roadmap

*Updated: June 27, 2026*

This roadmap tracks remaining work for **The Forsaken Tenet**. Completed P0-P6
roadmap history has been consolidated into `CHANGELOG.md`; this file is now
forward-looking and should stay focused on active, deferred, or decision-gated
work.

Some legacy module names, archived docs, repository paths, and compatibility
aliases may still refer to the earlier Dungeon Crawl working title.

## Planning Model

- `Active`: ready to work next after normal code/data inspection.
- `Ready`: scoped enough to implement, but not the top priority.
- `Spec Gate`: requires a one-page implementation decision before code changes.
- `Decision Gate`: requires product, balance, story, or art direction first.
- `Deferred`: intentionally postponed until a dependency, spec, or playtest
  signal exists.
- `Watch`: known risk to monitor while changing nearby systems.

Completed work belongs in `CHANGELOG.md`, not in this roadmap. If a loose idea
moves into implementation scope, add a small decision block here or in the
appropriate design-gate document before coding.

## Current Baseline

- Core game logic is split under `src/core/`; curses and pygame presentation
  layers live under `src/ui_curses/` and `src/ui_pygame/`.
- The shared BattleEngine, EventBus, data-driven abilities, diagnostics,
  gameplay statistics, save/load hardening, Bestiary, class-ring systems,
  Pygame dungeon/town/combat flows, selected-item artwork, enemy combat sprites,
  dungeon tile art, and non-asset audio routing are implemented.
- Recent class-mechanic follow-up shipped Weapon Master/Berserker/Grandmaster
  Weapon Discipline and weapon arts, the Sorcerer/Wizard 0-based School
  Affinity progression, the promotion ability transition decision matrix, and
  the V1 promotion class-kit track implementation.
- Current planning references:
  - `docs/CLASS_KIT_DESIGN_GATES.md` for promotion class-kit behavior and
    follow-up tuning gates.
  - `docs/COMBAT_BALANCE_DESIGN_GATES.md` for combat/balance gates.
  - `docs/STORY_AND_ENDGAME_DESIGN.md` for Vesperion, Voluntas, Liminal Gap,
    Reflection, and true-final story direction.
  - `docs/CLASS_RING_SYSTEM.md` for implemented class-ring activation
    behavior and follow-up tuning context.
  - `docs/PLAYTEST_CHECKLIST.md` for manual validation coverage.

## Active Priority - P7 Additional Improvements

Status: `Completed`

The P7 implementation for selector mouse support, reusable presenter/popup mouse
support, Equipment selected-slot visibility, dungeon location labels, enlarged
minimap modal, portrait-atlas variant browsing, generated dungeon special tiles,
generated familiar artwork, and Character Menu companion art has shipped and is
tracked in `CHANGELOG.md`. There is no remaining P7 Active Priority
implementation work.

Completed follow-up posture:

1. Watch for future selectable pygame overlays added during playtest and apply
   the same hover-to-select, left-click-to-confirm contract where appropriate.
2. Defer first-person town navigation until a later dedicated town-navigation
   pass.
   - The direct `--town-navigation` prototype path is optional; the town menu
     remains canonical and no longer exposes `Explore Town`.
   - The prototype now uses directional movement between town venues; do not
     replace the town menu until playtest feedback confirms the node graph,
     shortcuts, popup access, and pacing are worth promoting.
   - Future work needs town-specific first-person tiles/art, spatial layout
     decisions, travel distance/pacing rules, and interaction integration
     polish before promotion.
   - Decision: defer until core gameplay is complete, then re-evaluate need and
     scope.
3. Broader companion-management UI, summon action previews, and combat-side
   companion art remain deferred until playtest confirms the Character Menu
   presentation needs expansion.

## Presentation And Asset Gates

Status: `Decision Gate`

- Remaining status-effect artwork beyond the wired combat-state/stat-effect set
  is deferred; fallback initials remain valid where no PNG exists.
- Broader ability visuals are deferred until a batch is selected. Candidate
  reads include Reflect/Magic reflection flashes, Stun/Prone hit accents,
  elemental strike overlays, and other approved combat-state cues.
- Jump and Charge wind-up/impact visuals are deferred until enemy sprite stance
  adjustments are planned.
- Warp Point artistic renderings are deferred to a later presentation/art pass.
- Town NPC and venue renderings are deferred until art direction, target list,
  dimensions, and generation/review workflow are selected. Candidate targets
  include Sergeant/Barracks, inn patrons, shop purveyors, Church priest, Old
  Warehouse guards, staffed Warp Point scientists, and Bring Him Home
  family/child scenes.
- Enemy identity presentation needs a future decision pass for invisible enemy
  reveal rules, special-form notes, and construct-friendly bleed flavor such as
  `Oil Leak` while preserving underlying mechanics.
- A public-facing website/project page remains deferred until the title and
  identity pass are stable enough to present externally.
- Equipment art should appear on the Equip popup
- Screens to improve
  - Character Created screen is very basic, black with text
  - New Game story screens need more polish

## Dungeon, World, And Encounter Gates

Status: `Spec Gate`

- Decorative dungeon tiles are traversable visual/message hooks today. Future
  gameplay for harvesting roots/fungus/lichen, rubble destruction, crystal mana
  interactions, crystal projectiles, poison/fungus effects, and salvage from
  broken equipment needs a concrete dungeon-interaction spec before code work.
- Chest randomness and chest respawn behavior remain undecided.
- Luck/charisma bias for random encounters that satisfy active quest enemy
  needs remains undecided.
- Deeper Realm of Cambion rooms, events, rewards, special tiles, and encounters
  are deferred until a concrete content beat is chosen.
- Relic-specific discovery text should replace generic relic-found messaging in
  a future narrative/content pass.
- Sergeant/Barracks quest-lead hints, reactive tavern gameplay tips, and broader
  Barracks adventurer flavor are deferred until a town-content pass is selected.
- Improve minimap by including better tile indicators and make the player location
  stand out more by adding a blinking effect
- Low health effect should persist outside of combat when navigating the dungeon

## Equipment, Items, And Economy Gates

Status: `Spec Gate`

- Ultimate helmet acquisition remains outline-only. A dedicated spec must define
  quest triggers, reward selection, UI text, save flags, class/armor eligibility,
  and tests.
- Durability, repair, broken-item, shatter/loss rules, and any durability costs
  need a dedicated save/economy/combat/UI/test spec.
- Item identification remains deferred, including intelligence-based
  unidentified drop chance, identify scroll/shop access, inventory/shop/save
  behavior, and loot-display rules.
- Usable equipment/accessory active abilities are deferred; equipped items do
  not currently add active-use actions or durability costs.
- Armor speed and mobility penalties remain deferred; current weight and
  encumbrance behavior is unchanged.
- Rarity semantics need a future economy/item-design pass so shop appearance,
  drop chance, and generated item quality can be reasoned about separately.
- Random healing/mana refresher spots are deferred until dungeon interaction
  rules are clearer.
- Tome special effects remain a future item-balance pass so Tomes can compete
  better with Staves for some caster classes.
- Elemental armor options and item modification remain deferred until item
  identification, durability, and modification rules are specified.
- Additional P6-adjacent item content needs a one-page decision block covering
  catalog placement, rarity, shop/drop/crafting source, subtype, icon/render
  mapping, save compatibility, tests, and whether the item is inert reagent-only
  or actively usable.

## Class, Ability, And Combat Gates

Status: `Spec Gate`

- Major promotion class-kit V1 follow-up is now tuning and polish, not initial
  implementation. `docs/CLASS_KIT_DESIGN_GATES.md` remains the behavior
  reference for Demonologist corruption/bargain presentation, Shadowcaster
  Umbral Debt/Eclipse, Spellblade/Knight Enchanter, Summoner/Grand Summoner,
  Weapon Master/Berserker Bloodied Momentum, Paladin/Crusader Oath Conviction,
  Lancer/Dragoon Aerial Tempo, Sentinel/Stalwart Defender Resolve/Counterguard,
  Cleric/Templar Devotion Ward, Priest/Archbishop Prayer Benediction,
  Monk/Master Monk Ki/Dim Mak, Bard/Troubadour Repertoire/Crescendo,
  Druid/Lycan, Druid/Archdruid Aspect Harmony, Ranger/Beast Master companion
  bond, Shaman/Soulcatcher Totem Resonance, and the Footpad-track
  Fortune/Misfortune, Case Journal/Wayfinding, Death Mark/No-Trace Opener, and
  Stolen Charge/Arcane Larceny loops.
- Remaining class-kit follow-up after the V1 pass: expand bespoke per-ability
  riders where the compact V1 hooks are intentionally representative; improve
  UI/log surfacing for the new meters; and tune preservation/payoff values
  after playtest.
- Class Ring activation follow-up is limited to tuning, additional visual
  presentation, and playtest response unless a new spec changes the shipped
  activation flows. Radar-style Wizard affinity visualization is deferred; the
  current six affinity values remain readable text first.
- Class progression should eventually tie second-promotion identity, Class Ring
  activation, and major class-kit choices back to Voluntas as expressions of
  chosen selfhood. Story beats are deferred until a quest/content spec defines
  timing, text, flags, and optional/required status.
- Deep race-passive expansion remains deferred until the current always-on race
  identity pass has enough playtest feedback. The "7 sins / 7 virtues" ideas
  are design flavor unless promoted by spec.
- Monk/Master Monk now have the Ki/Dim Mak martial V1 loop and Master Monk-only
  `Ruyi Jingu Bang` ultimate-staff acquisition through the existing
  `Unobtainium` blacksmith flow. Combo chains, chained input timing, combo UI,
  longer progression, and legs/additional melee attacks with separate
  attack/crit/accuracy rules remain deferred.
- Bard/Troubadour now have the Repertoire/Crescendo music V1 loop. Broader
  Maestro-style progression, larger sheet-music economy expansion, and
  quest-locked composition remain deferred.
- Beast Master now has the companion bond/command V1 loop; broader monster
  taming, stables, companion visuals, and balance rules for stronger species
  remain deferred.
- Druid/Archdruid now have the Aspect Harmony V1 loop. New Grove questlines,
  catalyst economy expansion, and persistent post-attunement mastery remain
  deferred.
- Sentinel/Stalwart Defender now have the Resolve/Counterguard V1 loop. Broader
  party-tank threat rules and multi-target control remain deferred.
- Lancer/Dragoon now have the Aerial Tempo/Aerial Supremacy V1 loop. Broader
  Jump-system redesign, persistent Jump mastery, and extra Jump modification
  capacity remain deferred.
- Paladin/Crusader now have the Oath Conviction V1 loop. Multi-vow respecs,
  morality systems, and broader oath quest arcs remain deferred.
- Weapon Master/Berserker now have the Bloodied Momentum V1 loop. Forced
  berserk/loss-of-control and broader scar milestone trees remain deferred.
- Cleric/Templar now have the Devotion Ward V1 loop. Full divine economy
  redesign, relic quest expansion, and loot-centered Pious Bounty progression
  remain deferred.
- Priest/Archbishop now have the Prayer Benediction V1 loop. Full party-healer
  systems, morality gates, and resurrection economy redesign remain deferred.
- Thief/Rogue now have the Fortune/Misfortune and Loaded Dice V1 loop. Full
  loot-table redesign, persistent heist caches, and jackpot-forcing mechanics
  remain deferred.
- Inquisitor/Seeker now have the Case Journal/Revelation/Wayfinding V1 loop.
  Full quest pathing, guaranteed boss/trial escape, and loot-focused journal
  rewards remain deferred.
- Assassin/Ninja now have the Death Mark and No-Trace Opener V1 loop. Full
  stealth-system rewrites, persistent target marks, and unrestricted
  instant-death scaling remain deferred.
- Spell Stealer/Arcane Trickster now have the Stolen Charge and Arcane Larceny
  V1 loop. Broader stolen-spell mastery, free-scroll generation, and
  scroll-economy redesign remain deferred.
- `Transform4` is retired as a live Lycan Red Dragon reward. The legacy wrapper
  remains loadable for old saves/tests, while Lycan Red Dragon victories now
  set Dragon Essence state for the implemented transformed-only `Winged Pounce`
  action.
  `Frozen Armor` is implemented as a Sorcerer-line Ice mastery passive.
  `Eclipse` is now covered by the Shadowcaster Umbral Debt spec.
- Polearm Mastery exists as a future quest/item-unlock hook; do not wire it
  without a trigger, reward, UI, and balance decision.
- An always-hit flag for selected spells remains deferred until a combat spec
  defines resistance behavior, boss-immunity boundaries, UI text, and tests.
- Promotion ability transition expansion remains deferred for remaining
  promotion paths, spell/skill gain rules, class-specific retention variants,
  and any ability-history restoration mechanics.
- Diviner/Astromancer Foresight Threads and `Threaded Cast` are implemented
  while preserving the current per-save rune, spell-empowerment scope. Richer
  constellation presentation remains deferred to a dedicated UI/readability
  pass.
- Shaman/Soulcatcher Totem Resonance and `Totem Surge` are implemented while
  preserving the current communion, spellbook/Totem/Class Ring storage,
  nonlethal Soul Drain, and reduced Totem pulse-potency contracts.
- Additional P6 ability work needs a one-page spec covering trigger/class
  eligibility, storage/save migration, combat and out-of-combat behavior,
  UI/menu/status text, event/audio/logging needs, balance assumptions,
  regression tests, and manual playtest checks.
- Deferred ability/combat candidates from `docs/COMBAT_BALANCE_DESIGN_GATES.md`
  include spell/skill sorting, status-gated skill visibility, out-of-combat
  timed buffs/debuffs, Wind eject rewards, Absorb Essence, mana-percentage
  damage, Prismatic Rays, Throw, magic-stat success scaling, Monk/Master Monk
  bare-handed support, DnD-style dice rolls, charisma or alternate-stat
  experience, class/race-specific level scaling, Silence edge cases,
  Nightmare/flying land/takeoff behavior, status ticks after enemy defeat in
  future multi-actor flows, ignore-defense and shield/Reflect ordering,
  unlockable race/class/level strategy, difficulty tiers, multi-enemy combat,
  and speed-based combat stacks.
- Numeric tuning on Final Assault, Last Stand, Tame odds, Favored Enemy scaling,
  Rewind snapshot scope, resistance durations, one-use song strength,
  dark-spell pressure, Weapon Arts, School Affinity, and Bad Breath AI priority
  should wait for playtest or simulator reports.

## Story And Endgame Gates

Status: `Spec Gate`

- New Game intro story needs more information without giving away too much of
  the endgame storyline
- The Vesperion/Voluntas route is implemented as a story-first endgame. Future
  work should polish rather than replace that route unless a new story spec is
  written.
- Bespoke Guardian trial rooms, puzzles, combat variants, or mini-bosses remain
  deferred. Preserve the existing clue aggregation and Guardian-counter route
  when deepening individual trials.
- Deeper Reflection/Psychopomp behavior remains deferred, including stronger
  self-copy mechanics and balance tuning beyond current martial/mystic/hybrid
  priority shifts.
- Final Vesperion polish remains deferred: phase tuning, bespoke relic-counter
  interactions beyond current `Choose Fate` and phase pressure, audio/visual
  presentation, and final battle balance.
- Broader Waitress/Joffrey/busboy town-route rewrites remain deferred. Preserve
  the human grief of the tragedy and the true-final reframing already defined in
  `docs/STORY_AND_ENDGAME_DESIGN.md`.
- Hooded Figure polish remains staged: the current route reveals the wounded
  Liminal guide and surviving Witness of Voluntas, while any post-Reflection
  angelic confirmation or personal angelic name is deferred.
- Legacy Devil compatibility retirement remains deferred. The old Devil class
  and related tests stay valid until a dedicated cleanup intentionally retires
  that compatibility surface; Balor owns the old demonic visual direction.

## Systems, Audio, And Meta Gates

Status: `Deferred`

- Account-style persistent Bestiary history, Bestiary rewards, achievements,
  titles, gameplay bonuses, run summaries, and persistent statistics history are
  deferred until profile storage, migration, and scope/privacy rules are
  specified.
- Additional source-specific SFX routing beyond the current laser and bird
  routes is deferred until event payloads or creature-specific hooks are clear
  enough to avoid brittle name guesses.
- Final SFX replacement and final music for menu, town, shops, Church, inn,
  dungeon, normal combat, boss combat, and final combat are deferred to an
  asset-content pass.
- Audio-system enhancements such as spatial audio, dynamic combat-intensity
  music, sound-effect randomization, audio ducking, sound profiles, and
  per-entity sound customization remain deferred until an audio-content or
  settings pass promotes them.
- Event payload enrichment should continue only when a concrete UI, audio,
  diagnostics, analytics, or tooling consumer needs it.
- `tools/run_balance_suite.py --help` has a known argparse help-string issue
  involving an unescaped `%`. Treat it as tooling cleanup, not a gameplay
  balance issue.
- Combat/balance numeric changes should wait for simulator reports generated
  from the canonical commands in `docs/COMBAT_BALANCE_DESIGN_GATES.md` and
  checked against playtest findings.
- Mouse click additions for full support
  - NPC conversation progression (e.g. quest boxes)
  - Accept Bounty selection and Active Bounties screen
  - Most/all popup menus (e.g. Equipment Selection popup)

## Bugfixes

- When standing on an Stairs Up tile after taking a Stairs Down, the missing
  ceiling tile that is supposed to be above the stairs is above the space in
  front of the character view
- Health potions should have a minimum amount healed, then scale up by
  percentage

## Watch Items

- Keep checking guarded input after unusual transitions, especially paths that
  clear events before entering a selection loop.
- Watch enemies with explicit `.png` form swaps so palette/form changes keep
  invalidating the correct cached sprite.
- Preserve current Bestiary reveal layering: seen identity, defeated practical
  info, and detailed mechanics only when combat detail visibility was earned.
- Preserve current audio-theme behavior: repeated theme requests should not
  restart the active track unless forced, and combat should restore the previous
  non-combat theme.

## Working Principles

1. Fix before expanding. Resolve regressions and inconsistent behavior before
   adding more systems on top.
2. Keep UI thin. Game logic belongs in `src/core/`; UI layers should present,
   not own mechanics.
3. Prefer data-driven content. New abilities and content rules should go through
   the YAML/effect pipeline where practical.
4. Test what changes. Renderer, combat, quest, save, and input changes should
   have direct focused coverage.
5. Keep the roadmap current. Completed work should move to `CHANGELOG.md`, and
   loose ideas should be promoted behind a clear gate before implementation.
