# Crusader Ability Tree Implementation Reference

Status: `Finished`

Crusader has 26 nodes across `Melee`, `Spells`, `Healing`, and `Protection`.
Condemnation opens an exclusive two-handed or sword-and-board route while Holy,
healing, and protection branches remain compatible.
[Runtime diagram](crusader.svg).

Style closure, Conviction interactions, marks, typed Holy actions, replacement
nodes, equipment legality, and two-point capstones are covered by
`tests/core/test_paladin_crusader_trees.py` and
`tests/core/test_paladin_vows.py`.
