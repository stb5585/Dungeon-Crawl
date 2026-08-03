# Class Kit Design Gates

This is the durable class-kit design gate reference. It records shipped
class-mechanics baselines, scope boundaries, and the one-page decision gates
used for deeper class-kit work. Balance validation lives in
`PLAYTEST_CHECKLIST.md`.

## Promotion Kit V1 Status

Status: `V1 Implemented, Tuning/Open Polish`

The promotion class-track V1 pass is implemented through the
`src/core/classes/promotion_kits/` package and runtime hooks in player state,
save/load, combat, data-driven abilities, class rings, Demonologist contracts,
nature Totems, Beast Master companion state, and class skill grants.

Implemented V1 coverage includes:

- Combat-only promotion meters for Foresight Threads, blade charge/Arcane
  Tempo, Bloodied Momentum, Oath Conviction, Aerial Tempo, Resolve,
  Fortune/Misfortune, Revelation, Death Mark, Stolen Charge, Devotion, Prayer,
  Ki, Crescendo, Aspect Harmony, Beast Master commands, and Totem Resonance.
- Persistent promotion state for summon bonds, Case Journal, Bard repertoire,
  Lycan control/Dragon Essence, Demonologist corruption/patron mood, and Beast
  Master companion bond.
- Named V1 active/passive abilities such as `Threaded Cast`, `Eclipse`,
  `Hold the Line`, `Bulwark`, `Shield Riposte`, `Sanctuary Ward`,
  `Relic Aegis`, `Supplication`, `Great Benediction`, `Dim Mak`,
  `Fourfold Surge`, `Totem Surge`, `Conduit Command`, borrowed summon
  invocations, Beast Master commands, `Winged Pounce`, and the Footpad-track
  passive identities.
- Display identity updates for `Aerial Supremacy`, `Arcane Tempo`,
  `No-Trace Opener`, and `Arcane Larceny` while preserving legacy internal
  compatibility hooks.
- Master Monk-only `Ruyi Jingu Bang` ultimate-staff content through the
  existing `Unobtainium` blacksmith flow, with class-specific staff selection
  so Archbishop, Master Monk, and general staff users receive the correct
  ultimate staff.
- Awakened-ring smoothing for `Loaded Dice`, `Ordered Blessings`,
  `Divine Intervention`, `Encore`, and bond-scaling `Shared Recovery`, plus
  representative Rogue `Cheat Death`, Fortune/Misfortune payoff, and
  Bard/Troubadour Crescendo coda hooks.
- Regression coverage in `tests/core/test_promotion_class_kits.py`, plus
  updated class-ring, data-driven ability, item-helper, and core-suite tests.

Remaining follow-up is no longer initial implementation work; it is tuning,
presentation, and later content expansion:

- Expand bespoke ability-by-ability riders, UI surfacing, and combat-log copy
  where the V1 pass currently uses compact shared hooks and representative
  integration.
- Broaden manual playtest and balance tuning for the new meters, especially
  preservation effects, payoff strength, and high-action-economy loops such as
  Totems, songs, summons, and Doublecast-adjacent divine support.
- Deeper narrative beats tying second-promotion identity back to `Voluntas`
  remain deferred until their quest/content spec defines timing, text, flags,
  and optional/required status.

## UI/Log Polish Acceptance Matrix

Status: `Presentation-Only V1`

This matrix defines the first UI/log readability polish pass for shipped
promotion kits. It is an acceptance reference for shared status text, combat
logs, and lightweight menu/exploration surfacing only. This pass must not
change meter gain/spend rules, class-ring activation, save schema, quest state,
combat math, or numeric balance.

| Track/class | Status surface requirements | Combat-log requirements | Menu/exploration/town requirements | Ring-readiness/readability requirement | Regression/manual acceptance target |
| --- | --- | --- | --- | --- | --- |
| Astromancer | Constellation, rune grid, Foresight Threads, pending `Threaded Cast`. | Thread gain/cap/spend, pending cast, negated payoff, Rewind snapshot, active-sign enhancement. | `Runic Boost` and `Threaded Cast` remain selectable only when valid. | Show awakened/equipped `Constellation Cycle` readiness without implying manual sign control. | Build Threads, prepare `Threaded Cast`, and verify status/log state in combat. |
| Demonologist | Corruption, active patron/mood, familiar echo, contract history summary where available. | Corruption gain/cooling, mood changes, twist/lucky-twist, withheld/unlocked intent notes. | Contract quote and Church Crypt review show costs, risk, patron, echo, and unlocked/withheld intent state. | Show contract echo/ring awakening state as contract shaping, not a generic stat boost. | Quote and resolve one contract, then inspect status and crypt review. |
| Shadowcaster | Umbral Debt with cap, backlash, Eclipse turns. | Debt gain, cap/backlash, Eclipse activation/expiration, auto-heal spend, backlash conversion. | None beyond normal skill availability. | Show awakened/equipped `Umbral Debt` cap/stability readiness. | Store debt, enter Eclipse, overcap into backlash, and verify lines stay visible. |
| Knight Enchanter | Blade Charge, Arcane Tempo, pending burst. | Charge store/overwrite/spend, miss consumption, Tempo gain, three-stack burst. | `Arcane Duel` text uses `Arcane Tempo` display identity. | Preserve legacy `Mana Tap+` compatibility while displaying `Arcane Tempo`. | Cast spell, attack with charge, and inspect Tempo status/logs. |
| Grand Summoner | Known summon bond values or best bond, Conduit readiness. | Bond gain, borrowed invocation, `Conduit Command`, True Name rider, expiration. | Summon menus keep current recall/summon behavior and show valid borrowed invocation availability. | Show awakened/equipped `Conduit Ritual` as summon scaling plus conduit rider readiness. | Gain bond, invoke a summon, prime conduit, and inspect status/logs. |
| Berserker | Battle Scars, Bloodied Momentum/cap, bloodied threshold state where relevant. | Momentum gain/cap/spend, miss preservation, heavy-art mutation, `Final Assault` use. | None beyond existing weapon-art menus. | Show awakened/equipped `Bloodied Crits` and preservation readiness when relevant. | Build Momentum below 50% HP and spend it on a heavy art. |
| Crusader | Vow, aura/mark, Oath Conviction/cap. | Conviction gain/spend, clean-outcome bonus, vow rider, mark/aura changes, preservation. | Vow Trial text remains explicit when no vow exists. | Show awakened/equipped `Vow Affirmation` preservation readiness. | Use sworn-vow action before and after ring awakening. |
| Dragoon | Aerial Tempo/cap, pending follow-through, landing shield if active. | Clean Jump gain, interruption cleanup, spend, follow-through, landing shield. | Jump modification UI keeps existing capacity and no longer promises extra active mod capacity. | Show awakened/equipped `Aerial Supremacy` readiness. | Land a clean Jump, follow through, and inspect shield/readiness text. |
| Sentinel/Stalwart Defender | Sentinel Resolve/cap/spends; Stalwart full-bar Resolve Surges. | Resolve gain/cap/spend, block, barrier, riposte, Surge unlock/progress, automatic major-hit mitigation. | Shield-required actions fail clearly when shield/offhand setup is invalid. | Show awakened/equipped `Guard Meter` auto-spend readiness without making it the only Stalwart identity. | Build Resolve as Sentinel, spend it on shield actions, then promote and inspect Resolve Surges. |
| Rogue | Fortune, Misfortune, `Jinx`, risky-action readiness. | Meter gain/spend/cap, Fortune smoothing, Misfortune payoff, `Cheat Death`, preservation. | Loot finds exclude invalid item categories and log as extra ordinary finds. | Show awakened/equipped `Loaded Dice` and once-per-combat preservation readiness. | Spend both meters and verify `Loaded Dice` status/logs. |
| Seeker | Case Journal progress/rank, Revelation/cap, sight/detail state where available. | Case progress, milestone, Revelation gain/spend, telegraph prediction, mobility smoothing. | `Hidden Cache` and movement tools report claim/failure/smoothing clearly. | Show awakened/equipped `Hidden Cache` availability/readiness. | Gain Case progress, build Revelation, and inspect status/logs. |
| Ninja | Death Mark/cap on current target when available, opener readiness. | Mark application/cap/spend, miss consumption, immunity/boss/trial downgrade, preservation. | Stealth/opener surfaces keep initiative requirements clear. | Show awakened/equipped `No-Trace Opener` readiness. | Apply marks, spend a finisher, and verify downgrade/preservation lines. |
| Arcane Trickster | Stolen Charge/cap, `Arcane Larceny` buff/preservation readiness through combat/HUD status, not a dedicated Character Menu tab. | Charge gain/spend/cap, stolen-scroll contribution, miss/negated consumption, preservation. | Spell-steal menus fail clearly without `Blank Scroll` or against trial enemies; stolen-spell scrolls appear in the combat `Spells` picker. | Show awakened/equipped `Arcane Larceny` readiness. | Steal/cast stolen magic from `Spells`, spend Charge, and inspect status/logs. |
| Templar | Devotion/cap, active ward, `Holy Retribution`, next blessing. | Devotion gain/cap/spend, ward strength, `Pious Bounty`, blessing rotation, preservation. | Shield/offhand requirements for `Relic Aegis` fail clearly. | Show awakened/equipped `Ordered Blessings` preservation readiness. | Spend Devotion before and after ring awakening. |
| Hierophant | Devotion/cap, pending `Consecrated Conduit`, staff+shield state, `Sacred Overchannel`. | Devotion gain/cap/spend, staff/holy payoff, warding, mana return, preservation, Power Core overchannel boost. | Staff-required action fails clearly; two-handed staff and shield compatibility displays correctly. | Show awakened/equipped `Sacred Conduit` preservation readiness. | Spend Devotion into `Consecrated Conduit`, land staff/Holy payoff, and inspect status/logs. |
| Archbishop | Prayer/cap, support/Benediction effects, `Great Gospel`, Intervention readiness. | Prayer gain/cap/spend, `Doublecast` boundary, Benediction, Gospel reset, Intervention, preservation. | Resurrection/support menus keep MP and target failures clear. | Show awakened/equipped `Divine Intervention` readiness and preservation state. | Use `Supplication`/`Great Benediction` and inspect logs/status. |
| Master Monk | Ki/cap, `Dim Mak` readiness, weapon penalty/exception state where relevant. | Ki gain/spend/cap, `Dim Mak` weapon penalty, staff drop/disarm, ultimate-staff exception. | Blacksmith ultimate selection shows `Ruyi Jingu Bang` when eligible. | Show awakened/equipped `Martial Master` readiness. | Build full Ki, use `Dim Mak`, and inspect weapon/ring messages. |
| Troubadour | Active song, turns/steps, Crescendo, repertoire count/progress. | Practice XP, clean finish, mastery, Crescendo gain/spend, coda, route coda, preservation. | Composition/performance menus distinguish sheet use from mastered repertoire. | Show awakened/equipped `Encore` preservation readiness. | Let a song expire naturally and inspect coda/preservation lines. |
| Lycan | Form state, moon phase, Frenzy Lock, control rank, Dragon Essence. | Stress, pushback, dismissal block, rank progress, `Winged Pounce`, essence unlock. | `Dismiss Form` and transformation menus explain locked/unavailable states. | Show awakened/equipped `Controlled Frenzy` as stability support, not rank progress. | Trigger stress, inspect control/ring text, and unlock Dragon Essence. |
| Archdruid | Represented Aspect Harmony, `Primal Ascendance`, Tree/Growth contribution. | Aspect gain/cap, `Fourfold Surge` spend, rider downgrade, preservation. | Grove/attunement surfaces remain persistent progression, not combat meter UI. | Show awakened/equipped `Harmony Bonus` readiness/preservation. | Represent two aspects, surge, and verify status/logs. |
| Beast Master | Companion name/species, bond/rank, Favored Enemy, pending command. | Bond gain/milestone, command use/expiration, hunt synergy, Shared Recovery echo. | Tame/replacement messaging makes one-companion scope clear. | Show awakened/equipped `Shared Recovery` bond-scaling readiness. | Tame/command companion, gain bond, and inspect healing echo logs. |
| Soulcatcher | Active Totem aspect, Resonance/cap, Soul harvest count. | Resonance gain/cap/spend, forced pulse, Soul nonlethal contribution, ring cap/output. | Totem aspect menu shows active aspect and communion availability. | Show awakened/equipped `Aspect Evolution` resonance cap/readiness. | Build Resonance, use `Totem Surge`, and inspect status/logs. |

## Class Mechanic Tab Triage

Status: `Decision Record, Implementation Follow-Up Needed`

The pygame Character Menu now supports a middle mechanic tab, but not every
class kit deserves one. Use this triage when deciding whether to add bespoke tab
content, keep a label backed by compact summary rows, or remove/demote a tab to
combat HUD/status/log presentation.

Tab decision bands:

- `Required`: the kit has persistent progression, roster/detail inspection,
  selectable configuration, or a town/menu-adjacent review need. A tab should
  exist and should eventually have bespoke content if the current generic
  summary does not explain the mechanic.
- `Not Needed`: the kit is combat-only or already has a better action/menu
  surface. Do not add a Character Menu tab unless a future spec adds persistent
  progression or configuration.
- `Too General`: the idea is an expansion concept, not a tab decision. Promote
  a one-page spec before deciding UI.

