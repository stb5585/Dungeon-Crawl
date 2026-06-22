# Class Ring Activation Spec

## Current Implementation Status

Class Ring activation now has two implementation tiers:

- Fully playable activation flows: `Grandmaster of Arms`, `Demonologist`,
  `Archdruid`, `Berserker`, `Dragoon`, `Stalwart Defender`, `Wizard`,
  `Shadowcaster`, `Knight Enchanter`, `Grand Summoner`, `Rogue`, `Seeker`,
  `Ninja`, `Arcane Trickster`, `Crusader`, `Templar`, `Master Monk`, `Archbishop`,
  `Troubadour`, `Lycan`, `Astromancer`, `Soulcatcher`, and `Beast Master`.
- Legacy second-promotion foundation: saved awakening state, dormant/awakened
  Class Ring descriptions, activation helpers, and several runtime mechanics
  are implemented for the remaining second-promotion classes.

The standard Class Ring acquisition remains the Hooded Figure reward after the
Red Dragon quest. The ring's second-promotion power is dormant until awakened by
the current class's path.

## Grandmaster Of Arms

The Class Ring is earned from the Hooded Figure after the Red Dragon quest, but
its second-promotion power is dormant until each class awakens it through a
class-specific Quest Awakening.

For Grandmaster of Arms, awakening happens in the Barracks through a hidden
training hall led by the retired hero placeholder-named Master Varric.

### Discovery

- Eligible class: `Grandmaster of Arms`.
- The player must have the `Class Ring` equipped or stored in the Barracks
  storage locker.
- A Class Ring sitting only in inventory is not visible to town NPCs and does
  not trigger the Sergeant's hint.
- The Hooded Figure's Class Ring reward text hints that the ring is dormant and
  each class must awaken it differently.

### Weapon Discipline

Grandmaster tracks discipline XP and rank for:

- `Fist`
- `Dagger`
- `Sword`
- `Club`
- `Longsword`
- `Battle Axe`
- `Polearm`
- `Hammer`

Successful main-hand and offhand weapon hits grant discipline XP to that weapon
type. Victory grants bonus discipline XP to equipped weapon types that landed at
least one hit. Discipline uses 10 increasing ranks.

Each rank grants `+0.5%` accuracy and `+1%` technique proc chance for that
weapon type. At rank 10 this is `+5%` accuracy and `10%` technique chance.

### Class Ring Binding

The Grandmaster Class Ring holds one active weapon binding at a time. When worn,
it doubles the chosen weapon discipline bonus:

- Rank 10 unbound: `+5%` accuracy and `10%` technique chance.
- Rank 10 bound and ring equipped: `+10%` accuracy and `20%` technique chance.

Rebinding is available immediately after activation through a harder Secret
Master gauntlet. Rebinding replaces the active weapon binding.

### Weapon Techniques

One-handed techniques stack up to 3 stacks for 3 turns. Main-hand and offhand
procs both count.

Two-handed techniques do not stack; repeated procs refresh duration.

- `Fist`: Stagger, stacking Attack down.
- `Dagger`: Expose, stacking bleed pressure.
- `Sword`: Precision, stacking critical-damage benefit.
- `Club`: Daze, stacking Speed down.
- `Longsword`: Guard Break, non-stacking Defense down.
- `Battle Axe`: Rend, non-stacking heavy bleed.
- `Polearm`: Trip, non-stacking Prone effect.
- `Hammer`: Sunder, non-stacking stronger Defense down.

Existing immunity and physical-effect rules continue to apply.

### Secret Master Trial

Initial activation:

- Choose one target weapon type.
- The target weapon type must be equipped in the main-hand `Weapon` slot for
  every trial fight.
- Complete a 3-fight gauntlet.
- Success activates the ring and binds it to the chosen weapon type.

Rebinding:

- Choose the new target weapon type.
- Complete a harder 3-fight gauntlet while keeping that weapon type in the main
  hand.
- Success replaces the active binding.

Before each fight, HP and MP are raised to at least 50% if below that floor. The
trial does not heal above that floor.

Losing a fight is not normal death. The gauntlet resets to the beginning and
consumables spent remain spent.

