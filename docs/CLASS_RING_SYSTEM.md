# Class Ring System

This is the durable Class Ring system reference. It records shipped activation
flows, class-specific awakening rules, persistent state expectations, and
remaining tuning or presentation follow-up.

## Current Implementation Status

Playable activation flows and their advertised V1 combat riders are implemented
for `Grandmaster of Arms`, `Demonologist`, `Archdruid`, `Berserker`, `Dragoon`,
`Stalwart Defender`, `Wizard`, `Shadowcaster`, `Knight Enchanter`,
`Thaumaturgist`, `Rogue`, `Seeker`, `Ninja`, `Arcane Trickster`, `Crusader`,
`Templar`, `Hierophant`, `Master Monk`, `Archbishop`, `Troubadour`, `Lycan`,
`Astromancer`, `Soulcatcher`, and `Beast Master`.

Supporting class mechanics, saved state, status text, and Class Ring hooks are
part of the shipped critical class-kit baseline. Future changes are
presentation review, evidence-driven tuning, or separately specified expansion.
Radar-style Wizard visualization remains optional; the six affinity values are
currently exposed as readable text.

- Weapon Master starts Weapon Discipline and active Weapon Arts; Berserker
  carries that progress forward; Grandmaster of Arms deepens it with Class Ring
  binding and Perfect Bound Art.
- Sorcerer/Wizard School Affinity is implemented as a 0-based six-school wheel:
  Sorcerer caps at 50 with tier-2 upgrades, Wizard caps at 100 with tier-3
  upgrades and awakened-ring mastery buffs.

The standard Class Ring acquisition remains the Hooded Figure reward after the
Red Dragon quest. The ring's second-promotion power is dormant until awakened by
the current class's path.

## Readability Baseline

Class Ring presentation must distinguish possession and activation without
changing mechanics:

- `Inventory only`: the ring is owned but not town-visible for activation.
- `Stored`: the ring is town-visible from Barracks storage, but equipped-only
  effects are inactive.
- `Equipped`: the ring is town-visible and can apply equipped-only awakened
  effects.
- `Dormant`: the activation path has not been completed.
- `Awakened`: the activation path is complete; descriptions still state whether
  the effect is active while equipped or waiting to be equipped.

Special systems keep bespoke wording: Grandmaster binding names the Secret
Master trial and bound weapon, Demonologist text separates basic contracts from
empowered contracts and imprisoned echo identity, and Archdruid text separates
Fourfold/Grove progress from equipped Harmony Bonus.

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

Successful main-hand and offhand weapon hits can grant base `+1` discipline XP
to that weapon type. Victory can grant base `+3` bonus discipline XP to equipped
weapon types that landed at least one hit, and successful Weapon Arts can grant
base `+2` discipline XP. These are whole-XP insight rolls, not fractional
awards. Intelligence modifies the chance to gain insight, while performance
modifies the base chance: critical hits roll better than ordinary hits, Weapon
Arts roll better again, and victory rolls separately. Enemy promotion level
scales eligibility and chance: `pro_level = 0` grants no Weapon Discipline XP,
`pro_level = 1` grants half the baseline chance, `pro_level = 2` grants baseline
chance, and higher promotion levels scale upward. Discipline uses 10 increasing
ranks with a slower mastery curve: rank 1 begins at `24` XP and rank 10 at
`1290` XP.

The Character Menu surfaces this as a `Weapon Discipline` tab for Weapon Master,
Berserker, and Grandmaster of Arms, using a full-width per-weapon board with
icons, rank/XP progress bars, and visual equipped highlighting. Classes without
a class-usage mechanic hide the middle mechanic tab. Rank threshold crossings
also report in combat text; the first rank names the newly unlocked weapon art.
The pygame promotion preview shows the class transition, highlights promotion
stat deltas, previews the post-promotion Character Menu tabs, and highlights
the `Weapon Discipline` tab for Weapon Master. It briefly frames weapon use,
worthy fights, weapon arts, and Intelligence as the practical path into the
mechanic without exposing the underlying roll math. The pygame promotion flow
adds one concise congratulations popup after success, but does not add extra
tutorial popups after the redesigned preview; warnings, errors, and required
branch choices may still interrupt the flow.

