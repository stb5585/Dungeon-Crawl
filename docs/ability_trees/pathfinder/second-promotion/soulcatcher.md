# Soulcatcher Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 28 development nodes costing 30 points across four
seven-node disciplines. [Current diagram](soulcatcher.svg). The 20 points from
levels 61-100 buy 66.7% of the graph. Soulstorm and Perfect Surge cost two
points; every other node costs one.

## Progression Shape

| Discipline | Nodes in order |
| --- | --- |
| Soul Dominion | Soul Drain; Gentle Reaping; Soul Rend; Soul Amplifier; Desoul; Death Ward; Soulstorm |
| Essence | Absorb Essence; Discerning Vessel; Vulcanize; Varied Harvest; Essence Shell; Perfect Vessel; Eternal Harvest |
| Ancestral Totem | Totem Surge; Deep Resonance; Ancestral Aegis; Resonant Return; Deep Water; Ancestral Current; Perfect Surge |
| Spirit Warrior | Parry; Spirit Claw; Triple Strike; Haunting Blows; Dispel; True Piercing Strike; Spirit Warrior |

Soul Dominion preserves Soul Drain's one-HP floor while adding healing,
Soul-Totem potency, a Resonance-building weapon action, defensive Soul
attunement, and the active Soulstorm spender. Essence turns the existing
Absorb Essence and harvested-type record into staged Magic, Armor, weapon, and
Magic Defense bonuses, improved proc reliability, and MP recovery.

Ancestral Totem expands the existing loop with a fourth Resonance slot, an
active defensive/healing conversion, Water absorption mastery, occasional
stack preservation and extra generation, and a stronger deliberate Surge.
Spirit Warrior supplies a complete martial-support route and lets inherited
Bad Omens criticals build dread faster.

## Boundaries And Acceptance

- Soul Drain and Soulstorm remain nonlethal and do not bypass Death or boss
  immunity.
- Reuse combat-only Totem Resonance and the existing harvested-type record; no
  new soul currency or autonomous pet turns are introduced.
- Use the Totems tab, aspect/spirit popup, HUD, descriptions, and combat logs.
- Focused tests cover the 20-of-30 budget, all four paths, dread, Resonance
  spending/caps, harvest thresholds, spirit actions, nonlethal pulses, ring
  scaling, cleanup, and save/load.
