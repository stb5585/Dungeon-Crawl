# Dungeon Crawl Architecture & Migration Plan

## Current State Analysis

### Strengths
- **Data-Driven Foundation**: Effect system (`effects/` module) demonstrates separation of mechanics from implementation
- **Combat Logger**: Already captures battle events for analytics (BattleLogger in `combat.py`)
- **Clean Combat Result System**: `CombatResult` and `CombatResultGroup` provide structured data flow
- **Modular Design**: Separate modules for abilities, characters, items, enemies
- **Dataclasses for Stats**: Clean representation of game state (Stats, Combat, Resource, Level, StatusEffect)

### Technical Debt
1. **UI Coupling**: Curses library deeply embedded in game logic
2. **Mixed Concerns**: Combat flow mixed with rendering (`BattleManager.render_screen()`)
3. **Hardcoded Abilities**: 6000+ lines in `abilities.py` with procedural logic
4. **Enemy AI**: Placeholder action stack (see `enemies.py` line ~153)
5. **String-Based Communication**: Returns strings instead of structured events

## Migration Strategy: Terminal → GUI

### Phase 1: Presentation Layer Abstraction (Foundation)
**Goal**: Decouple game logic from terminal rendering without breaking existing game

#### 1.1 Create Presentation Interface
```python
# presentation/interface.py
class GamePresenter(ABC):
    @abstractmethod
    def render_combat(self, player, enemy, actions): pass
    
    @abstractmethod
    def render_menu(self, options): pass
    
    @abstractmethod
    def show_message(self, text): pass
    
    @abstractmethod
    def get_player_action(self, available_actions): pass
```

#### 1.2 Implement Terminal Presenter
Wrap existing curses logic in `CursesPresenter(GamePresenter)`

#### 1.3 Refactor Game Flow
- Replace direct curses calls with presenter methods
- Keep business logic separate from display logic

**Deliverables**:
- `presentation/` module with interface + curses implementation
- Modified `game.py` to use presenter pattern
- All tests still passing

**Status**: Partially complete - Interface defined (`presentation/interface.py`), 4 implementations created (Null, Console, EventDriven, Mock)

### Phase 2: Enhanced Combat & Event System ✅
**Goal**: Integrate action queue, implement event emissions, fix gameplay bugs

#### 2.1 EnhancedBattleManager
- Priority-based action queue (5 priority levels)
- Speed-based turn ordering
- Telegraph system for Seeker/Inquisitor foresight
- Charging action framework
- Backward compatible with feature flags

#### 2.2 Event System
```python
# events/event_bus.py
@dataclass
class CombatEvent:
    type: EventType  # ATTACK, SPELL_CAST, STATUS_APPLIED, etc.
    actor: Character
    target: Character | None
    result: CombatResult
    timestamp: float
    metadata: dict
```

#### 2.2 Event Emitter/Subscriber
```python
class EventBus:
    def emit(self, event: CombatEvent): ...
    def subscribe(self, event_type, callback): ...
```

Terminal presenter subscribes to events → formats as text
Future GUI presenter subscribes → updates sprite animations

**Deliverables**:
- `events/` module with event definitions
- Modified combat flow to emit events
- Backward-compatible terminal output

**Status**: ✅ **COMPLETE** - See `PHASE_2.md` and `EVENT_EMISSIONS.md`

### Phase 3: GUI Development (NEXT)
**Goal**: Build Pygame-based GUI using event-driven architecture

#### 3.1 Pygame Presenter
```python
# presentation/pygame_presenter.py
class PygamePresenter(GamePresenter):
    def __init__(self):
        self.event_bus = get_event_bus()
        self.event_bus.subscribe(EventType.DAMAGE_DEALT, self.animate_damage)
        self.event_bus.subscribe(EventType.SPELL_CAST, self.show_spell_effect)
    
    def animate_damage(self, event):
        # Display floating damage number
        # Animate health bar reduction
    
    def show_spell_effect(self, event):
        # Play spell animation
        # Show particle effects
```

