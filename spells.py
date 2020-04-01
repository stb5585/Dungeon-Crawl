###########################################
""" spell manager """


class Spell:
    """
    cost: amount of mana required to cast spell
    crit: chance to double damage; higher number means lower chance to crit
    level attained: the level when you attain the spell
    class(es): the class(es) that can cast the spells
    """

    def __init__(self, name, description, level, cost):
        self.name = name
        self.description = description
        self.level = level
        self.cost = cost

    def __str__(self):
        return "{}\n=====\n{}\nLevel: {}\nMana cost: {}\n".format(self.name, self.description, self.level, self.cost)


class FireSpell(Spell):

    def __init__(self, name, description, level, cost, damage, crit):
        super().__init__(name, description, level, cost)
        self.damage = damage
        self.crit = crit
        self.typ = 'Fire'


class IceSpell(Spell):

    def __init__(self, name, description, level, cost, damage, crit):
        super().__init__(name, description, level, cost)
        self.damage = damage
        self.crit = crit
        self.typ = 'Ice'


class ElecSpell(Spell):

    def __init__(self, name, description, level, cost, damage, crit):
        super().__init__(name, description, level, cost)
        self.damage = damage
        self.crit = crit
        self.typ = 'Electrical'


class Firebolt(FireSpell):

    def __init__(self):
        super().__init__(name='Firebolt', description='A mote of fire propelled at the foe.', level=3, cost=2, damage=8,
                         crit=10)


class Fireball(FireSpell):

    def __init__(self):
        super().__init__(name='Fireball', description='A giant ball of fire that consumes the enemy.', level=12,
                         cost=10, damage=30, crit=10)


class IceLance(IceSpell):

    def __init__(self):
        super().__init__(name='Ice Lance', description='A javelin of ice launched at the enemy.', level=5, cost=4,
                         damage=8, crit=5)


class Icicle(IceSpell):

    def __init__(self):
        super().__init__(name='Icicle', description='Frozen shards rain from the sky.', level=10, cost=10, damage=15,
                         crit=3)


class Shock(ElecSpell):

    def __init__(self):
        super().__init__(name='Shock', description='Electrocute the enemy with a strong voltage.', level=7, cost=6,
                         damage=12, crit=7)


class Lightning(ElecSpell):

    def __init__(self):
        super().__init__(name='Shock', description='Throws a bolt of lightning at the enemy.', level=15, cost=15,
                         damage=35, crit=5)


# Parameters
spell_dict = {str(Firebolt().level): Firebolt, str(Fireball().level): Fireball, str(IceLance().level): IceLance,
              str(Icicle().level): Icicle, str(Shock().level): Shock, str(Lightning().level): Lightning}
