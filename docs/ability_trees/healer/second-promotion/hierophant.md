# Hierophant Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 28 development nodes costing 30 points across four
disciplines. [Current diagram](hierophant.svg). The 20 points earned from levels
61-100 cover 67% of the graph. Only Deep Conduit and Gentle Grace cost two
points; every other node costs one.

## Decision

Consecrated Conduit contains Staff Conduit, Conduit Strike, Consecrated Conduit,
Deep Conduit, Holy II, Staff Ward, and Radiant Return. It provides a complete
staff battle-caster path: stronger typed Holy discharge, a larger resulting
ward, and one MP returned per spent Devotion.

Devotional Grace contains Regen II, Gentle Grace, Graceful Intercession,
Greater Intercession, Dispel, Warded Faith, and Abundant Grace. It supports a
guardian-healer who generates two Devotion from meaningful healing, spends a
single stack for healing and a ward, improves held mitigation, and can raise
the visible Devotion cap.

Radiant Office develops a Holy battle-caster through Smite III, shadow
resistance, Devotional Rebuke, Turn Undead II, Cleanse, and Silence. Luminous
Doctrine adds one Devotion to successful Holy pressure. Pastoral Office
provides a defensive-support route through Heal II, Bless, Sanctuary Ward,
Shell, Reflect, and Bastion Prayer. Merciful Ward converts meaningful direct
healing into a two-turn ward on its recipient. Heal III, Holy III, Regen III,
and Resurrection remain exclusive to the Archbishop identity.

| Discipline | Nodes in order |
| --- | --- |
| Consecrated Conduit | Staff Conduit; Conduit Strike; Consecrated Conduit; Deep Conduit; Holy II; Staff Ward; Radiant Return |
| Devotional Grace | Regen II; Gentle Grace; Graceful Intercession; Greater Intercession; Dispel; Warded Faith; Abundant Grace |
| Radiant Office | Smite III; Luminous Doctrine; Resist Shadow; Devotional Rebuke; Turn Undead II; Cleanse; Silence |
| Pastoral Office | Heal II; Bless; Sanctuary Ward; Shell; Reflect; Merciful Ward; Bastion Prayer |

## Boundaries And Acceptance

- Reuse Devotion, queued Conduit state, Staff Conduit equipment rules, and
  current ward state. New persistence is limited to node ownership.
- A validated miss may consume a prepared Conduit exactly as it does now.
- Use HUD/status/log/ability/equipment messages; no mechanic tab.
- Exclude relic economies, new prayer currency, heavy armor, and hammer identity.
- Focused tests cover all four disciplines, staff legality, active partial
  spending, typed mitigation, Holy and healing generation, recipient wards,
  held protection, cap growth, cleanup, ring preservation, and the 28-node,
  20-of-30 point envelope.
