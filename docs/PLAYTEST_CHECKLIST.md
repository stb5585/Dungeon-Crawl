# Playtest Checklist

## Recently Changed

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

### Quest Log
- [ ] Accept and complete a main quest that grants item rewards.
  - Expected: Quest completion and turned-in state are recorded correctly.

### Developer Tooling
- [ ] Run a focused combat simulator test after analytics changes.
  - Expected: The quick balance helper returns a report object even when no simulations are configured.
- [ ] Export a battle log JSON file during a debug run or test.
  - Expected: The file is created with metadata, events, and summary sections.
- [ ] Run an event-bus history check with history disabled.
  - Expected: Subscribers still receive events while history remains empty.
