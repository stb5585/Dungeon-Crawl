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
- [ ] Verify Mage, Footpad, Healer, and Pathfinder expose their four authored
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
  spending another point, and that both entries and all combat-rating nodes
  have no level requirement. Verify rating nodes grant `+10`, `+20`, and `+30`
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
- [ ] Verify Lancer shows 16 development nodes in a six-column layout. Jump
  must be the top skill in column 2 and own three independent paths: defensive
  Defend/Acrobat/Grounded Landing, middle `+20 Defense`/`+20 Attack`/promotion,
  and offensive Aerial Footwork/Quick Dive/Thrust/Rend. Polearm Proficiency
  must be the top skill in column 5 with Lance Sweep, `+50 HP`, and
  Zephyrstrike below it. Confirm Acrobat requires level 40, Thrust level 45,
  and Rend level 50.
  Confirm unbound Parry and True Strike occupy the final column and adopt
  retained ownership without another point.
- [ ] Confirm the connector to Promote: Dragoon follows Jump through both
  middle rating nodes. It must also require global level 60, `STR 17`, and
  `DEX 13`, but neither optional modifier branch.
- [ ] After promotion, verify Dragoon shows the same 16 Lancer nodes in the
  same positions, omits only Promote: Dragoon, and adds all 11 Dragoon nodes.
  Confirm prior purchases remain owned and every unpurchased Lancer node can
  still be purchased from the Dragoon tree. Confirm all three inherited Jump
  paths remain independent. Confirm Shield Block is absent because it was
  required on the Warrior-to-Lancer route.
- [ ] Confirm Polearm Excellence is ungated at row 5 and connects through
  `+30 Attack` to True Piercing Strike, with a second connector from True
  Strike. Confirm `+20 Attack` connects to Dragon's Ascent; Grounded Landing
  connects through Retribution and Unstoppable; and Rend connects through
  Quake and Soaring Strike. Dragon's Ascent must gate `+30 Defense`; that
  Defense node must not connect to Retribution.
  Dragon Dive must require Dragon's Ascent, Soaring Strike, and Unstoppable.
- [ ] Confirm Parry and True Strike occupy final-column rows 2 and 3. Confirm
  all new Dragoon nodes except Polearm Excellence are shifted down one row.
  Verify Dragon's Ascent has no separate level gate, Retribution requires 65,
  True Piercing Strike and Unstoppable 70, and Dragon Dive 80.
- [ ] Confirm Lancer remains within rows 0-6 and Dragoon fits rows 0-7 without
  scrolling at the standard progression-screen resolution.
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
- [ ] Verify Sentinel has 16 development nodes within rows 0-5 plus Promote:
  Stalwart Defender at `(1, 6)`. Confirm Counter, Wall, and Anti-magic
  prerequisites and level gates; Shield Block must be absent, while known Goad
  and Retaliate adopt without another point.
- [ ] Complete the ten-node Sentinel core, raise a Human's Constitution once,
  and promote for three points at level 60. Confirm four points remain,
  unpurchased Sentinel nodes close, learned nodes remain, and the Stalwart tree
  contains exactly 11 new development nodes within rows 0-3.
- [ ] Build Resolve from Defend, blocks, physical damage after mitigation,
  Goad, and Hold the Line. Verify caps 50/100, no duplicate ring gain, legacy
  `guard_meter` load compatibility, full-bar major-hit reduction, mastery
  persistence, and Surge thresholds 0/4/8.
- [ ] Prepare Spell Reflection for 25 Resolve. Verify a compatible hostile
  targeted spell reflects once across both legacy and data-driven execution;
  generic Reflect has priority, beneficial/area/unreflectable spells do not
  consume it, Mirror Bastion grants 20 Resolve and `+6 Magic Defense`, and
  expiry/combat/save/death/class cleanup works.
- [ ] Exercise Fortified Citadel at barrier 125/four turns, Crushing Reprisal
  at `1.60x` with two-turn `-3 Attack/-3 Speed`, and Final Redoubt at 40%
  healing/barrier 75/three turns. Verify Punishing Guard, Unbroken Wall,
  Watchful Reprisal, and Resolute Guard only alter their documented effects.
- [ ] Verify Paladin has 20 development nodes within rows 0-6 plus Promote:
  Crusader at `(2.5, 7)`. Confirm both Oath connectors descend to row 7 before
  joining the promotion. Confirm ungated Oath's Judgment `(1, 0)` splits into
  column-0 Double Strike/Attack/Tempered Conviction/True Strike and column-2
  Smite/Repel the Wicked/Magic/Hallowed Ground. Confirm ungated Oath's Shelter
  `(4, 0)` splits into column-3 Heal/MP/Sworn Purpose/Blessed Light and
  column-5 Bless/Magic Defense/Defense/Divine Protection. Resist Shadow must
  sit at `(3, 4)` with level 45 and Parry must sit at `(5, 3)`.
  Confirm Magic Defense and Resist Shadow have no connectors from Oath's
  Shelter, while Magic Defense gates Parry and Parry gates Defense. Divine
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
- [ ] Verify Crusader has exactly 19 new nodes within rows 0-5, grouped as
  Melee, Spells, Healing, and Protection. Confirm Condemnation is ungated and
  splits into mutually exclusive Two-Handed Weapon Proficiency and Sword &
  Board paths. Verify the two-handed route reaches level-75 Mortal Strike then
  Righteous Advance, while Sword & Board reaches level-70 True Piercing Strike
  then level-85 Triple Strike. Confirm no True Strike prerequisite or node and
  no Turn Undead II node remain. Verify Smite II -> Smite III and Heal II ->
  Cleanse -> Dispel replacements, retained-or-purchased Repel the Wicked in
  the Spells path, plus Consecrated Bulwark -> Parry ->
  Posturing protection training.
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
  in both frontends. Verify no character state changes before Spend, the entire
  valid distribution commits atomically, combat-rating details say they are
  permanent, attributes consume only attribute points, nodes consume only
  progression points, a first promotion consumes two progression points, and
  a second promotion consumes three.
- [ ] Compare promotion previews and applied combat bonuses. First-promotion
  Attack/Defense/Magic/Magic Defense bonuses must be `2x` class values and
  second-promotion bonuses `3x`; primary and HP/MP bonuses remain unscaled.
- [ ] Review every Paladin vow in both frontends. Confirm the selector preserves
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
