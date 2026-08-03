# Authored Ability-Tree Design

## Runtime Contract

All 49 playable classes own a declarative tree in
`src/core/progression_manifest.py`. `src/core/progression.py` builds and
validates those declarations, applies purchases atomically, and remains the
public runtime facade for both frontends.

Development nodes cost one point. First promotions cost two points and second
promotions cost three. Rating nodes scale with their tree tier: base trees
grant `+10`, first-promotion trees grant `+20`, and terminal trees grant `+30`.
HP and MP nodes likewise scale by tier at `+25`, `+50`, and `+100`. Named
talents grant the full rating amount for their tier for every rating they
increase, in addition to their class-specific effect, without appearing in the
spellbook. Active and passive ability nodes still instantiate the canonical
ability class.

Ability milestones are global for gated abilities and talents. Rating nodes
are never level-gated, and an authored inherited entry may also be ungated:

- Base trees: levels `1`, `5`, `10`, `15`, `20`, and `25`.
- First-promotion trees: levels `35`, `40`, `45`, `50`, and `55`.
- Terminal trees: levels `60`, `65`, `70`, `75`, `80`, `85`, `90`, and `95`.
- Promotion gates remain levels `30` and `60`.

Human routes retain at least three optional points at both promotion gates.
Every race/class combination allowed by the race registry can reach its legal
promotion at the gate. Route costs intentionally differ where class identity
or stat requirements differ.

## Tree Identities

### Base Trees

- Warrior: a shared Piercing Strike, Charge, and Weapon Focus trunk leading
  into Arms and Vanguard, plus Bulwark, Command, and independent martial
  talents.
- Mage: Elementalism, Occultism, Battlemagic, and Conjuration.
- Footpad: Subterfuge, Vigilance, Assassination, and Spellcraft.
- Healer: Devotion, Discipline, Restoration, and Inspiration.
- Pathfinder: Wilds, Divination, Totemism, and Huntsmanship.

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
  - Survival column: ungated Final Assault, Monkey Grip 1 at 65, an ungated
    `+30 Attack` node, Reckless Onslaught at 70, and Monkey Grip 2 at 75.
  - Fury column: ungated Frenzy, an ungated `+100 HP` node, Mortal Strike 2 at
    65, Boomerang Toss at 70, and Triple Strike at 75.
  - Independent center column: inherited-or-purchased Parry without a level
    gate, Pain Tolerance at 65, and Hemorrhage Thirst at 70. Hemorrhage Thirst
    heals the Berserker for enemy bleed-tick damage; a third consecutive-turn
    trigger makes the Berserker unconscious for two turns. Reckless Onslaught
    replaces Final Assault, deals double weapon damage, stacks Attack Up and
    Defense Down when refreshed, and knocks the user Prone when parried.
  - Both left paths use five vertically centered rows. The three independent
    entries use three vertically centered rows beside the weapon-art block.
  - Only the four two-handed disciplines appear in its class tab. Their eight
    rank-1/rank-5 art nodes form four centered rows independent of the three
    development columns.
- Grandmaster of Arms:
  - Every weapon discipline has rank-1, rank-5, and rank-10 art nodes; each
    higher form replaces the previous form.
  - Perfect Form is a floating talent granting `+1%` weapon damage and `+0.5%`
    hit chance per equipped discipline rank, with no level gate.
  - Double Strike is an ungated, inherited-or-purchased floating entry between
    Perfect Form and Adaptive Arsenal in the fourth column.
  - Adaptive Arsenal is a floating talent granting `+0.5%` parry chance and
    `+1%` counterattack critical chance per equipped discipline rank, with no
    level gate.
