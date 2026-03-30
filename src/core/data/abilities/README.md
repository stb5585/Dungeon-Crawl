# Ability YAML Definitions

This directory contains **179 YAML files** defining every active ability in the game. Each file is loaded at runtime by `ability_loader.py` and instantiated as one of **12 DataDriven classes** from `data_driven_abilities.py`. The original Python classes in `abilities.py` are thin `__new__` wrappers that delegate to the YAML loader.

## Quick Reference — Ability Types

| YAML `type:` | DataDriven Class | Count | Description |
|---|---|---:|---|
| `Skill` | `DataDrivenSkill` | 77 | Physical/weapon abilities, fallback for unknown types |
| `Spell` | `DataDrivenSpell` | 42 | Offensive magic (elemental, arcane) |
| `Support` | `DataDrivenSupportSpell` | 14 | Buff/utility spells (Bless, Protect, Shell, etc.) |
| `Status` | `DataDrivenStatusSpell` | 14 | Debuff/status-inflicting spells (Doom, Blind, etc.) |
| `StatusSkill` | `DataDrivenStatusSkill` | 7 | Physical-stat-based status infliction (Disarm, Goad) |
| `Heal` | `DataDrivenHealSpell` | 7 | Healing spells (Heal, Cure, Raise, etc.) |
| `CustomSpell` | `DataDrivenCustomSpell` | 4 | Abilities with unique execution logic (Disintegrate, etc.) |
| `WeaponSpell` | `DataDrivenWeaponSpell` | 3 | Hybrid weapon+spell attacks (Smite, Dispel Slash) |
| `MagicMissile` | `DataDrivenMagicMissileSpell` | 3 | Multi-projectile spells with configurable missile count |
| `ChargingSkill` | `DataDrivenChargingSkill` | 7 | Multi-turn charge abilities (Charge, Crushing Blow, Shadow Strike, Dragon Breath ×3) |
| `Movement` | `DataDrivenMovementSpell` | 2 | Non-combat world-state abilities (Sanctuary, Teleport) |
| `JumpSkill` | `DataDrivenJumpSkill` | 1 | Jump with full modification system (13 mods) |

## YAML Format

### Required Fields

Every ability YAML must include:

```yaml
name: Ability Name
type: Spell           # See type table above
subtype: Fire         # Category for elemental/thematic grouping
description: >-
  Description text shown to the player.
cost: 10              # Mana cost (0 if none)
```

### Common Optional Fields

```yaml
damage_mod: 2.0         # Damage multiplier
crit: 10                # Critical hit chance bonus
weapon: true            # Uses equipped weapon stats
self_target: true       # Targets caster instead of enemy
ignore_armor: true      # Bypasses target defense
school: Arcane          # Magic school for resistance checks
combat: false           # Cannot be used in combat (Movement spells)
```

### Charging Fields

For multi-turn abilities (`ChargingSkill`, `JumpSkill`, and some `Skill`/`Stealth`/`HolySpell`/`SummonSpell` types):

```yaml
charge_time: 1                # Turns to charge before executing
delay: 1                      # Action queue delay (usually = charge_time)
priority: NORMAL              # Action queue priority: NORMAL | HIGH | LOW
telegraph_message: "..."      # Message shown to Seeker/Inquisitor during charge
prone_while_charging: true    # Makes user vulnerable while charging
```

### Status Fields

For `Status` and `StatusSkill` types:

```yaml
# StatusSkill-specific
status_name: Disarm           # Status effect to apply
physical: true                # Physical (stat-based) vs magical check
actor_stat: strength          # Actor stat for contest
target_use_check_mod: speed   # Target stat for resistance
duration: 3                   # Status duration in turns (-1 = permanent)

# Status spell messages
messages:
  success: "{target} is afflicted!"
  immune: "{target} is immune."
  already: "{target} already has this status."
  resist: "The magic has no effect."
```

### Movement Fields

For `Movement` type abilities:

