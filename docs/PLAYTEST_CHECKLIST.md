# Playtest Checklist

## Recently Changed

### Dungeon Rendering
- [ ] Enter a dungeon room with side doors or detected Ore Vault doors.
  - Expected: Door/wall surface-slot states render consistently without stale slot overrides from a previous view.

### Combat Status Icons
- [ ] Trigger or simulate Blind Rage in combat.
  - Expected: The status row shows a distinct `BRG` icon.
  - Expected: `BRG` is prioritized with other urgent negative combat states before overflow.

### Main Menu
- [ ] Choose Settings from the pygame main menu.
  - Expected: A guarded modal message appears saying the settings menu is coming soon.
  - Expected: The key press used to choose Settings does not immediately dismiss the message.
- [ ] Quit from a pygame session after visiting dungeon or popup-heavy screens.
  - Expected: The game exits cleanly without leaving stale popup backgrounds or hanging the window.

### Quest Rewards
- [ ] Turn in "The Butcher" quest at the tavern after defeating the Minotaur.
  - Expected: The reward message grants 2 Old Keys.
  - Expected: The inventory shows 2 more Old Keys than before turn-in.
- [ ] Turn in "A Bad Dream" after locating Joffrey.
  - Expected: The reward message grants 3 Old Keys.
  - Expected: The inventory shows 3 more Old Keys than before turn-in.

## Regression Areas

### Locked Doors
- [ ] Try opening a locked dungeon door with at least one Old Key.
  - Expected: The door opens and consumes one Old Key.
- [ ] Try opening a locked dungeon door with no Old Keys or lockpick option.
  - Expected: The door stays locked and shows the missing-key prompt.

### Save/Load
- [ ] Save after receiving Old Keys, quit, and reload.
  - Expected: The Old Key count persists.
- [ ] Open the Load Game menu after a failed or interrupted save attempt.
  - Expected: Only real `.save` files appear; temporary leftovers and directories are hidden.
- [ ] Load an older or partially malformed save with tile-state data.
  - Expected: Valid door/chest/boss room states still restore, while malformed tile-state entries are ignored.

### Quest Log
- [ ] Accept and complete a main quest that grants item rewards.
  - Expected: Quest completion and turned-in state are recorded correctly.

### Statistics
- [ ] Open the Statistics entry from the pygame town menu.
  - Expected: The popup includes steps, stairs, defeats, deaths, flees, encounters survived, and high-water combat stats.
  - Expected: Missing or old save data displays as zeroes instead of crashing.

### Developer Tooling
- [ ] Run a focused combat simulator test after analytics changes.
  - Expected: The quick balance helper returns a report object even when no simulations are configured.
- [ ] Generate a compact combat simulator summary payload.
  - Expected: The payload includes totals, win rates, top abilities, top status effects, and outliers without raw per-battle results.
- [ ] Export a combat simulator balance report to JSON.
  - Expected: The file includes total battles, win rates, ability usage, status frequency, outliers, and raw results.
- [ ] Export a battle log JSON file during a debug run or test.
  - Expected: The file is created with metadata, events, and summary sections.
- [ ] Run an event-bus history check with history disabled.
  - Expected: Subscribers still receive events while history remains empty.
- [ ] Run focused action-queue tests after combat scheduling changes.
  - Expected: Negative delays are treated as instant actions and helper-created actions include debug metadata.
