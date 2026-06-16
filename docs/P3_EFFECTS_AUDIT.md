# P3 Effects Audit

Last updated: 2026-06-16

## Current Findings

- The small primitive effects in `src/core/effects/` are still reachable through
  `EffectFactory` and low-level tests, even though most live YAML abilities now
  use richer composite effects or the data-driven combat pipeline.
- `DamageEffect` was stale: it used the old `actor.strength` / `target.hp`
  contract while current characters use `actor.stats.strength` and
  `target.health.current`.
- `HealEffect`, `RegenEffect`, `StatusEffect`, and simple buff/resistance
  effects were broadly aligned with current data structures, but their result
  bucket writes were tightened to preserve the `CombatResult` shape when reused
  in smaller harnesses.

## Cleanup Completed

- `DamageEffect` now applies scaled damage through the current character health
  resource, clamps health at zero, records accumulated `CombatResult.damage`,
  and keeps `extra["last_damage"]` available for chained effects.
- `DamageEffect` keeps a fallback for older synthetic objects with `hp`, so
  existing low-level harnesses can still exercise it without a full character.
- `HealEffect` now reports actual applied healing after caps and target healing
  modifiers, matching the newer data-driven healing behavior.
- Type-only imports in the primitive effect modules now reference
  `src.core.character` directly.

## Follow-Up Work

- Add result-shape contract tests that compare representative legacy and YAML
  abilities.
- Audit whether `DamageEffect` should remain registered for external/custom
  ability data, since built-in YAML abilities no longer appear to use
  `type: damage`.
- Extract shared combat/healing result helpers only after the contract tests are
  in place.