#### 3.2 GUI Components
- **Combat View**: Character sprites, health/mana bars, status icons
- **Damage Numbers**: Floating text animations for damage/healing
- **Spell Effects**: Visual effects for spells/abilities
- **Turn Indicator**: Shows whose turn it is, telegraph messages
- **Combat Log**: Scrollable event history from event bus

**Benefits**:
- Modern, engaging interface
- Improved player experience
- Better visibility of combat mechanics
- Foundation for monetization (premium skins, effects)

**Deliverables**:
- `presentation/pygame_presenter.py`
- Sprite assets and animations
- Combat UI components
- Event-to-animation mappings

### Phase 4: Data-Driven Abilities
**Goal**: Move hardcoded abilities to JSON/YAML definitions

#### 4.1 Ability Schema
```yaml
# data/abilities/fireball.yaml
name: Fireball
type: Spell
subtype: Offensive
cost: 15
effects:
  - type: damage
    element: Fire
    base: 20
    scaling:
      - stat: intelligence
        ratio: 1.5
  - type: status
    name: Burn
    chance: 0.3
    duration: 3
```

#### 4.2 Ability Loader
```python
class AbilityFactory:
    @staticmethod
    def create(definition: dict) -> Ability:
        effects = [EffectFactory.create(e) for e in definition['effects']]
        return Ability(definition['name'], effects, ...)
```

**Benefits**:
- Easy balance tuning (no code changes)
- Moddability
- Analytics (which abilities are overpowered?)
- Automated testing of all abilities

**Status**: Partially complete - YAML loader exists in `data/ability_loader.py`, needs population with ability data

**Deliverables**:
- `data/abilities/` directory with YAML definitions
- `AbilityFactory` and `EffectFactory`
- Migration script for existing abilities
- Backward compatibility layer

### Phase 5: Analytics & Balance Framework
**Goal**: Automated testing and balance analysis (monetization angle)

#### 5.1 Combat Simulator
```python
class CombatSimulator:
    def simulate(self, p1, p2, iterations=1000):
        results = []
        for _ in range(iterations):
            battle = Battle(p1.clone(), p2.clone())
            results.append(battle.execute())
        return BalanceReport(results)
```

#### 5.2 Balance Metrics
- Win rate by class/level
- Average combat duration
- Ability usage frequency
- Damage distribution (identify outliers)

#### 5.3 Visualization
```python
# analytics/visualizer.py
class BalanceVisualizer:
    def plot_winrate_matrix(self): ...  # class vs class
    def plot_damage_curves(self): ...    # damage scaling by level
    def identify_overpowered(self): ...  # statistical outliers
```

**Deliverables**:
- `analytics/` module
- CLI tool: `python -m analytics.balance --class Warrior --iterations 10000`
- HTML reports with charts (matplotlib/plotly)
- Documented API for external tools

### Phase 6: GUI Implementation
**Goal**: Build actual GUI using presentation layer

#### 6.1 Technology Choice
**Option A: Pygame**
- Pros: Python-native, good for 2D tile-based games
- Cons: Desktop-only

**Option B: Web (Flask/FastAPI + Phaser.js)**
- Pros: Cross-platform, multiplayer-ready, modern
- Cons: More complex stack

**Recommendation**: Start with Pygame for desktop, web later

#### 6.2 Sprite System
```python
# presentation/pygame_presenter.py
class PygamePresenter(GamePresenter):
    def render_combat(self, player, enemy, actions):
        self.draw_sprite(player, self.player_pos)
        self.draw_sprite(enemy, self.enemy_pos)
        self.draw_action_menu(actions)
```

#### 6.3 Animation System
Subscribe to events:
- `ATTACK` → play attack animation
- `DAMAGE_TAKEN` → flash red, show damage number
- `STATUS_APPLIED` → show status icon

**Deliverables**:
- `presentation/pygame_presenter.py`
- Asset loading system
- Animation controller
- Playable GUI version (feature parity with terminal)

## Monetization Pathways

### Developer Tools (B2B)
1. **Combat Balance SaaS**
   - Upload game data (abilities, enemies)
   - Run simulations on cloud
   - Get balance reports

2. **Procedural Dungeon Generator**
   - API: `POST /generate-dungeon` → returns map JSON
   - Configurable difficulty curves
   - Subscription tiers by generation volume

