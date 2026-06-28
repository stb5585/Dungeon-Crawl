# The Forsaken Tenet Development Roadmap

*Updated: June 28, 2026*

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
  - `docs/PRESENTATION_ASSET_DESIGN_GATES.md` for presentation, generated
    bitmap, screen-polish, and visual-cue gates.
  - `docs/DUNGEON_WORLD_ENCOUNTER_DESIGN_GATES.md` for dungeon interaction,
    chest, random encounter, Cambion, relic, town-hint, and low-health
    navigation gates.
  - `docs/EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md` for shop polish, ultimate
    helmet acquisition, durability, identification, item modification, rarity,
    and economy gates.
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

Status: `Spec Gate`

`docs/PRESENTATION_ASSET_DESIGN_GATES.md` is the behavior reference for this
section. The first quick-win slice shipped visual Character Created and New Game
story-card screens plus reusable combat cues for reflection, hard-control hits,
and elemental weapon strikes.

Remaining follow-up after this V1 slice:

- Status-effect artwork remains opt-in; fallback initials remain valid where no
  approved PNG exists.
- Jump and Charge wind-up/impact visuals remain deferred until enemy sprite
  stance adjustments are planned.
- Warp Point artistic renderings need a generated-bitmap batch with review
  sheet/contact sheet before integration.
- Town NPC and venue renderings remain batch-gated until art direction,
  dimensions, and target list are selected.
- Enemy identity presentation still needs the rules/readability implementation
  for invisible reveal notes, special-form notes, and construct-friendly bleed
  flavor such as `Oil Leak` while preserving underlying mechanics.
- A public-facing website/project page remains deferred until the title and
  identity pass are stable enough to present externally.

## Dungeon, World, And Encounter Gates

Status: `Spec Map, V1 Quick Wins`

`docs/DUNGEON_WORLD_ENCOUNTER_DESIGN_GATES.md` is the durable reference for
dungeon interaction, chest policy, encounter bias, Realm of Cambion deferrals,
relic discovery text, town hint flavor, and low-health dungeon navigation
presentation. V1 quick wins formalize one-and-done chests, add relic-specific
discovery text, add a soft active-quest random-encounter nudge, and keep a
persistent low-health cue visible while navigating the dungeon.

## Equipment, Items, And Economy Gates

Status: `Spec Map, Shop Polish V1`

`docs/EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md` is the durable reference for
shop polish, ultimate helmet acquisition, durability/repair, item
identification, equipment actives, armor mobility, rarity semantics, dungeon
refreshers, Tome special effects, elemental armor/item modification, and
P6-adjacent item content. V1 prioritizes low-risk shop purchase/equip clarity
before save-heavy systems.

## Class, Ability, And Combat Gates

Status: `Spec Map, UI/Log Polish Next`

Class, ability, and combat planning is split across durable owner docs rather
than a single umbrella spec:

- `docs/CLASS_KIT_DESIGN_GATES.md` owns promotion kit behavior, V1 follow-up
  polish, deferred track expansions, and P6 class ability decision blocks.
- `docs/CLASS_RING_SYSTEM.md` owns Class Ring activation baselines and
  presentation/tuning follow-up.
- `docs/PROMOTION_ABILITY_RULES.md` owns promotion spell/skill retention rules
  and future transition-expansion requirements.
- `docs/COMBAT_BALANCE_DESIGN_GATES.md` owns combat semantics, balance-report
  gates, always-hit rules, Polearm Mastery gating, and deferred combat
  architecture.
- `docs/STORY_AND_ENDGAME_DESIGN.md` owns future Voluntas/class-identity story
  tie-ins.

First implementation priority after this spec map is UI/log readability polish
for class-kit meters, ring state, and combat messages. Mechanics and numeric
tuning should remain unchanged until playtest or simulator evidence promotes a
specific balance change.

## Story And Endgame Gates

Status: `Spec Map, New Game Intro Story Next`

`docs/STORY_AND_ENDGAME_DESIGN.md` is the durable reference for the implemented
Vesperion/Voluntas route, Liminal Gap, Guardian trials, Reflection/Psychopomp,
true-final completion, tavern epilogue, and deferred story polish gates. Future
work should deepen or polish that route rather than replace it unless a new
story spec explicitly changes the baseline.

First implementation priority after this spec map is New Game intro story copy
expansion using the story-card presentation owned by
`docs/PRESENTATION_ASSET_DESIGN_GATES.md`. The intro should add setting,
premise, tone, and early stakes without revealing Vesperion, Voluntas, the
busboy twist, the Hooded Figure truth, or true-final route mechanics.

## Systems, Audio, And Meta Gates

Status: `Spec Map, Mouse Support V1 Next`

Systems, audio, and meta planning is split across durable owner docs:

- `docs/SOUND_SYSTEM.md` owns audio runtime, diagnostics, source-specific
  routing, final asset replacement gates, and future audio enhancements.
- `docs/EVENT_EMISSIONS.md` owns event payload enrichment rules and
  consumer-driven event policy.
- `docs/COMBAT_BALANCE_DESIGN_GATES.md` owns balance-suite tooling notes and
  numeric combat tuning gates.

Account-wide Bestiary history, Bestiary rewards, achievements, titles,
gameplay bonuses, run summaries, and persistent statistics remain deferred
until profile storage, migration rules, privacy/scope decisions, and old-save
behavior are specified. Current per-save Bestiary behavior and reveal layering
remain the baseline: seen identity, defeated practical info, and detailed
mechanics only after combat detail visibility was earned.

First implementation priority after this spec map is Mouse Support V1: finish
mouse-click parity for NPC conversation progression, quest boxes, Accept Bounty
selection, Active Bounties, and remaining popup-menu flows. Use existing
`mouse_helpers`, popup menu, and choice/confirmation popup patterns; do not
alter quest state, bounty generation, save data, audio routing, keyboard
behavior, or gameplay rules.

## Bugfixes

- The dungeon loading screen comes before the popup "You are teleported back
  to town.", resulting in a jumpy transition between dungeon and town view.

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
