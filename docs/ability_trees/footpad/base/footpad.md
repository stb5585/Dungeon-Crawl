# Footpad Ability Tree Implementation Reference

Status: `Finished`

Footpad has 34 nodes across `Thief`, `Control`, `Assassin`, `Spell Stealer`,
`Defense`, and `Inquisitor`. Each promotion joins an identity track with its
authored shared track, producing four distinct level-30 routes.
[Runtime diagram](footpad.svg).

Tool inventory, stealth, trap, pursuit, scroll, control, route costs, promotion
joins, and stable IDs are covered by `tests/core/test_footpad_tree.py` and
`tests/core/test_flat_progression.py`.
