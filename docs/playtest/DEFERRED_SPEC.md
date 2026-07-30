# Deferred Playtest And Specification Gates

These areas are intentionally excluded from the current P8 checklist. They
need the decision contract in their owner document before implementation or a
large playtest campaign.

| Area | Why deferred | Owner document |
| --- | --- | --- |
| Durability, identification, item modification, and rarity changes | Save, UI, economy, and old-save contracts are not approved. | [`EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md`](../EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md) |
| Multi-enemy combat and combat-stack architecture | Targeting, action order, AI, balance, and simulator assumptions need a complete spec. | [`COMBAT_BALANCE_DESIGN_GATES.md`](../COMBAT_BALANCE_DESIGN_GATES.md) |
| Account-wide Bestiary, profiles, achievements, and persistent meta statistics | Profile ownership, storage, migration, and privacy decisions are open. | [`DEVELOPMENT_ROADMAP.md`](../DEVELOPMENT_ROADMAP.md) |
| Broader divine economy and deep class-kit expansions | Manual cadence, readability, preservation, and action-economy evidence is still pending. | [`CLASS_KIT_DESIGN_GATES.md`](../CLASS_KIT_DESIGN_GATES.md) |
| Vesperion/final-battle tuning and deeper Reflection mechanics | Story triggers, failure/retry behavior, and balance targets need a promoted slice. | [`STORY_AND_ENDGAME_DESIGN.md`](../STORY_AND_ENDGAME_DESIGN.md) |
| Final audio replacement, dynamic music, and spatial audio | Asset targets and runtime routing requirements need approval. | [`SOUND_SYSTEM.md`](../SOUND_SYSTEM.md) |

Moving an item out of this file requires a small spec covering scope, state and
save behavior, both frontend surfaces, failure behavior, and regression tests.