Each rank grants `+0.5%` accuracy and `+1%` technique proc chance for that
weapon type. At rank 10 this is `+5%` accuracy and `10%` technique chance.
Weapon Master now starts this same Weapon Discipline progression before second
promotion, using the existing save state so progress carries through Berserker
or into Grandmaster of Arms.
To reinforce that INT represents martial study as well as spellcraft, Weapon
Master and Grandmaster of Arms each gain `+1 INT` in their promotion stat
bonuses, trading one point from their prior pure martial peak stat.

### Weapon Arts

Weapon Discipline also unlocks active MP-cost weapon arts. Each art requires
the matching weapon type. Its tree node unlocks at rank 1, a second tree node
at rank 5 replaces it with a stronger level-2 form, and discipline mechanics
reach mastery at rank 10. Grandmaster of Arms can then purchase a level-3 form
that replaces level 2. Weapon-art nodes use only these discipline-rank gates,
not global level:

- `Fist`: `Iron Palm`.
- `Dagger`: `Hemorrhage`.
- `Sword`: `Riposte Line`.
- `Club`: `Low Sweep`.
- `Longsword`: `Guard Cleaver`.
- `Battle Axe`: `Reaver's Mark`.
- `Polearm`: `Brace`.
- `Hammer`: `Anvil Strike`.

Berserker's tab and tree show only Longsword, Battle Axe, Polearm, and Hammer.
Grandmaster of Arms retains all eight weapon types. Perfect Form adds `1%`
damage and `0.5%` hit per equipped discipline rank; Adaptive Arsenal adds
`0.5%` parry and `1%` counterattack critical chance per rank.

### Class Ring Binding

The Grandmaster Class Ring holds one active weapon binding at a time. When worn,
it doubles the chosen weapon discipline bonus:

- Rank 10 unbound: `+5%` accuracy and `10%` technique chance.
- Rank 10 bound and ring equipped: `+10%` accuracy and `20%` technique chance.

Rebinding is available immediately after activation through a harder Secret
Master gauntlet. Rebinding replaces the active weapon binding.

The awakened, equipped Grandmaster Class Ring also perfects the active art for
the bound weapon type, adding one conservative mastered-effect bonus on top of
the rank 10 art behavior.

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

The promotion-kit V1 pass keeps this two-stage progression and adds
corruption as a persistent risk/reward meter, patron favor/resentment as an
intent-access modifier, and stronger familiar echo effects. The
awakened ring remains the source of the echo identity: `Homunculus` stabilizes
protection/restoration bargains, `Fairy` improves sustain and corruption
cooling, `Mephit` pushes harmful contracts toward higher power and corruption,
and `Jinkin` adds a once-per-combat lucky twist chance.

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
  drained. Mastery unlocks the Tree of Life oak-form ability.
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

The promotion-kit V1 pass adds Archdruid-only combat `Aspect Harmony` without
changing Fourfold Balance persistence. Venom, Stone, Growth,
and Storm actions represent short-lived combat aspects that can be spent through
`Fourfold Surge`; awakened/equipped `Harmony Bonus` keeps its current
total-attunement scaling while raising the combat Harmony cap and preserving one
represented aspect once per combat after a clean Surge.

## Existing Second-Promotion Classes

All pre-existing second-promotion Class Ring effects now follow Quest
Awakening. The ring can be earned before awakening, but class-specific effects
remain dormant until the matching class completes its activation path. Legacy
awakening state is saved in `class_ring_awakening`.

The ring must be equipped or placed in Barracks storage for activation helpers.
Inventory-only rings do not count as visible town recognition.

Activation questlines, town gates, dormant/awakened ring state, and the class
mechanics below are implemented. The remaining work in this area is tuning,
additional visual presentation, and playtest follow-up.

### Warrior Branch

