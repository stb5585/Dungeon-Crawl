# The Forsaken Tenet Development Roadmap

*Updated: September 2, 2026*

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
lanes. Base-lineage promotions may combine identity and shared-track
prerequisites; promoted classes only expose combat paths relevant to their
catalogs. First promotions
cost two points and second promotions cost three; both are governed by path
prerequisites, permanent-stat gates, race eligibility, and global level 30/60
gates.
Learned abilities survive class changes; all unpurchased nodes in the prior
tree close. Church promotion and automatic level-based ability/stat awards
are retired. Progression is a Character Menu tab rather than a Town option.
Universal retention is intentional even when an ability falls outside the new
class identity: Monk keeps magic, Bard keeps divine abilities, Ranger keeps
attack spells, and Inquisitor keeps stealth. Promotion grants are additive;
specialization is expressed by current-tree access, mechanics, stats, and
equipment restrictions rather than destructive pruning.

Warrior was the first fully authored talent-tree prototype. Its six-column
graph leads through Arms to Weapon Master, Vanguard to Lancer, Bulwark to
Sentinel, and Command to Paladin. Weapon Master and Lancer share `Piercing
Strike -> Charge` before splitting into Weapon Focus and Honed Attack.
Weapon Master continues through `+10 Attack -> Cripple -> True Strike`, while
Lancer continues through `Driving Thrust -> +10 Defense -> Retaliate`.
Cripple is a level-20, less-accurate attack that weakens melee damage based on
damage dealt. The defensive trunk is `Shield Slam -> Shield Block`, then
Sentinel branches through Rally, Defense, Dishearten, and Aggressive Pursuit
while Paladin uses Goad, Chastise, Magic Defense, and Commitment. Commitment
rewards repeated attacks against one target and permanently closes the other
promotion routes. The fifth column connects Disarm, Defense, Improved Defend,
Upsurge, and Parry; the sixth connects Battle Cry, Adrenaline, HP, Double
Strike, and Achilles Heel. Weapon Master requires Strength 14, Dexterity 12,
and Intelligence 11; Sentinel requires Constitution 15; and Paladin requires
Constitution 14 and Wisdom 13. Requirements of 10 or lower are omitted from
every promotion. With separate currencies, all four routes cost eight progression
points; Weapon Master and Sentinel require four Human attribute points,
Paladin five, and Lancer three. Warrior off-hand equipment remains shield-only;
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
promoted and terminal class has a structurally declared graph. Named identity
paths do not by themselves prove authored mechanics: outside the rebuilt
Warrior, Mage, and Assassin/Ninja graphs, many promoted paths remain sparse
catalog-only layouts awaiting authored expansion. Generic rating padding has
been removed. Exact branch ownership and audit status are recorded in
`docs/ABILITY_TREE_DESIGN.md` and
`docs/CLASS_KIT_DESIGN_GATES.md`. Weapon Master is the first deliberately
asymmetric promoted tree: Berserker and Grandmaster routes use different node
types, Grandmaster forks permanently between Dual Wield and Duelist, and eight
independent weapon arts branch into rank-5 replacement upgrades instead of
being learned automatically. Its ungated inherited entry nodes and rating
nodes remain immediately available; the extended Berserker route adds
two-handed proficiency and discipline-scaled critical damage while keeping
both second-promotion nodes aligned.

Pathfinder has 40 development nodes across seven explicit vertical tracks:
Druid, Naturalism, Ranger, Melee, Shaman, Elemental, and Diviner. Its joined
promotion routes cost 11-14 points including promotion, leaving meaningful
choice within the 16 progression points available by level 30. Healer has 36 development nodes
across six full columns, and Footpad has 34 development nodes across six
columns. Healer's Bard, Cleric, and Priest promotions each require a complete
six-node identity column and the complete adjacent Support or Healing column;
their promotion routes cost 14 points including promotion. Monk remains an
independent six-node route costing eight points including promotion.
Footpad's Control track is required by both Thief and Assassin, while Defense
is required by both Spell Stealer and Inquisitor; each joined promotion route
costs 13 progression points.
Shared tracks can feed several promotions without duplicating nodes. The
remaining Footpad, Healer, and Pathfinder promotion graphs now expose only
their real catalog abilities. Generated rating families, repeated ranks,
generic cap masteries, and Lycan control acceleration were removed; exact
compact sizes prevent padding from returning. Beast Master's two-point Bonded
Bulwark remains because it has an authored companion-bond payoff. Several
underlying class systems still need the independently tracked implementation
work below.
Full counts, path costs, names, and generated diagrams live in
`docs/ABILITY_TREE_DESIGN.md` and `docs/ability_trees/`.

