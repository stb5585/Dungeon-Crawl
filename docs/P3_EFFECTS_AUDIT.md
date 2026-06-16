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
- Data-driven weapon skills now populate `CombatResult.damage` from the HP
  removed by their weapon strikes, so follow-up effects and presentation code
  can rely on the same result field used by data-driven spells.
- `tests/core/test_ability_result_contracts.py` now pins representative
  result-shape expectations for a damage spell and a multi-strike weapon skill.
- Legacy base `Spell.cast()` and `Skill.use()` now reuse the shared
  `Ability._reset_result()` lifecycle helper, preventing stale reusable
  messages, effect buckets, extra data, or damage/healing fields from leaking
  between old-style ability calls.
- `tests/core/test_ability_result_contracts.py` also covers the legacy base
  result reset contracts.
- `StatusApplyEffect` now delegates Stun application to
  `Character.apply_stun`, keeping YAML/composed status effects aligned with the
  post-stun immunity window used by other stun sources.
- `tests/core/test_status_effect_interactions.py` covers the effect-driven
  Stun immunity path.
- Status interaction coverage now pins the per-turn ordering for Poison, burn
  DOT, Bleed, and Regen, including final-turn cleanup before the Regen heal is
  evaluated.
- Timed Silence now expires through `Character.effects()` while
  `duration=-1` Silence remains indefinite until cured.
- `TestYAMLLoading.test_all_yaml_abilities_load_combat_ready` now walks all
  179 YAML ability files and verifies each one can produce a combat-ready
  object.
- The fixed Batch 1 spell loader test no longer skips missing files; those YAML
  files are required content.

## Follow-Up Work

- Add result-shape contract tests that compare representative concrete legacy
  and YAML abilities where true legacy implementations still exist.
- Enemy priority coverage now includes redundant target-status skips and
  target-positive-effect Dispel selection.
- Quest coverage now includes item-instance collection quests, partial progress
  before the required total, and no repeated completion message after a quest is
  completed.
- `Player.quests()` now has a typed signature and behavior docstring for enemy,
  item, and relic completion paths.
- Audit whether `DamageEffect` should remain registered for external/custom
  ability data, since built-in YAML abilities no longer appear to use
  `type: damage`.
- Extract shared combat/healing result helpers only after the contract tests are
  in place.
- Continue status interaction coverage for Sleep, Prone, and shield/reflect
  interactions.
