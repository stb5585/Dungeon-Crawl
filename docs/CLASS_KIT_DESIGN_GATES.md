# Class Kit Design Gates

This is the durable class-kit design gate reference. It records shipped
class-mechanics baselines, scope boundaries, and the one-page decision gates
used for deeper class-kit work. Balance validation lives in
`PLAYTEST_CHECKLIST.md`.

## Promotion Kit V1 Status

Status: `V1 Implemented, Tuning/Open Polish`

The promotion class-track V1 pass is implemented through
`src/core/classes/promotion_kits.py` and runtime hooks in player state,
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
- Cleric/Templar: full divine economy redesign, relic quest expansion, and
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

- Stalwart Defender `Resolve` / `Guard Meter`.
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
- Curses and pygame views may differ visually, but both must expose the same
  readable state.
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

### Summoner/Grand Summoner

V1 implementation spec: add per-summon bond progression that lets Summoners borrow
limited invocations from trusted summons, while Grand Summoner keeps the
existing `Conduit Ritual` sacrifice and `+30% Summons` ring scaling.

- Preserve existing scope: keep the current single-active-summon combat model,
  summon leveling, recall behavior, Silence/anti-magic suppression, roster
  acquisition, `Heal Summon`, `Raise Summon`, and Grand Summoner ring scaling.
- Storage: add persistent per-save `summon_bonds`, keyed by known summon name
  and capped at 100. Normalize missing or invalid state to 0 and ignore unknown
  summon keys.
- Bond gain: active summons gain +1 bond after completing a non-Recall combat
  action. Winning combat with an active, living summon grants that summon +5
  bond. Bond gains clamp at 100.
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
- UI text/surfaces: class/ring status text should show known summon bond values
  and Grand Summoner conduit readiness. Combat logs should clearly report bond
  gain, borrowed invocation use, conduit empowerment, and True Name riders.
- Save migration: old saves default to empty/zero bond state. Existing Grand
  Summoner awakening state and `hp_sacrificed` data remain compatible.
- Tests: cover bond normalization/save-load, action and victory bond gain, 100
  cap, 25/75 initialization bonuses stacking with `+30% Summons`, invocation
  unlock gates and representative riders, `Conduit Command` requirements,
  empowerment expiration, and bond-100 ring-only True Name rider behavior.
- Balance assumptions: start conservative; this is a v1 progression layer, not
  a full summon economy redesign or dual-summon combat rewrite.

### Weapon Master/Berserker Bloodied Momentum

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
  Paladin caps at `2`; Crusader caps at `3`.
- Conviction flow: if Conviction exists at action start, the next matching vow
  action spends all stacks before resolving. After resolution, valid vow action
  attempts gain `+1`; clean defining outcomes gain another `+1`, capped.
- Clean outcomes: successful `Redeem`, defeating a challenged or bounty foe for
  `Challenge`, successful guarded block for `Interpose`, and triggered
  `Judgment Riposte`.
- Vow-specific spend riders: `Redeem` gains `+5` percentage points mercy chance
  per stack, and successful mercy gains `+5%` XP/gold per stack while still
  granting no loot/kill/bounty credit. `Challenge` improves challenged-foe
  pressure by `+5%` accuracy/damage per stack for the challenge duration.
  `Interpose` improves the next guarded block by `+5` percentage points block
  chance and `+5%` mitigation per stack. `Judgment Riposte` gains `+10%` Holy
  counter damage per stack plus modest reliability or crit pressure, while
  respecting boss/immunity boundaries.
- `Vow Affirmation`: keep current aura benefits at `1.5x` and mark
  penalties/durations at `0.5x`. While awakened/equipped, after a clean
  matching empowered vow payoff, preserve `1` Conviction once per combat.
  Marks stay separate: Conviction never cleanses, shortens, or disables mark
  drawbacks.
- UI text/surfaces: class/status text should show sworn vow, active aura/mark,
  `Oath Conviction` stacks/cap, and affirmed-ring preservation readiness.
  Combat logs should report Conviction gain, spend, cap, clean outcome bonus,
  vow-specific rider, mark/aura changes, and ring preservation.
