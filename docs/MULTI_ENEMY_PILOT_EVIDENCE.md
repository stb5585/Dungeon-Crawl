# Multi-Enemy Curated Pilot Evidence

## Status

- Pilot 1 implementation: `Complete`
- Original 20-battle manual matrix: `Complete`
- Corrected automated balance gate: `Pass`
- Post-fix targeted confirmation: `Complete`
- Normal random-generation promotion: `Not authorized`

The development-only Pilot 1 feature, original manual matrix, and targeted
post-fix acceptance pass are complete.

## Scope

The pilot remains development-only. It does not enable random paired
encounters or authorize rosters larger than two.

| Key | Floor | Authored roster |
|---|---:|---|
| `carrion_crawl` | 1 | Giant Hornet, Battle Toad (0.95 health) |
| `wing_and_mattock` | 1 | Electric Bat, Battle Toad |
| `fang_and_spear` | 2 | Twisted Dwarf, Vampire Bat |

Use `DUNGEON_FORCE_ENCOUNTER=<key>` on an ordinary random-encounter floor.
`DUNGEON_FORCE_ENEMY` and `DUNGEON_FORCE_ENCOUNTER` are mutually exclusive.

## Automated Evidence

Historical Slice-6 command:

```bash
./.venv/bin/python tools/run_balance_suite.py \
  --tier base \
  --level 10 \
  --classes Warrior Mage Footpad Healer Pathfinder \
  --encounters carrion_crawl wing_and_mattock fang_and_spear \
  --iters 100 \
  --seed 1337
```

Acceptance requires 500 simulations per pair, zero crashes or invalid target
states, 55-75% aggregate player wins per pair, and no unexplained singleton
baseline drift. Results outside the target bands are evidence for review, not
authorization to tune enemy or ability values.

Completed on 2026-08-03. The command ran 500 paired simulations per
encounter plus 100 singleton comparisons for each member/class combination
(1,500 pair battles and 3,000 comparison battles). It completed with zero
crashes or invalid actor/target states.

Report:
`reports/balance_baselines/multi_enemy_slice6_pilot.txt`

Report SHA-256:
`cddb012def693accad470226c15df7538917c127e9cb83bc2ff50280e39d9df0`

| Pair | Win rate | Actor-turn ratio | Median winning HP | Automated gate |
|---|---:|---:|---:|---|
| Carrion Crawl | 100.0% | 2.11x | 81.8% | Fail |
| Wing and Mattock | 80.0% | 1.49x | 74.6% | Fail |
| Fang and Spear | 85.8% | 2.07x | 58.9% | Fail |

Wing and Mattock meets the actor-turn ratio band, and Fang and Spear meets the
winning-HP band. No pair meets all automated acceptance bands. In particular,
Pathfinder lost all 100 Wing and Mattock simulations while every other class
won all 100, indicating a class-specific interaction that should be
investigated before any tuning proposal.

The post-implementation singleton report is byte-identical to the Slice 0
baseline: 117 lines, `cmp` exit 0, SHA-256
`edccb0d62fecdf1d350189421aa9d5d9a2004a388c9bde2664df3896b7993fbe`.

Final repository validation completed with 2,544 passing tests. The focused
simulator regression suite completed with 31 passing tests, and
`git diff --check` reported no whitespace errors.

Automated status: `Completed - promotion blocked by acceptance metrics`

## Pilot Fix And Floor-Correct Balance Pass

The simulator now records action sequences, invalid intents, max-turn
outcomes, and repeated non-progress selections. For paired encounters, its
deterministic policy supplies Earth to Totem, does not recast an active Totem,
skips unsupported utility and invalid weapon skills, and stops heal/item
prolongation late in a bounded simulation. This eliminated the Pathfinder
`Natural Attunement` zero-damage loop. Singleton action selection remains on
the historical policy so its longitudinal balance report stays directly
comparable to Slice 0.

The original compositions were remeasured at their authored-floor
benchmarks:

