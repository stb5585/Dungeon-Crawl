###########################################
""" combat manager """

# Imports
import os
import time
import random

import spells
import world
import actions
import character
import storyline


# Functions
def statuses():  # TODO implement function to handle status effects
    pass


def absorb_essence(player, enemy):
    """
    Chance based on
    Different monster types improve differents stats
    Reptile: increase strength
    Aberration: increase intelligence
    Slime: increase wisdom
    Construct: increase constitution
    Humanoid: increase charisma
    Insect: increase dexterity
    Animal: increase max health
    Monster: increase max mana
    Undead: increase level
    Dragon: increase gold
    """
    if not random.randint(0, 100):
        print("You absorb part of the {}'s soul.".format(enemy.name))
        time.sleep(1)
        if enemy.enemy_typ == 'Reptile':
            print("Gain 1 strength.")
            player.strength += 1
        if enemy.enemy_typ == 'Aberration':
            print("Gain 1 intelligence.")
            player.intel += 1
        if enemy.enemy_typ == 'Slime':
            print("Gain 1 wisdom.")
            player.wisdom += 1
        if enemy.enemy_typ == 'Construct':
            print("Gain 1 constitution.")
            player.con += 1
        if enemy.enemy_typ == 'Humanoid':
            print("Gain 1 charisma.")
            player.charisma += 1
        if enemy.enemy_typ == 'Insect':
            print("Gain 1 dexterity.")
            player.dex += 1
        if enemy.enemy_typ == 'Animal':
            print("Gain 5 hit points.")
            player.max_health += 5
        if enemy.enemy_typ == 'Monster':
            print("Gain 5 mana points.")
            player.max_mana += 5
        if enemy.enemy_typ == 'Undead':
            print("Gain enough experience to level.")
            player.experience = player.exp_to_gain
            player.level_up()
        if enemy.enemy_typ == 'Dragon':
            print("Your gold has been doubled.")
            player.gold *= 2
        time.sleep(1)


