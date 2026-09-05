# Thief Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. Breadth: 22 one-point development nodes across four
disciplines, plus the Rogue promotion. [Current diagram](thief.svg).

## Progression Shape

Levels 31-60 award 15 points. Rogue requires one completed discipline and
three promotion points. Fortune and Misfortune now cost six points to complete;
Tools and Escape cost five, leaving six or seven points for cross-training.

| Discipline | Nodes in order |
| --- | --- |
| Fortune | Scavenger's Eye; Read the Room; Gold Toss; +50 HP; Gilt Edge; Fortune Favors the Bold |
| Misfortune | Mug; Hard Lessons; +20 Attack; Turn the Tables; Spiteful Streak; Reversal |
| Tools | Lockpick; Careful Hands; Trap Lore; Pilfering Strike; Master Tools |
| Escape | Cut and Run; Smoke Tactician; Fleet Footed; Lasting Head Start; Clean Getaway |

Turn the Tables is an active full-Misfortune conversion into Attack and
Defense. Pilfering Strike adds a weapon-and-theft action, while Cut and Run
adds combat damage and temporary Speed. Fortune talents improve generation,
risky-action accuracy, and clean-payoff preservation; Misfortune talents
strengthen damage and status conversion. Tool talents improve detection,
durability, and pilfered gold. Escape talents improve Smoke Bomb economy and
allow a trained Thief's successful normal flee roll to beat enemy perception.

## Boundaries And Acceptance

- Reuse combat-only Fortune/Misfortune and current action deduplication.
- Preserve ordinary loot eligibility and unique, ultimate, quest, special, and
  restricted-item exclusions.
- Keep tool durability and Smoke Bomb inventory behavior explicit in messages.
- Use HUD, logs, ability text, loot results, and trap-approach messages; no
  mechanic tab or new persistent state beyond purchased node IDs.
- Focused tests cover all four promotion routes, the seven-point cross-training
  budget, active spenders, loot safety, tool preservation, trap detection,
  cleanup, and stable legacy ability IDs.
