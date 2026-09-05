# Astromancer Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 28 development nodes costing 30 points across four
seven-node disciplines. [Current diagram](astromancer.svg). The 20 terminal-tier
points buy 66.7% of the graph.

## Progression Shape

| Discipline | Active and defining nodes |
| --- | --- |
| Foresight Threads | Foretell; Twist Fate; Threaded Cast; Rewind; Thread Spinner |
| Runic Constellations | Vulcanize; Weaken Mind; Boost; Learn Spell II; Celestial Runes |
| Celestial Force | Wormhole; Triplecast; Volcano; Tephra |
| Lucid Utility | Access Storage; Silent Lucidity |

Thread Spinner grants one extra Thread on its first valid generation each
combat. Celestial Runes adds 15 percentage points to active-sign rune drops.
Tephra makes Volcano scatter Fire debris onto every other living enemy. Access
Storage moves one selected item between storage and inventory outside combat,
charging MP equal to at least one point of item weight. Silent Lucidity allows
only Time and Divination spell casts while Sleep remains active.

## Boundaries And Acceptance

- Foresight Threads remain combat-only with a cap of three. Threaded Cast
  spends before resolution, and Rewind cannot restore spent Threads.
- Rewind still grants at most one Thread per combat and keeps its snapshot
  safety behavior.
- Learn Spell II remains capped at explicitly ranked rank-two enemy spells.
- Active constellation cycling, ring boost floors, and rune persistence retain
  their existing rules.
