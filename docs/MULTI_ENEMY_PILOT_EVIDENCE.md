# Multi-Enemy Curated Pilot Evidence

## Scope

The pilot remains development-only. It does not enable random paired
encounters or authorize rosters larger than two.

| Key | Floor | Authored roster |
|---|---:|---|
| `carrion_crawl` | 1 | Giant Centipede, Zombie |
| `wing_and_mattock` | 1 | Giant Hornet, Twisted Dwarf |
| `fang_and_spear` | 2 | Gnoll, Giant Snake |

Use `DUNGEON_FORCE_ENCOUNTER=<key>` on an ordinary random-encounter floor.
`DUNGEON_FORCE_ENEMY` and `DUNGEON_FORCE_ENCOUNTER` are mutually exclusive.

## Automated Evidence

Canonical pair command:

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

The curated encounters remain development-only. Automated stability passed,
but the balance bands and manual-play requirement did not. These results do
not authorize stat, cost, area-damage, normal-generation, or roster-size
changes.