- Tests: cover vow normalization, legacy no-vow saves, permanent vow locking,
  signature skill grants, Conviction cap/gain/extra gain/spend order/cleanup,
  all four vow spend riders, immunity boundaries, marks staying separate, and
  awakened/equipped `Vow Affirmation` preserving `1` Conviction once per combat
  after a clean empowered payoff.
- Balance assumptions: V1 supports all four vow paths equally. This is not a
  morality system, oath-respec system, or broader quest arc. Numeric values are
  conservative starting points for playtest tuning.

### Lancer/Dragoon Aerial Tempo And Aerial Supremacy

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
- Aerial Tempo storage: no persistent save state in V1. Lancer caps at `2`;
  Dragoon caps at `3`. Gain `+1` when Jump resolves without being interrupted.
  Clear on combat end, flee, death, save/load restore, class change, or after
  the next eligible follow-through action consumes it.
- Automatic follow-through: the next standard weapon attack or weapon-tagged
  polearm skill consumes all Aerial Tempo. Each stack adds a conservative
  damage and accuracy push; Dragoon also gets a small control rider chance such
  as brief Speed pressure. Misses consume Tempo but do not apply damage riders.
- Jump modification scope: do not add persistent Jump mastery state or extra
  active Jump modification capacity in V1. Existing modification unlocks,
  conflicts, save/load, and execution rules remain intact.
- Class Ring redesign: display the awakened Dragoon ring effect as
  `Aerial Supremacy`. Preserve old `+1 Jump Mod` compatibility internally for
  legacy saves/tests, but the redesign should no longer grant extra active Jump
  modification capacity.
- `Aerial Supremacy`: while the awakened ring is equipped, enhance the automatic
  follow-through after Jump and grant a reduced landing shield under the same
  identity, replacing separate `+1 Jump Mod` and `Meteor Guard` presentation.
- UI text/surfaces: class/status text should show Aerial Tempo stacks, cap,
  pending follow-through, and `Aerial Supremacy` readiness. Combat logs should
  report Tempo gain, interruption cleanup, Tempo spend, follow-through
  damage/control, landing shield, and legacy ring migration/display.
- Tests: cover Aerial Tempo cap, clean-landing gain, no gain on interrupted
  Jump, follow-through consumption, miss behavior, combat-end/save-load
  cleanup, Lancer cap `2`, Dragoon cap `3`, eligible follow-through action
  boundaries, Jump modification compatibility, `Aerial Supremacy` replacing
  extra mod capacity, legacy `+1 Jump Mod` compatibility, and unchanged
  Kaelenon/Recover/Dragon's Fury/Draconite behavior.
- Balance assumptions: this is a V1 extension, not a Jump-system redesign.
  Dragoon ring power shifts from flexibility to offensive/defensive post-Jump
  payoff. Numeric tuning starts conservative and should be adjusted after
  playtest.

### Sentinel/Stalwart Defender Resolve And Counterguard

V1 implementation spec: center Sentinel and Stalwart Defender on baseline `Resolve`,
shield stances, and controlled counterattacks. Sentinel becomes the active
shield-tactics class; Stalwart Defender deepens that loop with a higher Resolve
cap, active spends, `Last Stand` synergy, and awakened-ring automatic major-hit
mitigation.

- Preserve current identity: keep the shield/offhand requirement, heavy armor
  identity, `Shield Block`, `Goad`, `Retaliate`, `Last Stand`,
  `Shield Mastery`, and awakened Stalwart `Guard Meter` compatibility.
- Resolve storage: use the existing Stalwart `guard_meter` save shape as the
  compatibility key where practical, but present the resource as `Resolve`.
  Sentinel caps at `50`; Stalwart Defender caps at `100`. Normalize invalid or
  missing values on load and clamp to the class cap.
- Resolve gain: `Defend`, successful blocks, mitigated physical hits, and
  shield-tactic actions such as `Goad` build Resolve. Log gains clearly and
  report when Resolve is capped.
- Sentinel shield loop: add `Hold the Line`, a shield-required stance that
  improves block/mitigation and pressures the current enemy to engage.
  `Retaliate` remains the counter identity: successful blocks can trigger a
  modest weapon counter, with stronger reliability while `Hold the Line` is
  active.
- Stalwart spends: add `Bulwark`, spending Resolve for a short barrier or
  next-hit mitigation pulse, and `Shield Riposte`, spending Resolve after
  blocking or while guarded for a controlled counter with light Attack or Speed
  pressure.
