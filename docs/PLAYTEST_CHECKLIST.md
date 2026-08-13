# Playtest Checklist Index

The playtest material is grouped by decision value so the active queue stays
small without discarding historical regression coverage.

- [Current P8 playtest](playtest/CURRENT.md) contains the manual routes that
  can change the next implementation decision.
- [Shipped regressions](playtest/SHIPPED_REGRESSIONS.md) preserves the detailed
  system, content, frontend, save, asset, and audio checklist.
- [Deferred spec gates](playtest/DEFERRED_SPEC.md) lists concepts that need an
  owner-doc decision before implementation or playtest expansion.

Record class-kit findings in
[CLASS_KIT_EVIDENCE_NOTES.md](CLASS_KIT_EVIDENCE_NOTES.md). Completed automated
coverage belongs in tests and the changelog; this index should not become a
second implementation backlog.

## Flat Progression

- [ ] Create each base lineage and verify it begins with one unspent point,
  no purchased nodes, and no progression-granted ability. Spend that point on
  either an attribute or any available first-tier node.
- [ ] Verify both creation flows explain that the first point can be spent in
  Character > Progression and neither frontend opens that tab automatically.
- [ ] Confirm Warrior paths are ordered Weapon Master, Lancer, Sentinel, then
  Paladin. Verify Weapon Master and Lancer share Piercing Strike, level-5
  Charge, and level-10 Weapon Focus before splitting. Verify `+10 Attack`
  sits opposite Driving Thrust; the branches then end at True Strike and
  Retaliate respectively. Sentinel ends Dishearten, `+25 HP`; Paladin ends
  Magic Defense, Chastise.
- [ ] Verify the defensive spine is Shield Slam, Shield Block, Rally; Sentinel
  then branches through Defense, while Paladin branches directly through Goad.
  Lancer joins Shield Block at Retaliate. Confirm all four baseline Human
  Warrior promotion plans cost exactly 13 points.
- [ ] Verify Weapon Master requires Strength 15, Dexterity 12, Intelligence
  11; Lancer requires Strength 13; Sentinel requires Constitution 16; and
  Paladin requires Wisdom 13.
  Confirm promotion details say `Required level` and `Required Stats`, use full
  stat names, omit current-value suffixes, and wrap the competing-promotion
  warning in red.
- [ ] Verify Disarm, Battle Cry, Adrenaline, Honed Attack, Double Strike, and
  Parry are prerequisite-free fifth-column talents. Battle Cry has no level
  gate; the remaining applicable gates are 10, 15, 20, and 25 and appear only
  once in details.
- [ ] In pygame, confirm the Warrior nodes use semantic icons, have no path
  headings, do not overlap, and show downward prerequisite connectors. Verify
  cross-column connectors enter the side of their target node, and the Shield
  Block-to-Retaliate vertical segment bisects the Lancer and Sentinel columns.
  Verify the detail panel omits owned/available/blocked labels, lane text, and
  prerequisite text already communicated by connectors. Confirm Available
  Points appears in the tree header, the tree fills the content height, and
  the text-only detail panel sits beneath Primary Attributes. Confirm the
  permanent-choice warning sits at the bottom of the tree, remains muted
  normally, and turns red when a promotion is distributed.
- [ ] Verify connector lines are muted, remain behind opaque node and label
  backings, and never bleed through icons or talent names. Use each attribute
  row's minus/plus controls and confirm its staged total appears in parentheses.
- [ ] Verify Mage uses Elemental spell, Enhancement, Arcana, Occultism,
  Conjuration, and Universal columns. Confirm the six elemental spells are
  independent level-1 roots and their matching Enhancements require only that
  spell and level 20.
- [ ] Complete the `5/8/8/8` Sorcerer/Spellblade/Warlock/Conjurer routes.
  Confirm the exact `5/10/15/20/25` named gates, path-only MP nodes,
  level-`10/15/20/25` Universal roots, and two-point level-30 promotions.
- [ ] Select Classical Force and Arcane Tradition separately. Confirm either gates
  Sorcerer from `(0.5,6)` or `(1.5,6)` through promotion `(1,7)`, selecting one
  permanently closes the other, and Spend Distribution
  lists the closure before committing. Verify Elemental versus Arcane School
  Affinity, the agreed 50% off-school potency nerfs, and Arcane Tradition's halved
  Enhancement proc chance.
