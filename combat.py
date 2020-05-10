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
    if player.cls == 'INQUISITIVE' or player.cls == 'SEEKER' and 'Chest' not in enemy.name:
        print(enemy)
    tile = world.tile_exists(player.location_x, player.location_y, player.location_z)
    print(tile.intro_text())
    available_actions = tile.available_actions(player)
    combat = True
    flee = False
    while combat:
        valid_entry = False
        print("Health: %d/%d  Mana: %d/%d" % (player.health, player.health_max, player.mana, player.mana_max))
        if player.status_effects['Stun'][0]:
            player.status_effects['Stun'][1] -= 1
            if player.status_effects['Stun'][1] == 0:
                player.status_effects['Stun'][0] = False
                print("You are no longer stunned.")
        else:
            while True:
                for action in available_actions:
                    print(action)
                if 'Chest' not in enemy.name and 'Boss' not in tile.intro_text():
                    print(actions.Flee())
                action_input = input('Action: ').lower()
                for action in available_actions:
                    if action_input == action.hotkey and 'Move' in action.name:
                        player.do_action(action, **action.kwargs)
                        combat = False
                        player.state = 'normal'
                        valid_entry = True
                        break
                    elif action_input == action.hotkey and action_input != 'f' and action_input != 'x' \
                            and action_input != 'k' and action_input != 'p':
                        player.do_action(action, **action.kwargs)
                        valid_entry = True
                        break
                if action_input == 'p':
                    if player.use_item(enemy=enemy):
                        valid_entry = True
                if action_input == 'f':
                    flee = character.Player.flee(player, enemy)
                    valid_entry = True
                if action_input == 'x':
                    i = 0
                    spell_list = []
                    for entry in player.spellbook['Spells']:
                        if player.spellbook['Spells'][entry]().cost <= player.mana:
                            spell_list.append((str(entry) + '  ' + str(player.spellbook['Spells'][entry]().cost), i))
                            i += 1
                    if len(spell_list) == 0:
                        print("You do not have enough mana to cast any spells.")
                    else:
                        spell_list.append(('Go back', i))
                        spell_index = storyline.get_response(spell_list)
                        if spell_list[spell_index][0] == 'Go back':
                            continue
                        else:
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
                            elif player.spellbook['Skills'][entry]().name == 'Lockpick' and enemy.name != 'Locked Chest':
                                continue
                            elif player.spellbook['Skills'][entry]().name == 'Shield Slam' and \
                                    player.equipment['OffHand']().subtyp != 'Shield':
                                continue
                            elif enemy.name != 'Locked Chest':
                                skill_list.append((str(entry) + '  ' + str(player.spellbook['Skills'][entry]().cost), i))
                                i += 1
                            elif player.spellbook['Skills'][entry]().name == 'Lockpick' and enemy.name == 'Locked Chest':
                                skill_list.append((str(entry) + '  ' + str(player.spellbook['Skills'][entry]().cost), i))
                                i += 1
                    if len(skill_list) == 0 and enemy.name != 'Locked Chest':
                        print("You do not have enough mana to use any skills.")
                    else:
                        skill_list.append(('Go back', i))
                        skill_index = storyline.get_response(skill_list)
                        if skill_list[skill_index][0] == 'Go back':
                            continue
                        else:
                            skill = player.spellbook['Skills'][skill_list[skill_index][0].split('  ')[0]]
                            while True:
                                if skill().name == 'Smoke Screen':
                                    player.mana -= skill().cost
                                    flee = character.Player.flee(player, enemy, smoke=True)
                                elif skill().name == 'Multi-Cast':
                                    j = 0
                                    while j < skill().cast:
                                        spell_list = []
                                        i = 0
                                        for entry in player.spellbook['Spells']:
                                            if player.spellbook['Spells'][entry]().cost <= player.mana:
                                                spell_list.append(
                                                    (str(entry) + '  ' + str(player.spellbook['Spells'][entry]().cost), i))
                                                i += 1
                                        if len(spell_list) == 0:
                                            print("You do not have enough mana to cast any spells.")
                                            break
                                        spell_index = storyline.get_response(spell_list)
                                        spell = player.spellbook['Spells'][spell_list[spell_index][0].split('  ')[0]]
                                        player.cast_spell(enemy, spell)
                                        j += 1
                                        if enemy.health < 1:
                                            break
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
        if player.status_effects['Poison'][0]:
            player.status_effects['Poison'][1] -= 1
            poison_damage = player.status_effects['Poison'][2]
            poison_damage -= random.randint(0, player.con)
            if poison_damage > 0:
                poison_damage = random.randint(poison_damage // 2, poison_damage)
                player.health -= poison_damage
                print("The poison damages %s for %s health points." % (player.name, poison_damage))
            else:
                print("You resisted the poison.")
            if player.status_effects['Poison'][1] == 0:
                player.status_effects['Poison'][0] = False
                print("You are free from the poison.")
        if player.status_effects['DOT'][0]:
            player.status_effects['DOT'][1] -= 1
            dot_damage = player.status_effects['DOT'][2]
            dot_damage -= random.randint(0, player.wisdom)
            if dot_damage > 0:
                dot_damage = random.randint(dot_damage // 2, dot_damage)
                player.health -= dot_damage
                print("The magic damages %s for %s health points." % (player.name, dot_damage))
            else:
                print("You resisted the spell.")
            if player.status_effects['DOT'][1] == 0:
                player.status_effects['DOT'][0] = False
        if player.status_effects['Doom'][0]:
            player.status_effects['Doom'][1] -= 1
            if player.status_effects['Doom'][1] == 0:
                player.health = 0

        # Enemies turn
        if enemy.health <= 0 and 'Chest' not in enemy.name:
            print("You killed the %s." % enemy.name)
            print("You gained %s experience." % enemy.experience)
            player.loot(enemy)
            player.experience += enemy.experience
            if player.experience >= (25 ** player.pro_level) * player.level:
                player.level_up()
            player.state = 'normal'
            combat = False
        elif player.state == 'normal' or 'Chest' in enemy.name:
            combat = False
        elif enemy.status_effects['Stun'][0]:
            enemy.status_effects['Stun'][1] -= 1
            if enemy.status_effects['Stun'][1] == 0:
                enemy.status_effects['Stun'][0] = False
                print("The enemy is no longer stunned.")
        else:
            enemy_spell_list = []
            enemy_skill_list = []
            for entry in enemy.spellbook['Spells']:
                enemy_spell_index = enemy.spellbook['Spells'].index(entry)
                if enemy.spellbook['Spells'][enemy_spell_index]().cost <= enemy.mana:
                    enemy_spell_list.append(entry)
            for entry in enemy.spellbook['Skills']:
                enemy_skill_index = enemy.spellbook['Skills'].index(entry)
                if enemy.spellbook['Skills'][enemy_skill_index]().cost <= enemy.mana:
                    enemy_skill_list.append(entry)
            if len(enemy_spell_list) > 0 and len(enemy_skill_list) > 0:
                cast = random.randint(0, 2)
                if cast == 0:
                    enemy_spell = enemy_spell_list[random.randint(0, len(enemy_spell_list) - 1)]
                    enemy.cast_spell(player, enemy_spell)
                elif cast == 1:
                    enemy_skill = enemy_skill_list[random.randint(0, len(enemy_skill_list) - 1)]
                    enemy.use_ability(player, enemy_skill)
                else:
                    enemy.weapon_damage(player)
            elif len(enemy_spell_list) > 0:
                cast = random.randint(0, 1)
                if cast:
                    enemy_spell = enemy_spell_list[random.randint(0, len(enemy_spell_list) - 1)]
                    enemy.cast_spell(player, enemy_spell)
                else:
                    enemy.weapon_damage(player)
            elif len(enemy_skill_list) > 0:
                cast = random.randint(0, 1)
                if cast:
                    enemy_skill = enemy_skill_list[random.randint(0, len(enemy_skill_list) - 1)]
                    enemy.use_ability(player, enemy_skill)
                else:
                    enemy.weapon_damage(player)
            else:
                enemy.weapon_damage(player)
            if enemy.status_effects['Poison'][0]:
                enemy.status_effects['Poison'][1] -= 1
                poison_damage = enemy.status_effects['Poison'][2]
                poison_damage -= random.randint(0, enemy.con)
                if poison_damage > 0:
                    poison_damage = random.randint(poison_damage // 2, poison_damage)
                    enemy.health -= poison_damage
                    print("The poison damages %s for %s health points." % (enemy.name, poison_damage))
                else:
                    print("The enemy resisted the poison.")
                if enemy.status_effects['Poison'][1] == 0:
                    enemy.status_effects['Poison'][0] = False
            if enemy.status_effects['DOT'][0]:
                enemy.status_effects['DOT'][1] -= 1
                dot_damage = enemy.status_effects['DOT'][2]
                dot_damage -= random.randint(0, enemy.wisdom)
                if dot_damage > 0:
                    dot_damage = random.randint(dot_damage // 2, dot_damage)
                    enemy.health -= dot_damage
                    print("The magic damages %s for %s health points." % (enemy.name, dot_damage))
                else:
                    print("The enemy resisted the spell.")
                if enemy.status_effects['DOT'][1] == 0:
                    enemy.status_effects['DOT'][0] = False
            if enemy.status_effects['Doom'][0]:
                enemy.status_effects['DOT'][1] -= 1
                if enemy.status_effects['DOT'][1] == 0:
                    enemy.health = 0
            if enemy.health <= 0 and 'Chest' not in enemy.name:
                print("%s killed the %s." % (player.name, enemy.name))
                print("You gained %s experience." % enemy.experience)
                player.loot(enemy)
                player.experience += enemy.experience
                if player.experience >= (25 ** player.pro_level) * player.level:
                    player.level_up()
                player.state = 'normal'
                combat = False
        if player.health <= 0:
            print("You were slain by the %s." % enemy.name)
            combat = False
    player.state = 'normal'
    player.status_effects['Poison'][0] = False
    player.status_effects['DOT'][0] = False
    player.status_effects['Doom'][0] = False
    player.status_effects['Stun'][0] = False
