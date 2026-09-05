# Monk Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. The tree contains 23 development nodes costing 23
points across `Ki Assault`, `Ki Discipline`, `Centering`, and `Open Hand`.
[Runtime diagram](monk.svg). After reserving the three-point promotion, 12
tier-earned points buy 52.2% of its development cost.

## Implemented Decision

The tree preserves every original martial, healing, purity, guard, and Parry
action. Unarmed Proficiency adds a real fist/empty-hand accuracy and damage
benefit, while Flowing Palm supplies an active attack whose accuracy scales
with stored Ki. Six talents improve zero-Ki recovery, reaction generation,
Chi Heal, Mirror Breath, Centered Guard, and guarded status protection.

Centered Guard spends 8 MP to enter a two-turn defensive stance. Steadfast
Center extends it to three turns, while Guarded Purity adds two turns of
hostile-status immunity. Purging Kata now removes Blind and Berserk only:
Purity of Body already supplies Poison immunity, and Silence prevents normal
ability use rather than providing a viable self-cleanse opportunity.

Master Monk accepts any completed Ki Assault, Ki Discipline, or Centering
route. Open Hand remains optional cross-training. Ki stays combat-only with
fixed capacity, validated one-Ki spends, and one gain per action or reaction.

## Validation Contract

- Rows follow ungated, 35, 40, 45, 50, and 55; promotion remains row 7.
- Preserve fist/staff legality, miss costs, action claims, and combat cleanup.
- Unarmed Proficiency applies only to empty hands and fist weapons.
- Focused tests cover both new abilities, Ki gains and riders, all promotion
  endpoints, point coverage, and generated-diagram parity.
