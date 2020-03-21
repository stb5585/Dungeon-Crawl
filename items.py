###########################################
""" item manager """


class Item:
    """
    value: price in gold; sale price will be half this amount
    rarity: higher number means more rare
    """

    def __init__(self, name, description, value, rarity):
        self.name = name
        self.description = description
        self.value = value
        self.rarity = rarity

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\n".format(self.name, self.description, self.value)


class Weapon(Item):

    def __init__(self, name, description, value, rarity, damage):
        self.damage = damage
        self.typ = "Weapon"
        super().__init__(name, description, value, rarity)

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nDamage: {}".format(self.name, self.description, self.value, self.damage)


class Unarmed(Weapon):

    def __init__(self):
        super().__init__(name="BARE HANDS", description="Nothing but your fists.", value=0, rarity=0, damage=0)


class Sword(Weapon):

    def __init__(self):
        super().__init__(name="SWORD", description="A weapon with a long metal blade and a hilt with a hand "
                                                   "guard, used for thrusting or striking and now typically worn "
                                                   "as part of ceremonial dress.", value=1000, rarity=10, damage=5)


class Armor(Item):

    def __init__(self, name, description, value, rarity, armor):
        self.armor = armor
        self.typ = 'Armor'
        super().__init__(name, description, value, rarity)

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nArmor: {}".format(self.name, self.description, self.value, self.armor)


class Naked(Armor):

    def __init__(self):
        super().__init__(name="NO ARMOR", description="No armor equipped.", value=0, rarity=0, armor=0)


class Breastplate(Armor):

    def __init__(self):
        super().__init__(name="BREASTPLATE", description="A device worn over the torso to protect it from injury.",
                         value=1000, rarity=10, armor=5)


class Potion(Item):

    def __init__(self, name, description, value, rarity, percent):
        super().__init__(name, description, value, rarity)
        self.percent = percent


class HealthPotion(Potion):

    def __init__(self):
        super().__init__(name="HEALTH POTION", description="A potion that restores 25% of your health", value=100,
                         rarity=10, percent=0.25)
        self.typ = "Potion"