Trial fights grant discipline XP but no gold, loot, normal experience, quest
progress, or kill-count credit.

## Demonologist

Demonologist progression has two stages. Promotion to `Demonologist` reveals
the hidden Church Crypt and unlocks basic fiend contracts. The Class Ring is
awakened later, after it is obtained, by returning to the crypt and imprisoning
the current familiar inside the ring.

### Church Crypt

- Eligible class: `Demonologist`.
- The crypt becomes available immediately on promotion.
- An occult priest hints at the crypt after promotion.
- The crypt explains contracts, refreshes unlocked patrons from defeated-fiend
  history, binds one active patron, and awakens the Class Ring when eligible.
- Basic contracts do not require Class Ring activation.

### Contracts

Supported contract patrons:

- `Imp`
- `Quasit`
- `Incubus`
- `Succubus`
- `Archvile`
- `Maelephant`
- `Balor`

Defeating a supported fiend unlocks that contract. Existing kill history counts,
so previously defeated fiends are recognized when the Demonologist visits the
crypt. Only one patron can be active at a time, and switching happens in the
crypt.

In combat, `Call Contract` asks the active patron for an intent:

- `Harm`
- `Curse`
- `Protect`
- `Restore`
- `Desperate Aid`

The patron quotes a price before acting. The player may accept or refuse. Costs
are paid up front and always include gold. More urgent or desperate requests can
also demand a potion or permanent HP/MP sacrifice. Higher Charisma lowers the
chance and severity of fiendish misbehavior.

### Ring Awakening

Class Ring awakening requires:

- Player class is `Demonologist`.
- The Class Ring is equipped or stored in Barracks storage.
- The player has a familiar.

Awakening permanently imprisons the familiar in the ring. The familiar is removed
from normal familiar behavior and becomes the ring's echo:

- `Homunculus`: defensive echo.
- `Fairy`: sustain echo.
- `Mephit`: arcane/corruption echo.
- `Jinkin`: risk/reward echo.

Once awakened, the ring empowers all unlocked and future fiend contracts. The
empowered state improves contract strength and fulfillment odds, but bargain
drawbacks remain active.

## Archdruid

Archdruid awakening follows the Fourfold Balance path. The Class Ring remains
dormant until the Archdruid balances `Venom`, `Stone`, `Growth`, and `Storm`,
finds the Ancient Grove, and completes all four aspect rituals.

### Ancient Grove

- Eligible class: `Archdruid`.
- Each affinity tracks attunement from `0` to `100`.
- The Ancient Grove appears once all four affinities are at least `50`.
- The Class Ring must be equipped or stored in Barracks storage to awaken.
- A Class Ring sitting only in inventory does not awaken from the completed
  rituals.

### Attunement

- `Venom`: gains attunement when poisoning enemies; loses attunement from poison
  damage taken. Mastery grants Poison immunity.
- `Stone`: gains attunement by surviving physical damage; loses attunement when
  hard-control pressure such as Prone or Stun lands. Mastery grants Stone
  immunity and a modest physical defense benefit.
- `Growth`: gains attunement from healing done; loses attunement when life is
  drained. Mastery unlocks the Tree of Life state for future ability work.
- `Storm`: gains attunement from Electric and Wind damage dealt; loses
  attunement from Berserk or Silence. Mastery grants Lightning Rod, converting
  part of Electric/Wind damage taken into mana.

An affinity can rise normally, but it caps at `99` until its Grove aspect ritual
has been completed.

### Catalysts And Rituals

Each aspect ritual requires a unique catalyst. Catalysts are deterministic
first-time drops, only for Archdruids after the Grove is unlocked.

- `Venom`: `Serpent Venom Heart`.
- `Stone`: `Heartstone Shard`.
- `Growth`: `Verdant Seed`.
- `Storm`: `Stormglass Feather`.

Rituals consume their catalyst only on success. Failed ritual attempts reset
without consuming the catalyst.

Completing a ritual unlocks that aspect. Completing all four aspects awakens the
Class Ring if the ring is visible through equipment or Barracks storage.

### Harmony Bonus

When awakened and equipped, the Archdruid Class Ring grants a Harmony Bonus:

- `+1%` spell damage, healing, and resistance utility per `25` total attunement.
- If all four affinities are at least `75`, the Harmony Bonus is doubled.

