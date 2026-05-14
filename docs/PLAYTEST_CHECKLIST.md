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
  - Expected: Manual and scene-driven override counts are distinguishable while debugging.
- [ ] Run renderer diagnostics after moving through several dungeon views.
  - Expected: Projected-surface cache diagnostics report bounded cache size, remaining capacity, and full/not-full state.
- [ ] Run asset fallback diagnostics with a missing or renamed test asset.
  - Expected: Fallback counts identify the affected asset category without changing dungeon rendering.
- [ ] Inspect aggregate texture diagnostics after entering and leaving several rooms.
  - Expected: Loaded state, fallback counts/totals, cache size/limit/capacity, and override counts are visible in one diagnostic payload.

### Combat Status Icons
- [ ] Trigger or simulate Blind Rage in combat.
  - Expected: The status row shows a distinct `BRG` icon.
  - Expected: `BRG` is prioritized with other urgent negative combat states before overflow.
- [ ] Cast Enfeeble against a target with extremely low attack/defense.
  - Expected: Zero-value attack/defense changes are not reported and do not appear as green status icons.
- [ ] Stack repeated status effects alongside several other combat states.
  - Expected: Counted status icons keep urgent effects visible first and use stable ordering instead of flickering between turns.
- [ ] Resize the game window or view a crowded combat overlay.
  - Expected: Status icon labels remain clipped to the icon pill instead of spilling into neighboring UI.
- [ ] Inspect combat status layout diagnostics with many active effects.
  - Expected: Visible, hidden, overflow, urgent-visible, capacity, and row counts match the status row shown on screen.
  - Expected: Overflow state and hidden urgent-status count make it clear whether high-priority effects were hidden.

### Main Menu
- [ ] Choose Settings from the pygame main menu.
  - Expected: A guarded modal message appears saying the settings menu is coming soon.
  - Expected: The key press used to choose Settings does not immediately dismiss the message.
- [ ] Quit from a pygame session after visiting dungeon or popup-heavy screens.
  - Expected: The game exits cleanly without leaving stale popup backgrounds or hanging the window.
- [ ] Open several popups after moving between town, dungeon, and combat views.
  - Expected: A stale or unavailable popup background falls back cleanly instead of repeating an old scene.
  - Expected: Popup-background diagnostics expose provider presence and fallback count after stale-provider fallbacks.
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
- [ ] Inspect save-file metadata for a normal save, missing save, directory entry, and temp save.
  - Expected: Validity, file/directory state, existence, size, and tmp-vs-normal location are reported without loading the save.
- [ ] Inspect visible-save metadata from the load-game path.
  - Expected: Metadata appears in the same order as the load menu and excludes temporary leftovers and directories.
  - Expected: Summary diagnostics report visible save count, total size, and largest visible save without opening the save payload.
  - Expected: Loadable entries and visible filename lists match the load menu.
- [ ] Inspect save-directory diagnostics after creating a normal save, a `.tmp` leftover, a `.save` directory, and an unrelated file.
  - Expected: Visible saves, temp leftovers, directory entries, and ignored entries are counted separately.
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
  - Expected: Combat outcomes and total activity derive from the existing counters.
  - Expected: Missing or old save data displays as zeroes instead of crashing.
  - Expected: Encounters survived is never negative, even after old or manually edited save data.
  - Expected: Negative legacy/manual counters are displayed as zeroes before derived totals are calculated.

### Developer Tooling
- [ ] Run sound/music asset diagnostics for expected combat, town, and menu audio.
  - Expected: Present sound/music files report available paths, while missing placeholder content is reported without crashing or playing audio.
  - Expected: Default diagnostics include the runtime's combat, town, shop, church, inn, dungeon, and final-combat audio names.
  - Expected: Summary counts report available and missing SFX/music assets.
- [ ] Run a focused combat simulator test after analytics changes.
  - Expected: The quick balance helper returns a report object even when no simulations are configured.
- [ ] Generate a compact combat simulator summary payload.
  - Expected: The payload includes totals, win rates, top abilities, top status effects, and outliers without raw per-battle results.
- [ ] Export a combat simulator balance report to JSON.
  - Expected: The file includes total battles, win rates, ability usage, status frequency, outliers, and raw results.
- [ ] Export a battle log JSON file during a debug run or test.
  - Expected: The file is created with metadata, events, and summary sections.
- [ ] Generate a compact battle-log summary during a debug/tooling check.
  - Expected: The payload includes battle metadata, event-type counts, flag counts, actor/target counts, and aggregate summary counts without raw event rows.
  - Expected: Positive damage totals are attributed by actor and by target.
- [ ] Run an event-bus history check with history disabled.
  - Expected: Subscribers still receive events while history remains empty.
- [ ] Inspect compact event-bus history counts during a debug/test run.
  - Expected: Counts reflect only retained history and remain empty when history is disabled.
- [ ] Inspect compact event-bus subscriber counts during a debug/test run.
  - Expected: Duplicate subscriptions are counted once, and unsubscribed callbacks disappear from the counts.
- [ ] Inspect compact event-bus diagnostics during a debug/test run.
  - Expected: Enabled state, history size/limit, retained event counts, and subscriber counts are visible without raw event rows.
  - Expected: Diagnostics also expose whether bounded history is full and the total subscriber count.
- [ ] Run focused action-queue tests after combat scheduling changes.
  - Expected: Negative delays are treated as instant actions and helper-created actions include debug metadata.
