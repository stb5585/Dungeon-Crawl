# Multi-Enemy Development Pilot 2

## Status

Complete. Automated screening and seven targeted manual battles are recorded.
The three stable keys remain explicit development overrides and are not
included in random generation. One candidate passes every automated gate; two
remain blocked from promotion by their measured duration despite acceptable
manual pacing.

## Purpose

The second pilot broadens early-floor coverage after the first pilot's
20-battle manual evidence pass. It reuses explicit targeting, structured
settlement, the corrected simulator policy, and the same aggregate gates.

## Proposed Candidates

| Working key | Floor | Proposed members | Reason to test |
|---|---:|---|---|
| `grave_web` | 1 | Zombie, Giant Spider | slow durable enemy plus control/evasion pressure |
| `lesser_conspiracy` | 1 | Imp, Quasit | two distinct caster-like enemies without duplicate species |
| `hoof_and_howl` | 2 | Satyr, Direwolf | mixed utility and direct martial pressure |

These are screening candidates, not accepted compositions. Use them only with
`DUNGEON_FORCE_ENCOUNTER=<key>` or direct test/simulator APIs. Each must be
rejected or replaced if it creates double hard control, double invisibility,
a support loop, invalid targeting, or a max-turn policy outcome.

### Initial Screening Result

All three proposals were rejected at the full 500-battle aggregate:

| Key | Win rate | Turn ratio | Winning HP | Invalid/max-turn | Decision |
|---|---:|---:|---:|---:|---|
| `grave_web` | 87.4% | 3.29x | 43.3% | 0 / 0 | replace |
| `lesser_conspiracy` | 68.0% | 2.43x | 43.1% | 0 / 0 | replace |
| `hoof_and_howl` | 50.4% | 3.62x | 43.9% | 0 / 0 | replace |

The same-floor screening results next nominate `Zombie & Quasit`,
`Imp & Giant Spider`, and `Twisted Dwarf & Naga`, excluding Pilot 1 compositions
and keeping the two floor-1 selections distinct. The stable development keys are
retained while factual display names and authored members change.

The first floor-2 replacement also failed its full aggregate at 45.6% wins and
2.23x turns, with Mage and Pathfinder disproportionately suppressed by Naga's
Silence. The next screened floor-2 composition is `Twisted Dwarf & Xorn`.

Full confirmation also rejected `Imp & Giant Spider` at 75.8% wins, 2.65x
turns, and 76 repeated non-progress diagnostics. The next distinct screened
floor-1 composition is `Battle Toad & Satyr`.

## Selected Development Candidates

The stable keys retain their environment compatibility while display names,
members, and encounter-local modifiers reflect the selected screening result.
Modifiers apply only to freshly built pair members; singleton enemies and
reward values remain unchanged.

| Key | Floor | Final members | Health/offense | Wins | Turns | Winning HP | Stability | Gate |
|---|---:|---|---:|---:|---:|---:|---|---|
| `grave_web` | 1 | Zombie & Quasit | 0.85 / 1.20 | 72.4% | 2.18x | 47.5% | 0 invalid / 0 max-turn | Blocked: duration |
| `lesser_conspiracy` | 1 | Battle Toad & Satyr | 0.80 / 1.10 | 71.4% | 2.42x | 43.3% | 0 invalid / 0 max-turn | Blocked: duration |
| `hoof_and_howl` | 2 | Twisted Dwarf & Xorn | 0.90 / 1.10 | 56.8% | 1.86x | 45.4% | 0 invalid / 0 max-turn | Pass |

The passing Xorn aggregate recorded four repeated-non-progress diagnostics but
no max-turn loop. Its class spread remains an important manual diagnostic:
Mage won 0%, Pathfinder 13%, Footpad 98%, Healer 88%, and Warrior 85%.
Individual class rates do not gate acceptance under the approved contract,
but Pilot 2 manual battles should emphasize Mage and Pathfinder readability
and viability before any later promotion discussion.

The full confirmation commands used the five base classes, 100 iterations per
class, and seed 1337:

```bash
./.venv/bin/python tools/run_balance_suite.py \
  --tier base --level 5 \
  --classes Warrior Mage Footpad Healer Pathfinder \
  --encounters grave_web lesser_conspiracy \
  --iters 100 --seed 1337

./.venv/bin/python tools/run_balance_suite.py \
  --tier base --level 10 \
  --classes Warrior Mage Footpad Healer Pathfinder \
  --encounters hoof_and_howl \
  --iters 100 --seed 1337
```

The bounded grids used every 0.80–1.20 health/offense combination in 0.05
increments. `tools/search_curated_pair_tuning.py --members FIRST SECOND`
provides the focused exhaustive search and correctly ranks a no-pass grid by
lowest metric score. Reports are retained under `reports/balance_baselines/`.

Automated Pilot 2 status: `Partial pass (1 accepted, 2 blocked)`

Manual Pilot 2 status: `Pass (7 completed, 0 blocking defects)`

