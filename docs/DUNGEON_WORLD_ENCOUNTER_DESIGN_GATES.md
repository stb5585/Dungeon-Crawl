# Dungeon, World, And Encounter Design Gates

This document is the durable reference for dungeon, world, and encounter
design gates. It maps the roadmap section into implementation slices, runtime
rules, and validation targets. Completed work should move to `CHANGELOG.md`;
this file should keep active, deferred, or decision-gated direction.

## Status

Status: `Spec Map, V1 Quick Wins Shipped, Relic Text Shared`

The first implementation slice shipped low-risk improvements that do not
require new maps, generated art, or broad content rewrites:

- Relic-specific discovery text.
- Persistent low-health presentation while navigating the dungeon.
- Chest behavior formalized as one-and-done in V1.
- A small random-encounter nudge toward active quest enemy targets.
- Shared relic discovery copy for pygame and core/curses relic-room flows.

Heavier dungeon interaction systems and deeper Realm of Cambion content remain
deferred until their content beats are chosen.

## Dungeon Interaction V1

Decorative dungeon tiles remain traversable visual and message hooks by
default. This preserves existing movement, map authoring, renderer fallback,
and save behavior.

Future interaction mechanics should attach to the existing tile classes:

- `RootGrowthTile`: roots, fungus, or lichen harvesting.
- `FungusPatchTile`: fungus harvesting, poison risk, or cleansing hooks.
- `RubbleTile`: destruction, clearing, or hidden-drop hooks.
- `CrystalClusterTile`: mana interaction, projectile, or resonance hooks.
- `BonePileTile`: inspection or lore-drop hooks.
- `BrokenGearTile`: salvage hooks.

Any new per-tile state must default safely for old saves. Missing state should
behave like the current decorative hook: traversable, readable, and inert.

Hidden passages remain opt-in discovery beats. `Keen Eye` and the Magic Shop
`Oculus` can reveal the suspicious shimmer of nearby unvisited fake walls, but
the wall still behaves as map-authored terrain until the player moves through
or otherwise visits it. Quest-gated false walls, such as the Thieves Guild
trial wall, must remain non-enterable and non-detectable until their quest state
explicitly opens them.

## Chest Policy

V1 chest policy is that opened chests stay open and do not respawn. Existing
authored behavior remains the compatibility baseline:

- locked chest unlock flow;
- Master Key, Key, and Lockpick/Master Lockpick skill behavior, including the
  required limited-durability Lockpick Kit. Lockpick Kits lose durability on
  successful picks and can break early; Dexterity lowers break chance, and
  Master Lockpick lowers it further;
- mimic chance for ordinary chests, currently an explicit bounded chance for
  level 5+ players with higher odds on locked/enhanced chests and a modest Luck
  reduction;
- guaranteed Funhouse Mimic Chest behavior;
- loot popup presentation;
- inventory grant timing;
- empty chest fallback.

Future chest-randomness changes may tune loot tables or mimic odds, but they
must not introduce chest respawns without a separate save/state spec.

## Encounter Bias

Random encounters may receive a small luck/charisma-based nudge toward active
quest enemy targets. The nudge is intentionally soft:

- It only affects random encounters from ordinary cave paths.
- It only selects quest targets that already exist in that floor's random enemy
  catalog.
- It never guarantees the target.
- It does not affect fixed encounters, boss rooms, special events, Funhouse
  encounters, chest mimics, or bounty-board generation.
- Debug random-enemy overrides remain authoritative.

The bias should remain isolated behind a deterministic helper that accepts
player quest state, encounter level, stat access, and an injectable RNG.

## Realm Of Cambion

The current Realm of Cambion compatibility baseline is:

- Nimue entry from the Underground Spring;
- portal pairs and portal flavor;
- anti-magic switch and clue code;
- alarm enemies;
- Merzhin encounter and return handling.

Deeper Cambion rooms, rewards, special tiles, and encounter variants are
deferred until a concrete content beat is chosen. That future beat should define
map scope, reward source, new save flags, and regression tests before code
work starts.

## Relic Discovery Text

Relic rooms use relic-specific discovery text instead of the generic `You found
a relic` message. This is narrative-only. It must not change:

- relic item classes;
- special inventory behavior;
- relic room `read` state;
- health and mana restoration;
- Holy Relics quest completion;
- save shape.

Missing text mappings fall back to a readable generic message.

Runtime relic discovery text is owned by `src/core/map_tiles/rules.py` and reused by
the pygame dungeon manager. Both pygame interaction and core/curses
`RelicRoom.special_text()` use the same mapping and fallback.

## Town Hint Flavor

Town hint work should extend existing systems rather than adding a new town
content engine:

- quest `Help Text`;
- tavern patron comments;
- Sergeant/Barracks quest-lead hints;
- existing special-event dialogue.

Reactive tavern gameplay tips and broader Barracks adventurer flavor remain
content-table additions unless they require new state.

## Additional Improvements

- Create casino/gambling hall/backroom poker/blackjack/etc.
- Remove auto-heal when entering town
  - Add resting at the Tavern/Inn
    - Amount to heal affects the cost
  - Allow resting in the dungeon
    - Bedrolls make it more efficient for healing
    - Resting in general can trigger combat
    - There should be items to reduce encounter chance
      - Firestarter Kit
  - Make status effects last outside of battle
    - Healing status effects requires item, spell, or cleansing from Priest
- Implement traps throughout the dungeon
  - they need to be random so they are not predictable

## Low-Health Navigation

Low-health presentation should persist outside combat while the player is
navigating the dungeon. V1 uses a visual overlay cue at or below 25% HP.

This cue is presentation-only. It must not change movement, random encounter
rates, combat rules, save data, damage, healing, or death handling. It should
coexist with the existing short damage flash used by floor hazards.

## Validation

Focused regression coverage now covers:

- decorative dungeon tiles remain traversable and continue to show intro text;
- opened chests stay open and do not regenerate loot;
- locked chest, ordinary chest mimic chance, Funhouse Mimic Chest, mimic reward,
  and empty chest behavior;
- encounter bias can choose an active quest target with seeded RNG;
- encounter bias falls back when the target is absent or the soft roll fails;
- fixed and special encounters continue to bypass encounter bias;
- shared relic text mappings, generic fallback, inventory grant, `read` state,
  and full HP/MP restore in pygame and core/curses relic-room paths;
- low-health overlay visibility at or below 25% HP and absence above the
  threshold.