| Track/class | Current tab behavior | Tab decision | Additional implementation needed | Reasoning |
| --- | --- | --- | --- | --- |
| Weapon Master/Berserker/Grandmaster of Arms | `Weapon Discipline` bespoke tab exists. | `Required` | `No` for tab baseline; tune/readability evidence only. | Persistent per-weapon ranks, XP, equipped highlighting, and art unlocks need a durable review surface. |
| Paladin/Crusader | `Oath Conviction` bespoke tab exists. | `Required` | `No` for tab baseline; future only for oath-respec specs. | Permanent vow, signature skill, aura, mark, and Conviction rhythm need a stable review surface. |
| Lancer/Dragoon | `Aerial Tempo` bespoke tab exists with Jump Mod controls. | `Required` | `No` for tab baseline. | Jump modifications are selectable configuration and should live outside the combat action list. |
| Sentinel/Stalwart Defender | `Resolve` bespoke tab exists. | `Required` | `No` for tab baseline. | Resolve spends and Stalwart Surges are class-owned actions/payoffs with enough structure for a tab. |
| Summoner/Grand Summoner | `Summons` tab exists with roster/detail support. | `Required` | `Partial`: keep improving bond milestone/readiness and active-summon support text. | Multiple summons, bond values, invoke unlocks, and details are too dense for HUD-only presentation. |
| Ranger/Beast Master | `Companion & Hunt` tab exists with companion roster/detail and quarry-tracking support. | `Required` | `Partial`: future tuning for evolution payoff/stable scope only. | A persistent named companion, bond progression, and disciplined quarry tracking need inspection outside combat. |
| Warlock | `Familiar` tab exists through companion display. | `Required` | `Partial`: keep familiar growth/effect details readable. | Familiar identity persists and should be inspectable like other companions. |
| Demonologist | `Contracts` bespoke tab exists. | `Required` | `No` for tab baseline; tune hidden/revealed copy only. | Contract choice and patron state are menu/town-adjacent and too important to leave only in Crypt dialogue. |
| Sorcerer/Wizard | `School Affinity` bespoke tab exists. | `Required` | `No` for tab baseline; keep under-the-hood thresholds hidden. | Persistent affinity progression needs review and is not combat-only. |
| Diviner/Astromancer | `Runes` bespoke tab exists. | `Required` | `No` for tab baseline; keep advanced formula detail hidden. | Runes persist per save and are spent through spell empowerment, so a tab should explain inventory-like state. |
| Shaman/Soulcatcher | `Totems` bespoke tab exists plus separate Totem Aspects popup. | `Required` | `No` for tab baseline. | Totems have persistent communion unlocks plus active aspect configuration. |
| Inquisitor/Seeker | `Case Journal` bespoke tab exists. | `Required` | `No` for tab baseline. | Persistent Case Journal progress and route tools need an out-of-combat review surface. |
| Bard/Troubadour | `Crescendo` bespoke tab exists. | `Required` | `No` for tab baseline. | Song repertoire is persistent progression and advanced songs need readable mastery state. |
| Druid/Lycan | `Forms` bespoke tab exists for Druid/Lycan. | `Required` for Druid/Lycan | `No` for tab baseline. | Persistent transformation and Lycan control are identity systems, not just combat buffs. |
| Archdruid | `Aspects` bespoke tab exists. | `Required` | `No` for tab baseline. | Archdruid has both persistent attunement and combat-only aspect representation. |
| Shadowcaster | No mechanic tab; Umbral Debt appears in HUD/status/log surfaces. | `Not Needed` | `No` for a tab; keep debt/backlash/Eclipse readable through combat HUD, status rows, logs, and skill text. | The live decision is combat-only and resets, so a tab would mostly duplicate combat state. |
| Spellblade/Knight Enchanter | No mechanic tab; Blade Charge and Arcane Tempo appear in HUD/status/log surfaces. | `Not Needed` | `No` for a tab; explain compatible spell schools and alternation rhythm through promotion guidance, action text, HUD, and logs. | Charges and Tempo are combat-only and reset; the combat surface is the correct source of truth. |
| Thief/Rogue | No mechanic tab; Fortune/Misfortune appear in HUD/status/log/result surfaces. | `Not Needed` | `No` for a tab; solve risky-action eligibility through HUD/status hints, combat logs, action descriptions, and loot/result messages. | Manual evidence found clarity issues, but the strict tab rule keeps combat-only luck meters out of Character Menu. |
| Assassin/Ninja | No mechanic tab; Death Mark appears in HUD/status/log surfaces. | `Not Needed` | `No` for a tab; explain setup, finisher readiness, and No-Trace pressure through combat HUD, logs, and skill text. | Marks are combat-only and target-specific, so a persistent menu surface has limited value. |
| Monk/Master Monk | No mechanic tab; Ki appears in HUD/status/log/skill surfaces. | `Not Needed` | `No` for a tab; keep `Dim Mak`, weapon penalties, and ultimate-staff exception readable through combat and equipment messaging. | Ki is combat-only and the Master Monk equipment exceptions belong with skill/equipment feedback. |
| Priest/Archbishop | No mechanic tab; Prayer appears in HUD/status/log/skill surfaces. | `Not Needed` | `No` for a tab; keep Supplication, Benediction, Gospel, and Intervention readable through combat and support skill text. | Prayer is combat-only and largely action-driven. |
| Cleric/Templar/Hierophant | No mechanic tab; Devotion appears in status/log/skill text. | `Not Needed` | `No` for a tab; keep improving HUD/status/log/skill text. | Devotion is combat-only and the spec explicitly says it should not require a Character Menu mechanic tab. |
| Spell Stealer/Arcane Trickster | No mechanic tab; stolen scrolls live in combat `Spells`, Charge in HUD/status. | `Not Needed` | `No` for a tab; use Thieves Guild/backroom content for broader guidance. | Stolen Charge is combat-only and the spell inventory already has a primary action surface. |
| Broad expansions such as combo chains, sentient/leveling weapons, Maestro progression, summon bond death penalties, pet evolution/stables, Grove questlines, oath drift, heist caches, stealth rewrite, and scroll-economy redesign | No stable UI contract. | `Too General` | `Spec first` | These change mechanics, save state, economy, progression, or content scope; tab decisions should follow a promoted one-page spec. |

Implementation posture:

1. The bespoke tab baseline has shipped for `School Affinity`, `Contracts`,
   `Runes`, `Totems`, `Case Journal`, `Crescendo`, `Forms`, and `Aspects`.
   Future work should tune readability, hidden/revealed copy, and per-kit
   polish rather than reintroducing generic class summaries.
2. Do not add Character Menu tabs for combat-only meters unless a future spec
   adds persistent progression, configuration, roster/detail, or town/menu
   review needs.
3. Preserve the explicit no-tab decisions for Devotion and Stolen Charge until
   their specs change.
4. Treat broad expansion ideas as design gates, not implementation backlog.

## Class-Kit Balance Thresholds

Status: `Watch-First Thresholds`

These thresholds define when class-kit meter behavior, preservation effects, or
action-economy loops need closer evidence. They do not authorize numeric
tuning by themselves. Any balance change still needs simulator output, manual
playtest notes, and a promoted one-page tuning spec.

Threshold bands:

- `Pass`: the mechanic is visible, useful, and not dominant. It creates a
  recognizable class rhythm while preserving normal action tradeoffs.
- `Watch`: record the build, class/race/enemy matchup, level, gear/loadout,
  meter state, ring state, battle length, and relevant simulator payload. Rerun
  focused manual and simulator checks before deciding whether tuning is needed.
- `Tuning Gate`: promote a one-page balance spec before changing numbers,
  trigger rules, preservation behavior, or action-economy output.

Meter thresholds:

- `Watch` if a class-specific meter usually cannot produce one payoff within
  three ordinary eligible combats.
- `Watch` if a meter sits capped for most of a fight without meaningful
  spending pressure.
- `Watch` if a payoff can be rebuilt and spent repeatedly with no meaningful
  action, MP, target, risk, or opportunity-cost tradeoff.
- `Tuning Gate` if the same meter payoff dominates encounter outcomes across
  both simulator signal and manual playtest.

Preservation thresholds:

- `Watch` if once-per-combat ring preservation feels mandatory for baseline
  class function rather than smoothing.
- `Watch` if preserved resources routinely erase miss, immunity, negated
  payoff, or target-loss costs.
- `Tuning Gate` if preservation creates a repeatable same-turn or every-turn
  payoff loop.

Action-economy thresholds:

- `Watch` if autonomous or bonus outputs regularly exceed the player's direct
  action impact.
- `Watch` if Totems, songs, summons, companions, Doublecast-adjacent support,
  or route/economy codas produce low-interaction wins.
- `Tuning Gate` if a loop wins representative encounters while the player
  mostly defends, waits, or repeats one setup action.

Analytics hooks should remain lightweight. `CombatStats` may aggregate
classified `class_kit_events` and `action_economy_events` from existing action
names, BattleEngine result text, post-turn messages, and ability names. Missing
classifications are analytics gaps, not gameplay failures, and should be fixed
as reporting polish before any tuning decision.

## Progression Pacing Tables

Status: `Watch-First Pacing Reference`

These tables describe the current expected cadence for shipped persistent
class-kit progression on Bard/Troubadour, Beast Master, Lycan,
Summoner/Grand Summoner, and Inquisitor/Seeker. They are manual playtest and
review references only. They do not authorize balance changes, meter
gain/spend changes, rank-gate changes, simulator analytics changes, save-schema
changes, class-ring changes, or action-economy changes by themselves. Numeric
tuning still requires manual notes, existing balance-threshold evidence, and a
promoted one-page tuning spec.

| Track/class | Current progression rule | Expected ordinary cadence | Fast or narrow cadence | Watch trigger |
| --- | --- | --- | --- | --- |
| Bard/Troubadour | Crescendo gains `+1` per maintained combat song turn, caps at `3`, and spends only on natural expiration. Troubadour repertoire mastery requires `18` practice XP and `3` clean finishes. | Combat-only mastery should take `3` clean full 3-turn performances: each gives `+3` turn XP plus `+3` completion XP. | Exploration mastery can also take `3` clean full performances: each can give up to `+4` step XP plus `+3` completion XP. Composition `+1` XP buffers progress but never removes the `3` clean-finish requirement. | Watch if clean completions do not visibly move mastery, if interruption costs are unclear, or if codas/Encore make song loops win with low player input. |
| Beast Master | Companion bond caps at `100`; milestones are `25` `Trusted`, `50` `Battle-Trained`, `75` `Packmate`, and `100` `True Bond`. | Victory bond uses an inverse curve: low-bond companions usually gain larger chunks, while high-bond companions gain smaller chunks less often. | Favored Enemy active victories add an extra inverse-scaled practice opportunity rather than a guaranteed flat bump. | Watch if `Trusted` is not reachable after a handful of ordinary active wins, if high-bond growth still feels automatic, if replacement/tame state hides the pacing cost, or if command output regularly dominates direct player turns. |
| Summoner/Grand Summoner | Each summon has its own bond cap of `100`; milestones are `25`, `50`, `75`, and `100`. | Bond starts at summon level `2`; victory rolls a chance equal to enemy XP divided by that summon level's full XP span. A successful roll grants scaled `+1` to `+5` bond. | Low-XP fights often give no bond, while meaningful fights advance bond in proportion to their leveling value. Support actions do not add separate action bond. | Watch if low-level or low-threat fights become the best bond farm, if focused bond `50` feels unreachable, or if the chance-based cadence feels too opaque in logs/playtest notes. |
| Inquisitor/Seeker | Case Journal progress is per broad enemy type, caps at `100`, and milestones are `25` `Known Tells`, `50` `Weakness Brief`, `75` `Pattern Lock`, and `100` `Closed Case`. | `Inspect` plus visible-detail victory gains about `+7/combat`; milestones land near `4/8/11/15` combats against one enemy type. | Rich evidence loops with `Inspect`, `Exploit Weakness`, a visible telegraph, and victory gain about `+10/combat`; milestones land near `3/5/8/10` combats. Victory-only visible-detail progress gains `+4/combat`, or about `7/13/19/25` combats. | Watch if one enemy type cannot reach `Known Tells` after focused evidence gathering, or if spreading fights across many enemy types does not feel intentionally slower and readable. |
| Lycan | Control ranks are behavior-only. Each gate requires `3` matching successful stress records: `survive`, `dismiss`, `resist`, then `full_moon`. | Minimum full path is `12` phase-correct records: `Feral -> Muzzled`, `Muzzled -> Restive`, `Restive -> Tethered`, then `Tethered -> Tame`. | Real pacing depends on eligible stress opportunities, moon timing, and whether the player survives or resolves the correct behavior at the current gate. | Watch if a gate does not reasonably progress after 6-8 eligible opportunities, if the needed behavior is unclear, or if Class Ring/Dragon Essence appears to advance control rank. |

Pacing reads should record combat count or eligible opportunity count, relevant
actions, ring state, interruptions or failures, enemy type where applicable,
and whether the cadence felt like `Pass`, `Watch`, or `Tuning Gate`.

## Class, Ability, And Combat Gate Ownership

This document owns the promotion-kit side of the Class, Ability, and Combat
gates. `CLASS_RING_SYSTEM.md` owns Class Ring activation,
`PROMOTION_ABILITY_RULES.md` owns promotion ability retention, and
`COMBAT_BALANCE_DESIGN_GATES.md` owns combat semantics and balance-report gates.

The V1 promotion kit pass is implemented. Future work should start with
UI/log readability for combat meters, class status, ring state, and combat
messages, with no mechanic or numeric tuning changes in that slice.

Status locks to preserve unless a later spec explicitly changes them:

- `Transform4` is retired as a live Lycan Red Dragon reward. The legacy wrapper
  remains loadable for old saves/tests, while Lycan Red Dragon victories set
  Dragon Essence state for the transformed-only `Winged Pounce` action.
- `Frozen Armor` is implemented as a Sorcerer-line Ice mastery passive.
- `Eclipse` is covered by the Shadowcaster Umbral Debt spec.
- Diviner/Astromancer Foresight Threads and `Threaded Cast` are implemented
  while preserving the current per-save rune and spell-empowerment scope.
- Shaman/Soulcatcher Totem Resonance and `Totem Surge` are implemented while
  preserving communion, spellbook/Totem/Class Ring storage, nonlethal
  Soul Drain, and reduced Totem pulse-potency contracts.

Track expansions remain deferred and require a one-page decision block before
implementation:

- Monk/Master Monk: combo chains, chained input timing, combo UI, longer
  progression, and legs/additional melee attacks with separate attack, crit,
  and accuracy rules.
- Bard/Troubadour: broader Maestro progression, larger sheet-music economy, and
  quest-locked composition.
- Beast Master: broader monster taming, stables, companion visuals, and
  stronger-species balance rules.
- Druid/Archdruid: Grove questlines, catalyst economy expansion, and persistent
  post-attunement mastery.
- Sentinel/Stalwart Defender: party-tank threat rules and multi-target control.
- Lancer/Dragoon: broader Jump-system redesign, persistent Jump mastery, and
  extra Jump modification capacity.
- Paladin/Crusader: multi-vow respecs, morality systems, and broader oath
  quest arcs.
- Weapon Master/Berserker: forced berserk/loss-of-control and broader scar
  milestone trees.
- Cleric/Templar/Hierophant: full divine economy redesign, relic quest expansion, and
  loot-centered Pious Bounty progression.
- Priest/Archbishop: party-healer systems, morality gates, and resurrection
  economy redesign.
- Thief/Rogue: full loot-table redesign, persistent heist caches, and
  jackpot-forcing mechanics.
- Inquisitor/Seeker: full quest pathing, guaranteed boss/trial escape, and
  loot-focused journal rewards.
- Assassin/Ninja: stealth-system rewrites, persistent target marks, and
  unrestricted instant-death scaling.
- Spell Stealer/Arcane Trickster: stolen-spell mastery, free-scroll generation,
  and scroll-economy redesign.
- Thieves Guild V1: a town `Shops` menu option from the start, closed until
  level 10 like other gated shops. Once open, it is available to everyone for
  keys, Blank Scrolls, Lockpick Kits, Smoke Bombs, and future tool/contraband
  items in one tools tab. Spell scrolls, staves, tomes, rods, musical
  instruments, and the expensive fake-wall-revealing `Oculus` belong to
  Seraphine Voss's Magic Shop; Seraphine is a failed academy lecturer turned
  practical hedge-magus who sells spellwork that survives the dungeon. Promoted
  Footpad-line classes can join through a branch-themed hidden level 2
  initiation trial, then use the backroom for class guidance, Footpad-line
  Class Ring jobs, a guild-shop discount, and a one-time starter kit.
  Non-members hear from Mara Vale: "The wares are for all but the backroom is
  for a select few."

Future P6 class ability work needs a one-page decision block covering trigger,
class eligibility, storage/save migration, combat and exploration behavior,
UI/menu/status/combat-log copy, event/audio needs, balance assumptions,
regression tests, and manual playtest checks.

## Review Baseline

### Diviner/Astromancer Runes

Current shipped rune behavior:

- Rune signs: `Ember`, `Tide`, `Gale`, and `Stone`.
- Rune cap: `3` stored runes per sign.
- Rune source: natural-spell kills by `Diviner` or `Astromancer`.
- Base rune drop chance: `25%`.
- Astromancer active-sign kill bonus: `+25` percentage points when the kill
  matches the active constellation sign.
- Resistance scaling: target resistance lowers the chance multiplicatively;
  target weakness raises it multiplicatively.
- `Runic Boost`: spends one matching rune and empowers the selected spell with a
  `75%` fate floor.
- Awakened, equipped Astromancer Class Ring: raises active-sign `Runic Boost`
  from a `75%` floor to a `100%` floor.
- Progression storage: per-save `astromancer_state`; no account progression,
  rune items, permanent spell mutation, or gear rune modification.

### Shaman/Soulcatcher Nature Totems

Current shipped Totem behavior:

- Totem pulse chance: `35%` at end of player turn.
- Staff pulse bonus: `+15` percentage points.
- Totem pulse potency: `50%` of the selected spell output.
- Staff matching-cast bonus: `+20%` damage or healing when the player casts a
  matching nature spell while the matching Totem is active.