Mage is now the second bespoke base graph. Its six columns define independent
Elemental roots, matching Enhancements, Arcana, Occultism, Conjuration, and
Universal utility. Promotion route costs are `5` for Elemental Sorcerer, `6`
for Arcane Sorcerer, and `8/8/8` for Spellblade/Warlock/Conjurer. Sorcerer permanently chooses Classical
Force or Arcane Tradition, making School Affinity Elemental- or Arcane-focused
and severely nerfing the competing school. Learned spells survive promotion;
Guidance Upgrade and the six elemental spell nodes retain the existing
Sorcerer/Wizard partial carry-forward.

Spellblade now uses explicit Weapon, Armor, Spell, and Universal development.
Its combat loop stores independent Arcane and Elemental charge pools from
damaging spells; Storage Capacity adds a slot to each pool, and matching
Amplify talents double their release. Counter Charge uses the incoming spell's
broad category. Breakdown prepares spell-defense openings, while Novel
Shielding and the two Enhance passives make the equipped Tome, weapon, armor,
and current mana state part of the hybrid rotation.

Conjurer replaces the former tier-2 Summoner with authored Constructs, Binding,
Illusion/Movement, and Calling development. As Conjurer, the six Callings
create location-aware ordinary-enemy transients; the Calling nodes carry into
terminal Thaumaturgist, where each instead binds one permanent choice from its
two-Xenid pair. Conjure Animal becomes a seventh Calling and the fixed roster
contains exactly 14 named Xenids, including Hodag and Caladrius.
Thaumaturgist combines the former Summoner and Grand Summoner systems around
conduit progression: conduit replaces summon XP, unlocks Xenid ability tiers,
strengthens Xenid stats, and scales entity-specific caster effects. Mage
transient companions still act independently after the player,
use one transient slot, last 50 exploration steps, and never gain XP, bond,
loot, quest, or roster state. Numeric rating/HP/MP nodes are globally
path-gated without independent level gates; future class-specific nodes must
include a basic class mechanic instead of plain stat padding.

The terminal tree now uses five columns. Its Miracles lane contains Miracle
Blade, Miracle Shackles, Miracle Potion, and Miracle Crystal at levels
65/70/75/80; each consumes an extremely rare Reality Fragment to violate an
ordinary protection, restraint, item-creation, or mana/damage rule. The old
Summon/Summon 2 training passives are retired. Active Xenid death costs 25
conduit, and the combat-only 100-MP Raise Summon restores only that just-fallen
Xenid at 25% HP while refunding 10 conduit.

The authored terminal follow-up replaces Berserker's generated talents with
Heavy Weapons, Two-Weapon Assault, Fury, Survival, and eight centered
two-handed discipline arts. It adds Momentum, Tectonic Rift, Thunderous Vault,
Fatality, Composed Wrath, and Reckless Onslaught while retaining Final Assault
as a compatible purchase. Hemorrhage Thirst turns enemy bleed damage into
healing at the risk of a two-turn bloodlust crash. Grandmaster of Arms owns all
three levels of every weapon art plus ungated Double Strike positioned between
two ungated, discipline-scaled mastery talents.

Knight Enchanter now evolves Spellblade's typed Blade Charges through a
combat-only Foundation/Accent grammar instead of Arcane Tempo. Element, Force,
Protection, and Conjuration spell signatures shape Enchanted Assault, Aegis
Weave, and Spellbind without adding another resource.
The Arcane Duel ring's Weave Memory preserves a spent Accent as the next
Foundation. Its authored 20-node terminal tree uses one-point Assault, Aegis,
Spellbind, and independent universal columns. Storage Capacity II expands both
typed pools, while Quick Recharge carries a weapon-triggered release across a
multi-hit attack.

