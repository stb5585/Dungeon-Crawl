###########################################
""" combat manager """

# Imports
import os
import random


# Functions
def initiative(player_char, enemy):
    """
    Determine who goes char using each character's dexterity plus luck
    """
    p_chance = player_char.dex + player_char.check_mod('luck', luck_factor=10)
    e_chance = enemy.dex + enemy.check_mod('luck', luck_factor=10)
    total_chance = p_chance + e_chance
    chance_list = [p_chance / total_chance, e_chance / total_chance]
    choice = random.choices([player_char, enemy], chance_list)[0]
    return choice


def battle(player_char, enemy):
    """
    Function that controls combat
    """
    flee = False
    char = initiative(player_char, enemy)
    if char == player_char:
        opponent = enemy
    else:
        opponent = player_char
    tile = player_char.world_dict[(player_char.location_x, player_char.location_y, player_char.location_z)]
    combat = True
    while all([player_char.is_alive(), enemy.is_alive()]):
        available_actions = tile.available_actions(player_char)
        os.system('cls' if os.name == 'nt' else 'clear')
        player_char.minimap()
        print(tile.intro_text(player_char))
        if player_char.cls == 'Inquisitor' or player_char.cls == 'Seeker' or \
                'Vision' in player_char.equipment['Pendant']().mod:
            print(enemy)
        print(player_char.__str__())
        if not all([char.status_effects['Stun'][0], char.status_effects['Sleep'][0]]):
            while True:
                action = char.options(action_list=available_actions)
                valid_entry, combat, flee = char.combat_turn(opponent, action, combat, tile=tile)
                if valid_entry:
                    break
                else:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    available_actions = tile.available_actions(player_char)
                    player_char.minimap()
                    print(tile.intro_text(player_char))
                    if (player_char.cls == 'Inquisitor' or player_char.cls == 'Seeker' or
                            'Vision' in player_char.equipment['Pendant']().mod):
                        print(enemy)
                    print(player_char.__str__())

        # Familiar's turn
        if combat:
            char.familiar_turn(opponent)

        if not opponent.is_alive():
            if 'Resurrection' in list(char.spellbook['Spells'].keys()) and \
                    abs(char.health) <= char.mana:
                opponent.spellbook['Spells']['Resurrection']().cast(opponent, char)
                combat = True
            else:
                combat = False

        if not combat:
            break
        else:
            char.statuses()
            char.special_effects(opponent)
            if char == player_char:
                char = enemy
                opponent = player_char
            else:
                char = player_char
                opponent = enemy

    player_char.state = 'normal'
    player_char.end_combat(enemy, tile, flee=flee)
    if not flee:
        input("Press enter to continue")
