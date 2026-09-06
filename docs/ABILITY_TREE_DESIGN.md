# Authored Ability-Tree Design

## Runtime Contract

All 49 playable classes own a declarative tree in
`src/core/progression_manifest.py`. `src/core/progression.py` builds and
validates those declarations, applies purchases atomically, and remains the
public runtime facade for Pygame and headless validation.

Cross-reference diagrams for every playable class are indexed in
[`ability_trees/README.md`](ability_trees/README.md) and grouped by base-class
lineage, then base/first-promotion/second-promotion tier. They are generated from
the runtime graphs except for Mage's authoritative hand-routed connectors;
regenerate them after tree edits with
`./.venv/bin/python tools/generate_ability_tree_diagrams.py`. A regression test
fails if any generated diagram drifts from its class tree, while Mage is
checked for runtime-node coverage and preserved during regeneration.

Development nodes cost one point unless an authored advanced terminal talent
explicitly costs two. First promotions cost two points and second promotions
cost three. Rating nodes scale with their tree tier: base trees
grant `+10`, first-promotion trees grant `+20`, and terminal trees grant `+30`.
HP and MP nodes likewise scale by tier at `+25`, `+50`, and `+100`. These plain
rating and resource nodes are the only nodes that grant fixed stat amounts.
Named custom talents instead increase their affected ratings by `10%`, `20%`,
or `30%` according to tree tier, in addition to their class-specific effect,
without appearing in the spellbook. Active and passive ability nodes still
instantiate the canonical ability class.

Promotion prerequisites are rendered as gold connector paths. Requirements
that must all be purchased meet in the reserved buffer row before entering
through one top-edge stem. For `choose any one` promotions, the outermost
alternatives enter the promotion card from its left and right sides while any
interior alternatives retain separate top-edge stems. When one endpoint feeds multiple promotions, each edge
leaves from a distinct bottom anchor on that endpoint, preventing neighboring
promotion graphs from forming a shared visual bus. Long connections descend
through the gutter beside their source column instead of crossing unrelated
nodes. Trees that formerly used seven rows reserve an eighth row for promotion
routing; trees already using eight rows keep their authored geometry. Hovering
over a promotion highlights every node along its required paths in violet,
including available nodes, with brighter frames on the direct endpoints. Moving off the promotion
clears the highlight. The detail panel lists every endpoint by lane and node
name. In-game graph icons omit duplicate labels and rely on that detail panel
for the full name and description. SVG names truncate at 20 characters, while
non-Mana resource names use a separate third line below the ordinary node
metadata. Promotion cards reserve a second line for `Requires ALL/ANY`.

Ability milestones are global for gated abilities and talents. Rating nodes
are normally path-gated rather than level-gated; Spellblade's level-band rows
are the explicit exception. An authored inherited entry may also be ungated:

- Base trees: levels `1`, `5`, `10`, `15`, `20`, and `25`.
- First-promotion trees: levels `35`, `40`, `45`, `50`, and `55`.
- Terminal trees: levels `60`, `65`, `70`, `75`, `80`, `85`, `90`, and `95`.
- Promotion gates remain levels `30` and `60`.

Ability gates below the level already required to enter a promoted class are
redundant and are suppressed universally in that promoted tree. They impose no
runtime rule and show no `Required level` text there, while retaining their
authored gate in an earlier tree where it can still matter. This applies to
carried abilities such as Mage elemental spells, Lancer development in
Dragoon, and Mage/Conjurer Callings in Thaumaturgist.

Human routes retain at least three optional points at both promotion gates.
Every race/class combination allowed by the race registry can reach its legal
promotion at the gate. Route costs intentionally differ where class identity
or stat requirements differ.

## Tree Identities

### Base Trees

- Warrior: paired `Piercing Strike -> Charge` and `Shield Slam -> Shield Block`
  trunks leading into four promotion routes, plus connected Defense and
  Offense columns.
- Mage: a bespoke Elemental, Enhancement, Arcana, Occultism, Conjuration, and
  Universal graph described below.
- Footpad: Thief, shared Control, Assassin, Spell Stealer, shared Defense,
  and Inquisitor tracks.
- Healer: Bard, shared Support, Cleric, shared Healing, Priest, and Monk
  tracks.
- Pathfinder: Druid, shared Naturalism, Ranger, shared Melee, Shaman, shared
  Elemental, and Diviner tracks.

### Warrior Lineage

- Weapon Master:
  - Berserker route: ungated inherited-or-purchased Double Strike, ungated
    `+20 Attack`, level-35 Two-Handed Weapon Proficiency, a visual gap,
    Mortal Strike, Devastating Throw, and Brutish Strength. The proficiency
    grants `+10%` accuracy and damage with two-handed weapons; Brutish Strength
    increases the bonus portion of critical damage by `5%` per matching Weapon
    Discipline rank.
  - Grandmaster trunk: inherited-or-purchased Parry and `+20 Defense`, then a
    permanent choice between Dual Wield and Duelist. Parry and the rating node
    have no global-level requirement.
  - Dual Wield style: Dual Wield, stackable Honed Attack, Momentum, and Cross
    Block.
  - Duelist style: Duelist, Blind Fighting, Retort, and Maim. Maim replaces
    retained Cripple.
  - The styles rejoin at True Piercing Strike with an either/or prerequisite,
    then lead to Grandmaster of Arms.
  - Iron Palm, Hemorrhage, Riposte Line, Low Sweep, Guard Cleaver, Reaver's
    Mark, Brace, and Anvil Strike occupy an independent column. Each requires
    rank 1 in its matching Weapon Discipline. A child node immediately to its
    right requires rank 5 and replaces the lower form with its level-2 form.
    Neither form has a global-level gate or is learned automatically.
