# Deferred Playtest And Specification Gates

These areas need a decision contract in their owner document before
implementation or an expanded playtest campaign. Foundational refactors are
tracked separately in `FOUNDATIONAL_REFACTOR_PLAN.md`.

| Area | Why deferred | Owner document |
| --- | --- | --- |
| Durability, identification, item modification, and rarity changes | Current-save/reset, UI, and economy contracts are not approved. | [`EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md`](../EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md) |
| Multi-enemy normal generation, floor 5, and rosters larger than two | One-or-two-enemy architecture and development pilots exist, but no Pilot 3 pair qualified for ordinary rollout. Floor 5 needs its approved representative matrix and enemy-area-action review; larger rosters need a new layout and action-model contract. | [`MULTI_ENEMY_FUTURE_GATE.md`](../MULTI_ENEMY_FUTURE_GATE.md) |
| Account-wide Bestiary, profiles, achievements, and persistent meta statistics | Profile ownership, storage, migration, and privacy decisions are open. | [`DEVELOPMENT_ROADMAP.md`](../DEVELOPMENT_ROADMAP.md) |
| Broader divine economy and deep class-kit expansions | Manual cadence, readability, preservation, and action-economy evidence is still pending. | [`CLASS_KIT_DESIGN_GATES.md`](../CLASS_KIT_DESIGN_GATES.md) |
| Vesperion/final-battle tuning and deeper Reflection mechanics | Story triggers, failure/retry behavior, and balance targets need a promoted slice. | [`STORY_AND_ENDGAME_DESIGN.md`](../STORY_AND_ENDGAME_DESIGN.md) |
| Final audio replacement, dynamic music, and spatial audio | Asset targets and runtime routing requirements need approval. | [`SOUND_SYSTEM.md`](../SOUND_SYSTEM.md) |

Moving an item out of this file requires a small spec covering scope, state and
save behavior, Pygame and headless behavior, failure handling, and regression
tests.