- Water Totem: `+20%` Magic Defense and `25%` hostile spell-damage absorption
  into healing.
- Communion unlocks are represented by learned spells, not separate save flags.
- Soul Drain is a Soulcatcher level-4 spell that deals nonlethal current-HP
  percentage damage.

### Ring-Hooked Legacy Effects

These effects are implemented and visible through existing runtime hooks:

- Sentinel `Resolve` with Stalwart Defender legacy `Guard Meter` compatibility.
- Grand Summoner future summon scaling.
- Soulcatcher harvest tracking and Soul Aspect scaling.
- Beast Master shared recovery.
- Class status text for the legacy class-kit hooks.

## Diviner/Astromancer Rune Scope

The current rune system remains per-save and spell-empowerment based. Future
work must not add rune gear modification, rune inventory items, account history,
meta-progression, or permanent spell alteration unless a new spec explicitly
changes this scope.

### Scope Boundaries

- Keep the four-sign model as shipped: `Ember`, `Tide`, `Gale`, and `Stone`.
- Keep rune generation tied to the currently supported natural-spell elements.
- Do not add additional spell-school aliases to the rune system in this slice.

### UI Acceptance

- Combat must continue to show the current sign and compact four-sign rune grid.
- Pygame must expose the complete readable state supplied by the shared core.
- Richer constellation presentation is future polish unless promoted by a
  dedicated UI/readability pass.

### Implementation Requirements

If future rune work changes code, cover the final behavior with focused tests around:

- Rune cap and save/load normalization.
- Rune drop chance for resistance and weakness.
- `Runic Boost` rune consumption and Astromancer sign advancement.
- Awakened equipped ring floor behavior.

## Shaman/Soulcatcher Totem Scope

The current Totem system remains class-local and per-save through spellbook,
Totem, and Class Ring state. Communions are one-time unlocks represented by
learned spells, not new quest flags or account state.

### Communion Locations

Keep these locations locked for the current scope:

- Underground Spring: Water communion, unlocks `Tsunami`.
- Boulder: Earth communion, unlocks `Earthquake`.
- Fire Path: Fire communion, unlocks `Fireball`.
- Floor-3 strange-draft passage: Wind communion, unlocks `Tornado`.

### Soul Drain And Soul Totem

- Preserve `Soul Drain` as nonlethal current-HP percentage damage.
- `Soul Drain` must leave the target at at least `1` HP.
- Soul Totem may pulse `Soul Drain` only when Soul aspect is active and the
  spell is known.
- Soul Totem pulses use the same reduced Totem pulse potency as elemental
  pulses unless a later balance pass explicitly changes all pulse potency rules.

### Implementation Requirements

If future Totem work changes code, cover the final behavior with focused tests around:

- Communion class eligibility, repeat visits, and save/load spell persistence.
- Highest-unlocked matching spell selection for Totem pulses.
- Staff pulse chance and matching-cast amplification.
- Water Totem Magic Defense and spell absorption.
- Soul Drain nonlethal behavior and Soul Totem pulsing.

## Promotion Track Specs

The specs below are the accepted V1 implementation contracts. They remain here
as durable behavior references and as the source of follow-up tuning/polish
items. When changing one of these class tracks, preserve the storage boundaries,
save migration assumptions, and test intent unless a later spec explicitly
updates them.

### Diviner/Astromancer Foresight Threads

Class Design Inspirations: FF Tactics

V1 implementation spec: preserve the shipped Diviner/Astromancer rune system and
make Astromancer the time-threading capstone. Diviner keeps the current
learned-spell and rune foundation. Astromancer adds combat-only `Foresight
Threads` and an explicit `Threaded Cast` command for prediction-driven spell
payoff.

- Preserve shipped behavior: keep the four rune signs, rune cap `3`,
  natural-spell kill drops, resistance scaling, `Runic Boost`, active
  constellation cycling, `Astral Judgment`, `Foretell`, `Twist Fate`,
  `Wormhole`, `Rewind`, and awakened `Constellation Cycle`.
- Foresight Thread storage: Astromancer only, combat-only, cap `3`, and no
  persistent save field. Clear Threads on combat end, flee, death, save/load
  restore, class change, or leaving Astromancer.
- Thread gain: successful time/divination actions, successful `Runic Boost`,
  and `Astral Judgment` grant `+1` Thread. `Rewind` restores snapshot-safe
  Thread state and may grant its Thread only once per combat after a successful
  restore to prevent farming.
- `Threaded Cast`: new Astromancer active skill. It costs modest MP, requires
  at least `1` Thread, and marks the next eligible spell or `Runic Boost`.
  The marked action spends all Threads before resolution.
- Threaded payoff: spent Threads improve hit, status, rider reliability, and
  modest spell output. Misses or fully negated results consume Threads but
  apply no rider. Threaded Cast does not replace `Twist Fate`, bypass immunity,
  or mutate spells permanently.
- Class Ring enhancement: `Star Chart` still awakens displayed
  `Constellation Cycle`. The awakened, equipped ring keeps the active-sign
  `Runic Boost` fate-floor behavior and also strengthens active-sign
  `Threaded Cast` payoff through better rider/output reliability, without
  increasing Thread cap or controlling the constellation cycle.
- UI text/surfaces: class/status text should show current constellation, rune
  grid, Foresight Threads, pending `Threaded Cast`, and active-sign ring
  readiness. Combat logs should report Thread gain, cap, spend, pending
  Threaded Cast, negated payoff, Rewind snapshot handling, and active-sign ring
  enhancement.
- Tests: cover existing rune drops, caps, save/load normalization, resistance
  scaling, `Runic Boost` consumption, Thread cap and gain sources, combat-end
  and save/load cleanup, Rewind snapshot safety, `Threaded Cast` gating and
  spend-all behavior, `Twist Fate` stacking boundaries, and active-sign ring
  enhancement.
- Balance assumptions: Diviner does not get Foresight Threads in V1. Foresight
  Threads are combat-only to keep persistent progression focused on runes.
  Threaded Cast reliability and active-sign ring payoff should start
  conservative and be tuned after playtest.

### Demonologist Corruption And Bargain Presentation

Class Design Inspirations: WoW

V1 implementation spec: keep the existing fiend contract loop, then add corruption
as a real risk/reward meter, persistent patron mood, and stronger imprisoned
familiar echo identity. Demonologist should carry Warlock forward: familiar
identity matters, contracts layer on top, and Class Ring awakening converts the
familiar into a permanent contract-shaping echo.

- Storage: extend the existing `demonologist_contracts` save state with
  `corruption` as an integer from `0` to `100` and `patron_moods` as
  `{patron_name: int_-100_to_100}`. Missing values default cleanly, invalid
  values clamp on load, unknown patron keys are ignored, and all existing
  fields remain compatible.
- Corruption loop: accepted contracts add corruption. Normal intents add `+4`,
  `Desperate Aid` adds `+8`, item riders add `+2`, permanent HP/MP riders add
  `+4`, and twisted bargains add `+2`. Corruption cools naturally by `2` after
  combat victory and by `5` after normal rest/healing services.
- Corruption tiers: `0-24` has no bonus, `25-49` grants `+5%` contract strength
  and `+3%` misbehavior risk, `50-74` grants `+10%` strength and `+7%` risk,
  and `75-100` grants `+15%` strength and `+12%` risk. Twist severity gains
  `+0/+1/+2/+3` by tier.
- Patron mood: successful non-twisted bargains give the active patron `+3`
  mood, twisted bargains give `-4`, and refused quotes give `-1`. Positive mood
  opens extra intent access; negative mood withholds high-value intents but
  must never reduce a patron below one available intent.
- Favor unlocks: at `+25` and `+60`, patrons offer extra intents from this
  fixed table: `Imp` gains `Protect` then `Desperate Aid`; `Quasit` gains
  `Restore` then `Protect`; `Incubus` gains `Protect` then `Desperate Aid`;
  `Succubus` gains `Protect` then `Harm`; `Archvile` gains `Restore` then
  `Desperate Aid`; `Maelephant` gains `Curse` then `Restore`; `Balor` gains
  `Restore`.
- Resentment withholds: at `-25` and `-60`, patrons withhold high-value intents
  in priority order: `Desperate Aid`, `Restore`, `Protect`, `Curse`, while
  preserving at least one intent.
- `Abyssal Covenant`: keep the existing spell-power and contract-bonus behavior,
  but make it controlled channeling. While active, contract strength treats
  corruption as one tier higher, misbehavior treats corruption as one tier
  lower, and accepted-contract corruption gain is reduced by `2` to a minimum
  of `1`. Update text so it reads as stabilizing dangerous power rather than
  simply increasing corruption.
- Familiar echo identity: awakened Class Ring echo effects remain tied to the
  imprisoned familiar and modify the corruption loop. `Homunculus/Defense`
  makes `Protect` last `+1` turn and halves corruption risk bonus for `Protect`
  and `Restore`; `Fairy/Support` makes `Restore` heal `+10%` and improves
  natural corruption cooling by `+1`; `Mephit/Arcane` makes `Harm` and `Curse`
  treat corruption strength as one tier higher but add `+1` extra corruption;
  `Jinkin/Luck` gets one combat-only `35%` chance per fight to turn a twisted
  bargain into a lucky twist with normal success and `+10%` strength, while a
  failed luck twist adds `+1` severity.
- UI text/surfaces: contract quote UI should show patron mood, corruption tier,
  adjusted misbehavior risk, cost riders, and whether any intent is unlocked or
  withheld by mood. Church Crypt review text should show corruption, active
  patron mood, available patrons, active echo, recent contract history, and
  Class Ring awakening state. Class Ring text should mention empowered
  contracts plus the imprisoned familiar echo's current corruption-shaping
  effect.
- Tests: cover state normalization, save/load, corruption clamping, patron mood
  clamping, legacy saves without new fields, corruption gain/cooling, tiered
  strength/risk scaling, twist severity amplification, patron favor/resentment
  intent changes, `Abyssal Covenant` channeling, and representative familiar
  echo modifiers including Jinkin's combat reset.
- Balance assumptions: this is a V1 implementation slice, not a full contract
  economy rewrite. Existing patron roster, kill-history unlocks, crypt binding,
  and familiar imprisonment remain intact. Corruption tier bonuses and patron
  mood thresholds should be tuned after playtest.

### Shadowcaster Umbral Debt And Eclipse

Class Design Inspirations: WoW

V1 implementation spec: carry Warlock forward through shadow spells and familiar
identity, then make `Umbral Debt` the baseline Shadowcaster mechanic. Shadow
damage builds a spendable reserve, `Eclipse` spends that reserve for a short
shadow form, and the awakened Class Ring improves debt capacity, auto-healing,
and Eclipse stability.

- Storage: use existing `class_ring_awakening["data"]["Shadowcaster"]` state
  even before ring awakening. Track `debt`, `backlash`, `eclipse_turns`, and
  `familiar_echo_used`. Missing or legacy state normalizes cleanly; `debt` and
  `backlash` clamp to nonnegative integers; combat-only fields clear on combat
  end and save/load.
- Debt generation: Shadow/Dark damage dealt by a Shadowcaster stores `20%` of
  final damage as `Umbral Debt`. Baseline cap is `30%` of max HP. An awakened,
  equipped Shadowcaster Class Ring raises the cap to `45%` of max HP. Overcap
  becomes `backlash` instead of being lost.
- Active debt use: add active skill `Eclipse`. It requires at least `20` debt,
  spends `20` debt, lasts `3` turns, and does not persist after combat.
  Recasting while active refreshes duration and spends the debt again.
- Eclipse effect: while active, shadow damage gains `+15%`, Speed gains `+10%`,
  and Holy resistance drops by `0.25`. The Holy weakness is direct but should
  not apply any additional self-damage by itself.
- Ring enhancement: existing `Umbral Debt` ring identity remains. When awakened
  and equipped, low-HP auto-heal remains active below `35%` HP, spending debt
  to heal as currently implemented. The ring also reduces Eclipse backlash
  conversion by `25%`.
- Backlash: overcap stores `backlash`. When Eclipse ends or low-HP auto-heal
  triggers, convert up to `10%` max HP of backlash into nonlethal self Shadow
  damage and remove that amount from backlash. If combat ends with backlash
  remaining, convert up to `5%` max HP into nonlethal self Shadow damage and
  leave the rest stored.
- `Veil of Shadows`: keep the existing Shadowcaster passive power-up,
  invisibility, and surprise-opener behavior. If surprise activates Veil while
  Eclipse is active, the first Shadow/Dark hit gains an extra `+10%` damage and
  then consumes that one-opener bonus.
- Familiar carry-forward: familiar behavior remains otherwise unchanged.
  `Homunculus` reduces the Eclipse Holy penalty to `0.20`; `Fairy` makes
  low-HP auto-heal and Eclipse-end backlash conversion heal an extra `5%` of
  debt spent, capped conservatively; `Mephit` raises Shadow/Dark debt
  generation to `25%`; `Jinkin` gets one combat-only `30%` chance per fight for
  backlash conversion to ignore half of the converted backlash.
- UI text/surfaces: class status should show Umbral Debt, cap, backlash, and
  Eclipse turns when relevant. Ring text should describe `Umbral Debt` as
  awakened debt capacity, low-HP auto-heal, and Eclipse stabilization. Combat
  logs should report debt gain, Eclipse activation/expiration, auto-heal
  spending, and backlash conversion.
- Tests: cover debt normalization, legacy state compatibility, cap calculation,
  debt generation from Shadow/Dark damage only, overcap-to-backlash behavior,
  `Eclipse` gating/spend/refresh/duration/reset, shadow damage and Speed boosts,
  Holy resistance penalty, awakened ring cap and auto-heal, reduced backlash
  conversion, Veil surprise opener compatibility, and representative familiar
  hooks.
- Balance assumptions: this is a V1 class-kit spec, not the full stolen-light or
  late-game shadow narrative pass. Shadowcaster keeps Warlock shadow spells and
  familiar identity. Numeric tuning is conservative and should be revisited
  after playtest.

### Spellblade/Knight Enchanter

Class Design Inspirations: Tales of Destiny

V1 implementation spec: make Spellblade a spell-to-blade hybrid whose first
promotion loop carries forward into Knight Enchanter's awakened `Arcane Tempo`
identity.

- Trigger: casting a compatible damage spell creates one combat-only blade
  charge using that spell's school. The next eligible standard weapon attack or
  weapon-tagged skill consumes the charge.
- Element source: the charge uses the last compatible spell school. Casting
  another compatible damage spell overwrites the pending charge.
- Spell scope: elemental and arcane damage spells create charges. Support,
  healing, movement, and status-only spells do not.
- Charge payoff: a charged hit adds a conservative school-matched magic
  follow-up with clear combat-log/status text. Misses do not apply follow-up
  damage. Charges do not persist after combat.
- Promotion carry-forward: Spellblade gets the basic spell-to-blade charge
  loop. Knight Enchanter keeps it and adds `Arcane Tempo`.
- Class Ring redesign: the awakened Knight Enchanter ring should display
  `Arcane Tempo` while preserving old `Mana Tap+` compatibility internally for
  existing saves/tests.
- `Arcane Tempo`: while the awakened ring is equipped, consuming a blade charge
  grants 1 combat-only Tempo stack, max 3. At 3 stacks, the next charged weapon
  hit spends all stacks for an extra arcane burst.
- Mana Tap remains usable as sustain, but the Class Ring identity should read
  as `Arcane Tempo` rather than a basic conversion upgrade.
- Storage: v1 uses temporary combat state only. Do not add persistent save state
  for blade charges or Tempo.
- UI text/surfaces: combat log, class/ring status text, and current Arcane Duel
  awakening text. Equipment previews do not need new enchantment previews in
  v1.
