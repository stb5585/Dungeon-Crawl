# Shop Interface Update - Pygame GUI

## Overview
Updated the Pygame shop interface to closely match the curses terminal layout, providing a more familiar and consistent user experience.

## New Layout Structure

The shop screen now follows the exact layout of the curses terminal interface:

```
┌──────────────────────────────────────────────────────────────────┐
│                    Shop Header Message                            │
├─────────────────────────┬─────────────────────────────────────────┤
│                         │                                          │
│    Menu Options         │      Item Description                   │
│    - Buy                │      (Shows description of               │
│    - Sell               │       highlighted item)                 │
│    - Quests             │                                          │
│    - Leave              │                                          │
├─────────────────────────┴──────────────┬─────────────────────────┤
│                                        │                           │
│  Item List                             │  Equipment Modifications │
│  Type    Item               Cost Owned │  (Stat comparison)       │
│  ----    ----               ---- ----- │                           │
│  Health  Health Potion       100  x 0  │  Health:    +50  (Better)│
│  Misc    Mana Potion          50  x 2  │  Mana:      +25  (Better)│
│  ...                                   │  ...                     │
│                                        ├───────────────────────────┤
│                                        │                           │
│                                        │  Gold: 2500G             │
└────────────────────────────────────────┴───────────────────────────┘
```

## Files Created/Modified

### New Files
- **gui/shop_screen.py**: Complete implementation of the ShopScreen class that renders the multi-panel shop interface

### Modified Files
- **gui/shops.py**: Updated ShopManager to use the new ShopScreen for all shop interactions
  - `visit_alchemist()`: Now uses ShopScreen for main menu
  - `visit_blacksmith()`: Now uses ShopScreen for main menu
  - `visit_jeweler()`: Now uses ShopScreen for main menu
  - `buy_equipment()`: Simplified to use ShopScreen
  - `buy_potions()`: Updated to use ShopScreen
  - `sell_items()`: Updated to use ShopScreen

## Features

### Six-Panel Layout
1. **Top Header** (1/12 height): Shop title/message
2. **Options Panel** (left 1/3, 1/4 height): Buy/Sell/Quests/Leave menu
3. **Description Panel** (right 2/3, 1/4 height): Item description text
4. **Item List Panel** (left 2/3, 2/3 height): Scrollable list of all items
5. **Stat Comparison Panel** (right 1/3, 7/12 height): Equipment modifications preview
6. **Gold Panel** (right 1/3, 1/12 height): Player's current gold

### Item Display Format
Matches curses formatting exactly:
- **Buy mode**: `Type  Item  Cost  Owned`
- **Sell mode**: `Type  Item  Owned`

### Real-time Stat Comparison
When browsing equipment items (Weapon, OffHand, Armor, Accessory):
- Shows current vs. new item stats
- Color-coded: Green for improvements, Red for downgrades
- Displays stat differences with +/- indicators

### Responsive Navigation
- UP/DOWN: Navigate through options or items
- ENTER/SPACE: Select option or item
- ESC: Go back or cancel
- Scrolling for lists with >19 items

## Usage Example

```python
from gui.shops import ShopManager
from presentation.pygame_presenter import PygamePresenter

# Initialize presenter and player
presenter = PygamePresenter()
player = create_test_player(gold=5000, level=15)

# Create shop manager
shop_manager = ShopManager(presenter, player)

# Visit any shop
shop_manager.visit_alchemist()   # "Welcome to Ye Olde Item Shoppe."
shop_manager.visit_blacksmith()  # "Griswold's Blacksmith"
shop_manager.visit_jeweler()     # "Come glimpse the finest jewelry..."
```

## Technical Details

### ShopScreen Class
- **Window Positioning**: Uses precise ratios matching curses (1/12, 1/4, 1/3, 2/3, 7/12)
- **Font System**: Uses presenter's existing fonts (title_font, normal_font, small_font)
- **Color Scheme**: Matches curses colors (Yellow highlights, White text, Gray borders)
- **State Management**: Tracks current option, current item, scroll offset

### Key Methods
- `draw_all()`: Renders all six panels
- `navigate_options()`: Handle Buy/Sell/Quests/Leave navigation
- `navigate_items()`: Handle item list navigation with selection
- `update_item_list()`: Rebuild item list for Buy or Sell mode
- `draw_mod()`: Render equipment stat comparison

### Item Filtering
- **Level restrictions**: Items with `restriction` attribute are filtered by player level
- **Rarity filtering**: Town shops filter by rarity based on player level
- **Ultimate items**: Cannot be sold (filtered from sell list)

### Charisma Effects
- **Buy prices**: Reduced by charisma via `scaled_decay_function()`
- **Sell prices**: Increased by 2.5% per charisma point

## Benefits

1. **Consistency**: Pygame interface now matches curses terminal exactly
2. **Familiarity**: Players can easily transition between interfaces
3. **Information density**: All relevant info visible at once (no popup switching)
4. **Stat preview**: See equipment changes before purchase
5. **Gold tracking**: Always visible in dedicated panel
6. **Description clarity**: Dedicated panel for item descriptions

## Testing

Test script created at `test_shop_gui.py`:
```bash
python test_shop_gui.py
```

This creates a test player and opens the alchemist shop to verify the new interface.