- [ ] Trigger all six 20% Enhancements and verify refresh-only behavior: Fire
  Inside next-attack critical chance; Frozen Armor one-turn Defense/Ice
  resistance; Electrified melee jolts; Wind Currents Speed/melee accuracy;
  Refreshment 5% max HP/MP; and Terra Firma 50% melee damage.
- [ ] Verify Polymorph action denial, its smaller confused-pacing bunny artwork,
  and the 10% boss success chance without boss immunity. Verify all-enemy
  Blinding Fog, temporary-HP ordering, Shackles Dexterity/Strength checks, and
  the documented Arcane Fundamentals and Binding Circle bonuses. Confirm
  Forbidden Studies
  gives Shadow Bolt `+20%` damage and undead companions `+50%` duration.
- [ ] Verify Mana Shield redirects at most 25% of physical damage from each
  attack and Mana Shield 2 raises the cap to 50%; neither redirects magical
  damage.
- [ ] Cast Enfeeble across low, equal, and high Intelligence-versus-Constitution
  matchups. Confirm its `20-95%` hit-chance clamp and four-turn `20%` reductions
  from the target's base Attack and Defense.
- [ ] Verify Spellblade uses the four Weapon, Armor, Spell, and Universal
  columns, with Imbue Weapon absent because it gates the promotion from Mage.
  Confirm Counter Charge, Reflect, and Boost share ungated row 2; rows 3-7
  represent levels 35-55 in five-level steps; and the Knight Enchanter
  promotion occupies row 8. Verify Reflect
  leads through +20 Magic Defense, Novel Shielding, and +20 Defense to Enhance
  Armor, while Boost sits immediately above Kinetic Explosion. Verify True
  Strike, Parry, and Double Strike at levels 35, 40, and 45. Confirm
  Breakdown stacks to five and is consumed after benefiting a
  damaging spell; Novel Shielding requires a Tome, snapshots twice its power,
  refreshes for full cost, and absorbs direct weapon/spell damage before
  temporary HP while ignoring DOT, reflected, field, and environmental damage;
  and Kinetic Explosion damages every enemy for one charge per cast.
- [ ] With Storage Capacity, fill both the two-charge Arcane and two-charge
  Elemental pools and confirm categories accumulate independently.
  Confirm both typed icons remain visible at zero, are dark while empty, and
  light independently as their pools gain charges.
  Verify Counter Charge gains at most one charge per incoming spell action;
  Counter Charge uses the incoming spell category; each Amplify doubles only
  its matching pool; broad Arcane/elemental resistance applies; misses preserve
  charges; and combat end clears all Spellblade state.
- [ ] At full and empty mana, verify Enhance Blade adds respectively 100% and
  0% of base weapon damage before multipliers, while Enhance Armor adds 0% and
  100% of equipped armor to physical armor.
- [ ] Learn Knight Enchanter Third Eye at level 70 through Aegis Release. Confirm
  Intelligence increases critical chance and both weapon and spell dodge
  chance, while changing Intelligence without Third Eye does not grant those
  additions.
- [ ] As Knight Enchanter, cast Element, Force, Protection, and Conjuration
  spells and verify the first signature remains the Foundation while the latest
  different signature replaces only the Accent. Repeated signatures must not
  add slots, and mixed spell categories must never replace typed charges.
- [ ] Release each Foundation and Accent through an ordinary charged weapon
  hit, Aegis Weave, and Spellbind. Verify all charges are consumed, Spellbind
  waits up to three turns for a positive-damage spell hit, applicable damage is
  Non-elemental, and combat end clears pattern, pending Spellbind, and charges.
- [ ] Exercise Cleaving Edge, Resonant Strike, Echoing Blade, Arcane Riposte,
  Weave Reservoir, Re-debuff, Defensive Release, and Quick Recharge. Confirm
  Defend is replaced, preparation caps at three stacks, adjacent targeting
  follows encounter slots, and a multi-hit weapon release repeats on every
  successful hit without surviving the action. Verify Storage Capacity II
  supports three charges per type alone and four when stacked with Storage
  Capacity, and that all pending release state clears at combat end.
- [ ] Awaken and equip Arcane Duel. Confirm Weave Memory preserves a spent
  Accent as the next Foundation without creating or displaying Arcane Tempo.