- Berserker:
  - Heavy Weapons is `Monkey Grip -> Momentum (65) -> Tectonic Rift (75) ->
    Monkey Grip 2 (80)`. Tectonic Rift requires two two-handed weapons, damages
    every enemy with Earth pressure, knocks grounded targets Prone, and deals
    reduced debris damage to flying targets.
  - Two-Weapon Assault is `Mortal Strike 2 -> Boomerang Toss (65) -> +30
    Attack -> Thunderous Vault (75) -> Triple Strike (80)`. Thunderous Vault
    requires two two-handed weapons, attacks with each hand, then releases an
    Electric field against the encounter.
  - Fury is `Frenzy -> Hemorrhage Thirst (70) -> Fatality (75) -> Composed
    Wrath (80)`. Fatality makes a double-damage execution attempt, heals after
    a kill, and allows a surviving target to counter. Composed Wrath restores
    normal Attack/Skill choice during Frenzy.
  - Survival is `Parry -> Pain Tolerance (65) -> Final Assault (70) ->
    Reckless Onslaught (75)`. Final Assault and Reckless Onslaught are
    compatible purchases; Reckless Onslaught no longer replaces Final Assault.
    Hemorrhage Thirst heals the Berserker for enemy bleed-tick damage, while a
    third consecutive-turn trigger causes two turns of unconsciousness.
  - Only the four two-handed disciplines appear in its class tab. Their eight
    rank-1/rank-5 art nodes form four centered rows beside the four development
    columns. Monkey Grip 2, Triple Strike, Composed Wrath, Reckless Onslaught,
    and all four rank-5 arts cost two progression points.
- Grandmaster of Arms:
  - Every weapon discipline has rank-1, rank-5, and rank-10 art nodes; each
    higher form replaces the previous form. Every rank-10 art costs two points.
  - The six-column mastery route is `Double Strike -> Dual Wield Excellence
    (65) -> Weapon Swap (70)`, then forks to two-point Perfect Form and
    Adaptive Arsenal at level 75 before rejoining at Dual Wield Mastery (80).
    Excellence removes the main-hand Dual Wield accuracy penalty; Mastery
    removes the remaining off-hand penalty.
