##########################################
""" Basic RPG """

# Imports
import sys
import glob

import character
import storyline
import movement

try:
    if sys.argv[1] == 'story':
        while True:
            chapter = input("Which chapter do you wish to update? ")
            try:
                storyline.pickle_story(storyline.story)
                break
            except KeyError:
                print("Input was invalid. Please enter a valid chapter number.")
except IndexError:
    pass

if __name__ == "__main__":

    load = input("Do you wish to load a character? ").lower()
    if 'y' in load and len(glob.glob('save_files/*')) != 0:
        player = character.load_char()
    elif 'y' in load and len(glob.glob('save_files/*')) == 0:
        print("There are no save files to load. You will have to create a new character.")
        player = character.new_char()
    else:
        player = character.new_char()

    Commands = movement.Commands
    # player.status()
    if 'y' not in load:
        # storyline.read_story('chapters/chapter1.ch')
        print("(type help to get a list of actions)\n")
        print("%s enters a dark cave, searching for adventure." % player.name)

    while True:
        print("What would you like to do?")
        # line = input("> ")
        # args = line.split()
        # if len(args) > 0:
        # commandFound = False
        command_list = list(Commands[player.state].values())
        choice = storyline.get_response(command_list)
        # for c in Commands[player.state].keys():
        #     if args[0] == c[:len(args[0])]:
        try:
            choice()
        except TypeError:
            try:
                choice(player)
            except KeyError:
                choice(player.state)
            # commandFound = True
            # break
            # if not commandFound:
            #     print("%s doesn't understand the suggestion." % player.name)
