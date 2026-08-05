# Multi-Enemy Deeper-Floor Pilot

## Status

Status: `Manual acceptance complete; promoted-class balance provisional`

Automated result: `Partial pass (1 accepted, 2 blocked); rerun required after
the ability-tree refactor`

Pilot 3 extends curated two-enemy validation to dungeon floors 3 and 4. It
does not enable random pair generation, change save data, or permit more than
two enemies.

The six required manual runs are complete. Their targeting, presentation,
cleanup, and encounter-flow acceptance is closed. Their combat-length and
difficulty observations are not promotion evidence: current first-promotion
trees vary substantially in completeness, with Weapon Master currently the
most representative. Re-run the promoted-class matrices after the ability-tree
refactor and compare them with the reports below before changing pair balance
or enabling deeper-floor random generation.

## Benchmark Contract

Deeper floors must not be screened against the five base classes at arbitrary
high levels. The pair-tuning tool now accepts an explicit class matrix so the
benchmark can represent the expected promotion tier.

Floor 3 uses level 45 and these representative first promotions:

- Weapon Master
- Sorcerer
- Thief
- Cleric
- Druid

Floor 4 uses the same representatives at level 55. Individual class rates
remain diagnostic; the existing aggregate gates remain authoritative:

- 55–75% player wins;
- 1.25–2.0 times the harder member's singleton actor turns;
- 20–60% median winning-player HP;
- zero invalid intents or max-turn loops.

## Development Candidates

| Key | Floor | Members | Health/offense | Screening purpose |
|---|---:|---|---:|---|
| `rot_and_raptor` | 3 | Ghoul, Golden Eagle | 1.00 / 1.00 | grounded disease pressure plus a flying debuffer |
| `venomous_dream` | 3 | Night Hag, Pit Viper | 0.80 / 1.20 | caster control plus fast martial pressure |
| `burrow_and_bone` | 4 | Antlion, Troll | 0.90 / 0.95 | tunneling state changes plus durable regeneration |

The keys are development-only and work through
`DUNGEON_FORCE_ENCOUNTER=<key>` on their authored floors.

## Automated Evidence

The canonical 100-iteration, five-class matrices produced:

| Key | Battles | Wins | Turns | Winning HP | Invalid/max-turn | Gate |
|---|---:|---:|---:|---:|---:|---|
| `rot_and_raptor` | 500 | 66.0% | 1.86x | 57.6% | 0 / 0 | Pass |
| `venomous_dream` | 500 | 88.0% | 2.53x | 63.4% | 0 / 0 | Blocked: wins, duration, HP |
| `burrow_and_bone` | 500 | 65.4% | 2.45x | 65.2% | 0 / 0 | Blocked: duration, HP |

No candidate produced an invalid intent, max-turn loop, or repeated
non-progress diagnostic. The accepted pair has a wide diagnostic class spread:
Weapon Master 26%, Sorcerer 99%, Thief 99%, Cleric 93%, and Druid 13%.
Individual class rates do not gate acceptance, but its manual runs must include
Weapon Master and Druid.

Reports:

- `reports/balance_baselines/multi_enemy_pilot3_floor3.txt`
- `reports/balance_baselines/multi_enemy_pilot3_floor4.txt`

The two blocked keys remain explicit development overrides for targeted
testing. Their stability does not qualify them for later normal generation.

## Floor 5 Boundary

Floor 5 is deferred from this pilot. Its catalog jumps to endgame-scale
enemies, includes enemy-authored area actions that remain outside the current
multi-enemy contract, and requires a representative second-promotion matrix.
An exploratory level-70 second-promotion run against Earth Myrmidon and
Displacer Beast produced only 4% wins. Local encounter multipliers are not an
appropriate substitute for deciding class lineage coverage and enemy area
behavior.

Before floor 5 candidates are registered, approve:

1. the representative second-promotion lineages or a broader stratified class
   matrix;
2. whether enemy-authored area actions remain single-player-slot effects or
   need structured area resolution;
3. the floor-5 benchmark level and equipment assumptions;
4. whether endgame enemies shared with floor 6 are eligible.

## Validation

Run the floor-specific matrices with 100 iterations per class and seed 1337:

```bash
./.venv/bin/python tools/run_balance_suite.py \
  --tier first --level 45 \
  --classes "Weapon Master" Sorcerer Thief Cleric Druid \
  --encounters rot_and_raptor venomous_dream \
  --iters 100 --seed 1337

./.venv/bin/python tools/run_balance_suite.py \
  --tier first --level 55 \
  --classes "Weapon Master" Sorcerer Thief Cleric Druid \
  --encounters burrow_and_bone \
  --iters 100 --seed 1337
```

## Manual Evidence

Complete six manual battles total: two per pair. The accepted
`rot_and_raptor` runs must use Weapon Master and Druid because those were its
weakest automated classes. At least one run must verify the Golden Eagle's
flying placement, one must exercise Antlion tunneling, and one must verify
Night Hag control/status readability.

For every run, record completion, target/focus behavior, sprite placement,
status and transition readability, cleanup/rewards, perceived duration, and
any defect.

| # | Pair key | Required class/build | Result/duration | Focus and presentation | Mechanics/cleanup/rewards | Defect |
|---:|---|---|---|---|---|---|
| 1 | `rot_and_raptor` | Human Weapon Master, level 45 / 2-handed spec | easy win / 2 turns (True Strike may be too overpowered; used it to one-shot both enemies) | Ghoul is way too big on the screen and needs to be scaled down; Golden Eagle could be higher on the screen but would also need to be slightly smaller | good | no defects |
| 2 | `rot_and_raptor` | Half Elf Druid, level 45 | easy win / 2 turns (used Mortal Strike with a dagger to kill ghoul and Gust to kill Golden Eagle) | same as above | good | no defects |
| 3 | `venomous_dream` | Dwarf Healer, level 45 | easy win / 4 turns (could have been only 2 but I wanted to test Defensive Regen; used Regen, Defend, Holy, Holy to one-shot each of them) | Pit Viper is too large, especially when compared with the Night Hag | good | no defects |
| 4 | `venomous_dream` | Half Giant Monk, level 45 | easy win / 2 turns (Leg Sweep, Leg Sweep) | same as above | good | no defects |
| 5 | `burrow_and_bone` | Half Orc Assassin, level 55 | easy win / 3 turns (Invisibility, Triple Strike, Poison Strike) | Antlion is too large, especially compared with the Troll (which are meant to be very tall) | good | no defects |
| 6 | `burrow_and_bone` | Human Warlock, level 55 | fairly easy win / 5 turns (stunned by Antlion for 2 turns, mana shield, Ice lance (killed Antlion), Shadow Bolt (killed Troll)) | same as above | good | no defects |

Manual status: `Accepted (six of six completed)`

Balance follow-up: `Rebenchmark after the ability-tree refactor. Preserve
these reports as the pre-refactor comparison point; do not infer tuning from
the Druid run because its delayed promotion changed its level and stat-growth
history.`
