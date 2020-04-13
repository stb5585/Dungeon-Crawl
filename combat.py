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
    available_actions = tile.available_actions(player)
    combat = True
    flee = False
    stun = False
    poison = False
    dot = False
    doom = False
    stun_turn = 0
    stun_rounds = 0
    poison_turn = 0
    poison_rounds = 0
    poison_damage = 0
    dot_turn = 0
    dot_rounds = 0
    dot_damage = 0
    doom_turn = 0
    doom_rounds = 0
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
                if action_input == action.hotkey and action_input != 'f' and action_input != 'x' \
                        and action_input != 'k' and action_input != 'p':
                    player.do_action(action, **action.kwargs)
                    valid_entry = True
                    break
            if action_input == 'p':
                if player.use_item():
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
                    print("You do not have enough mana to cast any spells. You attack instead.")
                    player.weapon_damage(enemy)
                else:
                    spell_list.append(('Go back', i))
                    spell_index = storyline.get_response(spell_list)
                    if spell_list[spell_index][0] == 'Go back':
                        continue
                    else:
                        spell = player.spellbook['Spells'][spell_list[spell_index][0].split('  ')[0]]
                        if spell().name == 'Terrify':
                            if random.randint(player.intel // 2, player.intel) \
                                    > random.randint(enemy.wisdom // 2, enemy.wisdom):
                                stun = True
                                stun_rounds = spell().stun
                        if spell().name == 'Corruption':
                            if random.randint(player.intel // 2, player.intel) \
                                    > random.randint(enemy.wisdom // 2, enemy.wisdom):
                                dot = True
                                dot_rounds = spell().dot_turns
                                dot_damage = spell().damage
                        if spell().name == 'Doom':
                            if random.randint(player.intel // 4, player.intel) \
                                    > random.randint(enemy.wisdom // 2, enemy.wisdom):
                                doom = True
                                doom_rounds = spell().timer
                        player.cast_spell(enemy, spell)
                        if enemy.health > 0:
                            if stun and stun_turn == 0:
                                print("You stun the enemy for %s turns." % stun_rounds)
                            if dot and dot_turn == 0:
                                print("Your magic penetrates the enemy's resistance. They will take damage for the next"
                                      " %s rounds." % dot_rounds)
                        valid_entry = True
            if action_input == 'k':
                i = 0
                skill_list = []
                for entry in player.spellbook['Skills']:
                    if player.spellbook['Skills'][entry]().cost <= player.mana:
                        if player.spellbook['Skills'][entry]().name == 'Smoke Screen' and 'Boss' in tile.intro_text():
                            continue
                        else:
                            skill_list.append((str(entry) + '  ' + str(player.spellbook['Skills'][entry]().cost), i))
                            i += 1
                if len(skill_list) == 0:
                    print("You do not have enough mana to use any skills. You attack instead.")
                    player.weapon_damage(enemy)
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
                            elif skill().name == 'Steal':
                                player.mana -= skill().cost
                                if len(enemy.loot) != 0:
                                    if random.randint(0, player.dex) > random.randint(0, enemy.dex):
                                        i = random.randint(0, len(enemy.loot) - 1)
                                        item_key = list(enemy.loot.keys())[i]
                                        item = enemy.loot[item_key]
                                        del enemy.loot[item_key]
                                        if item_key == 'Gold':
                                            print("You steal %s gold from the enemy!" % item)
                                            player.gold += item
                                        else:
                                            player.modify_inventory(item, num=1)
                                            print("You steal %s from the enemy!" % item().name)
                                    else:
                                        print("You couldn't steal anything.")
                                else:
                                    print("The enemy doesn't have anything to steal.")
                            elif skill().name == 'Shield Slam':
                                if player.equipment['OffHand']().subtyp == 'Shield':
                                    player.mana -= skill().cost
                                    if random.randint(player.strength // 2, player.strength) \
                                            > random.randint(0, enemy.strength):
                                        print("You stun the enemy for %s turns." % skill().stun)
                                        stun = True
                                        stun_rounds = skill().stun
                                    else:
                                        print("You failed to stun the enemy.")
                                else:
                                    print("You are not equipped with a shield. You attack instead.")
                                player.weapon_damage(enemy)
                            elif skill().name == 'Kidney Punch':
                                player.mana -= skill().cost
                                player.weapon_damage(enemy)
                                if random.randint(player.dex // 2, player.dex) \
                                        > random.randint(0, enemy.dex):
                                    print("You stun the enemy for %s turns." % skill().stun)
                                    stun = True
                                    stun_rounds = skill().stun
                                else:
                                    print("Your stun attempt failed.")
                            elif skill().subtyp == 'Drain':
                                player.mana -= skill().cost
                                if 'Health' in skill().name:
                                    if random.randint(player.wisdom // 2, player.wisdom) \
                                            > random.randint(0, enemy.wisdom // 2):
                                        drain = random.randint(player.intel // 2, player.intel)
                                        if drain > enemy.health:
                                            drain = enemy.health
                                        enemy.health -= drain
                                        player.health += drain
                                        print("You drain %s health from the enemy." % drain)
                                if 'Mana' in skill().name:
                                    if random.randint(player.wisdom // 2, player.wisdom) \
                                            > random.randint(0, enemy.wisdom // 2):
                                        drain = random.randint(player.intel // 2, player.intel)
                                        if drain > enemy.mana:
                                            drain = enemy.mana
                                        enemy.mana -= drain
                                        player.mana += drain
                                        print("You drain %s mana from the enemy." % drain)
                            elif skill().name == 'Poison Strike':
                                player.weapon_damage(enemy)
                                if random.randint(player.dex // 2, player.dex) \
                                        > random.randint(enemy.con // 2, enemy.con):
                                    poison = True
                                    poison_damage = skill().poison_damage
                                    poison_rounds = skill().poison_rounds
                                else:
                                    print("The enemy resisted the poison.")
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
            if player.experience >= (25 ** player.pro_level) * player.level:
                player.level_up()
            player.state = 'normal'
            combat = False
        elif player.state == 'normal' or enemy.name == 'Chest':
            combat = False
        elif stun:
            stun_turn += 1
            if stun_turn == stun_rounds:
                stun = False
                print("The enemy is no longer stunned.")
        else:
            enemy.do_damage(player)
            if poison:
                poison_turn += 1
                poison_damage -= random.randint(0, enemy.con)
                if poison_damage > 0:
                    poison_damage = random.randint(poison_damage // 2, poison_damage)
                    enemy.health -= poison_damage
                    print("The poison damages %s for %s health points." % (enemy.name, poison_damage))
                else:
                    print("The enemy resisted the poison.")
                if poison_turn == poison_rounds:
                    poison = False
            if dot:
                dot_turn += 1
                dot_damage -= random.randint(0, enemy.wisdom)
                if dot_damage > 0:
                    dot_damage = random.randint(dot_damage // 2, dot_damage)
                    enemy.health -= dot_damage
                    print("The magic damages %s for %s health points." % (enemy.name, dot_damage))
                else:
                    print("The enemy resisted the spell.")
                if dot_turn == dot_rounds:
                    dot = False
            if doom:
                doom_turn += 1
                if doom_turn == doom_rounds:
                    enemy.health = 0
            if enemy.health <= 0:
                print("You killed the {0.name}.".format(enemy))
                print("You gained %s experience." % enemy.experience)
                player.loot(enemy)
                player.experience += enemy.experience
                if player.experience >= (25 ** player.pro_level) * player.level:
                    player.level_up()
                player.state = 'normal'
                combat = False
        if player.health <= 0:
            print("You were slain by the {0.name}.".format(enemy))
            combat = False
    player.state = 'normal'
