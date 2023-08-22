##########################################
""" Basic RPG """

# Imports
import os
import time
import glob

import pyfiglet

import actions
import player
import storyline
import tutorial

# Parameters
home = os.getcwd()
save_dir = "save_files"


# Functions
def new_player():
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    texts = [
        "A great evil has taken hold in the unlikeliest of places, a small town on the edge of the kingdom.\n",
        "The town of Silvana has sent out a plea for help, with many coming from far and wide to test their mettle.\n",
        "You, bright-eyed and bushy-tailed, decided that fame and glory were within reach.\n",
        "What you didn't know was that all who had attempted this feat have never been heard from again.\n",
        "Will you be different or just another lost soul?\n",
    ]
    for text in texts:
        time.sleep(1)
        storyline.slow_type(text)
    time.sleep(2)


def timmy():
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    texts = [
        "'Hello...who's there?'\n",
        "You see a small child peak out from behind some rubble.\n",
        "'This place is scary...I want to go home.'\n",
        "You have found the little boy, Timmy, and escort him home.\n"
    ]
    for text in texts:
        time.sleep(1)
        storyline.slow_type(text)
    time.sleep(2)


def dead_body():
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    texts = [
        "Before you lies the body of a warrior, battered, bloody, and broken...\n",
        "This must be the body of Joffrey, the one betrothed to the waitress at the tavern.\n",
        "You move the body for a proper burial and notice a crushed gold locket lying on the ground.\n",
        "You should return this to its rightful owner...\n"
    ]
    for text in texts:
        time.sleep(1)
        storyline.slow_type(text)
    time.sleep(2)


def relic_room(level):
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    relics = ['Triangulus', 'Quadrata', 'Hexagonum', 'Luna', 'Polaris', 'Infinitas']
    texts = [
        "A bright column of light highlights a pedestal at the center of the room.\n",
        "You instantly realize the significance of the finding, sure that this is one of the six relics you seek.\n",
        "You eagerly take the relic and instantly feel rejuvenated.\n"
        "You have obtained the {} relic!\n".format(relics[int(level) - 1])
    ]
    for text in texts:
        time.sleep(1)
        storyline.slow_type(text)
    time.sleep(2)


def warp_point(player_char):
    yes_no = ["Yes", "No"]
    print("Hello, {}. Do you want to warp back to town?".format(player_char.name))
    confirm = storyline.get_response(yes_no)
    if yes_no[confirm] == 'Yes':
        print("You step into the warp point, taking you back to town.")
        time.sleep(1)
        player_char.world_dict[(3, 0, 5)].warped = True
        player_char.change_location(5, 10, 0)
    else:
        print("Not a problem, come back when you change your mind.")
    return


def unobtainium_room():
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    texts = [
        "A brilliant column of light highlights the small piece of ore on a pedestal at the center of the room.\n",
        "You approach it with caution but find no traps or tricks.\n",
        "This must be the legendary ore you have heard so much about...\n",
        "You reach for it, half expecting to be obliterated...but all you feel is warmth throughout your body.\n",
        "You have obtained the Unobtainium!\n"
    ]
    for text in texts:
        time.sleep(1)
        storyline.slow_type(text)
    time.sleep(2)
    input("Press enter to continue")


def final_blocker():
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    texts = [
        "The invisible force that once blocked you path is now gone.\n",
        "What lies ahead is unknown.\n"
        "Proceed at your own peril...\n"
    ]
    for text in texts:
        time.sleep(1)
        storyline.slow_type(text)
    time.sleep(2)
    input("Press enter to continue")


def final_boss(player_char):
    """

    """

    os.system('cls' if os.name == 'nt' else 'clear')
    texts = [
        "You enter a massive room. A great beast greets you.\n",
        "\"Hello again, {}. You have done well to reach me, many have tried and failed.\n".format(player_char.name),
        "The bones of those that came before you litter this sanctum. Will your bones join them?\n",
        "It would seem our meeting was inevitable but it still doesn't lessen the sorrow I feel, knowing that one of us"
        " will not leave here alive.\n",
        "I give you but one chance to reconsider, after which I will not go easy on you.\""
    ]
    for text in texts:
        time.sleep(1)
        storyline.slow_type(text)
    print("Do you wish to fight or retreat with your tail tucked?")
    options = ['Fight', 'Retreat']
    response = storyline.get_response(options)
    if options[response] == "Fight":
        print("Then let us begin.")
        time.sleep(1)
        return True
    print("Run away, little girl, run away!")
    time.sleep(1)
    return False


def play():
    os.system('cls' if os.name == 'nt' else 'clear')
    f = pyfiglet.Figlet(font='slant')
    print(f.renderText("DUNGEON CRAWL"))
    time.sleep(2)
    if not os.path.exists('save_files'):
        os.mkdir('save_files')
    play_options = ['New Game', 'Load Game', 'Tutorial']
    play_index = storyline.get_response(play_options)
    os.system('cls' if os.name == 'nt' else 'clear')
    if play_index == 0:
        new_player()
        player_char = player.new_char()
    elif play_index == 1:
        print(f.renderText("DUNGEON CRAWL"))
        if len(glob.glob('save_files/*')) > 0:
            os.chdir(save_dir)
            player_char = player.load_char()
            os.chdir(home)
        else:
            print("There are no save files to load. Proceeding to new character creation.")
            time.sleep(1)
            new_player()
            player_char = player.new_char()
    else:
        player_char = tutorial.tutorial()
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        valid = False
        room = player_char.world_dict[(player_char.location_x, player_char.location_y, player_char.location_z)]
        room.modify_player(player_char)
        while not valid:
            if not player_char.is_alive():
                break
            room = player_char.world_dict[(player_char.location_x, player_char.location_y, player_char.location_z)]
            try:
                room.special_text(player_char)
            except AttributeError:
                pass
            if player_char.is_alive():
                os.system('cls' if os.name == 'nt' else 'clear')
                player_char.minimap()
                if room.intro_text(player_char) is not None:
                    print(room.intro_text(player_char))
                    try:
                        room.warning = True
                    except AttributeError:
                        pass
                if player_char.in_town():
                    break
                print("Player: {} | Health: {}/{} | Mana: {}/{}".format(player_char.name,
                                                                        player_char.health, player_char.health_max,
                                                                        player_char.mana, player_char.mana_max))
                available_actions = room.available_actions(player_char)
                print("\t\t{}".format(actions.MoveNorth()))
                print("\t{}\t{}".format(actions.MoveWest(), actions.MoveEast()))
                print("\t\t{}".format(actions.MoveSouth()))
                action_input = input()
                for action in available_actions:
                    if action_input == action.hotkey:
                        player_char.do_action(action, **action.kwargs)
                        if action_input in ['w', 'a', 's', 'd', 'o', 'j', 'u']:
                            valid = True
                        break
            else:
                player_char.death()
                valid = True
            if valid:
                break


if __name__ == "__main__":
    play()