def cast_spell(attacker, defender, spell, special=False):
    """
    Function that controls spells during combat
    """
    time.sleep(0.25)
    stun = defender.status_effects['Stun'][0]
    if not special:
        attacker.mana -= spell().cost
        print("{} casts {}.".format(attacker.name, spell().name))
    spell_mod = attacker.check_mod('magic')
    enemy_dam_red = defender.check_mod('magic def')
    if spell().name == "Magic Missile":
        for _ in range(spell().missiles):
            damage = 0
            damage += random.randint(spell().damage + spell_mod // 2, (spell().damage + spell_mod))
            damage -= random.randint(enemy_dam_red // 2, enemy_dam_red)
            crit = 1
            if not random.randint(0, spell().crit):
                crit = 2
            damage *= crit
            if crit == 2:
                print("Critical Hit!")
            if random.randint(0, defender.dex // 2) > \
                    random.randint(attacker.intel // 2, attacker.intel) and not stun:
                print("{} dodged the {} and was unhurt.".format(defender.name, spell().name))
            elif random.randint(0, defender.con // 2) > \
                    random.randint(attacker.intel // 2, attacker.intel):
                damage //= 2
                print("{} shrugs off the {} and only receives half of the damage.".format(defender.name, spell().name))
                print("{} damages {} for {} hit points.".format(attacker.name, defender.name, damage))
                defender.health = defender.health - damage
            else:
                if damage <= 0:
                    print("{} was ineffective and does 0 damage".format(spell().name))
                else:
                    print("{} damages {} for {} hit points.".format(attacker.name, defender.name, damage))
                    defender.health = defender.health - damage
            time.sleep(0.1)
    elif spell().cat == 'Attack':
        damage = 0
        damage += random.randint(spell().damage + spell_mod // 2, (spell().damage + spell_mod))
        damage -= random.randint(enemy_dam_red // 2, enemy_dam_red)
        crit = 1
        if not random.randint(0, spell().crit):
            crit = 2
        damage *= crit
        if crit == 2:
            print("Critical Hit!")
        if random.randint(0, defender.dex // 2) > \
                random.randint(attacker.intel // 2, attacker.intel) and not stun:
            print("{} dodged the {} and was unhurt.".format(defender.name, spell().name))
        elif random.randint(0, defender.con // 2) > \
                random.randint(attacker.intel // 2, attacker.intel):
            damage //= 2
            print("{} shrugs off the {} and only receives half of the damage.".format(defender.name, spell().name))
            print("{} damages {} for {} hit points.".format(attacker.name, defender.name, damage))
            defender.health = defender.health - damage
        else:
            if damage <= 0:
                print("{} was ineffective and does 0 damage".format(spell().name))
            else:
                print("{} damages {} for {} hit points.".format(attacker.name, defender.name, damage))
                defender.health = defender.health - damage
        if spell().name == 'Poison Breath':
            if random.randint((attacker.intel * crit) // 2, (attacker.intel * crit)) \
                    > random.randint(defender.con // 2, defender.con):
                pois_dmg = random.randint(spell().damage // 2, spell().damage)
                defender.status_effects['Poison'][0] = True
                defender.status_effects['Poison'][1] = spell().poison_rounds
                defender.status_effects['Poison'][2] = pois_dmg
                print("{} is poisoned for {} turns.".format(defender.name, spell().poison_rounds))
            else:
                print("{} resists the poison.".format(defender.name))
    elif spell().cat == 'Enhance':
        print("{}'s weapon has been imbued with arcane power!".format(attacker.name))
        _, _ = weapon_damage(attacker, defender, dmg_mod=spell().mod)
    elif spell().cat == 'Heal':
        heal_mod = attacker.check_mod('heal')
        heal = int(random.randint(attacker.health_max // 2, attacker.health_max) * spell().heal + heal_mod)
        attacker.health += heal
        print("{} heals themself for {} hit points.".format(attacker.name, heal))
        if attacker.health >= attacker.health_max:
            attacker.health = attacker.health_max
            print("{} is at full health.".format(attacker.name))
    elif spell().cat == 'Kill':
        if spell().name == 'Desoul':
            if random.randint(0, attacker.intel) \
                    > random.randint(defender.con // 2, defender.con):
                defender.health = 0
                print("{} has their soul ripped right out and falls to the ground dead.".format(defender.name))
            else:
                print("The spell has no effect.")
        elif spell().name == 'Petrify':
            if random.randint(0, attacker.intel) \
                    > random.randint(defender.con // 2, defender.con):
                defender.health = 0
                print("{} is turned to stone!".format(defender.name))
            else:
                print("The spell has no effect.")
    if spell().name == 'Terrify':
        if random.randint(attacker.intel // 2, attacker.intel) \
                > random.randint(defender.wisdom // 2, defender.wisdom):
            defender.status_effects["Stun"][0] = True
            defender.status_effects["Stun"][1] = spell().stun
            print("{} stunned {} for {} turns.".format(attacker.name, defender.name, spell().stun))
    if spell().name == 'Corruption':
        if random.randint(attacker.intel // 2, attacker.intel) \
                > random.randint(defender.wisdom // 2, defender.wisdom):
            defender.status_effects["DOT"][0] = True
            defender.status_effects["DOT"][1] = spell().dot_turns
            defender.status_effects["DOT"][2] = spell().damage + attacker.intel - enemy_dam_red
            print("{}'s magic penetrates {}'s defenses.".format(attacker.name, defender.name))
        else:
            print("The magic has no effect.")
    if spell().name == 'Doom':
        if random.randint(attacker.intel // 4, attacker.intel) \
                > random.randint(defender.wisdom // 2, defender.wisdom):
            defender.status_effects["Doom"][0] = True
            defender.status_effects["Doom"][1] = spell().timer
            print("{}'s magic places a timer on {}'s life.".format(attacker.name, defender.name))
        else:
            print("The magic has no effect.")
    if spell().name == 'Blinding Fog':
        if random.randint(attacker.intel // 2, attacker.intel) \
                > random.randint(defender.con // 2, defender.con):
            defender.status_effects['Blind'][0] = True
            defender.status_effects['Blind'][1] = spell().blind
            print("{} is blinded for {} turns.".format(defender.name, spell().blind))
        else:
            print("The spell had no effect.".format(attacker.name, defender.name))
    time.sleep(0.25)


def use_ability(attacker, defender, ability):
    """
    Function controls the use of abilities in combat
    """
    attacker.mana -= ability().cost
    print("{} uses {}.".format(attacker.name, ability().name))
    time.sleep(0.25)
    enemy_dam_red = defender.check_mod('armor')
    if ability().name == 'Steal':
        if len(defender.inventory) != 0:
            if random.randint(0, attacker.dex) > random.randint(0, defender.dex):
                i = random.randint(0, len(defender.inventory) - 1)
                item_key = list(defender.inventory.keys())[i]
                item = defender.inventory[item_key]
                del defender.inventory[item_key]
                if item_key == 'Gold':
                    print("{} steals {} gold from the {}.".format(attacker.name, item, defender.name))
                    attacker.gold += item
                else:  # if monster steals from player, item is lost
                    try:
                        attacker.modify_inventory(item, num=1)
                    except AttributeError:
                        pass
                    print("{} steals {} from {}.".format(attacker.name, item().name, defender.name))
            else:
                print("Steal fails.")
        else:
            print("{} doesn't have anything to steal.".format(defender.name))
    if ability().name == 'Mug':
        hit, crit = weapon_damage(attacker, defender)
        if hit:
            if len(defender.inventory) != 0:
                if random.randint((attacker.dex * crit) // 2, (attacker.dex * crit)) > random.randint(0, defender.dex):
                    i = random.randint(0, len(defender.inventory) - 1)
                    item_key = list(defender.inventory.keys())[i]
                    item = defender.inventory[item_key]
                    del defender.inventory[item_key]
                    if item_key == 'Gold':
                        print("{} steals {} gold from the {}.".format(attacker.name, item, defender.name))
                        attacker.gold += item
                    else:  # if monster steals from player, item is lost
                        try:
                            attacker.modify_inventory(item, num=1)
                        except AttributeError:
                            pass
                        print("{} steals {} from {}.".format(attacker.name, item().name, defender.name))
                else:
                    print("Steal fails.")
            else:
                print("{} doesn't have anything to steal.".format(defender.name))
    if ability().subtyp == 'Drain':
        if 'Health' in ability().name:
            drain = random.randint((attacker.health + attacker.intel) // 5,
                                   (attacker.health + attacker.intel) // 1.5)
            if not random.randint(attacker.wisdom // 2, attacker.wisdom) > random.randint(0, defender.wisdom // 2):
                drain = drain // 2
            if drain > defender.health:
                drain = defender.health
            defender.health -= drain
            attacker.health += drain
            if attacker.health > attacker.health_max:
                attacker.health = attacker.health_max
            print("{} drains {} health from {}.".format(attacker.name, drain, defender.name))
        if 'Mana' in ability().name:
            drain = random.randint((attacker.mana + attacker.intel) // 5,
                                   (attacker.mana + attacker.intel) // 1.5)
            if not random.randint(attacker.wisdom // 2, attacker.wisdom) > random.randint(0, defender.wisdom // 2):
                drain = drain // 2
            if drain > defender.mana:
                drain = defender.mana
            defender.mana -= drain
            attacker.mana += drain
            if attacker.mana > attacker.mana_max:
                attacker.mana = attacker.mana_max
            print("{} drains {} mana from {}.".format(attacker.name, drain, defender.name))
    if ability().name == "Shield Slam":
        dmg_mod = int(attacker.strength * (2 / attacker.equipment['OffHand']().mod))
        if 'Physical Damage' in attacker.equipment['Ring']().mod:
            dmg_mod += int(attacker.equipment['Ring']().mod.split(' ')[0])
        if random.randint(attacker.dex // 2, attacker.dex) > random.randint(0, defender.dex // 2):
            damage = max(1, dmg_mod)
            damage = max(0, (damage - enemy_dam_red))
            defender.health -= damage
            print("{} damages {} with Shield Slam for {} hit points.".format(attacker.name, defender.name, damage))
            if random.randint(attacker.strength // 2, attacker.strength) \
                    > random.randint(defender.strength // 2, defender.strength):
                print("{} is stunned for {} turns.".format(defender.name, ability().stun))
                defender.status_effects['Stun'][0] = True
                defender.status_effects['Stun'][1] = ability().stun
            else:
                print("{} fails to stun {}.".format(attacker.name, defender.name))
        else:
            print("{} swings their shield at {} but miss entirely.".format(attacker.name, defender.name))
    if ability().name == 'Poison Strike':
        hit, crit = weapon_damage(attacker, defender)
        if hit:
            if random.randint((attacker.dex * crit) // 2, (attacker.dex * crit)) \
                    > random.randint(defender.con // 2, defender.con):
                pois_dmg = random.randint(ability().poison_damage // 2, ability().poison_damage)
                defender.status_effects['Poison'][0] = True
                defender.status_effects['Poison'][1] = ability().poison_rounds
                defender.status_effects['Poison'][2] = pois_dmg
                print("{} is poisoned for {} turns.".format(defender.name, ability().poison_rounds))
                print("{} takes {} damage from the poison.".format(defender.name, pois_dmg))
                defender.health -= pois_dmg
            else:
                print("{} resists the poison.".format(defender.name))
    if ability().name == 'Kidney Punch':
        hit, crit = weapon_damage(attacker, defender)
        if hit:
            if random.randint((attacker.dex * crit) // 2, (attacker.dex * crit)) \
                    > random.randint(defender.con // 2, defender.con):
                defender.status_effects['Stun'][0] = True
                defender.status_effects['Stun'][1] = ability().stun
                print("{} is stunned for {} turns.".format(defender.name, ability().stun))
            else:
                print("{} fails to stun {}.".format(attacker.name, defender.name))
    if ability().name == 'Blind':
        if random.randint(attacker.dex // 2, attacker.dex) \
                > random.randint(defender.dex // 2, defender.dex):
            defender.status_effects['Blind'][0] = True
            defender.status_effects['Blind'][1] = ability().blind
            print("{} is blinded for {} turns.".format(defender.name, ability().blind))
        else:
            print("{} fails to blind {}.".format(attacker.name, defender.name))
    if ability().name == 'Lockpick':
        defender.lock = False
    if ability().name == 'Multi-Strike':
        for _ in range(ability().strikes):
            _, _ = weapon_damage(attacker, defender)
    if ability().name == 'Jump':
        for _ in range(ability().strikes):
            _, _ = weapon_damage(attacker, defender, crit=2)
    if ability().name == 'Backstab' or ability().name == 'Piercing Strike':
        _, _ = weapon_damage(attacker, defender, ignore=True)
    if ability().name == 'Mortal Strike':
        hit, crit = weapon_damage(attacker, defender, crit=ability().crit)
        if hit:
            if random.randint((attacker.strength * crit) // 2, (attacker.strength * crit)) \
                    > random.randint(defender.con // 2, defender.con):
                defender.status_effects['Bleed'][0] = True
                defender.status_effects['Bleed'][1] = attacker.strength // 10
                defender.status_effects['Bleed'][2] = attacker.strength // 2
                print("{} is bleeding for {} turns.".format(defender.name, ability().bleed))
    if ability().name == 'Disarm':
        if defender.equipment['Weapon']().subtyp != "Natural" and defender.equipment['Weapon']().subtyp != "None":
            if random.randint(attacker.strength // 2, attacker.strength) \
                    > random.randint(defender.con // 2, defender.con):
                defender.status_effects['Disarm'][0] = True
                defender.status_effects['Disarm'][1] = ability().turns
                print("{} is disarmed for {} turns.".format(defender.name, ability().turns))
            else:
                print("{} fails to disarm the {}.".format(attacker.name, defender.name))
        else:
            print("The {} cannot be disarmed.".format(defender.name))
    if ability().name == 'Multi-Cast':
        j = 0
        while j < ability().cast:
            spell_list = []
            i = 0
            for entry in attacker.spellbook['Spells']:
                if attacker.spellbook['Spells'][entry]().cost <= attacker.mana:
                    if attacker.spellbook['Spells'][entry]().name != 'Magic Missile':
                        spell_list.append(
                            (str(entry) + '  ' + str(attacker.spellbook['Spells'][entry]().cost), i))
                        i += 1
            if len(spell_list) == 0:
                print("{} does not have enough mana to cast any spells with Multi-Cast.".format(
                    attacker.name))
                attacker.mana += ability().cost
                break
            spell_index = storyline.get_response(spell_list)
            spell = attacker.spellbook['Spells'][spell_list[spell_index][0].split('  ')[0]]
            cast_spell(attacker, defender, spell)
            j += 1
            if defender.health < 1:
                break
    if ability().name == 'Elemental Strike':
        hit, crit = weapon_damage(attacker, defender)
        if hit:
            spell_list = [spells.Scorch, spells.WaterJet, spells.Tremor, spells.Gust]
            spell = random.choice(spell_list)
            if crit > 1:
                print("{} casts {} twice!".format(attacker.name, spell().name))
                cast_spell(attacker, defender, spell, special=True)
                cast_spell(attacker, defender, spell, special=True)
            else:
                print("{} casts {}.".format(attacker.name, spell().name))
                cast_spell(attacker, defender, spell, special=True)
    time.sleep(0.25)


def weapon_damage(attacker, defender, crit=1, dmg_mod=0, ignore=False, typ='attacks'):
    """
    Function that controls melee attacks during combat
    """
    hit = False  # indicates if the attack was successful for means of ability/weapon affects
    if typ == 'leers':
        print("{} {} at {}.".format(attacker.name, typ, defender.name))
        cast_spell(attacker, defender, spells.Petrify, special=True)
        return True, crit
    hit_mod = 1
    dmg_mod += attacker.check_mod('weapon')
    off_dmg_mod = attacker.check_mod('off')
    enemy_dam_red = defender.check_mod('armor')
    dodge = False
    off_dodge = False
    if attacker.status_effects['Blind'][0]:
        hit_mod = 2
    if crit == 1:
        if not random.randint(0, int(attacker.equipment['Weapon']().crit)):
            crit = 2
    off_crit = 1
    if attacker.equipment['OffHand']().typ == 'Weapon':
        if not random.randint(0, int(attacker.equipment['OffHand']().crit)):
            off_crit = 2
    if defender.status_effects['Stun'][0] and hit_mod == 1:
        if crit > 1:
            print("Critical hit!")
        dmg = max(1, dmg_mod - enemy_dam_red)
        damage = max(0, int(random.randint(dmg // 2, dmg) * crit))
        defender.health -= damage
        print("{} {} a stunned {} for {} damage.".format(attacker.name, typ, defender.name, damage))
        if attacker.equipment['OffHand']().typ == 'Weapon':
            if off_crit > 1:
                print("Critical offhand hit!")
            off_dmg = max(1, off_dmg_mod - enemy_dam_red)
            off_damage = max(0, int(random.randint(off_dmg // 2, off_dmg) * off_crit))
            print("{} {} a stunned {} for {} damage.".format(attacker.name, typ, defender.name, off_damage))
            defender.health -= off_damage
        hit = True
        time.sleep(0.5)
    else:
        if random.randint(0, defender.dex // 2) > \
                random.randint(attacker.dex // (2 * hit_mod), attacker.dex // hit_mod):
            dodge = True
        if attacker.equipment['OffHand']().typ == 'Weapon':
            if random.randint(0, defender.dex // 2) > \
                    random.randint(attacker.dex // (2 * hit_mod), attacker.dex // hit_mod):
                off_dodge = True
        if not dodge:
            hit = True
            if crit > 1:
                print("Critical hit!")
            if ignore:
                dmg = max(1, dmg_mod)
                damage = max(0, int(random.randint((dmg // 2), dmg) * crit))
            else:
                dmg = max(1, (dmg_mod - enemy_dam_red))
                damage = random.randint(dmg // 2, dmg)
                if defender.equipment['OffHand']().subtyp == 'Shield':
                    if not random.randint(0, int(defender.equipment['OffHand']().mod)):
                        blk_amt = (100 / defender.equipment['OffHand']().mod +
                                   random.randint(defender.strength // 2, defender.strength) -
                                   random.randint(attacker.strength // 2, attacker.strength)) / 100
                        if 'Shield Block' in list(defender.spellbook['Skills'].keys()):
                            blk_amt *= 2
                        blk_amt = min(1, blk_amt)
                        damage *= (1 - blk_amt)
                        print("{} blocks {}'s attack and mitigates {} percent of the damage.".format(
                            defender.name, attacker.name, int(blk_amt * 100)))
            if int(damage) > 0:
                print("{} {} {} for {} damage.".format(attacker.name, typ, defender.name, int(damage)))
                defender.health -= int(damage)
            else:
                print("{} {} {} but deals no damage.".format(attacker.name, typ, defender.name))
        else:
            if 'Parry' in list(defender.spellbook['Skills'].keys()):  # TODO need to prevent infinite loop
                print("{} parries {}'s attack and counterattacks!".format(defender.name, attacker.name))
                _, _ = weapon_damage(defender, attacker)
            else:
                print("{} evades {}'s attack.".format(defender.name, attacker.name))
        time.sleep(0.5)
        if not off_dodge:
            if attacker.equipment['OffHand']().typ == 'Weapon':
                if off_crit > 1:
                    print("Critical offhand hit!")
                if ignore:
                    off_dmg = max(1, off_dmg_mod)
                    off_damage = max(0, int(random.randint((off_dmg // 2), off_dmg) * off_crit))
                else:
                    off_dmg = max(1, off_dmg_mod - enemy_dam_red)
                    off_damage = max(0, int(random.randint(off_dmg // 2, off_dmg) * off_crit))
                    if defender.equipment['OffHand']().subtyp == 'Shield':
                        if not random.randint(0, int(defender.equipment['OffHand']().mod)):
                            off_blk_amt = (100 / defender.equipment['OffHand']().mod +
                                           random.randint(defender.strength // 2, defender.strength) -
                                           random.randint(attacker.strength // 2, attacker.strength)) / 100
                            if 'Shield Block' in list(defender.spellbook['Skills'].keys()):
                                off_blk_amt *= 2
                            off_blk_amt = min(1, off_blk_amt)
                            off_damage *= (1 - off_blk_amt)
                            print("{} blocks {}'s attack and mitigates {} percent of the damage.".format(
                                defender.name, attacker.name, int(off_blk_amt * 100)))
                if int(off_damage) > 0:
                    print("{} {} {} for {} damage.".format(attacker.name, typ, defender.name, int(off_damage)))
                    defender.health -= int(off_damage)
                else:
                    print("{} {} {} but deals no damage.".format(attacker.name, typ, defender.name))
        else:
            if 'Parry' in list(defender.spellbook['Skills'].keys()):  # TODO need to prevent infinite loop
                print("{} parries {}'s attack and counterattacks!".format(defender.name, attacker.name))
                _, _ = weapon_damage(defender, attacker)
            else:
                print("{} evades {}'s offhand attack.".format(defender.name, attacker.name))
        time.sleep(0.5)
    time.sleep(0.25)
    return hit, crit


def options(player, enemy, tile, action_list=None):
    """
    Controls the listed options during combat
    """
    print(tile.intro_text(player))
    if (player.cls == 'Inquisitor' or player.cls == 'Seeker' or 'Vision' in player.equipment['Pendant']().mod) and \
            'Chest' not in enemy.name and 'Door' not in enemy.name:
        print(enemy)
    print("Player: {} | Health: {}/{} | Mana: {}/{}".format(player.name, player.health, player.health_max,
                                                            player.mana, player.mana_max))
    if action_list is not None:
        for action in action_list:
            print(action)
        if 'Chest' not in enemy.name and 'Door' not in enemy.name and 'Boss' not in tile.intro_text(player):
            print(actions.Flee())
        action_input = input('Action: ').lower()
        return action_input


def player_turn(player, enemy, tile, available_actions, combat):
    valid_entry = False
    flee = False
    action_input = options(player, enemy, tile, available_actions)
    for action in available_actions:
        if action_input == action.hotkey and 'Move' in action.name:
            combat = False
            player.state = 'normal'
            valid_entry = True
            player.do_action(action, **action.kwargs)
            return valid_entry, combat
    if action_input == 'o':
        player.open_up(enemy)
        combat = False
        valid_entry = True
    if action_input == 'a':
        _, _ = weapon_damage(player, enemy)
        valid_entry = True
    if action_input == 'p':
        valid_entry = player.use_item(enemy=enemy)
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
        spell_list.append(('Go Back', i))
        spell_index = storyline.get_response(spell_list)
        if spell_list[spell_index][0] == 'Go Back':
            os.system('cls' if os.name == 'nt' else 'clear')
            return False, combat
        else:
            spell = player.spellbook['Spells'][spell_list[spell_index][0].split('  ')[0]]
            cast_spell(player, enemy, spell)
            valid_entry = True
    if action_input == 'k':
        i = 0
        skill_list = []
        for entry in player.spellbook['Skills']:
            if player.spellbook['Skills'][entry]().cost <= player.mana:
                if player.spellbook['Skills'][entry]().passive:
                    continue
                elif player.spellbook['Skills'][entry]().name == 'Smoke Screen' and 'Boss' in \
                        tile.intro_text(player):
                    continue
                elif player.spellbook['Skills'][entry]().name == 'Lockpick' and \
                        enemy.name != 'Locked Chest':
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
        skill_list.append(('Go Back', i))
        skill_index = storyline.get_response(skill_list)
        if skill_list[skill_index][0] == 'Go Back':
            os.system('cls' if os.name == 'nt' else 'clear')
            return False, combat
        else:
            skill = player.spellbook['Skills'][skill_list[skill_index][0].split('  ')[0]]
            while True:
                if skill().name == 'Smoke Screen':
                    player.mana -= skill().cost
                    flee = character.Player.flee(player, enemy, smoke=True)
                else:
                    use_ability(player, enemy, skill)
                break
            valid_entry = True
    if flee:
        """Moves the player randomly to an adjacent tile"""
        available_moves = tile.adjacent_moves()
        r = random.randint(0, len(available_moves) - 1)
        player.do_action(available_moves[r])
    return valid_entry, combat


def enemy_turn(player, enemy, combat, typ='attacks'):
    if 'Chest' not in enemy.name and 'Door' not in enemy.name:
        if enemy.equipment['Weapon']().typ == 'Natural':
            typ = enemy.equipment['Weapon']().name
    if enemy.health <= 0 and 'Chest' not in enemy.name:
        time.sleep(0.5)
        print("{} killed the {}.".format(player.name, enemy.name))
        time.sleep(0.25)
        print("{} gained {} experience.".format(player.name, enemy.experience))
        player.loot(enemy)
        player.experience += enemy.experience
        while player.experience >= player.exp_to_gain:
            player.level_up()
        if player.cls == "Soulcatcher":
            absorb_essence(player, enemy)
        player.state = 'normal'
        return False
    elif player.state == 'normal' or 'Chest' in enemy.name or 'Door' in enemy.name:
        return False
    elif enemy.status_effects['Stun'][0]:
        enemy.status_effects['Stun'][1] -= 1
        if enemy.status_effects['Stun'][1] == 0:
            enemy.status_effects['Stun'][0] = False
            print("The {} is no longer stunned.".format(enemy.name))
    else:
        enemy_spell_list = []
        enemy_skill_list = []
        for spell_name, spell in enemy.spellbook['Spells'].items():
            if enemy.spellbook['Spells'][spell_name]().cost <= enemy.mana:
                enemy_spell_list.append(spell)
        for spell_name, spell in enemy.spellbook['Skills'].items():
            if enemy.spellbook['Skills'][spell_name]().passive:
                continue
            elif enemy.spellbook['Skills'][spell_name]().cost <= enemy.mana:
                enemy_skill_list.append(spell)
        if len(enemy_spell_list) > 0 and len(enemy_skill_list) > 0:
            cast = random.randint(0, 2)
            if cast == 0:
                enemy_spell = enemy_spell_list[random.randint(0, len(enemy_spell_list) - 1)]
                cast_spell(enemy, player, enemy_spell)
                try:
                    if enemy_spell().rank == 1:
                        if (player.cls == "Diviner" or player.cls == "Geomancer") and \
                                enemy_spell().name not in player.spellbook['Spells']:
                            player.spellbook['Spells'][enemy_spell().name] = enemy_spell
                            print(enemy_spell())
                            print("You have gained the ability to cast {}.".format(enemy_spell().name))
                    elif enemy_spell().rank == 2:
                        if player.cls == "Geomancer" and enemy_spell().name not in player.spellbook['Spells']:
                            player.spellbook['Spells'][enemy_spell().name] = enemy_spell
                            print(enemy_spell())
                            print("You have gained the ability to cast {}.".format(enemy_spell().name))
                except AttributeError:
                    pass
            elif cast == 1:
                enemy_skill = enemy_skill_list[random.randint(0, len(enemy_skill_list) - 1)]
                use_ability(enemy, player, enemy_skill)
            else:
                _, _ = weapon_damage(enemy, player, typ=typ)
        elif len(enemy_spell_list) > 0:
            cast = random.randint(0, 1)
            if cast:
                enemy_spell = enemy_spell_list[random.randint(0, len(enemy_spell_list) - 1)]
                cast_spell(enemy, player, enemy_spell)
                try:
                    if enemy_spell().rank == 1:
                        if (player.cls == "Diviner" or player.cls == "Geomancer") and \
                                enemy_spell().name not in player.spellbook['Spells']:
                            player.spellbook['Spells'][enemy_spell().name] = enemy_spell
                            print(enemy_spell())
                            print("You have gained the ability to cast {}.".format(enemy_spell().name))
                    elif enemy_spell().rank == 2:
                        if player.cls == "Geomancer" and enemy_spell().name not in player.spellbook['Spells']:
                            player.spellbook['Spells'][enemy_spell().name] = enemy_spell
                            print(enemy_spell())
                            print("You have gained the ability to cast {}.".format(enemy_spell().name))
                except AttributeError:
                    pass
            else:
                _, _ = weapon_damage(enemy, player, typ=typ)
        elif len(enemy_skill_list) > 0:
            cast = random.randint(0, 1)
            if cast:
                enemy_skill = enemy_skill_list[random.randint(0, len(enemy_skill_list) - 1)]
                use_ability(enemy, player, enemy_skill)
            else:
                _, _ = weapon_damage(enemy, player, typ=typ)
        else:
            _, _ = weapon_damage(enemy, player, typ=typ)
        if enemy.status_effects['Poison'][0]:
            enemy.status_effects['Poison'][1] -= 1
            poison_damage = enemy.status_effects['Poison'][2]
            poison_damage -= random.randint(0, enemy.con)
            if poison_damage > 0:
                poison_damage = random.randint(poison_damage // 2, poison_damage)
                enemy.health -= poison_damage
                print("The poison damages {} for {} health points.".format(enemy.name, poison_damage))
            else:
                print("The {} resisted the poison.".format(enemy.name))
            if enemy.status_effects['Poison'][1] == 0:
                enemy.status_effects['Poison'][0] = False
                print("The poison has left the {}.".format(enemy.name))
        if enemy.status_effects['DOT'][0]:
            enemy.status_effects['DOT'][1] -= 1
            dot_damage = enemy.status_effects['DOT'][2]
            dot_damage -= random.randint(0, enemy.wisdom)
            if dot_damage > 0:
                dot_damage = random.randint(dot_damage // 2, dot_damage)
                enemy.health -= dot_damage
                print("The magic damages {} for {} health points.".format(enemy.name, dot_damage))
            else:
                print("The {} resisted the spell.".format(enemy.name))
            if enemy.status_effects['DOT'][1] == 0:
                enemy.status_effects['DOT'][0] = False
                print("The magic affecting the {} has worn off.".format(enemy.name))
        if enemy.status_effects['Doom'][0]:
            enemy.status_effects['Doom'][1] -= 1
            if enemy.status_effects['Doom'][1] == 0:
                print("The Doom countdown has expired and so has the {}!".format(enemy.name))
                enemy.health = 0
        if enemy.status_effects['Blind'][0]:
            enemy.status_effects['Blind'][1] -= 1
            if enemy.status_effects['Blind'][1] == 0:
                print("The {} is no longer blind.".format(enemy.name))
                enemy.status_effects['Blind'][0] = False
        if enemy.status_effects['Bleed'][0]:
            enemy.status_effects['Bleed'][1] -= 1
            bleed_damage = enemy.status_effects['Bleed'][2]
            bleed_damage -= random.randint(0, enemy.con)
            if bleed_damage > 0:
                bleed_damage = random.randint(bleed_damage // 2, bleed_damage)
                enemy.health -= bleed_damage
                print("The bleed damages {} for {} health points.".format(enemy.name, bleed_damage))
            else:
                print("The {} resisted the bleed.".format(enemy.name))
            if enemy.status_effects['Bleed'][1] == 0:
                enemy.status_effects['Bleed'][0] = False
                print("The {}'s wounds have healed and is no longer bleeding.".format(enemy.name))
        if enemy.status_effects['Disarm'][0]:
            enemy.status_effects['Disarm'][1] -= 1
            if enemy.status_effects['Disarm'][1] == 0:
                print("The {} picks up their weapon.".format(enemy.name))
                enemy.status_effects['Disarm'][0] = False
        if enemy.health <= 0 and 'Chest' not in enemy.name:
            print("{} killed the {}.".format(player.name, enemy.name))
            print("{} gained {} experience.".format(player.name, enemy.experience))
            player.loot(enemy)
            player.experience += enemy.experience
            while player.experience >= player.exp_to_gain:
                player.level_up()
            player.state = 'normal'
            return False
    if not player.is_alive():
        print("{} was slain by the {}.".format(player.name, enemy.name))
        return False
    return combat


def battle(player, enemy, wmap):
    """
    Function that controls combat; needs refactoring
    """
    tile = world.tile_exists(player.location_x, player.location_y, player.location_z)
    available_actions = tile.available_actions(player)
    combat = True
    while combat:
        os.system('cls' if os.name == 'nt' else 'clear')
        tile.minimap(player, wmap)
        if player.status_effects['Stun'][0]:
            print("Player: {} | Health: {}/{} | Mana: {}/{}".format(player.name, player.health, player.health_max,
                                                                    player.mana, player.mana_max))
            player.status_effects['Stun'][1] -= 1
            if player.status_effects['Stun'][1] == 0:
                player.status_effects['Stun'][0] = False
                print("{} is no longer stunned.".format(player.name))
        else:
            while True:
                valid_entry, combat = player_turn(player, enemy, tile, available_actions, combat)
                if valid_entry:
                    break
                else:
                    tile.minimap(player, wmap)
        if player.status_effects['Poison'][0]:
            player.status_effects['Poison'][1] -= 1
            poison_damage = player.status_effects['Poison'][2]
            poison_damage -= random.randint(0, player.con)
            if poison_damage > 0:
                poison_damage = random.randint(poison_damage // 2, poison_damage)
                player.health -= poison_damage
                print("The poison damages {} for {} health points.".format(player.name, poison_damage))
            else:
                print("{} resisted the poison.".format(player.name))
            if player.status_effects['Poison'][1] == 0:
                player.status_effects['Poison'][0] = False
                print("{} is free from the poison.".format(player.name))
        if player.status_effects['DOT'][0]:
            player.status_effects['DOT'][1] -= 1
            dot_damage = player.status_effects['DOT'][2]
            dot_damage -= random.randint(0, player.wisdom)
            if dot_damage > 0:
                dot_damage = random.randint(dot_damage // 2, dot_damage)
                player.health -= dot_damage
                print("The magic damages {} for {} health points.".format(player.name, dot_damage))
            else:
                print("{} resisted the spell.".format(player.name))
            if player.status_effects['DOT'][1] == 0:
                player.status_effects['DOT'][0] = False
                print("The magic affecting {} has worn off.".format(player.name))
        if player.status_effects['Doom'][0]:
            player.status_effects['Doom'][1] -= 1
            if player.status_effects['Doom'][1] == 0:
                print("The Doom countdown has expired and so has {}!".format(player.name))
                player.health = 0
        if player.status_effects['Blind'][0]:
            player.status_effects['Blind'][1] -= 1
            if player.status_effects['Blind'][1] == 0:
                print("{} is no longer blind.".format(player.name))
                player.status_effects['Blind'][0] = False
        if player.status_effects['Bleed'][0]:
            player.status_effects['Bleed'][1] -= 1
            bleed_damage = player.status_effects['Bleed'][2]
            bleed_damage -= random.randint(0, player.con)
            if bleed_damage > 0:
                bleed_damage = random.randint(bleed_damage // 2, bleed_damage)
                player.health -= bleed_damage
                print("The bleed damages {} for {} health points.".format(player.name, bleed_damage))
            else:
                print("{} resisted the bleed.".format(player.name))
            if player.status_effects['Bleed'][1] == 0:
                player.status_effects['Bleed'][0] = False
                print("{}'s wounds have healed and is no longer bleeding.".format(player.name))
        if player.status_effects['Disarm'][0]:
            player.status_effects['Disarm'][1] -= 1
            if player.status_effects['Disarm'][1] == 0:
                print("{} picks up their weapon.".format(player.name))
                player.status_effects['Disarm'][0] = False
        if not player.is_alive():
            print("{} was slain by the {}.".format(player.name, enemy.name))
            combat = False

        # Enemies turn
        if combat:
            combat = enemy_turn(player, enemy, combat)
        time.sleep(1)

    # os.system('cls' if os.name == 'nt' else 'clear')
    player.state = 'normal'
    player.status_effects['Poison'][0] = False
    player.status_effects['DOT'][0] = False
    player.status_effects['Doom'][0] = False
    player.status_effects['Stun'][0] = False
    player.status_effects['Blind'][0] = False
    player.status_effects['Bleed'][0] = False
    player.status_effects['Disarm'][0] = False
