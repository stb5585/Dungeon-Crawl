###########################################
""" item manager """

# Imports
import random


# Functions
def reciprocal(x: int) -> float:
    return 1.0 / x


def equip_compare(old, new: object):
    pass


def random_item(z: int) -> object:
    item_dict = {'Weapon': {'Dagger': [[BronzeDagger, IronDagger, SteelDagger, AdamantiteDagger, Carnwennan],
                                       [reciprocal(BronzeDagger().rarity), reciprocal(IronDagger().rarity),
                                        reciprocal(SteelDagger().rarity), reciprocal(AdamantiteDagger().rarity),
                                        reciprocal(Carnwennan().rarity)],
                                       ['1', '2', '3', '4', '5']],
                            'Sword': [[BronzeSword, IronSword, SteelSword, AdamantiteSword, Excalibur],
                                      [reciprocal(BronzeSword().rarity), reciprocal(IronSword().rarity),
                                       reciprocal(SteelSword().rarity), reciprocal(AdamantiteSword().rarity),
                                       reciprocal(Excalibur().rarity)],
                                      ['1', '2', '3', '4', '5']],
                            'Axe': [[BattleAxe, GreatAxe, AdamantiteAxe, Jarnbjorn],
                                    [reciprocal(BattleAxe().rarity), reciprocal(GreatAxe().rarity),
                                     reciprocal(AdamantiteAxe().rarity), reciprocal(Jarnbjorn().rarity)],
                                    ['1', '3', '4', '5']],
                            'Polearm': [[Spear, Lance, Pike, Halberd, Gungnir],
                                        [reciprocal(Spear().rarity), reciprocal(Lance().rarity),
                                         reciprocal(Pike().rarity), reciprocal(Halberd().rarity),
                                         reciprocal(Gungnir().rarity)],
                                        ['1', '2', '4', '5']],
                            'Staff': [[PineStaff, OakStaff, IronshodStaff, SerpentStaff, PrincessGuard],
                                      [reciprocal(PineStaff().rarity), reciprocal(OakStaff().rarity),
                                       reciprocal(IronshodStaff().rarity), reciprocal(SerpentStaff().rarity),
                                       reciprocal(PrincessGuard().rarity)],
                                      ['1', '2', '3', '4', '5']],
                            'Hammer': [[Hammer, OakHammer, IronHammer, EarthHammer, Mjolnir],
                                       [reciprocal(Hammer().rarity), reciprocal(OakHammer().rarity),
                                        reciprocal(IronHammer().rarity), reciprocal(EarthHammer().rarity),
                                        reciprocal(Mjolnir().rarity)],
                                       ['1', '2', '3', '4', '5']]
                            },
                 'OffHand': {'Shield': [[Buckler, WoodShield, BronzeShield, IronShield, TowerShield, MedusaShield],
                                        [reciprocal(Buckler().rarity), reciprocal(WoodShield().rarity),
                                         reciprocal(BronzeShield().rarity), reciprocal(IronShield().rarity),
                                         reciprocal(TowerShield().rarity), reciprocal(MedusaShield().rarity)],
                                        ['1', '1', '2', '3', '4', '5']],
                             'Grimoire': [[Book, TomeKnowledge, Necronomicon, Magus],
                                          [reciprocal(Book().rarity), reciprocal(TomeKnowledge().rarity),
                                           reciprocal(Necronomicon().rarity), reciprocal(Magus().rarity)],
                                          ['1', '3', '4', '5']]},
                 'Armor': {'Cloth': [[Tunic, ClothCloak, SilverCloak, GoldCloak, CloakEnchantment, WizardRobe,
                                      MerlinRobe],
                                     [reciprocal(Tunic().rarity), reciprocal(ClothCloak().rarity),
                                      reciprocal(SilverCloak().rarity), reciprocal(GoldCloak().rarity),
                                      reciprocal(CloakEnchantment().rarity), reciprocal(WizardRobe().rarity),
                                      reciprocal(MerlinRobe().rarity)],
                                     ['1', '1', '2', '3', '4', '4', '5']],
                           'Light': [[PaddedArmor, LeatherArmor, Cuirboulli, Studded, DragonHide],
                                     [reciprocal(PaddedArmor().rarity), reciprocal(LeatherArmor().rarity),
                                      reciprocal(Cuirboulli().rarity), reciprocal(Studded().rarity),
                                      reciprocal(DragonHide().rarity)],
                                     ['1', '2', '3', '4', '5']],
                           'Medium': [[HideArmor, ChainShirt, ScaleMail, Breastplate, HalfPlate, Aegis],
                                      [reciprocal(HideArmor().rarity), reciprocal(ChainShirt().rarity),
                                       reciprocal(ScaleMail().rarity), reciprocal(Breastplate().rarity),
                                       reciprocal(HalfPlate().rarity), reciprocal(Aegis().rarity)],
                                      ['1', '2', '3', '3', '4', '5']],
                           'Heavy': [[RingMail, ChainMail, Splint, PlateArmor, Genji],
                                     [reciprocal(RingMail().rarity), reciprocal(ChainMail().rarity),
                                      reciprocal(Splint().rarity), reciprocal(PlateArmor().rarity),
                                      reciprocal(Genji().rarity)],
                                     ['1', '2', '3', '4', '5']]},
                 'Potion': {'Health': [[HealthPotion, SuperHealthPotion, MasterHealthPotion],
                                       [reciprocal(HealthPotion().rarity), reciprocal(SuperHealthPotion().rarity),
                                        reciprocal(MasterHealthPotion().rarity)],
                                       ['1', '2', '3']],
                            'Mana': [[ManaPotion, SuperManaPotion, MasterManaPotion],
                                     [reciprocal(ManaPotion().rarity), reciprocal(SuperManaPotion().rarity),
                                      reciprocal(MasterManaPotion().rarity)],
                                     ['1', '2', '3']],
                            'Elixir': [[Elixir, Megalixir],
                                       [reciprocal(Elixir().rarity), reciprocal(Megalixir().rarity)],
                                       ['3', '4']],
                            'Stat': [[StrengthPotion, IntelPotion, WisdomPotion, ConPotion, CharismaPotion,
                                      DexterityPotion],
                                     [reciprocal(StrengthPotion().rarity), reciprocal(IntelPotion().rarity),
                                      reciprocal(WisdomPotion().rarity), reciprocal(ConPotion().rarity),
                                      reciprocal(CharismaPotion().rarity), reciprocal(DexterityPotion().rarity)],
                                     ['1', '1', '1', '1', '1', '1']]
                            }
                 }

    while True:
        rand_group = random.choice(list(item_dict))
        rand_type = random.choice(list(item_dict[rand_group]))
        treasure = random.choices(item_dict[rand_group][rand_type][0], item_dict[rand_group][rand_type][1])[0]
        item_index = item_dict[rand_group][rand_type][0].index(treasure)
        if int(item_dict[rand_group][rand_type][2][item_index]) <= z:
            rand_item = treasure
            break
    return rand_item


