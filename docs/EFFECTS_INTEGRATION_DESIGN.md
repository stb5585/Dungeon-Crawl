# Effects Integration & Abilities Refactor — Design Document

**Focus Area 3 from [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)**
**Status: Design Phase**

---

## 1. Current State Analysis

### 1.1 The Three Disconnected Systems

```
                     ┌─────────────────────────┐
                     │ abilities.py (7,571 LOC) │
                     │ ~215 ability classes     │
                     │ Inline damage/heal/status│
                     │ Returns: str             │
                     └─────────┬───────────────┘
                               │ (no connection)
         ┌─────────────────────┼─────────────────────┐
         │                     │                      │
┌────────▼────────┐  ┌────────▼────────┐   ┌────────▼────────┐
│ effects/ (20+   │  │ ability_loader  │   │ YAML (18 files) │
│ composable types│  │ EffectFactory   │   │ Only used for   │
│ Never executed  │  │ AbilityFactory  │   │ config loading  │
│ in combat       │  │ → SimpleAbility │   │ (charge_time,   │
│                 │  │ (no cast/use)   │   │  description)   │
└─────────────────┘  └─────────────────┘   └─────────────────┘
```

### 1.2 What Each System Does

| System | LOC | Purpose | Gap |
|--------|-----|---------|-----|
| `abilities.py` | 7,571 | All combat abilities, inline logic | Returns `str`, not `CombatResult`; no use of effects system |
| `effects/` | ~400 | 20+ composable effect types | Never called from combat; `apply()` uses `CombatResult` that abilities don't populate |
| `ability_loader.py` | 401 | Loads YAML → `SimpleAbility` | `SimpleAbility` has no `cast()`/`use()` — unusable in combat |
| YAML abilities | 18 files | Declarative ability definitions | Only 4 abilities read YAML, and only for config (cost, charge_time) |

### 1.3 Return Type Inconsistency

```python
# Base classes DECLARE CombatResult returns:
class Skill:
    def use(self, user, target, **kwargs) -> CombatResult: ...
class Spell:
    def cast(self, user, target, **kwargs) -> CombatResult: ...

# But ALL subclasses ACTUALLY return str:
class PiercingStrike(Offensive):
    def use(self, user, target, cover=False) -> str:
        return use_str  # ← string, not CombatResult

class Attack(Spell):
    def cast(self, caster, target, ...) -> str:
        return cast_message  # ← string, not CombatResult

# Battle engine wraps everything in str() just in case:
message += str(spell.cast(self.attacker, target=self.defender))
message += str(skill.use(self.attacker, target=self.defender))
```

### 1.4 How Combat Currently Works (Attack.cast pipeline)

```
1. Deduct mana (unless special/familiar)
2. Check immunities (Ice Block, tunnel)
3. Check reflect
4. Calculate spell_mod = caster.check_mod("magic", enemy=target)
5. Roll dodge (target.dodge_chance) and hit (caster.hit_chance)
6. If not dodged:
   a. Roll crit (1 in self.crit → 2x multiplier)
   b. Base damage = dmg_mod * spell_mod * crit_per
   c. handle_defenses() → Mana Shield absorption
   d. damage_reduction() → elemental resistance
   e. Class bonuses (Archbishop Holy +25%)
   f. Absorption/heal if damage < 0
   g. Variance: damage *= random(0.9, 1.1)
   h. CON save: target.con//2 vs caster.intel*crit → half damage
   i. Apply damage to target.health
   j. Call special_effect() → subtype-specific secondary (burn, chill, etc.)
   k. Counterspell check
   l. Wizard mana regen on Power Up
7. Return cast_message (str)
```

---

## 2. Design Goals

1. **Bridge** the effects system into actual combat execution
2. **No breakage** — existing hand-coded abilities remain unchanged; migration is opt-in
3. **Consistent returns** — new abilities return `CombatResult` with both structured data AND display messages
4. **YAML → combat-ready** — the loader produces real `Spell`/`Skill` subclass instances
5. **Incremental** — can migrate abilities one-by-one or in batches

---

## 3. Proposed Architecture

### 3.1 After Integration

```
                        ┌─────────────────────────┐
                        │  abilities.py (existing) │
                        │  ~200 hand-coded classes │
                        │  Returns: str (unchanged)│
                        └─────────────────────────┘
                                    +
  ┌────────────────────────────────────────────────────────┐
  │              NEW: data_driven_abilities.py              │
  │  DataDrivenSpell(Spell)     DataDrivenSkill(Skill)     │
  │  - Executes Effect pipeline in cast()/use()            │
  │  - Replicates Attack.cast damage pipeline              │
  │  - Returns CombatResult with .message field            │
  │  - Falls back to traditional str for UI compatibility  │
  └────────────────────┬───────────────────────────────────┘
                       │ uses
         ┌─────────────┼──────────────┐
         │             │              │
┌────────▼────────┐ ┌──▼──────────┐ ┌▼─────────────┐
│ effects/ (20+   │ │ YAML (18+)  │ │ ability_loader│
│ composable types│ │ Declarative │ │ → produces    │
│ Executed during │ │ ability defs│ │ DataDriven*   │
│ cast()/use()    │ │             │ │ instances     │
└─────────────────┘ └─────────────┘ └───────────────┘
```

