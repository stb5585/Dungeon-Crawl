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
    if player.cls == 'RANGER' or player.cls == 'SEEKER':
        print(enemy())
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
                if action_input == action.hotkey and action_input != 'f' and action_input != 'x'\
                        and action_input != 'k':
                    player.do_action(action, **action.kwargs)
                    valid_entry = True
                    break
            if action_input == 'f':
                flee = character.Player.flee(player, enemy)
                valid_entry = True
            if action_input == 'x':
                i = 0
                spell_list = []
                for entry in player.spellbook['Spells']:
                    if player.spellbook['Spells'][entry]().cost <= player.mana:
                        spell_list.append((str(entry)+'  '+str(player.spellbook['Spells'][entry]().cost), i))
                        i += 1
                if len(spell_list) == 0:
                    print("You do not have enough mana to cast any spells. You attack instead.")
                    player.weapon_damage(enemy)
                else:
                    spell_index = storyline.get_response(spell_list)
                    spell = player.spellbook['Spells'][spell_list[spell_index][0].split('  ')[0]]
                    player.cast_spell(enemy, spell)
                valid_entry = True
            if action_input == 'k':
                i = 0
                skill_list = []
                for entry in player.spellbook['Skills']:
                    if player.spellbook['Skills'][entry]().cost <= player.mana:
                        if player.spellbook['Skills'][entry]().name == 'Smoke Screen' and 'Boss' in tile.intro_text():
                            continue
                        else:
                            skill_list.append((str(entry)+'  '+str(player.spellbook['Skills'][entry]().cost), i))
                            i += 1
                if len(skill_list) == 0:
                    print("You do not have enough mana to use any skills. You attack instead.")
                    player.weapon_damage(enemy)
                else:
                    while True:
                        skill_index = storyline.get_response(skill_list)
                        skill = player.spellbook['Skills'][skill_list[skill_index][0].split('  ')[0]]
                        if skill().name == 'Smoke Screen' and 'Boss' not in tile.intro_text():
                            player.mana -= skill().cost
                            flee = character.Player.flee(player, enemy, smoke=True)
                            break
                        elif skill().name == 'Smoke Screen' and 'Boss' in tile.intro_text():
                            print("You cannot flee from boss fights!")
                        else:
                            player.use_ability(enemy, skill)
                            break
                valid_entry = True
            if flee:
                """Moves the player randomly to an adjacent tile"""
                available_moves = tile.adjacent_moves()
                r = random.randint(0, len(available_moves) - 1)
                player.do_action(available_moves[r])
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
