# Progression Refactor Implementation Checkpoint

> Historical note: the curses frontend referenced in this checkpoint was
> retired after the checkpoint and is archived at Git tag `curses-ui-final`.
> Pygame is now the only supported player-facing frontend.

> Post-checkpoint scoped continuation (August 5, 2026): the bespoke Mage base
> tree and Sorcerer/Wizard elemental carry-forward are approved under this
> preserved version-5 baseline. This does not reopen general lineage expansion;
> other lineage redesigns remain paused until separately approved.

> Post-checkpoint errata (August 6, 2026): Mage was rebaselined again before
> distribution. Its current graph is the Elemental/Enhancement/Arcana/
> Occultism/Conjuration/Universal design in `ABILITY_TREE_DESIGN.md`;
> Warded Casting was retired; Conjurer replaces tier-2 Summoner; and the former
> Summoner/Grand Summoner systems are combined in terminal Thaumaturgist.
> Conjurer uses its six Callings for location-aware ordinary transients;
> Thaumaturgist adds Conjure Animal, paired choices, and ultimate unlocks for
> the fixed 14-Xenid roster. Xenid XP was replaced by conduit-driven growth and
> reciprocal caster effects. No save migration is required. Numeric
> rating/HP/MP nodes now have no independent
> level gates, and permanent node closures require Spend Distribution
> confirmation. The checkpoint below remains historical.

## Status

This document records the complete progression and Warrior-line implementation
checkpoint before further tree work is paused for a broader game-design
change.

The code in this checkpoint is functional and regression-tested. It is a
stable reference for the behavior that existed at the pause, not a requirement
that the next design preserve the same tree or currency model. Do not continue
expanding or retuning authored trees until the replacement design establishes
its new progression, class, ability-ownership, and promotion boundaries.

The canonical detailed references remain:

- `ABILITY_TREE_DESIGN.md` for tree identities and exact Warrior-line graphs.
- `PROMOTION_ABILITY_RULES.md` for eligibility, retention, closure, and
  transaction rules.
- `CLASS_KIT_DESIGN_GATES.md` for class resources and promotion-kit behavior.
- `CLASS_RING_SYSTEM.md` for awakened ring compatibility.
- `PLAYTEST_CHECKLIST.md` for manual acceptance coverage.

## Runtime Architecture

The refactor created one shared flat-progression authority:

- `src/core/progression.py` owns global XP, global levels, point awards,
  attribute training, node availability, atomic purchase plans, promotion
  application, ability adoption, branch closure, previews, and validation.
- `src/core/progression_manifest.py` owns stable node IDs, authored paths,
  coordinates, prerequisites, level and stat gates, icon semantics, rating
  payloads, exclusive choices, and class-specific tree-size rules.
- Both frontends consume the shared runtime state and result objects instead of
  owning separate progression rules.
- The old player-level promotion and automatic class-ability award paths have
  been reduced to compatibility surfaces. Church promotion is retired.

All 49 registered playable classes have declarative tree definitions. Generic
lineages use authored class paths from the manifest; the complete Warrior
lineage received bespoke graph, geometry, ability, and class-mechanic work.

Node IDs and talent keys are persistent version-5 save API. Renaming them
requires an explicit migration or alias.

## Global Level, XP, And Currencies

- Player level is global and capped at 100. Promotion no longer resets a local
  class level.
- The XP curve and carryover are centralized in the progression runtime.
- A character begins with one progression point and earns another on every
  even global level.
- Primary-attribute points are earned every fourth global level.
- Attribute points are stored until the player spends them from Progression.
  Level-up no longer forces an immediate attribute choice.
- Progression points purchase tree nodes only. They cannot purchase primary
  attributes.
- Attribute points purchase Strength, Intelligence, Wisdom, Constitution,
  Charisma, and Dexterity. The pygame interface spells out Constitution and
  Dexterity.
- The save loader converts the prior combined-budget training accounting into
  separate progression and attribute pools when the separate attribute field
  is absent.

## Shared Node And Promotion Rules

- Ordinary development nodes cost one progression point.
- First promotions cost two progression points and require global level 30.
- Second promotions cost three progression points and require global level 60.
- Permanent stat requirements use base/trained attributes; equipment and
  temporary transformations do not satisfy them.
- Race restrictions continue to govern first promotions.
- Rating nodes scale by tree tier:
  - base: `+10`;
  - first promotion: `+20`;
  - second promotion: `+30`.
