###########################################
""" movement manager """

# Imports
import sys

import character


# Functions
def game_help(state):
    print(list(Commands[state].keys()))


def game_quit():
    print("Goodbye!")
    sys.exit(0)


# Define Parameters
Commands = {'normal':
                {'explore': ('EXPLORE', character.Player.explore), 'status': ('STATUS', character.Player.status),
                 'rest': ('REST', character.Player.rest), 'inventory': ('INVENTORY', character.Player.print_inventory),
                 'potion': ('POTION', character.Player.use_potion), 'save': ('SAVE', character.Player.save),
                 'quit': ('QUIT', game_quit)},
            'fight':
                {'attack': ('ATTACK', character.Player.combat), 'potion': ('POTION', character.Player.use_potion),
                 'flee': ('FLEE', character.Player.flee)}}