- `Berserker`: `No Healing Duel` awakens `Bloodied Crits`. While worn, the
  ring grants +10% crit below 50% HP, or +15% crit and +15% weapon damage below
  25% HP.
  - `Battle Scars`: after a non-trial victory at 10% HP or lower, Berserkers
    roll a 10% chance to gain 1 scar, capped at 20. Each scar permanently
    increases max HP by about 1% at the time it is earned and grants +0.5%
    weapon damage while below 25% HP.
  - Combat-only `Bloodied Momentum` builds once per player/enemy action below
    50% HP, gains one extra stack once per round below 25%, and has a 3/4/5 cap
    at 0/10/20 scars. Heavy weapon arts and `Final Assault` consume it for
    accuracy/damage pressure; Battle Scars preserve one clean spend at 10+
    scars, and awakened/equipped `Bloodied Crits` preserves one missed spend.
    At 20 scars, the victory stability threshold rises from 10% to 15% HP.
  - Status: playable in the Barracks when a dormant Berserker Class Ring is
    equipped or stored.
  - The duel has no normal XP, gold, loot, quest, kill-count, or death penalty
    rewards/outcomes.
  - Any player HP restoration during the duel fails the attempt; consumables
    spent before failure remain spent.
- `Crusader`: `Vow Trial` awakens `Vow Affirmation`.
  - Status: playable in the Church when a dormant Crusader Class Ring is
    equipped or stored and the character has already sworn a Paladin vow.
  - Promotion to `Paladin` permanently chooses one vow path. A Paladin or
    Crusader with missing vow state can swear one at the Church.
  - `Vow Affirmation` records the chosen vow in
    `class_ring_awakening["data"]["Crusader"]["vow"]`. While the affirmed ring
    is equipped, aura benefits are multiplied by 1.5 and mark penalties or
    durations are multiplied by 0.5.
  - The promotion-kit V1 pass adds combat-only `Oath Conviction` to the
    Paladin/Crusader vow loop. Signature-vow actions and their clean outcomes
    build Conviction; the separate `Oath's Judgment` and `Oath's Shelter`
    techniques consume all stacks for vow-specific offense or defense.
    Required Tempered Conviction makes the effective Paladin/Crusader caps
    `3/4`. Awakened/equipped `Vow Affirmation` preserves `1` Conviction once
    per combat after an empowered technique applies its primary effect.
    Conviction never cleanses, shortens, or disables mark drawbacks.
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
- `Dragoon`: `Guard The Fall` awakens `Aerial Supremacy`, preserving the
  legacy `+1 Jump Mod` hook internally for compatibility.
  - The promotion-kit V1 pass replaces the displayed awakened identity with
    `Aerial Supremacy`. The internal `+1 Jump Mod` alias remains accepted by
    tests, but the ring no longer grants extra active Jump modification
    capacity.
  - `Aerial Supremacy` enhances the automatic Aerial Tempo follow-through after
    a clean Jump landing from `+6%` damage and `+3` accuracy points per stack
    to `+8%` damage and `+4` accuracy points per stack. A clean damaging Jump
    creates a two-turn Landing Shield equal to 15% of actual Jump damage,
    minimum one. A new landing refreshes the larger shield; it does not stack.
    Incoming damage depletes it, and status presentation uses only `Aerial
    Supremacy` and `Landing Shield`, never a separate Meteor Guard payoff.
  - Status: playable in the Barracks when a dormant Dragoon Class Ring is
    equipped or stored.
  - The trial has no normal XP, gold, loot, quest, kill-count, or death penalty
    rewards/outcomes.
  - The Lancer/Dragoon Recover Jump Red Dragon route resolves the Red Dragon
    quest by restoring Kaelenon's humanoid transformation ability; this remains
    compatible with standard Class Ring acquisition and `Dragon's Fury` unlock.