The Class Ring description shows dormant, Grove-ready, ritual-progress, and
awakened states.

## Existing Second-Promotion Classes

All pre-existing second-promotion Class Ring effects now follow Quest
Awakening. The ring can be earned before awakening, but class-specific effects
remain dormant until the matching class completes its activation path. Legacy
awakening state is saved in `class_ring_awakening`.

The ring must be equipped or placed in Barracks storage for activation helpers.
Inventory-only rings do not count as visible town recognition.

The listed effects are represented in code as descriptions, saved state, and
mechanics helpers. Some have live combat hooks already; full quest UI, trial
encounters, and class-specific town interactions remain to be implemented per
class.

### Warrior Branch

- `Berserker`: `No Healing Duel` awakens `Bloodied Crits`. While worn, the
  ring grants +10% crit below 50% HP, or +15% crit and +15% weapon damage below
  25% HP.
  - Status: playable in the Barracks when a dormant Berserker Class Ring is
    equipped or stored.
  - The duel has no normal XP, gold, loot, quest, kill-count, or death penalty
    rewards/outcomes.
  - Any player HP restoration during the duel fails the attempt; consumables
    spent before failure remain spent.
- `Crusader`: `Vow Trial` awakens `Vow Affirmation`.
  - Status: playable in the Church when a dormant Crusader Class Ring is
    equipped or stored and the character has already sworn a Paladin vow.
  - Promotion to `Paladin` permanently chooses one vow path. Legacy
    Paladin/Crusader saves with no vow can swear one at the Church.
  - `Vow Affirmation` records the chosen vow in
    `class_ring_awakening["data"]["Crusader"]["vow"]`. While the affirmed ring
    is equipped, aura benefits are multiplied by 1.5 and mark penalties or
    durations are multiplied by 0.5.
  - Bosses and Class Ring trial enemies are immune to mercy-victory effects.
  - `Redemption` grants `Redeem`, which attempts a boss-immune mercy victory.
    Success grants normal XP and gold, no item loot, and no kill, bounty, or
    quest credit. `Redemption Aura` lasts 3 encounters: -25% encounter rate,
    +20% XP/gold, and +10% Redeem chance. `Mark of Perdition` lasts 3
    encounters: +25% encounter rate and -20% XP/gold.
  - `Conquest` grants `Challenge`, marking the current enemy for 3 turns with
    bonus accuracy/damage. Defeating the challenged foe or an active bounty
    target triggers `Conquest Aura`, lasting 3 encounters and stacking up to 3:
    each stack grants +5% initiative and +5% weapon/magic damage. Fleeing
    applies `Mark of the Craven`, persisting until a bounty target is killed:
    -10% initiative and -10% weapon/magic damage.
  - `Protection` grants `Interpose`, a 2-turn guarded stance that increases the
    next block chance and mitigation. A successful block triggers `Protection
    Aura`, lasting 2 combat turns and stacking up to 5: each stack grants +3%
    block chance and +5% block mitigation. Becoming stunned, prone, or asleep
    applies `Mark of Vulnerability`, increasing physical/melee damage taken by
    20% until incapacitation ends.
  - `Retribution` grants `Judgment Riposte`, a 2-turn retaliatory stance. The
    next enemy attack triggers a weapon/Holy counter; if it kills, `Retribution
    Aura` lasts 6 encounters instead of 3. The aura grants +10% dodge and +15%
    critical damage. Being disarmed or preparing the stance with no weapon
    applies `Mark of Mercy`; if HP is below 10%, the next damaging enemy melee
    hit is lethal. Vow Affirmation lowers this threshold to 5%.
- `Dragoon`: `Guard The Fall` awakens the existing `+1 Jump Mod` and adds
  `Meteor Guard`, a two-turn shield equal to 25% of Jump landing damage.
  - Status: playable in the Barracks when a dormant Dragoon Class Ring is
    equipped or stored.
  - The trial has no normal XP, gold, loot, quest, kill-count, or death penalty
    rewards/outcomes.
