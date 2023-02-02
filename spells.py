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


class Spell(Ability):
    """

    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.typ = 'Spell'


class Skill(Ability):
    """

    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.typ = 'Skill'
        self.passive = False


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


# Skills
class ShieldSlam(Offensive):
    """

    """
    def __init__(self):
        super().__init__(name='Shield Slam', description='Slam the enemy with your shield, damaging with a chance to '
                                                         'stun for 1 turn.',
                         cost=3)
        self.stun = 1  # defines for how many rounds the enemy is stunned


class ShieldSlam2(Offensive):
    """
    Replaces Shield Slam
    """
    def __init__(self):
        super().__init__(name='Shield Slam', description='Slam the enemy with your shield, damaging with a chance to '
                                                         'stun for 2 turn.',
                         cost=10)
        self.stun = 2  # defines for how many rounds the enemy is stunned


class ShieldSlam3(Offensive):
    """

    """
    def __init__(self):
        super().__init__(name='Shield Slam', description='Slam the enemy with your shield, damaging with a chance to '
                                                         'stun for 3 turn.',
                         cost=20)
        self.stun = 3  # defines for how many rounds the enemy is stunned


class ShieldSlam4(Offensive):
    """

    """
    def __init__(self):
        super().__init__(name='Shield Slam', description='Slam the enemy with your shield, damaging with a chance to '
                                                         'stun for 4 turn.',
                         cost=30)
        self.stun = 4  # defines for how many rounds the enemy is stunned


class DoubleStrike(Offensive):
    """

    """
    def __init__(self):
        super().__init__(name='Multi-Strike', description='Perform a double attack with the primary weapon.',
                         cost=14)
        self.strikes = 2  # number of strikes performed


class TripleStrike(Offensive):
    """
    Replaces DoubleStrike
    """
    def __init__(self):
        super().__init__(name='Multi-Strike', description='Perform a triple attack with the primary weapon.',
                         cost=26)
        self.strikes = 3


class QuadStrike(Offensive):
    """
    Replaces TripleStrike
    """
    def __init__(self):
        super().__init__(name='Multi-Strike', description='Perform a quadruple attack with the primary weapon.',
                         cost=40)
        self.strikes = 4


class FlurryBlades(Offensive):
    """
    Replaces QuadStrike
    """
    def __init__(self):
        super().__init__(name='Multi-Strike', description='Slices the enemy in a flurry of blades.',
                         cost=50)
        self.strikes = 5


class PiercingStrike(Offensive):
    """

    """
    def __init__(self):
        super().__init__(name='Piercing Strike', description='Pierces the enemy\'s defenses, ignoring armor.',
                         cost=5)


class Jump(Offensive):
    """

    """
    def __init__(self):
        super().__init__(name='Jump', description='Leap into the air and bring down your weapon onto the enemy, '
                                                  'delivering critical damage.',
                         cost=10)
        self.strikes = 1
        self.crit = 2


class DoubleJump(Offensive):
    """
    Replaces Jump
    """
    def __init__(self):
        super().__init__(name='Jump', description='Leap into the air and bring down your weapon onto the enemy, '
                                                  'delivering critical damage twice.',
                         cost=25)
        self.strikes = 2
        self.crit = 2


class TripleJump(Offensive):
    """
    Replaces Double Jump
    """
    def __init__(self):
        super().__init__(name='Jump', description='Leap into the air and bring down your weapon onto the enemy, '
                                                  'delivering critical damage thrice.',
                         cost=40)
        self.strikes = 3
        self.crit = 2


class DoubleCast(Offensive):
    """

    """
    def __init__(self):
        super().__init__(name='Multi-Cast', description='Cast two spells at once.',
                         cost=10)
        self.cast = 2


class TripleCast(Offensive):
    """
    Replaces DoubleCast
    """
    def __init__(self):
        super().__init__(name='Multi-Cast', description='Cast three spells at once.',
                         cost=20)
        self.cast = 3


class MortalStrike(Offensive):
    """
    Critical strike plus bleed for x turns, determined by the player's strength
    """
    def __init__(self):
        super().__init__(name='Mortal Strike', description='Assault the enemy, striking them with a critical hit and '
                                                           'placing a bleed effect that deals damage over the next '
                                                           '2 turns.',
                         cost=10)
        self.crit = 2
        self.bleed = 2


