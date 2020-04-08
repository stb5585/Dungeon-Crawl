###########################################
""" combat manager """

# Imports
import random

import world
import actions
import character
import storyline


# Functions
def battle(player, enemy):
    tile = world.tile_exists(player.location_x, player.location_y, player.location_z)
    print(tile.intro_text())
    available_actions = tile.available_actions()
    combat = True
    flee = False
    while combat:
        valid_entry = False
        print("Health: %d/%d  Mana: %d/%d" % (player.health, player.health_max, player.mana, player.mana_max))
        while True:
            for action in available_actions:
                print(action)
            if enemy.name != 'Chest' and 'Boss' not in tile.intro_text():
                print(actions.Flee())
            action_input = input('Action: ').lower()
            for action in available_actions:
                if action_input == action.hotkey and action_input != 'f' and action_input != 'x':
                    player.do_action(action, **action.kwargs)
                    valid_entry = True
                    break
            if action_input == 'f':
                flee = character.Player.flee(player, enemy)
            if flee:
                """Moves the player randomly to an adjacent tile"""
                available_moves = tile.adjacent_moves()
                r = random.randint(0, len(available_moves) - 1)
                player.do_action(available_moves[r])
                valid_entry = True
            if action_input == 'x':
                i = 0
                spell_list = []
                for entry in player.spellbook:
                    if player.spellbook[entry]().cost <= player.mana:
                        spell_list.append((str(entry)+'  '+str(player.spellbook[entry]().cost), i))
                        i += 1
                if len(spell_list) == 0:
                    print("You cannot cast any spells. You attack instead.")
                    player.weapon_damage(enemy)
                else:
                    spell_index = storyline.get_response(spell_list)
                    spell = player.spellbook[spell_list[spell_index][0].split('  ')[0]]
                    if spell().cost > player.mana:
                        print("You do not have enough mana to cast %s." % spell().name)
                        print("You attack instead!")
                        player.weapon_damage(enemy)
                    else:
                        player.special(enemy, spell)
                valid_entry = True
            if valid_entry:
                break
        if enemy.health <= 0 and enemy.name != 'Chest':
            print("You killed the {0.name}.".format(enemy))
            print("You gained %s experience." % enemy.experience)
            player.loot(enemy)
            player.experience += enemy.experience
            if player.experience >= (25**player.pro_level) * player.level:
                player.level_up()
            player.state = 'normal'
            combat = False
        elif player.state == 'normal' or enemy.name == 'Chest':
            combat = False
        else:
            enemy.do_damage(player)
        if player.health <= 0:
            print("You were slain by the {0.name}.".format(enemy))
            combat = False
    player.state = 'normal'
