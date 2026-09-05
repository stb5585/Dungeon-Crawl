# Inquisitor Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. The tree contains 23 development nodes costing 24
points across `Case Journal`, `Judgment`, and `Elemental Wards`.
[Runtime diagram](inquisitor.svg). After reserving the three-point promotion,
12 tier-earned points buy 50% of its development cost.

## Implemented Decision

`Case Journal` is the evidence route: Reveal, Inspect, the two-point Take Notes
Notebook action, Exploit Weakness, Analytical Precision, and Keen Eye. `Judgment` is the direct
combat route through Piercing Strike, Shield Block, anti-magic actions,
Reflect, and True Strike. Either endpoint unlocks Seeker. Enfeeble branches
from the Judgment route into Debilitating Doctrine. The six elemental
resistances now alternate with Warding Studies, Elemental Poise, and Adaptive
Constitution. They remain optional cross-training and never gate promotion.

Revelation remains target-specific combat state with a fixed capacity of two.
Case progress remains hidden, persists by broad enemy type, and exposes only
the `Known Tells`, `Weakness Brief`, `Pattern Lock`, and `Closed Case` ranks.
Take Notes reads those ranks outside combat and cannot create progress.

## Validation Contract

- Preserve every legacy catalog action, universal retention, target cleanup,
  and elemental-resistance behavior.
- Warding Studies extends all six elemental Resist spells from five turns to
  seven; the other ward passives permanently improve the player.
- The two promotion routes use any-of prerequisite semantics and converge only
  at the promotion node.
- Rows follow ungated, 35, 40, 45, 50, and 55; promotion remains row 7.
- Focused coverage verifies promotion routes, Notebook read-only behavior,
  Case milestones, Revelation spend/cleanup, and resistance availability.
- Hidden Cache remains exclusive to the awakened Seeker class ring.
