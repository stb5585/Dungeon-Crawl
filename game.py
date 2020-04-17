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
    os.system('cls' if os.name == 'nt' else 'clear')
    f = pyfiglet.Figlet(font='slant')
    print(f.renderText("DUNGEON CRAWL"))
    time.sleep(2)
    world.load_tiles()
    if not os.path.exists('save_files'):
        os.mkdir('save_files')
    play_options = [('New Game', 0), ('Load Game', 1), ('Tutorial', 2)]
    play_index = storyline.get_response(play_options)
    os.system('cls' if os.name == 'nt' else 'clear')
    if play_options[play_index][1] == 0:
        player = character.new_char()
    elif play_options[play_index][1] == 1:
        if len(glob.glob('save_files/*')) > 0:
            player = character.load_char()
        else:
            print("There are no save files to load. Proceeding to new character creation.")
            player = character.new_char()
    else:
        player = tutorial.tutorial()
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        room = world.tile_exists(player.location_x, player.location_y, player.location_z)
        room.modify_player(player)
        if player.is_alive():
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
        else:
            time.sleep(2)
            player.death()
            player.health = player.health_max
            player.mana = player.mana_max
            player.location_x, player.location_y, player.location_z = world.starting_position
            print("You wake up in town.")


if __name__ == "__main__":
    play()
