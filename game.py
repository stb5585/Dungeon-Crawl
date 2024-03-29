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


def unobtainium_room():
    texts = [
        "A brilliant column of light highlights the small piece of ore on a pedestal at the center of the room.",
        "You approach it with caution but find no traps or tricks.",
        "This must be the legendary ore you have heard so much about...",
        "You reach for it, half expecting to be obliterated...but all you feel is warmth throughout your body.",
        "You have obtained the Unobtainium!"
        ]
    for text in texts:
        time.sleep(0.1)
        storyline.slow_type(text)
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')


def final_boss(player):
    texts = [
        "You enter a massive room. A great beast greets you.",
        "\"Hello {}, I've heard stories of an adventurer making easy work of the creatures scattered throughout the "
        "labyrinth.".format(player.name),
        "It would seem our meeting was inevitable but it still doesn't lessen the sorrow I feel, knowing that one of us"
        " will not leave here alive.",
        "Let us settle this!\""
        ]
    for text in texts:
        time.sleep(0.1)
        storyline.slow_type(text)
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')


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
        world.save_world(world_dict=world_dict)
    else:
        player = tutorial.tutorial()
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        room = world.tile_exists(player.location_x, player.location_y, player.location_z)
        room.modify_player(player, world_dict)
        if player.is_alive():
            if (time.time() - timer) // (900 * player.pro_level):
                world.load_tiles(world_dict=world_dict, reload=True)
                timer = time.time()
            room = world.tile_exists(player.location_x, player.location_y, player.location_z)
            try:
                if room.special:
                    room.special_text(player)
            except AttributeError:
                pass
            room.modify_player(player, world_dict)
            os.system('cls' if os.name == 'nt' else 'clear')
            room.minimap(player, world_dict)
            if room.intro_text(player) is not None:
                print(room.intro_text(player))
            print("Player: {} | Health: {}/{} | Mana: {}/{}".format(player.name, player.health, player.health_max,
                                                                    player.mana, player.mana_max))
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
            player.death()


if __name__ == "__main__":
    start_time = time.time()
    play(start_time)
