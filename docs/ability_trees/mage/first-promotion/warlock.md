# Warlock Ability Tree Implementation Reference

Status: `Finished`

Warlock has 29 nodes across shadow control, draining, offense, curses,
corruption, and Familiar development. Familiar Bond and curse interactions
feed the mutually exclusive Shadowcaster and Demonologist routes.
[Runtime diagram](warlock.svg).

Curse scaling, familiar state and modifiers, route closure, combat cleanup,
and retained spells are covered by `tests/core/test_warlock_trees.py` and
`tests/core/test_warlock_curses.py`.
