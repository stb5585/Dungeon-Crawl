# Combat Sprite Animations - Implementation Guide

## Overview

Combat sprites now support smooth, continuous animations that enhance visual feedback during combat:

1. **2-Frame Idle Animation** - Gentle breathing/swaying motion
2. **Vertical Bob** - Continuous subtle up-down movement  
3. **Damage Flash** - Reddish tint when taking damage (fades out)
4. **Death Dissolve** - Scale-down and fade-out when defeated

## Architecture

### SpriteAnimator Class

Located in `src/ui_pygame/gui/combat_view.py`, this class manages all animation state for individual enemies:

```python
class SpriteAnimator:
    """Handles sprite animations (idle, breathe/sway, bob, damage, death)."""
    
    def __init__(self):
        self.frame = 0                # Current frame (0-1 for idle)
        self.animation_time = 0       # Accumulated frame counter
        self.animation_type = None    # Current animation: 'idle', 'damage', 'death', None
        self.bob_offset = 0           # Vertical bob offset in pixels
        self.damage_flash = 0         # 0-1, for red tint fading
        self.is_dead = False          # Marks when death animation completes
        self.death_progress = 0       # 0-1, progress of death animation
```

### CombatView Integration

The `CombatView` class manages a dict of animators (one per enemy instance):

```python
self.sprite_animators = {}  # Key: id(enemy), Value: SpriteAnimator
```

Key methods:
- `update_animations()` - Updates all active animators
- `enemy_take_damage(enemy)` - Triggers damage flash
- `enemy_dies(enemy)` - Triggers death animation
- `_get_sprite_animator(enemy)` - Gets or creates animator for enemy

## Animation Details

### 1. Idle Animation (Breathe/Sway)

**Properties:**
- Cycles through 2 frames every 60 frames (~1 second at 60fps)
- Frame 0: Base position (even counts of 30 frames)
- Frame 1: Sway position (odd counts of 30 frames)

**Implementation:**
```python
self.frame = int((self.animation_time // 30) % 2)
```

**Usage:**
Could be used for:
- Sprite scale variation (0.98x → 1.02x scale during sway)
- Rotation variation (±2° tilt)
- Currently just tracks frame counter for future expansion

### 2. Vertical Bob

**Properties:**
- Continuous sinusoidal motion
- Amplitude: ±8 pixels
- Period: 20 frames (~0.33 seconds at 60fps)
- Applied to Y position during rendering

**Implementation:**
```python
bob_cycle = self.animation_time / 20
self.bob_offset = math.sin(bob_cycle * math.pi * 2) * 8
```

**Applied during render:**
```python
bob_y = center_y + animator.bob_offset
sprite_rect = display_sprite.get_rect(center=(center_x, bob_y))
```

### 3. Damage Flash

**Properties:**
- Triggered when enemy takes damage
- Applies red tint (255, 100, 100)
- Fades over ~20 frames
- Strength: 1.0 → 0.0 (linear decay)

**Implementation:**
```python
def trigger_damage(self):
    self.damage_flash = 1.0

def update(self, dt=1):
    if self.damage_flash > 0:
        self.damage_flash = max(0, self.damage_flash - 0.05)
```

**Tint application:**
```python
overlay = pygame.Surface(surface.get_size())
overlay.fill((255, 100, 100))
overlay.set_alpha(int(strength * 255))
tinted.blit(overlay, (0, 0))
```

### 4. Death Animation (Scale-Down & Dissolve)

**Properties:**
- Duration: 60 frames (~1 second at 60fps)
- Scale: 1.0 → 0.3 (70% reduction)
- Alpha: 1.0 → 0.0 (fade out)
- Linear progression

**Implementation:**
```python
def trigger_death(self):
    self.animation_type = 'death'
    self.animation_time = 0

def update(self, dt=1):
    if self.animation_type == 'death':
        self.death_progress = min(1.0, self.animation_time / 60)
        if self.death_progress >= 1.0:
            self.is_dead = True
```

**Rendering:**
```python
if animator.animation_type == 'death':
    scale = 1.0 - (animator.death_progress * 0.7)
    death_size = int(256 * scale)
    display_sprite = pygame.transform.scale(display_sprite, (death_size, death_size))
    display_sprite.set_alpha(int(255 * (1.0 - animator.death_progress)))
```

## Integration Points

### Triggering Damage Flash

In `combat_manager.py`, when player damage is dealt:

```python
if damage_dealt > 0:
    self.combat_view.enemy_take_damage(enemy)
    self.combat_view.show_damage_flash(False)
```

### Triggering Death Animation

In `combat_manager.py`, when enemy dies:

```python
if not enemy.is_alive():
    self.combat_view.enemy_dies(enemy)
    break
```

### Continuous Updates

In both `render_combat()` and `render_enemy_in_dungeon()`:

```python
def render_combat(self, player_char, enemy, actions, selected_action=0):
    # Update animations every frame
    self.update_animations()
    
    # ... rest of rendering
```

## Customization

To modify animation parameters, edit `SpriteAnimator` class in `combat_view.py`:

### Bob Amplitude/Speed
```python
# Current: ±8 pixels, period of 20 frames
self.bob_offset = math.sin(bob_cycle * math.pi * 2) * 8  # Change 8 for amplitude
                                                         # Change 20 for speed
```

### Damage Flash Color/Duration
```python
# Current: Red tint, 20 frame fade
animator.damage_flash = 1.0  # Triggering
self.damage_flash = max(0, self.damage_flash - 0.05)  # Change 0.05 for duration

# In rendering:
animator.apply_tint(display_sprite, (255, 100, 100), animator.damage_flash)  # Change color
```

### Death Animation Speed/Scale
```python
# Current: 1 second, scale from 1.0 to 0.3
self.death_progress = min(1.0, self.animation_time / 60)  # Change 60 for duration
scale = 1.0 - (animator.death_progress * 0.7)  # Change 0.7 for final scale amount
```

## Future Enhancements

Possible additions to the animation system:

1. **Idle Frame Variations** - Use `self.frame` for scale/rotation changes
2. **Hit Knockback** - Temporary offset on damage
3. **Attack Animation** - Enemy moves forward during attack
4. **Status Effects** - Color pulses for poison, burn, etc.
5. **Hit Spark Effects** - Particle spawns on damage
6. **Boss Patterns** - Special animations for boss fights
7. **Animation Blending** - Smooth transitions between animation states

## Performance Considerations

- Animations are **O(1)** per sprite
- No per-pixel operations except on damage flash
- Sprite scaling happens during render (cached during update)
- Total overhead: ~1-2ms for typical combat scenario (1 visible enemy)

## Testing

To verify animations in-game:

1. **Idle/Bob**: Watch enemy sprite continuously sway gently
2. **Damage Flash**: Deal damage, see red tint fade over ~0.3 seconds
3. **Death**: Kill enemy, see sprite shrink and fade out over ~1 second
4. **Both renders**: Test in combat (first-person) and dungeon (exploration)
