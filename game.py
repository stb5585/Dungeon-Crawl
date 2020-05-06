##########################################
""" Basic RPG """

# Imports
import os
import glob
import time

import world
import character
import tutorial
import display


def play(timer):
    # f = pyfiglet.Figlet(font='slant')
    # print(f.renderText("DUNGEON CRAWL"))
    player = None
    world.load_tiles()
    if not os.path.exists('save_files'):
        os.mkdir('save_files')
    while True:
        play_option = display.intro_menu()
        if play_option == 'NEW GAME':
            player = character.new_char()
        elif play_option == 'LOAD GAME':
            if len(glob.glob('save_files/*')) > 0:
                player = character.load_char()
            else:
                player = False
        elif play_option == 'TUTORIAL':
            player = tutorial.tutorial()
        if player:
            break
    while True:
        if ((time.time() - timer) // (900 * player.pro_level)) > 0:
            world.load_tiles()
            timer = time.time()
        room = world.tile_exists(player.location_x, player.location_y, player.location_z)
        room.modify_player(player)
        display.dungeon(player)
        if player.is_alive():
            if player.state == 'fight':
                pass
            room = world.tile_exists(player.location_x, player.location_y, player.location_z)
            room.modify_player(player)
            available_actions = room.available_actions(player)
            display.player_movement(player, room, available_actions)
            # if room.intro_text() is not None:
            #     print(room.intro_text())
            # print("Choose an action:\n")
            # available_actions = room.available_actions(player)
            # for action in available_actions:
            #     print(action)
            # action_input = input('Action: ')
            # for action in available_actions:
            #     if action_input == action.hotkey:
            #         player.do_action(action, **action.kwargs)
            #         break
        else:
            player.death()
            player.health = player.health_max
            player.mana = player.mana_max
            player.location_x, player.location_y, player.location_z = world.starting_position


if __name__ == "__main__":
    start_time = time.time()
    play(start_time)
