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

    def __str__(self):
        return "{}\n=====\n{}\nMana cost: {}\n".format(self.name, self.description, self.cost)


class Spell(Ability):

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.typ = 'Spell'


class Skill(Ability):

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.typ = 'Skill'


"""
Spell section
"""


# Skill types
class Offensive(Skill):

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)


class Stealth(Skill):

    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)


# Skills
class DoubleStrike(Offensive):

    def __init__(self):
        super().__init__(name='Multi-Strike', description='Perform a double attack with the primary weapon.',
                         cost=10)
        self.strikes = 2


class TripleStrike(Offensive):
    """
    Should overwrite DoubleStrike (same name)
    """

    def __init__(self):
        super().__init__(name='Multi-Strike', description='Perform a triple attack with the primary weapon.',
                         cost=20)
        self.strikes = 3


class QuadStrike(Offensive):
    """
    Should overwrite TripleStrike (same name)
    """

    def __init__(self):
        super().__init__(name='Multi-Strike', description='Perform a quadruple attack with the primary weapon.',
                         cost=40)
        self.strikes = 4


class FlurryBlades(Offensive):
    """
    Should overwrite QuadStab (same name)
    """

    def __init__(self):
        super().__init__(name='Multi-Strike', description='Slices the enemy in a flurry.',
                         cost=50)
        self.strikes = 5


class Jump(Offensive):

    def __init__(self):
        super().__init__(name='Jump', description='Leap into the air and bring down your weapon onto the enemy, '
                                                  'delivering critical damage.',
                         cost=10)
        self.strikes = 1


class DoubleJump(Offensive):

    def __init__(self):
        super().__init__(name='Jump', description='Leap into the air and bring down your weapon onto the enemy, '
                                                  'delivering critical damage twice.',
                         cost=25)
        self.strikes = 2


class TripleJump(Offensive):

    def __init__(self):
        super().__init__(name='Jump', description='Leap into the air and bring down your weapon onto the enemy, '
                                                  'delivering critical damage thrice.',
                         cost=40)
        self.strikes = 3


# Stealth skills
class Backstab(Stealth):

    def __init__(self):
        super().__init__(name='Backstab', description='Strike the opponent in the back, guaranteeing a hit and ignoring'
                                                      ' any resistance or armor.',
                         cost=6)


class SmokeScreen(Stealth):

    def __init__(self):
        super().__init__(name='Smoke Screen', description='Obscure the player in a puff of smoke, allowing the '
                                                          'player to flee without fail.',
                         cost=5)
        self.escape = True


"""
Spell section
"""


# Spell types
class FireSpell(Spell):

    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Fire'


class IceSpell(Spell):

    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Ice'


class ElecSpell(Spell):

    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Electrical'


class HealSpell(Spell):

    def __init__(self, name, description, cost, heal, crit):
        super().__init__(name, description, cost)
        self.heal = heal
        self.crit = crit
        self.subtyp = 'Holy'


class EnhanceSpell(Spell):

    def __init__(self, name, description, cost, mod):
        super().__init__(name, description, cost)
        self.mod = mod


# Spells
class Firebolt(FireSpell):

    def __init__(self):
        super().__init__(name='Firebolt', description='A mote of fire propelled at the foe.',
                         cost=2, damage=6, crit=10)
        self.cat = 'Attack'


class Fireball(FireSpell):

    def __init__(self):
        super().__init__(name='Fireball', description='A giant ball of fire that consumes the enemy.',
                         cost=10, damage=20, crit=8)
        self.cat = 'Attack'


class Firestorm(FireSpell):

    def __init__(self):
        super().__init__(name='Firestorm', description='Fire rains from the sky, incinerating the enemy.',
                         cost=20, damage=40, crit=6)
        self.cat = 'Attack'


class IceLance(IceSpell):

    def __init__(self):
        super().__init__(name='Ice Lance', description='A javelin of ice launched at the enemy.',
                         cost=4, damage=8, crit=4)
        self.cat = 'Attack'


class Icicle(IceSpell):

    def __init__(self):
        super().__init__(name='Icicle', description='Frozen shards rain from the sky.',
                         cost=9, damage=15, crit=3)
        self.cat = 'Attack'


class IceBlizzard(IceSpell):

    def __init__(self):
        super().__init__(name='Ice Blizzard', description='The enemy is encased in a blistering cold, penetrating into '
                                                          'its bones.',
                         cost=18, damage=25, crit=2)
        self.cat = 'Attack'


