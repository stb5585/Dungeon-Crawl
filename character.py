##########################################
""" character manager """

# Imports
import random
from math import exp
from dataclasses import dataclass
from typing import Tuple


# functions
def sigmoid(x):
    return 1 / (1 + exp(-x))


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
class Combat:
    """
    Combat Stats:
        attack: base attack stat for calculating melee damage
        defense: base defense stat for calculating damage reduction
        magic: base stat for calculating magic damage
        magic_def: base stat for calculating magic damage reduction
    """
    attack: int = 0
    defense: int = 0
    magic: int = 0
    magic_def: int = 0

@dataclass
class Resource:
    max: int = 0
    current: int = 0

@dataclass
class Level:
    level: int = 1
    pro_level: int = 1
    exp: int = 0
    exp_to_gain: int = 25

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
        level (Level): A dataclass containing the level, promotion level, experience, and experience to gain of the character.
        health (Resource): A dataclass containing the maximum and current health of the character.
        mana (Resource): A dataclass containing the maximum and current mana of the character.
        stats (Stats): A dataclass containing the 6 primary statistics of the character.
        combat (Combat): A dataclass containing the 4 primary combat stats of the character.
        gold (int): how much gold the character possesses
        equipment (Dict[str, object]): A dictionary containing the items which the character is currently equipped. 
        inventory (Dict[str, List[object, int]]): A dictionary containing the character's inventory, including the item
            and quantity.
        special_inventory (Dict[str, List[object, int]]): A dictionary containing the character's special inventory, 
            including the item and quantity. The special inventory stores items that are related to quests or the plot
            of the story.
        spellbook (Dict[str, Dict[str, Spell]]): A dictionary containing the spells and skills learned for the
            character to use.
        status_effects (Dict[str, StatusEffect]): A dictionary containing the character's status effects.
        status_immunity (List[str]): A list of all status effects the character is immune against.
        resistance (Dict[str, float]): A dictionary containing the elemental impact on the character.
        flying (bool): A boolean variable indicating whether the character is flying or not. Flying affects chance
            to hit and some elemental effect.
        invisible (bool): A boolean variable indicating whether the character is invisible or not. Invisibility
            affects chance to hit.
    Methods:
        __init__():
            Initializes a Character object.
        
        effects(end=False):
            Manages and updates the character's effects, applying their respective consequences/benefits
            and handling the end of combat.
    """


    def __init__(self, name: str, health: Resource, mana: Resource, stats: Stats, combat: Combat):
        self.name = name
        self.race = None
        self.cls = None
        self.level = Level(1, 1, 0, 0)
        self.health = health
        self.mana = mana
        self.stats = stats
        self.combat = combat
        self.gold = 0
        self.equipment = {}
        self.inventory = {}
        self.spellbook = {'Spells': {},
                          'Skills': {}}
        self.status_effects = {"Berserk": StatusEffect(False, 0),
                               "Blind": StatusEffect(False, 0),
                               "Doom": StatusEffect(False, 0),
                               "Poison": StatusEffect(False, 0, 0),
                               "Silence": StatusEffect(False, 0),
                               "Sleep": StatusEffect(False, 0),
                               "Stun": StatusEffect(False, 0)}
        self.physical_effects = {"Bleed": StatusEffect(False, 0, 0),
                                 "Disarm": StatusEffect(False, 0),
                                 "Prone": StatusEffect(False, 0)}
        self.stat_effects = {"Attack": StatusEffect(False, 0, 0),
                             "Defense": StatusEffect(False, 0, 0),
                             "Magic": StatusEffect(False, 0, 0),
                             "Magic Defense": StatusEffect(False, 0, 0),
                             "Speed": StatusEffect(False, 0, 0)}
        self.magic_effects = {"DOT": StatusEffect(False, 0, 0),
                              "Duplicates": StatusEffect(False, 0),
                              "Ice Block": StatusEffect(False, 0),
                              "Mana Shield": StatusEffect(False, 0),
                              "Reflect": StatusEffect(False, 0),
                              "Regen": StatusEffect(False, 0, 0),
                              "Resist Fire": StatusEffect(False, 0, 0),
                              "Resist Ice": StatusEffect(False, 0, 0),
                              "Resist Electric": StatusEffect(False, 0, 0),
                              "Resist Water": StatusEffect(False, 0, 0),
                              "Resist Earth": StatusEffect(False, 0, 0),
                              "Resist Wind": StatusEffect(False, 0, 0)}
        self.class_effects = {"Jump": StatusEffect(False, 0),
                              "Power Up": StatusEffect(False, 0, 0)}
        self.status_immunity = []
        self.resistance = {'Fire': 0.,
                           'Ice': 0.,
                           'Electric': 0.,
                           'Water': 0.,
                           'Earth': 0.,
                           'Wind': 0.,
                           'Shadow': 0.,
                           'Holy': 0.,
                           "Poison": 0.,
                           'Physical': 0.}
        self.flying = False
        self.invisible = False
        self.sight = False
        self.turtle = False
        self.tunnel = False

    def incapacitated(self):
        return any([self.status_effects["Sleep"].active,
                    self.physical_effects["Prone"].active,
                    self.status_effects["Stun"].active])

    def effect_handler(self, effect):
        if effect in self.status_effects:
            return self.status_effects
        if effect in self.physical_effects:
            return self.physical_effects
        if effect in self.stat_effects:
            return self.stat_effects
        if effect in self.magic_effects:
            return self.magic_effects
        raise NotImplementedError(f"{effect} does not exist in character attributes.")

    def hit_chance(self, defender, typ='weapon'):
        """
        Calculate hit chance based on various factors.

        Things that affect hit chance
            Weapon attack: whether char is blind, if enemy is flying and/or invisible, enemy status effects,
                accessory bonuses, difference in pro level
            Spell attack: enemy status effects
        """

        hit_mod = sigmoid(random.randint(self.check_mod("speed", enemy=defender) // 2,
                                         self.check_mod("speed", enemy=defender)) /
                          random.randint(defender.check_mod("speed", enemy=defender) // 4,
                                         defender.check_mod("speed", enemy=defender) // 2))  # base hit percentage
        if typ == 'weapon':
            hit_mod *= 1 + (0.25 * ('Accuracy' in self.equipment['Ring'].mod))  # accuracy adds 25% chance to hit
            hit_mod *= 1 - (0.5 * self.status_effects["Blind"].active)  # blind lowers accuracy by 50%
            hit_mod *= 1 - (1 / 10) * defender.flying  # flying lowers accuracy by 10%
            hit_mod *= 1 - (0.25 * (self.physical_effects["Disarm"].active))
        hit_mod += 0.05 * (self.level.pro_level - defender.level.pro_level)  # makes it easier to hit lower level creatures
        hit_mod *= 1 - (1 / 3) * defender.invisible  # invisible lowers accuracy by 33.3%
        if hasattr(self, "encumbered"):
            if self.encumbered:
                hit_mod *= 0.75  # lower hit chance by 75% if encumbered
        return max(0, hit_mod)

    def dodge_chance(self, attacker, spell=False):
        a_stat = attacker.check_mod("speed", enemy=self)
        d_stat = self.check_mod("speed", enemy=attacker)
        if spell:
            a_stat = attacker.stats.intel
            d_stat = self.stats.wisdom
        armor_factor = {"None": 1, "Natural": 1, "Cloth": 1, "Light": 2, "Medium": 3, "Heavy": 4}
        a_chance = random.randint(a_stat // 2, a_stat) + \
            attacker.check_mod('luck', enemy=self, luck_factor=10)
        d_chance = random.randint(0, d_stat // 2) + self.check_mod('luck', enemy=attacker, luck_factor=15) + \
            (self.stat_effects["Speed"].active * self.stat_effects["Speed"].extra)
        chance = max(0, (d_chance - a_chance) / (a_chance + d_chance) / armor_factor[self.equipment['Armor'].subtyp])
        chance += 0.1 * ('Dodge' in self.equipment['Ring'].mod + "Evasion" in self.spellbook['Skills'])
        if self.cls.name == "Seeker" or (self.cls.name == "Templar" and self.class_effects["Power Up"].active):
            chance += (0.25 * self.power_up)
        if hasattr(self, "encumbered"):
            if self.encumbered:
                chance /= 2  # lower dodge chance by half if encumbered
        return min(0.75, chance)  # max of 75%
    
    def critical_chance(self, att):
        base_crit = 0.005 * (self.check_mod("speed") + self.check_mod("luck", luck_factor=10))
        crit_chance = self.equipment[att].crit + base_crit
        if self.cls.name == "Seeker":
            crit_chance += (0.1 * self.power_up)
        return crit_chance

    def weapon_damage(self, defender, dmg_mod=1.0, crit=1, ignore=False, cover=False, hit=False) -> Tuple[str, bool, int]:
        """
        Function that controls melee attacks during combat
        defender(Character): the target of the attack
        dmg_mod(float): a percentage value that modifies the amount of damage done
        crit(int): the damage multiplier for a critical hit
        ignore(bool): whether the attack ignores the target's defenses
        cover(bool): whether the attack can be blocked by a familiar or pet
        hit(bool): guarantees hit if target doesn't dodge
        """

        if defender.magic_effects["Ice Block"].active:
            return "Your attack has no effect.\n", False, crit
        hits = []  # indicates if the attack was successful for means of ability/weapon affects
        crits = []
        attacks = ['Weapon']
        if self.equipment['OffHand'].typ == 'Weapon':
            attacks.append('OffHand')
        weapon_dam_str = ""
        for i, att in enumerate(attacks):
            hits.append(hit)
            crits.append(1)
            ignore = ignore or self.equipment[att].ignore
            dodge = False
            # attacker variables
            typ = 'attacks'
            if self.equipment[att].subtyp == 'Natural':
                typ = self.equipment[att].att_name
                if typ == 'leers':
                    hits[i] = True
                    weapon_dam_str += self.equipment[att].special_effect(self, defender)
                    break
            crits[i] = 2 if crit == 1 and self.critical_chance(att) > random.random() else crit
            dmg = max(1, int(dmg_mod * self.check_mod(att.lower(), enemy=defender)))
            crit_per = random.uniform(1, crits[i])
            damage = max(0, int(dmg * crit_per))

            # defender variables
            if not hit:
                dodge = defender.dodge_chance(self) > random.random()
                hit_per = self.hit_chance(defender, typ='weapon')
                hits[i] = hit_per > random.random()
            if defender.incapacitated():
                dodge = False
                hits[i] = True

            # combat
            if dodge:
                hits[i] = False
                if 'Parry' in defender.spellbook['Skills']:
                    weapon_dam_str += f"{defender.name} parries {self.name}'s attack and counterattacks!\n"
                    counter_str, _, _ = defender.weapon_damage(self)
                    weapon_dam_str += counter_str
                    if not self.is_alive():
                        return weapon_dam_str, any(hits), max(crits)
                else:
                    weapon_dam_str += f"{defender.name} evades {self.name}'s attack.\n"
            else:
                if hits[i] and defender.magic_effects["Duplicates"].active:
                    if random.randint(0, defender.magic_effects["Duplicates"].duration):
                        hits[i] = False
                        weapon_dam_str += (f"{self.name} {typ} at {defender.name} but hits a mirror image and it "
                                           f"vanishes from existence.\n")
                        defender.magic_effects["Duplicates"].duration -= 1
                        if not defender.magic_effects["Duplicates"].duration:
                            defender.magic_effects["Duplicates"].active = False
                if hits[i]:
                    if crits[i] > 1:
                        weapon_dam_str += "Critical hit!\n"
                    if cover:
                        weapon_dam_str += (f"{defender.familiar.name} steps in front of the attack, "
                                           f"taking the damage for {defender.name}.\n")
                        damage = 0
                    elif ((defender.equipment['OffHand'].subtyp == 'Shield' or
                           'Dodge' in defender.equipment['Ring'].mod) and
                          not defender.magic_effects["Mana Shield"].active and \
                            not (defender.cls.name == "Crusader" and defender.power_up and 
                                 defender.class_effects["Power Up"].active)) and not defender.incapacitated():
                        blk_chance = defender.check_mod('shield', enemy=self) / 100
                        if blk_chance > random.random():
                            blk_per = blk_chance + ((defender.stats.strength - self.stats.strength) / damage)
                            if 'Shield Block' in defender.spellbook['Skills']:
                                blk_per *= 1.25
                            if blk_per > 0:
                                blk_per = min(1, blk_per)
                                damage *= (1 - blk_per)
                                damage = int(damage)
                                weapon_dam_str += (f"{defender.name} blocks {self.name}'s attack and mitigates "
                                                   f"{round(blk_per * 100)} percent of the damage.\n")
                    elif defender.magic_effects["Mana Shield"].active:
                        mana_loss = damage // defender.magic_effects["Mana Shield"].duration
                        if mana_loss > defender.mana.current:
                            abs_dam = defender.mana.current * defender.magic_effects["Mana Shield"].duration
                            weapon_dam_str += f"The mana shield around {defender.name} absorbs {abs_dam} damage.\n"
                            damage -= abs_dam
                            defender.mana.current = 0
                            defender.magic_effects["Mana Shield"].active = False
                            weapon_dam_str += f"The mana shield dissolves around {defender.name}.\n"
                        else:
                            weapon_dam_str += f"The mana shield around {defender.name} absorbs {damage} damage.\n"
                            defender.mana.current -= mana_loss
                            damage = 0
                            hits[i] = False
                    elif defender.cls.name == "Crusader" and defender.power_up and \
                        defender.class_effects["Power Up"].active:
                        if damage >= defender.class_effects["Power Up"].extra:
                            weapon_dam_str += (f"The shield around {defender.name} absorbs "
                                       f"{defender.class_effects['Power Up'].extra} damage.\n")
                            damage -= defender.class_effects["Power Up"].extra
                            defender.class_effects["Power Up"].active = False
                            weapon_dam_str += f"The shield dissolves around {defender.name}.\n"
                        else:
                            weapon_dam_str += f"The shield around {defender.name} absorbs {damage} damage.\n"
                            defender.class_effects["Power Up"].extra -= damage
                            damage = 0
                            hits[i] = False
                    elif defender.cls.name == "Templar" and defender.power_up and \
                        defender.class_effects["Power Up"].active:
                        ref_dam = int(0.25 * damage)
                        damage -= ref_dam
                        self.health.current -= ref_dam
                        weapon_dam_str += f"{ref_dam} is reflected back at {self.name}.\n"
                    if damage > 0:
                        e_resist = 0
                        if self.equipment[att].element:
                            e_resist = defender.check_mod('resist', enemy=self, typ=self.equipment[att].element)
                        p_resist = defender.check_mod('resist', enemy=self, typ='Physical',
                                                      ultimate=self.equipment[att].ultimate)
                        dam_red = defender.check_mod('armor', enemy=self, ignore=ignore)
                        damage = max(0, int(damage * (1 - p_resist) * (1 - e_resist) * (1 - (dam_red / (dam_red + 50)))))
                        variance = random.uniform(0.85, 1.15)
                        damage = int(damage * variance)
                        defender.health.current -= damage
                        if damage > 0:
                            weapon_dam_str += f"{self.name} {typ} {defender.name} for {damage} damage.\n"
                            if defender.status_effects["Sleep"].active and \
                                not random.randint(0, defender.status_effects["Sleep"].duration):
                                    weapon_dam_str += f"The attack awakens {defender.name}!\n"
                                    defender.status_effects["Sleep"].active = False
                                    defender.status_effects["Sleep"].duration = 0
                            if self.cls.name in "Ninja" and self.power_up:
                                dam_abs = self.class_effects["Power Up"].active * damage
                                self.health.current += dam_abs
                                weapon_dam_str += f"{self.name} absorbs {dam_abs} from {defender.name}.\n"
                            if self.cls.name in "Lycan" and self.power_up:
                                dam_abs = damage // 2
                                self.health.current += dam_abs
                                if dam_abs > 0:
                                    weapon_dam_str += f"{self.name} absorbs {dam_abs} from {defender.name}.\n"
                        else:
                            weapon_dam_str += f"{self.name} {typ} {defender.name} but deals no damage.\n"
                            hits[i] = False
                    else:
                        weapon_dam_str += f"{self.name} {typ} {defender.name} but deals no damage.\n"
                        hits[i] = False
                else:
                    weapon_dam_str += f"{self.name} {typ} {defender.name} but misses entirely.\n"
            if hits[i]:
                weapon_dam_str += defender.equipment['Armor'].special_effect(defender, self)
                if defender.is_alive() and damage > 0 and not defender.magic_effects["Mana Shield"].active:
                    weapon_dam_str += self.equipment[att].special_effect(self, defender, damage=damage, crit=crits[i])
                if self.cls.name == "Dragoon" and self.power_up:
                    self.class_effects["Power Up"].active = True
                    self.class_effects["Power Up"].duration += 1
            else:
                if self.cls.name == "Dragoon" and self.power_up:
                    self.class_effects["Power Up"].active = False
                    self.class_effects["Power Up"].duration = 0    

        return weapon_dam_str, any(hits), max(crits)

    def flee(self, enemy, smoke=False):
        blind = enemy.status_effects["Blind"].active
        success = False
        flee_message = f"{self.name} couldn't escape from the {enemy.name}."
        if smoke:
            if not enemy.sight or self.invisible:
                flee_message = f"{self.name} disappears in a cloud of smoke."
                self.state = 'normal'
                success = True
            else:
                flee_message = f"{enemy.name} is not fooled by cheap parlor tricks."
        else:
            chance = (self.check_mod('luck', enemy=enemy, luck_factor=10) + \
                (self.stat_effects["Speed"].active * self.stat_effects["Speed"].extra))
            chance = (chance / 100) + 0.2  # base 20% + chance
            speed_factor = (self.check_mod("speed", enemy=enemy) - enemy.check_mod("speed", enemy=enemy)) / \
                (self.check_mod("speed", enemy=enemy) + enemy.check_mod("speed", enemy=enemy) + 1)
            pro_diff = self.level.pro_level / max(enemy.level.pro_level, 1)
            flee_chance = min(0.95, chance + speed_factor * pro_diff)  # capped at 95%
            if random.random() > flee_chance or enemy.incapacitated() or blind:
                flee_message = f"{self.name} flees from the {enemy.name}."
                self.state = 'normal'
                success = True
        return success, flee_message

    def is_alive(self):
        return self.health.current > 0

    def modify_inventory(self, item, num=1, subtract=False, rare=False, quest=False, storage=False):
        inventory = self.special_inventory if rare else self.inventory
        if subtract:
            for _ in range(num):
                inventory[item.name].pop(0)
                if storage:
                    if item.name not in self.storage:
                        self.storage[item.name] = []
                    self.storage[item.name].append(item)
            if not len(inventory[item.name]):
                del inventory[item.name]
        else:
            if item.name not in inventory:
                inventory[item.name] = []
            num = min(num, 99 - len(inventory[item.name]))
            for _ in range(num):
                inventory[item.name].append(item)
                if storage:
                    self.storage[item.name].pop(0)
                    if not len(self.storage[item.name]):
                        del self.storage[item.name]
        if quest:
            self.quests(item=item)

    def effects(self, end=False):
        """
        Silence, Blind, and Disarm can be indefinite unless cured (duration=-1)
        """

        effect_dicts = [self.status_effects, self.physical_effects, self.stat_effects, self.magic_effects]

        def default(effect=None, end_combat=False):
            if end_combat:
                for effect_dict in effect_dicts:
                    for effect in effect_dict.keys():
                        effect_dict[effect].active = False
                        effect_dict[effect].duration = 0
                        effect_dict[effect].extra = 0
            else:
                effect_dict = self.effect_handler(effect=effect)
                effect_dict[effect].active = False
                effect_dict[effect].duration = 0
                effect_dict[effect].extra = 0

        if end:
            default(end_combat=True)
        else:
            status_text = ""
            if self.status_effects["Doom"].active:
                self.status_effects["Doom"].duration -= 1
                if not self.status_effects["Doom"].duration:
                    status_text += f"The Doom countdown has expired and so has {self.name}!\n"
                    self.health.current = 0
                    return status_text
            if self.magic_effects["Ice Block"].active:
                self.magic_effects["Ice Block"].duration -= 1
                gain_perc = 0.10 * (1 + (self.stats.intel / 30))
                health_gain = min(self.health.max - self.health.current, int(self.health.current * gain_perc))
                self.health.current += health_gain
                mana_gain = min(self.mana.max - self.mana.current, int(self.mana.current * gain_perc))
                self.mana.current += mana_gain 
                status_text += f"{self.name} regens {health_gain} health and {mana_gain} mana."
                if not self.magic_effects["Ice Block"].duration:
                    status_text += f"The ice block around {self.name} melts."
                    default(effect="Ice Block")
                else:
                    return status_text
            if self.physical_effects["Prone"].active and all([not self.status_effects["Stun"].active,
                                                              not self.status_effects["Sleep"].active]):
                if not random.randint(0, self.physical_effects["Prone"].duration) or \
                    random.randint(0, self.check_mod("luck", luck_factor=10)):
                    default(effect="Prone")
                    status_text += f"{self.name} is no longer prone.\n"
                else:
                    self.physical_effects["Prone"].duration -= 1
                    status_text += f"{self.name} is still prone.\n"
            if self.status_effects["Poison"].active:
                self.status_effects["Poison"].duration -= 1
                poison_damage = self.status_effects["Poison"].extra
                if not random.randint(0, self.stats.con // 10):
                    self.health.current -= poison_damage
                    status_text += f"The poison damages {self.name} for {poison_damage} health points.\n"
                else:
                    status_text += f"{self.name} resisted the poison.\n"
                if not self.status_effects["Poison"].duration:
                    default(effect="Poison")
                    status_text += f"The poison has left {self.name}.\n"
            if self.magic_effects["DOT"].active:
                self.magic_effects["DOT"].duration -= 1
                dot_damage = self.magic_effects["DOT"].extra
                if not random.randint(0, self.check_mod("magic def") // dot_damage):
                    self.health.current -= dot_damage
                    status_text += f"The magic damages {self.name} for {dot_damage} health points.\n"
                else:
                    status_text += f"{self.name} resisted the magic.\n"
                if not self.magic_effects["DOT"].duration:
                    default(effect="DOT")
                    status_text += f"The magic affecting {self.name} has worn off.\n"
            if self.physical_effects["Bleed"].active:
                self.physical_effects["Bleed"].duration -= 1
                bleed_damage = self.physical_effects["Bleed"].extra
                if not random.randint(0, self.stats.con // 10):
                    self.health.current -= bleed_damage
                    status_text += f"The bleed damages {self.name} for {bleed_damage} health points.\n"
                else:
                    status_text += f"{self.name} resisted the bleed.\n"
                if not self.physical_effects["Bleed"].duration:
                    default(effect="Bleed")
                    status_text += f"{self.name}'s wounds have healed and is no longer bleeding.\n"
            if self.status_effects["Blind"].active:
                self.status_effects["Blind"].duration -= 1
                if not self.status_effects["Blind"].duration:
                    status_text += f"{self.name} regains sight and is no longer blind.\n"
                    default(effect="Blind")
            if self.status_effects["Stun"].active:
                self.status_effects["Stun"].duration -= 1
                if not self.status_effects["Stun"].duration:
                    status_text += f"{self.name} is no longer stunned.\n"
                    default(effect="Stun")
            if self.status_effects["Sleep"].active:
                self.status_effects["Sleep"].duration -= 1
                if not self.status_effects["Sleep"].duration:
                    status_text += f"{self.name} is no longer asleep.\n"
                    default(effect="Sleep")
            if self.status_effects["Berserk"].active:
                self.status_effects["Berserk"].duration -= 1
                if not self.status_effects["Berserk"].duration:
                    status_text += f"{self.name} has regained their composure.\n"
                    default(effect="Berserk")
            if self.magic_effects["Reflect"].active:
                self.magic_effects["Reflect"].duration -= 1
                if not self.magic_effects["Reflect"].duration:
                    status_text += f"{self.name} is no longer reflecting magic.\n"
                    default(effect="Reflect")
            for stat in ["Attack", "Defense", "Magic", "Magic Defense", "Speed"]:
                if self.stat_effects[stat].active:
                    self.stat_effects[stat].duration -= 1
                    if not self.stat_effects[stat].duration:
                        # status_text += f"Bonus to {stat.lower()} for {self.name} has ended.\n"
                        default(effect=stat)
            if self.magic_effects["Regen"].active:
                self.magic_effects["Regen"].duration -= 1
                heal = self.magic_effects["Regen"].extra
                heal = min(heal, self.health.max - self.health.current)
                self.health.current += heal
                status_text += f"{self.name}'s health has regenerated by {heal}.\n"
                if not self.magic_effects["Regen"].duration:
                    status_text += "Regeneration spell ends.\n"
                    default(effect="Regen")
            if self.class_effects["Power Up"].active:
                if self.cls.name == "Lycan":
                    self.class_effects["Power Up"].duration += 1
                elif self.cls.name == "Dragoon":
                    pass
                else:
                    self.class_effects["Power Up"].duration -= 1
                if self.cls.name == "Knight Enchanter" and self.power_up:
                    mana_regen = int(self.mana.max * 0.25)
                    self.mana.current += mana_regen
                    status_text += f"{self.name} regens 25% of mana.\n"
                if self.cls.name == "Archbishop" and self.power_up:
                    health_regen = int(self.health.max * 0.10)
                    mana_regen = int(self.mana.max * 0.10)
                    self.health.current += health_regen
                    self.mana.current += mana_regen
                    status_text += f"{self.name} regens 10% of health and mana.\n"
                if not self.class_effects["Power Up"].duration:
                    if self.cls.name == "Crusader" and self.power_up:
                        status_text += (f"The shield around {self.name} explodes, dealing "
                                        f"{self.class_effects['Power Up'].extra} damage to the enemy.\n")
                    default(effect="Power Up")
            return status_text

    def special_effects(self, target):
        special_str = ""
        return special_str

    def familiar_turn(self, target):
        familiar_str = ""
        return familiar_str

    def check_mod(self, mod, enemy=None, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        if mod == 'weapon':
            weapon_mod = (self.equipment['Weapon'].damage * int(not self.physical_effects["Disarm"].active))
            weapon_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
            return max(0, weapon_mod + class_mod + self.combat.attack)
        if mod == 'shield':
            block_mod = 0
            if self.equipment['OffHand'].subtyp == 'Shield':
                block_mod = round(self.equipment['OffHand'].mod * (1 + ('Shield Block' in self.spellbook['Skills'])) * 100)
            if self.equipment['Ring'].mod == "Block":
                block_mod += 25
            return max(0, block_mod)
        if mod == 'offhand':
            try:
                off_mod = self.equipment['OffHand'].damage
                off_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
                return max(0, int((off_mod + class_mod + self.combat.attack) * 0.75))
            except AttributeError:
                return 0
        if mod == 'armor':
            armor_mod = self.equipment['Armor'].armor
            if self.turtle:
                class_mod += 99
            armor_mod += self.stat_effects["Defense"].extra * self.stat_effects["Defense"].active
            return max(0, (armor_mod * int(not ignore)) + class_mod + self.combat.defense)
        if mod == 'magic':
            magic_mod = int(self.stats.intel // 4) * self.level.pro_level
            if self.equipment['OffHand'].subtyp == 'Tome':
                magic_mod += self.equipment['OffHand'].mod
            if self.equipment['Weapon'].subtyp == 'Staff':
                magic_mod += int(self.equipment['Weapon'].damage * 0.75)
            magic_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            return max(0, magic_mod + class_mod + self.combat.magic)
        if mod == 'magic def':
            m_def_mod = self.stats.wisdom
            if self.turtle:
                class_mod += 99
            m_def_mod += self.stat_effects["Magic Defense"].extra * self.stat_effects["Magic Defense"].active
            return max(0, m_def_mod + class_mod + self.combat.magic_def)
        if mod == 'heal':
            heal_mod = self.stats.wisdom * self.level.pro_level
            if self.equipment['OffHand'].subtyp == 'Tome':
                heal_mod += self.equipment['OffHand'].mod
            elif self.equipment['Weapon'].subtyp == 'Staff':
                heal_mod += self.equipment['Weapon'].damage
            heal_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            return max(0, heal_mod + class_mod + self.combat.magic)
        if mod == 'resist':
            if ultimate and typ == 'Physical':  # ultimate weapons bypass Physical resistance
                return -0.25
            res_mod = self.resistance[typ]
            if self.flying:
                if typ == 'Earth':
                    res_mod = 1
                elif typ == 'Wind':
                    res_mod = -0.25
            return res_mod
        if mod == 'luck':
            luck_mod = self.stats.charisma // luck_factor
            return luck_mod
        if mod == "speed":
            speed_mod = self.stats.dex
            speed_mod += self.stat_effects["Speed"].extra * self.stat_effects["Speed"].active
            return speed_mod
        return 0

    def buff_str(self):
        buffs = []
        if self.equipment['Ring'].mod in ["Accuracy", "Dodge"]:
            buffs.append(self.equipment['Ring'].mod)
        if self.equipment['Pendant'].mod in \
            ["Vision", "Flying", "Invisible",
             "Status-Poison", "Status-Berserk", "Status-Stone", "Status-Silence", "Status-Death", "Status-All"]:
            buffs.append(self.equipment['Pendant'].mod)
        if self.flying and "Flying" not in buffs:
            buffs.append("Flying")
        if self.invisible and "Invisible" not in buffs:
            buffs.append("Invisible")
        if self.sight and "Vision" not in buffs:
            buffs.append("Vision")
        if not buffs:
            buffs.append("None")
        return ", ".join(buffs)

    def level_up(self):
        raise NotImplementedError

    def special_attack(self, target):
        raise NotImplementedError
