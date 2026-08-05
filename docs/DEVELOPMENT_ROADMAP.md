# The Forsaken Tenet Development Roadmap

*Updated: August 2, 2026*

This roadmap tracks remaining work for **The Forsaken Tenet**. Completed P0-P6
roadmap history has been consolidated into `CHANGELOG.md`; this file is now
forward-looking and should stay focused on active, deferred, or decision-gated
work.

Some legacy module names, archived docs, repository paths, and compatibility
aliases may still refer to the earlier Dungeon Crawl working title.

## Shipped - Flat Level and Authored Ability-Tree Progression

Player progression is one global level track from 1 through 100. New
characters begin with one permanent progression point, level 2 supplies the
second, and every even-numbered level thereafter supplies one more. New
primary-attribute points are a separate stored currency: every fourth global
level grants one, and they may be spent later from the Progression tab.
Progression points purchase tree nodes only; attribute points purchase
permanent `+1` primary-stat increases only. New
characters have no purchased nodes and no automatically learned progression
ability. The shared `src/core/progression.py` service owns XP
carryover, random growth, attribute training, ability/rating purchases,
promotion previews, branch closure, and class changes for Pygame and headless
validation.

Ability trees use class-authored specialization branches instead of universal
lanes. Base lineages lead to one terminal promotion per branch; promoted
classes only expose combat paths relevant to their catalogs. First promotions
cost two points and second promotions cost three; both are governed by path
prerequisites, permanent-stat gates, race eligibility, and global level 30/60
gates.
Learned abilities survive class changes; all unpurchased nodes in the prior
tree close. Church promotion and automatic level-based ability/stat awards
are retired. Progression is a Character Menu tab rather than a Town option.

Warrior was the first fully authored talent-tree prototype. Its ordered paths lead
through Arms to Weapon Master, Vanguard to Lancer, Bulwark to Sentinel, and
Command to Paladin. Weapon Master and Lancer share `Piercing Strike -> Charge
-> Weapon Focus` before splitting. Charge is level 5; Weapon Focus is level 10.
Weapon Master continues through `+10 Attack -> Cripple -> True Strike`, while
Lancer continues through `Driving Thrust -> +10 Defense -> Retaliate`.
Cripple is a level-20, less-accurate attack that weakens melee damage based on
damage dealt. The defensive spine is `Shield Slam -> Shield Block -> Rally`,
then Sentinel branches through Defense and
Paladin branches directly through Goad. Lancer joins Shield Block at
Retaliate. Cross-column connectors enter node sides instead of merging into
their vertical prerequisite lines. Disarm, Battle Cry, Adrenaline, Honed
Attack, Double Strike, and Parry are unbound talents in the fifth column.
Adrenaline is level 10, Honed Attack level 15, Double Strike level 20, and
Parry level 25; Battle Cry has no level gate. Weapon Master requires Strength
15, Dexterity 12, and Intelligence 11; Sentinel requires Constitution 16; and
Paladin requires Wisdom 13. Each first-promotion route costs 13 points from
the baseline Human Warrior under the former combined-budget accounting. With
separate currencies, Weapon Master/Sentinel/Paladin each cost eight progression
and five attribute points, while Lancer costs ten progression and three
attribute points. Warrior off-hand equipment remains shield-only;
Dual Wield is now an exclusive Weapon Master style. Combat-rating nodes grant
`+10` in base trees, `+20` in first-promotion trees, and `+30` in terminal
trees, while primary-attribute training remains `+1`.

Point distribution is transactional. Players may stage and remove tree nodes
or primary-attribute increments, inspect the remaining session budget, and
commit the entire distribution with one Spend action. Leaving with an
uncommitted distribution warns that those changes will be discarded, while
Reset clears it immediately. Spending a promotion first previews its class
description, one-time benefits, requirements, equipment conflicts, and branch
closure. One-time combat-rating bonuses use the promoted class's normal values
at `2x` for first promotions and `3x` for second promotions. The pygame tree
uses explicit top-to-bottom placement, semantic
ability icons, and prerequisite connectors without path headings or textual
availability labels.
The same declarative contract now covers all 49 class trees. Mage, Footpad,
Healer, and Pathfinder retain independent specialization roots, while every
promoted and terminal class uses named identity paths and class-kit talents
instead of generic four-lane rating padding. Exact branch ownership is recorded
in `docs/ABILITY_TREE_DESIGN.md`. Weapon Master is the first deliberately
asymmetric promoted tree: Berserker and Grandmaster routes use different node
types, Grandmaster forks permanently between Dual Wield and Duelist, and eight
independent weapon arts branch into rank-5 replacement upgrades instead of
being learned automatically. Its ungated inherited entry nodes and rating
nodes remain immediately available; the extended Berserker route adds
two-handed proficiency and discipline-scaled critical damage while keeping
both second-promotion nodes aligned.

