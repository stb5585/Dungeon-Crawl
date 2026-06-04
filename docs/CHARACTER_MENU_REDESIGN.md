# Character Menu Redesign

## Current Status

The modern Pygame Character Menu is implemented in parallel with the legacy menu. The legacy menu remains the default until the modern menu passes acceptance testing and receives explicit approval to replace it.

Opt-in paths:

- Set `DUNGEON_CRAWL_MODERN_CHARACTER_MENU=1` before launching the pygame client.
- Set `use_modern_character_menu = True` on the `PygameGame` or presenter object during debug/test setup.

## Implemented

- Generic tab model with initial `Character` and `Equipment` tabs.
- Character overview with race/sex portrait art, larger right-aligned Name, Race, Class, and Level details, and a wider right-column graphical level-progress bar tucked under Level. XP earned and XP remaining are shown only in the bar label to avoid duplicate summary rows.
- Larger core attributes and focused combat stats, including HP, MP, Attack, Defense, Magic Attack, Magic Defense, Critical, Block, Speed, and Weight. Dual-wielding shows main/offhand Attack values. Core attribute and combat values are right-aligned for easier scanning.
- Dividers separate identity from Core Attributes and Combat Stats from Weaknesses/Resistances.
- The Character tab uses a 50/50 Character and Combat Stats split so both portrait identity and stat/resistance information have stable space.
- Equipment layout prepared for `Weapon`, `Armor`, `Helmet`, `OffHand`, `Ring`, and `Pendant`.
- Helmet appears as a future UI slot only. Helmet mechanics are not implemented.
- Equipment tab with a spread-out paper-doll slot layout and item names, without an extra layout heading.
- The Character tab intentionally omits the equipment panel to avoid duplicating the Equipment tab.
- Equipment-derived persistent buffs such as Vision are shown inside the Character/Equipment views instead of a separate effects screen.
- The action menu uses `Change Equipment` for the equipment-management popup, keeps `Exit Menu` last, and omits `Quit Game`.
- Resistance presentation grouped into side-by-side weaknesses and resistances with exact values as secondary text. The resistance area reserves a static full-capacity block for the 10 possible resistance keys without truncating entries.
- Town and dungeon routing through the temporary feature flag while preserving the legacy default.

## Assumptions

- `level.exp_to_gain` is treated as experience remaining to the next level; level progress is calculated as `exp / (exp + exp_to_gain)` and labeled as earned XP versus XP to next level. The legacy `"MAX"` sentinel renders as a full bar with a max-level label.
- Existing equipment slots use the current save/runtime keys, including `OffHand`. The modern UI displays the user-facing label without changing persistence.
- Combat-only debuffs and temporary effects are not shown because they are not persistent outside combat.
- Future companion, set-bonus, and reputation systems should use the existing tab/panel structure rather than adding fixed screen positions.

## Acceptance Gate

Before making the modern menu default:

- Complete the Character Menu Redesign section in `docs/PLAYTEST_CHECKLIST.md`.
- Verify legacy Character Menu behavior remains available and unchanged.
- Review the modern menu at small and large pygame window sizes.
- Decide whether the first default modern release needs equipment comparison in the Equipment tab.