- HP and MP nodes scale by tree tier at `+25`, `+50`, and `+100`.
- Named class talents grant the full tier-scaled rating amount for every
  rating they improve, plus their bespoke effect. They do not create fake
  spellbook entries.
- Ability gates use global milestones:
  - base trees: levels 1, 5, 10, 15, 20, and 25;
  - first-promotion trees: 35, 40, 45, 50, and 55;
  - terminal trees: 60, 65, 70, 75, 80, 85, 90, and 95.
- Rating nodes and explicitly inherited entries may be ungated.
- A purchase distribution is validated and applied atomically. Failure restores
  the class, stats, resources, combat ratings, equipment, inventory,
  spellbook, summons, companions, and progression state.
- Promotion previews disclose stat/resource/combat bonuses, equipment
  conflicts, and permanent closure before confirmation.
- Promotion combat-rating bonuses are multiplied by class tier: first
  promotions receive `2x` their class gains and second promotions receive
  `3x`.
- Illegal equipment is returned to inventory during promotion.
- Learned abilities survive promotion. Upgrade nodes atomically replace their
  earlier spell or skill form.
- Promotion closes the previous tree, competing promotions, and unpurchased
  nodes. Lancer-to-Dragoon is the authored exception: the historical Lancer
  tab becomes read-only while unpurchased Lancer development remains available
  inside Dragoon.

## Ability Ownership And Compatibility

- Previously learned abilities marked as inheritable highlight their matching
  node without charging another point.
- Inherited gated abilities do not recursively own or highlight their
  prerequisites.
- The compatibility repair removes phantom Paladin Oath's Judgment, Attack,
  and Tempered Conviction ownership produced by the earlier recursive adoption
  behavior while preserving genuinely learned Double Strike and True Strike.
- Known Goad, Retaliate, Parry, Double Strike, True Strike, Repel the Wicked,
  and configured Jump modifications use the same matching-node adoption rule
  where declared.
- Boss, item, quest, Class Ring, Power Core, contract, summon-bond, vow, and
  Weapon Discipline rewards remain externally owned unless a specific tree
  node explicitly represents them.
- Recover, Dragon's Fury, and Skyfall remain on their existing external
  unlock routes.
- True Piercing Strike no longer requires True Strike in the Weapon Master,
  Dragoon, or Crusader authored paths.

## Authored Warrior Base Tree

The Warrior graph was rebuilt as the shared foundation for four first
promotions:

- Arms begins with Piercing Strike, Charge, and Weapon Focus before continuing
  through Attack, Cripple, and True Strike toward Weapon Master.
- Vanguard branches after Weapon Focus through Driving Thrust, Defense, and
  Retaliate toward Lancer.
- Bulwark begins with Shield Slam, Shield Block, and Rally, then continues
  through Defense, Dishearten, and HP toward Sentinel.
- Command joins the defensive trunk through Goad, Magic Defense, and Chastise
  toward Paladin.
- Disarm, Battle Cry, Adrenaline, Honed Attack, Double Strike, and Parry are
  independent martial choices.
- Explicit cross-column connector channels keep shared requirements readable.
- Promotion requirements and Human point routes were tuned so every legal
  Warrior route can reach its first promotion with separate attribute and
  progression currencies.

## Weapon Master, Berserker, And Grandmaster Of Arms

Weapon Master is split between a heavy-weapon Berserker route, a mutually
exclusive Dual Wield/Duelist route toward Grandmaster, and independent Weapon
Arts.

Implemented behavior includes:

- inherited Double Strike and Parry adoption;
- Two-Handed Weapon Proficiency with accuracy and damage bonuses;
- Brutish Strength critical scaling;
- Dual Wield and Duelist permanent exclusion;
- stackable Honed Attack;
- Momentum, Cross Block, Blind Fighting, Retort, and Maim;
- True Piercing Strike rejoining either style;
- rank-1 and rank-5 Weapon Art nodes that require matching discipline mastery
  and replace lower forms instead of auto-learning.

Berserker now has authored Survival, Fury, and independent passive paths:

