##########################################
""" character manager """

# Imports
import random
from math import exp
from dataclasses import dataclass


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
        self.status_effects={"Prone": StatusEffect(False, 0),
                             "Silence": StatusEffect(False, 0),
                             "Stun": StatusEffect(False, 0),
                             "Doom": StatusEffect(False, 0),
                             "Blind": StatusEffect(False, 0),
                             "Disarm": StatusEffect(False, 0),
                             "Sleep": StatusEffect(False, 0),
                             "Poison": StatusEffect(False, 0, 0),
                             "DOT": StatusEffect(False, 0, 0),
                             "Bleed": StatusEffect(False, 0, 0),
                             "Berserk": StatusEffect(False, 0),
                             "Attack": StatusEffect(False, 0, 0),
                             "Defense": StatusEffect(False, 0, 0),
                             "Magic": StatusEffect(False, 0, 0),
                             "Magic Defense": StatusEffect(False, 0, 0),
                            #  "Resist": StatusEffect(False, 0, 0),
                             "Regen": StatusEffect(False, 0, 0),
                             "Reflect": StatusEffect(False, 0),
                             "Mana Shield": StatusEffect(False, 0),
                             "Duplicates": StatusEffect(False, 0),
                             "Power Up": StatusEffect(False, 0, 0)}
        self.resistance = {'Fire': 0.,
                           'Ice': 0.,
                           'Electric': 0.,
                           'Water': 0.,
                           'Earth': 0.,
                           'Wind': 0.,
                           'Shadow': 0.,
                           'Holy': 0.,
                           'Poison': 0.,
                           'Death': 0.,
                           'Stone': 0.,
                           'Physical': 0.}
        self.flying = False
        self.invisible = False
        self.sight = False

    def incapacitated(self):
        return any([self.status_effects["Sleep"].active,
                    self.status_effects["Prone"].active,
                    self.status_effects["Stun"].active])

    def hit_chance(self, defender, typ='weapon'):
        """
        Calculate hit chance based on various factors.

        Things that affect hit chance
            Weapon attack: whether char is blind, if enemy is flying and/or invisible, enemy status effects,
                accessory bonuses, difference in pro level
            Spell attack: enemy status effects
        """

        hit_mod = sigmoid(random.randint(self.stats.dex // 2, self.stats.dex) /
                          random.randint(defender.stats.dex // 4, defender.stats.dex // 2))  # base hit percentage
        if typ == 'weapon':
            hit_mod *= 1 + (0.25 * ('Accuracy' in self.equipment['Ring'].mod))  # accuracy adds 25% chance to hit
            hit_mod *= 1 - (0.5 * self.status_effects['Blind'].active)  # blind lowers accuracy by 50%
            hit_mod *= 1 - (1 / 10) * defender.flying  # flying lowers accuracy by 10%
            hit_mod *= 1 - (0.25 * (self.status_effects['Disarm'].active))
        hit_mod += 0.05 * (self.level.pro_level - defender.level.pro_level)  # makes it easier to hit lower level creatures
        hit_mod *= 1 - (1 / 3) * defender.invisible  # invisible lowers accuracy by 33.3%
        if hasattr(self, "encumbered"):
            if self.encumbered:
                hit_mod *= 0.75  # lower hit chance by 75% if encumbered
        return max(0, hit_mod)

    def dodge_chance(self, attacker):
        armor_factor = {"None": 1, "Natural": 1, "Cloth": 1, "Light": 2, "Medium": 3, "Heavy": 4}
        a_chance = random.randint(attacker.stats.dex // 4, attacker.stats.dex) + \
            attacker.check_mod('luck', enemy=self, luck_factor=10)
        d_chance = random.randint(0, self.stats.dex) + self.check_mod('luck', enemy=attacker, luck_factor=15)
        chance = (d_chance - a_chance) / (a_chance + d_chance) / armor_factor[self.equipment['Armor'].subtyp]
        chance += 0.1 * ('Dodge' in self.equipment['Ring'].mod + "Evasion" in self.spellbook['Skills'])
        if self.cls.name == "Seeker" or (self.cls.name == "Templar" and self.status_effects['Power Up'].active):
            chance += (0.25 * self.power_up)
        if hasattr(self, "encumbered"):
            if self.encumbered:
                chance /= 2  # lower dodge chance by half if encumbered
        return max(0, chance)
    
    def critical_chance(self, att):
        base_crit = 0.005 * (self.stats.dex + self.check_mod("luck", luck_factor=10))
        crit_chance = self.equipment[att].crit + base_crit
        if self.cls.name == "Seeker":
            crit_chance += (0.1 * self.power_up)
        return crit_chance

    def weapon_damage(self, defender, dmg_mod=1.0, crit=1, ignore=False, cover=False, hit=False):
        """
        Function that controls melee attacks during combat
        defender(Character): the target of the attack
        dmg_mod(float): a percentage value that modifies the amount of damage done
        crit(int): the damage multiplier for a critical hit
        ignore(bool): whether the attack ignores the target's defenses
        cover(bool): whether the attack can be blocked by a familiar or pet
        hit(bool): guarantees hit if target doesn't dodge
        """

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
            dmg = random.randint(dmg // 2, dmg)
            crit_per = random.uniform(1, crits[i])
            damage = max(0, dmg * crit_per)

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
                if hits[i] and defender.status_effects["Duplicates"].active:
                    if random.randint(0, defender.status_effects["Duplicates"].duration):
                        hits[i] = False
                        use_str += (f"{self.name} {typ} at {defender.name} but hits a mirror image and it "
                                    f"vanishes from existence.\n")
                        defender.status_effects["Duplicates"].duration -= 1
                        if not defender.status_effects["Duplicates"].duration:
                            defender.status_effects["Duplicates"].active = False
                if hits[i]:
                    if crits[i] > 1:
                        weapon_dam_str += "Critical hit!\n"
                    if cover:
                        weapon_dam_str += (f"{defender.familiar.name} steps in front of the attack, "
                                           f"taking the damage for {defender.name}.\n")
                        damage = 0
                    elif ((defender.equipment['OffHand'].subtyp == 'Shield' or
                           'Dodge' in defender.equipment['Ring'].mod) and
                          not defender.status_effects['Mana Shield'].active and \
                            not (defender.cls.name == "Crusader" and defender.power_up and 
                                 defender.status_effects['Power Up'].active)) and not defender.incapacitated():
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
                    elif defender.status_effects['Mana Shield'].active:
                        mana_loss = damage // defender.status_effects['Mana Shield'].duration
                        if mana_loss > defender.mana.current:
                            abs_dam = defender.mana.current * defender.status_effects['Mana Shield'].duration
                            weapon_dam_str += f"The mana shield around {defender.name} absorbs {abs_dam} damage.\n"
                            damage -= abs_dam
                            defender.mana.current = 0
                            defender.status_effects['Mana Shield'].active = False
                            weapon_dam_str += f"The mana shield dissolves around {defender.name}.\n"
                        else:
                            weapon_dam_str += f"The mana shield around {defender.name} absorbs {damage} damage.\n"
                            defender.mana.current -= mana_loss
                            damage = 0
                            hits[i] = False
                    elif defender.cls.name == "Crusader" and defender.power_up and defender.status_effects['Power Up'].active:
                        if damage >= defender.status_effects['Power Up'].extra:
                            weapon_dam_str += (f"The shield around {defender.name} absorbs "
                                       f"{defender.status_effects['Power Up'].extra} damage.\n")
                            damage -= defender.status_effects['Power Up'].extra
                            defender.status_effects['Power Up'].active = False
                            weapon_dam_str += f"The shield dissolves around {defender.name}.\n"
                        else:
                            weapon_dam_str += f"The shield around {defender.name} absorbs {damage} damage.\n"
                            defender.status_effects['Power Up'].extra -= damage
                            damage = 0
                            hits[i] = False
                    elif defender.cls.name == "Templar" and defender.power_up and defender.status_effects['Power Up'].active:
                        ref_dam = int(0.25 * damage)
                        damage -= ref_dam
                        self.health.current -= ref_dam
                        weapon_dam_str += f"{ref_dam} is reflected back at {self.name}.\n"
                    if damage > 0:
                        e_resist = 0
                        if self.equipment[att].element:
                            e_resist = defender.check_mod('resist', enemy=self, typ=self.equipment[att].element)
                        p_resist = defender.check_mod('resist', enemy=self, typ='Physical', ultimate=self.equipment[att].ultimate)
                        dam_red = defender.check_mod('armor', enemy=self, ignore=ignore)
                        dam_red = random.randint(dam_red // 2, dam_red)
                        damage = max(0, int((damage - dam_red) * (1 - p_resist) * (1 - e_resist)))
                        defender.health.current -= damage
                        if damage > 0:
                            weapon_dam_str += f"{self.name} {typ} {defender.name} for {damage} damage.\n"
                            if defender.status_effects["Sleep"].active and \
                                not random.randint(0, defender.status_effects['Sleep'].duration):
                                    weapon_dam_str += f"The attack awakens {defender.name}!\n"
                                    defender.status_effects['Sleep'].active = False
                                    defender.status_effects['Sleep'].duration = 0
                            if self.cls.name in "Ninja" and self.power_up:
                                dam_abs = self.status_effects['Power Up'].active * damage
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
                if defender.is_alive() and damage > 0 and not defender.status_effects["Mana Shield"].active:
                    weapon_dam_str += self.equipment[att].special_effect(self, defender, damage=damage, crit=crits[i])
                if self.cls.name == "Dragoon" and self.power_up:
                    self.status_effects['Power Up'].active = True
                    self.status_effects['Power Up'].duration += 1
            else:
                if self.cls.name == "Dragoon" and self.power_up:
                    self.status_effects['Power Up'].active = False
                    self.status_effects['Power Up'].duration = 0    

        return weapon_dam_str, any(hits), max(crits)

    def flee(self, enemy, smoke=False):
        stun = enemy.status_effects['Stun'].active
        success = False
        flee_message = f"{self.name} couldn't escape from the {enemy.name}."
        if smoke:
            if not enemy.sight or self.invisible:
                flee_message = f"{self.name} disappears in a cloud of smoke."
                self.state = 'normal'
                success = True
            else:
                flee_message = f"{enemy.name} is not fooled by cheap parlor tricks."
        chance = self.check_mod('luck', enemy=enemy, luck_factor=10)
        if random.randint(self.stats.dex // 2, self.stats.dex) + chance > \
                random.randint(enemy.stats.dex // 2, enemy.stats.dex) or stun:
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

    def statuses(self, end=False):
        """
        Silence, Blind, and Disarm are indefinite unless cured
        """

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
            status_text = ""
            if self.status_effects['Prone'].active and all([not self.status_effects['Stun'].active,
                                                            not self.status_effects['Sleep'].active]):
                if not random.randint(0, self.status_effects['Prone'].duration):
                    default(status='Prone')
                    status_text += f"{self.name} is no longer prone.\n"
                else:
                    self.status_effects['Prone'].duration -= 1
                    status_text += f"{self.name} is still prone.\n"
            if self.status_effects['Poison'].active:
                self.status_effects['Poison'].duration -= 1
                poison_damage = self.status_effects['Poison'].extra
                poison_damage -= random.randint(0, self.stats.con // 4)
                if poison_damage > 0:
                    self.health.current -= poison_damage
                    status_text += f"The poison damages {self.name} for {poison_damage} health points.\n"
                else:
                    status_text += f"{self.name} resisted the poison.\n"
                if self.status_effects['Poison'].duration == 0:
                    default(status='Poison')
                    status_text += f"The poison has left {self.name}.\n"
            if self.status_effects['DOT'].active:
                self.status_effects['DOT'].duration -= 1
                dot_damage = self.status_effects['DOT'].extra
                dot_damage -= random.randint(0, self.stats.wisdom)
                if dot_damage > 0:
                    self.health.current -= dot_damage
                    status_text += f"The magic damages {self.name} for {dot_damage} health points.\n"
                else:
                    status_text += f"{self.name} resisted the magic.\n"
                if self.status_effects['DOT'].duration == 0:
                    default(status='DOT')
                    status_text += f"The magic affecting {self.name} has worn off.\n"
            if self.status_effects['Bleed'].active:
                self.status_effects['Bleed'].duration -= 1
                bleed_damage = self.status_effects['Bleed'].extra
                bleed_damage -= random.randint(0, self.stats.con)
                if bleed_damage > 0:
                    self.health.current -= bleed_damage
                    status_text += f"The bleed damages {self.name} for {bleed_damage} health points.\n"
                else:
                    status_text += f"{self.name} resisted the bleed.\n"
                if self.status_effects['Bleed'].duration == 0:
                    default(status='Bleed')
                    status_text += f"{self.name}'s wounds have healed and is no longer bleeding.\n"
            if self.status_effects['Regen'].active:
                self.status_effects['Regen'].duration -= 1
                heal = self.status_effects['Regen'].extra
                heal = min(heal, self.health.max - self.health.current)
                self.health.current += heal
                status_text += f"{self.name}'s health has regenerated by {heal}.\n"
                if self.status_effects['Regen'].duration == 0:
                    status_text += "Regeneration spell ends.\n"
                    default(status='Regen')
            if self.status_effects['Blind'].active:
                self.status_effects['Blind'].duration -= 1
                if self.status_effects['Blind'].duration == 0:
                    status_text += f"{self.name} is no longer blind.\n"
                    default(status='Blind')
            if self.status_effects['Stun'].active:
                self.status_effects['Stun'].duration -= 1
                if self.status_effects['Stun'].duration == 0:
                    status_text += f"{self.name} is no longer stunned.\n"
                    default(status='Stun')
            if self.status_effects['Sleep'].active:
                self.status_effects['Sleep'].duration -= 1
                if self.status_effects['Sleep'].duration == 0:
                    status_text += f"{self.name} is no longer asleep.\n"
                    default(status='Sleep')
            if self.status_effects['Reflect'].active:
                self.status_effects['Reflect'].duration -= 1
                if self.status_effects['Reflect'].duration == 0:
                    status_text += f"{self.name} is no longer reflecting magic.\n"
                    default(status='Reflect')
            for stat in ['Attack', 'Defense', 'Magic', 'Magic Defense']:
                if self.status_effects[stat].active:
                    self.status_effects[stat].duration -= 1
                    if self.status_effects[stat].duration == 0:
                        default(status=stat)
            if self.status_effects['Power Up'].active:
                if self.cls.name == "Lycan":
                    self.status_effects['Power Up'].duration += 1
                elif self.cls.name == "Dragoon":
                    pass
                else:
                    self.status_effects['Power Up'].duration -= 1
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
                if self.status_effects['Power Up'].duration == 0:
                    if self.cls.name == "Crusader" and self.power_up:
                        status_text += (f"The shield around {self.name} explodes, dealing "
                                        f"{self.status_effects['Power Up'].extra} damage to the enemy.\n")
                    default(status='Power Up')
            if self.status_effects['Berserk'].active:
                self.status_effects['Berserk'].duration -= 1
                if self.status_effects['Berserk'].duration == 0:
                    status_text += f"{self.name} has regained their composure.\n"
                    default(status="Berserk")
            if self.status_effects['Doom'].active:
                self.status_effects['Doom'].duration -= 1
                if self.status_effects['Doom'].duration == 0:
                    status_text += f"The Doom countdown has expired and so has {self.name}!\n"
                    self.health.current = 0
            return status_text

    def special_effects(self, target):
        special_str = ""
        return special_str

    def familiar_turn(self, target):
        familiar_str = ""
        return familiar_str