The authored terminal follow-up replaces Berserker's generated talents with
Survival, Fury, and independent center columns plus eight centered two-handed
discipline arts. Its promotion-level entries are ungated, its stat development
uses `+30 Attack` and `+100 HP`, and Reckless Onslaught replaces Final Assault
with a stacking offensive tradeoff. Hemorrhage Thirst turns enemy bleed damage
into healing at the risk of a two-turn bloodlust crash. Grandmaster of Arms now
owns all three levels of every weapon art plus ungated Double Strike positioned
between two ungated, discipline-scaled mastery talents.

Lancer and Dragoon now use authored Aerial Tempo trees instead of generated
catalog lanes. Lancer places Jump in column 2 and Polearm Proficiency in column
5, with independent defensive-modifier, middle-stat/promotion, and
offensive-modifier Jump paths, a `Lance Sweep -> +50 HP -> Zephyrstrike`
polearm line, and unbound Parry/True Strike in the final column. The middle
path is `Jump -> +20 Defense -> +20 Attack -> Promote: Dragoon`; promotion
also requires level 60, `STR 17`, and `DEX 13`. Dragoon retains all 16 Lancer
development nodes with the same independent prerequisites, omits the promotion
node, and adds 11 mastery nodes, so promotion never prevents later Lancer
training. Shield Block is not repeated; ungated Polearm Excellence starts its
Dragoon line at row 5; True Piercing Strike no longer requires True Strike; and Dragon
Dive joins Dragon's Ascent, Soaring Strike, and the Unstoppable landing path.
Dragon's Ascent follows the middle `+20 Attack` without a redundant level gate;
Quake and Soaring Strike extend Rend; and Retribution extends Grounded Landing
rather than the `+30 Defense` node, which is gated by Dragon's Ascent. Acrobat
unlocks at level 40, Thrust at 45, Rend at 50, Retribution at 65, True Piercing
Strike and Unstoppable at 70, and Dragon Dive at 80. Lancer fits within rows
0-6; Dragoon uses compact spacing across rows 0-7 without scrolling.
Jump modifiers synchronize with progression without becoming spellbook
actions, while Recover, Dragon's Fury, Skyfall, the Kaelenon route, and
polearm-and-shield equipment remain externally owned. Combat-only Aerial Tempo
resolves once per weapon action, and awakened Aerial Supremacy supplies the
tuned Landing Shield rather than a duplicate Meteor Guard payoff.

Sentinel, Stalwart Defender, Paladin, and Crusader now complete the authored
Warrior promotion set. Sentinel uses compact Counter, Wall, and Anti-magic
columns and closes its leftovers when the level-60, `CON 20` Stalwart
promotion is purchased. Stalwart contains only 11 new nodes: Last Stand and
counter mastery, three Surge modifiers, and the Spell Reflection/Mirror
Bastion path. Resolve uses the legacy `guard_meter` field as one value with
caps 50/100, explicit Defend/block/physical-damage/Goad/Hold gains, and no
duplicate Class Ring accumulation. Spell Reflection spends 25 Resolve and
shares compatibility and cleanup rules across legacy and data-driven spells.
The Stalwart promotion grants all three Surge wrappers, while mastery 0/4/8
continues controlling their availability.

Paladin now begins with ungated Oath's Judgment and Oath's Shelter roots.
Judgment branches left through `Double Strike -> +20 Attack -> Tempered
Conviction -> True Strike` and right through `Smite -> Repel the Wicked -> +20
Magic -> Hallowed Ground`. Shelter branches through `Heal -> +50 MP -> Sworn
Purpose -> Blessed Light` and `Bless -> +20 Magic Defense -> +20 Defense ->
Divine Protection`; level-45 Resist Shadow now sits between `+50 MP` and Sworn
Purpose so the Grace path cannot be entered midway, while Magic Defense gates
Parry and the remaining protection chain.
The centered level-60 Crusader promotion requires either Oath root plus its
existing stats and three-point cost. It sits at `(2.5, 7)`, with each Oath
connector descending to its row before joining. Because attributes use their own
currency, a baseline Human retains 14 progression points and nine attribute
points after the shortest promotion route. Crusader contains 19 new nodes
across Melee, Spells, Healing, and Protection. Ungated Condemnation splits
into exclusive Two-Handed Weapon Proficiency and Sword & Board routes.
Repel the Wicked replaces Turn Undead in the Paladin path and remains
retained-or-purchasable in the Crusader Spells path without an upgrade node.
Signature-vow actions now
generate combat-only Conviction. Oath's
Judgment and Oath's Shelter explicitly spend all stacks for one of four vow
payloads; required Tempered Conviction produces effective caps 3/4. Righteous
Advance, Consecrated Bulwark, and awakened/equipped Vow Affirmation apply their
locked upgrade and one-preservation rules without changing permanent vows,
auras, marks, Church recovery, or equipment legality.

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

