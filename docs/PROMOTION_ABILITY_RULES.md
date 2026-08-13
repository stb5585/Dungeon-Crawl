# Promotion Ability-Tree Rules

Promotion is a permanent purchase in the current class ability tree: two
points for a first promotion and three points for a second promotion.
`src/core/progression.py` is the runtime authority and
`src/core/progression_manifest.py` owns authored paths, icon semantics, stage
sizes, and structured stat groups. Trees may have multiple independent
first-tier nodes; there is no mandatory lineage root.

All 49 registered classes now use authored paths. Named talent nodes are
permanent purchases that may grant a small combat bonus and modify a
class-specific meter cap without adding a fake ability to the spellbook.
Their stable keys are part of the version-5 save contract.

Progression bonuses use one shared tier scale. Attack, Defense, Magic, and
Magic Defense nodes grant `+10/+20/+30` on base, first-promotion, and terminal
trees; HP and MP nodes grant `+25/+50/+100`. Named class talents use that same
rating amount for every rating they improve, in addition to their bespoke
mechanic.

Any staged purchase that would permanently close another node or descendant
path requires a generic `Spend Distribution` confirmation. The warning names
every newly closed ability before the distribution commits; canceling leaves
the pending distribution intact and spends nothing. This rule applies to all
current and future exclusive paths, not only Mage specializations.

## Eligibility

A promotion node is available only when:

- every declared path and cross-path prerequisite is owned (an authored
  either/or join may accept one of multiple prerequisites);
- global level 30 is reached for a first promotion, or level 60 for a second;
- the target class's permanent primary and secondary stat requirements pass;
- the player's race allows the first-promotion target; and
- two progression points are available for a first promotion, or three for a
  second promotion.

An ability's authored level gate is ignored and hidden when it is lower than
the level required to enter the class whose tree currently displays it. This
is a universal promoted-tree rule: the promotion itself has already satisfied
that gate. The same carried ability retains its original gate in an earlier
tree where the requirement is not redundant.

