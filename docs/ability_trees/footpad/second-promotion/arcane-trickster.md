# Arcane Trickster Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 11 development nodes costing 28 points across
`Spell Theft`, `Stolen Spell Mastery`, and `Misdirection`.
[Current diagram](arcane-trickster.svg).

## Point Pressure

Levels 61-100 award 20 progression points against a 28-point graph, providing
71% tier-earned cost coverage. The smaller graph leaves room for permanently
stolen enemy spells in the player's usable kit, while its two- and three-point
nodes keep progression choices consequential.

## Authored Paths

| Path | Node | Cost | Effect |
| --- | --- | ---: | --- |
| Spell Theft | Steal Spell II | 2 | Attempts to permanently learn an enemy spell. |
| Spell Theft | Master Thief | 3 | Adds 15 points to learning chance and raises its cap to 90%. |
| Spell Theft | Arcane Ambush | 2 | Deals 130% weapon damage and accepts charged payoff. |
| Spell Theft | Mnemonic Larceny | 3 | A successful permanent theft restores 11 MP. |
| Stolen Spell Mastery | Neural Connection | 3 | A known Weaken Mind mirrors its exact reductions as buffs for the same duration. |
| Misdirection | Third Eye | 2 | Applies Intelligence to established avoidance and critical calculations. |
| Misdirection | Vanishing Act | 2 | Spends one Charge for Speed and Defense. |
| Misdirection | Escape Artist | 3 | Strengthens and extends Vanishing Act. |
| Misdirection | False Opening | 2 | Deals weapon damage and lowers Attack and Magic. |
| Misdirection | Misdirection | 3 | Charged damage also lowers enemy Attack and Magic. |
| Misdirection | Grand Larceny | 3 | Raises maximum Stolen Charge from three to four. |

The two core columns use the ungated, 65, 70, 75, 80, and 85 level bands.
Neural Connection is an optional level-85 terminal leaf off Steal Spell II.
Weaken Mind must be permanently stolen and is no longer granted by progression.

## Boundaries And Acceptance

- Reuse permanent spell ownership, combat-only Charge, and the existing
  three-turn Arcane Larceny ring effect. The Spell Theft lane name keeps that
  optional ring effect distinct from ordinary progression.
- Do not replace learned spells or create free Blank Scrolls.
- Show Charge commitment, failure retention, and active deception through HUD,
  logs, spell labels, and descriptions; no mechanic tab is added.
- Ring preservation remains optional and is not assumed by tree balance.
- Focused tests cover permanent-learning odds and refund, conditional Neural Connection,
  both weapon/control actives, charge conversion, cap growth, old ownership,
  cleanup, and the 20-of-28 point envelope.