- Core game logic is split under `src/core/`; the supported presentation layer
  lives under `src/ui_pygame/`. The retired curses frontend is archived at
  `curses-ui-final`.
- The shared BattleEngine, EventBus, data-driven abilities, diagnostics,
  gameplay statistics, save/load hardening, Bestiary, class-ring systems,
  Pygame dungeon/town/combat flows, selected-item artwork, enemy combat sprites,
  dungeon tile art, and non-asset audio routing are implemented.
- Recent class-mechanic follow-up shipped Weapon Master/Berserker/Grandmaster
  Weapon Discipline and tree-purchased weapon arts, the `Weapon Discipline`
  Character Menu tab, pygame promotion preview/stat-delta education, INT-backed
  promotion stat tuning, the Sorcerer/Wizard 0-based School Affinity
  progression, the promotion ability transition decision matrix, and the V1
  promotion class-kit track implementation.
- Cleric now has a second level-3 fork: `Templar` remains the heavy shield
  defender, while `Hierophant` is the staff/shield/light-armor divine
  battle-caster with `Staff Conduit`, `Consecrated Conduit`, Devotion support,
  Church Class Ring awakening, and Voluntas bridge coverage.
- Cleric Devotion now has immediate post-promotion value: `Sanctuary Ward` is
  granted at Cleric level 1, held Devotion grants light incoming-damage
  reduction, `Sanctuary Ward` is hidden from combat skills until Devotion
  exists, and Devotion gain waits until the enemy survives the action.
- The relic quest opening now stages the mystery through `Uncertain Reports`
  before creating `The Holy Relics`, with old-save migration and shared core
  quest-progress handling.
- P8 automated closure now covers Devotion grants/visibility/survival rules,
  Race selection layout, Smoke Screen cleanup, promotion gear routing, staged
  relic progression, and shared postgame tavern dialogue. Manual play evidence
  remains the active readiness task.
- Current planning references:
  - `docs/PROGRESSION_REFACTOR_CHECKPOINT.md` for the complete version-5
    progression implementation record and the explicit pause boundary before
    the next game-design change.
  - `docs/ABILITY_TREE_DESIGN.md` for authored tree identities, exact
    Warrior-line graphs, and stable ownership rules.
  - `docs/CLASS_KIT_DESIGN_GATES.md` for promotion class-kit behavior and
    follow-up tuning gates.
  - `docs/COMBAT_BALANCE_DESIGN_GATES.md` for combat/balance gates.
  - `docs/STORY_AND_ENDGAME_DESIGN.md` for Vesperion, Voluntas, Liminal Gap,
    Reflection, and true-final story direction.
  - `docs/QUEST_STORY_INTEGRATION_DESIGN.md` for shipped quest-system staging
    that keeps early story objectives aligned with Forsaken Tenet mystery.
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

## Deferred Expansion Triage Map

This map indexes larger deferred expansions across owner docs. It does not make
any row implementation-ready by itself. Owner design-gate docs still define the
actual trigger, scope, save behavior, UI/log text, tests, and acceptance
criteria before code work begins.

Triage bands:

- `Promote Soon`: small, well-bounded slice with the owner doc already clear.
- `Needs Evidence`: requires playtest, simulator, UX, or asset review signal
  before promotion.
- `Needs Spec`: valid concept, but missing trigger, scope, UI, save, reward, or
  test contract.
- `Hold`: too broad or dependency-heavy for near-term implementation.
- `Do Not Promote As Cleanup`: tempting cleanup-shaped work that must stay
  behind a formal gate.

