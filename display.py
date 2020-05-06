###########################################
""" display window manager """

# Imports
import pygame
from pygame.locals import *
import sys
import numpy

import world
import races

pygame.init()

# Parameters
FPS = 60  # frames per second setting
fpsClock = pygame.time.Clock()

display_width = 1240
display_height = 755

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
AQUA = (0, 255, 255)
BLUE = (0, 0, 255)
FUCHSIA = (255, 0, 255)
GRAY = (128, 128, 128)
GREEN = (0, 128, 0)
LIME = (0, 255, 0)
MAROON = (128, 0, 0)
NAVYBLUE = (0, 0, 128)
OLIVE = (128, 128, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
SILVER = (192, 192, 192)
TEAL = (0, 128, 128)
YELLOW = (255, 255, 0)

# Setup game display
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Dungeon Crawl')  # sets title of window


# Event handling
class Input(object):
    """
    Wrapper for the pygame input module
    """

    def __init__(self, event, do_base_actions=True):
        self.event = event
        self.type = event.type
        self.handled = False

        if do_base_actions and self.base_actions():
            self.handled = True

    def base_actions(self):

        if self.is_quit():
            sys.exit()

    def is_user_action(self):
        return self.event.type == KEYDOWN

    def _is_key_event(self):
        return hasattr(self.event, 'key')

    def _has_key(self, keynames):

        if not self._is_key_event():
            return False

        if len(keynames) == 1 and type(keynames[0]) is tuple:
            keynames = keynames[0]

        for key in keynames:
            if self.event.key == _get_key(key):
                return True

        return False

    def is_key(self, *keynames):
        return self._has_key(keynames)

    def is_down(self):
        return self.event.type == KEYDOWN

    def key_down(self, *keynames):

        if not self.is_down():
            return False

        if len(keynames) == 0:
            return True

        return self.is_key(keynames)

    def is_quit(self):
        return self.event.type == QUIT


def event_loop():
    """
    Generator which runs through the event loop, takes care of global events and yields the unhandled event objects.
    """

    for event in pygame.event.get():
        event_handle = Input(event)
        if event_handle.handled:
            continue
        yield event_handle


def _get_key(key):
    if type(key) is str:
        if key[:2] != 'K_':
            key = 'K_' + key

    return key


# Game Functions
def dungeon(player):
    """
    Draws the dungeon map with the player icon on top of it
    """
    map_array = numpy.zeros((10, 15))
    _world = world.world_return()
    world.load_tiles()
    level = player.location_z
    for tile in _world['World']:
        if level == tile[2]:
            tile_x, tile_y = tile[0], tile[1]
            if _world['World'][tile] is None:
                continue
            elif _world['World'][tile] is not None:
                try:
                    if 'stairs' in _world['World'][tile].intro_text():
                        map_array[tile_x][tile_y] = 125
                    else:
                        map_array[tile_x][tile_y] = 255
                except TypeError:
                    map_array[tile_x][tile_y] = 255
    surf = pygame.surfarray.make_surface(map_array)
    surf = pygame.transform.scale(surf, (650, 650))  # Scaled a bit.
    game_display.blit(surf, (50, 50))


def player_movement(player, room, available_options):
    """
    Controls the player movement (icon and location)
    """
    pygame.draw.rect(game_display, WHITE, (display_width / 2, 0, display_width / 2, display_height / 2), 3)
    room_text = pygame.font.SysFont(None, 140, bold=True, italic=True)
    room_surf, room_rect = text_objects(room.intro_text(), room_text, WHITE)
    room_rect.center = ((display_width / 4), (display_height / 4))
    game_display.blit(room_surf, room_rect)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == KEYDOWN:
            if event.key in available_options:
                player.get_event(event)

    game_display.fill(BLACK)
    dungeon(player)
    player.draw(game_display)
    pygame.display.update()
    fpsClock.tick(FPS)


def text_objects(text, font, text_color):
    text_surface = font.render(text, True, text_color)
    return text_surface, text_surface.get_rect()


def select_box(box_color, width, height, loc_x, loc_y):
    box = pygame.Surface((width, height))
    box.set_alpha(150)
    box.fill(box_color)
    game_display.blit(box, (loc_x, loc_y))


def text_list_return(text, text_len=40):
    text_list = ['']
    i = 0
    for letter in text:
        if letter != '\n':
            text_list[i] += letter
        if len(text_list[i]) > text_len and letter.isspace():
            i += 1
            text_list.append('')

    return text_list


def blit_multi_line_text(word_list, surface, x_loc=2, y_loc=1.5, font_size=40):
    """Blit words in a multi-line format"""
    text = pygame.font.SysFont(None, font_size, bold=True)
    for i, word in enumerate(word_list):
        word_surf, word_rect = text_objects(word, text, WHITE)
        word_rect.center = ((display_width / x_loc), (display_height / y_loc) + (i * 50))
        surface.blit(word_surf, word_rect)


def game_background(title=False):
    """Initializes background with dungeon image"""
    background = pygame.image.load('resources/menu_background.jpg')
    background = pygame.transform.scale(background, (display_width, display_height))
    back_rect = background.get_rect()
    game_display.blit(background, back_rect)
    if title:
        # set title logo
        title_text = pygame.font.SysFont(None, 140, bold=True, italic=True)
        title_surf, title_rect = text_objects('DUNGEON CRAWL', title_text, WHITE)
        title_rect.center = ((display_width / 2), (display_height / 3))
        game_display.blit(title_surf, title_rect)


def intro_menu(rect_y=50, option='NEW GAME', select=False):
    """Outlines the introduction menu (new game, load game or tutorial)"""
    while not select:
        game_background(title=True)

        # lists the menu options
        menu_list = ['NEW GAME', 'LOAD GAME', 'TUTORIAL']
        blit_multi_line_text(menu_list, game_display)

        # defines the highlight box that will move over the options
        select_box(BLACK, (display_height / 3), (display_height / 15), (display_width / 2.5),
                   (display_height / 1.75) + rect_y)

        # event_loop()
        for event in pygame.event.get():
            print(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if not select:
                if event.type == KEYDOWN:
                    # Moves select_box over options and exits when enter is chosen
                    if option == 'NEW GAME':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'LOAD GAME'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y += 100
                            option = 'TUTORIAL'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'LOAD GAME':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'TUTORIAL'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'NEW GAME'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'TUTORIAL':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y -= 100
                            option = 'NEW GAME'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'LOAD GAME'
                        if event.key == K_RETURN:
                            select = True

        pygame.display.update()
        fpsClock.tick(FPS)
    return option


def race_description(race):
    race_text = ''
    if race == 'HUMAN':
        race_text = races.Human().description
    elif race == 'ELF':
        race_text = races.Elf().description
    elif race == 'GIANT':
        race_text = races.Giant().description
    elif race == 'GNOME':
        race_text = races.Gnome().description
    elif race == 'DWARF':
        race_text = races.Dwarf().description

    race_text_list = text_list_return(race_text)

    return race_text_list


def race_menu(race_dict, rect_y=50, option='HUMAN', select=False):
    """Defines the race menu for creating new characters"""
    race_list = list(race_dict.keys())
    race_list.append('GO BACK')
    while True:
        game_background()

        # lists the menu options
        blit_multi_line_text(race_list, game_display, y_loc=1.675)

        # defines the highlight box that will move over the options
        select_box(BLACK, (display_height / 3), (display_height / 15), (display_width / 2.5),
                   (display_height / 2) + rect_y)

        # Select your race text
        text = pygame.font.SysFont(None, 40, bold=True)
        word_surf, word_rect = text_objects('CHOOSE YOUR RACE', text, WHITE)
        word_rect.center = ((display_width / 2), (display_height / 1.50) - 100)
        game_display.blit(word_surf, word_rect)

        for event in pygame.event.get():
            print(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if not select:
                if event.type == KEYDOWN:
                    # Moves select_box over options and exits when enter is chosen
                    if option == 'HUMAN':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'ELF'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y += 250
                            option = 'GO BACK'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'ELF':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'GIANT'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'HUMAN'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'GIANT':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'GNOME'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'ELF'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'GNOME':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'DWARF'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'GIANT'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'DWARF':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'GO BACK'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'GNOME'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'GO BACK':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y -= 250
                            option = 'HUMAN'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'DWARF'
                        if event.key == K_RETURN:
                            select = True

        pygame.display.update()
        fpsClock.tick(FPS)
        if select:
            break
    if option == 'GO BACK':
        return False
    return option


def class_menu(class_dict, rect_y=50, option='WARRIOR', select=False):
    """Defines the class menu for creating new characters"""
    class_list = list(class_dict.keys())
    while True:
        game_background()

        # lists the menu options
        blit_multi_line_text(class_list, game_display)

        # defines the highlight box that will move over the options
        select_box(BLACK, (display_height / 3), (display_height / 15), (display_width / 2.5),
                   (display_height / 1.75) + rect_y)

        # Select your class text
        text = pygame.font.SysFont(None, 40, bold=True)
        word_surf, word_rect = text_objects('NOW CHOOSE YOUR CLASS', text, WHITE)
        word_rect.center = ((display_width / 2), (display_height / 1.50) - 50)
        game_display.blit(word_surf, word_rect)

        for event in pygame.event.get():
            print(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if not select:
                if event.type == KEYDOWN:
                    # Moves select_box over options and exits when enter is chosen
                    if option == 'WARRIOR':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'MAGE'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y += 100
                            option = 'FOOTPAD'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'MAGE':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'FOOTPAD'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'WARRIOR'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'FOOTPAD':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y -= 100
                            option = 'WARRIOR'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'MAGE'
                        if event.key == K_RETURN:
                            select = True

        pygame.display.update()
        fpsClock.tick(FPS)
        if select:
            break

    return option


def confirm_menu(rect_y=100, y_loc=5, additional_text=None, text_len=60, font_size=30, option='NO', select=False):
    """Defines the function for confirming selections"""
    confirm_list = ['YES', 'NO']
    while True:
        game_background()
        # lists the menu options
        blit_multi_line_text(confirm_list, game_display)

        # defines the highlight box that will move over the options
        select_box(BLACK, (display_height / 3), (display_height / 15), (display_width / 2.5),
                   (display_height / 1.75) + rect_y)

        text = pygame.font.SysFont(None, 40, bold=True)
        word_surf, word_rect = text_objects('ARE YOU SURE?', text, WHITE)
        word_rect.center = ((display_width / 2), (display_height / 1.50) - 50)
        game_display.blit(word_surf, word_rect)

        if additional_text is not None:
            add_text = text_list_return(additional_text, text_len=text_len)
            blit_multi_line_text(add_text, game_display, y_loc=y_loc, font_size=font_size)

        for event in pygame.event.get():
            print(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if not select:
                if event.type == KEYDOWN:
                    # Moves select_box over options and exits when enter is chosen
                    if option == 'YES':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'NO'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y += 50
                            option = 'NO'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'NO':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y -= 50
                            option = 'YES'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'YES'
                        if event.key == K_RETURN:
                            select = True

        pygame.display.update()
        fpsClock.tick(FPS)
        if select:
            return option


def name_input(select=False):
    """Defines the function to input text (i.e. for entering name of character)"""
    name_text = ''
    i = 0
    while True:
        game_background()

        text = pygame.font.SysFont(None, 40, bold=True)
        word_surf, word_rect = text_objects('ENTER YOUR NAME', text, WHITE)
        word_rect.center = ((display_width / 2), (display_height / 1.50) - 50)
        game_display.blit(word_surf, word_rect)

        # Print name text
        name_surf, name_rect = text_objects(name_text, text, WHITE)
        name_rect.center = ((display_width / 2), (display_height / 1.50))
        game_display.blit(name_surf, name_rect)

        for event in pygame.event.get():
            print(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    select = True
                elif event.key == K_BACKSPACE:
                    if name_text != '':
                        name_text = name_text[:-1]
                    if i != 0:
                        i -= 1
                elif len(name_text) > 10:
                    pass
                elif event.unicode.isalpha():
                    name_text += event.unicode.upper()
                    i += 1

        pygame.display.update()
        fpsClock.tick(FPS)

        if select:
            return name_text


def town_menu(rect_y=-25, select=False):
    town_options = ['BLACKSMITH', 'ARMORY', 'ALCHEMIST', 'CHURCH', 'DUNGEON', 'STATUS']
    option = town_options[0]
    while True:
        # set town background
        background = pygame.image.load('resources/town_background.jpg')
        background = pygame.transform.scale(background, (display_width, display_height))
        back_rect = background.get_rect()
        game_display.blit(background, back_rect)

        text = pygame.font.SysFont(None, 40, bold=True)
        word_surf, word_rect = text_objects('WELCOME TO THE TOWN OF SILVANA!', text, WHITE)
        word_rect.center = ((display_width / 2), (display_height / 2) - 150)
        game_display.blit(word_surf, word_rect)
        text = pygame.font.SysFont(None, 40, bold=True)
        word_surf, word_rect = text_objects('WHERE WOULD YOU LIKE TO GO?', text, WHITE)
        word_rect.center = ((display_width / 2), (display_height / 2) - 100)
        game_display.blit(word_surf, word_rect)

        # defines the highlight box that will move over the options
        select_box(BLACK, (display_height / 3), (display_height / 15), (display_width / 2.5),
                   (display_height / 2) + rect_y)

        # lists the menu options
        blit_multi_line_text(town_options, game_display, y_loc=2)

        for event in pygame.event.get():
            print(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if not select:
                if event.type == KEYDOWN:
                    if option == 'BLACKSMITH':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'ARMORY'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y += 250
                            option = 'STATUS'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'ARMORY':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'ALCHEMIST'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'BLACKSMITH'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'ALCHEMIST':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'CHURCH'
                        if event.key == pygame.K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'ARMORY'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'CHURCH':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'DUNGEON'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'ALCHEMIST'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'DUNGEON':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'STATUS'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'CHURCH'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'STATUS':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y -= 250
                            option = 'BLACKSMITH'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'DUNGEON'
                        if event.key == K_RETURN:
                            select = True

        pygame.display.update()
        fpsClock.tick(FPS)
        if select:
            return option


def load_menu(load_list, rect_y=50, select=False):
    """
    Function that shows characters to load; limit number of save files to 5
    """
    load_menu_list = ['-EMPTY-', '-EMPTY-', '-EMPTY-', '-EMPTY-', '-EMPTY-', 'GO BACK']
    i = 0
    for l_file in load_list:
        load_menu_list[i] = l_file.split('.save')[0]
        i += 1
    option = 0
    while True:
        game_background()

        # lists the menu options
        blit_multi_line_text(load_menu_list, game_display, y_loc=1.675)

        # defines the highlight box that will move over the options
        select_box(BLACK, (display_height / 3), (display_height / 15), (display_width / 2.5),
                   (display_height / 2) + rect_y)

        # Select your race text
        text = pygame.font.SysFont(None, 40, bold=True)
        word_surf, word_rect = text_objects('CHOOSE A FILE', text, WHITE)
        word_rect.center = ((display_width / 2), (display_height / 1.50) - 100)
        game_display.blit(word_surf, word_rect)

        for event in pygame.event.get():
            print(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if not select:
                if event.type == KEYDOWN:
                    if option == 0:
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 1
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y += 250
                            option = 5
                        if event.key == K_RETURN:
                            select = True
                    elif option == 1:
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 0
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 2
                        if event.key == K_RETURN:
                            select = True
                    elif option == 2:
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 3
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 1
                        if event.key == K_RETURN:
                            select = True
                    elif option == 3:
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 4
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 2
                        if event.key == K_RETURN:
                            select = True
                    elif option == 4:
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 3
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 5
                        if event.key == K_RETURN:
                            select = True
                    elif option == 5:
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y -= 250
                            option = 0
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 4
                        if event.key == K_RETURN:
                            select = True

        pygame.display.update()
        fpsClock.tick(FPS)
        if select:
            break

    if option == 5 or load_menu_list[option] == '-EMPTY-':
        return False
    return option


def status_menu(player, status_list, equip_list, rect_y=0, option='EQUIP', select=False):
    """Function that shows the player's status and inventory"""
    j = 0
    while True:
        game_display.fill(NAVYBLUE)
        pygame.draw.rect(game_display, WHITE, (0, 0, display_width / 2, display_height), 3)  # width = 3
        pygame.draw.rect(game_display, WHITE, (display_width / 2, 0, display_width / 2, display_height), 3)  # width = 3

        blit_multi_line_text(status_list, game_display, x_loc=4, y_loc=6)
        blit_multi_line_text(equip_list, game_display, x_loc=(4 / 3), y_loc=6)

        # defines the highlight box that will move over the options
        select_box(BLACK, (display_height / 3), (display_height / 15), (display_width / 1.54),
                   (display_height / 1.58) + rect_y)

        screen_options = ['EQUIP', 'SPELLBOOK', 'USE ITEM', 'EXIT']
        blit_multi_line_text(screen_options, game_display, x_loc=(4 / 3), y_loc=1.5)
        for event in pygame.event.get():
            print(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if not select:
                if event.type == KEYDOWN:
                    # Moves select_box over options and exits when enter is chosen
                    if option == 'EQUIP':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'SPELLBOOK'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y += 150
                            option = 'EXIT'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'SPELLBOOK':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'USE ITEM'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'EQUIP'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'USE ITEM':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y += 50
                            option = 'EXIT'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'SPELLBOOK'
                        if event.key == K_RETURN:
                            select = True
                    elif option == 'EXIT':
                        if event.key == K_DOWN or event.key == ord('s'):
                            rect_y -= 150
                            option = 'EQUIP'
                        if event.key == K_UP or event.key == ord('w'):
                            rect_y -= 50
                            option = 'USE ITEM'
                        if event.key == K_RETURN:
                            select = True

        # defines the highlight box that is around the player icon in menu
        player_box = pygame.Surface(((display_height / 7), (display_height / 6)))
        player_box.fill(WHITE)
        game_display.blit(player_box, (50, 50))
        pygame.draw.rect(game_display, YELLOW, (50, 50, (display_height / 7), (display_height / 6)), 3)

        player.draw(game_display, menu=True, i=j)
        j += 1
        if j // 20 > 5:
            j = 0
        pygame.display.update()
        fpsClock.tick(FPS)
        if select:
            return option


def menu_creator(menu_list, rect_y):
    """
    Function to create screen menus
    """
    
    return rect_y