class MortalStrike2(Offensive):
    """
    Devastating critical strike plus bleed for x turns, determined by the player's strength
    """
    def __init__(self):
        super().__init__(name='Mortal Strike', description='Assault the enemy, striking them with a devastating '
                                                           'critical hit and placing a bleed effect that deals damage '
                                                           'over the next 3 turns.',
                         cost=20)
        self.crit = 3
        self.bleed = 2


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
        super().__init__(name='Disarm', description='Disarm the enemy for 1 turn.',
                         cost=5)
        self.turns = 1


class Disarm2(Defensive):
    """
    Replaces Disarm
    """
    def __init__(self):
        super().__init__(name='Disarm', description='Disarm the enemy for 2 turns.',
                         cost=5)
        self.turns = 2


class Disarm3(Defensive):
    """
    Replaces Disarm 2
    """
    def __init__(self):
        super().__init__(name='Disarm', description='Disarm the enemy for 3 turns.',
                         cost=5)
        self.turns = 3


# Stealth skills
class Backstab(Stealth):
    """

    """
    def __init__(self):
        super().__init__(name='Backstab', description='Strike the opponent in the back, guaranteeing a hit and ignoring'
                                                      ' any resistance or armor.',
                         cost=6)


class Blind(Stealth):
    """

    """
    def __init__(self):
        super().__init__(name='Blind', description='Throw sand in the eyes of your enemy, blinding them and reducing '
                                                   'their chance to hit on a melee attack for 2 turns.',
                         cost=8)
        self.blind = 2


class KidneyPunch(Stealth):
    """

    """
    def __init__(self):
        super().__init__(name='Kidney Punch', description='Punch the enemy in the kidney, rendering them stunned for 1'
                                                          ' turn.',
                         cost=10)
        self.stun = 1


class KidneyPunch2(Stealth):
    """

    """
    def __init__(self):
        super().__init__(name='Kidney Punch', description='Punch the enemy in the kidney, rendering them stunned for 2'
                                                          ' turns.',
                         cost=22)
        self.stun = 2


class KidneyPunch3(Stealth):
    """

    """
    def __init__(self):
        super().__init__(name='Kidney Punch', description='Punch the enemy in the kidney, rendering them stunned for 3'
                                                          ' turns.',
                         cost=32)
        self.stun = 3


class SmokeScreen(Stealth):
    """

    """
    def __init__(self):
        super().__init__(name='Smoke Screen', description='Obscure the player in a puff of smoke, allowing the '
                                                          'player to flee without fail.',
                         cost=5)
        self.escape = True


class Steal(Stealth):
    """

    """
    def __init__(self):
        super().__init__(name='Steal', description='Relieve the enemy of their items.',
                         cost=6)


class Mug(Stealth):
    """

    """
    def __init__(self):
        super().__init__(name='Mug', description='Attack the enemy with a chance to steal their items.',
                         cost=20)


class Lockpick(Stealth):
    """

    """
    def __init__(self):
        super().__init__(name='Lockpick', description='Unlock a locked chest.',
                         cost=12)
        self.combat = False


class PoisonStrike(Stealth):
    """

    """
    def __init__(self):
        super().__init__(name='Poison Strike', description='Attack the enemy with a chance to poison the enemy for 2 '
                                                           'turns.',
                         cost=8)
        self.poison_damage = 10  # TODO need to scale; was 20, which is way too high for level 1
        self.poison_rounds = 2


class PoisonStrike2(Stealth):
    """
    Replaces Poison Strike
    """
    def __init__(self):
        super().__init__(name='Poison Strike', description='Attack the enemy with a chance to poison the enemy for 4 '
                                                           'turns.',
                         cost=14)
        self.poison_damage = 20
        self.poison_rounds = 4


# Drain skills
class HealthDrain(Drain):
    """

    """
    def __init__(self):
        super().__init__(name='Health Drain', description='Drain the enemy, absorbing their health.',
                         cost=10)


class ManaDrain(Drain):
    """

    """
    def __init__(self):
        super().__init__(name='Mana Drain', description='Drain the enemy, absorbing their mana.',
                         cost=0)