def remove(typ: str):
    typ_dict = dict(Weapon=NoWeapon, OffHand=NoOffHand, Armor=NoArmor)
    return typ_dict[typ]


class Item:
    """
    value: price in gold; sale price will be half this amount
    rarity: higher number means more rare
    crit: chance to double damage; higher number means lower chance to crit
    handed: identifies weapon as 1-handed or 2-handed; 2-handed weapons prohibit the ability to use a shield
    block: higher number means lower chance to block; if block is successful, damage mitigation will be decided randomly
    """

    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\n".format(self.name, self.description, self.value)


class Weapon(Item):

    def __init__(self, name, description, value, rarity, damage, crit, handed, subtyp, unequip, off):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.damage = damage
        self.crit = crit
        self.handed = handed
        self.subtyp = subtyp
        self.unequip = unequip
        self.off = off
        self.typ = "Weapon"

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nDamage: {}\nCritical Chance: {}\n{}-handed".format(self.name,
                                                                                             self.description,
                                                                                             self.value, self.damage,
                                                                                             self.crit, self.handed)


class NoWeapon(Weapon):

    def __init__(self):
        super().__init__(name="BARE HANDS", description="Nothing but your fists.",
                         value=0, rarity=0, damage=0, crit=10, handed=1, subtyp='None', unequip=True, off=True)


class BronzeDagger(Weapon):

    def __init__(self):
        super().__init__(name="BRONZE DAGGER", description="A bronze knife with a very sharp point and usually two "
                                                           "sharp edges, typically designed or capable of being used as"
                                                           " a thrusting or stabbing weapon.",
                         value=125, rarity=3, damage=1, crit=4, handed=1, subtyp='Dagger', unequip=False, off=True)


class IronDagger(Weapon):

    def __init__(self):
        super().__init__(name="IRON DAGGER", description="An iron knife with a very sharp point and usually two "
                                                         "sharp edges, typically designed or capable of being used as"
                                                         " a thrusting or stabbing weapon.",
                         value=800, rarity=7, damage=3, crit=3, handed=1, subtyp='Dagger', unequip=False, off=True)