Equipment and temporary transformations do not satisfy stat requirements.
Authored target-specific overrides may balance the total cost of a complete
path. Warrior's Weapon Master and Lancer routes share `Piercing Strike ->
Charge -> Weapon Focus` before splitting. Charge is level 5, Weapon Focus is
level 10, and the Weapon Master `+10 Attack` node sits opposite Driving
Thrust. The tree sets Weapon Master Strength/Dexterity/Intelligence to
`15/12/11`, Lancer Strength to `13`, Sentinel Constitution to `16`, and
Paladin Wisdom to `13`; all four first-promotion routes cost 13 points from
the baseline Human Warrior under the former combined-budget accounting. With
separate currencies, Weapon Master/Sentinel/Paladin each cost eight progression
and five attribute points, while Lancer costs ten progression and three
attribute points.

Other route-specific gates follow the same eventual-affordability contract
rather than forced symmetry. Level 30/60 is a minimum gate; a character whose
race/class starting attributes need more stored training may satisfy the stat
gate at a later fourth-level attribute award.

Mage is the second bespoke base graph and uses six columns. All six elemental
spells are independent level-1 roots in column 0; their matching level-20
Enhancements occupy column 1. Arcana, Occultism, and Conjuration are six-node
paths in columns 2-4. Reflect/Sleep/Boost/Mirror Image are independent
level-10/15/20/25 Universal nodes in column 5.

- Sorcerer, five points: buy either an elemental spell, its Enhancement, and
  Classical Force, or `Magic Missile -> Arcane Fundamentals -> Arcane Tradition`,
  then the two-point promotion. Classical Force and Arcane Tradition are mutually
  exclusive and Spend Distribution warns before the competing specialization
  closes.
- Spellblade, eight points:
  `Magic Missile -> Arcane Fundamentals -> +25 MP -> Polymorph -> Mana Shield
  -> Imbue Weapon -> Promote: Spellblade`.
- Warlock, eight points:
  `Enfeeble -> Blinding Fog -> Shadow Bolt -> Inflate Health -> Enliven Dead
  -> Forbidden Studies -> Promote: Warlock`.
- Conjurer, eight points:
  `Conjure Blade -> +25 MP -> Conjure Animal -> Binding Circle -> Conjure
  Shackles -> Conjure Potion -> Promote: Conjurer`.

All four promotions require level 30 and two points. Stat gates are Sorcerer
`INT 15/WIS 13`; Warlock `INT 14/CHA 14/WIS 10/CON 10`; Spellblade
`STR 10/CON 11/INT 14/CHA 12`; and Conjurer
`CHA 13/INT 13/WIS 12/CON 10/DEX 10` with no Strength requirement.

Learned Mage spells survive every promotion. Normally, unpurchased Mage nodes
and competing promotions close. Mage-to-Sorcerer remains a partial exception:
Arcane Fundamentals and the six elemental spells keep their Mage IDs and
remain purchasable in Sorcerer and Wizard. The historical Mage tab is
read-only. Conjurer has an authored four-discipline tree: Constructs, Binding,
Illusion/Movement, and Calling. Its level-60 three-point Thaumaturgist
promotion accepts Barrier Wall, Mana Barbs, Explosive Decoy, or Conjure Dragon.
As Conjurer, each Calling selects a standard enemy of its category nearest the
current location and creates a 50-step transient companion; it does not create
or select a Xenid. Conjure Animal plus all six Calling nodes appear in the
editable Thaumaturgist tree. Each Calling connects to a permanent choice
between two Xenids and then an ultimate unlock for that chosen Xenid.
The roster is fixed to 14 declared names, including Animal pair
Hodag/Caladrius. Thaumaturgist combines the former Summoner and Grand Summoner
permanent-roster tiers, but replaces summon XP with conduit-driven stats and
ability acquisition. Chosen Xenids also shape caster progression through
themed reciprocal effects; Conduit Mastery amplifies those effects. No direct
permanent-summon system is inherited at the Mage-to-Conjurer promotion.

Spellblade uses Weapon Enhancements, Armor Enhancements, Spell Enhancements,
and Universal / Extra Abilities. Its level-60, three-point Knight Enchanter
promotion accepts Enhance Blade, Enhance Armor, or Storage Capacity at row 8.
Imbue Weapon is already required to become a Spellblade and has no repeated
Spellblade node. Counter Charge, Reflect, and Boost share ungated row 2. True
Strike, Parry, and Double Strike occupy levels 35, 40, and 45. Reflect, Boost,
True Strike, Parry, and Double Strike adopt prior ownership without backfilling
their prerequisites. Knight Enchanter requires `STR 16/CON 16/INT 15/DEX 11`
and has no Charisma requirement. Mana Tap and Enhance Armor remain in
Knight Enchanter as catch-up purchases and become automatically owned there
when already learned as Spellblade. Knight Enchanter's four authored columns
organize Assault, Aegis, Spellbind, and independent universal talents. Quick
Recharge, Third Eye, and Storage Capacity II cost two points; every other node
costs one. Third Eye is a level-70 Aegis option that adds
Intelligence to critical-hit and dodge calculations. Storage Capacity II adds
two slots to each typed charge pool and stacks with Storage Capacity. Aegis
Weave and Spellbind consume the same typed Blade Charges as Enchanted Assault
and never create a second class resource.

Thaumaturgist compresses this terminal graph into five columns by adding a
four-node Miracles lane beside Calling, paired choice, ultimate, and conduit
development. `Miracle Blade (65) -> Miracle Shackles (70) -> Miracle Potion
(75) -> Miracle Crystal (80)` each consume a `Reality Fragment` and deliberately
break one ordinary combat or inventory rule. The former `Summon`/`Summon 2`
passive nodes no longer exist; a Thaumaturgist with a living Xenid receives the
combat Summon action from class state. A Xenid death removes 25 conduit, while
the 100-MP, combat-only `Raise Summon` restores only the just-fallen active
Xenid at 25% HP and refunds 10 of that loss.

Weapon Master is intentionally asymmetric. Double Strike and Parry entry nodes
have no global-level gate and adopt retained Warrior ownership without charging
again. Numeric rating, HP, and MP nodes normally have no independent level
gate; prerequisites alone unlock them. Spellblade's level-band layout is the
explicit exception, so its row-4 Magic and row-5 Defense ratings enforce levels
40 and 45. Ratings scale by tree tier: `+10` in base trees, `+20` in
first-promotion trees, and `+30` in terminal trees. New
class-specific nodes must include at least one basic class mechanic; do not add
new class-specific nodes whose entire identity is a plain numeric stat or
resource increase. The Grandmaster route permanently closes either Dual Wield or
Duelist when the competing style is chosen, and True Piercing Strike accepts
the terminal node from either style. Each independent weapon art checks
matching Weapon Discipline rank 1; its child upgrade checks rank 5 and replaces
the lower form. These art nodes have no global-level gate. Reaching either rank
makes the corresponding node purchasable but never grants it automatically.
The Berserker route places level-35 Two-Handed Weapon Proficiency between
Attack and Mortal Strike, with a visual gap before level-45 Mortal Strike. The
Grandmaster style gates are Dual Wield/Duelist at 35, Honed Attack/Blind
Fighting at 40, Momentum/Retort at 45, Cross Block/Maim at 50, and True
Piercing Strike at 55. Selecting Dual Wield or Duelist permanently closes every
descendant on the competing path, not only its entry node.

Berserker exposes only two-handed disciplines and owns eight rank-1/rank-5 art
nodes in four centered rows. Final Assault and Frenzy are immediately available
after promotion, because the promotion itself enforces level 60. Its left paths
include terminal-tier `+30 Attack` and `+100 HP` development nodes; the center
column contains inherited Parry, level-65 Pain Tolerance, and level-70
Hemorrhage Thirst. Hemorrhage Thirst converts enemy bleed-tick damage into
equal healing; triggering on a third consecutive enemy turn makes the Berserker
unconscious for two turns and resets the streak. Level-70 Reckless Onslaught
sits between `+30 Attack` and Monkey Grip 2 in the Survival path, replaces Final
Assault, and stacks its Attack-up and Defense-down tradeoff when refreshed.
Both left paths use five vertically centered rows, while the center column uses
three.

Grandmaster of Arms exposes all 16 inherited rank-1/rank-5 nodes plus eight
rank-10 level-3 replacements. Ungated Double Strike sits between Perfect Form
and Adaptive Arsenal in the fourth column. Both floating talents have no level
gate and scale from the currently equipped weapon's discipline.

Lancer uses three independent paths below Jump and two polearm development
line. The defensive path is `Defend -> Acrobat -> Grounded Landing`; the
middle nodes are `+20 Attack` directly below Jump and `+20 Defense -> Vigilant
Landing`; and the
offensive path is `Aerial Footwork -> Quick Dive -> Thrust -> Rend`. Polearm
Proficiency sits in column 5 and feeds the authored Assault and Guard
paths. Ungated inherited-or-purchased Parry and True
Strike occupy the final column. Modifier nodes never create spellbook entries.
Acrobat unlocks at level 40, Thrust at level 45, and Rend at level 50.
Polearm Excellence requires Polearm Proficiency directly. Promote: Dragoon in
column 4 requires both Vigilant Landing and Polearm Excellence, plus global
level 60, `STR 17`, and `DEX 13`; its left connector therefore runs from Jump
through Defense and Vigilant Landing, then descends in that column before
turning into promotion rather than crossing Thrust or Rend. Neither optional
modifier path is required.

Dragoon retains all 23 Lancer development nodes in the same positions and adds
11 class-specific nodes. The Lancer promotion node is the only omitted node.
The historical Lancer tab becomes read-only, but its purchased node IDs remain
owned and its unpurchased nodes remain editable in the Dragoon tree. The three
inherited Jump paths preserve the same independent prerequisites. Shield Block
is not repeated because reaching Lancer already requires it. Polearm
Proficiency sits in column 5, with Polearm Assault in column 4, Polearm Guard
in column 6, and universal attacks in column 7. Polearm Excellence (55) sits
under Proficiency as a direct dependency; Guard ends in Dragon Soul (50).
Vigilant Landing (45) follows Defense independently of Attack.
Dragoon extends column 5 through `+30 Attack -> Polearm Mastery (80)`, adds
Dragonheart (75) to Guard, and places level-75 True Piercing Strike in column 7
behind True Strike. The middle `+20 Attack` node
unlocks Dragon's Ascent, which has no separate level gate and gates
`+30 Defense`. Grounded Landing unlocks level-65 Retribution, which continues
to level-70 Unstoppable. Rend extends through Quake and Soaring Strike.
Level-80 Dragon Dive requires Dragon's Ascent, Soaring Strike, and Unstoppable.
Lancer and Dragoon use rows 0-7 without
progression-panel scrolling.

Sentinel uses six authored columns. Assault and Bulwark occupy columns 1 and 2;
Adrenaline at column 4.5 splits into Resistance and Support in columns 4 and 5;
Goad, Charge, and Double Strike are independent in column 6. Every node is
shifted down one row; the level-60 Stalwart Defender promotion at `(2, 8)`
accepts Watchful Reprisal, Resolute
Guard, Shielding Ward, or Braggadocious and otherwise retains `CON 20` and its
three-point cost.

Stalwart Defender contains 20 nodes across Assault, Bulwark, Resistance, and
Support. All nodes form continuous top-to-bottom prerequisite chains within
their four columns. Its full-bar Bursts are Citadel Aegis, Ironwall Revenge, Last Bastion,
and Stronghold; all four are immediately unlocked on promotion and remain out
of the ordinary Specials list. Point-purchased talents modify those Bursts and
the eight inherited Resolve actions. The tree occupies rows 1-6; Punishing
Guard, Unbroken Wall, Fortified Citadel, and Final Redoubt cost two points.

Paladin begins with independent ungated Oath's Judgment `(1, 0)` and Oath's
Shelter `(4, 0)` roots. Judgment branches through the column-0 `Double Strike
-> +20 Attack -> Tempered Conviction -> True Strike` path and the column-2
`Smite -> Repel the Wicked -> +20 Magic -> Hallowed Ground` path. Shelter branches
through column 3's `Heal -> +50 MP -> Resist Shadow -> Sworn Purpose -> Blessed
Light` and column 5's Bless branch. Magic Defense gates Parry at
`(5, 3)`, followed by `+20 Defense -> Divine Protection`. Tempered Conviction grants `+20
Defense` and one Conviction capacity;
Sworn Purpose grants `+20 Magic` and `+20 Magic Defense`. Blessed Light turns
successful combat healing spells into a three-turn `+10 Attack` buff. The
level-60 Crusader promotion is centered at `(2.5, 7)`, requires either Oath
root, `STR 15`, `CON 17`, `WIS 16`, `CHA 13`, and three progression points.
Its two prerequisite connectors descend to the promotion row before joining.
Six required Human attribute increases use the separate attribute pool,
leaving 14 progression points and nine attribute points on the shortest route.

Crusader contains 23 nodes across Melee, Spells, Healing, and Protection, using
the standard tier-3 row gates from ungated through level 95. Ungated
Condemnation splits into mutually exclusive two-point Two-Handed Weapon
Proficiency and Sword & Board styles. The shield route adds Censure, Shield
Ricochet, and the moved level-75 True Piercing Strike. Spells run from retained
Repel the Wicked through Smite II, Sanctification, and level-90 Smite III;
Healing runs from ungated Dispel through Cleanse, Heal II, and two-point Prayer
of Faith. Known inherited nodes remain owned but do not satisfy downstream
nodes until their preceding path is purchased. Unpurchased Sentinel and
Paladin nodes close at promotion; all already learned actions, talents, Resolve
mastery, and the permanent Paladin vow remain.

## Staging and Atomic Change

The Pygame frontend stages promotion nodes with other point purchases and commits the
distribution through one Spend action. Promotion details show the target,
requirements, and permanent branch-closure warning. Spending a distribution
containing a promotion opens a final benefit preview with its one-time bonuses
and equipment conflicts. Paladin vows and Warlock familiars are selected before
mutation.

A successful purchase:

- changes class without resetting global level, total XP, or XP carryover;
- applies the promoted class's one-time primary and resource bonuses, plus
  combat bonuses scaled to `2x` for first promotions and `3x` for second
  promotions;
- initializes vows, familiars, summons, contracts, teleport state, and other
  special class hooks in the same transaction;
- moves newly illegal gear to inventory;
- retains every learned spell and skill;
- marks the previous tree completed and read-only; and
- closes competing promotions and every unpurchased node in that tree.

Lancer-to-Dragoon is the explicit exception to the last rule: the old Lancer
tab is read-only, while the same development nodes remain available inside the
current Dragoon tree.

Mage-to-Sorcerer and Sorcerer-to-Wizard are the partial exception: old tree
tabs remain read-only, while Arcane Fundamentals and the six declared
elemental spell nodes remain available inside the current tree. Promotion
previews and results identify this partial carry-forward.

Cancellation changes nothing. An exception during application restores the
snapshotted class, stats, resources, combat ratings, equipment, inventory,
spellbook, companions, summons, and progression state.

## Retired Behavior

Promotion never resets a local class level, prunes abilities, or grants the
new class's former level-one catalog entries. `PROMOTION_ABILITY_RULES` and
`apply_promotion_ability_rules()` remain compatibility surfaces only; they are
not part of the canonical progression path. Church no longer offers class
promotion.

## Ability Retention and Upgrades

Purchased abilities stay active across promotions. Upgrade nodes require the
earlier ability and replace it atomically in the active spellbook. Quest,
Class Ring, Power Core, vow, contract, summon-bond, and Weapon Discipline
rewards remain owned by their existing systems and do not become tree nodes.
