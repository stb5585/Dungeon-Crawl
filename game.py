##########################################
""" Basic RPG """

# Imports
import os
import time
import glob
import pyfiglet

import world
import character
import town
import storyline
import tutorial


def play():
    os.system('clear')
    f = pyfiglet.Figlet(font='slant')
    print(f.renderText("DUNGEON CRAWL"))
    time.sleep(2)
    new_char = True
    world.load_tiles()
    if not os.path.exists('save_files'):
        os.mkdir('save_files')
    play_options = [('New Game', 0), ('Load Game', 1), ('Tutorial', 2)]
    play_index = storyline.get_response(play_options)
    os.system('clear')
    if play_options[play_index][1] == 0:
        player = character.new_char()
    elif play_options[play_index][1] == 1:
        if len(glob.glob('save_files/*')) > 0:
            player = character.load_char()
            new_char = False
        else:
            print("There are no save files to load. Proceeding to new character creation.")
            player = character.new_char()
    else:
        player = tutorial.tutorial()
    os.system('clear')
    if new_char:
        town.town(player)
    while player.is_alive():
        if player.location_z != 0:
            room = world.tile_exists(player.location_x, player.location_y, player.location_z)
            room.modify_player(player)
        # Check again since the room could have changed the player's state
        if player.is_alive():
            if player.location_z == 0:
                world.load_tiles()  # going back to town respawns dungeon
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
                available_actions = room.available_actions(player)
                for action in available_actions:
                    print(action)
                action_input = input('Action: ')
                for action in available_actions:
                    if action_input == action.hotkey:
                        player.do_action(action, **action.kwargs)
                        break


if __name__ == "__main__":
    play()