- [ ] Verify the Sorcerer gate is `INT 15/WIS 13`, Warlock
  `INT 14/CHA 14/WIS 10/CON 10`, Spellblade
  `STR 10/CON 11/INT 14/CHA 12`, and Conjurer
  `CHA 13/INT 13/WIS 12/CON 10/DEX 10`, with no Strength gate.
- [ ] Promote Mage along all four routes. Confirm every learned spell survives;
  non-elemental Mage nodes and competing promotions close; and unrelated
  classes cannot purchase Mage nodes. For Sorcerer and Wizard only, confirm
  unpurchased Arcane Fundamentals, Firebolt, Shock, Tremor, Water Jet, Ice
  Lance, and Gust appear in the current editable tree while the historical
  Mage tab remains read-only. Verify the promotion warning/result explains
  this partial carry-forward and save/load preserves ownership, talents,
  completed trees, and later elemental purchases.
- [ ] Conjure an animal and enliven the last defeated non-boss enemy. Confirm
  the Charisma/Luck check, one transient companion, an independent random
  follow-up after the player, replacement by a later summon, dissolution after
  50 exploration steps, save/load persistence, and no companion XP, bond,
  loot, quest, or permanent-roster entry. Confirm Conjurer does not inherit
  permanent Xenid systems merely by promotion.
- [ ] Verify the Conjurer tree contains Constructs, Binding,
  Illusion/Movement, and Calling with exact authored rows and level gates:
  Floating Crystal/Torchlight/Magic/Elixir/Barrier Wall,
  Sleep/Silence/Banish/Weaken Mind/Mana Barbs, Mirror Image/Nightmare
  Fuel/Volitation/Teleport/Explosive Decoy, and the six Callings. Confirm
  already-known Sleep and Mirror Image display as owned. Confirm Barrier Wall,
  Mana Barbs, Explosive Decoy, or Conjure Dragon can gate the level-60 three-point
  Thaumaturgist promotion.
- [ ] As Conjurer, cast every Calling on floors with and without a local exact
  type. Confirm it prioritizes an ordinary matching enemy from the current
  floor, falls back to the nearest matching floor, creates only the 50-step
  transient companion, and never prompts for or adds a Xenid.
- [ ] Promote to Thaumaturgist through a non-Calling discipline. Confirm
  Conjure Animal and all six unpurchased Calling nodes appear in the current
  tree while the historical Conjurer tree is read-only. Buy each paired choice,
  choose exactly one
  Xenid from each pair, and confirm the choice persists through save/load
  while the competing Xenid remains unavailable: Hodag/Caladrius, Patagon/Kobalos,
  Dilong/Cacus, Agloolik/Izulu, Hala/Lamashtu, Seraphim/Bardi, and
  Tiamat/Zahhak. Confirm no other summon is labeled a Xenid and Fuath remains
  only the Underground Spring boss.
- [ ] Raise several Xenid conduit values. Confirm Xenids gain stats and
  abilities from conduit rather than XP, each chosen Xenid adds its documented
  caster effect, the paired ultimate node grants only the selected Xenid's
  ultimate, and level-80 Conduit Mastery amplifies caster-side effects.
- [ ] Exercise Floating Crystal, Conjure Elixir, Barrier Wall, Banish, Mana
  Barbs, Torchlight, and all six Calling spells. Confirm Floating Crystal
  siphons 10% maximum MP per caster turn, bursts at 30%, and scales damage by
  spell power; Torchlight halves encounter rate for 50 steps. Confirm the
  Necromancer enemy raises one rewardless undead reinforcement that
  participates in the multi-enemy turn order.
- [ ] Conjure Animal on several floors. Confirm every result is an existing
  `Animal` enemy, current-floor Animals are preferred, and the nearest floor
  is used only when no local Animal is defined.
- [ ] At the standard Pygame resolution, confirm Mage, Sorcerer, and Wizard
  fit their progression panels without node overlap, scrolling, or clipped
  connectors. Confirm the Enhancement merge runs down the `0.5` midpoint into
  the top of Classical Force and the Arcane Fundamentals line runs down the
  `1.5` midpoint into the top of Arcane Tradition.
