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
  - Expected: Per-slot state identifies whether the texture came from defaults, scene overrides, or manual overrides.
- [ ] Run renderer diagnostics after moving through several dungeon views.
  - Expected: Projected-surface cache diagnostics report bounded cache size, remaining capacity, and full/not-full state.
- [ ] Run asset fallback diagnostics with a missing or renamed test asset.
  - Expected: Fallback counts identify the affected asset category without changing dungeon rendering.
  - Expected: Fallback key lists identify the affected texture, special-tile, or enemy asset names by category.
- [ ] Inspect aggregate texture diagnostics after entering and leaving several rooms.
  - Expected: Loaded state, fallback counts/totals, cache size/limit/capacity, and override counts are visible in one diagnostic payload.

### Combat Status Icons
- [ ] Trigger or simulate Blind Rage in combat.
  - Expected: The status row shows a distinct `BRG` icon.
  - Expected: `BRG` is prioritized with other urgent negative combat states before overflow.
- [ ] Cast Enfeeble against a target with extremely low attack/defense.
  - Expected: Zero-value attack/defense changes are not reported and do not appear as green status icons.
  - Expected: Combat view and dungeon HUD both suppress active stat effects whose value is exactly zero.
- [ ] Stack repeated status effects alongside several other combat states.
  - Expected: Counted status icons keep urgent effects visible first and use stable ordering instead of flickering between turns.
- [ ] Resize the game window or view a crowded combat overlay.
  - Expected: Status icon labels remain clipped to the icon pill instead of spilling into neighboring UI.
- [ ] Inspect combat status layout diagnostics with many active effects.
  - Expected: Visible, hidden, overflow, urgent-visible, capacity, and row counts match the status row shown on screen.
  - Expected: Overflow state and hidden urgent-status count make it clear whether high-priority effects were hidden.
  - Expected: Positive, negative, and neutral visible/hidden counts match the rendered icon mix.
  - Expected: Visible/hidden label lists identify exactly which status pills were shown or compacted.
  - Expected: Stat-effect icon filtering diagnostics identify active zero-value effects that were suppressed before rendering.

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
  - Expected: Level-up and stat-selection prompts accept the first fresh key once no key is held, even without a KEYUP event.
- [ ] Open choice, reward, quantity, and code-entry popups after changing screens.
  - Expected: Each popup draws over the current copied view instead of reusing a live or empty background surface.
  - Expected: Confirmation, reward, quantity, and code-entry popups all wait for the same buffered-key release rule before accepting input.
  - Expected: If no keys are currently held, the next fresh key press is accepted even if no synthetic KEYUP event arrives first.
- [ ] Enter combat or a character/shop selector after a previous key-driven transition.
  - Expected: The first fresh action key is accepted once no key is physically held, even if the loop never receives a KEYUP event.
- [ ] Move through main, town, load-game, shop-selection, race, class, and location menus after a prior key press.
  - Expected: Guarded navigation still blocks buffered held keys but accepts the next fresh key without waiting for a KEYUP event that may never arrive.
- [ ] Open the in-dungeon popup menu after a key-driven transition.
  - Expected: The menu ignores a still-held buffered key but accepts the first fresh selection key once no key is physically held.

### Quest Rewards
- [ ] Turn in "The Butcher" quest at the tavern after defeating the Minotaur.
  - Expected: The reward message grants 2 Old Keys.
  - Expected: The inventory shows 2 more Old Keys than before turn-in.
  - Expected: The quest-manager turn-in path records the quest as turned in after granting the keys.
- [ ] Turn in "A Bad Dream" after locating Joffrey.
  - Expected: The reward message grants 3 Old Keys.
  - Expected: The inventory shows 3 more Old Keys than before turn-in.
  - Expected: The quest-manager turn-in path records the quest as turned in after granting the keys.

## Regression Areas

### Locked Doors
- [ ] Try opening a locked dungeon door with at least one Old Key.
  - Expected: The door opens and consumes one Old Key.
  - Expected: The key-use prompt accepts the first fresh confirmation/cancel key after stale input clears.