class SteelDagger(Weapon):

    def __init__(self):
        super().__init__(name="STEEL DAGGER", description="A steel knife with a very sharp point and usually two "
                                                          "sharp edges, typically designed or capable of being used as"
                                                          " a thrusting or stabbing weapon.",
                         value=2000, rarity=15, damage=5, crit=2, handed=1, subtyp='Dagger', unequip=False, off=True)


class AdamantiteDagger(Weapon):

    def __init__(self):
        super().__init__(name="ADAMANTITE DAGGER", description="An adamantite knife with a very sharp point and usually"
                                                               " two sharp edges, typically designed or capable of "
                                                               "being used as a thrusting or stabbing weapon.",
                         value=3500, rarity=25, damage=8, crit=2, handed=1, subtyp='Dagger', unequip=False, off=True)


class Carnwennan(Weapon):

    def __init__(self):
        super().__init__(name="Carnwennan", description="King Arthur's dagger, sometimes described to shroud the user "
                                                        "in shadow.",
                         value=10000, rarity=50, damage=12, crit=1, handed=1, subtyp='Dagger', unequip=False, off=True)


class BronzeSword(Weapon):

    def __init__(self):
        super().__init__(name="BRONZE SWORD", description="A weapon with a long bronze blade and a hilt with a hand "
                                                          "guard, used for thrusting or striking and now typically "
                                                          "worn as part of ceremonial dress.",
                         value=125, rarity=3, damage=2, crit=8, handed=1, subtyp='Sword', unequip=False, off=True)


class IronSword(Weapon):

    def __init__(self):
        super().__init__(name="IRON SWORD", description="A weapon with a long iron blade and a hilt with a hand "
                                                        "guard, used for thrusting or striking and now typically worn "
                                                        "as part of ceremonial dress.",
                         value=1000, rarity=8, damage=5, crit=5, handed=1, subtyp='Sword', unequip=False, off=True)


class SteelSword(Weapon):

    def __init__(self):
        super().__init__(name="STEEL SWORD", description="A weapon with a long steel blade and a hilt with a hand "
                                                         "guard, used for thrusting or striking and now typically worn "
                                                         "as part of ceremonial dress.",
                         value=2000, rarity=15, damage=7, crit=4, handed=1, subtyp='Sword', unequip=False, off=True)


class AdamantiteSword(Weapon):

    def __init__(self):
        super().__init__(name="ADAMANTITE SWORD", description="A weapon with a long adamantite blade and a hilt with "
                                                              "a hand guard, used for thrusting or striking and now "
                                                              "typically worn as part of ceremonial dress.",
                         value=4000, rarity=25, damage=10, crit=3, handed=1, subtyp='Sword', unequip=False, off=True)


class Excalibur(Weapon):

    def __init__(self):
        super().__init__(name="EXCALIBUR", description="The legendary sword of King Arthur, bestowed upon him by the "
                                                       "Lady of the Lake.",
                         value=15000, rarity=50, damage=15, crit=2, handed=1, subtyp='Sword', unequip=False, off=True)


class BattleAxe(Weapon):

    def __init__(self):
        super().__init__(name="BATTLE AXE", description="An axe specifically designed for combat.",
                         value=500, rarity=6, damage=6, crit=8, handed=2, subtyp='Axe', unequip=False, off=False)


class GreatAxe(Weapon):

    def __init__(self):
        super().__init__(name="GREAT AXE", description="A double-bladed, two-handed melee weapon.",
                         value=1500, rarity=12, damage=10, crit=5, handed=2, subtyp='Axe', unequip=False, off=False)


class AdamantiteAxe(Weapon):

    def __init__(self):
        super().__init__(name="ADAMANTITE AXE", description="A double-bladed, two-handed melee weapon made from "
                                                            "adamantite.",
                         value=4000, rarity=30, damage=14, crit=4, handed=2, subtyp='Axe', unequip=False, off=False)


class Jarnbjorn(Weapon):

    def __init__(self):
        super().__init__(name="JARNBJORN", description="Legendary axe of Thor Odinson. Old Norse for \"iron bear\".",
                         value=12000, rarity=50, damage=20, crit=3, handed=2, subtyp='Axe', unequip=False, off=False)


class Spear(Weapon):

    def __init__(self):
        super().__init__(name="SPEAR", description="A pole weapon consisting of a shaft, usually of wood, with a "
                                                   "pointed head.",
                         value=600, rarity=6, damage=5, crit=6, handed=2, subtyp='Polearm', unequip=False, off=False)


class Lance(Weapon):

    def __init__(self):
        super().__init__(name="LANCE", description="A pole weapon designed for thrusting.",
                         value=1500, rarity=12, damage=9, crit=5, handed=2, subtyp='Polearm', unequip=False, off=False)