```yaml
movement_type: sanctuary    # sanctuary | teleport
combat: false               # Teleport cannot be used in combat
```

## Effect System

Effects define what happens when an ability executes. They are composable and can be nested.

### Simple Effects

```yaml
effects:
  # Direct damage
  - type: damage
    base: 100
    scaling: {stat: intelligence, ratio: 1.5}
    element: Fire
    ignore_defense: true

  # Status application
  - type: status_apply
    status_name: Stun
    duration: 3

  # Healing
  - type: heal
    target: self
    amount_percent: 0.3
```

### Stat Contest Wrapper

Many abilities wrap their effect in a stat contest — the effect only triggers if the actor wins the check:

```yaml
effects:
  - type: stat_contest
    actor_stat: intel
    actor_divisor: 2
    target_stat: wisdom
    target_lo_divisor: 4
    target_hi_divisor: 1
    effect:
      type: dynamic_dot
      dot_type: DOT
      duration: 2
      damage_lo_fraction: 0.25
      damage_hi_fraction: 0.5
```

### Compound / Chaining Effects

```yaml
# Multi-buff (Support spells)
- type: multi_buff
  stats: {Attack: 10, Defense: 8}
  duration: 5

# Ability chain — cast another ability as a sub-effect
- type: ability_chain
  ability_name: Heal
  target_self: true
  special: true
  use_method: cast

# Specialized execution effects
- type: charge_execute       # ChargingSkill execution
  dmg_mod: 1.25
  stun_duration: 1

- type: shadow_strike_execute  # Shadow Strike — guaranteed crit + blind
  dmg_mod: 2.0
  blind_chance: 0.6
  blind_duration: 2

- type: jump_execute         # JumpSkill execution
  base_dmg_mod: 2.0

- type: disintegrate         # CustomSpell — instant kill or massive damage
- type: holy_followup        # WeaponSpell — bonus holy damage
```

### Dynamic Effects

These apply runtime-calculated damage, DoTs, or debuffs:

```yaml
- type: dynamic_dot           # Damage over time
- type: dynamic_extra_damage  # Conditional bonus damage
- type: dynamic_multi_debuff  # Multiple debuffs in one effect
- type: dynamic_status_dot    # Status + DoT combo
```

## Examples by Type

### Spell — `fireball.yaml`

```yaml
name: Fireball
type: Spell
subtype: Fire
description: A giant ball of fire that consumes the enemy.
cost: 10
damage_mod: 2.0
crit: 10
school: Arcane
effects:
  - type: stat_contest
    actor_stat: intel
    actor_divisor: 2
    target_stat: wisdom
    effect:
      type: dynamic_dot
      dot_type: DOT
      duration: 2
      damage_lo_fraction: 0.25
      damage_hi_fraction: 0.5
```

### Skill — `backstab.yaml`

```yaml
name: Backstab
type: Skill
subtype: Stealth
description: Strike a stunned opponent in the back, ignoring defense.
cost: 6
weapon: true
damage_mod: 2.0
ignore_armor: true
```

### Status — `doom.yaml`

```yaml
name: Doom
type: Status
subtype: Death
description: "Places a timer on the enemy's life."
cost: 15
messages:
  success: "A timer has been placed on {target}'s life."
  immune: "{target} is immune to death spells."
effects:
  - type: stat_contest
    actor_stat: charisma
    effect:
      type: status_apply
      status_name: Doom
      duration: 5
      skip_if_active: true
```

### ChargingSkill — `charge.yaml`

```yaml
name: Charge
type: ChargingSkill
subtype: Offensive
cost: 10
weapon: true
damage_mod: 1.25
charge_time: 1
telegraph_message: "lowering their head and building momentum"
effects:
  - type: charge_execute
    dmg_mod: 1.25
    stun_duration: 1
priority: NORMAL
delay: 1
```

### Movement — `sanctuary.yaml`

```yaml
name: Sanctuary
type: Movement
subtype: Movement
cost: 100
movement_type: sanctuary
```

## Charging & Telegraph System

