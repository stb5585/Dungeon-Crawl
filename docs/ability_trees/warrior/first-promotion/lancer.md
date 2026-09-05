# Lancer Ability Tree Implementation Reference

Status: `Finished`

Lancer has 22 nodes across Jump core, assault/guard modifications, polearm
discipline, and unbound attacks. Aerial Tempo and selectable Jump modifiers
define its build; Vigilant Landing and Polearm Excellence gate Dragoon.
[Runtime diagram](lancer.svg).

Modifier ownership, placement, promotion prerequisites, equipment rules, and
combat-only Aerial Tempo are covered by
`tests/core/test_lancer_dragoon_trees.py` and
`tests/core/test_class_ability_mechanics.py`.