### 3.2 CombatResult Enhancement

Add a `message` field to `CombatResult`:

```python
@dataclass
class CombatResult:
    action: str = ""
    actor: Any = None
    target: Any = None
    hit: bool = True
    crit: bool = False
    dodge: bool = False
    block: bool = False
    block_amount: int = 0
    damage: int = 0
    healing: int = 0
    effects_applied: dict = field(default_factory=...)
    extra: dict = field(default_factory=dict)
    message: str = ""  # ← NEW: display text for UI
```

**`__str__` returns `self.message`**, so `str(result)` works transparently with the existing battle engine code that does `message += str(spell.cast(...))`.

### 3.3 DataDrivenSpell Design

```python
class DataDrivenSpell(Spell):
    """A spell whose behavior is defined by composed Effect objects + YAML config."""
    
    def __init__(self, name, description, cost, dmg_mod, crit, subtyp, effects, ...):
        super().__init__(name, description)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.crit = crit
        self.subtyp = subtyp
        self._effects = effects  # list[Effect] from EffectFactory
        
    def cast(self, caster, target=None, cover=False, special=False, fam=False) -> CombatResult:
        """
        Replicates the Attack.cast() pipeline but delegates secondary effects
        to the composed Effect objects.
        """
        self._ensure_result()
        result = self.result
        result.actor = caster
        result.target = target
        msg = ""
        
        # 1. Mana cost
        if not (special or fam or ...):
            caster.mana.current -= self.cost
            
        # 2. Immunity checks (Ice Block, tunnel)
        # 3. Reflect check
        # 4. Dodge/hit rolls (same as Attack.cast)
        # 5. Crit roll
        # 6. Base damage = dmg_mod * spell_mod * crit_per
        # 7. handle_defenses + damage_reduction
        # 8. Variance + CON save
        # 9. Apply damage
        
        # 10. Execute composed effects (replaces special_effect)
        for effect in self._effects:
            effect.apply(caster, target, result)
        
        # 11. Build message from result
        result.message = msg
        return result
    
    def __str__(self):
        # Display formatting (same as parent Ability.__str__)
        ...
```

**Key insight**: The core damage pipeline (steps 1-9) is shared across ALL Attack spells. Only `special_effect()` differs per spell subtype. `DataDrivenSpell.cast()` replaces the `special_effect` call with the effects pipeline.

### 3.4 DataDrivenSkill Design

```python
class DataDrivenSkill(Skill):
    """A skill whose behavior is defined by composed Effect objects."""
    
    def __init__(self, name, description, cost, weapon, dmg_mod, effects, ...):
        super().__init__(name, description)
        self.cost = cost
        self.weapon = weapon
        self.dmg_mod = dmg_mod
        self._effects = effects
        
    def use(self, user, target=None, cover=False, **kwargs) -> CombatResult:
        self._ensure_result()
        result = self.result
        result.actor = user
        result.target = target
        msg = ""
        
        user.mana.current -= self.cost
        if self.weapon:
            use_str, hit, crit = user.weapon_damage(target, cover=cover, dmg_mod=self.dmg_mod)
            msg += use_str
            
        # Execute effects
        for effect in self._effects:
            effect.apply(user, target, result)
        
        result.message = msg
        return result
```

### 3.5 AbilityFactory Upgrade

Currently produces `SimpleAbility` (useless). Will produce `DataDrivenSpell` or `DataDrivenSkill`:

```python
class AbilityFactory:
    @staticmethod
    def create_from_dict(ability_data: dict) -> Ability:
        effects = [EffectFactory.create(e) for e in ability_data.get('effects', [])]
        typ = ability_data.get('type', 'Skill')
        
        if typ == 'Spell':
            return DataDrivenSpell(
                name=ability_data['name'],
                description=ability_data.get('description', ''),
                cost=ability_data.get('cost', 0),
                dmg_mod=ability_data.get('damage_mod', 1.0),
                crit=ability_data.get('crit', 5),
                subtyp=ability_data.get('subtype', 'Non-elemental'),
                effects=effects,
                ...
            )
        elif typ in ('Skill', 'Attack'):
            return DataDrivenSkill(...)
```

### 3.6 EffectFactory Extensions Needed

Currently supports 8 types. Missing types to add:

| Type | Effect Class | YAML key |
|------|-------------|----------|
| Speed buff/debuff | `SpeedBuffEffect` / `SpeedDebuffEffect` | `speed_buff` / `speed_debuff` |
| Regen | `RegenEffect` | `regen` |
| Lifesteal | `LifestealEffect` | `lifesteal` |
| Shield | `ShieldEffect` | `shield` |
| Reflect | `ReflectDamageEffect` | `reflect` |
| Dispel | `DispelEffect` | `dispel` |
| Resistance | `ResistanceEffect` | `resistance` |
| Multi-stat | `MultiStatBuffEffect` | `multi_buff` |
| Scaling | `ScalingEffect` | `scaling` |
| Conditional | `ConditionalEffect` | `conditional` |

---

## 4. Migration Strategy

### 4.1 Compatibility Layer

The battle engine currently does:
```python
message += str(spell.cast(self.attacker, target=self.defender))
```

Since `CombatResult.__str__` returns `self.message`, both old (str-returning) and new (CombatResult-returning) abilities work transparently. **No battle engine changes needed.**

### 4.2 Migration Batches

**Batch 1 — Simple Offensive Spells** (~15 abilities)
These use `Attack.cast()` with only a `special_effect()` override:

| Spell | special_effect | Effect Equivalent |
|-------|---------------|------------------|
| Firebolt / Fireball / Firestorm | Burns (DOT) | `ChanceEffect(DamageOverTimeEffect(...))` |
| Scorch / MoltenRock / Volcano | Burns (DOT) | Same pattern, different values |
| Ice Lance / Icicle / IceBlizzard | Extra chill damage | `ChanceEffect(DamageEffect(...))` |
| Shock / Lightning / Electrocution | Stun chance | `ChanceEffect(StatusEffect("Stun", ...))` |
| Meteor | No secondary | Just `DamageEffect` |
| Ultima | No secondary | Just `DamageEffect` |
| MagicMissile / MM2 / MM3 | No secondary | Just `DamageEffect` |

**Why these first**: They all share the exact same `Attack.cast()` pipeline. The only difference is `special_effect()`, which maps directly to composed effects.

**Batch 2 — Healing & Support Spells** (~15 abilities)
Heal, Regen, Bless, Boost, Shell, Reflect, Cleanse, WindSpeed, etc.

**Batch 3 — Status & Death Spells** (~15 abilities)
Hex, Sleep, Doom, Desoul, Petrify, Disintegrate, etc.

**Batch 4 — Weapon Skills** (~20 abilities)
PiercingStrike, TrueStrike, ShieldSlam, DoubleStrike, etc.

**Remaining** — Complex/unique abilities stay hand-coded:
Jump (with modifications system), Slot Machine, Blackjack, Transform, Summon, etc.

### 4.3 Per-Ability Migration Process

1. Create YAML file in `src/core/data/abilities/`
2. Add entry that maps ability name → YAML file path
3. Existing Python class becomes **deprecated** (but still works)
4. Tests validate YAML version produces same outcomes as Python version

---

## 5. File Changes Summary

| File | Action |
|------|--------|
| `src/core/combat/combat_result.py` | Add `message: str = ""` field, add `__str__` method |
| `src/core/data/data_driven_abilities.py` | **NEW** — `DataDrivenSpell`, `DataDrivenSkill` |
| `src/core/data/ability_loader.py` | Replace `SimpleAbility` with `DataDrivenSpell`/`DataDrivenSkill` production; extend `EffectFactory` |
| `src/core/data/abilities/*.yaml` | New YAML files for migrated abilities |
| `tests/test_data_driven_abilities.py` | **NEW** — tests for the pipeline |
| `src/core/abilities.py` | No changes initially (existing classes untouched) |
| `src/core/combat/battle_engine.py` | No changes needed (`str()` wrapping handles both return types) |

---

## 6. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| YAML abilities behave differently from Python originals | Side-by-side comparison tests; keep Python versions as fallback |
| `CombatResult.message` breaks existing code | Default `""` + `__str__` returns `message` — backward compatible |
| Effects don't account for all edge cases (reflect, counterspell, etc.) | DataDrivenSpell replicates the full Attack.cast pipeline; effects only handle post-damage secondary effects |
| Save file compatibility | DataDrivenSpell/Skill have same attributes as their parents (Spell/Skill) |

---

## 7. Success Criteria

1. ✅ `CombatResult` has `message` field, `str(result)` works
2. ✅ `DataDrivenSpell.cast()` produces identical combat behavior to `Attack.cast()` + `FireSpell.special_effect()`
3. ✅ `AbilityFactory.create_from_yaml("fireball.yaml")` returns a combat-ready `DataDrivenSpell`
4. ✅ Batch 1 spells work in actual gameplay (curses + pygame)
5. ✅ All existing tests still pass (no regressions)
6. ✅ New tests validate the data-driven pipeline
