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

## Eligibility

A promotion node is available only when:

- every declared path and cross-path prerequisite is owned (an authored
  either/or join may accept one of multiple prerequisites);
- global level 30 is reached for a first promotion, or level 60 for a second;
- the target class's permanent primary and secondary stat requirements pass;
- the player's race allows the first-promotion target; and
- two progression points are available for a first promotion, or three for a
  second promotion.

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

Weapon Master is intentionally asymmetric. Double Strike and Parry entry nodes
have no global-level gate and adopt retained Warrior ownership without charging
again. Combat-rating nodes also have no level gate in any tree and scale by
tree tier: `+10` in base trees, `+20` in first-promotion trees, and `+30` in
terminal trees. The Grandmaster route permanently closes either Dual Wield or
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

Lancer uses three independent paths below Jump and one polearm development
line. The defensive path is `Defend -> Acrobat -> Grounded Landing`; the
middle path is `+20 Defense -> +20 Attack -> Promote: Dragoon`; and the
offensive path is `Aerial Footwork -> Quick Dive -> Thrust -> Rend`. Polearm
Proficiency sits in column 5 and owns a single line through Lance Sweep,
`+50 HP`, and Zephyrstrike. Ungated inherited-or-purchased Parry and True
Strike occupy the final column. Modifier nodes never create spellbook entries.
Acrobat unlocks at level 40, Thrust at level 45, and Rend at level 50.
Promote: Dragoon additionally requires global level 60, `STR 17`, and
`DEX 13`; neither optional modifier path is required.

Dragoon retains all 16 Lancer development nodes in the same positions and adds
11 class-specific nodes. The Lancer promotion node is the only omitted node.
The historical Lancer tab becomes read-only, but its purchased node IDs remain
owned and its unpurchased nodes remain editable in the Dragoon tree. The three
inherited Jump paths preserve the same independent prerequisites. Shield Block
is not repeated because reaching Lancer already requires it. Ungated Polearm
Excellence starts the Dragoon polearm line at row 5 and connects into
`+30 Attack -> True Piercing Strike`; level-70 True Piercing Strike no longer
requires True Strike. The middle `+20 Attack` node
unlocks Dragon's Ascent, which has no separate level gate and gates
`+30 Defense`. Grounded Landing unlocks level-65 Retribution, which continues
to level-70 Unstoppable. Rend extends through Quake and Soaring Strike.
Level-80 Dragon Dive requires Dragon's Ascent, Soaring Strike, and Unstoppable.
Lancer fits in rows 0-6; Dragoon uses compact spacing across rows 0-7 without
progression-panel scrolling.

Sentinel uses three authored columns. Counter runs from ungated Goad through
level-35 Shield Check, level-40 Retaliate, level-45 Shield Riposte, and
level-50 Watchful Reprisal. Wall runs from ungated Hold the Line through Brace
Wall, Covering Guard, Bulwark, and level-50 Resolute Guard. Anti-magic runs
from ungated Deflect Spell to level-45 Spell Reflection and two optional
durability nodes. Goad and Retaliate adopt known ownership. The level-60
Stalwart Defender promotion requires Watchful Reprisal, Resolute Guard,
`CON 20`, and three points. Its ten-node Human core plus one Constitution
increase leaves four points.

Stalwart Defender contains 11 new development nodes and no inherited-tree
duplicates. Last Stand and Punishing Guard start independent defense and
counter paths. Fortified Citadel, Crushing Reprisal, and Final Redoubt are
point-purchased Surge modifiers; Citadel Aegis, Ironwall Reprisal, and Last
Bastion themselves remain mastery rewards at thresholds 0, 4, and 8 and are
granted as action wrappers during promotion. Mirror Bastion checks learned
Spell Reflection rather than requiring ownership of a closed Sentinel node.

Paladin begins with independent ungated Oath's Judgment `(1, 0)` and Oath's
Shelter `(4, 0)` roots. Judgment branches through the column-0 `Double Strike
-> +20 Attack -> Tempered Conviction -> True Strike` path and the column-2
`Smite -> Repel the Wicked -> +20 Magic -> Hallowed Ground` path. Shelter branches
through column 3's `Heal -> +50 MP -> Sworn Purpose -> Blessed Light` and
column 5's Bless branch. Magic Defense and level-45 Resist Shadow are detached
from the Oath's Shelter connector. Magic Defense instead gates Parry at
`(5, 3)`, followed by `+20 Defense -> Divine Protection`. Tempered Conviction grants `+20
Defense` and one Conviction capacity;
Sworn Purpose grants `+20 Magic` and `+20 Magic Defense`. Blessed Light turns
successful combat healing spells into a three-turn `+10 Attack` buff. The
level-60 Crusader promotion is centered at `(2.5, 7)`, requires either Oath
root, `STR 15`, `CON 17`, `WIS 16`, `CHA 13`, and three progression points.
Its two prerequisite connectors descend to the promotion row before joining.
Six required Human attribute increases use the separate attribute pool,
leaving 14 progression points and nine attribute points on the shortest route.

Crusader contains only its 19 new nodes across Melee, Spells, Healing, and
Protection. Ungated Condemnation splits into mutually exclusive Two-Handed
Weapon Proficiency and Sword & Board styles. The former continues through
`+30 Attack`, level-75 Mortal Strike, and Righteous Advance; the latter
continues through level-70 True Piercing Strike and level-85 Triple Strike.
True Piercing Strike has no True Strike prerequisite. Smite II/III and Heal II
retain replacement ownership. Repel the Wicked is retained or purchasable
from the Spells path without a Turn Undead II node. Consecrated Bulwark leads
through Parry and level-65 Posturing
to the protection ratings. Unpurchased Sentinel and Paladin nodes close at
promotion; all already learned actions, talents, Resolve mastery, and the
permanent Paladin vow remain.

## Staging and Atomic Change

Both frontends stage promotion nodes with other point purchases and commit the
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
