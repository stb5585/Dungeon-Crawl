# Diviner Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. Breadth: 22 development nodes costing 22 points across
four disciplines, plus Astromancer promotion. [Current diagram](diviner.svg).
Witnessed enemy magic supplies Diviner's external repertoire, so the graph
does not add more learned spells. The 12 spendable pre-promotion points buy
54.5% of the graph.

## Progression Shape

| Discipline | Nodes in order |
| --- | --- |
| Rune Lore | Vulcanize; +20 Magic; Enfeeble; Elemental Script; Dispel; Open Sigils |
| Rune Flow | Haste; +20 Magic Defense; Quick Inscription; Runic Focus; Balanced Grid; Doublecast |
| Foresight | Learn Spell; row-2 gap; Pattern Memory; Clear Omen; Witnessed Certainty; Berserk |
| Chronomancy | row-1 gap; Held Moment; +20 Defense; Protected Future; Far Sight; Temporary Stasis |

Any completed discipline opens Astromancer, so rune, witnessed-spell, and time
builds are all valid. Open Sigils raises natural-element rune acquisition by
10 percentage points. Temporary Stasis costs 16 MP, denies two actions, and
pauses every other beneficial and hostile timer on the target while suspended.

## Boundaries And Acceptance

- Learned spells still require successful resolution, explicit authored rank,
  freshness, and a constructible ability class. Diviner remains rank-one only.
- Rune state remains per-save and Runic Boost still consumes a matching rune.
- Stasis uses existing Stun protection and does not tick poison, regeneration,
  Doom, buffs, or debuffs while time is stopped.
- Open Sigils, Doublecast, Berserk, and Temporary Stasis occupy the level-55
  row. Promotion remains on row 7 and accepts any one of those endpoints.