| Area | Deferred expansion | Triage band | Promotion trigger | Owner doc | First safe slice |
| --- | --- | --- | --- | --- | --- |
| Class-kit track expansions | Combo chains, Maestro progression, Beast Master stables, Grove questlines, Jump mastery, multi-vow systems, broader scar trees, divine economy, loot redesign, Seeker pathing, stealth rewrite, stolen-spell mastery. | `Needs Evidence` | Class-kit UI/log, pacing, and balance-threshold evidence identifies one specific track. | `CLASS_KIT_DESIGN_GATES.md` | One track's one-page spec, not a multi-track mechanics batch. |
| Class-ring tuning/presentation | Wizard radar visualization, ring status polish, and ring effect tuning. | `Needs Evidence` | Manual UI/readability notes or class-kit balance threshold findings. | `CLASS_RING_SYSTEM.md` | Presentation-only ring readability before numeric tuning. |
| Promotion ability transition expansions | Ability-history restoration, alternate retention policies, and new promotion spell/skill grants. | `Do Not Promote As Cleanup` | Explicit transition-rule spec with save/load and UI message behavior. | `PROMOTION_ABILITY_RULES.md` | One promotion path with save/load and text/pygame message coverage. |
| Combat semantics and architecture | Deeper-floor multi-enemy content, speed-based combat stacks, dice conversion, always-hit flags, ignore-defense order, unlockable race/class/difficulty strategy, and XP scaling. | `Needs Evidence` | Rebenchmark Pilot 3 after the ability-tree refactor, then decide the floor-5 second-promotion matrix and enemy-area-action boundary; other combat expansions still require their own full spec. | `MULTI_ENEMY_COMBAT_DESIGN.md`, `MULTI_ENEMY_PILOT_3_PLAN.md`, `COMBAT_BALANCE_DESIGN_GATES.md` | Preserve the completed manual acceptance and rerun promoted-class balance, not random rollout or rosters larger than two. |
| Equipment/economy save-heavy systems | Durability, identification, item modification, equipment actives, armor mobility, Tome effects, ultimate helmets, rarity semantics. | `Needs Spec` | Serializer, UI, economy, old-save, and balance contracts are defined. | `EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md` | Shop polish or one inert P6-adjacent item, not durability plus modification. |
| Dungeon/world interaction expansion | Harvestable roots/fungus, rubble clearing, crystal interaction, bone/gear salvage, deeper Realm of Cambion rooms, rewards, and encounter variants. | `Needs Spec` | Content beat, tile state, reward, and save behavior are defined. | `DUNGEON_WORLD_ENCOUNTER_DESIGN_GATES.md` | One decorative tile interaction with old-save inert fallback. |
| Presentation and asset expansions | Jump/Charge animation, Warp Point art, town/NPC/venue art, status-effect artwork, enemy identity presentation, website. | `Needs Evidence` | Target list and review-sheet workflow are approved, or UX evidence identifies a readability need. | `PRESENTATION_ASSET_DESIGN_GATES.md` | One generated bitmap batch or one readability layer with fallback behavior. |
| Story/endgame expansion | Bespoke Guardian rooms, mini-bosses, stronger consequences, deeper per-class Voluntas quests, deeper Reflection mechanics, Vesperion tuning/presentation, legacy Devil retirement. | `Needs Spec` | Story-content decision block defines beat, trigger, flags, UI surface, fallback, and tests. | `STORY_AND_ENDGAME_DESIGN.md` | One story-only vignette or one Guardian room spec, not route replacement. |
| Audio/event/meta systems | Final audio replacement, dynamic music, spatial audio, profiles, event payload enrichment, account-wide Bestiary, achievements, run summaries, persistent statistics. | `Needs Spec` | Concrete consumer, privacy/profile-storage decision, or asset-content need exists. | `SOUND_SYSTEM.md`, `EVENT_EMISSIONS.md`, Systems/Audio/Meta roadmap section | Source-specific event payload or audio route for an existing consumer. |
| UI/core boundary cleanup | Moving mechanics or data ownership out of `ui_*` modules into core services. | `Do Not Promote As Cleanup` | A concrete duplicated rule, save-critical behavior, or testability blocker is identified with owner module and compatibility behavior. | Systems/Audio/Meta roadmap section and the affected domain gate | One rule extraction with parity tests, not a broad UI-module refactor. |

## Active Priority - P8 Playtest Readiness And Polish

Status: `Active - Automated Closure Complete; Manual Evidence Pending`

P8 should convert the current shipped systems into a cleaner playtest baseline.
It is not a broad feature pass. The work should close obvious usability gaps,
add focused regressions around recent changes, and collect enough play evidence
to decide which larger gate deserves promotion next.

### Implementation Sequence

