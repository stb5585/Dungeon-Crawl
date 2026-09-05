# Mage Ability Tree Implementation Reference

Status: `Finished`

Mage has 36 nodes across elemental spells and enhancements, `Arcana`,
`Occultism`, `Conjuration`, and universal utility. Its independent roots and
joined paths lead to Sorcerer, Spellblade, Warlock, and Conjurer.
[Runtime diagram](mage.svg).

Elemental procs, specialization closure, promotion affordability, stable IDs,
and universal retention are covered by `tests/core/test_mage_tree.py`,
`test_mage_mechanics.py`, and `test_flat_progression.py`.
