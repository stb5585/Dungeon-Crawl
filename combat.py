###########################################
""" combat manager """

# Imports
import random

import world
import actions
import character


# Functions
def battle(player, enemy):
    tile = world.tile_exists(player.location_x, player.location_y, player.location_z)
    print(tile.intro_text())
    available_actions = tile.available_actions()
    combat = True
    flee = False
    while combat:
        for action in available_actions:
            print(action)
        print(actions.Flee())
        action_input = input('Action: ')
        for action in available_actions:
            if action_input == action.hotkey and action_input != 'f':
                player.do_action(action, **action.kwargs)
                break
        if action_input == 'f':
            flee = character.Player.flee(player, enemy)
        if flee:
            """Moves the player randomly to an adjacent tile"""
            available_moves = tile.adjacent_moves()
            r = random.randint(0, len(available_moves) - 1)
            player.do_action(available_moves[r])
        if enemy.health <= 0 and enemy.name != 'Chest':
            print("You killed the {0.name}.".format(enemy))
            print("You gained %s experience." % enemy.experience)
            player.loot(enemy)
            player.experience += enemy.experience
            if player.experience >= 10 * player.level:
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