- [ ] Try opening a locked dungeon door with no Old Keys or lockpick option.
  - Expected: The door stays locked and shows the missing-key prompt.

### Save/Load
- [ ] Save after receiving Old Keys, quit, and reload.
  - Expected: The Old Key count persists.
  - Expected: Multi-key quest rewards survive a SaveManager round trip.
- [ ] Open the Load Game menu after a failed or interrupted save attempt.
  - Expected: Only real `.save` files appear; temporary leftovers and directories are hidden.
- [ ] Attempt to delete or load invalid save entries such as blank names or folder-like entries.
  - Expected: The game refuses the invalid entry without loading directories, deleting directories, or creating blank-name saves.
- [ ] Validate save names from a debug/menu path before attempting load or delete.
  - Expected: Normal `.save` names pass; blank, absolute, path-bearing, and non-text entries are rejected.
- [ ] Inspect save-file metadata for a normal save, missing save, directory entry, and temp save.
  - Expected: Validity, file/directory state, existence, size, and tmp-vs-normal location are reported without loading the save.
  - Expected: Expected extension and extension-match state are visible for normal and tmp save paths.
  - Expected: Empty files are flagged directly in individual save metadata.
- [ ] Inspect visible-save metadata from the load-game path.
  - Expected: Metadata appears in the same order as the load menu and excludes temporary leftovers and directories.
  - Expected: Summary diagnostics report visible save count, total size, and largest visible save without opening the save payload.
  - Expected: Loadable entries and visible filename lists match the load menu.
  - Expected: Summary diagnostics include loadable and empty-save counts.
- [ ] Inspect save-directory diagnostics after creating a normal save, a `.tmp` leftover, a `.save` directory, and an unrelated file.
  - Expected: Visible saves, temp leftovers, directory entries, and ignored entries are counted separately.
  - Expected: Hidden-entry filename lists identify temp leftovers, directory-like saves, and ignored files.
  - Expected: Hidden-entry totals match temp leftovers plus directory-like saves plus ignored files.
- [ ] Load an older or partially malformed save with tile-state data.
  - Expected: Valid door/chest/boss room states still restore, while malformed tile-state entries are ignored.
  - Expected: Tile-state diagnostics count valid entries, malformed positions, malformed state payloads, and positions absent from the loaded world.
  - Expected: Tile-state diagnostics identify restorable attribute counts and any unknown legacy/custom attribute keys.
- [ ] Attempt to load a corrupted save file.
  - Expected: Loading fails gracefully without deleting or rewriting the corrupted file.

### Quest Log
- [ ] Accept and complete a main quest that grants item rewards.
  - Expected: Quest completion and turned-in state are recorded correctly.

### Statistics
- [ ] Open the Statistics entry from the pygame town menu.
  - Expected: The popup includes steps, stairs, defeats, deaths, flees, encounters survived, and high-water combat stats.
  - Expected: Combat outcomes and total activity derive from the existing counters.
  - Expected: Exploration actions and combat survival rate derive from existing counters without requiring a new save format.
  - Expected: Missing or old save data displays as zeroes instead of crashing.
  - Expected: Encounters survived is never negative, even after old or manually edited save data.
  - Expected: Negative legacy/manual counters are displayed as zeroes before derived totals are calculated.

### Developer Tooling
- [ ] Run sound/music asset diagnostics for expected combat, town, and menu audio.
  - Expected: Present sound/music files report available paths, while missing placeholder content is reported without crashing or playing audio.
  - Expected: Default diagnostics include the runtime's combat, town, shop, church, inn, dungeon, and final-combat audio names.
  - Expected: Summary counts report available and missing SFX/music assets.
  - Expected: Summary payloads include available and missing SFX/music name lists.
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
  - Expected: Damage-row counts distinguish all numeric damage events from positive-damage events.
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
  - Expected: Diagnostics expose remaining history capacity plus sorted retained-history and subscriber event-type lists.
- [ ] Run focused action-queue tests after combat scheduling changes.
  - Expected: Negative delays are treated as instant actions and helper-created actions include debug metadata.