- [ ] Verify Footpad, Healer, and Pathfinder expose their four authored
  independent first-tier choices. Confirm Pathfinder may choose Natural
  Attunement or Tremor and receives neither automatically.
- [ ] Inspect every promoted tree and confirm its branch labels match
  `ABILITY_TREE_DESIGN.md`, no terminal tree is a chain of anonymous rating
  nodes, and named talents do not appear in the combat spellbook.
- [ ] Purchase a meter-cap talent, save/load, and promote. Confirm ownership,
  the `+5` passive combat bonus, and the extra class-kit meter capacity all
  persist.
- [ ] For each race, verify every registry-legal first and second promotion can
  be purchased at levels 30 and 60 respectively. Human routes should retain at
  least three optional points.
- [ ] Use Natural Attunement and verify 5 MP, self target, three turns, and
  `level // 2 + 1` Defense and Magic Defense.
- [ ] Verify Weapon Focus adds 0.05 weapon accuracy without changing spell
  accuracy; Rally refreshes its three-turn defenses without stacking; and
  Driving Thrust uses 1.0x damage normally and 1.5x against Stun.
- [ ] Verify Dual Wield permits the listed one-handed off-hand weapons,
  only after its Weapon Master style node is purchased; a Warrior without that
  node may equip only shields in OffHand. Verify Cripple is level 20, sits
  immediately above True Strike, uses lowered accuracy, and reduces the
  target's melee damage in proportion to damage dealt.
- [ ] Verify Weapon Master's Berserker route begins with Double Strike and
  places level-35 Two-Handed Weapon Proficiency after Attack, leaves one empty
  row, then continues through Mortal Strike, Devastating Throw, and Brutish
  Strength. Verify both second-promotion nodes share a row. Verify its
  Grandmaster route begins with Parry, forks permanently between Dual Wield and
  Duelist, and rejoins at True Piercing Strike after either Cross Block or Maim.
- [ ] Verify Warrior-learned Double Strike and Parry are pre-owned without
  spending another point, and that both entries and all numeric rating/HP/MP
  nodes have no independent level requirement. Verify rating nodes grant `+10`, `+20`, and `+30`
  in base, first-promotion, and terminal trees respectively. Verify Weapon
  Master's Honed Attack purchase stacks its critical bonus from 25% to 50%
  when the Warrior rank was retained.
- [ ] Verify each Weapon Master art is independent and blocked below rank 1 of
  its matching Weapon Discipline. Verify its right-hand child is blocked below
  rank 5, replaces the lower form when purchased, and neither form is
  automatically added to Skills when its rank is reached. Verify neither art
  level has a global-level requirement and the specialization requirement is
  printed only once in node details.
- [ ] Select Dual Wield or Duelist and verify every unreachable descendant on
  the competing path turns red, while True Piercing Strike remains reachable
  through the selected path.
- [ ] Use Momentum with two weapons and verify the combined finisher occurs
  only when both opening attacks hit. Use Cross Block and verify Strength and
  both weapons determine mitigation; a complete block can disarm the attacker.
  Verify Duelist bonuses require one one-handed weapon and an empty off hand,
  Blind Fighting softens Blind, Retort adds Intelligence to Parry/counters,
  Maim disables the target's main hand and triples critical damage, and
  Devastating Throw disarms its user. Verify Two-Handed Weapon Proficiency adds
  `10%` accuracy and damage only with a two-handed weapon, and Brutish Strength
  increases critical bonus damage by `5%` per matching discipline rank.
- [ ] Verify Berserker's class tab hides Fist, Dagger, Sword, and Club. Confirm
  its tree contains four centered rows of two-handed rank-1/rank-5 arts.
  Confirm ungated Final Assault and Frenzy begin the left paths; Survival
  continues through Monkey Grip 1, `+30 Attack`, and Monkey Grip 2, while Fury
  continues through `+100 HP`, Mortal Strike 2, Boomerang Toss, and Triple
  Strike. Confirm level-70 Reckless Onslaught sits between `+30 Attack` and
  Monkey Grip 2. Confirm both left paths occupy five vertically centered rows,
  the centered third column contains ungated inherited Parry, level-65 Pain
  Tolerance, and level-70 Hemorrhage Thirst across three centered rows, and
  every column remains inside the tree panel.
