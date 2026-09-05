# Pathfinder Ability Tree Implementation Reference

Status: `Finished`

Pathfinder has 40 nodes across `Druid`, `Naturalism`, `Ranger`, `Melee`,
`Shaman`, `Elemental`, and `Diviner`. Authored shared-track joins create four
different but level-30-affordable promotion routes.
[Runtime diagram](pathfinder.svg).

Nature typing, shared prerequisites, promotion costs, animal utility,
Geomancy, Control Z, stable IDs, and retention are covered by
`tests/core/test_pathfinder_tree.py`, `tests/core/test_nature_totems.py`, and
`tests/core/test_flat_progression.py`.
