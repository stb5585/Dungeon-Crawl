# Archbishop Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. The tree contains 29 development nodes costing 31 points
across `Benediction`, `Great Gospel`, `Intervention`, `Sustaining Grace`, and
`Perfect Supplication`. [Runtime diagram](archbishop.svg). Twenty tier-earned
points buy 64.5% of development cost.

## Implemented Decision

Benediction offers committed improvements to Prayer threshold, duration,
healing, protection, resistance, and MP sustain. Great Gospel develops Holy
III, Silence, Mana Shield II, opening Prayer, and Gospel readiness.
Intervention retains Heal III, Resurrection, and Expel Curse while improving
the existing awakened-ring rescue rather than creating a second rescue.
Sustaining Grace deepens Regen III and Magical Invigoration; Perfect
Supplication improves its healing, ward, cleanse, and Prayer recovery.

All effects reuse Prayer, Gospel state, Regen ticks, and the once-per-combat
Divine Intervention record. No party-targeting or resurrection economy was
introduced.

## Validation Contract

- Rows follow ungated, 65, 70, 75, 80, 85, and 90 without scrolling.
- Prayer capacity remains seven and passive ticks cannot generate it.
- Divine Intervention keeps its awakened/equipped and once-per-combat gates.
- Focused tests cover partial Benediction, intervention chance/healing,
  Supplication, Invigoration, point coverage, and generated-diagram parity.