Charging abilities take multiple turns to execute:

1. **Turn 1–N**: Ability charges — player is committed, telegraph shown
2. **Turn N+1**: Ability fires with full effect

During charging:
- Character cannot perform other actions
- `prone_while_charging: true` makes the user vulnerable
- Telegraph system reveals intent to Seeker/Inquisitor class

**Standard classes see:**
```
The Dragon is preparing something...
```

**Seeker/Inquisitor sees:**
```
The Dragon is inhaling deeply, flames flickering in its throat!
```

The `telegraph_message` YAML field provides the detailed version.

## Architecture

### Loading Pipeline

```
abilities.py (class Foo)
  → __new__ → ability_loader._load_yaml_ability("foo.yaml")
    → parse YAML → EffectFactory.create_effect(effect_data)
    → AbilityFactory routes type → DataDriven* class
      → returns fully configured ability instance
```

### Key Files

| File | Role |
|---|---|
| `ability_loader.py` | YAML parsing, `EffectFactory`, `AbilityFactory`, type routing |
| `data_driven_abilities.py` | 12 `DataDriven*` classes that implement ability behavior |
| `effects/composite.py` | 93 composable effect types (`Effect` subclasses) |
| `effects/__init__.py` | Public effect exports |
| `abilities.py` | Thin `__new__` wrappers — delegate to YAML loader |

### Adding a New Ability

1. Create `ability_name.yaml` in this directory
2. Set `type:` to match an existing DataDriven class (see type table)
3. Define `effects:` using available effect types from `EffectFactory`
4. Add a wrapper class in `abilities.py` if the ability needs to be referenced by name:
   ```python
   class MyAbility:
       def __new__(cls):
           return _load_yaml_ability("my_ability.yaml", cls_name="MyAbility")
   ```
5. Run tests: `.venv/bin/python -m pytest tests/test_data_driven_abilities.py -v`

For charging abilities, also set `charge_time`, `delay`, `priority`, and `telegraph_message`.

## Future Features

### Cooldowns (Planned)

```yaml
cooldown: 3  # Cannot reuse for 3 turns after execution
```

Candidates: Dim Mak, Arcane Blast, Disintegrate, Detonate, ultimates.

### Companion Ultimate Attacks

11 summon companions each learn an ultimate ability at level 10:

| Summon | Ultimate | Type | Element | Key Mechanic |
|---|---|---|---|---|
| Patagon | Titanic Slam | Skill | Physical | 4× weapon damage + guaranteed stun |
| Dilong | Devour | Skill | Earth | 3 bites at (STR+CON)×1.5 each |
| Agloolik | Absolute Zero | Spell | Ice | 3× intel + 3-turn stun + permanent defense reduction |
| Cacus | Eruption | Spell | Fire | 3.5× (STR+INT) + Burn DOT + self defense buff |
| Fuath | Maelstrom Vortex | Spell | Water | 3× intel + Blind/Silence/Terrify |
| Izulu | Thunderstrike | Spell | Electric | 3× intel + 2 chain hits + stun |
| Hala | Wind Shrapnel | Spell | Wind | 5 hits at 1.2× intel, 25% crit each |
| Grigori | Divine Judgment | Spell | Holy | 3× wisdom (2× vs undead) + heal summoner + cleanse |
| Bardi | Oblivion | Spell | Shadow | 4× intel + 20% instant kill + stat drain |
| Kobalos | Grand Heist | Skill | — | Steal gold + random debuff + Gold Toss finisher |
| Zahhak | Cataclysm | Spell | Non-elemental | Cast 3 random spells + dragon breath + self power up |

## Notes

- All 179 YAML files are loaded and validated at startup
- Effect composition allows complex behavior without Python code changes
- YAML format enables balance tuning without touching source
- The `DataDrivenSkill` fallback handles types without explicit routing
- 613 data-driven ability tests in `tests/test_data_driven_abilities.py`
- Event system emits `SPELL_CAST`/`SKILL_USE` events for analytics and UI