class Pike(Weapon):

    def __init__(self):
        super().__init__(name="PIKE", description="A pole weapon designed for thrusting.",
                         value=3500, rarity=25, damage=11, crit=4, handed=2, subtyp='Polearm', unequip=False, off=False)


class Halberd(Weapon):

    def __init__(self):
        super().__init__(name="HALBERD", description="A combined spear and battle axe.",
                         value=4500, rarity=30, damage=13, crit=4, handed=2, subtyp='Polearm', unequip=False, off=False)


class Gungnir(Weapon):

    def __init__(self):
        super().__init__(name="GUNGNIR", description="Legendary spear of the god Odin. Old Norse for \"swaying one\".",
                         value=12000, rarity=50, damage=15, crit=3, handed=2, subtyp='Polearm', unequip=False, off=False)


class PineStaff(Weapon):

    def __init__(self):
        super().__init__(name="PINE STAFF", description="A pine walking stick wielded in 2 hands and used to strike the"
                                                        "opponent, typically used by magic users.",
                         value=250, rarity=4, damage=2, crit=12, handed=2, subtyp='Staff', unequip=False, off=False)


class OakStaff(Weapon):

    def __init__(self):
        super().__init__(name="OAK STAFF", description="An oak walking stick wielded in 2 hands and used to strike the"
                                                       "opponent, typically used by magic users.",
                         value=400, rarity=6, damage=3, crit=10, handed=2, subtyp='Staff', unequip=False, off=False)


class IronshodStaff(Weapon):

    def __init__(self):
        super().__init__(name="IRONSHOD STAFF", description="An iron walking stick, making it ideal for striking.",
                         value=1000, rarity=8, damage=6, crit=8, handed=2, subtyp='Staff', unequip=False, off=False)


class SerpentStaff(Weapon):

    def __init__(self):
        super().__init__(name="SERPENT STAFF", description="A magic staff, shaped to appear as a snake.",
                         value=2000, rarity=15, damage=12, crit=6, handed=2, subtyp='Staff', unequip=False, off=False)


class PrincessGuard(Weapon):

    def __init__(self):
        super().__init__(name="PRINCESS GUARD", description="A mythical staff from another world.",
                         value=10000, rarity=50, damage=20, crit=6, handed=2, subtyp='Staff', unequip=False, off=False)


class Hammer(Weapon):

    def __init__(self):
        super().__init__(name="HAMMER", description="",
                         value=250, rarity=4, damage=3, crit=12, handed=2, subtyp='Hammer', unequip=False, off=False)


class OakHammer(Weapon):

    def __init__(self):
        super().__init__(name="OAK HAMMER", description="",
                         value=400, rarity=6, damage=5, crit=10, handed=2, subtyp='Hammer', unequip=False, off=False)


class IronHammer(Weapon):

    def __init__(self):
        super().__init__(name="IRON HAMMER", description="",
                         value=1000, rarity=8, damage=8, crit=8, handed=2, subtyp='Hammer', unequip=False, off=False)


class EarthHammer(Weapon):

    def __init__(self):
        super().__init__(name="EARTH HAMMER", description="A magic staff, shaped to appear as a snake.",
                         value=2000, rarity=15, damage=14, crit=6, handed=2, subtyp='Hammer', unequip=False, off=False)


class Mjolnir(Weapon):

    def __init__(self):
        super().__init__(name="Mjolnir", description="The hammer of Thor, the Norse god of thunder",
                         value=20000, rarity=50, damage=24, crit=5, handed=2, subtyp='Hammer', unequip=False, off=False)


class Armor(Item):

    def __init__(self, name, description, value, rarity, armor, subtyp, unequip, **kwargs):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.armor = armor
        self.subtyp = subtyp
        self.unequip = unequip
        self.typ = 'Armor'

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nArmor: {}".format(self.name, self.description, self.value, self.armor)


class NoArmor(Armor):

    def __init__(self):
        super().__init__(name="NO ARMOR", description="No armor equipped.", value=0, rarity=0, armor=0, subtyp='None',
                         unequip=True)


class Tunic(Armor):

    def __init__(self):
        super().__init__(name="TUNIC", description="A close-fitting short coat as part of a uniform, especially a "
                                                   "police or military uniform.",
                         value=60, rarity=2, armor=1, subtyp='Cloth', unequip=False)


class ClothCloak(Armor):

    def __init__(self):
        super().__init__(name="CLOTH CLOAK", description="An outdoor cloth garment, typically sleeveless, that hangs"
                                                         "loosely from the shoulders.",
                         value=125, rarity=4, armor=2, subtyp='Cloth', unequip=False)


