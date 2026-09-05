# Troubadour Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 27 development nodes across `Finale` and `Mastery`.
[Current diagram](troubadour.svg).

## Identity

Troubadour retains Bard songs and turns completed performances into stronger
codas or permanent advanced-song repertoire. `Finale` accelerates and shapes
Crescendo spending. `Mastery` improves composition practice, natural finishes,
mastered repertoire costs, exploration cadence, and a non-ring Encore option.
Every node modifies the existing song, Crescendo, coda, practice, repertoire,
or Encore systems.

## Finale

| Node | Effect |
| --- | --- |
| Grand Finale | Spends 8 MP to end the active combat song and resolve its accumulated coda immediately. |
| Masterful Finale | All codas gain one effective Crescendo. |
| Decisive Ending | Reduces Grand Finale to 6 MP. |
| Crescendo Reserve | Raises the Crescendo cap by two. |
| Rolling Crescendo | Maintained turns gain one additional Crescendo. |
| Commanding Stage | Raises active-song strength by 10%. |
| Syncopated Strike | Deals 135% weapon damage and extends the active song on hit. |
| Heroic Finale | Valor codas gain one effective Crescendo. |
| Guardian Finale | Shelter codas gain one effective Crescendo. |
| Reviving Finale | Renewal codas gain one effective Crescendo and cleanse poison at two spent. |
| Riotous Finale | Battle Hymn's controlled Berserk coda lasts one additional turn. |
| Rallying Chorus | Restores HP and raises Attack and Magic. |
| Cutting Encore | Strengthens enemy-stat exploration debuffs by 5 percentage points. |
| Resonant Wave | Deals non-elemental damage and reduces enemy Attack and Magic. |

## Mastery

| Node | Effect |
| --- | --- |
| Composer's Memory | Composition grants two practice XP instead of one. |
| Practiced Ear | Maintained advanced-song turns grant one extra practice XP. |
| Flawless Form | Natural completion grants five practice XP instead of three. |
| Efficient Repertoire | Reduces mastered-song MP costs by two. |
| Repertoire Authority | Raises active-song strength by a further 10%. |
| Learned Encore | Natural completion leaves a 35%-strength beat without requiring the class ring. |
| Long Form | Adds one turn to combat songs. |
| Road Tested | Exploration practice ticks every 16 carried steps instead of 20. |
| Endless Refrain | Adds 20 steps to exploration performances. |
| Lasting Impression | Extends the encounter-rate route coda from 20 to 30 steps. |
| Prismatic Finale | Spends Crescendo on scaling random-element damage. |
| Virtuoso Repertoire | Starting a mastered advanced song immediately gains one Crescendo. |
| Countermelody | Raises a ward scaled by current Crescendo without spending it. |

## Cadence And Boundaries

The baseline mastery gate remains 18 practice XP plus three clean finishes.
Practice talents accelerate XP but never bypass clean completion. Grand Finale
uses the current song and Crescendo rather than adding a second finisher state.
Learned Encore supplies a modest normal talent; an awakened Troubadour ring can
still provide its stronger existing Encore behavior.

The tree preserves MP costs unless Efficient Repertoire is owned, one active
song, matching-instrument composition, reduced route codas, and the existing
save shape. No Maestro ranks, quest sheets, autonomous party turns, or new
persistent payloads are introduced.

Regression coverage lives in `tests/core/test_bard_troubadour_trees.py` and the
existing class-kit suites. It covers graph breadth, Grand Finale, practice and
clean-finish cadence, repertoire costs, codas, route effects, Encore, and
serialization compatibility.