- Paladin:
  - Ungated Oath's Judgment begins at `(1, 0)`. Its left branch is `Double
    Strike -> +20 Attack -> Tempered Conviction -> True Strike` in column 0;
    its right branch is `Smite -> Repel the Wicked -> +20 Magic -> Hallowed
    Ground` in column 2. Repel the Wicked is level 40, Tempered Conviction
    level 45, and Hallowed Ground level 55. Tempered Conviction grants `+20
    Defense` and one Conviction capacity.
  - Ungated Oath's Shelter begins at `(4, 0)`. Its left branch is `Heal -> +50
    MP -> Sworn Purpose -> Blessed Light` in column 3. Sworn Purpose is level
    50 and grants both `+20 Magic` and `+20 Magic
    Defense`. Blessed Light makes a successful healing-spell cast in combat
    grant `+10 Attack` for three turns, refreshing without stacking.
  - Its right branch begins with ungated Bless at `(5, 1)`. Magic Defense and
    level-45 Resist Shadow are detached from the Oath's Shelter connector.
    Magic Defense begins the protection chain through Parry, `+20 Defense`,
    and level-50 Divine Protection. Parry adopts prior ownership but never
    backfills Magic Defense or any other prerequisite.
  - Promote: Crusader is centered at `(2.5, 7)`: it requires either Oath root,
    global level 60, `STR 15`, `CON 17`, `WIS 16`, `CHA 13`, and three
    progression points. Each Oath connector drops straight to row 7 before
    joining the centered node. A baseline Human taking the shortest route
    retains 14 progression points and nine attribute points. Unpurchased
    Paladin nodes close.
  - Hallowed Ground costs 20 MP and creates a three-turn Holy field that
    damages nearby enemies and heals its caster each turn. Resist Shadow costs
    15 MP, is cast outside battle, and grants 50% Shadow resistance for 100
    steps of game time.
- Crusader:
  - Melee begins with ungated Condemnation. Its mutually exclusive branches
    are `Two-Handed Weapon Proficiency -> +30 Attack -> Mortal Strike ->
    Righteous Advance` and `Sword & Board -> True Piercing Strike -> Triple
    Strike`. Mortal Strike is level 75, True Piercing Strike level 70, and
    Triple Strike level 85. True Piercing Strike no longer requires True
    Strike.
  - Spells contains ungated Smite II, retained-or-purchased Repel the Wicked,
    and level-70 Smite III. An inherited Repel node does not backfill Smite II;
    there is no Turn Undead upgrade node.
  - Healing contains ungated Heal II, level-65 Cleanse, and level-70 Dispel.
  - Protection contains ungated Consecrated Bulwark, then Parry, level-65
    Posturing, `+30 Magic Defense`, and `+100 HP`. Smite II/III and Heal II use
    replacement ownership.
  - Condemnation deals weapon and Holy damage and can mark fiends or undead.
    Repel the Wicked normally drives a valid target from combat without kill
    rewards; a successful cast against a Condemnation-marked target
    disintegrates it.
- Lancer:
  - The six-column layout places ungated Jump at column 2 and ungated Polearm
    Proficiency at column 5.
  - Jump owns three independent paths: defensive modifiers (`Defend -> Acrobat
    -> Grounded Landing`), middle progression (`+20 Defense -> +20 Attack ->
    Promote: Dragoon`), and offensive modifiers (`Aerial Footwork -> Quick
    Dive -> Thrust -> Rend`). Acrobat unlocks at level 40, Thrust at level 45,
    and Rend at level 50. Aerial Footwork grants `+20 Attack` and one Aerial
    Tempo capacity; Grounded Landing grants `+20 Defense` and 10% final
    incoming damage reduction while Jump charges.
  - Polearm Proficiency owns one vertical line through level-35 Lance Sweep,
    `+50 HP`, then level-40 Zephyrstrike.
  - Ungated, inherited-or-purchased Parry and True Strike occupy the final
    column at rows 2 and 3 so either can be recovered if missed on the Warrior
    tree.
  - Jump-modification IDs remain stable under `lancer.jump-mod.*` and unlock
    configuration without creating spellbook entries.
  - Promote: Dragoon sits directly below Jump in column 2. Its connector runs
    through the two middle rating nodes, and it additionally requires global
    level 60, `STR 17`, and `DEX 13`. Neither modifier path is required.
- Dragoon:
  - The Dragoon tree retains all 16 Lancer development nodes in the same
    positions, omits only the promotion node, and adds 11 Dragoon nodes.
    Previously purchased nodes remain owned; any unpurchased Lancer skill,
    talent, rating, or Jump modification remains purchasable as a Dragoon.
    The three inherited Jump paths retain the same independent prerequisites.
  - Ungated Polearm Excellence starts the Dragoon polearm mastery line at row
    5, followed by `+30 Attack`, True Piercing Strike, and Polearm Mastery.
    True Piercing Strike unlocks at level 70 without a True Strike
    prerequisite, and each proficiency replaces its prior form.
  - Assault mastery extends Rend through Quake and Soaring Strike into Dragon
    Dive. The middle `+20 Attack` node separately unlocks Dragon's Ascent,
    which has no redundant level gate after Dragoon promotion.
  - Shield Block is absent because the Warrior-to-Lancer route already
    requires it. Grounded Landing starts level-65 Retribution and level-70
    Unstoppable. Dragon's Ascent gates the `+30 Defense` node. Level-80 Dragon
    Dive requires Dragon's Ascent, Soaring Strike, and Unstoppable.
  - Lancer remains within rows 0-6. Dragoon uses rows 0-7 with compact vertical
    spacing so the standard progression panel does not need to scroll.
  - Dragon's Ascent grants `+30 Attack`; a clean Soaring Strike landing grants
    two Aerial Tempo. Dragoon Jump modifiers use stable `dragoon.jump-mod.*`
    IDs.
- Sentinel:
  - Counter is `Goad -> Shield Check -> Retaliate -> Shield Riposte ->
    Watchful Reprisal`, followed by optional `+20 Attack`.
  - Wall is `Hold the Line -> Brace Wall -> Covering Guard -> Bulwark ->
    Resolute Guard`, followed by optional `+20 Defense`.
  - Anti-magic is `Deflect Spell -> Spell Reflection -> +20 Magic Defense ->
    +50 HP`. Shield Block is omitted because the Warrior route requires it.
  - Promote: Stalwart Defender sits at `(1, 6)` and requires Watchful Reprisal,
    Resolute Guard, global level 60, `CON 20`, and three points. The mandatory
    Human route leaves four points. Known Goad and Retaliate are adopted.
- Stalwart Defender:
  - Last Stand continues through level-65 Unbroken Wall, `+30 Defense`, and
    `+100 HP`; Punishing Guard independently leads to `+30 Attack`.
  - Fortified Citadel, Crushing Reprisal, and Final Redoubt are independent
    modifier talents at levels 65, 70, and 80. The three Surges remain
    mastery-granted actions and are not progression nodes.
  - Level-65 Mirror Bastion requires learned Spell Reflection and leads to
    `+30 Magic Defense`.
  - Sentinel and Stalwart fit within rows 0-6 and 0-3 respectively. Sentinel
    leftovers close on promotion; the terminal tree contains only new nodes.

### Mage Lineage

- Sorcerer/Wizard: School Affinity, Metamagic, Arcane Mastery, and
  Countermagic.
- Warlock/Shadowcaster/Demonologist: Umbral Magic, Sacrifice, Pacts, Umbral
  Debt, Deep Shadow, Contracts, and Corruption.
- Spellblade/Knight Enchanter: Channeling, Spellguard, Arcane Tempo, and
  Enchantment.
- Summoner/Grand Summoner: Summon Bond, Conjuration, Conduit, and True Names.

### Footpad Lineage

- Thief/Rogue: Fortune, Tools, Loaded Odds, and Cunning.
- Inquisitor/Seeker: Case Journal, Judgment, Wayfinding, and Revelation.
- Assassin/Ninja: Death Mark, Shadowcraft, Execution, and No Trace.
- Spell Stealer/Arcane Trickster: Spell Theft, Stolen Charge, Arcane Larceny,
  and Misdirection.

### Healer Lineage

- Cleric/Templar/Hierophant: Devotion, Bulwark, Relic Discipline, Ordered
  Blessings, Sacred Conduit, and Devotional Grace.
- Monk/Master Monk: Ki, Centering, Perfected Ki, and Diamond Body.
- Priest/Archbishop: Prayer, Grace, Benediction, and Intervention.
- Bard/Troubadour: Performance, Composition, Finale, and Mastery.

### Pathfinder Lineage

- Druid/Lycan/Archdruid: Forms, Nature Rites, Frenzy, Control, Fourfold
  Balance, and Aspect Harmony.
- Diviner/Astromancer: Runes, Foresight, Foresight Threads, and
  Constellations.
- Shaman/Soulcatcher: Totems, Elements, Soul Communion, and Totem Resonance.
- Ranger/Beast Master: Hunt, Companion Bond, Pack Tactics, and Commands.

## Ownership Boundaries

Promotion still initializes mandatory identity access: Paladin vows, Warlock
familiars, Summoner summon access, Demonologist contracts, and Ranger taming.
Quest, Class Ring, Power Core, contract reward, summon-bond reward, and
Weapon Discipline reward abilities remain externally owned.

Optional kit actions remain ability nodes. Named talent nodes can raise a
class-kit meter cap or grant a smaller permanent combat bonus. Talent effects
are queried by stable talent key and survive later promotions.

The normal branch-closure rule has one authored exception: promoting from
Lancer to Dragoon closes the historical Lancer tab but carries every Lancer
development node into the editable Dragoon tree.

Version-5 node and talent IDs are persistent save API. Renaming one requires a
save migration or alias.
