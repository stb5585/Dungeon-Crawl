##########################################
""" Basic RPG """

# Imports
import os
import time
import glob
import pyfiglet

import world
import character
import storyline
import tutorial


# Parameters
home = os.getcwd()
save_dir = "save_files"


def play(timer):
    world_dict = {'World': {}}
    os.system('cls' if os.name == 'nt' else 'clear')
    f = pyfiglet.Figlet(font='slant')
    print(f.renderText("DUNGEON CRAWL"))
    time.sleep(2)
    if not os.path.exists('save_files'):
        os.mkdir('save_files')
    play_options = [('New Game', 0), ('Load Game', 1), ('Tutorial', 2)]
    play_index = storyline.get_response(play_options)
    os.system('cls' if os.name == 'nt' else 'clear')
    if play_options[play_index][1] == 0:
        player = character.new_char()
        world.load_tiles(world_dict=world_dict)
        world_dict = world.world_return()
    elif play_options[play_index][1] == 1:
        if len(glob.glob('save_files/*')) > 0:
            os.chdir(save_dir)
            player, world_dict['World'] = character.load_char()
            os.chdir(home)
        else:
            print("There are no save files to load. Proceeding to new character creation.")
            player = character.new_char()
        world.load_tiles(world_dict=world_dict)
    else:
        player = tutorial.tutorial()
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        if ((time.time() - timer) // 900 * player.pro_level) > 0:
            world.load_tiles(world_dict=world_dict)
            timer = time.time()
        room = world.tile_exists(player.location_x, player.location_y, player.location_z)
        room.modify_player(player, world_dict)
        if player.is_alive():
            room = world.tile_exists(player.location_x, player.location_y, player.location_z)
            room.modify_player(player, world_dict)
            os.system('cls' if os.name == 'nt' else 'clear')
            room.minimap(player, world_dict)
            if room.intro_text(player) is not None:
                print(room.intro_text(player))
            print("Health: {}/{}  Mana: {}/{}".format(player.health, player.health_max, player.mana, player.mana_max))
            print("Choose an action:")
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
            time.sleep(2)


if __name__ == "__main__":
    start_time = time.time()
    play(start_time)
