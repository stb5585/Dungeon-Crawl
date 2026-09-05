# Wizard Ability Tree Implementation Reference

Status: `Finished`

Wizard has 28 nodes across master elemental spells/modifiers, Grand Arcana,
control, and spatial illusion. School Affinity, six school modifiers, and the
quest-awarded ultimate coexist without replacing learned Sorcerer spells.
[Runtime diagram](wizard.svg).

Affinity thresholds, streak behavior, modifiers, spell ownership, and diagram
layout are covered by `tests/core/test_wizard_tree.py` and
`tests/core/test_wizard_school_streak.py`.