- [ ] Use Frenzy and verify three forced basic-attack turns with its damage and
  critical bonuses. Verify Pain Tolerance halves bleed damage and vulnerability
  and doubles Bandage healing. Verify Boomerang Toss makes Devastating Throw
  hit three times, return, and avoid Disarm. Verify Reckless Onslaught replaces
  Final Assault, deals double weapon damage, stacks `+5 Attack/-5 Defense` when
  refreshed, and knocks its user Prone when parried. Verify Hemorrhage Thirst
  heals exactly the enemy's successful bleed-tick damage, a non-triggering turn
  breaks its streak, and a third consecutive trigger causes two unconscious
  turns before resetting.
- [ ] Verify Grandmaster of Arms shows all 24 rank-1/rank-5/rank-10 art nodes.
  Rank-10 nodes must require discipline 10, replace level 2, and have no global
  level gate. Confirm ungated Double Strike appears between Perfect Form and
  Adaptive Arsenal in the fourth column.
  Verify ungated Perfect Form scales damage/hit by `1%/0.5%` per rank and
  ungated Adaptive Arsenal scales parry/counter-critical chance by `0.5%/1%`
  per rank. Confirm all three floating entries and all three art columns remain
  inside the tree panel, and long specialization requirements wrap in Details.
- [ ] Verify Lancer shows 23 development nodes in a seven-column layout. Jump
  must be the top skill in column 2 and own three independent paths: defensive
  Defend/Acrobat/Grounded Landing, independent middle Defense/Vigilant Landing
  and Attack nodes,
  and offensive Aerial Footwork/Quick Dive/Thrust/Rend. Polearm Proficiency
  must be the top skill in column 5, with two-point Polearm Excellence below
  it. Confirm Acrobat requires level 40, Thrust level 45,
  and Rend level 50.
  Confirm unbound Parry and True Strike occupy the final column and adopt
  retained ownership without another point.
- [ ] Confirm Promote: Dragoon in column 4 has a left connector running `Jump
  -> +20 Defense -> Vigilant Landing -> promotion` and separately requires
  two-point Polearm Excellence. It must also require global level 60, `STR 17`,
  and `DEX 13`, but neither optional modifier branch. The Vigilant Landing
  connector must descend in column 2 and must not pass behind Thrust or Rend.
- [ ] After promotion, verify Dragoon shows the same 23 Lancer nodes in the
  same positions, omits only Promote: Dragoon, and adds all 11 Dragoon nodes.
  Confirm prior purchases remain owned and every unpurchased Lancer node can
  still be purchased from the Dragoon tree. Confirm all three inherited Jump
  paths remain independent. Confirm Shield Block is absent because it was
  required on the Warrior-to-Lancer route.
- [ ] Confirm Polearm Proficiency in column 5 feeds Polearm Assault in column 4
  and Polearm Guard in column 6, while Parry/True Strike use column 7.
  Exercise Extended Reach, Swing & Bash, Phalanx, Critical
  Vigor, Dragon Soul, and Vigilant Landing. Confirm `+20 Attack` connects to
  Dragon's Ascent; Grounded Landing
  connects through Retribution and Unstoppable; and Rend connects through
  Quake and Soaring Strike. Dragon's Ascent must gate `+30 Defense`; that
  Defense node must not connect to Retribution.
  Dragon Dive must require Dragon's Ascent, Soaring Strike, and Unstoppable.
- [ ] Confirm Parry and True Strike occupy final-column rows 2 and 3. Confirm
  Dragoon extends column 5 with Attack and level-80 Polearm Mastery, adds
  two-point level-75 Dragonheart to Guard, and moves level-75 True Piercing Strike to
  column 7 behind True Strike. Vigilant Landing must also cost two points.
  Verify Dragon's Ascent has no separate level gate, Retribution requires 65,
  Unstoppable 70 and Dragon Dive 80.
- [ ] Confirm Lancer and Dragoon fit rows 0-7 without
  scrolling at the standard progression-screen resolution.
- [ ] Open the Aerial Tempo tab with every Jump modification unlocked. Confirm
  the tab explains how clean Jump landings build Tempo and how weapon actions
  spend it, displays every modification at once in two columns, and uses a
  compact selected-modification description panel without scrolling.
