# Berserker Ability Tree Implementation Reference

Status: `Finished`

Berserker has 25 nodes across `Heavy Weapons`, `Two-Weapon Assault`, `Fury`,
`Survival`, and two-handed Weapon Arts. Bloodied Momentum, Battle Scars,
Hemorrhage Thirst, and compatible survival capstones define the terminal build.
[Runtime diagram](berserker.svg).

Momentum timing, scar thresholds, bloodlust crash, weapon disciplines, and art
replacement are covered by `tests/core/test_berserker_bloodied_momentum.py`
and `tests/core/test_warrior_terminal_trees.py`.
