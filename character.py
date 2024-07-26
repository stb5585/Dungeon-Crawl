##########################################
""" character manager """

# Imports
import time
import random
from math import exp

from dataclasses import dataclass


# Character dataclasses
@dataclass
class Stats:
    """
    Attributes:
        strength: The strength attribute of the character, influencing physical damage.
        intel: The intelligence attribute of a character, influencing magical damage.
        wisdom: The wisdom attribute of the character, influencing resistance to magical effects.
        con: The constitution attribute of the character, influencing resistance to certain effects.
        charisma: The charisma attribute of the character, influencing interactions with NPCs.
        dex: The dexterity attribute of the character, influencing speed and avoidance.
    """
    strength: int = 0
    intel: int = 0
    wisdom: int = 0
    con: int = 0
    charisma: int = 0
    dex: int = 0

@dataclass
class Resource:
    max: int = 0
    current: int = 0

@dataclass
class Level:
    level: int = 1
    pro_level: int = 0
    exp: int = 0
    exp_to_gain: int = 0

@dataclass
class StatusEffect:
    active: bool = False
    duration: int = 0
    extra: int = 0


class Character:
    """
    A class representing a character in a game, encapsulating attributes such as health, 
    status effects, and combat-related properties.

    Attributes:
        name (str): The name of the character.
        race (object): The race of the character.
        cls (object): The class of the character.
        health (Resource): A dataclass containing the maximum and current health of the character.
        mana (Resource): A dataclass containing the maximum and current mana of the character.
        stats (Stats): A dataclass containing the 6 primary statistics of the character.
        level (Level): A dataclass containing the level, promotion level, experience, and experience to gain of the character.
        equipment (Dict[str, object]): A dictionary containing the items which the character is currently equipped. 
        inventory (Dict[str, List[object, int]]): A dictionary containing the character's inventory, including the item
            and quantity.
        special_inventory (Dict[str, List[object, int]]): A dictionary containing the character's special inventory, 
            including the item and quantity. The special inventory stores items that are related to quests or the plot
            of the story.
        spellbook (Dict[str, Dict[str, Spell]]): A dictionary containing the spells and skills learned for the
            character to use.
        status_effects (Dict[str, StatusEffect]): A dictionary containing the character's status effects.
        resistance (Dict[str, float]): A dictionary containing the elemental impact on the character.
        flying (bool): A boolean variable indicating whether the character is flying or not. Flying affects chance
            to hit and some elemental effect.
        invisible (bool): A boolean variable indicating whether the character is invisible or not. Invisibility
            affects chance to hit.
    Methods:
        __init__():
            Initializes a Character object.
        
        statuses(end=False):
            Manages and updates the character's status effects, applying their respective consequences
            and handling the end of combat.
    """


    def __init__(self, name: str, health: Resource, mana: Resource, stats: Stats):
        self.name = name
        self.race = None
        self.cls = None
        self.health = health
        self.mana = mana
        self.stats = stats
        self.level = Level(1, 1, 0, 0)
        self.equipment = {}
        self.inventory = {}
        self.spellbook = {'Spells': {},
                          'Skills': {}}
        self.status_effects={"Prone": StatusEffect(False, 0), "Silence": StatusEffect(False, 0),
                             "Mana Shield": StatusEffect(False, 0), "Stun": StatusEffect(False, 0),
                             "Doom": StatusEffect(False, 0), "Blind": StatusEffect(False, 0),
                             "Disarm": StatusEffect(False, 0), "Sleep": StatusEffect(False, 0),
                             "Reflect": StatusEffect(False, 0), "Poison": StatusEffect(False, 0, 0),
                             "DOT": StatusEffect(False, 0, 0), "Bleed": StatusEffect(False, 0, 0),
                             "Regen": StatusEffect(False, 0, 0), "Attack": StatusEffect(False, 0, 0),
                             "Defense": StatusEffect(False, 0, 0), "Magic": StatusEffect(False, 0, 0),
                             "Magic Defense": StatusEffect(False, 0, 0)}
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

    def hit_chance(self, defender, typ='weapon'):
        """
        Calculate hit chance based on various factors.

        Things that affect hit chance
            Weapon attack: whether char is blind, if enemy is flying and/or invisible, enemy status effects,
                accessory bonuses, difference in pro level
            Spell attack: enemy status effects
        """

        def sigmoid(x):
            return 1 / (1 + exp(-x))

        hit_mod = sigmoid(random.randint(self.stats.dex // 2, self.stats.dex) /
                          random.randint(defender.stats.dex // 4, defender.stats.dex))  # base hit percentage
        if typ == 'weapon':
            hit_mod *= 1 + 0.25 * ('Accuracy' in self.equipment['Ring']().mod)  # accuracy adds 25% chance to hit
            hit_mod *= 1 - 0.5 * self.status_effects['Blind'].active  # blind lowers accuracy by 50%
            hit_mod *= 1 - (1 / 10) * defender.flying  # flying lowers accuracy by 10%
            hit_mod += 0.05 * (self.level.pro_level - defender.level.pro_level)  # makes it easier to hit lower level creatures
        else:
            hit_mod = 1
        hit_mod *= 1 - (1 / 3) * defender.invisible  # invisible lowers accuracy by 33.3%
        return max(0, hit_mod)

    def dodge_chance(self, attacker, typ='weapon'):
        a_chance = attacker.check_mod('luck', luck_factor=10)
        if typ == 'weapon':
            a_chance += random.randint(attacker.stats.dex // 2, attacker.stats.dex)
        d_chance = random.randint(0, self.stats.dex) + self.check_mod('luck', luck_factor=15)
        chance = (d_chance - a_chance) / (a_chance + d_chance)
        chance += 0.1 * ('Dodge' in self.equipment['Ring']().mod)
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
            ignore = ignore or self.equipment[att]().ignore
            # attacker variables
            typ = 'attacks'
            if self.equipment[att]().subtyp == 'Natural':
                typ = self.equipment[att]().att_name
                if typ == 'leers':
                    hits[i] = True
                    self.equipment[att]().special_effect(self, defender)
                    break

            crit_chance = self.equipment[att]().crit + (0.005 * self.stats.dex)
            crits[i] = 2 if crit == 1 and crit_chance > random.random() else crit
            dmg = max(1, dmg_mod + self.check_mod(att.lower()))
            damage = max(0, int(random.randint(dmg // 2, dmg) * crits[i]))

            # defender variables
            prone = defender.status_effects['Prone'].active
            stun = defender.status_effects['Stun'].active
            sleep = defender.status_effects['Sleep'].active
            dam_red = defender.check_mod('armor', ignore=ignore)
            resist = defender.check_mod('resist', typ='Physical', ultimate=self.equipment[att]().ultimate)
            dodge = defender.dodge_chance(self) > random.random()
            hit_per = self.hit_chance(defender, typ='weapon')
            hits[i] = hit_per > random.random()
            if any([prone, stun, sleep]):
                dodge = False
                hits[i] = True

            # combat
            if dodge:
                hits[i] = False
                if 'Parry' in defender.spellbook['Skills']:
                    print(f"{defender.name} parries {self.name}'s attack and counterattacks!")
                    defender.weapon_damage(self)
                    if not self.is_alive():
                        return False, max(crits)
                else:
                    print(f"{defender.name} evades {self.name}'s attack.")
            else:
                if hits[i]:
                    if crits[i] > 1:
                        print("Critical hit!")
                    if cover:
                        print(f"{defender.familiar.name} steps in front of the attack, "
                              f"taking the damage for {defender.name}.")
                        damage = 0
                    elif ((defender.equipment['OffHand']().subtyp == 'Shield' or
                           'Dodge' in defender.equipment['Ring']().mod) and
                          not defender.status_effects['Mana Shield'].active) and (not stun and not sleep):
                        blk_chance = defender.equipment['OffHand']().mod + \
                                     (('Block' in defender.equipment['Ring']().mod) * 0.25)
                        if blk_chance > random.random():
                            blk_amt = (defender.stats.strength * blk_chance) / self.stats.strength
                            if 'Shield Block' in defender.spellbook['Skills']:
                                blk_amt *= 2
                            blk_amt = min(1, blk_amt)
                            damage *= (1 - blk_amt)
                            damage = int(damage * (1 - resist))
                            print(f"{defender.name} blocks {self.name}'s attack and mitigates "
                                  f"{int(blk_amt * 100)} percent of the damage.")
                    elif defender.status_effects['Mana Shield'].active:
                        damage //= defender.status_effects['Mana Shield'].duration
                        if damage > defender.mana.current:
                            print(f"The mana shield around {defender.name} absorbs {defender.mana.current} damage.")
                            damage -= defender.mana.current
                            defender.mana.current = 0
                            defender.status_effects['Mana Shield'].active = False
                        else:
                            print(f"The mana shield around {defender.name} absorbs {damage} damage.")
                            defender.mana.current -= damage
                            damage = 0
                            hits[i] = False

                    if damage > 0:
                        damage = max(0, int((damage - dam_red) * (1 - resist)))
                        defender.health.current -= damage
                        if damage > 0:
                            print(f"{self.name} {typ} {defender.name} for {damage} damage.")
                            if sleep and not random.randint(0, 1):
                                    print(f"The attack awakens {defender.name}!")
                                    defender.status_effects['Sleep'].active = False
                                    defender.status_effects['Sleep'].duration = 0
                        else:
                            print(f"{self.name} {typ} {defender.name} but deals no damage.")
                            hits[i] = False
                    else:
                        print(f"{self.name} {typ} {defender.name} but deals no damage.")
                        hits[i] = False
                else:
                    print(f"{self.name} {typ} {defender.name} but misses entirely.")
                if i < (len(attacks) - 1):
                    time.sleep(0.5)

            if hits[i]:
                defender.equipment['Armor']().special_effect(defender, self)
                if defender.is_alive():
                    self.equipment[att]().special_effect(self, defender, damage=damage, crit=crits[i])

        return any(hits), max(crits)

    def is_alive(self):
        return self.health.current > 0

    def modify_inventory(self, item, num=0, subtract=False, rare=False):
        inventory = self.special_inventory if rare else self.inventory
        if subtract:
            inventory[item().name][1] -= num
            if inventory[item().name][1] == 0:
                del inventory[item().name]
        else:
            if item().name not in inventory:
                inventory[item().name] = [item, num]
            else:
                inventory[item().name][1] += num
        if rare:
            self.quests(item=item)

    def statuses(self, end=False):
        def default(status=None, end_combat=False):
            if end_combat:
                for key in self.status_effects.keys():
                    self.status_effects[key].active = False
                    self.status_effects[key].duration = 0
                    self.status_effects[key].extra = 0
            else:
                self.status_effects[status].active = False
                self.status_effects[status].duration = 0
                self.status_effects[status].extra = 0

        if end:
            default(end_combat=True)
        else:
            if self.status_effects['Prone'].active and all([not self.status_effects['Stun'].active,
                                                            not self.status_effects['Sleep'].active]):
                if not random.randint(0, self.status_effects['Prone'].duration):
                    default(status='Prone')
                    print(f"{self.name} is no longer prone.")
                else:
                    self.status_effects['Prone'].duration -= 1
                    print(f"{self.name} is still prone.")
            if self.status_effects['Disarm'].active and all([not self.status_effects['Stun'].active,
                                                            not self.status_effects['Sleep'].active]):
                self.status_effects['Disarm'].duration -= 1
                if self.status_effects['Disarm'].duration == 0:
                    print(f"{self.name} picks up their weapon.")
                    default(status='Disarm')
            if self.status_effects['Silence'].active:
                self.status_effects['Silence'].duration -= 1
                if self.status_effects['Silence'].duration == 0:
                    print(f"{self.name} is no longer silenced.")
                    default(status='Silence')
            if self.status_effects['Poison'].active:
                self.status_effects['Poison'].duration -= 1
                poison_damage = self.status_effects['Poison'].extra
                poison_damage -= random.randint(0, self.stats.con)
                if poison_damage > 0:
                    self.health.current -= poison_damage
                    print(f"The poison damages {self.name} for {poison_damage} health points.")
                else:
                    print(f"{self.name} resisted the poison.")
                if self.status_effects['Poison'].duration == 0:
                    default(status='Poison')
                    print(f"The poison has left {self.name}.")
            if self.status_effects['DOT'].active:
                self.status_effects['DOT'].duration -= 1
                dot_damage = self.status_effects['DOT'].extra
                dot_damage -= random.randint(0, self.stats.wisdom)
                if dot_damage > 0:
                    self.health.current -= dot_damage
                    print(f"The magic damages {self.name} for {dot_damage} health points.")
                else:
                    print(f"{self.name} resisted the magic.")
                if self.status_effects['DOT'].duration == 0:
                    default(status='DOT')
                    print(f"The magic affecting {self.name} has worn off.")
            if self.status_effects['Bleed'].active:
                self.status_effects['Bleed'].duration -= 1
                bleed_damage = self.status_effects['Bleed'].extra
                bleed_damage -= random.randint(0, self.stats.con)
                if bleed_damage > 0:
                    self.health.current -= bleed_damage
                    print(f"The bleed damages {self.name} for {bleed_damage} health points.")
                else:
                    print(f"{self.name} resisted the bleed.")
                if self.status_effects['Bleed'].duration == 0:
                    default(status='Bleed')
                    print(f"{self.name}'s wounds have healed and is no longer bleeding.")
            if self.status_effects['Regen'].active:
                self.status_effects['Regen'].duration -= 1
                heal = self.status_effects['Regen'].extra
                heal = min(heal, self.health.max - self.health.current)
                self.health.current += heal
                print(f"{self.name}'s health has regenerated by {heal}.")
                if self.status_effects['Regen'].duration == 0:
                    print("Regeneration spell ends.")
                    default(status='Regen')
            if self.status_effects['Blind'].active:
                self.status_effects['Blind'].duration -= 1
                if self.status_effects['Blind'].duration == 0:
                    print(f"{self.name} is no longer blind.")
                    default(status='Blind')
            if self.status_effects['Stun'].active:
                self.status_effects['Stun'].duration -= 1
                if self.status_effects['Stun'].duration == 0:
                    print(f"{self.name} is no longer stunned.")
                    default(status='Stun')
            if self.status_effects['Sleep'].active:
                self.status_effects['Sleep'].duration -= 1
                if self.status_effects['Sleep'].duration == 0:
                    print(f"{self.name} is no longer asleep.")
                    default(status='Sleep')
            if self.status_effects['Reflect'].active:
                self.status_effects['Reflect'].duration -= 1
                if self.status_effects['Reflect'].duration == 0:
                    print(f"{self.name} is no longer reflecting magic.")
                    default(status='Reflect')
            for stat in ['Attack', 'Defense', 'Magic', 'Magic Defense']:
                if self.status_effects[stat].active:
                    self.status_effects[stat].duration -= 1
                    if self.status_effects[stat].duration == 0:
                        default(status=stat)
            if self.status_effects['Doom'].active:
                self.status_effects['Doom'].duration -= 1
                if self.status_effects['Doom'].duration == 0:
                    print(f"The Doom countdown has expired and so has {self.name}!")
                    self.health.current = 0

    def special_effects(self, target):
        pass

    def familiar_turn(self, target):
        pass
