###########################################
""" enemy manager """

# Imports
import random
import time

import items
import spells


# Functions
def random_enemy(level):
    monsters = {'1': [Chest(), LockedChest(), GreenSlime(), Goblin(), GiantRat(), Bandit(), Skeleton(), GiantHornet(),
                      Zombie(), GiantSpider(), TwistedDwarf()],
                '2': [Chest(), LockedChest(), Gnoll(), Minotaur(), GiantOwl(), Orc(), Vampire(), Direwolf(), RedSlime(),
                      GiantSnake(), GiantScorpion(), Warrior(), Harpy(), Naga(), Wererat()],
                '3': [Chest(), LockedChest(), Warrior(), Pseudodragon(), Ghoul(), Troll(), Direbear(), EvilCrusader(),
                      Ogre(), BlackSlime(), GoldenEagle(), PitViper(), Alligator(), Disciple(), Werewolf()],
                '4': [Chest(), LockedChest(), Troll(), Direbear(), Cockatrice(), Gargoyle(), Conjurer(), Chimera(),
                      Dragonkin(), Griffin(), DrowAssassin(), Cyborg(), DarkKnight()],
                '5': [Chest(), LockedChest(), DrowAssassin(), DarkKnight(), Golem(), ShadowSerpent(), Aboleth(),
                      Beholder(), Behemoth(), Basilisk(), Hydra(), Lich(), MindFlayer(), Warforged(), Wyrm(), Wyvern()]}
    enemy = random.choice(monsters[level])

    return enemy