The two required runs per pair completed, and a seventh run exercised Hallowed
Ground against both members through the `ALL_ENEMIES` path. Testers found the
two blocked floor-1 pairs acceptable in manual play, but that qualitative
result does not erase their automated duration failures.

Repository validation completed with 2,569 passing tests. After adding focused
ranking coverage, the balance/catalog suite passed another 17 tests and
`git diff --check` remained clean. The final singleton parity command produced
the same 117 lines and SHA-256
`edccb0d62fecdf1d350189421aa9d5d9a2004a388c9bde2664df3896b7993fbe`
as the Slice 0 baseline.

## Selection And Validation

1. Re-run every proposed composition at its floor benchmark:
   floor 1 at level 5 and floor 2 at level 10.
2. Use Warrior, Mage, Footpad, Healer, and Pathfinder for 100 iterations each
   with seed 1337.
3. Require 55-75% aggregate wins, 1.25-2.0 times the harder singleton actor
   turns, 20-60% median winning HP, and zero crashes, invalid intents, or
   max-turn loops.
4. Treat individual class rates as diagnostic only.
5. Apply the same same-floor replacement and bounded 0.80-1.20 local
   multiplier procedure when a proposal fails.
6. Add stable debug keys only after automated selection, then complete six
   manual battles total: two battles for each of the three pairs.

## Next Phase After Pilot 2

Both early-floor curated pilots are complete. The next development phase will
select and validate curated pairs for deeper dungeon floors using the same
simulator, explicit debug overrides, and floor-appropriate benchmarks. It
must define eligible deeper floors and ordinary-enemy catalogs before choosing
compositions.

Normal random pair generation remains deferred. Its separate promotion gate
must still decide probability, eligible tiles, progression impact, exclusions,
telemetry, and a runtime kill switch. More than two enemies remains out of
scope.

## Manual Evidence

Pilot 2 required **six completed battles total, two per pair**. This was a
targeted confirmation pass rather than Pilot 1's 20-battle evidence run.
A Mage and a Pathfinder covered the two required `hoof_and_howl` runs because
those classes were its weakest automated diagnostics. A seventh Paladin run
exercised Hallowed Ground and the `ALL_ENEMIES` resolution path.

For each run, answer:

1. Did combat complete without a crash, invalid intent, stuck turn, or stale
   enemy state on retry?
2. Were focus selection, focus fallback, and action commitment clear?
3. Were both sprites correctly scaled, grounded (or airborne), and readable?
4. Did impacts, statuses, resolution removal, and reward presentation anchor
   to the correct combatant?
5. Did the encounter duration feel acceptable? For the two blocked pairs,
   note specifically whether combat felt excessively long.

| # | Pair key | Required class/build | Result and duration | Targeting/focus | Scale, ground, effects, removal | Cleanup/rewards | Defect |
|---:|---|---|---|---|---|---|---|
| 1 | `grave_web` | Gnome Mage (lvl 5) / Firebolt and Defense | easy win / 3 turns (did not feel too long) | targeting clear | sprites look good and grounded | good on all accounts | no defects encountered |
| 2 | `grave_web` | Giant Warrior (lvl 1) / Shield Slam | close defeat / 4 turns (defeated zombie on first hit, then couldn't hit Quasit after it transformed into Electric Bat) | good | good | good | no issues |
| 3 | `lesser_conspiracy` | Half Orc Footpad (lvl 1) / Quickstep | defeat / 2 turns (killed Battle Toad on first attack, Satyr stomped and stunned, then killed player on next turn) | good | good | good | no defects |
| 4 | `lesser_conspiracy` | Half Orc Footpad (lvl 1) / Balanced | easy win / 3 turns (killed Satyr first, Battle Toad charged Jump, blinded Toad who missed Jump, then killed on 3rd turn) | good | good | good | no defects |
| 5 | `hoof_and_howl` | Elf Mage, level 10 | fairly easy win / 3 turns (mage was attacked first and took damage, then used Mana Shield, then killed Dwarf with Tremor and then Xorn with Firebolt while taking absorbed damage) | good | good | good | no defects |
| 6 | `hoof_and_howl` | Half Elf Pathfinder, level 10 | fairly easy win / 2 turns (pathfinder attacked first and took damage, Xorn consumed Bless Scroll, Pathfinder cast Water Jet and injured Dwarf, Xorn expired from Doom because apparently the Bless Scroll applied that to it, then Pathfinder finished off Dwarf with Tremor) | good | no clear indication that Xorn was affected by Doom, although I don't know if that is bad without Sight | good | no defects |
| 7 | `hoof_and_howl` | Human Paladin, level 55 | easy win / 1 turn (Dwarf attacked, then Xorn ate antidote, then Hallowed Ground killed both of them) | good | good | good | no defects |

Manual status: `Complete - 7 runs, including dedicated ALL_ENEMIES coverage`

Pilot status: `Complete - deeper-floor curated validation is next`
