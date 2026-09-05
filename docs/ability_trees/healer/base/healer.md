# Healer Ability Tree Implementation Reference

Status: `Finished`

Healer has 36 nodes across `Bard`, `Support`, `Cleric`, `Healing`, `Priest`,
and `Monk`. Bard, Cleric, and Priest join identity and shared-support tracks;
Monk follows an independent martial route. [Runtime diagram](healer.svg).

Healing/support semantics, joined promotion prerequisites, route affordability,
staff and shield paths, stable IDs, and retention are covered by
`tests/core/test_healer_tree.py` and `tests/core/test_flat_progression.py`.