- [ ] Land clean and missed Jumps and verify each grants Tempo, consecutive
  Jumps stack to effective caps 3/4, and interruptions grant none. Spend Tempo
  with eligible Sword/Polearm actions and verify misses consume, multi-hit
  actions pay once, Jump/Dragon Dive do not double-dip, and Dragoon applies
  two-turn Speed pressure.
- [ ] Use Lance Sweep and Dragon Dive at their locked MP, weapon, Tempo,
  damage, and accuracy values. With awakened/equipped Aerial Supremacy, verify
  `+8%/+4` per-stack payoff tuning and a real two-turn 15% Landing Shield that
  refreshes to the larger value, absorbs damage, and expires. Confirm a
  dormant/unequipped or legacy `+1 Jump Mod` ring grants no extra capacity.
- [ ] Verify Sentinel has 24 development nodes across six columns, all shifted
  down one row, plus Promote: Stalwart Defender at `(2, 8)`. Confirm Assault, Bulwark, Resistance, and
  Support gates; Adrenaline's split; and independent inherited Goad, Charge,
  and Double Strike. Any one of the four level-55 talents must qualify.
- [ ] Promote for three points at level 60 with `CON 20`. Confirm unpurchased
  Sentinel nodes close and the Stalwart tree contains exactly 20 development
  nodes across Assault, Bulwark, Resistance, and Support in rows 1-6. Confirm
  every column is a continuous prerequisite chain, including Repercussion to
  Focused Assault, Hold the Line to Brace Wall, Spell Block to Bulwark Guard
  to Spell Reflection, and Purge Weakness to Boast. Confirm Punishing Guard,
  Unbroken Wall, Fortified Citadel, and Final Redoubt cost two points.
- [ ] Build Resolve from Defend, blocks, physical damage after mitigation,
  Goad, and Hold the Line. Verify caps 50/100, no duplicate ring gain, legacy
  `guard_meter` load compatibility, full-bar major-hit reduction, mastery
  persistence, and immediate access to all four full-bar Bursts.
- [ ] Exercise all eight Resolve actions in the 4-by-2 class-tab grid. Verify
  Spell Block scales with spell/shield strength, Shielding Ward halves the
  remainder, passive Spell Reflection can return blocked damage, and Mirror
  Bastion grants `+50 Magic Defense`.
- [ ] Exercise Citadel Aegis at 50% magic absorption, three/four-hit Ironwall
  Revenge, Last Bastion, and Stronghold's 30% melee/block modifiers. Verify
  Fortified Citadel, Crushing Vengeance, Double Payback, Iron Maiden,
  Punishing Guard, Braggadocious, and Final Redoubt alter only their documented
  effects. Bursts must be absent from ordinary Specials and unlocked in the
  Resolve tab.
- [ ] Verify Paladin has 20 development nodes within rows 0-6 plus Promote:
  Crusader at `(2.5, 7)`. Confirm both Oath connectors descend to row 7 before
  joining the promotion. Confirm ungated Oath's Judgment `(1, 0)` splits into
  column-0 Double Strike/Attack/Tempered Conviction/True Strike and column-2
  Smite/Repel the Wicked/Magic/Hallowed Ground. Confirm ungated Oath's Shelter
  `(4, 0)` splits into column-3 Heal/MP/Sworn Purpose/Blessed Light and
  column-5 Bless/Magic Defense/Defense/Divine Protection. Resist Shadow must
  sit at `(3, 4)` with level 45 and Parry must sit at `(5, 3)`.
  Confirm Bless connects to Magic Defense while Magic Defense gates Parry and
  Parry gates Defense. Divine
  Protection must sit at `(5, 5)` with level 50. Verify promotion accepts either Oath root,
  then complete the six Human stat increases, promote for three progression
  points, and confirm 14 progression points and nine attribute points remain
  on the shortest route before all unpurchased Paladin nodes close.
- [ ] Purchase level-55 Blessed Light beneath Sworn Purpose. Successfully cast
  a healing spell during combat and verify `+10 Attack` for three turns;
  repeat the heal to refresh rather than stack. Confirm zero healing,
  non-healing spells, and out-of-combat healing do not trigger it.
- [ ] Cast Hallowed Ground for 20 MP and verify all nearby enemies take Holy
  damage while the caster heals on each of three turns. Cast Resist Shadow
  outside battle for 15 MP and verify 50% Shadow resistance lasts for 100
  steps of game time, survives combat cleanup, expires naturally, and never
  appears in either frontend's combat spell selector.