3. **Open Core Model**
   - Free: Basic combat engine + analytics
   - Paid: Advanced AI, multiplayer, cloud saves

### Technical Roadmap for Tools

#### Year 1: Foundation
- Q1-Q2: Phases 1-3 (abstraction, events, action queue)
- Q3: Phase 4 (data-driven abilities)
- Q4: Phase 5 (analytics MVP)

#### Year 2: Product Development
- Q1: Polish analytics, create docs
- Q2: Extract reusable components into library
- Q3: Build demo games using library
- Q4: Launch developer beta

#### Year 3: Commercialization
- Q1-Q2: SaaS platform development
- Q3: Public launch, marketing
- Q4: Iterate based on feedback

## Implementation Priority (Next Steps)

### Immediate (This Session)
1. ✅ Create this architecture doc
2. ⏳ Implement basic `ActionQueue` (combat improvement)
3. ⏳ Enhance `Effect` system (add more effect types)
4. ⏳ Create `EventBus` prototype
5. ⏳ Start analytics module (basic combat simulator)

### Short Term (Next 2-4 Weeks)
1. Complete presentation layer abstraction
2. Migrate 10 abilities to data-driven format (proof of concept)
3. Implement enemy action stacks
4. Create balance testing CLI tool

### Medium Term (1-3 Months)
1. Full ability migration
2. Pygame GUI prototype
3. Comprehensive test suite
4. Documentation for library usage

## File Organization (Proposed)

```
dungeon-crawl/
├── core/                    # Engine (UI-agnostic)
│   ├── combat/
│   │   ├── action_queue.py
│   │   ├── battle_manager.py
│   │   └── turn_manager.py
│   ├── character/
│   │   ├── base.py
│   │   ├── player.py
│   │   └── enemy.py
│   ├── abilities/
│   │   ├── factory.py
│   │   └── loader.py
│   └── events/
│       ├── bus.py
│       └── types.py
├── data/                    # Definitions
│   ├── abilities/
│   ├── enemies/
│   ├── items/
│   └── maps/
├── presentation/            # UI layer
│   ├── interface.py
│   ├── curses_presenter.py
│   └── pygame_presenter.py  (future)
├── analytics/               # Balance tools
│   ├── simulator.py
│   ├── metrics.py
│   └── visualizer.py
├── effects/                 # Current (keep)
├── tests/
└── legacy/                  # Old code during migration
```

## Testing Strategy

### Unit Tests
- Every effect type
- Every ability (data-driven → easy to test all)
- Action queue edge cases
- Event bus behavior

### Integration Tests
- Full combat scenarios
- Save/load game state
- Quest completion flows

### Balance Tests
```python
def test_no_oneshot_builds():
    for attacker_class in ALL_CLASSES:
        for defender_class in ALL_CLASSES:
            sim = Simulator(attacker_class(level=10), defender_class(level=10))
            results = sim.run(1000)
            assert results.oneshot_rate < 0.05  # Less than 5% instant kills
```

### Performance Tests
- Combat simulation speed (target: 1000 battles/sec)
- UI render time (target: 60 FPS for GUI)

## Backward Compatibility

During migration:
- Keep existing files working
- New code in parallel modules
- Feature flags to toggle new systems
- Gradual deprecation with warnings

## Success Metrics

### Technical
- Code coverage > 80%
- Separation: 0% UI code in `core/`
- Performance: 1000 simulated battles < 10 seconds

### Product
- 3 demo games using the engine
- 10 external developers using tools
- Positive ROI on tool development (if monetized)

## Questions to Resolve

1. **Multiplayer**: Scope for Phase 7+?
2. **Mobile**: After GUI or parallel track?
3. **AI Difficulty**: Rule-based or ML? (Start rule-based)
4. **Save Format**: Current dill or JSON for cross-platform?
5. **Modding Support**: Plugin architecture? Scripting language?

## Conclusion

This architecture positions Dungeon Crawl as:
1. **A playable game** (terminal now, GUI later)
2. **A technical showcase** (clean architecture, testable)
3. **A platform** (reusable engine + tools)
4. **A product** (monetizable developer tools)

The migration is incremental, low-risk, and each phase delivers value independently.