```bash
./.venv/bin/python tools/run_balance_suite.py \
  --tier base --level 5 \
  --classes Warrior Mage Footpad Healer Pathfinder \
  --encounters carrion_crawl wing_and_mattock \
  --iters 100 --seed 1337

./.venv/bin/python tools/run_balance_suite.py \
  --tier base --level 10 \
  --classes Warrior Mage Footpad Healer Pathfinder \
  --encounters fang_and_spear \
  --iters 100 --seed 1337
```

| Original key | Level | Win rate | Turn ratio | Winning HP | Policy faults |
|---|---:|---:|---:|---:|---:|
| `carrion_crawl` | 5 | 89.8% | 2.25x | 46.7% | 0 |
| `wing_and_mattock` | 5 | 91.2% | 1.78x | 39.2% | 0 |
| `fang_and_spear` | 10 | 33.6% | 1.88x | 47.5% | 19 max-turn |

The same-floor search tool evaluated all 55 distinct floor-1 compositions and
170 eligible floor-2 compositions after excluding duplicate species, bosses,
double hard-control, double invisibility, and double support loops:

```bash
./.venv/bin/python tools/search_curated_pair_tuning.py \
  --floor 1 --level 5 --iters 5 --seed 1337

./.venv/bin/python tools/search_curated_pair_tuning.py \
  --floor 2 --level 10 --iters 1 --seed 1337
```

Catalog-order scoring selected `Giant Hornet & Battle Toad`,
`Electric Bat & Battle Toad`, and `Twisted Dwarf & Vampire Bat`. The first
floor-1 composition required the nearest bounded duration adjustment,
0.95 health and 1.0 offense; the other selected pairs remain at 1.0/1.0.
The stable environment keys did not change.

Full confirmation status:

| Key | Level | Composition | Health/offense | Win rate | Turn ratio | Winning HP | Policy faults | Gate |
|---|---:|---|---:|---:|---:|---:|---:|---|
| `carrion_crawl` | 5 | Giant Hornet & Battle Toad | 0.95 / 1.00 | 69.6% | 1.89x | 43.5% | 0 | Pass |
| `wing_and_mattock` | 5 | Electric Bat & Battle Toad | 1.00 / 1.00 | 71.8% | 1.76x | 43.8% | 0 | Pass |
| `fang_and_spear` | 10 | Twisted Dwarf & Vampire Bat | 1.00 / 1.00 | 63.6% | 1.58x | 53.2% | 0 | Pass |

Search and confirmation reports are retained under
`reports/balance_baselines/`. Metrics outside a band remain evidence, not
authorization for global enemy, ability-cost, or area-damage changes.

Automated balance-pass status: `Pass`

All six targeted manual confirmations passed. This closes Pilot 1 evidence but
does not enable random pair generation. Pilot 2 subsequently closed with its
own seven-run manual pass; the separate normal-generation promotion decision
remains outstanding.

Manual Confirmations

- no-Sight ordinary enemy: `Confirmed`; sprites remain visible while exact
  combat details are hidden.
- Sight: `Confirmed`; exact details are visible, and the
  unsupported focus-marker glyph has now been replaced with a drawn triangle.
- Invisible enemy: `Confirmed`; no-Sight presentation now hides
  the sprite and canonical identity, using `Unseen force` in the HUD and combat
  log. Sight continues to reveal the normal sprite and identity.
- Mixed resolution: `Confirmed`; complete one encounter with two different
  terminal resolutions, such as defeating one enemy and sparing, taming, or
  ejecting the other.
- Area attack: `Confirmed`; exercise Earthquake or Hallowed Ground against a
  living pair and confirm both target animations and results are readable.
- Consecutive enemy turns: `Confirmed`; the fixed actor order can give both
  enemies consecutive actions, including while the player is incapacitated.

The failed-encounter reset also now clears cached death-animation state. A
member defeated before player defeat therefore returns with both restored
runtime state and a visible sprite when the full authored encounter is retried.
The post-fix repository validation passed all 2,565 tests, and
`git diff --check` reported no whitespace errors.

The final singleton parity command was rerun after the policy split:

```bash
./.venv/bin/python tools/run_balance_suite.py \
  --tier base --level 10 --iters 30 --seed 1337
```

The generated 117-line report is byte-identical to
`reports/balance_baselines/multi_enemy_slice0_pre_refactor.txt`; `cmp`
returned 0 and both files have SHA-256
`edccb0d62fecdf1d350189421aa9d5d9a2004a388c9bde2664df3896b7993fbe`.
The completed repository validation passed all 2,552 tests, and
`git diff --check` reported no whitespace errors.

## Manual Evidence

Record 20 completed battles, including at least five for each pair. Check
focus readability, hidden-information clarity, action commitment, status and
impact anchoring, death/resolution presentation, reward summaries, and
crash-free cleanup.

| # | Pair key | Class/build | Result | Focus/readability notes | Defect |
|---:|---|---|---|---|---|
| 1 | carrion_crawl | Human Warrior (lvl 30)/no points distributed | easy win | reward summaries should be cumulative; cards still show some combat animations like strike, fade, and faint when defeated | no enemy sprites; card overlays feel detached from combat instead of part of the battlefield; no enemy movement animations like sway |
| 2 | carrion_crawl | Elf Mage (lvl 1)/Firebolt | easy defeat | log message should indicate defeat of individual enemies |  |
| 3 | carrion_crawl | Elf Mage (lvl 10)/Sorcerer Path | easy win |  |  |
| 4 | carrion_crawl | Half Orc Pathfinder (lvl 10)/Shaman Path | easy win |  |  |
| 5 | carrion_crawl | Half Elf Healer (lvl 5)/Holy & Monk Path | close win |  |  |
| 6 | carrion_crawl | Gnome Footpad (lvl 5)/Balanced | close win |  |  |
| 7 | wing_and_mattock | Half Giant Warrior (lvl 2)/Sword & Board | close defeat |  |  |
| 8 | wing_and_mattock | Half Giant Warrior (lvl 5)/Sword & Board | close win | had to fight another battle to confirm the enemy group changed correctly |  |
| 9 | wing_and_mattock | Dwarf Healer (lvl 2)/Priest | easy defeat |  |  |
| 10 | wing_and_mattock | Dwarf Healer (lvl 4)/Priest | close defeat |  |  |
| 11 | wing_and_mattock | Human Footpad (lvl 4)/Balanced | defeat |  |  |
| 12 | wing_and_mattock | Human Footpad (lvl 10)/Balanced | easy win |  |  |
| 13 | fang_and_spear | Half Giant Warrior (lvl 10)/Weapon Master Path | easy win |  | combat moves very slow; time between each character's action feels like it takes forever |
| 14 | fang_and_spear | Human Warrior (lvl 30)/no points distributed | easy win |  |  |
| 15 | fang_and_spear | Human Warrior (lvl 30)/no points distributed | easy win | equipping Pendant of Vision reveals enemy sprites and HP | enemy sprites should only be hidden if invisible without sight; Sight should also reveal MP; the turn box with active token blocks part of the card on left |
| 16 | fang_and_spear | Human Sentinel (lvl 30) | easy win |  |  |
| 17 | fang_and_spear | Human Stalwart Defender (lvl 66) | easy win |  |  |
| 18 | fang_and_spear | Elf Sorcerer (lvl 30) | easy win |  |  |
| 19 | fang_and_spear | Half Giant Footpad (lvl 4) | easy defeat | Debug Auto-kill works on single enemy as expected |  |
| 20 | fang_and_spear | Half Giant Footpad (lvl 10) | close defeat (started combat injured) |  |  |

Manual status: `Complete`

## Promotion Decision

The curated encounters remain development-only. The corrected automated
balance bands and post-fix targeted manual confirmations pass. Pilot 1 is
closed, but these results do not authorize global stat, ability-cost,
area-damage, normal-generation, or roster-size changes. Pilot 2 is also now
complete after seven targeted manual runs, including dedicated Hallowed Ground
and `ALL_ENEMIES` coverage. The next development phase expands curated
validation to deeper dungeon floors; the separate normal-generation promotion
decision remains outstanding.