- Tests: Spellblade charge creation/overwrite/consumption, non-damage spell
  exclusion, hit/miss behavior, combat-end reset, Knight Enchanter Tempo stack
  and burst behavior, awakened display rename, and legacy `Mana Tap+`
  compatibility.
- Balance assumptions: start conservative; the loop should reward alternating
  spell and weapon actions without making pure weapon turns or pure spell turns
  obsolete.

#### Improvements

- Ultimate weapon can be made sentient, allowing interaction and weapon can level

### Summoner/Grand Summoner

Class design inspiration: FFX

V1 implementation spec: add per-summon bond progression that lets Summoners borrow
limited invocations from trusted summons, while Grand Summoner keeps the
existing `Conduit Ritual` sacrifice and `+30% Summons` ring scaling.

- Preserve existing scope: keep the current single-active-summon combat model,
  summon leveling, recall behavior, Silence/anti-magic suppression, roster
  acquisition, `Heal Summon`, `Raise Summon`, and Grand Summoner ring scaling.
- Storage: add persistent per-save `summon_bonds`, keyed by known summon name
  and capped at 100. Normalize missing or invalid state to 0 and ignore unknown
  summon keys.
- Bond gain: an active, living summon is eligible for victory bond only at
  summon level `2+`. Use the enemy XP divided by the summon level's full XP span
  (`level.pro_level * summon.exp_scale * level.level`) as the roll chance. On a
  successful roll, grant scaled `+1` to `+5` bond from that same ratio. Bond
  gains clamp at 100. Boss victories guarantee the eligible bond roll succeeds
  and double the resulting gain. Do not grant separate per-action bond in this
  pass.
- Summon costs: calling a summon spends Summoner MP based on the summon tier;
  Kobalos also requires gold.
- Bond milestones: 25 grants `Attuned Bond`, adding +5% HP and damage when that
  summon initializes; 50 unlocks the owner-cast `Invoke <Summon>` borrowed
  invocation; 75 grants `Deep Bond`, raising the initialization bonus to +10%;
  100 grants `True Name`, enabling the Grand Summoner ring conduit rider.
- Borrowed invocations: owner-cast MP-cost class skills, not permanent copies of
  summon spellbooks. They require bond 50 with the named summon and do not
  require that summon to be active.
- Invocation list:
  - `Invoke Patagon`: Physical/Earth hit with small Attack down.
  - `Invoke Dilong`: Earth hit with small Defense down.
  - `Invoke Agloolik`: Ice hit with brief self Defense up.
  - `Invoke Cacus`: Fire hit with light Burn pressure.
  - `Invoke Fuath`: Water hit with small Weaken Mind chance.
  - `Invoke Izulu`: Electric hit with small HP siphon.
  - `Invoke Hala`: Wind hit with brief Speed or dodge support.
  - `Invoke Grigori`: Holy hit plus small self heal.
  - `Invoke Bardi`: Shadow hit with small Blind chance.
  - `Invoke Kobalos`: Physical/Poison hit with brief dodge support.
  - `Invoke Zahhak`: non-elemental arcane hit with small Magic Defense up.
- `Conduit Command`: Grand Summoner active skill that requires an active, living
  summon. It costs MP and empowers that summon's next non-Recall action by +25%
  damage or healing.
- `True Name` rider: at bond 100, while the awakened Grand Summoner Class Ring
  is equipped, `Conduit Command` also adds the active summon's lesser signature
  rider to the empowered action.
- Expiration: conduit empowerment expires after the summon takes its next
  non-Recall action, is recalled, dies, or combat ends.
- Active-summon support: while a summon is active, the summon remains the
  single player-side actor, but the visible `Support` action lets the Summoner
  spend that turn on limited intervention: restorative/support items, `Recall`,
  `Heal Summon`, `Raise Summon`, `Conduit Command`, or unlocked
  `Invoke <Summon>` skills. Do not expose Summoner `Defend`, full attacks,
  ordinary offensive spells, ordinary offensive skills, flee, or starting
  another summon through this support lane.
- Dilong/Tunnel: Dilong starts with explicit nonzero Magic and Magic Defense and
  learns `Surface`. Tunneling hides normal summon offense until `Surface` or
  `Recall` is chosen.
- UI text/surfaces: class/ring status text should show known summon bond values
  and Grand Summoner conduit readiness. Combat Focus omits the persistent
  `Summon Bond` row and, while a summon is active, shows active summon level,
  XP, HP, MP, and status icons. Combat logs should clearly report bond gain,
  borrowed invocation use, conduit empowerment, and True Name riders, with
  active summon action lines colored separately from player and enemy lines.
- Save migration: old saves default to empty/zero bond state. Existing Grand
  Summoner awakening state and `hp_sacrificed` data remain compatible.
- Tests: cover bond normalization/save-load, level-gated XP-ratio victory bond
  gain, failed/successful bond rolls, 100 cap, 25/75 initialization bonuses
  stacking with `+30% Summons`, invocation unlock gates and representative
  riders, `Conduit Command` requirements, support action turn flow, Dilong
  `Tunnel`/`Surface`, empowerment expiration, and bond-100 ring-only True Name
  rider behavior.
- Balance assumptions: start conservative; this is a v1 progression layer, not
  a full summon economy redesign or dual-summon combat rewrite.

Additional Improvements:

- Dying reduces the bond level by 50% for Summoner, reduce to 25% for Grand
  Summoner; once bond reaches 100, dying no longer reduces bond

Open follow-up gates:

- Consumable targeting policy: decide whether ordinary consumables beyond the
  current restorative/support lane can target summon creatures directly. The
  decision must define eligible item subtypes, combat-only versus menu use,
  Support-menu placement, failure text, save implications if any, and tests for
  active, dead, recalled, and missing summons.
- Dilong damage evidence: after the explicit starting Attack bump and the
  Earth/flying correction, use focused combat evidence before changing Dilong's
  physical damage numbers. Ground-contact Earth spells remain blocked by
  flying, but Earth Maw and non-grounded Earth damage should connect against
  flying targets that lack Earth resistance.

### Weapon Master/Berserker Bloodied Momentum

Class Design Inspirations: D&D

V1 implementation spec: preserve Weapon Master's implemented Weapon Discipline and
Weapon Arts, then give Berserker a distinct controlled-risk combat loop:
`Bloodied Momentum`. Berserker carries discipline forward, mutates heavy weapon
arts while injured, and uses Battle Scars and awakened `Bloodied Crits` to
stabilize the dangerous low-HP playstyle.

- Preserve shipped behavior: Weapon Discipline state, all eight Weapon Arts,
  rank 1/5/10 scaling, Berserker heavy dual-wield restrictions, `Monkey Grip`,
  `Monkey Grip 2`, `Final Assault`, `Battle Scars`, `No Healing Duel`, and
  awakened `Bloodied Crits`.
- Bloodied Momentum storage: Berserker only, combat-only, and no persistent
  save field. Base cap is `3`, raised to `4` at 10 Battle Scars and `5` at 20
  Battle Scars. Clear on combat end, flee, death, save/load restore, class
  change, or leaving Berserker.
- Momentum gain: successful weapon hits while below 50% HP grant `+1`
  Momentum once per player action. Taking meaningful damage while below 50% HP
  grants `+1` Momentum once per enemy action. Below 25% HP, the first eligible
  gain each round grants `+1` extra, capped.
- Automatic heavy payoff: the next Berserker heavy weapon art or Berserker
  weapon skill consumes all Momentum before resolving. Eligible heavy arts are
  `Guard Cleaver`, `Reaver's Mark`, `Brace`, and `Anvil Strike`.
- Heavy art mutation: each stack adds conservative accuracy/damage pressure and
  a small art-themed rider: stronger guard break, stronger mark pressure,
  stronger brace reduction/counter, or stronger defense crush. Misses consume
  Momentum but do not apply art riders.
- Battle Scars role: keep current scar HP bonus and below-25% weapon damage
  contribution. Scars improve Momentum cap and stability, not broad passive
  damage inflation. At 10+ scars, preserve `1` Momentum after a clean heavy-art
  payoff once per combat. At 20 scars, reduce the HP threshold for Battle Scar
  victory qualification from 10% to 15%.
- `Final Assault` integration: it remains once per combat. If Momentum exists
  when `Final Assault` triggers, consume all Momentum to improve counter
  reliability and survival pressure. If the counter kills, stabilize at 1 HP as
  current behavior does; if it fails, do not add extra rescue layers.
- Class Ring enhancement: awakened/equipped `Bloodied Crits` keeps current
  crit/damage thresholds. It also improves Momentum gain/spend reliability:
  below 50% HP, one missed heavy payoff per combat preserves `1` Momentum;
  below 25% HP, heavy payoff riders gain a modest reliability boost. The ring
  does not add loss of control, forced attacks, or self-damage.
- UI text/surfaces: class/status text should show `Bloodied Momentum`
  stacks/cap, bloodied threshold state, Battle Scar cap bonus, and ring
  preservation readiness. Combat logs should report Momentum gain, cap, spend,
  miss preservation, heavy-art mutation, Battle Scar stability, and
  `Final Assault` Momentum use.
- Tests: cover Weapon Master discipline/art progress carrying into Berserker,
  Momentum caps at 0/10/20 scars, gain from weapon hits and meaningful incoming
  damage, below-25% bonus gain, cleanup, heavy-art Momentum spend and miss
  consumption, Battle Scar stability and 20-scar victory threshold adjustment,
  `Final Assault` Momentum use, and awakened/equipped `Bloodied Crits`
  retaining current crit/damage bonuses while adding only the specified
  Momentum reliability effects.
- Balance assumptions: Berserker should be controlled risk, not forced
  berserk/loss-of-control. Heavy weapon identity is the Berserker mutation
  surface; Grandmaster remains the all-weapon perfection branch. Numeric values
  are conservative starting points for playtest tuning.

### Paladin/Crusader Oath Conviction

V1 implementation spec: refine the Paladin/Crusader path around vow rhythm. Paladin
keeps the permanent four-vow choice and existing aura/mark tension; Crusader
carries that vow forward with a higher combat-only `Oath Conviction` cap and
awakened `Vow Affirmation` smoothing the loop without erasing mark drawbacks.

- Preserve shipped behavior: permanent vow choice, legacy no-vow Church choice,
  `Redeem`, `Challenge`, `Interpose`, `Judgment Riposte`, aura/mark state,
  mercy immunity for bosses and Class Ring trials, Church `Vow Trial`, and
  current `Vow Affirmation` aura/mark tuning.
- Oath Conviction storage: add no persistent save field. Store Conviction as
  transient combat state, not persistent `paladin_vow` data. Clear on combat
  end, flee, death, save/load restore, class change, or invalid/missing vow.
  Base caps are Paladin `2` and Crusader `3`; required Tempered Conviction
  raises their effective inherited caps to `3` and `4`.
- Conviction flow: a valid `Redeem`, `Challenge`, `Interpose`, or `Judgment Riposte`
  use grants one stack. Its clean defining outcome grants one
  additional stack. Signature actions generate and never automatically spend.
- `Blessed Light`: this level-55 Paladin passive turns a successful
  healing-spell cast during combat into `+10 Attack` for three turns. Repeated
  healing refreshes the duration instead of stacking; out-of-combat and
  zero-healing casts do not trigger it.
- Clean outcomes: successful `Redeem`, defeating a challenged or bounty foe for
  `Challenge`, successful guarded block for `Interpose`, and triggered
  `Judgment Riposte`.
- `Oath's Judgment`: requires one stack, costs no MP, works under Silence, and
  spends all stacks after weapon, target, vow, and shield validation. A miss
  still spends. Redemption is a `0.9x` Holy strike with `+3` accuracy and `5%`
  maximum-HP healing per stack. Conquest is `1.0x + 0.15x` damage and `+5`
  accuracy per stack. Protection requires a shield, strikes at `0.75x`, lowers
  Attack by two per stack, and grants ten barrier per stack. Retribution is a
  `1.0x` Holy strike with `+3` accuracy per stack and prepares a `0.25x`
  per-stack Holy counter.
- `Oath's Shelter`: also spends all stacks after validation and works under
  Silence. Redemption heals `10%` maximum HP per stack and cleanses Poison at
  two. Conquest grants three Attack and Speed per stack. Protection grants 15
  barrier and five percentage points of block and mitigation per stack.
  Retribution reduces the next damaging hit by `8%` per stack and returns the
  prevented amount as Holy damage.
- Crusader talents: Righteous Advance adds `0.10x` direct Judgment damage and
  improves every vow rider by `25%`. Consecrated Bulwark adds one turn to
  Shelter effects and improves healing, barriers, mitigation, reflection, and
  rating values by `25%`.
- `Vow Affirmation`: keep current aura benefits at `1.5x` and mark
  penalties/durations at `0.5x`. While awakened/equipped, after a clean
  primary Judgment or Shelter effect, preserve `1` Conviction once per combat.
  Marks stay separate: Conviction never cleanses, shortens, or disables mark
  drawbacks.
- UI text/surfaces: class/status text should show sworn vow, active aura/mark,
  and `Oath Conviction` stacks/cap without surfacing class-ring details in the
  Character Menu class tab. Combat logs should report Conviction gain, spend,
  cap, clean outcome bonus, vow-specific rider, and mark/aura changes.
- Tests: cover vow normalization, legacy no-vow saves, permanent vow locking,
  signature skill grants, Conviction cap/gain/extra gain/spend order/cleanup,
  all four vow spend riders, immunity boundaries, marks staying separate, and
  awakened/equipped `Vow Affirmation` preserving `1` Conviction once per combat
  after a clean empowered payoff.
- Balance assumptions: V1 supports all four vow paths equally. This is not a
  morality system, oath-respec system, or broader quest arc. Numeric values are
  conservative starting points for playtest tuning.

#### Future Design Gate: Devotion Drift And Oathless Recovery

This is not V1 implementation scope. It defines the design space for a later,
more intentional path to changing the vow selected at promotion without turning
the vow into a casual menu toggle.

- Devotion drift: each vow can track an internal devotion band. Aura-aligned
  outcomes move the character toward that vow's ideal; mark-triggering or
  oath-straining outcomes move away from it. The band may influence the strength
  or flavor of the signature skill, aura, and mark, but the exact scale and
  breakpoints require separate tuning.
- Oathless state: extreme negative devotion should break the current vow into an
  oathless state instead of immediately selecting a replacement vow. Oathless
  applies a persistent vow-specific drawback until recovery is completed.
- Ritual recovery: each vow needs a named ritual that can restore, change, or
  reframe the oath. Ritual outcomes should be rated in broad tiers so the
  starting Conviction/Devotion band reflects how cleanly the oath was renewed.
- Required design decisions before implementation: devotion scale, oathless
  boundaries, ritual list, save/load shape, Church UI copy, combat status copy,
  and regression coverage for vow loss, restoration, and migration.

### Lancer/Dragoon Aerial Tempo And Aerial Supremacy

Class Design Inspirations: FFIV

V1 implementation spec: center Lancer and Dragoon on combat-only `Aerial Tempo`.
Clean Jump landings build short momentum, and the next eligible polearm or
weapon action automatically converts that momentum into follow-through pressure.
Dragoon keeps the existing Jump modification framework and Kaelenon route, but
its awakened Class Ring identity changes from `+1 Jump Mod` to
`Aerial Supremacy`, combining offensive post-Jump firepower with defensive
landing protection.

- Preserve current behavior: keep `Jump`, Jump modifications,
  polearm-and-shield legality, `Polearm Proficiency`, `Polearm Excellence`,
  `Zephyrstrike`, `Recover`, `Dragon's Fury`, `Skyfall`, Kaelenon restoration,
  `Draconite`, and `Draconite Pendant`.