- Final Assault, Monkey Grip, Reckless Onslaught, and terminal Attack;
- Frenzy, terminal HP, Mortal Strike II, Boomerang Toss, and Triple Strike;
- inherited Parry, Pain Tolerance, and Hemorrhage Thirst;
- two-handed rank-1/rank-5 Weapon Arts only;
- Frenzy's forced berserk/critical behavior;
- Reckless Onslaught's stacking Attack/Defense tradeoff and parry knockdown;
- bleed mitigation and Bandage synergy from Pain Tolerance;
- Hemorrhage Thirst healing with a third-turn crash;
- returning multi-hit Devastating Throw behavior through Boomerang Toss.

Grandmaster of Arms now exposes all eight discipline lines through rank 10:

- every higher Weapon Art replaces its lower form;
- Perfect Form scales weapon damage and accuracy from the equipped discipline;
- Adaptive Arsenal scales parry and counter-critical chance;
- inherited Double Strike remains a floating option.

## Lancer And Dragoon

Lancer and Dragoon were rebuilt around Jump configuration, polearm-and-shield
combat, guarded landings, and combat-only Aerial Tempo.

The Lancer graph contains:

- Jump at the top with three independent paths:
  - Defend, Acrobat, and Grounded Landing;
  - Defense, Attack, and Promote: Dragoon;
  - Aerial Footwork, Quick Dive, Thrust, and Rend.
- Polearm Proficiency through Lance Sweep, HP, and Zephyrstrike.
- catch-up Parry and True Strike nodes.
- a Dragoon promotion connector that runs through the middle stat path while
  retaining the existing level and stat gates.

The Dragoon graph carries every Lancer development node forward and adds:

- ungated Polearm Excellence, terminal Attack, True Piercing Strike, and
  Polearm Mastery;
- Quake and Soaring Strike after Rend;
- Dragon's Ascent, terminal Defense, and Dragon Dive;
- Retribution and Unstoppable after Grounded Landing;
- Dragon Dive requiring the aerial and guarded-landing terminals.

Implemented class mechanics include:

- Aerial Footwork increasing Attack and Tempo capacity;
- Grounded Landing reducing final incoming damage during Jump charge;
- Lance Sweep polearm validation, weapon damage, and Dexterity-scaled Speed
  control;
- completed, uninterrupted Jump granting Tempo on a hit or miss;
- consecutive Jumps stacking without consuming existing Tempo;
- action-start Tempo spending by the next eligible Sword or Polearm attack;
- one coherent action-level damage and accuracy payoff, including multi-hit
  skills and miss consumption;
- Dragoon Speed pressure on a successful payoff;
- Dragon's Ascent improving clean Soaring Strike Tempo gain;
- Dragon Dive as an explicit all-stack spender that does not double-trigger
  the automatic payoff;
- awakened and equipped Aerial Supremacy improving payoff values and creating
  a real two-turn Landing Shield from clean Jump damage;
- shield refresh, absorption, depletion, expiry, and cleanup;
- legacy `+1 Jump Mod` acceptance without granting extra active capacity;
- shared direct-test and battle-engine helpers for Tempo and Jump behavior.

The Kaelenon restoration route, Cambion terminal branch, Draconite crafting,
Draconite Pendant recovery, Guard the Fall, equipment legality, Jump
conflicts, and inline Jump Mod controls remain intact. Draconic Onslaught
remains deferred.

## Sentinel And Stalwart Defender

Sentinel was rebuilt around three authored paths:

- Counter: Goad, Shield Check, Retaliate, Shield Riposte, Watchful Reprisal,
  and optional Attack.
- Wall: Hold the Line, Brace Wall, Covering Guard, Bulwark, Resolute Guard,
  and optional Defense.
- Anti-magic: Deflect Spell, Spell Reflection, Magic Defense, and HP.

Shield Block is omitted because the Warrior route already requires it. Known
Goad and Retaliate are adopted. Promotion requires Watchful Reprisal,
Resolute Guard, level 60, Constitution 20, and three points.

Stalwart Defender contains only new terminal development:

- Last Stand, Unbroken Wall, Defense, and HP;
- Punishing Guard and Attack;
- Fortified Citadel, Crushing Reprisal, and Final Redoubt Surge modifiers;
- Mirror Bastion and Magic Defense.

Resolve uses the legacy `guard_meter` backing value:

- Sentinel cap 50; Stalwart cap 100.
- Defend grants 10.
- A successful block grants `clamp(blocked damage // 5, 5, 15)`.
- Physical damage after mitigation grants `max(1, damage // 5)`.
- Goad and Hold the Line grant 5.
- Duplicate promotion-kit and Class Ring gains were removed.

