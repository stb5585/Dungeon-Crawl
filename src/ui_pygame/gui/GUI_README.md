# Dungeon Crawl - Pygame GUI

## Overview

The GUI version of Dungeon Crawl uses Pygame to provide a graphical interface for combat instead of the traditional curses text interface.

## Features

- **Visual Combat Display**: See your character and enemies rendered with sprites
- **Animated Damage**: Floating damage numbers with color-coded damage types
- **Screen Shake Effects**: Dynamic camera shake based on damage intensity
- **Status Icons**: Visual indicators for active status effects
- **Real-time Event System**: Combat updates driven by event subscriptions
- **Combat Log**: Scrolling log of combat actions

## Quick Start

### Launch the GUI Game

```bash
./launch_gui.sh
```

Or directly with Python:

```bash
source .venv/bin/activate
export PYTHONPATH="$(pwd):$PYTHONPATH"
python pygame_game.py
```

## Current Status

### ✅ Implemented

- PygamePresenter with full event integration
- Sprite generation system (21 sprites)
- Sprite caching and management
- Character sprite rendering
- Health/Mana bar display
- Status effect icon display
- Combat demo with simulated events
- Floating damage text animations
- Screen shake on damage/crits
- Color-coded damage types (8 types)

### 🔄 In Progress

- Full BattleManager integration
- Player input handling during combat
- Complete combat action flow

### 📋 Planned

- Spell effect animations
- Particle systems for magic
- Sound effects and music
- Main menu polish
- Game over screens
- Save/Load integration

## Controls

- **Mouse**: Click menu options
- **Enter**: Confirm selections
- **ESC**: Cancel/Back
- **Space**: Advance text boxes

## Combat Demo

The current version includes a combat demo that:
1. Creates a test enemy (Goblin Warrior)
2. Simulates 3 combat turns
3. Shows damage animations and floating text
4. Demonstrates critical hits and screen shake
5. Displays final victory message

This demo showcases the GUI capabilities while full combat integration is completed.

## Architecture

### Components

- **pygame_game.py**: Main GUI game launcher
- **presentation/pygame_presenter.py**: Pygame-based presenter (550+ lines)
- **assets/sprite_generator.py**: Programmatic sprite creation
- **assets/sprite_manager.py**: Sprite caching and retrieval
- **events/**: Event bus system for decoupled combat logic

### Event Flow

```
Combat System → EventBus → PygamePresenter → Visual Display
```

The presenter subscribes to 7 combat events:
- COMBAT_START
- COMBAT_END
- TURN_START
- DAMAGE_DEALT
- HEALING_DONE
- CRITICAL_HIT
- STATUS_APPLIED

## Development

### Adding New Sprites

1. Create sprite in `assets/sprite_generator.py`
2. Add mapping in `assets/sprite_manager.py`
3. Sprite manager will cache on first load

### Customizing Colors

Edit color constants in `presentation/pygame_presenter.py`:
- DAMAGE_COLORS: Damage type colors
- Basic colors: RED, GREEN, BLUE, etc.

### Adjusting Animations

- **Floating Text**: Modify `FloatingText` class
- **Screen Shake**: Adjust intensity in `_on_damage_dealt()`
- **Speed**: Change `self.fps` in PygamePresenter.__init__()

## Troubleshooting

### "No video mode has been set"

This is expected when running tests without a display. The sprite manager handles this gracefully with fallback loading.

### Display not showing

Make sure you're running in a graphical environment (not SSH without X forwarding).

### Import errors

Ensure PYTHONPATH includes the project root:
```bash
export PYTHONPATH="/home/tom/Projects/Dungeon-Crawl:$PYTHONPATH"
```

## Credits

- Pygame 2.6.1
- SDL 2.28.4
- Event system inspired by observer pattern
- Sprite generation using programmatic pygame.draw functions
