# Shadowcaster Ability Tree Implementation Reference

Status: `Finished`

Shadowcaster has 21 nodes across `Umbral Debt`, deep shadow, veilcraft,
nightmares, and Familiar mastery. Shadow actions build combat-only debt that
can empower effects or fund Shade of Ahool before backlash.
[Runtime diagram](shadowcaster.svg).

Debt gain/spend, backlash, Shade validation, Familiar passives, cleanup, and
ring boundaries are covered by
`tests/core/test_shadowcaster_shade_backlash.py` and
`tests/core/test_dispersed_class_mechanics.py`.