- `Stalwart Defender`: `Siege Trial` awakens `Guard Meter`, which builds under
  defensive pressure and can be spent to reduce major incoming hits.
  - `Resolve` / `Guard Meter`: max 100. Defending, blocking, and mitigated
    physical damage build Resolve. While the awakened ring is equipped, a major
    incoming hit automatically spends 100 Resolve to reduce that hit by 40%.
  - Resolve is a baseline Sentinel/Stalwart resource. Sentinel spends it on
    eight shield and tempo actions: Hold the Line, Brace Wall, Spell Block,
    Bulwark Guard, Purge Weakness, Repercussion, Boast, and Focused Assault.
    Shield Riposte and Spell Reflection are passive modifiers. Spell Block
    absorbs compatible hostile projectile spells using spell and shield
    strength; Spell Reflection may return the blocked damage. Stalwart keeps
    those actions and adds the full-bar Resolve Bursts Citadel Aegis, Ironwall
    Revenge, Last Bastion, and Stronghold. The four Bursts are learned after
    four uses in separate associated-action mastery tracks carried forward
    from Sentinel and persisted through save/load. Mirror
    Bastion raises Magic Defense by 50 while its spell-defense payoff is active. Awakened/equipped
    `Shield Mastery` remains the strongest automation layer for major-hit
    mitigation and reads/spends this same Resolve value without a duplicate
    gain path.
  - Status: playable in the Barracks when a dormant Stalwart Defender Class
    Ring is equipped or stored.
  - The trial has no normal XP, gold, loot, quest, kill-count, or death penalty
    rewards/outcomes.

### Mage Branch

- `Sorcerer`/`Wizard`: `Four Formulae` awakens `School Streak`. Failed spell
  riders for the same school add +15% rider chance; four stacks guarantee the
  next eligible rider.
  - The effect is connected to Paralyzer, Ejection Gale, Subzero, and
    Unrelenting Waves once per spell action. Failure builds the persistent
    school streak, success resets it, and four failures guarantee and consume
    the next eligible opportunity. Player-facing ring copy keeps the formula
    and counter hidden.
  - `School Affinity` is specialization-aware. Classical Force tracks the six
    elemental schools; Arcane Tradition tracks Arcane affinity and presents only
    that school in the mechanic panel. Sorcerer affinity caps at 50; Wizard
    affinity caps at 100. Matching casts raise affinity by 2. Elemental
    specialization lowers the opposite by 1 and drifts other elemental schools
    down by 0.2.
    Opposites are `Fire`/`Ice`, `Water`/`Electric`, and `Earth`/`Wind`.
    Matching affinity grants +1% matching spell damage per full 10 affinity.
  - Sorcerer can purchase the matching tier-2 elemental or Arcane spell upgrade at
    30 affinity and gains mastery support at 50. Wizard unlocks tier-3 upgrades at
    80 and final mastery at 100.
  - Awakened, equipped Wizard Class Ring raises matching affinity gain to +3 and
    enables final-mastery 3-stack school buffs on matching casts.
  - Status: playable in the Church when a dormant Wizard Class Ring is equipped
    or stored.
- `Shadowcaster`: `Debt Cap Trial` awakens `Umbral Debt`. Shadow damage stores
  healing reserve, while overcapping creates backlash.
  - The promotion-kit V1 pass makes Umbral Debt a baseline Shadowcaster reserve
    and adds `Shade of Ahool` as a debt-spending shadow form. The awakened, equipped
    Class Ring raises the debt cap, preserves low-HP auto-healing, and reduces
    Shade of Ahool backlash conversion.
  - Shade now uses one class-kit timer and only its authored shadow form
    effects. Shade expiration and low-HP auto-healing convert stored backlash
    once, with ring stabilization and familiar variations applied during the
    conversion.
  - Status: playable in the Church when a dormant Shadowcaster Class Ring is
    equipped or stored.
- `Knight Enchanter`: `Arcane Duel` awakens `Weave Memory`, preserving the
  existing `Mana Tap+` ring hook internally for compatibility.
  - Knight Enchanter inherits Spellblade's combat-only Arcane and Elemental
    pools: one charge per damaging spell action, one slot per pool or two each
    with Storage Capacity, and full release on the next damaging weapon hit.
    Counter Charge uses the incoming spell category, misses preserve both pools,
    and each matching Amplify doubles its pool from 12% to 24% per charge.
  - Knight Enchanter casts also establish a two-slot Foundation/Accent pattern.
    Enchanted Assault, Aegis Weave, and Spellbind consume that pattern with the
    same typed charge pools. An awakened, equipped Arcane Duel ring preserves
    the spent Accent as the next Foundation. It does not add another meter.
  - Status: playable in the Church when a dormant Knight Enchanter Class Ring is
    equipped or stored.
