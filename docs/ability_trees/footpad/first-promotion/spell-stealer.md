# Spell Stealer Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. Breadth: 12 development nodes costing 19 points across
`Spell Theft` and `Stolen Charge`, plus the three-point Arcane Trickster
promotion. [Current diagram](spell-stealer.svg).

## Point Pressure

Levels 31-60 award 15 progression points. Reserving three for promotion leaves
12 tier-earned points for a 19-point development graph: 63% cost coverage.
Carried points can widen a build, but the tier itself cannot buy every node.
The compact graph deliberately prices defining passives at two or three points
instead of adding filler nodes.

## Authored Paths

| Path | Node | Cost | Effect |
| --- | --- | ---: | --- |
| Spell Theft | Steal Spell | 1 | Inscribes an enemy spell onto a Blank Scroll. |
| Spell Theft | Arcane Ledger | 2 | Reduces Steal Spell's MP cost by two. |
| Spell Theft | Wind Speed | 1 | Provides immediate speed support. |
| Spell Theft | Counterfeit Casting | 2 | Stolen-scroll casts gain two Charge instead of one. |
| Spell Theft | Silence | 1 | Shuts down enemy casting. |
| Spell Theft | Perfect Forgery | 2 | Gives successful theft a 25% chance to preserve its Blank Scroll. |
| Stolen Charge | Imbue Weapon | 1 | Adds an existing magical weapon setup. |
| Stolen Charge | Spellbreaker's Cut | 1 | Deals weapon damage and lowers Magic Defense. |
| Stolen Charge | Steal As Well | 1 | Weaves item theft into a damaging spell. |
| Stolen Charge | Borrowed Ward | 2 | Converts all Charge into Defense and Magic Defense. |
| Stolen Charge | Volatile Script | 2 | Raises each Charge's damage conversion from 20% to 25%. |
| Stolen Charge | Controlled Discharge | 3 | Retains one Charge when a committed payoff fails. |

Arcane Trickster requires either Perfect Forgery or Controlled Discharge, so
both complete paths remain valid. Development occupies the ungated, 35, 40,
45, 50, and 55 bands; row 6 is a connector buffer and promotion is row 7.

## Boundaries And Acceptance

- Reuse Blank Scroll inventory and combat-only Stolen Charge; purchased node
  IDs are the only persistent additions.
- Preserve spend-after-validation, aggregate-once action resolution, typed
  Arcane mitigation, and combat cleanup.
- Keep stolen scrolls in the combat Spells picker and Charge in HUD/status; no
  mechanic tab is added.
- Exclude free scroll generation, unrestricted permanent mastery, and a scroll
  economy redesign.
- Focused tests cover point pressure, both promotion routes, theft cost and
  preservation, charged offense and defense, failed discharge retention, and
  stable existing IDs.