- `Last Stand` synergy: keep the attack tradeoff, but improve low-HP block
  reliability and Resolve gain so the skill reinforces the wall-and-counter
  loop instead of acting as a disconnected passive.
- Class Ring enhancement: awakened/equipped `Shield Mastery` keeps the current
  automatic major-hit reduction. At full Resolve, the ring spends `100` Resolve
  to reduce a major incoming hit by `40%`. The ring also modestly improves
  block chance, spell-block eligibility, and counter reliability without
  replacing active Resolve spends.
- UI text/surfaces: class status should show Resolve, cap, active guard stance,
  and ring auto-guard readiness. Combat logs should report Resolve gain/spend,
  capped Resolve, blocks, barriers, ripostes, and automatic ring mitigation.
- Tests: cover Sentinel and Stalwart Resolve caps, gain sources, clamping,
  save/load normalization, legacy Stalwart `guard_meter` compatibility,
  `Hold the Line` shield requirements and expiration, `Retaliate` counter
  behavior, `Bulwark` and `Shield Riposte` costs/gates/effects/failure text,
  `Last Stand` low-HP defensive benefits and attack tradeoff, and
  awakened/equipped ring auto-spend behavior.
- Balance assumptions: this is a V1 shield-depth spec, not a party-tank or
  multi-target threat rewrite. Sentinel/Stalwart should feel like
  `Wall + Counter`: survive pressure, then answer with controlled retaliation.
  Numeric tuning starts conservative and should be adjusted after playtest.

### Thief/Rogue Fortune And Misfortune

V1 implementation spec: replace the earlier simple luck-pip idea with paired
combat-only `Fortune` and `Misfortune` meters. Thief gains stronger loot
identity through `Scavenger's Eye`; Rogue carries that forward with
`Finders Keepers`, `Cheat Death`, and a smoother risk/reward loop where success
improves odds and failure fuels bigger eventual payoffs.

- Preserve current identity: Footpad stealth/toolkit carry-forward remains
  intact. `Lockpick`, `Master Lockpick`, `Steal`, `Mug`, `Gold Toss`,
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
- Hybrid payoff: the next damaging spell, standard weapon hit, or weapon-tagged
  trickster skill spends all Charge before resolving. On a successful hit or
  damaging spell, each stack adds conservative arcane pressure: a small damage
  boost plus modest crit, status, or reliability pressure. Misses or fully
  negated actions consume Charge but apply no rider.
- Class Ring display: show the awakened Arcane Trickster effect as
  `Arcane Larceny`, while preserving existing internal `Spell Steal Buff`
  compatibility for saves and tests. Awakened/equipped `Arcane Larceny` keeps
  the current 3-turn `+20%` Magic damage and `+10%` dodge after successful spell
  theft.
- Ring enhancement: once per combat after a clean charged payoff,
  awakened/equipped `Arcane Larceny` preserves `1` Stolen Charge. It should not
  create free Blank Scrolls, bypass trial immunity, or make stolen spells
  permanent beyond the existing `Steal Spell 2` behavior.
- UI text/surfaces: class status should show `Stolen Charge`, cap, and
  `Arcane Larceny` preservation readiness. Combat logs should report Charge
  gain, capped Charge, spend, miss consumption, charged payoff, stolen-scroll
  contribution, and ring preservation.
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

### Cleric/Templar Devotion Ward

V1 implementation spec: make Cleric and Templar the holy defender branch through
combat-only `Devotion`. Cleric starts a modest healing, holy, shield, and
`Pious Bounty` rhythm, while Templar carries that forward with a higher cap,
stronger ward spends, `Holy Retribution` as a Devotion window, and awakened
`Ordered Blessings` smoothing the loop.

- Preserve current behavior: Healer spell carry-forward; Cleric shield/holy
  utility; `Shield Slam`, `Shield Block`, `Pious Bounty`, and `True Strike`;
  Templar shield/offhand identity; `Parry`, `Piercing Strike`, `Goad`,
  `Charge`, `Double Strike`, `True Piercing Strike`, `Holy Retribution`; and
  awakened `Ordered Blessings`.