- Aerial Tempo storage: no persistent save state in V1. Base caps are Lancer
  `2` and Dragoon `3`; purchased and retained Aerial Footwork raises the
  effective caps to `3` and `4`. Gain `+1` when Jump resolves without being
  interrupted, hit or miss. Dragon's Ascent raises a clean Soaring Strike
  landing to `+2`. Jump never consumes stored Tempo, permitting consecutive
  landings.
  Clear on combat end, flee, death, save/load restore, class change, or after
  the next eligible follow-through action consumes it.
- Automatic follow-through: the next standard attack or weapon-tagged skill
  using a class-legal Sword or Polearm consumes all Aerial Tempo at action
  start. Jump and Dragon Dive are excluded. Each stack grants `+6%` total
  successful weapon damage and `+3` accuracy points. Compute the bonus once
  from all successful weapon damage in the action; misses still consume.
  Successful Dragoon payoffs reduce Speed by one per stack for two turns.
- Jump modification scope: do not add persistent Jump mastery state or extra
  active Jump modification capacity in V1. Existing modification unlocks,
  conflicts, save/load, and execution rules remain intact.
- Class Ring redesign: display the awakened Dragoon ring effect as
  `Aerial Supremacy`. Preserve old `+1 Jump Mod` compatibility internally for
  legacy saves/tests, but the redesign should no longer grant extra active Jump
  modification capacity.
- `Aerial Supremacy`: while the awakened ring is equipped, each spent stack
  grants `+8%` total weapon damage and `+4` accuracy points. A clean damaging
  Jump creates a two-turn Landing Shield equal to 15% of actual Jump damage,
  minimum one, refreshing to the larger value rather than stacking. The shield
  absorbs real incoming damage. This replaces separate `+1 Jump Mod` and
  `Meteor Guard` presentation.
- UI text/surfaces: class/status text should show Aerial Tempo stacks, cap,
  and pending follow-through in combat/status surfaces. The pygame Character
  Menu manages Jump Mods inline from the `Aerial Tempo` tab rather than the
  general action row or a separate popup, and class-tab copy should avoid
  class-ring details. Combat logs should report Tempo gain, interruption
  cleanup, Tempo spend, follow-through damage/control, landing shield, and
  legacy ring migration/display.
- Tests: cover Aerial Tempo cap, clean-landing gain, no gain on interrupted
  Jump, follow-through consumption, miss behavior, combat-end/save-load
  cleanup, effective Lancer cap `3`, effective Dragoon cap `4`, eligible
  follow-through action
  boundaries, Jump modification compatibility, `Aerial Supremacy` replacing
  extra mod capacity, legacy `+1 Jump Mod` compatibility, and unchanged
  Kaelenon/Recover/Dragon's Fury/Draconite behavior.
- Balance assumptions: this is a V1 extension, not a Jump-system redesign.
  Dragoon ring power shifts from flexibility to offensive/defensive post-Jump
  payoff. Numeric tuning starts conservative and should be adjusted after
  playtest.

### Sentinel/Stalwart Defender Resolve And Surges

Class Design Inspirations: FFVII, WoW, D&D

Implementation target: center Sentinel on baseline `Resolve`, shield
stances, and controlled counterattacks. Sentinel should feel complete at first
promotion: it builds Resolve through defensive pressure and spends it on
shield-only tactical abilities. Stalwart Defender inherits the Sentinel Resolve
kit, raises the cap to support full-bar payoffs, and adds `Resolve Surges`
as the second-promotion identity.

- Preserve current identity: keep the shield/offhand requirement, heavy armor
  identity, `Shield Block`, `Goad`, `Retaliate`, `Last Stand`,
  `Shield Mastery`, and awakened Stalwart `Guard Meter` compatibility.
- Resolve storage: use the existing Stalwart `guard_meter` save shape as the
  compatibility key where practical, but present the resource as `Resolve`.
  Sentinel caps at `50`. Stalwart Defender raises the inherited cap to `100`
  so it can either keep using Sentinel shield spends or hold the full bar for
  Surges. Normalize invalid or missing values on load and clamp to the current
  class cap.
- Resolve gain: `Defend`, successful blocks, mitigated physical hits, and
  shield-tactic actions build Resolve. The locked values are Defend `10`;
  successful block `clamp(damage blocked // 5, 5, 15)`; physical damage taken
  after mitigation `max(1, damage // 5)`; and successful Goad or Hold the Line
  `5`. There is one gain path per event.
- Sentinel shield loop: add `Hold the Line`, a shield-required stance that
  improves block/mitigation and pressures the current enemy to engage.
  `Retaliate` remains the counter identity: successful blocks can trigger a
  modest weapon counter, with stronger reliability while `Hold the Line` is
  active.
- Sentinel Resolve spends: move `Bulwark` and `Shield Riposte` into the
  Sentinel kit. `Bulwark` spends Resolve for a short barrier or next-hit
  mitigation pulse. `Shield Riposte` spends Resolve after blocking or while
  guarded for a controlled counter with light Attack or Speed pressure.
- Additional Sentinel Resolve-only abilities:
  - `Shield Check`: spend a small amount of Resolve to batter the enemy with
    your shield, lowering their Attack and Speed without overlapping the direct
    damage/stun role of `Shield Slam`.
  - `Brace Wall`: spend Resolve to refresh `Hold the Line` and raise Defense
    for the next exchange.
  - `Covering Guard`: spend Resolve to prepare a short shield ward against the
    next dangerous hit.
  - `Deflect Spell`: spend Resolve with a shield equipped to raise Magic Defense
    and brace against hostile spell pressure without becoming a full anti-mage
    class.
  - `Spell Reflection`: spend `25` Resolve with a shield to prepare for two
    enemy spell opportunities. The first hostile, targeted, reflect-compatible
    spell returns to its caster. Generic Reflect takes priority; beneficial,
    area, and unreflectable spells do not consume the preparation.
- Stalwart Defender mechanic: add `Resolve Surges` as full-bar ultimate-style
  shield payoffs. Stalwart keeps all Sentinel spends, but can also save the
  larger Resolve bar for a Surge.
- Initial Surge set:
  - `Citadel Aegis`: mastery 0. Fortified Citadel raises its barrier from 100
    to 125 and stance duration from three turns to four.
  - `Ironwall Reprisal`: mastery 4. Crushing Reprisal raises damage from
    `1.35x` to `1.60x` and lowers Attack and Speed by three for two turns.
  - `Last Bastion`: mastery 8. Final Redoubt raises healing from `30%` to `40%`
    maximum HP, barrier from 50 to 75, and stance from two turns to three.
- Counter and wall talents: Watchful Reprisal grants `+20 Attack` and ten
  percentage points of Retaliate chance. Resolute Guard grants `+20 Defense`
  and adds five percentage points to Hold the Line block and mitigation.
  Punishing Guard grants `+30 Attack` and raises Shield Riposte from `0.75x` to
  `1.0x`. Unbroken Wall grants `+30 Defense`; during Last Stand it adds ten
  block points and raises Resolve gains by `50%`. Mirror Bastion makes a
  triggered Spell Reflection grant 20 Resolve and `+6 Magic Defense` for two
  turns.
- Surge unlock source: Resolve mastery progress from real combat behavior such
  as spending Resolve, blocking, mitigating hits, using `Hold the Line`, and
  other shield-tactic actions. Locked Surges are visible as grayed/question-mark
  boxes until mastery reveals them on the class tab. In combat, Surges should
  stay out of the `Resolve` action menu until the Stalwart is at full Resolve.
- `Last Stand` synergy: keep the attack tradeoff, but improve low-HP block
  reliability, Resolve gain, and Surge readiness so the skill reinforces
  the wall-and-counter loop instead of acting as a disconnected passive.
- Class Ring enhancement: awakened/equipped `Shield Mastery` keeps the current
  automatic major-hit reduction through legacy `Guard Meter` compatibility.
  The class tab should describe Stalwart identity through Resolve and Surges,
  not through ring terminology. The ring can modestly improve block chance,
  spell-block eligibility, and counter reliability without replacing active
  Sentinel Resolve spends or Stalwart Resolve Surges.
- UI text/surfaces: class status should show Resolve and cap; the pygame
  Character Menu class tab should center a large red Resolve progress bar with
  `current/cap` inside it, then list Sentinel Resolve-spending abilities as
  ability boxes. Stalwart Defender should add a `Resolve Surges` section with
  locked/unlocked boxes and full-bar requirement text. Combat should expose
  Resolve actions through a separate `Resolve` menu rather than the general
  `Skills` menu, and that menu should show Resolve costs instead of MP costs.
  Resolve actions are shield-pressure techniques, so Silence should not block
  their use.
  Combat Focus should render Resolve as a red charge bar with the `current/cap`
  value centered inside it rather than plain text. Combat logs should report Resolve
  gain/spend, capped Resolve, Surge use, blocks, barriers, ripostes, and
  automatic ring mitigation.
- Tests: cover Sentinel Resolve cap, gain sources, clamping, save/load
  normalization, legacy Stalwart `guard_meter` compatibility, `Hold the Line`
  shield requirements and expiration, `Retaliate` counter behavior, all
  Sentinel Resolve spend costs/gates/effects/failure text, Stalwart
  inherited-spend behavior, Surge lock/unlock/use/UI, `Last Stand` low-HP
  defensive benefits and attack tradeoff, and awakened/equipped ring auto-spend
  compatibility.
- Balance assumptions: this is a V1 shield-depth spec, not a party-tank or
  multi-target threat rewrite. Sentinel/Stalwart should feel like
  `Wall + Counter`: Sentinel survives pressure and spends Resolve on shield
  actions; Stalwart Defender layers full-bar Surges and stronger reactions
  onto that foundation. Numeric tuning starts conservative and should be
  adjusted after playtest.

### Thief/Rogue Fortune And Misfortune

V1 implementation spec: replace the earlier simple luck-pip idea with paired
combat-only `Fortune` and `Misfortune` meters. Thief gains stronger loot
identity through `Scavenger's Eye`; Rogue carries that forward with
`Finders Keepers`, `Cheat Death`, and a smoother risk/reward loop where success
improves odds and failure fuels bigger eventual payoffs.

- Preserve current identity: Footpad stealth/toolkit carry-forward remains
  intact. `Lockpick` and `Master Lockpick` require a carried `Lockpick Kit`
  with limited durability; each successful use can break the kit, with higher
  Dexterity and `Master Lockpick` lowering the break chance. `Smoke Screen`
  requires and consumes one `Smoke Bomb`.
  `Steal`, `Mug`, `Gold Toss`,
  `Poison Strike`, `Sneak Attack`, `Slot Machine`, `Triple Strike`,
  `Stroke of Luck`, and awakened `Loaded Dice` remain valid.
- New passive skills: add `Scavenger's Eye` for Thief, modestly improving enemy
  loot drop rate and nudging eligible drops toward better rarity; add
  `Finders Keepers` for Rogue, occasionally finding extra unlisted loot after
  eligible defeated enemies; add `Cheat Death` for Rogue, a once-per-combat
  fatal-damage luck save boosted by Misfortune.
- Loot boundaries: `Scavenger's Eye` and `Finders Keepers` must not create
  quest, special, unique, ultimate, invalid class-restricted, or invalid
  summon-gated items. Extra finds should use normal eligible loot tables and
  start conservative.
- Meter storage: `Fortune` and `Misfortune` are combat-only and require no new
  persistent save field. Thief caps both meters at `2`; Rogue caps both at `3`.
  Clear both meters on combat end, flee, death, save/load restore, class
  change, or leaving the track.
- Meter gain: meaningful combat rolls can move the meters. Attacks,
  dodges/parries, crits, theft/luck skills, and major status attempts count.
  Tiny status ticks and passive housekeeping rolls do not. Successful meaningful
  rolls grant Fortune; failed meaningful rolls, missed risky actions, poor
  `Slot Machine` outcomes, or failed theft/status attempts grant Misfortune.
- Fortune payoff: the next eligible risky action can spend all Fortune before
  resolving to improve odds. Eligible actions include `Steal`, `Mug`,
  `Sneak Attack`, `Gold Toss`, `Slot Machine`, major status attempts, and
  comparable Rogue-risk actions. Each Fortune gives conservative reliability,
  such as about `+5` percentage points to success, crit, or status odds, or a
  small value boost where odds do not fit.
- Misfortune payoff: the next successful eligible risky action can spend all
  Misfortune to increase severity or scale rather than pre-roll odds. Payoffs
  may include stronger damage, more gold/value, improved status duration, or a
  higher `Slot Machine` outcome impact. Misfortune should feel like comeback
  pressure, not forced bad luck, and must not automatically harm the player.
- `Slot Machine` handling: Fortune may improve odds or reroll/soften the worst
  failure-style outcomes without forcing jackpots. Misfortune may increase the
  scale of a successful outcome without upgrading it directly into a jackpot.
  Existing digit/card outcome identities remain recognizable.
- `Cheat Death`: once per combat when Rogue takes fatal damage, make a Luck
  check boosted by current Misfortune. On success, survive at `1` HP, spend all
  Misfortune, and apply a short `Jinx`/Misfortune-style debuff. On failure,
  fatal damage resolves normally. The V1 effect should be meaningful without
  destroying equipment/items or charging gold.
- Class Ring enhancement: awakened/equipped Rogue `Loaded Dice` keeps the
  existing 15% failed-luck-check conversion. Once per combat after a clean
  Fortune or Misfortune payoff, `Loaded Dice` preserves `1` point of the spent
  meter. The ring does not guarantee jackpots, create quest loot, or bypass
  class/trial restrictions.
- UI text/surfaces: class/status text should show Fortune, Misfortune, caps,
  active `Jinx`, and `Loaded Dice` preservation readiness. Combat logs should
  report meter gain/spend, capped meters, Fortune odds smoothing, Misfortune
  severity scaling, `Scavenger's Eye` loot nudges, `Finders Keepers` finds,
  `Cheat Death` success/failure, and `Loaded Dice` preservation.
- Tests: cover `Scavenger's Eye` ordinary loot odds/rarity without invalid
  drops; `Finders Keepers` extra eligible finds and exclusions; meter caps,
  gain from meaningful successes/failures, ignored tiny/passive rolls, and
  cleanup; Fortune spends on representative risky actions; Misfortune scaling
  after successful risky actions; `Slot Machine` jackpot boundaries; `Cheat
  Death` success/failure, 1 HP survival, Misfortune spend, and `Jinx`; and
  awakened/equipped `Loaded Dice` failed-luck conversion plus once-per-combat
  meter preservation.
- Balance assumptions: this is a V1 extension, not a full loot-table redesign
  or persistent heist-cache system. Fortune improves odds; Misfortune improves
  severity/scale after success. Numeric tuning starts conservative and should
  be adjusted after playtest.

### Inquisitor/Seeker Case Journal And Wayfinding

V1 implementation spec: center Inquisitor and Seeker on persistent enemy-type
`Case Journal` progress, combat-only `Revelation`, and Seeker mobility depth.
Inquisitor trades stealth for truth-seeking counterplay; Seeker carries that
forward with stronger exploit reliability, better route control, and awakened
`Hidden Cache` smoothing.

- Preserve current identity: `Footpad -> Inquisitor` remains an identity trade
  that removes stealth skills. Keep `Reveal`, `Inspect`, `Exploit Weakness`,
  `Keen Eye`, shield/medium-armor identity, anti-magic/resistance spell access,
  Seeker `Cartography`, `Third Eye`, `Teleport`, `Sanctuary`, `Volitation`,
  `Enter Wall`, and awakened `Hidden Cache`. Existing Bestiary behavior and
  sight/detail visibility from Inquisitor, Seeker, Vision pendant, and `Reveal`
  remain intact.
