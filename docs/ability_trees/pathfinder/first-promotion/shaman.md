# Shaman Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. Breadth: 19 development nodes costing 21 points across
four disciplines, plus the Soulcatcher promotion. [Current diagram](shaman.svg).

## Progression Shape

Levels 31-60 award 15 points. Soulcatcher requires one completed discipline
and three promotion points. The remaining 12 points buy 57.1% of the
development graph. Spirit Animal and Bad Omens cost two points because each
unlocks a class-defining mechanic; all other nodes cost one.

| Discipline | Nodes in order |
| --- | --- |
| Totems | Hydration; Resonant Ward; Spirit Mend; Totem Surge |
| Elements | Elemental Strike; Resist Fire; Resist Water; Resist Earth; Resist Wind; Astral Shift |
| Spirit Warrior | Spirit Animal; Piercing Strike; Maelstrom Weapon; True Strike; Double Strike |
| Bad Omens (cross-training) | Hex; Hexcraft; Omen Ward; Bad Omens |

Totem is learned automatically on promotion to Shaman and is not a tree
purchase. The Totems tab and its popup expose both elemental-aspect and spirit-animal
selection. Bear, Wolf, Owl, Panther, Eagle, Turtle, Toad, and Snake provide
different four-turn combat blessings; the selection round-trips through saves.
Bad Omens records combat-only dread when an enemy misses or the Shaman lands a
critical hit. At three stacks the omen resolves as a two-turn Stun and clears
that enemy's dread.

## Deferred: Skinwalker

Skinwalker is deliberately not purchasable yet. Its specification crosses the
combat-outcome, exploration-body, save, second-death, and town-ritual
lifecycles. The current defeat routine immediately resets combat and performs
resurrection in town, so adding only a death interception would leave an
unsaved or stranded spirit body. Implement this as one cohesive feature after
alternate-player-body traversal and ritual recovery have an approved contract.

## Boundaries And Acceptance

- Preserve communion unlocks, strongest-known-spell pulses, staff synergy,
  Water absorption, and one Resonance claim per action.
- Forced Totem Surge cannot generate Resonance from itself.
- Spirit-animal choice is persistent; dread and Resonance remain combat-only.
- Promotion accepts the Totems, Elements, or Spirit Warrior endpoint. Bad
  Omens remains an optional cross-training branch rather than a shortcut.
- Focused tests cover point pressure, promotion joins, animal blessings, dread
  realization, Totem behavior, save/load, and stable legacy abilities.