1. **Cleric/Hierophant Devotion closure**
   - Automated: complete. Focused tests cover immediate
     `Sanctuary Ward` grants, learned-ability promotion messaging, hidden skill
     visibility at 0 Devotion, held-stack damage reduction, and enemy-survival
     Devotion gain.
   - Manually smoke-test Cleric, Templar, and Hierophant Devotion in pygame
     combat, including `Relic Aegis`, `Consecrated Conduit`, and
     `Sacred Overchannel`.
2. **High-signal UI bugfixes**
   - Automated: complete. The Race selection `Virtue/Sin` section is pinned so
     two-line descriptions fit
     predictably, including the longest Dwarf description.
   - Automated: complete. Smoke Screen from invalid or non-fleeing states does
     not leak stale
     smoke, hidden-enemy, or flee-transition state into the next battle.
   - Automated: complete. Promotion with mixed legal/illegal gear keeps legal
     gear equipped,
     moves illegal gear to inventory, and does not grant promoted-class default
     gear.
3. **Quest and story-route regression pass**
   - Automated: complete. Staged relic opening checks confirm a new game starts with
     `Uncertain Reports`, `Cry Havoc!` stays spoiler-light, Triangulus updates
     report-back state, and reporting creates `The Holy Relics`.
   - Shared quest-progress logic and frontend regressions cover quest staging,
     old-save migration, and relic-count behavior.
4. **Class Ring and class-kit readability pass**
   - Inspect Class Ring wording across absent, inventory-only, stored,
     equipped-dormant, and equipped-awakened states.
   - Use `docs/CLASS_KIT_EVIDENCE_NOTES.md` to record manual findings for at
     least one martial meter, one caster/support meter, one persistent-progress
     track, and two awakened-ring preservation cases before numeric tuning.
5. **Playtest checklist triage**
   - Complete. `docs/PLAYTEST_CHECKLIST.md` indexes current playtest,
     deferred-spec, and shipped-regression groups.
   - Keep checklist edits documentation-only unless the route being checked
     exposes a reproducible bug.
6. **Next promotable implementation candidate**
   - Complete: shipped a shared postgame tavern dialogue slice for the Barkeep,
     Waitress, and Soldier. The next content candidate should be scoped only
     after the remaining manual evidence pass.
   - Do not promote durability, identification, multi-enemy combat, broader
     divine economy, account-wide Bestiary, or final-battle tuning without the
     owner-doc spec and evidence requirements.

## Active Priority - P7 Additional Improvements

Status: `Completed`

The P7 implementation for selector mouse support, reusable presenter/popup mouse
support, Equipment selected-slot visibility, dungeon location labels, enlarged
minimap modal, portrait-atlas variant browsing, generated dungeon special tiles,
generated familiar/summon artwork, and Character Menu companion art has shipped
and is tracked in `CHANGELOG.md`. There is no remaining P7 Active Priority
implementation work.

Completed follow-up posture:

1. Watch for future selectable pygame overlays added during playtest and apply
   the same hover-to-select, left-click-to-confirm contract where appropriate.
   - Shop screens now include that contract for main options, item rows, buy-list
     subtype tabs, and item-list wheel scrolling.
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
3. Town stable management, deeper evolution-specific companion behavior,
   summon action previews, and combat-side companion art placement remain
   deferred until playtest confirms the Character Menu presentation needs
   expansion.

## Presentation And Asset Gates

Status: `Spec Gate, V1 Identity/Asset Slices Shipped`

`docs/PRESENTATION_ASSET_DESIGN_GATES.md` is the behavior reference for this
section. The first quick-win slice shipped visual Character Created and New Game
story-card screens plus reusable combat cues for reflection, hard-control hits,
and elemental weapon strikes. The next focused slices shipped enemy identity
readability, a remade Quasit combat sprite, and active/inactive Warp Point
dungeon art with checked-in review sheets.

Remaining follow-up after this V1 slice:

- Status-effect artwork remains opt-in; fallback initials remain valid where no
  approved PNG exists. Evasive Guard now uses the approved status PNG.
- Jump and Charge wind-up/impact visuals remain deferred until enemy sprite
  stance adjustments are planned.
- Warp Point artistic renderings now have generated active/inactive runtime PNGs
  and a contact sheet.
- Town NPC renderings have shipped for recurring dialogue/shop/tavern figures,
  Old Warehouse guards, staffed Warp Point scientists, and story figures
  Acolyte, Reflection, and Vesperion through dialogue-only runtime art. Venue
  scenes and memory/reunion scene art remain deferred.
- Vesperion has a separate full-body combat sprite so final-boss combat art
  does not reuse dialogue portrait art or fall back to the generic boss sprite.
- Deferred story-scene targets are routed to presentation gates for
  Joffrey-body, Timmy-found/home, and Waitress grief/hostile variants.
