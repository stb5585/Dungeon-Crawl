###########################################
""" spell manager """


class Ability:
    """
    cost: amount of mana required to cast spell
    crit: chance to double damage; higher number means lower chance to crit
    level attained: the level when you attain the spell
    """

    def __init__(self, name, description, level, cost):
        self.name = name
        self.description = description
        self.level = level
        self.cost = cost

    def __str__(self):
        return "{}\n=====\n{}\nLevel: {}\nMana cost: {}\n".format(self.name, self.description, self.level, self.cost)


class Spell(Ability):

    def __init__(self, name, description, level, cost):
        super().__init__(name, description, level, cost)
        self.typ = 'Spell'


class Skill(Ability):

    def __init__(self, name, description, level, cost):
        super().__init__(name, description, level, cost)
        self.typ = 'Skill'


# Warrior skills
class Offensive(Skill):

    def __init__(self, name, description, level, cost, damage, crit):
        super().__init__(name, description, level, cost)
        self.damage = damage
        self.crit = crit


class DoubleStrike(Offensive):

    def __init__(self):
        super().__init__(name='Double Strike', description='Perform a double attack with the primary weapon.',
                         level=5, cost=6, damage=1, crit=1)


# Mage spells
class FireSpell(Spell):

    def __init__(self, name, description, level, cost, damage, crit):
        super().__init__(name, description, level, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Fire'


class IceSpell(Spell):

    def __init__(self, name, description, level, cost, damage, crit):
        super().__init__(name, description, level, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Ice'


class ElecSpell(Spell):

    def __init__(self, name, description, level, cost, damage, crit):
        super().__init__(name, description, level, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Electrical'


class Firebolt(FireSpell):

    def __init__(self):
        super().__init__(name='Firebolt', description='A mote of fire propelled at the foe.',
                         level=3, cost=2, damage=6, crit=10)


class Fireball(FireSpell):

    def __init__(self):
        super().__init__(name='Fireball', description='A giant ball of fire that consumes the enemy.',
                         level=12, cost=10, damage=20, crit=8)


class Firestorm(FireSpell):

    def __init__(self):
        super().__init__(name='Firestorm', description='Fire rains from the sky, incinerating the enemy.',
                         level=19, cost=20, damage=40, crit=6)


class IceLance(IceSpell):

    def __init__(self):
        super().__init__(name='Ice Lance', description='A javelin of ice launched at the enemy.',
                         level=5, cost=4, damage=8, crit=4)


class Icicle(IceSpell):

    def __init__(self):
        super().__init__(name='Icicle', description='Frozen shards rain from the sky.',
                         level=10, cost=9, damage=15, crit=3)


class IceBlizzard(IceSpell):

    def __init__(self):
        super().__init__(name='Ice Blizzard', description='The enemy is encased in a blistering cold, penetrating into '
                                                          'its bones.',
                         level=18, cost=18, damage=25, crit=2)


class Shock(ElecSpell):

    def __init__(self):
        super().__init__(name='Shock', description='An electrical arc from the caster\'s hands to the enemy.',
                         level=7, cost=6, damage=12, crit=7)


class Lightning(ElecSpell):

    def __init__(self):
        super().__init__(name='Lightning', description='Throws a bolt of lightning at the enemy.',
                         level=15, cost=15, damage=28, crit=6)


class Electrocution(ElecSpell):

    def __init__(self):
        super().__init__(name='Electrocution', description='A million volts of electricity passes through the enemy',
                         level=20, cost=25, damage=50, crit=5)


# Footpad skills
class Stealth(Skill):

    def __init__(self, name, description, level, cost, damage, crit):
        super().__init__(name, description, level, cost)
        self.damage = damage
        self.crit = crit


class Backstab(Stealth):

    def __init__(self):
        super().__init__(name='Backstab', description='Strike the opponent in the back, guaranteeing a hit and ignoring'
                                                      ' any resistance or armor.',
                         level=5, cost=6, damage=1, crit=1)


# Parameters
spell_dict = {'WARRIOR': {str(DoubleStrike().level): DoubleStrike},
              'WEAPON MASTER': {},
              'BERSERKER': {},
              'PALADIN': {},
              'CRUSADER': {},
              'LANCER': {},
              'DRAGOON': {},
              'MAGE': {str(Firebolt().level): Firebolt,
                       str(Fireball().level): Fireball,
                       str(IceLance().level): IceLance,
                       str(Icicle().level): Icicle,
                       str(Shock().level): Shock,
                       str(Lightning().level): Lightning,
                       str(Firestorm().level): Firestorm,
                       str(IceBlizzard().level): IceBlizzard,
                       str(Electrocution().level): Electrocution},
              'SORCERER': {},
              'WIZARD': {},
              'WARLOCK': {},
              'NECROMANCER': {},
              'FOOTPAD': {str(Backstab().level): Backstab},
              'THIEF': {},
              'ROGUE': {},
              'RANGER': {},
              'SEEKER': {},
              'ASSASSIN': {},
              'NINJA': {}
              }