- Case Journal storage: add persistent `case_journal` save state keyed by broad
  `enemy_typ`, storing integer progress from `0` to `100`. Normalize missing or
  invalid state on load and ignore unknown or blank enemy types.
- Case Journal progress: gain `+3` from `Inspect`, `+2` from successful
  `Exploit Weakness`, `+1` from observing a visible enemy special/telegraph,
  and `+4` from victory while enemy details were visible. Milestones are `25`
  `Known Tells`, `50` `Weakness Brief`, `75` `Pattern Lock`, and `100`
  `Closed Case`.
- Revelation storage: add combat-only target-side `Revelation`. Inquisitor caps
  at `2`; Seeker caps at `3`. Clear stacks on combat end, flee, death,
  save/load restore, class change, target death, or leaving the track.
- Revelation gain: gain stacks from `Inspect`, `Exploit Weakness`, visible
  telegraph reads, and successful Inquisitor anti-magic/setup actions such as
  `Silence`, `Dispel`, `Enfeeble`, or `Weaken Mind`.
- Revelation payoff: the next eligible exploit payoff consumes all stacks
  before resolving. Eligible payoffs are `Exploit Weakness`, a standard weapon
  hit, or a weapon-tagged precision skill. Each stack improves exploit
  reliability and modestly strengthens weakness/control pressure. Misses
  consume stacks but apply no rider.
- Case Journal payoff: against studied enemy types, `25+` makes the first
  `Inspect` grant +1 Revelation; `50+` gives `Exploit Weakness` a small
  accuracy/reliability bonus; `75+` gives visible telegraph reads a small
  defensive prediction bonus against that enemy's next action; `100` gives
  Seeker mobility tools a small MP discount or safer failure handling without
  bypassing boss or Class Ring trial restrictions.
- Seeker carry-forward: add `Wayfinding`, a passive route-control layer for
  `Teleport`, `Sanctuary`, `Volitation`, and `Enter Wall`. Mapping/sight context
  and Case Journal milestones can reduce movement-tool friction with clearer
  failure messages, small MP discounts, or reduced random-teleport scatter where
  the existing spell supports it. V1 does not add full-map quest pathing,
  guaranteed boss/trial escape, or a persistent route graph.
- Class Ring enhancement: `Hidden Cache` remains the awakened Seeker Class Ring
  identity and keeps one depth-weighted cache per sufficiently mapped dungeon
  level. While awakened and equipped, it also gives small insight smoothing:
  +1 Revelation once per combat after a clean `Inspect` or telegraph read, and
  slightly improves Seeker `Wayfinding` value. Preserve existing
  `claimed_caches` compatibility and cache gating.
- UI text/surfaces: status text should show current target Revelation, studied
  enemy-type progress/rank, active sight/detail state, and Hidden Cache
  availability when relevant. Combat/exploration logs should report Case
  Journal progress, milestone reach, Revelation gain/spend, immunity-safe
  exploit payoff, telegraph prediction, mobility smoothing, and Hidden Cache
  claim.
- Tests: cover the Inquisitor promotion identity trade, `case_journal`
  normalization/save-load/clamping/cleanup, progress gains and milestones,
  Revelation caps/gain/spend/cleanup for both classes, `Inspect`, telegraph
  reads, `Exploit Weakness`, anti-magic/setup action interactions, milestone
  bonuses at `25/50/75/100`, Seeker `Wayfinding`, and awakened/equipped
  `Hidden Cache` cache behavior plus insight smoothing.
- Balance assumptions: Case Journal progress is by broad enemy type, not
  individual enemy name. The main payoff is exploit reliability rather than
  loot generation. Seeker's added edge is mobility and route control, while
  `Hidden Cache` remains the visible ring identity. Numeric values start
  conservative and should be adjusted after playtest.

### Assassin/Ninja Death Mark And No-Trace Opener

V1 implementation spec: center Assassin and Ninja on combat-only `Death Mark`.
Assassin gains a visible passive setup loop from stealth, poison, and opening
pressure. Ninja carries that forward with a larger mark cap, Ninja Blade and
finisher execution payoffs, and an awakened ring identity displayed as
`No-Trace Opener` while preserving `First Strike Plus` compatibility.

- Preserve current identity: Footpad stealth carry-forward remains intact.
  Assassin keeps dagger/fist identity, `Poison Strike`, `Lockpick`,
  `Triple Strike`, and `Invisibility`. Ninja keeps Ninja Blade access, `Mug`,
  `Flurry Blades`, `Haste`, `Desoul`, `Blade of Fatalities`, and the current
  first-strike ring behavior.
- Passive skill: add `Death Mark` for Assassin. Marks are combat-only
  target-side state. Assassin caps at `1`; Ninja caps at `3`. Clear marks on
  combat end, flee, death, save/load restore, class change, target death, or
  leaving the track.
- Mark gain: valid setup actions can apply marks: `Sneak Attack`, successful
  `Poison Strike` poison application, `Invisibility` or surprise opener, and
  successful blind/silence-style setup. Poison/death immunity blocks those
  specific riders but does not make the target unmarkable if the setup action
  otherwise succeeds.
- Mark spend: the next eligible finisher automatically spends all marks before
  resolving. Eligible finishers include `Sneak Attack`, `Poison Strike`,
  `Desoul`, `Flurry Blades`, and the first Ninja Blade standard strike in
  combat.
- Assassin payoff: spending 1 mark improves hit, crit, and status reliability
  and strengthens poison, blind, bleed, or similar rider pressure.
- Ninja payoff: spending up to 3 marks adds stronger damage/crit and boss-safe
  execution pressure. Bosses and Class Ring trial enemies can be marked, but
  instant-death or execution riders downgrade to damage/control where death
  immunity, boss rules, or trial rules disallow instant death.
- Class Ring redesign: display the awakened Ninja effect as `No-Trace Opener`
  while preserving existing internal `First Strike Plus` compatibility for
  saves and tests. Awakened/equipped `No-Trace Opener` keeps the current
  initiative-based first standard attack double damage. With initiative, the
  first standard attack can apply 1 Death Mark before damage and, once per
  combat, preserve 1 spent mark after a clean marked payoff.
- UI text/surfaces: class/status text should show current Death Marks on the
  target, cap, and No-Trace preservation readiness. Combat logs should report
  mark application, capped marks, mark spend, immunity downgrade,
  boss/trial downgrade, Ninja Blade payoff, and ring mark preservation.
- Tests: cover `Death Mark` passive grant for Assassin and carry-forward to
  Ninja; Assassin cap `1` and Ninja cap `3`; mark gain from `Sneak Attack`,
  poison application from `Poison Strike`, `Invisibility`/surprise opener, and
  representative blind/silence setup; immunity boundaries; mark spend for
  representative Assassin and Ninja payoffs including `Flurry Blades`,
  `Desoul`, and first Ninja Blade standard strike; boss/trial execution
  downgrade; cleanup; and awakened/equipped `No-Trace Opener` compatibility,
  opener mark, and once-per-combat mark preservation.
- Balance assumptions: this is a V1 combat-depth spec, not a full
  stealth-system rewrite. Death Mark is combat-only and requires no persistent
  save field. Ninja remains the true execution branch, while Assassin gets
  reliable single-mark setup/payoff. Numeric tuning starts conservative and
  should be adjusted after playtest.

### Spell Stealer/Arcane Trickster Stolen Charge And Arcane Larceny

V1 implementation spec: preserve the existing Blank Scroll spell-theft economy,
`Steal Spell 2` permanent learning, `Steal As Well`, and Arcane Trickster ring
compatibility, then add a combat-only `Stolen Charge` loop. Spell Stealer turns
successful magical theft into short hybrid payoffs; Arcane Trickster deepens
that loop through the awakened `Arcane Larceny` ring identity.

- Preserve current identity: `Steal Spell` still requires and consumes a
  concrete `Blank Scroll` on successful theft, creates a usable inscribed
  stolen-spell scroll, and respects Class Ring trial immunity. `Steal Spell 2`
  remains Arcane Trickster permanent spell learning. `Steal As Well`,
  `Imbue Weapon`, `Third Eye`, and `Trickster's Gambit` remain intact.
- Charge storage: add combat-only `Stolen Charge` with no new persistent save
  field. Spell Stealer caps at `2`; Arcane Trickster caps at `3`. Clear Charge
  on combat end, flee, death, save/load restore, class change, or leaving the
  class track.
- Charge gain: successful `Steal Spell`, successful `Steal Spell 2`, and
  casting an inscribed stolen-spell scroll each grant `+1` Charge, capped. Item
  theft from `Steal As Well` does not independently grant Charge; Charge comes
  from stolen magic sources only.
- Hybrid payoff: the next successful damaging spell, standard weapon hit, or
  weapon-tagged trickster skill spends all Charge and adds bonus arcane damage
  equal to `20%` of the base damage per stored Charge, with a minimum of `5`
  per stored Charge.
  The current implementation releases only after a successful damaging result;
  missed or fully negated actions do not apply the payoff.
- Class Ring display: show the awakened Arcane Trickster effect as
  `Arcane Larceny`, while preserving existing internal `Spell Steal Buff`
  compatibility for saves and tests. Awakened/equipped `Arcane Larceny` keeps
  the current 3-turn `+20%` Magic damage and `+10%` dodge after successful spell
  theft.
- Ring enhancement: once per combat after a clean charged payoff,
  awakened/equipped `Arcane Larceny` preserves `1` Stolen Charge. It should not
  create free Blank Scrolls, bypass trial immunity, or make stolen spells
  permanent beyond the existing `Steal Spell 2` behavior.
- UI text/surfaces: combat/HUD status should show `Stolen Charge`, cap, and
  `Arcane Larceny` preservation readiness; `Spell Stealer` and
  `Arcane Trickster` do not receive a dedicated Character Menu mechanic tab.
  Inscribed stolen-spell scrolls are selected from the combat `Spells` picker
  with scroll labeling. Combat logs should report Charge gain, capped Charge,
  spend, miss consumption, charged payoff, stolen-scroll contribution, and ring
  preservation.
- Tests: cover `Steal Spell` Blank Scroll consumption, stolen-scroll creation,
  and immunity; `Steal Spell 2` permanent learning plus Charge gain; Charge
  caps, gain sources, spend-all behavior, miss consumption, and combat-end or
  save/load cleanup; representative spell, weapon, and weapon-tagged skill
  payoffs; `Steal As Well` item-theft boundaries; and awakened/equipped
  `Arcane Larceny` legacy buff plus once-per-combat Charge preservation.
- Balance assumptions: this is a V1 extension, not a full stolen-spell mastery
  or scroll-economy redesign. Blank Scroll scarcity remains part of the class
  identity. Arcane Trickster should feel hybrid and opportunistic, not like a
  second Wizard progression path. Numeric tuning starts conservative and should
  be adjusted after playtest.

### Cleric/Templar/Hierophant Devotion Ward

V1 implementation spec: make Cleric, Templar, and Hierophant the holy defender
branch through combat-only `Devotion`. Cleric starts a modest healing, holy,
shield, and `Pious Bounty` rhythm; Templar carries that forward with heavier
armor, stronger ward spends, `Holy Retribution`, and awakened `Ordered
Blessings`; Hierophant carries it toward staff-and-shield divine battle-casting
through `Staff Conduit`, `Consecrated Conduit`, and awakened `Sacred Conduit`.

- Preserve current behavior: Healer spell carry-forward; Cleric shield/holy
  utility; `Shield Slam`, `Shield Block`, `Pious Bounty`, and `True Strike`;
  Templar shield/offhand identity; `Parry`, `Piercing Strike`, `Goad`,
  `Charge`, `Double Strike`, `True Piercing Strike`, `Holy Retribution`;
  Hierophant staff/shield/light-armor identity; `Staff Conduit`,
  `Consecrated Conduit`, `Holy 2`, `Regen 2`, `Dispel`; and awakened
  `Ordered Blessings`/`Sacred Conduit`.
- Devotion storage: no persistent save field in V1. Devotion is combat-only,
  starts at 0, and clears on combat end, flee, death, save/load restore, class
  change, or leaving the Cleric/Templar/Hierophant track. Cleric caps at `3`;
  Templar and Hierophant cap at `5`.
- Held Devotion now gives defense-first value before a spend: each held stack
  reduces incoming damage by `3%` when that reduction removes at least 1 damage.
  This gives Cleric a build-or-spend decision immediately after promotion.
- Devotion gain: meaningful healing, Holy damage, successful `Turn Undead`,
  shield-tactic actions, and successful defensive blocks can grant `+1`
  Devotion after the enemy survives the action resolution.
- `Pious Bounty`: remains a reward accent, not the central economy loop.
  Righteous or undead-victory hooks can grant modest extra gold and should log
  providence clearly. A qualifying `Turn Undead` kill can mark bounty rewards,
  but the lethal action should not grant Devotion.
- `Sanctuary Ward`: Cleric/Templar/Hierophant active skill granted to Cleric at
  level `1`. It costs MP, requires at least `1` Devotion, and spends all stacks
  for a short barrier or next-hit mitigation pulse. More stacks improve
  mitigation and add a small cleanse or Regen chance. It should not appear in
  the combat Skills picker while the character has `0` Devotion.
- `Relic Aegis`: new Templar active skill. It costs MP, requires at least `2`
  Devotion and a shield/offhand defensive setup, and spends all stacks for
  stronger mitigation plus a brief holy counter or guard pulse.
- `Consecrated Conduit`: new Hierophant active skill. It costs MP, requires a
  staff and at least `1` Devotion, spends all stacks, and empowers the next
  staff strike, Smite, or Holy action with bonus holy damage, a modest self-ward,
  and small mana return.
- `Sacred Overchannel`: Hierophant Power Core active skill. It costs MP and
  opens the staff-and-shield channel for several rounds, improving staff/heal
  spell math, making staff or Holy actions build `2` Devotion once per action,
  and strengthening `Consecrated Conduit` payoffs with better mana return.
- `Holy Retribution`: keep the existing name, cost, and 5-round window. While
  active, physical attacks keep their holy-fire flavor, Devotion gain from
  holy/shield actions improves once per round, and Devotion ward spends gain a
  modest holy retaliation rider.
- Class Ring enhancement: `Relic Defense` still awakens displayed
  `Ordered Blessings`. Preserve the existing Regen, Defense, and Holy Damage
  blessing rotation through the current ring state for compatibility.
- `Ordered Blessings`: while awakened and equipped, the ring improves the next
  matching Devotion payoff and preserves `1` Devotion once per combat after a
  clean ward or holy-retaliation payoff. Do not replace the rotation with
  manual blessing choice in V1.
- `Sacred Conduit`: while awakened and equipped, the Hierophant ring slightly
  improves staff-conduit holy damage and preserves `1` Devotion once per combat
  after a clean `Consecrated Conduit` payoff.
- UI text/surfaces: Devotion should remain legible through combat logs, HUD or
  status rows, and skill text rather than requiring a dedicated Character Menu
  mechanic tab. Promotion should announce newly learned level-1 spells and
  skills. Surfaces should show stacks/cap, active ward, `Holy Retribution`
  window, next `Ordered Blessing`, and once-per-combat preservation readiness
  where relevant. Combat logs should report Devotion gain, cap, spend, ward
  strength, `Pious Bounty` providence, `Holy Retribution` riders, blessing
  rotation, and ring preservation.
- Tests: cover Healer -> Cleric, Cleric -> Templar, and Cleric -> Hierophant
  ability carry-forward, immediate `Sanctuary Ward` grant, Devotion caps/gain
  sources/once-per-action limit/cleanup, held-stack mitigation, `Pious Bounty`
  reward boundaries and Priest exclusion, `Sanctuary Ward` and `Relic Aegis`
  gating/MP/spend-all/mitigation/riders, `Holy Retribution` Devotion-window
  behavior, and awakened/equipped `Ordered Blessings` rotation plus once-per-
  combat Devotion preservation.