- `Stalwart Defender`: `Siege Trial` awakens `Guard Meter`, which builds under
  defensive pressure and can be spent to reduce major incoming hits.
  - Status: playable in the Barracks when a dormant Stalwart Defender Class
    Ring is equipped or stored.
  - The trial has no normal XP, gold, loot, quest, kill-count, or death penalty
    rewards/outcomes.

### Mage Branch

- `Wizard`: `Four Formulae` awakens `School Streak`. Failed spell riders for
  the same school add +15% rider chance; four stacks guarantee the next
  eligible rider.
  - Status: playable in the Church when a dormant Wizard Class Ring is equipped
    or stored.
- `Shadowcaster`: `Debt Cap Trial` awakens `Umbral Debt`. Shadow damage stores
  healing reserve, while overcapping creates backlash.
  - Status: playable in the Church when a dormant Shadowcaster Class Ring is
    equipped or stored.
- `Knight Enchanter`: `Arcane Duel` awakens the existing `Mana Tap+` ring hook.
  - Status: playable in the Church when a dormant Knight Enchanter Class Ring is
    equipped or stored.
- `Grand Summoner`: `Conduit Ritual` permanently sacrifices 5% max HP and
  awakens +30% HP and damage for current and future summons.
  - Status: playable in the Church when a dormant Grand Summoner Class Ring is
    equipped or stored.

### Footpad Branch

- `Rogue`: `Loaded Game` awakens `Loaded Dice`, giving failed luck checks a 15%
  chance to become successes.
  - Status: playable at the Old Warehouse when a dormant Rogue Class Ring is
    equipped or stored.
- `Seeker`: `Cartographer's Proof` awakens `Hidden Cache`, one depth-weighted
  cache per sufficiently mapped dungeon level.
  - Status: playable at the Old Warehouse when a dormant Seeker Class Ring is
    equipped or stored.
- `Ninja`: `No-Trace Contract` awakens `First Strike Plus`, doubling the first
  standard attack when the Ninja has initiative.
  - Status: playable at the Old Warehouse when a dormant Ninja Class Ring is
    equipped or stored.
- `Arcane Trickster`: `Impossible Theft` awakens `Spell Steal Buff`, granting
  +20% Magic damage and +10% dodge for 3 turns after a successful spell steal.
  - Status: playable at the Old Warehouse when a dormant Arcane Trickster Class
    Ring is equipped or stored.

### Healer And Pathfinder Branches

- `Templar`: `Relic Defense` awakens `Ordered Blessings`, rotating Regen,
  Defense, and Holy damage blessings through relevant actions.
  - Status: playable in the Church when a dormant Templar Class Ring is equipped
    or stored.
- `Master Monk`: `Purity Rite` awakens `Martial Master`, granting +50% damage
  and armor while unarmed and unarmored.
  - Status: playable in the Church when a dormant Master Monk Class Ring is
    equipped or stored.
- `Archbishop`: `Miracle Vigil` awakens `Divine Intervention`, a once-per-combat
  35% chance to heal 25% max HP on first falling below 50% HP.
  - Status: playable in the Church when a dormant Archbishop Class Ring is
    equipped or stored.
- `Troubadour`: `Lost Ballad` awakens `Encore`, causing expired songs to trigger
  one final weaker effect.
  - Status: playable in the Church when a dormant Troubadour Class Ring is
    equipped or stored.
- `Lycan`: `Control Rite` awakens `Controlled Frenzy`, reducing lock-in
  penalties and improving healing while locked in.
  - Status: playable in the Church when a dormant Lycan Class Ring is equipped
    or stored.
- `Astromancer`: `Star Chart` awakens `Constellation Cycle`, advancing active
  constellations through casting and granting matching bonuses.
  - Status: playable in the Church when a dormant Astromancer Class Ring is
    equipped or stored.
- `Soulcatcher`: `Ancestral Totem Rite` awakens `Aspect Evolution`, improving
  Soul Aspect based on distinct enemy types harvested.
  - Status: playable in the Church when a dormant Soulcatcher Class Ring is
    equipped or stored.
- `Beast Master`: `Pack Trial` awakens `Shared Recovery`, echoing a smaller heal
  to the bonded partner when the hero or companion is healed.
  - Status: playable in the Church when a dormant Beast Master Class Ring is
    equipped or stored.
