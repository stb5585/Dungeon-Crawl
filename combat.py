###########################################
""" combat manager """

# Imports
import os
import random
import time


# Functions
def combat_text(player_char, enemy, tile):
    """

    """

    if 'Boss' in str(tile):
        print("""
                Boss Fight!""")
    if not enemy.invisible:
        print(f"""
    {player_char.name} is attacked by a {enemy.name}.
        
        """)
    else:
        print(f"""
    An unseen entity is attacking {player_char.name}.
        
        """)
    if any([player_char.cls.name == 'Inquisitor', player_char.cls.name == 'Seeker',
            'Vision' in player_char.equipment['Pendant']().mod]) and \
            'Boss' not in str(tile):
        print(str(enemy))
    print(str(player_char))


def initiative(player_char, enemy):
    """
    Determine who goes char using each character's dexterity plus luck
    """

    p_chance = player_char.stats.dex + player_char.check_mod('luck', luck_factor=10)
    e_chance = enemy.stats.dex + enemy.check_mod('luck', luck_factor=10)
    total_chance = p_chance + e_chance
    chance_list = [p_chance / total_chance, e_chance / total_chance]
    first = random.choices([player_char, enemy], chance_list)[0]
    second = player_char if first == enemy else enemy
    return first, second


def battle(player_char, enemy):
    """
    Function that controls combat
    """

    flee = False
    first, second = initiative(player_char, enemy)
    tile = player_char.world_dict[(player_char.location_x, player_char.location_y, player_char.location_z)]
    combat = True
    while all([player_char.is_alive(), enemy.is_alive()]):
        available_actions = tile.available_actions(player_char)
        os.system('cls' if os.name == 'nt' else 'clear')
        player_char.minimap()
        combat_text(player_char, enemy, tile)
        if not any([first.status_effects['Prone'].active,
                    first.status_effects['Stun'].active,
                    first.status_effects['Sleep'].active]):
            while True:
                action = first.options(action_list=available_actions)
                valid_entry, combat, flee = first.combat_turn(second, action, combat)
                if valid_entry:
                    break
                os.system('cls' if os.name == 'nt' else 'clear')
                available_actions = tile.available_actions(player_char)
                player_char.minimap()
                combat_text(player_char, enemy, tile)
        else:
            if first.status_effects['Stun'].active:
                text = "stunned"
            elif first.status_effects['Sleep'].active:
                text = "asleep"
            else:
                text = "prone"
            print(f"{first.name} is {text}.")

        # Familiar's turn
        if combat:
            first.familiar_turn(second)

        if not second.is_alive():
            if 'Resurrection' in first.spellbook['Spells'] and \
                    abs(first.health.current) <= first.mana.current:
                second.spellbook['Spells']['Resurrection']().cast(second, target=first)
                combat = True
            else:
                combat = False

        if not combat:
            break
        first.statuses()
        first.special_effects(second)
        input("Press enter to continue")
        if first == player_char:
            first = enemy
            second = player_char
        else:
            first = player_char
            second = enemy

    win = player_char.is_alive()
    player_char.end_combat(enemy, tile, flee=flee)
    if not flee:
        if win:
            input("Press enter to continue")
    else:
        win = False
    return win