class Shock(ElecSpell):

    def __init__(self):
        super().__init__(name='Shock', description='An electrical arc from the caster\'s hands to the enemy.',
                         cost=6, damage=12, crit=7)
        self.cat = 'Attack'


class Lightning(ElecSpell):

    def __init__(self):
        super().__init__(name='Lightning', description='Throws a bolt of lightning at the enemy.',
                         cost=15, damage=28, crit=6)
        self.cat = 'Attack'


class Electrocution(ElecSpell):

    def __init__(self):
        super().__init__(name='Electrocution', description='A million volts of electricity passes through the enemy',
                         cost=25, damage=50, crit=5)
        self.cat = 'Attack'


class Heal(HealSpell):

    def __init__(self):
        super().__init__(name='Heal', description='A glowing light envelopes your body and heals you for up to 25% of '
                                                  'your health (16% chance to double).',
                         cost=12, heal=0.25, crit=5)
        self.cat = 'Heal'


class Restore(HealSpell):

    def __init__(self):
        super().__init__(name='Restore', description='A glowing light envelopes your body and heals you for up to 50% '
                                                     'of your health (25% chance to double).',
                         cost=25, heal=0.50, crit=3)
        self.cat = 'Heal'


class Renew(HealSpell):

    def __init__(self):
        super().__init__(name='Renew', description='A glowing light envelopes your body and heals you for up to 75% '
                                                   'of your health (33% chance to double).',
                         cost=25, heal=0.50, crit=2)
        self.cat = 'Heal'


class EnhanceBlade(EnhanceSpell):

    def __init__(self):
        super().__init__(name='Enhance Blade', description='Enchant your weapon with magical energy to enhance the '
                                                           'weapon\'s damage.',
                         cost=8, mod=5)
        self.cat = 'Enhance'


class EnhanceBlade2(EnhanceSpell):

    def __init__(self):
        super().__init__(name='Enhance Blade', description='Enchant your weapon with magical energy to enhance the '
                                                           'weapon\'s damage.',
                         cost=14, mod=10)
        self.cat = 'Enhance'


class EnhanceBlade3(EnhanceSpell):

    def __init__(self):
        super().__init__(name='Enhance Blade', description='Enchant your weapon with magical energy to enhance the '
                                                           'weapon\'s damage.',
                         cost=26, mod=20)
        self.cat = 'Enhance'


# Parameters
spell_dict = {'WARRIOR': {},
              'WEAPON MASTER': {},
              'BERSERKER': {},
              'PALADIN': {'2': Heal,
                          '16': Restore},
              'CRUSADER': {'8': Renew},
              'LANCER': {},
              'DRAGOON': {},
              'MAGE': {'3': Firebolt,
                       '8': IceLance,
                       '13': Shock},
              'SORCERER': {'2': Icicle,
                           '8': Lightning,
                           '15': Fireball},
              'WIZARD': {'4': Firestorm,
                         '10': IceBlizzard,
                         '15': Electrocution},
              'WARLOCK': {},
              'NECROMANCER': {},
              'SPELLBLADE': {'2': EnhanceBlade,
                             '14': EnhanceBlade2},
              'KNIGHT ENCHANTER': {'4': EnhanceBlade3},
              'FOOTPAD': {},
              'THIEF': {},
              'ROGUE': {},
              'RANGER': {},
              'SEEKER': {},
              'ASSASSIN': {},
              'NINJA': {}
              }

skill_dict = {'WARRIOR': {'10': DoubleStrike},
              'WEAPON MASTER': {'10': TripleStrike},
              'BERSERKER': {'10': QuadStrike},
              'PALADIN': {},
              'CRUSADER': {},
              'LANCER': {'5': Jump,
                         '15': DoubleJump},
              'DRAGOON': {'20': TripleJump},
              'MAGE': {},
              'SORCERER': {},
              'WIZARD': {},
              'WARLOCK': {},
              'NECROMANCER': {},
              'SPELLBLADE': {},
              'KNIGHT ENCHANTER': {'10': DoubleStrike},
              'FOOTPAD': {'5': SmokeScreen,
                          '8': Backstab,
                          '15': DoubleStrike},
              'THIEF': {},
              'ROGUE': {'10': TripleStrike},
              'RANGER': {},
              'SEEKER': {},
              'ASSASSIN': {'5': TripleStrike,
                           '20': QuadStrike},
              'NINJA': {'25': FlurryBlades}
              }