class SilverCloak(Armor):

    def __init__(self):
        super().__init__(name="SILVER CLOAK", description="A cloak weaved with strands of silver to improve protective"
                                                          "power.",
                         value=500, rarity=8, armor=4, subtyp='Cloth', unequip=False)


class GoldCloak(Armor):

    def __init__(self):
        super().__init__(name="GOLD CLOAK", description="A cloak weaved with strands of gold to improve protective"
                                                        "power.",
                         value=1500, rarity=12, armor=6, subtyp='Cloth', unequip=False)


class CloakEnchantment(Armor):

    def __init__(self):
        super().__init__(name="CLOAK of ENCHANTMENT", description="A magical cloak that shields the wearer from all "
                                                                  "forms of attack.",
                         value=2500, rarity=18, armor=8, subtyp='Cloth', unequip=False)


class WizardRobe(Armor):

    def __init__(self):
        super().__init__(name="WIZARD'S ROBE", description="A knee-length, long-sleeved robe with an impressive hood "
                                                           "designed to add a mysterious feel to magic users.",
                         value=5000, rarity=25, armor=10, subtyp='Cloth', unequip=False)


class MerlinRobe(Armor):

    def __init__(self):
        super().__init__(name="ROBES of MERLIN", description="The enchanted robes of Merlin the enchanter.",
                         value=14000, rarity=50, armor=12, subtyp='Cloth', unequip=False)


class PaddedArmor(Armor):

    def __init__(self):
        super().__init__(name="PADDED ARMOR", description="Consists of quilted layers of cloth and batting to provide"
                                                          " some protection from attack.",
                         value=75, rarity=2, armor=2, subtyp='Light', unequip=False)


class LeatherArmor(Armor):

    def __init__(self):
        super().__init__(name="LEATHER ARMOR", description="A protective covering made of animal hide, boiled to make "
                                                           "it tough and rigid and worn over the torso to protect it "
                                                           "from injury.",
                         value=350, rarity=5, armor=3, subtyp='Light', unequip=False)


class Cuirboulli(Armor):

    def __init__(self):
        super().__init__(name="CUIRBOULLI", description="French for \"boiled leather\", this armor has increased "
                                                        "rigidity for add protection",
                         value=700, rarity=7, armor=4, subtyp='Light', unequip=False)


class Studded(Armor):

    def __init__(self):
        super().__init__(name="STUDDED LEATHER", description="Leather armor embedded with iron studs to improve "
                                                             "defensive capabilities.",
                         value=1500, rarity=10, armor=6, subtyp='Light', unequip=False)


class DragonHide(Armor):

    def __init__(self):
        super().__init__(name="DRAGON HIDE", description="Hide armor made from the scales of a red dragon, "
                                                         "inconceivably light for this type of armor.",
                         value=15000, rarity=50, armor=15, subtyp='Light', unequip=False)


class HideArmor(Armor):

    def __init__(self):
        super().__init__(name="HIDE ARMOR", description="A crude armor made from thick furs and pelts.",
                         value=100, rarity=2, armor=3, subtyp='Medium', unequip=False)


class ChainShirt(Armor):

    def __init__(self):
        super().__init__(name="CHAIN SHIRT", description="A type of armor consisting of small metal rings linked "
                                                         "together in a pattern to form a mesh.",
                         value=400, rarity=6, armor=4, subtyp='Medium', unequip=False)


class ScaleMail(Armor):

    def __init__(self):
        super().__init__(name="SCALE MAIL", description="Armor consisting of a coat and leggings of leather covered"
                                                        " with overlapping pieces of metal, mimicking the scales of a "
                                                        "fish.",
                         value=900, rarity=9, armor=5, subtyp='Medium', unequip=False)


class Breastplate(Armor):

    def __init__(self):
        super().__init__(name="BREASTPLATE", description="Armor consisting of a fitted metal chest piece worn with "
                                                         "supple leather. Although it leaves the legs and arms "
                                                         "relatively unprotected, this armor provides good protection "
                                                         "for the wearer’s vital organs while leaving the wearer "
                                                         "relatively unencumbered.",
                         value=1800, rarity=12, armor=6, subtyp='Medium', unequip=False)


class HalfPlate(Armor):

    def __init__(self):
        super().__init__(name="HALF PLATE", description="Armor consisting of shaped metal plates that cover most of the"
                                                        " wearer’s body. It does not include leg Protection beyond "
                                                        "simple greaves that are attached with leather straps.",
                         value=3000, rarity=15, armor=8, subtyp='Medium', unequip=False)


