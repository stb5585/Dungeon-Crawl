# Foundational Characterization Baseline

Status: `Captured From master f7a4b25 Before Gameplay Refactor`

This record freezes the inputs that the foundational implementation must
preserve or deliberately replace. It is characterization, not a balance
target: no numeric tuning is authorized from these observations.

## Reproduction

The machine-readable snapshot is
[`reports/foundational/characterization_v0.json`](../reports/foundational/characterization_v0.json).
Regenerate it from the recorded source revision with:

```bash
./.venv/bin/python tools/characterize_foundational_contract.py \
  --samples 10000 --seed 1337 \
  --output reports/foundational/characterization_v0.json
```

The contact sample uses neutral actors without class, race, equipment, status,
proficiency, or explicit accuracy modifiers. Each cell resolves the legacy
independent dodge roll followed by the legacy hit roll. The resolution slice
must extend this matrix with the separately tested modifiers named in the
approved contract before accepting fitted curves.

## Ability Inventory

There are exactly 197 YAML ability files and all 197 filename stems are unique.
No definition has a canonical slug field yet. Legacy `type` values are:

| Value | Count |
| --- | ---: |
| Skill | 81 |
| Spell | 47 |
| Support | 18 |
| Status | 14 |
| Heal | 8 |
| ChargingSkill | 7 |
| StatusSkill | 7 |
| CustomSpell | 5 |
| MagicMissile | 4 |
| WeaponSpell | 3 |
| Movement | 2 |
| JumpSkill | 1 |

Eleven definitions omit `subtype`, 158 omit `school`, 193 omit
`target_scope`, and 195 omit `target_loss_policy`. These omissions and the
mixed semantic values are the legacy allowlist that must shrink to zero as
families migrate.

## Neutral Contact Distribution

Each value is the percentage of 10,000 strikes that made contact. Rows are the
attacker's effective weapon Speed or spell Intelligence; columns are the
defender's effective weapon Speed or spell Wisdom. Spell Charisma is held at
10, so its bounded term is zero.

### Weapon

| Attacker \ Defender | 6 | 10 | 14 | 18 | 22 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 89.36 | 79.40 | 69.58 | 62.70 | 55.72 |
| 10 | 95.82 | 88.41 | 82.05 | 75.88 | 70.46 |
| 14 | 98.60 | 94.29 | 87.76 | 83.23 | 77.99 |
| 18 | 99.35 | 96.62 | 92.59 | 87.82 | 84.81 |
| 22 | 99.72 | 98.03 | 94.90 | 91.83 | 88.65 |

### Spell

| Attacker \ Defender | 6 | 10 | 14 | 18 | 22 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 90.06 | 78.93 | 69.61 | 62.96 | 56.60 |
| 10 | 96.14 | 89.26 | 82.05 | 75.79 | 70.66 |
| 14 | 98.63 | 94.08 | 88.46 | 83.99 | 79.29 |
| 18 | 99.45 | 96.83 | 92.67 | 88.22 | 84.58 |
| 22 | 99.70 | 98.18 | 95.44 | 91.92 | 88.45 |

The legacy implementation uses Speed in both weapon hit and weapon dodge, and
uses Intelligence/Wisdom in analogous independent spell rolls. This snapshot
therefore measures the combined outcome the one-roll resolver must fit, not
either intermediate percentage in isolation.

## Retained Combat Evidence

The last byte-comparable singleton baseline is
[`multi_enemy_slice0_pre_refactor.txt`](../reports/balance_baselines/multi_enemy_slice0_pre_refactor.txt);
the post-pilot report is
[`multi_enemy_slice6_pilot.txt`](../reports/balance_baselines/multi_enemy_slice6_pilot.txt).
These remain the pre-foundation drift references.

Pilot 3's pre-tree, seed-1337 promoted-class evidence remains:

| Encounter | Battles | Wins | Turn ratio | Winning HP | Invalid / max-turn | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `rot_and_raptor` | 500 | 66.0% | 1.86x | 57.6% | 0 / 0 | Pass |
| `venomous_dream` | 500 | 88.0% | 2.53x | 63.4% | 0 / 0 | Blocked |
| `burrow_and_bone` | 500 | 65.4% | 2.45x | 65.2% | 0 / 0 | Blocked |

The detailed reports remain
[`multi_enemy_pilot3_floor3.txt`](../reports/balance_baselines/multi_enemy_pilot3_floor3.txt)
and
[`multi_enemy_pilot3_floor4.txt`](../reports/balance_baselines/multi_enemy_pilot3_floor4.txt).
None of this evidence authorizes normal pair generation under the new timing,
contact, or visibility rules.
