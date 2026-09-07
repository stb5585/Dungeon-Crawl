# Promotion Ability-Tree Rules

Promotion is a permanent purchase in the current class ability tree: two
points for a first promotion and three points for a second promotion.
`src/core/progression.py` is the runtime authority and
`src/core/progression_manifests/` owns authored paths, icon semantics, stage
sizes, and structured stat groups. Trees may have multiple independent
first-tier nodes; there is no mandatory lineage root.

All 49 registered classes have structurally declared, mechanically authored
paths. Compact trees are intentional where a class also gains a broad external
repertoire; they are not catalog-only placeholders. Generated rating families,
generic meter-cap padding, and invented node-count targets remain prohibited.

Footpad, Healer, and Pathfinder use authored joined base routes rather than one
universal eight-point budget. Footpad combines an identity track with Control
or Defense for a 13-point route including promotion. Healer's Bard, Cleric,
and Priest routes cost 14 while Monk costs 8. Pathfinder routes cost 11-14.
Their promotion prerequisites follow the authored ability lanes, and no minimum
node count is manufactured.

Bonded Bulwark raises bond-derived companion combat scaling from
15% to 25% at full bond. This declarative `kit_effect` payload is validated
with the tree manifest and does not add a generic stat rating.

Flat progression intentionally retains every already learned spell and skill
through every promotion. This includes off-identity abilities such as magic on
Monk or Ranger and stealth on Inquisitor. Special promotion initialization may
add mandatory abilities, but it may not delete or replace an existing
spellbook entry. Class identity comes from the new tree, mechanics, stats, and
equipment restrictions rather than destructive ability pruning.

Death Mark is the exception: Assassin has one target-specific mark and Ninja
has three. Capacity is fixed; Ninja progression improves setup, payoff,
coatings, concealment, and defensive play instead of adding more stacks.

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

Permanent stat gates of 10 or lower are omitted from promotion nodes because
they do not represent meaningful specialization beyond an ordinary baseline.
This normalization applies to both first and second promotions after authored
class-specific overrides are resolved.

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
`14/12/11`, Lancer Strength to `13`, Sentinel Constitution to `15`, and
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

- Sorcerer, five points on an Elemental route or six on the Arcane route: buy
  either an elemental spell, its Enhancement, and Classical Force, or `Magic
  Missile -> Guidance Upgrade -> Mana Rupture -> Arcane Tradition`, then the
  two-point promotion. Classical Force and Arcane Tradition are mutually
  exclusive and Spend Distribution warns before the competing specialization
  closes.
- Spellblade, eight points:
  `Magic Missile -> Guidance Upgrade -> Mana Rupture -> Polymorph -> Mana Shield
  -> Imbue Weapon -> Promote: Spellblade`.
- Warlock, eight points:
  `Enfeeble -> Blinding Fog -> Shadow Bolt -> Inflate Health -> Enliven Dead
  -> Forbidden Studies -> Promote: Warlock`.
- Conjurer, eight points:
  `Conjure Blade -> +25 MP -> Conjure Animal -> Binding Circle -> Conjure
  Shackles -> Conjure Potion -> Promote: Conjurer`.

All four promotions require level 30 and two points. Stat gates are Sorcerer
`INT 15/WIS 13`; Warlock `INT 13/CHA 14`; Spellblade
`CON 11/INT 13/CHA 12`; and Conjurer `CHA 12/INT 13/WIS 12`. Requirements of
10 or lower are omitted; Spellblade and Conjurer have no Strength requirement.

Learned Mage spells survive every promotion. Unpurchased Mage nodes and
competing promotions close. Sorcerer replaces the old Mage carry-forward with
affinity-gated tier-two elemental and Arcane spell nodes. The historical Mage
tab is read-only. Conjurer has an authored four-discipline tree: Constructs, Binding,
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
nodes in four centered rows. Its four development columns are Heavy Weapons,
Two-Weapon Assault, Fury, and Survival. Promotion-level roots are Monkey Grip,
Mortal Strike 2, Frenzy, and inherited-or-purchased Parry. Heavy Weapons adds
Momentum, Tectonic Rift, and Monkey Grip 2. Two-Weapon Assault adds Boomerang
Toss, `+30 Attack`, Thunderous Vault, and Triple Strike. Fury adds Hemorrhage
Thirst, Fatality, and Composed Wrath. Survival adds Pain Tolerance, Final
Assault, and Reckless Onslaught. Final Assault and Reckless Onslaught are
compatible; neither replaces the other. Hemorrhage Thirst converts enemy
bleed-tick damage into equal healing, and a third consecutive-turn trigger
makes the Berserker unconscious for two turns before resetting the streak.

Grandmaster of Arms exposes all 16 inherited rank-1/rank-5 nodes plus eight
rank-10 level-3 replacements. Its six-column mastery route runs from ungated
Double Strike through level-65 Dual Wield Excellence and Weapon Swap, forks to
level-75 Perfect Form and Adaptive Arsenal, and rejoins at level-80 Dual Wield
Mastery.

Lancer uses three independent paths below Jump and two polearm development
line. The defensive path is `Defend -> Acrobat -> Grounded Landing`; the
middle nodes are `+20 Attack` directly below Jump and `+20 Defense -> Vigilant
Landing`; and the
offensive path is `Aerial Footwork -> Quick Dive -> Thrust -> Rend`. Polearm
Proficiency sits in column 5 and feeds the authored Assault and Guard
paths. Ungated inherited-or-purchased True Strike occupies the final column;
Parry is absent. Modifier nodes never create spellbook entries.
Acrobat unlocks at level 40, Thrust at level 45, and Rend at level 50.
Polearm Excellence requires Polearm Proficiency directly. Promote: Dragoon in
column 4 requires both Vigilant Landing and Polearm Excellence, plus global
level 60, `STR 17`, and `DEX 13`; its left connector therefore runs from Jump
through Defense and Vigilant Landing, then descends in that column before
turning into promotion rather than crossing Thrust or Rend. Neither optional
modifier path is required.

