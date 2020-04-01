##########################################
""" Basic RPG """

# Imports
import os
import glob

import world
import character
import town


def play():
    new_char = True
    world.load_tiles()
    if not os.path.exists('save_files'):
        os.mkdir('save_files')
    if len(glob.glob('save_files/*')) != 0:
        load = input("Do you wish to load a character? ").lower()
        if 'y' in load:
            player = character.load_char()
            new_char = False
        else:
            player = character.new_char()
    else:
        player = character.new_char()
    if new_char:
        town.town(player)
    while player.is_alive():
        if player.location_z != 0:
            room = world.tile_exists(player.location_x, player.location_y, player.location_z)
            room.modify_player(player)
        # Check again since the room could have changed the player's state
        if player.is_alive():
            if player.location_z == 0:
                print("You feel rested!")
                player.health = player.health_max
                player.mana = player.mana_max
                town.town(player)
            else:
                room = world.tile_exists(player.location_x, player.location_y, player.location_z)
                room.modify_player(player)
                if room.intro_text() is not None:
                    print(room.intro_text())
                print("Choose an action:\n")
                available_actions = room.available_actions()
                for action in available_actions:
                    print(action)
                action_input = input('Action: ')
                for action in available_actions:
                    if action_input == action.hotkey:
                        player.do_action(action, **action.kwargs)
                        break


if __name__ == "__main__":
    play()
