# P3 Effects Audit

Last updated: 2026-06-19

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

## DOT And Effect Icon Audit

- DOT effect buckets:
  - `status_effects["Poison"]`: poison DOT, shown as `PSN` / `poison.png`.
  - `physical_effects["Bleed"]`: bleed DOT, shown as `RND` / `bleed.png`.
  - `magic_effects["DOT"]` with `source == "Burn"`: fire burn DOT, shown as `BRN` / `burn.png`.
  - `magic_effects["DOT"]` with other sources such as `Acid`, `Corruption`, or `Slot Machine`: generic DOT, shown as `DOT` / `dot.png`.
- Ability DOT applicators:
  - Burn/generic DOT: `Firebolt`, `Fireball`, `Firestorm`, `Scorch`, `Molten Rock`, `Volcano`, `Hellfire`, `Corruption`, `Acid Spit`, `Eruption`, and `Slot Machine`.
  - Poison DOT: `Poison Breath`, `Poison Strike`, `Hex`, `Lick`, and `Slot Machine`.
  - Bleed DOT: `Mortal Strike`, `Mortal Strike 2`, `Jump` with the `Rend` modification, and `Slot Machine`.
  - Indirect DOT: `Cataclysm` can invoke DOT-applying spells from the caster spellbook.
- Weapon/natural-weapon DOT applicators found outside the ability data layer:
  - Bleed: `Excalibur`, `Jarnbjorn`, `Claw3`, `Bear Claw`, `Cerberus Claws`, and `Tentacle`.
  - Poison: `Stinger`, `Pincers`, and `Viper Bite`.
  - Burn: `Elemental Blade` when its selected element is Fire.
- Active HUD labels still using text fallback because no PNG asset exists:
  - `HAN` / `Hangover`
  - `RF`, `RI`, `RE`, `RW`, `RTH`, `RWI` / elemental resistance buffs
- Newly wired effect icon assets:
  - `AST` / `Astral Shift`
  - `DUP` / `Mirror Image` / `Duplicates` fallback icon mapping
  - `ICE` / `Ice Block`
  - `MSH` / `Mana Shield`
  - `RFL` / magic-spell `Reflect`
  - `RFM` / Totem melee reflect secondary
  - `SPD` / `Speed` stat effects and Totem speed secondary

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
- Passive placeholder power-up hooks now also reuse
  `Ability._reset_result()`, preserving their interim effect markers while
  clearing stale reusable result state.
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
- Data-driven weapon/custom spell constructors and `cast()` methods now carry
  typed signatures around the Smite/Turn Undead wrapper contracts.
- Data-driven charging, magic-missile, Jump, and movement wrapper entry points
  now carry typed signatures around their existing flexible call contracts.
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
- `random_enemy()` now returns the selected catalog enemy by default, while
  explicit `set_random_enemy_override()` / `clear_random_enemy_override()`
  helpers preserve targeted debug encounters for ability playtesting.
- `DUNGEON_FORCE_ENEMY` now feeds the same random enemy override path, allowing
  debug launch scripts to force targeted encounters without code edits.
- Enemy combat-item selection now recognizes the live `Elixir` subtype for
  mixed health/mana recovery while keeping `Both` as a compatibility alias.
- `Character.handle_defenses()` and `Character.damage_reduction()` are now
  documented and typed as active shared defense contracts for legacy spells,
  YAML abilities, and composite effects rather than planned stubs.

## Closure Notes

- Enemy priority coverage now includes redundant target-status skips and
  target-positive-effect Dispel selection.
- Quest coverage now includes item-instance collection quests, partial progress
  before the required total, and no repeated completion message after a quest is
  completed.
- Class progression coverage now pins promotion spellbook transitions plus
  `Job` helmet/accessory equip defaults after typing those helper surfaces.
- `Player.quests()` now has a typed signature and behavior docstring for enemy,
  item, and relic completion paths.
- Base legacy ability entry points now carry typed signatures for optional
  targets and flexible kwargs, matching the result lifecycle contracts covered
  in `tests/core/test_ability_result_contracts.py`.
- Remaining consumable/stat/status potion and Sanctuary scroll overrides now
  carry typed `use()` signatures matching the base item call contract.
- Loot helper annotations now reflect that `random_item()` returns an item
  class/factory from the rarity cache rather than an instantiated item.
- Enemy catalog helpers now carry typed contracts around random enemy override
  factories, fixed resistance maps, and helper-built spellbooks.
- `Character` now carries focused type aliases and attribute annotations for
  effect maps, inventories, ability books, and combat result tuple contracts.
- A focused search found no explicit `pytest.mark.skip` / `xfail` tests left to
  convert for P3.
- Passive Power Up final gameplay effects, item TODOs, and content-expansion
  placeholders are deferred to P4; their current reusable-result contracts are
  covered, so they are not P3 blockers.
- Future shared combat/healing helper extraction should stay evidence-driven:
  extract only where new contract coverage exposes duplication or drift.