- `Thaumaturgist`: `Conduit Ritual` permanently sacrifices 5% max HP and
  awakens +30% HP and damage for any of the 14 named Xenids.
  - A newly chosen member of the fixed roster applies the awakened multiplier
    when its combat stats are initialized.
  - Conduit Command now empowers exactly the next committed Xenid action and
    expires on the summon lifecycle boundaries. A perfected conduit adds its
    lesser signature only while the awakened ring is equipped.
  - All fourteen borrowed invocations, including Hodag and Caladrius, use
    authored damage types, ordinary mitigation, and distinct thematic riders.
  - Status: playable in the Church when a dormant Thaumaturgist Class Ring is
    equipped or stored.

### Footpad Branch

- `Rogue`: `Loaded Game` awakens `Loaded Dice`, giving failed luck checks a 15%
  chance to become successes. The promotion-kit V1 pass adds
  combat-only `Fortune` and `Misfortune`, Fortune smoothing for representative
  risky actions, Misfortune severity payoff after clean risky successes, and
  `Cheat Death`; when awakened and equipped, `Loaded Dice` preserves 1 point of
  a spent meter once per combat after a clean Fortune or Misfortune payoff.
  - Failed eligible theft, risky-attack, and Cheat Death checks now call the
    conversion directly. Fortune and Misfortune resolve once per meaningful
    action, Jinx weakens real accuracy and luck checks, and the two learned loot
    passives affect only eligible ordinary rewards. Meter preservation occurs
    only after one clean payoff per combat.
  - Status: playable in the Thieves Guild backroom when a dormant Rogue Class Ring is
    equipped or stored.
- `Seeker`: `Cartographer's Proof` awakens `Hidden Cache`, one depth-weighted
  cache per sufficiently mapped dungeon level. The promotion-kit V1 pass adds
  persistent enemy-type `Case Journal`
  progress, combat-only `Revelation`, and Seeker `Wayfinding`; when awakened
  and equipped, `Hidden Cache` keeps its cache identity while adding small
  insight smoothing after clean `Inspect` or telegraph reads.
  - Hidden Cache availability and claim helpers are connected to mapped-floor
    rewards. Ring insight smoothing, Revelation spending, Case Journal
    milestones, and Wayfinding movement effects are part of the shipped V1
    class-kit closure.
  - Status: playable in the Thieves Guild backroom when a dormant Seeker Class Ring is
    equipped or stored.
- `Ninja`: `No-Trace Contract` awakens `No-Trace Opener`, preserving the
  legacy internal `First Strike Plus` hook while doubling the first standard
  Ninja Blade attack when the Ninja has initiative. It applies one opener mark
  before the roll, spends all marks even on a miss, and preserves one mark once
  per combat after a successful payoff against a surviving target.
  - Status: playable in the Thieves Guild backroom when a dormant Ninja Class Ring is
    equipped or stored.
- `Arcane Trickster`: `Impossible Theft` awakens `Arcane Larceny`, preserving
  the legacy internal `Spell Steal Buff` hook while granting +20% Magic damage
  and +10% dodge for 3 turns after a successful spell steal. The promotion-kit
  V1 pass adds combat-only `Stolen Charge`; when awakened and equipped,
  `Arcane Larceny` preserves 1 Charge once per combat after a clean charged
  payoff.
  - `Steal Spell`: available to `Spell Stealer` and `Arcane Trickster`. It
    requires a concrete `Blank Scroll` from the Thieves Guild shop/scroll loot table.
    On success, the blank is consumed and replaced with a usable stolen-spell
    scroll that preserves the stolen spell identity and normal scroll targeting
    rules. Class Ring trial enemies are immune.
  - Shipped: the three-turn buff requires the awakened ring to be equipped and
    clears at lifecycle boundaries. Stolen Charge resolves once per eligible
    action through typed Arcane mitigation, with validated theft costs and
    once-per-combat clean-payoff preservation.
  - Status: playable in the Thieves Guild backroom when a dormant Arcane Trickster
    Class Ring is equipped or stored.

