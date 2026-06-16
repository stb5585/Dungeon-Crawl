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
- Legacy `ElectricSpell` stun messaging now also depends on successful
  `Character.apply_stun()` application, avoiding false “stunned” text during
  post-stun immunity.
- `tests/core/test_status_effect_interactions.py` covers the effect-driven
  and legacy electric Stun immunity paths.
- Status interaction coverage now pins the per-turn ordering for Poison, burn
  DOT, Bleed, and Regen, including final-turn cleanup before the Regen heal is
  evaluated.
- Timed Silence now expires through `Character.effects()` while
  `duration=-1` Silence remains indefinite until cured.
- `Character.handle_defenses()` now reuses the shared Mana Shield absorption
  helper, and coverage pins shield depletion, leftover damage, and the
  "Mana Depleted" status event path.
- Composite weapon-spell follow-ups and related custom effects now call the
  shared Mana Shield/Crusader shield absorption helpers with the current
  attacker/defender contract; Smite coverage pins Mana Shield absorption text
  and mana consumption.
- Reflected data-driven damage spells now update `CombatResult.target` to the
  actual damaged character and retain the original reflector name in
  `extra["reflected_by"]`.
- Representative concrete legacy/YAML comparison coverage now pins shared
  Fire burn behavior between legacy `FireSpell.special_effect()` and
  data-driven `Fireball`.
- Data-driven spell effect-message detection now snapshots effect buckets by
  value, so newly appended bucket entries (for example fire DOT) can generate
  presentation messages.
- Legacy/YAML comparison coverage now also pins ice extra-damage behavior, and
  `DynamicExtraDamageEffect` message templates flow through data-driven spell
  presentation.
- The shared instant `HealSpell.cast()` path now reports and emits actual
  healing after health caps and healing-received modifiers, covering both
  remaining legacy subclasses and YAML `DataDrivenHealSpell` wrappers.
- `HealSpell._apply_instant_healing()` now centralizes instant-heal cap,
  modifier, and event logic for legacy casts plus YAML hybrid and out-of-combat
  heals.
- `DataDrivenHealSpell` cast, hybrid heal, HoT, and out-of-combat heal helpers
  now carry typed signatures around the consolidated healing behavior.
- Data-driven support/status spell `cast()` methods now carry typed signatures,
  with Cleanse coverage pinning default-target presentation.
- Sleep/Prone interaction coverage now pins that Prone recovery waits until
  the tick after Sleep expires.
- `TestYAMLLoading.test_all_yaml_abilities_load_combat_ready` now walks all
  179 YAML ability files and verifies each one can produce a combat-ready
  object.
- Built-in YAML abilities are now audited to ensure none use primitive
  `type: damage` effects; `DamageEffect` remains registered and covered for
  external/custom `EffectFactory` definitions.
- The fixed Batch 1 spell loader test no longer skips missing files; those YAML
  files are required content.

## Follow-Up Work

- Enemy priority coverage now includes redundant target-status skips and
  target-positive-effect Dispel selection.
- Quest coverage now includes item-instance collection quests, partial progress
  before the required total, and no repeated completion message after a quest is
  completed.
- `Player.quests()` now has a typed signature and behavior docstring for enemy,
  item, and relic completion paths.
- Continue extracting shared combat/healing result helpers only where new
  contract coverage exposes duplication or drift.
