# Arcane Trickster Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 12 development nodes costing 30 points across
`Arcane Larceny` and `Misdirection`. [Current diagram](arcane-trickster.svg).

## Point Pressure

Levels 61-100 award 20 progression points against a 30-point graph, providing
67% tier-earned cost coverage. The smaller graph leaves room for permanently
stolen enemy spells in the player's usable kit, while its two- and three-point
nodes keep progression choices consequential.

## Authored Paths

| Path | Node | Cost | Effect |
| --- | --- | ---: | --- |
| Arcane Larceny | Steal Spell II | 2 | Attempts to permanently learn an enemy spell. |
| Arcane Larceny | Master Thief | 3 | Adds 15 points to learning chance and raises its cap to 90%. |
| Arcane Larceny | Arcane Ambush | 2 | Deals 130% weapon damage and accepts charged payoff. |
| Arcane Larceny | Mnemonic Larceny | 3 | A successful permanent theft restores 11 MP. |
| Arcane Larceny | Weaken Mind | 2 | Reduces enemy Magic and Magic Defense. |
| Arcane Larceny | Neural Connection | 3 | Mirrors Weaken Mind's exact reductions as buffs for the same duration. |
| Misdirection | Third Eye | 2 | Applies Intelligence to established avoidance and critical calculations. |
| Misdirection | Vanishing Act | 2 | Spends one Charge for Speed and Defense. |
| Misdirection | Escape Artist | 3 | Strengthens and extends Vanishing Act. |
| Misdirection | False Opening | 2 | Deals weapon damage and lowers Attack and Magic. |
| Misdirection | Misdirection | 3 | Charged damage also lowers enemy Attack and Magic. |
| Misdirection | Grand Larceny | 3 | Raises maximum Stolen Charge from three to four. |

Both columns use the ungated, 65, 70, 75, 80, and 85 level bands. Steal Spell
II, Weaken Mind, and Third Eye retain stable IDs and recognize prior ownership.

## Boundaries And Acceptance

- Reuse permanent spell ownership, combat-only Charge, and the existing
  three-turn Arcane Larceny ring effect.
- Do not replace learned spells or create free Blank Scrolls.
- Show Charge commitment, failure retention, and active deception through HUD,
  logs, spell labels, and descriptions; no mechanic tab is added.
- Ring preservation remains optional and is not assumed by tree balance.
- Focused tests cover permanent-learning odds and refund, Neural Connection,
  both weapon/control actives, charge conversion, cap growth, old ownership,
  cleanup, and the 20-of-30 point envelope.
