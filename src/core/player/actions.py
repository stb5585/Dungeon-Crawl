"""Menu action metadata for the public Player class."""

from .core import Player


actions_dict = {
    'MoveForward': {
        'method': Player.move_forward,
        'name': 'Move forward (w)',
        'hotkey': 'w'
    },
    'TurnAround': {
        'method': Player.turn_around,
        'name': 'Turn around (s)',
        'hotkey': 's'
    },
    'TurnRight': {
        'method': Player.turn_right,
        'name': 'Turn right (d)',
        'hotkey': 'd'
    },
    'TurnLeft': {
        'method': Player.turn_left,
        'name': 'Turn left (a)',
        'hotkey': 'a'
    },
    'StairsUp': {
        'method': Player.stairs_up,
        'name': 'Take stairs up',
        'hotkey': 'u'
    },
    'StairsDown': {
        'method': Player.stairs_down,
        'name': 'Take stairs down',
        'hotkey': 'j'
    },
    'ViewInventory': {
        'method': Player.inventory_screen,
        'name': 'Inventory',
        'hotkey': None
    },
    'ViewKeyItems': {
        'method': Player.key_item_screen,
        'name': 'Key Items',
        'hotkey': None
    },
    'Equipment': {
        'method': Player.equipment_screen,
        'name': 'Equipment',
        'hotkey': None
    },
    'Specials': {
        'method': Player.abilities_screen,
        'name': 'Specials',
        'hotkey': None
    },
    'ViewQuests': {
        'method': Player.quests_screen,
        'name': 'Quests',
        'hotkey': None
    },
    'Summons': {
        'method': Player.summon_menu,
        'name': 'Summons',
        'hotkey': None
    },
    'JumpMods': {
        'method': Player.jump_mods_menu,
        'name': 'Jump Mods',
        'hotkey': None
    },
    'TotemAspects': {
        'method': Player.totem_aspects_menu,
        'name': 'Totem Aspects',
        'hotkey': None
    },
    'Flee': {
        'method': Player.flee,
        'name': 'Flee',
        'hotkey': None
    },
    'Open': {
        'method': Player.open_up,
        'name': 'Open',
        'hotkey': 'o'
    },
    'Save': {
        'method': Player.save,
        'name': 'Save',
        'hotkey': None
    },
    'Quit': {
        'method': Player.game_quit,
        'name': 'Quit',
        'hotkey': None
    },
    'CharacterMenu': {
        'method': Player.character_menu,
        'name': 'Character Menu',
        'hotkey': 'c'
    }
}
