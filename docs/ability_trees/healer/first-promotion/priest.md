# Priest Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. The tree contains 22 development nodes costing 22
points across `Prayer`, `Exorcism`, `Grace`, and `Protection`.
[Runtime diagram](priest.svg). After reserving promotion, 12 tier-earned points
buy 54.5% of development cost.

## Implemented Decision

Prayer retains Supplication and Holy II, then adds Dazed or Confused: Holy
damage first attempts a two-turn Stun and, if that fails, may confuse the
target, followed by a +20 Magic node. Exorcism makes Expel Curse available
before Archbishop alongside a +20 Magic Defense node, Dispel, and Berserk.
Grace adds Magical Invigoration, whose Regen-triggered
Magic stacks carry independent durations. Protection retains Mana Shield,
Shell, Cleanse, and Bless.

Seven talents improve deliberate Prayer gain, Supplication healing, warding
and cleansing, Holy disorientation, and Magical Invigoration strength and
duration. Passive Regen ticks remain excluded from Prayer generation.

## Validation Contract

- Any completed discipline endpoint can unlock Archbishop; promotion is row 7.
- Rows use the ungated, 35, 40, 45, 50, and 55 pattern.
- Prayer remains combat-only, capacity four, and action-deduplicated.
- Focused tests cover support generation, passive exclusions, independent
  Invigoration stacks, Supplication riders, curse removal, and point coverage.