class HealthManaDrain(Drain):
    """
    TODO Replaces Health and Mana Drain abilities
    """
    def __init__(self):
        super().__init__(name='Health/Mana Drain', description='Drain the enemy, absorbing the health and mana in '
                                                               'return.',
                         cost=10)


class LearnSpell(Class):
    """

    """
    def __init__(self):
        super().__init__(name='Learn Spell', description='Enables a diviner to learn rank 1 enemy spells.',
                         cost=0)
        self.passive = True


class LearnSpell2(Class):
    """
    Replaces Learn Spell
    """
    def __init__(self):
        super().__init__(name='Learn Spell', description='Enables a geomancer to learn rank 1 or 2 enemy spells.',
                         cost=0)
        self.passive = True


class Transform(Class):
    """

    """
    def __init__(self):
        super().__init__(name='Transform', description='Transforms the druid into a panther.',
                         cost=0)
        self.combat = False


class Transform2(Class):
    """

    """
    def __init__(self):
        super().__init__(name='Transform', description='Transforms the druid into a direbear.',
                         cost=0)
        self.combat = False


class Transform3(Class):
    """

    """
    def __init__(self):
        super().__init__(name='Transform', description='Transforms the lycan into a werewolf.',
                         cost=0)
        self.combat = False


class Transform4(Class):
    """

    """
    def __init__(self):
        super().__init__(name='Transform', description='Transforms the lycan into a griffin.',
                         cost=0)
        self.combat = False


class Transform5(Class):
    """

    """
    def __init__(self):
        super().__init__(name='Transform', description='Transforms the lycan into a red dragon.',
                         cost=0)
        self.combat = False


class ElementalStrike(Class):
    """

    """
    def __init__(self):
        super().__init__(name="Elemental Strike", description='Attack the enemy with your weapon and a random '
                                                              'elemental spell.',
                         cost=15)


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


"""
Spell section
"""


# Spell types
class NonElemSpell(Spell):
    """

    """
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Non-Elemental'


class FireSpell(Spell):
    """

    """
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Fire'


class IceSpell(Spell):
    """

    """
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Ice'


class ElecSpell(Spell):
    """

    """
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Electrical'


class WaterSpell(Spell):
    """

    """
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Water'


class EarthSpell(Spell):
    """

    """
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Earth'


class WindSpell(Spell):
    """

    """
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Wind'


class ShadowSpell(Spell):
    """

    """
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Shadow'


class HolySpell(Spell):
    """

    """
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Holy'


class DeathSpell(Spell):
    """

    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Death'


class StatusSpell(Spell):
    """

    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Status'


class HealSpell(Spell):
    """

    """
    def __init__(self, name, description, cost, heal, crit):
        super().__init__(name, description, cost)
        self.heal = heal
        self.crit = crit
        self.subtyp = 'Heal'
        self.combat = False


class EnhanceSpell(Spell):
    """

    """
    def __init__(self, name, description, cost, mod):
        super().__init__(name, description, cost)
        self.mod = mod


