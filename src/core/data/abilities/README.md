# Charging Abilities - YAML Definitions

This directory contains YAML definitions for abilities that require charge time (multi-turn abilities).

## Charging Mechanics

Charging abilities take multiple turns to execute:

1. **Turn 1-N**: Ability is "charging" - player is committed, telegraph message shown
2. **Turn N+1**: Ability executes with full effect

During charging:
- Character cannot perform other actions
- Some abilities make character vulnerable (e.g., prone)
- Telegraph system shows charging status to Seeker/Inquisitor

## YAML Format

### Required Fields

```yaml
name: Ability Name
type: Spell | Skill | Attack | PowerUp
subtype: Category (Fire, Physical, etc.)
description: Description text
cost: Mana cost (0 if no cost)
```

### Charging Fields

```yaml
# How many turns to charge before executing
charge_time: 2

# Message shown during telegraph (for Seeker/Inquisitor)
telegraph_message: "descriptive text of what they're doing"

# Priority level for action queue
priority: NORMAL | HIGH | LOW

# Same as charge_time, used by action queue
delay: 2
```

### Effects

Effects are applied when the ability executes (after charging):

```yaml
effects:
  - type: damage
    base: 150
    scaling:
      stat: intelligence
      ratio: 5.0
    element: Fire
  
  - type: status
    status_name: Stun
    duration: 3
    chance: 0.5  # Optional probability
  
  - type: heal
    base: 50
    scaling:
      stat: wisdom
      ratio: 2.0
```

## Available Charging Abilities

### High Charge Time (2 turns)

- **meteor.yaml** - Massive non-elemental damage (Behemoth final attack)
- **dragon_breath.yaml** - Elemental breath weapon (dragons)
- **detonate.yaml** - Self-destruct explosion (Steel Predator, Cyborg, Golem)

### Medium Charge Time (1 turn)

**Player/Enemy Skills:**
- **jump.yaml** - Leap attack with critical damage (user prone while charging)
- **charge.yaml** - Momentum-based stun attack
- **true_strike.yaml** - Guaranteed hit attack
- **true_piercing_strike.yaml** - Guaranteed hit + defense piercing

**Player Power-Ups:**
- **dim_mak.yaml** - Touch of death with instant kill chance (Monk)
- **arcane_blast.yaml** - Expend all mana for massive damage (Mage)
- **shadow_strike.yaml** - Guaranteed critical from shadows (Rogue)

**Enemy Abilities:**
- **summon_allies.yaml** - Summon creatures to fight
- **crushing_blow.yaml** - Devastating physical strike
- **holy_smite.yaml** - Divine smite with healing
- **ultima.yaml** - Void damage spell (Rank 2)
- **disintegrate.yaml** - Instant kill or massive damage spell

## Telegraph Messages

When Seeker/Inquisitor faces an enemy using a charging ability:

**Standard Classes See**:
```
Enemy Turn:
The Dragon is preparing something...
```

**Seeker/Inquisitor See**:
```
Enemy Turn:
The Dragon is inhaling deeply, flames flickering in its throat!
```

The telegraph message comes from the YAML `telegraph_message` field.

## Integration with Enhanced Combat

The EnhancedBattleManager uses these YAML files:

1. **Action Queue**: Abilities with `delay > 0` are scheduled for future turns
2. **Priority System**: Uses `priority` field for turn ordering
3. **Telegraph System**: Uses `telegraph_message` for foresight display
4. **Event Emission**: Emits `SPELL_CAST`/`SKILL_USE` events when ability executes

## Effect Types

### Damage Effects
```yaml
- type: damage
  base: 100
  scaling:
    stat: strength | intelligence | wisdom | dexterity
    ratio: 1.5
  element: Fire | Ice | Lightning | Poison | Physical | Holy | Shadow | Arcane | Non-elemental
  ignore_defense: true  # Optional
```

### Status Effects
```yaml
- type: status
  status_name: Stun | Blind | Sleep | Poison | etc.
  duration: 3
  chance: 0.5  # Optional (0.0-1.0)
```

### Healing Effects
```yaml
- type: heal
  base: 50
  scaling:
    stat: wisdom
    ratio: 2.0
  target: self | other
```

### Conditional Effects
```yaml
- type: conditional
  condition: target_killed | target_is_undead | etc.
  effect:
    type: heal
    amount: max_health
```

### Chance Effects
```yaml
- type: chance
  chance: 0.3
  effect:
    type: status
    status_name: Burn
```

## Usage Example

To add a new charging ability:

1. Create YAML file in this directory
2. Define charge_time and telegraph_message
3. Specify effects that execute after charging
4. Set priority and delay (usually same as charge_time)
5. Test with EnhancedBattleManager

The ability will automatically:
- Show telegraph message to Seeker/Inquisitor
- Queue for execution after charge_time turns
- Execute with full effects when ready
- Emit appropriate events

## Future Features

### Cooldowns (Planned)

Powerful abilities will have cooldown periods after use:

```yaml
cooldown: 3  # Cannot be used again for 3 turns after execution
```

This will prevent spamming of powerful abilities like:
- Dim Mak (touch of death)
- Arcane Blast (all-mana dump)
- Disintegrate (instant kill)
- Detonate (self-destruct)
- Ultimate power-ups

Cooldown tracking will be implemented in Phase 3 with the event system.

## Notes

- Charging abilities are more powerful than instant abilities
- Telegraph system provides counterplay (Seeker/Inquisitor can prepare)
- Event system tracks ability usage for analytics
- YAML format allows easy balancing without code changes
- Abilities marked as `prone_while_charging: true` make user vulnerable during charge
- Some abilities can be interrupted by status effects during charge (future implementation)
