# Rogue Ability Tree Implementation Reference

Status: `Finished`

Tier: terminal. Breadth: 28 development nodes costing 30 points across four
disciplines. [Current diagram](rogue.svg). The 20 points earned from levels
61-100 cover 67% of the graph. Only All In and Impossible Job cost two points;
every other node costs one.

## Authored Disciplines

| Discipline | Nodes in order |
| --- | --- |
| Loaded Odds | Finders Keepers; Stacked Odds; Slot Machine; Rigged Reels; Triple Strike; All In; The House Always Wins |
| Comebacks | Sneak Attack; Cruel Reversal; Zephyrstrike; Snake Eyes; Cheat Death; Cheat Fate; Break the Jinx |
| Cunning | Keen Eye; Master Lockpick; Disarm Traps; Sure Hands; Dirty Trick; Deep Pockets; Impossible Job |
| Escape | Take It On the Run; Cut and Run; Smoke Screen; Slippery Customer; Evasive Guard; Smoke and Mirrors; Gone Before Dawn |

All In actively spends both luck meters on one amplified weapon attack. Snake
Eyes spends Misfortune on damage and Blind, and Dirty Trick trades raw weapon
damage for paired Attack and Defense penalties. Loaded Odds improves Fortune
accuracy, Slot Machine scaling, and clean preservation. Comebacks improves
Misfortune conversion and makes Cheat Death more reliable with a shorter Jinx.

Disarm Traps becomes available after Master Lockpick. Find Traps stops the
first approach; approaching the warned tile again makes a DEX- and depth-based
disarm attempt. A Lockpick Kit, Master Lockpick, Sure Hands, and Impossible Job
improve the attempt. Failure triggers the trap, while Impossible Job limits a
failed attempt to half severity. Take It On the Run performs a theft during a
successful Smoke Screen escape; Gone Before Dawn doubles stolen gold.

## Boundaries And Acceptance

- Reuse Fortune, Misfortune, Jinx, Cheat Death, Loaded Dice, tool durability,
  trap state, and ordinary enemy inventory. Node ownership is the only new
  persistent state.
- Preserve Slot Machine result identities, loot exclusions, one luck claim per
  action, and one Cheat Death attempt per combat.
- Show resource spends, preservation, theft, disarm odds/results, and Jinx in
  existing HUD/log/ability/exploration surfaces; no mechanic tab.
- Exclude heist storage, inventory destruction, forced jackpots, global loot
  rewrites, and automatic trap removal without detection.
- Focused regression coverage verifies the 28-node, 20-of-30 point envelope,
  active luck spenders, fatal interception, Loaded Dice, safe loot, trap
  disarming, Smoke Screen theft, cleanup, and save-compatible ownership.
