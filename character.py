# Imports
import time
import random
from math import exp


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

    def hit_chance(self, defender, typ='weapon'):
        """
        Things that affect hit chance
        Weapon attack: whether char is blind, if enemy is flying and/or invisible, enemy status effects,
            accessory bonuses
        Spell attack: enemy status effects
        """

        def sigmoid(x):
            return 1 / (1 + exp(-x))

        hit_mod = sigmoid(random.randint(self.dex // 2, self.dex) /
                          random.randint(defender.dex // 4, defender.dex))  # base hit percentage
        if typ == 'weapon':
            hit_mod *= (1 + int('Accuracy' in self.equipment['Ring']().mod) * 0.25)  # accuracy adds 25% chance to hit
            hit_mod *= (1 - (int(self.status_effects['Blind'][0]) * 0.5))  # blind lowers accuracy by 50%
            hit_mod *= (1 - (int(defender.invisible) * (1 / 3)))  # invisible lowers accuracy by 33.3%
            hit_mod *= (1 - (int(defender.flying) * (1 / 10)))  # flying lowers accuracy by 10%
        else:
            hit_mod = 1
            hit_mod *= (1 - (int(defender.invisible) * (1 / 3)))  # invisible lowers accuracy by 33.3%
        if hit_mod < 0:
            return 0
        return hit_mod

    def dodge_chance(self, attacker):
        a_chance = random.randint(attacker.dex // 2, attacker.dex) + attacker.check_mod('luck', luck_factor=10)
        d_chance = random.randint(0, self.dex) + self.check_mod('luck', luck_factor=15)
        chance = (d_chance - a_chance) / (a_chance + d_chance)
        chance += (0.1 * int('Dodge' in self.equipment['Ring']().mod))
        print("Dodge chance: {}".format(chance))
        return max(0, chance)

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

            if crit == 1:
                if self.equipment[att]().crit > random.random():
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
            dam_red = defender.check_mod('armor', ignore=ignore)
            resist = defender.check_mod('resist', typ='Physical', ultimate=self.equipment[att]().ultimate)
            dodge = defender.dodge_chance(self) > random.random()
            hit_per = self.hit_chance(defender, typ='weapon')
            hits[i] = (hit_per > random.random())
            if any([prone, stun, sleep]):
                dodge = False
                hits[i] = True
            # combat
            if dodge:
                if 'Parry' in list(defender.spellbook['Skills'].keys()):
                    print("{} parries {}'s attack and counterattacks!".format(defender.name, self.name))
                    _, _ = defender.weapon_damage(self)
                else:
                    print("{} evades {}'s attack.".format(defender.name, self.name))
            else:
                if hits[i]:
                    if crits[i] > 1:
                        print("Critical hit!")
                    if cover:
                        print("{} steps in front of the attack, taking the damage for {}.".format(
                            defender.familiar.name, defender.name))
                        damage = 0
                    elif ((defender.equipment['OffHand']().subtyp == 'Shield' or
                           'Dodge' in defender.equipment['Ring']().mod) and
                          not defender.status_effects['Mana Shield'][0]) and (not stun and not sleep):
                        blk_chance = defender.equipment['OffHand']().mod + \
                                     (('Block' in defender.equipment['Ring']().mod) * 0.25)
                        print("Block chance: {}".format(blk_chance))
                        if blk_chance > random.random():
                            blk_amt = (defender.strength * blk_chance) / self.strength
                            print("Block percent: {}".format(blk_amt))
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
            if item().name in self.special_inventory:
                self.special_inventory[item().name][1] += num
            else:
                self.special_inventory[item().name] = [item, num]
            self.quests(item=item)

    def check_mod(self, mod, typ=None, luck_factor=1, ultimate=False, ignore=False):
        return 0

    def statuses(self, end=False):
        """

        """
        def default(status=None, end_combat=False):
            if end_combat:
                for key in list(self.status_effects.keys()):
                    self.status_effects[key][0] = False
                    self.status_effects[key][1] = 0
                    try:
                        self.status_effects[key][2] = 0
                    except IndexError:
                        pass
            else:
                self.status_effects[status][0] = False
                self.status_effects[status][1] = 0
                try:
                    self.status_effects[status][2] = 0
                except IndexError:
                    pass

        if end:
            default(end_combat=end)
        else:
            if self.status_effects['Prone'][0] and all([not self.status_effects['Stun'][0],
                                                        not self.status_effects['Sleep'][0]]):
                if not random.randint(0, self.status_effects['Prone'][1]):
                    default(status='Prone')
                    print("{} is no longer prone.".format(self.name))
                else:
                    self.status_effects['Prone'][1] -= 1
                    print("{} is still prone.".format(self.name))
            if self.status_effects['Disarm'][0] and all([not self.status_effects['Stun'][0],
                                                        not self.status_effects['Sleep'][0]]):
                self.status_effects['Disarm'][1] -= 1
                if self.status_effects['Disarm'][1] == 0:
                    print("{} picks up their weapon.".format(self.name))
                    default(status='Disarm')
            if self.status_effects['Silence'][0]:
                self.status_effects['Silence'][1] -= 1
                if self.status_effects['Silence'][1] == 0:
                    print("{} is no longer silenced.".format(self.name))
                    default(status='Silence')
            if self.status_effects['Poison'][0]:
                self.status_effects['Poison'][1] -= 1
                poison_damage = self.status_effects['Poison'][2]
                poison_damage -= random.randint(0, self.con)
                if poison_damage > 0:
                    self.health -= poison_damage
                    print("The poison damages {} for {} health points.".format(self.name, poison_damage))
                else:
                    print("{} resisted the poison.".format(self.name))
                if self.status_effects['Poison'][1] == 0:
                    default(status='Poison')
                    print("The poison has left {}.".format(self.name))
            if self.status_effects['DOT'][0]:
                self.status_effects['DOT'][1] -= 1
                dot_damage = self.status_effects['DOT'][2]
                dot_damage -= random.randint(0, self.wisdom)
                if dot_damage > 0:
                    self.health -= dot_damage
                    print("The magic damages {} for {} health points.".format(self.name, dot_damage))
                else:
                    print("{} resisted the magic.".format(self.name))
                if self.status_effects['DOT'][1] == 0:
                    default(status='DOT')
                    print("The magic affecting {} has worn off.".format(self.name))
            if self.status_effects['Bleed'][0]:
                self.status_effects['Bleed'][1] -= 1
                bleed_damage = self.status_effects['Bleed'][2]
                bleed_damage -= random.randint(0, self.con)
                if bleed_damage > 0:
                    self.health -= bleed_damage
                    print("The bleed damages {} for {} health points.".format(self.name, bleed_damage))
                else:
                    print("{} resisted the bleed.".format(self.name))
                if self.status_effects['Bleed'][1] == 0:
                    default(status='Bleed')
                    print("{}'s wounds have healed and is no longer bleeding.".format(self.name))
            if self.status_effects['Regen'][0]:  # TODO
                self.status_effects['Regen'][1] -= 1
                heal = self.status_effects['Regen'][2]
                if heal > (self.health_max - self.health):
                    heal = (self.health_max - self.health)
                self.health += heal
                print("{}'s health has regenerated by {}.".format(self.name, heal))
                if self.status_effects['Regen'][1] == 0:
                    print("Regeneration spell ends.")
                    default(status='Regen')
            if self.status_effects['Blind'][0]:
                self.status_effects['Blind'][1] -= 1
                if self.status_effects['Blind'][1] == 0:
                    print("{} is no longer blind.".format(self.name))
                    default(status='Blind')
            if self.status_effects['Stun'][0]:
                self.status_effects['Stun'][1] -= 1
                if self.status_effects['Stun'][1] == 0:
                    print("{} is no longer stunned.".format(self.name))
                    default(status='Stun')
            if self.status_effects['Sleep'][0]:
                self.status_effects['Sleep'][1] -= 1
                if self.status_effects['Sleep'][1] == 0:
                    print("{} is no longer asleep.".format(self.name))
                    default(status='Sleep')
            if self.status_effects['Reflect'][0]:
                self.status_effects['Reflect'][1] -= 1
                if self.status_effects['Reflect'][1] == 0:
                    print("{} is no longer reflecting magic.".format(self.name))
                    default(status='Reflect')
            for stat in ['Attack', 'Defense', 'Magic', 'Magic Defense']:
                if self.status_effects[stat][0]:
                    self.status_effects[stat][1] -= 1
                    if self.status_effects[stat][1] == 0:
                        default(status=stat)
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

    def quests(self, enemy=None, item=None):
        pass