- Devotion storage: no persistent save field in V1. Devotion is combat-only,
  starts at 0, and clears on combat end, flee, death, save/load restore, class
  change, or leaving the Cleric/Templar track. Cleric caps at `3`; Templar caps
  at `5`.
- Devotion gain: meaningful healing, Holy damage, successful `Turn Undead`,
  shield-tactic actions, and successful defensive blocks can grant `+1`
  Devotion, limited to once per player action.
- `Pious Bounty`: remains a reward accent, not the central economy loop.
  Righteous or undead-victory hooks can grant modest extra gold and should log
  providence clearly. A qualifying `Turn Undead` kill can also grant `+1`
  Devotion during combat.
- `Sanctuary Ward`: new Cleric/Templar active skill. It costs MP, requires at
  least `1` Devotion, and spends all stacks for a short barrier or next-hit
  mitigation pulse. More stacks improve mitigation and add a small cleanse or
  Regen chance.
- `Relic Aegis`: new Templar active skill. It costs MP, requires at least `2`
  Devotion and a shield/offhand defensive setup, and spends all stacks for
  stronger mitigation plus a brief holy counter or guard pulse.
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
- UI text/surfaces: class status should show Devotion stacks/cap, active ward,
  `Holy Retribution` window, next `Ordered Blessing`, and once-per-combat
  preservation readiness. Combat logs should report Devotion gain, cap, spend,
  ward strength, `Pious Bounty` providence, `Holy Retribution` riders, blessing
  rotation, and ring preservation.
- Tests: cover Healer -> Cleric and Cleric -> Templar ability carry-forward,
  Devotion caps/gain sources/once-per-action limit/cleanup, `Pious Bounty`
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

V1 implementation spec: center Ranger and Beast Master on one persistent tamed
companion. Ranger keeps `Tame` and `Favored Enemy`, gains companion bond and
conservative companion growth, while Beast Master carries that bond forward with
direct companion commands and stronger awakened-ring `Shared Recovery`.

- Preserve current scope: keep one active tamed companion, compact save state,
  replacement on new tame, existing companion-as-`familiar` behavior, `Tame`,
  `Favored Enemy`, `Pack Bond`, and awakened `Shared Recovery`.
- Storage: extend existing `tamed_companion` save state with `bond` from `0` to
  `100`, defaulting to `0`, and combat-only `pending_command`, cleared on combat
  end and save/load. Clamp invalid values on load; legacy saves without bond
  default cleanly.
- Replacement: a new tame replaces the old companion and starts a fresh bond.
  Do not add stable, roster, inactive bond memory, or species collection rules
  in V1.
- Bond gain: gain `+1` when the tamed companion completes a combat action, `+4`
  when combat is won with the companion active and alive, and `+2` extra when
  the defeated enemy type matches current `Favored Enemy`. Bond caps at `100`.
- Bond scaling: companion HP, damage, and defense scale conservatively with bond
  up to `+15%` at bond 100. Milestones are bond 25 `Trusted`, bond 50
  `Battle-Trained`, bond 75 `Packmate`, and bond 100 `True Bond`.
- Favored Enemy hunt synergy: keep Ranger's current personal bonus from kill
  history. Against current Favored Enemy targets, the companion gains a small
  accuracy/damage pressure bonus and bond grows faster on victory.
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
- UI text/surfaces: class/status text should show companion name/species, bond
  value/rank, current Favored Enemy, and active pending command. Ring text
  should describe `Shared Recovery` as bond-scaling healing echo for Beast
  Master and companion. Combat logs should report bond gain, milestone reach,
  command use/expiration, Favored Enemy hunt synergy, and Shared Recovery echo.
- Tests: cover tamed companion normalization, legacy save compatibility, bond
  clamping, save/load, new tame replacement resetting bond, bond gain from
  companion action/victory/Favored Enemy victory, 100 cap, bond stat scaling at
  25/50/75/100, Beast Master command requirements/effects/expiration, Favored
  Enemy personal bonus preservation, hunt synergy, and bond-scaling Shared
  Recovery without recursive healing.
- Balance assumptions: this is a V1 bond-and-command spec, not a stable, monster
  collection, or multi-companion combat redesign. Companion progression should
  be visible but conservative; player agency comes mainly from Beast Master
  commands.

### Shaman/Soulcatcher Totem Resonance

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
