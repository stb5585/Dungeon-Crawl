# Sorcerer Ability Tree Implementation Reference

Status: `Finished`

Sorcerer has 29 nodes across elemental spells, modifiers, Arcana, enhancements,
and illusion. Classical Force and Arcane Tradition establish a permanent
specialization that shapes School Affinity and the route to Wizard.
[Runtime diagram](sorcerer.svg).

Specialization closure, carried Mage spells, affinity progression, modifier
payoffs, and promotion paths are covered by `tests/core/test_sorcerer_tree.py`
and `tests/core/test_mage_mechanics.py`.