- Enemy identity presentation V1 is shipped for invisible reveal notes,
  Mad Waitress form-change notes, and construct-friendly `Oil Leak` wording
  while preserving underlying mechanics.
- Replace rock pile with dead boss renderings; should reflect the current log
  message when encountering the dead body

## Dungeon, World, And Encounter Gates

Status: `Spec Map, V1 Quick Wins Shipped, Relic Text Shared`

`docs/DUNGEON_WORLD_ENCOUNTER_DESIGN_GATES.md` is the durable reference for
dungeon interaction, chest policy, encounter bias, Realm of Cambion deferrals,
relic discovery text, town hint flavor, and low-health dungeon navigation
presentation. V1 quick wins have shipped and are locked by focused regression
coverage: opened chests stay open, relic rooms use relic-specific discovery
text through shared Pygame and core handling, random encounters can
receive a soft active-quest target nudge, and pygame dungeon navigation keeps a
persistent low-health cue visible.

## Equipment, Items, And Economy Gates

Status: `Spec Map, Shop Polish V1 Shipped`

`docs/EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md` is the durable reference for
shop polish, ultimate helmet acquisition, durability/repair, item
identification, equipment actives, armor mobility, rarity semantics, dungeon
refreshers, Tome special effects, elemental armor/item modification, and
P6-adjacent item content. Shop Polish V1 has shipped for pygame purchase/equip
prompt clarity and equip-failure inventory safety; save-heavy systems remain
deferred until their contracts are promoted.

## Class, Ability, And Combat Gates

Status: `Spec Map, UI/Log Polish Batch Active, P8 Playtest Readiness`

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

Current active implementation batch is presentation-only UI/log readability
polish for class-kit meters, ring state, combat messages, and compact
menu/status hints across all shipped promotion tracks. This batch may add
status/log text and evidence notes, but mechanics and numeric tuning should
remain unchanged until playtest or simulator evidence promotes a specific
balance change.

P8 narrows the immediate class/ability work to playtest readiness: finish
Devotion regression coverage, verify promotion messaging, check combat skill
visibility, and collect evidence before tuning class-kit numbers.

## Story And Endgame Gates

Status: `Spec Map, Story Polish Epic, Class Ring Voluntas Tie-In, Story Polish Bundle V2, Liminal Trials V2, And Narrative Systems Bundle V3 Implemented`

`docs/STORY_AND_ENDGAME_DESIGN.md` is the durable reference for the implemented
Vesperion/Voluntas route, Liminal Gap, Guardian trials, Reflection/Psychopomp,
true-final completion, tavern epilogue, and deferred story polish gates. Future
work should deepen or polish that route rather than replace it unless a new
story spec explicitly changes the baseline.

New Game intro story copy expansion has shipped through shared content data and
is reflected in Pygame. The Story Polish Epic has also shipped:
Guardian trial definitions now live in core, Triangulus and Infinitas use
retry-safe Liminal trial echoes, Reflection presentation has martial/mystic/
hybrid copy, the Hooded Figure has a one-time post-Reflection angelic
confirmation, and Vesperion/tragedy copy has been polished without combat
tuning. Class Ring/Voluntas Identity Tie-In V1 has also shipped as optional
Liminal route polish: after Voluntas is revealed, a visible Class Ring can be
affirmed through the Hooded Figure guide, recording the player's current class
and dormant/awakened ring state for a one-time Reflection echo without changing
Class Ring mechanics, rewards, or true-final gates. Story Polish Bundle V2
extends that route with class archetype affirmation scenes, a one-time
Reflection Voluntas answer, retry/victory echo prose, an unnamed Hooded Figure
witness farewell, and clearer Vesperion phase/counter logs without numeric
tuning. Liminal Trials V2 deepens all six existing Guardian gate interactions
with shared threshold and choice-specific vignettes, completed-trial recall for
older saves, and Hooded Figure trial-depth review while preserving the current
map, rewards, combat numbers, route gates, and true-final prerequisites.
Narrative Systems Bundle V3 adds story-state-only class follow-up, Reflection
path mirror, true-final Vesperion choice argument/tragedy reframing, and a
legacy Devil compatibility audit without removing old Devil surfaces.

Remaining story/endgame follow-up should be promoted through
`docs/STORY_AND_ENDGAME_DESIGN.md` before implementation. The next likely
story gates are bespoke Guardian rooms, stronger Guardian consequences or
mini-bosses, deeper per-class Voluntas quests, deeper Reflection mechanics,
final Vesperion balance/presentation tuning, or a dedicated legacy Devil
compatibility-retirement cleanup after the audit-only boundary is intentionally
promoted.

