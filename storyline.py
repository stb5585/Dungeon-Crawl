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
            print("Invalid input. Please use one \
                   of the following inputs:\n")
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

background = "Following the War of The Races, the land of Mordor, shrouded in darkness for hundreds of years, started" \
             " to thrive and attract settlers and adventurers from far and wide.  Trading posts became towns and towns" \
             " flourished into cities. Today there are hundreds of cities in the land of Mordor. The largest of these " \
             "cities is Marlith, which was built on the ruins of the ancient city of Rohin, known to historians as " \
             "'Dejenol', which translates to “City of the Mines”. It was at this location that vast Mines of Dejenol " \
             "were built - over fifteen hundred years ago by the Dwarven inhabitants of Rohin. These Mines were created" \
             " for the extraction of precious metals, including Platinum, Adamantite, Mithril, and Gold, as well as " \
             "necessities like Iron and Copper. The facts surrounding the sealing of the Mines and the fall of Rohin " \
             "are shrouded in mystery, but are believed to be mostly accurate. Legends have it that Rohin was the most" \
             " powerful and wealthy city in all of ancient Mordor, owing most of its wealth to the minerals and ores " \
             "taken from the Mines. As the metals were depleted on the upper levels, the miners dug deeper to find new" \
             " sources. Over a period of centuries, the Mines became so deep that it could take several days to " \
             "descend and work in the lower levels. As best as can be determined, somewhere on a lower level, a floor " \
             "gave way. It was from this location that foul creatures began to appear, killing everything in sight. " \
             "" \
             "As word reached the city of this catastrophe, search parties were organized using only the best and most" \
             " skilled miners. The few survivors recovered from the lower levels had glazed and terrified looks and " \
             "referred to the Mines simply as “The Doorway to Hell”. From that time on, most of the search parties that" \
             " entered the Mines were never seen again. Those who did return told stories of creatures and happenings " \
             "that were so mystical and magical as to be nearly unbelievable. " \
             "" \
             "In a matter of days, strange events were occurring closer and closer to the entrance of the Mines and " \
             "the city. It was then, that a decision to close the Mines was made and a massive door was fashioned from" \
             " a combination of ElvenOak and Adamantite, the only combination believed strong enough to entomb the " \
             "creatures and the magic of the Mines. Once the Mines were sealed, a lack of work and commerce caused the" \
             " population of Dejenol to dwindle. It was during this period that an evil wizard accompanied by an band " \
             "of thieves blew the door from its mounts and stole it for the valuable Adamantite." \
             "" \
             "The Wizard and his thieves were caught and the remains of the door returned, but the damage had been " \
             "done. Creatures had escaped from the Mines and built up their numbers, hiding in the forests near the " \
             "city. The city elders decided to punish the thieves and their master by locking them inside the Mines. " \
             "This time the door was sealed with magic so strong that no-one would be able to open it without the " \
             "secret knowledge of the spell used to seal it." \
             "" \
             "It was after the Mines were once again magically sealed that a great battle began between the inhabitants" \
             " of Dejenol and the creatures that had escaped. Due to the lack of warriors in Dejenol, a summons was " \
             "sent out to all of the lands. From this calling, the most skilled warriors and magicians came from all " \
             "over Mordor and from foreign regions as well.  Many of the creatures from the Mines were not susceptible" \
             " to normal combat. The battles for Dejenol lasted 2 years, during which the city was destroyed, the " \
             "entrance to the Mines lost, and most of the inhabitants were killed or driven mad. A few strong souls did" \
             " survive and lore has it that they guarded the entrance to the Mines until they died, spending their " \
             "final days recording what they knew, thought they knew, or had heard about the Mines and the creatures " \
             "within. Those who have entered and returned speak of vast treasures, magical items, and unexplainable " \
             "occurrences. " \
             "" \
             "Over a thousand years passed before the entrance to the Mines was once again discovered. With this " \
             "discovery, the elders of Marlith began making preparations to open the Mines and explore its depths. " \
             "Scholars studied the manuscript remnants found near the Mines’ entrance to glean what knowledge they " \
             "could about the Mines from the ancient scribblings. Equipped with this knowledge, a limited number of " \
             "explorers were permitted inside the Mines. At first, many who ventured into the Mines were killed " \
             "instantly, despite being well equipped with the best weapons and magical skill. However, as the " \
             "explorers’ experiences of fighting, magic, and their knowledge of the Mines increased, so did their " \
             "chances of survival. With exploration came newer knowledge, and with this new knowledge came a healthy " \
             "respect for the long-lost Dwarves, who created this vast underground world, and for the creatures that " \
             "still dominated the dark Mines. In the past year, more explorers have ventured into the Mines than ever," \
             "eradicating the creatures they’ve encountered, and forcing the nastier monsters deeper into the " \
             "darkness." \
             "" \
             "It was around this time that a rumor began about a Prince of Devils, who was said to exist in the " \
             "deepest depths of the mines. At first, many believed the creature to be a myth, used purely to instill " \
             "fear into would-be explorers. Yet, those with magical powers who have astrally scanned the mines swear " \
             "that they sense the presence of a dark, evil, and powerful being." \
             "" \
             "Even though nothing more is known about this Prince of Devils, the guilds have decided to add the " \
             "destruction of the dark being to their list of goals - and for those who accomplish this task, they will" \
             " receive the greatest gift of all - Eternal life in the pages of history." \
             "" \
             "And now, having nearly run out of experienced explorers, a decision was made to train new adventurers to" \
             " survive in the Mines, hence the city elders formed The Guilds. The Guilds train “students” in the " \
             "skills and arts that are essential to surviving and prospering in the Mines. It is now up to these new " \
             "Guild members to explore and return with information about the mines, which have taken on a new name to " \
             "those who dare enter..." \
             "" \
             "The Depths of Dejenol."
