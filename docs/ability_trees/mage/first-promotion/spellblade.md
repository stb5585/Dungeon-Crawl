# Spellblade Ability Tree Implementation Reference

Status: `Finished`

Spellblade has 20 nodes across weapon, armor, and spell enhancements plus
universal techniques. Typed Arcane and Elemental Blade Charges connect spell
setup to weapon release and gate Knight Enchanter.
[Runtime diagram](spellblade.svg).

Charge gain/caps, Amplify, Counter Charge, equipment-aware passives, promotion
adoption, and level bands are covered by `tests/core/test_spellblade_tree.py`.
