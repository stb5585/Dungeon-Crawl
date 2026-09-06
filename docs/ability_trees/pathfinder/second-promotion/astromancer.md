# Astromancer Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 27 development nodes costing 29 points across four
core disciplines and one optional modifier lane. [Current diagram](astromancer.svg).
The 20 terminal-tier points buy 69% of the graph.

## Progression Shape

| Discipline | Active and defining nodes |
| --- | --- |
| Foresight Threads | Foretell; Twist Fate; Threaded Cast; Rewind; Thread Spinner |
| Runic Constellations | Vulcanize; Weaken Mind; Boost; Learn Spell II; Celestial Runes |
| Celestial Force | Wormhole; Triplecast; Meteor Logic; Celestial Mastery |
| Lucid Utility | Access Storage; Silent Lucidity |
| Witnessed Magic | Tephra |

Thread Spinner grants one extra Thread on its first valid generation each
combat. Celestial Runes adds 15 percentage points to active-sign rune drops.
Celestial Mastery closes the Celestial Force discipline with a Magic bonus;
the separately quest-awarded active ability retains the name Astral Judgment.
Volcano is learned by witnessing its rank-two enemy spell rather than purchased
in this tree. Tephra is a terminal modifier off Learn Spell II and makes a known
Volcano scatter Fire debris onto every other living enemy without blocking
Celestial Force progression. Access Storage moves one selected item between
storage and inventory outside combat, charging MP equal to at least one point
of item weight. Silent Lucidity allows only Time and Divination spell casts
while Sleep remains active.

## Boundaries And Acceptance

- Foresight Threads remain combat-only with a cap of three. Threaded Cast
  spends before resolution, and Rewind cannot restore spent Threads.
- Rewind still grants at most one Thread per combat and keeps its snapshot
  safety behavior.
- Learn Spell II remains capped at explicitly ranked rank-two enemy spells,
  including Volcano. Stupefy is available to both learning ranks.
- Active constellation cycling, ring boost floors, and rune persistence retain
  their existing rules.