Lancer and Dragoon use authored Aerial Tempo trees. Lancer places Jump in
column 2, Polearm Assault in column 4, Polearm Proficiency and Excellence in
column 5, Polearm Guard in column 6, and universal attacks in column 7. Attack
sits directly below Jump; Defense leads independently to Vigilant Landing.
The polearm paths add Extended Reach, Swing & Bash, Phalanx, Critical Vigor,
Dragon Soul, and Polearm Excellence. Promotion sits in column 4 and requires
Vigilant Landing and Polearm Excellence plus level 60, `STR 17`, and `DEX 13`.
Dragoon retains all 23 Lancer
development nodes, adds Dragonheart, extends Polearm Excellence through Attack
to level-80 Polearm Mastery, and moves level-75 True Piercing Strike behind
True Strike in column 7. Dragon Dive joins Dragon's Ascent, Soaring Strike,
and the Unstoppable landing path.
The Aerial Tempo character tab presents its build/spend rules and every
unlocked Jump modification in a compact, non-scrolling two-column grid.
Dragon's Ascent follows the middle `+20 Attack` without a redundant level gate;
Quake and Soaring Strike extend Rend; and Retribution extends Grounded Landing
rather than the `+30 Defense` node, which is gated by Dragon's Ascent. Acrobat
unlocks at level 40, Thrust at 45, Rend at 50, Retribution at 65, True Piercing
Strike at 75, Unstoppable at 70, and Dragon Dive at 80. Both trees fit within
rows 0-7 without scrolling.
Jump modifiers synchronize with progression without becoming spellbook
actions, while Recover, Dragon's Fury, Skyfall, the Kaelenon route, and
polearm-and-shield equipment remain externally owned. Combat-only Aerial Tempo
resolves once per weapon action, and awakened Aerial Supremacy supplies the
tuned Landing Shield rather than a duplicate Meteor Guard payoff.

Sentinel, Stalwart Defender, Paladin, and Crusader complete the authored
Warrior promotion set. Sentinel uses six columns across Assault, Bulwark,
Resistance, Support, and independent inherited actions. Ungated, disconnected
Parry now tops its last column. Its centered promotion accepts any of four
level-55 talents. Stalwart contains 25 nodes across five disciplines, adding a
Shield Offense column while shifting Resistance and Support right. Resolve uses
the legacy `guard_meter` field as one value with
caps 50/100, explicit Defend/block/physical-damage/Goad/Hold gains, and no
duplicate Class Ring accumulation. Spell Block is the active anti-projectile
action and Spell Reflection is its passive reflection modifier. Stalwart's
Citadel Aegis, Ironwall Revenge, Last Bastion, and Stronghold full-bar Bursts
currently unlock immediately; replacing that placeholder with four
use-developed mastery tracks is an active critical gap below.
Its new Tower Offense, Get Even, Generator Shield, and Battle Determination
passives turn Shield Slam, Retaliate, Shield Ricochet, and Battle Cry into
additional Resolve interactions.

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
points after the shortest promotion route. Crusader contains 26 new nodes
across Melee, Spells, Healing, and Protection. Ungated Condemnation splits
into level-65 exclusive Two-Handed Weapon Proficiency and Sword & Board routes;
Beyond Reproach separately unlocks its mark/disintegration interaction. The
two-handed route ends in Penalization, while the shield route adds Censure,
True Piercing Strike, Shield Ricochet, and Triple Strike. The spell route runs
Repel the Wicked into Smite II, Sanctification, Undead Hunter, and Smite III;
Dispel begins the healing route through Cleanse, Heal II, Radiant Healing, and
Prayer of Faith. Protection now runs from Divine Protection through Parry,
Posturing, Consecrated Bulwark, and the replacing Divine Protection II.
Penalization, Smite III, and Divine Protection II cost two points.
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
  promotion stat tuning, Sorcerer/Wizard 0-based School Affinity progression,
  and the promotion ability transition decision matrix. The 2026-09-02 audit
  found several V1 class-kit payoffs that remain incomplete despite their
  state, tree, or presentation surfaces; they are tracked below.
- Cleric now has a second level-3 fork: `Templar` remains the heavy shield
  defender, while `Hierophant` is the staff/shield/light-armor divine
  battle-caster with `Staff Conduit`, `Consecrated Conduit`, Devotion support,
  Church Class Ring awakening, and Voluntas bridge coverage.
- Cleric Devotion has a narrow post-promotion foundation: `Sanctuary Ward` is
  granted at Cleric level 1, held Devotion grants light incoming-damage
  reduction, `Sanctuary Ward` is hidden from combat skills until Devotion
  exists, and queued gain waits until the enemy survives the action. The
  lineage audit found that action deduplication, several gain sources, and the
  Templar payoff/ring loop remain incomplete.
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