- Balance assumptions: this is a V1 defensive holy-depth spec, not a full
  divine economy or relic quest redesign. Cleric starts Devotion lightly;
  Templar is the deeper ward and ordered-blessing class. `Pious Bounty` should
  support identity without becoming the central loot engine. Numeric tuning
  starts conservative and should be revisited after playtest.

### Priest/Archbishop Prayer Benediction

V1 implementation spec: make Priest and Archbishop the pure divine support-caster
branch through combat-only `Prayer`. Priest deepens Healer's restorative spell
identity with visible support rhythm and `Supplication`, while Archbishop
carries that forward with a higher cap, proactive `Great Benediction`, `Great
Gospel` as a major Prayer reset/setup power-up, and awakened
`Divine Intervention` as the strongest emergency smoothing layer.

- Preserve current behavior: Healer spell carry-forward; Priest high-support
  spell progression; `Defensive Regen`, `Mana Shield`, `Regen2`, `Holy2`,
  `Shell`, `Cleanse`, `Bless`, `Dispel`, and `Berserk`; Archbishop `Doublecast`,
  `Mana Shield 2`, `Heal3`, `Holy3`, `Silence`, `Regen3`, `Resurrection`,
  `Great Gospel`, and awakened `Divine Intervention`.
- Prayer storage: no persistent save field in V1. Prayer is combat-only, starts
  at 0, and clears on combat end, flee, death, save/load restore, class change,
  or leaving the Priest/Archbishop track. Priest caps at `4`; Archbishop caps
  at `7`.
- Prayer gain: meaningful healing, cleansing a hostile status, applying or
  refreshing protective divine support, successful `Dispel`/`Silence`, Holy
  damage, `Defensive Regen` healing, and successful `Resurrection` can grant
  `+1` Prayer, limited to once per player action. Tiny regeneration ticks and
  passive housekeeping should not self-feed Prayer.
- `Supplication`: new Priest/Archbishop active skill. It costs MP, requires at
  least `1` Prayer, and spends all stacks for a targeted divine support pulse:
  modest HP restoration, short protection, and a small cleanse chance. More
  stacks improve the pulse conservatively.
- `Great Benediction`: new Archbishop active skill. It costs higher MP,
  requires at least `3` Prayer, and spends all stacks for several turns of
  improved healing, protection, status resistance, and modest MP sustain. It
  should be proactive support, not a second automatic death-prevention layer.
- `Doublecast` integration: Priest/Archbishop Prayer gain should count the
  whole player action, not each spell inside `Doublecast`, to prevent runaway
  stack generation. Prayer spend riders can improve both spells only if the
  spend happened before the `Doublecast` action begins.
- `Great Gospel`: keep the existing name, cost, 5-round window, cleanse, and
  power-up identity. On use, immediately set Prayer to at least half of the
  class cap. While active, healing and Holy spells keep their current boosted
  flavor, Prayer gain from divine support improves once per round, and
  `Supplication`/`Great Benediction` riders strengthen modestly.
- Class Ring enhancement: `Miracle Vigil` still awakens displayed
  `Divine Intervention`. Preserve the existing once-per-combat 35% chance to
  heal 25% max HP when first falling below 50% HP.
- `Divine Intervention`: while awakened and equipped, the ring also improves
  Prayer stability. After a clean `Supplication` or `Great Benediction` payoff,
  the ring preserves `1` Prayer once per combat. It does not spend Prayer,
  guarantee Intervention, or create immortality loops.
- UI text/surfaces: class status should show Prayer stacks/cap,
  `Great Gospel` window, active support or Benediction effects, and
  `Divine Intervention` readiness. Combat logs should report Prayer gain, cap,
  spend, support pulse, Benediction payoff, Doublecast boundaries,
  `Great Gospel` reset/riders, Intervention trigger/failure, and ring
  preservation.
- Tests: cover Healer -> Priest and Priest -> Archbishop ability carry-forward,
  Prayer caps/gain sources/once-per-action limit/cleanup, ignored passive ticks,
  `Supplication` and `Great Benediction` gating/MP/spend-all/payoffs,
  `Doublecast` gain boundaries, `Great Gospel` half-cap Prayer reset and active
  window behavior, `Resurrection` boundaries, and awakened/equipped
  `Divine Intervention` preserving legacy behavior plus Prayer smoothing.
- Balance assumptions: this is a V1 support-caster depth spec, not a full
  party-healer, morality, or resurrection-economy redesign. Priest is sustained
  support; Archbishop adds stronger proactive support and emergency smoothing.
  Numeric tuning starts conservative, especially around Prayer gain from
  healing loops, MP sustain, and `Great Gospel` reset value.

### Monk/Master Monk Ki, Dim Mak, And Ultimate Staff

V1 implementation spec: center Monk and Master Monk on combat-only `Ki`. Monk keeps
the existing spellcasting tradeoff and martial skill list, but gains a visible
rhythm resource from successful martial action. Master Monk carries that forward
with a higher Ki cap, redesigned passive power-up identity, `Dim Mak` as a
full-Ki finisher, and a Master Monk-specific `Unobtainium` ultimate staff that
makes staff play viable without replacing unarmed mastery.

- Preserve current identity: `Healer -> Monk` remains an identity trade that
  clears learned spells. Staff remains legal for Monk/Master Monk and can use
  normal martial skills; fist weapons remain legal and practical; true unarmed
  remains the cleanest mastery path.
- Chi-art replacements: remove later Monk/Master Monk spell exceptions from the
  long-term class identity. Replace them with skills: `Centered Guard` for
  defensive protection, `Mirror Breath` for brief reflection/counter-ward
  support, and `Purging Kata` for cleanse/dispel support.
- Power-up redesign: current power-up skill `Dim Mak` becomes the full-Ki
  finisher. Master Monk's normal power-up becomes passive `Martial Mastery`,
  focused on Ki discipline and finisher readiness.
- Ki storage: no persistent save state in V1. Ki starts at `0` each combat and
  clears on combat end, flee, death, save/load restore, or class change. Monk
  caps at `3`; Master Monk caps at `5`.
- Ki gain: successful standard attacks or martial skill hits gain `+1` Ki,
  once per player action. Successful dodge/parry/counter-style defensive
  reactions gain `+1` Ki. `Chi Heal` gains `+1` Ki if it meaningfully heals.
- Narrow V1 spend scope: only `Chi Heal`, `Leg Sweep`, `Hyakuretsukyaku`,
  `Suplex`, and `Hadouken` automatically spend `1` Ki when available. Suggested
  riders are stronger heal/cleanse support for `Chi Heal`, improved
  Prone/control pressure for `Leg Sweep` and `Suplex`, extra hit reliability
  for `Hyakuretsukyaku`, and modest range/pierce or Magic Defense pressure for
  `Hadouken`.
- `Dim Mak` finisher: Master Monk only. It requires full Ki and a moderate MP
  cost, spends all Ki, and is usable unarmed, with fist weapons, or with staff.
  Unarmed has no penalty, fist weapons apply `-10%` finisher power, and
  ordinary staff applies `-20%` finisher power and drops/disarms after use.
  `Dim Mak` should be a conservative high-impact control finisher: heavy
  physical/chi damage, strong Stun pressure, and boss-safe death pressure that
  downgrades to damage/control where instant death is disallowed.
- Ultimate staff: add Master Monk-only `Ruyi Jingu Bang`, crafted through the
  existing `Unobtainium` ultimate-weapon flow. It is a Staff ultimate weapon,
  restricted to `Master Monk`, and should be added to the staff ultimate
  selection without removing `Princess Guard` or `Dragon Staff`.
- `Ruyi Jingu Bang` behavior: lower magical flavor than `Dragon Staff`, with a
  martial Ki-conduit special effect. Suggested effect: on successful staff hit,
  modest chance to gain `+1` Ki if not capped; staff hits count as clean
  martial rhythm for Ki generation; `Dim Mak` may be performed through the
  staff without dropping/disarming it and without the ordinary staff finisher
  penalty.
- Class Ring enhancement: `Martial Master` remains the awakened Master Monk
  Class Ring identity. While awakened and equipped, it improves Ki discipline
  and `Dim Mak` instead of acting only as a flat stat multiplier. Suggested
  effects: preserve the current unarmed/no-armor bonus, raise `Dim Mak`
  reliability modestly, and refund `1` Ki after a clean full-Ki finisher once
  per combat.
- UI text/surfaces: class status should show current Ki and cap. Combat logs
  should report Ki gain, Ki spend, capped Ki, `Dim Mak` weapon penalties,
  ordinary-staff drop/disarm, the ultimate-staff exception, and `Martial Master`
  ring enhancement. Blacksmith/ultimate-weapon UI should show the Master Monk
  staff when eligible and `Unobtainium` is available.
- Tests: cover `Healer -> Monk` spell clearing, removal of normal
  `Shell`/`Reflect`/`Dispel` progression once chi-art replacements exist, Ki
  cap/gain/cleanup, key Ki riders, `Dim Mak` gating/spend/weapon penalties,
  ordinary staff drop/disarm, `Ruyi Jingu Bang` restriction/ultimate-flow
  visibility/Ki behavior/penalty exception, and awakened/equipped
  `Martial Master` preserving unarmed/no-armor benefit while improving
  Ki/`Dim Mak`.
- Balance assumptions: this is a V1 martial-depth spec, not a combo-input UI or
  extended limb/extra-attack system. `Ruyi Jingu Bang` is the only staff
  exception to `Dim Mak`'s ordinary staff penalty/disarm rule. Numeric tuning
  should start conservative and be revisited after playtest.

### Bard/Troubadour Repertoire And Crescendo

V1 implementation spec: keep the shipped song, instrument, sheet-music, and
`Encore` systems, then add a promotion-shaped music loop. Bard becomes a
light-support/music hybrid, while Troubadour turns composition and completed
performances into permanent repertoire. Combat songs build `Crescendo`, which
automatically resolves into song-specific codas when performances end
naturally.

- Preserve current behavior: baseline `Valor`, `Shelter`, and `Renewal` songs;
  advanced one-use sheet songs; exact-instrument composition requirements;
  exploration song hooks; Troubadour `1.5x` song strength; `Melody of
  Inspiration`; and awakened `Encore`.
- Promotion transition: `Healer -> Bard` becomes an identity trade. Bard keeps
  only light support spells: `Heal`, `Regen`, and `Cleanse` if known. Remove
  divine offense and higher divine identity spells such as `Holy`, `Holy2`,
  `Holy3`, `Turn Undead`, `Smite`, `Resurrection`, and higher direct-heal
  progression. `Bard -> Troubadour` keeps Bard songs, repertoire state, and
  light support spells.
- Storage: add persistent `bard_repertoire` state with `known`,
  `practice_xp`, and `clean_finishes` keyed by advanced song name. Missing or
  invalid legacy state normalizes cleanly; unknown song keys are ignored.
- Repertoire mastery: Troubadour-only. Composing an advanced song sheet with
  the matching instrument grants `+1` practice XP. Performing a combat song
  grants `+1` practice XP per resolved active song turn. Performing an
  exploration song grants `+1` practice XP per `20` carried steps, up to `4`
  per full duration. Natural completion grants `+3` practice XP and `+1` clean
  finish. A song becomes permanent at `18` practice XP and `3` clean finishes.
- Permanent repertoire performance: learned advanced songs no longer require
  sheet music, but cost MP and require an equipped musical instrument. Exact
  matching instruments remain required for composing sheets, not for performing
  mastered repertoire. Sheet items remain usable after mastery, consume
  normally, and do not cost MP.
- Suggested MP costs: `12` for defensive/combat support songs, `14` for
  `Battle Hymn`, `16` for `Chorus Time`, `10` for debuff exploration songs,
  and `12` for route/economy exploration songs.
- `Crescendo`: Bard and Troubadour gain `+1` combat-only Crescendo when a
  combat song resolves a maintained turn, capped at `3`. Crescendo clears on
  combat end, save/load, song interruption, or song replacement. Only natural
  song expiration spends Crescendo; replacement and combat end do not trigger
  codas.
- Song-specific codas: on natural expiration, spend all Crescendo to trigger a
  conservative coda related to the expiring song. `Valor` primes the next
  weapon or spell hit with a small performance damage/crit push. `Shelter`
  grants a brief shield or next-hit mitigation pulse. `Renewal` grants a small
  HP/MP pulse and minor cleanse chance. `Battle Hymn` lets the player keep a
  brief Berserk-style offensive benefit without loss of control while enemies
  retain frenzy drawbacks without the offensive benefit. `Ode to the Ramparts`
  converts the defense song into a small temporary barrier. `Chorus Time`
  applies one final reduced dumbfound/tempo check.
- Exploration route codas: on clean expiration, store one reduced lingering
  route effect, such as a next-encounter debuff, short reduced encounter
  modifier, one reduced difficulty-shift roll, or a `1.25x` next eligible loot
  roll.
- Class Ring and passive identity: `Encore` remains the awakened Troubadour
  Class Ring identity. Awakened/equipped `Encore` keeps its current final
  weaker effect and preserves `1` Crescendo after a natural coda. `Melody of
  Inspiration` remains Troubadour's normal passive power-up and does not
  replace `Encore`.
- UI text/surfaces: status text should show active song, turns or steps,
  Crescendo stacks, mastered repertoire count, and current practice progress
  when relevant. Combat and exploration logs should report practice XP, clean
  finishes, repertoire mastery, Crescendo gain, codas, route codas, and Encore
  preservation.
- Tests: cover `Healer -> Bard` promotion pruning, `bard_repertoire`
  normalization/save-load/unknown song cleanup, Troubadour-only practice from
  composition/combat turns/exploration steps/completions, mastery thresholds,
  permanent performance MP/instrument requirements, one-use sheet behavior
  before and after mastery, Crescendo cap/cleanup/natural-expiration spend, no
  combat-end coda, representative codas, route codas, and awakened/equipped
  `Encore` preserving `1` Crescendo while keeping its final weaker effect.
- Balance assumptions: this is a V1 music-depth spec, not a full quest-locked
  composition economy. Advanced exploration songs can become repertoire, but
  route codas must stay conservative because they affect dungeon economy and
  encounter shaping.

### Druid/Lycan

V1 implementation spec: make persistent transformation the branch's primary
mechanic. Druid gains stable wild shape, while Lycan turns transformation into a
coexistence arc with a single werewolf beast-self that becomes more controllable
through behavior, not form mastery.

- Transform persistence: `Transform` persists until dismissed across combat,
  exploration, save/load, and town transitions. Replace the current
  temp-save-only restoration model with persistent transform state that safely
  records the normal form's stats, equipment, spellbook, resistance, and class.
- Druid stable wild shape: Panther and Direbear remain selectable Druid forms.
  Druid can dismiss voluntarily unless incapacitated. Druid has no Lycan control
  ranks, involuntary transformation, or Frenzy Lock pushback.
- Lycan form identity: on Lycan promotion, Panther and Direbear stop being
  selectable forms. Their identity folds into Werewolf as instincts and flavor,
  not separate forms or mastery tracks. Werewolf is the central Lycan form.
- Lycan control state: add persistent `lycan_control` with `rank`,
  `stress_events`, and `dragon_essence`. Valid ranks are `Feral`, `Muzzled`,
  `Restive`, `Tethered`, and `Tame`; Lycan starts at `Feral`.
- Control purpose: ranks improve agency by reducing involuntary transformation,
  dismissal blocks, and Frenzy Lock duration. Ranks should not primarily be
  damage upgrades.
