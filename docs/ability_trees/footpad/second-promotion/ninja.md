# Ninja Ability Tree Implementation Reference

Status: `Finished`

Ninja has 28 nodes costing 33 points across utility, combat, toxin/death,
stealth, and defense. Point scarcity creates specialization among compatible
Death Mark setup, dedicated finishers, coatings, concealment, and counters.
[Runtime diagram](ninja.svg).

Three-mark capacity, setup/spend actions, toxin mastery, death contests,
No-Trace Opener, cleanup, and target HUD state are covered by
`tests/core/test_ninja_death_mark.py` and `tests/core/test_assassin_toxins.py`.