class Enemy:

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        self.name = name
        self.status_effects = {"Stun": [False, 0], "Poison": [False, 0, 0], "DOT": [False, 0, 0], "Doom": [False, 0]}
        self.health = health + con
        self.health_max = health + con
        self.mana = mana + intel
        self.mana_max = mana + intel
        self.strength = strength
        self.intel = intel
        self.wisdom = wisdom
        self.con = con
        self.charisma = charisma
        self.dex = dex
        self.experience = exp
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand)
        self.loot = {}
        self.spellbook = {'Spells': {},
                          'Skills': {}}

    def __str__(self):
        return "Enemy: {}  Health: {}/{}  Mana: {}/{}".format(self.name, self.health, self.health_max, self.mana,
                                                              self.mana_max)

    def is_alive(self):
        return self.health > 0

    def cast_spell(self, enemy, ability):
        """
        Function that controls the character's abilities and spells during combat
        """
        stun = enemy.status_effects['Stun'][0]
        print("{} casts {}.".format(self.name.capitalize(), ability().name))
        enemy_dam_red = 0
        if 'Defense' in enemy.equipment['Pendant']().mod:
            enemy_dam_red += int(enemy.equipment['Pendant']().mod.split(' ')[0])
        spell_mod = 0
        try:
            if 'Damage' in self.equipment['Pendant']().mod:
                spell_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
        except KeyError:
            pass
        if ability().cat == 'Attack':
            damage = random.randint(((ability().damage + self.intel) // 2) + spell_mod,
                                    (ability().damage + self.intel) + spell_mod)
            if self.equipment['OffHand']().subtyp == 'Tome':
                damage += self.equipment['OffHand']().mod
                spell_mod = self.equipment['OffHand']().mod
            elif self.equipment['Weapon']().subtyp == 'Staff':
                spell_mod = self.equipment['Weapon']().damage * 2
            damage -= random.randint((enemy.wisdom // 4) + enemy_dam_red, (enemy.wisdom // 2) + enemy_dam_red)
            crit = 1
            if not random.randint(0, ability().crit):
                crit = 2
            damage *= crit
            if crit == 2:
                print("Critical Hit!")
                time.sleep(0.25)
            if random.randint(0, enemy.dex // 2) > \
                    random.randint(self.intel // 2, self.intel) and not stun:
                print("{} dodged the {} and was unhurt.".format(enemy.name.capitalize(), ability().name))
                time.sleep(0.25)
            elif random.randint(0, enemy.con // 2) > \
                    random.randint(self.intel // 2, self.intel):
                damage //= 2
                print("{} shrugs off the {} and only receives half of the damage.".format(enemy.name.capitalize(),
                                                                                          ability().name))
                print("{} damages {} for {} hit points.".format(self.name, enemy.name.capitalize(), damage))
                time.sleep(0.25)
                enemy.health = enemy.health - damage
            else:
                if damage == 0:
                    print("{} was ineffective and did 0 damage".format(ability().name))
                    time.sleep(0.25)
                else:
                    print("{} damages {} for {} hit points.".format(self.name, enemy.name.capitalize(), damage))
                    time.sleep(0.25)
                    enemy.health = enemy.health - damage
        elif ability().cat == 'Enhance':
            self.weapon_damage(enemy, dmg_mod=ability().mod + spell_mod)
        elif ability().cat == 'Heal':
            heal = int(random.randint((self.health_max + self.wisdom) // 2,
                                      (self.health_max + self.wisdom)) * ability().heal)
            if (heal + self.health) > self.health_max:
                heal = self.health_max - self.health
            self.health += heal
            print("{} healed yourself for {} hit points.".format(self.name, heal))
            if enemy.cls == 'INQUISITOR' or enemy.cls == 'SEEKER' or 'Vision' in enemy.equipment['Pendant']().mod:
                print("{} fully healed itself!".format(self.name))
        elif ability().cat == 'Kill':
            if ability().name == 'Desoul':
                if random.randint(0, self.intel) \
                        > random.randint(enemy.con // 2, enemy.con):
                    enemy.health = 0
                    print("{} rips the soul right out of the {} and it falls to the ground dead.".format(
                        self.name, enemy.name.capitalize()))
                else:
                    print("The spell has no effect.")
            else:
                pass
        if ability().name == 'Terrify':
            if random.randint(self.intel // 2, self.intel) \
                    > random.randint(enemy.wisdom // 2, enemy.wisdom):
                enemy.status_effects["Stun"][0] = True
                enemy.status_effects["Stun"][1] = ability().stun
                print("{} stuns {} for {} turns.".format(self.name, enemy.name.capitalize(), ability().stun))
        if ability().name == 'Corruption':
            if random.randint(self.intel // 2, self.intel) \
                    > random.randint(enemy.wisdom // 2, enemy.wisdom):
                enemy.status_effects["DOT"][0] = True
                enemy.status_effects["DOT"][1] = ability().dot_turns
                enemy.status_effects["DOT"][2] = ability().damage + spell_mod
                print("{}'s magic penetrates {}'s defenses.".format(self.name, enemy.name.capitalize()))
            else:
                print("The magic has no effect.")
        if ability().name == 'Doom':
            if random.randint(self.intel // 4, self.intel) \
                    > random.randint(enemy.wisdom // 2, enemy.wisdom):
                enemy.status_effects["Doom"][0] = True
                enemy.status_effects["Doom"][1] = ability().timer
                print("{}'s magic places a timer on {}'s life!".format(self.name, enemy.name.capitalize()))
            else:
                print("The magic has no effect.")
        self.mana -= ability().cost

    def use_ability(self, enemy, ability):
        print("{} uses {}.".format(self.name, ability().name))
        time.sleep(0.25)
        self.mana -= ability().cost
        enemy_dam_red = 0
        if 'Defense' in enemy.equipment['Ring']().mod:
            enemy_dam_red += int(enemy.equipment['Ring']().mod.split(' ')[0])
        dmg_mod = 0
        try:
            if 'Attack' in self.equipment['Ring']().mod:
                dmg_mod += int(self.equipment['Ring']().mod.split(' ')[0])
        except KeyError:
            pass
        if ability().name == "Shield Slam":
            if random.randint(self.dex // 2, self.dex) > random.randint(0, enemy.dex // 2):
                damage = max(1, int(self.strength * (2 / self.equipment['OffHand']().mod)) + dmg_mod)
                damage = max(0, damage - enemy_dam_red)
                enemy.health -= damage
                print("{} damages {} with {} for {} hit points.".format(self.name, enemy.name.capitalize(),
                                                                        ability().name,
                                                                        damage))
                if random.randint(self.strength // 2, self.strength) \
                        > random.randint(enemy.strength // 2, enemy.strength):
                    print("{} stuns {} for {} turns.".format(self.name, enemy.name.capitalize(), ability().stun))
                    enemy.status_effects['Stun'][0] = True
                    enemy.status_effects['Stun'][1] = ability().stun
                else:
                    print("{} failed to stun {}.".format(self.name, enemy.name.capitalize()))
            else:
                print("{} swings its shield at {} but misses entirely!".format(self.name, enemy.name.capitalize()))
        if ability().name == 'Steal':
            if len(enemy.inventory) != 0:
                if random.randint(0, self.dex) > random.randint(0, enemy.dex):
                    i = random.randint(0, len(enemy.inventory))
                    if i:
                        item_key = list(enemy.inventory.keys())[i - 1]
                        item = enemy.loot[item_key]
                        enemy.modify_inventory(item, num=1, steal=True)
                        print("{} steals {} from {}!".format(self.name, item().name, enemy.name.capitalize()))
                    else:
                        enemy_gold = enemy.gold
                        gold_steal = random.randint(self.dex // 2, self.dex) * enemy.location_z
                        if enemy_gold >= gold_steal:
                            enemy.gold -= gold_steal
                            print("{} steals {} gold from {}!".format(self.name, gold_steal, enemy.name.capitalize()))
                            self.loot['Gold'] += gold_steal
                        else:
                            enemy_gold = 0
                            print("{} steals {} gold from {}!".format(self.name, enemy_gold, enemy.name.capitalize()))
                            self.loot['Gold'] += enemy_gold
                else:
                    print("{} couldn't steal anything.".format(self.name))
            else:
                print("{} doesn't have anything to steal.".format(enemy.name.capitalize()))
        if ability().subtyp == 'Drain':
            if 'Health' in ability().name:
                drain = random.randint((self.health + self.intel) // 5,
                                       (self.health + self.intel) // 1.5)
                if not random.randint(self.wisdom // 2, self.wisdom) > random.randint(0, enemy.wisdom // 2):
                    drain = drain // 2
                if drain > enemy.health:
                    drain = enemy.health
                enemy.health -= drain
                self.health += drain
                print("{} drains {} health from {}.".format(self.name, drain, enemy.name.capitalize()))
            if 'Mana' in ability().name:
                drain = random.randint((self.mana + self.intel) // 5,
                                       (self.mana + self.intel) // 1.5)
                if not random.randint(self.wisdom // 2, self.wisdom) > random.randint(0, enemy.wisdom // 2):
                    drain = drain // 2
                if drain > enemy.mana:
                    drain = enemy.mana
                enemy.mana -= drain
                self.mana += drain
                print("{} drains {} mana from {}.".format(self.name, drain, enemy.name.capitalize()))
        if ability().name == 'Poison Strike':
            self.weapon_damage(enemy)
            if random.randint(self.dex // 2, self.dex) \
                    > random.randint(enemy.con // 2, enemy.con):
                enemy.status_effects['Poison'][0] = True
                enemy.status_effects['Poison'][1] = ability().poison_rounds
                enemy.status_effects['Poison'][2] = ability().poison_damage
            else:
                print("{} resisted the poison.".format(enemy.name.capitalize()))
        if ability().name == 'Kidney Punch':
            self.weapon_damage(enemy)
            if random.randint(self.dex // 2, self.dex) \
                    > random.randint(enemy.con // 2, enemy.con):
                enemy.status_effects['Stun'][0] = True
                enemy.status_effects['Stun'][1] = ability().stun
            else:
                print("{} resisted the poison.".format(enemy.name.capitalize()))
        if ability().name == 'Lockpick':
            enemy.lock = False
        if ability().name == 'Multi-Strike':
            for _ in range(ability().strikes):
                self.weapon_damage(enemy)
        if ability().name == 'Jump':
            for _ in range(ability().strikes):
                self.weapon_damage(enemy, crit=2)
        if ability().name == 'Backstab' or ability().name == 'Piercing Strike':
            self.weapon_damage(enemy, ignore=True)
        if ability().name == 'Mortal Strike':
            self.weapon_damage(enemy, crit=ability().crit)

    def weapon_damage(self, enemy, crit=1, off_crit=1, ignore=False, dmg_mod=0):
        """
        Function that controls the character's basic attack during combat
        """
        try:
            if 'Attack' in self.equipment['Ring']().mod:
                dmg_mod += int(self.equipment['Ring']().mod.split(' ')[0])
        except KeyError:
            pass
        enemy_dam_red = 0
        if 'Defense' in enemy.equipment['Ring']().mod:
            enemy_dam_red += int(enemy.equipment['Ring']().mod.split(' ')[0])
        stun = enemy.status_effects['Stun'][0]
        blk = False
        off_blk = False
        blk_amt = 0
        off_blk_amt = 0
        dodge = False
        off_dodge = False
        off_damage = 0
        if self.equipment['Weapon']().typ == 'Natural':
            att_typ = self.equipment['Weapon']().name
            off_att_typ = self.equipment['Weapon']().name
            if self.equipment['Weapon']().ignore:
                print("Armor is ignored.")  # remove this statement
                ignore = True
        else:
            att_typ = 'damages'
            off_att_typ = 'damages'
        if ignore:
            dmg = max(1, (self.strength + self.equipment['Weapon']().damage + dmg_mod))
            damage = random.randint((dmg // 2) - enemy_dam_red, dmg - enemy_dam_red)
            if self.equipment['OffHand']().typ == 'Weapon' or self.equipment['OffHand']().typ == 'Natural':
                off_dmg = max(1, (self.strength // 2 + self.equipment['OffHand']().damage + dmg_mod // 2))
                off_damage = random.randint((off_dmg // 4) - enemy_dam_red, (off_dmg // 2) - enemy_dam_red)
        elif stun:
            dmg = max(1, (self.strength + self.equipment['Weapon']().damage - enemy.equipment['Armor']().armor
                          + dmg_mod))
            damage = random.randint((dmg // 2) - enemy_dam_red, dmg - enemy_dam_red)
            if self.equipment['OffHand']().typ == 'Weapon' or self.equipment['OffHand']().typ == 'Natural':
                off_dmg = max(1, (self.strength // 2 + self.equipment['OffHand']().damage
                                  - enemy.equipment['Armor']().armor + dmg_mod // 2))
                off_damage = random.randint((off_dmg // 4) - enemy_dam_red, (off_dmg // 2) - enemy_dam_red)
        else:
            dmg = max(1,
                      (self.strength + self.equipment['Weapon']().damage - enemy.equipment['Armor']().armor + dmg_mod))
            damage = random.randint((dmg // 2) - enemy_dam_red, dmg - enemy_dam_red)
            if enemy.equipment['OffHand']().subtyp == 'Shield':
                if not random.randint(0, int(enemy.equipment['OffHand']().mod)):
                    blk = True
                    blk_amt = (100 / enemy.equipment['OffHand']().mod +
                               random.randint(enemy.strength // 2, enemy.strength) -
                               random.randint(self.strength // 2, self.strength)) / 100
                    damage *= (1 - blk_amt)
            if random.randint(0, enemy.dex // 2) > random.randint(self.dex // 2, self.dex):
                print("{} evades {}'s attack.".format(enemy.name.capitalize(), self.name))
                time.sleep(0.25)
                dodge = True
            if self.equipment['OffHand']().typ == 'Weapon' or self.equipment['OffHand']().typ == 'Natural':
                off_crit = 1
                off_dmg = max(1, (self.strength // 2 + self.equipment['OffHand']().damage -
                                  enemy.equipment['Armor']().armor + dmg_mod // 2))
                off_damage = random.randint((off_dmg // 4) - enemy_dam_red, (off_dmg // 2) - enemy_dam_red)
                if enemy.equipment['OffHand']().subtyp == 'Shield':
                    if not random.randint(0, int(enemy.equipment['OffHand']().mod)):
                        off_blk = True
                        off_blk_amt = (100 / enemy.equipment['OffHand']().mod +
                                       random.randint(enemy.strength // 2, enemy.strength) -
                                       random.randint(self.strength // 2, self.strength)) / 100
                        off_damage *= (1 - off_blk_amt)
                if random.randint(0, enemy.dex // 2) > random.randint(self.dex // 2, self.dex):
                    off_dodge = True
        if not dodge:
            if not random.randint(0, int(self.equipment['Weapon']().crit)):
                crit = 2
            damage *= crit
            damage = int(damage)
            damage = max(0, damage)
            if crit == 2:
                print("Critical Hit!")
                time.sleep(0.25)
            if blk:
                print("{} blocked {}'s attack and mitigated {} percent of the damage.".format(
                    enemy.name.capitalize(), self.name, int(blk_amt * 100)))
            if damage == 0:
                print("{} attacked {} but did 0 damage".format(self.name, enemy.name.capitalize()))
                time.sleep(0.25)
            else:
                print("{} {} {} for {} hit points.".format(self.name, att_typ, enemy.name.capitalize(), damage))
                time.sleep(0.25)
            enemy.health -= damage
        if self.equipment['OffHand']().typ == 'Weapon' or self.equipment['OffHand']().typ == 'Natural':
            if not off_dodge:
                if not random.randint(0, int(self.equipment['OffHand']().crit)):
                    off_crit = 2
                off_damage *= off_crit
                off_damage = int(off_damage)
                off_damage = max(0, off_damage)
                if off_crit == 2:
                    print("Critical Hit!")
                    time.sleep(0.25)
                if off_blk:
                    print("{} blocked {}'s attack and mitigated {} percent of the damage.".format(
                        enemy.name.capitalize(), self.name, int(off_blk_amt * 100)))
                if off_damage == 0:
                    print("{} attacked {} but did 0 damage".format(self.name, enemy.name.capitalize()))
                    time.sleep(0.25)
                else:
                    print("{} {} {} for {} hit points.".format(self.name, off_att_typ, enemy.name.capitalize(),
                                                               off_damage))
                    time.sleep(0.25)
                enemy.health -= off_damage
            else:
                print("{} evades {}'s off-hand attack.".format(enemy.name.capitalize(), self.name))
                time.sleep(0.25)
        if att_typ == 'leers':
            if random.randint(0, self.intel) \
                    > random.randint(enemy.con // 2, enemy.con):
                enemy.health = 0
                print("{} turns {} to stone!".format(self.name, enemy.name.capitalize()))


# Natural weapons
class NaturalWeapon:

    def __init__(self, name, damage, crit, subtyp):
        self.name = name
        self.damage = damage
        self.crit = crit
        self.subtyp = subtyp
        self.ignore = False
        self.poison = False
        self.typ = "Natural"


class RatBite(NaturalWeapon):

    def __init__(self):
        super().__init__(name="bites", damage=2, crit=9, subtyp='Natural')


class WolfClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="swipes", damage=4, crit=6, subtyp='Natural')


class BearClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="mauls", damage=5, crit=7, subtyp='Natural')


class Stinger(NaturalWeapon):
    """
    Add a poison chance
    """

    def __init__(self):
        super().__init__(name="stings", damage=3, crit=4, subtyp='Natural')
        self.poison = True


class BirdClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="claws", damage=3, crit=5, subtyp='Natural')


class SnakeFang(NaturalWeapon):
    """
    Add a poison chance
    """

    def __init__(self):
        super().__init__(name="strikes", damage=3, crit=4, subtyp='Natural')
        self.poison = True


class AlligatorTail(NaturalWeapon):

    def __init__(self):
        super().__init__(name="swipes", damage=8, crit=8, subtyp='Natural')


class LionPaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="swipes", damage=5, crit=5, subtyp='Natural')


class Laser(NaturalWeapon):

    def __init__(self):
        super().__init__(name="zaps", damage=5, crit=3, subtyp='Natural')
        self.ignore = True


class Gaze(NaturalWeapon):
    """
    Attempts to turn the player to stone
    """

    def __init__(self):
        super().__init__(name="leers", damage=0, crit=5, subtyp='Natural')


class DragonClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="rakes", damage=6, crit=5, subtyp='Natural')
        self.ignore = False


class DragonTail(NaturalWeapon):

    def __init__(self):
        super().__init__(name="swipes", damage=18, crit=6, subtyp='Natural')


class NaturalArmor:

    def __init__(self, name, armor, subtyp):
        self.name = name
        self.armor = armor
        self.subtyp = subtyp
        self.typ = "Natural"


class AnimalHide(NaturalArmor):

    def __init__(self):
        super().__init__(name='Animal Hide', armor=2, subtyp='Natural')


class Carapace(NaturalArmor):

    def __init__(self):
        super().__init__(name='Carapace', armor=3, subtyp='Natural')


class StoneArmor(NaturalArmor):

    def __init__(self):
        super().__init__(name='Stone Armor', armor=4, subtyp='Natural')


class MetalPlating(NaturalArmor):

    def __init__(self):
        super().__init__(name='Metal Plating', armor=5, subtyp='Natural')


class DragonScale(NaturalArmor):

    def __init__(self):
        super().__init__(name='Dragon Scales', armor=6, subtyp='Natural')


# Enemy skills
class EnemySkill(spells.Ability):
    pass


# Enemies
class Chest(Enemy):

    def __init__(self):
        super().__init__(name='Chest', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0, exp=0)
        self.loot = dict()
        self.lock = False


class LockedChest(Enemy):

    def __init__(self):
        super().__init__(name='Locked Chest', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0,
                         exp=0)
        self.loot = dict()
        self.lock = True


class GreenSlime(Enemy):

    def __init__(self):
        super().__init__(name='Green Slime', health=random.randint(1, 6), mana=0, strength=6, intel=0, wisdom=15, con=8,
                         charisma=0, dex=4, exp=random.randint(1, 20))
        self.loot = dict(Gold=random.randint(1, 8), Key=items.Key)
        self.spellbook = {"Spells": [],
                          "Skills": []}


class GiantRat(Enemy):

    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(2, 4), mana=0, strength=4, intel=0, wisdom=3, con=6,
                         charisma=0, dex=15, exp=random.randint(7, 14))
        self.equipment['Weapon'] = RatBite
        self.loot = dict(Gold=random.randint(1, 5))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Goblin(Enemy):

    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(2, 4), mana=0, strength=6, intel=0, wisdom=2, con=8,
                         charisma=0, dex=8, exp=random.randint(7, 16))
        self.equipment['Weapon'] = items.BronzeSword
        self.loot = dict(Gold=random.randint(4, 10), Weapon=self.equipment['Weapon'])
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Bandit(Enemy):

    def __init__(self):
        super().__init__(name='Bandit', health=random.randint(4, 8), mana=6, strength=8, intel=0, wisdom=5, con=8,
                         charisma=0, dex=10, exp=random.randint(8, 18))
        self.equipment['Weapon'] = items.BronzeDagger
        self.equipment['Armor'] = items.PaddedArmor
        self.loot = dict(Gold=random.randint(15, 25), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])
        self.spellbook = {"Spells": [],
                          "Skills": [spells.Steal]}


class Skeleton(Enemy):

    def __init__(self):
        super().__init__(name='Skeleton', health=random.randint(5, 7), mana=0, strength=10, intel=0, wisdom=8, con=12,
                         charisma=0, dex=6, exp=random.randint(11, 20))
        self.equipment['Weapon'] = items.BronzeSword
        self.loot = dict(Gold=random.randint(10, 20), Potion=items.HealthPotion)
        self.spellbook = {"Spells": [],
                          "Skills": []}


class GiantHornet(Enemy):

    def __init__(self):
        super().__init__(name='Giant Hornet', health=random.randint(6, 10), mana=0, strength=6, intel=0, wisdom=6,
                         con=6, charisma=0, dex=18, exp=random.randint(13, 24))
        self.equipment['Weapon'] = Stinger
        self.loot = dict(Gold=random.randint(6, 15))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Zombie(Enemy):

    def __init__(self):
        super().__init__(name='Zombie', health=random.randint(8, 12), mana=20, strength=15, intel=0, wisdom=5, con=8,
                         charisma=0, dex=4, exp=random.randint(11, 22))
        self.loot = dict(Gold=random.randint(15, 30), Misc=items.Key)
        self.spellbook = {"Spells": [],
                          "Skills": [spells.HealthDrain]}


class GiantSpider(Enemy):

    def __init__(self):
        super().__init__(name='Giant Spider', health=random.randint(12, 15), mana=0, strength=9, intel=0, wisdom=10,
                         con=8, charisma=0, dex=12, exp=random.randint(15, 24))
        self.equipment['Weapon'] = Stinger
        self.equipment['Armor'] = Carapace
        self.loot = dict(Gold=random.randint(15, 30), Potion=items.ManaPotion)
        self.spellbook = {"Spells": [],
                          "Skills": []}


class TwistedDwarf(Enemy):

    def __init__(self):
        super().__init__(name='Twisted Dwarf', health=random.randint(15, 19), mana=10, strength=12, intel=0, wisdom=10,
                         con=12, charisma=0, dex=12, exp=random.randint(25, 44))
        self.equipment['Weapon'] = items.Axe
        self.equipment['Armor'] = items.HideArmor
        self.loot = dict(Gold=random.randint(25, 40), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])
        self.spellbook = {"Spells": [],
                          "Skills": [spells.PiercingStrike]}


# Level 1 Boss
class Minotaur(Enemy):

    def __init__(self):
        super().__init__(name='Minotaur', health=random.randint(20, 24), mana=20, strength=14, intel=0, wisdom=10,
                         con=14, charisma=0, dex=12, exp=random.randint(55, 110))
        self.equipment['Weapon'] = items.BattleAxe
        self.equipment['Armor'] = items.LeatherArmor
        self.loot = dict(Gold=random.randint(30, 75), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])
        self.spellbook = {"Spells": [],
                          "Skills": [spells.MortalStrike]}


class Gnoll(Enemy):

    def __init__(self):
        super().__init__(name='Gnoll', health=random.randint(10, 14), mana=0, strength=12, intel=0, wisdom=5, con=8,
                         charisma=0, dex=16, exp=random.randint(45, 85))
        self.equipment['Weapon'] = items.Spear
        self.equipment['Armor'] = items.PaddedArmor
        self.loot = dict(Gold=random.randint(30, 60), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])
        self.spellbook = {"Spells": [],
                          "Skills": []}


class GiantSnake(Enemy):

    def __init__(self):
        super().__init__(name='Giant Snake', health=random.randint(13, 16), mana=0, strength=14, intel=0, wisdom=6,
                         con=14, charisma=0, dex=16, exp=random.randint(60, 100))
        self.equipment['Weapon'] = SnakeFang
        self.loot = dict(Gold=random.randint(35, 75))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Orc(Enemy):

    def __init__(self):
        super().__init__(name='Orc', health=random.randint(8, 12), mana=0, strength=10, intel=0, wisdom=5, con=10,
                         charisma=0, dex=14, exp=random.randint(45, 80))
        self.equipment['Weapon'] = items.IronSword
        self.equipment['Armor'] = items.PaddedArmor
        self.loot = dict(Gold=random.randint(20, 65), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])
        self.spellbook = {"Spells": [],
                          "Skills": []}


class GiantOwl(Enemy):

    def __init__(self):
        super().__init__(name='Giant Owl', health=random.randint(8, 12), mana=0, strength=10, intel=0, wisdom=5, con=10,
                         charisma=0, dex=14, exp=random.randint(45, 80))
        self.equipment['Weapon'] = BirdClaw
        self.loot = dict(Gold=random.randint(20, 65))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Vampire(Enemy):

    def __init__(self):
        super().__init__(name='Vampire', health=random.randint(10, 15), mana=30, strength=19, intel=0, wisdom=12,
                         con=15, charisma=0, dex=14, exp=random.randint(50, 90))
        self.loot = dict(Gold=random.randint(40, 90), Potion=items.GreatHealthPotion)
        self.spellbook = {"Spells": [],
                          "Skills": [spells.HealthDrain]}


class Direwolf(Enemy):

    def __init__(self):
        super().__init__(name='Direwolf', health=random.randint(13, 16), mana=0, strength=17, intel=0, wisdom=6, con=14,
                         charisma=0, dex=16, exp=random.randint(60, 100))
        self.equipment['Weapon'] = WolfClaw
        self.equipment['Armor'] = AnimalHide
        self.loot = dict(Gold=random.randint(35, 75))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Wererat(Enemy):

    def __init__(self):
        super().__init__(name='Wererat', health=random.randint(12, 14), mana=0, strength=12, intel=0, wisdom=12, con=11,
                         charisma=0, dex=18, exp=random.randint(57, 94))
        self.equipment['Weapon'] = RatBite
        self.loot = dict(Gold=random.randint(40, 65))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class RedSlime(Enemy):

    def __init__(self):
        super().__init__(name='Red Slime', health=random.randint(8, 20), mana=30, strength=10, intel=10, wisdom=22,
                         con=12, charisma=0, dex=5, exp=random.randint(43, 150))
        self.loot = dict(Gold=random.randint(20, 120), Potion=items.SuperHealthPotion)
        self.spellbook = {'Spells': [spells.Firebolt],
                          'Skills': []}


class GiantScorpion(Enemy):

    def __init__(self):
        super().__init__(name='Giant Scorpion', health=random.randint(13, 18), mana=0, strength=12, intel=0, wisdom=10,
                         con=12, charisma=0, dex=9, exp=random.randint(65, 105))
        self.equipment['Weapon'] = Stinger
        self.equipment['Armor'] = Carapace
        self.loot = dict(Gold=random.randint(40, 65))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Warrior(Enemy):

    def __init__(self):
        super().__init__(name='Warrior', health=random.randint(12, 17), mana=0, strength=14, intel=0, wisdom=8, con=12,
                         charisma=0, dex=8, exp=random.randint(65, 110))
        self.equipment['Weapon'] = items.IronSword
        self.equipment['Armor'] = items.RingMail
        self.loot = dict(Gold=random.randint(25, 100), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])
        self.spellbook = {"Spells": [],
                          "Skills": [spells.PiercingStrike]}


class Harpy(Enemy):

    def __init__(self):
        super().__init__(name='Harpy', health=random.randint(18, 25), mana=0, strength=18, intel=13, wisdom=13,
                         con=14, charisma=0, dex=23, exp=random.randint(65, 115))
        self.equipment['Weapon'] = BirdClaw
        self.loot = dict(Gold=random.randint(50, 75))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Naga(Enemy):

    def __init__(self):
        super().__init__(name='Naga', health=random.randint(22, 28), mana=0, strength=15, intel=13, wisdom=15,
                         con=15, charisma=0, dex=17, exp=random.randint(67, 118))
        self.equipment['Weapon'] = items.Spear
        self.loot = dict(Gold=random.randint(55, 75), Weapon=self.equipment['Weapon'], Potion=items.GreatManaPotion)
        self.spellbook = {"Spells": [],
                          "Skills": []}


# Level 2 Boss
class Pseudodragon(Enemy):

    def __init__(self):
        super().__init__(name='Pseudodragon', health=random.randint(40, 55), mana=100, strength=22, intel=12, wisdom=16,
                         con=20, charisma=0, dex=14, exp=random.randint(125, 225))
        self.equipment['Weapon'] = DragonClaw
        self.equipment['Armor'] = DragonScale
        self.loot = dict(Gold=random.randint(100, 250), Potion=items.SuperManaPotion)
        self.spellbook = {'Spells': [spells.Fireball],
                          'Skills': []}


class Ghoul(Enemy):

    def __init__(self):
        super().__init__(name='Ghoul', health=random.randint(42, 60), mana=30, strength=23, intel=0, wisdom=8, con=24,
                         charisma=0, dex=12, exp=random.randint(110, 190))
        self.loot = dict(Gold=random.randint(35, 45), Potion=items.SuperHealthPotion)
        self.spellbook = {"Spells": [],
                          "Skills": [spells.HealthDrain]}


class PitViper(Enemy):

    def __init__(self):
        super().__init__(name='Pit Viper', health=random.randint(38, 50), mana=0, strength=17, intel=0, wisdom=8,
                         con=16, charisma=0, dex=18, exp=random.randint(115, 190))
        self.equipment['Weapon'] = SnakeFang
        self.loot = dict(Gold=random.randint(50, 85))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Disciple(Enemy):

    def __init__(self):
        super().__init__(name='Disciple', health=random.randint(40, 50), mana=50, strength=16, intel=17, wisdom=15,
                         con=16, charisma=0, dex=16, exp=random.randint(110, 190))
        self.equipment['Weapon'] = items.SteelDagger
        self.equipment['Armor'] = items.SilverCloak
        self.loot = dict(Gold=random.randint(55, 95), Potion=items.SuperManaPotion)
        self.spellbook = {'Spells': [spells.Icicle],
                          'Skills': []}


class Werewolf(Enemy):

    def __init__(self):
        super().__init__(name='Werewolf', health=random.randint(45, 55), mana=0, strength=18, intel=0, wisdom=10,
                         con=20, charisma=0, dex=18, exp=random.randint(120, 200))
        self.equipment['Weapon'] = WolfClaw
        self.equipment['Armor'] = AnimalHide
        self.equipment['OffHand'] = WolfClaw
        self.loot = dict(Gold=random.randint(45, 55))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class BlackSlime(Enemy):

    def __init__(self):
        super().__init__(name='Black Slime', health=random.randint(25, 60), mana=50, strength=13, intel=0, wisdom=30,
                         con=15, charisma=0, dex=6, exp=random.randint(85, 260))
        self.loot = dict(Gold=random.randint(30, 180), Potion=items.Elixir)
        self.spellbook = {'Spells': [spells.ShadowBolt],
                          'Skills': []}


class Ogre(Enemy):

    def __init__(self):
        super().__init__(name='Ogre', health=random.randint(40, 50), mana=0, strength=20, intel=10, wisdom=14, con=20,
                         charisma=0, dex=14, exp=random.randint(115, 195))
        self.equipment['Weapon'] = items.IronHammer
        self.equipment['Armor'] = items.LeatherArmor
        self.loot = dict(Gold=random.randint(50, 75), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Alligator(Enemy):

    def __init__(self):
        super().__init__(name='Alligator', health=random.randint(60, 75), mana=0, strength=19, intel=0, wisdom=7,
                         con=20, charisma=0, dex=15, exp=random.randint(120, 200))
        self.equipment['Weapon'] = AlligatorTail
        self.loot = dict(Gold=random.randint(40, 50))
        self.spellbook = {"Spells": [],
                          "Skills": [spells.DoubleStrike]}


class Troll(Enemy):

    def __init__(self):
        super().__init__(name='Troll', health=random.randint(50, 65), mana=0, strength=19, intel=0, wisdom=8, con=24,
                         charisma=0, dex=15, exp=random.randint(125, 210))
        self.equipment['Weapon'] = items.GreatAxe
        self.equipment['Armor'] = items.LeatherArmor
        self.loot = dict(Gold=random.randint(35, 45), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])
        self.spellbook = {"Spells": [],
                          "Skills": [spells.MortalStrike]}


class Direbear(Enemy):

    def __init__(self):
        super().__init__(name='Direbear', health=random.randint(55, 70), mana=0, strength=23, intel=0, wisdom=6, con=26,
                         charisma=0, dex=18, exp=random.randint(110, 210))
        self.equipment['Weapon'] = BearClaw
        self.equipment['Armor'] = AnimalHide
        self.equipment['OffHand'] = BearClaw
        self.loot = dict(Gold=random.randint(45, 60))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class GoldenEagle(Enemy):

    def __init__(self):
        super().__init__(name='Golden Eagle', health=random.randint(40, 50), mana=0, strength=16, intel=15, wisdom=15,
                         con=17, charisma=0, dex=25, exp=random.randint(130, 220))
        self.equipment['Weapon'] = BirdClaw
        self.equipment['OffHand'] = BirdClaw
        self.loot = dict(Gold=random.randint(50, 75))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class EvilCrusader(Enemy):

    def __init__(self):
        super().__init__(name='Evil Crusader', health=random.randint(45, 60), mana=50, strength=18, intel=18, wisdom=17,
                         con=26, charisma=0, dex=14, exp=random.randint(140, 225))
        self.equipment['Weapon'] = items.SteelSword
        self.equipment['Armor'] = items.Splint
        self.equipment['OffHand'] = items.KiteShield
        self.loot = dict(Gold=random.randint(65, 90), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         OffHand=self.equipment['OffHand'])
        self.spellbook = {"Spells": [spells.Smite],
                          "Skills": [spells.ShieldSlam]}


# Level 3 Boss
class Cockatrice(Enemy):

    def __init__(self):
        super().__init__(name='Cockatrice', health=random.randint(60, 75), mana=0, strength=23, intel=0, wisdom=15,
                         con=16, charisma=0, dex=20, exp=random.randint(250, 375))
        self.equipment['Weapon'] = BirdClaw
        self.equipment['OffHand'] = BirdClaw
        self.loot = dict(Gold=random.randint(120, 150), Potion=items.MasterHealthPotion)
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Gargoyle(Enemy):

    def __init__(self):
        super().__init__(name='Gargoyle', health=random.randint(35, 55), mana=0, strength=23, intel=10, wisdom=0,
                         con=18, charisma=0, dex=21, exp=random.randint(210, 330))
        self.equipment['Weapon'] = BirdClaw
        self.equipment['Armor'] = StoneArmor
        self.loot = dict(Gold=random.randint(75, 125))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Conjurer(Enemy):

    def __init__(self):
        super().__init__(name='Conjurer', health=random.randint(30, 45), mana=100, strength=12, intel=22, wisdom=18,
                         con=14, charisma=0, dex=13, exp=random.randint(215, 340))
        self.equipment['Weapon'] = items.SerpentStaff
        self.equipment['Armor'] = items.GoldCloak
        self.loot = dict(Gold=random.randint(110, 145), Potion=items.MasterManaPotion)
        self.spellbook = {"Spells": [spells.Icicle],
                          "Skills": [spells.ManaDrain]}


class Chimera(Enemy):

    def __init__(self):
        super().__init__(name='Chimera', health=random.randint(40, 75), mana=0, strength=23, intel=14, wisdom=16,
                         con=20, charisma=0, dex=14, exp=random.randint(230, 380))
        self.equipment['Weapon'] = LionPaw
        self.equipment['Armor'] = AnimalHide
        self.equipment['OffHand'] = BirdClaw
        self.loot = dict(Gold=random.randint(100, 250), Potion=items.SuperManaPotion)
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Dragonkin(Enemy):

    def __init__(self):
        super().__init__(name='Dragonkin', health=random.randint(50, 75), mana=0, strength=23, intel=10, wisdom=18,
                         con=20, charisma=0, dex=20, exp=random.randint(250, 480))
        self.equipment['Weapon'] = items.Halberd
        self.equipment['Armor'] = items.Breastplate
        self.loot = dict(Gold=random.randint(150, 300), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         Potion=items.Elixir)
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Griffin(Enemy):

    def __init__(self):
        super().__init__(name='Griffin', health=random.randint(60, 80), mana=0, strength=23, intel=10, wisdom=18,
                         con=18, charisma=0, dex=25, exp=random.randint(240, 450))
        self.equipment['Weapon'] = LionPaw
        self.equipment['Armor'] = AnimalHide
        self.equipment['OffHand'] = BearClaw
        self.loot = dict(Gold=random.randint(140, 280))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class DrowAssassin(Enemy):

    def __init__(self):
        super().__init__(name='Drow Assassin', health=random.randint(45, 65), mana=40, strength=15, intel=16, wisdom=15,
                         con=14, charisma=0, dex=22, exp=random.randint(280, 480))
        self.equipment['Weapon'] = items.Carnwennan
        self.equipment['Armor'] = items.Studded
        self.equipment['OffHand'] = items.AdamantiteDagger
        self.loot = dict(Gold=random.randint(160, 250), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         OffHand=self.equipment['OffHand'])
        self.spellbook = {"Spells": [],
                          "Skills": [spells.PoisonStrike, spells.Backstab, spells.KidneyPunch, spells.Steal]}


class Cyborg(Enemy):

    def __init__(self):
        super().__init__(name='Cyborg', health=random.randint(70, 95), mana=0, strength=28, intel=13, wisdom=0, con=18,
                         charisma=0, dex=14, exp=random.randint(290, 500))
        self.equipment['Weapon'] = Laser
        self.equipment['Armor'] = MetalPlating
        self.loot = dict(Gold=random.randint(200, 300))
        self.spellbook = {"Spells": [],
                          "Skills": []}


class DarkKnight(Enemy):

    def __init__(self):
        super().__init__(name='Dark Knight', health=random.randint(60, 80), mana=50, strength=20, intel=15, wisdom=12,
                         con=21, charisma=0, dex=17, exp=random.randint(300, 550))
        self.equipment['Weapon'] = items.Gungnir
        self.equipment['Armor'] = items.PlateMail
        self.equipment['OffHand'] = items.TowerShield
        self.loot = dict(Gold=random.randint(300, 420), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         OffHand=self.equipment['OffHand'])
        self.spellbook = {"Spells": [spells.EnhanceBlade],
                          "Skills": [spells.ShieldSlam2]}


# Level 4 boss
class Golem(Enemy):

    def __init__(self):
        super().__init__(name='Golem', health=random.randint(150, 200), mana=0, strength=27, intel=10, wisdom=18,
                         con=28, charisma=0, dex=20, exp=random.randint(500, 800))
        self.equipment['Weapon'] = Laser
        self.equipment['Armor'] = StoneArmor
        self.equipment['OffHand'] = Laser
        self.loot = dict(Gold=random.randint(400, 600), Potion=items.Aegis)
        self.spellbook = {"Spells": [],
                          "Skills": []}


class ShadowSerpent(Enemy):

    def __init__(self):
        super().__init__(name='Shadow Serpent', health=random.randint(130, 180), mana=0, strength=24, intel=10,
                         wisdom=15, con=22, charisma=0, dex=23, exp=random.randint(480, 790))
        self.equipment['Weapon'] = SnakeFang
        self.loot = dict(Gold=random.randint(280, 485), Potion=items.Megalixir)
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Aboleth(Enemy):

    def __init__(self):
        super().__init__(name='Aboleth', health=random.randint(110, 500), mana=120, strength=18, intel=20, wisdom=50,
                         con=25, charisma=0, dex=8, exp=random.randint(350, 930))
        self.loot = dict(Gold=random.randint(130, 750), Potion=items.AardBeing)
        self.spellbook = {"Spells": [spells.ShadowBolt3],
                          "Skills": []}


class Beholder(Enemy):

    def __init__(self):
        super().__init__(name='Beholder', health=random.randint(150, 300), mana=0, strength=25, intel=40, wisdom=35,
                         con=28, charisma=0, dex=20, exp=random.randint(500, 900))
        self.equipment['Weapon'] = Gaze
        self.loot = dict(Gold=random.randint(300, 500), OffHand=items.MedusaShield)
        self.spellbook = {"Spells": [spells.Electrocution],
                          "Skills": [spells.ManaDrain]}


class Behemoth(Enemy):

    def __init__(self):
        super().__init__(name='Behemoth', health=random.randint(200, 300), mana=0, strength=33, intel=25, wisdom=20,
                         con=30, charisma=0, dex=18, exp=random.randint(620, 950))
        self.equipment['Weapon'] = LionPaw
        self.equipment['Armor'] = AnimalHide
        self.equipment['OffHand'] = LionPaw
        self.loot = dict(Gold=random.randint(400, 550), Potion=items.Jarnbjorn)
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Lich(Enemy):

    def __init__(self):
        super().__init__(name='Lich', health=random.randint(160, 240), mana=120, strength=20, intel=35, wisdom=40,
                         con=20, charisma=0, dex=22, exp=random.randint(580, 920))
        self.equipment['Armor'] = items.MerlinRobe
        self.equipment['OffHand'] = items.Necronomicon
        self.loot = dict(Gold=random.randint(400, 530), Armor=self.equipment['Armor'], OffHand=self.equipment[
            'OffHand'])
        self.spellbook = {"Spells": [spells.ShadowBolt3, spells.Desoul],
                          "Skills": []}


class Basilisk(Enemy):

    def __init__(self):
        super().__init__(name='Basilisk', health=random.randint(180, 275), mana=0, strength=29, intel=26, wisdom=30,
                         con=27, charisma=0, dex=20, exp=random.randint(630, 900))
        self.equipment['Weapon'] = Gaze
        self.equipment['Armor'] = StoneArmor
        self.loot = dict(Gold=random.randint(380, 520), Potion=items.PrincessGuard)
        self.spellbook = {"Spells": [],
                          "Skills": []}


class MindFlayer(Enemy):

    def __init__(self):
        super().__init__(name='Mind Flayer', health=random.randint(190, 285), mana=150, strength=22, intel=40,
                         wisdom=35, con=25, charisma=0, dex=18, exp=random.randint(590, 850))
        self.equipment['Weapon'] = items.DragonStaff
        self.equipment['OffHand'] = items.Magus
        self.loot = dict(Gold=random.randint(450, 600), Weapon=self.equipment['Weapon'], OffHand=self.equipment[
            'OffHand'])
        self.spellbook = {"Spells": [spells.Doom, spells.Terrify2, spells.Corruption],
                          "Skills": []}


class Warforged(Enemy):

    def __init__(self):
        super().__init__(name='Warforged', health=random.randint(230, 300), mana=0, strength=30, intel=20, wisdom=0,
                         con=33, charisma=0, dex=10, exp=random.randint(580, 880))
        self.equipment['Weapon'] = items.Skullcrusher
        self.equipment['Armor'] = StoneArmor
        self.loot = dict(Gold=random.randint(380, 490), Weapon=self.equipment['Weapon'])
        self.spellbook = {"Spells": [],
                          "Skills": []}


class Wyrm(Enemy):

    def __init__(self):
        super().__init__(name='Wyrm', health=random.randint(220, 300), mana=150, strength=28, intel=28, wisdom=30,
                         con=28, charisma=0, dex=18, exp=random.randint(620, 880))
        self.equipment['Weapon'] = DragonTail
        self.equipment['Armor'] = DragonScale
        self.loot = dict(Gold=random.randint(650, 830), Weapon=items.Mjolnir)
        self.spellbook = {'Spells': [spells.Firestorm],
                          'Skills': []}


class Hydra(Enemy):

    def __init__(self):
        super().__init__(name='Hydra', health=random.randint(200, 275), mana=150, strength=31, intel=30, wisdom=26,
                         con=28, charisma=0, dex=18, exp=random.randint(600, 850))
        self.equipment['Weapon'] = DragonClaw
        self.equipment['Armor'] = DragonScale
        self.loot = dict(Gold=random.randint(400, 550), Weapon=items.Excalibur)
        self.spellbook = {'Spells': [spells.IceBlizzard],
                          'Skills': []}


class Wyvern(Enemy):

    def __init__(self):
        super().__init__(name='Wyvern', health=random.randint(220, 300), mana=0, strength=30, intel=33, wisdom=24,
                         con=30, charisma=0, dex=33, exp=random.randint(650, 900))
        self.equipment['Weapon'] = DragonClaw
        self.equipment['Armor'] = DragonScale
        self.equipment['OffHand'] = DragonClaw
        self.loot = dict(Gold=random.randint(420, 570), Armor=items.DragonHide)
        self.spellbook = {"Spells": [],
                          "Skills": []}


# Level 5 Boss
class RedDragon(Enemy):

    def __init__(self):
        super().__init__(name='Red Dragon', health=random.randint(500, 700), mana=250, strength=35, intel=28, wisdom=35,
                         con=30, charisma=0, dex=15, exp=random.randint(1200, 2000))
        self.equipment['Weapon'] = DragonTail
        self.equipment['Armor'] = DragonScale
        self.equipment['OffHand'] = DragonClaw
        self.loot = dict(Gold=random.randint(1500, 3000), Armor=items.Genji)
        self.spellbook = {"Spells": [spells.Restore],
                          "Skills": []}
