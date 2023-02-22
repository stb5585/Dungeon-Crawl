# Imports
import os
import random
import time

import enemies
import storyline
import combat
import world
from classes import classes_dict

###########################################
""" spell manager """


class Ability:
    """
    cost: amount of mana required to cast spell
    crit: chance to double damage; higher number means lower chance to crit
    level attained: the level when you attain the spell
    """

    def __init__(self, name, description, cost):
        self.name = name
        self.description = description
        self.cost = cost
        self.combat = True

    def __str__(self):
        return "{}\n=====\n{}\nMana cost: {}\n".format(self.name, self.description, self.cost)


class Skill(Ability):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.typ = 'Skill'
        self.subtyp = None
        self.passive = False

    def use(self, user, target=None, fam=False, cover=False):
        pass


class Spell(Ability):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.typ = 'Spell'
        self.subtyp = None

    def cast(self, caster, target=None, fam=False, cover=False):
        pass


"""
Skill section
"""


# Skill types
class Offensive(Skill):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Offensive'


class Defensive(Skill):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Defensive'


class Stealth(Skill):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Stealth'


class Poison(Skill):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Poison'


class Enhance(Skill):
    """

    """

    def __init__(self, name, description, cost, mod):
        super().__init__(name, description, cost)
        self.subtyp = 'Enhance'
        self.mod = mod


class Drain(Skill):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Drain'


class Class(Skill):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Class'


class Luck(Skill):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Luck'