- Paladin:
  - Ungated Oath's Judgment begins at `(1, 0)`. Its left branch is `Double
    Strike -> +20 Attack -> Tempered Conviction -> True Strike` in column 0;
    its right branch is `Smite -> Detect Undead (35) -> Repel the Wicked ->
    +20 Magic -> Detect Fiend (50) -> Hallowed Ground` in column 2. Repel the Wicked is level 40, Tempered Conviction
    level 45, and Hallowed Ground level 55. Tempered Conviction grants `+20%
    Defense` and one Conviction capacity.
  - Ungated Oath's Shelter begins at `(4, 0)`. Its left branch is `Heal -> +50
    MP -> Resist Shadow -> Sworn Purpose -> Blessed Light` in column 3.
    Resist Shadow is level 45 and cannot be purchased without the preceding
    Shelter-path nodes. Sworn Purpose is level
    50 and grants both `+20% Magic` and `+20% Magic
    Defense`. Blessed Light makes a successful healing-spell cast in combat
    grant `+10 Attack` for three turns, refreshing without stacking.
  - Its right branch begins with ungated Bless at `(5, 1)`. Bless connects to
    Magic Defense, which continues through Parry, `+20 Defense`,
    and level-50 Divine Protection. Parry adopts prior ownership but never
    backfills Magic Defense or any other prerequisite.
  - Promote: Crusader is centered at `(2.5, 7)`: it requires either Oath root,
    global level 60, `STR 15`, `CON 17`, `WIS 16`, `CHA 13`, and three
    progression points. Each Oath connector terminates independently on the
    centered promotion node. A baseline Human taking the shortest route
    retains 14 progression points and nine attribute points. Unpurchased
    Paladin nodes close.
  - Hallowed Ground costs 20 MP and creates a three-turn Holy field that
    damages nearby enemies and heals its caster each turn. Resist Shadow costs
    15 MP, is cast outside battle, and grants 50% Shadow resistance for 100
    steps of game time.
- Crusader:
  - Rows 0-7 represent ungated, 65, 70, 75, 80, 85, 90, and 95. Melee begins
    with ungated Condemnation. Its mutually exclusive two-point style nodes
    are level 65 and lead through `Two-Handed Weapon Proficiency -> Mortal
    Strike (75) -> Righteous Advance (80) -> Penalization (85)` or `Sword &
    Board -> Censure (70) -> True Piercing Strike (75) -> Shield Ricochet (80)
    -> Triple Strike (85)`. Beyond Reproach sits beneath Condemnation at level
    75.
  - Spells is `Repel the Wicked -> Smite II (65) -> Sanctification (70) ->
    Undead Hunter (75) -> Smite III (90)`. Sanctification increases all Holy
    damage by 50%. While an Undead enemy remains, Undead Hunter increases Speed
    by 20%—which also raises initiative weight—and critical chance by 10
    percentage points.
  - Healing is `Dispel -> Cleanse (65) -> Heal II (70) -> Radiant Healing (75)
    -> Prayer of Faith (85)`. Radiant Healing turns 10% of actual HP restored
    by an in-combat healing spell into Holy damage against one living hostile.
    Prayer of Faith costs two points and, below 10% HP, randomly heals to full,
    grants a two-turn all-damage barrier, or damages every enemy.
  - Ungated Parry now follows Two-Handed Weapon Proficiency in the first melee
    column. Protection is `Divine Protection -> Posturing (70) ->
    Consecrated Bulwark (75) -> Divine Protection II (80)`. Divine Protection
    II replaces Divine Protection, greatly raises Defense for five turns, and
    lowers nearby enemies' Attack and Magic for three turns. Upgraded spells
    retain replacement ownership without bypassing incomplete prerequisites.
  - Condemnation itself now deals only weapon and Holy damage. Beyond Reproach
    gives it a chance to mark fiends or undead; a successful Repel the Wicked
    then disintegrates the marked target. Penalization makes a successful
    Mortal Strike activate combat-long wrath, adding 15 percentage points of
    critical chance and 25% Holy damage.
- Lancer:
  - The seven-column layout places ungated Jump at column 2 and Polearm
    Proficiency at column 5. Polearm Assault occupies column 4, Polearm Guard
    occupies column 6, and inherited universal attacks occupy column 7.
  - Jump owns three independent paths: defensive modifiers (`Defend -> Acrobat
    -> Grounded Landing`), middle progression (`+20 Attack` directly below
    Jump plus `+20 Defense -> Vigilant Landing (45)`), and offensive modifiers (`Aerial Footwork -> Quick
    Dive -> Thrust -> Rend`). Acrobat unlocks at level 40, Thrust at level 45,
    and Rend at level 50. Aerial Footwork grants `+20% Attack` and one Aerial
    Tempo capacity; Grounded Landing grants `+20% Defense` and 10% final
    incoming damage reduction while Jump charges.
  - Polearm Assault is `Lance Sweep (35) -> Extended Reach (40) ->
    Zephyrstrike (45) -> Swing & Bash (50)`. Polearm Excellence (55) sits in
    column 5 and requires Polearm Proficiency directly.
    Polearm Guard is `Phalanx (35) -> Critical Vigor (40) -> +50 HP (45) ->
    Dragon Soul (50)`.
  - Ungated, inherited-or-purchased True Strike remains in the final column;
    Parry is no longer part of the Lancer or inherited Dragoon tree.
  - Jump-modification IDs remain stable under `lancer.jump-mod.*` and unlock
    configuration without creating spellbook entries.
  - Promote: Dragoon sits in column 4. Its left prerequisite runs `Jump -> +20
    Defense -> Vigilant Landing -> Promote: Dragoon`; Polearm Excellence is
    the second prerequisite. Promotion also requires global level 60, `STR
    17`, and `DEX 13`. Its prerequisite connectors terminate independently on
    the promotion node so neither appears to continue through another path.
    Neither Jump modifier path is required.
  - Polearm Excellence and Vigilant Landing each cost two points.
- Dragoon:
  - The Dragoon tree retains all 22 Lancer development nodes in the same
    positions, omits only the promotion node, and adds 11 Dragoon nodes.
    Previously purchased nodes remain owned; any unpurchased Lancer skill,
    talent, rating, or Jump modification remains purchasable as a Dragoon.
    The three inherited Jump paths retain the same independent prerequisites.
  - Column 5 extends Polearm Excellence through `+30 Attack -> Polearm Mastery
    (80)`.
    Polearm Guard gains two-point Dragonheart at level 75. True Piercing Strike
    moves to column 7 at level 75 and requires True Strike. Each proficiency replaces
    its prior form. Polearm
    Mastery and Dragon Dive each cost two points.
  - Assault mastery extends Rend through Quake and Soaring Strike into Dragon
    Dive. The middle `+20 Attack` node separately unlocks Dragon's Ascent,
    which has no redundant level gate after Dragoon promotion.
  - Shield Block is absent because Warrior Retaliate already requires Shield
    Block, which itself requires Shield Slam. The shield trunk runs through the
    gutter between the Vanguard and Bulwark columns before joining Retaliate.
    Grounded Landing starts level-65 Retribution and level-70
    Unstoppable. Dragon's Ascent gates the `+30 Defense` node. Level-80 Dragon
    Dive requires Dragon's Ascent, Soaring Strike, and Unstoppable.
  - Lancer and Dragoon use rows 0-7 with compact vertical
    spacing so the standard progression panel does not need to scroll.
  - Dragon's Ascent grants `+30% Attack`; a clean Soaring Strike landing grants
    two Aerial Tempo. Dragoon Jump modifiers use stable `dragoon.jump-mod.*`
    IDs.
- Sentinel:
  - Assault is `Retaliate -> Swing & Bash (35) -> +20 Attack (40) -> Focused
    Assault (45) -> Repercussion (50) -> Watchful Reprisal (55)`.
  - Bulwark is `Hold the Line -> Shield Riposte (35) -> +20 Defense (40) ->
    Brace Wall (45) -> Resolute Guard (55)`.
  - Adrenaline splits into Resistance (`Spell Block -> +20 Magic Defense ->
    Bulwark Guard -> Spell Reflection -> Shielding Ward`) and Support (`Purge
    Weakness -> +50 HP -> Boast -> Braggadocious`). Parry is absent; Goad,
    Charge, and Double Strike are disconnected in the fifth column at rows 3-5.
  - Sentinel development occupies rows 0-5, leaving row 6 as a promotion-path
    buffer. Promote: Stalwart Defender sits at `(1.5, 7)` and accepts any of Watchful
    Reprisal, Resolute Guard, Shielding Ward, or Braggadocious at level 60 with
    `CON 20` and a three-point cost.
- Stalwart Defender:
  - Five terminal disciplines contain 25 nodes: Assault, Bulwark, Shield
    Offense, Resistance, and Support. Inherited Resolve actions remain ungated
    catch-up nodes within those chains.
  - Assault culminates in Punishing Guard (70), Crushing Vengeance (75), and
    two-point Double Payback (80). Bulwark culminates in Last Stand (70),
    Unbroken Wall (80), and two-point Iron Maiden (85); the former Defense node
    is removed without shifting the remaining nodes.
  - Shield Offense is `Retaliate -> Shield Ricochet (65) -> Tower Offense (70)
    -> Get Even (75) -> Generator Shield (80)`. Tower Offense converts one-fifth
    of Shield Slam damage into Resolve, capped at 20. Get Even discounts the
    next non-Surge Resolve action by 10. Generator Shield grants 5 Resolve per
    Ricochet hit, doubled when that target is stunned.
  - Resistance adds Mirror Bastion (75) and Fortified Citadel (80); Support
    adds Battle Cry (70), Battle Determination (75), and Final Redoubt (80).
    Battle Determination makes Battle Cry generate 20 Resolve. Citadel Aegis,
    Ironwall Revenge, Last Bastion, and Stronghold are full-Resolve Bursts, not
    tree nodes. Each is intended to unlock after four uses of its associated
    barrier, counter, survival, or fortress family. Four persistent mastery
    tracks now enforce those requirements from Sentinel onward.
  - The complete Stalwart tree occupies rows 1-6. Punishing Guard, Unbroken
    Wall, Fortified Citadel, Final Redoubt, Double Payback, and Iron Maiden each
    cost two points.

### Mage Lineage

- Mage uses six visible columns: `0=Elemental spells`, `1=Enhancements`,
  `2=Arcana`, `3=Occultism`, `4=Conjuration`, and `5=Universal`.
- Elemental spells are six independent level-1 roots:
  `Firebolt/Ice Lance/Shock/Gust/Water Jet/Tremor` at rows `0-5`. Each has a
  level-20 Enhancement directly beside it: `Fire Inside/Frozen Armor/
  Electrified/Wind Currents/Refreshment/Terra Firma`. A successful matching
  spell has a 20% non-stacking, refresh-only proc chance.
  - Fire Inside grants `+25` percentage points of critical chance to the next
    attack; the charge lasts three turns and that attack consumes it regardless
    of hit or result.
  - Frozen Armor grants `+10 Defense` and `+25% Ice resistance` for one turn.
  - Electrified lasts three turns and jolts an attacker once per enemy action
    after a successful incoming melee hit; jolt damage scales from Intelligence.
  - Wind Currents grants `+3 Speed` and `+10` percentage points of melee hit
    chance for three turns.
  - Refreshment immediately restores `5%` of maximum HP and MP.
  - Terra Firma multiplies melee damage by `1.5` for three turns.
- Arcana is `Magic Missile -> Guidance Upgrade -> Mana Rupture -> Polymorph ->
  Mana Shield -> Imbue Weapon`. Gates are `1/5/path-only/15/20/25`.
  Guidance Upgrade increases only Magic Missile projectile critical bonus
  damage by 20%; it grants no static Magic increase. Mana Rupture deals damage
  based on the target's remaining MP. Polymorph denies
  the target two turns and
  replaces its combat sprite with a small, confused-pacing bunny for the
  duration. Bosses are not immune, but resist 90% of Polymorph attempts. Mana
  Shield redirects at most 25% of physical damage from each attack into MP;
  Mana Shield 2 raises that cap to 50%. Imbue Weapon retains its existing
  mechanic. This route leads to Spellblade.
- Occultism is `Enfeeble -> Blinding Fog -> Shadow Bolt -> Inflate Health ->
  Enliven Dead -> Forbidden Studies` at levels `1/5/10/15/20/25`, then
  Warlock. Enfeeble has a `70% + 2% per Intelligence-minus-Constitution point`
  hit chance, clamped to `20-95%`, and lowers the target's base Attack and
  Defense by `20%` for four turns. Blinding Fog targets all enemies. Enliven
  Dead uses the last
  defeated non-boss enemy and a Charisma/Luck check. Inflate Health grants a
  three-turn temporary-HP pool that absorbs post-mitigation damage before real
  HP. Forbidden Studies increases Shadow Bolt damage by `20%` and raised
  undead companion duration by `50%`.
- Conjuration is `Conjure Blade -> +25 MP -> Conjure Animal -> Binding Circle
  -> Conjure Shackles -> Conjure Potion` at levels
  `1/path-only/10/15/20/25`, then Conjurer. Binding Circle grants `+10 Defense`
  and `+10%` health/damage to conjured or summoned allies. Conjure Blade uses
  Intelligence and caster level instead of Strength; Conjure Animal selects
  only implemented `Animal` enemies, preferring those on the current dungeon
  floor before searching the nearest floor. Shackles first contests Dexterity, holds the
  enemy prone for up to three turns, and permits a Strength escape roll each
  turn. Conjure Potion creates a depth-scaled random HP or MP potion, has a
  50-step cooldown, works in combat or a dungeon, and is disabled in town.
- Universal roots are Reflect `(5,1)` at level 10, Sleep `(5,2)` at 15,
  Boost `(5,3)` at 20, and Mirror Image `(5,4)` at 25.
- Sorcerer requires either Classical Force `(0.5,6)` after any Enhancement or
  Arcane Tradition `(1.5,6)` after Mana Rupture; its promotion is `(1,7)`.
  Enhancement connectors converge at the `0.5` midpoint and enter Classical
  Force from above; Mana Rupture routes through the `1.5` midpoint and
  enters Arcane Tradition from above.
  The choice is permanent:
  Classical Force tracks Elemental School Affinity and applies 75% potency to
  Arcane damage/control/barriers/enhancements; Arcane Tradition tracks Arcane
  School Affinity, applies 75% elemental damage, and halves Enhancement proc
  chances. Mage spell learning remains unrestricted before promotion.
- First-promotion route costs, including the two-point promotion node, are `5`
  for an Elemental Sorcerer route, `6` for the Arcane Sorcerer route, and
  `8/8/8` for Spellblade/Warlock/Conjurer. All require level 30.
  Stat gates are Sorcerer `INT 15/WIS 13`; Warlock
  `INT 13/CHA 14`; Spellblade `CON 11/INT 13/CHA 12`; and Conjurer
  `CHA 12/INT 13/WIS 12`. Requirements of 10 or lower are omitted, and neither
  Spellblade nor Conjurer has a Strength requirement.
- Every learned Mage spell remains owned after promotion. Unpurchased Mage
  development and competing promotions close. Sorcerer does not carry the six
  level-one elemental spells, Magic Missile, or Guidance Upgrade into its
  editable tree; the historical Mage tab stays read-only.
- Sorcerer has five full columns plus two half-column specialization nodes.
  Column 1 contains the six tier-two elemental spells, each gated only by 30
  matching School Affinity. Their six level-35 modifiers occupy column 2 and
  feed Classical Enrichment `(0.5,6)` after any complete spell/modifier pair.
  Classical Enrichment unlocks at level 55 and lowers Arcane potency by another
  25 percentage points. Magic Missile II at 30 Arcane Affinity leads to Force
  Multiplier in column 3; the continuous branch then runs through Mana Rupture,
  Mana Leak, level-50 Kinetic Explosion, and Arcane Empowerment. Arcane Ritual
  `(1.5,6)` requires that entire Arcane branch at level 55 and lowers elemental potency by another 25
  percentage points. The level-60 Wizard promotion `(1,7)` accepts Classical
  Enrichment or Arcane Ritual. Spell Enhancements is `Boost -> Dispel -> +20
  Magic -> Refueling -> Doublecast`; Illusion is `Mirror Image -> Slow -> Ice
  Block -> Illusory Link`.
- Wizard has five authored columns and does not repeat Mage level-one spells,
  Magic Missile, Guidance Upgrade, Perfected Formula, or Layered Countermagic.
  Six affinity-gated tier-three elemental spells pair with Inferno, Subzero,
  Electrical Burns, Divine Wind, Unrelenting Waves, and Aftershock. Their
  cross-school reactions are intentionally undocumented in player-facing text.
  Grand Arcana is `Magic Missile III -> Fragmentation -> Mana Splinters ->
  Detonation Cascade (75)`. Mana Rupture, Kinetic Explosion, and Arcane
  Empowerment are inherited prerequisites and are not repeated in this tree.
  Photon Sphere is represented only as Unknown until Domingo casts it on the
  Wizard; the resulting investigation requires six distinct late-game arcane
  proofs and rewards the 150-MP, four-hit, all-enemy spell, 50 maximum MP, and
  three progression points. Prismatic Cataclysm is the parallel elemental
  ultimate: witness Circe, master all six affinities, and defeat all six
  Myrmidon schools; its Elemental Convergence modifier is revealed beneath it.
  Spaghettification sits beneath Photon Sphere and remains hidden until that
  reveal. Master Control includes Counterspell, Gravitational Pull (65), and
  Petrify (80). Spatial Illusion is Volitation -> Mirror Image II (65) ->
  Multiplicity (70) -> Teleport (75), with Triplecast at row 7 and level 90.
- Warlock uses six authored columns covering shadow control, drains, umbral
  offense, curses, corruption, and familiar development. Eclipse is a Warlock
  Shadow spell, Curse of Swarms propagates afflictions between nearby enemies,
  Hemorrhaging Curse adds persistent bleeding, and the independent familiar
  modifiers sit between Familiar Bond I and II. Columns one through five begin
  one row lower; the advanced curse sequence begins another row lower.
  Shadowcaster requires the Umbral Offense path through Shadow Bolt II plus
  either Doom or Mana Drain. Demonologist requires either Curse of Swarms or
  Life Tap.
- Shadowcaster has five terminal paths. Umbral Debt is `Mana Tap -> Soul
  Binding (65) -> Health/Mana Drain (70) -> Resource Abuse (75) -> Mortal
  Shackles (80) -> Top Off (85)`. Deep Shadow is `Shadow Bolt III -> Penny
  Dreadful (70) -> Piercing Bolt (75)`. Veilcraft is `Invisibility -> Shadow
  Curtain (65) -> Alacrity (70) -> Sciophobia (75)`. Nightmares is `Nightmare
  -> Night Terror (75) -> Desoul (80) -> Death Becomes Us (85)`. Familiar
  Mastery contains four independent two-point level-75 nodes: Indiscriminate
  Provocation, Uno Reverse Card, Night Moves, and Bullionaire. Shade of Ahool
  is granted on promotion and spends Umbral Debt to enter a three-turn flying
  shadow form with its authored Shadow, Speed, flight, Holy-weakness, backlash,
  ring, and familiar interactions.
- Demonologist has five authored paths: Contagion, Contract Mastery, Hellfire,
  Soul Harvest, and Demonic Curses. Contagion combines Life Tap mana economy
  with Corruption II, fire-triggered explosions, and persistent DOT growth.
  Hellfire combines grease-coated Shadow Bolts with Firebolt, Netherchar, and
  Napalm. Soul Harvest uses Doom for temporary undead and Desoul for Soul Gems,
  while Soul Vessel provides a Soul-Gem-funded death safeguard. Demonic Curses
  restores Elijah and Dysarthria at this tier and adds Flammable Affliction,
  Monkey's Paw, and Demon Eyes.
- Spellblade replaces the current two-column Channeling/Spellguard graph with
  four explicit columns: `0=Weapon Enhancements`, `1=Armor Enhancements`,
  `2=Spell Enhancements`, and `3=Universal / Extra Abilities`. Imbue Weapon is
  already required for Mage-to-Spellblade promotion and is not repeated here;
  Arcane Edge, Spellguard, and Elemental Strike are also absent from this tree.
  Row `2` holds the three ungated roots, rows `3/4/5/6/7` represent levels
  `35/40/45/50/55`, and row `8` contains the promotion.
  - Weapon Enhancements is `Counter Charge -> +20 Attack -> Breakdown -> Mana
    Slice -> Enhance Blade`. Counter Charge is an ungated passive that grants
    one blade charge after the Spellblade takes damage from a spell. The Attack
    rating is level 35. Breakdown is a level-40 passive: each damaging melee
    hit lowers that target's Magic Defense by 4, up to five stacks. The next
    spell to damage that target benefits from and then consumes every stack.
    Mana Slice and Enhance Blade unlock at levels 45 and 50. Enhance Blade
    adds base weapon damage multiplied by current mana percentage before
    weapon-skill and critical multipliers.
  - Armor Enhancements is `Reflect -> +20 Magic Defense -> Novel Shielding ->
    +20 Defense -> Enhance Armor`. Reflect is the ungated root and Magic
    Defense is level 35. Level-40 Novel Shielding costs 20 MP, requires a Tome, and
    creates a refresh-only three-turn absorption pool equal to twice that
    Tome's power. It blocks post-mitigation direct melee and spell damage; full
    absorption also prevents on-hit effects. The Defense node is level 45.
    Enhance Armor unlocks at level 55 and adds equipped armor multiplied by
    missing mana percentage to physical armor.
  - Spell Enhancements begins `Boost -> Kinetic Explosion -> +20 Magic -> Mana
    Tap`. Boost is the ungated row-2 root. Kinetic Explosion unlocks at level 35,
    costs 18 MP, and sends a `1.5x`
    Arcane-damage explosion across all enemies. Mana Tap unlocks at level 45, then
    branches into level-50 Amplify Arcane and Amplify Elemental. Neither
    Amplify choice excludes the other: they double the release power of the
    matching Arcane or Elemental pool respectively. The branches
    rejoin at level-55 Storage Capacity, which requires either Amplify and
    increases each typed pool's capacity from one to two.
  - Universal / Extra Abilities contains independent True Strike, Parry, and
    Double Strike nodes at levels 35, 40, and 45. They adopt existing ownership
    without backfilling any other Spellblade prerequisite.
  - One damaging spell action stores one Arcane or Elemental charge. Each pool
    holds one by default or two with Storage Capacity, and categories stack
    independently. The next damaging weapon hit releases both pools for 12%
    of that hit per charge, or 24% for a pool with its matching Amplify.
    Arcane resistance or averaged elemental resistance applies; Magic Defense
    does not. Misses preserve charges.
  - Promote: Knight Enchanter is `(1.5,7)` (visual row 8), costs three points,
    requires `STR 16/CON 16/INT 15/DEX 11`, and accepts
    Enhance Blade, Enhance Armor, or Storage Capacity as an either/or capstone.
    Knight Enchanter retains Mana Tap and Enhance Armor as catch-up nodes:
    each is automatically owned when learned as Spellblade and otherwise
    follows its normal Knight Enchanter purchase path.
- Knight Enchanter has five authored columns: Advanced Spells, Assault Release,
  Aegis Release, Spellbind Release, and Universal / Extra Abilities. Advanced
  Spells contains the six tier-two elemental spells and Magic Missile II as
  seven independent level-70, one-point nodes. Quick Recharge, Third Eye, and
  Storage Capacity II cost two points; its other 25 development nodes cost one.
  Double Strike, Enhance Armor, Mana Tap, and Parry are
  ungated entries that adopt prior ownership. Level-65 Riposte follows the
  universal Parry; True Piercing Strike and Triple Strike remain independent. Mana Slice II and
  Quick Recharge occupy rows 6 and 7; Storage Capacity II, Spellbind, and
  Echoing Blade occupy rows 4-6; True Piercing Strike and Triple Strike occupy
  their level-75 and level-85 rows. See
  `CLASS_KIT_DESIGN_GATES.md` for the exact geometry, release-talent rules, and
  numeric contract.
- Every Knight Enchanter combat cast records one of four broad signatures:
  Element, Force, Protection, or Conjuration. The first signature after a
  release becomes the Foundation; the latest different signature becomes or
  replaces the Accent. Repeating either signature reinforces it without adding
  another slot. Signatures do not alter or replace typed Blade Charges.
- A charged weapon hit remains the default release and becomes Enchanted
  Assault when a Foundation exists. Aegis Weave consumes the charges and
  pattern for temporary HP plus pattern-shaped buffs. Spellbind consumes them
  to empower the next damaging spell hit within three turns. Release effects
  use Non-elemental damage where applicable and reset the pattern. The awakened
  Arcane Duel ring's Weave Memory preserves a spent Accent as the next
  Foundation; Arcane Tempo no longer exists as a separate meter.
- Conjurer has four authored disciplines. Constructs are
  `Floating Crystal (30) -> Torchlight (35) -> +20 Magic (path-only) ->
  Conjure Elixir (45) -> Barrier Wall (55)`; Binding is
  `Sleep (30) -> Silence (35) -> Banish (40) -> Weaken Mind (45) ->
  Mana Barbs (55)`; Illusion/Movement is
  `Mirror Image (30) -> Nightmare Fuel (35) -> Volitation (45) ->
  Teleport (50) -> Explosive Decoy (55)`;
  and Calling is `Conjure Humanoid (30) -> Monster (35) -> Spirit (40) ->
  Fiend (45) -> Celestial (50) -> Dragon (55)`. The level-60,
  three-point Thaumaturgist promotion accepts the terminal node of any
  discipline. Development occupies rows 0-5, row 6 is reserved for connector
  routing, and the outer Calling/Construct alternatives enter the promotion
  card from its sides.
- Floating Crystal siphons `10%` of maximum MP after each caster turn, bursts
  after storing `30%` of maximum MP, and multiplies the stored mana by
  `1 + spell power / 100` for its damage. Torchlight halves the random
  encounter rate for 50 exploration steps.
- A Conjurer Calling creates an ordinary 50-step transient companion. It
  chooses an implemented enemy of the requested creature category from the
  current floor when possible, then the nearest matching floor; the ally acts
  independently after the player and never gains roster or bond state.
  Thaumaturgist adds Conjure Animal and replaces ordinary results with one
  permanently selected Xenid from each corresponding pair: Hodag/Caladrius,
  Patagon/Kobalos, Dilong/Cacus,
  Agloolik/Izulu, Hala/Lamashtu, Seraphim/Bardi, or Tiamat/Zahhak. These
  fourteen named creatures are the complete Xenid roster. All six Calling nodes retain
  their Conjurer IDs and remain purchasable in the editable Thaumaturgist tree;
  the historical Conjurer tab is read-only. Fuath remains the Underground
  Spring boss and is not a Xenid.
- Thaumaturgist uses five explicit columns: seven Callings; seven permanent
  paired-Xenid choices; seven matching ultimate unlocks; `Heal Summon
  (65) -> Conduit Command (70) -> Raise Summon (75) -> Conduit Mastery (80)`;
  and the Miracles chain `Miracle Blade (65) -> Miracle Shackles (70) ->
  Miracle Potion (75) -> Miracle Crystal (80)`. The four Miracles each consume
  two progression points and one extremely rare `Reality Fragment` reagent;
  Conduit Mastery also costs two points. Respectively, the Miracles bypass all
  ordinary attack protection, impose an inescapable three-turn restraint,
  create both maximum-tier Health and Mana potions without ordinary location
  or cooldown limits, and create mana from nothing before damaging every
  enemy. The obsolete `Summon` and `Summon 2` training passives are removed;
  the combat Summon action is available directly to Thaumaturgists with a
  living bound Xenid.
  Xenids do not gain XP. Their per-Xenid conduit value drives stat scaling and
  ability tiers, while every chosen Xenid contributes a themed caster effect.
  Conduit Mastery amplifies these reciprocal caster effects by 50%. If the
  active Xenid dies, its conduit falls by 25. `Raise Summon` is combat-only,
  costs 100 MP, restores only that combat's just-fallen active Xenid at 25% HP,
  and refunds 10 of the conduit lost to that death; it cannot raise roster-wide
  or historical deaths.

### Footpad Lineage

Footpad has 34 development nodes across six vertical tracks: Thief, Control,
Assassin, Spell Stealer, Defense, and Inquisitor. Rows advance from ungated
roots through level 5, 10, 15, 20, and 25 gates. Control deliberately leaves
row four blank after Smoke Screen and is required by both Thief and Assassin.
Defense leaves row two blank after Quickstep and is required by both Spell
Stealer and Inquisitor. The four promotion nodes sit between their identity
and shared columns, making each combined route cost 13 progression points.

The new nodes are implemented mechanics rather than labels. Avoid Traps hooks
into triggered traps, Do-over supplies one possible attack reroll per battle,
Serendipity improves ordinary loot rolls, and Mana Depletion drains MP only on
the basic Attack action. Obscuration requires the reusable 5,000G Censer of
Choking Ash sold by the Magic Shop, reduces random encounters for 50 steps,
and lowers accuracy against the user. Incantation Comprehension increases
scroll potency, Mystical Evasion adds spell dodge, and Disruption interrupts a
charged ability with a two-turn Silence on a critical hit. Outclassed enemies
can now choose to flee, and Aggressive Pursuit grants its advantaged
interception attack. Smoke Screen escapes bypass Aggressive Pursuit.

| Tree | Paths | Development nodes / total cost | Promotion route cost | Retained talents |
| --- | --- | ---: | ---: | --- |
| Thief | Fortune, Misfortune, Tools, Escape | 22 / 22 | Rogue: any complete discipline + 3 | Authored luck, tool, escape, and stat choices |
| Rogue | Loaded Odds, Comebacks, Cunning, Escape | 28 / 30 | Terminal | Authored luck, survival, tool, and escape talents |
| Inquisitor | Case Journal, Judgment, Elemental Wards | 23 / 24 | Seeker: either complete route + 3 | Take Notes costs two points; five added passives deepen casework, debuffs, and wards |
| Seeker | Wayfinding, Safe Passage, Revelation, Judgment | 28 / 30 | Terminal | Twelve authored mechanic talents |
| Assassin | Utility, Combat, Status / Death, Stealth, Counter | 25 / 25 | Ninja: Cutthroat path + 3 | Twist the Knife, OffHand Excellence, For Good Measure, Cutthroat, Surprise!, Main Gauche, Live and Learn |
| Ninja | Utility, Combat, Toxin / Death, Stealth, Defense | 28 / 33 | Terminal | Find Traps, Smash and Grab, Execution Rhythm, toxin mastery, concealment, counters, dedicated Death Mark finishers |
| Spell Stealer | Spell Theft, Stolen Charge | 12 / 19 | Arcane Trickster: either complete path + 3 | Five authored talents |
| Arcane Trickster | Arcane Larceny, Misdirection | 12 / 30 | Terminal | Six authored talents |

Fortune and Revelation use their canonical class caps. Stolen Charge uses its
canonical cap until the visible Grand Larceny purchase expands it. Ninja keeps its fixed
three-mark capacity and authored setup/finisher development.

All four Footpad promotion paths now use authored trees. Inquisitor's six
elemental wards remain independent cross-training rather than promotion gates;
Seeker expands the Case Journal and Wayfinding systems without adding another
meter. Generated rating families and repeated ranks remain prohibited.

Assassin now uses five authored six-row columns with intentional gaps instead
of generic kit branches. Its toxin line turns specific enemy and exploration
reagents into six coatings; coatings are never random loot and resolve their
standard reaction on a hit or severe reaction on a critical hit. Apply Toxin
coats one equipped dagger, while Hidden Blade consumes recoverable ammunition
from a ten-dagger pack. The tree also implements the utility, dual-wield,
stealth-opener, and parry-counter passives shown in the diagram.

### Healer Lineage

Healer has 36 development nodes across six full Bard, Support, Cleric,
Healing, Priest, and Monk columns. Bard joins its performance column to the
complete Support column; Cleric and Priest each join their identity column to
the complete Healing column. Those three joined routes cost 14 points each,
including promotion. Monk remains an independent six-node offensive-discipline
route costing eight points including promotion. This makes the shared support
and healing commitments explicit without duplicating their abilities.

The Bard line progresses through Imbue Weapon, Goad, Lullaby, Beginner's Luck,
Mental Shard, and Cacophany. Support supplies Bless, Tranquility, Courage,
Vision, Magic Defense, and Tutelary. Cleric combines Smite, Defense, Turn
Undead, Detect Undead, Divine Protection, and Shield Slam with Healing's Heal,
HP, Regen, MP, Safeguarding, and Heal II. Priest builds Holy, Magic, Flash
Blindness, Defensive Regen, Incite Panic, and Resist Shadow alongside that
same Healing column. Monk develops Zen Accuracy, Staff Proficiency, Attack,
Delayed Reaction, Leg Sweep, and Meditation.

| Tree | Paths | Development nodes / total cost | Promotion route cost | Retained talents |
| --- | --- | ---: | ---: | --- |
| Cleric | Devotion, Sacred Office, Bulwark, Judgment, Shared Ministry | 26 / 26 | Either terminal: one route endpoint + 3 | Nine authored talents and two shared active rites |
| Templar | Relic Discipline, Vanguard, Ordered Blessings, Judgment | 28 / 30 | Terminal | Relic durability, martial coverage, blessing riders, Holy judgment |
| Hierophant | Sacred Conduit, Devotional Grace, Radiant Office, Pastoral Office | 28 / 30 | Terminal | Staff payoff, partial spending, Holy pressure, direct-heal wards |
| Monk | Ki Assault, Ki Discipline, Centering, Open Hand | 23 / 23 | Master Monk: any complete primary route + 3 | Six authored Ki and centering talents plus three stat choices |
| Master Monk | Perfected Flurry, Final Art, Diamond Body, Rope-a-Dope, Dim Mak Mastery | 27 / 28 | Terminal | Dim Mak remains quest-awarded; its six optional modifiers are terminal leaves |
| Priest | Prayer, Exorcism, Grace, Protection | 22 / 22 | Archbishop: any complete discipline + 3 | Seven authored Prayer/support talents plus Magic and Magic Defense choices |
| Archbishop | Benediction, Great Gospel, Intervention, Sustaining Grace, Perfect Supplication | 29 / 31 | Terminal | Twenty authored support and crisis talents |
| Bard | Performance, Composition | 26 / 26 | Troubadour: 7 | Five visual columns, four `any` route capstones; Compose is inherent in the Class tab |
| Troubadour | Finale, Mastery | 27 / 27 | Terminal | Authored terminal kit |

The generated Healer passive families and their meter-cap payloads are removed.
Ki remains exactly 3/5. Devotion uses its class-defined cap unless the visible
Overflowing Grace or Abundant Grace node expands it; Prayer and Crescendo use
their authored rules. Troubadour has no ordinary catalog abilities of its
own outside its authored terminal actions; retained Bard abilities, repertoire,
codas, and ring mechanics remain available through universal promotion retention.

### Pathfinder Lineage

Pathfinder's 40 development nodes are split into seven vertical tracks: Druid,
Naturalism, Ranger, Melee, Shaman, Elemental, and Diviner. Two deliberate row-4
gaps preserve the requested Naturalism and Melee pacing. Druid joins its nature
spells to the shared Naturalism capstone; Ranger draws from Naturalism, its full
melee identity, and the shared Attack training; Shaman joins the same Attack
training to its full spirit identity and elemental magic; and Diviner joins
Elemental to its complete time/divination identity. Including promotion, the
routes cost 13, 14, 14, and 11 points respectively, keeping every promotion
reachable within the 16 points earned by level 30 without making the shared
tracks identical.

Nature is a first-class spell damage and resistance type. Abilities may declare
several qualifying damage types—for example Poison Dart is Nature/Poison,
Thorny Vine is Nature/Earth, and the reworked Poison Strike is a main-hand
Nature spell with Physical and Poison components. Elemental-trigger passives
inspect all declared types rather than forcing each spell into one school.

| Tree | Paths | Development nodes / total cost | Promotion route cost | Retained talents |
| --- | --- | ---: | ---: | --- |
| Druid | Panther Form, Direbear Form, Venom and Stone, Growth and Stars, Primal Practice | 28 / 28 | Lycan or Archdruid: any matching endpoint + 3 | Ten authored form/nature talents |
| Lycan | Frenzy, Moon Hunt, Dragon Essence, Control | 28 / 30 | Terminal | Nineteen authored form/control talents and three added active techniques |
| Archdruid | Venom, Stone, Growth, Storm | 28 / 30 | Terminal | Eighteen authored affinity talents |
| Diviner | Rune Lore, Rune Flow, Foresight, Chronomancy | 22 / 22 | Astromancer: any endpoint + 3 | Eleven authored rune/foresight talents plus three rating nodes and intentional gaps |
| Astromancer | Foresight Threads, Runic Constellations, Celestial Force, Lucid Utility | 28 / 30 | Terminal | Fourteen authored thread/rune/utility talents |
| Shaman | Totems, Elements, Spirit Warrior, Bad Omens | 19 / 21 | Soulcatcher: Totems, Elements, or Spirit Warrior endpoint | Totem is inherent; Hexcraft and Omen Ward deepen the optional omen route |
| Soulcatcher | Soul Dominion, Essence, Ancestral Totem, Spirit Warrior | 28 / 30 | Terminal | None |
| Ranger | Hunt, Companion Bond, Duelist/Ranged, Two-Handed, Defense | 24 / 24 | Beast Master: Companion Bond + 3 | Authored hunt, weapon, and defense talents |
| Beast Master | Pack Tactics, Commands, Guardian Bond, Apex Bond | 22 / 22 | Terminal | Authored companion-command talents |

Generated Pathfinder rating families remain removed. Fixed contracts now stay
fixed: Harmony is 4 (5 with its awakened ring), Threads are 3, Resonance is 3
(4 with Aspect Evolution), and Lycan ranks require three distinct qualifying
successes. Bonded Bulwark alone remains because its authored payoff raises the
full-bond companion coefficient from 15% to 25%, scaling at lower bond.

Ranger and Beast Master may equip Crossbows in the off hand. A basic attack
fires the selected bolt pack after the main-hand attack; using a bolt pack from
inventory changes the selection, and the least expensive available pack is the
fallback. Repeating Crossbows fire twice. Armor Piercing, Magic, Heat-Seeking,
Napalm, and Delayed Bolts apply their named combat behaviors, while recovery
chance determines whether ammunition is returned. Napalm ammunition is
recovered only as an ordinary Metal Bolt.

Active Resist effects appear as positive buff indicators in the Character Menu,
dungeon HUD, and combat HUD. Resist All applies a five-turn ward to Fire, Ice,
Electric, Water, Earth, Wind, Shadow, and Holy resistance.

Every promoted tree is authored. Compact trees remain exempt from arbitrary
breadth targets when their external repertoire or higher-cost masteries provide
meaningful development pressure. Do not restore generated passive families,
repeated ranks, or generic cap masteries to inflate node counts.
First-promotion route costs above include the three-point terminal promotion;
total development costs exclude promotion nodes.

## Ownership Boundaries

Promotion still initializes mandatory identity access: Paladin vows, Warlock
familiars, Thaumaturgist Calling choices and Xenid conduits, Demonologist
contracts, and Ranger taming.
Quest, Class Ring, Power Core, contract reward, summon-bond reward, and
Weapon Discipline reward abilities remain externally owned.

Optional kit actions remain ability nodes. Named talent nodes can raise a
class-kit meter cap or grant a smaller permanent combat bonus. Talent effects
are queried by stable talent key and survive later promotions.

The normal branch-closure rule has two authored carry-forward families.
Promoting from Lancer to Dragoon closes the historical Lancer tab but carries
every Lancer development node into the editable Dragoon tree. Mage to Sorcerer
and Sorcerer to Wizard keep only the declared elemental nodes editable in the
current tree; other historical development stays closed.

Version-5 node and talent IDs are persistent save API. Renaming one requires a
save migration or alias.