Spell Reflection spends 25 Resolve, requires a shield, ignores Silence, waits
for two enemy spell opportunities, and redirects the first compatible hostile
targeted spell. Generic Reflect has priority. Beneficial, area, and explicitly
unreflectable spells do not consume it. Mirror Bastion grants 20 Resolve and
two turns of Magic Defense after a trigger.

Stalwart promotion grants the Surge wrappers without purchasing nodes.
Mastery thresholds remain 0/4/8, and the three authored modifier talents apply
their documented barrier, damage, control, healing, and duration upgrades.

Post-checkpoint errata: the Anti-magic description above records the historical
checkpoint. Current Sentinel implements one merged
`Spell Reflection -> +20 Magic Defense -> +50 HP` branch. Spell Reflection is
ungated at `(4, 0)` and uses compatibility ID
`sentinel.ability.deflect-spell`. The retired learned Deflect Spell ability and
the old `sentinel.ability.spell-reflection` node ID migrate to this merged
behavior.

## Paladin And Crusader

Paladin was rebuilt around two ungated Conviction spenders:

- Oath's Judgment at the top of the Zeal side.
- Oath's Shelter at the top of the Grace/Protection side.

Judgment branches into:

- Double Strike, Attack, Tempered Conviction, and True Strike;
- Smite, Repel the Wicked, Magic, and Hallowed Ground.

Shelter branches through Heal, MP, Resist Shadow, Sworn Purpose, and Blessed
Light, while Bless remains its own Shelter branch. The protection chain is
Magic Defense, Parry, Defense, and Divine Protection.

Crusader promotion is centered on row 8. Either Oath root satisfies its path
requirement; the prerequisite connectors descend to the promotion row before
joining. Existing Strength, Constitution, Wisdom, and Charisma requirements
remain.

Crusader contains four terminal groups:

- Melee: Condemnation into mutually exclusive Two-Handed Weapon Proficiency
  and Sword & Board styles. The two-handed route continues through Attack,
  Mortal Strike, and Righteous Advance. Sword & Board continues through True
  Piercing Strike and Triple Strike.
- Spells: Smite II, retained-or-purchased Repel the Wicked, and Smite III.
- Healing: Heal II, Cleanse, and Dispel.
- Protection: Consecrated Bulwark, Parry, Posturing, Magic Defense, and HP.

The permanent Paladin vow flow now uses a styled selection popup with
descriptions, learned signature actions, Auras, Marks, background retention,
and final confirmation.

Conviction behavior includes:

- valid signature-vow use granting one stack;
- the clean defining outcome granting one additional stack;
- an eligible Redeem refusal still granting the first stack;
- Paladin/Crusader base caps 2/3, raised to 3/4 by Tempered Conviction;
- Oath's Judgment and Shelter validating before spending all stacks;
- Judgment misses consuming stacks;
- distinct Redemption, Conquest, Protection, and Retribution offense/support
  payloads;
- Righteous Advance and Consecrated Bulwark improving the corresponding Oath
  action;
- awakened/equipped Vow Affirmation preserving one stack once per combat
  without removing Mark penalties.

Additional implemented abilities include:

- Hallowed Ground, a three-turn Holy damage-and-healing field;
- Resist Shadow, an exploration-time Shadow resistance spell;
- Blessed Light, which turns successful combat healing into a refreshing
  Attack buff;
- Condemnation, which deals weapon and Holy damage and can mark fiends or
  undead;
- Repel the Wicked, which makes eligible enemies flee without kill rewards or
  disintegrates a Condemnation-marked target;
- Sword & Board, which improves accuracy and weapon damage with a one-handed
  weapon and shield.

Turn Undead and Turn Undead II are absent from the Paladin/Crusader trees.
True Strike is absent from Crusader and is not required by True Piercing
Strike.

## Frontend And Presentation Work

The pygame Character Menu now contains a full Progression tab:

- authored node coordinates and orthogonal connectors;
- compact layouts designed to avoid scrolling at the baseline resolution;
- icon-atlas rendering with owned, available, blocked, pending, and closed
  states;
- node detail descriptions, costs, level gates, stat gates, and blockers;
- staged node and attribute distribution with Reset and Spend Distribution;
- permanent promotion warnings and promotion previews;
- current/completed tree navigation;
- read-only completed trees;
- inline Lancer/Dragoon Jump Mod configuration;
- descriptive Paladin vow selection and confirmation.

The Primary Attributes panel:

- displays full attribute names;
- previews pending increases without mutating the player;
- shows stored available attribute points at the bottom;
- is tall enough for all attributes and the currency footer;
- leaves a separate, slightly smaller node-description panel.

The curses frontend uses the same progression runtime, point pools, promotion
requirements, class-mechanic menus, and ability ownership rules.

Both frontends received:

- promotion result and equipment-conflict handling;
- class-mechanic navigation for Weapon Discipline, Oath Conviction, Aerial
  Tempo, and Resolve;
- combat selection and logging support for the new actions;
- status/resource presentation and cleanup;
- restored external quest/item/class-ring routes.

The pygame progression visuals add a dedicated ability icon atlas and loader:

- `src/ui_pygame/assets/ability_icons/ability_icons.png`;
- `src/ui_pygame/assets/ability_icons/ability_icons.json`;
- `src/ui_pygame/assets/ability_icon_manager.py`.

## Save, Load, And Cleanup

- Save version 5 persists global progression state, purchased stable node IDs,
  trained attributes, ability ranks, completed trees, and chosen promotions.
- Pre-release version-4 authored progression saves are intentionally rejected
  because their generated IDs cannot be migrated safely.
- Legacy combined point accounting is normalized into separate currencies.
- Existing Guard Meter data remains the Resolve compatibility source.
- Existing Jump modification data and external rewards are synchronized with
  matching authored nodes.
- Combat-only Aerial Tempo, pending payoffs, landing shields, Conviction,
  pending Oath effects, and Spell Reflection preparation are cleared on their
  documented combat, flee, death, class-change, and restoration boundaries.
- Promotion transactions and failed staged distributions roll back safely.

## Tests And Validation At The Pause

Focused suites were added for:

- global XP, levels, currencies, save round trips, all 49 tree declarations,
  promotion affordability, stat gates, closure, and atomic purchases;
- Warrior, Weapon Master, Berserker, and Grandmaster authored graphs and
  mechanics;
- Lancer/Dragoon tree geometry, Jump modifications, Aerial Tempo, new actions,
  Aerial Supremacy, equipment, and quest regressions;
- Sentinel/Stalwart tree geometry, Resolve, Spell Reflection, Surges, mastery,
  and compatibility;
- Paladin/Crusader geometry, vow selection, Conviction, Oath actions,
  Hallowed Ground, Resist Shadow, Blessed Light, Condemnation, Repel the
  Wicked, Sword & Board, inheritance, and legacy adoption repair;
- pygame progression rendering, connectors, panel geometry, staging,
  confirmations, icons, and compact no-scroll layouts;
- curses and pygame combat, Church, promotion, Character Menu, save/load,
  equipment, shop, quest, and class-ring regressions.

Validation completed immediately before this checkpoint:

```text
./.venv/bin/python -m pytest -q
2578 passed
```

Authored-tree validation also passed with no errors, and `git diff --check`
reported no whitespace errors.

## Explicitly Preserved External Systems

The refactor intentionally preserves:

- Class Ring trials, awakenings, and current equipment requirement;
- permanent Paladin vows and Church recovery;
- Paladin Auras and Marks;
- Kaelenon, Realm of Cambion, Draconite, and Dragoon item/boss routes;
- Weapon Discipline insight and mastery;
- heavy-armor, shield, polearm-and-shield, and class weapon restrictions;
- quest-, item-, boss-, contract-, companion-, and Power Core-owned abilities;
- both frontend entry points and their shared combat engine.

## Deferred Or Out Of Scope At This Checkpoint

The following were deliberately not folded into the refactor:

- party threat or multi-target tank protection;
- Paladin morality, vow respec, or a broader oath-loss system;
- Draconic Onslaught Power Core implementation;
- migration of unfinished generated node IDs;
- converting external item, quest, boss, or Class Ring rewards into point
  purchases;
- broader combat or game-design changes implied by the next redesign.

## Resume Boundary

When work resumes, begin from a written replacement design and decide:

1. whether global flat progression and two stored currencies remain;
2. whether abilities, passive improvements, and promotions still share one
   tree;
3. how previously learned abilities participate in later class development;
4. whether promotion closes options, carries them forward, or changes the
   character's available progression surface;
5. which class resources remain baseline mechanics versus tree purchases;
6. what portion of the version-5 save contract should migrate.

Until those questions are answered, treat this commit as the last supported
checkpoint of the current authored-tree direction.
