# Bard Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. Breadth: 26 development nodes plus the Troubadour
promotion across `Performance` and `Composition`. [Current diagram](bard.svg).

## Identity

Bard sustains one combat or exploration song and builds Crescendo by completing
performed turns. `Performance` improves the three stable core songs, their
transition rules, their codas, and immediate attack, defense, and support
actions. `Composition` improves sheets, route songs, and prismatic or untyped
damage casting.

Compose is inherent to Bard and Troubadour rather than a purchased node. The
`Crescendo` Class tab opens its selector and shows which song matches the
equipped instrument. The older per-song composition classes remain
compatibility helpers, not tree nodes.

## Performance

| Node | Effect |
| --- | --- |
| Song of Valor | Starts the stable three-turn offensive song. |
| Sustained Performance | Adds one turn to combat songs. |
| Driving Rhythm | Adds 5% damage to an active Valor effect. |
| Rising Cadence | The first maintained turn gains an extra Crescendo. |
| Coda Craft | Codas resolve with one additional effective Crescendo. |
| Resonant Hall | Raises active-song strength by 10%. |
| Rhythmic Strike | Deals 115% weapon damage and gains Crescendo during a song. |
| Curtain Guard | Raises Defense and Magic Defense without ending the song. |
| Song of Shelter | Starts the stable mitigation song. |
| Sheltering Refrain | Adds 5% mitigation to Shelter. |
| Song of Renewal | Starts the stable HP/MP recovery song. |
| Restorative Harmony | Adds 2% maximum HP/MP to each Renewal pulse. |
| Seamless Transition | Replacing a song retains one Crescendo. |
| Crescendo Reserve | Raises the Crescendo cap from three to four. |
| Inspiring Verse | Instantly raises Attack and Magic without replacing the song. |

## Composition

| Node | Effect |
| --- | --- |
| Battle Arrangement | Extends Battle Hymn and Ode to the Ramparts by one turn. |
| Pointed Satire | Strengthens enemy-stat exploration debuffs by 5 percentage points. |
| Road Song | Adds 20 steps to exploration performances. |
| Gilded Verse | Improves active and lingering Gold Trigger loot multipliers. |
| Copyist | Gives composition a 25% chance to make a second matching sheet. |
| Kaleidoscope | Randomly produces Crimson damage, Azure slow, Emerald recovery, or Violet magic-defense pressure. |
| Vivid Palette | Raises Kaleidoscope potency by 15%; Emerald also restores MP. |
| Dissonant Chord | Deals non-elemental damage and reduces enemy Magic. |
| Elemental Cadence | Kaleidoscope gains one Crescendo while a combat song is active. |
| Prismatic Ray | Deals focused random-element damage with an elemental stat rider. |
| Prismatic Flourish | Extends Azure and Violet riders by one turn. |

## Promotion And Boundaries

Troubadour can be reached through Resonant Hall, Crescendo Reserve, Copyist, or
Prismatic Flourish; the gate uses `any`, keeping both documented paths viable.
The implementation retains one active song, inherent matching-instrument
composition, existing sheet items, existing repertoire state, and conservative route codas.
It does not introduce a second song inventory, quest composition, or a larger
sheet economy.

The 26 development nodes use five visual columns but retain four promotion
routes. Development is confined to rows 0-5 using the standard first-promotion
bands: ungated, 35, 40, 45, 50, and 55. Row 6 is the connector buffer and the
promotion occupies row 7, so the complete graph fits the standard eight-row
panel without scrolling.

Hovering the Troubadour promotion highlights every eligible route, not a
single arbitrarily selected route. All ancestors are purple and the four
direct endpoints use the brighter endpoint color. The detail panel also lists
all four choices under `Path requirement (choose any one)`.

Regression coverage lives in `tests/core/test_bard_troubadour_trees.py` and the
existing class-kit suites. It covers graph shape and stable IDs, the inherent
Compose selector, support, attack, defense, elemental and non-elemental actions,
duration and transition talents, and both Bard/Troubadour cadence rules.