### Healer And Pathfinder Branches

The September 2026 critical closure pass connected the previously orphaned V1
riders in this section, including Ordered Blessings rotation, full-Ki Dim Mak,
Controlled Frenzy smoothing, Soulcatcher aspect scaling, active-sign Threaded
Cast, Archdruid Aspect preservation, and Beast Master command enhancement. See
`CLASS_KIT_DESIGN_GATES.md` before changing ring numbers or expanding mechanics.

- `Templar`: `Relic Defense` awakens `Ordered Blessings`, rotating Regen,
  Defense, and Holy damage blessings through relevant actions.
  - The promotion-kit V1 pass adds combat-only `Devotion` to the
    Cleric/Templar branch. Cleric starts the holy defender rhythm through
    healing, Holy pressure, shield utility, and `Pious Bounty`; Templar raises
    the cap and spends Devotion through ward actions such as `Sanctuary Ward`
    and `Relic Aegis`.
  - `Holy Retribution` becomes a Devotion window while keeping
    its existing holy-fire attack flavor, and awakened/equipped
    `Ordered Blessings` preserves the current Regen/Defense/Holy Damage
    rotation while improving matching Devotion payoffs and preserving
    `1` Devotion once per combat.
  - Status: playable in the Church when a dormant Templar Class Ring is equipped
    or stored.
- `Hierophant`: `Consecration Rite` awakens `Sacred Conduit`, preserving `1`
  Devotion once per combat after a clean `Consecrated Conduit` payoff and
  lightly improving staff-conduit holy damage.
  - The promotion-kit pass adds Hierophant as the magical Cleric fork:
    staff/shield/light armor, `Staff Conduit`, late combat-caster spells, and
    a Devotion spender that rewards staff, Smite, and Holy follow-through.
  - Status: playable in the Church when a dormant Hierophant Class Ring is
    equipped or stored.
- `Master Monk`: `Purity Rite` awakens `Martial Master`, granting +50% damage
  and armor while unarmed and unarmored.
  - The promotion-kit V1 pass adds combat-only `Ki`, redesigns `Dim Mak` as a
    full-Ki Master Monk finisher, and adds the Master Monk-only
    `Ruyi Jingu Bang` ultimate staff through the existing `Unobtainium`
    blacksmith flow. `Dim Mak` recognizes `Ruyi Jingu Bang` for its
    no-penalty staff exception.
  - Awakened/equipped `Martial Master` preserves the unarmed/no-armor bonus
    while improving Ki discipline and `Dim Mak` reliability.
  - Status: playable in the Church when a dormant Master Monk Class Ring is
    equipped or stored.
- `Archbishop`: `Miracle Vigil` awakens `Divine Intervention`, a once-per-combat
  35% chance to heal 25% max HP on first falling below 50% HP.
  - The promotion-kit V1 pass adds combat-only `Prayer` to the
    Priest/Archbishop branch. Priest builds Prayer through meaningful healing,
    cleansing, divine support, Holy pressure, and anti-magic setup, while
    Archbishop raises the cap and spends Prayer through `Supplication` and
    `Great Benediction`.
  - `Great Gospel` becomes a major Prayer reset/setup window
    while preserving its cleanse and divine power-up identity, and
    awakened/equipped `Divine Intervention` keeps its current emergency heal
    behavior while preserving `1` Prayer once per combat after a clean
    Supplication or Benediction payoff.
  - Status: playable in the Church when a dormant Archbishop Class Ring is
    equipped or stored.
- `Troubadour`: `Lost Ballad` awakens `Encore`, causing expired songs to trigger
  one final weaker effect.
  - `Bard Songs`: `Bard` and `Troubadour` can perform one active 3-turn song at
    a time while a musical instrument is equipped in `OffHand`. `Valor` raises
    weapon and magic damage, `Shelter` reduces incoming damage, and `Renewal`
    pulses HP/MP recovery. `Troubadour` improves song strength by 50%; awakened
    `Encore` adds one final 50%-strength pulse or beat when a song expires.
  - The promotion-kit V1 pass adds Troubadour `Repertoire` mastery for advanced
    songs, combat-turn practice, clean-finish tracking, and combat-only
    `Crescendo` codas. Awakened/equipped `Encore` keeps its current final
    weaker effect and preserves 1 Crescendo after a natural coda.
  - Status: playable in the Church when a dormant Troubadour Class Ring is
    equipped or stored.
