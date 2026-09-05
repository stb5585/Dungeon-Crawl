# Cleric Ability Tree Implementation Reference

Status: `Finished`

Tier: first promotion. Breadth: 26 development nodes costing 26 points across
four promotion disciplines and shared `Shared Ministry`, plus separate
Hierophant and Templar promotions. [Current diagram](cleric.svg).

## Progression Shape

Levels 31-60 award 15 points. Either promotion requires one complete five-node
subpath and three promotion points, leaving seven points for cross-training.
The broader graph makes the two promotion identities distinct while leaving
shared healing and defense choices available to either path.

Hierophant accepts either Pious Bounty or Overflowing Grace. Templar accepts
either Bastion Practice or Consecrated Blows. Both gates use `any`; their
highlighted ancestors remain separate in the promotion UI.

| Discipline | Nodes in order |
| --- | --- |
| Devotion | Sanctuary Ward; Held Faith; Bless; +20 Attack; Lasting Sanctuary; Pious Bounty |
| Sacred Office | Smite; Smite II; Turn Undead II; Cleanse; Overflowing Grace |
| Bulwark | Shield Slam; Shield Block; Bastion Prayer; +20 Defense; Shield Litany; Bastion Practice |
| Judgment | True Strike; Devotional Rebuke; Measured Judgment; Silence; Consecrated Blows |
| Shared Ministry | Sacred Mending; Open Ministry; Hallowed Readiness; Common Purpose |

Held Faith strengthens passive Devotion mitigation. Lasting Sanctuary extends
the ward, while Overflowing Grace raises the visible cap. Bastion Prayer spends
only one stack so a Cleric can retain mitigation; Shield Litany accelerates
block generation. Devotional Rebuke adds typed Holy damage and Consecrated
Blows increases the resulting action-scoped Devotion gain.
Sacred Mending is a direct self-heal. Hallowed Readiness raises Defense and
Magic Defense without spending Devotion; its two shared talents strengthen
these actions and remain useful after either promotion.

## Boundaries And Acceptance

- Reuse combat-only Devotion and current action-claim deduplication. Node IDs
  are the only new persistent state.
- Keep Sanctuary Ward hidden until usable and retain enemy-survival gain rules.
- Use HUD/status/log/skill text; no mechanic tab.
- Exclude a divine currency, relic-loot progression, morality, and party threat.
- Focused tests cover both promotion routes and their remaining cross-training
  budget, held mitigation, partial and full spends, shield generation, typed
  Holy pressure, cleanup, retained ownership, and graph validation.