- [ ] Verify Crusader has 23 nodes and uses rows 0-7 for ungated through level
  95. Confirm the two melee style entries cost two points. Exercise Censure
  against a charging enemy and Shield Ricochet against multiple enemies. Verify
  `Repel the Wicked -> Smite II -> Sanctification -> Smite III`, including the
  50% Holy bonus and level-90 Smite III; verify `Dispel -> Cleanse -> Heal II ->
  Prayer of Faith`, including all three below-10%-HP outcomes. Confirm an
  inherited middle-path ability does not unlock its successor until the full
  preceding path is purchased.
- [ ] Cast Repel the Wicked on fiends and undead. Confirm failure leaves the
  target in combat, ordinary success makes it flee without kill rewards, and a
  successful cast against a Condemnation-marked target disintegrates it.
- [ ] For every vow, gain Conviction from a valid signature action and its
  clean outcome. Verify effective Paladin/Crusader caps 3/4, cleanup rules, and
  no automatic spending by Redeem, Challenge, Interpose, or Judgment Riposte.
- [ ] Use Oath's Judgment and Oath's Shelter for all four vows. Verify
  validation precedes spending, Judgment misses still consume, MP and Silence
  do not block either action, every locked damage/heal/barrier/rating/counter
  value applies, and the menus show current vow and all-stack cost.
- [ ] Verify Righteous Advance adds `0.10x` and 25% Judgment rider scaling,
  Consecrated Bulwark adds one turn and 25% Shelter scaling, and
  awakened/equipped Vow Affirmation preserves one Conviction only once per
  combat after a primary effect succeeds without removing mark penalties.
- [ ] Spend a successful distribution and verify no `You spent X points`
  popup appears. When that distribution promotes into a class with a mechanic
  tab, verify the new tab appears without leaving the Character Menu.
- [ ] Verify Dishearten reduces melee damage dealt by 25% for three turns, Chastise
  increases Shield Slam damage by 25%, and Retaliate triggers after blocks.
- [ ] Trigger Adrenaline below 10% health and verify it restores up to 20% of
  maximum HP; verify it does nothing at or above 10%. Confirm Honed Attack
  increases only the bonus portion of weapon critical damage by 25%.
- [ ] Gain enough XP for several levels at once. Verify the creation
  progression point, another at level 2, then one at each even level. Verify a
  separate stored attribute point at every fourth level and confirm neither
  currency forces an immediate selection popup.
- [ ] Stage and remove an attribute, ordinary ability, upgrade, and rating node
  in Pygame. Verify no character state changes before Spend, the entire
  valid distribution commits atomically, combat-rating details say they are
  permanent, attributes consume only attribute points, nodes consume only
  progression points, a first promotion consumes two progression points, and
  a second promotion consumes three.
- [ ] Compare promotion previews and applied combat bonuses. First-promotion
  Attack/Defense/Magic/Magic Defense bonuses must be `2x` class values and
  second-promotion bonuses `3x`; primary and HP/MP bonuses remain unscaled.
- [ ] Review every Paladin vow in Pygame. Confirm the selector preserves
  its background, documents the learned signature ability, Aura benefits, and
  Mark trigger/drawback, and requires confirmation before committing.
- [ ] Use Reset and verify all distributed-but-unspent nodes and attributes
  clear immediately. Stage a promotion and press Spend; verify a confirmation
  describes its class benefits, requirements, equipment conflicts, and branch
  closure before any points are committed.
- [ ] Attempt to leave Progression with staged changes. Cancel once and verify
  the distribution remains; confirm once and verify it is discarded without
  spending any points.
- [ ] Open Progression from the Character Menu tab and confirm it is absent
  from the Town menu. Selecting a blocked node must not open a confirmation.
- [ ] Preview and cancel a promotion; confirm nothing changes. Then promote
  and verify global level/XP and learned abilities remain, illegal gear is
  removed, special class choices initialize, and the old branch becomes
  read-only.
- [ ] Verify Church retains saving, quests, rites, vows, and contracts but no
  longer offers Promotion.
- [ ] Save/load a new character and verify exact progression state. Attempt a
  version-4 save and verify the explicit unsupported-version message.
