# Multi-Enemy Ability And Mechanic Inventory

## Status

Status: `Implemented through Slice 6 development pilot`

This inventory records the targeting and trigger contracts now represented by
runtime metadata. Abilities without explicit migrated YAML metadata continue
through the documented legacy inference defaults.

## Defaults

Abilities not called out below retain their current singleton behavior and use
these migration defaults:

- an offensive ability that currently consumes the defender is
  `SINGLE_ENEMY`;
- a support ability that applies only to its user is `SELF`;
- combat commands without a character target, including Flee, Recall, and
  Pickup Weapon, are `NONE`;
- no existing ability becomes `ALL_ENEMIES` merely because its description
  uses plural or area language;
- action cost and cast-level hooks run once; damage, status, reactions, and
  eligible defeat triggers run once per affected enemy;
- invisible enemies remain legal direct targets with the existing penalty and
  remain members of `ALL_ENEMIES`.

## Ability Inventory

| Canonical ability | Current behavior | Approved scope | Cost | Charge/delay | Lost-target policy | Reaction exposure | Trigger cadence |
|---|---|---|---:|---|---|---|---|
| Basic Attack | Hits current defender | `SINGLE_ENEMY` | none | none | n/a | dodge, block, thorns, Riposte per target | once per target |
| Jump | Charged leap at current defender | `SINGLE_ENEMY` | 10 MP | 1 turn | `LOCKED` | normal physical reactions on release | cost once; hit/kill per target |
| Charge | Charged weapon rush | `SINGLE_ENEMY` | 10 MP | 1 turn | `LOCKED` | normal physical reactions on release | cost once; hit/kill per target |
| Crushing Blow | Charged heavy strike | `SINGLE_ENEMY` | 25 MP | 1 turn | `LOCKED` | normal physical reactions on release | cost once; hit/kill per target |
| Shadow Strike | Charges, then strikes from concealment | `SINGLE_ENEMY` | 20 MP | 1 turn | `RETARGET_FOCUS` | normal physical reactions on release | cost once; hit/kill per target |
| Arcane Blast | Charged magical power-up attack | `SINGLE_ENEMY` | 0 MP | 1 turn | `RETARGET_FOCUS` | Reflect/Counterspell for resolved target | charge once; hit/kill per target |
| Wormhole | Sends another spell two turns forward | inherited from stored spell | 10 MP plus stored spell cost | 2 turns | `LOCKED` for single target; `SNAPSHOT_ROSTER` for future all-enemy spells | inherited per resolved target | both costs once; stored cast once |
| Hallowed Ground | Applies a three-turn field to supplied foes and healing field to caster | `ALL_ENEMIES` reference field | 20 MP | field ticks 3 owner turns | roster resolved at cast | status application and field damage per enemy | cast once; field portion per enemy; healing once |
| Earthquake | Direct earth damage and independent Prone checks | `ALL_ENEMIES` | 26 MP; full 2.5 modifier per target | none | `SNAPSHOT_ROSTER` | Reflect and Counterspell independently per enemy; flying is explicit no-effect | cost/cast once; damage, defense, effect, and reaction per enemy |
| Windswept | Attempts to remove one foe or lifts its user | `SINGLE_ENEMY`, or `SELF` when explicitly self-cast | 15 MP | none | n/a | target portion only | cast once; ejection ledger once |
| Smoke Screen | Consumes its resource to attempt encounter flee | `NONE` | 5 MP plus Smoke Bomb rule | none | n/a | fastest perceiving-hostile flee contest | once per attempt |
| Reflect | Places a spell-reflection ward on its user | `SELF` | 14 MP | duration effect | n/a | reflects only that target portion | once per reflected portion |
| Counterspell | Enemy retaliation after a spell portion | `SELF` reaction | 0 MP | reactive | n/a | retaliates independently per target portion; never cancels whole cast | at most once per eligible portion |
| Rewind | Restores the previous player choice-point snapshot | `NONE` | 40 MP | full encounter snapshot | restores roster, ledger, cycle, focus, pending/delayed actions, summon slot, and character effects | no direct reaction | once per cast |
| Foretell | Inspects the current enemy's next action | `SINGLE_ENEMY` | ability-defined | none | n/a | none | once per chosen target |
| Tame | Converts one eligible animal into a companion | `SINGLE_ENEMY` | ability-defined | none | n/a | target validation only | one `tamed` resolution; no normal kill rewards |
| Redeem / Mercy | Offers one eligible foe mercy | `SINGLE_ENEMY` | ability-defined | none | n/a | target validation only | one `mercy` resolution and restitution |
| Repel the Wicked | Removes or destroys one eligible fiend/undead | `SINGLE_ENEMY` | ability-defined | none | n/a | target validation only | `escaped/paladin_repel` or ordinary defeat |
| Summon / Recall | Replaces or restores the single player-side active slot | `NONE` | summon-defined | none | n/a | none | summon setup once per action; summon XP once per encounter |
| Familiar / companion / Totem automatic action | Uses current defender implicitly | `SINGLE_ENEMY` | mechanic-defined | automatic | `RETARGET_FOCUS` | normal target reactions | once per automatic action; rewards remain encounter-ledger driven |
| Battle Hymn / Bard opening fields | Enumerates current participants implicitly | `ALL_ENEMIES` when hostile-wide; otherwise `SELF` | ability-defined | duration/field | `SNAPSHOT_ROSTER` if delayed | per affected member | activation once; portion per member |
| Dragon Breath family | Charged enemy attack against the sole active player-side slot | `SINGLE_ENEMY` | enemy-defined | charged | `LOCKED` | player-side reactions once | cost/charge once; result once |

## Trigger Inventory

| Trigger or reward | Approved cadence | Eligibility |
|---|---|---|
| MP/item/rune spend and cast-level events | per action | always when the action commits |
| Damage, status, Reflect, Counterspell, thorns, retaliation | per target portion | only the affected target |
| Kill dictionary, gameplay defeat count, Bestiary defeat | per enemy | `defeated` only |
| Loot, bounty, quest defeat progress | per enemy | eligible `defeated` enemies only |
| Soul Harvest, death marks, on-kill class resources | per enemy | eligible `defeated` enemies only |
| Paladin enemy hooks and Lycan frenzy check | per enemy | resolution-specific; active frenzy does not extend |
| Ejection XP | per enemy | half XP; no kill-linked credit |
| Mercy restitution | per enemy | `mercy` only |
| Total XP award and summon XP settlement | per encounter | sum eligible ledger entries, then award once |
| Level-up, Battle Scar, contracts, class-kit cooling | per encounter | after reward aggregation |
| Grandmaster settlement and combat cleanup | per encounter | exactly once |
| Encounter/victory statistics and `promotion_kits.end_combat` | per encounter | exactly once |

## Slice Gates

- Slice 2 target-scope, target-loss, explicit-intent, actor-cycle, focus, and
  pending-target contracts are implemented for headless singleton/pair combat.
- Slice 3 structured Hallowed Ground and full-damage Earthquake resolution is
  implemented with ordered, per-combatant portions.
- Slice 4 exposes explicit focus and combatant-ID presentation in Pygame.
- Slice 5 implements ledger-based reward cadence and encounter simulation.
- Slice 6 provides three development-only curated pairs. No additional
  abilities or enemy area actions are promoted by that pilot.
