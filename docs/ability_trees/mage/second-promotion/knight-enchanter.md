# Knight Enchanter Ability Tree Implementation Reference

Status: `Finished`

Knight Enchanter has 28 nodes across advanced spells, Assault, Aegis, Spellbind,
and universal techniques. Foundation/Accent spell signatures transform typed
Blade Charges into three distinct releases without a second resource.
[Runtime diagram](knight-enchanter.svg).

Signature grammar, charge consumption, release effects, Weave Memory, Storage
Capacity II, Quick Recharge, and inherited ownership are covered by
`tests/core/test_knight_enchanter_tree.py`.