class MovementSpell(Spell):
    """

    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.combat = False


# Spells
class MagicMissile(NonElemSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Magic Missile', description='An orb of energy shoots forth from the caster, dealing '
                                                           'non-elemental damage.',
                         cost=5, damage=8, crit=8)
        self.cat = 'Attack'
        self.school = 'Arcane'
        self.missiles = 1


class MagicMissile2(NonElemSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Magic Missile', description='Two orbs of energy shoot forth from the caster, dealing '
                                                           'non-elemental damage.',
                         cost=18, damage=8, crit=8)
        self.cat = 'Attack'
        self.school = 'Arcane'
        self.missiles = 2


class MagicMissile3(NonElemSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Magic Missile', description='Three orbs of energy shoot forth from the caster, dealing '
                                                           'non-elemental damage.',
                         cost=40, damage=8, crit=8)
        self.cat = 'Attack'
        self.school = 'Arcane'
        self.missiles = 3


class Ultima(NonElemSpell):
    """
    Rank 2 Enemy Spell
    """
    def __init__(self):
        super().__init__(name='Ultima', description='Envelopes the enemy in a magical void, dealing massive non-'
                                                    'elemental damage.',
                         cost=35, damage=50, crit=4)
        self.cat = 'Attack'
        self.school = 'Non-Elemental'
        self.rank = 2


class Firebolt(FireSpell):
    """
    Arcane fire spells have lower crit but hit harder on average
    """
    def __init__(self):
        super().__init__(name='Firebolt', description='A mote of fire propelled at the foe.',
                         cost=2, damage=8, crit=10)
        self.cat = 'Attack'
        self.school = 'Arcane'


class Fireball(FireSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Fireball', description='A giant ball of fire that consumes the enemy.',
                         cost=10, damage=25, crit=8)
        self.cat = 'Attack'
        self.school = 'Arcane'


class Firestorm(FireSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Firestorm', description='Fire rains from the sky, incinerating the enemy.',
                         cost=20, damage=40, crit=6)
        self.cat = 'Attack'
        self.school = 'Arcane'


class Scorch(FireSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Scorch', description='Light a fire and watch the enemy burn!',
                         cost=10, damage=14, crit=10)
        self.cat = 'Attack'
        self.school = 'Elemental'


class MoltenRock(FireSpell):
    """
    Rank 1 Enemy Spell
    """
    def __init__(self):
        super().__init__(name='Molten Rock', description='A giant, molten boulder is hurled at the enemy, dealing great'
                                                         ' fire damage.',
                         cost=16, damage=28, crit=8)
        self.cat = 'Attack'
        self.school = 'Elemental'
        self.rank = 1


class Volcano(FireSpell):
    """
    Rank 2 Enemy Spell
    """
    def __init__(self):
        super().__init__(name='Volcano', description='A mighty eruption burst out from beneath the enemy\' feet, '
                                                     'dealing massive fire damage.',
                         cost=24, damage=48, crit=6)
        self.cat = 'Attack'
        self.school = 'Elemental'
        self.rank = 2


class IceLance(IceSpell):
    """
    Arcane ice spells have lower average damage but have the highest chance to crit
    """
    def __init__(self):
        super().__init__(name='Ice Lance', description='A javelin of ice launched at the enemy.',
                         cost=4, damage=8, crit=4)
        self.cat = 'Attack'
        self.school = 'Arcane'


class Icicle(IceSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Icicle', description='Frozen shards rain from the sky.',
                         cost=9, damage=15, crit=3)
        self.cat = 'Attack'
        self.school = 'Arcane'


class IceBlizzard(IceSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Ice Blizzard', description='The enemy is encased in a blistering cold, penetrating into '
                                                          'its bones.',
                         cost=18, damage=25, crit=2)
        self.cat = 'Attack'
        self.school = 'Arcane'


class Shock(ElecSpell):
    """
    Arcane electric spells have better crit than fire and better damage than ice
    """
    def __init__(self):
        super().__init__(name='Shock', description='An electrical arc from the caster\'s hands to the enemy.',
                         cost=6, damage=12, crit=7)
        self.cat = 'Attack'
        self.school = 'Arcane'


class Lightning(ElecSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Lightning', description='Throws a bolt of lightning at the enemy.',
                         cost=15, damage=22, crit=6)
        self.cat = 'Attack'
        self.school = 'Arcane'


class Electrocution(ElecSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Electrocution', description='A million volts of electricity passes through the enemy.',
                         cost=25, damage=38, crit=5)
        self.cat = 'Attack'
        self.school = 'Arcane'


class WaterJet(WaterSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Water Jet', description='A jet of water erupts from beneath the enemy\'s feet.',
                         cost=6, damage=12, crit=5)
        self.cat = 'Attack'
        self.school = 'Elemental'


class Aqualung(WaterSpell):
    """
    Rank 1 Enemy Spell
    """
    def __init__(self):
        super().__init__(name='Aqualung', description='Giant water bubbles surround the enemy and burst, causing great '
                                                      'water damage.',
                         cost=13, damage=20, crit=4)
        self.cat = 'Attack'
        self.school = 'Elemental'
        self.rank = 1


class Tsunami(WaterSpell):
    """
    Rank 2 Enemy Spell
    """
    def __init__(self):
        super().__init__(name='Water Jet', description='A massive tidal wave cascades over your foes.',
                         cost=26, damage=32, crit=3)
        self.cat = 'Attack'
        self.school = 'Elemental'
        self.rank = 2


class Tremor(EarthSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Tremor', description='The ground shakes, causing objects to fall and damage the enemy.',
                         cost=3, damage=7, crit=7)
        self.cat = 'Attack'
        self.school = 'Elemental'


class Mudslide(EarthSpell):
    """
    Rank 1 Enemy Spell
    """
    def __init__(self):
        super().__init__(name='Mudslide', description='A torrent of mud and earth sweep over the enemy, causing earth '
                                                      'damage.',
                         cost=16, damage=27, crit=6)
        self.cat = 'Attack'
        self.school = 'Elemental'
        self.rank = 1


class Earthquake(EarthSpell):
    """
    Rank 2 Enemy Spell
    """
    def __init__(self):
        super().__init__(name='Earthquake', description='The cave wall and ceiling are brought down by a massive '
                                                        'seismic event, dealing devastating earth damage.',
                         cost=26, damage=41, crit=5)
        self.cat = 'Attack'
        self.school = 'Elemental'
        self.rank = 2


class Gust(WindSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Gust', description='A strong gust of wind whips past the enemy.',
                         cost=12, damage=15, crit=6)
        self.cat = 'Attack'
        self.school = 'Elemental'


class Hurricane(WindSpell):
    """
    Rank 1 Enemy Spell
    """
    def __init__(self):
        super().__init__(name='Hurricane', description='A violent storm berates your foes, causing great wind damage.',
                         cost=22, damage=26, crit=4)
        self.cat = 'Attack'
        self.school = 'Elemental'
        self.rank = 1


class Tornado(WindSpell):
    """
    Rank 2 Enemy Spell
    """
    def __init__(self):
        super().__init__(name='Tornado', description='You bring down a cyclone that pelts the enemy with debris and '
                                                     'causes massive wind damage.',
                         cost=40, damage=40, crit=2)
        self.cat = 'Attack'
        self.school = 'Elemental'
        self.rank = 2


class ShadowBolt(ShadowSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Shadow Bolt', description='Launch a bolt of magic infused with dark energy, damaging the'
                                                         ' enemy.',
                         cost=8, damage=15, crit=5)
        self.cat = 'Attack'
        self.school = 'Shadow'


class ShadowBolt2(ShadowSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Shadow Bolt', description='Launch a large bolt of magic infused with dark energy, '
                                                         'damaging the enemy.',
                         cost=20, damage=35, crit=4)
        self.cat = 'Attack'
        self.school = 'Shadow'


class ShadowBolt3(ShadowSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Shadow Bolt', description='Launch a massive bolt of magic infused with dark energy, '
                                                         'damaging the enemy.',
                         cost=30, damage=45, crit=3)
        self.cat = 'Attack'
        self.school = 'Shadow'


class Corruption(ShadowSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Corruption', description='Damage the enemy and add a debuff that does damage for 2 '
                                                        'turns',
                         cost=10, damage=8, crit=5)
        self.cat = 'Attack'
        self.dot_turns = 2
        self.school = 'Shadow'


class Corruption2(ShadowSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Corruption', description='Damage the enemy and add a debuff that does damage for 4 '
                                                        'turns',
                         cost=25, damage=25, crit=4)
        self.cat = 'Attack'
        self.dot_turns = 4
        self.school = 'Shadow'


class Terrify(ShadowSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Terrify', description='Get in the mind of the enemy, terrifying them into inaction for a'
                                                     ' turn and doing damage in the process.',
                         cost=15, damage=10, crit=4)
        self.cat = 'Attack'
        self.stun = 1
        self.school = 'Shadow'


class Terrify2(ShadowSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Terrify', description='Get in the mind of the enemy, terrifying them into inaction for 2'
                                                     ' turns and doing damage in the process.',
                         cost=20, damage=15, crit=3)
        self.cat = 'Attack'
        self.stun = 2
        self.school = 'Shadow'


class Terrify3(ShadowSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Terrify', description='Get in the mind of the enemy, terrifying them into inaction for 3'
                                                     ' turns and doing damage in the process.',
                         cost=25, damage=20, crit=2)
        self.cat = 'Attack'
        self.stun = 3
        self.school = 'Shadow'


class Doom(DeathSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Doom', description='Places a timer on the enemy\'s life, ending it when the timer '
                                                  'expires.',
                         cost=15)
        self.cat = 'Kill'
        self.timer = 3
        self.school = 'Death'


class Desoul(DeathSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Desoul', description='Removes the soul from the enemy, instantly killing it.',
                         cost=50)
        self.cat = 'Kill'
        self.school = 'Death'


class Petrify(DeathSpell):
    """
    Rank 2 Enemy Spell
    """
    def __init__(self):
        super().__init__(name='Petrify', description='Gaze at the enemy and turn them into stone.',
                         cost=50)
        self.cat = 'Kill'
        self.school = 'Death'
        self.rank = 2


class Smite(HolySpell):
    """

    """
    def __init__(self):
        super().__init__(name='Smite', description='The power of light rebukes the enemy.', cost=10, damage=20, crit=4)
        self.cat = 'Attack'
        self.school = 'Holy'


class Smite2(HolySpell):
    """

    """
    def __init__(self):
        super().__init__(name='Smite', description='The power of light rebukes the enemy.', cost=20, damage=35, crit=3)
        self.cat = 'Attack'
        self.school = 'Holy'


class Smite3(HolySpell):
    """

    """
    def __init__(self):
        super().__init__(name='Smite', description='The power of light rebukes the enemy.', cost=32, damage=50, crit=2)
        self.cat = 'Attack'
        self.school = 'Holy'


class Holy(HolySpell):
    """

    """
    def __init__(self):
        super().__init__(name='Holy', description='The enemy is bathed in a holy light, cleansing it of evil.',
                         cost=4, damage=10, crit=10)
        self.cat = 'Attack'
        self.school = 'Holy'


class Holy2(HolySpell):
    """

    """
    def __init__(self):
        super().__init__(name='Holy', description='The enemy is bathed in a holy light, cleansing it of evil.',
                         cost=12, damage=24, crit=8)
        self.cat = 'Attack'
        self.school = 'Holy'


class Holy3(HolySpell):
    """

    """
    def __init__(self):
        super().__init__(name='Holy', description='The enemy is bathed in a holy light, cleansing it of evil.',
                         cost=28, damage=45, crit=6)
        self.cat = 'Attack'
        self.school = 'Holy'


class Heal(HealSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Heal', description='A glowing light envelopes your body and heals you for up to 25% of '
                                                  'your health (16% chance to double).',
                         cost=12, heal=0.25, crit=5)
        self.cat = 'Heal'


class Restore(HealSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Restore', description='A glowing light envelopes your body and heals you for up to 50% '
                                                     'of your health (25% chance to double).',
                         cost=25, heal=0.50, crit=3)
        self.cat = 'Heal'


class Renew(HealSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Renew', description='A glowing light envelopes your body and heals you for up to 75% '
                                                   'of your health (33% chance to double).',
                         cost=35, heal=0.75, crit=2)
        self.cat = 'Heal'


class EnhanceBlade(EnhanceSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Enhance Blade', description='Enchant your weapon with magical energy to enhance the '
                                                           'weapon\'s damage.',
                         cost=6, mod=5)
        self.cat = 'Enhance'
        self.school = 'Arcane'


class EnhanceBlade2(EnhanceSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Enhance Blade', description='Enchant your weapon with magical energy to enhance the '
                                                           'weapon\'s damage.',
                         cost=10, mod=10)
        self.cat = 'Enhance'
        self.school = 'Arcane'


class EnhanceBlade3(EnhanceSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Enhance Blade', description='Enchant your weapon with magical energy to enhance the '
                                                           'weapon\'s damage.',
                         cost=18, mod=20)
        self.cat = 'Enhance'
        self.school = 'Arcane'


class Sanctuary(MovementSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Sanctuary', description='Return to town from anywhere in the dungeon.',
                         cost=100)
        self.cat = 'Movement'


class Teleport(MovementSpell):
    """

    """
    def __init__(self):
        super().__init__(name='Teleport', description='Teleport to another location on the current level.',
                         cost=50)
        self.cat = 'Movement'


class BlindingFog(StatusSpell):
    """
    Rank 1 Enemy Spell
    """
    def __init__(self):
        super().__init__(name="Blinding Fog", description="The enemy is surrounding in a thick fog, lowering the chance"
                                                          " to hit on a melee attack.",
                         cost=7)
        self.cat = 'Status'
        self.school = 'Shadow'
        self.blind = 2
        self.rank = 1


class PoisonBreath(StatusSpell):
    """
    Rank 2 Enemy Spell
    """
    def __init__(self):
        super().__init__(name="Poison Breath", description="Your spew forth a toxic breath, dealing poison damage and "
                                                           "poisoning the target for 4 turns.",
                         cost=20)
        self.cat = 'Attack'
        self.school = 'Poison'
        self.damage = 15
        self.crit = 5
        self.poison_rounds = 4
        self.rank = 2


class DiseaseBreath(StatusSpell):
    """
    Enemy Spell; not learnable by player
    """
    def __init__(self):
        super().__init__(name="Disease Breath", description="A diseased cloud emanates onto the enemy, with a chance to"
                                                            " lower the enemy's constitution permanently.",
                         cost=25)
        self.cat = 'Status'
        self.school = 'Disease'


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
              'Warlock': {'5': HealthDrain,
                          '15': ManaDrain},
              'Necromancer': {'10': HealthManaDrain},
              'Spellblade': {'15': Parry},
              'Knight Enchanter': {'10': DoubleStrike},
              'Footpad': {'3': Disarm,
                          '5': SmokeScreen,
                          '6': Blind,
                          '8': Backstab,
                          '10': Steal,
                          '12': KidneyPunch,
                          '16': DoubleStrike,
                          '20': Parry},
              'Thief': {'5': Lockpick,
                        '8': TripleStrike,
                        '12': KidneyPunch2,
                        '14': Disarm2,
                        '15': Mug},
              'Rogue': {'10': KidneyPunch3,
                        '15': Disarm3,
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
                          '16': Restore},
              'Crusader': {'3': Smite2,
                           '8': Renew,
                           '18': Smite3},
              'Lancer': {},
              'Dragoon': {},
              'Mage': {'2': Firebolt,
                       '6': MagicMissile,
                       '8': IceLance,
                       '13': Shock},
              'Sorcerer': {'2': Icicle,
                           '8': Lightning,
                           '15': Fireball,
                           '18': MagicMissile2},
              'Wizard': {'4': Firestorm,
                         '10': IceBlizzard,
                         '15': Electrocution,
                         '20': Teleport,
                         '25': MagicMissile3},
              'Warlock': {'1': ShadowBolt,
                          '4': Corruption,
                          '10': Terrify,
                          '12': ShadowBolt2,
                          '15': Doom},
              'Necromancer': {'2': Terrify2,
                              '6': Corruption2,
                              '8': ShadowBolt3,
                              '16': Terrify3,
                              '18': Desoul},
              'Spellblade': {'2': EnhanceBlade,
                             '14': EnhanceBlade2},
              'Knight Enchanter': {'3': Fireball,
                                   '8': EnhanceBlade3,
                                   '9': Icicle,
                                   '12': Lightning},
              'Footpad': {},
              'Thief': {},
              'Rogue': {},
              'Inquisitor': {},
              'Seeker': {'1': Teleport,
                         '10': Sanctuary},
              'Assassin': {},
              'Ninja': {'20': Desoul},
              'Healer': {'4': Heal,
                         '10': Holy,
                         '18': Restore},
              'Cleric': {'2': Smite,
                         '16': Smite2},
              'Templar': {'10': Smite3},
              'Priest': {'3': Holy2,
                         '8': Renew},
              'Archbishop': {'4': Holy3},
              'Monk': {},
              'Master Monk': {},
              'Pathfinder': {'5': Tremor,
                             '11': WaterJet,
                             '14': Gust,
                             '19': Scorch},
              'Druid': {},
              'Lycan': {},
              'Diviner': {},
              'Geomancer': {},
              'Shaman': {},
              'Soulcatcher': {'12': Desoul},
              }
