###########################################
""" Storyline manager with typed-like output """

# Imports
import pickle
import sys
import time


def slow_type(line, typing_speed=100):
    for item in line:
        sys.stdout.write(item)
        sys.stdout.flush()
        time.sleep(5 / typing_speed)


def display_page_text(lines: list):
    for line in lines:
        slow_type(line)
        time.sleep(1)


def get_input(valid_input: list):
    while True:
        user_entered = input()
        if user_entered not in valid_input:
            print("Invalid input. Please use one of the following inputs:\n")
            print(valid_input)
        else:
            return user_entered


def get_response(options: list, **kwargs):
    for index, option in enumerate(options):
        print(str(index) + ". " + option[0])
        time.sleep(0.25)
    valid_inputs = [str(num) for num in range(len(options))]
    try:
        option_index = int(get_input(valid_inputs))
    except ValueError:
        print("Sorry to hear that, goodbye then...")
        sys.exit(0)
    return options[option_index][1]


def story_flow(story_dict: dict, response=False):
    curr_page = 1
    while curr_page is not None:
        page = story_dict.get(curr_page, None)
        if page is None:
            break
        display_page_text(page['Text'])
        if len(page['Options']) == 0:
            break
        curr_page = get_response(page['Options'])
        if response:
            return curr_page


def read_story(story_file, response=False):
    with open(story_file, 'rb') as file:
        story_dict = pickle.load(file)
    if not response:
        story_flow(story_dict)
    else:
        return story_flow(story_dict, response=response)
