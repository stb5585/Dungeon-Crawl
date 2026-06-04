# Character Menu Redesign

## Current Status

The modern Pygame Character Menu is implemented in parallel with the legacy menu. The legacy menu remains the default until the modern menu passes acceptance testing and receives explicit approval to replace it.

Opt-in paths:

- Set `DUNGEON_CRAWL_MODERN_CHARACTER_MENU=1` before launching the pygame client.
- Set `use_modern_character_menu = True` on the `PygameGame` or presenter object during debug/test setup.

## Implemented

- Generic tab model with initial `Character` and `Equipment` tabs.
- Character overview with portrait placeholder, level details, and graphical level-progress bar. XP earned and XP remaining are shown only in the bar label to avoid duplicate summary rows.
- Core attributes and focused combat stats, including HP, MP, Attack, Defense, Magic Attack, Magic Defense, Critical, Block, Speed, and Weight.
- Equipment layout prepared for `Weapon`, `Armor`, `Helmet`, `OffHand`, `Ring`, and `Pendant`.
- Helmet appears as a future UI slot only. Helmet mechanics are not implemented.
- Equipment tab with a paper-doll slot layout, item names, richer item descriptions, and summarized bonuses.
- The Character tab intentionally omits the equipment panel to avoid duplicating the Equipment tab.
- Equipment-derived persistent buffs such as Vision are shown inside the Character/Equipment views instead of a separate effects screen.
- The action menu uses `Change Equipment` for the equipment-management popup, keeps `Exit Menu` last, and omits `Quit Game`.
- Resistance presentation grouped into weaknesses and resistances with exact values as secondary text.
- Town and dungeon routing through the temporary feature flag while preserving the legacy default.

## Assumptions

- `level.exp_to_gain` is treated as experience remaining to the next level; level progress is calculated as `exp / (exp + exp_to_gain)` and labeled as earned XP versus XP to next level.
- Existing equipment slots use the current save/runtime keys, including `OffHand`. The modern UI displays the user-facing label without changing persistence.
- Combat-only debuffs and temporary effects are not shown because they are not persistent outside combat.
- Future portrait, companion, set-bonus, and reputation systems should use the existing tab/panel structure rather than adding fixed screen positions.

## Acceptance Gate

Before making the modern menu default:

- Complete the Character Menu Redesign section in `docs/PLAYTEST_CHECKLIST.md`.
- Verify legacy Character Menu behavior remains available and unchanged.
- Review the modern menu at small and large pygame window sizes.
- Decide whether the first default modern release needs equipment comparison in the Equipment tab.