## Active Class-Kit Closure

These are implementation defects or incomplete advertised mechanics, not
deferred expansion ideas.

- **Critical — Berserker Bloodied Momentum:** replace per-damage-event gain
  with once-per-player-action and once-per-enemy-action generation, enforce the
  one-per-round below-25% bonus, spend at validated heavy-art/Final Assault
  action start, implement art mutations and miss behavior, add Battle Scar
  milestone/ring preservation, and cover the entire loop with focused tests.
  Remove the meter and its claims instead if the complete payoff is not going
  to ship.
- **Ready cleanup — shared Momentum presentation:** the Weapon Master,
  Berserker, Assassin, and Ninja trees reuse one ability class, but its base
  description now always says `Death Mark Setup`. Move that label into
  Assassin/Ninja-specific tree or detail metadata so non-marking classes are
  not promised a mechanic they cannot use.
- **Critical — Stalwart Resolve mastery:** replace the meaningless scalar
  `resolve_mastery` and zero-threshold Surges with four persistent mastery
  tracks learned through associated barrier, counter, survival, and fortress
  actions. Start with four qualifying uses per track, count once per action or
  defensive event, carry progress from Sentinel into Stalwart, expose locked
  progress in the Resolve tab, and test save/load and promotion behavior.
- **Ready cleanup — retired Resolve APIs:** after the mastery rewrite, remove
  Shield Check, Bulwark, active Shield Riposte, Covering Guard, and active Spell
  Reflection classes/functions/exports/tests unless an explicit legacy-save
  compatibility decision keeps them in an isolated adapter.
- **Critical — Wizard School Streak:** connect awakened-and-equipped ring state
  to eligible random spell riders through a once-per-action registry. Failed
  riders build school-specific stacks, success resets them, and four stacks
  guarantee and consume the next eligible opportunity. Define and test the
  lifecycle of unsaved `wizard_school_buffs` at the same time.
- **Critical — Shadowcaster Shade/backlash:** remove predecessor bonuses still
  triggered by `shade_of_ahool_turns`, retain only the authored Shadow, Speed,
  flight, and Holy-resistance effects, unify its timer, and trigger backlash
  conversion once on Shade end and low-HP ring healing with the correct ring
  and familiar modifiers.
- **Critical — Thaumaturgist conduit payoff:** consume Conduit Command on the
  active Xenid's next non-Recall action for its authored damage/healing and
  True Name effects; implement Recall/death/combat cleanup. Replace generic
  invocation damage with fourteen authored typed invocations, including the
  missing Hodag and Caladrius abilities and every documented rider.
- **Ready coverage — implemented but dispersed mechanics:** add parameterized
  coverage for all Grandmaster Weapon Art forms, Wizard school modifiers,
  Warlock familiar modifiers, and Shadowcaster terminal passives. These hooks
  exist, but current tests are representative rather than exhaustive.
- **Critical — Thief/Rogue authored kit:** replace the class-name-only loot
  messages with learned `Scavenger's Eye` rarity/drop behavior and a real
  `Finders Keepers` extra-loot roll; make Fortune/Misfortune action-scoped and
  connect them to authored risky-action odds/outcomes. Gate Cheat Death on its
  learned node, give Jinx a defined effect or remove it, and integrate the
  currently unused Loaded Dice failed-luck conversion.
- **Critical — Inquisitor/Seeker investigation payoff:** add the missing Revelation spender,
  visible-detail/telegraph progress rules, all four Case milestone effects,
  target-specific cleanup/presentation, live Wayfinding consumers, and actual
  dungeon/reward integration for Hidden Cache.
- **Critical — Spell Stealer/Arcane Trickster stolen-magic payoff:** centralize
  validate-then-spend MP handling for both theft abilities, add the missing
  stolen-scroll source in Steal As Well, resolve Stolen Charge once per action
  across weapon and spell payoffs through typed Arcane damage, and settle miss
  consumption.
  Make the awakened/equipped Arcane Larceny buff expire after three turns and
  clear correctly at combat/load boundaries.
- **Resolved — generic Footpad talent removal:** Thief/Rogue,
  Inquisitor/Seeker, and Spell Stealer/Arcane Trickster now expose only their
  real catalog actions. Repeated rating families and generic meter-cap
  masteries are gone; the remaining kit implementation gaps stay critical.
