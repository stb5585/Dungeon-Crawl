###########################################
""" Storyline manager with typed-like output """

# Imports
import pickle
import os
import sys
import time


def slow_type(line):
    typing_speed = 100  # wpm
    for item in line:
        sys.stdout.write(item)
        sys.stdout.flush()
        time.sleep(5 / typing_speed)


def display_page_text(lines: list):
    for line in lines:
        slow_type(line)  # Make the user press enter to see the next line
        get_input([''])


def get_input(valid_input: list):
    while True:
        user_entered = input()

        if user_entered not in valid_input:
            print("Invalid input. Please use one of the following inputs:\n")
            print(valid_input)
            # user_entered = None

        else:
            return user_entered


def get_response(options: list, **kwargs):
    for index, option in enumerate(options):
        print(str(index) + ". " + option[0])
        time.sleep(0.25)

    valid_inputs = [str(num) for num in range(len(options))]
    option_index = int(get_input(valid_inputs))

    return options[option_index][1]


def story_flow(story_dict: dict):
    curr_page = 1
    while curr_page is not None:
        page = story_dict.get(curr_page, None)
        if page is None:
            # curr_page = None
            break

        display_page_text(page['Text'])

        if len(page['Options']) == 0:
            # curr_page = None
            break

        curr_page = get_response(page['Options'])


def pickle_story(story_dict: dict):
    if not os.path.exists('chapters/chapter' + str(list(story_dict.keys())[0]) + '.ch'):
        with open('chapters/chapter' + str(list(story_dict.keys())[0]) + '.ch', 'wb') as chapter:
            pickle.dump(story_dict, chapter)
    else:
        confirm = input("This chapter already exists. Are you sure you want to overwrite? (Yes or No) ").lower()
        if confirm == 'yes':
            os.remove('chapters/chapter' + str(list(story_dict.keys())[0]) + '.ch')
            with open('chapters/chapter' + str(list(story_dict.keys())[0]) + '.ch', 'wb') as chapter:
                pickle.dump(story_dict, chapter)
        else:
            print("The file will not be overridden.")


def read_story(story_file):
    # story_dict = {}

    with open(story_file, 'rb') as file:
        story_dict = pickle.load(file)

    story_flow(story_dict)


# Define story #
story = {1: {'Options': [("Yeah of course!", 2), ("I'm sorry I don't...", 3)],
             'Text': ["Hello there..", "I bet you weren't expecting to hear from me so soon...",
                      "...you seem a little confused do you know who I am?"]}}