### Additional Storyline/Endgame Content

Storyline follow-up should be promoted as small slices with one owner doc, one
trigger, and one validation target. Current candidates:

| Candidate | Status | First safe slice | Do not change without spec |
| --- | --- | --- | --- |
| Final-room and ending presentation polish | `Promote Soon` | Add story-card/dialogue polish that connects true-final prelude, victory, Voluntas ending, tavern epilogue, and final-room reminder. | Vesperion stats, AI, phase thresholds, `Choose Fate`, rewards, death/victory bookkeeping, or true-final gates. |
| Postgame town fallout | `Promote Soon` | Add local post-`main_story_complete` tavern/town acknowledgement for Busboy absence, Waitress/Joffrey grief, and Silvana after Voluntas. | Shop access, bounties, NPC availability, quest completion, rewards, or town routing. |
| Red Dragon continuity correction | `Ready` | Copy-only continuity pass that distinguishes Red Dragon boss defeat, Kaelenon restoration, and Zahhak binding without declaring non-Dragoon wins invalid. | Red Dragon floor gate, boss-room state, summon unlocks, Lancer/Dragoon mechanics, `Dragon's Fury`, rewards, or old saves. |
| Post-final save and harder replay | `Needs Spec` | One-page save/profile/difficulty spec for a completed-game marker and up to three completed heroes in harder replay. | Autosave behavior, inventory carryover, quest reset rules, profile storage, difficulty scaling, economy, or party composition. |
| Endgame asset/audio polish | `Needs Evidence` | Review existing Vesperion/Reflection/Acolyte portraits, Vesperion combat sprite, story-card timing, and final-combat audio routing before generating or tuning assets. | Combat mechanics, route gates, or dialogue availability. |

Near-term preference is the first two `Promote Soon` slices because they are
story-state-only and can be validated through special-event/dialogue checks plus
manual endgame playtest. The post-final save/replay idea is larger than story
copy; it needs save/load, profile, party, difficulty, economy, and old-save
contracts before implementation.

## Systems, Audio, And Meta Gates

Status: `Spec Map, Mouse Support V1 Shipped`

Systems, audio, and meta planning is split across durable owner docs:

- `docs/SOUND_SYSTEM.md` owns audio runtime, diagnostics, source-specific
  routing, final asset replacement gates, and future audio enhancements.
- `docs/EVENT_EMISSIONS.md` owns event payload enrichment rules and
  consumer-driven event policy.
- `docs/COMBAT_BALANCE_DESIGN_GATES.md` owns balance-suite tooling notes and
  numeric combat tuning gates.

## Other Bugfixes and Improvements

### Improvements

- [PAUSED] The version-5 flat-level and point-purchased ability-tree refactor
  is preserved in `docs/PROGRESSION_REFACTOR_CHECKPOINT.md`. Do not extend the
  current trees until the next fundamental game-design direction defines its
  progression, ability-ownership, and promotion model.
- Refactor ability menus in combat
  - Change to an action shortcut bar with (limited?) slots that can be rearranged
- Separate passive and usable abilities in the spellbook
  - create new tab for abilities; could be integrated with refactor ability bar
- Change how invisibility works in combat
  - invisible enemies are not singularly targetable but can be hit by AoE abilities
  - Do not draw sprite in combat unless Sight; possibly add reveal mechanic (high wisdom,
  combat awareness, etc.)
- Amplify charged abilities to make them more useful
  - add abilities for cancellation
- Add class-specific resource meters to the navigation and combat view
  - currently things like Resolve are included in the Combat Focus but should
    show up under HP and MP meters
  - use a different fill color for each different meter gauge
    - for Resolve, use dark purple
- Implement new combat view to allow for more realistic enemy sprite locations
  - allow expansion of multi-enemy combat beyond 2 enemies
  - make sure there is room for a combat stack for speed-based combat
- Resolve takes a long time to build up in order to use Bursts
  - increase generation for skills and/or lower cost for Resolve abilities
- Add popup helpers with descriptions for the Primary Attributes in the Progression
  tab
- Ability Improvements
  - `Ironwall Reprisal` should rarely miss, should do more damage, and hit
    all enemies; perhaps it is better described as a shockwave instead of
    a melee attack

### Playtest Findings

- The "Virtue/Sin" section at the bottom of the Race selection for a new character
  needs to be pinned at the level to allow for 2 lines per description; the
  Dwarf race description is the longest and fits this spacing