Dragoon retains all 22 Lancer development nodes in the same positions and adds
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

Sentinel uses five authored columns. Assault and Bulwark occupy columns 1 and 2;
Adrenaline at column 3.5 splits into Resistance and Support in columns 3 and 4.
Parry is absent; Goad, Charge, and Double Strike remain disconnected in column
5 at rows 3-5. The level-60 Stalwart Defender promotion at `(1.5, 8)`
accepts Watchful Reprisal, Resolute
Guard, Shielding Ward, or Braggadocious and otherwise retains `CON 20` and its
three-point cost.

Stalwart Defender contains 25 nodes across Assault, Bulwark, Shield Offense,
Resistance, and Support. The new third column runs from Retaliate through
Shield Ricochet, Tower Offense, Get Even, and Generator Shield. Its full-bar
Bursts are Citadel Aegis, Ironwall Revenge, Last Bastion,
and Stronghold. Each remains locked until its persistent mastery track records
four qualifying uses of associated barrier, counter, survival, or fortress
actions; qualifying Sentinel use carries into Stalwart Defender. Count mastery
at most once per action or defensive event. Learned Bursts remain out of the
ordinary Specials list. Point-purchased talents modify those Bursts and the
eight inherited Resolve actions. Support replaces its HP node with Battle Cry
and continues through Battle Determination to level-80 Final Redoubt. The tree
occupies rows 1-6; Punishing Guard, Double Payback, Unbroken Wall, Iron Maiden,
Fortified Citadel, and Final Redoubt cost two points. Runtime stores four capped
mastery tracks, credits their associated actions or defensive events at most
once, carries progress through promotion and save/load, and keeps exact progress
hidden until each Burst is discovered.

Paladin begins with independent ungated Oath's Judgment `(1, 0)` and Oath's
Shelter `(4, 0)` roots. Judgment branches through the column-0 `Double Strike
-> +20 Attack -> Tempered Conviction -> True Strike` path and the column-2
`Smite -> Detect Undead -> Repel the Wicked -> +20 Magic -> Detect Fiend ->
Hallowed Ground` path. Shelter branches
through column 3's `Heal -> +50 MP -> Resist Shadow -> Sworn Purpose -> Blessed
Light` and column 5's Bless branch. Tempered Conviction grants `+20%
Defense` and one Conviction capacity;
Sworn Purpose grants `+20% Magic` and `+20% Magic Defense`. Blessed Light turns
successful combat healing spells into a three-turn `+10 Attack` buff. The
level-60 Crusader promotion is centered at `(2.5, 7)`, requires either Oath
root, `STR 15`, `CON 17`, `WIS 16`, `CHA 13`, and three progression points.
Its two prerequisite connectors descend to the promotion row before joining.
Six required Human attribute increases use the separate attribute pool,
leaving 14 progression points and nine attribute points on the shortest route.

Crusader contains 26 nodes across Melee, Spells, Healing, and Protection, using
the standard tier-3 row gates from ungated through level 95. Ungated
Condemnation splits into mutually exclusive, level-65 two-point Two-Handed
Weapon Proficiency and Sword & Board styles; Beyond Reproach separately
unlocks Condemnation marking. The two-handed route ends in Penalization, while
the shield route adds Censure, Shield Ricochet, and level-75 True Piercing
Strike. Spells run from retained Repel the Wicked through Smite II,
Sanctification, Undead Hunter, and level-90 Smite III. Healing runs from
ungated Dispel through Cleanse, Heal II, Radiant Healing, and two-point Prayer
of Faith. Ungated Parry follows Two-Handed Weapon Proficiency. Protection runs
from inherited-or-purchased Divine Protection through Posturing, Consecrated
Bulwark, and replacing Divine Protection II.
Penalization, Smite III, and Divine Protection II cost two points.
Known inherited nodes remain owned but do not satisfy downstream nodes until
their preceding path is purchased. Unpurchased Sentinel and Paladin nodes close
at promotion; all already learned actions, talents, Resolve mastery progress,
and the permanent Paladin vow remain.

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

Mage-to-Sorcerer and Sorcerer-to-Wizard retain learned abilities in the
spellbook, but their current trees do not repeat unpurchased Mage roots.
Tier-two and tier-three elemental spells instead use their matching School
Affinity gates.

Cancellation changes nothing. An exception during application restores the
snapshotted class, stats, resources, combat ratings, equipment, inventory,
spellbook, companions, summons, and progression state.

## Retired Behavior

Promotion never resets a local class level, prunes abilities, or grants the
new class's former level-one catalog entries. The obsolete promotion-pruning
rule table and compatibility helper have been removed. Church no longer offers
class promotion, and its unreachable learn-as-you-level promotion handler has
also been removed.

## Ability Retention and Upgrades

Purchased abilities stay active across promotions. Upgrade nodes require the
earlier ability and replace it atomically in the active spellbook. Quest,
Class Ring, Power Core, vow, contract, summon-bond, and Weapon Discipline
rewards remain owned by their existing systems and do not become tree nodes.
