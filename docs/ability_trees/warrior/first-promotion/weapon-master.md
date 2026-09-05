# Weapon Master Ability Tree Implementation Reference

Status: `Finished`

Weapon Master has 33 nodes across `Berserker`, `Grandmaster`, `Dual Wield`,
`Duelist`, and `Weapon Arts`. It deliberately combines asymmetric promotion
routes, a permanent style fork, and eight discipline-gated art chains.
[Runtime diagram](weapon-master.svg).

Weapon Discipline ranks unlock purchases but never grant arts automatically.
Stable art and style IDs, branch closure, equipment rules, and retained entry
nodes are covered by `tests/core/test_weapon_master_tree.py` and
`tests/core/test_grandmaster_discipline.py`.
