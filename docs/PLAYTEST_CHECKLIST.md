# Playtest Checklist

## Recently Changed

### Dungeon Rendering
- [ ] Enter a dungeon room with side doors or detected Ore Vault doors.
  - Expected: Door/wall surface-slot states render consistently without stale slot overrides from a previous view.
- [ ] Revisit a room after moving through side corridors and backtracking.
  - Expected: Floor, ceiling, and wall textures return to the room's actual tile state instead of showing debug or stale override textures.
- [ ] Enable renderer surface-slot debugging while checking a side corridor.
  - Expected: Debug overlay information corresponds to the visible panel being inspected.
  - Expected: Slot diagnostics identify both default and overridden textures for the panel under inspection.
- [ ] Run renderer diagnostics after moving through several dungeon views.
  - Expected: Projected-surface cache diagnostics report a bounded cache size.
- [ ] Run asset fallback diagnostics with a missing or renamed test asset.
  - Expected: Fallback counts identify the affected asset category without changing dungeon rendering.

### Combat Status Icons
- [ ] Trigger or simulate Blind Rage in combat.
  - Expected: The status row shows a distinct `BRG` icon.
  - Expected: `BRG` is prioritized with other urgent negative combat states before overflow.
- [ ] Stack repeated status effects alongside several other combat states.
  - Expected: Counted status icons keep urgent effects visible first and use stable ordering instead of flickering between turns.
- [ ] Resize the game window or view a crowded combat overlay.
  - Expected: Status icon labels remain clipped to the icon pill instead of spilling into neighboring UI.

### Main Menu
- [ ] Choose Settings from the pygame main menu.
  - Expected: A guarded modal message appears saying the settings menu is coming soon.
  - Expected: The key press used to choose Settings does not immediately dismiss the message.
- [ ] Quit from a pygame session after visiting dungeon or popup-heavy screens.
  - Expected: The game exits cleanly without leaving stale popup backgrounds or hanging the window.
- [ ] Open several popups after moving between town, dungeon, and combat views.
  - Expected: A stale or unavailable popup background falls back cleanly instead of repeating an old scene.
- [ ] Open a yes/no or message confirmation after a screen transition.
  - Expected: The popup draws over a copied background instead of mutating the live screen surface.
- [ ] Level up and open the stat-selection prompt after changing screens.
  - Expected: Level-up overlays use a copied background and do not smear or redraw over the live screen unexpectedly.
- [ ] Open choice, reward, quantity, and code-entry popups after changing screens.
  - Expected: Each popup draws over the current copied view instead of reusing a live or empty background surface.

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
- [ ] Attempt to delete or load invalid save entries such as blank names or folder-like entries.
  - Expected: The game refuses the invalid entry without loading directories, deleting directories, or creating blank-name saves.
- [ ] Validate save names from a debug/menu path before attempting load or delete.
  - Expected: Normal `.save` names pass; blank, absolute, path-bearing, and non-text entries are rejected.
- [ ] Load an older or partially malformed save with tile-state data.
  - Expected: Valid door/chest/boss room states still restore, while malformed tile-state entries are ignored.
- [ ] Attempt to load a corrupted save file.
  - Expected: Loading fails gracefully without deleting or rewriting the corrupted file.

### Quest Log
- [ ] Accept and complete a main quest that grants item rewards.
  - Expected: Quest completion and turned-in state are recorded correctly.

### Statistics
- [ ] Open the Statistics entry from the pygame town menu.
  - Expected: The popup includes steps, stairs, defeats, deaths, flees, encounters survived, and high-water combat stats.
  - Expected: Missing or old save data displays as zeroes instead of crashing.
  - Expected: Encounters survived is never negative, even after old or manually edited save data.

### Developer Tooling
- [ ] Run a focused combat simulator test after analytics changes.
  - Expected: The quick balance helper returns a report object even when no simulations are configured.
- [ ] Generate a compact combat simulator summary payload.
  - Expected: The payload includes totals, win rates, top abilities, top status effects, and outliers without raw per-battle results.
- [ ] Export a combat simulator balance report to JSON.
  - Expected: The file includes total battles, win rates, ability usage, status frequency, outliers, and raw results.
- [ ] Export a battle log JSON file during a debug run or test.
  - Expected: The file is created with metadata, events, and summary sections.
- [ ] Generate a compact battle-log summary during a debug/tooling check.
  - Expected: The payload includes battle metadata and aggregate summary counts without raw event rows.
- [ ] Run an event-bus history check with history disabled.
  - Expected: Subscribers still receive events while history remains empty.
- [ ] Inspect compact event-bus history counts during a debug/test run.
  - Expected: Counts reflect only retained history and remain empty when history is disabled.
- [ ] Inspect compact event-bus subscriber counts during a debug/test run.
  - Expected: Duplicate subscriptions are counted once, and unsubscribed callbacks disappear from the counts.
- [ ] Inspect compact event-bus diagnostics during a debug/test run.
  - Expected: Enabled state, history size/limit, retained event counts, and subscriber counts are visible without raw event rows.
- [ ] Run focused action-queue tests after combat scheduling changes.
  - Expected: Negative delays are treated as instant actions and helper-created actions include debug metadata.