- **Resolved — Devotion action loop:** Cleric/Templar/Hierophant generation is
  action-scoped across healing, Holy, shield, block, and Turn Undead sources.
  Holy Retribution, Ordered Blessings, Relic Aegis, and typed action-consuming
  Consecrated Conduit payoffs are connected.
- **Resolved — Prayer support loop:** Priest/Archbishop generation is
  action-scoped across meaningful healing, support, cleanse, anti-magic,
  Resurrection, and authored Defensive Regen while passive ticks are excluded.
  Supplication, Great Benediction, Great Gospel, and Divine Intervention now
  resolve their complete resource payoffs.
- **Resolved — Monk/Master Monk Ki:** authored martial actions, hostile-action
  defensive reactions, and meaningful Chi Heal uses generate once per action;
  all five one-Ki riders and the full-Ki, 18-MP Dim Mak pipeline are connected.
  Dim Mak now honors weapon penalties, boss/Death immunity, contested Stun,
  essence recovery, and the once-per-combat Martial Master refund.
- **Resolved — Bard/Troubadour closure:** mastered repertoire has a live
  MP-costed combat action; composition, carried exploration steps, and clean
  completions advance mastery. Exploration songs leave conservative route
  codas, and Chorus Time's final coda now resolves its reduced contest.
- **Resolved — generic Healer talent removal:** all generated rating families
  and hidden meter-cap payloads are gone. Promoted Healer trees now contain
  only catalog abilities; Troubadour intentionally has no terminal purchases
  until genuinely authored progression is designed.
- **Resolved — Druid/Lycan persistent forms:** transformations use serialized,
  reversible overlays and survive combat, town, and save/load. Purchased nodes
  determine form access; Lycan stress, control ranks, ring mitigation, canonical
  Dragon Essence, dismissal rules, and Werewolf-only Winged Pounce are live.
- **Resolved — Diviner/Astromancer identity:** explicit rank metadata controls
  guaranteed learning from successfully resolved hostile spells. Threads now
  come only from the six authored actions, and Threaded Cast spends them on a
  validated spell/Runic Boost with exact accuracy, reliability, output, ring,
  and Rewind-safe behavior.
- **Resolved — Archdruid combat Aspect Harmony:** action/round-scoped charges,
  typed and immunity-aware Fourfold Surge riders, Primal Ascendance, Tree of
  Life, and once-per-combat Harmony preservation are live without changing
  persistent Grove/attunement progression.
- **Resolved — Totem Resonance and Soul harvest payoff:** matching casts and
  successful pulses gain once after resolution; Soul Totem/Surge consume
  harvested-type scaling nonlethally, and Aspect Evolution improves the cap,
  reliability, and output of every Surge aspect.
- **Resolved — Ranger/Beast Master closure:** awakened/equipped Shared Recovery
  now improves Pack Strike accuracy/output, Guard Partner, Harry Prey, and Mend
  Wounds while preserving the one-companion-turn action boundary.
- **Resolved — generic Pathfinder talent removal:** all generated rating
  families, cap inflation, and Lycan control acceleration are gone. Bonded
  Bulwark alone remains as a two-point authored companion-bond payoff; compact
  catalog-only trees make future authored expansion needs explicit.

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
| Promotion ability grant expansions | New mandatory promotion spell/skill grants; universal retention remains invariant. | `Do Not Promote As Cleanup` | Explicit additive-grant spec with save/load behavior and no ability replacement. | `PROMOTION_ABILITY_RULES.md` | One additive grant with flat-progression and save/load coverage. |
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
   - Automated foundation only. Focused tests cover immediate
     `Sanctuary Ward` grants, learned-ability promotion messaging, hidden skill
     visibility at 0 Devotion, held-stack damage reduction, and enemy-survival
     Devotion gain.
   - Completed: once-per-action generation, defensive sources, Holy
     Retribution riders, Ordered Blessings rotation, Relic Aegis counters, and
     typed/action-level Consecrated Conduit resolution have focused coverage.
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
- `docs/PROMOTION_ABILITY_RULES.md` owns universal promotion spell/skill
  retention and future additive-grant requirements.
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
- Combat improvements
  - Change how invisibility works in combat
    - invisible enemies are not singularly targetable but can be hit by AoE abilities
    - Do not draw sprite in combat unless Sight; possibly add reveal mechanic (high wisdom, combat awareness, etc.)
  - change/improve dodge calculations
    - speed is currently DEX-based; this makes some skills like Quickstep double-dip into DEX for dodge, making it overpowered
    - pure speed buffs are also currently applied twice: once in the base speed calculation and again in the dodge calculation
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
- Add popup helpers with descriptions for the Primary Attributes in the Progression
  tab
