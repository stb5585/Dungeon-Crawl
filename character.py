# Imports
import time
import random


class Character:
    """
    Basic definition of a character (player or enemy)
    """

    def __init__(self):
        self.name = ""
        self.health = 0
        self.health_max = 0
        self.mana = 0
        self.mana_max = 0
        self.race = ""
        self.cls = ""
        self.strength = 0
        self.intel = 0
        self.wisdom = 0
        self.con = 0
        self.charisma = 0
        self.dex = 0
        self.level = 0
        self.pro_level = 1
        self.status_effects = {"Prone": [False, 0],  # whether prone or not, difficulty rating
                               "Silence": [False, 0],  # whether silenced, turns remaining
                               "Mana Shield": [False, 0],  # whether mana shield is active, health reduction per mana
                               "Stun": [False, 0],  # whether stunned, turns remaining
                               "Doom": [False, 0],  # whether doomed, turns until death
                               "Blind": [False, 0],  # whether blind, turns
                               "Disarm": [False, 0],  # whether disarmed, turns
                               "Sleep": [False, 0],  # whether asleep, turns
                               "Reflect": [False, 0],  # whether reflecting spells, turns
                               "Poison": [False, 0, 0],  # whether poisoned, turns, damage per turn
                               "DOT": [False, 0, 0],  # whether corrupted or burning, turns, damage per turn
                               "Bleed": [False, 0, 0],  # whether bleeding, turns, damage per turn
                               "Regen": [False, 0, 0],  # whether HP is regenerating, turns, heal per turn
                               "Attack": [False, 0, 0],  # increased melee damage, turns, amount
                               "Defense": [False, 0, 0],  # increase armor rating, turns, amount
                               "Magic": [False, 0, 0],  # increase magic damage, turns, amount
                               "Magic Defense": [False, 0, 0],  # increase magic defense, turns, amount
                               }
        self.equipment = {}
        self.inventory = {}
        self.special_inventory = {}
        self.spellbook = {'Spells': {},
                          'Skills': {}}
        self.resistance = {'Fire': 0.,
                           'Ice': 0.,
                           'Electric': 0.,
                           'Water': 0.,
                           'Earth': 0.,
                           'Wind': 0.,
                           'Shadow': 0.,
                           'Death': 0.,
                           'Stone': 0.,
                           'Holy': 0.,
                           'Poison': 0.,
                           'Physical': 0.}
        self.flying = False
        self.invisible = False
        self.transform_list = []
        self.familiar = None
        self.turtle = False

    def options(self, action_list=None):
        pass

    def weapon_damage(self, defender, dmg_mod=0, crit=1, ignore=False, cover=False):
        """
        Function that controls melee attacks during combat
        """
        hits = []  # indicates if the attack was successful for means of ability/weapon affects
        crits = []
        attacks = ['Weapon']
        if self.equipment['OffHand']().typ == 'Weapon':
            attacks.append('OffHand')
        for i, att in enumerate(attacks):
            hits.append(False)
            crits.append(1)
            if not ignore:
                ignore = self.equipment[att]().ignore
            # attacker variables
            typ = 'attacks'
            if self.equipment[att]().subtyp == 'Natural':
                typ = self.equipment[att]().att_name
                if typ == 'leers':
                    hits[i] = True
                    self.equipment[att]().special_effect(self, defender)
                    break
            hit_mod = 1 + ((int(self.status_effects['Blind'][0]) +
                            int(defender.invisible) +
                            int(defender.flying)) / 2)
            if crit == 1:
                if not random.randint(0, int(self.equipment[att]().crit)):
                    crits[i] = 2
                else:
                    crits[i] = 1
            else:
                crits[i] = crit
            dmg = max(1, dmg_mod + self.check_mod(att.lower()))
            damage = max(0, int(random.randint(dmg // 2, dmg) * crits[i]))

            # defender variables
            prone = defender.status_effects['Prone'][0]
            stun = defender.status_effects['Stun'][0]
            sleep = defender.status_effects['Sleep'][0]
            dam_red = defender.check_mod('armor') * int(not ignore)
            resist = defender.check_mod('resist', typ='Physical', ultimate=self.equipment[att]().ultimate)
            chance = defender.check_mod('luck', luck_factor=15)
            dodge = random.randint(0, defender.dex // 2) + chance > random.randint(
                int(self.dex / (2 * hit_mod)), int(self.dex / hit_mod))
            if any([prone, stun, sleep]):
                dodge = False

            # combat
            if dodge:
                if 'Parry' in list(defender.spellbook['Skills'].keys()):
                    print("{} parries {}'s attack and counterattacks!".format(defender.name, self.name))
                    _, _ = defender.weapon_damage(self)
                else:
                    print("{} evades {}'s attack.".format(defender.name, self.name))
            else:
                if hit_mod == 1:
                    hits[i] = True
                else:
                    a_chance = self.check_mod('luck', luck_factor=10)
                    if random.randint(0, 1 + a_chance):
                        hits[i] = True
                if hits[i]:
                    if crits[i] > 1:
                        print("Critical hit!")
                    if cover:
                        print("{} steps in front of the attack, taking the damage for {}.".format(
                            defender.familiar.name, defender.name))
                        damage = 0
                    elif (defender.equipment['OffHand']().subtyp == 'Shield' and
                          not defender.status_effects['Mana Shield'][0]) and (not stun and not sleep):
                        if not random.randint(0, int(defender.equipment['OffHand']().mod)):
                            blk_amt = (100 / defender.equipment['OffHand']().mod +
                                       random.randint(defender.strength // 2, defender.strength) -
                                       random.randint(self.strength // 2, self.strength)) / 100
                            if blk_amt <= 0:
                                print("{} attempts to block {}'s attack but isn't strong enough.".format(
                                    defender.name, self.name))
                            else:
                                if 'Shield Block' in list(defender.spellbook['Skills'].keys()):
                                    blk_amt *= 2
                                blk_amt = min(1, blk_amt)
                                damage *= (1 - blk_amt)
                                damage = int(damage * (1 - resist))
                                print("{} blocks {}'s attack and mitigates {} percent of the damage.".format(
                                    defender.name, self.name, int(blk_amt * 100)))
                    elif defender.status_effects['Mana Shield'][0]:
                        damage //= defender.status_effects['Mana Shield'][1]
                        if damage > defender.mana:
                            print("The mana shield around {} absorbs {} damage.".format(defender.name, defender.mana))
                            damage -= defender.mana
                            defender.mana = 0
                            defender.status_effects['Mana Shield'][0] = False
                        else:
                            print("The mana shield around {} absorbs {} damage.".format(defender.name, damage))
                            defender.mana -= damage
                            damage = 0
                            hits[i] = False
                    if damage > 0:
                        damage = max(0, int((damage - dam_red) * (1 - resist)))
                        defender.health -= damage
                        if damage > 0:
                            print("{} {} {} for {} damage.".format(self.name, typ, defender.name, damage))
                            if sleep:
                                if not random.randint(0, 1):
                                    print("The attack awakens {}!".format(defender.name))
                                    defender.status_effects['Sleep'][0] = False
                                    defender.status_effects['Sleep'][1] = 0
                        else:
                            print("{} {} {} but deals no damage.".format(self.name, typ, defender.name))
                            hits[i] = False
                    else:
                        print("{} {} {} but deals no damage.".format(self.name, typ, defender.name))
                        hits[i] = False
                    time.sleep(0.5)
                else:
                    print("{} {} {} but misses entirely.".format(self.name, typ, defender.name))
            if hits[i] and self.equipment[att]().special and defender.is_alive():
                self.equipment[att]().special_effect(self, defender, damage=damage, crit=crits[i])
            time.sleep(0.5)
            if not defender.is_alive():
                break
            if hits[i] and defender.equipment['Armor']().special:
                defender.equipment['Armor']().special_effect(defender, self)

        return any(hits), max(crits)

    def is_alive(self):
        return self.health > 0

    def modify_inventory(self, item, num=0, subtract=False, rare=False):
        if not rare:
            if not subtract:
                if item().typ == 'Weapon' or item().typ == 'Armor' or item().typ == 'OffHand' or \
                        item().typ == 'Accessory':
                    if not item().unequip:
                        if item().name not in self.inventory:
                            self.inventory[item().name] = [item, num]
                        else:
                            self.inventory[item().name][1] += num
                else:
                    if item().name not in self.inventory:
                        self.inventory[item().name] = [item, num]
                    else:
                        self.inventory[item().name][1] += num
            else:
                self.inventory[item().name][1] -= num
                if self.inventory[item().name][1] == 0:
                    del self.inventory[item().name]
        else:
            self.special_inventory[item().name] = [item]

    def check_mod(self, mod, typ=None, luck_factor=1, ultimate=False):
        class_mod = 0
        if mod == 'weapon':
            weapon_mod = self.equipment['Weapon']().damage
            if 'Monk' in self.cls:
                class_mod += self.wisdom
            if self.cls in ['Spellblade', 'Knight Enchanter']:
                class_mod += (self.level + ((self.pro_level - 1) * 20)) * (self.mana / self.mana_max)
            if self.cls in ['Thief', 'Rogue', 'Assassin', 'Ninja']:
                class_mod += self.dex
            else:
                class_mod += self.strength
            if 'Physical Damage' in self.equipment['Ring']().mod:
                weapon_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            if self.status_effects['Attack'][0]:
                weapon_mod += self.status_effects['Attack'][2]
            return weapon_mod + class_mod
        elif mod == 'offhand':
            if 'Monk' in self.cls:
                class_mod += self.wisdom
            if self.cls in ['Spellblade', 'Knight Enchanter']:
                class_mod += (self.level + ((self.pro_level - 1) * 20)) * (self.mana / self.mana_max)
            if self.cls in ['Thief', 'Rogue', 'Assassin', 'Ninja']:
                class_mod += self.dex
            else:
                class_mod += self.strength
            try:
                off_mod = self.equipment['OffHand']().damage
                if 'Physical Damage' in self.equipment['Ring']().mod:
                    off_mod += int(self.equipment['Ring']().mod.split(' ')[0])
                if self.status_effects['Attack'][0]:
                    off_mod += self.status_effects['Attack'][2]
                return int((off_mod + class_mod) * 0.75)
            except AttributeError:
                return 0
        elif mod == 'armor':
            armor_mod = self.equipment['Armor']().armor
            if self.cls == 'Knight Enchanter':
                class_mod += self.intel * (self.mana / self.mana_max)
            if self.turtle:
                class_mod += 99
            if self.cls in ['Warlock', 'Shadowcaster']:
                if self.familiar.typ == 'Homunculus' and random.randint(0, 1) and self.familiar.pro_level > 1:
                    fam_mod = random.randint(0, 3) ** self.familiar.pro_level
                    print("{} improves {}'s armor by {}.".format(self.familiar.name, self.name, fam_mod))
                    armor_mod += fam_mod
            if 'Physical Defense' in self.equipment['Ring']().mod:
                armor_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            if self.status_effects['Defense'][0]:
                armor_mod += self.status_effects['Defense'][2]
            return armor_mod + class_mod
        elif mod == 'magic':
            magic_mod = int(self.intel // 2) * self.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                magic_mod += self.equipment['OffHand']().mod
            elif self.equipment['Weapon']().subtyp == 'Staff' or \
                    (self.cls in ['Spellblade', 'Knight Enchanter'] and
                     self.equipment['Weapon']().subtyp == 'Longsword'):
                magic_mod += int(self.equipment['Weapon']().damage * 1.5)
            if 'Magic Damage' in self.equipment['Pendant']().mod:
                magic_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            if self.status_effects['Magic'][0]:
                magic_mod += self.status_effects['Magic'][2]
            return magic_mod + class_mod
        elif mod == 'magic def':
            m_def_mod = self.wisdom
            if self.turtle:
                class_mod += 99
            if 'Magic Defense' in self.equipment['Pendant']().mod:
                m_def_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            if self.status_effects['Magic Defense'][0]:
                m_def_mod += self.status_effects['Magic Defense'][2]
            return m_def_mod + class_mod
        elif mod == 'heal':
            heal_mod = self.wisdom * self.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                heal_mod += self.equipment['OffHand']().mod
            elif self.equipment['Weapon']().subtyp == 'Staff':
                heal_mod += int(self.equipment['Weapon']().damage * 1.5)
            if self.status_effects['Magic'][0]:
                heal_mod += self.status_effects['Magic'][2]
            return heal_mod + class_mod
        elif mod == 'resist':
            if ultimate and typ == 'Physical':  # ultimate weapons by pass Physical resistance
                return 0
            try:
                res_mod = self.resistance[typ]
                if self.cls in ['Warlock', 'Shadowcaster']:
                    if self.familiar.typ == 'Mephit' and random.randint(0, 1) and self.familiar.pro_level > 1:
                        fam_mod = 0.25 * random.randint(1, max(1, self.charisma // 10))
                        print("{} increases {}'s resistance to {} by {}%.".format(self.familiar.name, self.name,
                                                                                  typ, int(fam_mod * 100)))
                        res_mod += fam_mod
                if self.equipment['Pendant']().mod == typ:
                    res_mod = 1
                return res_mod
            except KeyError:
                return 0
        elif mod == 'luck':
            luck_mod = self.charisma // luck_factor
            return luck_mod

    def statuses(self, end=False):
        """

        """

        if end:
            for key in list(self.status_effects.keys()):
                self.status_effects[key][0] = False
        else:
            if self.status_effects['Prone'][0] and all([not self.status_effects['Stun'][0],
                                                        not self.status_effects['Sleep'][0]]):
                if not random.randint(0, self.status_effects['Prone'][1]):
                    self.status_effects['Prone'][0] = False
                    print("{} is no longer prone.".format(self.name))
                else:
                    self.status_effects['Prone'][1] -= 1
                    print("{} is still prone.".format(self.name))
            if self.status_effects['Silence'][0]:
                self.status_effects['Silence'][1] -= 1
                if self.status_effects['Silence'][1] == 0:
                    print("{} is no longer silenced .".format(self.name))
                    self.status_effects['Silence'][0] = False
            if self.status_effects['Poison'][0]:
                self.status_effects['Poison'][1] -= 1
                poison_damage = self.status_effects['Poison'][2]
                poison_damage -= random.randint(0, self.con)
                if poison_damage > 0:
                    poison_damage = random.randint(poison_damage // 2, poison_damage)
                    self.health -= poison_damage
                    print("The poison damages {} for {} health points.".format(self.name, poison_damage))
                else:
                    print("{} resisted the poison.".format(self.name))
                if self.status_effects['Poison'][1] == 0:
                    self.status_effects['Poison'][0] = False
                    print("The poison has left {}.".format(self.name))
            if self.status_effects['DOT'][0]:
                self.status_effects['DOT'][1] -= 1
                dot_damage = self.status_effects['DOT'][2]
                dot_damage -= random.randint(0, self.wisdom)
                if dot_damage > 0:
                    dot_damage = random.randint(dot_damage // 2, dot_damage)
                    self.health -= dot_damage
                    print("The magic damages {} for {} health points.".format(self.name, dot_damage))
                elif dot_damage < 0:
                    self.health -= dot_damage
                    print("{} absorbs the magic for {} health points.".format(self.name, dot_damage))
                else:
                    print("{} resisted the magic.".format(self.name))
                if self.status_effects['DOT'][1] == 0:
                    self.status_effects['DOT'][0] = False
                    print("The magic affecting {} has worn off.".format(self.name))
            if self.status_effects['Blind'][0]:
                self.status_effects['Blind'][1] -= 1
                if self.status_effects['Blind'][1] == 0:
                    print("{} is no longer blind.".format(self.name))
                    self.status_effects['Blind'][0] = False
            if self.status_effects['Stun'][0]:
                self.status_effects['Stun'][1] -= 1
                if self.status_effects['Stun'][1] == 0:
                    print("{} is no longer stunned.".format(self.name))
                    self.status_effects['Stun'][0] = False
            if self.status_effects['Sleep'][0]:
                self.status_effects['Sleep'][1] -= 1
                if self.status_effects['Sleep'][1] == 0:
                    print("{} is no longer asleep.".format(self.name))
                    self.status_effects['Sleep'][0] = False
            if self.status_effects['Reflect'][0]:
                self.status_effects['Reflect'][1] -= 1
                if self.status_effects['Reflect'][1] == 0:
                    print("{} is no longer reflecting magic.".format(self.name))
                    self.status_effects['Reflect'][0] = False
            if self.status_effects['Bleed'][0]:
                self.status_effects['Bleed'][1] -= 1
                bleed_damage = self.status_effects['Bleed'][2]
                bleed_damage -= random.randint(0, self.con)
                if bleed_damage > 0:
                    bleed_damage = random.randint(bleed_damage // 2, bleed_damage)
                    self.health -= bleed_damage
                    print("The bleed damages {} for {} health points.".format(self.name, bleed_damage))
                else:
                    print("{} resisted the bleed.".format(self.name))
                if self.status_effects['Bleed'][1] == 0:
                    self.status_effects['Bleed'][0] = False
                    print("{}'s wounds have healed and is no longer bleeding.".format(self.name))
            if self.status_effects['Disarm'][0]:
                self.status_effects['Disarm'][1] -= 1
                if self.status_effects['Disarm'][1] == 0:
                    print("{} picks up their weapon.".format(self.name))
                    self.status_effects['Disarm'][0] = False
            if self.status_effects['Regen'][0]:
                self.status_effects['Regen'][1] -= 1
                heal = self.status_effects['Regen'][2]
                if heal > (self.health_max - self.health):
                    heal = (self.health_max - self.health)
                self.health += heal
                print("{}'s health has regenerated by {}.".format(self.name, heal))
                if self.status_effects['Regen'][1] == 0:
                    print("Regeneration spell ends.")
                    self.status_effects['Regen'][0] = False
            for stat in ['Attack', 'Defense', 'Magic', 'Magic Defense']:
                if self.status_effects[stat][0]:
                    self.status_effects[stat][1] -= 1
                    if self.status_effects[stat][1] == 0:
                        self.status_effects[stat][0] = False
            # Doom needs to be last
            if self.status_effects['Doom'][0]:
                self.status_effects['Doom'][1] -= 1
                if self.status_effects['Doom'][1] == 0:
                    print("The Doom countdown has expired and so has {}!".format(self.name))
                    self.health = 0

    def special_effects(self, enemy):
        pass

    def familiar_turn(self, enemy):
        pass

    def death(self):
        pass