class Aegis(Armor):

    def __init__(self):
        super().__init__(name="AEGIS BREASTPLATE", description="The breastplate of Zeus, emboldened with a bolt of "
                                                               "lightning.",
                         value=25000, rarity=75, armor=18, subtyp='Medium', unequip=False)


class RingMail(Armor):

    def __init__(self):
        super().__init__(name="RING MAIL", description="Leather armor with heavy rings sewn into it. The rings help "
                                                       "reinforce the armor against blows from Swords and axes.",
                         value=200, rarity=3, armor=4, subtyp='Heavy', unequip=False)


class ChainMail(Armor):

    def __init__(self):
        super().__init__(name="CHAIN MAIL", description="Made of interlocking metal rings, includes a layer of quilted "
                                                        "fabric worn underneath the mail to prevent chafing and to "
                                                        "cushion the impact of blows. The suit includes gauntlets.",
                         value=600, rarity=7, armor=5, subtyp='Heavy', unequip=False)


class Splint(Armor):

    def __init__(self):
        super().__init__(name="SPLINT MAIL", description="Armor made of narrow vertical strips of metal riveted to a "
                                                         "backing of leather that is worn over cloth padding. Flexible "
                                                         "chain mail protects the joints.",
                         value=1200, rarity=10, armor=6, subtyp='Heavy', unequip=False)


class PlateArmor(Armor):

    def __init__(self):
        super().__init__(name="PLATE ARMOR", description="Armor consisting of shaped, interlocking metal plates to "
                                                         "cover the entire body. A suit of plate includes gauntlets, "
                                                         "heavy leather boots, a visored helmet, and thick layers of "
                                                         "padding underneath the armor. Buckles and straps distribute "
                                                         "the weight over the body.",
                         value=5000, rarity=20, armor=10, subtyp='Heavy', unequip=False)


class Genji(Armor):

    def __init__(self):
        super().__init__(name="GENJI ARMOR", description="Mythical armor crafted by an unknown master blacksmith and "
                                                         "embued with protective enchantments that allow the user to "
                                                         "shrug off damage.",
                         value=50000, rarity=100, armor=25, subtyp='Heavy', unequip=False)


class OffHand(Item):
    """
    mod stat depends on the off-hand item; mod for shields is block and spell damage modifier for grimoires
    """

    def __init__(self, name, description, value, rarity, mod, subtyp, unequip, **kwargs):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.mod = mod
        self.subtyp = subtyp
        self.unequip = unequip
        self.typ = 'OffHand'

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nBlock: {}".format(self.name, self.description, self.value, self.mod)


class NoOffHand(OffHand):

    def __init__(self):
        super().__init__(name="NO OFFHAND", description="No off-hand equipped.", value=0, rarity=0, mod=0,
                         subtyp='None', unequip=True)


class Buckler(OffHand):

    def __init__(self):
        super().__init__(name="BUCKLER", description="A small round shield held by a handle or worn on the forearm.",
                         value=25, rarity=2, mod=10, subtyp='Shield', unequip=False)


class WoodShield(OffHand):

    def __init__(self):
        super().__init__(name="WOOD SHIELD", description="A broad piece of wood, held by straps used as a protection "
                                                         "against blows or missiles.",
                         value=100, rarity=4, mod=8, subtyp='Shield', unequip=False)


class BronzeShield(OffHand):

    def __init__(self):
        super().__init__(name="BRONZE SHIELD", description="A broad piece of bronze, held by a handle attached on one "
                                                           "side, used as a protection against blows or missiles.",
                         value=250, rarity=6, mod=6, subtyp='Shield', unequip=False)


class IronShield(OffHand):

    def __init__(self):
        super().__init__(name="IRON SHIELD", description="A broad piece of iron, held by a handle attached on one "
                                                         "side, used as a protection against blows or missiles.",
                         value=500, rarity=10, mod=4, subtyp='Shield', unequip=False)


class TowerShield(OffHand):

    def __init__(self):
        super().__init__(name="TOWER SHIELD", description="A defensive bulwark, an impenetrable wall.",
                         value=5000, rarity=30, mod=2, subtyp='Shield', unequip=False)


class MedusaShield(OffHand):

    def __init__(self):
        super().__init__(name="MEDUSA SHIELD", description="A shield that has been polished to resemble a mirror. Said"
                                                           " to be used to defeat the Gorgon Medusa. Reflects back some"
                                                           " magic.",
                         value=25000, rarity=75, mod=2, subtyp='Shield', unequip=False)


class Book(OffHand):

    def __init__(self):
        super().__init__(name="BOOK", description="A random book.", value=25, rarity=2, mod=2, subtyp='Grimoire',
                         unequip=False)


