# Templar Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 28 development nodes costing 30 points across four
disciplines. [Current diagram](templar.svg). The 20 points earned from levels
61-100 cover 67% of the graph. Only Reinforced Relic and Ordered Purpose cost
two points; every other node costs one.

## Decision

Relic Discipline develops Relic Aegis through shield blocks, longer protection,
Last Stand, Devotion recovery, and a low-health capstone. Reinforced Relic
improves both shielding and typed Holy counter damage; Enduring Aegis extends
the shield and counter; Last Line grants Devotion when Last Stand begins; and
Unbroken Reliquary strengthens Relic Aegis below half health.

Vanguard is a complete martial route through Charge, Goad, shield and parry
actions, and the Piercing Strike chain. Ordered Blessings develops Smite III,
Regen II, Bless, and Dispel alongside stronger blessings, MP return, and a
Magic Defense rider. Judgment supplies a Holy battle-priest route through
Devotional Rebuke, True Strike, Holy II, Turn Undead II, Cleanse, and Bastion
Prayer.

| Discipline | Nodes in order |
| --- | --- |
| Relic Discipline | Relic Aegis; Reinforced Relic; Shield Block; Enduring Aegis; Last Stand; Last Line; Unbroken Reliquary |
| Vanguard | Charge; Goad; Shield Slam; Parry; Piercing Strike; Double Strike; True Piercing Strike |
| Ordered Blessings | Smite III; Ordered Purpose; Regen II; Bless; Dispel; Liturgical Renewal; Perfect Order |
| Judgment | Devotional Rebuke; Exacting Judgment; True Strike; Holy II; Turn Undead II; Cleanse; Bastion Prayer |

## Boundaries And Acceptance

- Reuse Devotion, blessing rotation, Relic Aegis, and existing equipment
  legality. Purchased nodes are the only new persistent state.
- Preserve one claim per action and typed counter resolution.
- Present readiness and the next blessing in HUD/log/skill text; no new tab.
- Exclude party-threat rules, relic quest expansion, and a divine economy.
- Focused tests cover the 28-node, 20-of-30 point envelope, Relic Aegis scaling
  and duration, Last Stand generation, Ordered Blessing scaling and riders,
  ring preservation, cleanup, and stable ownership.
