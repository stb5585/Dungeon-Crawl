# Warrior Ability Tree Implementation Reference

Status: `Finished`

Warrior is a 30-node base tree across `Arms`, `Vanguard`, `Bulwark`, `Command`,
and independent utility. Its shared trunks lead to Weapon Master, Lancer,
Sentinel, and Paladin while preserving route-specific stat and branch gates.
[Runtime diagram](warrior.svg).

The graph is authoritative in `src/core/progression_manifest.py`. Stable node
IDs, shared prerequisites, Commitment closure, rating values, and promotion
costs are persistent progression API. Coverage lives in
`tests/core/test_warrior_tree_updates.py`, `test_flat_progression.py`, and
`test_ability_tree_diagrams.py`.
