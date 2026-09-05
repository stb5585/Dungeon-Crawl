# Grandmaster of Arms Ability Tree Implementation Reference

Status: `Finished`

Grandmaster of Arms has 30 nodes: all eight three-rank Weapon Art chains plus
its independent dual-wield mastery route. Weapon Discipline ranks gate each
purchase and rank-10 arts replace their lower forms.
[Runtime diagram](grandmaster-of-arms.svg).

All 24 art forms, rank gates, replacement, Weapon Swap, adaptive mastery, and
stable ownership are covered by `tests/core/test_grandmaster_discipline.py`
and `tests/core/test_weapon_master_tree.py`.