- Town Improvements
  - Add quests for the Magic Shop and Thieves Guild
  - Add Cure Curse in Church menu
- Items to include in the Settings menu
  - menu index reset or lock (stay on the menu option or default to top)
  - text print speed
  - combat speed
- Ability Improvements
  - Organize abilities into common files by class and/or type
    - for example, Resolve abilities are scattered in various files and even the Surges are not all in the same place
  - Continue playtesting Ironwall Revenge's three-hit reliability against
    high-dodge enemies and Repercussion's all-enemy tuning.
  - Resolve takes a long time to build up in order to use Bursts
    - increase generation for skills and/or lower cost for Resolve abilities
- Implement resting in the dungeon for recovery
  - include several items/tools that make resting more efficient
  - when resting, encounters can interrupt sleep; combat initiates with initiative lost
- Create and organize the spells and skills into coherent definitions
  - "Magic is organized into a coherent taxonomy that classifies spells according to their origin, mechanism, and intent. These classifications are designed to reflect how practitioners understand and manipulate magic within the world, ensuring that class identity, lore, and gameplay mechanics remain internally consistent."
  - differentiate ability types and schools; emphasize a clear philosophical origin
    - Innate arcane manipulation
    - Divine blessing
    - Natural forces
    - Spiritual communion
    - Extraplanar pacts
  - every ability should have a consistent mechanism or methodology
    - Manifesting
    - Binding
    - Transformation
    - Channeling
    - Projecting
  - every ability should have a clear intent
    - Damage
    - Protection
    - Restoration
    - Control
    - Mobility
    - Information
    - Summoning
  - classes should interact with them differently through altering reality
    - Spellblade channels magic through steel.
    - Conjurer brings entities into reality.
    - Thaumaturgist bends the rules governing reality.
    - Shaman negotiates with spirits.
    - Paladin invokes divine authority.
  - mechanics should reinforce philosophy
    - Resolve teaches perseverance.
    - Conduit teaches partnership.
    - Souls teach harvesting.
    - Oaths teach conviction.
  - similar effects do not require similar explanations
  - categories should explain, not just classify

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

### Weapon-hand decisions to revisit

- Basic attacks still use both equipped weapons; the main-hand-only rule applies
  to weapon abilities, spells, and automatic counterattacks.
- Sneak Attack explicitly uses both hands. Poison Strike is now a main-hand
  Poison Druid spell whose transformed bite deals physical and poison damage.
  Momentum and Thunderous Vault retain their authored hand-by-hand sequences.
  Kidney Punch still requires an off-hand weapon for its special effect rather
  than making a normal off-hand weapon-damage roll.
- Flurry of Blades uses only the main hand and has a 20-strike safety ceiling;
  its 8-percentage-point accuracy loss per attempt normally ends the sequence
  much earlier. Revisit the ceiling and penalty after combat telemetry exists.
- Decide whether future poison coatings apply separately to main- and off-hand
  weapons.
- Decide whether any future Riposte upgrades should explicitly enable a second
  off-hand counterattack; base Riposte and all existing Parry/Retaliate
  counterattacks are main-hand only.

### Detect spell tuning to revisit

- The eleven standard creature-family Detect spells currently last 50 travel
  steps. A matching encounter is revealed at a 50% base chance, gaining two
  percentage points per Wisdom above 10, capped at 90% (with a 25% floor).
- Detect Undead and Detect Fiend are placed in Paladin; Footpad uses Detect
  Animal, Detect Humanoid, and Detect Slime; and Pathfinder also uses Detect
  Animal alongside Detect Elemental. Place the remaining definitions in
  promotion trees where their creature families fit.

## Footpad Promotion Follow-Up

The obsolete empty column placeholders previously kept here are retired.
Assassin/Ninja now has an authored tree and implemented Death Mark system.
Thief/Rogue, Inquisitor/Seeker, and Spell Stealer/Arcane Trickster require the
mechanic closure and authored-tree replacement work listed in Active Class-Kit
Closure and specified in `docs/CLASS_KIT_DESIGN_GATES.md`. Do not add isolated
column fillers such as Find Traps or Disarm Traps before each branch's complete
identity, prerequisites, action semantics, and test contract are approved.