class TomeKnowledge(OffHand):

    def __init__(self):
        super().__init__(name="TOME of KNOWLEDGE", description="A tome containing secrets to enhancing spells.",
                         value=300, rarity=5, mod=5, subtyp='Grimoire', unequip=False)


class Necronomicon(OffHand):

    def __init__(self):
        super().__init__(name="NECRONOMICON", description="The book of the dead.",
                         value=5000, rarity=35, mod=10, subtyp='Grimoire', unequip=False)


class Magus(OffHand):

    def __init__(self):
        super().__init__(name="MAGUS", description="A book of magical art written by a powerful wizard.",
                         value=15000, rarity=75, mod=20, subtyp='Grimoire', unequip=False)


class Potion(Item):

    def __init__(self, name, description, value, rarity, subtyp, **kwargs):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.subtyp = subtyp
        self.typ = "Potion"


class HealthPotion(Potion):

    def __init__(self):
        super().__init__(name="HEALTH POTION", description="A potion that restores 25% of your health.",
                         value=100, rarity=5, subtyp='Health')
        self.percent = 0.25


class SuperHealthPotion(Potion):

    def __init__(self):
        super().__init__(name="SUPER HEALTH POTION", description="A potion that restores 50% of your health.",
                         value=600, rarity=10, subtyp='Health')
        self.percent = 0.50


class MasterHealthPotion(Potion):

    def __init__(self):
        super().__init__(name="MASTER HEALTH POTION", description="A potion that restores 100% of your health.",
                         value=1000, rarity=25, subtyp='Health')
        self.percent = 1.0


class ManaPotion(Potion):

    def __init__(self):
        super().__init__(name="MANA POTION", description="A potion that restores 25% of your mana.",
                         value=250, rarity=10, subtyp='Mana')
        self.percent = 0.25


class SuperManaPotion(Potion):

    def __init__(self):
        super().__init__(name="SUPER MANA POTION", description="A potion that restores 50% of your mana.",
                         value=1500, rarity=20, subtyp='Mana')
        self.percent = 0.50


class MasterManaPotion(Potion):

    def __init__(self):
        super().__init__(name="MASTER MANA POTION", description="A potion that restores 100% of your mana.",
                         value=2500, rarity=30, subtyp='Mana')
        self.percent = 1.0


class Elixir(Potion):

    def __init__(self):
        super().__init__(name="ELIXIR", description="A potion that restores up to 75% of your health and mana.",
                         value=4000, rarity=40, subtyp='Elixir')
        self.percent = 0.75


class Megalixir(Potion):

    def __init__(self):
        super().__init__(name="MEGALIXIR", description="A potion that restores up to 100% of your health and mana.",
                         value=5000, rarity=50, subtyp='Elixir')
        self.percent = 1.0


class StrengthPotion(Potion):

    def __init__(self):
        super().__init__(name="STRENGTH POTION", description="A potion that permanently increases your strength by 1",
                         value=20000, rarity=50, subtyp='Stat')
        self.stat = 'str'


class IntelPotion(Potion):

    def __init__(self):
        super().__init__(name="INTELLIGENCE POTION", description="A potion that permanently increases your intelligence"
                                                                 " by 1",
                         value=20000, rarity=50, subtyp='Stat')
        self.stat = 'int'


class WisdomPotion(Potion):

    def __init__(self):
        super().__init__(name="WISDOM POTION", description="A potion that permanently increases your wisdom by 1",
                         value=20000, rarity=50, subtyp='Stat')
        self.stat = 'wis'


class ConPotion(Potion):

    def __init__(self):
        super().__init__(name="CONSTITUTION POTION", description="A potion that permanently increases your constitution"
                                                                 " by 1",
                         value=20000, rarity=50, subtyp='Stat')
        self.stat = 'con'


class CharismaPotion(Potion):

    def __init__(self):
        super().__init__(name="CHARISMA POTION", description="A potion that permanently increases your strength by 1",
                         value=20000, rarity=50, subtyp='Stat')
        self.stat = 'cha'


class DexterityPotion(Potion):

    def __init__(self):
        super().__init__(name="DEXTERITY POTION", description="A potion that permanently increases your dexterity by 1",
                         value=20000, rarity=50, subtyp='Stat')
        self.stat = 'dex'


