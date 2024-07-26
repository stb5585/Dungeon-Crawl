###########################################
""" spell manager """

# Imports
import random
import time
from dataclasses import dataclass

import items
import enemies
import storyline


@dataclass
class Ability:
    """
    name: name of the ability
    description: description of the ability that explains what it does in so many words
    cost: amount of mana required to cast spell
    combat: boolean indicating whether the ability can only be cast in combat
    passive: boolean indicating whether the ability is passively active
    typ: the type of the ability
    subtyp: the subtype of the ability
    """
    name: str
    description: str
    cost: int
    combat: bool = True
    passive: bool = False
    typ: str = ""
    subtyp: str = ""

    def __str__(self):
        str_text = f"Type: {self.typ}\nSub-Type: {self.subtyp}\n{self.description}\n"
        if not self.passive:
            str_text += f"Mana Cost: {self.cost}\n"
        else:
            str_text += "Passive\n"
        return str_text
    
    def special_effect(self, caster, target, damage, crit):
        pass


@dataclass
class Spell(Ability):
    """
    typ: the type of these abilities is 'Spell'
    """
    typ: str = 'Spell'


@dataclass
class Skill(Ability):
    """
    typ: the type of these abilities is 'Skill'
    """
    typ: str = 'Skill'


"""
Skill section
"""
@dataclass
class Offensive(Skill):
    """
    subtyp: the subtype of these abilities is 'Offensive', meaning they either inflict damage or some other status
        effect
    """

    subtyp: str = 'Offensive'

@dataclass
class Defensive(Skill):
    """
    subtyp: the subtype of these abilities is 'Defensive', meaning they work to protect the user
    """

    subtyp: str = 'Defensive'


@dataclass
class Stealth(Skill):
    """
    subtyp: the subtype of these abilities is 'Stealth', meaning they work through subterfuge of some kind
    """

    subtyp: str = 'Stealth'


@dataclass
class Enhance(Skill):
    """
    subtyp: the subtype of these abilities is 'Enhance', meaning they enhance the user's equipment (Spellblade/Knight
        Enchanter)
    """

    subtyp: str = 'Enhance'


@dataclass
class Drain(Skill):
    """
    subtyp: the subtype of these abilities is 'Drain', meaning they drain health and/or mana from the enemy
    """

    subtyp: str = 'Drain'


@dataclass
class Class(Skill):
    """
    subtyp: the subtype of these abilities is 'Class', meaning they are specific to a particular class
    """

    subtyp: str = 'Class'


@dataclass
class Luck(Skill):
    """
    subtyp: the subtype of these abilities is 'Luck', meaning they rely mostly on luck (charisma)
    """

    subtyp: str = 'Luck'