- Stress triggers: low HP, kills while transformed, Full Moon, and extended
  transformed combat time can trigger beast pushback. Pushback can force
  Werewolf transformation if untransformed, block dismissal, or trigger Frenzy
  Lock if transformed. Higher control ranks reduce pushback chance and severity.
- Rank progression is behavior-only:
  - `Feral -> Muzzled`: survive repeated stress events without death or fleeing.
  - `Muzzled -> Restive`: dismiss successfully after combat stress multiple
    times.
  - `Restive -> Tethered`: avoid forced transformation through repeated stress
    checks.
  - `Tethered -> Tame`: dismiss safely after Full Moon or Frenzy-trigger stress
    multiple times.
- Class Ring enhancement: `Controlled Frenzy` remains the Lycan awakened ring
  identity but does not advance control rank. While equipped, it improves
  healing while Frenzy Locked and softens pushback by reducing Frenzy duration
  or dismissal-lock duration.
- Red Dragon enhancement: `Transform4` / Red Dragon transformation is retired
  as the Lycan payoff. Defeating the Red Dragon as Lycan unlocks
  `Dragon Essence`, which enhances Werewolf rather than replacing it and does
  not advance control rank.
- Dragon Essence action: add transformed-only `Winged Pounce`, a conservative
  stronger physical attack that briefly grants or uses flight. It is available
  only while transformed after Dragon Essence is unlocked.
- UI text/surfaces: expose persistent form state, `Dismiss Form`, moon phase,
  Frenzy Lock, control rank, and Dragon Essence state in class/ring status and
  combat logs. Class Ring text should present `Controlled Frenzy` as an
  enhancement event, not a control-progression gate.
- Compatibility: preserve existing Moon Cycle phases and step cadence. Preserve
  existing Druid nature spells and Lycan combat skills unless implementation
  requires minor text updates.
- Save migration: old saves default to untransformed persistent transform state,
  current Lycan moon/frenzy state, `Feral` control rank for Lycans, and locked
  Dragon Essence.
- Tests: cover Druid Panther/Direbear persistence and dismissal, save/load
  round-trips without duplicated transform bonuses, Lycan promotion merging
  Panther/Direbear into Werewolf, stress pushback by rank, behavior-only rank
  progression, `Controlled Frenzy` enhancement without rank advancement, Red
  Dragon essence replacing Red Dragon transform, and `Winged Pounce` gating.
- Balance assumptions: this is a v1 coexistence and agency system, not a full
  nature-form questline. Class Ring and Red Dragon are separate enhancement
  events, not required control-rank progression gates.

### Druid/Archdruid Aspect Harmony

Class Design Inspirations: WoW, D&D

V1 implementation spec: center Archdruid's class-kit expansion on combat-only
`Aspect Harmony`. The existing Fourfold Balance attunement, Grove rituals,
catalysts, mastery perks, and Class Ring `Harmony Bonus` remain the persistent
progression layer. Aspect Harmony adds a short combat loop where Archdruid
actions represent `Venom`, `Stone`, `Growth`, and `Storm`, then spend that
balance through `Fourfold Surge`.

- Preserve current behavior: Druid nature spell carry-forward, Druid/Lycan
  persistent-form spec boundaries, Archdruid Fourfold Balance state, Grove
  unlock, aspect rituals, catalyst drops, mastery perks, `Tree of Life`,
  `Primal Ascendance`, and awakened Class Ring `Harmony Bonus`.
- Aspect Harmony storage: Archdruid-only, combat-only, and no persistent save
  field in V1. Clear on combat end, flee, death, save/load restore, class
  change, or leaving Archdruid.
- Aspect representation: track represented aspects from qualifying actions.
  `Venom` comes from poison application or poison nature pressure; `Stone` from
  surviving or mitigating physical pressure; `Growth` from meaningful healing
  or `Tree of Life`; and `Storm` from Electric/Wind damage or storm utility.
- Balance reward: reward distinct represented aspects more than repeated
  stacks. Two represented aspects should make `Fourfold Surge` useful; all four
  aspects should be the clean best setup.
- New active skill: add `Fourfold Surge`. It requires at least two represented
  aspects and MP, then spends all represented Aspect Harmony for a conservative
  nature payoff based on the aspects represented.
- Surge riders: `Venom` adds poison or rider pressure, `Stone` adds mitigation
  or Defense support, `Growth` adds healing or cleanse support, and `Storm`
  adds Electric/Wind damage or Speed pressure. Boss, immunity, and Class Ring
  trial boundaries remain respected; blocked riders downgrade to allowed damage
  or support where appropriate.
- `Primal Ascendance`: preserve the existing flavor and nature-aspect power-up
  identity. While active, improve Aspect Harmony gain once per round and
  modestly strengthen `Fourfold Surge` riders.
- `Tree of Life`: keep integration light. It can generate Growth Harmony
  through meaningful healing, and Growth rider support improves slightly while
  Tree of Life is active without adding a new subsystem.
- Class Ring enhancement: awakened/equipped Archdruid Class Ring keeps the
  current total-attunement `Harmony Bonus`. It also raises the combat Aspect
  Harmony cap and preserves one represented aspect once per combat after a
  clean `Fourfold Surge`. It does not spend persistent attunement or bypass
  Grove/aspect ritual requirements.
- UI text/surfaces: class status should show represented Aspect Harmony, active
  `Primal Ascendance`, `Tree of Life` Growth contribution when relevant, and
  ring preservation readiness. Combat logs should report aspect gain, capped
  aspects, Surge spend, aspect-specific riders, immunity downgrades, and ring
  preservation.
- Tests: cover Fourfold Balance state, Grove rituals, catalysts, mastery perks,
  Aspect Harmony gain from representative Venom/Stone/Growth/Storm actions,
  cleanup, `Fourfold Surge` gating/MP/spend-all/distinct-aspect scaling/riders,
  immunity/boss/trial downgrade behavior, `Primal Ascendance` rider support,
  light `Tree of Life` contribution, and awakened/equipped `Harmony Bonus`
  compatibility plus one-aspect preservation.
- Balance assumptions: this is a V1 combat-depth spec, not a new Grove
  questline or catalyst economy expansion. Persistent progression remains
  Fourfold Balance; Aspect Harmony is combat-only. Archdruid gets this depth,
  while Druid remains covered by the persistent stable wild-shape spec and
  nature spell carry-forward.

### Ranger/Beast Master

Class Design Inspirations: Pokemon, WoW

V1 implementation spec: center Ranger and Beast Master on one active tamed
companion drawn from a small held roster. Ranger keeps `Tame` and `Favored
Enemy`, gains companion bond and conservative companion growth, while Beast
Master carries the active companion bond forward with direct companion commands
and stronger awakened-ring `Shared Recovery`.

- Preserve current scope: keep one active tamed companion, compact save state,
  a six-companion held roster, existing active companion-as-`familiar` behavior,
  `Tame`, `Favored Enemy`, `Pack Bond`, and awakened `Shared Recovery`.
- Storage: extend existing `tamed_companion` save state with `bond` from `0` to
  `100`, `species`, `evolution`, `special_ability`, `active_index`, and a
  bounded `companions` list, plus combat-only `pending_command`, cleared on
  combat end and save/load. Clamp invalid values on load; legacy saves without
  roster/flavor fields default cleanly.
- Tame flavor: a successful Ranger `Tame` starts the new companion at a small
  fresh bond with a species-derived special ability. The special should feel
  like a monster-training trait, not a separate command menu. The tame flow
  resolves combat first, skips enemy death/fade animation, then offers a
  dungeon-background nickname prompt with confirmation. Renamed companions
  display as `Nickname (Enemy Name)` so the original animal class remains
  visible.
- Tame action surface: `Tame` appears as a top-level combat option only for
  Ranger/Beast Master while there is no active living tamed companion. It is not
  shown in the normal `Skills` submenu.
- Roster limit: `Tame` adds a new species to the held roster and makes it active
  while room remains. Retaming an already held species strengthens that bond and
  makes it active. A full roster blocks new species with release-required
  messaging instead of silently overwriting an older companion.
- Bond gain: victory with an active living tamed companion creates an
  inverse-scaled bond opportunity. Low-bond companions usually gain larger
  chunks; higher-bond companions gain less and less often. Defeating the current
  `Favored Enemy` creates a smaller extra bond opportunity on the same inverse
  curve. Bond caps at `100`.
- Bond scaling: companion output scales conservatively with bond. Bond also
  updates visible species-family evolution forms. Evolution is currently flavor
  and identity/readability first; deeper evolution-specific stat/action
  differentiation remains a later tuning pass. Generic fallback ranks remain
  `Wild Form`, `Trusted Form`, `Battle Form`, `Pack Form`, and `Apex Form`;
  defined animal families use cleaner themed names such as Rat, Hornet, Bat,
  Spider, Panther, Toad, Snake, Owl, Direwolf, Scorpion, Direbear, Viper,
  Alligator, Eagle, and Antlion ladders.
- Special abilities: V1 tamed specials are compact automatic traits such as
  `Pounce`, `Guard Hide`, `Wingbeat`, `Primal Spark`, and `Keen Scent`. They
  unlock their small combat rider only after the first bond milestone and
  should be described by name in companion inspection rather than as formulas.
- Favored Enemy tracking mastery: `Favored Enemy` is an active combat skill that
  marks the current enemy type as the Ranger's quarry. Keeping the same mark
  through repeated hunts grows a persistent practice benefit; changing quarry
  carries over only a small amount of discipline. Against current Favored Enemy
  targets, the companion gains a small accuracy/damage pressure bonus and bond
  grows faster on victory.
- Beast Master commands: Ranger gets bond/stat growth; Beast Master adds direct
  orders for the next companion action. Add `Pack Strike`, `Guard Partner`,
  `Harry Prey`, and `Mend Wounds`.
- Command behavior: `Pack Strike` focuses companion damage on the current enemy;
  `Guard Partner` reduces the next meaningful hit against the hero if the
  companion is alive; `Harry Prey` applies light Speed or Defense pressure; and
  `Mend Wounds` spends the companion action for a small self/hero sustain
  effect. Commands require a living tamed companion and expire after the
  companion acts, companion death, flee, or combat end.
- Class Ring enhancement: keep `Shared Recovery` identity. Awakened/equipped
  Beast Master ring keeps the current 25% healing echo and scales it modestly
  with bond up to 35% at `True Bond`. The ring also improves command reliability,
  such as stronger `Guard Partner` reduction or better `Mend Wounds` value,
  without adding dual companion turns.
- UI text/surfaces: class/status text should show active companion name/species,
  bond value/rank, evolution form, special ability, held roster count, current
  Favored Enemy, and active pending command without showing `Promotion Tier` in
  class tabs. The `Companion & Hunt` tab may show held inactive companions as
  compact review rows, but only one active tamed companion contributes combat
  actions. Release requires confirmation. Tamed companion Inspect/detail views
  resolve art by original enemy class before nickname/name and show form, trait,
  bond, and flavor notes instead of targetable HP/MP/stat sheets. Ring text
  should describe `Shared Recovery` as bond-scaling healing echo for Beast
  Master and companion. Combat logs should report bond gain as a single general
  increase line, evolution, special-trigger flavor, command use/expiration,
  general Favored Enemy bonus triggers, full-roster tame blocks, and Shared
  Recovery echo.
- Tests: cover tamed companion normalization, legacy save compatibility, flavor
  field defaults, bond clamping, save/load, new species tames adding to the
  bounded roster, duplicate species retames growing/switching bond, full-roster
  release-required blocks, species special assignment, evolution on bond
  thresholds, inverse-scaled bond gain from victory/Favored Enemy victory,
  100 cap, bond stat scaling at 25/50/75/100, Beast Master command requirements/
  effects/expiration, Favored Enemy mark/switch/practice persistence, hunt synergy,
  and bond-scaling Shared Recovery without recursive healing.
- Balance assumptions: this is a V1 held-roster bond-and-command spec, not a
  town stable, collection-reward, or multi-companion combat redesign. Companion
  progression should be visible but conservative; player agency comes mainly
  from choosing the active companion and Beast Master commands.

#### Future Improvements

- Add a Ranger/Beast Master town stable unlock for storing inactive tamed
  companions. In that model the Character Menu `Companion & Hunt` tab should
  list only the active companion and tracking practice, while stable management
  owns stored companion review, rename, release, and lead selection.
- Species collection rewards and multi-companion combat routing remain future
  specs outside V1.

### Shaman/Soulcatcher Totem Resonance

Class Design Inspirations: WoW

V1 implementation spec: deepen the shipped Totem system without changing its core
contracts. Matching casts and Totem pulses build short combat-only `Totem
Resonance`; stacks improve pulse reliability and can be spent with `Totem
Surge` to force the active Totem's highest unlocked pulse. Soulcatcher carries
Shaman forward by adding Soul/harvest scaling, while the awakened ring improves
Resonance for all aspects.

- Preserve current behavior: four elemental communions remain spellbook
  unlocks, not quest flags; Totem pulse base chance remains `35%`; Staff bonus
  remains `+15` percentage points; normal Totem pulse potency remains `50%`;
  Staff matching-cast bonus remains `+20%`; Water Totem spell absorption and
  nonlethal `Soul Drain` remain intact.
- Storage: add no persistent save state in V1. Store combat-only Resonance on
  the active Totem effect, such as `magic_effects["Totem"].extra["resonance"]`.
  Clear Resonance when Totem expires, the active aspect changes, combat ends,
  or save/load restores state.
- Resonance gain: while a Totem is active, casting a matching aspect spell adds
  `+1` Resonance. A successful Totem pulse also adds `+1` Resonance after
  resolving. Resonance caps at `3` stacks by default.
- Resonance payoff: each stack adds `+5` percentage points to the active
  Totem's pulse chance and `+3%` output to player-cast matching aspect spells.
  Resonance bonuses do not change the base `50%` automatic pulse potency
  contract.
- New active skill: add `Totem Surge` for Shaman and Soulcatcher. It requires an
  active Totem, at least 1 Resonance stack, and a known spell for that active
  aspect. It costs modest MP, spends all Resonance, and forces the active
  Totem's highest unlocked matching spell to pulse immediately at normal
  reduced Totem potency.
- Surge guardrails: `Totem Surge` cannot trigger another Resonance gain from
  itself. It fails cleanly if no active Totem, no Resonance, no matching known
  spell, insufficient MP, or no valid target.
- Soulcatcher carry-forward: Soul Aspect uses the same Resonance rules when
  `Soul Drain` is known. Distinct harvested enemy types modestly improve Soul
  Surge value, capped conservatively, while preserving `Soul Drain` as
  nonlethal.
- Class Ring enhancement: keep `Aspect Evolution` identity. Awakened/equipped
  Soulcatcher ring improves Resonance for all aspects: cap becomes `4`, and
  `Totem Surge` gains a small reliability/output bonus. Existing Soul Aspect
  harvested-type scaling remains compatible.
- UI text/surfaces: class/status text should show active Totem aspect,
  Resonance stacks, and ring-enhanced cap when relevant. Combat logs should
  report Resonance gain, Surge spend, forced pulse, Soul harvest contribution,
  and ring-enhanced Resonance behavior.
- Tests: cover Resonance gain from matching casts and successful pulses, stack
  cap/reset/cleanup, pulse chance bonus without changing base pulse potency,
  matching-cast output bonus and Staff stacking, `Totem Surge` requirements/MP
  cost/spend/forced pulse/no self-feeding/no-spell failure, Soul Aspect
  nonlethal Surge scaling, and awakened/equipped Soulcatcher ring cap/output
  behavior without breaking existing Soul Aspect scaling.
- Balance assumptions: this is a V1 combat-depth spec, not permanent Totem
  mastery. Shaman remains the elemental Totem class; Soulcatcher keeps that
  identity and adds Soul/harvest depth. Initial tuning should be conservative
  because Totem pulses already provide free action economy.