- `Lycan`: `Control Rite` awakens `Controlled Frenzy`, reducing lock-in
  penalties and improving healing while locked in.
  - `Moon Cycle`: dungeon steps advance moon phase every 120 steps through
    `New`, `Waxing`, `Full`, and `Waning`. While transformed, moon phase
    affects damage and Frenzy Lock risk. Kills and low HP can trigger Frenzy
    Lock; Full Moon has the highest risk and longest duration. Awakened
    `Controlled Frenzy` improves healing received while locked by 25%.
  - Status: playable in the Church when a dormant Lycan Class Ring is equipped
    or stored.
- `Astromancer`: `Star Chart` awakens `Constellation Cycle`, strengthening
  active-sign Runic Boost fate floors while the Class Ring is equipped.
  Astromancer natural spell casts advance the active constellation, and the
  baseline Diviner/Astromancer rune system remains per-save spell empowerment
  rather than gear modification. The promotion-kit V1 pass keeps
  `Constellation Cycle` as the ring identity and adds active-sign `Threaded
  Cast` reliability/output support while the awakened ring is equipped.
  - Status: playable in the Church when a dormant Astromancer Class Ring is
    equipped or stored.
- `Soulcatcher`: `Ancestral Totem Rite` awakens `Aspect Evolution`, improving
  Soul Aspect based on distinct enemy types harvested.
  - `Nature Totems`: Shaman and Soulcatcher can bind one-time elemental
    communions at Underground Spring, Boulder, Fire Path, and the floor-3
    strange-draft passage to unlock `Tsunami`, `Earthquake`, `Fireball`, and
    `Tornado`. Active elemental Totems can pulse the highest unlocked matching
    spell at reduced potency, Staffs improve pulse cadence and matching
    player-cast nature spells, and Water Totem adds Magic Defense plus partial
    spell absorption into healing.
  - `Soul Drain`: Soulcatcher learns this level-4 spell as nonlethal
    current-HP damage; Soul Totem can pulse it when Soul Aspect is active and
    the spell is known.
  - The promotion-kit V1 pass adds combat-only `Totem Resonance` stacks from
    matching casts and successful Totem pulses, plus `Totem Surge` to spend
    those stacks for a forced reduced-potency pulse. The awakened, equipped
    Soulcatcher Class Ring raises the Resonance cap and improves Surge for all
    aspects while keeping `Aspect Evolution` compatible with Soul harvests.
  - Status: playable in the Church when a dormant Soulcatcher Class Ring is
    equipped or stored.
- `Beast Master`: `Pack Trial` awakens `Shared Recovery`, echoing a smaller heal
  to the bonded partner when the hero or companion is healed.
  - The promotion-kit V1 pass keeps one persistent tamed companion, adds
    companion bond growth, gives Beast Master direct companion commands, and
    lets the awakened, equipped Class Ring scale `Shared Recovery` from 25%
    toward 35% with bond. The ring also improves Pack Strike accuracy/output,
    Guard Partner strength/duration, Harry Prey pressure, and Mend Wounds
    healing without creating another companion action.
  - Status: playable in the Church when a dormant Beast Master Class Ring is
    equipped or stored.

## Follow-Up Gate

Current activation flows, awakening requirements, and persistent ring state are
the compatibility baseline. Future Class Ring work should be limited to tuning,
visual/readability presentation, and playtest response unless a dedicated spec
changes activation flow or awakening rules.

Radar-style Wizard affinity visualization remains deferred; the six affinity
values stay readable text first. Any new activation flow or altered awakening
rule must define eligibility, trigger source, required ring location, UI text,
save flags/state changes, failure behavior, and focused tests before
implementation.