# Skills #
# Offensive
class ShieldSlam(Offensive):
    """

    """

    def __init__(self):
        super().__init__(name='Shield Slam', description='Slam the enemy with your shield, damaging with a chance to '
                                                         'stun.',
                         cost=3)
        self.stun = 1  # defines for how many rounds the enemy is stunned

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        dam_red = target.check_mod('armor')
        dmg_mod = int(user.strength * (2 / user.equipment['OffHand']().mod))
        if 'Physical Damage' in user.equipment['Ring']().mod:
            dmg_mod += int(user.equipment['Ring']().mod.split(' ')[0])
        chance = target.check_mod('luck', luck_factor=10)
        if random.randint(user.dex // 2, user.dex) > random.randint(chance, (target.dex // 2) + chance):
            damage = max(1, dmg_mod)
            damage = max(0, (damage - dam_red))
            target.health -= damage
            print("{} damages {} with Shield Slam for {} hit points.".format(user.name, target.name, damage))
            if target.is_alive():
                if random.randint(user.strength // 2, user.strength) \
                        > random.randint(target.strength // 2, target.strength):
                    print("{} is stunned for {} turns.".format(target.name, self.stun))
                    target.status_effects['Stun'][0] = True
                    target.status_effects['Stun'][1] = self.stun
                else:
                    print("{} fails to stun {}.".format(user.name, target.name))
        else:
            print("{} swings their shield at {} but miss entirely.".format(user.name, target.name))


class ShieldSlam2(ShieldSlam):
    """
    Replaces Shield Slam
    """

    def __init__(self):
        super().__init__()
        self.stun = 2  # defines for how many rounds the enemy is stunned
        self.cost = 10


class ShieldSlam3(ShieldSlam):
    """

    """

    def __init__(self):
        super().__init__()
        self.stun = 3  # defines for how many rounds the enemy is stunned
        self.cost = 20


class ShieldSlam4(ShieldSlam):
    """

    """

    def __init__(self):
        super().__init__()
        self.stun = 4  # defines for how many rounds the enemy is stunned
        self.cost = 30


class DoubleStrike(Offensive):
    """

    """

    def __init__(self):
        super().__init__(name='Multi-Strike', description='Perform a multiple melee attacks with the primary weapon.',
                         cost=14)
        self.strikes = 2  # number of strikes performed

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        for _ in range(self.strikes):
            _, _ = combat.weapon_damage(user, target, cover=cover)
            if not target.is_alive():
                break


class TripleStrike(DoubleStrike):
    """
    Replaces DoubleStrike
    """

    def __init__(self):
        super().__init__()
        self.strikes = 3
        self.cost = 26


class QuadStrike(DoubleStrike):
    """
    Replaces TripleStrike
    """

    def __init__(self):
        super().__init__()
        self.strikes = 4
        self.cost = 40


class FlurryBlades(DoubleStrike):
    """
    Replaces QuadStrike
    """

    def __init__(self):
        super().__init__()
        self.strikes = 5
        self.cost = 50


class PiercingStrike(Offensive):
    """

    """

    def __init__(self):
        super().__init__(name='Piercing Strike', description='Pierces the enemy\'s defenses, ignoring armor.',
                         cost=5)

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        _, _ = combat.weapon_damage(user, target, cover=cover, ignore=True)


class Jump(Offensive):
    """

    """

    def __init__(self):
        super().__init__(name='Jump', description='Leap into the air and bring down your weapon onto the enemy, '
                                                  'delivering critical damage.',
                         cost=10)
        self.strikes = 1
        self.crit = 2

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        for _ in range(self.strikes):
            _, _ = combat.weapon_damage(user, target, cover=cover, crit=2)
            if not target.is_alive():
                break


class DoubleJump(Jump):
    """
    Replaces Jump
    """

    def __init__(self):
        super().__init__()
        self.strikes = 2
        self.cost = 25


class TripleJump(Jump):
    """
    Replaces Double Jump
    """

    def __init__(self):
        super().__init__()
        self.strikes = 3
        self.cost = 40


class DoubleCast(Offensive):
    """

    """

    def __init__(self):
        super().__init__(name='Multi-Cast', description='Cast multiple spells in a single turn.',
                         cost=10)
        self.cast = 2

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        j = 0
        while j < self.cast:
            spell_list = []
            for entry in user.spellbook['Spells']:
                if user.spellbook['Spells'][entry]().cost <= user.mana:
                    if user.spellbook['Spells'][entry]().name != 'Magic Missile':
                        spell_list.append(str(entry) + '  ' + str(user.spellbook['Spells'][entry]().cost))
            if len(spell_list) == 0:
                print("{} does not have enough mana to cast any spells with Multi-Cast.".format(
                    user.name))
                user.mana += self.cost
                break
            spell_index = storyline.get_response(spell_list)
            spell = user.spellbook['Spells'][spell_list[spell_index].rsplit('  ', 1)[0]]
            spell().cast(user, target, cover=False)
            j += 1
            os.system('cls' if os.name == 'nt' else 'clear')
            if not target.is_alive():
                break


class TripleCast(DoubleCast):
    """
    Replaces DoubleCast
    """

    def __init__(self):
        super().__init__()
        self.cast = 3
        self.cost = 20


class MortalStrike(Offensive):
    """
    Critical strike plus bleed; duration and damage determined by the player's strength
    """

    def __init__(self):
        super().__init__(name='Mortal Strike', description='Assault the enemy, striking them with a critical hit and '
                                                           'placing a bleed effect that deals damage.',
                         cost=10)
        self.crit = 2

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        hit, crit = combat.weapon_damage(user, target, cover=cover, crit=self.crit)
        if hit and target.is_alive():
            if random.randint((user.strength * crit) // 2, (user.strength * crit)) \
                    > random.randint(target.con // 2, target.con):
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = user.strength // 10
                target.status_effects['Bleed'][2] = user.strength // 2
                print("{} is bleeding for {} turns.".format(target.name, user.strength // 10))


class MortalStrike2(MortalStrike):
    """
    Devastating critical strike plus bleed; duration and damage determined by the player's strength
    """

    def __init__(self):
        super().__init__()
        self.crit = 3
        self.cost = 30


# Defensive skills
class ShieldBlock(Defensive):
    """
    Passive ability
    """

    def __init__(self):
        super().__init__(name='Shield Block', description='Ready your shield after attacking in anticipation for a '
                                                          'melee attack. If the enemy attacks, it is blocked and '
                                                          'reduces the damage received.',
                         cost=0)
        self.passive = True


class Parry(Defensive):
    """
    Passive ability
    """

    def __init__(self):
        super().__init__(name='Parry', description='Passive chance to counterattack if an attack is successfully '
                                                   'dodged.',
                         cost=0)
        self.passive = True


class Disarm(Defensive):
    """

    """

    def __init__(self):
        super().__init__(name='Disarm', description='Surprise the enemy by attacking their weapon, disarming them.',
                         cost=5)
        self.turns = 1

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        if target.equipment['Weapon']().subtyp != "Natural" and target.equipment['Weapon']().subtyp != "None":
            chance = target.check_mod('luck', luck_factor=10)
            if random.randint(user.strength // 2, user.strength) \
                    > random.randint(target.dex // 2, target.dex) + chance:
                target.status_effects['Disarm'][0] = True
                target.status_effects['Disarm'][1] = self.turns
                print("{} is disarmed for {} turns.".format(target.name, self.turns))
            else:
                print("{} fails to disarm the {}.".format(name, target.name))
        else:
            print("The {} cannot be disarmed.".format(target.name))


class Disarm2(Disarm):
    """
    Replaces Disarm
    """

    def __init__(self):
        super().__init__()
        self.turns = 2
        self.cost = 15


class Disarm3(Disarm):
    """
    Replaces Disarm 2
    """

    def __init__(self):
        super().__init__()
        self.turns = 3
        self.cost = 30


class Cover(Defensive):
    """

    """

    def __init__(self):
        super().__init__(name="Cover", description="You stand in the way in the face of attack, protecting your master"
                                                   " from harm.",
                         cost=0)
        self.passive = True


# Stealth skills
class Backstab(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Backstab', description='Strike the opponent in the back, guaranteeing a hit and ignoring'
                                                      ' any resistance or armor.',
                         cost=6)

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        _, _ = combat.weapon_damage(user, target, cover=cover, ignore=True)


class Blind(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Blind', description='Throw sand in the eyes of your enemy, blinding them and reducing '
                                                   'their chance to hit on a melee attack for 2 turns.',
                         cost=8)
        self.blind = 2

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        if random.randint(user.dex // 2, user.dex) \
                > random.randint(target.dex // 2, target.dex):
            target.status_effects['Blind'][0] = True
            target.status_effects['Blind'][1] = self.blind
            print("{} is blinded for {} turns.".format(target.name, self.blind))
        else:
            print("{} fails to blind {}.".format(user.name, target.name))


class SleepingPowder(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name="Sleeping Powder", description="Releases a powerful toxin that puts the target to sleep.",
                         cost=11)
        self.turns = 2

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        if random.randint(user.dex // 2, user.dex) \
                > random.randint(target.dex // 2, target.dex):
            target.status_effects['Sleep'][0] = True
            target.status_effects['Sleep'][1] = self.turns
            print("{} is asleep for {} turns.".format(target.name, self.turns))
        else:
            print("{} fails to put {} to sleep.".format(user.name, target.name))


class KidneyPunch(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Kidney Punch', description='Punch the enemy in the kidney, rendering them stunned.',
                         cost=10)
        self.stun = 1

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        hit, crit = combat.weapon_damage(user, target, cover=cover)
        if hit and target.is_alive():
            if random.randint((user.dex * crit) // 2, (user.dex * crit)) \
                    > random.randint(target.con // 2, target.con):
                target.status_effects['Stun'][0] = True
                target.status_effects['Stun'][1] = self.stun
                print("{} is stunned for {} turns.".format(target.name, self.stun))
            else:
                print("{} fails to stun {}.".format(user.name, target.name))


class KidneyPunch2(KidneyPunch):
    """

    """

    def __init__(self):
        super().__init__()
        self.stun = 2
        self.cost = 22


class KidneyPunch3(KidneyPunch2):
    """

    """

    def __init__(self):
        super().__init__()
        self.stun = 3
        self.cost = 32


class SmokeScreen(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Smoke Screen', description='Obscure the player in a puff of smoke, allowing the '
                                                          'player to flee without fail.',
                         cost=5)


class Steal(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Steal', description='Relieve the enemy of their items.',
                         cost=6)

    def use(self, user, target=None, fam=False, cover=False, crit=1, mug=False):
        if not fam:
            name = user.name
            if not mug:
                print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            if not mug:
                print("{} uses {}.".format(name, self.name))
        if len(target.inventory) != 0:
            chance = user.check_mod('luck', luck_factor=16)
            if random.randint((user.dex * crit) // 2, (user.dex * crit)) + chance > \
                    random.randint(target.dex // 2, target.dex):
                i = random.randint(0, len(target.inventory) - 1)
                item_key = list(target.inventory.keys())[i]
                item = target.inventory[item_key]
                del target.inventory[item_key]
                if item_key == 'Gold':
                    print("{} steals {} gold from the {}.".format(name, item, target.name))
                    user.gold += item
                else:  # if monster steals from player, item is lost
                    try:
                        user.modify_inventory(item, num=1)
                    except AttributeError:
                        pass
                    print("{} steals {} from {}.".format(name, item().name, target.name))
            else:
                print("Steal fails.")
        else:
            print("{} doesn't have anything to steal.".format(target.name))


class Mug(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Mug', description='Attack the enemy with a chance to steal their items.',
                         cost=20)

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        hit, crit = combat.weapon_damage(user, target, fam=fam, cover=cover)
        if hit:
            Steal().use(user, target, fam=fam, cover=False, crit=crit, mug=True)


class Lockpick(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Lockpick', description='Unlock a locked chest.',
                         cost=12)

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        target.lock = False


# Poison Skills
class PoisonStrike(Poison):
    """

    """

    def __init__(self):
        super().__init__(name='Poison Strike', description='Attack the enemy with a chance to poison.',
                         cost=8)
        self.poison_damage = 10
        self.poison_rounds = 2

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        hit, crit = combat.weapon_damage(user, target, cover=cover)
        if hit and target.is_alive():
            resist = target.check_mod('resist', self.subtyp)
            if resist < 1:
                if random.randint((user.dex * crit) // 2, (user.dex * crit)) * (1 - resist) \
                        > random.randint(target.con // 2, target.con):
                    pois_dmg = int(self.poison_damage * (1 - resist))
                    target.status_effects['Poison'][0] = True
                    target.status_effects['Poison'][1] = self.poison_rounds
                    target.status_effects['Poison'][2] = pois_dmg
                    print("{} is poisoned for {} turns.".format(target.name, self.poison_rounds))
                    print("{} takes {} damage from the poison.".format(target.name, pois_dmg))
                    target.health -= pois_dmg
                else:
                    print("{} resists the poison.".format(target.name))
            else:
                print("{} is immune to poison.".format(target.name))


class PoisonStrike2(PoisonStrike):
    """
    Replaces Poison Strike
    """

    def __init__(self):
        super().__init__()
        self.poison_damage = 20
        self.poison_rounds = 4
        self.cost = 14


class PoisonStrike3(PoisonStrike):
    """
    Replaces Poison Strike
    """

    def __init__(self):
        super().__init__()
        self.poison_damage = 30
        self.poison_rounds = 6
        self.cost = 25


# Enhance skills
class EnhanceBlade(Enhance):
    """

    """

    def __init__(self):
        super().__init__(name='Enhance Blade', description='Enchant your weapon with magical energy to enhance the '
                                                           'weapon\'s damage.',
                         cost=6, mod=5)
        self.school = 'Arcane'

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        print("{}'s weapon has been imbued with arcane power!".format(user.name))
        _, _ = combat.weapon_damage(user, target, cover=cover, dmg_mod=self.mod)


class EnhanceBlade2(EnhanceBlade):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 10
        self.mod = 10


class EnhanceBlade3(EnhanceBlade):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 18
        self.mod = 20


class EnhanceArmor(Enhance):
    """

    """

    def __init__(self):
        super().__init__(name='Enhance Armor', description='The Knight Enchanter can imbue their armor with arcane '
                                                           'power, improving their defense modified by their '
                                                           'intelligence multiplied by the percentage of their mana.',
                         cost=0, mod=0)
        self.school = 'Arcane'
        self.passive = True


# Drain skills
class HealthDrain(Drain):
    """

    """

    def __init__(self):
        super().__init__(name='Health Drain', description='Drain the enemy, absorbing their health.',
                         cost=10)

    def use(self, user, target=None, special=False, fam=False, cover=False):
        if not special:
            if not fam:
                name = user.name
                print("{} uses {}.".format(name, self.name))
                user.mana -= self.cost
            else:
                name = user.familiar.name
                print("{} uses {}.".format(name, self.name))
        drain = random.randint((user.health + user.intel) // 5,
                               (user.health + user.intel) // 1.5)
        chance = target.check_mod('luck', luck_factor=1)
        if not random.randint(user.wisdom // 2, user.wisdom) > random.randint(0, target.wisdom // 2) + chance:
            drain = drain // 2
        if drain > target.health:
            drain = target.health
        target.health -= drain
        user.health += drain
        if user.health > user.health_max:
            user.health = user.health_max
        print("{} drains {} health from {}.".format(user.name, drain, target.name))


class ManaDrain(Drain):
    """

    """

    def __init__(self):
        super().__init__(name='Mana Drain', description='Drain the enemy, absorbing their mana.',
                         cost=0)

    def use(self, user, target=None, special=False, fam=False, cover=False):
        if not special:
            if not fam:
                name = user.name
                print("{} uses {}.".format(name, self.name))
                user.mana -= self.cost
            else:
                name = user.familiar.name
                print("{} uses {}.".format(name, self.name))
        drain = random.randint((user.mana + user.intel) // 5,
                               (user.mana + user.intel) // 1.5)
        chance = target.check_mod('luck', luck_factor=10)
        if not random.randint(user.wisdom // 2, user.wisdom) > random.randint(0, target.wisdom // 2) + chance:
            drain = drain // 2
        if drain > target.mana:
            drain = target.mana
        target.mana -= drain
        user.mana += drain
        if user.mana > user.mana_max:
            user.mana = user.mana_max
        print("{} drains {} mana from {}.".format(user.name, drain, target.name))


class HealthManaDrain(Drain):
    """
    Replaces Health Drain
    """

    def __init__(self):
        super().__init__(name='Health/Mana Drain', description='Drain the enemy, absorbing the health and mana in '
                                                               'return.',
                         cost=0)

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        HealthDrain().use(user, target, special=True, cover=False)
        ManaDrain().use(user, target, special=True, cover=False)


# Class skills
class LearnSpell(Class):
    """

    """

    def __init__(self):
        super().__init__(name='Learn Spell', description='Enables a diviner to learn rank 1 enemy spells.',
                         cost=0)
        self.passive = True


class LearnSpell2(LearnSpell):
    """
    Replaces Learn Spell
    """

    def __init__(self):
        super().__init__()


class Transform(Class):
    """
    Panther
    """

    def __init__(self):
        super().__init__(name='Transform', description='Transforms the druid into a powerful creature, assuming the '
                                                       'spells and abilities inherent to the creature.',
                         cost=0)
        self.t_creature = enemies.Panther()

    def change(self, player):
        print("{} uses {}.".format(player.name, self.name))
        if player.cls in list(classes_dict.keys()):
            combat.transform(player, self.t_creature)
        else:
            combat.transform(player, self.t_creature, back=True)


class Transform2(Transform):
    """
    Direbear
    """

    def __init__(self):
        super().__init__()
        self.t_creature = enemies.Direbear()


class Transform3(Transform):
    """
    Werewolf
    """

    def __init__(self):
        super().__init__()
        self.t_creature = enemies.Werewolf()


class Transform4(Transform):
    """
    Griffin
    """

    def __init__(self):
        super().__init__()
        self.t_creature = enemies.Griffin()


class Transform5(Transform):
    """
    Red Dragon
    """

    def __init__(self):
        super().__init__()
        self.t_creature = enemies.RedDragon()


class Familiar(Class):
    """

    """

    def __init__(self):
        super().__init__(name="Familiar", description="The warlock gains the assistance of a familiar, a magic serving "
                                                      "as both a pet and a helper. The familiar's abilities rely on its"
                                                      " master's statistics and resources.",
                         cost=0)
        self.passive = True


class Familiar2(Familiar):
    """

    """

    def __init__(self):
        super().__init__()


class Familiar3(Familiar):
    """

    """

    def __init__(self):
        super().__init__()


class ElementalStrike(Class):
    """

    """

    def __init__(self):
        super().__init__(name="Elemental Strike", description='Attack the enemy with your weapon and a random '
                                                              'elemental spell.',
                         cost=15)

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        hit, crit = combat.weapon_damage(user, target, cover=cover)
        if hit and target.is_alive():
            spell_list = [Scorch, WaterJet, Tremor, Gust]
            spell = random.choice(spell_list)
            if crit > 1:
                spell().cast(user, target, cover=False)
                spell().cast(user, target, cover=False)
            else:
                spell().cast(user, target, cover=False)


class AbsorbEssence(Class):
    """
    Currently 5% chance
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

    def __init__(self):
        super().__init__(name='Absorb Essence', description='When a Soulcatcher kills an enemy, there is a chance that '
                                                            'they may absorb part of the enemy\'s essence, increasing '
                                                            'a random statistic.',
                         cost=0)
        self.passive = True


class ChiHeal(Class):
    """

    """

    def __init__(self):
        super().__init__(name="Chi Heal", description="The monk channels his chi energy, healing 25% of their health"
                                                      " and removing all negative status effects.",
                         cost=25)

    def use(self, user, target=None, fam=False, cover=False):
        if target is None:
            target = user
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
        Heal().cast(user, target=target, fam=fam, special=True, cover=False)
        Cleanse().cast(user, target=target, fam=fam, special=True, cover=False)


# Luck
class GoldToss(Luck):
    """
    Unblockable and unresistable but enemy has chance to catch/keep some of it
    max_thrown is a percentage
    """

    def __init__(self):
        super().__init__(name="Gold Toss", description='Toss a handful of gold at the enemy, dealing damage equal to '
                                                       'the amount of gold thrown.',
                         cost=0)

    def use(self, user, target=None, fam=False, cover=False, max_thrown=None):
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
            max_thrown = 0.1
        if user.gold == 0:
            print("Nothing happens.")
        else:
            a_chance = user.check_mod('luck', luck_factor=20)
            d_chance = target.check_mod('luck', luck_factor=10)
            if max_thrown:
                gold = max(1, int(max_thrown * user.gold))
            else:
                gold = user.gold
            damage = max(1, random.randint(1, gold) // (random.randint(1, 10) // max(1, a_chance)))
            user.gold -= damage
            print("{} throws {} gold at {}.".format(name, damage, target.name))
            if not random.randint(0, 1):
                catch = random.randint(min(damage, d_chance), damage)
                damage -= catch
                target.gold += catch
                print("{} catches some of the gold thrown, gaining {} gold.".format(target.name, catch))
            else:
                pass
            target.health -= damage
            print("{} does {} damage to {}.".format(name, damage, target.name))


class SlotMachine(Luck):
    """
    Rolls 3 10-sided dice (so to speak); 1000 possible results (000 to 999)
    Possible outcomes:
    Nothing: nothing happens
    Mark of the Beast: either user (player) or enemy (bypasses Death resistance) - 666 or 999
    3 of a Kind: full health/mana, cleanse negative statuses - (000, 111, 222, 333, 444, 555, 777, 888)
    Straight: damage to enemy equal to numbers multiplied together -
        (012 = 0, 123 = 6, 234 = 24, 345 = 60, 456 = 120, 567 = 210, 678 = 336, 789 = 504, 890 = 0)
    Palindrome: casts high level spell based on middle value - (number that follow xyx format)
    Pairs:  -
        two numbers that are the same but do not meet any of the other requirements i.e. 221 but not 212
    """

    def __init__(self):
        super().__init__(name="Slot Machine", description='Pull the handle and see what comes up! Depending on the '
                                                          'results, different possible outcomes can occur.',
                         cost=15)

    def use(self, user, target=None, fam=False, cover=False):
        hands = {"Death": ["666", "999"],
                 "Trips": ["000", "111", "222", "333", "444", "555", "777", "888"],
                 'Straight': ["012", "123", "234", "345", "456", "567", "678", "789", "890"],
                 'Palindrome': ['010', '020', '030', '040', '050', '060', '070', '080', '090',
                                '101', '121', '131', '141', '151', '161', '171', '181', '191',
                                '202', '212', '232', '242', '252', '262', '272', '282', '292',
                                '303', '313', '323', '343', '353', '363', '373', '383', '393',
                                '404', '414', '424', '434', '454', '464', '474', '484', '494',
                                '505', '515', '525', '535', '545', '565', '575', '585', '595',
                                '606', '616', '626', '636', '646', '656', '676', '686', '696',
                                '707', '717', '727', '737', '747', '757', '767', '787', '797',
                                '808', '818', '828', '838', '848', '858', '868', '878', '898',
                                '909', '919', '929', '939', '949', '959', '969', '979', '989']}
        a_chance = user.check_mod('luck', luck_factor=10)
        d_chance = target.check_mod('luck', luck_factor=10)
        if not fam:
            name = user.name
            print("{} uses {}.".format(name, self.name))
        else:
            name = user.familiar.name
            print("{} uses {}.".format(name, self.name))
            user.mana -= self.cost
        success = False
        retries = 0
        while not success:
            spin = self.spin()
            if spin in hands['Death']:
                print("The mark of the beast!")
                success = True
                if a_chance >= d_chance:
                    target.health = 0
                    print("Death has come for {}!".format(target.name))
                elif d_chance > a_chance:
                    user.health = 0
                    print("Death has come for {}!".format(user.name))
            elif spin in hands['Trips']:
                print("3 of a Kind!")
                success = True
                user.health = user.health_max
                user.mana = user.mana_max
                Cleanse().cast(user, fam=fam, special=True, cover=False)
            elif spin in hands['Straight']:
                print("Straight!")
                success = True
                ints = [int(x) for x in list(spin)]
                damage = 1
                for i in ints:
                    damage *= i
                target.health -= damage
                print("{} takes {} damage.".format(target.name, damage))
            elif spin in hands['Palindrome']:
                print("Palindrome!")
                success = True
                spell_list = [MagicMissile3, Firestorm, IceBlizzard, Electrocution, Tsunami, Earthquake, Tornado,
                              ShadowBolt3, Holy3, Ultima]
                spell = spell_list[int(spin[1])]
                print("{} is cast!".format(spell().name))
                spell().cast(user, target, fam=fam, special=True, cover=False)
            elif len(set(list(spin))) == 2 and spin not in hands['Palindrome']:
                print('Pairs!')
                success = True

            else:
                if random.randint(0, a_chance) and retries < 3:
                    print("No luck, try again.")
                    retries += 1
                else:
                    success = True
                    print("Nothing happens.")

    def spin(self):
        first, second, third = ("0", "0", "0")
        i = 0
        while i < 25:
            first = random.randint(0, 9)
            print("\t" + str(first) + "**", end="\r")
            time.sleep(0.05)
            i += 1

        j = 0
        while j < 25:
            second = random.randint(0, 9)
            print("\t" + str(first) + str(second) + "*", end="\r")
            time.sleep(0.05)
            j += 1

        k = 0
        while k < 25:
            third = random.randint(0, 9)
            print("\t" + str(first) + str(second) + str(third), end="\r")
            time.sleep(0.05)
            k += 1

        print("\t" + str(first) + str(second) + str(third))
        time.sleep(1)

        return str(first) + str(second) + str(third)


"""
Spell section
"""


# Spell types
class Attack(Spell):
    """

    """

    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.turns = None

    def cast(self, caster, target=None, fam=False, special=False, cover=False):
        if not special:
            if not fam:
                name = caster.name
                print("{} casts {}.".format(name, self.name))
                caster.mana -= self.cost
            else:
                name = caster.familiar.name
                print("{} casts {}.".format(name, self.name))
        else:
            if not fam:
                name = caster.name
            else:
                name = caster.familiar.name
        stun = target.status_effects['Stun'][0]
        reflect = target.status_effects['Reflect'][0]
        spell_mod = caster.check_mod('magic')
        chance = target.check_mod('luck', luck_factor=15)
        if random.randint(0, target.dex // 2) + chance > \
                random.randint(caster.intel // 2, caster.intel) and not stun and not reflect:
            print("{} dodged the {} and was unhurt.".format(target.name, self.name))
        else:
            damage = 0
            spell_dmg = int(self.damage + spell_mod)
            if reflect:
                target = caster
                print("{} is reflected back at {}!".format(self.name, caster.name))
            resist = target.check_mod('resist', typ=self.subtyp)
            dam_red = target.check_mod('magic def')
            damage += int(random.randint(spell_dmg // 2, spell_dmg) * (1 - resist))
            if damage < 0:
                crit = 1
                if not random.randint(0, self.crit):
                    crit = 2
                damage *= crit
                if crit == 2:
                    print("Critical Hit!")
                print("{} absorbs {} and is healed for {} health.".format(target.name, self.subtyp, abs(damage)))
            else:
                damage -= random.randint(dam_red // 2, dam_red)
                crit = 1
                if not random.randint(0, self.crit):
                    crit = 2
                damage *= crit
                if crit == 2:
                    print("Critical Hit!")
                if random.randint(0, target.con // 2) > \
                        random.randint((caster.intel * crit) // 2, (caster.intel * crit)):
                    damage //= 2
                    print("{} shrugs off the {} and only receives half of the damage.".format(target.name, self.name))
                    print("{} damages {} for {} hit points.".format(name, target.name, damage))
                else:
                    if damage <= 0:
                        print("{} was ineffective and does 0 damage.".format(self.name))
                        damage = 0
                    else:
                        print("{} damages {} for {} hit points.".format(name, target.name, damage))
                if self.turns and target.is_alive():
                    self.dot(caster, target, damage, crit, dam_red, resist, fam=fam)
            target.health -= damage

    def dot(self, caster, target, damage, crit, dam_red, resist, fam=False):
        pass


class HolySpell(Spell):
    """

    """

    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Holy'

    def cast(self, caster, target=None, fam=False, cover=False):
        pass


class SupportSpell(Spell):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)

    def cast(self, caster, target=None, fam=False, cover=False):
        pass


class DeathSpell(Spell):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Death'

    def cast(self, caster, target=None, fam=False, cover=False):
        pass


class StatusSpell(Spell):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = None

    def cast(self, caster, target=None, fam=False, cover=False):
        pass


class HealSpell(Spell):
    """

    """

    def __init__(self, name, description, cost, heal, crit):
        super().__init__(name, description, cost)
        self.heal = heal
        self.crit = crit
        self.turns = 0
        self.subtyp = 'Heal'
        self.combat = False

    def cast(self, caster, target=None, fam=False, special=False, cover=False):
        if target is None:
            target = caster
        if not special:
            if not fam:
                name = caster.name
                print("{} casts {}.".format(name, self.name))
                caster.mana -= self.cost
            else:
                name = caster.familiar.name
                print("{} casts {}.".format(name, self.name))
        else:
            if not fam:
                name = caster.name
            else:
                name = caster.familiar.name
        crit = 1
        heal_mod = caster.check_mod('heal')
        heal = int((random.randint(target.health_max // 2, target.health_max) * self.heal) + heal_mod)
        if self.turns:
            self.hot(target, heal)
        else:
            if not random.randint(0, self.crit):
                print("Critical Heal!")
                crit = 2
            heal *= crit
            target.health += heal
            print("{} heals {} for {} hit points.".format(name, target.name, heal))
            if target.health >= target.health_max:
                target.health = target.health_max
                print("{} is at full health.".format(target.name))

    def cast_out(self, player):
        player.mana -= self.cost
        print("{} casts {}.".format(player.name, self.name))
        if player.health == player.health_max:
            print("You are already at full health.")
            return
        crit = 1
        heal_mod = player.check_mod('heal')
        heal = int(player.health_max * self.heal + heal_mod)
        if not random.randint(0, self.crit):
            print("Critical Heal!")
            crit = 2
        heal *= crit
        player.health += heal
        print("{} heals themself for {} hit points.".format(player.name, heal))
        if player.health >= player.health_max:
            player.health = player.health_max
            print("{} is at full health.".format(player.name))

    def hot(self, caster, heal):
        pass


class MovementSpell(Spell):
    """

    """

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Movement'

    def cast(self, caster, target=None, fam=False, cover=False):
        pass


# Spells
class MagicMissile(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Magic Missile', description='Orbs of energy shoots forth from the caster, dealing '
                                                           'non-elemental damage.',
                         cost=5, damage=8, crit=8)
        self.subtyp = 'Non-elemental'
        self.missiles = 1

    def cast(self, caster, target=None, fam=False, special=False, cover=False):
        if not special:
            if not fam:
                name = caster.name
                print("{} casts {}.".format(name, self.name))
                caster.mana -= self.cost
            else:
                name = caster.familiar.name
                print("{} casts {}.".format(name, self.name))
        else:
            if not fam:
                name = caster.name
            else:
                name = caster.familiar.name
        stun = target.status_effects['Stun'][0]
        reflect = target.status_effects['Reflect'][0]
        spell_mod = caster.check_mod('magic')
        chance = target.check_mod('luck', luck_factor=15)
        for _ in range(self.missiles):
            if random.randint(0, target.dex // 2) + chance > \
                    random.randint(caster.intel // 2, caster.intel) and not stun:
                print("{} dodged the {} and was unhurt.".format(target.name, self.name))
            else:
                damage = 0
                damage += random.randint(self.damage + spell_mod // 2, (self.damage + spell_mod))
                if reflect:
                    target = caster
                    print("{} is reflected back at {}!".format(self.name, caster.name))
                dam_red = target.check_mod('magic def')
                damage -= random.randint(dam_red // 2, dam_red)
                crit = 1
                if not random.randint(0, self.crit):
                    crit = 2
                damage *= crit
                if crit == 2:
                    print("Critical Hit!")
                if random.randint(0, target.con // 2) > \
                        random.randint(caster.intel // 2, caster.intel):
                    damage //= 2
                    print("{} shrugs off the {} and only receives half of the damage.".format(target.name,
                                                                                              self.name))
                    print("{} damages {} for {} hit points.".format(name, target.name, damage))
                else:
                    if damage <= 0:
                        print("{} was ineffective and does 0 damage".format(self.name))
                    else:
                        print("{} damages {} for {} hit points.".format(name, target.name, damage))
                target.health -= damage
                os.system('cls' if os.name == 'nt' else 'clear')
                if not target.is_alive():
                    break
            time.sleep(0.1)


class MagicMissile2(MagicMissile):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 18
        self.missiles = 2


class MagicMissile3(MagicMissile):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 40
        self.missiles = 3


class Ultima(Attack):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Ultima', description='Envelopes the enemy in a magical void, dealing massive non-'
                                                    'elemental damage.',
                         cost=35, damage=50, crit=4)
        self.subtyp = 'Non-elemental'
        self.rank = 2


class Firebolt(Attack):
    """
    Arcane fire spells have lower crit but hit harder on average
    """

    def __init__(self):
        super().__init__(name='Firebolt', description='A mote of fire propelled at the foe.',
                         cost=2, damage=8, crit=10)
        self.subtyp = 'Fire'
        self.school = 'Arcane'


class Fireball(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Fireball', description='A giant ball of fire that consumes the enemy.',
                         cost=10, damage=25, crit=8)
        self.subtyp = 'Fire'
        self.school = 'Arcane'


class Firestorm(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Firestorm', description='Fire rains from the sky, incinerating the enemy.',
                         cost=20, damage=40, crit=6)
        self.subtyp = 'Fire'
        self.school = 'Arcane'


class Scorch(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Scorch', description='Light a fire and watch the enemy burn!',
                         cost=10, damage=14, crit=10)
        self.subtyp = 'Fire'
        self.school = 'Elemental'


class MoltenRock(Attack):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Molten Rock', description='A giant, molten boulder is hurled at the enemy, dealing great'
                                                         ' fire damage.',
                         cost=16, damage=28, crit=8)
        self.subtyp = 'Fire'
        self.school = 'Elemental'
        self.rank = 1


class Volcano(Attack):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Volcano', description='A mighty eruption burst out from beneath the enemy\' feet, '
                                                     'dealing massive fire damage.',
                         cost=24, damage=48, crit=6)
        self.subtyp = 'Fire'
        self.school = 'Elemental'
        self.rank = 2


class IceLance(Attack):
    """
    Arcane ice spells have lower average damage but have the highest chance to crit
    """

    def __init__(self):
        super().__init__(name='Ice Lance', description='A javelin of ice launched at the enemy.',
                         cost=4, damage=8, crit=4)
        self.subtyp = 'Ice'
        self.school = 'Arcane'


class Icicle(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Icicle', description='Frozen shards rain from the sky.',
                         cost=9, damage=15, crit=3)
        self.subtyp = 'Ice'
        self.school = 'Arcane'


class IceBlizzard(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Ice Blizzard', description='The enemy is encased in a blistering cold, penetrating into '
                                                          'its bones.',
                         cost=18, damage=25, crit=2)
        self.subtyp = 'Ice'
        self.school = 'Arcane'


class Shock(Attack):
    """
    Arcane electric spells have better crit than fire and better damage than ice
    """

    def __init__(self):
        super().__init__(name='Shock', description='An electrical arc from the caster\'s hands to the enemy.',
                         cost=6, damage=12, crit=7)
        self.subtyp = 'Electric'
        self.school = 'Arcane'


class Lightning(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Lightning', description='Throws a bolt of lightning at the enemy.',
                         cost=15, damage=22, crit=6)
        self.subtyp = 'Electric'
        self.school = 'Arcane'


class Electrocution(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Electrocution', description='A million volts of electricity passes through the enemy.',
                         cost=25, damage=38, crit=5)
        self.subtyp = 'Electric'
        self.school = 'Arcane'


class WaterJet(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Water Jet', description='A jet of water erupts from beneath the enemy\'s feet.',
                         cost=6, damage=12, crit=5)
        self.subtyp = 'Water'
        self.school = 'Elemental'


class Aqualung(Attack):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Aqualung', description='Giant water bubbles surround the enemy and burst, causing great '
                                                      'water damage.',
                         cost=13, damage=20, crit=4)
        self.subtyp = 'Water'
        self.school = 'Elemental'
        self.rank = 1


class Tsunami(Attack):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Water Jet', description='A massive tidal wave cascades over your foes.',
                         cost=26, damage=32, crit=3)
        self.subtyp = 'Water'
        self.school = 'Elemental'
        self.rank = 2


class Tremor(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Tremor', description='The ground shakes, causing objects to fall and damage the enemy.',
                         cost=3, damage=7, crit=7)
        self.subtyp = 'Earth'
        self.school = 'Elemental'


class Mudslide(Attack):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Mudslide', description='A torrent of mud and earth sweep over the enemy, causing earth '
                                                      'damage.',
                         cost=16, damage=27, crit=6)
        self.subtyp = 'Earth'
        self.school = 'Elemental'
        self.rank = 1


class Earthquake(Attack):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Earthquake', description='The cave wall and ceiling are brought down by a massive '
                                                        'seismic event, dealing devastating earth damage.',
                         cost=26, damage=41, crit=5)
        self.subtyp = 'Earth'
        self.school = 'Elemental'
        self.rank = 2


class Gust(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Gust', description='A strong gust of wind whips past the enemy.',
                         cost=12, damage=15, crit=6)
        self.subtyp = 'Wind'
        self.school = 'Elemental'


class Hurricane(Attack):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Hurricane', description='A violent storm berates your foes, causing great wind damage.',
                         cost=22, damage=26, crit=4)
        self.subtyp = 'Wind'
        self.school = 'Elemental'
        self.rank = 1


class Tornado(Attack):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Tornado', description='You bring down a cyclone that pelts the enemy with debris and '
                                                     'causes massive wind damage.',
                         cost=40, damage=40, crit=2)
        self.subtyp = 'Wind'
        self.school = 'Elemental'
        self.rank = 2


class ShadowBolt(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Shadow Bolt', description='Launch a bolt of magic infused with dark energy, damaging the'
                                                         ' enemy.',
                         cost=8, damage=15, crit=5)
        self.subtyp = 'Shadow'
        self.school = 'Shadow'


class ShadowBolt2(ShadowBolt):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 20
        self.damage = 35
        self.crit = 4


class ShadowBolt3(ShadowBolt):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 30
        self.damage = 45
        self.crit = 3


class Corruption(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Corruption', description='Damage the enemy and add a debuff that does damage over time.',
                         cost=10, damage=8, crit=5)
        self.subtyp = 'Shadow'
        self.turns = 2

    def dot(self, caster, target, damage, crit, dam_red, resist, fam=False):
        if not fam:
            name = caster.name
        else:
            name = caster.familiar.name
        if random.randint((caster.intel * crit) // 2, (caster.intel * crit)) * (1 - resist) \
                > random.randint(target.wisdom // 2, target.wisdom):
            spell_dmg = int((damage + caster.intel - dam_red) * (1 - resist))
            if spell_dmg > 0:
                target.status_effects["DOT"][0] = True
                target.status_effects["DOT"][1] = self.turns
                target.status_effects["DOT"][2] = spell_dmg
                print("{}'s magic penetrates {}'s defenses.".format(name, target.name))
            else:
                print("{} was ineffective and does 0 damage.".format(self.name))
        else:
            print("The magic has no effect.")


class Corruption2(Corruption):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 25
        self.damage = 25
        self.crit = 4
        self.turns = 4


class Terrify(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Terrify', description='Get in the mind of the enemy, terrifying them into inaction and '
                                                     'doing damage in the process.',
                         cost=15, damage=10, crit=4)
        self.turns = 1

    def dot(self, caster, target, damage, crit, dam_red, resist, fam=False):
        if not fam:
            name = caster.name
        else:
            name = caster.familiar.name
        if random.randint((caster.intel * crit) // 2, (caster.intel * crit)) * (1 - resist) \
                > random.randint(target.wisdom // 2, target.wisdom):
            target.status_effects["Stun"][0] = True
            target.status_effects["Stun"][1] = self.turns
            print("{} stunned {} for {} turns.".format(name, target.name, self.turns))


class Terrify2(Terrify):
    """

    """

    def __init__(self):
        super().__init__()
        self.turns = 2
        self.cost = 20
        self.damage = 15
        self.crit = 3


class Terrify3(Terrify):
    """

    """

    def __init__(self):
        super().__init__()
        self.turns = 3
        self.cost = 25
        self.damage = 20
        self.crit = 2


class Doom(DeathSpell):
    """
    Can't be reflected
    """
    def __init__(self):
        super().__init__(name='Doom', description='Places a timer on the enemy\'s life, ending it when the timer '
                                                  'expires.',
                         cost=15)
        self.timer = 3

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        resist = target.check_mod('resist', typ=self.subtyp)
        chance = target.check_mod('luck', luck_factor=10)
        if resist < 1:
            if random.randint(caster.intel // 4, caster.intel) * (1 - resist) \
                    > random.randint(target.wisdom // 2, target.wisdom) + chance:
                target.status_effects["Doom"][0] = True
                target.status_effects["Doom"][1] = self.timer
                print("{}'s magic places a timer on {}'s life and "
                      "will expire in {} turns.".format(name, target.name, self.timer))
            else:
                print("The magic has no effect.")
        else:
            print("{} is immune to death spells.".format(target.name))


class Desoul(DeathSpell):
    """
    Can't be reflected
    """

    def __init__(self):
        super().__init__(name='Desoul', description='Removes the soul from the enemy, instantly killing it.',
                         cost=50)

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        resist = target.check_mod('resist', typ=self.subtyp)
        chance = target.check_mod('luck', luck_factor=10)
        if resist < 1:
            if random.randint(0, caster.intel) * (1 - resist) \
                    > random.randint(target.con // 2, target.con) + chance:
                target.health = 0
                print("{} has their soul ripped right out and falls to the ground dead.".format(target.name))
            else:
                print("The spell has no effect.")
        else:
            print("{} is immune to death spells.".format(target.name))


class Petrify(DeathSpell):
    """
    Rank 2 Enemy Spell; Can't be reflected except by Medusa Shield
    """

    def __init__(self):
        super().__init__(name='Petrify', description='Gaze at the enemy and turn them into stone.',
                         cost=50)
        self.rank = 2

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        if target.equipment['OffHand']().name == 'MEDUSA SHIELD':
            print("{} uses the Medusa Shield to reflect {} back at {}!".format(target.name, self.name, caster.name))
            target = caster
        resist = target.check_mod('resist', typ=self.subtyp)
        chance = target.check_mod('luck', luck_factor=1)
        if resist < 1:
            if random.randint(0, caster.intel) * (1 - resist) \
                    > random.randint(target.con // 2, target.con) + chance:
                target.health = 0
                print("{} is turned to stone!".format(target.name))
            else:
                print("The spell has no effect.")
        else:
            print("{} is immune to death spells.".format(target.name))


class Smite(HolySpell):
    """
    Can't be reflected
    """

    def __init__(self):
        super().__init__(name='Smite', description='The power of light rebukes the enemy, adding bonus holy damage to '
                                                   'a successful attack roll.',
                         cost=10, damage=20, crit=4)
        self.school = 'Holy'

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        hit, crit = combat.weapon_damage(caster, target, cover=cover)
        if hit and target.is_alive():
            spell_mod = caster.check_mod('magic')
            dam_red = target.check_mod('magic def')
            resist = target.check_mod('resist', 'Holy')
            spell_dmg = int(self.damage + spell_mod)
            damage = int(random.randint(spell_dmg // 2, spell_dmg))
            damage = int(damage * (1 - resist))
            damage *= crit
            if damage < 0:
                print("{} absorbs {} and is healed for {} health.".format(target.name, self.subtyp, abs(damage)))
            else:
                damage -= random.randint(dam_red // 2, dam_red)
                if random.randint(0, target.con // 2) > \
                        random.randint((caster.intel * crit) // 2, (caster.intel * crit)):
                    damage //= 2
                    print("{} shrugs off the {} and only receives half of the damage.".format(target.name, self.name))
                    print("{} smites {} for {} hit points.".format(name, target.name, damage))
                else:
                    if damage <= 0:
                        damage = 0
                        print("{} was ineffective and does 0 damage.".format(self.name))
                    else:
                        print("{} smites {} for {} hit points.".format(name, target.name, damage))
            target.health -= damage


class Smite2(Smite):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 20
        self.damage = 35
        self.crit = 3


class Smite3(Smite):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 32
        self.damage = 50
        self.crit = 2


class Holy(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Holy', description='The enemy is bathed in a holy light, cleansing it of evil.',
                         cost=4, damage=10, crit=10)


class Holy2(Holy):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 12
        self.damage = 24
        self.crit = 8


class Holy3(Holy):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 28
        self.damage = 45
        self.crit = 6


class TurnUndead(HolySpell):
    """
    chance is the value entered into the random function to determine result (i.e. chance of 3 has a 25% of working)
    crit will double chance of kill or double damage
    """

    def __init__(self):
        super().__init__(name="Turn Undead", description="A holy chant is recited with a chance to banish any nearby "
                                                         "undead from existence.",
                         cost=12, damage=5, crit=5)
        self.chance = 3

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        if target.enemy_typ == "Undead":
            crit = 1
            chance = self.chance
            if not random.randint(0, self.crit):
                print("Critical hit!")
                crit = 2
                chance -= 1
            if not random.randint(0, chance):
                target.health = 0
                print("The {} has been rebuked, destroying the undead monster.".format(target.name))
            else:
                spell_mod = caster.check_mod('magic')
                dam_red = target.check_mod('magic def')
                resist = target.check_mod('resist', 'Holy')
                spell_dmg = int(self.damage + spell_mod)
                damage = random.randint(spell_dmg // 2, spell_dmg)
                damage *= crit
                damage = int(damage * (1 - resist))
                damage -= dam_red
                target.health -= damage
                print("{} damages {} for {} hit points.".format(name, target.name, damage))
        else:
            print("The spell does nothing.")


class TurnUndead2(TurnUndead):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 20
        self.damage = 13
        self.crit = 3
        self.chance = 2  # 33% chance


class Heal(HealSpell):
    """
    Critical heal will double healing amount
    """

    def __init__(self):
        super().__init__(name='Heal', description='A glowing light envelopes your body and heals you for a percentage '
                                                  'of the target\'s health.',
                         cost=12, heal=0.25, crit=5)


class Heal2(Heal):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 25
        self.heal = 0.5
        self.crit = 3


class Heal3(Heal):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 35
        self.heal = 0.75
        self.crit = 2


class Regen(HealSpell):
    """

    """

    def __init__(self):
        super().__init__(name='Regen', description='Cooling waters stimulate your natural healing ability, regenerating'
                                                   ' health over time.',
                         cost=8, heal=0.1, crit=5)
        self.combat = True
        self.turns = 3

    def hot(self, target, heal):
        target.status_effects['Regen'][0] = True
        target.status_effects['Regen'][1] = self.turns
        target.status_effects['Regen'][2] = heal


class Regen2(Regen):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 18
        self.heal = 0.2


class Regen3(Regen):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 30
        self.heal = 0.3


class Bless(SupportSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Bless", description="A prayer is spoken, bestowing a mighty blessing upon the caster's "
                                                   "weapon, increasing melee damage.",
                         cost=5)
        self.mod = 5
        self.turns = 3

    def cast(self, caster, target=None, fam=False, cover=False):
        if target is None:
            target = caster
        if not fam:
            target = caster
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        print("{}'s attack increases by {} for {} turns.".format(target.name, self.mod, self.turns - 1))
        target.status_effects['Attack'][0] = True
        target.status_effects['Attack'][1] = self.turns
        target.status_effects['Attack'][2] = self.mod


class Bless2(Bless):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 12
        self.mod = 15
        self.turns = 5


class Boost(SupportSpell):
    """
    Increases magic damage
    """

    def __init__(self):
        super().__init__(name="Boost", description="Supercharge the magic capabilities of the target, increasing magic"
                                                   " damage.",
                         cost=22)
        self.mod = 20  # TODO
        self.turns = 3

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            target = caster
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        print("{}'s magic increases by {} for {} turns.".format(target.name, self.mod, self.turns))
        target.status_effects['Magic'][0] = True
        target.status_effects['Magic'][1] = self.turns
        target.status_effects['Magic'][2] = self.mod


class ManaShield(SupportSpell):
    """
    Reduction indicates how much damage a single mana point reduces
    """

    def __init__(self):
        super().__init__(name="Mana Shield", description="A protective shield envelopes the caster, absorbing damage "
                                                         "at the expense of mana.",
                         cost=0)
        self.reduction = 1

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            target = caster
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))


class ManaShield2(ManaShield):
    """

    """

    def __init__(self):
        super().__init__()
        self.reduction = 2


class Reflect(SupportSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Reflect", description="A magical shield surrounds the user, reflecting incoming spells "
                                                     "back at the caster.",
                         cost=14)
        self.turns = 2

    def cast(self, caster, target=None, fam=False, cover=False):
        if target is None:
            target = caster
        if not fam:
            target = caster
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        target.status_effects['Reflect'][0] = True
        target.status_effects['Reflect'][1] = self.turns
        print("A magic force field envelopes {}.".format(target.name))


class Resurrection(SupportSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Resurrection", description="The ultimate boon bestowed upon only the chosen few. Life "
                                                          "returns where it once left.",
                         cost=0)
        self.passive = True

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            max_heal = target.health_max - target.health
            if target.mana > max_heal:
                target.health = target.health_max
                target.mana -= max_heal
                print("{} expends mana but is healed to full life!".format(target.name, max_heal, max_heal))
            else:
                target.health += target.mana
                print("{} expends all mana but is healed for {} hit points!".format(target.name, target.mana))
                target.mana = 0
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
            heal = int(target.health_max * 0.1)
            target.health = heal
            print("{} is brought back to life and is healed for {} hit points.".format(target.name, heal))


class Cleanse(SupportSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Cleanse", description="You feel all ailments leave your body like a draught of panacea.",
                         cost=20)

    def cast(self, caster, target=None, fam=False, special=False, cover=False):
        if not special:
            if not fam:
                target = caster
                name = caster.name
                print("{} casts {}.".format(name, self.name))
                caster.mana -= self.cost
            else:
                name = caster.familiar.name
                print("{} casts {}.".format(name, self.name))
        if target is None:
            target = caster
        target.status_effects['Stun'][0] = False
        target.status_effects['Doom'][0] = False
        target.status_effects['Blind'][0] = False
        target.status_effects['Sleep'][0] = False
        target.status_effects['Poison'][0] = False
        target.status_effects['DOT'][0] = False
        target.status_effects['Bleed'][0] = False


class Sanctuary(MovementSpell):
    """

    """

    def __init__(self):
        super().__init__(name='Sanctuary', description='Return to town from anywhere in the dungeon.',
                         cost=100)

    def cast_out(self, player):
        player.mana -= self.cost
        print("{} casts Sanctuary and is transported back to town.".format(player.name))
        player.health = player.health_max
        player.mana = player.mana_max
        player.location_x, player.location_y, player.location_z = world.starting_position


class Teleport(MovementSpell):
    """

    """

    def __init__(self):
        super().__init__(name='Teleport', description='Teleport to another location on the current level.',
                         cost=50)

    def cast_out(self, player):
        pass


class BlindingFog(StatusSpell):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__(name="Blinding Fog", description="The enemy is surrounding in a thick fog, lowering the chance"
                                                          " to hit on a melee attack.",
                         cost=7)
        self.subtyp = 'Status'
        self.turns = 2
        self.rank = 1

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        if random.randint(caster.intel // 2, caster.intel) \
                > random.randint(target.con // 2, target.con):
            target.status_effects['Blind'][0] = True
            target.status_effects['Blind'][1] = self.turns
            print("{} is blinded for {} turns.".format(target.name, self.turns))
        else:
            print("The spell had no effect.")


class PoisonBreath(Attack):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__(name="Poison Breath", description="Your spew forth a toxic breath, dealing poison damage and "
                                                           "poisoning the target for 4 turns.",
                         cost=20, damage=15, crit=5)
        self.subtyp = 'Poison'
        self.school = 'Poison'
        self.turns = 4
        self.rank = 2

    def dot(self, caster, target, damage, crit, dam_red, resist, fam=False):
        if not fam:
            name = caster.name
        else:
            name = caster.familiar.name
        if random.randint((caster.intel * crit) // 2, (caster.intel * crit)) \
                > random.randint(target.con // 2, target.con):
            target.status_effects['Poison'][0] = True
            target.status_effects['Poison'][1] = self.turns
            target.status_effects['Poison'][2] = damage // self.turns
            print("{} poisons {} for {} turns.".format(name, target.name, self.turns))
        else:
            print("{} resists the poison.".format(target.name))


class DiseaseBreath(StatusSpell):
    """
    Enemy Spell; not learnable by player
    """

    def __init__(self):
        super().__init__(name="Disease Breath", description="A diseased cloud emanates onto the enemy, with a chance to"
                                                            " lower the enemy's constitution permanently.",
                         cost=25)
        self.school = 'Disease'

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        if random.randint(caster.intel // 2, caster.intel) > \
                random.randint(target.con // 2, target.con):
            if not random.randint(0, 9):
                print("The disease cripples {}, lowering their constitution by 1.")
                target.con -= 1
            else:
                print("The spell does nothing.")
        else:
            print("The spell does nothing.")


class Sleep(StatusSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Sleep", description="A magical tune lulls the target to sleep.",
                         cost=9)
        self.turns = 3

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        if random.randint(caster.intel // 2, caster.intel) \
                > random.randint(target.wisdom // 2, target.wisdom):
            target.status_effects['Sleep'][0] = True
            target.status_effects['Sleep'][1] = self.turns
            print("{} is asleep for {} turns.".format(target.name, self.turns))
        else:
            print("{} fails to put {} to sleep.".format(name, target.name))


class Stupefy(StatusSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Stupefy", description="Hit your enemy so hard, they go stupid and cannot act.",
                         cost=14)
        self.turns = 2

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            name = caster.name
            print("{} casts {}.".format(name, self.name))
            caster.mana -= self.cost
        else:
            name = caster.familiar.name
            print("{} casts {}.".format(name, self.name))
        if random.randint(caster.intel // 2, caster.intel) \
                > random.randint(target.wisdom // 2, target.wisdom):
            target.status_effects['Stun'][0] = True
            target.status_effects['Stun'][1] = self.turns
            print("{} is stunned for {} turns.".format(target.name, self.turns))
        else:
            print("{} fails to stun {}.".format(name, target.name))


# Parameters
skill_dict = {'Warrior': {'3': ShieldSlam,
                          '8': PiercingStrike,
                          '10': Disarm,
                          '13': Parry,
                          '17': DoubleStrike},
              'Weapon Master': {'1': MortalStrike,
                                '4': Disarm2,
                                '10': TripleStrike},
              'Berserker': {'2': Disarm3,
                            '5': MortalStrike2,
                            '10': QuadStrike},
              'Paladin': {'4': ShieldSlam2,
                          '6': ShieldBlock,
                          '20': ShieldSlam3},
              'Crusader': {'5': MortalStrike,
                           '10': ShieldSlam4},
              'Lancer': {'2': Jump,
                         '15': DoubleJump},
              'Dragoon': {'5': ShieldSlam2,
                          '10': ShieldBlock,
                          '20': TripleJump,
                          '25': ShieldSlam3},
              'Mage': {},
              'Sorcerer': {'10': DoubleCast},
              'Wizard': {'15': TripleCast},
              'Warlock': {'1': Familiar,
                          '5': HealthDrain,
                          '15': ManaDrain,
                          '20': Familiar2},
              'Shadowcaster': {'10': HealthManaDrain,
                               '20': Familiar3},
              'Spellblade': {'15': Parry},
              'Knight Enchanter': {'10': DoubleStrike},
              'Footpad': {'3': Disarm,
                          '5': SmokeScreen,
                          '6': Blind,
                          '8': Backstab,
                          '10': Steal,
                          '12': KidneyPunch,
                          '16': DoubleStrike,
                          '19': SleepingPowder,
                          '20': Parry},
              'Thief': {'5': Lockpick,
                        '8': TripleStrike,
                        '12': KidneyPunch2,
                        '14': Disarm2,
                        '15': Mug,
                        '20': PoisonStrike},
              'Rogue': {'10': KidneyPunch3,
                        '15': Disarm3,
                        '17': PoisonStrike2,
                        '20': QuadStrike},
              'Inquisitor': {'1': ShieldSlam,
                             '12': TripleStrike,
                             '15': ShieldBlock,
                             '18': MortalStrike},
              'Seeker': {'5': ShieldSlam2,
                         '13': Parry,
                         '25': ShieldSlam3},
              'Assassin': {'2': Disarm2,
                           '5': TripleStrike,
                           '8': PoisonStrike,
                           '10': KidneyPunch2,
                           '15': Lockpick,
                           '17': Disarm3,
                           '20': QuadStrike},
              'Ninja': {'4': PoisonStrike2,
                        '8': Mug,
                        '20': KidneyPunch3,
                        '25': FlurryBlades},
              'Healer': {},
              'Cleric': {'6': ShieldSlam,
                         '12': ShieldBlock},
              'Templar': {'2': Parry,
                          '9': ShieldSlam2},
              'Priest': {},
              'Archbishop': {'5': DoubleCast},
              'Monk': {'3': DoubleStrike,
                       '5': ChiHeal,
                       '19': TripleStrike},
              'Master Monk': {'10': QuadStrike},
              'Pathfinder': {},
              'Druid': {'1': Transform,
                        '10': Transform2},
              'Lycan': {'1': Transform3,
                        '10': Transform4,
                        '20': Transform5},
              'Diviner': {'1': LearnSpell,
                          '18': DoubleCast},
              'Geomancer': {'1': LearnSpell2,
                            '25': TripleCast},
              'Shaman': {'1': ElementalStrike,
                         '14': DoubleStrike},
              'Soulcatcher': {'1': AbsorbEssence,
                              '2': Parry,
                              '9': TripleStrike},
              }

spell_dict = {'Warrior': {},
              'Weapon Master': {},
              'Berserker': {},
              'Paladin': {'2': Heal,
                          '4': Smite,
                          '16': Heal2},
              'Crusader': {'3': Smite2,
                           '8': Heal3,
                           '16': Cleanse,
                           '18': Smite3},
              'Lancer': {},
              'Dragoon': {},
              'Mage': {'2': Firebolt,
                       '6': MagicMissile,
                       '8': IceLance,
                       '13': Shock},
              'Sorcerer': {'2': Icicle,
                           '6': Reflect,
                           '8': Lightning,
                           '10': Sleep,
                           '15': Fireball,
                           '18': MagicMissile2},
              'Wizard': {'4': Firestorm,
                         '7': Boost,
                         '10': IceBlizzard,
                         '15': Electrocution,
                         '20': Teleport,
                         '25': MagicMissile3},
              'Warlock': {'1': ShadowBolt,
                          '4': Corruption,
                          '10': Terrify,
                          '12': ShadowBolt2,
                          '15': Doom},
              'Shadowcaster': {'2': Terrify2,
                               '6': Corruption2,
                               '8': ShadowBolt3,
                               '16': Terrify3,
                               '18': Desoul},
              'Spellblade': {'2': EnhanceBlade,
                             '14': EnhanceBlade2,
                             '20': Reflect},
              'Knight Enchanter': {'1': EnhanceArmor,
                                   '3': Fireball,
                                   '8': EnhanceBlade3,
                                   '9': Icicle,
                                   '12': Lightning},
              'Footpad': {},
              'Thief': {},
              'Rogue': {},
              'Inquisitor': {'15': Reflect},
              'Seeker': {'1': Teleport,
                         '10': Sanctuary},
              'Assassin': {},
              'Ninja': {'20': Desoul},
              'Healer': {'4': Heal,
                         '8': Regen,
                         '10': Holy,
                         '18': Heal2},
              'Cleric': {'2': Smite,
                         '3': TurnUndead,
                         '5': Bless,
                         '14': Cleanse,
                         '16': Smite2,
                         '19': TurnUndead2},
              'Templar': {'3': Bless2,
                          '6': Regen2,
                          '10': Smite3},
              'Priest': {'1': Regen2,
                         '3': Holy2,
                         '8': Heal3,
                         '11': Cleanse,
                         '15': Bless},
              'Archbishop': {'4': Holy3,
                             '7': Regen3,
                             '12': Bless2,
                             '20': Resurrection},
              'Monk': {},
              'Master Monk': {'2': Reflect},
              'Pathfinder': {'5': Tremor,
                             '11': WaterJet,
                             '14': Gust,
                             '19': Scorch},
              'Druid': {'5': Regen},
              'Lycan': {},
              'Diviner': {},
              'Geomancer': {'15': Boost},
              'Shaman': {'9': Regen},
              'Soulcatcher': {'12': Desoul},
              }