Account-wide Bestiary history, Bestiary rewards, achievements, titles,
gameplay bonuses, run summaries, and persistent statistics remain deferred
until profile storage, migration rules, privacy/scope decisions, and old-save
behavior are specified. Current per-save Bestiary behavior and reveal layering
remain the baseline: seen identity, defeated practical info, and detailed
mechanics only after combat detail visibility was earned.

Mouse Support V1 has shipped for the highest-ROI shared pygame layers: NPC
conversation/quest-text progression, bounty/content selection lists, read-only
content boxes, and reusable popup-menu row hover/click/wheel behavior. The pass
used the existing `mouse_helpers`, popup menu, and guarded-input patterns
without altering quest state, bounty generation, save data, audio routing,
keyboard behavior, or gameplay rules.

Bounty-board restocks now use saved per-character progress baselines: an empty
board with no active bounty can refill after enough dungeon steps, enemy
defeats, or a level gain, while immediate turn-in/reopen loops remain blocked.
Current tuning is conservative and should be playtested before changing the
thresholds.

The July 2026 ad hoc bugfix/improvement batch for Invisible Stalker visibility,
combat buff indicators, Weapon Discipline presentation, bounty-board popup
backgrounds, Pathfinder-branch promotion-preview tabs, and Warrior-line class
mechanic tabs has shipped and is tracked in `CHANGELOG.md`. Mage-tree mechanic
tabs are also wired, including Warlock's `Familiar` tab wording, and Footpad-tree
and Healer-tree tabs now announce their matching class-kit tracks. The pygame
Paladin vow picker now uses the current styled selection popup over the
progression background. Each highlighted choice documents its learned
signature ability, Aura benefits, Mark trigger and drawback, and then requires
an explicit oath confirmation before promotion commits.

### 2026-07-03 Roadmap Triage Implementation Note

- Confirmed `ENCUMBERED` already affects initiative, hit chance, and dodge; no
  new mechanic was needed.
- Fixed Corruption DOT apply messaging so it uses corruption language instead
  of burn language.
- Added baseline secondary effects for Water, Wind, and Earth attack spell
  families: Water weakens Attack, Wind slows Speed, and Earth can knock prone.
- Reduced Barghest Enfeeble pressure by lowering its priority and adding short
  debuff-failure cooldown behavior for enemy AI.
- Added pygame combat menu descriptions for usable items, spells, skills, Runic
  Boost, and Steal As Well.
- Reduced the fixed pygame combat-start transition delay.
- Changed looted relic altar minimap presentation to a spent altar icon.
- Added summon combat presentation follow-up: mapped summon art fallbacks,
  active-summon turn token display, active-summon status icons in the turn card,
  simplified summon victory XP text, and XP/level-scaled summon bond gain.
- Replaced mapped summon art fallbacks with bespoke transparent companion art
  for all 11 summon creatures, plus a summon companion-art review sheet.
- Balance baseline status: focused tests passed, but the full
  `tools/run_remaining_balance_baseline.py` wrapper did not complete in-session
  because its captured subprocess bundle stayed silent for several minutes.
  A dry-run bundle summary was written at
  `reports/balance_baselines/20260703_085504/remaining_balance_baseline_summary.txt`;
  do not treat it as numeric tuning evidence.

### 2026-07-02 Implementation And Evidence Note

- Implemented the Rookie Mistake sprite gate, popup mouse-close affordance,
  Combat Focus Evasive Guard cleanup, Fortune/Misfortune coin meters, blood
  overlay renderer/assets, and NPC response-map voice polish.
- Preserved current Footpad, ordinary drop, multi-strike, poison, and Enfeeble
  numeric behavior for this evidence-only balance pass.
- Added `poison_consistency` to `remaining_improvement_tuning_report()` with
  application rate, duration, tick damage, resist outcome, and immunity outcome
  metrics.
- Ran `./.venv/bin/python tools/run_remaining_balance_baseline.py`; summary
  output:
  `reports/balance_baselines/20260702_112805/remaining_balance_baseline_summary.txt`.
  `base_level_10` completed with return code 0. `first_level_20`,
  `second_level_30`, and `race_delta_level_20` returned 1 because
  `tools/run_balance_suite.py` referenced missing `abilities.DragonsFury`.
  The analytics harness now uses the existing Dragoon `DraconicOnslaught`
  power-up and skips optional missing power-ups instead of aborting. A rerun
  wrote partial output under `reports/balance_baselines/20260702_113519/` and
  was stopped after `base_level_10` completed because the remaining sweeps were
  still running beyond the practical validation window.

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