# Skills #
# Offensive
class ShieldSlam(Offensive):
    """
    Cannot crit with Shield Slam
    multiplier indicates the factor by which the damage is calculated
    """

    def __init__(self):
        super().__init__(name='Shield Slam', description='Slam the enemy with your shield, damaging with a chance to '
                                                         'stun for several turns.',
                         cost=8)
        self.multiplier = 5

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        dodge = target.dodge_chance(user) > random.random()
        if any(target.status_effects[x].active for x in ['Sleep', 'Stun', 'Prone']):
            hit = True
            dodge = False
        else:
            hit_per = user.hit_chance(target, typ='weapon')
            hit = hit_per > random.random()
        if dodge:
            print(f"{target.name} evades {user.name}'s attack.")
        else:
            dam_red = target.check_mod('armor')
            dmg_mod = int(user.stats.strength * user.equipment['OffHand']().mod * self.multiplier)
            dmg_mod = random.randint(dmg_mod // 2, dmg_mod)
            if 'Physical Damage' in user.equipment['Ring']().mod:
                dmg_mod += int(user.equipment['Ring']().mod.split(' ')[0])
            damage = max(1, dmg_mod)
            if hit and cover:
                print(f"{target.familiar.name} steps in front of the attack, absorbing the damage directed at "
                      f"{target.name}.")
            elif hit:
                resist = target.check_mod('resist', typ='Physical')
                damage = max(0, int((damage - dam_red) * (1 - resist)))
                if hit and target.status_effects['Mana Shield'].active and damage > 0:
                    damage //= target.status_effects['Mana Shield'].duration
                    if damage > target.mana.current:
                        print(f"The mana shield around {target.name} absorbs {target.mana.current} damage.")
                        damage -= target.mana.current
                        target.mana.current = 0
                        target.status_effects['Mana Shield'].active = False
                    else:
                        print(f"The mana shield around {target.name} absorbs {damage} damage.")
                        target.mana.current -= damage
                        damage = 0
                if damage == 0:
                    print(f"{user.name} hits {target.name} with their shield but it does no damage.")
                else:
                    target.health.current -= damage
                    print(f"{user.name} damages {target.name} with Shield Slam for {damage} hit points.")
                    if target.is_alive() and not target.status_effects['Stun'].active:
                        if random.randint(0, user.stats.strength) \
                                > random.randint(target.stats.strength // 2, target.stats.strength):
                            turns = max(1, user.stats.strength // 8)
                            target.status_effects['Stun'].active = True
                            target.status_effects['Stun'].duration = turns
                            print(f"{target.name} is stunned.")
                        else:
                            print(f"{user.name} fails to stun {target.name}.")
            else:
                print(f"{user.name} swings their shield at {target.name} but miss entirely.")


class DoubleStrike(Offensive):
    """

    """

    def __init__(self):
        super().__init__(name='Multi-Strike', description='Perform two melee attacks with your primary weapon.',
                         cost=14)
        self.strikes = 2  # number of strikes performed

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        for _ in range(self.strikes):
            _, _ = user.weapon_damage(target, cover=cover)
            if not target.is_alive():
                break


class TripleStrike(DoubleStrike):
    """
    Replaces DoubleStrike
    """

    def __init__(self):
        super().__init__()
        self.description = 'Perform three melee attacks with your primary weapon.'
        self.strikes = 3
        self.cost = 26


class QuadStrike(DoubleStrike):
    """
    Replaces TripleStrike
    """

    def __init__(self):
        super().__init__()
        self.description = 'Perform four melee attacks with your primary weapon.'
        self.strikes = 4
        self.cost = 40


class FlurryBlades(DoubleStrike):
    """
    Replaces QuadStrike
    """

    def __init__(self):
        super().__init__()
        self.description = 'Perform five melee attacks with your primary weapon.'
        self.strikes = 5
        self.cost = 50


class PiercingStrike(Offensive):
    """

    """

    def __init__(self):
        super().__init__(name='Piercing Strike', description='Pierces the enemy\'s defenses, ignoring armor.',
                         cost=5)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        _, _ = user.weapon_damage(target, cover=cover, ignore=True)


class Jump(Offensive):
    """

    """

    def __init__(self):
        super().__init__(name='Jump', description='Leap into the air and bring down your weapon onto the enemy, '
                                                  'delivering critical damage.',
                         cost=10)
        self.strikes = 1
        self.crit = 2

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        for _ in range(self.strikes):
            _, _ = user.weapon_damage(target, cover=cover, crit=2)
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

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        j = 0
        while j < self.cast:
            spell_list = []
            for entry in user.spellbook['Spells']:
                if user.spellbook['Spells'][entry]().cost <= user.mana.current:
                    if user.spellbook['Spells'][entry]().name != 'Magic Missile':
                        if user.cls:
                            spell_list.append(str(entry) + '  ' + str(user.spellbook['Spells'][entry]().cost))
                        else:
                            spell_list.append(str(entry))
            if len(spell_list) == 0:
                print(f"{user.name} does not have enough mana to cast any spells with Multi-Cast.")
                user.mana.current += self.cost
                break
            if user.cls in ['Sorcerer', 'Wizard', 'Archbishop', 'Diviner', 'Geomancer']:
                spell_index = storyline.get_response(spell_list)
                spell = user.spellbook['Spells'][spell_list[spell_index].rsplit('  ', 1)[0]]
            else:
                spell_index = random.choice(spell_list)
                spell = user.spellbook['Spells'][spell_index]
            spell().cast(user, target=target, cover=False)
            j += 1
            time.sleep(1)
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

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        hit, crit = user.weapon_damage(target, cover=cover, crit=self.crit)
        if hit and target.is_alive() and not target.status_effects['Bleed'].active:
            if random.randint((user.stats.strength * crit) // 2, (user.stats.strength * crit)) \
                    > random.randint(target.stats.con // 2, target.stats.con) and not target.status_effects['Mana Shield'].active:
                bleed_dmg = user.stats.strength * crit
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.status_effects['Bleed'].active = True
                target.status_effects['Bleed'].duration = max(user.stats.strength // 10, target.status_effects["Bleed"].duration)
                target.status_effects['Bleed'].extra = max(bleed_dmg, target.status_effects["Bleed"].extra)
                print(f"{target.name} is bleeding.")


class MortalStrike2(MortalStrike):
    """
    Devastating critical strike plus bleed; duration and damage determined by the player's strength
    """

    def __init__(self):
        super().__init__()
        self.crit = 3
        self.cost = 30


class BattleCry(Offensive):
    """

    """

    def __init__(self):
        super().__init__(name="Battle Cry", description="Unleash a furious scream, increasing your attack damage for "
                                                        "several turns.",
                         cost=16)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        turns = max(2, user.stats.strength // 10)
        dmg_mod = max(1, user.stats.strength // 2)
        user.status_effects['Attack'].active = True
        user.status_effects['Attack'].duration = max(user.status_effects['Attack'].duration, turns)
        user.status_effects['Attack'].extra += dmg_mod
        print(f"{user.name}'s attack damage increases by {dmg_mod}.")


class Charge(Offensive):
    """
    Can stun then attacks, as opposed to other abilities that attack then stun
    """

    def __init__(self):
        super().__init__(name="Charge", description="Charge the enemy, possibly stunning them for the turn and doing "
                                                    "weapon damage.",
                         cost=10)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        if random.randint(user.stats.strength // 2, user.stats.strength) > \
                random.randint(target.stats.con // 2, target.stats.con) and not target.status_effects['Stun'].active:
            target.status_effects["Stun"].active = True
            target.status_effects["Stun"].duration = 1
            print(f"{user.name} stunned {target.name}.")
        _, _ = user.weapon_damage(target)


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
        super().__init__(name='Disarm', description='Surprise the enemy by attacking their weapon, knocking it out of '
                                                    'their grasp.',
                         cost=4)

    def use(self, user, target=None, cover=False):
        name = user.name
        print(f"{name} uses {self.name}.")
        user.mana.current -= self.cost
        if target.equipment["Weapon"]().subtyp not in ["Natural", "None"]:
            if not target.status_effects["Disarm"].active:
                chance = target.check_mod("luck", luck_factor=10)
                if random.randint(user.stats.strength // 2, user.stats.strength) \
                        > random.randint(target.stats.dex // 2, target.stats.dex) + chance:
                    turns = max(2, user.stats.strength // 10)
                    target.status_effects['Disarm'].active = True
                    target.status_effects['Disarm'].duration = turns
                    print(f"{target.name} is disarmed.")
                else:
                    print(f"{name} fails to disarm the {target.name}.")
            else:
                print(f"{target.name} is already disarmed.")
        else:
            print(f"The {target.name} cannot be disarmed.")


class Cover(Defensive):
    """
    Familiar only skill
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

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        _, _ = user.weapon_damage(target, cover=cover, ignore=True)


class PocketSand(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Pocket Sand', description='Throw sand in the eyes of your enemy, blinding them and '
                                                         'reducing their chance to hit on a melee attack for 2 turns.',
                         cost=8)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        if not target.status_effects['Disarm'].active:
            if random.randint(user.stats.dex // 2, user.stats.dex) \
                    > random.randint(target.stats.dex // 2, target.stats.dex):
                target.status_effects['Blind'].active = True
                target.status_effects['Blind'].duration = max(2, user.stats.dex // 10)
                print(f"{target.name} is blinded.")
            else:
                print(f"{user.name} fails to blind {target.name}.")
        else:
            print(f"{target.name} is already blinded.")


class SleepingPowder(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name="Sleeping Powder", description="Releases a powerful toxin that puts the target to sleep.",
                         cost=11)
        self.turns = 2

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        if not target.status_effects['Sleep'].active:
            if random.randint(user.stats.dex // 2, user.stats.dex) \
                    > random.randint(target.stats.dex // 2, target.stats.dex):
                target.status_effects['Sleep'].active = True
                target.status_effects['Sleep'].duration = self.turns
                print(f"{target.name} is asleep.")
            else:
                print(f"{user.name} fails to put {target.name} to sleep.")
        else:
            print(f"{target.name} is already asleep.")


class KidneyPunch(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Kidney Punch', description='Punch the enemy in the kidney, rendering them stunned.',
                         cost=18)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        hit, crit = user.weapon_damage(target, cover=cover)
        if not target.status_effects['Stun'].active:
            if hit and target.is_alive() and not target.status_effects['Mana Shield'].active:
                if random.randint(0, (user.stats.dex * crit)) \
                        > random.randint(target.stats.con // 2, target.stats.con):
                    target.status_effects['Stun'].active = True
                    target.status_effects['Stun'].duration = max(2, user.stats.dex // 10)
                    print(f"{target.name} is stunned.")
                else:
                    print(f"{user.name} fails to stun {target.name}.")


class SmokeScreen(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Smoke Screen', description='Obscure the player in a puff of smoke, allowing the '
                                                          'player to flee without fail.',
                         cost=5)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        print(f"{user.name} casts {self.name}.")
        print(f"{user.name} disappears in a cloud of smoke.")


class Steal(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Steal', description='Relieve the enemy of their items.',
                         cost=6)

    def use(self, user, target=None, cover=False, crit=1, mug=False):
        if not mug:
            print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        if len(target.inventory) != 0:
            chance = user.check_mod('luck', luck_factor=16)
            if random.randint((user.stats.dex * crit) // 2, (user.stats.dex * crit)) + chance > \
                    random.randint(target.stats.dex // 2, target.stats.dex):
                item_key = random.choice(list(target.inventory))
                item = target.inventory[item_key][0]
                target.modify_inventory(item, num=1, subtract=True)
                if item_key == 'Gold':
                    print(f"{user.name} steals {item} gold from {target.name}.")
                    user.gold += item
                else:  # if monster steals from player, item is lost
                    try:
                        user.modify_inventory(item, num=1)
                    except AttributeError:
                        pass
                    print(f"{user.name} steals {item_key} from {target.name}.")
            else:
                print("Steal fails.")
        else:
            print(f"{target.name} doesn't have anything to steal.")


class Mug(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Mug', description='Attack the enemy with a chance to steal their items.',
                         cost=20)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        hit, crit = user.weapon_damage(target, cover=cover)
        if hit:
            Steal().use(user, target, cover=False, crit=crit, mug=True)


class Lockpick(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Lockpick', description='Unlock a locked chest.',
                         cost=0)
        self.passive = True


# Poison Skills
class PoisonStrike(Stealth):
    """

    """

    def __init__(self):
        super().__init__(name='Poison Strike', description='Attack the enemy with a chance to poison.',
                         cost=14)
        self.damage = 8

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        hit, crit = user.weapon_damage(target, cover=cover)
        if not target.status_effects['Poison'].active:
            if hit and target.is_alive() and not target.status_effects['Mana Shield'].active:
                resist = target.check_mod('resist', 'Poison')
                if resist < 1:
                    if random.randint(user.stats.dex // 2, user.stats.dex) * crit * (1 - resist) \
                            > random.randint(target.stats.con // 2, target.stats.con):
                        turns = max(1, user.stats.dex // 10)
                        pois_dmg = random.randint(1, max(1, int((self.damage * user.level.pro_level) * (1 - resist))))
                        target.status_effects['Poison'].active = True
                        target.status_effects['Poison'].duration = max(turns, target.status_effects["Poison"].duration)
                        target.status_effects['Poison'].extra = max(pois_dmg, target.status_effects["Poison"].extra)
                        print(f"{target.name} is poisoned.")
                    else:
                        print(f"{target.name} resists the poison.")
                else:
                    print(f"{target.name} is immune to poison.")


# Enhance skills
class ImbueWeapon(Enhance):
    """

    """

    def __init__(self):
        super().__init__(name='Imbue Weapon', description='Imbue your weapon with magical energy to enhance the '
                                                          'weapon\'s damage.',
                         cost=12)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        dmg_mod = max(1, user.stats.intel // 3)
        print(f"{user.name}'s weapon has been imbued with arcane power, increasing damage by {dmg_mod}.")
        _, _ = user.weapon_damage(target, cover=cover, dmg_mod=dmg_mod)


class EnhanceBlade(Enhance):
    """
    Level * (Current Mana / Max Mana)
    """

    def __init__(self):
        super().__init__(name='Enhance Blade', description="The Spellblade has an innate ability to increase melee "
                                                           "damage based on the percentage of mana used.",
                         cost=0)
        self.passive = True


class EnhanceArmor(Enhance):
    """

    """

    def __init__(self):
        super().__init__(name='Enhance Armor', description='The Knight Enchanter can imbue their armor with arcane '
                                                           'power, improving their defense modified by their '
                                                           'intelligence multiplied by the percentage of their mana.',
                         cost=0)
        self.passive = True


# Drain skills
class HealthDrain(Drain):
    """

    """

    def __init__(self):
        super().__init__(name='Health Drain', description='Drain the enemy, absorbing their health.',
                         cost=10)

    def use(self, user, target=None, cover=False, special=False):
        if not special:
            print(f"{user.name} uses {self.name}.")
            user.mana.current -= self.cost
        drain = random.randint((user.health.current + user.stats.intel) // 5,
                               (user.health.current + user.stats.intel) // 1.5)
        chance = target.check_mod('luck', luck_factor=1)
        if not random.randint(user.stats.wisdom // 2, user.stats.wisdom) > random.randint(0, target.stats.wisdom // 2) + chance:
            drain = drain // 2
        drain = min(drain, target.health.current)
        target.health.current -= drain
        user.health.current += drain
        user.health.current = min(user.health.current, user.health.max)
        print(f"{user.name} drains {drain} health from {target.name}.")


class ManaDrain(Drain):
    """

    """

    def __init__(self):
        super().__init__(name='Mana Drain', description='Drain the enemy, absorbing their mana.',
                         cost=0)

    def use(self, user, target=None, cover=False, special=False):
        if not special:
            print(f"{user.name} uses {self.name}.")
            user.mana.current -= self.cost
        drain = random.randint((user.mana.current + user.stats.intel) // 5,
                               (user.mana.current + user.stats.intel) // 1.5)
        chance = target.check_mod('luck', luck_factor=10)
        if not random.randint(user.stats.wisdom // 2, user.stats.wisdom) > random.randint(0, target.stats.wisdom // 2) + chance:
            drain = drain // 2
        drain = min(drain, target.mana.current)
        target.mana.current -= drain
        user.mana.current += drain
        user.mana.current = min(user.mana.current, user.mana.max)
        print(f"{user.name} drains {drain} mana from {target.name}.")


class HealthManaDrain(Drain):
    """
    Replaces Health Drain
    """

    def __init__(self):
        super().__init__(name='Health/Mana Drain', description='Drain the enemy, absorbing the health and mana in '
                                                               'return.',
                         cost=0)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
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
        self.description = "Enables a diviner to learn rank 2 enemy spells."


class Transform(Class):
    """
    Panther
    """

    def __init__(self):
        super().__init__(name='Transform', description='Transforms the druid into a powerful creature, assuming the '
                                                       'spells and abilities inherent to the creature.',
                         cost=0)
        self.t_creature = enemies.Panther

    def use(self, user):
        user.transform = self.t_creature


class Transform2(Transform):
    """
    Direbear
    """

    def __init__(self):
        super().__init__()
        self.t_creature = enemies.Direbear


class Transform3(Transform):
    """
    Werewolf
    """

    def __init__(self):
        super().__init__()
        self.t_creature = enemies.Werewolf


class Transform4(Transform):
    """
    Red Dragon; learned only from defeating the Red Dragon
    """

    def __init__(self):
        super().__init__()
        self.t_creature = enemies.RedDragon


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
        self.description = "The warlock's familiar gains strength, unlocking additional abilities."


class Familiar3(Familiar):
    """

    """

    def __init__(self):
        super().__init__()
        self.description = "The warlock's familiar gains additional strength, unlocking even more abilities."


class ElementalStrike(Class):
    """

    """

    def __init__(self):
        super().__init__(name="Elemental Strike", description='Attack the enemy with your weapon and a random '
                                                              'elemental spell.',
                         cost=15)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        hit, crit = user.weapon_damage(target, cover=cover)
        if hit and target.is_alive():
            spell_list = [Scorch, WaterJet, Tremor, Gust]
            spell = random.choice(spell_list)
            if crit > 1:
                spell().cast(user, target=target, cover=False)
                spell().cast(user, target=target, cover=False)
            else:
                spell().cast(user, target=target, cover=False)


class AbsorbEssence(Class):
    """
    Currently 5% chance
    Different monster types improve different stats
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


class LegSweep(Class):
    """

    """

    def __init__(self):
        super().__init__(name="Leg Sweep", description="Sweep the leg, tripping the enemy and leaving them prone.",
                         cost=8)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        hit, _ = user.weapon_damage(target, cover=cover)
        if hit and target.is_alive():
            if not target.status_effects['Prone'].active:
                if random.randint(user.stats.strength // 2, user.stats.strength) > \
                        random.randint(target.stats.strength // 2, target.stats.strength) and not target.flying:
                    target.status_effects['Prone'].active = True
                    target.status_effects['Prone'].duration = max(1, user.stats.strength // 20)
                    print(f"{user.name} trips {target.name} and they fall prone.")


class ChiHeal(Class):
    """

    """

    def __init__(self):
        super().__init__(name="Chi Heal", description="The monk channels his chi energy, healing 25% of their health"
                                                      " and removing all negative status effects.",
                         cost=25)

    def use(self, user, target=None, cover=False):
        target = user
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        Heal().cast(user, target=target, special=True, cover=False)
        Cleanse().cast(user, target=target, special=True, cover=False)


class Inspect(Class):
    """

    """

    def __init__(self):
        super().__init__(name="Inspect", description="Your attention to detail allows you to inspect aspects of the "
                                                     "enemy, possibly revealing a tender spot.",
                         cost=5)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        inspect_text = target.inspect() + "\n"
        print(inspect_text)


class ExploitWeakness(Class):
    """
    Adds damage to melee attack equal to the user's strength multiplied by the lowest resistance
    """

    def __init__(self):
        super().__init__(name="Exploit Weakness", description="Inspect and identify the enemy's greatest weakness and "
                                                              "exploit it.",
                         cost=10)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        types = list(target.resistance)
        resists = list(target.resistance.values())
        weak = min(resists)
        if weak < 0:
            mod = int(user.stats.strength * -weak)
            print(f"{user.name} targets {target.name}'s weakness to {types[resists.index(weak)].lower()} to "
                  f"increase their attack!")
        else:
            mod = 0
            print(f"{target.name} has no identifiable weakness. The skill is ineffective.")
        time.sleep(0.5)
        _, _ = user.weapon_damage(target, dmg_mod=mod)


class KeenEye(Class):
    """
    Gives Seekers insights about their surroundings
    """

    def __init__(self):
        super().__init__(name="Keen Eye", description="As a Seeker, you can gain insights into your surroundings.",
                         cost=0)
        self.passive = True


# Luck
class GoldToss(Luck):
    """
    Rank 1 Enemy Spell
    Unblockable (including mana shield and cover) and unresistable but enemy has chance to catch/keep some of it
    max_thrown is a percentage
    """

    def __init__(self):
        super().__init__(name="Gold Toss", description='Toss a handful of gold at the enemy, dealing damage equal to '
                                                       'the amount of gold thrown.',
                         cost=0)
        self.rank = 1

    def use(self, user, target=None, cover=False):
        max_thrown = 0.1
        print(f"{user.name} uses {self.name}.")
        if user.gold == 0:
            print("Nothing happens.")
        else:
            a_chance = user.check_mod('luck', luck_factor=20)
            d_chance = target.check_mod('luck', luck_factor=10)
            gold = max(1, int(max_thrown * user.gold))
            damage = max(1, random.randint(1, gold) // (random.randint(1, 3) // max(1, a_chance)))
            user.gold -= damage
            print(f"{user.name} throws {damage} gold at {target.name}.")
            if not random.randint(0, 1) and \
                    not any(target.status_effects[x].active for x in ['Sleep', 'Stun', 'Prone']):
                catch = random.randint(min(damage, d_chance), damage)
                damage -= catch
                if catch > 0:
                    target.gold += catch
                    print(f"{target.name} catches some of the gold thrown, gaining {catch} gold.")
            else:
                pass
            target.health.current -= damage
            print(f"{user.name} does {damage} damage to {target.name}.")


class SlotMachine(Luck):
    """
    Rank 2 Enemy Skill
    Rolls 3 10-sided dice (so to speak); 1000 possible results (000 to 999)
    Possible outcomes:
    Nothing: nothing happens
    Mark of the Beast: either user (player) or enemy (bypasses Death resistance) - (666 or 999)
    3 of a Kind: full health/mana, cleanse negative statuses - (000, 111, 222, 333, 444, 555, 777, 888)
    Straight: damage to enemy equal to numbers multiplied together (unresistable and unblockable) -
        (012 = 0, 123 = 6, 234 = 24, 345 = 60, 456 = 120, 567 = 210, 678 = 336, 789 = 504, 890 = 0)
    Palindrome: casts high level spell based on middle value - (number that follow xyx format)
    Pairs: random status effect ["Stun", "Doom", "Blind", "Disarm", "Sleep", "Reflect", "Poison", "DOT",
                           "Bleed", "Regen", "Attack", "Defense", "Magic", "Magic Defense"] -
        (two numbers that are the same but do not meet any of the other requirements i.e. 221 but not 212)
    Evens: all numbers even; gain gold equal to spin - (i.e. 246 or 680)
    Odds: all numbers odd; gain random item - (i.e. 137 or 531)
    Chance: if no other spin hits, there is a chance that the user attacks with damage mod equal to one of the spins
    """

    def __init__(self):
        super().__init__(name="Slot Machine", description='Pull the handle and see what comes up! Depending on the '
                                                          'results, different possible outcomes can occur.',
                         cost=15)
        self.rank = 2

    def use(self, user, target=None, cover=False):
        def spin_wheel():
            dice = ["*", "*", "*"]

            for die, _ in enumerate(dice):
                for _ in range(25):
                    dice[die] = str(random.randint(0, 9))
                    print(f"\t{dice[0]}{dice[1]}{dice[2]}", end="\r")
                    time.sleep(0.05)

            print(f"\t{dice[0]}{dice[1]}{dice[2]}\n", end="\r")
            time.sleep(1)

            return "".join(dice)

        hands = {"Death": ["666", "999"],
                 "Trips": ["000", "111", "222", "333", "444", "555", "777", "888"],
                 'Straight': ["012", "123", "234", "345", "456", "567", "678", "789"],
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
        user_chance = user.check_mod('luck', luck_factor=10)
        target_chance = target.check_mod('luck', luck_factor=10)
        print(f"{user.name} uses {self.name}.")
        success = False
        retries = 0
        while not success:
            spin = spin_wheel()
            if spin in hands['Death']:
                print("The mark of the beast!")
                success = True
                if target_chance > user_chance + 1:
                    target = user
                resist = target.check_mod('resist', typ='Death')
                if resist < 1:
                    target.health.current = 0
                    print(f"Death has come for {target.name}!")
                else:
                    print(f"{target.name} is immune to death spells.")
            elif spin in hands['Trips']:
                print("3 of a Kind!")
                success = True
                if random.randint(0, max(1, user_chance)):
                    target = user
                target.health.current = target.health.max
                target.mana.current = target.mana.max
                print(f"{target.name} has been revitalized! Health and mana are restored.")
                Cleanse().cast(target, special=True, cover=False)
            elif "".join(sorted(spin)) in hands['Straight']:
                print("Straight!")
                success = True
                if target_chance > user_chance + 1:
                    target = user
                ints = [int(x) for x in list(spin)]
                damage = 1
                for i in ints:
                    damage *= i
                target.health.current -= damage
                print(f"{target.name} takes {damage} damage.")
            elif spin in hands['Palindrome']:
                print("Palindrome!")
                success = True
                if target_chance > user_chance + 1:
                    target = user
                spell_list = [MagicMissile3, Firestorm, IceBlizzard, Electrocution, Tsunami, Earthquake, Tornado,
                              ShadowBolt3, Holy3, Ultima]
                spell = spell_list[int(spin[1])]
                print(f"{spell().name} is cast!")
                spell().cast(user, target=target, special=True, cover=False)
            elif len(set(spin)) == 2:
                print('Pairs!')
                success = True
                duration = int(min(set(list(spin)), key=list(spin).count))  # number of turns effect will last
                if duration == 0:
                    duration = 10
                amount = int(max(set(list(spin)), key=list(spin).count))  # amount it will affect target
                if amount == 0:
                    amount = 10
                amount **= 2
                effects = ["Stun", "Doom", "Blind", "Disarm", "Sleep", "Reflect", "Poison", "DOT",
                           "Bleed", "Regen", "Attack", "Defense", "Magic", "Magic Defense"]
                if not random.randint(0, 1):
                    target = user
                effect = random.choice(effects)
                print(f"{effect} has been randomly selected to affect {target.name}.")
                typ = len(target.status_effects[effect])
                target.status_effects[effect].active = True
                target.status_effects[effect].duration = max(duration, target.status_effects[effect].duration)
                if typ == 3:
                    target.status_effects[effect].extra = amount
                    if effect in ["Attack", "Defense", "Magic", "Magic Defense"]:
                        print(f"{target.name}'s {effect.lower()} is temporarily increased by {amount}.")
            elif all(int(x) % 2 == 0 for x in list(spin)):
                print("Evens!")
                success = True
                if user_chance + 1 >= target_chance:
                    target = user
                target.gold += (int(spin) * 10)
                print(f"{target.name} gains {int(spin)} gold!")
            elif all(int(x) % 2 == 1 for x in list(spin)):
                print("Odds!")
                success = True
                level = min(list(spin))
                if user_chance + 1 >= target_chance:
                    target = user
                item = items.random_item(int(level))
                try:
                    target.modify_inventory(item, num=1)
                except AttributeError:
                    pass
                print(f"{target.name} gains {item().name}.")
            elif random.randint(0, user_chance):
                print("Chance!")
                success = True
                mod = int(random.choice(list(spin)))
                print(f"{user.name} gains {mod} attack.")
                user.weapon_damage(target, dmg_mod=mod)
            else:
                if random.randint(0, user_chance) and retries < 2:
                    print("No luck, try again.")
                    retries += 1
                else:
                    success = True
                    print("Nothing happens.")


# Enemy skills
class Lick(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Lick", description="Lick the target, dealing damage and inflicting random status "
                                                  "effect(s).",
                         cost=10)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        hit, _ = user.weapon_damage(target)
        if hit:
            status_effects = ['Prone', 'Silence', 'Stun', 'Blind', 'Sleep']
            if random.randint(user.stats.strength // 2, user.stats.strength) > \
                    random.randint(target.stats.con // 2, target.stats.con):
                random_effect = random.choice(status_effects)
                if not target.status_effects[random_effect].active:
                    target.status_effects[random_effect].active = True
                    target.status_effects[random_effect].duration = random.randint(2, max(3, user.stats.strength // 8))
                    print(f"{target.name} is affected by {random_effect.lower()}.")


class AcidSpit(Skill):
    """
    dodge reduces damage by half
    """

    def __init__(self):
        super().__init__(name="Acid Spit", description="Spit a corrosive substance on the target, dealing initial "
                                                       "damage plus damage over time.",
                         cost=6)
        self.damage = 8

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= (self.cost * user.level.pro_level)
        dmg = self.damage * max(1, user.level.pro_level)
        dam_red = target.check_mod('magic def')
        damage = random.randint(dmg // 2, dmg) - dam_red
        hit = user.hit_chance(target)
        dodge = target.dodge_chance(user) > random.random()
        if hit:
            if dodge:
                print(f"{target.name} partially dodges the attack, only taking half damage.")
                damage //= 2
            if damage > 0:
                print(f"{target.name} takes {damage} damage from the acid.")
                target.health.current -= damage
                target.status_effects["DOT"].active = True
                target.status_effects["DOT"].duration = 2
                target.status_effects["DOT"].extra = max(damage, target.status_effects["DOT"].extra)
                print(f"{target.name} is covered in a corrosive substance.")
            else:
                print("The acid is ineffective.")
        else:
            print(f"{user.name} misses {target.name} with {self.name}.")


class Web(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Web", description="Expel a thick, sticky substance onto the enemy, leaving them prone.",
                         cost=6)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        if random.randint(user.stats.dex // 2, user.stats.dex) > \
                random.randint(target.stats.strength // 2, target.stats.strength):
            if not target.status_effects['Prone'].active:
                target.status_effects['Prone'].active = True
                target.status_effects['Prone'].duration = max(1, user.stats.strength // 20)
            else:
                target.status_effects['Prone'].duration += 1
            print(f"{target.name} is trapped in a web and is prone.")
        else:
            print(f"{target.name} evades the web.")


class Howl(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Howl", description="The wolf howls at the moon, terrifying the enemy.",
                         cost=10)

    def use(self, user, target=None, cover=False):
        turns = max(1, user.stats.strength // 10)
        print(f"{user.name} howls at the moon.")
        user.mana.current -= self.cost
        if not target.status_effects["Stun"].active:
            if random.randint(0, user.stats.strength) > random.randint(target.stats.con // 2, target.stats.con):
                target.status_effects["Stun"].active = True
                target.status_effects['Stun'].duration = turns
                print(f"{user.name} stunned {target.name}.")
            else:
                print(f"{target.name}'s resolve is steadfast.")
        else:
            print(f"{target.name} is already stunned.")


class Shapeshift(Skill):
    """

    """

    def __init__(self):
        super().__init__(name='Shapeshift', description="Some enemies can change their appearance and type. This is the"
                                                        " skill they use to do so.",
                         cost=0)

    def use(self, user, target=None, cover=False):
        while True:
            s_creature = random.choice(user.transform)()
            if user.cls != s_creature.cls:
                break
        print(f"{user.name} changes shape, becoming a {s_creature.name}.")
        user.cls = s_creature.cls
        user.stats = s_creature.stats
        user.equipment = s_creature.equipment
        user.spellbook = s_creature.spellbook
        user.resistance = s_creature.resistance
        user.flying = s_creature.flying
        user.invisible = s_creature.invisible
        user.spellbook['Skills']['Shapeshift'] = Shapeshift


class Trip(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Trip", description="Grab the enemy's leg and trip them to the ground, leaving them "
                                                  "prone.",
                         cost=6)

    def use(self, user, target=None, cover=False, special=False):
        if not special:
            print(f"{user.name} uses {self.name}.")
            user.mana.current -= self.cost
        if not target.status_effects["Prone"].active:
            if random.randint(user.stats.dex // 2, user.stats.dex) > \
                    random.randint(target.stats.strength // 2, target.stats.strength) and not target.flying:
                target.status_effects['Prone'].active = True
                target.status_effects['Prone'].duration = max(1, user.stats.strength // 20)
                print(f"{user.name} trips {target.name} and they fall prone.")
            else:
                if not special:
                    print(f"{user.name} fails to trip {target.name}.")
        else:
            if not special:
                print(f"{target.name} is already prone.")


class NightmareFuel(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Nightmare Fuel", description="Invade the enemy's dreams, messing with their mind and "
                                                            "dealing damage.",
                         cost=20)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        crit = 1
        if target.status_effects['Sleep'].active:
            if random.randint(user.stats.intel // 2, user.stats.intel) > \
                    random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                if random.random() > 0.9:  # 10% chance to crit
                    print("Critical hit!")
                    crit = 2
                damage = target.status_effects['Sleep'].duration * user.stats.intel * crit
                damage = max(1, random.randint(damage // 2, damage))
                target.health.current -= damage
                print(f"{user.name} invades {target.name}'s dreams, dealing {damage} damage.")
            else:
                print(f"{target.name} resists the spell.")
        else:
            print("The spell does nothing.")


class ThrowRock(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Throw Rock", description="Grab the nearest rock or stone and chuck it at the enemy, with"
                                                        " a chance to knock the target prone.",
                         cost=7)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        size = random.randint(0, 4)  # size of rock thrown
        sizes = ['tiny', 'small', 'medium', 'large', 'massive']
        print(f"{user.name} throws a {sizes[size]} rock at {target.name}.")
        a_chance = user.check_mod('luck', luck_factor=10)
        d_chance = target.check_mod('luck', luck_factor=15)
        dodge = (random.randint(0, target.stats.dex // 2) + d_chance >
                 random.randint(user.stats.dex // 2, user.stats.dex) + a_chance)
        stun = any(target.status_effects[x] for x in ['Stun', 'Sleep', 'Prone'])
        dam_red = target.check_mod('armor')
        resist = target.check_mod('resist', 'Physical')
        hit_per = user.hit_chance(target, typ='weapon')
        hit = hit_per > random.random()
        if stun:
            dodge = False
            hit = True
        if dodge:
            print(f"{target.name} evades the attack.")
        else:
            if cover:
                print(f"{target.familiar.name} steps in front of the attack, absorbing the damage directed at "
                      f"{target.name}.")
            elif hit:
                damage = random.randint(user.stats.strength // 4, user.stats.strength // 3) * (size + 1)
                damage = max(0, int((damage - dam_red) * (1 - resist)))
                if target.status_effects['Mana Shield'].active:
                    damage //= target.status_effects['Mana Shield'].duration
                    if damage > target.mana.current:
                        print(f"The mana shield around {target.name} absorbs {target.mana.current} damage.")
                        damage -= target.mana.current
                        target.mana.current = 0
                        target.status_effects['Mana Shield'].active = False
                    else:
                        print(f"The mana shield around {target.name} absorbs {damage} damage.")
                        target.mana.current -= damage
                        damage = 0
                if damage > 0:
                    target.health.current -= damage
                    print(f"{target.name} is hit by the rock and takes {damage} damage.")
                    if not target.status_effects["Prone"].active:
                        if random.randint(user.stats.strength // 2, user.stats.strength) > \
                                random.randint(target.stats.strength // 2, target.stats.strength):
                            target.status_effects['Prone'].active = True
                            target.status_effects['Prone'].duration = max(1, size)
                            print(f"{target.name} is knocked over and falls prone.")
                else:
                    print(f"{target.name} shrugs off the damage.")
            else:
                print(f"{user.name} misses {target.name} with the throw.")


class Stomp(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Stomp", description="Stomp on the enemy, dealing damage with a chance to stun.",
                         cost=8)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        resist = target.check_mod('resist', 'Physical')
        a_chance = user.check_mod('luck', luck_factor=10)
        d_chance = target.check_mod('luck', luck_factor=15)
        dodge = (random.randint(0, target.stats.dex // 2) + d_chance >
                 random.randint(user.stats.dex // 2, user.stats.dex) + a_chance)
        stun = any(target.status_effects[x] for x in ['Stun', 'Sleep', 'Prone'])
        if stun:
            dodge = False
            hit = True
        else:
            hit_per = user.hit_chance(target, typ='weapon')
            hit = hit_per > random.random()
        if dodge:
            print(f"{target.name} evades the attack.")
        else:
            if cover and hit:
                print(f"{target.familiar.name} steps in front of the attack, absorbing the damage directed at "
                      f"{target.name}.")
            elif hit:
                crit = 1
                if not random.randint(0, a_chance):
                    crit = 2
                    print("Critical hit!")
                damage = int(random.randint(user.stats.strength // 2, user.stats.strength) * (1 - resist)) * crit
                if target.status_effects['Mana Shield'].active:
                    damage //= target.status_effects['Mana Shield'].duration
                    if damage > target.mana.current:
                        print(f"The mana shield around {target.name} absorbs {target.mana.current} damage.")
                        damage -= target.mana.current
                        target.mana.current = 0
                        target.status_effects['Mana Shield'].active = False
                    else:
                        print(f"The mana shield around {target.name} absorbs {damage} damage.")
                        target.mana.current -= damage
                        damage = 0
                if damage > 0:
                    target.health.current -= damage
                    print(f"{user.name} stomps {target.name}, dealing {damage} damage.")
                    if not target.status_effects["Stun"].active:
                        if random.randint(user.stats.strength // 2, user.stats.strength) > \
                                random.randint(target.stats.con // 2, target.stats.con):
                            turns = max(2, user.stats.strength // 10)
                            target.status_effects["Stun"].active = True
                            target.status_effects['Stun'].duration = turns
                            print(f"{user.name} stunned {target.name}.")
                else:
                    print("{} stomps {} but deals no damage.")
            else:
                print(f"{user.name} misses {target.name}.")


class Screech(Skill):
    """
    Only silences if damage is dealt
    """

    def __init__(self):
        super().__init__(name="Screech", description="Let out an ear-piercing screech, damaging the foe and silencing"
                                                     " them.",
                         cost=15)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        damage = 0
        if random.randint(user.stats.dex // 2, user.stats.dex) + user.stats.intel > \
                random.randint(target.stats.con // 2, target.stats.con) + target.stats.wisdom:
            resist = target.check_mod('resist', 'Physical')
            damage = int(user.stats.intel * (1 - resist))
            if damage > 0:
                target.health.current -= damage
                print(f"The deafening screech hurts {target.name} for {damage} damage.")
                if not target.status_effects["Silence"].active:
                    duration = random.randint(1, max(2, user.stats.intel // 10))
                    target.status_effects['Silence'].active = True
                    target.status_effects['Silence'].duration = duration
                    print(f"{target.name} has been silenced.")
        if damage <= 0:
            print("The spell is ineffective.")


class Detonate(Skill):
    """
    Cannot fully resist the damage except with Mana Shield
    """

    def __init__(self):
        super().__init__(name="Detonate", description="Systems are failing and retreat is not an option. Protocol "
                                                      "states the prime directive is destruction of the enemy by any "
                                                      "means necessary. Self-destruct sequence initiated.",
                         cost=0)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} explodes, sending shrapnel in all directions.")
        resist = target.check_mod('resist', 'Physical')
        damage = max(user.health.current // 2, int(user.health.current * (1 - resist))) * random.randint(1, 4)
        if target.status_effects['Mana Shield'].active:
            damage //= target.status_effects['Mana Shield'].duration
            if damage > target.mana.current:
                print(f"The mana shield around {target.name} absorbs {target.mana.current} damage.")
                damage -= target.mana.current
                target.mana.current = 0
                target.status_effects['Mana Shield'].active = False
            else:
                print(f"The mana shield around {target.name} absorbs {damage} damage.")
                target.mana.current -= damage
                damage = 0
        if damage > 0:
            t_chance = target.check_mod('luck', luck_factor=20)
            if random.randint(0, target.stats.dex // 15) + t_chance:
                damage = max(1, damage // 2)
                print(f"{target.name} dodges the shrapnel, only taking half damage.")
            print(f"{target.name} takes {damage} damage from the shrapnel.")
        else:
            print(f"{target.name} was unhurt by the explosion.")
        user.health.current = 0


class Crush(Skill):
    """
    Can't be covered or blacked by Mana Shield
    """

    def __init__(self):
        super().__init__(name="Crush", description="Take the enemy into your clutches and attempt to squeeze the life "
                                                   "from them.",
                         cost=25)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        resist = target.check_mod('resist', 'Physical')
        a_chance = user.check_mod('luck', luck_factor=15)
        d_chance = target.check_mod('luck', luck_factor=10)
        dodge = (random.randint(0, target.stats.dex // 2) + d_chance >
                 random.randint(user.stats.dex // 2, user.stats.dex) + a_chance)
        stun = any(target.status_effects[x] for x in ['Stun', 'Sleep', 'Prone'])
        if stun:
            hit = True
            dodge = False
        else:
            a_hit = user.stats.dex + user.stats.strength
            d_hit = target.stats.dex + target.stats.strength
            hit = (random.randint(a_hit // 2, a_hit) + a_chance >
                   random.randint(d_hit // 2, d_hit) + d_chance)
        if dodge:
            print(f"{target.name} evades the attack.")
        else:
            if hit:
                print(f"{user.name} grabs {target.name}.")
                crit = 1
                if not random.randint(0, d_chance):
                    crit = 2
                    print("Critical hit!")
                damage = max(int(target.health.current * 0.25),
                             int(random.randint(user.stats.strength // 2, user.stats.strength) * (1 - resist)) * crit)
                target.health.current -= damage
                print(f"{user.name} crushes {target.name}, dealing {damage} damage.")
                if random.randint(user.stats.strength // 2, user.stats.strength) > \
                        random.randint(target.stats.dex // 2, target.stats.dex) + d_chance:
                    fall_damage = int(random.randint(user.stats.strength // 2, user.stats.strength) * (1 - resist))
                    target.health.current -= fall_damage
                    print(f"{user.name} throws {target.name} to the ground, dealing {fall_damage} damage.")
                else:
                    print(f"{target.name} rolls as they hit the ground, preventing any fall damage.")
            else:
                print(f"{user.name} grabs for {target.name} but misses.")


class ConsumeItem(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Consume Item", description="You enjoy the finer things in life, which includes metal, "
                                                          "wood, and leather. Steal an item from the enemy and consume"
                                                          " it, absorbing the power of the item.",
                         cost=14)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        u_chance = user.check_mod('luck', luck_factor=10)
        t_chance = target.check_mod('luck', luck_factor=10)
        if random.randint(0, user.stats.dex) + u_chance > random.randint(target.stats.dex // 2, target.stats.dex) + t_chance:
            if len(target.inventory) != 0 and random.randint(0, u_chance):
                item_key = random.choice(list(target.inventory))
                item = target.inventory[item_key][0]
                target.modify_inventory(item, num=1, subtract=True)
                print(f"{user.name} steals {item_key} from {target.name} and consumes it.")
                duration = max(1, int(1 / item().rarity))
                amount = max(1, int(2 / item().rarity))
                if item().typ == 'Weapon':
                    stat = 'Attack'
                    print(f"{user.name}'s {stat.lower()} increases by {amount}.")
                elif item().typ == 'Armor':
                    stat = 'Defense'
                    print(f"{user.name}'s {stat.lower()} increases by {amount}.")
                elif item().typ == 'OffHand':
                    if item().subtyp == 'Tome':
                        stat = 'Magic'
                    else:
                        stat = 'Magic Defense'
                    print(f"{user.name}'s {stat.lower()} increases by {amount}.")
                elif item().typ == 'Accessory':
                    if item().subtyp == 'Ring':
                        stat = random.choice(['Attack', 'Defense'])
                    else:
                        stat = random.choice(['Magic', 'Magic Defense'])
                    print(f"{user.name}'s {stat.lower()} increases by {amount}.")
                elif item().typ == 'Potion':
                    if item().subtyp != 'Stat':
                        stat = 'Regen'
                        print(f"{user.name} regenerated HP over {duration} turns.")
                    else:
                        stat = 'Poison'
                        print(f"{user.name} is poisoned.")
                else:
                    stat = random.choice(['Silence', 'Stun', 'Blind', 'Sleep'])
                    print(f'{user.name} is affected by {stat.lower()}.')
                user.status_effects[stat].active = True
                user.status_effects[stat].duration = duration + 1
                try:
                    user.status_effects[stat].extra = amount
                except IndexError:
                    pass
            else:
                gold = random.randint(target.gold // 100, target.gold // 50) * u_chance
                regen = gold // 10
                print(f"{user.name} steals {gold} gold from {target.name} and consumes it.")
                print(f"{user.name} regains {regen} health and mana.")
                user.health.current += regen
                user.health.current = min(user.health.current, user.health.max)
                user.mana.current += regen
                user.mana.current = min(user.mana.current, user.mana.max)
        else:
            print(f"{user.name} can't steal anything.")


class DestroyMetal(Skill):
    """

    """
    def __init__(self):
        super().__init__(name="Destroy Metal", description="Target metal items and destroy them.",
                         cost=27)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        metal_items = ['Fist', 'Dagger', 'Sword', 'Ninja Blade', 'Longsword', 'Battle Axe', 'Polearm',
                       'Shield', 'Heavy', 'Ring', 'Pendant', 'Key']
        destroy_list = []
        destroy_loc = 'inv'
        for item in [target.inventory[x][0] for x in target.inventory]:
            if item().subtyp in metal_items and not item().ultimate and item().rarity > 0:
                destroy_list.append(item)
        if len(destroy_list) == 0:
            destroy_loc = 'equip'
            for item in target.equipment.values():
                if item().subtyp in metal_items and not item().ultimate and item().rarity > 0:
                    destroy_list.append(item)
        try:
            destroy_item = random.choice(destroy_list)
            t_chance = target.check_mod('luck', luck_factor=5)
            if not random.randint(0, int(2 / destroy_item().rarity) + t_chance):
                if destroy_loc == 'inv':
                    print(f"{user.name} destroys a {destroy_item().name.lower()} out of {target.name}'s inventory.")
                    target.modify_inventory(destroy_item, num=1, subtract=True)
                elif destroy_loc == 'equip':
                    if destroy_item().typ not in ['Weapon', 'Accessory']:
                        print(f"{user.name} destroys {target.name}'s {destroy_item().typ.lower()}.")
                        target.equipment[destroy_item().typ] = items.remove(destroy_item().typ)
                    elif destroy_item().typ == 'Accessory':
                        print(f"{user.name} destroys {target.name}'s {destroy_item().subtyp.lower()}.")
                        target.equipment[destroy_item().subtyp] = items.remove(destroy_item().subtyp)
                    else:
                        if target.equipment['OffHand'] == destroy_item:
                            target.equipment['OffHand'] = items.remove('OffHand')
                            print(f"{user.name} destroys {target.name}'s offhand weapon.")
                        else:
                            target.equipment[destroy_item().typ] = items.remove(destroy_item().typ)
                            print(f"{user.name} destroys {target.name}'s {destroy_item().typ.lower()}.")
                else:
                    raise AssertionError("You shouldn't reach here.")
            else:
                print(f"{user.name} fails to destroy any items.")
        except IndexError:
            print(f"{target.name} isn't carrying any metal items.")


class Turtle(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Turtle", description="Hunker down into a ball, reducing all damage to 0 and regenerating"
                                                    " health.",
                         cost=0)
        self.passive = True


class GoblinPunch(Skill):
    """
    does damage based on the strength difference between the user and target; the higher the target's strength is
      compared to the user, the more damage it will cause
    """

    def __init__(self):
        super().__init__(name="Goblin Punch", description="Attack the target multiple times with a flurry of punches, "
                                                          "dealing damage based on the strength difference between the "
                                                          "user and target.",
                         cost=0)
        self.max_punches = 5

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        num_attacks = max(1, random.randint(user.level.pro_level, self.max_punches))
        str_diff = max(1, user.stats.strength - target.stats.strength)
        for _ in range(num_attacks):
            if user.hit_chance(target) > random.random():
                target.health.current -= str_diff
                print(f"{user.name} punches {target.name} for {str_diff} damage.")
            else:
                print(f"{user.name} punches air, missing {target.name}.")
            time.sleep(0.1)


class Blackjack(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Blackjack", description="Play a round of blackjack with the Jester; different things "
                                                       "happen depending on the result.",
                         cost=7)

    def use(self, user, target=None, cover=False):
        def draw_card(cards):
            card = random.choice(cards)
            return cards.pop(cards.index(card))

        def score(hand):
            total = 0
            for card in hand:
                try:
                    total += int(card.split()[1])
                except ValueError:
                    if card.split()[1] in ['J', 'Q', 'K']:
                        total += 10
                    else:
                        total += 11
                        if total > 21:
                            total -= 10
            return total

        numbers = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        suits = ["♠️", "♥️", "♣️", "♦️"]
        deck = [f"{suit} {number}" for suit in suits for number in numbers]
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        user_hand = [draw_card(deck), draw_card(deck)]
        user_score = score(user_hand)
        user_stay = False
        target_hand = [draw_card(deck), draw_card(deck)]
        target_score = score(target_hand)
        target_stay = False
        while True:
            print(f"Your Hand: {''.join(target_hand)} Jester's Hand: {''.join(user_hand)}", end="\r")
            if target_score > 21:
                break
            if user_score > 21:
                break
            if not target_stay:
                if target_score < 17:
                    target_hand.append(draw_card(deck))
                    target_score = score(target_hand)
                else:
                    target_stay = True
            if not user_stay:
                if user_score < 17:
                    user_hand.append(draw_card(deck))
                    user_score = score(user_hand)
                else:
                    user_stay = True
            if all([target_stay, user_stay]):
                break
            time.sleep(0.5)
        print(f"Your Hand: {''.join(target_hand)} Jester's Hand: {''.join(user_hand)}\n", end="\r")
        if target_score > 21:
            print("You busted!")
        elif user_score > 21:
            print("Jester busted!")
        else:
            pass


class BrainGorge(Skill):
    """
    ignores mana shield
    """

    def __init__(self):
        super().__init__(name="Brain Gorge", description="Attack the enemy and attempt to latch on and eat its brain; a"
                                                         " successful attack can lower intelligence.",
                         cost=30)

    def use(self, user, target=None, cover=False):
        print(f"{user.name} uses {self.name}.")
        user.mana.current -= self.cost
        hit, crit = user.weapon_damage(target)
        if hit:
            t_chance = target.check_mod('luck', luck_factor=15)
            print(f"{user.name} latches onto {target.name}.")
            if any([target.status_effects['Stun'].active, target.status_effects["Sleep"].active]) or \
                (random.randint(user.stats.strength // 2, user.stats.strength) >
                 random.randint(target.stats.con // 2, target.stats.con) + t_chance):
                resist = target.check_mod('resist', 'Physical')
                damage = int(random.randint(user.stats.strength // 4, user.stats.strength) * (1 - resist)) * crit
                target.health.current -= damage
                if damage > 0:
                    print(f"{user.name} does an additional {damage} damage to {target.name}.")
                    if not target.is_alive() or \
                            (random.randint(user.stats.intel // 2, user.stats.intel) >
                             random.randint(target.stats.wisdom // 2, target.stats.wisdom) + t_chance):
                        target.stats.intel -= 1
                        print(f"{user.name} eats a part of {target.name}'s brain, lowering their intelligence by 1.")


class Counterspell(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Counterspell", description="If the Behemoth is the target of an attack spell, it will "
                                                          "counter with a spell of its own.",
                         cost=0)
        self.passive = True

    def use(self, user, target=None, cover=False):
        spell = random.choice(user.spellbook['Spells'].values())
        spell().cast(user, target=target, cover=cover)


class FinalAttack(Skill):
    """

    """

    def __init__(self):
        super().__init__(name="Final Attack", description="Upon death, the behemoth unleashes the powerful Meteor "
                                                          "spell.",
                         cost=0)
        self.passive = True


class ChooseFate(Skill):
    """
    The player gets to choose what the Devil does on his turn; your choices affect the Devil's stats
    Each time Attack is selected, the damage mod goes up (increases attack and armor)
    Each time a spell is selected, the magic mod goes up (increases magic, healing, and magic defense)
    Each time a skill is selected, the damage and magic mod goes down
    """

    def __init__(self):
        super().__init__(name="Choose Fate", description="The Devil likes to toy with his food, letting the player "
                                                         "decide what he will do for that turn.",
                         cost=0)

    def use(self, user, target=None, cover=False):
        print("I'm bored, you choose.")
        options = ['Attack', 'Hellfire', 'Crush']
        option = storyline.get_response(options)
        mod_up = random.randint(10, 25)
        if options[option] == 'Attack':
            _, _ = user.weapon_damage(target)
            user.damage_mod += mod_up
            print("Hahaha, my power increases!")
        elif options[option] == 'Hellfire':
            user.spell_mod += mod_up
            Hellfire().cast(user, target=target)
            print("The devastation will only get worse from here.")
        elif options[option] == "Crush":
            Crush().use(user, target)
            mod_down = random.randint(0, 10)
            if user.damage_mod > 0:
                user.damage_mod -= mod_down
            if user.spell_mod > 0:
                user.spell_mod -= mod_down
            print("Interesting choice...maybe I'll show pity.")
        else:
            raise AssertionError("You shouldn't reach here.")


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

    def cast(self, caster, target=None, cover=False, special=False):
        if not special:
            print(f"{caster.name} casts {self.name}.")
            caster.mana.current -= self.cost
        stun = target.status_effects['Stun'].active
        reflect = target.status_effects['Reflect'].active
        spell_mod = caster.check_mod('magic')
        dodge = target.dodge_chance(caster) > random.random()
        hit_per = caster.hit_chance(target, typ='spell')
        hit = hit_per > random.random()
        if stun:
            dodge = False
            hit = True
        if dodge and not reflect:
            print(f"{target.name} dodged the {self.name} and was unhurt.")
        elif cover:
            print(f"{target.familiar.name} steps in front of the attack, absorbing the damage directed at "
                  f"{target.name}.")
        else:
            if hit:
                spell_dmg = int(self.damage + spell_mod)
                if reflect:
                    target = caster
                    print(f"{self.name} is reflected back at {caster.name}!")
                resist = target.check_mod('resist', typ=self.subtyp)
                dam_red = target.check_mod('magic def')
                damage = int(random.randint(spell_dmg // 2, spell_dmg))
                crit = 1
                if not random.randint(0, self.crit):
                    crit = 2
                damage *= crit
                if crit == 2:
                    print("Critical Hit!")
                if target.status_effects['Mana Shield'].active:
                    damage //= target.status_effects['Mana Shield'].duration
                    if damage > target.mana.current:
                        print(f"The mana shield around {target.name} absorbs {target.mana.current} damage.")
                        damage -= target.mana.current
                        target.mana.current = 0
                        target.status_effects['Mana Shield'].active = False
                    else:
                        print(f"The mana shield around {target.name} absorbs {damage} damage.")
                        target.mana.current -= damage
                        damage = 0
                if damage < 0:
                    target.health.current -= damage
                    print(f"{target.name} absorbs {self.subtyp} and is healed for {abs(damage)} health.")
                else:
                    damage = int(damage * (1 - resist))
                    damage -= random.randint(dam_red // 4, dam_red)
                    if damage <= 0:
                        print(f"{self.name} was ineffective and does no damage.")
                        damage = 0
                    elif random.randint(0, target.stats.con // 2) > \
                            random.randint((caster.stats.intel * crit) // 2, (caster.stats.intel * crit)):
                        damage //= 2
                        if damage > 0:
                            print(f"{target.name} shrugs off the {self.name} and only receives half of the damage.")
                            print(f"{caster.name} damages {target.name} for {damage} hit points.")
                        else:
                            print(f"{self.name} was ineffective and does no damage.")
                    else:
                        print(f"{caster.name} damages {target.name} for {damage} hit points.")
                    target.health.current -= damage
                    if target.is_alive() and damage > 0 and not reflect:
                        self.special_effect(caster, target, damage, crit)
                    elif target.is_alive() and damage > 0 and reflect:
                        self.special_effect(caster, caster, damage, crit)
                if 'Counterspell' in target.spellbook['Spells']:
                    print(f"{target.name} uses Counterspell.")
                    Counterspell().use(target, caster)
            else:
                print(f"The spell misses {target.name}.")


class HolySpell(Spell):
    """

    """

    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Holy'


@dataclass
class SupportSpell(Spell):
    """

    """

    subtyp: str = 'Support'


@dataclass
class DeathSpell(Spell):
    """

    """

    subtyp: str = 'Death'


@dataclass
class StatusSpell(Spell):
    """

    """

    subtyp: str = 'Status'


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

    def cast(self, caster, target=None, cover=False, special=False):
        target = caster
        if not special:
            print(f"{caster.name} casts {self.name}.")
            caster.mana.current -= self.cost
        crit = 1
        heal_mod = caster.check_mod('heal')
        heal = int((random.randint(target.health.max // 2, target.health.max) + heal_mod) * self.heal)
        if self.turns:
            self.hot(target, heal)
        else:
            if not random.randint(0, self.crit):
                print("Critical Heal!")
                crit = 2
            heal *= crit
            target.health.current += heal
            print(f"{caster.name} heals {target.name} for {heal} hit points.")
            if target.health.current >= target.health.max:
                target.health.current = target.health.max
                print(f"{target.name} is at full health.")

    def cast_out(self, player_char):
        player_char.mana.current -= self.cost
        print(f"{player_char.name} casts {self.name}.")
        if player_char.health.current == player_char.health.max:
            print("You are already at full health.")
            return
        crit = 1
        heal_mod = player_char.check_mod('heal')
        heal = int(player_char.health.max * self.heal + heal_mod)
        if not random.randint(0, self.crit):
            print("Critical Heal!")
            crit = 2
        heal *= crit
        player_char.health.current += heal
        print(f"{player_char.name} heals themself for {heal} hit points.")
        if player_char.health.current >= player_char.health.max:
            player_char.health.current = player_char.health.max
            print(f"{player_char.name} is at full health.")


@dataclass
class MovementSpell(Spell):
    """

    """

    subtyp: str = 'Movement'


# Spells
class MagicMissile(Attack):
    """
    Can't be reflected
    """

    def __init__(self):
        super().__init__(name='Magic Missile', description='Orbs of energy shoots forth from the caster, dealing '
                                                           'non-elemental damage.',
                         cost=5, damage=8, crit=8)
        self.subtyp = 'Non-elemental'
        self.missiles = 1

    def cast(self, caster, target=None, cover=False, special=False):
        if not special:
            name = caster.name
            print(f"{name} casts {self.name}.")
            caster.mana.current -= self.cost
        stun = any(target.status_effects[x].active for x in ['Sleep', 'Stun', 'Prone'])
        spell_mod = caster.check_mod('magic')
        hits = []
        for i in range(self.missiles):
            hits.append(False)
            dodge = target.dodge_chance(caster) > random.random()
            hit_per = caster.hit_chance(target, typ='spell')
            hits[i] = hit_per > random.random()
            if stun:
                dodge = False
                hits[i] = True
            damage = 0
            damage += random.randint(self.damage + spell_mod // 2, (self.damage + spell_mod))
            crit = 1
            if not random.randint(0, self.crit):
                crit = 2
            damage *= crit
            if crit == 2:
                print("Critical Hit!")
            if dodge:
                print(f"{target.name} dodged the {self.name} and was unhurt.")
            elif cover:
                print(f"{target.familiar.name} steps in front of the attack, absorbing the damage directed at "
                      f"{target.name}.")
            else:
                if hits[i]:
                    if target.status_effects['Mana Shield'].active:
                        damage //= target.status_effects['Mana Shield'].duration
                        if damage > target.mana.current:
                            print(f"The mana shield around {target.name} absorbs {target.mana.current} damage.")
                            damage -= target.mana.current
                            target.mana.current = 0
                            target.status_effects['Mana Shield'].active = False
                        else:
                            print(f"The mana shield around {target.name} absorbs {damage} damage.")
                            target.mana.current -= damage
                            damage = 0
                    dam_red = target.check_mod('magic def')
                    damage -= random.randint(dam_red // 2, dam_red)
                    if damage <= 0:
                        print(f"{self.name} was ineffective and does no damage")
                        damage = 0
                    elif random.randint(0, target.stats.con // 2) > \
                            random.randint(caster.stats.intel // 2, caster.stats.intel):
                        damage //= 2
                        if damage > 0:
                            print(f"{target.name} shrugs off the {self.name} and only receives half of the damage.")
                            print(f"{name} damages {target.name} for {damage} hit points.")
                        else:
                            print(f"{self.name} was ineffective and does no damage")
                    else:
                        print(f"{name} damages {target.name} for {damage} hit points.")
                    target.health.current -= damage
                    time.sleep(1)
                    if not target.is_alive():
                        break
                else:
                    print(f"The spell misses {target.name}.")
                time.sleep(0.1)
        if any(hits):
            if 'Counterspell' in target.spellbook['Spells']:
                print(f"{target.name} uses Counterspell.")
                Counterspell().use(target, caster)


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


class Meteor(Attack):
    """
    Enemy spell - Final Attack for Behemoth
    """

    def __init__(self):
        super().__init__(name='Meteor', description='A large, extra-terrestrial rock falls from the heavens, crushing '
                                                    'the target for immense damage.',
                         cost=0, damage=75, crit=3)
        self.subtyp = 'Non-elemental'


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
                         cost=10, damage=25, crit=10)
        self.subtyp = 'Fire'
        self.school = 'Arcane'


class Firestorm(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Firestorm', description='Fire rains from the sky, incinerating the enemy.',
                         cost=20, damage=40, crit=10)
        self.subtyp = 'Fire'
        self.school = 'Arcane'


class Scorch(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Scorch', description='Light a fire and watch the enemy burn!',
                         cost=6, damage=14, crit=9)
        self.subtyp = 'Fire'
        self.school = 'Elemental'


class MoltenRock(Attack):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Molten Rock', description='A giant, molten boulder is hurled at the enemy, dealing great'
                                                         ' fire damage.',
                         cost=16, damage=28, crit=9)
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
                         cost=24, damage=48, crit=9)
        self.subtyp = 'Fire'
        self.school = 'Elemental'
        self.rank = 2


class IceLance(Attack):
    """
    Arcane ice spells have lower average damage but have the highest chance to crit
    """

    def __init__(self):
        super().__init__(name='Ice Lance', description='A javelin of ice launched at the enemy.',
                         cost=4, damage=4, crit=2)
        self.subtyp = 'Ice'
        self.school = 'Arcane'


class Icicle(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Icicle', description='Frozen shards rain from the sky.',
                         cost=9, damage=15, crit=2)
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
                         cost=6, damage=10, crit=4)
        self.subtyp = 'Electric'
        self.school = 'Arcane'


class Lightning(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Lightning', description='Throws a bolt of lightning at the enemy.',
                         cost=15, damage=18, crit=4)
        self.subtyp = 'Electric'
        self.school = 'Arcane'


class Electrocution(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Electrocution', description='A million volts of electricity passes through the enemy.',
                         cost=25, damage=32, crit=4)
        self.subtyp = 'Electric'
        self.school = 'Arcane'


class WaterJet(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Water Jet', description='A jet of water erupts from beneath the enemy\'s feet.',
                         cost=4, damage=12, crit=3)
        self.subtyp = 'Water'
        self.school = 'Elemental'


class Aqualung(Attack):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Aqualung', description='Giant water bubbles surround the enemy and burst, causing great '
                                                      'water damage.',
                         cost=13, damage=20, crit=3)
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
                         cost=3, damage=8, crit=8)
        self.subtyp = 'Earth'
        self.school = 'Elemental'


class Mudslide(Attack):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Mudslide', description='A torrent of mud and earth sweep over the enemy, causing earth '
                                                      'damage.',
                         cost=16, damage=30, crit=8)
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
                         cost=26, damage=50, crit=8)
        self.subtyp = 'Earth'
        self.school = 'Elemental'
        self.rank = 2


class Sandstorm(Attack):
    """
    Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Sandstorm', description='Engulf the enemy in a sandstorm, doing damage and blinding '
                                                       'them.',
                         cost=22, damage=32, crit=6)
        self.subtyp = 'Earth'

    def special_effect(self, caster, target, damage, crit):
        if not target.status_effects["Blind"].active:
            if random.randint(caster.stats.intel // 2, caster.stats.intel) > \
                    random.randint(target.stats.con // 2, target.stats.con):
                target.status_effects['Blind'].active = True
                target.status_effects['Blind'].duration = max(2, caster.stats.intel // 10)
                print(f"{target.name} is blinded by the {self.name}.")


class Gust(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Gust', description='A strong gust of wind whips past the enemy.',
                         cost=7, damage=15, crit=6)
        self.subtyp = 'Wind'
        self.school = 'Elemental'


class Hurricane(Attack):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Hurricane', description='A violent storm berates your foes, causing great wind damage.',
                         cost=22, damage=26, crit=6)
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
                         cost=40, damage=40, crit=6)
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
                         cost=16, damage=12, crit=5)
        self.subtyp = 'Shadow'

    def special_effect(self, caster, target, damage, crit):
        if random.randint((caster.stats.intel * crit) // 2, (caster.stats.intel * crit)) \
                > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
            turns = max(1, caster.stats.intel // 10)
            target.status_effects["DOT"].active = True
            target.status_effects["DOT"].duration = max(turns, target.status_effects["DOT"].duration)
            target.status_effects["DOT"].extra = max(damage, target.status_effects["DOT"].extra)
            print(f"{caster.name}'s magic penetrates {target.name}'s defenses.")


class Terrify(Attack):
    """

    """

    def __init__(self):
        super().__init__(name='Terrify', description='Get in the mind of the enemy, terrifying them into inaction and '
                                                     'doing damage in the process.',
                         cost=18, damage=10, crit=4)

    def special_effect(self, caster, target, damage, crit):
        if not target.status_effects["Stun"].active:
            if random.randint(0, (caster.stats.intel * crit)) > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                turns = max(1, caster.stats.intel // 10)
                target.status_effects["Stun"].active = True
                target.status_effects["Stun"].duration = turns
                print(f"{caster.name} stunned {target.name}.")


class Doom(DeathSpell):
    """
    Can't be reflected
    """

    def __init__(self):
        super().__init__(name='Doom', description='Places a timer on the enemy\'s life, ending it when the timer '
                                                  'expires.',
                         cost=15)
        self.timer = 3

    def cast(self, caster, target=None, cover=False, special=False):
        if not special:
            print(f"{caster.name} casts {self.name}.")
            caster.mana.current -= self.cost
        resist = target.check_mod('resist', typ=self.subtyp)
        chance = target.check_mod('luck', luck_factor=10)
        if resist < 1:
            if not target.status_effects["Doom"].active:
                if random.randint(caster.stats.intel // 4, caster.stats.intel) * (1 - resist) \
                        > random.randint(target.stats.wisdom // 2, target.stats.wisdom) + chance:
                    target.status_effects["Doom"].active = True
                    target.status_effects["Doom"].duration = self.timer
                    print(f"A timer has been placed on {target.name}'s life.")
                else:
                    if not special:
                        print("The magic has no effect.")
        else:
            if not special:
                print(f"{target.name} is immune to death spells.")


class Desoul(DeathSpell):
    """
    Can't be reflected
    """

    def __init__(self):
        super().__init__(name='Desoul', description='Removes the soul from the enemy, instantly killing it.',
                         cost=50)

    def cast(self, caster, target=None, cover=False, special=False):
        if not special:
            print(f"{caster.name} casts {self.name}.")
            caster.mana.current -= self.cost
        resist = target.check_mod('resist', typ=self.subtyp)
        chance = target.check_mod('luck', luck_factor=10)
        if resist < 1:
            if random.randint(0, caster.stats.intel) * (1 - resist) \
                    > random.randint(target.stats.con // 2, target.stats.con) + chance:
                target.health.current = 0
                print(f"{target.name} has their soul ripped right out and falls to the ground dead.")
            else:
                if not special:
                    print("The spell has no effect.")
        else:
            if not special:
                print(f"{target.name} is immune to death spells.")


class Petrify(DeathSpell):
    """
    Rank 2 Enemy Spell; Can't be reflected except by Medusa Shield
    """

    def __init__(self):
        super().__init__(name='Petrify', description='Gaze at the enemy and turn them into stone.',
                         cost=50)
        self.rank = 2

    def cast(self, caster, target=None, cover=False, special=False):
        if not special:
            print(f"{caster.name} casts {self.name}.")
            caster.mana.current -= self.cost
        if target.equipment['OffHand']().name == 'MEDUSA SHIELD':
            print(f"{target.name} uses the Medusa Shield to reflect {self.name} back at {caster.name}!")
            target = caster
        resist = target.check_mod('resist', typ="Stone")
        chance = target.check_mod('luck', luck_factor=1)
        if resist < 1:
            if random.randint(0, caster.stats.intel) * (1 - resist) \
                    > random.randint(target.stats.con // 2, target.stats.con) + chance:
                target.health.current = 0
                print(f"{target.name} is turned to stone!")
            else:
                if not special:
                    print("The spell has no effect.")
        else:
            if not special:
                print(f"{target.name} is immune to death spells.")


class Disintegrate(DeathSpell):
    """
    Can't be reflected or absorbed by Mana Shield
    """

    def __init__(self):
        super().__init__(name='Disintegrate', description='An intense blast focused directly at the target, '
                                                          'obliterating them or doing great damage.',
                         cost=65)

    def cast(self, caster, target=None, cover=False, special=False):
        if not special:
            print(f"{caster.name} casts {self.name}.")
            caster.mana.current -= self.cost
        resist = target.check_mod('resist', typ=self.subtyp)
        chance = target.check_mod('luck', luck_factor=15)
        if resist < 1:
            if random.randint(0, caster.stats.intel) * (1 - resist) \
                    > random.randint(target.stats.con // 2, target.stats.con) + chance:
                target.health.current = 0
                print(f"The intense blast from disintegrate leaves {target.name} in a heap of ashes.")
        if target.is_alive():
            damage = int(caster.stats.intel + (target.health.current * 0.25))
            if random.randint(0, chance):
                print(f"{target.name} dodges the brunt of the blast, taking only half damage.")
                damage //= 2
            target.health.current -= damage
            print(f"The blast from {self.name.lower()} hurts {target.name} for {damage} damage.")


class Smite(HolySpell):
    """
    Can't be reflected; holy damage crit based on melee crit and can be absorbed by mana shield TODO
    """

    def __init__(self):
        super().__init__(name='Smite', description='The power of light rebukes the enemy, adding bonus holy damage to '
                                                   'a successful attack roll.',
                         cost=10, damage=20, crit=4)
        self.school = 'Holy'

    def cast(self, caster, target=None, cover=False):
        print(f"{caster.name} casts {self.name}.")
        caster.mana.current -= self.cost
        hit, crit = caster.weapon_damage(target, cover=cover)
        if hit and target.is_alive():
            spell_mod = caster.check_mod('magic')
            dam_red = target.check_mod('magic def')
            resist = target.check_mod('resist', 'Holy')
            spell_dmg = int(self.damage + spell_mod)
            damage = int(random.randint(spell_dmg // 2, spell_dmg))
            damage *= crit
            if target.status_effects['Mana Shield'].active:
                damage //= target.status_effects['Mana Shield'].duration
                if damage > target.mana.current:
                    print(f"The mana shield around {target.name} absorbs {target.mana.current} damage.")
                    damage -= target.mana.current
                    target.mana.current = 0
                    target.status_effects['Mana Shield'].active = False
                else:
                    print(f"The mana shield around {target.name} absorbs {damage} damage.")
                    target.mana.current -= damage
                    damage = 0
            damage = int(damage * (1 - resist))
            if damage < 0:
                target.health.current -= damage
                print(f"{target.name} absorbs {self.subtyp} and is healed for {abs(damage)} health.")
            else:
                damage -= random.randint(dam_red // 2, dam_red)
                if damage <= 0:
                    damage = 0
                    print(f"{self.name} was ineffective and does no damage.")
                elif random.randint(0, target.stats.con // 2) > \
                        random.randint((caster.stats.intel * crit) // 2, (caster.stats.intel * crit)):
                    damage //= 2
                    if damage > 0:
                        print(f"{target.name} shrugs off the {self.name} and only receives half of the damage.")
                        print(f"{caster.name} smites {target.name} for {damage} hit points.")
                    else:
                        print(f"{self.name} was ineffective and does no damage.")
                else:
                    print(f"{caster.name} smites {target.name} for {damage} hit points.")
                target.health.current -= damage


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
        self.subtyp = 'Holy'


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
    crit will double chance of kill or double damage
    can't be absorbed or reflected
    """

    def __init__(self):
        super().__init__(name="Turn Undead", description="A holy chant is recited with a chance to banish any nearby "
                                                         "undead from existence.",
                         cost=12, damage=5, crit=5)

    def cast(self, caster, target=None, cover=False):
        print(f"{caster.name} casts {self.name}.")
        caster.mana.current -= self.cost
        if target.enemy_typ == "Undead":
            crit = 1
            chance = max(2, target.check_mod('luck', luck_factor=6))
            if not random.randint(0, self.crit):
                print("Critical hit!")
                crit = 2
                chance -= 1
            if not random.randint(0, chance):
                target.health.current = 0
                print(f"The {target.name} has been rebuked, destroying the undead monster.")
            else:
                spell_mod = caster.check_mod('magic')
                dam_red = target.check_mod('magic def')
                resist = target.check_mod('resist', 'Holy')
                spell_dmg = int(self.damage + spell_mod)
                damage = random.randint(spell_dmg // 2, spell_dmg)
                damage *= crit
                damage = int(damage * (1 - resist))
                damage -= dam_red
                target.health.current -= damage
                print(f"{caster.name} damages {target.name} for {damage} hit points.")
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
        self.cost = 18
        self.heal = 0.5
        self.crit = 3


class Heal3(Heal):
    """

    """

    def __init__(self):
        super().__init__()
        self.cost = 25
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

    def hot(self, caster, heal):
        caster.status_effects['Regen'].active = True
        caster.status_effects['Regen'].duration = max(self.turns, caster.status_effects["Regen"].duration)
        caster.status_effects['Regen'].extra = max(heal, caster.status_effects["Regen"].extra)


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
                         cost=8)

    def cast(self, caster, target=None, cover=False):
        if target is None:
            target = caster
            print(f"{caster.name} casts {self.name} on themself.")
        else:
            print(f"{caster.name} casts {self.name} on {target.name}.")
        caster.mana.current -= self.cost
        duration = max(2, caster.stats.wisdom // 10)
        amount = max(5, caster.stats.wisdom // 2)
        target.status_effects['Attack'].active = True
        target.status_effects['Attack'].duration = duration
        target.status_effects['Attack'].extra = amount
        print(f"{target.name}'s attack increases by {amount}.")


class Boost(SupportSpell):
    """
    Increases magic damage
    """

    def __init__(self):
        super().__init__(name="Boost", description="Supercharge the magic capabilities of the target, increasing magic"
                                                   " damage.",
                         cost=22)

    def cast(self, caster, target=None, cover=False):
        if target is None:
            target = caster
            print(f"{caster.name} casts {self.name} on themself.")
        else:
            print(f"{caster.name} casts {self.name} on {target.name}.")
        caster.mana.current -= self.cost
        target.status_effects['Magic'].active = True
        target.status_effects['Magic'].duration = max(2, caster.stats.intel // 10)
        target.status_effects['Magic'].extra = max(1, caster.stats.intel // 2)
        print(f"{target.name}'s magic increases by {target.status_effects['Magic'].extra}.")


class Shell(SupportSpell):
    """
    Increases magic defense
    """

    def __init__(self):
        super().__init__(name="Shell", description="The target is shrouded in a magical veil, lessening the damage from"
                                                   " magic attacks.",
                         cost=26)

    def cast(self, caster, target=None, cover=False):
        if target is None:
            target = caster
            print(f"{caster.name} casts {self.name} on themself.")
        else:
            print(f"{caster.name} casts {self.name} on {target.name}.")
        caster.mana.current -= self.cost
        target.status_effects['Magic Defense'].active = True
        target.status_effects['Magic Defense'].duration = max(2, caster.stats.intel // 10)
        target.status_effects['Magic Defense'].extra = max(1, caster.stats.intel // 2)
        print(f"{target.name}'s magic defense increases by {target.status_effects['Magic Defense'].extra}.")


class ManaShield(SupportSpell):
    """
    Reduction indicates how much damage a single mana point reduces
    """

    def __init__(self):
        super().__init__(name="Mana Shield", description="A protective shield envelopes the caster, absorbing damage "
                                                         "at the expense of mana.",
                         cost=0)
        self.reduction = 1

    def cast(self, caster, target=None, cover=False):
        target = caster
        print(f"{caster.name} casts {self.name}.")
        caster.mana.current -= self.cost
        target.status_effects['Mana Shield'].active = True
        target.status_effects['Mana Shield'].duration = self.reduction
        print(f"A mana shield envelopes {target.name}.")


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

    def cast(self, caster, target=None, cover=False):
        if target is None:
            target = caster
            print(f"{caster.name} casts {self.name} on themself.")
        else:
            print(f"{caster.name} casts {self.name} on {target.name}.")
        caster.mana.current -= self.cost
        target.status_effects['Reflect'].active = True
        target.status_effects['Reflect'].duration = max(2, caster.stats.intel // 10)
        print(f"A magic force field envelopes {target.name}.")


class Resurrection(SupportSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Resurrection", description="The ultimate boon bestowed upon only the chosen few. Life "
                                                          "returns where it once left.",
                         cost=0)
        self.passive = True

    def cast(self, caster, target=None, cover=False):
        if target is None:
            target = caster
            print(f"{caster.name} casts {self.name} on themself.")
            max_heal = target.health.max - target.health.current
            if target.mana.current > max_heal:
                target.health.current = target.health.max
                target.mana.current -= max_heal
                print(f"{target.name} expends mana and is healed to full life!")
            else:
                target.health.current += target.mana.current
                print(f"{target.name} expends all mana and is healed for {target.mana.current} hit points!")
                target.mana.current = 0
        else:
            print(f"{caster.name} casts {self.name} on {target.name}.")
            heal = int(target.health.max * 0.1)
            target.health.current = heal
            print(f"{target.name} is brought back to life and is healed for {heal} hit points.")
        caster.mana.current -= self.cost


class Cleanse(SupportSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Cleanse", description="You feel all ailments leave your body like a draught of panacea.",
                         cost=20)

    def cast(self, caster, target=None, cover=False, special=False):
        if target is None:
            target = caster
        if not special:
            if target is None:
                print(f"{caster.name} casts {self.name} on themself.")
            else:
                print(f"{caster.name} casts {self.name} on {target.name}.")
            caster.mana.current -= self.cost
        target.status_effects['Stun'].active = False
        target.status_effects['Doom'].active = False
        target.status_effects['Blind'].active = False
        target.status_effects['Sleep'].active = False
        target.status_effects['Poison'].active = False
        target.status_effects['DOT'].active = False
        target.status_effects['Bleed'].active = False
        print(f"All negative status effects have been cured for {target.name}!")


class Sanctuary(MovementSpell):
    """

    """

    def __init__(self):
        super().__init__(name='Sanctuary', description='Return to town from anywhere in the dungeon.',
                         cost=100)

    def cast_out(self, player_char):
        player_char.mana.current -= self.cost
        print(f"{player_char.name} casts Sanctuary and is transported back to town.")
        player_char.health.current = player_char.health.max
        player_char.mana.current = player_char.mana.max
        player_char.location_x, player_char.location_y, player_char.location_z = (5, 10, 0)


class Teleport(MovementSpell):
    """

    """

    def __init__(self):
        super().__init__(name='Teleport', description='Teleport the user to a previously set location.',
                         cost=50)
        self.combat = False

    def cast_out(self, player_char):
        options = ['Set', 'Teleport']
        option_index = storyline.get_response(options)
        if options[option_index] == 'Set':
            print(f"This location has been set for teleport by {player_char.name}.")
            player_char.teleport = player_char.location_x, player_char.location_y, player_char.location_z
        else:
            print(f"{player_char.name} teleports to set location.")
            player_char.mana.current -= self.cost
            player_char.location_x, player_char.location_y, player_char.location_z = player_char.teleport


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

    def cast(self, caster, target=None, cover=False):
        print(f"{caster.name} casts {self.name}.")
        caster.mana.current -= self.cost
        if not target.status_effects["Blind"].active:
            if random.randint(caster.stats.intel // 2, caster.stats.intel) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                target.status_effects['Blind'].active = True
                target.status_effects['Blind'].duration = self.turns
                print(f"{target.name} is blinded.")
            else:
                print("The spell had no effect.")
        else:
            print(f"{target.name} is already blinded.")


class PoisonBreath(Attack):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__(name="Poison Breath", description="Your spew forth a toxic breath, dealing poison damage and "
                                                           "poisoning the target.",
                         cost=20, damage=15, crit=5)
        self.subtyp = 'Poison'
        self.school = 'Poison'
        self.rank = 2

    def special_effect(self, caster, target, damage, crit):
        if random.randint((caster.stats.intel * crit) // 2, (caster.stats.intel * crit)) \
                > random.randint(target.stats.con // 2, target.stats.con) and not target.status_effects['Mana Shield'].active:
            turns = max(2, caster.stats.intel // 10)
            target.status_effects['Poison'].active = True
            target.status_effects['Poison'].duration = max(turns, target.status_effects["Poison"].duration)
            target.status_effects['Poison'].extra = max(damage, target.status_effects["Poison"].extra)
            print(f"{caster.name} poisons {target.name}.")


class DiseaseBreath(StatusSpell):
    """
    Enemy Spell; not learnable by player
    """

    def __init__(self):
        super().__init__(name="Disease Breath", description="A diseased cloud emanates onto the enemy, with a chance to"
                                                            " lower the enemy's constitution permanently.",
                         cost=25)
        self.school = 'Disease'

    def cast(self, caster, target=None, cover=False):
        caster.mana.current -= self.cost
        print(f"{caster.name} casts {self.name}.")
        t_chance = target.check_mod('luck', luck_factor=10)
        if random.randint(caster.stats.intel // 2, caster.stats.intel) > \
                random.randint(target.stats.con // 2, target.stats.con):
            if not random.randint(0, 9 + t_chance):
                print(f"The disease cripples {target.name}, lowering their constitution by 1.")
                target.stats.con -= 1
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

    def cast(self, caster, target=None, cover=False):
        print(f"{caster.name} casts {self.name}.")
        caster.mana.current -= self.cost
        if not target.status_effects["Sleep"].active:
            if random.randint(caster.stats.intel // 2, caster.stats.intel) \
                    > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                target.status_effects['Sleep'].active = True
                target.status_effects['Sleep'].duration = self.turns
                print(f"{target.name} is asleep.")
            else:
                print(f"{caster.name} fails to put {target.name} to sleep.")
        else:
            print(f"{target.name} is already asleep.")


class Stupefy(StatusSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Stupefy", description="Hit the enemy so hard, they go stupid and cannot act.",
                         cost=14)
        self.turns = 2

    def cast(self, caster, target=None, cover=False):
        print(f"{caster.name} casts {self.name} on {target.name}.")
        caster.mana.current -= self.cost
        if not target.status_effects["Stun"].active:
            if random.randint(0, caster.stats.intel) \
                    > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                target.status_effects['Stun'].active = True
                target.status_effects['Stun'].duration = self.turns
                print(f"{target.name} is stunned.")
            else:
                print(f"{caster.name} fails to stun {target.name}.")
        else:
            print(f"{target.name} is already stunned.")


class WeakenMind(StatusSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Weaken Mind", description="Attack the enemy's mind, diminishing their ability to deal "
                                                         "damage and defend against magic.",
                         cost=20)

    def cast(self, caster, target=None, cover=False):
        print(f"{caster.name} casts {self.name} on {target.name}.")
        caster.mana.current -= self.cost
        if random.randint(caster.stats.intel // 2, caster.stats.intel) > random.randint(target.stats.con // 2, target.stats.con):
            for stat in ['Magic', 'Magic Defense']:
                stat_mod = random.randint(max(1, caster.stats.intel // 5), max(5, caster.stats.intel // 2))
                target.status_effects[stat].active = True
                target.status_effects[stat].duration = random.randint(1, max(2, caster.stats.intel // 10))
                target.status_effects[stat].extra = target.status_effects[stat] - stat_mod
                print(f"{target.name}'s {stat.lower()} is lowered by {stat_mod}.")


class Enfeeble(StatusSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Enfeeble", description="Cripple your foe, reducing their attack and defense rating.",
                         cost=12)

    def cast(self, caster, target=None, cover=False):
        print(f"{caster.name} casts {self.name} on {target.name}.")
        caster.mana.current -= self.cost
        if random.randint(caster.stats.intel // 2, caster.stats.intel) > random.randint(target.stats.con // 2, target.stats.con):
            for stat in ['Attack', 'Defense']:
                stat_mod = random.randint(max(1, caster.stats.intel // 5), max(5, caster.stats.intel // 2))
                target.status_effects[stat].active = True
                target.status_effects[stat].duration = random.randint(1, max(2, caster.stats.intel // 10))
                target.status_effects[stat].extra = target.status_effects[stat].extra - stat_mod
                print(f"{target.name}'s {stat.lower()} is lowered by {stat_mod}.")
        else:
            print(f"{target.name} resists the spell.")


class Dispel(StatusSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Dispel", description="Cast an anti-magic spell on your foe, removing any positive status"
                                                    " effects.",
                         cost=20)

    def cast(self, caster, target=None, cover=False):
        print(f"{caster.name} casts {self.name} on {target.name}.")
        caster.mana.current -= self.cost
        if random.randint(caster.stats.intel // 2, caster.stats.intel) > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
            target.status_effects["Regen"].active = False
            target.status_effects["Attack"].active = False
            target.status_effects["Defense"].active = False
            target.status_effects["Magic"].active = False
            target.status_effects["Magic Defense"].active = False
            print(f"All positive status effects removed from {target.name}.")
        else:
            print(f"{target.name} resists the spell.")


class Silence(StatusSpell):
    """

    """

    def __init__(self):
        super().__init__(name="Silence", description="Tongue-tie the enemy's brain, making spell casting impossible.",
                         cost=20)

    def cast(self, caster, target=None, cover=False):
        print(f"{caster.name} casts {self.name} on {target.name}.")
        caster.mana.current -= self.cost
        if not target.status_effects["Silence"].active:
            if random.randint(caster.stats.intel // 2, caster.stats.intel) > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                target.status_effects['Silence'].active = True
                target.status_effects['Silence'].duration = random.randint(1, max(2, caster.stats.intel // 10))
                print(f"{target.name} has been silenced.")
            else:
                print("The spell is ineffective.")
        else:
            print(f"{target.name} is already silenced.")


# Enemy spells
class Hellfire(Attack):
    """
    Devil's spell; the fire is non-elemental
    """

    def __init__(self):
        super().__init__(name="Hellfire", description="The flames of Hell lick at the toes of the enemy, inflicting "
                                                      "immense initial damage as well as damage over time.",
                         cost=25, damage=100, crit=2)
        self.subtyp = 'Non-elemental'

    def special_effect(self, caster, target, damage, crit):
        if random.randint((caster.stats.intel * crit) // 2, (caster.stats.intel * crit)) \
                > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
            turns = max(2, caster.stats.intel // 10)
            target.status_effects["DOT"].active = True
            target.status_effects["DOT"].duration = max(turns, target.status_effects["DOT"].duration)
            target.status_effects["DOT"].extra = max(damage, target.status_effects["DOT"].extra)
            print(f"The flames of Hell continue to burn {target.name}.")


# Parameters
skill_dict = {'Warrior': {'3': ShieldSlam,
                          '8': PiercingStrike,
                          '10': Disarm,
                          '13': Parry,
                          '15': Charge},
              'Weapon Master': {'1': MortalStrike,
                                '6': DoubleStrike,
                                '20': TripleStrike},
              'Berserker': {'1': BattleCry,
                            '5': MortalStrike2,
                            '15': QuadStrike},
              'Paladin': {'6': ShieldBlock,
                          '18': DoubleStrike},
              'Crusader': {'5': MortalStrike,
                           '22': TripleStrike},
              'Lancer': {'2': Jump,
                         '15': DoubleJump},
              'Dragoon': {'10': ShieldBlock,
                          '12': BattleCry,
                          '20': TripleJump},
              'Mage': {},
              'Sorcerer': {'10': DoubleCast},
              'Wizard': {'15': TripleCast},
              'Warlock': {'1': Familiar,
                          '5': HealthDrain,
                          '15': ManaDrain,
                          '20': Familiar2},
              'Shadowcaster': {'10': HealthManaDrain,
                               '20': Familiar3},
              'Spellblade': {'1': EnhanceBlade,
                             '10': ImbueWeapon,
                             '15': Parry},
              'Knight Enchanter': {'1': EnhanceArmor,
                                   '10': DoubleStrike},
              'Footpad': {'3': Disarm,
                          '5': SmokeScreen,
                          '6': PocketSand,
                          '8': Backstab,
                          '10': Steal,
                          '12': KidneyPunch,
                          '16': DoubleStrike,
                          '19': SleepingPowder,
                          '20': Parry},
              'Thief': {'5': Lockpick,
                        '8': TripleStrike,
                        '15': Mug,
                        '20': PoisonStrike},
              'Rogue': {'20': QuadStrike},
              'Inquisitor': {'1': ShieldSlam,
                             '5': Inspect,
                             '10': ExploitWeakness,
                             '12': TripleStrike,
                             '15': ShieldBlock,
                             '18': MortalStrike},
              'Seeker': {'6': Charge,
                         '10': KeenEye,
                         '13': Parry},
              'Assassin': {'5': TripleStrike,
                           '8': PoisonStrike,
                           '15': Lockpick,
                           '20': QuadStrike},
              'Ninja': {'8': Mug,
                        '25': FlurryBlades},
              'Healer': {},
              'Cleric': {'6': ShieldSlam,
                         '12': ShieldBlock},
              'Templar': {'2': Parry,
                          '14': Charge},
              'Priest': {},
              'Archbishop': {'5': DoubleCast},
              'Monk': {'1': ChiHeal,
                       '3': DoubleStrike,
                       '5': LegSweep,
                       '13': KidneyPunch,
                       '19': TripleStrike},
              'Master Monk': {'10': QuadStrike},
              'Pathfinder': {},
              'Druid': {'1': Transform,
                        '10': Transform2},
              'Lycan': {'1': Transform3},
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
                           '18': Smite3,
                           '20': Dispel},
              'Lancer': {},
              'Dragoon': {},
              'Mage': {'2': Firebolt,
                       '6': MagicMissile,
                       '8': IceLance,
                       '13': Shock,
                       '16': Enfeeble},
              'Sorcerer': {'2': Icicle,
                           '6': Reflect,
                           '8': Lightning,
                           '10': Sleep,
                           '15': Fireball,
                           '16': Dispel,
                           '18': MagicMissile2,
                           '20': WeakenMind},
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
                          '15': Doom,
                          '19': Dispel},
              'Shadowcaster': {'8': ShadowBolt3,
                               '18': Desoul},
              'Spellblade': {'20': Reflect},
              'Knight Enchanter': {'1': EnhanceArmor,
                                   '3': Fireball,
                                   '9': Icicle,
                                   '12': Lightning,
                                   '20': Dispel},
              'Footpad': {},
              'Thief': {},
              'Rogue': {},
              'Inquisitor': {'3': Dispel,
                             '12': Enfeeble,
                             '15': Reflect},
              'Seeker': {'1': Teleport,
                         '10': Sanctuary},
              'Assassin': {},
              'Ninja': {'20': Desoul},
              'Healer': {'2': Heal,
                         '8': Regen,
                         '10': Holy,
                         '18': Heal2},
              'Cleric': {'2': Smite,
                         '3': TurnUndead,
                         '5': Bless,
                         '14': Cleanse,
                         '15': Silence,
                         '16': Smite2,
                         '19': TurnUndead2},
              'Templar': {'6': Regen2,
                          '10': Smite3,
                          '18': Dispel},
              'Priest': {'1': Regen2,
                         '3': Holy2,
                         '6': Shell,
                         '8': Heal3,
                         '10': ManaShield,
                         '11': Cleanse,
                         '15': Bless,
                         '17': Dispel},
              'Archbishop': {'4': Holy3,
                             '6': Silence,
                             '7': Regen3,
                             '15': ManaShield2,
                             '20': Resurrection},
              'Monk': {'15': Shell},
              'Master Monk': {'2': Reflect,
                              '12': Dispel},
              'Pathfinder': {'5': Tremor,
                             '11': WaterJet,
                             '14': Gust,
                             '19': Scorch},
              'Druid': {'5': Regen},
              'Lycan': {'8': Dispel},
              'Diviner': {'3': Enfeeble,
                          '14': Dispel},
              'Geomancer': {'10': WeakenMind,
                            '15': Boost},
              'Shaman': {'9': Regen},
              'Soulcatcher': {'6': Dispel,
                              '12': Desoul},
              }