# Parameters
items_dict = {'Weapon': {'Dagger': [[BronzeDagger, IronDagger, SteelDagger, AdamantiteDagger, Carnwennan],
                                    [reciprocal(BronzeDagger().rarity), reciprocal(IronDagger().rarity),
                                     reciprocal(SteelDagger().rarity), reciprocal(AdamantiteDagger().rarity),
                                     reciprocal(Carnwennan().rarity)]],
                         'Sword': [[BronzeSword, IronSword, SteelSword, AdamantiteSword, Excalibur],
                                   [reciprocal(BronzeSword().rarity), reciprocal(IronSword().rarity),
                                    reciprocal(SteelSword().rarity), reciprocal(AdamantiteSword().rarity),
                                    reciprocal(Excalibur().rarity)]],
                         'Axe': [[BattleAxe, GreatAxe, AdamantiteAxe, Jarnbjorn],
                                 [reciprocal(BattleAxe().rarity), reciprocal(GreatAxe().rarity),
                                  reciprocal(AdamantiteAxe().rarity), reciprocal(Jarnbjorn().rarity)]],
                         'Polearm': [[Spear, Lance, Halberd, Gungnir],
                                     [reciprocal(Spear().rarity), reciprocal(Lance().rarity),
                                      reciprocal(Halberd().rarity), reciprocal(Gungnir().rarity)]],
                         'Staff': [[PineStaff, OakStaff, IronshodStaff, SerpentStaff, PrincessGuard],
                                   [reciprocal(PineStaff().rarity), reciprocal(OakStaff().rarity),
                                    reciprocal(IronshodStaff().rarity), reciprocal(SerpentStaff().rarity),
                                    reciprocal(PrincessGuard().rarity)]]},
              'OffHand': {'Shield': [[Buckler, WoodShield, BronzeShield, IronShield, TowerShield, MedusaShield],
                                     [reciprocal(Buckler().rarity), reciprocal(WoodShield().rarity),
                                      reciprocal(BronzeShield().rarity), reciprocal(IronShield().rarity),
                                      reciprocal(TowerShield().rarity), reciprocal(MedusaShield().rarity)]],
                          'Grimoire': [[Book, TomeKnowledge, Necronomicon, Magus],
                                       [reciprocal(Book().rarity), reciprocal(TomeKnowledge().rarity),
                                        reciprocal(Necronomicon().rarity), reciprocal(Magus().rarity)]]},
              'Armor': {'Cloth': [[Tunic, ClothCloak, SilverCloak, WizardRobe, CloakEnchantment, MerlinRobe],
                                  [reciprocal(Tunic().rarity), reciprocal(ClothCloak().rarity),
                                   reciprocal(SilverCloak().rarity), reciprocal(WizardRobe().rarity),
                                   reciprocal(CloakEnchantment().rarity), reciprocal(MerlinRobe().rarity)]],
                        'Light': [[PaddedArmor, LeatherArmor, Cuirboulli, Studded, DragonHide],
                                  [reciprocal(PaddedArmor().rarity), reciprocal(LeatherArmor().rarity),
                                   reciprocal(Cuirboulli().rarity), reciprocal(Studded().rarity),
                                   reciprocal(DragonHide().rarity)]],
                        'Medium': [[HideArmor, ChainShirt, ScaleMail, Breastplate, HalfPlate, Aegis],
                                   [reciprocal(HideArmor().rarity), reciprocal(ChainShirt().rarity),
                                    reciprocal(ScaleMail().rarity), reciprocal(Breastplate().rarity),
                                    reciprocal(HalfPlate().rarity), reciprocal(Aegis().rarity)]],
                        'Heavy': [[RingMail, ChainMail, Splint, PlateArmor, Genji],
                                  [reciprocal(RingMail().rarity), reciprocal(ChainMail().rarity),
                                   reciprocal(Splint().rarity), reciprocal(PlateArmor().rarity),
                                   reciprocal(Genji().rarity)]]},
              'Potion': {'Health': [[HealthPotion, SuperHealthPotion, MasterHealthPotion],
                                    [reciprocal(HealthPotion().rarity), reciprocal(SuperHealthPotion().rarity),
                                     reciprocal(MasterHealthPotion().rarity)]],
                         'Mana': [[ManaPotion, SuperManaPotion, MasterManaPotion],
                                  [reciprocal(ManaPotion().rarity), reciprocal(SuperManaPotion().rarity),
                                   reciprocal(MasterManaPotion().rarity)]],
                         'Elixir': [[Elixir, Megalixir],
                                    [reciprocal(Elixir().rarity), reciprocal(Megalixir().rarity)]],
                         'Stat': [[StrengthPotion, IntelPotion, WisdomPotion, ConPotion, CharismaPotion,
                                   DexterityPotion],
                                  [reciprocal(StrengthPotion().rarity), reciprocal(IntelPotion().rarity),
                                   reciprocal(WisdomPotion().rarity), reciprocal(ConPotion().rarity),
                                   reciprocal(CharismaPotion().rarity), reciprocal(DexterityPotion().rarity)]]
                         }
              }
